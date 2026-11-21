# Rust gaps

Parity tests that fail because `uacalc` / `uacalc_lib` is missing logic are marked `pytest.mark.xfail(..., strict=True)` with a reason that starts with `Rust gap:`. They are kept separate from Java-bug / environment xfails (see `tools/check_xfail_prefixes.py`).

Gaps visible only in the Rust crate (the `org.uacalc` Python shim already matches Java) are listed as `#[ignore = "Rust gap: …"]` or `#[ignore = "Known Java bug: …"]` tests in `tests/rust_gaps.rs` and a few in-tree tests. `cargo test --workspace` stays green; `cargo test --test rust_gaps -- --ignored` is the Rust watch list.

## Closed in #104–#106

| Area | Verification |
| --- | --- |
| `CongruenceLattice` type theory (`type_ji`, `type_interval`, `type_set`, `get_type_finder`, `find_type_from_subtrace`) | `tests/rust_gaps.rs` (`type_*_not_stub`, `get_type_finder_not_stub`); `tests/parity/test_rust_gaps.py` (`test_rust_gap_type_*_bound`) |
| `CongruenceLattice.coatoms` | Raises `UnsupportedOperationException`, matching Java; `con_coatoms_not_none` in `rust_gaps.rs` |
| `SubProductAlgebra.projection_kernel` | `sub_product_projection_kernel` in `rust_gaps.rs`; `test_rust_gap_sub_product_projection_kernel` |
| `QuotientOperation.value_at_arrays` | `quotient_value_at_arrays` in `rust_gaps.rs`; `test_rust_gap_quotient_value_at_arrays` |
| `TermOperationImp.make_table` | `test_rust_gap_term_operation_imp_make_table` |
| `Malcev` idempotent helpers on `uacalc_lib.alg` | Direct-call tests in `tests/parity/test_rust_gaps.py` (`test_type_set_idempotent_cyclic2_is_exactly_affine`, etc.) |
| `MatrixPowerAlgebra` con/sub, universe list, bare `elementIndex` (#104) | Parity alg `untested_wraps` cases (xfails removed) |
| `ReductAlgebra` con/sub, `getUniverseOrder`, `convertToDefaultValueOps` (#104) | Same |
| `FiniteField` empty `GeneralAlgebra` stubs (#104) | Example `untested_wraps` (xfails removed) |
| `BigProductAlgebra.is_similar_to` / `update_similarity_type` | `big_product_*` tests in `rust_gaps.rs`; `test_rust_gap_big_product_*` |
| `BasicSet.union` (#106) | `tests/parity/sublat` strict xfails with `Known Java bug:` |

## Dropped from the Oct 21 audit (already match Java on the Python surface)

| Item | Why dropped |
| --- | --- |
| `CongruenceLattice.typeJI` / `typeSet` / `getTypeFinder` via `org.uacalc` | CPython shim uses `TypeFinder`; Rust methods call it too. |
| `CongruenceLattice.coatoms` via `org.uacalc` | Shim raises `UnsupportedOperationException`, matching Java. |
| `BigProductAlgebra.projectionKernel` | Java returns null; `uacalc_lib` returns `None`. Rust core returns `Err` until implemented (not Python-visible). |
| `SubalgebraLattice.atoms` / `coatoms` / `meetIrreducibles` via `org.uacalc` | Shim returns `None`, matching Java TODOs. |
| `SubalgebraLattice.isSmallerThan` via `org.uacalc` | Shim uses `cardinality()`, matching Java’s observable result. |
| `SubalgebraLattice.setMonitor` via `org.uacalc` | Shim stores the monitor. |
| `SubProductElement.getAlgebra` via Python | Bindings do not hit the Rust `Element::get_algebra` panic. |
| `BigProductAlgebra.isSimilarTo` via `org.uacalc` | Shim falls back to similarity-type equality. |

## Current gaps

### SubalgebraLattice (Rust crate only)

- **atoms / coatoms:** Java TODOs return null — parity xfails labelled `Known Java bug:`; ignored tests `sublat_atoms_not_none`, `sublat_coatoms_not_none`.
- **`is_smaller_than`:** Returns false when universe is unset (Java triggers `makeUniverse` as a side effect). **Tests:** `sublat_is_smaller_than_computes_universe`.
- **`set_monitor`:** Rust no-op. **Tests:** `sublat_set_monitor_stores`.
- **`make_meet_irreducibles`:** Empty stub list. **Tests:** `sublat_meet_irreducibles_not_empty_stub`.

### BigProductAlgebra.universe (Python)

Java does not override `universe()` (null field). Enumerating C2² would diverge. **Tests:** `test_rust_gap_big_product_universe` (`Known Java bug:`).

### SubProductElement.get_algebra (Rust crate)

- **Rust:** `Element::get_algebra` panics; Python bindings avoid this path.
- **Tests:** `sub_product_element_get_algebra`.

### MatrixPowerAlgebra.elementIndex (Java bug)

Java searches `universe()` for `IntArray` but cartesian-product elements are `ArrayList`s, so every lookup returns -1. Rust returns the Horner index. **Tests:** `src/alg/matrix_power_algebra_tests.rs` (`Known Java bug:` ignore).

### SimpleList cons sharing

- **Tests:** `src/util/simple_list.rs` `test_cons_memory_efficiency`.

### Malcev `pixley_term` distributivity guard

- **Tests:** `pixley_term_uses_distributivity_guard`.

### MemoryMonitor placeholder

- **Tests:** `memory_monitor_reads_real_rss`.

### Closer.doOneStagePartialClosure parallel worker

Parallel worker body not bound on Python shim.

### AlgebraFromMinimalSets operation table from a basic algebra

Java returns null for minimal-sets operation naming when cloning from `BasicAlgebra`. **Tests:** `jython_comparison/scripts/algebra_from_minimal_sets_smoke.py`.

### MatrixPowerAlgebra.getElement typing

`PyIntArray` from `get_element` is not iterable like Java `IntArray`. **Tests:** `jython_comparison/scripts/matrix_power_algebra_smoke.py`.

### SubProductAlgebra.getElementFromTerm (Java bug)

`findTerms=false` leaves `terms` null; Java NPEs on `terms.length`. Python returns null like `getTerm`. **Tests:** parity `inh_sp_get_elem_term`.

### Projective plane → ternary ring

Java `readProjectivePlane` returns null after parse. Rust keeps “not yet implemented” error. **Tests:** `test_rust_gap_read_projective_plane` (`Known Java bug:`).

### Malcev.typeSetIdempotent (Java bug)

Java `types1.add(2)` instead of `types2.add(2)` on some algebras. Documented in `tests/parity/KNOWN_DIFFERENCES.md` and malcev parity xfails.

## Platform notes (not Rust-gap xfails)

On Windows, `malcev_term_rand_bin` and `hagemann_mitschke_rand_bin` exceed the 120s search timeout Linux CI meets. Platform xfails use prefix `Environment:`.