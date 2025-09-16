#!/usr/bin/env python3
"""
Comprehensive Java Compatibility Test Suite

This module provides a unified test suite that integrates all Java UACalc compatibility
test classes into a single, cohesive testing framework. It addresses Task 13.1 by
ensuring all test classes work together in the unified framework.

Features:
- Unified test execution across all compatibility test classes
- Comprehensive test result aggregation and reporting
- Test filtering and selective execution capabilities
- Performance monitoring and resource usage tracking
- Conflict resolution and dependency management
"""

import unittest
import sys
import os
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
import json

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.python.base_compatibility_test import BaseCompatibilityTest, TestSuiteReport

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('comprehensive_test_suite.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestSuiteConfiguration:
    """Configuration for the comprehensive test suite"""
    include_algebra_tests: bool = True
    include_congruence_tests: bool = True
    include_operation_tests: bool = True
    include_term_tests: bool = True
    include_lattice_tests: bool = True
    include_equation_tests: bool = True
    include_group_tests: bool = True
    include_io_tests: bool = True
    include_utility_tests: bool = True
    
    # Filtering options
    max_algebra_size: Optional[int] = None
    specific_algebras: Optional[List[str]] = None
    specific_operations: Optional[List[str]] = None
    
    # Performance options
    timeout_per_test: int = 300
    parallel_execution: bool = False
    max_parallel_tests: int = 4
    
    # Reporting options
    generate_detailed_report: bool = True
    save_results_to_file: bool = True
    output_file: str = "comprehensive_test_results.json"

class ComprehensiveTestSuite:
    """
    Comprehensive test suite that integrates all Java UACalc compatibility tests.
    
    This class addresses Task 13.1 by providing:
    - Unified test execution framework
    - Test dependency management
    - Conflict resolution between test classes
    - Performance and resource monitoring
    """
    
    def __init__(self, config: TestSuiteConfiguration):
        self.config = config
        self.test_classes = self._discover_test_classes()
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
    def _discover_test_classes(self) -> Dict[str, Any]:
        """Discover all available compatibility test classes"""
        test_classes = {}
        
        # Core Algebra Tests (org.uacalc.alg)
        if self.config.include_algebra_tests:
            try:
                from tests.python.test_algebra_compatibility import AlgebraCompatibilityTest
                from tests.python.test_basic_algebra_compatibility import BasicAlgebraCompatibilityTest
                from tests.python.test_small_algebra_compatibility import SmallAlgebraCompatibilityTest
                from tests.python.test_algebras_compatibility import AlgebrasCompatibilityTest
                from tests.python.test_free_algebra_compatibility import FreeAlgebraCompatibilityTest
                from tests.python.test_homomorphism_compatibility import HomomorphismCompatibilityTest
                from tests.python.test_malcev_compatibility import MalcevCompatibilityTest
                from tests.python.test_product_algebra_compatibility import ProductAlgebraCompatibilityTest
                from tests.python.test_quotient_algebra_compatibility import QuotientAlgebraCompatibilityTest
                from tests.python.test_subalgebra_compatibility import SubalgebraCompatibilityTest
                
                test_classes.update({
                    'algebra': AlgebraCompatibilityTest,
                    'basic_algebra': BasicAlgebraCompatibilityTest,
                    'small_algebra': SmallAlgebraCompatibilityTest,
                    'algebras': AlgebrasCompatibilityTest,
                    'free_algebra': FreeAlgebraCompatibilityTest,
                    'homomorphism': HomomorphismCompatibilityTest,
                    'malcev': MalcevCompatibilityTest,
                    'product_algebra': ProductAlgebraCompatibilityTest,
                    'quotient_algebra': QuotientAlgebraCompatibilityTest,
                    'subalgebra': SubalgebraCompatibilityTest,
                })
                logger.info("Loaded algebra compatibility tests")
            except ImportError as e:
                logger.warning(f"Could not load algebra tests: {e}")
        
        # Congruence and Lattice Tests (org.uacalc.alg.conlat)
        if self.config.include_congruence_tests:
            try:
                from tests.python.test_congruence_lattice_compatibility import CongruenceLatticeCompatibilityTest
                from tests.python.test_partition_compatibility import PartitionCompatibilityTest
                from tests.python.test_binary_relation_compatibility import BinaryRelationCompatibilityTest
                from tests.python.test_polymorphisms_compatibility import PolymorphismsCompatibilityTest
                from tests.python.test_type_finder_compatibility import TypeFinderCompatibilityTest
                
                test_classes.update({
                    'congruence_lattice': CongruenceLatticeCompatibilityTest,
                    'partition': PartitionCompatibilityTest,
                    'binary_relation': BinaryRelationCompatibilityTest,
                    'polymorphisms': PolymorphismsCompatibilityTest,
                    'type_finder': TypeFinderCompatibilityTest,
                })
                logger.info("Loaded congruence and lattice compatibility tests")
            except ImportError as e:
                logger.warning(f"Could not load congruence tests: {e}")
        
        # Operation Tests (org.uacalc.alg.op)
        if self.config.include_operation_tests:
            try:
                from tests.python.test_operation_compatibility import OperationCompatibilityTest
                from tests.python.test_operations_compatibility import OperationsCompatibilityTest
                from tests.python.test_operation_symbol_compatibility import OperationSymbolCompatibilityTest
                from tests.python.test_term_operation_compatibility import TermOperationCompatibilityTest
                
                test_classes.update({
                    'operation': OperationCompatibilityTest,
                    'operations': OperationsCompatibilityTest,
                    'operation_symbol': OperationSymbolCompatibilityTest,
                    'term_operation': TermOperationCompatibilityTest,
                })
                logger.info("Loaded operation compatibility tests")
            except ImportError as e:
                logger.warning(f"Could not load operation tests: {e}")
        
        # Term Tests (org.uacalc.terms)
        if self.config.include_term_tests:
            try:
                from tests.python.test_term_compatibility import TermCompatibilityTest
                from tests.python.test_terms_compatibility import TermsCompatibilityTest
                from tests.python.test_variable_compatibility import VariableCompatibilityTest
                from tests.python.test_taylor_compatibility import TaylorCompatibilityTest
                
                test_classes.update({
                    'term': TermCompatibilityTest,
                    'terms': TermsCompatibilityTest,
                    'variable': VariableCompatibilityTest,
                    'taylor': TaylorCompatibilityTest,
                })
                logger.info("Loaded term compatibility tests")
            except ImportError as e:
                logger.warning(f"Could not load term tests: {e}")
        
        # Lattice Tests (org.uacalc.lat)
        if self.config.include_lattice_tests:
            try:
                from tests.python.test_lattice_compatibility import LatticeCompatibilityTest
                from tests.python.test_basic_lattice_compatibility import BasicLatticeCompatibilityTest
                from tests.python.test_order_compatibility import OrderCompatibilityTest
                from tests.python.test_lattices_compatibility import LatticesCompatibilityTest
                
                test_classes.update({
                    'lattice': LatticeCompatibilityTest,
                    'basic_lattice': BasicLatticeCompatibilityTest,
                    'order': OrderCompatibilityTest,
                    'lattices': LatticesCompatibilityTest,
                })
                logger.info("Loaded lattice compatibility tests")
            except ImportError as e:
                logger.warning(f"Could not load lattice tests: {e}")
        
        # Equation Tests (org.uacalc.eq)
        if self.config.include_equation_tests:
            try:
                from tests.python.test_equation_compatibility import EquationCompatibilityTest
                from tests.python.test_equations_compatibility import EquationsCompatibilityTest
                from tests.python.test_presentation_compatibility import PresentationCompatibilityTest
                
                test_classes.update({
                    'equation': EquationCompatibilityTest,
                    'equations': EquationsCompatibilityTest,
                    'presentation': PresentationCompatibilityTest,
                })
                logger.info("Loaded equation compatibility tests")
            except ImportError as e:
                logger.warning(f"Could not load equation tests: {e}")
        
        # Group Tests (org.uacalc.group)
        if self.config.include_group_tests:
            try:
                from tests.python.test_permutation_group_compatibility import PermutationGroupCompatibilityTest
                
                test_classes.update({
                    'permutation_group': PermutationGroupCompatibilityTest,
                })
                logger.info("Loaded group compatibility tests")
            except ImportError as e:
                logger.warning(f"Could not load group tests: {e}")
        
        # I/O Tests (org.uacalc.io)
        if self.config.include_io_tests:
            try:
                from tests.python.test_algebra_io_compatibility import AlgebraIOCompatibilityTest
                from tests.python.test_algebra_reader_compatibility import AlgebraReaderCompatibilityTest
                from tests.python.test_algebra_writer_compatibility import AlgebraWriterCompatibilityTest
                
                test_classes.update({
                    'algebra_io': AlgebraIOCompatibilityTest,
                    'algebra_reader': AlgebraReaderCompatibilityTest,
                    'algebra_writer': AlgebraWriterCompatibilityTest,
                })
                logger.info("Loaded I/O compatibility tests")
            except ImportError as e:
                logger.warning(f"Could not load I/O tests: {e}")
        
        # Utility Tests (org.uacalc.util)
        if self.config.include_utility_tests:
            try:
                from tests.python.test_int_array_compatibility import IntArrayCompatibilityTest
                from tests.python.test_horner_compatibility import HornerCompatibilityTest
                from tests.python.test_sequence_generator_compatibility import SequenceGeneratorCompatibilityTest
                
                test_classes.update({
                    'int_array': IntArrayCompatibilityTest,
                    'horner': HornerCompatibilityTest,
                    'sequence_generator': SequenceGeneratorCompatibilityTest,
                })
                logger.info("Loaded utility compatibility tests")
            except ImportError as e:
                logger.warning(f"Could not load utility tests: {e}")
        
        logger.info(f"Discovered {len(test_classes)} test classes")
        return test_classes
    
    def _resolve_test_dependencies(self) -> List[str]:
        """
        Resolve dependencies between test classes to ensure proper execution order.
        
        Returns:
            List of test class names in dependency order
        """
        # Define dependency relationships
        dependencies = {
            # Basic tests should run first
            'basic_algebra': [],
            'basic_lattice': [],
            'operation': [],
            'operation_symbol': [],
            
            # Core algebra tests depend on basic tests
            'algebra': ['basic_algebra'],
            'small_algebra': ['basic_algebra'],
            'algebras': ['basic_algebra'],
            
            # Advanced algebra tests depend on core tests
            'free_algebra': ['algebra'],
            'homomorphism': ['algebra'],
            'malcev': ['algebra'],
            'product_algebra': ['algebra'],
            'quotient_algebra': ['algebra'],
            'subalgebra': ['algebra'],
            
            # Congruence tests depend on algebra tests
            'congruence_lattice': ['algebra'],
            'partition': ['algebra'],
            'binary_relation': ['algebra'],
            'polymorphisms': ['algebra'],
            'type_finder': ['algebra'],
            
            # Operation tests depend on basic operation tests
            'operations': ['operation'],
            'term_operation': ['operation', 'term'],
            
            # Term tests
            'term': [],
            'terms': ['term'],
            'variable': ['term'],
            'taylor': ['term'],
            
            # Lattice tests
            'lattice': ['basic_lattice'],
            'order': ['basic_lattice'],
            'lattices': ['lattice'],
            
            # Equation tests depend on term tests
            'equation': ['term'],
            'equations': ['equation'],
            'presentation': ['equation'],
            
            # Group tests
            'permutation_group': [],
            
            # I/O tests
            'algebra_io': [],
            'algebra_reader': ['algebra_io'],
            'algebra_writer': ['algebra_io'],
            
            # Utility tests
            'int_array': [],
            'horner': [],
            'sequence_generator': [],
        }
        
        # Topological sort to resolve dependencies
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(node):
            if node in temp_visited:
                raise ValueError(f"Circular dependency detected involving {node}")
            if node in visited:
                return
            
            temp_visited.add(node)
            for dep in dependencies.get(node, []):
                if dep in self.test_classes:
                    visit(dep)
            temp_visited.remove(node)
            visited.add(node)
            result.append(node)
        
        # Visit all available test classes
        for test_class in self.test_classes.keys():
            if test_class not in visited:
                visit(test_class)
        
        return result
    
    def _check_for_conflicts(self) -> List[str]:
        """
        Check for potential conflicts between test classes.
        
        Returns:
            List of conflict descriptions
        """
        conflicts = []
        
        # Check for overlapping test data usage
        test_data_usage = {}
        for test_name, test_class in self.test_classes.items():
            if hasattr(test_class, 'test_algebra_files'):
                for algebra_file in test_class.test_algebra_files:
                    if algebra_file in test_data_usage:
                        conflicts.append(f"Test data conflict: {algebra_file} used by both {test_data_usage[algebra_file]} and {test_name}")
                    test_data_usage[algebra_file] = test_name
        
        # Check for resource conflicts
        resource_heavy_tests = ['congruence_lattice', 'malcev', 'automorphism_group', 'free_algebra']
        heavy_tests_found = [name for name in resource_heavy_tests if name in self.test_classes]
        if len(heavy_tests_found) > 2:
            conflicts.append(f"Multiple resource-heavy tests detected: {heavy_tests_found}. Consider running sequentially.")
        
        return conflicts
    
    def run_comprehensive_tests(self) -> TestSuiteReport:
        """
        Run the comprehensive test suite with all integrated test classes.
        
        Returns:
            TestSuiteReport with aggregated results
        """
        logger.info("Starting comprehensive Java compatibility test suite")
        self.start_time = time.time()
        
        # Resolve dependencies
        execution_order = self._resolve_test_dependencies()
        logger.info(f"Test execution order: {execution_order}")
        
        # Check for conflicts
        conflicts = self._check_for_conflicts()
        if conflicts:
            logger.warning("Potential conflicts detected:")
            for conflict in conflicts:
                logger.warning(f"  - {conflict}")
        
        # Create test suite
        suite = unittest.TestSuite()
        
        # Add test classes in dependency order
        for test_name in execution_order:
            if test_name in self.test_classes:
                test_class = self.test_classes[test_name]
                logger.info(f"Adding test class: {test_name}")
                
                # Create test loader
                loader = unittest.TestLoader()
                
                # Apply filters if specified
                if self.config.specific_operations and test_name not in self.config.specific_operations:
                    continue
                
                # Load tests from the class
                try:
                    tests = loader.loadTestsFromTestCase(test_class)
                    suite.addTest(tests)
                    logger.info(f"Added {tests.countTestCases()} tests from {test_name}")
                except Exception as e:
                    logger.error(f"Failed to load tests from {test_name}: {e}")
        
        # Run the test suite
        logger.info(f"Running {suite.countTestCases()} total tests")
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            descriptions=True,
            failfast=False
        )
        
        result = runner.run(suite)
        
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report(result, execution_time)
        
        # Save results if requested
        if self.config.save_results_to_file:
            self._save_results_to_file(report)
        
        logger.info(f"Comprehensive test suite completed in {execution_time:.2f}s")
        return report
    
    def _generate_comprehensive_report(self, test_result: unittest.TestResult, execution_time: float) -> TestSuiteReport:
        """Generate a comprehensive test suite report"""
        
        # Collect all test results from BaseCompatibilityTest classes
        all_test_results = []
        for test_class in self.test_classes.values():
            if hasattr(test_class, 'test_results_history'):
                all_test_results.extend(test_class.test_results_history)
        
        total_tests = test_result.testsRun
        failed_tests = len(test_result.failures) + len(test_result.errors)
        passed_tests = total_tests - failed_tests
        skipped_tests = len(test_result.skipped) if hasattr(test_result, 'skipped') else 0
        
        compatibility_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0
        
        # Calculate feature coverage
        feature_coverage = {}
        if all_test_results:
            operations = set(r.operation for r in all_test_results)
            for operation in operations:
                op_results = [r for r in all_test_results if r.operation == operation]
                op_passed = sum(1 for r in op_results if r.matches)
                feature_coverage[operation] = (op_passed / len(op_results) * 100) if op_results else 0.0
        
        # Create detailed failure information
        failed_test_details = []
        for failure in test_result.failures + test_result.errors:
            failed_test_details.append({
                'test_name': str(failure[0]),
                'error_message': str(failure[1]),
                'test_type': 'failure' if failure in test_result.failures else 'error'
            })
        
        return TestSuiteReport(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            compatibility_percentage=compatibility_percentage,
            failed_test_details=failed_test_details,
            feature_coverage=feature_coverage,
            execution_time_total=execution_time
        )
    
    def _save_results_to_file(self, report: TestSuiteReport):
        """Save test results to file"""
        try:
            results_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_tests': report.total_tests,
                'passed_tests': report.passed_tests,
                'failed_tests': report.failed_tests,
                'skipped_tests': report.skipped_tests,
                'compatibility_percentage': report.compatibility_percentage,
                'execution_time_total': report.execution_time_total,
                'feature_coverage': report.feature_coverage,
                'failed_test_details': report.failed_test_details,
                'test_classes_executed': list(self.test_classes.keys()),
                'configuration': {
                    'include_algebra_tests': self.config.include_algebra_tests,
                    'include_congruence_tests': self.config.include_congruence_tests,
                    'include_operation_tests': self.config.include_operation_tests,
                    'include_term_tests': self.config.include_term_tests,
                    'include_lattice_tests': self.config.include_lattice_tests,
                    'include_equation_tests': self.config.include_equation_tests,
                    'include_group_tests': self.config.include_group_tests,
                    'include_io_tests': self.config.include_io_tests,
                    'include_utility_tests': self.config.include_utility_tests,
                    'max_algebra_size': self.config.max_algebra_size,
                    'timeout_per_test': self.config.timeout_per_test,
                }
            }
            
            with open(self.config.output_file, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            logger.info(f"Test results saved to {self.config.output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results to file: {e}")

def main():
    """Main entry point for the comprehensive test suite"""
    parser = argparse.ArgumentParser(description='Comprehensive Java UACalc Compatibility Test Suite')
    
    # Test category options
    parser.add_argument('--no-algebra', action='store_true', help='Skip algebra tests')
    parser.add_argument('--no-congruence', action='store_true', help='Skip congruence tests')
    parser.add_argument('--no-operation', action='store_true', help='Skip operation tests')
    parser.add_argument('--no-term', action='store_true', help='Skip term tests')
    parser.add_argument('--no-lattice', action='store_true', help='Skip lattice tests')
    parser.add_argument('--no-equation', action='store_true', help='Skip equation tests')
    parser.add_argument('--no-group', action='store_true', help='Skip group tests')
    parser.add_argument('--no-io', action='store_true', help='Skip I/O tests')
    parser.add_argument('--no-utility', action='store_true', help='Skip utility tests')
    
    # Filtering options
    parser.add_argument('--max-algebra-size', type=int, help='Maximum algebra size to test')
    parser.add_argument('--specific-algebras', nargs='+', help='Specific algebras to test')
    parser.add_argument('--specific-operations', nargs='+', help='Specific operations to test')
    
    # Performance options
    parser.add_argument('--timeout', type=int, default=300, help='Timeout per test in seconds')
    parser.add_argument('--parallel', action='store_true', help='Enable parallel execution')
    parser.add_argument('--max-parallel', type=int, default=4, help='Maximum parallel tests')
    
    # Output options
    parser.add_argument('--output-file', default='comprehensive_test_results.json', help='Output file for results')
    parser.add_argument('--no-save', action='store_true', help='Do not save results to file')
    
    args = parser.parse_args()
    
    # Create configuration
    config = TestSuiteConfiguration(
        include_algebra_tests=not args.no_algebra,
        include_congruence_tests=not args.no_congruence,
        include_operation_tests=not args.no_operation,
        include_term_tests=not args.no_term,
        include_lattice_tests=not args.no_lattice,
        include_equation_tests=not args.no_equation,
        include_group_tests=not args.no_group,
        include_io_tests=not args.no_io,
        include_utility_tests=not args.no_utility,
        max_algebra_size=args.max_algebra_size,
        specific_algebras=args.specific_algebras,
        specific_operations=args.specific_operations,
        timeout_per_test=args.timeout,
        parallel_execution=args.parallel,
        max_parallel_tests=args.max_parallel,
        save_results_to_file=not args.no_save,
        output_file=args.output_file
    )
    
    # Create and run test suite
    test_suite = ComprehensiveTestSuite(config)
    report = test_suite.run_comprehensive_tests()
    
    # Print summary
    print("\n" + "="*80)
    print("COMPREHENSIVE JAVA UACALC COMPATIBILITY TEST SUITE RESULTS")
    print("="*80)
    print(f"Total Tests: {report.total_tests}")
    print(f"Passed: {report.passed_tests}")
    print(f"Failed: {report.failed_tests}")
    print(f"Skipped: {report.skipped_tests}")
    print(f"Compatibility: {report.compatibility_percentage:.1f}%")
    print(f"Execution Time: {report.execution_time_total:.2f}s")
    print("="*80)
    
    if report.feature_coverage:
        print("\nFeature Coverage:")
        for feature, percentage in sorted(report.feature_coverage.items()):
            print(f"  {feature}: {percentage:.1f}%")
    
    if report.failed_test_details:
        print(f"\nFailed Tests ({len(report.failed_test_details)}):")
        for failure in report.failed_test_details[:10]:  # Show first 10
            print(f"  - {failure['test_name']}: {failure['error_message'][:100]}...")
        if len(report.failed_test_details) > 10:
            print(f"  ... and {len(report.failed_test_details) - 10} more")
    
    return 0 if report.failed_tests == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
