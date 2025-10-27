/* CentralityDataWrapper.java - CLI wrapper for org.uacalc.alg.conlat.CentralityData
 * 
 * This wrapper exposes all public methods of the CentralityData class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg.conlat;

import java.util.*;
import org.uacalc.alg.conlat.CentralityData;
import org.uacalc.alg.conlat.BinaryRelation;
import org.uacalc.alg.conlat.BasicBinaryRelation;
import org.uacalc.alg.conlat.Partition;
import org.uacalc.element.SubProductElement;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the CentralityData class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class CentralityDataWrapper extends WrapperBase {
    
    /**
     * Main entry point for the CentralityData CLI wrapper.
     */
    public static void main(String[] args) {
        CentralityDataWrapper wrapper = new CentralityDataWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("CentralityData wrapper failed", e);
        }
    }
    
    /**
     * Run the CentralityData CLI wrapper with the given arguments.
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
                
            case "new":
                handleNew(options);
                break;
                
            case "get_left":
                handleGetLeft(options);
                break;
                
            case "get_right":
                handleGetRight(options);
                break;
                
            case "get_delta":
                handleGetDelta(options);
                break;
                
            case "compare_to":
                handleCompareTo(options);
                break;
                
            case "to_string":
                handleToString(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle new command - create a new CentralityData.
     */
    private void handleNew(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 3);
        
        // Create simple binary relations for testing
        BasicBinaryRelation s = new BasicBinaryRelation(size);
        BasicBinaryRelation t = new BasicBinaryRelation(size);
        Partition delta = new Partition(size);
        
        // Add some pairs for testing
        if (size >= 2) {
            s.add(0, 1);
            t.add(1, 0);
        }
        
        CentralityData data = new CentralityData(s, t, delta);
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "new");
        result.put("size", size);
        result.put("status", "created");
        result.put("left_universe_size", data.getLeft().universeSize());
        result.put("right_universe_size", data.getRight().universeSize());
        result.put("delta_universe_size", data.getDelta().universeSize());
        result.put("delta_blocks", data.getDelta().numberOfBlocks());
        
        handleSuccess(result);
    }
    
    /**
     * Handle get_left command - get the left relation.
     */
    private void handleGetLeft(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 3);
        
        BasicBinaryRelation s = new BasicBinaryRelation(size);
        BasicBinaryRelation t = new BasicBinaryRelation(size);
        Partition delta = new Partition(size);
        
        if (size >= 2) {
            s.add(0, 1);
        }
        
        CentralityData data = new CentralityData(s, t, delta);
        BinaryRelation left = data.getLeft();
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "get_left");
        result.put("status", "success");
        result.put("universe_size", left.universeSize());
        result.put("is_related_0_1", left.isRelated(0, Math.min(1, size - 1)));
        
        handleSuccess(result);
    }
    
    /**
     * Handle get_right command - get the right relation.
     */
    private void handleGetRight(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 3);
        
        BasicBinaryRelation s = new BasicBinaryRelation(size);
        BasicBinaryRelation t = new BasicBinaryRelation(size);
        Partition delta = new Partition(size);
        
        if (size >= 2) {
            t.add(1, 2 % size);
        }
        
        CentralityData data = new CentralityData(s, t, delta);
        BinaryRelation right = data.getRight();
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "get_right");
        result.put("status", "success");
        result.put("universe_size", right.universeSize());
        result.put("is_related_1_2", right.isRelated(1, 2 % size));
        
        handleSuccess(result);
    }
    
    /**
     * Handle get_delta command - get the delta partition.
     */
    private void handleGetDelta(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 3);
        boolean is_one = getBoolArg(options, "is_one", false);
        
        BasicBinaryRelation s = new BasicBinaryRelation(size);
        BasicBinaryRelation t = new BasicBinaryRelation(size);
        Partition delta;
        
        if (is_one) {
            delta = new Partition(new int[]{-(size)});
            for (int i = 1; i < size; i++) {
                int[] old = delta.toArray();
                int[] newArr = new int[old.length + 1];
                System.arraycopy(old, 0, newArr, 0, old.length);
                newArr[i] = 0;
                delta = new Partition(newArr);
            }
        } else {
            delta = new Partition(size);
        }
        
        CentralityData data = new CentralityData(s, t, delta);
        Partition result_delta = data.getDelta();
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "get_delta");
        result.put("status", "success");
        result.put("universe_size", result_delta.universeSize());
        result.put("num_blocks", result_delta.numberOfBlocks());
        
        handleSuccess(result);
    }
    
    /**
     * Handle compare_to command - compare two CentralityData objects.
     */
    private void handleCompareTo(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 3);
        
        BasicBinaryRelation s1 = new BasicBinaryRelation(size);
        BasicBinaryRelation t1 = new BasicBinaryRelation(size);
        Partition delta1 = new Partition(size);
        
        BasicBinaryRelation s2 = new BasicBinaryRelation(size);
        BasicBinaryRelation t2 = new BasicBinaryRelation(size);
        
        // Create one partition (all in one block)
        int[] oneArray = new int[size];
        oneArray[0] = -size;
        for (int i = 1; i < size; i++) {
            oneArray[i] = 0;
        }
        Partition delta2 = new Partition(oneArray);
        
        CentralityData data1 = new CentralityData(s1, t1, delta1);
        CentralityData data2 = new CentralityData(s2, t2, delta2);
        
        int cmp = data1.compareTo(data2);
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "compare_to");
        result.put("status", "success");
        result.put("comparison", cmp);
        result.put("delta1_blocks", delta1.numberOfBlocks());
        result.put("delta2_blocks", delta2.numberOfBlocks());
        
        handleSuccess(result);
    }
    
    /**
     * Handle to_string command - get string representation.
     */
    private void handleToString(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 2);
        
        BasicBinaryRelation s = new BasicBinaryRelation(size);
        BasicBinaryRelation t = new BasicBinaryRelation(size);
        Partition delta = new Partition(size);
        
        if (size >= 2) {
            s.add(0, 1);
            t.add(1, 0);
        }
        
        CentralityData data = new CentralityData(s, t, delta);
        String str = data.toString();
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "to_string");
        result.put("status", "success");
        result.put("string_length", str.length());
        result.put("contains_left", str.contains("left:"));
        result.put("contains_right", str.contains("right:"));
        result.put("contains_delta", str.contains("delta:"));
        
        handleSuccess(result);
    }
    
    /**
     * Handle test command - run basic functionality tests.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        List<String> results = new ArrayList<>();
        
        // Test 1: Basic creation
        try {
            BasicBinaryRelation s = new BasicBinaryRelation(3);
            BasicBinaryRelation t = new BasicBinaryRelation(3);
            Partition delta = new Partition(3);
            CentralityData data = new CentralityData(s, t, delta);
            results.add("PASS: Basic creation");
        } catch (Exception e) {
            results.add("FAIL: Basic creation - " + e.getMessage());
        }
        
        // Test 2: Getters
        try {
            BasicBinaryRelation s = new BasicBinaryRelation(3);
            BasicBinaryRelation t = new BasicBinaryRelation(3);
            Partition delta = new Partition(3);
            CentralityData data = new CentralityData(s, t, delta);
            
            if (data.getLeft().universeSize() == 3 &&
                data.getRight().universeSize() == 3 &&
                data.getDelta().universeSize() == 3) {
                results.add("PASS: Getters");
            } else {
                results.add("FAIL: Getters - incorrect universe sizes");
            }
        } catch (Exception e) {
            results.add("FAIL: Getters - " + e.getMessage());
        }
        
        // Test 3: Comparison
        try {
            BasicBinaryRelation s1 = new BasicBinaryRelation(3);
            BasicBinaryRelation t1 = new BasicBinaryRelation(3);
            Partition delta1 = new Partition(3);
            CentralityData data1 = new CentralityData(s1, t1, delta1);
            
            BasicBinaryRelation s2 = new BasicBinaryRelation(3);
            BasicBinaryRelation t2 = new BasicBinaryRelation(3);
            int[] oneArray = new int[]{-3, 0, 0};
            Partition delta2 = new Partition(oneArray);
            CentralityData data2 = new CentralityData(s2, t2, delta2);
            
            int cmp = data1.compareTo(data2);
            results.add("PASS: Comparison (result=" + cmp + ")");
        } catch (Exception e) {
            results.add("FAIL: Comparison - " + e.getMessage());
        }
        
        // Test 4: ToString
        try {
            BasicBinaryRelation s = new BasicBinaryRelation(2);
            BasicBinaryRelation t = new BasicBinaryRelation(2);
            Partition delta = new Partition(2);
            s.add(0, 1);
            CentralityData data = new CentralityData(s, t, delta);
            String str = data.toString();
            
            if (str.contains("left:") && str.contains("right:") && str.contains("delta:")) {
                results.add("PASS: ToString");
            } else {
                results.add("FAIL: ToString - missing expected content");
            }
        } catch (Exception e) {
            results.add("FAIL: ToString - " + e.getMessage());
        }
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "test");
        result.put("status", "completed");
        result.put("results", results);
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the CentralityData wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "new --size 3                     # Create a new CentralityData",
            "get_left --size 3                # Get the left relation",
            "get_right --size 3               # Get the right relation",
            "get_delta --size 3               # Get the delta partition",
            "get_delta --size 3 --is_one true # Get the delta partition (one)",
            "compare_to --size 3              # Compare two CentralityData objects",
            "to_string --size 2               # Get string representation",
            "test                             # Run basic functionality tests"
        };
        
        showUsage("CentralityData", 
                 "CLI wrapper for org.uacalc.alg.conlat.CentralityData operations", 
                 examples);
    }
}
