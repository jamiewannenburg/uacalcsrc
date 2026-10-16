#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.fplat``.

Runs under **CPython** (shim → Java-shaped facade) and **Jython** (Java
classes from ``uacalc.jar``). Normalized stdout is compared to checked-in
fixtures by pytest.

**CPython**::

    PYTHONPATH=python python tests/parity/fplat/golden_fplat_surface.py

**Jython**::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/fplat/golden_fplat_surface.py

Imports ``PartiallyDefinedLattice`` first so ``dir()`` lists the type.
The constructor matches Java: ``(name, Order, joins, meets)``.
"""
from __future__ import print_function

import sys


def main():
    from org.uacalc.fplat import PartiallyDefinedLattice  # noqa: F401
    from org.uacalc.lat import Order
    from org.uacalc.terms import VariableImp

    import org.uacalc.fplat as fplat_pkg

    is_java = sys.platform.startswith('java')
    runtime = 'jython' if is_java else 'cpython'

    print('MODULE: org.uacalc.fplat')
    print('RUNTIME: ' + runtime)
    names = sorted(n for n in dir(fplat_pkg) if not n.startswith('_'))
    print('PUBLIC_COUNT: ' + str(len(names)))
    print('HAS_PARTIALLY_DEFINED_LATTICE: ' + (
        'yes' if 'PartiallyDefinedLattice' in names else 'no'))
    for n in names:
        print('NAME: ' + n)

    class NameOrder(Order):
        def leq(self, a, b):
            def _n(v):
                fn = getattr(v, 'getName', None) or getattr(v, 'get_name', None)
                if callable(fn):
                    return fn()
                return str(v)
            return _n(a) <= _n(b)

    x = VariableImp('x')
    y = VariableImp('y')
    L = PartiallyDefinedLattice('T', NameOrder(), [[x, y]], [])
    print('SMOKE_LEQ_XY: ' + str(bool(L.leq(x, y))).lower())
    print('SMOKE_LEQ_YX: ' + str(bool(L.leq(y, x))).lower())


if __name__ == '__main__':
    main()
