"""Typed XML write/read for Product/Power/Quotient/Subalgebra/SubProduct.

Java AlgebraWriter emits nested ``<productAlgebra>`` / ``<powerAlgebra>`` /
``<quotientAlgebra>`` / ``<subAlgebra>`` / ``<subProductAlgebra>`` instead of
flattening to ``<basicAlgebra>`` tables. The Rust ``SmallAlgebra<i32>`` writer
cannot see factors/root/congruence, so the org shim builds that XML here and
rebuilds the typed algebra when those tags are present on read.

FreeAlgebra stays on the dedicated Rust writer (coordinate tuples) and the
known Java ``</freeAlgebra>`` reader bug is unchanged.
"""

from __future__ import annotations

import os
import tempfile
from typing import Any, List, Optional
from xml.etree import ElementTree as ET

import uacalc_lib as _uacalc_lib

_io = getattr(_uacalc_lib, "io")
_LibAlgebraReader = _io.AlgebraReader
_LibAlgebraWriter = _io.AlgebraWriter

_FREE_TYPE_NAMES = ("PyFreeAlgebra", "FreeAlgebra")
_BASIC_TYPE_NAMES = ("PyBasicAlgebra", "BasicAlgebra")
_PRODUCT_TYPE_NAMES = ("PyProductAlgebra", "ProductAlgebra")
_POWER_TYPE_NAMES = ("PyPowerAlgebra", "PowerAlgebra")
_QUOTIENT_TYPE_NAMES = ("PyQuotientAlgebra", "QuotientAlgebra")
_SUB_TYPE_NAMES = ("PySubalgebra", "Subalgebra")
_SUBPROD_TYPE_NAMES = ("PySubProductAlgebra", "SubProductAlgebra")


def _tname(alg: Any) -> str:
    return type(alg).__name__


def _local(tag: str) -> str:
    if tag.startswith("{"):
        return tag.rsplit("}", 1)[-1]
    return tag


def _call(obj: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if obj is None or not hasattr(obj, name):
            continue
        val = getattr(obj, name)
        if callable(val):
            try:
                return val()
            except TypeError:
                continue
        return val
    return default


def _int_row(row: Any) -> List[int]:
    if row is None:
        return []
    for attr in ("toArray", "to_array", "getArray", "get_array"):
        fn = getattr(row, attr, None)
        if callable(fn):
            try:
                return [int(x) for x in list(fn())]
            except TypeError:
                continue
    try:
        return [int(x) for x in list(row)]
    except TypeError:
        return [int(row[i]) for i in range(len(row))]


def _xml_escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _named_desc_card_xml(alg: Any) -> str:
    parts = []
    name = _call(alg, "getName", "name")
    if name is not None and str(name):
        parts.append("    <algName>{}</algName>\n".format(_xml_escape(str(name))))
    desc = _call(alg, "getDescription", "description")
    if desc is not None and str(desc):
        parts.append("    <desc>{}</desc>\n".format(_xml_escape(str(desc))))
    card = _call(alg, "cardinality")
    if card is not None:
        parts.append("    <cardinality>{}</cardinality>\n".format(int(card)))
    return "".join(parts)


def _indent_block(text: str, prefix: str) -> str:
    lines = text.strip("\n").splitlines()
    return "\n".join(prefix + line if line.strip() else line for line in lines)


def _write_basic_document(alg: Any) -> str:
    inner = getattr(alg, "_inner", alg)
    if _tname(inner) not in _BASIC_TYPE_NAMES:
        conv = getattr(inner, "to_basic_algebra", None)
        if callable(conv):
            inner = conv()
    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)
    try:
        _LibAlgebraWriter.write_algebra_xml_to_file(inner, path)
        with open(path) as handle:
            return handle.read()
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def _basic_algebra_xml(alg: Any) -> str:
    text = _write_basic_document(alg)
    start = text.find("<basicAlgebra>")
    end = text.rfind("</basicAlgebra>")
    if start < 0 or end < 0:
        raise ValueError("basicAlgebra XML fragment missing")
    return text[start : end + len("</basicAlgebra>")]


def _read_basic_document(xml: str) -> Any:
    fd, path = tempfile.mkstemp(suffix=".ua")
    os.close(fd)
    try:
        with open(path, "w") as handle:
            handle.write(xml)
        return _LibAlgebraReader.new_from_file(path).read_algebra_file()
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def _elem_document(elem: ET.Element) -> str:
    body = ET.tostring(elem, encoding="unicode")
    return '<?xml version="1.0"?>\n<algebra>\n' + body + "\n</algebra>\n"


def _find_child(elem: ET.Element, name: str) -> Optional[ET.Element]:
    for child in list(elem):
        if _local(child.tag) == name:
            return child
    return None


def _find_children(elem: ET.Element, name: str) -> List[ET.Element]:
    return [child for child in list(elem) if _local(child.tag) == name]


def _text(elem: Optional[ET.Element]) -> str:
    if elem is None or elem.text is None:
        return ""
    return elem.text.strip()


def _parse_int_array(text: str) -> List[int]:
    parts = [p.strip() for p in text.replace("\n", ",").split(",")]
    return [int(p) for p in parts if p]


def _parse_product_elems(parent: Optional[ET.Element]) -> List[List[int]]:
    if parent is None:
        return []
    out = []
    for child in _find_children(parent, "productElem"):
        out.append(_parse_int_array("".join(child.itertext())))
    return out


def _write_int_array_xml(values: List[int], indent: str) -> str:
    joined = ",".join(str(int(v)) for v in values)
    return "{0}<intArray>\n{0}  {1}\n{0}</intArray>\n".format(indent, joined)


def write_typed_algebra_xml(algebra: Any, path: str) -> bool:
    """Write Java-shaped typed XML when ``algebra`` is a known derived kind.

    Returns True if a typed document was written, False to fall through to the
    basic-algebra writer.
    """
    alg = getattr(algebra, "_inner", algebra)
    name = _tname(alg)
    if name in _FREE_TYPE_NAMES:
        _LibAlgebraWriter.write_free_algebra_xml_to_file(alg, path)
        return True
    if name in _PRODUCT_TYPE_NAMES:
        _write_product(alg, path)
        return True
    if name in _POWER_TYPE_NAMES:
        _write_power(alg, path)
        return True
    if name in _QUOTIENT_TYPE_NAMES:
        _write_quotient(alg, path)
        return True
    if name in _SUB_TYPE_NAMES:
        _write_subalgebra(alg, path)
        return True
    if name in _SUBPROD_TYPE_NAMES:
        _write_subproduct(alg, path)
        return True
    return False


def _write_product(alg: Any, path: str) -> None:
    factors = list(_call(alg, "factors") or [])
    chunks = [_indent_block(_basic_algebra_xml(factor), "        ") for factor in factors]
    factor_xml = "".join(
        "      <factor>\n{}\n      </factor>\n".format(chunk) for chunk in chunks
    )
    xml = (
        '<?xml version="1.0"?>\n<algebra>\n  <productAlgebra>\n'
        + _named_desc_card_xml(alg)
        + "    <factors>\n"
        + factor_xml
        + "    </factors>\n  </productAlgebra>\n</algebra>\n"
    )
    with open(path, "w") as handle:
        handle.write(xml)


def _write_power(alg: Any, path: str) -> None:
    root = _call(alg, "getRoot", "get_root")
    power = int(_call(alg, "getPower", "get_power") or 0)
    root_xml = _indent_block(_basic_algebra_xml(root), "      ")
    xml = (
        '<?xml version="1.0"?>\n<algebra>\n  <powerAlgebra>\n'
        + _named_desc_card_xml(alg)
        + "    <power>{}</power>\n    <root>\n{}\n    </root>\n".format(power, root_xml)
        + "  </powerAlgebra>\n</algebra>\n"
    )
    with open(path, "w") as handle:
        handle.write(xml)


def _partition_block_string(part: Any) -> str:
    for name in ("toString", "to_string"):
        fn = getattr(part, name, None)
        if callable(fn):
            try:
                return str(fn())
            except TypeError:
                try:
                    return str(fn(None))
                except Exception:
                    pass
    return str(part)


def _partition_array(part: Any) -> List[int]:
    arr = _call(part, "toArray", "to_array", "getArray", "get_array") or []
    return [int(x) for x in list(arr)]


def _write_quotient(alg: Any, path: str) -> None:
    super_alg = _call(alg, "superAlgebra", "super_algebra")
    cong = _call(alg, "getCongruence", "get_congruence")
    super_xml = _indent_block(_basic_algebra_xml(super_alg), "      ")
    xml = (
        '<?xml version="1.0"?>\n<algebra>\n  <quotientAlgebra>\n'
        + _named_desc_card_xml(alg)
        + "    <superAlgebra>\n{}\n    </superAlgebra>\n".format(super_xml)
        + "    <congruence>\n      <partition>\n        {}\n      </partition>\n".format(
            _partition_block_string(cong)
        )
        + _write_int_array_xml(_partition_array(cong), "      ")
        + "    </congruence>\n  </quotientAlgebra>\n</algebra>\n"
    )
    with open(path, "w") as handle:
        handle.write(xml)


def _write_subalgebra(alg: Any, path: str) -> None:
    super_alg = _call(alg, "superAlgebra", "super_algebra")
    univ = list(_call(alg, "getSubuniverseArray", "get_subuniverse_array") or [])
    super_xml = _indent_block(_basic_algebra_xml(super_alg), "      ")
    xml = (
        '<?xml version="1.0"?>\n<algebra>\n  <subAlgebra>\n'
        + _named_desc_card_xml(alg)
        + "    <superAlgebra>\n{}\n    </superAlgebra>\n".format(super_xml)
        + "    <subUniverse>\n"
        + _write_int_array_xml([int(x) for x in univ], "      ")
        + "    </subUniverse>\n  </subAlgebra>\n</algebra>\n"
    )
    with open(path, "w") as handle:
        handle.write(xml)


def _write_product_elems(rows: List[List[int]], indent: str) -> str:
    parts = []
    for row in rows:
        joined = ",".join(str(int(v)) for v in row)
        parts.append("{0}<productElem>\n{0}  {1}\n{0}</productElem>\n".format(indent, joined))
    return "".join(parts)


def _write_subproduct(alg: Any, path: str) -> None:
    gens = [_int_row(g) for g in (_call(alg, "generators") or [])]
    univ = [_int_row(u) for u in (_call(alg, "getUniverseList", "get_universe_list") or [])]
    prod = _call(alg, "getProductAlgebra", "get_product_algebra", "superAlgebra", "super_algebra")
    powers = list(_call(prod, "getPowers", "get_powers") or [])
    roots = list(_call(prod, "rootFactors", "root_factors") or [])
    root_xml = "".join(
        "          <factor>\n{}\n          </factor>\n".format(
            _indent_block(_basic_algebra_xml(root), "            ")
        )
        for root in roots
    )
    powers_xml = _write_int_array_xml([int(p) for p in powers], "        ") if powers else "        <intArray>\n        </intArray>\n"
    xml = (
        '<?xml version="1.0"?>\n<algebra>\n  <subProductAlgebra>\n'
        + _named_desc_card_xml(alg)
        + "    <generators>\n"
        + _write_product_elems(gens, "      ")
        + "    </generators>\n"
    )
    if univ:
        xml += (
            "    <universe>\n"
            + _write_product_elems(univ, "      ")
            + "    </universe>\n"
        )
    xml += (
        "    <superAlgebra>\n      <bigProductAlgebra>\n        <powers>\n"
        + powers_xml
        + "        </powers>\n        <rootFactors>\n"
        + root_xml
        + "        </rootFactors>\n      </bigProductAlgebra>\n    </superAlgebra>\n"
        + "  </subProductAlgebra>\n</algebra>\n"
    )
    with open(path, "w") as handle:
        handle.write(xml)


def rebuild_typed_algebra(result: Any, xml_text: Optional[str]) -> Any:
    """Rebuild Product/Power/Quotient/Subalgebra/SubProduct from nested XML."""
    if not xml_text or result is None:
        return result
    try:
        root = ET.fromstring(xml_text.strip())
    except ET.ParseError:
        return result
    child = None
    for elem in list(root):
        if _local(elem.tag) != "algebra":
            child = elem
            break
    if child is None:
        return result
    rebuilt = _rebuild_element(child)
    return rebuilt if rebuilt is not None else result


def _rebuild_element(elem: ET.Element) -> Any:
    tag = _local(elem.tag)
    if tag == "productAlgebra":
        return _rebuild_product(elem)
    if tag == "powerAlgebra":
        return _rebuild_power(elem)
    if tag == "quotientAlgebra":
        return _rebuild_quotient(elem)
    if tag == "subAlgebra":
        return _rebuild_subalgebra(elem)
    if tag == "subProductAlgebra":
        return _rebuild_subproduct(elem)
    return None


def _alg_name(elem: ET.Element) -> str:
    return _text(_find_child(elem, "algName"))


def _rebuild_product(elem: ET.Element) -> Any:
    from org.uacalc.alg import ProductAlgebra

    factors_el = _find_child(elem, "factors")
    factors = []
    if factors_el is not None:
        for factor_el in _find_children(factors_el, "factor"):
            nested = None
            for child in list(factor_el):
                nested = child
                break
            if nested is None:
                continue
            rebuilt = _rebuild_element(nested)
            if rebuilt is None:
                rebuilt = _read_basic_document(_elem_document(nested))
            factors.append(rebuilt)
    if len(factors) < 2:
        return None
    name = _alg_name(elem)
    if name:
        return ProductAlgebra(name, factors)
    return ProductAlgebra(factors)


def _rebuild_power(elem: ET.Element) -> Any:
    from org.uacalc.alg import PowerAlgebra

    power_text = _text(_find_child(elem, "power"))
    try:
        power = int(power_text)
    except (TypeError, ValueError):
        return None
    root_el = _find_child(elem, "root")
    if root_el is None or not list(root_el):
        return None
    nested = list(root_el)[0]
    root = _rebuild_element(nested) or _read_basic_document(_elem_document(nested))
    name = _alg_name(elem)
    if name:
        return PowerAlgebra(name, root, power)
    return PowerAlgebra(root, power)


def _rebuild_quotient(elem: ET.Element) -> Any:
    from org.uacalc.alg import QuotientAlgebra
    from org.uacalc.alg.conlat import BasicPartition

    super_el = _find_child(elem, "superAlgebra")
    if super_el is None or not list(super_el):
        return None
    nested = list(super_el)[0]
    super_alg = _rebuild_element(nested) or _read_basic_document(_elem_document(nested))
    cong_el = _find_child(elem, "congruence")
    arr = []
    if cong_el is not None:
        int_el = _find_child(cong_el, "intArray")
        if int_el is not None:
            arr = _parse_int_array("".join(int_el.itertext()))
        if not arr:
            part_el = _find_child(cong_el, "partition")
            text = _text(part_el)
            if text:
                try:
                    cong = BasicPartition(text)
                    name = _alg_name(elem)
                    if name:
                        return QuotientAlgebra(name, super_alg, cong)
                    return QuotientAlgebra(super_alg, cong)
                except Exception:
                    return None
    if not arr:
        return None
    cong = BasicPartition(arr)
    name = _alg_name(elem)
    if name:
        return QuotientAlgebra(name, super_alg, cong)
    return QuotientAlgebra(super_alg, cong)


def _rebuild_subalgebra(elem: ET.Element) -> Any:
    from org.uacalc.alg import Subalgebra

    super_el = _find_child(elem, "superAlgebra")
    if super_el is None or not list(super_el):
        return None
    nested = list(super_el)[0]
    super_alg = _rebuild_element(nested) or _read_basic_document(_elem_document(nested))
    univ_el = _find_child(elem, "subUniverse")
    univ = []
    if univ_el is not None:
        int_el = _find_child(univ_el, "intArray")
        if int_el is not None:
            univ = _parse_int_array("".join(int_el.itertext()))
    name = _alg_name(elem)
    if name:
        return Subalgebra(name, super_alg, univ)
    return Subalgebra(super_alg, univ)


def _rebuild_subproduct(elem: ET.Element) -> Any:
    from org.uacalc.alg import BigProductAlgebra, SubProductAlgebra
    from org.uacalc.util import IntArray

    gens = _parse_product_elems(_find_child(elem, "generators"))
    super_el = _find_child(elem, "superAlgebra")
    if super_el is None:
        return None
    big_el = _find_child(super_el, "bigProductAlgebra")
    if big_el is None:
        return None
    powers_el = _find_child(big_el, "powers")
    powers = []
    if powers_el is not None:
        int_el = _find_child(powers_el, "intArray")
        if int_el is not None:
            powers = _parse_int_array("".join(int_el.itertext()))
    roots = []
    roots_el = _find_child(big_el, "rootFactors")
    if roots_el is not None:
        for factor_el in _find_children(roots_el, "factor"):
            if not list(factor_el):
                continue
            nested = list(factor_el)[0]
            roots.append(
                _rebuild_element(nested) or _read_basic_document(_elem_document(nested))
            )
    if not roots:
        return None
    if len(roots) == 1 and len(powers) == 1:
        prod = BigProductAlgebra(roots[0], int(powers[0]))
    elif powers:
        prod = BigProductAlgebra(roots, [int(p) for p in powers])
    else:
        prod = BigProductAlgebra(roots)
    # Java AlgebraReader does not restore <algName> on subProductAlgebra.
    gen_ias = [IntArray([int(x) for x in g]) for g in gens]
    return SubProductAlgebra("", prod, gen_ias)
