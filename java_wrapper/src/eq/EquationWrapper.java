/* EquationWrapper.java - CLI wrapper for org.uacalc.eq.Equation
 * 
 * This wrapper exposes all public methods of the Equation class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.eq;

import java.util.*;
import org.uacalc.eq.Equation;
import org.uacalc.terms.*;
import org.uacalc.alg.*;
import org.uacalc.alg.op.*;
import org.uacalc.io.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Equation class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class EquationWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Equation CLI wrapper.
     */
    public static void main(String[] args) {
        EquationWrapper wrapper = new EquationWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Equation wrapper failed", e);
        }
    }
    
    /**
     * Run the Equation CLI wrapper with the given arguments.
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
                
            case "toString":
                handleToString(options);
                break;
                
            case "getVariableList":
                handleGetVariableList(options);
                break;
                
            case "getOperationSymbols":
                handleGetOperationSymbols(options);
                break;
                
            case "findFailure":
                handleFindFailure(options);
                break;
                
            case "findFailureMap":
                handleFindFailureMap(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle toString command.
     */
    private void handleToString(Map<String, String> options) throws Exception {
        String left = getRequiredArg(options, "left");
        String right = getRequiredArg(options, "right");
        
        Term leftTerm = parseTermString(left);
        Term rightTerm = parseTermString(right);
        Equation eq = new Equation(leftTerm, rightTerm);
        
        String result = eq.toString();
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "toString");
        data.put("left", left);
        data.put("right", right);
        data.put("status", result);
        
        handleSuccess(data);
    }
    
    /**
     * Handle getVariableList command.
     */
    private void handleGetVariableList(Map<String, String> options) throws Exception {
        String left = getRequiredArg(options, "left");
        String right = getRequiredArg(options, "right");
        
        Term leftTerm = parseTermString(left);
        Term rightTerm = parseTermString(right);
        Equation eq = new Equation(leftTerm, rightTerm);
        
        List<Variable> varList = eq.getVariableList();
        List<String> varNames = new ArrayList<>();
        for (Variable v : varList) {
            varNames.add(v.name());
        }
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "getVariableList");
        data.put("left", left);
        data.put("right", right);
        data.put("status", varNames);
        
        handleSuccess(data);
    }
    
    /**
     * Handle getOperationSymbols command.
     */
    private void handleGetOperationSymbols(Map<String, String> options) throws Exception {
        String left = getRequiredArg(options, "left");
        String right = getRequiredArg(options, "right");
        
        Term leftTerm = parseTermString(left);
        Term rightTerm = parseTermString(right);
        Equation eq = new Equation(leftTerm, rightTerm);
        
        Set<OperationSymbol> opSymbols = eq.getOperationSymbols();
        List<String> opNames = new ArrayList<>();
        for (OperationSymbol sym : opSymbols) {
            opNames.add(sym.name() + "/" + sym.arity());
        }
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "getOperationSymbols");
        data.put("left", left);
        data.put("right", right);
        data.put("status", opNames);
        
        handleSuccess(data);
    }
    
    /**
     * Handle findFailure command.
     */
    private void handleFindFailure(Map<String, String> options) throws Exception {
        String left = getRequiredArg(options, "left");
        String right = getRequiredArg(options, "right");
        String algPath = getRequiredArg(options, "algebra");
        
        Term leftTerm = parseTermString(left);
        Term rightTerm = parseTermString(right);
        Equation eq = new Equation(leftTerm, rightTerm);
        
        // Load algebra
        AlgebraReader reader = new AlgebraReader(algPath);
        SmallAlgebra alg = (SmallAlgebra) reader.readAlgebraFile();
        
        int[] failure = eq.findFailure(alg);
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "findFailure");
        data.put("left", left);
        data.put("right", right);
        data.put("algebra", algPath);
        
        if (failure == null) {
            data.put("status", null);
        } else {
            List<Integer> failureList = new ArrayList<>();
            for (int i : failure) {
                failureList.add(i);
            }
            data.put("status", failureList);
        }
        
        handleSuccess(data);
    }
    
    /**
     * Handle findFailureMap command.
     */
    private void handleFindFailureMap(Map<String, String> options) throws Exception {
        String left = getRequiredArg(options, "left");
        String right = getRequiredArg(options, "right");
        String algPath = getRequiredArg(options, "algebra");
        
        Term leftTerm = parseTermString(left);
        Term rightTerm = parseTermString(right);
        Equation eq = new Equation(leftTerm, rightTerm);
        
        // Load algebra
        AlgebraReader reader = new AlgebraReader(algPath);
        SmallAlgebra alg = (SmallAlgebra) reader.readAlgebraFile();
        
        Map<Variable, Integer> failureMap = eq.findFailureMap(alg);
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "findFailureMap");
        data.put("left", left);
        data.put("right", right);
        data.put("algebra", algPath);
        
        if (failureMap == null) {
            data.put("status", null);
        } else {
            Map<String, Integer> resultMap = new HashMap<>();
            for (Map.Entry<Variable, Integer> entry : failureMap.entrySet()) {
                resultMap.put(entry.getKey().name(), entry.getValue());
            }
            data.put("status", resultMap);
        }
        
        handleSuccess(data);
    }
    
    /**
     * Handle test command.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        Map<String, Object> data = new HashMap<>();
        data.put("command", "test");
        
        try {
            // Test 1: Simple variable equation
            Term x = new VariableImp("x");
            Term y = new VariableImp("y");
            Equation eq1 = new Equation(x, y);
            
            String eq1Str = eq1.toString();
            if (!eq1Str.equals("x = y")) {
                throw new Exception("Expected 'x = y', got: " + eq1Str);
            }
            
            List<Variable> vars = eq1.getVariableList();
            if (vars.size() != 2) {
                throw new Exception("Expected 2 variables, got: " + vars.size());
            }
            
            data.put("status", "All tests passed");
            handleSuccess(data);
        } catch (Exception e) {
            data.put("status", "Test failed: " + e.getMessage());
            handleError("Test failed", e);
        }
    }
    
    /**
     * Parse a simple term string into a Term object.
     * Supports simple variables like "x", "y", etc.
     */
    private Term parseTermString(String termStr) throws Exception {
        termStr = termStr.trim();
        
        // For now, only support simple variable terms
        if (termStr.matches("[a-zA-Z_][a-zA-Z0-9_]*")) {
            return new VariableImp(termStr);
        }
        
        throw new Exception("Unsupported term format: " + termStr + " (only simple variables supported)");
    }
    
    /**
     * Show usage information for the Equation wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "toString --left x --right y",
            "getVariableList --left x --right y",
            "getOperationSymbols --left x --right y",
            "findFailure --left x --right y --algebra path/to/algebra.ua",
            "findFailureMap --left x --right y --algebra path/to/algebra.ua",
            "test"
        };
        
        showUsage("Equation", 
                 "CLI wrapper for org.uacalc.eq.Equation operations", 
                 examples);
    }
}
