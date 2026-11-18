# Phase 3 resource-limits overhead

Median wall time per iteration with **no** resource limits (`set_*_limit(None)`, `clear_cancel()`), **release** `uacalc_lib`, same Windows worker.

Measured via `tools/benchmark_resource_limits_phase3.py` (`--repeats 5 --runs 11`).

| Workload | `origin/jython` (988bd1b) ms | Phase 3 branch ms | Δ (%) |
|----------|------------------------------|-------------------|-------|
| `sg_close_power` (m4⁵) | 0.884 | 0.851 | **−3.7%** |
| `sg_close_parallel` (m4⁴, term map) | 0.594 | 0.592 | **−0.4%** |
| Term interpretation (m4, arity 3) | 0.637 | 0.570 | **−10.5%** |
| `TypeFinder.find_type_set` (lyndon) | 4.454 | 4.735 | **+6.3%** |

Interpretation:

- Sub‑millisecond workloads are noise‑dominated; power / parallel / term medians are flat or faster than jython.
- Type set adds one `ComputationScope` and join‑irreducible checkpoints (+0.28 ms median here). Re‑measure on CI release builds; target remains **≤ ~3%** on primary closure paths.

## Reproduce

**Jython baseline** (isolated venv, release build from `origin/jython` worktree):

```powershell
cd uacalcsrc-jython\uacalc_lib
cargo build --release
# install .pyd + python/uacalc_lib/__init__.py into a fresh venv site-packages
python tools/benchmark_resource_limits_phase3.py --label jython
```

**Phase 3 branch**:

```powershell
maturin develop --release
$env:PYTHONPATH = "python"
python tools/benchmark_resource_limits_phase3.py --label branch
```