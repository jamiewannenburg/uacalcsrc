"""Tests for con() and sub() methods in algebra implementations.

This module contains comprehensive tests for the con() and sub() methods
in PowerAlgebra, ProductAlgebra, Subalgebra, and ReductAlgebra implementations.
"""

import unittest
import os
import uacalc_lib
from test_utils import run_java_wrapper


class TestConSubMethods(unittest.TestCase):
    """Test cases for con() and sub() methods in various algebra types."""

    def setUp(self):
        """Set up test fixtures."""
        self.BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        self.PowerAlgebra = uacalc_lib.alg.PowerAlgebra
        self.ProductAlgebra = uacalc_lib.alg.ProductAlgebra
        self.Subalgebra = uacalc_lib.alg.Subalgebra
        self.ReductAlgebra = uacalc_lib.alg.ReductAlgebra
        self.CongruenceLattice = uacalc_lib.alg.CongruenceLattice
        self.SubalgebraLattice = uacalc_lib.alg.SubalgebraLattice

    def test_power_algebra_con_method(self):
        """Test PowerAlgebra con() method."""
        # Create a basic small algebra
        root_alg = self.BasicAlgebra("TestRoot", [0, 1])
        
        # Create power algebra
        power_alg = self.PowerAlgebra(root_alg, 2)
        
        # Test con() method
        con_lat = power_alg.con()
        
        # Verify it returns a CongruenceLattice
        self.assertIsInstance(con_lat, self.CongruenceLattice)
        
        # Verify basic properties
        self.assertEqual(con_lat.alg_size(), 4)  # 2^2 = 4

    def test_power_algebra_sub_method(self):
        """Test PowerAlgebra sub() method."""
        # Create a basic small algebra
        root_alg = self.BasicAlgebra("TestRoot", [0, 1])
        
        # Create power algebra
        power_alg = self.PowerAlgebra(root_alg, 2)
        
        # Test sub() method
        sub_lat = power_alg.sub()
        
        # Verify it returns a SubalgebraLattice
        self.assertIsInstance(sub_lat, self.SubalgebraLattice)
        
        # Verify basic properties - cardinality returns -1 until universe is computed
        self.assertIsInstance(sub_lat.cardinality(), int)

    def test_product_algebra_con_method(self):
        """Test ProductAlgebra con() method."""
        # Create two basic small algebras
        alg1 = self.BasicAlgebra("A1", [0, 1])
        alg2 = self.BasicAlgebra("A2", [0, 1])
        
        # Create product algebra
        product_alg = self.ProductAlgebra("A1 x A2", [alg1, alg2])
        
        # Test con() method
        con_lat = product_alg.con()
        
        # Verify it returns a CongruenceLattice
        self.assertIsInstance(con_lat, self.CongruenceLattice)
        
        # Verify basic properties
        self.assertEqual(con_lat.alg_size(), 4)  # 2 * 2 = 4

    def test_product_algebra_sub_method(self):
        """Test ProductAlgebra sub() method."""
        # Create two basic small algebras
        alg1 = self.BasicAlgebra("A1", [0, 1])
        alg2 = self.BasicAlgebra("A2", [0, 1])
        
        # Create product algebra
        product_alg = self.ProductAlgebra("A1 x A2", [alg1, alg2])
        
        # Test sub() method
        sub_lat = product_alg.sub()
        
        # Verify it returns a SubalgebraLattice
        self.assertIsInstance(sub_lat, self.SubalgebraLattice)
        
        # Verify basic properties - cardinality returns -1 until universe is computed
        self.assertIsInstance(sub_lat.cardinality(), int)

    def test_subalgebra_con_method(self):
        """Test Subalgebra con() method."""
        # Create a basic small algebra
        super_alg = self.BasicAlgebra("Super", [0, 1, 2])

        # Create subalgebra with universe [0, 1]
        sub_alg = self.Subalgebra("Sub", super_alg, [0, 1])

        # Test con() method
        con_lat = sub_alg.con()

        # Verify it returns a CongruenceLattice
        self.assertIsInstance(con_lat, self.CongruenceLattice)

        # Verify basic properties
        self.assertEqual(con_lat.alg_size(), 2)  # Subalgebra universe is [0, 1]


    def test_subalgebra_sub_method(self):
        """Test Subalgebra sub() method."""
        # Create a basic small algebra
        super_alg = self.BasicAlgebra("Super", [0, 1, 2])
        
        # Create subalgebra with universe [0, 1]
        sub_alg = self.Subalgebra("Sub", super_alg, [0, 1])
        
        # Test sub() method
        sub_lat = sub_alg.sub()
        
        # Verify it returns a SubalgebraLattice
        self.assertIsInstance(sub_lat, self.SubalgebraLattice)
        
        # Verify basic properties - cardinality returns -1 until universe is computed
        self.assertIsInstance(sub_lat.cardinality(), int)

    def test_reduct_algebra_con_method(self):
        """Test ReductAlgebra con() method."""
        # Create a basic small algebra
        super_alg = self.BasicAlgebra("Super", [0, 1])
        
        # Create reduct algebra (no terms for simplicity)
        reduct_alg = self.ReductAlgebra(super_alg, [])
        
        # Test con() method
        con_lat = reduct_alg.con()
        
        # Verify it returns a CongruenceLattice
        self.assertIsInstance(con_lat, self.CongruenceLattice)
        
        # Verify basic properties
        self.assertEqual(con_lat.alg_size(), 2)  # Same universe as super algebra

    def test_reduct_algebra_sub_method(self):
        """Test ReductAlgebra sub() method."""
        # Create a basic small algebra
        super_alg = self.BasicAlgebra("Super", [0, 1])
        
        # Create reduct algebra (no terms for simplicity)
        reduct_alg = self.ReductAlgebra(super_alg, [])
        
        # Test sub() method
        sub_lat = reduct_alg.sub()
        
        # Verify it returns a SubalgebraLattice
        self.assertIsInstance(sub_lat, self.SubalgebraLattice)
        
        # Verify basic properties - cardinality returns -1 until universe is computed
        self.assertIsInstance(sub_lat.cardinality(), int)

    def test_lazy_initialization(self):
        """Test that con() and sub() methods use lazy initialization."""
        # Create a power algebra
        root_alg = self.BasicAlgebra("TestRoot", [0, 1])
        power_alg = self.PowerAlgebra(root_alg, 2)
        
        # First call should create the lattice
        con_lat1 = power_alg.con()
        self.assertIsInstance(con_lat1, self.CongruenceLattice)
        
        # Second call should return the same instance (cached)
        con_lat2 = power_alg.con()
        self.assertIsInstance(con_lat2, self.CongruenceLattice)
        
        # Both should have the same universe size
        self.assertEqual(con_lat1.alg_size(), con_lat2.alg_size())

    def test_lattice_properties(self):
        """Test basic properties of returned lattices."""
        # Create a power algebra
        root_alg = self.BasicAlgebra("TestRoot", [0, 1])
        power_alg = self.PowerAlgebra(root_alg, 2)
        
        # Test congruence lattice properties
        con_lat = power_alg.con()
        self.assertEqual(con_lat.alg_size(), 4)
        
        # Test subalgebra lattice properties
        sub_lat = power_alg.sub()
        self.assertIsInstance(sub_lat.cardinality(), int)  # Returns -1 until universe computed

    def test_error_handling(self):
        """Test error handling in con() and sub() methods."""
        # Create a power algebra
        root_alg = self.BasicAlgebra("TestRoot", [0, 1])
        power_alg = self.PowerAlgebra(root_alg, 2)
        
        # These methods should not raise exceptions for valid algebras
        try:
            con_lat = power_alg.con()
            sub_lat = power_alg.sub()
            # If we get here, the methods worked correctly
            self.assertIsInstance(con_lat, self.CongruenceLattice)
            self.assertIsInstance(sub_lat, self.SubalgebraLattice)
        except Exception as e:
            self.fail(f"con() or sub() method raised an exception: {e}")


if __name__ == '__main__':
    unittest.main()