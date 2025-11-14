/* SubProductAlgebraWrapper.java - CLI wrapper for org.uacalc.alg.SubProductAlgebra
 * 
 * This wrapper exposes public methods of the SubProductAlgebra class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.op.*;
import org.uacalc.util.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the SubProductAlgebra class that provides command-line access
 * to public methods for testing and validation purposes.
 */
public class SubProductAlgebraWrapper extends WrapperBase {
    
    /**
     * Main entry point for the SubProductAlgebra CLI wrapper.
     */
    public static void main(String[] args) {
        SubProductAlgebraWrapper wrapper = new SubProductAlgebraWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("SubProductAlgebra wrapper failed", e);
        }
    }
    
    /**
     * Run the SubProductAlgebra CLI wrapper with the given arguments.
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
                
            case "create":
                handleCreate(options);
                break;
                
            case "cardinality":
                handleCardinality(options);
                break;
                
            case "element_index":
                handleElementIndex(options);
                break;
                
            case "get_element":
                handleGetElement(options);
                break;
                
            case "generators":
                handleGenerators(options);
                break;
                
            case "get_universe_list":
                handleGetUniverseList(options);
                break;
                
            case "get_universe_order":
                handleGetUniverseOrder(options);
                break;
                
            case "transpose":
                handleTranspose(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Create a SubProductAlgebra from a BigProductAlgebra and generators.
     * Usage: create --name "name" --factors 2 --factor_sizes 2,3 --generators "0,0|1,0|0,1" [--find_terms false]
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "TestSubProduct");
        int factors = getIntArg(options, "factors", 2);
        String factorSizesStr = getRequiredArg(options, "factor_sizes");
        String generatorsStr = getRequiredArg(options, "generators");
        boolean findTerms = getBoolArg(options, "find_terms", false);
        
        // Parse factor sizes
        String[] sizeStrs = factorSizesStr.split(",");
        if (sizeStrs.length != factors) {
            throw new IllegalArgumentException("Number of factor sizes must match number of factors");
        }
        
        // Create factor algebras with at least one operation (constant)
        List<SmallAlgebra> factorAlgs = new ArrayList<>();
        for (int i = 0; i < factors; i++) {
            int size = Integer.parseInt(sizeStrs[i].trim());
            // Create a constant operation
            List<Operation> ops = new ArrayList<>();
            OperationSymbol constSym = new OperationSymbol("c" + i, 0, false);
            int[] constTable = new int[1];
            constTable[0] = 0; // Constant value
            Operation constOp = Operations.makeIntOperation(constSym, size, constTable);
            ops.add(constOp);
            SmallAlgebra alg = new BasicAlgebra("Factor" + i, size, ops);
            factorAlgs.add(alg);
        }
        
        // Create BigProductAlgebra with powers array so rootFactors() is set
        // Use powers of 1 for each factor to make it behave like a direct product
        int[] powers = new int[factors];
        for (int i = 0; i < factors; i++) {
            powers[i] = 1;
        }
        BigProductAlgebra product = new BigProductAlgebra(factorAlgs, powers);
        
        // Parse generators
        String[] genStrs = generatorsStr.split("\\|");
        List<IntArray> gens = new ArrayList<>();
        for (String genStr : genStrs) {
            String[] parts = genStr.split(",");
            int[] arr = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                arr[i] = Integer.parseInt(parts[i].trim());
            }
            gens.add(new IntArray(arr));
        }
        
        // Create SubProductAlgebra
        SubProductAlgebra subProd = new SubProductAlgebra(name, product, gens, findTerms);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "create");
        result.put("name", subProd.getName());
        result.put("cardinality", subProd.cardinality());
        result.put("number_of_generators", gens.size());
        result.put("status", "created");
        
        handleSuccess(result);
    }
    
    /**
     * Get the cardinality of a SubProductAlgebra.
     */
    private void handleCardinality(Map<String, String> options) throws Exception {
        SubProductAlgebra subProd = createSubProductAlgebra(options);
        
        int card = subProd.cardinality();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "cardinality");
        result.put("cardinality", card);
        
        handleSuccess(result);
    }
    
    /**
     * Get the index of an element.
     * Usage: element_index --element "0,1" [other create options]
     */
    private void handleElementIndex(Map<String, String> options) throws Exception {
        SubProductAlgebra subProd = createSubProductAlgebra(options);
        String elementStr = getRequiredArg(options, "element");
        
        // Parse element as IntArray
        String[] parts = elementStr.split(",");
        int[] elemArray = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            elemArray[i] = Integer.parseInt(parts[i].trim());
        }
        IntArray elem = new IntArray(elemArray);
        
        int index = subProd.elementIndex(elem);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "element_index");
        List<Integer> elemList = new ArrayList<>();
        for (int val : elemArray) {
            elemList.add(val);
        }
        result.put("element", elemList);
        result.put("index", index);
        
        handleSuccess(result);
    }
    
    /**
     * Get an element by index.
     * Usage: get_element --index 0 [other create options]
     */
    private void handleGetElement(Map<String, String> options) throws Exception {
        SubProductAlgebra subProd = createSubProductAlgebra(options);
        int index = getIntArg(options, "index", 0);
        
        Object element = subProd.getElement(index);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_element");
        result.put("index", index);
        
        if (element instanceof IntArray) {
            IntArray ia = (IntArray) element;
            List<Integer> elemList = new ArrayList<>();
            for (int val : ia.getArray()) {
                elemList.add(val);
            }
            result.put("element", elemList);
        } else {
            result.put("element", element.toString());
        }
        
        handleSuccess(result);
    }
    
    /**
     * Get the generators.
     */
    private void handleGenerators(Map<String, String> options) throws Exception {
        SubProductAlgebra subProd = createSubProductAlgebra(options);
        
        List<IntArray> gens = subProd.generators();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "generators");
        result.put("number_of_generators", gens.size());
        
        List<List<Integer>> genLists = new ArrayList<>();
        for (IntArray gen : gens) {
            List<Integer> genList = new ArrayList<>();
            for (int val : gen.getArray()) {
                genList.add(val);
            }
            genLists.add(genList);
        }
        result.put("generators", genLists);
        
        handleSuccess(result);
    }
    
    /**
     * Get the universe list.
     */
    private void handleGetUniverseList(Map<String, String> options) throws Exception {
        SubProductAlgebra subProd = createSubProductAlgebra(options);
        
        List<IntArray> univ = subProd.getUniverseList();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_universe_list");
        result.put("universe_size", univ.size());
        
        List<List<Integer>> univLists = new ArrayList<>();
        for (IntArray elem : univ) {
            List<Integer> elemList = new ArrayList<>();
            for (int val : elem.getArray()) {
                elemList.add(val);
            }
            univLists.add(elemList);
        }
        result.put("universe", univLists);
        
        handleSuccess(result);
    }
    
    /**
     * Get the universe order (element to index mapping).
     */
    private void handleGetUniverseOrder(Map<String, String> options) throws Exception {
        SubProductAlgebra subProd = createSubProductAlgebra(options);
        
        Map<IntArray, Integer> order = subProd.getUniverseOrder();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_universe_order");
        result.put("map_size", order.size());
        
        // Serialize the map - convert IntArray keys to List<Integer> for JSON serialization
        Map<List<Integer>, Integer> serializedMap = new HashMap<>();
        for (Map.Entry<IntArray, Integer> entry : order.entrySet()) {
            List<Integer> keyList = new ArrayList<>();
            for (int val : entry.getKey().getArray()) {
                keyList.add(val);
            }
            serializedMap.put(keyList, entry.getValue());
        }
        result.put("order", serializedMap);
        
        handleSuccess(result);
    }
    
    /**
     * Transpose a list of IntArrays.
     * Usage: transpose --arrays "0,1|2,3|4,5"
     */
    private void handleTranspose(Map<String, String> options) throws Exception {
        String arraysStr = getRequiredArg(options, "arrays");
        
        // Parse arrays
        String[] arrayStrs = arraysStr.split("\\|");
        List<IntArray> arrays = new ArrayList<>();
        for (String arrayStr : arrayStrs) {
            String[] parts = arrayStr.split(",");
            int[] arr = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                arr[i] = Integer.parseInt(parts[i].trim());
            }
            arrays.add(new IntArray(arr));
        }
        
        List<IntArray> transposed = SubProductAlgebra.transpose(arrays);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "transpose");
        result.put("input_size", arrays.size());
        result.put("output_size", transposed.size());
        
        List<List<Integer>> transposedLists = new ArrayList<>();
        for (IntArray arr : transposed) {
            List<Integer> arrList = new ArrayList<>();
            for (int val : arr.getArray()) {
                arrList.add(val);
            }
            transposedLists.add(arrList);
        }
        result.put("transposed", transposedLists);
        
        handleSuccess(result);
    }
    
    /**
     * Run basic tests.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Create a simple test case with operations
        List<SmallAlgebra> factorAlgs = new ArrayList<>();
        // Create A1 with constant operation
        List<Operation> ops1 = new ArrayList<>();
        OperationSymbol constSym1 = new OperationSymbol("c1", 0, false);
        int[] constTable1 = new int[1];
        constTable1[0] = 0;
        ops1.add(Operations.makeIntOperation(constSym1, 2, constTable1));
        factorAlgs.add(new BasicAlgebra("A1", 2, ops1));
        
        // Create A2 with constant operation
        List<Operation> ops2 = new ArrayList<>();
        OperationSymbol constSym2 = new OperationSymbol("c2", 0, false);
        int[] constTable2 = new int[1];
        constTable2[0] = 0;
        ops2.add(Operations.makeIntOperation(constSym2, 3, constTable2));
        factorAlgs.add(new BasicAlgebra("A2", 3, ops2));
        
        // Create BigProductAlgebra with powers array so rootFactors() is set
        int[] powers = new int[] {1, 1};
        BigProductAlgebra product = new BigProductAlgebra(factorAlgs, powers);
        
        List<IntArray> gens = new ArrayList<>();
        gens.add(new IntArray(new int[] {0, 0}));
        gens.add(new IntArray(new int[] {1, 0}));
        gens.add(new IntArray(new int[] {0, 1}));
        
        SubProductAlgebra subProd = new SubProductAlgebra("TestSubProd", product, gens, false);
        
        // Test basic methods
        int card = subProd.cardinality();
        List<IntArray> univ = subProd.getUniverseList();
        Map<IntArray, Integer> order = subProd.getUniverseOrder();
        List<IntArray> generators = subProd.generators();
        
        // Test element access
        IntArray firstElem = (IntArray) subProd.getElement(0);
        int firstIndex = subProd.elementIndex(firstElem);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test");
        result.put("name", subProd.getName());
        result.put("cardinality", card);
        result.put("universe_size", univ.size());
        result.put("order_map_size", order.size());
        result.put("generators_count", generators.size());
        result.put("first_element_index", firstIndex);
        result.put("test_passed", true);
        
        handleSuccess(result);
    }
    
    /**
     * Helper method to create a SubProductAlgebra from options.
     */
    private SubProductAlgebra createSubProductAlgebra(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "TestSubProduct");
        int factors = getIntArg(options, "factors", 2);
        String factorSizesStr = getOptionalArg(options, "factor_sizes", "2,3");
        String generatorsStr = getOptionalArg(options, "generators", "0,0|1,0|0,1");
        boolean findTerms = getBoolArg(options, "find_terms", false);
        
        // Parse factor sizes
        String[] sizeStrs = factorSizesStr.split(",");
        if (sizeStrs.length != factors) {
            throw new IllegalArgumentException("Number of factor sizes must match number of factors");
        }
        
        // Create factor algebras with at least one operation (constant)
        List<SmallAlgebra> factorAlgs = new ArrayList<>();
        for (int i = 0; i < factors; i++) {
            int size = Integer.parseInt(sizeStrs[i].trim());
            // Create a constant operation
            List<Operation> ops = new ArrayList<>();
            OperationSymbol constSym = new OperationSymbol("c" + i, 0, false);
            int[] constTable = new int[1];
            constTable[0] = 0; // Constant value
            Operation constOp = Operations.makeIntOperation(constSym, size, constTable);
            ops.add(constOp);
            SmallAlgebra alg = new BasicAlgebra("Factor" + i, size, ops);
            factorAlgs.add(alg);
        }
        
        // Create BigProductAlgebra with powers array so rootFactors() is set
        // Use powers of 1 for each factor to make it behave like a direct product
        int[] powers = new int[factors];
        for (int i = 0; i < factors; i++) {
            powers[i] = 1;
        }
        BigProductAlgebra product = new BigProductAlgebra(factorAlgs, powers);
        
        // Parse generators
        String[] genStrs = generatorsStr.split("\\|");
        List<IntArray> gens = new ArrayList<>();
        for (String genStr : genStrs) {
            String[] parts = genStr.split(",");
            int[] arr = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                arr[i] = Integer.parseInt(parts[i].trim());
            }
            gens.add(new IntArray(arr));
        }
        
        return new SubProductAlgebra(name, product, gens, findTerms);
    }
    
    /**
     * Serialize an int array as a JSON array string.
     */
    private String serializeIntArray(int[] arr) {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        for (int i = 0; i < arr.length; i++) {
            if (i > 0) sb.append(", ");
            sb.append(arr[i]);
        }
        sb.append("]");
        return sb.toString();
    }
    
    /**
     * Show usage information for the SubProductAlgebra wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create --name \"SubProd\" --factors 2 --factor_sizes 2,3 --generators \"0,0|1,0|0,1\"",
            "cardinality --factors 2 --factor_sizes 2,3 --generators \"0,0|1,0|0,1\"",
            "element_index --element \"0,0\" --factors 2 --factor_sizes 2,3 --generators \"0,0|1,0|0,1\"",
            "get_element --index 0 --factors 2 --factor_sizes 2,3 --generators \"0,0|1,0|0,1\"",
            "generators --factors 2 --factor_sizes 2,3 --generators \"0,0|1,0|0,1\"",
            "get_universe_list --factors 2 --factor_sizes 2,3 --generators \"0,0|1,0|0,1\"",
            "get_universe_order --factors 2 --factor_sizes 2,3 --generators \"0,0|1,0|0,1\"",
            "transpose --arrays \"0,1|2,3|4,5\"",
            "test"
        };
        
        showUsage("SubProductAlgebra", 
                 "CLI wrapper for org.uacalc.alg.SubProductAlgebra operations", 
                 examples);
    }
}

