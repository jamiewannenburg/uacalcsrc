/* BadAlgebraFileExceptionWrapper.java - CLI wrapper for org.uacalc.io.BadAlgebraFileException
 * 
 * This wrapper exposes all public methods of the BadAlgebraFileException class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.io;

import java.util.*;
import org.uacalc.io.BadAlgebraFileException;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the BadAlgebraFileException class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class BadAlgebraFileExceptionWrapper extends WrapperBase {
    
    /**
     * Main entry point for the BadAlgebraFileException CLI wrapper.
     */
    public static void main(String[] args) {
        BadAlgebraFileExceptionWrapper wrapper = new BadAlgebraFileExceptionWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("BadAlgebraFileException wrapper failed", e);
        }
    }
    
    /**
     * Run the BadAlgebraFileException CLI wrapper with the given arguments.
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
                
            case "test":
                handleTest();
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the create command - create a new BadAlgebraFileException instance.
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        String message = getRequiredArg(options, "message");
        
        BadAlgebraFileException exception = new BadAlgebraFileException(message);
        
        Map<String, Object> result = new HashMap<>();
        result.put("message", exception.getMessage());
        result.put("class_name", exception.getClass().getSimpleName());
        result.put("string_representation", exception.toString());
        
        handleSuccess(result);
    }
    
    /**
     * Handle the test command - run basic functionality tests.
     */
    private void handleTest() throws Exception {
        Map<String, Object> testResults = new HashMap<>();
        
        // Test 1: Create exception with simple message
        try {
            BadAlgebraFileException ex1 = new BadAlgebraFileException("Test message");
            testResults.put("test1_create_simple", Map.of(
                "success", true,
                "message", ex1.getMessage(),
                "class_name", ex1.getClass().getSimpleName()
            ));
        } catch (Exception e) {
            testResults.put("test1_create_simple", Map.of(
                "success", false,
                "error", e.getMessage()
            ));
        }
        
        // Test 2: Create exception with empty message
        try {
            BadAlgebraFileException ex2 = new BadAlgebraFileException("");
            testResults.put("test2_create_empty", Map.of(
                "success", true,
                "message", ex2.getMessage(),
                "is_empty", ex2.getMessage().isEmpty()
            ));
        } catch (Exception e) {
            testResults.put("test2_create_empty", Map.of(
                "success", false,
                "error", e.getMessage()
            ));
        }
        
        // Test 3: Create exception with special characters
        try {
            String specialMessage = "Error: File 'test\\file.txt' not found!\nLine 42: Invalid format";
            BadAlgebraFileException ex3 = new BadAlgebraFileException(specialMessage);
            testResults.put("test3_create_special_chars", Map.of(
                "success", true,
                "message", ex3.getMessage(),
                "contains_newline", ex3.getMessage().contains("\n"),
                "contains_backslash", ex3.getMessage().contains("\\")
            ));
        } catch (Exception e) {
            testResults.put("test3_create_special_chars", Map.of(
                "success", false,
                "error", e.getMessage()
            ));
        }
        
        // Test 4: Test toString method
        try {
            BadAlgebraFileException ex4 = new BadAlgebraFileException("toString test");
            String toString = ex4.toString();
            testResults.put("test4_to_string", Map.of(
                "success", true,
                "toString", toString,
                "contains_class_name", toString.contains("BadAlgebraFileException"),
                "contains_message", toString.contains("toString test")
            ));
        } catch (Exception e) {
            testResults.put("test4_to_string", Map.of(
                "success", false,
                "error", e.getMessage()
            ));
        }
        
        handleSuccess(testResults);
    }
    
    /**
     * Show usage information for the BadAlgebraFileException wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "BadAlgebraFileExceptionWrapper create --message \"File not found\"",
            "BadAlgebraFileExceptionWrapper test",
            "BadAlgebraFileExceptionWrapper help"
        };
        
        showUsage("BadAlgebraFileExceptionWrapper", 
                 "CLI wrapper for org.uacalc.io.BadAlgebraFileException operations", 
                 examples);
    }
}
