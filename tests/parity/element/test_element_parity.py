"""Parity smoke tests for ``org.uacalc.element`` shim (core-element slice)."""

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


def _uacalc_lib_element():
    try:
        import uacalc_lib  # noqa: PLC0415
    except ImportError:
        pytest.skip('uacalc_lib not available')
    try:
        return getattr(uacalc_lib, 'element')
    except AttributeError as exc:
        pytest.skip(f'uacalc_lib.element not available: {exc}')


def test_org_uacalc_element_import_smoke():
    _uacalc_lib_element()
    _ensure_python_org_on_path()
    import org.uacalc.element as elt  # noqa: PLC0415

    assert elt.__name__ == 'org.uacalc.element'


def test_org_uacalc_element_same_module_on_reimport():
    """``importlib.import_module`` must resolve to the same ``org.uacalc.element`` shim."""
    import importlib  # noqa: PLC0415

    _uacalc_lib_element()
    _ensure_python_org_on_path()
    m1 = importlib.import_module('org.uacalc.element')
    import org.uacalc.element as m2  # noqa: PLC0415

    assert m1 is m2


def test_element_shim_public_names_match_uacalc_lib():
    """Re-exported symbols match the nested ``uacalc_lib.element`` module."""
    lib_element = _uacalc_lib_element()
    _ensure_python_org_on_path()
    import org.uacalc.element as shim  # noqa: PLC0415

    # Native ``uacalc_lib`` may report the submodule as ``element`` or ``uacalc_lib.element``.
    assert getattr(lib_element, '__name__', '') in ('uacalc_lib.element', 'element')
    assert shim.__name__ == 'org.uacalc.element'

    lib_public = {n for n in dir(lib_element) if not n.startswith('_')}
    shim_public = {n for n in dir(shim) if not n.startswith('_')}
    assert shim_public == lib_public
    for name in lib_public:
        assert getattr(shim, name) is getattr(lib_element, name)


def test_element_shim_reexports_element_class_when_bound():
    """If bindings expose ``Element``, the org shim must forward the same object."""
    lib_element = _uacalc_lib_element()
    if not hasattr(lib_element, "Element"):
        pytest.skip("uacalc_lib.element.Element not in this build")
    _ensure_python_org_on_path()
    import org.uacalc.element as shim  # noqa: PLC0415

    assert shim.Element is lib_element.Element
