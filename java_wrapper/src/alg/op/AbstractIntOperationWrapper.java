/* AbstractIntOperationWrapper.java - CLI wrapper for org.uacalc.alg.op.AbstractIntOperation
 * 
 * This wrapper creates AbstractIntOperation instances for testing. This is a concrete
 * class (despite the name) that extends AbstractOperation and is designed for
 * Jython/Groovy compatibility. Most methods throw UnsupportedOperationException.
 */

package java_wrapper.src.alg.op;

import java.util.*;
import org.uacalc.alg.op.OperationSymbol;
import org.uacalc.alg.op.AbstractIntOperation;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for AbstractIntOperation that provides command-line access
 * to constructor testing and basic functionality verification.
 */
public class AbstractIntOperationWrapper extends WrapperBase {
    
    /**
     * Main entry point for the AbstractIntOperation CLI wrapper.
     */
    public static void main(String[] args) {
        AbstractIntOperationWrapper wrapper = new AbstractIntOperationWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("AbstractIntOperation wrapper failed", e);
        }
    }
    
    /**
     * Run the AbstractIntOperation CLI wrapper with the given arguments.
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
                
            case "newWithName":
                handleNewWithName(options);
                break;
                
            case "newWithSymbol":
                handleNewWithSymbol(options);
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
                
            case "valueAtException":
                handleValueAtException(options);
                break;
                
            case "isTotal":
                handleIsTotal(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the newWithName command - create AbstractIntOperation with name/arity/size.
     */
    private void handleNewWithName(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int algSize = getIntArg(options, "algSize", 3);
        
        AbstractIntOperation op = new AbstractIntOperation(name, arity, algSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("name", op.symbol().name());
        data.put("arity", op.arity());
        data.put("algSize", op.getSetSize());
        data.put("symbolName", op.symbol().name());
        data.put("symbolArity", op.symbol().arity());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the newWithSymbol command - create AbstractIntOperation with symbol/size.
     */
    private void handleNewWithSymbol(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int algSize = getIntArg(options, "algSize", 3);
        boolean associative = getBoolArg(options, "associative", false);
        
        OperationSymbol symbol = new OperationSymbol(name, arity, associative);
        AbstractIntOperation op = new AbstractIntOperation(symbol, algSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("name", op.symbol().name());
        data.put("arity", op.arity());
        data.put("algSize", op.getSetSize());
        data.put("symbolName", op.symbol().name());
        data.put("symbolArity", op.symbol().arity());
        data.put("symbolAssociative", op.symbol().isAssociative());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the arity command.
     */
    private void handleArity(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int algSize = getIntArg(options, "algSize", 3);
        
        AbstractIntOperation op = new AbstractIntOperation(name, arity, algSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("arity", op.arity());
        data.put("name", name);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the getSetSize command.
     */
    private void handleGetSetSize(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int algSize = getIntArg(options, "algSize", 3);
        
        AbstractIntOperation op = new AbstractIntOperation(name, arity, algSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("setSize", op.getSetSize());
        data.put("algSize", algSize);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the symbol command.
     */
    private void handleSymbol(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int algSize = getIntArg(options, "algSize", 3);
        
        AbstractIntOperation op = new AbstractIntOperation(name, arity, algSize);
        OperationSymbol sym = op.symbol();
        
        Map<String, Object> data = new HashMap<>();
        data.put("symbolName", sym.name());
        data.put("symbolArity", sym.arity());
        data.put("symbolAssociative", sym.isAssociative());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the valueAtException command - verify that valueAt throws exception.
     */
    private void handleValueAtException(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int algSize = getIntArg(options, "algSize", 3);
        
        AbstractIntOperation op = new AbstractIntOperation(name, arity, algSize);
        
        boolean threwException = false;
        String exceptionMessage = "";
        
        try {
            // This should throw UnsupportedOperationException
            List<Integer> args = Arrays.asList(0, 1);
            op.valueAt(args);
        } catch (UnsupportedOperationException e) {
            threwException = true;
            exceptionMessage = e.getClass().getSimpleName();
        }
        
        Map<String, Object> data = new HashMap<>();
        data.put("threwException", threwException);
        data.put("exceptionType", exceptionMessage);
        data.put("name", name);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isTotal command.
     */
    private void handleIsTotal(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = getIntArg(options, "arity", 2);
        int algSize = getIntArg(options, "algSize", 3);
        
        AbstractIntOperation op = new AbstractIntOperation(name, arity, algSize);
        
        Map<String, Object> data = new HashMap<>();
        data.put("isTotal", op.isTotal());
        data.put("name", name);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the test command.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        Map<String, Object> data = new HashMap<>();
        
        // Test constructor with name
        AbstractIntOperation op1 = new AbstractIntOperation("test1", 2, 3);
        data.put("constructor1_arity", op1.arity());
        data.put("constructor1_setSize", op1.getSetSize());
        data.put("constructor1_symbolName", op1.symbol().name());
        
        // Test constructor with symbol
        OperationSymbol sym = new OperationSymbol("test2", 3, false);
        AbstractIntOperation op2 = new AbstractIntOperation(sym, 4);
        data.put("constructor2_arity", op2.arity());
        data.put("constructor2_setSize", op2.getSetSize());
        data.put("constructor2_symbolName", op2.symbol().name());
        
        // Test that valueAt throws exception
        boolean threw = false;
        try {
            op1.valueAt(Arrays.asList(0, 1));
        } catch (UnsupportedOperationException e) {
            threw = true;
        }
        data.put("valueAt_throws", threw);
        
        // Test isTotal
        data.put("isTotal", op1.isTotal());
        
        handleSuccess(data);
    }
    
    /**
     * Show usage information.
     */
    private void showUsage() {
        String[] examples = {
            "newWithName --name \"f\" --arity 2 --algSize 3",
            "newWithSymbol --name \"g\" --arity 3 --algSize 4 --associative false",
            "arity --name \"f\" --arity 2 --algSize 3",
            "getSetSize --name \"f\" --arity 2 --algSize 3", 
            "symbol --name \"f\" --arity 2 --algSize 3",
            "valueAtException --name \"f\" --arity 2 --algSize 3",
            "isTotal --name \"f\" --arity 2 --algSize 3",
            "test"
        };
        
        showUsage("AbstractIntOperation", 
                 "CLI wrapper for org.uacalc.alg.op.AbstractIntOperation operations", 
                 examples);
    }
}
