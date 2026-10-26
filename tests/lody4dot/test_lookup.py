"""Offline knowledge selection, role composition and relocation behavior."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[2] / "plugin/lody4dot/scripts/lookup.py"
SPEC = importlib.util.spec_from_file_location("lody4dot_lookup", SCRIPT)
lookup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lookup)


class LookupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "repo"
        self.skill = self.repo / "skill/lody4dot"
        self.references = self.skill / "references"
        self.roles = self.references / "roles"
        self.fake_script = self.repo / "plugin/lody4dot/scripts/lookup.py"
        self.fake_script.parent.mkdir(parents=True)
        self.write(self.roles / "common.md", "Common: task authorization, one writer, UNKNOWN, Save/readback.\n")
        self.write(self.roles / "workspace/review.md", "Review a precise version independently.\n")
        self.write(self.roles / "project/owner.md", "Own the project's accepted baseline and integration.\n")
        self.write(self.roles / "project/example.md", "Project example: complete source and listening evidence.\n")
        self.index = {
            "schema_version": 1, "library_version": "1.0.0",
            "common": {"resource": "common.md"},
            "projects": [{"id": "example", "name": "Example", "resource": "project/example.md"}],
            "roles": [
                {"id": "review", "name": "Reviewer", "scope": "workspace", "kind": "shared_role",
                 "summary": "Review exact artifacts", "resource": "workspace/review.md",
                 "methods": ["review-method"], "source_role_id": "old-review"},
                {"id": "owner", "name": "Project owner", "scope": "project", "kind": "project_owner",
                 "project_id": "example", "summary": "Own integration", "resource": "project/owner.md",
                 "methods": [], "source_role_id": "old-owner"},
            ],
            "methods": [{"id": "review-method", "name": "Optional review method", "relation": "optional_method",
                         "bundled": False, "source": {"repository": "https://github.com/example/methods",
                         "commit": "a" * 40, "path": "skills/review/SKILL.md",
                         "url": "https://github.com/example/methods/blob/" + "a" * 40 + "/skills/review/SKILL.md",
                         "license": "MIT"}}],
            "provenance": {"source_version": "2.2", "evidence_scope": "historical design; not deployment"},
        }
        self.save_index()
        self.entry = {"command": "session observe", "effect": "read", "verification": "help_verified",
                      "success_evidence": ["persisted exact turn"], "sources": ["historic/source"]}
        for name, extra in (
            ("command-index.json", {"verification_note": "Help coverage is not current business execution."}),
            ("help-snapshot.json", {"captured_at": "2026-10-25T06:56:46Z"}),
            ("command-audit.json", {"audited_at": "2026-10-25T07:06:33Z", "scope": "bounded_official_cli",
                                    "online_followups": [{"irrelevant_private_summary": "must-not-be-returned"}]}),
        ):
            self.write_json(self.references / name, {
                "schema_version": 1, "lody_version": "0.108.1", **extra,
                "commands": [self.entry, {"command": "session chat", "effect": "execute"}],
            })

    @staticmethod
    def write(path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_json(self, path, value):
        self.write(path, json.dumps(value, ensure_ascii=False))

    def save_index(self):
        self.write_json(self.roles / "index.json", self.index)

    def run_cli(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(lookup, "__file__", str(self.fake_script)), redirect_stdout(stdout), redirect_stderr(stderr):
            code = lookup.main(list(args))
        return code, json.loads(stdout.getvalue()), stderr.getvalue()

    def assert_rejected(self, *args):
        code, result, _ = self.run_cli(*args)
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "fail")
        self.assertNotIn("entry", result)
        self.assertNotIn("prompt", result)
        return result

    def test_exact_command_preserves_original_entry_and_snapshot_scope(self):
        for detail, field in (("index", "verification_note"), ("help", "captured_at"), ("audit", "audited_at")):
            with self.subTest(detail=detail):
                code, result, errors = self.run_cli("command", "session observe", "--detail", detail)
                self.assertEqual(code, 0)
                self.assertEqual(result["entry"], self.entry)
                self.assertEqual(result["source"]["lody_version"], "0.108.1")
                self.assertIn(field, result["source"])
                self.assertEqual(errors, "")
                self.assertNotIn("session chat", json.dumps(result))
                self.assertNotIn("must-not-be-returned", json.dumps(result))

    def test_command_default_reads_only_index_not_other_snapshots(self):
        (self.references / "command-audit.json").unlink()
        (self.references / "help-snapshot.json").unlink()
        self.assertEqual(self.run_cli("command", "session observe")[0], 0)
        self.assert_rejected("command", "session observe", "--detail", "audit")

    def test_unknown_or_duplicate_commands_fail_without_partial_data(self):
        self.assert_rejected("command", "session")
        self.write_json(self.references / "command-index.json", {
            "schema_version": 1, "lody_version": "0.108.1", "commands": [self.entry, self.entry]})
        self.assert_rejected("command", "session observe")

    def test_command_rejects_bad_json_schema_and_nonfinite_values(self):
        path = self.references / "command-index.json"
        for raw in ('{"commands": [], "commands": []}', '{"commands": NaN}', '[]',
                    '{"schema_version": true, "lody_version":"0.108.1", "commands":[]}'):
            with self.subTest(raw=raw):
                self.write(path, raw)
                self.assert_rejected("command", "session observe")

    def test_roles_list_contains_only_filtered_metadata(self):
        code, result, _ = self.run_cli("roles", "--scope", "workspace")
        self.assertEqual(code, 0)
        self.assertEqual([item["id"] for item in result["roles"]], ["review"])
        self.assertNotIn("Review a precise", json.dumps(result))
        self.assertNotIn("Common:", json.dumps(result))
        self.assertEqual(len(self.run_cli("roles", "--project", "example")[1]["roles"]), 2)
        self.assertEqual([r["id"] for r in self.run_cli("roles", "--scope", "project")[1]["roles"]], ["owner"])
        self.assert_rejected("roles", "--project", "missing")

    def test_role_metadata_exposes_optional_method_without_loading_body(self):
        code, result, _ = self.run_cli("role", "review")
        self.assertEqual(code, 0)
        self.assertFalse(result["native_payload"])
        self.assertEqual(result["role"]["id"], "review")
        self.assertNotIn("prompt", result)
        self.assertFalse(result["methods"][0]["bundled"])
        self.assertEqual(result["methods"][0]["availability"], "not_bundled")
        self.assertEqual(result["role"], self.index["roles"][0])
        self.assertEqual(result["methods"][0]["source"], self.index["methods"][0]["source"])
        self.assertEqual(result["resources"], ["common.md", "workspace/review.md"])
        self.assertNotIn("Project example:", json.dumps(result))

    def test_render_keeps_complete_prompt_and_provenance_without_repeated_lookup_metadata(self):
        code, result, _ = self.run_cli("role", "review", "--project", "example", "--render")
        self.assertEqual(code, 0)
        self.assertEqual(result["role"], {"id": "review", "name": "Reviewer", "scope": "workspace", "kind": "shared_role"})
        self.assertEqual(result["project"], {"id": "example", "name": "Example"})
        self.assertEqual(result["methods"], [{"id": "review-method", "relation": "optional_method", "availability": "not_bundled"}])
        self.assertNotIn("resources", result)
        self.assertNotIn(self.index["methods"][0]["source"]["url"], json.dumps(result))
        self.assertFalse(result["native_payload"])
        self.assertEqual(result["source"]["evidence_scope"], "definitions_not_runtime_binding_or_deployment")
        self.assertEqual(result["provenance"], self.index["provenance"])
        self.assertEqual(result["prompt"], "Common: task authorization, one writer, UNKNOWN, Save/readback.\n\n"
                         "Review a precise version independently.\n\n"
                         "Project example: complete source and listening evidence.")
        self.assertEqual(result["prompt_chars"], len(result["prompt"]))
        self.assertEqual(result["components"], [
            {"resource": resource, "sha256": hashlib.sha256((self.roles / resource).read_bytes()).hexdigest()}
            for resource in ("common.md", "workspace/review.md", "project/example.md")
        ])

    def test_render_preserves_project_role_identity(self):
        code, result, _ = self.run_cli("role", "owner", "--project", "example", "--render")
        self.assertEqual(code, 0)
        self.assertEqual(result["role"], {"id": "owner", "name": "Project owner", "scope": "project",
                                         "kind": "project_owner", "project_id": "example"})
        self.assertEqual(result["methods"], [])

    def test_role_render_composes_only_common_role_and_explicit_project(self):
        code, plain, _ = self.run_cli("role", "review", "--render")
        self.assertEqual(code, 0)
        self.assertIn("Common:", plain["prompt"])
        self.assertIn("Review a precise", plain["prompt"])
        self.assertNotIn("Project example:", plain["prompt"])
        code, project, _ = self.run_cli("role", "review", "--project", "example", "--render")
        self.assertEqual(code, 0)
        self.assertIn("Project example:", project["prompt"])
        self.assertNotIn("Own the project's", project["prompt"])
        self.assertEqual(len(project["components"]), 3)
        for component in project["components"]:
            self.assertEqual(component["sha256"], hashlib.sha256((self.roles / component["resource"]).read_bytes()).hexdigest())
        self.assertEqual(project["prompt_chars"], len(project["prompt"]))

    def test_project_roles_require_matching_explicit_project(self):
        self.assert_rejected("role", "owner")
        self.assert_rejected("role", "owner", "--project", "missing")
        self.assertEqual(self.run_cli("role", "owner", "--project", "example", "--render")[0], 0)

    def test_unknown_role_and_duplicate_ids_are_rejected(self):
        self.assert_rejected("role", "missing")
        for collection in ("roles", "projects", "methods"):
            original = deepcopy(self.index)
            self.index[collection].append(deepcopy(self.index[collection][0]))
            self.save_index()
            self.assert_rejected("check")
            self.index = original

    def test_schema_scope_kind_project_and_method_dependencies_are_checked(self):
        mutations = [
            lambda d: d.update(schema_version=True),
            lambda d: d["roles"][0].update(scope="global"),
            lambda d: d["roles"][0].update(kind="project_owner"),
            lambda d: d["roles"][1].update(project_id="missing"),
            lambda d: d["roles"][0].update(methods=["missing"]),
            lambda d: d["methods"][0].update(bundled=True),
            lambda d: d["methods"][0]["source"].update(commit="main"),
        ]
        original = deepcopy(self.index)
        for mutate in mutations:
            self.index = deepcopy(original)
            mutate(self.index)
            self.save_index()
            self.assert_rejected("check")

    def test_missing_or_escaping_resource_is_rejected(self):
        self.write(self.root / "private.md", "fictional-sensitive-content")
        for resource in ("absent.md", "../outside.md", str(self.root / "private.md")):
            self.index["roles"][0]["resource"] = resource
            self.save_index()
            result = self.assert_rejected("role", "review", "--render")
            self.assertNotIn("fictional-sensitive-content", json.dumps(result))

    def test_symlink_leaf_and_ancestor_are_rejected(self):
        self.write(self.root / "outside.md", "outside")
        link = self.roles / "linked.md"
        link.symlink_to(self.root / "outside.md")
        folder = self.roles / "linked-folder"
        folder.symlink_to(self.roles / "workspace", target_is_directory=True)
        for resource in ("linked.md", "linked-folder/review.md"):
            self.index["roles"][0]["resource"] = resource
            self.save_index()
            self.assert_rejected("check")

    def test_empty_and_oversized_complete_prompt_fail_without_truncation(self):
        for text in ("", "x" * 32768):
            self.write(self.roles / "workspace/review.md", text)
            self.assert_rejected("role", "review", "--render")
            self.assert_rejected("check")

    def test_check_includes_project_combinations_and_has_no_stdout_side_effect(self):
        output = io.StringIO()
        with redirect_stdout(output):
            summary = lookup.validate_library(self.skill)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(summary["role_count"], 2)
        self.assertEqual(summary["project_count"], 1)
        self.assertEqual(summary["render_count"], 3)
        self.write(self.roles / "project/example.md", "x" * 32700)
        self.assert_rejected("check")

    def test_operation_is_read_only_and_cannot_make_network_or_process_calls(self):
        before = {str(p.relative_to(self.repo)): p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
        with patch.object(socket, "create_connection", side_effect=AssertionError("Network attempted")), \
             patch.object(subprocess, "Popen", side_effect=AssertionError("Process attempted")):
            self.assertEqual(self.run_cli("role", "review", "--render")[0], 0)
            self.assertEqual(self.run_cli("check")[0], 0)
        after = {str(p.relative_to(self.repo)): p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_validator_exposes_only_stable_knowledge_errors_to_builder(self):
        self.index["roles"][0]["scope"] = []
        self.save_index()
        with self.assertRaises(lookup.KnowledgeError):
            lookup.validate_library(self.skill)
        with self.assertRaises(lookup.KnowledgeError) as caught:
            lookup.validate_library(self.root / "fictional-sensitive-path")
        self.assertNotIn("fictional-sensitive-path", str(caught.exception))

    def test_bundle_relocation_and_source_layout_ignore_working_directory(self):
        shutil.copy2(SCRIPT, self.fake_script)
        bundle = self.root / "bundle"
        (bundle / "scripts").mkdir(parents=True)
        shutil.copy2(SCRIPT, bundle / "scripts/lookup.py")
        shutil.copytree(self.skill, bundle / "skills/lody4dot")
        unrelated = self.root / "elsewhere"
        unrelated.mkdir()
        for script in (self.fake_script, bundle / "scripts/lookup.py"):
            result = subprocess.run([sys.executable, str(script), "role", "review", "--render"],
                                    cwd=unrelated, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Review a precise", json.loads(result.stdout)["prompt"])
            self.assertEqual(result.stderr, "")

    def test_bad_arguments_and_read_errors_are_sanitized_json(self):
        report = self.assert_rejected("command", "session observe", "--detail", "fictional-sensitive-value")
        self.assertNotIn("fictional-sensitive-value", json.dumps(report))
        with patch.object(Path, "read_bytes", side_effect=OSError("fictional-sensitive-value")):
            report = self.assert_rejected("command", "session observe")
        self.assertNotIn("fictional-sensitive-value", json.dumps(report))


if __name__ == "__main__":
    unittest.main()
