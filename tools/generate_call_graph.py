#!/usr/bin/env python3
"""
Quick wrapper script to generate Java call graphs.

This is a simplified interface to the java_call_graph_analyzer.py tool,
designed for generating fine-grained method-level call graphs.

Usage:
    python generate_call_graph.py [options]

Examples:
    python generate_call_graph.py
    python generate_call_graph.py --output-dir my_call_graph
    python generate_call_graph.py --show-mermaid
"""

import sys
import os
from pathlib import Path

# Add the tools directory to the path so we can import the analyzer
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from java_call_graph_analyzer import JavaCallGraphAnalyzer

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate Java call graphs for UACalc library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Generate call graph analysis
  %(prog)s --output-dir my_graphs    # Custom output directory
  %(prog)s --show-mermaid            # Display Mermaid diagram in console
  %(prog)s --setup                   # Setup required tools first
        """
    )
    
    parser.add_argument("--output-dir", default="call_graph_analysis",
                       help="Output directory for generated files (default: call_graph_analysis)")
    parser.add_argument("--show-mermaid", action="store_true",
                       help="Display Mermaid diagram in console")
    parser.add_argument("--source", default=".",
                       help="Source directory containing Java files (default: current directory)")
    parser.add_argument("--setup", action="store_true",
                       help="Setup required tools first")
    parser.add_argument("--use-ant", action="store_true",
                       help="Use Ant build system for setup and analysis")
    
    args = parser.parse_args()
    
    print("🔍 UACalc Java Call Graph Generator")
    print("=" * 50)
    
    # Setup tools if requested
    if args.setup:
        if args.use_ant:
            print("Setting up call graph tools using Ant...")
            import subprocess
            result = subprocess.run(['ant', 'setup-callgraph'], capture_output=True, text=True)
            if result.returncode != 0:
                print("Ant setup failed. Please check the error messages above.")
                print(f"Error: {result.stderr}")
                return 1
            print("Ant setup complete! Now running call graph analysis...\n")
        else:
            print("Setting up call graph tools...")
            from setup_call_graph_tools import main as setup_main
            setup_result = setup_main()
            if setup_result != 0:
                print("Setup failed. Please check the error messages above.")
                return 1
            print("Setup complete! Now running call graph analysis...\n")
    
    # Initialize analyzer
    analyzer = JavaCallGraphAnalyzer(args.source)
    
    # Run analysis
    output_path = analyzer.run_analysis(args.output_dir)
    
    if not output_path:
        print("Call graph analysis failed. You may need to:")
        print("1. Compile your Java sources first")
        print("2. Run with --setup to install required tools")
        print("3. Check that java-callgraph is properly installed")
        return 1
    
    if args.show_mermaid:
        print("\n📊 MERMAID DIAGRAM (Method Call Graph):")
        print("=" * 60)
        mermaid_diagram = analyzer.generate_mermaid_call_graph()
        print(mermaid_diagram)
    
    print(f"\n✅ Analysis complete! All files saved to: {output_path}")
    print("\n📋 Generated files:")
    for file_path in sorted(output_path.glob("*")):
        if file_path.is_file():
            print(f"   📄 {file_path.name}")
    
    print("\n💡 Usage tips:")
    print("   • The call graph shows method-level dependencies")
    print("   • Use the JSON file for programmatic analysis")
    print("   • The text summary shows most called/calling methods")
    print("   • Mermaid diagrams can be viewed in any Mermaid-compatible viewer")
    
    # Show quick summary
    print("\n📊 Quick Summary:")
    most_called = analyzer.get_most_called_methods(5)
    if most_called:
        print("Most Called Methods:")
        for i, (method, count) in enumerate(most_called, 1):
            print(f"  {i}. {method} ({count} calls)")
    
    most_calling = analyzer.get_most_calling_methods(5)
    if most_calling:
        print("Most Calling Methods:")
        for i, (method, count) in enumerate(most_calling, 1):
            print(f"  {i}. {method} ({count} calls)")

if __name__ == "__main__":
    sys.exit(main())
