# Analysis: Jython vs. Python API Alignment

To achieve a "drop-in replacement" status for existing Jython scripts, the new Python bindings must match the Java-style API exposed by Jython.

## 1. Package Structure Alignment
Currently, our Python bindings use a "flat" or "Rust-idiomatic" structure:
- `uacalc_lib.alg`
- `uacalc_lib.lat`

Jython scripts expect the original Java package structure:
- `org.uacalc.alg`
- `org.uacalc.io`
- `org.uacalc.alg.conlat`

### Suggested Change:
Create a Python-side wrapper package `org.uacalc` that imports from `uacalc_lib` to provide the expected namespace.

```python
# org/uacalc/alg/__init__.py
from uacalc_lib.alg import SmallAlgebra, BasicAlgebra
```

---

## 2. Method Naming (CamelCase vs. snake_case)
Rust and our current Python bindings prefer `snake_case`. Java and Jython use `camelCase`.

| Jython/Java Method | Current Python Method |
|-------------------|-----------------------|
| `cardinality()`   | `cardinality()` (Matches!) |
| `getUniverseList()`| `get_universe_list()` |
| `readAlgebraFile()`| `read_algebra_file()` |
| `con()`           | `con()` (Matches!) |
| `sub()`           | `sub()` (Matches!) |

### Suggested Change:
Expose aliases in the Python classes to support both.
```python
class Algebra:
    def getUniverseList(self):
        return self.get_universe_list()
```

---

## 3. The `con()` and `sub()` Pattern
In Jython, `alg.con()` returns a `CongruenceLattice` object. In our Rust implementation, we have something similar, but we need to ensure the return type has the same methods (e.g., `getUniverseList()`).

### Discrepancy:
- **Jython:** `alg.con()` returns the lattice.
- **Current Rust:** `alg.con()` (in `BasicAlgebra`) returns a reference to a `CongruenceLattice`. We need to ensure the Python binding for this lattice exposes the Java-style methods.

---

## 4. Output String Formatting (`__str__` vs `toString()`)
Jython uses Java's `toString()` for its `__str__` and `__repr__`.

### Example (Partition):
- **Jython/Java:** `|0,1|2,3|`
- **Current Python:** May vary depending on implementation.

### Suggested Change:
Override `__repr__` and `__str__` in all bound classes to match the Java `toString()` output exactly. This is critical for automated output comparison (diffing).

---

## 5. Static Utility Classes
Jython uses classes like `AlgebraIO` with static methods.

### Current Python:
We often use modules: `uacalc_lib.io.read_algebra_file()`.

### Suggested Change:
Wrap these in Python classes with `@staticmethod` to match the `AlgebraIO.readAlgebraFile()` syntax.
