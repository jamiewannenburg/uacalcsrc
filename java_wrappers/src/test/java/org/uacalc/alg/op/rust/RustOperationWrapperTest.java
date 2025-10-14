package org.uacalc.alg.op.rust;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import org.uacalc.alg.op.Operation;
import java.util.Arrays;
import java.util.List;

/**
 * Test suite for RustOperationWrapper to ensure compatibility with Java Operation interface.
 */
public class RustOperationWrapperTest {
    
    private RustOperationWrapper identity3;
    private RustOperationWrapper constant2_3_1;
    private RustOperationWrapper maltsevOp;
    
    @BeforeEach
    void setUp() {
        // Create identity operation on set {0, 1, 2}
        identity3 = RustOperationWrapper.identity(3);
        
        // Create constant operation f(x,y) = 1 on set {0, 1, 2}
        constant2_3_1 = RustOperationWrapper.constant(2, 3, 1);
        
        // Create a Maltsev operation
        int[] maltsevTable = new int[27]; // 3^3 = 27
        for (int x = 0; x < 3; x++) {
            for (int y = 0; y < 3; y++) {
                for (int z = 0; z < 3; z++) {
                    int index = x * 9 + y * 3 + z;
                    if (y == z) {
                        maltsevTable[index] = x; // f(x,y,y) = x
                    } else if (x == y) {
                        maltsevTable[index] = z; // f(x,x,z) = z
                    } else {
                        maltsevTable[index] = 0; // Default case
                    }
                }
            }
        }
        maltsevOp = new RustOperationWrapper("maltsev", 3, 3, maltsevTable);
    }
    
    @Test
    void testBasicProperties() {
        assertEquals(1, identity3.arity());
        assertEquals(3, identity3.getSetSize());
        assertEquals("identity", identity3.symbol().name());
        assertTrue(identity3.isTableBased());
        
        assertEquals(2, constant2_3_1.arity());
        assertEquals(3, constant2_3_1.getSetSize());
        assertEquals("const_1", constant2_3_1.symbol().name());
    }
    
    @Test
    void testIdentityOperation() {
        // Test identity property: f(x) = x
        assertEquals(0, identity3.intValueAt(new int[]{0}));
        assertEquals(1, identity3.intValueAt(new int[]{1}));
        assertEquals(2, identity3.intValueAt(new int[]{2}));
        
        // Test with generic valueAt method
        List<Integer> args = Arrays.asList(1);
        assertEquals(1, identity3.valueAt(args));
    }
    
    @Test
    void testConstantOperation() {
        // Test constant property: f(x,y) = 1 for all x,y
        for (int x = 0; x < 3; x++) {
            for (int y = 0; y < 3; y++) {
                assertEquals(1, constant2_3_1.intValueAt(new int[]{x, y}));
            }
        }
    }
    
    @Test
    void testPropertyChecks() {
        // Identity should be idempotent
        assertTrue(identity3.isIdempotent());
        assertTrue(identity3.isTotal());
        
        // Constant operation properties
        assertTrue(constant2_3_1.isCommutative()); // Constants are commutative
        assertTrue(constant2_3_1.isTotal());
        assertFalse(constant2_3_1.isIdempotent()); // f(0,0) = 1 ≠ 0
        
        // Maltsev operation properties
        assertEquals(3, maltsevOp.arity());
        assertTrue(maltsevOp.isMaltsev());
        assertTrue(maltsevOp.isTotal());
    }
    
    @Test
    void testMaltsevIdentities() {
        // Test f(x,y,y) = x and f(x,x,y) = y
        for (int x = 0; x < 3; x++) {
            for (int y = 0; y < 3; y++) {
                assertEquals(x, maltsevOp.intValueAt(new int[]{x, y, y}));
                assertEquals(y, maltsevOp.intValueAt(new int[]{x, x, y}));
            }
        }
    }
    
    @Test
    void testArrayEvaluation() {
        // Test array-based evaluation
        int[][] args = {{0, 1, 2}, {1, 2, 0}};
        int[] result = constant2_3_1.valueAt(args);
        
        assertEquals(3, result.length);
        assertEquals(1, result[0]); // f(0,1) = 1
        assertEquals(1, result[1]); // f(1,2) = 1 
        assertEquals(1, result[2]); // f(2,0) = 1
    }
    
    @Test
    void testTableAccess() {
        int[] table = identity3.getTable();
        assertNotNull(table);
        assertEquals(3, table.length);
        assertArrayEquals(new int[]{0, 1, 2}, table);
        
        // Test Horner encoding access
        assertEquals(0, identity3.intValueAt(0));
        assertEquals(1, identity3.intValueAt(1));
        assertEquals(2, identity3.intValueAt(2));
    }
    
    @Test
    void testComparison() {
        Operation identity = RustOperationWrapper.identity(3);
        Operation constant = RustOperationWrapper.constant(2, 3, 1);
        
        // Higher arity should come first in comparison
        assertTrue(constant.compareTo(identity) < 0);
        assertTrue(identity.compareTo(constant) > 0);
        
        // Same operation should be equal
        assertEquals(0, identity.compareTo(identity3));
    }
    
    @Test
    void testErrorHandling() {
        // Test invalid arguments
        assertThrows(IllegalArgumentException.class, () -> {
            identity3.intValueAt(new int[]{0, 1}); // Wrong arity
        });
        
        assertThrows(IllegalArgumentException.class, () -> {
            identity3.intValueAt(new int[]{3}); // Out of range
        });
        
        assertThrows(IndexOutOfBoundsException.class, () -> {
            identity3.intValueAt(5); // Horner index out of bounds
        });
    }
}