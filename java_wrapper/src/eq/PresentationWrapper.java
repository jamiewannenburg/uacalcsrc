/* PresentationWrapper.java - CLI wrapper for org.uacalc.eq.Presentation
 * 
 * This wrapper exposes all public methods of the Presentation class through
 * a command-line interface for testing and validation against Rust/Python implementations.
 */

package java_wrapper.src.eq;

import java.util.*;
import org.uacalc.eq.Presentation;
import org.uacalc.terms.*;
import org.uacalc.eq.Equation;
import java_wrapper.src.WrapperBase;

/**
 * CLI wrapper for the Presentation class that provides command-line access
 * to all public methods for testing and validation purposes.
 */
public class PresentationWrapper extends WrapperBase {
    
    /**
     * Main entry point for the Presentation CLI wrapper.
     */
    public static void main(String[] args) {
        PresentationWrapper wrapper = new PresentationWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Presentation wrapper failed", e);
        }
    }
    
    /**
     * Run the Presentation CLI wrapper with the given arguments.
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
                
            case "create":
                handleCreate(options);
                break;
                
            case "get_variables":
                handleGetVariables(options);
                break;
                
            case "get_relations":
                handleGetRelations(options);
                break;
                
            case "test":
                handleTest();
                break;
                
            default:
                handleError("Unknown command: " + command, null);
        }
    }
    
    /**
     * Handle the create command.
     * Usage: create --variables "var1,var2,..." --relations "eq1,eq2,..."
     */
    private void handleCreate(Map<String, String> options) throws Exception {
        String variablesStr = getRequiredArg(options, "variables");
        String relationsStr = getOptionalArg(options, "relations", "");
        
        // Parse variables
        String[] variableNames = variablesStr.split(",");
        List<Variable> variables = new ArrayList<>();
        for (String name : variableNames) {
            variables.add(new VariableImp(name.trim()));
        }
        
        // Parse relations (for now, create empty list since we don't have equation parsing)
        List<Equation> relations = new ArrayList<>();
        if (!relationsStr.isEmpty()) {
            // In a real implementation, we would parse the relations string
            // For now, we'll create empty relations
        }
        
        // Create presentation
        Presentation presentation = new Presentation(variables, relations);
        
        // Store the presentation for later use (in a real implementation, you'd use a proper storage mechanism)
        // For now, we'll just return the variable and relation counts
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "create");
        result.put("variables_count", variables.size());
        result.put("relations_count", relations.size());
        result.put("variables", variables.stream().map(Variable::getName).toArray(String[]::new));
        handleSuccess(result);
    }
    
    /**
     * Handle the get_variables command.
     * Usage: get_variables --variables "var1,var2,..."
     */
    private void handleGetVariables(Map<String, String> options) throws Exception {
        String variablesStr = getRequiredArg(options, "variables");
        
        // Parse variables
        String[] variableNames = variablesStr.split(",");
        List<Variable> variables = new ArrayList<>();
        for (String name : variableNames) {
            variables.add(new VariableImp(name.trim()));
        }
        
        // Create a temporary presentation to test getVariables
        Presentation presentation = new Presentation(variables, new ArrayList<>());
        List<Variable> retrievedVariables = presentation.getVariables();
        
        String[] variableNamesArray = retrievedVariables.stream()
            .map(Variable::getName)
            .toArray(String[]::new);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_variables");
        result.put("variables", variableNamesArray);
        result.put("count", retrievedVariables.size());
        handleSuccess(result);
    }
    
    /**
     * Handle the get_relations command.
     * Usage: get_relations --variables "var1,var2,..." --relations "eq1,eq2,..."
     */
    private void handleGetRelations(Map<String, String> options) throws Exception {
        String variablesStr = getRequiredArg(options, "variables");
        String relationsStr = getOptionalArg(options, "relations", "");
        
        // Parse variables
        String[] variableNames = variablesStr.split(",");
        List<Variable> variables = new ArrayList<>();
        for (String name : variableNames) {
            variables.add(new VariableImp(name.trim()));
        }
        
        // Parse relations (for now, create empty list)
        List<Equation> relations = new ArrayList<>();
        if (!relationsStr.isEmpty()) {
            // In a real implementation, we would parse the relations string
        }
        
        // Create a temporary presentation to test getRelations
        Presentation presentation = new Presentation(variables, relations);
        List<Equation> retrievedRelations = presentation.getRelations();
        
        String[] relationStrings = retrievedRelations.stream()
            .map(Equation::toString)
            .toArray(String[]::new);
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "get_relations");
        result.put("relations", relationStrings);
        result.put("count", retrievedRelations.size());
        handleSuccess(result);
    }
    
    /**
     * Handle the test command - run comprehensive tests.
     */
    private void handleTest() throws Exception {
        // Test 1: Create presentation with variables
        List<Variable> variables = Arrays.asList(
            new VariableImp("x"),
            new VariableImp("y"),
            new VariableImp("z")
        );
        List<Equation> relations = new ArrayList<>();
        
        Presentation presentation = new Presentation(variables, relations);
        
        // Test 2: Get variables
        List<Variable> retrievedVars = presentation.getVariables();
        boolean variablesTest = retrievedVars.size() == 3 && 
            retrievedVars.get(0).getName().equals("x") &&
            retrievedVars.get(1).getName().equals("y") &&
            retrievedVars.get(2).getName().equals("z");
        
        // Test 3: Get relations (should be empty)
        List<Equation> retrievedRels = presentation.getRelations();
        boolean relationsTest = retrievedRels.isEmpty();
        
        // Test 4: String representation
        String strRepr = presentation.toString();
        boolean strTest = strRepr.contains("Presentation") && strRepr.contains("x") && strRepr.contains("y") && strRepr.contains("z");
        
        Map<String, Object> result = new HashMap<>();
        result.put("command", "test");
        result.put("create_presentation", true);
        result.put("get_variables", variablesTest);
        result.put("get_relations", relationsTest);
        result.put("string_representation", strTest);
        result.put("variables_count", retrievedVars.size());
        result.put("relations_count", retrievedRels.size());
        handleSuccess(result);
    }
    
    /**
     * Show usage information for the Presentation wrapper.
     */
    private void showUsage() {
        String[] examples = {
            "create --variables \"x,y,z\" --relations \"\"",
            "get_variables --variables \"x,y,z\"",
            "get_relations --variables \"x,y,z\" --relations \"\"",
            "test"
        };
        
        showUsage("Presentation", 
                 "CLI wrapper for org.uacalc.eq.Presentation operations", 
                 examples);
    }
}