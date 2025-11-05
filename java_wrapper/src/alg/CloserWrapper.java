/* CloserWrapper.java - CLI wrapper for org.uacalc.alg.Closer
 * 
 * This wrapper exposes core methods of the Closer class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import java.io.*;
import org.uacalc.alg.*;
import org.uacalc.util.*;
import org.uacalc.io.*;
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
                
            case "sg_close_ba2_power":
                handleSgCloseBa2Power(options);
                break;
                
            case "sg_close_free_algebra":
                handleSgCloseFreeAlgebra(options);
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
     * Handle sg_close_ba2_power command - compute closure with ba2 power algebra.
     */
    private void handleSgCloseBa2Power(Map<String, String> options) throws Exception {
        // Get parameters
        int power = getIntArg(options, "power", 2);
        String gensStr = getRequiredArg(options, "generators");
        
        // Load ba2 algebra
        SmallAlgebra ba2 = loadBa2();
        
        // Create power algebra
        BigProductAlgebra algebra = new BigProductAlgebra(ba2, power);
        
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
        response.put("command", "sg_close_ba2_power");
        response.put("power", power);
        response.put("base_size", ba2.cardinality());
        response.put("generators_count", generators.size());
        response.put("closure_size", result.size());
        response.put("closure", resultList);
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle sg_close_free_algebra command - compute closure with free algebra.
     */
    private void handleSgCloseFreeAlgebra(Map<String, String> options) throws Exception {
        // Get parameters
        int numGens = getIntArg(options, "num_gens", 1);
        int power = getIntArg(options, "power", 2);
        String gensStr = getRequiredArg(options, "generators");
        
        // Load ba2 and create free algebra
        SmallAlgebra ba2 = loadBa2();
        FreeAlgebra freeAlg = new FreeAlgebra(ba2, numGens);
        freeAlg.makeOperationTables();
        
        // Create power algebra from free algebra
        BigProductAlgebra algebra = new BigProductAlgebra(freeAlg, power);
        
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
        response.put("command", "sg_close_free_algebra");
        response.put("num_gens", numGens);
        response.put("power", power);
        response.put("base_size", freeAlg.cardinality());
        response.put("generators_count", generators.size());
        response.put("closure_size", result.size());
        response.put("closure", resultList);
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Load ba2 algebra from resources/algebras/ba2.ua
     */
    private SmallAlgebra loadBa2() throws Exception {
        // Try to find ba2.ua file
        String[] possiblePaths = {
            "resources/algebras/ba2.ua",
            "algebras/ba2.ua",
            "../resources/algebras/ba2.ua"
        };
        
        File ba2File = null;
        for (String path : possiblePaths) {
            File f = new File(path);
            if (f.exists()) {
                ba2File = f;
                break;
            }
        }
        
        if (ba2File == null) {
            // Try loading from classpath
            ClassLoader cl = Thread.currentThread().getContextClassLoader();
            InputStream is = cl.getResourceAsStream("algebras/ba2.ua");
            if (is != null) {
                return AlgebraIO.readAlgebraFromStream(is);
            }
            throw new Exception("ba2.ua not found in any expected location");
        }
        
        return AlgebraIO.readAlgebraFile(ba2File);
    }
    
    /**
     * Show usage information for the Closer wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "test --power 2",
            "sg_close --base_size 2 --power 2 --generators \"0,0;0,1\"",
            "sg_close_ba2_power --power 3 --generators \"0,0,1;1,1,0\"",
            "sg_close_free_algebra --num_gens 1 --power 3 --generators \"0,0,1;1,1,0\"",
            "help"
        };
        
        showUsage("Closer", 
                 "CLI wrapper for org.uacalc.alg.Closer operations", 
                 examples);
    }
}

