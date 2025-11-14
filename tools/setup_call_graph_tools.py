#!/usr/bin/env python3
"""
Setup script for Java Call Graph Analysis Tools

This script helps set up the required tools for fine-grained call graph analysis,
including java-callgraph and other dependencies.

Usage:
    python setup_call_graph_tools.py [options]
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse

def check_java():
    """Check if Java is installed and get version."""
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stderr.split('\n')[0]
            print(f"✓ Java found: {version_line}")
            return True
        else:
            print("✗ Java not found")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ Java not found")
        return False

def check_maven():
    """Check if Maven is installed."""
    try:
        result = subprocess.run(['mvn', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ Maven found: {version_line}")
            return True
        else:
            print("✗ Maven not found")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ Maven not found")
        return False

def check_git():
    """Check if Git is installed."""
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.strip()
            print(f"✓ Git found: {version_line}")
            return True
        else:
            print("✗ Git not found")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ Git not found")
        return False

def install_java_callgraph(install_dir: Path):
    """Install java-callgraph tool."""
    print("\nInstalling java-callgraph...")
    
    java_callgraph_dir = install_dir / "java-callgraph"
    
    if java_callgraph_dir.exists():
        print(f"java-callgraph already exists at {java_callgraph_dir}")
        return str(java_callgraph_dir / "target" / "java-callgraph-1.0-SNAPSHOT.jar")
    
    try:
        # Clone the repository
        print("Cloning java-callgraph repository...")
        result = subprocess.run([
            'git', 'clone', 
            'https://github.com/gousiosg/java-callgraph.git',
            str(java_callgraph_dir)
        ], check=True, capture_output=True, text=True)
        
        print("✓ Repository cloned successfully")
        
        # Build the project
        print("Building java-callgraph...")
        result = subprocess.run([
            'mvn', 'clean', 'compile', 'package'
        ], cwd=java_callgraph_dir, check=True, capture_output=True, text=True)
        
        print("✓ java-callgraph built successfully")
        
        jar_path = java_callgraph_dir / "target" / "java-callgraph-1.0-SNAPSHOT.jar"
        if jar_path.exists():
            print(f"✓ JAR file created: {jar_path}")
            return str(jar_path)
        else:
            print("✗ JAR file not found after build")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing java-callgraph: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None

def install_alternative_tools(install_dir: Path):
    """Install alternative call graph tools."""
    print("\nInstalling alternative tools...")
    
    # Install WALA (if needed)
    wala_dir = install_dir / "wala"
    if not wala_dir.exists():
        print("WALA is a more advanced but complex tool.")
        print("For now, we'll focus on java-callgraph.")
        print("You can install WALA manually from: https://github.com/wala/WALA")
    
    # Install Soot (if needed)
    soot_dir = install_dir / "soot"
    if not soot_dir.exists():
        print("Soot is another powerful static analysis tool.")
        print("You can install Soot manually from: https://github.com/soot-oss/soot")

def create_config_file(install_dir: Path, jar_path: str):
    """Create a configuration file for the tools."""
    config = {
        "java_callgraph": {
            "jar_path": jar_path,
            "install_dir": str(install_dir)
        },
        "tools": {
            "java_callgraph_analyzer": "tools/java_call_graph_analyzer.py",
            "generate_dependency_graph": "tools/generate_dependency_graph.py"
        }
    }
    
    config_file = install_dir / "call_graph_config.json"
    import json
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration file created: {config_file}")

def main():
    parser = argparse.ArgumentParser(description="Setup Java call graph analysis tools")
    parser.add_argument("--install-dir", default="tools/callgraph",
                       help="Directory to install tools (default: tools/callgraph)")
    parser.add_argument("--skip-deps", action="store_true",
                       help="Skip dependency checks")
    
    args = parser.parse_args()
    
    install_dir = Path(args.install_dir)
    install_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔧 Java Call Graph Tools Setup")
    print("=" * 40)
    print(f"Install directory: {install_dir}")
    
    # Check dependencies
    if not args.skip_deps:
        print("\nChecking dependencies...")
        deps_ok = True
        
        if not check_java():
            deps_ok = False
            print("Please install Java 8 or later")
        
        if not check_maven():
            deps_ok = False
            print("Please install Maven")
        
        if not check_git():
            deps_ok = False
            print("Please install Git")
        
        if not deps_ok:
            print("\n✗ Some dependencies are missing. Please install them and try again.")
            return 1
    
    # Install java-callgraph
    jar_path = install_java_callgraph(install_dir)
    if not jar_path:
        print("\n✗ Failed to install java-callgraph")
        return 1
    
    # Install alternative tools
    install_alternative_tools(install_dir)
    
    # Create configuration file
    create_config_file(install_dir, jar_path)
    
    print("\n✅ Setup complete!")
    print(f"\nTools installed in: {install_dir}")
    print(f"java-callgraph JAR: {jar_path}")
    print("\nYou can now run call graph analysis with:")
    print("  python tools/java_call_graph_analyzer.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
