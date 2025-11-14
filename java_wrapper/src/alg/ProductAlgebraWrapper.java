/* ProductAlgebraWrapper.java - CLI wrapper for org.uacalc.alg.ProductAlgebra
 * 
 * This wrapper exposes all public methods of the ProductAlgebra class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.ProductAlgebra;
import org.uacalc.io.AlgebraIO;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the ProductAlgebra class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class ProductAlgebraWrapper extends WrapperBase {
    
    /**
     * Main entry point for the ProductAlgebra CLI wrapper.
     */
    public static void main(String[] args) {
        ProductAlgebraWrapper wrapper = new ProductAlgebraWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("ProductAlgebra wrapper failed", e);
        }
    }
    
    /**
     * Run the ProductAlgebra CLI wrapper with the given arguments.
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
                
            case "calc_card":
                handleCalcCard(options);
                break;
                
            case "factors":
                handleFactors(options);
                break;
                
            case "projection":
                handleProjection(options);
                break;
                
            case "element_index":
                handleElementIndex(options);
                break;
                
            case "get_element":
                handleGetElement(options);
                break;
                
            case "cardinality":
                handleCardinality(options);
                break;
                
            case "algebra_type":
                handleAlgebraType(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Create a product algebra from a list of algebra files.
     * Usage: create --files file1.ua,file2.ua [--name "name"]
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        String name = getOptionalArg(options, "name", "");
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        ProductAlgebra product = new ProductAlgebra(name, algebras);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "create");
        result.put("name", product.getName());
        result.put("cardinality", product.cardinality());
        result.put("number_of_factors", algebras.size());
        
        handleSuccess(result);
    }
    
    /**
     * Calculate cardinality of a product.
     * Usage: calc_card --sizes 2,3,4
     */
    private void handleCalcCard(Map<String, String> options) throws Exception {
        String sizesStr = getRequiredArg(options, "sizes");
        
        String[] sizeStrs = sizesStr.split(",");
        int[] sizes = new int[sizeStrs.length];
        
        for (int i = 0; i < sizeStrs.length; i++) {
            sizes[i] = Integer.parseInt(sizeStrs[i].trim());
        }
        
        int card = ProductAlgebra.calcCard(sizes);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "calc_card");
        result.put("sizes", serializeSizes(sizes));
        result.put("cardinality", card);
        
        handleSuccess(result);
    }
    
    /**
     * Get the factors of a product algebra.
     * Usage: factors --files file1.ua,file2.ua
     */
    private void handleFactors(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        ProductAlgebra product = new ProductAlgebra("", algebras);
        List<SmallAlgebra> factors = product.factors();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "factors");
        result.put("number_of_factors", factors.size());
        
        List<String> factorNames = new ArrayList<>();
        for (SmallAlgebra alg : factors) {
            factorNames.add(alg.getName());
        }
        result.put("factor_names", factorNames);
        
        handleSuccess(result);
    }
    
    /**
     * Get a projection of the product.
     * Usage: projection --files file1.ua,file2.ua --index 0
     */
    private void handleProjection(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        int index = getIntArg(options, "index", 0);
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        ProductAlgebra product = new ProductAlgebra("", algebras);
        SmallAlgebra projection = product.projection(index);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "projection");
        result.put("index", index);
        result.put("projection_name", projection.getName());
        result.put("projection_cardinality", projection.cardinality());
        
        handleSuccess(result);
    }
    
    /**
     * Get the index of an element (IntArray).
     * Usage: element_index --files file1.ua,file2.ua --element 0,1
     */
    private void handleElementIndex(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        String elementStr = getRequiredArg(options, "element");
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        ProductAlgebra product = new ProductAlgebra("", algebras);
        
        // Parse element as IntArray
        String[] elemParts = elementStr.split(",");
        int[] elemArray = new int[elemParts.length];
        for (int i = 0; i < elemParts.length; i++) {
            elemArray[i] = Integer.parseInt(elemParts[i].trim());
        }
        
        org.uacalc.util.IntArray ia = new org.uacalc.util.IntArray(elemArray);
        int index = product.elementIndex(ia);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "element_index");
        result.put("element", serializeIntArray(elemArray));
        result.put("index", index);
        
        handleSuccess(result);
    }
    
    /**
     * Get an element by index.
     * Usage: get_element --files file1.ua,file2.ua --index 5
     */
    private void handleGetElement(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        int index = getIntArg(options, "index", 0);
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        ProductAlgebra product = new ProductAlgebra("", algebras);
        Object element = product.getElement(index);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_element");
        result.put("index", index);
        
        if (element instanceof org.uacalc.util.IntArray) {
            org.uacalc.util.IntArray ia = (org.uacalc.util.IntArray) element;
            result.put("element", serializeIntArray(ia.getArray()));
        } else {
            result.put("element", element.toString());
        }
        
        handleSuccess(result);
    }
    
    /**
     * Get the cardinality of a product.
     * Usage: cardinality --files file1.ua,file2.ua
     */
    private void handleCardinality(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        ProductAlgebra product = new ProductAlgebra("", algebras);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "cardinality");
        result.put("cardinality", product.cardinality());
        
        handleSuccess(result);
    }
    
    /**
     * Get the algebra type.
     * Usage: algebra_type --files file1.ua,file2.ua
     */
    private void handleAlgebraType(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        ProductAlgebra product = new ProductAlgebra("", algebras);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "algebra_type");
        result.put("algebra_type", product.algebraType().toString());
        
        handleSuccess(result);
    }
    
    /**
     * Run basic tests.
     * Usage: test --files file1.ua,file2.ua
     */
    private void handleTest(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        ProductAlgebra product = new ProductAlgebra("TestProduct", algebras);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test");
        result.put("name", product.getName());
        result.put("cardinality", product.cardinality());
        result.put("number_of_factors", product.factors().size());
        result.put("algebra_type", product.algebraType().toString());
        result.put("test_passed", true);
        
        handleSuccess(result);
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
     * Serialize sizes array as a JSON array string.
     */
    private String serializeSizes(int[] sizes) {
        return serializeIntArray(sizes);
    }
    
    /**
     * Show usage information for the ProductAlgebra wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create --files file1.ua,file2.ua --name \"Product\"",
            "calc_card --sizes 2,3,4",
            "factors --files file1.ua,file2.ua",
            "projection --files file1.ua,file2.ua --index 0",
            "element_index --files file1.ua,file2.ua --element 0,1",
            "get_element --files file1.ua,file2.ua --index 5",
            "cardinality --files file1.ua,file2.ua",
            "algebra_type --files file1.ua,file2.ua",
            "test --files file1.ua,file2.ua"
        };
        
        showUsage("ProductAlgebra", 
                 "CLI wrapper for org.uacalc.alg.ProductAlgebra operations", 
                 examples);
    }
}

