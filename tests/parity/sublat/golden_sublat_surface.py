#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.alg.sublat``.

**CPython**::

    PYTHONPATH=python python tests/parity/sublat/golden_sublat_surface.py

**Jython**::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/sublat/golden_sublat_surface.py
"""
from __future__ import print_function

import sys


def main():
    if sys.platform.startswith("java"):
        from org.uacalc.alg.sublat import BasicSet  # noqa: F401
        from org.uacalc.alg.sublat import SubalgebraLattice  # noqa: F401

    import org.uacalc.alg.sublat as pkg

    is_java = sys.platform.startswith("java")
    runtime = "jython" if is_java else "cpython"

    print("MODULE: org.uacalc.alg.sublat")
    print("RUNTIME: " + runtime)

    names = sorted(n for n in dir(pkg) if not n.startswith("_"))
    print("PUBLIC_COUNT: " + str(len(names)))
    for n in names:
        print("NAME: " + n)

    if is_java and "BasicSet" in names:
        from org.uacalc.alg.sublat import BasicSet  # noqa: F401

        s = BasicSet([0, 1])
        print("SAMPLE_BASIC_SET_UNIVERSE_SIZE: " + str(s.universeSize()))
    else:
        print("SAMPLE_BASIC_SET_UNIVERSE_SIZE: skip (no BasicSet on this runtime)")


if __name__ == "__main__":
    main()
