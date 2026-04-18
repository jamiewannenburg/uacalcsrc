"""Golden stdout checks for ``tests/parity/conlat/golden_conlat_surface.py``."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "tests" / "parity" / "conlat" / "golden_conlat_surface.py"
FIXTURES = REPO_ROOT / "tests" / "parity" / "conlat" / "fixtures"
JAR = REPO_ROOT / "jars" / "uacalc.jar"


def _normalize_output(text: str) -> str:
    if text.startswith("\ufeff"):
        text = text[1:]
    lines = [ln.rstrip("\r") for ln in text.strip().splitlines()]
    return "\n".join(lines) + "\n"


def _read_golden(name: str) -> str:
    path = FIXTURES / name
    raw = path.read_text(encoding="utf-8", errors="replace")
    return _normalize_output(raw)


def test_golden_conlat_surface_cpython_matches_fixture():
    if not SCRIPT.is_file():
        pytest.fail(f"missing golden script: {SCRIPT}")
    r = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT / "python")},
        timeout=60,
        check=False,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert r.stderr.strip() == "", r.stderr
    assert _normalize_output(r.stdout) == _read_golden("golden_conlat_surface.cpython.txt")


def test_golden_conlat_surface_jython_matches_fixture():
    jython = shutil.which("jython")
    if not jython:
        pytest.skip("jython not on PATH")
    if not JAR.is_file():
        pytest.skip(f"missing {JAR}")

    env = dict(os.environ)
    env["CLASSPATH"] = str(JAR)
    env["PYTHONPATH"] = ""

    r = subprocess.run(
        [jython, str(SCRIPT)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=120,
        check=False,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert r.stderr.strip() == "", r.stderr
    assert _normalize_output(r.stdout) == _read_golden("golden_conlat_surface.jython.txt")
