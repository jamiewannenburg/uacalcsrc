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

    class _FailureMapKey(object):
        """Dict key whose repr matches Java ``Variable`` in failure maps."""

        def __init__(self, var: Any) -> None:
            self._var = var

        def getName(self) -> str:
            getter = getattr(self._var, "getName", None)
            if callable(getter):
                return str(getter())
            return str(self._var)

        def __repr__(self) -> str:
            return self.getName()

        def __hash__(self) -> int:
            return hash(self.getName())

        def __eq__(self, other: Any) -> bool:
            if other is self:
                return True
            if hasattr(other, "getName") and other.getName() == self.getName():
                return True
            return False

    def _coerce_equation_algebra(alg: Any) -> Any:
        """Accept Jamie wrappers, subclasses, and native ``PyBasicAlgebra``."""
        if alg is None:
            return alg
        inner = getattr(alg, "_inner", None)
        if inner is not None:
            return inner
        conv = getattr(alg, "to_basic_algebra", None)
        if callable(conv):
            return conv()
        return alg

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
            rust_alg = _coerce_equation_algebra(alg)
            try:
                return _orig(self, rust_alg) if _orig is not None else None
            except (TypeError, ValueError) as exc:
                translate_illegal_argument(exc)

        def _failure_values_to_python(alg: Any, raw: Any) -> Any:
            """Map integer failure values back through the algebra's universe labels."""
            if raw is None:
                return None
            inner = getattr(alg, "_inner", alg)
            is_int = getattr(alg, "_java_int_universe", None)
            if is_int is None:
                fn = getattr(inner, "int_universe", None)
                is_int = fn() if callable(fn) else True
            if is_int:
                return raw
            get_el = getattr(inner, "get_element", None) or getattr(alg, "getElement", None)
            if not callable(get_el):
                return raw
            if isinstance(raw, dict):
                out = {}
                for key, val in dict(raw).items():
                    try:
                        idx = int(val)
                    except (TypeError, ValueError):
                        out[key] = val
                        continue
                    py_val = get_el(idx)
                    out[key] = py_val if py_val is not None and py_val != -1 else val
                return out
            if isinstance(raw, (list, tuple)):
                mapped = []
                for val in raw:
                    try:
                        idx = int(val)
                    except (TypeError, ValueError):
                        mapped.append(val)
                        continue
                    py_val = get_el(idx)
                    mapped.append(py_val if py_val is not None and py_val != -1 else val)
                return type(raw)(mapped)
            return raw

        def findFailureMap(self, alg, report=None, _orig=_orig_fail_map):
            if alg is None:
                raise NullPointerException()
            rust_alg = _coerce_equation_algebra(alg)
            try:
                raw = _orig(self, rust_alg) if _orig is not None else None
            except (TypeError, ValueError) as exc:
                translate_illegal_argument(exc)
            if raw is None:
                return None
            from org.uacalc.terms import VariableImp

            raw_dict = dict(raw)
            out = {}
            var_by_name = {}
            for var in self.getVariableList():
                name = var.getName() if hasattr(var, "getName") else str(var)
                var_by_name[name] = var
            for name in sorted(raw_dict.keys()):
                var = var_by_name.get(name)
                if var is None:
                    var = VariableImp(str(name))
                out[_FailureMapKey(var)] = raw_dict[name]
            mapped = _failure_values_to_python(alg, out)
            return mapped if mapped is not None else out

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
