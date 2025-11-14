/* IntArrayWrapper.java - CLI wrapper for org.uacalc.util.IntArray
 * 
 * This wrapper exposes all public methods of the IntArray class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.util;

import java.util.*;
import org.uacalc.util.IntArray;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the IntArray class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class IntArrayWrapper extends WrapperBase {
    
    private IntArray intArray;
    private int[] inputArray;
    private int inputSize;
    private String inputString;
    
    /**
     * Main entry point for the IntArray CLI wrapper.
     */
    public static void main(String[] args) {
        IntArrayWrapper wrapper = new IntArrayWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("IntArray wrapper failed", e);
        }
    }
    
    /**
     * Run the IntArray CLI wrapper with the given arguments.
     */
    @Override
    public void run(String[] args) throws Exception {
        if (args.length == 0) {
            showUsage();
            return;
        }
        
        Map<String, String> options = parseArgs(args);
        String command = options.get("arg0");
        
        if (command == null) {
            showUsage();
            return;
        }
        
        switch (command) {
            case "help":
                showUsage();
                break;
                
            case "new":
                handleNew(options);
                break;
                
            case "from_array":
                handleFromArray(options);
                break;
                
            case "from_string":
                handleFromString(options);
                break;
                
            case "universe_size":
                handleUniverseSize(options);
                break;
                
            case "to_array":
                handleToArray(options);
                break;
                
            case "get":
                handleGet(options);
                break;
                
            case "set":
                handleSet(options);
                break;
                
            case "satisfies_blocks_constraint":
                handleSatisfiesBlocksConstraint(options);
                break;
                
            case "satisfies_values_constraint":
                handleSatisfiesValuesConstraint(options);
                break;
                
            case "satisfies_set_constraint":
                handleSatisfiesSetConstraint(options);
                break;
                
            case "satisfies_congruence_constraint":
                handleSatisfiesCongruenceConstraint(options);
                break;
                
            case "is_idempotent":
                handleIsIdempotent(options);
                break;
                
            case "is_constant":
                handleIsConstant(options);
                break;
                
            case "clone_array":
                handleCloneArray(options);
                break;
                
            case "to_string":
                handleToString(options);
                break;
                
            case "string_to_array":
                handleStringToArray(options);
                break;
                
            case "array_to_string":
                handleArrayToString(options);
                break;
                
            case "arrays_equal":
                handleArraysEqual(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    private void handleNew(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 0);
        intArray = new IntArray(size);
        inputSize = size;
        
        Map<String, Object> result = new HashMap<>();
        result.put("size", size);
        result.put("status", "created");
        handleSuccess(result);
    }
    
    private void handleFromArray(Map<String, String> options) throws Exception {
        String arrayStr = getRequiredArg(options, "array");
        int[] array = parseIntArray(arrayStr);
        intArray = new IntArray(array);
        inputArray = array.clone();
        
        Map<String, Object> result = new HashMap<>();
        result.put("array", Arrays.toString(array));
        result.put("status", "created");
        handleSuccess(result);
    }
    
    private void handleFromString(Map<String, String> options) throws Exception {
        String str = getRequiredArg(options, "str");
        int[] array = IntArray.stringToArray(str);
        intArray = new IntArray(array);
        inputString = str;
        
        Map<String, Object> result = new HashMap<>();
        result.put("str", str);
        result.put("array", Arrays.toString(array));
        result.put("status", "created");
        handleSuccess(result);
    }
    
    private void handleUniverseSize(Map<String, String> options) throws Exception {
        ensureIntArrayExists();
        int size = intArray.universeSize();
        
        Map<String, Object> result = new HashMap<>();
        result.put("status", size);
        handleSuccess(result);
    }
    
    private void handleToArray(Map<String, String> options) throws Exception {
        ensureIntArrayExists();
        int[] array = intArray.toArray();
        
        Map<String, Object> result = new HashMap<>();
        result.put("status", Arrays.toString(array));
        handleSuccess(result);
    }
    
    private void handleGet(Map<String, String> options) throws Exception {
        ensureIntArrayExists();
        int index = getIntArg(options, "index", 0);
        int value = intArray.get(index);
        
        Map<String, Object> result = new HashMap<>();
        result.put("index", index);
        result.put("status", value);
        handleSuccess(result);
    }
    
    private void handleSet(Map<String, String> options) throws Exception {
        ensureIntArrayExists();
        int index = getIntArg(options, "index", 0);
        int value = getIntArg(options, "value", 0);
        intArray.set(index, value);
        
        Map<String, Object> result = new HashMap<>();
        result.put("index", index);
        result.put("value", value);
        result.put("status", "set");
        handleSuccess(result);
    }
    
    private void handleSatisfiesBlocksConstraint(Map<String, String> options) throws Exception {
        ensureIntArrayExists();
        String blocksStr = getRequiredArg(options, "blocks");
        int[][] blocks = parseInt2DArray(blocksStr);
        boolean result = intArray.satisfiesBlocksConstraint(blocks);
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("blocks", blocksStr);
        resultMap.put("status", result);
        handleSuccess(resultMap);
    }
    
    private void handleSatisfiesValuesConstraint(Map<String, String> options) throws Exception {
        ensureIntArrayExists();
        String valuesStr = getRequiredArg(options, "values");
        int[][] values = parseInt2DArray(valuesStr);
        boolean result = intArray.satisfiesValuesConstraint(values);
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("values", valuesStr);
        resultMap.put("status", result);
        handleSuccess(resultMap);
    }
    
    private void handleSatisfiesSetConstraint(Map<String, String> options) throws Exception {
        ensureIntArrayExists();
        int index = getIntArg(options, "index", 0);
        String setStr = getRequiredArg(options, "possible_values");
        Set<Integer> possibleValues = parseIntSet(setStr);
        boolean result = intArray.satisfiesSetConstraint(index, possibleValues);
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("index", index);
        resultMap.put("possible_values", setStr);
        resultMap.put("status", result);
        handleSuccess(resultMap);
    }
    
    private void handleSatisfiesCongruenceConstraint(Map<String, String> options) throws Exception {
        ensureIntArrayExists();
        int index = getIntArg(options, "index", 0);
        String alphaStr = getRequiredArg(options, "alpha");
        int elemIndex = getIntArg(options, "elem_index", 0);
        
        // For now, return an error since we need Partition implementation
        handleError("Partition constraint not yet implemented in Java wrapper", null);
    }
    
    private void handleIsIdempotent(Map<String, String> options) throws Exception {
        ensureIntArrayExists();
        boolean result = intArray.isIdempotent();
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("status", result);
        handleSuccess(resultMap);
    }
    
    private void handleIsConstant(Map<String, String> options) throws Exception {
        ensureIntArrayExists();
        boolean result = intArray.isConstant();
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("status", result);
        handleSuccess(resultMap);
    }
    
    private void handleCloneArray(Map<String, String> options) throws Exception {
        ensureIntArrayExists();
        IntArray cloned = (IntArray) intArray.clone();
        int[] clonedArray = cloned.toArray();
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("status", Arrays.toString(clonedArray));
        handleSuccess(resultMap);
    }
    
    private void handleToString(Map<String, String> options) throws Exception {
        ensureIntArrayExists();
        String result = intArray.toString();
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("status", result);
        handleSuccess(resultMap);
    }
    
    private void handleStringToArray(Map<String, String> options) throws Exception {
        String str = getRequiredArg(options, "str");
        int[] result = IntArray.stringToArray(str);
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("str", str);
        resultMap.put("status", Arrays.toString(result));
        handleSuccess(resultMap);
    }
    
    private void handleArrayToString(Map<String, String> options) throws Exception {
        String arrayStr = getRequiredArg(options, "array");
        int[] array = parseIntArray(arrayStr);
        String result = IntArray.intArrayToString(array);
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("array", arrayStr);
        resultMap.put("status", result);
        handleSuccess(resultMap);
    }
    
    private void handleArraysEqual(Map<String, String> options) throws Exception {
        String array1Str = getRequiredArg(options, "array1");
        String array2Str = getRequiredArg(options, "array2");
        int[] array1 = parseIntArray(array1Str);
        int[] array2 = parseIntArray(array2Str);
        boolean result = IntArray.equalIntArrays(array1, array2);
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("array1", array1Str);
        resultMap.put("array2", array2Str);
        resultMap.put("status", result);
        handleSuccess(resultMap);
    }
    
    private void handleTest(Map<String, String> options) throws Exception {
        // Run basic functionality tests
        List<String> testResults = new ArrayList<>();
        
        try {
            // Test 1: Create from size
            IntArray test1 = new IntArray(3);
            testResults.add("✓ Created IntArray from size");
            
            // Test 2: Create from array
            int[] testArray = {1, 2, 3};
            IntArray test2 = new IntArray(testArray);
            testResults.add("✓ Created IntArray from array");
            
            // Test 3: Create from string
            IntArray test3 = new IntArray(IntArray.stringToArray("1, 2, 3"));
            testResults.add("✓ Created IntArray from string");
            
            // Test 4: Basic operations
            test2.set(0, 5);
            int value = test2.get(0);
            if (value == 5) {
                testResults.add("✓ Set and get operations work");
            } else {
                testResults.add("✗ Set and get operations failed");
            }
            
            // Test 5: String conversion
            String str = test2.toString();
            if (str.contains("5")) {
                testResults.add("✓ String conversion works");
            } else {
                testResults.add("✗ String conversion failed");
            }
            
            // Test 6: Equality
            IntArray test4 = new IntArray(new int[]{5, 2, 3});
            if (test2.equals(test4)) {
                testResults.add("✓ Equality comparison works");
            } else {
                testResults.add("✗ Equality comparison failed");
            }
            
        } catch (Exception e) {
            testResults.add("✗ Test failed with exception: " + e.getMessage());
        }
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("status", "completed");
        resultMap.put("results", testResults);
        handleSuccess(resultMap);
    }
    
    private void ensureIntArrayExists() throws Exception {
        if (intArray == null) {
            throw new Exception("IntArray not initialized. Use 'new', 'from_array', or 'from_string' first.");
        }
    }
    
    private int[] parseIntArray(String arrayStr) throws Exception {
        arrayStr = arrayStr.trim();
        if (arrayStr.startsWith("[") && arrayStr.endsWith("]")) {
            arrayStr = arrayStr.substring(1, arrayStr.length() - 1);
        }
        
        if (arrayStr.isEmpty()) {
            return new int[0];
        }
        
        String[] parts = arrayStr.split(",");
        int[] result = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            result[i] = Integer.parseInt(parts[i].trim());
        }
        return result;
    }
    
    private int[][] parseInt2DArray(String arrayStr) throws Exception {
        arrayStr = arrayStr.trim();
        if (arrayStr.startsWith("[") && arrayStr.endsWith("]")) {
            arrayStr = arrayStr.substring(1, arrayStr.length() - 1);
        }
        
        // Simple parsing for 2D arrays like "[[1,2],[3,4]]"
        List<int[]> rows = new ArrayList<>();
        String[] rowStrs = arrayStr.split("\\],\\s*\\[");
        
        for (String rowStr : rowStrs) {
            rowStr = rowStr.replaceAll("[\\[\\]]", "");
            if (!rowStr.isEmpty()) {
                String[] parts = rowStr.split(",");
                int[] row = new int[parts.length];
                for (int i = 0; i < parts.length; i++) {
                    row[i] = Integer.parseInt(parts[i].trim());
                }
                rows.add(row);
            }
        }
        
        return rows.toArray(new int[0][]);
    }
    
    private Set<Integer> parseIntSet(String setStr) throws Exception {
        setStr = setStr.trim();
        if (setStr.startsWith("{") && setStr.endsWith("}")) {
            setStr = setStr.substring(1, setStr.length() - 1);
        }
        
        Set<Integer> result = new HashSet<>();
        if (!setStr.isEmpty()) {
            String[] parts = setStr.split(",");
            for (String part : parts) {
                result.add(Integer.parseInt(part.trim()));
            }
        }
        return result;
    }
    
    /**
     * Show usage information for the IntArray wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "new --size 5",
            "from_array --array \"[1, 2, 3]\"",
            "from_string --str \"1, 2, 3\"",
            "get --index 0",
            "set --index 1 --value 42",
            "is_idempotent",
            "is_constant",
            "to_string",
            "string_to_array --str \"1, 2, 3\"",
            "arrays_equal --array1 \"[1,2,3]\" --array2 \"[1,2,3]\"",
            "test"
        };
        
        showUsage("IntArray", 
                 "CLI wrapper for org.uacalc.util.IntArray operations", 
                 examples);
    }
}
