"""Independent organization-skill distribution, without Lody runtime inputs."""
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile


SCRIPT = Path(__file__).resolve().parents[2] / "plugin/lody4dot/scripts/build.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("organization_skill_build", SCRIPT)
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)

RECEIPT = ".organization-collaboration-build.json"
TOOL = "organization-collaboration-build"


class OrganizationSkillBuildTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.repo = self.root / "repo"
        self.skill = self.repo / "skill/organization-collaboration"
        self.output = self.root / "organization"
        self.archive = self.root / "organization.zip"
        self.write(self.skill / "SKILL.md", "# Organization\n[Context](references/context.md)\n")
        self.write(self.skill / "references/context.md", "# Context\n[Entry](../SKILL.md)\n")

    @staticmethod
    def write(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def run_cli(self, *arguments, output=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(builder, "__file__", str(self.repo / "plugin/lody4dot/scripts/build.py")), \
             redirect_stdout(stdout), redirect_stderr(stderr):
            code = builder.main(["--organization-skill-only", "--output", str(output or self.output),
                                 "--json", *map(str, arguments)])
        return code, json.loads(stdout.getvalue())

    def test_standalone_archive_contains_only_skill_and_its_own_receipt(self):
        self.write(self.skill / "references/new-position.md", "# Future position\n")
        # No Lody skill, plugin manifest, role library, or runtime exists in this repo.
        with patch.object(builder, "build", side_effect=AssertionError("Lody builder was invoked")):
            code, result = self.run_cli("--zip", self.archive)
        self.assertEqual(code, 0)
        self.assertEqual(result["artifact_type"], "organization_skill")
        self.assertEqual(result["skill"], "organization-collaboration")
        self.assertNotIn("manifest_sha256", result)
        expected = {"SKILL.md", "references/context.md", "references/new-position.md", RECEIPT}
        self.assertEqual(set(builder.inventory(self.output)), expected)
        with zipfile.ZipFile(self.archive) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(set(archive.namelist()), expected)
            receipt = json.loads(archive.read(RECEIPT))
            self.assertEqual(receipt["tool"], TOOL)
            self.assertEqual(receipt["skill"], "organization-collaboration")
            for name, digest in receipt["files"].items():
                self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), digest)
        self.assertEqual(result["receipt_sha256"], hashlib.sha256((self.output / RECEIPT).read_bytes()).hexdigest())
        self.assertEqual(result["archive"]["sha256"], hashlib.sha256(self.archive.read_bytes()).hexdigest())
        builder.check_references(self.output)

    def test_standalone_default_directory_is_separate_from_lody_default(self):
        previous = Path.cwd()
        stdout = io.StringIO()
        try:
            os.chdir(self.root)
            with patch.object(builder, "__file__", str(self.repo / "plugin/lody4dot/scripts/build.py")), \
                 redirect_stdout(stdout):
                code = builder.main(["--organization-skill-only", "--json"])
        finally:
            os.chdir(previous)
        self.assertEqual(code, 0)
        self.assertEqual(Path(json.loads(stdout.getvalue())["output"]), self.root / "dist/organization-collaboration")
        self.assertFalse((self.root / "dist/lody4dot").exists())

    def test_existing_directory_file_and_symlinks_are_preserved(self):
        for kind in ("empty", "directory", "file", "symlink", "dangling"):
            with self.subTest(kind=kind):
                output = self.root / kind
                if kind == "empty":
                    output.mkdir()
                elif kind == "directory":
                    self.write(output / "user-file", "preserve")
                elif kind == "file":
                    output.write_text("preserve")
                else:
                    output.symlink_to(self.skill if kind == "symlink" else self.root / "missing")
                code, result = self.run_cli("--zip", self.archive, output=output)
                self.assertEqual(code, 3)
                self.assertEqual(result["status"], "fail")
                self.assertFalse(self.archive.exists())
                self.assertTrue(output.exists() or output.is_symlink())
                if kind == "directory":
                    self.assertEqual((output / "user-file").read_text(), "preserve")
                elif kind == "file":
                    self.assertEqual(output.read_text(), "preserve")
                elif kind in {"symlink", "dangling"}:
                    self.assertTrue(output.is_symlink())

    def test_existing_archive_is_refused_before_directory_build(self):
        self.archive.write_bytes(b"preserve")
        code, result = self.run_cli("--zip", self.archive)
        self.assertEqual(code, 3)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.archive.read_bytes(), b"preserve")

    def test_output_and_archive_cannot_be_inside_source(self):
        for relative in ("skill/organization-collaboration/output", "skill/lody4dot/output", "plugin/lody4dot/output"):
            with self.subTest(relative=relative):
                code, _ = self.run_cli(output=self.repo / relative)
                self.assertEqual(code, 3)
                self.assertFalse((self.repo / relative).exists())
        code, _ = self.run_cli("--zip", self.skill / "output.zip")
        self.assertEqual(code, 3)
        self.assertFalse(self.output.exists())

    def test_bad_source_members_are_rejected_before_output(self):
        for relative in ("references/deep/position.md", "references/context.json", "scripts/run.py",
                         "references/secret.md", "references/.env"):
            with self.subTest(relative=relative):
                path = self.skill / relative
                self.write(path, "unwanted")
                try:
                    code, _ = self.run_cli("--zip", self.archive)
                    self.assertEqual(code, 3)
                    self.assertFalse(self.output.exists())
                    self.assertFalse(self.archive.exists())
                finally:
                    path.unlink()

    def test_missing_entry_and_external_reference_are_rejected(self):
        entry = self.skill / "SKILL.md"
        content = entry.read_text()
        entry.unlink()
        code, _ = self.run_cli()
        self.assertEqual(code, 3)
        self.assertFalse(self.output.exists())
        entry.write_text(content + "[Outside](../../lody4dot/SKILL.md)\n")
        code, _ = self.run_cli()
        self.assertEqual(code, 3)
        self.assertFalse(self.output.exists())

    def test_symlinked_reference_is_rejected_without_reading_target(self):
        secret = self.root / "private"
        secret.write_text("outside fixture")
        (self.skill / "references/link.md").symlink_to(secret)
        code, _ = self.run_cli()
        self.assertEqual(code, 3)
        self.assertFalse(self.output.exists())

    def test_non_utf8_document_fails_without_publishing_partial_output(self):
        (self.skill / "references/context.md").write_bytes(b"\xff")
        code, result = self.run_cli("--zip", self.archive)
        self.assertEqual(code, 3)
        self.assertEqual(result["error_category"], "build_input")
        self.assertFalse(self.output.exists())
        self.assertFalse(self.archive.exists())
        self.assertEqual(list(self.root.glob(".organization-skill-build-*")), [])

    def test_archive_failure_keeps_successful_directory_explicit(self):
        with patch.object(builder, "create_archive", side_effect=builder.BuildError("injected archive failure")):
            code, result = self.run_cli("--zip", self.archive)
        self.assertEqual(code, 3)
        self.assertEqual(result["failure_stage"], "archive")
        self.assertTrue(result["output_applied"])
        self.assertTrue((self.output / RECEIPT).is_file())
        self.assertFalse(self.archive.exists())

    def test_changed_standalone_content_is_not_archived(self):
        code, _ = self.run_cli()
        self.assertEqual(code, 0)
        (self.output / "SKILL.md").write_text("changed")
        with self.assertRaises(builder.BuildError):
            builder.create_archive(self.output, self.archive, receipt_name=RECEIPT, tool=TOOL)
        self.assertFalse(self.archive.exists())

    def test_new_output_race_does_not_replace_other_writer(self):
        original = builder.check_references

        def introduce_output(root):
            original(root)
            self.output.mkdir()
            (self.output / "other-writer").write_text("preserve")

        with patch.object(builder, "check_references", side_effect=introduce_output):
            code, _ = self.run_cli()
        self.assertEqual(code, 3)
        self.assertEqual((self.output / "other-writer").read_text(), "preserve")
        self.assertEqual(list(self.output.iterdir()), [self.output / "other-writer"])

    def test_failed_directory_commit_removes_only_its_empty_reservation(self):
        with patch.object(builder.os, "replace", side_effect=OSError("injected commit failure")):
            code, _ = self.run_cli()
        self.assertEqual(code, 3)
        self.assertFalse(self.output.exists())
        self.assertTrue((self.skill / "SKILL.md").is_file())
        self.assertEqual(list(self.root.glob(".organization-skill-build-*")), [])


if __name__ == "__main__":
    unittest.main()
