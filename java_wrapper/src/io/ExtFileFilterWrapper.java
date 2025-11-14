/* ExtFileFilterWrapper.java - CLI wrapper for org.uacalc.io.ExtFileFilter
 * 
 * This wrapper exposes all public methods of the ExtFileFilter class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.io;

import java.util.*;
import org.uacalc.io.ExtFileFilter;
import java_wrapper.src.WrapperBase;
import java.io.File;

/**
 * CLI wrapper for the ExtFileFilter class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class ExtFileFilterWrapper extends WrapperBase {
    
    /**
     * Main entry point for the ExtFileFilter CLI wrapper.
     */
    public static void main(String[] args) {
        ExtFileFilterWrapper wrapper = new ExtFileFilterWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("ExtFileFilter wrapper failed", e);
        }
    }
    
    /**
     * Run the ExtFileFilter CLI wrapper with the given arguments.
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
                
            case "new_single":
                handleNewSingle(options);
                break;
                
            case "accept":
                handleAccept(options);
                break;
                
            case "get_description":
                handleGetDescription(options);
                break;
                
            case "get_extensions":
                handleGetExtensions(options);
                break;
                
            case "split_off_extension":
                handleSplitOffExtension(options);
                break;
                
            case "get_extension":
                handleGetExtension(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the 'new' command - create ExtFileFilter with description and list of extensions
     */
    private void handleNew(Map<String, String> options) throws Exception {
        String description = getRequiredArg(options, "description");
        String extsStr = getRequiredArg(options, "exts");
        
        // Parse extensions from comma-separated string
        List<String> exts = Arrays.asList(extsStr.split(","));
        
        ExtFileFilter filter = new ExtFileFilter(description, exts);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "new");
        result.put("description", description);
        result.put("exts", exts);
        result.put("status", "ExtFileFilter created successfully");
        handleSuccess(result);
    }
    
    /**
     * Handle the 'new_single' command - create ExtFileFilter with description and single extension
     */
    private void handleNewSingle(Map<String, String> options) throws Exception {
        String description = getRequiredArg(options, "description");
        String ext = getRequiredArg(options, "ext");
        
        ExtFileFilter filter = new ExtFileFilter(description, ext);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "new_single");
        result.put("description", description);
        result.put("ext", ext);
        result.put("status", "ExtFileFilter created successfully");
        handleSuccess(result);
    }
    
    /**
     * Handle the 'accept' command - check if file should be accepted by filter
     */
    private void handleAccept(Map<String, String> options) throws Exception {
        String description = getRequiredArg(options, "description");
        String extsStr = getRequiredArg(options, "exts");
        String path = getRequiredArg(options, "path");
        
        // Parse extensions from comma-separated string
        List<String> exts = Arrays.asList(extsStr.split(","));
        
        ExtFileFilter filter = new ExtFileFilter(description, exts);
        File file = new File(path);
        boolean accepted = filter.accept(file);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "accept");
        result.put("description", description);
        result.put("exts", exts);
        result.put("path", path);
        result.put("status", accepted);
        handleSuccess(result);
    }
    
    /**
     * Handle the 'get_description' command - get filter description
     */
    private void handleGetDescription(Map<String, String> options) throws Exception {
        String description = getRequiredArg(options, "description");
        String extsStr = getRequiredArg(options, "exts");
        
        // Parse extensions from comma-separated string
        List<String> exts = Arrays.asList(extsStr.split(","));
        
        ExtFileFilter filter = new ExtFileFilter(description, exts);
        String result = filter.getDescription();
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("command", "get_description");
        resultMap.put("description", description);
        resultMap.put("exts", exts);
        resultMap.put("status", result);
        handleSuccess(resultMap);
    }
    
    /**
     * Handle the 'get_extensions' command - get filter extensions
     */
    private void handleGetExtensions(Map<String, String> options) throws Exception {
        String description = getRequiredArg(options, "description");
        String extsStr = getRequiredArg(options, "exts");
        
        // Parse extensions from comma-separated string
        List<String> exts = Arrays.asList(extsStr.split(","));
        
        ExtFileFilter filter = new ExtFileFilter(description, exts);
        // Since exts field is not accessible, we return the original extensions
        List<String> result = new ArrayList<>(exts);
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("command", "get_extensions");
        resultMap.put("description", description);
        resultMap.put("exts", exts);
        resultMap.put("status", result);
        handleSuccess(resultMap);
    }
    
    /**
     * Handle the 'split_off_extension' command - split filename into name and extension
     */
    private void handleSplitOffExtension(Map<String, String> options) throws Exception {
        String path = getRequiredArg(options, "path");
        
        File file = new File(path);
        String[] result = ExtFileFilter.splitOffExtension(file);
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("command", "split_off_extension");
        resultMap.put("path", path);
        Map<String, String> splitResult = new HashMap<>();
        splitResult.put("name", result[0]);
        splitResult.put("extension", result[1]);
        resultMap.put("status", splitResult);
        handleSuccess(resultMap);
    }
    
    /**
     * Handle the 'get_extension' command - get file extension
     */
    private void handleGetExtension(Map<String, String> options) throws Exception {
        String path = getRequiredArg(options, "path");
        
        File file = new File(path);
        String result = ExtFileFilter.getExtension(file);
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("command", "get_extension");
        resultMap.put("path", path);
        resultMap.put("status", result);
        handleSuccess(resultMap);
    }
    
    /**
     * Handle the 'test' command - run basic functionality tests
     */
    private void handleTest(Map<String, String> options) throws Exception {
        List<Map<String, Object>> tests = new ArrayList<>();
        
        // Test 1: Create filter with multiple extensions
        try {
            List<String> exts = Arrays.asList("ua", "xml");
            ExtFileFilter filter1 = new ExtFileFilter("UA Files", exts);
            tests.add(Map.of(
                "test", "create_filter_multiple_exts",
                "description", filter1.getDescription(),
                "extensions", new ArrayList<>(exts),
                "success", true
            ));
        } catch (Exception e) {
            tests.add(Map.of(
                "test", "create_filter_multiple_exts",
                "error", e.getMessage(),
                "success", false
            ));
        }
        
        // Test 2: Create filter with single extension
        try {
            ExtFileFilter filter2 = new ExtFileFilter("UA Files", "ua");
            tests.add(Map.of(
                "test", "create_filter_single_ext",
                "description", filter2.getDescription(),
                "extensions", Arrays.asList("ua"),
                "success", true
            ));
        } catch (Exception e) {
            tests.add(Map.of(
                "test", "create_filter_single_ext",
                "error", e.getMessage(),
                "success", false
            ));
        }
        
        // Test 3: Test file acceptance
        try {
            ExtFileFilter filter3 = new ExtFileFilter("UA Files", "ua");
            File testFile = new File("test.ua");
            boolean accepted = filter3.accept(testFile);
            tests.add(Map.of(
                "test", "accept_file",
                "path", "test.ua",
                "accepted", accepted,
                "success", true
            ));
        } catch (Exception e) {
            tests.add(Map.of(
                "test", "accept_file",
                "error", e.getMessage(),
                "success", false
            ));
        }
        
        // Test 4: Test extension splitting
        try {
            File testFile = new File("example.ua");
            String[] split = ExtFileFilter.splitOffExtension(testFile);
            tests.add(Map.of(
                "test", "split_off_extension",
                "path", "example.ua",
                "name", split[0],
                "extension", split[1],
                "success", true
            ));
        } catch (Exception e) {
            tests.add(Map.of(
                "test", "split_off_extension",
                "error", e.getMessage(),
                "success", false
            ));
        }
        
        // Test 5: Test extension extraction
        try {
            File testFile = new File("example.ua");
            String ext = ExtFileFilter.getExtension(testFile);
            tests.add(Map.of(
                "test", "get_extension",
                "path", "example.ua",
                "extension", ext,
                "success", true
            ));
        } catch (Exception e) {
            tests.add(Map.of(
                "test", "get_extension",
                "error", e.getMessage(),
                "success", false
            ));
        }
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("command", "test");
        resultMap.put("tests", tests);
        handleSuccess(resultMap);
    }
    
    /**
     * Show usage information for the ExtFileFilter wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "new --description \"UA Files\" --exts \"ua,xml\"",
            "new_single --description \"UA Files\" --ext \"ua\"",
            "accept --description \"UA Files\" --exts \"ua,xml\" --path \"example.ua\"",
            "get_description --description \"UA Files\" --exts \"ua,xml\"",
            "get_extensions --description \"UA Files\" --exts \"ua,xml\"",
            "split_off_extension --path \"example.ua\"",
            "get_extension --path \"example.ua\"",
            "test"
        };
        
        showUsage("ExtFileFilter", 
                 "CLI wrapper for org.uacalc.io.ExtFileFilter operations", 
                 examples);
    }
}
