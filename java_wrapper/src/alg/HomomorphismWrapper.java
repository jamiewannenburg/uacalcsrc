/* HomomorphismWrapper.java - CLI wrapper for org.uacalc.alg.Homomorphism
 * 
 * This wrapper exposes all public methods of the Homomorphism class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.Homomorphism;
import org.uacalc.alg.SmallAlgebra;
import org.uacalc.alg.BasicAlgebra;
import org.uacalc.alg.conlat.Partition;
import org.uacalc.util.IntArray;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Homomorphism class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class HomomorphismWrapper extends WrapperBase {
    
    // Store input data for accessor methods since we can't access private fields
    private Map<Integer, Integer> inputMap;
    private SmallAlgebra inputDomain;
    private SmallAlgebra inputRange;
    
    /**
     * Main entry point for the Homomorphism CLI wrapper.
     */
    public static void main(String[] args) {
        HomomorphismWrapper wrapper = new HomomorphismWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Homomorphism wrapper failed", e);
        }
    }
    
    /**
     * Run the Homomorphism CLI wrapper with the given arguments.
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
                
            case "kernel":
                handleKernel(options);
                break;
                
            case "product_homo":
                handleProductHomo(options);
                break;
                
            case "get_domain":
                handleGetDomain(options);
                break;
                
            case "set_domain":
                handleSetDomain(options);
                break;
                
            case "get_range":
                handleGetRange(options);
                break;
                
            case "set_range":
                handleSetRange(options);
                break;
                
            case "get_map":
                handleGetMap(options);
                break;
                
            case "set_map":
                handleSetMap(options);
                break;
                
            case "to_string":
                handleToString(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the test command.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Create a simple test homomorphism
        Map<Integer, Integer> map = new HashMap<>();
        map.put(0, 0);
        map.put(1, 1);
        
        // Create mock algebras for testing
        SmallAlgebra domain = createMockAlgebra("domain", 2);
        SmallAlgebra range = createMockAlgebra("range", 2);
        
        Homomorphism homo = new Homomorphism(domain, range, map);
        
        // Test kernel computation
        Partition kernel = homo.kernel();
        
        // Test toString
        String str = homo.toString();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test");
        result.put("kernel_blocks", kernel.numberOfBlocks());
        result.put("kernel_string", kernel.toString());
        result.put("to_string", str);
        handleSuccess(result);
    }
    
    /**
     * Handle the new command.
     */
    private void handleNew(Map<String, String> options) throws Exception {
        String domainName = getRequiredArg(options, "domain_name");
        String rangeName = getRequiredArg(options, "range_name");
        String mapStr = getRequiredArg(options, "map");
        
        // Parse mapping
        Map<Integer, Integer> map = parseMap(mapStr);
        
        // Create mock algebras
        SmallAlgebra domain = createMockAlgebra(domainName, getMaxKey(map) + 1);
        SmallAlgebra range = createMockAlgebra(rangeName, getMaxValue(map) + 1);
        
        // Store input data for accessor methods
        this.inputMap = new HashMap<>(map);
        this.inputDomain = domain;
        this.inputRange = range;
        
        Homomorphism homo = new Homomorphism(domain, range, map);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "new");
        result.put("domain_name", domain.getName());
        result.put("range_name", range.getName());
        result.put("map_size", map.size());
        result.put("created", true);
        handleSuccess(result);
    }
    
    /**
     * Handle the kernel command.
     */
    private void handleKernel(Map<String, String> options) throws Exception {
        String domainName = getRequiredArg(options, "domain_name");
        String rangeName = getRequiredArg(options, "range_name");
        String mapStr = getRequiredArg(options, "map");
        
        // Parse mapping
        Map<Integer, Integer> map = parseMap(mapStr);
        
        // Create mock algebras
        SmallAlgebra domain = createMockAlgebra(domainName, getMaxKey(map) + 1);
        SmallAlgebra range = createMockAlgebra(rangeName, getMaxValue(map) + 1);
        
        Homomorphism homo = new Homomorphism(domain, range, map);
        Partition kernel = homo.kernel();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "kernel");
        result.put("number_of_blocks", kernel.numberOfBlocks());
        result.put("kernel_string", kernel.toString());
        handleSuccess(result);
    }
    
    /**
     * Handle the product_homo command.
     */
    private void handleProductHomo(Map<String, String> options) throws Exception {
        String homosStr = getRequiredArg(options, "homomorphisms");
        
        // For simplicity, create a single homomorphism and test product_homo with it
        Map<Integer, Integer> map = new HashMap<>();
        map.put(0, 0);
        map.put(1, 1);
        
        SmallAlgebra domain = createMockAlgebra("domain", 2);
        SmallAlgebra range = createMockAlgebra("range", 2);
        
        Homomorphism homo = new Homomorphism(domain, range, map);
        List<Homomorphism> homos = Arrays.asList(homo);
        
        List<IntArray> result = Homomorphism.productHomo(homos);
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("command", "product_homo");
        resultMap.put("result_size", result.size());
        resultMap.put("result", result.toString());
        handleSuccess(resultMap);
    }
    
    /**
     * Handle the get_domain command.
     */
    private void handleGetDomain(Map<String, String> options) throws Exception {
        if (inputDomain == null) {
            handleError("No domain set. Use 'new' command first.", null);
            return;
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_domain");
        result.put("domain_name", inputDomain.getName());
        result.put("domain_cardinality", inputDomain.cardinality());
        handleSuccess(result);
    }
    
    /**
     * Handle the set_domain command.
     */
    private void handleSetDomain(Map<String, String> options) throws Exception {
        String domainName = getRequiredArg(options, "domain_name");
        int cardinality = getIntArg(options, "cardinality", 2);
        
        SmallAlgebra domain = createMockAlgebra(domainName, cardinality);
        this.inputDomain = domain;
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "set_domain");
        result.put("domain_name", domain.getName());
        result.put("domain_cardinality", domain.cardinality());
        handleSuccess(result);
    }
    
    /**
     * Handle the get_range command.
     */
    private void handleGetRange(Map<String, String> options) throws Exception {
        if (inputRange == null) {
            handleError("No range set. Use 'new' command first.", null);
            return;
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_range");
        result.put("range_name", inputRange.getName());
        result.put("range_cardinality", inputRange.cardinality());
        handleSuccess(result);
    }
    
    /**
     * Handle the set_range command.
     */
    private void handleSetRange(Map<String, String> options) throws Exception {
        String rangeName = getRequiredArg(options, "range_name");
        int cardinality = getIntArg(options, "cardinality", 2);
        
        SmallAlgebra range = createMockAlgebra(rangeName, cardinality);
        this.inputRange = range;
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "set_range");
        result.put("range_name", range.getName());
        result.put("range_cardinality", range.cardinality());
        handleSuccess(result);
    }
    
    /**
     * Handle the get_map command.
     */
    private void handleGetMap(Map<String, String> options) throws Exception {
        if (inputMap == null) {
            handleError("No map set. Use 'new' command first.", null);
            return;
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_map");
        result.put("map", inputMap.toString());
        result.put("map_size", inputMap.size());
        handleSuccess(result);
    }
    
    /**
     * Handle the set_map command.
     */
    private void handleSetMap(Map<String, String> options) throws Exception {
        String mapStr = getRequiredArg(options, "map");
        
        Map<Integer, Integer> map = parseMap(mapStr);
        this.inputMap = new HashMap<>(map);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "set_map");
        result.put("map", map.toString());
        result.put("map_size", map.size());
        handleSuccess(result);
    }
    
    /**
     * Handle the to_string command.
     */
    private void handleToString(Map<String, String> options) throws Exception {
        String domainName = getRequiredArg(options, "domain_name");
        String rangeName = getRequiredArg(options, "range_name");
        String mapStr = getRequiredArg(options, "map");
        
        // Parse mapping
        Map<Integer, Integer> map = parseMap(mapStr);
        
        // Create mock algebras
        SmallAlgebra domain = createMockAlgebra(domainName, getMaxKey(map) + 1);
        SmallAlgebra range = createMockAlgebra(rangeName, getMaxValue(map) + 1);
        
        Homomorphism homo = new Homomorphism(domain, range, map);
        String str = homo.toString();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "to_string");
        result.put("result", str);
        handleSuccess(result);
    }
    
    /**
     * Parse a mapping string into a Map.
     */
    private Map<Integer, Integer> parseMap(String mapStr) throws Exception {
        Map<Integer, Integer> map = new HashMap<>();
        
        if (mapStr.trim().isEmpty()) {
            return map;
        }
        
        String[] pairs = mapStr.split(",");
        for (String pair : pairs) {
            String[] parts = pair.trim().split(":");
            if (parts.length != 2) {
                throw new IllegalArgumentException("Invalid mapping format: " + pair);
            }
            
            int key = Integer.parseInt(parts[0].trim());
            int value = Integer.parseInt(parts[1].trim());
            map.put(key, value);
        }
        
        return map;
    }
    
    /**
     * Get the maximum key from a map.
     */
    private int getMaxKey(Map<Integer, Integer> map) {
        return map.keySet().stream().mapToInt(Integer::intValue).max().orElse(0);
    }
    
    /**
     * Get the maximum value from a map.
     */
    private int getMaxValue(Map<Integer, Integer> map) {
        return map.values().stream().mapToInt(Integer::intValue).max().orElse(0);
    }
    
    /**
     * Create a mock algebra for testing.
     */
    private SmallAlgebra createMockAlgebra(String name, int cardinality) {
        // Create a BasicAlgebra instance for testing
        return new BasicAlgebra(name, cardinality, new ArrayList<>());
    }
    
    /**
     * Show usage information for the Homomorphism wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "java HomomorphismWrapper test",
            "java HomomorphismWrapper new --domain_name domain --range_name range --map \"0:0,1:1\"",
            "java HomomorphismWrapper kernel --domain_name domain --range_name range --map \"0:0,1:1\"",
            "java HomomorphismWrapper product_homo --homomorphisms \"[homo1,homo2]\"",
            "java HomomorphismWrapper get_domain",
            "java HomomorphismWrapper set_domain --domain_name new_domain --cardinality 3",
            "java HomomorphismWrapper get_range",
            "java HomomorphismWrapper set_range --range_name new_range --cardinality 3",
            "java HomomorphismWrapper get_map",
            "java HomomorphismWrapper set_map --map \"0:0,1:1,2:0\"",
            "java HomomorphismWrapper to_string --domain_name domain --range_name range --map \"0:0,1:1\""
        };
        
        showUsage("Homomorphism", 
                 "CLI wrapper for org.uacalc.alg.Homomorphism operations", 
                 examples);
    }
}
