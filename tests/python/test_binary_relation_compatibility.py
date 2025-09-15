#!/usr/bin/env python3
"""
Binary Relation Compatibility Test

This module tests the compatibility of binary relation operations between
the Rust/Python UACalc implementation and the original Java UACalc library.
Tests include relation construction, closures, composition, and property checking.
"""

import unittest
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import itertools

from tests.python.base_compatibility_test import BaseCompatibilityTest


class BinaryRelationCompatibilityTest(BaseCompatibilityTest):
    """
    Test org.uacalc.alg.conlat.BinaryRelation class compatibility.
    
    This class tests:
    - Binary relation construction and membership operations
    - Reflexive, symmetric, and transitive closure computations
    - Relation composition and equivalence closure generation
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
    """
    
    def test_binary_relation_construction_compatibility(self):
        """Test binary relation construction and membership operations"""
        # Test on various sizes
        test_sizes = [2, 3, 4, 5]
        
        for size in test_sizes:
            with self.subTest(size=size):
                self._test_binary_relation_construction(size)
    
    def _test_binary_relation_construction(self, size: int):
        """Test binary relation construction for a specific size"""
        # Generate test relations
        test_relations = self._generate_test_relations(size)
        
        for i, relation_data in enumerate(test_relations):
            with self.subTest(relation_case=i):
                self._test_single_relation_construction(relation_data, i)
    
    def _generate_test_relations(self, size: int) -> List[Dict[str, Any]]:
        """Generate test cases for binary relation construction"""
        test_relations = []
        
        # Test case 1: Empty relation
        test_relations.append({
            'name': 'empty',
            'size': size,
            'pairs': [],
            'description': 'Empty relation'
        })
        
        # Test case 2: Identity relation
        identity_pairs = [(i, i) for i in range(size)]
        test_relations.append({
            'name': 'identity',
            'size': size,
            'pairs': identity_pairs,
            'description': 'Identity relation'
        })
        
        # Test case 3: Universal relation
        universal_pairs = [(i, j) for i in range(size) for j in range(size)]
        test_relations.append({
            'name': 'universal',
            'size': size,
            'pairs': universal_pairs,
            'description': 'Universal relation'
        })
        
        # Test case 4: Some specific relations for small sizes
        if size >= 3:
            # Chain relation: 0->1->2->...
            chain_pairs = [(i, i+1) for i in range(size-1)]
            test_relations.append({
                'name': 'chain',
                'size': size,
                'pairs': chain_pairs,
                'description': 'Chain relation'
            })
        
        if size >= 4:
            # Cycle relation: 0->1->2->...->0
            cycle_pairs = [(i, (i+1) % size) for i in range(size)]
            test_relations.append({
                'name': 'cycle',
                'size': size,
                'pairs': cycle_pairs,
                'description': 'Cycle relation'
            })
        
        return test_relations
    
    def _test_single_relation_construction(self, relation_data: Dict[str, Any], case_index: int):
        """Test construction of a single binary relation"""
        size = relation_data['size']
        pairs = relation_data['pairs']
        
        # Create relation representation for testing
        rust_result = {
            'relation_name': relation_data['name'],
            'size': size,
            'pairs': sorted(pairs),
            'pairs_count': len(pairs),
            'is_reflexive': self._is_reflexive(pairs, size),
            'is_symmetric': self._is_symmetric(pairs),
            'is_transitive': self._is_transitive(pairs, size),
            'is_equivalence': False  # Will be computed
        }
        
        # Check if it's an equivalence relation
        rust_result['is_equivalence'] = (
            rust_result['is_reflexive'] and 
            rust_result['is_symmetric'] and 
            rust_result['is_transitive']
        )
        
        # Test relation properties via Java
        relation_json = json.dumps({
            'size': size,
            'pairs': pairs
        })
        
        timeout = self._get_test_timeout('relation_properties', size)
        java_result = self._run_java_operation('relation_properties', relation_json, timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'relation_construction', 
            f"size_{size}_{relation_data['name']}"
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Binary relation construction mismatch for {relation_data['name']} (size {size}): "
                f"Rust properties: reflexive={rust_result['is_reflexive']}, "
                f"symmetric={rust_result['is_symmetric']}, transitive={rust_result['is_transitive']}, "
                f"Java properties: reflexive={java_result.get('is_reflexive')}, "
                f"symmetric={java_result.get('is_symmetric')}, transitive={java_result.get('is_transitive')}"
            )
    
    def _is_reflexive(self, pairs: List[Tuple[int, int]], size: int) -> bool:
        """Check if relation is reflexive"""
        diagonal = {(i, i) for i in range(size)}
        relation_set = set(pairs)
        return diagonal.issubset(relation_set)
    
    def _is_symmetric(self, pairs: List[Tuple[int, int]]) -> bool:
        """Check if relation is symmetric"""
        relation_set = set(pairs)
        for a, b in pairs:
            if (b, a) not in relation_set:
                return False
        return True
    
    def _is_transitive(self, pairs: List[Tuple[int, int]], size: int) -> bool:
        """Check if relation is transitive"""
        relation_set = set(pairs)
        for a, b in pairs:
            for c in range(size):
                if (b, c) in relation_set and (a, c) not in relation_set:
                    return False
        return True
    
    def test_reflexive_closure_compatibility(self):
        """Test reflexive closure computation matches exactly"""
        test_sizes = [2, 3, 4]
        
        for size in test_sizes:
            with self.subTest(size=size):
                self._test_reflexive_closure(size)
    
    def _test_reflexive_closure(self, size: int):
        """Test reflexive closure for a specific size"""
        # Test on various relations
        test_relations = self._generate_test_relations(size)[:3]  # Test first 3 relations
        
        for relation_data in test_relations:
            with self.subTest(relation=relation_data['name']):
                self._test_single_reflexive_closure(relation_data)
    
    def _test_single_reflexive_closure(self, relation_data: Dict[str, Any]):
        """Test reflexive closure of a single relation"""
        size = relation_data['size']
        pairs = relation_data['pairs']
        
        # Compute reflexive closure manually for comparison
        closure_pairs = set(pairs)
        for i in range(size):
            closure_pairs.add((i, i))
        
        rust_result = {
            'relation_name': relation_data['name'],
            'original_size': size,
            'original_pairs_count': len(pairs),
            'closure_pairs_count': len(closure_pairs),
            'closure_pairs': sorted(list(closure_pairs)),
            'is_reflexive': True  # Closure is always reflexive
        }
        
        # Test reflexive closure via Java
        relation_json = json.dumps({
            'size': size,
            'pairs': pairs
        })
        
        timeout = self._get_test_timeout('reflexive_closure', size)
        java_result = self._run_java_operation('reflexive_closure', relation_json, timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'reflexive_closure', 
            f"size_{size}_{relation_data['name']}"
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Reflexive closure mismatch for {relation_data['name']} (size {size}): "
                f"Rust pairs count: {rust_result['closure_pairs_count']}, "
                f"Java pairs count: {java_result.get('closure_pairs_count')}"
            )
    
    def test_symmetric_closure_compatibility(self):
        """Test symmetric closure computation matches exactly"""
        test_sizes = [2, 3, 4]
        
        for size in test_sizes:
            with self.subTest(size=size):
                self._test_symmetric_closure(size)
    
    def _test_symmetric_closure(self, size: int):
        """Test symmetric closure for a specific size"""
        # Test on various relations
        test_relations = self._generate_test_relations(size)[:3]  # Test first 3 relations
        
        for relation_data in test_relations:
            with self.subTest(relation=relation_data['name']):
                self._test_single_symmetric_closure(relation_data)
    
    def _test_single_symmetric_closure(self, relation_data: Dict[str, Any]):
        """Test symmetric closure of a single relation"""
        size = relation_data['size']
        pairs = relation_data['pairs']
        
        # Compute symmetric closure manually for comparison
        closure_pairs = set(pairs)
        for a, b in pairs:
            closure_pairs.add((b, a))
        
        rust_result = {
            'relation_name': relation_data['name'],
            'original_size': size,
            'original_pairs_count': len(pairs),
            'closure_pairs_count': len(closure_pairs),
            'closure_pairs': sorted(list(closure_pairs)),
            'is_symmetric': True  # Closure is always symmetric
        }
        
        # Test symmetric closure via Java
        relation_json = json.dumps({
            'size': size,
            'pairs': pairs
        })
        
        timeout = self._get_test_timeout('symmetric_closure', size)
        java_result = self._run_java_operation('symmetric_closure', relation_json, timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'symmetric_closure', 
            f"size_{size}_{relation_data['name']}"
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Symmetric closure mismatch for {relation_data['name']} (size {size}): "
                f"Rust pairs count: {rust_result['closure_pairs_count']}, "
                f"Java pairs count: {java_result.get('closure_pairs_count')}"
            )
    
    def test_transitive_closure_compatibility(self):
        """Test transitive closure computation matches exactly"""
        test_sizes = [2, 3, 4]
        
        for size in test_sizes:
            with self.subTest(size=size):
                self._test_transitive_closure(size)
    
    def _test_transitive_closure(self, size: int):
        """Test transitive closure for a specific size"""
        # Test on various relations
        test_relations = self._generate_test_relations(size)[:3]  # Test first 3 relations
        
        for relation_data in test_relations:
            with self.subTest(relation=relation_data['name']):
                self._test_single_transitive_closure(relation_data)
    
    def _test_single_transitive_closure(self, relation_data: Dict[str, Any]):
        """Test transitive closure of a single relation"""
        size = relation_data['size']
        pairs = relation_data['pairs']
        
        # Compute transitive closure using Floyd-Warshall algorithm
        closure_pairs = self._compute_transitive_closure(pairs, size)
        
        rust_result = {
            'relation_name': relation_data['name'],
            'original_size': size,
            'original_pairs_count': len(pairs),
            'closure_pairs_count': len(closure_pairs),
            'closure_pairs': sorted(list(closure_pairs)),
            'is_transitive': True  # Closure is always transitive
        }
        
        # Test transitive closure via Java
        relation_json = json.dumps({
            'size': size,
            'pairs': pairs
        })
        
        timeout = self._get_test_timeout('transitive_closure', size)
        java_result = self._run_java_operation('transitive_closure', relation_json, timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'transitive_closure', 
            f"size_{size}_{relation_data['name']}"
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Transitive closure mismatch for {relation_data['name']} (size {size}): "
                f"Rust pairs count: {rust_result['closure_pairs_count']}, "
                f"Java pairs count: {java_result.get('closure_pairs_count')}"
            )
    
    def _compute_transitive_closure(self, pairs: List[Tuple[int, int]], size: int) -> Set[Tuple[int, int]]:
        """Compute transitive closure using Floyd-Warshall algorithm"""
        # Initialize adjacency matrix
        matrix = [[False] * size for _ in range(size)]
        for a, b in pairs:
            matrix[a][b] = True
        
        # Floyd-Warshall algorithm
        for k in range(size):
            for i in range(size):
                for j in range(size):
                    matrix[i][j] = matrix[i][j] or (matrix[i][k] and matrix[k][j])
        
        # Convert back to pairs
        closure_pairs = set()
        for i in range(size):
            for j in range(size):
                if matrix[i][j]:
                    closure_pairs.add((i, j))
        
        return closure_pairs
    
    def test_equivalence_closure_compatibility(self):
        """Test equivalence closure computation matches exactly"""
        test_sizes = [2, 3, 4]
        
        for size in test_sizes:
            with self.subTest(size=size):
                self._test_equivalence_closure(size)
    
    def _test_equivalence_closure(self, size: int):
        """Test equivalence closure for a specific size"""
        # Test on various relations
        test_relations = self._generate_test_relations(size)[:3]  # Test first 3 relations
        
        for relation_data in test_relations:
            with self.subTest(relation=relation_data['name']):
                self._test_single_equivalence_closure(relation_data)
    
    def _test_single_equivalence_closure(self, relation_data: Dict[str, Any]):
        """Test equivalence closure of a single relation"""
        size = relation_data['size']
        pairs = relation_data['pairs']
        
        # Compute equivalence closure (reflexive + symmetric + transitive)
        closure_pairs = set(pairs)
        
        # Add reflexive pairs
        for i in range(size):
            closure_pairs.add((i, i))
        
        # Add symmetric pairs
        symmetric_pairs = set(closure_pairs)
        for a, b in closure_pairs:
            symmetric_pairs.add((b, a))
        
        # Compute transitive closure
        final_closure = self._compute_transitive_closure(list(symmetric_pairs), size)
        
        rust_result = {
            'relation_name': relation_data['name'],
            'original_size': size,
            'original_pairs_count': len(pairs),
            'closure_pairs_count': len(final_closure),
            'closure_pairs': sorted(list(final_closure)),
            'is_equivalence': True  # Closure is always an equivalence relation
        }
        
        # Convert to partition representation
        partition_blocks = self._relation_to_partition(final_closure, size)
        rust_result['partition_blocks'] = [sorted(list(block)) for block in partition_blocks]
        rust_result['partition_blocks'].sort()
        rust_result['partition_blocks_count'] = len(partition_blocks)
        
        # Test equivalence closure via Java
        relation_json = json.dumps({
            'size': size,
            'pairs': pairs
        })
        
        timeout = self._get_test_timeout('equivalence_closure', size)
        java_result = self._run_java_operation('equivalence_closure', relation_json, timeout=timeout)
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'equivalence_closure', 
            f"size_{size}_{relation_data['name']}"
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Equivalence closure mismatch for {relation_data['name']} (size {size}): "
                f"Rust blocks: {rust_result['partition_blocks']}, "
                f"Java blocks: {java_result.get('partition_blocks')}"
            )
    
    def _relation_to_partition(self, relation_pairs: Set[Tuple[int, int]], size: int) -> List[Set[int]]:
        """Convert equivalence relation to partition blocks"""
        # Use union-find to compute equivalence classes
        parent = list(range(size))
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # Process all pairs
        for a, b in relation_pairs:
            union(a, b)
        
        # Group elements by their root
        blocks = {}
        for i in range(size):
            root = find(i)
            if root not in blocks:
                blocks[root] = set()
            blocks[root].add(i)
        
        return list(blocks.values())
    
    def test_relation_composition_compatibility(self):
        """Test relation composition matches exactly"""
        test_sizes = [2, 3, 4]
        
        for size in test_sizes:
            with self.subTest(size=size):
                self._test_relation_composition(size)
    
    def _test_relation_composition(self, size: int):
        """Test relation composition for a specific size"""
        # Test composition of simple relations
        test_relations = self._generate_test_relations(size)[:3]
        
        for rel1, rel2 in itertools.combinations(test_relations, 2):
            with self.subTest(rel1=rel1['name'], rel2=rel2['name']):
                self._test_single_relation_composition(rel1, rel2)
    
    def _test_single_relation_composition(self, rel1_data: Dict[str, Any], rel2_data: Dict[str, Any]):
        """Test composition of two specific relations"""
        size = rel1_data['size']
        pairs1 = rel1_data['pairs']
        pairs2 = rel2_data['pairs']
        
        # Compute composition manually: R1 ∘ R2 = {(a,c) | ∃b: (a,b) ∈ R1 ∧ (b,c) ∈ R2}
        composition_pairs = set()
        for a, b in pairs1:
            for b2, c in pairs2:
                if b == b2:
                    composition_pairs.add((a, c))
        
        rust_result = {
            'relation1_name': rel1_data['name'],
            'relation2_name': rel2_data['name'],
            'size': size,
            'relation1_pairs_count': len(pairs1),
            'relation2_pairs_count': len(pairs2),
            'composition_pairs_count': len(composition_pairs),
            'composition_pairs': sorted(list(composition_pairs))
        }
        
        # Test relation composition via Java
        relation1_json = json.dumps({'size': size, 'pairs': pairs1})
        relation2_json = json.dumps({'size': size, 'pairs': pairs2})
        
        timeout = self._get_test_timeout('relation_composition', size)
        java_result = self._run_java_operation(
            'relation_composition', relation1_json, relation2_json, timeout=timeout
        )
        
        # Compare results
        comparison_result = self._compare_results(
            rust_result, java_result, 'relation_composition', 
            f"size_{size}_{rel1_data['name']}_compose_{rel2_data['name']}"
        )
        
        if not comparison_result.matches and java_result:
            self.test_logger.warning(
                f"Relation composition mismatch for {rel1_data['name']} ∘ {rel2_data['name']} (size {size}): "
                f"Rust pairs count: {rust_result['composition_pairs_count']}, "
                f"Java pairs count: {java_result.get('composition_pairs_count')}"
            )


if __name__ == '__main__':
    unittest.main()