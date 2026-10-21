"""CLI version observations must never gate an authorized command."""
from contextlib import redirect_stdout
import hashlib
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
import auth
import common


class CliVersionPolicyTests(unittest.TestCase):
    def test_other_and_unknown_versions_do_not_gate_managed_entrypoint(self):
        with tempfile.TemporaryDirectory() as temporary:
            prefix = Path(temporary)
            lock = b'{"lockfileVersion":3}\n'
            digest = hashlib.sha256(lock).hexdigest()
            runtime = prefix / "versions" / digest
            cli = runtime / "node_modules/lody/dist/index.js"
            cli.parent.mkdir(parents=True)
            cli.write_text("// not executed\n")
            (prefix / ".lody4dot-managed.json").write_text('{"schema_version":1,"owner":"lody4dot"}')
            (prefix / "current").symlink_to(Path("versions") / digest)
            (runtime / "package-lock.json").write_bytes(lock)
            for observed in ("0.100.0", "2.0.0-rc.1", None):
                with self.subTest(observed=observed):
                    (runtime / "receipt.json").write_text(json.dumps({
                        "schema_version": 1, "lody_version": observed, "lock_sha256": digest}))
                    self.assertEqual(common.installed_cli(prefix), cli)
                    evidence = common.local_provenance(prefix, prefix / "absent-package")
                    self.assertEqual(evidence["runtime"]["status"], "consistent")
                    self.assertEqual(evidence["runtime"]["lody_version"], observed)

    def test_version_query_drift_and_failure_are_only_sanitized_observations(self):
        cases = [(0, "v0.108.0\n", "", "0.108.0"),
                 (1, "fixture-private-output", "fixture-private-error", None),
                 (0, "fixture-private-output", "", None)]
        for code, stdout, stderr, expected in cases:
            with self.subTest(code=code, expected=expected), \
                 patch.object(common, "run_native", return_value=(code, stdout, stderr)):
                actual = common.offline_version(Path("/fixture/cli"), 1)
                self.assertEqual(actual, expected)
                warnings = common.version_warnings(actual)
                self.assertEqual(warnings[0]["status"], "warn")
                self.assertNotIn("fixture-private", json.dumps(warnings))
        with patch.object(common, "run_native", side_effect=common.ToolError(4, "timeout", "withheld")):
            self.assertIsNone(common.offline_version(Path("/fixture/cli"), 1))

    def test_verify_only_continues_account_query_with_other_or_unknown_version(self):
        for version in ("0.100.0", "0.108.0", None):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as temporary, \
                 patch.dict(os.environ, {}, clear=True), \
                 patch.object(auth, "installed_cli", return_value=Path("/fixture/cli")), \
                 patch.object(auth, "offline_version", return_value=version), \
                 patch.object(auth, "verify_account", return_value=2) as query, \
                 patch.object(auth, "run_native") as login:
                output = io.StringIO()
                with redirect_stdout(output):
                    code = auth.main(["--verify-only", "--data-dir", temporary, "--json"])
                value = json.loads(output.getvalue())
                self.assertEqual(code, 0)
                self.assertEqual(value["account"], "authenticated")
                self.assertEqual(value["cli_version"], version)
                self.assertEqual(value["warnings"][0]["status"], "warn")
                query.assert_called_once()
                login.assert_not_called()

    def test_version_warning_does_not_replace_real_account_failure(self):
        with tempfile.TemporaryDirectory() as temporary, \
             patch.object(auth, "installed_cli", return_value=Path("/fixture/cli")), \
             patch.object(auth, "offline_version", return_value="0.100.0"), \
             patch.object(auth, "verify_account", side_effect=common.ToolError(4, "permission", "Access denied.")):
            output = io.StringIO()
            with redirect_stdout(output):
                code = auth.main(["--verify-only", "--data-dir", temporary, "--json"])
            value = json.loads(output.getvalue())
            self.assertEqual(code, 4)
            self.assertEqual(value["error_category"], "permission")


if __name__ == "__main__":
    unittest.main()
