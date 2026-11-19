#!/usr/bin/env python3
"""Print stderr / first stdout diff for manifest xfail candidates."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests" / "jython_scripts"))
from harness import FIXTURES_ROOT, compare_phd_outputs, normalize_phd_output, run_phd_script_cpython  # noqa: E402

MANIFEST = REPO / "tests" / "jython_scripts" / "phd" / "manifest.json"
GOLDENS = REPO / "tests" / "jython_scripts" / "phd" / "goldens"


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in data["scripts"]:
        if not entry.get("xfail_cpython") and entry["path"] != "probes/nullary_string_to_term.py":
            continue
        rel = entry["path"]
        argv = list(entry.get("argv") or [])
        fixture_root = FIXTURES_ROOT if entry.get("use_fixture_copy") else None
        rc, out, err, artifact_dir = run_phd_script_cpython(rel, argv, fixture_root=fixture_root)
        print("===", rel, "rc=", rc)
        if err.strip():
            for line in err.strip().splitlines()[:8]:
                print("  ", line)
        if entry.get("compare_stdout", True):
            golden = GOLDENS / (Path(rel).name + ".stdout")
            if golden.is_file():
                exp = normalize_phd_output(golden.read_text(encoding="utf-8"))
                got = normalize_phd_output(out)
                if got != exp:
                    el, gl = exp.splitlines(), got.splitlines()
                    for i, (e, g) in enumerate(zip(el, gl)):
                        if e != g:
                            print(f"  stdout line {i+1} jython={e!r} cpython={g!r}")
                            break
                    else:
                        print(f"  stdout line count jython={len(el)} cpython={len(gl)}")
        if entry.get("compare_files") and artifact_dir:
            errs = compare_phd_outputs(entry, out, artifact_dir)
            for e in errs:
                print(" ", e)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())