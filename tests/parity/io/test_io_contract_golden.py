"""Golden stdout for ``parity_io_contract.py`` (CPython; Jython when available)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "tests" / "parity" / "io" / "parity_io_contract.py"
FIXTURES = REPO_ROOT / "tests" / "parity" / "io" / "fixtures"
JAR = REPO_ROOT / "jars" / "uacalc.jar"


def _normalize_output(text: str) -> str:
    lines = [ln.rstrip("\r") for ln in text.strip().splitlines()]
    return "\n".join(lines) + "\n"


def _read_golden(name: str) -> str:
    path = FIXTURES / name
    if not path.is_file():
        pytest.skip(f"missing golden fixture {path} — run parity_io_contract.py and check in")
    return _normalize_output(path.read_text(encoding="utf-8"))


def test_parity_io_contract_cpython_matches_fixture():
    golden_path = FIXTURES / "golden_io_contract.cpython.txt"
    if not golden_path.is_file():
        pytest.skip(
            "golden_io_contract.cpython.txt not checked in — "
            "run parity_io_contract.py and add fixtures/golden_io_contract.cpython.txt"
        )
    if not SCRIPT.is_file():
        pytest.fail(f"missing script: {SCRIPT}")
    r = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT / "python")},
        timeout=180,
        check=False,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    golden = _normalize_output(golden_path.read_text(encoding="utf-8"))
    assert _normalize_output(r.stdout) == golden


def test_parity_io_contract_jython_matches_fixture():
    golden_path = FIXTURES / "golden_io_contract.jython.txt"
    if not golden_path.is_file():
        pytest.skip("golden_io_contract.jython.txt not checked in")
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
        timeout=300,
        check=False,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    golden = _normalize_output(golden_path.read_text(encoding="utf-8"))
    assert _normalize_output(r.stdout) == golden
