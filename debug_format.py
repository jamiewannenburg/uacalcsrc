#!/usr/bin/env python3
import json

with open('task_analysis/task_analysis_results.json', 'r') as f:
    data = json.load(f)
    
# Find the latest Task 22 result
for result in data:
    if 'Task 22' in result.get('task_file', ''):
        print('=== LATEST TASK 22 RESULT ===')
        print('Success:', result.get('success'))
        print('Error:', result.get('error'))
        
        so = result.get('structured_output', {})
        print('Structured output keys:', list(so.keys()))
        print('Type:', so.get('type'))
        print('Subtype:', so.get('subtype'))
        print('Is error:', so.get('is_error'))
        
        if 'result' in so:
            result_text = so['result']
            print('Result text length:', len(result_text))
            print('First 100 chars:', result_text[:100])
            
            # Check if it contains the expected markers
            has_json_marker = '```json' in result_text
            has_success_marker = '{"success"' in result_text
            has_json_newline = '```json\n{' in result_text
            
            print('Contains ```json marker:', has_json_marker)
            print('Contains success marker:', has_success_marker)
            print('Contains ```json newline marker:', has_json_newline)
        break
