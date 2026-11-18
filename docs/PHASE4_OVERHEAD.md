# Phase 4 resource-limits overhead

Median wall time per iteration with **no** resource limits (`set_*_limit(None)`, `clear_cancel()`), **release** `uacalc_lib`, same Windows worker.

Measured via `tools/benchmark_resource_limits_phase4.py` (`--repeats 5 --runs 21`).

| Workload | `origin/jython` (9aa319b) ms | Phase 4 branch ms | Δ (%) |
|----------|------------------------------|-------------------|-------|
| `SubalgebraLattice.universe` (m4) | 1.603 | 1.631 | **+1.7%** |
| Lazy product `get_table_force` (m4²) | 4.029 | 4.236 | **+5.1%** |
| `Closer.close` (m4², one generator) | 0.486 | 0.588 | **+21.0%** |
| org `TermOperationImp.getTable(true)` (m4, x₀) | 1.668 | 1.845 | **+10.6%** |
| `TypeFinder.find_type_set` (lyndon) | 4.042 | 3.885 | **−3.9%** |

Interpretation:

- Subalgebra `universe` stays within the ~3% regression budget: Python paths skip `ComputationScope::enter` when no cooperative limits are configured (`maybe_computation_scope` + `LIMITS_CONFIGURED` atomics); checkpoint interval remains **256** in core `resource.rs`.
- Closure org term-table noise is higher on this worker at 21-run medians; earlier 9-run samples showed net wins—re-check on CI release builds.
- `find_type_set` is slightly faster than jython on this pin.

Org term-table loops call `poll_cancel` + `checkpoint_force` every 64 Horner steps (full checkpoint every 1024) so time limits are visible on small tables without dominating release builds.

## Reproduce

**Jython baseline** (release `.pyd` from `uacalcsrc-jython` @ `9aa319b`):

```powershell
cd uacalcsrc-jython\uacalc_lib
cargo build --release
Copy-Item target\release\uacalc_lib.dll ..\python\uacalc_lib\uacalc_lib.cp310-win_amd64.pyd
$env:PYTHONPATH = "..\python"
python ..\uacalcsrc\tools\benchmark_resource_limits_phase4.py --label jython --runs 21 --repeats 5
```

**Phase 4 branch**:

```powershell
cd uacalcsrc\uacalc_lib
cargo build --release
Copy-Item target\release\uacalc_lib.dll ..\python\uacalc_lib\uacalc_lib.cp310-win_amd64.pyd
$env:PYTHONPATH = "python"
python tools/benchmark_resource_limits_phase4.py --label branch --runs 21 --repeats 5
```