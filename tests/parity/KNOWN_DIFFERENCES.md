# Known Differences Between Java and Python Implementations

This document records differences found by the exact golden-data parity suite.
Java UACalc is the source of truth. These entries are **strict xfails** (unexpected
pass is a failure), never silent skips.

Malcev is intentionally left alone.

---

## Format

```markdown
### package.ClassName.methodName

- **Java behavior**: ...
- **Python behavior**: ...
- **Status**: Accepted / Under Review / To Be Fixed
```

---

## General

### Python `__repr__` / `__str__` vs Java default `toString()`

- **Java**: Default `toString()` for algebras and lattices is `ClassName@hexid`.
- **Python**: `__str__` is semantic, e.g. `BasicAlgebra(GeneralAlgebra(name: C2, ...))`
  or `BasicLattice(chain2j)`.
- **Status**: Accepted
- **Tests**: `skip_string_check=True` for those types. Term `toString()` **is**
  compared exactly (`x0`, `f(x0,x1)`, `c()`).

### Boolean string form

- **Java**: `true` / `false`
- **Python**: `True` / `False`
- **Status**: Accepted
- **Tests**: `skip_string_check=True` on boolean returns; values still compared exactly.

### Exception types

- **Java**: `NumberFormatException`, `FileNotFoundException`, `IllegalArgumentException`, …
- **Python (shim)**: Java-named types in `org.uacalc._exceptions`, with inheritance
  so `except ValueError` / `except OSError` still work. The shim translates at the
  wrapper boundary; `uacalc_lib` still raises `ValueError` / `FileNotFoundError`.
- **Status**: Shim-fixable cases below are translated. Remaining mismatches are
  library/owner (wrong message or missing-file vs empty-parse).

---

## org.uacalc.io

### AlgebraIO.readAlgebraFile (invalid XML cardinality)

- **Java**: `NumberFormatException: For input string: "NOT_A_NUMBER"`
- **Python**: shim maps the library `ValueError` to `NumberFormatException` (same
  `For input string: "…"` form when the `<cardinality>` token is available).
- **Status**: Fixed in the shim
- **Tests**: `read_invalid` passes

### AlgebraIO.readAlgebraFile (missing file)

- **Java**: `FileNotFoundException`
- **Python**: `ValueError: No algebras found in file`
- **Status**: To Be Fixed (Python should surface a missing-file error)
- **Tests**: `read_nonexistent` strict xfail
- **Owner vs shim**: Library — the parser reports “no algebras” instead of a missing file; a shim existence check would only hide that.

### AlgebraIO.convertToXML output path

- **Java**: `ExtFileFilter.splitOffExtension` uses `File.getName()`, so XML is written
  as `<basename>.xml` in the current working directory.
- **Python**: library still writes beside the source `.alg` path; the shim relocates
  that file to `cwd/<basename>.xml`.
- **Status**: Fixed in the shim
- **Tests**: `convert_to_xml` passes

### AlgebraWriter / writeAlgebraFile XML `<universe>`

- **Java**: omits `<universe>` for basic algebras.
- **Python** (current `uacalc_lib`): matches Java; no extra `<universe>`.
- **Status**: Resolved in the library (strict xfails removed after CI XPASS)
- **Tests**: `write_algebra_file_xml`, `writer_write_algebra_xml`,
  `test_write_algebra_file_roundtrip_xml` now pass.

### AlgebraWriter.writeAlgebra / writeBasicAlgebra flush

- **Java**: does not close/flush the `PrintWriter`, so a subsequent file read is empty
  until `writeAlgebraXML()` (which closes). Java has no `flush()` method.
- **Python**: org wrapper `writeAlgebra` / `writeBasicAlgebra` leave the destination
  file unflushed (empty). `AlgebraWriter.flush()` is a no-op so an explicit flush
  still matches Java. `uacalc_lib` still writes and flushes; only the org wrapper
  changed.
- **Status**: Fixed in the shim
- **Tests**: `writer_write_algebra`, `writer_write_basic_algebra` pass
- **Owner vs shim**: Shim — no-op `flush` / unflushed `writeAlgebra` in
  `python/org/uacalc/io` only.

### Mace4Reader missing file

- **Java**: `FileNotFoundException` from `FileInputStream`
- **Python**: shim `Mace4Reader.open` raises `FileNotFoundException` (also an
  `OSError` / `FileNotFoundError` subclass).
- **Status**: Fixed in the shim
- **Tests**: `mace4_missing_file` passes

### AlgebraIO.readAlgebraListFile (known Java bug)

- **Java**: SAX list reader keeps only the last algebra in
  `cyclic2_cyclic3_list.ua` (C3). This is a **known Java bug**, not a shim or
  library defect. Java golden expected values are left unchanged.
- **Python**: the org wrapper (`AlgebraIO.readAlgebraListFile` and
  `AlgebraReader.readAlgebraListFile`) deliberately returns the full list of
  every algebra (C2 and C3), including in its Jython-compatible API.
  `uacalc_lib` is unchanged.
- **Status**: Known Java bug — intentional difference; Python is the desired
  behavior
- **Tests**: `read_algebra_list_file`, `reader_read_algebra_list_file` strict
  xfail (Java golden still records last-only C3)
- **Owner vs shim**: Known Java bug. Not a shim issue and not a library issue.

---

## org.uacalc.terms

### Terms.stringToTerm invalid input

- **Java**: `IllegalArgumentException` (`empty string`, `The string + cannot be made into a function symbol.`)
- **Python**: shim maps the library `ValueError` to `IllegalArgumentException` with
  the same message.
- **Status**: Fixed in the shim
- **Tests**: `string_to_term_empty`, `string_to_term_plus_invalid` pass

---

## org.uacalc.lat

### Lattices.latticeFromJoin on a cyclic / non-ordered table

- **Java**: catches `NonOrderedSetException`, prints a stack trace, **returns null**
- **Python**: org wrapper returns `None` when the join table does not define a
  lattice (library `ValueError`, or join that is not a semilattice). `uacalc_lib`
  is unchanged and may still construct a `BasicLattice`.
- **Status**: Fixed in the shim
- **Tests**: `lattice_from_join_not_ordered` passes
- **Owner vs shim**: Shim — catch-and-`None` lives in `python/org/uacalc/lat` only.

### Lattices.dual

- **Java**: `NullPointerException` (comment in `Lattices.java`: “this causes a npe”)
- **Python**: `ValueError` about Clone/reference limits
- **Status**: Java is buggy; Python is incomplete. Left as a visible xfail.
- **Tests**: `lattices_dual` strict xfail
- **Owner vs shim**: Library/Java — Java NPE is a known bug; Python still needs Clone/reference support in `uacalc_lib`, not a rename in the shim.

### Lattices.conToSmallLattice

- **Java**: instance method on a class with a private constructor. After building
  an `OrderedSet` it **always returns null** (the poset is discarded). Null
  argument raises `NullPointerException`.
- **Python**: static `Lattices.conToSmallLattice`; raises `ValueError` (no
  `PySmallLattice` wrapper). Null / non-congruence argument also `ValueError`.
- **Status**: To Be Fixed (Python wrapper); Java return value is the golden.
- **Tests**: `lattices_con_to_small_lattice`, `lattices_con_to_small_lattice_null`
  strict xfail
- **Owner vs shim**: Library/Java — Java always returns null (owner question); Python `ValueError` is a missing `PySmallLattice` wrapper, not a shim rename.

### OrderedSets.maximals generic `Order`

- **Java**: `maximals(elems, Order)` accepts any `Order.leq`.
- **Python**: only `DivisibilityOrder`, `PrefixOrder`, and `NaturalOrder` route through
  `uacalc_lib`. Any other order raises `NotImplementedError` (no Python reimplementation).
- **Status**: Pending binding
- **Tests**: divisibility case exercises `maximals_divisibility`; generic `Order.leq`
  is listed as pending in `parity-coverage`, not as a silent skip.

### Universe list order

- **Java**: latdraw linear-extension order (e.g. chain `[1, 0]`, diamond `[0, 2, 1, 3]`)
- **Python**: element-label order `[0, 1, …]`
- **Status**: Accepted for comparison — golden serialization sorts the universe as a set.
  Cardinality, name, zero, join, meet, and leq are compared exactly and match.

---

## org.uacalc.alg.op

### Operation.isTableBased (IntOperationImp)

- **Java**: `Operations.IntOperationImp` extends `AbstractOperation` and does **not**
  override `isTableBased()`, so table-constructed ops from
  `makeIntOperation(symbol, size, table)` report `false`.
- **Python**: `IntOperation` is table-backed and `is_table_based()` returns `true`.
- **Status**: To Be Fixed (Java likely omitted the override; Python matches the
  documented meaning of the method)
- **Tests**: `op_is_table_based` strict xfail
- **Owner vs shim**: Owner/library — changing Rust `IntOperation` to lie would
  break `makeIntOperation(Operation)` skip-if-table-based logic; this is not a
  rename in the shim.

---

## org.uacalc.alg (Algebra / SmallAlgebra / BasicAlgebra)

### Algebra.setMonitor / getMonitor / ProgressReport

- **Java**: `setMonitor(ProgressReport)` stores a static `GeneralAlgebra.monitor`.
  Jython rejects a non-`ProgressReport` argument with `TypeError`.
- **Python**: `org.uacalc.ui.tm.ProgressReport` is not bound. The shim stores a
  module-level monitor like Java's static field, accepts `None`, and raises
  `TypeError` for any other argument.
- **Status**: Accepted — UI type is out of scope; exception type matches Jython
- **Tests**: `alg_set_monitor` (TypeError), `alg_monitoring_after_set`,
  `alg_get_monitor_default`, `alg_monitoring_default`
- **Owner vs shim**: Shim — argument check only. Not a library defect.

### SmallAlgebra.getElement(null)

- **Java/Jython**: `getElement(int)` — Jython cannot coerce `None` to `int`, so
  this is `TypeError` (`getElement(): 1st arg can't be coerced to int`), not NPE.
- **Python**: `int(None)` is also `TypeError`.
- **Status**: Accepted — matches Jython
- **Tests**: `small_get_element_null`
- **Owner vs shim**: Shim — argument coercion. Not a library defect.

---

## org.uacalc.alg.Malcev

Left alone, as specified. `minority_term` / `weak_nu_term` are not part of this
io / terms / lat golden suite.
