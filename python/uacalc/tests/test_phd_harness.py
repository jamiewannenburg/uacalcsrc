"""Unit tests for PhD Jython→CPython harness conversions."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tests" / "jython_scripts"))

from cpython_support.load_dmm import _jython2_patches  # noqa: E402
from harness import (  # noqa: E402
    _normalize_phd_io_path,
    _stabilize_fixture_mtimes,
    normalize_phd_output,
    prepare_jython2_source,
)


def test_jython2_bare_map_statement_is_eager():
    src = "def main():\n    map(lambda x: x + 1, range(3))\n"
    out = _jython2_patches(src)
    assert "list(map(lambda x: x + 1, range(3)))" in out


def test_prepare_jython2_source_applies_map_patch():
    src = "if 1:\n    map(foo, bar)\n"
    out = prepare_jython2_source(src)
    assert "list(map(foo, bar))" in out


def test_normalize_phd_io_path_strips_temp_prefix():
    raw = (
        r"C-{5}-{1} deleting C:\Users\me\AppData\Local\Temp\phd_fixture_x\input\C-5-1.ua"
    )
    assert _normalize_phd_io_path(raw) == (
        "C-{5}-{1} deleting tests/jython_scripts/phd_runtime/input/C-5-1.ua"
    )


def test_stabilize_fixture_mtimes_orders_c5_files(tmp_path: Path):
    inp = tmp_path / "input"
    inp.mkdir()
    for name in ("C-5-10.ua", "C-5-2.ua", "C-5-1.ua"):
        (inp / name).write_text("x", encoding="utf-8")
    _stabilize_fixture_mtimes(tmp_path)
    mtimes = [(p.name, p.stat().st_mtime) for p in inp.glob("C-5-*.ua")]
    mtimes.sort(key=lambda t: t[1])
    assert [n for n, _ in mtimes] == ["C-5-1.ua", "C-5-2.ua", "C-5-10.ua"]


def test_normalize_phd_output_matches_logical_paths():
    text = (
        "C-5-*.ua\n"
        r"C:\repo\tests\jython_scripts\phd_runtime\input\C-5-1.ua" + "\n"
    )
    norm = normalize_phd_output(text)
    assert norm == "C-5-*.ua\ntests/jython_scripts/phd_runtime/input/C-5-1.ua"