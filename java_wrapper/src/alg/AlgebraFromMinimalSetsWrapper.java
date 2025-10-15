/* AlgebraFromMinimalSetsWrapper.java - CLI wrapper for org.uacalc.alg.AlgebraFromMinimalSets
 * 
 * This wrapper exposes all public methods of the AlgebraFromMinimalSets class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.AlgebraFromMinimalSets;
import org.uacalc.alg.SmallAlgebra;
import org.uacalc.alg.BasicAlgebra;
import org.uacalc.alg.op.Operation;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the AlgebraFromMinimalSets class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class AlgebraFromMinimalSetsWrapper extends WrapperBase {
    
    /**
     * Main entry point for the AlgebraFromMinimalSets CLI wrapper.
     */
    public static void main(String[] args) {
        AlgebraFromMinimalSetsWrapper wrapper = new AlgebraFromMinimalSetsWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("AlgebraFromMinimalSets wrapper failed", e);
        }
    }
    
    /**
     * Run the AlgebraFromMinimalSets CLI wrapper with the given arguments.
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
                
            case "construct_basic":
                handleConstructBasic(options);
                break;
                
            case "construct_with_maps":
                handleConstructWithMaps(options);
                break;
                
            case "construct_with_name":
                handleConstructWithName(options);
                break;
                
            case "construct_with_connecting_points":
                handleConstructWithConnectingPoints(options);
                break;
                
            case "construct_full":
                handleConstructFull(options);
                break;
                
            case "get_info":
                handleGetInfo(options);
                break;
                
            case "test_main":
                handleTestMain(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the basic constructor: AlgebraFromMinimalSets(SmallAlgebra minAlg)
     */
    private void handleConstructBasic(Map<String, String> options) throws Exception {
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        
        // Create a basic minimal algebra
        SmallAlgebra minAlg = new BasicAlgebra("minimal", minAlgSize, new ArrayList<Operation>());
        
        // Create AlgebraFromMinimalSets
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(minAlg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "construct_basic");
        result.put("min_alg_size", minAlgSize);
        result.put("cardinality", alg.cardinality());
        result.put("name", alg.name());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Handle constructor with maps: AlgebraFromMinimalSets(SmallAlgebra minAlg, int algSize, List<int[]> maps)
     */
    private void handleConstructWithMaps(Map<String, String> options) throws Exception {
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        int algSize = getIntArg(options, "alg_size", 7);
        
        // Create a basic minimal algebra
        SmallAlgebra minAlg = new BasicAlgebra("minimal", minAlgSize, new ArrayList<Operation>());
        
        // Create some example maps (for simplicity, we'll use null to get default maps)
        List<int[]> maps = null;
        
        // Create AlgebraFromMinimalSets
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(minAlg, algSize, maps);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "construct_with_maps");
        result.put("min_alg_size", minAlgSize);
        result.put("alg_size", algSize);
        result.put("cardinality", alg.cardinality());
        result.put("name", alg.name());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Handle constructor with name: AlgebraFromMinimalSets(String name, SmallAlgebra minAlg)
     */
    private void handleConstructWithName(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        
        // Create a basic minimal algebra
        SmallAlgebra minAlg = new BasicAlgebra("minimal", minAlgSize, new ArrayList<Operation>());
        
        // Create AlgebraFromMinimalSets
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(name, minAlg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "construct_with_name");
        result.put("name", name);
        result.put("min_alg_size", minAlgSize);
        result.put("cardinality", alg.cardinality());
        result.put("actual_name", alg.name());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Handle constructor with connecting points: AlgebraFromMinimalSets(String name, SmallAlgebra minAlg, List<Integer> connectPts)
     */
    private void handleConstructWithConnectingPoints(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        String connectPtsStr = getOptionalArg(options, "connect_pts", "1,2");
        
        // Parse connecting points
        List<Integer> connectPts = new ArrayList<>();
        if (connectPtsStr != null && !connectPtsStr.isEmpty()) {
            String[] parts = connectPtsStr.split(",");
            for (String part : parts) {
                connectPts.add(Integer.parseInt(part.trim()));
            }
        }
        
        // Create a basic minimal algebra
        SmallAlgebra minAlg = new BasicAlgebra("minimal", minAlgSize, new ArrayList<Operation>());
        
        // Create AlgebraFromMinimalSets
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(name, minAlg, connectPts);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "construct_with_connecting_points");
        result.put("name", name);
        result.put("min_alg_size", minAlgSize);
        result.put("connect_pts", connectPts);
        result.put("cardinality", alg.cardinality());
        result.put("actual_name", alg.name());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Handle full constructor: AlgebraFromMinimalSets(String name, SmallAlgebra minAlg, int algSize, List<int[]> maps, List<Integer> connectPts)
     */
    private void handleConstructFull(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        int algSize = getIntArg(options, "alg_size", 7);
        String connectPtsStr = getOptionalArg(options, "connect_pts", "1,2");
        
        // Parse connecting points
        List<Integer> connectPts = new ArrayList<>();
        if (connectPtsStr != null && !connectPtsStr.isEmpty()) {
            String[] parts = connectPtsStr.split(",");
            for (String part : parts) {
                connectPts.add(Integer.parseInt(part.trim()));
            }
        }
        
        // Create a basic minimal algebra
        SmallAlgebra minAlg = new BasicAlgebra("minimal", minAlgSize, new ArrayList<Operation>());
        
        // Create some example maps (for simplicity, we'll use null to get default maps)
        List<int[]> maps = null;
        
        // Create AlgebraFromMinimalSets
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(name, minAlg, algSize, maps, connectPts);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "construct_full");
        result.put("name", name);
        result.put("min_alg_size", minAlgSize);
        result.put("alg_size", algSize);
        result.put("connect_pts", connectPts);
        result.put("cardinality", alg.cardinality());
        result.put("actual_name", alg.name());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Handle getting basic information about an algebra.
     */
    private void handleGetInfo(Map<String, String> options) throws Exception {
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        
        // Create a basic minimal algebra
        SmallAlgebra minAlg = new BasicAlgebra("minimal", minAlgSize, new ArrayList<Operation>());
        
        // Create AlgebraFromMinimalSets
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(minAlg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_info");
        result.put("min_alg_size", minAlgSize);
        result.put("cardinality", alg.cardinality());
        result.put("name", alg.name());
        result.put("operations_count", alg.operations().size());
        result.put("is_total", alg.isTotal());
        result.put("is_idempotent", alg.isIdempotent());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Handle testing the static main method.
     */
    private void handleTestMain(Map<String, String> options) throws Exception {
        // Call the static main method
        String[] mainArgs = {};
        AlgebraFromMinimalSets.main(mainArgs);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test_main");
        result.put("status", "completed");
        
        handleSuccess(result);
    }
    
    /**
     * Handle running basic functionality tests.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        boolean allPassed = true;
        List<String> testResults = new ArrayList<>();
        
        try {
            // Test 1: Basic constructor
            SmallAlgebra minAlg1 = new BasicAlgebra("minimal", 3, new ArrayList<Operation>());
            AlgebraFromMinimalSets alg1 = new AlgebraFromMinimalSets(minAlg1);
            if (alg1.cardinality() != 7) {
                allPassed = false;
                testResults.add("Test 1 FAILED: Expected cardinality 7, got " + alg1.cardinality());
            } else {
                testResults.add("Test 1 PASSED: Basic constructor");
            }
            
            // Test 2: Constructor with name
            SmallAlgebra minAlg2 = new BasicAlgebra("minimal", 3, new ArrayList<Operation>());
            AlgebraFromMinimalSets alg2 = new AlgebraFromMinimalSets("TestAlgebra", minAlg2);
            if (!alg2.name().equals("TestAlgebra")) {
                allPassed = false;
                testResults.add("Test 2 FAILED: Expected name 'TestAlgebra', got '" + alg2.name() + "'");
            } else {
                testResults.add("Test 2 PASSED: Constructor with name");
            }
            
            // Test 3: Constructor with connecting points
            SmallAlgebra minAlg3 = new BasicAlgebra("minimal", 3, new ArrayList<Operation>());
            List<Integer> connectPts = Arrays.asList(1, 2);
            AlgebraFromMinimalSets alg3 = new AlgebraFromMinimalSets("TestAlgebra", minAlg3, connectPts);
            if (alg3.cardinality() != 7) {
                allPassed = false;
                testResults.add("Test 3 FAILED: Expected cardinality 7, got " + alg3.cardinality());
            } else {
                testResults.add("Test 3 PASSED: Constructor with connecting points");
            }
            
        } catch (Exception e) {
            allPassed = false;
            testResults.add("Test FAILED with exception: " + e.getMessage());
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test");
        result.put("all_passed", allPassed);
        result.put("test_results", testResults);
        result.put("status", allPassed ? "success" : "failure");
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the AlgebraFromMinimalSets wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "construct_basic --min_alg_size 3",
            "construct_with_maps --min_alg_size 3 --alg_size 7",
            "construct_with_name --name TestAlgebra --min_alg_size 3",
            "construct_with_connecting_points --name TestAlgebra --min_alg_size 3 --connect_pts 1,2",
            "construct_full --name TestAlgebra --min_alg_size 3 --alg_size 7 --connect_pts 1,2",
            "get_info --min_alg_size 3",
            "test_main",
            "test"
        };
        
        showUsage("AlgebraFromMinimalSets", 
                 "CLI wrapper for org.uacalc.alg.AlgebraFromMinimalSets operations", 
                 examples);
    }
}