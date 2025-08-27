#!/usr/bin/env python3
"""
Simple test script to verify JavaWrapper functionality
"""

import subprocess
import json
import os
import sys

def test_java_wrapper():
    """Test the JavaWrapper functionality"""
    
    # Check if Java is available
    try:
        subprocess.run(["java", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Java not found. Skipping Java wrapper tests.")
        return False
    
    # Check if the Java wrapper file exists
    java_wrapper_path = "scripts/JavaWrapper.java"
    if not os.path.exists(java_wrapper_path):
        print(f"Java wrapper not found: {java_wrapper_path}")
        return False
    
    # Try to compile the Java wrapper
    try:
        result = subprocess.run([
            "javac", "-cp", "jars/*;org", "-d", "scripts", java_wrapper_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"Failed to compile Java wrapper: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error compiling Java wrapper: {e}")
        return False
    
    # Test with a simple algebra file
    test_file = "resources/algebras/ba2.ua"
    if not os.path.exists(test_file):
        print(f"Test algebra file not found: {test_file}")
        return False
    
    print("Testing JavaWrapper functionality...")
    
    # Test properties command
    try:
        result = subprocess.run([
            "java", "-cp", "jars/*;scripts", "scripts.JavaWrapper", 
            "properties", test_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            print(f"✓ Properties test passed: {data.get('name', 'Unknown')} algebra")
        else:
            print(f"✗ Properties test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Properties test error: {e}")
        return False
    
    # Test cg command
    try:
        result = subprocess.run([
            "java", "-cp", "jars/*;scripts", "scripts.JavaWrapper", 
            "cg", test_file, "0", "1"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            print(f"✓ CG test passed: partition with {len(data.get('partition', []))} blocks")
        else:
            print(f"✗ CG test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ CG test error: {e}")
        return False
    
    # Test lattice command
    try:
        result = subprocess.run([
            "java", "-cp", "jars/*;scripts", "scripts.JavaWrapper", 
            "lattice", test_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            print(f"✓ Lattice test passed: size {data.get('size', 'Unknown')}")
        else:
            print(f"✗ Lattice test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Lattice test error: {e}")
        return False
    
    print("All JavaWrapper tests passed!")
    return True

if __name__ == "__main__":
    success = test_java_wrapper()
    sys.exit(0 if success else 1)
