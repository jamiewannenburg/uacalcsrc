"""Golden stdout checks for ``tests/parity/element/golden_element_surface.py``."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "tests" / "parity" / "element" / "golden_element_surface.py"
FIXTURES = REPO_ROOT / "tests" / "parity" / "element" / "fixtures"
JAR = REPO_ROOT / "jars" / "uacalc.jar"


def _normalize_output(text: str) -> str:
    lines = [ln.rstrip("\r") for ln in text.strip().splitlines()]
    return "\n".join(lines) + "\n"


def _read_golden(name: str) -> str:
    path = FIXTURES / name
    return _normalize_output(path.read_text(encoding="utf-8"))


def _public_count_from_golden(text: str) -> int:
    for line in text.splitlines():
        if line.startswith("PUBLIC_COUNT:"):
            return int(line.split(":", 1)[1].strip())
    raise AssertionError("missing PUBLIC_COUNT line")


def test_golden_element_surface_fixtures_have_expected_markers():
    """Both fixtures share structural markers (counts may differ across builds)."""
    c = _read_golden("golden_element_surface.cpython.txt")
    j = _read_golden("golden_element_surface.jython.txt")
    for blob, label in ((c, "cpython"), (j, "jython")):
        assert "MODULE: org.uacalc.element" in blob, label
        assert f"RUNTIME: {label}" in blob, label
        assert _public_count_from_golden(blob) >= 0


def test_golden_element_surface_cpython_matches_fixture():
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
    assert _normalize_output(r.stdout) == _read_golden("golden_element_surface.cpython.txt")


def test_golden_element_surface_jython_matches_fixture():
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
    assert _normalize_output(r.stdout) == _read_golden("golden_element_surface.jython.txt")
