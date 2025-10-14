/* PartiallyDefinedLatticeWrapper.java - CLI wrapper for org.uacalc.fplat.PartiallyDefinedLattice
 * 
 * This wrapper exposes all public methods of the PartiallyDefinedLattice class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.fplat;

import java.util.*;
import org.uacalc.fplat.PartiallyDefinedLattice;
import org.uacalc.lat.Order;
import org.uacalc.terms.Variable;
import org.uacalc.terms.VariableImp;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the PartiallyDefinedLattice class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class PartiallyDefinedLatticeWrapper extends WrapperBase {
    
    /**
     * Main entry point for the PartiallyDefinedLattice CLI wrapper.
     */
    public static void main(String[] args) {
        PartiallyDefinedLatticeWrapper wrapper = new PartiallyDefinedLatticeWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("PartiallyDefinedLattice wrapper failed", e);
        }
    }
    
    /**
     * Run the PartiallyDefinedLattice CLI wrapper with the given arguments.
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
                
            case "leq":
                handleLeq(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the create command - create a partially defined lattice.
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "default");
        String orderType = getOptionalArg(options, "order", "index");
        String joinsStr = getOptionalArg(options, "joins", "");
        String meetsStr = getOptionalArg(options, "meets", "");
        
        // Create some example variables
        Variable x = new VariableImp("x");
        Variable y = new VariableImp("y");
        Variable z = new VariableImp("z");
        
        // Create order relation
        Order<Variable> order = createVariableOrder(orderType);
        
        // Parse joins and meets (simplified for demo)
        List<List<Variable>> joins = parseVariableOperations(joinsStr);
        List<List<Variable>> meets = parseVariableOperations(meetsStr);
        
        // Create the partially defined lattice
        PartiallyDefinedLattice pdl = new PartiallyDefinedLattice(name, order, joins, meets);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "create");
        response.put("name", name);
        response.put("order", orderType);
        response.put("joins_count", joins.size());
        response.put("meets_count", meets.size());
        response.put("status", "created");
        
        handleSuccess("create", response);
    }
    
    /**
     * Handle the leq command - test order relation.
     */
    private void handleLeq(Map<String, String> options) throws Exception {
        String var1Name = getRequiredArg(options, "var1");
        String var2Name = getRequiredArg(options, "var2");
        String orderType = getOptionalArg(options, "order", "index");
        
        // Create variables
        Variable var1 = new VariableImp(var1Name);
        Variable var2 = new VariableImp(var2Name);
        
        // Create order relation
        Order<Variable> order = createVariableOrder(orderType);
        
        // Create simple PDL for testing
        PartiallyDefinedLattice pdl = new PartiallyDefinedLattice(
            "test", order, new ArrayList<>(), new ArrayList<>()
        );
        
        // Test order relation
        boolean result = pdl.leq(var1, var2);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "leq");
        response.put("var1", var1Name);
        response.put("var2", var2Name);
        response.put("order", orderType);
        response.put("status", result);
        
        handleSuccess("leq", response);
    }
    
    /**
     * Handle the test command (equivalent to main method).
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Create example variables
        Variable x = new VariableImp("x");
        Variable y = new VariableImp("y");
        Variable z = new VariableImp("z");
        
        // Create alphabetical order
        Order<Variable> alphabeticalOrder = new Order<Variable>() {
            public boolean leq(Variable a, Variable b) {
                return a.getName().compareTo(b.getName()) <= 0;
            }
        };
        
        // Create some join and meet operations
        List<List<Variable>> joins = new ArrayList<>();
        joins.add(Arrays.asList(x, y));
        joins.add(Arrays.asList(y, z));
        
        List<List<Variable>> meets = new ArrayList<>();
        meets.add(Arrays.asList(x, y));
        meets.add(Arrays.asList(x, z));
        
        // Create partially defined lattice
        PartiallyDefinedLattice pdl = new PartiallyDefinedLattice(
            "example", alphabeticalOrder, joins, meets
        );
        
        // Test some order relations
        Map<String, Object> orderTests = new HashMap<>();
        orderTests.put("x_leq_y", pdl.leq(x, y));
        orderTests.put("y_leq_z", pdl.leq(y, z));
        orderTests.put("x_leq_z", pdl.leq(x, z));
        orderTests.put("y_leq_x", pdl.leq(y, x));
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "test");
        response.put("name", "example");
        response.put("variables", Arrays.asList("x", "y", "z"));
        response.put("joins_count", joins.size());
        response.put("meets_count", meets.size());
        response.put("order_tests", orderTests);
        response.put("status", "completed");
        
        handleSuccess("test", response);
    }
    
    /**
     * Create a variable order relation based on type.
     */
    private Order<Variable> createVariableOrder(String orderType) throws Exception {
        switch (orderType.toLowerCase()) {
            case "index":
                return new Order<Variable>() {
                    public boolean leq(Variable a, Variable b) {
                        // Compare by hashCode as a proxy for index
                        return a.hashCode() <= b.hashCode();
                    }
                };
                
            case "alphabetical":
                return new Order<Variable>() {
                    public boolean leq(Variable a, Variable b) {
                        return a.getName().compareTo(b.getName()) <= 0;
                    }
                };
                
            case "reverse":
                return new Order<Variable>() {
                    public boolean leq(Variable a, Variable b) {
                        return a.getName().compareTo(b.getName()) >= 0;
                    }
                };
                
            default:
                throw new Exception("Unknown order type: " + orderType + ". Supported: index, alphabetical, reverse");
        }
    }
    
    /**
     * Parse variable operations from string (simplified).
     */
    private List<List<Variable>> parseVariableOperations(String operationsStr) {
        List<List<Variable>> operations = new ArrayList<>();
        
        if (operationsStr.trim().isEmpty()) {
            return operations;
        }
        
        // Simple format: "x,y;y,z" means operations on (x,y) and (y,z)
        String[] opStrings = operationsStr.split(";");
        for (String opStr : opStrings) {
            String[] varNames = opStr.trim().split(",");
            List<Variable> vars = new ArrayList<>();
            for (String varName : varNames) {
                vars.add(new VariableImp(varName.trim()));
            }
            if (!vars.isEmpty()) {
                operations.add(vars);
            }
        }
        
        return operations;
    }
    
    /**
     * Show usage information for the PartiallyDefinedLattice wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "java PartiallyDefinedLatticeWrapper create --name \"example\" --order alphabetical --joins \"x,y;y,z\" --meets \"x,z\"",
            "java PartiallyDefinedLatticeWrapper leq --var1 x --var2 y --order alphabetical",
            "java PartiallyDefinedLatticeWrapper test"
        };
        
        showUsage("PartiallyDefinedLatticeWrapper", 
                 "CLI wrapper for org.uacalc.fplat.PartiallyDefinedLattice operations", 
                 examples);
    }
}