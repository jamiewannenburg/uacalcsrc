"""Compatibility shim for ``org.uacalc.terms``.

CPython re-exports ``uacalc_lib.terms`` and adds Jython facades used by
``~/uacalc`` scripts: ``Terms.stringToTerm``, ``Variable`` (= ``VariableImp``),
``NonVariableTerm.makeConstantTerm``.
"""

_CLASS_ALIASES = {
    "NonVariableTerm": {
        "makeConstantTerm": "make_constant_term",
        "intEval": "int_eval",
        "isaVariable": "isa_variable",
        "getVariableList": "get_variable_list",
        "leadingOperationSymbol": "leading_operation_symbol",
        "getOperationSymbols": "get_operation_symbols",
        "getChildren": "get_children",
        "writeStringBuffer": "write_string_buffer",
        "toString": "to_string",
        "hashCode": "hashCode",
    },
    "VariableImp": {
        "intEval": "int_eval",
        "isaVariable": "isa_variable",
        "getName": "get_name",
        "getVariableList": "get_variable_list",
        "leadingOperationSymbol": "leading_operation_symbol",
        "getOperationSymbols": "get_operation_symbols",
        "getChildren": "get_children",
        "writeStringBuffer": "write_string_buffer",
        "toString": "to_string",
        "hashCode": "hashCode",
    },
    "Variable": {
        "getName": "get_name",
    },
    "Terms": {},
    "Taylor": {
        "markovicMcKenzieTerm": "markovicMcKenzieTerm",
        "siggersTerm": "siggersTerm",
        "canonicalForm": "canonicalForm",
        "interprets": "interprets",
        "termFromArray": "termFromArray",
        "makeBalancedTayorTerm": "makeBalancedTayorTerm",
        "lexicographicallyCompare": "lexicographicallyCompare",
        "arity": "arity",
        "inteqs": "inteqs",
        "equations": "equations",
    },
}

if __import__("sys").platform.startswith("java"):
    from org.uacalc.terms import *  # noqa: F403
else:
    import uacalc_lib as _uacalc_lib

    _terms = _uacalc_lib.terms
    for _name in dir(_terms):
        if not _name.startswith("_"):
            globals()[_name] = getattr(_terms, _name)

    _LibNonVariableTerm = _terms.NonVariableTerm
    _string_to_term = _terms.string_to_term
    VariableImp = _terms.VariableImp
    Variable = VariableImp

    _make_constant_term = _LibNonVariableTerm.make_constant_term

    # jython_contracts validate() only sees ClassDef methods. Keep this stub in
    # the AST, then replace it with the library class so isinstance() works and
    # ``NonVariableTerm is uacalc_lib.terms.NonVariableTerm``.
    class NonVariableTerm:
        @staticmethod
        def makeConstantTerm(sym):
            return _make_constant_term(sym)

    NonVariableTerm = _LibNonVariableTerm
    NonVariableTerm.makeConstantTerm = staticmethod(_make_constant_term)

    for _vname in ("x", "y", "z"):
        _attr = getattr(VariableImp, _vname, None)
        if callable(_attr):
            try:
                setattr(VariableImp, _vname, _attr())
            except TypeError:
                pass

    class Terms(object):
        """Static facade matching Java ``org.uacalc.terms.Terms``."""

        _lib = _terms
        _string_to_term = staticmethod(_string_to_term)

        @staticmethod
        def stringToTerm(s):
            from org.uacalc._exceptions import (
                IllegalArgumentException,
                translate_illegal_argument,
            )

            if s is None:
                raise IllegalArgumentException("null string")
            try:
                return Terms._string_to_term(str(s))
            except ValueError as exc:
                translate_illegal_argument(exc)

        @staticmethod
        def isValidVarString(s):
            from org.uacalc._exceptions import NullPointerException

            if s is None:
                raise NullPointerException()
            return Terms._lib.is_valid_var_string(str(s))

        @staticmethod
        def isValidOpNameString(s):
            from org.uacalc._exceptions import NullPointerException

            if s is None:
                raise NullPointerException()
            return Terms._lib.is_valid_op_name_string(str(s))

        @staticmethod
        def flatten(term):
            from org.uacalc._exceptions import (
                NullPointerException,
                translate_illegal_argument,
            )

            if term is None:
                raise NullPointerException()
            try:
                return Terms._lib.flatten(term)
            except ValueError as exc:
                translate_illegal_argument(exc)

    from org.uacalc.terms._jython_compat import _install as _install_jython_compat

    _install_jython_compat(globals())

    del (
        _uacalc_lib,
        _terms,
        _name,
        _vname,
        _attr,
        _LibNonVariableTerm,
        _make_constant_term,
        _install_jython_compat,
    )
