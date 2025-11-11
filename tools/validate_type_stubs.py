#!/usr/bin/env python3
"""
Script to validate that all exported names from Rust registration functions
are present in the uacalc_lib.pyi type stub file.

This script parses the Rust registration functions and compares them with
the type stubs to ensure nothing is missing.
"""

import re
import sys
from pathlib import Path
from typing import Dict, Set, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def extract_exported_names_from_rust() -> Dict[str, Set[str]]:
    """Extract exported class and function names from Rust registration functions."""
    uacalc_lib_src = project_root / "uacalc_lib" / "src"
    exports: Dict[str, Set[str]] = {}
    
    # Pattern to match m.add("ClassName", ...) or m.add_function(...)
    add_class_pattern = re.compile(r'm\.add\("([^"]+)",')
    add_function_pattern = re.compile(r'm\.add_function\(wrap_pyfunction!\((\w+),')
    
    # Find all registration functions
    for rust_file in uacalc_lib_src.rglob("*.rs"):
        with open(rust_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check if this file has a register_*_module function
            module_match = re.search(r'pub fn register_(\w+)_module', content)
            if not module_match:
                continue
            
            module_name = module_match.group(1)
            if module_name not in exports:
                exports[module_name] = set()
            
            # Extract class names
            for match in add_class_pattern.finditer(content):
                class_name = match.group(1)
                exports[module_name].add(class_name)
            
            # Extract function names
            for match in add_function_pattern.finditer(content):
                func_name = match.group(1)
                exports[module_name].add(func_name)
    
    return exports

def extract_names_from_pyi() -> Dict[str, Set[str]]:
    """Extract class and function names from the .pyi file."""
    pyi_file = project_root / "python" / "uacalc" / "uacalc_lib.pyi"
    
    if not pyi_file.exists():
        return {}
    
    with open(pyi_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    exports: Dict[str, Set[str]] = {}
    current_module = None
    
    # Pattern to match module class definitions
    module_pattern = re.compile(r'^class (\w+):')
    class_pattern = re.compile(r'^\s+class (\w+):')
    function_pattern = re.compile(r'^\s+def (\w+)\(')
    
    for line in content.split('\n'):
        # Check for module class
        match = module_pattern.match(line)
        if match:
            module_name = match.group(1)
            if module_name in ['element', 'types', 'example', 'terms', 'lat', 'io', 'eq', 'group', 'fplat', 'alg', 'util']:
                current_module = module_name
                exports[current_module] = set()
            continue
        
        if current_module:
            # Check for class definitions
            match = class_pattern.match(line)
            if match:
                class_name = match.group(1)
                exports[current_module].add(class_name)
                continue
            
            # Check for function definitions (module-level)
            match = function_pattern.match(line)
            if match:
                func_name = match.group(1)
                # Only add if it's at module level (not indented much)
                if line.startswith('    def '):
                    exports[current_module].add(func_name)
    
    return exports

def compare_exports() -> Tuple[bool, List[str]]:
    """Compare Rust exports with .pyi file exports."""
    rust_exports = extract_exported_names_from_rust()
    pyi_exports = extract_names_from_pyi()
    
    issues = []
    all_good = True
    
    # Check each module
    all_modules = set(rust_exports.keys()) | set(pyi_exports.keys())
    
    for module in sorted(all_modules):
        rust_names = rust_exports.get(module, set())
        pyi_names = pyi_exports.get(module, set())
        
        missing_in_pyi = rust_names - pyi_names
        extra_in_pyi = pyi_names - rust_names
        
        if missing_in_pyi:
            all_good = False
            issues.append(f"Module '{module}': Missing in .pyi: {sorted(missing_in_pyi)}")
        
        if extra_in_pyi:
            # This is less critical, but worth noting
            issues.append(f"Module '{module}': Extra in .pyi (not in Rust): {sorted(extra_in_pyi)}")
    
    return all_good, issues

def main():
    """Main validation function."""
    print("Validating type stubs against Rust exports...")
    print("=" * 60)
    
    all_good, issues = compare_exports()
    
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✓ All exported names are present in the .pyi file!")
    
    # Also print summary
    rust_exports = extract_exported_names_from_rust()
    pyi_exports = extract_names_from_pyi()
    
    print("\nSummary:")
    print(f"  Modules in Rust: {len(rust_exports)}")
    print(f"  Modules in .pyi: {len(pyi_exports)}")
    
    for module in sorted(set(rust_exports.keys()) | set(pyi_exports.keys())):
        rust_count = len(rust_exports.get(module, set()))
        pyi_count = len(pyi_exports.get(module, set()))
        print(f"  {module}: Rust={rust_count}, .pyi={pyi_count}")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())

