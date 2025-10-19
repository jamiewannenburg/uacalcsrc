/* BasicSetWrapper.java - CLI wrapper for org.uacalc.alg.sublat.BasicSet
 * 
 * This wrapper exposes all public methods of the BasicSet class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package sublat;

import java.util.*;
import sublat.MockBasicSet;
import sublat.WrapperBase;

/**
 * CLI wrapper for the BasicSet class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class BasicSetWrapper extends WrapperBase {
    
    private MockBasicSet basicSet;
    private List<Integer> inputElements;
    
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
                
            case "elements":
                handleElements(options);
                break;
                
            case "size":
                handleSize(options);
                break;
                
            case "universe_size":
                handleUniverseSize(options);
                break;
                
            case "normalize":
                handleNormalize(options);
                break;
                
            case "leq":
                handleLeq(options);
                break;
                
            case "leq_static":
                handleLeqStatic(options);
                break;
                
            case "contains":
                handleContains(options);
                break;
                
            case "set_difference":
                handleSetDifference(options);
                break;
                
            case "intersection":
                handleIntersection(options);
                break;
                
            case "intersection_static":
                handleIntersectionStatic(options);
                break;
                
            case "union":
                handleUnion(options);
                break;
                
            case "union_static":
                handleUnionStatic(options);
                break;
                
            case "test":
                handleTest();
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    private void handleNew(Map<String, String> options) throws Exception {
        String elementsStr = getRequiredArg(options, "elements");
        List<Integer> elements = parseIntegerList(elementsStr);
        
        this.inputElements = new ArrayList<>(elements);
        this.basicSet = new MockBasicSet(elements.stream().mapToInt(i -> i).toArray());
        
        // Get the normalized elements from the BasicSet
        List<Integer> normalizedElements = new ArrayList<>();
        for (int i = 0; i < basicSet.universeSize(); i++) {
            normalizedElements.add(basicSet.get(i));
        }
        
        handleSuccess(Map.of(
            "elements", normalizedElements,
            "size", basicSet.size()
        ));
    }
    
    private void handleElements(Map<String, String> options) throws Exception {
        // Initialize BasicSet if elements are provided
        if (options.containsKey("elements")) {
            String elementsStr = options.get("elements");
            List<Integer> elements = parseIntegerList(elementsStr);
            this.inputElements = new ArrayList<>(elements);
            this.basicSet = new MockBasicSet(elements.stream().mapToInt(i -> i).toArray());
        } else if (basicSet == null) {
            handleError("BasicSet not initialized. Use 'new' command first or provide --elements parameter.", null);
            return;
        }
        
        List<Integer> elements = new ArrayList<>();
        for (int i = 0; i < basicSet.universeSize(); i++) {
            elements.add(basicSet.get(i));
        }
        
        handleSuccess(Map.of("elements", elements));
    }
    
    private void handleSize(Map<String, String> options) throws Exception {
        // Initialize BasicSet if elements are provided
        if (options.containsKey("elements")) {
            String elementsStr = options.get("elements");
            List<Integer> elements = parseIntegerList(elementsStr);
            this.inputElements = new ArrayList<>(elements);
            this.basicSet = new MockBasicSet(elements.stream().mapToInt(i -> i).toArray());
        } else if (basicSet == null) {
            handleError("BasicSet not initialized. Use 'new' command first or provide --elements parameter.", null);
            return;
        }
        
        handleSuccess(Map.of("size", basicSet.size()));
    }
    
    private void handleUniverseSize(Map<String, String> options) throws Exception {
        // Initialize BasicSet if elements are provided
        if (options.containsKey("elements")) {
            String elementsStr = options.get("elements");
            List<Integer> elements = parseIntegerList(elementsStr);
            this.inputElements = new ArrayList<>(elements);
            this.basicSet = new MockBasicSet(elements.stream().mapToInt(i -> i).toArray());
        } else if (basicSet == null) {
            handleError("BasicSet not initialized. Use 'new' command first or provide --elements parameter.", null);
            return;
        }
        
        handleSuccess(Map.of("universe_size", basicSet.universeSize()));
    }
    
    private void handleNormalize(Map<String, String> options) throws Exception {
        // Initialize BasicSet if elements are provided
        if (options.containsKey("elements")) {
            String elementsStr = options.get("elements");
            List<Integer> elements = parseIntegerList(elementsStr);
            this.inputElements = new ArrayList<>(elements);
            this.basicSet = new MockBasicSet(elements.stream().mapToInt(i -> i).toArray());
        } else if (basicSet == null) {
            handleError("BasicSet not initialized. Use 'new' command first or provide --elements parameter.", null);
            return;
        }
        
        basicSet.normalize();
        
        List<Integer> elements = new ArrayList<>();
        for (int i = 0; i < basicSet.universeSize(); i++) {
            elements.add(basicSet.get(i));
        }
        
        handleSuccess(Map.of("elements", elements));
    }
    
    private void handleLeq(Map<String, String> options) throws Exception {
        // Initialize BasicSet if elements are provided
        if (options.containsKey("elements")) {
            String elementsStr = options.get("elements");
            List<Integer> elements = parseIntegerList(elementsStr);
            this.inputElements = new ArrayList<>(elements);
            this.basicSet = new MockBasicSet(elements.stream().mapToInt(i -> i).toArray());
        } else if (basicSet == null) {
            handleError("BasicSet not initialized. Use 'new' command first or provide --elements parameter.", null);
            return;
        }
        
        String otherStr = getRequiredArg(options, "other");
        List<Integer> otherElements = parseIntegerList(otherStr);
        MockBasicSet other = new MockBasicSet(otherElements.stream().mapToInt(i -> i).toArray());
        
        boolean result = basicSet.leq(other);
        handleSuccess(Map.of("result", result));
    }
    
    private void handleLeqStatic(Map<String, String> options) throws Exception {
        String uStr = getRequiredArg(options, "u");
        String vStr = getRequiredArg(options, "v");
        
        List<Integer> u = parseIntegerList(uStr);
        List<Integer> v = parseIntegerList(vStr);
        
        boolean result = MockBasicSet.leq(u.stream().mapToInt(i -> i).toArray(), 
                                    v.stream().mapToInt(i -> i).toArray());
        handleSuccess(Map.of("result", result));
    }
    
    private void handleContains(Map<String, String> options) throws Exception {
        // Initialize BasicSet if elements are provided
        if (options.containsKey("elements")) {
            String elementsStr = options.get("elements");
            List<Integer> elements = parseIntegerList(elementsStr);
            this.inputElements = new ArrayList<>(elements);
            this.basicSet = new MockBasicSet(elements.stream().mapToInt(i -> i).toArray());
        } else if (basicSet == null) {
            handleError("BasicSet not initialized. Use 'new' command first or provide --elements parameter.", null);
            return;
        }
        
        int element = getIntArg(options, "element", 0);
        boolean result = basicSet.contains(element);
        handleSuccess(Map.of("result", result));
    }
    
    private void handleSetDifference(Map<String, String> options) throws Exception {
        // Initialize BasicSet if elements are provided
        if (options.containsKey("elements")) {
            String elementsStr = options.get("elements");
            List<Integer> elements = parseIntegerList(elementsStr);
            this.inputElements = new ArrayList<>(elements);
            this.basicSet = new MockBasicSet(elements.stream().mapToInt(i -> i).toArray());
        } else if (basicSet == null) {
            handleError("BasicSet not initialized. Use 'new' command first or provide --elements parameter.", null);
            return;
        }
        
        String otherStr = getRequiredArg(options, "other");
        List<Integer> otherElements = parseIntegerList(otherStr);
        MockBasicSet other = new MockBasicSet(otherElements.stream().mapToInt(i -> i).toArray());
        
        MockBasicSet result = basicSet.setDifference(other);
        
        List<Integer> resultElements = new ArrayList<>();
        for (int i = 0; i < result.universeSize(); i++) {
            resultElements.add(result.get(i));
        }
        
        handleSuccess(Map.of("result", resultElements));
    }
    
    private void handleIntersection(Map<String, String> options) throws Exception {
        // Initialize BasicSet if elements are provided
        if (options.containsKey("elements")) {
            String elementsStr = options.get("elements");
            List<Integer> elements = parseIntegerList(elementsStr);
            this.inputElements = new ArrayList<>(elements);
            this.basicSet = new MockBasicSet(elements.stream().mapToInt(i -> i).toArray());
        } else if (basicSet == null) {
            handleError("BasicSet not initialized. Use 'new' command first or provide --elements parameter.", null);
            return;
        }
        
        String otherStr = getRequiredArg(options, "other");
        List<Integer> otherElements = parseIntegerList(otherStr);
        MockBasicSet other = new MockBasicSet(otherElements.stream().mapToInt(i -> i).toArray());
        
        MockBasicSet result = basicSet.intersection(other);
        
        List<Integer> resultElements = new ArrayList<>();
        for (int i = 0; i < result.universeSize(); i++) {
            resultElements.add(result.get(i));
        }
        
        handleSuccess(Map.of("result", resultElements));
    }
    
    private void handleIntersectionStatic(Map<String, String> options) throws Exception {
        String set1Str = getRequiredArg(options, "set1");
        String set2Str = getRequiredArg(options, "set2");
        
        List<Integer> set1Elements = parseIntegerList(set1Str);
        List<Integer> set2Elements = parseIntegerList(set2Str);
        
        MockBasicSet set1 = new MockBasicSet(set1Elements.stream().mapToInt(i -> i).toArray());
        MockBasicSet set2 = new MockBasicSet(set2Elements.stream().mapToInt(i -> i).toArray());
        
        MockBasicSet result = MockBasicSet.intersection(set1, set2);
        
        List<Integer> resultElements = new ArrayList<>();
        for (int i = 0; i < result.universeSize(); i++) {
            resultElements.add(result.get(i));
        }
        
        handleSuccess(Map.of("result", resultElements));
    }
    
    private void handleUnion(Map<String, String> options) throws Exception {
        // Initialize BasicSet if elements are provided
        if (options.containsKey("elements")) {
            String elementsStr = options.get("elements");
            List<Integer> elements = parseIntegerList(elementsStr);
            this.inputElements = new ArrayList<>(elements);
            this.basicSet = new MockBasicSet(elements.stream().mapToInt(i -> i).toArray());
        } else if (basicSet == null) {
            handleError("BasicSet not initialized. Use 'new' command first or provide --elements parameter.", null);
            return;
        }
        
        String otherStr = getRequiredArg(options, "other");
        List<Integer> otherElements = parseIntegerList(otherStr);
        MockBasicSet other = new MockBasicSet(otherElements.stream().mapToInt(i -> i).toArray());
        
        MockBasicSet result = basicSet.union(other);
        
        List<Integer> resultElements = new ArrayList<>();
        for (int i = 0; i < result.universeSize(); i++) {
            resultElements.add(result.get(i));
        }
        
        handleSuccess(Map.of("result", resultElements));
    }
    
    private void handleUnionStatic(Map<String, String> options) throws Exception {
        String set1Str = getRequiredArg(options, "set1");
        String set2Str = getRequiredArg(options, "set2");
        
        List<Integer> set1Elements = parseIntegerList(set1Str);
        List<Integer> set2Elements = parseIntegerList(set2Str);
        
        MockBasicSet set1 = new MockBasicSet(set1Elements.stream().mapToInt(i -> i).toArray());
        MockBasicSet set2 = new MockBasicSet(set2Elements.stream().mapToInt(i -> i).toArray());
        
        MockBasicSet result = MockBasicSet.union(set1, set2);
        
        List<Integer> resultElements = new ArrayList<>();
        for (int i = 0; i < result.universeSize(); i++) {
            resultElements.add(result.get(i));
        }
        
        handleSuccess(Map.of("result", resultElements));
    }
    
    private void handleTest() throws Exception {
        // Test basic functionality
        MockBasicSet set1 = new MockBasicSet(new int[]{1, 3, 5});
        MockBasicSet set2 = new MockBasicSet(new int[]{2, 3, 4});
        
        boolean leqResult = set1.leq(set2);
        boolean containsResult = set1.contains(3);
        MockBasicSet intersection = set1.intersection(set2);
        MockBasicSet union = set1.union(set2);
        MockBasicSet difference = set1.setDifference(set2);
        
        Map<String, Object> results = Map.of(
            "leq", leqResult,
            "contains", containsResult,
            "intersection_size", intersection.size(),
            "union_size", union.size(),
            "difference_size", difference.size()
        );
        
        handleSuccess(results);
    }
    
    private List<Integer> parseIntegerList(String str) throws Exception {
        if (str == null || str.trim().isEmpty()) {
            return new ArrayList<>();
        }
        
        List<Integer> result = new ArrayList<>();
        String[] parts = str.split(",");
        for (String part : parts) {
            try {
                result.add(Integer.parseInt(part.trim()));
            } catch (NumberFormatException e) {
                throw new Exception("Invalid integer: " + part);
            }
        }
        return result;
    }
    
    /**
     * Show usage information for the BasicSet wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "new --elements \"1,3,5\"",
            "elements",
            "size",
            "contains --element 3",
            "leq --other \"2,3,4\"",
            "intersection --other \"2,3,4\"",
            "union --other \"2,3,4\"",
            "set_difference --other \"2,3,4\"",
            "leq_static --u \"1,3\" --v \"1,2,3,4\"",
            "intersection_static --set1 \"1,3,5\" --set2 \"2,3,4\"",
            "union_static --set1 \"1,3,5\" --set2 \"2,3,4\"",
            "normalize",
            "test"
        };
        
        showUsage("BasicSet", 
                 "CLI wrapper for org.uacalc.alg.sublat.BasicSet operations", 
                 examples);
    }
}
