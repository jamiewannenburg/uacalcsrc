#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden snapshot script for core ``org.uacalc.alg`` (BasicAlgebra smoke).

Runs under **CPython** (``PYTHONPATH=python`` → shim + ``uacalc_lib``) and
**Jython** (``CLASSPATH=jars/uacalc.jar``, empty ``PYTHONPATH`` → Java).

Normalized stdout is compared to fixtures by ``test_alg_core_golden_smoke.py``.
"""
from __future__ import print_function

import sys


def main():
    import org.uacalc.alg as alg_pkg  # noqa: PLC0415

    a = alg_pkg.BasicAlgebra("T", [0, 1, 2], [])
    print("MODULE: org.uacalc.alg")
    print("RUNTIME: " + ("jython" if sys.platform.startswith("java") else "cpython"))
    print("CARDINALITY: " + str(a.cardinality()))
    print("NAME: " + str(a.getName()))
    print("UNIVERSE_SORTED: " + str(sorted(list(a.getUniverseList()))))


if __name__ == "__main__":
    main()
