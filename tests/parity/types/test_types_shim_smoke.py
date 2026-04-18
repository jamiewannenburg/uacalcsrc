"""Smoke tests for ``org.uacalc.types`` shim (core-util / core-types workstream)."""

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


try:
    import uacalc_lib  # noqa: F401
except ImportError:
    pytest.skip("uacalc_lib not available", allow_module_level=True)


def test_org_uacalc_types_import_smoke():
    _ensure_python_org_on_path()
    import org.uacalc.types as types_pkg  # noqa: PLC0415

    assert types_pkg.__name__ == "org.uacalc.types"


def test_types_shim_public_names_match_uacalc_lib():
    """Re-exported symbols match ``uacalc_lib.types`` when that submodule has public names."""
    lib_types = getattr(uacalc_lib, "types", None)
    _ensure_python_org_on_path()
    import org.uacalc.types as shim  # noqa: PLC0415

    if lib_types is None:
        lib_public: set[str] = set()
    else:
        lib_public = {n for n in dir(lib_types) if not n.startswith("_")}
    shim_public = {n for n in dir(shim) if not n.startswith("_")}
    assert shim_public == lib_public
    if not lib_public:
        pytest.skip(
            "uacalc_lib.types is an empty stub (no public names); "
            "org.uacalc.types parity deferred until bindings add exports"
        )
    for name in lib_public:
        assert getattr(shim, name) is getattr(lib_types, name)
