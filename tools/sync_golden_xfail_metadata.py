#!/usr/bin/env python3
"""Sync xfail_reason fields in golden JSON from parity case specs (metadata only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from generate_golden_data import load_test_cases  # noqa: E402

PACKAGES = (
    "alg",
    "example",
    "sublat",
    "lat",
    "io",
    "util",
    "terms",
    "parallel",
    "group",
    "eq",
    "element",
    "conlat",
    "alg_op",
    "fplat",
    "random",
)


def golden_paths(package: str) -> list[Path]:
    base = REPO_ROOT / "tests" / "parity" / package / "golden_data"
    if not base.is_dir():
        return []
    return sorted(base.glob("*_jython.json"))


def main() -> int:
    changed = 0
    for package in PACKAGES:
        try:
            specs = load_test_cases(package, None)
        except Exception as exc:
            print(f"skip package {package}: {exc}")
            continue
        by_id = {s.id: s.xfail_reason for s in specs}
        for gpath in golden_paths(package):
            data = json.loads(gpath.read_text(encoding="utf-8"))
            touched = False
            for tc in data.get("test_cases", []):
                tid = tc.get("id")
                if tid not in by_id:
                    continue
                new_val = by_id[tid]
                if tc.get("xfail_reason") != new_val:
                    tc["xfail_reason"] = new_val
                    touched = True
            if touched:
                gpath.write_text(
                    json.dumps(data, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                changed += 1
                print("updated", gpath.relative_to(REPO_ROOT))
    print(f"done ({changed} golden file(s) touched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())