package org.uacalc.alg.op;

import java.util.List;

/**
 * Simplified Operation interface for testing Rust wrapper compatibility.
 * This is a minimal version of the full UACalc Operation interface.
 */
public interface Operation extends Comparable<Operation> {
    
    /**
     * This gives the arity of this operation.
     */
    int arity();

    /**
     * This gives the size of the set upon which the operation is defined.
     */
    int getSetSize();

    /**
     * The operation symbol for this operation.
     */
    OperationSymbol symbol();

    /**
     * This operation is the element version.
     */
    Object valueAt(List args);

    /**
     * This operation is for fast product operation. 
     */
    int[] valueAt(int[][] args);

    /**
     * This (optional) operation is the int version.
     */
    int intValueAt(int[] args);
    
    /**
     * This (optional) operation is for fast access to the table.
     */
    int intValueAt(int arg);

    /**
     * Make a table for faster evaluation.
     */
    void makeTable();

    /**
     * Get the table for this operation or null if it does not exist.
     */
    int[] getTable();
    
    /**
     * Get the table for this operation, making it if necessary.
     */
    int[] getTable(boolean makeTable);
    
    boolean isTableBased();

    /**
     * Is this operation idempotent in the sense f(x,x,..,x) = x.
     */
    boolean isIdempotent();

    /**
     * Is this operation binary and associative.
     */
    boolean isAssociative();

    /**
     * Is this operation binary and commutative.
     */
    boolean isCommutative();

    /**
     * Is this operation totally symmetric.
     */
    boolean isTotallySymmetric();
    
    /**
     * Check if a ternary operation is a Maltsev operation.
     */
    boolean isMaltsev();
    
    /**
     * Only OperationWithDefaultValue's can fail this.
     */
    boolean isTotal();
}