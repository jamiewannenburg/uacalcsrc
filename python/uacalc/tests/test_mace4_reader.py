import unittest
import os
import uacalc_lib

class TestMace4Reader(unittest.TestCase):
    """Test Mace4Reader functionality."""
    
    def test_is_ordinary_character(self):
        """Test is_ordinary_character method."""
        Mace4Reader = uacalc_lib.io.Mace4Reader
        
        # Test ordinary characters
        self.assertTrue(Mace4Reader.is_ordinary_character('a'))
        self.assertTrue(Mace4Reader.is_ordinary_character('A'))
        self.assertTrue(Mace4Reader.is_ordinary_character('z'))
        self.assertTrue(Mace4Reader.is_ordinary_character('Z'))
        self.assertTrue(Mace4Reader.is_ordinary_character('$'))
        self.assertTrue(Mace4Reader.is_ordinary_character('_'))
        
        # Test non-ordinary characters
        self.assertFalse(Mace4Reader.is_ordinary_character('1'))
        self.assertFalse(Mace4Reader.is_ordinary_character('+'))
        self.assertFalse(Mace4Reader.is_ordinary_character('-'))
        self.assertFalse(Mace4Reader.is_ordinary_character(' '))
    
    def test_is_special_character(self):
        """Test is_special_character method."""
        Mace4Reader = uacalc_lib.io.Mace4Reader
        
        # Test special characters
        self.assertTrue(Mace4Reader.is_special_character('+'))
        self.assertTrue(Mace4Reader.is_special_character('-'))
        self.assertTrue(Mace4Reader.is_special_character('*'))
        self.assertTrue(Mace4Reader.is_special_character('/'))
        self.assertTrue(Mace4Reader.is_special_character('{'))
        self.assertTrue(Mace4Reader.is_special_character('}'))
        self.assertTrue(Mace4Reader.is_special_character('='))
        self.assertTrue(Mace4Reader.is_special_character('<'))
        self.assertTrue(Mace4Reader.is_special_character('>'))
        
        # Test non-special characters
        self.assertFalse(Mace4Reader.is_special_character('a'))
        self.assertFalse(Mace4Reader.is_special_character('1'))
        self.assertFalse(Mace4Reader.is_special_character(' '))
    
    def test_parse_simple_algebra(self):
        """Test parsing a simple algebra."""
        Mace4Reader = uacalc_lib.io.Mace4Reader
        
        # Use the real Mace4 file
        algebra = Mace4Reader.parse_algebra_from_file("resources/mace4/KR-8.model")
        
        self.assertIsNotNone(algebra)
        self.assertEqual(algebra.name(), "model1")
        self.assertEqual(algebra.cardinality(), 8)
        operations = algebra.operations()
        self.assertEqual(len(operations), 6)
        # Check that operations are Operation objects (IntOperation or BasicOperation)
        for op in operations:
            # Operations should have arity() and symbol() methods
            self.assertTrue(hasattr(op, 'arity'))
            self.assertTrue(hasattr(op, 'symbol'))
            # Check that we can access name and arity
            self.assertIsInstance(op.symbol().name(), str)  # name
            self.assertIsInstance(op.arity(), int)  # arity
    
    def test_parse_algebra_with_multiple_operations(self):
        """Test parsing an algebra with multiple operations."""
        Mace4Reader = uacalc_lib.io.Mace4Reader
    
        # Use the real Mace4 file which has multiple operations
        algebra = Mace4Reader.parse_algebra_from_file("resources/mace4/KR-8.model")
    
        self.assertIsNotNone(algebra)
        self.assertEqual(algebra.name(), "model1")
        self.assertEqual(algebra.cardinality(), 8)
        operations = algebra.operations()
        self.assertEqual(len(operations), 6)  # KR-8.model has 6 operations
        # Check that operations are Operation objects (IntOperation or BasicOperation)
        for op in operations:
            # Operations should have arity() and symbol() methods
            self.assertTrue(hasattr(op, 'arity'))
            self.assertTrue(hasattr(op, 'symbol'))
            # Check that we can access name and arity
            self.assertIsInstance(op.symbol().name(), str)  # name
            self.assertIsInstance(op.arity(), int)  # arity
    
    def test_parse_algebra_list(self):
        """Test parsing a list of algebras."""
        Mace4Reader = uacalc_lib.io.Mace4Reader
    
        # Use the real Mace4 file which contains multiple algebras
        algebras = Mace4Reader.parse_algebra_list_from_file("resources/mace4/KR-8-expl.model")
        algebras = list(algebras)
        self.assertGreaterEqual(len(algebras), 2)  # KR-8-expl.model contains at least 2 algebras
    
        # Check algebras
        for alg in algebras:
            # Names should start with "model" (e.g., "model1", "model3")
            self.assertTrue(alg.name().startswith("model"), f"Expected name to start with 'model', got '{alg.name()}'")
            self.assertEqual(alg.cardinality(), 8)
            operations = alg.operations()
            self.assertEqual(len(operations), 6)
            # Check that operations are Operation objects (IntOperation or BasicOperation)
            for op in operations:
                # Operations should have arity() and symbol() methods
                self.assertTrue(hasattr(op, 'arity'))
                self.assertTrue(hasattr(op, 'symbol'))
                # Check that we can access name and arity
                self.assertIsInstance(op.symbol().name(), str)  # name
                self.assertIsInstance(op.arity(), int)  # arity
    
    def test_parse_algebra_error_handling(self):
        """Test error handling with invalid input."""
        Mace4Reader = uacalc_lib.io.Mace4Reader
        
        # Test with invalid input (no interpretation found)
        invalid_input = "invalid input"
        
        reader = Mace4Reader.new_from_stream(invalid_input.encode('utf-8'))
        algebra = reader.parse_algebra_from_stream(invalid_input.encode('utf-8'))
        
        # Should return None for invalid input
        self.assertIsNone(algebra)
    
    def test_parse_algebra_malformed_syntax(self):
        """Test error handling with malformed syntax."""
        Mace4Reader = uacalc_lib.io.Mace4Reader
        
        # Test with malformed syntax (missing closing parenthesis)
        malformed_input = "interpretation(2, [number=1], [function(f, (_,_), [0,1,1,0])"
        
        reader = Mace4Reader.new_from_stream(malformed_input.encode('utf-8'))
        
        # Should raise an exception for malformed syntax
        with self.assertRaises(Exception):
            reader.parse_algebra()
    
    def test_character_classification_comprehensive(self):
        """Test comprehensive character classification."""
        Mace4Reader = uacalc_lib.io.Mace4Reader
        
        # Test all ordinary characters
        ordinary_chars = ['a', 'b', 'c', 'A', 'B', 'C', 'z', 'Z', '$', '_']
        for c in ordinary_chars:
            self.assertTrue(Mace4Reader.is_ordinary_character(c), f"Character '{c}' should be ordinary")
            self.assertFalse(Mace4Reader.is_special_character(c), f"Character '{c}' should not be special")
        
        # Test all special characters
        special_chars = ['{', '+', '-', '*', '/', '\\', '^', '<', '>', '=', '`', '~', '?', '@', '&', '|', '!', '#', '\'', ';', '}']
        for c in special_chars:
            self.assertTrue(Mace4Reader.is_special_character(c), f"Character '{c}' should be special")
            self.assertFalse(Mace4Reader.is_ordinary_character(c), f"Character '{c}' should not be ordinary")
        
        # Test digits (should be neither ordinary nor special in first character context)
        digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for c in digits:
            self.assertFalse(Mace4Reader.is_ordinary_character(c), f"Digit '{c}' should not be ordinary")
            self.assertFalse(Mace4Reader.is_special_character(c), f"Digit '{c}' should not be special")
    
    def test_reader_creation_from_file(self):
        """Test creating reader from file."""
        Mace4Reader = uacalc_lib.io.Mace4Reader
        
        # Use the real Mace4 file
        reader = Mace4Reader.new_from_file("resources/mace4/KR-8.model")
        algebra = reader.parse_algebra_from_file("resources/mace4/KR-8.model")
        
        self.assertIsNotNone(algebra)
        self.assertEqual(algebra.name(), "model1")
        self.assertEqual(algebra.cardinality(), 8)
    
    def test_reader_string_representation(self):
        """Test reader string representation."""
        Mace4Reader = uacalc_lib.io.Mace4Reader
        
        reader = Mace4Reader.new_from_file("resources/mace4/KR-8.model")
        
        # Test string representation
        str_repr = str(reader)
        self.assertIn("Mace4Reader", str_repr)
        
        # Test repr representation
        repr_str = repr(reader)
        self.assertEqual(repr_str, "Mace4Reader()")

if __name__ == '__main__':
    unittest.main()
