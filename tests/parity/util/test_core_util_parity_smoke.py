"""
Smoke tests for org.uacalc.util shim (core-util parity slice).

Mirrors patterns from python/uacalc/tests/test_jython_examples_parity.py:
repo-root path setup, optional uacalc_lib, and org.uacalc package imports.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]


def _ensure_python_org_on_path() -> None:
    """So ``import org.uacalc...`` resolves to python/org/."""
    py_root = REPO_ROOT / "python"
    s = str(py_root)
    if s not in sys.path:
        sys.path.insert(0, s)


try:
    import uacalc_lib
except ImportError:
    pytest.skip("uacalc_lib not available", allow_module_level=True)

if not hasattr(uacalc_lib, "util"):
    pytest.skip(
        "uacalc_lib.util not available (native extension missing or stale build)",
        allow_module_level=True,
    )


class TestCoreUtilParitySmoke:
    """Minimal import + one util API vs uacalc_lib.util."""

    def test_import_org_uacalc_util(self):
        _ensure_python_org_on_path()
        import org.uacalc.util as util_pkg  # pylint: disable=import-outside-toplevel

        assert util_pkg is not None
        assert hasattr(util_pkg, "IntArray")

    def test_int_array_from_array_matches_direct_lib(self):
        _util = getattr(uacalc_lib, "util")
        direct = _util.IntArray.from_array([1, 2, 3])

        _ensure_python_org_on_path()
        from org.uacalc.util import IntArray  # pylint: disable=import-outside-toplevel

        shim = IntArray.from_array([1, 2, 3])
        assert shim.to_array() == direct.to_array() == [1, 2, 3]
