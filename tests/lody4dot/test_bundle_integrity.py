"""Offline regression coverage for packaged provenance and diagnostic outcomes."""

import argparse
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "plugin/lody4dot/scripts"
sys.path.insert(0, str(SCRIPTS))
import common
import doctor

SPEC = importlib.util.spec_from_file_location("lody4dot_integrity_build", SCRIPTS / "build.py")
build_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_module)


class BundleIntegrityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="lody4dot-integrity-", dir="/tmp")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        linux = patch.object(sys, "platform", "linux")
        linux.start()
        self.addCleanup(linux.stop)

    @staticmethod
    def write(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")

    def bundle_fixture(self, name="bundle", *, receipt=True, extra=None):
        bundle = self.root / name
        files = {
            ".codex-plugin/plugin.json": json.dumps({
                "name": "lody4dot", "version": "1.2.3", "skills": "./skills"}),
            "scripts/doctor.py": "# Offline diagnostic fixture\n",
            "skills/lody4dot/SKILL.md": "# Offline skill fixture\n",
        }
        files.update(extra or {})
        hashes = {}
        for relative, content in files.items():
            path = bundle / relative
            self.write(path, content)
            hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        if receipt:
            self.write(bundle / ".lody4dot-build.json", json.dumps({
                "schema_version": 1, "tool": "lody4dot-build",
                "plugin_version": "1.2.3", "files": hashes}))
        return bundle

    def managed_fixture(self):
        prefix = self.root / "runtime"
        lock = b'{"lockfileVersion":3,"packages":{}}\n'
        digest = hashlib.sha256(lock).hexdigest()
        runtime = prefix / "versions" / digest
        self.write(runtime / "node_modules/lody/dist/index.js", "// Never executed\n")
        self.write(prefix / ".lody4dot-managed.json", json.dumps({
            "schema_version": 1, "owner": "lody4dot"}))
        (prefix / "current").symlink_to(Path("versions") / digest)
        (runtime / "package-lock.json").write_bytes(lock)
        self.write(runtime / "receipt.json", json.dumps({
            "schema_version": 1, "lock_sha256": digest,
            "lody_version": "0.108.1", "node_version": "v24.22.1",
            "platform": "linux", "native_modules": []}))
        return prefix

    @staticmethod
    def update_receipt(bundle, change):
        path = bundle / ".lody4dot-build.json"
        receipt = json.loads(path.read_text())
        change(receipt)
        path.write_text(json.dumps(receipt))

    def provenance(self, bundle):
        return common.local_provenance(self.root / "uninstalled", bundle)

    def diagnose(self, bundle, prefix, *arguments, node_available=True):
        output, errors = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, {}, clear=True), \
             patch.object(doctor, "__file__", str(bundle / "scripts/doctor.py")), \
             patch.object(doctor, "offline_version", return_value="0.108.1") as cli_probe, \
             patch.object(doctor.shutil, "which", return_value="/fixture/node" if node_available else None), \
             patch.object(doctor.subprocess, "run", return_value=argparse.Namespace(
                 returncode=0, stdout="v24.22.1")) as node_probe, \
             patch.object(doctor, "state_directory", return_value=self.root / "state") as state, \
             patch.object(doctor, "verify_account", return_value=1) as account, \
             patch.object(doctor, "verify_catalog") as catalog, \
             redirect_stdout(output), redirect_stderr(errors):
            code = doctor.main(["--prefix", str(prefix), *arguments, "--json"])
        calls = {"state": state, "account": account, "catalog": catalog,
                 "node_probe": node_probe, "cli_probe": cli_probe}
        return code, json.loads(output.getvalue()), errors.getvalue(), calls

    def test_real_build_is_consistent_and_importable_without_source_tree(self):
        bundle = self.root / "release"
        build_module.build(REPO, bundle)
        receipt = json.loads((bundle / ".lody4dot-build.json").read_text())
        manifest = json.loads((bundle / ".codex-plugin/plugin.json").read_text())
        self.assertIn("scripts/package_layout.py", receipt["files"])
        self.assertTrue(any(name.startswith("skills/lody4dot/references/roles/workspace/")
                            for name in receipt["files"]))
        self.assertTrue(any(name.startswith("skills/lody4dot/references/roles/projects/")
                            for name in receipt["files"]))
        source = self.provenance(bundle)
        self.assertEqual(source["bundle"]["status"], "consistent")
        self.assertEqual(source["bundle"]["plugin_version"], manifest["version"])
        self.assertEqual(source["bundle"]["listed_file_count"], len(receipt["files"]))
        code, value, _, _ = self.diagnose(bundle, self.managed_fixture())
        self.assertEqual(code, 0)
        self.assertEqual(value["status"], "pass")
        checks = {item["name"]: item for item in value["checks"]}
        self.assertEqual(checks["provenance"]["status"], "pass")
        self.assertIn("provenance", value["verified_scope"])
        # A fresh isolated interpreter must import the distributed helpers on its own.
        process = subprocess.run([
            sys.executable, "-I", "-B", "-c",
            "import json,sys; from pathlib import Path; "
            "root=Path(sys.argv[1]); sys.path.insert(0,str(root/'scripts')); "
            "import common; print(json.dumps(common.local_provenance(sys.argv[2],root)))",
            str(bundle), str(self.root / "uninstalled"),
        ], capture_output=True, text=True, cwd=self.root, timeout=15)
        self.assertEqual(process.returncode, 0, process.stderr)
        packaged = json.loads(process.stdout)
        self.assertEqual(packaged["bundle"], source["bundle"])

    def test_role_library_members_are_accepted_and_hashed(self):
        names = (
            "skills/lody4dot/references/roles/common.md",
            "skills/lody4dot/references/roles/index.json",
            "skills/lody4dot/references/roles/workspace/quality.md",
            "skills/lody4dot/references/roles/projects/mymcp.md",
        )
        bundle = self.bundle_fixture(extra={name: "{}\n" if name.endswith(".json") else "# Role\n"
                                           for name in names})
        for name in names:
            with self.subTest(name=name):
                self.assertTrue(common._bundle_member(name))
        self.assertEqual(self.provenance(bundle)["bundle"]["status"], "consistent")
        (bundle / names[-1]).write_text("# Changed role\n")
        result = self.provenance(bundle)["bundle"]
        self.assertEqual(result["status"], "mismatch")
        self.assertEqual(result.get("reason"), "sha256_mismatch")

    def test_illegal_members_are_rejected_before_any_member_is_opened(self):
        names = (
            "../private-fixture-material.md", "/tmp/private-fixture-material.md",
            "scripts//doctor.py", "scripts/./doctor.py", "scripts/../doctor.py",
            "scripts\\doctor.py", "scripts/private-token.py",
            "scripts/build.py", "scripts/arbitrary.py",
            "skills/lody4dot/references/roles/extra.md",
            "skills/lody4dot/references/roles/workspace/.env",
            "skills/lody4dot/references/roles/projects/credentials.md",
            "skills/lody4dot/references/roles/workspace/private.key",
            "skills/lody4dot/references/roles/other/quality.md",
            "skills/lody4dot/references/roles/projects/nested/quality.md",
        )
        original_open = Path.open
        for index, name in enumerate(names):
            with self.subTest(name=name):
                bundle = self.bundle_fixture(f"illegal-{index}")
                self.update_receipt(bundle, lambda value: value["files"].update({name: "0" * 64}))
                allowed = {bundle / ".codex-plugin/plugin.json", bundle / ".lody4dot-build.json"}

                def guarded_open(path, *args, **kwargs):
                    if path not in allowed:
                        self.fail("An illegal receipt caused a package member to be opened")
                    return original_open(path, *args, **kwargs)

                with patch.object(Path, "open", new=guarded_open):
                    source = self.provenance(bundle)
                self.assertEqual(source["bundle"]["status"], "invalid")
                self.assertEqual(source["bundle"].get("reason"), "illegal_member")
                self.assertFalse(common._bundle_member(name))
                self.assertNotIn("private-fixture-material", json.dumps(source))

    def test_malformed_receipts_have_stable_sanitized_reason(self):
        invalid = (
            "fixture-private-material", b"\xfffixture-private-material",
            "[]", "[" * 10000 + "0" + "]" * 10000,
            json.dumps({"schema_version": 1, "tool": "lody4dot-build", "plugin_version": "1.2.3",
                        "files": {".codex-plugin/plugin.json": "fixture-private-material"}}),
        )
        for index, raw in enumerate(invalid):
            with self.subTest(index=index):
                bundle = self.bundle_fixture(f"malformed-{index}")
                (bundle / ".lody4dot-build.json").write_bytes(raw if isinstance(raw, bytes) else raw.encode())
                source = self.provenance(bundle)
                self.assertEqual(source["bundle"]["status"], "invalid")
                self.assertEqual(source["bundle"].get("reason"), "invalid_receipt")
                self.assertNotIn("fixture-private-material", json.dumps(source))

    def test_missing_listed_member_has_distinct_reason(self):
        bundle = self.bundle_fixture()
        (bundle / "skills/lody4dot/SKILL.md").unlink()
        result = self.provenance(bundle)["bundle"]
        self.assertEqual(result["status"], "mismatch")
        self.assertEqual(result.get("reason"), "missing_member")

    def test_symlinked_members_are_not_opened(self):
        relative = "skills/lody4dot/references/cloud.md"
        original_open = Path.open
        for kind in ("file", "directory"):
            with self.subTest(kind=kind):
                bundle = self.bundle_fixture(kind, extra={relative: "# Reference\n"})
                external = self.root / f"external-{kind}"
                private = external / "cloud.md"
                self.write(private, "fixture-private-material")
                member = bundle / relative
                member.unlink()
                if kind == "file":
                    member.symlink_to(private)
                else:
                    member.parent.rmdir()
                    member.parent.symlink_to(external, target_is_directory=True)

                def guarded_open(path, *args, **kwargs):
                    if path.resolve() == private:
                        self.fail("Symlinked package evidence was opened")
                    return original_open(path, *args, **kwargs)

                with patch.object(Path, "open", new=guarded_open):
                    source = self.provenance(bundle)
                self.assertEqual(source["bundle"]["status"], "mismatch")
                self.assertEqual(source["bundle"].get("reason"), "unsafe_path")
                self.assertNotIn("fixture-private-material", json.dumps(source))

    def test_symlinked_receipt_is_invalid_without_opening_target(self):
        bundle = self.bundle_fixture()
        receipt = bundle / ".lody4dot-build.json"
        external = self.root / "private-receipt.json"
        receipt.rename(external)
        receipt.symlink_to(external)
        original_open = Path.open

        def guarded_open(path, *args, **kwargs):
            if path.resolve() == external:
                self.fail("Symlinked build receipt was opened")
            return original_open(path, *args, **kwargs)

        with patch.object(Path, "open", new=guarded_open):
            source = self.provenance(bundle)
        self.assertEqual(source["bundle"]["status"], "invalid")
        self.assertEqual(source["bundle"].get("reason"), "unsafe_path")

    def test_invalid_or_changed_bundle_fails_doctor_before_account_queries(self):
        prefix = self.managed_fixture()
        for kind, expected in (("malformed", "invalid"), ("illegal", "invalid"), ("changed", "mismatch")):
            for connect in (False, True):
                with self.subTest(kind=kind, connect=connect):
                    bundle = self.bundle_fixture(f"{kind}-{connect}")
                    if kind == "malformed":
                        (bundle / ".lody4dot-build.json").write_text("fixture-private-material")
                    elif kind == "illegal":
                        self.update_receipt(bundle, lambda value: value["files"].update({
                            "../fixture-private-material": "0" * 64}))
                    else:
                        (bundle / "skills/lody4dot/SKILL.md").write_text("# Changed\n")
                    arguments = ("--profile", "control", "--connect") if connect else ()
                    code, value, errors, calls = self.diagnose(bundle, prefix, *arguments)
                    self.assertNotEqual(code, 0)
                    self.assertEqual(value["status"], "fail")
                    self.assertEqual(value["error_category"], "invalid_provenance")
                    self.assertEqual(value["provenance"]["bundle"]["status"], expected)
                    checks = {item["name"]: item for item in value["checks"]}
                    self.assertEqual(checks.get("provenance", {}).get("status"), "fail")
                    self.assertNotIn("provenance", value["verified_scope"])
                    self.assertEqual(value["account"], "not_run")
                    for call in calls.values():
                        call.assert_not_called()
                    self.assertNotIn("fixture-private-material", json.dumps(value) + errors)

    def test_runtime_lock_mismatch_blocks_receipt_selected_node_before_execution(self):
        prefix = self.managed_fixture()
        bundle = self.bundle_fixture()
        runtime = (prefix / "current").resolve()
        node = self.root / "managed-node"
        self.write(node, "#!/bin/sh\nexit 99\n")
        node.chmod(0o755)
        receipt_path = runtime / "receipt.json"
        receipt = json.loads(receipt_path.read_text())
        receipt["node_path"] = str(node)
        receipt_path.write_text(json.dumps(receipt))
        (runtime / "package-lock.json").write_text('{"changed":true}\n')

        code, value, _, calls = self.diagnose(bundle, prefix, "--profile", "control", "--connect")

        self.assertNotEqual(code, 0)
        self.assertEqual(value["status"], "fail")
        self.assertEqual(value["error_category"], "invalid_provenance")
        self.assertEqual(value["provenance"]["bundle"]["status"], "consistent")
        self.assertEqual(value["provenance"]["runtime"]["status"], "mismatch")
        self.assertEqual(value["provenance"]["runtime"].get("reason"), "sha256_mismatch")
        checks = {item["name"]: item for item in value["checks"]}
        self.assertEqual(checks.get("provenance", {}).get("status"), "fail")
        self.assertNotIn("provenance", value["verified_scope"])
        self.assertEqual(value["account"], "not_run")
        for call in calls.values():
            call.assert_not_called()

    def test_missing_source_receipt_warns_and_allows_other_checks(self):
        prefix = self.managed_fixture()
        bundle = self.bundle_fixture(receipt=False)
        code, value, _, calls = self.diagnose(
            bundle, prefix, "--profile", "control", "--connect")
        self.assertEqual(code, 0)
        self.assertEqual(value["status"], "pass")
        self.assertEqual(value["provenance"]["bundle"]["status"], "not_provided")
        checks = {item["name"]: item for item in value["checks"]}
        self.assertEqual(checks.get("provenance", {}).get("status"), "warn")
        self.assertNotIn("provenance", value["verified_scope"])
        self.assertEqual(value["account"], "authenticated")
        calls["state"].assert_called_once()
        calls["account"].assert_called_once()

    def test_missing_executable_can_be_preserved_alongside_failed_provenance(self):
        prefix = self.managed_fixture()
        bundle = self.bundle_fixture()
        (bundle / "skills/lody4dot/SKILL.md").write_text("# Changed\n")
        code, value, _, calls = self.diagnose(bundle, prefix, node_available=False)
        self.assertNotEqual(code, 0)
        self.assertNotEqual(value["status"], "pass")
        self.assertEqual(value["error_category"], "missing_executable")
        self.assertEqual(value["provenance"]["bundle"]["status"], "mismatch")
        checks = {item["name"]: item for item in value["checks"]}
        self.assertEqual(checks.get("provenance", {}).get("status"), "fail")
        self.assertNotIn("provenance", value["verified_scope"])
        for call in calls.values():
            call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
