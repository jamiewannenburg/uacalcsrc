"""Cooperative resource limits (phase 1) via uacalc_lib and org.uacalc shim."""

from __future__ import annotations

import json
import os
import subprocess
import threading
import time

import pytest

import uacalc_lib
from org.uacalc._exceptions import OutOfMemoryError
from org.uacalc.alg import BigProductAlgebra, Closer
from org.uacalc.alg.op import Operations
from org.uacalc.io import AlgebraIO
from org.uacalc.util import IntArray
from test_utils import build_java_command

# Calibrated on worker (m4.ua product closure + Java free-algebra closure).
M4_ALGEBRA = os.path.join("resources", "algebras", "m4.ua")
HEAVY_POWER = 5
HEAVY_GENERATORS: tuple[tuple[int, ...], ...] = (
    (0, 0, 1, 0, 0),
    (1, 1, 0, 1, 0),
    (2, 1, 2, 0, 1),
)
HEAVY_CLOSURE_SIZE = 13
# Effectively unbounded: uncancelled run would far exceed test timeouts (speed-independent).
STRESS_REPEATS = 1 << 62
CANCEL_WAKE_SEC = 0.15
GENEROUS_TEST_BOUND_SEC = 10.0
MEM_LIMIT_LOW = 512
MEM_LIMIT_HIGH = 4096
JAVA_FREE_NUM_GENS = 3
JAVA_FREE_POWER = 2
JAVA_FREE_GENERATORS = "0,0,1;1,1,0"
JAVA_LOW_XMX_MB = 32
JAVA_HIGH_XMX_MB = 512
JAVA_SUBPROCESS_TIMEOUT_SEC = 180
TIME_LIMIT_REALISTIC_SEC = 0.2


def _repo_root() -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
    )


_M4_CACHE = None


def _m4_org():
    global _M4_CACHE
    if _M4_CACHE is None:
        path = os.path.join(_repo_root(), M4_ALGEBRA)
        _M4_CACHE = AlgebraIO.readAlgebraFile(path)
    return _M4_CACHE


def _heavy_gens() -> list[IntArray]:
    return [IntArray(list(g)) for g in HEAVY_GENERATORS]


def _heavy_org_closer() -> Closer:
    bp = BigProductAlgebra(_m4_org(), HEAVY_POWER)
    return Closer(bp, _heavy_gens())


def _heavy_lib_closer() -> uacalc_lib.alg.Closer:
    os.chdir(_repo_root())
    path = os.path.join(_repo_root(), M4_ALGEBRA)
    m4 = uacalc_lib.io.AlgebraReader.new_from_file(path).read_algebra_file()
    bp = uacalc_lib.alg.BigProductAlgebra.new_power(m4, HEAVY_POWER)
    return uacalc_lib.alg.Closer(bp, _heavy_gens())


def _stress_lib_closer(closer: uacalc_lib.alg.Closer, repeats: int) -> None:
    closer.set_suppress_output(True)
    uacalc_lib.alg._stress_sg_close_power(closer, repeats)


def test_limit_setters_exported():
    for name in (
        "set_memory_limit",
        "set_element_limit",
        "set_time_limit",
        "cancel",
        "clear_cancel",
    ):
        assert hasattr(uacalc_lib, name)


def test_make_int_operation_raises_memory_error_not_value_error():
    LibOps = uacalc_lib.alg.Operations
    uacalc_lib.set_memory_limit(64)
    with pytest.raises(MemoryError, match="memory limit"):
        LibOps.make_int_operation("f", 2, 500, [0] * (500 * 500))


def test_org_operations_make_int_operation_out_of_memory():
    uacalc_lib.set_memory_limit(64)
    with pytest.raises(OutOfMemoryError):
        Operations.makeIntOperation("g", 2, 400, [0] * (400 * 400))


def test_org_closer_sg_close_power_out_of_memory():
    closer = _heavy_org_closer()
    try:
        uacalc_lib.set_memory_limit(MEM_LIMIT_LOW)
        with pytest.raises(OutOfMemoryError):
            closer.sgClosePower()
        uacalc_lib.set_memory_limit(MEM_LIMIT_HIGH)
        ans = closer.sgClosePower()
        assert ans is not None
        assert len(ans) == HEAVY_CLOSURE_SIZE
        uacalc_lib.set_memory_limit(MEM_LIMIT_LOW)
        with pytest.raises(OutOfMemoryError):
            closer.sgClose()
        uacalc_lib.set_memory_limit(None)
        ans2 = closer.sgClose()
        assert ans2 is not None
        assert len(ans2) == HEAVY_CLOSURE_SIZE
    finally:
        uacalc_lib.set_memory_limit(None)


def test_lib_closer_pre_cancel_keyboard_interrupt():
    closer = _heavy_lib_closer()
    uacalc_lib.clear_cancel()
    uacalc_lib.cancel()
    with pytest.raises(KeyboardInterrupt):
        closer.sg_close_power()
    uacalc_lib.clear_cancel()


def test_org_closer_pre_cancel_returns_none():
    closer = _heavy_org_closer()
    uacalc_lib.clear_cancel()
    uacalc_lib.cancel()
    assert closer.sgClosePower() is None
    uacalc_lib.clear_cancel()
    assert _heavy_org_closer().sgClosePower() is not None


def test_lib_closer_cancel_from_other_thread():
    uacalc_lib.clear_cancel()
    started = threading.Event()
    outcome: dict = {"exc": None, "finished": False}

    def run() -> None:
        worker = _heavy_lib_closer()
        started.set()
        try:
            _stress_lib_closer(worker, STRESS_REPEATS)
            outcome["exc"] = "completed"
        except KeyboardInterrupt as exc:
            outcome["exc"] = exc
        finally:
            outcome["finished"] = True

    thread = threading.Thread(target=run, name="stress-close")
    cancel_t0 = time.perf_counter()
    thread.start()
    assert started.wait(timeout=30.0)
    time.sleep(CANCEL_WAKE_SEC)
    uacalc_lib.cancel()
    thread.join(timeout=GENEROUS_TEST_BOUND_SEC)
    interrupted = time.perf_counter() - cancel_t0
    assert not thread.is_alive(), "closure thread did not finish after cancel"
    assert outcome["finished"] is True
    assert isinstance(outcome["exc"], KeyboardInterrupt), outcome["exc"]
    assert interrupted < GENEROUS_TEST_BOUND_SEC
    uacalc_lib.clear_cancel()
    _stress_lib_closer(_heavy_lib_closer(), 5)


def test_limits_reset_allows_repeat_after_failure():
    LibOps = uacalc_lib.alg.Operations
    uacalc_lib.set_memory_limit(64)
    with pytest.raises(MemoryError):
        LibOps.make_int_operation("h", 2, 400, [0] * (400 * 400))
    uacalc_lib.set_memory_limit(None)
    op = LibOps.make_int_operation("h", 2, 2, [0, 1, 1, 0])
    assert op is not None


def test_lib_con_cardinality_memory_and_recompute():
    os.chdir(_repo_root())
    path = os.path.join(_repo_root(), "resources", "algebras", "cyclic3.ua")
    c3 = uacalc_lib.io.AlgebraReader.new_from_file(path).read_algebra_file()
    con = c3.con()
    uacalc_lib.set_memory_limit(32)
    with pytest.raises(MemoryError, match="memory limit"):
        con.con_cardinality()
    uacalc_lib.set_memory_limit(None)
    card = con.con_cardinality()
    assert card >= 2
    assert con.con_cardinality() == card


def test_lib_time_limit_instant_on_closure_entry():
    closer = _heavy_lib_closer()
    uacalc_lib.set_time_limit(1e-12)
    try:
        with pytest.raises(TimeoutError, match="time limit"):
            closer.sg_close_power()
    finally:
        uacalc_lib.set_time_limit(None)


def test_lib_time_limit_realistic_on_stress_closure():
    uacalc_lib.set_time_limit(None)
    closer = _heavy_lib_closer()
    uacalc_lib.set_time_limit(TIME_LIMIT_REALISTIC_SEC)
    t0 = time.perf_counter()
    try:
        with pytest.raises(TimeoutError, match="time limit"):
            _stress_lib_closer(closer, STRESS_REPEATS)
    finally:
        uacalc_lib.set_time_limit(None)
    elapsed = time.perf_counter() - t0
    assert elapsed < GENEROUS_TEST_BOUND_SEC


def _java_sg_close_free_algebra(xmx_mb: int) -> tuple[bool, bool, str]:
    """Return (ran_to_completion, success, detail)."""
    cmd = build_java_command(
        "java_wrapper.src.alg.CloserWrapper",
        [
            "sg_close_free_algebra",
            "--num_gens",
            str(JAVA_FREE_NUM_GENS),
            "--power",
            str(JAVA_FREE_POWER),
            "--generators",
            JAVA_FREE_GENERATORS,
        ],
    )
    cmd.insert(1, f"-Xmx{xmx_mb}m")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=JAVA_SUBPROCESS_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return (False, False, "timeout")
    combined = (proc.stderr or "") + (proc.stdout or "")
    if "OutOfMemoryError" in combined:
        return (True, False, "oom")
    if proc.returncode != 0:
        return (True, False, f"exit {proc.returncode}")
    marker = combined.find('{"success"')
    if marker < 0:
        return (True, False, "no json")
    payload = json.loads(combined[marker:])
    data = payload.get("data", payload)
    if isinstance(data, str):
        data = json.loads(data)
    ok = data.get("status") == "success"
    return (True, ok, "success" if ok else str(data.get("status")))


@pytest.mark.slow
def test_java_vs_python_same_side_of_cutoff():
    if not os.environ.get("JAVA_HOME"):
        pytest.skip("JAVA_HOME not set")

    java_low_ran, java_low_ok, _ = _java_sg_close_free_algebra(JAVA_LOW_XMX_MB)
    java_high_ran, java_high_ok, _ = _java_sg_close_free_algebra(JAVA_HIGH_XMX_MB)
    if not (java_low_ran and not java_low_ok and java_high_ran and java_high_ok):
        pytest.skip("Java -Xmx did not bracket the calibrated free-algebra workload")

    uacalc_lib.set_memory_limit(MEM_LIMIT_LOW)
    try:
        with pytest.raises(MemoryError, match="memory limit"):
            _heavy_lib_closer().sg_close_power()
    finally:
        uacalc_lib.set_memory_limit(None)

    uacalc_lib.set_memory_limit(MEM_LIMIT_HIGH)
    try:
        result = _heavy_lib_closer().sg_close_power()
    finally:
        uacalc_lib.set_memory_limit(None)
    assert result is not None
    assert len(result) == HEAVY_CLOSURE_SIZE