"""Parity cases for wrapped org.uacalc.io constructors with no tests."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SKIP = dict(skip_string_check=True)


def _c(cid, method, setup, call, description, **kw):
    return TestCaseSpec(
        id=cid,
        method=method,
        setup=setup,
        call=call,
        description=description,
        **kw
    )


TEST_CASES = [
    _c(
        "ctor_algebra_reader",
        "AlgebraReader.AlgebraReader",
        """
import sys
from org.uacalc.io import AlgebraReader
path = "resources/algebras/cyclic2.ua"
if sys.platform.startswith("java"):
    from java.io import File
    reader = AlgebraReader(File(path))
else:
    reader = AlgebraReader(path)
""",
        "reader.readAlgebraFile().cardinality()",
        "AlgebraReader constructor then read cyclic2",
        **_SKIP
    ),
    _c(
        "ctor_algebra_reader_c3",
        "AlgebraReader.AlgebraReader",
        """
import sys
from org.uacalc.io import AlgebraReader
path = "resources/algebras/cyclic3.ua"
if sys.platform.startswith("java"):
    from java.io import File
    reader = AlgebraReader(File(path))
else:
    reader = AlgebraReader(path)
""",
        "reader.readAlgebraFile().cardinality()",
        "AlgebraReader constructor then read cyclic3",
        **_SKIP
    ),
    _c(
        "ctor_algebra_writer",
        "AlgebraWriter.AlgebraWriter",
        """
import os, tempfile
from org.uacalc.io import AlgebraIO, AlgebraWriter
alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
fd, OUT_PATH = tempfile.mkstemp(suffix=".xml")
os.close(fd)
CAPTURE_PATH = OUT_PATH
writer = AlgebraWriter(alg, OUT_PATH)
""",
        "writer.writeAlgebraXML() or True",
        "AlgebraWriter constructor then writeAlgebraXML",
        capture_file=True,
        **_SKIP
    ),
    _c(
        "ctor_mace4_reader",
        "Mace4Reader.Mace4Reader",
        """
import sys
from org.uacalc.io import Mace4Reader
path = "resources/mace4/KR-8.model"
if sys.platform.startswith("java"):
    from java.io import FileInputStream
    reader = Mace4Reader(FileInputStream(path))
else:
    fh = open(path, "rb")
    reader = Mace4Reader(fh)
""",
        "reader.parseAlgebra().cardinality()",
        "Mace4Reader constructor then parseAlgebra",
        **_SKIP
    ),
    _c(
        "ctor_ext_file_filter",
        "ExtFileFilter.ExtFileFilter",
        """
from org.uacalc.io import ExtFileFilter
filt = ExtFileFilter("UA Files", "ua")
""",
        "filt.getDescription()",
        "ExtFileFilter constructor description",
    ),
    _c(
        "ctor_bad_algebra_file_exc",
        "BadAlgebraFileException.BadAlgebraFileException",
        """
from org.uacalc.io import BadAlgebraFileException
exc = BadAlgebraFileException("bad file")
""",
        "str(exc)",
        "BadAlgebraFileException constructor message",
        skip_string_check=True,
        notes="Exception toString prefix differs (Java vs Python).",
    ),
]
