#!/usr/bin/env python3
"""Phase 4 overhead medians (no limits set)."""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path


def _median_ms(samples: list[float]) -> float:
    return statistics.median(samples)


def bench_sub_universe(repeats: int, runs: int) -> float:
    import uacalc_lib as u

    path = str(Path.cwd() / "resources" / "algebras" / "m4.ua")
    samples: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        for _ in range(repeats):
            u.clear_cancel()
            u.set_memory_limit(None)
            u.set_element_limit(None)
            u.set_time_limit(None)
            alg = u.io.AlgebraReader.new_from_file(path).read_algebra_file()
            sub = alg.sub()
            sub.universe()
        samples.append((time.perf_counter() - t0) * 1000.0 / repeats)
    return _median_ms(samples)


def bench_lazy_product_table(repeats: int, runs: int) -> float:
    import uacalc_lib as u

    path = str(Path.cwd() / "resources" / "algebras" / "m4.ua")
    samples: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        for _ in range(repeats):
            alg = u.io.AlgebraReader.new_from_file(path).read_algebra_file()
            prod = u.alg.ProductAlgebra("m4^2", [alg, alg])
            op = prod.operations()[0]
            op.get_table_force(True)
        samples.append((time.perf_counter() - t0) * 1000.0 / repeats)
    return _median_ms(samples)


def bench_closer_close(repeats: int, runs: int) -> float:
    import uacalc_lib as u

    path = str(Path.cwd() / "resources" / "algebras" / "m4.ua")
    samples: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        for _ in range(repeats):
            alg = u.io.AlgebraReader.new_from_file(path).read_algebra_file()
            bp = u.alg.BigProductAlgebra.new_power(alg, 2)
            gens = [u.util.IntArray.from_array([0, 0])]
            closer = u.alg.Closer(bp, gens)
            closer.close()
        samples.append((time.perf_counter() - t0) * 1000.0 / repeats)
    return _median_ms(samples)


def bench_org_term_table(repeats: int, runs: int) -> float:
    import org.uacalc.alg.op  # noqa: F401 — TermOperationImp getTable
    import uacalc_lib as u
    from org.uacalc.io import AlgebraIO
    from org.uacalc.terms import VariableImp

    path = str(Path.cwd() / "resources" / "algebras" / "m4.ua")
    samples: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        for _ in range(repeats):
            u.clear_cancel()
            m4 = AlgebraIO.readAlgebraFile(path)
            var = VariableImp("x0")
            op = var.interpretation(m4)
            op.getTable(True)
        samples.append((time.perf_counter() - t0) * 1000.0 / repeats)
    return _median_ms(samples)


def bench_type_set(repeats: int, runs: int) -> float:
    import uacalc_lib as u

    path = str(Path.cwd() / "resources" / "algebras" / "lyndon.ua")
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
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--runs", type=int, default=9)
    parser.add_argument("--label", default="branch")
    args = parser.parse_args()
    out = {
        "sub_universe_median_ms": bench_sub_universe(args.repeats, args.runs),
        "lazy_product_table_median_ms": bench_lazy_product_table(args.repeats, args.runs),
        "closer_close_median_ms": bench_closer_close(args.repeats, args.runs),
        "org_term_table_median_ms": bench_org_term_table(args.repeats, args.runs),
        "type_set_median_ms": bench_type_set(args.repeats, args.runs),
    }
    for k, v in out.items():
        print(f"{args.label}_{k}={v:.4f}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
    raise SystemExit(main())