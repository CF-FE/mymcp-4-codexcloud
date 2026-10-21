#!/usr/bin/env python3
"""Install the locked Lody runtime without login or daemon side effects."""

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

import platform_support
from common import parse_cli_version, version_warnings


MARKER = ".lody4dot-managed.json"
OWNER = {"schema_version": 1, "owner": "lody4dot"}
RUNTIME_DIR = Path(__file__).resolve().parent.parent / "runtime"
NATIVE_MODULES = ["better-sqlite3", "@lydell/node-pty", "@napi-rs/keyring",
                  "loro-crdt", "@loro-dev/roost-node"]
LAUNCHER = '''#!/usr/bin/env python3
# Managed by lody4dot installer
import os
from pathlib import Path
import sys

runtime = Path(__file__).resolve().parent.parent / "current"
os.execvp("node", ["node", str(runtime / "node_modules/lody/dist/index.js"), *sys.argv[1:]])
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
    version = manifest.get("dependencies", {}).get("lody")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise InstallError("Lody dependency must use one exact version", 5, "unsupported")
    packages = lock.get("packages")
    if (lock.get("lockfileVersion") != 3 or not isinstance(packages, dict)
            or packages.get("", {}).get("dependencies") != manifest.get("dependencies")
            or packages.get("node_modules/lody", {}).get("version") != version):
        raise InstallError("Manifest and lockfile do not agree", 5, "unsupported")
    if (policy.get("schema_version") != 1 or policy.get("lifecycle_scripts") != "disabled"
            or policy.get("reviewed_install_script_packages") != []
            or policy.get("native_modules") != NATIVE_MODULES):
        raise InstallError("Build policy is not supported", 5, "unsupported")
    if any(not isinstance(item, dict) or item.get("hasInstallScript")
           for item in packages.values()):
        raise InstallError("Install scripts require a new reviewed build policy", 5, "unsupported")
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
    return node, npm, version


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
            (not launcher.is_file() or launcher.read_text(encoding="utf-8") != LAUNCHER)):
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


def _verify(directory, node, version):
    cli = directory / "node_modules/lody/dist/index.js"
    if not cli.is_file() or cli.is_symlink():
        raise InstallError("Installed Lody entrypoint is unavailable", 4, "install")
    with tempfile.TemporaryDirectory(prefix="lody4dot-verify-") as state:
        env = os.environ.copy()
        env.pop("LODY_CLI_TOKEN", None)
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


def _activate(prefix, digest):
    # Nothing after current replacement may fail: old current remains usable until this point.
    launcher = prefix / "bin/lody"
    if not launcher.exists():
        fd, filename = tempfile.mkstemp(prefix=".lody-", dir=launcher.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(LAUNCHER)
            os.chmod(filename, 0o755)
            os.replace(filename, launcher)
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(filename)
    else:
        launcher.chmod(0o755)
    temporary = prefix / ".current-next"
    if temporary.is_symlink() or temporary.exists():
        raise InstallError("Unexpected activation temporary path; refusing replacement")
    try:
        temporary.symlink_to(Path("versions") / digest)
        os.replace(temporary, prefix / "current")
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
    version, digest = _inputs(runtime_dir)
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
        destination = prefix / "versions" / digest
        _safe_directory(destination)
        reused = destination.exists()
        if reused:
            receipt = _read_json(destination / "receipt.json")
            _read_json(destination / "package-lock.json")
            _read_json(destination / "package.json")
            if (receipt.get("schema_version") != 1 or receipt.get("lock_sha256") != digest
                    or hashlib.sha256((destination / "package-lock.json").read_bytes()).hexdigest() != digest
                    or (destination / "package.json").read_bytes() != (runtime_dir / "package.json").read_bytes()):
                raise InstallError("Existing version does not match its managed receipt")
            actual, warnings = _verify(destination, node, version)
            receipt.update({"lody_version": actual, "baseline_lody_version": version})
            _write_json(destination / "receipt.json", receipt)
        else:
            with tempfile.TemporaryDirectory(prefix=".staging-", dir=prefix / "versions") as temporary:
                staging = Path(temporary)
                for name in ("package.json", "package-lock.json", "build-policy.json"):
                    shutil.copyfile(runtime_dir / name, staging / name)
                env = os.environ.copy()
                env.pop("LODY_CLI_TOKEN", None)
                _run([npm, "ci", "--ignore-scripts", "--no-fund", "--no-audit",
                      "--cache", str(prefix / "cache")], cwd=staging, env=env, timeout=300)
                actual, warnings = _verify(staging, node, version)
                _write_json(staging / "receipt.json", {
                    "schema_version": 1, "lody_version": actual,
                    "baseline_lody_version": version, "lock_sha256": digest,
                    "node_version": node_version, "platform": "linux", "native_modules": NATIVE_MODULES})
                staging.rename(destination)
                # TemporaryDirectory cleanup tolerates the renamed staging path.
        _activate(prefix, digest)
    return {"schema_version": 1, "status": "pass", "error_category": None,
            "lody_version": actual, "actual_lody_version": actual,
            "baseline_lody_version": version, "warnings": warnings,
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
