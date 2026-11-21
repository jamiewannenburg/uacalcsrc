"""Import smoke: ``org.uacalc.io`` re-exports on CPython.

Classification: SMOKE test - only verifies imports work and basic structure exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

pytestmark = pytest.mark.smoke  # Mark all tests in this file as smoke tests

_IO_PUBLIC = (
    "AlgebraIO",
    "AlgebraReader",
    "AlgebraWriter",
    "BadAlgebraFileException",
    "ExtFileFilter",
    "JSONChannel",
    "Mace4Reader",
    "convert_to_xml",
    "parse_line",
    "read_algebra_file",
    "read_algebra_from_stream",
    "read_algebra_list_file",
    "read_algebra_list_from_stream",
    "read_projective_plane",
    "read_projective_plane_from_stream",
    "write_algebra_file",
    "write_algebra_file_with_style",
)


def _ensure_python_org_on_path() -> None:
    py_root = REPO_ROOT / "python"
    s = str(py_root)
    if s not in sys.path:
        sys.path.insert(0, s)


import sys
from pathlib import Path as _Path

try:
    import uacalc_lib
except ImportError as _uacalc_exc:
    _tools = _Path(__file__).resolve().parents[3] / "tools"
    if str(_tools) not in sys.path:
        sys.path.insert(0, str(_tools))
    from strict_testing import guard_import_skip  # noqa: E402

    guard_import_skip("uacalc_lib", _uacalc_exc)


def test_org_uacalc_io_exports_expected_names():
    _ensure_python_org_on_path()
    import org.uacalc.io as io_pkg  # pylint: disable=import-outside-toplevel

    names = sorted(n for n in dir(io_pkg) if not n.startswith("_"))
    assert names == sorted(_IO_PUBLIC)


@pytest.mark.parametrize("name", _IO_PUBLIC)
def test_org_uacalc_io_each_symbol_importable(name: str):
    _ensure_python_org_on_path()
    import org.uacalc.io as io_pkg  # pylint: disable=import-outside-toplevel

    assert hasattr(io_pkg, name)
    assert getattr(io_pkg, name) is not None
