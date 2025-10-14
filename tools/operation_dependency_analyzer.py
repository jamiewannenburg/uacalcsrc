#!/usr/bin/env python3
"""
Operation Dependency Analyzer

This tool specifically analyzes the dependency chain for operation-related classes
to determine the correct implementation order.
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

class OperationDependencyAnalyzer:
    def __init__(self, source_root: str):
        self.source_root = Path(source_root)
        self.operation_files = {
            'Operation.java': 'org/uacalc/alg/op/Operation.java',
            'AbstractOperation.java': 'org/uacalc/alg/op/AbstractOperation.java', 
            'Operations.java': 'org/uacalc/alg/op/Operations.java',
            'SequenceGenerator.java': 'org/uacalc/util/SequenceGenerator.java'
        }
        
    def analyze_operation_dependencies(self):
        """Analyze dependencies for operation classes."""
        print("Analyzing Operation Class Dependencies")
        print("=" * 50)
        
        results = {}
        
        for class_name, file_path in self.operation_files.items():
            full_path = self.source_root / file_path
            if full_path.exists():
                print(f"\nAnalyzing {class_name}...")
                analysis = self._analyze_file(full_path)
                results[class_name] = analysis
                self._print_analysis(class_name, analysis)
            else:
                print(f"File not found: {full_path}")
        
        return results
    
    def _analyze_file(self, file_path: Path) -> Dict:
        """Analyze a single Java file for dependencies."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        analysis = {
            'file_path': str(file_path),
            'implements': [],
            'extends': [],
            'static_method_calls': [],
            'instance_method_calls': [],
            'constructor_calls': [],
            'uacalc_dependencies': set()
        }
        
        # Extract implements clause
        implements_match = re.search(r'implements\s+([^{]+)', content)
        if implements_match:
            implements_str = implements_match.group(1)
            analysis['implements'] = [imp.strip() for imp in implements_str.split(',')]
        
        # Extract extends clause  
        extends_match = re.search(r'extends\s+([^{]+)', content)
        if extends_match:
            extends_str = extends_match.group(1)
            analysis['extends'] = [ext.strip() for ext in extends_str.split(',')]
        
        # Find static method calls (Class.method() pattern)
        static_calls = re.findall(r'(\w+(?:\.\w+)*)\.(\w+)\s*\(', content)
        for class_name, method_name in static_calls:
            if self._is_uacalc_class(class_name):
                analysis['static_method_calls'].append(f"{class_name}.{method_name}")
                analysis['uacalc_dependencies'].add(class_name)
        
        # Find constructor calls (new Class() pattern)
        constructor_calls = re.findall(r'new\s+(\w+(?:\.\w+)*)\s*\(', content)
        for class_name in constructor_calls:
            if self._is_uacalc_class(class_name):
                analysis['constructor_calls'].append(class_name)
                analysis['uacalc_dependencies'].add(class_name)
        
        # Find specific method calls we know about
        specific_calls = [
            'Operations.isTotal',
            'Operations.isTotallySymmetric', 
            'Operations.isAssociative',
            'Operations.isCommutative',
            'Operations.isMaltsev',
            'SequenceGenerator.sequenceIncrementor',
            'SequenceGenerator.nondecreasingSequenceIncrementor',
            'ArrayString.toString',
            'Horner.horner',
            'Horner.hornerInv'
        ]
        
        for call in specific_calls:
            if call in content:
                class_name = call.split('.')[0]
                if self._is_uacalc_class(class_name):
                    analysis['static_method_calls'].append(call)
                    analysis['uacalc_dependencies'].add(class_name)
        
        return analysis
    
    def _is_uacalc_class(self, class_name: str) -> bool:
        """Check if a class name is a UACalc class."""
        uacalc_classes = [
            'Operation', 'AbstractOperation', 'Operations', 'OperationSymbol',
            'SequenceGenerator', 'ArrayString', 'Horner', 'ArrayIncrementor',
            'PermutationGenerator', 'IntArray', 'SimpleList'
        ]
        return class_name in uacalc_classes
    
    def _print_analysis(self, class_name: str, analysis: Dict):
        """Print analysis results for a class."""
        print(f"  File: {Path(analysis['file_path']).name}")
        
        if analysis['implements']:
            print(f"  Implements: {', '.join(analysis['implements'])}")
        
        if analysis['extends']:
            print(f"  Extends: {', '.join(analysis['extends'])}")
        
        if analysis['static_method_calls']:
            print(f"  Static Method Calls:")
            for call in sorted(analysis['static_method_calls']):
                print(f"    - {call}")
        
        if analysis['constructor_calls']:
            print(f"  Constructor Calls:")
            for call in sorted(analysis['constructor_calls']):
                print(f"    - new {call}()")
        
        uacalc_deps = sorted(analysis['uacalc_dependencies'])
        print(f"  UACalc Dependencies: {len(uacalc_deps)}")
        for dep in uacalc_deps:
            print(f"    - {dep}")
    
    def determine_implementation_order(self, results: Dict) -> List[str]:
        """Determine the correct implementation order based on dependencies."""
        print("\n" + "=" * 50)
        print("IMPLEMENTATION ORDER ANALYSIS")
        print("=" * 50)
        
        # Build dependency graph
        dependencies = {}
        for class_name, analysis in results.items():
            dependencies[class_name] = analysis['uacalc_dependencies']
        
        # Topological sort to determine order
        order = []
        remaining = set(dependencies.keys())
        
        while remaining:
            # Find classes with no remaining dependencies
            ready = []
            for class_name in remaining:
                class_deps = dependencies[class_name]
                if not class_deps or all(dep not in remaining for dep in class_deps):
                    ready.append(class_name)
            
            if not ready:
                print("Warning: Circular dependencies detected!")
                break
            
            # Add ready classes to order
            ready.sort()  # For consistent ordering
            order.extend(ready)
            remaining -= set(ready)
        
        print("\nRecommended Implementation Order:")
        for i, class_name in enumerate(order, 1):
            deps = dependencies[class_name]
            dep_count = len(deps)
            print(f"{i}. {class_name} (depends on {dep_count} UACalc classes)")
            if deps:
                print(f"   Dependencies: {', '.join(sorted(deps))}")
        
        return order

def main():
    analyzer = OperationDependencyAnalyzer(".")
    results = analyzer.analyze_operation_dependencies()
    order = analyzer.determine_implementation_order(results)
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print("Based on the analysis, implement classes in this order:")
    for i, class_name in enumerate(order, 1):
        print(f"{i}. {class_name}")

if __name__ == "__main__":
    main()

