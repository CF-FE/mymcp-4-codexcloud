"""Transactional installer behavior; subprocesses are controlled fixtures."""

import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[2] / "plugin/lody4dot/scripts/install.py"
sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location("lody4dot_install", SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.prefix = self.root / "tool"
        self.runtime = self.root / "runtime"
        self.runtime.mkdir()
        manifest = {"name": "lody4dot-runtime", "version": "0.1.0", "private": True,
                    "dependencies": {"lody": "0.107.2"},
                    "overrides": {"lody": {"tinypool": "2.1.2"}}}
        lock = {"lockfileVersion": 3, "packages": {
            "": {"dependencies": manifest["dependencies"]},
            "node_modules/lody": {"version": "0.107.2"},
            "node_modules/tinypool": {"version": "2.1.2"}}}
        policy = {"schema_version": 1, "lifecycle_scripts": "disabled",
                  "reviewed_install_script_packages": [],
                  "native_modules": installer.NATIVE_MODULES}
        for name, data in (("package.json", manifest), ("package-lock.json", lock),
                           ("build-policy.json", policy)):
            (self.runtime / name).write_text(json.dumps(data))
        self.commands = []
        self.failure = None
        self.node_version = "v24.19.0"
        self.reported_version = "0.107.2"
        self.patches = [patch.object(installer, "_run", side_effect=self.run_fixture),
                        patch.object(installer.shutil, "which", side_effect=lambda name: "/usr/bin/" + name),
                        patch.object(installer.sys, "platform", "linux")]
        for mocked in self.patches:
            mocked.start()
            self.addCleanup(mocked.stop)

    def run_fixture(self, args, *, cwd=None, env=None, timeout=None):
        self.commands.append((args, cwd, env))
        if args[1:] == ["--version"] and args[0].endswith("node"):
            return subprocess.CompletedProcess(args, 0, self.node_version + "\n", "")
        if "ci" in args:
            if self.failure == "npm":
                raise installer.InstallError("npm install failed", 4, "install", 17)
            runtime = Path(cwd)
            cli = runtime / "node_modules/lody/dist/index.js"
            cli.parent.mkdir(parents=True)
            cli.write_text("// fixture CLI\n")
            return subprocess.CompletedProcess(args, 0, "installed", "")
        if args[-1] == "--version":
            if self.failure == "version_timeout":
                raise installer.InstallError("Subprocess timed out", 4, "timeout")
            if self.failure == "version_failed":
                raise installer.InstallError("Required subprocess failed; output withheld", 4,
                                             "subprocess", 7)
            if self.failure == "version_invalid":
                return subprocess.CompletedProcess(args, 0, "unexpected fixture-secret output\n", "")
            if self.failure == "version_invalid_encoding":
                raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "fixture decoding failure")
            version = "0.1.0" if self.failure == "version" else self.reported_version
            return subprocess.CompletedProcess(args, 0, version + "\n", "")
        if args[-1] == "--help":
            if self.failure == "help":
                return subprocess.CompletedProcess(args, 0, "not the expected CLI help\n", "")
            if self.failure == "help_failed":
                raise installer.InstallError("Required subprocess failed; output withheld", 4,
                                             "subprocess", 7)
            return subprocess.CompletedProcess(args, 0, "Usage: lody [options] [command]\n", "")
        if "--input-type=module" in args:
            if self.failure == "native":
                raise installer.InstallError("native module check failed", 4, "native", 1)
            return subprocess.CompletedProcess(args, 0, "native-ok\n", "")
        raise AssertionError(args)

    def perform(self):
        return installer.install(self.prefix, runtime_dir=self.runtime)

    def assert_old_install_survives(self, before):
        self.assertEqual((self.prefix / "current").readlink(), before)
        self.assertEqual((self.prefix / "state/sentinel").read_text(), "keep")
        self.assertTrue((self.prefix / "bin/lody").is_file())

    def prepare_upgrade(self):
        self.perform()
        state = self.prefix / "state"
        state.mkdir()
        (state / "sentinel").write_text("keep")
        before = (self.prefix / "current").readlink()
        lock = self.runtime / "package-lock.json"
        lock.write_text(lock.read_text() + "\n")
        return before

    def test_repeated_same_lock_reuses_validated_runtime_and_keeps_state(self):
        first = self.perform()
        (self.prefix / "state").mkdir()
        (self.prefix / "state/sentinel").write_text("keep")
        second = self.perform()
        self.assertFalse(first["reused"])
        self.assertTrue(second["reused"])
        self.assertEqual(second["warnings"], [])
        self.assertEqual(sum("ci" in command for command, _, _ in self.commands), 1)
        self.assertEqual((self.prefix / "state/sentinel").read_text(), "keep")
        self.assertIn("current", (self.prefix / "bin/lody").read_text())

    def test_unmanaged_nonempty_prefix_is_untouched(self):
        self.prefix.mkdir()
        (self.prefix / "user-file").write_text("keep")
        with self.assertRaises(installer.InstallError):
            self.perform()
        self.assertEqual((self.prefix / "user-file").read_text(), "keep")
        self.assertFalse((self.prefix / installer.MARKER).exists())

    def test_unsupported_node_does_not_create_prefix(self):
        self.node_version = "v22.13.9"
        with self.assertRaises(installer.InstallError) as error:
            self.perform()
        self.assertEqual(error.exception.exit_code, 5)
        self.assertFalse(self.prefix.exists())

    def test_unsupported_platform_precedes_runtime_input_and_does_not_create_prefix(self):
        with patch.object(installer.sys, "platform", "win32"):
            with self.assertRaises(installer.InstallError) as error:
                installer.install(self.prefix, runtime_dir=self.root / "missing-runtime")
        self.assertEqual(error.exception.exit_code, 5)
        self.assertEqual(error.exception.category, "unsupported")
        self.assertFalse(self.prefix.exists())
        self.assertEqual(self.commands, [])

    def test_npm_failure_preserves_previous_entry_and_state(self):
        before = self.prepare_upgrade()
        self.failure = "npm"
        with self.assertRaises(installer.InstallError):
            self.perform()
        self.assert_old_install_survives(before)

    def test_native_failure_preserves_previous_entry_and_state(self):
        before = self.prepare_upgrade()
        self.reported_version = "0.108.0"
        self.failure = "native"
        with self.assertRaises(installer.InstallError):
            self.perform()
        self.assert_old_install_survives(before)

    def test_version_mismatch_warns_and_activates_without_changing_state(self):
        before = self.prepare_upgrade()
        self.failure = "version"
        result = self.perform()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["lody_version"], "0.1.0")
        self.assertEqual(result["actual_lody_version"], "0.1.0")
        self.assertEqual(result["baseline_lody_version"], "0.107.2")
        warning = result["warnings"][0]
        self.assertEqual(warning["code"], "cli_version_differs_from_baseline")
        self.assertEqual(warning["status"], "warn")
        self.assertEqual(warning["baseline"], "0.107.2")
        self.assertEqual(warning["actual"], "0.1.0")
        self.assertNotEqual((self.prefix / "current").readlink(), before)
        self.assertEqual((self.prefix / "state/sentinel").read_text(), "keep")
        self.assertTrue((self.prefix / "bin/lody").is_file())
        receipt = json.loads((self.prefix / "current/receipt.json").read_text())
        self.assertEqual(receipt["lody_version"], "0.1.0")
        self.assertEqual(receipt["baseline_lody_version"], "0.107.2")

    def test_unknown_or_unavailable_version_warns_and_checks_actual_functionality(self):
        for failure in ("version_invalid", "version_invalid_encoding", "version_failed", "version_timeout"):
            with self.subTest(failure=failure):
                self.prefix = self.root / failure
                self.failure = failure
                self.commands.clear()
                result = self.perform()
                self.assertEqual(result["status"], "pass")
                self.assertIsNone(result["lody_version"])
                self.assertIsNone(result["actual_lody_version"])
                self.assertEqual(result["baseline_lody_version"], "0.107.2")
                self.assertEqual(result["warnings"][0]["code"], "cli_version_unknown")
                self.assertNotIn("fixture-secret", json.dumps(result))
                self.assertTrue(any(command[-1] == "--help" for command, _, _ in self.commands))
                self.assertTrue(any("--input-type=module" in command
                                    for command, _, _ in self.commands))
                receipt = json.loads((self.prefix / "current/receipt.json").read_text())
                self.assertIsNone(receipt["lody_version"])
                self.assertEqual(receipt["baseline_lody_version"], "0.107.2")

    def test_recorded_actual_version_does_not_block_same_lock_reuse(self):
        self.perform()
        receipt_path = self.prefix / "current/receipt.json"
        receipt = json.loads(receipt_path.read_text())
        receipt["lody_version"] = "0.108.0"
        receipt_path.write_text(json.dumps(receipt))
        (self.prefix / "state").mkdir()
        (self.prefix / "state/sentinel").write_text("keep")
        result = self.perform()
        self.assertTrue(result["reused"])
        self.assertEqual(result["lody_version"], "0.107.2")
        self.assertEqual(json.loads(receipt_path.read_text())["lody_version"], "0.107.2")
        self.assertEqual(sum("ci" in command for command, _, _ in self.commands), 1)
        self.assertEqual((self.prefix / "state/sentinel").read_text(), "keep")

    def test_failed_receipt_refresh_keeps_previous_receipt_runtime_and_state(self):
        self.perform()
        before = (self.prefix / "current").readlink()
        (self.prefix / "state").mkdir()
        (self.prefix / "state/sentinel").write_text("keep")
        receipt_path = self.prefix / "current/receipt.json"
        previous_receipt = receipt_path.read_bytes()
        self.reported_version = "0.108.0"
        write_text = Path.write_text

        def partial_receipt_write(path, data, *args, **kwargs):
            if path.parent == receipt_path.resolve().parent and "receipt" in path.name:
                write_text(path, "{", *args, **kwargs)
                raise OSError("fixture partial write")
            return write_text(path, data, *args, **kwargs)

        with patch.object(Path, "write_text", partial_receipt_write):
            with self.assertRaises(OSError):
                self.perform()
        self.assertEqual(receipt_path.read_bytes(), previous_receipt)
        self.assertEqual(list(receipt_path.resolve().parent.glob(".receipt.json-*")), [])
        self.assert_old_install_survives(before)

    def test_failed_help_remains_blocking_and_preserves_old_runtime(self):
        before = self.prepare_upgrade()
        self.reported_version = "0.108.0"
        for failure in ("help", "help_failed"):
            with self.subTest(failure=failure):
                self.failure = failure
                with self.assertRaises(installer.InstallError):
                    self.perform()
                self.assert_old_install_survives(before)

    def test_text_output_prints_version_warning(self):
        self.failure = "version"
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(installer, "RUNTIME_DIR", self.runtime), \
                patch.object(installer.sys, "stdout", stdout), \
                patch.object(installer.sys, "stderr", stderr):
            code = installer.main(["--prefix", str(self.prefix)])
        self.assertEqual(code, 0)
        self.assertIn("warn", stderr.getvalue().lower())
        self.assertIn("0.107.2", stderr.getvalue())
        self.assertIn("0.1.0", stderr.getvalue())
        self.assertIn("ready", stdout.getvalue())

    def test_json_output_reports_unknown_version_without_raw_output(self):
        self.failure = "version_invalid"
        stdout = io.StringIO()
        with patch.object(installer, "RUNTIME_DIR", self.runtime), \
                patch.object(installer.sys, "stdout", stdout):
            code = installer.main(["--prefix", str(self.prefix), "--json"])
        self.assertEqual(code, 0)
        result = json.loads(stdout.getvalue())
        self.assertEqual(result["status"], "pass")
        self.assertIsNone(result["actual_lody_version"])
        self.assertEqual(result["baseline_lody_version"], "0.107.2")
        self.assertEqual(result["warnings"][0]["status"], "warn")
        self.assertNotIn("fixture-secret", stdout.getvalue())

    def test_failure_before_switch_preserves_previous_entry(self):
        before = self.prepare_upgrade()
        replace = installer.os.replace

        def fail_switch(source, destination):
            if Path(destination) == self.prefix / "current":
                raise OSError("fixture failure")
            return replace(source, destination)

        with patch.object(installer.os, "replace", side_effect=fail_switch):
            with self.assertRaises(OSError):
                self.perform()
        self.assert_old_install_survives(before)
        self.assertFalse((self.prefix / ".current-next").exists())

    def test_symlink_parent_is_rejected_without_mutating_target(self):
        target = self.root / "target"
        target.mkdir()
        link = self.root / "link"
        link.symlink_to(target, target_is_directory=True)
        with self.assertRaises(installer.InstallError):
            installer.install(link / "tool", runtime_dir=self.runtime)
        self.assertEqual(list(target.iterdir()), [])

    def test_modified_reused_lock_is_rejected_without_reinstall(self):
        self.perform()
        current = (self.prefix / "current").readlink()
        lock = self.prefix / current / "package-lock.json"
        lock.write_text(lock.read_text() + "\n")
        with self.assertRaises(installer.InstallError):
            self.perform()
        self.assertEqual((self.prefix / "current").readlink(), current)
        self.assertEqual(sum("ci" in command for command, _, _ in self.commands), 1)

    def test_unknown_launcher_is_not_overwritten(self):
        self.perform()
        launcher = self.prefix / "bin/lody"
        launcher.write_text("user owned launcher\n")
        with self.assertRaises(installer.InstallError):
            self.perform()
        self.assertEqual(launcher.read_text(), "user owned launcher\n")

    def test_unknown_current_target_is_not_followed(self):
        self.perform()
        current = self.prefix / "current"
        current.unlink()
        current.symlink_to(self.root / "outside")
        with self.assertRaises(installer.InstallError):
            self.perform()
        self.assertEqual(current.readlink(), self.root / "outside")

    def test_lifecycle_script_in_lock_is_rejected_before_install(self):
        lock = json.loads((self.runtime / "package-lock.json").read_text())
        lock["packages"]["node_modules/lody"]["hasInstallScript"] = True
        (self.runtime / "package-lock.json").write_text(json.dumps(lock))
        with self.assertRaises(installer.InstallError):
            self.perform()
        self.assertFalse(self.prefix.exists())

    def test_version_checks_use_isolated_state_without_token(self):
        with patch.dict(installer.os.environ, {"LODY_CLI_TOKEN": "fixture-secret", "HTTPS_PROXY": "fixture-proxy"}):
            self.perform()
        checks = [(command, env) for command, _, env in self.commands if env and "LODY_DATA_DIR" in env]
        self.assertGreater(len(checks), 1)
        for _, env in checks:
            self.assertNotIn("LODY_CLI_TOKEN", env)
            self.assertEqual(env["HTTPS_PROXY"], "fixture-proxy")
            self.assertNotIn(str(self.prefix), env["LODY_DATA_DIR"])

    def test_supported_node_range(self):
        for version in ("v22.14.0", "22.99.0", "v23.6.0", "v24.19.0"):
            self.assertTrue(installer.supported_node(version), version)
        for version in ("v20.19.0", "v22.13.9", "v23.5.9", "garbage"):
            self.assertFalse(installer.supported_node(version), version)


if __name__ == "__main__":
    unittest.main()
