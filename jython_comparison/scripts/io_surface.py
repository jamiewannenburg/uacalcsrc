# Dual-runtime surface for org.uacalc.io file-level contracts.
from __future__ import print_function

import os
import sys
import tempfile

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
    print("parseLine", AlgebraIO.parseLine("7"), AlgebraIO.parseLine("% x"))
    alg = AlgebraIO.readAlgebraFile(C2)
    print("readFile", alg.cardinality())
    stream = _stream(C2)
    print("readStream", AlgebraIO.readAlgebraFromStream(stream).cardinality())
    lst = AlgebraIO.readAlgebraListFile(LIST)
    print("listFile", len(list(lst)))
    stream2 = _stream(C2)
    one = AlgebraIO.readAlgebraListFromStream(stream2)
    print("listStream", one.cardinality() if hasattr(one, "cardinality") else len(list(one)))

    reader = AlgebraReader(C2)
    print("readerFile", reader.readAlgebraFile().cardinality())
    stream3 = _stream(C2)
    if sys.platform.startswith("java"):
        r2 = AlgebraReader(stream3)
        print("readerStream", r2.readAlgebraFromStream().cardinality())
    else:
        data = stream3.read()
        stream3.close()
        r2 = AlgebraReader(data)
        print("readerStream", r2.readAlgebraFromStream().cardinality())
    rlist = AlgebraReader(LIST)
    print("readerList", len(list(rlist.readAlgebraListFile())))
    stream4 = _stream(C2)
    if sys.platform.startswith("java"):
        r3 = AlgebraReader(stream4)
        print("readerListStream", r3.readAlgebraListFromStream() is not None)
    else:
        data = stream4.read()
        stream4.close()
        r3 = AlgebraReader(data)
        print("readerListStream", r3.readAlgebraListFromStream() is not None)

    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)
    writer = AlgebraWriter(alg, path)
    writer.writeAlgebra()
    writer.writeBasicAlgebra()
    writer.flush()
    writer.writeAlgebraXML()
    print("writerXML", os.path.getsize(path) > 0)
    os.unlink(path)

    filt = ExtFileFilter("UA Files", "ua")
    if sys.platform.startswith("java"):
        from java.io import File
        ua = File("foo.ua")
        txt = File("foo.txt")
    else:
        ua = "foo.ua"
        txt = "foo.txt"
    print("accept", filt.accept(ua), filt.accept(txt), filt.getDescription())
    print("ext", ExtFileFilter.getExtension(ua), list(ExtFileFilter.splitOffExtension(ua)))

    stream5 = _stream(MACE)
    mace = Mace4Reader(stream5)
    print("mace", mace.parseAlgebra().cardinality())
    print("ord", Mace4Reader.isOrdinaryCharacter("a"), Mace4Reader.isSpecialCharacter("+"))


if __name__ == "__main__":
    main()
