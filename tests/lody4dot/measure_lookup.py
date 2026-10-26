#!/usr/bin/env python3
"""Measure offline output, including the existing inline lookup baseline; no Lody calls."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skill/lody4dot"
LOOKUP = ROOT / "plugin/lody4dot/scripts/lookup.py"
INLINE = "import json,sys; d=json.load(open(sys.argv[1])); e=[x for x in d['commands'] if x['command']==sys.argv[2]]; assert len(e)==1; print(json.dumps(e[0],ensure_ascii=False,indent=2))"


def measure(args, repetitions):
    elapsed, outputs = [], []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(repetitions):
        start = time.perf_counter()
        result = subprocess.run([sys.executable, *map(str, args)], cwd=ROOT,
                                capture_output=True, check=True, env=env, timeout=15)
        elapsed.append((time.perf_counter() - start) * 1000)
        outputs.append(result.stdout)
    if any(output != outputs[0] for output in outputs):
        raise ValueError("Non-deterministic output")
    body = outputs[0].decode("utf-8")
    return json.loads(body), {"stdout_bytes": len(outputs[0]), "stdout_characters": len(body),
                             "calls_per_lookup": 1, "repetitions": repetitions,
                             "local_process_median_ms": round(statistics.median(elapsed), 3)}


def report(repetitions):
    baseline = json.loads((ROOT / "tests/lody4dot/fixtures/knowledge-baseline.json").read_text())
    before = baseline["entrypoint"].encode()
    assert hashlib.sha256(before).hexdigest() == baseline["entrypoint_sha256"]
    current = (SKILL / "SKILL.md").read_bytes()
    result = {"schema_version": 1, "scope": "offline_output_and_local_process_only",
              "measured_at": datetime.now(timezone.utc).isoformat(), "python": sys.version.split()[0],
              "entrypoint": {"baseline_bytes": len(before), "baseline_sha256": baseline["entrypoint_sha256"],
                             "current_bytes": len(current), "current_sha256": hashlib.sha256(current).hexdigest()},
              "commands": [], "roles": [],
              "not_measured": ["model_tokens", "model_latency", "business_latency", "live_role_quality"]}
    for detail, filename in (("index", "command-index.json"), ("help", "help-snapshot.json"), ("audit", "command-audit.json")):
        source = SKILL / "references" / filename
        inline, old = measure(["-c", INLINE, source, "session observe"], repetitions)
        selected, new = measure([LOOKUP, "command", "session observe", "--detail", detail], repetitions)
        assert selected["entry"] == inline
        result["commands"].append({"command": "session observe", "detail": detail,
                                   "full_file_bytes": source.stat().st_size,
                                   "existing_inline": old, "lookup_with_provenance": new,
                                   "entry_equal": True})
    original = ROOT / "docs/lody4dot/workspace-roles/v2.2/roles-v2.json"
    old_roles = {role["role_id"]: role for role in json.loads(original.read_text())["roles"]}
    for identity, source_id, project in (("workspace_quality", "workspace_quality", None),
                                         ("workspace_quality", "workspace_quality", "fanren-work"),
                                         ("fanren_audio_production", "audio_production", "fanren-work")):
        args = [LOOKUP, "role", identity, "--render"]
        if project:
            args += ["--project", project]
        selected, measured = measure(args, repetitions)
        result["roles"].append({"role": identity, "project": project,
                                "v2_2_full_file_bytes": original.stat().st_size,
                                "v2_2_selected_prompt_bytes": len(old_roles[source_id]["prompt"].encode()),
                                "rendered_prompt_bytes": len(selected["prompt"].encode()),
                                "lookup_with_metadata": measured,
                                "comparison_scope": "versioned_derivative_not_identical_prompt_semantics"})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetitions", type=int, choices=range(1, 6), default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    text = json.dumps(report(args.repetitions), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
