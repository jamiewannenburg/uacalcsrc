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
    
    def build_agent_prompt(self, task_info: Dict) -> str:
        """Build comprehensive prompt for cursor-agent to analyze implementation status."""
        task_file = task_info['task_file']
        java_file = task_info['java_file']
        is_completed = task_info['is_completed']
        
        prompt = f"""You are a Rust translation expert analyzing a Java-to-Rust translation task. Your job is to analyze the current implementation status and provide detailed status information.

## Your Task:
1. Read and analyze the task file: {task_file}
2. Read and analyze the Java file: {java_file}
3. Check the current implementation status in the codebase
4. Update the task file with current implementation status
5. Provide structured status information

## Analysis Requirements:

### 1. Implementation Status Verification
- Check if Rust implementation exists in src/ directory
- Check if Python bindings exist in uacalc_lib/src/ directory  
- Check if Java wrapper exists in java_wrapper/src/ directory
- Check if tests exist (either in separate test files or in mod.rs)
- Verify the quality and completeness of each component

### 2. Dependency Analysis
- Parse Java imports to identify UACalc dependencies
- Check if dependencies are implemented in the codebase
- Determine if this task is blocked by missing dependencies
- Identify what needs to be implemented before this task can proceed

### 3. Status Determination
Based on implementation status, determine:
- **Complete**: All 4 components implemented (Rust, Python, Java wrapper, Tests)
- **Partially Complete**: 75%+ components implemented
- **In Progress**: 25-74% components implemented
- **Blocked**: Has dependencies that prevent implementation
- **Not Started**: Less than 25% components implemented

### 4. Task File Updates
- Update the task file with current implementation status
- Mark acceptance criteria as complete/incomplete based on actual implementation
- Add detailed status information and recommendations
- Remove outdated or incorrect information

## Output Requirements:
1. Update the task file with current implementation status
2. Return structured JSON output with your findings
3. Provide detailed status breakdown for each component
4. Include blocking dependencies if any
5. Give recommendations for next steps

## Files to Analyze:
- Task file: {task_file}
- Java file: {java_file}
- Rust source: src/ directory
- Python bindings: uacalc_lib/src/ directory
- Java wrappers: java_wrapper/src/ directory

Begin your analysis and update the task file accordingly. Return your findings in JSON format with the following structure:
{{
  "success": true/false,
  "analysis": {{
    "java_file": "{java_file}",
    "status": "complete|partially_complete|in_progress|blocked|not_started",
    "completion_percentage": 0-100,
    "rust_implementation": {{
      "exists": true/false,
      "path": "path/to/implementation",
      "quality": "excellent|good|basic|poor",
      "notes": "implementation notes"
    }},
    "python_bindings": {{
      "exists": true/false,
      "path": "path/to/bindings", 
      "quality": "excellent|good|basic|poor",
      "notes": "bindings notes"
    }},
    "java_wrapper": {{
      "exists": true/false,
      "path": "path/to/wrapper",
      "quality": "excellent|good|basic|poor", 
      "notes": "wrapper notes"
    }},
    "tests": {{
      "exists": true/false,
      "path": "path/to/tests",
      "quality": "excellent|good|basic|poor",
      "notes": "test notes"
    }},
    "blocking_dependencies": ["list", "of", "blocking", "dependencies"],
    "ready_dependencies": ["list", "of", "ready", "dependencies"],
    "recommendations": "detailed recommendations for next steps"
  }},
  "task_file_updated": true/false,
  "changes_made": "description of changes made to task file"
}}"""

        return prompt
    
    def spawn_cursor_agent(self, task_file: str, prompt: str) -> Tuple[bool, str]:
        """Spawn cursor-agent for a single task using headless mode."""
        try:
            # Change to project root directory
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            # Build cursor-agent command using headless syntax
            cmd = [
                "cursor-agent",  # Now available in PATH
                "-p",  # Enable print mode for non-interactive execution
                "--force",  # Allow file modifications without confirmation
                "--output-format", "json",  # Set output format to JSON for structured output
                prompt  # Provide the prompt (includes file paths and context)
            ]
            
            logger.info(f"Spawning cursor-agent for {task_file}")
            
            # Execute cursor-agent
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=900  # 15 minute timeout per task
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully processed {task_file}")
                return True, result.stdout
            else:
                logger.error(f"cursor-agent failed for {task_file}: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            logger.error(f"cursor-agent timed out for {task_file}")
            return False, "Timeout"
        except Exception as e:
            logger.error(f"Error running cursor-agent for {task_file}: {e}")
            return False, str(e)
        finally:
            os.chdir(original_cwd)
    
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
            
            # Extract component status from cursor-agent analysis
            rust_impl = result.get('rust_implementation', {})
            python_impl = result.get('python_bindings', {})
            java_wrapper_impl = result.get('java_wrapper', {})
            tests_impl = result.get('tests', {})
            
            rust_status = "✅" if rust_impl.get('exists', False) else "❌"
            python_status = "✅" if python_impl.get('exists', False) else "❌"
            java_wrapper_status = "✅" if java_wrapper_impl.get('exists', False) else "❌"
            tests_status = "✅" if tests_impl.get('exists', False) else "❌"
            
            # Add quality indicators if available
            if rust_impl.get('quality'):
                rust_status += f" ({rust_impl['quality']})"
            if python_impl.get('quality'):
                python_status += f" ({python_impl['quality']})"
            if java_wrapper_impl.get('quality'):
                java_wrapper_status += f" ({java_wrapper_impl['quality']})"
            if tests_impl.get('quality'):
                tests_status += f" ({tests_impl['quality']})"
            
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
        
        # Build prompt for cursor-agent
        prompt = self.build_agent_prompt(task_info)
        
        # Spawn cursor-agent
        success, output = self.spawn_cursor_agent(str(task_path), prompt)
        
        # Try to parse JSON output if successful
        structured_output = None
        if success and output:
            try:
                structured_output = json.loads(output)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON output for {task_path.name}")
                structured_output = {"raw_output": output}
        
        # Extract status information from structured output
        if structured_output and structured_output.get('success'):
            analysis = structured_output.get('analysis', {})
            return {
                'task_file': str(task_path),
                'success': True,
                'java_file': task_info['java_file'],
                'status': analysis.get('status', 'unknown'),
                'completion_percentage': analysis.get('completion_percentage', 0),
                'rust_implementation': analysis.get('rust_implementation', {}),
                'python_bindings': analysis.get('python_bindings', {}),
                'java_wrapper': analysis.get('java_wrapper', {}),
                'tests': analysis.get('tests', {}),
                'blocking_dependencies': analysis.get('blocking_dependencies', []),
                'ready_dependencies': analysis.get('ready_dependencies', []),
                'recommendations': analysis.get('recommendations', ''),
                'task_file_updated': structured_output.get('task_file_updated', False),
                'changes_made': structured_output.get('changes_made', ''),
                'structured_output': structured_output
            }
        else:
            return {
                'task_file': str(task_path),
                'success': False,
                'java_file': task_info['java_file'],
                'error': output if not success else 'Failed to parse analysis',
                'structured_output': structured_output
            }
    
    def get_all_task_files(self) -> List[Path]:
        """Get all task files in the tasks directory."""
        task_files = []
        for task_file in self.tasks_dir.glob("*.md"):
            if task_file.is_file():
                task_files.append(task_file)
        
        # Sort by task number for consistent processing
        task_files.sort(key=lambda x: int(re.search(r'Task (\d+)', x.name).group(1)) if re.search(r'Task (\d+)', x.name) else 0)
        return task_files
    
    def load_existing_results(self) -> Dict[str, Dict]:
        """Load existing results from task_analysis_results.json."""
        results_file = self.project_root / "task_analysis" / "task_analysis_results.json"
        if not results_file.exists():
            return {}
        
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            # Convert list to dict keyed by task path, keeping only the last occurrence of each task
            task_results = {}
            for result in results:
                task_path = result.get('task_file')
                if task_path:
                    task_results[task_path] = result
            
            return task_results
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to load existing results: {e}")
            return {}
    
    def is_task_failed(self, task_path: str, existing_results: Dict[str, Dict]) -> bool:
        """Check if a task failed based on existing results."""
        if task_path not in existing_results:
            return False
        
        result = existing_results[task_path]
        return result.get('success', True) == False
    
    def save_results_incrementally(self, new_results: List[Dict], existing_results: Dict[str, Dict]):
        """Save results incrementally by merging with existing results."""
        results_file = self.project_root / "task_analysis" / "task_analysis_results.json"
        
        # Create directory if it doesn't exist
        results_file.parent.mkdir(exist_ok=True)
        
        # Merge new results with existing ones
        for result in new_results:
            existing_results[result['task_file']] = result
        
        # Convert back to list and save
        all_results = list(existing_results.values())
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        logger.info(f"Results saved incrementally to {results_file}")

    def run_analysis(self, parallel: int = 3, task_filter: Optional[str] = None, dry_run: bool = False, rerun: bool = False):
        """Run the complete task analysis with batched parallel processing."""
        logger.info("Starting task implementation status analysis...")
        
        # Load existing results
        existing_results = self.load_existing_results()
        logger.info(f"Loaded {len(existing_results)} existing results")
        
        # Get all task files
        task_files = self.get_all_task_files()
        
        # Apply filter if specified
        if task_filter:
            task_files = [f for f in task_files if task_filter in f.name]
        
        # Only run previously failed tasks unless rerun is specified
        if not rerun:
            original_count = len(task_files)
            task_files = [f for f in task_files if self.is_task_failed(str(f), existing_results)]
            filtered_count = original_count - len(task_files)
            if filtered_count > 0:
                logger.info(f"Filtered out {filtered_count} successful/new tasks (use --rerun to include them)")
        
        logger.info(f"Found {len(task_files)} task files to process")
        
        if dry_run:
            logger.info("DRY RUN - Would process the following tasks:")
            for task_file in task_files:
                task_info = self.parse_task_file(task_file)
                if task_info:
                    is_failed = self.is_task_failed(str(task_file), existing_results)
                    status = "previously failed" if is_failed else "new/incomplete"
                    logger.info(f"  - {task_file.name}: {task_info['java_file']} ({status})")
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
                    
                    # Save results incrementally after each batch
                    if batch_results:
                        self.save_results_incrementally(batch_results, existing_results)
                    
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
                
                # Save results incrementally after each task
                self.save_results_incrementally([result], existing_results)
        
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
