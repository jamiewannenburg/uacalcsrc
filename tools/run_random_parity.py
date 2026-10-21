#!/usr/bin/env python3
"""Generate randomized parity goldens or sweep extra seeds against live Java.

Usage:
    python3 tools/run_random_parity.py generate
    python3 tools/run_random_parity.py sweep --seed-start 0 --count 500
    RANDOM_PARITY_SEEDS=1000 python3 tools/run_random_parity.py sweep

CI uses the checked-in seed list in jython_comparison/scripts/random_parity.py
and goldens under tests/parity/random/golden_data/. This tool is for
regenerating those goldens and for larger local live-Java sweeps.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "jython_comparison" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "python"))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from generate_golden_data import (  # noqa: E402
    build_classpath,
    extract_json,
    find_jython,
    generate_golden_for_package,
)
from random_parity import run_seed  # noqa: E402
from random_parity_config import (  # noqa: E402
    CI_SEEDS,
    KNOWN_JAVA_NPE_PATHS,
    LIBRARY_BUG_PREFIXES,
    XFAILS,
)


def _xfails_for_seed(seed: int) -> dict:
    return {path: reason for (s, path), reason in XFAILS.items() if int(s) == int(seed)}


def _path_xfailed(path: str, xfails: dict) -> bool:
    if path in xfails:
        return True
    return any(
        path == key or path.startswith(key + ".") or path.startswith(key + "[")
        for key in xfails
    )


def _known_java_npe(path, actual, expected) -> bool:
    if path not in KNOWN_JAVA_NPE_PATHS:
        return False
    return (
        isinstance(expected, dict)
        and expected.get("error") == "NullPointerException"
        and not (
            isinstance(actual, dict) and actual.get("error") == "NullPointerException"
        )
    )


def _library_bug_path(path: str) -> bool:
    for prefix in LIBRARY_BUG_PREFIXES:
        if path == prefix or path.startswith(prefix + ".") or path.startswith(prefix + "["):
            return True
    return False


def _walk_diffs(actual, expected, prefix=""):
    diffs = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        keys = sorted(set(list(expected.keys()) + list(actual.keys())))
        for key in keys:
            path = prefix + "." + key if prefix else key
            if key not in actual:
                diffs.append((path, "<missing>", expected[key]))
            elif key not in expected:
                diffs.append((path, actual[key], "<missing>"))
            else:
                diffs.extend(_walk_diffs(actual[key], expected[key], path))
        return diffs
    if isinstance(expected, list) and isinstance(actual, list):
        n = max(len(actual), len(expected))
        for i in range(n):
            path = "{0}[{1}]".format(prefix, i)
            if i >= len(actual):
                diffs.append((path, "<missing>", expected[i]))
            elif i >= len(expected):
                diffs.append((path, actual[i], "<missing>"))
            else:
                diffs.extend(_walk_diffs(actual[i], expected[i], path))
        return diffs
    if actual != expected:
        diffs.append((prefix or "<root>", actual, expected))
    return diffs


def cmd_generate(_args: argparse.Namespace) -> int:
    generate_golden_for_package("random")
    return 0


def _jython_batch(start: int, count: int) -> list:
    jython = find_jython()
    if not jython:
        print("ERROR: Jython not found. Install Jython 2.7.x or set JYTHON.", file=sys.stderr)
        sys.exit(1)
    script = textwrap.dedent(
        """
        import json, sys, os
        sys.path.insert(0, os.path.join({root!r}, "jython_comparison", "scripts"))
        from random_parity import run_seed
        start = int(sys.argv[1]); count = int(sys.argv[2])
        out = []
        for seed in range(start, start + count):
            try:
                result = run_seed(seed)
                out.append({{"seed": seed, "result": result}})
            except Exception:
                e = sys.exc_info()[1]
                out.append({{"seed": seed, "error": type(e).__name__ + ": " + str(e)}})
        print("---GOLDEN_JSON_BEGIN---")
        print(json.dumps(out))
        print("---GOLDEN_JSON_END---")
        """
    ).format(root=str(REPO_ROOT))
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as handle:
        handle.write(script)
        script_path = handle.name
    env = os.environ.copy()
    env["CLASSPATH"] = build_classpath()
    env["PYTHONPATH"] = ""
    try:
        proc = subprocess.run(
            [jython, script_path, str(start), str(count)],
            capture_output=True,
            text=True,
            timeout=max(180, 10 * count),
            env=env,
            cwd=str(REPO_ROOT),
        )
    finally:
        Path(script_path).unlink(missing_ok=True)
    if proc.returncode != 0 and not proc.stdout:
        print("ERROR: Jython sweep failed:\n{0}".format(proc.stderr), file=sys.stderr)
        sys.exit(1)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
        if not proc.stderr.endswith("\n"):
            sys.stderr.write("\n")
    return extract_json(proc.stdout)


def cmd_sweep(args: argparse.Namespace) -> int:
    start = int(args.seed_start)
    count = int(args.count)
    print("Sweeping seeds [{0}, {1}) against live Java ({2} seeds)".format(
        start, start + count, count
    ))
    java_rows = _jython_batch(start, count)
    java_by_seed = {}
    java_errors = []
    for row in java_rows:
        seed = int(row["seed"])
        if row.get("error"):
            java_errors.append((seed, row["error"]))
        else:
            java_by_seed[seed] = row["result"]
    mismatches = []
    py_errors = []
    matched = 0
    xfailed = 0
    for seed in range(start, start + count):
        try:
            py = run_seed(seed)
        except Exception as exc:
            py_errors.append((seed, type(exc).__name__ + ": " + str(exc)))
            continue
        java = java_by_seed.get(seed)
        if java is None:
            continue
        diffs = _walk_diffs(py, java)
        xfails = _xfails_for_seed(seed)
        unexpected = [
            d
            for d in diffs
            if not _path_xfailed(d[0], xfails)
            and not _known_java_npe(d[0], d[1], d[2])
            and not _library_bug_path(d[0])
        ]
        used = [d for d in diffs if _path_xfailed(d[0], xfails)]
        if used and not unexpected:
            xfailed += 1
        if unexpected:
            mismatches.append((seed, unexpected[:8]))
        elif not diffs:
            matched += 1
        else:
            matched += 1
    print("matched={0} xfail_only={1} mismatches={2} java_errors={3} python_errors={4}".format(
        matched, xfailed, len(mismatches), len(java_errors), len(py_errors)
    ))
    for seed, err in java_errors[:20]:
        print("  JAVA seed {0}: {1}".format(seed, err))
    for seed, err in py_errors[:20]:
        print("  PYTHON seed {0}: {1}".format(seed, err))
    for seed, diffs in mismatches[:40]:
        n, arities = None, None
        try:
            from random_parity import family_for_seed
            n, arities = family_for_seed(seed)
        except Exception:
            pass
        print("  MISMATCH seed {0} n={1} arities={2}".format(seed, n, arities))
        for path, act, exp in diffs:
            print("    {0}".format(path))
            print("      python: {0}".format(json.dumps(act, sort_keys=True, default=str)[:240]))
            print("      java:   {0}".format(json.dumps(exp, sort_keys=True, default=str)[:240]))
    if len(mismatches) > 40:
        print("  ... {0} more mismatched seeds".format(len(mismatches) - 40))
    return 1 if mismatches or java_errors or py_errors else 0


def cmd_ci_seeds(_args: argparse.Namespace) -> int:
    print(" ".join(str(s) for s in CI_SEEDS))
    print("count={0}".format(len(CI_SEEDS)))
    return 0


def main() -> int:
    env_count = os.environ.get("RANDOM_PARITY_SEEDS")
    env_start = os.environ.get("RANDOM_PARITY_SEED_START")
    parser = argparse.ArgumentParser(description="Randomized Java/Python parity")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_gen = sub.add_parser("generate", help="Write Jython goldens for CI seeds")
    p_gen.set_defaults(func=cmd_generate)
    p_sw = sub.add_parser("sweep", help="Compare many seeds against live Java")
    p_sw.add_argument("--seed-start", type=int, default=int(env_start or "0"))
    p_sw.add_argument("--count", type=int, default=int(env_count or "200"))
    p_sw.set_defaults(func=cmd_sweep)
    p_ci = sub.add_parser("ci-seeds", help="Print the checked-in CI seed list")
    p_ci.set_defaults(func=cmd_ci_seeds)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
