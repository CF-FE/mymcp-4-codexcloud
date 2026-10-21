"""Offline handoff structure checks; all identifiers below are fictional fixtures."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[2] / "plugin/lody4dot/scripts/handoff.py"
SPEC = importlib.util.spec_from_file_location("lody4dot_handoff", SCRIPT)
handoff = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(handoff)


def ref(kind, identity=None, system="lody"):
    return {"system": system, "kind": kind, "id": identity or "fixture-" + kind}


def record():
    return {
        "schema_version": 1,
        "correlation_ref": ref("correlation", system="lody4dot"),
        "objective": "Produce a deterministic result from fictional test input.",
        "authorization_scope": "Only the fictional fixture task is authorized.",
        "coordinator_ref": None,
        "control_host_ref": None,
        "executor_ref": ref("machine"),
        "lody_refs": {name: ref(name) for name in (
            "workspace", "machine", "agent_config", "session", "user_turn", "assistant_turn")},
        "input_artifacts": [],
        "expected_outputs": ["A deterministic test result"],
        "versions": {"plugin": "0.1.4", "cli": "0.107.2", "source_commit": None, "environment": None},
        "observations": [{
            "source": "persisted", "freshness": "synced", "status": "completed",
            "observed_at": "2026-10-21T08:00:00+08:00", "evidence_origin": "agent_record",
            "session_ref": ref("session"), "user_turn_ref": ref("user_turn"),
            "assistant_turn_ref": ref("assistant_turn"),
        }],
        "result_artifacts": [{
            "location": "/fictional-executor/result.json", "executor_ref": ref("machine"),
            "sha256": "a" * 64, "byte_length": 20,
            "access_method": "agent_readback", "evidence_origin": "agent_record",
        }],
        "unresolved": [],
    }


class HandoffTests(unittest.TestCase):
    def capture(self, raw, *arguments):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "record.json"
            path.write_text(raw if isinstance(raw, str) else json.dumps(raw), encoding="utf-8")
            before = path.read_bytes()
            output, errors = io.StringIO(), io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                code = handoff.main(["--input", str(path), "--json", *arguments])
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(sorted(p.name for p in Path(folder).iterdir()), ["record.json"])
            return code, json.loads(output.getvalue()), errors.getvalue()

    def test_complete_result_only_passes_declared_structure(self):
        code, value, errors = self.capture(record(), "--stage", "result")
        self.assertEqual(code, 0)
        self.assertEqual(value["status"], "pass")
        self.assertEqual(value["validation_scope"], "structure_and_declared_consistency")
        self.assertIn("business_outcome", value["not_verified"])
        self.assertIn("service_acl", value["not_verified"])
        self.assertIn("artifact_contents", value["not_verified"])
        self.assertEqual(value["credential_scan"], "known_patterns_only")
        self.assertEqual(value["findings"], [])
        self.assertEqual(errors, "")

    def test_intent_does_not_require_future_native_ids(self):
        value = record()
        value["lody_refs"] = {name: None for name in value["lody_refs"]}
        value["versions"] = {name: None for name in value["versions"]}
        value["observations"], value["result_artifacts"] = [], []
        self.assertEqual(self.capture(value, "--stage", "intent")[0], 0)
        code, report, _ = self.capture(value, "--stage", "dispatched")
        self.assertEqual(code, 3)
        self.assertEqual(report["status"], "blocked")
        self.assertIn("$.lody_refs.session", [f["path"] for f in report["findings"]])

    def test_unknown_objective_or_scope_is_a_gap_not_verified(self):
        for field in ("objective", "authorization_scope"):
            with self.subTest(field=field):
                value = record(); value[field] = None
                code, report, _ = self.capture(value)
                self.assertEqual(code, 3)
                self.assertIn("$." + field, [f["path"] for f in report["findings"]])

    def test_wrong_turn_type_and_identical_turn_ids_are_errors(self):
        for mutation in ("wrong_type", "same_id", "wrong_system"):
            with self.subTest(mutation=mutation):
                value = record()
                if mutation == "wrong_type":
                    value["lody_refs"]["assistant_turn"] = ref("user_turn")
                elif mutation == "same_id":
                    value["lody_refs"]["assistant_turn"]["id"] = value["lody_refs"]["user_turn"]["id"]
                else:
                    value["lody_refs"]["session"]["system"] = "chatgpt"
                code, _, _ = self.capture(value, "--stage", "dispatched")
                self.assertEqual(code, 2)

    def test_wrong_observation_cannot_validate_result_association(self):
        value = record()
        value["observations"][0]["assistant_turn_ref"]["id"] = "fixture-other-turn"
        code, report, _ = self.capture(value, "--stage", "result")
        self.assertEqual(code, 2)
        self.assertIn("reference_mismatch", [f["code"] for f in report["findings"]])

    def test_metadata_stale_unknown_or_running_is_not_result_evidence(self):
        for field, content in (("source", "metadata"), ("freshness", "stale"),
                               ("freshness", "unknown"), ("status", "running"),
                               ("observed_at", None)):
            with self.subTest(field=field, content=content):
                value = record(); value["observations"][0][field] = content
                code, _, _ = self.capture(value, "--stage", "result")
                self.assertEqual(code, 3)

    def test_failed_or_canceled_record_can_be_structurally_complete(self):
        for outcome in ("failed", "canceled"):
            with self.subTest(outcome=outcome):
                value = record(); value["observations"][0]["status"] = outcome
                value["result_artifacts"] = []
                self.assertEqual(self.capture(value, "--stage", "result")[0], 0)

    def test_latest_declared_observation_must_support_result(self):
        value = record()
        later = deepcopy(value["observations"][0])
        later.update(observed_at="2026-10-21T08:00:01+08:00", status="running")
        value["observations"].append(later)
        self.assertEqual(self.capture(value, "--stage", "result")[0], 3)

    def test_conflicting_simultaneous_outcomes_are_not_consistent(self):
        value = record()
        other = deepcopy(value["observations"][0]); other["status"] = "failed"
        value["observations"].append(other)
        self.assertEqual(self.capture(value, "--stage", "result")[0], 2)

    def test_wrong_json_types_are_bad_input_not_internal_failure(self):
        for name in ("source", "freshness", "status"):
            for wrong in ([], {}, True, 42):
                with self.subTest(name=name, wrong=wrong):
                    value = record(); value["observations"][0][name] = wrong
                    self.assertEqual(self.capture(value, "--stage", "result")[0], 2)

    def test_timestamp_requires_timezone_and_valid_calendar_date(self):
        for timestamp in ("not-a-time", "2026-10-21T08:00:00", "2026-02-30T08:00:00Z"):
            with self.subTest(timestamp=timestamp):
                value = record(); value["observations"][0]["observed_at"] = timestamp
                self.assertEqual(self.capture(value, "--stage", "result")[0], 2)
        value = record(); value["observations"][0]["observed_at"] = "2026-10-21T00:00:00Z"
        self.assertEqual(self.capture(value, "--stage", "result")[0], 0)

    def test_artifact_needs_executor_and_valid_digest_but_is_never_opened(self):
        for field, content, expected in (("executor_ref", None, 3), ("sha256", None, 3),
                                         ("sha256", "not-a-digest", 2), ("byte_length", True, 2),
                                         ("access_method", None, 3)):
            with self.subTest(field=field):
                value = record(); value["result_artifacts"][0][field] = content
                self.assertEqual(self.capture(value, "--stage", "result")[0], expected)
        value = record(); value["result_artifacts"][0]["location"] = "https://unopened.invalid/result"
        with patch.object(socket, "socket", side_effect=AssertionError("network attempted")), \
             patch.object(subprocess, "Popen", side_effect=AssertionError("process attempted")):
            self.assertEqual(self.capture(value, "--stage", "result")[0], 0)

    def test_artifact_cannot_claim_a_different_declared_executor(self):
        value = record(); value["result_artifacts"][0]["executor_ref"]["id"] = "fixture-other-machine"
        self.assertEqual(self.capture(value, "--stage", "result")[0], 2)

    def test_result_artifact_must_agree_with_known_native_executor(self):
        for executor in (None, ref("runtime", "fixture-runtime", "codex")):
            with self.subTest(executor=executor):
                value = record(); value["executor_ref"] = executor
                value["result_artifacts"][0]["executor_ref"]["id"] = "fixture-other-machine"
                self.assertEqual(self.capture(value, "--stage", "result")[0], 2)

    def test_native_machine_and_same_namespace_executor_must_agree(self):
        value = record(); value["lody_refs"]["machine"]["id"] = "fixture-another-machine"
        self.assertEqual(self.capture(value, "--stage", "dispatched")[0], 2)

    def test_dispatched_or_result_needs_one_executor_location_reference(self):
        for stage in ("dispatched", "result"):
            value = record()
            value["lody_refs"]["machine"], value["executor_ref"] = None, None
            value["observations"][0]["status"] = "canceled"
            value["result_artifacts"] = []
            self.assertEqual(self.capture(value, "--stage", stage)[0], 3)

    def test_different_reference_namespaces_do_not_prove_identity_mapping(self):
        value = record()
        value["executor_ref"] = ref("runtime", "fixture-runtime", "codex")
        code, report, _ = self.capture(value, "--stage", "result")
        self.assertEqual(code, 0)
        self.assertIn("executor_identity_mapping", report["not_verified"])

    def test_input_artifact_can_belong_to_another_executor(self):
        value = record()
        item = deepcopy(value["result_artifacts"][0])
        item["executor_ref"] = ref("runtime", "fixture-control-host", "codex")
        item["location"] = "/fictional-control-host/input.json"
        value["input_artifacts"] = [item]
        self.assertEqual(self.capture(value, "--stage", "result")[0], 0)

    def test_duplicate_keys_nan_nonobject_and_bool_version_are_rejected(self):
        for raw in ('{"schema_version":1,"schema_version":1}', '{"schema_version":NaN}',
                    '{"schema_version":Infinity}', '[]', 'null', '{broken',
                    json.dumps({**record(), "schema_version": True})):
            with self.subTest(raw=raw[:35]):
                code, _, errors = self.capture(raw)
                self.assertEqual(code, 2)
                self.assertEqual(errors, "")

    def test_unknown_keys_and_sensitive_values_never_reach_output(self):
        hidden = "fictional-private-marker"
        samples = []
        value = record(); value[hidden] = hidden; samples.append(value)
        value = record(); value["versions"][hidden] = hidden; samples.append(value)
        value = record(); value["objective"] = "LODY_CLI_TOKEN=" + hidden; samples.append(value)
        value = record(); value["authorization_scope"] = {"access_token": hidden}; samples.append(value)
        for value in samples:
            with self.subTest(value=value):
                code, report, errors = self.capture(value)
                self.assertEqual(code, 2)
                self.assertNotIn(hidden, json.dumps(report) + errors)

    def test_public_report_does_not_echo_business_values_or_ids(self):
        value = record(); value["objective"] = "fictional confidential objective"
        value["lody_refs"]["session"]["id"] = "fictional-private-session"
        code, report, errors = self.capture(value, "--stage", "result")
        self.assertEqual(code, 2)  # Observation points at the original fictional session.
        text = json.dumps(report) + errors
        self.assertNotIn(value["objective"], text)
        self.assertNotIn(value["lody_refs"]["session"]["id"], text)

    def test_depth_and_size_limits_fail_without_recursion_output(self):
        raw = "[" * 80 + "0" + "]" * 80
        self.assertEqual(self.capture(raw)[0], 2)
        with patch.object(handoff, "MAX_BYTES", 100):
            code, _, _ = self.capture(record())
        self.assertEqual(code, 2)

    def test_unknown_fields_inside_refs_report_only_known_parent_path(self):
        value = record(); value["lody_refs"]["session"]["fictional-secret-key"] = "private"
        code, report, _ = self.capture(value)
        self.assertEqual(code, 2)
        self.assertNotIn("fictional-secret-key", json.dumps(report))

    def test_invalid_cli_choices_and_paths_are_sanitized(self):
        for args in (["--stage", "fictional-private-stage"],
                     ["--input", "/fictional-private-path"],
                     ["--fictional-private-option"]):
            output, errors = io.StringIO(), io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                code = handoff.main([*args, "--json"])
            self.assertEqual(code, 2)
            self.assertNotIn("fictional-private", output.getvalue() + errors.getvalue())

    def test_input_must_be_a_regular_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "real.json"; path.write_text(json.dumps(record()))
            link = Path(folder) / "link.json"; link.symlink_to(path)
            output = io.StringIO()
            with redirect_stdout(output):
                code = handoff.main(["--input", str(link), "--json"])
            self.assertEqual(code, 2)

    def test_named_pipe_is_rejected_without_blocking(self):
        with tempfile.TemporaryDirectory() as folder:
            pipe = Path(folder) / "record.pipe"
            os.mkfifo(pipe)
            result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(pipe), "--json"],
                                    capture_output=True, text=True, timeout=2)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_text_report_is_also_sanitized(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "record.json"; path.write_text('{"private-value":"do-not-echo"}')
            output = io.StringIO()
            with redirect_stdout(output):
                code = handoff.main(["--input", str(path)])
            self.assertEqual(code, 2)
            self.assertNotIn("private-value", output.getvalue())
            self.assertNotIn("do-not-echo", output.getvalue())


if __name__ == "__main__":
    unittest.main()
