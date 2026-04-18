#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.terms``.

Runs under **CPython** (shim → ``uacalc_lib.terms``) and **Jython** (Java
classes from ``uacalc.jar``). Normalized stdout is compared to checked-in
fixtures by pytest.

**CPython** (repo root)::

    PYTHONPATH=python python tests/parity/terms/golden_terms_surface.py

**Windows (PowerShell)**::

    $env:PYTHONPATH = "python"; python tests/parity/terms/golden_terms_surface.py

**Jython** (Java on classpath; do not put ``python/`` on ``PYTHONPATH`` so the
real Java package is used)::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/terms/golden_terms_surface.py

Jython's ``org.uacalc.terms`` package does not populate ``dir()`` until concrete
types are imported; the script imports the public Java classes first so the
listing matches what callers see after those imports.
"""
from __future__ import print_function

import sys


def main():
    if sys.platform.startswith('java'):
        from org.uacalc.terms import NonVariableTerm  # noqa: F401
        from org.uacalc.terms import Taylor  # noqa: F401
        from org.uacalc.terms import Term  # noqa: F401
        from org.uacalc.terms import Terms  # noqa: F401
        from org.uacalc.terms import Variable  # noqa: F401
        from org.uacalc.terms import VariableImp  # noqa: F401

    import org.uacalc.terms as terms_pkg

    is_java = sys.platform.startswith('java')
    runtime = 'jython' if is_java else 'cpython'

    print('MODULE: org.uacalc.terms')
    print('RUNTIME: ' + runtime)
    names = sorted(n for n in dir(terms_pkg) if not n.startswith('_'))
    print('PUBLIC_COUNT: ' + str(len(names)))
    print('HAS_IS_VALID_VAR_STRING: ' + (
        'yes' if 'is_valid_var_string' in names else 'no'))
    for n in names:
        print('NAME: ' + n)

    # uacalc_lib exposes helpers on the package; the JAR top-level package may not.
    if 'is_valid_var_string' in names:
        ok = terms_pkg.is_valid_var_string('x')
        print('SMOKE_VALID_X: ' + ('yes' if ok else 'no'))


if __name__ == '__main__':
    main()
