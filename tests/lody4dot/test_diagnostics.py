"""Observable diagnostic/authentication behavior; no Lody account is used."""
import argparse
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[2] / "plugin/lody4dot/scripts"
sys.path.insert(0, str(SCRIPTS))
import common
import doctor
import auth


class DiagnosticTests(unittest.TestCase):
    def capture(self, module, args):
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            code = module.main([*args, "--json"])
        return code, json.loads(output.getvalue()), errors.getvalue()

    def managed_fixture(self, root):
        prefix = root / "runtime"
        lock = b'{"lockfileVersion":3,"packages":{}}\n'
        digest = hashlib.sha256(lock).hexdigest()
        version = prefix / "versions" / digest
        cli = version / "node_modules/lody/dist/index.js"
        cli.parent.mkdir(parents=True)
        cli.write_text("// fixture CLI; never executed\n")
        (prefix / ".lody4dot-managed.json").write_text('{"schema_version":1,"owner":"lody4dot"}')
        (prefix / "current").symlink_to(Path("versions") / digest)
        (version / "package-lock.json").write_bytes(lock)
        (version / "receipt.json").write_text(json.dumps({
            "schema_version": 1, "lody_version": "0.107.2", "lock_sha256": digest,
            "node_version": "v24.19.0", "platform": "linux", "native_modules": []}))
        return prefix, version, digest

    def bundle_fixture(self, root, *, receipt=True):
        bundle = root / "bundle"
        files = {
            ".codex-plugin/plugin.json": json.dumps({"name": "lody4dot", "version": "0.1.4", "skills": "./skills"}),
            "scripts/doctor.py": "# fixture doctor\n",
            "skills/lody4dot/SKILL.md": "# fixture skill\n",
        }
        hashes = {}
        for name, content in files.items():
            path = bundle / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        if receipt:
            (bundle / ".lody4dot-build.json").write_text(json.dumps({
                "schema_version": 1, "tool": "lody4dot-build", "plugin_version": "0.1.4", "files": hashes}))
        return bundle

    def test_runtime_failure_retains_passed_checks_and_explicit_unrun_checks(self):
        with tempfile.TemporaryDirectory() as prefix, patch.dict(os.environ, {}, clear=True), \
             patch.object(doctor.shutil, "which", return_value="/node"), \
             patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(returncode=0, stdout="v24.19.0")):
            code, value, _ = self.capture(doctor, ["--prefix", prefix, "--profile", "control", "--connect"])
        self.assertEqual(code, 3)
        self.assertEqual(value["account"], "not_run")
        checks = {item["name"]: item for item in value["checks"]}
        self.assertEqual(checks["credential_environment"]["evidence"]["observation"], "missing")
        self.assertEqual(checks["node"]["status"], "pass")
        self.assertEqual(checks["runtime"]["status"], "blocked")
        self.assertEqual(checks["account"]["status"], "not_run")
        self.assertEqual(checks["workspace_catalog"]["status"], "not_run")
        self.assertEqual(checks["task_execution"]["status"], "not_run")
        self.assertEqual(value["verified_scope"], ["node"])

    def test_account_failure_retains_runtime_scope_and_never_claims_directory_success(self):
        with patch.object(doctor, "installed_cli", return_value=Path("/fixture/cli")), \
             patch.object(doctor, "offline_version", return_value="0.107.2"), \
             patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(returncode=0, stdout="v24.19.0")), \
             patch.object(doctor, "state_directory", return_value=Path("/private/state")), \
             patch.object(doctor, "verify_account", side_effect=common.ToolError(4, "network", "Account query failed.", 1)), \
             patch.object(doctor, "verify_catalog") as catalog:
            code, value, _ = self.capture(doctor, ["--profile", "control", "--connect", "--workspace", "fixture-id"])
        self.assertEqual(code, 4)
        self.assertEqual(value["schema_version"], 1)
        self.assertEqual(value["account"], "not_run")
        self.assertEqual(value["raw_exit_code"], 1)
        checks = {item["name"]: item for item in value["checks"]}
        self.assertEqual(checks["runtime"]["status"], "pass")
        self.assertEqual(checks["account"]["status"], "fail")
        self.assertEqual(checks["workspace_catalog"]["status"], "not_run")
        self.assertEqual(value["verified_scope"], ["node", "runtime"])
        catalog.assert_not_called()

    def test_observation_scope_and_location_do_not_invent_platform_identity(self):
        with patch.object(doctor, "installed_cli", return_value=Path("/fixture/cli")), \
             patch.object(doctor, "offline_version", return_value="0.107.2"), \
             patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(returncode=0, stdout="v24.19.0")), \
             patch.object(doctor, "state_directory", return_value=Path("/private/state")), \
             patch.object(doctor, "verify_account", return_value=2):
            code, value, _ = self.capture(doctor, ["--profile", "control", "--connect"])
        self.assertEqual(code, 0)
        timestamp = datetime.fromisoformat(value["observed_at"].replace("Z", "+00:00"))
        self.assertIsNotNone(timestamp.tzinfo)
        self.assertEqual(value["verified_scope"], ["node", "runtime", "account"])
        self.assertEqual(value["control_environment"]["cli_path"], "/fixture/cli")
        self.assertEqual(value["control_environment"]["tool"], "lody4dot-doctor")
        self.assertNotIn("task_ref", value["control_environment"])
        self.assertNotIn("runtime_ref", value["control_environment"])

    def test_receipts_report_plugin_and_runtime_versions_independently(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prefix, version, digest = self.managed_fixture(root)
            bundle = self.bundle_fixture(root)
            with patch.object(doctor, "__file__", str(bundle / "scripts/doctor.py")), \
                 patch.object(doctor, "offline_version", return_value="0.107.2"), \
                 patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(returncode=0, stdout="v24.19.0")):
                code, value, _ = self.capture(doctor, ["--prefix", str(prefix)])
            self.assertEqual(code, 0)
            source = value["provenance"]
            self.assertEqual(source["plugin"]["version"], "0.1.4")
            self.assertEqual(source["bundle"]["status"], "consistent")
            self.assertEqual(source["runtime"]["status"], "consistent")
            self.assertEqual(source["runtime"]["lody_version"], "0.107.2")
            self.assertEqual(source["runtime"]["lock_sha256"], digest)
            self.assertEqual(source["assurance"], "local_file_consistency_only")

    def test_source_checkout_without_build_receipt_is_not_an_installation_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prefix, _, _ = self.managed_fixture(root)
            bundle = self.bundle_fixture(root, receipt=False)
            with patch.object(doctor, "__file__", str(bundle / "scripts/doctor.py")), \
                 patch.object(doctor, "offline_version", return_value="0.107.2"), \
                 patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(returncode=0, stdout="v24.19.0")):
                code, value, _ = self.capture(doctor, ["--prefix", str(prefix)])
            self.assertEqual(code, 0)
            self.assertEqual(value["status"], "pass")
            self.assertEqual(value["provenance"]["plugin"]["version"], "0.1.4")
            self.assertEqual(value["provenance"]["bundle"]["status"], "not_provided")

    def test_source_hash_mismatch_is_reported_without_changing_legacy_cli_scope(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prefix, version, _ = self.managed_fixture(root)
            bundle = self.bundle_fixture(root)
            (version / "package-lock.json").write_text('{"changed":true}')
            (bundle / "skills/lody4dot/SKILL.md").write_text("# changed fixture\n")
            with patch.object(doctor, "__file__", str(bundle / "scripts/doctor.py")), \
                 patch.object(doctor, "offline_version", return_value="0.107.2"), \
                 patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(returncode=0, stdout="v24.19.0")):
                code, value, _ = self.capture(doctor, ["--prefix", str(prefix)])
            self.assertEqual(code, 0)
            self.assertEqual(value["verified_scope"], ["node", "runtime"])
            self.assertEqual(value["provenance"]["bundle"]["status"], "mismatch")
            self.assertEqual(value["provenance"]["runtime"]["status"], "mismatch")

    def test_invalid_provenance_cannot_read_outside_bundle_or_echo_arbitrary_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prefix, _, _ = self.managed_fixture(root)
            bundle = self.bundle_fixture(root)
            (root / "private.json").write_text("fixture-private-material")
            (bundle / ".lody4dot-build.json").write_text(json.dumps({
                "schema_version": 1, "tool": "lody4dot-build", "plugin_version": "fixture-private-material",
                "files": {"../private.json": "0" * 64}}))
            with patch.object(doctor, "__file__", str(bundle / "scripts/doctor.py")), \
                 patch.object(doctor, "offline_version", return_value="0.107.2"), \
                 patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(returncode=0, stdout="v24.19.0")):
                code, value, errors = self.capture(doctor, ["--prefix", str(prefix)])
            self.assertEqual(code, 0)
            self.assertEqual(value["provenance"]["bundle"]["status"], "invalid")
            self.assertNotIn("fixture-private-material", json.dumps(value) + errors)

    def test_proxy_connect_rejection_is_not_classified_as_object_permission(self):
        for message in ("Tunnel connection failed: 403 Forbidden fixture-secret",
                        "CONNECT 403 Forbidden fixture-secret"):
            with self.subTest(message=message):
                failure = common.native_failure(1, "", message)
                value = common.error_result(failure)
                self.assertEqual(value["error_category"], "network")
                self.assertEqual(value["failure_layer"], "proxy_transport")
                self.assertEqual(value["raw_exit_code"], 1)
                self.assertNotIn("fixture-secret", json.dumps(value))

    def test_deep_optional_receipt_does_not_replace_primary_failure_or_drop_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self.bundle_fixture(root)
            (bundle / ".lody4dot-build.json").write_text("[" * 10000 + "0" + "]" * 10000)
            with patch.object(doctor, "__file__", str(bundle / "scripts/doctor.py")), \
                 patch.object(doctor.shutil, "which", return_value=None):
                code, value, _ = self.capture(doctor, ["--prefix", str(root / "missing")])
            self.assertEqual(code, 3)
            self.assertEqual(value["error_category"], "missing_executable")
            self.assertEqual(value["provenance"]["bundle"]["status"], "invalid")
            self.assertEqual(next(item for item in value["checks"] if item["name"] == "node")["status"], "blocked")

    def test_fifo_managed_metadata_is_rejected_without_reading_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            prefix = Path(temporary)
            marker = prefix / ".lody4dot-managed.json"
            os.mkfifo(marker)
            # A regular-file guard must reject the FIFO before any blocking open.
            original_open = Path.open
            def reject_fifo_open(path, *args, **kwargs):
                if path == marker:
                    self.fail("managed FIFO was opened")
                return original_open(path, *args, **kwargs)
            with patch.object(Path, "open", reject_fifo_open), \
                 patch.object(doctor.shutil, "which", return_value=None):
                code, value, _ = self.capture(doctor, ["--prefix", str(prefix)])
            self.assertEqual(code, 3)
            self.assertEqual(value["error_category"], "missing_executable")
            self.assertEqual(value["provenance"]["runtime"]["status"], "invalid")

    def test_deep_managed_receipt_is_a_missing_runtime_not_an_uncaught_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            prefix, version, _ = self.managed_fixture(Path(temporary))
            (version / "receipt.json").write_text("[" * 10000 + "0" + "]" * 10000)
            with self.assertRaises(common.ToolError) as caught:
                common.installed_cli(prefix)
            self.assertEqual(caught.exception.category, "missing_runtime")

    def test_source_receipt_rejects_sensitive_named_members_before_reading(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self.bundle_fixture(root)
            sensitive = bundle / "skills/lody4dot/references/credentials.json"
            sensitive.parent.mkdir(parents=True)
            sensitive.write_text("fixture-private-material")
            receipt_path = bundle / ".lody4dot-build.json"
            receipt = json.loads(receipt_path.read_text())
            receipt["files"]["skills/lody4dot/references/credentials.json"] = hashlib.sha256(sensitive.read_bytes()).hexdigest()
            receipt_path.write_text(json.dumps(receipt))
            original_open = Path.open
            def reject_sensitive_open(path, *args, **kwargs):
                if path == sensitive:
                    self.fail("sensitive package member was opened")
                return original_open(path, *args, **kwargs)
            with patch.object(Path, "open", reject_sensitive_open):
                source = common.local_provenance(root / "missing", bundle)
            self.assertEqual(source["bundle"]["status"], "invalid")

    def test_missing_runtime_is_not_authentication_success(self):
        with tempfile.TemporaryDirectory() as prefix, patch.dict(os.environ, {}, clear=True), \
             patch.object(doctor.shutil, "which", return_value="/node"), \
             patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(returncode=0, stdout="v24.19.0")):
            code, value, _ = self.capture(doctor, ["--prefix", prefix])
        self.assertEqual(code, 3)
        self.assertEqual(value["status"], "blocked")
        self.assertEqual(value["error_category"], "missing_runtime")

    def test_default_does_not_query_account_or_touch_state(self):
        with patch.object(doctor, "installed_cli", return_value=Path("/fixture/cli")), \
             patch.object(doctor, "offline_version", return_value="0.107.2"), \
             patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(returncode=0, stdout="v24.19.0")), \
             patch.object(doctor, "state_directory") as state, patch.object(doctor, "verify_account") as query:
            code, value, _ = self.capture(doctor, [])
        self.assertEqual(code, 0)
        self.assertEqual(value["account"], "not_run")
        state.assert_not_called()
        query.assert_not_called()

    def test_control_and_task_do_not_infer_success_from_installed_cli(self):
        for profile in ("control", "task", "worker"):
            with self.subTest(profile=profile), patch.object(doctor, "installed_cli", return_value=Path("/fixture/cli")), \
                 patch.object(doctor, "offline_version", return_value="0.107.2"), \
                 patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(returncode=0, stdout="v24.19.0")):
                code, value, _ = self.capture(doctor, ["--profile", profile])
                self.assertEqual(code, 3)
                self.assertEqual(value["status"], "blocked")

    def test_only_explicit_connection_can_pass_control(self):
        with patch.object(doctor, "installed_cli", return_value=Path("/fixture/cli")), \
             patch.object(doctor, "offline_version", return_value="0.107.2"), \
             patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(returncode=0, stdout="v24.19.0")), \
             patch.object(doctor, "state_directory", return_value=Path("/private/state")), \
             patch.object(doctor, "verify_account", return_value=2) as query, \
             patch.object(doctor, "verify_catalog") as catalog:
            code, value, _ = self.capture(doctor, ["--profile", "control", "--connect"])
        self.assertEqual(code, 0)
        self.assertEqual(value["account"], "authenticated")
        self.assertEqual(next(c for c in value["checks"] if c["name"] == "workspace_catalog")["status"], "not_run")
        query.assert_called_once()
        catalog.assert_not_called()

    def test_catalog_query_uses_exact_selector_and_all_pages_as_separate_arguments(self):
        selector = "workspace with spaces $(not-a-shell-command)"
        payload = {"items": [{"id": "machine-1", "name": "test machine"}], "hasMore": False}
        with patch.object(common, "run_native", return_value=(0, json.dumps(payload), "")) as native:
            count = common.verify_catalog(Path("/cli"), Path("/state"), selector, 2)
        self.assertEqual(count, 1)
        self.assertEqual(native.call_args.args[0],
                         ["node", Path("/cli"), "machine", "list", "--workspace", selector, "--all-pages", "--json"])
        self.assertEqual(native.call_args.kwargs, {"data_dir": Path("/state"), "timeout": 2})

    def test_catalog_empty_result_is_valid_only_with_complete_pagination(self):
        with patch.object(common, "run_native", return_value=(0, '{"items":[],"hasMore":false}', "")):
            self.assertEqual(common.verify_catalog(Path("/cli"), Path("/state"), "workspace", 2), 0)
        for stdout in ("", "not json", "null", "[]", "{}",
                       '{"items":[],"hasMore":true}',
                       '{"items":[],"hasMore":false,"nextCursor":"another-page"}',
                       '{"items":[{}],"hasMore":false}',
                       '{"items":[],"hasMore":false,"ok":false}'):
            with self.subTest(stdout=stdout), patch.object(common, "run_native", return_value=(0, stdout, "")):
                with self.assertRaises(common.ToolError) as caught:
                    common.verify_catalog(Path("/cli"), Path("/state"), "workspace", 2)
                self.assertEqual(caught.exception.code, 4)
                self.assertEqual(caught.exception.category, "invalid_response")

    def test_native_json_accepts_only_known_stream_diagnostics_around_one_record(self):
        payload = {"ok": True, "workspaceId": "workspace-1", "items": [
            {"id": "machine-1", "name": "test machine"}], "machines": [
            {"id": "machine-1", "name": "test machine"}], "hasMore": False}
        record = json.dumps(payload, separators=(",", ":"))
        attached = "[workspace-1] Remote Streams transport attached"
        detached = "[workspace-1] Remote Streams transport detached"
        for stdout in (f"{attached}\n{record}\n{detached}\n",
                       f"{record}\n{attached}\n{detached}\n",
                       f"{attached}\n{detached}\n{record}\n"):
            with self.subTest(stdout=stdout), \
                 patch.object(common, "run_native", return_value=(0, stdout, "")), \
                 redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(common.verify_catalog(Path("/cli"), Path("/state"), "workspace-1", 2), 1)
                self.assertNotIn("workspace-1", errors.getvalue())
                self.assertNotIn("test machine", errors.getvalue())

    def test_native_json_rejects_unknown_or_mismatched_diagnostics_and_multiple_records(self):
        payload = {"workspaceId": "workspace-1", "items": [], "hasMore": False}
        record = json.dumps(payload, separators=(",", ":"))
        attached = "[workspace-1] Remote Streams transport attached"
        invalid = (
            f"unknown log fixture-secret\n{record}\n",
            f"[different-workspace] Remote Streams transport attached\n{record}\n",
            f"{attached}\n{record}\n{record}\n",
            f"{attached}\n{record}\n[]\n",
            f"{attached}\n{{\"workspaceId\":\"workspace-1\",\"items\":[]\n",
            f"{attached}\n{json.dumps({'items': [], 'hasMore': False})}\n",
            f"{attached}\n{json.dumps({'workspaceId': '', 'items': [], 'hasMore': False})}\n",
            f" {attached}\n{record}\n",
            f"\x1e{record}\x1e",
            f"\x1e\n{record}\n",
        )
        for stdout in invalid:
            with self.subTest(stdout=stdout), patch.object(common, "run_native", return_value=(0, stdout, "")), \
                 redirect_stderr(io.StringIO()) as errors:
                with self.assertRaises(common.ToolError) as caught:
                    common.verify_catalog(Path("/cli"), Path("/state"), "workspace-1", 2)
                self.assertEqual(caught.exception.category, "invalid_response")
                self.assertNotIn("fixture-secret", str(caught.exception) + errors.getvalue())

    def test_account_query_uses_the_same_strict_native_json_boundary(self):
        payload = {"ok": True, "workspaceId": "workspace-1", "workspaces": [
            {"id": "workspace-1", "name": "test workspace"}]}
        stdout = "[workspace-1] Remote Streams transport attached\n" + json.dumps(payload) + "\n"
        with patch.object(common, "run_native", return_value=(0, stdout, "")), redirect_stderr(io.StringIO()):
            self.assertEqual(common.verify_account(Path("/cli"), Path("/state"), 2), 1)

    def test_catalog_failure_retains_authenticated_account_without_passing_control(self):
        for profile in ("control", "inspect"):
            with self.subTest(profile=profile), \
                 patch.object(doctor, "installed_cli", return_value=Path("/fixture/cli")), \
                 patch.object(doctor, "offline_version", return_value="0.107.2"), \
                 patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(returncode=0, stdout="v24.19.0")), \
                 patch.object(doctor, "state_directory", return_value=Path("/private/state")), \
                 patch.object(doctor, "verify_account", return_value=2), \
                 patch.object(doctor, "verify_catalog", side_effect=common.ToolError(4, "network", "Catalog connection failed.", 1)):
                code, value, _ = self.capture(doctor, ["--profile", profile, "--connect", "--workspace", "chosen-id"])
            self.assertEqual(code, 4)
            self.assertEqual(value["status"], "fail")
            self.assertEqual(value["account"], "authenticated")
            self.assertEqual(value["error_category"], "network")
            self.assertEqual(value["raw_exit_code"], 1)
            checks = {check["name"]: check for check in value["checks"]}
            self.assertEqual(checks["account"]["status"], "pass")
            self.assertEqual(checks["workspace_catalog"]["status"], "fail")
            self.assertNotIn("machine_count", checks["workspace_catalog"]["evidence"])

    def test_catalog_success_passes_control_but_not_task_execution(self):
        for profile, expected_code in (("control", 0), ("task", 3), ("worker", 3)):
            with self.subTest(profile=profile), \
                 patch.object(doctor, "installed_cli", return_value=Path("/fixture/cli")), \
                 patch.object(doctor, "offline_version", return_value="0.107.2"), \
                 patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(returncode=0, stdout="v24.19.0")), \
                 patch.object(doctor, "state_directory", return_value=Path("/private/state")), \
                 patch.object(doctor, "verify_account", return_value=2), \
                 patch.object(doctor, "verify_catalog", return_value=3) as catalog:
                code, value, _ = self.capture(doctor, ["--profile", profile, "--connect", "--workspace", "chosen-id"])
            self.assertEqual(code, expected_code)
            checks = {check["name"]: check for check in value["checks"]}
            self.assertEqual(checks["workspace_catalog"]["status"], "pass")
            self.assertEqual(checks["workspace_catalog"]["evidence"], {"machine_count": 3, "has_more": False, "all_pages": True})
            self.assertEqual(checks["task_execution"]["status"], "not_run")
            catalog.assert_called_once_with(Path("/fixture/cli"), Path("/private/state"), "chosen-id", 30)

    def test_workspace_without_explicit_connect_is_argument_error_before_queries(self):
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(doctor, "verify_account") as query, patch.object(doctor, "verify_catalog") as catalog, \
             redirect_stdout(output), redirect_stderr(errors):
            with self.assertRaises(SystemExit) as caught:
                doctor.main(["--workspace", "chosen-id", "--json"])
        self.assertEqual(caught.exception.code, 2)
        query.assert_not_called()
        catalog.assert_not_called()
        self.assertEqual(output.getvalue(), "")

    def test_bad_json_empty_response_and_wrong_schema_are_external_failure(self):
        for stdout in ("", "not json", "{}", '{"ok":false,"workspaces":[]}', '{"ok":true,"workspaces":[{}]}'):
            with self.subTest(stdout=stdout), patch.object(common, "run_native", return_value=(0, stdout, "")):
                with self.assertRaises(common.ToolError) as caught:
                    common.verify_account(Path("/cli"), Path("/state"), 1)
                self.assertEqual(caught.exception.code, 4)
                self.assertEqual(caught.exception.category, "invalid_response")

    def test_query_error_categories_do_not_echo_native_response(self):
        for text, category in (("permission denied secret-value", "permission"),
                               ("fetch failed secret-value", "network"),
                               ("CLI token is invalid or expired secret-value", "authentication")):
            with self.subTest(category=category), patch.object(common, "run_native", return_value=(1, "", text)):
                with self.assertRaises(common.ToolError) as caught:
                    common.verify_account(Path("/cli"), Path("/state"), 1)
                self.assertEqual(caught.exception.category, category)
                self.assertNotIn("secret-value", str(caught.exception))
                self.assertEqual(caught.exception.raw_exit_code, 1)

    def test_native_timeout_terminates_and_does_not_expose_output(self):
        with tempfile.TemporaryDirectory() as state:
            with self.assertRaises(common.ToolError) as caught:
                common.run_native([sys.executable, "-c", "import time; print('secret-value', flush=True); time.sleep(10)"], data_dir=state, timeout=0.05)
        self.assertEqual(caught.exception.category, "timeout")
        self.assertNotIn("secret-value", str(caught.exception))

    def test_missing_token_never_attempts_login(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(auth, "run_native") as native:
            code, value, errors = self.capture(auth, ["--login"])
        self.assertEqual(code, 3)
        self.assertEqual(value["error_category"], "missing_credential")
        native.assert_not_called()

    def test_verify_only_does_not_login_even_if_token_is_present(self):
        with patch.dict(os.environ, {"LODY_CLI_TOKEN": "secret-value"}), \
             patch.object(auth, "installed_cli", return_value=Path("/cli")), \
             patch.object(auth, "offline_version", return_value="0.107.2"), \
             patch.object(auth, "state_directory", return_value=Path("/state")), \
             patch.object(auth, "verify_account", return_value=1), patch.object(auth, "run_native") as native:
            code, value, errors = self.capture(auth, ["--verify-only"])
        self.assertEqual(code, 0)
        self.assertEqual(value["machine_registration"], "not_requested")
        self.assertNotIn("secret-value", json.dumps(value) + errors)
        native.assert_not_called()

    def test_explicit_login_does_not_forward_echoed_credential(self):
        token = "fixture-token-with-sensitive-material"
        with patch.dict(os.environ, {"LODY_CLI_TOKEN": token}), \
             patch.object(auth, "installed_cli", return_value=Path("/cli")), \
             patch.object(auth, "offline_version", return_value="0.107.2"), \
             patch.object(auth, "state_directory", return_value=Path("/state")), \
             patch.object(auth, "run_native", return_value=(1, token, "invalid or expired " + token)) as native:
            code, value, errors = self.capture(auth, ["--login"])
        self.assertEqual(code, 4)
        self.assertNotIn(token, json.dumps(value) + errors)
        self.assertEqual(native.call_args.args[0][-2:], ["--auth", token])

    def test_login_success_does_not_infer_remote_machine_registration(self):
        token = "fixture-token-that-native-login-echoes"
        with patch.dict(os.environ, {"LODY_CLI_TOKEN": token}), \
             patch.object(auth, "installed_cli", return_value=Path("/cli")), \
             patch.object(auth, "offline_version", return_value="0.107.2"), \
             patch.object(auth, "state_directory", return_value=Path("/state")), \
             patch.object(auth, "run_native", return_value=(0, token, token)), \
             patch.object(auth, "verify_account", return_value=1):
            code, value, errors = self.capture(auth, ["--login"])
        self.assertEqual(code, 0)
        self.assertEqual(value["account"], "authenticated")
        self.assertEqual(value["machine_registration"], "not_verified")
        self.assertEqual(value["local_identity"], "written_by_login")
        self.assertNotIn(token, json.dumps(value) + errors)

    def test_state_directory_is_explicit_private_and_does_not_chmod_user_state(self):
        with tempfile.TemporaryDirectory() as base, patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(common.ToolError):
                common.state_directory(None)
            path = Path(base) / "state"
            self.assertEqual(common.state_directory(str(path), create=True), path)
            self.assertEqual(path.stat().st_mode & 0o777, 0o700)
            path.chmod(0o755)
            with self.assertRaises(common.ToolError):
                common.state_directory(str(path), create=True)
            self.assertEqual(path.stat().st_mode & 0o777, 0o755)

    def test_managed_cli_rejects_external_pointer(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory)
            (prefix / ".lody4dot-managed.json").write_text('{"schema_version":1,"owner":"lody4dot"}')
            (prefix / "current").symlink_to("/tmp")
            with self.assertRaises(common.ToolError) as caught:
                common.installed_cli(prefix)
        self.assertEqual(caught.exception.category, "missing_runtime")


if __name__ == "__main__":
    unittest.main()
