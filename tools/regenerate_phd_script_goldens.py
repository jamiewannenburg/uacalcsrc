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
PHD = REPO / "tests" / "jython_scripts" / "phd"
GOLDENS = PHD / "goldens"
MANIFEST = PHD / "manifest.json"


def load_entries() -> list[dict]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return list(data["scripts"])


def run_jython(script: Path, argv: list[str], cwd: Path) -> tuple[int, str, str]:
    jython = os.environ.get("JYTHON", "jython")
    default_jar = (REPO / "jars" / "uacalc.jar").resolve()
    cp = os.environ.get("CLASSPATH", str(default_jar))
    vendor = REPO / "tests" / "jython_scripts" / "_vendor"
    env = os.environ.copy()
    env["CLASSPATH"] = cp
    env["PYTHONPATH"] = str(vendor)
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
        script = PHD / rel
        if not script.is_file():
            print(f"missing {script}", file=sys.stderr)
            return 2
        argv = list(entry.get("argv") or [])
        rc, out, err = run_jython(script, argv, PHD)
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