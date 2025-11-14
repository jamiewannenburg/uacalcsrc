/* TestUnaryOperation.java - Test unary operation class for Java wrappers */

package java_wrapper.src.alg.op;

import java.util.*;
import org.uacalc.alg.op.OperationSymbol;
import org.uacalc.alg.op.Operation;
import org.uacalc.alg.op.AbstractOperation;

/**
 * Simple test unary operation: (a + 1) % setSize
 */
public class TestUnaryOperation extends AbstractOperation {
    private boolean tableCreated = false;
    private int[] table = null;
    
    public TestUnaryOperation(String name, int setSize) {
        super(new OperationSymbol(name, 1), setSize);
    }
    
    @Override
    public int intValueAt(int[] args) {
        if (args.length != 1) {
            throw new IllegalArgumentException("Unary operation requires 1 argument");
        }
        return (args[0] + 1) % getSetSize();
    }
    
    @Override
    public Object valueAt(List args) {
        if (args.size() != 1) {
            throw new IllegalArgumentException("Unary operation requires 1 argument");
        }
        int arg0 = ((Integer) args.get(0)).intValue();
        return Integer.valueOf((arg0 + 1) % getSetSize());
    }
    
    @Override
    public void makeTable() {
        super.makeTable();
        tableCreated = true;
        
        // Create the table: for unary operation with set size n, table size is n
        int size = getSetSize();
        table = new int[size];
        for (int i = 0; i < size; i++) {
            table[i] = intValueAt(new int[]{i});
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
