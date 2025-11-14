/* ParameterizedAlgebraWrapper.java - CLI wrapper for org.uacalc.alg.ParameterizedAlgebra
 * 
 * This wrapper exposes all public methods of the ParameterizedAlgebra class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.ParameterizedAlgebra;
import org.uacalc.alg.op.ParameterizedOperation;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the ParameterizedAlgebra class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class ParameterizedAlgebraWrapper extends WrapperBase {
    
    /**
     * Main entry point for the ParameterizedAlgebra CLI wrapper.
     */
    public static void main(String[] args) {
        ParameterizedAlgebraWrapper wrapper = new ParameterizedAlgebraWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("ParameterizedAlgebra wrapper failed", e);
        }
    }
    
    /**
     * Run the ParameterizedAlgebra CLI wrapper with the given arguments.
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
                
            case "get_parameter_map":
                handleGetParameterMap(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Test get_parameter_map method.
     */
    private void handleGetParameterMap(Map<String, String> options) throws Exception {
        String paramNamesStr = getRequiredArg(options, "param_names");
        String valuesStr = getRequiredArg(options, "values");
        String name = getOptionalArg(options, "name", "TestAlgebra");
        String setSizeExp = getOptionalArg(options, "set_size_exp", "n");
        String description = getOptionalArg(options, "description", "Test algebra");
        
        // Parse parameter names (comma-separated)
        List<String> paramNames = parseStringList(paramNamesStr);
        
        // Parse values (comma-separated integers)
        List<Integer> values = parseIntegerList(valuesStr);
        
        // Create ParameterizedAlgebra using reflection
        ParameterizedAlgebra paramAlg = new ParameterizedAlgebra();
        setField(paramAlg, "parameterNames", paramNames);
        setField(paramAlg, "name", name);
        setField(paramAlg, "setSizeExp", setSizeExp);
        setField(paramAlg, "description", description);
        setField(paramAlg, "ops", new ArrayList<ParameterizedOperation>());
        
        // Get parameter map
        Map<String, String> parmMap = paramAlg.getParameterMap(values);
        
        // Build response
        Map<String, Object> response = new HashMap<>();
        response.put("command", "get_parameter_map");
        response.put("param_names", paramNames);
        response.put("values", values);
        response.put("status", parmMap);
        
        handleSuccess(response);
    }
    
    /**
     * Set a field using reflection (for package-private fields).
     */
    private void setField(Object obj, String fieldName, Object value) throws Exception {
        java.lang.reflect.Field field = obj.getClass().getDeclaredField(fieldName);
        field.setAccessible(true);
        field.set(obj, value);
    }
    
    /**
     * Run basic tests for ParameterizedAlgebra.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        List<Map<String, Object>> testResults = new ArrayList<>();
        
        // Test 1: Basic parameter map
        try {
            List<String> paramNames = Arrays.asList("n", "m");
            List<Integer> values = Arrays.asList(3, 4);
            
            ParameterizedAlgebra paramAlg = new ParameterizedAlgebra();
            setField(paramAlg, "parameterNames", paramNames);
            setField(paramAlg, "name", "TestAlgebra");
            setField(paramAlg, "setSizeExp", "n*m");
            setField(paramAlg, "description", "Test algebra");
            setField(paramAlg, "ops", new ArrayList<ParameterizedOperation>());
            
            Map<String, String> parmMap = paramAlg.getParameterMap(values);
            
            Map<String, Object> test1 = new HashMap<>();
            test1.put("test", "basic_parameter_map");
            test1.put("status", "pass");
            test1.put("result", parmMap);
            testResults.add(test1);
        } catch (Exception e) {
            Map<String, Object> test1 = new HashMap<>();
            test1.put("test", "basic_parameter_map");
            test1.put("status", "fail");
            test1.put("error", e.getMessage());
            testResults.add(test1);
        }
        
        // Test 2: Single parameter
        try {
            List<String> paramNames = Arrays.asList("n");
            List<Integer> values = Arrays.asList(5);
            
            ParameterizedAlgebra paramAlg = new ParameterizedAlgebra();
            setField(paramAlg, "parameterNames", paramNames);
            setField(paramAlg, "name", "Zn");
            setField(paramAlg, "setSizeExp", "n");
            setField(paramAlg, "description", "Cyclic group");
            setField(paramAlg, "ops", new ArrayList<ParameterizedOperation>());
            
            Map<String, String> parmMap = paramAlg.getParameterMap(values);
            
            Map<String, Object> test2 = new HashMap<>();
            test2.put("test", "single_parameter");
            test2.put("status", "pass");
            test2.put("result", parmMap);
            testResults.add(test2);
        } catch (Exception e) {
            Map<String, Object> test2 = new HashMap<>();
            test2.put("test", "single_parameter");
            test2.put("status", "fail");
            test2.put("error", e.getMessage());
            testResults.add(test2);
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "test");
        response.put("tests", testResults);
        response.put("total", testResults.size());
        response.put("status", "completed");
        
        handleSuccess(response);
    }
    
    /**
     * Parse a comma-separated list of strings.
     */
    private List<String> parseStringList(String str) {
        if (str == null || str.trim().isEmpty()) {
            return new ArrayList<>();
        }
        return Arrays.asList(str.split(","));
    }
    
    /**
     * Parse a comma-separated list of integers.
     */
    private List<Integer> parseIntegerList(String str) {
        if (str == null || str.trim().isEmpty()) {
            return new ArrayList<>();
        }
        List<Integer> result = new ArrayList<>();
        for (String s : str.split(",")) {
            result.add(Integer.parseInt(s.trim()));
        }
        return result;
    }
    
    /**
     * Show usage information for the ParameterizedAlgebra wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "get_parameter_map --param_names n,m --values 3,4",
            "get_parameter_map --param_names n --values 5 --name Zn --set_size_exp n",
            "test"
        };
        
        showUsage("ParameterizedAlgebra", 
                 "CLI wrapper for org.uacalc.alg.ParameterizedAlgebra operations", 
                 examples);
    }
}
