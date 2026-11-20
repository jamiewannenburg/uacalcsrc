"""Compatibility shim for ``org.uacalc.terms``.

CPython re-exports ``uacalc_lib.terms`` and adds Jython facades used by
``~/uacalc`` scripts: ``Terms.stringToTerm``, ``Variable`` (= ``VariableImp``),
``NonVariableTerm.makeConstantTerm``.
"""

_CLASS_ALIASES = {
    "Term": {
        "isaVariable": "isa_variable",
        "leadingOperationSymbol": "leading_operation_symbol",
        "getOperationSymbols": "get_operation_symbols",
        "getChildren": "get_children",
        "eval": "eval",
        "intEval": "int_eval",
        "interpretation": "interpretation",
        "depth": "depth",
        "length": "length",
        "getVariableList": "get_variable_list",
        "substitute": "substitute",
        "toString": "to_string",
        "writeStringBuffer": "write_string_buffer",
    },
    "NonVariableTerm": {
        "makeConstantTerm": "make_constant_term",
        "eval": "eval",
        "intEval": "int_eval",
        "isaVariable": "isa_variable",
        "interpretation": "interpretation",
        "depth": "depth",
        "length": "length",
        "substitute": "substitute",
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

    class _CallableSingleton:
        """Java ``Variable.x`` literals plus ``VariableImp.x()`` factories on one name."""

        __slots__ = ("_factory", "_inst")

        def __init__(self, factory):
            self._factory = factory
            self._inst = factory()

        def __call__(self):
            return self._factory()

        def __getattr__(self, name):
            return getattr(self._inst, name)

        def __repr__(self):
            return repr(self._inst)

        def __eq__(self, other):
            return self._inst == other

        def __hash__(self):
            return hash(self._inst)

    for _vname in ("x", "y", "z"):
        _factory = getattr(VariableImp, _vname)
        if callable(_factory):
            setattr(VariableImp, _vname, _CallableSingleton(_factory))

    class Term(object):
        """Java ``org.uacalc.terms.Term`` interface surface for contracts."""

        def isaVariable(self):
            raise NotImplementedError

        def leadingOperationSymbol(self):
            raise NotImplementedError

        def getOperationSymbols(self):
            raise NotImplementedError

        def getChildren(self):
            raise NotImplementedError

        def eval(self, alg, mmap):
            raise NotImplementedError

        def intEval(self, alg, mmap):
            raise NotImplementedError

        def interpretation(self, alg, varlist=None, useAll=None):
            raise NotImplementedError

        def depth(self):
            raise NotImplementedError

        def length(self):
            raise NotImplementedError

        def getVariableList(self):
            raise NotImplementedError

        def substitute(self, mmap):
            raise NotImplementedError

        def toString(self):
            raise NotImplementedError

        def writeStringBuffer(self, sb):
            raise NotImplementedError

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
        _LibNonVariableTerm,
        _make_constant_term,
        _install_jython_compat,
    )
