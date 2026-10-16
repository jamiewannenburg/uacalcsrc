"""Jython-facing helpers for ``org.uacalc.terms`` (CPython only).

Renames, overload dispatch, Map/List argument adaptation, and Java exception
translation. Library logic stays in ``uacalc_lib``.
"""

from __future__ import annotations

from typing import Any, Optional

from org.uacalc._exceptions import (
    IllegalArgumentException,
    NullPointerException,
    translate_illegal_argument,
)


def _var_name(obj: Any) -> str:
    if obj is None:
        raise NullPointerException()
    if isinstance(obj, str):
        return obj
    getter = getattr(obj, "getName", None) or getattr(obj, "get_name", None)
    if callable(getter):
        return str(getter())
    return str(obj)


def _varlist_to_names(varlist: Any) -> Optional[list]:
    if varlist is None:
        return None
    return [_var_name(v) for v in list(varlist)]


def _var_map_to_names(mmap: Any) -> dict:
    if mmap is None:
        raise NullPointerException()
    items = mmap.items() if hasattr(mmap, "items") else mmap
    out = {}
    for k, v in items:
        name = k if isinstance(k, str) else _var_name(k)
        out[name] = v
    return out


def _npe_or_iae(exc: BaseException) -> None:
    if isinstance(exc, (IllegalArgumentException, NullPointerException)):
        raise exc
    msg = str(exc)
    if isinstance(exc, (TypeError, AttributeError)) and (
        "NoneType" in type(exc).__name__ or "NoneType" in msg or "null" in msg.lower()
    ):
        raise NullPointerException(msg) from exc
    if isinstance(exc, ValueError) and "not found" in msg.lower():
        raise NullPointerException(msg) from exc
    if isinstance(exc, ValueError):
        translate_illegal_argument(exc)
    raise exc


def _install(g: dict) -> None:
    VariableImp = g["VariableImp"]
    NonVariableTerm = g["NonVariableTerm"]
    TermOperationImp = g.get("TermOperationImp")

    def _names_to_vars(names: Any) -> list:
        if names is None:
            return []
        return [VariableImp(n) if not hasattr(n, "getName") else n for n in list(names)]

    def _bind(cls: Any, name: str, impl: Any) -> None:
        if cls is None:
            return
        try:
            setattr(cls, name, impl)
        except (TypeError, AttributeError):
            pass

    def _wrap_eval(orig):
        def eval(self, alg, mmap):  # noqa: A001 - Java method name
            if alg is None or mmap is None:
                raise NullPointerException()
            try:
                return orig(self, alg, _var_map_to_names(mmap))
            except Exception as exc:
                _npe_or_iae(exc)

        return eval

    def _wrap_int_eval(orig):
        def intEval(self, alg, mmap):
            if alg is None or mmap is None:
                raise NullPointerException()
            try:
                return orig(self, alg, _var_map_to_names(mmap))
            except Exception as exc:
                _npe_or_iae(exc)

        return intEval

    def _wrap_interpretation(orig, term_op_cls):
        def interpretation(self, alg, varlist=None, useAll=None):
            if alg is None:
                raise NullPointerException()
            if varlist is None:
                vars_ = _names_to_vars(
                    getattr(self, "get_variable_list", lambda: [])()
                )
                return term_op_cls(self, vars_, alg)
            names = _varlist_to_names(varlist)
            use_all = True if useAll is None else bool(useAll)
            try:
                return orig(self, alg, names, use_all)
            except Exception as exc:
                _npe_or_iae(exc)

        return interpretation

    def _wrap_substitute(orig):
        def substitute(self, mmap):
            if mmap is None:
                raise NullPointerException()
            try:
                return orig(self, _var_map_to_names(mmap))
            except Exception as exc:
                _npe_or_iae(exc)

        return substitute

    def _wrap_get_variable_list(orig):
        def getVariableList(self):
            return _names_to_vars(orig(self))

        return getVariableList

    def equals(self, other):
        return self == other

    def hashCode(self):
        return hash(self)

    def toString(self):
        return str(self)

    def writeStringBuffer(self, sb):
        writer = getattr(self, "write_string_buffer", None)
        if writer is None:
            return str(self) if not sb else str(sb) + str(self)
        if hasattr(sb, "append"):
            sb.append(writer(""))
            return sb
        return writer("" if sb is None else str(sb))

    for cls in (VariableImp, NonVariableTerm):
        _orig_eval = getattr(cls, "eval", None)
        _orig_int = getattr(cls, "int_eval", None) or getattr(cls, "intEval", None)
        _orig_interp = getattr(cls, "interpretation", None)
        _orig_sub = getattr(cls, "substitute", None)
        _orig_gvl = getattr(cls, "get_variable_list", None)

        if _orig_eval is not None:
            _bind(cls, "eval", _wrap_eval(_orig_eval))
        if _orig_int is not None:
            _bind(cls, "intEval", _wrap_int_eval(_orig_int))
        if _orig_interp is not None and TermOperationImp is not None:
            _bind(
                cls,
                "interpretation",
                _wrap_interpretation(_orig_interp, TermOperationImp),
            )
        if _orig_sub is not None:
            _bind(cls, "substitute", _wrap_substitute(_orig_sub))
        if _orig_gvl is not None:
            _bind(cls, "getVariableList", _wrap_get_variable_list(_orig_gvl))

        _bind(cls, "equals", equals)
        _bind(cls, "hashCode", hashCode)
        _bind(cls, "toString", toString)
        _bind(cls, "writeStringBuffer", writeStringBuffer)

        for camel, snake in (
            ("isaVariable", "isa_variable"),
            ("getName", "get_name"),
            ("leadingOperationSymbol", "leading_operation_symbol"),
            ("getOperationSymbols", "get_operation_symbols"),
            ("getChildren", "get_children"),
        ):
            if not hasattr(cls, camel) and hasattr(cls, snake):
                _bind(cls, camel, getattr(cls, snake))

    if not hasattr(NonVariableTerm, "LEFT_PAR"):
        NonVariableTerm.LEFT_PAR = "("
        NonVariableTerm.RIGHT_PAR = ")"
        NonVariableTerm.COMMA = ","

    if TermOperationImp is not None:
        for camel, snake in (
            ("intValueAt", "int_value_at"),
            ("getSetSize", "get_set_size"),
            ("getTerm", "get_term"),
            ("getOrderedVariables", "get_ordered_variables"),
            ("getTable", "get_table"),
        ):
            if not hasattr(TermOperationImp, camel) and hasattr(TermOperationImp, snake):
                _bind(TermOperationImp, camel, getattr(TermOperationImp, snake))
