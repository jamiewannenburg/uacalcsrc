/* BasicAlgebraWrapper.java - CLI wrapper for org.uacalc.alg.BasicAlgebra
 * 
 * This wrapper exposes public methods of the BasicAlgebra class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 * 
 * Note: This is a PARTIAL implementation that excludes con() and sub() methods
 * (congruence and subalgebra lattices) as per the implementation requirements.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.SmallAlgebra.AlgebraType;
import org.uacalc.alg.op.Operation;
import org.uacalc.alg.op.Operations;
import org.uacalc.alg.op.OperationSymbol;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the BasicAlgebra class that provides command-line access
 * to public methods for testing and validation purposes (excluding con/sub lattices).
 */
public class BasicAlgebraWrapper extends WrapperBase {
    
    /**
     * Main entry point for the BasicAlgebra CLI wrapper.
     */
    public static void main(String[] args) {
        BasicAlgebraWrapper wrapper = new BasicAlgebraWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("BasicAlgebra wrapper failed", e);
        }
    }
    
    /**
     * Run the BasicAlgebra CLI wrapper with the given arguments.
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
                
            case "create-int":
                handleCreateInt(options);
                break;
                
            case "get-universe-list":
                handleGetUniverseList(options);
                break;
                
            case "get-universe-order":
                handleGetUniverseOrder(options);
                break;
                
            case "int-universe":
                handleIntUniverse(options);
                break;
                
            case "element-index":
                handleElementIndex(options);
                break;
                
            case "get-element":
                handleGetElement(options);
                break;
                
            case "algebra-type":
                handleAlgebraType(options);
                break;
                
            case "cardinality":
                handleCardinality(options);
                break;
                
            case "name":
                handleName(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Create a BasicAlgebra with integer universe.
     */
    private void handleCreateInt(Map<String, String> options) {
        try {
            String name = getRequiredArg(options, "name");
            int size = getIntArg(options, "size", 0);
            
            // Create a simple algebra with integer universe
            List<Operation> operations = new ArrayList<>();
            BasicAlgebra alg = new BasicAlgebra(name, size, operations);
            
            Map<String, Object> result = new HashMap<>();
            result.put("name", alg.getName());
            result.put("cardinality", alg.cardinality());
            result.put("int_universe", alg.intUniverse());
            result.put("algebra_type", alg.algebraType().toString());
            
            handleSuccess(result);
        } catch (Exception e) {
            handleError("Failed to create integer universe BasicAlgebra", e);
        }
    }
    
    /**
     * Get the universe list from a BasicAlgebra.
     */
    private void handleGetUniverseList(Map<String, String> options) {
        try {
            String name = getOptionalArg(options, "name", "test");
            int size = getIntArg(options, "size", 0);
            
            List<Operation> operations = new ArrayList<>();
            BasicAlgebra alg = new BasicAlgebra(name, size, operations);
            
            List universeList = alg.getUniverseList();
            
            Map<String, Object> result = new HashMap<>();
            result.put("universe_list", universeList);
            result.put("size", universeList != null ? universeList.size() : 0);
            
            handleSuccess(result);
        } catch (Exception e) {
            handleError("Failed to get universe list", e);
        }
    }
    
    /**
     * Get the universe order map from a BasicAlgebra.
     */
    private void handleGetUniverseOrder(Map<String, String> options) {
        try {
            String name = getOptionalArg(options, "name", "test");
            int size = getIntArg(options, "size", 0);
            
            List<Operation> operations = new ArrayList<>();
            BasicAlgebra alg = new BasicAlgebra(name, size, operations);
            
            Map universeOrder = alg.getUniverseOrder();
            
            Map<String, Object> result = new HashMap<>();
            result.put("has_universe_order", universeOrder != null);
            result.put("size", universeOrder != null ? universeOrder.size() : 0);
            
            handleSuccess(result);
        } catch (Exception e) {
            handleError("Failed to get universe order", e);
        }
    }
    
    /**
     * Check if algebra uses integer universe.
     */
    private void handleIntUniverse(Map<String, String> options) {
        try {
            String name = getOptionalArg(options, "name", "test");
            int size = getIntArg(options, "size", 0);
            
            List<Operation> operations = new ArrayList<>();
            BasicAlgebra alg = new BasicAlgebra(name, size, operations);
            
            boolean intUniverse = alg.intUniverse();
            
            Map<String, Object> result = new HashMap<>();
            result.put("int_universe", intUniverse);
            
            handleSuccess(result);
        } catch (Exception e) {
            handleError("Failed to check int universe", e);
        }
    }
    
    /**
     * Get the index of an element.
     */
    private void handleElementIndex(Map<String, String> options) {
        try {
            String name = getOptionalArg(options, "name", "test");
            int size = getIntArg(options, "size", 0);
            int element = getIntArg(options, "element", 0);
            
            List<Operation> operations = new ArrayList<>();
            BasicAlgebra alg = new BasicAlgebra(name, size, operations);
            
            int index = alg.elementIndex(element);
            
            Map<String, Object> result = new HashMap<>();
            result.put("element", element);
            result.put("index", index);
            
            handleSuccess(result);
        } catch (Exception e) {
            handleError("Failed to get element index", e);
        }
    }
    
    /**
     * Get an element by index.
     */
    private void handleGetElement(Map<String, String> options) {
        try {
            String name = getOptionalArg(options, "name", "test");
            int size = getIntArg(options, "size", 0);
            int index = getIntArg(options, "index", 0);
            
            List<Operation> operations = new ArrayList<>();
            BasicAlgebra alg = new BasicAlgebra(name, size, operations);
            
            Object element = alg.getElement(index);
            
            Map<String, Object> result = new HashMap<>();
            result.put("index", index);
            result.put("element", element);
            
            handleSuccess(result);
        } catch (Exception e) {
            handleError("Failed to get element", e);
        }
    }
    
    /**
     * Get the algebra type.
     */
    private void handleAlgebraType(Map<String, String> options) {
        try {
            String name = getOptionalArg(options, "name", "test");
            int size = getIntArg(options, "size", 0);
            
            List<Operation> operations = new ArrayList<>();
            BasicAlgebra alg = new BasicAlgebra(name, size, operations);
            
            AlgebraType type = alg.algebraType();
            
            Map<String, Object> result = new HashMap<>();
            result.put("algebra_type", type.toString());
            
            handleSuccess(result);
        } catch (Exception e) {
            handleError("Failed to get algebra type", e);
        }
    }
    
    /**
     * Get the cardinality.
     */
    private void handleCardinality(Map<String, String> options) {
        try {
            String name = getOptionalArg(options, "name", "test");
            int size = getIntArg(options, "size", 0);
            
            List<Operation> operations = new ArrayList<>();
            BasicAlgebra alg = new BasicAlgebra(name, size, operations);
            
            int cardinality = alg.cardinality();
            
            Map<String, Object> result = new HashMap<>();
            result.put("cardinality", cardinality);
            
            handleSuccess(result);
        } catch (Exception e) {
            handleError("Failed to get cardinality", e);
        }
    }
    
    /**
     * Get the name.
     */
    private void handleName(Map<String, String> options) {
        try {
            String name = getRequiredArg(options, "name");
            int size = getIntArg(options, "size", 0);
            
            List<Operation> operations = new ArrayList<>();
            BasicAlgebra alg = new BasicAlgebra(name, size, operations);
            
            String algName = alg.getName();
            
            Map<String, Object> result = new HashMap<>();
            result.put("name", algName);
            
            handleSuccess(result);
        } catch (Exception e) {
            handleError("Failed to get name", e);
        }
    }
    
    /**
     * Run basic functionality tests.
     */
    private void handleTest(Map<String, String> options) {
        try {
            Map<String, Object> testResults = new HashMap<>();
            
            // Test 1: Create integer universe algebra
            List<Operation> operations = new ArrayList<>();
            BasicAlgebra alg = new BasicAlgebra("test", 5, operations);
            testResults.put("test1_name", alg.getName());
            testResults.put("test1_cardinality", alg.cardinality());
            testResults.put("test1_int_universe", alg.intUniverse());
            testResults.put("test1_algebra_type", alg.algebraType().toString());
            
            // Test 2: Element operations
            testResults.put("test2_element_0", alg.getElement(0));
            testResults.put("test2_element_2", alg.getElement(2));
            testResults.put("test2_index_of_0", alg.elementIndex(0));
            testResults.put("test2_index_of_3", alg.elementIndex(3));
            
            // Test 3: Universe operations
            List universeList = alg.getUniverseList();
            Map universeOrder = alg.getUniverseOrder();
            testResults.put("test3_universe_list_null", universeList == null);
            testResults.put("test3_universe_order_null", universeOrder == null);
            
            handleSuccess(testResults);
        } catch (Exception e) {
            handleError("Test failed", e);
        }
    }
    
    /**
     * Show usage information for the BasicAlgebra wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create-int --name MyAlgebra --size 5",
            "get-universe-list --name test --size 3",
            "get-universe-order --name test --size 4",
            "int-universe --name test --size 5",
            "element-index --name test --size 5 --element 2",
            "get-element --name test --size 5 --index 3",
            "algebra-type --name test --size 5",
            "cardinality --name test --size 5",
            "name --name MyAlgebra --size 5",
            "test"
        };
        
        showUsage("BasicAlgebra (Partial Implementation)", 
                 "CLI wrapper for org.uacalc.alg.BasicAlgebra operations (excluding con/sub lattices)", 
                 examples);
    }
}

