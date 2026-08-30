#!/usr/bin/env python3
"""Run all contract-linked parity scripts under Jython and CPython; diff stdout."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from jython_contracts.registry import collect_script_entries, load_all_contracts  # noqa: E402


def run_cmd(cmd, env, cwd):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd),
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def filter_lines(text: str, ignore_prefixes):
    lines = []
    for line in text.splitlines():
        if any(line.startswith(prefix) for prefix in ignore_prefixes):
            continue
        lines.append(line)
    return lines


def compare_script(script_path: str, ignore_lines, cwd: Path) -> bool:
    print(f"\n=== {script_path} ===")

    jython_env = os.environ.copy()
    jython_env["CLASSPATH"] = str(cwd / "jars" / "uacalc.jar")
    jython_env["PYTHONPATH"] = ""

    python_env = os.environ.copy()
    python_env["PYTHONPATH"] = f"{cwd / 'python'}:{cwd / 'python' / 'uacalc_lib'}"

    jython_bin = os.environ.get("JYTHON", "jython")
    python_bin = cwd / "venv" / "bin" / "python3"
    if not python_bin.exists():
        python_bin = Path(sys.executable)

    j_out, j_err, j_rc = run_cmd(f"{jython_bin} {script_path}", jython_env, cwd)
    p_out, p_err, p_rc = run_cmd(f"{python_bin} {script_path}", python_env, cwd)

    print("--- JYTHON ---")
    print(j_out)
    if j_err:
        print("ERR:", j_err)
    print("--- PYTHON ---")
    print(p_out)
    if p_err:
        print("ERR:", p_err)

    if j_rc != 0 or p_rc != 0:
        print(f"FAILURE: non-zero exit (jython={j_rc}, python={p_rc})")
        return False

    if j_out == p_out:
        print("SUCCESS: Outputs match perfectly!")
        return True

    j_lines = filter_lines(j_out, ignore_lines)
    p_lines = filter_lines(p_out, ignore_lines)
    if j_lines == p_lines:
        print("SUCCESS: Core outputs match (ignored prefixes excluded)!")
        return True

    print("FAILURE: Outputs differ.")
    return False


def main():
    cwd = PROJECT_ROOT
    contracts = load_all_contracts()
    scripts = collect_script_entries(contracts)

    if not scripts:
        # Fallback for early bootstrap
        scripts = [
            {
                "path": "jython_comparison/scripts/load_cyclic2.py",
                "ignore_lines": ["Universe:"],
            }
        ]

    ok = True
    for script in scripts:
        path = script["path"]
        ignore = script.get("ignore_lines") or []
        if not (cwd / path).is_file():
            print(f"FAILURE: missing script {path}")
            ok = False
            continue
        if not compare_script(path, ignore, cwd):
            ok = False

    print("\n--- SUMMARY ---")
    if ok:
        print("All parity scripts matched.")
        return 0
    print("One or more parity scripts failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
