"""Small shared boundary for diagnostic and explicit authentication commands."""
from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import signal
import subprocess
import sys
import tempfile

import platform_support

SCHEMA_VERSION = 1


def _lock_baseline():
    """The shipped lock is an observation, not the installation version policy."""
    try:
        runtime = Path(__file__).resolve().parent.parent / "runtime"
        lock, _ = _provenance_json(runtime, "package-lock.json")
        value = lock["packages"]["node_modules/lody"]["version"]
        return value if isinstance(value, str) and re.fullmatch(r"\d+\.\d+\.\d+", value) else None
    except (OSError, ValueError, KeyError, TypeError):
        return None


DEFAULT_PREFIX = "/workspace/.tools/lody4dot"


def parse_cli_version(value):
    """Retain only a bounded version token, never arbitrary command output."""
    if not isinstance(value, str) or len(value) > 128:
        return None
    value = value.strip()
    match = re.fullmatch(
        r"v?([0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?)", value)
    return match.group(1) if match else None


def version_warnings(actual, baseline=None):
    """Versions are observations and advice, never execution prerequisites."""
    if baseline is None:
        baseline = LODY_VERSION
    actual, baseline = parse_cli_version(actual), parse_cli_version(baseline)
    if actual is None:
        return [{"code": "cli_version_unknown", "status": "warn", "actual": None,
                 "baseline": baseline,
                 "message": "Lody CLI version is unknown; continue with actual command results."}]
    if actual != baseline:
        return [{"code": "cli_version_differs_from_baseline", "status": "warn", "actual": actual,
                 "baseline": baseline,
                 "message": "Lody CLI differs from the tested baseline; execution is not blocked."}]
    return []


class ToolError(Exception):
    def __init__(self, code: int, category: str, message: str, raw_exit_code=None, *, failure_layer=None):
        super().__init__(message)
        self.code, self.category, self.raw_exit_code = code, category, raw_exit_code
        self.failure_layer = failure_layer


def require_runtime_platform():
    """Reject unsupported systems before POSIX state or native process work."""
    try:
        platform_support.require_supported_platform()
    except platform_support.UnsupportedPlatform as exc:
        raise ToolError(5, "unsupported_platform", str(exc)) from None


def result(status, **fields):
    return {"schema_version": SCHEMA_VERSION, "status": status, **fields}


def emit(value, as_json):
    if as_json:
        print(json.dumps(value, ensure_ascii=False, sort_keys=True))
    else:
        print(f"{value['status']}: {value.get('message', value.get('profile', 'lody4dot'))}")
        for check in value.get("checks", []):
            print(f"  {check['name']}: {check['status']} — {check['message']}")
        for warning in value.get("warnings", []):
            print(f"  warn: {warning['message']}")


def error_result(error):
    value = result("blocked" if error.code == 3 else "fail", error_category=error.category,
                   message=str(error), raw_exit_code=error.raw_exit_code)
    if error.failure_layer is not None:
        value["failure_layer"] = error.failure_layer
    return value


def supported_node(version):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", version.strip())
    if not match:
        return False
    major, minor, _ = map(int, match.groups())
    return (major == 22 and minor >= 14) or (major == 23 and minor >= 6) or major >= 24


def installed_cli(prefix):
    """Resolve only our managed runtime; do not trust arbitrary symlink targets."""
    prefix = Path(prefix).absolute()
    try:
        if prefix.is_symlink():
            raise ValueError("symlink prefix")
        marker_path = prefix / ".lody4dot-managed.json"
        if marker_path.is_symlink():
            raise ValueError("symlink marker")
        marker, _ = _provenance_json(prefix, ".lody4dot-managed.json")
        if marker.get("owner") != "lody4dot" or marker.get("schema_version") != 1:
            raise ValueError("foreign marker")
        current = prefix / "current"
        if not current.is_symlink():
            raise ValueError("missing managed pointer")
        relative = Path(os.readlink(current))
        if len(relative.parts) != 2 or relative.parts[0] != "versions" or not re.fullmatch(r"[a-f0-9]{64}", relative.parts[1]):
            raise ValueError("invalid managed pointer")
        version_dir = prefix / relative
        if (prefix / "versions").is_symlink() or version_dir.is_symlink():
            raise ValueError("external version")
        receipt_path = version_dir / "receipt.json"
        if receipt_path.is_symlink():
            raise ValueError("external receipt")
        receipt, _ = _provenance_json(version_dir, "receipt.json")
        if receipt.get("schema_version") != 1 or receipt.get("lock_sha256") != relative.name:
            raise ValueError("invalid receipt")
        cli = version_dir / "node_modules/lody/dist/index.js"
        if not cli.is_file() or not cli.resolve().is_relative_to(version_dir.resolve()):
            raise ValueError("missing CLI")
        return cli
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        raise ToolError(3, "missing_runtime", "Managed Lody runtime is unavailable; run install.py.") from exc


def node_for_cli(cli):
    """Keep the interpreter that was validated when this owned CLI was installed."""
    cli = Path(cli)
    if (cli.name != "index.js" or cli.parent.name != "dist"
            or cli.parent.parent.name != "lody"):
        return "node"
    runtime = cli.parents[3]
    receipt_path = runtime / "receipt.json"
    if not receipt_path.exists():
        return "node"
    try:
        receipt, _ = _provenance_json(runtime, "receipt.json")
        if "node_path" not in receipt:
            return "node"  # Previously installed receipts retain their PATH behavior.
        raw = receipt["node_path"]
        if not isinstance(raw, str) or not raw or len(raw) > 4096:
            raise ValueError("invalid interpreter")
        node = Path(raw)
        if not node.is_absolute() or node.resolve() != node:
            raise ValueError("invalid interpreter")
        if not node.is_file() or not os.access(node, os.X_OK):
            raise ToolError(3, "missing_executable", "Managed Node executable is unavailable; prepare supported Node.")
        return str(node)
    except ToolError:
        raise
    except (OSError, ValueError, TypeError):
        raise ToolError(5, "invalid_runtime", "Managed Node interpreter receipt is invalid.") from None


def _provenance_bytes(root, relative, limit=2 * 1024 * 1024):
    """Read bounded local evidence without following package members out of root."""
    name = PurePosixPath(relative)
    if (not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative
            or name.is_absolute() or name.as_posix() != relative or ".." in name.parts):
        raise ValueError("invalid evidence path")
    root = Path(root).absolute()
    if root.resolve() != root:
        raise ValueError("symlinked evidence root")
    path = root
    for part in name.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("symlinked evidence")
    if not path.is_file() or path.stat().st_size > limit:
        raise ValueError("unavailable evidence")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("evidence exceeds limit")
    return raw


def _provenance_json(root, relative):
    raw = _provenance_bytes(root, relative)
    try:
        value = json.loads(raw)
    except RecursionError as exc:
        raise ValueError("evidence nesting exceeds parser limit") from exc
    if not isinstance(value, dict):
        raise ValueError("invalid evidence object")
    return value, hashlib.sha256(raw).hexdigest()


LODY_VERSION = _lock_baseline()


def _bundle_member(name):
    """Limit hashes to the existing package layout, never identity/cache files."""
    if not isinstance(name, str):
        return False
    parts = PurePosixPath(name).parts
    sensitive_name = r"(^\.env($|\.)|(^|[._-])(token|credentials?|secrets?)([._-]|$)|\.(pem|key|p12|pfx)$)"
    if any(re.search(sensitive_name, part, re.IGNORECASE) for part in parts):
        return False
    return (name in {"README.md", ".codex-plugin/plugin.json", ".agents/plugins/marketplace.json"}
            or name in {"hosts/codex-cloud.md", "hosts/codex-cli.md", "hosts/dot.md"}
            or len(parts) == 2 and parts[0] == "scripts" and parts[1].endswith(".py")
            or name in {"runtime/package.json", "runtime/package-lock.json", "runtime/build-policy.json"}
            or name in {"skills/lody4dot/SKILL.md", "skills/lody4dot-setup/SKILL.md"}
            or len(parts) == 4 and parts[:3] == ("skills", "lody4dot", "references")
            and PurePosixPath(name).suffix in {".md", ".json"})


def local_provenance(prefix, package_root):
    """Report independent local sources; hashes are not signatures or release proof."""
    value = {"assurance": "local_file_consistency_only",
             "plugin": {"status": "not_provided"},
             "bundle": {"status": "not_provided", "coverage": "receipt_listed_files_only"},
             "runtime": {"status": "not_provided"}}
    package_root = Path(package_root).absolute()
    semver = r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?"
    manifest_version = None
    manifest_path = package_root / ".codex-plugin/plugin.json"
    if manifest_path.exists() or manifest_path.is_symlink():
        try:
            manifest, digest = _provenance_json(package_root, ".codex-plugin/plugin.json")
            version = manifest.get("version")
            if manifest.get("name") != "lody4dot" or not isinstance(version, str) or not re.fullmatch(semver, version):
                raise ValueError("invalid plugin manifest")
            manifest_version = version
            value["plugin"] = {"status": "observed", "version": version,
                               "source": ".codex-plugin/plugin.json", "manifest_sha256": digest}
        except (OSError, ValueError, TypeError):
            value["plugin"] = {"status": "invalid"}
    receipt_path = package_root / ".lody4dot-build.json"
    if receipt_path.exists() or receipt_path.is_symlink():
        try:
            receipt, digest = _provenance_json(package_root, ".lody4dot-build.json")
            files, version = receipt.get("files"), receipt.get("plugin_version")
            if (receipt.get("schema_version") != 1 or receipt.get("tool") != "lody4dot-build"
                    or not isinstance(version, str) or not re.fullmatch(semver, version)
                    or not isinstance(files, dict) or not 0 < len(files) <= 512
                    or ".codex-plugin/plugin.json" not in files
                    or any(not _bundle_member(name) or not isinstance(digest, str)
                           or not re.fullmatch(r"[a-f0-9]{64}", digest) for name, digest in files.items())):
                raise ValueError("invalid bundle receipt")
            consistent = manifest_version == version
            total = 0
            for name, expected in files.items():
                try:
                    raw = _provenance_bytes(package_root, name)
                    total += len(raw)
                    if total > 16 * 1024 * 1024:
                        consistent = False
                        break
                    consistent = hashlib.sha256(raw).hexdigest() == expected and consistent
                except (OSError, ValueError):
                    consistent = False
            value["bundle"] = {"status": "consistent" if consistent else "mismatch",
                               "receipt_sha256": digest, "plugin_version": version,
                               "listed_file_count": len(files), "coverage": "receipt_listed_files_only"}
        except (OSError, ValueError, TypeError):
            value["bundle"] = {"status": "invalid", "coverage": "receipt_listed_files_only"}
    marker = Path(prefix).absolute() / ".lody4dot-managed.json"
    if marker.exists() or marker.is_symlink():
        try:
            cli = installed_cli(prefix)
            runtime = cli.parents[3]
            receipt, digest = _provenance_json(runtime, "receipt.json")
            expected = receipt.get("lock_sha256")
            if not isinstance(expected, str) or not re.fullmatch(r"[a-f0-9]{64}", expected):
                raise ValueError("invalid runtime receipt")
            actual = None
            try:
                actual = hashlib.sha256(_provenance_bytes(runtime, "package-lock.json")).hexdigest()
            except (OSError, ValueError):
                pass
            value["runtime"] = {"status": "consistent" if actual == expected else "mismatch",
                                "lody_version": parse_cli_version(receipt.get("lody_version")),
                                "version_source": "installation_receipt",
                                "baseline_lody_version": parse_cli_version(receipt.get("baseline_lody_version")),
                                "receipt_sha256": digest,
                                "lock_sha256": expected, "actual_lock_sha256": actual}
        except (ToolError, OSError, ValueError, TypeError, IndexError):
            value["runtime"] = {"status": "invalid"}
    return value


def state_directory(argument, *, create=False):
    require_runtime_platform()
    raw = argument or os.environ.get("LODY_DATA_DIR")
    if not raw:
        raise ToolError(3, "missing_state_directory", "Set a private per-task LODY_DATA_DIR or pass --data-dir.")
    path = Path(raw).absolute()
    if path.is_symlink() or path.resolve() != path:
        raise ToolError(3, "unsafe_state_directory", "State directory must not traverse symbolic links.")
    if create:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not path.is_dir():
        raise ToolError(3, "missing_state_directory", "State directory does not exist.")
    stat = path.stat()
    if stat.st_uid != os.getuid() or stat.st_mode & 0o077:
        raise ToolError(3, "unsafe_state_directory", "State directory must be owned by the current user with mode 0700.")
    return path


def run_native(argv, *, data_dir, timeout=30, keep_token=False):
    """Capture native output without ever echoing it or subprocess arguments."""
    require_runtime_platform()
    env = os.environ.copy()
    env.update(LODY_DATA_DIR=str(data_dir), NO_COLOR="1")
    if not keep_token:
        env.pop("LODY_CLI_TOKEN", None)
    argv = list(argv)
    if len(argv) > 1 and str(argv[0]) == "node":
        argv[0] = node_for_cli(argv[1])
    try:
        process = subprocess.Popen([str(a) for a in argv], env=env, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   start_new_session=True)
    except FileNotFoundError as exc:
        raise ToolError(3, "missing_executable", "Required executable is unavailable.") from exc
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate()
        raise ToolError(4, "timeout", "Lody command timed out; no automatic retry was made.") from exc
    return process.returncode, stdout, stderr


def native_failure(code, stdout, stderr):
    # Classify without forwarding output: even arbitrary token encodings stay private.
    content = (stdout + "\n" + stderr).lower()
    # These signals identify a rejected proxy tunnel, not an object ACL decision.
    proxy_denial = bool(re.search(r"tunnel connection failed:\s*(?:403|407)\b|\bconnect\s+(?:403|407)\b", content))
    if proxy_denial:
        category = "network"
    elif any(s in content for s in ("invalid or expired", "unauthorized", "login required", "not authenticated", "please login", "run `lody login`", "not logged in")):
        category = "authentication"
    elif any(s in content for s in ("permission", "forbidden", "access denied")):
        category = "permission"
    elif any(s in content for s in ("network", "fetch failed", "connect", "certificate", "enotfound")):
        category = "network"
    else:
        category = "native_command"
    return ToolError(4, category, "Lody command failed; native output was withheld to protect credentials.", code,
                     failure_layer="proxy_transport" if proxy_denial else None)


def parse_native_json(stdout):
    """Accept JSON, or one record surrounded only by pinned Streams diagnostics."""
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as original:
        lines = [line.removesuffix("\r") for line in stdout.split("\n") if line.strip(" \t\r")]
        records = []
        for index, line in enumerate(lines):
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                records.append((index, value))
        if len(records) != 1 or len(lines) < 2:
            raise ValueError("Expected one native JSON record") from original
        record_index, payload = records[0]
        workspace_id = payload.get("workspaceId")
        if not isinstance(workspace_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", workspace_id):
            raise ValueError("Expected a valid workspace ID") from original
        # Lody 0.107.2 emits these two exact messages on stdout from its
        # Streams attach/detach path. No other log line may be discarded.
        diagnostics = {
            f"[{workspace_id}] Remote Streams transport attached",
            f"[{workspace_id}] Remote Streams transport detached",
        }
        if any(line not in diagnostics for index, line in enumerate(lines) if index != record_index):
            raise ValueError("Unexpected text around native JSON") from original
        print(f"lody4dot: ignored {len(lines) - 1} recognized Streams diagnostic line(s).", file=sys.stderr)
        return payload


def verify_account(cli, data_dir, timeout):
    code, stdout, stderr = run_native(["node", cli, "workspace", "list", "--json"],
                                     data_dir=data_dir, timeout=timeout)
    if code:
        raise native_failure(code, stdout, stderr)
    try:
        payload = parse_native_json(stdout)
        spaces = payload["workspaces"]
        if payload.get("ok") is not True or not isinstance(spaces, list):
            raise ValueError("unexpected schema")
        if any(not isinstance(w, dict) or not isinstance(w.get("id"), str) or not isinstance(w.get("name"), str) for w in spaces):
            raise ValueError("unexpected workspace")
    except (ValueError, KeyError, TypeError) as exc:
        raise ToolError(4, "invalid_response", "Workspace query returned an invalid or empty JSON response.", code) from exc
    return len(spaces)


def verify_catalog(cli, data_dir, workspace, timeout):
    """Probe the workspace catalog separately from the account-only endpoint."""
    code, stdout, stderr = run_native(
        ["node", cli, "machine", "list", "--workspace", workspace, "--all-pages", "--json"],
        data_dir=data_dir, timeout=timeout)
    if code:
        raise native_failure(code, stdout, stderr)
    try:
        # 0.107.2 runDiscoveryList prints the final page's hasMore/nextCursor
        # alongside the accumulated canonical items and a machines alias.
        payload = parse_native_json(stdout)
        machines = payload["items"]
        if (payload.get("ok", True) is not True or not isinstance(machines, list)
                or payload.get("hasMore") is not False or payload.get("nextCursor") is not None):
            raise ValueError("incomplete or unexpected catalog page")
        if any(not isinstance(machine, dict)
               or not isinstance(machine.get("id"), str) or not machine["id"].strip()
               or not isinstance(machine.get("name"), str) for machine in machines):
            raise ValueError("unexpected machine")
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise ToolError(4, "invalid_response", "Machine catalog query returned invalid JSON or incomplete pagination.", code) from exc
    # 0.108.1 can exit successfully with a partial catalog while syncing.
    # Completed pages, including older versions, may omit sync entirely.
    sync = payload.get("sync")
    if isinstance(sync, dict) and sync.get("state") == "syncing":
        raise ToolError(3, "catalog_syncing",
                        "Machine catalog is still syncing; a complete catalog has not been verified.", code)
    return len(machines)


def offline_version(cli, timeout):
    require_runtime_platform()
    try:
        with tempfile.TemporaryDirectory(prefix="lody4dot-inspect-") as state:
            code, stdout, _ = run_native(["node", cli, "--version"], data_dir=state, timeout=min(timeout, 5))
        return parse_cli_version(stdout) if code == 0 else None
    except (ToolError, OSError, ValueError, TypeError):
        return None
