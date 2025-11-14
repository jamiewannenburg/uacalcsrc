/* PolinLikeAlgebraWrapper.java - CLI wrapper for org.uacalc.alg.PolinLikeAlgebra
 * 
 * This wrapper exposes public methods of the PolinLikeAlgebra class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.op.*;
import org.uacalc.io.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the PolinLikeAlgebra class that provides command-line access
 * to public methods for testing and validation purposes.
 */
public class PolinLikeAlgebraWrapper extends WrapperBase {
    
    /**
     * Main entry point for the PolinLikeAlgebra CLI wrapper.
     */
    public static void main(String[] args) {
        PolinLikeAlgebraWrapper wrapper = new PolinLikeAlgebraWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("PolinLikeAlgebra wrapper failed", e);
        }
    }
    
    /**
     * Run the PolinLikeAlgebra CLI wrapper with the given arguments.
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
                
            case "cardinality":
                handleCardinality(options);
                break;
                
            case "get_element":
                handleGetElement(options);
                break;
                
            case "element_index":
                handleElementIndex(options);
                break;
                
            case "algebra_type":
                handleAlgebraType(options);
                break;
                
            case "top_algebra_name":
                handleTopAlgebraName(options);
                break;
                
            case "bottom_algebra_name":
                handleBottomAlgebraName(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle creating a new PolinLikeAlgebra.
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "polin");
        String topAlgFile = getOptionalArg(options, "top_alg", "resources/algebras/cyclic2.ua");
        String botAlgFile = getOptionalArg(options, "bot_alg", "resources/algebras/cyclic2.ua");
        int topConstIndex = getIntArg(options, "top_const_index", 0);
        int botConstIndex = getIntArg(options, "bot_const_index", 0);
        
        // Load algebras from files
        SmallAlgebra topAlg = AlgebraIO.readAlgebraFile(topAlgFile);
        SmallAlgebra botAlg = AlgebraIO.readAlgebraFile(botAlgFile);
        
        // Create PolinLikeAlgebra with identity map (null)
        PolinLikeAlgebra polin = new PolinLikeAlgebra(name, topAlg, botAlg, null, topConstIndex, botConstIndex);
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"create\",");
        result.append("\"name\":\"").append(name).append("\",");
        result.append("\"top_alg\":\"").append(topAlgFile).append("\",");
        result.append("\"bot_alg\":\"").append(botAlgFile).append("\",");
        result.append("\"top_const_index\":").append(topConstIndex).append(",");
        result.append("\"bot_const_index\":").append(botConstIndex).append(",");
        result.append("\"cardinality\":").append(polin.cardinality()).append(",");
        result.append("\"status\":\"created\"}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle cardinality method.
     */
    private void handleCardinality(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "polin");
        String topAlgFile = getOptionalArg(options, "top_alg", "resources/algebras/cyclic2.ua");
        String botAlgFile = getOptionalArg(options, "bot_alg", "resources/algebras/cyclic2.ua");
        int topConstIndex = getIntArg(options, "top_const_index", 0);
        int botConstIndex = getIntArg(options, "bot_const_index", 0);
        
        SmallAlgebra topAlg = AlgebraIO.readAlgebraFile(topAlgFile);
        SmallAlgebra botAlg = AlgebraIO.readAlgebraFile(botAlgFile);
        PolinLikeAlgebra polin = new PolinLikeAlgebra(name, topAlg, botAlg, null, topConstIndex, botConstIndex);
        
        int card = polin.cardinality();
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"cardinality\",");
        result.append("\"status\":").append(card).append("}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle get_element method.
     */
    private void handleGetElement(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "polin");
        String topAlgFile = getOptionalArg(options, "top_alg", "resources/algebras/cyclic2.ua");
        String botAlgFile = getOptionalArg(options, "bot_alg", "resources/algebras/cyclic2.ua");
        int topConstIndex = getIntArg(options, "top_const_index", 0);
        int botConstIndex = getIntArg(options, "bot_const_index", 0);
        int index = getIntArg(options, "index", 0);
        
        SmallAlgebra topAlg = AlgebraIO.readAlgebraFile(topAlgFile);
        SmallAlgebra botAlg = AlgebraIO.readAlgebraFile(botAlgFile);
        PolinLikeAlgebra polin = new PolinLikeAlgebra(name, topAlg, botAlg, null, topConstIndex, botConstIndex);
        
        Object elem = polin.getElement(index);
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"get_element\",");
        result.append("\"index\":").append(index).append(",");
        result.append("\"status\":").append(elem).append("}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle element_index method.
     */
    private void handleElementIndex(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "polin");
        String topAlgFile = getOptionalArg(options, "top_alg", "resources/algebras/cyclic2.ua");
        String botAlgFile = getOptionalArg(options, "bot_alg", "resources/algebras/cyclic2.ua");
        int topConstIndex = getIntArg(options, "top_const_index", 0);
        int botConstIndex = getIntArg(options, "bot_const_index", 0);
        int elem = getIntArg(options, "element", 0);
        
        SmallAlgebra topAlg = AlgebraIO.readAlgebraFile(topAlgFile);
        SmallAlgebra botAlg = AlgebraIO.readAlgebraFile(botAlgFile);
        PolinLikeAlgebra polin = new PolinLikeAlgebra(name, topAlg, botAlg, null, topConstIndex, botConstIndex);
        
        int index = polin.elementIndex(elem);
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"element_index\",");
        result.append("\"element\":").append(elem).append(",");
        result.append("\"status\":").append(index).append("}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle algebra_type method.
     */
    private void handleAlgebraType(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "polin");
        String topAlgFile = getOptionalArg(options, "top_alg", "resources/algebras/cyclic2.ua");
        String botAlgFile = getOptionalArg(options, "bot_alg", "resources/algebras/cyclic2.ua");
        int topConstIndex = getIntArg(options, "top_const_index", 0);
        int botConstIndex = getIntArg(options, "bot_const_index", 0);
        
        SmallAlgebra topAlg = AlgebraIO.readAlgebraFile(topAlgFile);
        SmallAlgebra botAlg = AlgebraIO.readAlgebraFile(botAlgFile);
        PolinLikeAlgebra polin = new PolinLikeAlgebra(name, topAlg, botAlg, null, topConstIndex, botConstIndex);
        
        SmallAlgebra.AlgebraType type = polin.algebraType();
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"algebra_type\",");
        result.append("\"status\":\"").append(type).append("\"}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle top_algebra_name method.
     */
    private void handleTopAlgebraName(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "polin");
        String topAlgFile = getOptionalArg(options, "top_alg", "resources/algebras/cyclic2.ua");
        String botAlgFile = getOptionalArg(options, "bot_alg", "resources/algebras/cyclic2.ua");
        int topConstIndex = getIntArg(options, "top_const_index", 0);
        int botConstIndex = getIntArg(options, "bot_const_index", 0);
        
        SmallAlgebra topAlg = AlgebraIO.readAlgebraFile(topAlgFile);
        SmallAlgebra botAlg = AlgebraIO.readAlgebraFile(botAlgFile);
        PolinLikeAlgebra polin = new PolinLikeAlgebra(name, topAlg, botAlg, null, topConstIndex, botConstIndex);
        
        // Store top algebra name during construction (can't access protected field)
        String topName = topAlg.getName();
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"top_algebra_name\",");
        result.append("\"status\":\"").append(topName).append("\"}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle bottom_algebra_name method.
     */
    private void handleBottomAlgebraName(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "polin");
        String topAlgFile = getOptionalArg(options, "top_alg", "resources/algebras/cyclic2.ua");
        String botAlgFile = getOptionalArg(options, "bot_alg", "resources/algebras/cyclic2.ua");
        int topConstIndex = getIntArg(options, "top_const_index", 0);
        int botConstIndex = getIntArg(options, "bot_const_index", 0);
        
        SmallAlgebra topAlg = AlgebraIO.readAlgebraFile(topAlgFile);
        SmallAlgebra botAlg = AlgebraIO.readAlgebraFile(botAlgFile);
        PolinLikeAlgebra polin = new PolinLikeAlgebra(name, topAlg, botAlg, null, topConstIndex, botConstIndex);
        
        // Store bottom algebra name during construction (can't access protected field)
        String botName = botAlg.getName();
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"bottom_algebra_name\",");
        result.append("\"status\":\"").append(botName).append("\"}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Handle running basic tests.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Load algebras from files
        SmallAlgebra topAlg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua");
        SmallAlgebra botAlg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua");
        
        // Create PolinLikeAlgebra
        PolinLikeAlgebra polin = new PolinLikeAlgebra("test_polin", topAlg, botAlg, null, 0, 0);
        
        // Test basic methods
        int card = polin.cardinality();
        Object elem0 = polin.getElement(0);
        Object elem1 = polin.getElement(1);
        Object elem2 = polin.getElement(2);
        int idx0 = polin.elementIndex(0);
        int idx1 = polin.elementIndex(1);
        SmallAlgebra.AlgebraType type = polin.algebraType();
        // Store algebra names during construction (can't access protected fields)
        String topName = topAlg.getName();
        String botName = botAlg.getName();
        
        StringBuilder result = new StringBuilder();
        result.append("{\"command\":\"test\",");
        result.append("\"cardinality\":").append(card).append(",");
        result.append("\"element_0\":").append(elem0).append(",");
        result.append("\"element_1\":").append(elem1).append(",");
        result.append("\"element_2\":").append(elem2).append(",");
        result.append("\"index_0\":").append(idx0).append(",");
        result.append("\"index_1\":").append(idx1).append(",");
        result.append("\"type\":\"").append(type).append("\",");
        result.append("\"top_name\":\"").append(topName).append("\",");
        result.append("\"bot_name\":\"").append(botName).append("\",");
        result.append("\"status\":\"success\"}");
        
        handleSuccess(result.toString());
    }
    
    /**
     * Show usage information for the PolinLikeAlgebra wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create --name polin --top_alg resources/algebras/cyclic2.ua --bot_alg resources/algebras/cyclic2.ua --top_const_index 0 --bot_const_index 0",
            "cardinality --top_alg resources/algebras/cyclic2.ua --bot_alg resources/algebras/cyclic2.ua",
            "get_element --top_alg resources/algebras/cyclic2.ua --bot_alg resources/algebras/cyclic2.ua --index 0",
            "element_index --top_alg resources/algebras/cyclic2.ua --bot_alg resources/algebras/cyclic2.ua --element 0",
            "algebra_type --top_alg resources/algebras/cyclic2.ua --bot_alg resources/algebras/cyclic2.ua",
            "top_algebra_name --top_alg resources/algebras/cyclic2.ua --bot_alg resources/algebras/cyclic2.ua",
            "bottom_algebra_name --top_alg resources/algebras/cyclic2.ua --bot_alg resources/algebras/cyclic2.ua",
            "test"
        };
        
        showUsage("PolinLikeAlgebra", 
                 "CLI wrapper for org.uacalc.alg.PolinLikeAlgebra operations", 
                 examples);
    }
}

