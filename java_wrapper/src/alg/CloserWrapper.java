/* CloserWrapper.java - CLI wrapper for org.uacalc.alg.Closer
 * 
 * This wrapper exposes core methods of the Closer class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.util.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Closer class that provides command-line access
 * to core closure methods for testing and validation purposes.
 */
public class CloserWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Closer CLI wrapper.
     */
    public static void main(String[] args) {
        CloserWrapper wrapper = new CloserWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Closer wrapper failed", e);
        }
    }
    
    /**
     * Run the Closer CLI wrapper with the given arguments.
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
                
            case "sg_close":
                handleSgClose(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle test command - run basic functionality tests.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Create a simple power algebra for testing
        SmallAlgebra base = makeTestAlgebra(2); // 2-element algebra
        int power = getIntArg(options, "power", 2);
        
        BigProductAlgebra algebra = new BigProductAlgebra(base, power);
        
        // Create some generators
        List<IntArray> generators = new ArrayList<>();
        int[] arr1 = new int[power];
        for (int i = 0; i < power; i++) arr1[i] = 0;
        generators.add(new IntArray(arr1));
        
        int[] arr2 = new int[power];
        for (int i = 0; i < power; i++) arr2[i] = i % 2;
        generators.add(new IntArray(arr2));
        
        // Create closer
        Closer closer = new Closer(algebra, generators);
        closer.setSuppressOutput(true);
        
        // Compute closure
        List<IntArray> result = closer.sgClose();
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "test");
        response.put("power", power);
        response.put("base_size", base.cardinality());
        response.put("generators_count", generators.size());
        response.put("closure_size", result.size());
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle sg_close command - compute closure of generators.
     */
    private void handleSgClose(Map<String, String> options) throws Exception {
        // Get parameters
        int baseSize = getIntArg(options, "base_size", 2);
        int power = getIntArg(options, "power", 2);
        String gensStr = getRequiredArg(options, "generators");
        
        // Create algebra
        SmallAlgebra base = makeTestAlgebra(baseSize);
        BigProductAlgebra algebra = new BigProductAlgebra(base, power);
        
        // Parse generators
        List<IntArray> generators = parseGenerators(gensStr, power);
        
        // Create closer and compute closure
        Closer closer = new Closer(algebra, generators);
        closer.setSuppressOutput(true);
        
        List<IntArray> result = closer.sgClose();
        
        // Format result
        List<List<Integer>> resultList = new ArrayList<>();
        for (IntArray ia : result) {
            List<Integer> elem = new ArrayList<>();
            for (int i = 0; i < ia.universeSize(); i++) {
                elem.add(ia.get(i));
            }
            resultList.add(elem);
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "sg_close");
        response.put("base_size", baseSize);
        response.put("power", power);
        response.put("generators_count", generators.size());
        response.put("closure_size", result.size());
        response.put("closure", resultList);
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Create a simple test algebra with given size.
     */
    private SmallAlgebra makeTestAlgebra(int size) throws Exception {
        // Create a trivial algebra with no operations for testing
        return new BasicAlgebra("TestAlg", size, new ArrayList<>());
    }
    
    /**
     * Parse generators from a string representation.
     * Format: "[[0,1],[1,0]]" or similar
     */
    private List<IntArray> parseGenerators(String gensStr, int power) throws Exception {
        List<IntArray> generators = new ArrayList<>();
        
        // Simple parsing - expects format like "0,1;1,0" where ; separates generators
        String[] parts = gensStr.split(";");
        for (String part : parts) {
            String[] values = part.split(",");
            int[] arr = new int[power];
            for (int i = 0; i < Math.min(power, values.length); i++) {
                arr[i] = Integer.parseInt(values[i].trim());
            }
            generators.add(new IntArray(arr));
        }
        
        return generators;
    }
    
    /**
     * Show usage information for the Closer wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "test --power 2",
            "sg_close --base_size 2 --power 2 --generators \"0,0;0,1\"",
            "help"
        };
        
        showUsage("Closer", 
                 "CLI wrapper for org.uacalc.alg.Closer operations", 
                 examples);
    }
}

