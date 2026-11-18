# Cooperative resource limits (phase 1)

Phase 1 adds **per-computation** cooperative limits inside the Rust core. There is no subprocess wrapper and no global allocator hook.

## Python API (`uacalc_lib`)

| Function | Semantics |
|----------|-----------|
| `set_memory_limit(bytes \| None)` | Max charged bytes for the next top-level computation |
| `set_element_limit(n \| None)` | Max kept elements (closure / con-universe nodes) |
| `set_time_limit(seconds \| None)` | Wall-clock budget from top-level scope entry |
| `cancel()` | Request cooperative stop (global flag) |
| `clear_cancel()` | Clear the cancel flag without consuming it |

Limits apply when a **top-level** `ComputationScope` starts (e.g. `Closer.sg_close`, `con_cardinality` with universe build). Nested scopes share the same budget and do **not** reset counters.

## Error mapping (`uacalc_lib`)

| `UaError` | Python |
|-----------|--------|
| `Memory` / `ElementLimit` | `MemoryError` |
| `Interrupted` | `KeyboardInterrupt` |
| `TimeLimit` | `TimeoutError` |
| `Message` | `ValueError` |

## `org.uacalc` shim

- `MemoryError` → `OutOfMemoryError` (`java.lang.OutOfMemoryError`)
- `Closer.sgClose*` → `None` on `KeyboardInterrupt` (Java interrupt behaviour)
- `uacalc_lib` itself raises `KeyboardInterrupt` directly

## Choke points (phase 1)

1. **`Closer::sg_close_impl` / `sg_close_power_impl`** — charge per newly kept element; checkpoint every 256 inner steps; `set_max_size` unchanged (partial closure, not an error).
2. **`alloc_i32_table`** — `make_int_operation_from_dyn`, XML `opTable` reads.
3. **`CongruenceLattice::make_universe_with_limit`** — charge per new join; checkpoint in loops; failed run clears universe cache.

## Not covered (later phases)

- Subalgebra lattice construction
- Partition-join closures beyond con-universe
- Term interpretation tables (except op-table materialization)
- Polymorphisms search
- **`sg_close_parallel`** (phase 2–3)

## Python GIL and cross-thread `cancel()` (phase 3)

`cancel()` sets a **global** flag that Rust checkpoints honor on any thread. On the Python bindings, however, **`Closer.sg_close_power` / `sg_close` (and other real closure paths) run while holding the CPython GIL**, so another Python thread cannot call `cancel()` until that call returns. Cooperative stop from another thread during a **normal** closure therefore does not work today; only **Ctrl-C** (main thread) is polled via the signal hook inside checkpoints.

Phase 1 tests use the private **`_stress_sg_close_power`** helper, which releases the GIL with `allow_threads` so cross-thread cancel can be exercised. **Phase 3:** release the GIL around the Rust body of `sg_close*` / other long-running exported methods so `cancel()` from a worker thread matches Rust behaviour.