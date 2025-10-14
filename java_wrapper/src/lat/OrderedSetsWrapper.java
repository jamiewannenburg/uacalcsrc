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
                
            case "test":
                handleTest(options);
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the maximals command.
     */
    private void handleMaximals(Map<String, String> options) throws Exception {
        String elementsStr = getOptionalArg(options, "elements", "2,3,6,35,175");
        String orderType = getOptionalArg(options, "order", "divisibility");
        
        // Parse elements
        List<Integer> elements = parseIntegerList(elementsStr);
        
        // Create order relation
        Order<Integer> order = createOrder(orderType);
        
        // Compute maximals
        List<Integer> maximals = OrderedSets.maximals(elements, order);
        
        // Create response
        Map<String, Object> response = new HashMap<>();
        response.put("command", "maximals");
        response.put("elements", elements);
        response.put("order", orderType);
        response.put("status", maximals);
        
        handleSuccess("maximals", response);
    }
    
    /**
     * Handle the test command (equivalent to main method).
     */
    private void handleTest(Map<String, String> options) throws Exception {
        List<Integer> lst = new ArrayList<Integer>();
        lst.add(2);
        lst.add(3);
        lst.add(6);
        lst.add(35);
        lst.add(35 * 5);
        
        List<Integer> maxs = OrderedSets.maximals(lst, new Order<Integer>() {
            public boolean leq(Integer a, Integer b) {
                return a % b == 0;
            }
        });
        
        Map<String, Object> response = new HashMap<>();
        response.put("command", "test");
        response.put("elements", lst);
        response.put("order", "divisibility");
        response.put("status", maxs);
        
        handleSuccess("test", response);
    }
    
    /**
     * Parse a comma-separated list of integers.
     */
    private List<Integer> parseIntegerList(String str) throws Exception {
        List<Integer> result = new ArrayList<>();
        if (str.trim().isEmpty()) {
            return result;
        }
        
        String[] parts = str.split(",");
        for (String part : parts) {
            try {
                result.add(Integer.parseInt(part.trim()));
            } catch (NumberFormatException e) {
                throw new Exception("Invalid integer in list: " + part.trim());
            }
        }
        return result;
    }
    
    /**
     * Create an order relation based on the type.
     */
    private Order<Integer> createOrder(String orderType) throws Exception {
        switch (orderType.toLowerCase()) {
            case "divisibility":
                return new Order<Integer>() {
                    public boolean leq(Integer a, Integer b) {
                        return a % b == 0;
                    }
                };
                
            case "natural":
                return new Order<Integer>() {
                    public boolean leq(Integer a, Integer b) {
                        return a <= b;
                    }
                };
                
            default:
                throw new Exception("Unknown order type: " + orderType + ". Supported: divisibility, natural");
        }
    }
    
    /**
     * Show usage information for the OrderedSets wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "java OrderedSetsWrapper maximals --elements \"2,3,6,35,175\" --order divisibility",
            "java OrderedSetsWrapper test",
            "java OrderedSetsWrapper maximals --elements \"1,2,3,4,5\" --order natural"
        };
        
        showUsage("OrderedSetsWrapper", 
                 "CLI wrapper for org.uacalc.lat.OrderedSets operations", 
                 examples);
    }
}