"""Managed CLI commands keep the interpreter validated by their installation."""
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
import common
import doctor


class ManagedNodeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        # This fixture models the supported Linux runtime independently of host OS.
        platform = patch.object(doctor.sys, "platform", "linux")
        platform.start()
        self.addCleanup(platform.stop)
        self.prefix = self.root / "runtime"
        lock = b'{"lockfileVersion":3}\n'
        digest = hashlib.sha256(lock).hexdigest()
        self.runtime = self.prefix / "versions" / digest
        self.cli = self.runtime / "node_modules/lody/dist/index.js"
        self.cli.parent.mkdir(parents=True)
        self.cli.write_text("// fixture: interpreter selection only\n")
        (self.prefix / ".lody4dot-managed.json").write_text('{"schema_version":1,"owner":"lody4dot"}')
        (self.prefix / "current").symlink_to(Path("versions") / digest)
        (self.runtime / "package-lock.json").write_bytes(lock)
        self.node = self.root / "managed-node"
        self.node.write_text("#!" + sys.executable + "\nimport sys\n"
                             "print('v24.22.1' if len(sys.argv)==2 else '0.108.1')\n")
        self.node.chmod(0o755)
        self.receipt = {"schema_version": 1, "lock_sha256": digest,
                        "lody_version": "0.108.1", "node_path": str(self.node)}
        self.write_receipt()

    def write_receipt(self):
        (self.runtime / "receipt.json").write_text(json.dumps(self.receipt))

    def test_cli_probe_uses_receipt_interpreter_instead_of_platform_path(self):
        code, output, _ = common.run_native(["node", self.cli, "--version"], data_dir=self.root)
        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), "0.108.1")

    def test_offline_doctor_reports_the_managed_node_without_path_node(self):
        output = io.StringIO()
        with patch.object(doctor.shutil, "which", return_value=None), redirect_stdout(output):
            code = doctor.main(["--prefix", str(self.prefix), "--json"])
        report = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        node = next(item for item in report["checks"] if item["name"] == "node")
        self.assertEqual(node["evidence"]["version"], "v24.22.1")
        self.assertEqual(report["account"], "not_run")

    def test_relative_receipt_interpreter_is_rejected_without_execution(self):
        self.receipt["node_path"] = "../fixture-sensitive-node"
        self.write_receipt()
        with self.assertRaises(common.ToolError) as failure:
            common.run_native(["node", self.cli, "--version"], data_dir=self.root)
        self.assertNotIn("fixture-sensitive", str(failure.exception))

    def test_missing_new_receipt_interpreter_does_not_fall_back_to_path(self):
        self.node.unlink()
        with self.assertRaises(common.ToolError) as failure:
            common.run_native(["node", self.cli, "--version"], data_dir=self.root)
        self.assertEqual(failure.exception.category, "missing_executable")

    def test_legacy_receipt_without_interpreter_retains_path_compatibility(self):
        self.receipt.pop("node_path")
        self.write_receipt()
        self.assertEqual(common.node_for_cli(self.cli), "node")


if __name__ == "__main__":
    unittest.main()
