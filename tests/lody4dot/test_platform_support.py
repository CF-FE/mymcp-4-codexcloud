"""Platform boundary behavior without claiming native Windows or Darwin support."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[2] / "plugin/lody4dot/scripts"
sys.path.insert(0, str(SCRIPTS))
import platform_support
import common


class PlatformBoundaryTests(unittest.TestCase):
    def installer_for_platform(self, platform, prefix):
        return self.command_for_platform("install.py", platform, ["--prefix", str(prefix)])

    def command_for_platform(self, script, platform, arguments):
        # A platform lacking fcntl must reach the CLI's supported error contract.
        # Real native platform support still requires a real target-machine run.
        wrapper = """
import argparse, builtins, contextlib, datetime, hashlib, json, os, pathlib, platform, re
import runpy, shutil, subprocess, sys, tempfile
scripts, script, target_platform, *arguments = sys.argv[1:]
sys.path.insert(0, scripts)
platform.uname()
original_import = builtins.__import__
def without_posix_lock(name, *args, **kwargs):
    if name == 'fcntl':
        raise ImportError('fixture: no POSIX lock module')
    return original_import(name, *args, **kwargs)
builtins.__import__ = without_posix_lock
sys.platform = target_platform
os.environ['LODY_CLI_TOKEN'] = 'fixture-private-credential'
for name in ('getuid', 'killpg'):
    if hasattr(os, name):
        delattr(os, name)
sys.argv = [scripts + '/' + script, *arguments, '--json']
runpy.run_path(scripts + '/' + script, run_name='__main__')
"""
        return subprocess.run(
            [sys.executable, "-c", wrapper, str(SCRIPTS), script, platform, *arguments],
            capture_output=True, text=True, timeout=10,
        )

    def test_unsupported_platform_returns_json_without_posix_import_or_writes(self):
        for platform in ("win32", "darwin"):
            with self.subTest(platform=platform), tempfile.TemporaryDirectory() as temporary:
                prefix = Path(temporary) / "existing"
                prefix.mkdir()
                sentinel = prefix / "user-file"
                sentinel.write_text("keep")
                outcome = self.installer_for_platform(platform, prefix)
                self.assertEqual(outcome.returncode, 5, outcome.stderr)
                report = json.loads(outcome.stdout)
                self.assertEqual(report["schema_version"], 1)
                self.assertEqual(report["status"], "fail")
                self.assertEqual(report["error_category"], "unsupported")
                self.assertNotIn("Traceback", outcome.stderr)
                self.assertEqual(list(prefix.iterdir()), [sentinel])
                self.assertEqual(sentinel.read_text(), "keep")

    def test_diagnostic_and_auth_commands_reject_unsupported_platform_without_identity_writes(self):
        for platform in ("win32", "darwin"):
            for script, mode in (("doctor.py", []), ("auth.py", ["--verify-only"]),
                                 ("auth.py", ["--login"])):
                with self.subTest(platform=platform, script=script, mode=mode), \
                     tempfile.TemporaryDirectory() as temporary:
                    prefix = Path(temporary) / "runtime"
                    state = Path(temporary) / "new-identity"
                    outcome = self.command_for_platform(script, platform,
                        [*mode, "--prefix", str(prefix), "--data-dir", str(state)])
                    self.assertEqual(outcome.returncode, 5, outcome.stderr)
                    report = json.loads(outcome.stdout)
                    self.assertEqual(report["schema_version"], 1)
                    self.assertEqual(report["status"], "fail")
                    self.assertEqual(report["error_category"], "unsupported_platform")
                    self.assertEqual(report["message"], "Lody4dot runtime tools currently support Linux only.")
                    self.assertNotIn("Traceback", outcome.stderr)
                    self.assertNotIn("fixture-private-credential", outcome.stdout + outcome.stderr)
                    self.assertFalse(state.exists())
                    self.assertFalse(prefix.exists())

    def test_common_runtime_boundaries_reject_before_posix_state_or_process_actions(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary) / "identity"
            with patch.object(platform_support.sys, "platform", "win32"), \
                 patch.object(common.subprocess, "Popen", side_effect=AssertionError("Must not launch")), \
                 patch.object(common.tempfile, "TemporaryDirectory", side_effect=AssertionError("Must not create state")):
                for operation, call in (
                    ("state_directory", lambda: common.state_directory(str(state), create=True)),
                    ("run_native", lambda: common.run_native(["unused"], data_dir=state)),
                    ("offline_version", lambda: common.offline_version(Path("/unused"), 1)),
                ):
                    with self.subTest(operation=operation):
                        with self.assertRaises(common.ToolError) as error:
                            call()
                        self.assertEqual(error.exception.code, 5)
                        self.assertEqual(error.exception.category, "unsupported_platform")
                self.assertFalse(state.exists())

    @unittest.skipUnless(sys.platform == "linux", "Real lock behavior requires Linux")
    def test_install_lock_is_nonblocking_and_released_with_its_stream(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "install.lock"
            with path.open("a") as owner:
                platform_support.acquire_install_lock(owner)
                with path.open("a") as contender:
                    with self.assertRaises(BlockingIOError):
                        platform_support.acquire_install_lock(contender)
            with path.open("a") as successor:
                platform_support.acquire_install_lock(successor)


if __name__ == "__main__":
    unittest.main()
