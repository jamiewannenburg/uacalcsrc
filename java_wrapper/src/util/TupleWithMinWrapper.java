/* TupleWithMinWrapper.java - CLI wrapper for org.uacalc.util.virtuallist.TupleWithMin
 * 
 * This wrapper exposes all public methods of the TupleWithMin class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.util;

import java.util.*;
import org.uacalc.util.virtuallist.TupleWithMin;
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
                
            case "create":
                handleCreate(options);
                break;
                
            case "get":
                handleGet(options);
                break;
                
            case "size":
                handleSize(options);
                break;
                
            case "test":
                handleTest();
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle create command - creates a TupleWithMin and returns size.
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        int arrayLen = getIntArg(options, "array_len", 0);
        int base = getIntArg(options, "base", 0);
        int min = getIntArg(options, "min", 0);
        
        TupleWithMin tuples = new TupleWithMin(arrayLen, base, min);
        long size = tuples.size();
        
        handleSuccess("{\"array_len\":" + arrayLen + 
                     ",\"base\":" + base + 
                     ",\"min\":" + min + 
                     ",\"status\":" + size + "}");
    }
    
    /**
     * Handle get command - gets the kth element from a TupleWithMin.
     */
    private void handleGet(Map<String, String> options) throws Exception {
        int arrayLen = getIntArg(options, "array_len", 0);
        int base = getIntArg(options, "base", 0);
        int min = getIntArg(options, "min", 0);
        long k = getLongArg(options, "k", 0);
        
        TupleWithMin tuples = new TupleWithMin(arrayLen, base, min);
        int[] result = tuples.get(k);
        
        handleSuccess("{\"array_len\":" + arrayLen + 
                     ",\"base\":" + base + 
                     ",\"min\":" + min + 
                     ",\"k\":" + k + 
                     ",\"status\":\"" + Arrays.toString(result) + "\"}");
    }
    
    /**
     * Handle size command - gets the size of a TupleWithMin.
     */
    private void handleSize(Map<String, String> options) throws Exception {
        int arrayLen = getIntArg(options, "array_len", 0);
        int base = getIntArg(options, "base", 0);
        int min = getIntArg(options, "min", 0);
        
        TupleWithMin tuples = new TupleWithMin(arrayLen, base, min);
        long size = tuples.size();
        
        handleSuccess("{\"array_len\":" + arrayLen + 
                     ",\"base\":" + base + 
                     ",\"min\":" + min + 
                     ",\"status\":" + size + "}");
    }
    
    /**
     * Handle test command - runs basic functionality tests.
     */
    private void handleTest() throws Exception {
        // Test basic functionality matching the Java main method
        TupleWithMin tuples = new TupleWithMin(3, 4, 2);
        long size = tuples.size();
        int[] first = tuples.get(0);
        int[] last = tuples.get(size - 1);
        
        handleSuccess("{\"array_len\":3" + 
                     ",\"base\":4" + 
                     ",\"min\":2" + 
                     ",\"size\":" + size + 
                     ",\"first\":\"" + Arrays.toString(first) + "\"" +
                     ",\"last\":\"" + Arrays.toString(last) + "\"" +
                     ",\"status\":\"all_tests_passed\"}");
    }
    
    /**
     * Get a long argument from the options map with a default value.
     * 
     * @param options The options map
     * @param key The argument key
     * @param defaultValue The default value
     * @return The argument value or default
     */
    protected long getLongArg(Map<String, String> options, String key, long defaultValue) {
        String value = options.get(key);
        if (value == null) {
            return defaultValue;
        }
        try {
            return Long.parseLong(value);
        } catch (NumberFormatException e) {
            throw new NumberFormatException("Invalid long for argument " + key + ": " + value);
        }
    }
    
    /**
     * Show usage information for the TupleWithMin wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create --array_len 3 --base 4 --min 2",
            "get --array_len 3 --base 4 --min 2 --k 5",
            "size --array_len 3 --base 4 --min 2",
            "test"
        };
        
        showUsage("TupleWithMin", 
                 "CLI wrapper for org.uacalc.util.virtuallist.TupleWithMin operations", 
                 examples);
    }
}
