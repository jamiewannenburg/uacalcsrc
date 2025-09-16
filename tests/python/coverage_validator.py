#!/usr/bin/env python3
"""
Java UACalc Coverage Validation Tool

This module validates comprehensive coverage of Java UACalc functionality by
checking that all major Java UACalc classes have corresponding compatibility tests.
It addresses Task 13.2 by verifying test coverage completeness.

Features:
- Maps Java UACalc packages to test classes
- Identifies gaps in test coverage
- Validates that all critical functionality is covered
- Generates coverage reports and recommendations
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

@dataclass
class JavaClassInfo:
    """Information about a Java class"""
    package: str
    class_name: str
    file_path: Path
    is_interface: bool = False
    is_abstract: bool = False
    is_public: bool = True
    methods: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class TestClassInfo:
    """Information about a test class"""
    test_name: str
    test_file: Path
    target_java_package: str
    target_java_classes: List[str] = field(default_factory=list)
    test_methods: List[str] = field(default_factory=list)
    coverage_percentage: float = 0.0

@dataclass
class CoverageReport:
    """Comprehensive coverage report"""
    total_java_classes: int
    covered_java_classes: int
    total_test_classes: int
    coverage_percentage: float
    package_coverage: Dict[str, float]
    missing_tests: List[str]
    redundant_tests: List[str]
    recommendations: List[str]
    detailed_mapping: Dict[str, Dict[str, Any]]

class JavaUACalcCoverageValidator:
    """
    Validates comprehensive coverage of Java UACalc functionality.
    
    This class addresses Task 13.2 by:
    - Verifying all major Java UACalc classes have corresponding tests
    - Checking that all critical functionality is covered
    - Identifying and addressing gaps in test coverage
    """
    
    def __init__(self):
        self.java_classes = {}
        self.test_classes = {}
        self.package_mapping = self._initialize_package_mapping()
        
    def _initialize_package_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the mapping between Java packages and expected test coverage"""
        return {
            'org.uacalc.alg': {
                'description': 'Core algebra classes and interfaces',
                'critical_classes': [
                    'Algebra', 'BasicAlgebra', 'SmallAlgebra', 'Algebras',
                    'FreeAlgebra', 'Homomorphism', 'Malcev', 'ProductAlgebra',
                    'QuotientAlgebra', 'Subalgebra'
                ],
                'test_class': 'algebra_compatibility',
                'priority': 'high'
            },
            'org.uacalc.alg.conlat': {
                'description': 'Congruence lattice and related structures',
                'critical_classes': [
                    'CongruenceLattice', 'Partition', 'BinaryRelation',
                    'Polymorphisms', 'TypeFinder'
                ],
                'test_class': 'congruence_compatibility',
                'priority': 'high'
            },
            'org.uacalc.alg.op': {
                'description': 'Operation interfaces and implementations',
                'critical_classes': [
                    'Operation', 'Operations', 'OperationSymbol', 'TermOperation'
                ],
                'test_class': 'operation_compatibility',
                'priority': 'high'
            },
            'org.uacalc.terms': {
                'description': 'Term parsing and evaluation',
                'critical_classes': [
                    'Term', 'Terms', 'Variable', 'Taylor'
                ],
                'test_class': 'term_compatibility',
                'priority': 'high'
            },
            'org.uacalc.lat': {
                'description': 'Lattice structures and operations',
                'critical_classes': [
                    'Lattice', 'BasicLattice', 'Order', 'Lattices'
                ],
                'test_class': 'lattice_compatibility',
                'priority': 'medium'
            },
            'org.uacalc.eq': {
                'description': 'Equation representation and operations',
                'critical_classes': [
                    'Equation', 'Equations', 'Presentation'
                ],
                'test_class': 'equation_compatibility',
                'priority': 'medium'
            },
            'org.uacalc.group': {
                'description': 'Group theory operations',
                'critical_classes': [
                    'PermutationGroup'
                ],
                'test_class': 'group_compatibility',
                'priority': 'medium'
            },
            'org.uacalc.io': {
                'description': 'Input/output operations',
                'critical_classes': [
                    'AlgebraIO', 'AlgebraReader', 'AlgebraWriter'
                ],
                'test_class': 'io_compatibility',
                'priority': 'high'
            },
            'org.uacalc.util': {
                'description': 'Utility classes and helper functions',
                'critical_classes': [
                    'IntArray', 'Horner', 'SequenceGenerator'
                ],
                'test_class': 'utility_compatibility',
                'priority': 'low'
            }
        }
    
    def discover_java_classes(self) -> Dict[str, JavaClassInfo]:
        """Discover all Java classes in the UACalc source code"""
        java_classes = {}
        java_source_dir = project_root / "org"
        
        if not java_source_dir.exists():
            logger.warning("Java source directory not found, using package mapping only")
            return java_classes
        
        for java_file in java_source_dir.rglob("*.java"):
            try:
                class_info = self._parse_java_file(java_file)
                if class_info:
                    key = f"{class_info.package}.{class_info.class_name}"
                    java_classes[key] = class_info
            except Exception as e:
                logger.warning(f"Failed to parse Java file {java_file}: {e}")
        
        logger.info(f"Discovered {len(java_classes)} Java classes")
        return java_classes
    
    def _parse_java_file(self, file_path: Path) -> Optional[JavaClassInfo]:
        """Parse a Java file to extract class information"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract package name
            package_match = None
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('package '):
                    package_match = line.replace('package ', '').replace(';', '').strip()
                    break
            
            if not package_match:
                return None
            
            # Extract class name and modifiers
            class_name = None
            is_interface = False
            is_abstract = False
            is_public = False
            
            for line in content.split('\n'):
                line = line.strip()
                if 'class ' in line or 'interface ' in line:
                    if 'interface ' in line:
                        is_interface = True
                        parts = line.split('interface ')
                    else:
                        parts = line.split('class ')
                    
                    if len(parts) > 1:
                        class_declaration = parts[1].split()[0]
                        class_name = class_declaration.split('<')[0].split('{')[0]
                    
                    # Check modifiers
                    if 'public ' in line:
                        is_public = True
                    if 'abstract ' in line:
                        is_abstract = True
                    break
            
            if not class_name:
                return None
            
            # Extract method names (simplified)
            methods = []
            in_class = False
            brace_count = 0
            
            for line in content.split('\n'):
                line = line.strip()
                if '{' in line and (f'class {class_name}' in line or f'interface {class_name}' in line):
                    in_class = True
                    brace_count = line.count('{') - line.count('}')
                
                if in_class:
                    brace_count += line.count('{') - line.count('}')
                    
                    # Look for method declarations
                    if ('public ' in line or 'private ' in line or 'protected ' in line) and '(' in line and ')' in line:
                        if not line.startswith('//') and not line.startswith('*'):
                            # Extract method name
                            method_part = line.split('(')[0].split()[-1]
                            if method_part and method_part not in ['public', 'private', 'protected', 'static', 'final']:
                                methods.append(method_part)
                    
                    if brace_count <= 0:
                        break
            
            return JavaClassInfo(
                package=package_match,
                class_name=class_name,
                file_path=file_path,
                is_interface=is_interface,
                is_abstract=is_abstract,
                is_public=is_public,
                methods=methods
            )
            
        except Exception as e:
            logger.error(f"Error parsing Java file {file_path}: {e}")
            return None
    
    def discover_test_classes(self) -> Dict[str, TestClassInfo]:
        """Discover all compatibility test classes"""
        test_classes = {}
        test_dir = project_root / "tests" / "python"
        
        if not test_dir.exists():
            logger.warning("Test directory not found")
            return test_classes
        
        for test_file in test_dir.glob("test_*_compatibility.py"):
            try:
                test_info = self._parse_test_file(test_file)
                if test_info:
                    test_classes[test_info.test_name] = test_info
            except Exception as e:
                logger.warning(f"Failed to parse test file {test_file}: {e}")
        
        logger.info(f"Discovered {len(test_classes)} test classes")
        return test_classes
    
    def _parse_test_file(self, file_path: Path) -> Optional[TestClassInfo]:
        """Parse a test file to extract test class information"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract test class name
            test_class_name = None
            for line in content.split('\n'):
                line = line.strip()
                if 'class ' in line and 'CompatibilityTest' in line:
                    parts = line.split('class ')
                    if len(parts) > 1:
                        test_class_name = parts[1].split('(')[0].split(':')[0].strip()
                    break
            
            if not test_class_name:
                return None
            
            # Extract test methods
            test_methods = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('def test_') and '(' in line:
                    method_name = line.split('def ')[1].split('(')[0]
                    test_methods.append(method_name)
            
            # Determine target Java package based on file name
            file_name = file_path.stem
            target_package = self._infer_target_package(file_name)
            
            return TestClassInfo(
                test_name=test_class_name,
                test_file=file_path,
                target_java_package=target_package,
                test_methods=test_methods
            )
            
        except Exception as e:
            logger.error(f"Error parsing test file {file_path}: {e}")
            return None
    
    def _infer_target_package(self, test_file_name: str) -> str:
        """Infer the target Java package from test file name"""
        mapping = {
            'test_algebra_compatibility': 'org.uacalc.alg',
            'test_basic_algebra_compatibility': 'org.uacalc.alg',
            'test_small_algebra_compatibility': 'org.uacalc.alg',
            'test_algebras_compatibility': 'org.uacalc.alg',
            'test_free_algebra_compatibility': 'org.uacalc.alg',
            'test_homomorphism_compatibility': 'org.uacalc.alg',
            'test_malcev_compatibility': 'org.uacalc.alg',
            'test_product_algebra_compatibility': 'org.uacalc.alg',
            'test_quotient_algebra_compatibility': 'org.uacalc.alg',
            'test_subalgebra_compatibility': 'org.uacalc.alg',
            'test_congruence_lattice_compatibility': 'org.uacalc.alg.conlat',
            'test_partition_compatibility': 'org.uacalc.alg.conlat',
            'test_binary_relation_compatibility': 'org.uacalc.alg.conlat',
            'test_polymorphisms_compatibility': 'org.uacalc.alg.conlat',
            'test_type_finder_compatibility': 'org.uacalc.alg.conlat',
            'test_operation_compatibility': 'org.uacalc.alg.op',
            'test_operations_compatibility': 'org.uacalc.alg.op',
            'test_operation_symbol_compatibility': 'org.uacalc.alg.op',
            'test_term_operation_compatibility': 'org.uacalc.alg.op',
            'test_term_compatibility': 'org.uacalc.terms',
            'test_terms_compatibility': 'org.uacalc.terms',
            'test_variable_compatibility': 'org.uacalc.terms',
            'test_taylor_compatibility': 'org.uacalc.terms',
            'test_lattice_compatibility': 'org.uacalc.lat',
            'test_basic_lattice_compatibility': 'org.uacalc.lat',
            'test_order_compatibility': 'org.uacalc.lat',
            'test_lattices_compatibility': 'org.uacalc.lat',
            'test_equation_compatibility': 'org.uacalc.eq',
            'test_equations_compatibility': 'org.uacalc.eq',
            'test_presentation_compatibility': 'org.uacalc.eq',
            'test_permutation_group_compatibility': 'org.uacalc.group',
            'test_algebra_io_compatibility': 'org.uacalc.io',
            'test_algebra_reader_compatibility': 'org.uacalc.io',
            'test_algebra_writer_compatibility': 'org.uacalc.io',
            'test_int_array_compatibility': 'org.uacalc.util',
            'test_horner_compatibility': 'org.uacalc.util',
            'test_sequence_generator_compatibility': 'org.uacalc.util',
        }
        
        return mapping.get(test_file_name, 'unknown')
    
    def validate_coverage(self) -> CoverageReport:
        """
        Validate comprehensive coverage of Java UACalc functionality.
        
        Returns:
            CoverageReport with detailed coverage analysis
        """
        logger.info("Starting coverage validation")
        
        # Discover Java classes and test classes
        self.java_classes = self.discover_java_classes()
        self.test_classes = self.discover_test_classes()
        
        # Calculate coverage metrics
        total_java_classes = len(self.java_classes)
        covered_java_classes = 0
        package_coverage = {}
        missing_tests = []
        redundant_tests = []
        recommendations = []
        detailed_mapping = {}
        
        # Analyze each package
        for package, package_info in self.package_mapping.items():
            package_java_classes = [cls for cls in self.java_classes.values() if cls.package == package]
            package_test_classes = [test for test in self.test_classes.values() if test.target_java_package == package]
            
            package_total = len(package_java_classes)
            package_covered = len(package_test_classes)
            
            if package_total > 0:
                package_coverage[package] = (package_covered / package_total) * 100
                covered_java_classes += package_covered
            else:
                # Use expected classes from mapping
                expected_classes = package_info.get('critical_classes', [])
                package_coverage[package] = (package_covered / len(expected_classes)) * 100 if expected_classes else 100
                covered_java_classes += package_covered
            
            # Check for missing tests
            if package_info.get('priority') == 'high' and package_coverage[package] < 100:
                missing_tests.append(f"{package}: {package_info['description']}")
            
            # Generate recommendations
            if package_coverage[package] < 80:
                recommendations.append(f"Improve coverage for {package}: {package_info['description']}")
            
            # Create detailed mapping
            detailed_mapping[package] = {
                'description': package_info['description'],
                'priority': package_info.get('priority', 'medium'),
                'java_classes_found': len(package_java_classes),
                'test_classes_found': len(package_test_classes),
                'coverage_percentage': package_coverage[package],
                'java_classes': [cls.class_name for cls in package_java_classes],
                'test_classes': [test.test_name for test in package_test_classes],
                'critical_classes': package_info.get('critical_classes', [])
            }
        
        # Check for redundant tests
        test_packages = set(test.target_java_package for test in self.test_classes.values())
        for test_package in test_packages:
            if test_package not in self.package_mapping:
                redundant_tests.append(f"Test targets unknown package: {test_package}")
        
        # Calculate overall coverage
        if total_java_classes > 0:
            coverage_percentage = (covered_java_classes / total_java_classes) * 100
        else:
            # Fallback calculation based on expected packages
            total_expected = sum(len(info.get('critical_classes', [])) for info in self.package_mapping.values())
            coverage_percentage = (covered_java_classes / total_expected) * 100 if total_expected > 0 else 0
        
        # Generate additional recommendations
        if coverage_percentage < 90:
            recommendations.append("Overall coverage is below 90%. Consider adding more test classes.")
        
        if len(missing_tests) > 0:
            recommendations.append(f"Address {len(missing_tests)} missing test areas for critical functionality.")
        
        return CoverageReport(
            total_java_classes=total_java_classes,
            covered_java_classes=covered_java_classes,
            total_test_classes=len(self.test_classes),
            coverage_percentage=coverage_percentage,
            package_coverage=package_coverage,
            missing_tests=missing_tests,
            redundant_tests=redundant_tests,
            recommendations=recommendations,
            detailed_mapping=detailed_mapping
        )
    
    def generate_coverage_report(self, report: CoverageReport, output_file: str = "coverage_report.json"):
        """Generate a detailed coverage report"""
        try:
            report_data = {
                'summary': {
                    'total_java_classes': report.total_java_classes,
                    'covered_java_classes': report.covered_java_classes,
                    'total_test_classes': report.total_test_classes,
                    'coverage_percentage': report.coverage_percentage,
                    'timestamp': str(Path().cwd())
                },
                'package_coverage': report.package_coverage,
                'missing_tests': report.missing_tests,
                'redundant_tests': report.redundant_tests,
                'recommendations': report.recommendations,
                'detailed_mapping': report.detailed_mapping
            }
            
            with open(output_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"Coverage report saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to generate coverage report: {e}")
    
    def print_coverage_summary(self, report: CoverageReport):
        """Print a human-readable coverage summary"""
        print("\n" + "="*80)
        print("JAVA UACALC COMPATIBILITY TEST COVERAGE VALIDATION")
        print("="*80)
        print(f"Total Java Classes: {report.total_java_classes}")
        print(f"Covered by Tests: {report.covered_java_classes}")
        print(f"Total Test Classes: {report.total_test_classes}")
        print(f"Overall Coverage: {report.coverage_percentage:.1f}%")
        print("="*80)
        
        print("\nPackage Coverage:")
        for package, coverage in sorted(report.package_coverage.items()):
            priority = report.detailed_mapping.get(package, {}).get('priority', 'medium')
            status = "✓" if coverage >= 80 else "⚠" if coverage >= 50 else "✗"
            print(f"  {status} {package}: {coverage:.1f}% ({priority} priority)")
        
        if report.missing_tests:
            print(f"\nMissing Tests ({len(report.missing_tests)}):")
            for missing in report.missing_tests:
                print(f"  - {missing}")
        
        if report.redundant_tests:
            print(f"\nRedundant Tests ({len(report.redundant_tests)}):")
            for redundant in report.redundant_tests:
                print(f"  - {redundant}")
        
        if report.recommendations:
            print(f"\nRecommendations ({len(report.recommendations)}):")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")
        
        print("="*80)

def main():
    """Main entry point for coverage validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Java UACalc test coverage')
    parser.add_argument('--output-file', default='coverage_report.json', help='Output file for coverage report')
    parser.add_argument('--no-save', action='store_true', help='Do not save report to file')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Create validator and run validation
    validator = JavaUACalcCoverageValidator()
    report = validator.validate_coverage()
    
    # Print summary
    validator.print_coverage_summary(report)
    
    # Save report if requested
    if not args.no_save:
        validator.generate_coverage_report(report, args.output_file)
    
    # Return exit code based on coverage
    return 0 if report.coverage_percentage >= 80 else 1

if __name__ == '__main__':
    sys.exit(main())
