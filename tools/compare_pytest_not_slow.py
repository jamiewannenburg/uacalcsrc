#!/usr/bin/env python3
"""Run pytest -m 'not slow' and write failed nodeids (one per line)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_pytest(cwd: Path, junit_path: Path, python_exe: str) -> int:
    junit_path.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    py_src = cwd / "python"
    if py_src.is_dir():
        env["PYTHONPATH"] = os.pathsep.join([str(py_src), env.get("PYTHONPATH", "")]).strip(
            os.pathsep
        )
    cmd = [
        python_exe,
        "-m",
        "pytest",
        "python/uacalc/tests",
        "-m",
        "not slow",
        "--tb=no",
        "-q",
        f"--junitxml={junit_path}",
    ]
    return subprocess.run(cmd, cwd=cwd, check=False, env=env).returncode


def parse_failures(junit_path: Path) -> list[str]:
    if not junit_path.is_file():
        return []
  # stdlib only: minimal XML scan
    import xml.etree.ElementTree as ET

    root = ET.parse(junit_path).getroot()
    failed: list[str] = []
    for case in root.iter("testcase"):
        if case.find("failure") is not None or case.find("error") is not None:
            cls = case.get("classname", "")
            name = case.get("name", "")
            failed.append(f"{cls}::{name}" if cls else name)
    return sorted(failed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", type=Path, default=_repo_root())
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--junit-out", type=Path, required=True)
    parser.add_argument("--failures-out", type=Path, required=True)
    args = parser.parse_args()
    rc = run_pytest(args.cwd, args.junit_out, args.python)
    failures = parse_failures(args.junit_out)
    args.failures_out.write_text("\n".join(failures) + ("\n" if failures else ""), encoding="utf-8")
    print(f"pytest exit={rc}, failures={len(failures)}")
    print(f"wrote {args.failures_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())