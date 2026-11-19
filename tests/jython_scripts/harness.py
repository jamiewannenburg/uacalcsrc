"""Run Jamie PhD scripts under CPython (org.uacalc) with print-statement conversion."""
from __future__ import annotations

import ast
import io
import json
import os
import re
import runpy
import shutil
import sys
import tempfile
import tokenize
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VENDOR = Path(__file__).resolve().parent / "_vendor"
CPYTHON_SUPPORT = Path(__file__).resolve().parent / "cpython_support"
PHD_ROOT = Path(__file__).resolve().parent / "phd_runtime"
GOLDENS_ROOT = Path(__file__).resolve().parent / "phd" / "goldens"
FIXTURES_ROOT = Path(__file__).resolve().parent / "phd" / "fixtures"

# Normalisations applied when comparing stdout (documented in PHD_SCRIPT_COMPARISONS.md).
ADDRESS_RE = re.compile(r"\b(?:0x)?[0-9a-f]{8,}\b", re.I)
TIMING_RE = re.compile(r"\b\d+\.\d+s\b")
CLASS_AT_RE = re.compile(r"\b\w+@[0-9a-f]+\b", re.I)


def normalize_phd_file(content: str, path: str | Path) -> str:
    """Stable line endings and whitespace for golden file comparison (json/dot/tex)."""
    path = Path(path)
    suffix = path.suffix.lower()
    text = content.replace("\r\n", "\n").replace("\r", "\n")
    if suffix == ".json":
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and "edges" in obj:
                obj = dict(obj)
                if isinstance(obj.get("nodes"), list):
                    obj["nodes"] = sorted(obj["nodes"], key=str)
                if isinstance(obj.get("edges"), list):
                    obj["edges"] = sorted(
                        [tuple(e) for e in obj["edges"]],
                        key=lambda t: (str(t[0]), str(t[1])),
                    )
                    obj["edges"] = [list(e) for e in obj["edges"]]
            return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
        except json.JSONDecodeError:
            pass
    lines = [ln.rstrip() for ln in text.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + ("\n" if lines else "")


def normalize_phd_output(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if re.match(r"^depth is -?\d+$", line.strip()):
            continue
        line = ADDRESS_RE.sub("<addr>", line)
        line = CLASS_AT_RE.sub("<obj>", line)
        line = TIMING_RE.sub("<time>", line)
        line = re.sub(r"\b(\d+)L\b", r"\1", line)
        lines.append(line)
    return "\n".join(lines).strip()


def _collect_print_lines(source: str) -> list[tuple[int, int, str]]:
    """Return (start, end, line) for each print statement line (Jython 2 style)."""
    out: list[tuple[int, int, str]] = []
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except tokenize.TokenError:
        return out
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type == tokenize.NAME and tok.string == "print" and i + 1 < len(tokens):
            if tokens[i + 1].type == tokenize.OP and tokens[i + 1].string == "(":
                i += 1
                continue
            start_line = tok.start[0]
            parts = [tok.string]
            j = i + 1
            while j < len(tokens) and tokens[j].type not in (
                tokenize.NEWLINE,
                tokenize.NL,
            ):
                parts.append(tokens[j].string)
                j += 1
            end_line = tokens[j - 1].end[0] if j > i + 1 else start_line
            out.append((start_line, end_line, "".join(parts)))
            i = j
            continue
        i += 1
    return out


def convert_print_statements_to_function(source: str) -> str:
    """
    Token-level rewrite of Jython-style ``print expr`` to ``print(expr)``.

    Applied at load time so copied PhD script bodies stay unchanged on disk.
    """
    lines = source.splitlines(keepends=True)
    for start, end, stmt in _collect_print_lines(source):
        converted = stmt
        m = re.match(r"print\s+(.+)", stmt.strip())
        if m:
            converted = "print({})".format(m.group(1).strip())
        for ln in range(start, end + 1):
            if ln <= len(lines):
                if ln == start:
                    suffix = ""
                    if lines[ln - 1].endswith("\n"):
                        suffix = "\n"
                        body = lines[ln - 1].rstrip("\n")
                    else:
                        body = lines[ln - 1]
                    indent = body[: len(body) - len(body.lstrip())]
                    if ln == end:
                        lines[ln - 1] = indent + converted + suffix
                    else:
                        lines[ln - 1] = ""
                elif ln == end and start != end:
                    lines[ln - 1] = ""
    return "".join(lines)


def prepare_jython2_source(source: str) -> str:
    """Print statements, dict iterators, and legacy except syntax for CPython 3."""
    out_lines: list[str] = []
    for line in source.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("print ") and not stripped.startswith("print("):
            indent = line[: len(line) - len(stripped)]
            body = stripped[6:]
            comment = ""
            if "#" in body:
                body, _, comment = body.partition("#")
                comment = "#" + comment
            line = f"{indent}print({body.strip()}){comment}"
        out_lines.append(line)
    source = "\n".join(out_lines)
    if source and not source.endswith("\n"):
        source += "\n"
    source = source.replace(".iteritems()", ".items()")
    source = source.replace(".iterkeys()", ".keys()")
    source = source.replace(".itervalues()", ".values()")
    source = re.sub(
        r"^(\s*)except\s+(\w+)\s*,\s*(\w+)\s*:",
        r"\1except \2 as \3:",
        source,
        flags=re.MULTILINE,
    )
    return source


def _prime_cpython_imports() -> None:
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from cpython_support.latdraw_shim import install_latdraw_shim  # noqa: WPS433
    from cpython_support.load_dmm import ensure_dmm_loaded  # noqa: WPS433

    install_latdraw_shim()
    ensure_dmm_loaded()


def phd_sys_path() -> list[str]:
    return [
        str(REPO_ROOT / "python"),
        str(REPO_ROOT / "python" / "uacalc_lib"),
        str(VENDOR),
        str(CPYTHON_SUPPORT),
        str(PHD_ROOT),
    ]


def run_phd_script_cpython(
    script_rel: str,
    argv_suffix: list[str] | None = None,
    *,
    cwd: Path | None = None,
    fixture_root: Path | None = None,
) -> tuple[int, str, str, Path | None]:
    script = PHD_ROOT / script_rel
    if not script.is_file():
        raise FileNotFoundError(script)
    cwd = cwd or PHD_ROOT
    fixture_root = fixture_root or FIXTURES_ROOT
    source = prepare_jython2_source(script.read_text(encoding="utf-8", errors="replace"))

    saved_path = list(sys.path)
    saved_modules = dict(sys.modules)
    saved_argv = sys.argv[:]
    saved_cwd = os.getcwd()
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    run_cwd = cwd
    used_fixture_tmp = False
    try:
        if fixture_root.is_dir():
            work = Path(tempfile.mkdtemp(prefix="phd_fixture_"))
            used_fixture_tmp = True
            shutil.copytree(
                fixture_root,
                work,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            run_cwd = work
        os.chdir(str(run_cwd))
        os.environ.setdefault("PHD_SKIP_DRAW", "1")
        os.environ.setdefault("PHD_SIMPLE_DOT", "1")
        sys.path = phd_sys_path() + [p for p in saved_path if p not in phd_sys_path()]
        sys.argv = [str(script)] + list(argv_suffix or [])
        sys.stdout = out_buf
        sys.stderr = err_buf
        _prime_cpython_imports()
        code = compile(source, str(script), "exec")
        glob: dict[str, Any] = {"__name__": "__main__", "__file__": str(script)}
        exec(code, glob, glob)
        rc = 0
    except SystemExit as exc:
        rc = int(exc.code) if isinstance(exc.code, int) else (1 if exc.code else 0)
    except BaseException:
        import traceback

        traceback.print_exc(file=err_buf)
        rc = 1
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
        sys.argv = saved_argv
        sys.path = saved_path
        os.chdir(saved_cwd)
        for name, mod in list(sys.modules.items()):
            if name not in saved_modules:
                del sys.modules[name]
    artifact_dir = run_cwd if used_fixture_tmp else None
    return rc, out_buf.getvalue(), err_buf.getvalue(), artifact_dir


def compare_phd_outputs(
    entry: dict[str, Any],
    stdout: str,
    artifact_dir: Path,
    *,
    goldens_root: Path | None = None,
) -> list[str]:
    """Return human-readable mismatch lines (empty when all comparisons pass)."""
    goldens_root = goldens_root or GOLDENS_ROOT
    script_path = Path(entry["path"])
    stem = script_path.name
    errors: list[str] = []

    if entry.get("compare_stdout"):
        golden_stdout = goldens_root / f"{stem}.stdout"
        if not golden_stdout.is_file():
            errors.append(f"missing golden stdout {golden_stdout}")
        else:
            expected = normalize_phd_output(golden_stdout.read_text(encoding="utf-8"))
            got = normalize_phd_output(stdout)
            if got != expected:
                errors.append(f"stdout differs from {golden_stdout}")

    for rel in entry.get("compare_files") or []:
        rel_path = Path(rel)
        got_path = artifact_dir / rel_path
        golden_path = goldens_root / stem / rel_path
        if not golden_path.is_file():
            errors.append(f"missing golden {golden_path}")
            continue
        if not got_path.is_file():
            errors.append(f"missing artifact {got_path}")
            continue
        got = normalize_phd_file(
            got_path.read_text(encoding="utf-8", errors="replace"), rel_path
        )
        expected = normalize_phd_file(
            golden_path.read_text(encoding="utf-8", errors="replace"), rel_path
        )
        if got != expected:
            errors.append(f"file {rel} differs from {golden_path}")
    return errors


def load_manifest() -> list[dict[str, Any]]:
    manifest_path = PHD_ROOT / "manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return list(data.get("scripts", []))