#!/usr/bin/env jython
# -*- coding: utf-8 -*-
"""
Enumerate subalgebras of term reducts from a Mace4 model stream (Jython + uacalc.jar).

This demonstrates Jython interoperability: ``org.uacalc.io.Mace4Reader`` reads from a
Java ``InputStream``, so models can be consumed incrementally from a file or from
stdin (for example a pipe from ``mace4``) without loading the entire stream into a
Python buffer first.

**Environment** (from the repository root; build Java with Ant if ``jars/`` is missing,
see the root README *Quick Start*):

- **Unix:** ``export CLASSPATH="jars/uacalc.jar:jars/LatDraw.jar"``
- **Windows:** ``set CLASSPATH=jars\uacalc.jar;jars\LatDraw.jar``

Put the JARs on ``CLASSPATH`` (not ``sys.path``). Then::

  jython jython_comparison/subreducts_mace4_stream.py --help
  jython jython_comparison/subreducts_mace4_stream.py join meet -f resources/mace4/KR-8-expl.model
  mace4 ... | jython jython_comparison/subreducts_mace4_stream.py join meet

**Rust / uacalc_lib:** The core reader is ``Mace4Reader::new`` over any ``Read`` stream.
In Python, ``parse_algebra_from_stream`` / ``parse_algebra_list_from_stream`` take a full
``bytes`` value (``Vec<u8>`` in Rust), not an open file object. Lazy per-algebra iteration
over a *file path* is ``parse_algebra_list_from_file``. For stdin-style use from CPython
without Jython, you would buffer input (or extend the bindings with a streaming iterator).
"""
from __future__ import print_function

import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Read Mace4 models from a file or stdin and list subalgebras of the "
            "specified term reduct (Jython + Java UACalc)."
        )
    )
    parser.add_argument(
        "terms",
        nargs="+",
        metavar="TERM",
        help="Terms defining the reduct signature (passed to Terms.stringToTerm), e.g. x*y",
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="models_file",
        metavar="PATH",
        help="Mace4 models file (default: read from standard input)",
    )
    return parser.parse_args()


def iter_mace4_algebras(stream):
    """
    Yield ``SmallAlgebra`` instances from a Mace4 text stream.

    :param stream: Java ``java.io.InputStream`` (file, stdin, pipe, etc.)
    """
    from org.uacalc.io import Mace4Reader

    reader = Mace4Reader(stream)
    while True:
        alg = reader.parseAlgebra()
        if alg is None:
            break
        yield alg


def subreducts(alg, signature_terms):
    """Yield ``Subalgebra`` instances for the reduct of ``alg`` to ``signature_terms``."""
    from org.uacalc.alg import Subalgebra, ReductAlgebra
    from org.uacalc.alg.sublat import SubalgebraLattice

    reduct_algebra = ReductAlgebra(alg, signature_terms)
    sl = SubalgebraLattice(reduct_algebra)
    for gens in sl.iterator():
        yield Subalgebra(reduct_algebra, gens)


def main():
    args = parse_args()
    from java.io import FileInputStream
    from java.lang import System
    from org.uacalc.terms import Terms

    signature = [Terms.stringToTerm(t) for t in args.terms]

    stream = None
    close_stream = False
    try:
        if args.models_file:
            path = os.path.abspath(args.models_file)
            stream = FileInputStream(path)
            close_stream = True
        else:
            stream = System.in

        found = 0
        for model_index, alg in enumerate(iter_mace4_algebras(stream)):
            for subalg in subreducts(alg, signature):
                found += 1
                print(found, model_index, subalg.cardinality())
    finally:
        if close_stream and stream is not None:
            stream.close()


if __name__ == "__main__":
    main()
