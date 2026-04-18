#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden / documentation snapshot for ``org.uacalc.alg.parallel`` vs ``Pool`` placement.

On **Java/Jython**, ``Pool`` lives in package ``org.uacalc.alg.parallel`` (see jar).

On **CPython** with current ``uacalc_lib`` builds, ``org.uacalc.alg.parallel`` may be an
empty shim while ``Pool`` is exposed on ``uacalc_lib.alg`` (Rust ``PyPool``).

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
    print(
        "POOL_NOTE: On Jython, Pool is org.uacalc.alg.parallel.Pool; "
        "on CPython uacalc_lib often exposes Pool on uacalc_lib.alg while the "
        "org.uacalc.alg.parallel shim may be empty until alg.parallel is wired."
    )

    if is_java:
        from org.uacalc.alg.parallel import Pool  # noqa: F401
        from org.uacalc.alg.parallel import SingleClose  # noqa: F401

    import org.uacalc.alg.parallel as pkg

    names = sorted(n for n in dir(pkg) if not n.startswith("_"))
    print("SHIM_PUBLIC_COUNT: " + str(len(names)))
    for n in names:
        print("SHIM_NAME: " + n)

    if not is_java:
        try:
            import uacalc_lib  # noqa: F401
        except ImportError:
            print("UACALC_LIB_POOL: unavailable (uacalc_lib import failed)")
            return
        alg = getattr(uacalc_lib, "alg", None)
        pool = getattr(alg, "Pool", None) if alg is not None else None
        if pool is not None:
            print("UACALC_LIB_ALG_POOL: " + repr(pool))
        else:
            print("UACALC_LIB_ALG_POOL: missing")


if __name__ == "__main__":
    main()
