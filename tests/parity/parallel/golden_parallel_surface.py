#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.alg.parallel``.

On both **Jython** and **CPython**, ``Pool`` and ``SingleClose`` live in
``org.uacalc.alg.parallel``.

**CPython**::

    PYTHONPATH=python python tests/parity/parallel/golden_parallel_surface.py

**Jython**::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/parallel/golden_parallel_surface.py
"""
from __future__ import print_function

import sys


def main():
    is_java = sys.platform.startswith("java")
    runtime = "jython" if is_java else "cpython"

    print("MODULE: org.uacalc.alg.parallel")
    print("RUNTIME: " + runtime)

    from org.uacalc.alg.parallel import Pool  # noqa: F401
    from org.uacalc.alg.parallel import SingleClose  # noqa: F401

    import org.uacalc.alg.parallel as pkg

    names = sorted(n for n in dir(pkg) if not n.startswith("_"))
    print("SHIM_PUBLIC_COUNT: " + str(len(names)))
    for n in names:
        print("SHIM_NAME: " + n)
    print("HAS_POOL: " + ("yes" if "Pool" in names else "no"))
    print("HAS_SINGLE_CLOSE: " + ("yes" if "SingleClose" in names else "no"))


if __name__ == "__main__":
    main()
