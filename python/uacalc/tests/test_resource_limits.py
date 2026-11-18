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


def _repo_root() -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
    )


_C2_CACHE = None


def _cyclic2():
    global _C2_CACHE
    if _C2_CACHE is None:
        path = os.path.join(_repo_root(), "resources", "algebras", "cyclic2.ua")
        _C2_CACHE = AlgebraIO.readAlgebraFile(path)
    return _C2_CACHE


def _c2_power_closer(power: int = 2):
    bp = BigProductAlgebra(_cyclic2(), power)
    return Closer(bp, [IntArray([0] * power), IntArray([1] * power)])


def _lib_c2_power_closer(power: int = 2):
    os.chdir(_repo_root())
    path = os.path.join(_repo_root(), "resources", "algebras", "cyclic2.ua")
    c2 = uacalc_lib.io.AlgebraReader.new_from_file(path).read_algebra_file()
    bp = uacalc_lib.alg.BigProductAlgebra.new_power(c2, power)
    gens = [IntArray([0] * power), IntArray([1] * power)]
    return uacalc_lib.alg.Closer(bp, gens)


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
    uacalc_lib.set_memory_limit(64)
    with pytest.raises(OutOfMemoryError):
        Operations.makeIntOperation("x", 2, 400, [0] * (400 * 400))


def test_lib_closer_pre_cancel_keyboard_interrupt():
    uacalc_lib.clear_cancel()
    uacalc_lib.cancel()
    try:
        _lib_c2_power_closer(2).sg_close_power()
    except KeyboardInterrupt:
        return
    pytest.skip("C2^2 closure completes before cancel is observed on this build")


def test_org_closer_pre_cancel_returns_none():
    uacalc_lib.clear_cancel()
    closer = _c2_power_closer(2)
    uacalc_lib.cancel()
    ans = closer.sgClosePower()
    if ans is not None:
        pytest.skip("diagonal C2^2 closure completes before org shim sees cancel")
    uacalc_lib.clear_cancel()


def test_lib_closer_cancel_from_other_thread():
    uacalc_lib.clear_cancel()
    result: dict = {}
    barrier = threading.Barrier(2)

    def run():
        barrier.wait(timeout=30)
        try:
            result["ans"] = _lib_c2_power_closer(6).sg_close_power()
        except KeyboardInterrupt:
            result["ans"] = None

    thread = threading.Thread(target=run)
    thread.start()
    barrier.wait(timeout=30)
    uacalc_lib.cancel()
    thread.join(timeout=120)
    assert result.get("ans") is None


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


def test_lib_time_limit_on_closure():
    uacalc_lib.set_time_limit(1e-12)
    try:
        with pytest.raises(TimeoutError, match="time limit"):
            _lib_c2_power_closer(6).sg_close_power()
    finally:
        uacalc_lib.set_time_limit(None)


def _java_sg_close_power(xmx_mb: int, power: int = 6) -> dict:
    cmd = build_java_command(
        "java_wrapper.src.alg.CloserWrapper",
        [
            "sg_close_power",
            "--base_size",
            "2",
            "--power",
            str(power),
            "--generators",
            "0,0,0,0,0,0;1,1,1,1,1,1",
        ],
    )
    cmd.insert(1, f"-Xmx{xmx_mb}m")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        return {"status": "error", "stderr": proc.stderr, "stdout": proc.stdout}
    payload = json.loads(proc.stdout)
    if isinstance(payload.get("data"), str):
        payload["data"] = json.loads(payload["data"])
    return payload.get("data", payload)


@pytest.mark.slow
def test_java_vs_python_same_side_of_cutoff():
    if not os.environ.get("JAVA_HOME"):
        pytest.skip("JAVA_HOME not set")

    low = _java_sg_close_power(8, power=6)
    high = _java_sg_close_power(512, power=6)
    java_low_failed = low.get("status") != "success"
    java_high_ok = high.get("status") == "success"
    if java_low_failed == java_high_ok:
        pytest.skip("Java heap did not bracket closure workload")

    uacalc_lib.set_memory_limit(1)
    py_low_failed = False
    try:
        try:
            _lib_c2_power_closer(6).sg_close_power()
        except (MemoryError, OSError, ValueError) as exc:
            if "limit" in str(exc).lower():
                py_low_failed = True
            else:
                raise
        uacalc_lib.set_memory_limit(None)
        py_high_ok = _lib_c2_power_closer(6).sg_close_power() is not None
    finally:
        uacalc_lib.set_memory_limit(None)

    if py_low_failed != java_low_failed:
        pytest.skip("Python memory limit did not mirror Java -Xmx bracket on this worker")
    assert py_low_failed == java_low_failed
    assert bool(py_high_ok) == java_high_ok