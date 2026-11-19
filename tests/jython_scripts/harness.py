"""Run Jamie PhD scripts under CPython (org.uacalc) with print-statement conversion."""
from __future__ import annotations

import ast
import io
import json
import os
import re
import runpy
import sys
import tokenize
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VENDOR = Path(__file__).resolve().parent / "_vendor"
PHD_ROOT = Path(__file__).resolve().parent / "phd"

# Normalisations applied when comparing stdout (documented in PHD_SCRIPT_COMPARISONS.md).
ADDRESS_RE = re.compile(r"\b(?:0x)?[0-9a-f]{8,}\b", re.I)
TIMING_RE = re.compile(r"\b\d+\.\d+s\b")
CLASS_AT_RE = re.compile(r"\b\w+@[0-9a-f]+\b", re.I)


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


def phd_sys_path() -> list[str]:
    return [
        str(REPO_ROOT / "python"),
        str(REPO_ROOT / "python" / "uacalc_lib"),
        str(VENDOR),
        str(PHD_ROOT),
    ]


def run_phd_script_cpython(
    script_rel: str,
    argv_suffix: list[str] | None = None,
    *,
    cwd: Path | None = None,
) -> tuple[int, str, str]:
    script = PHD_ROOT / script_rel
    if not script.is_file():
        raise FileNotFoundError(script)
    cwd = cwd or PHD_ROOT
    source = script.read_text(encoding="utf-8", errors="replace")
    if "from __future__ import print_function" not in source:
        source = convert_print_statements_to_function(source)

    saved_path = list(sys.path)
    saved_argv = sys.argv[:]
    saved_cwd = os.getcwd()
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    try:
        os.chdir(str(cwd))
        sys.path = phd_sys_path() + saved_path
        sys.argv = [str(script)] + list(argv_suffix or [])
        sys.stdout = out_buf
        sys.stderr = err_buf
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
    return rc, out_buf.getvalue(), err_buf.getvalue()


def load_manifest() -> list[dict[str, Any]]:
    manifest_path = PHD_ROOT / "manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return list(data.get("scripts", []))