/* AlgebrasWrapper.java - CLI wrapper for org.uacalc.alg.Algebras
 * 
 * This wrapper exposes all public methods of the Algebras class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import java.io.*;
import org.uacalc.alg.*;
import org.uacalc.alg.op.*;
import org.uacalc.io.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Algebras class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class AlgebrasWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Algebras CLI wrapper.
     */
    public static void main(String[] args) {
        AlgebrasWrapper wrapper = new AlgebrasWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Algebras wrapper failed", e);
        }
    }
    
    /**
     * Run the Algebras CLI wrapper with the given arguments.
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
                
            case "isEndomorphism":
                handleIsEndomorphism(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle isEndomorphism command - test if an operation is an endomorphism.
     */
    private void handleIsEndomorphism(Map<String, String> options) throws Exception {
        // Get algebra file path or create test algebra
        String algFile = options.get("algebra");
        SmallAlgebra alg;
        
        if (algFile != null && !algFile.isEmpty()) {
            // Load algebra from file
            File file = new File(algFile);
            if (!file.exists()) {
                handleError("Algebra file not found: " + algFile, null);
                return;
            }
            alg = AlgebraIO.readAlgebraFile(file);
        } else {
            // Create a simple test algebra
            int size = getIntArg(options, "size", 2);
            alg = makeTestAlgebra(size);
        }
        
        // Get operation - can be specified as:
        // 1. Operation file (not supported yet)
        // 2. Table specification: "arity:table" where table is comma-separated
        String opSpec = options.get("operation");
        if (opSpec == null || opSpec.isEmpty()) {
            handleError("Required argument missing: operation", null);
            return;
        }
        
        Operation endo = parseOperation(opSpec, alg.cardinality());
        
        // Call Java method
        boolean result = Algebras.isEndomorphism(endo, alg);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "isEndomorphism");
        response.put("result", result);
        response.put("algebra_size", alg.cardinality());
        response.put("operation_arity", endo.arity());
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Parse an operation from string specification.
     * Format: "arity:table" where table is comma-separated values
     * Example: "1:0,1" for identity on 2-element set
     */
    private Operation parseOperation(String opSpec, int setSize) throws Exception {
        int colonIndex = opSpec.indexOf(':');
        if (colonIndex < 0) {
            throw new IllegalArgumentException("Invalid operation format (missing colon): " + opSpec);
        }
        
        int arity = Integer.parseInt(opSpec.substring(0, colonIndex).trim());
        String tableStr = opSpec.substring(colonIndex + 1).trim();
        
        // Parse table
        String[] tableParts = tableStr.split(",");
        int[] table = new int[tableParts.length];
        for (int i = 0; i < tableParts.length; i++) {
            table[i] = Integer.parseInt(tableParts[i].trim());
        }
        
        // Create operation symbol
        OperationSymbol symbol = new OperationSymbol("endo", arity, false);
        
        // Create operation
        Operation op = Operations.makeIntOperation(symbol, setSize, table);
        
        return op;
    }
    
    /**
     * Create a simple test algebra with given size.
     */
    private SmallAlgebra makeTestAlgebra(int size) throws Exception {
        // Create a simple algebra with a binary operation (first projection)
        List<Operation> ops = new ArrayList<>();
        
        OperationSymbol sym = new OperationSymbol("f", 2, false);
        int[] table = new int[size * size];
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                table[i * size + j] = i; // First projection
            }
        }
        Operation op = Operations.makeIntOperation(sym, size, table);
        ops.add(op);
        
        return new BasicAlgebra("TestAlg", size, ops);
    }
    
    
    /**
     * Show usage information for the Algebras wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "isEndomorphism --algebra algebras/ba2.ua --operation \"1:0,1\"",
            "isEndomorphism --size 2 --operation \"1:0,1\"",
            "help"
        };
        
        showUsage("Algebras", 
                 "CLI wrapper for org.uacalc.alg.Algebras operations", 
                 examples);
    }
}
