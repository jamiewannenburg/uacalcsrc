package org.uacalc.alg.op.rust;

import org.uacalc.alg.op.*;
import java.util.List;

/**
 * Java wrapper for Rust-based Operation implementations.
 * This class provides a bridge between Java and Rust Operation implementations
 * for testing and compatibility purposes.
 */
public class RustOperationWrapper implements Operation {
    
    private final String name;
    private final int arity;
    private final int setSize;
    private final int[] table;
    private final OperationSymbol symbol;
    
    /**
     * Create a new RustOperationWrapper with a lookup table.
     */
    public RustOperationWrapper(String name, int arity, int setSize, int[] table) {
        this.name = name;
        this.arity = arity;
        this.setSize = setSize;
        this.table = table.clone();
        this.symbol = new OperationSymbol(name, arity);
    }
    
    /**
     * Create an identity operation wrapper.
     */
    public static RustOperationWrapper identity(int setSize) {
        int[] table = new int[setSize];
        for (int i = 0; i < setSize; i++) {
            table[i] = i;
        }
        return new RustOperationWrapper("identity", 1, setSize, table);
    }
    
    /**
     * Create a constant operation wrapper.
     */
    public static RustOperationWrapper constant(int arity, int setSize, int constant) {
        int tableSize = arity == 0 ? 1 : (int) Math.pow(setSize, arity);
        int[] table = new int[tableSize];
        for (int i = 0; i < tableSize; i++) {
            table[i] = constant;
        }
        return new RustOperationWrapper("const_" + constant, arity, setSize, table);
    }
    
    @Override
    public int arity() {
        return arity;
    }
    
    @Override
    public int getSetSize() {
        return setSize;
    }
    
    @Override
    public OperationSymbol symbol() {
        return symbol;
    }
    
    @Override
    public Object valueAt(List args) {
        // Convert to int array and delegate
        int[] intArgs = new int[args.size()];
        for (int i = 0; i < args.size(); i++) {
            intArgs[i] = (Integer) args.get(i);
        }
        return intValueAt(intArgs);
    }
    
    @Override
    public int[] valueAt(int[][] args) {
        if (args.length == 0) return new int[0];
        
        int resultLength = args[0].length;
        int[] result = new int[resultLength];
        
        for (int i = 0; i < resultLength; i++) {
            int[] pointArgs = new int[args.length];
            for (int j = 0; j < args.length; j++) {
                pointArgs[j] = args[j][i];
            }
            result[i] = intValueAt(pointArgs);
        }
        
        return result;
    }
    
    @Override
    public int intValueAt(int[] args) {
        if (args.length != arity) {
            throw new IllegalArgumentException("Expected " + arity + " arguments, got " + args.length);
        }
        
        // Convert arguments to table index using Horner's method
        int index = 0;
        for (int arg : args) {
            if (arg < 0 || arg >= setSize) {
                throw new IllegalArgumentException("Argument " + arg + " out of range [0, " + setSize + ")");
            }
            index = index * setSize + arg;
        }
        
        if (index >= table.length) {
            throw new IndexOutOfBoundsException("Index " + index + " out of bounds for table of size " + table.length);
        }
        
        return table[index];
    }
    
    @Override
    public int intValueAt(int arg) {
        if (arg < 0 || arg >= table.length) {
            throw new IndexOutOfBoundsException("Horner index " + arg + " out of bounds for table of size " + table.length);
        }
        return table[arg];
    }
    
    @Override
    public void makeTable() {
        // Table already exists
    }
    
    @Override
    public int[] getTable() {
        return table.clone();
    }
    
    @Override
    public int[] getTable(boolean makeTable) {
        return getTable();
    }
    
    @Override
    public boolean isTableBased() {
        return true;
    }
    
    @Override
    public boolean isIdempotent() {
        for (int i = 0; i < setSize; i++) {
            int[] args = new int[arity];
            for (int j = 0; j < arity; j++) {
                args[j] = i;
            }
            if (intValueAt(args) != i) {
                return false;
            }
        }
        return true;
    }
    
    @Override
    public boolean isAssociative() {
        if (arity != 2) return false;
        
        for (int a = 0; a < setSize; a++) {
            for (int b = 0; b < setSize; b++) {
                for (int c = 0; c < setSize; c++) {
                    int ab = intValueAt(new int[]{a, b});
                    int bc = intValueAt(new int[]{b, c});
                    int ab_c = intValueAt(new int[]{ab, c});
                    int a_bc = intValueAt(new int[]{a, bc});
                    
                    if (ab_c != a_bc) {
                        return false;
                    }
                }
            }
        }
        
        return true;
    }
    
    @Override
    public boolean isCommutative() {
        if (arity != 2) return false;
        
        for (int a = 0; a < setSize; a++) {
            for (int b = 0; b < setSize; b++) {
                int ab = intValueAt(new int[]{a, b});
                int ba = intValueAt(new int[]{b, a});
                
                if (ab != ba) {
                    return false;
                }
            }
        }
        
        return true;
    }
    
    @Override
    public boolean isTotallySymmetric() {
        if (arity <= 1) return true;
        if (arity == 2) return isCommutative();
        
        // For higher arities, this would require checking all permutations
        // For now, return a conservative result
        return false;
    }
    
    @Override
    public boolean isMaltsev() {
        if (arity != 3) return false;
        
        for (int x = 0; x < setSize; x++) {
            for (int y = 0; y < setSize; y++) {
                int f_xyy = intValueAt(new int[]{x, y, y});
                int f_xxy = intValueAt(new int[]{x, x, y});
                
                if (f_xyy != x || f_xxy != y) {
                    return false;
                }
            }
        }
        
        return true;
    }
    
    @Override
    public boolean isTotal() {
        return true; // Table-based operations are always total
    }
    
    @Override
    public int compareTo(Operation other) {
        // Compare by arity first (higher arity first), then by name
        int arityCompare = Integer.compare(other.arity(), this.arity());
        if (arityCompare != 0) return arityCompare;
        
        return this.symbol().name().compareTo(other.symbol().name());
    }
    
    @Override
    public String toString() {
        return name + "[rust-table]";
    }
}