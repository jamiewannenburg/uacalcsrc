/* AbstractOperationWrapper.java - CLI wrapper for org.uacalc.alg.op testing via AbstractOperation implementation
 * 
 * This wrapper creates AbstractOperation instances for testing since Operation
 * is an interface that cannot be instantiated directly. It provides access to
 * all Operation interface methods through concrete implementations.
 */

package java_wrapper.src.alg.op;

import java.util.*;
import org.uacalc.alg.op.OperationSymbol;
import org.uacalc.alg.op.Operation;
import org.uacalc.alg.op.AbstractOperation;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for testing Operation interface functionality through AbstractOperation
 * concrete implementation. Provides command-line access to all Operation methods
 * for testing and validation purposes.
 */
public class AbstractOperationWrapper extends WrapperBase {
    
    /**
     * Main entry point for the AbstractOperation CLI wrapper.
     */
    public static void main(String[] args) {
        AbstractOperationWrapper wrapper = new AbstractOperationWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("AbstractOperation wrapper failed", e);
        }
    }
    
    /**
     * Run the AbstractOperation CLI wrapper with the given arguments.
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
                
            case "arity":
                handleArity(options);
                break;
                
            case "getSetSize":
                handleGetSetSize(options);
                break;
                
            case "symbol":
                handleSymbol(options);
                break;
                
            case "valueAt":
                handleValueAt(options);
                break;
                
            case "intValueAt":
                handleIntValueAt(options);
                break;
                
            case "makeTable":
                handleMakeTable(options);
                break;
                
            case "getTable":
                handleGetTable(options);
                break;
                
            case "getTableForce":
                handleGetTableForce(options);
                break;
                
            case "isTableBased":
                handleIsTableBased(options);
                break;
                
            case "isIdempotent":
                handleIsIdempotent(options);
                break;
                
            case "isAssociative":
                handleIsAssociative(options);
                break;
                
            case "isCommutative":
                handleIsCommutative(options);
                break;
                
            case "isTotallySymmetric":
                handleIsTotallySymmetric(options);
                break;
                
            case "isMaltsev":
                handleIsMaltsev(options);
                break;
                
            case "isTotal":
                handleIsTotal(options);
                break;
                
            case "compareTo":
                handleCompareTo(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Create a simple test operation based on type.
     */
    private Operation createTestOperation(String type, int setSize) throws Exception {
        switch (type) {
            case "binary":
                return new TestBinaryOperation("testBin", setSize);
            case "unary":
                return new TestUnaryOperation("testUn", setSize);
            case "nullary":
                return new TestNullaryOperation("testNull", setSize);
            default:
                throw new Exception("Unknown operation type: " + type);
        }
    }
    
    /**
     * Handle the arity command.
     */
    private void handleArity(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("arity", op.arity());
        data.put("type", type);
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the getSetSize command.
     */
    private void handleGetSetSize(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("setSize", op.getSetSize());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the symbol command.
     */
    private void handleSymbol(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        OperationSymbol sym = op.symbol();
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", sym.name());
        data.put("symbolArity", sym.arity());
        data.put("symbolAssociative", sym.isAssociative());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the valueAt command.
     */
    private void handleValueAt(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        String argsStr = getRequiredArg(options, "args");
        
        Operation op = createTestOperation(type, setSize);
        
        // Parse arguments
        List<Integer> args = new ArrayList<>();
        if (!argsStr.trim().isEmpty()) {
            String[] argParts = argsStr.split(",");
            for (String part : argParts) {
                args.add(Integer.parseInt(part.trim()));
            }
        }
        
        // Note: valueAt in Java takes List args and returns Object
        // For simplicity, we'll use intValueAt which is more specific
        int[] intArgs = args.stream().mapToInt(i -> i).toArray();
        int result = op.intValueAt(intArgs);
        
        Map<String, Object> data = new HashMap<>();
        data.put("result", result);
        data.put("args", args);
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the intValueAt command.
     */
    private void handleIntValueAt(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        String argsStr = getRequiredArg(options, "args");
        
        Operation op = createTestOperation(type, setSize);
        
        // Parse arguments
        int[] args;
        if (argsStr.trim().isEmpty()) {
            // Handle nullary operations (no arguments)
            args = new int[0];
        } else {
            String[] argParts = argsStr.split(",");
            args = new int[argParts.length];
            for (int i = 0; i < argParts.length; i++) {
                args[i] = Integer.parseInt(argParts[i].trim());
            }
        }
        
        int result = op.intValueAt(args);
        
        Map<String, Object> data = new HashMap<>();
        data.put("result", result);
        data.put("args", Arrays.toString(args));
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeTable command.
     */
    private void handleMakeTable(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        op.makeTable();
        
        Map<String, Object> data = new HashMap<>();
        data.put("status", "table_created");
        data.put("type", type);
        data.put("isTableBased", op.isTableBased());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the getTable command.
     */
    private void handleGetTable(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        op.makeTable(); // Ensure table exists
        
        int[] table = op.getTable();
        
        Map<String, Object> data = new HashMap<>();
        data.put("table", table != null ? Arrays.asList(Arrays.stream(table).boxed().toArray(Integer[]::new)) : null);
        data.put("hasTable", table != null);
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the getTableForce command.
     */
    private void handleGetTableForce(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        boolean makeTable = getBoolArg(options, "makeTable", true);
        
        Operation op = createTestOperation(type, setSize);
        int[] table = op.getTable(makeTable);
        
        Map<String, Object> data = new HashMap<>();
        data.put("table", table != null ? Arrays.asList(Arrays.stream(table).boxed().toArray(Integer[]::new)) : null);
        data.put("makeTable", makeTable);
        data.put("hasTable", table != null);
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isTableBased command.
     */
    private void handleIsTableBased(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isTableBased", op.isTableBased());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isIdempotent command.
     */
    private void handleIsIdempotent(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isIdempotent", op.isIdempotent());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isAssociative command.
     */
    private void handleIsAssociative(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isAssociative", op.isAssociative());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isCommutative command.
     */
    private void handleIsCommutative(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isCommutative", op.isCommutative());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isTotallySymmetric command.
     */
    private void handleIsTotallySymmetric(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isTotallySymmetric", op.isTotallySymmetric());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isMaltsev command.
     */
    private void handleIsMaltsev(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isMaltsev", op.isMaltsev());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isTotal command.
     */
    private void handleIsTotal(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isTotal", op.isTotal());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the compareTo command.
     */
    private void handleCompareTo(Map<String, String> options) throws Exception {
        String type1 = getRequiredArg(options, "type1");
        String type2 = getRequiredArg(options, "type2");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op1 = createTestOperation(type1, setSize);
        Operation op2 = createTestOperation(type2, setSize);
        
        int comparison = op1.compareTo(op2);
        
        Map<String, Object> data = new HashMap<>();
        data.put("comparison", comparison);
        data.put("type1", type1);
        data.put("type2", type2);
        data.put("op1_arity", op1.arity());
        data.put("op2_arity", op2.arity());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the test command.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        Map<String, Object> data = new HashMap<>();
        
        // Test binary operation
        Operation binOp = createTestOperation("binary", 3);
        data.put("binary_arity", binOp.arity());
        data.put("binary_setSize", binOp.getSetSize());
        data.put("binary_result_0_1", binOp.intValueAt(new int[]{0, 1}));
        data.put("binary_isIdempotent", binOp.isIdempotent());
        data.put("binary_isAssociative", binOp.isAssociative());
        
        // Test unary operation
        Operation unOp = createTestOperation("unary", 3);
        data.put("unary_arity", unOp.arity());
        data.put("unary_result_1", unOp.intValueAt(new int[]{1}));
        
        // Test nullary operation  
        Operation nullOp = createTestOperation("nullary", 3);
        data.put("nullary_arity", nullOp.arity());
        data.put("nullary_result", nullOp.intValueAt(new int[]{}));
        
        handleSuccess(data);
    }
    
    /**
     * Show usage information.
     */
    private void showUsage() {
        String[] examples = {
            "arity --type binary --setSize 3",
            "getSetSize --type unary --setSize 4",
            "symbol --type binary",
            "valueAt --type binary --args \"0,1\" --setSize 3",
            "intValueAt --type unary --args \"2\" --setSize 3",
            "makeTable --type binary --setSize 2",
            "getTable --type binary --setSize 2",
            "getTableForce --type binary --setSize 2 --makeTable true",
            "isTableBased --type binary --setSize 3",
            "isIdempotent --type binary --setSize 3",
            "isAssociative --type binary --setSize 3",
            "isCommutative --type binary --setSize 3",
            "isTotallySymmetric --type binary --setSize 3",
            "isMaltsev --type binary --setSize 3",
            "isTotal --type binary --setSize 3",
            "compareTo --type1 binary --type2 unary --setSize 3",
            "test"
        };
        
        showUsage("AbstractOperation", 
                 "CLI wrapper for Operation interface testing via AbstractOperation", 
                 examples);
    }
}

/**
 * Simple test binary operation: (a + b) % setSize
 */
class TestBinaryOperation extends AbstractOperation {
    private boolean tableCreated = false;
    private int[] table = null;
    
    public TestBinaryOperation(String name, int setSize) {
        super(new OperationSymbol(name, 2), setSize);
    }
    
    @Override
    public int intValueAt(int[] args) {
        if (args.length != 2) {
            throw new IllegalArgumentException("Binary operation requires 2 arguments");
        }
        return (args[0] + args[1]) % getSetSize();
    }
    
    @Override
    public Object valueAt(List args) {
        if (args.size() != 2) {
            throw new IllegalArgumentException("Binary operation requires 2 arguments");
        }
        int arg0 = ((Integer) args.get(0)).intValue();
        int arg1 = ((Integer) args.get(1)).intValue();
        return Integer.valueOf((arg0 + arg1) % getSetSize());
    }
    
    @Override
    public void makeTable() {
        super.makeTable();
        tableCreated = true;
        
        // Create the table: for binary operation with set size n, table size is n^2
        int size = getSetSize();
        table = new int[size * size];
        int index = 0;
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                table[index++] = intValueAt(new int[]{i, j});
            }
        }
    }
    
    @Override
    public boolean isTableBased() {
        return tableCreated;
    }
    
    @Override
    public int[] getTable() {
        return table;
    }
}

/**
 * Simple test unary operation: (a + 1) % setSize
 */
class TestUnaryOperation extends AbstractOperation {
    private boolean tableCreated = false;
    private int[] table = null;
    
    public TestUnaryOperation(String name, int setSize) {
        super(new OperationSymbol(name, 1), setSize);
    }
    
    @Override
    public int intValueAt(int[] args) {
        if (args.length != 1) {
            throw new IllegalArgumentException("Unary operation requires 1 argument");
        }
        return (args[0] + 1) % getSetSize();
    }
    
    @Override
    public Object valueAt(List args) {
        if (args.size() != 1) {
            throw new IllegalArgumentException("Unary operation requires 1 argument");
        }
        int arg0 = ((Integer) args.get(0)).intValue();
        return Integer.valueOf((arg0 + 1) % getSetSize());
    }
    
    @Override
    public void makeTable() {
        super.makeTable();
        tableCreated = true;
        
        // Create the table: for unary operation with set size n, table size is n
        int size = getSetSize();
        table = new int[size];
        for (int i = 0; i < size; i++) {
            table[i] = intValueAt(new int[]{i});
        }
    }
    
    @Override
    public boolean isTableBased() {
        return tableCreated;
    }
    
    @Override
    public int[] getTable() {
        return table;
    }
}

/**
 * Simple test nullary operation: returns 0
 */
class TestNullaryOperation extends AbstractOperation {
    private boolean tableCreated = false;
    private int[] table = null;
    
    public TestNullaryOperation(String name, int setSize) {
        super(new OperationSymbol(name, 0), setSize);
    }
    
    @Override
    public int intValueAt(int[] args) {
        if (args.length != 0) {
            throw new IllegalArgumentException("Nullary operation requires 0 arguments");
        }
        return 0;
    }
    
    @Override
    public Object valueAt(List args) {
        if (args.size() != 0) {
            throw new IllegalArgumentException("Nullary operation requires 0 arguments");
        }
        return Integer.valueOf(0);
    }
    
    @Override
    public void makeTable() {
        super.makeTable();
        tableCreated = true;
        
        // Create the table: for nullary operation, table size is 1
        table = new int[]{intValueAt(new int[]{})};
    }
    
    @Override
    public boolean isTableBased() {
        return tableCreated;
    }
    
    @Override
    public int[] getTable() {
        return table;
    }
}
