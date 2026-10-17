#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate ``resources/special/*.ua`` fixtures with Jython + Java UACalc.

Run from repo root::

    CLASSPATH=jars/uacalc.jar jython tests/parity/io/generate_special_algebra_fixtures.py

CPython cannot run this script meaningfully (needs Java algebras). After generation,
both Jython and CPython parity tests read the same files.
"""
from __future__ import print_function

import os
import sys

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
SPECIAL_DIR = os.path.join(REPO_ROOT, "resources", "special")


def main():
    if not sys.platform.startswith("java"):
        print("This generator requires Jython (Java platform).", file=sys.stderr)
        sys.exit(2)
    
    # sys.path.append("jars/uacalc.jar")
    sys.path.append(os.path.join(REPO_ROOT,"jars","uacalc.jar"))
    # print(os.path.join(REPO_ROOT,"jars","LatDraw.jar"))
    sys.path.append(os.path.join(REPO_ROOT,"jars","LatDraw.jar"))
    from org.uacalc.io import AlgebraIO, AlgebraWriter  # noqa: F401
    from org.uacalc.alg import BasicAlgebra, ProductAlgebra, PowerAlgebra  # noqa: F401
    from org.uacalc.alg import QuotientAlgebra, Subalgebra, FreeAlgebra  # noqa: F401
    from org.uacalc.alg import BigProductAlgebra, SubProductAlgebra  # noqa: F401
    from org.uacalc.util import IntArray  # noqa: F401
    
    try:
        os.makedirs(SPECIAL_DIR)
    except OSError as exc:
        pass # directory already exists

    c2_path = os.path.join(REPO_ROOT, "resources", "algebras", "cyclic2.ua")
    c3_path = os.path.join(REPO_ROOT, "resources", "algebras", "cyclic3.ua")
    c2 = AlgebraIO.readAlgebraFile(c2_path)
    c3 = AlgebraIO.readAlgebraFile(c3_path)
    AlgebraWriter(c2, os.path.join(SPECIAL_DIR, "basic_cyclic2.ua")).writeAlgebraXML()

    prod = ProductAlgebra([c2, c2])
    AlgebraWriter(prod, os.path.join(SPECIAL_DIR, "product_c2_c2.ua")).writeAlgebraXML()

    # Minimal quotient: use a known congruence on C2 if available; skip if API differs.
    try:
        con = c2.con().universe().iterator().next()
        quot = QuotientAlgebra(c2, con)
        AlgebraWriter(quot, os.path.join(SPECIAL_DIR, "quotient_example.ua")).writeAlgebraXML()
    except Exception as exc:
        print("SKIP quotient_example.ua:", exc)

    try:
        sub = Subalgebra(c2, [0])
        AlgebraWriter(sub, os.path.join(SPECIAL_DIR, "subalgebra_example.ua")).writeAlgebraXML()
    except Exception as exc:
        print("SKIP subalgebra_example.ua:", exc)

    try:
        pwr = PowerAlgebra(c2, 2)
        AlgebraWriter(pwr, os.path.join(SPECIAL_DIR, "power_c2_sq.ua")).writeAlgebraXML()
    except Exception as exc:
        print("SKIP power_c2_sq.ua:", exc)

    try:
        f1 = FreeAlgebra(c2, 1)
        f1.setName("F1")
        AlgebraWriter(f1, os.path.join(SPECIAL_DIR, "free_c2_f1.ua")).writeAlgebraXML()
    except Exception as exc:
        print("SKIP free_c2_f1.ua:", exc)

    # BigProductAlgebra is Algebra but not SmallAlgebra, so
    # AlgebraWriter(alg, path) cannot take it. Nested <bigProductAlgebra>
    # is already present in free_c2_f1.ua / subproduct_c2.ua.

    try:
        bp = BigProductAlgebra(c2, 2)
        sp = SubProductAlgebra("SP", bp, [IntArray([0, 0]), IntArray([1, 1])])
        AlgebraWriter(sp, os.path.join(SPECIAL_DIR, "subproduct_c2.ua")).writeAlgebraXML()
    except Exception as exc:
        print("SKIP subproduct_c2.ua:", exc)

    try:
        prod = ProductAlgebra([c2, c3])
        AlgebraWriter(prod, os.path.join(SPECIAL_DIR, "product_c2_c3.ua")).writeAlgebraXML()
    except Exception as exc:
        print("SKIP product_c2_c3.ua:", exc)

    try:
        pwr = PowerAlgebra(c3, 2)
        AlgebraWriter(pwr, os.path.join(SPECIAL_DIR, "power_c3_sq.ua")).writeAlgebraXML()
    except Exception as exc:
        print("SKIP power_c3_sq.ua:", exc)

    try:
        sub = Subalgebra(c3, [0])
        AlgebraWriter(sub, os.path.join(SPECIAL_DIR, "subalgebra_c3.ua")).writeAlgebraXML()
    except Exception as exc:
        print("SKIP subalgebra_c3.ua:", exc)

    print("Wrote fixtures under", SPECIAL_DIR)


if __name__ == "__main__":
    main()
