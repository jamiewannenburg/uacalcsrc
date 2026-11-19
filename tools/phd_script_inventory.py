#!/usr/bin/env python3
"""Inventory Jamie's PhD scripts with full temp-tree copy and Jython probes."""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\u28409265\Documents\uacalc")
ARGV_MANIFEST = REPO / "tools" / "phd_script_argv.json"
VENDOR = REPO / "tests" / "jython_scripts" / "_vendor"
MAX_FILE = 1024 * 1024
TIMEOUT = 30

SKIP_DIR_NAMES = {"venv", "__pycache__", ".jython_cache", "node_modules"}
SKIP_SUFFIX = {".class", ".out"}
SKIP_TOP_OUTPUT = "output"


def _scripts() -> list[Path]:
    return sorted(SRC.glob("*.py"))


def _classify_imports(text: str) -> dict[str, bool]:
    low = text.lower()
    return {
        "org_uacalc": "org.uacalc" in text or "uacalc.jar" in text,
        "pyparsing": "pyparsing" in low or re.search(r"\bimport pp\b", text) is not None,
        "dmm": re.search(r"\b(from dmm|import dmm)\b", text) is not None,
        "other_java": "from java." in text,
        "py3_print": "print(" in text and "end=" in text,
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
    return sorted(
        set(re.findall(r"""['"](?:input/)?([^'"]+\.(?:ua|model|in|json))['"]""", text))
    )


def should_skip_path(path: Path) -> bool:
    if any(part in SKIP_DIR_NAMES for part in path.parts):
        return True
    if path.suffix.lower() in SKIP_SUFFIX:
        return True
    try:
        if path.is_file() and path.stat().st_size > MAX_FILE:
            return True
    except OSError:
        return True
    return False


def copy_phd_tree(dest: Path, *, full: bool = False, link_input: bool = True) -> None:
    """Copy Jamie tree into dest. Default: top-level .py + jars + junction/symlink input."""
    dest.mkdir(parents=True, exist_ok=True)
    for py in SRC.glob("*.py"):
        shutil.copy2(py, dest / py.name)
    for name in ("uacalc.jar", "LatDraw.jar"):
        jar = SRC / name
        if jar.is_file() and jar.stat().st_size <= MAX_FILE:
            shutil.copy2(jar, dest / name)
    for f in SRC.iterdir():
        if not f.is_file() or f.suffix == ".py":
            continue
        if should_skip_path(f) or f.stat().st_size > MAX_FILE:
            continue
        if f.name in ("uacalc.jar", "LatDraw.jar"):
            continue
        shutil.copy2(f, dest / f.name)
    inp_dest = dest / "input"
    if not full and link_input and (SRC / "input").is_dir():
        if inp_dest.exists():
            if inp_dest.is_symlink() or inp_dest.is_dir():
                pass
            else:
                inp_dest.unlink()
        if not inp_dest.exists():
            try:
                os.symlink(SRC / "input", inp_dest, target_is_directory=True)
            except OSError:
                subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(inp_dest), str(SRC / "input")],
                    check=False,
                    capture_output=True,
                )
    if not full:
        if VENDOR.is_dir():
            vendor_dest = dest / "_vendor_pyparsing"
            vendor_dest.mkdir(exist_ok=True)
            for p in VENDOR.glob("*.py"):
                shutil.copy2(p, vendor_dest / p.name)
        (dest / "output").mkdir(exist_ok=True)
        return
    for root, dirnames, filenames in os.walk(SRC):
        root_path = Path(root)
        dirnames[:] = [
            d
            for d in dirnames
            if d not in SKIP_DIR_NAMES and not (root_path == SRC and d == SKIP_TOP_OUTPUT)
        ]
        rel = root_path.relative_to(SRC)
        for name in filenames:
            src = root_path / name
            if should_skip_path(src):
                continue
            target = dest / rel / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
    if VENDOR.is_dir():
        vendor_dest = dest / "_vendor_pyparsing"
        vendor_dest.mkdir(exist_ok=True)
        for p in VENDOR.glob("*.py"):
            shutil.copy2(p, vendor_dest / p.name)


def _categorize_error(stderr: str, stdout: str, imports: dict) -> str:
    s = (stderr + stdout).lower()
    if "timed out" in s or "timeout" in s:
        return "timeout"
    if "could not find" in s or "no such file" in s or "filenotfound" in s:
        return "missing-input-or-args"
    if "syntaxerror" in s or "mismatched input" in s:
        return "syntax-jython2-vs-py3"
    if imports.get("pyparsing") and "no module named pyparsing" in s:
        return "missing-pyparsing"
    if "importerror: no module named" in s:
        return "missing-local-module"
    if "varlist must have all the variable" in s:
        return "api-java-termoperationimp-varlist"
    if "empty string" in s and "illegalargumentexception" in s:
        return "api-java-stringtoterm-nullary"
    if "sparqlwrapper" in s or "dbpedia" in s:
        return "external-network"
    if "pygraphviz" in s or "no module named numpy" in s:
        return "missing-optional-python-dep"
    if "illegalargumentexception" in s or "nullpointerexception" in s:
        return "java-runtime-exception"
    if "exception" in s or "traceback" in s:
        return "script-or-data-exception"
    return "other"


def _run_jython(
    tmp: Path,
    script_name: str,
    argv: list[str],
    *,
    jar: Path,
    use_repo_jar_for_syspath: bool,
) -> dict:
    jython = os.environ.get("JYTHON", "jython")
    pp_parts = [
        str(tmp / "_vendor_pyparsing") if (tmp / "_vendor_pyparsing").is_dir() else "",
        str(VENDOR),
    ]
    pp = os.pathsep.join(p for p in pp_parts if p)
    env = os.environ.copy()
    env["CLASSPATH"] = str(jar.resolve())
    env["PYTHONPATH"] = pp
    if use_repo_jar_for_syspath:
        shutil.copy2(jar, tmp / "uacalc.jar")
    else:
        old = SRC / "uacalc.jar"
        if old.is_file() and old.stat().st_size < MAX_FILE:
            shutil.copy2(old, tmp / "uacalc.jar")
    cmd = [jython, str(tmp / script_name), *argv]
    t0 = time.perf_counter()
    proc = subprocess.Popen(
        cmd,
        cwd=str(tmp),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    stdout = ""
    stderr = ""
    try:
        stdout, stderr = proc.communicate(timeout=TIMEOUT)
        elapsed = time.perf_counter() - t0
        return {
            "exit": proc.returncode,
            "seconds": round(elapsed, 3),
            "stdout_len": len(stdout),
            "stdout_head": stdout[:300],
            "stderr": stderr[:1200],
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            capture_output=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
        out = stdout or (exc.stdout or "")
        err = stderr or (exc.stderr or "")
        if isinstance(out, bytes):
            out = out.decode("utf-8", errors="replace")
        if isinstance(err, bytes):
            err = err.decode("utf-8", errors="replace")
        elapsed = time.perf_counter() - t0
        return {
            "exit": -1,
            "seconds": round(elapsed, 3),
            "stdout_len": len(out),
            "stdout_head": out[:300],
            "stderr": err[:1200],
            "timed_out": True,
        }


def status_for(imports: dict, run: dict | None) -> str:
    if not imports["org_uacalc"] and not imports["dmm"]:
        return "not-applicable"
    if imports.get("py3_print"):
        return "syntax-jython2"
    if run is None:
        return "jython-error"
    if run["timed_out"]:
        return "slow"
    if run["exit"] != 0:
        return "jython-error"
    return "fast-ok"


def _strip_run_artifacts(root: Path) -> None:
    out = root / "output"
    if out.is_dir():
        shutil.rmtree(out, ignore_errors=True)
    for pattern in ("*_re.ua", "s*.ua", "sa*.ua"):
        for p in root.glob(pattern):
            if p.name not in {"sugihara.py"} and p.suffix == ".ua":
                try:
                    p.unlink()
                except OSError:
                    pass


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", metavar="SCRIPT", default=None)
    args = parser.parse_args()
    argv_map = json.loads(ARGV_MANIFEST.read_text(encoding="utf-8"))
    repo_jar = (REPO / "jars" / "uacalc.jar").resolve()
    old_jar = (SRC / "uacalc.jar").resolve()

    rows = []
    with tempfile.TemporaryDirectory(prefix="phd_master_") as td:
        master = Path(td)
        copy_phd_tree(master)
        scripts = _scripts()
        if args.only is not None:
            only = set(args.only)
            scripts = [s for s in scripts if s.name in only]
        for idx, script in enumerate(scripts, 1):
            print(f"[{idx}/{len(scripts)}] {script.name}", flush=True)
            text = script.read_text(encoding="utf-8", errors="replace")
            imports = _classify_imports(text)
            argv = argv_map.get(script.name, [])
            entry = {
                "script": script.name,
                "imports": imports,
                "needs_argv": "sys.argv" in text,
                "argv_default": argv,
                "input_refs": _input_refs(text),
                "local_deps": sorted(_local_imports(text)),
            }
            if not imports["org_uacalc"] and not imports["dmm"]:
                entry["status"] = "not-applicable"
                entry["run_repo_jar"] = None
                rows.append(entry)
                continue
            if imports.get("py3_print"):
                entry["status"] = "syntax-jython2"
                entry["error_category"] = "syntax-jython2-vs-py3"
                entry["run_repo_jar"] = None
                rows.append(entry)
                continue

            _strip_run_artifacts(master)
            run_repo = _run_jython(
                master,
                script.name,
                argv,
                jar=repo_jar,
                use_repo_jar_for_syspath=True,
            )
            entry["run_repo_jar"] = run_repo
            entry["status"] = status_for(imports, run_repo)
            if entry["status"] == "jython-error":
                entry["error_category"] = _categorize_error(
                    run_repo.get("stderr", ""),
                    run_repo.get("stdout_head", ""),
                    imports,
                )
                _strip_run_artifacts(master)
                run_old = _run_jython(
                    master,
                    script.name,
                    argv,
                    jar=old_jar,
                    use_repo_jar_for_syspath=False,
                )
                entry["run_old_jar"] = run_old
                if run_old["exit"] == 0 and run_repo["exit"] != 0:
                    entry["error_category"] = (
                        entry["error_category"] + "+api-drift-old-jar-works"
                    )
                elif run_old["exit"] != 0 and run_repo["exit"] != 0:
                    if run_old.get("stderr", "")[:80] == run_repo.get("stderr", "")[:80]:
                        entry["error_category"] = (
                            entry["error_category"] + "+same-on-old-jar"
                        )
            else:
                entry["error_category"] = None
            rows.append(entry)

    out = REPO / "tools" / "phd_inventory.json"
    if args.only is not None and out.is_file():
        existing = json.loads(out.read_text(encoding="utf-8"))
        by_name = {e["script"]: e for e in existing}
        for r in rows:
            by_name[r["script"]] = r
        order = [e["script"] for e in existing]
        for name in by_name:
            if name not in order:
                order.append(name)
        rows = [by_name[name] for name in order]
    out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    cats: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        cat = r.get("error_category")
        if cat:
            cats[cat] = cats.get(cat, 0) + 1
    print(json.dumps({"status": counts, "error_categories": cats}, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())