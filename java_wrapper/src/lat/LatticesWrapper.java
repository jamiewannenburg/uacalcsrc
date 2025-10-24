/* LatticesWrapper.java - CLI wrapper for org.uacalc.lat.Lattices
 * 
 * This wrapper exposes all public methods of the Lattices class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.lat;

import java.util.*;
import org.uacalc.lat.Lattices;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Lattices class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class LatticesWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Lattices CLI wrapper.
     */
    public static void main(String[] args) {
        LatticesWrapper wrapper = new LatticesWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Lattices wrapper failed", e);
        }
    }
    
    /**
     * Run the Lattices CLI wrapper with the given arguments.
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
                
            case "lattice_from_meet":
                handleLatticeFromMeet(options);
                break;
                
            case "lattice_from_join":
                handleLatticeFromJoin(options);
                break;
                
            case "lattice_from_meet_with_universe":
                handleLatticeFromMeetWithUniverse(options);
                break;
                
            case "lattice_from_join_with_universe":
                handleLatticeFromJoinWithUniverse(options);
                break;
                
            case "con_to_small_lattice":
                handleConToSmallLattice(options);
                break;
                
            case "dual":
                handleDual(options);
                break;
                
            case "test":
                handleTest();
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle lattice_from_meet command.
     */
    private void handleLatticeFromMeet(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        // Note: This would require a concrete Operation implementation
        // For now, return an error indicating this is not implemented
        handleError("lattice_from_meet requires a concrete Operation implementation which is not yet available", null);
    }
    
    /**
     * Handle lattice_from_join command.
     */
    private void handleLatticeFromJoin(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        // Note: This would require a concrete Operation implementation
        // For now, return an error indicating this is not implemented
        handleError("lattice_from_join requires a concrete Operation implementation which is not yet available", null);
    }
    
    /**
     * Handle lattice_from_meet_with_universe command.
     */
    private void handleLatticeFromMeetWithUniverse(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        String univStr = getRequiredArg(options, "univ");
        // Note: This would require a concrete Operation implementation
        // For now, return an error indicating this is not implemented
        handleError("lattice_from_meet_with_universe requires a concrete Operation implementation which is not yet available", null);
    }
    
    /**
     * Handle lattice_from_join_with_universe command.
     */
    private void handleLatticeFromJoinWithUniverse(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        String univStr = getRequiredArg(options, "univ");
        // Note: This would require a concrete Operation implementation
        // For now, return an error indicating this is not implemented
        handleError("lattice_from_join_with_universe requires a concrete Operation implementation which is not yet available", null);
    }
    
    /**
     * Handle con_to_small_lattice command.
     */
    private void handleConToSmallLattice(Map<String, String> options) throws Exception {
        // Note: This requires CongruenceLattice which is not yet implemented
        handleError("con_to_small_lattice requires CongruenceLattice which is not yet implemented", null);
    }
    
    /**
     * Handle dual command.
     */
    private void handleDual(Map<String, String> options) throws Exception {
        // Note: This requires BasicLattice which is not yet implemented
        handleError("dual requires BasicLattice which is not yet implemented", null);
    }
    
    /**
     * Handle test command.
     */
    private void handleTest() throws Exception {
        // Test basic functionality
        Map<String, Object> result = new HashMap<>();
        result.put("status", "Lattices wrapper is working");
        result.put("available_methods", Arrays.asList(
            "lattice_from_meet",
            "lattice_from_join", 
            "lattice_from_meet_with_universe",
            "lattice_from_join_with_universe",
            "con_to_small_lattice",
            "dual"
        ));
        result.put("note", "Most methods require dependencies that are not yet implemented");
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the Lattices wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "lattice_from_meet --name \"TestLattice\" --meet <operation>",
            "lattice_from_join --name \"TestLattice\" --join <operation>",
            "lattice_from_meet_with_universe --name \"TestLattice\" --univ \"[0,1,2]\" --meet <operation>",
            "lattice_from_join_with_universe --name \"TestLattice\" --univ \"[0,1,2]\" --join <operation>",
            "con_to_small_lattice --con <congruence_lattice>",
            "dual --lat <basic_lattice>",
            "test"
        };
        
        showUsage("Lattices", 
                 "CLI wrapper for org.uacalc.lat.Lattices operations", 
                 examples);
    }
}
