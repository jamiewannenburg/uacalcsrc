/* AlgebrasWrapper.java - CLI wrapper for org.uacalc.alg.Algebras
 * 
 * This wrapper exposes all public methods of the Algebras class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import java.io.*;
import org.uacalc.alg.*;
import org.uacalc.alg.op.*;
import org.uacalc.io.*;
import org.uacalc.terms.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Algebras class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class AlgebrasWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Algebras CLI wrapper.
     */
    public static void main(String[] args) {
        AlgebrasWrapper wrapper = new AlgebrasWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Algebras wrapper failed", e);
        }
    }
    
    /**
     * Run the Algebras CLI wrapper with the given arguments.
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
                
            case "isEndomorphism":
                handleIsEndomorphism(options);
                break;
                
            case "isHomomorphism":
                handleIsHomomorphism(options);
                break;
                
            case "jonssonTerms":
                handleJonssonTerms(options);
                break;
                
            case "jonssonLevel":
                handleJonssonLevel(options);
                break;
                
            case "matrixPower":
                handleMatrixPower(options);
                break;
                
            case "findNUF":
                handleFindNUF(options);
                break;
                
            case "ternaryDiscriminatorAlgebra":
                handleTernaryDiscriminatorAlgebra(options);
                break;
                
            case "fullTransformationSemigroup":
                handleFullTransformationSemigroup(options);
                break;
                
            case "memberOfQuasivariety":
                handleMemberOfQuasivariety(options);
                break;
                
            case "memberOfQuasivarietyList":
                handleMemberOfQuasivarietyList(options);
                break;
                
            case "memberOfQuasivarietyGenByProperSubs":
                handleMemberOfQuasivarietyGenByProperSubs(options);
                break;
                
            case "makeRandomAlgebra":
                handleMakeRandomAlgebra(options);
                break;
                
            case "makeRandomAlgebraWithSeed":
                handleMakeRandomAlgebraWithSeed(options);
                break;
                
            case "makeRandomAlgebraWithArities":
                handleMakeRandomAlgebraWithArities(options);
                break;
                
            case "makeRandomAlgebraWithAritiesAndSeed":
                handleMakeRandomAlgebraWithAritiesAndSeed(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle isEndomorphism command - test if an operation is an endomorphism.
     */
    private void handleIsEndomorphism(Map<String, String> options) throws Exception {
        // Get algebra file path or create test algebra
        String algFile = options.get("algebra");
        SmallAlgebra alg;
        
        if (algFile != null && !algFile.isEmpty()) {
            // Load algebra from file
            File file = new File(algFile);
            if (!file.exists()) {
                handleError("Algebra file not found: " + algFile, null);
                return;
            }
            alg = AlgebraIO.readAlgebraFile(file);
        } else {
            // Create a simple test algebra
            int size = getIntArg(options, "size", 2);
            alg = makeTestAlgebra(size);
        }
        
        // Get operation - can be specified as:
        // 1. Operation file (not supported yet)
        // 2. Table specification: "arity:table" where table is comma-separated
        String opSpec = options.get("operation");
        if (opSpec == null || opSpec.isEmpty()) {
            handleError("Required argument missing: operation", null);
            return;
        }
        
        Operation endo = parseOperation(opSpec, alg.cardinality());
        
        // Call Java method
        boolean result = Algebras.isEndomorphism(endo, alg);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "isEndomorphism");
        response.put("result", result);
        response.put("algebra_size", alg.cardinality());
        response.put("operation_arity", endo.arity());
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Parse an operation from string specification.
     * Format: "arity:table" where table is comma-separated values
     * Example: "1:0,1" for identity on 2-element set
     */
    private Operation parseOperation(String opSpec, int setSize) throws Exception {
        int colonIndex = opSpec.indexOf(':');
        if (colonIndex < 0) {
            throw new IllegalArgumentException("Invalid operation format (missing colon): " + opSpec);
        }
        
        int arity = Integer.parseInt(opSpec.substring(0, colonIndex).trim());
        String tableStr = opSpec.substring(colonIndex + 1).trim();
        
        // Parse table
        String[] tableParts = tableStr.split(",");
        int[] table = new int[tableParts.length];
        for (int i = 0; i < tableParts.length; i++) {
            table[i] = Integer.parseInt(tableParts[i].trim());
        }
        
        // Create operation symbol
        OperationSymbol symbol = new OperationSymbol("endo", arity, false);
        
        // Create operation
        Operation op = Operations.makeIntOperation(symbol, setSize, table);
        
        return op;
    }
    
    /**
     * Create a simple test algebra with given size.
     */
    private SmallAlgebra makeTestAlgebra(int size) throws Exception {
        // Create a simple algebra with a binary operation (first projection)
        List<Operation> ops = new ArrayList<>();
        
        OperationSymbol sym = new OperationSymbol("f", 2, false);
        int[] table = new int[size * size];
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                table[i * size + j] = i; // First projection
            }
        }
        Operation op = Operations.makeIntOperation(sym, size, table);
        ops.add(op);
        
        return new BasicAlgebra("TestAlg", size, ops);
    }
    
    /**
     * Create a test similarity type.
     */
    private SimilarityType createTestSimilarityType() throws Exception {
        List<OperationSymbol> symbols = new ArrayList<>();
        symbols.add(new OperationSymbol("f", 2, false));
        symbols.add(new OperationSymbol("g", 1, false));
        return new SimilarityType(symbols);
    }
    
    
    /**
     * Handle isHomomorphism command - test if a map is a homomorphism.
     */
    private void handleIsHomomorphism(Map<String, String> options) throws Exception {
        // Get algebra files or create test algebras
        String alg0File = options.get("algebra0");
        String alg1File = options.get("algebra1");
        SmallAlgebra alg0;
        SmallAlgebra alg1;
        
        if (alg0File != null && !alg0File.isEmpty() && alg1File != null && !alg1File.isEmpty()) {
            // Load algebras from files
            File file0 = new File(alg0File);
            File file1 = new File(alg1File);
            if (!file0.exists()) {
                handleError("Algebra file not found: " + alg0File, null);
                return;
            }
            if (!file1.exists()) {
                handleError("Algebra file not found: " + alg1File, null);
                return;
            }
            alg0 = AlgebraIO.readAlgebraFile(file0);
            alg1 = AlgebraIO.readAlgebraFile(file1);
        } else {
            // Create simple test algebras
            int size = getIntArg(options, "size", 2);
            alg0 = makeTestAlgebra(size);
            alg1 = makeTestAlgebra(size);
        }
        
        // Get map - can be specified as comma-separated values
        String mapSpec = options.get("map");
        if (mapSpec == null || mapSpec.isEmpty()) {
            handleError("Required argument missing: map", null);
            return;
        }
        
        int[] map = parseMap(mapSpec, alg0.cardinality());
        
        // Call Java method
        boolean result = Algebras.isHomomorphism(map, alg0, alg1);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "isHomomorphism");
        response.put("result", result);
        response.put("algebra0_size", alg0.cardinality());
        response.put("algebra1_size", alg1.cardinality());
        response.put("map_size", map.length);
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Parse a map from string specification.
     * Format: comma-separated values
     * Example: "0,1" for identity map on 2-element set
     */
    private int[] parseMap(String mapSpec, int expectedSize) throws Exception {
        String[] parts = mapSpec.split(",");
        int[] map = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            map[i] = Integer.parseInt(parts[i].trim());
        }
        
        if (map.length != expectedSize) {
            throw new IllegalArgumentException(
                "Map size " + map.length + " does not match algebra size " + expectedSize);
        }
        
        return map;
    }
    
    /**
     * Handle jonssonTerms command - find Jonsson terms for an algebra.
     */
    private void handleJonssonTerms(Map<String, String> options) throws Exception {
        // Get algebra file path
        String algFile = options.get("algebra");
        if (algFile == null || algFile.isEmpty()) {
            handleError("Required argument missing: algebra", null);
            return;
        }
        
        // Load algebra from file
        File file = new File(algFile);
        if (!file.exists()) {
            handleError("Algebra file not found: " + algFile, null);
            return;
        }
        SmallAlgebra alg = AlgebraIO.readAlgebraFile(file);
        
        // Call Java method
        List<Term> terms = Algebras.jonssonTerms(alg);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "jonssonTerms");
        response.put("algebra", alg.getName());
        response.put("algebra_size", alg.cardinality());
        
        if (terms != null && !terms.isEmpty()) {
            response.put("terms_found", true);
            response.put("count", terms.size());
            
            List<String> termStrings = new ArrayList<>();
            for (Term term : terms) {
                termStrings.add(term.toString());
            }
            response.put("terms", termStrings);
        } else {
            response.put("terms_found", false);
            response.put("count", 0);
        }
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle jonssonLevel command - get Jonsson level for an algebra.
     */
    private void handleJonssonLevel(Map<String, String> options) throws Exception {
        // Get algebra file path
        String algFile = options.get("algebra");
        if (algFile == null || algFile.isEmpty()) {
            handleError("Required argument missing: algebra", null);
            return;
        }
        
        // Load algebra from file
        File file = new File(algFile);
        if (!file.exists()) {
            handleError("Algebra file not found: " + algFile, null);
            return;
        }
        SmallAlgebra alg = AlgebraIO.readAlgebraFile(file);
        
        // Call Java method
        int level = Algebras.jonssonLevel(alg);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "jonssonLevel");
        response.put("algebra", alg.getName());
        response.put("algebra_size", alg.cardinality());
        response.put("level", level);
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle matrixPower command - create a matrix power algebra.
     */
    private void handleMatrixPower(Map<String, String> options) throws Exception {
        // Get algebra file path or create test algebra
        String algFile = options.get("algebra");
        SmallAlgebra alg;
        
        if (algFile != null && !algFile.isEmpty()) {
            // Load algebra from file
            File file = new File(algFile);
            if (!file.exists()) {
                handleError("Algebra file not found: " + algFile, null);
                return;
            }
            alg = AlgebraIO.readAlgebraFile(file);
        } else {
            // Create a simple test algebra
            int size = getIntArg(options, "size", 2);
            alg = makeTestAlgebra(size);
        }
        
        // Get power k
        int k = getIntArg(options, "k", 2);
        if (k <= 0) {
            handleError("Power k must be positive", null);
            return;
        }
        
        // Call Java method
        SmallAlgebra result = Algebras.matrixPower(alg, k);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "matrixPower");
        response.put("input_algebra", alg.getName());
        response.put("input_size", alg.cardinality());
        response.put("power", k);
        response.put("result_algebra", result.getName());
        response.put("result_size", result.cardinality());
        response.put("operations_count", result.operations().size());
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle findNUF command - find a near unanimity term of the given arity.
     */
    private void handleFindNUF(Map<String, String> options) throws Exception {
        // Get algebra file path
        String algFile = options.get("algebra");
        if (algFile == null || algFile.isEmpty()) {
            handleError("Required argument missing: algebra", null);
            return;
        }
        
        // Load algebra from file
        File file = new File(algFile);
        if (!file.exists()) {
            handleError("Algebra file not found: " + algFile, null);
            return;
        }
        SmallAlgebra alg = AlgebraIO.readAlgebraFile(file);
        
        // Get arity
        int arity = getIntArg(options, "arity", 3);
        if (arity < 3) {
            handleError("Arity must be at least 3", null);
            return;
        }
        
        // Call Java method
        Term term = Algebras.findNUF(alg, arity);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "findNUF");
        response.put("algebra", alg.getName());
        response.put("algebra_size", alg.cardinality());
        response.put("arity", arity);
        
        if (term != null) {
            response.put("term_found", true);
            response.put("term", term.toString());
        } else {
            response.put("term_found", false);
            response.put("term", null);
        }
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle ternaryDiscriminatorAlgebra command - create a ternary discriminator algebra.
     */
    private void handleTernaryDiscriminatorAlgebra(Map<String, String> options) throws Exception {
        // Get cardinality
        int card = getIntArg(options, "card", 3);
        if (card <= 0) {
            handleError("Cardinality must be positive", null);
            return;
        }
        
        // Call Java method
        SmallAlgebra result = Algebras.ternaryDiscriminatorAlgebra(card);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "ternaryDiscriminatorAlgebra");
        response.put("cardinality", card);
        response.put("result_algebra", result.getName());
        response.put("result_size", result.cardinality());
        response.put("operations_count", result.operations().size());
        
        // Check that it has exactly one operation (the discriminator)
        if (result.operations().size() == 1) {
            Operation discOp = result.operations().get(0);
            response.put("operation_arity", discOp.arity());
            response.put("operation_name", discOp.symbol().name());
        }
        
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle fullTransformationSemigroup command - create the full transformation semigroup.
     */
    private void handleFullTransformationSemigroup(Map<String, String> options) throws Exception {
        // Get n
        int n = getIntArg(options, "n", 3);
        if (n <= 0) {
            handleError("n must be positive", null);
            return;
        }
        if (n > 9) {
            handleError("n can be at most 9", null);
            return;
        }
        
        // Get boolean flags (default to false if not provided)
        boolean includeConstants = "true".equalsIgnoreCase(options.get("includeConstants")) || 
                                   "1".equals(options.get("includeConstants"));
        boolean includeId = "true".equalsIgnoreCase(options.get("includeId")) || 
                           "1".equals(options.get("includeId"));
        
        // Call Java method
        SmallAlgebra result = withSilencedStdout(() -> Algebras.fullTransformationSemigroup(n, includeConstants, includeId));
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "fullTransformationSemigroup");
        response.put("n", n);
        response.put("include_constants", includeConstants);
        response.put("include_id", includeId);
        response.put("result_algebra", result.getName());
        response.put("result_size", result.cardinality());
        response.put("operations_count", result.operations().size());
        
        // Add operation details
        List<Map<String, Object>> opsInfo = new ArrayList<>();
        for (Operation op : result.operations()) {
            Map<String, Object> opInfo = new HashMap<>();
            opInfo.put("name", op.symbol().name());
            opInfo.put("arity", op.arity());
            opsInfo.add(opInfo);
        }
        response.put("operations", opsInfo);
        
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle memberOfQuasivariety command - test if algebra A is in the quasivariety generated by B.
     */
    private void handleMemberOfQuasivariety(Map<String, String> options) throws Exception {
        // Get algebra A file path or create test algebra
        String algAFile = options.get("algebra_a");
        SmallAlgebra algA;
        
        if (algAFile != null && !algAFile.isEmpty()) {
            File file = new File(algAFile);
            if (!file.exists()) {
                handleError("Algebra A file not found: " + algAFile, null);
                return;
            }
            algA = AlgebraIO.readAlgebraFile(file);
        } else {
            int size = getIntArg(options, "size_a", 2);
            algA = makeTestAlgebra(size);
        }
        
        // Get algebra B file path or create test algebra
        String algBFile = options.get("algebra_b");
        SmallAlgebra algB;
        
        if (algBFile != null && !algBFile.isEmpty()) {
            File file = new File(algBFile);
            if (!file.exists()) {
                handleError("Algebra B file not found: " + algBFile, null);
                return;
            }
            algB = AlgebraIO.readAlgebraFile(file);
        } else {
            int size = getIntArg(options, "size_b", 2);
            algB = makeTestAlgebra(size);
        }
        
        // Call Java method
        List<Homomorphism> homos = Algebras.memberOfQuasivariety(algA, algB, null);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "memberOfQuasivariety");
        response.put("algebra_a", algA.getName());
        response.put("algebra_a_size", algA.cardinality());
        response.put("algebra_b", algB.getName());
        response.put("algebra_b_size", algB.cardinality());
        response.put("in_quasivariety", homos != null);
        
        if (homos != null) {
            response.put("homomorphisms_count", homos.size());
            List<Map<String, Object>> homoMaps = new ArrayList<>();
            for (Homomorphism homo : homos) {
                Map<String, Object> homoMap = new HashMap<>();
                homoMap.put("domain", homo.getDomain().getName());
                homoMap.put("range", homo.getRange().getName());
                homoMap.put("map", homo.getMap());
                homoMaps.add(homoMap);
            }
            response.put("homomorphisms", homoMaps);
        } else {
            response.put("homomorphisms_count", 0);
        }
        
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle memberOfQuasivarietyList command - test if algebra A is in the quasivariety generated by a list of algebras.
     */
    private void handleMemberOfQuasivarietyList(Map<String, String> options) throws Exception {
        // Get algebra A file path or create test algebra
        String algAFile = options.get("algebra_a");
        SmallAlgebra algA;
        
        if (algAFile != null && !algAFile.isEmpty()) {
            File file = new File(algAFile);
            if (!file.exists()) {
                handleError("Algebra A file not found: " + algAFile, null);
                return;
            }
            algA = AlgebraIO.readAlgebraFile(file);
        } else {
            int size = getIntArg(options, "size_a", 2);
            algA = makeTestAlgebra(size);
        }
        
        // Get list of generating algebras
        String genAlgsFile = options.get("gen_algs_file");
        List<SmallAlgebra> genAlgs = new ArrayList<>();
        
        if (genAlgsFile != null && !genAlgsFile.isEmpty()) {
            // Load from file (assuming it's a list file)
            List<SmallAlgebra> algs = AlgebraIO.readAlgebraListFile(new File(genAlgsFile));
            genAlgs.addAll(algs);
        } else {
            // Create test algebras
            String genAlgsStr = options.get("gen_algs");
            if (genAlgsStr != null && !genAlgsStr.isEmpty()) {
                // Comma-separated list of algebra files
                String[] files = genAlgsStr.split(",");
                for (String file : files) {
                    File f = new File(file.trim());
                    if (f.exists()) {
                        genAlgs.add(AlgebraIO.readAlgebraFile(f));
                    }
                }
            } else {
                // Create default test algebra
                int size = getIntArg(options, "size_b", 2);
                genAlgs.add(makeTestAlgebra(size));
            }
        }
        
        if (genAlgs.isEmpty()) {
            handleError("No generating algebras specified", null);
            return;
        }
        
        // Call Java method
        List<Homomorphism> homos = Algebras.memberOfQuasivariety(algA, genAlgs, null);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "memberOfQuasivarietyList");
        response.put("algebra_a", algA.getName());
        response.put("algebra_a_size", algA.cardinality());
        response.put("generating_algebras_count", genAlgs.size());
        
        List<String> genAlgNames = new ArrayList<>();
        for (SmallAlgebra alg : genAlgs) {
            genAlgNames.add(alg.getName());
        }
        response.put("generating_algebras", genAlgNames);
        
        response.put("in_quasivariety", homos != null);
        
        if (homos != null) {
            response.put("homomorphisms_count", homos.size());
            List<Map<String, Object>> homoMaps = new ArrayList<>();
            for (Homomorphism homo : homos) {
                Map<String, Object> homoMap = new HashMap<>();
                homoMap.put("domain", homo.getDomain().getName());
                homoMap.put("range", homo.getRange().getName());
                homoMap.put("map", homo.getMap());
                homoMaps.add(homoMap);
            }
            response.put("homomorphisms", homoMaps);
        } else {
            response.put("homomorphisms_count", 0);
        }
        
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle memberOfQuasivarietyGenByProperSubs command - test if algebra A can be embedded into a product of proper subalgebras of A.
     */
    private void handleMemberOfQuasivarietyGenByProperSubs(Map<String, String> options) throws Exception {
        // Get algebra A file path or create test algebra
        String algAFile = options.get("algebra");
        SmallAlgebra algA;
        
        if (algAFile != null && !algAFile.isEmpty()) {
            File file = new File(algAFile);
            if (!file.exists()) {
                handleError("Algebra A file not found: " + algAFile, null);
                return;
            }
            algA = AlgebraIO.readAlgebraFile(file);
        } else {
            int size = getIntArg(options, "size", 2);
            algA = makeTestAlgebra(size);
        }
        
        // Call Java method
        List<Homomorphism> homos = Algebras.memberOfQuasivarietyGenByProperSubs(algA, null);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "memberOfQuasivarietyGenByProperSubs");
        response.put("algebra", algA.getName());
        response.put("algebra_size", algA.cardinality());
        response.put("can_be_embedded", homos != null);
        
        if (homos != null) {
            response.put("homomorphisms_count", homos.size());
            List<Map<String, Object>> homoMaps = new ArrayList<>();
            for (Homomorphism homo : homos) {
                Map<String, Object> homoMap = new HashMap<>();
                homoMap.put("domain", homo.getDomain().getName());
                homoMap.put("range", homo.getRange().getName());
                homoMap.put("map", homo.getMap());
                homoMaps.add(homoMap);
            }
            response.put("homomorphisms", homoMaps);
        } else {
            response.put("homomorphisms_count", 0);
        }
        
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle makeRandomAlgebra command - create a random algebra with similarity type.
     */
    private void handleMakeRandomAlgebra(Map<String, String> options) throws Exception {
        int n = getIntArg(options, "n", 3);
        if (n <= 0) {
            handleError("Size n must be positive", null);
            return;
        }
        
        // Create a test similarity type (binary operation)
        SimilarityType simType = createTestSimilarityType();
        
        // Call Java method
        SmallAlgebra result = Algebras.makeRandomAlgebra(n, simType);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "makeRandomAlgebra");
        response.put("size", n);
        response.put("result_algebra", result.getName());
        response.put("result_size", result.cardinality());
        response.put("operations_count", result.operations().size());
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle makeRandomAlgebraWithSeed command - create a random algebra with similarity type and seed.
     */
    private void handleMakeRandomAlgebraWithSeed(Map<String, String> options) throws Exception {
        int n = getIntArg(options, "n", 3);
        if (n <= 0) {
            handleError("Size n must be positive", null);
            return;
        }
        
        long seed = getLongArg(options, "seed", 12345L);
        
        // Create a test similarity type (binary operation)
        SimilarityType simType = createTestSimilarityType();
        
        // Call Java method
        SmallAlgebra result = Algebras.makeRandomAlgebra(n, simType, seed);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "makeRandomAlgebraWithSeed");
        response.put("size", n);
        response.put("seed", seed);
        response.put("result_algebra", result.getName());
        response.put("result_size", result.cardinality());
        response.put("operations_count", result.operations().size());
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle makeRandomAlgebraWithArities command - create a random algebra with arities.
     */
    private void handleMakeRandomAlgebraWithArities(Map<String, String> options) throws Exception {
        int n = getIntArg(options, "n", 3);
        if (n <= 0) {
            handleError("Size n must be positive", null);
            return;
        }
        
        // Get arities from comma-separated string or use default
        String aritiesStr = options.get("arities");
        int[] arities;
        if (aritiesStr != null && !aritiesStr.isEmpty()) {
            String[] parts = aritiesStr.split(",");
            arities = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                arities[i] = Integer.parseInt(parts[i].trim());
            }
        } else {
            // Default: one binary operation
            arities = new int[]{2};
        }
        
        // Call Java method
        SmallAlgebra result = Algebras.makeRandomAlgebra(n, arities);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "makeRandomAlgebraWithArities");
        response.put("size", n);
        response.put("arities", arities);
        response.put("result_algebra", result.getName());
        response.put("result_size", result.cardinality());
        response.put("operations_count", result.operations().size());
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Handle makeRandomAlgebraWithAritiesAndSeed command - create a random algebra with arities and seed.
     */
    private void handleMakeRandomAlgebraWithAritiesAndSeed(Map<String, String> options) throws Exception {
        int n = getIntArg(options, "n", 3);
        if (n <= 0) {
            handleError("Size n must be positive", null);
            return;
        }
        
        // Get arities from comma-separated string or use default
        String aritiesStr = options.get("arities");
        int[] arities;
        if (aritiesStr != null && !aritiesStr.isEmpty()) {
            String[] parts = aritiesStr.split(",");
            arities = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                arities[i] = Integer.parseInt(parts[i].trim());
            }
        } else {
            // Default: one binary operation
            arities = new int[]{2};
        }
        
        long seed = getLongArg(options, "seed", 12345L);
        
        // Call Java method
        SmallAlgebra result = Algebras.makeRandomAlgebra(n, arities, seed);
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "makeRandomAlgebraWithAritiesAndSeed");
        response.put("size", n);
        response.put("arities", arities);
        response.put("seed", seed);
        response.put("result_algebra", result.getName());
        response.put("result_size", result.cardinality());
        response.put("operations_count", result.operations().size());
        response.put("status", "success");
        
        handleSuccess(response);
    }
    
    /**
     * Show usage information for the Algebras wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "isEndomorphism --algebra algebras/ba2.ua --operation \"1:0,1\"",
            "isEndomorphism --size 2 --operation \"1:0,1\"",
            "matrixPower --size 2 --k 3",
            "matrixPower --algebra algebras/ba2.ua --k 2",
            "isHomomorphism --algebra0 algebras/ba2.ua --algebra1 algebras/ba2.ua --map \"0,1\"",
            "isHomomorphism --size 2 --map \"0,1\"",
            "jonssonTerms --algebra algebras/ba2.ua",
            "jonssonLevel --algebra algebras/ba2.ua",
            "findNUF --algebra algebras/ba2.ua --arity 3",
            "ternaryDiscriminatorAlgebra --card 3",
            "fullTransformationSemigroup --n 3 --includeConstants true --includeId true",
            "memberOfQuasivarietyGenByProperSubs --algebra algebras/lat3.ua",
            "memberOfQuasivarietyGenByProperSubs --size 3",
            "makeRandomAlgebra --n 3",
            "makeRandomAlgebraWithSeed --n 3 --seed 12345",
            "makeRandomAlgebraWithArities --n 3 --arities \"2,1\"",
            "makeRandomAlgebraWithAritiesAndSeed --n 3 --arities \"2,1\" --seed 12345",
            "help"
        };
        
        showUsage("Algebras", 
                 "CLI wrapper for org.uacalc.alg.Algebras operations", 
                 examples);
    }
}
