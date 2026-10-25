#!/usr/bin/env python3
"""Resolve and install Lody latest transactionally, without login or daemon effects."""

import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

import platform_support
from common import parse_cli_version, version_warnings


MARKER = ".lody4dot-managed.json"
OWNER = {"schema_version": 1, "owner": "lody4dot"}
RUNTIME_DIR = Path(__file__).resolve().parent.parent / "runtime"
NATIVE_MODULES = ["better-sqlite3", "@lydell/node-pty", "@napi-rs/keyring",
                  "loro-crdt", "@loro-dev/roost-node"]
PRIVATE_ENVIRONMENT_KEYS = ("LODY_CLI_TOKEN", "NPM_TOKEN", "NODE_AUTH_TOKEN", "GITEE_ACCESS_TOKEN")
LEGACY_LAUNCHER = '''#!/usr/bin/env python3
# Managed by lody4dot installer
import os
from pathlib import Path
import sys

runtime = Path(__file__).resolve().parent.parent / "current"
os.execvp("node", ["node", str(runtime / "node_modules/lody/dist/index.js"), *sys.argv[1:]])
'''
LAUNCHER = '''#!/usr/bin/env python3
# Managed by lody4dot installer
import json
import os
from pathlib import Path
import sys

runtime = Path(__file__).resolve().parent.parent / "current"
receipt = json.loads((runtime / "receipt.json").read_text(encoding="utf-8"))
if "node_path" not in receipt:
    # Receipts written before Node pinning retain their original launch behavior.
    os.execvp("node", ["node", str(runtime / "node_modules/lody/dist/index.js"), *sys.argv[1:]])
node = receipt["node_path"]
if not isinstance(node, str) or not Path(node).is_absolute():
    raise SystemExit("Managed Node path is invalid")
os.execv(node, [node, str(runtime / "node_modules/lody/dist/index.js"), *sys.argv[1:]])
'''
NATIVE_CHECK = '''import { createRequire } from 'node:module';
const require = createRequire(process.cwd() + '/package.json');
const Database = require('better-sqlite3');
const db = new Database(':memory:');
if (db.prepare('SELECT 1 AS value').get().value !== 1) throw Error('sqlite check');
db.close();
require('@lydell/node-pty');
require('@napi-rs/keyring');
require('loro-crdt');
await import('@loro-dev/roost-node');
console.log('native-ok');
'''


class InstallError(Exception):
    """A deliberately non-sensitive error suitable for JSON output."""

    def __init__(self, message, exit_code=3, category="prerequisite", raw_exit_code=None):
        super().__init__(message)
        self.exit_code = exit_code
        self.category = category
        self.raw_exit_code = raw_exit_code


def supported_node(version):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", version.strip())
    if not match:
        return False
    major, minor, patch = map(int, match.groups())
    return (major == 22 and (minor, patch) >= (14, 0)) or (major, minor, patch) >= (23, 6, 0)


def _run(args, *, cwd=None, env=None, timeout=180):
    try:
        result = subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                                text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        raise InstallError("Subprocess timed out", 4, "timeout") from None
    except OSError:
        raise InstallError("Could not start required subprocess", 3, "prerequisite") from None
    if result.returncode:
        raise InstallError("Required subprocess failed; output withheld", 4,
                           "subprocess", result.returncode)
    return result


def _read_json(path):
    if path.is_symlink() or not path.is_file():
        raise InstallError("Required managed file is missing or is a symlink")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        raise InstallError("Required JSON file is unreadable or invalid") from None
    if not isinstance(value, dict):
        raise InstallError("Required JSON file must contain an object")
    return value


def _inputs(runtime_dir):
    if runtime_dir.is_symlink() or not runtime_dir.is_dir():
        raise InstallError("Runtime input directory is unavailable")
    manifest = _read_json(runtime_dir / "package.json")
    lock = _read_json(runtime_dir / "package-lock.json")
    policy = _read_json(runtime_dir / "build-policy.json")
    if manifest.get("dependencies", {}).get("lody") != "latest":
        raise InstallError("Lody dependency must use latest", 5, "unsupported")
    packages = lock.get("packages")
    version = packages.get("node_modules/lody", {}).get("version") if isinstance(packages, dict) else None
    if (lock.get("lockfileVersion") != 3 or not isinstance(packages, dict)
            or packages.get("", {}).get("dependencies") != manifest.get("dependencies")
            or not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version)):
        raise InstallError("Manifest and lockfile do not agree", 5, "unsupported")
    if (policy.get("schema_version") != 1 or policy.get("lifecycle_scripts") != "disabled"
            or policy.get("reviewed_install_script_packages") != []
            or policy.get("native_modules") != NATIVE_MODULES):
        raise InstallError("Build policy is not supported", 5, "unsupported")
    if any(not isinstance(item, dict) or item.get("hasInstallScript")
           for item in packages.values()):
        raise InstallError("Install scripts require a new reviewed build policy", 5, "unsupported")
    for item in packages.values():
        if "resolved" not in item:
            continue
        try:
            source = urlsplit(item["resolved"]) if isinstance(item["resolved"], str) else None
        except ValueError:
            source = None
        if (source is None or source.scheme != "https" or source.netloc != "registry.npmjs.org"
                or not source.path.startswith("/") or source.query or source.fragment):
            raise InstallError("Package sources must use the official npm HTTPS registry", 5, "unsupported")
    # The scoped override is a reviewed compatibility fix, not an npm audit downgrade.
    if manifest.get("overrides") != {"lody": {"tinypool": "2.1.2"}}:
        raise InstallError("Reviewed Tinypool override is required", 5, "unsupported")
    pools = [item.get("version") for path, item in packages.items()
             if path.endswith("node_modules/tinypool")]
    if not pools or any(version != "2.1.2" for version in pools):
        raise InstallError("Lockfile does not contain the reviewed Tinypool version", 5, "unsupported")
    digest = hashlib.sha256((runtime_dir / "package-lock.json").read_bytes()).hexdigest()
    return version, digest


def _preflight():
    node, npm = shutil.which("node"), shutil.which("npm")
    if not node or not npm:
        raise InstallError("Node.js and npm are required")
    version = _run([node, "--version"], timeout=15).stdout.strip()
    if not supported_node(version):
        raise InstallError("Node.js >=22.14 <23 or >=23.6 is required", 5, "unsupported")
    return str(Path(node).resolve()), npm, version


def _safe_directory(path):
    if path.is_symlink() or (path.exists() and not path.is_dir()):
        raise InstallError("A managed directory has an unexpected file type")


def _check_layout(prefix):
    if any(parent.is_symlink() for parent in prefix.parents):
        raise InstallError("Installation prefix has a symlink ancestor")
    _safe_directory(prefix)
    if prefix.exists():
        marker = prefix / MARKER
        if not marker.exists():
            if any(prefix.iterdir()):
                raise InstallError("Refusing a nonempty unmanaged installation prefix")
        elif _read_json(marker) != OWNER:
            raise InstallError("Installation prefix has an unknown owner")
    for name in ("versions", "cache", "bin"):
        _safe_directory(prefix / name)
    lock = prefix / ".install.lock"
    if lock.is_symlink() or (lock.exists() and not lock.is_file()):
        raise InstallError("Installation lock has an unexpected file type")
    launcher = prefix / "bin/lody"
    if launcher.is_symlink() or (launcher.exists() and
            (not launcher.is_file() or launcher.read_text(encoding="utf-8") not in {LAUNCHER, LEGACY_LAUNCHER})):
        raise InstallError("Refusing to replace an unknown CLI launcher")
    current = prefix / "current"
    if current.is_symlink():
        target = current.readlink()
        if (target.is_absolute() or len(target.parts) != 2 or target.parts[0] != "versions"
                or not re.fullmatch(r"[0-9a-f]{64}", target.parts[1])):
            raise InstallError("Current runtime points outside a managed version")
        directory = prefix / target
        _safe_directory(directory)
        receipt = _read_json(directory / "receipt.json")
        if receipt.get("schema_version") != 1 or receipt.get("lock_sha256") != target.parts[1]:
            raise InstallError("Current runtime has no valid ownership receipt")
    elif current.exists():
        raise InstallError("Refusing an unknown current runtime path")


def _write_json(path, value):
    # A failed refresh must not truncate the active runtime's ownership receipt.
    fd, filename = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    os.close(fd)
    try:
        Path(filename).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(filename, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(filename)


def _restore_receipt(path, contents):
    fd, filename = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(contents)
        os.replace(filename, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(filename)


def _verify(directory, node, version):
    cli = directory / "node_modules/lody/dist/index.js"
    if not cli.is_file() or cli.is_symlink():
        raise InstallError("Installed Lody entrypoint is unavailable", 4, "install")
    with tempfile.TemporaryDirectory(prefix="lody4dot-verify-") as state:
        env = os.environ.copy()
        for name in PRIVATE_ENVIRONMENT_KEYS:
            env.pop(name, None)
        env.update({"LODY_DATA_DIR": state, "NO_COLOR": "1"})
        try:
            reported = _run([node, str(cli), "--version"], cwd=directory, env=env,
                            timeout=5).stdout
        except (InstallError, UnicodeError):
            actual = None
        else:
            actual = parse_cli_version(reported)
        warnings = version_warnings(actual, baseline=version)
        help_text = _run([node, str(cli), "--help"], cwd=directory, env=env,
                         timeout=45).stdout
        if "Usage: lody" not in help_text:
            raise InstallError("Installed Lody help check failed", 4, "install")
        native = _run([node, "--input-type=module", "-e", NATIVE_CHECK], cwd=directory,
                      env=env, timeout=45).stdout
        if native.strip() != "native-ok":
            raise InstallError("Installed native module check failed", 4, "native")
    return actual, warnings


def _replace_launcher(launcher, text):
    fd, filename = tempfile.mkstemp(prefix=".lody-", dir=launcher.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.chmod(filename, 0o755)
        os.replace(filename, launcher)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(filename)


def _activate(prefix, digest):
    # A failed current switch also restores the previous known launcher.
    launcher = prefix / "bin/lody"
    previous = launcher.read_text(encoding="utf-8") if launcher.exists() else None
    temporary = prefix / ".current-next"
    if temporary.is_symlink() or temporary.exists():
        raise InstallError("Unexpected activation temporary path; refusing replacement")
    changed = False
    try:
        temporary.symlink_to(Path("versions") / digest)
        if previous != LAUNCHER:
            _replace_launcher(launcher, LAUNCHER)
            changed = True
        else:
            launcher.chmod(0o755)
        os.replace(temporary, prefix / "current")
    except BaseException:
        if changed:
            if previous is None:
                launcher.unlink()
            else:
                _replace_launcher(launcher, previous)
        raise
    finally:
        with contextlib.suppress(FileNotFoundError):
            temporary.unlink()


def install(prefix, *, runtime_dir=None):
    try:
        platform_support.require_supported_platform()
    except platform_support.UnsupportedPlatform as exc:
        raise InstallError(str(exc), 5, "unsupported") from None
    prefix = Path(os.path.abspath(os.path.expanduser(str(prefix))))
    runtime_dir = Path(runtime_dir) if runtime_dir is not None else RUNTIME_DIR
    _inputs(runtime_dir)
    node, npm, node_version = _preflight()
    _check_layout(prefix)
    prefix.mkdir(parents=True, exist_ok=True)
    if not (prefix / MARKER).exists():
        _write_json(prefix / MARKER, OWNER)
    with (prefix / ".install.lock").open("a", encoding="utf-8") as lockfile:
        try:
            platform_support.acquire_install_lock(lockfile)
        except BlockingIOError:
            raise InstallError("Another installation owns this prefix; retry after it finishes") from None
        _check_layout(prefix)
        for name in ("versions", "cache", "bin"):
            (prefix / name).mkdir(exist_ok=True)
        receipt_backup = None
        receipt_update = None
        with tempfile.TemporaryDirectory(prefix=".staging-", dir=prefix / "versions") as temporary:
            staging = Path(temporary)
            for name in ("package.json", "package-lock.json", "build-policy.json"):
                shutil.copyfile(runtime_dir / name, staging / name)
            env = os.environ.copy()
            for name in PRIVATE_ENVIRONMENT_KEYS:
                env.pop(name, None)
            env["PATH"] = str(Path(node).parent) + os.pathsep + env.get("PATH", os.defpath)
            npm_options = ["--ignore-scripts", "--engine-strict", "--no-fund", "--no-audit",
                           "--registry=https://registry.npmjs.org", "--cache", str(prefix / "cache")]
            _run([npm, "update", "lody", "--package-lock-only", *npm_options],
                 cwd=staging, env=env, timeout=300)
            version, digest = _inputs(staging)
            destination = prefix / "versions" / digest
            _safe_directory(destination)
            reused = destination.exists()
            if reused:
                receipt = _read_json(destination / "receipt.json")
                _read_json(destination / "package-lock.json")
                _read_json(destination / "package.json")
                if (receipt.get("schema_version") != 1 or receipt.get("lock_sha256") != digest
                        or hashlib.sha256((destination / "package-lock.json").read_bytes()).hexdigest() != digest
                        or (destination / "package.json").read_bytes() != (staging / "package.json").read_bytes()):
                    raise InstallError("Existing version does not match its managed receipt")
                actual, warnings = _verify(destination, node, version)
                old_receipt = (destination / "receipt.json").read_bytes()
                receipt.update({"lody_version": actual, "baseline_lody_version": version,
                                "node_path": node, "node_version": node_version})
                receipt_backup = (destination / "receipt.json", old_receipt)
                receipt_update = (destination / "receipt.json", receipt)
            else:
                _run([npm, "ci", *npm_options], cwd=staging, env=env, timeout=300)
                actual, warnings = _verify(staging, node, version)
                _write_json(staging / "receipt.json", {
                    "schema_version": 1, "lody_version": actual,
                    "baseline_lody_version": version, "lock_sha256": digest,
                    "node_path": node, "node_version": node_version,
                    "platform": "linux", "native_modules": NATIVE_MODULES})
                staging.rename(destination)
                # TemporaryDirectory cleanup tolerates the renamed staging path.
        try:
            if receipt_update is not None:
                _write_json(*receipt_update)
            _activate(prefix, digest)
        except BaseException:
            if receipt_backup is not None:
                _restore_receipt(*receipt_backup)
            raise
    return {"schema_version": 1, "status": "pass", "error_category": None,
            "lody_version": actual, "actual_lody_version": actual,
            "baseline_lody_version": version, "warnings": warnings,
            "requested_lody_version": "latest", "node_path": node,
            "lock_sha256": digest, "reused": reused,
            "prefix": str(prefix), "cli": str(prefix / "bin/lody"),
            "evidence": (["version"] if actual is not None else []) + ["help", "native_modules"],
            "authentication": "not_run", "daemon": "not_run"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", default="/workspace/.tools/lody4dot")
    parser.add_argument("--json", action="store_true", help="Write machine-readable output")
    args = parser.parse_args(argv)
    try:
        result = install(args.prefix)
        code = 0
    except InstallError as error:
        result = {"schema_version": 1, "status": "blocked" if error.exit_code == 3 else "fail",
                  "error_category": error.category, "message": str(error),
                  "raw_exit_code": error.raw_exit_code}
        code = error.exit_code
    except (OSError, ValueError):
        result = {"schema_version": 1, "status": "fail", "error_category": "internal",
                  "message": "Installation could not complete; existing runtime was not replaced"}
        code = 10
    if args.json:
        print(json.dumps(result, sort_keys=True))
    elif code:
        print(result["message"], file=sys.stderr)
    else:
        for warning in result["warnings"]:
            print(f"WARN: {warning['message']} "
                  f"(baseline={warning['baseline']}, actual={warning['actual'] or 'unknown'})",
                  file=sys.stderr)
        print(f"Lody {result['lody_version'] or 'version unknown'} ready: "
              f"{result['cli']} (reused={result['reused']})")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
