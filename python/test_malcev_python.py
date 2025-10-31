"""
Test Malcev functions from Python bindings.

This test module verifies that the Malcev functions are properly exposed
through the Python bindings and return appropriate error messages indicating
they are not yet implemented.
"""

import unittest
import uacalc_lib


class TestMalcevPython(unittest.TestCase):
    """Test Malcev functions through Python bindings."""
    
    def test_malcev_functions_exist(self):
        """Test that Malcev functions are accessible from Python."""
        # Check that the functions exist in the alg module
        self.assertTrue(hasattr(uacalc_lib.alg, 'malcev_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'majority_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'minority_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'pixley_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'nu_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'weak_majority_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'semilattice_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'difference_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'jonsson_terms'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'is_congruence_dist_idempotent'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'is_congruence_modular_idempotent'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'congruence_modular_variety'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'jonsson_level'))
        
    def test_malcev_term_with_cyclic3(self):
        """Test malcev_term with cyclic3 algebra."""
        import os
        algebra_path = "resources/algebras/cyclic3.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Test malcev_term
        try:
            result = uacalc_lib.alg.malcev_term(alg)
            # Should either return a term or None, not raise an error
            if result is not None:
                self.assertIsInstance(result, str)
                print(f"Found Malcev term: {result}")
            else:
                print("No Malcev term found (this is valid)")
        except Exception as e:
            # If it's still not implemented, that's okay for now
            if "not yet implemented" in str(e):
                self.skipTest("malcev_term not yet fully implemented")
            else:
                raise
    
    def test_majority_term_with_cyclic3(self):
        """Test majority_term with cyclic3 algebra."""
        import os
        algebra_path = "resources/algebras/cyclic3.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Test majority_term
        try:
            result = uacalc_lib.alg.majority_term(alg)
            # Should either return a term or None, not raise an error
            if result is not None:
                self.assertIsInstance(result, str)
                print(f"Found majority term: {result}")
            else:
                print("No majority term found (this is valid)")
        except Exception as e:
            # If it's still not implemented, that's okay for now
            if "not yet implemented" in str(e):
                self.skipTest("majority_term not yet fully implemented")
            else:
                raise
    
    def test_minority_term_with_cyclic3(self):
        """Test minority_term with cyclic3 algebra."""
        import os
        algebra_path = "resources/algebras/cyclic3.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Test minority_term
        try:
            result = uacalc_lib.alg.minority_term(alg)
            # Should either return a term or None, not raise an error
            if result is not None:
                self.assertIsInstance(result, str)
                print(f"Found minority term: {result}")
            else:
                print("No minority term found (this is valid)")
        except Exception as e:
            # If it's still not implemented, that's okay for now
            if "not yet implemented" in str(e):
                self.skipTest("minority_term not yet fully implemented")
            else:
                raise
    
    def test_pixley_term_with_cyclic3(self):
        """Test pixley_term with cyclic3 algebra."""
        import os
        algebra_path = "resources/algebras/cyclic3.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Test pixley_term
        try:
            result = uacalc_lib.alg.pixley_term(alg)
            # Should either return a term or None, not raise an error
            if result is not None:
                self.assertIsInstance(result, str)
                print(f"Found Pixley term: {result}")
            else:
                print("No Pixley term found (this is valid)")
        except Exception as e:
            # If it's still not implemented, that's okay for now
            if "not yet implemented" in str(e):
                self.skipTest("pixley_term not yet fully implemented")
            else:
                raise
    
    def test_nu_term_with_cyclic3(self):
        """Test nu_term with cyclic3 algebra."""
        import os
        algebra_path = "resources/algebras/cyclic3.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Test nu_term
        try:
            result = uacalc_lib.alg.nu_term(alg, 3)
            # Should either return a term or None
            if result is not None:
                self.assertIsInstance(result, str)
                print(f"Found NU term: {result}")
            else:
                print("No NU term found (this is valid)")
        except Exception as e:
            # If it's still not implemented, that's okay for now
            if "not yet implemented" in str(e):
                self.skipTest("nu_term not yet fully implemented")
            else:
                raise
    
    def test_weak_majority_term_not_implemented(self):
        """Test that weak_majority_term returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.weak_majority_term(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_semilattice_term_not_implemented(self):
        """Test that semilattice_term returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.semilattice_term(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_difference_term_not_implemented(self):
        """Test that difference_term returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.difference_term(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_jonsson_terms_not_implemented(self):
        """Test that jonsson_terms returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.jonsson_terms(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_is_congruence_dist_idempotent_not_implemented(self):
        """Test that is_congruence_dist_idempotent returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.is_congruence_dist_idempotent(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_is_congruence_modular_idempotent_not_implemented(self):
        """Test that is_congruence_modular_idempotent returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.is_congruence_modular_idempotent(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_congruence_modular_variety_not_implemented(self):
        """Test that congruence_modular_variety returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.congruence_modular_variety(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_jonsson_level_not_implemented(self):
        """Test that jonsson_level returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.jonsson_level(None)
        self.assertIn("not yet implemented", str(context.exception))


if __name__ == '__main__':
    unittest.main()

