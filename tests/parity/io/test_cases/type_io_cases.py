"""Type-specific AlgebraWriter/AlgebraReader parity cases.

For each Java algebra kind: same-runtime write then read, plus reading a
Jython-written fixture (Java write, both read). Python write / Java read is
the same XML as the capture cases when the writer matches Java.
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = """
import os, tempfile
from org.uacalc.io import AlgebraIO, AlgebraReader, AlgebraWriter
from org.uacalc.alg import (
    FreeAlgebra, ProductAlgebra, PowerAlgebra, QuotientAlgebra, Subalgebra,
    BigProductAlgebra, SubProductAlgebra,
)
from org.uacalc.util import IntArray
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
ba2 = AlgebraIO.readAlgebraFile("resources/algebras/ba2.ua")

def _wr(alg):
    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)
    AlgebraIO.writeAlgebraFile(alg, path)
    read = AlgebraIO.readAlgebraFile(path)
    os.unlink(path)
    return read

def _xml_tags(alg):
    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)
    AlgebraIO.writeAlgebraFile(alg, path)
    text = open(path).read()
    os.unlink(path)
    tags = []
    for tag in (
        "basicAlgebra", "freeAlgebra", "productAlgebra", "powerAlgebra",
        "quotientAlgebra", "subAlgebra", "bigProductAlgebra", "subProductAlgebra",
        "productElem", "generators", "rootFactors", "factors", "superAlgebra",
        "congruence", "subUniverse", "powers",
    ):
        if "<" + tag + ">" in text:
            tags.append(tag)
    return tags
"""

_SKIP = dict(skip_string_check=True)

_PROD_XFAIL = (
    "Owner/library: AlgebraWriter.writeProductAlgebra is a hardcoded stub on "
    "Box<dyn SmallAlgebra<i32>> (no factors). The org shim still routes "
    "ProductAlgebra through to_basic_algebra(), so Python writes "
    "<basicAlgebra> tables. Java writes <productAlgebra> and rereads a "
    "ProductAlgebra."
)

_PWR_XFAIL = (
    "Owner/library: AlgebraWriter.writePowerAlgebra is a hardcoded stub "
    "(placeholder power=2 and nested basic of the power, not the root). "
    "The org shim still routes PowerAlgebra through to_basic_algebra()."
)

_QUOT_XFAIL = (
    "Owner/library: AlgebraWriter.writeQuotientAlgebra is a hardcoded stub "
    "(partition 0,1). The org shim still routes QuotientAlgebra through "
    "to_basic_algebra()."
)

_SUB_XFAIL = (
    "Owner/library: AlgebraWriter.writeSubalgebra is a hardcoded stub "
    "(subUniverse 0,1). The org shim still routes Subalgebra through "
    "to_basic_algebra()."
)

_SUBPROD_XFAIL = (
    "Owner/library: AlgebraWriter.writeSubProductAlgebra is a hardcoded stub "
    "(no IntArray generators). The org shim still routes SubProductAlgebra "
    "through to_basic_algebra()."
)

_READER_NESTED_XFAIL = (
    "Owner/library: Rust AlgebraReader only materializes BasicAlgebra. "
    "Java reconstructs ProductAlgebra / PowerAlgebra / QuotientAlgebra / "
    "Subalgebra / BigProductAlgebra / SubProductAlgebra from nested XML. "
    "Python keeps the last nested basicAlgebra (often a factor or the "
    "super algebra)."
)

_FA_JAVA_BUG_XFAIL = (
    "Known Java bug: AlgebraReader has no freeAlgebra end-element handler, "
    "so write-then-read returns the nested generating algebra instead of "
    "F(n). Python rebuilds F(n) from the <freeAlgebra> XML. Java golden "
    "values are left unchanged."
)

TEST_CASES = [
    TestCaseSpec(
        id="wr_free_c2_f1",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + """
f = FreeAlgebra(c2, 1)
f.setName("F1")
""",
        call="_wr(f)",
        description="write then read F(1) over cyclic2",
        xfail_reason=_FA_JAVA_BUG_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="wr_free_c3_f1",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + """
f = FreeAlgebra(c3, 1)
f.setName("F1")
""",
        call="_wr(f)",
        description="write then read F(1) over cyclic3",
        xfail_reason=_FA_JAVA_BUG_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="wr_free_lat2_f1",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + """
f = FreeAlgebra(lat2, 1)
f.setName("F1")
""",
        call="_wr(f)",
        description="write then read F(1) over lat2 (Java rereads lat2, not F(1))",
        xfail_reason=_FA_JAVA_BUG_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="wr_free_ba2_f1",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + """
f = FreeAlgebra(ba2, 1)
f.setName("F1")
""",
        call="_wr(f)",
        description="write then read F(1) over ba2 (Java rereads ba2, not F(1))",
        xfail_reason=_FA_JAVA_BUG_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="xml_free_c2_f1_tags",
        method="AlgebraWriter.writeAlgebraXML",
        setup=_SETUP + """
f = FreeAlgebra(c2, 1)
f.setName("F1")
""",
        call="_xml_tags(f)",
        description="FreeAlgebra write emits <freeAlgebra> + productElem tags",
        **_SKIP
    ),
    TestCaseSpec(
        id="read_special_free_c2_f1",
        method="AlgebraReader.readAlgebraFile",
        setup=_SETUP,
        call='AlgebraReader("resources/special/free_c2_f1.ua").readAlgebraFile()',
        description="Java-written F(1)/C2 fixture (cross: Java write, both read)",
        xfail_reason=_FA_JAVA_BUG_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="wr_prod_c2_c2",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + """
prod = ProductAlgebra([c2, c2])
""",
        call="_wr(prod)",
        description="write then read ProductAlgebra(C2, C2)",
        xfail_reason=_PROD_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="xml_prod_c2_c2_tags",
        method="AlgebraWriter.writeAlgebraXML",
        setup=_SETUP + """
prod = ProductAlgebra([c2, c2])
""",
        call="_xml_tags(prod)",
        description="ProductAlgebra write tags (Java productAlgebra vs Python basicAlgebra)",
        xfail_reason=_PROD_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="read_special_product",
        method="AlgebraReader.readAlgebraFile",
        setup=_SETUP,
        call='AlgebraReader("resources/special/product_c2_c2.ua").readAlgebraFile()',
        description="Java-written product fixture (cross: Java write, both read)",
        xfail_reason=_READER_NESTED_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="wr_pwr_c2_2",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + """
pwr = PowerAlgebra(c2, 2)
""",
        call="_wr(pwr)",
        description="write then read PowerAlgebra(C2, 2)",
        xfail_reason=_PWR_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="xml_pwr_c2_2_tags",
        method="AlgebraWriter.writeAlgebraXML",
        setup=_SETUP + """
pwr = PowerAlgebra(c2, 2)
""",
        call="_xml_tags(pwr)",
        description="PowerAlgebra write tags (Java powerAlgebra vs Python basicAlgebra)",
        xfail_reason=_PWR_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="read_special_power",
        method="AlgebraReader.readAlgebraFile",
        setup=_SETUP,
        call='AlgebraReader("resources/special/power_c2_sq.ua").readAlgebraFile()',
        description="Java-written power fixture (cross: Java write, both read)",
        xfail_reason=_READER_NESTED_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="wr_quot_c2",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + """
cons = list(c2.con().universe())
quot = QuotientAlgebra(c2, cons[0])
""",
        call="_wr(quot)",
        description="write then read QuotientAlgebra of C2 by |0|1|",
        xfail_reason=_QUOT_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="xml_quot_c2_tags",
        method="AlgebraWriter.writeAlgebraXML",
        setup=_SETUP + """
cons = list(c2.con().universe())
quot = QuotientAlgebra(c2, cons[0])
""",
        call="_xml_tags(quot)",
        description="QuotientAlgebra write tags (Java quotientAlgebra vs Python basicAlgebra)",
        xfail_reason=_QUOT_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="read_special_quotient",
        method="AlgebraReader.readAlgebraFile",
        setup=_SETUP,
        call='AlgebraReader("resources/special/quotient_example.ua").readAlgebraFile()',
        description="Java-written quotient fixture (cross: Java write, both read)",
        xfail_reason=_READER_NESTED_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="wr_sub_c2",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + """
sub = Subalgebra(c2, [0])
""",
        call="_wr(sub)",
        description="write then read Subalgebra of C2 on {0}",
        xfail_reason=_SUB_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="xml_sub_c2_tags",
        method="AlgebraWriter.writeAlgebraXML",
        setup=_SETUP + """
sub = Subalgebra(c2, [0])
""",
        call="_xml_tags(sub)",
        description="Subalgebra write tags (Java subAlgebra vs Python basicAlgebra)",
        xfail_reason=_SUB_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="read_special_subalgebra",
        method="AlgebraReader.readAlgebraFile",
        setup=_SETUP,
        call='AlgebraReader("resources/special/subalgebra_example.ua").readAlgebraFile()',
        description="Java-written subalgebra fixture (cross: Java write, both read)",
        xfail_reason=_READER_NESTED_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="wr_subprod_c2",
        method="AlgebraIO.writeAlgebraFile",
        setup=_SETUP + """
bp = BigProductAlgebra(c2, 2)
sp = SubProductAlgebra("SP", bp, [IntArray([0, 0]), IntArray([1, 1])])
""",
        call="_wr(sp)",
        description="write then read SubProductAlgebra of C2^2 on two gens",
        xfail_reason=_SUBPROD_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="xml_subprod_c2_tags",
        method="AlgebraWriter.writeAlgebraXML",
        setup=_SETUP + """
bp = BigProductAlgebra(c2, 2)
sp = SubProductAlgebra("SP", bp, [IntArray([0, 0]), IntArray([1, 1])])
""",
        call="_xml_tags(sp)",
        description="SubProductAlgebra write tags (Java subProductAlgebra vs Python basicAlgebra)",
        xfail_reason=_SUBPROD_XFAIL,
        **_SKIP
    ),
    TestCaseSpec(
        id="read_special_subproduct",
        method="AlgebraReader.readAlgebraFile",
        setup=_SETUP,
        call='AlgebraReader("resources/special/subproduct_c2.ua").readAlgebraFile()',
        description="Java-written subproduct fixture (cross: Java write, both read)",
        xfail_reason=_READER_NESTED_XFAIL,
        **_SKIP
    ),
]
