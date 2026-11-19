#!/usr/bin/env python3
"""Inventory Jamie's top-level PhD scripts (read-only source tree) and probe under Jython."""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\u28409265\Documents\uacalc")
ARGV_MANIFEST = REPO / "tools" / "phd_script_argv.json"
VENDOR = REPO / "tests" / "jython_scripts" / "_vendor"
MAX_FILE = 1024 * 1024
TIMEOUT = 30

SKIP_DIR = {"venv", "__pycache__", ".jython_cache", "output", "input"}


def _scripts() -> list[Path]:
    return sorted(SRC.glob("*.py"))


def _classify_imports(text: str) -> dict[str, bool]:
    low = text.lower()
    return {
        "org_uacalc": "org.uacalc" in text or "uacalc.jar" in text,
        "pyparsing": "pyparsing" in low or "import pp" in low,
        "dmm": re.search(r"\b(from dmm|import dmm)\b", text) is not None,
        "other_java": "from java." in text,
    }


def _local_imports(text: str) -> set[str]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.level == 0:
                mods.add(node.module.split(".")[0])
    return mods


def _input_refs(text: str) -> list[str]:
    return sorted(set(re.findall(r"""['"](?:input/)?([^'"]+\.(?:ua|model|in|json))['"]""", text)))


def _needs_argv(text: str) -> bool:
    return "sys.argv" in text


def _copy_deps(tmp: Path, script: Path, text: str) -> None:
    deps = _local_imports(text) & {p.stem for p in _scripts()}
    for name in deps:
        src = SRC / f"{name}.py"
        if src.is_file():
            shutil.copy2(src, tmp / f"{name}.py")
    inp = tmp / "input"
    inp.mkdir(exist_ok=True)
    for ref in _input_refs(text):
        candidates = [SRC / "input" / ref, SRC / ref]
        for c in candidates:
            if c.is_file() and c.stat().st_size <= MAX_FILE:
                shutil.copy2(c, inp / Path(ref).name)
                break
    argv = json.loads(ARGV_MANIFEST.read_text(encoding="utf-8")).get(script.name, [])
    for tok in argv:
        if tok.endswith((".ua", ".model", ".in", ".json")):
            cands = [SRC / tok, SRC / "input" / Path(tok).name]
            for c in cands:
                if c.is_file() and c.stat().st_size <= MAX_FILE:
                    dst = inp / Path(tok).name
                    if tok.startswith("input/"):
                        shutil.copy2(c, inp / Path(tok).name)
                    else:
                        shutil.copy2(c, inp / c.name)
                    break


def _run_jython(tmp: Path, script_name: str, argv: list[str]) -> dict:
    jython = os.environ.get("JYTHON", "jython")
    cp = os.environ.get("CLASSPATH", str(REPO / "jars" / "uacalc.jar"))
    pp = str(VENDOR) if VENDOR.is_dir() else str(SRC / "venv" / "Lib" / "site-packages")
    env = os.environ.copy()
    env["CLASSPATH"] = cp
    env["PYTHONPATH"] = pp
  # uacalc.jar beside scripts (some scripts sys.path.append it)
    jar_src = SRC / "uacalc.jar"
    if jar_src.is_file() and jar_src.stat().st_size < MAX_FILE:
        shutil.copy2(jar_src, tmp / "uacalc.jar")
    lat = SRC / "LatDraw.jar"
    if lat.is_file() and lat.stat().st_size < MAX_FILE:
        shutil.copy2(lat, tmp / "LatDraw.jar")
    cmd = [jython, str(tmp / script_name), *argv]
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(tmp),
            capture_output=True,
            text=True,
            env=env,
            timeout=TIMEOUT,
        )
        elapsed = time.perf_counter() - t0
        return {
            "exit": proc.returncode,
            "seconds": round(elapsed, 3),
            "stdout_len": len(proc.stdout),
            "stderr": proc.stderr[:500],
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "exit": -1,
            "seconds": TIMEOUT,
            "stdout_len": len(exc.stdout or ""),
            "stderr": (exc.stderr or b"").decode("utf-8", errors="replace")[:500],
            "timed_out": True,
        }


def status_for(imports: dict[str, bool], run: dict | None, text: str) -> str:
    if not imports["org_uacalc"] and not imports["dmm"]:
        return "not-applicable"
    if imports["pyparsing"]:
        return "needs-pyparsing"
    if run is None:
        return "jython-error"
    if run["timed_out"]:
        return "slow"
    if run["exit"] != 0:
        return "jython-error"
    return "fast-ok"


def main() -> int:
    argv_map = json.loads(ARGV_MANIFEST.read_text(encoding="utf-8"))
    rows = []
    for script in _scripts():
        text = script.read_text(encoding="utf-8", errors="replace")
        imports = _classify_imports(text)
        entry = {
            "script": script.name,
            "imports": imports,
            "needs_argv": _needs_argv(text),
            "argv_default": argv_map.get(script.name, []),
            "input_refs": _input_refs(text),
            "local_deps": sorted(_local_imports(text)),
        }
        st = "not-applicable"
        run_info = None
        if imports["org_uacalc"] or imports["dmm"]:
            if imports["pyparsing"]:
                st = "needs-pyparsing"
            else:
                with tempfile.TemporaryDirectory(prefix="phd_inv_") as td:
                    tmp = Path(td)
                    shutil.copy2(script, tmp / script.name)
                    _copy_deps(tmp, script, text)
                    run_info = _run_jython(tmp, script.name, entry["argv_default"])
                    st = status_for(imports, run_info, text)
        entry["status"] = st
        entry["run"] = run_info
        rows.append(entry)

    out = REPO / "tools" / "phd_inventory.json"
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(json.dumps(counts, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())