/* BasicLatticeWrapper.java - CLI wrapper for org.uacalc.lat.BasicLattice
 * 
 * This wrapper exposes all public methods of the BasicLattice class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.lat;

import java.util.*;
import org.uacalc.lat.BasicLattice;
import org.uacalc.lat.Lattice;
import org.uacalc.alg.conlat.CongruenceLattice;
import org.uacalc.alg.sublat.SubalgebraLattice;
import org.uacalc.alg.op.Operation;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the BasicLattice class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class BasicLatticeWrapper extends WrapperBase {
    
    /**
     * Main entry point for the BasicLattice CLI wrapper.
     */
    public static void main(String[] args) {
        BasicLatticeWrapper wrapper = new BasicLatticeWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("BasicLattice wrapper failed", e);
        }
    }
    
    /**
     * Run the BasicLattice CLI wrapper with the given arguments.
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
                
            case "new_from_poset":
                handleNewFromPoset(options);
                break;
                
            case "new_from_lattice":
                handleNewFromLattice(options);
                break;
                
            case "new_from_congruence":
                handleNewFromCongruence(options);
                break;
                
            case "join":
                handleJoin(options);
                break;
                
            case "meet":
                handleMeet(options);
                break;
                
            case "leq":
                handleLeq(options);
                break;
                
            case "atoms":
                handleAtoms(options);
                break;
                
            case "coatoms":
                handleCoatoms(options);
                break;
                
            case "join_irreducibles":
                handleJoinIrreducibles(options);
                break;
                
            case "meet_irreducibles":
                handleMeetIrreducibles(options);
                break;
                
            case "to_graph_data":
                handleToGraphData(options);
                break;
                
            case "filter":
                handleFilter(options);
                break;
                
            case "ideal":
                handleIdeal(options);
                break;
                
            case "test":
                handleTest();
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle new_from_poset command.
     * Note: This is a placeholder as creating from poset requires OrderedSet which is complex.
     */
    private void handleNewFromPoset(Map<String, String> options) throws Exception {
        handleError("new_from_poset requires OrderedSet creation which is complex. Use new_from_congruence or new_from_lattice instead.", null);
    }
    
    /**
     * Handle new_from_lattice command.
     * Note: This requires a Lattice implementation.
     */
    private void handleNewFromLattice(Map<String, String> options) throws Exception {
        handleError("new_from_lattice requires a Lattice implementation. Use new_from_congruence instead.", null);
    }
    
    /**
     * Handle new_from_congruence command.
     */
    private void handleNewFromCongruence(Map<String, String> options) throws Exception {
        try {
            String name = getOptionalArg(options, "name", "");
            String labelStr = getOptionalArg(options, "label", "true");
            boolean label = Boolean.parseBoolean(labelStr);
            
            // Note: This would require creating a CongruenceLattice first
            // For now, return an error indicating this needs a CongruenceLattice
            handleError("new_from_congruence requires a CongruenceLattice instance. Use CongruenceLatticeWrapper to create one first.", null);
            
        } catch (Exception e) {
            handleError("new_from_congruence command failed", e);
        }
    }
    
    /**
     * Handle join command.
     */
    private void handleJoin(Map<String, String> options) throws Exception {
        try {
            String latticeJson = getRequiredArg(options, "lattice");
            String aStr = getRequiredArg(options, "a");
            String bStr = getRequiredArg(options, "b");
            
            // Note: This would require deserializing the BasicLattice
            // For now, return an error
            handleError("join command requires BasicLattice deserialization which is not yet implemented", null);
            
        } catch (Exception e) {
            handleError("join command failed", e);
        }
    }
    
    /**
     * Handle meet command.
     */
    private void handleMeet(Map<String, String> options) throws Exception {
        try {
            String latticeJson = getRequiredArg(options, "lattice");
            String aStr = getRequiredArg(options, "a");
            String bStr = getRequiredArg(options, "b");
            
            // Note: This would require deserializing the BasicLattice
            // For now, return an error
            handleError("meet command requires BasicLattice deserialization which is not yet implemented", null);
            
        } catch (Exception e) {
            handleError("meet command failed", e);
        }
    }
    
    /**
     * Handle leq command.
     */
    private void handleLeq(Map<String, String> options) throws Exception {
        try {
            String latticeJson = getRequiredArg(options, "lattice");
            String aStr = getRequiredArg(options, "a");
            String bStr = getRequiredArg(options, "b");
            
            // Note: This would require deserializing the BasicLattice
            // For now, return an error
            handleError("leq command requires BasicLattice deserialization which is not yet implemented", null);
            
        } catch (Exception e) {
            handleError("leq command failed", e);
        }
    }
    
    /**
     * Handle atoms command.
     */
    private void handleAtoms(Map<String, String> options) throws Exception {
        try {
            String latticeJson = getRequiredArg(options, "lattice");
            
            // Note: This would require deserializing the BasicLattice
            // For now, return an error
            handleError("atoms command requires BasicLattice deserialization which is not yet implemented", null);
            
        } catch (Exception e) {
            handleError("atoms command failed", e);
        }
    }
    
    /**
     * Handle coatoms command.
     */
    private void handleCoatoms(Map<String, String> options) throws Exception {
        try {
            String latticeJson = getRequiredArg(options, "lattice");
            
            // Note: This would require deserializing the BasicLattice
            // For now, return an error
            handleError("coatoms command requires BasicLattice deserialization which is not yet implemented", null);
            
        } catch (Exception e) {
            handleError("coatoms command failed", e);
        }
    }
    
    /**
     * Handle join_irreducibles command.
     */
    private void handleJoinIrreducibles(Map<String, String> options) throws Exception {
        try {
            String latticeJson = getRequiredArg(options, "lattice");
            
            // Note: This would require deserializing the BasicLattice
            // For now, return an error
            handleError("join_irreducibles command requires BasicLattice deserialization which is not yet implemented", null);
            
        } catch (Exception e) {
            handleError("join_irreducibles command failed", e);
        }
    }
    
    /**
     * Handle meet_irreducibles command.
     */
    private void handleMeetIrreducibles(Map<String, String> options) throws Exception {
        try {
            String latticeJson = getRequiredArg(options, "lattice");
            
            // Note: This would require deserializing the BasicLattice
            // For now, return an error
            handleError("meet_irreducibles command requires BasicLattice deserialization which is not yet implemented", null);
            
        } catch (Exception e) {
            handleError("meet_irreducibles command failed", e);
        }
    }
    
    /**
     * Handle to_graph_data command.
     */
    private void handleToGraphData(Map<String, String> options) throws Exception {
        try {
            String latticeJson = getRequiredArg(options, "lattice");
            
            // Note: This would require deserializing the BasicLattice
            // For now, return an error
            handleError("to_graph_data command requires BasicLattice deserialization which is not yet implemented", null);
            
        } catch (Exception e) {
            handleError("to_graph_data command failed", e);
        }
    }
    
    /**
     * Handle filter command.
     */
    private void handleFilter(Map<String, String> options) throws Exception {
        try {
            String latticeJson = getRequiredArg(options, "lattice");
            String elementStr = getRequiredArg(options, "element");
            
            // Note: This would require deserializing the BasicLattice
            // For now, return an error
            handleError("filter command requires BasicLattice deserialization which is not yet implemented", null);
            
        } catch (Exception e) {
            handleError("filter command failed", e);
        }
    }
    
    /**
     * Handle ideal command.
     */
    private void handleIdeal(Map<String, String> options) throws Exception {
        try {
            String latticeJson = getRequiredArg(options, "lattice");
            String elementStr = getRequiredArg(options, "element");
            
            // Note: This would require deserializing the BasicLattice
            // For now, return an error
            handleError("ideal command requires BasicLattice deserialization which is not yet implemented", null);
            
        } catch (Exception e) {
            handleError("ideal command failed", e);
        }
    }
    
    /**
     * Handle test command.
     */
    private void handleTest() throws Exception {
        // Test basic functionality
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test");
        result.put("status", "BasicLattice wrapper is available");
        result.put("message", "Use CongruenceLatticeWrapper to create a CongruenceLattice, then use get_basic_lattice method");
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the BasicLattice wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "new_from_congruence --name \"TestLattice\" --label true",
            "join --lattice <json> --a 0 --b 1",
            "meet --lattice <json> --a 0 --b 1",
            "leq --lattice <json> --a 0 --b 1",
            "atoms --lattice <json>",
            "coatoms --lattice <json>",
            "join_irreducibles --lattice <json>",
            "meet_irreducibles --lattice <json>",
            "filter --lattice <json> --element 0",
            "ideal --lattice <json> --element 0",
            "to_graph_data --lattice <json>",
            "test"
        };
        
        showUsage("BasicLattice", 
                 "CLI wrapper for org.uacalc.lat.BasicLattice operations", 
                 examples);
    }
}

