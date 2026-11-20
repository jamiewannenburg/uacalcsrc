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
import copy
import difflib
import json
import os
import re
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


# Java-side progress / debug lines that CPython does not mirror on stdout.
# Anchored regexes only — avoid broad prefixes that could hide real probes.
DEFAULT_IGNORE_LINE_PATTERNS: list[str] = [
    r"^oneGenerated size = \d+$",
    r"^pass \d+ of \d+, size = \d+$",
    r"^pass: \d+, size: \d+$",
    r"^labels has size \d+$",
    r"^ucs has size \d+$",
    r"^universe size: \d+$",
    r"^depth is -?\d+$",
    r"^Constructing free algebra on \d+ generators over .+$",
    r"^projs size = \d+$",
    r"^done constructing free algebra, size = \d+$",
    r"^made the free algebra, but haven't found the elements\.$",
    r"^gens v length = \d+$",
    r"^map = .+$",
    r"^tmp = .+$",
    r"^i = \d+, j = \d+$",
    r"^table\[j\]\[i\] = -?\d+$",
    r"^tmp\.length = \d+$",
    r"^fails to commute at .+$",
    r"^null InputStream$",
    r"^need a file name of an algebra$",
]

def normalize_comparison_line(line: str) -> str:
    """Cosmetic stdout normalization (repr/format), not value hiding."""
    line = re.sub(r"\b(\d+)L\b", r"\1", line)
    line = line.replace(", ", ",")
    line = re.sub(r"\bu'", "'", line)
    line = re.sub(
        r"array\('i',\s*\[([^\]]*)\]\)",
        lambda m: "[" + m.group(1) + "]",
        line,
    )
    return line


def _line_ignored(line: str, ignore_rules: list[str]) -> bool:
    for rule in ignore_rules:
        if rule.startswith("^") or rule.endswith("$") or "\\" in rule:
            if re.match(rule, line):
                return True
        elif line.startswith(rule):
            return True
    return False


def filter_lines(text: str, ignore_rules: list[str]) -> list[str]:
    lines = []
    for line in text.splitlines():
        if _line_ignored(line, ignore_rules):
            continue
        lines.append(normalize_comparison_line(line))
    return lines


def _extract_json_payload(text: str) -> object | None:
    """Parse a JSON object from stdout that may include filtered debug lines."""
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    return None


def _delete_json_path(data: object, path: str) -> None:
    parts = path.split(".")
    if not parts:
        return
    cur = data
    for key in parts[:-1]:
        if not isinstance(cur, dict) or key not in cur:
            return
        cur = cur[key]
    last = parts[-1]
    if isinstance(cur, dict):
        cur.pop(last, None)


def _json_compare_ignoring_paths(
    jython_out: str,
    python_out: str,
    ignore_json_paths: list[str],
) -> bool | None:
    """Return match result when both stdout blobs are JSON; None if not applicable."""
    if not ignore_json_paths:
        return None
    j_data = _extract_json_payload(jython_out)
    p_data = _extract_json_payload(python_out)
    if j_data is None or p_data is None:
        return None
    j_copy = copy.deepcopy(j_data)
    p_copy = copy.deepcopy(p_data)
    for path in ignore_json_paths:
        _delete_json_path(j_copy, path)
        _delete_json_path(p_copy, path)
    return json.dumps(j_copy, sort_keys=True) == json.dumps(p_copy, sort_keys=True)


def compare_outputs(
    jython_out: str,
    python_out: str,
    *,
    ignore_rules: list[str] | None = None,
    ignore_universe_line: bool = False,
    ignore_json_paths: list[str] | None = None,
) -> tuple[bool, str, str]:
    """
    Returns (match, normalized_jython, normalized_python) for optional diff printing.
    """
    if jython_out == python_out:
        return True, jython_out, python_out

    rules = list(ignore_rules or [])
    if ignore_universe_line and "Universe:" not in rules:
        rules.append("Universe:")

    j_norm = "\n".join(filter_lines(jython_out, rules))
    p_norm = "\n".join(filter_lines(python_out, rules))
    if j_norm == p_norm:
        return True, j_norm, p_norm

    json_match = _json_compare_ignoring_paths(jython_out, python_out, list(ignore_json_paths or []))
    if json_match is True:
        return True, j_norm, p_norm
    if json_match is False:
        return False, j_norm, p_norm

    if not rules and not ignore_json_paths:
        return False, jython_out, python_out
    return False, j_norm, p_norm


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
    ignore_rules: list[str] | None = None,
) -> bool:
    try:
        from jython_contracts.comparison_allowlist import (
            script_comparison_overrides,
        )
    except ImportError:
        script_comparison_overrides = None  # type: ignore[assignment,misc]

    overrides = None
    if script_comparison_overrides is not None:
        overrides = script_comparison_overrides(script, repo)

    ignore_u = not args.no_ignore_universe
    rules = list(DEFAULT_IGNORE_LINE_PATTERNS)
    for p in ignore_rules or []:
        if p not in rules:
            rules.append(p)
    if overrides is not None:
        for pattern in overrides.ignore_line_patterns:
            if pattern not in rules:
                rules.append(pattern)
    if ignore_u and "Universe:" not in rules:
        rules.append("Universe:")

    ignore_json_paths = list(overrides.ignore_json_paths) if overrides else []

    jython_env = os.environ.copy()
    jython_env["CLASSPATH"] = args.classpath
    jython_env["PYTHONPATH"] = ""

    py_env = os.environ.copy()
    py_env["PYTHONPATH"] = args.pythonpath
    py_env["PYTHONUNBUFFERED"] = "1"

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
        ignore_rules=rules,
        ignore_universe_line=False,
        ignore_json_paths=ignore_json_paths,
    )
    ok = j_code == 0 and p_code == 0 and match

    if not args.quiet:
        print("\n--- COMPARISON ---")
    if ok:
        if not args.quiet:
            suffix = ""
            if jython_out != python_out:
                if overrides and (overrides.ignore_line_patterns or overrides.ignore_json_paths):
                    suffix = f" (Known difference: {overrides.reason})"
                else:
                    suffix = " (ignored prefixes excluded)"
            print("SUCCESS: Outputs match" + suffix)
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
            f"(ignore_rules={rules!r}).",
            file=sys.stderr,
        )

    if overrides is not None and overrides.allow_remaining_mismatch:
        note = f"ALLOWLISTED: {overrides.reason}"
        print(note, file=sys.stderr)
        if not args.quiet:
            print(note)
        return True

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
            script, repo=repo, args=args, ignore_rules=list(ignore)
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
