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

7. **Term interpretation** (`VariableImp` / `NonVariableTerm::interpretation*`) — `alloc_i32_table` up front, checkpoints in the Horner fill loop, `make_int_operation_precharged`; `ComputationScope` per interpretation call.
8. **`make_int_operation_from_dyn`** — checkpoints in the materialization loop.
9. **`Partition::unary_polymorphisms` / `binary_polymorphisms`** — scope, checkpoints in search, charge per kept polymorphism table.
10. **`TypeFinder::find_type_set`**, **`next_pair_for_subtrace`**, **`find_type_from_subtrace`** — scope and checkpoints; element charge when growing A² / A⁴ universes.
11. **`Closer::sg_close_parallel`** — `ComputationScope`, shared budget across `SingleClose` workers, checkpoints and `charge_kept_closure_element` in worker loops; `UaError` propagation (Python `ua_to_py`).
12. **Python GIL** — `py.allow_threads` on `Closer::sg_close`, `sg_close_from`, `sg_close_power`, `sg_close_parallel`, and `CongruenceLattice::con_cardinality` (checked). **`SubalgebraLattice` universe/cardinality/filter** still hold the GIL: `PySubalgebraLattice` uses an internal `RefCell`, which is not `Sync` and cannot be used inside `allow_threads` without restructuring the wrapper.

Stress helpers (`_stress_sg_close_power`, `_stress_sub_universe`) remain for focused tests.

## Phase 4 (not covered)

- Lazy `make_table` on `ProductOperation`, `SubgroupOperation`, `uacalc_lib::abstract_operation::make_table`, and manual n^arity builders in `power_algebra` / `convert` paths
- **`VirtualLists`** / combination enumeration helpers
- **`make_random_operations*`** large table batches beyond existing `make_int_operation` charge
- **`Closer::close`** (non–sub-power) and most **`BigProductAlgebra`** entry points without `allow_threads`
- **`SubalgebraLattice` GIL release** (requires `RefCell` → `Mutex` or owned-lattice transfer before `allow_threads`)
- **`CongruenceLattice::universe`** Python accessor (still uncached infallible path; limits apply via `con_cardinality_checked` / `make_universe_with_limit_checked` on other entry points)
- Term interpretation during **Jython compat** table builds in `python/org/uacalc/alg/op/_jython_compat.py` (pure Python loops)
- Homomorphism / equation checking inside serial closure (no extra charges beyond kept elements)

## Python GIL and cross-thread `cancel()`

`cancel()` sets a **global** flag honored at checkpoints (including on parallel worker threads when a shared budget is attached). Phase 3 releases the GIL on long-running **`Closer`** closure methods so another Python thread can call `cancel()` while subpower closure runs. Ctrl-C on the main thread is still polled via the signal hook inside checkpoints.