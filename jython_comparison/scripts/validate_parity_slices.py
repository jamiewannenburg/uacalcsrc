# coding: utf-8
#!/usr/bin/env python3
"""
Validate jython_comparison/parity_slices.yaml against parity_inventory.yaml without PyYAML.

Checks:
- Every java_package_prefix in parity_slices appears as a package or prefix of a package
  in parity_inventory.yaml's `packages:` section.
- Every ``depends_on:`` entry references a slice ``id`` defined in the same file (catches
  typos like ``core-ioo`` vs ``core-io``). Package names belong under
  ``java_package_prefixes``, not under ``depends_on``.
- Slice ``id:`` values are unique (duplicate rows break ownership tracking).
- Slice ``id:`` values use kebab-case (letters, digits, hyphens) and must not look like
  Java package names (no ``org.`` / dots)-those belong under ``java_package_prefixes``.
- ``depends_on`` list items that look like Java package names (e.g. ``org.uacalc...``)
  are flagged-those belong under ``java_package_prefixes``, not ``depends_on``.

Exit code 0 on success, 1 on validation errors, 2 on missing files.
"""

from __future__ import annotations

import difflib
import re
import sys
from collections import Counter
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


def _load_slice_ids_ordered(slices_path: Path) -> list[str]:
    ids: list[str] = []
    for line in slices_path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s+- id:\s+(\S+)\s*$", line)
        if m:
            ids.append(m.group(1))
    return ids


def _duplicate_slice_id_errors(ids: list[str]) -> list[str]:
    counts = Counter(ids)
    dupes = sorted(k for k, v in counts.items() if v > 1)
    if not dupes:
        return []
    return [
        "Duplicate '- id:' values in parity_slices.yaml (must be unique): "
        + ", ".join(repr(x) for x in dupes)
    ]


def _slice_id_format_errors(ids: list[str]) -> list[str]:
    """
    Slice ids must be kebab-case labels (e.g. ``core-io``), not Java package paths.

    Catches typos like ``- id: org.uacalc.io`` where the author confused ``id`` with
    ``java_package_prefixes``.
    """
    errs: list[str] = []
    kebab = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
    for sid in ids:
        if "." in sid or sid.startswith("org") and "uacalc" in sid:
            errs.append(
                f"Slice id {sid!r} looks like a Java package or dotted path. "
                "Use a kebab-case slice id (e.g. core-io) under '- id:', and put "
                "org.uacalc.* under java_package_prefixes:."
            )
            continue
        if not kebab.match(sid):
            errs.append(
                f"Slice id {sid!r} should match kebab-case "
                r"^[a-z0-9]+(-[a-z0-9]+)*$ (letters, digits, single hyphens between tokens)."
            )
    return errs


def _depends_on_package_name_errors(slices_path: Path) -> list[str]:
    """
    Flag ``depends_on`` entries that look like inventory package names instead of slice ids.

    Slice ids are kebab-case (``core-io``); Java packages contain ``org.uacalc``.
    """
    lines = slices_path.read_text(encoding="utf-8", errors="replace").splitlines()
    errs: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m_dep = re.match(r"^(\s*)depends_on:\s*$", line)
        if m_dep:
            base_indent = len(m_dep.group(1))
            i += 1
            while i < len(lines):
                line2 = lines[i]
                if not line2.strip():
                    i += 1
                    continue
                ws = len(line2) - len(line2.lstrip())
                if ws <= base_indent:
                    break
                mm = re.match(r"^\s+-\s+(\S+)\s*$", line2)
                if mm:
                    dep = mm.group(1)
                    if "org.uacalc" in dep or dep.startswith("org."):
                        errs.append(
                            f"depends_on lists {dep!r}, which looks like a Java package / "
                            "inventory path. Use a slice id (e.g. core-io), not org.uacalc.*."
                        )
                i += 1
            continue
        i += 1
    return errs


def _depends_on_errors(slices_path: Path, slice_ids: set[str]) -> list[str]:
    """Unknown ``depends_on`` targets (slice id typos)."""
    lines = slices_path.read_text(encoding="utf-8", errors="replace").splitlines()
    errs: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m_dep = re.match(r"^(\s*)depends_on:\s*$", line)
        if m_dep:
            base_indent = len(m_dep.group(1))
            i += 1
            while i < len(lines):
                line2 = lines[i]
                if not line2.strip():
                    i += 1
                    continue
                ws = len(line2) - len(line2.lstrip())
                if ws <= base_indent:
                    break
                mm = re.match(r"^\s+-\s+(\S+)\s*$", line2)
                if mm:
                    dep = mm.group(1)
                    if dep not in slice_ids:
                        suggest = difflib.get_close_matches(
                            dep, sorted(slice_ids), n=3, cutoff=0.55
                        )
                        hint = (
                            f" Did you mean {suggest[0]!r}?"
                            if len(suggest) == 1
                            else (f" Close matches: {suggest}." if suggest else "")
                        )
                        errs.append(
                            f"depends_on references unknown slice id {dep!r} (not listed under "
                            f"\"- id:\").{hint}"
                        )
                i += 1
            continue
        i += 1
    return errs


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
    slice_ids_list = _load_slice_ids_ordered(sl)
    slice_ids = set(slice_ids_list)
    if not slice_ids:
        print("No slice ids parsed from parity_slices.yaml (- id:)", file=sys.stderr)
        return 2

    prefixes = _load_slice_prefixes(sl)
    errs: list[str] = []
    errs.extend(_duplicate_slice_id_errors(slice_ids_list))
    errs.extend(_slice_id_format_errors(slice_ids_list))
    for pref in prefixes:
        if pref in pkgs:
            continue
        if any(p == pref or p.startswith(pref + ".") for p in pkgs):
            continue
        suggestions = difflib.get_close_matches(pref, sorted(pkgs), n=3, cutoff=0.45)
        hint = (
            f" (similar inventory packages: {', '.join(suggestions)})"
            if suggestions
            else ""
        )
        errs.append(
            f"parity_slices.yaml: java_package_prefix {pref!r} not found in "
            f"parity_inventory.yaml packages.{hint}"
        )
    errs.extend(_depends_on_errors(sl, slice_ids))
    errs.extend(_depends_on_package_name_errors(sl))
    if errs:
        for e in errs:
            print(e, file=sys.stderr)
        return 1
    print(
        f"OK: {len(prefixes)} java_package_prefix entries validated against {len(pkgs)} "
        f"inventory packages; {len(slice_ids)} slice ids; depends_on targets checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
