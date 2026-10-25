"""Optional knowledge baseline cannot follow untrusted lock metadata."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[2] / "plugin/lody4dot/scripts"
sys.path.insert(0, str(SCRIPTS))
import common


class LockBaselineTests(unittest.TestCase):
    def test_linked_lock_is_not_read_as_a_knowledge_baseline(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "scripts").mkdir()
            (root / "runtime").mkdir()
            source = root / "scripts/common.py"
            source.write_text("# fixture\n")
            outside = root / "outside.json"
            outside.write_text('{"packages":{"node_modules/lody":{"version":"9.9.9"}}}')
            (root / "runtime/package-lock.json").symlink_to(outside)
            with patch.object(common, "__file__", str(source)):
                self.assertIsNone(common._lock_baseline())

    def test_deep_lock_does_not_abort_module_consumers(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "scripts").mkdir()
            (root / "runtime").mkdir()
            source = root / "scripts/common.py"
            source.write_text("# fixture\n")
            (root / "runtime/package-lock.json").write_text("[" * 10000 + "0" + "]" * 10000)
            with patch.object(common, "__file__", str(source)):
                self.assertIsNone(common._lock_baseline())


if __name__ == "__main__":
    unittest.main()
