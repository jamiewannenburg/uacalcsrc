#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.eq``.

Runs under **CPython** (shim → ``uacalc_lib.eq``) and **Jython** (Java
classes from ``uacalc.jar``). Normalized stdout is compared to checked-in
fixtures by pytest.

**CPython** (repo root)::

    PYTHONPATH=python python tests/parity/eq/golden_eq_surface.py

**Windows (PowerShell)**::

    $env:PYTHONPATH = "python"; python tests/parity/eq/golden_eq_surface.py

**Jython**::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/eq/golden_eq_surface.py

Imports concrete Java types first so ``dir(org.uacalc.eq)`` matches typical
script usage after those imports.
"""
from __future__ import print_function

import sys


def main():
    if sys.platform.startswith('java'):
        from org.uacalc.eq import Equation  # noqa: F401
        from org.uacalc.eq import Equations  # noqa: F401
        from org.uacalc.eq import Presentation  # noqa: F401

    import org.uacalc.eq as eq_pkg

    is_java = sys.platform.startswith('java')
    if is_java:
        from org.uacalc.alg.op import OperationSymbol  # noqa: PLC0415
    else:
        from org.uacalc.alg import OperationSymbol  # noqa: PLC0415

    runtime = 'jython' if is_java else 'cpython'

    print('MODULE: org.uacalc.eq')
    print('RUNTIME: ' + runtime)
    names = sorted(n for n in dir(eq_pkg) if not n.startswith('_'))
    print('PUBLIC_COUNT: ' + str(len(names)))
    print('HAS_ASSOCIATIVE_LAW: ' + (
        'yes' if 'associative_law' in names else 'no'))
    for n in names:
        print('NAME: ' + n)

    if 'associative_law' in names:
        op = OperationSymbol('*', 2)
        out = eq_pkg.associative_law(op)
        text = out if isinstance(out, str) else str(out)
        print('SMOKE_ASSOC_LAW: ' + text)
    else:
        print('SMOKE: associative_law is uacalc_lib-only (not in JAR package)')


if __name__ == '__main__':
    main()
