#!/usr/bin/env python3
"""
Generate a comprehensive task list for translating UACalc Java library to Rust/Python.

This script uses the dependency analysis to create an ordered list of translation tasks,
where each task translates a single Java file to Rust with Python bindings, creates
a Java CLI wrapper, and implements comprehensive tests.

Tasks are ordered by dependency: files with no dependencies come first, building up
to files with many dependencies.
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple, Set, Dict

# Packages to exclude (UI-related and example packages)
EXCLUDED_PACKAGES = {
    "org.uacalc.ui",
    "org.uacalc.ui.table",
    "org.uacalc.ui.tm",
    "org.uacalc.ui.util",
    "org.uacalc.nbui",
    "org.uacalc.example",
}

# Special files to skip
EXCLUDED_FILES = {
    "org.uacalc.fplat.package-info",  # Just a package-info file
}


def should_include_class(class_name: str) -> bool:
    """Check if a class should be included in the task list."""
    if class_name in EXCLUDED_FILES:
        return False
    
    # Check if class belongs to excluded package
    for pkg in EXCLUDED_PACKAGES:
        if class_name.startswith(pkg + "."):
            return False
    
    return True


def get_class_package(class_name: str) -> str:
    """Extract package name from class name."""
    parts = class_name.split(".")
    return ".".join(parts[:-1])


def get_class_simple_name(class_name: str) -> str:
    """Extract simple class name from fully qualified name."""
    return class_name.split(".")[-1]


def get_file_path(class_name: str) -> str:
    """Convert class name to file path."""
    return class_name.replace(".", "/") + ".java"


def get_rust_module_path(class_name: str) -> str:
    """Convert class name to Rust module path."""
    parts = class_name.split(".")
    # Skip "org.uacalc" prefix
    if len(parts) > 2 and parts[0] == "org" and parts[1] == "uacalc":
        parts = parts[2:]
    return "::".join(parts)


def count_public_methods(java_file_path: Path) -> int:
    """Estimate number of public methods in a Java file."""
    if not java_file_path.exists():
        return 0
    
    try:
        content = java_file_path.read_text()
        # Simple heuristic: count "public" occurrences
        # Subtract 1 for class declaration
        return max(0, content.count("public ") - 1)
    except:
        return 0


def generate_task_markdown(
    task_num: int,
    class_name: str,
    dependency_count: int,
    dependencies: List[str],
    base_path: Path
) -> str:
    """Generate markdown for a single task."""
    simple_name = get_class_simple_name(class_name)
    package = get_class_package(class_name)
    file_path = get_file_path(class_name)
    rust_path = get_rust_module_path(class_name)
    
    # Count public methods
    java_file = base_path / file_path
    method_count = count_public_methods(java_file)
    
    # Filter dependencies to only included classes
    included_deps = [d for d in dependencies if should_include_class(d)]
    
    md = f"""
## Task {task_num}: Translate `{simple_name}`

**Java File:** `{file_path}`  
**Package:** `{package}`  
**Rust Module:** `{rust_path}`  
**Dependencies:** {dependency_count} ({len(included_deps)} non-UI/example)  
**Estimated Public Methods:** ~{method_count}

### Description
Translate the Java class `{class_name}` to Rust with Python bindings.

### Dependencies
"""
    
    if included_deps:
        md += "This class depends on:\n"
        for dep in included_deps[:10]:  # Show first 10
            md += f"- `{dep}`\n"
        if len(included_deps) > 10:
            md += f"- ... and {len(included_deps) - 10} more\n"
    else:
        md += "No dependencies on other UACalc classes (leaf node).\n"
    
    md += """
### Implementation Steps

1. **Analyze Java Implementation**
   - Read and understand the Java source code
   - Identify all public methods and their signatures
   - Note any special patterns (interfaces, abstract classes, etc.)
   - Identify dependencies on other UACalc classes

2. **Design Rust Translation**
   - Determine if Java interfaces should become Rust traits
   - Design struct/enum representations matching Java semantics
   - Plan for Rust idioms (Option instead of null, Result for errors, etc.)
   - Ensure all public methods are translated

3. **Implement Rust Code**
   - Create Rust module structure
   - Implement all public methods
   - Add comprehensive documentation
   - Follow Rust naming conventions (snake_case)

4. **Create Python Bindings (PyO3)**
   - Expose all public methods to Python
   - Use appropriate PyO3 types (PyResult, etc.)
   - Add Python docstrings

5. **Create Java CLI Wrapper**
   - Create wrapper in `java_wrapper/src/` matching package structure
   - Implement `main` method accepting command-line arguments
   - Expose all public methods through CLI commands
   - Output results in JSON/text format for comparison

6. **Write Rust Tests**
   - Test all public methods
   - Add tests with timeouts (slightly longer than Java completion times)
   - Test edge cases and error conditions
   - Compare results against Java CLI wrapper output

7. **Write Python Tests**
   - Test all public methods through Python bindings
   - Compare results against Java CLI wrapper output
   - Verify Python API matches Rust API

8. **Verification**
   - Run all tests and ensure they pass
   - Verify outputs match Java implementation exactly
   - Check test coverage for all public methods

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete

---
"""
    return md


def main():
    """Generate the complete task list."""
    # Load dependency analysis
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    dep_file = project_root / "dependency_analysis" / "dependencies.json"
    
    if not dep_file.exists():
        print(f"Error: Dependency file not found: {dep_file}", file=sys.stderr)
        sys.exit(1)
    
    with open(dep_file) as f:
        data = json.load(f)
    
    # Extract dependency hierarchy
    hierarchy = data.get("dependency_hierarchy", {})
    files_by_dep = hierarchy.get("files_by_dependency_count", [])
    class_dependencies = data.get("class_dependencies", {})
    
    # Filter to only classes (not packages) and exclude UI/example packages
    tasks = []
    for item in files_by_dep:
        if len(item) != 3:
            continue
        
        class_name, dep_count, item_type = item
        
        if item_type != "class":
            continue
        
        if not should_include_class(class_name):
            continue
        
        dependencies = class_dependencies.get(class_name, [])
        tasks.append((class_name, dep_count, dependencies))
    
    # Generate plan format
    output = f"""<!-- 4d9e87d0-d5e0-4887-af72-83cb11148076 ce2ef38c-4a0a-47e6-b19f-d4041c1bb5da -->
# UACalc Rust/Python Translation Plan

## Overview

This plan contains the ordered list of translation tasks for converting the UACalc Java library to Rust with Python bindings. Tasks are ordered by dependency count to ensure foundational classes are translated before dependent classes.

## Translation Strategy

### Approach
- Direct Java-to-Rust translation maintaining exact semantics
- Use Rust idioms where appropriate (traits for interfaces, Result/Option, etc.)
- All public methods must be translated and tested
- Output must match Java implementation exactly

### Testing Strategy
- Rust tests for all public methods with timeouts
- Python binding tests comparing against Java
- Java CLI wrappers for ground truth comparison
- Global memory limit configurable from Python

### Excluded Packages
The following packages are **excluded** from this plan:
- `org.uacalc.ui.*` - UI components (not needed for core library)
- `org.uacalc.nbui.*` - NetBeans UI components
- `org.uacalc.example.*` - Example/demo classes (NOTE: To be implemented later)

## Translation Tasks

"""
    
    for idx, (class_name, dep_count, dependencies) in enumerate(tasks, 1):
        output += generate_task_markdown(
            idx, class_name, dep_count, dependencies, project_root
        )
    
    # Add summary section
    dep_counts = {}
    for _, dep_count, _ in tasks:
        dep_counts[dep_count] = dep_counts.get(dep_count, 0) + 1
    
    output += f"""
## Summary

- **Total Tasks**: {len(tasks)}
- **0 Dependencies**: {dep_counts.get(0, 0)} classes
- **1-2 Dependencies**: {sum(dep_counts.get(i, 0) for i in range(1, 3))} classes
- **3-5 Dependencies**: {sum(dep_counts.get(i, 0) for i in range(3, 6))} classes
- **6+ Dependencies**: {sum(dep_counts.get(i, 0) for i in range(6, max(dep_counts.keys()) + 1))} classes

## Notes

- Each task includes analysis, implementation, testing, and verification phases
- All tasks are designed to be LLM-executable with clear acceptance criteria
- Tasks are ordered by dependency count to ensure dependencies are available when needed
- Java CLI wrappers provide ground truth for comparison testing
"""
    
    # Write output to plan file
    output_file = project_root / "TRANSLATION_TASKS.md"
    output_file.write_text(output)
    
    print(f"Generated {len(tasks)} tasks")
    print(f"Output written to: {output_file}")
    
    # Print summary statistics
    print(f"\nTask Distribution by Dependency Count:")
    for dep_count in sorted(dep_counts.keys())[:10]:
        count = dep_counts[dep_count]
        print(f"  {dep_count} dependencies: {count} tasks")
    
    if len(dep_counts) > 10:
        print(f"  ... and {len(dep_counts) - 10} more dependency levels")


if __name__ == "__main__":
    main()

