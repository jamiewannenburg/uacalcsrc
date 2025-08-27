import org.uacalc.alg.*;
import org.uacalc.alg.conlat.*;
import org.uacalc.io.*;
import org.uacalc.terms.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import java.util.*;
import java.io.*;

/**
 * Java wrapper for UACalc functionality to enable comparison with Rust implementation.
 * Outputs results in JSON format for easy parsing by comparison scripts.
 */
public class JavaWrapper {
    private static final ObjectMapper mapper = new ObjectMapper();
    
    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Usage: JavaWrapper <operation> <ua_file> [args...]");
            System.exit(1);
        }
        
        String operation = args[0];
        String uaFile = args[1];
        
        try {
            switch (operation) {
                case "properties":
                    outputProperties(uaFile);
                    break;
                case "cg":
                    if (args.length < 4) {
                        System.err.println("Usage: JavaWrapper cg <ua_file> <a> <b>");
                        System.exit(1);
                    }
                    int a = Integer.parseInt(args[2]);
                    int b = Integer.parseInt(args[3]);
                    outputCg(uaFile, a, b);
                    break;
                case "lattice":
                    outputLattice(uaFile);
                    break;
                case "term":
                    if (args.length < 4) {
                        System.err.println("Usage: JavaWrapper term <ua_file> <term_string>");
                        System.exit(1);
                    }
                    String termString = args[2];
                    outputTermEvaluation(uaFile, termString);
                    break;
                default:
                    System.err.println("Unknown operation: " + operation);
                    System.exit(1);
            }
        } catch (Exception e) {
            ObjectNode error = mapper.createObjectNode();
            error.put("error", e.getMessage());
            error.put("type", e.getClass().getSimpleName());
            System.out.println(error.toString());
            System.exit(1);
        }
    }
    
    private static void outputProperties(String uaFile) throws Exception {
        long startTime = System.currentTimeMillis();
        long startMemory = getMemoryUsage();
        
        // Load algebra
        Algebra algebra = AlgebraIO.readAlgebra(uaFile);
        
        long endTime = System.currentTimeMillis();
        long endMemory = getMemoryUsage();
        
        ObjectNode result = mapper.createObjectNode();
        result.put("name", algebra.getName());
        result.put("cardinality", algebra.cardinality());
        result.put("operation_count", algebra.getOperations().size());
        result.put("java_time_ms", endTime - startTime);
        result.put("java_memory_mb", (endMemory - startMemory) / 1024.0 / 1024.0);
        
        ArrayNode symbols = result.putArray("operation_symbols");
        ArrayNode arities = result.putArray("operation_arities");
        
        for (Operation op : algebra.getOperations()) {
            symbols.add(op.getSymbol());
            arities.add(op.getArity());
        }
        
        System.out.println(result.toString());
    }
    
    private static void outputCg(String uaFile, int a, int b) throws Exception {
        long startTime = System.currentTimeMillis();
        long startMemory = getMemoryUsage();
        
        // Load algebra
        Algebra algebra = AlgebraIO.readAlgebra(uaFile);
        
        // Compute congruence lattice
        CongruenceLattice conLat = new CongruenceLattice(algebra);
        
        // Compute Cg(a,b)
        Partition cg = conLat.Cg(a, b);
        
        long endTime = System.currentTimeMillis();
        long endMemory = getMemoryUsage();
        
        ObjectNode result = mapper.createObjectNode();
        result.put("java_time_ms", endTime - startTime);
        result.put("java_memory_mb", (endMemory - startMemory) / 1024.0 / 1024.0);
        
        // Convert partition to list of blocks
        ArrayNode partition = result.putArray("partition");
        for (int i = 0; i < cg.getNumBlocks(); i++) {
            ArrayNode block = partition.addArray();
            for (int element : cg.getBlock(i)) {
                block.add(element);
            }
        }
        
        System.out.println(result.toString());
    }
    
    private static void outputLattice(String uaFile) throws Exception {
        long startTime = System.currentTimeMillis();
        long startMemory = getMemoryUsage();
        
        // Load algebra
        Algebra algebra = AlgebraIO.readAlgebra(uaFile);
        
        // Compute congruence lattice
        CongruenceLattice conLat = new CongruenceLattice(algebra);
        
        long endTime = System.currentTimeMillis();
        long endMemory = getMemoryUsage();
        
        ObjectNode result = mapper.createObjectNode();
        result.put("size", conLat.size());
        result.put("join_irreducibles", conLat.getJoinIrreducibles().size());
        result.put("height", conLat.height());
        result.put("width", conLat.width());
        result.put("java_time_ms", endTime - startTime);
        result.put("java_memory_mb", (endMemory - startMemory) / 1024.0 / 1024.0);
        
        System.out.println(result.toString());
    }
    
    private static void outputTermEvaluation(String uaFile, String termString) throws Exception {
        long startTime = System.currentTimeMillis();
        long startMemory = getMemoryUsage();
        
        // Load algebra
        Algebra algebra = AlgebraIO.readAlgebra(uaFile);
        
        // Parse and evaluate term
        TermParser parser = new TermParser(algebra);
        Term term = parser.parse(termString);
        
        // Create empty variable assignment
        Map<String, Integer> assignment = new HashMap<>();
        
        // Evaluate term
        int result = term.evaluate(algebra, assignment);
        
        long endTime = System.currentTimeMillis();
        long endMemory = getMemoryUsage();
        
        ObjectNode output = mapper.createObjectNode();
        output.put("result", result);
        output.put("java_time_ms", endTime - startTime);
        output.put("java_memory_mb", (endMemory - startMemory) / 1024.0 / 1024.0);
        
        System.out.println(output.toString());
    }
    
    private static long getMemoryUsage() {
        Runtime runtime = Runtime.getRuntime();
        return runtime.totalMemory() - runtime.freeMemory();
    }
}
