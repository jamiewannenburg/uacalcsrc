/* MaltsevProductDecompositionWrapper.java - CLI wrapper for org.uacalc.alg.MaltsevProductDecomposition
 * 
 * This wrapper exposes all public methods of the MaltsevProductDecomposition class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.MaltsevProductDecomposition;
import org.uacalc.alg.SmallAlgebra;
import org.uacalc.alg.BasicAlgebra;
import org.uacalc.alg.conlat.Partition;
import org.uacalc.alg.conlat.BasicPartition;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the MaltsevProductDecomposition class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class MaltsevProductDecompositionWrapper extends WrapperBase {
    
    // Store input data for accessor methods
    private SmallAlgebra inputAlgebra;
    private Partition inputCongruence;
    
    /**
     * Main entry point for the MaltsevProductDecomposition CLI wrapper.
     */
    public static void main(String[] args) {
        MaltsevProductDecompositionWrapper wrapper = new MaltsevProductDecompositionWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("MaltsevProductDecomposition wrapper failed", e);
        }
    }
    
    /**
     * Run the MaltsevProductDecomposition CLI wrapper with the given arguments.
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
                
            case "test":
                handleTest(options);
                break;
                
            case "new":
                handleNew(options);
                break;
                
            case "get_congruence":
                handleGetCongruence(options);
                break;
                
            case "get_algebra":
                handleGetAlgebra(options);
                break;
                
            case "get_block_algebras":
                handleGetBlockAlgebras(options);
                break;
                
            case "get_quotient_algebra":
                handleGetQuotientAlgebra(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle test command - runs basic functionality test.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Create a simple test algebra
        Set<Integer> universe = new HashSet<>();
        universe.add(0);
        universe.add(1);
        universe.add(2);
        universe.add(3);
        SmallAlgebra alg = new BasicAlgebra("TestAlgebra", 4, new ArrayList<>());
        
        // Create a congruence with blocks {0,1}, {2,3}
        int[] array = new int[]{-2, 0, -2, 2};
        Partition cong = new BasicPartition(array);
        
        // Create decomposition
        MaltsevProductDecomposition decomp = new MaltsevProductDecomposition(alg, cong);
        
        // Get components
        Partition congruence = decomp.getCongruence();
        SmallAlgebra algebra = decomp.getAlgebra();
        List<SmallAlgebra> blockAlgs = decomp.getBlockAlgebras();
        SmallAlgebra quotAlg = decomp.getQuotientAlgebra();
        
        // Return results
        Map<String, Object> result = new HashMap<>();
        result.put("algebra_cardinality", algebra.cardinality());
        result.put("congruence_blocks", congruence.numberOfBlocks());
        result.put("block_count", blockAlgs.size());
        result.put("quotient_cardinality", quotAlg.cardinality());
        result.put("status", "ok");
        
        handleSuccess(result);
    }
    
    /**
     * Handle new command - creates a new MaltsevProductDecomposition.
     */
    private void handleNew(Map<String, String> options) throws Exception {
        // Get algebra cardinality
        int card = getIntArg(options, "cardinality", 4);
        
        // Get congruence array
        String arrayStr = getRequiredArg(options, "congruence");
        String[] parts = arrayStr.split(",");
        int[] array = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            array[i] = Integer.parseInt(parts[i].trim());
        }
        
        // Create algebra and congruence
        SmallAlgebra alg = new BasicAlgebra("TestAlg", card, new ArrayList<>());
        Partition cong = new BasicPartition(array);
        
        // Store inputs
        this.inputAlgebra = alg;
        this.inputCongruence = cong;
        
        // Create decomposition
        MaltsevProductDecomposition decomp = new MaltsevProductDecomposition(alg, cong);
        
        // Return result
        Map<String, Object> result = new HashMap<>();
        result.put("algebra_cardinality", alg.cardinality());
        result.put("congruence_blocks", cong.numberOfBlocks());
        result.put("block_count", decomp.getBlockAlgebras().size());
        result.put("quotient_cardinality", decomp.getQuotientAlgebra().cardinality());
        result.put("status", "ok");
        
        handleSuccess(result);
    }
    
    /**
     * Handle get_congruence command.
     */
    private void handleGetCongruence(Map<String, String> options) throws Exception {
        if (this.inputCongruence == null) {
            handleError("No decomposition created yet", null);
            return;
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("blocks", this.inputCongruence.numberOfBlocks());
        result.put("size", this.inputCongruence.universeSize());
        result.put("status", "ok");
        
        handleSuccess(result);
    }
    
    /**
     * Handle get_algebra command.
     */
    private void handleGetAlgebra(Map<String, String> options) throws Exception {
        if (this.inputAlgebra == null) {
            handleError("No decomposition created yet", null);
            return;
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("cardinality", this.inputAlgebra.cardinality());
        result.put("name", "TestAlg");
        result.put("status", "ok");
        
        handleSuccess(result);
    }
    
    /**
     * Handle get_block_algebras command.
     */
    private void handleGetBlockAlgebras(Map<String, String> options) throws Exception {
        // Get algebra cardinality
        int card = getIntArg(options, "cardinality", 4);
        
        // Get congruence array
        String arrayStr = getRequiredArg(options, "congruence");
        String[] parts = arrayStr.split(",");
        int[] array = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            array[i] = Integer.parseInt(parts[i].trim());
        }
        
        // Create algebra and congruence
        SmallAlgebra alg = new BasicAlgebra("TestAlg", card, new ArrayList<>());
        Partition cong = new BasicPartition(array);
        
        // Create decomposition
        MaltsevProductDecomposition decomp = new MaltsevProductDecomposition(alg, cong);
        
        // Get block algebras
        List<SmallAlgebra> blockAlgs = decomp.getBlockAlgebras();
        
        // Return result
        Map<String, Object> result = new HashMap<>();
        result.put("block_count", blockAlgs.size());
        
        // Add cardinalities of block algebras
        List<Integer> cardinalities = new ArrayList<>();
        for (SmallAlgebra blockAlg : blockAlgs) {
            cardinalities.add(blockAlg.cardinality());
        }
        result.put("cardinalities", cardinalities);
        result.put("status", "ok");
        
        handleSuccess(result);
    }
    
    /**
     * Handle get_quotient_algebra command.
     */
    private void handleGetQuotientAlgebra(Map<String, String> options) throws Exception {
        // Get algebra cardinality
        int card = getIntArg(options, "cardinality", 4);
        
        // Get congruence array
        String arrayStr = getRequiredArg(options, "congruence");
        String[] parts = arrayStr.split(",");
        int[] array = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            array[i] = Integer.parseInt(parts[i].trim());
        }
        
        // Create algebra and congruence
        SmallAlgebra alg = new BasicAlgebra("TestAlg", card, new ArrayList<>());
        Partition cong = new BasicPartition(array);
        
        // Create decomposition
        MaltsevProductDecomposition decomp = new MaltsevProductDecomposition(alg, cong);
        
        // Get quotient algebra
        SmallAlgebra quotAlg = decomp.getQuotientAlgebra();
        
        // Return result
        Map<String, Object> result = new HashMap<>();
        result.put("cardinality", quotAlg.cardinality());
        result.put("status", "ok");
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the MaltsevProductDecomposition wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "test - Run basic functionality test",
            "new --cardinality 4 --congruence \"-2,0,-2,2\" - Create decomposition",
            "get_congruence - Get congruence partition",
            "get_algebra - Get original algebra",
            "get_block_algebras --cardinality 4 --congruence \"-2,0,-2,2\" - Get block algebras",
            "get_quotient_algebra --cardinality 4 --congruence \"-2,0,-2,2\" - Get quotient algebra"
        };
        
        showUsage("MaltsevProductDecomposition", 
                 "CLI wrapper for org.uacalc.alg.MaltsevProductDecomposition operations", 
                 examples);
    }
}
