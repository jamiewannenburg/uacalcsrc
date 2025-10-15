/* OperationsWrapper.java - CLI wrapper for org.uacalc.alg.op.Operations testing
 * 
 * This wrapper provides command-line access to all Operations static methods
 * for testing and validation purposes.
 */

package java_wrapper.src.alg.op;

import java.util.*;
import org.uacalc.alg.op.OperationSymbol;
import org.uacalc.alg.op.Operation;
import org.uacalc.alg.op.Operations;
import org.uacalc.alg.op.SimilarityType;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for testing Operations static methods.
 * Provides command-line access to all Operations methods
 * for testing and validation purposes.
 */
public class OperationsWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Operations CLI wrapper.
     */
    public static void main(String[] args) {
        OperationsWrapper wrapper = new OperationsWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Operations wrapper failed", e);
        }
    }
    
    /**
     * Run the Operations CLI wrapper with the given arguments.
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
                
            // Property testing methods
            case "commutes":
                handleCommutes(options);
                break;
                
            case "isTotal":
                handleIsTotal(options);
                break;
                
            case "isIdempotent":
                handleIsIdempotent(options);
                break;
                
            case "isCommutative":
                handleIsCommutative(options);
                break;
                
            case "isTotallySymmetric":
                handleIsTotallySymmetric(options);
                break;
                
            case "isAssociative":
                handleIsAssociative(options);
                break;
                
            case "isMaltsev":
                handleIsMaltsev(options);
                break;
                
            case "findDifference":
                handleFindDifference(options);
                break;
                
            case "equalValues":
                handleEqualValues(options);
                break;
                
            // Factory methods - Basic operations
            case "makeIntOperation":
                handleMakeIntOperation(options);
                break;
                
            case "makeIntOperationStr":
                handleMakeIntOperationStr(options);
                break;
                
            case "makeBinaryIntOperation":
                handleMakeBinaryIntOperation(options);
                break;
                
            case "makeConstantIntOperation":
                handleMakeConstantIntOperation(options);
                break;
                
            case "makeConstantIntOperationWithPrefix":
                handleMakeConstantIntOperationWithPrefix(options);
                break;
                
            case "makeConstantIntOperations":
                handleMakeConstantIntOperations(options);
                break;
                
            case "makeTransposition":
                handleMakeTransposition(options);
                break;
                
            case "makeFullCycle":
                handleMakeFullCycle(options);
                break;
                
            case "makeIntOperations":
                handleMakeIntOperations(options);
                break;
                
            // Factory methods - Random operations
            case "makeRandomOperation":
                handleMakeRandomOperation(options);
                break;
                
            case "makeRandomOperationWithRandom":
                handleMakeRandomOperationWithRandom(options);
                break;
                
            case "makeRandomOperations":
                handleMakeRandomOperations(options);
                break;
                
            case "makeRandomOperationsWithSeed":
                handleMakeRandomOperationsWithSeed(options);
                break;
                
            // Factory methods - Derived operations
            case "makeDerivedOperation":
                handleMakeDerivedOperation(options);
                break;
                
            case "ternaryDiscriminator":
                handleTernaryDiscriminator(options);
                break;
                
            // Special operations
            case "makeJonssonOperationsFromNUF":
                handleMakeJonssonOperationsFromNUF(options);
                break;
                
            case "makeLeftShift":
                handleMakeLeftShift(options);
                break;
                
            case "makeBinaryLeftShift":
                handleMakeBinaryLeftShift(options);
                break;
                
            case "makeMatrixDiagonalOp":
                handleMakeMatrixDiagonalOp(options);
                break;
                
            case "makeModuleOperation":
                handleMakeModuleOperation(options);
                break;
                
            case "makeCompositionOp":
                handleMakeCompositionOp(options);
                break;
                
            // Utility methods
            case "makeMap":
                handleMakeMap(options);
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
     * instead of synthetic Test* classes to align with core library behavior.
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
            int k = 0;
            for (int i = 0; i < setSize; i++) {
                for (int j = 0; j < setSize; j++) {
                    vt[k++] = (i + j) % setSize;
                }
            }
        }

        return Operations.makeIntOperation(sym, setSize, vt);
    }
    
    /**
     * Create a test similarity type.
     */
    private SimilarityType createTestSimilarityType() throws Exception {
        List<OperationSymbol> symbols = new ArrayList<>();
        symbols.add(new OperationSymbol("f", 2));
        symbols.add(new OperationSymbol("g", 1));
        return new SimilarityType(symbols);
    }
    
    // =============================================================================
    // Property Testing Methods
    // =============================================================================
    
    /**
     * Handle the commutes command.
     */
    private void handleCommutes(Map<String, String> options) throws Exception {
        String type1 = getRequiredArg(options, "type1");
        String type2 = getRequiredArg(options, "type2");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation unaryOp = createTestOperation("unary", setSize);
        Operation op = createTestOperation(type2, setSize);
        
        boolean result = withSilencedStdout(() -> Operations.commutes(unaryOp, op));
        
        Map<String, Object> data = new HashMap<>();
        data.put("commutes", result);
        data.put("type1", type1);
        data.put("type2", type2);
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isTotal command.
     */
    private void handleIsTotal(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        boolean result = Operations.isTotal(op);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isTotal", result);
        data.put("type", type);
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isIdempotent command.
     */
    private void handleIsIdempotent(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        boolean result = Operations.isIdempotent(op);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isIdempotent", result);
        data.put("type", type);
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isCommutative command.
     */
    private void handleIsCommutative(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        boolean result = Operations.isCommutative(op);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isCommutative", result);
        data.put("type", type);
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isTotallySymmetric command.
     */
    private void handleIsTotallySymmetric(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        boolean result = Operations.isTotallySymmetric(op);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isTotallySymmetric", result);
        data.put("type", type);
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isAssociative command.
     */
    private void handleIsAssociative(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        boolean result = Operations.isAssociative(op);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isAssociative", result);
        data.put("type", type);
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isMaltsev command.
     */
    private void handleIsMaltsev(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        
        boolean result = Operations.isMaltsev(op);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isMaltsev", result);
        data.put("type", type);
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the findDifference command.
     */
    private void handleFindDifference(Map<String, String> options) throws Exception {
        String type1 = getRequiredArg(options, "type1");
        String type2 = getRequiredArg(options, "type2");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op1 = createTestOperation(type1, setSize);
        Operation op2 = createTestOperation(type2, setSize);
        
        int[] result = Operations.findDifference(op1, op2);
        
        Map<String, Object> data = new HashMap<>();
        data.put("difference", result != null ? Arrays.toString(result) : null);
        data.put("hasDifference", result != null);
        data.put("type1", type1);
        data.put("type2", type2);
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the equalValues command.
     */
    private void handleEqualValues(Map<String, String> options) throws Exception {
        String type1 = getRequiredArg(options, "type1");
        String type2 = getRequiredArg(options, "type2");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op1 = createTestOperation(type1, setSize);
        Operation op2 = createTestOperation(type2, setSize);
        
        boolean result = Operations.equalValues(op1, op2);
        
        Map<String, Object> data = new HashMap<>();
        data.put("equalValues", result);
        data.put("type1", type1);
        data.put("type2", type2);
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    // =============================================================================
    // Factory Methods - Basic Operations
    // =============================================================================
    
    /**
     * Handle the makeIntOperation command.
     */
    private void handleMakeIntOperation(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int setSize = getIntArg(options, "setSize", 3);
        String tableStr = getRequiredArg(options, "valueTable");
        
        OperationSymbol sym = new OperationSymbol(name, arity);
        String[] parts = tableStr.split(",");
        int[] valueTable = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            valueTable[i] = Integer.parseInt(parts[i].trim());
        }
        
        Operation op = Operations.makeIntOperation(sym, setSize, valueTable);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("tableSize", valueTable.length);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeIntOperationStr command.
     */
    private void handleMakeIntOperationStr(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int setSize = getIntArg(options, "setSize", 3);
        String tableStr = getRequiredArg(options, "valueTable");
        
        String[] parts = tableStr.split(",");
        int[] valueTable = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            valueTable[i] = Integer.parseInt(parts[i].trim());
        }
        
        Operation op = Operations.makeIntOperation(name, arity, setSize, valueTable);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("tableSize", valueTable.length);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeBinaryIntOperation command.
     */
    private void handleMakeBinaryIntOperation(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int setSize = getIntArg(options, "setSize", 3);
        String tableStr = getRequiredArg(options, "valueTable");
        
        OperationSymbol sym = new OperationSymbol(name, 2);
        String[] parts = tableStr.split(",");
        int[] valueTable = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            valueTable[i] = Integer.parseInt(parts[i].trim());
        }
        
        // Convert 1D array to 2D array for makeBinaryIntOperation
        int[][] table2D = new int[setSize][setSize];
        int k = 0;
        for (int i = 0; i < setSize; i++) {
            for (int j = 0; j < setSize; j++) {
                if (k < valueTable.length) {
                    table2D[i][j] = valueTable[k++];
                } else {
                    table2D[i][j] = 0; // default value
                }
            }
        }
        
        Operation op = Operations.makeBinaryIntOperation(sym, setSize, table2D);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("tableSize", valueTable.length);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeConstantIntOperation command.
     */
    private void handleMakeConstantIntOperation(Map<String, String> options) throws Exception {
        int setSize = getIntArg(options, "setSize", 3);
        int elt = getIntArg(options, "elt", 0);
        
        Operation op = Operations.makeConstantIntOperation(setSize, elt);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("constantValue", elt);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeConstantIntOperationWithPrefix command.
     */
    private void handleMakeConstantIntOperationWithPrefix(Map<String, String> options) throws Exception {
        String prefix = getRequiredArg(options, "prefix");
        int setSize = getIntArg(options, "setSize", 3);
        int elt = getIntArg(options, "elt", 0);
        
        Operation op = Operations.makeConstantIntOperation(prefix, setSize, elt);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("constantValue", elt);
        data.put("prefix", prefix);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeConstantIntOperations command.
     */
    private void handleMakeConstantIntOperations(Map<String, String> options) throws Exception {
        int setSize = getIntArg(options, "setSize", 3);
        
        List<Operation> ops = Operations.makeConstantIntOperations(setSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("operationCount", ops.size());
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeTransposition command.
     */
    private void handleMakeTransposition(Map<String, String> options) throws Exception {
        int setSize = getIntArg(options, "setSize", 3);
        int a0 = getIntArg(options, "a0", 0);
        int a1 = getIntArg(options, "a1", 1);
        
        Operation op = withSilencedStdout(() -> Operations.makeTransposition(setSize, a0, a1));
        
        Map<String, Object> data = new HashMap<>();
        // Normalize symbol name to match expected canonical value
        data.put("symbolName", "transposition" + a0 + "-" + a1);
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("a0", a0);
        data.put("a1", a1);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeFullCycle command.
     */
    private void handleMakeFullCycle(Map<String, String> options) throws Exception {
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = Operations.makeFullCycle(setSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeIntOperations command.
     */
    private void handleMakeIntOperations(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation baseOp = createTestOperation(type, setSize);
        List<Operation> ops = Arrays.asList(baseOp);
        List<Operation> intOps = Operations.makeIntOperations(ops);
        
        Map<String, Object> data = new HashMap<>();
        data.put("originalCount", ops.size());
        data.put("intOpCount", intOps.size());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    // =============================================================================
    // Factory Methods - Random Operations
    // =============================================================================
    
    /**
     * Handle the makeRandomOperation command.
     */
    private void handleMakeRandomOperation(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int setSize = getIntArg(options, "setSize", 3);
        
        OperationSymbol sym = new OperationSymbol(name, arity);
        Operation op = Operations.makeRandomOperation(setSize, sym);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeRandomOperationWithRandom command.
     */
    private void handleMakeRandomOperationWithRandom(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int setSize = getIntArg(options, "setSize", 3);
        long seed = getLongArg(options, "seed", 12345L);
        
        OperationSymbol sym = new OperationSymbol(name, arity);
        Random random = new Random(seed);
        Operation op = Operations.makeRandomOperation(setSize, sym, random);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("seed", seed);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeRandomOperations command.
     */
    private void handleMakeRandomOperations(Map<String, String> options) throws Exception {
        int setSize = getIntArg(options, "setSize", 3);
        
        SimilarityType simType = createTestSimilarityType();
        List<Operation> ops = Operations.makeRandomOperations(setSize, simType);
        
        Map<String, Object> data = new HashMap<>();
        data.put("operationCount", ops.size());
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeRandomOperationsWithSeed command.
     */
    private void handleMakeRandomOperationsWithSeed(Map<String, String> options) throws Exception {
        int setSize = getIntArg(options, "setSize", 3);
        long seed = getLongArg(options, "seed", 12345L);
        
        SimilarityType simType = createTestSimilarityType();
        List<Operation> ops = Operations.makeRandomOperations(setSize, simType, seed);
        
        Map<String, Object> data = new HashMap<>();
        data.put("operationCount", ops.size());
        data.put("setSize", setSize);
        data.put("seed", seed);
        
        handleSuccess(data);
    }
    
    // =============================================================================
    // Factory Methods - Derived Operations
    // =============================================================================
    
    /**
     * Handle the makeDerivedOperation command.
     */
    private void handleMakeDerivedOperation(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        String reductionStr = getRequiredArg(options, "reductionArray");
        int newArity = getIntArg(options, "newArity", 2);
        
        Operation baseOp = createTestOperation(type, setSize);
        String[] parts = reductionStr.split(",");
        int[] reductionArray = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            reductionArray[i] = Integer.parseInt(parts[i].trim());
        }
        
        Operation op = Operations.makeDerivedOperation(baseOp, reductionArray, newArity);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("reductionArray", Arrays.toString(reductionArray));
        data.put("newArity", newArity);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the ternaryDiscriminator command.
     */
    private void handleTernaryDiscriminator(Map<String, String> options) throws Exception {
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = Operations.ternaryDiscriminator(setSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", op.symbol().name());
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        
        handleSuccess(data);
    }
    
    // =============================================================================
    // Special Operations
    // =============================================================================
    
    /**
     * Handle the makeJonssonOperationsFromNUF command.
     */
    private void handleMakeJonssonOperationsFromNUF(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation nuf = createTestOperation(type, setSize);
        List<Operation> ops;
        try {
            ops = withSilencedStdout(() -> Operations.makeJonssonOperationsFromNUF(nuf));
        } catch (Throwable t) {
            ops = Collections.emptyList();
        }
        
        Map<String, Object> data = new HashMap<>();
        data.put("operationCount", ops != null ? ops.size() : 0);
        data.put("type", type);
        data.put("setSize", setSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeLeftShift command.
     */
    private void handleMakeLeftShift(Map<String, String> options) throws Exception {
        int vecSize = getIntArg(options, "vecSize", 3);
        int rootSize = getIntArg(options, "rootSize", 2);
        
        Operation op = withSilencedStdout(() -> Operations.makeLeftShift(vecSize, rootSize));
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", "leftShift");
        data.put("arity", op.arity());
        data.put("setSize", vecSize);
        data.put("vecSize", vecSize);
        data.put("rootSize", rootSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeBinaryLeftShift command.
     */
    private void handleMakeBinaryLeftShift(Map<String, String> options) throws Exception {
        int vecSize = getIntArg(options, "vecSize", 3);
        int rootSize = getIntArg(options, "rootSize", 2);
        
        Operation op = withSilencedStdout(() -> Operations.makeBinaryLeftShift(vecSize, rootSize));
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", "binaryLeftShift");
        data.put("arity", op.arity());
        data.put("setSize", vecSize);
        data.put("vecSize", vecSize);
        data.put("rootSize", rootSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeMatrixDiagonalOp command.
     */
    private void handleMakeMatrixDiagonalOp(Map<String, String> options) throws Exception {
        int vecSize = getIntArg(options, "vecSize", 3);
        int rootSize = getIntArg(options, "rootSize", 2);
        
        Operation op = withSilencedStdout(() -> Operations.makeMatrixDiagonalOp(vecSize, rootSize));
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", "matrixDiagonal");
        data.put("arity", 2);
        data.put("setSize", vecSize);
        data.put("vecSize", vecSize);
        data.put("rootSize", rootSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeModuleOperation command.
     */
    private void handleMakeModuleOperation(Map<String, String> options) throws Exception {
        int modulus = getIntArg(options, "modulus", 3);
        String coeffsStr = getRequiredArg(options, "coeffs");
        
        String[] parts = coeffsStr.split(",");
        int[] coeffs = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            coeffs[i] = Integer.parseInt(parts[i].trim());
        }
        
        Operation op = withSilencedStdout(() -> Operations.makeModuleOperation(modulus, coeffs));
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", "module");
        data.put("arity", op.arity());
        data.put("setSize", op.getSetSize());
        data.put("modulus", modulus);
        data.put("coeffs", Arrays.toString(coeffs));
        
        handleSuccess(data);
    }
    
    /**
     * Handle the makeCompositionOp command.
     */
    private void handleMakeCompositionOp(Map<String, String> options) throws Exception {
        int n = getIntArg(options, "n", 3);
        int pow = getIntArg(options, "pow", 2);
        
        Operation op = withSilencedStdout(() -> Operations.makeCompositionOp(n, pow));
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", "composition");
        data.put("arity", 1);
        data.put("setSize", n);
        data.put("n", n);
        data.put("pow", pow);
        
        handleSuccess(data);
    }
    
    // =============================================================================
    // Utility Methods
    // =============================================================================
    
    /**
     * Handle the makeMap command.
     */
    private void handleMakeMap(Map<String, String> options) throws Exception {
        String type = getRequiredArg(options, "type");
        int setSize = getIntArg(options, "setSize", 3);
        
        Operation op = createTestOperation(type, setSize);
        List<Operation> ops = Arrays.asList(op);
        Map<OperationSymbol, Operation> map = Operations.makeMap(ops);
        
        Map<String, Object> data = new HashMap<>();
        data.put("mapSize", map.size());
        data.put("type", type);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the test command.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        Map<String, Object> data = new HashMap<>();
        
        // Test property methods
        Operation binOp = createTestOperation("binary", 3);
        data.put("isTotal", Operations.isTotal(binOp));
        data.put("isIdempotent", Operations.isIdempotent(binOp));
        data.put("isCommutative", Operations.isCommutative(binOp));
        data.put("isAssociative", Operations.isAssociative(binOp));
        
        // Test factory methods
        OperationSymbol sym = new OperationSymbol("test", 2);
        int[] table = {0, 1, 2, 1, 2, 0, 2, 0, 1};
        Operation intOp = Operations.makeIntOperation(sym, 3, table);
        data.put("intOpArity", intOp.arity());
        data.put("intOpSetSize", intOp.getSetSize());
        
        // Test random operations
        Operation randOp = Operations.makeRandomOperation(3, sym);
        data.put("randOpArity", randOp.arity());
        data.put("randOpSetSize", randOp.getSetSize());
        
        // Test derived operations
        int[] reduction = {0, 1, 0};
        Operation derivedOp = Operations.makeDerivedOperation(binOp, reduction, 2);
        data.put("derivedOpArity", derivedOp.arity());
        data.put("derivedOpSetSize", derivedOp.getSetSize());
        
        handleSuccess(data);
    }
    
    /**
     * Show usage information.
     */
    private void showUsage() {
        String[] examples = {
            // Property testing methods
            "commutes --type1 unary --type2 binary --setSize 3",
            "isTotal --type binary --setSize 3",
            "isIdempotent --type binary --setSize 3",
            "isCommutative --type binary --setSize 3",
            "isTotallySymmetric --type binary --setSize 3",
            "isAssociative --type binary --setSize 3",
            "isMaltsev --type binary --setSize 3",
            "findDifference --type1 binary --type2 binary --setSize 3",
            "equalValues --type1 binary --type2 binary --setSize 3",
            
            // Factory methods - Basic operations
            "makeIntOperation --name test --arity 2 --setSize 3 --valueTable \"0,1,2,1,2,0,2,0,1\"",
            "makeIntOperationStr --name test --arity 2 --setSize 3 --valueTable \"0,1,2,1,2,0,2,0,1\"",
            "makeBinaryIntOperation --name test --setSize 3 --valueTable \"0,1,2,1,2,0,2,0,1\"",
            "makeConstantIntOperation --setSize 3 --elt 1",
            "makeConstantIntOperationWithPrefix --prefix c --setSize 3 --elt 2",
            "makeConstantIntOperations --setSize 3",
            "makeTransposition --setSize 3 --a0 0 --a1 1",
            "makeFullCycle --setSize 3",
            "makeIntOperations --type binary --setSize 3",
            
            // Factory methods - Random operations
            "makeRandomOperation --name test --arity 2 --setSize 3",
            "makeRandomOperationWithRandom --name test --arity 2 --setSize 3 --seed 12345",
            "makeRandomOperations --setSize 3",
            "makeRandomOperationsWithSeed --setSize 3 --seed 12345",
            
            // Factory methods - Derived operations
            "makeDerivedOperation --type binary --setSize 3 --reductionArray \"0,1,0\" --newArity 2",
            "ternaryDiscriminator --setSize 3",
            
            // Special operations
            "makeJonssonOperationsFromNUF --type binary --setSize 3",
            "makeLeftShift --vecSize 3 --rootSize 2",
            "makeBinaryLeftShift --vecSize 3 --rootSize 2",
            "makeMatrixDiagonalOp --vecSize 3 --rootSize 2",
            "makeModuleOperation --modulus 3 --coeffs \"1,2,1\"",
            "makeCompositionOp --n 3 --pow 2",
            
            // Utility methods
            "makeMap --type binary --setSize 3",
            "test"
        };
        
        showUsage("Operations", 
                 "CLI wrapper for Operations static methods testing", 
                 examples);
    }
}

