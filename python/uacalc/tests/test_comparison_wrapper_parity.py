"""Wrapper behaviour locked for jython_comparison allowlist fixes."""

from __future__ import annotations

import os
import tempfile

import pytest

from org.uacalc._exceptions import IllegalArgumentException, NullPointerException
from org.uacalc.alg import Algebras, Closer, ParameterizedAlgebra
from org.uacalc.io import AlgebraIO, AlgebraWriter
from org.uacalc.util import IntArray


def _repo_root():
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
    )


def test_closer_accepts_null_algebra_constructor():
    c2_path = os.path.join(_repo_root(), "resources", "algebras", "cyclic2.ua")
    c2 = AlgebraIO.readAlgebraFile(c2_path)
    g00 = IntArray([0, 0])
    closer = Closer(None, [g00])
    assert closer is not None
    with pytest.raises(NullPointerException):
        closer.sgClose()


def test_find_in_clone_empty_ops_with_report_is_iae():
    c2_path = os.path.join(_repo_root(), "resources", "algebras", "cyclic2.ua")
    c2 = AlgebraIO.readAlgebraFile(c2_path)
    with pytest.raises(IllegalArgumentException):
        Algebras.findInClone([], c2, None)


def test_parameterized_algebra_null_names_npe():
    with pytest.raises(NullPointerException):
        ParameterizedAlgebra().getParameterMap([1])


def test_algebra_list_file_returns_full_list_despite_java_bug():
    path = os.path.join(
        _repo_root(), "resources", "algebras", "cyclic2_cyclic3_list.ua"
    )
    algs = AlgebraIO.readAlgebraListFile(path)
    assert len(algs) == 2
    cards = sorted(int(a.cardinality()) for a in algs)
    assert cards == [2, 3]


def test_algebra_writer_has_no_flush_like_java():
    c2_path = os.path.join(_repo_root(), "resources", "algebras", "cyclic2.ua")
    c2 = AlgebraIO.readAlgebraFile(c2_path)
    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)
    try:
        writer = AlgebraWriter(c2, path)
        assert not hasattr(writer, "flush")
        with pytest.raises(AttributeError):
            writer.flush()
    finally:
        os.unlink(path)