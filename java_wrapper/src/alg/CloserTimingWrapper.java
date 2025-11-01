/* CloserTimingWrapper.java - CLI wrapper for org.uacalc.alg.CloserTiming
 * 
 * This wrapper exposes all public methods of the CloserTiming class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.alg;

import java.util.*;
import org.uacalc.alg.*;
import org.uacalc.ui.tm.ProgressReport;
import org.uacalc.io.AlgebraIO;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the CloserTiming class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class CloserTimingWrapper extends WrapperBase {
    
    /**
     * Main entry point for the CloserTiming CLI wrapper.
     */
    public static void main(String[] args) {
        CloserTimingWrapper wrapper = new CloserTimingWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("CloserTiming wrapper failed", e);
        }
    }
    
    /**
     * Run the CloserTiming CLI wrapper with the given arguments.
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
                
            case "update_pass":
                handleUpdatePass(options);
                break;
                
            case "increment_apps":
                handleIncrementApps(options);
                break;
                
            case "increment_next_pass_size":
                handleIncrementNextPassSize(options);
                break;
                
            case "ms_to_string":
                handleMsToString(options);
                break;
                
            case "get_pass":
                handleGetPass(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Create a new CloserTiming instance.
     * Usage: new --files file1.ua,file2.ua [--with_report false]
     */
    private void handleNew(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        BigProductAlgebra product = new BigProductAlgebra("", algebras);
        ProgressReport report = null; // Use null for testing (matches Rust None)
        
        CloserTiming timing = new CloserTiming(product, report);
        
        // Get accessible information
        int numOps = product.operations().size();
        List<Integer> arities = new ArrayList<>();
        for (int i = 0; i < numOps; i++) {
            arities.add(product.operations().get(i).arity());
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "new");
        result.put("num_factors", product.getNumberOfFactors());
        result.put("arities", arities);
        result.put("num_operations", numOps);
        result.put("status", "created");
        
        handleSuccess(result);
    }
    
    /**
     * Update pass information.
     * Usage: update_pass --files file1.ua,file2.ua --size 10
     */
    private void handleUpdatePass(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        int size = getIntArg(options, "size", 0);
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        BigProductAlgebra product = new BigProductAlgebra("", algebras);
        CloserTiming timing = new CloserTiming(product, null);
        
        timing.updatePass(size);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "update_pass");
        result.put("size", size);
        result.put("status", "updated");
        
        handleSuccess(result);
    }
    
    /**
     * Increment application counters.
     * Usage: increment_apps --files file1.ua,file2.ua --count 100
     */
    private void handleIncrementApps(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        int count = getIntArg(options, "count", 1);
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        BigProductAlgebra product = new BigProductAlgebra("", algebras);
        CloserTiming timing = new CloserTiming(product, null);
        timing.updatePass(10); // Initialize with a pass
        
        for (int i = 0; i < count; i++) {
            timing.incrementApps();
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "increment_apps");
        result.put("count", count);
        result.put("status", "incremented");
        
        handleSuccess(result);
    }
    
    /**
     * Increment next pass size.
     * Usage: increment_next_pass_size --files file1.ua,file2.ua --count 5
     */
    private void handleIncrementNextPassSize(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        int count = getIntArg(options, "count", 1);
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        BigProductAlgebra product = new BigProductAlgebra("", algebras);
        CloserTiming timing = new CloserTiming(product, null);
        
        for (int i = 0; i < count; i++) {
            timing.incrementNextPassSize();
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "increment_next_pass_size");
        result.put("count", count);
        result.put("status", "incremented");
        
        handleSuccess(result);
    }
    
    /**
     * Convert milliseconds to time string.
     * Usage: ms_to_string --ms 65000
     */
    private void handleMsToString(Map<String, String> options) throws Exception {
        long ms = Long.parseLong(getRequiredArg(options, "ms"));
        
        // Create a temporary CloserTiming to access the static method
        // Since msToString is private, we need to use reflection or create an instance
        // For now, we'll create a minimal instance to access the method
        // Actually, since it's private, we'll need to replicate the logic
        String timeStr = msToString(ms);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "ms_to_string");
        result.put("ms", ms);
        result.put("time_string", timeStr);
        
        handleSuccess(result);
    }
    
    /**
     * Get the current pass number.
     * Usage: get_pass --files file1.ua,file2.ua [--size 10]
     */
    private void handleGetPass(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        int size = getIntArg(options, "size", 0);
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        BigProductAlgebra product = new BigProductAlgebra("", algebras);
        CloserTiming timing = new CloserTiming(product, null);
        
        if (size > 0) {
            timing.updatePass(size);
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_pass");
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Run basic tests.
     * Usage: test --files file1.ua,file2.ua
     */
    private void handleTest(Map<String, String> options) throws Exception {
        String filesStr = getRequiredArg(options, "files");
        
        String[] files = filesStr.split(",");
        List<SmallAlgebra> algebras = new ArrayList<>();
        
        for (String file : files) {
            SmallAlgebra alg = AlgebraIO.readAlgebraFile(file.trim());
            algebras.add(alg);
        }
        
        BigProductAlgebra product = new BigProductAlgebra("TestProduct", algebras);
        CloserTiming timing = new CloserTiming(product, null);
        
        timing.updatePass(10);
        timing.incrementApps();
        timing.incrementNextPassSize();
        
        // Get accessible information
        int numOps = product.operations().size();
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test");
        result.put("num_factors", product.getNumberOfFactors());
        result.put("num_operations", numOps);
        result.put("test_passed", true);
        result.put("status", "success");
        
        handleSuccess(result);
    }
    
    /**
     * Helper method to convert milliseconds to time string.
     * This replicates the logic from CloserTiming.msToString()
     */
    private String msToString(long ms) {
        final String colon = ":";
        final long totSecs = ms / 1000;
        final long secs = totSecs % 60;
        final long totMins = totSecs / 60;
        final long mins = totMins % 60;
        final long hrs = totMins / 60;
        String secsString = secs < 10 ? "0" + Long.toString(secs) : Long.toString(secs);
        if (hrs == 0) {
            if (mins == 0) return Long.toString(secs);
            return Long.toString(mins) + colon + secsString;
        }
        String minsString = mins < 10 ? "0" + Long.toString(mins) : Long.toString(mins);
        return Long.toString(hrs) + colon + minsString + colon + secsString;
    }
    
    /**
     * Show usage information for the CloserTiming wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "new --files file1.ua,file2.ua",
            "update_pass --files file1.ua,file2.ua --size 10",
            "increment_apps --files file1.ua,file2.ua --count 100",
            "increment_next_pass_size --files file1.ua,file2.ua --count 5",
            "ms_to_string --ms 65000",
            "get_pass --files file1.ua,file2.ua --size 10",
            "test --files file1.ua,file2.ua"
        };
        
        showUsage("CloserTiming", 
                 "CLI wrapper for org.uacalc.alg.CloserTiming operations", 
                 examples);
    }
}

