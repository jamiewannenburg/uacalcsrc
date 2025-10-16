/* BasicSetWrapper.java - CLI wrapper for org.uacalc.alg.sublat.BasicSet
 * 
 * This wrapper exposes all public methods of the BasicSet class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg.sublat;

import java.util.*;
import org.uacalc.alg.sublat.BasicSet;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the BasicSet class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class BasicSetWrapper extends WrapperBase {
    
    /**
     * Main entry point for the BasicSet CLI wrapper.
     */
    public static void main(String[] args) {
        BasicSetWrapper wrapper = new BasicSetWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("BasicSet wrapper failed", e);
        }
    }
    
    /**
     * Run the BasicSet CLI wrapper with the given arguments.
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
                
            case "normalize":
                handleNormalize(options);
                break;
                
            case "compareTo":
                handleCompareTo(options);
                break;
                
            case "leq":
                handleLeq(options);
                break;
                
            case "leqArrays":
                handleLeqArrays(options);
                break;
                
            case "contains":
                handleContains(options);
                break;
                
            case "setDifference":
                handleSetDifference(options);
                break;
                
            case "intersection":
                handleIntersection(options);
                break;
                
            case "intersectionStatic":
                handleIntersectionStatic(options);
                break;
                
            case "union":
                handleUnion(options);
                break;
                
            case "unionStatic":
                handleUnionStatic(options);
                break;
                
            case "toString":
                handleToString(options);
                break;
                
            case "empty":
                handleEmpty();
                break;
                
            case "test":
                handleTest();
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Create a new BasicSet from an array of elements.
     */
    private void handleNew(Map<String, String> options) {
        try {
            String elementsStr = getRequiredArg(options, "elements");
            int[] elements = parseIntArray(elementsStr);
            BasicSet set = new BasicSet(elements);
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "new");
            response.put("elements", arrayToList(set.toArray()));
            response.put("size", set.universeSize());
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Failed to create BasicSet", e);
        }
    }
    
    /**
     * Test the normalize method.
     */
    private void handleNormalize(Map<String, String> options) {
        try {
            String elementsStr = getRequiredArg(options, "elements");
            int[] elements = parseIntArray(elementsStr);
            BasicSet set = new BasicSet(elements);
            set.normalize();
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "normalize");
            response.put("elements", arrayToList(set.toArray()));
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Failed to normalize BasicSet", e);
        }
    }
    
    /**
     * Compare two sets using compareTo.
     */
    private void handleCompareTo(Map<String, String> options) {
        try {
            String elements1Str = getRequiredArg(options, "elements1");
            String elements2Str = getRequiredArg(options, "elements2");
            
            int[] elements1 = parseIntArray(elements1Str);
            int[] elements2 = parseIntArray(elements2Str);
            
            BasicSet set1 = new BasicSet(elements1);
            BasicSet set2 = new BasicSet(elements2);
            
            int result = set1.compareTo(set2);
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "compareTo");
            response.put("status", result);
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Failed to compare sets", e);
        }
    }
    
    /**
     * Check if set1 is a subset of set2.
     */
    private void handleLeq(Map<String, String> options) {
        try {
            String elements1Str = getRequiredArg(options, "elements1");
            String elements2Str = getRequiredArg(options, "elements2");
            
            int[] elements1 = parseIntArray(elements1Str);
            int[] elements2 = parseIntArray(elements2Str);
            
            BasicSet set1 = new BasicSet(elements1);
            BasicSet set2 = new BasicSet(elements2);
            
            boolean result = set1.leq(set2);
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "leq");
            response.put("status", result);
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Failed to check subset", e);
        }
    }
    
    /**
     * Static method to check if array u is a subset of array v.
     */
    private void handleLeqArrays(Map<String, String> options) {
        try {
            String uStr = getRequiredArg(options, "u");
            String vStr = getRequiredArg(options, "v");
            
            int[] u = parseIntArray(uStr);
            int[] v = parseIntArray(vStr);
            
            boolean result = BasicSet.leq(u, v);
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "leqArrays");
            response.put("status", result);
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Failed to check array subset", e);
        }
    }
    
    /**
     * Check if a set contains an element.
     */
    private void handleContains(Map<String, String> options) {
        try {
            String elementsStr = getRequiredArg(options, "elements");
            int element = getIntArg(options, "element", 0);
            
            int[] elements = parseIntArray(elementsStr);
            BasicSet set = new BasicSet(elements);
            
            boolean result = set.contains(element);
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "contains");
            response.put("status", result);
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Failed to check containment", e);
        }
    }
    
    /**
     * Compute set difference.
     */
    private void handleSetDifference(Map<String, String> options) {
        try {
            String elements1Str = getRequiredArg(options, "elements1");
            String elements2Str = getRequiredArg(options, "elements2");
            
            int[] elements1 = parseIntArray(elements1Str);
            int[] elements2 = parseIntArray(elements2Str);
            
            BasicSet set1 = new BasicSet(elements1);
            BasicSet set2 = new BasicSet(elements2);
            
            BasicSet diff = set1.setDifference(set2);
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "setDifference");
            response.put("elements", arrayToList(diff.toArray()));
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Failed to compute set difference", e);
        }
    }
    
    /**
     * Compute set intersection.
     */
    private void handleIntersection(Map<String, String> options) {
        try {
            String elements1Str = getRequiredArg(options, "elements1");
            String elements2Str = getRequiredArg(options, "elements2");
            
            int[] elements1 = parseIntArray(elements1Str);
            int[] elements2 = parseIntArray(elements2Str);
            
            BasicSet set1 = new BasicSet(elements1);
            BasicSet set2 = new BasicSet(elements2);
            
            BasicSet inter = set1.intersection(set2);
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "intersection");
            response.put("elements", arrayToList(inter.toArray()));
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Failed to compute intersection", e);
        }
    }
    
    /**
     * Static method to compute set intersection.
     */
    private void handleIntersectionStatic(Map<String, String> options) {
        try {
            String elements1Str = getRequiredArg(options, "elements1");
            String elements2Str = getRequiredArg(options, "elements2");
            
            int[] elements1 = parseIntArray(elements1Str);
            int[] elements2 = parseIntArray(elements2Str);
            
            BasicSet set1 = new BasicSet(elements1);
            BasicSet set2 = new BasicSet(elements2);
            
            BasicSet inter = BasicSet.intersection(set1, set2);
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "intersectionStatic");
            response.put("elements", arrayToList(inter.toArray()));
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Failed to compute static intersection", e);
        }
    }
    
    /**
     * Compute set union.
     */
    private void handleUnion(Map<String, String> options) {
        try {
            String elements1Str = getRequiredArg(options, "elements1");
            String elements2Str = getRequiredArg(options, "elements2");
            
            int[] elements1 = parseIntArray(elements1Str);
            int[] elements2 = parseIntArray(elements2Str);
            
            BasicSet set1 = new BasicSet(elements1);
            BasicSet set2 = new BasicSet(elements2);
            
            BasicSet u = set1.union(set2);
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "union");
            response.put("elements", arrayToList(u.toArray()));
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Failed to compute union", e);
        }
    }
    
    /**
     * Static method to compute set union.
     */
    private void handleUnionStatic(Map<String, String> options) {
        try {
            String elements1Str = getRequiredArg(options, "elements1");
            String elements2Str = getRequiredArg(options, "elements2");
            
            int[] elements1 = parseIntArray(elements1Str);
            int[] elements2 = parseIntArray(elements2Str);
            
            BasicSet set1 = new BasicSet(elements1);
            BasicSet set2 = new BasicSet(elements2);
            
            BasicSet u = BasicSet.union(set1, set2);
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "unionStatic");
            response.put("elements", arrayToList(u.toArray()));
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Failed to compute static union", e);
        }
    }
    
    /**
     * Test toString method.
     */
    private void handleToString(Map<String, String> options) {
        try {
            String elementsStr = getRequiredArg(options, "elements");
            int[] elements = parseIntArray(elementsStr);
            BasicSet set = new BasicSet(elements);
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "toString");
            response.put("status", set.toString());
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Failed to convert to string", e);
        }
    }
    
    /**
     * Test empty set.
     */
    private void handleEmpty() {
        try {
            BasicSet empty = BasicSet.EMPTY_SET;
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "empty");
            response.put("size", empty.universeSize());
            response.put("elements", arrayToList(empty.toArray()));
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Failed to create empty set", e);
        }
    }
    
    /**
     * Run basic functionality tests.
     */
    private void handleTest() {
        try {
            // Test 1: Create a set
            BasicSet set1 = new BasicSet(new int[]{3, 1, 2});
            boolean test1 = set1.universeSize() == 3 && set1.get(0) == 1;
            
            // Test 2: Set operations
            BasicSet set2 = new BasicSet(new int[]{2, 3, 4});
            BasicSet union = set1.union(set2);
            boolean test2 = union.universeSize() == 4;
            
            // Test 3: Contains
            boolean test3 = set1.contains(2) && !set1.contains(4);
            
            // Test 4: Subset
            BasicSet subset = new BasicSet(new int[]{1, 2});
            boolean test4 = subset.leq(set1);
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "test");
            response.put("test1", test1);
            response.put("test2", test2);
            response.put("test3", test3);
            response.put("test4", test4);
            response.put("status", test1 && test2 && test3 && test4);
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Test failed", e);
        }
    }
    
    /**
     * Parse a comma-separated string of integers into an array.
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
     * Convert an int array to a List for JSON serialization.
     */
    private List<Integer> arrayToList(int[] arr) {
        List<Integer> list = new ArrayList<>();
        for (int val : arr) {
            list.add(val);
        }
        return list;
    }
    
    /**
     * Show usage information for the BasicSet wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "new --elements 1,2,3",
            "normalize --elements 3,1,2",
            "compareTo --elements1 1,2 --elements2 1,2,3",
            "leq --elements1 1,2 --elements2 1,2,3",
            "leqArrays --u 1,2 --v 1,2,3",
            "contains --elements 1,2,3 --element 2",
            "setDifference --elements1 1,2,3 --elements2 2,3,4",
            "intersection --elements1 1,2,3 --elements2 2,3,4",
            "intersectionStatic --elements1 1,2,3 --elements2 2,3,4",
            "union --elements1 1,2 --elements2 2,3",
            "unionStatic --elements1 1,2 --elements2 2,3",
            "toString --elements 1,2,3",
            "empty",
            "test"
        };
        
        showUsage("BasicSet", 
                 "CLI wrapper for org.uacalc.alg.sublat.BasicSet operations", 
                 examples);
    }
}
