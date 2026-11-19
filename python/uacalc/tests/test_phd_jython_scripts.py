"""Compare CPython (org.uacalc) stdout against Jython/Java goldens for PhD scripts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tests" / "jython_scripts"))
from harness import (  # noqa: E402
    FIXTURES_ROOT,
    compare_phd_outputs,
    normalize_phd_output,
    run_phd_script_cpython,
)

PHD = REPO / "tests" / "jython_scripts" / "phd_runtime"
MANIFEST = REPO / "tests" / "jython_scripts" / "phd" / "manifest.json"
GOLDENS = REPO / "tests" / "jython_scripts" / "phd" / "goldens"


def _entries():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return data["scripts"]


def _case_id(entry: dict) -> str:
    return entry["path"]


@pytest.mark.parametrize("entry", _entries(), ids=_case_id)
def test_phd_script_stdout_matches_jython_golden(entry: dict):
    if entry.get("skip_cpython"):
        pytest.skip(entry["skip_cpython"])
    if entry.get("skip_jython_golden"):
        pytest.skip(entry["skip_jython_golden"])
    rel = entry["path"]
    compare_stdout = entry.get("compare_stdout", True)
    compare_files = entry.get("compare_files") or []
    if not compare_stdout and not compare_files:
        pytest.skip("no compare_stdout or compare_files")
    rel = entry["path"]
    golden_path = GOLDENS / (Path(rel).name + ".stdout")
    expected = ""
    if compare_stdout:
        assert golden_path.is_file(), (
            f"Missing golden {golden_path}; run tools/regenerate_phd_script_goldens.py"
        )
        expected = normalize_phd_output(golden_path.read_text(encoding="utf-8"))
    argv = list(entry.get("argv") or [])
    cwd = PHD
    if entry.get("cwd_fixture"):
        cwd = FIXTURES_ROOT
    fixture_root = FIXTURES_ROOT if entry.get("use_fixture_copy") else None
    rc, out, err, artifact_dir = run_phd_script_cpython(
        rel, argv, cwd=cwd, fixture_root=fixture_root
    )
    got = normalize_phd_output(out)
    xfail = entry.get("xfail_cpython")
    if xfail:
        if compare_stdout and (got != expected or rc != 0):
            pytest.xfail(xfail.get("reason", "known PhD script divergence"))
        if rc != 0:
            pytest.xfail(xfail.get("reason", "known PhD script divergence"))
        if compare_files:
            base = artifact_dir or (FIXTURES_ROOT if entry.get("cwd_fixture") else cwd)
            file_errors = compare_phd_outputs(entry, out, Path(base))
            if file_errors:
                pytest.xfail(xfail.get("reason", "known PhD script divergence"))
        return
    assert rc == 0, f"stderr:\n{err}"
    if compare_stdout:
        assert got == expected, _first_diff(expected, got)
    if compare_files:
        base = artifact_dir or (FIXTURES_ROOT if entry.get("cwd_fixture") else cwd)
        file_errors = compare_phd_outputs(entry, out, Path(base))
        assert not file_errors, "\n".join(file_errors)


def _first_diff(expected: str, got: str) -> str:
    el = expected.splitlines()
    gl = got.splitlines()
    for i, (e, g) in enumerate(zip(el, gl)):
        if e != g:
            return f"first differing line {i + 1}:\n  jython: {e!r}\n  cpython: {g!r}"
    if len(el) != len(gl):
        return f"line count jython={len(el)} cpython={len(gl)}"
    return "unknown diff"


@pytest.mark.parametrize("entry", [e for e in _entries() if e.get("slow")], ids=_case_id)
@pytest.mark.slow
def test_phd_script_slow(entry: dict):
    test_phd_script_stdout_matches_jython_golden(entry)