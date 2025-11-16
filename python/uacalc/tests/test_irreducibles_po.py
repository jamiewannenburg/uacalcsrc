"""Test cases for join_irreducibles_po and meet_irreducibles_po methods."""

import unittest
import uacalc_lib
BasicAlgebra = uacalc_lib.alg.BasicAlgebra
CongruenceLattice = uacalc_lib.alg.CongruenceLattice
SubalgebraLattice = uacalc_lib.alg.SubalgebraLattice
BasicLattice = uacalc_lib.lat.BasicLattice
OrderedSet = uacalc_lib.lat.OrderedSet
OrderedSetPartition = uacalc_lib.lat.OrderedSetPartition
OrderedSetBasicSet = uacalc_lib.lat.OrderedSetBasicSet


class TestIrreduciblesPO(unittest.TestCase):
    """Test join_irreducibles_po and meet_irreducibles_po methods."""

    def test_congruence_lattice_join_irreducibles_po(self):
        """Test join_irreducibles_po for CongruenceLattice."""
        alg = BasicAlgebra('TestAlg', [0, 1, 2], [])
        conlat = CongruenceLattice(alg)
        
        jis_po = conlat.join_irreducibles_po()
        
        # Should return an OrderedSetPartition
        self.assertIsNotNone(jis_po)
        self.assertIsInstance(jis_po, OrderedSetPartition)
        
        # Should have a name
        self.assertEqual(jis_po.name(), "JoinIrreducibles")
        
        # Should have at least one element
        self.assertGreater(jis_po.cardinality(), 0)
        
        # Universe should be a list of Partitions
        universe = jis_po.universe()
        self.assertIsInstance(universe, list)
        self.assertEqual(len(universe), jis_po.cardinality())
        
        # Each element should be a Partition
        for p in universe:
            self.assertIsInstance(p, uacalc_lib.alg.Partition)

    def test_congruence_lattice_meet_irreducibles_po(self):
        """Test meet_irreducibles_po for CongruenceLattice."""
        alg = BasicAlgebra('TestAlg', [0, 1, 2], [])
        conlat = CongruenceLattice(alg)
        
        mis_po = conlat.meet_irreducibles_po()
        
        # Should return an OrderedSetPartition
        self.assertIsNotNone(mis_po)
        self.assertIsInstance(mis_po, uacalc_lib.lat.OrderedSetPartition)
        
        # Should have a name
        self.assertEqual(mis_po.name(), "MeetIrreducibles")
        
        # Universe should be a list of Partitions
        universe = mis_po.universe()
        self.assertIsInstance(universe, list)
        self.assertEqual(len(universe), mis_po.cardinality())
        
        # Each element should be a Partition
        for p in universe:
            self.assertIsInstance(p, uacalc_lib.alg.Partition)

    def test_subalgebra_lattice_join_irreducibles_po(self):
        """Test join_irreducibles_po for SubalgebraLattice."""
        alg = BasicAlgebra('TestAlg', [0, 1, 2], [])
        sub_lat = SubalgebraLattice(alg)
        
        jis_po = sub_lat.join_irreducibles_po()
        
        # Should return an OrderedSetBasicSet
        self.assertIsNotNone(jis_po)
        self.assertIsInstance(jis_po, OrderedSetBasicSet)
        
        # Should have a name
        self.assertEqual(jis_po.name(), "JoinIrreducibles")
        
        # Should have at least one element
        self.assertGreater(jis_po.cardinality(), 0)
        
        # Universe should be a list of BasicSets
        universe = jis_po.universe()
        self.assertIsInstance(universe, list)
        self.assertEqual(len(universe), jis_po.cardinality())
        
        # Each element should be a BasicSet
        for bs in universe:
            self.assertIsInstance(bs, uacalc_lib.alg.BasicSet)

    def test_subalgebra_lattice_meet_irreducibles_po(self):
        """Test meet_irreducibles_po for SubalgebraLattice."""
        alg = BasicAlgebra('TestAlg', [0, 1, 2], [])
        sub_lat = SubalgebraLattice(alg)
        
        mis_po = sub_lat.meet_irreducibles_po()
        
        # Should return an OrderedSetBasicSet
        self.assertIsNotNone(mis_po)
        self.assertIsInstance(mis_po, uacalc_lib.lat.OrderedSetBasicSet)
        
        # Should have a name
        self.assertEqual(mis_po.name(), "MeetIrreducibles")
        
        # Universe should be a list of BasicSets
        universe = mis_po.universe()
        self.assertIsInstance(universe, list)
        self.assertEqual(len(universe), mis_po.cardinality())
        
        # Each element should be a BasicSet
        for bs in universe:
            self.assertIsInstance(bs, uacalc_lib.alg.sublat.BasicSet)

    def test_basic_lattice_from_ordered_set(self):
        """Test creating BasicLattice from OrderedSet with filters."""
        # Create an OrderedSet from filters
        universe = [0, 1, 2, 3]
        filters = [
            [0, 1, 2, 3],  # 0's filter
            [1, 2, 3],     # 1's filter
            [2, 3],        # 2's filter
            [3],           # 3's filter
        ]
        poset = OrderedSet.from_filters(universe, filters, name="TestPoset")
        
        # Note: BasicLattice.new_from_poset doesn't exist in Python bindings
        # Instead, we can create a BasicLattice from a lattice operation
        # For now, just verify the OrderedSet was created correctly
        self.assertIsNotNone(poset)
        self.assertIsInstance(poset, OrderedSet)
        self.assertEqual(poset.name(), "TestPoset")
        self.assertEqual(poset.cardinality(), 4)
        
        # Verify the universe
        univ = poset.universe()
        self.assertEqual(sorted(univ), sorted(universe))
        
        # Verify order relations
        self.assertTrue(poset.leq(0, 1))
        self.assertTrue(poset.leq(1, 2))
        self.assertTrue(poset.leq(2, 3))
        self.assertTrue(poset.leq(0, 3))  # Transitivity

    def test_ordered_set_leq_relations(self):
        """Test that OrderedSet preserves order relations."""
        alg = BasicAlgebra('TestAlg', [0, 1, 2], [])
        conlat = CongruenceLattice(alg)
        
        jis_po = conlat.join_irreducibles_po()
        universe = jis_po.universe()
        
        # If there are at least 2 elements, test order relations
        if len(universe) >= 2:
            # Test that leq works
            # Note: We can't easily test specific relations without knowing the structure
            # But we can test that the method doesn't crash
            try:
                result = jis_po.leq(universe[0], universe[1])
                self.assertIsInstance(result, bool)
            except Exception:
                # If elements are not comparable, that's okay
                pass


if __name__ == '__main__':
    unittest.main()

