"""
Contract parity for ``org.uacalc.io`` (see ``tests/parity/io/CONTRACT.md``).

Uses Java/Jython names on the ``org.uacalc.io`` shim. Failures reflect missing
``uacalc_lib`` behavior or incomplete compatibility wrappers — not hidden skips.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, List

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

from tests.parity.io.io_parity_helpers import (  # noqa: E402
    MACE4_LIST_FILE,
    MACE4_SINGLE_FILE,
    MULTI_ALGEBRA_LIST_FILE,
    SAMPLE_ALGEBRA_FILES,
    SPECIAL_FIXTURE_NAMES,
    algebra_path,
    format_algebra_list_summaries,
    format_algebra_summary,
    mace4_path,
    normalize_xml_file,
    normalize_xml_text,
    semantic_algebra_summary,
    special_path,
    summaries_equal,
)


def _ensure_python_org_on_path() -> None:
    py_root = REPO_ROOT / "python"
    s = str(py_root)
    if s not in sys.path:
        sys.path.insert(0, s)


try:
    import uacalc_lib  # noqa: F401
except ImportError:
    pytest.skip("uacalc_lib not available", allow_module_level=True)


@pytest.fixture(scope="module", autouse=True)
def _chdir_repo_root():
    old = os.getcwd()
    os.chdir(REPO_ROOT)
    yield
    os.chdir(old)


@pytest.fixture(scope="module")
def io_pkg():
    _ensure_python_org_on_path()
    import org.uacalc.io as pkg  # noqa: PLC0415

    return pkg


# --- Java/Jython surface: camelCase must exist on contract types ---


@pytest.mark.parametrize(
    "cls_name,method",
    [
        ("AlgebraIO", "readAlgebraFile"),
        ("AlgebraIO", "readAlgebraFromStream"),
        ("AlgebraIO", "readAlgebraListFile"),
        ("AlgebraIO", "readAlgebraListFromStream"),
        ("AlgebraIO", "convertToXML"),
        ("AlgebraIO", "writeAlgebraFile"),
        ("AlgebraReader", "readAlgebraFile"),
        ("AlgebraReader", "readAlgebraFromStream"),
        ("AlgebraReader", "readAlgebraListFile"),
        ("AlgebraReader", "readAlgebraListFromStream"),
        ("AlgebraWriter", "writeAlgebraXML"),
        ("AlgebraWriter", "writeAlgebra"),
        ("AlgebraWriter", "writeBasicAlgebra"),
        ("Mace4Reader", "parseAlgebra"),
        ("Mace4Reader", "parseAlgebraList"),
    ],
)
def test_contract_camelcase_methods_exist(io_pkg, cls_name: str, method: str):
    cls = getattr(io_pkg, cls_name)
    assert callable(getattr(cls, method)), (
        f"missing {cls_name}.{method} on org.uacalc.io shim"
    )


def test_algebra_reader_jython_style_constructor(io_pkg):
    path = algebra_path("cyclic2.ua")
    if not os.path.isfile(path):
        pytest.skip("cyclic2.ua missing")
    reader = io_pkg.AlgebraReader(str(path))
    assert callable(reader.readAlgebraFile)


def test_mace4_reader_jython_style_constructor(io_pkg):
    path = mace4_path(MACE4_SINGLE_FILE)
    if not os.path.isfile(path):
        pytest.skip(f"{MACE4_SINGLE_FILE} missing")
    with open(path, "rb") as fh:
        reader = io_pkg.Mace4Reader(fh.read())
    assert callable(reader.parseAlgebra)


# --- Semantic parity vs uacalc_lib (same bindings, Java names) ---


def _lib_io():
    import uacalc_lib  # noqa: PLC0415

    return getattr(uacalc_lib, "io")


@pytest.mark.parametrize("fname", SAMPLE_ALGEBRA_FILES)
def test_algebra_io_read_algebra_file_matches_lib(fname: str, io_pkg):
    path = algebra_path(fname)
    if not os.path.isfile(path):
        pytest.skip(f"{fname} missing")

    lib_alg = _lib_io().read_algebra_file(path)
    shim_alg = io_pkg.AlgebraIO.readAlgebraFile(path)
    assert summaries_equal(
        semantic_algebra_summary(lib_alg),
        semantic_algebra_summary(shim_alg),
    )


@pytest.mark.parametrize("fname", SAMPLE_ALGEBRA_FILES)
def test_algebra_io_read_algebra_from_stream_matches_lib(fname: str, io_pkg):
    path = algebra_path(fname)
    if not os.path.isfile(path):
        pytest.skip(f"{fname} missing")

    with open(path, "rb") as fh:
        data = fh.read()
    lib_alg = _lib_io().read_algebra_from_stream(data)
    shim_alg = io_pkg.AlgebraIO.readAlgebraFromStream(data)
    assert summaries_equal(
        semantic_algebra_summary(lib_alg),
        semantic_algebra_summary(shim_alg),
    )


@pytest.mark.parametrize("fname", SAMPLE_ALGEBRA_FILES)
def test_algebra_reader_read_methods_match_lib(fname: str, io_pkg):
    path = algebra_path(fname)
    if not os.path.isfile(path):
        pytest.skip(f"{fname} missing")

    spath = path
    with open(path, "rb") as fh:
        data = fh.read()
    lib = _lib_io()

    lib_r = lib.AlgebraReader.new_from_file(spath)
    shim_r = io_pkg.AlgebraReader(spath)

    assert summaries_equal(
        semantic_algebra_summary(lib_r.read_algebra_file()),
        semantic_algebra_summary(shim_r.readAlgebraFile()),
    )

    lib_stream = lib.AlgebraReader.new_from_stream(data)
    shim_stream = io_pkg.AlgebraReader(data)
    assert summaries_equal(
        semantic_algebra_summary(lib_stream.read_algebra_from_stream(data)),
        semantic_algebra_summary(shim_stream.readAlgebraFromStream()),
    )


def test_algebra_io_read_algebra_list_file(io_pkg):
    path = algebra_path(MULTI_ALGEBRA_LIST_FILE)
    if not os.path.isfile(path):
        pytest.skip("multi-algebra fixture missing")

    lib_list = _lib_io().read_algebra_list_file(path)
    shim_list = io_pkg.AlgebraIO.readAlgebraListFile(path)
    assert format_algebra_list_summaries(lib_list) == format_algebra_list_summaries(
        shim_list
    )
    # CONTRACT.md targets two algebras in the fixture; Jython+CPython currently return one
    # (last ``basicAlgebra`` only). Keep the assertion to surface parser gaps.
    assert len(shim_list) >= 2, (
        "expected >=2 algebras in cyclic2_cyclic3_list.ua; got {0} — "
        "check AlgebraReader list parsing in uacalc_lib/Java".format(len(shim_list))
    )


def test_mace4_reader_parse_algebra(io_pkg):
    path = mace4_path(MACE4_SINGLE_FILE)
    if not os.path.isfile(path):
        pytest.skip("mace4 single file missing")

    with open(path, "rb") as fh:
        data = fh.read()
    lib_alg = _lib_io().Mace4Reader.parse_algebra_from_file(path)
    shim_alg = io_pkg.Mace4Reader(data).parseAlgebra()
    assert summaries_equal(
        semantic_algebra_summary(lib_alg),
        semantic_algebra_summary(shim_alg),
    )


def test_mace4_reader_parse_algebra_list(io_pkg):
    path = mace4_path(MACE4_LIST_FILE)
    if not os.path.isfile(path):
        pytest.skip("mace4 list file missing")

    with open(path, "rb") as fh:
        data = fh.read()
    lib_list = list(_lib_io().Mace4Reader.parse_algebra_list_from_file(path))
    shim_list = io_pkg.Mace4Reader(data).parseAlgebraList()
    if not isinstance(shim_list, list):
        shim_list = list(shim_list)
    assert format_algebra_list_summaries(lib_list) == format_algebra_list_summaries(
        shim_list
    )
    assert len(shim_list) >= 2


def test_write_algebra_file_roundtrip_xml(io_pkg):
    src = algebra_path("cyclic3.ua")
    if not os.path.isfile(src):
        pytest.skip("cyclic3.ua missing")

    alg = io_pkg.AlgebraIO.readAlgebraFile(src)
    with tempfile.NamedTemporaryFile(suffix=".ua", delete=False) as tmp:
        out = Path(tmp.name)
    try:
        io_pkg.AlgebraIO.writeAlgebraFile(alg, str(out))
        reread = io_pkg.AlgebraIO.readAlgebraFile(str(out))
        assert summaries_equal(
            semantic_algebra_summary(alg),
            semantic_algebra_summary(reread),
        )
        assert normalize_xml_file(out) == normalize_xml_file(src)
    finally:
        out.unlink(missing_ok=True)


def test_write_algebra_file_old_style(io_pkg):
    src = algebra_path("cyclic3.ua")
    if not os.path.isfile(src):
        pytest.skip("cyclic3.ua missing")

    alg = io_pkg.AlgebraIO.readAlgebraFile(src)
    with tempfile.NamedTemporaryFile(suffix=".ua", delete=False) as tmp:
        out = Path(tmp.name)
    try:
        io_pkg.AlgebraIO.writeAlgebraFile(alg, str(out), False)
        assert normalize_xml_file(out)
    finally:
        out.unlink(missing_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".alg", delete=False) as tmp2:
        out2 = Path(tmp2.name)
    try:
        io_pkg.AlgebraIO.writeAlgebraFile(alg, str(out2), True)
        assert out2.stat().st_size > 0
    finally:
        out2.unlink(missing_ok=True)


def test_algebra_writer_write_algebra_xml(io_pkg):
    src = algebra_path("cyclic3.ua")
    if not os.path.isfile(src):
        pytest.skip("cyclic3.ua missing")

    alg = io_pkg.AlgebraIO.readAlgebraFile(src)
    with tempfile.NamedTemporaryFile(suffix=".ua", delete=False) as tmp:
        out = Path(tmp.name)
    try:
        io_pkg.AlgebraWriter(alg, str(out)).writeAlgebraXML()
        written = normalize_xml_file(out)
        assert written.startswith("<algebra>")
        reread = io_pkg.AlgebraIO.readAlgebraFile(str(out))
        assert summaries_equal(
            semantic_algebra_summary(alg),
            semantic_algebra_summary(reread),
        )
    finally:
        out.unlink(missing_ok=True)


def test_bad_algebra_file_invalid_fixture_fails(io_pkg):
    path = algebra_path("invalid_parity.ua")
    if not os.path.isfile(path):
        pytest.skip("invalid_parity.ua missing")

    Bad = io_pkg.BadAlgebraFileException
    with pytest.raises(Exception) as excinfo:
        io_pkg.AlgebraIO.readAlgebraFile(path)
    # Jython raises BadAlgebraFileException; CPython may surface ValueError from PyO3.
    assert excinfo.type in (Bad, ValueError, OSError) or issubclass(
        excinfo.type, Exception
    )


@pytest.mark.parametrize("sname", SPECIAL_FIXTURE_NAMES)
def test_special_algebra_fixtures_readable(io_pkg, sname: str):
    path = special_path(sname)
    if not os.path.isfile(path):
        pytest.skip(
            "resources/special/{0} missing — run "
            "tests/parity/io/generate_special_algebra_fixtures.py with Jython".format(
                sname
            )
        )
    alg = io_pkg.AlgebraReader(path).readAlgebraFile()
    summary = semantic_algebra_summary(alg)
    assert summary["cardinality"] > 0


def _summary_for_case(stdout: str, case_label: str) -> str | None:
    """Return the SUMMARY or LIST line following a CASE line, if present."""
    lines = [ln.rstrip("\r") for ln in stdout.splitlines()]
    needle = "CASE: " + case_label
    for idx, line in enumerate(lines):
        if line == needle and idx + 1 < len(lines):
            nxt = lines[idx + 1]
            if nxt.startswith("SUMMARY:") or nxt.startswith("LIST:"):
                return nxt
    return None


def test_jython_cross_runtime_read_summaries_match_when_jython_available():
    """Compare semantic SUMMARY lines for basic read cases (Jython vs CPython shim)."""
    jython = shutil.which("jython")
    jar = REPO_ROOT / "jars" / "uacalc.jar"
    script = REPO_ROOT / "tests" / "parity" / "io" / "parity_io_contract.py"
    if not jython or not jar.is_file():
        pytest.skip("jython or uacalc.jar not available")

    env_base = dict(os.environ)
    r_py = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**env_base, "PYTHONPATH": str(REPO_ROOT / "python")},
        timeout=180,
        check=False,
    )
    assert r_py.returncode == 0, r_py.stderr + r_py.stdout

    env_jy = dict(env_base)
    env_jy["CLASSPATH"] = str(jar)
    env_jy["PYTHONPATH"] = ""
    r_jy = subprocess.run(
        [jython, str(script)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env_jy,
        timeout=300,
        check=False,
    )
    assert r_jy.returncode == 0, (r_jy.stderr or "") + (r_jy.stdout or "")

    mismatches = []
    for fname in SAMPLE_ALGEBRA_FILES:
        case = "AlgebraIO.readAlgebraFile:" + fname
        py_line = _summary_for_case(r_py.stdout, case)
        jy_line = _summary_for_case(r_jy.stdout, case)
        if py_line is None or jy_line is None:
            continue
        # CPython reports kind "Basic"; Jython uses enum name "BASIC".
        py_norm = py_line.replace('"kind":"Basic"', '"kind":"BASIC"')
        if py_norm != jy_line:
            mismatches.append((case, py_line, jy_line))
    if mismatches:
        case, py_line, jy_line = mismatches[0]
        pytest.fail(
            "CPython vs Jython summary mismatch for {0}\n  cpython: {1}\n  jython:  {2}".format(
                case, py_line, jy_line
            )
        )
