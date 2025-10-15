/* TupleWithMinWrapper.java - CLI wrapper for org.uacalc.util.virtuallist.TupleWithMin
 * 
 * This wrapper exposes all public methods of the TupleWithMin class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.util.virtuallist;

import java.util.*;
import org.uacalc.util.virtuallist.TupleWithMin;
import org.uacalc.util.virtuallist.LongList;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the TupleWithMin class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class TupleWithMinWrapper extends WrapperBase {
    
    /**
     * Main entry point for the TupleWithMin CLI wrapper.
     */
    public static void main(String[] args) {
        TupleWithMinWrapper wrapper = new TupleWithMinWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("TupleWithMin wrapper failed", e);
        }
    }
    
    /**
     * Run the TupleWithMin CLI wrapper with the given arguments.
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
                
            case "get":
                handleGet(options);
                break;
                
            case "size":
                handleSize(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the 'new' command - create a new TupleWithMin and verify it.
     */
    private void handleNew(Map<String, String> options) {
        int arrayLen = getIntArg(options, "arrayLen", 0);
        int base = getIntArg(options, "base", 0);
        int min = getIntArg(options, "min", 0);
        
        try {
            TupleWithMin tuples = new TupleWithMin(arrayLen, base, min);
            
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("command", "new");
            data.put("arrayLen", arrayLen);
            data.put("base", base);
            data.put("min", min);
            data.put("status", "created");
            data.put("size", tuples.size());
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to create TupleWithMin", e);
        }
    }
    
    /**
     * Handle the 'get' command - get the kth element.
     */
    private void handleGet(Map<String, String> options) {
        int arrayLen = getIntArg(options, "arrayLen", 0);
        int base = getIntArg(options, "base", 0);
        int min = getIntArg(options, "min", 0);
        long k = getLongArg(options, "k", 0L);
        
        try {
            TupleWithMin tuples = new TupleWithMin(arrayLen, base, min);
            int[] result = tuples.get(k);
            
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("command", "get");
            data.put("arrayLen", arrayLen);
            data.put("base", base);
            data.put("min", min);
            data.put("k", k);
            data.put("value", Arrays.asList(boxArray(result)));
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to get element", e);
        }
    }
    
    /**
     * Handle the 'size' command - get the size of the list.
     */
    private void handleSize(Map<String, String> options) {
        int arrayLen = getIntArg(options, "arrayLen", 0);
        int base = getIntArg(options, "base", 0);
        int min = getIntArg(options, "min", 0);
        
        try {
            TupleWithMin tuples = new TupleWithMin(arrayLen, base, min);
            long size = tuples.size();
            
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("command", "size");
            data.put("arrayLen", arrayLen);
            data.put("base", base);
            data.put("min", min);
            data.put("size", size);
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to get size", e);
        }
    }
    
    /**
     * Handle the 'test' command - run basic functionality tests.
     */
    private void handleTest(Map<String, String> options) {
        try {
            // Test case from Java main method
            TupleWithMin tuples = new TupleWithMin(3, 4, 2);
            long size = tuples.size();
            
            // Get first few elements
            List<List<Integer>> elements = new ArrayList<>();
            for (int i = 0; i < Math.min(10, size); i++) {
                int[] arr = tuples.get(i);
                elements.add(Arrays.asList(boxArray(arr)));
            }
            
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("command", "test");
            data.put("arrayLen", 3);
            data.put("base", 4);
            data.put("min", 2);
            data.put("size", size);
            data.put("elements", elements);
            data.put("status", "passed");
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Test failed", e);
        }
    }
    
    /**
     * Box an int array to Integer array for serialization.
     */
    private Integer[] boxArray(int[] arr) {
        Integer[] result = new Integer[arr.length];
        for (int i = 0; i < arr.length; i++) {
            result[i] = arr[i];
        }
        return result;
    }
    
    /**
     * Show usage information for the TupleWithMin wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "new --arrayLen 3 --base 4 --min 2",
            "get --arrayLen 3 --base 4 --min 2 --k 0",
            "size --arrayLen 3 --base 4 --min 2",
            "test"
        };
        
        showUsage("TupleWithMin", 
                 "CLI wrapper for org.uacalc.util.virtuallist.TupleWithMin operations", 
                 examples);
    }
}
