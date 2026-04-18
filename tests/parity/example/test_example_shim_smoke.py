"""Smoke tests for ``org.uacalc.example`` shim (examples-org slice)."""

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


def _uacalc_lib_example():
    try:
        import uacalc_lib  # noqa: PLC0415
    except ImportError:
        pytest.skip("uacalc_lib not available")
    try:
        return getattr(uacalc_lib, "example")
    except AttributeError as exc:
        pytest.skip(f"uacalc_lib.example not available: {exc}")


def test_org_uacalc_example_import_smoke():
    _uacalc_lib_example()
    _ensure_python_org_on_path()
    import org.uacalc.example as ex  # noqa: PLC0415

    assert ex.__name__ == "org.uacalc.example"


def test_example_shim_public_names_match_uacalc_lib():
    """Re-exported symbols match ``uacalc_lib.example`` (may be empty until demos are bound)."""
    lib_example = _uacalc_lib_example()
    _ensure_python_org_on_path()
    import org.uacalc.example as shim  # noqa: PLC0415

    assert getattr(lib_example, "__name__", "") in ("uacalc_lib.example", "example")
    assert shim.__name__ == "org.uacalc.example"

    lib_public = {n for n in dir(lib_example) if not n.startswith("_")}
    shim_public = {n for n in dir(shim) if not n.startswith("_")}
    assert shim_public == lib_public
    for name in lib_public:
        assert getattr(shim, name) is getattr(lib_example, name)
