#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.example``.

Jython imports the packaged demo classes so ``dir(org.uacalc.example)`` lists
the symbols scripts see after those imports. CPython uses the org shim ports.

**CPython** (repo root)::

    PYTHONPATH=python python tests/parity/example/golden_example_surface.py

**Jython**::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/example/golden_example_surface.py
"""
from __future__ import print_function

import sys


def main():
    if sys.platform.startswith("java"):
        from org.uacalc.example import Average  # noqa: F401
        from org.uacalc.example import ConLyndonF3  # noqa: F401
        from org.uacalc.example import FilteringAlgebras  # noqa: F401
        from org.uacalc.example import FiniteField  # noqa: F401
        from org.uacalc.example import FinitelyPresentedAlg  # noqa: F401
        from org.uacalc.example import HasConstantTuple  # noqa: F401
        from org.uacalc.example import HasKaryNU  # noqa: F401
        from org.uacalc.example import Jipsen  # noqa: F401
        from org.uacalc.example import KKMVWExample  # noqa: F401
        from org.uacalc.example import Kearnes  # noqa: F401
        from org.uacalc.example import MembershipTester  # noqa: F401
        from org.uacalc.example import Michalewski  # noqa: F401
        from org.uacalc.example import NoSymGroup  # noqa: F401
        from org.uacalc.example import ParallelClose8  # noqa: F401
        from org.uacalc.example import TupleStream  # noqa: F401
        from org.uacalc.example import Type1  # noqa: F401

    import org.uacalc.example as ex

    is_java = sys.platform.startswith("java")
    runtime = "jython" if is_java else "cpython"

    print("MODULE: org.uacalc.example")
    print("RUNTIME: " + runtime)
    skip = set(["annotations"])
    names = sorted(n for n in dir(ex) if not n.startswith("_") and n not in skip)
    print("PUBLIC_COUNT: " + str(len(names)))
    for n in names:
        print("NAME: " + n)


if __name__ == "__main__":
    main()
