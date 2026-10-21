#!/usr/bin/env python3
"""Check a handoff record offline; never fetch references or execute Lody tasks."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
import os
from pathlib import Path
import re
import stat
import sys


MAX_BYTES = 1024 * 1024
MAX_DEPTH = 24
MAX_NODES = 10000
MAX_FINDINGS = 64
STAGES = ("intent", "dispatched", "result")
LODY_KINDS = ("workspace", "machine", "agent_config", "session", "user_turn", "assistant_turn")
ROOT_FIELDS = {"schema_version", "correlation_ref", "objective", "authorization_scope",
               "coordinator_ref", "control_host_ref", "executor_ref", "lody_refs",
               "input_artifacts", "expected_outputs", "versions", "observations",
               "result_artifacts", "unresolved"}
SECRET_KEYS = {"token", "access_token", "refresh_token", "api_key", "password", "secret",
               "credentials", "private_key", "authorization_header", "lody_cli_token"}
SECRET_VALUE = re.compile(
    r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----|"
    r"\bLODY_CLI_TOKEN[\"']?\s*[:=]\s*\S+|"
    r"\bBearer\s+[A-Za-z0-9._~+/-]{8,}|"
    r"\bgh[pousr]_[A-Za-z0-9]{25,}|\bsk-[A-Za-z0-9_-]{20,}", re.IGNORECASE)


class InputError(Exception):
    """A fixed code only: caller values and raw parser exceptions are not public."""


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise InputError("invalid_arguments")


def _bounded(payload):
    pending, count, characters = [(payload, 0)], 0, 0
    while pending:
        value, depth = pending.pop()
        count += 1
        if count > MAX_NODES or depth > MAX_DEPTH:
            raise InputError("record_too_complex")
        if isinstance(value, dict):
            for key, item in value.items():
                if not isinstance(key, str):
                    raise InputError("invalid_object_key")
                characters += len(key)
                if key.lower().replace("-", "_") in SECRET_KEYS or SECRET_VALUE.search(key):
                    raise InputError("sensitive_input")
                pending.append((item, depth + 1))
        elif isinstance(value, list):
            pending.extend((item, depth + 1) for item in value)
        elif isinstance(value, str):
            characters += len(value)
            if SECRET_VALUE.search(value):
                raise InputError("sensitive_input")
        elif isinstance(value, float) and not math.isfinite(value):
            raise InputError("nonfinite_number")
        if characters > MAX_BYTES:
            raise InputError("record_too_large")


def _pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise InputError("duplicate_key")
        value[key] = item
    return value


def _constant(value):
    raise InputError("nonfinite_number")


def read_record(filename):
    try:
        path = Path(filename)
        if path.is_symlink() or not path.is_file():
            raise InputError("invalid_input_file")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                             | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(descriptor, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise InputError("invalid_input_file")
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise InputError("record_too_large")
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_constant)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise InputError("invalid_input") from exc


class Validation:
    def __init__(self, stage):
        self.stage, self.findings, self.failed, self.blocked = stage, [], False, False
        self.truncated = False

    def issue(self, path, code, *, gap=False):
        self.failed |= not gap
        self.blocked |= gap
        if len(self.findings) < MAX_FINDINGS:
            self.findings.append({"path": path, "code": code, "status": "blocked" if gap else "fail"})
        else:
            self.truncated = True

    def text(self, value, path, *, required=False):
        if value is None:
            if required:
                self.issue(path, "missing_required", gap=True)
            return None
        if not isinstance(value, str):
            self.issue(path, "invalid_text")
            return None
        if not value.strip():
            self.issue(path, "missing_required", gap=True)
            return None
        return value

    def obj(self, value, path, fields):
        if value is None:
            return {}
        if not isinstance(value, dict):
            self.issue(path, "invalid_object")
            return {}
        if value.keys() - fields:
            # An unknown key itself may contain a secret. Report its known parent only.
            self.issue(path, "unexpected_field")
        return value

    def array(self, value, path):
        if value is None:
            return []
        if not isinstance(value, list):
            self.issue(path, "invalid_array")
            return []
        return value

    def reference(self, value, path, kinds, *, required=False, lody=False):
        if value is None:
            if required:
                self.issue(path, "missing_required", gap=True)
            return None
        item = self.obj(value, path, {"system", "kind", "id"})
        system = self.text(item.get("system"), path + ".system", required=True)
        kind = self.text(item.get("kind"), path + ".kind", required=True)
        identity = self.text(item.get("id"), path + ".id", required=True)
        if kind is not None and kind not in kinds:
            self.issue(path + ".kind", "reference_type_mismatch")
        if lody and system is not None and system != "lody":
            self.issue(path + ".system", "reference_system_mismatch")
        return (system, kind, identity) if system and kind and identity else None

    def artifacts(self, values, path, executors):
        items = self.array(values, path)
        for index, value in enumerate(items):
            location = f"{path}[{index}]"
            item = self.obj(value, location, {"location", "executor_ref", "sha256", "byte_length",
                                              "access_method", "evidence_origin"})
            for name in ("location", "access_method", "evidence_origin"):
                self.text(item.get(name), location + "." + name, required=True)
            owner = self.reference(item.get("executor_ref"), location + ".executor_ref",
                                   {"machine", "runtime"}, required=True)
            if owner and any(executor and executor[:2] == owner[:2] and executor[2] != owner[2]
                             for executor in executors):
                self.issue(location + ".executor_ref", "reference_mismatch")
            digest = self.text(item.get("sha256"), location + ".sha256", required=True)
            if digest and not re.fullmatch(r"[a-fA-F0-9]{64}", digest):
                self.issue(location + ".sha256", "invalid_digest")
            size = item.get("byte_length")
            if size is None:
                self.issue(location + ".byte_length", "missing_required", gap=True)
            elif type(size) is not int or size < 0:
                self.issue(location + ".byte_length", "invalid_byte_length")
        return items

    def observations(self, values, refs):
        items = self.array(values, "$.observations")
        candidates = []
        for index, value in enumerate(items):
            path = f"$.observations[{index}]"
            item = self.obj(value, path, {"source", "freshness", "status", "observed_at", "evidence_origin",
                                        "session_ref", "user_turn_ref", "assistant_turn_ref"})
            source = self.text(item.get("source"), path + ".source", required=True)
            freshness = self.text(item.get("freshness"), path + ".freshness", required=True)
            status = self.text(item.get("status"), path + ".status", required=True)
            self.text(item.get("evidence_origin"), path + ".evidence_origin", required=True)
            timestamp = self.text(item.get("observed_at"), path + ".observed_at", required=True)
            parsed = None
            if timestamp:
                try:
                    parsed = datetime.fromisoformat(timestamp[:-1] + "+00:00" if timestamp.endswith("Z") else timestamp)
                    if parsed.utcoffset() is None:
                        raise ValueError("timezone required")
                except ValueError:
                    self.issue(path + ".observed_at", "invalid_timestamp")
                    parsed = None
            matched = True
            for kind in ("session", "user_turn", "assistant_turn"):
                observed = self.reference(item.get(kind + "_ref"), path + "." + kind + "_ref", {kind},
                                          required=self.stage == "result", lody=True)
                if observed and refs.get(kind) and observed != refs[kind]:
                    self.issue(path + "." + kind + "_ref", "reference_mismatch")
                    matched = False
                matched &= bool(observed and refs.get(kind))
            if source not in {None, "persisted", "metadata", "unknown"}:
                self.issue(path + ".source", "invalid_observation_source")
            if freshness not in {None, "synced", "stale", "unknown"}:
                self.issue(path + ".freshness", "invalid_observation_freshness")
            if matched and parsed is not None:
                candidates.append((parsed, source, freshness, status))
        latest = []
        if candidates:
            observed_at = max(item[0] for item in candidates)
            latest = [item for item in candidates if item[0] == observed_at]
        outcomes = {item[3] for item in latest}
        if len(outcomes) > 1:
            self.issue("$.observations", "conflicting_result_observations")
        eligible = bool(latest and len(outcomes) == 1 and all(
            source == "persisted" and freshness == "synced" and status in {"completed", "failed", "canceled"}
            for _, source, freshness, status in latest))
        if self.stage == "result" and not eligible:
            self.issue("$.observations", "matching_persisted_result_required", gap=True)
        return outcomes if eligible else set()

    def report(self):
        return {"schema_version": 1, "status": "fail" if self.failed else "blocked" if self.blocked else "pass",
                "stage": self.stage, "validation_scope": "structure_and_declared_consistency",
                "error_category": "invalid_record" if self.failed else "missing_evidence" if self.blocked else None,
                "findings": self.findings, "findings_truncated": self.truncated,
                "not_verified": ["identity", "service_acl", "authorization", "provenance", "business_outcome",
                                 "artifact_contents", "current_freshness", "executor_identity_mapping"],
                "credential_scan": "known_patterns_only", "timestamp_check": "format_and_declared_order_only"}


def validate_record(payload, stage="intent"):
    if stage not in STAGES:
        raise InputError("invalid_arguments")
    _bounded(payload)
    check = Validation(stage)
    root = check.obj(payload, "$", ROOT_FIELDS)
    if type(root.get("schema_version")) is not int or root.get("schema_version") != 1:
        check.issue("$.schema_version", "unsupported_schema")
    for name in ("objective", "authorization_scope"):
        check.text(root.get(name), "$." + name, required=True)
    check.reference(root.get("correlation_ref"), "$.correlation_ref", {"correlation"})
    check.reference(root.get("coordinator_ref"), "$.coordinator_ref", {"agent", "conversation"})
    check.reference(root.get("control_host_ref"), "$.control_host_ref", {"host", "runtime", "connection"})
    executor = check.reference(root.get("executor_ref"), "$.executor_ref", {"machine", "runtime"})
    native = check.obj(root.get("lody_refs"), "$.lody_refs", set(LODY_KINDS))
    refs = {}
    for kind in LODY_KINDS:
        required = stage != "intent" and kind in {"workspace", "session", "user_turn"}
        required |= stage == "result" and kind == "assistant_turn"
        refs[kind] = check.reference(native.get(kind), "$.lody_refs." + kind, {kind}, required=required, lody=True)
    if stage != "intent" and not executor and not refs["machine"]:
        check.issue("$.executor_ref", "executor_location_required", gap=True)
    if executor and refs["machine"] and executor[:2] == refs["machine"][:2] and executor[2] != refs["machine"][2]:
        check.issue("$.executor_ref", "reference_mismatch")
    if refs["user_turn"] and refs["assistant_turn"] and refs["user_turn"][2] == refs["assistant_turn"][2]:
        check.issue("$.lody_refs", "inconsistent_turn_identifiers")
    versions = check.obj(root.get("versions"), "$.versions", {"plugin", "cli", "source_commit", "environment"})
    for name in ("plugin", "cli", "source_commit", "environment"):
        value = check.text(versions.get(name), "$.versions." + name, required=stage != "intent" and name in {"plugin", "cli"})
        if value and name == "source_commit" and not re.fullmatch(r"[a-fA-F0-9]{40}|[a-fA-F0-9]{64}", value):
            check.issue("$.versions.source_commit", "invalid_commit")
    check.artifacts(root.get("input_artifacts"), "$.input_artifacts", ())
    output = check.artifacts(root.get("result_artifacts"), "$.result_artifacts", (executor, refs["machine"]))
    outcomes = check.observations(root.get("observations"), refs)
    if stage == "result" and "completed" in outcomes and not output:
        check.issue("$.result_artifacts", "result_artifact_required", gap=True)
    for name in ("expected_outputs", "unresolved"):
        for index, value in enumerate(check.array(root.get(name), "$." + name)):
            check.text(value, f"$.{name}[{index}]", required=True)
    value = check.report()
    return value, 2 if check.failed else 3 if check.blocked else 0


def main(argv=None):
    arguments = sys.argv[1:] if argv is None else argv
    as_json, stage = "--json" in arguments, None
    try:
        parser = SafeParser(description=__doc__)
        parser.add_argument("--input", required=True, help="Explicit handoff JSON file; references inside are never opened.")
        parser.add_argument("--stage", choices=STAGES, default="intent", help="Required-field check level, not an execution state.")
        parser.add_argument("--json", action="store_true")
        args = parser.parse_args(arguments)
        stage = args.stage
        value, code = validate_record(read_record(args.input), stage)
    except InputError as exc:
        check = Validation(stage)
        check.issue("$", str(exc))
        value, code = check.report(), 2
        value["error_category"] = "invalid_input"
    except Exception:
        check = Validation(stage)
        check.issue("$", "internal_failure")
        value, code = check.report(), 10
        value["error_category"] = "internal"
    if as_json:
        print(json.dumps(value, ensure_ascii=False, sort_keys=True))
    else:
        print(f"{value['status']}: structure and declared consistency only; real access and results are not verified.")
        for finding in value["findings"]:
            print(f"  {finding['path']}: {finding['code']}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
