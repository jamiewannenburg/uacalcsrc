/* SimilarityTypeWrapper.java - CLI wrapper for org.uacalc.alg.op.SimilarityType
 * 
 * This wrapper exposes all public methods of the SimilarityType class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg.op;

import java.util.*;
import org.uacalc.alg.op.SimilarityType;
import org.uacalc.alg.op.OperationSymbol;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the SimilarityType class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class SimilarityTypeWrapper extends WrapperBase {
    
    /**
     * Main entry point for the SimilarityType CLI wrapper.
     */
    public static void main(String[] args) {
        SimilarityTypeWrapper wrapper = new SimilarityTypeWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("SimilarityType wrapper failed", e);
        }
    }
    
    /**
     * Run the SimilarityType CLI wrapper with the given arguments.
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
                
            case "new_sorted":
                handleNewSorted(options);
                break;
                
            case "get_operation_symbols":
                handleGetOperationSymbols(options);
                break;
                
            case "get_sorted_operation_symbols":
                handleGetSortedOperationSymbols(options);
                break;
                
            case "input_size":
                handleInputSize(options);
                break;
                
            case "get_arities_map":
                handleGetAritiesMap(options);
                break;
                
            case "get_max_arity":
                handleGetMaxArity(options);
                break;
                
            case "lattice_similarity_type":
                handleLatticeSimilarityType();
                break;
                
            case "group_similarity_type":
                handleGroupSimilarityType();
                break;
                
            case "arities_string":
                handleAritiesString(options);
                break;
                
            case "toString":
                handleToString(options);
                break;
                
            case "equals":
                handleEquals(options);
                break;
                
            case "hashCode":
                handleHashCode(options);
                break;
                
            case "test":
                handleTest();
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the 'new' command.
     */
    private void handleNew(Map<String, String> options) throws Exception {
        String operationSymbolsStr = getRequiredArg(options, "operation_symbols");
        List<OperationSymbol> operationSymbols = parseOperationSymbols(operationSymbolsStr);
        
        SimilarityType similarityType = new SimilarityType(operationSymbols);
        
        Map<String, Object> result = new HashMap<>();
        result.put("similarity_type", similarityType.toString());
        result.put("operation_symbols", operationSymbolsStr);
        
        handleSuccess(result);
    }
    
    /**
     * Handle the 'new_sorted' command.
     */
    private void handleNewSorted(Map<String, String> options) throws Exception {
        String operationSymbolsStr = getRequiredArg(options, "operation_symbols");
        List<OperationSymbol> operationSymbols = parseOperationSymbols(operationSymbolsStr);
        
        SimilarityType similarityType = new SimilarityType(operationSymbols, true);
        
        Map<String, Object> result = new HashMap<>();
        result.put("similarity_type", similarityType.toString());
        result.put("operation_symbols", operationSymbolsStr);
        result.put("sorted", true);
        
        handleSuccess(result);
    }
    
    /**
     * Handle the 'get_operation_symbols' command.
     */
    private void handleGetOperationSymbols(Map<String, String> options) throws Exception {
        String operationSymbolsStr = getRequiredArg(options, "operation_symbols");
        List<OperationSymbol> operationSymbols = parseOperationSymbols(operationSymbolsStr);
        
        SimilarityType similarityType = new SimilarityType(operationSymbols);
        List<OperationSymbol> result = similarityType.getOperationSymbols();
        
        Map<String, Object> response = new HashMap<>();
        response.put("operation_symbols", formatOperationSymbols(result));
        response.put("count", result.size());
        
        handleSuccess(response);
    }
    
    /**
     * Handle the 'get_sorted_operation_symbols' command.
     */
    private void handleGetSortedOperationSymbols(Map<String, String> options) throws Exception {
        String operationSymbolsStr = getRequiredArg(options, "operation_symbols");
        List<OperationSymbol> operationSymbols = parseOperationSymbols(operationSymbolsStr);
        
        SimilarityType similarityType = new SimilarityType(operationSymbols);
        List<OperationSymbol> result = similarityType.getSortedOperationSymbols();
        
        Map<String, Object> response = new HashMap<>();
        response.put("sorted_operation_symbols", formatOperationSymbols(result));
        response.put("count", result.size());
        
        handleSuccess(response);
    }
    
    /**
     * Handle the 'input_size' command.
     */
    private void handleInputSize(Map<String, String> options) throws Exception {
        String operationSymbolsStr = getRequiredArg(options, "operation_symbols");
        int algSize = getIntArg(options, "alg_size", 5);
        
        List<OperationSymbol> operationSymbols = parseOperationSymbols(operationSymbolsStr);
        SimilarityType similarityType = new SimilarityType(operationSymbols);
        
        int inputSize = similarityType.inputSize(algSize);
        
        Map<String, Object> result = new HashMap<>();
        result.put("input_size", inputSize);
        result.put("alg_size", algSize);
        result.put("operation_symbols", operationSymbolsStr);
        
        handleSuccess(result);
    }
    
    /**
     * Handle the 'get_arities_map' command.
     */
    private void handleGetAritiesMap(Map<String, String> options) throws Exception {
        String operationSymbolsStr = getRequiredArg(options, "operation_symbols");
        List<OperationSymbol> operationSymbols = parseOperationSymbols(operationSymbolsStr);
        
        SimilarityType similarityType = new SimilarityType(operationSymbols);
        Map<Integer, Integer> aritiesMap = similarityType.getAritiesMap();
        
        Map<String, Object> result = new HashMap<>();
        result.put("arities_map", aritiesMap);
        result.put("operation_symbols", operationSymbolsStr);
        
        handleSuccess(result);
    }
    
    /**
     * Handle the 'get_max_arity' command.
     */
    private void handleGetMaxArity(Map<String, String> options) throws Exception {
        String operationSymbolsStr = getRequiredArg(options, "operation_symbols");
        List<OperationSymbol> operationSymbols = parseOperationSymbols(operationSymbolsStr);
        
        SimilarityType similarityType = new SimilarityType(operationSymbols);
        int maxArity = similarityType.getMaxArity();
        
        Map<String, Object> result = new HashMap<>();
        result.put("max_arity", maxArity);
        result.put("operation_symbols", operationSymbolsStr);
        
        handleSuccess(result);
    }
    
    /**
     * Handle the 'lattice_similarity_type' command.
     */
    private void handleLatticeSimilarityType() throws Exception {
        SimilarityType latticeType = SimilarityType.LATTICE_SIMILARITY_TYPE;
        
        Map<String, Object> result = new HashMap<>();
        result.put("similarity_type", latticeType.toString());
        result.put("operation_symbols", formatOperationSymbols(latticeType.getOperationSymbols()));
        result.put("max_arity", latticeType.getMaxArity());
        
        handleSuccess(result);
    }
    
    /**
     * Handle the 'group_similarity_type' command.
     */
    private void handleGroupSimilarityType() throws Exception {
        SimilarityType groupType = SimilarityType.GROUP_SIMILARITY_TYPE;
        
        Map<String, Object> result = new HashMap<>();
        result.put("similarity_type", groupType.toString());
        result.put("operation_symbols", formatOperationSymbols(groupType.getOperationSymbols()));
        result.put("max_arity", groupType.getMaxArity());
        
        handleSuccess(result);
    }
    
    /**
     * Handle the 'arities_string' command.
     */
    private void handleAritiesString(Map<String, String> options) throws Exception {
        String operationSymbolsStr = getRequiredArg(options, "operation_symbols");
        List<OperationSymbol> operationSymbols = parseOperationSymbols(operationSymbolsStr);
        
        SimilarityType similarityType = new SimilarityType(operationSymbols);
        String aritiesString = similarityType.aritiesString();
        
        Map<String, Object> result = new HashMap<>();
        result.put("arities_string", aritiesString);
        result.put("operation_symbols", operationSymbolsStr);
        
        handleSuccess(result);
    }
    
    /**
     * Handle the 'toString' command.
     */
    private void handleToString(Map<String, String> options) throws Exception {
        String operationSymbolsStr = getRequiredArg(options, "operation_symbols");
        List<OperationSymbol> operationSymbols = parseOperationSymbols(operationSymbolsStr);
        
        SimilarityType similarityType = new SimilarityType(operationSymbols);
        String stringRep = similarityType.toString();
        
        Map<String, Object> result = new HashMap<>();
        result.put("string_representation", stringRep);
        result.put("operation_symbols", operationSymbolsStr);
        
        handleSuccess(result);
    }
    
    /**
     * Handle the 'equals' command.
     */
    private void handleEquals(Map<String, String> options) throws Exception {
        String operationSymbols1Str = getRequiredArg(options, "operation_symbols1");
        String operationSymbols2Str = getRequiredArg(options, "operation_symbols2");
        
        List<OperationSymbol> operationSymbols1 = parseOperationSymbols(operationSymbols1Str);
        List<OperationSymbol> operationSymbols2 = parseOperationSymbols(operationSymbols2Str);
        
        SimilarityType similarityType1 = new SimilarityType(operationSymbols1);
        SimilarityType similarityType2 = new SimilarityType(operationSymbols2);
        
        boolean equals = similarityType1.equals(similarityType2);
        
        Map<String, Object> result = new HashMap<>();
        result.put("equals", equals);
        result.put("operation_symbols1", operationSymbols1Str);
        result.put("operation_symbols2", operationSymbols2Str);
        
        handleSuccess(result);
    }
    
    /**
     * Handle the 'hashCode' command.
     */
    private void handleHashCode(Map<String, String> options) throws Exception {
        String operationSymbolsStr = getRequiredArg(options, "operation_symbols");
        List<OperationSymbol> operationSymbols = parseOperationSymbols(operationSymbolsStr);
        
        SimilarityType similarityType = new SimilarityType(operationSymbols);
        int hashCode = similarityType.hashCode();
        
        Map<String, Object> result = new HashMap<>();
        result.put("hash_code", hashCode);
        result.put("operation_symbols", operationSymbolsStr);
        
        handleSuccess(result);
    }
    
    /**
     * Handle the 'test' command - run basic functionality tests.
     */
    private void handleTest() throws Exception {
        Map<String, Object> results = new HashMap<>();
        
        // Test 1: Create similarity type
        List<OperationSymbol> ops = Arrays.asList(OperationSymbol.JOIN, OperationSymbol.MEET);
        SimilarityType st = new SimilarityType(ops);
        results.put("test_create", st.toString());
        
        // Test 2: Input size calculation
        int inputSize = st.inputSize(3);
        results.put("test_input_size", inputSize);
        
        // Test 3: Max arity
        int maxArity = st.getMaxArity();
        results.put("test_max_arity", maxArity);
        
        // Test 4: Arities map
        Map<Integer, Integer> aritiesMap = st.getAritiesMap();
        results.put("test_arities_map", aritiesMap);
        
        // Test 5: Constants
        results.put("test_lattice_type", SimilarityType.LATTICE_SIMILARITY_TYPE.toString());
        results.put("test_group_type", SimilarityType.GROUP_SIMILARITY_TYPE.toString());
        
        // Test 6: Equality
        SimilarityType st2 = new SimilarityType(Arrays.asList(OperationSymbol.MEET, OperationSymbol.JOIN));
        results.put("test_equals", st.equals(st2));
        
        handleSuccess(results);
    }
    
    /**
     * Parse operation symbols from a string format.
     * Format: "name1:arity1,name2:arity2,..."
     */
    private List<OperationSymbol> parseOperationSymbols(String str) {
        List<OperationSymbol> symbols = new ArrayList<>();
        if (str == null || str.trim().isEmpty()) {
            return symbols;
        }
        
        String[] parts = str.split(",");
        for (String part : parts) {
            String[] nameArity = part.trim().split(":");
            if (nameArity.length != 2) {
                throw new IllegalArgumentException("Invalid operation symbol format: " + part + 
                    ". Expected format: name:arity");
            }
            String name = nameArity[0].trim();
            int arity = Integer.parseInt(nameArity[1].trim());
            symbols.add(new OperationSymbol(name, arity));
        }
        
        return symbols;
    }
    
    /**
     * Format operation symbols for output.
     */
    private String formatOperationSymbols(List<OperationSymbol> symbols) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < symbols.size(); i++) {
            if (i > 0) sb.append(",");
            OperationSymbol sym = symbols.get(i);
            sb.append(sym.name()).append(":").append(sym.arity());
        }
        return sb.toString();
    }
    
    /**
     * Show usage information for the SimilarityType wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "SimilarityTypeWrapper new --operation_symbols=\"join:2,meet:2\"",
            "SimilarityTypeWrapper new_sorted --operation_symbols=\"prod:2,inv:1,id:0\"",
            "SimilarityTypeWrapper get_operation_symbols --operation_symbols=\"join:2,meet:2\"",
            "SimilarityTypeWrapper input_size --operation_symbols=\"join:2,meet:2\" --alg_size=5",
            "SimilarityTypeWrapper get_arities_map --operation_symbols=\"join:2,meet:2,inv:1\"",
            "SimilarityTypeWrapper get_max_arity --operation_symbols=\"join:2,meet:2,inv:1\"",
            "SimilarityTypeWrapper lattice_similarity_type",
            "SimilarityTypeWrapper group_similarity_type",
            "SimilarityTypeWrapper arities_string --operation_symbols=\"join:2,meet:2,inv:1\"",
            "SimilarityTypeWrapper toString --operation_symbols=\"join:2,meet:2\"",
            "SimilarityTypeWrapper equals --operation_symbols1=\"join:2,meet:2\" --operation_symbols2=\"meet:2,join:2\"",
            "SimilarityTypeWrapper hashCode --operation_symbols=\"join:2,meet:2\"",
            "SimilarityTypeWrapper test"
        };
        
        showUsage("SimilarityTypeWrapper", 
                 "CLI wrapper for org.uacalc.alg.op.SimilarityType operations", 
                 examples);
    }
}
