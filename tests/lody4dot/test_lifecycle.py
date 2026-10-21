"""Bootstrap recovery outcomes, using isolated subprocesses without an account."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[2] / "plugin/lody4dot/scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("lody4dot_bootstrap", SCRIPTS / "bootstrap.py")
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)

DOCTOR = '''import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--prefix');p.add_argument('--profile');p.add_argument('--timeout',type=float);p.add_argument('--json',action='store_true');a=p.parse_args()
ready=(Path(a.prefix)/'ready').exists()
print(json.dumps({'schema_version':1,'status':'pass' if ready else 'blocked','error_category':None if ready else 'missing_runtime','account':'not_run'}))
raise SystemExit(0 if ready else 3)
'''
INSTALL = '''import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--prefix');p.add_argument('--json',action='store_true');a=p.parse_args()
root=Path(a.prefix);root.mkdir(exist_ok=True);(root/'ready').write_text('owned runtime')
with (root/'install-count').open('a') as stream: stream.write('installed\\n')
print(json.dumps({'schema_version':1,'status':'pass','authentication':'not_run','daemon':'not_run'}))
'''


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tools = self.root / "scripts"
        self.tools.mkdir()
        self.prefix = self.root / "runtime"
        (self.tools / "doctor.py").write_text(DOCTOR)
        (self.tools / "install.py").write_text(INSTALL)

    def run_bootstrap(self, *arguments):
        output = io.StringIO()
        with patch.object(bootstrap, "SCRIPTS", self.tools), redirect_stdout(output):
            code = bootstrap.main(["--prefix", str(self.prefix), "--json", *arguments])
        return code, json.loads(output.getvalue())

    def test_default_only_checks_and_does_not_install_missing_runtime(self):
        code, report = self.run_bootstrap()
        self.assertEqual(code, 3)
        self.assertEqual(report["status"], "blocked")
        self.assertFalse(self.prefix.exists())
        self.assertEqual([p["tool"] for p in report["steps"]], ["doctor"])

    def test_repair_missing_restores_once_and_next_start_only_checks(self):
        code, report = self.run_bootstrap("--repair-missing")
        self.assertEqual(code, 0)
        self.assertEqual([p["tool"] for p in report["steps"]], ["doctor", "install", "doctor"])
        code, report = self.run_bootstrap("--repair-missing")
        self.assertEqual(code, 0)
        self.assertEqual([p["tool"] for p in report["steps"]], ["doctor"])
        self.assertEqual((self.prefix / "install-count").read_text().splitlines(), ["installed"])
        self.assertEqual(report["authentication"], "not_run")
        self.assertEqual(report["daemon"], "not_run")

    def test_prepare_runs_managed_install_and_then_inspect(self):
        code, report = self.run_bootstrap("--prepare")
        self.assertEqual(code, 0)
        self.assertEqual([p["tool"] for p in report["steps"]], ["install", "doctor"])
        self.assertEqual(report["inspection"]["account"], "not_run")

    def test_version_failure_is_not_treated_as_missing_installation(self):
        (self.tools / "doctor.py").write_text(
            "import json; print(json.dumps({'schema_version':1,'status':'fail','error_category':'unsupported_version'})); raise SystemExit(5)"
        )
        code, report = self.run_bootstrap("--repair-missing")
        self.assertEqual(code, 5)
        self.assertEqual(report["error_category"], "unsupported_version")
        self.assertFalse(self.prefix.exists())

    def test_failed_install_preserves_caller_files_and_stops_before_inspect(self):
        self.prefix.mkdir()
        (self.prefix / "user-data").write_text("keep")
        (self.tools / "install.py").write_text(
            "import json; print(json.dumps({'schema_version':1,'status':'fail','error_category':'prerequisite'})); raise SystemExit(3)"
        )
        code, report = self.run_bootstrap("--prepare")
        self.assertEqual(code, 3)
        self.assertEqual([p["tool"] for p in report["steps"]], ["install"])
        self.assertEqual((self.prefix / "user-data").read_text(), "keep")

    def test_invalid_child_response_does_not_echo_details(self):
        secret = "fixture-sensitive-value-never-forward"
        (self.tools / "doctor.py").write_text(f"print({secret!r})")
        code, report = self.run_bootstrap()
        self.assertEqual(code, 4)
        self.assertEqual(report["error_category"], "invalid_response")
        self.assertNotIn(secret, json.dumps(report))

    def test_caller_identity_directory_is_preserved(self):
        state = self.root / "caller-state"
        state.mkdir()
        (state / "owned-by-user").write_text("preserve")
        with patch.dict("os.environ", {"LODY_DATA_DIR": str(state)}):
            self.run_bootstrap("--repair-missing")
        self.assertEqual(list(p.name for p in state.iterdir()), ["owned-by-user"])
        self.assertEqual((state / "owned-by-user").read_text(), "preserve")


if __name__ == "__main__":
    unittest.main()
