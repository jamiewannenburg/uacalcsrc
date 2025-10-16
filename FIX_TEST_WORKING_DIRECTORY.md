# Test Failure Analysis & Fix

## Root Cause

**Java wrappers ARE compiled** ✅ but tests fail because they run from the wrong directory.

### The Problem

1. **Tests run from**: `/workspace/python/uacalc/tests/`
2. **Classpath uses relative paths**: `java_wrapper/build/classes:build/classes:org:jars/*`
3. **These paths don't exist** from the test directory
4. **Java can't find classes** → ClassNotFoundException

### Evidence

```bash
# From /workspace - WORKS ✅
$ cd /workspace && java -cp "java_wrapper/build/classes:..." \
    java_wrapper.src.util.SimpleListWrapper make_list
{"success": true, "data": "()"}

# From test directory - FAILS ❌
$ cd /workspace/python/uacalc/tests
$ java -cp "java_wrapper/build/classes:..." \
    java_wrapper.src.util.SimpleListWrapper make_list
Error: Could not find or load main class
```

## Solution

Add `cwd=project_root` to all subprocess.run() calls that invoke Java wrappers.

### Files That Need Fixing

1. ✅ `test_utils.py` - Fixed (TestHarness.run_java_cli)
2. ✅ `test_partition.py` - Fixed (run_java_wrapper function)
3. ⏳ Need to check all other test files with subprocess.run

### Test Files Using subprocess.run

From grep results:
- test_abstract_int_operation.py
- test_abstract_operation.py
- test_array_incrementor.py
- test_basic_operation.py
- test_binary_relation.py
- test_horner.py
- test_int_array.py
- test_int_operation.py
- test_long_list.py
- test_operations.py
- test_operation_symbol.py
- test_operation_with_default_value.py
- test_ordered_sets.py
- test_permutation_generator.py
- test_similarity_type.py
- test_subtrace.py

Most of these already use `cwd=project_root` in their subprocess calls.

## Status

- ✅ Java wrappers compiled (ant compile-wrappers succeeded)
- ✅ test_utils.py fixed (TestHarness now uses cwd=project_root)
- ✅ test_partition.py fixed (added cwd=project_root)
- ⏳ Need to verify other test files

## Next Steps

Run tests again to see improvement after the fixes.
