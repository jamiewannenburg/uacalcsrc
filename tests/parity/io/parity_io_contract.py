#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contract snapshot for ``org.uacalc.io`` (CONTRACT.md).

Runs under CPython (``PYTHONPATH=python``) and Jython (``CLASSPATH=jars/uacalc.jar``).
Stdout is compared to checked-in fixtures by ``test_io_contract_golden.py``.
"""
from __future__ import print_function

import os
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# CPython: repo shims; Jython: Java package from jar.
if not sys.platform.startswith("java"):
    _py = os.path.join(REPO_ROOT, "python")
    if _py not in sys.path:
        sys.path.insert(0, _py)

from tests.parity.io.io_parity_helpers import (  # noqa: E402
    MACE4_LIST_FILE,
    MACE4_SINGLE_FILE,
    MULTI_ALGEBRA_LIST_FILE,
    SAMPLE_ALGEBRA_FILES,
    SPECIAL_FIXTURE_NAMES,
    algebra_path,
    format_algebra_list_summaries,
    format_algebra_summary,
    mace4_path,
    normalize_xml_file,
    semantic_algebra_summary,
    special_path,
)

from org.uacalc.io import (  # noqa: E402
    AlgebraIO,
    AlgebraReader,
    AlgebraWriter,
    BadAlgebraFileException,
    Mace4Reader,
)


def _stream_arg(data):
    """CPython shim accepts bytes; Jython Java APIs need ``java.io.InputStream``."""
    if sys.platform.startswith("java"):
        from java.io import ByteArrayInputStream

        if isinstance(data, str):
            data = bytearray(data)
        elif not isinstance(data, bytearray):
            data = bytearray(data)
        return ByteArrayInputStream(data)
    return data


def _runtime():
    return "jython" if sys.platform.startswith("java") else "cpython"


def _case(name):
    print("CASE: " + name)


def _ok(label):
    print("OK: " + label)


def _fail(label, exc):
    print("FAIL: " + label + ": " + str(exc.__class__.__name__) + ": " + str(exc))


def _run(label, fn):
    try:
        fn()
        _ok(label)
    except Exception as exc:  # noqa: BLE001 — parity reports any failure
        _fail(label, exc)


def main():
    print("MODULE: org.uacalc.io.contract")
    print("RUNTIME: " + _runtime())

    for fname in SAMPLE_ALGEBRA_FILES:
        path = algebra_path(fname)
        if not os.path.isfile(path):
            continue
        spath = path

        _case("AlgebraIO.readAlgebraFile:" + fname)
        alg = AlgebraIO.readAlgebraFile(spath)
        print("SUMMARY: " + format_algebra_summary(semantic_algebra_summary(alg)))

        _case("AlgebraIO.readAlgebraFromStream:" + fname)
        with open(path, "rb") as fh:
            data = fh.read()
        alg2 = AlgebraIO.readAlgebraFromStream(_stream_arg(data))
        print("SUMMARY: " + format_algebra_summary(semantic_algebra_summary(alg2)))

        _case("AlgebraReader.readAlgebraFile:" + fname)
        reader = AlgebraReader(spath)
        alg3 = reader.readAlgebraFile()
        print("SUMMARY: " + format_algebra_summary(semantic_algebra_summary(alg3)))

        _case("AlgebraReader.readAlgebraFromStream:" + fname)
        reader2 = AlgebraReader(_stream_arg(data))
        alg4 = reader2.readAlgebraFromStream()
        print("SUMMARY: " + format_algebra_summary(semantic_algebra_summary(alg4)))

    list_path = algebra_path(MULTI_ALGEBRA_LIST_FILE)
    if os.path.isfile(list_path):
        lstr = list_path
        _case("AlgebraIO.readAlgebraListFile")
        algs = AlgebraIO.readAlgebraListFile(lstr)
        print("LIST:\n" + format_algebra_list_summaries(algs))

        _case("AlgebraReader.readAlgebraListFile")
        rlist = AlgebraReader(lstr).readAlgebraListFile()
        print("LIST:\n" + format_algebra_list_summaries(rlist))

    mace_single = mace4_path(MACE4_SINGLE_FILE)
    if os.path.isfile(mace_single):
        _case("Mace4Reader.parseAlgebra")
        with open(mace_single, "rb") as fh:
            mdata = fh.read()
        malg = Mace4Reader(_stream_arg(mdata)).parseAlgebra()
        print("SUMMARY: " + format_algebra_summary(semantic_algebra_summary(malg)))

    mace_list = mace4_path(MACE4_LIST_FILE)
    if os.path.isfile(mace_list):
        _case("Mace4Reader.parseAlgebraList")
        with open(mace_list, "rb") as fh:
            mlist = Mace4Reader(_stream_arg(fh.read())).parseAlgebraList()
        if not isinstance(mlist, list):
            mlist = list(mlist)
        print("LIST:\n" + format_algebra_list_summaries(mlist))

    for sname in SPECIAL_FIXTURE_NAMES:
        sp = special_path(sname)
        if not os.path.isfile(sp):
            print("SKIP: special:" + sname)
            continue
        _case("AlgebraReader.special:" + sname)
        salg = AlgebraReader(sp).readAlgebraFile()
        print("SUMMARY: " + format_algebra_summary(semantic_algebra_summary(salg)))

    cyclic3 = algebra_path("cyclic3.ua")
    if os.path.isfile(cyclic3):
        alg = AlgebraIO.readAlgebraFile(cyclic3)

        def _write_roundtrip():
            with tempfile.NamedTemporaryFile(suffix=".ua", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                AlgebraIO.writeAlgebraFile(alg, tmp_path)
                round_trip = AlgebraIO.readAlgebraFile(tmp_path)
                print(
                    "SUMMARY: "
                    + format_algebra_summary(semantic_algebra_summary(round_trip))
                )
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

        _case("AlgebraIO.writeAlgebraFile.roundtrip")
        _run("write/read roundtrip", _write_roundtrip)

        def _writer_xml():
            with tempfile.NamedTemporaryFile(suffix=".ua", delete=False) as tmp2:
                tmp2_path = tmp2.name
            try:
                AlgebraWriter(alg, tmp2_path).writeAlgebraXML()
                print("XML_NORM: " + normalize_xml_file(tmp2_path))
            finally:
                try:
                    os.unlink(tmp2_path)
                except OSError:
                    pass

        _case("AlgebraWriter.writeAlgebraXML")
        _run("AlgebraWriter.writeAlgebraXML", _writer_xml)

    invalid = algebra_path("invalid_parity.ua")
    if os.path.isfile(invalid):
        _case("BadAlgebraFileException.readAlgebraFile")
        _run(
            "catch BadAlgebraFileException",
            lambda: _read_invalid_or_reraise(invalid),
        )


def _read_invalid_or_reraise(path):
    try:
        AlgebraIO.readAlgebraFile(path)
    except:  # noqa: E722 — Jython raises Java exception types
        return
    raise AssertionError("expected readAlgebraFile to fail on invalid fixture")


if __name__ == "__main__":
    main()
