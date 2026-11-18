"""Resource limit APIs and Python exception mapping."""

import pytest

import uacalc_lib
from org.uacalc._exceptions import OutOfMemoryError


def test_limit_setters_exported():
    for name in (
        "set_memory_limit",
        "set_element_limit",
        "set_time_limit",
        "cancel",
        "clear_cancel",
    ):
        assert hasattr(uacalc_lib, name)


def test_huge_table_memory_error():
    Operations = uacalc_lib.alg.Operations
    uacalc_lib.clear_cancel()
    uacalc_lib.set_memory_limit(64)
    with pytest.raises(ValueError, match="memory limit"):
        Operations.make_int_operation("f", 2, 500, [0] * (500 * 500))


def test_org_shim_out_of_memory_translation():
    Operations = uacalc_lib.alg.Operations
    uacalc_lib.clear_cancel()
    uacalc_lib.set_memory_limit(64)

    def _lib_call(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError as exc:
            if "memory limit" in str(exc).lower():
                raise OutOfMemoryError(str(exc)) from exc
            raise
        except MemoryError as exc:
            raise OutOfMemoryError(str(exc)) from exc

    with pytest.raises(OutOfMemoryError):
        _lib_call(Operations.make_int_operation, "g", 2, 400, [0] * (400 * 400))