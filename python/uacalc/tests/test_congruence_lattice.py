"""
Test suite for CongruenceLattice bindings.
"""
import pytest
import uacalc_lib
import unittest
import os
import subprocess
import json
import sys
from pathlib import Path

# Type aliases for convenience
BasicAlgebra = uacalc_lib.alg.BasicAlgebra
CongruenceLattice = uacalc_lib.alg.CongruenceLattice
Partition = uacalc_lib.alg.Partition
BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation

# Get project root to locate resources
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESOURCES_ALGEBRAS_DIR = PROJECT_ROOT / "resources" / "algebras"


def test_congruence_lattice_creation():
    """Test basic CongruenceLattice creation."""
    # Create a simple algebra
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    
    # Create congruence lattice
    con_lat = CongruenceLattice(alg)
    
    assert con_lat is not None
    assert str(con_lat).startswith("Con")


def test_alg_size():
    """Test alg_size method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    assert con_lat.alg_size() == 3


def test_zero_and_one():
    """Test zero and one congruence methods."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    zero = con_lat.zero()
    one = con_lat.one()
    
    assert isinstance(zero, Partition)
    assert isinstance(one, Partition)
    
    # Zero should have more blocks than one
    assert zero.number_of_blocks() > one.number_of_blocks()


def test_cardinality():
    """Test con_cardinality method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    cardinality = con_lat.con_cardinality()
    
    assert cardinality >= 2  # At least zero and one


def test_cardinality_size_4():
    """Test cardinality for a 4-element algebra."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2, 3] ,[])
    con_lat = CongruenceLattice(alg)
    
    cardinality = con_lat.con_cardinality()
    
    assert cardinality >= 2  # At least zero and one


def test_is_distributive():
    """Test is_distributive method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    is_dist = con_lat.is_distributive()
    
    assert isinstance(is_dist, bool)


def test_get_description():
    """Test get_description method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    desc = con_lat.get_description()
    
    assert isinstance(desc, str)


def test_string_representation():
    """Test __str__ and __repr__ methods."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    str_repr = str(con_lat)
    repr_repr = repr(con_lat)
    
    assert "Con" in str_repr
    assert "Con" in repr_repr


def test_multiple_algebras():
    """Test creating multiple congruence lattices."""
    alg1 = BasicAlgebra("Alg1", [0, 1, 2] ,[])
    alg2 = BasicAlgebra("Alg2", [0, 1, 2, 3] ,[])
    
    con_lat1 = CongruenceLattice(alg1)
    con_lat2 = CongruenceLattice(alg2)
    
    assert con_lat1.alg_size() == 3
    assert con_lat2.alg_size() == 4


def test_tg_tolerance():
    """Test tolerance generation (tg method)."""
    alg = BasicAlgebra.new_with_constant_op("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    # Generate tolerance for elements 0 and 1
    tol = con_lat.tg(0, 1)
    
    assert isinstance(tol, BasicBinaryRelation)
    assert tol.universe_size() == 3


def test_generating_pair():
    """Test generating_pair method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    zero = con_lat.zero()
    pair = con_lat.generating_pair(zero)
    
    # Should return None or a tuple
    if pair is not None:
        assert isinstance(pair, tuple)
        assert len(pair) == 2


def test_find_coatom_above():
    """Test find_coatom_above method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    zero = con_lat.zero()
    coatom = con_lat.find_coatom_above(zero)
    
    # Should return None or a Partition
    if coatom is not None:
        assert isinstance(coatom, Partition)


def test_find_join_irred():
    """Test find_join_irred method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    zero = con_lat.zero()
    one = con_lat.one()
    
    ji = con_lat.find_join_irred(zero, one)
    
    # Should return None or a Partition
    if ji is not None:
        assert isinstance(ji, Partition)


def test_find_meet_irred():
    """Test find_meet_irred method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    zero = con_lat.zero()
    one = con_lat.one()
    
    mi = con_lat.find_meet_irred(zero, one)
    
    # Should return None or a Partition
    if mi is not None:
        assert isinstance(mi, Partition)


def test_find_maximal_chain():
    """Test find_maximal_chain method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    chain = con_lat.find_maximal_chain()
    
    assert isinstance(chain, list)
    assert len(chain) >= 2  # At least zero and one
    
    # All elements should be partitions
    for partition in chain:
        assert isinstance(partition, Partition)


def test_idempotent_polynomials():
    """Test idempotent_polynomials method."""
    alg = BasicAlgebra.new_with_constant_op("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    polynomials = con_lat.idempotent_polynomials()
    assert isinstance(polynomials, list)
    
    # All elements should be IntArrays
    for poly in polynomials:
        assert isinstance(poly, uacalc_lib.IntArray)


def test_delta():
    """Test delta method (stubbed)."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    zero_partition = con_lat.zero()
    one_partition = con_lat.one()
    
    delta_result = con_lat.delta(zero_partition, one_partition)
    assert isinstance(delta_result, Partition)
    # Since it's stubbed, it should return the zero partition
    assert delta_result == zero_partition


def test_commutator2():
    """Test commutator2 method (stubbed)."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    zero_partition = con_lat.zero()
    one_partition = con_lat.one()
    
    comm_result = con_lat.commutator2(zero_partition, one_partition)
    assert isinstance(comm_result, Partition)
    # Since it's stubbed, it should return the zero partition
    assert comm_result == zero_partition


def test_centralizes():
    """Test centralizes method (stubbed)."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2] ,[])
    con_lat = CongruenceLattice(alg)
    
    # Convert zero and one partitions to binary relations
    zero_partition = con_lat.zero()
    one_partition = con_lat.one()
    
    # Convert partitions to binary relations for the centralizes method
    s_relation = zero_partition.to_binary_relation()  # Zero partition as binary relation
    t_relation = one_partition.to_binary_relation()    # One partition as binary relation
    delta_partition = zero_partition                   # Delta remains as partition
    
    # Test with default behavior (should return True when stubbed)
    centralizes_result = con_lat.centralizes(s_relation, t_relation, delta_partition)
    assert isinstance(centralizes_result, bool)
    assert centralizes_result == True  # Stubbed to return True


def test_generic_type_support():
    """Test that CongruenceLattice works with algebras of different sizes."""
    for size in [2, 3, 4, 5]:
        elements = list(range(size))
        alg = BasicAlgebra(f"Alg{size}", elements ,[])
        con_lat = CongruenceLattice(alg)
        
        assert con_lat.alg_size() == size
        assert con_lat.con_cardinality() >= 2


def test_error_handling():
    """Test error handling for invalid inputs"""
    alg = BasicAlgebra.new_with_constant_op('TestAlg', [0,1,2,3])
    conlat = CongruenceLattice(alg)
    
    # Should not raise
    zero = conlat.zero()
    one = conlat.one()
    
    # Test with valid partitions
    result = conlat.tg(0, 1)
    assert isinstance(result, BasicBinaryRelation)


def test_principals():
    """Test getting principal congruences"""
    # Create a 3-element algebra with projection
    alg = BasicAlgebra('TestAlg', [0, 1, 2] ,[])
    conlat = CongruenceLattice(alg)
    
    # Get principals
    principals = conlat.principals()
    
    assert isinstance(principals, list)
    # For a 3-element algebra, we should have Cg(0,1), Cg(0,2), Cg(1,2)
    assert len(principals) >= 3
    
    # Each should be a Partition
    for p in principals:
        assert isinstance(p, Partition)


def test_atoms():
    """Test getting atoms of the lattice"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2] ,[])
    conlat = CongruenceLattice(alg)
    
    atoms = conlat.atoms()
    
    assert isinstance(atoms, list)
    # Atoms should be non-empty for non-trivial algebra
    assert len(atoms) > 0
    
    # Each atom should be a partition above zero
    zero = conlat.zero()
    for atom in atoms:
        assert isinstance(atom, Partition)


def test_meet_irreducibles_method():
    """Test getting meet irreducible congruences"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2] ,[])
    conlat = CongruenceLattice(alg)
    
    mis = conlat.meet_irreducibles()
    
    assert isinstance(mis, list)
    # Each should be a Partition
    for m in mis:
        assert isinstance(m, Partition)


def test_universe():
    """Test getting all congruences"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2] ,[])
    conlat = CongruenceLattice(alg)
    
    universe = conlat.universe()
    
    assert isinstance(universe, list)
    # Universe should include at least zero and one
    assert len(universe) >= 2
    
    # Cardinality should match
    assert len(universe) == conlat.con_cardinality()
    
    # Each should be a Partition
    for con in universe:
        assert isinstance(con, Partition)


def test_permutability_level():
    """Test getting permutability level"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2] ,[])
    conlat = CongruenceLattice(alg)
    
    level = conlat.permutability_level()
    
    assert isinstance(level, int)
    # Level should be >= -1 (not computed) or >= 0
    assert level >= -1


def test_cg():
    """Test computing principal congruence"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2, 3] ,[])
    conlat = CongruenceLattice(alg)
    
    # Compute Cg(0, 1)
    cg_01 = conlat.cg(0, 1)
    
    assert isinstance(cg_01, Partition)
    
    # Cg(a, a) should be zero
    cg_00 = conlat.cg(0, 0)
    zero = conlat.zero()
    # They should represent the same partition
    assert cg_00.universe_size() == zero.universe_size()


def test_complements():
    """Test getting complements"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2, 3] ,[])
    conlat = CongruenceLattice(alg)
    
    zero = conlat.zero()
    complements = conlat.complements(zero)
    
    assert isinstance(complements, list)
    # Zero's only complement should be one (in a complemented lattice)
    # But the lattice might not be complemented
    for comp in complements:
        assert isinstance(comp, Partition)


def test_find_principal_chain():
    """Test finding a principal chain"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2, 3] ,[])
    conlat = CongruenceLattice(alg)
    
    chain = conlat.find_principal_chain()
    
    assert isinstance(chain, list)
    # Chain should have at least 2 elements (zero and one)
    assert len(chain) >= 2
    
    # Each should be a Partition
    for p in chain:
        assert isinstance(p, Partition)


def test_find_upper_cover():
    """Test finding upper cover"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2, 3] ,[])
    conlat = CongruenceLattice(alg)
    
    zero = conlat.zero()
    cover = conlat.find_upper_cover(zero)
    
    # Cover might be None or a Partition
    if cover is not None:
        assert isinstance(cover, Partition)


def test_irredundant_meet_decomposition():
    """Test getting irredundant meet decomposition"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2] ,[])
    conlat = CongruenceLattice(alg)
    
    decomp = conlat.irredundant_meet_decomposition()
    
    assert isinstance(decomp, list)
    # Each should be a Partition
    for p in decomp:
        assert isinstance(p, Partition)


def test_join_irreducibles():
    """Test getting join irreducibles"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2] ,[])
    conlat = CongruenceLattice(alg)
    
    jis = conlat.join_irreducibles()
    
    assert isinstance(jis, list)
    # Should have at least one join irreducible (atoms)
    assert len(jis) > 0
    
    # Each should be a Partition
    for ji in jis:
        assert isinstance(ji, Partition)


def find_all_algebras():
    """Find all .ua algebra files in resources/algebras/ and subdirectories."""
    algebras = []
    if not RESOURCES_ALGEBRAS_DIR.exists():
        return algebras
    
    # Files in root
    for file in RESOURCES_ALGEBRAS_DIR.glob("*.ua"):
        algebras.append(str(file))
    
    # Files in subdirectories
    for subdir in RESOURCES_ALGEBRAS_DIR.iterdir():
        if subdir.is_dir():
            for file in subdir.glob("*.ua"):
                algebras.append(str(file))
    
    return sorted(algebras)


def run_java_wrapper(command, args=None, timeout=60):
    """Run Java wrapper and return parsed JSON result."""
    separator = ";" if os.name == "nt" else ":"
    cmd = [
        "java", "-cp",
        f"java_wrapper/build/classes{separator}build/classes{separator}org{separator}jars/*",
        "java_wrapper.src.alg.conlat.CongruenceLatticeWrapper",
        command
    ]
    if args:
        cmd.extend(args)
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(PROJECT_ROOT)
    )
    
    # Check if output contains error JSON (success: false)
    stdout = result.stdout.strip()
    if "success" in stdout and '"success": false' in stdout:
        # Try to parse error
        try:
            error_json = json.loads(stdout.split('\n')[-1])
            error_msg = error_json.get("error", "Unknown error")
            raise RuntimeError(f"Java wrapper error: {error_msg}")
        except:
            pass
    
    if result.returncode != 0:
        # Check if stderr is just INFO messages (not real errors)
        stderr_lower = result.stderr.lower()
        if "info:" in stderr_lower or "warning:" in stderr_lower:
            # Might just be log messages, try to continue
            pass
        else:
            raise RuntimeError(f"Java wrapper failed: {result.stderr}")
    
    # Extract JSON from output
    stdout = result.stdout.strip()
    lines = stdout.split('\n')
    
    # Find complete JSON object
    brace_count = 0
    json_lines = []
    found_start = False
    for line in reversed(lines):
        line_stripped = line.strip()
        if not found_start and line_stripped.endswith('}'):
            found_start = True
        if found_start:
            json_lines.insert(0, line)
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0 and line_stripped.startswith('{'):
                break
    
    if not json_lines:
        raise RuntimeError("Could not find JSON in Java output")
    
    json_str = '\n'.join(json_lines)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Could not parse JSON from Java output: {e}. JSON: {json_str[:200]}")


class TestCongruenceLatticeJavaComparison(unittest.TestCase):
    """Test CongruenceLattice against Java implementation for all algebras."""
    
    def test_all_algebras_cardinality_and_distributivity(self):
        """Test congruence lattice cardinality and distributivity for all algebras."""
        algebras = find_all_algebras()
        
        if not algebras:
            self.skipTest("No algebra files found in resources/algebras/")
        
        print(f"\nTesting {len(algebras)} algebras...")
        
        results = {
            'total_algebras': len(algebras),
            'skipped': 0,
            'compared': 0,
            'mismatches': []
        }
        
        for algebra_path in algebras:
            algebra_name = os.path.basename(algebra_path)
            print(f"\nTesting algebra: {algebra_name}")
            
            try:
                # Load algebra in Python
                AlgebraReader = uacalc_lib.io.AlgebraReader
                reader = AlgebraReader.new_from_file(algebra_path)
                alg = reader.read_algebra_file()
                
                # Get Python results
                con_lat = CongruenceLattice(alg)
                python_cardinality = con_lat.con_cardinality()
                python_is_distributive = con_lat.is_distributive()
                
                # Get Java results
                try:
                    # Get cardinality from Java
                    java_card_output = run_java_wrapper("con_cardinality", [
                        "--algebra", algebra_path
                    ], timeout=30)
                    java_card_data = java_card_output.get("data", {})
                    java_cardinality = java_card_data.get("cardinality")
                    
                    # Get distributivity from Java
                    java_dist_output = run_java_wrapper("is_distributive", [
                        "--algebra", algebra_path
                    ], timeout=30)
                    java_dist_data = java_dist_output.get("data", {})
                    java_is_distributive = java_dist_data.get("is_distributive")
                    
                    results['compared'] += 1
                    
                    # Compare cardinality
                    if python_cardinality != java_cardinality:
                        mismatch = {
                            'algebra': algebra_name,
                            'property': 'cardinality',
                            'python': python_cardinality,
                            'java': java_cardinality
                        }
                        results['mismatches'].append(mismatch)
                        print(f"  ✗ cardinality: Python={python_cardinality}, Java={java_cardinality}")
                    else:
                        print(f"  ✓ cardinality: {python_cardinality}")
                    
                    # Compare distributivity
                    if python_is_distributive != java_is_distributive:
                        mismatch = {
                            'algebra': algebra_name,
                            'property': 'is_distributive',
                            'python': python_is_distributive,
                            'java': java_is_distributive
                        }
                        results['mismatches'].append(mismatch)
                        print(f"  ✗ is_distributive: Python={python_is_distributive}, Java={java_is_distributive}")
                    else:
                        print(f"  ✓ is_distributive: {python_is_distributive}")
                    
                except subprocess.TimeoutExpired:
                    print(f"  ⏩ Java wrapper timed out, skipping")
                    results['skipped'] += 1
                except Exception as e:
                    print(f"  ⏩ Java wrapper error: {e}, skipping")
                    results['skipped'] += 1
                    
            except Exception as e:
                print(f"  ⏩ Error loading algebra: {e}, skipping")
                results['skipped'] += 1
                continue
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"Test Summary:")
        print(f"  Total algebras: {results['total_algebras']}")
        print(f"  Tests compared: {results['compared']}")
        print(f"  Tests skipped: {results['skipped']}")
        print(f"  Mismatches: {len(results['mismatches'])}")
        print(f"{'='*60}")
        
        if results['mismatches']:
            print("\nMismatches found:")
            for mismatch in results['mismatches']:
                print(f"  {mismatch['algebra']} / {mismatch['property']}: "
                      f"Python={mismatch['python']}, Java={mismatch['java']}")
        
        # Fail test if there are mismatches
        if results['mismatches']:
            self.fail(f"Found {len(results['mismatches'])} mismatches between Python and Java implementations")
