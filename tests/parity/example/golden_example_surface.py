#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.example``.

Jython imports a few stable demo classes so ``dir(org.uacalc.example)`` lists
the symbols scripts see after those imports. CPython uses the shim, which
re-exports ``uacalc_lib.example`` (often empty until Rust binds demos).

**CPython** (repo root)::

    PYTHONPATH=python python tests/parity/example/golden_example_surface.py

**Jython**::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/example/golden_example_surface.py
"""
from __future__ import print_function

import sys


def main():
    if sys.platform.startswith("java"):
        # Populate the Java package namespace (dir() is sparse until imports).
        from org.uacalc.example import Average  # noqa: F401
        from org.uacalc.example import FiniteField  # noqa: F401
        from org.uacalc.example import Type1  # noqa: F401

    import org.uacalc.example as ex

    is_java = sys.platform.startswith("java")
    runtime = "jython" if is_java else "cpython"

    print("MODULE: org.uacalc.example")
    print("RUNTIME: " + runtime)
    names = sorted(n for n in dir(ex) if not n.startswith("_"))
    print("PUBLIC_COUNT: " + str(len(names)))
    for n in names:
        print("NAME: " + n)


if __name__ == "__main__":
    main()
