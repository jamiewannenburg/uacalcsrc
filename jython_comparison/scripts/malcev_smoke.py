# coding: utf-8
# Dual-runtime parity script for Malcev static helpers (Java/Jython source of truth).
from __future__ import print_function

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parity_probe import probe as _show, section

import sys

from org.uacalc.io import AlgebraIO
from org.uacalc.alg import Malcev, Algebras


def _term_list(terms):
    items = list(terms) if terms is not None else []
    return "[" + ",".join(str(t).replace(" ", "") for t in items) + "]"


def test():
    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
    _show("malcev_c2", lambda: Malcev.malcevTerm(c2))
    _show("majority_lat2", lambda: Malcev.majorityTerm(lat2))
    _show("jonsson_level_lat2", lambda: Malcev.jonssonLevel(lat2))
    _show("jonsson_terms_lat2", lambda: _term_list(Malcev.jonssonTerms(lat2)))
    _show("findNUF_lat2", lambda: Algebras.findNUF(lat2, 3))
    _show("algs_jonsson_level", lambda: Algebras.jonssonLevel(lat2))
    _show("malcev_null", lambda: Malcev.malcevTerm(None))


if __name__ == "__main__":
    test()
