#!/usr/bin/env python3
"""
Demo script showing Ant integration for dependency analysis.

This script demonstrates how to use the Ant build system for:
1. Setting up call graph tools
2. Running dependency analysis
3. Managing the build process

Usage:
    python ant_integration_demo.py
"""

import subprocess
import sys
from pathlib import Path

def run_ant_command(target, description):
    """Run an Ant command and return success status."""
    print(f"\n🔧 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(['ant', target], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✓ {description} completed successfully")
            if result.stdout:
                # Show last few lines of output
                lines = result.stdout.strip().split('\n')
                for line in lines[-5:]:
                    if line.strip():
                        print(f"  {line}")
            return True
        else:
            print(f"✗ {description} failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ {description} timed out")
        return False
    except FileNotFoundError:
        print("✗ Ant not found. Please install Apache Ant")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def check_ant_available():
    """Check if Ant is available."""
    try:
        result = subprocess.run(['ant', '-version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ Ant found: {version_line}")
            return True
        else:
            print("✗ Ant not found")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ Ant not found")
        return False

def show_available_targets():
    """Show available Ant targets for dependency analysis."""
    print("\n📋 Available Ant Targets for Dependency Analysis:")
    print("=" * 60)
    
    targets = [
        ("setup-callgraph", "Setup java-callgraph tool in tools/callgraph/"),
        ("callgraph", "Generate method-level call graph analysis"),
        ("dependency-analysis", "Generate both package and method-level analysis"),
        ("clean-callgraph", "Clean call graph tools and analysis files"),
        ("compile-dist", "Compile Java sources (required for analysis)")
    ]
    
    for target, description in targets:
        print(f"  ant {target:<20} - {description}")

def main():
    print("🚀 UACalc Ant Integration Demo")
    print("=" * 60)
    print("This demo shows how to use Ant for dependency analysis setup and execution.")
    
    # Check if Ant is available
    if not check_ant_available():
        print("\nPlease install Apache Ant to use the integrated build system.")
        print("On Ubuntu/Debian: sudo apt-get install ant")
        print("On macOS: brew install ant")
        print("On Windows: Download from https://ant.apache.org/")
        return 1
    
    # Show available targets
    show_available_targets()
    
    # Demo the workflow
    print("\n🔄 Demo Workflow:")
    print("=" * 30)
    
    # Step 1: Setup call graph tools
    if not run_ant_command("setup-callgraph", "Setting up java-callgraph tool"):
        print("\nSetup failed. This might be due to missing dependencies:")
        print("- Git (for cloning java-callgraph)")
        print("- Maven (for building java-callgraph)")
        print("- Java 8+ (for running Maven)")
        return 1
    
    # Step 2: Compile sources
    if not run_ant_command("compile-dist", "Compiling Java sources"):
        print("\nCompilation failed. Check your Java sources.")
        return 1
    
    # Step 3: Run dependency analysis
    if not run_ant_command("dependency-analysis", "Running comprehensive dependency analysis"):
        print("\nDependency analysis failed.")
        return 1
    
    # Show results
    print("\n✅ Demo Complete!")
    print("=" * 20)
    
    # Check what was generated
    analysis_dirs = ["dependency_analysis", "call_graph_analysis"]
    for dir_name in analysis_dirs:
        if Path(dir_name).exists():
            files = list(Path(dir_name).glob("*"))
            print(f"\n📁 {dir_name}/ ({len(files)} files):")
            for file_path in sorted(files):
                if file_path.is_file():
                    print(f"   📄 {file_path.name}")
    
    print("\n💡 Next Steps:")
    print("  • Explore the generated analysis files")
    print("  • Use Mermaid diagrams for visualization")
    print("  • Analyze JSON data programmatically")
    print("  • Run 'ant clean-callgraph' to clean up")
    
    print("\n🔧 Manual Commands:")
    print("  • ant setup-callgraph    - Setup tools only")
    print("  • ant callgraph          - Method-level analysis only")
    print("  • ant dependency-analysis - Full analysis")
    print("  • ant clean-callgraph    - Clean everything")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
