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
- **Python**: typically `ValueError` or `FileNotFoundError` from Rust/PyO3.
- **Status**: Under Review (message text often matches for terms)
- **Tests**: strict xfail on the error cases below. Exception **type** is the mismatch;
  tests do not rewrite Java expected types.

---

## org.uacalc.io

### AlgebraIO.readAlgebraFile (invalid XML cardinality)

- **Java**: `NumberFormatException: For input string: "NOT_A_NUMBER"`
- **Python**: `ValueError: Failed to parse cardinality: invalid digit found in string`
- **Status**: Under Review
- **Tests**: `read_invalid` strict xfail

### AlgebraIO.readAlgebraFile (missing file)

- **Java**: `FileNotFoundException`
- **Python**: `ValueError: No algebras found in file`
- **Status**: To Be Fixed (Python should surface a missing-file error)
- **Tests**: `read_nonexistent` strict xfail

### AlgebraIO.convertToXML output path

- **Java**: `ExtFileFilter.splitOffExtension` uses `File.getName()`, so XML is written
  as `<basename>.xml` in the current working directory.
- **Python**: writes beside the source `.alg` path.
- **Status**: Under Review
- **Tests**: `convert_to_xml` strict xfail

### AlgebraWriter / writeAlgebraFile XML `<universe>`

- **Java**: omits `<universe>` for basic algebras.
- **Python**: emits `<universe><elem>…</elem></universe>` (element order may also differ).
- **Status**: Under Review
- **Tests**: `write_algebra_file_xml`, `writer_write_algebra_xml`,
  `test_write_algebra_file_roundtrip_xml` strict xfail. Semantic reread
  (`test_write_algebra_file_roundtrip_semantic`) passes.

### AlgebraWriter.writeAlgebra / writeBasicAlgebra flush

- **Java**: does not close/flush the `PrintWriter`, so a subsequent file read is empty
  until `writeAlgebraXML()` (which closes).
- **Python**: writes immediately.
- **Status**: Accepted as Java behavior (source of truth)
- **Tests**: `writer_write_algebra`, `writer_write_basic_algebra` strict xfail

### Mace4Reader missing file

- **Java**: `FileNotFoundException` from `FileInputStream`
- **Python**: `FileNotFoundError` from `open()`
- **Status**: Accepted (platform exception names)
- **Tests**: `mace4_missing_file` strict xfail

### AlgebraIO.readAlgebraListFile

- **Java and Python**: both currently return only the last algebra in
  `cyclic2_cyclic3_list.ua` (C3). Recorded as matching Java, not as a skip.
  Contract test `test_algebra_io_read_algebra_list_file` asserts `len == 1`.

---

## org.uacalc.terms

### Terms.stringToTerm invalid input

- **Java**: `IllegalArgumentException` (`empty string`, `The string + cannot be made into a function symbol.`)
- **Python**: `ValueError` with the same message
- **Status**: Under Review
- **Tests**: `string_to_term_empty`, `string_to_term_plus_invalid` strict xfail

---

## org.uacalc.lat

### Lattices.latticeFromJoin on a cyclic / non-ordered table

- **Java**: catches `NonOrderedSetException`, prints a stack trace, **returns null**
- **Python**: constructs a `BasicLattice`
- **Status**: To Be Fixed
- **Tests**: `lattice_from_join_not_ordered` strict xfail

### Lattices.dual

- **Java**: `NullPointerException` (comment in `Lattices.java`: “this causes a npe”)
- **Python**: `ValueError` about Clone/reference limits
- **Status**: Java is buggy; Python is incomplete. Left as a visible xfail.
- **Tests**: `lattices_dual` strict xfail

### Lattices.conToSmallLattice

- **Java**: instance method on a class with a private constructor. After building
  an `OrderedSet` it **always returns null** (the poset is discarded). Null
  argument raises `NullPointerException`.
- **Python**: static `Lattices.conToSmallLattice`; raises `ValueError` (no
  `PySmallLattice` wrapper). Null / non-congruence argument also `ValueError`.
- **Status**: To Be Fixed (Python wrapper); Java return value is the golden.
- **Tests**: `lattices_con_to_small_lattice`, `lattices_con_to_small_lattice_null`
  strict xfail

### Universe list order

- **Java**: latdraw linear-extension order (e.g. chain `[1, 0]`, diamond `[0, 2, 1, 3]`)
- **Python**: element-label order `[0, 1, …]`
- **Status**: Accepted for comparison — golden serialization sorts the universe as a set.
  Cardinality, name, zero, join, meet, and leq are compared exactly and match.

---

## org.uacalc.alg.Malcev

Left alone, as specified. `minority_term` / `weak_nu_term` are not part of this
io / terms / lat golden suite.
