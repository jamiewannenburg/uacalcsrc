/* EquationsWrapper.java - CLI wrapper for org.uacalc.eq.Equations */

package eq;

import org.uacalc.alg.op.OperationSymbol;
import org.uacalc.eq.Equations;
import org.uacalc.eq.Equation;
import org.uacalc.terms.Term;
import org.uacalc.terms.NonVariableTerm;
import org.uacalc.terms.Variable;
import org.uacalc.terms.VariableImp;

import java.util.List;
import java.util.ArrayList;

/**
 * CLI wrapper for the Equations class to enable testing and comparison
 * with the Rust implementation.
 */
public class EquationsWrapper {
    
    public static void main(String[] args) {
        if (args.length == 0) {
            printUsage();
            return;
        }
        
        String command = args[0];
        
        try {
            switch (command) {
                case "associative-law":
                    handleAssociativeLaw(args);
                    break;
                case "cyclic-law":
                    handleCyclicLaw(args);
                    break;
                case "first-second-symmetric-law":
                    handleFirstSecondSymmetricLaw(args);
                    break;
                case "test":
                    runTests();
                    break;
                default:
                    System.err.println("Unknown command: " + command);
                    printUsage();
                    System.exit(1);
            }
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    private static void printUsage() {
        System.out.println("Usage: java eq.EquationsWrapper <command> [options]");
        System.out.println();
        System.out.println("Commands:");
        System.out.println("  associative-law --op-name <name> --op-arity <arity>");
        System.out.println("    Generate associative law equation f(x,f(y,z)) = f(f(x,y),z)");
        System.out.println();
        System.out.println("  cyclic-law --op-name <name> --op-arity <arity>");
        System.out.println("    Generate cyclic law equation f(x0,x1,...,x{k-1}) = f(x{k-1},x0,...,x{k-2})");
        System.out.println();
        System.out.println("  first-second-symmetric-law --op-name <name> --op-arity <arity>");
        System.out.println("    Generate first-second symmetric law equation f(x0,x1,x2,...,xk) = f(x1,x0,x2,...,xk)");
        System.out.println();
        System.out.println("  test");
        System.out.println("    Run basic functionality tests");
        System.out.println();
        System.out.println("Options:");
        System.out.println("  --op-name <name>    Operation symbol name");
        System.out.println("  --op-arity <arity>  Operation symbol arity (integer)");
    }
    
    private static void handleAssociativeLaw(String[] args) {
        String opName = null;
        int opArity = -1;
        
        // Parse arguments
        for (int i = 1; i < args.length; i++) {
            if (args[i].equals("--op-name") && i + 1 < args.length) {
                opName = args[++i];
            } else if (args[i].equals("--op-arity") && i + 1 < args.length) {
                opArity = Integer.parseInt(args[++i]);
            }
        }
        
        if (opName == null || opArity == -1) {
            System.err.println("Error: --op-name and --op-arity are required");
            System.exit(1);
        }
        
        OperationSymbol op = new OperationSymbol(opName, opArity, false);
        Equation equation = Equations.associativeLaw(op);
        
        System.out.println("Associative Law Equation:");
        System.out.println("Operation: " + opName + "/" + opArity);
        System.out.println("Equation: " + equation);
        System.out.println("Left side: " + equation.leftSide());
        System.out.println("Right side: " + equation.rightSide());
        System.out.println("Variables: " + equation.getVariableList());
    }
    
    private static void handleCyclicLaw(String[] args) {
        String opName = null;
        int opArity = -1;
        
        // Parse arguments
        for (int i = 1; i < args.length; i++) {
            if (args[i].equals("--op-name") && i + 1 < args.length) {
                opName = args[++i];
            } else if (args[i].equals("--op-arity") && i + 1 < args.length) {
                opArity = Integer.parseInt(args[++i]);
            }
        }
        
        if (opName == null || opArity == -1) {
            System.err.println("Error: --op-name and --op-arity are required");
            System.exit(1);
        }
        
        try {
            OperationSymbol op = new OperationSymbol(opName, opArity, false);
            Equation equation = Equations.cyclicLaw(op);
            
            System.out.println("Cyclic Law Equation:");
            System.out.println("Operation: " + opName + "/" + opArity);
            System.out.println("Equation: " + equation);
            System.out.println("Left side: " + equation.leftSide());
            System.out.println("Right side: " + equation.rightSide());
            System.out.println("Variables: " + equation.getVariableList());
        } catch (IllegalArgumentException e) {
            System.err.println("Error: " + e.getMessage());
            System.exit(1);
        }
    }
    
    private static void handleFirstSecondSymmetricLaw(String[] args) {
        String opName = null;
        int opArity = -1;
        
        // Parse arguments
        for (int i = 1; i < args.length; i++) {
            if (args[i].equals("--op-name") && i + 1 < args.length) {
                opName = args[++i];
            } else if (args[i].equals("--op-arity") && i + 1 < args.length) {
                opArity = Integer.parseInt(args[++i]);
            }
        }
        
        if (opName == null || opArity == -1) {
            System.err.println("Error: --op-name and --op-arity are required");
            System.exit(1);
        }
        
        try {
            OperationSymbol op = new OperationSymbol(opName, opArity, false);
            Equation equation = Equations.firstSecondSymmetricLaw(op);
            
            System.out.println("First-Second Symmetric Law Equation:");
            System.out.println("Operation: " + opName + "/" + opArity);
            System.out.println("Equation: " + equation);
            System.out.println("Left side: " + equation.leftSide());
            System.out.println("Right side: " + equation.rightSide());
            System.out.println("Variables: " + equation.getVariableList());
        } catch (IllegalArgumentException e) {
            System.err.println("Error: " + e.getMessage());
            System.exit(1);
        }
    }
    
    private static void runTests() {
        System.out.println("Running Equations tests...");
        System.out.println();
        
        // Test associative law
        System.out.println("Test 1: Associative Law (binary operation)");
        try {
            OperationSymbol mult = new OperationSymbol("multiply", 2, false);
            Equation assocEq = Equations.associativeLaw(mult);
            System.out.println("✓ Associative law generated: " + assocEq);
        } catch (Exception e) {
            System.out.println("✗ Associative law failed: " + e.getMessage());
        }
        
        // Test associative law with wrong arity
        System.out.println("Test 2: Associative Law (wrong arity)");
        try {
            OperationSymbol unary = new OperationSymbol("unary_op", 1, false);
            Equations.associativeLaw(unary);
            System.out.println("✗ Should have thrown exception for wrong arity");
        } catch (IllegalArgumentException e) {
            System.out.println("✓ Correctly caught wrong arity: " + e.getMessage());
        }
        
        // Test cyclic law
        System.out.println("Test 3: Cyclic Law (ternary operation)");
        try {
            OperationSymbol ternary = new OperationSymbol("ternary_op", 3, false);
            Equation cyclicEq = Equations.cyclicLaw(ternary);
            System.out.println("✓ Cyclic law generated: " + cyclicEq);
        } catch (Exception e) {
            System.out.println("✗ Cyclic law failed: " + e.getMessage());
        }
        
        // Test cyclic law with unary operation
        System.out.println("Test 4: Cyclic Law (unary operation)");
        try {
            OperationSymbol unary = new OperationSymbol("unary_op", 1, false);
            Equation cyclicEq = Equations.cyclicLaw(unary);
            System.out.println("✓ Cyclic law (unary) generated: " + cyclicEq);
        } catch (Exception e) {
            System.out.println("✗ Cyclic law (unary) failed: " + e.getMessage());
        }
        
        // Test first-second symmetric law
        System.out.println("Test 5: First-Second Symmetric Law (binary operation)");
        try {
            OperationSymbol binary = new OperationSymbol("binary_op", 2, false);
            Equation symmEq = Equations.firstSecondSymmetricLaw(binary);
            System.out.println("✓ First-second symmetric law generated: " + symmEq);
        } catch (Exception e) {
            System.out.println("✗ First-second symmetric law failed: " + e.getMessage());
        }
        
        // Test first-second symmetric law with unary operation
        System.out.println("Test 6: First-Second Symmetric Law (wrong arity)");
        try {
            OperationSymbol unary = new OperationSymbol("unary_op", 1, false);
            Equations.firstSecondSymmetricLaw(unary);
            System.out.println("✗ Should have thrown exception for wrong arity");
        } catch (IllegalArgumentException e) {
            System.out.println("✓ Correctly caught wrong arity: " + e.getMessage());
        }
        
        System.out.println();
        System.out.println("All tests completed!");
    }
}
