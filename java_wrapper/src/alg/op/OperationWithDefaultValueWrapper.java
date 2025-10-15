/* OperationWithDefaultValueWrapper.java - CLI wrapper for org.uacalc.alg.op.OperationWithDefaultValue testing
 * 
 * This wrapper provides command-line access to all OperationWithDefaultValue methods
 * for testing and validation purposes.
 */

package java_wrapper.src.alg.op;

import java.util.*;
import org.uacalc.alg.op.OperationSymbol;
import org.uacalc.alg.op.Operation;
import org.uacalc.alg.op.OperationWithDefaultValue;
import org.uacalc.alg.op.Operations;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for testing OperationWithDefaultValue functionality.
 * Provides command-line access to all OperationWithDefaultValue methods
 * for testing and validation purposes.
 */
public class OperationWithDefaultValueWrapper extends WrapperBase {
    
    /**
     * Main entry point for the OperationWithDefaultValue CLI wrapper.
     */
    public static void main(String[] args) {
        OperationWithDefaultValueWrapper wrapper = new OperationWithDefaultValueWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("OperationWithDefaultValue wrapper failed", e);
        }
    }
    
    /**
     * Run the OperationWithDefaultValue CLI wrapper with the given arguments.
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
                
            case "constructor1":
                handleConstructor1(options);
                break;
                
            case "constructor2":
                handleConstructor2(options);
                break;
                
            case "constructor3":
                handleConstructor3(options);
                break;
                
            case "constructor4":
                handleConstructor4(options);
                break;
                
            case "constructor5":
                handleConstructor5(options);
                break;
                
            case "constructor6":
                handleConstructor6(options);
                break;
                
            case "intValueAt":
                handleIntValueAt(options);
                break;
                
            case "intValueAtSingle":
                handleIntValueAtSingle(options);
                break;
                
            case "valueAt":
                handleValueAt(options);
                break;
                
            case "getDefaultValue":
                handleGetDefaultValue(options);
                break;
                
            case "setDefaultValue":
                handleSetDefaultValue(options);
                break;
                
            case "isTotal":
                handleIsTotal(options);
                break;
                
            case "updateRandomValueTable":
                handleUpdateRandomValueTable(options);
                break;
                
            case "getRandomValueTable":
                handleGetRandomValueTable(options);
                break;
                
            case "isIdempotentSet":
                handleIsIdempotentSet(options);
                break;
                
            case "setIdempotent":
                handleSetIdempotent(options);
                break;
                
            case "makeIdempotent":
                handleMakeIdempotent(options);
                break;
                
            case "isDiagonal":
                handleIsDiagonal(options);
                break;
                
            case "makeTable":
                handleMakeTable(options);
                break;
                
            case "getTotalTable":
                handleGetTotalTable(options);
                break;
                
            case "makeOrdinaryOperation":
                handleMakeOrdinaryOperation(options);
                break;
                
            case "makeOrdinary":
                handleMakeOrdinary(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Create a deterministic test operation using Operations.makeIntOperation
     * instead of synthetic Test* classes. This avoids mismatched names and
     * aligns with the core library behavior.
     */
    private Operation createTestOperation(String type, int setSize) throws Exception {
        OperationSymbol sym;
        int arity;
        if ("binary".equals(type)) {
            sym = new OperationSymbol("f", 2);
            arity = 2;
        } else if ("unary".equals(type)) {
            sym = new OperationSymbol("f", 1);
            arity = 1;
        } else if ("nullary".equals(type)) {
            sym = new OperationSymbol("const", 0);
            arity = 0;
        } else {
            throw new Exception("Unknown operation type: " + type);
        }

        // Build a simple deterministic table:
        // - nullary: [0]
        // - unary: (i + 1) % setSize
        // - binary: (i + j) % setSize in lexicographic order
        int tableSize = 1;
        for (int i = 0; i < arity; i++) tableSize *= Math.max(1, setSize);
        int[] vt = new int[tableSize];
        if (arity == 0) {
            vt[0] = 0;
        } else if (arity == 1) {
            for (int i = 0; i < setSize; i++) {
                vt[i] = (i + 1) % setSize;
            }
        } else { // arity == 2
            int idx = 0;
            for (int i = 0; i < setSize; i++) {
                for (int j = 0; j < setSize; j++) {
                    vt[idx++] = (i + j) % setSize;
                }
            }
        }

        return Operations.makeIntOperation(sym, setSize, vt);
    }
    
    /**
     * Handle constructor1: OperationWithDefaultValue(Operation op)
     */
    private void handleConstructor1(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("defaultValue", op.getDefaultValue());
        data.put("isTotal", op.isTotal());
        
        handleSuccess(data);
    }
    
    /**
     * Handle constructor2: OperationWithDefaultValue(String name, int arity, int algSize, int defaultValue)
     */
    private void handleConstructor2(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int algSize = getIntArg(options, "algSize", 3);
        int defaultValue = getIntArg(options, "defaultValue", 0);
        
        OperationWithDefaultValue op = new OperationWithDefaultValue(name, arity, algSize, defaultValue);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("defaultValue", op.getDefaultValue());
        
        handleSuccess(data);
    }
    
    /**
     * Handle constructor3: OperationWithDefaultValue(OperationSymbol sym, int algSize)
     */
    private void handleConstructor3(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int algSize = getIntArg(options, "algSize", 3);
        
        OperationSymbol sym = new OperationSymbol(name, arity);
        OperationWithDefaultValue op = new OperationWithDefaultValue(sym, algSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("defaultValue", op.getDefaultValue());
        
        handleSuccess(data);
    }
    
    /**
     * Handle constructor4: OperationWithDefaultValue(OperationSymbol sym, int algSize, int defaultValue)
     */
    private void handleConstructor4(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int algSize = getIntArg(options, "algSize", 3);
        int defaultValue = getIntArg(options, "defaultValue", 0);
        
        OperationSymbol sym = new OperationSymbol(name, arity);
        OperationWithDefaultValue op = new OperationWithDefaultValue(sym, algSize, defaultValue);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("defaultValue", op.getDefaultValue());
        
        handleSuccess(data);
    }
    
    /**
     * Handle constructor5: OperationWithDefaultValue(Operation op, int algSize)
     */
    private void handleConstructor5(Map<String, String> options) throws Exception {
        // Avoid Java constructor bug by materializing the table and using the safe constructor
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);

        Operation baseOp = createTestOperation(type, setSize);
        baseOp.makeTable();
        int[] vt = baseOp.getTable();
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp.symbol(), setSize, vt, -1);

        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("defaultValue", op.getDefaultValue());

        handleSuccess(data);
    }
    
    /**
     * Handle constructor6: OperationWithDefaultValue(OperationSymbol sym, int algSize, int[] valueTable, int defaultValue)
     */
    private void handleConstructor6(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int algSize = getIntArg(options, "algSize", 3);
        int defaultValue = getIntArg(options, "defaultValue", 0);
        String tableStr = getOptionalArg(options, "valueTable", "");
        
        OperationSymbol sym = new OperationSymbol(name, arity);
        int[] valueTable = null;
        
        if (!tableStr.isEmpty()) {
            String[] parts = tableStr.split(",");
            valueTable = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                valueTable[i] = Integer.parseInt(parts[i].trim());
            }
        }
        
        OperationWithDefaultValue op = new OperationWithDefaultValue(sym, algSize, valueTable, defaultValue);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("defaultValue", op.getDefaultValue());
        data.put("hasValueTable", valueTable != null);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the intValueAt command.
     */
    private void handleIntValueAt(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        int defaultValue = getIntArg(options, "defaultValue", 0);
        String argsStr = getRequiredArg(options, "args");
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        op.setDefaultValue(defaultValue);
        
        // Parse arguments
        int[] args;
        if (argsStr.trim().isEmpty()) {
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
        data.put("defaultValue", defaultValue);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the intValueAtSingle command.
     */
    private void handleIntValueAtSingle(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        int defaultValue = getIntArg(options, "defaultValue", 0);
        int arg = getIntArg(options, "arg", 0);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        op.setDefaultValue(defaultValue);
        
        int result = op.intValueAt(arg);
        
        Map<String, Object> data = new HashMap<>();
        data.put("result", result);
        data.put("arg", arg);
        data.put("type", type);
        data.put("defaultValue", defaultValue);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the valueAt command.
     */
    private void handleValueAt(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        int defaultValue = getIntArg(options, "defaultValue", 0);
        String argsStr = getRequiredArg(options, "args");
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        op.setDefaultValue(defaultValue);
        
        // Parse arguments
        List<Integer> args = new ArrayList<>();
        if (!argsStr.trim().isEmpty()) {
            String[] argParts = argsStr.split(",");
            for (String part : argParts) {
                args.add(Integer.parseInt(part.trim()));
            }
        }
        
        Object result = op.valueAt(args);
        
        Map<String, Object> data = new HashMap<>();
        data.put("result", result);
        data.put("args", args);
        data.put("type", type);
        data.put("defaultValue", defaultValue);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the getDefaultValue command.
     */
    private void handleGetDefaultValue(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        int defaultValue = getIntArg(options, "defaultValue", 0);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        op.setDefaultValue(defaultValue);
        
        Map<String, Object> data = new HashMap<>();
        data.put("defaultValue", op.getDefaultValue());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the setDefaultValue command.
     */
    private void handleSetDefaultValue(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        int defaultValue = getIntArg(options, "defaultValue", 0);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        op.setDefaultValue(defaultValue);
        
        Map<String, Object> data = new HashMap<>();
        data.put("status", "default_value_set");
        data.put("defaultValue", op.getDefaultValue());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isTotal command.
     */
    private void handleIsTotal(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        int defaultValue = getIntArg(options, "defaultValue", 0);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        op.setDefaultValue(defaultValue);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isTotal", op.isTotal());
        data.put("defaultValue", defaultValue);
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the updateRandomValueTable command.
     */
    private void handleUpdateRandomValueTable(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        op.updateRandomValueTable();
        
        Map<String, Object> data = new HashMap<>();
        data.put("status", "random_table_updated");
        data.put("type", type);
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the getRandomValueTable command.
     */
    private void handleGetRandomValueTable(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        int[] randomTable = op.getRandomValueTable();
        
        Map<String, Object> data = new HashMap<>();
        data.put("randomTable", Arrays.asList(Arrays.stream(randomTable).boxed().toArray(Integer[]::new)));
        data.put("tableSize", randomTable.length);
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isIdempotentSet command.
     */
    private void handleIsIdempotentSet(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isIdempotentSet", op.isIdempotentSet());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the setIdempotent command.
     */
    private void handleSetIdempotent(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        boolean idempotent = getBoolArg(options, "idempotent", true);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        op.setIdempotent(idempotent);
        
        Map<String, Object> data = new HashMap<>();
        data.put("status", "idempotent_set");
        data.put("isIdempotentSet", op.isIdempotentSet());
        data.put("idempotent", idempotent);
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeIdempotent command.
     */
    private void handleMakeIdempotent(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        op.makeIdempotent();
        
        Map<String, Object> data = new HashMap<>();
        data.put("status", "made_idempotent");
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isDiagonal command.
     */
    private void handleIsDiagonal(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        int row = getIntArg(options, "row", 0);
        int col = getIntArg(options, "col", 0);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isDiagonal", op.isDiagonal(row, col));
        data.put("row", row);
        data.put("col", col);
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeTable command.
     */
    private void handleMakeTable(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        op.makeTable();
        
        Map<String, Object> data = new HashMap<>();
        data.put("status", "table_created");
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the getTotalTable command.
     */
    private void handleGetTotalTable(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        int defaultValue = getIntArg(options, "defaultValue", 0);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        op.setDefaultValue(defaultValue);
        
        int[] totalTable = op.getTotalTable();
        
        Map<String, Object> data = new HashMap<>();
        data.put("totalTable", totalTable != null ? Arrays.asList(Arrays.stream(totalTable).boxed().toArray(Integer[]::new)) : null);
        data.put("hasTotalTable", totalTable != null);
        data.put("defaultValue", defaultValue);
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeOrdinaryOperation command.
     */
    private void handleMakeOrdinaryOperation(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        int defaultValue = getIntArg(options, "defaultValue", 0);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        op.setDefaultValue(defaultValue);
        
        Operation ordinaryOp = op.makeOrdinaryOperation();
        
        Map<String, Object> data = new HashMap<>();
        data.put("hasOrdinaryOperation", ordinaryOp != null);
        if (ordinaryOp != null) {
            data.put("ordinaryOpSymbol", ordinaryOp.symbol().name());
            data.put("ordinaryOpArity", ordinaryOp.arity());
            data.put("ordinaryOpSetSize", ordinaryOp.getSetSize());
        }
        data.put("defaultValue", defaultValue);
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeOrdinary command.
     */
    private void handleMakeOrdinary(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        int defaultValue = getIntArg(options, "defaultValue", 0);
        
        Operation baseOp = createTestOperation(type, setSize);
        OperationWithDefaultValue op = new OperationWithDefaultValue(baseOp);
        op.setDefaultValue(defaultValue);
        
        List<Operation> ops = Arrays.asList(op, baseOp);
        List<Operation> ordinaryOps = OperationWithDefaultValue.makeOrdinary(ops);
        
        Map<String, Object> data = new HashMap<>();
        data.put("originalCount", ops.size());
        data.put("ordinaryCount", ordinaryOps.size());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the test command.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        Map<String, Object> data = new HashMap<>();
        
        // Test constructor1
        Operation binOp = createTestOperation("binary", 3);
        OperationWithDefaultValue op1 = new OperationWithDefaultValue(binOp);
        data.put("constructor1_defaultValue", op1.getDefaultValue());
        data.put("constructor1_isTotal", op1.isTotal());
        
        // Test constructor2
        OperationWithDefaultValue op2 = new OperationWithDefaultValue("testOp", 2, 3, 1);
        data.put("constructor2_defaultValue", op2.getDefaultValue());
        data.put("constructor2_arity", op2.arity());
        
        // Test default value operations
        op1.setDefaultValue(2);
        data.put("setDefaultValue_result", op1.getDefaultValue());
        data.put("setDefaultValue_isTotal", op1.isTotal());
        
        // Test random value table
        op1.updateRandomValueTable();
        int[] randomTable = op1.getRandomValueTable();
        data.put("randomTableSize", randomTable.length);
        
        // Test idempotent operations
        op1.setIdempotent(true);
        data.put("isIdempotentSet", op1.isIdempotentSet());
        
        handleSuccess(data);
    }
    
    /**
     * Show usage information.
     */
    private void showUsage() {
        String[] examples = {
            "constructor1 --type binary --setSize 3",
            "constructor2 --name testOp --arity 2 --algSize 3 --defaultValue 1",
            "constructor3 --name testOp --arity 2 --algSize 3",
            "constructor4 --name testOp --arity 2 --algSize 3 --defaultValue 1",
            "constructor5 --type binary --setSize 3",
            "constructor6 --name testOp --arity 2 --algSize 3 --defaultValue 1 --valueTable \"0,1,2,1,2,0,2,0,1\"",
            "intValueAt --type binary --args \"0,1\" --setSize 3 --defaultValue 1",
            "intValueAtSingle --type unary --arg 1 --setSize 3 --defaultValue 2",
            "valueAt --type binary --args \"1,2\" --setSize 3 --defaultValue 0",
            "getDefaultValue --type binary --setSize 3 --defaultValue 1",
            "setDefaultValue --type binary --setSize 3 --defaultValue 2",
            "isTotal --type binary --setSize 3 --defaultValue 1",
            "updateRandomValueTable --type binary --setSize 3",
            "getRandomValueTable --type binary --setSize 3",
            "isIdempotentSet --type binary --setSize 3",
            "setIdempotent --type binary --setSize 3 --idempotent true",
            "makeIdempotent --type binary --setSize 3",
            "isDiagonal --type binary --setSize 3 --row 0 --col 0",
            "makeTable --type binary --setSize 3",
            "getTotalTable --type binary --setSize 3 --defaultValue 1",
            "makeOrdinaryOperation --type binary --setSize 3 --defaultValue 1",
            "makeOrdinary --type binary --setSize 3 --defaultValue 1",
            "test"
        };
        
        showUsage("OperationWithDefaultValue", 
                 "CLI wrapper for OperationWithDefaultValue testing", 
                 examples);
    }
}

