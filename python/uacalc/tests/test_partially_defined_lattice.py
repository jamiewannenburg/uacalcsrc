"""
Tests for PartiallyDefinedLattice in Python bindings.
"""

import unittest
import sys

# Import through uacalc_lib module
import uacalc_lib


class TestPartiallyDefinedLattice(unittest.TestCase):
    """Test PartiallyDefinedLattice functionality."""
    
    def test_create_simple_lattice(self):
        """Test creating a simple partially defined lattice."""
        PartiallyDefinedLattice = uacalc_lib.fplat.PartiallyDefinedLattice
        VariableImp = uacalc_lib.terms.VariableImp
        
        # Create variables
        x = VariableImp("x")
        y = VariableImp("y")
        z = VariableImp("z")
        
        # Create joins and meets
        joins = [[x, y]]
        meets = [[y, z]]
        
        # Create lattice
        lattice = PartiallyDefinedLattice("TestLattice", joins, meets)
        
        # Test name
        self.assertEqual(lattice.name(), "TestLattice")
    
    def test_lattice_leq(self):
        """Test leq (less than or equal) operation."""
        PartiallyDefinedLattice = uacalc_lib.fplat.PartiallyDefinedLattice
        VariableImp = uacalc_lib.terms.VariableImp
        
        # Create variables with different names
        a = VariableImp("a")
        b = VariableImp("b")
        c = VariableImp("c")
        
        # Create empty joins and meets
        joins = []
        meets = []
        
        # Create lattice
        lattice = PartiallyDefinedLattice("OrderTest", joins, meets)
        
        # Test order relations (name-based order)
        self.assertTrue(lattice.leq(a, b))  # a <= b
        self.assertTrue(lattice.leq(b, c))  # b <= c
        self.assertTrue(lattice.leq(a, c))  # a <= c (transitivity)
        self.assertFalse(lattice.leq(c, a))  # c > a
        
        # Test reflexivity
        self.assertTrue(lattice.leq(a, a))
        self.assertTrue(lattice.leq(b, b))
        self.assertTrue(lattice.leq(c, c))
    
    def test_get_defined_joins(self):
        """Test getting defined joins."""
        PartiallyDefinedLattice = uacalc_lib.fplat.PartiallyDefinedLattice
        VariableImp = uacalc_lib.terms.VariableImp
        
        # Create variables
        x = VariableImp("x")
        y = VariableImp("y")
        z = VariableImp("z")
        w = VariableImp("w")
        
        # Create multiple joins
        joins = [
            [x, y],
            [z, w]
        ]
        meets = []
        
        # Create lattice
        lattice = PartiallyDefinedLattice("JoinTest", joins, meets)
        
        # Get joins
        result_joins = lattice.get_defined_joins()
        
        # Test that we got back the right number of joins
        self.assertEqual(len(result_joins), 2)
        
        # Test that each join has the right number of variables
        self.assertEqual(len(result_joins[0]), 2)
        self.assertEqual(len(result_joins[1]), 2)
    
    def test_get_defined_meets(self):
        """Test getting defined meets."""
        PartiallyDefinedLattice = uacalc_lib.fplat.PartiallyDefinedLattice
        VariableImp = uacalc_lib.terms.VariableImp
        
        # Create variables
        x = VariableImp("x")
        y = VariableImp("y")
        z = VariableImp("z")
        
        # Create multiple meets
        joins = []
        meets = [
            [x, y],
            [y, z]
        ]
        
        # Create lattice
        lattice = PartiallyDefinedLattice("MeetTest", joins, meets)
        
        # Get meets
        result_meets = lattice.get_defined_meets()
        
        # Test that we got back the right number of meets
        self.assertEqual(len(result_meets), 2)
        
        # Test that each meet has the right number of variables
        self.assertEqual(len(result_meets[0]), 2)
        self.assertEqual(len(result_meets[1]), 2)
    
    def test_multiple_joins_meets(self):
        """Test lattice with multiple joins and meets."""
        PartiallyDefinedLattice = uacalc_lib.fplat.PartiallyDefinedLattice
        VariableImp = uacalc_lib.terms.VariableImp
        
        # Create several variables
        x = VariableImp("x")
        y = VariableImp("y")
        z = VariableImp("z")
        w = VariableImp("w")
        
        # Create multiple joins and meets
        joins = [
            [x, y],
            [z, w]
        ]
        meets = [
            [x, z],
            [y, w]
        ]
        
        # Create lattice
        lattice = PartiallyDefinedLattice("MultiLattice", joins, meets)
        
        # Test counts
        result_joins = lattice.get_defined_joins()
        result_meets = lattice.get_defined_meets()
        
        self.assertEqual(len(result_joins), 2)
        self.assertEqual(len(result_meets), 2)
    
    def test_string_representation(self):
        """Test string representation of lattice."""
        PartiallyDefinedLattice = uacalc_lib.fplat.PartiallyDefinedLattice
        VariableImp = uacalc_lib.terms.VariableImp
        
        # Create variables
        x = VariableImp("x")
        y = VariableImp("y")
        
        # Create lattice
        lattice = PartiallyDefinedLattice("TestLattice", [[x, y]], [[x, y]])
        
        # Test string representations
        str_repr = str(lattice)
        repr_repr = repr(lattice)
        
        self.assertIn("TestLattice", str_repr)
        self.assertIn("TestLattice", repr_repr)
    
    def test_empty_joins_meets(self):
        """Test lattice with empty joins and meets."""
        PartiallyDefinedLattice = uacalc_lib.fplat.PartiallyDefinedLattice
        
        # Create lattice with empty joins and meets
        lattice = PartiallyDefinedLattice("EmptyLattice", [], [])
        
        # Test that it was created successfully
        self.assertEqual(lattice.name(), "EmptyLattice")
        
        # Test that joins and meets are empty
        self.assertEqual(len(lattice.get_defined_joins()), 0)
        self.assertEqual(len(lattice.get_defined_meets()), 0)
    
    def test_single_variable_joins_meets(self):
        """Test lattice with single-variable joins and meets."""
        PartiallyDefinedLattice = uacalc_lib.fplat.PartiallyDefinedLattice
        VariableImp = uacalc_lib.terms.VariableImp
        
        # Create variables
        x = VariableImp("x")
        y = VariableImp("y")
        
        # Create joins and meets with single variables
        joins = [[x], [y]]
        meets = [[x], [y]]
        
        # Create lattice
        lattice = PartiallyDefinedLattice("SingleVarLattice", joins, meets)
        
        # Test counts
        result_joins = lattice.get_defined_joins()
        result_meets = lattice.get_defined_meets()
        
        self.assertEqual(len(result_joins), 2)
        self.assertEqual(len(result_meets), 2)
        self.assertEqual(len(result_joins[0]), 1)
        self.assertEqual(len(result_meets[0]), 1)


if __name__ == '__main__':
    unittest.main()
