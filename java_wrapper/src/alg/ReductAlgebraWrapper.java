/* ReductAlgebraWrapper.java - CLI wrapper for org.uacalc.alg.ReductAlgebra
 * 
 * This wrapper exposes all public methods of the ReductAlgebra class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.conlat.*;
import org.uacalc.terms.*;
import org.uacalc.util.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the ReductAlgebra class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class ReductAlgebraWrapper extends WrapperBase {
    
    /**
     * Main entry point for the ReductAlgebra CLI wrapper.
     */
    public static void main(String[] args) {
        ReductAlgebraWrapper wrapper = new ReductAlgebraWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("ReductAlgebra wrapper failed", e);
        }
    }
    
    /**
     * Run the ReductAlgebra CLI wrapper with the given arguments.
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
                
            case "super_algebra":
                handleSuperAlgebra(options);
                break;
                
            case "con":
                handleCon(options);
                break;
                
            case "sub":
                handleSub(options);
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
                
            case "make_operation_tables":
                handleMakeOperationTables(options);
                break;
                
            case "congruence_as_algebra":
                handleCongruenceAsAlgebra(options);
                break;
                
            case "congruence_as_algebra_with_name":
                handleCongruenceAsAlgebraWithName(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle creating a new ReductAlgebra.
     * Usage: create --super_size 4 --term_list "x,y" [--super_name "name"]
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        int superSize = getIntArg(options, "super_size", 4);
        String termListStr = getOptionalArg(options, "term_list", "");
        String superName = getOptionalArg(options, "super_name", "super");
        
        // Create a simple super algebra
        SmallAlgebra superAlg = new BasicAlgebra(superName, superSize, new ArrayList<>());
        
        // Parse term list - for simplicity, we'll create variable terms
        List<Term> termList = new ArrayList<>();
        if (!termListStr.isEmpty()) {
            String[] termNames = termListStr.split(",");
            for (String termName : termNames) {
                termList.add(new VariableImp(termName.trim()));
            }
        }
        
        ReductAlgebra reduct = new ReductAlgebra(superAlg, termList);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "create");
        result.put("name", reduct.getName());
        result.put("cardinality", reduct.cardinality());
        result.put("super_size", superSize);
        result.put("term_count", termList.size());
        
        handleSuccess(result);
    }
    
    /**
     * Handle creating a new ReductAlgebra with a name.
     * Usage: create_with_name --name "MyReduct" --super_size 4 --term_list "x,y"
     */
    private void handleCreateWithName(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int superSize = getIntArg(options, "super_size", 4);
        String termListStr = getOptionalArg(options, "term_list", "");
        String superName = getOptionalArg(options, "super_name", "super");
        
        // Create a simple super algebra
        SmallAlgebra superAlg = new BasicAlgebra(superName, superSize, new ArrayList<>());
        
        // Parse term list - for simplicity, we'll create variable terms
        List<Term> termList = new ArrayList<>();
        if (!termListStr.isEmpty()) {
            String[] termNames = termListStr.split(",");
            for (String termName : termNames) {
                termList.add(new VariableImp(termName.trim()));
            }
        }
        
        ReductAlgebra reduct = new ReductAlgebra(name, superAlg, termList);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "create_with_name");
        result.put("name", reduct.getName());
        result.put("cardinality", reduct.cardinality());
        result.put("super_size", superSize);
        result.put("term_count", termList.size());
        
        handleSuccess(result);
    }
    
    /**
     * Handle getting the super algebra.
     * Usage: super_algebra --super_size 4 --term_list ""
     */
    private void handleSuperAlgebra(Map<String, String> options) throws Exception {
        int superSize = getIntArg(options, "super_size", 4);
        String termListStr = getOptionalArg(options, "term_list", "");
        String superName = getOptionalArg(options, "super_name", "super");
        
        // Create super algebra and reduct
        SmallAlgebra superAlg = new BasicAlgebra(superName, superSize, new ArrayList<>());
        List<Term> termList = new ArrayList<>();
        if (!termListStr.isEmpty()) {
            String[] termNames = termListStr.split(",");
            for (String termName : termNames) {
                termList.add(new VariableImp(termName.trim()));
            }
        }
        ReductAlgebra reduct = new ReductAlgebra(superAlg, termList);
        
        SmallAlgebra parent = reduct.superAlgebra();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "super_algebra");
        result.put("super_name", parent.getName());
        result.put("super_cardinality", parent.cardinality());
        
        handleSuccess(result);
    }
    
    /**
     * Handle getting the congruence lattice.
     * Usage: con --super_size 4 --term_list ""
     */
    private void handleCon(Map<String, String> options) throws Exception {
        int superSize = getIntArg(options, "super_size", 4);
        String termListStr = getOptionalArg(options, "term_list", "");
        String superName = getOptionalArg(options, "super_name", "super");
        
        // Create super algebra and reduct
        SmallAlgebra superAlg = new BasicAlgebra(superName, superSize, new ArrayList<>());
        List<Term> termList = new ArrayList<>();
        if (!termListStr.isEmpty()) {
            String[] termNames = termListStr.split(",");
            for (String termName : termNames) {
                termList.add(new VariableImp(termName.trim()));
            }
        }
        ReductAlgebra reduct = new ReductAlgebra(superAlg, termList);
        
        CongruenceLattice con = reduct.con();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "con");
        result.put("alg_size", con.getAlgebra().cardinality());
        result.put("zero_blocks", con.zero().numberOfBlocks());
        result.put("one_blocks", con.one().numberOfBlocks());
        
        handleSuccess(result);
    }
    
    /**
     * Handle getting the subalgebra lattice.
     * Usage: sub --super_size 4 --term_list ""
     */
    private void handleSub(Map<String, String> options) throws Exception {
        int superSize = getIntArg(options, "super_size", 4);
        String termListStr = getOptionalArg(options, "term_list", "");
        String superName = getOptionalArg(options, "super_name", "super");
        
        // Create super algebra and reduct
        SmallAlgebra superAlg = new BasicAlgebra(superName, superSize, new ArrayList<>());
        List<Term> termList = new ArrayList<>();
        if (!termListStr.isEmpty()) {
            String[] termNames = termListStr.split(",");
            for (String termName : termNames) {
                termList.add(new VariableImp(termName.trim()));
            }
        }
        ReductAlgebra reduct = new ReductAlgebra(superAlg, termList);
        
        org.uacalc.alg.sublat.SubalgebraLattice sub = reduct.sub();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "sub");
        result.put("cardinality", sub.cardinality());
        
        handleSuccess(result);
    }
    
    /**
     * Handle element_index method.
     * Usage: element_index --super_size 4 --term_list "" --element 1
     */
    private void handleElementIndex(Map<String, String> options) throws Exception {
        int superSize = getIntArg(options, "super_size", 4);
        String termListStr = getOptionalArg(options, "term_list", "");
        int element = getIntArg(options, "element", 0);
        String superName = getOptionalArg(options, "super_name", "super");
        
        // Create super algebra and reduct
        SmallAlgebra superAlg = new BasicAlgebra(superName, superSize, new ArrayList<>());
        List<Term> termList = new ArrayList<>();
        if (!termListStr.isEmpty()) {
            String[] termNames = termListStr.split(",");
            for (String termName : termNames) {
                termList.add(new VariableImp(termName.trim()));
            }
        }
        ReductAlgebra reduct = new ReductAlgebra(superAlg, termList);
        
        int index = reduct.elementIndex(element);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "element_index");
        result.put("element", element);
        result.put("index", index);
        
        handleSuccess(result);
    }
    
    /**
     * Handle get_element method.
     * Usage: get_element --super_size 4 --term_list "" --index 1
     */
    private void handleGetElement(Map<String, String> options) throws Exception {
        int superSize = getIntArg(options, "super_size", 4);
        String termListStr = getOptionalArg(options, "term_list", "");
        int index = getIntArg(options, "index", 0);
        String superName = getOptionalArg(options, "super_name", "super");
        
        // Create super algebra and reduct
        SmallAlgebra superAlg = new BasicAlgebra(superName, superSize, new ArrayList<>());
        List<Term> termList = new ArrayList<>();
        if (!termListStr.isEmpty()) {
            String[] termNames = termListStr.split(",");
            for (String termName : termNames) {
                termList.add(new VariableImp(termName.trim()));
            }
        }
        ReductAlgebra reduct = new ReductAlgebra(superAlg, termList);
        
        Object elem = reduct.getElement(index);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_element");
        result.put("index", index);
        result.put("element", elem);
        
        handleSuccess(result);
    }
    
    /**
     * Handle cardinality method.
     * Usage: cardinality --super_size 4 --term_list ""
     */
    private void handleCardinality(Map<String, String> options) throws Exception {
        int superSize = getIntArg(options, "super_size", 4);
        String termListStr = getOptionalArg(options, "term_list", "");
        String superName = getOptionalArg(options, "super_name", "super");
        
        // Create super algebra and reduct
        SmallAlgebra superAlg = new BasicAlgebra(superName, superSize, new ArrayList<>());
        List<Term> termList = new ArrayList<>();
        if (!termListStr.isEmpty()) {
            String[] termNames = termListStr.split(",");
            for (String termName : termNames) {
                termList.add(new VariableImp(termName.trim()));
            }
        }
        ReductAlgebra reduct = new ReductAlgebra(superAlg, termList);
        
        int card = reduct.cardinality();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "cardinality");
        result.put("cardinality", card);
        
        handleSuccess(result);
    }
    
    /**
     * Handle algebra_type method.
     * Usage: algebra_type --super_size 4 --term_list ""
     */
    private void handleAlgebraType(Map<String, String> options) throws Exception {
        int superSize = getIntArg(options, "super_size", 4);
        String termListStr = getOptionalArg(options, "term_list", "");
        String superName = getOptionalArg(options, "super_name", "super");
        
        // Create super algebra and reduct
        SmallAlgebra superAlg = new BasicAlgebra(superName, superSize, new ArrayList<>());
        List<Term> termList = new ArrayList<>();
        if (!termListStr.isEmpty()) {
            String[] termNames = termListStr.split(",");
            for (String termName : termNames) {
                termList.add(new VariableImp(termName.trim()));
            }
        }
        ReductAlgebra reduct = new ReductAlgebra(superAlg, termList);
        
        SmallAlgebra.AlgebraType type = reduct.algebraType();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "algebra_type");
        result.put("type", type.toString());
        
        handleSuccess(result);
    }
    
    /**
     * Handle make_operation_tables method.
     * Usage: make_operation_tables --super_size 4 --term_list ""
     */
    private void handleMakeOperationTables(Map<String, String> options) throws Exception {
        int superSize = getIntArg(options, "super_size", 4);
        String termListStr = getOptionalArg(options, "term_list", "");
        String superName = getOptionalArg(options, "super_name", "super");
        
        // Create super algebra and reduct
        SmallAlgebra superAlg = new BasicAlgebra(superName, superSize, new ArrayList<>());
        List<Term> termList = new ArrayList<>();
        if (!termListStr.isEmpty()) {
            String[] termNames = termListStr.split(",");
            for (String termName : termNames) {
                termList.add(new VariableImp(termName.trim()));
            }
        }
        ReductAlgebra reduct = new ReductAlgebra(superAlg, termList);
        
        reduct.makeOperationTables();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "make_operation_tables");
        result.put("status", "success");
        
        handleSuccess(result);
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
        SmallAlgebra resultAlg = ReductAlgebra.congruenceAsAlgebra(superAlg, cong);
        
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
        SmallAlgebra resultAlg = ReductAlgebra.congruenceAsAlgebra(name, superAlg, cong);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "congruence_as_algebra_with_name");
        result.put("name", resultAlg.getName());
        result.put("cardinality", resultAlg.cardinality());
        result.put("algebra_type", resultAlg.algebraType().toString());
        
        handleSuccess(result);
    }
    
    /**
     * Handle running basic tests.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Create a simple super algebra
        SmallAlgebra superAlg = new BasicAlgebra("test_super", 5, new ArrayList<>());
        
        // Create reduct algebra with empty term list
        List<Term> termList = new ArrayList<>();
        ReductAlgebra reduct = new ReductAlgebra("test_reduct", superAlg, termList);
        
        // Test basic methods
        int card = reduct.cardinality();
        SmallAlgebra parent = reduct.superAlgebra();
        int idx0 = reduct.elementIndex(0);
        Object elem0 = reduct.getElement(0);
        SmallAlgebra.AlgebraType type = reduct.algebraType();
        
        // Test con() and sub()
        CongruenceLattice con = reduct.con();
        org.uacalc.alg.sublat.SubalgebraLattice sub = reduct.sub();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test");
        result.put("cardinality", card);
        result.put("super_name", parent.getName());
        result.put("element_index_0", idx0);
        result.put("get_element_0", elem0);
        result.put("algebra_type", type.toString());
        result.put("con_alg_size", con.getAlgebra().cardinality());
        result.put("sub_cardinality", sub.cardinality());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the ReductAlgebra wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create --super_size 4 --term_list \"x,y\"",
            "create_with_name --name \"MyReduct\" --super_size 4 --term_list \"x,y\"",
            "super_algebra --super_size 4 --term_list \"\"",
            "con --super_size 4 --term_list \"\"",
            "sub --super_size 4 --term_list \"\"",
            "element_index --super_size 4 --term_list \"\" --element 1",
            "get_element --super_size 4 --term_list \"\" --index 1",
            "cardinality --super_size 4 --term_list \"\"",
            "algebra_type --super_size 4 --term_list \"\"",
            "make_operation_tables --super_size 4 --term_list \"\"",
            "congruence_as_algebra --super_size 4 --partition \"0,0,1,1\"",
            "congruence_as_algebra_with_name --name \"CongAlg\" --super_size 4 --partition \"0,0,1,1\"",
            "test"
        };
        
        showUsage("ReductAlgebra", 
                 "CLI wrapper for org.uacalc.alg.ReductAlgebra operations", 
                 examples);
    }
}

