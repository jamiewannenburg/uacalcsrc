#!/usr/bin/env python3
"""
Result Comparison Framework

This module provides comprehensive result comparison capabilities for Java UACalc
compatibility testing, including type-aware comparisons, tolerance handling,
and detailed diff reporting.
"""

import json
import math
from typing import Any, Dict, List, Tuple, Optional, Union, Set
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ComparisonType(Enum):
    """Types of comparisons that can be performed"""
    EXACT = "exact"
    NUMERIC_TOLERANCE = "numeric_tolerance"
    SET_COMPARISON = "set_comparison"
    PARTITION_COMPARISON = "partition_comparison"
    LATTICE_COMPARISON = "lattice_comparison"
    OPERATION_TABLE_COMPARISON = "operation_table_comparison"

@dataclass
class ComparisonResult:
    """Result of a detailed comparison operation"""
    matches: bool
    comparison_type: ComparisonType
    details: str
    path: str = ""
    rust_value: Any = None
    java_value: Any = None
    tolerance_used: Optional[float] = None
    
@dataclass
class DiffReport:
    """Detailed difference report between two values"""
    overall_match: bool
    comparison_results: List[ComparisonResult]
    summary: str
    total_comparisons: int
    failed_comparisons: int
    
    def __str__(self) -> str:
        if self.overall_match:
            return f"✓ All {self.total_comparisons} comparisons passed"
        else:
            return f"✗ {self.failed_comparisons}/{self.total_comparisons} comparisons failed: {self.summary}"

class ResultComparator:
    """
    Comprehensive result comparison framework with support for different data types
    and comparison strategies used in algebraic computations.
    """
    
    def __init__(self, default_tolerance: float = 1e-10):
        """
        Initialize the result comparator.
        
        Args:
            default_tolerance: Default tolerance for floating-point comparisons
        """
        self.default_tolerance = default_tolerance
        self.comparison_results = []
        
    def compare(self, rust_result: Any, java_result: Any, 
                comparison_type: Optional[ComparisonType] = None,
                tolerance: Optional[float] = None,
                context: str = "") -> DiffReport:
        """
        Compare two results with detailed reporting.
        
        Args:
            rust_result: Result from Rust implementation
            java_result: Result from Java implementation
            comparison_type: Specific comparison type to use
            tolerance: Tolerance for numeric comparisons
            context: Context information for error reporting
            
        Returns:
            DiffReport with detailed comparison results
        """
        self.comparison_results = []
        tolerance = tolerance or self.default_tolerance
        
        try:
            # Determine comparison type if not specified
            if comparison_type is None:
                comparison_type = self._infer_comparison_type(rust_result, java_result)
            
            # Perform the comparison
            overall_match = self._perform_comparison(
                rust_result, java_result, comparison_type, tolerance, context
            )
            
            # Generate summary
            failed_results = [r for r in self.comparison_results if not r.matches]
            summary = self._generate_summary(failed_results)
            
            return DiffReport(
                overall_match=overall_match,
                comparison_results=self.comparison_results.copy(),
                summary=summary,
                total_comparisons=len(self.comparison_results),
                failed_comparisons=len(failed_results)
            )
            
        except Exception as e:
            logger.error(f"Comparison failed with exception: {e}")
            error_result = ComparisonResult(
                matches=False,
                comparison_type=ComparisonType.EXACT,
                details=f"Comparison exception: {e}",
                path=context,
                rust_value=rust_result,
                java_value=java_result
            )
            return DiffReport(
                overall_match=False,
                comparison_results=[error_result],
                summary=f"Comparison exception: {e}",
                total_comparisons=1,
                failed_comparisons=1
            )
    
    def _infer_comparison_type(self, rust_result: Any, java_result: Any) -> ComparisonType:
        """Infer the appropriate comparison type based on the data"""
        # Check for numeric types
        if isinstance(rust_result, (int, float)) and isinstance(java_result, (int, float)):
            return ComparisonType.NUMERIC_TOLERANCE
        
        # Check for partition-like structures (list of lists)
        if (isinstance(rust_result, list) and rust_result and 
            isinstance(rust_result[0], list) and
            isinstance(java_result, list) and java_result and
            isinstance(java_result[0], list)):
            return ComparisonType.PARTITION_COMPARISON
        
        # Check for set-like structures
        if (isinstance(rust_result, (list, set, tuple)) and 
            isinstance(java_result, (list, set, tuple))):
            return ComparisonType.SET_COMPARISON
        
        # Check for operation table structures (nested lists with numeric values)
        if (isinstance(rust_result, list) and rust_result and
            isinstance(rust_result[0], list) and rust_result[0] and
            isinstance(rust_result[0][0], (int, float)) and
            isinstance(java_result, list) and java_result and
            isinstance(java_result[0], list) and java_result[0] and
            isinstance(java_result[0][0], (int, float))):
            return ComparisonType.OPERATION_TABLE_COMPARISON
        
        # Default to exact comparison
        return ComparisonType.EXACT
    
    def _perform_comparison(self, rust_result: Any, java_result: Any,
                          comparison_type: ComparisonType, tolerance: float,
                          path: str) -> bool:
        """Perform the actual comparison based on the specified type"""
        if comparison_type == ComparisonType.EXACT:
            return self._compare_exact(rust_result, java_result, path)
        elif comparison_type == ComparisonType.NUMERIC_TOLERANCE:
            return self._compare_numeric(rust_result, java_result, tolerance, path)
        elif comparison_type == ComparisonType.SET_COMPARISON:
            return self._compare_sets(rust_result, java_result, path)
        elif comparison_type == ComparisonType.PARTITION_COMPARISON:
            return self._compare_partitions(rust_result, java_result, path)
        elif comparison_type == ComparisonType.LATTICE_COMPARISON:
            return self._compare_lattices(rust_result, java_result, tolerance, path)
        elif comparison_type == ComparisonType.OPERATION_TABLE_COMPARISON:
            return self._compare_operation_tables(rust_result, java_result, path)
        else:
            return self._compare_recursive(rust_result, java_result, tolerance, path)
    
    def _compare_exact(self, rust_val: Any, java_val: Any, path: str) -> bool:
        """Perform exact comparison"""
        matches = rust_val == java_val
        
        result = ComparisonResult(
            matches=matches,
            comparison_type=ComparisonType.EXACT,
            details="Exact match" if matches else f"Values differ: {rust_val} != {java_val}",
            path=path,
            rust_value=rust_val,
            java_value=java_val
        )
        self.comparison_results.append(result)
        return matches
    
    def _compare_numeric(self, rust_val: Any, java_val: Any, tolerance: float, path: str) -> bool:
        """Compare numeric values with tolerance"""
        if not isinstance(rust_val, (int, float)) or not isinstance(java_val, (int, float)):
            return self._compare_exact(rust_val, java_val, path)
        
        diff = abs(rust_val - java_val)
        matches = diff <= tolerance
        
        result = ComparisonResult(
            matches=matches,
            comparison_type=ComparisonType.NUMERIC_TOLERANCE,
            details=f"Numeric comparison (diff: {diff:.2e}, tolerance: {tolerance:.2e})" if matches 
                   else f"Numeric values differ beyond tolerance: {rust_val} vs {java_val} (diff: {diff:.2e} > {tolerance:.2e})",
            path=path,
            rust_value=rust_val,
            java_value=java_val,
            tolerance_used=tolerance
        )
        self.comparison_results.append(result)
        return matches
    
    def _compare_sets(self, rust_val: Any, java_val: Any, path: str) -> bool:
        """Compare set-like structures (order-independent)"""
        try:
            rust_set = set(rust_val) if not isinstance(rust_val, set) else rust_val
            java_set = set(java_val) if not isinstance(java_val, set) else java_val
            
            matches = rust_set == java_set
            
            if matches:
                details = f"Sets match ({len(rust_set)} elements)"
            else:
                only_in_rust = rust_set - java_set
                only_in_java = java_set - rust_set
                details = f"Sets differ: only in Rust: {only_in_rust}, only in Java: {only_in_java}"
            
            result = ComparisonResult(
                matches=matches,
                comparison_type=ComparisonType.SET_COMPARISON,
                details=details,
                path=path,
                rust_value=rust_val,
                java_value=java_val
            )
            self.comparison_results.append(result)
            return matches
            
        except (TypeError, ValueError) as e:
            # Fall back to exact comparison if set conversion fails
            logger.debug(f"Set comparison failed, falling back to exact: {e}")
            return self._compare_exact(rust_val, java_val, path)
    
    def _compare_partitions(self, rust_val: Any, java_val: Any, path: str) -> bool:
        """Compare partition structures (list of lists representing equivalence classes)"""
        if not isinstance(rust_val, list) or not isinstance(java_val, list):
            return self._compare_exact(rust_val, java_val, path)
        
        try:
            # Normalize partitions: sort elements within blocks and sort blocks
            rust_normalized = self._normalize_partition(rust_val)
            java_normalized = self._normalize_partition(java_val)
            
            matches = rust_normalized == java_normalized
            
            if matches:
                details = f"Partitions match ({len(rust_normalized)} blocks)"
            else:
                details = f"Partitions differ: Rust blocks: {rust_normalized}, Java blocks: {java_normalized}"
            
            result = ComparisonResult(
                matches=matches,
                comparison_type=ComparisonType.PARTITION_COMPARISON,
                details=details,
                path=path,
                rust_value=rust_val,
                java_value=java_val
            )
            self.comparison_results.append(result)
            return matches
            
        except Exception as e:
            logger.debug(f"Partition comparison failed, falling back to exact: {e}")
            return self._compare_exact(rust_val, java_val, path)
    
    def _normalize_partition(self, partition: List[List[int]]) -> List[List[int]]:
        """Normalize a partition for comparison"""
        # Sort elements within each block
        normalized_blocks = [sorted(block) for block in partition if block]
        # Sort blocks by their first element
        normalized_blocks.sort(key=lambda block: block[0] if block else float('inf'))
        return normalized_blocks
    
    def _compare_lattices(self, rust_val: Any, java_val: Any, tolerance: float, path: str) -> bool:
        """Compare lattice structures"""
        if not isinstance(rust_val, dict) or not isinstance(java_val, dict):
            return self._compare_recursive(rust_val, java_val, tolerance, path)
        
        # Compare lattice properties
        lattice_properties = ['size', 'height', 'width', 'join_irreducibles']
        all_match = True
        
        for prop in lattice_properties:
            if prop in rust_val and prop in java_val:
                prop_matches = self._compare_numeric(
                    rust_val[prop], java_val[prop], tolerance, f"{path}.{prop}"
                )
                all_match = all_match and prop_matches
            elif prop in rust_val or prop in java_val:
                # Property exists in only one result
                result = ComparisonResult(
                    matches=False,
                    comparison_type=ComparisonType.LATTICE_COMPARISON,
                    details=f"Property '{prop}' missing in {'Java' if prop in rust_val else 'Rust'}",
                    path=f"{path}.{prop}",
                    rust_value=rust_val.get(prop),
                    java_value=java_val.get(prop)
                )
                self.comparison_results.append(result)
                all_match = False
        
        return all_match
    
    def _compare_operation_tables(self, rust_val: Any, java_val: Any, path: str) -> bool:
        """Compare operation tables (2D arrays of integers)"""
        if not isinstance(rust_val, list) or not isinstance(java_val, list):
            return self._compare_exact(rust_val, java_val, path)
        
        # Check dimensions
        if len(rust_val) != len(java_val):
            result = ComparisonResult(
                matches=False,
                comparison_type=ComparisonType.OPERATION_TABLE_COMPARISON,
                details=f"Table dimensions differ: {len(rust_val)} vs {len(java_val)} rows",
                path=path,
                rust_value=rust_val,
                java_value=java_val
            )
            self.comparison_results.append(result)
            return False
        
        # Check each row
        all_match = True
        for i, (rust_row, java_row) in enumerate(zip(rust_val, java_val)):
            if not isinstance(rust_row, list) or not isinstance(java_row, list):
                row_matches = rust_row == java_row
            else:
                if len(rust_row) != len(java_row):
                    row_matches = False
                else:
                    row_matches = all(r == j for r, j in zip(rust_row, java_row))
            
            if not row_matches:
                result = ComparisonResult(
                    matches=False,
                    comparison_type=ComparisonType.OPERATION_TABLE_COMPARISON,
                    details=f"Row {i} differs: {rust_row} vs {java_row}",
                    path=f"{path}[{i}]",
                    rust_value=rust_row,
                    java_value=java_row
                )
                self.comparison_results.append(result)
                all_match = False
        
        if all_match:
            result = ComparisonResult(
                matches=True,
                comparison_type=ComparisonType.OPERATION_TABLE_COMPARISON,
                details=f"Operation table matches ({len(rust_val)}x{len(rust_val[0]) if rust_val else 0})",
                path=path,
                rust_value=rust_val,
                java_value=java_val
            )
            self.comparison_results.append(result)
        
        return all_match
    
    def _compare_recursive(self, rust_val: Any, java_val: Any, tolerance: float, path: str) -> bool:
        """Recursively compare complex data structures"""
        # Handle None values
        if rust_val is None and java_val is None:
            return True
        if rust_val is None or java_val is None:
            result = ComparisonResult(
                matches=False,
                comparison_type=ComparisonType.EXACT,
                details=f"None mismatch: Rust={rust_val}, Java={java_val}",
                path=path,
                rust_value=rust_val,
                java_value=java_val
            )
            self.comparison_results.append(result)
            return False
        
        # Handle dictionaries
        if isinstance(rust_val, dict) and isinstance(java_val, dict):
            return self._compare_dicts(rust_val, java_val, tolerance, path)
        
        # Handle lists/tuples
        if isinstance(rust_val, (list, tuple)) and isinstance(java_val, (list, tuple)):
            return self._compare_sequences(rust_val, java_val, tolerance, path)
        
        # Handle numeric values
        if isinstance(rust_val, (int, float)) and isinstance(java_val, (int, float)):
            return self._compare_numeric(rust_val, java_val, tolerance, path)
        
        # Handle other types with exact comparison
        return self._compare_exact(rust_val, java_val, path)
    
    def _compare_dicts(self, rust_dict: Dict, java_dict: Dict, tolerance: float, path: str) -> bool:
        """Compare dictionary structures"""
        rust_keys = set(rust_dict.keys())
        java_keys = set(java_dict.keys())
        
        all_match = True
        
        # Check for missing keys
        if rust_keys != java_keys:
            missing_in_java = rust_keys - java_keys
            missing_in_rust = java_keys - rust_keys
            
            if missing_in_java:
                result = ComparisonResult(
                    matches=False,
                    comparison_type=ComparisonType.EXACT,
                    details=f"Keys missing in Java: {missing_in_java}",
                    path=path,
                    rust_value=list(missing_in_java),
                    java_value=None
                )
                self.comparison_results.append(result)
                all_match = False
            
            if missing_in_rust:
                result = ComparisonResult(
                    matches=False,
                    comparison_type=ComparisonType.EXACT,
                    details=f"Keys missing in Rust: {missing_in_rust}",
                    path=path,
                    rust_value=None,
                    java_value=list(missing_in_rust)
                )
                self.comparison_results.append(result)
                all_match = False
        
        # Compare values for common keys
        common_keys = rust_keys & java_keys
        for key in common_keys:
            key_matches = self._compare_recursive(
                rust_dict[key], java_dict[key], tolerance, f"{path}.{key}"
            )
            all_match = all_match and key_matches
        
        return all_match
    
    def _compare_sequences(self, rust_seq: Union[List, Tuple], java_seq: Union[List, Tuple], 
                          tolerance: float, path: str) -> bool:
        """Compare sequence structures"""
        if len(rust_seq) != len(java_seq):
            result = ComparisonResult(
                matches=False,
                comparison_type=ComparisonType.EXACT,
                details=f"Sequence length mismatch: {len(rust_seq)} vs {len(java_seq)}",
                path=path,
                rust_value=len(rust_seq),
                java_value=len(java_seq)
            )
            self.comparison_results.append(result)
            return False
        
        all_match = True
        for i, (rust_item, java_item) in enumerate(zip(rust_seq, java_seq)):
            item_matches = self._compare_recursive(
                rust_item, java_item, tolerance, f"{path}[{i}]"
            )
            all_match = all_match and item_matches
        
        return all_match
    
    def _generate_summary(self, failed_results: List[ComparisonResult]) -> str:
        """Generate a summary of failed comparisons"""
        if not failed_results:
            return "All comparisons passed"
        
        # Group failures by type
        failure_types = {}
        for result in failed_results:
            comp_type = result.comparison_type.value
            if comp_type not in failure_types:
                failure_types[comp_type] = []
            failure_types[comp_type].append(result)
        
        # Create summary
        summary_parts = []
        for comp_type, failures in failure_types.items():
            summary_parts.append(f"{len(failures)} {comp_type} failures")
        
        return "; ".join(summary_parts)

class StructuredErrorReporter:
    """
    Provides structured error reporting with context information for test failures.
    """
    
    def __init__(self):
        self.error_categories = {
            'java_unavailable': [],
            'java_operation_failed': [],
            'result_mismatch': [],
            'timeout': [],
            'exception': []
        }
    
    def report_error(self, error_type: str, test_name: str, operation: str, 
                    algebra_name: str, details: str, context: Optional[Dict] = None):
        """Report a structured error"""
        error_info = {
            'test_name': test_name,
            'operation': operation,
            'algebra_name': algebra_name,
            'details': details,
            'context': context or {}
        }
        
        if error_type in self.error_categories:
            self.error_categories[error_type].append(error_info)
        else:
            logger.warning(f"Unknown error type: {error_type}")
            self.error_categories.setdefault('unknown', []).append(error_info)
    
    def generate_error_report(self) -> Dict[str, Any]:
        """Generate a comprehensive error report"""
        total_errors = sum(len(errors) for errors in self.error_categories.values())
        
        report = {
            'total_errors': total_errors,
            'error_summary': {
                category: len(errors) 
                for category, errors in self.error_categories.items()
                if errors
            },
            'detailed_errors': self.error_categories
        }
        
        return report
    
    def print_error_summary(self):
        """Print a human-readable error summary"""
        total_errors = sum(len(errors) for errors in self.error_categories.values())
        
        if total_errors == 0:
            print("✓ No errors reported")
            return
        
        print(f"✗ {total_errors} errors reported:")
        
        for category, errors in self.error_categories.items():
            if errors:
                print(f"  {category}: {len(errors)} errors")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"    - {error['test_name']}: {error['details']}")
                if len(errors) > 3:
                    print(f"    ... and {len(errors) - 3} more")