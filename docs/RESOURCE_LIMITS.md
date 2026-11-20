# Cooperative resource limits

Cooperative **per-computation** limits live in the Rust core. There is no subprocess wrapper and no global allocator hook.

## Python API (`uacalc_lib`)

| Function | Semantics |
|----------|-----------|
| `set_memory_limit(bytes \| None)` | Max charged bytes for the next top-level computation |
| `set_element_limit(n \| None)` | Max kept elements (closure / lattice nodes) |
| `set_time_limit(seconds \| None)` | Wall-clock budget from top-level scope entry |
| `cancel()` | Request cooperative stop (global flag) |
| `clear_cancel()` | Clear the cancel flag without consuming it |
| `checkpoint()` | Poll limits/cancel from pure-Python loops (e.g. org term table build) |

Limit configuration (`set_*_limit`) is **thread-local**: only the thread that called the setter stores the values in its TLS budget.

When Python releases the GIL (`py.allow_threads` on `SubalgebraLattice` / `CongruenceLattice` methods), the worker thread copies the caller’s limit snapshot via `AllowThreadsResourceGuard::enter()` before running checked Rust code, so limits set on the main thread still apply inside the worker. The global `LIMITS_CONFIGURED` atomic reflects whether **any** thread has a non-`None` limit (used to decide whether to open a top-level `ComputationScope` on the fast path).

**Cancel** and **Python signals** do not require a scope: `cancel()` sets a global flag read at every [`CHECKPOINT_INTERVAL`] (256) step and in `poll_cancel` / `checkpoint_force`. With no limits configured, lattice code may skip the outer `ComputationScope` but checkpoints and the signal hook still run on the inner loops.

Limits apply when a **top-level** `ComputationScope` starts (e.g. `Closer.sg_close`, `con_cardinality`, `SubalgebraLattice.cardinality` / `universe`). Nested scopes share the same budget and do **not** reset counters.

Parallel closure workers attach to a **shared budget** (`SharedBudget`) so charges and checkpoints on all threads count against one computation.

## Error mapping (`uacalc_lib`)

| `UaError` | Python |
|-----------|--------|
| `Memory` / `ElementLimit` | `MemoryError` |
| `Interrupted` | `KeyboardInterrupt` |
| `TimeLimit` | `TimeoutError` |
| `Message` | `ValueError` |

## `org.uacalc` shim

- `MemoryError` → `OutOfMemoryError` (`java.lang.OutOfMemoryError`) via `_lib_call` on `alg`, `alg.sublat`, and related shims
- `Closer.sgClose*` / `sg_close` / `sg_close_power` / `sg_close_parallel` → `None` on `KeyboardInterrupt` via `_lib_call_closer`
- `uacalc_lib` itself raises `KeyboardInterrupt` directly

## Choke points

### Phase 1

1. **`Closer::sg_close_impl` / `sg_close_power_impl`** — charge per newly kept element; checkpoint every 256 inner steps; `set_max_size` unchanged (partial closure, not an error).
2. **`alloc_i32_table`** — `make_int_operation_from_dyn`, XML `opTable` reads.
3. **`CongruenceLattice::make_universe_with_limit`** — charge per new join; checkpoint in loops; failed run clears universe cache (`make_principals_checked`, `make_join_irreducibles_checked`, `make_cg_aux`).

### Phase 2

4. **`SubalgebraLattice`** — checked universe / cardinality / filter / sg paths with `charge_kept_subalgebra`; cache cleared on failure.
5. **`Partition::join_closure_checked` / `meet_closure_checked`** — checkpoints and partition charges.
6. **`CongruenceLattice::permutability_level`** — checkpoints over incomparable pairs.

### Phase 3

7. **Term interpretation** — `alloc_i32_table` up front, checkpoints in Horner fill, `make_int_operation_precharged`; scope per call.
8. **`make_int_operation_from_dyn`** — checkpoints in materialization loop.
9. **`Partition::unary_polymorphisms` / `binary_polymorphisms`** — scope, checkpoints, charge per kept table.
10. **`TypeFinder::find_type_set`** and subtrace helpers — scope and checkpoints.
11. **`Closer::sg_close_parallel`** — shared budget across workers.
12. **Python GIL** — `py.allow_threads` on long **`Closer`** closure methods and `CongruenceLattice::con_cardinality`.

### Phase 4

13. **Lazy `make_table`** — `build_i32_table_horner` in `ProductOperation`, `RestrictedOperation` (subalgebra), quotient op, `convert::operation_to_py` / `ops_to_basic_algebra`; failed builds clear partial tables.
14. **`make_random_operation(s)`** — `alloc_i32_table`, checkpoints in fill and across the similarity type batch.
15. **`Closer::close_checked`** — scope + checkpoint; Python `close()` uses `allow_threads` and `ua_to_py`.
16. **Homomorphism map growth** — `charge_homomorphism_entry` on new `homomorphism.insert` entries during serial closure (in addition to kept-element charges).
17. **`SubalgebraLattice` GIL** — `Arc<Mutex<...>>` wrapper; `allow_threads` on `universe`, `cardinality`, `filter`, `one_generated_subalgebras`, `join_irreducibles` (lock not held across Python re-entry).
18. **`CongruenceLattice::universe_checked`** — Python `universe()` uses checked path + `allow_threads`.
19. **org `TermOperationImp._ensure_table_op`** — calls `uacalc_lib.checkpoint()` every 256 Horner entries.

**Deliberately light / unchanged**

- **`VirtualLists` equality / hash** over huge lists: still O(n) without charging (rare in hot paths); indexed access remains virtual.
- **`PyAbstractOperation::make_table`** (Python callback mode): still runs under the GIL without Rust table charging — callers should prefer Rust table ops when limits matter.
- **`BigProductOperation`**: remains non-table-based by design.

Stress helpers (`_stress_sg_close_power`, `_stress_sub_universe`) remain for focused tests.

## Python GIL and cross-thread `cancel()`

`cancel()` sets a **global** flag honored at checkpoints (including on parallel worker threads when a shared budget is attached). Phase 3+ releases the GIL on long-running **`Closer`** closure methods and, in phase 4, on **`SubalgebraLattice` universe/cardinality/filter** and **`CongruenceLattice.universe`** so another Python thread can call `cancel()` while lattice work runs.

## Rust integration tests

`cancel()` and `reset_all_limits()` touch **process-global** state. Cargo runs each `tests/resource_limits_*.rs` binary in parallel, so those tests must take `resource::test_isolation_guard()` for their full duration; otherwise one test can call `reset_all_limits()` and clear cancel while another’s `*_stress` loop is still running (flake or hang).