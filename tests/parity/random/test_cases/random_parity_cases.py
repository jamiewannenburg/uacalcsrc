"""Golden-case specs for randomized org.uacalc parity (one snapshot per CI seed)."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))
sys.path.insert(0, str(REPO_ROOT / "jython_comparison" / "scripts"))

from parity_test_base import TestCaseSpec
from random_parity_config import CI_SEEDS, DEFAULT_CASE_TIMEOUT, XFAILS, family_for_seed

_SETUP = r"""
import sys, os
sys.path.insert(0, os.path.join(REPO_ROOT, "jython_comparison", "scripts"))
from random_parity import run_seed
"""

_SEED_XFAIL = {}
for (_seed, _path), _reason in XFAILS.items():
    _SEED_XFAIL.setdefault(_seed, []).append((_path, _reason))


def _xfail_reason(seed):
    items = _SEED_XFAIL.get(int(seed))
    if not items:
        return None
    bits = [path + ": " + reason for path, reason in items]
    return "Random parity xfail seed {0}: {1}".format(seed, "; ".join(bits))


TEST_CASES = []
for _seed in CI_SEEDS:
    _n, _arities = family_for_seed(_seed)
    TEST_CASES.append(
        TestCaseSpec(
            id="random_seed_{0}".format(_seed),
            method="Algebras.makeRandomAlgebra",
            setup=_SETUP,
            call="run_seed({0})".format(_seed),
            description=(
                "Randomized parity snapshot seed {0} (n={1}, arities={2})"
            ).format(_seed, _n, list(_arities)),
            skip_string_check=True,
            timeout_seconds=DEFAULT_CASE_TIMEOUT,
            xfail_reason=_xfail_reason(_seed),
            notes="Whole-snapshot xfail only when every failing path is listed in XFAILS.",
        )
    )
