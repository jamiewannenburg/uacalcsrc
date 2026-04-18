#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.lat``.

Runs under **CPython** (shim → ``uacalc_lib.lat``) and **Jython** (Java
classes from ``uacalc.jar``). Normalized stdout is compared to checked-in
fixtures by pytest.

**CPython** (repo root)::

    PYTHONPATH=python python tests/parity/lat/golden_lat_surface.py

**Windows (PowerShell)**::

    $env:PYTHONPATH = "python"; python tests/parity/lat/golden_lat_surface.py

**Jython** (Java on classpath; do not put ``python/`` on ``PYTHONPATH`` so the
real Java package is used)::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/lat/golden_lat_surface.py

Jython’s ``org.uacalc.lat`` package does not populate ``dir()`` until concrete
types are imported; the script imports the public Java classes first so the
listing matches what callers see after those imports.
"""
from __future__ import print_function

import sys


def main():
    if sys.platform.startswith('java'):
        # Populate the Java package namespace (dir() is empty before this).
        from org.uacalc.lat import BasicLattice  # noqa: F401
        from org.uacalc.lat import Lattice  # noqa: F401
        from org.uacalc.lat import Lattices  # noqa: F401
        from org.uacalc.lat import Order  # noqa: F401
        from org.uacalc.lat import OrderedSets  # noqa: F401
        from org.uacalc.lat import SmallLattice  # noqa: F401

    import org.uacalc.lat as lat_pkg

    is_java = sys.platform.startswith('java')
    runtime = 'jython' if is_java else 'cpython'

    print('MODULE: org.uacalc.lat')
    print('RUNTIME: ' + runtime)
    names = sorted(n for n in dir(lat_pkg) if not n.startswith('_'))
    print('PUBLIC_COUNT: ' + str(len(names)))
    print('HAS_BASIC_LATTICE: ' + ('yes' if 'BasicLattice' in names else 'no'))
    for n in names:
        print('NAME: ' + n)


if __name__ == '__main__':
    main()
