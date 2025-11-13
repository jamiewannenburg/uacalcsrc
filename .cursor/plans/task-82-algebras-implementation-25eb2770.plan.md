<!-- 25eb2770-1563-4992-9d85-8ad5634fa671 a246db26-b2b1-4334-9db3-c75c40bbf022 -->
# Task 82: Algebras Implementation Plan

## Phase 1: Update Task Documentation

1. **Update dependencies section** in `tasks/Task 82 - Algebras.md`:

- Mark all completed dependencies as ✅ COMPLETED
- Remove duplicates and consolidate the dependency list
- Update status to reflect that all critical dependencies are complete

2. **Add public methods list** at the end of the task file:

- Extract all 23 public static methods from `org/uacalc/alg/Algebras.java`
- List them with signatures and brief descriptions
- Format as a checklist for tracking implementation progress

## Phase 2: Implement isEndomorphism

3. **Create Rust module** `src/alg/algebras.rs`:

- Create module with `is_endomorphism` function
- Signature: `pub fn is_endomorphism(endo: &dyn Operation, alg: &dyn SmallAlgebra) -> Result<bool, String>`
- Implementation: Check if `endo.arity() == 1`, then iterate through all operations in `alg` and use `commutes_unary` to verify commutation
- Handle errors properly (return Err if endo is not unary)

4. **Add module to** `src/alg/mod.rs`:

- Add `pub mod algebras;` declaration
- Re-export the function if needed

5. **Create Python binding** in `uacalc_lib/src/alg/mod.rs`:

- Add `#[pyfunction]` wrapper for `is_endomorphism`
- Handle conversion between Python and Rust types
- Register function in `register_alg_module`

6. **Create Java wrapper** `java_wrapper/src/alg/AlgebrasWrapper.java`:

- Extend `WrapperBase`
- Add `isEndomorphism` command handler
- Parse arguments (operation and algebra)
- Call Java `Algebras.isEndomorphism` and output JSON result

7. **Create Rust test** in `src/alg/algebras.rs`:

- Test with simple algebra and endomorphism
- Test with non-endomorphism operation
- Test error case (non-unary operation)
- Use timeout utilities from `tests/common/mod.rs`

8. **Create Python test**:

- Test the Python binding works correctly
- Create comparison test that calls both Python binding and Java wrapper for `isEndomorphism`
- Compare results to ensure they match
- Test with various algebras and endomorphisms
- Test error cases (non-unary operations)
- Use test utilities from `tests/common/mod.rs` for Java wrapper execution
- Place test in appropriate Python test file (e.g., `python/uacalc/tests/` or similar)

## Phase 3: Compilation and Testing

9. **Compile Rust code**:

- Ensure `cargo build` succeeds
- Fix any compilation errors

10. **Compile Java wrapper**:

- Run `ant compile-wrappers`
- Fix any compilation errors

11. **Compile Python bindings**:

- Activate venv: `source venv/bin/activate` (or equivalent)
- Run `maturin develop` (or `maturin build`)
- Suppress warnings with `RUSTFLAGS="-A warnings"` if needed

12. **Run tests**:

- Run Rust tests: `cargo test algebras`
- Verify all tests pass

13. **Run python tests:**

- Activate venv: `source venv/bin/activate` (or equivalent)
- Run python tests: `pytest python/uacalc/tests/test_algebras.py`
- Verify all tests pass

## Files to Modify/Create

- `tasks/Task 82 - Algebras.md` - Update dependencies and add method list
- `src/alg/algebras.rs` - NEW: Rust implementation
- `src/alg/mod.rs` - Add module declaration
- `uacalc_lib/src/alg/mod.rs` - Add Python binding
- `java_wrapper/src/alg/AlgebrasWrapper.java` - NEW: Java wrapper
- Tests will be in `src/alg/algebras.rs` (Rust tests)
- Python tests will be in `python/uacalc/tests/test_algebras.py` (Python tests)

## Implementation Notes

- `isEndomorphism` is chosen because it's simple and has all dependencies available
- Uses existing `commutes_unary` from `src/alg/op/operations.rs`
- Follows existing patterns for Python bindings and Java wrappers
- Error handling: Return `Result<bool, String>` for proper error propagation