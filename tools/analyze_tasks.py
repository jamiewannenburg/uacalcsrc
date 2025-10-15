#!/usr/bin/env python3
"""
Task Analysis Automation Script

This script spawns cursor-agent CLI instances to analyze each of the 85 task files
in the tasks/ directory. Each agent analyzes the corresponding Java file, determines
appropriate Rust implementation patterns, verifies dependencies, and updates the
task file with detailed recommendations.
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
        logging.FileHandler('../task_analysis/task_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TaskAnalyzer:
    def __init__(self, project_root: str = "/home/jamie/Documents/uacalcsrc"):
        self.project_root = Path(project_root)
        self.tasks_dir = self.project_root / "tasks"
        self.java_dir = self.project_root / "org"
        self.patterns_file = self.project_root / "IMPLEMENTATION_PATTERNS.md"
        
        # Verify required directories exist
        if not self.tasks_dir.exists():
            raise FileNotFoundError(f"Tasks directory not found: {self.tasks_dir}")
        if not self.java_dir.exists():
            raise FileNotFoundError(f"Java directory not found: {self.java_dir}")
        if not self.patterns_file.exists():
            raise FileNotFoundError(f"Implementation patterns file not found: {self.patterns_file}")
    
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
        """Build comprehensive prompt for cursor-agent."""
        task_file = task_info['task_file']
        java_file = task_info['java_file']
        is_completed = task_info['is_completed']
        
        prompt = f"""You are a Rust translation expert analyzing a Java-to-Rust translation task. Your job is to analyze the task file and provide detailed implementation recommendations WITHOUT implementing any code.

## Your Task:
1. Read and analyze the task file: {task_file}
2. Read and analyze the Java file: {java_file}
3. Read the implementation patterns: {self.patterns_file}
4. Update the task file with detailed recommendations

## Analysis Requirements:

### 1. Java File Analysis
- Read the Java file and understand its structure
- Identify all public methods and their signatures
- Determine if it's an interface, abstract class, or concrete class
- Identify any special patterns (builder, factory, etc.)

### 2. Deep Dependency Analysis
- Parse Java imports to identify UACalc dependencies
- Search the entire codebase for actual usage patterns of this class
- Cross-reference with other task files to ensure correct ordering
- Verify all dependencies are correctly listed in the task
- Look for indirect dependencies through method calls and field access
- Identify missing dependencies that should be added
- Do NOT trust the existing dependency list - analyze from scratch

### 3. Rust Implementation Pattern Analysis
- Determine if Java class should become: interface → trait, abstract class → trait + default impls, concrete class → struct
- Identify methods that should be: trait methods, struct methods, free functions
- Determine if generics or dynamic dispatch should be used
- Check for builder patterns, factory methods, etc.

### 4. Usage Pattern Analysis
- Search codebase for files that import/use this class
- Identify common usage patterns
- Determine if class is meant to be instantiated or used as abstraction layer

### 5. Java Wrapper Suitability
- If abstract/interface → not suitable until concrete implementation available
- If concrete class → suitable for testing
- If utility class with static methods → suitable for testing

### 6. Verification for Completed Tasks
{f"- This task is marked as COMPLETED - verify implementation against criteria" if is_completed else "- This task is NOT completed - provide implementation recommendations"}
- Check if all dependencies are correctly listed
- Verify Rust implementation exists and follows patterns
- Check if Java wrapper exists and is testable
- If criteria not met: uncheck boxes and add recommendations

## Output Requirements:
1. Update the task file with detailed recommendations, delete irrelevant sections in the task file.
2. For completed tasks: verify and potentially uncheck boxes if criteria not met
3. Add specific recommendations for:
   - Rust struct/trait/enum design
   - Method organization (trait vs struct methods)
   - Generic vs dynamic dispatch decisions
   - Java wrapper appropriateness
   - Testing strategy
4. Do NOT implement any code - only provide analysis and recommendations
5. Return structured JSON output with your findings and success status

## Files to Read:
- Task file: {task_file}
- Java file: {java_file}
- Implementation patterns: {self.patterns_file}

Begin your analysis and update the task file accordingly. Return your findings in JSON format with the following structure:
{{
  "success": true/false,
  "analysis": {{
    "java_class_type": "interface|abstract|concrete",
    "rust_construct": "trait|struct|enum",
    "dependencies_found": ["list", "of", "dependencies"],
    "dependencies_correct": true/false,
    "java_wrapper_suitable": true/false,
    "implementation_recommendations": "detailed recommendations",
    "testing_strategy": "recommended strategy"
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
    
    def process_single_task(self, task_path: Path) -> Dict:
        """Process a single task file."""
        logger.info(f"Processing task: {task_path.name}")
        
        # Parse task file to get basic info
        task_info = self.parse_task_file(task_path)
        if not task_info:
            return {
                'task': str(task_path),
                'success': False,
                'error': 'Failed to parse task file'
            }
        
        # Build prompt
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
        
        return {
            'task': str(task_path),
            'success': success,
            'output': output,
            'structured_output': structured_output,
            'java_file': task_info['java_file'],
            'is_completed': task_info['is_completed']
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
            # This ensures that if there are duplicates, the most recent one is used
            task_results = {}
            for result in results:
                task_path = result.get('task')
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
        
        # Merge new results with existing ones (this overwrites any existing result for the same task)
        for result in new_results:
            existing_results[result['task']] = result
        
        # Convert back to list and save (this ensures no duplicates)
        all_results = list(existing_results.values())
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        logger.info(f"Results saved incrementally to {results_file}")
    
    def cleanup_results_file(self):
        """Clean up the results file to remove any duplicate entries."""
        results_file = self.project_root / "task_analysis" / "task_analysis_results.json"
        if not results_file.exists():
            return
        
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            # Remove duplicates by keeping only the last occurrence of each task
            seen_tasks = set()
            cleaned_results = []
            duplicate_count = 0
            
            for result in results:
                task_path = result.get('task')
                if task_path and task_path not in seen_tasks:
                    seen_tasks.add(task_path)
                    cleaned_results.append(result)
                elif task_path:
                    duplicate_count += 1
            
            if duplicate_count > 0:
                logger.info(f"Removed {duplicate_count} duplicate entries from results file")
                with open(results_file, 'w') as f:
                    json.dump(cleaned_results, f, indent=2, default=str)
                logger.info(f"Cleaned results file saved to {results_file}")
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to cleanup results file: {e}")

    def run_analysis(self, parallel: int = 3, task_filter: Optional[str] = None, dry_run: bool = False, rerun: bool = False):
        """Run the complete task analysis with batched parallel processing."""
        logger.info("Starting task analysis...")
        
        # Clean up results file to remove any duplicates
        self.cleanup_results_file()
        
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
                                'task': str(task_file),
                                'success': False,
                                'error': str(e)
                            }
                            batch_results.append(error_result)
                            results.append(error_result)
                    
                    # Save results incrementally after each batch
                    if batch_results:
                        self.save_results_incrementally(batch_results, existing_results)
                    
                    # Log batch results
                    batch_successful = sum(1 for r in batch_results if r['success'])
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
        
        # Report final results
        elapsed_time = time.time() - start_time
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        logger.info(f"Analysis complete in {elapsed_time:.2f} seconds")
        logger.info(f"Total results: {successful} successful, {failed} failed")
        
        return results

def main():
    parser = argparse.ArgumentParser(description="Analyze UACalc translation tasks using cursor-agent")
    parser.add_argument("--parallel", "-p", type=int, default=3, 
                       help="Number of parallel processes per batch (default: 3)")
    parser.add_argument("--task-filter", "-f", type=str, 
                       help="Only process tasks matching this pattern")
    parser.add_argument("--dry-run", "-d", action="store_true",
                       help="Show what would be done without executing")
    parser.add_argument("--rerun", "-r", action="store_true",
                       help="Rerun all tasks, including those already completed")
    parser.add_argument("--cleanup", "-c", action="store_true",
                       help="Clean up results file to remove duplicates and exit")
    parser.add_argument("--project-root", type=str, default="/home/jamie/Documents/uacalcsrc",
                       help="Project root directory")
    
    args = parser.parse_args()
    
    try:
        analyzer = TaskAnalyzer(args.project_root)
        
        if args.cleanup:
            analyzer.cleanup_results_file()
            return 0
        
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
