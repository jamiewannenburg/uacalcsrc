#!/usr/bin/env python3
"""
Test script to verify Java compatibility setup is working correctly.
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def test_java_wrapper_compilation():
    """Test that JavaWrapper compiles successfully."""
    print("Testing JavaWrapper compilation...")
    
    try:
        result = subprocess.run([
            "javac", "-cp", "jars/*", "scripts/JavaWrapper.java"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ JavaWrapper compiled successfully")
            return True
        else:
            print(f"✗ JavaWrapper compilation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ JavaWrapper compilation error: {e}")
        return False

def test_java_wrapper_execution():
    """Test that JavaWrapper can execute basic operations."""
    print("\nTesting JavaWrapper execution...")
    
    # Test basic properties operation
    try:
        result = subprocess.run([
            "java", "-cp", "jars/*:scripts", "JavaWrapper", 
            "properties", "resources/algebras/ba2.ua"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if "name" in data and "cardinality" in data:
                print("✓ JavaWrapper properties operation works")
                print(f"  Algebra: {data['name']}, size: {data['cardinality']}")
                return True
            else:
                print(f"✗ JavaWrapper properties returned invalid data: {data}")
                return False
        else:
            print(f"✗ JavaWrapper properties failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ JavaWrapper execution error: {e}")
        return False

def test_java_cg_operation():
    """Test that JavaWrapper can compute congruences."""
    print("\nTesting JavaWrapper Cg operation...")
    
    try:
        result = subprocess.run([
            "java", "-cp", "jars/*:scripts", "JavaWrapper", 
            "cg", "resources/algebras/ba2.ua", "0", "1"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if "partition" in data:
                print("✓ JavaWrapper Cg operation works")
                print(f"  Cg(0,1) partition: {data['partition']}")
                return True
            else:
                print(f"✗ JavaWrapper Cg returned invalid data: {data}")
                return False
        else:
            print(f"✗ JavaWrapper Cg failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ JavaWrapper Cg error: {e}")
        return False

def test_java_lattice_operation():
    """Test that JavaWrapper can compute lattice properties."""
    print("\nTesting JavaWrapper lattice operation...")
    
    try:
        result = subprocess.run([
            "java", "-cp", "jars/*:scripts", "JavaWrapper", 
            "lattice", "resources/algebras/ba2.ua"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if "size" in data:
                print("✓ JavaWrapper lattice operation works")
                print(f"  Lattice size: {data['size']}")
                return True
            else:
                print(f"✗ JavaWrapper lattice returned invalid data: {data}")
                return False
        else:
            print(f"✗ JavaWrapper lattice failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ JavaWrapper lattice error: {e}")
        return False

def test_python_java_compatibility():
    """Test that Python can run Java compatibility tests."""
    print("\nTesting Python-Java compatibility tests...")
    
    try:
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/python/test_java_compatibility.py::JavaCompatibilityTest::test_algebra_properties_compatibility",
            "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and "PASSED" in result.stdout:
            print("✓ Python-Java compatibility test passed")
            return True
        else:
            print(f"✗ Python-Java compatibility test failed")
            print(f"  stdout: {result.stdout}")
            print(f"  stderr: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Python-Java compatibility test error: {e}")
        return False

def check_prerequisites():
    """Check that all prerequisites are available."""
    print("Checking prerequisites...")
    
    # Check Java
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Java is available")
        else:
            print("✗ Java not found")
            return False
    except:
        print("✗ Java not found")
        return False
    
    # Check uacalc.jar
    if Path("jars/uacalc.jar").exists():
        print("✓ uacalc.jar found")
    else:
        print("✗ uacalc.jar not found in jars/ directory")
        return False
    
    # Check JavaWrapper.java
    if Path("scripts/JavaWrapper.java").exists():
        print("✓ JavaWrapper.java found")
    else:
        print("✗ JavaWrapper.java not found")
        return False
    
    # Check sample algebra files
    algebras_dir = Path("resources/algebras")
    if algebras_dir.exists() and list(algebras_dir.glob("*.ua")):
        print("✓ Sample algebra files found")
    else:
        print("✗ No sample algebra files found")
        return False
    
    return True

def main():
    """Run all Java compatibility tests."""
    print("Java Compatibility Test Suite")
    print("=" * 50)
    
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please run setup first.")
        return 1
    
    tests = [
        test_java_wrapper_compilation,
        test_java_wrapper_execution,
        test_java_cg_operation,
        test_java_lattice_operation,
        test_python_java_compatibility,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Java compatibility tests passed!")
        print("\nYou can now run the full compatibility test suite:")
        print("  python -m pytest tests/python/test_java_compatibility.py -v")
        return 0
    else:
        print("❌ Some tests failed. Please check the setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())