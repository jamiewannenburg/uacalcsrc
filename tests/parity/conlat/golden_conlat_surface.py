#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.alg.conlat``.

Runs under **CPython** (shim → ``uacalc_lib``) and **Jython**
(Java from ``uacalc.jar``). Normalized stdout is compared to checked-in fixtures.

**CPython** (repo root)::

    PYTHONPATH=python python tests/parity/conlat/golden_conlat_surface.py

**Jython** (empty ``PYTHONPATH``; ``CLASSPATH`` includes ``jars/uacalc.jar``)::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/conlat/golden_conlat_surface.py
"""
from __future__ import print_function

import sys


def main():
    if sys.platform.startswith("java"):
        from org.uacalc.alg.conlat import BasicPartition  # noqa: F401
        from org.uacalc.alg.conlat import Partition  # noqa: F401

    import org.uacalc.alg.conlat as pkg

    is_java = sys.platform.startswith("java")
    runtime = "jython" if is_java else "cpython"

    print("MODULE: org.uacalc.alg.conlat")
    print("RUNTIME: " + runtime)

    names = sorted(n for n in dir(pkg) if not n.startswith("_"))
    print("PUBLIC_COUNT: " + str(len(names)))
    for n in names:
        print("NAME: " + n)

    BP = getattr(pkg, "BasicPartition", None)
    if BP is not None and hasattr(BP, "zero"):
        z = BP.zero(3)
        j = z.join(BP.one(3))
        print("SAMPLE_BP_JOIN: " + str(j))
    else:
        print("SAMPLE_BP_JOIN: skip (no BasicPartition on this runtime)")


if __name__ == "__main__":
    main()
