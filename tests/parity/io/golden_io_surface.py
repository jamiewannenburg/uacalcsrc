#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.io``.

Runs under **CPython** (shim → ``uacalc_lib.io``) and **Jython** (Java
classes from ``uacalc.jar``). Normalized stdout is compared to checked-in
fixtures by pytest.

**CPython** (repo root)::

    PYTHONPATH=python python tests/parity/io/golden_io_surface.py

**Windows (PowerShell)**::

    $env:PYTHONPATH = "python"; python tests/parity/io/golden_io_surface.py

**Jython** (Java on classpath; do not put ``python/`` on ``PYTHONPATH`` so the
real Java package is used)::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/io/golden_io_surface.py

Jython's ``org.uacalc.io`` package does not populate ``dir()`` until concrete
types are imported; the script imports the public Java classes first so the
listing matches what callers see after those imports.

``JSONChannel`` is a CPython placeholder class until ``uacalc_lib`` binds the
Java implementation; Jython loads the real class from ``uacalc.jar``.
"""
from __future__ import print_function

import sys


def main():
    if sys.platform.startswith('java'):
        from org.uacalc.io import AlgebraIO  # noqa: F401
        from org.uacalc.io import AlgebraReader  # noqa: F401
        from org.uacalc.io import AlgebraWriter  # noqa: F401
        from org.uacalc.io import BadAlgebraFileException  # noqa: F401
        from org.uacalc.io import ExtFileFilter  # noqa: F401
        from org.uacalc.io import JSONChannel  # noqa: F401
        from org.uacalc.io import Mace4Reader  # noqa: F401

    import org.uacalc.io as io_pkg

    is_java = sys.platform.startswith('java')
    runtime = 'jython' if is_java else 'cpython'

    print('MODULE: org.uacalc.io')
    print('RUNTIME: ' + runtime)
    names = sorted(n for n in dir(io_pkg) if not n.startswith('_'))
    print('PUBLIC_COUNT: ' + str(len(names)))
    for n in names:
        print('NAME: ' + n)


if __name__ == '__main__':
    main()
