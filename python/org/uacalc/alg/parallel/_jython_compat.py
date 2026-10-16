"""Jython-facing helpers for ``org.uacalc.alg.parallel`` (CPython only).

Java ``Pool`` is an empty class with a package-private static ``ForkJoinPool``.
``SingleClose`` is a ForkJoin ``RecursiveTask`` whose public surface is the
constructors plus ``doOneStep``. Thread counts, timing, ProgressReport, and
the term map from a parallel pass are non-deterministic / internal — not
asserted here.
"""

from __future__ import annotations

from typing import Any

from org.uacalc._exceptions import NullPointerException, translate_illegal_argument


def _install(g: dict) -> None:
    _LibPool = g.get("Pool")
    _LibSingleClose = g.get("SingleClose")
    g["_LibPool"] = _LibPool
    g["_LibSingleClose"] = _LibSingleClose

    def _npe(msg: str = "") -> None:
        raise NullPointerException(msg)

    def _elts_found_value(elts_found: Any) -> Any:
        if elts_found is None:
            return 0
        if isinstance(elts_found, bool):
            return int(elts_found)
        if isinstance(elts_found, (int, float)):
            return int(elts_found)
        getter = getattr(elts_found, "get", None)
        if callable(getter):
            try:
                return getter()
            except TypeError:
                pass
        return elts_found

    class Pool(object):
        """Java ``org.uacalc.alg.parallel.Pool``: shared runtime placeholder."""

        fjPool = None

        def __init__(self) -> None:
            if _LibPool is not None:
                try:
                    self._inner = _LibPool()
                except TypeError:
                    self._inner = _LibPool
            else:
                self._inner = None

        @staticmethod
        def fj_pool() -> Any:
            if _LibPool is None:
                return "initialized"
            fn = getattr(_LibPool, "fj_pool", None)
            if callable(fn):
                return fn()
            return "initialized"

        @staticmethod
        def is_initialized() -> bool:
            if _LibPool is None:
                return True
            fn = getattr(_LibPool, "is_initialized", None)
            if callable(fn):
                return bool(fn())
            return True

        def toString(self) -> str:
            return str(self)

        def __str__(self) -> str:
            return "Pool()"

        def __repr__(self) -> str:
            return "Pool()"

    class SingleClose(object):
        """Java ``SingleClose`` constructor + ``doOneStep``.

        Scripts pass a universe list, term map (dict), operation, min/max, and
        an element counter. ForkJoinPool / Thread / ProgressReport / CloserTiming
        arguments to ``doOneStep`` are accepted and ignored (internal).
        """

        def __init__(
            self,
            univList: Any,
            map: Any,
            op: Any,
            min: Any,
            max: Any,
            eltsFound: Any,
            inc: Any = None,
        ) -> None:
            if univList is None or op is None:
                _npe()
            self.univList = list(univList)
            self.map = map
            self.op = op
            self.min = int(min)
            self.max = int(max)
            self.eltsFound = eltsFound
            self._inner = None
            if _LibSingleClose is None:
                return
            try:
                self._inner = _LibSingleClose(
                    self.univList,
                    map,
                    op,
                    self.min,
                    self.max,
                    _elts_found_value(eltsFound),
                )
            except Exception as exc:
                if isinstance(exc, (TypeError, ValueError, NullPointerException)):
                    if "null" in str(exc).lower() or univList is None or op is None:
                        _npe(str(exc))
                    translate_illegal_argument(exc)
                raise

        def doOneStep(
            self,
            pool: Any = None,
            callingThread: Any = None,
            report: Any = None,
            timing: Any = None,
        ) -> Any:
            if self._inner is None:
                raise TypeError("SingleClose is not bound")
            fn = getattr(self._inner, "doOneStep", None) or getattr(
                self._inner, "do_one_step", None
            )
            if not callable(fn):
                raise TypeError("doOneStep is not bound")
            try:
                return fn(pool, callingThread, report, timing)
            except TypeError:
                return fn()

        def toString(self) -> str:
            return str(self)

        def __str__(self) -> str:
            return "SingleClose(min={0}, max={1})".format(self.min, self.max)

        def __repr__(self) -> str:
            return str(self)

    g["Pool"] = Pool
    g["SingleClose"] = SingleClose
