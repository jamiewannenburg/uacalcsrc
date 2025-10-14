/* IntOperationWrapper.java - CLI wrapper for table-based Operation testing
 * 
 * This wrapper creates table-based Operation instances for testing the Operation
 * interface with precomputed tables. It provides access to all Operation methods
 * through table-based concrete implementations.
 */

package java_wrapper.src.alg.op;

import java.util.*;
import org.uacalc.alg.op.OperationSymbol;
import org.uacalc.alg.op.Operation;
import org.uacalc.alg.op.Operations;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for testing Operation interface functionality through table-based
 * concrete implementations. Uses Operations.makeIntOperation for creating
 * table-based operations.
 */
public class IntOperationWrapper extends WrapperBase {
    
    /**
     * Main entry point for the IntOperation CLI wrapper.
     */
    public static void main(String[] args) {
        IntOperationWrapper wrapper = new IntOperationWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("IntOperation wrapper failed", e);
        }
    }
    
    /**
     * Run the IntOperation CLI wrapper with the given arguments.
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
                
            case "create":
                handleCreate(options);
                break;
                
            case "xor":
                handleXor(options);
                break;
                
            case "and":
                handleAnd(options);
                break;
                
            case "or":
                handleOr(options);
                break;
                
            case "arity":
                handleArity(options);
                break;
                
            case "getSetSize":
                handleGetSetSize(options);
                break;
                
            case "intValueAt":
                handleIntValueAt(options);
                break;
                
            case "intValueAtHorner":
                handleIntValueAtHorner(options);
                break;
                
            case "getTable":
                handleGetTable(options);
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
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Create a binary XOR operation.
     */
    private Operation createXorOperation() {
        OperationSymbol sym = new OperationSymbol("xor", 2);
        int[] table = {0, 1, 1, 0}; // XOR truth table
        return Operations.makeIntOperation(sym, 2, table);
    }
    
    /**
     * Create a binary AND operation.
     */
    private Operation createAndOperation() {
        OperationSymbol sym = new OperationSymbol("and", 2);
        int[] table = {0, 0, 0, 1}; // AND truth table
        return Operations.makeIntOperation(sym, 2, table);
    }
    
    /**
     * Create a binary OR operation.
     */
    private Operation createOrOperation() {
        OperationSymbol sym = new OperationSymbol("or", 2);
        int[] table = {0, 1, 1, 1}; // OR truth table
        return Operations.makeIntOperation(sym, 2, table);
    }
    
    /**
     * Create an operation from a table string.
     */
    private Operation createOperationFromTable(String name, int arity, int setSize, String tableStr) {
        OperationSymbol sym = new OperationSymbol(name, arity);
        
        // Parse table string
        String[] parts = tableStr.split(",");
        int[] table = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            table[i] = Integer.parseInt(parts[i].trim());
        }
        
        return Operations.makeIntOperation(sym, setSize, table);
    }
    
    /**
     * Handle the create command.
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int setSize = getIntArg(options, "setSize", 2);
        String tableStr = getRequiredArg(options, "table");
        
        Operation op = createOperationFromTable(name, arity, setSize, tableStr);
        
        Map<String, Object> data = new HashMap<>();
        data.put("name", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("isTableBased", op.isTableBased());
        data.put("table", Arrays.asList(Arrays.stream(op.getTable()).boxed().toArray(Integer[]::new)));
        
        handleSuccess(data);
    }
    
    /**
     * Handle the xor command.
     */
    private void handleXor(Map<String, String> options) throws Exception {
        Operation op = createXorOperation();
        
        Map<String, Object> data = new HashMap<>();
        data.put("name", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("table", Arrays.asList(Arrays.stream(op.getTable()).boxed().toArray(Integer[]::new)));
        data.put("result_0_0", op.intValueAt(new int[]{0, 0}));
        data.put("result_0_1", op.intValueAt(new int[]{0, 1}));
        data.put("result_1_0", op.intValueAt(new int[]{1, 0}));
        data.put("result_1_1", op.intValueAt(new int[]{1, 1}));
        
        handleSuccess(data);
    }
    
    /**
     * Handle the and command.
     */
    private void handleAnd(Map<String, String> options) throws Exception {
        Operation op = createAndOperation();
        
        Map<String, Object> data = new HashMap<>();
        data.put("name", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("table", Arrays.asList(Arrays.stream(op.getTable()).boxed().toArray(Integer[]::new)));
        data.put("result_0_0", op.intValueAt(new int[]{0, 0}));
        data.put("result_0_1", op.intValueAt(new int[]{0, 1}));
        data.put("result_1_0", op.intValueAt(new int[]{1, 0}));
        data.put("result_1_1", op.intValueAt(new int[]{1, 1}));
        
        handleSuccess(data);
    }
    
    /**
     * Handle the or command.
     */
    private void handleOr(Map<String, String> options) throws Exception {
        Operation op = createOrOperation();
        
        Map<String, Object> data = new HashMap<>();
        data.put("name", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("table", Arrays.asList(Arrays.stream(op.getTable()).boxed().toArray(Integer[]::new)));
        data.put("result_0_0", op.intValueAt(new int[]{0, 0}));
        data.put("result_0_1", op.intValueAt(new int[]{0, 1}));
        data.put("result_1_0", op.intValueAt(new int[]{1, 0}));
        data.put("result_1_1", op.intValueAt(new int[]{1, 1}));
        
        handleSuccess(data);
    }
    
    /**
     * Handle the arity command.
     */
    private void handleArity(Map<String, String> options) throws Exception {
        String type = getOptionalArg(options, "type", "xor");
        
        Operation op;
        switch (type) {
            case "xor":
                op = createXorOperation();
                break;
            case "and":
                op = createAndOperation();
                break;
            case "or":
                op = createOrOperation();
                break;
            default:
                throw new Exception("Unknown type: " + type);
        }
        
        Map<String, Object> data = new HashMap<>();
        data.put("arity", op.arity());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the getSetSize command.
     */
    private void handleGetSetSize(Map<String, String> options) throws Exception {
        String type = getOptionalArg(options, "type", "xor");
        
        Operation op;
        switch (type) {
            case "xor":
                op = createXorOperation();
                break;
            case "and":
                op = createAndOperation();
                break;
            case "or":
                op = createOrOperation();
                break;
            default:
                throw new Exception("Unknown type: " + type);
        }
        
        Map<String, Object> data = new HashMap<>();
        data.put("setSize", op.getSetSize());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the intValueAt command.
     */
    private void handleIntValueAt(Map<String, String> options) throws Exception {
        String type = getOptionalArg(options, "type", "xor");
        String argsStr = getRequiredArg(options, "args");
        
        Operation op;
        switch (type) {
            case "xor":
                op = createXorOperation();
                break;
            case "and":
                op = createAndOperation();
                break;
            case "or":
                op = createOrOperation();
                break;
            default:
                throw new Exception("Unknown type: " + type);
        }
        
        // Parse arguments
        String[] argParts = argsStr.split(",");
        int[] args = new int[argParts.length];
        for (int i = 0; i < argParts.length; i++) {
            args[i] = Integer.parseInt(argParts[i].trim());
        }
        
        int result = op.intValueAt(args);
        
        Map<String, Object> data = new HashMap<>();
        data.put("result", result);
        data.put("args", Arrays.toString(args));
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the intValueAtHorner command.
     */
    private void handleIntValueAtHorner(Map<String, String> options) throws Exception {
        String type = getOptionalArg(options, "type", "xor");
        int hornerIndex = getIntArg(options, "index", 0);
        
        Operation op;
        switch (type) {
            case "xor":
                op = createXorOperation();
                break;
            case "and":
                op = createAndOperation();
                break;
            case "or":
                op = createOrOperation();
                break;
            default:
                throw new Exception("Unknown type: " + type);
        }
        
        int result = op.intValueAt(hornerIndex);
        
        Map<String, Object> data = new HashMap<>();
        data.put("result", result);
        data.put("index", hornerIndex);
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the getTable command.
     */
    private void handleGetTable(Map<String, String> options) throws Exception {
        String type = getOptionalArg(options, "type", "xor");
        
        Operation op;
        switch (type) {
            case "xor":
                op = createXorOperation();
                break;
            case "and":
                op = createAndOperation();
                break;
            case "or":
                op = createOrOperation();
                break;
            default:
                throw new Exception("Unknown type: " + type);
        }
        
        int[] table = op.getTable();
        
        Map<String, Object> data = new HashMap<>();
        data.put("table", Arrays.asList(Arrays.stream(table).boxed().toArray(Integer[]::new)));
        data.put("tableSize", table.length);
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isTableBased command.
     */
    private void handleIsTableBased(Map<String, String> options) throws Exception {
        String type = getOptionalArg(options, "type", "xor");
        
        Operation op;
        switch (type) {
            case "xor":
                op = createXorOperation();
                break;
            case "and":
                op = createAndOperation();
                break;
            case "or":
                op = createOrOperation();
                break;
            default:
                throw new Exception("Unknown type: " + type);
        }
        
        Map<String, Object> data = new HashMap<>();
        data.put("isTableBased", op.isTableBased());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isIdempotent command.
     */
    private void handleIsIdempotent(Map<String, String> options) throws Exception {
        String type = getOptionalArg(options, "type", "xor");
        
        Operation op;
        switch (type) {
            case "xor":
                op = createXorOperation();
                break;
            case "and":
                op = createAndOperation();
                break;
            case "or":
                op = createOrOperation();
                break;
            default:
                throw new Exception("Unknown type: " + type);
        }
        
        Map<String, Object> data = new HashMap<>();
        data.put("isIdempotent", op.isIdempotent());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isAssociative command.
     */
    private void handleIsAssociative(Map<String, String> options) throws Exception {
        String type = getOptionalArg(options, "type", "xor");
        
        Operation op;
        switch (type) {
            case "xor":
                op = createXorOperation();
                break;
            case "and":
                op = createAndOperation();
                break;
            case "or":
                op = createOrOperation();
                break;
            default:
                throw new Exception("Unknown type: " + type);
        }
        
        Map<String, Object> data = new HashMap<>();
        data.put("isAssociative", op.isAssociative());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isCommutative command.
     */
    private void handleIsCommutative(Map<String, String> options) throws Exception {
        String type = getOptionalArg(options, "type", "xor");
        
        Operation op;
        switch (type) {
            case "xor":
                op = createXorOperation();
                break;
            case "and":
                op = createAndOperation();
                break;
            case "or":
                op = createOrOperation();
                break;
            default:
                throw new Exception("Unknown type: " + type);
        }
        
        Map<String, Object> data = new HashMap<>();
        data.put("isCommutative", op.isCommutative());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the test command.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        Map<String, Object> data = new HashMap<>();
        
        // Test XOR operation
        Operation xorOp = createXorOperation();
        data.put("xor_arity", xorOp.arity());
        data.put("xor_setSize", xorOp.getSetSize());
        data.put("xor_isTableBased", xorOp.isTableBased());
        data.put("xor_result_0_1", xorOp.intValueAt(new int[]{0, 1}));
        data.put("xor_result_1_1", xorOp.intValueAt(new int[]{1, 1}));
        data.put("xor_isIdempotent", xorOp.isIdempotent());
        data.put("xor_isCommutative", xorOp.isCommutative());
        
        // Test AND operation
        Operation andOp = createAndOperation();
        data.put("and_result_0_0", andOp.intValueAt(new int[]{0, 0}));
        data.put("and_result_1_1", andOp.intValueAt(new int[]{1, 1}));
        data.put("and_isIdempotent", andOp.isIdempotent());
        data.put("and_isCommutative", andOp.isCommutative());
        
        // Test OR operation
        Operation orOp = createOrOperation();
        data.put("or_result_0_1", orOp.intValueAt(new int[]{0, 1}));
        data.put("or_result_0_0", orOp.intValueAt(new int[]{0, 0}));
        data.put("or_isIdempotent", orOp.isIdempotent());
        data.put("or_isCommutative", orOp.isCommutative());
        
        handleSuccess(data);
    }
    
    /**
     * Show usage information.
     */
    private void showUsage() {
        String[] examples = {
            "create --name \"f\" --arity 2 --setSize 2 --table \"0,1,1,0\"",
            "xor",
            "and", 
            "or",
            "arity --type xor",
            "getSetSize --type and",
            "intValueAt --type xor --args \"0,1\"",
            "intValueAtHorner --type xor --index 1",
            "getTable --type and",
            "isTableBased --type or",
            "isIdempotent --type and",
            "isAssociative --type xor",
            "isCommutative --type or",
            "test"
        };
        
        showUsage("IntOperation", 
                 "CLI wrapper for table-based Operation interface testing", 
                 examples);
    }
}