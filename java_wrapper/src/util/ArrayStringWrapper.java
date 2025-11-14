/* ArrayStringWrapper.java - CLI wrapper for org.uacalc.util.ArrayString
 * 
 * This wrapper exposes all public methods of the ArrayString class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.util;

import java.util.*;
import org.uacalc.util.ArrayString;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the ArrayString class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class ArrayStringWrapper extends WrapperBase {
    
    /**
     * Main entry point for the ArrayString CLI wrapper.
     */
    public static void main(String[] args) {
        ArrayStringWrapper wrapper = new ArrayStringWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("ArrayString wrapper failed", e);
        }
    }
    
    /**
     * Run the ArrayString CLI wrapper with the given arguments.
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
                
            case "to_string":
                handleToString(options);
                break;
                
            case "to_string_int":
                handleToStringInt(options);
                break;
                
            case "to_string_2d_int":
                handleToString2DInt(options);
                break;
                
            case "to_string_str":
                handleToStringStr(options);
                break;
                
            case "to_string_2d_str":
                handleToString2DStr(options);
                break;
                
            case "value_of":
                handleValueOf(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle to_string command - convert array to string
     */
    private void handleToString(Map<String, String> options) throws Exception {
        String arrayStr = getRequiredArg(options, "array");
        Object array = parseArray(arrayStr);
        String result = ArrayString.toString(array);
        handleSuccess(result);
    }
    
    /**
     * Handle to_string_int command - convert integer array to string
     */
    private void handleToStringInt(Map<String, String> options) throws Exception {
        String arrayStr = getRequiredArg(options, "array");
        int[] array = parseIntArray(arrayStr);
        String result = ArrayString.toString(array);
        handleSuccess(result);
    }
    
    /**
     * Handle to_string_2d_int command - convert 2D integer array to string
     */
    private void handleToString2DInt(Map<String, String> options) throws Exception {
        String arrayStr = getRequiredArg(options, "array");
        int[][] array = parseInt2DArray(arrayStr);
        String result = ArrayString.toString(array);
        handleSuccess(result);
    }
    
    /**
     * Handle to_string_str command - convert string array to string
     */
    private void handleToStringStr(Map<String, String> options) throws Exception {
        String arrayStr = getRequiredArg(options, "array");
        String[] array = parseStringArray(arrayStr);
        String result = ArrayString.toString(array);
        handleSuccess(result);
    }
    
    /**
     * Handle to_string_2d_str command - convert 2D string array to string
     */
    private void handleToString2DStr(Map<String, String> options) throws Exception {
        String arrayStr = getRequiredArg(options, "array");
        String[][] array = parseString2DArray(arrayStr);
        String result = ArrayString.toString(array);
        handleSuccess(result);
    }
    
    /**
     * Handle value_of command - convert value to string
     */
    private void handleValueOf(Map<String, String> options) throws Exception {
        String value = getRequiredArg(options, "value");
        String result = ArrayString.toString(value);
        handleSuccess(result);
    }
    
    /**
     * Handle test command - run basic functionality tests
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Test integer array
        int[] intArray = {1, 2, 3};
        String intResult = ArrayString.toString(intArray);
        
        // Test string array
        String[] strArray = {"hello", "world"};
        String strResult = ArrayString.toString(strArray);
        
        // Test 2D integer array
        int[][] int2DArray = {{1, 2}, {3, 4}};
        String int2DResult = ArrayString.toString(int2DArray);
        
        // Test 2D string array
        String[][] str2DArray = {{"a", "b"}, {"c", "d"}};
        String str2DResult = ArrayString.toString(str2DArray);
        
        // Test empty array
        int[] emptyArray = {};
        String emptyResult = ArrayString.toString(emptyArray);
        
        // Test single element array
        int[] singleArray = {42};
        String singleResult = ArrayString.toString(singleArray);
        
        // Test null value
        String nullResult = ArrayString.toString(null);
        
        // Test non-array value
        String nonArrayResult = ArrayString.toString("not an array");
        
        // Create JSON structure matching Python test
        String json = String.format(
            "{\"int_array\":\"%s\",\"str_array\":\"%s\",\"int_2d_array\":\"%s\",\"str_2d_array\":\"%s\",\"empty_array\":\"%s\",\"single_array\":\"%s\",\"null_value\":\"%s\",\"non_array\":\"%s\"}",
            intResult, strResult, int2DResult, str2DResult, emptyResult, singleResult, nullResult, nonArrayResult
        );
        
        handleSuccess(json);
    }
    
    /**
     * Parse a generic array from string representation
     */
    private Object parseArray(String arrayStr) throws Exception {
        // For simplicity, try to parse as integer array first
        try {
            return parseIntArray(arrayStr);
        } catch (Exception e) {
            // If that fails, try string array
            return parseStringArray(arrayStr);
        }
    }
    
    /**
     * Parse integer array from string representation
     */
    private int[] parseIntArray(String arrayStr) throws Exception {
        if (arrayStr.trim().equals("[]")) {
            return new int[0];
        }
        
        // Remove brackets and split by comma
        String content = arrayStr.trim();
        if (content.startsWith("[") && content.endsWith("]")) {
            content = content.substring(1, content.length() - 1);
        }
        
        if (content.trim().isEmpty()) {
            return new int[0];
        }
        
        String[] parts = content.split(",");
        int[] result = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            result[i] = Integer.parseInt(parts[i].trim());
        }
        return result;
    }
    
    /**
     * Parse 2D integer array from string representation
     */
    private int[][] parseInt2DArray(String arrayStr) throws Exception {
        if (arrayStr.trim().equals("[]")) {
            return new int[0][0];
        }
        
        // Remove outer brackets and split by inner arrays
        String content = arrayStr.trim();
        if (content.startsWith("[") && content.endsWith("]")) {
            content = content.substring(1, content.length() - 1);
        }
        
        if (content.trim().isEmpty()) {
            return new int[0][0];
        }
        
        // Split by "],[" pattern
        String[] parts = content.split("\\],\\[");
        int[][] result = new int[parts.length][];
        
        for (int i = 0; i < parts.length; i++) {
            String part = parts[i];
            // Remove remaining brackets
            if (part.startsWith("[")) {
                part = part.substring(1);
            }
            if (part.endsWith("]")) {
                part = part.substring(0, part.length() - 1);
            }
            
            if (part.trim().isEmpty()) {
                result[i] = new int[0];
            } else {
                String[] elements = part.split(",");
                result[i] = new int[elements.length];
                for (int j = 0; j < elements.length; j++) {
                    result[i][j] = Integer.parseInt(elements[j].trim());
                }
            }
        }
        
        return result;
    }
    
    /**
     * Parse string array from string representation
     */
    private String[] parseStringArray(String arrayStr) throws Exception {
        if (arrayStr.trim().equals("[]")) {
            return new String[0];
        }
        
        // Remove brackets and split by comma
        String content = arrayStr.trim();
        if (content.startsWith("[") && content.endsWith("]")) {
            content = content.substring(1, content.length() - 1);
        }
        
        if (content.trim().isEmpty()) {
            return new String[0];
        }
        
        String[] parts = content.split(",");
        String[] result = new String[parts.length];
        for (int i = 0; i < parts.length; i++) {
            result[i] = parts[i].trim();
        }
        return result;
    }
    
    /**
     * Parse 2D string array from string representation
     */
    private String[][] parseString2DArray(String arrayStr) throws Exception {
        if (arrayStr.trim().equals("[]")) {
            return new String[0][0];
        }
        
        // Remove outer brackets and split by inner arrays
        String content = arrayStr.trim();
        if (content.startsWith("[") && content.endsWith("]")) {
            content = content.substring(1, content.length() - 1);
        }
        
        if (content.trim().isEmpty()) {
            return new String[0][0];
        }
        
        // Split by "],[" pattern
        String[] parts = content.split("\\],\\[");
        String[][] result = new String[parts.length][];
        
        for (int i = 0; i < parts.length; i++) {
            String part = parts[i];
            // Remove remaining brackets
            if (part.startsWith("[")) {
                part = part.substring(1);
            }
            if (part.endsWith("]")) {
                part = part.substring(0, part.length() - 1);
            }
            
            if (part.trim().isEmpty()) {
                result[i] = new String[0];
            } else {
                String[] elements = part.split(",");
                result[i] = new String[elements.length];
                for (int j = 0; j < elements.length; j++) {
                    result[i][j] = elements[j].trim();
                }
            }
        }
        
        return result;
    }
    
    /**
     * Show usage information for the ArrayString wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "to_string --array \"[1,2,3]\"",
            "to_string_int --array \"[1,2,3]\"",
            "to_string_2d_int --array \"[[1,2],[3,4]]\"",
            "to_string_str --array \"[hello,world]\"",
            "to_string_2d_str --array \"[[a,b],[c,d]]\"",
            "value_of --value \"hello\"",
            "test"
        };
        
        showUsage("ArrayString", 
                 "CLI wrapper for org.uacalc.util.ArrayString operations", 
                 examples);
    }
}
