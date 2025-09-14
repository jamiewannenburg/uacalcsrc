#!/usr/bin/env python3
"""
Test Data Management System for UACalc Compatibility Testing

This module provides utilities for discovering, categorizing, and managing
test algebra files and generating systematic test cases.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import uacalc

class AlgebraComplexity(Enum):
    """Categorization of algebra complexity for testing"""
    TRIVIAL = "trivial"      # Size 1-2
    SMALL = "small"          # Size 3-5  
    MEDIUM = "medium"        # Size 6-10
    LARGE = "large"          # Size 11-20
    VERY_LARGE = "very_large" # Size > 20

@dataclass
class AlgebraMetadata:
    """Metadata about a test algebra"""
    file_path: Path
    name: str
    cardinality: int
    operation_count: int
    operation_symbols: List[str]
    operation_arities: List[int]
    complexity: AlgebraComplexity
    file_size_bytes: int
    load_time_ms: float
    
class TestDataManager:
    """Manages test algebra files and generates test cases"""
    
    def __init__(self, resources_dir: str = "resources/algebras"):
        self.resources_dir = Path(resources_dir)
        self.algebra_metadata: Dict[str, AlgebraMetadata] = {}
        self.metadata_cache_file = Path("tests/python/.algebra_metadata_cache.json")
        self._load_metadata_cache()
    
    def discover_algebras(self) -> List[Path]:
        """Discover all algebra files and extract metadata"""
        if not self.resources_dir.exists():
            return []
        
        algebra_files = list(self.resources_dir.glob("*.ua"))
        
        # Extract metadata for each algebra
        for ua_file in algebra_files:
            if str(ua_file) not in self.algebra_metadata:
                try:
                    metadata = self._extract_metadata(ua_file)
                    self.algebra_metadata[str(ua_file)] = metadata
                except Exception as e:
                    print(f"Warning: Could not extract metadata from {ua_file}: {e}")
        
        # Save updated metadata cache
        self._save_metadata_cache()
        
        return algebra_files
    
    def get_algebras_by_complexity(self, complexity: AlgebraComplexity) -> List[Path]:
        """Get algebras filtered by complexity level"""
        return [
            Path(file_path) for file_path, metadata in self.algebra_metadata.items()
            if metadata.complexity == complexity
        ]
    
    def get_algebras_by_size_range(self, min_size: int, max_size: int) -> List[Path]:
        """Get algebras within a specific size range"""
        return [
            Path(file_path) for file_path, metadata in self.algebra_metadata.items()
            if min_size <= metadata.cardinality <= max_size
        ]
    
    def get_test_algebra_pairs(self) -> List[Tuple[Path, Path]]:
        """Generate pairs of algebras for isomorphism testing"""
        algebra_files = list(self.algebra_metadata.keys())
        pairs = []
        
        for i in range(len(algebra_files)):
            for j in range(i + 1, len(algebra_files)):
                file1, file2 = Path(algebra_files[i]), Path(algebra_files[j])
                metadata1 = self.algebra_metadata[algebra_files[i]]
                metadata2 = self.algebra_metadata[algebra_files[j]]
                
                # Only pair algebras of similar complexity for meaningful tests
                if (metadata1.complexity == metadata2.complexity or
                    abs(metadata1.cardinality - metadata2.cardinality) <= 2):
                    pairs.append((file1, file2))
        
        return pairs
    
    def generate_element_pairs(self, cardinality: int, max_pairs: int = 10) -> List[Tuple[int, int]]:
        """Generate element pairs for congruence testing"""
        pairs = []
        
        # Generate all pairs for small algebras
        if cardinality <= 5:
            for a in range(cardinality):
                for b in range(a, cardinality):
                    pairs.append((a, b))
        else:
            # Sample pairs for larger algebras
            import random
            random.seed(42)  # Deterministic sampling
            
            # Always include diagonal pairs
            for i in range(min(cardinality, 5)):
                pairs.append((i, i))
            
            # Add some random pairs
            while len(pairs) < max_pairs and len(pairs) < cardinality * (cardinality - 1) // 2:
                a = random.randint(0, cardinality - 1)
                b = random.randint(0, cardinality - 1)
                if (a, b) not in pairs and (b, a) not in pairs:
                    pairs.append((min(a, b), max(a, b)))
        
        return pairs[:max_pairs]
    
    def generate_generator_sets(self, cardinality: int) -> List[List[int]]:
        """Generate different generator sets for subalgebra testing"""
        generator_sets = []
        
        # Single element generators
        for i in range(min(cardinality, 3)):
            generator_sets.append([i])
        
        # Two element generators
        if cardinality > 1:
            generator_sets.append([0, 1])
            if cardinality > 2:
                generator_sets.append([0, 2])
                generator_sets.append([1, 2])
        
        # Three element generators for larger algebras
        if cardinality > 3:
            generator_sets.append([0, 1, 2])
        
        # Full universe (should generate the whole algebra)
        if cardinality <= 5:
            generator_sets.append(list(range(cardinality)))
        
        return generator_sets
    
    def get_algebra_summary(self) -> Dict[str, Any]:
        """Get summary statistics about discovered algebras"""
        if not self.algebra_metadata:
            return {}
        
        complexities = {}
        total_algebras = len(self.algebra_metadata)
        size_distribution = {}
        operation_count_distribution = {}
        
        for metadata in self.algebra_metadata.values():
            # Complexity distribution
            complexity = metadata.complexity.value
            complexities[complexity] = complexities.get(complexity, 0) + 1
            
            # Size distribution
            size_range = f"{metadata.cardinality}"
            if metadata.cardinality > 10:
                size_range = "10+"
            size_distribution[size_range] = size_distribution.get(size_range, 0) + 1
            
            # Operation count distribution
            op_count = metadata.operation_count
            operation_count_distribution[op_count] = operation_count_distribution.get(op_count, 0) + 1
        
        return {
            "total_algebras": total_algebras,
            "complexity_distribution": complexities,
            "size_distribution": size_distribution,
            "operation_count_distribution": operation_count_distribution,
            "average_cardinality": sum(m.cardinality for m in self.algebra_metadata.values()) / total_algebras,
            "average_operations": sum(m.operation_count for m in self.algebra_metadata.values()) / total_algebras
        }
    
    def _extract_metadata(self, ua_file: Path) -> AlgebraMetadata:
        """Extract metadata from an algebra file"""
        import time
        
        start_time = time.time()
        algebra = uacalc.load_algebra(str(ua_file))
        load_time_ms = (time.time() - start_time) * 1000
        
        cardinality = algebra.cardinality
        operations = algebra.operations()
        operation_count = len(operations)
        operation_symbols = [op.symbol for op in operations]
        operation_arities = [op.arity() for op in operations]
        
        # Determine complexity
        if cardinality <= 2:
            complexity = AlgebraComplexity.TRIVIAL
        elif cardinality <= 5:
            complexity = AlgebraComplexity.SMALL
        elif cardinality <= 10:
            complexity = AlgebraComplexity.MEDIUM
        elif cardinality <= 20:
            complexity = AlgebraComplexity.LARGE
        else:
            complexity = AlgebraComplexity.VERY_LARGE
        
        return AlgebraMetadata(
            file_path=ua_file,
            name=algebra.name,
            cardinality=cardinality,
            operation_count=operation_count,
            operation_symbols=operation_symbols,
            operation_arities=operation_arities,
            complexity=complexity,
            file_size_bytes=ua_file.stat().st_size,
            load_time_ms=load_time_ms
        )
    
    def _load_metadata_cache(self):
        """Load metadata cache from file"""
        if self.metadata_cache_file.exists():
            try:
                with open(self.metadata_cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                for file_path, metadata_dict in cache_data.items():
                    # Convert dict back to AlgebraMetadata
                    metadata_dict['file_path'] = Path(metadata_dict['file_path'])
                    metadata_dict['complexity'] = AlgebraComplexity(metadata_dict['complexity'])
                    self.algebra_metadata[file_path] = AlgebraMetadata(**metadata_dict)
            except Exception as e:
                print(f"Warning: Could not load metadata cache: {e}")
    
    def _save_metadata_cache(self):
        """Save metadata cache to file"""
        try:
            # Create directory if it doesn't exist
            self.metadata_cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert metadata to serializable format
            cache_data = {}
            for file_path, metadata in self.algebra_metadata.items():
                cache_data[file_path] = {
                    'file_path': str(metadata.file_path),
                    'name': metadata.name,
                    'cardinality': metadata.cardinality,
                    'operation_count': metadata.operation_count,
                    'operation_symbols': metadata.operation_symbols,
                    'operation_arities': metadata.operation_arities,
                    'complexity': metadata.complexity.value,
                    'file_size_bytes': metadata.file_size_bytes,
                    'load_time_ms': metadata.load_time_ms
                }
            
            with open(self.metadata_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metadata cache: {e}")

class TestCaseGenerator:
    """Generates systematic test cases for comprehensive coverage"""
    
    def __init__(self, data_manager: TestDataManager):
        self.data_manager = data_manager
    
    def generate_operation_test_cases(self, operation_arity: int, algebra_size: int, max_cases: int = 20) -> List[List[int]]:
        """Generate comprehensive operation evaluation test cases"""
        if operation_arity == 0:
            return [[]]  # Nullary operation
        
        test_cases = []
        
        # For small algebras, test all combinations
        if algebra_size ** operation_arity <= max_cases:
            import itertools
            test_cases = list(itertools.product(range(algebra_size), repeat=operation_arity))
        else:
            # Sample test cases for larger algebras
            import random
            random.seed(42)  # Deterministic sampling
            
            # Always include corner cases
            corner_cases = [
                [0] * operation_arity,  # All zeros
                [algebra_size - 1] * operation_arity,  # All max elements
            ]
            
            # Add diagonal cases for binary operations
            if operation_arity == 2:
                for i in range(min(algebra_size, 5)):
                    corner_cases.append([i, i])
            
            test_cases.extend(corner_cases)
            
            # Add random cases
            while len(test_cases) < max_cases:
                case = [random.randint(0, algebra_size - 1) for _ in range(operation_arity)]
                if case not in test_cases:
                    test_cases.append(case)
        
        return [list(case) for case in test_cases[:max_cases]]
    
    def generate_comprehensive_test_plan(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate a comprehensive test plan for all discovered algebras"""
        algebras = self.data_manager.discover_algebras()
        test_plan = {
            "algebra_properties": [],
            "congruence_generation": [],
            "subalgebra_generation": [],
            "isomorphism_checking": [],
            "maltsev_conditions": [],
            "operation_evaluation": []
        }
        
        for ua_file in algebras:
            metadata = self.data_manager.algebra_metadata.get(str(ua_file))
            if not metadata:
                continue
            
            # Algebra properties tests (all algebras)
            test_plan["algebra_properties"].append({
                "file": str(ua_file),
                "name": metadata.name,
                "complexity": metadata.complexity.value
            })
            
            # Congruence generation tests (skip very large algebras)
            if metadata.complexity != AlgebraComplexity.VERY_LARGE:
                element_pairs = self.data_manager.generate_element_pairs(metadata.cardinality)
                test_plan["congruence_generation"].append({
                    "file": str(ua_file),
                    "name": metadata.name,
                    "element_pairs": element_pairs[:5]  # Limit pairs for testing
                })
            
            # Subalgebra generation tests (skip large algebras)
            if metadata.complexity in [AlgebraComplexity.TRIVIAL, AlgebraComplexity.SMALL, AlgebraComplexity.MEDIUM]:
                generator_sets = self.data_manager.generate_generator_sets(metadata.cardinality)
                test_plan["subalgebra_generation"].append({
                    "file": str(ua_file),
                    "name": metadata.name,
                    "generator_sets": generator_sets
                })
            
            # Maltsev conditions (small to medium algebras)
            if metadata.complexity in [AlgebraComplexity.SMALL, AlgebraComplexity.MEDIUM]:
                test_plan["maltsev_conditions"].append({
                    "file": str(ua_file),
                    "name": metadata.name,
                    "complexity": metadata.complexity.value
                })
            
            # Operation evaluation tests
            for i, (symbol, arity) in enumerate(zip(metadata.operation_symbols, metadata.operation_arities)):
                test_cases = self.generate_operation_test_cases(arity, metadata.cardinality)
                test_plan["operation_evaluation"].append({
                    "file": str(ua_file),
                    "name": metadata.name,
                    "operation_index": i,
                    "operation_symbol": symbol,
                    "operation_arity": arity,
                    "test_cases": test_cases[:10]  # Limit test cases
                })
        
        # Isomorphism checking tests (pairs of algebras)
        algebra_pairs = self.data_manager.get_test_algebra_pairs()
        for file1, file2 in algebra_pairs[:10]:  # Limit pairs
            metadata1 = self.data_manager.algebra_metadata.get(str(file1))
            metadata2 = self.data_manager.algebra_metadata.get(str(file2))
            if metadata1 and metadata2:
                test_plan["isomorphism_checking"].append({
                    "file1": str(file1),
                    "file2": str(file2),
                    "name1": metadata1.name,
                    "name2": metadata2.name,
                    "complexity1": metadata1.complexity.value,
                    "complexity2": metadata2.complexity.value
                })
        
        return test_plan