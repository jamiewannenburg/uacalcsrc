/* SubalgebraWrapper.java - CLI wrapper for org.uacalc.alg.Subalgebra
 * 
 * This wrapper exposes public methods of the Subalgebra class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.conlat.*;
import org.uacalc.util.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Subalgebra class that provides command-line access
 * to public methods for testing and validation purposes.
 */
public class SubalgebraWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Subalgebra CLI wrapper.
     */
    public static void main(String[] args) {
        SubalgebraWrapper wrapper = new SubalgebraWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Subalgebra wrapper failed", e);
        }
    }
    
    /**
     * Run the Subalgebra CLI wrapper with the given arguments.
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
                
            case "index":
                handleIndex(options);
                break;
                
            case "restrict_partition":
                handleRestrictPartition(options);
                break;
                
            case "super_algebra":
                handleSuperAlgebra(options);
                break;
                
            case "get_subuniverse_array":
                handleGetSubuniverseArray(options);
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
                
            case "congruence_as_algebra":
                handleCongruenceAsAlgebra(options);
                break;
                
            case "congruence_as_algebra_with_name":
                handleCongruenceAsAlgebraWithName(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle creating a new Subalgebra.
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "");
        int superSize = getIntArg(options, "super_size", 4);
        String universeStr = getOptionalArg(options, "universe", "0,1");
        
        // Create a simple super algebra with the given size
        SmallAlgebra superAlg = new BasicAlgebra(name.isEmpty() ? "super" : name + "_super", 
                                                   superSize, new ArrayList<>());
        
        // Parse universe as comma-separated integers
        String[] elements = universeStr.split(",");
        int[] univ = new int[elements.length];
        for (int i = 0; i < elements.length; i++) {
            univ[i] = Integer.parseInt(elements[i].trim());
        }
        
        Subalgebra subalg = new Subalgebra(name, superAlg, univ);
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"create\",");
        result.append("\"name\":\"").append(name).append("\",");
        result.append("\"super_size\":").append(superSize).append(",");
        result.append("\"universe\":\"").append(universeStr).append("\",");
        result.append("\"cardinality\":").append(subalg.cardinality()).append(",");
        result.append("\"status\":\"created\"}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle finding the index of an element.
     */
    private void handleIndex(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "");
        int superSize = getIntArg(options, "super_size", 4);
        String universeStr = getOptionalArg(options, "universe", "0,1,2");
        int k = getIntArg(options, "k", 0);
        
        // Create subalgebra
        SmallAlgebra superAlg = new BasicAlgebra(name.isEmpty() ? "super" : name + "_super", 
                                                   superSize, new ArrayList<>());
        String[] elements = universeStr.split(",");
        int[] univ = new int[elements.length];
        for (int i = 0; i < elements.length; i++) {
            univ[i] = Integer.parseInt(elements[i].trim());
        }
        
        Subalgebra subalg = new Subalgebra(name, superAlg, univ);
        
        int index = subalg.index(k);
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"index\",");
        result.append("\"k\":").append(k).append(",");
        result.append("\"status\":").append(index).append("}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle restricting a partition to the subalgebra.
     */
    private void handleRestrictPartition(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "");
        int superSize = getIntArg(options, "super_size", 4);
        String universeStr = getOptionalArg(options, "universe", "0,1,2");
        String partitionStr = getOptionalArg(options, "partition", "-1,-1,-1,-1");
        
        // Create subalgebra
        SmallAlgebra superAlg = new BasicAlgebra(name.isEmpty() ? "super" : name + "_super", 
                                                   superSize, new ArrayList<>());
        String[] elements = universeStr.split(",");
        int[] univ = new int[elements.length];
        for (int i = 0; i < elements.length; i++) {
            univ[i] = Integer.parseInt(elements[i].trim());
        }
        
        Subalgebra subalg = new Subalgebra(name, superAlg, univ);
        
        // Create partition on super algebra
        String[] parElements = partitionStr.split(",");
        int[] parArr = new int[parElements.length];
        for (int i = 0; i < parElements.length; i++) {
            parArr[i] = Integer.parseInt(parElements[i].trim());
        }
        Partition par = new BasicPartition(parArr);
        
        // Restrict partition
        BasicPartition restricted = subalg.restrictPartition(par);
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"restrict_partition\",");
        result.append("\"size\":").append(restricted.universeSize()).append(",");
        result.append("\"blocks\":").append(restricted.numberOfBlocks()).append(",");
        result.append("\"status\":\"success\"}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle getting super algebra name.
     */
    private void handleSuperAlgebra(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "");
        int superSize = getIntArg(options, "super_size", 4);
        String universeStr = getOptionalArg(options, "universe", "0,1");
        
        // Create subalgebra
        SmallAlgebra superAlg = new BasicAlgebra(name.isEmpty() ? "super" : name + "_super", 
                                                   superSize, new ArrayList<>());
        String[] elements = universeStr.split(",");
        int[] univ = new int[elements.length];
        for (int i = 0; i < elements.length; i++) {
            univ[i] = Integer.parseInt(elements[i].trim());
        }
        
        Subalgebra subalg = new Subalgebra(name, superAlg, univ);
        
        SmallAlgebra parent = subalg.superAlgebra();
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"super_algebra\",");
        result.append("\"status\":\"").append(parent.getName()).append("\"}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle getting subuniverse array.
     */
    private void handleGetSubuniverseArray(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "");
        int superSize = getIntArg(options, "super_size", 4);
        String universeStr = getOptionalArg(options, "universe", "0,1,2");
        
        // Create subalgebra
        SmallAlgebra superAlg = new BasicAlgebra(name.isEmpty() ? "super" : name + "_super", 
                                                   superSize, new ArrayList<>());
        String[] elements = universeStr.split(",");
        int[] univ = new int[elements.length];
        for (int i = 0; i < elements.length; i++) {
            univ[i] = Integer.parseInt(elements[i].trim());
        }
        
        Subalgebra subalg = new Subalgebra(name, superAlg, univ);
        
        int[] subuniv = subalg.getSubuniverseArray();
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"get_subuniverse_array\",");
        result.append("\"status\":[");
        for (int i = 0; i < subuniv.length; i++) {
            if (i > 0) result.append(",");
            result.append(subuniv[i]);
        }
        result.append("]}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle element_index method.
     */
    private void handleElementIndex(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "");
        int superSize = getIntArg(options, "super_size", 4);
        String universeStr = getOptionalArg(options, "universe", "0,1,2");
        int elem = getIntArg(options, "element", 0);
        
        // Create subalgebra
        SmallAlgebra superAlg = new BasicAlgebra(name.isEmpty() ? "super" : name + "_super", 
                                                   superSize, new ArrayList<>());
        String[] elements = universeStr.split(",");
        int[] univ = new int[elements.length];
        for (int i = 0; i < elements.length; i++) {
            univ[i] = Integer.parseInt(elements[i].trim());
        }
        
        Subalgebra subalg = new Subalgebra(name, superAlg, univ);
        
        int index = subalg.elementIndex(elem);
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"element_index\",");
        result.append("\"element\":").append(elem).append(",");
        result.append("\"status\":").append(index).append("}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle get_element method.
     */
    private void handleGetElement(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "");
        int superSize = getIntArg(options, "super_size", 4);
        String universeStr = getOptionalArg(options, "universe", "0,1,2");
        int index = getIntArg(options, "index", 0);
        
        // Create subalgebra
        SmallAlgebra superAlg = new BasicAlgebra(name.isEmpty() ? "super" : name + "_super", 
                                                   superSize, new ArrayList<>());
        String[] elements = universeStr.split(",");
        int[] univ = new int[elements.length];
        for (int i = 0; i < elements.length; i++) {
            univ[i] = Integer.parseInt(elements[i].trim());
        }
        
        Subalgebra subalg = new Subalgebra(name, superAlg, univ);
        
        Object elem = subalg.getElement(index);
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"get_element\",");
        result.append("\"index\":").append(index).append(",");
        result.append("\"status\":").append(elem).append("}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle cardinality method.
     */
    private void handleCardinality(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "");
        int superSize = getIntArg(options, "super_size", 4);
        String universeStr = getOptionalArg(options, "universe", "0,1,2");
        
        // Create subalgebra
        SmallAlgebra superAlg = new BasicAlgebra(name.isEmpty() ? "super" : name + "_super", 
                                                   superSize, new ArrayList<>());
        String[] elements = universeStr.split(",");
        int[] univ = new int[elements.length];
        for (int i = 0; i < elements.length; i++) {
            univ[i] = Integer.parseInt(elements[i].trim());
        }
        
        Subalgebra subalg = new Subalgebra(name, superAlg, univ);
        
        int card = subalg.cardinality();
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"cardinality\",");
        result.append("\"status\":").append(card).append("}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle algebra_type method.
     */
    private void handleAlgebraType(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "");
        int superSize = getIntArg(options, "super_size", 4);
        String universeStr = getOptionalArg(options, "universe", "0,1");
        
        // Create subalgebra
        SmallAlgebra superAlg = new BasicAlgebra(name.isEmpty() ? "super" : name + "_super", 
                                                   superSize, new ArrayList<>());
        String[] elements = universeStr.split(",");
        int[] univ = new int[elements.length];
        for (int i = 0; i < elements.length; i++) {
            univ[i] = Integer.parseInt(elements[i].trim());
        }
        
        Subalgebra subalg = new Subalgebra(name, superAlg, univ);
        
        SmallAlgebra.AlgebraType type = subalg.algebraType();
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"algebra_type\",");
        result.append("\"status\":\"").append(type).append("\"}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle running basic tests.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Create a simple super algebra
        SmallAlgebra superAlg = new BasicAlgebra("test_super", 5, new ArrayList<>());
        
        // Create subalgebra with universe {0, 2, 4}
        int[] univ = new int[] {0, 2, 4};
        Subalgebra subalg = new Subalgebra("test_sub", superAlg, univ);
        
        // Test basic methods
        int card = subalg.cardinality();
        int idx0 = subalg.index(0);
        int idx2 = subalg.index(2);
        int idx1 = subalg.index(1);  // Should be negative (not in subalgebra)
        SmallAlgebra parent = subalg.superAlgebra();
        int[] subuniv = subalg.getSubuniverseArray();
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"test\",");
        result.append("\"cardinality\":").append(card).append(",");
        result.append("\"index_0\":").append(idx0).append(",");
        result.append("\"index_2\":").append(idx2).append(",");
        result.append("\"index_1\":").append(idx1).append(",");
        result.append("\"super_name\":\"").append(parent.getName()).append("\",");
        result.append("\"subuniv_length\":").append(subuniv.length).append(",");
        result.append("\"status\":\"success\"}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle congruence_as_algebra static method.
     * Usage: congruence_as_algebra --super_size 4 --partition "0,0,1,1"
     */
    private void handleCongruenceAsAlgebra(Map<String, String> options) throws Exception {
        int superSize = getIntArg(options, "super_size", 4);
        String partitionStr = getRequiredArg(options, "partition");
        
        // Create super algebra
        SmallAlgebra superAlg = new BasicAlgebra("super", superSize, new ArrayList<>());
        
        // Parse partition
        String[] parElements = partitionStr.split(",");
        int[] parArr = new int[parElements.length];
        for (int i = 0; i < parElements.length; i++) {
            parArr[i] = Integer.parseInt(parElements[i].trim());
        }
        Partition cong = new BasicPartition(parArr);
        
        // Call static method
        SmallAlgebra resultAlg = Subalgebra.congruenceAsAlgebra(superAlg, cong);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "congruence_as_algebra");
        result.put("name", resultAlg.getName());
        result.put("cardinality", resultAlg.cardinality());
        result.put("algebra_type", resultAlg.algebraType().toString());
        
        handleSuccess(result);
    }
    
    /**
     * Handle congruence_as_algebra_with_name static method.
     * Usage: congruence_as_algebra_with_name --name "CongAlg" --super_size 4 --partition "0,0,1,1"
     */
    private void handleCongruenceAsAlgebraWithName(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int superSize = getIntArg(options, "super_size", 4);
        String partitionStr = getRequiredArg(options, "partition");
        
        // Create super algebra
        SmallAlgebra superAlg = new BasicAlgebra("super", superSize, new ArrayList<>());
        
        // Parse partition
        String[] parElements = partitionStr.split(",");
        int[] parArr = new int[parElements.length];
        for (int i = 0; i < parElements.length; i++) {
            parArr[i] = Integer.parseInt(parElements[i].trim());
        }
        Partition cong = new BasicPartition(parArr);
        
        // Call static method
        SmallAlgebra resultAlg = Subalgebra.congruenceAsAlgebra(name, superAlg, cong);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "congruence_as_algebra_with_name");
        result.put("name", resultAlg.getName());
        result.put("cardinality", resultAlg.cardinality());
        result.put("algebra_type", resultAlg.algebraType().toString());
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the Subalgebra wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create --name sub --super_size 4 --universe 0,1,2",
            "index --super_size 4 --universe 0,1,2 --k 1",
            "restrict_partition --super_size 4 --universe 0,1,2 --partition -2,0,-1,2",
            "super_algebra --super_size 4 --universe 0,1",
            "get_subuniverse_array --super_size 4 --universe 0,1,2",
            "element_index --super_size 4 --universe 0,1,2 --element 1",
            "get_element --super_size 4 --universe 0,1,2 --index 1",
            "cardinality --super_size 4 --universe 0,1,2",
            "algebra_type --super_size 4 --universe 0,1",
            "congruence_as_algebra --super_size 4 --partition \"0,0,1,1\"",
            "congruence_as_algebra_with_name --name \"CongAlg\" --super_size 4 --partition \"0,0,1,1\"",
            "test"
        };
        
        showUsage("Subalgebra", 
                 "CLI wrapper for org.uacalc.alg.Subalgebra operations", 
                 examples);
    }
}

