# Rust gaps

Parity tests that fail because `uacalc` / `uacalc_lib` is missing logic
(stubs, unbound parallel workers, incomplete searches) are marked
`pytest.mark.xfail(..., strict=True)` with a reason that **starts with**
`Rust gap:`. They are kept separate from Java-bug / Java-limitation xfails.

Gaps that are only visible inside the Rust crate (the `org.uacalc` Python
shim already matches Java) are `#[ignore = "Rust gap: ..."]` tests in
`tests/rust_gaps.rs` (and two in-tree ignored tests). `cargo test` stays
green; `cargo test --test rust_gaps -- --ignored` is the watch list.

This file is the maintained list: Rust location, what is missing, and the
test(s) that surface it.

## Dropped from the Oct 21 audit (already match Java on the Python surface)

| Item | Why dropped |
| --- | --- |
| `CongruenceLattice.typeJI` / `typeSet` / `getTypeFinder` via `org.uacalc` | The CPython shim computes these with its TypeFinder. The Rust lattice methods now call `TypeFinder` as well. |
| `CongruenceLattice.coatoms` via `org.uacalc` | Shim raises `UnsupportedOperationException`, matching Java. |
| `BigProductAlgebra.projectionKernel` | Java also returns null; `uacalc_lib` returns `None`. |
| `SubalgebraLattice.atoms` / `coatoms` / `meetIrreducibles` via `org.uacalc` | Shim returns `None`, matching Java's empty stubs. |
| `SubalgebraLattice.isSmallerThan` via `org.uacalc` | Shim uses `cardinality()`, matching Java's observable result. |
| `SubalgebraLattice.setMonitor` via `org.uacalc` | Shim stores the monitor; Java `ProgressReport` is out of scope. |
| `SubProductElement.getAlgebra` via Python | `uacalc_lib` stores the algebra as a `PyObject` and does not hit the Rust `Element::get_algebra` panic. |
| `BigProductAlgebra.isSimilarTo` via `org.uacalc` | Shim falls back to similarity-type equality when `is_similar_to` is unbound. |

## Current gaps

### CongruenceLattice type theory

Closed. `type_ji`, `type_interval` (`type(beta, alpha)` via `find_join_irred(alpha, beta)`), `type_set`, and `get_type_finder` call `TypeFinder`. `find_type_from_subtrace` writes the typed subtrace, including its matrix universe, back into the join-irreducible cache, matching Java `TypeFinder.findType(Subtrace)`. Bound on `PyCongruenceLattice`. Checkpoints run once per join irreducible in `type_set`.

### CongruenceLattice.coatoms

`coatoms()` is bound and raises `UnsupportedOperationException: Not implemented yet.`, matching Java. `Lattice::coatoms` stays `None` so other lattices are unchanged.

### commutator2 swallows errors

- **Rust:** `src/alg/conlat/congruence_lattice.rs` `commutator2` returns `zero()` on `Err`.
- **Missing:** Surface the internal error (or match Java's exception) instead of a silent zero congruence.
- **Tests:** ignored `commutator2_does_not_swallow_errors`. (Happy-path `commutator2(zero, one)` already matches Java in `python/uacalc/tests/test_congruence_lattice.py`.)

### SubalgebraLattice atoms / coatoms

`atoms()` and `coatoms()` still return null, matching the Java TODOs. Strict xfails `test_rust_gap_sublat_atoms` and `test_rust_gap_sublat_coatoms` are labelled `Known Java bug:`. The other SubalgebraLattice gaps (`is_smaller_than`, `set_monitor`, meet irreducibles) are unchanged; their ignored tests remain in `tests/rust_gaps.rs`.

### BigProductAlgebra universe

`universe()` stays an empty iterator. Java `BigProductAlgebra` does not override `universe()`, and `GeneralAlgebra.universe()` returns the unset field (null). Enumerating cyclic2^2 would diverge. Strict xfail `test_rust_gap_big_product_universe` is labelled `Known Java bug:`. `projectionKernel` on `BigProductAlgebra` is still Java's null stub.

`is_similar_to` compares similarity types (Java `SimilarityType.equals`, order-insensitive). `update_similarity_type` rebuilds the type from `operations()` symbols.

### SubProductAlgebra projection_kernel

Closed. `projection_kernel(k)` builds the partition of elements that agree on coordinate `k` (`Partition::zero`, then `join_blocks`), with a checkpoint on each inner pair. A negative or out-of-range coordinate is an error. Bound as `projection_kernel` / `projectionKernel`.

### SmallLattice is_similar_to always true

- **Rust:** `src/lat/small_lattice.rs` `DiamondLattice` / `BooleanLattice` `is_similar_to` always `true`.
- **Missing:** Compare similarity types (as `BasicLattice` does).
- **Tests:** ignored `diamond_lattice_is_similar_to_checks_type`.

### meetIrreducibles on lattices built from a congruence lattice

- **Rust:** `uacalc_lib` `BasicLattice.meet_irreducibles` only handles the `Int32` inner variant; lattices built from `CongruenceLattice` take the other arm and error. `src/lat/basic_lattice.rs` `meet_irreducibles` itself is implemented for `BasicLattice<T>`, but the Python binding does not expose the Partition-typed lattice.
- **Missing:** Bind `meet_irreducibles` for the congruence-lattice inner.
- **Tests:** Covered by `test_rust_gap_sublat_atoms` / coatoms style xfails once a Con-backed `BasicLattice` is used; until then the Partition inner is Rust-only (see ignored sublat meet-irreducible stub). Existing `python/uacalc/tests/test_small_lattice.py` covers operation-built lattices, which work.

### QuotientOperation.value_at_arrays

Closed. Column-wise evaluation calls `int_value_at` (representatives, super-operation, congruence representative, binary search), with a checkpoint per column. Java `AbstractOperation.valueAt(int[][])` throws; the crate's `value_at_arrays` is the vectorized `intValueAt` path the gap asked for.

### TermOperationImp.make_table

Closed. `make_table` keeps an existing interpretation table or fills a Horner cache from `int_value_at`, with a checkpoint per row. Bound as `make_table` / `makeTable`.

### Projective plane to ternary ring

`AlgebraIO.readProjectivePlane` parses the file and returns null. Rust still returns `Projective plane to ternary ring conversion not yet implemented`, which `python/uacalc/tests/test_algebra_io.py` locks. Strict xfail `test_rust_gap_read_projective_plane` is labelled `Known Java bug:`. Do not invent a ternary ring.

### SubProductElement.get_algebra panic

- **Rust:** `src/element/sub_product_element.rs` `Element::get_algebra` panics. Python bindings do not call this path.
- **Missing:** Return the algebra without the lifetime workaround panic.
- **Tests:** ignored `sub_product_element_get_algebra`.

### MatrixPowerAlgebra.elementIndex of a real vector (ignored Rust test)

- **Java bug:** `PowerAlgebra.elementIndex` searches `universe()` for an `IntArray`, but `MatrixPowerAlgebra` stores `ProductAlgebra.makeCartesianProduct`, whose iterator yields `ArrayList`s. The `instanceof IntArray` test never hits, so every lookup, including `[0, 0]`, returns -1. A bare `int` also returns -1, and that path is matched (`inh_mp_elem_idx`).
- **Rust:** `element_index(&[0, 0])` returns the Horner index 0.
- **Tests:** ignored `test_element_index` (`Known Java bug:` reason). Do not change Rust to return -1.

### SimpleList cons sharing (ignored Rust test)

- **Rust:** `src/util/simple_list.rs` `test_cons_memory_efficiency` panics `left:0 right:1`.
- **Missing:** Sharing identity of `rest().rest()` after two `cons` from the same base.
- **Tests:** ignored `test_cons_memory_efficiency` (`Rust gap:` reason).

### Malcev pixley_term distributivity TODO

- **Rust:** `src/alg/malcev.rs` `pixley_term` skips `is_congruence_dist_idempotent` for idempotent algebras.
- **Missing:** Fail fast with `Ok(None)` on idempotent non-CD algebras instead of enumerating F(2)^3.
- **Tests:** ignored `pixley_term_uses_distributivity_guard`.

### Malcev idempotent methods

Closed on `uacalc_lib.alg` and delegated from `org.uacalc.alg.Malcev` when the Rust function is present: `sd_idempotent`, `cp_idempotent`, `cube_term_blocker_idempotent`, `type_set_idempotent`, `types_in_sof_a_idempotent`, `types_in_sof_a_strictly_simple_idempotent`, `types_in_sof_a_i_robust_decompdempotent`, `omitted_ideal_idempotent`.

Outer loops call `resource::checkpoint`. `type_set_idempotent` uses `types1 = {1}` and `types2 = {2}`. Java's `types1.add(2)` (the line after `types2` is created) leaves `types2` empty; that divergence is a known Java bug, recorded in `tests/parity/KNOWN_DIFFERENCES.md`. On `cyclic2.ua` (`typ(A) = {2}`, no type 1 in `HS(A)`) Rust returns `[[2], [2]]` and Java returns `[[2], [2, 3]]`. Java `System.out.println` traces in the cube-term and robust-decomposition methods are not printed. The method name `typesInSofAIRobustDecompdempotent` keeps Java's spelling.

### MemoryMonitor placeholder

- **Rust:** `src/common.rs` `MemoryMonitor::current_memory_usage` returns `pid as usize * 1024`.
- **Missing:** Read real RSS (or equivalent).
- **Tests:** ignored `memory_monitor_reads_real_rss`.

### Closer.doOneStagePartialClosure parallel worker

- **Rust:** `src/alg/closer.rs` / Python shim `python/org/uacalc/alg/_jython_compat.py` — the parallel worker body is not bound. Success-path fixtures still hit Java's empty-`rawList` / null-`termMap` exceptions first.
- **Missing:** Bind the worker. No `Rust gap:` xfail yet (unchanged from leftover wraps).

### AlgebraFromMinimalSets operation table from a basic algebra

- **Rust:** `uacalc_lib` `AlgebraFromMinimalSets` built from `cyclic2.ua` exposes a unary `s` operation via `get_operation`; Java returns null for `OperationSymbol("s", 1)`.
- **Missing:** Match Java minimal-sets operation naming when cloning from a `BasicAlgebra`.
- **Tests:** `jython_comparison/scripts/algebra_from_minimal_sets_smoke.py` (`op_s`).

### MatrixPowerAlgebra.getElement typing

- **Rust:** `uacalc_lib` `PyMatrixPowerAlgebra.get_element` returns a `PyIntArray` that CPython scripts cannot iterate like Java `IntArray`.
- **Missing:** Expose Java-compatible `getElement` / universe element handles for matrix-power algebras.
- **Tests:** `jython_comparison/scripts/matrix_power_algebra_smoke.py` (`getElement0`, `op_plus`).

### SubProductAlgebra.getElementFromTerm on a term-less constructor

- **Java bug:** `SubProductAlgebra(name, product, gens)` calls the overload with `findTerms=false`, so `terms` stays null. `getTerm` returns null. `getElementFromTerm` then reads `terms.length` and throws `NullPointerException`.
- **Rust / Python:** return null, the same result `getTerm` already documents. Do not copy the NPE.
- **Tests:** `inh_sp_get_elem_term` in `tests/parity/alg/test_cases/untested_wraps_cases.py` (`Known Java bug:` strict xfail).

### UnaryTermsMonoid universe / element_index

- **Rust:** `get_universe_list` on `UnaryTermsMonoid` exposes term-like universe entries; `element_index` binding expects `IntArray`.
- **Missing:** Match Java universe element type for indexing.
- **Tests:** `python/uacalc/tests/test_unary_terms_monoid.py` `test_unary_terms_monoid_universe` (strict xfail).

### Operations.make_composition_op / make_jonsson_operations_from_nuf

- **Rust:** `src/alg/op/operations.rs` `make_composition_op` builds tables with out-of-range indices for `(n,pow)=(3,2)`; `make_jonsson_operations_from_nuf` hits negative capacity during NUF reduct expansion.
- **Missing:** Match Java `Operations.makeCompositionOp` / `makeJonssonOperationsFromNUF` encodings.
- **Tests:** `python/uacalc/tests/test_operations.py` `test_make_composition_op`, `test_make_jonsson_operations_from_nuf` (strict xfails).

## Platform notes (not Rust-gap xfails)

On Windows, `malcev_term_rand_bin` and `hagemann_mitschke_rand_bin`
(size-3 magma seed 11, F(2)=409) exceed the 120s search timeout that
Linux CI meets. They are Windows-only xfails, not `Rust gap:` entries.
