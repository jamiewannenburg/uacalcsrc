# Phase 4 resource-limits overhead

Median wall time per iteration with **no** resource limits (`set_*_limit(None)`, `clear_cancel()`), **release** `uacalc_lib`, same Windows worker.

Measured via `tools/benchmark_resource_limits_phase4.py` and `tools/benchmark_resource_limits_phase3.py` (`--repeats 5 --runs 9` unless noted).

| Workload | `origin/jython` (9aa319b) ms | Phase 4 branch ms | Δ (%) |
|----------|------------------------------|-------------------|-------|
| `SubalgebraLattice.universe` (m4) | 1.716 | 1.805 | **+5.2%** |
| Lazy product `get_table_force` (m4²) | 4.448 | 4.167 | **−6.3%** |
| `Closer.close` (m4², one generator) | 0.678 | 0.501 | **−26.1%** |
| org `TermOperationImp.getTable(true)` (m4, x₀) | 2.167 | 1.793 | **−17.3%** |
| `TypeFinder.find_type_set` (lyndon) | 3.948 | 4.048 | **+2.5%** |

Interpretation:

- Closure and org term-table loops stay well below the ~3% regression budget versus jython (net faster here).
- `find_type_set` is **+2.5%** (improved vs phase 3’s +6.3% on an older jython pin).
- `sub.universe` is **+5.2%** on this worker (GIL release + `Arc<Mutex<…>>`); worth watching on CI release builds but acceptable for cooperative limits.

Org term-table loops call `poll_cancel` + `checkpoint_force` every 64 Horner steps (full checkpoint every 1024) so time limits are visible on small tables without dominating release builds.

## Reproduce

**Jython baseline** (`uacalcsrc-jython` @ `origin/jython`, release `.pyd`):

```powershell
cd uacalcsrc-jython\uacalc_lib
cargo build --release
Copy-Item target\release\uacalc_lib.dll ..\python\uacalc_lib\uacalc_lib.cp310-win_amd64.pyd
$env:PYTHONPATH = "..\python"
python ..\uacalcsrc\tools\benchmark_resource_limits_phase4.py --label jython
```

**Phase 4 branch**:

```powershell
cd uacalcsrc\uacalc_lib
cargo build --release
Copy-Item target\release\uacalc_lib.dll ..\python\uacalc_lib\uacalc_lib.cp310-win_amd64.pyd
$env:PYTHONPATH = "python"
python tools/benchmark_resource_limits_phase4.py --label branch
```