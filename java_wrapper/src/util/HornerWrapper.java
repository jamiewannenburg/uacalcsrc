/* Horner.java - CLI wrapper for org.uacalc.util.Horner
 * 
 * This wrapper exposes all public methods of the Horner class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.util;

import java.util.*;
import org.uacalc.util.Horner;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Horner class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class HornerWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Horner CLI wrapper.
     */
    public static void main(String[] args) {
        HornerWrapper wrapper = new HornerWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Horner wrapper failed", e);
        }
    }
    
    /**
     * Run the Horner CLI wrapper with the given arguments.
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
                
            case "horner":
                handleHorner(options);
                break;
                
            case "hornerInv":
                handleHornerInv(options);
                break;
                
            case "hornerSameSize":
                handleHornerSameSize(options);
                break;
                
            case "hornerInvSameSize":
                handleHornerInvSameSize(options);
                break;
                
            case "hornerInteger":
                handleHornerInteger(options);
                break;
                
            case "reverseArray":
                handleReverseArray(options);
                break;
                
            case "leftRightReverse":
                handleLeftRightReverse(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the horner command.
     */
    private void handleHorner(Map<String, String> options) throws Exception {
        int[] args = parseIntArray(getRequiredArg(options, "args"));
        int[] sizes = parseIntArray(getRequiredArg(options, "sizes"));
        
        if (args.length != sizes.length) {
            throw new IllegalArgumentException("args and sizes arrays must have the same length");
        }
        
        int result = Horner.horner(args, sizes);
        
        Map<String, Object> data = new HashMap<>();
        data.put("result", result);
        data.put("args", args);
        data.put("sizes", sizes);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the hornerInv command.
     */
    private void handleHornerInv(Map<String, String> options) throws Exception {
        int k = Integer.parseInt(getRequiredArg(options, "k"));
        int[] sizes = parseIntArray(getRequiredArg(options, "sizes"));
        
        int[] result = Horner.hornerInv(k, sizes);
        
        Map<String, Object> data = new HashMap<>();
        data.put("result", result);
        data.put("k", k);
        data.put("sizes", sizes);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the hornerSameSize command.
     */
    private void handleHornerSameSize(Map<String, String> options) throws Exception {
        int[] args = parseIntArray(getRequiredArg(options, "args"));
        int size = Integer.parseInt(getRequiredArg(options, "size"));
        
        int result = Horner.horner(args, size);
        
        Map<String, Object> data = new HashMap<>();
        data.put("result", result);
        data.put("args", args);
        data.put("size", size);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the hornerInvSameSize command.
     */
    private void handleHornerInvSameSize(Map<String, String> options) throws Exception {
        int k = Integer.parseInt(getRequiredArg(options, "k"));
        int size = Integer.parseInt(getRequiredArg(options, "size"));
        int length = Integer.parseInt(getRequiredArg(options, "length"));
        
        int[] result = Horner.hornerInv(k, size, length);
        
        Map<String, Object> data = new HashMap<>();
        data.put("result", result);
        data.put("k", k);
        data.put("size", size);
        data.put("length", length);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the hornerInteger command.
     */
    private void handleHornerInteger(Map<String, String> options) throws Exception {
        Integer[] args = parseIntegerArray(getRequiredArg(options, "args"));
        int size = Integer.parseInt(getRequiredArg(options, "size"));
        
        int result = Horner.horner(args, size);
        
        Map<String, Object> data = new HashMap<>();
        data.put("result", result);
        data.put("args", args);
        data.put("size", size);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the reverseArray command.
     */
    private void handleReverseArray(Map<String, String> options) throws Exception {
        int[] arr = parseIntArray(getRequiredArg(options, "arr"));
        
        int[] result = Horner.reverseArray(arr);
        
        Map<String, Object> data = new HashMap<>();
        data.put("result", result);
        data.put("input", arr);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the leftRightReverse command.
     */
    private void handleLeftRightReverse(Map<String, String> options) throws Exception {
        int[] values = parseIntArray(getRequiredArg(options, "values"));
        int algSize = Integer.parseInt(getRequiredArg(options, "algSize"));
        int arity = Integer.parseInt(getRequiredArg(options, "arity"));
        
        int[] result = Horner.leftRightReverse(values, algSize, arity);
        
        Map<String, Object> data = new HashMap<>();
        data.put("result", result);
        data.put("values", values);
        data.put("algSize", algSize);
        data.put("arity", arity);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the test command - runs the original main method test.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Run the original test from the main method
        String[] testArgs = {};
        org.uacalc.util.Horner.main(testArgs);
        
        Map<String, Object> data = new HashMap<>();
        data.put("message", "Test completed successfully");
        
        handleSuccess(data);
    }
    
    /**
     * Parse a comma-separated string of integers into an int array.
     */
    private int[] parseIntArray(String str) {
        if (str.trim().isEmpty()) {
            return new int[0];
        }
        
        return Arrays.stream(str.split(","))
                .map(String::trim)
                .mapToInt(Integer::parseInt)
                .toArray();
    }
    
    /**
     * Parse a comma-separated string of integers into an Integer array.
     */
    private Integer[] parseIntegerArray(String str) {
        if (str.trim().isEmpty()) {
            return new Integer[0];
        }
        
        return Arrays.stream(str.split(","))
                .map(String::trim)
                .map(Integer::parseInt)
                .toArray(Integer[]::new);
    }
    
    /**
     * Show usage information for the Horner wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "horner --args \"1,2,3\" --sizes \"4,5,6\"",
            "hornerInv --k 123 --sizes \"4,5,6\"",
            "hornerSameSize --args \"1,2,3\" --size 10",
            "hornerInvSameSize --k 123 --size 10 --length 3",
            "hornerInteger --args \"1,2,3\" --size 10",
            "reverseArray --arr \"1,2,3,4\"",
            "leftRightReverse --values \"0,1,2,3\" --algSize 2 --arity 2",
            "test"
        };
        
        showUsage("Horner", 
                 "CLI wrapper for org.uacalc.util.Horner encoding/decoding operations", 
                 examples);
    }
}
