#!/usr/bin/env python3
"""
Script to split TRANSLATION_TASKS.md into individual task files.
Each task file will contain the Overview, Translation Strategy, and the specific task.
"""

import re
import os
from pathlib import Path

def main():
    # Read the main file
    input_file = "TRANSLATION_TASKS.md"
    tasks_dir = "tasks"
    
    # Ensure tasks directory exists
    Path(tasks_dir).mkdir(exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the Overview and Translation Strategy sections (before the first task)
    overview_match = re.search(r'^# UACalc Rust/Python Translation Plan\n\n(.*?)\n## Translation Tasks\n', content, re.DOTALL)
    if overview_match:
        overview_section = overview_match.group(1)
    else:
        overview_section = ""
    
    # Find all tasks using regex - improved pattern to better capture task boundaries
    # Split the content by task headers to get individual tasks
    task_sections = re.split(r'\n## Task \d+:', content)
    
    # Process each task section
    task_count = 0
    for i, section in enumerate(task_sections):
        if i == 0:
            # Skip the first section (overview and strategy)
            continue
            
        # Extract task number and class name from the section
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        # First line should contain the task info
        first_line = lines[0].strip()
        
        # Parse task number and class name
        task_match = re.match(r'^Translate `([^`]+)`(?:\s+(.*?))?$', first_line)
        if not task_match:
            continue
            
        class_name = task_match.group(1)
        status = task_match.group(2) if task_match.group(2) else ""
        task_count += 1
        
        # Get the rest of the content (skip the first line which is the task header)
        task_content = '\n'.join(lines[1:]).strip()
        
        # Clean up the task content (remove trailing --- if present)
        if task_content.endswith('\n---'):
            task_content = task_content[:-4].rstrip()
        
        # Create filename: "Task X - ClassName.md"
        filename = f"Task {task_count} - {class_name}.md"
        filepath = os.path.join(tasks_dir, filename)
        
        # Create the content for this task file
        file_content = f"""# UACalc Rust/Python Translation Plan

{overview_section}

## Translation Tasks

## Task {task_count}: Translate `{class_name}`{f' {status}' if status else ''}

{task_content}
"""
        
        # Write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        print(f"Created: {filepath}")
    
    print(f"\nSuccessfully created {task_count} task files in the '{tasks_dir}' directory.")

if __name__ == "__main__":
    main()
