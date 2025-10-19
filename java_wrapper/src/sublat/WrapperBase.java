/* WrapperBase.java - Base class for Java CLI wrappers
 * 
 * This class provides common functionality for all Java CLI wrappers,
 * including standardized JSON output, error handling, and argument parsing.
 */

package sublat;

import java.io.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
// Simple JSON implementation without external dependencies

/**
 * Base class for Java CLI wrappers that provides common functionality
 * for standardized output, error handling, and argument parsing.
 */
public abstract class WrapperBase {
    
    // Simple JSON implementation without external dependencies
    protected final PrintStream out;
    protected final PrintStream err;
    protected final long startTime;
    
    /**
     * Constructor for the base wrapper.
     */
    public WrapperBase() {
        this.out = System.out;
        this.err = System.err;
        this.startTime = System.currentTimeMillis();
    }
    
    /**
     * Main entry point for CLI wrappers.
     * Subclasses should implement this method to handle their specific commands.
     */
    public abstract void run(String[] args) throws Exception;
    
    /**
     * Parse command line arguments and return a map of options.
     * 
     * @param args Command line arguments
     * @return Map of parsed options
     */
    protected Map<String, String> parseArgs(String[] args) {
        Map<String, String> options = new HashMap<>();
        
        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            
            if (arg.startsWith("--")) {
                // Long option
                String key = arg.substring(2);
                if (key.contains("=")) {
                    // Handle --key=value format
                    String[] parts = key.split("=", 2);
                    options.put(parts[0], parts[1]);
                } else if (i + 1 < args.length && !args[i + 1].startsWith("-")) {
                    // Handle --key value format
                    options.put(key, args[++i]);
                } else {
                    options.put(key, "true");
                }
            } else if (arg.startsWith("-")) {
                // Short option
                String key = arg.substring(1);
                if (i + 1 < args.length && !args[i + 1].startsWith("-")) {
                    options.put(key, args[++i]);
                } else {
                    options.put(key, "true");
                }
            } else {
                // Positional argument
                options.put("arg" + i, arg);
            }
        }
        
        return options;
    }
    
    /**
     * Create a standardized JSON response string.
     * 
     * @param success Whether the operation was successful
     * @param data The result data
     * @param error Error message if any
     * @return JSON response string
     */
    protected String createResponse(boolean success, Object data, String error) {
        StringBuilder json = new StringBuilder();
        json.append("{\n");
        json.append("  \"success\": ").append(success).append(",\n");
        json.append("  \"timestamp\": ").append(System.currentTimeMillis()).append(",\n");
        json.append("  \"duration_ms\": ").append(System.currentTimeMillis() - startTime).append(",\n");
        
        if (data != null) {
            json.append("  \"data\": ");
            json.append(serializeObject(data));
            json.append(",\n");
        }
        
        if (error != null) {
            json.append("  \"error\": \"").append(escapeJson(error)).append("\",\n");
        }
        
        // Remove trailing comma
        if (json.charAt(json.length() - 2) == ',') {
            json.setLength(json.length() - 2);
            json.append("\n");
        }
        
        json.append("}");
        return json.toString();
    }
    
    /**
     * Output a JSON response to stdout.
     * 
     * @param response The response string to output
     */
    protected void outputJson(String response) {
        out.println(response);
    }
    
    /**
     * Output a simple text response to stdout.
     * 
     * @param text The text to output
     */
    protected void outputText(String text) {
        out.println(text);
    }
    
    /**
     * Handle an error and output appropriate response.
     * 
     * @param error The error message
     * @param exception The exception that occurred
     */
    protected void handleError(String error, Exception exception) {
        StringBuilder response = new StringBuilder();
        response.append("{\n");
        response.append("  \"success\": false,\n");
        response.append("  \"timestamp\": ").append(System.currentTimeMillis()).append(",\n");
        response.append("  \"duration_ms\": ").append(System.currentTimeMillis() - startTime).append(",\n");
        response.append("  \"error\": \"").append(escapeJson(error)).append("\"");
        
        if (exception != null) {
            response.append(",\n");
            response.append("  \"exception\": \"").append(exception.getClass().getSimpleName()).append("\",\n");
            response.append("  \"exception_message\": \"").append(escapeJson(exception.getMessage())).append("\"");
        }
        
        response.append("\n}");
        outputJson(response.toString());
        System.exit(1);
    }
    
    /**
     * Handle a successful operation and output the result.
     * 
     * @param data The result data
     */
    protected void handleSuccess(Object data) {
        String response = createResponse(true, data, null);
        outputJson(response);
    }
    
    /**
     * Execute an action while temporarily silencing System.out to avoid
     * polluting JSON output with library debug prints.
     */
    protected <T> T withSilencedStdout(java.util.concurrent.Callable<T> action) throws Exception {
        PrintStream originalOut = System.out;
        try {
            System.setOut(new PrintStream(new OutputStream() {
                @Override public void write(int b) { /* discard */ }
                @Override public void write(byte[] b, int off, int len) { /* discard */ }
            }));
            return action.call();
        } finally {
            System.setOut(originalOut);
        }
    }
    
    /**
     * Get a required argument from the options map.
     * 
     * @param options The options map
     * @param key The argument key
     * @return The argument value
     * @throws IllegalArgumentException if the argument is missing
     */
    protected String getRequiredArg(Map<String, String> options, String key) {
        String value = options.get(key);
        if (value == null) {
            throw new IllegalArgumentException("Required argument missing: " + key);
        }
        return value;
    }
    
    /**
     * Get an optional argument from the options map with a default value.
     * 
     * @param options The options map
     * @param key The argument key
     * @param defaultValue The default value
     * @return The argument value or default
     */
    protected String getOptionalArg(Map<String, String> options, String key, String defaultValue) {
        return options.getOrDefault(key, defaultValue);
    }
    
    /**
     * Parse an integer argument.
     * 
     * @param options The options map
     * @param key The argument key
     * @param defaultValue The default value
     * @return The parsed integer
     * @throws NumberFormatException if the value cannot be parsed
     */
    protected int getIntArg(Map<String, String> options, String key, int defaultValue) {
        String value = options.get(key);
        if (value == null) {
            return defaultValue;
        }
        try {
            return Integer.parseInt(value);
        } catch (NumberFormatException e) {
            throw new NumberFormatException("Invalid integer for argument " + key + ": " + value);
        }
    }
    
    /**
     * Parse a boolean argument.
     * 
     * @param options The options map
     * @param key The argument key
     * @param defaultValue The default value
     * @return The parsed boolean
     */
    protected boolean getBoolArg(Map<String, String> options, String key, boolean defaultValue) {
        String value = options.get(key);
        if (value == null) {
            return defaultValue;
        }
        return Boolean.parseBoolean(value);
    }
    
    /**
     * Parse a long argument.
     * 
     * @param options The options map
     * @param key The argument key
     * @param defaultValue The default value
     * @return The parsed long
     * @throws NumberFormatException if the value cannot be parsed
     */
    protected long getLongArg(Map<String, String> options, String key, long defaultValue) {
        String value = options.get(key);
        if (value == null) {
            return defaultValue;
        }
        try {
            return Long.parseLong(value);
        } catch (NumberFormatException e) {
            throw new NumberFormatException("Invalid long for argument " + key + ": " + value);
        }
    }
    
    /**
     * Show usage information for the wrapper.
     * 
     * @param className The name of the wrapper class
     * @param description Description of what the wrapper does
     * @param examples Examples of usage
     */
    protected void showUsage(String className, String description, String[] examples) {
        err.println("Usage: " + className + " <command> [options]");
        err.println();
        err.println("Description: " + description);
        err.println();
        err.println("Commands:");
        err.println("  help     Show this help message");
        err.println();
        err.println("Examples:");
        for (String example : examples) {
            err.println("  " + example);
        }
    }
    
    /**
     * Execute a command with timeout.
     * 
     * @param timeoutSeconds Timeout in seconds
     * @param command The command to execute
     * @return The result of the command
     * @throws TimeoutException if the command times out
     */
    protected <T> T executeWithTimeout(int timeoutSeconds, java.util.concurrent.Callable<T> command) 
            throws Exception {
        java.util.concurrent.ExecutorService executor = 
            java.util.concurrent.Executors.newSingleThreadExecutor();
        
        try {
            java.util.concurrent.Future<T> future = executor.submit(command);
            return future.get(timeoutSeconds, TimeUnit.SECONDS);
        } catch (java.util.concurrent.TimeoutException e) {
            throw new TimeoutException("Operation timed out after " + timeoutSeconds + " seconds");
        } finally {
            executor.shutdown();
        }
    }
    
    /**
     * Custom timeout exception.
     */
    public static class TimeoutException extends Exception {
        public TimeoutException(String message) {
            super(message);
        }
    }
    
    /**
     * Serialize an object to JSON string.
     */
    private String serializeObject(Object obj) {
        if (obj == null) {
            return "null";
        } else if (obj instanceof String) {
            return "\"" + escapeJson((String) obj) + "\"";
        } else if (obj instanceof Number || obj instanceof Boolean) {
            return obj.toString();
        } else if (obj instanceof int[]) {
            int[] arr = (int[]) obj;
            StringBuilder sb = new StringBuilder();
            sb.append("[");
            for (int i = 0; i < arr.length; i++) {
                if (i > 0) sb.append(", ");
                sb.append(arr[i]);
            }
            sb.append("]");
            return sb.toString();
        } else if (obj instanceof Integer[]) {
            Integer[] arr = (Integer[]) obj;
            StringBuilder sb = new StringBuilder();
            sb.append("[");
            for (int i = 0; i < arr.length; i++) {
                if (i > 0) sb.append(", ");
                sb.append(arr[i]);
            }
            sb.append("]");
            return sb.toString();
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
            Map<?, ?> map = (Map<?, ?>) obj;
            StringBuilder sb = new StringBuilder();
            sb.append("{\n");
            boolean first = true;
            for (Map.Entry<?, ?> entry : map.entrySet()) {
                if (!first) sb.append(",\n");
                // Always quote keys for valid JSON, but preserve integer values
                sb.append("    \"").append(escapeJson(entry.getKey().toString())).append("\": ");
                sb.append(serializeObject(entry.getValue()));
                first = false;
            }
            sb.append("\n  }");
            return sb.toString();
        } else {
            return "\"" + escapeJson(obj.toString()) + "\"";
        }
    }
    
    /**
     * Escape special characters for JSON.
     */
    private String escapeJson(String str) {
        if (str == null) return "";
        return str.replace("\\", "\\\\")
                 .replace("\"", "\\\"")
                 .replace("\b", "\\b")
                 .replace("\f", "\\f")
                 .replace("\n", "\\n")
                 .replace("\r", "\\r")
                 .replace("\t", "\\t");
    }
    
    /**
     * Main method template for subclasses.
     * 
     * @param args Command line arguments
     */
    public static void main(String[] args) {
        // This should be implemented by subclasses
        System.err.println("WrapperBase.main() should not be called directly");
        System.exit(1);
    }
}
