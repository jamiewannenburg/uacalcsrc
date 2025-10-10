/* OperationSymbolWrapper.java - CLI wrapper for org.uacalc.alg.op.OperationSymbol
 * 
 * This wrapper exposes all public methods of the OperationSymbol class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

import java.util.*;
import org.uacalc.alg.op.OperationSymbol;

/**
 * CLI wrapper for the OperationSymbol class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class OperationSymbolWrapper extends WrapperBase {
    
    /**
     * Main entry point for the OperationSymbol CLI wrapper.
     */
    public static void main(String[] args) {
        OperationSymbolWrapper wrapper = new OperationSymbolWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("OperationSymbol wrapper failed", e);
        }
    }
    
    /**
     * Run the OperationSymbol CLI wrapper with the given arguments.
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
                
            case "arity":
                handleArity(options);
                break;
                
            case "name":
                handleName(options);
                break;
                
            case "isAssociative":
                handleIsAssociative(options);
                break;
                
            case "setAssociative":
                handleSetAssociative(options);
                break;
                
            case "toString":
                handleToString(options);
                break;
                
            case "toStringWithArity":
                handleToStringWithArity(options);
                break;
                
            case "compareTo":
                handleCompareTo(options);
                break;
                
            case "equals":
                handleEquals(options);
                break;
                
            case "hashCode":
                handleHashCode(options);
                break;
                
            case "getOperationSymbol":
                handleGetOperationSymbol(options);
                break;
                
            case "constants":
                handleConstants(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the new command - create a new OperationSymbol.
     */
    private void handleNew(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = Integer.parseInt(getRequiredArg(options, "arity"));
        boolean associative = getBoolArg(options, "associative", false);
        
        OperationSymbol sym = new OperationSymbol(name, arity, associative);
        
        Map<String, Object> data = new HashMap<>();
        data.put("name", sym.name());
        data.put("arity", sym.arity());
        data.put("associative", sym.isAssociative());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the arity command - get arity of an OperationSymbol.
     */
    private void handleArity(Map<String, String> options) throws Exception {
        OperationSymbol sym = createOperationSymbol(options);
        
        Map<String, Object> data = new HashMap<>();
        data.put("arity", sym.arity());
        data.put("symbol", sym.toString());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the name command - get name of an OperationSymbol.
     */
    private void handleName(Map<String, String> options) throws Exception {
        OperationSymbol sym = createOperationSymbol(options);
        
        Map<String, Object> data = new HashMap<>();
        data.put("name", sym.name());
        data.put("symbol", sym.toString());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the isAssociative command - check if OperationSymbol is associative.
     */
    private void handleIsAssociative(Map<String, String> options) throws Exception {
        OperationSymbol sym = createOperationSymbol(options);
        
        Map<String, Object> data = new HashMap<>();
        data.put("associative", sym.isAssociative());
        data.put("symbol", sym.toString());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the setAssociative command - set associativity of an OperationSymbol.
     */
    private void handleSetAssociative(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        int arity = Integer.parseInt(getRequiredArg(options, "arity"));
        boolean associative = getBoolArg(options, "associative", false);
        boolean newAssociative = getBoolArg(options, "newAssociative", false);
        
        OperationSymbol sym = new OperationSymbol(name, arity, associative);
        sym.setAssociative(newAssociative);
        
        Map<String, Object> data = new HashMap<>();
        data.put("name", sym.name());
        data.put("arity", sym.arity());
        data.put("associative", sym.isAssociative());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the toString command - convert OperationSymbol to string.
     */
    private void handleToString(Map<String, String> options) throws Exception {
        OperationSymbol sym = createOperationSymbol(options);
        
        Map<String, Object> data = new HashMap<>();
        data.put("string", sym.toString());
        data.put("symbol", sym.toString());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the toStringWithArity command - convert OperationSymbol to string with arity.
     */
    private void handleToStringWithArity(Map<String, String> options) throws Exception {
        OperationSymbol sym = createOperationSymbol(options);
        boolean showArity = getBoolArg(options, "showArity", false);
        
        Map<String, Object> data = new HashMap<>();
        data.put("string", sym.toString(showArity));
        data.put("showArity", showArity);
        data.put("symbol", sym.toString());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the compareTo command - compare two OperationSymbols.
     */
    private void handleCompareTo(Map<String, String> options) throws Exception {
        OperationSymbol sym1 = createOperationSymbol(options, "1");
        OperationSymbol sym2 = createOperationSymbol(options, "2");
        
        int comparison = sym1.compareTo(sym2);
        
        Map<String, Object> data = new HashMap<>();
        data.put("comparison", comparison);
        data.put("symbol1", sym1.toString());
        data.put("symbol2", sym2.toString());
        data.put("symbol1_arity", sym1.arity());
        data.put("symbol2_arity", sym2.arity());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the equals command - check equality of two OperationSymbols.
     */
    private void handleEquals(Map<String, String> options) throws Exception {
        OperationSymbol sym1 = createOperationSymbol(options, "1");
        OperationSymbol sym2 = createOperationSymbol(options, "2");
        
        boolean equals = sym1.equals(sym2);
        
        Map<String, Object> data = new HashMap<>();
        data.put("equals", equals);
        data.put("symbol1", sym1.toString());
        data.put("symbol2", sym2.toString());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the hashCode command - get hash code of an OperationSymbol.
     */
    private void handleHashCode(Map<String, String> options) throws Exception {
        OperationSymbol sym = createOperationSymbol(options);
        
        Map<String, Object> data = new HashMap<>();
        data.put("hashCode", sym.hashCode());
        data.put("symbol", sym.toString());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the getOperationSymbol command - generate OperationSymbol with uniform naming.
     */
    private void handleGetOperationSymbol(Map<String, String> options) throws Exception {
        int arity = Integer.parseInt(getRequiredArg(options, "arity"));
        
        OperationSymbol sym = OperationSymbol.getOperationSymbol(arity);
        
        Map<String, Object> data = new HashMap<>();
        data.put("name", sym.name());
        data.put("arity", sym.arity());
        data.put("associative", sym.isAssociative());
        
        handleSuccess(data);
    }
    
    /**
     * Handle the constants command - get all static constants.
     */
    private void handleConstants(Map<String, String> options) throws Exception {
        Map<String, Object> data = new HashMap<>();
        
        Map<String, Object> join = new HashMap<>();
        join.put("name", OperationSymbol.JOIN.name());
        join.put("arity", OperationSymbol.JOIN.arity());
        join.put("associative", OperationSymbol.JOIN.isAssociative());
        data.put("JOIN", join);
        
        Map<String, Object> meet = new HashMap<>();
        meet.put("name", OperationSymbol.MEET.name());
        meet.put("arity", OperationSymbol.MEET.arity());
        meet.put("associative", OperationSymbol.MEET.isAssociative());
        data.put("MEET", meet);
        
        Map<String, Object> product = new HashMap<>();
        product.put("name", OperationSymbol.PRODUCT.name());
        product.put("arity", OperationSymbol.PRODUCT.arity());
        product.put("associative", OperationSymbol.PRODUCT.isAssociative());
        data.put("PRODUCT", product);
        
        Map<String, Object> inverse = new HashMap<>();
        inverse.put("name", OperationSymbol.INVERSE.name());
        inverse.put("arity", OperationSymbol.INVERSE.arity());
        inverse.put("associative", OperationSymbol.INVERSE.isAssociative());
        data.put("INVERSE", inverse);
        
        Map<String, Object> identity = new HashMap<>();
        identity.put("name", OperationSymbol.IDENTITY.name());
        identity.put("arity", OperationSymbol.IDENTITY.arity());
        identity.put("associative", OperationSymbol.IDENTITY.isAssociative());
        data.put("IDENTITY", identity);
        
        handleSuccess(data);
    }
    
    /**
     * Handle the test command - run basic functionality tests.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        Map<String, Object> data = new HashMap<>();
        
        // Test basic creation
        OperationSymbol sym1 = new OperationSymbol("f", 2, false);
        data.put("basic_creation", sym1.toString());
        
        // Test associativity
        OperationSymbol sym2 = new OperationSymbol("g", 2, true);
        data.put("associative_creation", sym2.isAssociative());
        
        // Test comparison
        OperationSymbol sym3 = new OperationSymbol("h", 3, false);
        int comparison = sym3.compareTo(sym1);
        data.put("comparison_result", comparison);
        
        // Test getOperationSymbol
        OperationSymbol sym4 = OperationSymbol.getOperationSymbol(2);
        data.put("generated_symbol", sym4.name());
        
        handleSuccess(data);
    }
    
    /**
     * Create an OperationSymbol from command line options.
     */
    private OperationSymbol createOperationSymbol(Map<String, String> options) throws Exception {
        return createOperationSymbol(options, "");
    }
    
    /**
     * Create an OperationSymbol from command line options with suffix.
     */
    private OperationSymbol createOperationSymbol(Map<String, String> options, String suffix) throws Exception {
        String name = getRequiredArg(options, "name" + suffix);
        int arity = Integer.parseInt(getRequiredArg(options, "arity" + suffix));
        boolean associative = getBoolArg(options, "associative" + suffix, false);
        
        return new OperationSymbol(name, arity, associative);
    }
    
    /**
     * Show usage information for the OperationSymbol wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "new --name \"f\" --arity 2",
            "new --name \"g\" --arity 2 --associative true",
            "arity --name \"f\" --arity 2",
            "name --name \"f\" --arity 2",
            "isAssociative --name \"f\" --arity 2",
            "setAssociative --name \"f\" --arity 2 --newAssociative true",
            "toString --name \"f\" --arity 2",
            "toStringWithArity --name \"f\" --arity 2 --showArity true",
            "compareTo --name1 \"f\" --arity1 2 --name2 \"g\" --arity2 3",
            "equals --name1 \"f\" --arity1 2 --name2 \"f\" --arity2 2",
            "hashCode --name \"f\" --arity 2",
            "getOperationSymbol --arity 2",
            "constants",
            "test"
        };
        
        showUsage("OperationSymbol", 
                 "CLI wrapper for org.uacalc.alg.op.OperationSymbol operations", 
                 examples);
    }
}
