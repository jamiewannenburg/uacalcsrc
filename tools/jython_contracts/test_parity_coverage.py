"""Tests for parity coverage per-class matching and reporting."""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from jython_contracts.parity_coverage import (  # noqa: E402
    build_parity_coverage,
    format_parity_coverage,
    scan_behavioral_test_methods,
    scan_java_public_methods,
    scan_python_wrapper_methods,
)


@pytest.fixture()
def mini_pkg(tmp_path: Path, monkeypatch):
    """Two Java types sharing a method name; only one is wrapped and tested."""
    repo = tmp_path / "repo"
    (repo / "org" / "uacalc" / "demo").mkdir(parents=True)
    (repo / "python" / "org" / "uacalc" / "demo").mkdir(parents=True)
    (repo / "tests" / "parity" / "demo" / "golden_data").mkdir(parents=True)

    java_a = textwrap.dedent(
        """
        package org.uacalc.demo;
        public class Alpha {
            public int shared() { return 1; }
            public int onlyAlpha() { return 2; }
        }
        """
    )
    java_b = textwrap.dedent(
        """
        package org.uacalc.demo;
        public class Beta {
            public int shared() { return 3; }
            public int onlyBeta() { return 4; }
        }
        """
    )
    (repo / "org" / "uacalc" / "demo" / "Alpha.java").write_text(java_a, encoding="utf-8")
    (repo / "org" / "uacalc" / "demo" / "Beta.java").write_text(java_b, encoding="utf-8")

    py = textwrap.dedent(
        """
        class Alpha:
            def shared(self):
                return 1
            def onlyAlpha(self):
                return 2
        """
    )
    (repo / "python" / "org" / "uacalc" / "demo" / "_jython_compat.py").write_text(
        py, encoding="utf-8"
    )

    golden = {
        "test_cases": [
            {"method": "Alpha.shared", "args": [], "expected": 1},
            {"method": "Alpha.onlyAlpha", "args": [], "expected": 2},
        ]
    }
    (repo / "tests" / "parity" / "demo" / "golden_data" / "alpha_jython.json").write_text(
        json.dumps(golden), encoding="utf-8"
    )

    import jython_contracts.parity_coverage as pc

    monkeypatch.setattr(pc, "PROJECT_ROOT", repo)
    return repo


def test_java_scan_is_per_class():
    java = REPO_ROOT / "org" / "uacalc" / "lat" / "BasicLattice.java"
    if not java.is_file():
        pytest.skip("BasicLattice.java not in workspace")
    names = scan_java_public_methods(java)
    assert all("." in n for n in names)
    assert "BasicLattice.cardinality" in names or any(
        n.startswith("BasicLattice.") for n in names
    )


def test_python_scan_returns_qualified_keys():
    py = textwrap.dedent(
        """
        class Widget:
            def doThing(self):
                pass
            def __init__(self):
                pass
        """
    )
    path = Path(__file__).parent / "_tmp_widget.py"
    path.write_text(py, encoding="utf-8")
    try:
        got = scan_python_wrapper_methods(path)
        assert "Widget.doThing" in got
        assert "Widget.Widget" in got
    finally:
        path.unlink(missing_ok=True)


def test_shared_method_name_does_not_cross_classes(mini_pkg):
    report = build_parity_coverage(packages=["demo"])
    cov = report.by_package["demo"]
    assert "Alpha.shared" in cov.wrapped_methods
    assert "Beta.shared" not in cov.wrapped_methods
    assert "Beta.shared" in cov.unwrapped_methods
    assert "Alpha.shared" in cov.tested_methods
    assert "Beta.shared" not in cov.tested_methods


def test_format_lists_all_by_default(mini_pkg):
    report = build_parity_coverage(packages=["demo"])
    text = format_parity_coverage(
        report, show_unwrapped=True, show_untested=True, list_limit=None
    )
    assert "Beta.shared" in text
    assert "Beta.onlyBeta" in text


def test_format_respects_limit(mini_pkg):
    report = build_parity_coverage(packages=["demo"])
    text = format_parity_coverage(report, show_unwrapped=True, list_limit=1)
    assert "... and" in text


def test_behavioral_scan_keeps_class_prefix(mini_pkg):
    parity_dir = mini_pkg / "tests" / "parity" / "demo"
    tested = scan_behavioral_test_methods(parity_dir)
    assert "Alpha.shared" in tested
    assert "shared" not in tested


def test_comparison_allowlist_paths_exist():
    from jython_contracts.comparison_allowlist import KNOWN_OUTPUT_DIFFERENCES

    for path in KNOWN_OUTPUT_DIFFERENCES:
        assert (REPO_ROOT / path).is_file(), path