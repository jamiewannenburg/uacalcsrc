#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.fplat``.

Runs under **CPython** (shim → ``uacalc_lib.fplat``) and **Jython** (Java
classes from ``uacalc.jar``). Normalized stdout is compared to checked-in
fixtures by pytest.

**CPython**::

    PYTHONPATH=python python tests/parity/fplat/golden_fplat_surface.py

**Jython**::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/fplat/golden_fplat_surface.py

Imports ``PartiallyDefinedLattice`` first so ``dir()`` lists the type.
"""
from __future__ import print_function

import sys


def main():
    from org.uacalc.fplat import PartiallyDefinedLattice  # noqa: F401

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

    if is_java:
        # Java ctor is (name, Order<Variable>, joins, meets); Rust shim allows a 3-arg shortcut.
        print('SMOKE: ctor differs (Java needs Order + join/meet lists; Rust shim uses 3-arg)')
    else:
        L = PartiallyDefinedLattice('T', [], [])
        print('SMOKE_T_STR: ' + str(L))


if __name__ == '__main__':
    main()
