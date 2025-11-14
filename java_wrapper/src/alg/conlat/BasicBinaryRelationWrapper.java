/* BasicBinaryRelationWrapper.java - CLI wrapper for org.uacalc.alg.conlat.BasicBinaryRelation
 * 
 * This wrapper exposes all public methods of the BasicBinaryRelation class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg.conlat;

import java.util.*;
import org.uacalc.alg.conlat.BasicBinaryRelation;
import org.uacalc.alg.conlat.BinaryRelation;
import org.uacalc.util.IntArray;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the BasicBinaryRelation class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class BasicBinaryRelationWrapper extends WrapperBase {
    
    private BasicBinaryRelation relation;
    private int universeSize;
    
    /**
     * Main entry point for the BasicBinaryRelation CLI wrapper.
     */
    public static void main(String[] args) {
        BasicBinaryRelationWrapper wrapper = new BasicBinaryRelationWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("BasicBinaryRelation wrapper failed", e);
        }
    }
    
    /**
     * Run the BasicBinaryRelation CLI wrapper with the given arguments.
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
                
            case "add":
                handleAdd(options);
                break;
                
            case "is_related":
                handleIsRelated(options);
                break;
                
            case "universe_size":
                handleUniverseSize(options);
                break;
                
            case "get_pairs":
                handleGetPairs(options);
                break;
                
            case "compose":
                handleCompose(options);
                break;
                
            case "is_reflexive":
                handleIsReflexive(options);
                break;
                
            case "is_symmetric":
                handleIsSymmetric(options);
                break;
                
            case "identity":
                handleIdentity(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the create command.
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        String sizeStr = getRequiredArg(options, "size");
        int size = Integer.parseInt(sizeStr);
        
        if (size <= 0) {
            handleError("Size must be positive", null);
            return;
        }
        
        relation = new BasicBinaryRelation(size);
        universeSize = size;
        
        handleSuccess("{\"command\":\"create\",\"size\":" + size + ",\"status\":\"created\"}");
    }
    
    /**
     * Handle the add command.
     */
    private void handleAdd(Map<String, String> options) throws Exception {
        if (relation == null) {
            handleError("No relation created. Use 'create' first.", null);
            return;
        }
        
        String iStr = getRequiredArg(options, "i");
        String jStr = getRequiredArg(options, "j");
        
        int i = Integer.parseInt(iStr);
        int j = Integer.parseInt(jStr);
        
        if (i < 0 || i >= universeSize || j < 0 || j >= universeSize) {
            handleError("Indices out of bounds", null);
            return;
        }
        
        relation.add(i, j);
        
        handleSuccess("{\"command\":\"add\",\"i\":" + i + ",\"j\":" + j + ",\"status\":\"added\"}");
    }
    
    /**
     * Handle the is_related command.
     */
    private void handleIsRelated(Map<String, String> options) throws Exception {
        if (relation == null) {
            handleError("No relation created. Use 'create' first.", null);
            return;
        }
        
        String iStr = getRequiredArg(options, "i");
        String jStr = getRequiredArg(options, "j");
        
        int i = Integer.parseInt(iStr);
        int j = Integer.parseInt(jStr);
        
        if (i < 0 || i >= universeSize || j < 0 || j >= universeSize) {
            handleError("Indices out of bounds", null);
            return;
        }
        
        boolean result = relation.isRelated(i, j);
        
        handleSuccess("{\"command\":\"is_related\",\"i\":" + i + ",\"j\":" + j + ",\"status\":" + result + "}");
    }
    
    /**
     * Handle the universe_size command.
     */
    private void handleUniverseSize(Map<String, String> options) throws Exception {
        if (relation == null) {
            handleError("No relation created. Use 'create' first.", null);
            return;
        }
        
        int size = relation.universeSize();
        
        handleSuccess("{\"command\":\"universe_size\",\"status\":" + size + "}");
    }
    
    /**
     * Handle the get_pairs command.
     */
    private void handleGetPairs(Map<String, String> options) throws Exception {
        if (relation == null) {
            handleError("No relation created. Use 'create' first.", null);
            return;
        }
        
        NavigableSet<IntArray> pairs = relation.getPairs();
        List<String> pairStrings = new ArrayList<>();
        
        for (IntArray pair : pairs) {
            pairStrings.add("[" + pair.get(0) + "," + pair.get(1) + "]");
        }
        
        StringBuilder json = new StringBuilder();
        json.append("{\"command\":\"get_pairs\",\"pairs\":[");
        for (int i = 0; i < pairStrings.size(); i++) {
            if (i > 0) json.append(",");
            json.append("\"").append(pairStrings.get(i)).append("\"");
        }
        json.append("],\"status\":").append(pairStrings.size()).append("}");
        handleSuccess(json.toString());
    }
    
    /**
     * Handle the compose command.
     */
    private void handleCompose(Map<String, String> options) throws Exception {
        if (relation == null) {
            handleError("No relation created. Use 'create' first.", null);
            return;
        }
        
        String otherPairsStr = getRequiredArg(options, "other_pairs");
        String[] pairStrings = otherPairsStr.split(";");
        
        BasicBinaryRelation other = new BasicBinaryRelation(universeSize);
        
        for (String pairStr : pairStrings) {
            if (pairStr.trim().isEmpty()) continue;
            
            // Parse pair in format "[i,j]"
            pairStr = pairStr.trim();
            if (!pairStr.startsWith("[") || !pairStr.endsWith("]")) {
                handleError("Invalid pair format: " + pairStr, null);
                return;
            }
            
            String content = pairStr.substring(1, pairStr.length() - 1);
            String[] parts = content.split(",");
            
            if (parts.length != 2) {
                handleError("Invalid pair format: " + pairStr, null);
                return;
            }
            
            int i = Integer.parseInt(parts[0].trim());
            int j = Integer.parseInt(parts[1].trim());
            
            if (i < 0 || i >= universeSize || j < 0 || j >= universeSize) {
                handleError("Indices out of bounds in pair: " + pairStr, null);
                return;
            }
            
            other.add(i, j);
        }
        
        BinaryRelation composition = relation.compose(other);
        NavigableSet<IntArray> resultPairs = composition.getPairs();
        List<String> resultPairStrings = new ArrayList<>();
        
        for (IntArray pair : resultPairs) {
            resultPairStrings.add("[" + pair.get(0) + "," + pair.get(1) + "]");
        }
        
        StringBuilder json = new StringBuilder();
        json.append("{\"command\":\"compose\",\"result_pairs\":[");
        for (int i = 0; i < resultPairStrings.size(); i++) {
            if (i > 0) json.append(",");
            json.append("\"").append(resultPairStrings.get(i)).append("\"");
        }
        json.append("],\"status\":").append(resultPairStrings.size()).append("}");
        handleSuccess(json.toString());
    }
    
    /**
     * Handle the is_reflexive command.
     */
    private void handleIsReflexive(Map<String, String> options) throws Exception {
        if (relation == null) {
            handleError("No relation created. Use 'create' first.", null);
            return;
        }
        
        boolean result = relation.isReflexive();
        
        handleSuccess("{\"command\":\"is_reflexive\",\"status\":" + result + "}");
    }
    
    /**
     * Handle the is_symmetric command.
     */
    private void handleIsSymmetric(Map<String, String> options) throws Exception {
        if (relation == null) {
            handleError("No relation created. Use 'create' first.", null);
            return;
        }
        
        boolean result = relation.isSymmetric();
        
        handleSuccess("{\"command\":\"is_symmetric\",\"status\":" + result + "}");
    }
    
    /**
     * Handle the identity command.
     */
    private void handleIdentity(Map<String, String> options) throws Exception {
        String sizeStr = getRequiredArg(options, "size");
        int size = Integer.parseInt(sizeStr);
        
        if (size <= 0) {
            handleError("Size must be positive", null);
            return;
        }
        
        BinaryRelation identity = BasicBinaryRelation.identity(size);
        NavigableSet<IntArray> pairs = identity.getPairs();
        List<String> pairStrings = new ArrayList<>();
        
        for (IntArray pair : pairs) {
            pairStrings.add("[" + pair.get(0) + "," + pair.get(1) + "]");
        }
        
        StringBuilder json = new StringBuilder();
        json.append("{\"command\":\"identity\",\"size\":").append(size).append(",\"pairs\":[");
        for (int i = 0; i < pairStrings.size(); i++) {
            if (i > 0) json.append(",");
            json.append("\"").append(pairStrings.get(i)).append("\"");
        }
        json.append("],\"status\":").append(pairStrings.size()).append("}");
        handleSuccess(json.toString());
    }
    
    /**
     * Handle the test command.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Create a test relation
        relation = new BasicBinaryRelation(3);
        universeSize = 3;
        
        // Add some test pairs
        relation.add(0, 1);
        relation.add(1, 2);
        relation.add(0, 0);
        relation.add(1, 1);
        relation.add(2, 2);
        
        // Test various operations
        boolean isRelated01 = relation.isRelated(0, 1);
        boolean isRelated12 = relation.isRelated(1, 2);
        boolean isRelated02 = relation.isRelated(0, 2);
        boolean isReflexive = relation.isReflexive();
        boolean isSymmetric = relation.isSymmetric();
        
        NavigableSet<IntArray> pairs = relation.getPairs();
        List<String> pairStrings = new ArrayList<>();
        
        for (IntArray pair : pairs) {
            pairStrings.add("[" + pair.get(0) + "," + pair.get(1) + "]");
        }
        
        StringBuilder json = new StringBuilder();
        json.append("{\"command\":\"test\",\"is_related_01\":").append(isRelated01);
        json.append(",\"is_related_12\":").append(isRelated12);
        json.append(",\"is_related_02\":").append(isRelated02);
        json.append(",\"is_reflexive\":").append(isReflexive);
        json.append(",\"is_symmetric\":").append(isSymmetric);
        json.append(",\"pairs\":[");
        for (int i = 0; i < pairStrings.size(); i++) {
            if (i > 0) json.append(",");
            json.append("\"").append(pairStrings.get(i)).append("\"");
        }
        json.append("],\"status\":\"test_completed\"}");
        handleSuccess(json.toString());
    }
    
    /**
     * Override handleSuccess to output JSON directly for test compatibility.
     */
    @Override
    protected void handleSuccess(Object data) {
        if (data instanceof String) {
            System.out.println((String) data);
        } else {
            super.handleSuccess(data);
        }
    }
    
    /**
     * Show usage information for the BasicBinaryRelation wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create --size 5",
            "add --i 0 --j 1",
            "is_related --i 0 --j 1",
            "universe_size",
            "get_pairs",
            "compose --other_pairs \"[0,1];[1,2]\"",
            "is_reflexive",
            "is_symmetric",
            "identity --size 3",
            "test"
        };
        
        showUsage("BasicBinaryRelation", 
                 "CLI wrapper for org.uacalc.alg.conlat.BasicBinaryRelation operations", 
                 examples);
    }
}
