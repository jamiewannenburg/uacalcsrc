/* AlgebraReaderWrapper.java - CLI wrapper for org.uacalc.io.AlgebraReader
 * 
 * This wrapper exposes all public methods of the AlgebraReader class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.io;

import java.io.*;
import java.util.*;
import org.xml.sax.*;
import javax.xml.parsers.*;

import org.uacalc.io.AlgebraReader;
import org.uacalc.alg.SmallAlgebra;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the AlgebraReader class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class AlgebraReaderWrapper extends WrapperBase {
    
    /**
     * Main entry point for the AlgebraReader CLI wrapper.
     */
    public static void main(String[] args) {
        AlgebraReaderWrapper wrapper = new AlgebraReaderWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("AlgebraReader wrapper failed", e);
        }
    }
    
    /**
     * Run the AlgebraReader CLI wrapper with the given arguments.
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
                
            case "read-algebra-file":
                handleReadAlgebraFile(options);
                break;
                
            case "read-algebra-from-stream":
                handleReadAlgebraFromStream(options);
                break;
                
            case "read-algebra-list-file":
                handleReadAlgebraListFile(options);
                break;
                
            case "read-algebra-list-from-stream":
                handleReadAlgebraListFromStream(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Read a single algebra from a file.
     */
    private void handleReadAlgebraFile(Map<String, String> options) throws Exception {
        String filePath = getRequiredArg(options, "file");
        
        AlgebraReader reader = new AlgebraReader(filePath);
        SmallAlgebra algebra = reader.readAlgebraFile();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "read-algebra-file");
        result.put("file", filePath);
        result.put("algebra_name", algebra.getName());
        result.put("algebra_cardinality", algebra.cardinality());
        result.put("algebra_type", algebra.algebraType().toString());
        result.put("num_operations", algebra.operations().size());
        
        handleSuccess(result);
    }
    
    /**
     * Read a single algebra from a stream.
     */
    private void handleReadAlgebraFromStream(Map<String, String> options) throws Exception {
        String data = getRequiredArg(options, "data");
        
        InputStream stream = new ByteArrayInputStream(data.getBytes("UTF-8"));
        AlgebraReader reader = new AlgebraReader(stream);
        SmallAlgebra algebra = reader.readAlgebraFromStream();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "read-algebra-from-stream");
        result.put("algebra_name", algebra.getName());
        result.put("algebra_cardinality", algebra.cardinality());
        result.put("algebra_type", algebra.algebraType().toString());
        result.put("num_operations", algebra.operations().size());
        
        handleSuccess(result);
    }
    
    /**
     * Read a list of algebras from a file.
     */
    private void handleReadAlgebraListFile(Map<String, String> options) throws Exception {
        String filePath = getRequiredArg(options, "file");
        
        AlgebraReader reader = new AlgebraReader(filePath);
        List<SmallAlgebra> algebras = reader.readAlgebraListFile();
        
        List<Map<String, Object>> algebraList = new ArrayList<>();
        for (SmallAlgebra alg : algebras) {
            Map<String, Object> algInfo = new HashMap<>();
            algInfo.put("name", alg.getName());
            algInfo.put("cardinality", alg.cardinality());
            algInfo.put("type", alg.algebraType().toString());
            algInfo.put("num_operations", alg.operations().size());
            algebraList.add(algInfo);
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "read-algebra-list-file");
        result.put("file", filePath);
        result.put("num_algebras", algebras.size());
        result.put("algebras", algebraList);
        
        handleSuccess(result);
    }
    
    /**
     * Read a list of algebras from a stream.
     */
    private void handleReadAlgebraListFromStream(Map<String, String> options) throws Exception {
        String data = getRequiredArg(options, "data");
        
        InputStream stream = new ByteArrayInputStream(data.getBytes("UTF-8"));
        AlgebraReader reader = new AlgebraReader(stream);
        List<SmallAlgebra> algebras = reader.readAlgebraListFromStream();
        
        List<Map<String, Object>> algebraList = new ArrayList<>();
        for (SmallAlgebra alg : algebras) {
            Map<String, Object> algInfo = new HashMap<>();
            algInfo.put("name", alg.getName());
            algInfo.put("cardinality", alg.cardinality());
            algInfo.put("type", alg.algebraType().toString());
            algInfo.put("num_operations", alg.operations().size());
            algebraList.add(algInfo);
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "read-algebra-list-from-stream");
        result.put("num_algebras", algebras.size());
        result.put("algebras", algebraList);
        
        handleSuccess(result);
    }
    
    /**
     * Run basic tests of the AlgebraReader functionality.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Test reading a simple algebra file
        String testFile = "resources/algebras/lat2.ua";
        
        AlgebraReader reader = new AlgebraReader(testFile);
        SmallAlgebra algebra = reader.readAlgebraFile();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test");
        result.put("test_file", testFile);
        result.put("algebra_name", algebra.getName());
        result.put("algebra_cardinality", algebra.cardinality());
        result.put("num_operations", algebra.operations().size());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the AlgebraReader wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "read-algebra-file --file path/to/file.ua",
            "read-algebra-from-stream --data '<xml>...</xml>'",
            "read-algebra-list-file --file path/to/file.ua",
            "read-algebra-list-from-stream --data '<xml>...</xml>'",
            "test"
        };
        
        showUsage("AlgebraReader", 
                 "CLI wrapper for org.uacalc.io.AlgebraReader operations", 
                 examples);
    }
}

