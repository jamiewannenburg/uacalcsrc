#!/usr/bin/env python3
"""Print branch-only failures between two compare_pytest_not_slow.py failure lists."""

from __future__ import annotations

import argparse
from pathlib import Path


def read_lines(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    return {ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--branch", type=Path, required=True)
    args = parser.parse_args()
    base = read_lines(args.baseline)
    branch = read_lines(args.branch)
    only_branch = sorted(branch - base)
    only_base = sorted(base - branch)
    print(f"baseline_failures={len(base)}")
    print(f"branch_failures={len(branch)}")
    print(f"branch_only_failures={len(only_branch)}")
    print(f"baseline_only_failures={len(only_base)}")
    if only_branch:
        print("--- branch-only ---")
        for line in only_branch:
            print(line)
    if only_base:
        print("--- baseline-only (fixed on branch) ---")
        for line in only_base:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())