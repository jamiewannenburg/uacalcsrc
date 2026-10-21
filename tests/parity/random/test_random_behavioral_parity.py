"""Randomized behavioral parity: CPython snapshots vs Java/Jython goldens."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests" / "parity"))
sys.path.insert(0, str(REPO_ROOT / "jython_comparison" / "scripts"))

from parity_test_base import BehavioralParityTest
from random_parity_config import KNOWN_JAVA_NPE_PATHS, LIBRARY_BUG_PREFIXES, XFAILS
from tests.parity.random.test_cases.random_parity_cases import TEST_CASES

pytestmark = pytest.mark.behavioral


def _walk_diffs(actual, expected, prefix=""):
    diffs = []
    if type(actual) != type(expected) and not (
        isinstance(actual, (int, type(None))) and isinstance(expected, (int, type(None)))
    ):
        if actual != expected:
            diffs.append((prefix or "<root>", actual, expected))
        return diffs
    if isinstance(expected, dict) and isinstance(actual, dict):
        keys = sorted(set(list(expected.keys()) + list(actual.keys())))
        for key in keys:
            path = prefix + "." + key if prefix else key
            if key not in actual:
                diffs.append((path, "<missing>", expected[key]))
            elif key not in expected:
                diffs.append((path, actual[key], "<missing>"))
            else:
                diffs.extend(_walk_diffs(actual[key], expected[key], path))
        return diffs
    if isinstance(expected, list) and isinstance(actual, list):
        n = max(len(actual), len(expected))
        for i in range(n):
            path = "{0}[{1}]".format(prefix, i)
            if i >= len(actual):
                diffs.append((path, "<missing>", expected[i]))
            elif i >= len(expected):
                diffs.append((path, actual[i], "<missing>"))
            else:
                diffs.extend(_walk_diffs(actual[i], expected[i], path))
        return diffs
    if actual != expected:
        diffs.append((prefix or "<root>", actual, expected))
    return diffs


def _xfails_for_seed(seed):
    return {path: reason for (s, path), reason in XFAILS.items() if int(s) == int(seed)}


def _is_npe(value):
    return isinstance(value, dict) and value.get("error") == "NullPointerException"


def _known_java_npe(path, actual, expected):
    """Java-only NPE on a listed path is a known Java ProgressReport bug."""
    if path not in KNOWN_JAVA_NPE_PATHS:
        return False
    if _is_npe(expected) and not _is_npe(actual):
        return True
    return False


def _library_bug_path(path):
    for prefix in LIBRARY_BUG_PREFIXES:
        if path == prefix or path.startswith(prefix + ".") or path.startswith(prefix + "["):
            return True
    return False


class TestRandomBehavioralParity(BehavioralParityTest):
    package = "random"
    golden_file = "random_jython.json"

    def assert_snapshot(self, seed, actual, expected):
        diffs = _walk_diffs(actual, expected)
        xfails = _xfails_for_seed(seed)
        unexpected = []
        unused = set(xfails)
        for path, act, exp in diffs:
            reason = xfails.get(path)
            if reason is None:
                # Allow prefix xfails (e.g. "con.typeSet" covers nested paths).
                matched = None
                for key, why in xfails.items():
                    if path == key or path.startswith(key + ".") or path.startswith(key + "["):
                        matched = key
                        reason = why
                        break
                if matched is not None:
                    unused.discard(matched)
                    continue
                if _known_java_npe(path, act, exp):
                    continue
                if _library_bug_path(path):
                    continue
                unexpected.append((path, act, exp))
            else:
                unused.discard(path)
        # Strict xfails: listed paths must still mismatch.
        unused_msgs = []
        for path in sorted(unused):
            unused_msgs.append(
                "{0}: listed xfail no longer mismatches ({1})".format(path, xfails[path])
            )
        if unexpected or unused_msgs:
            parts = []
            for path, act, exp in unexpected[:20]:
                parts.append(
                    "{0}\n  python: {1}\n  java:   {2}".format(
                        path,
                        json.dumps(act, sort_keys=True, default=str),
                        json.dumps(exp, sort_keys=True, default=str),
                    )
                )
            if len(unexpected) > 20:
                parts.append("... {0} more mismatches".format(len(unexpected) - 20))
            parts.extend(unused_msgs)
            self.fail(
                "random seed {0}: {1} mismatch(es)\n{2}".format(
                    seed, len(unexpected), "\n".join(parts)
                )
            )


def _bind(case, seed):
    def test(self):
        expected_case = self.test_cases_by_id[case.id]
        timeout = expected_case.get("timeout_seconds") or case.timeout_seconds
        if timeout:
            actual_result = self._execute_case_with_timeout(expected_case, float(timeout))
        else:
            actual_result = self._execute_case(expected_case)
        self.assertTrue(
            actual_result.success,
            "{0}: exception {1}: {2}".format(
                case.id, actual_result.exception_type, actual_result.exception_message
            ),
        )
        from parity_test_base import serialize_for_golden

        actual = serialize_for_golden(actual_result.return_value)
        expected = expected_case["result"].get("return_value")
        self.assert_snapshot(seed, actual, expected)

    test.__name__ = "test_{0}".format(case.id)
    test.__doc__ = case.description
    if case.xfail_reason and not _xfails_for_seed(seed):
        test = pytest.mark.xfail(reason=case.xfail_reason, strict=True)(test)
    return test


for _case in TEST_CASES:
    _seed = int(_case.id.rsplit("_", 1)[-1])
    setattr(
        TestRandomBehavioralParity,
        "test_{0}".format(_case.id),
        _bind(_case, _seed),
    )


LIVE_COUNT = os.environ.get("RANDOM_PARITY_SEEDS")
LIVE_START = int(os.environ.get("RANDOM_PARITY_SEED_START") or "0")


@pytest.mark.skipif(
    not LIVE_COUNT,
    reason="Set RANDOM_PARITY_SEEDS=N to run extra seeds against live Java",
)
def test_live_java_extra_seeds(tmp_path):
    """Optional local sweep: CPython run_seed vs one Jython batch."""
    count = int(LIVE_COUNT)
    from random_parity import run_seed
    from tools.generate_golden_data import build_classpath, find_jython, extract_json
    import subprocess
    import textwrap

    jython = find_jython()
    if not jython:
        pytest.skip("Jython not found")
    script = textwrap.dedent(
        """
        import json, sys, os
        sys.path.insert(0, os.path.join({root!r}, "jython_comparison", "scripts"))
        from random_parity import run_seed
        start = int(sys.argv[1]); count = int(sys.argv[2])
        out = []
        for seed in range(start, start + count):
            out.append({{"seed": seed, "result": run_seed(seed)}})
        print("---GOLDEN_JSON_BEGIN---")
        print(json.dumps(out))
        print("---GOLDEN_JSON_END---")
        """
    ).format(root=str(REPO_ROOT))
    path = tmp_path / "live_random_parity.py"
    path.write_text(script, encoding="utf-8")
    env = os.environ.copy()
    env["CLASSPATH"] = build_classpath()
    env["PYTHONPATH"] = ""
    proc = subprocess.run(
        [jython, str(path), str(LIVE_START), str(count)],
        capture_output=True,
        text=True,
        timeout=max(120, 8 * count),
        env=env,
        cwd=str(REPO_ROOT),
    )
    java_rows = extract_json(proc.stdout)
    java_by_seed = {int(row["seed"]): row["result"] for row in java_rows}
    failures = []
    for seed in range(LIVE_START, LIVE_START + count):
        py = run_seed(seed)
        java = java_by_seed.get(seed)
        if java is None:
            failures.append("seed {0}: missing Java result".format(seed))
            continue
        diffs = _walk_diffs(py, java)
        xfails = _xfails_for_seed(seed)
        unexpected = []
        for path, act, exp in diffs:
            if path in xfails:
                continue
            if any(
                path == key or path.startswith(key + ".") or path.startswith(key + "[")
                for key in xfails
            ):
                continue
            if _known_java_npe(path, act, exp):
                continue
            if _library_bug_path(path):
                continue
            unexpected.append(path)
        if unexpected:
            failures.append(
                "seed {0}: {1}".format(seed, ", ".join(unexpected[:12]))
            )
    assert not failures, "live Java mismatches:\n" + "\n".join(failures[:40])
