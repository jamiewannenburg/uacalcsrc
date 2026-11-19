#!/usr/bin/env python3
"""Sync Jamie's small files into tests/jython_scripts/phd_runtime for harness/CI."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

# Reuse Jamie tree rules from inventory
from phd_script_inventory import SRC, VENDOR, copy_phd_tree, should_skip_path

REPO = Path(__file__).resolve().parents[1]
DEST = REPO / "tests" / "jython_scripts" / "phd_runtime"
READ_ME = (
    "Mirror of Jamie's read-only ~/uacalc tree (top-level .py, jars, input via symlink locally).\n"
    "Regenerate: python tools/sync_phd_runtime.py\n"
)


def _copy_required_inputs() -> None:
    inv = REPO / "tools" / "phd_script_argv.json"
    argv_map = json.loads(inv.read_text(encoding="utf-8"))
    dest_in = DEST / "input"
    dest_in.mkdir(exist_ok=True)
    tokens: set[str] = set()
    for argv in argv_map.values():
        for tok in argv:
            if tok.startswith("-"):
                continue
            if "*" in tok:
                for p in (SRC / "input").glob(tok.replace("input/", "")):
                    if not should_skip_path(p):
                        shutil.copy2(p, dest_in / p.name)
            elif any(tok.endswith(ext) for ext in (".ua", ".model", ".in", ".json")):
                tokens.add(tok.replace("input/", ""))
            elif "/" not in tok and "\\" not in tok:
                tokens.add(f"{tok}.ua")
    inv = REPO / "tools" / "phd_inventory.json"
    if inv.is_file():
        for row in json.loads(inv.read_text(encoding="utf-8")):
            if row.get("status") != "fast-ok":
                continue
            for ref in row.get("input_refs") or []:
                if "{" in ref or "%" in ref:
                    continue
                tokens.add(ref.replace("input/", ""))
    for ref in tokens:
        for base in (SRC / "input", SRC):
            p = base / ref
            if p.is_file() and not should_skip_path(p):
                dst = dest_in / p.name
                if not dst.exists():
                    shutil.copy2(p, dst)
                break
    for name in (
        "KR-1gen.model",
        "t3.model",
        "group.in",
        "KR-8.model",
        "b2.ua",
        "c4_weaved.ua",
    ):
        for base in (SRC / "input", SRC):
            p = base / name
            if p.is_file() and not should_skip_path(p):
                dst = dest_in / p.name
                try:
                    if dst.resolve() != p.resolve():
                        shutil.copy2(p, dst)
                except OSError:
                    shutil.copy2(p, dst)
                if name.endswith(".model"):
                    shutil.copy2(p, DEST / name)
                break


def main() -> int:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    copy_phd_tree(DEST, full=False, link_input=False)
    (DEST / "input").mkdir(exist_ok=True)
    _copy_required_inputs()
    if VENDOR.is_dir():
        vdest = DEST / "_vendor_pyparsing"
        vdest.mkdir(exist_ok=True)
        for p in VENDOR.glob("*.py"):
            shutil.copy2(p, vdest / p.name)
    probes_src = REPO / "tests" / "jython_scripts" / "phd" / "probes"
    if probes_src.is_dir():
        probes_dest = DEST / "probes"
        probes_dest.mkdir(exist_ok=True)
        for p in probes_src.glob("*.py"):
            shutil.copy2(p, probes_dest / p.name)
    (DEST / "README.txt").write_text(READ_ME, encoding="utf-8")
    n_py = len(list(DEST.glob("*.py")))
    n_in = len(list((DEST / "input").glob("*"))) if (DEST / "input").exists() else 0
    print(f"synced {DEST}: {n_py} scripts, {n_in} input files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())