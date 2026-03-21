# Plan: Python-Jython Compatibility Layer

To allow existing Jython scripts to run with the new Python bindings and compare their outputs, we should implement a compatibility layer.

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
