"""Golden stdout checks for ``tests/parity/eq/golden_eq_surface.py``."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "tests" / "parity" / "eq" / "golden_eq_surface.py"
FIXTURES = REPO_ROOT / "tests" / "parity" / "eq" / "fixtures"
JAR = REPO_ROOT / "jars" / "uacalc.jar"


def _normalize_output(text: str) -> str:
    """Normalize subprocess stdout for comparison.

    Cosmetic: strip ``\\r``. Equation-law **strings** in ``SMOKE_ASSOC_LAW`` use
    ASCII; if future output includes non-ASCII, keep fixtures UTF-8 and avoid
    normalizing semantic text here. Separate fixtures capture Jython (JAR:
    classes only, no ``associative_law``) vs CPython (``uacalc_lib`` adds
    static helpers and different ``PUBLIC_COUNT``).
    """
    lines = [ln.rstrip("\r") for ln in text.strip().splitlines()]
    return "\n".join(lines) + "\n"


def _read_golden(name: str) -> str:
    path = FIXTURES / name
    return _normalize_output(path.read_text(encoding="utf-8"))


def test_normalize_output_strips_carriage_returns():
    assert _normalize_output("a\r\nb\r\n") == "a\nb\n"


def _public_count_from_golden(text: str) -> int:
    for line in text.splitlines():
        if line.startswith("PUBLIC_COUNT:"):
            return int(line.split(":", 1)[1].strip())
    raise AssertionError("missing PUBLIC_COUNT line")


def test_golden_eq_surface_fixtures_have_expected_markers():
    c = _read_golden("golden_eq_surface.cpython.txt")
    j = _read_golden("golden_eq_surface.jython.txt")
    for blob, label in ((c, "cpython"), (j, "jython")):
        assert "MODULE: org.uacalc.eq" in blob, label
        assert f"RUNTIME: {label}" in blob, label
        assert _public_count_from_golden(blob) >= 1
    assert _public_count_from_golden(c) != _public_count_from_golden(j)


def test_golden_eq_surface_cpython_matches_fixture():
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
    assert _normalize_output(r.stdout) == _read_golden("golden_eq_surface.cpython.txt")


def test_golden_eq_surface_jython_matches_fixture():
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
    assert _normalize_output(r.stdout) == _read_golden("golden_eq_surface.jython.txt")
