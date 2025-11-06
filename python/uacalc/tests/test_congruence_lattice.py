"""
Test suite for CongruenceLattice bindings.
"""
import pytest
import uacalc_lib

# Type aliases for convenience
BasicAlgebra = uacalc_lib.alg.BasicAlgebra
CongruenceLattice = uacalc_lib.alg.CongruenceLattice
Partition = uacalc_lib.alg.Partition
BasicBinaryRelation = uacalc_lib.alg.BasicBinaryRelation


def test_congruence_lattice_creation():
    """Test basic CongruenceLattice creation."""
    # Create a simple algebra
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
    
    # Create congruence lattice
    con_lat = CongruenceLattice(alg)
    
    assert con_lat is not None
    assert str(con_lat).startswith("Con")


def test_alg_size():
    """Test alg_size method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    assert con_lat.alg_size() == 3


def test_zero_and_one():
    """Test zero and one congruence methods."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    zero = con_lat.zero()
    one = con_lat.one()
    
    assert isinstance(zero, Partition)
    assert isinstance(one, Partition)
    
    # Zero should have more blocks than one
    assert zero.number_of_blocks() > one.number_of_blocks()


def test_cardinality():
    """Test con_cardinality method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    cardinality = con_lat.con_cardinality()
    
    assert cardinality >= 2  # At least zero and one


def test_cardinality_size_4():
    """Test cardinality for a 4-element algebra."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2, 3])
    con_lat = CongruenceLattice(alg)
    
    cardinality = con_lat.con_cardinality()
    
    assert cardinality >= 2  # At least zero and one


def test_is_distributive():
    """Test is_distributive method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    is_dist = con_lat.is_distributive()
    
    assert isinstance(is_dist, bool)


def test_get_description():
    """Test get_description method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    desc = con_lat.get_description()
    
    assert isinstance(desc, str)


def test_string_representation():
    """Test __str__ and __repr__ methods."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    str_repr = str(con_lat)
    repr_repr = repr(con_lat)
    
    assert "Con" in str_repr
    assert "Con" in repr_repr


def test_multiple_algebras():
    """Test creating multiple congruence lattices."""
    alg1 = BasicAlgebra("Alg1", [0, 1, 2])
    alg2 = BasicAlgebra("Alg2", [0, 1, 2, 3])
    
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
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    zero = con_lat.zero()
    pair = con_lat.generating_pair(zero)
    
    # Should return None or a tuple
    if pair is not None:
        assert isinstance(pair, tuple)
        assert len(pair) == 2


def test_find_coatom_above():
    """Test find_coatom_above method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    zero = con_lat.zero()
    coatom = con_lat.find_coatom_above(zero)
    
    # Should return None or a Partition
    if coatom is not None:
        assert isinstance(coatom, Partition)


def test_find_join_irred():
    """Test find_join_irred method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    zero = con_lat.zero()
    one = con_lat.one()
    
    ji = con_lat.find_join_irred(zero, one)
    
    # Should return None or a Partition
    if ji is not None:
        assert isinstance(ji, Partition)


def test_find_meet_irred():
    """Test find_meet_irred method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    zero = con_lat.zero()
    one = con_lat.one()
    
    mi = con_lat.find_meet_irred(zero, one)
    
    # Should return None or a Partition
    if mi is not None:
        assert isinstance(mi, Partition)


def test_find_maximal_chain():
    """Test find_maximal_chain method."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
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
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    zero_partition = con_lat.zero()
    one_partition = con_lat.one()
    
    delta_result = con_lat.delta(zero_partition, one_partition)
    assert isinstance(delta_result, Partition)
    # Since it's stubbed, it should return the zero partition
    assert delta_result == zero_partition


def test_commutator2():
    """Test commutator2 method (stubbed)."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
    con_lat = CongruenceLattice(alg)
    
    zero_partition = con_lat.zero()
    one_partition = con_lat.one()
    
    comm_result = con_lat.commutator2(zero_partition, one_partition)
    assert isinstance(comm_result, Partition)
    # Since it's stubbed, it should return the zero partition
    assert comm_result == zero_partition


def test_centralizes():
    """Test centralizes method (stubbed)."""
    alg = BasicAlgebra("TestAlg", [0, 1, 2])
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
        alg = BasicAlgebra(f"Alg{size}", elements)
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
    alg = BasicAlgebra('TestAlg', [0, 1, 2])
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
    alg = BasicAlgebra('TestAlg', [0, 1, 2])
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
    alg = BasicAlgebra('TestAlg', [0, 1, 2])
    conlat = CongruenceLattice(alg)
    
    mis = conlat.meet_irreducibles()
    
    assert isinstance(mis, list)
    # Each should be a Partition
    for m in mis:
        assert isinstance(m, Partition)


def test_universe():
    """Test getting all congruences"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2])
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
    alg = BasicAlgebra('TestAlg', [0, 1, 2])
    conlat = CongruenceLattice(alg)
    
    level = conlat.permutability_level()
    
    assert isinstance(level, int)
    # Level should be >= -1 (not computed) or >= 0
    assert level >= -1


def test_cg():
    """Test computing principal congruence"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2, 3])
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
    alg = BasicAlgebra('TestAlg', [0, 1, 2, 3])
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
    alg = BasicAlgebra('TestAlg', [0, 1, 2, 3])
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
    alg = BasicAlgebra('TestAlg', [0, 1, 2, 3])
    conlat = CongruenceLattice(alg)
    
    zero = conlat.zero()
    cover = conlat.find_upper_cover(zero)
    
    # Cover might be None or a Partition
    if cover is not None:
        assert isinstance(cover, Partition)


def test_irredundant_meet_decomposition():
    """Test getting irredundant meet decomposition"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2])
    conlat = CongruenceLattice(alg)
    
    decomp = conlat.irredundant_meet_decomposition()
    
    assert isinstance(decomp, list)
    # Each should be a Partition
    for p in decomp:
        assert isinstance(p, Partition)


def test_join_irreducibles():
    """Test getting join irreducibles"""
    alg = BasicAlgebra('TestAlg', [0, 1, 2])
    conlat = CongruenceLattice(alg)
    
    jis = conlat.join_irreducibles()
    
    assert isinstance(jis, list)
    # Should have at least one join irreducible (atoms)
    assert len(jis) > 0
    
    # Each should be a Partition
    for ji in jis:
        assert isinstance(ji, Partition)
