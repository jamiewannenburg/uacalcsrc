"""Compatibility shim for ``org.uacalc.terms``.

CPython re-exports ``uacalc_lib.terms`` and adds Jython facades used by
``~/uacalc`` scripts: ``Terms.stringToTerm``, ``Variable`` (= ``VariableImp``),
``NonVariableTerm.makeConstantTerm``.
"""

_CLASS_ALIASES = {
    "NonVariableTerm": {
        "makeConstantTerm": "make_constant_term",
        "intEval": "int_eval",
    },
    "VariableImp": {
        "intEval": "int_eval",
    },
    "Terms": {},
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

    if not hasattr(_LibNonVariableTerm, "makeConstantTerm"):
        _LibNonVariableTerm.makeConstantTerm = _LibNonVariableTerm.make_constant_term
    if not hasattr(_LibNonVariableTerm, "isaVariable") and hasattr(
        _LibNonVariableTerm, "isa_variable"
    ):
        _LibNonVariableTerm.isaVariable = _LibNonVariableTerm.isa_variable
    if not hasattr(VariableImp, "isaVariable") and hasattr(VariableImp, "isa_variable"):
        VariableImp.isaVariable = VariableImp.isa_variable
    if not hasattr(VariableImp, "intEval") and hasattr(VariableImp, "int_eval"):
        VariableImp.intEval = VariableImp.int_eval
    if not hasattr(VariableImp, "getVariableList") and hasattr(VariableImp, "get_variable_list"):
        VariableImp.getVariableList = VariableImp.get_variable_list
    if not hasattr(_LibNonVariableTerm, "getVariableList") and hasattr(
        _LibNonVariableTerm, "get_variable_list"
    ):
        _LibNonVariableTerm.getVariableList = _LibNonVariableTerm.get_variable_list

    for _vname in ("x", "y", "z"):
        _attr = getattr(VariableImp, _vname, None)
        if callable(_attr):
            try:
                setattr(VariableImp, _vname, _attr())
            except TypeError:
                pass

    class Terms(object):
        """Static facade matching Java ``org.uacalc.terms.Terms``."""

        @staticmethod
        def stringToTerm(s):
            return _string_to_term(str(s))

    NonVariableTerm = _LibNonVariableTerm

    del _uacalc_lib, _terms, _name, _vname, _attr, _LibNonVariableTerm
