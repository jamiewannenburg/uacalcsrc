/* MaltsevDecompositionIteratorWrapper.java - CLI wrapper for org.uacalc.alg.MaltsevDecompositionIterator
 * 
 * This wrapper exposes all public methods of the MaltsevDecompositionIterator class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.MaltsevDecompositionIterator;
import org.uacalc.alg.SmallAlgebra;
import org.uacalc.alg.BasicAlgebra;
import org.uacalc.io.AlgebraIO;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the MaltsevDecompositionIterator class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class MaltsevDecompositionIteratorWrapper extends WrapperBase {
    
    // Store the iterator for stateful operations
    private MaltsevDecompositionIterator iterator;
    private SmallAlgebra inputAlgebra;
    
    /**
     * Main entry point for the MaltsevDecompositionIterator CLI wrapper.
     */
    public static void main(String[] args) {
        MaltsevDecompositionIteratorWrapper wrapper = new MaltsevDecompositionIteratorWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("MaltsevDecompositionIterator wrapper failed", e);
        }
    }
    
    /**
     * Run the MaltsevDecompositionIterator CLI wrapper with the given arguments.
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
                handleTest(options);
                break;
                
            case "create":
                handleCreate(options);
                break;
                
            case "has_next":
                handleHasNext(options);
                break;
                
            case "next":
                handleNext(options);
                break;
                
            case "iterate":
                handleIterate(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the test command.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Create a simple idempotent algebra for testing
        SmallAlgebra alg = createIdempotentAlgebra("test", 3);
        
        MaltsevDecompositionIterator iter = new MaltsevDecompositionIterator(alg);
        
        // Test hasNext
        boolean hasNext = iter.hasNext();
        
        // Test next (if available)
        SmallAlgebra nextAlg = null;
        if (hasNext) {
            nextAlg = iter.next();
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test");
        result.put("has_next", hasNext);
        result.put("next_cardinality", nextAlg != null ? nextAlg.cardinality() : -1);
        handleSuccess(result);
    }
    
    /**
     * Handle the create command.
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        String algebraPath = getOptionalArg(options, "algebra_path", "");
        
        SmallAlgebra alg;
        if (algebraPath != null && !algebraPath.isEmpty()) {
            // Load algebra from file
            alg = AlgebraIO.readAlgebraFile(algebraPath);
        } else {
            // Create a default idempotent algebra
            String name = getOptionalArg(options, "name", "test");
            int cardinality = getIntArg(options, "cardinality", 3);
            alg = createIdempotentAlgebra(name, cardinality);
        }
        
        // Store input algebra
        this.inputAlgebra = alg;
        
        // Create iterator
        this.iterator = new MaltsevDecompositionIterator(alg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "create");
        result.put("algebra_name", alg.getName());
        result.put("algebra_cardinality", alg.cardinality());
        result.put("has_next", iterator.hasNext());
        result.put("created", true);
        handleSuccess(result);
    }
    
    /**
     * Handle the has_next command.
     */
    private void handleHasNext(Map<String, String> options) throws Exception {
        if (iterator == null) {
            handleError("Iterator not created. Use 'create' command first.", null);
            return;
        }
        
        boolean hasNext = iterator.hasNext();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "has_next");
        result.put("has_next", hasNext);
        handleSuccess(result);
    }
    
    /**
     * Handle the next command.
     */
    private void handleNext(Map<String, String> options) throws Exception {
        if (iterator == null) {
            handleError("Iterator not created. Use 'create' command first.", null);
            return;
        }
        
        if (!iterator.hasNext()) {
            handleError("No more elements in iterator", null);
            return;
        }
        
        SmallAlgebra alg = iterator.next();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "next");
        result.put("cardinality", alg.cardinality());
        result.put("algebra_name", alg.getName());
        result.put("has_next", iterator.hasNext());
        handleSuccess(result);
    }
    
    /**
     * Handle the iterate command - iterate through all algebras and print cardinalities.
     */
    private void handleIterate(Map<String, String> options) throws Exception {
        String algebraPath = getOptionalArg(options, "algebra_path", "");
        
        SmallAlgebra alg;
        if (algebraPath != null && !algebraPath.isEmpty()) {
            // Load algebra from file
            alg = AlgebraIO.readAlgebraFile(algebraPath);
        } else {
            // Create a default idempotent algebra
            String name = getOptionalArg(options, "name", "test");
            int cardinality = getIntArg(options, "cardinality", 3);
            alg = createIdempotentAlgebra(name, cardinality);
        }
        
        MaltsevDecompositionIterator iter = new MaltsevDecompositionIterator(alg);
        
        List<Integer> cardinalities = new ArrayList<>();
        int count = 0;
        while (iter.hasNext()) {
            SmallAlgebra nextAlg = iter.next();
            cardinalities.add(nextAlg.cardinality());
            count++;
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "iterate");
        result.put("count", count);
        result.put("cardinalities", cardinalities);
        handleSuccess(result);
    }
    
    /**
     * Create a simple idempotent algebra for testing.
     */
    private SmallAlgebra createIdempotentAlgebra(String name, int cardinality) {
        // Create a BasicAlgebra with no operations (trivially idempotent)
        return new BasicAlgebra(name, cardinality, new ArrayList<>());
    }
    
    /**
     * Show usage information for the MaltsevDecompositionIterator wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "java MaltsevDecompositionIteratorWrapper test",
            "java MaltsevDecompositionIteratorWrapper create --name test --cardinality 3",
            "java MaltsevDecompositionIteratorWrapper create --algebra_path resources/algebras/n5.ua",
            "java MaltsevDecompositionIteratorWrapper has_next",
            "java MaltsevDecompositionIteratorWrapper next",
            "java MaltsevDecompositionIteratorWrapper iterate --name test --cardinality 3",
            "java MaltsevDecompositionIteratorWrapper iterate --algebra_path resources/algebras/n5.ua"
        };
        
        showUsage("MaltsevDecompositionIterator", 
                 "CLI wrapper for org.uacalc.alg.MaltsevDecompositionIterator operations", 
                 examples);
    }
}

