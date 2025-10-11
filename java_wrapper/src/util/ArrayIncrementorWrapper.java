/* ArrayIncrementorWrapper.java - CLI wrapper for org.uacalc.util.ArrayIncrementor
 * 
 * This wrapper exposes all public methods of the ArrayIncrementor interface through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.util;

import java.util.*;
import org.uacalc.util.ArrayIncrementor;
import org.uacalc.util.PermutationGenerator;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the ArrayIncrementor interface that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class ArrayIncrementorWrapper extends WrapperBase {
    
    /**
     * Main entry point for the ArrayIncrementor CLI wrapper.
     */
    public static void main(String[] args) {
        ArrayIncrementorWrapper wrapper = new ArrayIncrementorWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("ArrayIncrementor wrapper failed", e);
        }
    }
    
    /**
     * Run the ArrayIncrementor CLI wrapper with the given arguments.
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
                
            case "test":
                handleTest();
                break;
                
            case "array_incrementor":
                handleArrayIncrementor(options);
                break;
                
            case "list_incrementor":
                handleListIncrementor(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the array_incrementor command.
     */
    private void handleArrayIncrementor(Map<String, String> options) throws Exception {
        String arrayStr = getRequiredArg(options, "array");
        String[] arrayParts = arrayStr.split(",");
        int[] arr = new int[arrayParts.length];
        for (int i = 0; i < arrayParts.length; i++) {
            arr[i] = Integer.parseInt(arrayParts[i].trim());
        }
        
        ArrayIncrementor incrementor = PermutationGenerator.arrayIncrementor(arr);
        
        // Test incrementing
        List<int[]> results = new ArrayList<>();
        results.add(arr.clone()); // Add initial state
        
        while (incrementor.increment()) {
            results.add(arr.clone());
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "array_incrementor");
        result.put("input_array", Arrays.toString(arr));
        result.put("total_permutations", results.size());
        result.put("results", results);
        
        handleSuccess(result);
    }
    
    /**
     * Handle the list_incrementor command.
     */
    private void handleListIncrementor(Map<String, String> options) throws Exception {
        String listStr = getRequiredArg(options, "list");
        String[] listParts = listStr.split(",");
        List<String> lst = new ArrayList<>();
        for (String part : listParts) {
            lst.add(part.trim());
        }
        
        ArrayIncrementor incrementor = PermutationGenerator.listIncrementor(lst);
        
        // Test incrementing
        List<List<String>> results = new ArrayList<>();
        results.add(new ArrayList<>(lst)); // Add initial state
        
        while (incrementor.increment()) {
            results.add(new ArrayList<>(lst));
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "list_incrementor");
        result.put("input_list", lst);
        result.put("total_permutations", results.size());
        result.put("results", results);
        
        handleSuccess(result);
    }
    
    /**
     * Handle the test command.
     */
    private void handleTest() throws Exception {
        // Test array incrementor
        int[] testArray = {0, 1, 2};
        ArrayIncrementor arrayIncrementor = PermutationGenerator.arrayIncrementor(testArray);
        
        List<int[]> arrayResults = new ArrayList<>();
        arrayResults.add(testArray.clone());
        
        while (arrayIncrementor.increment()) {
            arrayResults.add(testArray.clone());
        }
        
        // Test list incrementor
        List<String> testList = Arrays.asList("a", "b", "c");
        ArrayIncrementor listIncrementor = PermutationGenerator.listIncrementor(testList);
        
        List<List<String>> listResults = new ArrayList<>();
        listResults.add(new ArrayList<>(testList));
        
        while (listIncrementor.increment()) {
            listResults.add(new ArrayList<>(testList));
        }
        
        Map<String, Object> arrayTest = new HashMap<>();
        arrayTest.put("input", Arrays.toString(testArray));
        arrayTest.put("permutations", arrayResults.size());
        arrayTest.put("results", arrayResults);
        
        Map<String, Object> listTest = new HashMap<>();
        listTest.put("input", testList);
        listTest.put("permutations", listResults.size());
        listTest.put("results", listResults);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test");
        result.put("array_test", arrayTest);
        result.put("list_test", listTest);
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the ArrayIncrementor wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "ArrayIncrementorWrapper help",
            "ArrayIncrementorWrapper test",
            "ArrayIncrementorWrapper array_incrementor --array \"0,1,2\"",
            "ArrayIncrementorWrapper list_incrementor --list \"a,b,c\""
        };
        
        showUsage("ArrayIncrementor", 
                 "CLI wrapper for org.uacalc.util.ArrayIncrementor operations", 
                 examples);
    }
}
