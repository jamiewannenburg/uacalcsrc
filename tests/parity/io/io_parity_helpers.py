"""Shared helpers for ``org.uacalc.io`` contract parity tests (CPython 3 + Jython 2.7)."""

from __future__ import print_function

import json
import os
import re
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
)

SAMPLE_ALGEBRA_FILES = (
    "cyclic2.ua",
    "cyclic3.ua",
    "lat2.ua",
    "n5.ua",
)

MULTI_ALGEBRA_LIST_FILE = "cyclic2_cyclic3_list.ua"

MACE4_SINGLE_FILE = "KR-8.model"
MACE4_LIST_FILE = "KR-8-expl.model"

SPECIAL_FIXTURE_NAMES = (
    "basic_cyclic2.ua",
    "product_c2_c2.ua",
    "quotient_example.ua",
    "subalgebra_example.ua",
    "power_c2_sq.ua",
)


def algebra_path(name):
    return os.path.join(REPO_ROOT, "resources", "algebras", name)


def mace4_path(name):
    return os.path.join(REPO_ROOT, "resources", "mace4", name)


def special_path(name):
    return os.path.join(REPO_ROOT, "resources", "special", name)


def operation_table_ints(op):
    if hasattr(op, "makeTable"):
        op.makeTable()
    elif hasattr(op, "make_table"):
        op.make_table()
    table = None
    if hasattr(op, "getTable"):
        table = op.getTable()
    elif hasattr(op, "get_table"):
        table = op.get_table()
    if table is not None:
        return [int(x) for x in table]
    return []


def _callable_attr(obj, name):
    value = getattr(obj, name, None)
    if value is None:
        return None
    if callable(value):
        return value()
    return value


def _algebra_name(alg):
    if hasattr(alg, "getName"):
        return alg.getName()
    return _callable_attr(alg, "name")


def _algebra_kind(alg):
    if hasattr(alg, "algebraType"):
        return alg.algebraType()
    return _callable_attr(alg, "algebra_type")


def _algebra_operations(alg):
    if hasattr(alg, "operations"):
        ops = alg.operations()
        return ops if ops is not None else []
    if hasattr(alg, "getOperations"):
        return alg.getOperations()
    return []


def _op_symbol_name(op):
    sym = op.symbol() if hasattr(op, "symbol") else op.getSymbol()
    if hasattr(sym, "name") and callable(sym.name):
        return sym.name()
    if hasattr(sym, "getName"):
        return sym.getName()
    return sym.name


def _op_arity(op):
    if hasattr(op, "arity"):
        ar = op.arity()
        return int(ar() if callable(ar) else ar)
    return int(op.getArity())


def semantic_algebra_summary(alg):
    """Normalized algebra summary per CONTRACT.md."""
    ops = _algebra_operations(alg)
    symbols = []
    arities = []
    tables = []
    for op in sorted(ops, key=lambda o: (_op_symbol_name(o), _op_arity(o))):
        symbols.append(_op_symbol_name(op))
        arities.append(_op_arity(op))
        tables.append(operation_table_ints(op))

    kind = _algebra_kind(alg)
    name = _algebra_name(alg)

    return {
        "name": str(name),
        "cardinality": int(alg.cardinality()),
        "kind": str(kind) if kind is not None else None,
        "symbols": symbols,
        "arities": arities,
        "tables": tables,
    }


def format_algebra_summary(summary):
    return json.dumps(summary, sort_keys=True, separators=(",", ":"))


def format_algebra_list_summaries(algebras):
    parts = [format_algebra_summary(semantic_algebra_summary(a)) for a in algebras]
    return "\n".join(parts)


def normalize_xml_text(text):
    """Canonical XML for comparison (structure + text, not byte-identical)."""
    root = ET.fromstring(text.strip())
    rough = ET.tostring(root, encoding="unicode")
    rough = re.sub(r">\s+<", "><", rough)
    return rough.strip()


def normalize_xml_file(path):
    with open(path, "r") as fh:
        return normalize_xml_text(fh.read())


def summaries_equal(a, b):
    return format_algebra_summary(a) == format_algebra_summary(b)
