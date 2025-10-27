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
        
    def test_malcev_term_not_implemented(self):
        """Test that malcev_term returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.malcev_term(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_majority_term_not_implemented(self):
        """Test that majority_term returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.majority_term(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_minority_term_not_implemented(self):
        """Test that minority_term returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.minority_term(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_pixley_term_not_implemented(self):
        """Test that pixley_term returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.pixley_term(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_nu_term_not_implemented(self):
        """Test that nu_term returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.nu_term(None, 3)
        self.assertIn("not yet implemented", str(context.exception))
    
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

