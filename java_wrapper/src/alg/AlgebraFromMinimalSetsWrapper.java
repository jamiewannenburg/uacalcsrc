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
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the AlgebraFromMinimalSets class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class AlgebraFromMinimalSetsWrapper extends WrapperBase {
    
    // Store input data for accessor methods since we can't access private fields
    private SmallAlgebra inputMinAlgebra;
    private String inputName;
    private Integer inputAlgSize;
    private List<int[]> inputMaps;
    private List<Integer> inputConnectPts;
    
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
                
            case "test":
                handleTest(options);
                break;
                
            case "new":
                handleNew(options);
                break;
                
            case "new_with_size":
                handleNewWithSize(options);
                break;
                
            case "new_with_name":
                handleNewWithName(options);
                break;
                
            case "new_with_connecting_pts":
                handleNewWithConnectingPts(options);
                break;
                
            case "new_full":
                handleNewFull(options);
                break;
                
            case "cardinality":
                handleCardinality(options);
                break;
                
            case "name":
                handleName(options);
                break;
                
            case "get_element":
                handleGetElement(options);
                break;
                
            case "element_index":
                handleElementIndex(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the test command.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Create a simple test algebra
        SmallAlgebra minAlg = new BasicAlgebra(null, 3, new ArrayList<>());
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(minAlg);
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "test");
        data.put("cardinality", alg.cardinality());
        data.put("name", alg.getName());
        data.put("status", "success");
        
        handleSuccess(data);
    }
    
    /**
     * Handle the new command (default constructor).
     */
    private void handleNew(Map<String, String> options) throws Exception {
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        SmallAlgebra minAlg = new BasicAlgebra(null, minAlgSize, new ArrayList<>());
        
        inputMinAlgebra = minAlg;
        
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(minAlg);
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "new");
        data.put("min_alg_size", minAlgSize);
        data.put("cardinality", alg.cardinality());
        data.put("name", alg.getName());
        data.put("status", "success");
        
        handleSuccess(data);
    }
    
    /**
     * Handle the new_with_size command.
     */
    private void handleNewWithSize(Map<String, String> options) throws Exception {
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        int algSize = getIntArg(options, "alg_size", 7);
        String mapsStr = getOptionalArg(options, "maps", null);
        
        SmallAlgebra minAlg = new BasicAlgebra(null, minAlgSize, new ArrayList<>());
        List<int[]> maps = null;
        
        if (mapsStr != null && !mapsStr.isEmpty()) {
            maps = parseMaps(mapsStr);
        }
        
        inputMinAlgebra = minAlg;
        inputAlgSize = algSize;
        inputMaps = maps;
        
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(minAlg, algSize, maps);
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "new_with_size");
        data.put("min_alg_size", minAlgSize);
        data.put("alg_size", algSize);
        data.put("maps_count", maps != null ? maps.size() : 0);
        data.put("cardinality", alg.cardinality());
        data.put("name", alg.getName());
        data.put("status", "success");
        
        handleSuccess(data);
    }
    
    /**
     * Handle the new_with_name command.
     */
    private void handleNewWithName(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", null);
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        
        SmallAlgebra minAlg = new BasicAlgebra(null, minAlgSize, new ArrayList<>());
        
        inputName = name;
        inputMinAlgebra = minAlg;
        
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(name, minAlg);
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "new_with_name");
        data.put("name", name);
        data.put("min_alg_size", minAlgSize);
        data.put("cardinality", alg.cardinality());
        data.put("status", "success");
        
        handleSuccess(data);
    }
    
    /**
     * Handle the new_with_connecting_pts command.
     */
    private void handleNewWithConnectingPts(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", null);
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        String connectPtsStr = getOptionalArg(options, "connect_pts", null);
        
        SmallAlgebra minAlg = new BasicAlgebra(null, minAlgSize, new ArrayList<>());
        List<Integer> connectPts = null;
        
        if (connectPtsStr != null && !connectPtsStr.isEmpty()) {
            connectPts = parseIntegerList(connectPtsStr);
        }
        
        inputName = name;
        inputMinAlgebra = minAlg;
        inputConnectPts = connectPts;
        
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(name, minAlg, connectPts);
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "new_with_connecting_pts");
        data.put("name", name);
        data.put("min_alg_size", minAlgSize);
        data.put("connect_pts", connectPts);
        data.put("cardinality", alg.cardinality());
        data.put("status", "success");
        
        handleSuccess(data);
    }
    
    /**
     * Handle the new_full command.
     */
    private void handleNewFull(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", null);
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        int algSize = getIntArg(options, "alg_size", 7);
        String mapsStr = getOptionalArg(options, "maps", null);
        String connectPtsStr = getOptionalArg(options, "connect_pts", null);
        
        SmallAlgebra minAlg = new BasicAlgebra(null, minAlgSize, new ArrayList<>());
        List<int[]> maps = null;
        List<Integer> connectPts = null;
        
        if (mapsStr != null && !mapsStr.isEmpty()) {
            maps = parseMaps(mapsStr);
        }
        if (connectPtsStr != null && !connectPtsStr.isEmpty()) {
            connectPts = parseIntegerList(connectPtsStr);
        }
        
        inputName = name;
        inputMinAlgebra = minAlg;
        inputAlgSize = algSize;
        inputMaps = maps;
        inputConnectPts = connectPts;
        
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(name, minAlg, algSize, maps, connectPts);
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "new_full");
        data.put("name", name);
        data.put("min_alg_size", minAlgSize);
        data.put("alg_size", algSize);
        data.put("maps_count", maps != null ? maps.size() : 0);
        data.put("connect_pts", connectPts);
        data.put("cardinality", alg.cardinality());
        data.put("status", "success");
        
        handleSuccess(data);
    }
    
    /**
     * Handle the cardinality command.
     */
    private void handleCardinality(Map<String, String> options) throws Exception {
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        SmallAlgebra minAlg = new BasicAlgebra(null, minAlgSize, new ArrayList<>());
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(minAlg);
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "cardinality");
        data.put("cardinality", alg.cardinality());
        data.put("status", "success");
        
        handleSuccess(data);
    }
    
    /**
     * Handle the name command.
     */
    private void handleName(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", null);
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        SmallAlgebra minAlg = new BasicAlgebra(name, minAlgSize, new ArrayList<>());
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(name, minAlg);
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "name");
        data.put("name", alg.getName());
        data.put("status", "success");
        
        handleSuccess(data);
    }
    
    /**
     * Handle the get_element command.
     */
    private void handleGetElement(Map<String, String> options) throws Exception {
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        int k = getIntArg(options, "k", 0);
        SmallAlgebra minAlg = new BasicAlgebra(null, minAlgSize, new ArrayList<>());
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(minAlg);
        
        Integer element = (Integer) alg.getElement(k);
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "get_element");
        data.put("k", k);
        data.put("element", element);
        data.put("status", "success");
        
        handleSuccess(data);
    }
    
    /**
     * Handle the element_index command.
     */
    private void handleElementIndex(Map<String, String> options) throws Exception {
        int minAlgSize = getIntArg(options, "min_alg_size", 3);
        int elem = getIntArg(options, "elem", 0);
        SmallAlgebra minAlg = new BasicAlgebra(null, minAlgSize, new ArrayList<>());
        AlgebraFromMinimalSets alg = new AlgebraFromMinimalSets(minAlg);
        
        Integer index = alg.elementIndex(elem);
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "element_index");
        data.put("elem", elem);
        data.put("index", index);
        data.put("status", "success");
        
        handleSuccess(data);
    }
    
    /**
     * Parse a list of maps from a string.
     * Format: "[[0,1,2],[3,4,5],[6,7,8]]" or "0,1,2;3,4,5;6,7,8"
     */
    private List<int[]> parseMaps(String mapsStr) throws Exception {
        List<int[]> maps = new ArrayList<>();
        
        // Try to parse as semicolon-separated lists
        if (mapsStr.contains(";")) {
            String[] mapStrings = mapsStr.split(";");
            for (String mapStr : mapStrings) {
                String[] parts = mapStr.split(",");
                int[] map = new int[parts.length];
                for (int i = 0; i < parts.length; i++) {
                    map[i] = Integer.parseInt(parts[i].trim());
                }
                maps.add(map);
            }
        } else {
            // Single map
            String[] parts = mapsStr.split(",");
            int[] map = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                map[i] = Integer.parseInt(parts[i].trim());
            }
            maps.add(map);
        }
        
        return maps;
    }
    
    /**
     * Parse a list of integers from a string.
     * Format: "0,1,2" or "[0,1,2]"
     */
    private List<Integer> parseIntegerList(String listStr) throws Exception {
        List<Integer> list = new ArrayList<>();
        
        // Remove brackets if present
        String cleaned = listStr.trim();
        if (cleaned.startsWith("[") && cleaned.endsWith("]")) {
            cleaned = cleaned.substring(1, cleaned.length() - 1);
        }
        
        String[] parts = cleaned.split(",");
        for (String part : parts) {
            list.add(Integer.parseInt(part.trim()));
        }
        
        return list;
    }
    
    /**
     * Show usage information for the AlgebraFromMinimalSets wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "java AlgebraFromMinimalSetsWrapper help",
            "java AlgebraFromMinimalSetsWrapper test",
            "java AlgebraFromMinimalSetsWrapper new --min_alg_size 3",
            "java AlgebraFromMinimalSetsWrapper new_with_size --min_alg_size 3 --alg_size 7 --maps \"0,1,2;3,4,5;6,7,8\"",
            "java AlgebraFromMinimalSetsWrapper new_with_name --name \"Test\" --min_alg_size 3",
            "java AlgebraFromMinimalSetsWrapper new_with_connecting_pts --name \"Test\" --min_alg_size 3 --connect_pts \"0,2\"",
            "java AlgebraFromMinimalSetsWrapper new_full --name \"Test\" --min_alg_size 3 --alg_size 7 --maps \"0,1,2;3,4,5\" --connect_pts \"0,2\"",
            "java AlgebraFromMinimalSetsWrapper cardinality --min_alg_size 3",
            "java AlgebraFromMinimalSetsWrapper name --name \"Test\" --min_alg_size 3",
            "java AlgebraFromMinimalSetsWrapper get_element --min_alg_size 3 --k 0",
            "java AlgebraFromMinimalSetsWrapper element_index --min_alg_size 3 --elem 0"
        };
        
        showUsage("AlgebraFromMinimalSets", 
                 "CLI wrapper for org.uacalc.alg.AlgebraFromMinimalSets operations", 
                 examples);
    }
}

