#!/usr/bin/env python3
"""
Test to demonstrate the comprehensive Java compatibility testing framework
"""

import unittest
from tests.python.test_data_manager import TestDataManager, TestCaseGenerator, AlgebraComplexity

class ComprehensiveFrameworkTest(unittest.TestCase):
    """Test the comprehensive testing framework components"""
    
    def setUp(self):
        self.data_manager = TestDataManager()
        self.test_case_generator = TestCaseGenerator(self.data_manager)
    
    def test_algebra_discovery(self):
        """Test that algebras are discovered and categorized correctly"""
        algebras = self.data_manager.discover_algebras()
        self.assertGreater(len(algebras), 0, "Should discover at least one algebra")
        
        # Test metadata extraction
        for algebra_file in algebras[:3]:  # Test first 3
            metadata = self.data_manager.algebra_metadata.get(str(algebra_file))
            self.assertIsNotNone(metadata, f"Should have metadata for {algebra_file}")
            self.assertGreater(metadata.cardinality, 0, "Cardinality should be positive")
            self.assertGreater(metadata.operation_count, 0, "Should have at least one operation")
            self.assertIsInstance(metadata.complexity, AlgebraComplexity)
    
    def test_complexity_categorization(self):
        """Test that algebras are categorized by complexity correctly"""
        algebras = self.data_manager.discover_algebras()
        
        # Get algebras by complexity
        trivial = self.data_manager.get_algebras_by_complexity(AlgebraComplexity.TRIVIAL)
        small = self.data_manager.get_algebras_by_complexity(AlgebraComplexity.SMALL)
        medium = self.data_manager.get_algebras_by_complexity(AlgebraComplexity.MEDIUM)
        
        # Verify complexity categorization
        for algebra_file in trivial:
            metadata = self.data_manager.algebra_metadata[str(algebra_file)]
            self.assertLessEqual(metadata.cardinality, 2, "Trivial algebras should have cardinality <= 2")
        
        for algebra_file in small:
            metadata = self.data_manager.algebra_metadata[str(algebra_file)]
            self.assertTrue(3 <= metadata.cardinality <= 5, "Small algebras should have cardinality 3-5")
        
        for algebra_file in medium:
            metadata = self.data_manager.algebra_metadata[str(algebra_file)]
            self.assertTrue(6 <= metadata.cardinality <= 10, "Medium algebras should have cardinality 6-10")
    
    def test_test_case_generation(self):
        """Test that test cases are generated systematically"""
        # Test operation test case generation
        binary_cases = self.test_case_generator.generate_operation_test_cases(2, 3, 10)
        self.assertGreater(len(binary_cases), 0, "Should generate test cases for binary operations")
        
        # All cases should have arity 2
        for case in binary_cases:
            self.assertEqual(len(case), 2, "Binary operation cases should have 2 arguments")
            self.assertTrue(all(0 <= arg < 3 for arg in case), "Arguments should be in range [0, 3)")
        
        # Test nullary operation
        nullary_cases = self.test_case_generator.generate_operation_test_cases(0, 5, 10)
        self.assertEqual(len(nullary_cases), 1, "Nullary operation should have one test case")
        self.assertEqual(nullary_cases[0], [], "Nullary operation case should be empty")
    
    def test_comprehensive_test_plan_generation(self):
        """Test that comprehensive test plans are generated"""
        test_plan = self.test_case_generator.generate_comprehensive_test_plan()
        
        # Verify all test categories are present
        expected_categories = [
            "algebra_properties", "congruence_generation", "subalgebra_generation",
            "isomorphism_checking", "maltsev_conditions", "operation_evaluation"
        ]
        
        for category in expected_categories:
            self.assertIn(category, test_plan, f"Test plan should include {category}")
            self.assertIsInstance(test_plan[category], list, f"{category} should be a list")
        
        # Verify algebra properties tests include all algebras
        self.assertGreater(len(test_plan["algebra_properties"]), 0, 
                          "Should have algebra properties tests")
        
        # Verify operation evaluation tests have proper structure
        if test_plan["operation_evaluation"]:
            op_test = test_plan["operation_evaluation"][0]
            required_fields = ["file", "name", "operation_symbol", "operation_arity", "test_cases"]
            for field in required_fields:
                self.assertIn(field, op_test, f"Operation test should have {field}")
    
    def test_algebra_summary_statistics(self):
        """Test that summary statistics are computed correctly"""
        algebras = self.data_manager.discover_algebras()
        summary = self.data_manager.get_algebra_summary()
        
        if algebras:
            self.assertIn("total_algebras", summary)
            self.assertEqual(summary["total_algebras"], len(algebras))
            self.assertIn("complexity_distribution", summary)
            self.assertIn("average_cardinality", summary)
            self.assertIn("average_operations", summary)
            
            # Verify averages are reasonable
            self.assertGreater(summary["average_cardinality"], 0)
            self.assertGreater(summary["average_operations"], 0)

if __name__ == '__main__':
    unittest.main()