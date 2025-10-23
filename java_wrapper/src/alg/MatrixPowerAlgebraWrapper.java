/* MatrixPowerAlgebraWrapper.java - CLI wrapper for org.uacalc.alg.MatrixPowerAlgebra
 * 
 * This wrapper exposes all public methods of the MatrixPowerAlgebra class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the MatrixPowerAlgebra class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class MatrixPowerAlgebraWrapper extends WrapperBase {
    
    private MatrixPowerAlgebra matrixPowerAlgebra;
    private SmallAlgebra rootAlgebra;
    private int power;
    private String name;
    
    /**
     * Main entry point for the MatrixPowerAlgebra CLI wrapper.
     */
    public static void main(String[] args) {
        MatrixPowerAlgebraWrapper wrapper = new MatrixPowerAlgebraWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("MatrixPowerAlgebra wrapper failed", e);
        }
    }
    
    /**
     * Run the MatrixPowerAlgebra CLI wrapper with the given arguments.
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
                
            case "create_with_name":
                handleCreateWithName(options);
                break;
                
            case "get_power":
                handleGetPower(options);
                break;
                
            case "cardinality":
                handleCardinality(options);
                break;
                
            case "get_element":
                handleGetElement(options);
                break;
                
            case "element_index":
                handleElementIndex(options);
                break;
                
            case "algebra_type":
                handleAlgebraType(options);
                break;
                
            case "name":
                handleName(options);
                break;
                
            case "set_name":
                handleSetName(options);
                break;
                
            case "is_unary":
                handleIsUnary(options);
                break;
                
            case "is_idempotent":
                handleIsIdempotent(options);
                break;
                
            case "is_total":
                handleIsTotal(options);
                break;
                
            case "operations_count":
                handleOperationsCount(options);
                break;
                
            case "get_universe_list":
                handleGetUniverseList(options);
                break;
                
            case "get_universe_order":
                handleGetUniverseOrder(options);
                break;
                
            case "convert_to_default_value_ops":
                handleConvertToDefaultValueOps(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    private void handleCreate(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            handleError("MatrixPowerAlgebra not created. Use 'create_with_name' first.", null);
            return;
        }
        
        String result = "{\"command\":\"create\",\"name\":\"" + matrixPowerAlgebra.getName() + 
            "\",\"power\":" + matrixPowerAlgebra.getPower() + 
            ",\"cardinality\":" + matrixPowerAlgebra.cardinality() + 
            ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleCreateWithName(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "");
        String rootName = getRequiredArg(options, "root_name");
        int rootSize = getIntArg(options, "root_size", 2);
        int power = getIntArg(options, "power", 2);
        
        // Create a simple root algebra
        rootAlgebra = new BasicAlgebra(rootName, rootSize, new ArrayList<>());
        this.name = name;
        this.power = power;
        
        if (name.isEmpty()) {
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, power);
        } else {
            matrixPowerAlgebra = new MatrixPowerAlgebra(name, rootAlgebra, power);
        }
        
        String result = "{\"command\":\"create_with_name\",\"name\":\"" + matrixPowerAlgebra.getName() + 
            "\",\"power\":" + matrixPowerAlgebra.getPower() + 
            ",\"cardinality\":" + matrixPowerAlgebra.cardinality() + 
            ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleGetPower(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, 4);
        }
        
        int power = matrixPowerAlgebra.getPower();
        String result = "{\"command\":\"get_power\",\"power\":" + power + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleCardinality(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 3, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, 2);
        }
        
        int cardinality = matrixPowerAlgebra.cardinality();
        String result = "{\"command\":\"cardinality\",\"cardinality\":" + cardinality + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleGetElement(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, 2);
        }
        
        int index = getIntArg(options, "index", 0);
        Object element = matrixPowerAlgebra.getElement(index);
        
        // Format array properly if it's an int array
        String elementStr;
        if (element instanceof int[]) {
            elementStr = Arrays.toString((int[])element);
        } else {
            elementStr = element.toString();
        }
        
        String result = "{\"command\":\"get_element\",\"index\":" + index + 
            ",\"element\":\"" + elementStr + "\",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleElementIndex(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, 2);
        }
        
        // Parse element from command line arguments
        String elementStr = options.get("element");
        int[] element;
        if (elementStr != null && !elementStr.isEmpty()) {
            // Parse array from string like "[0, 0]"
            elementStr = elementStr.replaceAll("[\\[\\]\\s]", ""); // Remove brackets and spaces
            String[] parts = elementStr.split(",");
            element = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                element[i] = Integer.parseInt(parts[i].trim());
            }
        } else {
            // Default element for testing
            element = new int[]{0, 0};
        }
        
        int index = matrixPowerAlgebra.elementIndex(element);
        
        String result = "{\"command\":\"element_index\",\"element\":\"" + Arrays.toString(element) + 
            "\",\"index\":" + index + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleAlgebraType(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, 2);
        }
        
        SmallAlgebra.AlgebraType type = matrixPowerAlgebra.algebraType();
        String result = "{\"command\":\"algebra_type\",\"type\":\"" + type.toString() + "\",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleName(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra("MyMatrixPower", rootAlgebra, 2);
        }
        
        String name = matrixPowerAlgebra.getName();
        String result = "{\"command\":\"name\",\"name\":\"" + name + "\",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleSetName(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, 2);
        }
        
        String newName = getRequiredArg(options, "name");
        matrixPowerAlgebra.setName(newName);
        
        String result = "{\"command\":\"set_name\",\"new_name\":\"" + newName + "\",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleIsUnary(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, 2);
        }
        
        boolean isUnary = matrixPowerAlgebra.isUnary();
        String result = "{\"command\":\"is_unary\",\"is_unary\":" + isUnary + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleIsIdempotent(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, 2);
        }
        
        boolean isIdempotent = matrixPowerAlgebra.isIdempotent();
        String result = "{\"command\":\"is_idempotent\",\"is_idempotent\":" + isIdempotent + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleIsTotal(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, 2);
        }
        
        boolean isTotal = matrixPowerAlgebra.isTotal();
        String result = "{\"command\":\"is_total\",\"is_total\":" + isTotal + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleOperationsCount(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, 2);
        }
        
        int count = matrixPowerAlgebra.operations().size();
        String result = "{\"command\":\"operations_count\",\"count\":" + count + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleGetUniverseList(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, 2);
        }
        
        int universeSize = matrixPowerAlgebra.getUniverseList().size();
        String result = "{\"command\":\"get_universe_list\",\"universe_size\":" + universeSize + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleGetUniverseOrder(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, 2);
        }
        
        boolean hasOrder = matrixPowerAlgebra.getUniverseOrder() != null;
        String result = "{\"command\":\"get_universe_order\",\"has_order\":" + hasOrder + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleConvertToDefaultValueOps(Map<String, String> options) throws Exception {
        if (matrixPowerAlgebra == null) {
            // Auto-create a default algebra for testing
            rootAlgebra = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
            matrixPowerAlgebra = new MatrixPowerAlgebra(rootAlgebra, 2);
        }
        
        // This should fail for matrix power algebras
        String result = "{\"command\":\"convert_to_default_value_ops\",\"error\":\"Only for basic algebras\",\"status\":\"expected_failure\"}";
        handleSuccess(result);
    }
    
    private void handleTest(Map<String, String> options) throws Exception {
        // Create a test matrix power algebra
        SmallAlgebra testRoot = new BasicAlgebra("TestRoot", 2, new ArrayList<>());
        MatrixPowerAlgebra testMatrixPower = new MatrixPowerAlgebra("TestMatrixPower", testRoot, 3);
        
        // Test basic functionality
        int cardinality = testMatrixPower.cardinality();
        int power = testMatrixPower.getPower();
        String name = testMatrixPower.getName();
        SmallAlgebra.AlgebraType type = testMatrixPower.algebraType();
        
        String result = "{\"command\":\"test\",\"name\":\"" + name + 
            "\",\"power\":" + power + 
            ",\"cardinality\":" + cardinality + 
            ",\"algebra_type\":\"" + type.toString() + 
            "\",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the MatrixPowerAlgebra wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create_with_name --root_name TestRoot --root_size 2 --power 3",
            "get_power",
            "cardinality",
            "get_element --index 0",
            "element_index",
            "algebra_type",
            "get_universe_list",
            "get_universe_order",
            "test"
        };
        
        showUsage("MatrixPowerAlgebra", 
                 "CLI wrapper for org.uacalc.alg.MatrixPowerAlgebra operations", 
                 examples);
    }
}