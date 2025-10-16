/* TermsWrapper.java - CLI wrapper for org.uacalc.terms.Terms
 * 
 * This wrapper exposes all public static methods of the Terms utility class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.terms;

import java.util.*;
import org.uacalc.terms.*;
import org.uacalc.alg.op.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Terms utility class that provides command-line access
 * to all public static methods for testing and validation purposes.
 */
public class TermsWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Terms CLI wrapper.
     */
    public static void main(String[] args) {
        TermsWrapper wrapper = new TermsWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Terms wrapper failed", e);
        }
    }
    
    /**
     * Run the Terms CLI wrapper with the given arguments.
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
                
            case "string_to_term":
                handleStringToTerm(options);
                break;
                
            case "is_valid_var_string":
                handleIsValidVarString(options);
                break;
                
            case "is_valid_op_name_string":
                handleIsValidOpNameString(options);
                break;
                
            case "flatten":
                handleFlatten(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle string_to_term command - parse a string into a Term.
     */
    private void handleStringToTerm(Map<String, String> options) {
        String str = getRequiredArg(options, "str");
        
        try {
            Term term = Terms.stringToTerm(str);
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("command", "string_to_term");
            data.put("input", str);
            data.put("term", term.toString());
            data.put("is_variable", term.isaVariable());
            data.put("depth", term.depth());
            data.put("length", term.length());
            
            if (!term.isaVariable()) {
                data.put("leading_op", term.leadingOperationSymbol().name());
                data.put("arity", term.leadingOperationSymbol().arity());
            }
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to parse term from string: " + str, e);
        }
    }
    
    /**
     * Handle is_valid_var_string command - validate if a string can be a variable name.
     */
    private void handleIsValidVarString(Map<String, String> options) {
        String str = getRequiredArg(options, "str");
        
        try {
            boolean isValid = Terms.isValidVarString(str);
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("command", "is_valid_var_string");
            data.put("input", str);
            data.put("status", isValid);
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to validate variable string: " + str, e);
        }
    }
    
    /**
     * Handle is_valid_op_name_string command - validate if a string can be an operation name.
     */
    private void handleIsValidOpNameString(Map<String, String> options) {
        String str = getRequiredArg(options, "str");
        
        try {
            boolean isValid = Terms.isValidOpNameString(str);
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("command", "is_valid_op_name_string");
            data.put("input", str);
            data.put("status", isValid);
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to validate operation name string: " + str, e);
        }
    }
    
    /**
     * Handle flatten command - flatten associative operations in a term.
     */
    private void handleFlatten(Map<String, String> options) {
        String str = getRequiredArg(options, "str");
        
        try {
            Term term = Terms.stringToTerm(str);
            Term flattened = Terms.flatten(term);
            
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("command", "flatten");
            data.put("input", str);
            data.put("original", term.toString());
            data.put("flattened", flattened.toString());
            data.put("original_depth", term.depth());
            data.put("flattened_depth", flattened.depth());
            data.put("original_length", term.length());
            data.put("flattened_length", flattened.length());
            
            handleSuccess(data);
        } catch (Exception e) {
            handleError("Failed to flatten term: " + str, e);
        }
    }
    
    /**
     * Handle test command - run basic functionality tests.
     */
    private void handleTest(Map<String, String> options) {
        Map<String, Object> results = new LinkedHashMap<>();
        int passed = 0;
        int failed = 0;
        
        // Test 1: Parse simple variable
        try {
            Term x = Terms.stringToTerm("x");
            if (x.isaVariable() && x.toString().equals("x")) {
                results.put("test_parse_variable", "PASS");
                passed++;
            } else {
                results.put("test_parse_variable", "FAIL: incorrect result");
                failed++;
            }
        } catch (Exception e) {
            results.put("test_parse_variable", "FAIL: " + e.getMessage());
            failed++;
        }
        
        // Test 2: Parse compound term
        try {
            Term term = Terms.stringToTerm("f(x,y)");
            if (!term.isaVariable() && term.toString().equals("f(x,y)")) {
                results.put("test_parse_compound", "PASS");
                passed++;
            } else {
                results.put("test_parse_compound", "FAIL: incorrect result");
                failed++;
            }
        } catch (Exception e) {
            results.put("test_parse_compound", "FAIL: " + e.getMessage());
            failed++;
        }
        
        // Test 3: Validate valid variable string
        try {
            if (Terms.isValidVarString("x") && Terms.isValidVarString("var1")) {
                results.put("test_valid_var_string", "PASS");
                passed++;
            } else {
                results.put("test_valid_var_string", "FAIL");
                failed++;
            }
        } catch (Exception e) {
            results.put("test_valid_var_string", "FAIL: " + e.getMessage());
            failed++;
        }
        
        // Test 4: Validate invalid variable string
        try {
            if (!Terms.isValidVarString("") && !Terms.isValidVarString("1x") && !Terms.isValidVarString("x,y")) {
                results.put("test_invalid_var_string", "PASS");
                passed++;
            } else {
                results.put("test_invalid_var_string", "FAIL");
                failed++;
            }
        } catch (Exception e) {
            results.put("test_invalid_var_string", "FAIL: " + e.getMessage());
            failed++;
        }
        
        // Test 5: Flatten associative operation
        try {
            // Create an associative operation
            OperationSymbol f = new OperationSymbol("f", 2, true);
            
            // Create term f(f(x,y),z)
            List<Term> args1 = new ArrayList<>();
            args1.add(new VariableImp("x"));
            args1.add(new VariableImp("y"));
            Term inner = new NonVariableTerm(f, args1);
            
            List<Term> args2 = new ArrayList<>();
            args2.add(inner);
            args2.add(new VariableImp("z"));
            Term outer = new NonVariableTerm(f, args2);
            
            Term flattened = Terms.flatten(outer);
            // Should be f(x,y,z)
            if (flattened.toString().equals("f(x,y,z)")) {
                results.put("test_flatten", "PASS");
                passed++;
            } else {
                results.put("test_flatten", "FAIL: got " + flattened.toString());
                failed++;
            }
        } catch (Exception e) {
            results.put("test_flatten", "FAIL: " + e.getMessage());
            failed++;
        }
        
        results.put("summary", passed + " passed, " + failed + " failed");
        handleSuccess(results);
    }
    
    /**
     * Show usage information for the Terms wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "string_to_term --str \"f(x,y)\"",
            "is_valid_var_string --str \"x\"",
            "is_valid_op_name_string --str \"f\"",
            "flatten --str \"f(f(x,y),z)\"",
            "test"
        };
        
        showUsage("Terms", 
                 "CLI wrapper for org.uacalc.terms.Terms utility operations", 
                 examples);
    }
}

