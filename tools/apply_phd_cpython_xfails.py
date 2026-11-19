#!/usr/bin/env python3
"""Compare CPython stdout to goldens; set manifest xfail_cpython with first diff."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests" / "jython_scripts"))
from harness import normalize_phd_output, run_phd_script_cpython  # noqa: E402

MANIFEST = REPO / "tests" / "jython_scripts" / "phd" / "manifest.json"
GOLDENS = REPO / "tests" / "jython_scripts" / "phd" / "goldens"


def first_diff(expected: str, got: str) -> str:
    el = expected.splitlines()
    gl = got.splitlines()
    for i, (e, g) in enumerate(zip(el, gl)):
        if e != g:
            return f"line {i + 1}: jython={e!r} cpython={g!r}"
    if len(el) != len(gl):
        return f"line count jython={len(el)} cpython={len(gl)}"
    return "unknown"


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = data["scripts"]
    for entry in entries:
        if entry.get("skip_cpython") or entry.get("skip_jython_golden"):
            continue
        rel = entry["path"]
        golden = GOLDENS / (Path(rel).name + ".stdout")
        if not golden.is_file():
            continue
        expected = normalize_phd_output(golden.read_text(encoding="utf-8"))
        rc, out, _ = run_phd_script_cpython(rel, list(entry.get("argv") or []))
        got = normalize_phd_output(out)
        if rc == 0 and got == expected:
            entry.pop("xfail_cpython", None)
            continue
        reason = first_diff(expected, got) if got != expected else f"exit code {rc}"
        entry["xfail_cpython"] = {"reason": reason}
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"updated {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())