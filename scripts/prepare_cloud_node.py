#!/usr/bin/env python3
"""Prepare the saved cloud environment's official Linux x64 Node baseline.

This owns only its explicit prefix; it never changes the platform runtime or
authenticates. The fixed SHA256 was verified against the official SHASUMS256.txt.
Lody's separate installer continues to resolve npm latest with engine-strict.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import posixpath
import re
import shutil
import stat
import subprocess
import tarfile
import tempfile
import urllib.parse
import urllib.request


VERSION = "v24.22.1"
NPM_VERSION = "11.19.1"
ARCHIVE_ROOT = f"node-{VERSION}-linux-x64"
ARCHIVE_URL = f"https://nodejs.org/dist/{VERSION}/{ARCHIVE_ROOT}.tar.xz"
CHECKSUMS_URL = f"https://nodejs.org/dist/{VERSION}/SHASUMS256.txt"
ARCHIVE_SHA256 = "6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6"
DEFAULT_PREFIX = Path("/workspace/.tools/lody4dot-node")
MARKER = {"schema_version": 1, "owner": "lody4dot-node"}
MAX_ARCHIVE_BYTES = 150 * 1024 * 1024
MAX_EXTRACTED_BYTES = 1024 * 1024 * 1024


class NodeSetupError(Exception):
    """A bounded, non-secret error category suitable for cloud setup output."""


def _real_directory(path):
    if path.is_symlink() or not path.is_dir():
        raise NodeSetupError("unsafe_directory")


def _regular_file(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.geteuid():
        raise NodeSetupError("unsafe_file")


def _json_file(path):
    _regular_file(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise NodeSetupError("invalid_receipt")
    return value


def _atomic_bytes(path, content):
    descriptor, temporary = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def _receipt_matches(receipt, prefix, version, *, pinned=False):
    root = prefix / "versions" / version
    expected_url = f"https://nodejs.org/dist/{version}/node-{version}-linux-x64.tar.xz"
    valid = (isinstance(receipt, dict)
             and receipt.get("version") == version
             and receipt.get("prefix") == str(prefix)
             and receipt.get("node") == str(root / "bin/node")
             and receipt.get("npm") == str(root / "bin/npm")
             and receipt.get("archive_url") == expected_url
             and receipt.get("checksum_verified") is True
             and isinstance(receipt.get("sha256"), str)
             and re.fullmatch(r"[0-9a-f]{64}", receipt["sha256"]) is not None)
    return valid and (not pinned or receipt["sha256"] == ARCHIVE_SHA256)


def _layout(prefix):
    # Check ancestors before mkdir or file reads, including broken symlinks.
    for ancestor in [*reversed(prefix.parents), prefix]:
        if ancestor.is_symlink():
            raise NodeSetupError("symlink_prefix")
        if ancestor.exists():
            _real_directory(ancestor)
    if not prefix.exists():
        prefix.mkdir(parents=True, mode=0o700)
        with (prefix / ".managed.json").open("x", encoding="utf-8") as stream:
            json.dump(MARKER, stream)
    if _json_file(prefix / ".managed.json") != MARKER:
        raise NodeSetupError("unmanaged_prefix")
    if prefix.stat().st_uid != os.geteuid():
        raise NodeSetupError("unmanaged_prefix")
    if any(item.name not in {".managed.json", "receipt.json", "versions", "current", ".install.lock"}
           for item in prefix.iterdir()):
        raise NodeSetupError("unknown_prefix_entry")
    versions = prefix / "versions"
    if not versions.exists() and not versions.is_symlink():
        versions.mkdir(mode=0o700)
    _real_directory(versions)
    receipt_path = prefix / "receipt.json"
    receipt = _json_file(receipt_path) if receipt_path.exists() or receipt_path.is_symlink() else None
    current = prefix / "current"
    if current.exists() or current.is_symlink():
        if not current.is_symlink():
            raise NodeSetupError("unsafe_current")
        target = os.readlink(current)
        if not re.fullmatch(r"versions/v[0-9]+\.[0-9]+\.[0-9]+", target):
            raise NodeSetupError("unsafe_current")
        _real_directory(prefix / target)
        if not _receipt_matches(receipt, prefix, Path(target).name):
            raise NodeSetupError("invalid_current_receipt")
    if (prefix / ".current-next").exists() or (prefix / ".current-next").is_symlink():
        raise NodeSetupError("unknown_activation_entry")
    return receipt


class _OfficialRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        url = urllib.parse.urlsplit(new_url)
        if url.scheme != "https" or url.netloc != "nodejs.org":
            raise NodeSetupError("unofficial_download_redirect")
        return super().redirect_request(request, fp, code, message, headers, new_url)


def _download(destination):
    opener = urllib.request.build_opener(_OfficialRedirects())
    with opener.open(ARCHIVE_URL, timeout=60) as response, destination.open("xb") as stream:
        count = 0
        while chunk := response.read(1024 * 1024):
            count += len(chunk)
            if count > MAX_ARCHIVE_BYTES:
                raise NodeSetupError("archive_too_large")
            stream.write(chunk)


def _extract(archive_path, stage):
    # Extract regular files first, then links. No write can traverse an archive
    # symlink, including on Python 3.10 where tarfile.data_filter is unavailable.
    with tarfile.open(archive_path, "r:xz") as archive:
        members = {}
        total = 0
        for member in archive:
            path = PurePosixPath(member.name)
            if (path.is_absolute() or ".." in path.parts or "\\" in member.name
                    or not path.parts or path.parts[0] != ARCHIVE_ROOT
                    or path in members or len(members) >= 100000
                    or not (member.isdir() or member.isfile() or member.issym() or member.islnk())):
                raise NodeSetupError("unsafe_archive_member")
            total += member.size
            if total > MAX_EXTRACTED_BYTES:
                raise NodeSetupError("archive_too_large")
            members[path] = member
        links = {path for path, member in members.items() if member.issym() or member.islnk()}
        hardlink_targets = {}
        for path, member in members.items():
            if any(parent in links for parent in path.parents):
                raise NodeSetupError("archive_link_parent")
            if member.issym() or member.islnk():
                target = member.linkname
                if not target or target.startswith("/") or "\\" in target:
                    raise NodeSetupError("unsafe_archive_link")
                target_path = PurePosixPath(posixpath.normpath(
                    str(path.parent / target) if member.issym() else target))
                if not target_path.parts or target_path.parts[0] != ARCHIVE_ROOT:
                    raise NodeSetupError("unsafe_archive_link")
                if member.islnk() and (target_path not in members or not members[target_path].isfile()):
                    raise NodeSetupError("unsafe_archive_hardlink")
                if member.islnk():
                    hardlink_targets[path] = target_path
            target = stage.joinpath(*path.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source, target.open("xb") as destination:
                    shutil.copyfileobj(source, destination)
                target.chmod(member.mode & 0o777)
        root = stage / ARCHIVE_ROOT
        for path in links:
            member = members[path]
            target = stage.joinpath(*path.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            if member.issym():
                target.symlink_to(member.linkname)
            else:
                os.link(stage.joinpath(*hardlink_targets[path].parts), target)
        for path in links:
            if not stage.joinpath(*path.parts).resolve(strict=True).is_relative_to(root):
                raise NodeSetupError("unsafe_archive_link")
        return root


def _probe(root):
    node, npm = root / "bin/node", root / "bin/npm"
    _real_directory(root)
    _real_directory(root / "bin")
    _regular_file(node)
    npm_script = npm.resolve(strict=True)
    if not npm_script.is_relative_to(root) or not npm_script.is_file():
        raise NodeSetupError("unsafe_npm_path")
    environment = {"PATH": str(root / "bin"), "LC_ALL": "C"}
    versions = []
    with tempfile.TemporaryDirectory(prefix="lody4dot-node-probe-") as temporary:
        # npm must not load an existing user's credentials or project config,
        # write to their cache, or check the network during a version probe.
        user_config = Path(temporary) / "user.npmrc"
        global_config = Path(temporary) / "global.npmrc"
        user_config.write_text("", encoding="utf-8")
        global_config.write_text("", encoding="utf-8")
        npm_arguments = [str(node), str(npm_script), "--version", "--offline",
                         f"--userconfig={user_config}", f"--globalconfig={global_config}",
                         f"--cache={temporary}/cache", "--logs-max=0", "--update-notifier=false"]
        for arguments in ([str(node), "--version"], npm_arguments):
            result = subprocess.run(arguments, capture_output=True, text=True, timeout=30,
                                    env=environment, cwd=temporary)
            versions.append(result.stdout.strip())
            if result.returncode:
                raise NodeSetupError("version_probe_failed")
    if versions != [VERSION, NPM_VERSION]:
        raise NodeSetupError("unexpected_runtime_version")
    return versions


def _activate(prefix, receipt_bytes):
    current, receipt_path = prefix / "current", prefix / "receipt.json"
    backup = receipt_path.read_bytes() if receipt_path.exists() else None
    temporary = prefix / ".current-next"
    temporary.symlink_to(Path("versions") / VERSION)
    try:
        _atomic_bytes(receipt_path, receipt_bytes)
        os.replace(temporary, current)
    except BaseException:
        try:
            if backup is None:
                receipt_path.unlink(missing_ok=True)
            else:
                _atomic_bytes(receipt_path, backup)
        finally:
            temporary.unlink(missing_ok=True)
        raise


def prepare_node(prefix=DEFAULT_PREFIX):
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "amd64"}:
        raise NodeSetupError("unsupported_platform_linux_x64_required")
    import fcntl

    prefix = Path(prefix).absolute()
    if ".." in prefix.parts or prefix == Path("/"):
        raise NodeSetupError("unsafe_prefix")
    created_version = False
    activated = False
    final = prefix / "versions" / VERSION
    try:
        _layout(prefix)
        descriptor = os.open(prefix / ".install.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, "rb") as lock:
            _regular_file(prefix / ".install.lock")
            fcntl.flock(lock, fcntl.LOCK_EX)
            receipt = _layout(prefix)
            reused = final.exists() or final.is_symlink()
            if reused:
                _real_directory(final)
                if not _receipt_matches(receipt, prefix, VERSION, pinned=True):
                    raise NodeSetupError("unowned_version_directory")
                node_version, npm_version = _probe(final)
            else:
                with tempfile.TemporaryDirectory(prefix=".staging-", dir=prefix / "versions") as temporary:
                    stage = Path(temporary)
                    archive = stage / "node.tar.xz"
                    _download(archive)
                    if hashlib.sha256(archive.read_bytes()).hexdigest() != ARCHIVE_SHA256:
                        raise NodeSetupError("archive_checksum_mismatch")
                    candidate = _extract(archive, stage)
                    node_version, npm_version = _probe(candidate)
                    candidate.rename(final)
                    created_version = True
                receipt = {
                    **MARKER, "observed_at": datetime.now(timezone.utc).isoformat(),
                    "version": VERSION, "prefix": str(prefix), "node": str(final / "bin/node"),
                    "npm": str(final / "bin/npm"), "node_version": node_version,
                    "npm_version": npm_version, "archive_url": ARCHIVE_URL,
                    "sha256": ARCHIVE_SHA256, "checksum_verified": True,
                    "source_checksums": CHECKSUMS_URL, "platform_runtime_modified": False,
                    "identity_or_security_settings_changed": False,
                }
            expected_current = str(Path("versions") / VERSION)
            if not reused or not (prefix / "current").is_symlink() or os.readlink(prefix / "current") != expected_current:
                _activate(prefix, (json.dumps(receipt, indent=2) + "\n").encode())
            activated = True
            return {"status": "pass", "version": VERSION, "prefix": str(prefix),
                    "node": str(final / "bin/node"), "npm": str(final / "bin/npm"),
                    "node_version": node_version, "npm_version": npm_version, "reused": reused,
                    "sha256": ARCHIVE_SHA256, "archive_url": ARCHIVE_URL,
                    "authentication": "not_run", "platform_runtime_modified": False}
    except NodeSetupError:
        raise
    except Exception as error:
        raise NodeSetupError("node_preparation_failed") from error
    finally:
        if created_version and not activated:
            try:
                shutil.rmtree(final)
            except OSError as error:
                raise NodeSetupError("failed_version_cleanup_incomplete") from error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=Path, default=DEFAULT_PREFIX)
    parser.add_argument("--json", action="store_true", help="emit machine-readable setup evidence")
    arguments = parser.parse_args(argv)
    try:
        report = prepare_node(arguments.prefix)
    except NodeSetupError as error:
        report = {"status": "fail", "error_category": str(error), "authentication": "not_run"}
    if arguments.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(f"Node preparation: {report['status']} ({report.get('node_version', report.get('error_category'))})")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
