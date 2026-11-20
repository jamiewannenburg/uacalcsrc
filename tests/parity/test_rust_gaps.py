"""Strict xfails that surface known Rust stubs.

Each reason starts with ``Rust gap:`` so an implementation that starts matching
Java will XPASS (and fail under ``strict=True``) until the mark is removed.

Gaps that are only visible in the Rust crate (Python ``org.uacalc`` shims already
match Java) live in ``tests/rust_gaps.rs`` as ``#[ignore]`` tests instead.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import uacalc_lib

REPO_ROOT = Path(__file__).resolve().parents[2]
ALGEBRAS = REPO_ROOT / "resources" / "algebras"


def _c2():
    return uacalc_lib.io.AlgebraReader.new_from_file(
        str(ALGEBRAS / "cyclic2.ua")
    ).read_algebra_file()


def _con(alg=None):
    return uacalc_lib.alg.CongruenceLattice(alg or _c2())


# --- CongruenceLattice type theory (Rust stubs; Python org shim uses TypeFinder) ---


def test_rust_gap_type_ji_bound():
    assert hasattr(_con(), "type_ji")


def test_rust_gap_type_interval_bound():
    assert hasattr(_con(), "type_interval")


def test_rust_gap_type_set_bound():
    assert hasattr(_con(), "type_set")


def test_rust_gap_get_type_finder_bound():
    con = _con()
    assert hasattr(con, "get_type_finder") or hasattr(con, "getTypeFinder")


def test_rust_gap_con_coatoms_bound():
    assert hasattr(_con(), "coatoms")


# --- Python-only Malcev idempotent methods not ported to uacalc_lib ---


def _malcev_missing(name):
    alg = uacalc_lib.alg
    return hasattr(alg, name) or hasattr(alg, "Malcev") and hasattr(alg.Malcev, name)


def test_rust_gap_sd_idempotent():
    assert _malcev_missing("sd_idempotent") or _malcev_missing("sdIdempotent")


def test_rust_gap_cp_idempotent():
    assert _malcev_missing("cp_idempotent") or _malcev_missing("cpIdempotent")


def test_rust_gap_cube_term_blocker_idempotent():
    assert _malcev_missing("cube_term_blocker_idempotent") or _malcev_missing(
        "cubeTermBlockerIdempotent"
    )


def test_rust_gap_type_set_idempotent():
    assert _malcev_missing("type_set_idempotent") or _malcev_missing("typeSetIdempotent")


def test_rust_gap_types_in_sof_a_idempotent():
    assert _malcev_missing("types_in_sof_a_idempotent") or _malcev_missing(
        "typesInSofAIdempotent"
    )


def test_rust_gap_types_in_sof_a_strictly_simple_idempotent():
    assert _malcev_missing("types_in_sof_a_strictly_simple_idempotent") or _malcev_missing(
        "typesInSofAStrictlySimpleIdempotent"
    )


def test_rust_gap_types_in_sof_a_i_robust_decomp_idempotent():
    assert _malcev_missing("types_in_sof_a_i_robust_decompdempotent") or _malcev_missing(
        "typesInSofAIRobustDecompdempotent"
    )


def test_rust_gap_omitted_ideal_idempotent():
    assert _malcev_missing("omitted_ideal_idempotent") or _malcev_missing(
        "omittedIdealIdempotent"
    )


# --- TermOperationImp cannot build a value table ---


def test_rust_gap_term_operation_imp_make_table():
    NonVariableTerm = uacalc_lib.terms.NonVariableTerm
    TermOperationImp = uacalc_lib.terms.TermOperationImp
    VariableImp = uacalc_lib.terms.VariableImp

    alg = _c2()
    plus = list(alg.operations())[0].symbol()
    x = VariableImp("x")
    y = VariableImp("y")
    term = NonVariableTerm(plus, [x, y])
    op = TermOperationImp(term, [x, y], alg)
    maker = getattr(op, "make_table", None) or getattr(op, "makeTable", None)
    assert callable(maker)
    maker()
    table = op.get_table() if hasattr(op, "get_table") else op.getTable()
    assert table is not None
    assert len(list(table)) == int(alg.cardinality()) ** 2


# --- Quotient operations cannot evaluate on whole value arrays ---


def test_rust_gap_quotient_value_at_arrays():
    QuotientAlgebra = uacalc_lib.alg.QuotientAlgebra

    alg = _c2()
    con = alg.con() if hasattr(alg, "con") else _con(alg)
    # Cg(0, 1) on C2 is the full congruence, so index 1 is not a quotient element.
    # The zero congruence keeps both representatives; +(0, 1) = 1 on C2.
    zero = con.zero() if hasattr(con, "zero") else con.Zero()
    q = QuotientAlgebra("Q", alg, zero)
    op = list(q.operations())[0]
    fn = getattr(op, "value_at_arrays", None) or getattr(op, "valueAt", None)
    assert callable(fn)
    got = fn([[0], [1]])
    assert list(got) == [1]


# --- Projective plane → ternary ring ---


@pytest.mark.xfail(
    reason=(
        "Known Java bug: AlgebraIO.readProjectivePlane parses the plane and "
        "returns null (org/uacalc/io/AlgebraIO.java). Rust keeps the existing "
        "'not yet implemented' error; inventing a ternary ring would diverge "
        "from Java and from python/uacalc/tests/test_algebra_io.py."
    ),
    strict=True,
)
def test_rust_gap_read_projective_plane():
    import tempfile
    import os

    handle, path = tempfile.mkstemp(suffix=".txt")
    os.close(handle)
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("0 1 2\n")
            fh.write("0 3 4\n")
            fh.write("0 5 6\n")
            fh.write("1 3 5\n")
            fh.write("1 4 6\n")
            fh.write("2 3 6\n")
            fh.write("2 4 5\n")
        alg = uacalc_lib.io.read_projective_plane(path)
        assert int(alg.cardinality()) > 0
    finally:
        os.remove(path)


# --- BigProductAlgebra Rust stubs not bound / empty ---


@pytest.mark.xfail(
    reason=(
        "Known Java bug: BigProductAlgebra does not override universe(), so "
        "GeneralAlgebra.universe() returns the unset field (null). A 4-element "
        "enumeration of cyclic2^2 would diverge from Java."
    ),
    strict=True,
)
def test_rust_gap_big_product_universe():
    BigProductAlgebra = uacalc_lib.alg.BigProductAlgebra

    bp = BigProductAlgebra.new_power(_c2(), 2)
    fn = getattr(bp, "universe", None)
    assert callable(fn)
    items = list(fn())
    assert len(items) == 4


def test_rust_gap_big_product_is_similar_to():
    BigProductAlgebra = uacalc_lib.alg.BigProductAlgebra

    alg = _c2()
    bp = BigProductAlgebra.new_power(alg, 2)
    fn = getattr(bp, "is_similar_to", None) or getattr(bp, "isSimilarTo", None)
    assert callable(fn)
    assert fn(bp) is True


def test_rust_gap_sub_product_projection_kernel():
    BigProductAlgebra = uacalc_lib.alg.BigProductAlgebra
    SubProductAlgebra = uacalc_lib.alg.SubProductAlgebra

    IntArray = uacalc_lib.util.IntArray
    c2 = _c2()
    bp = BigProductAlgebra.new_power(c2, 2)
    gens = [IntArray.from_array([0, 0]), IntArray.from_array([1, 1])]
    sp = SubProductAlgebra("SP", bp, gens, False)
    fn = getattr(sp, "projection_kernel", None) or getattr(sp, "projectionKernel", None)
    assert callable(fn), "projection_kernel should be bound on uacalc_lib.SubProductAlgebra"
    part = fn(0)
    assert part is not None
    blocks = getattr(part, "number_of_blocks", None) or getattr(part, "numberOfBlocks", None)
    assert callable(blocks)
    assert int(blocks()) >= 1


def test_rust_gap_big_product_update_similarity_type():
    BigProductAlgebra = uacalc_lib.alg.BigProductAlgebra

    bp = BigProductAlgebra.new_power(_c2(), 2)
    fn = getattr(bp, "update_similarity_type", None) or getattr(
        bp, "updateSimilarityType", None
    )
    assert callable(fn)
    before = bp.similarity_type() if hasattr(bp, "similarity_type") else None
    fn()
    after = bp.similarity_type() if hasattr(bp, "similarity_type") else None
    assert before is not None
    assert after is not None
    if hasattr(after, "get_operation_symbols"):
        symbols = list(after.get_operation_symbols())
    elif hasattr(after, "symbols"):
        symbols = list(after.symbols())
    else:
        symbols = list(after)
    assert len(symbols) >= 1 


# --- SubalgebraLattice atoms/coatoms/is_smaller_than (uacalc_lib, not the org shim) ---


@pytest.mark.xfail(
    reason=(
        "Known Java bug: SubalgebraLattice.atoms is a TODO that returns null "
        "(org/uacalc/alg/sublat/SubalgebraLattice.java). A non-empty atom list "
        "would diverge from Java."
    ),
    strict=True,
)
def test_rust_gap_sublat_atoms():
    sl = _c2().sub() if hasattr(_c2(), "sub") else None
    if sl is None:
        sl = uacalc_lib.alg.SubalgebraLattice(_c2())
    atoms = sl.atoms()
    assert atoms is not None
    assert len(list(atoms)) > 0


@pytest.mark.xfail(
    reason=(
        "Known Java bug: SubalgebraLattice.coatoms is a TODO that returns null "
        "(org/uacalc/alg/sublat/SubalgebraLattice.java). A non-empty coatom list "
        "would diverge from Java."
    ),
    strict=True,
)
def test_rust_gap_sublat_coatoms():
    sl = uacalc_lib.alg.SubalgebraLattice(_c2())
    coatoms = sl.coatoms()
    assert coatoms is not None
    assert len(list(coatoms)) > 0
