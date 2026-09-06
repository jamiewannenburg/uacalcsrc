"""Compatibility shim for ``org.uacalc.alg.sublat``.

CPython: ``SubalgebraLattice`` lives on ``uacalc_lib.alg``; re-export it here so
``from org.uacalc.alg.sublat import SubalgebraLattice`` matches Jython.
"""


def _load_cp() -> None:
    import org.uacalc.alg as _alg

    if hasattr(_alg, "SubalgebraLattice"):
        globals()["SubalgebraLattice"] = _alg.SubalgebraLattice

    _CLASS_ALIASES = {
        "SubalgebraLattice": {
            "iterator": "iterator",
            "Sg": "sg",
        },
    }
    globals()["_CLASS_ALIASES"] = _CLASS_ALIASES


if __import__("sys").platform.startswith("java"):
    from org.uacalc.alg.sublat import *  # noqa: F403
else:
    _load_cp()
    del _load_cp
