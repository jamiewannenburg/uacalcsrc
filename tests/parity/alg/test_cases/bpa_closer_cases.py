"""Golden parity cases for BigProductAlgebra and CloserTiming."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec

_SETUP = r"""
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import BigProductAlgebra, CloserTiming, ProductAlgebra
from org.uacalc.util import IntArray
c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
c3 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua")
lat2 = AlgebraIO.readAlgebraFile("resources/algebras/lat2.ua")
m3 = AlgebraIO.readAlgebraFile("resources/algebras/m3.ua")
bp2 = BigProductAlgebra(c2, 2)
bp3 = BigProductAlgebra(c3, 2)
bp_lat = BigProductAlgebra(lat2, 2)
bp_prod = BigProductAlgebra([c2, c3])
bp_m3 = BigProductAlgebra(m3, 1)
g00 = IntArray([0, 0])
g11 = IntArray([1, 1])
g01 = IntArray([0, 1])
ct = CloserTiming(bp2, None)
ct.updatePass(2)

def _ias(lst):
    if lst is None:
        return None
    out = []
    for x in list(lst):
        try:
            out.append([int(v) for v in list(x)])
        except TypeError:
            getter = getattr(x, "getArray", None) or getattr(x, "to_array", None)
            out.append([int(v) for v in getter()] if callable(getter) else x)
    return out

def _map_items(m):
    if m is None:
        return None
    try:
        return sorted((int(k), int(m[k])) for k in m)
    except Exception:
        return sorted((int(k), int(v)) for k, v in m.items())

def _op_meta(alg):
    names = []
    for op in list(alg.operations()):
        sym = op.symbol()
        name = sym.name() if callable(getattr(sym, "name", None)) else str(sym)
        names.append((str(name), int(op.arity())))
    names.sort()
    return names

def _factor_cards(factors):
    if factors is None:
        return None
    return [int(f.cardinality()) for f in list(factors)]
"""

_BOOL = dict(skip_string_check=True, notes="Java str(true/false) vs Python str(True/False).")
_LIST = dict(skip_string_check=True, notes="Java List/Map toString vs Python list/dict.")
_NONE = dict(skip_string_check=True, notes="Java null vs Python None.")

TEST_CASES = [
    TestCaseSpec(
        id="bpa_c2_2_card",
        method="BigProductAlgebra.cardinality",
        setup=_SETUP,
        call="bp2.cardinality()",
        description="C2^2 big product cardinality",
    ),
    TestCaseSpec(
        id="bpa_c3_2_card",
        method="BigProductAlgebra.cardinality",
        setup=_SETUP,
        call="bp3.cardinality()",
        description="C3^2 big product cardinality",
    ),
    TestCaseSpec(
        id="bpa_prod_card",
        method="BigProductAlgebra.cardinality",
        setup=_SETUP,
        call="bp_prod.cardinality()",
        description="C2 x C3 big product cardinality",
    ),
    TestCaseSpec(
        id="bpa_c2_2_nfactors",
        method="BigProductAlgebra.getNumberOfFactors",
        setup=_SETUP,
        call="bp2.getNumberOfFactors()",
        description="C2^2 number of factors",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_c2_2_is_power",
        method="BigProductAlgebra.isPower",
        setup=_SETUP,
        call="bp2.isPower()",
        description="C2^2 is a power",
        **_BOOL
    ),
    TestCaseSpec(
        id="bpa_prod_is_power",
        method="BigProductAlgebra.isPower",
        setup=_SETUP,
        call="bp_prod.isPower()",
        description="C2 x C3 is not a power",
        **_BOOL
    ),
    TestCaseSpec(
        id="bpa_c2_2_powers",
        method="BigProductAlgebra.getPowers",
        setup=_SETUP,
        call="None if bp2.getPowers() is None else [int(x) for x in list(bp2.getPowers())]",
        description="C2^2 getPowers",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_prod_powers",
        method="BigProductAlgebra.getPowers",
        setup=_SETUP,
        call="bp_prod.getPowers()",
        description="non-power getPowers is null",
        **_NONE
    ),
    TestCaseSpec(
        id="bpa_c2_2_root",
        method="BigProductAlgebra.rootFactors",
        setup=_SETUP,
        call="_factor_cards(bp2.rootFactors())",
        description="C2^2 rootFactors cardinalities",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_prod_root",
        method="BigProductAlgebra.rootFactors",
        setup=_SETUP,
        call="bp_prod.rootFactors()",
        description="non-power rootFactors is null",
        **_NONE
    ),
    TestCaseSpec(
        id="bpa_c2_2_factors",
        method="BigProductAlgebra.factors",
        setup=_SETUP,
        call="_factor_cards(bp2.factors())",
        description="C2^2 factors cardinalities",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_prod_factors",
        method="BigProductAlgebra.factors",
        setup=_SETUP,
        call="_factor_cards(bp_prod.factors())",
        description="C2 x C3 factors cardinalities",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_c2_2_size_mult",
        method="BigProductAlgebra.sizeMultiplicities",
        setup=_SETUP,
        call="_map_items(bp2.sizeMultiplicities())",
        description="C2^2 size multiplicities",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_prod_size_mult",
        method="BigProductAlgebra.sizeMultiplicities",
        setup=_SETUP,
        call="_map_items(bp_prod.sizeMultiplicities())",
        description="C2 x C3 size multiplicities",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_c2_2_proj",
        method="BigProductAlgebra.projection",
        setup=_SETUP,
        call="bp2.projection(0).cardinality()",
        description="C2^2 projection(0) cardinality",
    ),
    TestCaseSpec(
        id="bpa_c2_2_proj_kernel",
        method="BigProductAlgebra.projectionKernel",
        setup=_SETUP,
        call="bp2.projectionKernel(0)",
        description="projectionKernel is a Java stub (null)",
        **_NONE
    ),
    TestCaseSpec(
        id="bpa_c2_2_ops",
        method="BigProductAlgebra.operations",
        setup=_SETUP,
        call="_op_meta(bp2)",
        description="C2^2 operation names and arities",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_lat2_2_ops",
        method="BigProductAlgebra.operations",
        setup=_SETUP,
        call="_op_meta(bp_lat)",
        description="lat2^2 operation names and arities",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_c2_2_value_at",
        method="BigProductAlgebra.operations",
        setup=_SETUP,
        call="[int(x) for x in list(list(bp2.operations())[0].valueAt([[0, 0], [1, 1]]))]",
        description="C2^2 first op valueAt on two tuples",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_c2_2_constants",
        method="BigProductAlgebra.getConstants",
        setup=_SETUP,
        call="_ias(bp2.getConstants())",
        description="C2^2 constants",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_lat2_2_constants",
        method="BigProductAlgebra.getConstants",
        setup=_SETUP,
        call="_ias(bp_lat.getConstants())",
        description="lat2^2 constants",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_c2_2_sg_close",
        method="BigProductAlgebra.sgClose",
        setup=_SETUP,
        call="sorted(_ias(bp2.sgClose([g00, g11])))",
        description="sgClose of the diagonal in C2^2",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_c3_2_sg_close",
        method="BigProductAlgebra.sgClose",
        setup=_SETUP,
        call="sorted(_ias(bp3.sgClose([IntArray([0, 0]), IntArray([1, 1])])))",
        description="sgClose of two diagonal gens in C3^2",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_lat2_2_sg_close",
        method="BigProductAlgebra.sgClose",
        setup=_SETUP,
        call="sorted(_ias(bp_lat.sgClose([g00, g11])))",
        description="sgClose of the diagonal in lat2^2",
        **_LIST
    ),
    TestCaseSpec(
        id="bpa_c2_2_name",
        method="BigProductAlgebra.getName",
        setup=_SETUP,
        call="str(bp2.getName())",
        description="default name of C2^2",
    ),
    TestCaseSpec(
        id="bpa_make_tables",
        method="BigProductAlgebra.makeOperationTables",
        setup=_SETUP,
        call="(bp2.makeOperationTables(), bp2.cardinality())[1]",
        description="makeOperationTables is a no-op that returns",
    ),
    TestCaseSpec(
        id="bpa_const_symbol_null",
        method="BigProductAlgebra.getConstantSymbol",
        setup=_SETUP,
        call="bp2.getConstantSymbol(None)",
        description="getConstantSymbol(null) is null",
        **_NONE
    ),
    TestCaseSpec(
        id="ct_update_pass",
        method="CloserTiming.updatePass",
        setup=_SETUP,
        call="(CloserTiming(bp3, None).updatePass(4), 4)[1]",
        description="updatePass returns after resetting counters",
    ),
    TestCaseSpec(
        id="ct_increment_next",
        method="CloserTiming.incrementNextPassSize",
        setup=_SETUP,
        call="(ct.incrementNextPassSize(), ct.incrementNextPassSize(), 1)[2]",
        description="incrementNextPassSize is callable",
    ),
    TestCaseSpec(
        id="ct_increment_apps",
        method="CloserTiming.incrementApps",
        setup=_SETUP,
        call="(ct.incrementApps(), ct.incrementApps(), bp2.getNumberOfFactors())[2]",
        description="incrementApps a few times stays below timing thresholds",
    ),
    TestCaseSpec(
        id="ct_null_alg",
        method="CloserTiming.updatePass",
        setup=_SETUP,
        call="CloserTiming(None, None)",
        description="CloserTiming(null, null) NPE",
        expected_exception="NullPointerException",
    ),
]
