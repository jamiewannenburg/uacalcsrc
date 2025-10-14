#!/usr/bin/env python3
"""
Script to analyze task dependencies from task_analysis_results.json and determine
a proper sequence where each task only depends on previously completed tasks.
"""

import json
import re
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Optional

def extract_task_name(task_path: str) -> str:
    """Extract task name from file path."""
    # Extract task name from path like "/home/jamie/Documents/uacalcsrc/tasks/Task 1 - OperationSymbol.md"
    match = re.search(r'Task \d+ - ([^.]+)\.md', task_path)
    if match:
        return match.group(1)
    return task_path.split('/')[-1].replace('.md', '')

def extract_dependencies_from_analysis(analysis_text: str) -> List[str]:
    """Extract dependencies from the analysis text."""
    dependencies = []
    
    # Look for "dependencies_found" in the analysis
    if '"dependencies_found"' in analysis_text:
        # Extract the dependencies array
        deps_match = re.search(r'"dependencies_found":\s*\[(.*?)\]', analysis_text)
        if deps_match:
            deps_str = deps_match.group(1)
            # Parse individual dependencies
            dep_matches = re.findall(r'"([^"]+)"', deps_str)
            dependencies.extend(dep_matches)
    
    return dependencies

def build_dependency_graph(data: List[Dict]) -> Tuple[Dict[str, Set[str]], Dict[str, bool]]:
    """Build dependency graph from task analysis data."""
    graph = defaultdict(set)  # task -> set of dependencies
    completed = {}  # task -> is_completed
    
    for item in data:
        task_path = item.get('task', '')
        task_name = extract_task_name(task_path)
        is_completed = item.get('is_completed', False)
        completed[task_name] = is_completed
        
        # Extract dependencies from structured output
        structured_output = item.get('structured_output', {})
        analysis_text = structured_output.get('result', '')
        
        dependencies = extract_dependencies_from_analysis(analysis_text)
        
        # Add dependencies to graph
        for dep in dependencies:
            graph[task_name].add(dep)
    
    return dict(graph), completed

def topological_sort(graph: Dict[str, Set[str]], completed: Dict[str, bool]) -> List[str]:
    """
    Perform topological sort to determine task execution order.
    Only includes tasks that are not completed.
    """
    # Filter to only incomplete tasks
    incomplete_tasks = {task for task, is_comp in completed.items() if not is_comp}
    
    # Build in-degree count
    in_degree = defaultdict(int)
    for task in incomplete_tasks:
        in_degree[task] = 0
    
    # Calculate in-degrees for incomplete tasks only
    for task in incomplete_tasks:
        for dep in graph.get(task, set()):
            if dep in incomplete_tasks:  # Only count dependencies that are also incomplete
                in_degree[task] += 1
    
    # Initialize queue with tasks that have no dependencies
    queue = deque([task for task in incomplete_tasks if in_degree[task] == 0])
    result = []
    
    while queue:
        current = queue.popleft()
        result.append(current)
        
        # Update in-degrees for tasks that depend on current
        for task in incomplete_tasks:
            if current in graph.get(task, set()):
                in_degree[task] -= 1
                if in_degree[task] == 0:
                    queue.append(task)
    
    # Check for circular dependencies
    if len(result) != len(incomplete_tasks):
        remaining = incomplete_tasks - set(result)
        print(f"Warning: Circular dependencies detected for tasks: {remaining}")
    
    return result

def analyze_dependencies():
    """Main function to analyze dependencies and output sequence."""
    print("Loading task analysis results...")
    
    try:
        with open('/home/jamie/Documents/uacalcsrc/task_analysis_results.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: task_analysis_results.json not found")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return
    
    print(f"Loaded {len(data)} task analysis results")
    
    # Build dependency graph
    print("Building dependency graph...")
    graph, completed = build_dependency_graph(data)
    
    # Count completed vs incomplete tasks
    completed_count = sum(1 for is_comp in completed.values() if is_comp)
    incomplete_count = len(completed) - completed_count
    
    print(f"Found {completed_count} completed tasks and {incomplete_count} incomplete tasks")
    
    # Perform topological sort
    print("Determining task execution sequence...")
    sequence = topological_sort(graph, completed)
    
    # Output results
    print("\n" + "="*80)
    print("TASK EXECUTION SEQUENCE")
    print("="*80)
    print("The following sequence ensures each task only depends on previously completed tasks:")
    print()
    
    for i, task in enumerate(sequence, 1):
        deps = graph.get(task, set())
        incomplete_deps = [dep for dep in deps if not completed.get(dep, True)]
        
        print(f"{i:2d}. {task}")
        if incomplete_deps:
            print(f"     Dependencies: {', '.join(incomplete_deps)}")
        else:
            print(f"     Dependencies: None (or all completed)")
        print()
    
    # Write to file
    output_file = '/home/jamie/Documents/uacalcsrc/task_execution_sequence.txt'
    with open(output_file, 'w') as f:
        f.write("TASK EXECUTION SEQUENCE\n")
        f.write("="*80 + "\n")
        f.write("The following sequence ensures each task only depends on previously completed tasks:\n\n")
        
        for i, task in enumerate(sequence, 1):
            deps = graph.get(task, set())
            incomplete_deps = [dep for dep in deps if not completed.get(dep, True)]
            
            f.write(f"{i:2d}. {task}\n")
            if incomplete_deps:
                f.write(f"     Dependencies: {', '.join(incomplete_deps)}\n")
            else:
                f.write(f"     Dependencies: None (or all completed)\n")
            f.write("\n")
        
        f.write("\nDEPENDENCY ANALYSIS SUMMARY\n")
        f.write("="*80 + "\n")
        f.write(f"Total tasks analyzed: {len(completed)}\n")
        f.write(f"Completed tasks: {completed_count}\n")
        f.write(f"Incomplete tasks: {incomplete_count}\n")
        f.write(f"Tasks in execution sequence: {len(sequence)}\n")
    
    print(f"Results written to: {output_file}")
    
    # Additional analysis
    print("\nDEPENDENCY ANALYSIS SUMMARY")
    print("="*80)
    print(f"Total tasks analyzed: {len(completed)}")
    print(f"Completed tasks: {completed_count}")
    print(f"Incomplete tasks: {incomplete_count}")
    print(f"Tasks in execution sequence: {len(sequence)}")
    
    # Show dependency details
    print("\nDETAILED DEPENDENCY INFORMATION")
    print("="*80)
    for task in sequence:
        deps = graph.get(task, set())
        if deps:
            print(f"{task}:")
            for dep in deps:
                status = "✓" if completed.get(dep, False) else "✗"
                print(f"  - {dep} ({status})")
            print()

if __name__ == "__main__":
    analyze_dependencies()
