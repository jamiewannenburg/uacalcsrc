"""
Example tests demonstrating algebra loading patterns.

This file shows best practices for loading and testing with algebras.
"""

import unittest
import pytest
import os
import uacalc_lib


class TestAlgebraLoadingPatterns(unittest.TestCase):
    """Examples of different algebra loading patterns."""
    
    def test_direct_algebra_loading(self):
        """Example: Direct algebra loading with skip on missing."""
        algebra_path = "resources/algebras/cyclic3.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Use algebra for testing
        self.assertIsNotNone(alg)
        self.assertGreater(alg.cardinality(), 0)
    
    def test_with_helper_function(self):
        """Example: Using load_test_algebra helper from conftest."""
        from conftest import load_test_algebra
        
        alg = load_test_algebra("cyclic2")
        
        # Use algebra for testing
        VariableImp = uacalc_lib.terms.VariableImp
        x = VariableImp("x")
        
        result = x.eval(alg, {"x": 0})
        self.assertEqual(result, 0)
    
    def test_with_multiple_algebras(self):
        """Example: Testing with multiple algebras."""
        from conftest import load_test_algebra
        
        algebra_names = ["cyclic2", "cyclic3", "n5"]
        
        for name in algebra_names:
            with self.subTest(algebra=name):
                try:
                    alg = load_test_algebra(name, skip_if_missing=False)
                except FileNotFoundError:
                    self.skipTest(f"Algebra {name} not found")
                
                # Test variable evaluation
                VariableImp = uacalc_lib.terms.VariableImp
                x = VariableImp("x")
                
                result = x.eval(alg, {"x": 0})
                self.assertEqual(result, 0)
    
    @classmethod
    def setUpClass(cls):
        """Example: Load algebras once for entire test class."""
        from conftest import load_test_algebra
        
        cls.algebras = {}
        
        for name in ["cyclic2", "cyclic3"]:
            try:
                cls.algebras[name] = load_test_algebra(name, skip_if_missing=False)
            except (FileNotFoundError, Exception):
                pass  # Skip if not available
    
    def test_with_class_loaded_algebra(self):
        """Example: Using algebra loaded in setUpClass."""
        if "cyclic2" not in self.algebras:
            self.skipTest("cyclic2 not available")
        
        alg = self.algebras["cyclic2"]
        
        VariableImp = uacalc_lib.terms.VariableImp
        x = VariableImp("x")
        
        # Test both elements
        for i in range(2):
            result = x.eval(alg, {"x": i})
            self.assertEqual(result, i)


# Pytest-style tests with fixtures
class TestWithPytestFixtures:
    """Examples using pytest fixtures from conftest.py"""
    
    def test_with_cyclic2_fixture(self, cyclic2_algebra):
        """Example: Using cyclic2_algebra fixture."""
        alg = cyclic2_algebra
        
        VariableImp = uacalc_lib.terms.VariableImp
        x = VariableImp("x")
        
        result = x.eval(alg, {"x": 1})
        assert result == 1
    
    def test_with_cyclic3_fixture(self, cyclic3_algebra):
        """Example: Using cyclic3_algebra fixture."""
        alg = cyclic3_algebra
        
        VariableImp = uacalc_lib.terms.VariableImp
        x = VariableImp("x")
        
        # Test all elements
        for i in range(3):
            result = x.eval(alg, {"x": i})
            assert result == i
    
    def test_with_parameterized_fixture(self, test_algebra):
        """Example: Using parameterized test_algebra fixture."""
        # This test runs once for each algebra in the fixture params
        alg = test_algebra
        
        VariableImp = uacalc_lib.terms.VariableImp
        x = VariableImp("x")
        
        # Test first element
        result = x.eval(alg, {"x": 0})
        assert result == 0
    
    def test_with_algebra_loader_fixture(self, algebra_loader):
        """Example: Using algebra_loader fixture."""
        # Load specific algebra on demand
        alg = algebra_loader("cyclic3")
        
        VariableImp = uacalc_lib.terms.VariableImp
        x = VariableImp("x")
        
        result = x.eval(alg, {"x": 2})
        assert result == 2


# Parameterized tests
@pytest.mark.parametrize("algebra_name,size", [
    ("cyclic2", 2),
    ("cyclic3", 3),
])
def test_algebra_size(algebra_name, size, algebra_loader):
    """Example: Parameterized test with algebra loading."""
    alg = algebra_loader(algebra_name)
    assert alg.cardinality() == size


@pytest.mark.parametrize("algebra_name", ["cyclic2", "cyclic3", "n5"])
def test_variable_evaluation(algebra_name, algebra_loader):
    """Example: Test variable evaluation across algebras."""
    alg = algebra_loader(algebra_name)
    
    VariableImp = uacalc_lib.terms.VariableImp
    x = VariableImp("x")
    
    # Variable evaluation should return the value from the map
    result = x.eval(alg, {"x": 0})
    assert result == 0


class TestAdvancedPatterns:
    """Advanced testing patterns with algebras."""
    
    def test_with_custom_algebra_path(self):
        """Example: Loading from custom path."""
        custom_path = "resources/algebras/cyclic2.ua"
        
        if not os.path.exists(custom_path):
            pytest.skip(f"Custom algebra {custom_path} not found")
        
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(custom_path)
        alg = reader.read_algebra_file()
        
        assert alg is not None
        assert alg.cardinality() > 0
    
    def test_algebra_operations(self, cyclic3_algebra):
        """Example: Testing algebra operations."""
        alg = cyclic3_algebra
        
        # Get algebra info
        cardinality = alg.cardinality()
        assert cardinality == 3
        
        # Test with variables
        VariableImp = uacalc_lib.terms.VariableImp
        x = VariableImp("x")
        y = VariableImp("y")
        
        # Test multiple variables
        result_x = x.eval(alg, {"x": 1, "y": 2})
        result_y = y.eval(alg, {"x": 1, "y": 2})
        
        assert result_x == 1
        assert result_y == 2
    
    def test_error_handling(self, cyclic2_algebra):
        """Example: Testing error conditions."""
        alg = cyclic2_algebra
        
        VariableImp = uacalc_lib.terms.VariableImp
        x = VariableImp("x")
        
        # Should raise error when variable not in map
        with pytest.raises(ValueError):
            x.eval(alg, {})  # Missing 'x'
        
        # Should raise error with wrong variable name
        with pytest.raises(ValueError):
            x.eval(alg, {"y": 0})  # Wrong variable name


if __name__ == '__main__':
    # Run unittest tests
    unittest.main(argv=[''], verbosity=2, exit=False)
    
    # Run pytest tests
    pytest.main([__file__, '-v'])
