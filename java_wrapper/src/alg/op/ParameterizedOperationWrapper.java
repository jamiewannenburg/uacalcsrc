/* ParameterizedOperationWrapper.java - CLI wrapper for org.uacalc.alg.op.ParameterizedOperation
 * 
 * This wrapper exposes all public methods of the ParameterizedOperation class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg.op;

import java.util.*;
import org.uacalc.alg.op.ParameterizedOperation;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the ParameterizedOperation class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class ParameterizedOperationWrapper extends WrapperBase {
    
    /**
     * Main entry point for the ParameterizedOperation CLI wrapper.
     */
    public static void main(String[] args) {
        ParameterizedOperationWrapper wrapper = new ParameterizedOperationWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("ParameterizedOperation wrapper failed", e);
        }
    }
    
    /**
     * Run the ParameterizedOperation CLI wrapper with the given arguments.
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
                
            case "sub_parm_values":
                handleSubParmValues(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Test sub_parm_values method.
     */
    private void handleSubParmValues(Map<String, String> options) throws Exception {
        String paramString = getRequiredArg(options, "param_string");
        String parmMapStr = getOptionalArg(options, "parm_map", "");
        
        // Parse parameter map (format: key1=value1,key2=value2)
        Map<String, String> parmMap = new HashMap<>();
        if (!parmMapStr.isEmpty()) {
            for (String pair : parmMapStr.split(",")) {
                String[] parts = pair.split("=");
                if (parts.length == 2) {
                    parmMap.put(parts[0].trim(), parts[1].trim());
                }
            }
        }
        
        // Call subParmValues
        String result = ParameterizedOperation.subParmValues(paramString, parmMap);
        
        // Build response
        Map<String, Object> response = new HashMap<>();
        response.put("command", "sub_parm_values");
        response.put("param_string", paramString);
        response.put("parm_map", parmMap);
        response.put("status", result);
        
        handleSuccess(response);
    }
    
    /**
     * Run basic tests for ParameterizedOperation.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        List<Map<String, Object>> testResults = new ArrayList<>();
        
        // Test 1: Basic sub_parm_values
        try {
            Map<String, String> parmMap = new HashMap<>();
            parmMap.put("n", "5");
            
            String result = ParameterizedOperation.subParmValues("n+1", parmMap);
            
            Map<String, Object> test1 = new HashMap<>();
            test1.put("test", "basic_sub_parm_values");
            test1.put("status", "pass");
            test1.put("result", result);
            testResults.add(test1);
        } catch (Exception e) {
            Map<String, Object> test1 = new HashMap<>();
            test1.put("test", "basic_sub_parm_values");
            test1.put("status", "fail");
            test1.put("error", e.getMessage());
            testResults.add(test1);
        }
        
        // Test 2: Empty parameter map
        try {
            Map<String, String> parmMap = new HashMap<>();
            
            String result = ParameterizedOperation.subParmValues("n*m", parmMap);
            
            Map<String, Object> test2 = new HashMap<>();
            test2.put("test", "empty_parameter_map");
            test2.put("status", "pass");
            test2.put("result", result);
            testResults.add(test2);
        } catch (Exception e) {
            Map<String, Object> test2 = new HashMap<>();
            test2.put("test", "empty_parameter_map");
            test2.put("status", "fail");
            test2.put("error", e.getMessage());
            testResults.add(test2);
        }
        
        // Test 3: Multiple parameters
        try {
            Map<String, String> parmMap = new HashMap<>();
            parmMap.put("n", "3");
            parmMap.put("m", "4");
            
            String result = ParameterizedOperation.subParmValues("n*m", parmMap);
            
            Map<String, Object> test3 = new HashMap<>();
            test3.put("test", "multiple_parameters");
            test3.put("status", "pass");
            test3.put("result", result);
            testResults.add(test3);
        } catch (Exception e) {
            Map<String, Object> test3 = new HashMap<>();
            test3.put("test", "multiple_parameters");
            test3.put("status", "fail");
            test3.put("error", e.getMessage());
            testResults.add(test3);
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "test");
        response.put("tests", testResults);
        response.put("total", testResults.size());
        response.put("status", "completed");
        
        handleSuccess(response);
    }
    
    /**
     * Show usage information for the ParameterizedOperation wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "sub_parm_values --param_string \"n+1\" --parm_map n=5",
            "sub_parm_values --param_string \"n*m\" --parm_map n=3,m=4",
            "test"
        };
        
        showUsage("ParameterizedOperation", 
                 "CLI wrapper for org.uacalc.alg.op.ParameterizedOperation operations", 
                 examples);
    }
}
