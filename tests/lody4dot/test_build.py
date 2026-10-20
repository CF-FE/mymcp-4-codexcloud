"""Self-contained build behavior, including safe refusal and relocation."""

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[2] / "plugin/lody4dot/scripts/build.py"
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
        self.plugin = self.repo / "plugin/lody4dot"
        self.output = self.root / "package"
        self.write(self.skill / "SKILL.md", "# Lody\n\n[Reference](references/cloud.md)\n")
        self.write(self.skill / "references/cloud.md", "# Cloud\n[Source](https://lody.ai/zh/docs/cli/)\n")
        self.write_json(self.skill / "references/command-index.json", {"commands": []})
        self.write_json(self.skill / "references/sources.json", {"resource": "help-snapshot.json"})
        self.write_json(self.skill / "references/help-snapshot.json", {"commands": []})
        self.write(self.plugin / "README.md", "# Plugin\n[Skill](skills/lody4dot/SKILL.md)\n")
        self.write_json(self.plugin / ".codex-plugin/plugin.json", {
            "name": "lody4dot", "version": "0.1.0", "skills": "./skills",
        })
        for name in ("install.py", "doctor.py", "auth.py", "common.py"):
            self.write(self.plugin / "scripts" / name, "print('fixture')\n")
        self.write(self.plugin / "scripts/build.py", "# source-only builder\n")
        for name in ("package.json", "package-lock.json", "build-policy.json"):
            self.write_json(self.plugin / "runtime" / name, {})

    @staticmethod
    def write(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")

    def write_json(self, path, value):
        self.write(path, json.dumps(value) + "\n")

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
        marketplace = json.loads((relocated / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual(marketplace["plugins"][0]["source"], {"source": "local", "path": "."})

    def test_rebuild_owned_output_updates_and_keeps_output_complete(self):
        build_module.build(self.repo, self.output)
        self.write(self.skill / "references/cloud.md", "# Updated reference\n")
        build_module.build(self.repo, self.output)
        self.assertEqual((self.output / "skills/lody4dot/references/cloud.md").read_text(), "# Updated reference\n")
        build_module.check_owned_output(self.output)

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
