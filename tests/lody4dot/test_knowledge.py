"""Catch version/help drift without installing Lody or querying an account."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "skill/lody4dot/references"


class KnowledgeTests(unittest.TestCase):
    def test_index_covers_the_captured_public_tree_exactly(self):
        snapshot = json.loads((REF / "help-snapshot.json").read_text())
        index = json.loads((REF / "command-index.json").read_text())
        actual = {c["command"]: c for c in snapshot["commands"]}
        expected = {c["command"]: c for c in index["commands"]}
        self.assertEqual(len(actual), len(snapshot["commands"]))
        self.assertEqual(len(expected), len(index["commands"]))
        self.assertEqual(set(actual), set(expected))
        self.assertEqual(len(actual), 70)
        self.assertEqual(len(snapshot["roots"]), 20)
        self.assertEqual(set(snapshot["roots"]), {c.split()[0] for c in actual})
        self.assertFalse(any("__internal" in c or "daemon-runner" in c for c in actual))
        for command, item in actual.items():
            self.assertEqual(item["exit_code"], 0, command)
            self.assertEqual(hashlib.sha256(item["help"].encode()).hexdigest(), item["sha256"], command)
            self.assertEqual(expected[command]["help_sha256"], item["sha256"], command)

    def test_runtime_and_reference_versions_agree(self):
        package = json.loads((ROOT / "plugin/lody4dot/runtime/package.json").read_text())
        snapshot = json.loads((REF / "help-snapshot.json").read_text())
        index = json.loads((REF / "command-index.json").read_text())
        self.assertEqual(package["dependencies"]["lody"], snapshot["lody_version"])
        self.assertEqual(snapshot["lody_version"], index["lody_version"])
        self.assertEqual(package["overrides"], {"lody": {"tinypool": "2.1.2"}})

    def test_index_retains_effect_and_evidence_instead_of_claiming_business_tests(self):
        index = json.loads((REF / "command-index.json").read_text())
        for item in index["commands"]:
            with self.subTest(command=item["command"]):
                self.assertTrue(item["success_evidence"])
                self.assertTrue(item["sources"])
                self.assertIn(item["verification"], ("documented", "help_verified"))
                self.assertIn(item["effect"], ("read", "modify", "execute", "propose", "authenticate", "local_file", "mixed"))
                self.assertEqual(set(item["requires"]), {"authentication", "workspace", "local_runtime"})


if __name__ == "__main__":
    unittest.main()
