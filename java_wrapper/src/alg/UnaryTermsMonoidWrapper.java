/* UnaryTermsMonoidWrapper.java - CLI wrapper for org.uacalc.alg.UnaryTermsMonoid
 * 
 * This wrapper exposes all public methods of the UnaryTermsMonoid class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.op.Operation;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the UnaryTermsMonoid class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class UnaryTermsMonoidWrapper extends WrapperBase {
    
    private UnaryTermsMonoid monoid;
    private SmallAlgebra generatingAlgebra;
    
    /**
     * Main entry point for the UnaryTermsMonoid CLI wrapper.
     */
    public static void main(String[] args) {
        UnaryTermsMonoidWrapper wrapper = new UnaryTermsMonoidWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("UnaryTermsMonoid wrapper failed", e);
        }
    }
    
    /**
     * Run the UnaryTermsMonoid CLI wrapper with the given arguments.
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
                
            case "construct":
                handleConstruct(options);
                break;
                
            case "construct_with_id":
                handleConstructWithId(options);
                break;
                
            case "algebra_type":
                handleAlgebraType(options);
                break;
                
            case "cardinality":
                handleCardinality(options);
                break;
                
            case "name":
                handleName(options);
                break;
                
            case "set_name":
                handleSetName(options);
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
                
            case "operations_count":
                handleOperationsCount(options);
                break;
                
            case "get_universe_list":
                handleGetUniverseList(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    private void handleConstruct(Map<String, String> options) throws Exception {
        String baseName = getOptionalArg(options, "base_name", "TestBase");
        int baseSize = getIntArg(options, "base_size", 3);
        
        // Create a simple generating algebra
        generatingAlgebra = new BasicAlgebra(baseName, baseSize, new ArrayList<>());
        
        // Create UnaryTermsMonoid
        monoid = new UnaryTermsMonoid(generatingAlgebra);
        
        String result = "{\"command\":\"construct\",\"base_name\":\"" + baseName + 
            "\",\"base_size\":" + baseSize + 
            ",\"name\":\"" + monoid.getName() + 
            "\",\"cardinality\":" + monoid.cardinality() + 
            ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleConstructWithId(Map<String, String> options) throws Exception {
        String baseName = getOptionalArg(options, "base_name", "TestBase");
        int baseSize = getIntArg(options, "base_size", 3);
        boolean includeId = getBoolArg(options, "include_id", false);
        
        // Create a simple generating algebra
        generatingAlgebra = new BasicAlgebra(baseName, baseSize, new ArrayList<>());
        
        // Create UnaryTermsMonoid with includeId flag
        monoid = new UnaryTermsMonoid(generatingAlgebra, includeId);
        
        String result = "{\"command\":\"construct_with_id\",\"base_name\":\"" + baseName + 
            "\",\"base_size\":" + baseSize + 
            ",\"include_id\":" + includeId + 
            ",\"name\":\"" + monoid.getName() + 
            "\",\"cardinality\":" + monoid.cardinality() + 
            ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleAlgebraType(Map<String, String> options) throws Exception {
        if (monoid == null) {
            // Auto-create a default monoid for testing
            generatingAlgebra = new BasicAlgebra("TestBase", 3, new ArrayList<>());
            monoid = new UnaryTermsMonoid(generatingAlgebra);
        }
        
        SmallAlgebra.AlgebraType type = monoid.algebraType();
        String result = "{\"command\":\"algebra_type\",\"type\":\"" + type.toString() + "\",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleCardinality(Map<String, String> options) throws Exception {
        if (monoid == null) {
            // Auto-create a default monoid for testing
            generatingAlgebra = new BasicAlgebra("TestBase", 3, new ArrayList<>());
            monoid = new UnaryTermsMonoid(generatingAlgebra);
        }
        
        int cardinality = monoid.cardinality();
        String result = "{\"command\":\"cardinality\",\"cardinality\":" + cardinality + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleName(Map<String, String> options) throws Exception {
        if (monoid == null) {
            // Auto-create a default monoid for testing
            generatingAlgebra = new BasicAlgebra("TestBase", 3, new ArrayList<>());
            monoid = new UnaryTermsMonoid(generatingAlgebra);
        }
        
        String name = monoid.getName();
        String result = "{\"command\":\"name\",\"name\":\"" + name + "\",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleSetName(Map<String, String> options) throws Exception {
        if (monoid == null) {
            // Auto-create a default monoid for testing
            generatingAlgebra = new BasicAlgebra("TestBase", 3, new ArrayList<>());
            monoid = new UnaryTermsMonoid(generatingAlgebra);
        }
        
        String newName = getRequiredArg(options, "name");
        monoid.setName(newName);
        
        String result = "{\"command\":\"set_name\",\"new_name\":\"" + newName + 
            "\",\"name\":\"" + monoid.getName() + "\",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleIsUnary(Map<String, String> options) throws Exception {
        if (monoid == null) {
            // Auto-create a default monoid for testing
            generatingAlgebra = new BasicAlgebra("TestBase", 3, new ArrayList<>());
            monoid = new UnaryTermsMonoid(generatingAlgebra);
        }
        
        boolean isUnary = monoid.isUnary();
        String result = "{\"command\":\"is_unary\",\"is_unary\":" + isUnary + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleIsIdempotent(Map<String, String> options) throws Exception {
        if (monoid == null) {
            // Auto-create a default monoid for testing
            generatingAlgebra = new BasicAlgebra("TestBase", 3, new ArrayList<>());
            monoid = new UnaryTermsMonoid(generatingAlgebra);
        }
        
        boolean isIdempotent = monoid.isIdempotent();
        String result = "{\"command\":\"is_idempotent\",\"is_idempotent\":" + isIdempotent + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleIsTotal(Map<String, String> options) throws Exception {
        if (monoid == null) {
            // Auto-create a default monoid for testing
            generatingAlgebra = new BasicAlgebra("TestBase", 3, new ArrayList<>());
            monoid = new UnaryTermsMonoid(generatingAlgebra);
        }
        
        boolean isTotal = monoid.isTotal();
        String result = "{\"command\":\"is_total\",\"is_total\":" + isTotal + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleOperationsCount(Map<String, String> options) throws Exception {
        if (monoid == null) {
            // Auto-create a default monoid for testing
            generatingAlgebra = new BasicAlgebra("TestBase", 3, new ArrayList<>());
            monoid = new UnaryTermsMonoid(generatingAlgebra);
        }
        
        int count = monoid.operations().size();
        String result = "{\"command\":\"operations_count\",\"count\":" + count + 
            ",\"operations_count\":" + count + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleGetUniverseList(Map<String, String> options) throws Exception {
        if (monoid == null) {
            // Auto-create a default monoid for testing
            generatingAlgebra = new BasicAlgebra("TestBase", 3, new ArrayList<>());
            monoid = new UnaryTermsMonoid(generatingAlgebra);
        }
        
        List<?> universeList = monoid.getUniverseList();
        int universeSize = universeList != null ? universeList.size() : 0;
        
        // Build universe array - simplified version
        StringBuilder universeJson = new StringBuilder("[");
        if (universeList != null && !universeList.isEmpty()) {
            for (int i = 0; i < Math.min(universeList.size(), 10); i++) {  // Limit to first 10 for readability
                if (i > 0) universeJson.append(",");
                universeJson.append("\"").append(universeList.get(i).toString()).append("\"");
            }
            if (universeList.size() > 10) {
                universeJson.append(",\"...\"");
            }
        }
        universeJson.append("]");
        
        String result = "{\"command\":\"get_universe_list\",\"universe_size\":" + universeSize + 
            ",\"universe\":" + universeJson.toString() + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleTest(Map<String, String> options) throws Exception {
        // Create a test UnaryTermsMonoid
        SmallAlgebra testBase = new BasicAlgebra("TestBase", 2, new ArrayList<>());
        UnaryTermsMonoid testMonoid = new UnaryTermsMonoid(testBase);
        
        // Test basic functionality
        int cardinality = testMonoid.cardinality();
        String name = testMonoid.getName();
        SmallAlgebra.AlgebraType type = testMonoid.algebraType();
        boolean isUnary = testMonoid.isUnary();
        int opsCount = testMonoid.operations().size();
        
        String result = "{\"command\":\"test\",\"name\":\"" + name + 
            "\",\"cardinality\":" + cardinality + 
            ",\"algebra_type\":\"" + type.toString() + 
            "\",\"is_unary\":" + isUnary + 
            ",\"operations_count\":" + opsCount + 
            ",\"status\":\"success\",\"message\":\"Test completed successfully\"}";
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the UnaryTermsMonoid wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "construct --base_name TestBase --base_size 3",
            "construct_with_id --base_name TestBase --base_size 3 --include_id false",
            "algebra_type",
            "cardinality",
            "name",
            "set_name --name NewMonoidName",
            "is_unary",
            "is_idempotent",
            "is_total",
            "operations_count",
            "get_universe_list",
            "test"
        };
        
        showUsage("UnaryTermsMonoid", 
                 "CLI wrapper for org.uacalc.alg.UnaryTermsMonoid operations", 
                 examples);
    }
}
