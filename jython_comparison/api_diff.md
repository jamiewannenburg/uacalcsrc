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
| `getName()`       | `name()` / `get_name()` (Rust often uses `name()`; alias `getName` may be patched on shims) |
| `elementIndex()`  | `element_index()` |
| `algebraType()`   | `algebra_type()` |
| `resetConAndSub()`| `reset_con_and_sub()` |
| `stringToTerm()` (static) | `string_to_term()` on the terms module / class |
| `AlgebraIO.readAlgebraFile` | `AlgebraIO.read_algebra_file` or module-level `read_algebra_file` |
| `Mace4Reader.parseAlgebraFromFile` | `parse_algebra_from_file()` |
| `BasicPartition.toString()` shape | `str()` / `__repr__` should match Java `BasicPartition` text (parity tests normalize ordering where needed) |
| `intValueAt(int[])` / table indexing | `int_value_at` / `compute_value` (Rust/Python) |
| `valueAt(int[])` (Operation) | `value_at` (may raise or map to `compute_value` on bound ops) |
| `getSymbol()` / `symbol()` | `symbol` / operation symbol accessor on bound types |
| `isIdempotent()` | `is_idempotent()` |
| `table()` / `getTable()` | `table` / `get_table()` depending on binding |
| `makeTable()` (lazy int ops) | `make_table()` on `AbstractIntOperation`-style bindings |
| `fromIntValueAtFunction` (Jython-friendly factories) | `from_int_value_at_function()` where exposed in `uacalc_lib.alg` |
| `parseAlgebraFromFile` (`Mace4Reader`) | `parse_algebra_from_file()` |
| `stringToTerm` (`Terms`) | `string_to_term()` |
| `getMeet()` / `getJoin()` (lattice-like types) | `get_meet()` / `get_join()` (where bound) |
| `intValue()` (numeric / boxed results) | `int_value()` |
| `isZero()` / `isOne()` (partition / relation helpers) | `is_zero()` / `is_one()` |
| `getPartition()` (congruence-style accessors) | `get_partition()` |
| `clone()` (Java `Object` / algebra copies) | `clone()` (often same name; verify per type) |

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
