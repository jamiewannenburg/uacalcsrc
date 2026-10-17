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

- **Java**: `FileNotFoundException` with
  `<absolute path> (No such file or directory)` (Jython `str(exc)` also has
  the `java.io.FileNotFoundException: ` prefix; the harness strips it).
- **Python**: shim existence check in `AlgebraIO.readAlgebraFile` /
  `AlgebraReader.readAlgebraFile` raises `FileNotFoundException` with the
  same `getMessage()` form. `uacalc_lib` is unchanged.
- **Status**: Fixed in the shim
- **Tests**: `read_nonexistent` passes
- **Owner vs shim**: Shim — check-before-read in `python/org/uacalc/io` only.

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
- **Python**: org wrapper raises `NullPointerException` to match Java. `uacalc_lib.lat.dual`
  is unchanged (still the Clone/reference `ValueError`).
- **Status**: Fixed in the shim
- **Tests**: `lattices_dual` passes
- **Owner vs shim**: Shim — Java NPE is a known bug; the org wrapper matches it.
  Library dual is still incomplete.

### Lattices.conToSmallLattice

- **Java**: instance method on a class with a private constructor. After building
  an `OrderedSet` it **always returns null** (the poset is discarded). Null
  argument raises `NullPointerException`.
- **Python**: org wrapper returns `None`; null argument raises `NullPointerException`.
  `uacalc_lib.lat.con_to_small_lattice` now returns a `SmallLattice` (`PySmallLattice`).
- **Status**: Fixed in the shim (Java null/NPE). Library binding added.
- **Tests**: `lattices_con_to_small_lattice`, `lattices_con_to_small_lattice_null` pass
- **Owner vs shim**: Shim matches Java’s null/NPE. Library exposes `PySmallLattice`
  for direct `uacalc_lib` use.

### OrderedSets.maximals generic `Order`

- **Java**: `maximals(elems, Order)` accepts any `Order.leq`. Jython implements the
  interface with a Python class.
- **Python**: `org.uacalc.lat.Order` is a subclassable class with `leq(a, b)` (or
  `Order(callable)`). `OrderedSets.maximals` always calls `uacalc_lib.lat.maximals`,
  which evaluates Python `leq` (object method or two-arg callable) inside the Rust
  maximals algorithm. Ints, lists, tuples, and user objects work.
- **Status**: Implemented
- **Tests**: `order_leq_*`, `ordered_sets_maximals_generic_divisibility`,
  `_callable`, `_lists`, `_objects`, `_empty`, `_null_order`
- **Owner vs shim**: Thin shim (`Order` + null checks). Algorithm is
  `uacalc_lib/src/lat.rs` `maximals`.

### SmallLattice.upperCoversIndices (known Java bug)

- **Java/Jython**: `Lattices.conToSmallLattice` always returns null (the
  constructed poset is discarded). Calling `null.upperCoversIndices(0)` is
  Jython `AttributeError` (`'NoneType' object has no attribute
  'upperCoversIndices'`). There is no public Java class that implements
  `SmallLattice`. This is a **known Java bug**, not a shim or library defect.
  Java golden expected values are left unchanged.
- **Python**: org `conToSmallLattice` still returns `None` (Java null).
  `DiamondLattice.upperCoversIndices(0)` is `[1, 2]` (bottom covered by the
  two atoms) — the desired SmallLattice behaviour.
- **Status**: Known Java bug — intentional difference; Python is the desired
  behavior
- **Tests**: `small_lattice_upper_covers_indices` strict xfail (Java golden
  still records the AttributeError)
- **Owner vs shim**: Known Java bug. Not a shim issue and not a library issue.

### BasicLattice.makeOrderedSet

- **Java**: returns `org.latdraw.orderedset.OrderedSet` (POElem universe).
- **Python**: returns `uacalc_lib` `OrderedSet` (int labels) via
  `OrderedSet.from_lattice`. Cardinality matches.
- **Status**: Accepted for comparison — golden cases compare cardinality, not
  the latdraw type.
- **Tests**: `basic_lattice_make_ordered_set`, `ordered_set_*_via_poset`

### BasicLattice.findJoinIrred / findMeetIrred / irredundant* / makeIrredundant*

- **Java**: `findJoinIrred(1, 0)` on the 2-chain is `1`; `findMeetIrred(0, 1)` is
  `0`; `irredundantJoinDecomposition(1)` / `makeIrredundantJoin(jis)` are `[1]`;
  `irredundantMeetDecomposition(0)` / `makeIrredundantMeet(mis)` are `[0]`.
- **Python**: org wrapper implements the Java algorithms on `BasicLattice`
  using existing `join` / `meet` / `leq` / irreducibles / covers.
- **Status**: Implemented
- **Tests**: `basic_lattice_find_join_irred`, `basic_lattice_find_meet_irred`,
  `basic_lattice_irredundant_join_decomp`, `basic_lattice_irredundant_meet_decomp`,
  `basic_lattice_make_irredundant_join`, `basic_lattice_make_irredundant_meet`,
  plus diamond (`_m3`) and empty/null (`_leq`, `_zero`, `_one`) cases
- **Owner vs shim**: Shim — Java algorithms in `python/org/uacalc/lat`.

### BasicLattice.con / sub

- **Java**: `con()` of the 2-chain has cardinality **2**; `sub()` has cardinality
  **4**.
- **Python**: org wrapper builds a `BasicAlgebra` from the join/meet tables and
  returns `CongruenceLattice` / `SubalgebraLattice`.
- **Status**: Implemented
- **Tests**: `basic_lattice_con`, `basic_lattice_sub`, `basic_lattice_con_m3`,
  `basic_lattice_sub_m3`
- **Owner vs shim**: Shim — table extract in `python/org/uacalc/lat`; lattices
  from `uacalc_lib`.

### BasicLattice from CongruenceLattice

- **Java**: `BasicLattice("ConC2", C2.con(), false)` has cardinality **2**.
- **Python**: `PyBasicLattice::new` now calls `universe()` and
  `join_irreducibles()` on the congruence lattice (Java `makeOrderedSet` does
  the same) before `new_from_lattice`, so cardinality is **2**.
- **Status**: Fixed in the library
- **Tests**: `basic_lattice_from_con_c2`, `basic_lattice_from_con_lat2`,
  plus `basic_from_con_*` for C3, N5, M3, ba2
- **Owner vs shim**: Owner/library — `PyBasicLattice::new` /
  `BasicLattice::new_from_lattice`.

### BasicLattice from SubalgebraLattice

- **Java**: `BasicLattice(name, lat)` accepts any `Lattice`, including
  `SubalgebraLattice`.
- **Python**: `PyBasicLattice::new` now also accepts a `SubalgebraLattice`,
  computes `universe` + `join_irreducibles`, and builds
  `BasicLattice<BasicSet>`. Cardinality matches Java. Join/meet/leq on that
  BasicSet view stay Int32-only (same limitation as before).
- **Status**: Fixed in the library
- **Tests**: `basic_from_sub_c2_card`, `basic_from_sub_c3_card`,
  `basic_from_sub_lat2_card`, `basic_from_sub_ba2_card`,
  `sub_get_basic_lattice_c2`
- **Owner vs shim**: Owner/library — `PyBasicLattice::try_from_subalgebra_lattice`.

### Deliberately unwrapped lat methods

- **Java**: `getVertices`, `main`, `run` are Swing/latdraw drawing helpers;
  `intValueAt` / `valueAt` are methods of the anonymous join/meet
  `Operation`s inside `BasicLattice`, not of the lattice itself.
  `getDiagram` is also GUI (dotted return type, not in the 41-method scan).
- **Python**: not bound. Filter/ideal/covers/leq/univ are covered via
  `BasicLattice` and `OrderedSet`.
- **Status**: Skipped by design (GUI / scanner false-positives). Malcev is
  out of scope.
- **Tests**: none (noted in `PENDING_BINDINGS` and `parity_slices`).

### Universe list order

- **Java**: latdraw linear-extension order (e.g. chain `[1, 0]`, diamond `[0, 2, 1, 3]`)
- **Python**: element-label order `[0, 1, …]`
- **Status**: Accepted for comparison — golden serialization sorts the universe as a set.
  Cardinality, name, zero, join, meet, and leq are compared exactly and match.

---

## org.uacalc.alg.op

### Operation.isTableBased (IntOperationImp)

- **Java**: `Operations.IntOperationImp` extends `AbstractOperation` and does **not**
  override `isTableBased()`, so `makeIntOperation(symbol, size, table)` reports
  `false`. Function / value-at constructors also stay `false`. Factories that
  override it (`makeIntOperation(Operation)`, `makeConstantIntOperation`) report
  `true`.
- **Python**: the org wrapper records how each `Operation` was constructed and
  `isTableBased()` uses that flag. It does not read the Rust backend (always
  table-based). `uacalc_lib` is unchanged.
- **Status**: Fixed in the shim
- **Tests**: `op_is_table_based` passes
- **Owner vs shim**: Shim — construction flag in `python/org/uacalc/alg/op` only.

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

## org.uacalc.alg (Subalgebra / products / quotients)

### ProductAlgebra.calcCard([])

- **Java**: `calcCard(new int[0])` is `1` (empty product of `BigInteger.ONE`).
- **Python**: the org wrapper returns `1` for an empty size list before calling
  `uacalc_lib` (which still rejects empty sizes). `uacalc_lib` is unchanged.
- **Status**: Fixed in the shim
- **Tests**: `prod_calc_card_empty` passes
- **Owner vs shim**: Shim — empty-list check in `python/org/uacalc/alg` only.

### ProductAlgebra([]) / PowerAlgebra(alg, 0)

- **Java**: `makeOperations()` does `algebras.get(0)` and throws
  `IndexOutOfBoundsException: Index 0 out of bounds for length 0`.
- **Python**: the org wrapper raises the same `IndexOutOfBoundsException` before
  calling `uacalc_lib` (which would reject empty products with `ValueError`).
- **Status**: Fixed in the shim
- **Tests**: `prod_empty_ctor`, `pwr_zero` pass
- **Owner vs shim**: Shim — argument check only. Not a library defect.

### PowerAlgebra.elementIndex (known Java bug)

- **Java**: `PowerAlgebra.elementIndex` linear-searches `universe()` for
  `IntArray`, but `ProductAlgebra.makeCartesianProduct` yields `ArrayList`s, so
  the method always returns `-1`.
- **Python**: the org wrapper matches that always-`-1` result.
- **Status**: Known Java bug — matched on purpose
- **Tests**: `pwr_element_index` passes
- **Owner vs shim**: Known Java bug. Shim matches Java; not a library defect.

### FreeAlgebra AlgebraIO write/read (known Java bug)

- **Java (live)**: F(1) over cyclic2 has cardinality 2, universe
  `[[0,1],[0,0]]`, terms `x`, `+(x,x)`, and `+` table `[1,0,0,1]`. Live
  generation already matches Python (`fa_live_*`).
- **Java (AlgebraIO)**: `writeFreeAlgebra` emits `<freeAlgebra>` with
  coordinate-tuple generators/universe and a nested `<bigProductAlgebra>`
  whose root factor is the *generating* algebra. `AlgebraReader` has
  handlers for `basicAlgebra`, `productAlgebra`, `powerAlgebra`,
  `quotientAlgebra`, `subAlgebra`, `bigProductAlgebra`, and
  `subProductAlgebra`, but **no `freeAlgebra` end-element handler**. After
  write/read the last nested `basicAlgebra` wins, so the result is the
  generating algebra, not F(n):
  - F(1)/C2: live table `[1,0,0,1]`; after IO, C2 table `[0,1,1,0]`, name
    `C2` (not a relabel of F(1) — it *is* C2).
  - F(1)/C3: live table `[1,2,0,2,0,1,0,1,2]`; after IO, C3 table
    `[0,1,2,1,2,0,2,0,1]`.
  - F(1)/lat2: live card **1**; after IO, lat2 card **2** (base lattice).
  - F(1)/ba2: live card **4**; after IO, ba2 card **2** (base boolean
    algebra).
- **Python**: `writeAlgebraFile` still emits Java `<freeAlgebra>` XML
  (`AlgebraWriter::write_free_algebra_xml_to_file`). The reader **does
  not** copy the Java bug: `</freeAlgebra>` rebuilds F(n) from the nested
  generating algebra plus generator count and materializes a
  `BasicAlgebra` with F(n)'s universe and tables. Python write-then-read
  of F(n) therefore returns F(n)'s cardinality and tables (see
  `test_python_write_read_free_algebra_restores_fn`).
- **Status**: Known Java bug — intentional difference; Python is the
  desired behavior. Java golden expected values are left unchanged.
- **Tests**: `fa_roundtrip_write_read`, `fa_roundtrip_c3_f1`,
  `fa_roundtrip_lat2_f1`, `fa_roundtrip_ba2_f1` strict xfail (Java golden
  still records the generating algebra). IO cases `wr_free_*` and
  `read_special_free_c2_f1` are the same bug and are also strict xfail.
  `xml_free_c2_f1_tags` and live `fa_live_*` still pass.
- **Owner vs shim**: Known Java bug on read. Owner/library write is
  implemented (`src/io/mod.rs` `write_free_algebra_xml_to_file`). Reader
  reconstruction is in `src/io/algebra_reader.rs`.

### AlgebraWriter typed XML (product / power / quotient / subalgebra)

- **Java**: `writeAlgebra` dispatches to `writeProductAlgebra`,
  `writePowerAlgebra`, `writeQuotientAlgebra`, `writeSubalgebra`,
  `writeBigProductAlgebra`, `writeSubProductAlgebra` and writes nested
  factors / root / congruence / subuniverse.
- **Python**: dedicated Rust writers emit the same nested tags
  (`write_product_algebra_xml_to_file`, `write_power_algebra_xml_to_file`,
  `write_quotient_algebra_xml_to_file`, `write_subalgebra_xml_to_file`,
  `write_sub_product_algebra_xml_to_file`). The generic
  `Box<dyn SmallAlgebra<i32>>` writer still cannot see factors/root, so
  those paths error and the org shim dispatches to the dedicated APIs.
  `write_big_product_typed` is the nested super algebra of
  `<freeAlgebra>` / `<subProductAlgebra>`. Standalone `BigProductAlgebra`
  is not a `SmallAlgebra`, so Java `AlgebraWriter(alg, path)` cannot take
  it. Nested derived factors are written as `<basicAlgebra>` tables (same
  as the previous org shim) when the nested value is already a basic
  algebra, which matches the checked-in Java fixtures.
- **Status**: Implemented in the library
- **Tests**: `wr_prod_*`, `wr_pwr_*`, `wr_quot_*`, `wr_sub_*`,
  `wr_subprod_*`, `xml_*_tags`, plus
  `test_typed_algebra_python_roundtrip.py`
- **Owner vs shim**: Owner/library — `src/io/mod.rs` dedicated writers.
  Org shim only dispatches.

### AlgebraReader nested algebra kinds

- **Java**: reconstructs `ProductAlgebra` / `PowerAlgebra` /
  `QuotientAlgebra` / `Subalgebra` / `BigProductAlgebra` /
  `SubProductAlgebra` from nested XML (card 4 for C2×C2 and C2², card 1
  for the `{0}` subalgebra).
- **Python**: `src/io/algebra_reader.rs` still materializes a
  `BasicAlgebra` (last nested basic, or a rebuilt `FreeAlgebra`). The org
  shim then rebuilds the typed algebra from the raw XML
  (`rebuild_typed_algebra` in `python/org/uacalc/io/_typed_xml.py`).
  PowerAlgebra tables use Horner/product encoding, matching Java C2²
  `[0,1,2,3,1,0,3,2,2,3,0,1,3,2,1,0]` rather than cyclic-on-4.
- **Status**: Implemented (shim rebuild + library Horner tables)
- **Tests**: `read_special_product`, `read_special_power`,
  `read_special_quotient`, `read_special_subalgebra`,
  `read_special_subproduct` and the wider `read_special_*` / `wr_*` cases
- **Owner vs shim**: Owner/library for write and PowerAlgebra tables;
  org shim for typed rebuild on read.

### Subalgebra Jython serialize is Class@hex

- **Java**: `Subalgebra.toString()` is `org.uacalc.alg.Subalgebra@hex`.
  The Jython golden generator historically missed `"algebra"` in the
  class name (`Subalgebra` has a lowercase `a`), so the frozen golden
  return value is that identity string instead of tables.
- **Python**: write/read rebuilds a typed `Subalgebra` with cardinality
  and Horner tables (C2 on `{0}` is card 1, table `[0]`). The parity
  harness treats a Java `Class@hex` fallback golden as matching that
  semantic algebra summary.
- **Status**: Documented difference — Python is the meaningful format
- **Tests**: `wr_sub_c2`, `read_special_subalgebra`, `wr_sub_c3`,
  `wr_sub_c2_full`, `read_special_subalgebra_c3`
- **Owner vs shim**: Known Java `toString` / golden-capture gap. Not a
  library defect.

### Algebras.quasiCriticalCongruences

- **Java**: on cyclic2 the list is the *zero* congruence `|0|1|` (one
  singleton block each). Earlier notes that said `|0,1|` were wrong; the
  golden value is `|0|1|`.
- **Python**: `uacalc_lib` now matches Java. The previous empty list was
  `Algebra::universe()` on a congruence lattice whose universe had not been
  computed (`make_universe` lives on the inherent `universe(&mut self)`).
- **Status**: Fixed in the library
- **Tests**: `algs_quasi_crit_congs` plus wider `algs_quasi_crit_*`
- **Owner vs shim**: Owner/library — `src/alg/algebras.rs`.

### QuotientAlgebra.elementIndex (known Java quirk)

- **Java**: `elementIndex(obj)` returns
  `congruence.representative(superAlgebra.elementIndex(obj))`, a representative
  in the *super* algebra, not the quotient index (`binarySearch` of
  representatives).
- **Python**: the org wrapper matches that super-representative result.
- **Status**: Known Java quirk — matched on purpose
- **Tests**: `quot_element_index` passes
- **Owner vs shim**: Known Java bug/quirk. Shim matches Java.

---

## org.uacalc.alg.conlat

### CongruenceLattice.getDescription (default)

- **Java**: `"Congruence Lattice of " + alg` uses `Algebra.toString()`, i.e.
  `org.uacalc.alg.BasicAlgebra@hex`.
- **Python**: library `get_description` now uses the same
  `org.uacalc.alg.<Type>@hex` identity form. The hex is not stable across
  processes; the parity harness compares class prefixes.
- **Status**: Fixed in the library
- **Tests**: `cl_get_description` passes. After `setDescription` the
  strings still match (`cl_set_description`).
- **Owner vs shim**: Owner/library — `src/alg/conlat/congruence_lattice.rs`.

### CongruenceLattice.Delta

- **Java**: `Delta(zero, one)` on cyclic2 is the one partition `|0,1|`.
- **Python**: library implements Java’s algorithm (congruence-as-algebra of
  `alpha`, then join of `Cg((a,a),(b,b))` for pairs in `beta`).
- **Status**: Fixed in the library
- **Tests**: `cl_delta` passes
- **Owner vs shim**: Owner/library — `src/alg/conlat/congruence_lattice.rs`.

### CongruenceLattice.idempotentPolynomials

- **Java**: one nonconstant idempotent unary polynomial on cyclic2.
- **Python**: library now generates Pol_1(A) from the identity tuple in
  `A^{|A|}` plus constants (Java’s `includeConstants`), then filters
  idempotent non-constants.
- **Status**: Fixed in the library
- **Tests**: `cl_idempotent_polys` passes
- **Owner vs shim**: Owner/library — `src/alg/conlat/congruence_lattice.rs`.

### CongruenceLattice.getPermutabilityLevelWitnesses

- **Java**: after `permutabilityLevel()` on cyclic2 (a chain, no incomparable
  pair) the witness array is two nulls (`None` in Jython). Incomparable
  pairs use `BasicPartition.permutabilityLevel(par0, par1)`.
- **Python**: library stores `[None, None]` until an incomparable pair is
  found, and uses `Partition::permutability_level_of_join`.
- **Status**: Fixed in the library
- **Tests**: `cl_perm_witnesses` passes
- **Owner vs shim**: Owner/library — `src/alg/conlat/congruence_lattice.rs`.

---

## org.uacalc.terms

Taylor / MMS (`markovicMcKenzieTerm`, `siggersTerm`, `interprets`, `canonicalForm`,
`makeBalancedTayorTerm`) is Malcev-adjacent and is not wrapped in this pass.

Anonymous `Operation` methods nested inside `interpretation()` (`intValueAt`,
`makeTable`, `getTable`, `valueAt`, `getTerm`, `getOrderedvariables`) are not
methods of `VariableImp` / `NonVariableTerm`. They appear in the Java-file
heuristic. Exercise them on the returned operation instead.

`Terms.main` / `Terms.testFlatten` are Java development helpers.

### VariableImp.interpretation (varlist omits the variable)

- **Java**: `varlist.indexOf(this)` is `-1`; interpretation still returns a
  projection operation. `intValueAt` later throws
  `ArrayIndexOutOfBoundsException`.
- **Python**: `uacalc_lib` rejects the missing name (`ValueError`); the org shim
  maps that to `NullPointerException` at construction. Left as-is: building a
  projection at index `-1` is not desirable.
- **Status**: Known Java bug — intentional difference; Python is the desired
  behavior
- **Tests**: `variable_interp_missing_var` strict xfail (Java golden still
  records arity 1)
- **Owner vs shim**: Known Java bug. Not a shim issue and not a library issue.

### Term.interpretation operation symbol

- **Java**: anonymous op named `"Op_" + term`.
- **Python**: library `IntOperation` uses `Op_{name}` for variables and the
  term string (no `Op_` prefix) for compound terms. Tests compare
  `intValueAt` tables, not symbol names.
- **Status**: Accepted
- **Owner vs shim**: Owner/library — symbol naming in `src/terms/mod.rs`.

---

## org.uacalc.eq

`Equation.findFailure(alg, ProgressReport)` / `findFailureMap(alg, report)`
overloads are not bound (`org.uacalc.ui.tm.ProgressReport`). `Equations.main`
is a Java stub.

Native `uacalc_lib.eq.Equation.left_side` / `right_side` still return strings;
the org shim's `leftSide` / `rightSide` return term objects via
`left_side_term` / `right_side_term`. Same split for
`Presentation.get_relations` (strings) vs `getRelations` (Equation objects).

---

## org.uacalc.alg.sublat

### BasicSet.union index bug

- **Java**: `union` loops `if (!lst.contains(i)) lst.add(set2.get(i))` using the
  *index* `i`, not the element. `{0,2} ∪ {1,3}` is `{0,2,3}` (drops 1).
- **Python**: org shim reproduces that Java loop. `uacalc_lib` still does a
  correct set-union.
- **Status**: Matched in the shim
- **Tests**: `bs_union_index_bug` passes
- **Owner vs shim**: Shim — `python/org/uacalc/alg/sublat/_jython_compat.py`

### BasicSet.union duplicate-preserving normalize

- **Java**: `normalize()` only sorts, so `union({5,6}, {5})` is `[5, 5, 6]`.
- **Python**: `BasicSet::new` dedupes to `[5, 6]`.
- **Status**: Strict xfail (library keeps unique sets)
- **Tests**: `bs_union_keeps_dups`
- **Owner vs shim**: Owner/library — do not teach `BasicSet` to store duplicates.

### SubalgebraLattice.meet / join(List) / atoms / coatoms / meetIrreducibles

- **Java**: these methods are identically `null` (empty stubs / TODOs).
- **Python**: org shim returns `None`. `uacalc_lib` still implements lattice
  meet as intersection and `join_list` as a fold.
- **Status**: Matched in the shim
- **Owner vs shim**: Shim

### SubalgebraLattice.Sg vs sg

- **Java**: `sg(int[])` returns `BasicSet`; `Sg(...)` returns `Subalgebra`.
- **Python**: org shim dispatches the same way (previously aliased `Sg` to `sg`).
- **Status**: Fixed in the shim
- **Tests**: `sl_sg0`, `sl_Sg_card`, `sl_Sg_name`

### SubalgebraLattice.con / sub of the lattice

- **Java**: `con()` / `sub()` go through `getBasicLattice()` and compute
  `Con(Sub(A))` / `Sub(Sub(A))` (card 4 and 8 on cyclic2).
- **Python**: `BasicLattice` built from a `BasicSet` universe cannot extract i32
  join/meet tables (`get_element` is ops-only).
- **Status**: Strict xfail (roadmap)
- **Tests**: `sl_con`, `sl_sub`
- **Owner vs shim**: Owner/library — BasicLattice over `BasicSet`

### SubalgebraLattice.getDiagram

- **Java**: latdraw `Diagram` when drawable.
- **Python**: not bound (GUI / Swing out of scope).
- **Status**: Strict xfail
- **Tests**: `sl_get_diagram`

---

## org.uacalc.element

### Element / SubProductElement parent accessors

- **Java**: `getParent()`, `getParentArray()`, and `parentIndexArray()` are
  empty stubs (`return null`).
- **Python**: org shim / `uacalc_lib` return `None`.
- **Status**: Matched
- **Tests**: `f1_0_parent`, `f1_0_parent_array`, `f1_0_parent_index_array`,
  `sp_parent`

### SubProductElement.equals / hashCode

- **Java**: no overrides; `Object` identity equality and identity hash.
- **Python**: no `__eq__` / `__hash__` on the PyO3 class; identity as well.
  Two separately constructed elements with the same IntArray and algebra
  are not equal.
- **Status**: Matched
- **Tests**: `f1_0_eq_self`, `f1_0_eq_copy`, `f1_0_hash_stable`

### SubProductElement.toString trailing comma

- **Java**: `toString` appends `"var -> [coords], "` per variable and leaves
  the trailing `", "` (the "delete the last ," line is commented out).
- **Python**: matches that form, including the trailing comma-space.
- **Status**: Matched
- **Tests**: `f1_0_to_string`, `sp_0_to_string`, `spn_to_string`

### SubProductElement.getVariableList when findTerms is false

- **Java**: `getTerm()` is null, so `getVariableList()` NPEs.
- **Python**: shim raises `NullPointerException`.
- **Status**: Matched
- **Tests**: `spn_vars_npe`

### Element instantiation

- **Java**: interface; cannot `new Element()`.
- **Python**: `Element()` raises `ValueError` ("interface and cannot be
  instantiated"). Not compared in goldens.
- **Status**: Accepted (pending binding note)
- **Owner vs shim**: Library constructor guard on `uacalc_lib.element.Element`

---

## org.uacalc.util

### IntArray.getArray live alias

- **Java**: `getArray()` / `toArray()` return the live backing `int[]`; mutating it changes the IntArray.
- **Python**: `uacalc_lib` IntArray is copy-on-write and returns a copy.
- **Status**: Strict xfail (roadmap)
- **Tests**: `ia_getarray_copy`
- **Owner vs shim**: Owner/library — keep copy-on-write

### IntArray.setIntArray replace

- **Java**: `setIntArray(int[])` replaces the backing store and can change `universeSize`.
- **Python**: shim can write same-length values via `set`; length change raises `UnsupportedOperationException`.
- **Status**: Strict xfail (roadmap)
- **Tests**: `ia_setintarray_replace`
- **Owner vs shim**: Owner/library — copy-on-write IntArray

### LongList.stream / parallelStream

- **Java**: default Java 8 `Stream` / parallel stream over `get(k)`.
- **Python**: not bound.
- **Status**: Strict xfail
- **Tests**: `ll_stream`, `ll_parallel_stream`
- **Owner vs shim**: Out of scope (Java 8 Stream)

### SimpleList.app / rev

- **Java**: `app` / `rev` are commented out of the live class (scanner still
  sees them in source). Calling them is `AttributeError`.
- **Python**: aliases of `append` / `reverse`.
- **Status**: Strict xfail
- **Tests**: `sl_app_commented`, `sl_rev_commented`
- **Owner vs shim**: Owner — do not expose commented-out Java

### Commented-out Java (not wrapped)

- **Java**: `IntArray.satisfiesConstraint`, `SimpleList` iterator
  `regenerate` / `reinitialize` / `removeConflicts` live only in comments.
  `*.main` methods are development helpers.
- **Python**: not wrapped.
- **Status**: Skipped (inventory / PENDING_BINDINGS notes)
- **Owner vs shim**: Out of scope (dead / helper Java)

### SimpleList serialization

- **Java**: custom `writeObject` / `readObject` encodes the sharing graph.
- **Python**: not bound. Core list ops (cons/first/rest/append/reverse) match.
- **Status**: Documented gap (no golden case; cannot dual-run Java serialization)
- **Owner vs shim**: Owner — serialization roadmap

---

## org.uacalc.group

### PermutationGroup constructors do not close the group

- **Java**: `PermutationGroup(name, generators)` / `(name, generators, universeList)`
  only store the lists. `universe` and `operations` stay null, so
  `cardinality()` is `-1`. `universeList` is unused.
- **Python (shim)**: matches that shell. Group elements are obtained by closing
  generators under the static `prod` / `inv` / `id` operations (goldens).
- **Status**: Matched
- **Tests**: `s2_cardinality`, `s3u_cardinality`, `empty_cardinality`, `close_*`

### PermutationGroup.toString

- **Java**: default `Object.toString()` (`PermutationGroup@hex`).
- **Python**: semantic `PermutationGroup(name)`.
- **Status**: Accepted
- **Tests**: surface smoke uses `getName`; behavioral cases `skip_string_check`
  on the group object itself. IntArray `toString` of `prod`/`inv`/`id` **is**
  compared exactly (`[1, 0, 2]`).

### uacalc_lib extras (`to_basic_algebra`, `automorphism_group`)

- **Java**: no such methods on `org.uacalc.group.PermutationGroup`.
- **Python (`uacalc_lib`)**: `to_basic_algebra` builds a `BasicAlgebra` on the
  underlying set `{0,…,n-1}` with product/inverse/identity operations that take
  integer args, not a Cayley table of the generated permutation group.
  `automorphism_group` enumerates `Aut(A)` and is Rust-only.
- **Status**: Documented gap / roadmap (Cayley-table conversion). Not in the
  Java goldens.
- **Owner vs shim**: Owner — deep; leave the Java class as the parity target.

---

## org.uacalc.fplat

### PartiallyDefinedLattice constructor

- **Java**: `(String name, Order<Variable> order, List<List<Variable>> joins, List<List<Variable>> meets)`. The name is unused (no field). `leq` delegates to `order.leq`. `definedJoins` / `definedMeets` are package-private fields; there are no public join/meet methods.
- **Python (org wrapper)**: same 4-arg constructor. `getDefinedJoins` / `getDefinedMeets` expose the stored lists (Jython goldens also read the Java fields). `uacalc_lib.fplat` still has a 3-arg shortcut `(name, joins, meets)` with a name-order; that is not the org.uacalc API.
- **Status**: Matched on `org.uacalc.fplat`
- **Tests**: `tests/parity/fplat`

### PartiallyDefinedLattice.toString

- **Java**: default `Object.toString()` (`PartiallyDefinedLattice@hex`).
- **Python**: semantic `PartiallyDefinedLattice(name)`.
- **Status**: Accepted
- **Tests**: `skip_string_check` on toString cases

---

## org.uacalc.alg.parallel

### Pool has no public methods

- **Java**: empty class; `static ForkJoinPool fjPool` is package-private.
- **Python**: class + constructor; extras `fj_pool()` / `is_initialized()` only check that a runtime exists. Thread counts are not tested.
- **Status**: Matched on the importable class; field/thread internals skipped
- **Tests**: `pool_class_name`, `pool_construct`

### SingleClose.doOneStep thread internals

- **Java**: `doOneStep(ForkJoinPool, Thread, ProgressReport, CloserTiming)`. Constructor prints `increment: N`. Term map may differ across runs (Java comment). `compute()` is the ForkJoin hook.
- **Python**: `doOneStep` accepts those args and ignores them; uses the library closer pass. Timing, thread counts, and term maps are not compared. New elements are sorted.
- **Status**: Deterministic element sets compared; internals skipped
- **Tests**: `par_*` pass. Direct `single_close_*` one-step goldens are strict xfail (below).

### SingleClose.doOneStep on a Java IntOperation (`valueAt(int[][])`)

- **Java**: `IntOperation.valueAt(int[][])` is `UnsupportedOperationException`. Calling `SingleClose.doOneStep` with a table operation from `Operations.makeIntOperation` therefore does not produce new elements that way.
- **Python**: Rust `SingleClose` uses `value_at_arrays` and returns new elements. CPython `BigProductAlgebra.operations()` is also not bound, so the script-usable parallel closer remains `Closer.doParallel` / `sgClose`.
- **Status**: Strict xfail (roadmap). Parallel element-set parity is covered by the `Closer.doParallel` `sgClose` goldens.
- **Tests**: `single_close_c2_one_step`, `single_close_m3_one_step` strict xfail
- **Owner vs shim**: Owner/library — `value_at_arrays` vs Java UOE. Not a shim issue.

### Closer.doParallel / sgCloseParallel

- **Java**: static `Closer.doParallel` routes `sgClose()` through `sgCloseParallel(elems, closedMark, ConcurrentMap)`. The 3-arg overload plus debug `System.out` are not reimplemented on CPython.
- **Python**: `Closer.doParallel = True` uses `sg_close_parallel()` (no-arg). Small algebras take the serial SingleClose path (`computationSize < 1e6`).
- **Status**: Sorted universes compared to Java sequential/parallel close
- **Tests**: `seq_*`, `par_*`, `par_matches_seq_*`

---

## org.uacalc.alg.Malcev

Left alone, as specified. `minority_term` / `weak_nu_term` are not part of this
io / terms / lat golden suite.

### alg.Malcev.sd_meet_terms (z3 Java comparison)

- **Java / Rust**: Intermittent mismatch on `z3.ua` in
  `test_sd_meet_terms_with_z3_java_comparison` (`alg::malcev`). Java HashMap
  iteration can change which terms are found; the comparison has been red on
  `jython` since PR #52.
- **Status**: Deferred — flaky Malcev mismatch; `#[ignore]` until the suite is
  reliable. Not a lattice or parity-shim issue. Do not treat this as a Malcev
  logic fix.
- **Tests**: `#[ignore]` on `test_sd_meet_terms_with_z3_java_comparison`
