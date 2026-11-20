"""Tests for narrow Jython/CPython comparison overrides (not whole-script allowlists)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from jython_comparison.run_comparison import compare_outputs  # noqa: E402


def test_random_parity_ignores_only_basicset_union_json_path():
    base = {
        "basicset": {
            "union": {"elements": [0, 2, 3], "string": "[0, 2, 3]"},
            "intersection": {"elements": [0]},
        },
        "seed": 0,
    }
    j_out = json.dumps({**base, "basicset": {**base["basicset"], "union": {"elements": [0, 2, 3]}}}, sort_keys=True)
    p_out = json.dumps(
        {
            **base,
            "basicset": {
                **base["basicset"],
                "union": {"elements": [0, 1, 2, 3], "string": "[0, 1, 2, 3]"},
            },
        },
        sort_keys=True,
    )
    match, _, _ = compare_outputs(
        j_out,
        p_out,
        ignore_json_paths=["basicset.union"],
    )
    assert match


def test_random_parity_union_ignored_with_jython_debug_prefix_lines():
    """Jython may print Java progress lines before the JSON snapshot line."""
    payload = {
        "basicset": {
            "union": {"elements": [0], "string": "[0]"},
            "seed_marker": 0,
        },
        "seed": 0,
    }
    j_payload = dict(payload)
    j_payload["basicset"] = {**payload["basicset"], "union": {"elements": [0], "string": "[0]"}}
    p_payload = dict(payload)
    p_payload["basicset"] = {
        **payload["basicset"],
        "union": {"elements": [0, 1], "string": "[0, 1]"},
    }
    j_out = "oneGenerated size = 2\n" + json.dumps(j_payload, sort_keys=True)
    p_out = json.dumps(p_payload, sort_keys=True)
    match, _, _ = compare_outputs(
        j_out,
        p_out,
        ignore_rules=[r"^oneGenerated size = \d+$"],
        ignore_json_paths=["basicset.union"],
    )
    assert match


def test_random_parity_non_union_json_diff_still_fails():
    j_out = json.dumps(
        {
            "basicset": {"union": {"elements": [0, 1]}},
            "seed": 1,
        },
        sort_keys=True,
    )
    p_out = json.dumps(
        {
            "basicset": {"union": {"elements": [0, 1]}},
            "seed": 2,
        },
        sort_keys=True,
    )
    match, _, _ = compare_outputs(
        j_out,
        p_out,
        ignore_json_paths=["basicset.union"],
    )
    assert not match


def test_basic_set_ops_ignores_only_union_line():
    j_out = "inter=[1, 3]\nunion=[0, 2, 3]\n"
    p_out = "inter=[1, 3]\nunion=[0, 1, 2, 3]\n"
    match, _, _ = compare_outputs(
        j_out,
        p_out,
        ignore_rules=[r"^union=.*"],
    )
    assert match


def test_basic_set_ops_other_line_mismatch_still_fails():
    j_out = "inter=[1, 3]\nunion=[0, 2, 3]\n"
    p_out = "inter=[9]\nunion=[0, 1, 2, 3]\n"
    match, _, _ = compare_outputs(
        j_out,
        p_out,
        ignore_rules=[r"^union=.*"],
    )
    assert not match