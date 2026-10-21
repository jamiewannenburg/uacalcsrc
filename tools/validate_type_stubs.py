#!/usr/bin/env python3
"""
Validate that uacalc_lib.pyi matches the actual wrapper surface.

The checker prefers a live ``import uacalc_lib`` (dir of each submodule).
When the extension is not importable it falls back to parsing Rust
``m.add`` / ``m.add_function`` / ``m.add_class`` / ``#[pyclass(name=...)]``.
"""

import inspect
import re
import sys
from pathlib import Path
from typing import Dict, Set, List, Tuple, Optional

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
    pyclass_name = re.compile(r'#\[pyclass\(name\s*=\s*"([^"]+)"')
    
    # First, find all actual top-level modules by reading lib.rs
    lib_rs = uacalc_lib_src / "lib.rs"
    actual_modules = set()
    if lib_rs.exists():
        with open(lib_rs, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find all add_submodule calls to get actual module names
            # Pattern matches: m.add_submodule(&alg_module)?
            submodule_pattern = re.compile(r'm\.add_submodule\(&(\w+)_module\)')
            for match in submodule_pattern.finditer(content):
                # Extract module name from variable name like "alg_module" -> "alg"
                var_name = match.group(1)
                # The variable is named "{module}_module", so the module name is just var_name
                actual_modules.add(var_name)
    
    # Now find all module registration functions, but only for actual modules
    module_to_files: Dict[str, List[Path]] = {}
    for rust_file in uacalc_lib_src.rglob("*.rs"):
        with open(rust_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check if this file has a register_*_module function
            module_match = re.search(r'pub fn register_(\w+)_module', content)
            if module_match:
                module_name = module_match.group(1)
                # Only include if it's an actual top-level module
                if module_name in actual_modules:
                    if module_name not in module_to_files:
                        module_to_files[module_name] = []
                    module_to_files[module_name].append(rust_file)
    
    # For each module, search all files in its directory (including subdirectories)
    # to find all registrations, not just in the main registration file
    for module_name, main_files in module_to_files.items():
        if module_name not in exports:
            exports[module_name] = set()
        
        if not main_files:
            continue
        
        # Determine the module directory - use the directory of the first main file
        module_dir = main_files[0].parent
        
        # If the file is directly in src/ (like terms.rs, io.rs), search that file only
        # Otherwise, search the entire module directory tree
        if module_dir == uacalc_lib_src:
            # Module is in root src directory, search just that file
            for main_file in main_files:
                with open(main_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    _collect_rust_exports(
                        content, exports[module_name],
                        add_class_pattern, add_function_pattern, pyclass_name,
                    )
        else:
            # Module has its own directory, search all files in that directory tree
            for rust_file in module_dir.rglob("*.rs"):
                with open(rust_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    _collect_rust_exports(
                        content, exports[module_name],
                        add_class_pattern, add_function_pattern, pyclass_name,
                    )
    
    return exports


def _collect_rust_exports(
    content: str,
    bucket: Set[str],
    add_class_pattern,
    add_function_pattern,
    pyclass_name,
) -> None:
    for match in add_class_pattern.finditer(content):
        name = match.group(1)
        if not name.startswith("Py"):
            bucket.add(name)
    for match in add_function_pattern.finditer(content):
        bucket.add(match.group(1))
    for match in pyclass_name.finditer(content):
        bucket.add(match.group(1))


def extract_runtime_exports() -> Optional[Dict[str, Set[str]]]:
    """Live uacalc_lib submodule dir(); None if the extension is not importable."""
    try:
        import uacalc_lib  # pylint: disable=import-outside-toplevel
    except ImportError:
        return None
    skip = {"general_algebra"}  # historical pyi module name, not a real submodule
    exports: Dict[str, Set[str]] = {}
    for name in dir(uacalc_lib):
        if name.startswith("_"):
            continue
        obj = getattr(uacalc_lib, name)
        if not inspect.ismodule(obj):
            continue
        if name in skip:
            continue
        names = set()
        for item in dir(obj):
            if item.startswith("_") or item.startswith("Py"):
                continue
            child = getattr(obj, item, None)
            if inspect.ismodule(child):
                continue
            names.add(item)
        exports[name] = names
    return exports

def extract_names_from_pyi() -> Dict[str, Set[str]]:
    """Extract class and function names from the .pyi file."""
    pyi_file = project_root / "python" / "uacalc_lib" / "__init__.pyi"
    
    if not pyi_file.exists():
        return {}
    
    with open(pyi_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    exports: Dict[str, Set[str]] = {}
    current_module = None
    
    # Pattern to match module class definitions
    module_pattern = re.compile(r'^class (\w+):')
    class_pattern = re.compile(r'^\s+class (\w+)(?:\(|:)')
    function_pattern = re.compile(r'^\s+def (\w+)\(')
    
    for line in content.split('\n'):
        # Check for module class
        match = module_pattern.match(line)
        if match:
            module_name = match.group(1)
            if module_name in ['element', 'types', 'example', 'terms', 'lat', 'io', 'eq', 'group', 'fplat', 'alg', 'util', 'general_algebra', 'parallel']:
                current_module = module_name
                exports[current_module] = set()
            continue
        
        if current_module:
            # Check for class definitions
            match = class_pattern.match(line)
            if match:
                class_name = match.group(1)
                # Skip Protocol classes - they're type hints only, not Rust exports
                if '(Protocol)' in line or 'Protocol' in line:
                    continue
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

# PyO3 classes present in source but never registered on a Python module.
_UNREGISTERED_PYCLASSES = frozenset({"SmallAlgebra"})


def compare_exports() -> Tuple[bool, List[str]]:
    """Compare the actual wrapper surface with .pyi file exports."""
    runtime_exports = extract_runtime_exports()
    rust_exports = extract_exported_names_from_rust()
    pyi_exports = extract_names_from_pyi()
    source_exports: Dict[str, Set[str]] = {}
    for module in set(rust_exports) | set(runtime_exports or {}):
        names = set(rust_exports.get(module, set()))
        if runtime_exports is not None:
            names |= runtime_exports.get(module, set())
        names -= _UNREGISTERED_PYCLASSES
        source_exports[module] = names
    source_label = "Rust+runtime" if runtime_exports is not None else "Rust"
    
    issues = []
    all_good = True
    
    all_modules = set(source_exports.keys()) | set(pyi_exports.keys())
    
    for module in sorted(all_modules):
        source_names = source_exports.get(module, set())
        pyi_names = pyi_exports.get(module, set())
        
        missing_in_pyi = source_names - pyi_names
        extra_in_pyi = pyi_names - source_names
        
        if missing_in_pyi:
            all_good = False
            issues.append(
                f"Module '{module}': Missing in .pyi ({source_label}): {sorted(missing_in_pyi)}"
            )
        
        if extra_in_pyi:
            issues.append(
                f"Module '{module}': Extra in .pyi (not in {source_label}): {sorted(extra_in_pyi)}"
            )
    
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
    runtime_exports = extract_runtime_exports()
    pyi_exports = extract_names_from_pyi()
    
    print("\nSummary:")
    print(f"  Modules in Rust: {len(rust_exports)}")
    print(f"  Modules in runtime: {len(runtime_exports) if runtime_exports else 'unavailable'}")
    print(f"  Modules in .pyi: {len(pyi_exports)}")
    
    modules = set(rust_exports.keys()) | set(pyi_exports.keys())
    if runtime_exports:
        modules |= set(runtime_exports.keys())
    for module in sorted(modules):
        rust_names = rust_exports.get(module, set()) - _UNREGISTERED_PYCLASSES
        rust_count = len(rust_names)
        pyi_count = len(pyi_exports.get(module, set()))
        runtime_count = len(runtime_exports.get(module, set())) if runtime_exports else "-"
        print(f"  {module}: Rust={rust_count}, runtime={runtime_count}, .pyi={pyi_count}")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())

