"""
Tests aligned with Jython example scripts under jython_comparison/.

Covers the same APIs as:
- jython_comparison/test_script.py  (org.uacalc.io.AlgebraIO, org.uacalc.alg.*)
- jython_comparison/debug_jython.py (same, plus introspection)
- jython_comparison/subreducts_mace4_stream.py (Mace4Reader, Terms.stringToTerm,
  ReductAlgebra, subalgebra lattice from algebra.sub()) — CPython uses the same
  Rust-backed types via uacalc_lib; the Jython script uses SubalgebraLattice(alg)
  and iterator(), which are not all exposed identically in Python yet.

Also smoke-tests parity manifest tooling (validate script + inventory builder).
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Tests run with cwd = repo root (see conftest / pytest from project root).
REPO_ROOT = Path(__file__).resolve().parents[3]


def _ensure_python_org_on_path() -> None:
    """So ``import org.uacalc...`` resolves to python/org/."""
    py_root = REPO_ROOT / "python"
    s = str(py_root)
    if s not in sys.path:
        sys.path.insert(0, s)


def _load_generate_inventory_module():
    path = REPO_ROOT / "jython_comparison" / "scripts" / "generate_parity_inventory.py"
    spec = importlib.util.spec_from_file_location(
        "uacalc_generate_parity_inventory", path
    )
    if spec is None or spec.loader is None:
        pytest.fail(f"Could not load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


try:
    import uacalc_lib  # noqa: F401
except ImportError:
    pytest.skip("uacalc_lib not available", allow_module_level=True)


@pytest.fixture(scope="module", autouse=True)
def change_to_repo_root():
    """Resources use paths like resources/algebras/... relative to repo root."""
    old = os.getcwd()
    os.chdir(REPO_ROOT)
    yield
    os.chdir(old)


class TestJythonTestScriptParity:
    """Mirrors jython_comparison/test_script.py on CPython + org.uacalc shims."""

    def test_algebra_io_and_alg_cyclic2_matches_direct_lib(self):
        """Same algebra facts as test_script.py; compares org.uacalc to uacalc_lib."""
        ua_path = REPO_ROOT / "resources" / "algebras" / "cyclic2.ua"
        if not ua_path.is_file():
            pytest.skip("resources/algebras/cyclic2.ua not found")

        io = getattr(uacalc_lib, "io")
        reader = io.AlgebraReader.new_from_file(str(ua_path))
        direct = reader.read_algebra_file()

        _ensure_python_org_on_path()
        from org.uacalc.io import AlgebraIO  # pylint: disable=import-outside-toplevel

        shim = AlgebraIO.readAlgebraFile(str(ua_path))

        assert shim.name() == direct.name() == "C2"
        assert shim.cardinality() == direct.cardinality() == 2
        assert shim.con().cardinality() == direct.con().cardinality() == 2
        # run_comparison.py excludes Universe: line for Jython vs CPython; compare as sets.
        # PyO3 classes may not accept runtime camelCase aliases; semantic API is get_universe_list.
        assert (
            set(shim.get_universe_list()) == set(direct.get_universe_list()) == {0, 1}
        )

    def test_star_import_org_uacalc_alg_exports_core_types(self):
        """Ensure ``dir(org.uacalc.alg)`` exposes types re-exported from uacalc_lib (Jython style)."""
        _ensure_python_org_on_path()
        import org.uacalc.alg as alg_pkg  # pylint: disable=import-outside-toplevel

        ns = org_uacalc_alg_star()
        assert "BasicAlgebra" in ns
        # SmallAlgebra is a Java type name; bindings expose concrete algebras as BasicAlgebra.
        assert ns["BasicAlgebra"] is getattr(alg_pkg, "BasicAlgebra")


def org_uacalc_alg_star() -> dict:
    """Populate dict like ``from org.uacalc.alg import *`` (no exec)."""
    _ensure_python_org_on_path()
    import org.uacalc.alg as alg_pkg  # pylint: disable=import-outside-toplevel

    out = {}
    for name in dir(alg_pkg):
        if not name.startswith("_"):
            out[name] = getattr(alg_pkg, name)
    return out


class TestSubreductsMace4ExampleAPIs:
    """APIs exercised by subreducts_mace4_stream.py (CPython / uacalc_lib)."""

    def test_parse_mace4_algebra_and_terms_string_to_term(self):
        path = REPO_ROOT / "resources" / "mace4" / "KR-8-expl.model"
        if not path.is_file():
            pytest.skip("KR-8-expl.model not found")

        io = getattr(uacalc_lib, "io")
        terms = getattr(uacalc_lib, "terms")
        Mace4Reader = io.Mace4Reader

        alg = Mace4Reader.parse_algebra_from_file(str(path))
        assert alg.name() == "model1"
        assert alg.cardinality() == 8

        # Jython uses Terms.stringToTerm on CLI tokens; same underlying parser.
        t1 = terms.string_to_term("join")
        t2 = terms.string_to_term("meet")
        assert t1 is not None and t2 is not None

    def test_reduct_sub_smoke_matches_subreducts_workflow(self):
        """
        Jython builds SubalgebraLattice(ReductAlgebra(...)); in Python bindings use
        ``reduct.sub()`` (SmallAlgebra provides sub()).
        """
        path = REPO_ROOT / "resources" / "mace4" / "KR-8-expl.model"
        if not path.is_file():
            pytest.skip("KR-8-expl.model not found")

        io = getattr(uacalc_lib, "io")
        alg_mod = getattr(uacalc_lib, "alg")
        Mace4Reader = io.Mace4Reader
        ReductAlgebra = alg_mod.ReductAlgebra

        a = Mace4Reader.parse_algebra_from_file(str(path))
        reduct = ReductAlgebra(a, ["join", "meet"])
        sub_lat = reduct.sub()
        assert sub_lat.cardinality() >= 1


class TestParityTooling:
    """Verify jython_comparison manifest scripts run cleanly."""

    def test_validate_parity_slices_subprocess(self):
        script = REPO_ROOT / "jython_comparison" / "scripts" / "validate_parity_slices.py"
        r = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        assert r.returncode == 0, r.stderr + r.stdout

    def test_generate_parity_inventory_build_inventory_smoke(self):
        mod = _load_generate_inventory_module()
        inv = mod.build_inventory(REPO_ROOT)
        assert "meta" in inv and "types" in inv
        assert inv["meta"]["java_org_uacalc_files_scanned"] > 0

    def test_generate_parity_inventory_verify_current_tree(self):
        mod = _load_generate_inventory_module()
        code = mod.verify_fresh(REPO_ROOT)
        assert code == 0, (
            "parity_inventory.yaml missing or stale; run: "
            "python jython_comparison/scripts/generate_parity_inventory.py"
        )
