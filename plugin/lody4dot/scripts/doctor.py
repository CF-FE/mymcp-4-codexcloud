#!/usr/bin/env python3
"""Read-only Lody readiness checks. Never install, authenticate or start a host."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
import platform
from pathlib import Path
import re
import shutil
import subprocess
import sys

from common import (DEFAULT_PREFIX, LODY_VERSION, ToolError, emit, error_result, installed_cli,
                    local_provenance, node_for_cli, offline_version, require_runtime_platform, result,
                    parse_cli_version, state_directory, supported_node, verify_account,
                    verify_catalog, version_warnings)


# A short-lived, isolated child gives the complete network operation a wall-clock
# deadline, including DNS. Only the selected version crosses this boundary.
_LATEST_QUERY = '''import json
from urllib.request import Request, HTTPRedirectHandler, build_opener
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
try:
    request = Request("https://registry.npmjs.org/lody/latest", headers={"Accept": "application/json"})
    with build_opener(NoRedirect()).open(request, timeout=5) as response:
        if response.status != 200:
            raise ValueError("registry response")
        payload = response.read(65537)
    if len(payload) > 65536:
        raise ValueError("registry response size")
    value = json.loads(payload)["version"]
    if not isinstance(value, str) or len(value) > 128:
        raise ValueError("registry version")
    print(json.dumps(value))
except Exception:
    raise SystemExit(1)
'''


def _registry_latest(timeout):
    """Best-effort latest tag query; never return native response or fail a task."""
    env = os.environ.copy()
    for name in ("LODY_CLI_TOKEN", "GITEE_ACCESS_TOKEN", "NPM_TOKEN", "NODE_AUTH_TOKEN"):
        env.pop(name, None)
    try:
        response = subprocess.run([sys.executable, "-I", "-B", "-c", _LATEST_QUERY],
                                  env=env, stdin=subprocess.DEVNULL, capture_output=True,
                                  text=True, timeout=min(timeout, 5), check=False)
        if response.returncode or len(response.stdout) > 1024:
            return None
        return parse_cli_version(json.loads(response.stdout))
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired):
        return None


def _update_check(actual, latest):
    evidence = dict(actual=actual, latest=latest,
                    source="https://registry.npmjs.org/lody/latest", automatic_upgrade=False)
    if latest is None:
        return "warn", "Latest-version check was unavailable; execution continues.", dict(evidence, observation="unavailable")
    if actual == latest:
        return "pass", "Installed CLI matches the registry latest tag.", dict(evidence, observation="current")
    stable = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    if (actual is not None and re.fullmatch(stable, actual) and re.fullmatch(stable, latest)
            and tuple(map(int, actual.split("."))) < tuple(map(int, latest.split(".")))):
        return "warn", "A newer Lody CLI is available; execution continues without upgrading.", dict(evidence, observation="update_available")
    return "warn", "The installed version cannot be classified as behind latest; execution continues.", dict(evidence, observation="comparison_unknown")


def diagnose(args):
    observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    checks = []
    def check(name, status, message, **evidence):
        value = dict(name=name, status=status, message=message, evidence=evidence)
        for index, previous in enumerate(checks):
            if previous["name"] == name:
                checks[index] = value
                return
        checks.append(value)

    credential = "present" if os.environ.get("LODY_CLI_TOKEN", "").strip() else "missing"
    check("credential_environment", "pass" if credential == "present" else "not_run",
          "LODY_CLI_TOKEN presence only; no authentication inferred.", observation=credential)
    for name, message in (
        ("node", "Node version was not checked."),
        ("runtime", "Managed CLI was not checked."),
        ("cli_version", "CLI version observation was not run."),
        ("cli_updates", "Latest-version check was not requested; use --check-updates for an advisory query."),
        ("account", "No successful read-only account query was observed."),
        ("workspace_catalog", "No complete workspace machine catalog was observed."),
        ("local_runtime", "No daemon was started or inferred from CLI availability."),
        ("task_execution", "Agent credentials, target and persisted task results require separate validation."),
    ):
        check(name, "not_run", message)
    provenance = local_provenance(args.prefix, Path(__file__).resolve().parent.parent)
    sources = {name: provenance[name]["status"] for name in ("plugin", "bundle", "runtime")}
    provenance_failed = any(status in {"invalid", "mismatch"} for status in sources.values())
    if provenance_failed:
        check("provenance", "fail", "Local provenance evidence is invalid or inconsistent.",
              sources=sources, reasons={name: provenance[name].get("reason") for name in sources
                                       if sources[name] in {"invalid", "mismatch"}})
    elif "not_provided" in sources.values():
        check("provenance", "warn", "Some local provenance evidence was not provided; consistency is not fully verified.",
              sources=sources)
    else:
        check("provenance", "pass", "Provided local evidence is consistent; this is not signature or release verification.",
              sources=sources, coverage="receipt_listed_files_only")
    session, cli, failure = "not_run", None, None
    active = "platform"
    try:
        require_runtime_platform()
        active = "node"
        runtime_error = None
        try:
            cli = installed_cli(args.prefix)
        except ToolError as exc:
            runtime_error = exc
        executable = node_for_cli(cli) if cli is not None else "node"
        if executable == "node" and not shutil.which("node"):
            raise ToolError(3, "missing_executable", "Node is unavailable.")
        if provenance_failed:
            # Preserve a known prerequisite error, but never run a probe or repair
            # using evidence already known to be invalid or inconsistent.
            if runtime_error is not None:
                active = "runtime"
                raise runtime_error
            active = "provenance"
            raise ToolError(5, "invalid_provenance", "Local provenance validation failed; execution was not attempted.")
        try:
            node = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=args.timeout)
        except subprocess.TimeoutExpired as exc:
            raise ToolError(4, "timeout", "Node version check timed out.") from exc
        if node.returncode or not supported_node(node.stdout):
            raise ToolError(5, "unsupported_node", "Node must be >=22.14 <23 or >=23.6.")
        check("node", "pass", "Supported tooling Node version; installer checks CLI dependency engines.",
              version=node.stdout.strip(), executable=executable)
        active = "runtime"
        if runtime_error is not None:
            raise runtime_error
        version = offline_version(cli, args.timeout)
        if version is None:
            check("runtime", "warn", "Managed CLI entrypoint exists; version execution was not verified.", version=None)
        else:
            check("runtime", "pass", "Managed CLI version command completed; no version restriction is applied.", version=version)
        warnings = version_warnings(version)
        if warnings:
            warning = warnings[0]
            check("cli_version", "warn", warning["message"], code=warning["code"],
                  actual=warning["actual"], baseline=warning["baseline"])
        else:
            check("cli_version", "pass", "CLI version matches the tested baseline; this is advisory.",
                  actual=version, baseline=LODY_VERSION)
        if args.check_updates:
            status, message, evidence = _update_check(version, _registry_latest(args.timeout))
            check("cli_updates", status, message, **evidence)
        if args.connect:
            active = "account"
            state = state_directory(args.data_dir)
            count = verify_account(cli, state, args.timeout)
            session = "authenticated"
            check("account", "pass", "Read-only workspace query succeeded.",
                  observation=session, workspace_count=count)
            if args.workspace:
                active = "workspace_catalog"
                count = verify_catalog(cli, state, args.workspace, args.timeout)
                check("workspace_catalog", "pass", "Selected workspace machine catalog query completed.",
                      machine_count=count, has_more=False, all_pages=True)
            else:
                check("workspace_catalog", "not_run", "Pass --workspace with --connect to check the machine catalog; account success does not verify this connection.")
        else:
            check("account", "not_run", "Use --connect with a private state directory for a read-only query.")
            check("workspace_catalog", "not_run", "No workspace catalog query was requested.")
    except ToolError as exc:
        failure = exc
    except (OSError, ValueError, TypeError):
        failure = ToolError(10, "internal", "Diagnostic failed; native details withheld.")
    if failure:
        evidence = dict(error_category=failure.category, raw_exit_code=failure.raw_exit_code)
        if failure.failure_layer is not None:
            evidence["failure_layer"] = failure.failure_layer
        if active != "provenance":
            check(active, "blocked" if failure.code == 3 else "fail", str(failure), **evidence)
        value, code = error_result(failure), failure.code
    else:
        passed = args.profile == "inspect" or (args.profile == "control" and args.connect)
        if not passed:
            check("requested_profile", "blocked", "Requested profile has prerequisites that these checks have not verified.")
        value = result("pass" if passed else "blocked",
                       error_category=None if passed else "unverified_prerequisites")
        code = 0 if passed else 3
    value.update(profile=args.profile, checks=checks, credential_environment=credential, account=session,
                 observed_at=observed_at,
                 verified_scope=[item["name"] for item in checks
                                 if item["status"] == "pass"
                                 and item["name"] not in {"credential_environment", "cli_version", "cli_updates"}],
                 control_environment={"tool": "lody4dot-doctor", "os": platform.system(),
                                      "architecture": platform.machine(),
                                      "script_path": str(Path(__file__).resolve()),
                                      "cli_path": str(cli) if cli is not None else None},
                 provenance=provenance)
    return value, code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", default=DEFAULT_PREFIX)
    parser.add_argument("--profile", choices=("inspect", "control", "task", "worker"), default="inspect")
    parser.add_argument("--connect", action="store_true", help="Explicitly perform a read-only workspace query.")
    parser.add_argument("--check-updates", action="store_true", help="Best-effort npm latest-version query (up to 5 seconds); warnings never block execution or upgrade the CLI.")
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
