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
M4_SUB_CARD = 31
LYNDON_CON_CARD_MIN = 10
LYNDON_ALGEBRA = os.path.join("resources", "algebras", "lyndon.ua")
JAVA_SUB_LOW_XMX_MB = 32
JAVA_SUB_HIGH_XMX_MB = 512
PYTHON_SUB_MEM_LOW = 64
PYTHON_SUB_MEM_HIGH = 4096
PYTHON_CON_MEM_LOW = 128
PYTHON_CON_ELEMENT_LOW = 4
JAVA_SUB_STRESS_COPIES = 48
JAVA_SUB_STRESS_RESERVE_MB = 4
PYTHON_SUB_STRESS_MEM_LOW = 64


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


def _heavy_lib_gens_lib() -> list:
    return [uacalc_lib.util.IntArray.from_array(list(g)) for g in HEAVY_GENERATORS]


def _heavy_lib_closer_with_term_map() -> uacalc_lib.alg.Closer:
    os.chdir(_repo_root())
    path = os.path.join(_repo_root(), M4_ALGEBRA)
    m4 = uacalc_lib.io.AlgebraReader.new_from_file(path).read_algebra_file()
    bp = uacalc_lib.alg.BigProductAlgebra.new_power(m4, HEAVY_POWER)
    return uacalc_lib.alg.Closer.new_with_make_term_map(bp, _heavy_lib_gens_lib(), True)


def _stress_lib_closer(closer: uacalc_lib.alg.Closer, repeats: int) -> None:
    closer.set_suppress_output(True)
    stress = getattr(uacalc_lib.alg, "stress_sg_close_power", None) or getattr(
        uacalc_lib.alg, "_stress_sg_close_power"
    )
    stress(closer, repeats)


def _stress_lib_sub_universe(sub: uacalc_lib.alg.SubalgebraLattice, repeats: int) -> int:
    stress = getattr(uacalc_lib.alg, "stress_sub_universe", None) or getattr(
        uacalc_lib.alg, "_stress_sub_universe"
    )
    return stress(sub, repeats)


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


def test_lib_closer_production_cancel_from_other_thread():
    """Cross-thread cancel on real sg_close_power (GIL released), not stress helper."""
    uacalc_lib.clear_cancel()
    started = threading.Event()
    outcome: dict = {"exc": None, "finished": False}

    def run() -> None:
        started.set()
        try:
            while True:
                worker = _heavy_lib_closer()
                worker.set_suppress_output(True)
                worker.sg_close_power()
        except KeyboardInterrupt as exc:
            outcome["exc"] = exc
        finally:
            outcome["finished"] = True

    thread = threading.Thread(target=run, name="prod-close")
    cancel_t0 = time.perf_counter()
    thread.start()
    assert started.wait(timeout=30.0)
    ticks = 0
    wake_deadline = time.perf_counter() + CANCEL_WAKE_SEC
    while time.perf_counter() < wake_deadline:
        ticks += 1
        time.sleep(0.01)
    uacalc_lib.cancel()
    thread.join(timeout=GENEROUS_TEST_BOUND_SEC)
    interrupted = time.perf_counter() - cancel_t0
    assert ticks >= 5, "main thread blocked while closure ran"
    assert not thread.is_alive()
    assert outcome["finished"] is True
    assert isinstance(outcome["exc"], KeyboardInterrupt), outcome["exc"]
    assert interrupted < GENEROUS_TEST_BOUND_SEC
    uacalc_lib.clear_cancel()
    assert len(_heavy_lib_closer().sg_close_power()) == HEAVY_CLOSURE_SIZE


def test_lib_closer_production_sg_close_cancel_from_other_thread():
    """Cross-thread cancel on real ``sg_close`` (not stress helper)."""
    uacalc_lib.clear_cancel()
    started = threading.Event()
    outcome: dict = {"exc": None, "finished": False}

    def run() -> None:
        started.set()
        worker = _heavy_lib_closer()
        worker.set_suppress_output(True)
        try:
            while True:
                worker.sg_close()
        except KeyboardInterrupt as exc:
            outcome["exc"] = exc
        finally:
            outcome["finished"] = True

    thread = threading.Thread(target=run, name="prod-sg-close")
    cancel_t0 = time.perf_counter()
    thread.start()
    assert started.wait(timeout=30.0)
    ticks = 0
    wake_deadline = time.perf_counter() + CANCEL_WAKE_SEC
    while time.perf_counter() < wake_deadline:
        ticks += 1
        time.sleep(0.01)
    uacalc_lib.cancel()
    thread.join(timeout=GENEROUS_TEST_BOUND_SEC)
    assert ticks >= 3, "main thread blocked before cancel"
    assert not thread.is_alive()
    assert outcome["finished"] is True
    assert isinstance(outcome["exc"], KeyboardInterrupt), outcome["exc"]
    assert time.perf_counter() - cancel_t0 < GENEROUS_TEST_BOUND_SEC
    uacalc_lib.clear_cancel()
    ans = _heavy_lib_closer().sg_close_power()
    assert len(ans) == HEAVY_CLOSURE_SIZE


def test_lib_parallel_closer_production_cancel_from_other_thread():
    """Parallel ``sg_close_parallel`` honors cancel from another thread (shared budget)."""
    uacalc_lib.clear_cancel()
    started = threading.Event()
    outcome: dict = {"exc": None, "finished": False}

    def run() -> None:
        started.set()
        try:
            while True:
                worker = _heavy_lib_closer_with_term_map()
                worker.set_suppress_output(True)
                worker.sg_close_parallel()
        except KeyboardInterrupt as exc:
            outcome["exc"] = exc
        finally:
            outcome["finished"] = True

    thread = threading.Thread(target=run, name="prod-parallel-close")
    cancel_t0 = time.perf_counter()
    thread.start()
    assert started.wait(timeout=30.0)
    time.sleep(CANCEL_WAKE_SEC)
    uacalc_lib.cancel()
    thread.join(timeout=GENEROUS_TEST_BOUND_SEC)
    assert not thread.is_alive()
    assert outcome["finished"] is True
    assert isinstance(outcome["exc"], KeyboardInterrupt), outcome["exc"]
    assert time.perf_counter() - cancel_t0 < GENEROUS_TEST_BOUND_SEC
    uacalc_lib.clear_cancel()
    assert len(_heavy_lib_closer_with_term_map().sg_close_parallel()) > 0


def test_lib_main_thread_responsive_during_closure():
    done = threading.Event()
    started = threading.Event()

    def run() -> None:
        closer = _heavy_lib_closer()
        closer.set_suppress_output(True)
        started.set()
        end = time.perf_counter() + 1.0
        while time.perf_counter() < end:
            closer.sg_close_power()
        done.set()

    t = threading.Thread(target=run, daemon=True)
    t.start()
    assert started.wait(timeout=GENEROUS_TEST_BOUND_SEC)
    ticks = 0
    deadline = time.perf_counter() + 0.5
    while time.perf_counter() < deadline and not done.is_set():
        ticks += 1
        time.sleep(0.01)
    assert ticks >= 20, "main thread starved while closure ran (GIL not released)"
    done.wait(timeout=GENEROUS_TEST_BOUND_SEC)
    t.join(timeout=GENEROUS_TEST_BOUND_SEC)


def test_lib_term_interpretation_memory_limit():
    m4 = _m4_lib_algebra()
    var = uacalc_lib.terms.VariableImp("x0")
    uacalc_lib.set_memory_limit(32)
    try:
        with pytest.raises(MemoryError, match="memory limit"):
            var.interpretation(m4, ["x0", "x1"], True)
    finally:
        uacalc_lib.set_memory_limit(None)
    op = var.interpretation(m4, ["x0", "x1"], True)
    assert op is not None


def test_org_unary_polymorphisms_element_limit():
    from org.uacalc.alg.conlat import BasicPartition

    pars = [BasicPartition.zero(3), BasicPartition.one(3)]
    uacalc_lib.set_element_limit(4)
    try:
        with pytest.raises(OutOfMemoryError):
            BasicPartition.unaryPolymorphisms(pars)
    finally:
        uacalc_lib.set_element_limit(None)
    polys = BasicPartition.unaryPolymorphisms(pars)
    assert len(polys) > 0


def test_org_closer_production_cancel_returns_none():
    closer = _heavy_org_closer()
    uacalc_lib.clear_cancel()
    started = threading.Event()
    holder: dict = {"ans": "pending"}

    def run() -> None:
        started.set()
        while True:
            ans = _heavy_org_closer().sgClosePower()
            if ans is None:
                holder["ans"] = None
                break
            holder["ans"] = ans

    thread = threading.Thread(target=run)
    thread.start()
    assert started.wait(timeout=30.0)
    time.sleep(CANCEL_WAKE_SEC)
    uacalc_lib.cancel()
    thread.join(timeout=GENEROUS_TEST_BOUND_SEC)
    assert holder["ans"] is None
    uacalc_lib.clear_cancel()
    assert _heavy_org_closer().sgClosePower() is not None


def test_lib_type_set_time_limit():
    lyndon = _lyndon_lib_algebra()
    tf = uacalc_lib.alg.TypeFinder(lyndon)
    tf.init()
    uacalc_lib.set_time_limit(0)
    try:
        with pytest.raises(TimeoutError):
            tf.find_type_set()
    finally:
        uacalc_lib.set_time_limit(None)
    types = tf.find_type_set()
    assert len(types) >= 1


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


def _m4_lib_algebra():
    os.chdir(_repo_root())
    path = os.path.join(_repo_root(), "resources", "algebras", "m4.ua")
    return uacalc_lib.io.AlgebraReader.new_from_file(path).read_algebra_file()


def _lyndon_lib_algebra():
    os.chdir(_repo_root())
    path = os.path.join(_repo_root(), "resources", "algebras", "lyndon.ua")
    return uacalc_lib.io.AlgebraReader.new_from_file(path).read_algebra_file()


def test_lib_subalgebra_cardinality_memory_and_recompute():
    sub = _m4_lib_algebra().sub()
    uacalc_lib.set_memory_limit(64)
    try:
        with pytest.raises(MemoryError, match="memory limit"):
            sub.cardinality()
    finally:
        uacalc_lib.set_memory_limit(None)
    card = sub.cardinality()
    assert card == M4_SUB_CARD
    assert sub.cardinality() == card


def test_lib_subalgebra_universe_element_limit():
    sub = _m4_lib_algebra().sub()
    uacalc_lib.set_element_limit(4)
    try:
        with pytest.raises(MemoryError, match="element limit"):
            sub.universe()
    finally:
        uacalc_lib.set_element_limit(None)
    assert len(sub.universe()) == M4_SUB_CARD


def test_lib_subalgebra_cancel_from_other_thread():
    uacalc_lib.clear_cancel()
    started = threading.Event()
    outcome: dict = {"exc": None}

    def run() -> None:
        sub = _m4_lib_algebra().sub()
        started.set()
        try:
            _stress_lib_sub_universe(sub, STRESS_REPEATS)
            outcome["exc"] = "completed"
        except KeyboardInterrupt as exc:
            outcome["exc"] = exc

    thread = threading.Thread(target=run)
    cancel_t0 = time.perf_counter()
    thread.start()
    assert started.wait(timeout=30.0)
    time.sleep(CANCEL_WAKE_SEC)
    uacalc_lib.cancel()
    thread.join(timeout=GENEROUS_TEST_BOUND_SEC)
    assert isinstance(outcome["exc"], KeyboardInterrupt)
    assert time.perf_counter() - cancel_t0 < GENEROUS_TEST_BOUND_SEC
    uacalc_lib.clear_cancel()
    assert _m4_lib_algebra().sub().cardinality() == M4_SUB_CARD


def test_org_subalgebra_universe_out_of_memory():
    from org.uacalc.io import AlgebraIO

    m4 = AlgebraIO.readAlgebraFile(os.path.join(_repo_root(), M4_ALGEBRA))
    sub = m4.sub()
    uacalc_lib.set_memory_limit(PYTHON_SUB_MEM_LOW)
    try:
        with pytest.raises(OutOfMemoryError):
            sub.cardinality()
    finally:
        uacalc_lib.set_memory_limit(None)
    assert int(sub.cardinality()) == M4_SUB_CARD


def test_org_subalgebra_universe_and_filter_out_of_memory_and_recovery():
    from org.uacalc.alg.sublat import BasicSet
    from org.uacalc.io import AlgebraIO

    m4 = AlgebraIO.readAlgebraFile(os.path.join(_repo_root(), M4_ALGEBRA))
    sub = m4.sub()
    elt = BasicSet([0])
    uacalc_lib.set_memory_limit(PYTHON_SUB_MEM_LOW)
    try:
        with pytest.raises(OutOfMemoryError):
            list(sub.universe())
        with pytest.raises(OutOfMemoryError):
            list(sub.filter(elt))
    finally:
        uacalc_lib.set_memory_limit(None)
    assert len(list(sub.universe())) == M4_SUB_CARD
    assert len(list(sub.filter(elt))) >= 1


def test_org_subalgebra_one_gens_and_join_irreducibles_out_of_memory():
    import org.uacalc.alg.sublat  # noqa: F401 — install shim methods on PySubalgebraLattice
    from org.uacalc.io import AlgebraIO

    m4 = AlgebraIO.readAlgebraFile(os.path.join(_repo_root(), M4_ALGEBRA))
    uacalc_lib.set_memory_limit(PYTHON_SUB_MEM_LOW)
    try:
        with pytest.raises(OutOfMemoryError):
            list(m4.sub().oneGeneratedSubalgebras())
        with pytest.raises(OutOfMemoryError):
            list(m4.sub().joinIrreducibles())
    finally:
        uacalc_lib.set_memory_limit(None)
    assert int(m4.sub().cardinality()) == M4_SUB_CARD


def test_org_con_lattice_cardinality_out_of_memory_and_recovery():
    from org.uacalc.io import AlgebraIO

    path = os.path.join(_repo_root(), LYNDON_ALGEBRA)
    lyndon = AlgebraIO.readAlgebraFile(path)
    con = lyndon.con()
    uacalc_lib.set_memory_limit(PYTHON_CON_MEM_LOW)
    try:
        with pytest.raises(OutOfMemoryError):
            int(con.cardinality())
    finally:
        uacalc_lib.set_memory_limit(None)
    card = int(con.cardinality())
    assert card >= LYNDON_CON_CARD_MIN
    assert int(con.cardinality()) == card


def test_lib_con_universe_lyndon_memory_and_recompute():
    con = _lyndon_lib_algebra().con()
    uacalc_lib.set_memory_limit(PYTHON_CON_MEM_LOW)
    try:
        with pytest.raises(MemoryError, match="memory limit"):
            con.con_cardinality()
    finally:
        uacalc_lib.set_memory_limit(None)
    card = con.con_cardinality()
    assert card >= LYNDON_CON_CARD_MIN
    assert con.con_cardinality() == card


def test_lib_con_universe_lyndon_element_limit_and_recovery():
    uacalc_lib.set_memory_limit(None)
    expected = _lyndon_lib_algebra().con().con_cardinality()
    uacalc_lib.set_element_limit(PYTHON_CON_ELEMENT_LOW)
    try:
        con = _lyndon_lib_algebra().con()
        with pytest.raises(MemoryError, match="element limit"):
            con.con_cardinality()
    finally:
        uacalc_lib.set_element_limit(None)
    assert _lyndon_lib_algebra().con().con_cardinality() == expected


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


def _parse_java_wrapper_json(combined: str) -> dict | None:
    idx = combined.rfind('"success"')
    if idx < 0:
        return None
    start = combined.rfind("{", 0, idx)
    if start < 0:
        return None
    depth = 0
    for pos in range(start, len(combined)):
        ch = combined[pos]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(combined[start : pos + 1])
                except json.JSONDecodeError:
                    return None
    return None


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
    payload = _parse_java_wrapper_json(combined)
    if payload is None:
        return (True, False, "no json")
    data = payload.get("data", payload)
    if isinstance(data, str):
        data = json.loads(data)
    ok = data.get("status") == "success"
    return (True, ok, "success" if ok else str(data.get("status")))


def _java_subalgebra_cardinality(xmx_mb: int) -> tuple[bool, bool, str]:
    """Return (ran_to_completion, success, detail)."""
    cmd = build_java_command(
        "java_wrapper.src.alg.sublat.SubalgebraLatticeWrapper",
        [
            "sub_cardinality_stress",
            "--algebra",
            os.path.join(_repo_root(), M4_ALGEBRA),
            "--copies",
            str(JAVA_SUB_STRESS_COPIES),
            "--reserve_mb",
            str(JAVA_SUB_STRESS_RESERVE_MB),
        ],
    )
    cmd.insert(1, f"-Xmx{xmx_mb}m")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=JAVA_SUBPROCESS_TIMEOUT_SEC,
            cwd=_repo_root(),
        )
    except subprocess.TimeoutExpired:
        return (False, False, "timeout")
    combined = (proc.stderr or "") + (proc.stdout or "")
    if "OutOfMemoryError" in combined:
        return (True, False, "oom")
    if proc.returncode != 0:
        return (True, False, f"exit {proc.returncode}")
    payload = _parse_java_wrapper_json(combined)
    if payload is None:
        return (True, False, "no json")
    data = payload.get("data", payload)
    if isinstance(data, str):
        data = json.loads(data)
    ok = data.get("status") == "success" and int(data.get("cardinality", 0)) == M4_SUB_CARD
    return (True, ok, "success" if ok else str(data))


def _java_con_cardinality(xmx_mb: int) -> tuple[bool, bool, str]:
    cmd = build_java_command(
        "java_wrapper.src.alg.conlat.CongruenceLatticeWrapper",
        ["con_cardinality", "--algebra", os.path.join(_repo_root(), LYNDON_ALGEBRA)],
    )
    cmd.insert(1, f"-Xmx{xmx_mb}m")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=JAVA_SUBPROCESS_TIMEOUT_SEC,
            cwd=_repo_root(),
        )
    except subprocess.TimeoutExpired:
        return (False, False, "timeout")
    combined = (proc.stderr or "") + (proc.stdout or "")
    if "OutOfMemoryError" in combined:
        return (True, False, "oom")
    if proc.returncode != 0:
        return (True, False, f"exit {proc.returncode}")
    payload = _parse_java_wrapper_json(combined)
    if payload is None:
        return (True, False, "no json")
    data = payload.get("data", payload)
    card = int(data.get("cardinality", 0))
    ok = card >= LYNDON_CON_CARD_MIN
    return (True, ok, f"card={card}")


@pytest.mark.slow
def test_java_subalgebra_vs_python_same_side_of_cutoff():
    if not os.environ.get("JAVA_HOME"):
        pytest.skip("JAVA_HOME not set")
    java_low_ran, java_low_ok, low_detail = _java_subalgebra_cardinality(JAVA_SUB_LOW_XMX_MB)
    java_high_ran, java_high_ok, high_detail = _java_subalgebra_cardinality(JAVA_SUB_HIGH_XMX_MB)
    assert java_low_ran and not java_low_ok, f"Java low -Xmx should OOM or fail: {low_detail}"
    assert java_high_ran and java_high_ok, f"Java high -Xmx should succeed: {high_detail}"

    m4 = _m4_lib_algebra()
    uacalc_lib.set_memory_limit(PYTHON_SUB_STRESS_MEM_LOW)
    try:
        with pytest.raises(MemoryError, match="memory limit"):
            m4.sub().cardinality()
    finally:
        uacalc_lib.set_memory_limit(None)

    uacalc_lib.set_memory_limit(PYTHON_SUB_MEM_HIGH)
    try:
        assert m4.sub().cardinality() == M4_SUB_CARD
    finally:
        uacalc_lib.set_memory_limit(None)


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