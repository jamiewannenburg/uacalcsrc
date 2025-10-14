/* OrderedSetsWrapper.java - CLI wrapper for org.uacalc.lat.OrderedSets
 * 
 * This wrapper exposes all public methods of the OrderedSets class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.lat;

import java.util.*;
import org.uacalc.lat.OrderedSets;
import org.uacalc.lat.Order;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the OrderedSets class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class OrderedSetsWrapper extends WrapperBase {
    
    /**
     * Main entry point for the OrderedSets CLI wrapper.
     */
    public static void main(String[] args) {
        OrderedSetsWrapper wrapper = new OrderedSetsWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("OrderedSets wrapper failed", e);
        }
    }
    
    /**
     * Run the OrderedSets CLI wrapper with the given arguments.
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
                
            case "maximals":
                handleMaximals(options);
                break;
                
            case "main":
                handleMain(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle maximals command with various order types.
     */
    private void handleMaximals(Map<String, String> options) {
        try {
            String elementsStr = getRequiredArg(options, "elements");
            String orderType = getOptionalArg(options, "order", "divisibility");
            
            // Parse elements based on order type
            List<Integer> elements = new ArrayList<Integer>();
            if (!elementsStr.trim().isEmpty()) {
                String[] elemArray = elementsStr.split(",");
                for (String elem : elemArray) {
                    String trimmed = elem.trim();
                    if (!trimmed.isEmpty()) {
                        elements.add(Integer.parseInt(trimmed));
                    }
                }
            }
            
            List<Integer> result;
            switch (orderType.toLowerCase()) {
                case "divisibility":
                    result = OrderedSets.maximals(elements, new Order<Integer>() {
                        public boolean leq(Integer a, Integer b) {
                            if (a == 0) return true;  // 0 divides everything by convention
                            if (b == 0) return a == 0;
                            return a != 0 && b % a == 0;
                        }
                    });
                    break;
                    
                case "natural":
                    result = OrderedSets.maximals(elements, new Order<Integer>() {
                        public boolean leq(Integer a, Integer b) {
                            return a <= b;
                        }
                    });
                    break;
                    
                default:
                    handleError("Unknown order type: " + orderType, null);
                    return;
            }
            
            Map<String, Object> response = new HashMap<String, Object>();
            response.put("command", "maximals");
            response.put("elements", elements);
            response.put("order", orderType);
            response.put("status", result);
            
            handleSuccess(response);
            
        } catch (Exception e) {
            handleError("maximals command failed", e);
        }
    }
    
    /**
     * Handle main command - runs the test from the main method.
     */
    private void handleMain(Map<String, String> options) {
        try {
            // Replicate the main method behavior
            List<Integer> lst = new ArrayList<Integer>();
            lst.add(2);
            lst.add(3);
            lst.add(6);
            lst.add(35);
            lst.add(35 * 5);
            
            List<Integer> maxs = OrderedSets.maximals(lst, new Order<Integer>() {
                public boolean leq(Integer a, Integer b) {
                    if (a == 0) return true;  // 0 divides everything by convention
                    if (b == 0) return a == 0;
                    return a != 0 && b % a == 0;
                }
            });
            
            Map<String, Object> response = new HashMap<String, Object>();
            response.put("command", "main");
            response.put("input", lst);
            response.put("status", maxs);
            response.put("message", "max's are " + maxs);
            
            handleSuccess(response);
            
        } catch (Exception e) {
            handleError("main command failed", e);
        }
    }
    
    /**
     * Show usage information for the OrderedSets wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "maximals --elements \"2,3,6,35,175\" --order divisibility",
            "maximals --elements \"1,2,3,4,5\" --order natural",
            "main"
        };
        
        showUsage("OrderedSets", 
                 "CLI wrapper for org.uacalc.lat.OrderedSets operations", 
                 examples);
    }
}