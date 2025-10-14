// Java test wrapper for Operation implementations
// This file provides test utilities for comparing Java and Rust implementations

package test_wrappers;

import org.uacalc.alg.op.*;

/**
 * Test utilities for Operation implementations
 */
public class OperationTest {
    
    /**
     * Create a simple binary operation for testing (XOR on {0,1})
     */
    public static Operation createXorOperation() {
        // Create using Operations utility class
        int[] table = {0, 1, 1, 0}; // XOR truth table
        return Operations.makeIntOperation("xor", 2, table, 2);
    }
    
    /**
     * Create a simple unary operation for testing (NOT on {0,1})
     */
    public static Operation createNotOperation() {
        int[] table = {1, 0}; // NOT truth table
        return Operations.makeIntOperation("not", 1, table, 2);
    }
    
    /**
     * Create addition modulo n operation
     */
    public static Operation createAdditionMod(int n) {
        int[] table = new int[n * n];
        int index = 0;
        for (int a = 0; a < n; a++) {
            for (int b = 0; b < n; b++) {
                table[index++] = (a + b) % n;
            }
        }
        return Operations.makeIntOperation("add_mod" + n, 2, table, n);
    }
    
    /**
     * Create a max operation on {0, 1, ..., n-1}
     */
    public static Operation createMaxOperation(int n) {
        int[] table = new int[n * n];
        int index = 0;
        for (int a = 0; a < n; a++) {
            for (int b = 0; b < n; b++) {
                table[index++] = Math.max(a, b);
            }
        }
        return Operations.makeIntOperation("max", 2, table, n);
    }
    
    /**
     * Create a ternary Maltsev operation on {0, 1}
     */
    public static Operation createMaltsevOperation() {
        // Maltsev operation: f(x,y,y) = x and f(x,x,y) = y
        int[] table = {0, 1, 0, 0, 1, 1, 0, 1};
        return Operations.makeIntOperation("maltsev", 3, table, 2);
    }
    
    /**
     * Test operation properties
     */
    public static void testOperationProperties(Operation op) {
        System.out.println("Testing operation: " + op.symbol());
        System.out.println("  Arity: " + op.arity());
        System.out.println("  Set size: " + op.getSetSize());
        System.out.println("  Is table-based: " + op.isTableBased());
        System.out.println("  Is idempotent: " + op.isIdempotent());
        
        if (op.arity() == 2) {
            System.out.println("  Is associative: " + op.isAssociative());
            System.out.println("  Is commutative: " + op.isCommutative());
        }
        
        System.out.println("  Is totally symmetric: " + op.isTotallySymmetric());
        
        if (op.arity() == 3) {
            System.out.println("  Is Maltsev: " + op.isMaltsev());
        }
        
        System.out.println("  Is total: " + op.isTotal());
        System.out.println();
    }
    
    /**
     * Test operation evaluation for small cases
     */
    public static void testOperationEvaluation(Operation op) {
        System.out.println("Testing evaluation for operation: " + op.symbol());
        
        int arity = op.arity();
        int setSize = op.getSetSize();
        
        // Only test small cases to avoid excessive output
        if (setSize <= 3 && arity <= 2) {
            int[] args = new int[arity];
            
            // Generate all possible argument combinations
            int totalCombinations = (int) Math.pow(setSize, arity);
            for (int i = 0; i < totalCombinations; i++) {
                // Convert i to base-setSize representation
                int temp = i;
                for (int j = arity - 1; j >= 0; j--) {
                    args[j] = temp % setSize;
                    temp /= setSize;
                }
                
                int result = op.intValueAt(args);
                
                System.out.print("  " + op.symbol() + "(");
                for (int j = 0; j < arity; j++) {
                    System.out.print(args[j]);
                    if (j < arity - 1) System.out.print(",");
                }
                System.out.println(") = " + result);
            }
        }
        System.out.println();
    }
    
    /**
     * Main method for running tests
     */
    public static void main(String[] args) {
        System.out.println("Testing Operation implementations");
        System.out.println("================================");
        
        // Test XOR operation
        Operation xor = createXorOperation();
        testOperationProperties(xor);
        testOperationEvaluation(xor);
        
        // Test NOT operation
        Operation not = createNotOperation();
        testOperationProperties(not);
        testOperationEvaluation(not);
        
        // Test addition mod 3
        Operation addMod3 = createAdditionMod(3);
        testOperationProperties(addMod3);
        testOperationEvaluation(addMod3);
        
        // Test max operation
        Operation max = createMaxOperation(3);
        testOperationProperties(max);
        testOperationEvaluation(max);
        
        // Test Maltsev operation
        Operation maltsev = createMaltsevOperation();
        testOperationProperties(maltsev);
        // Skip evaluation for ternary operations (too much output)
        
        System.out.println("All tests completed!");
    }
}