/* TypeFinderWrapper.java - CLI wrapper for org.uacalc.alg.conlat.TypeFinder
 * 
 * This wrapper exposes all public methods of the TypeFinder class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg.conlat;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.conlat.*;
import org.uacalc.util.*;
import org.uacalc.io.AlgebraIO;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the TypeFinder class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class TypeFinderWrapper extends WrapperBase {
    
    /**
     * Main entry point for the TypeFinder CLI wrapper.
     */
    public static void main(String[] args) {
        TypeFinderWrapper wrapper = new TypeFinderWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("TypeFinder wrapper failed", e);
        }
    }
    
    /**
     * Run the TypeFinder CLI wrapper with the given arguments.
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
                
            case "find_type_set":
                handleFindTypeSet(options);
                break;
                
            case "find_type":
                handleFindType(options);
                break;
                
            case "find_subtrace":
                handleFindSubtrace(options);
                break;
                
            case "is_subtrace":
                handleIsSubtrace(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the test command - basic functionality test.
     */
    private void handleTest(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        SmallAlgebra alg = AlgebraIO.readAlgebraFile(algebraPath);
        TypeFinder tf = new TypeFinder(alg);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test");
        result.put("algebra_path", algebraPath);
        result.put("alg_size", alg.cardinality());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Handle the find_type_set command.
     */
    private void handleFindTypeSet(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        
        SmallAlgebra alg = AlgebraIO.readAlgebraFile(algebraPath);
        TypeFinder tf = new TypeFinder(alg);
        
        HashSet<Integer> typeSet = tf.findTypeSet();
        List<Integer> typeList = new ArrayList<>(typeSet);
        Collections.sort(typeList);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "find_type_set");
        result.put("algebra_path", algebraPath);
        result.put("type_set", typeList);
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Handle the find_type command.
     */
    private void handleFindType(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        int jiIndex = getIntArg(options, "ji_index", 0);
        
        SmallAlgebra alg = AlgebraIO.readAlgebraFile(algebraPath);
        TypeFinder tf = new TypeFinder(alg);
        
        CongruenceLattice con = alg.con();
        List<Partition> jis = con.joinIrreducibles();
        
        if (jiIndex < 0 || jiIndex >= jis.size()) {
            throw new IllegalArgumentException("ji_index out of range: " + jiIndex);
        }
        
        Partition ji = jis.get(jiIndex);
        int type = tf.findType(ji);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "find_type");
        result.put("algebra_path", algebraPath);
        result.put("ji_index", jiIndex);
        result.put("type", type);
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Handle the find_subtrace command.
     */
    private void handleFindSubtrace(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        int jiIndex = getIntArg(options, "ji_index", 0);
        
        SmallAlgebra alg = AlgebraIO.readAlgebraFile(algebraPath);
        TypeFinder tf = new TypeFinder(alg);
        
        CongruenceLattice con = alg.con();
        List<Partition> jis = con.joinIrreducibles();
        
        if (jiIndex < 0 || jiIndex >= jis.size()) {
            throw new IllegalArgumentException("ji_index out of range: " + jiIndex);
        }
        
        Partition ji = jis.get(jiIndex);
        Subtrace subtrace = tf.findSubtrace(ji);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "find_subtrace");
        result.put("algebra_path", algebraPath);
        result.put("ji_index", jiIndex);
        result.put("first", subtrace.first());
        result.put("second", subtrace.second());
        result.put("has_involution", subtrace.hasInvolution());
        result.put("type", subtrace.type());
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Handle the is_subtrace command.
     */
    private void handleIsSubtrace(Map<String, String> options) throws Exception {
        String algebraPath = getRequiredArg(options, "algebra");
        int jiIndex = getIntArg(options, "ji_index", 0);
        int a = getIntArg(options, "a", 0);
        int b = getIntArg(options, "b", 1);
        
        SmallAlgebra alg = AlgebraIO.readAlgebraFile(algebraPath);
        TypeFinder tf = new TypeFinder(alg);
        
        CongruenceLattice con = alg.con();
        List<Partition> jis = con.joinIrreducibles();
        
        if (jiIndex < 0 || jiIndex >= jis.size()) {
            throw new IllegalArgumentException("ji_index out of range: " + jiIndex);
        }
        
        Partition ji = jis.get(jiIndex);
        IntArray pair = new IntArray(new int[] {a, b});
        boolean isSubtrace = tf.isSubtrace(pair, ji);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "is_subtrace");
        result.put("algebra_path", algebraPath);
        result.put("ji_index", jiIndex);
        result.put("a", a);
        result.put("b", b);
        result.put("is_subtrace", isSubtrace);
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the TypeFinder wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "test --algebra path/to/algebra.ua",
            "find_type_set --algebra path/to/algebra.ua",
            "find_type --algebra path/to/algebra.ua --ji_index 0",
            "find_subtrace --algebra path/to/algebra.ua --ji_index 0",
            "is_subtrace --algebra path/to/algebra.ua --ji_index 0 --a 0 --b 1",
        };
        
        showUsage("TypeFinder", 
                 "CLI wrapper for org.uacalc.alg.conlat.TypeFinder operations", 
                 examples);
    }
}
