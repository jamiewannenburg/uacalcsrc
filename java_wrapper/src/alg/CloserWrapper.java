/* CloserWrapper.java - CLI wrapper for org.uacalc.alg.Closer
 * 
 * This wrapper exposes core methods of the Closer class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import java.io.*;
import org.uacalc.alg.*;
import org.uacalc.alg.conlat.*;
import org.uacalc.util.*;
import org.uacalc.io.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Closer class that provides command-line access
 * to core closure methods for testing and validation purposes.
 */
public class CloserWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Closer CLI wrapper.
     */
    public static void main(String[] args) {
        CloserWrapper wrapper = new CloserWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Closer wrapper failed", e);
        }
    }
    
    /**
     * Run the Closer CLI wrapper with the given arguments.
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
                
            case "sg_close":
                handleSgClose(options);
                break;
                
            case "sg_close_ba2_power":
                handleSgCloseBa2Power(options);
                break;
                
            case "sg_close_free_algebra":
                handleSgCloseFreeAlgebra(options);
                break;
                
            case "sg_close_power":
                handleSgClosePower(options);
                break;
                
            case "sg_close_with_constraints":
                handleSgCloseWithConstraints(options);
                break;
                
            case "sg_close_with_homomorphism":
                handleSgCloseWithHomomorphism(options);
                break;
                
            case "sg_close_with_operations_finding":
                handleSgCloseWithOperationsFinding(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle test command - run basic functionality tests.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Create a simple power algebra for testing
        SmallAlgebra base = makeTestAlgebra(2); // 2-element algebra
        int power = getIntArg(options, "power", 2);
        
        BigProductAlgebra algebra = new BigProductAlgebra(base, power);
        
        // Create some generators
        List<IntArray> generators = new ArrayList<>();
        int[] arr1 = new int[power];
        for (int i = 0; i < power; i++) arr1[i] = 0;
        generators.add(new IntArray(arr1));
        
        int[] arr2 = new int[power];
        for (int i = 0; i < power; i++) arr2[i] = i % 2;
        generators.add(new IntArray(arr2));
        
        // Create closer
        Closer closer = new Closer(algebra, generators);
        closer.setSuppressOutput(true);
        
        // Compute closure
        List<IntArray> result = closer.sgClose();
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "test");
        response.put("power", power);
        response.put("base_size", base.cardinality());
        response.put("generators_count", generators.size());
        response.put("closure_size", result.size());
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle sg_close command - compute closure of generators.
     */
    private void handleSgClose(Map<String, String> options) throws Exception {
        // Get parameters
        int baseSize = getIntArg(options, "base_size", 2);
        int power = getIntArg(options, "power", 2);
        String gensStr = getRequiredArg(options, "generators");
        
        // Create algebra
        SmallAlgebra base = makeTestAlgebra(baseSize);
        BigProductAlgebra algebra = new BigProductAlgebra(base, power);
        
        // Parse generators
        List<IntArray> generators = parseGenerators(gensStr, power);
        
        // Create closer and compute closure
        Closer closer = new Closer(algebra, generators);
        closer.setSuppressOutput(true);
        
        List<IntArray> result = closer.sgClose();
        
        // Format result
        List<List<Integer>> resultList = new ArrayList<>();
        for (IntArray ia : result) {
            List<Integer> elem = new ArrayList<>();
            for (int i = 0; i < ia.universeSize(); i++) {
                elem.add(ia.get(i));
            }
            resultList.add(elem);
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "sg_close");
        response.put("base_size", baseSize);
        response.put("power", power);
        response.put("generators_count", generators.size());
        response.put("closure_size", result.size());
        response.put("closure", resultList);
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Create a simple test algebra with given size.
     */
    private SmallAlgebra makeTestAlgebra(int size) throws Exception {
        // Create a trivial algebra with no operations for testing
        return new BasicAlgebra("TestAlg", size, new ArrayList<>());
    }
    
    /**
     * Parse generators from a string representation.
     * Format: "[[0,1],[1,0]]" or similar
     */
    private List<IntArray> parseGenerators(String gensStr, int power) throws Exception {
        List<IntArray> generators = new ArrayList<>();
        
        // Simple parsing - expects format like "0,1;1,0" where ; separates generators
        String[] parts = gensStr.split(";");
        for (String part : parts) {
            String[] values = part.split(",");
            int[] arr = new int[power];
            for (int i = 0; i < Math.min(power, values.length); i++) {
                arr[i] = Integer.parseInt(values[i].trim());
            }
            generators.add(new IntArray(arr));
        }
        
        return generators;
    }
    
    /**
     * Handle sg_close_power command - compute closure using sgClosePower method.
     */
    private void handleSgClosePower(Map<String, String> options) throws Exception {
        // Get parameters
        int baseSize = getIntArg(options, "base_size", 2);
        int power = getIntArg(options, "power", 2);
        String gensStr = getRequiredArg(options, "generators");
        
        // Create algebra
        SmallAlgebra base = makeTestAlgebra(baseSize);
        BigProductAlgebra algebra = new BigProductAlgebra(base, power);
        
        // Parse generators
        List<IntArray> generators = parseGenerators(gensStr, power);
        
        // Create closer and compute closure using sgClosePower
        Closer closer = new Closer(algebra, generators);
        closer.setSuppressOutput(true);
        
        List<IntArray> result = closer.sgClosePower();
        
        // Format result
        List<List<Integer>> resultList = new ArrayList<>();
        for (IntArray ia : result) {
            List<Integer> elem = new ArrayList<>();
            for (int i = 0; i < ia.universeSize(); i++) {
                elem.add(ia.get(i));
            }
            resultList.add(elem);
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "sg_close_power");
        response.put("base_size", baseSize);
        response.put("power", power);
        response.put("generators_count", generators.size());
        response.put("closure_size", result.size());
        response.put("closure", resultList);
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle sg_close_ba2_power command - compute closure with ba2 power algebra.
     */
    private void handleSgCloseBa2Power(Map<String, String> options) throws Exception {
        // Get parameters
        int power = getIntArg(options, "power", 2);
        String gensStr = getRequiredArg(options, "generators");
        
        // Load ba2 algebra
        SmallAlgebra ba2 = loadBa2();
        
        // Create power algebra
        BigProductAlgebra algebra = new BigProductAlgebra(ba2, power);
        
        // Parse generators
        List<IntArray> generators = parseGenerators(gensStr, power);
        
        // Create closer and compute closure
        Closer closer = new Closer(algebra, generators);
        closer.setSuppressOutput(true);
        
        List<IntArray> result = closer.sgClose();
        
        // Format result
        List<List<Integer>> resultList = new ArrayList<>();
        for (IntArray ia : result) {
            List<Integer> elem = new ArrayList<>();
            for (int i = 0; i < ia.universeSize(); i++) {
                elem.add(ia.get(i));
            }
            resultList.add(elem);
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "sg_close_ba2_power");
        response.put("power", power);
        response.put("base_size", ba2.cardinality());
        response.put("generators_count", generators.size());
        response.put("closure_size", result.size());
        response.put("closure", resultList);
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle sg_close_free_algebra command - compute closure with free algebra.
     */
    private void handleSgCloseFreeAlgebra(Map<String, String> options) throws Exception {
        // Get parameters
        int numGens = getIntArg(options, "num_gens", 1);
        int power = getIntArg(options, "power", 2);
        String gensStr = getRequiredArg(options, "generators");
        
        // Load ba2 and create free algebra
        SmallAlgebra ba2 = loadBa2();
        FreeAlgebra freeAlg = new FreeAlgebra(ba2, numGens);
        freeAlg.makeOperationTables();
        
        // Create power algebra from free algebra
        BigProductAlgebra algebra = new BigProductAlgebra(freeAlg, power);
        
        // Parse generators
        List<IntArray> generators = parseGenerators(gensStr, power);
        
        // Create closer and compute closure
        Closer closer = new Closer(algebra, generators);
        closer.setSuppressOutput(true);
        
        List<IntArray> result = closer.sgClose();
        
        // Format result
        List<List<Integer>> resultList = new ArrayList<>();
        for (IntArray ia : result) {
            List<Integer> elem = new ArrayList<>();
            for (int i = 0; i < ia.universeSize(); i++) {
                elem.add(ia.get(i));
            }
            resultList.add(elem);
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "sg_close_free_algebra");
        response.put("num_gens", numGens);
        response.put("power", power);
        response.put("base_size", freeAlg.cardinality());
        response.put("generators_count", generators.size());
        response.put("closure_size", result.size());
        response.put("closure", resultList);
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Load ba2 algebra from resources/algebras/ba2.ua
     */
    private SmallAlgebra loadBa2() throws Exception {
        // Try to find ba2.ua file
        String[] possiblePaths = {
            "resources/algebras/ba2.ua",
            "algebras/ba2.ua",
            "../resources/algebras/ba2.ua"
        };
        
        File ba2File = null;
        for (String path : possiblePaths) {
            File f = new File(path);
            if (f.exists()) {
                ba2File = f;
                break;
            }
        }
        
        if (ba2File == null) {
            // Try loading from classpath
            ClassLoader cl = Thread.currentThread().getContextClassLoader();
            InputStream is = cl.getResourceAsStream("algebras/ba2.ua");
            if (is != null) {
                return AlgebraIO.readAlgebraFromStream(is);
            }
            throw new Exception("ba2.ua not found in any expected location");
        }
        
        return AlgebraIO.readAlgebraFile(ba2File);
    }
    
    /**
     * Handle sg_close_with_constraints command - compute closure with constraint handling.
     */
    private void handleSgCloseWithConstraints(Map<String, String> options) throws Exception {
        // Get parameters
        int baseSize = getIntArg(options, "base_size", 2);
        int power = getIntArg(options, "power", 2);
        String gensStr = getRequiredArg(options, "generators");
        
        // For constraint testing, we need an algebra with operations
        // Use ba2 if base_size is 2, otherwise create test algebra
        SmallAlgebra base;
        if (baseSize == 2) {
            base = loadBa2();
        } else {
            base = makeTestAlgebra(baseSize);
        }
        BigProductAlgebra algebra = new BigProductAlgebra(base, power);
        
        // Parse generators
        List<IntArray> generators = parseGenerators(gensStr, power);
        
        // Create closer
        Closer closer = new Closer(algebra, generators);
        closer.setSuppressOutput(true);
        
        // Parse and set constraints
        // Blocks constraint: format "0,1;2,3" means indices 0,1 must be equal and 2,3 must be equal
        String blocksStr = options.get("blocks");
        if (blocksStr != null && !blocksStr.isEmpty()) {
            int[][] blocks = parseBlocks(blocksStr);
            closer.setBlocks(blocks);
        }
        
        // Values constraint: format "0:1,2:0" means index 0 = 1, index 2 = 0
        String valuesStr = options.get("values");
        if (valuesStr != null && !valuesStr.isEmpty()) {
            int[][] values = parseValues(valuesStr);
            closer.setValues(values);
        }
        
        // Set constraint: format "0:0,1,2" means index 0 must be in {0,1,2}
        String setConstraintStr = options.get("set_constraint");
        int setConstraintIndex = getIntArg(options, "set_constraint_index", -1);
        if (setConstraintStr != null && !setConstraintStr.isEmpty() && setConstraintIndex >= 0) {
            Set<Integer> constraintSet = parseSetConstraint(setConstraintStr);
            closer.setConstraintSet(constraintSet);
            closer.setIndexForConstraintSet(setConstraintIndex);
        }
        
        // Congruence constraint
        String congruenceStr = options.get("congruence");
        int congruenceIndex = getIntArg(options, "congruence_index", -1);
        int congruenceElemIndex = getIntArg(options, "congruence_elem_index", -1);
        if (congruenceStr != null && !congruenceStr.isEmpty() && congruenceIndex >= 0 && congruenceElemIndex >= 0) {
            Partition partition = parsePartition(congruenceStr, baseSize);
            closer.setupCongruenceConstraint(partition, congruenceIndex, congruenceElemIndex);
        }
        
        // Compute closure
        List<IntArray> result = closer.sgClose();
        
        // Format result
        List<List<Integer>> resultList = new ArrayList<>();
        for (IntArray ia : result) {
            List<Integer> elem = new ArrayList<>();
            for (int i = 0; i < ia.universeSize(); i++) {
                elem.add(ia.get(i));
            }
            resultList.add(elem);
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "sg_close_with_constraints");
        response.put("base_size", baseSize);
        response.put("power", power);
        response.put("generators_count", generators.size());
        response.put("closure_size", result.size());
        response.put("closure", resultList);
        response.put("found_element", closer.getElementToFind() != null);
        if (closer.getElementToFind() != null) {
            IntArray found = closer.getElementToFind();
            List<Integer> foundList = new ArrayList<>();
            for (int i = 0; i < found.universeSize(); i++) {
                foundList.add(found.get(i));
            }
            response.put("found_element_value", foundList);
        }
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Parse blocks constraint from string.
     * Format: "0,1;2,3" means indices 0,1 must be equal and 2,3 must be equal
     */
    private int[][] parseBlocks(String blocksStr) throws Exception {
        List<int[]> blocks = new ArrayList<>();
        String[] parts = blocksStr.split(";");
        for (String part : parts) {
            String[] indices = part.split(",");
            int[] block = new int[indices.length];
            for (int i = 0; i < indices.length; i++) {
                block[i] = Integer.parseInt(indices[i].trim());
            }
            blocks.add(block);
        }
        return blocks.toArray(new int[0][]);
    }
    
    /**
     * Parse values constraint from string.
     * Format: "0:1,2:0" means index 0 = 1, index 2 = 0
     */
    private int[][] parseValues(String valuesStr) throws Exception {
        List<int[]> values = new ArrayList<>();
        String[] parts = valuesStr.split(",");
        for (String part : parts) {
            String[] pair = part.split(":");
            if (pair.length != 2) {
                throw new Exception("Invalid values format: " + part);
            }
            int[] value = new int[2];
            value[0] = Integer.parseInt(pair[0].trim());
            value[1] = Integer.parseInt(pair[1].trim());
            values.add(value);
        }
        return values.toArray(new int[0][]);
    }
    
    /**
     * Parse set constraint from string.
     * Format: "0,1,2" means set {0,1,2}
     */
    private Set<Integer> parseSetConstraint(String setStr) throws Exception {
        Set<Integer> set = new HashSet<>();
        String[] parts = setStr.split(",");
        for (String part : parts) {
            set.add(Integer.parseInt(part.trim()));
        }
        return set;
    }
    
    /**
     * Parse partition from string.
     * Format: "[[0 1][2]]" or "|0 1|2|"
     */
    private Partition parsePartition(String partitionStr, int universeSize) throws Exception {
        // Try to parse as bracket notation first
        try {
            return new BasicPartition(partitionStr, universeSize);
        } catch (Exception e) {
            // If that fails, try creating without length
            try {
                return new BasicPartition(partitionStr);
            } catch (Exception e2) {
                // If that fails, create a trivial partition (all elements separate)
                return BasicPartition.zero(universeSize);
            }
        }
    }
    
    /**
     * Handle sg_close_with_homomorphism command - closure with homomorphism checking.
     */
    private void handleSgCloseWithHomomorphism(Map<String, String> options) throws Exception {
        int baseSize = getIntArg(options, "base_size", 2);
        int power = getIntArg(options, "power", 2);
        
        // Load ba2 algebra (ensures operations are available)
        SmallAlgebra base = loadBa2();
        BigProductAlgebra algebra = new BigProductAlgebra(base, power);
        
        // Parse generators
        String gensStr = options.get("generators");
        if (gensStr == null || gensStr.isEmpty()) {
            handleError("generators parameter is required", null);
            return;
        }
        List<IntArray> generators = parseGenerators(gensStr, power);
        
        // Create closer
        Closer closer = new Closer(algebra, generators);
        
        // Enable term map (required for homomorphism checking)
        closer.setTermMap(new HashMap<IntArray, org.uacalc.terms.Term>());
        
        // Parse image algebra generators
        String imageGensStr = options.get("image_generators");
        if (imageGensStr == null || imageGensStr.isEmpty()) {
            handleError("image_generators parameter is required", null);
            return;
        }
        String[] imageGenParts = imageGensStr.split(",");
        int[] imageGens = new int[imageGenParts.length];
        for (int i = 0; i < imageGenParts.length; i++) {
            imageGens[i] = Integer.parseInt(imageGenParts[i].trim());
        }
        
        // Set image algebra - for now, always use the base algebra as image
        // This works for homomorphisms from A^n to A (projection homomorphisms)
        // For homomorphisms from A^n to A^n, we would need a different approach
        closer.setImageAlgebra(base);
        
        // Set homomorphism from generators
        // Note: imageGens are indices into the image algebra universe
        // For ba2 (size 2), valid indices are 0,1
        // For ba2^2, we need indices 0-3 (representing [0,0], [0,1], [1,0], [1,1])
        // The indices are computed using Horner encoding: [a,b] -> a + b*baseSize
        // So for ba2^2: [0,0]=0, [0,1]=1, [1,0]=2, [1,1]=3
        closer.setHomomorphism(imageGens);
        
        // Compute closure using power method for power algebras
        // This ensures homomorphism checking works correctly
        List<IntArray> result;
        if (power > 1) {
            result = closer.sgClosePower();
        } else {
            result = closer.sgClose();
        }
        
        // Format result
        List<List<Integer>> resultList = new ArrayList<>();
        for (IntArray ia : result) {
            List<Integer> elem = new ArrayList<>();
            for (int i = 0; i < ia.universeSize(); i++) {
                elem.add(ia.get(i));
            }
            resultList.add(elem);
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "sg_close_with_homomorphism");
        response.put("base_size", baseSize);
        response.put("power", power);
        response.put("generators_count", generators.size());
        response.put("closure_size", result.size());
        response.put("closure", resultList);
        
        // Check for failing equation
        org.uacalc.eq.Equation failingEq = closer.getFailingEquation();
        if (failingEq != null) {
            response.put("failing_equation", failingEq.toString());
            response.put("has_failing_equation", true);
        } else {
            response.put("has_failing_equation", false);
        }
        
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle sg_close_with_operations_finding command - closure with operations finding.
     */
    private void handleSgCloseWithOperationsFinding(Map<String, String> options) throws Exception {
        int baseSize = getIntArg(options, "base_size", 2);
        int power = getIntArg(options, "power", 2);
        
        // Load ba2 algebra (ensures operations are available)
        SmallAlgebra base = loadBa2();
        BigProductAlgebra algebra = new BigProductAlgebra(base, power);
        
        // Parse generators
        String gensStr = options.get("generators");
        if (gensStr == null || gensStr.isEmpty()) {
            handleError("generators parameter is required", null);
            return;
        }
        List<IntArray> generators = parseGenerators(gensStr, power);
        
        // Parse operations to find - format: "arity:table1,table2,..."
        // For example, "2:0,1,2,1" means a binary operation with table [0,1,2,1]
        String opsStr = options.get("operations");
        if (opsStr == null || opsStr.isEmpty()) {
            handleError("operations parameter is required", null);
            return;
        }
        
        List<org.uacalc.alg.op.Operation> operationsToFind = parseOperations(opsStr, baseSize);
        
        // Create closer with term map (required for operations finding)
        // Use constructor that creates term map automatically
        Closer closer = new Closer(algebra, generators, true);
        
        // Set root algebra and operations
        closer.setRootAlgebra(base);
        closer.setOperations(operationsToFind);
        
        // Compute closure using power method for power algebras
        List<IntArray> result;
        if (power > 1) {
            result = closer.sgClosePower();
        } else {
            result = closer.sgClose();
        }
        
        // Format result
        List<List<Integer>> resultList = new ArrayList<>();
        for (IntArray ia : result) {
            List<Integer> elem = new ArrayList<>();
            for (int i = 0; i < ia.universeSize(); i++) {
                elem.add(ia.get(i));
            }
            resultList.add(elem);
        }
        
        // Get term map for operations
        Map<org.uacalc.alg.op.Operation, org.uacalc.terms.Term> termMapForOps = closer.getTermMapForOperations();
        Map<String, String> operationsFound = new HashMap<>();
        if (termMapForOps != null) {
            for (org.uacalc.alg.op.Operation op : termMapForOps.keySet()) {
                org.uacalc.terms.Term term = termMapForOps.get(op);
                operationsFound.put(op.symbol().name(), term.toString());
            }
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "sg_close_with_operations_finding");
        response.put("base_size", baseSize);
        response.put("power", power);
        response.put("generators_count", generators.size());
        response.put("closure_size", result.size());
        response.put("closure", resultList);
        response.put("operations_found_count", operationsFound.size());
        response.put("operations_found", operationsFound);
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Parse operations from string format: "arity:table1,table2,..."
     * Multiple operations can be separated by semicolons: "2:0,1,2,1;3:0,1,2,..."
     */
    private List<org.uacalc.alg.op.Operation> parseOperations(String opsStr, int setSize) throws Exception {
        List<org.uacalc.alg.op.Operation> operations = new ArrayList<>();
        
        String[] opStrings = opsStr.split(";");
        for (String opStr : opStrings) {
            opStr = opStr.trim();
            if (opStr.isEmpty()) continue;
            
            // Format: "arity:table" where table is comma-separated values
            int colonIndex = opStr.indexOf(':');
            if (colonIndex < 0) {
                throw new IllegalArgumentException("Invalid operation format (missing colon): " + opStr);
            }
            
            int arity = Integer.parseInt(opStr.substring(0, colonIndex).trim());
            String tableStr = opStr.substring(colonIndex + 1).trim();
            
            // Parse table
            String[] tableParts = tableStr.split(",");
            int[] table = new int[tableParts.length];
            for (int i = 0; i < tableParts.length; i++) {
                table[i] = Integer.parseInt(tableParts[i].trim());
            }
            
            // Create operation symbol
            org.uacalc.alg.op.OperationSymbol symbol = new org.uacalc.alg.op.OperationSymbol("f" + operations.size(), arity, false);
            
            // Create operation
            org.uacalc.alg.op.Operation op = org.uacalc.alg.op.Operations.makeIntOperation(symbol, setSize, table);
            operations.add(op);
        }
        
        return operations;
    }
    
    /**
     * Show usage information for the Closer wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "test --power 2",
            "sg_close --base_size 2 --power 2 --generators \"0,0;0,1\"",
            "sg_close_power --base_size 2 --power 2 --generators \"0,0;0,1\"",
            "sg_close_ba2_power --power 3 --generators \"0,0,1;1,1,0\"",
            "sg_close_free_algebra --num_gens 1 --power 3 --generators \"0,0,1;1,1,0\"",
            "sg_close_with_constraints --base_size 2 --power 2 --generators \"0,0;0,1\" --blocks \"0,1\"",
            "sg_close_with_homomorphism --base_size 2 --power 2 --generators \"0,0;0,1\" --image_generators \"0,1\"",
            "sg_close_with_operations_finding --base_size 2 --power 2 --generators \"0,0;0,1\" --operations \"2:0,1,1,0\"",
            "help"
        };
        
        showUsage("Closer", 
                 "CLI wrapper for org.uacalc.alg.Closer operations", 
                 examples);
    }
}

