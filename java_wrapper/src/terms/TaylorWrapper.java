/* TaylorWrapper.java - CLI wrapper for org.uacalc.terms.Taylor
 * 
 * This wrapper exposes all public methods of the Taylor class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.terms;

import java.util.*;
import org.uacalc.terms.*;
import org.uacalc.alg.op.OperationSymbol;
import org.uacalc.util.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Taylor class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class TaylorWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Taylor CLI wrapper.
     */
    public static void main(String[] args) {
        TaylorWrapper wrapper = new TaylorWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Taylor wrapper failed", e);
        }
    }
    
    /**
     * Run the Taylor CLI wrapper with the given arguments.
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
                
            case "markovic_mckenzie_term":
                handleMarkovicMcKenzieTerm(options);
                break;
                
            case "siggers_term":
                handleSiggersTerm(options);
                break;
                
            case "new_with_arity":
                handleNewWithArity(options);
                break;
                
            case "canonical_form":
                handleCanonicalForm(options);
                break;
                
            case "term_from_array":
                handleTermFromArray(options);
                break;
                
            case "lexicographically_compare_arrays":
                handleLexicographicallyCompareArrays(options);
                break;
                
            case "arity":
                handleArity(options);
                break;
                
            case "inteqs":
                handleInteqs(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Get the Markovic-McKenzie term.
     */
    private void handleMarkovicMcKenzieTerm(Map<String, String> options) {
        try {
            Taylor taylor = Taylor.markovicMcKenzieTerm();
            
            Map<String, Object> data = new HashMap<>();
            data.put("command", "markovic_mckenzie_term");
            data.put("arity", taylor.arity());
            data.put("inteqs_count", taylor.inteqs().size());
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to get Markovic-McKenzie term", e);
        }
    }
    
    /**
     * Get the Siggers term.
     */
    private void handleSiggersTerm(Map<String, String> options) {
        try {
            Taylor taylor = Taylor.siggersTerm();
            
            Map<String, Object> data = new HashMap<>();
            data.put("command", "siggers_term");
            data.put("arity", taylor.arity());
            data.put("inteqs_count", taylor.inteqs().size());
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to get Siggers term", e);
        }
    }
    
    /**
     * Create a new Taylor with arity and equations.
     */
    private void handleNewWithArity(Map<String, String> options) {
        try {
            int arity = getIntArg(options, "arity");
            String eqsStr = getRequiredArg(options, "eqs");
            
            // Parse equations: format is "[[1,0,0,0],[0,0,1,1]]:[[0,0,1,0],[0,1,0,0]]"
            List<List<IntArray>> eqs = parseEquations(eqsStr);
            
            Taylor taylor = new Taylor(arity, eqs);
            
            Map<String, Object> data = new HashMap<>();
            data.put("command", "new_with_arity");
            data.put("arity", taylor.arity());
            data.put("inteqs_count", taylor.inteqs().size());
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to create Taylor", e);
        }
    }
    
    /**
     * Get the canonical form of a term.
     */
    private void handleCanonicalForm(Map<String, String> options) {
        try {
            String termStr = getRequiredArg(options, "term");
            int arity = getIntArg(options, "arity");
            String eqsStr = getRequiredArg(options, "eqs");
            
            List<List<IntArray>> eqs = parseEquations(eqsStr);
            Taylor taylor = new Taylor(arity, eqs);
            
            // Parse the term
            Term term = TermParser.parse(termStr);
            Term canonical = taylor.canonicalForm(term);
            
            Map<String, Object> data = new HashMap<>();
            data.put("command", "canonical_form");
            data.put("status", canonical.toString());
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to get canonical form", e);
        }
    }
    
    /**
     * Create a term from an array.
     */
    private void handleTermFromArray(Map<String, String> options) {
        try {
            String arrStr = getRequiredArg(options, "arr");
            int arity = getIntArg(options, "arity");
            String eqsStr = getRequiredArg(options, "eqs");
            
            // Parse array: format is "0,1,1,0"
            String[] parts = arrStr.split(",");
            int[] arr = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                arr[i] = Integer.parseInt(parts[i].trim());
            }
            
            List<List<IntArray>> eqs = parseEquations(eqsStr);
            Taylor taylor = new Taylor(arity, eqs);
            
            Term term = taylor.termFromArray(arr);
            
            Map<String, Object> data = new HashMap<>();
            data.put("command", "term_from_array");
            data.put("status", term.toString());
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to create term from array", e);
        }
    }
    
    /**
     * Lexicographically compare two arrays.
     */
    private void handleLexicographicallyCompareArrays(Map<String, String> options) {
        try {
            String aStr = getRequiredArg(options, "a");
            String bStr = getRequiredArg(options, "b");
            
            // Parse arrays
            String[] aParts = aStr.split(",");
            int[] a = new int[aParts.length];
            for (int i = 0; i < aParts.length; i++) {
                a[i] = Integer.parseInt(aParts[i].trim());
            }
            
            String[] bParts = bStr.split(",");
            int[] b = new int[bParts.length];
            for (int i = 0; i < bParts.length; i++) {
                b[i] = Integer.parseInt(bParts[i].trim());
            }
            
            int result = Taylor.lexicographicallyCompare(a, b);
            
            Map<String, Object> data = new HashMap<>();
            data.put("command", "lexicographically_compare_arrays");
            data.put("status", result);
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to compare arrays", e);
        }
    }
    
    /**
     * Get the arity of a Taylor term.
     */
    private void handleArity(Map<String, String> options) {
        try {
            int arity = getIntArg(options, "arity");
            String eqsStr = getRequiredArg(options, "eqs");
            
            List<List<IntArray>> eqs = parseEquations(eqsStr);
            Taylor taylor = new Taylor(arity, eqs);
            
            Map<String, Object> data = new HashMap<>();
            data.put("command", "arity");
            data.put("status", taylor.arity());
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to get arity", e);
        }
    }
    
    /**
     * Get the integer equations.
     */
    private void handleInteqs(Map<String, String> options) {
        try {
            int arity = getIntArg(options, "arity");
            String eqsStr = getRequiredArg(options, "eqs");
            
            List<List<IntArray>> eqs = parseEquations(eqsStr);
            Taylor taylor = new Taylor(arity, eqs);
            
            List<List<IntArray>> inteqs = taylor.inteqs();
            List<String> eqStrings = new ArrayList<>();
            for (List<IntArray> eq : inteqs) {
                StringBuilder sb = new StringBuilder();
                sb.append("[");
                sb.append(arrayToString(eq.get(0).getArray()));
                sb.append(",");
                sb.append(arrayToString(eq.get(1).getArray()));
                sb.append("]");
                eqStrings.add(sb.toString());
            }
            
            Map<String, Object> data = new HashMap<>();
            data.put("command", "inteqs");
            data.put("status", eqStrings);
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to get inteqs", e);
        }
    }
    
    /**
     * Run basic tests to verify Taylor functionality.
     */
    private void handleTest(Map<String, String> options) {
        try {
            // Test Markovic-McKenzie term
            Taylor mm = Taylor.markovicMcKenzieTerm();
            assert mm.arity() == 4 : "Markovic-McKenzie arity should be 4";
            
            // Test Siggers term
            Taylor siggers = Taylor.siggersTerm();
            assert siggers.arity() == 6 : "Siggers arity should be 6";
            
            // Test lexicographic comparison
            int[] a = {1, 2, 3};
            int[] b = {1, 2, 4};
            int result = Taylor.lexicographicallyCompare(a, b);
            assert result < 0 : "a should be less than b";
            
            Map<String, Object> data = new HashMap<>();
            data.put("command", "test");
            data.put("status", "All tests passed");
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Test failed", e);
        }
    }
    
    /**
     * Parse equations from string format.
     * Format: "[[1,0,0,0],[0,0,1,1]]:[[0,0,1,0],[0,1,0,0]]"
     */
    private List<List<IntArray>> parseEquations(String eqsStr) {
        List<List<IntArray>> eqs = new ArrayList<>();
        String[] eqParts = eqsStr.split(":");
        
        for (String eqPart : eqParts) {
            List<IntArray> eq = new ArrayList<>();
            // Remove outer brackets
            eqPart = eqPart.trim();
            if (eqPart.startsWith("[") && eqPart.endsWith("]")) {
                eqPart = eqPart.substring(1, eqPart.length() - 1);
            }
            
            // Split into two sides
            String[] sides = eqPart.split("\\],\\[");
            for (String side : sides) {
                side = side.replace("[", "").replace("]", "").trim();
                String[] nums = side.split(",");
                int[] arr = new int[nums.length];
                for (int i = 0; i < nums.length; i++) {
                    arr[i] = Integer.parseInt(nums[i].trim());
                }
                eq.add(new IntArray(arr));
            }
            eqs.add(eq);
        }
        
        return eqs;
    }
    
    /**
     * Convert an array to a string representation.
     */
    private String arrayToString(int[] arr) {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        for (int i = 0; i < arr.length; i++) {
            if (i > 0) sb.append(",");
            sb.append(arr[i]);
        }
        sb.append("]");
        return sb.toString();
    }
    
    /**
     * Show usage information for the Taylor wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "help - Show this help message",
            "markovic_mckenzie_term - Get the Markovic-McKenzie term",
            "siggers_term - Get the Siggers term",
            "new_with_arity --arity 4 --eqs '[[1,0,0,0],[0,0,1,1]]:[[0,0,1,0],[0,1,0,0]]' - Create a new Taylor",
            "lexicographically_compare_arrays --a 1,2,3 --b 1,2,4 - Compare two arrays",
            "arity --arity 4 --eqs '[[1,0,0,0],[0,0,1,1]]' - Get the arity",
            "test - Run basic tests"
        };
        
        showUsage("Taylor", 
                 "CLI wrapper for org.uacalc.terms.Taylor operations", 
                 examples);
    }
}

/**
 * Simple term parser for testing.
 */
class TermParser {
    public static Term parse(String str) {
        str = str.trim();
        
        // Check if it's a variable
        if (!str.contains("(")) {
            return new VariableImp(str);
        }
        
        // Parse as compound term
        int parenPos = str.indexOf('(');
        String opName = str.substring(0, parenPos);
        String argsStr = str.substring(parenPos + 1, str.lastIndexOf(')'));
        
        List<Term> children = parseArgs(argsStr);
        OperationSymbol sym = new OperationSymbol(opName, children.size(), false);
        
        return new NonVariableTerm(sym, children);
    }
    
    private static List<Term> parseArgs(String argsStr) {
        List<Term> args = new ArrayList<>();
        int depth = 0;
        int start = 0;
        
        for (int i = 0; i < argsStr.length(); i++) {
            char c = argsStr.charAt(i);
            if (c == '(') depth++;
            else if (c == ')') depth--;
            else if (c == ',' && depth == 0) {
                args.add(parse(argsStr.substring(start, i)));
                start = i + 1;
            }
        }
        
        // Add last argument
        if (start < argsStr.length()) {
            args.add(parse(argsStr.substring(start)));
        }
        
        return args;
    }
}
