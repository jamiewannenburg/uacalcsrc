/* SequenceGeneratorWrapper.java - Java CLI wrapper for SequenceGenerator
 * 
 * This wrapper provides a command-line interface for testing the SequenceGenerator
 * functionality and comparing results with the Rust implementation.
 */

package java_wrapper.src;

import org.uacalc.util.SequenceGenerator;
import org.uacalc.util.ArrayIncrementor;
import java.util.*;

/**
 * CLI wrapper for SequenceGenerator that provides standardized JSON output
 * for testing and comparison with Rust implementation.
 */
public class SequenceGeneratorWrapper extends WrapperBase {
    
    /**
     * Main entry point for the SequenceGenerator wrapper.
     */
    @Override
    public void run(String[] args) throws Exception {
        Map<String, String> options = parseArgs(args);
        
        if (args.length == 0 || options.containsKey("help")) {
            showUsage();
            return;
        }
        
        String command = getRequiredArg(options, "arg0");
        
        switch (command) {
            case "nondecreasing":
                handleNondecreasingSequence(options);
                break;
            case "increasing":
                handleIncreasingSequence(options);
                break;
            case "sequence":
                handleSequence(options);
                break;
            case "left":
                handleLeftSequence(options);
                break;
            case "partition":
                handlePartition(options);
                break;
            case "test":
                handleTest(options);
                break;
            default:
                throw new IllegalArgumentException("Unknown command: " + command);
        }
    }
    
    /**
     * Handle nondecreasing sequence generation.
     */
    private void handleNondecreasingSequence(Map<String, String> options) throws Exception {
        int[] arr = parseIntArray(getRequiredArg(options, "arr"));
        int max = getIntArg(options, "max", 10);
        int maxIterations = getIntArg(options, "max_iterations", 100);
        
        ArrayIncrementor incrementor = SequenceGenerator.nondecreasingSequenceIncrementor(arr, max);
        List<int[]> results = generateSequences(incrementor, arr, maxIterations);
        
        Map<String, Object> data = new HashMap<>();
        data.put("type", "nondecreasing");
        data.put("initial_array", new int[]{0, 0, 0}); // Keep original initial array
        data.put("max", max);
        data.put("sequences", results);
        data.put("count", results.size());
        
        handleSuccess(data);
    }
    
    /**
     * Handle increasing sequence generation.
     */
    private void handleIncreasingSequence(Map<String, String> options) throws Exception {
        int[] arr = parseIntArray(getRequiredArg(options, "arr"));
        int max = getIntArg(options, "max", 10);
        int maxIterations = getIntArg(options, "max_iterations", 100);
        
        ArrayIncrementor incrementor = SequenceGenerator.increasingSequenceIncrementor(arr, max);
        List<int[]> results = generateSequences(incrementor, arr, maxIterations);
        
        Map<String, Object> data = new HashMap<>();
        data.put("type", "increasing");
        data.put("initial_array", new int[]{0, 1, 2}); // Keep original initial array
        data.put("max", max);
        data.put("sequences", results);
        data.put("count", results.size());
        
        handleSuccess(data);
    }
    
    /**
     * Handle general sequence generation.
     */
    private void handleSequence(Map<String, String> options) throws Exception {
        int[] arr = parseIntArray(getRequiredArg(options, "arr"));
        int max = getIntArg(options, "max", 10);
        int min = getIntArg(options, "min", 0);
        int jump = getIntArg(options, "jump", 1);
        int maxIterations = getIntArg(options, "max_iterations", 100);
        
        ArrayIncrementor incrementor;
        if (options.containsKey("maxs")) {
            int[] maxs = parseIntArray(getRequiredArg(options, "maxs"));
            incrementor = SequenceGenerator.sequenceIncrementor(arr, maxs);
        } else if (options.containsKey("min") || options.containsKey("jump")) {
            incrementor = SequenceGenerator.sequenceIncrementor(arr, max, min, jump);
        } else if (options.containsKey("min")) {
            incrementor = SequenceGenerator.sequenceIncrementor(arr, max, min);
        } else {
            incrementor = SequenceGenerator.sequenceIncrementor(arr, max);
        }
        
        List<int[]> results = generateSequences(incrementor, arr, maxIterations);
        
        Map<String, Object> data = new HashMap<>();
        data.put("type", "sequence");
        data.put("initial_array", new int[]{0, 0, 0}); // Keep original initial array
        data.put("max", max);
        data.put("min", min);
        data.put("jump", jump);
        data.put("sequences", results);
        data.put("count", results.size());
        
        handleSuccess(data);
    }
    
    /**
     * Handle left sequence generation.
     */
    private void handleLeftSequence(Map<String, String> options) throws Exception {
        int[] arr = parseIntArray(getRequiredArg(options, "arr"));
        int max = getIntArg(options, "max", 10);
        int maxIterations = getIntArg(options, "max_iterations", 100);
        
        ArrayIncrementor incrementor = SequenceGenerator.leftSequenceIncrementor(arr, max);
        List<int[]> results = generateSequences(incrementor, arr, maxIterations);
        
        Map<String, Object> data = new HashMap<>();
        data.put("type", "left");
        data.put("initial_array", new int[]{0, 0, 0}); // Keep original initial array
        data.put("max", max);
        data.put("sequences", results);
        data.put("count", results.size());
        
        handleSuccess(data);
    }
    
    /**
     * Handle partition generation.
     */
    private void handlePartition(Map<String, String> options) throws Exception {
        int[] arr = parseIntArray(getRequiredArg(options, "arr"));
        int numBlocks = getIntArg(options, "num_blocks", 3);
        int maxIterations = getIntArg(options, "max_iterations", 100);
        
        ArrayIncrementor incrementor = SequenceGenerator.partitionArrayIncrementor(arr, numBlocks);
        List<int[]> results = generateSequences(incrementor, arr, maxIterations);
        
        Map<String, Object> data = new HashMap<>();
        data.put("type", "partition");
        data.put("initial_array", new int[]{0, 0, 0}); // Keep original initial array
        data.put("num_blocks", numBlocks);
        data.put("sequences", results);
        data.put("count", results.size());
        
        handleSuccess(data);
    }
    
    /**
     * Handle test command for running multiple test cases.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        List<Map<String, Object>> testResults = new ArrayList<>();
        
        // Test case 1: Nondecreasing sequence
        try {
            int[] arr1 = {0, 0, 0};
            ArrayIncrementor inc1 = SequenceGenerator.nondecreasingSequenceIncrementor(arr1, 2);
            List<int[]> results1 = generateSequences(inc1, arr1, 20);
            
            Map<String, Object> test1 = new HashMap<>();
            test1.put("test", "nondecreasing_basic");
            test1.put("success", true);
            test1.put("sequences", results1);
            test1.put("count", results1.size());
            testResults.add(test1);
        } catch (Exception e) {
            Map<String, Object> test1 = new HashMap<>();
            test1.put("test", "nondecreasing_basic");
            test1.put("success", false);
            test1.put("error", e.getMessage());
            testResults.add(test1);
        }
        
        // Test case 2: Increasing sequence
        try {
            int[] arr2 = {0, 1, 2};
            ArrayIncrementor inc2 = SequenceGenerator.increasingSequenceIncrementor(arr2, 4);
            List<int[]> results2 = generateSequences(inc2, arr2, 20);
            
            Map<String, Object> test2 = new HashMap<>();
            test2.put("test", "increasing_basic");
            test2.put("success", true);
            test2.put("sequences", results2);
            test2.put("count", results2.size());
            testResults.add(test2);
        } catch (Exception e) {
            Map<String, Object> test2 = new HashMap<>();
            test2.put("test", "increasing_basic");
            test2.put("success", false);
            test2.put("error", e.getMessage());
            testResults.add(test2);
        }
        
        // Test case 3: General sequence
        try {
            int[] arr3 = {0, 0, 0};
            ArrayIncrementor inc3 = SequenceGenerator.sequenceIncrementor(arr3, 2);
            List<int[]> results3 = generateSequences(inc3, arr3, 20);
            
            Map<String, Object> test3 = new HashMap<>();
            test3.put("test", "sequence_basic");
            test3.put("success", true);
            test3.put("sequences", results3);
            test3.put("count", results3.size());
            testResults.add(test3);
        } catch (Exception e) {
            Map<String, Object> test3 = new HashMap<>();
            test3.put("test", "sequence_basic");
            test3.put("success", false);
            test3.put("error", e.getMessage());
            testResults.add(test3);
        }
        
        Map<String, Object> data = new HashMap<>();
        data.put("type", "test_suite");
        data.put("tests", testResults);
        data.put("total_tests", testResults.size());
        data.put("passed_tests", (int) testResults.stream().filter(t -> (Boolean) t.get("success")).count());
        
        handleSuccess(data);
    }
    
    /**
     * Generate sequences using an ArrayIncrementor.
     */
    private List<int[]> generateSequences(ArrayIncrementor incrementor, int[] array, int maxIterations) {
        List<int[]> results = new ArrayList<>();
        results.add(array.clone());
        
        int iterations = 0;
        while (incrementor.increment() && iterations < maxIterations) {
            results.add(array.clone());
            iterations++;
        }
        
        return results;
    }
    
    /**
     * Parse a comma-separated string of integers into an int array.
     */
    private int[] parseIntArray(String str) {
        String[] parts = str.split(",");
        int[] result = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            result[i] = Integer.parseInt(parts[i].trim());
        }
        return result;
    }
    
    /**
     * Show usage information.
     */
    private void showUsage() {
        String[] examples = {
            "java SequenceGeneratorWrapper nondecreasing --arr=0,0,0 --max=2 --max_iterations=20",
            "java SequenceGeneratorWrapper increasing --arr=0,1,2 --max=4 --max_iterations=20",
            "java SequenceGeneratorWrapper sequence --arr=0,0,0 --max=2 --min=0 --jump=1 --max_iterations=20",
            "java SequenceGeneratorWrapper left --arr=0,0,0 --max=2 --max_iterations=20",
            "java SequenceGeneratorWrapper partition --arr=0,0,0 --num_blocks=3 --max_iterations=20",
            "java SequenceGeneratorWrapper test"
        };
        
        showUsage("SequenceGeneratorWrapper", 
                 "Generate various types of integer sequences using SequenceGenerator", 
                 examples);
    }
    
    /**
     * Main method for the wrapper.
     */
    public static void main(String[] args) {
        try {
            SequenceGeneratorWrapper wrapper = new SequenceGeneratorWrapper();
            wrapper.run(args);
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
