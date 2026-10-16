"""Jython-facing helpers for ``org.uacalc.element`` (CPython only).

Renames, Java null→NPE, and ``toString`` matching ``SubProductElement``.
Library logic stays in ``uacalc_lib``.
"""

from __future__ import annotations

from typing import Any

from org.uacalc._exceptions import NullPointerException, translate_illegal_argument


def _install(g: dict) -> None:
    Element = g.get("Element")
    SubProductElement = g.get("SubProductElement")

    def _bind(cls: Any, name: str, impl: Any) -> None:
        if cls is None:
            return
        try:
            setattr(cls, name, impl)
        except (TypeError, AttributeError):
            pass

    def _npe(exc: BaseException) -> None:
        if isinstance(exc, NullPointerException):
            raise exc
        msg = str(exc)
        if msg == "null" or "NoneType" in type(exc).__name__:
            raise NullPointerException() from exc
        if isinstance(exc, (TypeError, AttributeError, ValueError)) and (
            "null" in msg.lower() or "NoneType" in msg
        ):
            raise NullPointerException() from exc
        if isinstance(exc, ValueError):
            translate_illegal_argument(exc)
        raise exc

    if SubProductElement is None:
        return

    _orig_get_algebra = getattr(SubProductElement, "get_algebra", None)
    _orig_index = getattr(SubProductElement, "index", None)
    _orig_get_term = getattr(SubProductElement, "get_term", None)
    _orig_gvl = getattr(SubProductElement, "get_variable_list", None)
    _orig_gvm = getattr(SubProductElement, "get_variable_map", None)
    _orig_parent = getattr(SubProductElement, "get_parent", None)
    _orig_parent_arr = getattr(SubProductElement, "get_parent_array", None)
    _orig_parent_idx = getattr(SubProductElement, "parent_index_array", None)

    def getAlgebra(self: Any, _orig=_orig_get_algebra) -> Any:
        try:
            return _orig(self) if _orig is not None else None
        except Exception as exc:
            _npe(exc)

    def index(self: Any, _orig=_orig_index) -> int:
        try:
            return int(_orig(self)) if _orig is not None else 0
        except Exception as exc:
            _npe(exc)
            return 0

    def getTerm(self: Any, _orig=_orig_get_term) -> Any:
        try:
            return _orig(self) if _orig is not None else None
        except Exception as exc:
            _npe(exc)

    def getVariableList(self: Any, _orig=_orig_gvl) -> Any:
        try:
            out = _orig(self) if _orig is not None else None
        except Exception as exc:
            _npe(exc)
            return None
        if out is None:
            raise NullPointerException()
        return list(out)

    def getVariableMap(self: Any, _orig=_orig_gvm) -> Any:
        try:
            out = _orig(self) if _orig is not None else None
        except Exception as exc:
            _npe(exc)
            return None
        if out is None:
            raise NullPointerException()
        return out

    def getParent(self: Any, _orig=_orig_parent) -> Any:
        try:
            return _orig(self) if _orig is not None else None
        except Exception:
            return None

    def getParentArray(self: Any, _orig=_orig_parent_arr) -> Any:
        try:
            return _orig(self) if _orig is not None else None
        except Exception:
            return None

    def parentIndexArray(self: Any, _orig=_orig_parent_idx) -> Any:
        try:
            return _orig(self) if _orig is not None else None
        except Exception:
            return None

    def toString(self: Any) -> str:
        try:
            return str(self)
        except Exception as exc:
            _npe(exc)
            return ""

    _bind(SubProductElement, "getAlgebra", getAlgebra)
    _bind(SubProductElement, "index", index)
    _bind(SubProductElement, "getTerm", getTerm)
    _bind(SubProductElement, "getVariableList", getVariableList)
    _bind(SubProductElement, "getVariableMap", getVariableMap)
    _bind(SubProductElement, "getParent", getParent)
    _bind(SubProductElement, "getParentArray", getParentArray)
    _bind(SubProductElement, "parentIndexArray", parentIndexArray)
    _bind(SubProductElement, "toString", toString)

    if Element is not None:
        _bind(Element, "getAlgebra", getAlgebra)
        _bind(Element, "index", index)
        _bind(Element, "getParent", getParent)
        _bind(Element, "getParentArray", getParentArray)
        _bind(Element, "parentIndexArray", parentIndexArray)
        _bind(Element, "toString", toString)
