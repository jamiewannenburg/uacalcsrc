/* PartitionWrapper.java - CLI wrapper for org.uacalc.alg.conlat.Partition
 * 
 * This wrapper exposes all public methods of the Partition interface through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg.conlat;

import java.util.*;
import org.uacalc.alg.conlat.*;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Partition interface that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class PartitionWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Partition CLI wrapper.
     */
    public static void main(String[] args) {
        PartitionWrapper wrapper = new PartitionWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Partition wrapper failed", e);
        }
    }
    
    /**
     * Run the Partition CLI wrapper with the given arguments.
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
                handleTest();
                break;
                
            case "zero":
                handleZero(options);
                break;
                
            case "one":
                handleOne(options);
                break;
                
            case "from_array":
                handleFromArray(options);
                break;
                
            case "from_string":
                handleFromString(options);
                break;
                
            case "universe_size":
                handleUniverseSize(options);
                break;
                
            case "number_of_blocks":
                handleNumberOfBlocks(options);
                break;
                
            case "is_related":
                handleIsRelated(options);
                break;
                
            case "representative":
                handleRepresentative(options);
                break;
                
            case "is_representative":
                handleIsRepresentative(options);
                break;
                
            case "representatives":
                handleRepresentatives(options);
                break;
                
            case "block_index":
                handleBlockIndex(options);
                break;
                
            case "get_blocks":
                handleGetBlocks(options);
                break;
                
            case "join_blocks":
                handleJoinBlocks(options);
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
                
            case "normalize":
                handleNormalize(options);
                break;
                
            case "is_zero":
                handleIsZero(options);
                break;
                
            case "is_uniform":
                handleIsUniform(options);
                break;
                
            case "is_initial_lex_representative":
                handleIsInitialLexRepresentative(options);
                break;
                
            case "to_array":
                handleToArray(options);
                break;
                
            case "rank":
                handleRank(options);
                break;
                
            case "to_string":
                handleToString(options);
                break;
                
            case "to_string_with_type":
                handleToStringWithType(options);
                break;
                
            case "to_string_with_max_len":
                handleToStringWithMaxLen(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle test command - run basic functionality tests.
     */
    private void handleTest() throws Exception {
        handleSuccess("Running basic Partition tests...");
        
        // Test zero partition
        BasicPartition zero = BasicPartition.zero(3);
        handleSuccess("Zero partition created: " + zero.toString());
        
        // Test one partition
        BasicPartition one = BasicPartition.one(3);
        handleSuccess("One partition created: " + one.toString());
        
        // Test from array
        int[] array = {-2, 0, -1, -1};
        BasicPartition fromArray = new BasicPartition(array);
        handleSuccess("From array created: " + fromArray.toString());
        
        // Test from string
        BasicPartition fromString = new BasicPartition("|0 1|2 3|");
        handleSuccess("From string created: " + fromString.toString());
        
        // Test basic operations
        handleSuccess("Zero universe size: " + zero.universeSize());
        handleSuccess("Zero number of blocks: " + zero.numberOfBlocks());
        handleSuccess("One universe size: " + one.universeSize());
        handleSuccess("One number of blocks: " + one.numberOfBlocks());
        
        // Test is_related
        handleSuccess("Zero is_related(0,1): " + zero.isRelated(0, 1));
        handleSuccess("One is_related(0,1): " + one.isRelated(0, 1));
        
        // Test representatives
        handleSuccess("Zero representatives: " + Arrays.toString(zero.representatives()));
        handleSuccess("One representatives: " + Arrays.toString(one.representatives()));
        
        // Test join and meet
        Partition join = zero.join(one);
        handleSuccess("Zero join One: " + join.toString());
        
        Partition meet = zero.meet(one);
        handleSuccess("Zero meet One: " + meet.toString());
        
        // Test leq
        handleSuccess("Zero leq One: " + zero.leq(one));
        handleSuccess("One leq Zero: " + one.leq(zero));
        
        handleSuccess("All tests completed successfully");
    }
    
    /**
     * Handle zero command - create zero partition.
     */
    private void handleZero(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 3);
        BasicPartition zero = BasicPartition.zero(size);
        handleSuccess(zero.toString());
    }
    
    /**
     * Handle one command - create one partition.
     */
    private void handleOne(Map<String, String> options) throws Exception {
        int size = getIntArg(options, "size", 3);
        BasicPartition one = BasicPartition.one(size);
        handleSuccess(one.toString());
    }
    
    /**
     * Handle from_array command - create partition from array.
     */
    private void handleFromArray(Map<String, String> options) throws Exception {
        String arrayStr = getRequiredArg(options, "array");
        int[] array = parseIntArray(arrayStr);
        BasicPartition partition = new BasicPartition(array);
        handleSuccess(partition.toString());
    }
    
    /**
     * Handle from_string command - create partition from string.
     */
    private void handleFromString(Map<String, String> options) throws Exception {
        String str = getRequiredArg(options, "str");
        String lengthStr = getOptionalArg(options, "length", null);
        Integer length = lengthStr != null ? Integer.parseInt(lengthStr) : null;
        BasicPartition partition;
        if (length != null) {
            partition = new BasicPartition(str, length);
        } else {
            partition = new BasicPartition(str);
        }
        handleSuccess(partition.toString());
    }
    
    /**
     * Handle universe_size command - get universe size.
     */
    private void handleUniverseSize(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        handleSuccess(String.valueOf(partition.universeSize()));
    }
    
    /**
     * Handle number_of_blocks command - get number of blocks.
     */
    private void handleNumberOfBlocks(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        handleSuccess(String.valueOf(partition.numberOfBlocks()));
    }
    
    /**
     * Handle is_related command - check if elements are related.
     */
    private void handleIsRelated(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        int i = getIntArg(options, "i", 0);
        int j = getIntArg(options, "j", 1);
        handleSuccess(String.valueOf(partition.isRelated(i, j)));
    }
    
    /**
     * Handle representative command - get representative of element.
     */
    private void handleRepresentative(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        int i = getIntArg(options, "i", 0);
        handleSuccess(String.valueOf(partition.representative(i)));
    }
    
    /**
     * Handle is_representative command - check if element is representative.
     */
    private void handleIsRepresentative(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        int i = getIntArg(options, "i", 0);
        handleSuccess(String.valueOf(partition.isRepresentative(i)));
    }
    
    /**
     * Handle representatives command - get all representatives.
     */
    private void handleRepresentatives(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        int[] reps = partition.representatives();
        handleSuccess(Arrays.toString(reps));
    }
    
    /**
     * Handle block_index command - get block index of element.
     */
    private void handleBlockIndex(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        int i = getIntArg(options, "i", 0);
        handleSuccess(String.valueOf(partition.blockIndex(i)));
    }
    
    /**
     * Handle get_blocks command - get blocks as array of arrays.
     */
    private void handleGetBlocks(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        int[][] blocks = partition.getBlocks();
        handleSuccess(Arrays.deepToString(blocks));
    }
    
    /**
     * Handle join_blocks command - join two blocks.
     */
    private void handleJoinBlocks(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        int r = getIntArg(options, "r", 0);
        int s = getIntArg(options, "s", 1);
        partition.joinBlocks(r, s);
        handleSuccess(partition.toString());
    }
    
    /**
     * Handle join command - join two partitions.
     */
    private void handleJoin(Map<String, String> options) throws Exception {
        BasicPartition partition1 = createPartitionFromOptions(options, "partition1");
        BasicPartition partition2 = createPartitionFromOptions(options, "partition2");
        Partition join = partition1.join(partition2);
        handleSuccess(join.toString());
    }
    
    /**
     * Handle meet command - meet two partitions.
     */
    private void handleMeet(Map<String, String> options) throws Exception {
        BasicPartition partition1 = createPartitionFromOptions(options, "partition1");
        BasicPartition partition2 = createPartitionFromOptions(options, "partition2");
        Partition meet = partition1.meet(partition2);
        handleSuccess(meet.toString());
    }
    
    /**
     * Handle leq command - check if partition is less than or equal to another.
     */
    private void handleLeq(Map<String, String> options) throws Exception {
        BasicPartition partition1 = createPartitionFromOptions(options, "partition1");
        BasicPartition partition2 = createPartitionFromOptions(options, "partition2");
        handleSuccess(String.valueOf(partition1.leq(partition2)));
    }
    
    /**
     * Handle normalize command - normalize partition.
     */
    private void handleNormalize(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        partition.normalize();
        handleSuccess(partition.toString());
    }
    
    /**
     * Handle is_zero command - check if partition is zero.
     */
    private void handleIsZero(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        handleSuccess(String.valueOf(partition.isZero()));
    }
    
    /**
     * Handle is_uniform command - check if partition is uniform.
     */
    private void handleIsUniform(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        handleSuccess(String.valueOf(partition.isUniform()));
    }
    
    /**
     * Handle is_initial_lex_representative command - check if partition is in initial lex form.
     */
    private void handleIsInitialLexRepresentative(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        handleSuccess(String.valueOf(partition.isInitialLexRepresentative()));
    }
    
    /**
     * Handle to_array command - get array representation.
     */
    private void handleToArray(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        int[] array = partition.toArray();
        handleSuccess(Arrays.toString(array));
    }
    
    /**
     * Handle rank command - get rank of partition.
     */
    private void handleRank(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        handleSuccess(String.valueOf(partition.rank()));
    }
    
    /**
     * Handle to_string command - get string representation.
     */
    private void handleToString(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        handleSuccess(partition.toString());
    }
    
    /**
     * Handle to_string_with_type command - get string representation with type.
     */
    private void handleToStringWithType(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        String typeStr = getRequiredArg(options, "type");
        Partition.PrintType type = parsePrintType(typeStr);
        handleSuccess(partition.toString(type));
    }
    
    /**
     * Handle to_string_with_max_len command - get string representation with max length.
     */
    private void handleToStringWithMaxLen(Map<String, String> options) throws Exception {
        BasicPartition partition = createPartitionFromOptions(options);
        int maxLen = getIntArg(options, "max_len", 100);
        handleSuccess(partition.toString(maxLen));
    }
    
    /**
     * Create a BasicPartition from command line options.
     */
    private BasicPartition createPartitionFromOptions(Map<String, String> options) throws Exception {
        return createPartitionFromOptions(options, "partition");
    }
    
    /**
     * Create a BasicPartition from command line options with specified key.
     */
    private BasicPartition createPartitionFromOptions(Map<String, String> options, String key) throws Exception {
        String arrayStr = getOptionalArg(options, key + "_array", null);
        if (arrayStr != null) {
            int[] array = parseIntArray(arrayStr);
            return new BasicPartition(array);
        }
        
        String str = getOptionalArg(options, key + "_str", null);
        if (str != null) {
            String lengthStr = getOptionalArg(options, key + "_length", null);
            Integer length = lengthStr != null ? Integer.parseInt(lengthStr) : null;
            if (length != null) {
                return new BasicPartition(str, length);
            } else {
                return new BasicPartition(str);
            }
        }
        
        // Default to zero partition of size 3
        int size = getIntArg(options, key + "_size", 3);
        return BasicPartition.zero(size);
    }
    
    /**
     * Parse an integer array from string representation.
     */
    private int[] parseIntArray(String arrayStr) throws Exception {
        arrayStr = arrayStr.trim();
        if (arrayStr.startsWith("[") && arrayStr.endsWith("]")) {
            arrayStr = arrayStr.substring(1, arrayStr.length() - 1);
        }
        
        String[] parts = arrayStr.split(",");
        int[] array = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            array[i] = Integer.parseInt(parts[i].trim());
        }
        return array;
    }
    
    /**
     * Parse a PrintType from string.
     */
    private Partition.PrintType parsePrintType(String typeStr) throws Exception {
        switch (typeStr.toLowerCase()) {
            case "internal":
                return Partition.PrintType.INTERNAL;
            case "ewk":
                return Partition.PrintType.EWK;
            case "block":
                return Partition.PrintType.BLOCK;
            case "human":
                return Partition.PrintType.HUMAN;
            case "sq_brace_block":
                return Partition.PrintType.SQ_BRACE_BLOCK;
            default:
                throw new IllegalArgumentException("Invalid print type: " + typeStr);
        }
    }
    
    /**
     * Show usage information for the Partition wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "test",
            "zero --size 4",
            "one --size 3",
            "from_array --array \"[-2,0,-1,-1]\"",
            "from_string --str \"|0 1|2 3|\"",
            "universe_size --partition_array \"[-2,0,-1,-1]\"",
            "number_of_blocks --partition_array \"[-2,0,-1,-1]\"",
            "is_related --partition_array \"[-2,0,-1,-1]\" --i 0 --j 1",
            "representative --partition_array \"[-2,0,-1,-1]\" --i 2",
            "is_representative --partition_array \"[-2,0,-1,-1]\" --i 0",
            "representatives --partition_array \"[-2,0,-1,-1]\"",
            "block_index --partition_array \"[-2,0,-1,-1]\" --i 1",
            "get_blocks --partition_array \"[-2,0,-1,-1]\"",
            "join_blocks --partition_array \"[-1,-1,-1,-1]\" --r 0 --s 1",
            "join --partition1_array \"[-2,0,-1,-1]\" --partition2_array \"[-1,-1,-2,2]\"",
            "meet --partition1_array \"[-2,0,-1,-1]\" --partition2_array \"[-1,-1,-2,2]\"",
            "leq --partition1_array \"[-2,0,-1,-1]\" --partition2_array \"[-4,0,0,0]\"",
            "normalize --partition_array \"[0,0,-1,-1]\"",
            "is_zero --partition_array \"[-1,-1,-1,-1]\"",
            "is_uniform --partition_array \"[-2,0,-2,2]\"",
            "is_initial_lex_representative --partition_array \"[-2,0,-1,-1]\"",
            "to_array --partition_array \"[-2,0,-1,-1]\"",
            "rank --partition_array \"[-2,0,-1,-1]\"",
            "to_string --partition_array \"[-2,0,-1,-1]\"",
            "to_string_with_type --partition_array \"[-2,0,-1,-1]\" --type block",
            "to_string_with_max_len --partition_array \"[-2,0,-1,-1]\" --max_len 50"
        };
        
        showUsage("Partition", 
                 "CLI wrapper for org.uacalc.alg.conlat.Partition operations", 
                 examples);
    }
}
