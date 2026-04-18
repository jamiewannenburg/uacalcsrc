# Plan: Python-Jython Compatibility Layer

**Agent workflow, slices, and regeneration commands:** see [AGENTS_PARITY.md](AGENTS_PARITY.md).

To allow existing Jython scripts to run with the new Python bindings and compare their outputs, we should implement a compatibility layer.

## Current status (2026)

What is in place today (this repository):

- **Package mirroring:** `python/org/uacalc/` provides shims for the packages listed in `parity_inventory.yaml` under `python_org_uacalc_packages_with_init` (including `io`, `alg` and subpackages, `element`, `lat`, `util`, `example`, `eq`, `terms`, `group`, `fplat`). On CPython, each shim re-exports from the matching `uacalc_lib` submodule where it exists; on Jython, packages such as `org.uacalc.lat` load the Java classes from the classpath (see `python/org/uacalc/lat/__init__.py`). The `example` package follows the same pattern; `uacalc_lib.example` may still be a thin placeholder until demos are bound.
- **CamelCase on algebras:** `org.uacalc.alg` applies `monkey_patch_classes()` for `getUniverseList`, `elementIndex`, and related Java-style names on bound algebra classes where the bindings expose snake_case.
- **Verification:** `jython_comparison/scripts/validate_parity_slices.py` checks slice ids, `depends_on`, and that `java_package_prefixes` exist in `parity_inventory.yaml`; `generate_parity_inventory.py` rebuilds inventory from Java and wrapper metadata. Parity tests live under `tests/parity/` and `python/uacalc/tests/test_jython_examples_parity.py`. `jython_comparison/run_comparison.py` compares Jython vs CPython stdout for a chosen script (default `jython_comparison/test_script.py`), exiting non-zero on mismatch or subprocess failure.
- **Per-slice tracking:** `jython_comparison/parity_slices.yaml` lists owners and `status` for each Java package prefix. All tracked slices use **`parity_golden`** (golden scripts under each `parity_tests_dir` plus pytest vs Jython/CPython fixtures). Swing/NetBeans UI packages are not slice-tracked here. See `notes` on each slice for where CPython still lags Jython pending `uacalc_lib` growth.

Still pending or partial:

- **Full behavioral parity:** Many packages have import/surface tests or goldens but not full Jython-vs-CPython behavioral parity on every type (congruence lattice, subalgebra lattice, parallel helpers, etc.—see slice `status` and `notes`).
- **String parity:** `toString()`-equivalent output is aligned for some types only; remaining gaps are tracked per slice and golden tests.
- **Example/demo Java classes:** `org.uacalc.example` has a Python shim and tests under `tests/parity/example/`; Rust-backed demo types remain optional until scripts import them by name.

## Phase 1: Package Redirection
Create a Python package hierarchy that mirrors the original Java package structure.

1.  **Create `org/uacalc/` package** in the Python source.
2.  **Redirect imports:**
    - `org/uacalc/io/__init__.py`: `from uacalc_lib.io import *`
    - `org/uacalc/alg/__init__.py`: `from uacalc_lib.alg import *`
    - `org/uacalc/alg/conlat/__init__.py`: `from uacalc_lib.alg.conlat import *`

## Phase 2: Python-Side Method Aliasing
Instead of changing the Rust code (which should remain idiomatic Rust), we can wrap the Rust-exposed classes in Python to add Java-style aliases.

**Example for `Algebra`:**
```python
# python/uacalc/wrappers.py
class AlgebraWrapper:
    def __init__(self, rust_alg):
        self._rust_alg = rust_alg

    def cardinality(self):
        return self._rust_alg.cardinality()

    # Java alias
    def getUniverseList(self):
        return self._rust_alg.get_universe_list()
    
    # ... and so on
```

## Phase 3: Output String Parity
The Java `toString()` methods are used by Jython for `print`. We must ensure that the Rust/Python `__repr__` and `__str__` methods return identical strings.

**Critical Classes for Output Parity:**
- `BasicPartition` (should be `|0,1|2,3|`)
- `OperationSymbol`
- `Algebra` (usually just the name)
- `Term` (prefix/infix notation should match)

## Phase 4: Automated Verification (The "Jython Test Suite")
1.  **Install a standalone Jython 2.7 JAR.**
2.  **Write a script runner:**
    - Executes `jython script.py` (with original Java UACalc on classpath).
    - Executes `python script.py` (with our Python compatibility layer).
    - Diffs the stdout/stderr.
3.  **Target:** Zero diff output.
