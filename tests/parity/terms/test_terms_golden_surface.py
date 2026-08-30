"""Golden stdout checks for ``tests/parity/terms/golden_terms_surface.py``."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "tests" / "parity" / "terms" / "golden_terms_surface.py"
FIXTURES = REPO_ROOT / "tests" / "parity" / "terms" / "fixtures"
JAR = REPO_ROOT / "jars" / "uacalc.jar"


def _normalize_output(text: str) -> str:
    """Normalize subprocess stdout for comparison.

    Cosmetic only (line endings). Jython 2 vs CPython 3 differences for this
    golden are handled by **separate** checked-in fixtures (``*.cpython.txt`` vs
    ``*.jython.txt``): the JAR exposes class types (``Term``, ``Terms``, …)
    while ``uacalc_lib`` adds package-level helpers (``is_valid_var_string``,
    …) and different ``PUBLIC_COUNT``. We do not try to unify those in one
    fixture.
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


def test_golden_terms_surface_fixtures_have_expected_markers():
    """Both fixtures share structural markers; counts differ (CPython vs Jython)."""
    c = _read_golden("golden_terms_surface.cpython.txt")
    j = _read_golden("golden_terms_surface.jython.txt")
    for blob, label in ((c, "cpython"), (j, "jython")):
        assert "MODULE: org.uacalc.terms" in blob, label
        assert f"RUNTIME: {label}" in blob, label
        assert _public_count_from_golden(blob) >= 1
    assert _public_count_from_golden(c) != _public_count_from_golden(j)


def test_golden_terms_surface_cpython_matches_fixture():
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
    assert _normalize_output(r.stdout) == _read_golden("golden_terms_surface.cpython.txt")


def test_golden_terms_surface_jython_matches_fixture():
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
    assert _normalize_output(r.stdout) == _read_golden("golden_terms_surface.jython.txt")
