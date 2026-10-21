# coding: utf-8
"""Dual-runtime randomized parity harness (Jython 2.7 + CPython 3).

Given a seed, build a small random algebra with ``Algebras.makeRandomAlgebra``
(Java ``Random``-matched) plus other seed-derived inputs, then snapshot a
cross-section of org.uacalc results as a JSON-friendly dict. The same function
runs under Jython (Java UACalc) and CPython (uacalc_lib wrapper).
"""
from __future__ import print_function, absolute_import

import os
import re
import sys
import tempfile

from org.uacalc.alg import (
    Algebras,
    FreeAlgebra,
    Malcev,
    ProductAlgebra,
    QuotientAlgebra,
)
from org.uacalc.alg.conlat import BasicPartition, CongruenceLattice
from org.uacalc.alg.op import OperationSymbol, Operations
from org.uacalc.alg.sublat import BasicSet, SubalgebraLattice
from org.uacalc.io import AlgebraIO
from org.uacalc.lat import Lattices, OrderedSets
from org.uacalc.terms import NonVariableTerm, Terms, VariableImp
from org.uacalc.util import IntArray, SequenceGenerator

from random_parity_config import (  # noqa: E402
    CI_SEEDS,
    DEFAULT_CASE_TIMEOUT,
    FAMILIES,
    XFAILS,
    family_for_seed,
)

# Re-export config names so `from random_parity import CI_SEEDS` still works.
_ = (CI_SEEDS, DEFAULT_CASE_TIMEOUT, FAMILIES, XFAILS, family_for_seed)


class Rng(object):
    """Minimal LCG, identical on Jython 2.7 and CPython 3."""

    def __init__(self, seed):
        self.state = (int(seed) ^ 0x9E3779B9) & 0xFFFFFFFF

    def next(self):
        self.state = (self.state * 1664525 + 1013904223) & 0xFFFFFFFF
        return self.state

    def randint(self, a, b):
        if b <= a:
            return a
        return a + (self.next() % (b - a + 1))

    def choice(self, seq):
        return seq[self.randint(0, len(seq) - 1)]


def _exc_name(exc):
    name = type(exc).__name__
    if "." in name:
        name = name.split(".")[-1]
    if name.startswith("Py") and len(name) > 2 and name[2].isupper():
        name = name[2:]
    return name


def _safe(fn):
    try:
        return fn()
    except Exception:
        e = sys.exc_info()[1]
        return {"error": _exc_name(e)}
    except:
        # Jython: java.lang.Exception is not always a Python Exception.
        e = sys.exc_info()[1]
        return {"error": _exc_name(e)}


def _as_int(x):
    if x is None:
        return None
    return int(x)


def _as_bool(x):
    if x is None:
        return None
    if isinstance(x, bool):
        return x
    text = str(x).lower()
    if text == "true":
        return True
    if text == "false":
        return False
    return bool(x)


def _int_list(seq):
    if seq is None:
        return None
    try:
        return [_as_int(x) for x in list(seq)]
    except Exception:
        return None


def _ia(vals):
    if sys.platform.startswith("java"):
        from jarray import array as _jarray
        return _jarray([int(x) for x in vals], "i")
    return [int(x) for x in vals]


def _snap(a):
    if a is None:
        return None
    try:
        return [int(a[i]) for i in range(len(a))]
    except Exception:
        try:
            return [int(x) for x in list(a)]
        except Exception:
            return None


def _varmap(pairs):
    try:
        from java.util import HashMap
        m = HashMap()
        for k, v in pairs:
            m.put(k, v)
        return m
    except ImportError:
        out = {}
        for k, v in pairs:
            out[k] = v
        return out


def _part(p):
    if p is None:
        return None
    arr = _int_list(p.toArray()) if hasattr(p, "toArray") else None
    blocks = None
    try:
        raw = p.getBlocks()
        blocks = sorted([sorted(_int_list(b) or []) for b in list(raw)])
    except Exception:
        blocks = None
    nblocks = None
    try:
        nblocks = _as_int(p.numberOfBlocks())
    except Exception:
        pass
    return {
        "string": str(p),
        "array": arr,
        "blocks": blocks,
        "nblocks": nblocks,
    }


def _parts(seq):
    if seq is None:
        return None
    items = [_part(p) for p in list(seq)]
    items.sort(key=lambda d: (d or {}).get("string") or "")
    return items


def _bset(s):
    if s is None:
        return None
    arr = None
    if hasattr(s, "toArray"):
        arr = _int_list(s.toArray())
    elif hasattr(s, "to_array"):
        arr = _int_list(s.to_array())
    if arr is None:
        try:
            arr = _int_list(s)
        except Exception:
            arr = None
    return {"string": str(s), "elements": arr}


def _op_values(op, n):
    arity = _as_int(op.arity())
    iva = op.intValueAt
    if arity == 0:
        return [_as_int(iva([]))]
    if arity == 1:
        return [_as_int(iva([i])) for i in range(n)]
    if arity == 2:
        return [_as_int(iva([i, j])) for i in range(n) for j in range(n)]
    if arity == 3 and n <= 2:
        return [
            _as_int(iva([i, j, k]))
            for i in range(n)
            for j in range(n)
            for k in range(n)
        ]
    return {"arity": arity, "skipped": "high_arity"}


def _alg_tables(alg):
    n = _as_int(alg.cardinality())
    rows = []
    for op in list(alg.operations()):
        sym = op.symbol()
        name = str(sym.name() if hasattr(sym, "name") else sym)
        rows.append(
            {
                "symbol": name,
                "arity": _as_int(op.arity()),
                "values": _op_values(op, n),
            }
        )
    return rows


def _term_str(t):
    if t is None:
        return None
    return str(t).replace(" ", "")


def _partition_string(rng, n):
    parent = list(range(n))

    def _root(x):
        while parent[x] != x:
            x = parent[x]
        return x

    merges = rng.randint(0, n)
    i = 0
    while i < merges:
        a = rng.randint(0, n - 1)
        b = rng.randint(0, n - 1)
        ra, rb = _root(a), _root(b)
        parent[ra] = rb
        i += 1
    groups = {}
    for x in range(n):
        r = _root(x)
        groups.setdefault(r, []).append(x)
    keys = sorted(groups.keys())
    parts = []
    for k in keys:
        parts.append(" ".join(str(v) for v in groups[k]))
    return "|" + "|".join(parts) + "|"


def _subset(rng, n):
    out = []
    for i in range(n):
        if rng.randint(0, 1) == 1:
            out.append(i)
    if not out:
        out.append(0)
    return out


def _unary_only(arities):
    for a in arities:
        if int(a) > 1:
            return False
    return True


def snapshot_alg(alg):
    return {
        "name": str(alg.getName()),
        "card": _as_int(alg.cardinality()),
        "isUnary": _as_bool(alg.isUnary()),
        "isIdempotent": _as_bool(alg.isIdempotent()),
        "isTotal": _as_bool(alg.isTotal()),
        "tables": _alg_tables(alg),
    }


def snapshot_sg(alg, rng, n):
    gens = _subset(rng, n)
    sl = alg.sub()
    sg = sl.sg(gens)
    Sg = sl.Sg(gens)
    return {
        "gens": gens,
        "sg": _bset(sg),
        "Sg_card": _as_int(Sg.cardinality()),
        "sub_card": _as_int(sl.cardinality()),
        "sgClose_empty": _safe(lambda: _int_list(alg.sgClose([])) if hasattr(alg, "sgClose") else None),
    }


def snapshot_product(alg, n):
    if n > 3:
        return {"skipped": "size"}
    prod = ProductAlgebra([alg, alg])
    return {
        "card": _as_int(prod.cardinality()),
        "factors": _as_int(prod.numberOfFactors()) if hasattr(prod, "numberOfFactors") else 2,
        "calcCard": _safe(lambda: _as_int(ProductAlgebra.calcCard([n, n]))),
    }


def snapshot_quotient(alg):
    con = alg.con()
    n = _as_int(alg.cardinality())
    a, b = 0, min(1, n - 1)
    cong = con.Cg(a, b)
    q = QuotientAlgebra(alg, cong)
    return {
        "cong": _part(cong),
        "card": _as_int(q.cardinality()),
        "getCongruence": _part(q.getCongruence()) if hasattr(q, "getCongruence") else None,
    }


def snapshot_hom(alg, n):
    ident = list(range(n))
    const0 = [0] * n
    return {
        "id": _as_bool(Algebras.isHomomorphism(ident, alg, alg)),
        "const0": _as_bool(Algebras.isHomomorphism(const0, alg, alg)),
    }


def snapshot_free(alg, n, arities):
    out = {}
    if n <= 3:
        out["f1"] = _safe(lambda: _as_int(FreeAlgebra(alg, 1).cardinality()))
    else:
        out["f1"] = {"skipped": "size"}
    if n == 2:
        out["f2"] = _safe(lambda: _as_int(FreeAlgebra(alg, 2).cardinality()))
    else:
        out["f2"] = {"skipped": "size"}
    return out


def snapshot_con(alg, rng, n):
    con = CongruenceLattice(alg)
    a, b = 0, min(1, n - 1)
    cg = con.Cg(a, b)
    jis = _safe(lambda: _parts(con.joinIrreducibles()))
    mis = _safe(lambda: _parts(con.meetIrreducibles()))
    atoms = _safe(lambda: _parts(con.atoms()))
    coatoms = _safe(lambda: _parts(con.coatoms()))
    principals = _safe(lambda: _parts(con.principals()))
    type_set = _safe(lambda: sorted(_as_int(x) for x in list(con.typeSet())))
    perm = _safe(lambda: _as_int(con.permutabilityLevel()))
    dist = _safe(lambda: _as_bool(con.isDistributive()))
    zero, one = con.zero(), con.one()
    # commutator2 builds congruence-as-algebra + Delta; keep it on n<=3
    # and rely on DEFAULT_CASE_TIMEOUT (15s) so a hang cannot stall CI.
    if n <= 3:
        c2_zo = _safe(lambda: _part(con.commutator2(zero, one)))
        c2_oo = _safe(lambda: _part(con.commutator2(one, one)))
    else:
        c2_zo = {"skipped": "size"}
        c2_oo = {"skipped": "size"}
    return {
        "card": _as_int(con.cardinality()),
        "cg": _part(cg),
        "joinIrreducibles": jis,
        "meetIrreducibles": mis,
        "atoms": atoms,
        "coatoms": coatoms,
        "principals": principals,
        "typeSet": type_set,
        "permutabilityLevel": perm,
        "isDistributive": dist,
        "join_zero_one": _part(con.join(zero, one)),
        "meet_zero_one": _part(con.meet(zero, one)),
        "leq_zero_one": _as_bool(con.leq(zero, one)),
        "commutator2_zero_one": c2_zo,
        "commutator2_one_one": c2_oo,
    }


def snapshot_sub(alg, rng, n):
    sl = SubalgebraLattice(alg)
    gens = _subset(rng, n)
    return {
        "card": _as_int(sl.cardinality()),
        "sg": _bset(sl.sg(gens)),
        "Sg_card": _as_int(sl.Sg(gens).cardinality()),
        "joinIrreducibles_n": _safe(lambda: len(list(sl.joinIrreducibles()))),
        "zero": _bset(sl.zero()),
        "one": _bset(sl.one()),
    }


def snapshot_partitions(rng, n):
    p1 = BasicPartition(_partition_string(rng, n))
    p2 = BasicPartition(_partition_string(rng, n))
    z = BasicPartition.zero(n)
    o = BasicPartition.one(n)
    joined = p1.join(p2)
    met = p1.meet(p2)
    arr = _int_list(p1.toArray())
    rt = BasicPartition(arr)
    return {
        "p1": _part(p1),
        "p2": _part(p2),
        "join": _part(joined),
        "meet": _part(met),
        "leq": _as_bool(p1.leq(p2)),
        "leq_zero": _as_bool(z.leq(p1)),
        "leq_one": _as_bool(p1.leq(o)),
        "roundtrip_eq": _as_bool(p1.equals(rt)),
        "roundtrip": _part(rt),
        "isInitialLex": _safe(lambda: _as_bool(p1.isInitialLexRepresentative())),
        "universeSize": _as_int(p1.universeSize()),
        "isRelated_01": _safe(lambda: _as_bool(p1.isRelated(0, min(1, n - 1)))),
    }


def snapshot_terms(alg, n, arities):
    arity0 = int(arities[0])
    x0 = VariableImp("x0")
    x1 = VariableImp("x1")
    if arity0 <= 0:
        t = Terms.stringToTerm("r0()")
    elif arity0 == 1:
        t = Terms.stringToTerm("r0(x0)")
    else:
        t = Terms.stringToTerm("r0(x0,x1)")
    pairs = [(x0, 0)]
    if arity0 >= 2:
        pairs.append((x1, min(1, n - 1)))
    mmap = _varmap(pairs)
    ev = _safe(lambda: _as_int(t.intEval(alg, mmap)))
    interp = _safe(lambda: _op_values(t.interpretation(alg), n))
    eq_op = None
    try:
        op0 = list(alg.operations())[0]
        iv = t.interpretation(alg)
        eq_op = _op_values(iv, n) == _op_values(op0, n)
    except Exception:
        eq_op = {"error": _exc_name(sys.exc_info()[1])}
    flat = _safe(lambda: _term_str(Terms.flatten(t) if arity0 == 2 else t))
    return {
        "term": _term_str(t),
        "isaVariable": _as_bool(t.isaVariable()) if hasattr(t, "isaVariable") else False,
        "eval": ev,
        "interpretation": interp,
        "equals_op0": eq_op,
        "flatten": flat,
        "valid_var": _as_bool(Terms.isValidVarString("x0")),
        "valid_op": _as_bool(Terms.isValidOpNameString("r0")),
        "const": _term_str(NonVariableTerm.makeConstantTerm(OperationSymbol("c", 0))),
    }


def snapshot_malcev(alg, n, arities):
    unary = _unary_only(arities)
    out = {}
    # Unary clones have no Malcev term; Java malcevTerm(alg) NPEs on a null
    # ProgressReport.addStartLine in that case (known Java bug). Skip unaries.
    if unary:
        out["malcevTerm"] = {"skipped": "unary"}
    elif n <= 2:
        out["malcevTerm"] = _safe(lambda: _term_str(Malcev.malcevTerm(alg)))
    else:
        out["malcevTerm"] = {"skipped": "size"}
    if n == 2 and not unary:
        out["majorityTerm"] = _safe(lambda: _term_str(Malcev.majorityTerm(alg)))
        out["minorityTerm"] = _safe(lambda: _term_str(Malcev.minorityTerm(alg)))
    else:
        out["majorityTerm"] = {"skipped": "size"}
        out["minorityTerm"] = {"skipped": "size"}
    return out


def snapshot_lat(alg, rng, n):
    con = alg.con()
    univ = list(con.universe())
    maxs = _safe(lambda: _parts(OrderedSets.maximals(univ, con)))
    # 2-chain join is a lattice on both sides. Random join tables are not
    # compared: Java sometimes adds a bottom instead of returning null.
    chain = Operations.makeIntOperation(OperationSymbol("v", 2), 2, [0, 1, 1, 1])
    lat_chain = Lattices.latticeFromJoin("chain2j", chain)
    zero, one = con.zero(), con.one()
    return {
        "con_card": _as_int(con.cardinality()),
        "maximals": maxs,
        "latticeFromJoin_chain": None if lat_chain is None else _as_int(lat_chain.cardinality()),
        "con_join": _part(con.join(zero, one)),
        "con_meet": _part(con.meet(zero, one)),
        "con_leq": _as_bool(con.leq(zero, one)),
    }


def snapshot_util(rng, n):
    seq = [rng.randint(0, n - 1) for _i in range(min(3, n + 1))]
    ia = IntArray(seq)
    start = [0] * min(2, max(1, n - 1))
    buf = _ia(start)
    collected = [_snap(buf)]
    inc = SequenceGenerator.sequenceIncrementor(buf, max(1, n - 1))
    steps = 0
    while inc.increment() and steps < 8:
        collected.append(_snap(buf))
        steps += 1
    psize = min(n, 4)
    nblocks = max(1, min(2, psize))
    part0 = SequenceGenerator.initialPartition(psize, nblocks)
    pbuf = _ia(_snap(part0) if part0 is not None else [0] * psize)
    pinc = SequenceGenerator.partitionArrayIncrementor(pbuf, nblocks)
    psteps = [_snap(pbuf)]
    k = 0
    while pinc.increment() and k < 6:
        psteps.append(_snap(pbuf))
        k += 1
    return {
        "intarray": {
            "seq": seq,
            "toString": str(ia),
            "universeSize": _as_int(ia.universeSize()),
            "toArray": _int_list(ia.toArray()),
            "isConstant": _as_bool(ia.isConstant()),
            "isIdempotent": _safe(lambda: _as_bool(ia.isIdempotent())),
        },
        "sequenceIncrementor": collected,
        "initialPartition": _snap(part0),
        "partitionArrayIncrementor": psteps,
    }


def snapshot_basicset(rng, n):
    # Split the universe so union cannot hit Java's duplicate-preserving bug.
    cut = rng.randint(0, n)
    a = list(range(0, cut))
    b = list(range(cut, n))
    if not a:
        a = [0]
        b = [i for i in b if i != 0]
    sa = BasicSet(a)
    sb = BasicSet(b) if b else BasicSet.EMPTY_SET
    return {
        "a": _bset(sa),
        "b": _bset(sb),
        "union": _bset(sa.union(sb)),
        "intersection": _bset(sa.intersection(sb)),
        "leq": _as_bool(sa.leq(sb)),
        "contains0": _as_bool(sa.contains(0)),
    }


def snapshot_io(alg):
    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)
    try:
        AlgebraIO.writeAlgebraFile(alg, path)
        back = AlgebraIO.readAlgebraFile(path)
        fh = open(path, "r")
        try:
            raw = fh.read()
        finally:
            fh.close()
        norm = re.sub(r"\s+", " ", raw).strip()
        return {
            "roundtrip": snapshot_alg(back),
            "xml_len": len(norm),
            "xml_has_name": ("RAlg" in norm),
            "xml_has_card": ('<cardinality>' + str(int(alg.cardinality())) + '</cardinality>') in raw.replace(" ", ""),
        }
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


def _jsonify(obj):
    """Force a snapshot into JSON-serializable Python types (Jython + CPython)."""
    if obj is None or isinstance(obj, bool):
        return obj
    if isinstance(obj, (int, float)):
        return obj
    try:
        unicode  # noqa: F821 — Jython 2
        str_types = (str, unicode)  # noqa: F821
    except NameError:
        str_types = (str,)
    if isinstance(obj, str_types):
        return str(obj)
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out[str(k)] = _jsonify(v)
        return out
    if isinstance(obj, (list, tuple)):
        return [_jsonify(x) for x in list(obj)]
    # Java Integer / Long / Boolean leftover
    try:
        if obj is True or obj is False:
            return bool(obj)
        return int(obj)
    except Exception:
        return str(obj)


def run_seed(seed):
    """Return a JSON-friendly snapshot for ``seed`` (Jython + CPython)."""
    seed = int(seed)
    n, arities = family_for_seed(seed)
    rng = Rng(seed * 10007 + 13)
    alg = Algebras.makeRandomAlgebra(n, list(arities), seed)
    snap = {
        "seed": seed,
        "n": n,
        "arities": list(arities),
        "alg": _safe(lambda: snapshot_alg(alg)),
        "sg": _safe(lambda: snapshot_sg(alg, rng, n)),
        "product": _safe(lambda: snapshot_product(alg, n)),
        "quotient": _safe(lambda: snapshot_quotient(alg)),
        "hom": _safe(lambda: snapshot_hom(alg, n)),
        "free": _safe(lambda: snapshot_free(alg, n, arities)),
        "con": _safe(lambda: snapshot_con(alg, rng, n)),
        "sub": _safe(lambda: snapshot_sub(alg, rng, n)),
        "part": _safe(lambda: snapshot_partitions(rng, n)),
        "terms": _safe(lambda: snapshot_terms(alg, n, arities)),
        "malcev": _safe(lambda: snapshot_malcev(alg, n, arities)),
        "lat": _safe(lambda: snapshot_lat(alg, rng, n)),
        "util": _safe(lambda: snapshot_util(rng, n)),
        "basicset": _safe(lambda: snapshot_basicset(rng, n)),
        "io": _safe(lambda: snapshot_io(alg)),
    }
    return _jsonify(snap)


def xfail_reason(seed, path):
    return XFAILS.get((int(seed), path))


def main(argv=None):
    import json
    argv = list(sys.argv[1:] if argv is None else argv)
    seed = 0
    if argv:
        seed = int(argv[0])
    env_seed = os.environ.get("RANDOM_PARITY_SEED")
    if env_seed:
        seed = int(env_seed)
    result = run_seed(seed)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
