#!/usr/bin/env python3
"""
Quick wrapper script to generate UACalc dependency graphs.

This is a simplified interface to the java_dependency_analyzer.py tool,
specifically designed for generating Mermaid diagrams that LLMs can easily
understand and use when analyzing the UACalc project structure.

Usage:
    python generate_dependency_graph.py [--output-dir DIR] [--format FORMAT]

Examples:
    python generate_dependency_graph.py
    python generate_dependency_graph.py --format mermaid
    python generate_dependency_graph.py --output-dir my_analysis
"""

import sys
import os
from pathlib import Path

# Add the scripts directory to the path so we can import the analyzer
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from java_dependency_analyzer import JavaDependencyAnalyzer

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate UACalc Java dependency graphs for LLM analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Generate all formats in dependency_analysis/
  %(prog)s --format mermaid          # Only generate Mermaid diagrams
  %(prog)s --output-dir my_graphs    # Custom output directory
  %(prog)s --show-mermaid            # Display Mermaid diagram in console
        """
    )
    
    parser.add_argument("--output-dir", default="dependency_analysis",
                       help="Output directory for generated files (default: dependency_analysis)")
    parser.add_argument("--format", choices=["all", "mermaid", "dot", "json", "text"], 
                       default="all", help="Output format (default: all)")
    parser.add_argument("--show-mermaid", action="store_true",
                       help="Display Mermaid diagram in console")
    parser.add_argument("--source", default=".",
                       help="Source directory containing Java files (default: current directory)")
    
    args = parser.parse_args()
    
    print("🔍 UACalc Java Dependency Graph Generator")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = JavaDependencyAnalyzer(args.source)
    
    # Run analysis
    output_path = analyzer.run_analysis(args.output_dir)
    
    if args.show_mermaid or args.format in ["all", "mermaid"]:
        print("\n📊 MERMAID DIAGRAM (Package Dependencies):")
        print("=" * 60)
        mermaid_diagram = analyzer.generate_mermaid_diagram()
        print(mermaid_diagram)
        
        print("\n📊 MERMAID DIAGRAM (Key Class Dependencies):")
        print("=" * 60)
        detailed_diagram = analyzer.generate_detailed_mermaid()
        print(detailed_diagram)
        
        # Save Mermaid diagrams to separate files for easy copying
        mermaid_file = output_path / "package_dependencies.mmd"
        detailed_file = output_path / "class_dependencies.mmd"
        
        print(f"\n💾 Mermaid diagrams saved to:")
        print(f"   📄 {mermaid_file}")
        print(f"   📄 {detailed_file}")
    
    print(f"\n✅ Analysis complete! All files saved to: {output_path}")
    print("\n📋 Generated files:")
    for file_path in sorted(output_path.glob("*")):
        if file_path.is_file():
            print(f"   📄 {file_path.name}")
    
    print("\n💡 Usage tips:")
    print("   • Copy Mermaid diagrams to any Mermaid-compatible viewer")
    print("   • Use the JSON file for programmatic analysis")
    print("   • The DOT file can be rendered with Graphviz")
    print("   • The text summary provides human-readable overview")

if __name__ == "__main__":
    main()
