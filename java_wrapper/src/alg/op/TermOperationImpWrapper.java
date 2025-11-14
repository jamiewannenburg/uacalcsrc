/* TermOperationImpWrapper.java - CLI wrapper for org.uacalc.alg.op.TermOperationImp
 * 
 * This wrapper exposes all public methods of the TermOperationImp class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg.op;

import java.util.*;
import org.uacalc.alg.op.TermOperationImp;
import org.uacalc.alg.SmallAlgebra;
import org.uacalc.terms.*;
import org.uacalc.io.AlgebraReader;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the TermOperationImp class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class TermOperationImpWrapper extends WrapperBase {
    
    /**
     * Main entry point for the TermOperationImp CLI wrapper.
     */
    public static void main(String[] args) {
        TermOperationImpWrapper wrapper = new TermOperationImpWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("TermOperationImp wrapper failed", e);
        }
    }
    
    /**
     * Run the TermOperationImp CLI wrapper with the given arguments.
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
                
            case "create_simple":
                handleCreateSimple(options);
                break;
                
            case "get_term":
                handleGetTerm(options);
                break;
                
            case "get_ordered_variables":
                handleGetOrderedVariables(options);
                break;
                
            case "int_value_at":
                handleIntValueAt(options);
                break;
                
            case "arity":
                handleArity(options);
                break;
                
            case "to_string":
                handleToString(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            case "create_from_term":
                handleCreateFromTerm(options);
                break;
                
            case "get_table":
                handleGetTable(options);
                break;
                
            case "value_at":
                handleValueAt(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Create a simple term operation for testing.
     * Args: --algebra_path <path> --var <name>
     */
    private void handleCreateSimple(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra_path");
        String varName = getRequiredArg(options, "var");
        
        // Load the algebra
        AlgebraReader reader = new AlgebraReader(algebraPath);
        SmallAlgebra alg = (SmallAlgebra) reader.readAlgebraFile();
        
        // Create a simple variable term
        Variable var = new VariableImp(varName);
        List<Variable> variables = new ArrayList<>();
        variables.add(var);
        
        // Create the term operation
        TermOperationImp termOp = new TermOperationImp(var, variables, alg);
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "create_simple");
        result.put("algebra_path", algebraPath);
        result.put("var_name", varName);
        result.put("arity", termOp.arity());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Get the term from a term operation.
     * Args: --algebra_path <path> --var <name>
     */
    private void handleGetTerm(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra_path");
        String varName = getRequiredArg(options, "var");
        
        // Load the algebra and create term operation
        AlgebraReader reader = new AlgebraReader(algebraPath);
        SmallAlgebra alg = (SmallAlgebra) reader.readAlgebraFile();
        
        Variable var = new VariableImp(varName);
        List<Variable> variables = new ArrayList<>();
        variables.add(var);
        
        TermOperationImp termOp = new TermOperationImp(var, variables, alg);
        
        // Get the term
        Term term = termOp.getTerm();
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "get_term");
        result.put("term_string", term.toString());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Get the ordered variables from a term operation.
     * Args: --algebra_path <path> --vars <comma-separated-vars>
     */
    private void handleGetOrderedVariables(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra_path");
        String varsStr = getRequiredArg(options, "vars");
        
        // Parse variable names
        String[] varNames = varsStr.split(",");
        
        // Load the algebra
        AlgebraReader reader = new AlgebraReader(algebraPath);
        SmallAlgebra alg = (SmallAlgebra) reader.readAlgebraFile();
        
        // Create variables
        List<Variable> variables = new ArrayList<>();
        for (String varName : varNames) {
            variables.add(new VariableImp(varName.trim()));
        }
        
        // For simplicity, use the first variable as the term
        Term term = variables.get(0);
        
        // Create the term operation
        TermOperationImp termOp = new TermOperationImp(term, variables, alg);
        
        // Get ordered variables
        List orderedVars = termOp.getOrderedVariables();
        List<String> varStrings = new ArrayList<>();
        for (Object v : orderedVars) {
            varStrings.add(v.toString());
        }
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "get_ordered_variables");
        result.put("variables", varStrings);
        result.put("count", varStrings.size());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Evaluate the term operation at given arguments.
     * Args: --algebra_path <path> [--var <name> | --term <term_string> --vars <vars>] --args <comma-separated-ints>
     */
    private void handleIntValueAt(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra_path");
        String argsStr = getRequiredArg(options, "args");
        
        // Parse arguments
        String[] argStrs = argsStr.split(",");
        int[] args = new int[argStrs.length];
        for (int i = 0; i < argStrs.length; i++) {
            args[i] = Integer.parseInt(argStrs[i].trim());
        }
        
        // Load the algebra
        AlgebraReader reader = new AlgebraReader(algebraPath);
        SmallAlgebra alg = (SmallAlgebra) reader.readAlgebraFile();
        
        Term term;
        List<Variable> variables = new ArrayList<>();
        
        // Check if using term string or simple variable
        if (options.containsKey("term") && options.containsKey("vars")) {
            // Use term string
            String termStr = getRequiredArg(options, "term");
            String varsStr = getRequiredArg(options, "vars");
            
            term = Terms.stringToTerm(termStr);
            
            String[] varNames = varsStr.split(",");
            for (String varName : varNames) {
                variables.add(new VariableImp(varName.trim()));
            }
        } else {
            // Use simple variable
            String varName = getRequiredArg(options, "var");
            Variable var = new VariableImp(varName);
            variables.add(var);
            term = var;
        }
        
        TermOperationImp termOp = new TermOperationImp(term, variables, alg);
        
        // Evaluate
        int value = termOp.intValueAt(args);
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "int_value_at");
        result.put("args", argsStr);
        result.put("value", value);
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Get the arity of a term operation.
     * Args: --algebra_path <path> --var <name>
     */
    private void handleArity(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra_path");
        String varName = getRequiredArg(options, "var");
        
        // Load the algebra and create term operation
        AlgebraReader reader = new AlgebraReader(algebraPath);
        SmallAlgebra alg = (SmallAlgebra) reader.readAlgebraFile();
        
        Variable var = new VariableImp(varName);
        List<Variable> variables = new ArrayList<>();
        variables.add(var);
        
        TermOperationImp termOp = new TermOperationImp(var, variables, alg);
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "arity");
        result.put("arity", termOp.arity());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Get the string representation of a term operation.
     * Args: --algebra_path <path> --var <name>
     */
    private void handleToString(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra_path");
        String varName = getRequiredArg(options, "var");
        
        // Load the algebra and create term operation
        AlgebraReader reader = new AlgebraReader(algebraPath);
        SmallAlgebra alg = (SmallAlgebra) reader.readAlgebraFile();
        
        Variable var = new VariableImp(varName);
        List<Variable> variables = new ArrayList<>();
        variables.add(var);
        
        TermOperationImp termOp = new TermOperationImp(var, variables, alg);
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "to_string");
        result.put("string", termOp.toString());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Run basic functionality tests.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        String algebraPath = getOptionalArg(options, "algebra_path", "resources/algebras/cyclic3.ua");
        
        // Load the algebra
        AlgebraReader reader = new AlgebraReader(algebraPath);
        SmallAlgebra alg = (SmallAlgebra) reader.readAlgebraFile();
        
        // Create a simple variable term operation
        Variable x = new VariableImp("x");
        List<Variable> variables = new ArrayList<>();
        variables.add(x);
        
        TermOperationImp termOp = new TermOperationImp(x, variables, alg);
        
        // Run tests
        boolean passed = true;
        List<String> tests = new ArrayList<>();
        
        // Test 1: Check arity
        if (termOp.arity() == 1) {
            tests.add("arity: PASS");
        } else {
            tests.add("arity: FAIL (expected 1, got " + termOp.arity() + ")");
            passed = false;
        }
        
        // Test 2: Check getTerm
        Term term = termOp.getTerm();
        if (term != null && term.toString().equals("x")) {
            tests.add("getTerm: PASS");
        } else {
            tests.add("getTerm: FAIL (expected 'x', got '" + (term != null ? term.toString() : "null") + "')");
            passed = false;
        }
        
        // Test 3: Check getOrderedVariables
        List orderedVars = termOp.getOrderedVariables();
        if (orderedVars != null && orderedVars.size() == 1) {
            tests.add("getOrderedVariables: PASS");
        } else {
            tests.add("getOrderedVariables: FAIL (expected size 1, got " + (orderedVars != null ? orderedVars.size() : "null") + ")");
            passed = false;
        }
        
        // Test 4: Check intValueAt - identity function for variable
        int[] args = {0};
        int value = termOp.intValueAt(args);
        if (value == 0) {
            tests.add("intValueAt([0]): PASS");
        } else {
            tests.add("intValueAt([0]): FAIL (expected 0, got " + value + ")");
            passed = false;
        }
        
        // Test 5: Check toString
        String str = termOp.toString();
        if (str != null && str.equals("x")) {
            tests.add("toString: PASS");
        } else {
            tests.add("toString: FAIL (expected 'x', got '" + str + "')");
            passed = false;
        }
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "test");
        result.put("algebra_path", algebraPath);
        result.put("tests", tests);
        result.put("all_passed", passed);
        result.put("status", passed ? "success" : "failure");
        
        handleSuccess(result);
    }
    
    /**
     * Create TermOperationImp from a term string (supports NonVariableTerm).
     * Args: --algebra_path <path> --term <term_string> --vars <comma-separated-vars>
     */
    private void handleCreateFromTerm(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra_path");
        String termStr = getRequiredArg(options, "term");
        String varsStr = getRequiredArg(options, "vars");
        
        // Load the algebra
        AlgebraReader reader = new AlgebraReader(algebraPath);
        SmallAlgebra alg = (SmallAlgebra) reader.readAlgebraFile();
        
        // Parse term string
        Term term = Terms.stringToTerm(termStr);
        
        // Parse variable names
        String[] varNames = varsStr.split(",");
        List<Variable> variables = new ArrayList<>();
        for (String varName : varNames) {
            variables.add(new VariableImp(varName.trim()));
        }
        
        // Create the term operation
        TermOperationImp termOp = new TermOperationImp(term, variables, alg);
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "create_from_term");
        result.put("algebra_path", algebraPath);
        result.put("term_string", termStr);
        result.put("variables", Arrays.asList(varNames));
        result.put("arity", termOp.arity());
        result.put("set_size", termOp.getSetSize());
        result.put("term_string_result", termOp.toString());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Get the operation table for a term operation.
     * Args: --algebra_path <path> --term <term_string> --vars <comma-separated-vars>
     */
    private void handleGetTable(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra_path");
        String termStr = getRequiredArg(options, "term");
        String varsStr = getRequiredArg(options, "vars");
        
        // Load the algebra
        AlgebraReader reader = new AlgebraReader(algebraPath);
        SmallAlgebra alg = (SmallAlgebra) reader.readAlgebraFile();
        
        // Parse term string
        Term term = Terms.stringToTerm(termStr);
        
        // Parse variable names
        String[] varNames = varsStr.split(",");
        List<Variable> variables = new ArrayList<>();
        for (String varName : varNames) {
            variables.add(new VariableImp(varName.trim()));
        }
        
        // Create the term operation
        TermOperationImp termOp = new TermOperationImp(term, variables, alg);
        
        // Get the table (force creation if needed)
        int[] table = termOp.getTable(true);
        
        // Convert to list for JSON
        List<Integer> tableList = new ArrayList<>();
        if (table != null) {
            for (int val : table) {
                tableList.add(val);
            }
        }
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "get_table");
        result.put("term_string", termStr);
        result.put("arity", termOp.arity());
        result.put("set_size", termOp.getSetSize());
        result.put("table_size", tableList.size());
        result.put("table", tableList);
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Evaluate the term operation at given arguments (valueAt method).
     * Args: --algebra_path <path> --term <term_string> --vars <comma-separated-vars> --args <comma-separated-ints>
     */
    private void handleValueAt(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra_path");
        String termStr = getRequiredArg(options, "term");
        String varsStr = getRequiredArg(options, "vars");
        String argsStr = getRequiredArg(options, "args");
        
        // Parse arguments
        String[] argStrs = argsStr.split(",");
        List<Integer> argsList = new ArrayList<>();
        for (String argStr : argStrs) {
            argsList.add(Integer.parseInt(argStr.trim()));
        }
        
        // Load the algebra
        AlgebraReader reader = new AlgebraReader(algebraPath);
        SmallAlgebra alg = (SmallAlgebra) reader.readAlgebraFile();
        
        // Parse term string
        Term term = Terms.stringToTerm(termStr);
        
        // Parse variable names
        String[] varNames = varsStr.split(",");
        List<Variable> variables = new ArrayList<>();
        for (String varName : varNames) {
            variables.add(new VariableImp(varName.trim()));
        }
        
        // Create the term operation
        TermOperationImp termOp = new TermOperationImp(term, variables, alg);
        
        // Convert List<Integer> to int[] for intValueAt
        int[] argsArray = new int[argsList.size()];
        for (int i = 0; i < argsList.size(); i++) {
            argsArray[i] = argsList.get(i);
        }
        
        // Evaluate using intValueAt (more reliable than valueAt)
        int value = termOp.intValueAt(argsArray);
        
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("command", "value_at");
        result.put("term_string", termStr);
        result.put("args", argsList);
        result.put("value", value);
        result.put("value_type", "Integer");
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the TermOperationImp wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create_simple --algebra_path resources/algebras/cyclic3.ua --var x",
            "create_from_term --algebra_path resources/algebras/baker2.ua --term bak(x,y,z) --vars x,y,z",
            "get_term --algebra_path resources/algebras/cyclic3.ua --var x",
            "get_ordered_variables --algebra_path resources/algebras/cyclic3.ua --vars x,y",
            "int_value_at --algebra_path resources/algebras/cyclic3.ua --var x --args 1",
            "value_at --algebra_path resources/algebras/baker2.ua --term bak(x,y,z) --vars x,y,z --args 0,0,0",
            "get_table --algebra_path resources/algebras/baker2.ua --term bak(x,y,z) --vars x,y,z",
            "arity --algebra_path resources/algebras/cyclic3.ua --var x",
            "to_string --algebra_path resources/algebras/cyclic3.ua --var x",
            "test [--algebra_path <path>]"
        };
        
        showUsage("TermOperationImp", 
                 "CLI wrapper for org.uacalc.alg.op.TermOperationImp operations", 
                 examples);
    }
}

