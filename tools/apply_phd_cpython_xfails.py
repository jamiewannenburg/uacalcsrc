#!/usr/bin/env python3
"""Compare CPython stdout to goldens; set manifest xfail_cpython with first diff."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests" / "jython_scripts"))
from harness import (  # noqa: E402
    FIXTURES_ROOT,
    compare_phd_outputs,
    normalize_phd_output,
    run_phd_script_cpython,
)

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
        compare_stdout = entry.get("compare_stdout", True)
        compare_files = entry.get("compare_files") or []
        if not compare_stdout and not compare_files:
            continue
        golden = GOLDENS / (Path(rel).name + ".stdout")
        expected = ""
        if compare_stdout and golden.is_file():
            expected = normalize_phd_output(golden.read_text(encoding="utf-8"))
        fixture_root = FIXTURES_ROOT if entry.get("use_fixture_copy") else None
        rc, out, _, artifact_dir = run_phd_script_cpython(
            rel, list(entry.get("argv") or []), fixture_root=fixture_root
        )
        got = normalize_phd_output(out)
        ok = rc == 0
        if compare_stdout and golden.is_file():
            ok = ok and got == expected
        if compare_files and artifact_dir:
            errs = compare_phd_outputs(entry, out, artifact_dir)
            ok = ok and not errs
            fail_detail = errs[0] if errs else ""
        else:
            fail_detail = ""
        if ok:
            entry.pop("xfail_cpython", None)
            continue
        if fail_detail:
            reason = fail_detail
        elif compare_stdout and got != expected:
            reason = first_diff(expected, got)
        else:
            reason = f"exit code {rc}"
        entry["xfail_cpython"] = {"reason": reason}
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"updated {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())