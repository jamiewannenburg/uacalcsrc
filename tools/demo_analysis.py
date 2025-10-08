#!/usr/bin/env python3
"""
Demo script showing both package-level and method-level dependency analysis.

This script demonstrates the two levels of analysis available:
1. Package/class-level dependencies (coarse-grained)
2. Method-level call graphs (fine-grained)

Usage:
    python demo_analysis.py
"""

import sys
from pathlib import Path

# Add the tools directory to the path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

def run_package_analysis():
    """Run package-level dependency analysis."""
    print("🔍 Running Package-Level Dependency Analysis")
    print("=" * 50)
    
    try:
        from java_dependency_analyzer import JavaDependencyAnalyzer
        
        analyzer = JavaDependencyAnalyzer(".")
        output_path = analyzer.run_analysis("demo_package_analysis")
        
        if output_path:
            print(f"✓ Package analysis complete: {output_path}")
            
            # Show some key insights
            files_by_deps = analyzer.get_files_by_dependency_count()
            print(f"\n📊 Package Analysis Insights:")
            print(f"  • Total files analyzed: {len(files_by_deps)}")
            print(f"  • Leaves (depend on nothing): {len([f for f in files_by_deps if f[1] == 0])}")
            print(f"  • Most dependent file: {files_by_deps[-1][0]} ({files_by_deps[-1][1]} dependencies)")
            
            return True
        else:
            print("✗ Package analysis failed")
            return False
            
    except Exception as e:
        print(f"✗ Error in package analysis: {e}")
        return False

def run_call_graph_analysis():
    """Run method-level call graph analysis."""
    print("\n🔍 Running Method-Level Call Graph Analysis")
    print("=" * 50)
    
    try:
        from java_call_graph_analyzer import JavaCallGraphAnalyzer
        
        analyzer = JavaCallGraphAnalyzer(".")
        
        # Check if tools are available
        if not analyzer.check_dependencies():
            print("⚠️  Call graph tools not available. Run setup first:")
            print("   python tools/setup_call_graph_tools.py")
            return False
        
        output_path = analyzer.run_analysis("demo_call_graph_analysis")
        
        if output_path:
            print(f"✓ Call graph analysis complete: {output_path}")
            
            # Show some key insights
            most_called = analyzer.get_most_called_methods(5)
            most_calling = analyzer.get_most_calling_methods(5)
            
            print(f"\n📊 Call Graph Analysis Insights:")
            if most_called:
                print(f"  • Most called method: {most_called[0][0]} ({most_called[0][1]} calls)")
            if most_calling:
                print(f"  • Most calling method: {most_calling[0][0]} ({most_calling[0][1]} calls)")
            
            return True
        else:
            print("✗ Call graph analysis failed")
            return False
            
    except Exception as e:
        print(f"✗ Error in call graph analysis: {e}")
        return False

def show_comparison():
    """Show comparison between the two analysis levels."""
    print("\n📊 Analysis Level Comparison")
    print("=" * 50)
    
    print("Package/Class Level Analysis:")
    print("  • Granularity: Classes and packages")
    print("  • Dependencies: Import relationships")
    print("  • Use cases: Architecture understanding, refactoring planning")
    print("  • Tools: Custom Python analyzer")
    print("  • Output: Package dependency graphs")
    
    print("\nMethod Level Analysis:")
    print("  • Granularity: Individual methods")
    print("  • Dependencies: Method call relationships")
    print("  • Use cases: Performance optimization, code complexity")
    print("  • Tools: java-callgraph (off-the-shelf)")
    print("  • Output: Method call graphs")
    
    print("\n💡 When to use which:")
    print("  • Use package analysis for: High-level architecture, dependency management")
    print("  • Use call graph analysis for: Performance tuning, method optimization")

def main():
    print("🚀 UACalc Dependency Analysis Demo")
    print("=" * 60)
    print("This demo shows both levels of dependency analysis available:")
    print("1. Package/class-level (coarse-grained)")
    print("2. Method-level (fine-grained)")
    print()
    
    # Run package analysis
    package_success = run_package_analysis()
    
    # Run call graph analysis
    call_graph_success = run_call_graph_analysis()
    
    # Show comparison
    show_comparison()
    
    # Summary
    print("\n✅ Demo Summary")
    print("=" * 20)
    if package_success:
        print("✓ Package-level analysis completed")
    else:
        print("✗ Package-level analysis failed")
    
    if call_graph_success:
        print("✓ Method-level analysis completed")
    else:
        print("✗ Method-level analysis failed (may need setup)")
    
    print("\n📁 Generated files:")
    print("  • demo_package_analysis/ - Package dependency analysis")
    print("  • demo_call_graph_analysis/ - Method call graph analysis")
    
    print("\n🔧 Next steps:")
    if not call_graph_success:
        print("  1. Run: python tools/setup_call_graph_tools.py")
        print("  2. Compile your Java sources")
        print("  3. Re-run this demo")
    else:
        print("  1. Explore the generated analysis files")
        print("  2. Use the Mermaid diagrams for visualization")
        print("  3. Analyze the JSON data programmatically")

if __name__ == "__main__":
    main()
