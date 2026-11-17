# Dual-runtime surface for org.uacalc.io file-level contracts.
from __future__ import print_function

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parity_probe import section

from org.uacalc.io import (
    AlgebraIO,
    AlgebraReader,
    AlgebraWriter,
    ExtFileFilter,
    Mace4Reader,
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
C2 = os.path.join(ROOT, "resources", "algebras", "cyclic2.ua")
LIST = os.path.join(ROOT, "resources", "algebras", "cyclic2_cyclic3_list.ua")
MACE = os.path.join(ROOT, "resources", "mace4", "KR-8.model")


def _stream(path):
    if sys.platform.startswith("java"):
        from java.io import FileInputStream
        return FileInputStream(path)
    return open(path, "rb")


def main():
    section(
        "parseLine",
        lambda: print(
            "parseLine",
            AlgebraIO.parseLine("7"),
            AlgebraIO.parseLine("% x"),
        ),
    )
    alg = AlgebraIO.readAlgebraFile(C2)
    section("readFile", lambda: print("readFile", alg.cardinality()))
    stream = _stream(C2)
    section(
        "readStream",
        lambda: print(
            "readStream",
            AlgebraIO.readAlgebraFromStream(stream).cardinality(),
        ),
    )
    lst = AlgebraIO.readAlgebraListFile(LIST)
    section("listFile", lambda: print("listFile", len(list(lst))))
    stream2 = _stream(C2)
    one = AlgebraIO.readAlgebraListFromStream(stream2)

    def _list_stream():
        print(
            "listStream",
            one.cardinality() if hasattr(one, "cardinality") else len(list(one)),
        )

    section("listStream", _list_stream)

    reader = AlgebraReader(C2)
    section("readerFile", lambda: print("readerFile", reader.readAlgebraFile().cardinality()))
    stream3 = _stream(C2)

    def _reader_stream():
        if sys.platform.startswith("java"):
            r2 = AlgebraReader(stream3)
            print("readerStream", r2.readAlgebraFromStream().cardinality())
        else:
            data = stream3.read()
            stream3.close()
            r2 = AlgebraReader(data)
            print("readerStream", r2.readAlgebraFromStream().cardinality())

    section("readerStream", _reader_stream)
    rlist = AlgebraReader(LIST)
    section("readerList", lambda: print("readerList", len(list(rlist.readAlgebraListFile()))))
    stream4 = _stream(C2)

    def _reader_list_stream():
        if sys.platform.startswith("java"):
            r3 = AlgebraReader(stream4)
            print("readerListStream", r3.readAlgebraListFromStream() is not None)
        else:
            data = stream4.read()
            stream4.close()
            r3 = AlgebraReader(data)
            print("readerListStream", r3.readAlgebraListFromStream() is not None)

    section("readerListStream", _reader_list_stream)

    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)

    def _writer():
        writer = AlgebraWriter(alg, path)
        writer.writeAlgebra()
        writer.writeBasicAlgebra()
        writer.flush()
        writer.writeAlgebraXML()
        print("writerXML", os.path.getsize(path) > 0)
        os.unlink(path)

    section("writerXML", _writer)

    filt = ExtFileFilter("UA Files", "ua")
    if sys.platform.startswith("java"):
        from java.io import File

        ua = File("foo.ua")
        txt = File("foo.txt")
    else:
        ua = "foo.ua"
        txt = "foo.txt"
    section(
        "accept",
        lambda: print(
            "accept",
            filt.accept(ua),
            filt.accept(txt),
            filt.getDescription(),
        ),
    )
    section(
        "ext",
        lambda: print(
            "ext",
            ExtFileFilter.getExtension(ua),
            list(ExtFileFilter.splitOffExtension(ua)),
        ),
    )
    stream5 = _stream(MACE)
    mace = Mace4Reader(stream5)
    section("mace", lambda: print("mace", mace.parseAlgebra().cardinality()))
    section(
        "ord",
        lambda: print(
            "ord",
            Mace4Reader.isOrdinaryCharacter("a"),
            Mace4Reader.isSpecialCharacter("+"),
        ),
    )


if __name__ == "__main__":
    main()