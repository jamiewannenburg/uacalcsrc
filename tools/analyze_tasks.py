#!/usr/bin/env python3
"""
Task Implementation Status Analysis Script

This script analyzes each of the 85 task files in the tasks/ directory to verify
what is already implemented and what still needs to be implemented. It checks:
- Rust implementation status
- Python bindings status  
- Java wrapper status
- Testing status
- Dependencies that are blocking implementation

The script updates TASK_STATUS.md with the current status of all tasks.
"""

import os
import re
import subprocess
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TaskAnalyzer:
    def __init__(self, project_root: str = "/home/jamie/Documents/uacalcsrc"):
        self.project_root = Path(project_root)
        self.tasks_dir = self.project_root / "tasks"
        self.java_dir = self.project_root / "org"
        self.rust_src_dir = self.project_root / "src"
        self.python_lib_dir = self.project_root / "uacalc_lib" / "src"
        self.java_wrapper_dir = self.project_root / "java_wrapper" / "src"
        self.task_status_file = self.project_root / "TASK_STATUS.md"
        
        # Verify required directories exist
        if not self.tasks_dir.exists():
            raise FileNotFoundError(f"Tasks directory not found: {self.tasks_dir}")
        if not self.java_dir.exists():
            raise FileNotFoundError(f"Java directory not found: {self.java_dir}")
        if not self.rust_src_dir.exists():
            raise FileNotFoundError(f"Rust source directory not found: {self.rust_src_dir}")
        if not self.python_lib_dir.exists():
            raise FileNotFoundError(f"Python library directory not found: {self.python_lib_dir}")
    
    def parse_task_file(self, task_path: Path) -> Dict:
        """Parse a task file to extract Java file path, dependencies, and status."""
        try:
            with open(task_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract Java file path from the content
            java_file = self.extract_java_file_path(content)
            
            # Extract dependencies
            dependencies = self.extract_dependencies(content)
            
            # Check completion status
            is_completed = self.check_completion_status(content)
            
            return {
                'task_file': str(task_path),
                'java_file': java_file,
                'dependencies': dependencies,
                'is_completed': is_completed,
                'content': content
            }
        except Exception as e:
            logger.error(f"Error parsing task file {task_path}: {e}")
            return None
    
    def extract_java_file_path(self, content: str) -> Optional[str]:
        """Extract Java file path from task content."""
        # Look for patterns like "**Java File:** `org/uacalc/alg/op/Operation.java`"
        pattern = r'\*\*Java File:\*\*\s*`([^`]+\.java)`'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        
        # Fallback: look for any .java file reference
        pattern = r'`([^`]*\.java)`'
        matches = re.findall(pattern, content)
        if matches:
            return matches[0]
        
        return None
    
    def extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from task content."""
        dependencies = []
        
        # Look for dependencies section
        deps_section = re.search(r'### Dependencies\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
        if deps_section:
            deps_text = deps_section.group(1)
            # Extract dependency lines
            dep_lines = re.findall(r'-\s*`([^`]+)`', deps_text)
            dependencies.extend(dep_lines)
        
        return dependencies
    
    def check_completion_status(self, content: str) -> bool:
        """Check if task is marked as completed."""
        # Count checked boxes
        checked_boxes = content.count('- [x]')
        total_boxes = content.count('- [')
        
        # Consider completed if all boxes are checked
        return checked_boxes > 0 and checked_boxes == total_boxes
    
    def check_rust_implementation(self, java_file_path: str) -> Dict[str, bool]:
        """Check if Rust implementation exists for the Java file."""
        # Convert Java path to expected Rust module path
        # e.g., org/uacalc/alg/op/OperationSymbol.java -> alg/op/operation_symbol.rs
        java_path = Path(java_file_path)
        java_name = java_path.stem  # e.g., OperationSymbol
        
        # Convert CamelCase to snake_case
        rust_name = re.sub(r'(?<!^)(?=[A-Z])', '_', java_name).lower()
        
        # Map Java package to Rust module
        package_mapping = {
            'org/uacalc/alg': 'alg',
            'org/uacalc/terms': 'terms', 
            'org/uacalc/eq': 'eq',
            'org/uacalc/util': 'util',
            'org/uacalc/io': 'io',
            'org/uacalc/lat': 'lat',
            'org/uacalc/group': 'group',
            'org/uacalc/element': 'element',
            'org/uacalc/fplat': 'fplat',
            'org/uacalc/example': 'example'
        }
        
        rust_module = None
        for java_pkg, rust_mod in package_mapping.items():
            if java_file_path.startswith(java_pkg):
                rust_module = rust_mod
                break
        
        if not rust_module:
            return {'exists': False, 'path': None, 'reason': 'Unknown package'}
        
        # Check for Rust file
        rust_file_path = self.rust_src_dir / rust_module / f"{rust_name}.rs"
        rust_exists = rust_file_path.exists()
        
        # Check for implementation in mod.rs
        mod_rs_path = self.rust_src_dir / rust_module / "mod.rs"
        mod_rs_contains = False
        if mod_rs_path.exists():
            with open(mod_rs_path, 'r', encoding='utf-8') as f:
                mod_content = f.read()
                mod_rs_contains = java_name.lower() in mod_content.lower() or rust_name in mod_content
        
        return {
            'exists': rust_exists or mod_rs_contains,
            'path': str(rust_file_path) if rust_exists else str(mod_rs_path) if mod_rs_contains else None,
            'reason': 'Found in separate file' if rust_exists else 'Found in mod.rs' if mod_rs_contains else 'Not found'
        }
    
    def check_python_bindings(self, java_file_path: str) -> Dict[str, bool]:
        """Check if Python bindings exist for the Java file."""
        java_path = Path(java_file_path)
        java_name = java_path.stem
        
        # Convert CamelCase to snake_case
        rust_name = re.sub(r'(?<!^)(?=[A-Z])', '_', java_name).lower()
        
        # Map Java package to Python module
        package_mapping = {
            'org/uacalc/alg': 'alg',
            'org/uacalc/terms': 'terms',
            'org/uacalc/eq': 'eq', 
            'org/uacalc/util': 'util',
            'org/uacalc/io': 'io',
            'org/uacalc/lat': 'lat',
            'org/uacalc/group': 'group',
            'org/uacalc/element': 'element',
            'org/uacalc/fplat': 'fplat',
            'org/uacalc/example': 'example'
        }
        
        python_module = None
        for java_pkg, py_mod in package_mapping.items():
            if java_file_path.startswith(java_pkg):
                python_module = py_mod
                break
        
        if not python_module:
            return {'exists': False, 'path': None, 'reason': 'Unknown package'}
        
        # Check for Python bindings file
        python_file_path = self.python_lib_dir / f"{python_module}.rs"
        python_exists = python_file_path.exists()
        
        # Check if the class is exposed in the Python bindings
        python_contains = False
        if python_exists:
            with open(python_file_path, 'r', encoding='utf-8') as f:
                py_content = f.read()
                # Look for PyO3 bindings or class name
                python_contains = (f"Py{java_name}" in py_content or 
                                 java_name in py_content or
                                 rust_name in py_content)
        
        return {
            'exists': python_exists and python_contains,
            'path': str(python_file_path) if python_exists else None,
            'reason': 'Found in Python bindings' if python_exists and python_contains else 'Not found'
        }
    
    def check_java_wrapper(self, java_file_path: str) -> Dict[str, bool]:
        """Check if Java wrapper exists for the Java file."""
        java_path = Path(java_file_path)
        java_name = java_path.stem
        
        # Convert Java path to wrapper path
        # e.g., org/uacalc/alg/op/OperationSymbol.java -> alg/op/OperationSymbolWrapper.java
        wrapper_path = self.java_wrapper_dir / java_file_path.replace('.java', 'Wrapper.java')
        
        wrapper_exists = wrapper_path.exists()
        
        return {
            'exists': wrapper_exists,
            'path': str(wrapper_path) if wrapper_exists else None,
            'reason': 'Found wrapper' if wrapper_exists else 'No wrapper found'
        }
    
    def check_tests(self, java_file_path: str) -> Dict[str, bool]:
        """Check if tests exist for the Java file."""
        java_path = Path(java_file_path)
        java_name = java_path.stem
        
        # Convert CamelCase to snake_case
        rust_name = re.sub(r'(?<!^)(?=[A-Z])', '_', java_name).lower()
        
        # Check for Rust tests
        rust_test_path = self.rust_src_dir / "tests" / f"{rust_name}_tests.rs"
        rust_tests_exist = rust_test_path.exists()
        
        # Check for tests in the module itself
        mod_tests_exist = False
        package_mapping = {
            'org/uacalc/alg': 'alg',
            'org/uacalc/terms': 'terms',
            'org/uacalc/eq': 'eq',
            'org/uacalc/util': 'util',
            'org/uacalc/io': 'io',
            'org/uacalc/lat': 'lat',
            'org/uacalc/group': 'group',
            'org/uacalc/element': 'element',
            'org/uacalc/fplat': 'fplat',
            'org/uacalc/example': 'example'
        }
        
        for java_pkg, rust_mod in package_mapping.items():
            if java_file_path.startswith(java_pkg):
                mod_path = self.rust_src_dir / rust_mod / "mod.rs"
                if mod_path.exists():
                    with open(mod_path, 'r', encoding='utf-8') as f:
                        mod_content = f.read()
                        mod_tests_exist = '#[cfg(test)]' in mod_content and 'mod tests' in mod_content
                break
        
        return {
            'exists': rust_tests_exist or mod_tests_exist,
            'path': str(rust_test_path) if rust_tests_exist else 'In mod.rs' if mod_tests_exist else None,
            'reason': 'Found test file' if rust_tests_exist else 'Found in mod.rs' if mod_tests_exist else 'No tests found'
        }
    
    def analyze_implementation_status(self, task_info: Dict) -> Dict:
        """Analyze the implementation status of a task."""
        java_file = task_info['java_file']
        if not java_file:
            return {
                'success': False,
                'error': 'No Java file found in task'
            }
        
        # Check implementation status
        rust_status = self.check_rust_implementation(java_file)
        python_status = self.check_python_bindings(java_file)
        java_wrapper_status = self.check_java_wrapper(java_file)
        tests_status = self.check_tests(java_file)
        
        # Determine overall status
        rust_impl = rust_status['exists']
        python_impl = python_status['exists']
        java_wrapper_impl = java_wrapper_status['exists']
        tests_impl = tests_status['exists']
        
        # Calculate completion percentage
        total_components = 4  # Rust, Python, Java wrapper, Tests
        completed_components = sum([rust_impl, python_impl, java_wrapper_impl, tests_impl])
        completion_percentage = (completed_components / total_components) * 100
        
        # Determine status
        if completion_percentage == 100:
            status = "complete"
        elif completion_percentage >= 75:
            status = "partially_complete"
        elif completion_percentage >= 25:
            status = "in_progress"
        else:
            status = "not_started"
        
        # Check for blocking dependencies
        dependencies = task_info.get('dependencies', [])
        blocking_deps = []
        
        # For now, we'll mark as blocked if dependencies exist and implementation is not complete
        # This is a simplified check - in a real implementation, you'd check if dependencies are implemented
        if dependencies and completion_percentage < 100:
            status = "blocked"
            blocking_deps = dependencies
        
        return {
            'success': True,
            'task_file': task_info['task_file'],
            'java_file': java_file,
            'status': status,
            'completion_percentage': completion_percentage,
            'rust_implementation': rust_status,
            'python_bindings': python_status,
            'java_wrapper': java_wrapper_status,
            'tests': tests_status,
            'blocking_dependencies': blocking_deps,
            'dependencies': dependencies
        }
    
    def create_task_status_md(self, all_results: List[Dict]) -> str:
        """Create the TASK_STATUS.md file content."""
        # Sort results by task number
        def extract_task_number(task_file: str) -> int:
            match = re.search(r'Task (\d+)', task_file)
            return int(match.group(1)) if match else 999
        
        sorted_results = sorted(all_results, key=lambda x: extract_task_number(x.get('task_file', '')))
        
        # Count statuses
        status_counts = {}
        for result in all_results:
            status = result.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Generate markdown content
        md_content = f"""# UACalc Translation Task Status

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Status | Count | Percentage |
|--------|-------|------------|
"""
        
        total_tasks = len(all_results)
        for status in ['complete', 'partially_complete', 'in_progress', 'blocked', 'not_started']:
            count = status_counts.get(status, 0)
            percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
            md_content += f"| {status.replace('_', ' ').title()} | {count} | {percentage:.1f}% |\n"
        
        md_content += f"""
**Total Tasks:** {total_tasks}

## Task Details

| Task | Java File | Status | Completion | Rust | Python | Java Wrapper | Tests | Blocking Dependencies |
|------|-----------|--------|------------|------|--------|--------------|-------|----------------------|
"""
        
        for result in sorted_results:
            task_file = result.get('task_file', '')
            task_name = Path(task_file).stem if task_file else 'Unknown'
            java_file = result.get('java_file', 'N/A')
            status = result.get('status', 'unknown')
            completion = f"{result.get('completion_percentage', 0):.0f}%"
            
            rust_status = "✅" if result.get('rust_implementation', {}).get('exists', False) else "❌"
            python_status = "✅" if result.get('python_bindings', {}).get('exists', False) else "❌"
            java_wrapper_status = "✅" if result.get('java_wrapper', {}).get('exists', False) else "❌"
            tests_status = "✅" if result.get('tests', {}).get('exists', False) else "❌"
            
            blocking_deps = result.get('blocking_dependencies', [])
            blocking_str = ", ".join(blocking_deps[:2])  # Show first 2 dependencies
            if len(blocking_deps) > 2:
                blocking_str += f" (+{len(blocking_deps) - 2} more)"
            
            md_content += f"| {task_name} | `{java_file}` | {status.replace('_', ' ').title()} | {completion} | {rust_status} | {python_status} | {java_wrapper_status} | {tests_status} | {blocking_str} |\n"
        
        md_content += """
## Status Definitions

- **Complete**: All components implemented (Rust, Python bindings, Java wrapper, Tests)
- **Partially Complete**: 75%+ components implemented
- **In Progress**: 25-74% components implemented  
- **Blocked**: Has dependencies that prevent implementation
- **Not Started**: Less than 25% components implemented

## Implementation Components

- **Rust**: Core Rust implementation
- **Python**: Python bindings via PyO3
- **Java Wrapper**: Java CLI wrapper for testing
- **Tests**: Rust test suite

## Notes

- Tasks are ordered by dependency count (lowest first)
- Blocking dependencies are shown for tasks that cannot proceed
- Completion percentage is based on the 4 main components
- Status is automatically determined based on implementation progress
"""
        
        return md_content
    
    def process_single_task(self, task_path: Path) -> Dict:
        """Process a single task file."""
        logger.info(f"Processing task: {task_path.name}")
        
        # Parse task file to get basic info
        task_info = self.parse_task_file(task_path)
        if not task_info:
            return {
                'task_file': str(task_path),
                'success': False,
                'error': 'Failed to parse task file'
            }
        
        # Analyze implementation status
        analysis_result = self.analyze_implementation_status(task_info)
        
        return analysis_result
    
    def get_all_task_files(self) -> List[Path]:
        """Get all task files in the tasks directory."""
        task_files = []
        for task_file in self.tasks_dir.glob("*.md"):
            if task_file.is_file():
                task_files.append(task_file)
        
        # Sort by task number for consistent processing
        task_files.sort(key=lambda x: int(re.search(r'Task (\d+)', x.name).group(1)) if re.search(r'Task (\d+)', x.name) else 0)
        return task_files
    

    def run_analysis(self, parallel: int = 3, task_filter: Optional[str] = None, dry_run: bool = False, rerun: bool = False):
        """Run the complete task analysis with batched parallel processing."""
        logger.info("Starting task implementation status analysis...")
        
        # Get all task files
        task_files = self.get_all_task_files()
        
        # Apply filter if specified
        if task_filter:
            task_files = [f for f in task_files if task_filter in f.name]
        
        logger.info(f"Found {len(task_files)} task files to process")
        
        if dry_run:
            logger.info("DRY RUN - Would process the following tasks:")
            for task_file in task_files:
                task_info = self.parse_task_file(task_file)
                if task_info:
                    logger.info(f"  - {task_file.name}: {task_info['java_file']}")
            return
        
        # Process tasks in batches
        results = []
        start_time = time.time()
        
        if parallel > 1:
            # Process in batches of parallel workers
            batch_size = parallel
            total_batches = (len(task_files) + batch_size - 1) // batch_size
            
            logger.info(f"Processing {len(task_files)} tasks in {total_batches} batches of {batch_size} parallel workers")
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(task_files))
                batch_files = task_files[start_idx:end_idx]
                
                logger.info(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch_files)} tasks)")
                
                # Process batch in parallel
                with ThreadPoolExecutor(max_workers=parallel) as executor:
                    future_to_task = {
                        executor.submit(self.process_single_task, task_file): task_file 
                        for task_file in batch_files
                    }
                    
                    batch_results = []
                    for future in as_completed(future_to_task):
                        task_file = future_to_task[future]
                        try:
                            result = future.result()
                            batch_results.append(result)
                            results.append(result)
                        except Exception as e:
                            logger.error(f"Error processing {task_file}: {e}")
                            error_result = {
                                'task_file': str(task_file),
                                'success': False,
                                'error': str(e)
                            }
                            batch_results.append(error_result)
                            results.append(error_result)
                    
                    # Log batch results
                    batch_successful = sum(1 for r in batch_results if r.get('success', False))
                    batch_failed = len(batch_results) - batch_successful
                    logger.info(f"Batch {batch_num + 1} complete: {batch_successful} successful, {batch_failed} failed")
                    
                    # Small delay between batches to avoid overwhelming the system
                    if batch_num < total_batches - 1:  # Don't delay after the last batch
                        logger.info("Waiting 2 seconds before next batch...")
                        time.sleep(2)
        else:
            # Sequential processing
            logger.info("Processing tasks sequentially...")
            for i, task_file in enumerate(task_files, 1):
                logger.info(f"Processing task {i}/{len(task_files)}: {task_file.name}")
                result = self.process_single_task(task_file)
                results.append(result)
        
        # Generate TASK_STATUS.md file
        logger.info("Generating TASK_STATUS.md file...")
        md_content = self.create_task_status_md(results)
        
        with open(self.task_status_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"TASK_STATUS.md file created at {self.task_status_file}")
        
        # Report final results
        elapsed_time = time.time() - start_time
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        
        # Count statuses
        status_counts = {}
        for result in results:
            status = result.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        logger.info(f"Analysis complete in {elapsed_time:.2f} seconds")
        logger.info(f"Total results: {successful} successful, {failed} failed")
        logger.info("Status breakdown:")
        for status, count in status_counts.items():
            logger.info(f"  {status.replace('_', ' ').title()}: {count}")
        
        return results

def main():
    parser = argparse.ArgumentParser(description="Analyze UACalc translation task implementation status")
    parser.add_argument("--parallel", "-p", type=int, default=3, 
                       help="Number of parallel processes per batch (default: 3)")
    parser.add_argument("--task-filter", "-f", type=str, 
                       help="Only process tasks matching this pattern")
    parser.add_argument("--dry-run", "-d", action="store_true",
                       help="Show what would be done without executing")
    parser.add_argument("--rerun", "-r", action="store_true",
                       help="Rerun all tasks, including those already completed")
    parser.add_argument("--project-root", type=str, default="/home/jamie/Documents/uacalcsrc",
                       help="Project root directory")
    
    args = parser.parse_args()
    
    try:
        analyzer = TaskAnalyzer(args.project_root)
        
        analyzer.run_analysis(
            parallel=args.parallel,
            task_filter=args.task_filter,
            dry_run=args.dry_run,
            rerun=args.rerun
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
