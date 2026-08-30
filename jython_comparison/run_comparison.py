#!/usr/bin/env python3
"""
Run the same script under Jython (Java UACalc on CLASSPATH) and CPython (org.uacalc shims)
and compare normalized stdout.

With no ``--script``, runs every ``testing.scripts`` entry from ``jython_contracts/``.

Environment variables
---------------------
CLASSPATH
    JARs for Jython (default: ``./jars/uacalc.jar`` under the repo root). Passed to the
    Jython subprocess; must include ``uacalc.jar`` so ``org.uacalc.*`` resolves.

PYTHONPATH
    For the CPython run, the script sets ``python`` and ``python/uacalc_lib`` (or your
    ``--pythonpath``) so ``import org.uacalc`` and ``uacalc_lib`` work. For Jython it
    clears ``PYTHONPATH`` by default so the real Java packages are used instead of the
    repo shims.

JYTHON
    Executable for Jython (default: ``jython`` on ``PATH``).

UACALC_PYTHON
    CPython interpreter (default: ``sys.executable`` when this file is run with Python).

Exit codes: 0 if outputs match (optionally ignoring Universe lines), 1 on mismatch or
subprocess failure, 2 on bad arguments or missing script.

Use in CI: run with default script or ``--script``; exit code 1 fails the job on diff or
non-zero subprocess exit.
"""

from __future__ import annotations

import argparse
import difflib
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))


def _repo_root() -> Path:
    return PROJECT_ROOT


def _default_classpath(repo: Path) -> str:
    return str(repo / "jars" / "uacalc.jar")


def _default_pythonpath(repo: Path) -> str:
    return os.pathsep.join(
        [
            str(repo / "python"),
            str(repo / "python" / "uacalc_lib"),
        ]
    )


def run_cmd(
    argv: list[str],
    env: dict[str, str],
) -> tuple[int, str, str]:
    result = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(_repo_root()),
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def filter_lines(text: str, ignore_prefixes: list[str]) -> list[str]:
    lines = []
    for line in text.splitlines():
        if any(line.startswith(prefix) for prefix in ignore_prefixes):
            continue
        lines.append(line)
    return lines


def compare_outputs(
    jython_out: str,
    python_out: str,
    *,
    ignore_prefixes: list[str] | None = None,
    ignore_universe_line: bool = False,
) -> tuple[bool, str, str]:
    """
    Returns (match, normalized_jython, normalized_python) for optional diff printing.
    """
    if jython_out == python_out:
        return True, jython_out, python_out

    prefixes = list(ignore_prefixes or [])
    if ignore_universe_line and "Universe:" not in prefixes:
        prefixes.append("Universe:")
    if not prefixes:
        return False, jython_out, python_out

    j_norm = "\n".join(filter_lines(jython_out, prefixes))
    p_norm = "\n".join(filter_lines(python_out, prefixes))
    return j_norm == p_norm, j_norm, p_norm


def parse_args(repo: Path) -> argparse.Namespace:
    epilog = """Environment variables (CLI flags override when listed):
  CLASSPATH     JARs for Jython (see --classpath). Must include uacalc.jar.
  PYTHONPATH    Used for CPython run if --pythonpath not passed (default: repo python/).
  JYTHON        Jython executable (default: jython).
  UACALC_PYTHON CPython interpreter (default: same as invoking python).

Examples:
  python jython_comparison/run_comparison.py
  python jython_comparison/run_comparison.py --script jython_comparison/test_script.py --quiet
"""
    p = argparse.ArgumentParser(
        description=(
            "Compare Jython vs CPython stdout for a parity script "
            "(default: all jython_contracts testing.scripts entries)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog,
    )
    p.add_argument(
        "--script",
        type=Path,
        default=None,
        help=(
            "Script path relative to repo root or absolute. "
            "Default: run all contract-linked scripts "
            "(e.g. jython_comparison/test_script.py)."
        ),
    )
    p.add_argument(
        "--jython",
        default=os.environ.get("JYTHON", "jython"),
        help="Jython executable (default: env JYTHON or 'jython').",
    )
    p.add_argument(
        "--python",
        default=os.environ.get("UACALC_PYTHON", sys.executable),
        help="CPython executable (default: env UACALC_PYTHON or sys.executable).",
    )
    p.add_argument(
        "--classpath",
        default=os.environ.get("CLASSPATH", _default_classpath(repo)),
        help="CLASSPATH for Jython (default: env CLASSPATH or ./jars/uacalc.jar).",
    )
    p.add_argument(
        "--pythonpath",
        default=os.environ.get("PYTHONPATH", _default_pythonpath(repo)),
        help="PYTHONPATH for CPython run (default: python + python/uacalc_lib).",
    )
    p.add_argument(
        "--no-ignore-universe",
        action="store_true",
        help="Do not strip lines starting with 'Universe:' when comparing.",
    )
    p.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Print only errors and the final status line.",
    )
    p.add_argument(
        "--diff",
        action="store_true",
        help="On mismatch, print a unified diff of normalized stdout (stderr).",
    )
    return p.parse_args()


def _resolve_python_bin(repo: Path, explicit: str) -> str:
    if explicit and explicit != sys.executable:
        return explicit
    venv_py = repo / "venv" / "bin" / "python3"
    if venv_py.exists():
        return str(venv_py)
    return explicit or sys.executable


def compare_one_script(
    script: Path,
    *,
    repo: Path,
    args: argparse.Namespace,
    ignore_prefixes: list[str] | None = None,
) -> bool:
    ignore_u = not args.no_ignore_universe
    prefixes = list(ignore_prefixes or [])
    if ignore_u and "Universe:" not in prefixes:
        prefixes.append("Universe:")

    jython_env = os.environ.copy()
    jython_env["CLASSPATH"] = args.classpath
    jython_env["PYTHONPATH"] = ""

    py_env = os.environ.copy()
    py_env["PYTHONPATH"] = args.pythonpath

    python_bin = _resolve_python_bin(repo, args.python)

    if not args.quiet:
        print(f"\n=== {script} ===")
        print("Running Jython...")
    j_code, jython_out, jython_err = run_cmd([args.jython, str(script)], jython_env)
    if not args.quiet:
        print("Running Python...")
    p_code, python_out, python_err = run_cmd([python_bin, str(script)], py_env)

    if not args.quiet:
        print("\n--- JYTHON OUTPUT ---")
        print(jython_out)
        if jython_err:
            print("ERR: " + jython_err)

        print("\n--- PYTHON OUTPUT ---")
        print(python_out)
        if python_err:
            print("ERR: " + python_err)

    match, j_cmp, p_cmp = compare_outputs(
        jython_out,
        python_out,
        ignore_prefixes=prefixes,
        ignore_universe_line=False,
    )
    ok = j_code == 0 and p_code == 0 and match

    if not args.quiet:
        print("\n--- COMPARISON ---")
    if ok:
        if not args.quiet:
            print(
                "SUCCESS: Outputs match"
                + ("" if jython_out == python_out else " (ignored prefixes excluded)!")
            )
        return True

    if args.diff and j_code == 0 and p_code == 0 and not match:
        diff = difflib.unified_diff(
            j_cmp.splitlines(),
            p_cmp.splitlines(),
            fromfile="jython",
            tofile="cpython",
            lineterm="",
        )
        print("\n".join(diff), file=sys.stderr)

    if not args.quiet:
        print("FAILURE: Outputs differ or a subprocess failed.")
    if j_code != 0:
        print(f"Jython exit code: {j_code}", file=sys.stderr)
    if p_code != 0:
        print(f"Python exit code: {p_code}", file=sys.stderr)
    if j_code == 0 and p_code == 0:
        print(
            "Stdout mismatch after comparison rules "
            f"(ignore_prefixes={prefixes!r}).",
            file=sys.stderr,
        )
    return False


def _contract_script_entries() -> list[dict]:
    from jython_contracts.registry import (  # noqa: E402
        collect_script_entries,
        load_all_contracts,
    )

    contracts = load_all_contracts()
    scripts = collect_script_entries(contracts)
    if scripts:
        return scripts
    # Fallback for early bootstrap
    return [
        {
            "path": "jython_comparison/scripts/load_cyclic2.py",
            "ignore_lines": ["Universe:"],
        }
    ]


def main() -> int:
    repo = _repo_root()
    args = parse_args(repo)

    if args.script is not None:
        script = args.script
        if not script.is_absolute():
            candidate = repo / script
            if candidate.is_file():
                script = candidate
        if not script.is_file():
            print(f"Script not found: {script}", file=sys.stderr)
            return 2
        return 0 if compare_one_script(script, repo=repo, args=args) else 1

    entries = _contract_script_entries()
    ok = True
    for entry in entries:
        path = entry["path"]
        ignore = entry.get("ignore_lines") or []
        script = repo / path
        if not script.is_file():
            print(f"FAILURE: missing script {path}", file=sys.stderr)
            ok = False
            continue
        if not compare_one_script(
            script, repo=repo, args=args, ignore_prefixes=list(ignore)
        ):
            ok = False

    if not args.quiet:
        print("\n--- SUMMARY ---")
        if ok:
            print("All parity scripts matched.")
        else:
            print("One or more parity scripts failed.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
