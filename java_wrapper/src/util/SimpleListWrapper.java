/* SimpleListWrapper.java - CLI wrapper for org.uacalc.util.SimpleList
 * 
 * This wrapper exposes all public methods of the SimpleList class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.util;

import java.util.*;
import org.uacalc.util.SimpleList;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the SimpleList class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class SimpleListWrapper extends WrapperBase {
    
    /**
     * Main entry point for the SimpleList CLI wrapper.
     */
    public static void main(String[] args) {
        SimpleListWrapper wrapper = new SimpleListWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("SimpleList wrapper failed", e);
        }
    }
    
    /**
     * Run the SimpleList CLI wrapper with the given arguments.
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
                
            case "make_list":
                handleMakeList(options);
                break;
                
            case "make_list_single":
                handleMakeListSingle(options);
                break;
                
            case "is_empty":
                handleIsEmpty(options);
                break;
                
            case "size":
                handleSize(options);
                break;
                
            case "first":
                handleFirst(options);
                break;
                
            case "rest":
                handleRest(options);
                break;
                
            case "cons":
                handleCons(options);
                break;
                
            case "copy_list":
                handleCopyList(options);
                break;
                
            case "append":
                handleAppend(options);
                break;
                
            case "reverse":
                handleReverse(options);
                break;
                
            case "reverse_with":
                handleReverseWith(options);
                break;
                
            case "contains":
                handleContains(options);
                break;
                
            case "get":
                handleGet(options);
                break;
                
            case "index_of":
                handleIndexOf(options);
                break;
                
            case "last_index_of":
                handleLastIndexOf(options);
                break;
                
            case "sub_list":
                handleSubList(options);
                break;
                
            case "to_array":
                handleToArray(options);
                break;
                
            case "contains_all":
                handleContainsAll(options);
                break;
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle make_list command - create empty list
     */
    private void handleMakeList(Map<String, String> options) throws Exception {
        SimpleList list = SimpleList.makeList();
        handleSuccess(list.toString());
    }
    
    /**
     * Handle make_list_single command - create list with single element
     */
    private void handleMakeListSingle(Map<String, String> options) throws Exception {
        String obj = getRequiredArg(options, "obj");
        SimpleList list = SimpleList.makeList(obj);
        handleSuccess(list.toString());
    }
    
    /**
     * Handle is_empty command
     */
    private void handleIsEmpty(Map<String, String> options) throws Exception {
        SimpleList list = createListFromArgs(options);
        boolean result = list.isEmpty();
        handleSuccess(String.valueOf(result));
    }
    
    /**
     * Handle size command
     */
    private void handleSize(Map<String, String> options) throws Exception {
        SimpleList list = createListFromArgs(options);
        int result = list.size();
        handleSuccess(String.valueOf(result));
    }
    
    /**
     * Handle first command
     */
    private void handleFirst(Map<String, String> options) throws Exception {
        SimpleList list = createListFromArgs(options);
        Object result = list.first();
        handleSuccess(result != null ? result.toString() : "null");
    }
    
    /**
     * Handle rest command
     */
    private void handleRest(Map<String, String> options) throws Exception {
        SimpleList list = createListFromArgs(options);
        SimpleList result = list.rest();
        handleSuccess(result.toString());
    }
    
    /**
     * Handle cons command
     */
    private void handleCons(Map<String, String> options) throws Exception {
        SimpleList list = createListFromArgs(options);
        String obj = getRequiredArg(options, "obj");
        SimpleList result = list.cons(obj);
        handleSuccess(result.toString());
    }
    
    /**
     * Handle copy_list command
     */
    private void handleCopyList(Map<String, String> options) throws Exception {
        SimpleList list = createListFromArgs(options);
        SimpleList result = list.copyList();
        handleSuccess(result.toString());
    }
    
    /**
     * Handle append command
     */
    private void handleAppend(Map<String, String> options) throws Exception {
        SimpleList list1 = createListFromArgs(options);
        SimpleList list2 = createListFromArgs(options, "list2");
        SimpleList result = list1.append(list2);
        handleSuccess(result.toString());
    }
    
    /**
     * Handle reverse command
     */
    private void handleReverse(Map<String, String> options) throws Exception {
        SimpleList list = createListFromArgs(options);
        SimpleList result = list.reverse();
        handleSuccess(result.toString());
    }
    
    /**
     * Handle reverse_with command
     */
    private void handleReverseWith(Map<String, String> options) throws Exception {
        SimpleList list1 = createListFromArgs(options);
        SimpleList list2 = createListFromArgs(options, "list2");
        SimpleList result = list1.reverse(list2);
        handleSuccess(result.toString());
    }
    
    /**
     * Handle contains command
     */
    private void handleContains(Map<String, String> options) throws Exception {
        SimpleList list = createListFromArgs(options);
        String obj = getRequiredArg(options, "obj");
        boolean result = list.contains(obj);
        handleSuccess(String.valueOf(result));
    }
    
    /**
     * Handle get command
     */
    private void handleGet(Map<String, String> options) throws Exception {
        SimpleList list = createListFromArgs(options);
        int index = getIntArg(options, "index", 0);
        Object result = list.get(index);
        handleSuccess(result != null ? result.toString() : "null");
    }
    
    /**
     * Handle index_of command
     */
    private void handleIndexOf(Map<String, String> options) throws Exception {
        SimpleList list = createListFromArgs(options);
        String obj = getRequiredArg(options, "obj");
        int result = list.indexOf(obj);
        handleSuccess(String.valueOf(result));
    }
    
    /**
     * Handle last_index_of command
     */
    private void handleLastIndexOf(Map<String, String> options) throws Exception {
        SimpleList list = createListFromArgs(options);
        String obj = getRequiredArg(options, "obj");
        int result = list.lastIndexOf(obj);
        handleSuccess(String.valueOf(result));
    }
    
    /**
     * Handle sub_list command
     */
    private void handleSubList(Map<String, String> options) throws Exception {
        SimpleList list = createListFromArgs(options);
        int start = getIntArg(options, "start", 0);
        int end = getIntArg(options, "end", 0);
        List result = list.subList(start, end);
        handleSuccess(result.toString());
    }
    
    /**
     * Handle to_array command
     */
    private void handleToArray(Map<String, String> options) throws Exception {
        SimpleList list = createListFromArgs(options);
        Object[] result = list.toArray();
        handleSuccess(Arrays.toString(result));
    }
    
    /**
     * Handle contains_all command
     */
    private void handleContainsAll(Map<String, String> options) throws Exception {
        SimpleList list1 = createListFromArgs(options);
        SimpleList list2 = createListFromArgs(options, "list2");
        boolean result = list1.containsAll(list2);
        handleSuccess(String.valueOf(result));
    }
    
    /**
     * Handle test command - run basic functionality tests
     */
    private void handleTest(Map<String, String> options) throws Exception {
        // Test basic operations
        SimpleList empty = SimpleList.makeList();
        SimpleList list1 = empty.cons("a").cons("b").cons("c");
        
        // Test size
        if (list1.size() != 3) {
            throw new Exception("Size test failed: expected 3, got " + list1.size());
        }
        
        // Test first
        if (!"c".equals(list1.first())) {
            throw new Exception("First test failed: expected 'c', got " + list1.first());
        }
        
        // Test rest
        SimpleList rest = list1.rest();
        if (rest.size() != 2) {
            throw new Exception("Rest test failed: expected size 2, got " + rest.size());
        }
        
        // Test contains
        if (!list1.contains("b")) {
            throw new Exception("Contains test failed: should contain 'b'");
        }
        
        // Test reverse
        SimpleList reversed = list1.reverse();
        if (!"a".equals(reversed.first())) {
            throw new Exception("Reverse test failed: expected first 'a', got " + reversed.first());
        }
        
        // Test append
        SimpleList list2 = empty.cons("d").cons("e");
        SimpleList appended = list1.append(list2);
        if (appended.size() != 5) {
            throw new Exception("Append test failed: expected size 5, got " + appended.size());
        }
        
        handleSuccess("All tests passed");
    }
    
    /**
     * Create a SimpleList from command line arguments
     */
    private SimpleList createListFromArgs(Map<String, String> options) throws Exception {
        return createListFromArgs(options, "list");
    }
    
    /**
     * Create a SimpleList from command line arguments with custom key
     */
    private SimpleList createListFromArgs(Map<String, String> options, String key) throws Exception {
        String listStr = getOptionalArg(options, key, "");
        if (listStr.isEmpty()) {
            return SimpleList.makeList();
        }
        
        // Parse comma-separated values
        String[] items = listStr.split(",");
        SimpleList result = SimpleList.makeList();
        for (int i = items.length - 1; i >= 0; i--) {
            result = result.cons(items[i].trim());
        }
        return result;
    }
    
    /**
     * Show usage information for the SimpleList wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "make_list",
            "make_list_single --obj \"hello\"",
            "is_empty --list \"a,b,c\"",
            "size --list \"a,b,c\"",
            "first --list \"a,b,c\"",
            "rest --list \"a,b,c\"",
            "cons --list \"a,b\" --obj \"c\"",
            "copy_list --list \"a,b,c\"",
            "append --list \"a,b\" --list2 \"c,d\"",
            "reverse --list \"a,b,c\"",
            "reverse_with --list \"a,b\" --list2 \"c,d\"",
            "contains --list \"a,b,c\" --obj \"b\"",
            "get --list \"a,b,c\" --index 1",
            "index_of --list \"a,b,c\" --obj \"b\"",
            "last_index_of --list \"a,b,b,c\" --obj \"b\"",
            "sub_list --list \"a,b,c,d\" --start 1 --end 3",
            "to_array --list \"a,b,c\"",
            "contains_all --list \"a,b,c\" --list2 \"a,b\"",
            "test"
        };
        
        showUsage("SimpleList", 
                 "CLI wrapper for org.uacalc.util.SimpleList operations", 
                 examples);
    }
}
