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
    from uacalc_lib.alg import CongruenceLattice

    return CongruenceLattice(alg or _c2())


# --- CongruenceLattice type theory (Rust stubs; Python org shim uses TypeFinder) ---


@pytest.mark.xfail(
    reason="Rust gap: CongruenceLattice.type_ji is a stub (always 0) and is not bound on uacalc_lib",
    strict=True,
)
def test_rust_gap_type_ji_bound():
    assert hasattr(_con(), "type_ji")


@pytest.mark.xfail(
    reason="Rust gap: CongruenceLattice.type_interval is a stub (always 0) and is not bound on uacalc_lib",
    strict=True,
)
def test_rust_gap_type_interval_bound():
    assert hasattr(_con(), "type_interval")


@pytest.mark.xfail(
    reason="Rust gap: CongruenceLattice.type_set is a stub Err and is not bound on uacalc_lib",
    strict=True,
)
def test_rust_gap_type_set_bound():
    assert hasattr(_con(), "type_set")


@pytest.mark.xfail(
    reason="Rust gap: CongruenceLattice.get_type_finder is a stub Err and is not bound on uacalc_lib",
    strict=True,
)
def test_rust_gap_get_type_finder_bound():
    con = _con()
    assert hasattr(con, "get_type_finder") or hasattr(con, "getTypeFinder")


@pytest.mark.xfail(
    reason="Rust gap: CongruenceLattice.coatoms returns None (Java throws UnsupportedOperationException); not bound on uacalc_lib",
    strict=True,
)
def test_rust_gap_con_coatoms_bound():
    assert hasattr(_con(), "coatoms")


# --- Python-only Malcev idempotent methods not ported to uacalc_lib ---


def _malcev_missing(name):
    alg = uacalc_lib.alg
    return hasattr(alg, name) or hasattr(alg, "Malcev") and hasattr(alg.Malcev, name)


@pytest.mark.xfail(
    reason="Rust gap: sdIdempotent is not ported to uacalc_lib",
    strict=True,
)
def test_rust_gap_sd_idempotent():
    assert _malcev_missing("sd_idempotent") or _malcev_missing("sdIdempotent")


@pytest.mark.xfail(
    reason="Rust gap: cpIdempotent is not ported to uacalc_lib",
    strict=True,
)
def test_rust_gap_cp_idempotent():
    assert _malcev_missing("cp_idempotent") or _malcev_missing("cpIdempotent")


@pytest.mark.xfail(
    reason="Rust gap: cubeTermBlockerIdempotent is not ported to uacalc_lib",
    strict=True,
)
def test_rust_gap_cube_term_blocker_idempotent():
    assert _malcev_missing("cube_term_blocker_idempotent") or _malcev_missing(
        "cubeTermBlockerIdempotent"
    )


@pytest.mark.xfail(
    reason="Rust gap: typeSetIdempotent is not ported to uacalc_lib",
    strict=True,
)
def test_rust_gap_type_set_idempotent():
    assert _malcev_missing("type_set_idempotent") or _malcev_missing("typeSetIdempotent")


@pytest.mark.xfail(
    reason="Rust gap: typesInSofAIdempotent is not ported to uacalc_lib",
    strict=True,
)
def test_rust_gap_types_in_sof_a_idempotent():
    assert _malcev_missing("types_in_sof_a_idempotent") or _malcev_missing(
        "typesInSofAIdempotent"
    )


@pytest.mark.xfail(
    reason="Rust gap: typesInSofAStrictlySimpleIdempotent is not ported to uacalc_lib",
    strict=True,
)
def test_rust_gap_types_in_sof_a_strictly_simple_idempotent():
    assert _malcev_missing("types_in_sof_a_strictly_simple_idempotent") or _malcev_missing(
        "typesInSofAStrictlySimpleIdempotent"
    )


@pytest.mark.xfail(
    reason="Rust gap: typesInSofAIRobustDecompdempotent is not ported to uacalc_lib",
    strict=True,
)
def test_rust_gap_types_in_sof_a_i_robust_decomp_idempotent():
    assert _malcev_missing("types_in_sof_a_i_robust_decompdempotent") or _malcev_missing(
        "typesInSofAIRobustDecompdempotent"
    )


@pytest.mark.xfail(
    reason="Rust gap: omittedIdealIdempotent is not ported to uacalc_lib",
    strict=True,
)
def test_rust_gap_omitted_ideal_idempotent():
    assert _malcev_missing("omitted_ideal_idempotent") or _malcev_missing(
        "omittedIdealIdempotent"
    )


# --- TermOperationImp cannot build a value table ---


@pytest.mark.xfail(
    reason="Rust gap: TermOperationImp.make_table always Err (immutable interpretation)",
    strict=True,
)
def test_rust_gap_term_operation_imp_make_table():
    from uacalc_lib.terms import NonVariableTerm, TermOperationImp, VariableImp

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


@pytest.mark.xfail(
    reason="Rust gap: QuotientOperation.value_at_arrays is unimplemented",
    strict=True,
)
def test_rust_gap_quotient_value_at_arrays():
    from uacalc_lib.alg import QuotientAlgebra

    alg = _c2()
    con = alg.con() if hasattr(alg, "con") else _con(alg)
    q = QuotientAlgebra("Q", alg, con.cg(0, 1) if hasattr(con, "cg") else con.Cg(0, 1))
    op = list(q.operations())[0]
    fn = getattr(op, "value_at_arrays", None) or getattr(op, "valueAt", None)
    assert callable(fn)
    # Java evaluates the whole-array form; the Rust stub returns Err.
    got = fn([[0], [1]]) if fn.__code__.co_argcount != 1 else fn([0, 1])
    assert got is not None


# --- Projective plane → ternary ring ---


@pytest.mark.xfail(
    reason="Rust gap: projective plane to ternary ring conversion unimplemented",
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
    reason="Rust gap: BigProductAlgebra.universe is an empty iterator",
    strict=True,
)
def test_rust_gap_big_product_universe():
    from uacalc_lib.alg import BigProductAlgebra

    bp = BigProductAlgebra.new_power(_c2(), 2)
    fn = getattr(bp, "universe", None)
    assert callable(fn)
    items = list(fn())
    assert len(items) == 4


@pytest.mark.xfail(
    reason="Rust gap: BigProductAlgebra.is_similar_to always returns false",
    strict=True,
)
def test_rust_gap_big_product_is_similar_to():
    from uacalc_lib.alg import BigProductAlgebra

    alg = _c2()
    bp = BigProductAlgebra.new_power(alg, 2)
    fn = getattr(bp, "is_similar_to", None) or getattr(bp, "isSimilarTo", None)
    assert callable(fn)
    assert fn(bp) is True


@pytest.mark.xfail(
    reason="Rust gap: BigProductAlgebra.update_similarity_type is a no-op",
    strict=True,
)
def test_rust_gap_big_product_update_similarity_type():
    from uacalc_lib.alg import BigProductAlgebra

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
    assert list(after.symbols() if hasattr(after, "symbols") else after) 


# --- SubalgebraLattice atoms/coatoms/is_smaller_than (uacalc_lib, not the org shim) ---


@pytest.mark.xfail(
    reason="Rust gap: SubalgebraLattice.atoms is a TODO stub returning None",
    strict=True,
)
def test_rust_gap_sublat_atoms():
    sl = _c2().sub() if hasattr(_c2(), "sub") else None
    if sl is None:
        from uacalc_lib.alg import SubalgebraLattice

        sl = SubalgebraLattice(_c2())
    atoms = sl.atoms()
    assert atoms is not None
    assert len(list(atoms)) > 0


@pytest.mark.xfail(
    reason="Rust gap: SubalgebraLattice.coatoms is a TODO stub returning None",
    strict=True,
)
def test_rust_gap_sublat_coatoms():
    from uacalc_lib.alg import SubalgebraLattice

    sl = SubalgebraLattice(_c2())
    coatoms = sl.coatoms()
    assert coatoms is not None
    assert len(list(coatoms)) > 0
