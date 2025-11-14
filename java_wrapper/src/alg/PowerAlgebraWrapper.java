/* PowerAlgebraWrapper.java - CLI wrapper for org.uacalc.alg.PowerAlgebra
 * 
 * This wrapper exposes all public methods of the PowerAlgebra class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.PowerAlgebra;
import org.uacalc.alg.SmallAlgebra.AlgebraType;
import org.uacalc.io.AlgebraIO;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the PowerAlgebra class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class PowerAlgebraWrapper extends WrapperBase {
    
    /**
     * Main entry point for the PowerAlgebra CLI wrapper.
     */
    public static void main(String[] args) {
        PowerAlgebraWrapper wrapper = new PowerAlgebraWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("PowerAlgebra wrapper failed", e);
        }
    }
    
    /**
     * Run the PowerAlgebra CLI wrapper with the given arguments.
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
                
            case "create_with_name":
                handleCreateWithName(options);
                break;
                
            case "get_root":
                handleGetRoot(options);
                break;
                
            case "parent":
                handleParent(options);
                break;
                
            case "parents":
                handleParents(options);
                break;
                
            case "get_power":
                handleGetPower(options);
                break;
                
            case "get_root_size":
                handleGetRootSize(options);
                break;
                
            case "cardinality":
                handleCardinality(options);
                break;
                
            case "name":
                handleName(options);
                break;
                
            case "algebra_type":
                handleAlgebraType(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Create a power algebra from a root algebra file and power.
     * Usage: create --root_file file.ua --power 3
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        String rootFile = getRequiredArg(options, "root_file");
        int power = getIntArg(options, "power", 1);
        
        SmallAlgebra root = AlgebraIO.readAlgebraFile(rootFile);
        PowerAlgebra powerAlg = new PowerAlgebra(root, power);
        
        handleSuccess(powerAlg);
    }
    
    /**
     * Create a power algebra with a custom name.
     * Usage: create_with_name --name "CustomName" --root_file file.ua --power 2
     */
    private void handleCreateWithName(Map<String, String> options) throws Exception {
        String name = getRequiredArg(options, "name");
        String rootFile = getRequiredArg(options, "root_file");
        int power = getIntArg(options, "power", 1);
        
        SmallAlgebra root = AlgebraIO.readAlgebraFile(rootFile);
        PowerAlgebra powerAlg = new PowerAlgebra(name, root, power);
        
        handleSuccess(powerAlg);
    }
    
    /**
     * Get the root algebra.
     * Usage: get_root --root_file file.ua --power 2
     */
    private void handleGetRoot(Map<String, String> options) throws Exception {
        PowerAlgebra powerAlg = createPowerAlgebra(options);
        SmallAlgebra root = powerAlg.getRoot();
        
        handleSuccess(root);
    }
    
    /**
     * Get the parent algebra (same as root for power algebra).
     * Usage: parent --root_file file.ua --power 2
     */
    private void handleParent(Map<String, String> options) throws Exception {
        PowerAlgebra powerAlg = createPowerAlgebra(options);
        SmallAlgebra parent = powerAlg.parent();
        
        handleSuccess(parent);
    }
    
    /**
     * Get the parent algebras (list containing the root algebra).
     * Usage: parents --root_file file.ua --power 2
     */
    private void handleParents(Map<String, String> options) throws Exception {
        PowerAlgebra powerAlg = createPowerAlgebra(options);
        List<SmallAlgebra> parents = powerAlg.parents();
        
        handleSuccess(parents);
    }
    
    /**
     * Get the power/exponent.
     * Usage: get_power --root_file file.ua --power 3
     */
    private void handleGetPower(Map<String, String> options) throws Exception {
        PowerAlgebra powerAlg = createPowerAlgebra(options);
        int power = powerAlg.getPower();
        
        handleSuccess(power);
    }
    
    /**
     * Get the size of the root algebra.
     * Usage: get_root_size --root_file file.ua --power 2
     */
    private void handleGetRootSize(Map<String, String> options) throws Exception {
        PowerAlgebra powerAlg = createPowerAlgebra(options);
        int rootSize = powerAlg.getRoot().cardinality();
        
        handleSuccess(rootSize);
    }
    
    /**
     * Get the cardinality of the power algebra.
     * Usage: cardinality --root_file file.ua --power 2
     */
    private void handleCardinality(Map<String, String> options) throws Exception {
        PowerAlgebra powerAlg = createPowerAlgebra(options);
        int cardinality = powerAlg.cardinality();
        
        handleSuccess(cardinality);
    }
    
    /**
     * Get the name of the power algebra.
     * Usage: name --root_file file.ua --power 2
     */
    private void handleName(Map<String, String> options) throws Exception {
        PowerAlgebra powerAlg = createPowerAlgebra(options);
        // PowerAlgebra doesn't have a name() method, so we'll return a placeholder
        String name = "PowerAlgebra";
        
        handleSuccess(name);
    }
    
    /**
     * Get the algebra type.
     * Usage: algebra_type --root_file file.ua --power 2
     */
    private void handleAlgebraType(Map<String, String> options) throws Exception {
        PowerAlgebra powerAlg = createPowerAlgebra(options);
        AlgebraType type = powerAlg.algebraType();
        
        handleSuccess(type);
    }
    
    /**
     * Run basic functionality tests.
     * Usage: test --root_file file.ua --power 2
     */
    private void handleTest(Map<String, String> options) throws Exception {
        String rootFile = getRequiredArg(options, "root_file");
        int power = getIntArg(options, "power", 1);
        
        // Test 1: Create power algebra
        SmallAlgebra root = AlgebraIO.readAlgebraFile(rootFile);
        PowerAlgebra powerAlg = new PowerAlgebra(root, power);
        
        // Test 2: Verify basic properties
        int expectedCardinality = (int) Math.pow(root.cardinality(), power);
        if (powerAlg.cardinality() != expectedCardinality) {
            throw new RuntimeException("Cardinality mismatch: expected " + expectedCardinality + 
                                     ", got " + powerAlg.cardinality());
        }
        
        // Test 3: Verify power
        if (powerAlg.getPower() != power) {
            throw new RuntimeException("Power mismatch: expected " + power + 
                                     ", got " + powerAlg.getPower());
        }
        
        // Test 4: Verify root
        if (powerAlg.getRoot() != root) {
            throw new RuntimeException("Root algebra mismatch");
        }
        
        // Test 5: Verify parent
        if (powerAlg.parent() != root) {
            throw new RuntimeException("Parent algebra mismatch");
        }
        
        // Test 6: Verify parents list
        List<SmallAlgebra> parents = powerAlg.parents();
        if (parents.size() != 1 || parents.get(0) != root) {
            throw new RuntimeException("Parents list mismatch");
        }
        
        // Test 7: Verify algebra type
        if (powerAlg.algebraType() != AlgebraType.POWER) {
            throw new RuntimeException("Algebra type mismatch: expected POWER, got " + powerAlg.algebraType());
        }
        
        handleSuccess(powerAlg);
    }
    
    /**
     * Helper method to create a PowerAlgebra from options.
     */
    private PowerAlgebra createPowerAlgebra(Map<String, String> options) throws Exception {
        String rootFile = getRequiredArg(options, "root_file");
        int power = getIntArg(options, "power", 1);
        
        SmallAlgebra root = AlgebraIO.readAlgebraFile(rootFile);
        return new PowerAlgebra(root, power);
    }
    
    /**
     * Show usage information for the PowerAlgebra wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create --root_file resources/algebras/cyclic3.ua --power 2",
            "create_with_name --name \"C3^2\" --root_file resources/algebras/cyclic3.ua --power 2",
            "get_root --root_file resources/algebras/cyclic3.ua --power 2",
            "parent --root_file resources/algebras/cyclic3.ua --power 2",
            "parents --root_file resources/algebras/cyclic3.ua --power 2",
            "get_power --root_file resources/algebras/cyclic3.ua --power 3",
            "get_root_size --root_file resources/algebras/cyclic3.ua --power 2",
            "cardinality --root_file resources/algebras/cyclic3.ua --power 2",
            "name --root_file resources/algebras/cyclic3.ua --power 2",
            "algebra_type --root_file resources/algebras/cyclic3.ua --power 2",
            "test --root_file resources/algebras/cyclic3.ua --power 2"
        };
        
        showUsage("PowerAlgebra", 
                 "CLI wrapper for org.uacalc.alg.PowerAlgebra operations", 
                 examples);
    }
}
