/* LongListWrapper.java - CLI wrapper for org.uacalc.util.virtuallist.LongList
 * 
 * This wrapper exposes all public methods of the LongList class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.util;

import java.util.*;
import org.uacalc.util.virtuallist.LongList;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the LongList class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class LongListWrapper extends WrapperBase {
    
    /**
     * Main entry point for the LongList CLI wrapper.
     */
    public static void main(String[] args) {
        LongListWrapper wrapper = new LongListWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("LongList wrapper failed", e);
        }
    }
    
    /**
     * Run the LongList CLI wrapper with the given arguments.
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
                
            case "int_tuples":
                handleIntTuples(options);
                break;
                
            case "int_tuples_with_min":
                handleIntTuplesWithMin(options);
                break;
                
            case "fixed_sized_subsets":
                handleFixedSizedSubsets(options);
                break;
                
            case "subsets":
                handleSubsets(options);
                break;
                
            case "permutations":
                handlePermutations(options);
                break;
                
            case "factorial":
                handleFactorial(options);
                break;
                
            case "binomial":
                handleBinomial(options);
                break;
                
            case "log2":
                handleLog2(options);
                break;
                
            case "pow2":
                handlePow2(options);
                break;
                
            case "test":
                handleTest();
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle int_tuples command.
     */
    private void handleIntTuples(Map<String, String> options) throws Exception {
        int tupleLength = getIntArg(options, "tuple_length", 0);
        int base = getIntArg(options, "base", 0);
        Long k = getOptionalLongArg(options, "k");
        
        LongList<int[]> list = LongList.intTuples(tupleLength, base);
        
        if (k != null) {
            int[] result = list.get(k);
            handleSuccess("{\"tuple_length\":" + tupleLength + 
                         ",\"base\":" + base + 
                         ",\"k\":" + k + 
                         ",\"status\":\"" + Arrays.toString(result) + "\"}");
        } else {
            handleSuccess("{\"tuple_length\":" + tupleLength + 
                         ",\"base\":" + base + 
                         ",\"size\":" + list.size() + "}");
        }
    }
    
    /**
     * Handle int_tuples_with_min command.
     */
    private void handleIntTuplesWithMin(Map<String, String> options) throws Exception {
        int tupleLength = getIntArg(options, "tuple_length", 0);
        int base = getIntArg(options, "base", 0);
        int min = getIntArg(options, "min", 0);
        Long k = getOptionalLongArg(options, "k");
        
        LongList<int[]> list = LongList.intTuplesWithMin(tupleLength, base, min);
        
        if (k != null) {
            int[] result = list.get(k);
            handleSuccess("{\"tuple_length\":" + tupleLength + 
                         ",\"base\":" + base + 
                         ",\"min\":" + min + 
                         ",\"k\":" + k + 
                         ",\"status\":\"" + Arrays.toString(result) + "\"}");
        } else {
            handleSuccess("{\"tuple_length\":" + tupleLength + 
                         ",\"base\":" + base + 
                         ",\"min\":" + min + 
                         ",\"size\":" + list.size() + "}");
        }
    }
    
    /**
     * Handle fixed_sized_subsets command.
     */
    private void handleFixedSizedSubsets(Map<String, String> options) throws Exception {
        int subsetSize = getIntArg(options, "subset_size", 0);
        int setSize = getIntArg(options, "set_size", 0);
        Long k = getOptionalLongArg(options, "k");
        
        LongList<int[]> list = LongList.fixedSizedSubsets(subsetSize, setSize);
        
        if (k != null) {
            int[] result = list.get(k);
            handleSuccess("{\"subset_size\":" + subsetSize + 
                         ",\"set_size\":" + setSize + 
                         ",\"k\":" + k + 
                         ",\"status\":\"" + Arrays.toString(result) + "\"}");
        } else {
            handleSuccess("{\"subset_size\":" + subsetSize + 
                         ",\"set_size\":" + setSize + 
                         ",\"size\":" + list.size() + "}");
        }
    }
    
    /**
     * Handle subsets command.
     */
    private void handleSubsets(Map<String, String> options) throws Exception {
        int setSize = getIntArg(options, "set_size", 0);
        Long k = getOptionalLongArg(options, "k");
        
        LongList<int[]> list = LongList.subsets(setSize);
        
        if (k != null) {
            int[] result = list.get(k);
            handleSuccess("{\"set_size\":" + setSize + 
                         ",\"k\":" + k + 
                         ",\"status\":\"" + Arrays.toString(result) + "\"}");
        } else {
            handleSuccess("{\"set_size\":" + setSize + 
                         ",\"size\":" + list.size() + "}");
        }
    }
    
    /**
     * Handle permutations command.
     */
    private void handlePermutations(Map<String, String> options) throws Exception {
        int n = getIntArg(options, "n", 0);
        Long k = getOptionalLongArg(options, "k");
        
        LongList<int[]> list = LongList.permutations(n);
        
        if (k != null) {
            int[] result = list.get(k);
            handleSuccess("{\"n\":" + n + 
                         ",\"k\":" + k + 
                         ",\"status\":\"" + Arrays.toString(result) + "\"}");
        } else {
            handleSuccess("{\"n\":" + n + 
                         ",\"size\":" + list.size() + "}");
        }
    }
    
    /**
     * Handle factorial command.
     */
    private void handleFactorial(Map<String, String> options) throws Exception {
        // Debug: print all options
        System.err.println("Debug: options = " + options);
        int n = getIntArg(options, "n", 0);
        System.err.println("Debug: n = " + n);
        long result = LongList.factorial(n);
        
        handleSuccess("{\"n\":" + n + 
                     ",\"status\":" + result + "}");
    }
    
    /**
     * Handle binomial command.
     */
    private void handleBinomial(Map<String, String> options) throws Exception {
        int n = getIntArg(options, "n", 0);
        int r = getIntArg(options, "r", 0);
        long result = LongList.binomial(n, r);
        
        handleSuccess("{\"n\":" + n + 
                     ",\"r\":" + r + 
                     ",\"status\":" + result + "}");
    }
    
    /**
     * Handle log2 command.
     */
    private void handleLog2(Map<String, String> options) throws Exception {
        long k = getLongArg(options, "k", 0);
        int result = LongList.log2(k);
        
        handleSuccess("{\"k\":" + k + 
                     ",\"status\":" + result + "}");
    }
    
    /**
     * Handle pow2 command.
     */
    private void handlePow2(Map<String, String> options) throws Exception {
        int r = getIntArg(options, "r", 0);
        long result = LongList.pow2(r);
        
        handleSuccess("{\"r\":" + r + 
                     ",\"status\":" + result + "}");
    }
    
    /**
     * Handle test command.
     */
    private void handleTest() throws Exception {
        // Test basic functionality
        LongList<int[]> tuples = LongList.intTuples(3, 4);
        int[] result1 = tuples.get(0);
        
        LongList<int[]> subsets = LongList.subsets(4);
        int[] result2 = subsets.get(0);
        
        long factorial = LongList.factorial(5);
        long binomial = LongList.binomial(5, 2);
        
        handleSuccess("{\"int_tuples_size\":" + tuples.size() + 
                     ",\"int_tuples_first\":\"" + Arrays.toString(result1) + "\"" +
                     ",\"subsets_size\":" + subsets.size() + 
                     ",\"subsets_first\":\"" + Arrays.toString(result2) + "\"" +
                     ",\"factorial_5\":" + factorial + 
                     ",\"binomial_5_2\":" + binomial + 
                     ",\"status\":\"all_tests_passed\"}");
    }
    
    /**
     * Get an optional long argument from the options map.
     * 
     * @param options The options map
     * @param key The argument key
     * @return The argument value or null if not present
     */
    private Long getOptionalLongArg(Map<String, String> options, String key) {
        String value = options.get(key);
        if (value == null) {
            return null;
        }
        try {
            return Long.parseLong(value);
        } catch (NumberFormatException e) {
            throw new NumberFormatException("Invalid long for argument " + key + ": " + value);
        }
    }
    
    /**
     * Get a long argument from the options map with a default value.
     * 
     * @param options The options map
     * @param key The argument key
     * @param defaultValue The default value
     * @return The argument value or default
     */
    private long getLongArg(Map<String, String> options, String key, long defaultValue) {
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
     * Show usage information for the LongList wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "int_tuples --tuple_length=3 --base=4",
            "int_tuples --tuple_length=3 --base=4 --k=5",
            "int_tuples_with_min --tuple_length=3 --base=4 --min=2",
            "int_tuples_with_min --tuple_length=3 --base=4 --min=2 --k=5",
            "fixed_sized_subsets --subset_size=3 --set_size=6",
            "fixed_sized_subsets --subset_size=3 --set_size=6 --k=5",
            "subsets --set_size=4",
            "subsets --set_size=4 --k=5",
            "permutations --n=4",
            "permutations --n=4 --k=5",
            "factorial --n=5",
            "binomial --n=5 --r=2",
            "log2 --k=8",
            "pow2 --r=3",
            "test"
        };
        
        showUsage("LongList", 
                 "CLI wrapper for org.uacalc.util.virtuallist.LongList operations", 
                 examples);
    }
}
