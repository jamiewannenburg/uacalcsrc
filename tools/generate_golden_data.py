#!/usr/bin/env python3
"""Generate golden behavioral parity data from Java/Jython.

This script runs test cases against the real Java UACalc (via Jython) and
stores the expected outputs in JSON format for parity testing.

Usage:
    python3 tools/generate_golden_data.py --package io
    python3 tools/generate_golden_data.py --package lat --type Lattices
    python3 tools/generate_golden_data.py --all
    python3 tools/generate_golden_data.py --package io --diff
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))

from parity_test_base import (
    TestCaseSpec, TestResult, serialize_for_golden, save_golden_data
)


def find_jython() -> Optional[str]:
    """Find jython executable."""
    jython = shutil.which("jython")
    if jython:
        return jython
    
    # Check common locations
    common_paths = [
        "/usr/local/bin/jython",
        "/usr/bin/jython",
        str(Path.home() / "jython" / "bin" / "jython"),
    ]
    for path in common_paths:
        if Path(path).exists():
            return path
    
    return None


def run_test_case_jython(
    package: str, test_case: TestCaseSpec, jar_path: Path
) -> TestResult:
    """Run a single test case using Jython/Java and return the result."""
    # Create a temporary script to run the test case
    script = f"""#!/usr/bin/env jython
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import json

# Import the Java package
import org.uacalc.{package} as pkg

def serialize_result(obj):
    \"\"\"Convert result to JSON-serializable form.\"\"\"
    if obj is None:
        return None
    if isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [serialize_result(item) for item in obj]
    if isinstance(obj, dict):
        return {{k: serialize_result(v) for k, v in obj.items()}}
    
    # Handle Java objects
    class_name = obj.__class__.__name__
    result = {{'__type__': class_name}}
    
    # Try common attribute patterns
    for attr_name in ['name', 'cardinality']:
        if hasattr(obj, attr_name):
            val = getattr(obj, attr_name)
            if callable(val):
                result[attr_name] = val()
            else:
                result[attr_name] = val
        # Try Java getter pattern
        getter = 'get' + attr_name.capitalize()
        if hasattr(obj, getter):
            val = getattr(obj, getter)
            if callable(val):
                result[attr_name] = val()
    
    # Operations count
    for ops_attr in ['operations', 'getOperations']:
        if hasattr(obj, ops_attr):
            ops = getattr(obj, ops_attr)
            if callable(ops):
                ops = ops()
            if ops:
                try:
                    result['operation_count'] = len(list(ops))
                except:
                    pass
            break
    
    return result

# Parse method name and call it
method_parts = {json.dumps(test_case.method.split('.'))}
obj = pkg
for part in method_parts[:-1]:
    obj = getattr(obj, part)
method = getattr(obj, method_parts[-1])

try:
    args = {json.dumps(test_case.args)}
    kwargs = {json.dumps(test_case.kwargs)}
    result = method(*args, **kwargs)
    
    output = {{
        'success': True,
        'return_value': serialize_result(result),
        'return_type': result.__class__.__name__ if result else 'NoneType',
        'string_repr': str(result) if result is not None else ''
    }}
    print(json.dumps(output))
except Exception as e:
    output = {{
        'success': False,
        'exception': {{
            'type': e.__class__.__name__,
            'message': str(e)
        }}
    }}
    print(json.dumps(output))
"""
    
    # Write script to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script)
        script_path = f.name
    
    try:
        jython = find_jython()
        if not jython:
            return TestResult(
                success=False,
                exception_type="JythonNotFound",
                exception_message="Jython not found. Install it or set JYTHON env var."
            )
        
        env = os.environ.copy()
        env['CLASSPATH'] = str(jar_path)
        env['PYTHONPATH'] = ''
        
        proc = subprocess.run(
            [jython, script_path],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
            cwd=str(REPO_ROOT)
        )
        
        if proc.returncode != 0:
            return TestResult(
                success=False,
                exception_type="JythonError",
                exception_message=f"Jython failed: {proc.stderr}"
            )
        
        # Parse JSON output
        result_data = json.loads(proc.stdout.strip())
        
        if result_data['success']:
            return TestResult(
                success=True,
                return_value=result_data['return_value'],
                return_type=result_data['return_type'],
                string_repr=result_data['string_repr']
            )
        else:
            return TestResult(
                success=False,
                exception_type=result_data['exception']['type'],
                exception_message=result_data['exception']['message']
            )
    finally:
        Path(script_path).unlink(missing_ok=True)


def generate_golden_for_package(package: str, type_name: Optional[str] = None) -> None:
    """Generate golden data for a package.
    
    Args:
        package: Package name (e.g., "io", "lat", "terms")
        type_name: Optional specific type name (e.g., "Lattices")
    """
    print(f"Generating golden data for org.uacalc.{package}" +
          (f".{type_name}" if type_name else ""))
    
    # Find JAR
    jar_path = REPO_ROOT / "jars" / "uacalc.jar"
    if not jar_path.exists():
        print(f"ERROR: {jar_path} not found", file=sys.stderr)
        sys.exit(1)
    
    # Check Jython
    jython = find_jython()
    if not jython:
        print("ERROR: Jython not found. Install it to generate golden data.",
              file=sys.stderr)
        print("  Try: pip install jython-installer; jython-installer",
              file=sys.stderr)
        sys.exit(1)
    
    print(f"Using Jython: {jython}")
    print(f"Using JAR: {jar_path}")
    
    # Load test case specifications
    test_cases = load_test_cases(package, type_name)
    if not test_cases:
        print(f"No test cases found for {package}" +
              (f".{type_name}" if type_name else ""))
        print(f"Create test cases in tests/parity/{package}/test_cases/")
        return
    
    print(f"Found {len(test_cases)} test case(s)")
    
    # Run test cases
    golden_test_cases = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"  [{i}/{len(test_cases)}] {test_case.id}...", end=" ")
        result = run_test_case_jython(package, test_case, jar_path)
        
        if result.success:
            print("✓")
            result_data = {
                'success': True,
                'return_value': result.return_value,
                'return_type': result.return_type,
                'string_repr': result.string_repr
            }
        else:
            print(f"✗ ({result.exception_type})")
            result_data = {
                'success': False,
                'exception': {
                    'type': result.exception_type,
                    'message': result.exception_message
                }
            }
        
        golden_test_cases.append({
            'id': test_case.id,
            'method': test_case.method,
            'args': test_case.args,
            'kwargs': test_case.kwargs,
            'description': test_case.description,
            'result': result_data,
            'skip_string_check': test_case.skip_string_check,
            'notes': test_case.notes
        })
    
    # Save golden data
    golden_data = {
        'metadata': {
            'package': f'org.uacalc.{package}',
            'type': type_name or 'package',
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'runtime': 'jython',
            'jar': 'uacalc.jar',
            'test_cases': len(golden_test_cases)
        },
        'test_cases': golden_test_cases
    }
    
    filename = f"{type_name}_jython.json" if type_name else f"{package}_jython.json"
    save_golden_data(package, filename, golden_data)
    
    golden_path = REPO_ROOT / "tests" / "parity" / package / "golden_data" / filename
    print(f"\n✓ Golden data saved to {golden_path.relative_to(REPO_ROOT)}")


def load_test_cases(package: str, type_name: Optional[str]) -> List[TestCaseSpec]:
    """Load test case specifications for a package/type.
    
    Looks for tests/parity/{package}/test_cases/{type}_cases.py or
    tests/parity/{package}/test_cases.py with TEST_CASES list.
    """
    test_cases_dir = REPO_ROOT / "tests" / "parity" / package / "test_cases"
    
    # Try type-specific file first
    if type_name:
        cases_file = test_cases_dir / f"{type_name.lower()}_cases.py"
    else:
        cases_file = test_cases_dir / "cases.py"
    
    if not cases_file.exists():
        # Try package-level test_cases.py
        cases_file = REPO_ROOT / "tests" / "parity" / package / "test_cases.py"
    
    if not cases_file.exists():
        return []
    
    # Import and extract TEST_CASES
    import importlib.util
    spec = importlib.util.spec_from_file_location("test_cases", cases_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Look for TEST_CASES or {TYPE}_TEST_CASES
    if type_name and hasattr(module, f"{type_name.upper()}_TEST_CASES"):
        return getattr(module, f"{type_name.upper()}_TEST_CASES")
    elif hasattr(module, "TEST_CASES"):
        return module.TEST_CASES
    else:
        return []


def show_diff(package: str, type_name: Optional[str] = None) -> None:
    """Show diff between old and new golden data."""
    filename = f"{type_name}_jython.json" if type_name else f"{package}_jython.json"
    golden_path = REPO_ROOT / "tests" / "parity" / package / "golden_data" / filename
    
    if not golden_path.exists():
        print(f"No existing golden data at {golden_path}")
        return
    
    # This is a placeholder - could use difflib or call git diff
    print(f"Review changes to {golden_path.relative_to(REPO_ROOT)}")
    subprocess.run(['git', 'diff', '--color', str(golden_path)], cwd=REPO_ROOT)


def main():
    parser = argparse.ArgumentParser(description="Generate golden parity test data")
    parser.add_argument(
        '--package', '-p',
        help='Package name (e.g., io, lat, terms)'
    )
    parser.add_argument(
        '--type', '-t',
        help='Specific type name within package (e.g., Lattices)'
    )
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Generate for all packages with test cases'
    )
    parser.add_argument(
        '--diff', '-d',
        action='store_true',
        help='Show diff after generating'
    )
    
    args = parser.parse_args()
    
    if args.all:
        # Find all packages with test_cases
        parity_dir = REPO_ROOT / "tests" / "parity"
        packages = []
        for pkg_dir in parity_dir.iterdir():
            if pkg_dir.is_dir() and (pkg_dir / "test_cases").exists():
                packages.append(pkg_dir.name)
        
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


if __name__ == '__main__':
    main()
