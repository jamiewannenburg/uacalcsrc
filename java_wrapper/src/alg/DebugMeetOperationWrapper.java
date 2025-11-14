/* DebugMeetOperationWrapper.java - CLI wrapper for debugging meet operation on F(1)^3
 * 
 * This wrapper creates F(1) over ba2, then F(1)^3, and tests meet operation
 * with detailed debug output for comparison with Rust implementation.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.op.*;
import org.uacalc.io.AlgebraIO;
import org.uacalc.util.IntArray;
import java_wrapper.src.WrapperBase;

public class DebugMeetOperationWrapper extends WrapperBase {
    
    public static void main(String[] args) {
        DebugMeetOperationWrapper wrapper = new DebugMeetOperationWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("DebugMeetOperationWrapper failed", e);
        }
    }
    
    @Override
    public void run(String[] args) throws Exception {
        if (args.length == 0) {
            showUsage();
            return;
        }
        
        Map<String, String> options = parseArgs(args);
        String command = options.get("arg0");
        
        if (command == null || command.equals("debug_meet")) {
            handleDebugMeet(options);
        } else {
            showUsage();
        }
    }
    
    private void showUsage() {
        System.out.println("Usage: DebugMeetOperationWrapper debug_meet");
        System.out.println("This will create F(1) over ba2, then F(1)^3, and test meet operation");
    }
    
    private void handleDebugMeet(Map<String, String> options) throws Exception {
        // Load ba2
        SmallAlgebra ba2 = AlgebraIO.readAlgebraFile("resources/algebras/ba2.ua");
        
        // Create F(1)
        FreeAlgebra f1 = new FreeAlgebra("F1", ba2, 1);
        
        System.out.println("\n=== JAVA DEBUG INFO ===");
        System.out.println("F(1) cardinality: " + f1.cardinality());
        
        // Get F(1) universe
        List<IntArray> f1Universe = f1.getUniverseList();
        System.out.println("F(1) universe (" + f1Universe.size() + " elements):");
        for (int i = 0; i < f1Universe.size(); i++) {
            IntArray elem = f1Universe.get(i);
            System.out.println("  Index " + i + ": " + Arrays.toString(elem.getArray()));
        }
        
        // Get F(1) operations
        List<Operation> f1Ops = f1.operations();
        System.out.println("\nF(1) operations (" + f1Ops.size() + "):");
        for (Operation op : f1Ops) {
            System.out.println("  " + op.symbol().name() + " (arity " + op.arity() + ")");
        }
        
        // Test meet on F(1) directly
        Operation meetOpF1 = null;
        for (Operation op : f1Ops) {
            if (op.symbol().name().equals("meet")) {
                meetOpF1 = op;
                break;
            }
        }
        
        if (meetOpF1 != null) {
            System.out.println("\nTesting meet on F(1) directly:");
            for (int i = 0; i < 3; i++) {
                for (int j = 0; j < 3; j++) {
                    int result = meetOpF1.intValueAt(new int[]{i, j});
                    IntArray resultElem = f1Universe.get(result);
                    System.out.println("  meet(" + i + ", " + j + ") = " + result + 
                                     " (element " + Arrays.toString(resultElem.getArray()) + ")");
                }
            }
        }
        
        // Create F(1)^3
        BigProductAlgebra f1Power3 = new BigProductAlgebra(f1, 3);
        
        System.out.println("\nF(1)^3 created successfully");
        System.out.println("Number of factors: " + f1Power3.getNumberOfFactors());
        
        // Get meet operation for F(1)^3
        List<Operation> opsPower3 = f1Power3.operations();
        Operation meetOp = null;
        for (Operation op : opsPower3) {
            if (op.symbol().name().equals("meet")) {
                meetOp = op;
                break;
            }
        }
        
        if (meetOp != null) {
            System.out.println("\nTesting meet([0,0,1], [1,1,0]) on F(1)^3:");
            IntArray arg0 = new IntArray(new int[]{0, 0, 1});
            IntArray arg1 = new IntArray(new int[]{1, 1, 0});
            List<IntArray> args = new ArrayList<>();
            args.add(arg0);
            args.add(arg1);
            
            System.out.println("  Arguments: " + Arrays.toString(arg0.getArray()) + 
                               ", " + Arrays.toString(arg1.getArray()));
            
            // Use valueAt which takes List<IntArray>
            Object resultObj = meetOp.valueAt(args);
            if (resultObj instanceof IntArray) {
                IntArray result = (IntArray) resultObj;
                System.out.println("  Result: " + Arrays.toString(result.getArray()));
                System.out.println("  Expected: [0, 0, 0]");
                if (!Arrays.equals(result.getArray(), new int[]{0, 0, 0})) {
                    System.out.println("  *** MISMATCH ***");
                } else {
                    System.out.println("  ✓ Correct!");
                }
            }
        }
        
        // Create detailed JSON output
        Map<String, Object> result = new HashMap<>();
        result.put("f1_cardinality", f1.cardinality());
        
        List<List<Integer>> univLists = new ArrayList<>();
        for (IntArray elem : f1Universe) {
            List<Integer> elemList = new ArrayList<>();
            for (int val : elem.getArray()) {
                elemList.add(val);
            }
            univLists.add(elemList);
        }
        result.put("f1_universe", univLists);
        
        // Create meet table
        List<List<Integer>> meetTable = new ArrayList<>();
        for (int i = 0; i < 3; i++) {
            List<Integer> row = new ArrayList<>();
            for (int j = 0; j < 3; j++) {
                if (meetOpF1 != null) {
                    row.add(meetOpF1.intValueAt(new int[]{i, j}));
                } else {
                    row.add(-1);
                }
            }
            meetTable.add(row);
        }
        Map<String, Object> meetTableObj = new HashMap<>();
        meetTableObj.put("rows", meetTable);
        result.put("f1_meet_table", meetTableObj);
        
        result.put("f1_power3_factors", f1Power3.getNumberOfFactors());
        
        Map<String, Object> testArgs = new HashMap<>();
        testArgs.put("arg0", Arrays.asList(0, 0, 1));
        testArgs.put("arg1", Arrays.asList(1, 1, 0));
        result.put("test_args", testArgs);
        
        if (meetOp != null) {
            IntArray arg0 = new IntArray(new int[]{0, 0, 1});
            IntArray arg1 = new IntArray(new int[]{1, 1, 0});
            List<IntArray> args = new ArrayList<>();
            args.add(arg0);
            args.add(arg1);
            Object resultObj = meetOp.valueAt(args);
            if (resultObj instanceof IntArray) {
                IntArray resultIA = (IntArray) resultObj;
                List<Integer> resultList = new ArrayList<>();
                for (int val : resultIA.getArray()) {
                    resultList.add(val);
                }
                result.put("test_result", resultList);
            }
        }
        
        result.put("expected_result", Arrays.asList(0, 0, 0));
        
        handleSuccess(result);
    }
}




