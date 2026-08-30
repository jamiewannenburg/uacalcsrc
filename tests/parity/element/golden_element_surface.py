#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.element``.

Runs under **CPython** (shim → ``uacalc_lib.element``) and **Jython** (Java
classes from ``uacalc.jar``). Normalized stdout is compared to checked-in
fixtures by pytest.

**CPython** (repo root)::

    PYTHONPATH=python python tests/parity/element/golden_element_surface.py

**Windows (PowerShell)**::

    $env:PYTHONPATH = \"python\"; python tests/parity/element/golden_element_surface.py

**Jython** (Java on classpath; do not put ``python/`` on ``PYTHONPATH`` so the
real Java package is used)::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/element/golden_element_surface.py

Jython’s ``org.uacalc.element`` package does not populate ``dir()`` until
typical types are imported; the script imports ``Element`` and
``SubProductElement`` first so the listing matches what scripts see after those
imports.
"""
from __future__ import print_function

import sys


def main():
    if sys.platform.startswith('java'):
        # Populate the Java package namespace (dir() is empty before this).
        from org.uacalc.element import Element  # noqa: F401
        from org.uacalc.element import SubProductElement  # noqa: F401

    import org.uacalc.element as elt

    is_java = sys.platform.startswith('java')
    runtime = 'jython' if is_java else 'cpython'

    print('MODULE: org.uacalc.element')
    print('RUNTIME: ' + runtime)
    names = sorted(n for n in dir(elt) if not n.startswith('_'))
    print('PUBLIC_COUNT: ' + str(len(names)))
    for n in names:
        print('NAME: ' + n)


if __name__ == '__main__':
    main()
