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

## Error mapping (`uacalc_lib`)

| `UaError` | Python |
|-----------|--------|
| `Memory` / `ElementLimit` | `MemoryError` |
| `Interrupted` | `KeyboardInterrupt` |
| `TimeLimit` | `TimeoutError` |
| `Message` | `ValueError` |

## `org.uacalc` shim

- `MemoryError` → `OutOfMemoryError` (`java.lang.OutOfMemoryError`) via `_lib_call` on `alg`, `alg.sublat`, and related shims
- `Closer.sgClose*` → `None` on `KeyboardInterrupt` (Java interrupt behaviour)
- `uacalc_lib` itself raises `KeyboardInterrupt` directly

## Choke points

### Phase 1

1. **`Closer::sg_close_impl` / `sg_close_power_impl`** — charge per newly kept element; checkpoint every 256 inner steps; `set_max_size` unchanged (partial closure, not an error).
2. **`alloc_i32_table`** — `make_int_operation_from_dyn`, XML `opTable` reads.
3. **`CongruenceLattice::make_universe_with_limit`** — charge per new join; checkpoint in loops; failed run clears universe cache (`make_principals_checked`, `make_join_irreducibles_checked`, `make_cg_aux`).

### Phase 2

4. **`SubalgebraLattice`** — `make_sg_with_max_size_checked` (checkpoints + memory charge on new closure elements); `make_one_generated_subalgebras_checked`, `make_join_irreducibles_checked`, `join_closure_checked`, `make_universe_with_limit_checked` / `cardinality_checked` / `universe_checked` / `filter_checked` with `charge_kept_subalgebra` on kept `BasicSet`s; `clear_sublat_computation_caches` on failure; Python `cardinality`, `universe`, `filter`, `sg`, `one_generated_subalgebras`, `join_irreducibles`.
5. **`Partition::join_closure_checked` / `meet_closure_checked`** — checkpoints and `charge_kept_partition` when new partitions are kept (used by lattice closures and partition helpers).
6. **`CongruenceLattice::permutability_level`** — checkpoints over incomparable pairs once the universe is known.

## Not covered (later phases)

- Term interpretation tables (except op-table materialization)
- Polymorphisms search
- **`sg_close_parallel`**
- Releasing the GIL on routine `sg()` / `SubalgebraLattice` methods (stress helper `_stress_sub_universe` releases the GIL for tests)

## Python GIL and cross-thread `cancel()` (phase 3)

`cancel()` sets a **global** flag that Rust checkpoints honor on any thread. Most Python entry points still run **while holding the GIL**, so another Python thread often cannot call `cancel()` until the call returns. Cooperative stop from another thread during a normal computation therefore does not work today; only **Ctrl-C** (main thread) is polled via the signal hook inside checkpoints.

Phase 1–2 tests use private stress helpers (`_stress_sg_close_power`, `_stress_sub_universe`) that release the GIL with `allow_threads` so cross-thread cancel can be exercised. **Phase 3:** release the GIL around the Rust body of long-running exported methods so `cancel()` from a worker thread matches Rust behaviour.