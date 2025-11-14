/* SingleCloseWrapper.java - CLI wrapper for org.uacalc.alg.parallel.SingleClose
 * 
 * This wrapper exposes all public methods of the SingleClose class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg.parallel;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import org.uacalc.alg.parallel.SingleClose;
import org.uacalc.util.IntArray;
import org.uacalc.alg.op.*;
import org.uacalc.terms.*;
import org.uacalc.alg.*;
import org.uacalc.ui.tm.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the SingleClose class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class SingleCloseWrapper extends WrapperBase {
    
    /**
     * Main entry point for the SingleClose CLI wrapper.
     */
    public static void main(String[] args) {
        SingleCloseWrapper wrapper = new SingleCloseWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("SingleClose wrapper failed", e);
        }
    }
    
    /**
     * Run the SingleClose CLI wrapper with the given arguments.
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
                
            case "compute_size":
                handleComputeSize(options);
                break;
                
            case "get_increment":
                handleGetIncrement(options);
                break;
                
            case "get_computation_size":
                handleGetComputationSize(options);
                break;
                
            case "is_too_small":
                handleIsTooSmall(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    private void handleNew(Map<String, String> options) throws Exception {
        // Create a simple 2-element universe
        List<IntArray> univList = new ArrayList<>();
        univList.add(new IntArray(new int[]{0}));
        univList.add(new IntArray(new int[]{1}));
        
        // Create concurrent map
        ConcurrentMap<IntArray, Term> map = new ConcurrentHashMap<>();
        map.put(univList.get(0), new VariableImp("x"));
        map.put(univList.get(1), new VariableImp("y"));
        
        // Create a simple binary operation (XOR)
        OperationSymbol opSym = new OperationSymbol("f", 2, false);
        int[] table = new int[]{0, 1, 1, 0}; // XOR table for 2-element set
        Operation op = Operations.makeIntOperation(opSym, 2, table);
        
        int min = getIntArg(options, "min", 0);
        int max = getIntArg(options, "max", 1);
        AtomicInteger eltsFound = new AtomicInteger(0);
        
        SingleClose singleClose = new SingleClose(univList, map, op, min, max, eltsFound);
        
        Map<String, Object> result = new HashMap<>();
        result.put("status", "created");
        result.put("increment", getFieldInt(singleClose, "increment"));
        result.put("computation_size", getFieldLong(singleClose, "computationSize"));
        result.put("too_small", getFieldBoolean(singleClose, "tooSmall"));
        handleSuccess(result);
    }
    
    private SingleClose createTestSingleClose(int min, int max) {
        List<IntArray> univList = new ArrayList<>();
        univList.add(new IntArray(new int[]{0}));
        univList.add(new IntArray(new int[]{1}));
        
        ConcurrentMap<IntArray, Term> map = new ConcurrentHashMap<>();
        map.put(univList.get(0), new VariableImp("x"));
        map.put(univList.get(1), new VariableImp("y"));
        
        OperationSymbol opSym = new OperationSymbol("f", 2, false);
        int[] table = new int[]{0, 1, 1, 0};
        Operation op = Operations.makeIntOperation(opSym, 2, table);
        
        AtomicInteger eltsFound = new AtomicInteger(0);
        return new SingleClose(univList, map, op, min, max, eltsFound);
    }
    
    private int getFieldInt(SingleClose sc, String fieldName) throws Exception {
        java.lang.reflect.Field field = SingleClose.class.getDeclaredField(fieldName);
        field.setAccessible(true);
        return field.getInt(sc);
    }
    
    private long getFieldLong(SingleClose sc, String fieldName) throws Exception {
        java.lang.reflect.Field field = SingleClose.class.getDeclaredField(fieldName);
        field.setAccessible(true);
        return field.getLong(sc);
    }
    
    private boolean getFieldBoolean(SingleClose sc, String fieldName) throws Exception {
        java.lang.reflect.Field field = SingleClose.class.getDeclaredField(fieldName);
        field.setAccessible(true);
        return field.getBoolean(sc);
    }
    
    private void handleComputeSize(Map<String, String> options) throws Exception {
        int min = getIntArg(options, "min", 0);
        int max = getIntArg(options, "max", 1);
        SingleClose singleClose = createTestSingleClose(min, max);
        
        Map<String, Object> result = new HashMap<>();
        result.put("computation_size", getFieldLong(singleClose, "computationSize"));
        handleSuccess(result);
    }
    
    private void handleGetIncrement(Map<String, String> options) throws Exception {
        SingleClose singleClose = createTestSingleClose(0, 1);
        
        Map<String, Object> result = new HashMap<>();
        result.put("increment", getFieldInt(singleClose, "increment"));
        handleSuccess(result);
    }
    
    private void handleGetComputationSize(Map<String, String> options) throws Exception {
        SingleClose singleClose = createTestSingleClose(0, 1);
        
        Map<String, Object> result = new HashMap<>();
        result.put("computation_size", getFieldLong(singleClose, "computationSize"));
        handleSuccess(result);
    }
    
    private void handleIsTooSmall(Map<String, String> options) throws Exception {
        SingleClose singleClose = createTestSingleClose(0, 1);
        
        Map<String, Object> result = new HashMap<>();
        result.put("too_small", getFieldBoolean(singleClose, "tooSmall"));
        handleSuccess(result);
    }
    
    private void handleTest(Map<String, String> options) throws Exception {
        SingleClose singleClose = createTestSingleClose(0, 1);
        
        Map<String, Object> result = new HashMap<>();
        result.put("status", "test_passed");
        result.put("increment", getFieldInt(singleClose, "increment"));
        result.put("computation_size", getFieldLong(singleClose, "computationSize"));
        result.put("too_small", getFieldBoolean(singleClose, "tooSmall"));
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the SingleClose wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "new --min 0 --max 1",
            "get_increment",
            "get_computation_size",
            "is_too_small",
            "compute_size --min 0 --max 1",
            "test"
        };
        
        showUsage("SingleCloseWrapper", 
                 "CLI wrapper for org.uacalc.alg.parallel.SingleClose operations", 
                 examples);
    }
}

