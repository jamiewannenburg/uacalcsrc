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
| `CongruenceLattice.typeJI` / `typeSet` / `getTypeFinder` via `org.uacalc` | The CPython shim computes these with `TypeFinder`. The Rust inherent methods stay stubs (see below). |
| `CongruenceLattice.coatoms` via `org.uacalc` | Shim raises `UnsupportedOperationException`, matching Java. |
| `BigProductAlgebra.projectionKernel` | Java also returns null; `uacalc_lib` returns `None`. |
| `SubalgebraLattice.atoms` / `coatoms` / `meetIrreducibles` via `org.uacalc` | Shim returns `None`, matching Java's empty stubs. |
| `SubalgebraLattice.isSmallerThan` via `org.uacalc` | Shim uses `cardinality()`, matching Java's observable result. |
| `SubalgebraLattice.setMonitor` via `org.uacalc` | Shim stores the monitor; Java `ProgressReport` is out of scope. |
| `SubProductElement.getAlgebra` via Python | `uacalc_lib` stores the algebra as a `PyObject` and does not hit the Rust `Element::get_algebra` panic. |
| `BigProductAlgebra.isSimilarTo` via `org.uacalc` | Shim falls back to similarity-type equality when `is_similar_to` is unbound. |

## Current gaps

### CongruenceLattice type theory stubs

- **Rust:** `src/alg/conlat/congruence_lattice.rs` `type_ji` (always 0), `type_interval` (always 0), `type_set` (`Err`), `get_type_finder` (`Err`). Not bound on `uacalc_lib` `PyCongruenceLattice`.
- **Missing:** Wire `TypeFinder` into the lattice (the org shim already does this in Python).
- **Tests:** `tests/parity/test_rust_gaps.py` `test_rust_gap_type_ji_bound`, `test_rust_gap_type_interval_bound`, `test_rust_gap_type_set_bound`, `test_rust_gap_get_type_finder_bound`; ignored `tests/rust_gaps.rs` `type_ji_not_stub`, `type_interval_not_stub`, `type_set_not_stub`, `get_type_finder_not_stub`.

### CongruenceLattice.coatoms

- **Rust:** `Lattice::coatoms` in `src/alg/conlat/congruence_lattice.rs` returns `None`.
- **Missing:** Either throw like Java (`UnsupportedOperationException`) or compute coatoms.
- **Tests:** `test_rust_gap_con_coatoms_bound`; ignored `con_coatoms_not_none`.

### commutator2 swallows errors

- **Rust:** `src/alg/conlat/congruence_lattice.rs` `commutator2` returns `zero()` on `Err`.
- **Missing:** Surface the internal error (or match Java's exception) instead of a silent zero congruence.
- **Tests:** ignored `commutator2_does_not_swallow_errors`. (Happy-path `commutator2(zero, one)` already matches Java in `python/uacalc/tests/test_congruence_lattice.py`.)

### SubalgebraLattice atoms / coatoms / is_smaller_than / set_monitor / meet irreducibles

- **Rust:** `src/alg/sublat/mod.rs` `atoms`/`coatoms` `None`; `is_smaller_than` false when universe is unset; `set_monitor` no-op; `make_meet_irreducibles` empty vec.
- **Missing:** Compute atoms/coatoms; `makeUniverse` as a side effect of `is_smaller_than`; store the monitor; implement meet irreducibles.
- **Tests:** `test_rust_gap_sublat_atoms`, `test_rust_gap_sublat_coatoms`; ignored `sublat_atoms_not_none`, `sublat_coatoms_not_none`, `sublat_is_smaller_than_computes_universe`, `sublat_set_monitor_stores`, `sublat_meet_irreducibles_not_empty_stub`.

### BigProductAlgebra universe / is_similar_to / update_similarity_type / projection_kernel

- **Rust:** `src/alg/big_product_algebra.rs` `universe` empty iterator; `is_similar_to` always false; `update_similarity_type` no-op; `projection_kernel` `Err`.
- **Missing:** Enumerate small products; compare similarity types; fill symbols from operations; compute the projection kernel (Java's public method is a null stub, but the Rust `Result` path is still unimplemented).
- **Tests:** `test_rust_gap_big_product_universe`, `test_rust_gap_big_product_is_similar_to`, `test_rust_gap_big_product_update_similarity_type`; ignored `big_product_universe_not_empty`, `big_product_is_similar_to_self`, `big_product_update_similarity_type`, `big_product_projection_kernel`.

### SubProductAlgebra projection_kernel

- **Rust:** `src/alg/sub_product_algebra.rs` has no `projection_kernel`; `uacalc_lib/src/alg/sub_product_algebra.rs` does not expose `projection_kernel` / `projectionKernel` on `PySubProductAlgebra` (unlike `ProductAlgebra` / `BigProductAlgebra`, which return Java-null `None`).
- **Missing:** Build the coordinate agreement partition in Rust and bind it on `PySubProductAlgebra` (Java implements this on `SubProductAlgebra`; parity golden `sp_proj_kern`).
- **Tests:** `tests/parity/test_rust_gaps.py` `test_rust_gap_sub_product_projection_kernel` (strict xfail on the `uacalc_lib` binding); ignored `tests/rust_gaps.rs` `sub_product_projection_kernel`. The `org.uacalc` shim may compute the partition in Python until Rust is filled in.

### SmallLattice is_similar_to always true

- **Rust:** `src/lat/small_lattice.rs` `DiamondLattice` / `BooleanLattice` `is_similar_to` always `true`.
- **Missing:** Compare similarity types (as `BasicLattice` does).
- **Tests:** ignored `diamond_lattice_is_similar_to_checks_type`.

### meetIrreducibles on lattices built from a congruence lattice

- **Rust:** `uacalc_lib` `BasicLattice.meet_irreducibles` only handles the `Int32` inner variant; lattices built from `CongruenceLattice` take the other arm and error. `src/lat/basic_lattice.rs` `meet_irreducibles` itself is implemented for `BasicLattice<T>`, but the Python binding does not expose the Partition-typed lattice.
- **Missing:** Bind `meet_irreducibles` for the congruence-lattice inner.
- **Tests:** Covered by `test_rust_gap_sublat_atoms` / coatoms style xfails once a Con-backed `BasicLattice` is used; until then the Partition inner is Rust-only (see ignored sublat meet-irreducible stub). Existing `python/uacalc/tests/test_small_lattice.py` covers operation-built lattices, which work.

### QuotientOperation.value_at_arrays

- **Rust:** `src/alg/quotient_algebra.rs` `value_at_arrays` returns `Err("value_at_arrays not implemented for QuotientOperation")`.
- **Missing:** Evaluate the super-operation on representative tuples.
- **Tests:** `test_rust_gap_quotient_value_at_arrays`; ignored `quotient_value_at_arrays`.

### TermOperationImp cannot build a value table

- **Rust:** `src/alg/op/term_operation_imp.rs` `make_table` / `create_value_table` always `Err` (immutable interpretation). Not bound on `PyTermOperationImp`.
- **Missing:** Build and cache a table from `int_value_at`, matching Java `getTable(true)`.
- **Tests:** `test_rust_gap_term_operation_imp_make_table`.

### Projective plane to ternary ring

- **Rust:** `src/io/algebra_io.rs` `read_projective_plane_from_reader` returns `Err("Projective plane to ternary ring conversion not yet implemented")`.
- **Missing:** Construct the ternary ring algebra after parsing the plane.
- **Tests:** `test_rust_gap_read_projective_plane`. (`python/uacalc/tests/test_algebra_io.py` currently asserts the error string; that assertion must flip when this is implemented.)

### SubProductElement.get_algebra panic

- **Rust:** `src/element/sub_product_element.rs` `Element::get_algebra` panics. Python bindings do not call this path.
- **Missing:** Return the algebra without the lifetime workaround panic.
- **Tests:** ignored `sub_product_element_get_algebra`.

### MatrixPowerAlgebra.elementIndex (ignored Rust test)

- **Rust:** `src/alg/matrix_power_algebra_tests.rs` `test_element_index` — Rust returns 0, Java -1.
- **Missing:** Match Java `elementIndex` universe comparison (or document a Java bug if Java is wrong).
- **Tests:** ignored `test_element_index` (`Rust gap:` reason).

### SimpleList cons sharing (ignored Rust test)

- **Rust:** `src/util/simple_list.rs` `test_cons_memory_efficiency` panics `left:0 right:1`.
- **Missing:** Sharing identity of `rest().rest()` after two `cons` from the same base.
- **Tests:** ignored `test_cons_memory_efficiency` (`Rust gap:` reason).

### Malcev pixley_term distributivity TODO

- **Rust:** `src/alg/malcev.rs` `pixley_term` skips `is_congruence_dist_idempotent` for idempotent algebras.
- **Missing:** Fail fast with `Ok(None)` on idempotent non-CD algebras instead of enumerating F(2)^3.
- **Tests:** ignored `pixley_term_uses_distributivity_guard`.

### Python-only Malcev idempotent methods not ported to Rust

- **Rust:** Not registered in `uacalc_lib/src/alg/malcev.rs`. The org shim reimplements them in `python/org/uacalc/alg/_jython_compat.py`.
- **Missing:** `sd_idempotent`, `cp_idempotent`, `cube_term_blocker_idempotent`, `type_set_idempotent`, `types_in_sof_a_idempotent`, `types_in_sof_a_strictly_simple_idempotent`, `types_in_sof_a_i_robust_decompdempotent`, `omitted_ideal_idempotent`.
- **Tests:** `test_rust_gap_sd_idempotent`, `test_rust_gap_cp_idempotent`, `test_rust_gap_cube_term_blocker_idempotent`, `test_rust_gap_type_set_idempotent`, `test_rust_gap_types_in_sof_a_idempotent`, `test_rust_gap_types_in_sof_a_strictly_simple_idempotent`, `test_rust_gap_types_in_sof_a_i_robust_decomp_idempotent`, `test_rust_gap_omitted_ideal_idempotent`.

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
- **Tests:** `jython_comparison/scripts/matrix_power_algebra_smoke.py` (`getElement0`).

## Platform notes (not Rust-gap xfails)

On Windows, `malcev_term_rand_bin` and `hagemann_mitschke_rand_bin`
(size-3 magma seed 11, F(2)=409) exceed the 120s search timeout that
Linux CI meets. They are Windows-only xfails, not `Rust gap:` entries.
