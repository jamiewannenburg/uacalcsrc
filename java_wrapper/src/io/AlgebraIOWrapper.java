/* AlgebraIOWrapper.java - CLI wrapper for org.uacalc.io.AlgebraIO
 * 
 * This wrapper exposes all public methods of the AlgebraIO class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.io;

import java.io.*;
import java.util.*;
import org.uacalc.io.AlgebraIO;
import org.uacalc.alg.SmallAlgebra;
import org.uacalc.alg.op.Operation;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the AlgebraIO class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class AlgebraIOWrapper extends WrapperBase {
    
    /**
     * Main entry point for the AlgebraIO CLI wrapper.
     */
    public static void main(String[] args) {
        AlgebraIOWrapper wrapper = new AlgebraIOWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("AlgebraIO wrapper failed", e);
        }
    }
    
    /**
     * Run the AlgebraIO CLI wrapper with the given arguments.
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
                
            case "parse_line":
                handleParseLine(options);
                break;
                
            case "read_algebra_file":
                handleReadAlgebraFile(options);
                break;
                
            case "read_algebra_from_stream":
                handleReadAlgebraFromStream(options);
                break;
                
            case "read_algebra_list_file":
                handleReadAlgebraListFile(options);
                break;
                
            case "read_algebra_list_from_stream":
                handleReadAlgebraListFromStream(options);
                break;
                
            case "convert_to_xml":
                handleConvertToXML(options);
                break;
                
            case "write_algebra_file":
                handleWriteAlgebraFile(options);
                break;
                
            case "write_algebra_file_with_style":
                handleWriteAlgebraFileWithStyle(options);
                break;
                
            case "read_projective_plane":
                handleReadProjectivePlane(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the parse_line command.
     */
    private void handleParseLine(Map<String, String> options) throws Exception {
        String line = getRequiredArg(options, "line");
        
        int result = AlgebraIO.parseLine(line);
        
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("command", "parse_line");
        response.put("line", line);
        response.put("status", result);
        
        handleSuccess(response);
    }
    
    /**
     * Handle the read_algebra_file command.
     */
    private void handleReadAlgebraFile(Map<String, String> options) throws Exception {
        String path = getRequiredArg(options, "path");
        
        SmallAlgebra alg = AlgebraIO.readAlgebraFile(path);
        
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("command", "read_algebra_file");
        response.put("path", path);
        response.put("name", alg.getName());
        response.put("cardinality", alg.cardinality());
        response.put("num_operations", alg.operations().size());
        
        handleSuccess(response);
    }
    
    /**
     * Handle the read_algebra_from_stream command.
     */
    private void handleReadAlgebraFromStream(Map<String, String> options) throws Exception {
        String path = getRequiredArg(options, "path");
        
        FileInputStream fis = new FileInputStream(path);
        SmallAlgebra alg = AlgebraIO.readAlgebraFromStream(fis);
        fis.close();
        
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("command", "read_algebra_from_stream");
        response.put("name", alg.getName());
        response.put("cardinality", alg.cardinality());
        response.put("num_operations", alg.operations().size());
        
        handleSuccess(response);
    }
    
    /**
     * Handle the read_algebra_list_file command.
     */
    private void handleReadAlgebraListFile(Map<String, String> options) throws Exception {
        String path = getRequiredArg(options, "path");
        
        List<SmallAlgebra> algebras = AlgebraIO.readAlgebraListFile(path);
        
        List<Map<String, Object>> algebrasInfo = new ArrayList<>();
        for (SmallAlgebra alg : algebras) {
            Map<String, Object> algInfo = new LinkedHashMap<>();
            algInfo.put("name", alg.getName());
            algInfo.put("cardinality", alg.cardinality());
            algInfo.put("num_operations", alg.operations().size());
            algebrasInfo.add(algInfo);
        }
        
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("command", "read_algebra_list_file");
        response.put("path", path);
        response.put("count", algebras.size());
        response.put("algebras", algebrasInfo);
        
        handleSuccess(response);
    }
    
    /**
     * Handle the read_algebra_list_from_stream command.
     */
    private void handleReadAlgebraListFromStream(Map<String, String> options) throws Exception {
        String path = getRequiredArg(options, "path");
        
        FileInputStream fis = new FileInputStream(path);
        SmallAlgebra alg = AlgebraIO.readAlgebraListFromStream(fis);
        fis.close();
        
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("command", "read_algebra_list_from_stream");
        response.put("name", alg.getName());
        response.put("cardinality", alg.cardinality());
        response.put("num_operations", alg.operations().size());
        
        handleSuccess(response);
    }
    
    /**
     * Handle the convert_to_xml command.
     */
    private void handleConvertToXML(Map<String, String> options) throws Exception {
        String path = getRequiredArg(options, "path");
        
        AlgebraIO.convertToXML(path);
        
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("command", "convert_to_xml");
        response.put("path", path);
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle the write_algebra_file command.
     */
    private void handleWriteAlgebraFile(Map<String, String> options) throws Exception {
        String inputPath = getRequiredArg(options, "input_path");
        String outputPath = getRequiredArg(options, "output_path");
        
        // Read the algebra first
        SmallAlgebra alg = AlgebraIO.readAlgebraFile(inputPath);
        
        // Write it to the output file
        AlgebraIO.writeAlgebraFile(alg, outputPath);
        
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("command", "write_algebra_file");
        response.put("input_path", inputPath);
        response.put("output_path", outputPath);
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle the write_algebra_file_with_style command.
     */
    private void handleWriteAlgebraFileWithStyle(Map<String, String> options) throws Exception {
        String inputPath = getRequiredArg(options, "input_path");
        String outputPath = getRequiredArg(options, "output_path");
        boolean oldStyle = getBoolArg(options, "old_style", false);
        
        // Read the algebra first
        SmallAlgebra alg = AlgebraIO.readAlgebraFile(inputPath);
        
        // Write it to the output file
        AlgebraIO.writeAlgebraFile(alg, outputPath, oldStyle);
        
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("command", "write_algebra_file_with_style");
        response.put("input_path", inputPath);
        response.put("output_path", outputPath);
        response.put("old_style", oldStyle);
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle the read_projective_plane command.
     */
    private void handleReadProjectivePlane(Map<String, String> options) throws Exception {
        String path = getRequiredArg(options, "path");
        
        try {
            SmallAlgebra alg = AlgebraIO.readProjectivePlane(path);
            
            Map<String, Object> response = new LinkedHashMap<>();
            response.put("command", "read_projective_plane");
            response.put("path", path);
            if (alg != null) {
                response.put("name", alg.getName());
                response.put("cardinality", alg.cardinality());
                response.put("num_operations", alg.operations().size());
            } else {
                response.put("status", "null_result");
            }
            
            handleSuccess(response);
        } catch (Exception e) {
            // Expected for unimplemented functionality
            Map<String, Object> response = new LinkedHashMap<>();
            response.put("command", "read_projective_plane");
            response.put("path", path);
            response.put("status", "error");
            response.put("message", e.getMessage());
            
            handleSuccess(response);
        }
    }
    
    /**
     * Handle the test command.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("command", "test");
        
        // Test parse_line
        int parseResult = AlgebraIO.parseLine("42");
        response.put("parse_line_test", parseResult == 42);
        
        // Test parse_line with comment
        int commentResult = AlgebraIO.parseLine("% comment");
        response.put("parse_line_comment_test", commentResult == -1);
        
        // Test read_algebra_file if cyclic3.ua exists
        try {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic3.ua");
            response.put("read_algebra_file_test", alg.cardinality() == 3);
        } catch (Exception e) {
            response.put("read_algebra_file_test", "skipped: " + e.getMessage());
        }
        
        handleSuccess(response);
    }
    
    /**
     * Show usage information for the AlgebraIO wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "parse_line --line \"42\"",
            "parse_line --line \"% comment\"",
            "read_algebra_file --path \"resources/algebras/cyclic3.ua\"",
            "read_algebra_from_stream --path \"resources/algebras/cyclic3.ua\"",
            "read_algebra_list_file --path \"resources/algebras/cyclic3.ua\"",
            "convert_to_xml --path \"test.alg\"",
            "write_algebra_file --input_path \"test.ua\" --output_path \"output.xml\"",
            "write_algebra_file_with_style --input_path \"test.ua\" --output_path \"output.alg\" --old_style true",
            "read_projective_plane --path \"plane.txt\"",
            "test"
        };
        
        showUsage("AlgebraIO", 
                 "CLI wrapper for org.uacalc.io.AlgebraIO operations", 
                 examples);
    }
}

