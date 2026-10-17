# coding: utf-8
# Dual-runtime parity script for Malcev static helpers (Java/Jython source of truth).
from __future__ import print_function

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import Malcev, Algebras


def _show(label, thunk):
    try:
        print(label + "=" + str(thunk()).replace(" ", ""))
    except Exception:
        e = sys.exc_info()[1]
        msg = str(e).replace("\n", " ").replace("\r", " ")
        print(label + "=EXC:" + type(e).__name__ + ":" + msg)


def test():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
    _show("malcev_c2", lambda: Malcev.malcevTerm(c2))
    _show("majority_lat2", lambda: Malcev.majorityTerm(lat2))
    _show("jonsson_level_lat2", lambda: Malcev.jonssonLevel(lat2))
    _show("jonsson_terms_lat2", lambda: Malcev.jonssonTerms(lat2))
    _show("findNUF_lat2", lambda: Algebras.findNUF(lat2, 3))
    _show("algs_jonsson_level", lambda: Algebras.jonssonLevel(lat2))
    _show("malcev_null", lambda: Malcev.malcevTerm(None))


if __name__ == "__main__":
    test()
