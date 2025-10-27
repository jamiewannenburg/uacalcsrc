/* AlgebraWriterWrapper.java - CLI wrapper for org.uacalc.io.AlgebraWriter
 * 
 * This wrapper exposes all public methods of the AlgebraWriter class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.io;

import java.io.*;
import java.util.*;

import org.uacalc.io.AlgebraWriter;
import org.uacalc.alg.SmallAlgebra;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the AlgebraWriter class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class AlgebraWriterWrapper extends WrapperBase {
    
    /**
     * Main entry point for the AlgebraWriter CLI wrapper.
     */
    public static void main(String[] args) {
        AlgebraWriterWrapper wrapper = new AlgebraWriterWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("AlgebraWriter wrapper failed", e);
        }
    }
    
    /**
     * Run the AlgebraWriter CLI wrapper with the given arguments.
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
                
            case "write-algebra-xml":
                handleWriteAlgebraXML(options);
                break;
                
            case "write-algebra":
                handleWriteAlgebra(options);
                break;
                
            case "write-basic-algebra":
                handleWriteBasicAlgebra(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Write complete algebra XML to a file.
     */
    private void handleWriteAlgebraXML(Map<String, String> options) throws Exception {
        String algebraFile = getRequiredArg(options, "algebra-file");
        String outputFile = getRequiredArg(options, "output-file");
        
        // Read the algebra from file
        org.uacalc.io.AlgebraReader reader = new org.uacalc.io.AlgebraReader(algebraFile);
        SmallAlgebra algebra = reader.readAlgebraFile();
        
        // Write the algebra XML
        AlgebraWriter writer = new AlgebraWriter(algebra, outputFile);
        writer.writeAlgebraXML();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "write-algebra-xml");
        result.put("input_file", algebraFile);
        result.put("output_file", outputFile);
        result.put("algebra_name", algebra.getName());
        result.put("algebra_cardinality", algebra.cardinality());
        result.put("algebra_type", algebra.algebraType().toString());
        result.put("num_operations", algebra.operations().size());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Write algebra XML to a file.
     */
    private void handleWriteAlgebra(Map<String, String> options) throws Exception {
        String algebraFile = getRequiredArg(options, "algebra-file");
        String outputFile = getRequiredArg(options, "output-file");
        
        // Read the algebra from file
        org.uacalc.io.AlgebraReader reader = new org.uacalc.io.AlgebraReader(algebraFile);
        SmallAlgebra algebra = reader.readAlgebraFile();
        
        // Write the algebra XML
        AlgebraWriter writer = new AlgebraWriter(algebra, outputFile);
        writer.writeAlgebra();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "write-algebra");
        result.put("input_file", algebraFile);
        result.put("output_file", outputFile);
        result.put("algebra_name", algebra.getName());
        result.put("algebra_cardinality", algebra.cardinality());
        result.put("algebra_type", algebra.algebraType().toString());
        result.put("num_operations", algebra.operations().size());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Write basic algebra XML to a file.
     */
    private void handleWriteBasicAlgebra(Map<String, String> options) throws Exception {
        String algebraFile = getRequiredArg(options, "algebra-file");
        String outputFile = getRequiredArg(options, "output-file");
        
        // Read the algebra from file
        org.uacalc.io.AlgebraReader reader = new org.uacalc.io.AlgebraReader(algebraFile);
        SmallAlgebra algebra = reader.readAlgebraFile();
        
        // Write the basic algebra XML
        AlgebraWriter writer = new AlgebraWriter(algebra, outputFile);
        writer.writeBasicAlgebra();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "write-basic-algebra");
        result.put("input_file", algebraFile);
        result.put("output_file", outputFile);
        result.put("algebra_name", algebra.getName());
        result.put("algebra_cardinality", algebra.cardinality());
        result.put("algebra_type", algebra.algebraType().toString());
        result.put("num_operations", algebra.operations().size());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Run basic tests of the AlgebraWriter functionality.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Test writing a simple algebra file
        String testInputFile = "resources/algebras/lat2.ua";
        String testOutputFile = "test_output.xml";
        
        // Read the algebra from file
        org.uacalc.io.AlgebraReader reader = new org.uacalc.io.AlgebraReader(testInputFile);
        SmallAlgebra algebra = reader.readAlgebraFile();
        
        // Write the algebra XML
        AlgebraWriter writer = new AlgebraWriter(algebra, testOutputFile);
        writer.writeAlgebraXML();
        
        // Check if output file was created
        File outputFile = new File(testOutputFile);
        boolean fileCreated = outputFile.exists();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test");
        result.put("test_input_file", testInputFile);
        result.put("test_output_file", testOutputFile);
        result.put("algebra_name", algebra.getName());
        result.put("algebra_cardinality", algebra.cardinality());
        result.put("num_operations", algebra.operations().size());
        result.put("output_file_created", fileCreated);
        result.put("output_file_size", fileCreated ? outputFile.length() : 0);
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the AlgebraWriter wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "write-algebra-xml --algebra-file path/to/input.ua --output-file path/to/output.xml",
            "write-algebra --algebra-file path/to/input.ua --output-file path/to/output.xml",
            "write-basic-algebra --algebra-file path/to/input.ua --output-file path/to/output.xml",
            "test"
        };
        
        showUsage("AlgebraWriter", 
                 "CLI wrapper for org.uacalc.io.AlgebraWriter operations", 
                 examples);
    }
}
