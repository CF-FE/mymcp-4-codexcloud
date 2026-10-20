"""Small shared boundary for diagnostic and explicit authentication commands."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile

SCHEMA_VERSION = 1
LODY_VERSION = "0.107.2"
DEFAULT_PREFIX = "/workspace/.tools/lody4dot"


class ToolError(Exception):
    def __init__(self, code: int, category: str, message: str, raw_exit_code=None):
        super().__init__(message)
        self.code, self.category, self.raw_exit_code = code, category, raw_exit_code


def result(status, **fields):
    return {"schema_version": SCHEMA_VERSION, "status": status, **fields}


def emit(value, as_json):
    if as_json:
        print(json.dumps(value, ensure_ascii=False, sort_keys=True))
    else:
        print(f"{value['status']}: {value.get('message', value.get('profile', 'lody4dot'))}")
        for check in value.get("checks", []):
            print(f"  {check['name']}: {check['status']} — {check['message']}")


def error_result(error):
    return result("blocked" if error.code == 3 else "fail", error_category=error.category,
                  message=str(error), raw_exit_code=error.raw_exit_code)


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
        marker = json.loads(marker_path.read_text())
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
        receipt = json.loads(receipt_path.read_text())
        if receipt.get("schema_version") != 1 or receipt.get("lock_sha256") != relative.name:
            raise ValueError("invalid receipt")
        cli = version_dir / "node_modules/lody/dist/index.js"
        if not cli.is_file() or not cli.resolve().is_relative_to(version_dir.resolve()):
            raise ValueError("missing CLI")
        if receipt.get("lody_version") != LODY_VERSION:
            raise ToolError(5, "unsupported_version", "Installed Lody version is unsupported.")
        return cli
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        raise ToolError(3, "missing_runtime", "Managed Lody runtime is unavailable; run install.py.") from exc


def state_directory(argument, *, create=False):
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
    env = os.environ.copy()
    env.update(LODY_DATA_DIR=str(data_dir), NO_COLOR="1")
    if not keep_token:
        env.pop("LODY_CLI_TOKEN", None)
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
    if any(s in content for s in ("invalid or expired", "unauthorized", "login required", "not authenticated", "please login", "run `lody login`", "not logged in")):
        category = "authentication"
    elif any(s in content for s in ("permission", "forbidden", "access denied")):
        category = "permission"
    elif any(s in content for s in ("network", "fetch failed", "connect", "certificate", "enotfound")):
        category = "network"
    else:
        category = "native_command"
    return ToolError(4, category, "Lody command failed; native output was withheld to protect credentials.", code)


def verify_account(cli, data_dir, timeout):
    code, stdout, stderr = run_native(["node", cli, "workspace", "list", "--json"],
                                     data_dir=data_dir, timeout=timeout)
    if code:
        raise native_failure(code, stdout, stderr)
    try:
        payload = json.loads(stdout)
        spaces = payload["workspaces"]
        if payload.get("ok") is not True or not isinstance(spaces, list):
            raise ValueError("unexpected schema")
        if any(not isinstance(w, dict) or not isinstance(w.get("id"), str) or not isinstance(w.get("name"), str) for w in spaces):
            raise ValueError("unexpected workspace")
    except (ValueError, KeyError, TypeError) as exc:
        raise ToolError(4, "invalid_response", "Workspace query returned an invalid or empty JSON response.", code) from exc
    return len(spaces)


def offline_version(cli, timeout):
    with tempfile.TemporaryDirectory(prefix="lody4dot-inspect-") as state:
        code, stdout, stderr = run_native(["node", cli, "--version"], data_dir=state, timeout=timeout)
    if code:
        raise native_failure(code, stdout, stderr)
    if stdout.strip() != LODY_VERSION:
        raise ToolError(5, "unsupported_version", "Runtime did not report the supported Lody version.", code)
    return LODY_VERSION
