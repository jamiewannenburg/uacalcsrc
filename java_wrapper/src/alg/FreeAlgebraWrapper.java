/* FreeAlgebraWrapper.java - CLI wrapper for org.uacalc.alg.FreeAlgebra
 * 
 * This wrapper exposes all public methods of the FreeAlgebra class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.op.Operation;
import org.uacalc.terms.*;
import org.uacalc.eq.*;
import org.uacalc.ui.tm.ProgressReport;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the FreeAlgebra class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class FreeAlgebraWrapper extends WrapperBase {
    
    private FreeAlgebra freeAlgebra;
    private SmallAlgebra baseAlgebra;
    private int numberOfGens;
    private String name;
    
    /**
     * Main entry point for the FreeAlgebra CLI wrapper.
     */
    public static void main(String[] args) {
        FreeAlgebraWrapper wrapper = new FreeAlgebraWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("FreeAlgebra wrapper failed", e);
        }
    }
    
    /**
     * Run the FreeAlgebra CLI wrapper with the given arguments.
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
                
            case "construct":
                handleConstruct(options);
                break;
                
            case "construct_with_name":
                handleConstructWithName(options);
                break;
                
            case "construct_with_progress":
                handleConstructWithProgress(options);
                break;
                
            case "construct_with_decompose":
                handleConstructWithDecompose(options);
                break;
                
            case "construct_with_relations":
                handleConstructWithRelations(options);
                break;
                
            case "idempotent_terms":
                handleIdempotentTerms(options);
                break;
                
            case "algebra_type":
                handleAlgebraType(options);
                break;
                
            case "automorphism":
                handleAutomorphism(options);
                break;
                
            case "find_equation":
                handleFindEquation(options);
                break;
                
            case "cardinality":
                handleCardinality(options);
                break;
                
            case "name":
                handleName(options);
                break;
                
            case "set_name":
                handleSetName(options);
                break;
                
            case "is_unary":
                handleIsUnary(options);
                break;
                
            case "is_idempotent":
                handleIsIdempotent(options);
                break;
                
            case "is_total":
                handleIsTotal(options);
                break;
                
            case "operations_count":
                handleOperationsCount(options);
                break;
                
            case "get_universe_list":
                handleGetUniverseList(options);
                break;
                
            case "get_universe_order":
                handleGetUniverseOrder(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    private void handleConstruct(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            handleError("FreeAlgebra not created. Use 'construct_with_name' first.", null);
            return;
        }
        
        String result = "{\"command\":\"construct\",\"name\":\"" + freeAlgebra.getName() + 
            "\",\"number_of_gens\":" + numberOfGens + 
            ",\"cardinality\":" + freeAlgebra.cardinality() + 
            ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleConstructWithName(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "F");
        String baseName = getRequiredArg(options, "base_name");
        int baseSize = getIntArg(options, "base_size", 2);
        int gens = getIntArg(options, "gens", 2);
        
        // Create a simple base algebra
        baseAlgebra = new BasicAlgebra(baseName, baseSize, new ArrayList<>());
        this.name = name;
        this.numberOfGens = gens;
        
        freeAlgebra = new FreeAlgebra(name, baseAlgebra, gens);
        
        String result = "{\"command\":\"construct_with_name\",\"name\":\"" + freeAlgebra.getName() + 
            "\",\"base_name\":\"" + baseName + 
            "\",\"base_size\":" + baseSize + 
            ",\"gens\":" + gens + 
            ",\"cardinality\":" + freeAlgebra.cardinality() + 
            ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleConstructWithProgress(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "F");
        String baseName = getRequiredArg(options, "base_name");
        int baseSize = getIntArg(options, "base_size", 2);
        int gens = getIntArg(options, "gens", 2);
        boolean makeUniverse = getBoolArg(options, "make_universe", true);
        boolean thinGens = getBoolArg(options, "thin_gens", true);
        boolean decompose = getBoolArg(options, "decompose", true);
        
        // Create a simple base algebra
        baseAlgebra = new BasicAlgebra(baseName, baseSize, new ArrayList<>());
        this.name = name;
        this.numberOfGens = gens;
        
        // Create progress report (use null for now)
        ProgressReport report = null;
        
        freeAlgebra = new FreeAlgebra(name, baseAlgebra, gens, makeUniverse, thinGens, decompose, null, report);
        
        String result = "{\"command\":\"construct_with_progress\",\"name\":\"" + freeAlgebra.getName() + 
            "\",\"base_name\":\"" + baseName + 
            "\",\"base_size\":" + baseSize + 
            ",\"gens\":" + gens + 
            ",\"make_universe\":" + makeUniverse + 
            ",\"thin_gens\":" + thinGens + 
            ",\"decompose\":" + decompose + 
            ",\"cardinality\":" + freeAlgebra.cardinality() + 
            ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleConstructWithDecompose(Map<String, String> options) throws Exception {
        String name = getOptionalArg(options, "name", "F");
        String baseName = getRequiredArg(options, "base_name");
        int baseSize = getIntArg(options, "base_size", 2);
        int gens = getIntArg(options, "gens", 2);
        boolean makeUniverse = getBoolArg(options, "make_universe", true);
        boolean thinGens = getBoolArg(options, "thin_gens", true);
        boolean decompose = getBoolArg(options, "decompose", true);
        
        // Create a simple base algebra
        baseAlgebra = new BasicAlgebra(baseName, baseSize, new ArrayList<>());
        this.name = name;
        this.numberOfGens = gens;
        
        freeAlgebra = new FreeAlgebra(name, baseAlgebra, gens, makeUniverse, thinGens, decompose, null, null);
        
        String result = "{\"command\":\"construct_with_decompose\",\"name\":\"" + freeAlgebra.getName() + 
            "\",\"base_name\":\"" + baseName + 
            "\",\"base_size\":" + baseSize + 
            ",\"gens\":" + gens + 
            ",\"make_universe\":" + makeUniverse + 
            ",\"thin_gens\":" + thinGens + 
            ",\"decompose\":" + decompose + 
            ",\"cardinality\":" + freeAlgebra.cardinality() + 
            ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleConstructWithRelations(Map<String, String> options) throws Exception {
        String baseName = getRequiredArg(options, "base_name");
        int baseSize = getIntArg(options, "base_size", 2);
        int gens = getIntArg(options, "gens", 2);
        
        // Create a simple base algebra
        baseAlgebra = new BasicAlgebra(baseName, baseSize, new ArrayList<>());
        this.name = "F";
        this.numberOfGens = gens;
        
        // Create empty relations list for now
        List<Equation> relations = new ArrayList<>();
        
        freeAlgebra = new FreeAlgebra(baseAlgebra, gens, relations, null);
        
        String result = "{\"command\":\"construct_with_relations\",\"name\":\"" + freeAlgebra.getName() + 
            "\",\"base_name\":\"" + baseName + 
            "\",\"base_size\":" + baseSize + 
            ",\"gens\":" + gens + 
            ",\"relations_count\":" + relations.size() + 
            ",\"cardinality\":" + freeAlgebra.cardinality() + 
            ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleIdempotentTerms(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            // Auto-create a default algebra for testing
            baseAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
            freeAlgebra = new FreeAlgebra("TestFree", baseAlgebra, 2);
        }
        
        List<Term> idempotentTerms = freeAlgebra.getIdempotentTerms();
        int count = idempotentTerms != null ? idempotentTerms.size() : 0;
        
        // Build terms array
        StringBuilder termsJson = new StringBuilder("[");
        if (idempotentTerms != null && !idempotentTerms.isEmpty()) {
            for (int i = 0; i < idempotentTerms.size(); i++) {
                if (i > 0) termsJson.append(",");
                termsJson.append("\"").append(idempotentTerms.get(i).toString()).append("\"");
            }
        }
        termsJson.append("]");
        
        String result = "{\"command\":\"idempotent_terms\",\"count\":" + count + 
            ",\"terms\":" + termsJson.toString() + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleAlgebraType(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            // Auto-create a default algebra for testing
            baseAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
            freeAlgebra = new FreeAlgebra("TestFree", baseAlgebra, 2);
        }
        
        SmallAlgebra.AlgebraType type = freeAlgebra.algebraType();
        String result = "{\"command\":\"algebra_type\",\"type\":\"" + type.toString() + "\",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleAutomorphism(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            // Auto-create a default algebra for testing
            baseAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
            freeAlgebra = new FreeAlgebra("TestFree", baseAlgebra, 2);
        }
        
        int x = getIntArg(options, "x", 0);
        int y = getIntArg(options, "y", 1);
        
        Operation result = freeAlgebra.switchXandYAutomorphism();
        boolean hasResult = result != null;
        
        String jsonResult = "{\"command\":\"automorphism\",\"x\":" + x + 
            ",\"y\":" + y + 
            ",\"has_result\":" + hasResult + 
            ",\"automorphism\":" + (result != null ? "\"" + result.toString() + "\"" : "null") +
            ",\"status\":\"success\"}";
        handleSuccess(jsonResult);
    }
    
    private void handleFindEquation(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            // Auto-create a default algebra for testing
            baseAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
            freeAlgebra = new FreeAlgebra("TestFree", baseAlgebra, 2);
        }
        
        String bName = getOptionalArg(options, "b_name", "B");
        int bSize = getIntArg(options, "b_size", 2);
        
        // Create algebra B
        SmallAlgebra b = new BasicAlgebra(bName, bSize, new ArrayList<>());
        
        // Create bGens array with default values
        int[] bGens = new int[bSize];
        for (int i = 0; i < bSize; i++) {
            bGens[i] = i;
        }
        
        Equation equation = FreeAlgebra.findEquationOfAnotB(freeAlgebra, b, bGens, null);
        boolean hasEquation = equation != null;
        
        String result = "{\"command\":\"find_equation\",\"b_name\":\"" + bName + 
            "\",\"b_size\":" + bSize + 
            ",\"has_equation\":" + hasEquation + 
            ",\"equation\":" + (equation != null ? "\"" + equation.toString() + "\"" : "null") +
            ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleCardinality(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            // Auto-create a default algebra for testing
            baseAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
            freeAlgebra = new FreeAlgebra("TestFree", baseAlgebra, 2);
        }
        
        int cardinality = freeAlgebra.cardinality();
        String result = "{\"command\":\"cardinality\",\"cardinality\":" + cardinality + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleName(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            // Auto-create a default algebra for testing
            baseAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
            freeAlgebra = new FreeAlgebra("TestFree", baseAlgebra, 2);
        }
        
        String name = freeAlgebra.getName();
        String result = "{\"command\":\"name\",\"name\":\"" + name + "\",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleSetName(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            // Auto-create a default algebra for testing
            baseAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
            freeAlgebra = new FreeAlgebra("TestFree", baseAlgebra, 2);
        }
        
        String newName = getRequiredArg(options, "name");
        freeAlgebra.setName(newName);
        
        String result = "{\"command\":\"set_name\",\"new_name\":\"" + newName + 
            "\",\"name\":\"" + newName + "\",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleIsUnary(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            // Auto-create a default algebra for testing
            baseAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
            freeAlgebra = new FreeAlgebra("TestFree", baseAlgebra, 2);
        }
        
        boolean isUnary = freeAlgebra.isUnary();
        String result = "{\"command\":\"is_unary\",\"is_unary\":" + isUnary + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleIsIdempotent(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            // Auto-create a default algebra for testing
            baseAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
            freeAlgebra = new FreeAlgebra("TestFree", baseAlgebra, 2);
        }
        
        boolean isIdempotent = freeAlgebra.isIdempotent();
        String result = "{\"command\":\"is_idempotent\",\"is_idempotent\":" + isIdempotent + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleIsTotal(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            // Auto-create a default algebra for testing
            baseAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
            freeAlgebra = new FreeAlgebra("TestFree", baseAlgebra, 2);
        }
        
        boolean isTotal = freeAlgebra.isTotal();
        String result = "{\"command\":\"is_total\",\"is_total\":" + isTotal + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleOperationsCount(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            // Auto-create a default algebra for testing
            baseAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
            freeAlgebra = new FreeAlgebra("TestFree", baseAlgebra, 2);
        }
        
        int count = freeAlgebra.operations().size();
        String result = "{\"command\":\"operations_count\",\"count\":" + count + 
            ",\"operations_count\":" + count + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleGetUniverseList(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            // Auto-create a default algebra for testing
            baseAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
            freeAlgebra = new FreeAlgebra("TestFree", baseAlgebra, 2);
        }
        
        List<?> universeList = freeAlgebra.getUniverseList();
        int universeSize = universeList != null ? universeList.size() : 0;
        
        // Build universe array
        StringBuilder universeJson = new StringBuilder("[");
        if (universeList != null && !universeList.isEmpty()) {
            for (int i = 0; i < universeList.size(); i++) {
                if (i > 0) universeJson.append(",");
                universeJson.append("\"").append(universeList.get(i).toString()).append("\"");
            }
        }
        universeJson.append("]");
        
        String result = "{\"command\":\"get_universe_list\",\"universe_size\":" + universeSize + 
            ",\"universe\":" + universeJson.toString() + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleGetUniverseOrder(Map<String, String> options) throws Exception {
        if (freeAlgebra == null) {
            // Auto-create a default algebra for testing
            baseAlgebra = new BasicAlgebra("TestBase", 2, new ArrayList<>());
            freeAlgebra = new FreeAlgebra("TestFree", baseAlgebra, 2);
        }
        
        boolean hasOrder = freeAlgebra.getUniverseOrder() != null;
        String result = "{\"command\":\"get_universe_order\",\"has_order\":" + hasOrder + ",\"status\":\"success\"}";
        handleSuccess(result);
    }
    
    private void handleTest(Map<String, String> options) throws Exception {
        // Create a test free algebra
        SmallAlgebra testBase = new BasicAlgebra("TestBase", 2, new ArrayList<>());
        FreeAlgebra testFree = new FreeAlgebra("TestFree", testBase, 2);
        
        // Test basic functionality
        int cardinality = testFree.cardinality();
        String name = testFree.getName();
        SmallAlgebra.AlgebraType type = testFree.algebraType();
        List<Term> idempotentTerms = testFree.getIdempotentTerms();
        int idempotentCount = idempotentTerms != null ? idempotentTerms.size() : 0;
        
        String result = "{\"command\":\"test\",\"name\":\"" + name + 
            ",\"cardinality\":" + cardinality + 
            ",\"algebra_type\":\"" + type.toString() + 
            ",\"idempotent_terms_count\":" + idempotentCount + 
            ",\"status\":\"success\",\"message\":\"Test completed successfully\"}";
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the FreeAlgebra wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "construct_with_name --name F --base_name TestBase --base_size 2 --gens 2",
            "construct_with_progress --name F --base_name TestBase --base_size 2 --gens 2 --make_universe true --thin_gens true --decompose true",
            "construct_with_decompose --name F --base_name TestBase --base_size 2 --gens 2 --make_universe true --thin_gens true --decompose true",
            "construct_with_relations --base_name TestBase --base_size 2 --gens 2",
            "idempotent_terms",
            "algebra_type",
            "automorphism --x 0 --y 1",
            "find_equation --b_name B --b_size 2",
            "cardinality",
            "name",
            "set_name --name NewName",
            "is_unary",
            "is_idempotent",
            "is_total",
            "operations_count",
            "get_universe_list",
            "get_universe_order",
            "test"
        };
        
        showUsage("FreeAlgebra", 
                 "CLI wrapper for org.uacalc.alg.FreeAlgebra operations", 
                 examples);
    }
}
