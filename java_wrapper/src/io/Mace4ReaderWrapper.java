/* Mace4ReaderWrapper.java - CLI wrapper for org.uacalc.io.Mace4Reader
 * 
 * This wrapper exposes all public methods of the Mace4Reader class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.io;

import java.util.*;
import java.io.*;
import org.uacalc.io.Mace4Reader;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Mace4Reader class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class Mace4ReaderWrapper extends WrapperBase {
    
    private Mace4Reader reader;
    private String inputData;
    
    /**
     * Main entry point for the Mace4Reader CLI wrapper.
     */
    public static void main(String[] args) {
        Mace4ReaderWrapper wrapper = new Mace4ReaderWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Mace4Reader wrapper failed", e);
        }
    }
    
    /**
     * Run the Mace4Reader CLI wrapper with the given arguments.
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
                
            case "is_ordinary_character":
                handleIsOrdinaryCharacter(options);
                break;
                
            case "is_special_character":
                handleIsSpecialCharacter(options);
                break;
                
            case "parse_algebra":
                handleParseAlgebra(options);
                break;
                
            case "parse_algebra_list":
                handleParseAlgebraList(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the is_ordinary_character command.
     */
    private void handleIsOrdinaryCharacter(Map<String, String> options) throws Exception {
        String character = getRequiredArg(options, "character");
        if (character.length() != 1) {
            handleError("Character must be a single character", null);
            return;
        }
        
        char c = character.charAt(0);
        boolean result = Mace4Reader.isOrdinaryCharacter(c);
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("command", "is_ordinary_character");
        resultMap.put("character", character);
        resultMap.put("status", result);
        handleSuccess(resultMap);
    }
    
    /**
     * Handle the is_special_character command.
     */
    private void handleIsSpecialCharacter(Map<String, String> options) throws Exception {
        String character = getRequiredArg(options, "character");
        if (character.length() != 1) {
            handleError("Character must be a single character", null);
            return;
        }
        
        char c = character.charAt(0);
        boolean result = Mace4Reader.isSpecialCharacter(c);
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("command", "is_special_character");
        resultMap.put("character", character);
        resultMap.put("status", result);
        handleSuccess(resultMap);
    }
    
    /**
     * Handle the parse_algebra command.
     */
    private void handleParseAlgebra(Map<String, String> options) throws Exception {
        InputStream stream;
        
        if (options.containsKey("file")) {
            // Read from file
            String filePath = getRequiredArg(options, "file");
            stream = new FileInputStream(filePath);
        } else if (options.containsKey("input")) {
            // Read from string input
            String input = getRequiredArg(options, "input");
            stream = new ByteArrayInputStream(input.getBytes("UTF-8"));
        } else {
            handleError("Either --file or --input argument is required", null);
            return;
        }
        
        try {
            Mace4Reader reader = new Mace4Reader(stream);
            
            org.uacalc.alg.SmallAlgebra algebra = reader.parseAlgebra();
            
            if (algebra == null) {
                Map<String, Object> resultMap = new HashMap<>();
                resultMap.put("command", "parse_algebra");
                resultMap.put("status", null);
                handleSuccess(resultMap);
            } else {
                Map<String, Object> statusMap = new HashMap<>();
                statusMap.put("name", algebra.getName());
                statusMap.put("cardinality", algebra.cardinality());
                statusMap.put("operations_count", algebra.operations().size());
                
                Map<String, Object> resultMap = new HashMap<>();
                resultMap.put("command", "parse_algebra");
                resultMap.put("status", statusMap);
                handleSuccess(resultMap);
            }
        } catch (Exception e) {
            handleError("Failed to parse algebra: " + e.getMessage(), e);
        } finally {
            stream.close();
        }
    }
    
    /**
     * Handle the parse_algebra_list command.
     */
    private void handleParseAlgebraList(Map<String, String> options) throws Exception {
        InputStream stream;
        
        if (options.containsKey("file")) {
            // Read from file
            String filePath = getRequiredArg(options, "file");
            stream = new FileInputStream(filePath);
        } else if (options.containsKey("input")) {
            // Read from string input
            String input = getRequiredArg(options, "input");
            stream = new ByteArrayInputStream(input.getBytes("UTF-8"));
        } else {
            handleError("Either --file or --input argument is required", null);
            return;
        }
        
        try {
            Mace4Reader reader = new Mace4Reader(stream);
            
            List<org.uacalc.alg.SmallAlgebra> algebras = reader.parseAlgebraList();
            
            List<Map<String, Object>> algebraData = new ArrayList<>();
            for (org.uacalc.alg.SmallAlgebra algebra : algebras) {
                Map<String, Object> algInfo = new HashMap<>();
                algInfo.put("name", algebra.getName());
                algInfo.put("cardinality", algebra.cardinality());
                algInfo.put("operations_count", algebra.operations().size());
                algebraData.add(algInfo);
            }
            
            Map<String, Object> resultMap = new HashMap<>();
            resultMap.put("command", "parse_algebra_list");
            resultMap.put("status", algebraData);
            handleSuccess(resultMap);
        } catch (Exception e) {
            handleError("Failed to parse algebra list: " + e.getMessage(), e);
        } finally {
            stream.close();
        }
    }
    
    /**
     * Handle the test command.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        Map<String, Object> results = new HashMap<>();
        
        // Test is_ordinary_character
        results.put("is_ordinary_character_a", Mace4Reader.isOrdinaryCharacter('a'));
        results.put("is_ordinary_character_1", Mace4Reader.isOrdinaryCharacter('1'));
        results.put("is_ordinary_character_dollar", Mace4Reader.isOrdinaryCharacter('$'));
        results.put("is_ordinary_character_underscore", Mace4Reader.isOrdinaryCharacter('_'));
        
        // Test is_special_character
        results.put("is_special_character_plus", Mace4Reader.isSpecialCharacter('+'));
        results.put("is_special_character_minus", Mace4Reader.isSpecialCharacter('-'));
        results.put("is_special_character_a", Mace4Reader.isSpecialCharacter('a'));
        
        // Test with sample Mace4 input
        String sampleInput = "interpretation(2, [number=1], [function(f, (_,_), [0,1,1,0])]).";
        try {
            InputStream stream = new ByteArrayInputStream(sampleInput.getBytes("UTF-8"));
            Mace4Reader reader = new Mace4Reader(stream);
            org.uacalc.alg.SmallAlgebra algebra = reader.parseAlgebra();
            
            if (algebra != null) {
                results.put("parse_sample_success", true);
                results.put("sample_algebra_name", algebra.getName());
                results.put("sample_algebra_cardinality", algebra.cardinality());
                results.put("sample_algebra_operations_count", algebra.operations().size());
            } else {
                results.put("parse_sample_success", false);
            }
        } catch (Exception e) {
            results.put("parse_sample_success", false);
            results.put("parse_sample_error", e.getMessage());
        }
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("command", "test");
        resultMap.put("status", results);
        handleSuccess(resultMap);
    }
    
    /**
     * Show usage information for the Mace4Reader wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "is_ordinary_character --character a",
            "is_special_character --character +",
            "parse_algebra --file resources/mace4/KR-8.model",
            "parse_algebra --input \"interpretation(2, [number=1], [function(f, (_,_), [0,1,1,0])]).\"",
            "parse_algebra_list --file resources/mace4/KR-8.model",
            "test"
        };
        
        showUsage("Mace4Reader", 
                 "CLI wrapper for org.uacalc.io.Mace4Reader operations", 
                 examples);
    }
}
