#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.alg.op``.

**CPython**::

    PYTHONPATH=python python tests/parity/alg_op/golden_alg_op_surface.py

**Jython**::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/alg_op/golden_alg_op_surface.py
"""
from __future__ import print_function

import sys


def main():
    if sys.platform.startswith("java"):
        from org.uacalc.alg.op import AbstractIntOperation  # noqa: F401
        from org.uacalc.alg.op import OperationSymbol  # noqa: F401

    import org.uacalc.alg.op as pkg

    is_java = sys.platform.startswith("java")
    runtime = "jython" if is_java else "cpython"

    print("MODULE: org.uacalc.alg.op")
    print("RUNTIME: " + runtime)

    names = sorted(n for n in dir(pkg) if not n.startswith("_"))
    print("PUBLIC_COUNT: " + str(len(names)))
    for n in names:
        print("NAME: " + n)

    if is_java and "OperationSymbol" in names and "AbstractIntOperation" in names:
        from org.uacalc.alg.op import AbstractIntOperation  # noqa: F401
        from org.uacalc.alg.op import OperationSymbol  # noqa: F401

        sym = OperationSymbol("*", 2)
        op = AbstractIntOperation(sym, 3)
        print("SAMPLE_OP_SYMBOL: " + str(sym))
        print("SAMPLE_OP_ARITY: " + str(sym.arity()))
        print("SAMPLE_ABS_INT_OP_SET_SIZE: " + str(op.getSetSize()))
    else:
        print("SAMPLE_OP_SYMBOL: skip (no OperationSymbol on this runtime)")


if __name__ == "__main__":
    main()
