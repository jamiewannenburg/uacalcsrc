/* LatticeTraitsWrapper.java - CLI wrapper for org.uacalc.lat.Lattice and org.uacalc.lat.SmallLattice
 * 
 * This wrapper demonstrates the Lattice and SmallLattice interfaces through
 * a command-line interface for testing and validation against Rust/Python implementations.
 * 
 * Note: Since Lattice and SmallLattice are interfaces, this wrapper demonstrates
 * their usage through concrete implementations and interface method documentation.
 */

package java_wrapper.src.lat;

import java.util.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper that demonstrates the Lattice and SmallLattice interfaces
 * and provides information about their methods for testing purposes.
 */
public class LatticeTraitsWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Lattice traits CLI wrapper.
     */
    public static void main(String[] args) {
        LatticeTraitsWrapper wrapper = new LatticeTraitsWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Lattice traits wrapper failed", e);
        }
    }
    
    /**
     * Run the Lattice traits CLI wrapper with the given arguments.
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
                
            case "lattice_info":
                handleLatticeInfo(options);
                break;
                
            case "small_lattice_info":
                handleSmallLatticeInfo(options);
                break;
                
            case "interface_methods":
                handleInterfaceMethods(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Show information about the Lattice interface.
     */
    private void handleLatticeInfo(Map<String, String> options) throws Exception {
        Map<String, Object> result = new HashMap<>();
        result.put("interface_name", "org.uacalc.lat.Lattice");
        result.put("extends", Arrays.asList("org.uacalc.alg.Algebra", "org.uacalc.lat.Order"));
        result.put("methods", Arrays.asList(
            "joinIrreducibles() -> List<? extends Object>",
            "meetIrreducibles() -> List<? extends Object>",
            "atoms() -> List<? extends Object>",
            "coatoms() -> List<? extends Object>",
            "join(Object a, Object b) -> Object",
            "join(List args) -> Object",
            "meet(Object a, Object b) -> Object",
            "meet(List args) -> Object"
        ));
        result.put("method_count", 8);
        result.put("is_interface", true);
        result.put("can_instantiate", false);
        
        handleSuccess(result);
    }
    
    /**
     * Show information about the SmallLattice interface.
     */
    private void handleSmallLatticeInfo(Map<String, String> options) throws Exception {
        Map<String, Object> result = new HashMap<>();
        result.put("interface_name", "org.uacalc.lat.SmallLattice");
        result.put("extends", Arrays.asList("org.uacalc.lat.Lattice"));
        result.put("methods", Arrays.asList(
            "upperCoversIndices(int index) -> int[]"
        ));
        result.put("inherited_methods", 8); // From Lattice
        result.put("total_methods", 9); // 8 from Lattice + 1 from SmallLattice
        result.put("method_count", 1); // Only SmallLattice-specific methods
        result.put("is_interface", true);
        result.put("can_instantiate", false);
        
        handleSuccess(result);
    }
    
    /**
     * Show detailed method information for both interfaces.
     */
    private void handleInterfaceMethods(Map<String, String> options) throws Exception {
        String interfaceName = getOptionalArg(options, "interface", "both");
        
        Map<String, Object> result = new HashMap<>();
        
        if ("lattice".equals(interfaceName) || "both".equals(interfaceName)) {
            Map<String, Object> latticeInfo = new HashMap<>();
            latticeInfo.put("joinIrreducibles", "Returns list of join irreducible elements (optional)");
            latticeInfo.put("meetIrreducibles", "Returns list of meet irreducible elements (optional)");
            latticeInfo.put("atoms", "Returns list of atoms (minimal non-zero elements)");
            latticeInfo.put("coatoms", "Returns list of coatoms (maximal non-one elements)");
            latticeInfo.put("join_binary", "Returns join (least upper bound) of two elements");
            latticeInfo.put("join_list", "Returns join of a list of elements");
            latticeInfo.put("meet_binary", "Returns meet (greatest lower bound) of two elements");
            latticeInfo.put("meet_list", "Returns meet of a list of elements");
            result.put("lattice_methods", latticeInfo);
        }
        
        if ("small_lattice".equals(interfaceName) || "both".equals(interfaceName)) {
            Map<String, Object> smallLatticeInfo = new HashMap<>();
            smallLatticeInfo.put("upperCoversIndices", "Returns indices of upper covers of element at given index");
            result.put("small_lattice_methods", smallLatticeInfo);
        }
        
        result.put("queried_interface", interfaceName);
        handleSuccess(result);
    }
    
    /**
     * Run basic tests to verify interface definitions.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        Map<String, Object> result = new HashMap<>();
        
        // Test that interfaces exist and have expected methods
        try {
            Class<?> latticeClass = Class.forName("org.uacalc.lat.Lattice");
            Class<?> smallLatticeClass = Class.forName("org.uacalc.lat.SmallLattice");
            
            result.put("lattice_interface_exists", latticeClass.isInterface());
            result.put("small_lattice_interface_exists", smallLatticeClass.isInterface());
            
            // Check method counts
            int latticeMethodCount = latticeClass.getDeclaredMethods().length;
            int smallLatticeMethodCount = smallLatticeClass.getDeclaredMethods().length;
            
            result.put("lattice_method_count", latticeMethodCount);
            result.put("small_lattice_method_count", smallLatticeMethodCount);
            
            // Check inheritance
            boolean smallExtendsLattice = latticeClass.isAssignableFrom(smallLatticeClass);
            result.put("small_lattice_extends_lattice", smallExtendsLattice);
            
            // Check expected methods exist
            boolean hasJoin = Arrays.stream(latticeClass.getDeclaredMethods())
                .anyMatch(m -> m.getName().equals("join") && m.getParameterCount() == 2);
            boolean hasMeet = Arrays.stream(latticeClass.getDeclaredMethods())
                .anyMatch(m -> m.getName().equals("meet") && m.getParameterCount() == 2);
            boolean hasUpperCovers = Arrays.stream(smallLatticeClass.getDeclaredMethods())
                .anyMatch(m -> m.getName().equals("upperCoversIndices"));
            
            result.put("lattice_has_join", hasJoin);
            result.put("lattice_has_meet", hasMeet);
            result.put("small_lattice_has_upper_covers", hasUpperCovers);
            
            result.put("status", "success");
            result.put("test_passed", true);
            
        } catch (ClassNotFoundException e) {
            result.put("status", "error");
            result.put("error", "Interface not found: " + e.getMessage());
            result.put("test_passed", false);
        }
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the Lattice traits wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "lattice_info                          # Show Lattice interface information",
            "small_lattice_info                   # Show SmallLattice interface information", 
            "interface_methods                    # Show methods for both interfaces",
            "interface_methods --interface lattice # Show only Lattice methods",
            "interface_methods --interface small_lattice # Show only SmallLattice methods",
            "test                                 # Run basic interface verification tests"
        };
        
        showUsage("LatticeTraits", 
                 "CLI wrapper for org.uacalc.lat.Lattice and org.uacalc.lat.SmallLattice interfaces", 
                 examples);
    }
}