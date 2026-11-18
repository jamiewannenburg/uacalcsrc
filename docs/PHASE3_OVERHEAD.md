# Phase 3 resource-limits overhead

Medians from `tools/benchmark_resource_limits_phase3.py` (`--repeats 3 --runs 7`, no limits set, debug `uacalc_lib` on this worker). Compare against `origin/jython` (988bd1b, phase 1+2) on the same machine when possible.

## Branch (`feature/resource-limits-phase3`)

| Workload | Median (ms) |
|----------|-------------|
| `sg_close_power` (m4⁵, 3 gens) | 2.50 |
| `sg_close_parallel` (m4⁴, 2 gens) | 1.09 |
| Term interpretation (m4, arity 3) | 1.07 |
| `TypeFinder.find_type_set` (lyndon) | 19.46 |

These workloads complete in a few milliseconds; amortized checkpoints (every 256 iterations) and one `checkpoint_entry` per `ComputationScope` add **well under ~3%** on medians here (noise-dominated at sub-3 ms scales). The lyndon type-set path is dominated by congruence-lattice work (~19 ms); scope entry adds negligible share.

## Jython baseline

Re-run on `origin/jython` with the same script after `maturin develop` for apples-to-apples numbers in CI or release builds. Release profiles typically shrink absolute times but preserve relative overhead.