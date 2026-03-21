# Analysis: Performance Optimizations

## 1. Unnecessary Synchronization in `BasicAlgebra`
`BasicAlgebra` uses `RwLock<Option<T>>` for caching its universe list and order.

### Problem:
A `RwLock` has overhead for every read/write. If the algebra is immutable after its initial creation, this overhead is wasted.

### Suggestion: `OnceCell`
Use `once_cell::sync::OnceCell` (or the now-standard `std::sync::OnceLock`). This is optimized for single initialization.

```rust
pub struct BasicAlgebra<T> {
    universe_list: OnceLock<Vec<T>>,
    universe_order: OnceLock<HashMap<T, usize>>,
    // ...
}

fn get_element(&self, k: usize) -> Option<T> {
    self.universe_list.get_or_init(|| {
        self.base.universe.iter().cloned().collect()
    }).get(k).cloned()
}
```

---

## 2. Expensive `clone_box()` for Algebras
The `clone_box()` implementation for `BasicAlgebra` creates a whole new algebra and recomputes all its operation tables.

### Problem:
If operation tables are large (e.g., 1 million entries), cloning becomes very slow.

### Suggestion: `Arc` Sharing
Operation tables should be wrapped in `Arc<Vec<i32>>` rather than cloned deeply.

```rust
pub struct OperationWithTable {
    symbol: OperationSymbol,
    table: Arc<Vec<i32>>, // Shared across all clones
}
```
This reduces the cost of `clone_box()` from O(N) to O(1), where N is the total size of all operation tables.

---

## 3. Python Extension Redundancy
The `uacalc_lib` crate (Python bindings) re-implements `PySimpleListInner` to hold `PyObject` instead of making the core `SimpleList<T>` generic enough to be used.

### Problem:
Code duplication between the core library and the extension.

### Suggestion: Use generic `SimpleList<PyObject>`
Since the core `SimpleList<T>` is already generic, the Python extension should simply use it directly:

```rust
// Instead of re-implementing logic:
type PySimpleList = SimpleList<PyObject>;
```
This ensures that any improvements made to the core `SimpleList` (e.g., tail-call optimization) are automatically available to the Python bindings.
