#!/usr/bin/env python3
"""Read-only Lody readiness checks. Never install, authenticate or start a host."""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess

from common import (DEFAULT_PREFIX, ToolError, emit, error_result, installed_cli,
                    offline_version, result, state_directory, supported_node, verify_account)


def diagnose(args):
    checks = []
    def check(name, status, message, **evidence):
        checks.append(dict(name=name, status=status, message=message, evidence=evidence))
    credential = "present" if os.environ.get("LODY_CLI_TOKEN", "").strip() else "missing"
    check("credential_environment", "pass" if credential == "present" else "not_run",
          "LODY_CLI_TOKEN presence only; no authentication inferred.", observation=credential)
    if platform.system() != "Linux":
        raise ToolError(5, "unsupported_platform", "This installer supports Linux only.")
    if not shutil.which("node"):
        raise ToolError(3, "missing_executable", "Node is unavailable.")
    try:
        node = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=args.timeout)
    except subprocess.TimeoutExpired as exc:
        raise ToolError(4, "timeout", "Node version check timed out.") from exc
    if node.returncode or not supported_node(node.stdout):
        raise ToolError(5, "unsupported_node", "Node must be >=22.14 <23 or >=23.6.")
    check("node", "pass", "Supported Node version.", version=node.stdout.strip())
    cli = installed_cli(args.prefix)
    version = offline_version(cli, args.timeout)
    check("runtime", "pass", "Managed CLI reports the supported version.", version=version)
    session = "not_run"
    if args.connect:
        state = state_directory(args.data_dir)
        count = verify_account(cli, state, args.timeout)
        session = "authenticated"
        check("account", "pass", "Read-only workspace query succeeded.", observation=session, workspace_count=count)
    else:
        check("account", "not_run", "Use --connect with a private state directory for a read-only query.")
    check("local_runtime", "not_run", "No daemon was started or inferred from CLI availability.")
    check("task_execution", "not_run", "Agent credentials, target and persisted task results require separate validation.")
    passed = args.profile == "inspect" or (args.profile == "control" and args.connect)
    if not passed:
        check("requested_profile", "blocked", "Requested profile has prerequisites that these checks have not verified.")
    return result("pass" if passed else "blocked", profile=args.profile, checks=checks,
                  credential_environment=credential, account=session,
                  error_category=None if passed else "unverified_prerequisites"), 0 if passed else 3


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", default=DEFAULT_PREFIX)
    parser.add_argument("--profile", choices=("inspect", "control", "task", "worker"), default="inspect")
    parser.add_argument("--connect", action="store_true", help="Explicitly perform a read-only workspace query.")
    parser.add_argument("--data-dir")
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not 0 < args.timeout <= 300:
        parser.error("--timeout must be >0 and <=300")
    try:
        value, code = diagnose(args)
    except ToolError as exc:
        value, code = error_result(exc), exc.code
        value["profile"] = args.profile
    except (OSError, ValueError, TypeError):
        value, code = result("fail", error_category="internal", message="Diagnostic failed; native details withheld."), 10
    emit(value, args.json)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
