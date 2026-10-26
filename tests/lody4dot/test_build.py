"""Self-contained build behavior, including safe refusal and relocation."""

import hashlib
import importlib.util
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile


SCRIPT = Path(__file__).resolve().parents[2] / "plugin/lody4dot/scripts/build.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("lody4dot_build", SCRIPT)
build_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_module)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.skill = self.repo / "skill/lody4dot"
        self.setup_skill = self.repo / "skill/lody4dot-setup"
        self.plugin = self.repo / "plugin/lody4dot"
        self.output = self.root / "package"
        self.write(self.skill / "SKILL.md", "# Lody\n\n[Reference](references/cloud.md)\n")
        self.write(self.skill / "references/cloud.md", "# Cloud\n[Source](https://lody.ai/zh/docs/cli/)\n")
        self.write_json(self.skill / "references/command-index.json", {"schema_version": 1, "lody_version": "0.108.1", "commands": []})
        self.write(self.skill / "references/knowledge.md", "# Offline knowledge\n")
        self.write(self.skill / "references/roles/common.md", "Use the authorized scope and preserve unknown results.\n")
        self.write(self.skill / "references/roles/quality.md", "Review the selected artifact.\n")
        self.write_json(self.skill / "references/roles/index.json", {
            "schema_version": 1, "library_version": "1.0.0", "provenance": {},
            "common": {"resource": "common.md"}, "projects": [], "methods": [],
            "roles": [{"id": "fixture_quality", "name": "Quality", "scope": "workspace",
                       "kind": "shared_role", "summary": "Read-only review", "resource": "quality.md",
                       "methods": [], "source_role_id": "quality"}],
        })
        self.write_json(self.skill / "references/sources.json", {"resource": "help-snapshot.json"})
        self.write_json(self.skill / "references/help-snapshot.json", {"commands": []})
        self.write(self.setup_skill / "SKILL.md", "# Setup\n[Core](../lody4dot/SKILL.md)\n")
        self.write(self.plugin / "README.md", "# Plugin\n[Skill](skills/lody4dot/SKILL.md)\n")
        self.write_json(self.plugin / ".codex-plugin/plugin.json", {
            "name": "lody4dot", "version": "0.1.0", "skills": "./skills",
            "extensions": {"com.openai": {"onboardingSkill": "./skills/lody4dot-setup/SKILL.md"}},
        })
        for name in ("install.py", "doctor.py", "auth.py", "common.py",
                     "platform_support.py", "bootstrap.py", "handoff.py"):
            self.write(self.plugin / "scripts" / name, "print('fixture')\n")
        for name in ("codex-cloud.md", "codex-cli.md", "dot.md"):
            self.write(self.plugin / "hosts" / name, "# Host\n[Prepare](../scripts/bootstrap.py)\n")
        self.write(self.plugin / "scripts/build.py", "# source-only builder\n")
        self.write(self.plugin / "scripts/lookup.py", (SCRIPT.parent / "lookup.py").read_text())
        for name in ("package.json", "package-lock.json", "build-policy.json"):
            self.write_json(self.plugin / "runtime" / name, {})

    @staticmethod
    def write(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")

    def write_json(self, path, value):
        self.write(path, json.dumps(value) + "\n")

    def run_cli(self, *arguments, output=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(build_module, "__file__", str(self.plugin / "scripts/build.py")), \
             redirect_stdout(stdout), redirect_stderr(stderr):
            code = build_module.main([
                "--output", str(output or self.output), "--json", *map(str, arguments),
            ])
        return code, json.loads(stdout.getvalue())

    def test_default_cli_retains_directory_only_result(self):
        code, result = self.run_cli()
        self.assertEqual(code, 0)
        self.assertEqual(set(result), {
            "schema_version", "status", "output", "file_count", "manifest_sha256",
        })
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["file_count"] + 1, len(build_module.inventory(self.output)))
        self.assertEqual(result["manifest_sha256"],
                         hashlib.sha256((self.output / build_module.RECEIPT).read_bytes()).hexdigest())

    def test_zip_cli_contains_complete_root_bundle_and_verified_digest_summary(self):
        target = self.root / "release/lody4dot.zip"
        code, result = self.run_cli("--zip", target)
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "pass")
        files = build_module.inventory(self.output)
        with zipfile.ZipFile(target) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(len(archive.infolist()), len(files))
            self.assertEqual(set(archive.namelist()), set(files))
            self.assertIn(".agents/plugins/marketplace.json", archive.namelist())
            self.assertIn(".codex-plugin/plugin.json", archive.namelist())
            receipt = json.loads(archive.read(build_module.RECEIPT))
            for name, expected in files.items():
                self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), expected, name)
                if name != build_module.RECEIPT:
                    self.assertEqual(receipt["files"][name], expected, name)
        metadata = result["archive"]
        self.assertEqual(metadata["path"], str(target))
        self.assertEqual(metadata["file_count"], len(files))
        self.assertEqual(metadata["size_bytes"], target.stat().st_size)
        self.assertEqual(metadata["sha256"], hashlib.sha256(target.read_bytes()).hexdigest())
        self.assertEqual(metadata["receipt_sha256"], files[build_module.RECEIPT])
        self.assertTrue(metadata["verification"])

    def test_existing_or_modified_zip_is_never_replaced_or_rebuilds_directory(self):
        target = self.root / "release.zip"
        code, _ = self.run_cli("--zip", target)
        self.assertEqual(code, 0)
        previous = build_module.inventory(self.output)
        self.write(self.skill / "references/cloud.md", "# Updated source\n")
        for modified in (False, True):
            with self.subTest(modified=modified):
                if modified:
                    target.write_bytes(target.read_bytes() + b"user annotation")
                before = target.read_bytes()
                code, result = self.run_cli("--zip", target)
                self.assertEqual(code, 3)
                self.assertEqual(result["status"], "fail")
                self.assertEqual(target.read_bytes(), before)
                self.assertEqual(build_module.inventory(self.output), previous)

    def test_zip_accepts_epoch_source_timestamp_without_changing_content(self):
        skill = self.skill / "SKILL.md"
        contents = skill.read_bytes()
        os.utime(skill, (0, 0))
        target = self.root / "epoch.zip"
        code, result = self.run_cli("--zip", target)
        self.assertEqual(code, 0)
        with zipfile.ZipFile(target) as archive:
            self.assertIsNone(archive.testzip())
            name = "skills/lody4dot/SKILL.md"
            self.assertEqual(archive.read(name), contents)
            receipt = json.loads(archive.read(build_module.RECEIPT))
            self.assertEqual(receipt["files"][name], hashlib.sha256(contents).hexdigest())
        self.assertEqual(result["archive"]["sha256"], hashlib.sha256(target.read_bytes()).hexdigest())

    def test_any_existing_archive_path_is_refused_before_build(self):
        foreign = self.root / "foreign.txt"
        self.write(foreign, "keep foreign data")
        for kind in ("file", "directory", "symlink", "dangling_symlink"):
            with self.subTest(kind=kind):
                target = self.root / f"{kind}.zip"
                if kind == "file":
                    self.write(target, "not an owned zip")
                elif kind == "directory":
                    self.write(target / "user-file", "keep")
                else:
                    target.symlink_to(foreign if kind == "symlink" else self.root / "missing")
                code, result = self.run_cli("--zip", target)
                self.assertEqual(code, 3)
                self.assertEqual(result["status"], "fail")
                self.assertFalse(self.output.exists())
                self.assertEqual(foreign.read_text(), "keep foreign data")
                if kind == "directory":
                    self.assertEqual((target / "user-file").read_text(), "keep")
                    shutil.rmtree(target)
                else:
                    if kind == "file":
                        self.assertEqual(target.read_text(), "not an owned zip")
                    else:
                        self.assertTrue(target.is_symlink())
                    target.unlink()

    def test_archive_path_cannot_overlap_source_or_output(self):
        before = build_module.inventory(self.repo)
        targets = [self.output, self.output / "nested.zip",
                   self.plugin / "release.zip", self.skill / "release.zip"]
        for target in targets:
            with self.subTest(target=target):
                code, result = self.run_cli("--zip", target)
                self.assertEqual(code, 3)
                self.assertEqual(result["status"], "fail")
                self.assertFalse(target.exists())
                self.assertFalse(self.output.exists())
                self.assertEqual(build_module.inventory(self.repo), before)
        target = self.root / "ancestor.zip"
        code, _ = self.run_cli("--zip", target, output=target / "bundle")
        self.assertEqual(code, 3)
        self.assertFalse(target.exists())

    def test_late_archive_path_competitor_is_preserved_and_temporary_file_removed(self):
        target = self.root / "release.zip"
        real_link = build_module.os.link

        def competing_link(source, destination, *args, **kwargs):
            Path(destination).write_bytes(b"another writer owns this path")
            return real_link(source, destination, *args, **kwargs)

        with patch.object(build_module.os, "link", side_effect=competing_link):
            code, result = self.run_cli("--zip", target)
        self.assertEqual(code, 3)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(target.read_bytes(), b"another writer owns this path")
        self.assertEqual([], list(self.root.glob(".lody4dot-*")))
        build_module.check_owned_output(self.output)

    def test_archive_publish_failure_leaves_no_partial_zip_or_temporary_file(self):
        target = self.root / "release.zip"
        with patch.object(build_module.os, "link", side_effect=OSError("publish unavailable")):
            code, result = self.run_cli("--zip", target)
        self.assertEqual(code, 3)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(result["output_applied"])
        self.assertEqual(result["failure_stage"], "archive")
        self.assertEqual(result["output"], str(self.output))
        self.assertEqual(result["manifest_sha256"],
                         hashlib.sha256((self.output / build_module.RECEIPT).read_bytes()).hexdigest())
        self.assertFalse(target.exists())
        self.assertEqual([], list(self.root.glob(".lody4dot-*")))
        build_module.check_owned_output(self.output)

    def test_archive_content_change_with_valid_crc_fails_before_publication(self):
        real_write = zipfile.ZipFile.write
        changes = (("skills/lody4dot/SKILL.md", b"changed during archive creation"),
                   (build_module.RECEIPT, b"[]"))
        for index, (changed_name, payload) in enumerate(changes):
            with self.subTest(changed_name=changed_name):
                target = self.root / f"changed-{index}.zip"

                def changed_write(archive, filename, arcname=None, *args, **kwargs):
                    if str(arcname) == changed_name:
                        return archive.writestr(arcname, payload)
                    return real_write(archive, filename, arcname, *args, **kwargs)

                with patch.object(zipfile.ZipFile, "write", new=changed_write):
                    code, result = self.run_cli("--zip", target)
                self.assertEqual(code, 3)
                self.assertEqual(result["status"], "fail")
                self.assertFalse(target.exists())
                self.assertEqual([], list(self.root.glob(".lody4dot-*")))
                build_module.check_owned_output(self.output)

    def test_archive_parent_file_is_preserved_before_directory_build(self):
        parent = self.root / "foreign-parent"
        parent.write_bytes(b"existing parent file")
        code, result = self.run_cli("--zip", parent / "release.zip")
        self.assertEqual(code, 3)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(parent.read_bytes(), b"existing parent file")
        self.assertFalse(self.output.exists())
        self.assertEqual([], list(self.root.glob(".lody4dot-*")))

    def test_invalid_source_does_not_create_archive(self):
        target = self.root / "release.zip"
        (self.setup_skill / "SKILL.md").unlink()
        code, result = self.run_cli("--zip", target)
        self.assertEqual(code, 3)
        self.assertEqual(result["status"], "fail")
        self.assertFalse(target.exists())
        self.assertFalse(self.output.exists())

    def test_build_relocates_all_resources_and_hashes_exact_content(self):
        result = build_module.build(self.repo, self.output)
        relocated = self.root / "elsewhere/copied"
        relocated.parent.mkdir()
        shutil.move(self.output, relocated)
        build_module.check_references(relocated)
        receipt = json.loads((relocated / build_module.RECEIPT).read_text())
        actual = build_module.inventory(relocated)
        actual.pop(build_module.RECEIPT)
        self.assertEqual(actual, receipt["files"])
        self.assertEqual(result["file_count"], len(actual))
        self.assertEqual(actual["scripts/install.py"], hashlib.sha256(b"print('fixture')\n").hexdigest())
        self.assertFalse((relocated / "scripts/build.py").exists())
        self.assertTrue((relocated / "scripts/platform_support.py").is_file())
        self.assertTrue((relocated / "scripts/bootstrap.py").is_file())
        self.assertTrue((relocated / "scripts/handoff.py").is_file())
        self.assertTrue((relocated / "hosts/codex-cloud.md").is_file())
        self.assertTrue((relocated / "hosts/dot.md").is_file())
        manifest = json.loads((relocated / ".codex-plugin/plugin.json").read_text())
        setup = relocated / manifest["extensions"]["com.openai"]["onboardingSkill"]
        self.assertEqual(setup.read_text(), "# Setup\n[Core](../lody4dot/SKILL.md)\n")
        self.assertIn("skills/lody4dot-setup/SKILL.md", receipt["files"])
        marketplace = json.loads((relocated / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual(marketplace["plugins"][0]["source"], {"source": "local", "path": "."})

    def test_rebuild_owned_output_updates_and_keeps_output_complete(self):
        build_module.build(self.repo, self.output)
        self.write(self.skill / "references/cloud.md", "# Updated reference\n")
        build_module.build(self.repo, self.output)
        self.assertEqual((self.output / "skills/lody4dot/references/cloud.md").read_text(), "# Updated reference\n")
        build_module.check_owned_output(self.output)

    def test_relocated_bundle_can_render_role_from_unrelated_directory(self):
        build_module.build(self.repo, self.output)
        relocated = self.root / "relocated"
        shutil.move(self.output, relocated)
        result = subprocess.run([sys.executable, str(relocated / "scripts/lookup.py"),
                                 "role", "fixture_quality", "--render"],
                                cwd=self.root, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["native_payload"])
        self.assertIn("preserve unknown results", payload["prompt"])
        self.assertIn("Review the selected artifact", payload["prompt"])
        self.assertEqual(len(payload["components"]), 2)

    def test_output_parent_aliases_preserve_role_validation(self):
        parent = self.root / "real-parent"
        parent.mkdir()
        alias = self.root / "alias-parent"
        alias.symlink_to(parent, target_is_directory=True)
        nested = parent / "nested"
        nested.mkdir()
        for output in (alias / "bundle", nested / ".." / "another-bundle"):
            with self.subTest(output=str(output)):
                result = build_module.build(self.repo, output)
                self.assertEqual(result["status"], "pass")
                build_module.check_owned_output(output)
                self.assertTrue((output / "skills/lody4dot/references/roles/index.json").is_file())

    def test_invalid_role_dependency_cannot_replace_existing_bundle(self):
        build_module.build(self.repo, self.output)
        before = build_module.inventory(self.output)
        path = self.skill / "references/roles/index.json"
        catalog = json.loads(path.read_text())
        catalog["roles"][0]["methods"] = ["missing_method"]
        self.write_json(path, catalog)
        with self.assertRaisesRegex(build_module.BuildError, "Role library"):
            build_module.build(self.repo, self.output)
        self.assertEqual(build_module.inventory(self.output), before)

    def test_post_commit_cleanup_failure_reports_applied_output_without_rollback(self):
        real_check = build_module.check_owned_output
        real_remove = build_module.shutil.rmtree
        for failure in ("ownership_check", "partial_removal"):
            with self.subTest(failure=failure):
                output = self.root / failure
                self.write(self.skill / "references/cloud.md", "# Previous reference\n")
                build_module.build(self.repo, output)
                self.write(self.skill / "references/cloud.md", "# Applied reference\n")

                def check(path):
                    if path.name.startswith(".lody4dot-previous-") and failure == "ownership_check":
                        raise build_module.BuildError("fixture-private-cleanup-details")
                    return real_check(path)

                def remove(path, *args, **kwargs):
                    if Path(path).name.startswith(".lody4dot-previous-"):
                        (Path(path) / "skills/lody4dot/references/cloud.md").unlink()
                        raise PermissionError("fixture-private-cleanup-details")
                    return real_remove(path, *args, **kwargs)

                with patch.object(build_module, "check_owned_output", side_effect=check), \
                     patch.object(build_module.shutil, "rmtree", side_effect=remove):
                    code, result = self.run_cli(output=output)

                self.assertEqual(code, 0)
                self.assertEqual(result["status"], "pass")
                self.assertTrue(result["output_applied"])
                self.assertEqual(result["output"], str(output))
                warning, = result["warnings"]
                self.assertEqual(warning["code"], "backup_cleanup_failed")
                backup = Path(warning["backup_path"])
                self.assertEqual(backup.parent, output.parent)
                self.assertTrue(backup.is_dir())
                self.assertEqual((backup / "skills/lody4dot/references/cloud.md").exists(),
                                 failure == "ownership_check")
                self.assertNotIn("fixture-private-cleanup-details", json.dumps(result))
                self.assertEqual((output / "skills/lody4dot/references/cloud.md").read_text(),
                                 "# Applied reference\n")
                real_check(output)
                self.assertEqual(result["manifest_sha256"],
                                 hashlib.sha256((output / build_module.RECEIPT).read_bytes()).hexdigest())

    def test_zip_continues_after_backup_cleanup_warning(self):
        build_module.build(self.repo, self.output)
        self.write(self.skill / "references/cloud.md", "# Applied ZIP reference\n")
        target = self.root / "release.zip"
        real_remove = build_module.shutil.rmtree

        def remove(path, *args, **kwargs):
            if Path(path).name.startswith(".lody4dot-previous-"):
                raise PermissionError("fixture-private-cleanup-details")
            return real_remove(path, *args, **kwargs)

        with patch.object(build_module.shutil, "rmtree", side_effect=remove):
            code, result = self.run_cli("--zip", target)
        self.assertEqual(code, 0)
        self.assertEqual(result["warnings"][0]["code"], "backup_cleanup_failed")
        self.assertTrue(result["output_applied"])
        self.assertTrue(result["archive"]["verification"])
        self.assertEqual(result["archive"]["sha256"], hashlib.sha256(target.read_bytes()).hexdigest())
        with zipfile.ZipFile(target) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.read("skills/lody4dot/references/cloud.md"),
                             b"# Applied ZIP reference\n")

    def test_archive_failure_preserves_applied_output_and_cleanup_warning(self):
        build_module.build(self.repo, self.output)
        self.write(self.skill / "references/cloud.md", "# Applied before archive failure\n")
        target = self.root / "release.zip"
        real_remove = build_module.shutil.rmtree

        def remove(path, *args, **kwargs):
            if Path(path).name.startswith(".lody4dot-previous-"):
                raise PermissionError("fixture-private-cleanup-details")
            return real_remove(path, *args, **kwargs)

        with patch.object(build_module.shutil, "rmtree", side_effect=remove), \
             patch.object(build_module.os, "link", side_effect=OSError("archive publish unavailable")):
            code, result = self.run_cli("--zip", target)

        self.assertEqual(code, 3)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["failure_stage"], "archive")
        self.assertTrue(result["output_applied"])
        self.assertEqual(result["output"], str(self.output))
        warning, = result["warnings"]
        self.assertEqual(warning["code"], "backup_cleanup_failed")
        self.assertTrue(Path(warning["backup_path"]).is_dir())
        self.assertNotIn("fixture-private-cleanup-details", json.dumps(result))
        self.assertNotIn("archive", result)
        self.assertFalse(target.exists())
        self.assertEqual((self.output / "skills/lody4dot/references/cloud.md").read_text(),
                         "# Applied before archive failure\n")
        self.assertEqual(result["manifest_sha256"],
                         hashlib.sha256((self.output / build_module.RECEIPT).read_bytes()).hexdigest())
        build_module.check_owned_output(self.output)

    def test_text_cli_displays_backup_cleanup_warning(self):
        build_module.build(self.repo, self.output)
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(build_module, "__file__", str(self.plugin / "scripts/build.py")), \
             patch.object(build_module.shutil, "rmtree", side_effect=PermissionError("fixture-private-cleanup-details")), \
             redirect_stdout(stdout), redirect_stderr(stderr):
            code = build_module.main(["--output", str(self.output)])
        self.assertEqual(code, 0)
        self.assertIn("Built", stdout.getvalue())
        self.assertIn("backup_cleanup_failed", stderr.getvalue())
        self.assertIn(".lody4dot-previous-", stderr.getvalue())
        self.assertNotIn("fixture-private-cleanup-details", stdout.getvalue() + stderr.getvalue())

    def test_text_cli_archive_failure_reports_applied_output_and_cleanup_warning(self):
        build_module.build(self.repo, self.output)
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(build_module, "__file__", str(self.plugin / "scripts/build.py")), \
             patch.object(build_module.shutil, "rmtree", side_effect=PermissionError("fixture-private-cleanup-details")), \
             patch.object(build_module.os, "link", side_effect=OSError("archive publish unavailable")), \
             redirect_stdout(stdout), redirect_stderr(stderr):
            code = build_module.main(["--output", str(self.output), "--zip", str(self.root / "release.zip")])
        self.assertEqual(code, 3)
        self.assertIn("Directory output remains applied", stderr.getvalue())
        self.assertIn(str(self.output), stderr.getvalue())
        self.assertIn("backup_cleanup_failed", stderr.getvalue())
        self.assertIn(".lody4dot-previous-", stderr.getvalue())
        self.assertNotIn("fixture-private-cleanup-details", stdout.getvalue() + stderr.getvalue())

    def test_unmanaged_or_modified_output_is_preserved(self):
        self.write(self.output / "user.txt", "user data")
        with self.assertRaisesRegex(build_module.BuildError, "unmanaged"):
            build_module.build(self.repo, self.output)
        self.assertEqual((self.output / "user.txt").read_text(), "user data")
        shutil.rmtree(self.output)
        build_module.build(self.repo, self.output)
        self.write(self.output / "user.txt", "later addition")
        with self.assertRaisesRegex(build_module.BuildError, "unowned"):
            build_module.build(self.repo, self.output)
        self.assertEqual((self.output / "user.txt").read_text(), "later addition")

    def test_missing_or_external_reference_fails_without_replacing_previous_build(self):
        build_module.build(self.repo, self.output)
        previous = build_module.inventory(self.output)
        for link in ("references/missing.md", "../../outside.md"):
            with self.subTest(link=link):
                self.write(self.skill / "SKILL.md", f"[bad]({link})\n")
                with self.assertRaises(build_module.BuildError):
                    build_module.build(self.repo, self.output)
                self.assertEqual(previous, build_module.inventory(self.output))

    def test_missing_required_runtime_is_rejected(self):
        (self.plugin / "runtime/package-lock.json").unlink()
        with self.assertRaisesRegex(build_module.BuildError, "Missing required"):
            build_module.build(self.repo, self.output)
        self.assertFalse(self.output.exists())

    def test_missing_onboarding_skill_preserves_previous_build(self):
        build_module.build(self.repo, self.output)
        previous = build_module.inventory(self.output)
        (self.setup_skill / "SKILL.md").unlink()
        with self.assertRaisesRegex(build_module.BuildError, "Missing required source"):
            build_module.build(self.repo, self.output)
        self.assertEqual(previous, build_module.inventory(self.output))

    def test_invalid_onboarding_targets_preserve_previous_build(self):
        build_module.build(self.repo, self.output)
        previous = build_module.inventory(self.output)
        path = self.plugin / ".codex-plugin/plugin.json"
        manifest = json.loads(path.read_text())
        for extension in ({}, {"com.openai": None}, {"com.openai": []},
                          *({"com.openai": {"onboardingSkill": value}} for value in (
                              "../outside/SKILL.md", "./skills/missing/SKILL.md",
                              "https://example.com/SKILL.md", "/absolute/SKILL.md", None))):
            with self.subTest(extension=extension):
                self.write_json(path, {**manifest, "extensions": extension})
                with self.assertRaisesRegex(build_module.BuildError, "onboardingSkill"):
                    build_module.build(self.repo, self.output)
                self.assertEqual(previous, build_module.inventory(self.output))

    def test_setup_extra_resources_are_rejected_without_replacing_output(self):
        build_module.build(self.repo, self.output)
        previous = build_module.inventory(self.output)
        self.write(self.setup_skill / "references/extra.md", "# Unowned setup resource\n")
        with self.assertRaisesRegex(build_module.BuildError, "Unexpected file in setup skill"):
            build_module.build(self.repo, self.output)
        self.assertEqual(previous, build_module.inventory(self.output))

    def test_setup_references_are_checked_and_symlinks_rejected(self):
        build_module.build(self.repo, self.output)
        previous = build_module.inventory(self.output)
        path = self.setup_skill / "SKILL.md"
        for target in ("../lody4dot/missing.md", "../../../outside.md"):
            with self.subTest(target=target):
                self.write(path, f"[Broken]({target})\n")
                with self.assertRaises(build_module.BuildError):
                    build_module.build(self.repo, self.output)
                self.assertEqual(previous, build_module.inventory(self.output))
        path.unlink()
        path.symlink_to(self.skill / "SKILL.md")
        with self.assertRaisesRegex(build_module.BuildError, "Symlink"):
            build_module.build(self.repo, self.output)
        self.assertEqual(previous, build_module.inventory(self.output))

    def test_missing_shared_runtime_helper_is_rejected_without_replacing_output(self):
        build_module.build(self.repo, self.output)
        previous = build_module.inventory(self.output)
        (self.plugin / "scripts/platform_support.py").unlink()
        with self.assertRaisesRegex(build_module.BuildError, "Missing required"):
            build_module.build(self.repo, self.output)
        self.assertEqual(build_module.inventory(self.output), previous)

    def test_missing_common_dependency_is_rejected(self):
        (self.plugin / "scripts/common.py").unlink()
        with self.assertRaisesRegex(build_module.BuildError, "Missing required source: scripts/common.py"):
            build_module.build(self.repo, self.output)
        self.assertFalse(self.output.exists())

    def test_reference_style_links_cannot_leave_package_or_miss_resource(self):
        for target in ("../../outside.md", "references/missing.md"):
            with self.subTest(target=target):
                self.write(self.skill / "SKILL.md", f"[doc][ref]\n\n[ref]: {target}\n")
                with self.assertRaises(build_module.BuildError):
                    build_module.build(self.repo, self.output)
        self.write(self.skill / "SKILL.md", "[doc][ref]\n\n[ref]: references/cloud.md\n")
        build_module.build(self.repo, self.output)

    def test_symlink_input_and_output_are_rejected(self):
        external = self.root / "outside.md"
        self.write(external, "outside")
        linked = self.skill / "references/linked.md"
        linked.symlink_to(external)
        with self.assertRaisesRegex(build_module.BuildError, "Symlink"):
            build_module.build(self.repo, self.output)
        linked.unlink()
        self.output.symlink_to(self.root / "other", target_is_directory=True)
        with self.assertRaisesRegex(build_module.BuildError, "symlink"):
            build_module.build(self.repo, self.output)

    def test_sensitive_or_unlisted_input_fails_closed(self):
        for name, contents in ((".env", "secret"), ("access.token", "secret"), ("extra.txt", "unexpected")):
            with self.subTest(name=name):
                path = self.plugin / "runtime" / name
                self.write(path, contents)
                with self.assertRaises(build_module.BuildError):
                    build_module.build(self.repo, self.output)
                path.unlink()
        for assignment in ('LODY_CLI_TOKEN="fake-sensitive-material"', "export LODY_CLI_TOKEN=fake-sensitive-material"):
            with self.subTest(assignment=assignment):
                self.write(self.skill / "references/cloud.md", assignment + "\n")
                with self.assertRaisesRegex(build_module.BuildError, "Sensitive content"):
                    build_module.build(self.repo, self.output)

    def test_failed_final_switch_restores_previous_build(self):
        build_module.build(self.repo, self.output)
        previous = build_module.inventory(self.output)
        self.write(self.skill / "references/cloud.md", "# New content\n")
        real_replace = build_module.os.replace

        def fail_final_switch(source, destination):
            if Path(source).name.startswith(".lody4dot-build-"):
                raise OSError("fixture rename failure")
            return real_replace(source, destination)

        with patch.object(build_module.os, "replace", side_effect=fail_final_switch):
            with self.assertRaisesRegex(OSError, "fixture rename failure"):
                build_module.build(self.repo, self.output)
        self.assertEqual(previous, build_module.inventory(self.output))
        self.assertEqual([], list(self.root.glob(".lody4dot-*")))


if __name__ == "__main__":
    unittest.main()
