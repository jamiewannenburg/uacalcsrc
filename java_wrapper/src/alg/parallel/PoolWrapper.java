/* PoolWrapper.java - CLI wrapper for org.uacalc.alg.parallel.Pool
 * 
 * This wrapper exposes the static Pool.fjPool field through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg.parallel;

import java.util.*;
import org.uacalc.alg.parallel.Pool;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Pool class that provides command-line access
 * to the static fjPool field for testing and validation purposes.
 */
public class PoolWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Pool CLI wrapper.
     */
    public static void main(String[] args) {
        PoolWrapper wrapper = new PoolWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Pool wrapper failed", e);
        }
    }
    
    /**
     * Run the Pool CLI wrapper with the given arguments.
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
                
            case "get_pool":
                handleGetPool(options);
                break;
                
            case "is_initialized":
                handleIsInitialized(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle get_pool command - check if pool is initialized
     */
    private void handleGetPool(Map<String, String> options) throws Exception {
        // Use reflection to access the package-private fjPool field
        java.lang.reflect.Field field = Pool.class.getDeclaredField("fjPool");
        field.setAccessible(true);
        Object pool = field.get(null);
        boolean initialized = pool != null;
        handleSuccess(initialized);
    }
    
    /**
     * Handle is_initialized command - verify pool initialization
     */
    private void handleIsInitialized(Map<String, String> options) throws Exception {
        // Use reflection to access the package-private fjPool field
        java.lang.reflect.Field field = Pool.class.getDeclaredField("fjPool");
        field.setAccessible(true);
        Object pool = field.get(null);
        boolean initialized = pool != null;
        handleSuccess(initialized);
    }
    
    /**
     * Handle test command - run basic functionality tests
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Use reflection to access the package-private fjPool field
        java.lang.reflect.Field field = Pool.class.getDeclaredField("fjPool");
        field.setAccessible(true);
        
        // Test pool initialization
        Object pool1 = field.get(null);
        boolean initialized = pool1 != null;
        
        // Access the pool multiple times to verify it's the same instance
        Object pool2 = field.get(null);
        boolean same_instance = (pool1 == pool2);
        
        // Create JSON structure matching Python test
        String json = String.format(
            "{\"initialized\":%s,\"same_instance\":%s}",
            initialized, same_instance
        );
        
        handleSuccess(json);
    }
    
    /**
     * Show usage information for the Pool wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "get_pool - Check if pool is initialized",
            "is_initialized - Verify pool initialization",
            "test - Run basic functionality tests"
        };
        
        showUsage("Pool", 
                 "CLI wrapper for org.uacalc.alg.parallel.Pool", 
                 examples);
    }
}

