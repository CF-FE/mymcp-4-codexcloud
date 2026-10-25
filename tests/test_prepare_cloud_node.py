"""Offline behavior checks for the saved cloud environment's Node bootstrap."""

import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_cloud_node.py"
SPEC = importlib.util.spec_from_file_location("prepare_cloud_node", SCRIPT)
node_setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(node_setup)


class CloudNodeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.prefix = self.root / "node"
        self.archive = self.make_archive()
        self.digest = hashlib.sha256(self.archive).hexdigest()
        self.downloads = []
        self.addCleanup(patch.stopall)
        patch.object(node_setup, "ARCHIVE_SHA256", self.digest).start()
        patch.object(node_setup.platform, "system", return_value="Linux").start()
        patch.object(node_setup.platform, "machine", return_value="x86_64").start()
        patch.object(node_setup, "_download", side_effect=self.download).start()

    def make_archive(self, extra=None):
        content = io.BytesIO()
        top = "node-v24.22.1-linux-x64"
        files = {
            "bin/node": (b'#!/bin/sh\nif [ "$1" = "--version" ]; then\n'
                         b"printf 'v24.22.1\\n'\nelse\nprintf '11.19.1\\n'\nfi\n", 0o755),
            "lib/node_modules/npm/bin/npm-cli.js": (b"// fixture only\n", 0o644),
        }
        with tarfile.open(fileobj=content, mode="w:xz") as archive:
            for name, (data, mode) in files.items():
                member = tarfile.TarInfo(f"{top}/{name}")
                member.size, member.mode = len(data), mode
                archive.addfile(member, io.BytesIO(data))
            member = tarfile.TarInfo(f"{top}/bin/npm")
            member.type, member.linkname = tarfile.SYMTYPE, "../lib/node_modules/npm/bin/npm-cli.js"
            archive.addfile(member)
            if extra:
                for name, kind, link in extra if isinstance(extra, list) else [extra]:
                    member = tarfile.TarInfo(name)
                    member.type, member.linkname = kind, link
                    archive.addfile(member, io.BytesIO(b""))
        return content.getvalue()

    def download(self, destination):
        self.downloads.append(destination)
        destination.write_bytes(self.archive)

    def install(self):
        return node_setup.prepare_node(self.prefix)

    def snapshot(self):
        return ((self.prefix / "receipt.json").read_bytes(),
                os.readlink(self.prefix / "current"))

    def seed_previous(self):
        self.install()
        previous = self.prefix / "versions/v24.21.0"
        (self.prefix / "versions/v24.22.1").rename(previous)
        (self.prefix / "current").unlink()
        (self.prefix / "current").symlink_to("versions/v24.21.0")
        receipt = json.loads((self.prefix / "receipt.json").read_text())
        receipt.update(version="v24.21.0", node=str(previous / "bin/node"),
                       npm=str(previous / "bin/npm"),
                       archive_url="https://nodejs.org/dist/v24.21.0/node-v24.21.0-linux-x64.tar.xz")
        (self.prefix / "receipt.json").write_text(json.dumps(receipt))
        return self.snapshot()

    def test_fresh_install_checks_archive_and_preserves_internal_npm_link(self):
        report = self.install()
        self.assertFalse(report["reused"])
        self.assertEqual(report["node_version"], "v24.22.1")
        self.assertEqual(report["npm_version"], "11.19.1")
        self.assertEqual(os.readlink(self.prefix / "current"), "versions/v24.22.1")
        self.assertTrue((self.prefix / "current/bin/npm").is_symlink())
        self.assertEqual(json.loads((self.prefix / ".managed.json").read_text()),
                         {"schema_version": 1, "owner": "lody4dot-node"})

    def test_existing_manual_receipt_reuses_without_download_or_receipt_rewrite(self):
        self.install()
        receipt = json.loads((self.prefix / "receipt.json").read_text())
        for field in ("schema_version", "node_version", "npm_version", "owner"):
            receipt.pop(field, None)
        (self.prefix / "receipt.json").write_text(json.dumps(receipt, indent=4))
        before = self.snapshot()
        self.downloads.clear()
        self.assertTrue(self.install()["reused"])
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.downloads, [])

    def test_checksum_failure_keeps_previous_receipt_and_current(self):
        before = self.seed_previous()
        with patch.object(node_setup, "ARCHIVE_SHA256", "0" * 64):
            with self.assertRaises(node_setup.NodeSetupError):
                self.install()
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.prefix / "versions/v24.22.1").exists())

    def test_failed_version_probe_preserves_previous_entry_and_receipt(self):
        before = self.seed_previous()
        result = node_setup.subprocess.CompletedProcess([], 0, stdout="unexpected-version\n")
        with patch.object(node_setup.subprocess, "run", return_value=result):
            with self.assertRaises(node_setup.NodeSetupError):
                self.install()
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.prefix / "versions/v24.22.1").exists())

    def test_activation_failure_rolls_back_both_entry_and_receipt(self):
        before = self.seed_previous()
        original = node_setup.os.replace

        def fail_current(source, destination):
            if Path(destination) == self.prefix / "current":
                raise OSError("fixture activation failure")
            return original(source, destination)

        with patch.object(node_setup.os, "replace", side_effect=fail_current):
            with self.assertRaises(node_setup.NodeSetupError):
                self.install()
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.prefix / ".current-next").exists())

    def test_no_fallible_temporary_cleanup_follows_current_commit(self):
        original_replace, original_unlink = node_setup.os.replace, Path.unlink
        committed = False

        def track_commit(source, destination):
            nonlocal committed
            result = original_replace(source, destination)
            if Path(destination) == self.prefix / "current":
                committed = True
            return result

        def reject_post_commit_cleanup(path, *args, **kwargs):
            if committed and path == self.prefix / ".current-next":
                raise OSError("fixture cleanup after commit")
            return original_unlink(path, *args, **kwargs)

        with patch.object(node_setup.os, "replace", side_effect=track_commit), \
                patch.object(Path, "unlink", reject_post_commit_cleanup):
            self.install()
        self.assertTrue(committed)
        self.assertTrue((self.prefix / "current/bin/node").is_file())

    def test_stage_cleanup_failure_leaves_previous_entry_and_receipt(self):
        before = self.seed_previous()
        original = node_setup.tempfile.TemporaryDirectory.cleanup

        def fail_cleanup(temporary):
            original(temporary)
            if Path(temporary.name).name.startswith(".staging-"):
                raise OSError("fixture cleanup failure")

        with patch.object(node_setup.tempfile.TemporaryDirectory, "cleanup", fail_cleanup):
            with self.assertRaises(node_setup.NodeSetupError):
                self.install()
        self.assertEqual(self.snapshot(), before)

    def test_unmanaged_prefix_and_symlink_ancestor_are_not_modified(self):
        self.prefix.mkdir()
        (self.prefix / "foreign").write_text("keep")
        with self.assertRaises(node_setup.NodeSetupError):
            self.install()
        self.assertEqual((self.prefix / "foreign").read_text(), "keep")
        link = self.root / "link"
        link.symlink_to(self.prefix, target_is_directory=True)
        with self.assertRaises(node_setup.NodeSetupError):
            node_setup.prepare_node(link / "nested")
        self.assertFalse((self.prefix / "nested").exists())
        self.assertEqual(self.downloads, [])

    def test_unowned_version_directory_and_external_current_are_rejected(self):
        self.install()
        (self.prefix / "receipt.json").unlink()
        with self.assertRaises(node_setup.NodeSetupError):
            self.install()
        (self.prefix / "current").unlink()
        (self.prefix / "current").symlink_to(self.root)
        with self.assertRaises(node_setup.NodeSetupError):
            self.install()
        self.assertEqual(os.readlink(self.prefix / "current"), str(self.root))

    def test_tar_escape_paths_links_and_special_files_never_activate(self):
        top = "node-v24.22.1-linux-x64"
        fixtures = [
            (f"{top}/../../escape", tarfile.REGTYPE, ""),
            ("/absolute", tarfile.REGTYPE, ""),
            (f"{top}/bin/escape", tarfile.SYMTYPE, "../../outside"),
            (f"{top}/bin/escape", tarfile.SYMTYPE, "/outside"),
            (f"{top}/hard", tarfile.LNKTYPE, "../outside"),
            (f"{top}/fifo", tarfile.FIFOTYPE, ""),
            [(f"{top}/one", tarfile.SYMTYPE, "."),
             (f"{top}/two", tarfile.SYMTYPE, "one/../outside")],
            [(f"{top}/one", tarfile.SYMTYPE, "."),
             (f"{top}/one/child", tarfile.REGTYPE, "")],
        ]
        for index, fixture in enumerate(fixtures):
            with self.subTest(fixture=fixture):
                self.archive = self.make_archive(fixture)
                with patch.object(node_setup, "ARCHIVE_SHA256", hashlib.sha256(self.archive).hexdigest()):
                    with self.assertRaises(node_setup.NodeSetupError):
                        node_setup.prepare_node(self.root / f"invalid-{index}")
                self.assertFalse((self.root / f"invalid-{index}/current").exists())
        self.assertFalse((self.root / "escape").exists())

    def test_safe_internal_hardlink_is_extracted_without_changing_node(self):
        top = "node-v24.22.1-linux-x64"
        self.archive = self.make_archive((f"{top}/npm-hardlink", tarfile.LNKTYPE,
                                          f"{top}/lib/node_modules/npm/bin/npm-cli.js"))
        with patch.object(node_setup, "ARCHIVE_SHA256", hashlib.sha256(self.archive).hexdigest()):
            self.install()
        self.assertEqual((self.prefix / "current/npm-hardlink").read_bytes(), b"// fixture only\n")

    def test_hardlink_uses_the_validated_normalized_source(self):
        top = "node-v24.22.1-linux-x64"
        self.archive = self.make_archive([
            (f"{top}/sentinel", tarfile.REGTYPE, ""),
            (f"{top}/deep/link", tarfile.SYMTYPE, ".."),
            (f"{top}/hard", tarfile.LNKTYPE, f"{top}/deep/link/../../sentinel"),
        ])
        original = node_setup.os.link

        def require_validated_source(source, destination):
            # Resolving the raw path through deep/link before '..' can reach
            # outside the archive root, even though normpath stays inside.
            self.assertNotIn("..", Path(source).parts)
            self.assertEqual(Path(source).name, "sentinel")
            return original(source, destination)

        with patch.object(node_setup, "ARCHIVE_SHA256", hashlib.sha256(self.archive).hexdigest()), \
                patch.object(node_setup.os, "link", side_effect=require_validated_source):
            self.install()
        self.assertEqual((self.prefix / "current/hard").read_bytes(), b"")

    def test_probes_remove_all_inherited_environment_including_node_options(self):
        original = node_setup.subprocess.run
        observed = []

        def capture(*args, **kwargs):
            observed.append((args[0], kwargs))
            if len(observed) == 2:
                configs = [Path(argument.split("=", 1)[1]) for argument in args[0]
                           if argument.startswith(("--userconfig=", "--globalconfig="))]
                self.assertEqual(len(set(configs)), 2)
                self.assertTrue(all(path.read_bytes() == b"" for path in configs))
            return original(*args, **kwargs)

        with patch.dict(os.environ, {"LODY_CLI_TOKEN": "fixture-secret", "NODE_OPTIONS": "fixture-option",
                                     "NPM_TOKEN": "fixture-secret"}), \
                patch.object(node_setup.subprocess, "run", side_effect=capture):
            self.install()
        self.assertEqual(len(observed), 2)
        self.assertTrue(all(set(options["env"]) <= {"PATH", "LC_ALL"} for _, options in observed))
        self.assertIn("--offline", observed[1][0])
        self.assertTrue(any(argument.startswith("--userconfig=") for argument in observed[1][0]))
        self.assertTrue(any(argument.startswith("--globalconfig=") for argument in observed[1][0]))
        self.assertNotEqual(Path(observed[1][1]["cwd"]), self.prefix)

    def test_unsupported_platform_stops_before_creating_prefix(self):
        with patch.object(node_setup.platform, "machine", return_value="aarch64"):
            with self.assertRaises(node_setup.NodeSetupError):
                self.install()
        self.assertFalse(self.prefix.exists())


class OfficialArchiveTests(unittest.TestCase):
    def test_pinned_source_is_the_verified_official_linux_x64_archive(self):
        self.assertEqual(node_setup.ARCHIVE_URL,
                         "https://nodejs.org/dist/v24.22.1/node-v24.22.1-linux-x64.tar.xz")
        self.assertEqual(node_setup.ARCHIVE_SHA256,
                         "6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6")

    def test_redirects_cannot_leave_official_https_source(self):
        handler = node_setup._OfficialRedirects()
        for url in ("http://nodejs.org/archive", "https://fixture.invalid/archive",
                    "https://fixture@nodejs.org/archive"):
            with self.subTest(url=url), self.assertRaises(node_setup.NodeSetupError):
                handler.redirect_request(None, None, 302, "", {}, url)


if __name__ == "__main__":
    unittest.main()
