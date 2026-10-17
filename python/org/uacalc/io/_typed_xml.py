"""Typed XML write/read for Product/Power/Quotient/Subalgebra/SubProduct.

Java AlgebraWriter emits nested ``<productAlgebra>`` / ``<powerAlgebra>`` /
``<quotientAlgebra>`` / ``<subAlgebra>`` / ``<subProductAlgebra>`` instead of
flattening to ``<basicAlgebra>`` tables. Dedicated Rust writers on the
concrete types emit that XML; the org shim dispatches to them and rebuilds
the typed algebra when those tags are present on read.

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


def write_typed_algebra_xml(algebra: Any, path: str) -> bool:
    """Write Java-shaped typed XML when ``algebra`` is a known derived kind.

    Returns True if a typed document was written, False to fall through to the
    basic-algebra writer.
    """
    alg = getattr(algebra, "_inner", algebra)
    name = _tname(alg)
    writers = (
        (_FREE_TYPE_NAMES, "write_free_algebra_xml_to_file"),
        (_PRODUCT_TYPE_NAMES, "write_product_algebra_xml_to_file"),
        (_POWER_TYPE_NAMES, "write_power_algebra_xml_to_file"),
        (_QUOTIENT_TYPE_NAMES, "write_quotient_algebra_xml_to_file"),
        (_SUB_TYPE_NAMES, "write_subalgebra_xml_to_file"),
        (_SUBPROD_TYPE_NAMES, "write_sub_product_algebra_xml_to_file"),
    )
    for type_names, method in writers:
        if name in type_names:
            getattr(_LibAlgebraWriter, method)(alg, path)
            return True
    return False


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
