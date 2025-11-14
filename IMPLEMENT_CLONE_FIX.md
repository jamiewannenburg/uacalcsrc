## Clone/Borrow Recursion Fix – Implementation Plan

### Summary of the Problem
- Operations often close over their parent algebra. Deep-cloning operations (e.g., via `clone_box()`) triggers recursive cloning paths that can re-enter `operations()` on the same or related algebra, causing infinite recursion or hangs.
- Several algebra wrappers (e.g., `Subalgebra`, `SubalgebraLattice`, `QuotientAlgebra`, `Product`, `BigProduct`) use inner-delegation patterns that call back into `operations()` during construction or operation logic, exacerbating recursion and borrowing conflicts.
- Python bindings require clonable objects, which historically pushed us toward deep cloning of trait objects. This conflicts with Rust’s ownership model and creates cycles.

### Core Goals
- Eliminate infinite recursion and borrowing issues when cloning/using operations.
- Preserve Python clonability semantics without deep copies.
- Keep derived algebras efficient (e.g., BigProduct should not build full tables).

### Robust Architecture (Arc/Weak + Reference Access)
1. Store operations as `Vec<Arc<dyn Operation>>` in algebras.
2. Expose non-cloning reference accessors:
   - `operations_ref_arc(&self) -> &[Arc<dyn Operation>]`.
3. Keep legacy `operations() -> Vec<Box<dyn Operation>>` as a shallow wrapper using an `ArcOp` delegator that wraps an `Arc<dyn Operation>` in a `Box<dyn Operation>` without deep cloning.
4. Operations that need a parent algebra hold a `Weak<...>` backref instead of owning it, breaking cycles.
5. Derived algebras build and store their wrapper ops once (as `Arc<dyn Operation>`) and never call their own `operations()` from inside operation logic.
6. Python: expose Arc-backed objects; Python “clone” maps to `Arc::clone` (cheap, no deep copy).

---

## Step 0 – Target Test
First, try to make `test_sg_generation` in `tests/subalgebra_lattice_tests.rs` run without hanging. This serves as the pilot validation of the approach.

## Step 1 – Introduce Arc-based Delegation (Pilot)
1. Add a tiny `ArcOp` delegator type (e.g., in `src/alg/op/operation.rs`) that wraps `Arc<dyn Operation>` and implements `Operation` by delegating every method. Its `clone_box()` returns a new `ArcOp` with `Arc::clone` (shallow clone).
2. In `GeneralAlgebra<T>`, add `operations_ref_arc(&self) -> &[Arc<dyn Operation>]` and migrate internal operation storage to `Vec<Arc<dyn Operation>>` (you can keep both vectors briefly during migration if needed).
3. Change `GeneralAlgebra::operations()` to return boxed `ArcOp` wrappers built from `operations_ref_arc()` (no deep clone). This eliminates recursion originating from deep cloning.

## Step 2 – Break Backref Cycles in One Derived Op
1. Pick the restricted operation used by `Subalgebra`/`SubalgebraLattice` and change its parent reference to `Weak<...>` (e.g., a small `SubalgebraCore<T>` that exposes only what the op needs).
2. Ensure its `int_value_at` (and friends) use reference access:
   - Get the super algebra via `Weak::upgrade()`.
   - Use `operations_ref_arc()` to consult needed operations.
   - Do not call any `operations()` inside operation methods.
3. Implement `clone_box()` for the restricted op to shallow copy the `Weak` and any `Arc` data; never deep clone the parent.

## Step 3 – Switch One Hot Path in SubalgebraLattice
1. Replace any `let ops = alg.operations();` in the `SubalgebraLattice` code path that powers `sg()` with:
   - `let ops_ref = alg.operations_ref_arc();`
   - Wrap with `ArcOp` only when a boxed `Operation` is strictly required.
2. Ensure nothing in this path re-enters `operations()` from within `Operation` logic.

## Step 4 – Run the Pilot Test
1. Unignore `test_sg_generation` in `tests/subalgebra_lattice_tests.rs`.
2. Run just this test module to validate there’s no hang:
   - `cargo test tests::subalgebra_lattice_tests::test_sg_generation -- --nocapture`
3. If it still hangs, search for any remaining calls to `operations()` within operation code and replace with reference-based access. Also validate any backrefs are `Weak`, not owning pointers.

## Step 5 – Roll Out Incrementally
1. Convert other derived algebras (Quotient, Reduct, Product, BigProduct) to the same pattern:
   - Store wrapper ops as `Arc<dyn Operation>`.
   - Use `Weak` backrefs where an op needs a parent.
   - Keep all internal lookups via `operations_ref_arc()`.
2. Ensure BigProduct operations remain lazy (never build full tables). Compute via references to component ops only.
3. Python bindings: where operations are returned, provide views backed by the existing `Arc` list. Python “copies” should map to shallow clones.

## Step 6 – Cleanups and Optional Deletions
1. Where feasible, remove or minimize `clone_box()` implementations, keeping only the delegating one for `ArcOp` and any special cases. Avoid deep cloning of algebras/ops.
2. Remove legacy code paths that built operation maps by deep clone; rebuild maps from `Arc` references if needed.

## Acceptance Checklist
- `tests/subalgebra_lattice_tests::test_sg_generation` no longer hangs.
- No infinite recursion observed in any derived algebra construction or op usage.
- Python tests still pass; Python-visible clones are cheap `Arc` clones.
- BigProduct remains lazy and does not materialize full op tables.
- No borrow checker errors related to incrementors (keep using `get_current()`).

## Notes
- Pool/SingleClose are not the root cause of the recursion; they impact performance and borrow ergonomics but are orthogonal to this fix.
- Prefer trait layering and reference APIs over inner-delegation that re-enters `operations()`.


