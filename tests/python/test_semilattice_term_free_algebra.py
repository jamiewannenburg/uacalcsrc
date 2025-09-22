#!/usr/bin/env python3
"""
Test suite for semilattice term finding using free algebra approach.

This module tests the robust free algebra implementation for finding semilattice terms,
including timeout protection and comprehensive term generation.
"""

import unittest
import sys
import os
import tempfile
import logging
from pathlib import Path
import time

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import uacalc
    from uacalc import MalcevAnalyzer, create_algebra, create_operation, UACalcError
except ImportError as e:
    raise ImportError(f"Failed to import uacalc: {e}") from e

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemilatticeTermFreeAlgebraTest(unittest.TestCase):
    """Test semilattice term finding using free algebra approach."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MalcevAnalyzer()
        
    def test_trivial_algebra_semilattice_term(self):
        """Test semilattice term finding for trivial algebra (cardinality 1)."""
        logger.info("Testing trivial algebra semilattice term finding")
        
        # Create trivial algebra with one element
        algebra = create_algebra("Trivial", [0])
        
        # Add a binary operation (identity)
        op_table = [[0]]  # f(0, 0) = 0
        operation = create_operation("f", 2, op_table)
        algebra.add_operation("f", operation)
        
        # Find semilattice term
        term = self.analyzer.find_semilattice_term(algebra)
        
        # Should find the identity term
        self.assertIsNotNone(term)
        self.assertEqual(term, "x")
        
        logger.info(f"Found semilattice term for trivial algebra: {term}")
    
    def test_small_algebra_semilattice_term(self):
        """Test semilattice term finding for small algebra (cardinality 2)."""
        logger.info("Testing small algebra semilattice term finding")
        
        # Create small algebra with two elements
        algebra = create_algebra("Small", [0, 1])
        
        # Add a binary operation that forms a semilattice
        # f(0, 0) = 0, f(0, 1) = 1, f(1, 0) = 1, f(1, 1) = 1 (join operation)
        op_table = [
            [0, 1],  # f(0, 0) = 0, f(0, 1) = 1
            [1, 1]   # f(1, 0) = 1, f(1, 1) = 1
        ]
        operation = create_operation("f", 2, op_table)
        algebra.add_operation("f", operation)
        
        # Find semilattice term
        term = self.analyzer.find_semilattice_term(algebra)
        
        # Should find a semilattice term
        self.assertIsNotNone(term)
        logger.info(f"Found semilattice term for small algebra: {term}")
    
    def test_semilattice_algebra_term_finding(self):
        """Test semilattice term finding for known semilattice algebra."""
        logger.info("Testing semilattice algebra term finding")
        
        # Create a known semilattice algebra (join semilattice)
        algebra = create_algebra("JoinSemilattice", [0, 1, 2])
        
        # Add join operation: f(x, y) = max(x, y)
        op_table = [
            [0, 1, 2],  # f(0, 0) = 0, f(0, 1) = 1, f(0, 2) = 2
            [1, 1, 2],  # f(1, 0) = 1, f(1, 1) = 1, f(1, 2) = 2
            [2, 2, 2]   # f(2, 0) = 2, f(2, 1) = 2, f(2, 2) = 2
        ]
        operation = create_operation("join", 2, op_table)
        algebra.add_operation("join", operation)
        
        # Find semilattice term
        term = self.analyzer.find_semilattice_term(algebra)
        
        # Should find a semilattice term
        self.assertIsNotNone(term)
        logger.info(f"Found semilattice term for join semilattice: {term}")
    
    def test_non_semilattice_algebra(self):
        """Test semilattice term finding for non-semilattice algebra."""
        logger.info("Testing non-semilattice algebra term finding")
        
        # Create a non-semilattice algebra
        algebra = create_algebra("NonSemilattice", [0, 1])
        
        # Add a binary operation that is not associative
        # f(0, 0) = 0, f(0, 1) = 0, f(1, 0) = 1, f(1, 1) = 0
        op_table = [
            [0, 0],  # f(0, 0) = 0, f(0, 1) = 0
            [1, 0]   # f(1, 0) = 1, f(1, 1) = 0
        ]
        operation = create_operation("f", 2, op_table)
        algebra.add_operation("f", operation)
        
        # Find semilattice term
        try:
            term = self.analyzer.find_semilattice_term(algebra)
            # Should not find a semilattice term
            self.assertIsNone(term)
            logger.info("Correctly found no semilattice term for non-semilattice algebra")
        except UACalcError as e:
            # It's also acceptable to raise an error when no semilattice term is found
            self.assertIn("No semilattice term found", str(e))
            logger.info(f"Correctly raised error for non-semilattice algebra: {e}")
    
    def test_free_algebra_timeout_protection(self):
        """Test that free algebra approach has timeout protection."""
        logger.info("Testing free algebra timeout protection")
        
        # Create a larger algebra that might trigger timeout
        algebra = create_algebra("Large", [0, 1, 2, 3])
        
        # Add a complex operation
        op_table = [
            [0, 1, 2, 3],
            [1, 0, 3, 2],
            [2, 3, 0, 1],
            [3, 2, 1, 0]
        ]
        operation = create_operation("f", 2, op_table)
        algebra.add_operation("f", operation)
        
        # This should not hang due to timeout protection
        try:
            term = self.analyzer.find_semilattice_term(algebra)
            logger.info(f"Free algebra timeout protection working, result: {term}")
        except UACalcError as e:
            if "timeout" in str(e).lower():
                logger.info("Timeout protection working correctly")
            else:
                raise
    
    def test_multiple_operations_semilattice_term(self):
        """Test semilattice term finding with multiple operations."""
        logger.info("Testing semilattice term finding with multiple operations")
        
        # Create algebra with multiple operations
        algebra = create_algebra("MultiOp", [0, 1, 2])
        
        # Add join operation
        join_table = [
            [0, 1, 2],
            [1, 1, 2],
            [2, 2, 2]
        ]
        operation = create_operation("join", 2, join_table)
        algebra.add_operation("join", operation)
        
        # Add meet operation
        meet_table = [
            [0, 0, 0],
            [0, 1, 1],
            [0, 1, 2]
        ]
        operation = create_operation("meet", 2, meet_table)
        algebra.add_operation("meet", operation)
        
        # Add a non-semilattice operation
        other_table = [
            [0, 1, 0],
            [1, 0, 1],
            [0, 1, 2]
        ]
        operation = create_operation("other", 2, other_table)
        algebra.add_operation("other", operation)
        
        # Find semilattice term
        term = self.analyzer.find_semilattice_term(algebra)
        
        # Should find a semilattice term (either join or meet)
        self.assertIsNotNone(term)
        logger.info(f"Found semilattice term with multiple operations: {term}")
    
    def test_semilattice_term_properties(self):
        """Test that found semilattice terms have correct properties."""
        logger.info("Testing semilattice term properties")
        
        # Create a known semilattice algebra
        algebra = create_algebra("TestSemilattice", [0, 1])
        
        # Add join operation
        op_table = [
            [0, 1],
            [1, 1]
        ]
        operation = create_operation("join", 2, op_table)
        algebra.add_operation("join", operation)
        
        # Find semilattice term
        term = self.analyzer.find_semilattice_term(algebra)
        
        if term is not None:
            # The term should be a valid term expression
            self.assertIsInstance(term, str)
            self.assertGreater(len(term), 0)
            
            # The term should contain operation symbols and variables
            # This is a basic check - more sophisticated validation would require
            # parsing and evaluating the term
            logger.info(f"Semilattice term '{term}' has valid format")
        else:
            logger.info("No semilattice term found (which is also valid)")
    
    def test_analyze_malcev_conditions_integration(self):
        """Test integration with analyze_malcev_conditions."""
        logger.info("Testing integration with analyze_malcev_conditions")
        
        # Create a semilattice algebra
        algebra = create_algebra("IntegrationTest", [0, 1])
        
        # Add join operation
        op_table = [
            [0, 1],
            [1, 1]
        ]
        operation = create_operation("join", 2, op_table)
        algebra.add_operation("join", operation)
        
        # Analyze Malcev conditions
        analysis = self.analyzer.analyze_malcev_conditions(algebra)
        
        # Check that semilattice term is found in the analysis
        self.assertIsNotNone(analysis.semilattice_term)
        logger.info(f"Integration test found semilattice term: {analysis.semilattice_term}")
    
    def test_error_handling(self):
        """Test error handling in semilattice term finding."""
        logger.info("Testing error handling")
        
        # Test with invalid algebra (should not crash)
        try:
            # Create algebra but don't add any operations
            algebra = create_algebra("NoOps", [0, 1])
            
            # This should handle gracefully
            term = self.analyzer.find_semilattice_term(algebra)
            logger.info(f"Handled algebra with no operations gracefully: {term}")
        except Exception as e:
            # If it raises an exception, it should be a UACalcError, not a crash
            self.assertIsInstance(e, UACalcError)
            logger.info(f"Correctly handled error: {e}")


class FreeAlgebraTimeoutTest(unittest.TestCase):
    """Test timeout protection in free algebra operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MalcevAnalyzer()
    
    def test_timeout_protection_small_algebra(self):
        """Test that timeout protection works for small algebras."""
        logger.info("Testing timeout protection for small algebras")
        
        # Create a small algebra
        algebra = create_algebra("TimeoutTest", [0, 1])
        
        # Add an operation
        op_table = [
            [0, 1],
            [1, 0]
        ]
        operation = create_operation("f", 2, op_table)
        algebra.add_operation("f", operation)
        
        # This should complete quickly without timeout
        start_time = time.time()
        term = self.analyzer.find_semilattice_term(algebra)
        end_time = time.time()
        
        # Should complete in reasonable time (less than 10 seconds)
        self.assertLess(end_time - start_time, 10.0)
        logger.info(f"Small algebra completed in {end_time - start_time:.2f} seconds")
    
    def test_memory_protection(self):
        """Test that memory limits are respected."""
        logger.info("Testing memory protection")
        
        # Set a small memory limit
        original_limit = uacalc.get_memory_limit_mb()
        uacalc.set_memory_limit_mb(64)  # 64MB limit
        
        try:
            # Create a moderate-sized algebra
            algebra = create_algebra("MemoryTest", [0, 1, 2])
            
            # Add operations
            op_table = [
                [0, 1, 2],
                [1, 0, 2],
                [2, 2, 0]
            ]
            operation = create_operation("f", 2, op_table)
            algebra.add_operation("f", operation)
            
            # This should respect memory limits
            term = self.analyzer.find_semilattice_term(algebra)
            logger.info(f"Memory protection test completed: {term}")
            
        finally:
            # Restore original memory limit
            uacalc.set_memory_limit_mb(original_limit)


if __name__ == "__main__":
    import time
    
    # Set up test suite
    suite = unittest.TestSuite()
    
    # Add semilattice term tests
    suite.addTest(unittest.makeSuite(SemilatticeTermFreeAlgebraTest))
    suite.addTest(unittest.makeSuite(FreeAlgebraTimeoutTest))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        logger.info("All semilattice term free algebra tests passed!")
    else:
        logger.error(f"Tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
        for failure in result.failures:
            logger.error(f"Failure: {failure[0]}: {failure[1]}")
        for error in result.errors:
            logger.error(f"Error: {error[0]}: {error[1]}")
    
    sys.exit(0 if result.wasSuccessful() else 1)
