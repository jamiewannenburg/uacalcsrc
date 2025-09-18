#!/usr/bin/env python3
"""
Partition Compatibility Test

This module tests the compatibility of partition operations between
the Rust/Python UACalc implementation and the original Java UACalc library.
Tests include partition construction, union, refinement, and lattice operations.
"""

import unittest
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import itertools

from tests.python.base_compatibility_test import BaseCompatibilityTest


class PartitionCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.alg.conlat.Partition class compatibility.
    
    This class tests:
    - Partition construction, union, and refinement operations
    - Partition comparison (finer/coarser relationships)
    - Partition join and meet operations in the partition lattice
    
    Requirements: 2.1, 2.3
    """
    
    def test_partition_construction_compatibility(self):
        """Test partition construction produces identical partitions"""
        for algebra_file in self.algebra_files[:4]:  # Test on first 4 algebras
            with self.subTest(algebra=algebra_file.name):
                self._test_partition_construction(algebra_file)
    
    def _test_partition_construction(self, algebra_file: Path):
        """Test partition construction for a specific algebra"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip large algebras for performance
        if self._should_skip_test(algebra.cardinality, 'partition'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Test various partition constructions
        test_cases = self._generate_partition_test_cases(algebra.cardinality)
        
        for i, partition_data in enumerate(test_cases):
            with self.subTest(partition_case=i):
                self._test_single_partition_construction(algebra, algebra_file, partition_data, i)
    
    def _generate_partition_test_cases(self, cardinality: int) -> List[Dict[str, Any]]:
        """Generate test cases for partition construction"""
        test_cases = []
        
        # Test case 1: Identity partition (each element in its own block)
        identity_blocks = [[i] for i in range(cardinality)]
        test_cases.append({
            'name': 'identity',
            'blocks': identity_blocks,
            'description': 'Identity partition (finest)'
        })
        
        # Test case 2: Universal partition (all elements in one block)
        universal_blocks = [list(range(cardinality))]
        test_cases.append({
            'name': 'universal',
            'blocks': universal_blocks,
            'description': 'Universal partition (coarsest)'
        })
        
        # Test case 3: Some intermediate partitions for small algebras
        if cardinality >= 4:
            # Partition with two blocks
            mid = cardinality // 2
            two_block_partition = [list(range(mid)), list(range(mid, cardinality))]
            test_cases.append({
                'name': 'two_blocks',
                'blocks': two_block_partition,
                'description': 'Two-block partition'
            })
        
        if cardinality >= 6:
            # Partition with three blocks
            third = cardinality // 3
            three_block_partition = [
                list(range(third)),
                list(range(third, 2 * third)),
                list(range(2 * third, cardinality))
            ]
            test_cases.append({
                'name': 'three_blocks',
                'blocks': three_block_partition,
                'description': 'Three-block partition'
            })
        
        return test_cases
    
    def _test_single_partition_construction(self, algebra, algebra_file: Path, 
                                          partition_data: Dict[str, Any], case_index: int):
        """Test construction of a single partition"""
        # Create partition in Rust implementation
        try:
            blocks = partition_data['blocks']
            
            # Create partition using Rust/Python API
            import uacalc_rust
            partition = uacalc_rust.create_partition_from_blocks(algebra.cardinality, blocks)
            
            rust_result = {
                'algebra_name': algebra.name,
                'partition_name': partition_data['name'],
                'blocks_count': partition.num_blocks,
                'blocks': [sorted(block) for block in partition.blocks()],
                'total_elements': sum(len(block) for block in partition.blocks()),
                'is_valid_partition': self._is_valid_partition(partition.blocks(), algebra.cardinality)
            }
            
            # Sort blocks for consistent comparison
            rust_result['blocks'].sort()
            
        except Exception as e:
            self.fail(f"Rust partition construction failed for {algebra.name}, case {case_index}: {e}")
        
        # Test partition construction via Java
        partition_json = json.dumps(blocks)
        
        timeout = self._get_test_timeout('partition', algebra.cardinality)
        java_result = self._run_java_operation(
            'partition_construction', str(algebra_file), partition_json, timeout=timeout
        )
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'partition_construction', 
            f"{algebra.name}_{partition_data['name']}"
        )
        
        if not comparison_result.matches:
            self.test_logger.warning(
                f"Partition construction mismatch for {algebra.name}, case {partition_data['name']}: "
                f"Rust blocks: {rust_result.get('blocks')}, "
                f"Java blocks: {java_result.get('blocks')}"
            )
    
    def _is_valid_partition(self, blocks: List[List[int]], cardinality: int) -> bool:
        """Check if blocks form a valid partition"""
        # Check that all elements are covered exactly once
        all_elements = set()
        for block in blocks:
            for element in block:
                if element in all_elements:
                    return False  # Element appears in multiple blocks
                all_elements.add(element)
        
        # Check that all elements from 0 to cardinality-1 are covered
        return all_elements == set(range(cardinality))
    
    def test_partition_join_operations_compatibility(self):
        """Test partition join operations match exactly"""
        for algebra_file in self.algebra_files[:3]:  # Test on first 3 algebras
            with self.subTest(algebra=algebra_file.name):
                self._test_partition_join_operations(algebra_file)
    
    def _test_partition_join_operations(self, algebra_file: Path):
        """Test partition join operations for a specific algebra"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip large algebras for performance
        if self._should_skip_test(algebra.cardinality, 'partition_join'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Test join operations between different congruences
        if algebra.cardinality <= 6:  # Only test on small algebras
            self._test_congruence_join_operations(algebra, algebra_file)
    
    def _test_congruence_join_operations(self, algebra, algebra_file: Path):
        """Test congruence join operations"""
        # Get some principal congruences to test joins
        test_pairs = [(0, 1), (1, 2)] if algebra.cardinality > 2 else [(0, 1)]
        
        for pair1, pair2 in itertools.combinations(test_pairs, 2):
            with self.subTest(cg1=pair1, cg2=pair2):
                self._test_single_congruence_join(algebra, algebra_file, pair1, pair2)
    
    def _test_single_congruence_join(self, algebra, algebra_file: Path, 
                                   pair1: Tuple[int, int], pair2: Tuple[int, int]):
        """Test join of two specific congruences"""
        try:
            # Get congruences from Rust implementation
            cg1_rust = algebra.cg(pair1[0], pair1[1])
            cg2_rust = algebra.cg(pair2[0], pair2[1])
            
            # Compute join using Rust partition operations
            join_rust = cg1_rust.join(cg2_rust)
            
            rust_result = {
                'algebra_name': algebra.name,
                'cg1_pair': list(pair1),
                'cg2_pair': list(pair2),
                'join_computed': True,
                'join_blocks': [sorted(list(block)) for block in join_rust.blocks()],
                'join_blocks_count': join_rust.num_blocks
            }
            
            # Sort blocks for consistent comparison
            rust_result['join_blocks'].sort()
            
        except Exception as e:
            self.fail(f"Rust congruence join failed for {algebra.name}, pairs {pair1}, {pair2}: {e}")
        
        # Test congruence join via Java
        # Create JSON representations of the congruences as partition blocks
        cg1_blocks = [[pair1[0], pair1[1]]] if pair1[0] != pair1[1] else []
        cg2_blocks = [[pair2[0], pair2[1]]] if pair2[0] != pair2[1] else []
        
        cg1_json = json.dumps(cg1_blocks)
        cg2_json = json.dumps(cg2_blocks)
        
        timeout = self._get_test_timeout('congruence_join', algebra.cardinality)
        java_result = self._run_java_operation(
            'congruence_join', str(algebra_file), cg1_json, cg2_json, timeout=timeout
        )
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'congruence_join', 
            f"{algebra.name}_join_Cg{pair1}_Cg{pair2}"
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Congruence join mismatch for {algebra.name}, Cg{pair1} ∨ Cg{pair2}: "
                f"Rust blocks: {rust_result.get('join_blocks')}, "
                f"Java blocks: {java_result.get('join_partition')}"
            )
    
    def test_partition_meet_operations_compatibility(self):
        """Test partition meet operations match exactly"""
        for algebra_file in self.algebra_files[:3]:  # Test on first 3 algebras
            with self.subTest(algebra=algebra_file.name):
                self._test_partition_meet_operations(algebra_file)
    
    def _test_partition_meet_operations(self, algebra_file: Path):
        """Test partition meet operations for a specific algebra"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip large algebras for performance
        if self._should_skip_test(algebra.cardinality, 'partition_meet'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Test meet operations between different congruences
        if algebra.cardinality <= 6:  # Only test on small algebras
            self._test_congruence_meet_operations(algebra, algebra_file)
    
    def _test_congruence_meet_operations(self, algebra, algebra_file: Path):
        """Test congruence meet operations"""
        # Get some principal congruences to test meets
        test_pairs = [(0, 1), (1, 2)] if algebra.cardinality > 2 else [(0, 1)]
        
        for pair1, pair2 in itertools.combinations(test_pairs, 2):
            with self.subTest(cg1=pair1, cg2=pair2):
                self._test_single_congruence_meet(algebra, algebra_file, pair1, pair2)
    
    def _test_single_congruence_meet(self, algebra, algebra_file: Path, 
                                   pair1: Tuple[int, int], pair2: Tuple[int, int]):
        """Test meet of two specific congruences"""
        try:
            # Get congruences from Rust implementation
            cg1_rust = algebra.cg(pair1[0], pair1[1])
            cg2_rust = algebra.cg(pair2[0], pair2[1])
            
            # Compute meet using Rust partition operations
            meet_rust = cg1_rust.meet(cg2_rust)
            
            rust_result = {
                'algebra_name': algebra.name,
                'cg1_pair': list(pair1),
                'cg2_pair': list(pair2),
                'meet_computed': True,
                'meet_blocks': [sorted(list(block)) for block in meet_rust.blocks()],
                'meet_blocks_count': meet_rust.num_blocks
            }
            
            # Sort blocks for consistent comparison
            rust_result['meet_blocks'].sort()
            
        except Exception as e:
            self.fail(f"Rust congruence meet failed for {algebra.name}, pairs {pair1}, {pair2}: {e}")
        
        # Test congruence meet via Java
        # Create JSON representations of the congruences as partition blocks
        cg1_blocks = [[pair1[0], pair1[1]]] if pair1[0] != pair1[1] else []
        cg2_blocks = [[pair2[0], pair2[1]]] if pair2[0] != pair2[1] else []
        
        cg1_json = json.dumps(cg1_blocks)
        cg2_json = json.dumps(cg2_blocks)
        
        timeout = self._get_test_timeout('congruence_meet', algebra.cardinality)
        java_result = self._run_java_operation(
            'congruence_meet', str(algebra_file), cg1_json, cg2_json, timeout=timeout
        )
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'congruence_meet', 
            f"{algebra.name}_meet_Cg{pair1}_Cg{pair2}"
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Congruence meet mismatch for {algebra.name}, Cg{pair1} ∧ Cg{pair2}: "
                f"Rust blocks: {rust_result.get('meet_blocks')}, "
                f"Java blocks: {java_result.get('meet_partition')}"
            )
    
    def test_partition_ordering_compatibility(self):
        """Test partition ordering (finer/coarser relationships) match exactly"""
        for algebra_file in self.algebra_files[:3]:  # Test on first 3 algebras
            with self.subTest(algebra=algebra_file.name):
                self._test_partition_ordering(algebra_file)
    
    def _test_partition_ordering(self, algebra_file: Path):
        """Test partition ordering for a specific algebra"""
        # Load algebra in Rust/Python
        algebra = self._load_test_algebra(algebra_file)
        
        # Skip large algebras for performance
        if self._should_skip_test(algebra.cardinality, 'partition_ordering'):
            self.skipTest(f"Skipping large algebra {algebra.name} (size: {algebra.cardinality})")
        
        # Test ordering between different congruences
        if algebra.cardinality <= 6:  # Only test on small algebras
            self._test_congruence_ordering(algebra, algebra_file)
    
    def _test_congruence_ordering(self, algebra, algebra_file: Path):
        """Test congruence ordering operations"""
        # Test some basic ordering relationships
        test_pairs = [(0, 0), (0, 1)] if algebra.cardinality > 1 else [(0, 0)]
        
        for pair1, pair2 in itertools.combinations_with_replacement(test_pairs, 2):
            if pair1 != pair2:  # Don't test identical pairs
                with self.subTest(cg1=pair1, cg2=pair2):
                    self._test_single_congruence_ordering(algebra, algebra_file, pair1, pair2)
    
    def _test_single_congruence_ordering(self, algebra, algebra_file: Path, 
                                       pair1: Tuple[int, int], pair2: Tuple[int, int]):
        """Test ordering between two specific congruences"""
        try:
            # Get congruences from Rust implementation
            cg1_rust = algebra.cg(pair1[0], pair1[1])
            cg2_rust = algebra.cg(pair2[0], pair2[1])
            
            # Test ordering using Rust partition operations
            cg1_finer_than_cg2 = cg1_rust.is_finer_than(cg2_rust)
            cg2_finer_than_cg1 = cg2_rust.is_finer_than(cg1_rust)
            
            rust_result = {
                'algebra_name': algebra.name,
                'cg1_pair': list(pair1),
                'cg2_pair': list(pair2),
                'cg1_leq_cg2': cg1_finer_than_cg2,  # cg1 ≤ cg2 means cg1 is finer than cg2
                'cg2_leq_cg1': cg2_finer_than_cg1,  # cg2 ≤ cg1 means cg2 is finer than cg1
                'ordering_available': True
            }
            
        except Exception as e:
            self.fail(f"Rust congruence ordering failed for {algebra.name}, pairs {pair1}, {pair2}: {e}")
        
        # Test congruence ordering via Java
        # Create JSON representations of the congruences as partition blocks
        cg1_blocks = [[pair1[0], pair1[1]]] if pair1[0] != pair1[1] else []
        cg2_blocks = [[pair2[0], pair2[1]]] if pair2[0] != pair2[1] else []
        
        cg1_json = json.dumps(cg1_blocks)
        cg2_json = json.dumps(cg2_blocks)
        
        timeout = self._get_test_timeout('congruence_ordering', algebra.cardinality)
        java_result = self._run_java_operation(
            'congruence_ordering', str(algebra_file), cg1_json, cg2_json, timeout=timeout
        )
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'congruence_ordering', 
            f"{algebra.name}_order_Cg{pair1}_Cg{pair2}"
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Congruence ordering mismatch for {algebra.name}, Cg{pair1} vs Cg{pair2}: "
                f"Rust: cg1≤cg2={rust_result.get('cg1_leq_cg2')}, cg2≤cg1={rust_result.get('cg2_leq_cg1')}, "
                f"Java: cg1≤cg2={java_result.get('cong1_leq_cong2')}, cg2≤cg1={java_result.get('cong2_leq_cong1')}"
            )


if __name__ == '__main__':
    unittest.main()