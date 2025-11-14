#!/usr/bin/env python3
"""
Java Call Graph Analyzer for UACalc Library

This tool uses off-the-shelf Java call graph analysis tools to generate
fine-grained method-level dependency graphs. It integrates with java-callgraph
and other static analysis tools to provide detailed call graph analysis.

Usage:
    python java_call_graph_analyzer.py [options]

Dependencies:
    - java-callgraph (https://github.com/gousiosg/java-callgraph)
    - Java 8+ runtime
    - Maven or Gradle (for building java-callgraph)
"""

import os
import re
import json
import argparse
import subprocess
import tempfile
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

class JavaCallGraphAnalyzer:
    def __init__(self, source_root: str):
        self.source_root = Path(source_root)
        self.java_files: Dict[str, Path] = {}
        self.class_files: Dict[str, Path] = {}
        self.call_graph_data: List[Tuple[str, str]] = []
        self.method_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.class_methods: Dict[str, Set[str]] = defaultdict(set)
        self.method_to_class: Dict[str, str] = {}
        
        # NetworkX graph for call graph analysis
        if NETWORKX_AVAILABLE:
            self.call_graph = nx.DiGraph()
        else:
            self.call_graph = None
    
    def check_dependencies(self) -> bool:
        """Check if required tools are available."""
        print("Checking dependencies...")
        
        # Check Java
        try:
            result = subprocess.run(['java', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✓ Java runtime found")
            else:
                print("✗ Java runtime not found")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("✗ Java runtime not found")
            return False
        
        # Check if java-callgraph is available
        java_callgraph_path = self._find_java_callgraph()
        if java_callgraph_path:
            print(f"✓ java-callgraph found at {java_callgraph_path}")
            self.java_callgraph_path = java_callgraph_path
            return True
        else:
            print("✗ java-callgraph not found")
            print("Please install java-callgraph:")
            print("  git clone https://github.com/gousiosg/java-callgraph.git")
            print("  cd java-callgraph && mvn compile")
            return False
    
    def _find_java_callgraph(self) -> Optional[str]:
        """Find java-callgraph installation."""
        # First check project-local installation (preferred)
        project_paths = [
            Path("tools/callgraph/java-callgraph"),
            Path("callgraph/java-callgraph"),
            Path("java-callgraph")
        ]
        
        for path in project_paths:
            jar_path = path / "target" / "javacg-0.1-SNAPSHOT-static.jar"
            if jar_path.exists():
                return str(jar_path)
        
        # Fallback to system-wide installations
        system_paths = [
            Path.home() / "java-callgraph",
            Path.home() / "tools" / "java-callgraph",
            Path("/opt") / "java-callgraph",
            Path("/usr/local") / "java-callgraph"
        ]
        
        for path in system_paths:
            jar_path = path / "target" / "javacg-0.1-SNAPSHOT-static.jar"
            if jar_path.exists():
                return str(jar_path)
        
        return None
    
    def scan_java_files(self):
        """Scan for Java source files and compiled class files."""
        print(f"Scanning Java files in {self.source_root}...")
        
        # Find Java source files
        for java_file in self.source_root.rglob("*.java"):
            if "org/uacalc" in str(java_file):
                self.java_files[java_file.name] = java_file
        
        # Find compiled class files
        for class_file in self.source_root.rglob("*.class"):
            if "org/uacalc" in str(class_file):
                self.class_files[class_file.name] = class_file
        
        print(f"Found {len(self.java_files)} Java source files")
        print(f"Found {len(self.class_files)} compiled class files")
    
    def extract_methods_from_source(self) -> Dict[str, List[str]]:
        """Extract method signatures from Java source files."""
        methods_by_class = defaultdict(list)
        
        for file_name, file_path in self.java_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract package
                package_match = re.search(r'package\s+([\w.]+);', content)
                package = package_match.group(1) if package_match else ""
                
                # Extract class name
                class_match = re.search(r'public\s+(?:class|interface|enum)\s+(\w+)', content)
                if not class_match:
                    continue
                class_name = class_match.group(1)
                full_class_name = f"{package}.{class_name}" if package else class_name
                
                # Extract method signatures
                method_pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w\s,]+)?\s*\{'
                methods = re.findall(method_pattern, content)
                
                for method in methods:
                    if method not in ['if', 'for', 'while', 'switch', 'try', 'catch', 'finally']:
                        methods_by_class[full_class_name].append(method)
                        
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
        
        return methods_by_class
    
    def generate_call_graph(self) -> bool:
        """Generate call graph using java-callgraph tool."""
        if not hasattr(self, 'java_callgraph_path'):
            print("java-callgraph not available")
            return False
        
        print("Generating call graph using java-callgraph...")
        
        # Find all class files
        class_paths = []
        for class_file in self.class_files.values():
            class_paths.append(str(class_file.parent))
        
        if not class_paths:
            print("No compiled class files found. Please compile the Java sources first.")
            return False
        
        # Create temporary file for output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_output = temp_file.name
        
        try:
            # Run java-callgraph with Java module compatibility flags
            cmd = [
                'java', 
                '--add-opens', 'java.base/java.util=ALL-UNNAMED',
                '--add-opens', 'java.base/java.lang=ALL-UNNAMED',
                '--add-opens', 'java.base/java.lang.reflect=ALL-UNNAMED',
                '-jar', self.java_callgraph_path,
                '--include', 'org.uacalc.*',
                '--output', temp_output
            ] + class_paths
            
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✓ Call graph generated successfully")
                self._parse_call_graph_output(temp_output)
                return True
            else:
                print(f"✗ Call graph generation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ Call graph generation timed out")
            return False
        except Exception as e:
            print(f"✗ Error generating call graph: {e}")
            return False
        finally:
            # Clean up temporary file
            if os.path.exists(temp_output):
                os.unlink(temp_output)
    
    def _parse_call_graph_output(self, output_file: str):
        """Parse the call graph output file."""
        try:
            with open(output_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse call graph line format: caller -> callee
                    if ' -> ' in line:
                        caller, callee = line.split(' -> ', 1)
                        caller = caller.strip()
                        callee = callee.strip()
                        
                        # Only include org.uacalc methods
                        if 'org.uacalc' in caller and 'org.uacalc' in callee:
                            self.call_graph_data.append((caller, callee))
                            self.method_dependencies[caller].add(callee)
                            
                            # Extract class information
                            caller_class = '.'.join(caller.split('.')[:-1])
                            callee_class = '.'.join(callee.split('.')[:-1])
                            
                            if caller_class:
                                self.class_methods[caller_class].add(caller)
                                self.method_to_class[caller] = caller_class
                            
                            if callee_class:
                                self.class_methods[callee_class].add(callee)
                                self.method_to_class[callee] = callee_class
            
            print(f"Parsed {len(self.call_graph_data)} method call relationships")
            
        except Exception as e:
            print(f"Error parsing call graph output: {e}")
    
    def build_networkx_graph(self):
        """Build NetworkX graph from call graph data."""
        if not NETWORKX_AVAILABLE:
            return
        
        print("Building NetworkX call graph...")
        
        # Add nodes (methods)
        for caller, callee in self.call_graph_data:
            self.call_graph.add_node(caller, type='method')
            self.call_graph.add_node(callee, type='method')
            self.call_graph.add_edge(caller, callee)
        
        print(f"NetworkX graph built with {self.call_graph.number_of_nodes()} nodes and {self.call_graph.number_of_edges()} edges")
    
    def get_method_statistics(self) -> Dict:
        """Get comprehensive method call statistics."""
        if not NETWORKX_AVAILABLE or not self.call_graph:
            return {"error": "NetworkX not available"}
        
        stats = {
            "total_methods": self.call_graph.number_of_nodes(),
            "total_calls": self.call_graph.number_of_edges(),
            "density": nx.density(self.call_graph),
            "is_weakly_connected": nx.is_weakly_connected(self.call_graph),
            "strongly_connected_components": len(list(nx.strongly_connected_components(self.call_graph))),
            "weakly_connected_components": len(list(nx.weakly_connected_components(self.call_graph))),
        }
        
        # Add centrality measures
        if self.call_graph.number_of_nodes() > 0:
            try:
                stats["pagerank"] = dict(nx.pagerank(self.call_graph))
                stats["betweenness_centrality"] = dict(nx.betweenness_centrality(self.call_graph))
                stats["in_degree_centrality"] = dict(nx.in_degree_centrality(self.call_graph))
                stats["out_degree_centrality"] = dict(nx.out_degree_centrality(self.call_graph))
            except Exception as e:
                stats["centrality_error"] = str(e)
        
        return stats
    
    def get_most_called_methods(self, top_n: int = 20) -> List[Tuple[str, int]]:
        """Get methods that are called most frequently."""
        if not NETWORKX_AVAILABLE or not self.call_graph:
            return []
        
        in_degrees = dict(self.call_graph.in_degree())
        return sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def get_most_calling_methods(self, top_n: int = 20) -> List[Tuple[str, int]]:
        """Get methods that call other methods most frequently."""
        if not NETWORKX_AVAILABLE or not self.call_graph:
            return []
        
        out_degrees = dict(self.call_graph.out_degree())
        return sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def find_call_cycles(self) -> List[List[str]]:
        """Find cycles in the call graph."""
        if not NETWORKX_AVAILABLE or not self.call_graph:
            return []
        
        try:
            return list(nx.simple_cycles(self.call_graph))
        except Exception:
            return []
    
    def generate_mermaid_call_graph(self, output_file: Optional[str] = None, max_nodes: int = 50) -> str:
        """Generate a Mermaid diagram of the call graph (simplified)."""
        mermaid_lines = ["graph TD"]
        
        # Get top methods by centrality
        if NETWORKX_AVAILABLE and self.call_graph:
            try:
                pagerank = nx.pagerank(self.call_graph)
                top_methods = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
                method_set = set(method for method, _ in top_methods)
                
                # Add nodes
                for method in method_set:
                    method_id = method.replace('.', '_').replace('(', '_').replace(')', '_')
                    short_name = method.split('.')[-1]
                    mermaid_lines.append(f'    {method_id}["{short_name}"]')
                
                # Add edges (only between top methods)
                for caller, callee in self.call_graph_data:
                    if caller in method_set and callee in method_set:
                        caller_id = caller.replace('.', '_').replace('(', '_').replace(')', '_')
                        callee_id = callee.replace('.', '_').replace('(', '_').replace(')', '_')
                        mermaid_lines.append(f'    {caller_id} --> {callee_id}')
                        
            except Exception as e:
                print(f"Error generating Mermaid call graph: {e}")
                return "graph TD\n    Error[\"Error generating call graph\"]"
        else:
            mermaid_lines.append('    Error["NetworkX not available"]')
        
        mermaid_content = '\n'.join(mermaid_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(mermaid_content)
            print(f"Mermaid call graph written to {output_file}")
        
        return mermaid_content
    
    def generate_json_report(self, output_file: str):
        """Generate a JSON report of the call graph analysis."""
        report = {
            "call_graph_data": self.call_graph_data,
            "method_dependencies": {method: list(deps) for method, deps in self.method_dependencies.items()},
            "class_methods": {cls: list(methods) for cls, methods in self.class_methods.items()},
            "statistics": {
                "total_methods": len(set(method for caller, callee in self.call_graph_data for method in [caller, callee])),
                "total_calls": len(self.call_graph_data),
                "total_classes": len(self.class_methods)
            }
        }
        
        # Add NetworkX analysis if available
        if NETWORKX_AVAILABLE:
            report["networkx_analysis"] = {
                "graph_statistics": self.get_method_statistics(),
                "most_called_methods": self.get_most_called_methods(),
                "most_calling_methods": self.get_most_calling_methods(),
                "call_cycles": self.find_call_cycles()
            }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"JSON call graph report written to {output_file}")
    
    def generate_text_summary(self, output_file: str):
        """Generate a human-readable text summary."""
        with open(output_file, 'w') as f:
            f.write("UACalc Java Call Graph Analysis\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"Total Methods: {len(set(method for caller, callee in self.call_graph_data for method in [caller, callee]))}\n")
            f.write(f"Total Method Calls: {len(self.call_graph_data)}\n")
            f.write(f"Total Classes: {len(self.class_methods)}\n\n")
            
            # Most called methods
            f.write("Most Called Methods (by incoming calls):\n")
            f.write("-" * 40 + "\n")
            most_called = self.get_most_called_methods(20)
            for i, (method, count) in enumerate(most_called, 1):
                f.write(f"{i:2d}. {method} ({count} calls)\n")
            
            f.write("\nMost Calling Methods (by outgoing calls):\n")
            f.write("-" * 40 + "\n")
            most_calling = self.get_most_calling_methods(20)
            for i, (method, count) in enumerate(most_calling, 1):
                f.write(f"{i:2d}. {method} ({count} calls)\n")
            
            # NetworkX analysis
            if NETWORKX_AVAILABLE:
                f.write("\nNetworkX Call Graph Analysis:\n")
                f.write("-" * 30 + "\n")
                stats = self.get_method_statistics()
                if "error" not in stats:
                    f.write(f"Graph Density: {stats['density']:.3f}\n")
                    f.write(f"Strongly Connected Components: {stats['strongly_connected_components']}\n")
                    f.write(f"Weakly Connected Components: {stats['weakly_connected_components']}\n")
                    
                    # Call cycles
                    cycles = self.find_call_cycles()
                    if cycles:
                        f.write(f"\nCall Cycles Found: {len(cycles)}\n")
                        for i, cycle in enumerate(cycles[:5]):  # Show first 5 cycles
                            f.write(f"  Cycle {i+1}: {' -> '.join(cycle)} -> {cycle[0]}\n")
                    else:
                        f.write("\nNo call cycles found.\n")
                else:
                    f.write("NetworkX analysis not available.\n")
            
            # Class method counts
            f.write("\nMethods per Class:\n")
            f.write("-" * 20 + "\n")
            for cls, methods in sorted(self.class_methods.items(), key=lambda x: len(x[1]), reverse=True):
                f.write(f"{cls}: {len(methods)} methods\n")
        
        print(f"Text summary written to {output_file}")
    
    def run_analysis(self, output_dir: str = "call_graph_analysis"):
        """Run the complete call graph analysis."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print("Starting Java call graph analysis...")
        
        # Check dependencies
        if not self.check_dependencies():
            print("Dependencies not met. Please install required tools.")
            return None
        
        # Scan files
        self.scan_java_files()
        
        # Generate call graph
        if not self.generate_call_graph():
            print("Failed to generate call graph.")
            return None
        
        # Build NetworkX graph
        self.build_networkx_graph()
        
        # Generate outputs
        self.generate_mermaid_call_graph(output_path / "call_graph.mmd")
        self.generate_json_report(output_path / "call_graph.json")
        self.generate_text_summary(output_path / "call_graph_summary.txt")
        
        print(f"\nCall graph analysis complete! Output files written to {output_path}")
        print("\nGenerated files:")
        print("- call_graph.mmd: Mermaid diagram of method call graph")
        print("- call_graph.json: Complete call graph data in JSON format")
        print("- call_graph_summary.txt: Human-readable summary")
        
        return output_path

def main():
    parser = argparse.ArgumentParser(description="Analyze Java call graphs in UACalc library")
    parser.add_argument("--source", default=".", 
                       help="Source directory containing Java files (default: current directory)")
    parser.add_argument("--output", default="call_graph_analysis",
                       help="Output directory for analysis results (default: call_graph_analysis)")
    
    args = parser.parse_args()
    
    analyzer = JavaCallGraphAnalyzer(args.source)
    output_path = analyzer.run_analysis(args.output)
    
    if output_path:
        # Print summary to console
        print("\n" + "="*60)
        print("CALL GRAPH SUMMARY:")
        print("="*60)
        
        most_called = analyzer.get_most_called_methods(10)
        if most_called:
            print("Top 10 Most Called Methods:")
            for i, (method, count) in enumerate(most_called, 1):
                print(f"{i:2d}. {method} ({count} calls)")
        
        print("\nTop 10 Most Calling Methods:")
        most_calling = analyzer.get_most_calling_methods(10)
        for i, (method, count) in enumerate(most_calling, 1):
            print(f"{i:2d}. {method} ({count} calls)")

if __name__ == "__main__":
    main()
