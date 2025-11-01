/* MalcevWrapper.java - CLI wrapper for org.uacalc.alg.Malcev
 * 
 * This wrapper exposes all public methods of the Malcev class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.terms.*;
import org.uacalc.io.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Malcev class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class MalcevWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Malcev CLI wrapper.
     */
    public static void main(String[] args) {
        MalcevWrapper wrapper = new MalcevWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Malcev wrapper failed", e);
        }
    }
    
    /**
     * Run the Malcev CLI wrapper with the given arguments.
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
                
            case "malcev_term":
                handleMalcevTerm(options);
                break;
                
            case "majority_term":
                handleMajorityTerm(options);
                break;
                
            case "minority_term":
                handleMinorityTerm(options);
                break;
                
            case "pixley_term":
                handlePixleyTerm(options);
                break;
                
            case "nu_term":
                handleNuTerm(options);
                break;
                
            case "weak_majority_term":
                handleWeakMajorityTerm(options);
                break;
                
            case "semilattice_term":
                handleSemilatticeTerm(options);
                break;
                
            case "difference_term":
                handleDifferenceTerm(options);
                break;
                
            case "jonsson_terms":
                handleJonssonTerms(options);
                break;
                
            case "is_congruence_modular":
                handleIsCongruenceModular(options);
                break;
                
            case "is_congruence_modular_idempotent":
                handleIsCongruenceModularIdempotent(options);
                break;
                
            case "is_congruence_dist_idempotent":
                handleIsCongruenceDistIdempotent(options);
                break;
                
            case "sd_meet_idempotent":
                handleSdMeetIdempotent(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Run basic test to verify wrapper functionality.
     */
    private void handleTest(Map<String, String> options) {
        handleSuccess("Malcev wrapper is working correctly");
    }
    
    /**
     * Find a Malcev term for the algebra.
     */
    private void handleMalcevTerm(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        // Load algebra from file
        SmallAlgebra alg = loadAlgebra(algebraPath);
        
        // Find Malcev term
        Term term = Malcev.malcevTerm(alg);
        
        // Return result
        Map<String, Object> result = new HashMap<>();
        result.put("command", "malcev_term");
        result.put("algebra", alg.getName());
        result.put("cardinality", alg.cardinality());
        
        if (term != null) {
            result.put("term_found", true);
            result.put("term", term.toString());
        } else {
            result.put("term_found", false);
        }
        
        handleSuccess(result);
    }
    
    /**
     * Find a majority term for the algebra.
     */
    private void handleMajorityTerm(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        SmallAlgebra alg = loadAlgebra(algebraPath);
        Term term = Malcev.majorityTerm(alg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "majority_term");
        result.put("algebra", alg.getName());
        
        if (term != null) {
            result.put("term_found", true);
            result.put("term", term.toString());
        } else {
            result.put("term_found", false);
        }
        
        handleSuccess(result);
    }
    
    /**
     * Find a minority term for the algebra.
     */
    private void handleMinorityTerm(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        SmallAlgebra alg = loadAlgebra(algebraPath);
        Term term = Malcev.minorityTerm(alg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "minority_term");
        result.put("algebra", alg.getName());
        
        if (term != null) {
            result.put("term_found", true);
            result.put("term", term.toString());
        } else {
            result.put("term_found", false);
        }
        
        handleSuccess(result);
    }
    
    /**
     * Find a Pixley term for the algebra.
     */
    private void handlePixleyTerm(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        SmallAlgebra alg = loadAlgebra(algebraPath);
        Term term = Malcev.pixleyTerm(alg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "pixley_term");
        result.put("algebra", alg.getName());
        
        if (term != null) {
            result.put("term_found", true);
            result.put("term", term.toString());
        } else {
            result.put("term_found", false);
        }
        
        handleSuccess(result);
    }
    
    /**
     * Find a near unanimity term of the given arity.
     */
    private void handleNuTerm(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        int arity = getIntArg(options, "arity", 3);
        
        SmallAlgebra alg = loadAlgebra(algebraPath);
        Term term = Malcev.nuTerm(alg, arity);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "nu_term");
        result.put("algebra", alg.getName());
        result.put("arity", arity);
        
        if (term != null) {
            result.put("term_found", true);
            result.put("term", term.toString());
        } else {
            result.put("term_found", false);
        }
        
        handleSuccess(result);
    }
    
    /**
     * Find a weak majority term for the algebra.
     */
    private void handleWeakMajorityTerm(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        SmallAlgebra alg = loadAlgebra(algebraPath);
        Term term = Malcev.weakMajorityTerm(alg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "weak_majority_term");
        result.put("algebra", alg.getName());
        
        if (term != null) {
            result.put("term_found", true);
            result.put("term", term.toString());
        } else {
            result.put("term_found", false);
        }
        
        handleSuccess(result);
    }
    
    /**
     * Find a semilattice term for the algebra.
     */
    private void handleSemilatticeTerm(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        SmallAlgebra alg = loadAlgebra(algebraPath);
        Term term = Malcev.semilatticeTerm(alg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "semilattice_term");
        result.put("algebra", alg.getName());
        
        if (term != null) {
            result.put("term_found", true);
            result.put("term", term.toString());
        } else {
            result.put("term_found", false);
        }
        
        handleSuccess(result);
    }
    
    /**
     * Find a difference term for the algebra.
     */
    private void handleDifferenceTerm(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        SmallAlgebra alg = loadAlgebra(algebraPath);
        Term term = Malcev.differenceTerm(alg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "difference_term");
        result.put("algebra", alg.getName());
        
        if (term != null) {
            result.put("term_found", true);
            result.put("term", term.toString());
        } else {
            result.put("term_found", false);
        }
        
        handleSuccess(result);
    }
    
    /**
     * Find Jonsson terms for the algebra.
     */
    private void handleJonssonTerms(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        SmallAlgebra alg = loadAlgebra(algebraPath);
        List<Term> terms = Malcev.jonssonTerms(alg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "jonsson_terms");
        result.put("algebra", alg.getName());
        
        if (terms != null && !terms.isEmpty()) {
            result.put("terms_found", true);
            result.put("count", terms.size());
            
            List<String> termStrings = new ArrayList<>();
            for (Term term : terms) {
                termStrings.add(term.toString());
            }
            result.put("terms", termStrings);
        } else {
            result.put("terms_found", false);
            result.put("count", 0);
        }
        
        handleSuccess(result);
    }
    
    /**
     * Test if the variety generated by the algebra is congruence modular.
     */
    private void handleIsCongruenceModular(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        SmallAlgebra alg = loadAlgebra(algebraPath);
        boolean isModular = Malcev.congruenceModularVariety(alg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "is_congruence_modular");
        result.put("algebra", alg.getName());
        result.put("is_modular", isModular);
        
        handleSuccess(result);
    }
    
    /**
     * Test if an idempotent algebra is congruence modular.
     */
    private void handleIsCongruenceModularIdempotent(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        SmallAlgebra alg = loadAlgebra(algebraPath);
        boolean isModular = Malcev.isCongruenceModularIdempotent(alg, null);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "is_congruence_modular_idempotent");
        result.put("algebra", alg.getName());
        result.put("is_modular", isModular);
        
        handleSuccess(result);
    }
    
    /**
     * Test if an idempotent algebra is congruence distributive.
     */
    private void handleIsCongruenceDistIdempotent(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        SmallAlgebra alg = loadAlgebra(algebraPath);
        boolean isDist = Malcev.isCongruenceDistIdempotent(alg, null);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "is_congruence_dist_idempotent");
        result.put("algebra", alg.getName());
        result.put("is_distributive", isDist);
        
        handleSuccess(result);
    }
    
    /**
     * Find a witness for SD-meet failure in an idempotent algebra.
     */
    private void handleSdMeetIdempotent(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        SmallAlgebra alg = loadAlgebra(algebraPath);
        org.uacalc.util.IntArray witness = Malcev.sdMeetIdempotent(alg, null);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "sd_meet_idempotent");
        result.put("algebra", alg.getName());
        
        if (witness != null) {
            result.put("witness_found", true);
            result.put("witness", witness.toArray());
        } else {
            result.put("witness_found", false);
        }
        
        handleSuccess(result);
    }
    
    /**
     * Load an algebra from a file.
     */
    private SmallAlgebra loadAlgebra(String path) throws Exception {
        AlgebraReader reader = new AlgebraReader(path);
        return reader.readAlgebraFile();
    }
    
    /**
     * Show usage information for the Malcev wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "test - Test wrapper functionality",
            "malcev_term --algebra <path> - Find a Malcev term",
            "majority_term --algebra <path> - Find a majority term",
            "minority_term --algebra <path> - Find a minority term",
            "pixley_term --algebra <path> - Find a Pixley term",
            "nu_term --algebra <path> --arity <n> - Find a near unanimity term",
            "weak_majority_term --algebra <path> - Find a weak majority term",
            "semilattice_term --algebra <path> - Find a semilattice term",
            "difference_term --algebra <path> - Find a difference term",
            "jonsson_terms --algebra <path> - Find Jonsson terms",
            "is_congruence_modular --algebra <path> - Test if variety is congruence modular",
            "is_congruence_modular_idempotent --algebra <path> - Test if idempotent algebra is congruence modular",
            "is_congruence_dist_idempotent --algebra <path> - Test if idempotent algebra is congruence distributive",
            "sd_meet_idempotent --algebra <path> - Find SD-meet failure witness for idempotent algebra"
        };
        
        showUsage("Malcev", 
                 "CLI wrapper for org.uacalc.alg.Malcev operations", 
                 examples);
    }
}

