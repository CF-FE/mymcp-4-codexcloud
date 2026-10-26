#!/usr/bin/env python3
"""Prepare Lody latest or inspect owned dependencies; never restore identity or tasks."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

from common import DEFAULT_PREFIX, ToolError, emit, error_result, result, run_native

SCRIPTS = Path(__file__).resolve().parent


def run_tool(name, prefix, state, timeout):
    arguments = [sys.executable, SCRIPTS / (name + ".py"), "--prefix", prefix, "--json"]
    if name == "doctor":
        # Let inspect's Node and CLI probes time out and clean their own process
        # groups before the outer bootstrap watchdog terminates the doctor.
        arguments += ["--profile", "inspect", "--timeout", str(min(30, timeout / 4))]
    # Only the two owned tools above are reachable. Their inspect/install paths
    # never authenticate; preserve presence observations, not caller login state.
    code, stdout, _ = run_native(arguments, data_dir=state, timeout=timeout, keep_token=True)
    try:
        value = json.loads(stdout)
        if (not isinstance(value, dict) or type(value.get("schema_version")) is not int
                or value["schema_version"] != 1
                or value.get("status") not in {"pass", "blocked", "fail"}
                or (code == 0) != (value["status"] == "pass")
                or code not in {0, 2, 3, 4, 5, 10}):
            raise ValueError("Unexpected owned-tool result")
    except (ValueError, TypeError) as exc:
        raise ToolError(4, "invalid_response", "Owned tool returned an invalid response; details withheld.", code) from exc
    return code, value


def bootstrap(args):
    steps = []
    inspection = None
    requested = "prepare" if args.prepare else "repair_missing" if args.repair_missing else "inspect"
    try:
        with tempfile.TemporaryDirectory(prefix="lody4dot-bootstrap-") as state:
            def run(name):
                code, value = run_tool(name, args.prefix, state, args.timeout)
                steps.append({"tool": name, "exit_code": code, "status": value["status"],
                              "error_category": value.get("error_category")})
                return code, value

            if args.prepare:
                code, value = run("install")
                if code:
                    return report(value, requested, steps, inspection), code
            code, inspection = run("doctor")
            if (args.repair_missing and code == 3
                    and inspection.get("error_category") == "missing_runtime"
                    and not any(item.get("name") == "provenance" and item.get("status") == "fail"
                                for item in inspection.get("checks", []))):
                code, value = run("install")
                if code:
                    return report(value, requested, steps, inspection), code
                code, inspection = run("doctor")
            return report(inspection, requested, steps, inspection), code
    except ToolError as exc:
        return report(error_result(exc), requested, steps, inspection), exc.code


def report(outcome, requested, steps, inspection):
    warnings = [
        {"code": item["name"], "status": "warn", "message": item["message"]}
        for item in (inspection or {}).get("checks", [])
        if item.get("name") in {"runtime", "cli_version", "cli_updates", "provenance"} and item.get("status") == "warn"
    ]
    return result(outcome["status"], requested_action=requested,
                  error_category=outcome.get("error_category"),
                  raw_exit_code=outcome.get("raw_exit_code"), steps=steps,
                  inspection=inspection, warnings=warnings, authentication="not_run", daemon="not_run",
                  task_recovery="not_run", verification_scope="owned_dependency_readiness")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", default=DEFAULT_PREFIX)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--prepare", action="store_true", help="Resolve and install official Lody latest, then inspect.")
    actions.add_argument("--repair-missing", action="store_true", help="Inspect first; resolve latest only for a missing managed runtime.")
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not 0 < args.timeout <= 1800:
        parser.error("--timeout must be >0 and <=1800")
    try:
        value, code = bootstrap(args)
    except (OSError, ValueError, TypeError):
        value, code = result("fail", error_category="internal",
                             message="Dependency bootstrap failed; details withheld."), 10
    emit(value, args.json)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
