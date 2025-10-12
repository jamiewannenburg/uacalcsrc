#!/usr/bin/env python3
"""
Improved Dependency Analyzer for UACalc Java Library

This tool performs static analysis of Java source code to detect:
1. Interface implementations (implements keyword)
2. Static method calls (Class.method() calls)
3. Instance method calls
4. Constructor calls
5. Field accesses

It provides a more accurate dependency analysis than the previous tools.
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter
import sys

class ImprovedDependencyAnalyzer:
    def __init__(self, source_root: str):
        self.source_root = Path(source_root)
        self.java_files: Dict[str, Path] = {}
        self.class_info: Dict[str, Dict] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
        
    def scan_java_files(self):
        """Scan for Java source files."""
        print(f"Scanning Java files in {self.source_root}...")
        
        for java_file in self.source_root.rglob("*.java"):
            if "org/uacalc" in str(java_file):
                self.java_files[java_file.name] = java_file
        
        print(f"Found {len(self.java_files)} Java source files")
    
    def extract_class_info(self, file_path: Path) -> Optional[Dict]:
        """Extract class information from a Java file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract package
            package_match = re.search(r'package\s+([\w.]+);', content)
            package = package_match.group(1) if package_match else ""
            
            # Extract class/interface/enum name and type
            class_patterns = [
                r'public\s+(?:abstract\s+)?class\s+(\w+)',
                r'public\s+interface\s+(\w+)',
                r'public\s+enum\s+(\w+)',
                r'class\s+(\w+)',  # non-public classes
                r'interface\s+(\w+)',  # non-public interfaces
            ]
            
            class_name = None
            class_type = None
            
            for pattern in class_patterns:
                match = re.search(pattern, content)
                if match:
                    class_name = match.group(1)
                    if 'interface' in pattern:
                        class_type = 'interface'
                    elif 'enum' in pattern:
                        class_type = 'enum'
                    else:
                        class_type = 'class'
                    break
            
            if not class_name:
                return None
            
            full_class_name = f"{package}.{class_name}" if package else class_name
            
            # Extract implements clause
            implements_match = re.search(r'implements\s+([^{]+)', content)
            implements = []
            if implements_match:
                implements_str = implements_match.group(1)
                # Split by comma and clean up
                implements = [imp.strip() for imp in implements_str.split(',')]
            
            # Extract extends clause
            extends_match = re.search(r'extends\s+([^{]+)', content)
            extends = []
            if extends_match:
                extends_str = extends_match.group(1)
                extends = [ext.strip() for ext in extends_str.split(',')]
            
            # Extract method calls (both static and instance)
            method_calls = self._extract_method_calls(content)
            
            # Extract field accesses
            field_accesses = self._extract_field_accesses(content)
            
            return {
                'name': full_class_name,
                'type': class_type,
                'package': package,
                'implements': implements,
                'extends': extends,
                'method_calls': method_calls,
                'field_accesses': field_accesses,
                'file_path': str(file_path)
            }
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def _extract_method_calls(self, content: str) -> List[str]:
        """Extract method calls from Java code."""
        method_calls = []
        
        # Pattern for method calls: ClassName.methodName() or object.methodName()
        # This is a simplified pattern - in reality, Java parsing is much more complex
        method_patterns = [
            r'(\w+(?:\.\w+)*)\.(\w+)\s*\(',  # Class.method() or object.method()
            r'(\w+)\s*\.\s*(\w+)\s*\(',      # More flexible spacing
        ]
        
        for pattern in method_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                class_or_object = match.group(1)
                method_name = match.group(2)
                
                # Skip common Java keywords and primitives
                if class_or_object in ['if', 'for', 'while', 'switch', 'try', 'catch', 'finally', 'return', 'new', 'this', 'super']:
                    continue
                
                # Skip method names that are likely keywords
                if method_name in ['if', 'for', 'while', 'switch', 'try', 'catch', 'finally', 'return', 'new']:
                    continue
                
                # Try to resolve the class name
                resolved_class = self._resolve_class_name(class_or_object, content)
                if resolved_class:
                    method_calls.append(f"{resolved_class}.{method_name}")
        
        return list(set(method_calls))  # Remove duplicates
    
    def _extract_field_accesses(self, content: str) -> List[str]:
        """Extract field accesses from Java code."""
        field_accesses = []
        
        # Pattern for field access: ClassName.fieldName or object.fieldName
        field_pattern = r'(\w+(?:\.\w+)*)\.(\w+)(?!\s*\()'  # Not followed by (
        
        matches = re.finditer(field_pattern, content)
        for match in matches:
            class_or_object = match.group(1)
            field_name = match.group(2)
            
            # Skip common patterns
            if class_or_object in ['this', 'super', 'System', 'Math']:
                continue
            
            resolved_class = self._resolve_class_name(class_or_object, content)
            if resolved_class:
                field_accesses.append(f"{resolved_class}.{field_name}")
        
        return list(set(field_accesses))
    
    def _resolve_class_name(self, identifier: str, content: str) -> Optional[str]:
        """Try to resolve a class name from an identifier."""
        # If it's already a fully qualified name
        if '.' in identifier and len(identifier.split('.')) > 1:
            return identifier
        
        # Look for imports
        import_pattern = rf'import\s+([\w.]*\.)?{re.escape(identifier)}\s*;'
        import_match = re.search(import_pattern, content)
        if import_match:
            return import_match.group(1).rstrip('.') + '.' + identifier if import_match.group(1) else identifier
        
        # Check if it's a class in the same package
        package_match = re.search(r'package\s+([\w.]+);', content)
        if package_match:
            package = package_match.group(1)
            return f"{package}.{identifier}"
        
        # Check if it's a class in java.lang (implicit import)
        if identifier in ['String', 'Object', 'Integer', 'Boolean', 'Character', 'Byte', 'Short', 'Long', 'Float', 'Double']:
            return f"java.lang.{identifier}"
        
        return None
    
    def analyze_dependencies(self):
        """Analyze dependencies between classes."""
        print("Analyzing class dependencies...")
        
        # First pass: extract class information
        for file_name, file_path in self.java_files.items():
            class_info = self.extract_class_info(file_path)
            if class_info:
                self.class_info[class_info['name']] = class_info
        
        # Second pass: build dependency graph
        for class_name, info in self.class_info.items():
            dependencies = set()
            
            # Add interface implementations
            for interface in info['implements']:
                if interface in self.class_info:
                    dependencies.add(interface)
                    self.reverse_dependencies[interface].add(class_name)
            
            # Add class extensions
            for parent in info['extends']:
                if parent in self.class_info:
                    dependencies.add(parent)
                    self.reverse_dependencies[parent].add(class_name)
            
            # Add method call dependencies
            for method_call in info['method_calls']:
                # Extract class name from method call
                if '.' in method_call:
                    called_class = method_call.rsplit('.', 1)[0]
                    if called_class in self.class_info:
                        dependencies.add(called_class)
                        self.reverse_dependencies[called_class].add(class_name)
            
            # Add field access dependencies
            for field_access in info['field_accesses']:
                if '.' in field_access:
                    accessed_class = field_access.rsplit('.', 1)[0]
                    if accessed_class in self.class_info:
                        dependencies.add(accessed_class)
                        self.reverse_dependencies[accessed_class].add(class_name)
            
            self.dependencies[class_name] = dependencies
        
        print(f"Analyzed dependencies for {len(self.class_info)} classes")
    
    def get_dependency_levels(self) -> Dict[int, List[str]]:
        """Get classes organized by dependency level (0 = no dependencies, higher = more dependencies)."""
        levels = defaultdict(list)
        
        # Calculate dependency counts
        dep_counts = {}
        for class_name in self.class_info.keys():
            # Count only UACalc dependencies (exclude java.*, etc.)
            uacalc_deps = [dep for dep in self.dependencies[class_name] if 'org.uacalc' in dep]
            dep_counts[class_name] = len(uacalc_deps)
        
        # Group by dependency count
        for class_name, count in dep_counts.items():
            levels[count].append(class_name)
        
        return dict(levels)
    
    def generate_report(self, output_dir: str = "improved_dependency_analysis"):
        """Generate comprehensive dependency analysis report."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate JSON report
        report = {
            "class_info": self.class_info,
            "dependencies": {cls: list(deps) for cls, deps in self.dependencies.items()},
            "reverse_dependencies": {cls: list(deps) for cls, deps in self.reverse_dependencies.items()},
            "dependency_levels": self.get_dependency_levels(),
            "statistics": {
                "total_classes": len(self.class_info),
                "total_dependencies": sum(len(deps) for deps in self.dependencies.values()),
                "classes_with_no_dependencies": len([cls for cls, deps in self.dependencies.items() if not any('org.uacalc' in dep for dep in deps)])
            }
        }
        
        json_file = output_path / "improved_dependencies.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate text summary
        self._generate_text_summary(output_path / "improved_dependencies_summary.txt")
        
        # Generate Mermaid diagram
        self._generate_mermaid_diagram(output_path / "improved_dependencies.mmd")
        
        print(f"Analysis complete! Reports written to {output_path}")
        return output_path
    
    def _generate_text_summary(self, output_file: Path):
        """Generate human-readable text summary."""
        with open(output_file, 'w') as f:
            f.write("UACalc Improved Dependency Analysis\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Total Classes: {len(self.class_info)}\n")
            f.write(f"Total Dependencies: {sum(len(deps) for deps in self.dependencies.values())}\n\n")
            
            # Show classes by dependency level
            levels = self.get_dependency_levels()
            f.write("Classes by Dependency Level:\n")
            f.write("-" * 30 + "\n")
            
            for level in sorted(levels.keys()):
                classes = levels[level]
                f.write(f"\nLevel {level} ({len(classes)} classes):\n")
                for class_name in sorted(classes):
                    f.write(f"  - {class_name}\n")
            
            # Show specific analysis for operation classes
            f.write("\n\nOperation Classes Analysis:\n")
            f.write("-" * 30 + "\n")
            
            operation_classes = ['org.uacalc.alg.op.Operation', 'org.uacalc.alg.op.AbstractOperation', 
                               'org.uacalc.alg.op.Operations', 'org.uacalc.util.SequenceGenerator']
            
            for class_name in operation_classes:
                if class_name in self.class_info:
                    info = self.class_info[class_name]
                    f.write(f"\n{class_name}:\n")
                    f.write(f"  Type: {info['type']}\n")
                    if info['implements']:
                        f.write(f"  Implements: {', '.join(info['implements'])}\n")
                    if info['extends']:
                        f.write(f"  Extends: {', '.join(info['extends'])}\n")
                    
                    uacalc_deps = [dep for dep in self.dependencies[class_name] if 'org.uacalc' in dep]
                    f.write(f"  UACalc Dependencies: {len(uacalc_deps)}\n")
                    for dep in sorted(uacalc_deps):
                        f.write(f"    - {dep}\n")
    
    def _generate_mermaid_diagram(self, output_file: Path):
        """Generate Mermaid diagram of dependencies."""
        with open(output_file, 'w') as f:
            f.write("graph TD\n")
            
            # Add nodes for classes with dependencies
            for class_name, deps in self.dependencies.items():
                if any('org.uacalc' in dep for dep in deps):
                    node_id = class_name.replace('.', '_').replace('$', '_')
                    short_name = class_name.split('.')[-1]
                    f.write(f'    {node_id}["{short_name}"]\n')
            
            # Add edges for dependencies
            for class_name, deps in self.dependencies.items():
                if any('org.uacalc' in dep for dep in deps):
                    from_id = class_name.replace('.', '_').replace('$', '_')
                    for dep in deps:
                        if 'org.uacalc' in dep:
                            to_id = dep.replace('.', '_').replace('$', '_')
                            f.write(f'    {from_id} --> {to_id}\n')

def main():
    parser = argparse.ArgumentParser(description="Improved dependency analysis for UACalc Java library")
    parser.add_argument("--source", default=".", 
                       help="Source directory containing Java files (default: current directory)")
    parser.add_argument("--output", default="improved_dependency_analysis",
                       help="Output directory for analysis results (default: improved_dependency_analysis)")
    
    args = parser.parse_args()
    
    analyzer = ImprovedDependencyAnalyzer(args.source)
    analyzer.scan_java_files()
    analyzer.analyze_dependencies()
    output_path = analyzer.generate_report(args.output)
    
    # Print summary to console
    print("\n" + "="*60)
    print("IMPROVED DEPENDENCY ANALYSIS SUMMARY:")
    print("="*60)
    
    levels = analyzer.get_dependency_levels()
    for level in sorted(levels.keys()):
        classes = levels[level]
        print(f"\nLevel {level} ({len(classes)} classes):")
        for class_name in sorted(classes):
            print(f"  - {class_name}")
    
    # Show specific analysis for operation classes
    print("\n\nOperation Classes Analysis:")
    print("-" * 30)
    
    operation_classes = ['org.uacalc.alg.op.Operation', 'org.uacalc.alg.op.AbstractOperation', 
                       'org.uacalc.alg.op.Operations', 'org.uacalc.util.SequenceGenerator']
    
    for class_name in operation_classes:
        if class_name in analyzer.class_info:
            info = analyzer.class_info[class_name]
            uacalc_deps = [dep for dep in analyzer.dependencies[class_name] if 'org.uacalc' in dep]
            print(f"\n{class_name}:")
            print(f"  Type: {info['type']}")
            if info['implements']:
                print(f"  Implements: {', '.join(info['implements'])}")
            if info['extends']:
                print(f"  Extends: {', '.join(info['extends'])}")
            print(f"  UACalc Dependencies: {len(uacalc_deps)}")
            for dep in sorted(uacalc_deps):
                print(f"    - {dep}")

if __name__ == "__main__":
    main()
