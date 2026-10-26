"""Shared, bounded member policy for building and inspecting lody4dot bundles."""
from pathlib import PurePosixPath
import re


SCRIPT_NAMES = frozenset({
    "install.py", "doctor.py", "auth.py", "common.py", "platform_support.py",
    "bootstrap.py", "handoff.py", "lookup.py", "package_layout.py",
})
HOST_NAMES = frozenset({"codex-cloud.md", "codex-cli.md", "dot.md"})
RUNTIME_NAMES = frozenset({"package.json", "package-lock.json", "build-policy.json"})
SENSITIVE_NAME = re.compile(
    r"(^\.env($|\.)|(^|[._-])(token|credentials?|secrets?)([._-]|$)|"
    r"\.(pem|key|p12|pfx)$)", re.IGNORECASE,
)


def bundle_member(name):
    """Accept only canonical relative paths in the supported package layout."""
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        return False
    path = PurePosixPath(name)
    parts = path.parts
    if (path.is_absolute() or path.as_posix() != name or ".." in parts
            or any(SENSITIVE_NAME.search(part) for part in parts)):
        return False
    if name in {"README.md", ".codex-plugin/plugin.json", ".agents/plugins/marketplace.json",
                "skills/lody4dot/SKILL.md", "skills/lody4dot-setup/SKILL.md"}:
        return True
    if len(parts) == 2:
        allowed = {"scripts": SCRIPT_NAMES, "hosts": HOST_NAMES, "runtime": RUNTIME_NAMES}
        return parts[1] in allowed.get(parts[0], ())
    if parts[:3] != ("skills", "lody4dot", "references"):
        return False
    if len(parts) == 4:
        return path.suffix in {".md", ".json"}
    if parts[3:4] != ("roles",):
        return False
    return (len(parts) == 5 and parts[4] in {"index.json", "common.md"}
            or len(parts) == 6 and parts[4] in {"workspace", "projects"} and path.suffix == ".md")
