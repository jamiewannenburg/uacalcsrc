#!/usr/bin/env python3
"""Median timings for phase-3 overhead comparison (no limits set)."""

from __future__ import annotations

import argparse
import os
import statistics
import sys
import time
from pathlib import Path


def _median_ms(samples: list[float]) -> float:
    return statistics.median(samples)


def bench_sg_close_power(repeats: int, runs: int) -> float:
    import uacalc_lib as u

    root = Path.cwd()
    path = str(root / "resources" / "algebras" / "m4.ua")
    samples: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        for _ in range(repeats):
            u.clear_cancel()
            u.set_memory_limit(None)
            u.set_element_limit(None)
            u.set_time_limit(None)
            alg = u.io.AlgebraReader.new_from_file(path).read_algebra_file()
            bp = u.alg.BigProductAlgebra.new_power(alg, 5)
            gens = [
                u.util.IntArray.from_array([0, 0, 1, 0, 0]),
                u.util.IntArray.from_array([1, 1, 0, 1, 0]),
                u.util.IntArray.from_array([2, 1, 2, 0, 1]),
            ]
            closer = u.alg.Closer(bp, gens)
            closer.set_suppress_output(True)
            closer.sg_close_power()
        samples.append((time.perf_counter() - t0) * 1000.0 / repeats)
    return _median_ms(samples)


def bench_sg_close_parallel(repeats: int, runs: int) -> float:
    import uacalc_lib as u

    root = Path.cwd()
    path = str(root / "resources" / "algebras" / "m4.ua")
    samples: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        for _ in range(repeats):
            u.clear_cancel()
            alg = u.io.AlgebraReader.new_from_file(path).read_algebra_file()
            bp = u.alg.BigProductAlgebra.new_power(alg, 4)
            gens = [
                u.util.IntArray.from_array([0, 0, 1, 0]),
                u.util.IntArray.from_array([1, 1, 0, 1]),
            ]
            closer = u.alg.Closer.new_with_make_term_map(bp, gens, True)
            closer.set_suppress_output(True)
            closer.sg_close_parallel()
        samples.append((time.perf_counter() - t0) * 1000.0 / repeats)
    return _median_ms(samples)


def bench_term_interpretation(repeats: int, runs: int) -> float:
    import uacalc_lib as u

    root = Path.cwd()
    path = str(root / "resources" / "algebras" / "m4.ua")
    samples: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        for _ in range(repeats):
            alg = u.io.AlgebraReader.new_from_file(path).read_algebra_file()
            var = u.terms.VariableImp("x0")
            var.interpretation(alg, ["x0", "x1", "x2"], True)
        samples.append((time.perf_counter() - t0) * 1000.0 / repeats)
    return _median_ms(samples)


def bench_type_set(repeats: int, runs: int) -> float:
    import uacalc_lib as u

    root = Path.cwd()
    path = str(root / "resources" / "algebras" / "lyndon.ua")
    samples: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        for _ in range(repeats):
            alg = u.io.AlgebraReader.new_from_file(path).read_algebra_file()
            tf = u.alg.TypeFinder(alg)
            tf.init()
            tf.find_type_set()
        samples.append((time.perf_counter() - t0) * 1000.0 / repeats)
    return _median_ms(samples)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--runs", type=int, default=11)
    parser.add_argument("--label", default="branch")
    args = parser.parse_args()
    out = {
        "sg_close_power_median_ms": bench_sg_close_power(args.repeats, args.runs),
        "sg_close_parallel_median_ms": bench_sg_close_parallel(args.repeats, args.runs),
        "term_interpretation_median_ms": bench_term_interpretation(args.repeats, args.runs),
        "type_set_median_ms": bench_type_set(args.repeats, args.runs),
    }
    for k, v in out.items():
        print(f"{args.label}_{k}={v:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())