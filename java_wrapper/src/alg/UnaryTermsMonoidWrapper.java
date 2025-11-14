/* UnaryTermsMonoidWrapper.java - CLI wrapper for org.uacalc.alg.UnaryTermsMonoid
 * 
 * This wrapper exposes all public methods of the UnaryTermsMonoid class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.SmallAlgebra.AlgebraType;
import org.uacalc.alg.op.Operation;
import org.uacalc.io.AlgebraIO;
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
                
            case "new":
                handleNew(options);
                break;
                
            case "new_with_id":
                handleNewWithId(options);
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
                
            case "get_element":
                handleGetElement(options);
                break;
                
            case "element_index":
                handleElementIndex(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Create a new UnaryTermsMonoid from a generating algebra.
     * Usage: new --alg_file file.ua
     */
    private void handleNew(Map<String, String> options) throws Exception {
        String algFile = getRequiredArg(options, "alg_file");
        
        generatingAlgebra = AlgebraIO.readAlgebraFile(algFile);
        monoid = new UnaryTermsMonoid(generatingAlgebra);
        
        Map<String, Object> result = new HashMap<>();
        result.put("name", monoid.getName());
        result.put("cardinality", monoid.cardinality());
        result.put("algebra_type", monoid.algebraType().toString());
        
        handleSuccess(result);
    }
    
    /**
     * Create a new UnaryTermsMonoid with optional identity inclusion.
     * Usage: new_with_id --alg_file file.ua --include_id true
     */
    private void handleNewWithId(Map<String, String> options) throws Exception {
        String algFile = getRequiredArg(options, "alg_file");
        boolean includeId = getBoolArg(options, "include_id", false);
        
        generatingAlgebra = AlgebraIO.readAlgebraFile(algFile);
        monoid = new UnaryTermsMonoid(generatingAlgebra, includeId);
        
        Map<String, Object> result = new HashMap<>();
        result.put("name", monoid.getName());
        result.put("cardinality", monoid.cardinality());
        result.put("algebra_type", monoid.algebraType().toString());
        result.put("include_id", includeId);
        
        handleSuccess(result);
    }
    
    /**
     * Get the algebra type.
     * Usage: algebra_type --alg_file file.ua
     */
    private void handleAlgebraType(Map<String, String> options) throws Exception {
        ensureMonoidCreated(options);
        
        AlgebraType type = monoid.algebraType();
        
        Map<String, Object> result = new HashMap<>();
        result.put("type", type.toString());
        
        handleSuccess(result);
    }
    
    /**
     * Get the cardinality of the monoid.
     * Usage: cardinality --alg_file file.ua
     */
    private void handleCardinality(Map<String, String> options) throws Exception {
        ensureMonoidCreated(options);
        
        int cardinality = monoid.cardinality();
        
        Map<String, Object> result = new HashMap<>();
        result.put("cardinality", cardinality);
        
        handleSuccess(result);
    }
    
    /**
     * Get the name of the monoid.
     * Usage: name --alg_file file.ua
     */
    private void handleName(Map<String, String> options) throws Exception {
        ensureMonoidCreated(options);
        
        String name = monoid.getName();
        
        Map<String, Object> result = new HashMap<>();
        result.put("name", name);
        
        handleSuccess(result);
    }
    
    /**
     * Set the name of the monoid.
     * Usage: set_name --alg_file file.ua --name "NewName"
     */
    private void handleSetName(Map<String, String> options) throws Exception {
        ensureMonoidCreated(options);
        
        String newName = getRequiredArg(options, "name");
        monoid.setName(newName);
        
        Map<String, Object> result = new HashMap<>();
        result.put("name", monoid.getName());
        
        handleSuccess(result);
    }
    
    /**
     * Check if the monoid is unary.
     * Usage: is_unary --alg_file file.ua
     */
    private void handleIsUnary(Map<String, String> options) throws Exception {
        ensureMonoidCreated(options);
        
        boolean isUnary = monoid.isUnary();
        
        Map<String, Object> result = new HashMap<>();
        result.put("is_unary", isUnary);
        
        handleSuccess(result);
    }
    
    /**
     * Check if the monoid is idempotent.
     * Usage: is_idempotent --alg_file file.ua
     */
    private void handleIsIdempotent(Map<String, String> options) throws Exception {
        ensureMonoidCreated(options);
        
        boolean isIdempotent = monoid.isIdempotent();
        
        Map<String, Object> result = new HashMap<>();
        result.put("is_idempotent", isIdempotent);
        
        handleSuccess(result);
    }
    
    /**
     * Check if the monoid is total.
     * Usage: is_total --alg_file file.ua
     */
    private void handleIsTotal(Map<String, String> options) throws Exception {
        ensureMonoidCreated(options);
        
        boolean isTotal = monoid.isTotal();
        
        Map<String, Object> result = new HashMap<>();
        result.put("is_total", isTotal);
        
        handleSuccess(result);
    }
    
    /**
     * Get the number of operations.
     * Usage: operations_count --alg_file file.ua
     */
    private void handleOperationsCount(Map<String, String> options) throws Exception {
        ensureMonoidCreated(options);
        
        int count = monoid.operations().size();
        
        Map<String, Object> result = new HashMap<>();
        result.put("operations_count", count);
        
        handleSuccess(result);
    }
    
    /**
     * Get the universe list.
     * Usage: get_universe_list --alg_file file.ua
     */
    private void handleGetUniverseList(Map<String, String> options) throws Exception {
        ensureMonoidCreated(options);
        
        List universeList = monoid.getUniverseList();
        int universeSize = universeList != null ? universeList.size() : 0;
        
        // Build universe array
        StringBuilder universeJson = new StringBuilder("[");
        if (universeList != null && !universeList.isEmpty()) {
            for (int i = 0; i < universeList.size(); i++) {
                if (i > 0) universeJson.append(",");
                universeJson.append("\"").append(universeList.get(i).toString()).append("\"");
            }
        }
        universeJson.append("]");
        
        Map<String, Object> result = new HashMap<>();
        result.put("universe_size", universeSize);
        result.put("universe", universeJson.toString());
        
        handleSuccess(result);
    }
    
    /**
     * Get an element by index.
     * Usage: get_element --alg_file file.ua --index 0
     */
    private void handleGetElement(Map<String, String> options) throws Exception {
        ensureMonoidCreated(options);
        
        int index = getIntArg(options, "index", 0);
        Object element = monoid.getElement(index);
        
        Map<String, Object> result = new HashMap<>();
        result.put("index", index);
        result.put("element", element != null ? element.toString() : null);
        result.put("has_element", element != null);
        
        handleSuccess(result);
    }
    
    /**
     * Get the index of an element.
     * Usage: element_index --alg_file file.ua --element_index 0
     * Note: This is a simplified version since we can't easily pass Term objects via CLI
     */
    private void handleElementIndex(Map<String, String> options) throws Exception {
        ensureMonoidCreated(options);
        
        // For CLI, we'll just test with the first element from universe list
        List universeList = monoid.getUniverseList();
        if (universeList == null || universeList.isEmpty()) {
            throw new RuntimeException("Universe list is empty");
        }
        
        Object firstElement = universeList.get(0);
        int index = monoid.elementIndex(firstElement);
        
        Map<String, Object> result = new HashMap<>();
        result.put("element", firstElement.toString());
        result.put("index", index);
        
        handleSuccess(result);
    }
    
    /**
     * Run basic functionality tests.
     * Usage: test --alg_file file.ua
     */
    private void handleTest(Map<String, String> options) throws Exception {
        String algFile = getRequiredArg(options, "alg_file");
        
        // Test 1: Create monoid
        generatingAlgebra = AlgebraIO.readAlgebraFile(algFile);
        monoid = new UnaryTermsMonoid(generatingAlgebra);
        
        // Test 2: Verify basic properties
        if (monoid.algebraType() != AlgebraType.UNARY_TERMS_MONOID) {
            throw new RuntimeException("Algebra type mismatch: expected UNARY_TERMS_MONOID, got " + monoid.algebraType());
        }
        
        // Test 3: Verify cardinality
        int cardinality = monoid.cardinality();
        if (cardinality < 0) {
            throw new RuntimeException("Invalid cardinality: " + cardinality);
        }
        
        // Test 4: Verify name
        String name = monoid.getName();
        if (name == null || name.isEmpty()) {
            throw new RuntimeException("Name is null or empty");
        }
        
        // Test 5: Verify operations count
        int opsCount = monoid.operations().size();
        if (opsCount != 1) {
            throw new RuntimeException("Expected 1 operation (product), got " + opsCount);
        }
        
        // Test 6: Verify universe list
        List universeList = monoid.getUniverseList();
        if (universeList == null) {
            throw new RuntimeException("Universe list is null");
        }
        if (universeList.size() != cardinality) {
            throw new RuntimeException("Universe list size mismatch: expected " + cardinality + ", got " + universeList.size());
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("name", name);
        result.put("cardinality", cardinality);
        result.put("algebra_type", monoid.algebraType().toString());
        result.put("operations_count", opsCount);
        result.put("universe_size", universeList.size());
        result.put("is_unary", monoid.isUnary());
        result.put("is_idempotent", monoid.isIdempotent());
        result.put("is_total", monoid.isTotal());
        
        handleSuccess(result);
    }
    
    /**
     * Helper method to ensure monoid is created, creating it if needed.
     */
    private void ensureMonoidCreated(Map<String, String> options) throws Exception {
        if (monoid == null) {
            String algFile = getOptionalArg(options, "alg_file", null);
            if (algFile == null) {
                // Try to create a default test algebra
                generatingAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
                monoid = new UnaryTermsMonoid(generatingAlgebra);
            } else {
                generatingAlgebra = AlgebraIO.readAlgebraFile(algFile);
                monoid = new UnaryTermsMonoid(generatingAlgebra);
            }
        }
    }
    
    /**
     * Show usage information for the UnaryTermsMonoid wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "new --alg_file resources/algebras/cyclic3.ua",
            "new_with_id --alg_file resources/algebras/cyclic3.ua --include_id true",
            "algebra_type --alg_file resources/algebras/cyclic3.ua",
            "cardinality --alg_file resources/algebras/cyclic3.ua",
            "name --alg_file resources/algebras/cyclic3.ua",
            "set_name --alg_file resources/algebras/cyclic3.ua --name \"NewName\"",
            "is_unary --alg_file resources/algebras/cyclic3.ua",
            "is_idempotent --alg_file resources/algebras/cyclic3.ua",
            "is_total --alg_file resources/algebras/cyclic3.ua",
            "operations_count --alg_file resources/algebras/cyclic3.ua",
            "get_universe_list --alg_file resources/algebras/cyclic3.ua",
            "get_element --alg_file resources/algebras/cyclic3.ua --index 0",
            "element_index --alg_file resources/algebras/cyclic3.ua",
            "test --alg_file resources/algebras/cyclic3.ua"
        };
        
        showUsage("UnaryTermsMonoid", 
                 "CLI wrapper for org.uacalc.alg.UnaryTermsMonoid operations", 
                 examples);
    }
}

