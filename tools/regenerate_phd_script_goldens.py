#!/usr/bin/env python3
"""Regenerate stdout goldens for tests/jython_scripts/phd using Jython + Java UACalc."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "tests" / "jython_scripts" / "phd_runtime"
GOLDENS = REPO / "tests" / "jython_scripts" / "phd" / "goldens"
MANIFEST = REPO / "tests" / "jython_scripts" / "phd" / "manifest.json"


def load_entries() -> list[dict]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return list(data["scripts"])


def run_jython(script: Path, argv: list[str], cwd: Path) -> tuple[int, str, str]:
    jython = os.environ.get("JYTHON", "jython")
    if jython == "jython" and sys.platform == "win32":
        candidates = [
            Path(r"C:\Users\u28409265\AppData\Local\Programs\Jython\bin\jython.exe"),
            Path(r"C:\Users\u28409265\AppData\Local\Programs\jython\bin\jython.exe"),
        ]
        for c in candidates:
            if c.is_file():
                jython = str(c)
                break
    default_jar = (REPO / "jars" / "uacalc.jar").resolve()
    cp = os.environ.get("CLASSPATH", str(default_jar))
    vendor = REPO / "tests" / "jython_scripts" / "_vendor"
    v2 = RUNTIME / "_vendor_pyparsing"
    pp = os.pathsep.join([str(v2), str(vendor)])
    env = os.environ.copy()
    env["CLASSPATH"] = cp
    env["PYTHONPATH"] = pp
    proc = subprocess.run(
        [jython, str(script), *argv],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env=env,
    )
    return proc.returncode, proc.stdout, proc.stderr


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", action="append", default=[])
    args = parser.parse_args()
    GOLDENS.mkdir(parents=True, exist_ok=True)
    for entry in load_entries():
        rel = entry["path"]
        if entry.get("skip_jython_golden"):
            print(f"skip {rel}: {entry['skip_jython_golden']}")
            continue
        if args.only and rel not in args.only:
            continue
        script = RUNTIME / rel
        if not script.is_file():
            print(f"missing {script}", file=sys.stderr)
            return 2
        argv = list(entry.get("argv") or [])
        cwd = RUNTIME
        if entry.get("cwd_model"):
            cwd = RUNTIME
        rc, out, err = run_jython(script, argv, cwd)
        if rc != 0:
            print(f"WARN {rel} exit {rc}", file=sys.stderr)
            if err:
                print(err[:800], file=sys.stderr)
        golden = GOLDENS / (Path(rel).name + ".stdout")
        golden.write_text(out, encoding="utf-8")
        print(f"golden {golden} ({len(out)} bytes, exit={rc})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())