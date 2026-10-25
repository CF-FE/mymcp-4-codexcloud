"""Catch version/help drift without installing Lody or querying an account."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "skill/lody4dot/references"


class KnowledgeTests(unittest.TestCase):
    def test_command_audit_covers_the_actual_recursively_advertised_tree(self):
        snapshot = json.loads((REF / "help-snapshot.json").read_text())
        audit = json.loads((REF / "command-audit.json").read_text())
        captured = {item["command"]: item for item in snapshot["commands"]}

        def advertised(text):
            section = text.split("Commands:\n", 1)
            if len(section) == 1:
                return []
            return [name for name in re.findall(r"^  ([\w-]+)(?:\s|$)", section[1], re.M)
                    if name not in {"help", "__internal", "daemon-runner"}]

        pending = advertised(snapshot["root_help"]["help"])
        discovered = set()
        while pending:
            command = pending.pop()
            self.assertNotIn(command, discovered)
            self.assertIn(command, captured)
            discovered.add(command)
            children = advertised(captured[command]["help"])
            self.assertEqual(children, captured[command]["children"])
            pending.extend(command + " " + child for child in children)
        business = [item for item in audit["commands"] if item["kind"] != "builtin_help"]
        self.assertEqual(discovered, set(captured))
        self.assertEqual(discovered, {item["command"] for item in business})
        expected_helpers = {"help"} | {
            command + " help" for command, item in captured.items()
            if re.search(r"^  help(?:\s|$)", item["help"], re.M)
        }
        self.assertEqual(expected_helpers, {
            item["command"] for item in audit["commands"] if item["kind"] == "builtin_help"
        })
        self.assertEqual(audit["discovery"]["audited_entry_count"], len(audit["commands"]))
        self.assertEqual(len({item["command"] for item in audit["commands"]}), len(audit["commands"]))

    def test_command_audit_keeps_help_source_and_business_evidence_separate(self):
        snapshot = json.loads((REF / "help-snapshot.json").read_text())
        audit = json.loads((REF / "command-audit.json").read_text())
        captures = {item["command"]: item for item in snapshot["commands"]}
        captures["lody"] = snapshot["root_help"]
        for item in audit["commands"]:
            with self.subTest(command=item["command"]):
                self.assertTrue({"parameters", "purpose", "identity_requirement",
                                 "workspace_requirement", "side_effects", "validation", "result"} <= item.keys())
                reference = item["parameters"]["help_snapshot"]
                self.assertEqual(reference["sha256"], captures[reference["command"]]["sha256"])
                self.assertIn("required", item["identity_requirement"])
                self.assertIn("required", item["workspace_requirement"])
                self.assertTrue(item["side_effects"]["detail"])
                self.assertFalse(item["side_effects"]["business_operation_executed"])
                self.assertEqual(item["validation"]["help_result"], "help_verified")
                self.assertEqual(item["result"]["help_exit_code"], 0)
                self.assertFalse(item["result"]["online_success"])
                self.assertIn(item["result"]["online_status"], {"not_run", "not_applicable"})
                self.assertIn(item["result"]["business_status"],
                              {"not_run", "not_applicable_group", "not_applicable_help"})

    def test_index_covers_the_captured_public_tree_exactly(self):
        snapshot = json.loads((REF / "help-snapshot.json").read_text())
        index = json.loads((REF / "command-index.json").read_text())
        actual = {c["command"]: c for c in snapshot["commands"]}
        expected = {c["command"]: c for c in index["commands"]}
        self.assertEqual(len(actual), len(snapshot["commands"]))
        self.assertEqual(len(expected), len(index["commands"]))
        self.assertEqual(set(actual), set(expected))
        self.assertEqual(set(snapshot["roots"]), {c.split()[0] for c in actual})
        self.assertTrue({"workspace", "project", "agent-config", "agent-role", "login"}
                        .issubset(snapshot["roots"]))
        self.assertFalse(any("__internal" in c or "daemon-runner" in c for c in actual))
        for command, item in actual.items():
            self.assertEqual(item["exit_code"], 0, command)
            self.assertEqual(hashlib.sha256(item["help"].encode()).hexdigest(), item["sha256"], command)
            self.assertEqual(expected[command]["help_sha256"], item["sha256"], command)
            for child in item.get("children", []):
                self.assertIn(command + " " + child, actual)

    def test_runtime_and_reference_versions_agree(self):
        package = json.loads((ROOT / "plugin/lody4dot/runtime/package.json").read_text())
        lock = json.loads((ROOT / "plugin/lody4dot/runtime/package-lock.json").read_text())
        snapshot = json.loads((REF / "help-snapshot.json").read_text())
        index = json.loads((REF / "command-index.json").read_text())
        self.assertEqual(package["dependencies"]["lody"], "latest")
        self.assertEqual(lock["packages"][""]["dependencies"], package["dependencies"])
        self.assertEqual(lock["packages"]["node_modules/lody"]["version"], snapshot["lody_version"])
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
