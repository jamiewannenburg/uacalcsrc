/* SimpleAlgebraWrapper.java - Simple CLI wrapper for org.uacalc.alg.GeneralAlgebra
 * 
 * This is a simplified wrapper that focuses on basic functionality for testing.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.GeneralAlgebra;
import org.uacalc.alg.BasicAlgebra;
import java_wrapper.src.WrapperBase;

/**
 * Simple CLI wrapper for the GeneralAlgebra class.
 */
public class SimpleAlgebraWrapper extends WrapperBase {
    
    public static void main(String[] args) {
        SimpleAlgebraWrapper wrapper = new SimpleAlgebraWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("SimpleAlgebra wrapper failed", e);
        }
    }
    
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
                
            case "test":
                handleTest(options);
                break;
                
            case "cardinality":
                handleCardinality(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    private void handleTest(Map<String, String> options) throws Exception {
        GeneralAlgebra algebra = new BasicAlgebra("TestAlgebra", 3, new ArrayList<>());
        
        String name = algebra.getName();
        int cardinality = algebra.cardinality();
        boolean isUnary = algebra.isUnary();
        boolean isTotal = algebra.isTotal();
        
        handleSuccess("{\"command\":\"test\",\"name\":\"" + name + 
                     "\",\"cardinality\":" + cardinality + 
                     ",\"is_unary\":" + isUnary + 
                     ",\"is_total\":" + isTotal + 
                     ",\"status\":\"success\"}");
    }
    
    private void handleCardinality(Map<String, String> options) throws Exception {
        String name = getStringArg(options, "name", "TestAlgebra");
        String universeStr = getStringArg(options, "universe", "");
        
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
        
        handleSuccess("{\"command\":\"cardinality\",\"name\":\"" + name + "\",\"status\":" + result + "}");
    }
    
    private void showUsage() {
        String[] examples = {
            "test",
            "cardinality --name \"MyAlgebra\" --universe \"0,1,2\""
        };
        
        showUsage("SimpleAlgebra", 
                 "Simple CLI wrapper for org.uacalc.alg.GeneralAlgebra operations", 
                 examples);
    }
    
    private String getStringArg(Map<String, String> options, String key, String defaultValue) {
        String value = options.get(key);
        return value != null ? value : defaultValue;
    }
}
