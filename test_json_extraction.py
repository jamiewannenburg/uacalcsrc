#!/usr/bin/env python3
import json
import re

# Load the actual result data
with open('task_analysis/task_analysis_results.json', 'r') as f:
    data = json.load(f)
    
# Find the latest Task 22 result
for result in data:
    if 'Task 22' in result.get('task_file', ''):
        so = result.get('structured_output', {})
        if 'result' in so:
            result_text = so['result']
            print('=== TESTING JSON EXTRACTION ===')
            print(f'Result text length: {len(result_text)}')
            
            # Test the regex approach
            json_match = re.search(r'```json\s*(\{.*\})\s*```', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                print(f'Found JSON block with regex, length: {len(json_str)}')
                print('JSON preview:')
                print(json_str[:200])
                print('...')
                
                try:
                    parsed = json.loads(json_str)
                    print('SUCCESS! Parsed JSON with regex:')
                    print(f'  Success: {parsed.get("success")}')
                    print(f'  Status: {parsed.get("analysis", {}).get("status")}')
                    print(f'  Priority: {parsed.get("analysis", {}).get("priority")}')
                    print(f'  Completion: {parsed.get("analysis", {}).get("completion_percentage")}%')
                except Exception as e:
                    print(f'JSON parse error with regex: {e}')
            else:
                print('Regex did not find JSON block')
                
                # Test the manual approach
                json_start = result_text.find('```json\n{')
                if json_start != -1:
                    json_start = result_text.find('{', json_start)
                    print(f'Found JSON start marker at position {json_start}')
                    
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
                    
                    print(f'JSON extraction: start={json_start}, end={json_end}, brace_count={brace_count}')
                    if brace_count == 0:
                        json_str = result_text[json_start:json_end]
                        print(f'Extracted JSON manually, length: {len(json_str)}')
                        print('JSON preview:')
                        print(json_str[:200])
                        print('...')
                        
                        try:
                            parsed = json.loads(json_str)
                            print('SUCCESS! Parsed JSON manually:')
                            print(f'  Success: {parsed.get("success")}')
                            print(f'  Status: {parsed.get("analysis", {}).get("status")}')
                            print(f'  Priority: {parsed.get("analysis", {}).get("priority")}')
                            print(f'  Completion: {parsed.get("analysis", {}).get("completion_percentage")}%')
                        except Exception as e:
                            print(f'JSON parse error manually: {e}')
                            print('Full JSON:')
                            print(json_str)
                    else:
                        print('Could not find complete JSON object')
                else:
                    print('Could not find JSON start marker')
        break
