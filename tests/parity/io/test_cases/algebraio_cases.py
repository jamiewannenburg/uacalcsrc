"""Test case specifications for org.uacalc.io behavioral parity."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_READ_SETUP = """
from org.uacalc.io import AlgebraIO, AlgebraReader, AlgebraWriter, Mace4Reader, BadAlgebraFileException
"""

_STREAM_SETUP = """
import sys
from org.uacalc.io import AlgebraIO, AlgebraReader, Mace4Reader
path = %r
if sys.platform.startswith("java"):
    from java.io import FileInputStream
    stream = FileInputStream(path)
else:
    stream = open(path, "rb")
"""

_WRITE_SETUP = """
import os, tempfile
from org.uacalc.io import AlgebraIO, AlgebraWriter
alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
fd, OUT_PATH = tempfile.mkstemp(suffix=%r)
os.close(fd)
CAPTURE_PATH = OUT_PATH
"""

TEST_CASES = [
    TestCaseSpec(
        id="read_cyclic2",
        method="AlgebraIO.readAlgebraFile",
        setup=_READ_SETUP,
        call='AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")',
        description="Read cyclic2 algebra from file",
        skip_string_check=True,
        notes="Java toString is Class@ident; Python str is semantic.",
    ),
    TestCaseSpec(
        id="read_cyclic3",
        method="AlgebraIO.readAlgebraFile",
        setup=_READ_SETUP,
        call='AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")',
        description="Read cyclic3 algebra from file",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="read_lat2",
        method="AlgebraIO.readAlgebraFile",
        setup=_READ_SETUP,
        call='AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")',
        description="Read lat2 algebra from file",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="read_n5",
        method="AlgebraIO.readAlgebraFile",
        setup=_READ_SETUP,
        call='AlgebraIO.readAlgebraFile("resources/algebras/n5.ua")',
        description="Read n5 algebra from file",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="read_invalid",
        method="AlgebraIO.readAlgebraFile",
        setup=_READ_SETUP,
        call='AlgebraIO.readAlgebraFile("resources/algebras/invalid_parity.ua")',
        description="Reading invalid file should raise",
        expected_exception="NumberFormatException",
    ),
    TestCaseSpec(
        id="read_nonexistent",
        method="AlgebraIO.readAlgebraFile",
        setup=_READ_SETUP,
        call='AlgebraIO.readAlgebraFile("resources/algebras/nonexistent.ua")',
        description="Reading nonexistent file should raise",
        expected_exception="FileNotFoundException",
        xfail_reason=(
            "Java raises FileNotFoundException; Python currently raises "
            "ValueError('No algebras found in file')."
        ),
    ),
    TestCaseSpec(
        id="read_from_stream_cyclic2",
        method="AlgebraIO.readAlgebraFromStream",
        setup=_STREAM_SETUP % "resources/algebras/cyclic2.ua",
        call="AlgebraIO.readAlgebraFromStream(stream)",
        description="Read cyclic2 from an input stream",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="read_algebra_list_file",
        method="AlgebraIO.readAlgebraListFile",
        setup=_READ_SETUP,
        call='AlgebraIO.readAlgebraListFile("resources/algebras/cyclic2_cyclic3_list.ua")',
        description="Read multi-algebra list file (Java returns the last algebra only)",
        skip_string_check=True,
        xfail_reason=(
            "Java AlgebraIO.readAlgebraListFile returns only the last algebra (C3). "
            "Current uacalc_lib returns both C2 and C3."
        ),
    ),
    TestCaseSpec(
        id="read_algebra_list_from_stream",
        method="AlgebraIO.readAlgebraListFromStream",
        setup=_STREAM_SETUP % "resources/algebras/cyclic2.ua",
        call="AlgebraIO.readAlgebraListFromStream(stream)",
        description="Read algebra list from stream (Java API returns a single algebra)",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="write_algebra_file_xml",
        method="AlgebraIO.writeAlgebraFile",
        setup=_WRITE_SETUP % ".ua",
        call="AlgebraIO.writeAlgebraFile(alg, OUT_PATH)",
        description="Write algebra XML to a .ua path",
        capture_file=True,
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="write_algebra_file_old_style",
        method="AlgebraIO.writeAlgebraFile",
        setup=_WRITE_SETUP % ".alg",
        call="AlgebraIO.writeAlgebraFile(alg, OUT_PATH, True)",
        description="Write old-style .alg file",
        capture_file=True,
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="convert_to_xml",
        method="AlgebraIO.convertToXML",
        setup="""
import os, tempfile
from org.uacalc.io import AlgebraIO
alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
# Stable basename so Java File.getName() / Python file_name() match the golden
# algName (legacy .alg format names the algebra after the file).
alg_dir = tempfile.mkdtemp()
alg_path = os.path.join(alg_dir, "tmpZWnK01.alg")
AlgebraIO.writeAlgebraFile(alg, alg_path, True)
AlgebraIO.convertToXML(alg_path)
# Java ExtFileFilter.splitOffExtension uses File.getName(), so the XML
# is written next to cwd as <basename>.xml, not beside the temp .alg file.
CAPTURE_PATH = os.path.join(os.getcwd(), "tmpZWnK01.xml")
OUT_PATH = CAPTURE_PATH
""",
        call="None",
        description="Convert a .alg file to XML beside it",
        capture_file=True,
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="reader_read_algebra_file",
        method="AlgebraReader.readAlgebraFile",
        setup=_READ_SETUP + """
import sys
path = "resources/algebras/cyclic2.ua"
if sys.platform.startswith("java"):
    from java.io import File
    reader = AlgebraReader(File(path))
else:
    reader = AlgebraReader(path)
""",
        call="reader.readAlgebraFile()",
        description="AlgebraReader.readAlgebraFile on cyclic2",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="reader_read_algebra_from_stream",
        method="AlgebraReader.readAlgebraFromStream",
        setup=_STREAM_SETUP % "resources/algebras/cyclic3.ua"
        + """
if sys.platform.startswith("java"):
    reader = AlgebraReader(stream)
else:
    data = stream.read()
    stream.close()
    reader = AlgebraReader(data)
""",
        call="reader.readAlgebraFromStream()",
        description="AlgebraReader.readAlgebraFromStream on cyclic3",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="reader_read_algebra_list_file",
        method="AlgebraReader.readAlgebraListFile",
        setup=_READ_SETUP + """
import sys
path = "resources/algebras/cyclic2_cyclic3_list.ua"
if sys.platform.startswith("java"):
    from java.io import File
    reader = AlgebraReader(File(path))
else:
    reader = AlgebraReader(path)
""",
        call="reader.readAlgebraListFile()",
        description="AlgebraReader.readAlgebraListFile",
        skip_string_check=True,
        xfail_reason=(
            "Java AlgebraReader.readAlgebraListFile returns only the last algebra (C3). "
            "Current uacalc_lib returns both C2 and C3."
        ),
    ),
    TestCaseSpec(
        id="writer_write_algebra_xml",
        method="AlgebraWriter.writeAlgebraXML",
        setup=_WRITE_SETUP % ".xml" + """
writer = AlgebraWriter(alg, OUT_PATH)
""",
        call="writer.writeAlgebraXML()",
        description="AlgebraWriter.writeAlgebraXML",
        capture_file=True,
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="writer_write_algebra",
        method="AlgebraWriter.writeAlgebra",
        setup=_WRITE_SETUP % ".xml" + """
writer = AlgebraWriter(alg, OUT_PATH)
""",
        call="writer.writeAlgebra()",
        description="AlgebraWriter.writeAlgebra",
        capture_file=True,
        skip_string_check=True,
        xfail_reason=(
            "Java writeAlgebra() does not close/flush the PrintWriter, so the "
            "captured file is empty. Python writes immediately."
        ),
    ),
    TestCaseSpec(
        id="writer_write_basic_algebra",
        method="AlgebraWriter.writeBasicAlgebra",
        setup=_WRITE_SETUP % ".xml" + """
writer = AlgebraWriter(alg, OUT_PATH)
""",
        call="writer.writeBasicAlgebra()",
        description="AlgebraWriter.writeBasicAlgebra",
        capture_file=True,
        skip_string_check=True,
        xfail_reason=(
            "Java writeBasicAlgebra() does not close/flush the PrintWriter, so the "
            "captured file is empty. Python writes immediately and includes <universe>."
        ),
    ),
    TestCaseSpec(
        id="mace4_parse_algebra",
        method="Mace4Reader.parseAlgebra",
        setup="""
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
        call="reader.parseAlgebra()",
        description="Mace4Reader.parseAlgebra on KR-8.model",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="mace4_parse_algebra_list",
        method="Mace4Reader.parseAlgebraList",
        setup="""
import sys
from org.uacalc.io import Mace4Reader
path = "resources/mace4/KR-8-expl.model"
if sys.platform.startswith("java"):
    from java.io import FileInputStream
    reader = Mace4Reader(FileInputStream(path))
else:
    fh = open(path, "rb")
    reader = Mace4Reader(fh)
""",
        call="reader.parseAlgebraList()",
        description="Mace4Reader.parseAlgebraList on KR-8-expl.model",
        skip_string_check=True,
    ),
    TestCaseSpec(
        id="mace4_missing_file",
        method="Mace4Reader.parseAlgebra",
        setup="""
import sys
from org.uacalc.io import Mace4Reader
path = "resources/mace4/does_not_exist.model"
if sys.platform.startswith("java"):
    from java.io import FileInputStream
    reader = Mace4Reader(FileInputStream(path))
else:
    reader = Mace4Reader.open(path) if hasattr(Mace4Reader, "open") else None
    if reader is None:
        fh = open(path, "rb")
        reader = Mace4Reader(fh)
""",
        call="reader.parseAlgebra()",
        description="Mace4Reader on a missing file should raise",
        expected_exception="FileNotFoundException",
    ),
]
