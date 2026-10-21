#!/usr/bin/env python3
"""Build the self-contained lody4dot plugin from repository-owned sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import unquote, urlsplit


RECEIPT = ".lody4dot-build.json"
TOOL = "lody4dot-build"
SCRIPT_NAMES = {"install.py", "doctor.py", "auth.py", "common.py", "build.py", "platform_support.py"}
RUNTIME_NAMES = {"package.json", "package-lock.json", "build-policy.json"}
REQUIRED = (
    "README.md", ".codex-plugin/plugin.json", "scripts/install.py",
    "scripts/doctor.py", "scripts/auth.py", "scripts/common.py", "scripts/platform_support.py", "runtime/package.json",
    "runtime/package-lock.json", "runtime/build-policy.json",
)
SKILL_REQUIRED = (
    "SKILL.md", "references/command-index.json", "references/sources.json",
    "references/help-snapshot.json",
)
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
MARKDOWN_DEFINITION = re.compile(r"(?m)^ {0,3}\[[^\]]+\]:\s*(<[^>\r\n]+>|\S+)")
SENSITIVE_NAME = re.compile(
    r"(^\.env($|\.)|(^|[._-])(token|credentials?|secrets?)([._-]|$)|"
    r"\.(pem|key|p12|pfx)$)", re.IGNORECASE,
)
SENSITIVE_CONTENT = re.compile(
    rb"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----|"
    rb"[\"']?LODY_CLI_TOKEN[\"']?[ \t]*[:=][ \t]*"
    rb"(?:\"[^\"\r\n]+\"|'[^'\r\n]+'|[^\s\"'`,}][^\s`,}]*)"
)


class BuildError(Exception):
    """An unsafe or incomplete build input/output."""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BuildError(f"Invalid or unreadable JSON: {path.name}") from exc


def inventory(root: Path) -> dict[str, str]:
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise BuildError(f"Symlink is not allowed: {path.relative_to(root)}")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = digest(path)
        elif not path.is_dir():
            raise BuildError(f"Unsupported file type: {path.relative_to(root)}")
    return files


def check_source_tree(root: Path, kind: str) -> list[Path]:
    if root.is_symlink() or not root.is_dir():
        raise BuildError(f"Missing or symlinked {kind} source")
    selected = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        label = relative.as_posix()
        if path.is_symlink():
            raise BuildError(f"Symlink is not allowed in {kind}: {label}")
        if SENSITIVE_NAME.search(path.name):
            raise BuildError(f"Sensitive file is not allowed in {kind}: {label}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise BuildError(f"Unsupported file type in {kind}: {label}")
        if "__pycache__" in relative.parts and path.suffix == ".pyc":
            continue
        if SENSITIVE_CONTENT.search(path.read_bytes()):
            raise BuildError(f"Sensitive content is not allowed in {kind}: {label}")
        if kind == "skill":
            allowed = label == "SKILL.md" or (
                relative.parts[0] == "references" and path.suffix in {".md", ".json"}
            )
        else:
            allowed = (
                label in {"README.md", ".codex-plugin/plugin.json"}
                or len(relative.parts) == 2 and relative.parts[0] == "scripts"
                and path.name in SCRIPT_NAMES
                or len(relative.parts) == 2 and relative.parts[0] == "runtime"
                and path.name in RUNTIME_NAMES
            )
        if not allowed:
            raise BuildError(f"Unexpected file in {kind}: {label}")
        if path.suffix == ".json":
            read_json(path)
        if label != "scripts/build.py":
            selected.append(path)
    return selected


def check_local_reference(root: Path, owner: Path, target: str) -> None:
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    parsed = urlsplit(target)
    if parsed.scheme in {"https", "http", "mailto"}:
        return
    if parsed.scheme or parsed.netloc:
        raise BuildError(f"Unsupported reference in {owner.relative_to(root)}")
    decoded = unquote(parsed.path)
    if not decoded:
        return
    candidate = (owner.parent / decoded).resolve()
    if not candidate.is_relative_to(root.resolve()):
        raise BuildError(f"Reference leaves package: {owner.relative_to(root)} -> {target}")
    if not candidate.exists():
        raise BuildError(f"Missing reference: {owner.relative_to(root)} -> {target}")


def check_references(root: Path) -> None:
    def json_resources(value, owner):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"resource", "$ref"} and isinstance(item, str):
                    check_local_reference(root, owner, item)
                else:
                    json_resources(item, owner)
        elif isinstance(value, list):
            for item in value:
                json_resources(item, owner)

    for path in root.rglob("*"):
        if path.suffix == ".md":
            contents = path.read_text(encoding="utf-8")
            for link in MARKDOWN_LINK.findall(contents) + MARKDOWN_DEFINITION.findall(contents):
                check_local_reference(root, path, link)
        elif path.suffix == ".json":
            json_resources(read_json(path), path)


def check_owned_output(output: Path) -> None:
    if output.is_symlink():
        raise BuildError("Output must not be a symlink")
    if not output.exists():
        return
    if not output.is_dir():
        raise BuildError("Output must be a directory")
    actual = inventory(output)
    if not actual:
        return
    if RECEIPT not in actual:
        raise BuildError("Refusing to replace a non-empty unmanaged output directory")
    receipt = read_json(output / RECEIPT)
    if not isinstance(receipt, dict) or receipt.get("tool") != TOOL or receipt.get("schema_version") != 1:
        raise BuildError("Output has an invalid ownership receipt")
    actual.pop(RECEIPT)
    if actual != receipt.get("files"):
        raise BuildError("Existing output contains changed or unowned files; preserve it separately")


def build(repo: Path, output: Path) -> dict:
    repo = repo.resolve()
    # Check the given leaf before resolving, so a symlink cannot confer ownership.
    if output.is_symlink():
        raise BuildError("Output must not be a symlink")
    output = output.absolute()
    skill = repo / "skill/lody4dot"
    plugin = repo / "plugin/lody4dot"
    for source in (skill, plugin):
        resolved = output.resolve()
        if resolved == source.resolve() or resolved.is_relative_to(source.resolve()) or source.resolve().is_relative_to(resolved):
            raise BuildError("Output must be separate from the source trees")
    skill_files = check_source_tree(skill, "skill")
    plugin_files = check_source_tree(plugin, "plugin")
    for source, required in ((skill, SKILL_REQUIRED), (plugin, REQUIRED)):
        for relative in required:
            if not (source / relative).is_file():
                raise BuildError(f"Missing required source: {relative}")
    manifest = read_json(plugin / ".codex-plugin/plugin.json")
    if not isinstance(manifest, dict) or manifest.get("name") != "lody4dot" or manifest.get("skills") != "./skills":
        raise BuildError("Plugin manifest must declare lody4dot with skills ./skills")
    check_owned_output(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".lody4dot-build-", dir=output.parent))
    backup = None
    try:
        for source, selected, prefix in (
            (skill, skill_files, Path("skills/lody4dot")),
            (plugin, plugin_files, Path(".")),
        ):
            for path in selected:
                destination = staging / prefix / path.relative_to(source)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination)
        marketplace = staging / ".agents/plugins/marketplace.json"
        marketplace.parent.mkdir(parents=True)
        marketplace.write_text(json.dumps({
            "name": "lody4dot-local",
            "plugins": [{"name": "lody4dot", "source": {"source": "local", "path": "."}}],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        check_references(staging)
        files = inventory(staging)
        receipt = {"schema_version": 1, "tool": TOOL, "plugin_version": manifest.get("version"), "files": files}
        (staging / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # Validate again just before moving, protecting additions since preflight.
        check_owned_output(output)
        if output.exists():
            backup = Path(tempfile.mkdtemp(prefix=".lody4dot-previous-", dir=output.parent))
            backup.rmdir()
            os.replace(output, backup)
        try:
            os.replace(staging, output)
        except BaseException:
            if backup is not None:
                os.replace(backup, output)
                backup = None
            raise
        if backup is not None:
            check_owned_output(backup)
            shutil.rmtree(backup)
            backup = None
        return {"schema_version": 1, "status": "pass", "output": str(output), "file_count": len(files), "manifest_sha256": digest(output / RECEIPT)}
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist/lody4dot"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = build(Path(__file__).resolve().parents[3], args.output)
        code = 0
    except (BuildError, OSError) as exc:
        result = {"schema_version": 1, "status": "fail", "error_category": "build_input", "message": str(exc)}
        code = 3
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif code:
        print(result["message"], file=sys.stderr)
    else:
        print(f"Built {result['file_count']} files at {result['output']}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
