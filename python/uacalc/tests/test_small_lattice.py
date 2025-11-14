"""
Tests for SmallLattice implementations.

This module tests the SmallLattice trait implementations including
DiamondLattice and BooleanLattice, focusing on the upper_covers_indices
method and other lattice operations.
"""

import unittest
import uacalc_lib


class TestDiamondLattice(unittest.TestCase):
    """Test DiamondLattice (M3) implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.lattice = uacalc_lib.lat.DiamondLattice()
    
    def test_creation(self):
        """Test lattice creation and basic properties."""
        self.assertIsNotNone(self.lattice)
        self.assertEqual(self.lattice.size(), 4)
        self.assertEqual(self.lattice.cardinality(), 4)
        self.assertEqual(self.lattice.universe(), [0, 1, 2, 3])
    
    def test_get_element(self):
        """Test getting elements by index."""
        self.assertEqual(self.lattice.get_element(0), 0)
        self.assertEqual(self.lattice.get_element(1), 1)
        self.assertEqual(self.lattice.get_element(2), 2)
        self.assertEqual(self.lattice.get_element(3), 3)
        self.assertIsNone(self.lattice.get_element(4))  # out of bounds
    
    def test_upper_covers_indices(self):
        """Test upper covers indices method."""
        # Bottom element (0) is covered by both atoms (1, 2)
        covers_0 = self.lattice.upper_covers_indices(0)
        self.assertEqual(set(covers_0), {1, 2})
        
        # Left atom (1) is covered by top (3)
        covers_1 = self.lattice.upper_covers_indices(1)
        self.assertEqual(covers_1, [3])
        
        # Right atom (2) is covered by top (3)
        covers_2 = self.lattice.upper_covers_indices(2)
        self.assertEqual(covers_2, [3])
        
        # Top element (3) has no upper covers
        covers_3 = self.lattice.upper_covers_indices(3)
        self.assertEqual(covers_3, [])
        
        # Out of bounds should return empty list
        covers_out = self.lattice.upper_covers_indices(4)
        self.assertEqual(covers_out, [])
    
    def test_order_relation(self):
        """Test the order relation (≤)."""
        # Bottom element is less than or equal to everything
        self.assertTrue(self.lattice.leq(0, 0))
        self.assertTrue(self.lattice.leq(0, 1))
        self.assertTrue(self.lattice.leq(0, 2))
        self.assertTrue(self.lattice.leq(0, 3))
        
        # Atoms are less than or equal to themselves and top
        self.assertTrue(self.lattice.leq(1, 1))
        self.assertTrue(self.lattice.leq(1, 3))
        self.assertTrue(self.lattice.leq(2, 2))
        self.assertTrue(self.lattice.leq(2, 3))
        
        # Top element is only less than or equal to itself
        self.assertTrue(self.lattice.leq(3, 3))
        
        # Atoms are not comparable to each other
        self.assertFalse(self.lattice.leq(1, 2))
        self.assertFalse(self.lattice.leq(2, 1))
        
        # Nothing is less than bottom (except bottom itself)
        self.assertFalse(self.lattice.leq(1, 0))
        self.assertFalse(self.lattice.leq(2, 0))
        self.assertFalse(self.lattice.leq(3, 0))
    
    def test_join_operation(self):
        """Test join (least upper bound) operation."""
        # Join with bottom element
        self.assertEqual(self.lattice.join(0, 1), 1)
        self.assertEqual(self.lattice.join(0, 2), 2)
        self.assertEqual(self.lattice.join(0, 3), 3)
        self.assertEqual(self.lattice.join(1, 0), 1)
        self.assertEqual(self.lattice.join(2, 0), 2)
        self.assertEqual(self.lattice.join(3, 0), 3)
        
        # Join of atoms is top
        self.assertEqual(self.lattice.join(1, 2), 3)
        self.assertEqual(self.lattice.join(2, 1), 3)
        
        # Join with top element
        self.assertEqual(self.lattice.join(1, 3), 3)
        self.assertEqual(self.lattice.join(2, 3), 3)
        self.assertEqual(self.lattice.join(3, 1), 3)
        self.assertEqual(self.lattice.join(3, 2), 3)
        
        # Idempotent
        self.assertEqual(self.lattice.join(0, 0), 0)
        self.assertEqual(self.lattice.join(1, 1), 1)
        self.assertEqual(self.lattice.join(2, 2), 2)
        self.assertEqual(self.lattice.join(3, 3), 3)
    
    def test_meet_operation(self):
        """Test meet (greatest lower bound) operation."""
        # Meet with top element
        self.assertEqual(self.lattice.meet(3, 1), 1)
        self.assertEqual(self.lattice.meet(3, 2), 2)
        self.assertEqual(self.lattice.meet(3, 0), 0)
        self.assertEqual(self.lattice.meet(1, 3), 1)
        self.assertEqual(self.lattice.meet(2, 3), 2)
        self.assertEqual(self.lattice.meet(0, 3), 0)
        
        # Meet of atoms is bottom
        self.assertEqual(self.lattice.meet(1, 2), 0)
        self.assertEqual(self.lattice.meet(2, 1), 0)
        
        # Meet with bottom element
        self.assertEqual(self.lattice.meet(1, 0), 0)
        self.assertEqual(self.lattice.meet(2, 0), 0)
        self.assertEqual(self.lattice.meet(0, 1), 0)
        self.assertEqual(self.lattice.meet(0, 2), 0)
        
        # Idempotent
        self.assertEqual(self.lattice.meet(0, 0), 0)
        self.assertEqual(self.lattice.meet(1, 1), 1)
        self.assertEqual(self.lattice.meet(2, 2), 2)
        self.assertEqual(self.lattice.meet(3, 3), 3)
    
    def test_join_list(self):
        """Test join of multiple elements."""
        # Join of all elements should be top
        self.assertEqual(self.lattice.join_list([0, 1, 2, 3]), 3)
        
        # Join of atoms should be top
        self.assertEqual(self.lattice.join_list([1, 2]), 3)
        
        # Join of single element should be that element
        self.assertEqual(self.lattice.join_list([1]), 1)
        
        # Join of empty list should be bottom
        self.assertEqual(self.lattice.join_list([]), 0)
    
    def test_meet_list(self):
        """Test meet of multiple elements."""
        # Meet of all elements should be bottom
        self.assertEqual(self.lattice.meet_list([0, 1, 2, 3]), 0)
        
        # Meet of atoms should be bottom
        self.assertEqual(self.lattice.meet_list([1, 2]), 0)
        
        # Meet of single element should be that element
        self.assertEqual(self.lattice.meet_list([1]), 1)
        
        # Meet of empty list should be top
        self.assertEqual(self.lattice.meet_list([]), 3)
    
    def test_atoms_and_coatoms(self):
        """Test atoms and coatoms."""
        atoms = self.lattice.atoms()
        self.assertIsNotNone(atoms)
        self.assertEqual(set(atoms), {1, 2})
        
        coatoms = self.lattice.coatoms()
        self.assertIsNotNone(coatoms)
        self.assertEqual(set(coatoms), {1, 2})
    
    def test_join_irreducibles(self):
        """Test join irreducibles."""
        join_irr = self.lattice.join_irreducibles()
        self.assertIsNotNone(join_irr)
        self.assertEqual(set(join_irr), {1, 2})
    
    def test_meet_irreducibles(self):
        """Test meet irreducibles."""
        meet_irr = self.lattice.meet_irreducibles()
        self.assertIsNotNone(meet_irr)
        self.assertEqual(set(meet_irr), {1, 2})
    
    def test_lattice_laws(self):
        """Test that lattice laws are satisfied."""
        # Commutative laws
        for a in range(4):
            for b in range(4):
                self.assertEqual(self.lattice.join(a, b), self.lattice.join(b, a))
                self.assertEqual(self.lattice.meet(a, b), self.lattice.meet(b, a))
        
        # Associative laws
        for a in range(4):
            for b in range(4):
                for c in range(4):
                    # join(join(a,b), c) == join(a, join(b,c))
                    left_join = self.lattice.join(self.lattice.join(a, b), c)
                    right_join = self.lattice.join(a, self.lattice.join(b, c))
                    self.assertEqual(left_join, right_join)
                    
                    # meet(meet(a,b), c) == meet(a, meet(b,c))
                    left_meet = self.lattice.meet(self.lattice.meet(a, b), c)
                    right_meet = self.lattice.meet(a, self.lattice.meet(b, c))
                    self.assertEqual(left_meet, right_meet)
        
        # Absorption laws
        for a in range(4):
            for b in range(4):
                # join(a, meet(a,b)) == a
                self.assertEqual(self.lattice.join(a, self.lattice.meet(a, b)), a)
                # meet(a, join(a,b)) == a
                self.assertEqual(self.lattice.meet(a, self.lattice.join(a, b)), a)
    
    def test_string_representations(self):
        """Test string representations."""
        self.assertEqual(str(self.lattice), "DiamondLattice")
        self.assertEqual(repr(self.lattice), "DiamondLattice()")


class TestBooleanLattice(unittest.TestCase):
    """Test BooleanLattice (2-element lattice) implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.lattice = uacalc_lib.lat.BooleanLattice()
    
    def test_creation(self):
        """Test lattice creation and basic properties."""
        self.assertIsNotNone(self.lattice)
        self.assertEqual(self.lattice.size(), 2)
        self.assertEqual(self.lattice.cardinality(), 2)
        self.assertEqual(self.lattice.universe(), [0, 1])
    
    def test_get_element(self):
        """Test getting elements by index."""
        self.assertEqual(self.lattice.get_element(0), 0)
        self.assertEqual(self.lattice.get_element(1), 1)
        self.assertIsNone(self.lattice.get_element(2))  # out of bounds
    
    def test_upper_covers_indices(self):
        """Test upper covers indices method."""
        # Bottom element (0) is covered by top (1)
        covers_0 = self.lattice.upper_covers_indices(0)
        self.assertEqual(covers_0, [1])
        
        # Top element (1) has no upper covers
        covers_1 = self.lattice.upper_covers_indices(1)
        self.assertEqual(covers_1, [])
        
        # Out of bounds should return empty list
        covers_out = self.lattice.upper_covers_indices(2)
        self.assertEqual(covers_out, [])
    
    def test_order_relation(self):
        """Test the order relation (≤)."""
        # Bottom element is less than or equal to everything
        self.assertTrue(self.lattice.leq(0, 0))
        self.assertTrue(self.lattice.leq(0, 1))
        
        # Top element is only less than or equal to itself
        self.assertTrue(self.lattice.leq(1, 1))
        
        # Top is not less than bottom
        self.assertFalse(self.lattice.leq(1, 0))
    
    def test_join_operation(self):
        """Test join (least upper bound) operation."""
        # Join with bottom element
        self.assertEqual(self.lattice.join(0, 1), 1)
        self.assertEqual(self.lattice.join(1, 0), 1)
        
        # Idempotent
        self.assertEqual(self.lattice.join(0, 0), 0)
        self.assertEqual(self.lattice.join(1, 1), 1)
    
    def test_meet_operation(self):
        """Test meet (greatest lower bound) operation."""
        # Meet with top element
        self.assertEqual(self.lattice.meet(1, 0), 0)
        self.assertEqual(self.lattice.meet(0, 1), 0)
        
        # Idempotent
        self.assertEqual(self.lattice.meet(0, 0), 0)
        self.assertEqual(self.lattice.meet(1, 1), 1)
    
    def test_join_list(self):
        """Test join of multiple elements."""
        # Join of all elements should be top
        self.assertEqual(self.lattice.join_list([0, 1]), 1)
        
        # Join of single element should be that element
        self.assertEqual(self.lattice.join_list([0]), 0)
        self.assertEqual(self.lattice.join_list([1]), 1)
        
        # Join of empty list should be bottom
        self.assertEqual(self.lattice.join_list([]), 0)
    
    def test_meet_list(self):
        """Test meet of multiple elements."""
        # Meet of all elements should be bottom
        self.assertEqual(self.lattice.meet_list([0, 1]), 0)
        
        # Meet of single element should be that element
        self.assertEqual(self.lattice.meet_list([0]), 0)
        self.assertEqual(self.lattice.meet_list([1]), 1)
        
        # Meet of empty list should be top
        self.assertEqual(self.lattice.meet_list([]), 1)
    
    def test_atoms_and_coatoms(self):
        """Test atoms and coatoms."""
        atoms = self.lattice.atoms()
        self.assertIsNotNone(atoms)
        self.assertEqual(atoms, [1])
        
        coatoms = self.lattice.coatoms()
        self.assertIsNotNone(coatoms)
        self.assertEqual(coatoms, [1])
    
    def test_join_irreducibles(self):
        """Test join irreducibles."""
        join_irr = self.lattice.join_irreducibles()
        self.assertIsNotNone(join_irr)
        self.assertEqual(join_irr, [1])
    
    def test_meet_irreducibles(self):
        """Test meet irreducibles."""
        meet_irr = self.lattice.meet_irreducibles()
        self.assertIsNotNone(meet_irr)
        self.assertEqual(meet_irr, [1])
    
    def test_lattice_laws(self):
        """Test that lattice laws are satisfied."""
        # Commutative laws
        for a in range(2):
            for b in range(2):
                self.assertEqual(self.lattice.join(a, b), self.lattice.join(b, a))
                self.assertEqual(self.lattice.meet(a, b), self.lattice.meet(b, a))
        
        # Associative laws
        for a in range(2):
            for b in range(2):
                for c in range(2):
                    # join(join(a,b), c) == join(a, join(b,c))
                    left_join = self.lattice.join(self.lattice.join(a, b), c)
                    right_join = self.lattice.join(a, self.lattice.join(b, c))
                    self.assertEqual(left_join, right_join)
                    
                    # meet(meet(a,b), c) == meet(a, meet(b,c))
                    left_meet = self.lattice.meet(self.lattice.meet(a, b), c)
                    right_meet = self.lattice.meet(a, self.lattice.meet(b, c))
                    self.assertEqual(left_meet, right_meet)
        
        # Absorption laws
        for a in range(2):
            for b in range(2):
                # join(a, meet(a,b)) == a
                self.assertEqual(self.lattice.join(a, self.lattice.meet(a, b)), a)
                # meet(a, join(a,b)) == a
                self.assertEqual(self.lattice.meet(a, self.lattice.join(a, b)), a)
    
    def test_string_representations(self):
        """Test string representations."""
        self.assertEqual(str(self.lattice), "BooleanLattice")
        self.assertEqual(repr(self.lattice), "BooleanLattice()")


class TestSmallLatticeComparison(unittest.TestCase):
    """Test comparison between different SmallLattice implementations."""
    
    def test_diamond_vs_boolean(self):
        """Test that DiamondLattice and BooleanLattice have different properties."""
        diamond = uacalc_lib.lat.DiamondLattice()
        boolean = uacalc_lib.lat.BooleanLattice()
        
        # Different sizes
        self.assertNotEqual(diamond.size(), boolean.size())
        self.assertEqual(diamond.size(), 4)
        self.assertEqual(boolean.size(), 2)
        
        # Different upper covers for bottom element
        diamond_covers = diamond.upper_covers_indices(0)
        boolean_covers = boolean.upper_covers_indices(0)
        self.assertNotEqual(len(diamond_covers), len(boolean_covers))
        self.assertEqual(len(diamond_covers), 2)  # diamond has 2 upper covers
        self.assertEqual(len(boolean_covers), 1)  # boolean has 1 upper cover
        
        # Different atoms
        diamond_atoms = diamond.atoms()
        boolean_atoms = boolean.atoms()
        self.assertNotEqual(len(diamond_atoms), len(boolean_atoms))
        self.assertEqual(len(diamond_atoms), 2)  # diamond has 2 atoms
        self.assertEqual(len(boolean_atoms), 1)  # boolean has 1 atom


if __name__ == '__main__':
    unittest.main()
