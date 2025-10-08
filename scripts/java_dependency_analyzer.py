#!/usr/bin/env python3
"""
Java Dependency Graph Generator for UACalc Library

This tool analyzes Java source files in the org.uacalc package and generates
dependency graphs showing the relationships between classes and packages.
The output is designed to be LLM-friendly for understanding project structure.

Usage:
    python java_dependency_analyzer.py [options]

Output formats:
    - Mermaid diagrams (for LLM consumption)
    - Graphviz DOT files (for visualization)
    - JSON dependency data
    - Text summaries
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter
import sys

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("Warning: NetworkX not available. Install with 'pip install networkx' for enhanced graph analysis.")

class JavaDependencyAnalyzer:
    def __init__(self, source_root: str):
        self.source_root = Path(source_root)
        self.java_files: Dict[str, Path] = {}
        self.packages: Set[str] = set()
        self.classes: Set[str] = set()
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.package_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.class_to_package: Dict[str, str] = {}
        self.package_structure: Dict[str, List[str]] = defaultdict(list)
        
        # NetworkX graphs for advanced analysis
        if NETWORKX_AVAILABLE:
            self.package_graph = nx.DiGraph()
            self.class_graph = nx.DiGraph()
        else:
            self.package_graph = None
            self.class_graph = None
        
    def scan_java_files(self):
        """Scan for all Java files in the source directory."""
        print(f"Scanning Java files in {self.source_root}...")
        
        for java_file in self.source_root.rglob("*.java"):
            if "org/uacalc" in str(java_file):
                self.java_files[java_file.name] = java_file
                
        print(f"Found {len(self.java_files)} Java files")
        
    def parse_java_file(self, file_path: Path) -> Tuple[str, str, Set[str]]:
        """Parse a Java file to extract package, class name, and imports."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None, None, set()
            
        # Extract package declaration
        package_match = re.search(r'package\s+([\w.]+);', content)
        package_name = package_match.group(1) if package_match else "unknown"
        
        # Extract class name (first public class/interface)
        class_match = re.search(r'public\s+(?:class|interface|enum)\s+(\w+)', content)
        class_name = class_match.group(1) if class_match else file_path.stem
        
        # Extract imports
        imports = set()
        import_pattern = r'import\s+([\w.]+)(?:\.\*)?;'
        for match in re.finditer(import_pattern, content):
            import_name = match.group(1)
            # Only include org.uacalc imports for internal dependencies
            if import_name.startswith('org.uacalc'):
                imports.add(import_name)
                
        return package_name, class_name, imports
        
    def analyze_dependencies(self):
        """Analyze all Java files and build dependency graph."""
        print("Analyzing dependencies...")
        
        for file_name, file_path in self.java_files.items():
            package, class_name, imports = self.parse_java_file(file_path)
            
            if package is None:
                continue
                
            full_class_name = f"{package}.{class_name}"
            
            # Store package and class information
            self.packages.add(package)
            self.classes.add(full_class_name)
            self.class_to_package[full_class_name] = package
            self.package_structure[package].append(class_name)
            
            # Process imports
            for import_name in imports:
                # Handle wildcard imports
                if import_name.endswith('.*'):
                    base_package = import_name[:-2]
                    self.package_dependencies[package].add(base_package)
                else:
                    # Specific class import
                    self.dependencies[full_class_name].add(import_name)
                    # Also add package dependency
                    import_package = '.'.join(import_name.split('.')[:-1])
                    if import_package:
                        self.package_dependencies[package].add(import_package)
                        
        print(f"Found {len(self.packages)} packages and {len(self.classes)} classes")
        
        # Build NetworkX graphs if available
        if NETWORKX_AVAILABLE:
            self._build_networkx_graphs()
    
    def _build_networkx_graphs(self):
        """Build NetworkX graphs for advanced analysis."""
        if not NETWORKX_AVAILABLE:
            return
            
        # Build package graph
        for package in self.packages:
            self.package_graph.add_node(package, type='package')
            
        for package, deps in self.package_dependencies.items():
            for dep in deps:
                if dep in self.packages:
                    self.package_graph.add_edge(package, dep)
                    
        # Build class graph
        for class_name in self.classes:
            package = self.class_to_package.get(class_name, 'unknown')
            self.class_graph.add_node(class_name, package=package, type='class')
            
        for class_name, deps in self.dependencies.items():
            for dep in deps:
                if dep in self.classes:
                    self.class_graph.add_edge(class_name, dep)
    
    def get_graph_statistics(self) -> Dict:
        """Get comprehensive graph statistics using NetworkX."""
        if not NETWORKX_AVAILABLE or not self.package_graph:
            return {"error": "NetworkX not available"}
            
        stats = {
            "package_graph": {
                "nodes": self.package_graph.number_of_nodes(),
                "edges": self.package_graph.number_of_edges(),
                "density": nx.density(self.package_graph),
                "is_weakly_connected": nx.is_weakly_connected(self.package_graph),
                "is_strongly_connected": nx.is_strongly_connected(self.package_graph),
                "strongly_connected_components": len(list(nx.strongly_connected_components(self.package_graph))),
                "weakly_connected_components": len(list(nx.weakly_connected_components(self.package_graph))),
            },
            "class_graph": {
                "nodes": self.class_graph.number_of_nodes(),
                "edges": self.class_graph.number_of_edges(),
                "density": nx.density(self.class_graph),
                "is_weakly_connected": nx.is_weakly_connected(self.class_graph),
                "is_strongly_connected": nx.is_strongly_connected(self.class_graph),
                "strongly_connected_components": len(list(nx.strongly_connected_components(self.class_graph))),
                "weakly_connected_components": len(list(nx.weakly_connected_components(self.class_graph))),
            }
        }
        
        # Add centrality measures for packages
        if self.package_graph.number_of_nodes() > 0:
            try:
                stats["package_graph"]["betweenness_centrality"] = dict(nx.betweenness_centrality(self.package_graph))
                stats["package_graph"]["in_degree_centrality"] = dict(nx.in_degree_centrality(self.package_graph))
                stats["package_graph"]["out_degree_centrality"] = dict(nx.out_degree_centrality(self.package_graph))
                stats["package_graph"]["pagerank"] = dict(nx.pagerank(self.package_graph))
            except Exception as e:
                stats["package_graph"]["centrality_error"] = str(e)
                
        return stats
    
    def find_most_central_packages(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """Find the most central packages using NetworkX centrality measures."""
        if not NETWORKX_AVAILABLE or not self.package_graph:
            return []
            
        try:
            # Use PageRank to find most important packages
            pagerank = nx.pagerank(self.package_graph)
            return sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:top_n]
        except Exception:
            return []
    
    def find_cycles(self) -> List[List[str]]:
        """Find cycles in the dependency graph."""
        if not NETWORKX_AVAILABLE or not self.package_graph:
            return []
            
        try:
            return list(nx.simple_cycles(self.package_graph))
        except Exception:
            return []
    
    def find_longest_paths(self, top_n: int = 5) -> List[List[str]]:
        """Find the longest dependency paths."""
        if not NETWORKX_AVAILABLE or not self.package_graph:
            return []
            
        try:
            # Find all simple paths and return the longest ones
            all_paths = []
            for source in self.package_graph.nodes():
                for target in self.package_graph.nodes():
                    if source != target:
                        try:
                            paths = list(nx.all_simple_paths(self.package_graph, source, target, cutoff=10))
                            all_paths.extend(paths)
                        except nx.NetworkXNoPath:
                            continue
                            
            return sorted(all_paths, key=len, reverse=True)[:top_n]
        except Exception:
            return []
    
    def get_files_by_dependency_count(self, include_packages: bool = True, include_classes: bool = True) -> List[Tuple[str, int, str]]:
        """
        Return a list of files/packages/classes ordered from least dependencies (leaves) to most dependencies (roots).
        
        Args:
            include_packages: Whether to include package-level analysis
            include_classes: Whether to include class-level analysis
            
        Returns:
            List of tuples: (name, dependency_count, type) where type is 'package' or 'class'
            Ordered from least dependencies to most dependencies
        """
        results = []
        
        if include_packages:
            # Analyze package dependencies
            for package in self.packages:
                # Count outgoing dependencies (what this package depends on)
                outgoing_deps = len(self.package_dependencies.get(package, set()))
                # Count incoming dependencies (what depends on this package)
                incoming_deps = sum(1 for pkg, deps in self.package_dependencies.items() 
                                  if package in deps)
                # Total dependencies (both directions)
                total_deps = outgoing_deps + incoming_deps
                results.append((package, total_deps, 'package'))
        
        if include_classes:
            # Analyze class dependencies
            for class_name in self.classes:
                # Count outgoing dependencies (what this class depends on)
                outgoing_deps = len(self.dependencies.get(class_name, set()))
                # Count incoming dependencies (what depends on this class)
                incoming_deps = sum(1 for cls, deps in self.dependencies.items() 
                                  if class_name in deps)
                # Total dependencies (both directions)
                total_deps = outgoing_deps + incoming_deps
                results.append((class_name, total_deps, 'class'))
        
        # Sort by dependency count (ascending - leaves first)
        return sorted(results, key=lambda x: x[1])
    
    def get_dependency_hierarchy(self) -> Dict[str, List[str]]:
        """
        Get a hierarchical view of dependencies organized by dependency levels.
        
        Returns:
            Dictionary with levels as keys and lists of items at that level as values.
            Level 0 = leaves (no dependencies), higher levels = more dependencies.
        """
        hierarchy = {}
        
        # Get all items with their dependency counts
        items_with_counts = self.get_files_by_dependency_count()
        
        # Group by dependency count
        for name, count, item_type in items_with_counts:
            level = count
            if level not in hierarchy:
                hierarchy[level] = []
            hierarchy[level].append((name, item_type))
        
        # Sort items within each level alphabetically
        for level in hierarchy:
            hierarchy[level].sort(key=lambda x: x[0])
        
        return hierarchy
    
    def get_leaf_packages(self) -> List[str]:
        """Get packages that have no outgoing dependencies (true leaves)."""
        leaves = []
        for package in self.packages:
            if not self.package_dependencies.get(package, set()):
                leaves.append(package)
        return sorted(leaves)
    
    def get_root_packages(self) -> List[str]:
        """Get packages that nothing depends on (true roots)."""
        roots = []
        all_dependents = set()
        for deps in self.package_dependencies.values():
            all_dependents.update(deps)
        
        for package in self.packages:
            if package not in all_dependents:
                roots.append(package)
        return sorted(roots)
    
    def get_leaf_classes(self) -> List[str]:
        """Get classes that have no outgoing dependencies (true leaves)."""
        leaves = []
        for class_name in self.classes:
            if not self.dependencies.get(class_name, set()):
                leaves.append(class_name)
        return sorted(leaves)
    
    def get_root_classes(self) -> List[str]:
        """Get classes that nothing depends on (true roots)."""
        roots = []
        all_dependents = set()
        for deps in self.dependencies.values():
            all_dependents.update(deps)
        
        for class_name in self.classes:
            if class_name not in all_dependents:
                roots.append(class_name)
        return sorted(roots)
        
    def generate_mermaid_diagram(self, output_file: Optional[str] = None) -> str:
        """Generate a Mermaid diagram of the dependency graph."""
        mermaid_lines = ["graph TD"]
        
        # Add package nodes
        for package in sorted(self.packages):
            package_id = package.replace('.', '_')
            mermaid_lines.append(f'    {package_id}["{package}"]')
            
        # Add package dependencies
        for package, deps in self.package_dependencies.items():
            package_id = package.replace('.', '_')
            for dep in deps:
                if dep in self.packages:  # Only internal dependencies
                    dep_id = dep.replace('.', '_')
                    mermaid_lines.append(f'    {package_id} --> {dep_id}')
                    
        mermaid_content = '\n'.join(mermaid_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(mermaid_content)
            print(f"Mermaid diagram written to {output_file}")
            
        return mermaid_content
    
    def generate_hierarchy_mermaid(self, output_file: Optional[str] = None) -> str:
        """Generate a Mermaid diagram showing the dependency hierarchy."""
        mermaid_lines = ["graph TD"]
        
        # Get dependency hierarchy
        hierarchy = self.get_dependency_hierarchy()
        
        # Add nodes grouped by dependency level
        for level in sorted(hierarchy.keys()):
            items = hierarchy[level]
            for name, item_type in items:
                node_id = name.replace('.', '_')
                short_name = name.split('.')[-1]
                color = "lightgreen" if item_type == "package" else "lightblue"
                mermaid_lines.append(f'    {node_id}["{short_name}"]')
                mermaid_lines.append(f'    classDef level{level} fill:{color}')
                mermaid_lines.append(f'    class {node_id} level{level}')
        
        # Add dependencies
        for package, deps in self.package_dependencies.items():
            package_id = package.replace('.', '_')
            for dep in deps:
                if dep in self.packages:
                    dep_id = dep.replace('.', '_')
                    mermaid_lines.append(f'    {package_id} --> {dep_id}')
        
        mermaid_content = '\n'.join(mermaid_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(mermaid_content)
            print(f"Hierarchy Mermaid diagram written to {output_file}")
            
        return mermaid_content
        
    def generate_detailed_mermaid(self, output_file: Optional[str] = None) -> str:
        """Generate a detailed Mermaid diagram showing key classes."""
        mermaid_lines = ["graph TD"]
        
        # Identify key classes (interfaces, main classes)
        key_classes = set()
        for file_name, file_path in self.java_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Look for interfaces and main classes
                if ('public interface' in content or 
                    'public class' in content and 'extends' in content or
                    'public class' in content and 'implements' in content):
                    
                    package, class_name, _ = self.parse_java_file(file_path)
                    if package:
                        full_name = f"{package}.{class_name}"
                        key_classes.add(full_name)
                        
            except Exception:
                continue
                
        # Add key class nodes
        for class_name in sorted(key_classes):
            class_id = class_name.replace('.', '_')
            short_name = class_name.split('.')[-1]
            mermaid_lines.append(f'    {class_id}["{short_name}"]')
            
        # Add class dependencies (simplified)
        for class_name, deps in self.dependencies.items():
            if class_name in key_classes:
                class_id = class_name.replace('.', '_')
                for dep in deps:
                    if dep in key_classes:
                        dep_id = dep.replace('.', '_')
                        mermaid_lines.append(f'    {class_id} --> {dep_id}')
                        
        mermaid_content = '\n'.join(mermaid_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(mermaid_content)
            print(f"Detailed Mermaid diagram written to {output_file}")
            
        return mermaid_content
        
    def generate_graphviz_dot(self, output_file: str):
        """Generate a Graphviz DOT file for visualization."""
        with open(output_file, 'w') as f:
            f.write("digraph UACalcDependencies {\n")
            f.write("    rankdir=TB;\n")
            f.write("    node [shape=box, style=filled, fillcolor=lightblue];\n")
            f.write("    edge [color=gray];\n\n")
            
            # Add package nodes
            for package in sorted(self.packages):
                package_id = package.replace('.', '_')
                f.write(f'    {package_id} [label="{package}"];\n')
                
            f.write("\n")
            
            # Add package dependencies
            for package, deps in self.package_dependencies.items():
                package_id = package.replace('.', '_')
                for dep in deps:
                    if dep in self.packages:
                        dep_id = dep.replace('.', '_')
                        f.write(f'    {package_id} -> {dep_id};\n')
                        
            f.write("}\n")
            
        print(f"Graphviz DOT file written to {output_file}")
        
    def generate_json_report(self, output_file: str):
        """Generate a JSON report of all dependencies."""
        report = {
            "packages": sorted(list(self.packages)),
            "classes": sorted(list(self.classes)),
            "package_dependencies": {pkg: sorted(list(deps)) 
                                   for pkg, deps in self.package_dependencies.items()},
            "class_dependencies": {cls: sorted(list(deps)) 
                                 for cls, deps in self.dependencies.items()},
            "package_structure": {pkg: sorted(classes) 
                                for pkg, classes in self.package_structure.items()},
            "statistics": {
                "total_packages": len(self.packages),
                "total_classes": len(self.classes),
                "total_dependencies": sum(len(deps) for deps in self.dependencies.values())
            }
        }
        
        # Add NetworkX analysis if available
        if NETWORKX_AVAILABLE:
            report["networkx_analysis"] = {
                "graph_statistics": self.get_graph_statistics(),
                "most_central_packages": self.find_most_central_packages(),
                "cycles": self.find_cycles(),
                "longest_paths": self.find_longest_paths()
            }
        
        # Add dependency hierarchy analysis
        report["dependency_hierarchy"] = {
            "files_by_dependency_count": self.get_files_by_dependency_count(),
            "dependency_levels": self.get_dependency_hierarchy(),
            "leaf_packages": self.get_leaf_packages(),
            "root_packages": self.get_root_packages(),
            "leaf_classes": self.get_leaf_classes(),
            "root_classes": self.get_root_classes()
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"JSON report written to {output_file}")
        
    def generate_text_summary(self, output_file: str):
        """Generate a human-readable text summary."""
        with open(output_file, 'w') as f:
            f.write("UACalc Java Library Dependency Analysis\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Total Packages: {len(self.packages)}\n")
            f.write(f"Total Classes: {len(self.classes)}\n")
            f.write(f"Total Dependencies: {sum(len(deps) for deps in self.dependencies.values())}\n\n")
            
            f.write("Package Structure:\n")
            f.write("-" * 20 + "\n")
            for package in sorted(self.packages):
                classes = self.package_structure[package]
                f.write(f"{package} ({len(classes)} classes)\n")
                for cls in sorted(classes):
                    f.write(f"  - {cls}\n")
                f.write("\n")
                
            f.write("Package Dependencies:\n")
            f.write("-" * 20 + "\n")
            for package in sorted(self.packages):
                deps = self.package_dependencies[package]
                if deps:
                    f.write(f"{package} depends on:\n")
                    for dep in sorted(deps):
                        f.write(f"  - {dep}\n")
                    f.write("\n")
                    
            # Find most connected packages
            f.write("Most Connected Packages:\n")
            f.write("-" * 25 + "\n")
            package_connections = Counter()
            for package, deps in self.package_dependencies.items():
                package_connections[package] += len(deps)
            for package, count in package_connections.most_common(10):
                f.write(f"{package}: {count} dependencies\n")
                
            # Add NetworkX analysis if available
            if NETWORKX_AVAILABLE:
                f.write("\nNetworkX Graph Analysis:\n")
                f.write("-" * 25 + "\n")
                
                stats = self.get_graph_statistics()
                if "error" not in stats:
                    pkg_stats = stats["package_graph"]
                    f.write(f"Package Graph Density: {pkg_stats['density']:.3f}\n")
                    f.write(f"Strongly Connected Components: {pkg_stats['strongly_connected_components']}\n")
                    f.write(f"Weakly Connected Components: {pkg_stats['weakly_connected_components']}\n")
                    
                    # Most central packages
                    central_packages = self.find_most_central_packages(5)
                    if central_packages:
                        f.write("\nMost Central Packages (PageRank):\n")
                        for package, score in central_packages:
                            f.write(f"  {package}: {score:.3f}\n")
                    
                    # Cycles
                    cycles = self.find_cycles()
                    if cycles:
                        f.write(f"\nCycles Found: {len(cycles)}\n")
                        for i, cycle in enumerate(cycles[:3]):  # Show first 3 cycles
                            f.write(f"  Cycle {i+1}: {' -> '.join(cycle)} -> {cycle[0]}\n")
                    else:
                        f.write("\nNo cycles found in package dependencies.\n")
                        
                    # Longest paths
                    longest_paths = self.find_longest_paths(3)
                    if longest_paths:
                        f.write("\nLongest Dependency Paths:\n")
                        for i, path in enumerate(longest_paths):
                            f.write(f"  Path {i+1} (length {len(path)}): {' -> '.join(path)}\n")
                else:
                    f.write("NetworkX analysis not available.\n")
            
            # Add dependency hierarchy analysis
            f.write("\nDependency Hierarchy Analysis:\n")
            f.write("-" * 30 + "\n")
            
            # Show files ordered by dependency count
            files_by_deps = self.get_files_by_dependency_count()
            f.write("Files ordered by dependency count (leaves to roots):\n")
            f.write("(Format: name, dependency_count, type)\n\n")
            
            # Group by dependency count for better readability
            current_count = -1
            for name, count, item_type in files_by_deps:
                if count != current_count:
                    current_count = count
                    f.write(f"\nDependency Count {count}:\n")
                f.write(f"  {name} ({item_type})\n")
            
            # Show leaf and root analysis
            f.write("\nLeaf Analysis (no outgoing dependencies):\n")
            leaf_packages = self.get_leaf_packages()
            leaf_classes = self.get_leaf_classes()
            f.write(f"  Leaf Packages ({len(leaf_packages)}): {', '.join(leaf_packages)}\n")
            f.write(f"  Leaf Classes ({len(leaf_classes)}): {', '.join(leaf_classes[:10])}")
            if len(leaf_classes) > 10:
                f.write(f" ... and {len(leaf_classes) - 10} more")
            f.write("\n")
            
            f.write("\nRoot Analysis (nothing depends on them):\n")
            root_packages = self.get_root_packages()
            root_classes = self.get_root_classes()
            f.write(f"  Root Packages ({len(root_packages)}): {', '.join(root_packages)}\n")
            f.write(f"  Root Classes ({len(root_classes)}): {', '.join(root_classes[:10])}")
            if len(root_classes) > 10:
                f.write(f" ... and {len(root_classes) - 10} more")
            f.write("\n")
                
        print(f"Text summary written to {output_file}")
    
    def generate_networkx_visualization(self, output_file: str):
        """Generate a NetworkX-based visualization (if matplotlib is available)."""
        if not NETWORKX_AVAILABLE or not self.package_graph:
            print("NetworkX not available for visualization")
            return
            
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            
            # Create figure
            plt.figure(figsize=(16, 12))
            
            # Use spring layout for better visualization
            pos = nx.spring_layout(self.package_graph, k=3, iterations=50)
            
            # Draw nodes with different colors based on centrality
            pagerank = nx.pagerank(self.package_graph)
            node_colors = [pagerank.get(node, 0) for node in self.package_graph.nodes()]
            
            # Draw the graph
            nx.draw_networkx_nodes(self.package_graph, pos, 
                                 node_color=node_colors, 
                                 node_size=1000,
                                 cmap=plt.cm.Reds,
                                 alpha=0.8)
            
            nx.draw_networkx_edges(self.package_graph, pos, 
                                 edge_color='gray', 
                                 arrows=True, 
                                 arrowsize=20,
                                 alpha=0.6)
            
            # Add labels
            labels = {node: node.split('.')[-1] for node in self.package_graph.nodes()}
            nx.draw_networkx_labels(self.package_graph, pos, labels, font_size=8)
            
            plt.title("UACalc Package Dependencies (NetworkX Visualization)\nNode size and color indicate PageRank centrality", 
                     fontsize=14, pad=20)
            plt.axis('off')
            
            # Add colorbar
            if len(node_colors) > 0 and min(node_colors) != max(node_colors):
                sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, 
                                         norm=plt.Normalize(vmin=min(node_colors), vmax=max(node_colors)))
                sm.set_array([])
                cbar = plt.colorbar(sm, shrink=0.8, ax=plt.gca())
                cbar.set_label('PageRank Centrality', rotation=270, labelpad=20)
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"NetworkX visualization written to {output_file}")
            
        except ImportError:
            print("Matplotlib not available for NetworkX visualization")
        except Exception as e:
            print(f"Error generating NetworkX visualization: {e}")
        
    def run_analysis(self, output_dir: str = "dependency_analysis"):
        """Run the complete analysis and generate all outputs."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print("Starting Java dependency analysis...")
        self.scan_java_files()
        self.analyze_dependencies()
        
        # Generate all output formats
        self.generate_mermaid_diagram(output_path / "package_dependencies.mmd")
        self.generate_detailed_mermaid(output_path / "class_dependencies.mmd")
        self.generate_hierarchy_mermaid(output_path / "dependency_hierarchy.mmd")
        self.generate_graphviz_dot(output_path / "dependencies.dot")
        self.generate_json_report(output_path / "dependencies.json")
        self.generate_text_summary(output_path / "summary.txt")
        
        # Generate NetworkX visualization if available
        if NETWORKX_AVAILABLE:
            self.generate_networkx_visualization(output_path / "networkx_visualization.png")
        
        print(f"\nAnalysis complete! Output files written to {output_path}")
        print("\nGenerated files:")
        print("- package_dependencies.mmd: Mermaid diagram of package dependencies")
        print("- class_dependencies.mmd: Mermaid diagram of key class dependencies")
        print("- dependency_hierarchy.mmd: Mermaid diagram showing dependency hierarchy")
        print("- dependencies.dot: Graphviz DOT file for visualization")
        print("- dependencies.json: Complete dependency data in JSON format")
        print("- summary.txt: Human-readable summary")
        if NETWORKX_AVAILABLE:
            print("- networkx_visualization.png: NetworkX-based graph visualization")
            print("- Enhanced analysis with centrality measures, cycle detection, and path analysis")
        print("- Dependency hierarchy analysis: files ordered from leaves to roots")
        
        return output_path

def main():
    parser = argparse.ArgumentParser(description="Analyze Java dependencies in UACalc library")
    parser.add_argument("--source", default=".", 
                       help="Source directory containing Java files (default: current directory)")
    parser.add_argument("--output", default="dependency_analysis",
                       help="Output directory for analysis results (default: dependency_analysis)")
    parser.add_argument("--format", choices=["all", "mermaid", "dot", "json", "text"], 
                       default="all", help="Output format (default: all)")
    
    args = parser.parse_args()
    
    analyzer = JavaDependencyAnalyzer(args.source)
    output_path = analyzer.run_analysis(args.output)
    
    # Print Mermaid diagram to console for easy copying
    print("\n" + "="*60)
    print("MERMAID DIAGRAM (Package Dependencies):")
    print("="*60)
    print(analyzer.generate_mermaid_diagram())
    
    print("\n" + "="*60)
    print("MERMAID DIAGRAM (Key Class Dependencies):")
    print("="*60)
    print(analyzer.generate_detailed_mermaid())
    
    print("\n" + "="*60)
    print("DEPENDENCY HIERARCHY (Files ordered from leaves to roots):")
    print("="*60)
    files_by_deps = analyzer.get_files_by_dependency_count()
    print("Top 20 files with least dependencies (leaves):")
    for i, (name, count, item_type) in enumerate(files_by_deps[:20]):
        print(f"{i+1:2d}. {name} ({count} deps, {item_type})")
    
    print(f"\nBottom 10 files with most dependencies (roots):")
    for i, (name, count, item_type) in enumerate(files_by_deps[-10:]):
        print(f"{len(files_by_deps)-9+i:2d}. {name} ({count} deps, {item_type})")
    
    print(f"\nLeaf Analysis:")
    leaf_packages = analyzer.get_leaf_packages()
    leaf_classes = analyzer.get_leaf_classes()
    print(f"  Leaf Packages ({len(leaf_packages)}): {', '.join(leaf_packages[:5])}")
    if len(leaf_packages) > 5:
        print(f"    ... and {len(leaf_packages) - 5} more")
    print(f"  Leaf Classes ({len(leaf_classes)}): {', '.join(leaf_classes[:5])}")
    if len(leaf_classes) > 5:
        print(f"    ... and {len(leaf_classes) - 5} more")

if __name__ == "__main__":
    main()
