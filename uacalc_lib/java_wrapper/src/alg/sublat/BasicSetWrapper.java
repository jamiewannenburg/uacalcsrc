/* BasicSetWrapper.java - CLI wrapper for org.uacalc.alg.sublat.BasicSet */

package java_wrapper.src.alg.sublat;

import java.util.*;
import org.uacalc.alg.sublat.BasicSet;
import java_wrapper.src.WrapperBase;

public class BasicSetWrapper extends WrapperBase {
    
    public static void main(String[] args) {
        BasicSetWrapper wrapper = new BasicSetWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("BasicSet wrapper failed", e);
        }
    }
    
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
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    private void handleTest() {
        try {
            BasicSet set1 = new BasicSet(new int[]{3, 1, 2});
            boolean test1 = set1.universeSize() == 3 && set1.get(0) == 1;
            
            BasicSet set2 = new BasicSet(new int[]{2, 3, 4});
            BasicSet union = set1.union(set2);
            boolean test2 = union.universeSize() == 4;
            
            boolean test3 = set1.contains(2) && !set1.contains(4);
            
            BasicSet subset = new BasicSet(new int[]{1, 2});
            boolean test4 = subset.leq(set1);
            
            Map<String, Object> response = new HashMap<>();
            response.put("command", "test");
            response.put("test1", test1);
            response.put("test2", test2);
            response.put("test3", test3);
            response.put("test4", test4);
            response.put("status", test1 && test2 && test3 && test4);
            
            handleSuccess(response);
        } catch (Exception e) {
            handleError("Test failed", e);
        }
    }
    
    private void showUsage() {
        String[] examples = {
            "test"
        };
        
        showUsage("BasicSet", 
                 "CLI wrapper for org.uacalc.alg.sublat.BasicSet operations", 
                 examples);
    }
}
