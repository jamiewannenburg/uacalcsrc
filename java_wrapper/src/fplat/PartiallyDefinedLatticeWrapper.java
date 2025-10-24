/* PartiallyDefinedLatticeWrapper.java - CLI wrapper for org.uacalc.fplat.PartiallyDefinedLattice
 * 
 * This wrapper exposes all public methods of the PartiallyDefinedLattice class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.fplat;

import java.util.*;
import org.uacalc.fplat.PartiallyDefinedLattice;
import org.uacalc.lat.Order;
import org.uacalc.terms.*;
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
        String name = getOptionalArg(options, "name", "TestLattice");
        String joinsStr = getOptionalArg(options, "joins", "");
        String meetsStr = getOptionalArg(options, "meets", "");
        
        // Create a simple name-based order for variables
        Order<Variable> order = new Order<Variable>() {
            @Override
            public boolean leq(Variable a, Variable b) {
                return a.name().compareTo(b.name()) <= 0;
            }
        };
        
        // Parse joins and meets from comma-separated strings
        List<List<Variable>> joins = parseVariableLists(joinsStr);
        List<List<Variable>> meets = parseVariableLists(meetsStr);
        
        // Create the lattice
        PartiallyDefinedLattice lattice = new PartiallyDefinedLattice(name, order, joins, meets);
        
        // Test leq operation with first variables if available
        boolean leqResult = false;
        String varA = "";
        String varB = "";
        
        if (!joins.isEmpty() && !joins.get(0).isEmpty() && joins.get(0).size() >= 2) {
            Variable a = joins.get(0).get(0);
            Variable b = joins.get(0).get(1);
            varA = a.name();
            varB = b.name();
            leqResult = lattice.leq(a, b);
        }
        
        // Prepare response data
        Map<String, Object> data = new HashMap<>();
        data.put("command", "create");
        data.put("name", name);
        data.put("joins_count", joins.size());
        data.put("meets_count", meets.size());
        data.put("status", "created");
        
        if (!varA.isEmpty()) {
            data.put("leq_test_a", varA);
            data.put("leq_test_b", varB);
            data.put("leq_result", leqResult);
        }
        
        handleSuccess(data);
    }
    
    /**
     * Handle the test command - run basic functionality tests.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        List<Map<String, Object>> testResults = new ArrayList<>();
        
        // Test 1: Create simple lattice
        try {
            Order<Variable> order = new Order<Variable>() {
                @Override
                public boolean leq(Variable a, Variable b) {
                    return a.name().compareTo(b.name()) <= 0;
                }
            };
            
            Variable x = new VariableImp("x");
            Variable y = new VariableImp("y");
            Variable z = new VariableImp("z");
            
            List<List<Variable>> joins = new ArrayList<>();
            List<Variable> join1 = new ArrayList<>();
            join1.add(x);
            join1.add(y);
            joins.add(join1);
            
            List<List<Variable>> meets = new ArrayList<>();
            List<Variable> meet1 = new ArrayList<>();
            meet1.add(y);
            meet1.add(z);
            meets.add(meet1);
            
            PartiallyDefinedLattice lattice = new PartiallyDefinedLattice("Test", order, joins, meets);
            
            Map<String, Object> test1 = new HashMap<>();
            test1.put("test", "create_simple");
            test1.put("status", "passed");
            test1.put("leq_x_y", lattice.leq(x, y));
            test1.put("leq_y_x", lattice.leq(y, x));
            test1.put("leq_x_x", lattice.leq(x, x));
            testResults.add(test1);
        } catch (Exception e) {
            Map<String, Object> test1 = new HashMap<>();
            test1.put("test", "create_simple");
            test1.put("status", "failed");
            test1.put("error", e.getMessage());
            testResults.add(test1);
        }
        
        // Test 2: Create lattice with multiple joins
        try {
            Order<Variable> order = new Order<Variable>() {
                @Override
                public boolean leq(Variable a, Variable b) {
                    return a.name().compareTo(b.name()) <= 0;
                }
            };
            
            Variable a = new VariableImp("a");
            Variable b = new VariableImp("b");
            Variable c = new VariableImp("c");
            
            List<List<Variable>> joins = new ArrayList<>();
            List<Variable> join1 = new ArrayList<>();
            join1.add(a);
            join1.add(b);
            joins.add(join1);
            
            List<Variable> join2 = new ArrayList<>();
            join2.add(b);
            join2.add(c);
            joins.add(join2);
            
            List<List<Variable>> meets = new ArrayList<>();
            
            PartiallyDefinedLattice lattice = new PartiallyDefinedLattice("Test2", order, joins, meets);
            
            Map<String, Object> test2 = new HashMap<>();
            test2.put("test", "multiple_joins");
            test2.put("status", "passed");
            test2.put("joins_count", 2);
            test2.put("leq_a_b", lattice.leq(a, b));
            test2.put("leq_b_c", lattice.leq(b, c));
            testResults.add(test2);
        } catch (Exception e) {
            Map<String, Object> test2 = new HashMap<>();
            test2.put("test", "multiple_joins");
            test2.put("status", "failed");
            test2.put("error", e.getMessage());
            testResults.add(test2);
        }
        
        Map<String, Object> data = new HashMap<>();
        data.put("command", "test");
        data.put("test_count", testResults.size());
        data.put("tests", testResults);
        
        handleSuccess(data);
    }
    
    /**
     * Parse a string representation of variable lists into actual lists.
     * Format: "x,y;z,w" means [[x,y], [z,w]]
     */
    private List<List<Variable>> parseVariableLists(String str) {
        List<List<Variable>> result = new ArrayList<>();
        
        if (str == null || str.trim().isEmpty()) {
            return result;
        }
        
        String[] groups = str.split(";");
        for (String group : groups) {
            List<Variable> varList = new ArrayList<>();
            String[] varNames = group.split(",");
            for (String varName : varNames) {
                varName = varName.trim();
                if (!varName.isEmpty()) {
                    varList.add(new VariableImp(varName));
                }
            }
            if (!varList.isEmpty()) {
                result.add(varList);
            }
        }
        
        return result;
    }
    
    /**
     * Show usage information for the PartiallyDefinedLattice wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "help                                        - Show this help message",
            "create --name MyLattice --joins x,y;z,w --meets a,b  - Create a lattice",
            "test                                        - Run basic functionality tests"
        };
        
        showUsage("PartiallyDefinedLattice", 
                 "CLI wrapper for org.uacalc.fplat.PartiallyDefinedLattice operations", 
                 examples);
    }
}
