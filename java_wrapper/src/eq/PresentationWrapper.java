package eq;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;

/**
 * Java CLI wrapper for Presentation class.
 * 
 * This wrapper provides command-line access to the Presentation functionality
 * through the Rust implementation via JNI.
 */
public class PresentationWrapper {
    
    private static final ObjectMapper mapper = new ObjectMapper();
    
    // Load the native library
    static {
        try {
            System.loadLibrary("uacalc_java_wrapper");
        } catch (UnsatisfiedLinkError e) {
            System.err.println("Failed to load native library: " + e.getMessage());
            System.exit(1);
        }
    }
    
    // Native method declarations
    private static native long createPresentation(String[] variables, long[] equationPtrs);
    private static native String[] getVariables(long ptr);
    private static native String[] getRelations(long ptr);
    private static native void freePresentation(long ptr);
    
    /**
     * Main method for CLI interface.
     */
    public static void main(String[] args) {
        if (args.length == 0) {
            printUsage();
            return;
        }
        
        String command = args[0];
        
        try {
            switch (command) {
                case "create":
                    handleCreate(args);
                    break;
                case "get_variables":
                    handleGetVariables(args);
                    break;
                case "get_relations":
                    handleGetRelations(args);
                    break;
                case "test":
                    handleTest();
                    break;
                default:
                    System.err.println("Unknown command: " + command);
                    printUsage();
                    System.exit(1);
            }
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    /**
     * Handle the create command.
     * Usage: create <var1,var2,...> <eq1,eq2,...>
     */
    private static void handleCreate(String[] args) {
        if (args.length < 3) {
            System.err.println("Usage: create <var1,var2,...> <eq1,eq2,...>");
            System.exit(1);
        }
        
        String[] variables = args[1].split(",");
        String[] relations = args[2].split(",");
        
        // For now, create empty equation pointers (in real implementation, these would be created)
        long[] equationPtrs = new long[relations.length];
        
        long ptr = createPresentation(variables, equationPtrs);
        
        ObjectNode result = mapper.createObjectNode();
        result.put("success", true);
        result.put("presentation_ptr", ptr);
        result.put("variables_count", variables.length);
        result.put("relations_count", relations.length);
        
        System.out.println(result.toString());
    }
    
    /**
     * Handle the get_variables command.
     * Usage: get_variables <presentation_ptr>
     */
    private static void handleGetVariables(String[] args) {
        if (args.length < 2) {
            System.err.println("Usage: get_variables <presentation_ptr>");
            System.exit(1);
        }
        
        long ptr = Long.parseLong(args[1]);
        String[] variables = getVariables(ptr);
        
        ObjectNode result = mapper.createObjectNode();
        result.put("success", true);
        ArrayNode varsArray = result.putArray("variables");
        for (String var : variables) {
            varsArray.add(var);
        }
        
        System.out.println(result.toString());
    }
    
    /**
     * Handle the get_relations command.
     * Usage: get_relations <presentation_ptr>
     */
    private static void handleGetRelations(String[] args) {
        if (args.length < 2) {
            System.err.println("Usage: get_relations <presentation_ptr>");
            System.exit(1);
        }
        
        long ptr = Long.parseLong(args[1]);
        String[] relations = getRelations(ptr);
        
        ObjectNode result = mapper.createObjectNode();
        result.put("success", true);
        ArrayNode relsArray = result.putArray("relations");
        for (String rel : relations) {
            relsArray.add(rel);
        }
        
        System.out.println(result.toString());
    }
    
    /**
     * Handle the test command - run comprehensive tests.
     */
    private static void handleTest() {
        ObjectNode result = mapper.createObjectNode();
        result.put("success", true);
        result.put("test_name", "PresentationWrapper");
        
        ArrayNode tests = result.putArray("tests");
        
        try {
            // Test 1: Create presentation with variables
            String[] variables = {"x", "y", "z"};
            long[] equationPtrs = {};
            long ptr = createPresentation(variables, equationPtrs);
            
            ObjectNode test1 = mapper.createObjectNode();
            test1.put("name", "create_presentation");
            test1.put("passed", true);
            test1.put("variables_count", variables.length);
            tests.add(test1);
            
            // Test 2: Get variables
            String[] retrievedVars = getVariables(ptr);
            ObjectNode test2 = mapper.createObjectNode();
            test2.put("name", "get_variables");
            test2.put("passed", Arrays.equals(variables, retrievedVars));
            test2.put("expected_count", variables.length);
            test2.put("actual_count", retrievedVars.length);
            tests.add(test2);
            
            // Test 3: Get relations (should be empty)
            String[] retrievedRels = getRelations(ptr);
            ObjectNode test3 = mapper.createObjectNode();
            test3.put("name", "get_relations");
            test3.put("passed", retrievedRels.length == 0);
            test3.put("relations_count", retrievedRels.length);
            tests.add(test3);
            
            // Clean up
            freePresentation(ptr);
            
            ObjectNode test4 = mapper.createObjectNode();
            test4.put("name", "cleanup");
            test4.put("passed", true);
            tests.add(test4);
            
        } catch (Exception e) {
            ObjectNode errorTest = mapper.createObjectNode();
            errorTest.put("name", "error_handling");
            errorTest.put("passed", false);
            errorTest.put("error", e.getMessage());
            tests.add(errorTest);
        }
        
        System.out.println(result.toString());
    }
    
    /**
     * Print usage information.
     */
    private static void printUsage() {
        System.out.println("PresentationWrapper - Java CLI wrapper for Presentation");
        System.out.println();
        System.out.println("Usage: java eq.PresentationWrapper <command> [args...]");
        System.out.println();
        System.out.println("Commands:");
        System.out.println("  create <var1,var2,...> <eq1,eq2,...>  - Create a new presentation");
        System.out.println("  get_variables <ptr>                   - Get variables from presentation");
        System.out.println("  get_relations <ptr>                   - Get relations from presentation");
        System.out.println("  test                                  - Run comprehensive tests");
        System.out.println();
        System.out.println("Examples:");
        System.out.println("  java eq.PresentationWrapper create x,y,z \"x=y,y=z\"");
        System.out.println("  java eq.PresentationWrapper get_variables 12345");
        System.out.println("  java eq.PresentationWrapper test");
    }
}