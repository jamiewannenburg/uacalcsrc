/* SubalgebraLatticeWrapper.java - CLI wrapper for org.uacalc.alg.sublat.SubalgebraLattice
 * 
 * This wrapper exposes all public methods of the SubalgebraLattice class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg.sublat;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.alg.sublat.*;
import org.uacalc.io.AlgebraIO;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the SubalgebraLattice class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class SubalgebraLatticeWrapper extends WrapperBase {
    
    private SubalgebraLattice subLat;
    private SmallAlgebra algebra;
    
    /**
     * Main entry point for the SubalgebraLattice CLI wrapper.
     */
    public static void main(String[] args) {
        SubalgebraLatticeWrapper wrapper = new SubalgebraLatticeWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("SubalgebraLattice wrapper failed", e);
        }
    }
    
    /**
     * Run the SubalgebraLattice CLI wrapper with the given arguments.
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
                
            case "new":
                handleNew(options);
                break;
                
            case "get_algebra":
                handleGetAlgebra(options);
                break;
                
            case "get_description":
                handleGetDescription(options);
                break;
                
            case "set_description":
                handleSetDescription(options);
                break;
                
            case "is_drawable":
                handleIsDrawable(options);
                break;
                
            case "is_smaller_than":
                handleIsSmallerThan(options);
                break;
                
            case "universe_found":
                handleUniverseFound(options);
                break;
                
            case "sg":
                handleSg(options);
                break;
                
            case "sg_from_gens":
                handleSgFromGens(options);
                break;
                
            case "one_generated_subalgebras":
                handleOneGeneratedSubalgebras(options);
                break;
                
            case "join_irreducibles":
                handleJoinIrreducibles(options);
                break;
                
            case "meet_irreducibles":
                handleMeetIrreducibles(options);
                break;
                
            case "join":
                handleJoin(options);
                break;
                
            case "meet":
                handleMeet(options);
                break;
                
            case "leq":
                handleLeq(options);
                break;
                
            case "universe":
                handleUniverse(options);
                break;
                
            case "cardinality":
                handleCardinality(options);
                break;
                
            case "filter":
                handleFilter(options);
                break;
                
            case "find_minimal_generating_set":
                handleFindMinimalGeneratingSet(options);
                break;
                
            case "zero":
                handleZero(options);
                break;
                
            case "one":
                handleOne(options);
                break;
                
            case "extend_to_homomorphism":
                handleExtendToHomomorphism(options);
                break;
                
            case "no_duplicates":
                handleNoDuplicates(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    // Handler methods
    
    private void handleNew(Map<String, String> options) throws Exception {
        String algebraFile = getRequiredArg(options, "algebra");
        
        try {
            algebra = (SmallAlgebra) AlgebraIO.readAlgebraFile(algebraFile);
            subLat = new SubalgebraLattice(algebra);
            
            Map<String, Object> result = new HashMap<>();
            result.put("command", "new");
            result.put("algebra_file", algebraFile);
            result.put("algebra_name", algebra.getName());
            result.put("algebra_size", algebra.cardinality());
            result.put("status", "created");
            
            handleSuccess(result);
        } catch (Exception e) {
            handleError("Failed to create SubalgebraLattice", e);
        }
    }
    
    private void handleGetAlgebra(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        
        SmallAlgebra alg = subLat.getAlgebra();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_algebra");
        result.put("algebra_name", alg.getName());
        result.put("algebra_size", alg.cardinality());
        result.put("num_operations", alg.operations().size());
        
        handleSuccess(result);
    }
    
    private void handleGetDescription(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        
        String desc = subLat.getDescription();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_description");
        result.put("description", desc);
        
        handleSuccess(result);
    }
    
    private void handleSetDescription(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        String desc = getRequiredArg(options, "description");
        
        subLat.setDescription(desc);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "set_description");
        result.put("description", desc);
        result.put("status", "set");
        
        handleSuccess(result);
    }
    
    private void handleIsDrawable(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        
        boolean drawable = subLat.isDrawable();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "is_drawable");
        result.put("is_drawable", drawable);
        
        handleSuccess(result);
    }
    
    private void handleIsSmallerThan(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        int size = getIntArg(options, "size", 100);
        
        boolean smaller = subLat.isSmallerThan(size);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "is_smaller_than");
        result.put("size", size);
        result.put("is_smaller", smaller);
        
        handleSuccess(result);
    }
    
    private void handleUniverseFound(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        
        boolean found = subLat.universeFound();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "universe_found");
        result.put("universe_found", found);
        
        handleSuccess(result);
    }
    
    private void handleSg(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        String gensStr = getRequiredArg(options, "generators");
        
        int[] gens = parseIntArray(gensStr);
        BasicSet sub = subLat.sg(gens);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "sg");
        result.put("generators", Arrays.toString(gens));
        result.put("subalgebra", basicSetToList(sub));
        result.put("size", sub.universeSize());
        
        handleSuccess(result);
    }
    
    private void handleSgFromGens(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        String gensStr = getRequiredArg(options, "generators");
        
        int[] gens = parseIntArray(gensStr);
        Subalgebra sub = subLat.Sg(gens);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "sg_from_gens");
        result.put("generators", Arrays.toString(gens));
        result.put("subalgebra_name", sub.getName());
        // Get universe as array
        int[] univArray = sub.getSubuniverseArray();
        List<Integer> universeList = new ArrayList<>();
        for (int i = 0; i < univArray.length; i++) {
            universeList.add(univArray[i]);
        }
        result.put("universe", universeList);
        result.put("size", sub.cardinality());
        
        handleSuccess(result);
    }
    
    private void handleOneGeneratedSubalgebras(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        
        List<BasicSet> oneGens = subLat.oneGeneratedSubalgebras();
        
        List<List<Integer>> oneGensList = new ArrayList<>();
        for (BasicSet bs : oneGens) {
            oneGensList.add(basicSetToList(bs));
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "one_generated_subalgebras");
        result.put("count", oneGens.size());
        result.put("one_generated", oneGensList);
        
        handleSuccess(result);
    }
    
    private void handleJoinIrreducibles(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        
        List<BasicSet> jis = subLat.joinIrreducibles();
        
        List<List<Integer>> jisList = new ArrayList<>();
        for (BasicSet bs : jis) {
            jisList.add(basicSetToList(bs));
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "join_irreducibles");
        result.put("count", jis.size());
        result.put("join_irreducibles", jisList);
        
        handleSuccess(result);
    }
    
    private void handleMeetIrreducibles(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        
        List<BasicSet> mis = subLat.meetIrreducibles();
        
        List<List<Integer>> misList = new ArrayList<>();
        for (BasicSet bs : mis) {
            misList.add(basicSetToList(bs));
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "meet_irreducibles");
        result.put("count", mis.size());
        result.put("meet_irreducibles", misList);
        
        handleSuccess(result);
    }
    
    private void handleJoin(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        String aStr = getRequiredArg(options, "a");
        String bStr = getRequiredArg(options, "b");
        
        BasicSet a = createBasicSet(parseIntArray(aStr));
        BasicSet b = createBasicSet(parseIntArray(bStr));
        
        BasicSet joinResult = (BasicSet) subLat.join(a, b);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "join");
        result.put("a", basicSetToList(a));
        result.put("b", basicSetToList(b));
        result.put("join", basicSetToList(joinResult));
        
        handleSuccess(result);
    }
    
    private void handleMeet(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        String aStr = getRequiredArg(options, "a");
        String bStr = getRequiredArg(options, "b");
        
        BasicSet a = createBasicSet(parseIntArray(aStr));
        BasicSet b = createBasicSet(parseIntArray(bStr));
        
        BasicSet meetResult = (BasicSet) subLat.meet(a, b);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "meet");
        result.put("a", basicSetToList(a));
        result.put("b", basicSetToList(b));
        result.put("meet", basicSetToList(meetResult));
        
        handleSuccess(result);
    }
    
    private void handleLeq(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        String aStr = getRequiredArg(options, "a");
        String bStr = getRequiredArg(options, "b");
        
        BasicSet a = createBasicSet(parseIntArray(aStr));
        BasicSet b = createBasicSet(parseIntArray(bStr));
        
        boolean leqResult = subLat.leq(a, b);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "leq");
        result.put("a", basicSetToList(a));
        result.put("b", basicSetToList(b));
        result.put("leq", leqResult);
        
        handleSuccess(result);
    }
    
    private void handleUniverse(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        
        Set<BasicSet> universe = subLat.universe();
        
        List<List<Integer>> universeList = new ArrayList<>();
        for (BasicSet bs : universe) {
            universeList.add(basicSetToList(bs));
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "universe");
        result.put("size", universe.size());
        result.put("universe", universeList);
        
        handleSuccess(result);
    }
    
    private void handleCardinality(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        
        int card = subLat.cardinality();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "cardinality");
        result.put("cardinality", card);
        
        handleSuccess(result);
    }
    
    private void handleFilter(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        String eltStr = getRequiredArg(options, "element");
        
        BasicSet elt = createBasicSet(parseIntArray(eltStr));
        Set<BasicSet> filtered = subLat.filter(elt);
        
        List<List<Integer>> filteredList = new ArrayList<>();
        for (BasicSet bs : filtered) {
            filteredList.add(basicSetToList(bs));
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "filter");
        result.put("element", basicSetToList(elt));
        result.put("filtered", filteredList);
        result.put("count", filtered.size());
        
        handleSuccess(result);
    }
    
    private void handleFindMinimalGeneratingSet(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        
        BasicSet genSet = subLat.findMinimalSizedGeneratingSet();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "find_minimal_generating_set");
        result.put("generating_set", basicSetToList(genSet));
        result.put("size", genSet.universeSize());
        
        handleSuccess(result);
    }
    
    private void handleZero(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        
        BasicSet zero = subLat.zero();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "zero");
        result.put("zero_subalgebra", basicSetToList(zero));
        
        handleSuccess(result);
    }
    
    private void handleOne(Map<String, String> options) throws Exception {
        ensureSubLatInitialized();
        
        BasicSet one = subLat.one();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "one");
        result.put("one_subalgebra", basicSetToList(one));
        
        handleSuccess(result);
    }
    
    private void handleExtendToHomomorphism(Map<String, String> options) throws Exception {
        // Static method test
        String gensAStr = getRequiredArg(options, "gens_a");
        String gensBStr = getRequiredArg(options, "gens_b");
        String algAFile = getRequiredArg(options, "algebra_a");
        String algBFile = getRequiredArg(options, "algebra_b");
        
        SmallAlgebra algA = (SmallAlgebra) AlgebraIO.readAlgebraFile(algAFile);
        SmallAlgebra algB = (SmallAlgebra) AlgebraIO.readAlgebraFile(algBFile);
        
        int[] gensA = parseIntArray(gensAStr);
        int[] gensB = parseIntArray(gensBStr);
        
        Map<Integer, Integer> homo = SubalgebraLattice.extendToHomomorphism(gensA, gensB, algA, algB);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "extend_to_homomorphism");
        result.put("gens_a", Arrays.toString(gensA));
        result.put("gens_b", Arrays.toString(gensB));
        result.put("homomorphism", homo);
        result.put("exists", homo != null);
        
        handleSuccess(result);
    }
    
    private void handleNoDuplicates(Map<String, String> options) throws Exception {
        // Static method test
        String listStr = getRequiredArg(options, "list");
        
        int[] arr = parseIntArray(listStr);
        List<Integer> lst = new ArrayList<>();
        for (int i : arr) {
            lst.add(i);
        }
        Collections.sort(lst);
        
        List<Integer> noDups = SubalgebraLattice.noDuplicates(lst);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "no_duplicates");
        result.put("input", lst);
        result.put("output", noDups);
        
        handleSuccess(result);
    }
    
    // Helper methods
    
    private void ensureSubLatInitialized() throws Exception {
        if (subLat == null) {
            throw new Exception("SubalgebraLattice not initialized. Use 'new' command first.");
        }
    }
    
    private int[] parseIntArray(String str) {
        if (str == null || str.trim().isEmpty()) {
            return new int[0];
        }
        String[] parts = str.split(",");
        int[] result = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            result[i] = Integer.parseInt(parts[i].trim());
        }
        return result;
    }
    
    private BasicSet createBasicSet(int[] arr) {
        return new BasicSet(arr);
    }
    
    private List<Integer> basicSetToList(BasicSet bs) {
        List<Integer> result = new ArrayList<>();
        for (int i = 0; i < bs.universeSize(); i++) {
            result.add(bs.get(i));
        }
        return result;
    }
    
    /**
     * Show usage information for the SubalgebraLattice wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "# Create a SubalgebraLattice from an algebra file",
            "new --algebra resources/algebras/cyclic3.ua",
            "",
            "# Get algebra information",
            "get_algebra",
            "get_description",
            "",
            "# Generate subalgebras",
            "sg --generators 0,1",
            "sg_from_gens --generators 1,2",
            "",
            "# Compute lattice structure",
            "one_generated_subalgebras",
            "join_irreducibles",
            "meet_irreducibles",
            "universe",
            "",
            "# Lattice operations",
            "join --a 0,1 --b 1,2",
            "meet --a 0,1,2 --b 1,2",
            "leq --a 0,1 --b 0,1,2",
            "",
            "# Utility methods",
            "zero",
            "one",
            "cardinality",
            "is_drawable",
            "find_minimal_generating_set",
            "filter --element 0,1",
            "",
            "# Static methods",
            "no_duplicates --list 1,2,2,3,3,3",
            "extend_to_homomorphism --gens_a 0,1 --gens_b 1,2 --algebra_a alg1.ua --algebra_b alg2.ua"
        };
        
        showUsage("SubalgebraLattice", 
                 "CLI wrapper for org.uacalc.alg.sublat.SubalgebraLattice operations", 
                 examples);
    }
}
