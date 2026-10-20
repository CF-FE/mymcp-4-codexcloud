#!/usr/bin/env python3
"""Read-only Lody readiness checks. Never install, authenticate or start a host."""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess

from common import (DEFAULT_PREFIX, ToolError, emit, error_result, installed_cli,
                    offline_version, result, state_directory, supported_node,
                    verify_account, verify_catalog)


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
    catalog_error = None
    if args.connect:
        state = state_directory(args.data_dir)
        count = verify_account(cli, state, args.timeout)
        session = "authenticated"
        check("account", "pass", "Read-only workspace query succeeded.", observation=session, workspace_count=count)
        if args.workspace:
            try:
                count = verify_catalog(cli, state, args.workspace, args.timeout)
                check("workspace_catalog", "pass", "Selected workspace machine catalog query completed.",
                      machine_count=count, has_more=False, all_pages=True)
            except ToolError as exc:
                catalog_error = exc
                check("workspace_catalog", "blocked" if exc.code == 3 else "fail", str(exc),
                      error_category=exc.category, raw_exit_code=exc.raw_exit_code)
        else:
            check("workspace_catalog", "not_run", "Pass --workspace with --connect to check the machine catalog; account success does not verify this connection.")
    else:
        check("account", "not_run", "Use --connect with a private state directory for a read-only query.")
        check("workspace_catalog", "not_run", "No workspace catalog query was requested.")
    check("local_runtime", "not_run", "No daemon was started or inferred from CLI availability.")
    check("task_execution", "not_run", "Agent credentials, target and persisted task results require separate validation.")
    if catalog_error:
        value = error_result(catalog_error)
        value.update(profile=args.profile, checks=checks, credential_environment=credential, account=session)
        return value, catalog_error.code
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
    parser.add_argument("--workspace", help="Also check this workspace's complete machine catalog; requires --connect.")
    parser.add_argument("--data-dir")
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not 0 < args.timeout <= 300:
        parser.error("--timeout must be >0 and <=300")
    if args.workspace is not None and (not args.connect or not args.workspace.strip()):
        parser.error("--workspace requires --connect and a nonempty selector")
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
