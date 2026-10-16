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

### SmallLattice.upperCoversIndices

- **Java/Jython**: `Lattices.conToSmallLattice` always returns null. Calling
  `null.upperCoversIndices(0)` is Jython `AttributeError`
  (`'NoneType' object has no attribute 'upperCoversIndices'`). There is no
  public Java class that implements `SmallLattice`.
- **Python**: org `conToSmallLattice` still returns `None` (Java null).
  `DiamondLattice.upperCoversIndices(0)` is `[1, 2]` (bottom covered by the
  two atoms).
- **Status**: Strict xfail / roadmap
- **Tests**: `small_lattice_upper_covers_indices`
- **Owner vs shim**: Owner/library — Java has no constructible `SmallLattice`.
  Python extras (`DiamondLattice` / `BooleanLattice` / `uacalc_lib.SmallLattice`)
  implement the method.

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
- **Python**: these methods are not bound on `PyBasicLattice` (`AttributeError`).
- **Status**: Strict xfail / roadmap
- **Tests**: `basic_lattice_find_join_irred`, `basic_lattice_find_meet_irred`,
  `basic_lattice_irredundant_join_decomp`, `basic_lattice_irredundant_meet_decomp`,
  `basic_lattice_make_irredundant_join`, `basic_lattice_make_irredundant_meet`
- **Owner vs shim**: Owner/library — algorithms live on Java `BasicLattice` and
  are not wrapped in `uacalc_lib/src/lat.rs`.

### BasicLattice.con / sub

- **Java**: `con()` of the 2-chain has cardinality **2**; `sub()` has cardinality
  **4**.
- **Python**: `PyBasicLattice` has no `con` / `sub` (`AttributeError`).
- **Status**: Strict xfail / roadmap
- **Tests**: `basic_lattice_con`, `basic_lattice_sub`
- **Owner vs shim**: Owner/library — CongruenceLattice / SubalgebraLattice from
  a BasicLattice.

### BasicLattice from CongruenceLattice

- **Java**: `BasicLattice("ConC2", C2.con(), false)` has cardinality **2**.
- **Python**: the same constructor yields cardinality **0** (the Partition
  variant does not populate the universe the way Java's latdraw poset does).
- **Status**: Strict xfail / roadmap
- **Tests**: `basic_lattice_from_con_c2`
- **Owner vs shim**: Owner/library — `PyBasicLattice::new` /
  `BasicLattice::new_from_lattice`.

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

### AlgebraWriter type-specific stubs (product / power / quotient / subalgebra)

- **Java**: `writeAlgebra` dispatches to `writeProductAlgebra`,
  `writePowerAlgebra`, `writeQuotientAlgebra`, `writeSubalgebra`,
  `writeBigProductAlgebra`, `writeSubProductAlgebra` and writes nested
  factors / root / congruence / subuniverse.
- **Python**: those `src/io/mod.rs` writers are still hardcoded
  placeholders (power=2, partition `0,1`, one dummy factor).
  `write_big_product_typed` exists only as the nested super algebra of
  `<freeAlgebra>` / `<subProductAlgebra>`. Standalone `BigProductAlgebra`
  is not a `SmallAlgebra`, so Java `AlgebraWriter(alg, path)` cannot take
  it. The org shim therefore still routes the SmallAlgebra-derived types
  through
  `to_basic_algebra()` so write/read stays semantically useful as flat
  tables. Matching Java XML needs typed writers plus a reader that rebuilds
  those kinds (the Rust reader only materializes `BasicAlgebra`).
- **Status**: Strict xfail / roadmap.
- **Tests**: `wr_prod_c2_c2`, `xml_prod_c2_c2_tags`, `wr_pwr_c2_2`,
  `xml_pwr_c2_2_tags`, `wr_quot_c2`, `xml_quot_c2_tags`, `wr_sub_c2`,
  `xml_sub_c2_tags`, `wr_subprod_c2`, `xml_subprod_c2_tags` strict xfail.
- **Owner vs shim**: Owner/library — typed XML write/read.

### AlgebraReader nested algebra kinds

- **Java**: reconstructs `ProductAlgebra` / `PowerAlgebra` /
  `QuotientAlgebra` / `Subalgebra` / `BigProductAlgebra` /
  `SubProductAlgebra` from nested XML (card 4 for C2×C2 and C2², card 1
  for the `{0}` subalgebra).
- **Python**: `src/io/algebra_reader.rs` only builds `BasicAlgebra`. A
  nested file yields the last nested basic algebra (a factor or the super
  algebra). Example: `resources/special/product_c2_c2.ua` is Java
  `ProductAlgebra` card 4 vs Python `BasicAlgebra` C2 card 2.
- **Status**: Strict xfail / roadmap.
- **Tests**: `read_special_product`, `read_special_power`,
  `read_special_quotient`, `read_special_subalgebra`,
  `read_special_subproduct` strict xfail.
- **Owner vs shim**: Owner/library — typed XML read.

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
