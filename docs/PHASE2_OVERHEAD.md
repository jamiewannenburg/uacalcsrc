# Phase 2 overhead and pytest delta

Measured on this worker (Windows, CPython 3.10, `maturin develop`, 7 runs × 3 repeats, no limits set).

| Workload | `origin/jython` median (ms) | Phase 2 branch median (ms) | Δ |
| --- | ---: | ---: | ---: |
| m4.ua `SubalgebraLattice` universe (`cardinality()`) | 7.992 | 8.030 | +0.5% |
| lyndon.ua `CongruenceLattice` universe (`con_cardinality()`) | 7.337 | 6.767 | −7.8% |

## `pytest python/uacalc/tests -m "not slow"` (same venv/build)

| Tree | Failed | Passed |
| --- | ---: | ---: |
| Clean worktree `origin/jython` (`9378c5c`) | 442 | 801 |
| Branch `cursor/resource-limits-phase2-b84d` | 115 | 1143 |

**Failures on branch but not on baseline (3):** these passed in isolation after the full run; likely suite-order / environment coupling, not deterministic regressions:

- `test_subalgebra_lattice::test_join_irreducibles`
- `test_subalgebra_lattice::test_one_generated_subalgebras`
- `test_subalgebra_lattice::test_sg_generation`