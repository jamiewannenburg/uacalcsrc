/* SubtraceWrapper.java - CLI wrapper for org.uacalc.alg.conlat.Subtrace
 * 
 * This wrapper exposes all public methods of the Subtrace class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg.conlat;

import java.util.*;
import org.uacalc.alg.conlat.Subtrace;
import org.uacalc.util.IntArray;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Subtrace class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class SubtraceWrapper extends WrapperBase {
    
    private Subtrace subtrace;
    
    /**
     * Main entry point for the Subtrace CLI wrapper.
     */
    public static void main(String[] args) {
        SubtraceWrapper wrapper = new SubtraceWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Subtrace wrapper failed", e);
        }
    }
    
    /**
     * Run the Subtrace CLI wrapper with the given arguments.
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
                
            case "create_with_type":
                handleCreateWithType(options);
                break;
                
            case "first":
                handleFirst(options);
                break;
                
            case "second":
                handleSecond(options);
                break;
                
            case "type":
                handleType(options);
                break;
                
            case "has_involution":
                handleHasInvolution(options);
                break;
                
            case "set_type":
                handleSetType(options);
                break;
                
            case "set_subtrace_universe":
                handleSetSubtraceUniverse(options);
                break;
                
            case "get_subtrace_universe":
                handleGetSubtraceUniverse(options);
                break;
                
            case "set_matrix_universe":
                handleSetMatrixUniverse(options);
                break;
                
            case "get_matrix_universe":
                handleGetMatrixUniverse(options);
                break;
                
            case "to_string_brief":
                handleToStringBrief(options);
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
        String aStr = getRequiredArg(options, "a");
        String bStr = getRequiredArg(options, "b");
        String invStr = getRequiredArg(options, "has_involution");
        
        int a = Integer.parseInt(aStr);
        int b = Integer.parseInt(bStr);
        boolean hasInvolution = Boolean.parseBoolean(invStr);
        
        subtrace = new Subtrace(a, b, hasInvolution);
        
        handleSuccess("{\"command\":\"create\",\"a\":" + a + ",\"b\":" + b + 
                     ",\"has_involution\":" + hasInvolution + ",\"status\":\"created\"}");
    }
    
    /**
     * Handle the create_with_type command.
     */
    private void handleCreateWithType(Map<String, String> options) throws Exception {
        String aStr = getRequiredArg(options, "a");
        String bStr = getRequiredArg(options, "b");
        String invStr = getRequiredArg(options, "has_involution");
        String typeStr = getRequiredArg(options, "type");
        
        int a = Integer.parseInt(aStr);
        int b = Integer.parseInt(bStr);
        boolean hasInvolution = Boolean.parseBoolean(invStr);
        int type = Integer.parseInt(typeStr);
        
        subtrace = new Subtrace(a, b, hasInvolution, type);
        
        handleSuccess("{\"command\":\"create_with_type\",\"a\":" + a + ",\"b\":" + b + 
                     ",\"has_involution\":" + hasInvolution + ",\"type\":" + type + ",\"status\":\"created\"}");
    }
    
    /**
     * Handle the first command.
     */
    private void handleFirst(Map<String, String> options) throws Exception {
        if (subtrace == null) {
            handleError("No subtrace created. Use 'create' first.", null);
            return;
        }
        
        int result = subtrace.first();
        handleSuccess("{\"command\":\"first\",\"status\":" + result + "}");
    }
    
    /**
     * Handle the second command.
     */
    private void handleSecond(Map<String, String> options) throws Exception {
        if (subtrace == null) {
            handleError("No subtrace created. Use 'create' first.", null);
            return;
        }
        
        int result = subtrace.second();
        handleSuccess("{\"command\":\"second\",\"status\":" + result + "}");
    }
    
    /**
     * Handle the type command.
     */
    private void handleType(Map<String, String> options) throws Exception {
        if (subtrace == null) {
            handleError("No subtrace created. Use 'create' first.", null);
            return;
        }
        
        int result = subtrace.type();
        handleSuccess("{\"command\":\"type\",\"status\":" + result + "}");
    }
    
    /**
     * Handle the has_involution command.
     */
    private void handleHasInvolution(Map<String, String> options) throws Exception {
        if (subtrace == null) {
            handleError("No subtrace created. Use 'create' first.", null);
            return;
        }
        
        boolean result = subtrace.hasInvolution();
        handleSuccess("{\"command\":\"has_involution\",\"status\":" + result + "}");
    }
    
    /**
     * Handle the set_type command.
     */
    private void handleSetType(Map<String, String> options) throws Exception {
        if (subtrace == null) {
            handleError("No subtrace created. Use 'create' first.", null);
            return;
        }
        
        String typeStr = getRequiredArg(options, "type");
        int type = Integer.parseInt(typeStr);
        
        subtrace.setType(type);
        
        handleSuccess("{\"command\":\"set_type\",\"type\":" + type + ",\"status\":\"set\"}");
    }
    
    /**
     * Handle the set_subtrace_universe command.
     */
    private void handleSetSubtraceUniverse(Map<String, String> options) throws Exception {
        if (subtrace == null) {
            handleError("No subtrace created. Use 'create' first.", null);
            return;
        }
        
        String pairsStr = getRequiredArg(options, "pairs");
        List<IntArray> universe = new ArrayList<>();
        
        // Parse pairs in format "[1,2];[3,4];..."
        String[] pairStrings = pairsStr.split(";");
        
        for (String pairStr : pairStrings) {
            if (pairStr.trim().isEmpty()) continue;
            
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
            
            universe.add(new IntArray(new int[]{i, j}));
        }
        
        subtrace.setSubtraceUniverse(universe);
        
        handleSuccess("{\"command\":\"set_subtrace_universe\",\"size\":" + universe.size() + ",\"status\":\"set\"}");
    }
    
    /**
     * Handle the get_subtrace_universe command.
     */
    private void handleGetSubtraceUniverse(Map<String, String> options) throws Exception {
        if (subtrace == null) {
            handleError("No subtrace created. Use 'create' first.", null);
            return;
        }
        
        List<IntArray> universe = subtrace.getSubtraceUniverse();
        
        if (universe == null) {
            handleSuccess("{\"command\":\"get_subtrace_universe\",\"status\":null}");
        } else {
            List<String> pairStrings = new ArrayList<>();
            for (IntArray pair : universe) {
                pairStrings.add("[" + pair.get(0) + "," + pair.get(1) + "]");
            }
            
            StringBuilder json = new StringBuilder();
            json.append("{\"command\":\"get_subtrace_universe\",\"pairs\":[");
            for (int i = 0; i < pairStrings.size(); i++) {
                if (i > 0) json.append(",");
                json.append("\"").append(pairStrings.get(i)).append("\"");
            }
            json.append("],\"status\":").append(pairStrings.size()).append("}");
            handleSuccess(json.toString());
        }
    }
    
    /**
     * Handle the set_matrix_universe command.
     */
    private void handleSetMatrixUniverse(Map<String, String> options) throws Exception {
        if (subtrace == null) {
            handleError("No subtrace created. Use 'create' first.", null);
            return;
        }
        
        String tuplesStr = getRequiredArg(options, "tuples");
        List<IntArray> universe = new ArrayList<>();
        
        // Parse tuples in format "[1,2,3,4];[5,6,7,8];..."
        String[] tupleStrings = tuplesStr.split(";");
        
        for (String tupleStr : tupleStrings) {
            if (tupleStr.trim().isEmpty()) continue;
            
            tupleStr = tupleStr.trim();
            if (!tupleStr.startsWith("[") || !tupleStr.endsWith("]")) {
                handleError("Invalid tuple format: " + tupleStr, null);
                return;
            }
            
            String content = tupleStr.substring(1, tupleStr.length() - 1);
            String[] parts = content.split(",");
            
            if (parts.length != 4) {
                handleError("Invalid tuple format (must have 4 elements): " + tupleStr, null);
                return;
            }
            
            int[] tuple = new int[4];
            for (int i = 0; i < 4; i++) {
                tuple[i] = Integer.parseInt(parts[i].trim());
            }
            
            universe.add(new IntArray(tuple));
        }
        
        subtrace.setMatrixUniverse(universe);
        
        handleSuccess("{\"command\":\"set_matrix_universe\",\"size\":" + universe.size() + ",\"status\":\"set\"}");
    }
    
    /**
     * Handle the get_matrix_universe command.
     */
    private void handleGetMatrixUniverse(Map<String, String> options) throws Exception {
        if (subtrace == null) {
            handleError("No subtrace created. Use 'create' first.", null);
            return;
        }
        
        List<IntArray> universe = subtrace.getMatrixUniverse();
        
        if (universe == null) {
            handleSuccess("{\"command\":\"get_matrix_universe\",\"status\":null}");
        } else {
            List<String> tupleStrings = new ArrayList<>();
            for (IntArray tuple : universe) {
                StringBuilder sb = new StringBuilder();
                sb.append("[");
                for (int i = 0; i < tuple.universeSize(); i++) {
                    if (i > 0) sb.append(",");
                    sb.append(tuple.get(i));
                }
                sb.append("]");
                tupleStrings.add(sb.toString());
            }
            
            StringBuilder json = new StringBuilder();
            json.append("{\"command\":\"get_matrix_universe\",\"tuples\":[");
            for (int i = 0; i < tupleStrings.size(); i++) {
                if (i > 0) json.append(",");
                json.append("\"").append(tupleStrings.get(i)).append("\"");
            }
            json.append("],\"status\":").append(tupleStrings.size()).append("}");
            handleSuccess(json.toString());
        }
    }
    
    /**
     * Handle the to_string_brief command.
     */
    private void handleToStringBrief(Map<String, String> options) throws Exception {
        if (subtrace == null) {
            handleError("No subtrace created. Use 'create' first.", null);
            return;
        }
        
        String briefStr = getOptionalArg(options, "brief", "false");
        boolean brief = Boolean.parseBoolean(briefStr);
        
        String result = subtrace.toString(brief);
        
        handleSuccess("{\"command\":\"to_string_brief\",\"brief\":" + brief + 
                     ",\"result\":\"" + result + "\",\"status\":\"" + result + "\"}");
    }
    
    /**
     * Handle the test command.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Create test subtrace
        subtrace = new Subtrace(1, 2, true, 3);
        
        int first = subtrace.first();
        int second = subtrace.second();
        int type = subtrace.type();
        boolean hasInvolution = subtrace.hasInvolution();
        String toStringResult = subtrace.toString();
        String briefResult = subtrace.toString(true);
        
        // Test universe operations
        List<IntArray> testUniverse = new ArrayList<>();
        testUniverse.add(new IntArray(new int[]{1, 1}));
        testUniverse.add(new IntArray(new int[]{1, 2}));
        testUniverse.add(new IntArray(new int[]{2, 2}));
        
        subtrace.setSubtraceUniverse(testUniverse);
        List<IntArray> retrievedUniverse = subtrace.getSubtraceUniverse();
        
        StringBuilder json = new StringBuilder();
        json.append("{\"command\":\"test\",\"first\":").append(first);
        json.append(",\"second\":").append(second);
        json.append(",\"type\":").append(type);
        json.append(",\"has_involution\":").append(hasInvolution);
        json.append(",\"to_string\":\"").append(toStringResult).append("\"");
        json.append(",\"brief_string\":\"").append(briefResult).append("\"");
        json.append(",\"universe_size\":").append(retrievedUniverse != null ? retrievedUniverse.size() : 0);
        json.append(",\"status\":\"test_completed\"}");
        
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
     * Show usage information for the Subtrace wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create --a 1 --b 2 --has_involution true",
            "create_with_type --a 1 --b 2 --has_involution true --type 3",
            "first",
            "second", 
            "type",
            "has_involution",
            "set_type --type 5",
            "set_subtrace_universe --pairs \"[1,1];[1,2];[2,2]\"",
            "get_subtrace_universe",
            "set_matrix_universe --tuples \"[1,1,2,2];[1,2,1,2]\"",
            "get_matrix_universe",
            "to_string_brief --brief true",
            "test"
        };
        
        showUsage("Subtrace", 
                 "CLI wrapper for org.uacalc.alg.conlat.Subtrace operations", 
                 examples);
    }
}
