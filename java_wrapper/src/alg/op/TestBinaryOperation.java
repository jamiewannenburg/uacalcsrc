/* TestBinaryOperation.java - Test binary operation class for Java wrappers */

package java_wrapper.src.alg.op;

import java.util.*;
import org.uacalc.alg.op.OperationSymbol;
import org.uacalc.alg.op.Operation;
import org.uacalc.alg.op.AbstractOperation;

/**
 * Simple test binary operation: (a + b) % setSize
 */
public class TestBinaryOperation extends AbstractOperation {
    private boolean tableCreated = false;
    private int[] table = null;
    
    public TestBinaryOperation(String name, int setSize) {
        super(new OperationSymbol(name, 2), setSize);
    }
    
    @Override
    public int intValueAt(int[] args) {
        if (args.length != 2) {
            throw new IllegalArgumentException("Binary operation requires 2 arguments");
        }
        return (args[0] + args[1]) % getSetSize();
    }
    
    @Override
    public Object valueAt(List args) {
        if (args.size() != 2) {
            throw new IllegalArgumentException("Binary operation requires 2 arguments");
        }
        int arg0 = ((Integer) args.get(0)).intValue();
        int arg1 = ((Integer) args.get(1)).intValue();
        return Integer.valueOf((arg0 + arg1) % getSetSize());
    }
    
    @Override
    public void makeTable() {
        super.makeTable();
        tableCreated = true;
        
        // Create the table: for binary operation with set size n, table size is n^2
        int size = getSetSize();
        table = new int[size * size];
        int index = 0;
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                table[index++] = intValueAt(new int[]{i, j});
            }
        }
    }
    
    @Override
    public boolean isTableBased() {
        return tableCreated;
    }
    
    @Override
    public int[] getTable() {
        return table;
    }
}