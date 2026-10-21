#!/usr/bin/env python3
"""Explicit login adapter; local identity and remote registration are distinct."""
from __future__ import annotations

import argparse
import os

from common import (DEFAULT_PREFIX, ToolError, emit, error_result, installed_cli,
                    native_failure, offline_version, require_runtime_platform, result, run_native,
                    state_directory, verify_account, version_warnings)


def authenticate(args):
    require_runtime_platform()
    token = os.environ.get("LODY_CLI_TOKEN", "").strip()
    if args.login and not token:
        raise ToolError(3, "missing_credential", "LODY_CLI_TOKEN is not injected; no login was attempted.")
    cli = installed_cli(args.prefix)
    version = offline_version(cli, args.timeout)
    state = state_directory(args.data_dir, create=args.login)
    if args.login:
        # The verified CLI accepts credentials via argv only. No shell, history,
        # logging, debug output or native output forwarding. OS process visibility
        # still applies; document this boundary instead of inventing a transport.
        code, stdout, stderr = run_native(["node", cli, "login", "--auth", token],
                                         data_dir=state, timeout=args.timeout)
        if code:
            raise native_failure(code, stdout, stderr)
    count = verify_account(cli, state, args.timeout)
    return result("pass", operation="login" if args.login else "verify-only",
                  credential_environment="present" if token else "missing",
                  account="authenticated", evidence={"kind": "live_read_only_query", "workspace_count": count},
                  local_identity="written_by_login" if args.login else "not_modified",
                  machine_registration="not_verified" if args.login else "not_requested",
                  cli_version=version, warnings=version_warnings(version))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--login", action="store_true", help="Use LODY_CLI_TOKEN; writes identity and may connect/register a machine.")
    mode.add_argument("--verify-only", action="store_true", help="Read-only query using existing state; never log in.")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX)
    parser.add_argument("--data-dir", help="Private per-task state directory (or LODY_DATA_DIR).")
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not 0 < args.timeout <= 300:
        parser.error("--timeout must be >0 and <=300")
    try:
        value, code = authenticate(args), 0
    except ToolError as exc:
        value, code = error_result(exc), exc.code
    except (OSError, ValueError, TypeError):
        value, code = result("fail", error_category="internal", message="Authentication adapter failed; native details withheld."), 10
    emit(value, args.json)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
