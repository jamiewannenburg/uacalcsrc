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

### FreeAlgebra AlgebraIO write/read table order

- **Java (live)**: F(1) over cyclic2 has cardinality 2, universe
  `[[0,1],[0,0]]` (generator identity, then `+(x,x)`), terms `x`, `+(x,x)`,
  and `+` table `[1,0,0,1]`. Generation already matches Python (`fa_card`,
  `fa_universe_list`, `fa_get_operation`, `fa_get_terms`).
- **Java (AlgebraIO)**: `writeFreeAlgebra` emits `<freeAlgebra>` with
  coordinate-tuple generators/universe. After read, integer indices follow
  the reconstructed tuple order. For F(1)/C2 that order is the 0↔1 relabel
  of the live table: `[0,1,1,0]` instead of `[1,0,0,1]`. Not an endian flip
  and not “translate to integers first” in the generator; the live FreeAlgebra
  is already integer-indexed in generation order. The permutation happens
  only in write/read.
- **Python**: `org.uacalc.io.AlgebraIO.writeAlgebraFile` calls
  `to_basic_algebra()` (integer operation tables) because `uacalc_lib`
  writers take `PyBasicAlgebra`. Roundtrip therefore keeps the live table
  `[1,0,0,1]`. `src/io/mod.rs` `write_free_algebra` is still a hardcoded
  stub; implementing Java’s FreeAlgebra XML on `Box<dyn SmallAlgebra<i32>>`
  (which has already forgotten the `IntArray` coordinates) is not a clean
  element-order tweak and would knock on every FreeAlgebra IO path.
- **Status**: Strict xfail / roadmap. Live generation is the source of
  truth and already agrees. Do not reorder Python’s live universe to match
  Java’s after-IO labels.
- **Wider roundtrips** (live snap matches in every case; only the read-back
  differs):
  - F(1)/C3: Java after-IO `+` table `[0,1,2,1,2,0,2,0,1]` vs Python live
    `[1,2,0,2,0,1,0,1,2]` (a 0/1/2 relabel; both card 3).
  - F(1)/lat2: Java after-IO card **2** with the base-lattice tables vs
    Python live card **1**.
  - F(1)/ba2: Java after-IO card **2** (the base algebra) vs Python live
    card **4**.
- **Tests**: `fa_roundtrip_write_read`, `fa_roundtrip_c3_f1`,
  `fa_roundtrip_lat2_f1`, `fa_roundtrip_ba2_f1` strict xfail. Live coverage
  `fa_live_*` (C2 F(1..3), C3 F(1..2), lat2 F(1..2), ba2/z3/n5/M3 F(1))
  passes.
- **Owner vs shim**: Owner/library — FreeAlgebra XML write/read. The org
  wrapper’s BasicAlgebra materialization preserves live indices on purpose.

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
