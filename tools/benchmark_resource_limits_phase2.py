#!/usr/bin/env python3
"""Median timings for phase-2 overhead comparison (no limits set)."""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path


def _median_ms(samples: list[float]) -> float:
    return statistics.median(samples)


def bench_m4_sub_universe(repeats: int, runs: int) -> float:
    import uacalc_lib as u

    path = str(Path("resources/algebras/m4.ua").resolve())
    u.set_memory_limit(None)
    u.set_element_limit(None)
    u.clear_cancel()

    def once() -> None:
        alg = u.io.AlgebraReader.new_from_file(path).read_algebra_file()
        sub = alg.sub()
        sub.universe_found()  # cheap if cached
        # force recompute on fresh lattice each time
        _ = sub.cardinality()

    # warm
    once()
    samples: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        for _ in range(repeats):
            alg = u.io.AlgebraReader.new_from_file(path).read_algebra_file()
            _ = alg.sub().cardinality()
        samples.append((time.perf_counter() - t0) * 1000.0 / repeats)
    return _median_ms(samples)


def bench_lyndon_con_universe(repeats: int, runs: int) -> float:
    import uacalc_lib as u

    path = str(Path("resources/algebras/lyndon.ua").resolve())
    u.set_memory_limit(None)
    u.set_element_limit(None)

    samples: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        for _ in range(repeats):
            alg = u.io.AlgebraReader.new_from_file(path).read_algebra_file()
            _ = alg.con().con_cardinality()
        samples.append((time.perf_counter() - t0) * 1000.0 / repeats)
    return _median_ms(samples)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--runs", type=int, default=7)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    import os

    os.chdir(root)
    m4 = bench_m4_sub_universe(args.repeats, args.runs)
    lyndon = bench_lyndon_con_universe(args.repeats, args.runs)
    print(f"m4_sub_universe_median_ms={m4:.4f}")
    print(f"lyndon_con_cardinality_median_ms={lyndon:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())