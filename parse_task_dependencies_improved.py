#!/usr/bin/env python3
"""
Improved script to parse dependencies from task files and determine proper execution sequence.
This script reads the actual task files to extract dependencies listed in them.
"""

import os
import re
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Optional

def extract_task_name_from_filename(filename: str) -> str:
    """Extract task name from filename like 'Task 1 - OperationSymbol.md'."""
    match = re.search(r'Task \d+ - ([^.]+)\.md', filename)
    if match:
        return match.group(1)
    return filename.replace('.md', '')

def extract_task_number_from_filename(filename: str) -> int:
    """Extract task number from filename like 'Task 1 - OperationSymbol.md'."""
    match = re.search(r'Task (\d+)', filename)
    if match:
        return int(match.group(1))
    return 0

def parse_dependencies_from_task_file(filepath: str) -> Tuple[List[str], int]:
    """
    Parse dependencies from a task file.
    Returns (dependencies_list, dependency_count)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return [], 0
    
    dependencies = []
    dependency_count = 0
    
    # Look for dependency count in the header
    dep_count_match = re.search(r'\*\*Dependencies:\*\*\s*(\d+)', content)
    if dep_count_match:
        dependency_count = int(dep_count_match.group(1))
    
    # Parse different types of dependency sections
    dependencies.extend(parse_direct_dependencies(content))
    dependencies.extend(parse_task_references(content))
    dependencies.extend(parse_class_references(content))
    dependencies.extend(parse_implementation_order(content))
    
    # Remove duplicates and clean up
    dependencies = list(set(dependencies))
    dependencies = [dep.strip() for dep in dependencies if dep.strip()]
    
    return dependencies, dependency_count

def parse_direct_dependencies(content: str) -> List[str]:
    """Parse direct dependencies from content."""
    dependencies = []
    
    # Look for "Direct Dependencies" section
    direct_deps_match = re.search(r'### Direct Dependencies(.*?)(?=###|\Z)', content, re.DOTALL | re.IGNORECASE)
    if direct_deps_match:
        section_content = direct_deps_match.group(1)
        # Look for task references like "OperationSymbol (Task 1)"
        task_refs = re.findall(r'([A-Z][a-zA-Z0-9]+)\s*\(Task\s*(\d+)\)', section_content)
        for class_name, task_num in task_refs:
            dependencies.append(f"Task {task_num}: {class_name}")
    
    return dependencies

def parse_task_references(content: str) -> List[str]:
    """Parse task references from content."""
    dependencies = []
    
    # Look for task references like "Task 1: OperationSymbol" or "Task 1 - OperationSymbol"
    task_patterns = [
        r'Task (\d+):\s*([^-\n]+)',
        r'Task (\d+)\s*-\s*([^-\n]+)',
        r'Task (\d+)\s*([^-\n]+)',
    ]
    
    for pattern in task_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            task_num, task_name = match
            task_name = task_name.strip()
            # Skip if it's just a number or very short
            if len(task_name) > 2 and not task_name.isdigit():
                dependencies.append(f"Task {task_num}: {task_name}")
    
    return dependencies

def parse_class_references(content: str) -> List[str]:
    """Parse class references from content."""
    dependencies = []
    
    # Look for class names in backticks or bold
    class_patterns = [
        r'`([A-Z][a-zA-Z0-9]+)`',  # Backtick quoted classes
        r'\*\*([A-Z][a-zA-Z0-9]+)\*\*',  # Bold classes
    ]
    
    for pattern in class_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # Filter out common words that aren't class names
            if match not in ['Java', 'Rust', 'Task', 'Note', 'Type', 'Key', 'Core', 'Main', 'All', 'The', 'This', 'For', 'And', 'But', 'Not', 'Are', 'Can', 'Has', 'Was', 'Will', 'Should', 'Must', 'May', 'Could', 'Would', 'Might', 'Class', 'Method', 'Interface', 'Abstract', 'Public', 'Private', 'Static', 'Final', 'Void', 'Int', 'Long', 'Double', 'Float', 'Boolean', 'String', 'Object', 'List', 'Set', 'Map', 'Array', 'Vector', 'Result', 'Option', 'Some', 'None', 'Ok', 'Err']:
                dependencies.append(match)
    
    return dependencies

def parse_implementation_order(content: str) -> List[str]:
    """Parse implementation order sections."""
    dependencies = []
    
    # Look for "Implementation Order" or "Prerequisites" sections
    order_patterns = [
        r'### Dependencies Implementation Order(.*?)(?=###|\Z)',
        r'### Prerequisites(.*?)(?=###|\Z)',
        r'### Blocking Dependencies(.*?)(?=###|\Z)',
    ]
    
    for pattern in order_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            section_content = match
            # Look for task references
            task_refs = re.findall(r'Task (\d+):\s*([^-\n]+)', section_content)
            for task_num, task_name in task_refs:
                dependencies.append(f"Task {task_num}: {task_name.strip()}")
    
    return dependencies

def build_dependency_graph(tasks_dir: str) -> Tuple[Dict[str, Set[str]], Dict[str, int], Dict[str, str]]:
    """
    Build dependency graph from task files.
    Returns (graph, task_numbers, task_files)
    """
    graph = defaultdict(set)
    task_numbers = {}
    task_files = {}
    
    if not os.path.exists(tasks_dir):
        print(f"Tasks directory not found: {tasks_dir}")
        return dict(graph), task_numbers, task_files
    
    # Read all task files
    for filename in os.listdir(tasks_dir):
        if filename.startswith('Task ') and filename.endswith('.md'):
            filepath = os.path.join(tasks_dir, filename)
            task_name = extract_task_name_from_filename(filename)
            task_number = extract_task_number_from_filename(filename)
            
            task_numbers[task_name] = task_number
            task_files[task_name] = filepath
            
            # Parse dependencies
            dependencies, dep_count = parse_dependencies_from_task_file(filepath)
            
            # Add dependencies to graph
            for dep in dependencies:
                # Try to map dependency to task name
                dep_task_name = map_dependency_to_task_name(dep, task_numbers)
                if dep_task_name and dep_task_name != task_name:
                    graph[task_name].add(dep_task_name)
    
    return dict(graph), task_numbers, task_files

def map_dependency_to_task_name(dependency: str, task_numbers: Dict[str, int]) -> Optional[str]:
    """Map a dependency string to a task name."""
    # If it's already a task reference like "Task 1: OperationSymbol"
    task_match = re.search(r'Task (\d+):\s*([^-\n]+)', dependency)
    if task_match:
        task_num = int(task_match.group(1))
        task_name = task_match.group(2).strip()
        # Find the actual task name in our list
        for name, num in task_numbers.items():
            if num == task_num:
                return name
        return task_name
    
    # If it's just a class name, try to find matching task
    class_name = dependency.strip()
    for task_name in task_numbers.keys():
        if class_name.lower() in task_name.lower() or task_name.lower() in class_name.lower():
            return task_name
    
    return None

def topological_sort(graph: Dict[str, Set[str]], task_numbers: Dict[str, int]) -> List[str]:
    """
    Perform topological sort to determine task execution order.
    """
    # Build in-degree count
    in_degree = defaultdict(int)
    for task in task_numbers.keys():
        in_degree[task] = 0
    
    # Calculate in-degrees
    for task in task_numbers.keys():
        for dep in graph.get(task, set()):
            if dep in task_numbers:
                in_degree[task] += 1
    
    # Initialize queue with tasks that have no dependencies
    queue = deque([task for task in task_numbers.keys() if in_degree[task] == 0])
    result = []
    
    while queue:
        current = queue.popleft()
        result.append(current)
        
        # Update in-degrees for tasks that depend on current
        for task in task_numbers.keys():
            if current in graph.get(task, set()):
                in_degree[task] -= 1
                if in_degree[task] == 0:
                    queue.append(task)
    
    # Check for circular dependencies
    if len(result) != len(task_numbers):
        remaining = set(task_numbers.keys()) - set(result)
        print(f"Warning: Circular dependencies detected for tasks: {remaining}")
    
    return result

def main():
    """Main function to analyze task dependencies."""
    tasks_dir = '/home/jamie/Documents/uacalcsrc/tasks'
    
    print("Parsing task files for dependencies...")
    
    # Build dependency graph
    graph, task_numbers, task_files = build_dependency_graph(tasks_dir)
    
    print(f"Found {len(task_numbers)} tasks")
    
    # Perform topological sort
    print("Determining task execution sequence...")
    sequence = topological_sort(graph, task_numbers)
    
    # Output results
    print("\n" + "="*80)
    print("TASK EXECUTION SEQUENCE (from task files)")
    print("="*80)
    print("The following sequence ensures each task only depends on previously completed tasks:")
    print()
    
    for i, task in enumerate(sequence, 1):
        task_num = task_numbers.get(task, 0)
        deps = graph.get(task, set())
        
        print(f"{i:2d}. Task {task_num:2d}: {task}")
        if deps:
            dep_list = []
            for dep in sorted(deps, key=lambda x: task_numbers.get(x, 999)):
                dep_num = task_numbers.get(dep, 0)
                dep_list.append(f"Task {dep_num}: {dep}")
            print(f"     Dependencies: {', '.join(dep_list)}")
        else:
            print(f"     Dependencies: None")
        print()
    
    # Write to file
    output_file = '/home/jamie/Documents/uacalcsrc/task_execution_sequence_corrected.txt'
    with open(output_file, 'w') as f:
        f.write("TASK EXECUTION SEQUENCE (from task files)\n")
        f.write("="*80 + "\n")
        f.write("The following sequence ensures each task only depends on previously completed tasks:\n\n")
        
        for i, task in enumerate(sequence, 1):
            task_num = task_numbers.get(task, 0)
            deps = graph.get(task, set())
            
            f.write(f"{i:2d}. Task {task_num:2d}: {task}\n")
            if deps:
                dep_list = []
                for dep in sorted(deps, key=lambda x: task_numbers.get(x, 999)):
                    dep_num = task_numbers.get(dep, 0)
                    dep_list.append(f"Task {dep_num}: {dep}")
                f.write(f"     Dependencies: {', '.join(dep_list)}\n")
            else:
                f.write(f"     Dependencies: None\n")
            f.write("\n")
        
        f.write("\nDEPENDENCY ANALYSIS SUMMARY\n")
        f.write("="*80 + "\n")
        f.write(f"Total tasks analyzed: {len(task_numbers)}\n")
        f.write(f"Tasks with dependencies: {len([t for t in task_numbers.keys() if graph.get(t, set())])}\n")
        f.write(f"Tasks without dependencies: {len([t for t in task_numbers.keys() if not graph.get(t, set())])}\n")
        f.write(f"Tasks in execution sequence: {len(sequence)}\n")
    
    print(f"Results written to: {output_file}")
    
    # Show dependency statistics
    tasks_with_deps = [t for t in task_numbers.keys() if graph.get(t, set())]
    tasks_without_deps = [t for t in task_numbers.keys() if not graph.get(t, set())]
    
    print("\nDEPENDENCY ANALYSIS SUMMARY")
    print("="*80)
    print(f"Total tasks analyzed: {len(task_numbers)}")
    print(f"Tasks with dependencies: {len(tasks_with_deps)}")
    print(f"Tasks without dependencies: {len(tasks_without_deps)}")
    print(f"Tasks in execution sequence: {len(sequence)}")
    
    # Show tasks with most dependencies
    if tasks_with_deps:
        print("\nTASKS WITH MOST DEPENDENCIES:")
        print("-" * 40)
        sorted_by_deps = sorted(tasks_with_deps, key=lambda x: len(graph.get(x, set())), reverse=True)
        for task in sorted_by_deps[:10]:  # Top 10
            task_num = task_numbers.get(task, 0)
            dep_count = len(graph.get(task, set()))
            print(f"Task {task_num:2d}: {task} ({dep_count} dependencies)")

if __name__ == "__main__":
    main()
