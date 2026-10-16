#!/usr/bin/env python3
"""Generate golden behavioral parity data from Java/Jython.

Usage:
    python3 tools/generate_golden_data.py --package io
    python3 tools/generate_golden_data.py --package lat --type Lattices
    python3 tools/generate_golden_data.py --all
    python3 tools/generate_golden_data.py --package io --diff
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import TestCaseSpec, save_golden_data, spec_to_dict  # noqa: E402


JYTHON_RUNNER = r'''
# -*- coding: utf-8 -*-
from __future__ import print_function
import json
import os
import sys
import re

from java.io import ByteArrayOutputStream, PrintStream
from java.lang import System

MARKER_BEGIN = "---GOLDEN_JSON_BEGIN---"
MARKER_END = "---GOLDEN_JSON_END---"

def call_or_get(obj, *names):
    for name in names:
        if hasattr(obj, name):
            val = getattr(obj, name)
            if callable(val):
                try:
                    return val()
                except TypeError:
                    pass
            else:
                return val
    return None

def op_table(op):
    if hasattr(op, "makeTable"):
        try:
            op.makeTable()
        except Exception:
            pass
    table = None
    if hasattr(op, "getTable"):
        table = op.getTable()
    if table is None:
        return []
    return [int(x) for x in list(table)]

def op_symbol_name(op):
    try:
        sym = op.symbol() if callable(getattr(op, "symbol", None)) else getattr(op, "symbol", None)
    except Exception:
        sym = None
    if sym is None:
        return ""
    name = call_or_get(sym, "name", "getName")
    return str(name) if name is not None else str(sym)

def op_arity(op):
    ar = call_or_get(op, "arity", "getArity")
    try:
        return int(ar)
    except Exception:
        return 0

def horner_inv_same_size(k, size, length):
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

def op_eval_values(op, limit=32):
    arity = op_arity(op)
    size_raw = call_or_get(op, "getSetSize", "get_set_size")
    try:
        size = int(size_raw)
    except Exception:
        size = 0
    total = 1 if arity == 0 else (size ** arity if size > 0 else 0)
    iva = getattr(op, "intValueAt", None)
    if iva is None or not callable(iva):
        return []
    values = []
    for idx in range(min(total, limit)):
        args = horner_inv_same_size(idx, size, arity)
        try:
            values.append(int(iva(args)))
        except Exception:
            e = sys.exc_info()[1]
            values.append({"error": type(e).__name__, "message": str(e)})
    return values

def serialize(obj):
    if obj is None:
        return None
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, (int, float)):
        return obj
    if isinstance(obj, (str, unicode)):
        return str(obj)
    if isinstance(obj, dict):
        if obj.get("__type__") in ("file", "algebra", "lattice", "term"):
            return obj
        out = {}
        for k in obj:
            out[str(k)] = serialize(obj[k])
        return out
    if isinstance(obj, (list, tuple)):
        return [serialize(item) for item in obj]
    try:
        import array as _arraymod
        if isinstance(obj, _arraymod.array):
            return [serialize(item) for item in obj]
    except Exception:
        pass
    try:
        from java.util import Collection
        if isinstance(obj, Collection):
            return [serialize(item) for item in obj]
    except Exception:
        pass
    try:
        # Java primitive arrays (int[], etc.)
        if hasattr(obj, "__getitem__") and hasattr(obj, "__len__") and not isinstance(obj, (str, dict)):
            tname = type(obj).__name__
            if tname.startswith("[") or tname.endswith("[]"):
                return [serialize(obj[i]) for i in range(len(obj))]
    except Exception:
        pass
    class_name = obj.__class__.__name__
    if class_name.startswith("Py") and len(class_name) > 2:
        class_name = class_name[2:]
    if "Lattice" in class_name:
        univ = call_or_get(obj, "universe", "getUniverseList")
        univ_ser = None
        if univ is not None:
            univ_ser = []
            for item in list(univ):
                text = str(item)
                try:
                    univ_ser.append(int(text))
                except Exception:
                    univ_ser.append(text)
            try:
                univ_ser = sorted(univ_ser)
            except Exception:
                univ_ser = sorted(univ_ser, key=str)
        zero = call_or_get(obj, "zero")
        zero_ser = None
        if zero is not None:
            zt = str(zero)
            try:
                zero_ser = int(zt)
            except Exception:
                zero_ser = zt
        return {
            "__type__": "lattice",
            "class": class_name,
            "name": str(call_or_get(obj, "name", "getName") or ""),
            "cardinality": int(call_or_get(obj, "cardinality") or 0),
            "universe": univ_ser,
            "zero": zero_ser,
        }
    if "Algebra" in class_name:
        ops = call_or_get(obj, "operations", "getOperations") or []
        ops = list(ops)
        symbols = []
        arities = []
        tables = []
        for op in ops:
            symbols.append(op_symbol_name(op))
            arities.append(op_arity(op))
            tables.append(op_table(op))
        return {
            "__type__": "algebra",
            "class": class_name,
            "name": str(call_or_get(obj, "name", "getName") or ""),
            "cardinality": int(call_or_get(obj, "cardinality") or 0),
            "operation_count": len(ops),
            "symbols": symbols,
            "arities": arities,
            "tables": tables,
        }
    if class_name == "BasicSet":
        arr = call_or_get(obj, "toArray", "to_array", "getArray", "get_array", "elements")
        if arr is None:
            n_raw = call_or_get(obj, "universeSize", "universe_size", "size")
            try:
                n = int(n_raw)
            except Exception:
                n = 0
            getter = getattr(obj, "get", None)
            arr = [int(getter(i)) for i in range(n)] if getter is not None and callable(getter) else []
        us = call_or_get(obj, "universeSize", "universe_size", "size")
        return {
            "__type__": "basic_set",
            "class": "BasicSet",
            "string": str(obj),
            "elements": [int(x) for x in list(arr)],
            "universe_size": int(us) if us is not None else 0,
        }
    if "Partition" in class_name and "Lattice" not in class_name:
        arr = call_or_get(obj, "toArray", "to_array", "getArray", "get_array") or []
        us = call_or_get(obj, "universeSize", "universe_size")
        nb = call_or_get(obj, "numberOfBlocks", "number_of_blocks")
        if class_name == "Partition":
            class_name = "BasicPartition"
        return {
            "__type__": "partition",
            "class": class_name,
            "string": str(obj),
            "array": [int(x) for x in list(arr)],
            "universe_size": int(us) if us is not None else 0,
            "number_of_blocks": int(nb) if nb is not None else 0,
        }
    if "Term" in class_name or class_name in ("VariableImp", "NonVariableTerm"):
        isa = call_or_get(obj, "isaVariable", "isa_variable")
        return {
            "__type__": "term",
            "class": class_name,
            "string": str(obj),
            "isa_variable": bool(isa) if isa is not None else None,
        }
    if "OperationSymbol" in class_name:
        return {
            "__type__": "operation_symbol",
            "name": str(call_or_get(obj, "name", "getName") or obj),
            "arity": int(call_or_get(obj, "arity", "getArity") or 0),
        }
    if "SimilarityType" in class_name:
        symbols = call_or_get(obj, "getOperationSymbols", "get_operation_symbols") or []
        max_ar = call_or_get(obj, "getMaxArity", "get_max_arity")
        return {
            "__type__": "similarity_type",
            "class": class_name,
            "string": str(obj),
            "symbols": [serialize(s) for s in list(symbols)],
            "max_arity": int(max_ar) if max_ar is not None else -1,
        }
    if (
        ("Operation" in class_name or "IntOperation" in class_name or "BasicOperation" in class_name)
        and class_name not in ("Operations", "ParameterizedOperation")
    ):
        set_size = call_or_get(obj, "getSetSize", "get_set_size")
        arity = op_arity(obj)
        try:
            size_i = int(set_size)
        except Exception:
            size_i = 0
        total = 1 if arity == 0 else (size_i ** arity if size_i > 0 else 0)
        return {
            "__type__": "operation",
            "symbol": op_symbol_name(obj),
            "arity": arity,
            "set_size": size_i if set_size is not None else None,
            "value_count": total,
            "values": op_eval_values(obj),
        }
    try:
        from java.util import Map
        if isinstance(obj, Map):
            out = {}
            for entry in obj.entrySet():
                out[str(serialize(entry.getKey()) if not isinstance(entry.getKey(), (str, int)) else entry.getKey())] = serialize(entry.getValue())
            return out
    except Exception:
        pass
    text = str(obj)
    try:
        if re.match(r"^-?\d+$", text or ""):
            return int(text)
    except Exception:
        pass
    return {"__repr__": repr(obj), "__type__": class_name, "string": text}

def exception_simple_name(exc):
    name = type(exc).__name__
    if "." in name:
        name = name.split(".")[-1]
    return name

def file_payload(path, content):
    return {
        "__type__": "file",
        "suffix": os.path.splitext(str(path))[1],
        "normalized": re.sub(r"\s+", " ", content).strip(),
    }

def run_case(case):
    ns = {"__name__": "parity_case", "REPO_ROOT": os.getcwd()}
    setup = case.get("setup") or ""
    call = case.get("call") or ""
    method_name = case.get("method") or ""
    args = case.get("args") or []
    kwargs = case.get("kwargs") or {}
    capture_file = case.get("capture_file") or False

    old_out = System.out
    baos = ByteArrayOutputStream()
    System.setOut(PrintStream(baos))
    try:
        if setup:
            exec setup in ns
        if call:
            result = eval(call, ns)
        else:
            parts = method_name.split(".")
            obj = __import__("org.uacalc." + CASES_PACKAGE, fromlist=[""])
            for part in parts[:-1]:
                obj = getattr(obj, part)
            method = getattr(obj, parts[-1])
            result = method(*args, **kwargs)
        if capture_file:
            path = ns.get("CAPTURE_PATH") or ns.get("OUT_PATH")
            if not path:
                raise RuntimeError("capture_file set but CAPTURE_PATH/OUT_PATH missing")
            fh = open(path, "r")
            try:
                content = fh.read()
            finally:
                fh.close()
            result = file_payload(path, content)
        return {
            "success": True,
            "return_value": serialize(result),
            "return_type": result.__class__.__name__ if result is not None else "NoneType",
            "string_repr": "" if result is None else str(result),
        }
    except:
        e = sys.exc_info()[1]
        return {
            "success": False,
            "exception": {
                "type": exception_simple_name(e),
                "message": str(e),
            },
        }
    finally:
        System.setOut(old_out)

CASES_PACKAGE = %PACKAGE_REPR%
cases = json.loads(%CASES_JSON%)
results = []
for case in cases:
    results.append({"id": case.get("id"), "result": run_case(case)})

print(MARKER_BEGIN)
print(json.dumps(results))
print(MARKER_END)
'''


def find_jython() -> Optional[str]:
    jython = shutil.which("jython")
    if jython:
        return jython
    env = os.environ.get("JYTHON")
    if env and Path(env).exists():
        return env
    common_paths = [
        "/tmp/jython/bin/jython",
        "/usr/local/bin/jython",
        "/usr/bin/jython",
        str(Path.home() / "jython" / "bin" / "jython"),
        str(Path.home() / "jython2.7.4" / "bin" / "jython"),
        str(Path.home() / "jython2.7.3" / "bin" / "jython"),
    ]
    for path in common_paths:
        if Path(path).exists():
            return path
    return None


def build_classpath() -> str:
    jars = REPO_ROOT / "jars"
    parts = [
        str(REPO_ROOT / "build" / "classes"),
        str(jars / "uacalc.jar"),
        str(jars / "LatDraw.jar"),
        str(jars / "miglayout-3.7-swing.jar"),
    ]
    existing = [p for p in parts if Path(p).exists()]
    if not existing:
        print("ERROR: no Java classes or jars found. Run 'ant dist'.", file=sys.stderr)
        sys.exit(1)
    if not (jars / "LatDraw.jar").exists():
        print("WARNING: jars/LatDraw.jar missing; lat cases may fail.", file=sys.stderr)
    return os.pathsep.join(existing)


def load_test_cases(package: str, type_name: Optional[str]) -> List[TestCaseSpec]:
    test_cases_dir = REPO_ROOT / "tests" / "parity" / package / "test_cases"
    cases: List[TestCaseSpec] = []
    if type_name:
        files = [test_cases_dir / "{0}_cases.py".format(type_name.lower())]
    else:
        files = sorted(test_cases_dir.glob("*_cases.py")) if test_cases_dir.exists() else []
        if not files:
            files = [REPO_ROOT / "tests" / "parity" / package / "test_cases.py"]

    parity_tests_path = str(REPO_ROOT / "tests" / "parity")
    if parity_tests_path not in sys.path:
        sys.path.insert(0, parity_tests_path)

    import importlib.util

    for cases_file in files:
        if not cases_file.exists():
            continue
        spec = importlib.util.spec_from_file_location(
            "test_cases_{0}_{1}".format(package, cases_file.stem), cases_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if type_name and hasattr(module, "{0}_TEST_CASES".format(type_name.upper())):
            cases.extend(getattr(module, "{0}_TEST_CASES".format(type_name.upper())))
        elif hasattr(module, "TEST_CASES"):
            cases.extend(module.TEST_CASES)
    return cases


def extract_json(stdout: str) -> Any:
    begin = "---GOLDEN_JSON_BEGIN---"
    end = "---GOLDEN_JSON_END---"
    if begin in stdout and end in stdout:
        payload = stdout.split(begin, 1)[1].split(end, 1)[0].strip()
        return json.loads(payload)
    # Fallback: last JSON array/object in stdout
    text = stdout.strip()
    for opener, closer in (("[", "]"), ("{", "}")):
        start = text.rfind(opener)
        if start == -1:
            continue
        try:
            return json.loads(text[start:])
        except json.JSONDecodeError:
            continue
    raise json.JSONDecodeError("no JSON found", stdout, 0)


def run_cases_jython(package: str, test_cases: List[TestCaseSpec], classpath: str) -> Dict[str, Any]:
    jython = find_jython()
    if not jython:
        print("ERROR: Jython not found. Install Jython 2.7.x or set JYTHON.", file=sys.stderr)
        sys.exit(1)

    cases_json = json.dumps([spec_to_dict(tc) for tc in test_cases])
    script = JYTHON_RUNNER.replace("%PACKAGE_REPR%", repr(package)).replace(
        "%CASES_JSON%", repr(cases_json)
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as handle:
        handle.write(script)
        script_path = handle.name

    env = os.environ.copy()
    env["CLASSPATH"] = classpath
    env["PYTHONPATH"] = ""

    try:
        proc = subprocess.run(
            [jython, script_path],
            capture_output=True,
            text=True,
            timeout=max(60, 15 * len(test_cases)),
            env=env,
            cwd=str(REPO_ROOT),
        )
    finally:
        Path(script_path).unlink(missing_ok=True)

    if proc.stderr:
        # LatDraw prints NonOrderedSetException stack traces to stderr on purpose.
        sys.stderr.write(proc.stderr)
        if not proc.stderr.endswith("\n"):
            sys.stderr.write("\n")

    try:
        results = extract_json(proc.stdout)
    except (json.JSONDecodeError, ValueError) as exc:
        print("ERROR: failed to parse Jython output: {0}".format(exc), file=sys.stderr)
        print("stdout:\n{0}".format(proc.stdout), file=sys.stderr)
        sys.exit(1)

    by_id = {item["id"]: item["result"] for item in results}
    return by_id


def generate_golden_for_package(package: str, type_name: Optional[str] = None) -> None:
    print(
        "Generating golden data for org.uacalc.{0}{1}".format(
            package, ".{0}".format(type_name) if type_name else ""
        )
    )
    classpath = build_classpath()
    jython = find_jython()
    if not jython:
        print("ERROR: Jython not found.", file=sys.stderr)
        sys.exit(1)
    print("Using Jython: {0}".format(jython))
    print("Using classpath: {0}".format(classpath))

    test_cases = load_test_cases(package, type_name)
    if not test_cases:
        print(
            "No test cases found for {0}. Create tests/parity/{0}/test_cases/".format(
                package
            )
        )
        return

    print("Found {0} test case(s)".format(len(test_cases)))
    results_by_id = run_cases_jython(package, test_cases, classpath)

    golden_test_cases = []
    for spec in test_cases:
        result = results_by_id.get(spec.id)
        if result is None:
            print("  {0}... missing from Jython output".format(spec.id))
            result = {
                "success": False,
                "exception": {
                    "type": "MissingJythonResult",
                    "message": "case was not returned by the Jython runner",
                },
            }
        elif result.get("success"):
            print("  {0}... ok".format(spec.id))
        else:
            exc = result.get("exception") or {}
            print("  {0}... {1}".format(spec.id, exc.get("type", "error")))

        entry = spec_to_dict(spec)
        entry["result"] = result
        golden_test_cases.append(entry)

    golden_data = {
        "metadata": {
            "package": "org.uacalc.{0}".format(package),
            "type": type_name or "package",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "runtime": "jython",
            "jar": "uacalc.jar",
            "test_cases": len(golden_test_cases),
        },
        "test_cases": golden_test_cases,
    }

    filename = "{0}_jython.json".format(type_name if type_name else package)
    save_golden_data(package, filename, golden_data)
    golden_path = REPO_ROOT / "tests" / "parity" / package / "golden_data" / filename
    print("\nGolden data saved to {0}".format(golden_path.relative_to(REPO_ROOT)))


def show_diff(package: str, type_name: Optional[str] = None) -> None:
    filename = "{0}_jython.json".format(type_name if type_name else package)
    golden_path = REPO_ROOT / "tests" / "parity" / package / "golden_data" / filename
    if not golden_path.exists():
        print("No existing golden data at {0}".format(golden_path))
        return
    subprocess.run(["git", "diff", "--color", str(golden_path)], cwd=REPO_ROOT)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate golden parity test data")
    parser.add_argument("--package", "-p", help="Package name (e.g., io, lat, terms)")
    parser.add_argument("--type", "-t", help="Specific type name within package")
    parser.add_argument("--all", "-a", action="store_true", help="Generate for all packages with test cases")
    parser.add_argument("--diff", "-d", action="store_true", help="Show diff after generating")
    args = parser.parse_args()

    if args.all:
        parity_dir = REPO_ROOT / "tests" / "parity"
        packages = [
            pkg_dir.name
            for pkg_dir in sorted(parity_dir.iterdir())
            if pkg_dir.is_dir() and (pkg_dir / "test_cases").exists()
        ]
        if not packages:
            print("No packages with test_cases found", file=sys.stderr)
            sys.exit(1)
        for package in packages:
            generate_golden_for_package(package)
            if args.diff:
                show_diff(package)
    elif args.package:
        generate_golden_for_package(args.package, args.type)
        if args.diff:
            show_diff(args.package, args.type)
    else:
        parser.error("Specify --package or --all")


if __name__ == "__main__":
    main()
