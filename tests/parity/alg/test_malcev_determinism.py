"""Run Malcev methods several times to prove deterministic results."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _ensure_python_org_on_path() -> None:
    py_root = REPO_ROOT / "python"
    s = str(py_root)
    if s not in sys.path:
        sys.path.insert(0, s)


# Full term-finding suite on tiny SI algebras. z3/polin only run cheap probes
# (F(2)^4 / path search on polin is too large for a 5-repeat loop).
_FULL = ("cyclic2.ua", "cyclic3.ua", "lat2.ua")
_CHEAP = ("z3.ua", "polin.ua")
_REPEATS = 5


def _term(t):
    if t is None:
        return None
    if isinstance(t, (list, tuple)):
        return [_term(x) for x in t]
    return str(t).replace(" ", "")


def _full_probes(Malcev, alg):
    return (
        ("malcevTerm", lambda: _term(Malcev.malcevTerm(alg))),
        ("majorityTerm", lambda: _term(Malcev.majorityTerm(alg))),
        ("minorityTerm", lambda: _term(Malcev.minorityTerm(alg))),
        ("jonssonTerms", lambda: _term(Malcev.jonssonTerms(alg))),
        ("jonssonLevel", lambda: Malcev.jonssonLevel(alg)),
        ("sdmeetTerms", lambda: _term(Malcev.sdmeetTerms(alg))),
        ("congruenceModularVariety", lambda: Malcev.congruenceModularVariety(alg)),
    )


def _cheap_probes(Malcev, alg):
    return (
        ("malcevTerm", lambda: _term(Malcev.malcevTerm(alg))),
        ("congruenceModularVariety", lambda: Malcev.congruenceModularVariety(alg)),
        ("sdmeetTerms", lambda: _term(Malcev.sdmeetTerms(alg))),
    )


@pytest.mark.parametrize("ua_name", list(_FULL) + list(_CHEAP))
def test_malcev_methods_are_deterministic(ua_name):
    _ensure_python_org_on_path()
    from org.uacalc.alg import Malcev  # noqa: PLC0415
    from org.uacalc.io import AlgebraIO  # noqa: PLC0415

    alg = AlgebraIO.readAlgebraFile(str(REPO_ROOT / "resources" / "algebras" / ua_name))
    probes = _full_probes(Malcev, alg) if ua_name in _FULL else _cheap_probes(Malcev, alg)
    for name, thunk in probes:
        first = thunk()
        for i in range(1, _REPEATS):
            again = thunk()
            assert again == first, "{0} on {1} changed on run {2}: {3!r} vs {4!r}".format(
                name, ua_name, i + 1, first, again
            )
