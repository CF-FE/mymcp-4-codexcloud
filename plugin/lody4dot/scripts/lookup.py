#!/usr/bin/env python3
"""Read exact command knowledge and role definitions offline; emit JSON only."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import urlsplit


MAX_BYTES = 2 * 1024 * 1024
MAX_PROMPT_CHARS = 32768
COMMAND_FILES = {"index": "command-index.json", "help": "help-snapshot.json", "audit": "command-audit.json"}
KINDS = {"workspace": {"coordinator", "shared_role"}, "project": {"project_owner", "task_template"}}
ID = re.compile(r"[a-z][a-z0-9_-]{0,63}\Z")


class KnowledgeError(Exception):
    """A stable, non-sensitive input or shipped-knowledge error code."""


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise KnowledgeError("invalid_arguments")


def _text(value):
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeError("invalid_schema")
    return value


def _identifier(value):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise KnowledgeError("invalid_schema")
    return value


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise KnowledgeError("duplicate_json_key")
        result[key] = value
    return result


def _constant(value):
    raise KnowledgeError("invalid_json")


def _path(root, relative, suffix):
    if not isinstance(relative, str) or "\\" in relative:
        raise KnowledgeError("invalid_resource")
    resource = PurePosixPath(relative)
    if resource.is_absolute() or ".." in resource.parts or resource.suffix != suffix:
        raise KnowledgeError("invalid_resource")
    root = Path(root).absolute()
    if root.is_symlink() or root.resolve() != root:
        raise KnowledgeError("invalid_resource")
    candidate = root
    for part in resource.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise KnowledgeError("invalid_resource")
    if not candidate.is_relative_to(root) or not stat.S_ISREG(candidate.stat().st_mode):
        raise KnowledgeError("invalid_resource")
    return candidate


def _bytes(root, relative, suffix):
    path = _path(root, relative, suffix)
    if path.stat().st_size > MAX_BYTES:
        raise KnowledgeError("resource_too_large")
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise KnowledgeError("resource_too_large")
    return data


def _json(root, relative):
    value = json.loads(_bytes(root, relative, ".json").decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_constant)
    if not isinstance(value, dict) or type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        raise KnowledgeError("invalid_schema")
    return value


def _table(items, key="id"):
    if not isinstance(items, list):
        raise KnowledgeError("invalid_schema")
    table = {}
    for item in items:
        if not isinstance(item, dict):
            raise KnowledgeError("invalid_schema")
        identity = _text(item.get(key)) if key == "command" else _identifier(item.get(key))
        if identity in table:
            raise KnowledgeError("duplicate_identifier")
        table[identity] = item
    return table


def skill_root():
    """Find the source or relocated bundle by this script, never by cwd."""
    plugin = Path(__file__).resolve().parent.parent
    bundled = plugin / "skills/lody4dot"
    if (plugin / "skills").exists():
        return bundled
    if plugin.name == "lody4dot" and plugin.parent.name == "plugin":
        return plugin.parent.parent / "skill/lody4dot"
    raise KnowledgeError("missing_skill_root")


def command(root, name, detail="index"):
    filename = COMMAND_FILES[detail]
    data = _json(Path(root) / "references", filename)
    _text(data.get("lody_version"))
    entries = _table(data.get("commands"), "command")
    if name not in entries:
        raise KnowledgeError("unknown_command")
    source = {"resource": "references/" + filename, "lody_version": data["lody_version"],
              "evidence_scope": "shipped_snapshot_not_current_runtime"}
    for field in ("captured_at", "audited_at", "updated_at", "scope", "verification_note", "discovery_note"):
        if field in data:
            source[field] = data[field]
    return {"entry": entries[name], "source": source}


class RoleLibrary:
    def __init__(self, root):
        self.root = Path(root) / "references/roles"
        self.data = _json(self.root, "index.json")
        self.version = _text(self.data.get("library_version"))
        if not re.fullmatch(r"\d+\.\d+\.\d+", self.version):
            raise KnowledgeError("invalid_schema")
        if not isinstance(self.data.get("common"), dict) or not isinstance(self.data.get("provenance"), dict):
            raise KnowledgeError("invalid_schema")
        self.common = self.data["common"].get("resource")
        _path(self.root, self.common, ".md")
        self.projects = _table(self.data.get("projects"))
        self.roles = _table(self.data.get("roles"))
        self.methods = _table(self.data.get("methods"))
        for project in self.projects.values():
            _text(project.get("name"))
            _path(self.root, project.get("resource"), ".md")
        for method in self.methods.values():
            _text(method.get("name"))
            if method.get("relation") not in {"optional_method", "inspiration"} or method.get("bundled") is not False:
                raise KnowledgeError("invalid_method")
            source = method.get("source")
            if not isinstance(source, dict):
                raise KnowledgeError("invalid_method_source")
            repository, commit, path = (_text(source.get(key)) for key in ("repository", "commit", "path"))
            parsed = urlsplit(repository)
            if parsed.scheme != "https" or not parsed.netloc or parsed.query or parsed.fragment:
                raise KnowledgeError("invalid_method_source")
            if not re.fullmatch(r"[a-f0-9]{40}", commit) or PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts:
                raise KnowledgeError("invalid_method_source")
            if source.get("url") != repository.rstrip("/") + "/blob/" + commit + "/" + path:
                raise KnowledgeError("invalid_method_source")
            _text(source.get("license"))
        for role in self.roles.values():
            for field in ("name", "summary", "source_role_id"):
                _text(role.get(field))
            scope = role.get("scope")
            if scope not in KINDS or role.get("kind") not in KINDS[scope]:
                raise KnowledgeError("invalid_role_scope")
            project = role.get("project_id")
            if scope == "project" and project not in self.projects or scope == "workspace" and project is not None:
                raise KnowledgeError("invalid_role_project")
            methods = role.get("methods")
            if not isinstance(methods, list) or any(not isinstance(item, str) for item in methods):
                raise KnowledgeError("invalid_method_dependency")
            if len(methods) != len(set(methods)) or any(item not in self.methods for item in methods):
                raise KnowledgeError("invalid_method_dependency")
            _path(self.root, role.get("resource"), ".md")

    def source(self):
        return {"resource": "references/roles/index.json", "library_version": self.version,
                "evidence_scope": "definitions_not_runtime_binding_or_deployment"}

    def project(self, identity):
        if identity is not None and identity not in self.projects:
            raise KnowledgeError("unknown_project")
        return self.projects.get(identity)

    def list(self, scope=None, project=None):
        self.project(project)
        selected = [role for role in self.roles.values()
                    if (scope is None or role["scope"] == scope)
                    and (project is None or role["scope"] == "workspace" or role["project_id"] == project)]
        fields = ("id", "name", "scope", "kind", "summary", "project_id")
        return {"roles": [{key: role[key] for key in fields if key in role} for role in selected], "source": self.source()}

    def role(self, identity, project=None, render=False):
        if identity not in self.roles:
            raise KnowledgeError("unknown_role")
        chosen = self.roles[identity]
        project_data = self.project(project)
        if chosen["scope"] == "project" and project != chosen["project_id"]:
            raise KnowledgeError("project_required_or_mismatched")
        resources = [self.common, chosen["resource"]]
        if project_data is not None:
            resources.append(project_data["resource"])
        value = {"role": chosen, "resources": resources, "source": self.source(), "native_payload": False,
                 "methods": [dict(self.methods[item], availability="not_bundled") for item in chosen["methods"]]}
        if project_data is not None:
            value["project"] = {key: project_data[key] for key in ("id", "name", "resource")}
        if render:
            # Render carries the complete prompt; detailed method sources remain in the lookup view.
            fields = ("id", "name", "scope", "kind", "project_id")
            value["role"] = {key: chosen[key] for key in fields if key in chosen}
            value["methods"] = [{"id": item, "relation": self.methods[item]["relation"],
                                 "availability": "not_bundled"} for item in chosen["methods"]]
            del value["resources"]
            if project_data is not None:
                value["project"] = {key: project_data[key] for key in ("id", "name")}
            parts, components = [], []
            for relative in resources:
                data = _bytes(self.root, relative, ".md")
                parts.append(_text(data.decode("utf-8")).strip())
                components.append({"resource": relative, "sha256": hashlib.sha256(data).hexdigest()})
            prompt = "\n\n".join(parts)
            if len(prompt) > MAX_PROMPT_CHARS:
                raise KnowledgeError("prompt_too_long")
            value.update(prompt=prompt, prompt_chars=len(prompt), components=components,
                         provenance=self.data["provenance"])
        return value


def validate_library(root):
    """Validate all role/project compositions without stdout or side effects."""
    try:
        library = RoleLibrary(root)
        sizes = []
        for role in library.roles.values():
            projects = [role["project_id"]] if role["scope"] == "project" else [None, *library.projects]
            for project in projects:
                sizes.append(library.role(role["id"], project, render=True)["prompt_chars"])
        return {"role_count": len(library.roles), "project_count": len(library.projects),
                "method_count": len(library.methods), "render_count": len(sizes),
                "max_prompt_chars": max(sizes, default=0), "source": library.source()}
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        raise KnowledgeError("invalid_or_unreadable_knowledge") from None


def main(argv=None):
    parser = SafeParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True, parser_class=SafeParser)
    command_parser = commands.add_parser("command", help="Read one exact command from a shipped snapshot.")
    command_parser.add_argument("name")
    command_parser.add_argument("--detail", choices=tuple(COMMAND_FILES), default="index")
    roles_parser = commands.add_parser("roles", help="List summaries; a project includes shared roles and its own roles.")
    roles_parser.add_argument("--scope", choices=tuple(KINDS))
    roles_parser.add_argument("--project")
    role_parser = commands.add_parser("role", help="Read one definition, optionally compose its complete prompt.")
    role_parser.add_argument("id")
    role_parser.add_argument("--project")
    role_parser.add_argument("--render", action="store_true")
    commands.add_parser("check", help="Validate the whole role library and every explicit composition.")
    try:
        args = parser.parse_args(argv)
        root = skill_root()
        if args.action == "command":
            payload = command(root, args.name, args.detail)
        elif args.action == "check":
            payload = validate_library(root)
        else:
            library = RoleLibrary(root)
            payload = library.list(args.scope, args.project) if args.action == "roles" else library.role(args.id, args.project, args.render)
        result, code = {"schema_version": 1, "status": "pass", **payload}, 0
    except KnowledgeError as exc:
        result, code = {"schema_version": 1, "status": "fail", "error_category": str(exc)}, 2
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        result, code = {"schema_version": 1, "status": "fail", "error_category": "invalid_or_unreadable_knowledge"}, 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
