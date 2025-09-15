#!/usr/bin/env python3
"""
Comprehensive Test Runner

This module provides a unified test runner that integrates all components of the
base test infrastructure, including the BaseCompatibilityTest class, result
comparison framework, and test data management.
"""

import unittest
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Import our infrastructure components
from tests.python.base_compatibility_test import BaseCompatibilityTest, CompatibilityTestResult, TestSuiteReport
from tests.python.result_comparison import ResultComparator, ComparisonType, StructuredErrorReporter
from tests.python.test_data_manager import TestDataManager, TestCaseGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_results.log')
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveTestRunner:
    """
    Unified test runner that demonstrates the complete base test infrastructure.
    """
    
    def __init__(self):
        self.data_manager = TestDataManager()
        self.test_case_generator = TestCaseGenerator(self.data_manager)
        self.result_comparator = ResultComparator()
        self.error_reporter = StructuredErrorReporter()
        self.start_time = None
        
    def run_infrastructure_demo(self) -> Dict[str, Any]:
        """
        Run a comprehensive demonstration of the test infrastructure.
        
        Returns:
            Dictionary containing demo results and statistics
        """
        logger.info("Starting comprehensive test infrastructure demonstration")
        self.start_time = time.time()
        
        demo_results = {
            'java_environment': self._test_java_environment(),
            'test_data_management': self._test_data_management(),
            'result_comparison': self._test_result_comparison(),
            'base_test_functionality': self._test_base_functionality(),
            'integration_test': self._run_integration_test()
        }
        
        total_time = time.time() - self.start_time
        demo_results['execution_time'] = total_time
        demo_results['summary'] = self._generate_demo_summary(demo_results)
        
        logger.info(f"Infrastructure demonstration completed in {total_time:.2f}s")
        return demo_results
    
    def _test_java_environment(self) -> Dict[str, Any]:
        """Test Java environment setup and validation"""
        logger.info("Testing Java environment setup...")
        
        results = {
            'java_available': False,
            'compilation_successful': False,
            'basic_operation_works': False,
            'error_details': []
        }
        
        try:
            # Test Java availability using BaseCompatibilityTest
            class JavaEnvTest(BaseCompatibilityTest):
                def test_java_setup(self):
                    return self.java_available
            
            # Create test instance and check setup
            test_instance = JavaEnvTest()
            test_instance.setUpClass()
            
            results['java_available'] = test_instance.java_available
            
            if test_instance.java_available:
                # Test basic operation
                java_result = test_instance._run_java_operation("properties", "resources/algebras/ba2.ua")
                if java_result and java_result.get('name'):
                    results['basic_operation_works'] = True
                    results['compilation_successful'] = True
                    logger.info("✓ Java environment fully functional")
                else:
                    results['error_details'].append("Basic Java operation failed")
                    logger.warning("✗ Java environment setup incomplete")
            else:
                results['error_details'].append("Java environment not available")
                logger.warning("✗ Java environment not available")
                
        except Exception as e:
            results['error_details'].append(f"Java environment test failed: {e}")
            logger.error(f"Java environment test failed: {e}")
        
        return results
    
    def _test_data_management(self) -> Dict[str, Any]:
        """Test data management capabilities"""
        logger.info("Testing data management system...")
        
        results = {
            'algebras_discovered': 0,
            'complexity_analysis': {},
            'test_cases_generated': 0,
            'caching_works': False,
            'error_details': []
        }
        
        try:
            # Test algebra discovery
            algebras = self.data_manager.discover_algebras()
            results['algebras_discovered'] = len(algebras)
            
            if algebras:
                # Test complexity analysis
                summary = self.data_manager.get_algebra_summary()
                if summary:
                    results['complexity_analysis'] = summary
                
                # Test test case generation
                test_algebra = algebras[0]
                test_cases = self.test_case_generator.generate_element_pairs(4)
                results['test_cases_generated'] = len(test_cases)
                
                # Test caching (load same algebra twice)
                start_time = time.time()
                algebra1 = self.data_manager.load_algebra_with_cache(str(test_algebra))
                first_load_time = time.time() - start_time
                
                start_time = time.time()
                algebra2 = self.data_manager.load_algebra_with_cache(str(test_algebra))
                second_load_time = time.time() - start_time
                
                # Second load should be faster (cached)
                results['caching_works'] = second_load_time < first_load_time
                
                logger.info(f"✓ Data management: {len(algebras)} algebras, {len(test_cases)} test cases")
            else:
                results['error_details'].append("No algebras discovered")
                logger.warning("✗ No test algebras found")
                
        except Exception as e:
            results['error_details'].append(f"Data management test failed: {e}")
            logger.error(f"Data management test failed: {e}")
        
        return results
    
    def _test_result_comparison(self) -> Dict[str, Any]:
        """Test result comparison framework"""
        logger.info("Testing result comparison framework...")
        
        results = {
            'exact_comparison': False,
            'numeric_tolerance': False,
            'set_comparison': False,
            'partition_comparison': False,
            'complex_structure': False,
            'error_details': []
        }
        
        try:
            # Test exact comparison
            diff_report = self.result_comparator.compare("test", "test", ComparisonType.EXACT)
            results['exact_comparison'] = diff_report.overall_match
            
            # Test numeric tolerance
            diff_report = self.result_comparator.compare(1.0000001, 1.0, ComparisonType.NUMERIC_TOLERANCE, tolerance=1e-6)
            results['numeric_tolerance'] = diff_report.overall_match
            
            # Test set comparison
            diff_report = self.result_comparator.compare([1, 2, 3], [3, 1, 2], ComparisonType.SET_COMPARISON)
            results['set_comparison'] = diff_report.overall_match
            
            # Test partition comparison
            partition1 = [[0, 1], [2, 3]]
            partition2 = [[2, 3], [0, 1]]  # Different order, same partition
            diff_report = self.result_comparator.compare(partition1, partition2, ComparisonType.PARTITION_COMPARISON)
            results['partition_comparison'] = diff_report.overall_match
            
            # Test complex structure comparison
            complex1 = {"size": 4, "operations": [{"name": "f", "arity": 2}]}
            complex2 = {"size": 4, "operations": [{"name": "f", "arity": 2}]}
            diff_report = self.result_comparator.compare(complex1, complex2)
            results['complex_structure'] = diff_report.overall_match
            
            logger.info("✓ Result comparison framework functional")
            
        except Exception as e:
            results['error_details'].append(f"Result comparison test failed: {e}")
            logger.error(f"Result comparison test failed: {e}")
        
        return results
    
    def _test_base_functionality(self) -> Dict[str, Any]:
        """Test BaseCompatibilityTest functionality"""
        logger.info("Testing BaseCompatibilityTest functionality...")
        
        results = {
            'setup_successful': False,
            'algebra_loading': False,
            'java_operation_execution': False,
            'result_comparison_integration': False,
            'error_details': []
        }
        
        try:
            # Create a test class that inherits from BaseCompatibilityTest
            class FunctionalityTest(BaseCompatibilityTest):
                def test_basic_functionality(self):
                    # Test algebra loading
                    if self.algebra_files:
                        algebra = self._load_test_algebra(self.algebra_files[0])
                        self.assertIsNotNone(algebra)
                        return True
                    return False
            
            # Run the test
            test_instance = FunctionalityTest()
            test_instance.setUpClass()
            test_instance.setUp()
            
            results['setup_successful'] = True
            
            # Test algebra loading
            if test_instance.algebra_files:
                try:
                    algebra = test_instance._load_test_algebra(test_instance.algebra_files[0])
                    results['algebra_loading'] = algebra is not None
                except Exception as e:
                    results['error_details'].append(f"Algebra loading failed: {e}")
            
            # Test Java operation execution
            if test_instance.java_available and test_instance.algebra_files:
                try:
                    java_result = test_instance._run_java_operation(
                        "properties", str(test_instance.algebra_files[0])
                    )
                    results['java_operation_execution'] = java_result is not None
                except Exception as e:
                    results['error_details'].append(f"Java operation failed: {e}")
            
            # Test result comparison integration
            try:
                test_result = test_instance._compare_results(
                    {"test": "value"}, {"test": "value", "success": True}, 
                    "test_operation", "test_context"
                )
                results['result_comparison_integration'] = isinstance(test_result, CompatibilityTestResult)
            except Exception as e:
                results['error_details'].append(f"Result comparison integration failed: {e}")
            
            test_instance.tearDown()
            logger.info("✓ BaseCompatibilityTest functionality verified")
            
        except Exception as e:
            results['error_details'].append(f"Base functionality test failed: {e}")
            logger.error(f"Base functionality test failed: {e}")
        
        return results
    
    def _run_integration_test(self) -> Dict[str, Any]:
        """Run a complete integration test"""
        logger.info("Running integration test...")
        
        results = {
            'test_executed': False,
            'results_generated': False,
            'report_created': False,
            'error_details': []
        }
        
        try:
            # Create a comprehensive integration test
            class IntegrationTest(BaseCompatibilityTest):
                def test_complete_workflow(self):
                    """Test the complete workflow from algebra loading to result comparison"""
                    if not self.algebra_files:
                        self.skipTest("No algebra files available")
                    
                    # Load algebra
                    algebra = self._load_test_algebra(self.algebra_files[0])
                    
                    # Simulate Rust result
                    rust_result = {
                        "name": algebra.name if hasattr(algebra, 'name') else "test_algebra",
                        "cardinality": algebra.cardinality if hasattr(algebra, 'cardinality') else 2,
                        "operation_count": len(algebra.operations()) if hasattr(algebra, 'operations') else 1
                    }
                    
                    # Get Java result (if available)
                    if self.java_available:
                        java_result = self._run_java_operation("properties", str(self.algebra_files[0]))
                        
                        # Compare results
                        comparison_result = self._compare_results(
                            rust_result, java_result, "properties", self.algebra_files[0].name
                        )
                        
                        return comparison_result
                    else:
                        # Create mock comparison for testing
                        return CompatibilityTestResult(
                            test_name="integration_test",
                            algebra_name="test_algebra",
                            operation="properties",
                            rust_result=rust_result,
                            java_result=None,
                            matches=False,
                            error_message="Java not available"
                        )
            
            # Run the integration test
            test_instance = IntegrationTest()
            test_instance.setUpClass()
            test_instance.setUp()
            
            comparison_result = test_instance.test_complete_workflow()
            results['test_executed'] = True
            results['results_generated'] = isinstance(comparison_result, CompatibilityTestResult)
            
            # Generate test suite report
            test_report = test_instance.generate_test_suite_report()
            results['report_created'] = isinstance(test_report, TestSuiteReport)
            
            test_instance.tearDown()
            logger.info("✓ Integration test completed successfully")
            
        except Exception as e:
            results['error_details'].append(f"Integration test failed: {e}")
            logger.error(f"Integration test failed: {e}")
        
        return results
    
    def _generate_demo_summary(self, demo_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the demonstration results"""
        summary = {
            'overall_success': True,
            'components_tested': len(demo_results) - 2,  # Exclude execution_time and summary
            'successful_components': 0,
            'failed_components': [],
            'recommendations': []
        }
        
        # Analyze each component
        for component, results in demo_results.items():
            if component in ['execution_time', 'summary']:
                continue
                
            if isinstance(results, dict):
                # Check if component was successful
                component_success = self._evaluate_component_success(component, results)
                if component_success:
                    summary['successful_components'] += 1
                else:
                    summary['failed_components'].append(component)
                    summary['overall_success'] = False
        
        # Generate recommendations
        if not summary['overall_success']:
            summary['recommendations'] = self._generate_recommendations(demo_results)
        
        return summary
    
    def _evaluate_component_success(self, component: str, results: Dict[str, Any]) -> bool:
        """Evaluate if a component test was successful"""
        if component == 'java_environment':
            return results.get('java_available', False) and results.get('basic_operation_works', False)
        elif component == 'test_data_management':
            return results.get('algebras_discovered', 0) > 0
        elif component == 'result_comparison':
            return (results.get('exact_comparison', False) and 
                   results.get('numeric_tolerance', False) and
                   results.get('set_comparison', False))
        elif component == 'base_test_functionality':
            return results.get('setup_successful', False) and results.get('algebra_loading', False)
        elif component == 'integration_test':
            return results.get('test_executed', False) and results.get('results_generated', False)
        
        return False
    
    def _generate_recommendations(self, demo_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on failed components"""
        recommendations = []
        
        java_env = demo_results.get('java_environment', {})
        if not java_env.get('java_available', False):
            recommendations.append("Install Java and ensure it's in PATH")
            recommendations.append("Place uacalc.jar in jars/ directory")
            recommendations.append("Ensure JavaWrapper.java is in scripts/ directory")
        
        data_mgmt = demo_results.get('test_data_management', {})
        if data_mgmt.get('algebras_discovered', 0) == 0:
            recommendations.append("Add .ua algebra files to resources/algebras/ directory")
        
        return recommendations

def main():
    """Main entry point for the comprehensive test runner"""
    print("Comprehensive Java UACalc Compatibility Test Infrastructure")
    print("=" * 60)
    
    runner = ComprehensiveTestRunner()
    demo_results = runner.run_infrastructure_demo()
    
    # Print results
    print("\nDemo Results:")
    print("-" * 40)
    
    for component, results in demo_results.items():
        if component in ['execution_time', 'summary']:
            continue
            
        print(f"\n{component.replace('_', ' ').title()}:")
        if isinstance(results, dict):
            for key, value in results.items():
                if key != 'error_details':
                    print(f"  {key}: {value}")
            if results.get('error_details'):
                print(f"  Errors: {len(results['error_details'])}")
                for error in results['error_details'][:2]:  # Show first 2 errors
                    print(f"    - {error}")
    
    # Print summary
    summary = demo_results.get('summary', {})
    print(f"\nSummary:")
    print(f"  Overall Success: {'✓' if summary.get('overall_success') else '✗'}")
    print(f"  Components Tested: {summary.get('components_tested', 0)}")
    print(f"  Successful: {summary.get('successful_components', 0)}")
    print(f"  Failed: {len(summary.get('failed_components', []))}")
    print(f"  Execution Time: {demo_results.get('execution_time', 0):.2f}s")
    
    if summary.get('recommendations'):
        print(f"\nRecommendations:")
        for rec in summary['recommendations']:
            print(f"  - {rec}")
    
    # Save detailed results
    results_file = Path("test_infrastructure_demo_results.json")
    with open(results_file, 'w') as f:
        json.dump(demo_results, f, indent=2, default=str)
    print(f"\nDetailed results saved to: {results_file}")
    
    return 0 if summary.get('overall_success') else 1

if __name__ == "__main__":
    sys.exit(main())