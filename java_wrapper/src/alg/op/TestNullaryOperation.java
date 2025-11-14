/* TestNullaryOperation.java - Test nullary operation class for Java wrappers */

package java_wrapper.src.alg.op;

import java.util.*;
import org.uacalc.alg.op.OperationSymbol;
import org.uacalc.alg.op.Operation;
import org.uacalc.alg.op.AbstractOperation;

/**
 * Simple test nullary operation: returns 0
 */
public class TestNullaryOperation extends AbstractOperation {
    private boolean tableCreated = false;
    private int[] table = null;
    
    public TestNullaryOperation(String name, int setSize) {
        super(new OperationSymbol(name, 0), setSize);
    }
    
    @Override
    public int intValueAt(int[] args) {
        if (args.length != 0) {
            throw new IllegalArgumentException("Nullary operation requires 0 arguments");
        }
        return 0;
    }
    
    @Override
    public Object valueAt(List args) {
        if (args.size() != 0) {
            throw new IllegalArgumentException("Nullary operation requires 0 arguments");
        }
        return Integer.valueOf(0);
    }
    
    @Override
    public void makeTable() {
        super.makeTable();
        tableCreated = true;
        
        // Create the table: for nullary operation, table size is 1
        table = new int[]{intValueAt(new int[]{})};
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