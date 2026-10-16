"""Base classes and utilities for parity testing.

This module provides infrastructure for exact behavioral parity tests between
Java/Jython and CPython implementations.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest import TestCase

# Parity test type markers
SMOKE = "smoke"
SURFACE = "surface"
BEHAVIORAL = "behavioral"

REPO_ROOT = Path(__file__).resolve().parents[2]

_JAVA_IDENTITY_TOSTRING = re.compile(r"^[\w.$]+@[0-9a-fA-F]+$")


@dataclass
class TestCaseSpec:
    """Specification for a single behavioral test case.

    ``setup`` and ``call`` are dual-runtime snippets (Jython 2.7 + CPython 3).
    If ``call`` is empty, the harness invokes ``method(*args, **kwargs)``.
    """

    id: str
    method: str
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    setup: str = ""
    call: str = ""
    description: str = ""
    expected_exception: Optional[str] = None
    skip_string_check: bool = False
    compare_exception_message: bool = False
    capture_file: bool = False
    xfail_reason: Optional[str] = None
    notes: str = ""


@dataclass
class TestResult:
    """Result from running a test case."""

    success: bool
    return_value: Any = None
    return_type: str = ""
    string_repr: str = ""
    exception_type: str = ""
    exception_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


def _call_or_get(obj: Any, *names: str) -> Any:
    for name in names:
        if not hasattr(obj, name):
            continue
        val = getattr(obj, name)
        if callable(val):
            try:
                return val()
            except TypeError:
                continue
        return val
    return None


def _op_table(op: Any) -> List[int]:
    if hasattr(op, "makeTable"):
        try:
            op.makeTable()
        except Exception:
            pass
    elif hasattr(op, "make_table"):
        try:
            op.make_table()
        except Exception:
            pass
    table = None
    if hasattr(op, "getTable"):
        table = op.getTable()
    elif hasattr(op, "get_table"):
        table = op.get_table()
    if table is None:
        return []
    return [int(x) for x in list(table)]


def _op_symbol_name(op: Any) -> str:
    if hasattr(op, "symbol"):
        try:
            sym = op.symbol() if callable(op.symbol) else op.symbol
        except Exception:
            sym = None
    else:
        sym = getattr(op, "getSymbol", lambda: None)()
    if sym is None:
        return ""
    name = _call_or_get(sym, "name", "getName")
    return str(name) if name is not None else str(sym)


def _op_arity(op: Any) -> int:
    ar = _call_or_get(op, "arity", "getArity")
    return int(ar) if ar is not None else 0


def _horner_inv_same_size(k: int, size: int, length: int) -> List[int]:
    """Match UACalc Horner.hornerInv for equal component sizes."""
    if length <= 0:
        return []
    ans = [0] * length
    remaining = int(k)
    for i in range(length - 1):
        if size:
            ans[i] = remaining % size
            remaining = (remaining - ans[i]) // size
        else:
            ans[i] = 0
    ans[length - 1] = remaining
    return ans


def _op_eval_values(op: Any, limit: int = 32) -> List[Any]:
    arity = _op_arity(op)
    size_raw = _call_or_get(op, "getSetSize", "get_set_size")
    size = int(size_raw) if size_raw is not None else 0
    total = 1 if arity == 0 else (size ** arity if size > 0 else 0)
    iva = getattr(op, "intValueAt", None) or getattr(op, "int_value_at", None)
    if not callable(iva):
        return []
    values = []
    for idx in range(min(total, limit)):
        args = _horner_inv_same_size(idx, size, arity)
        try:
            values.append(int(iva(args)))
        except Exception as exc:
            values.append({"error": type(exc).__name__, "message": str(exc)})
    return values


def _lattice_zero_ser(zero: Any) -> Any:
    if zero is None:
        return None
    text = str(zero)
    try:
        return int(text)
    except (TypeError, ValueError):
        return text


def serialize_for_golden(obj: Any) -> Any:
    """Convert an object to a JSON-serializable form for golden data."""
    if obj is None:
        return None

    if isinstance(obj, bool):
        return obj
    if isinstance(obj, (int, float, str)):
        return obj
    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, (list, tuple)):
        return [serialize_for_golden(item) for item in obj]

    try:
        import array as _arraymod

        if isinstance(obj, _arraymod.array):
            return [serialize_for_golden(item) for item in obj]
    except Exception:
        pass

    if isinstance(obj, dict):
        if obj.get("__type__") in ("file", "algebra", "lattice", "term"):
            return obj
        return {str(k): serialize_for_golden(v) for k, v in obj.items()}

    class_name = type(obj).__name__
    if class_name.startswith("Py") and len(class_name) > 2 and class_name[2].isupper():
        class_name = class_name[2:]

    # Lattice-like (before Algebra: SubalgebraLattice contains both names)
    if "Lattice" in class_name or "lattice" in class_name:
        univ = _call_or_get(obj, "universe", "getUniverseList")
        univ_ser = None
        if univ is not None:
            univ_ser = []
            for item in list(univ):
                text = str(item)
                try:
                    univ_ser.append(int(text))
                except (TypeError, ValueError):
                    univ_ser.append(text)
            try:
                univ_ser = sorted(univ_ser)
            except TypeError:
                univ_ser = sorted(univ_ser, key=str)
        return {
            "__type__": "lattice",
            "class": class_name,
            "name": str(_call_or_get(obj, "name", "getName") or ""),
            "cardinality": int(_call_or_get(obj, "cardinality") or 0),
            "universe": univ_ser,
            "zero": _lattice_zero_ser(_call_or_get(obj, "zero")),
        }

    # Algebra-like
    if any(tag in class_name for tag in ("Algebra", "algebra")):
        ops = _call_or_get(obj, "operations", "getOperations") or []
        ops = list(ops)
        symbols = []
        arities = []
        tables = []
        for op in ops:
            symbols.append(_op_symbol_name(op))
            arities.append(_op_arity(op))
            tables.append(_op_table(op))
        return {
            "__type__": "algebra",
            "class": class_name,
            "name": str(_call_or_get(obj, "name", "getName") or ""),
            "cardinality": int(_call_or_get(obj, "cardinality") or 0),
            "operation_count": len(ops),
            "symbols": symbols,
            "arities": arities,
            "tables": tables,
        }

    # BasicSet (before Lattice: SubalgebraLattice is a lattice)
    if class_name == "BasicSet":
        arr = _call_or_get(obj, "toArray", "to_array", "getArray", "get_array", "elements")
        if arr is None:
            n = int(_call_or_get(obj, "universeSize", "universe_size", "size") or 0)
            getter = getattr(obj, "get", None)
            arr = [int(getter(i)) for i in range(n)] if callable(getter) else []
        return {
            "__type__": "basic_set",
            "class": "BasicSet",
            "string": str(obj),
            "elements": [int(x) for x in list(arr)],
            "universe_size": int(
                _call_or_get(obj, "universeSize", "universe_size", "size") or 0
            ),
        }

    # Partition / BasicPartition (before Lattice: CongruenceLattice is a lattice)
    if "Partition" in class_name and "Lattice" not in class_name:
        arr = _call_or_get(obj, "toArray", "to_array", "getArray", "get_array") or []
        if class_name == "Partition":
            class_name = "BasicPartition"
        return {
            "__type__": "partition",
            "class": class_name,
            "string": str(obj),
            "array": [int(x) for x in list(arr)],
            "universe_size": int(
                _call_or_get(obj, "universeSize", "universe_size") or 0
            ),
            "number_of_blocks": int(
                _call_or_get(obj, "numberOfBlocks", "number_of_blocks") or 0
            ),
        }

    # Term-like
    if "Term" in class_name or class_name in ("VariableImp", "NonVariableTerm"):
        isa = _call_or_get(obj, "isaVariable", "isa_variable")
        return {
            "__type__": "term",
            "class": class_name,
            "string": str(obj),
            "isa_variable": bool(isa) if isa is not None else None,
        }

    # OperationSymbol
    if "OperationSymbol" in class_name:
        return {
            "__type__": "operation_symbol",
            "name": str(_call_or_get(obj, "name", "getName") or obj),
            "arity": int(_call_or_get(obj, "arity", "getArity") or 0),
        }

    # SimilarityType
    if "SimilarityType" in class_name:
        symbols = _call_or_get(obj, "getOperationSymbols", "get_operation_symbols") or []
        return {
            "__type__": "similarity_type",
            "class": class_name,
            "string": str(obj),
            "symbols": [serialize_for_golden(s) for s in list(symbols)],
            "max_arity": int(
                _call_or_get(obj, "getMaxArity", "get_max_arity")
                if _call_or_get(obj, "getMaxArity", "get_max_arity") is not None
                else -1
            ),
        }

    # Operation-like (IntOperation, AbstractOperation, …)
    if (
        any(tag in class_name for tag in ("Operation", "IntOperation", "BasicOperation"))
        and class_name not in ("Operations", "ParameterizedOperation")
    ):
        set_size = _call_or_get(obj, "getSetSize", "get_set_size")
        arity = _op_arity(obj)
        size_i = int(set_size) if set_size is not None else 0
        total = 1 if arity == 0 else (size_i ** arity if size_i > 0 else 0)
        return {
            "__type__": "operation",
            "symbol": _op_symbol_name(obj),
            "arity": arity,
            "set_size": size_i if set_size is not None else None,
            "value_count": total,
            "values": _op_eval_values(obj),
        }

    # POElem / lattice elements: prefer integer labels
    text = str(obj)
    try:
        if re.fullmatch(r"-?\d+", text or ""):
            return int(text)
    except Exception:
        pass

    return {"__repr__": repr(obj), "__type__": class_name, "string": text}


def _maybe_elem(obj: Any) -> Any:
    if obj is None:
        return None
    text = str(obj)
    try:
        return int(text)
    except (TypeError, ValueError):
        return obj


def exception_simple_name(exc: BaseException) -> str:
    name = type(exc).__name__
    if "." in name:
        name = name.rsplit(".", 1)[-1]
    return name


def load_golden_data(package: str, filename: str) -> Dict[str, Any]:
    """Load golden data JSON file for a package."""
    golden_dir = REPO_ROOT / "tests" / "parity" / package / "golden_data"
    filepath = golden_dir / filename

    if not filepath.exists():
        raise FileNotFoundError(
            "Golden data file not found: {0}\n"
            "Generate it with: python3 tools/generate_golden_data.py --package {1}".format(
                filepath, package
            )
        )

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_golden_data(package: str, filename: str, data: Dict[str, Any]) -> None:
    """Save golden data to JSON file."""
    golden_dir = REPO_ROOT / "tests" / "parity" / package / "golden_data"
    golden_dir.mkdir(parents=True, exist_ok=True)

    filepath = golden_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def spec_to_dict(spec: TestCaseSpec) -> Dict[str, Any]:
    return {
        "id": spec.id,
        "method": spec.method,
        "args": spec.args,
        "kwargs": spec.kwargs,
        "setup": spec.setup,
        "call": spec.call,
        "description": spec.description,
        "expected_exception": spec.expected_exception,
        "skip_string_check": spec.skip_string_check,
        "compare_exception_message": spec.compare_exception_message,
        "capture_file": spec.capture_file,
        "xfail_reason": spec.xfail_reason,
        "notes": spec.notes,
    }


class BehavioralParityTest(TestCase):
    """Base class for behavioral parity tests.

    Subclasses should set:
        package: str
        golden_file: str
    """

    package: str = ""
    golden_file: str = ""

    @classmethod
    def setUpClass(cls):
        if not cls.package or not cls.golden_file:
            raise ValueError(
                "{0} must set 'package' and 'golden_file' class attributes".format(
                    cls.__name__
                )
            )
        python_dir = str(REPO_ROOT / "python")
        if python_dir not in sys.path:
            sys.path.insert(0, python_dir)
        os.chdir(str(REPO_ROOT))
        cls.golden_data = load_golden_data(cls.package, cls.golden_file)
        cls.test_cases_by_id = {
            tc["id"]: tc for tc in cls.golden_data.get("test_cases", [])
        }

    def run_golden_test_case(self, test_id: str) -> None:
        if test_id not in self.test_cases_by_id:
            self.fail("Test case '{0}' not found in golden data".format(test_id))

        expected = self.test_cases_by_id[test_id]
        expected_result = expected["result"]
        actual_result = self._execute_case(expected)

        if expected_result.get("success"):
            self.assertTrue(
                actual_result.success,
                "{0}: Expected success but got exception: {1}: {2}".format(
                    test_id,
                    actual_result.exception_type,
                    actual_result.exception_message,
                ),
            )
            self._compare_values(
                test_id,
                serialize_for_golden(actual_result.return_value),
                expected_result.get("return_value"),
                "return value",
            )
            if not expected.get("skip_string_check", False):
                self.assertEqual(
                    actual_result.string_repr,
                    expected_result.get("string_repr", ""),
                    "{0}: String representation mismatch".format(test_id),
                )
        else:
            self.assertFalse(
                actual_result.success,
                "{0}: Expected exception but method succeeded with {1!r}".format(
                    test_id, actual_result.return_value
                ),
            )
            expected_exc_type = expected_result["exception"]["type"]
            self.assertEqual(
                actual_result.exception_type,
                expected_exc_type,
                "{0}: Exception type mismatch".format(test_id),
            )
            if expected.get("compare_exception_message", False):
                expected_msg = expected_result["exception"].get("message", "")
                if expected_msg and not self._messages_match(
                    actual_result.exception_message, expected_msg
                ):
                    self.fail(
                        "{0}: Exception message mismatch\n  Expected: {1}\n  Actual:   {2}".format(
                            test_id, expected_msg, actual_result.exception_message
                        )
                    )

    def _execute_case(self, expected: Dict[str, Any]) -> TestResult:
        setup = expected.get("setup") or ""
        call = expected.get("call") or ""
        method_name = expected["method"]
        args = expected.get("args") or []
        kwargs = expected.get("kwargs") or {}
        capture_file = expected.get("capture_file", False)

        python_dir = str(REPO_ROOT / "python")
        if python_dir not in sys.path:
            sys.path.insert(0, python_dir)

        ns: Dict[str, Any] = {
            "__name__": "parity_case",
            "REPO_ROOT": str(REPO_ROOT),
        }
        try:
            if setup:
                exec(setup, ns)  # noqa: S102 — dual-runtime case setup
            if call:
                result = eval(call, ns)  # noqa: S307 — dual-runtime case call
            else:
                result = self._invoke_method(method_name, args, kwargs)
            if capture_file:
                path = ns.get("CAPTURE_PATH") or ns.get("OUT_PATH")
                if not path:
                    raise RuntimeError("capture_file set but CAPTURE_PATH/OUT_PATH missing")
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    content = fh.read()
                result = self._file_payload(path, content)
            return TestResult(
                success=True,
                return_value=result,
                return_type=type(result).__name__ if result is not None else "NoneType",
                string_repr="" if result is None else str(result),
            )
        except Exception as exc:
            return TestResult(
                success=False,
                exception_type=exception_simple_name(exc),
                exception_message=str(exc),
            )

    def _file_payload(self, path: Any, content: str) -> Dict[str, Any]:
        return {
            "__type__": "file",
            "suffix": os.path.splitext(str(path))[1],
            "normalized": re.sub(r"\s+", " ", content).strip(),
        }

    def _invoke_method(
        self, method_name: str, args: List[Any], kwargs: Dict[str, Any]
    ) -> Any:
        package_name = "org.uacalc.{0}".format(self.package)
        pkg = __import__(package_name, fromlist=[""])
        obj = pkg
        parts = method_name.split(".")
        for part in parts[:-1]:
            obj = getattr(obj, part)
        method = getattr(obj, parts[-1])
        return method(*args, **kwargs)

    def _compare_values(
        self, test_id: str, actual: Any, expected: Any, context: str
    ) -> None:
        if actual == expected:
            return
        # Java Object.toString() is Class@identityHashCode. Golden files freeze
        # one JVM run's hex; compare the class prefix only.
        if _normalize_java_identity(actual) == _normalize_java_identity(expected):
            return
        self.fail(
            "{0}: {1} mismatch\n  Expected: {2}\n  Actual:   {3}".format(
                test_id,
                context,
                json.dumps(expected, indent=2, sort_keys=True),
                json.dumps(actual, indent=2, sort_keys=True),
            )
        )

    def _messages_match(self, actual: str, expected: str) -> bool:
        if actual == expected:
            return True
        actual_norm = actual.replace("\\", "/").strip()
        expected_norm = expected.replace("\\", "/").strip()
        if actual_norm == expected_norm:
            return True
        # Java often prefixes "java.lang.Foo: "
        if ": " in expected_norm:
            expected_tail = expected_norm.split(": ", 1)[-1]
            if actual_norm == expected_tail or actual_norm.endswith(expected_tail):
                return True
        return False


def looks_like_java_identity(text: str) -> bool:
    return bool(_JAVA_IDENTITY_TOSTRING.match(text or ""))


_JAVA_IDENTITY_IN_STRING = re.compile(r"[\w.$]+@[0-9a-fA-F]+")


def _normalize_java_identity(obj: Any) -> Any:
    """Replace Java identity-hash suffixes so Class@hex compares equal across runs."""
    if isinstance(obj, str):
        return _JAVA_IDENTITY_IN_STRING.sub(
            lambda m: m.group(0).rsplit("@", 1)[0] + "@<id>", obj
        )
    if isinstance(obj, list):
        return [_normalize_java_identity(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _normalize_java_identity(v) for k, v in obj.items()}
    return obj
