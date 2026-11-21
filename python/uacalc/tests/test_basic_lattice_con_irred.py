"""Parity tests for BasicLattice join/meet irreducibles on congruence lattices."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import uacalc_lib
from test_utils import build_java_command, get_project_root

sys.path.insert(0, str(Path(__file__).parent.parent))

BasicAlgebra = uacalc_lib.alg.BasicAlgebra
CongruenceLattice = uacalc_lib.alg.CongruenceLattice
BasicLattice = uacalc_lib.lat.BasicLattice
Partition = uacalc_lib.alg.Partition
AlgebraReader = uacalc_lib.io.AlgebraReader

PROJECT_ROOT = get_project_root()
N5_PATH = PROJECT_ROOT / "resources" / "algebras" / "n5.ua"


def canonical_partition(p) -> tuple[tuple[int, ...], ...]:
    blocks = p.get_blocks()
    normalized = [tuple(sorted(b)) for b in blocks]
    return tuple(sorted(normalized))


def parse_java_irred_sections(stdout: str) -> tuple[set[tuple[tuple[int, ...], ...]], set[tuple[tuple[int, ...], ...]]]:
    """Parse DumpN5Irred output into canonical partition sets."""

    def parse_blocks_line(line: str) -> tuple[tuple[int, ...], ...]:
        # Each line is like "[0, 1]|[2, 3]" with blocks sorted lexicographically.
        parts = line.strip().split("|")
        blocks = []
        for part in parts:
            inner = part.strip()
            if inner.startswith("[") and inner.endswith("]"):
                inner = inner[1:-1].strip()
            if not inner:
                continue
            nums = tuple(int(x.strip()) for x in inner.split(",") if x.strip())
            blocks.append(nums)
        return tuple(sorted(blocks))

    join_set: set[tuple[tuple[int, ...], ...]] = set()
    meet_set: set[tuple[tuple[int, ...], ...]] = set()
    section = None
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if line == "JOIN_IRREDUCIBLES":
            section = "join"
            continue
        if line == "MEET_IRREDUCIBLES":
            section = "meet"
            continue
        # CongruenceLattice construction prints diagnostic lines to stdout.
        if not line.startswith("["):
            continue
        parsed = parse_blocks_line(line)
        if section == "join":
            join_set.add(parsed)
        elif section == "meet":
            meet_set.add(parsed)
    return join_set, meet_set


def run_java_dump(algebra_path: Path) -> tuple[set[tuple[tuple[int, ...], ...]], set[tuple[tuple[int, ...], ...]]]:
    rel = algebra_path.relative_to(PROJECT_ROOT).as_posix()
    cmd = build_java_command("DumpN5Irred", [rel])
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        pytest.fail(
            f"DumpN5Irred failed (exit {result.returncode}):\n{result.stderr}\n{result.stdout}"
        )
    return parse_java_irred_sections(result.stdout)


def load_n5_algebra():
    if not N5_PATH.is_file():
        pytest.skip(f"{N5_PATH} not found")
    reader = AlgebraReader.new_from_file(str(N5_PATH))
    return reader.read_algebra_file()


def basic_lattice_from_congruence(alg) -> BasicLattice:
    con_lat = CongruenceLattice(alg)
    basic = BasicLattice("n5", con_lat, False)
    return basic


@pytest.fixture
def n5_basic_lattice() -> BasicLattice:
    return basic_lattice_from_congruence(load_n5_algebra())


def test_congruence_basic_lattice_irreducibles_match_java(n5_basic_lattice: BasicLattice):
    java_join, java_meet = run_java_dump(N5_PATH)

    join_irr = n5_basic_lattice.join_irreducibles()
    meet_irr = n5_basic_lattice.meet_irreducibles()

    assert join_irr, "join_irreducibles() should be non-empty for n5 congruence lattice"
    assert meet_irr, "meet_irreducibles() should be non-empty for n5 congruence lattice"

    for p in join_irr:
        assert isinstance(p, Partition), "join_irreducibles must return Partition elements"
    for p in meet_irr:
        assert isinstance(p, Partition), "meet_irreducibles must return Partition elements"

    py_join = {canonical_partition(p) for p in join_irr}
    py_meet = {canonical_partition(p) for p in meet_irr}

    assert py_join == java_join, f"join_irreducibles mismatch:\n  py={py_join}\n  java={java_join}"
    assert py_meet == java_meet, f"meet_irreducibles mismatch:\n  py={py_meet}\n  java={java_meet}"


def test_congruence_basic_lattice_join_irreducibles_parity_with_meet(n5_basic_lattice: BasicLattice):
    """join_irreducibles Partition binding sanity (already implemented; assert returns Partitions)."""
    jis = n5_basic_lattice.join_irreducibles()
    assert jis
    assert all(isinstance(p, Partition) for p in jis)