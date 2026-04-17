#!/usr/bin/env python3
"""
Validate jython_comparison/parity_slices.yaml against parity_inventory.yaml without PyYAML.

Checks:
- Every java_package_prefix in parity_slices appears as a package or prefix of a package
  in parity_inventory.yaml's `packages:` section.

Exit code 0 on success, 1 on validation errors, 2 on missing files.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_inventory_packages(inv_path: Path) -> set[str]:
    text = inv_path.read_text(encoding="utf-8", errors="replace")
    pkgs: set[str] = set()
    for line in text.splitlines():
        # Keys under packages: are indented two spaces, end with :
        m = re.match(r"^  (org\.uacalc[\w.]*):\s*$", line)
        if m:
            pkgs.add(m.group(1))
    return pkgs


def _load_slice_prefixes(slices_path: Path) -> list[str]:
    """Collect list items that look like org.uacalc.* (used under java_package_prefixes)."""
    text = slices_path.read_text(encoding="utf-8", errors="replace")
    prefixes: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^\s+-\s+(org\.uacalc[\w.]*)\s*$", line)
        if m:
            prefixes.append(m.group(1))
    return prefixes


def main() -> int:
    repo = _repo_root()
    inv = repo / "jython_comparison" / "parity_inventory.yaml"
    sl = repo / "jython_comparison" / "parity_slices.yaml"
    if not inv.is_file() or not sl.is_file():
        print("Missing parity_inventory.yaml or parity_slices.yaml", file=sys.stderr)
        return 2
    pkgs = _load_inventory_packages(inv)
    if not pkgs:
        print("No packages parsed from parity_inventory.yaml", file=sys.stderr)
        return 2
    prefixes = _load_slice_prefixes(sl)
    errs: list[str] = []
    for pref in prefixes:
        if pref in pkgs:
            continue
        if any(p == pref or p.startswith(pref + ".") for p in pkgs):
            continue
        errs.append(f"java_package_prefix not found in inventory: {pref}")
    if errs:
        for e in errs:
            print(e, file=sys.stderr)
        return 1
    print(f"OK: {len(prefixes)} java_package_prefix entries validated against {len(pkgs)} inventory packages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
