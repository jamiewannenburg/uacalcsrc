/* WrapperBase.java - Base class for CLI wrappers
 * 
 * This base class provides common functionality for all CLI wrappers including
 * argument parsing, JSON output formatting, and error handling.
 */

package java_wrapper.src;

import java.util.*;

/**
 * Base class for CLI wrappers that provides common functionality
 * for argument parsing, JSON output, and error handling.
 */
public abstract class WrapperBase {
    
    /**
     * Run the wrapper with the given arguments.
     * This method must be implemented by subclasses.
     */
    public abstract void run(String[] args) throws Exception;
    
    /**
     * Parse command line arguments into a map.
     * Arguments are expected in the format: command --key value --key2 value2
     */
    protected Map<String, String> parseArgs(String[] args) {
        Map<String, String> options = new HashMap<>();
        
        if (args.length > 0) {
            options.put("arg0", args[0]); // The command
        }
        
        for (int i = 1; i < args.length; i++) {
            if (args[i].startsWith("--") && i + 1 < args.length) {
                String key = args[i].substring(2); // Remove "--"
                String value = args[i + 1];
                options.put(key, value);
                i++; // Skip the value in next iteration
            }
        }
        
        return options;
    }
    
    /**
     * Get a required argument value.
     */
    protected String getRequiredArg(Map<String, String> options, String key) throws Exception {
        String value = options.get(key);
        if (value == null) {
            throw new Exception("Required argument --" + key + " not provided");
        }
        return value;
    }
    
    /**
     * Get an optional argument value with default.
     */
    protected String getOptionalArg(Map<String, String> options, String key, String defaultValue) {
        return options.getOrDefault(key, defaultValue);
    }
    
    /**
     * Get an integer argument value.
     */
    protected int getIntArg(Map<String, String> options, String key) throws Exception {
        String value = getRequiredArg(options, key);
        try {
            return Integer.parseInt(value);
        } catch (NumberFormatException e) {
            throw new Exception("Invalid integer value for --" + key + ": " + value);
        }
    }
    
    /**
     * Get a boolean argument value.
     */
    protected boolean getBoolArg(Map<String, String> options, String key, boolean defaultValue) {
        String value = options.get(key);
        if (value == null) return defaultValue;
        return Boolean.parseBoolean(value);
    }
    
    /**
     * Output a success response in JSON format.
     */
    protected void handleSuccess(String command, Object data) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("command", command);
        response.put("data", serializeObject(data));
        
        System.out.println(toJson(response));
    }
    
    /**
     * Handle an error and output in JSON format.
     */
    protected void handleError(String message, Exception e) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("error", message);
        if (e != null) {
            response.put("details", e.getMessage());
        }
        
        System.err.println(toJson(response));
        System.exit(1);
    }
    
    /**
     * Show usage information.
     */
    protected void showUsage(String className, String description, String[] examples) {
        System.out.println("Usage: java " + className + " <command> [options]");
        System.out.println();
        System.out.println("Description: " + description);
        System.out.println();
        System.out.println("Commands:");
        System.out.println("  help    Show this help message");
        System.out.println();
        if (examples.length > 0) {
            System.out.println("Examples:");
            for (String example : examples) {
                System.out.println("  " + example);
            }
        }
    }
    
    /**
     * Convert an object to JSON string (simple implementation).
     */
    private String toJson(Map<String, Object> obj) {
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        boolean first = true;
        for (Map.Entry<String, Object> entry : obj.entrySet()) {
            if (!first) sb.append(", ");
            sb.append("\"").append(entry.getKey()).append("\": ");
            sb.append(serializeObject(entry.getValue()));
            first = false;
        }
        sb.append("}");
        return sb.toString();
    }
    
    /**
     * Serialize an object to JSON string.
     */
    private String serializeObject(Object obj) {
        if (obj == null) {
            return "null";
        } else if (obj instanceof String) {
            return "\"" + obj.toString().replace("\"", "\\\"") + "\"";
        } else if (obj instanceof Number || obj instanceof Boolean) {
            return obj.toString();
        } else if (obj instanceof List) {
            List<?> list = (List<?>) obj;
            StringBuilder sb = new StringBuilder();
            sb.append("[");
            for (int i = 0; i < list.size(); i++) {
                if (i > 0) sb.append(", ");
                sb.append(serializeObject(list.get(i)));
            }
            sb.append("]");
            return sb.toString();
        } else if (obj instanceof Map) {
            @SuppressWarnings("unchecked")
            Map<String, Object> map = (Map<String, Object>) obj;
            StringBuilder sb = new StringBuilder();
            sb.append("{");
            boolean first = true;
            for (Map.Entry<String, Object> entry : map.entrySet()) {
                if (!first) sb.append(", ");
                sb.append("\"").append(entry.getKey()).append("\": ");
                sb.append(serializeObject(entry.getValue()));
                first = false;
            }
            sb.append("}");
            return sb.toString();
        } else {
            return "\"" + obj.toString().replace("\"", "\\\"") + "\"";
        }
    }
}