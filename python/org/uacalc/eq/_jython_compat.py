"""Jython-facing helpers for ``org.uacalc.eq`` (CPython only).

Renames, argument adaptation, and Java exception translation. Library logic
stays in ``uacalc_lib``.
"""

from __future__ import annotations

from typing import Any

from org.uacalc._exceptions import (
    NullPointerException,
    translate_illegal_argument,
)


def _install(g: dict) -> None:
    Equation = g.get("Equation")
    Presentation = g.get("Presentation")

    def _bind(cls: Any, name: str, impl: Any) -> None:
        if cls is None:
            return
        try:
            setattr(cls, name, impl)
        except (TypeError, AttributeError):
            pass

    def _names_to_vars(names):
        from org.uacalc.terms import VariableImp

        if names is None:
            return []
        out = []
        for n in list(names):
            if hasattr(n, "getName"):
                out.append(n)
            else:
                out.append(VariableImp(str(n)))
        return out

    if Equation is not None:
        _orig_gvl = getattr(Equation, "get_variable_list", None)
        _orig_fail = getattr(Equation, "find_failure", None)
        _orig_fail_map = getattr(Equation, "find_failure_map", None)

        def leftSide(self):
            fn = getattr(self, "left_side_term", None)
            if fn is not None:
                return fn()
            return self.left_side()

        def rightSide(self):
            fn = getattr(self, "right_side_term", None)
            if fn is not None:
                return fn()
            return self.right_side()

        def getOperationSymbols(self):
            fn = getattr(self, "get_operation_symbol_objects", None)
            if fn is not None:
                return fn()
            return self.get_operation_symbols()

        def getVariableList(self, _orig=_orig_gvl):
            names = _orig(self) if _orig is not None else []
            return _names_to_vars(names)

        def findFailure(self, alg, report=None, _orig=_orig_fail):
            if alg is None:
                raise NullPointerException()
            try:
                return _orig(self, alg) if _orig is not None else None
            except ValueError as exc:
                translate_illegal_argument(exc)

        def findFailureMap(self, alg, report=None, _orig=_orig_fail_map):
            if alg is None:
                raise NullPointerException()
            try:
                raw = _orig(self, alg) if _orig is not None else None
            except ValueError as exc:
                translate_illegal_argument(exc)
            if raw is None:
                return None
            from org.uacalc.terms import VariableImp

            out = {}
            for name, val in dict(raw).items():
                key = name if hasattr(name, "getName") else VariableImp(str(name))
                out[key] = val
            return out

        def toString(self):
            return str(self)

        _bind(Equation, "leftSide", leftSide)
        _bind(Equation, "rightSide", rightSide)
        _bind(Equation, "getOperationSymbols", getOperationSymbols)
        _bind(Equation, "getVariableList", getVariableList)
        _bind(Equation, "findFailure", findFailure)
        _bind(Equation, "findFailureMap", findFailureMap)
        _bind(Equation, "toString", toString)

    if Presentation is not None:
        _orig_vars = getattr(Presentation, "get_variables", None)

        def getVariables(self, _orig=_orig_vars):
            names = _orig(self) if _orig is not None else []
            return _names_to_vars(names)

        def getRelations(self):
            fn = getattr(self, "get_relation_objects", None)
            if fn is not None:
                return fn()
            return self.get_relations()

        _bind(Presentation, "getVariables", getVariables)
        _bind(Presentation, "getRelations", getRelations)
