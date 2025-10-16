#!/usr/bin/env python3
import json
import re

with open('task_analysis/task_analysis_results.json', 'r') as f:
    data = json.load(f)
    
# Find the latest Task 22 result
for result in data:
    if 'Task 22' in result.get('task_file', ''):
        so = result.get('structured_output', {})
        if 'result' in so:
            result_text = so['result']
            
            # Test the JSON extraction logic
            print('=== TESTING JSON EXTRACTION ===')
            
            # Try to find complete JSON object by counting braces
            json_start = result_text.find('```json\n{')
            if json_start != -1:
                # Skip the ```json marker
                json_start = result_text.find('{', json_start)
                print(f'Found ```json marker at position {json_start}')
            elif result_text.find('{"success"') != -1:
                json_start = result_text.find('{"success"')
                print(f'Found success marker at position {json_start}')
            elif result_text.find('{\n  "success"') != -1:
                json_start = result_text.find('{\n  "success"')
                print(f'Found formatted success marker at position {json_start}')
            elif result_text.find('{ "success"') != -1:
                json_start = result_text.find('{ "success"')
                print(f'Found spaced success marker at position {json_start}')
            
            if json_start != -1:
                print(f'JSON start position: {json_start}')
                # Find the matching closing brace
                brace_count = 0
                json_end = json_start
                for i, char in enumerate(result_text[json_start:], json_start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                print(f'JSON end position: {json_end}')
                print(f'Brace count at end: {brace_count}')
                
                if brace_count == 0:
                    json_str = result_text[json_start:json_end]
                    print(f'Extracted JSON length: {len(json_str)}')
                    print('JSON preview:')
                    print(json_str[:200])
                    print('...')
                    
                    try:
                        parsed = json.loads(json_str)
                        print('SUCCESS! Parsed JSON:')
                        print(f'  Success: {parsed.get("success")}')
                        print(f'  Status: {parsed.get("analysis", {}).get("status")}')
                        print(f'  Priority: {parsed.get("analysis", {}).get("priority")}')
                        print(f'  Completion: {parsed.get("analysis", {}).get("completion_percentage")}%')
                    except Exception as e:
                        print(f'JSON parse error: {e}')
                        print('Full JSON:')
                        print(json_str)
                else:
                    print('Could not find complete JSON object')
            else:
                print('Could not find JSON start marker')
        break
