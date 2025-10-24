/* CongruenceLatticeWrapper.java - CLI wrapper for org.uacalc.alg.conlat.CongruenceLattice
 * 
 * This wrapper exposes key public methods of the CongruenceLattice class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 * 
 * Note: This is a minimal wrapper focusing on core functionality. Methods requiring
 * CentralityData, TypeFinder, and BigProductAlgebra are not included as those
 * dependencies are not yet implemented in the Rust version.
 */

package java_wrapper.src.alg.conlat;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.conlat.*;
import org.uacalc.element.*;
import org.uacalc.alg.op.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the CongruenceLattice class that provides command-line access
 * to core public methods for testing and validation purposes.
 */
public class CongruenceLatticeWrapper extends WrapperBase {
    
    /**
     * Main entry point for the CongruenceLattice CLI wrapper.
     */
    public static void main(String[] args) {
        CongruenceLatticeWrapper wrapper = new CongruenceLatticeWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("CongruenceLattice wrapper failed", e);
        }
    }
    
    /**
     * Run the CongruenceLatticeWrapper CLI wrapper with the given arguments.
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
                
            case "test_basic":
                testBasic(options);
                break;
                
            case "con_cardinality":
                getConCardinality(options);
                break;
                
            case "is_distributive":
                isDistributive(options);
                break;
                
            case "principals":
                getPrincipals(options);
                break;
                
            case "join_irreducibles":
                getJoinIrreducibles(options);
                break;
                
            case "atoms":
                getAtoms(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Test basic CongruenceLattice functionality
     */
    private void testBasic(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 3);
        
        // Create a simple algebra (empty operations for testing)
        SmallAlgebra alg = new BasicAlgebra("TestAlg", size, new ArrayList<Operation>());
        
        // Create congruence lattice
        CongruenceLattice conLat = new CongruenceLattice(alg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("alg_size", conLat.getAlgebra().cardinality());
        result.put("zero_blocks", conLat.zero().numberOfBlocks());
        result.put("one_blocks", conLat.one().numberOfBlocks());
        result.put("description", conLat.getDescription());
        
        handleSuccess(result);
    }
    
    /**
     * Get the cardinality of the congruence lattice
     */
    private void getConCardinality(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 3);
        
        SmallAlgebra alg = new BasicAlgebra("TestAlg", size, new ArrayList<Operation>());
        CongruenceLattice conLat = new CongruenceLattice(alg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("cardinality", conLat.cardinality());
        result.put("alg_size", size);
        
        handleSuccess(result);
    }
    
    /**
     * Test if the lattice is distributive
     */
    private void isDistributive(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 3);
        
        SmallAlgebra alg = new BasicAlgebra("TestAlg", size, new ArrayList<Operation>());
        CongruenceLattice conLat = new CongruenceLattice(alg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("is_distributive", conLat.isDistributive());
        result.put("cardinality", conLat.cardinality());
        
        handleSuccess(result);
    }
    
    /**
     * Get principal congruences
     */
    private void getPrincipals(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 3);
        
        SmallAlgebra alg = new BasicAlgebra("TestAlg", size, new ArrayList<Operation>());
        CongruenceLattice conLat = new CongruenceLattice(alg);
        
        List<Partition> principals = conLat.principals();
        
        Map<String, Object> result = new HashMap<>();
        result.put("count", principals.size());
        result.put("alg_size", size);
        
        handleSuccess(result);
    }
    
    /**
     * Get join irreducible congruences
     */
    private void getJoinIrreducibles(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 3);
        
        SmallAlgebra alg = new BasicAlgebra("TestAlg", size, new ArrayList<Operation>());
        CongruenceLattice conLat = new CongruenceLattice(alg);
        
        List<Partition> jis = conLat.joinIrreducibles();
        
        Map<String, Object> result = new HashMap<>();
        result.put("count", jis.size());
        result.put("alg_size", size);
        
        handleSuccess(result);
    }
    
    /**
     * Get atoms of the lattice
     */
    private void getAtoms(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 3);
        
        SmallAlgebra alg = new BasicAlgebra("TestAlg", size, new ArrayList<Operation>());
        CongruenceLattice conLat = new CongruenceLattice(alg);
        
        List<Partition> atoms = conLat.atoms();
        
        Map<String, Object> result = new HashMap<>();
        result.put("count", atoms.size());
        result.put("alg_size", size);
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the CongruenceLattice wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "test_basic --size 3",
            "con_cardinality --size 4",
            "is_distributive --size 3",
            "principals --size 3",
            "join_irreducibles --size 3",
            "atoms --size 3"
        };
        
        showUsage("CongruenceLattice", 
                 "CLI wrapper for org.uacalc.alg.conlat.CongruenceLattice operations", 
                 examples);
    }
}
