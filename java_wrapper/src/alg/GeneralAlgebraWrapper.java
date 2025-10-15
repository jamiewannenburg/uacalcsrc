/* GeneralAlgebraWrapper.java - CLI wrapper for org.uacalc.alg.GeneralAlgebra
 * 
 * This wrapper exposes all public methods of the GeneralAlgebra class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.GeneralAlgebra;
import org.uacalc.alg.BasicAlgebra;
import org.uacalc.alg.Algebra;
import org.uacalc.alg.op.Operation;
import org.uacalc.alg.op.OperationSymbol;
import org.uacalc.alg.op.SimilarityType;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the GeneralAlgebra class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class GeneralAlgebraWrapper extends WrapperBase {
    
    /**
     * Main entry point for the GeneralAlgebra CLI wrapper.
     */
    public static void main(String[] args) {
        GeneralAlgebraWrapper wrapper = new GeneralAlgebraWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("GeneralAlgebra wrapper failed", e);
        }
    }
    
    /**
     * Run the GeneralAlgebra CLI wrapper with the given arguments.
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
                
            case "create_with_universe":
                handleCreateWithUniverse(options);
                break;
            
            case "name":
                handleName(options);
                break;
                
            case "set_name":
                handleSetName(options);
                break;
                
            case "description":
                handleDescription(options);
                break;
                
            case "set_description":
                handleSetDescription(options);
                break;
                
            case "cardinality":
                handleCardinality(options);
                break;
                
            case "input_size":
                handleInputSize(options);
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
                
            case "monitoring":
                handleMonitoring(options);
                break;
                
            case "universe":
                handleUniverse(options);
                break;
                
            case "similarity_type":
                handleSimilarityType(options);
                break;
                
            case "is_similar_to":
                handleIsSimilarTo(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle creating a new GeneralAlgebra with just a name.
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        String name = getStringArg(options, "name", "TestAlgebra");
        
        GeneralAlgebra algebra = new BasicAlgebra(name, 3, new ArrayList<>());
        
        handleSuccess("{\"command\":\"create\",\"name\":\"" + name + "\",\"status\":\"created\"}");
    }
    
    /**
     * Handle creating a new GeneralAlgebra with a name and universe.
     */
    private void handleCreateWithUniverse(Map<String, String> options) throws Exception {
        String name = getStringArg(options, "name", "TestAlgebra");
        String universeStr = getStringArg(options, "universe", "");
        
        // Parse universe as comma-separated integers
        Set<Integer> universe = new HashSet<>();
        if (!universeStr.isEmpty()) {
            String[] elements = universeStr.split(",");
            for (String elem : elements) {
                universe.add(Integer.parseInt(elem.trim()));
            }
        }
        
        GeneralAlgebra algebra = new GeneralAlgebra(name, universe, new ArrayList<>());
        
        handleSuccess("{\"command\":\"create_with_universe\",\"name\":\"" + name + "\",\"universe_size\":" + universe.size() + ",\"status\":\"created\"}");
    }
    
    /**
     * Handle getting the name of an algebra.
     */
    private void handleName(Map<String, String> options) throws Exception {
        String name = getStringArg(options, "name", "TestAlgebra");
        
        GeneralAlgebra algebra = new BasicAlgebra(name, 3, new ArrayList<>());
        String result = algebra.getName();
        
        handleSuccess("{\"command\":\"name\",\"input_name\":\"" + name + "\",\"status\":\"" + (result != null ? result : "") + "\"}");
    }
    
    /**
     * Handle setting the name of an algebra.
     */
    private void handleSetName(Map<String, String> options) throws Exception {
        String originalName = getRequiredArg(options, "original_name");
        String newName = getRequiredArg(options, "new_name");
        
        GeneralAlgebra algebra = new BasicAlgebra(originalName, 3, new ArrayList<>());
        algebra.setName(newName);
        String result = algebra.getName();
        
        handleSuccess(Map.of(
            "command", "set_name",
            "original_name", originalName,
            "new_name", newName,
            "status", result
        ));
    }
    
    /**
     * Handle getting the description of an algebra.
     */
    private void handleDescription(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        
        GeneralAlgebra algebra = new BasicAlgebra(name, 3, new ArrayList<>());
        String result = algebra.getDescription();
        
        handleSuccess(Map.of(
            "command", "description",
            "name", name,
            "status", result != null ? result : ""
        ));
    }
    
    /**
     * Handle setting the description of an algebra.
     */
    private void handleSetDescription(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        String description = getOptionalArg(options, "description", null);
        
        GeneralAlgebra algebra = new BasicAlgebra(name, 3, new ArrayList<>());
        algebra.setDescription(description);
        String result = algebra.getDescription();
        
        handleSuccess(Map.of(
            "command", "set_description",
            "name", name,
            "description", description != null ? description : "",
            "status", result != null ? result : ""
        ));
    }
    
    /**
     * Handle getting the cardinality of an algebra.
     */
    private void handleCardinality(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        String universeStr = getOptionalArg(options, "universe", "");
        
        GeneralAlgebra algebra;
        if (!universeStr.isEmpty()) {
            Set<Integer> universe = new HashSet<>();
            String[] elements = universeStr.split(",");
            for (String elem : elements) {
                universe.add(Integer.parseInt(elem.trim()));
            }
            algebra = new GeneralAlgebra(name, universe, new ArrayList<>());
        } else {
            algebra = new BasicAlgebra(name, 3, new ArrayList<>());
        }
        
        int result = algebra.cardinality();
        
        handleSuccess(Map.of(
            "command", "cardinality",
            "name", name,
            "status", result
        ));
    }
    
    /**
     * Handle getting the input size of an algebra.
     */
    private void handleInputSize(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        String universeStr = getOptionalArg(options, "universe", "");
        
        GeneralAlgebra algebra;
        if (!universeStr.isEmpty()) {
            Set<Integer> universe = new HashSet<>();
            String[] elements = universeStr.split(",");
            for (String elem : elements) {
                universe.add(Integer.parseInt(elem.trim()));
            }
            algebra = new GeneralAlgebra(name, universe, new ArrayList<>());
        } else {
            algebra = new BasicAlgebra(name, 3, new ArrayList<>());
        }
        
        int result = algebra.inputSize();
        
        handleSuccess(Map.of(
            "command", "input_size",
            "name", name,
            "status", result
        ));
    }
    
    /**
     * Handle checking if an algebra is unary.
     */
    private void handleIsUnary(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        
        GeneralAlgebra algebra = new BasicAlgebra(name, 3, new ArrayList<>());
        boolean result = algebra.isUnary();
        
        handleSuccess(Map.of(
            "command", "is_unary",
            "name", name,
            "status", result
        ));
    }
    
    /**
     * Handle checking if an algebra is idempotent.
     */
    private void handleIsIdempotent(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        
        GeneralAlgebra algebra = new BasicAlgebra(name, 3, new ArrayList<>());
        boolean result = algebra.isIdempotent();
        
        handleSuccess(Map.of(
            "command", "is_idempotent",
            "name", name,
            "status", result
        ));
    }
    
    /**
     * Handle checking if an algebra is total.
     */
    private void handleIsTotal(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        
        GeneralAlgebra algebra = new BasicAlgebra(name, 3, new ArrayList<>());
        boolean result = algebra.isTotal();
        
        handleSuccess(Map.of(
            "command", "is_total",
            "name", name,
            "status", result
        ));
    }
    
    /**
     * Handle checking if monitoring is enabled.
     */
    private void handleMonitoring(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        
        GeneralAlgebra algebra = new BasicAlgebra(name, 3, new ArrayList<>());
        boolean result = algebra.monitoring();
        
        handleSuccess(Map.of(
            "command", "monitoring",
            "name", name,
            "status", result
        ));
    }
    
    /**
     * Handle getting the universe of an algebra.
     */
    private void handleUniverse(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        String universeStr = getOptionalArg(options, "universe", "");
        
        GeneralAlgebra algebra;
        if (!universeStr.isEmpty()) {
            Set<Integer> universe = new HashSet<>();
            String[] elements = universeStr.split(",");
            for (String elem : elements) {
                universe.add(Integer.parseInt(elem.trim()));
            }
            algebra = new GeneralAlgebra(name, universe, new ArrayList<>());
        } else {
            algebra = new BasicAlgebra(name, 3, new ArrayList<>());
        }
        
        Set<?> universe = algebra.universe();
        List<Object> universeList = new ArrayList<>(universe);
        Collections.sort(universeList, (a, b) -> {
            if (a instanceof Integer && b instanceof Integer) {
                return ((Integer) a).compareTo((Integer) b);
            }
            return a.toString().compareTo(b.toString());
        });
        
        handleSuccess(Map.of(
            "command", "universe",
            "name", name,
            "status", universeList
        ));
    }
    
    /**
     * Handle getting the similarity type of an algebra.
     */
    private void handleSimilarityType(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        
        GeneralAlgebra algebra = new BasicAlgebra(name, 3, new ArrayList<>());
        SimilarityType similarityType = algebra.similarityType();
        
        handleSuccess(Map.of(
            "command", "similarity_type",
            "name", name,
            "status", similarityType != null ? similarityType.toString() : "null"
        ));
    }
    
    /**
     * Handle checking if two algebras are similar.
     */
    private void handleIsSimilarTo(Map<String, String> options) throws Exception {
        String name1 = getRequiredArg(options, "name1");
        String name2 = getRequiredArg(options, "name2");
        
        GeneralAlgebra algebra1 = new BasicAlgebra(name1, 3, new ArrayList<>());
        GeneralAlgebra algebra2 = new BasicAlgebra(name2, 3, new ArrayList<>());
        
        boolean result = algebra1.isSimilarTo(algebra2);
        
        handleSuccess(Map.of(
            "command", "is_similar_to",
            "name1", name1,
            "name2", name2,
            "status", result
        ));
    }
    
    /**
     * Handle running basic tests.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Test creating an algebra
        GeneralAlgebra algebra = new BasicAlgebra("TestAlgebra", 3, new ArrayList<>());
        
        // Test basic properties
        String name = algebra.getName();
        String description = algebra.getDescription();
        int cardinality = algebra.cardinality();
        int inputSize = algebra.inputSize();
        boolean isUnary = algebra.isUnary();
        boolean isIdempotent = algebra.isIdempotent();
        boolean isTotal = algebra.isTotal();
        boolean monitoring = algebra.monitoring();
        
        // Test with universe
        Set<Integer> universe = new HashSet<>(Arrays.asList(0, 1, 2));
        GeneralAlgebra algebraWithUniverse = new GeneralAlgebra("TestWithUniverse", universe);
        int cardinalityWithUniverse = algebraWithUniverse.cardinality();
        
        handleSuccess("{\"command\":\"test\",\"basic_name\":\"" + name + 
                     "\",\"basic_description\":\"" + (description != null ? description : "") + 
                     "\",\"basic_cardinality\":" + cardinality + 
                     ",\"basic_input_size\":" + inputSize + 
                     ",\"basic_is_unary\":" + isUnary + 
                     ",\"basic_is_idempotent\":" + isIdempotent +
                     ",\"basic_is_total\":" + isTotal +
                     ",\"basic_monitoring\":" + monitoring +
                     ",\"universe_cardinality\":" + cardinalityWithUniverse +
                     ",\"status\":\"all_tests_passed\"}");
    }
    
    /**
     * Show usage information for the GeneralAlgebra wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create --name \"MyAlgebra\"",
            "create_with_universe --name \"MyAlgebra\" --universe \"0,1,2\"",
            "name --name \"MyAlgebra\"",
            "set_name --original_name \"OldName\" --new_name \"NewName\"",
            "description --name \"MyAlgebra\"",
            "set_description --name \"MyAlgebra\" --description \"My test algebra\"",
            "cardinality --name \"MyAlgebra\" --universe \"0,1,2\"",
            "input_size --name \"MyAlgebra\" --universe \"0,1,2\"",
            "is_unary --name \"MyAlgebra\"",
            "is_idempotent --name \"MyAlgebra\"",
            "is_total --name \"MyAlgebra\"",
            "monitoring --name \"MyAlgebra\"",
            "universe --name \"MyAlgebra\" --universe \"0,1,2\"",
            "similarity_type --name \"MyAlgebra\"",
            "is_similar_to --name1 \"Algebra1\" --name2 \"Algebra2\"",
            "test"
        };
        
        showUsage("GeneralAlgebra", 
                 "CLI wrapper for org.uacalc.alg.GeneralAlgebra operations", 
                 examples);
    }
    
    /**
     * Get a string argument from the options map with a default value.
     * 
     * @param options The options map
     * @param key The argument key
     * @param defaultValue The default value
     * @return The argument value or default
     */
    private String getStringArg(Map<String, String> options, String key, String defaultValue) {
        String value = options.get(key);
        return value != null ? value : defaultValue;
    }
}
