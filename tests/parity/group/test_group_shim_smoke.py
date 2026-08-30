"""Smoke tests for ``org.uacalc.group`` shim (core-group slice)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _ensure_python_org_on_path() -> None:
    py_root = REPO_ROOT / "python"
    s = str(py_root)
    if s not in sys.path:
        sys.path.insert(0, s)


def _uacalc_lib_group():
    try:
        import uacalc_lib  # noqa: PLC0415
    except ImportError:
        pytest.skip("uacalc_lib not available")
    try:
        return getattr(uacalc_lib, "group")
    except AttributeError as exc:
        pytest.skip(f"uacalc_lib.group not available: {exc}")


def test_org_uacalc_group_import_smoke():
    _uacalc_lib_group()
    _ensure_python_org_on_path()
    import org.uacalc.group as grp  # noqa: PLC0415

    assert grp.__name__ == "org.uacalc.group"


def test_group_shim_public_names_match_uacalc_lib():
    lib_group = _uacalc_lib_group()
    _ensure_python_org_on_path()
    import org.uacalc.group as shim  # noqa: PLC0415

    lib_public = {n for n in dir(lib_group) if not n.startswith("_")}
    shim_public = {n for n in dir(shim) if not n.startswith("_")}
    assert shim_public == lib_public
    for name in lib_public:
        assert getattr(shim, name) is getattr(lib_group, name)


def test_group_minimal_if_bindings():
    _uacalc_lib_group()
    _ensure_python_org_on_path()
    import org.uacalc.group as grp  # noqa: PLC0415

    g = grp.PermutationGroup("S2", [(0, 1)])
    assert "S2" in str(g)
