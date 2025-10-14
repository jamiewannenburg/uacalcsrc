package org.uacalc.alg.op;

/**
 * Simplified OperationSymbol class for testing Rust wrapper compatibility.
 * This is a minimal version of the full UACalc OperationSymbol class.
 */
public class OperationSymbol implements Comparable<OperationSymbol> {
    
    private final String name;
    private final int arity;
    private boolean associative = false;
    
    public OperationSymbol(String name, int arity) {
        this(name, arity, false);
    }

    public OperationSymbol(String name, int arity, boolean assoc) {
        this.name = name;
        this.arity = arity;
        setAssociative(assoc);
    }

    /**
     * This gives the arity of this operation.
     */
    public int arity() { 
        return arity; 
    }

    public String name() { 
        return name; 
    }
    
    public boolean isAssociative() { 
        return associative; 
    }
    
    public void setAssociative(boolean assoc) {
        if (assoc && arity != 2) {
            throw new IllegalArgumentException("Only binary operations can be associative.");
        }
        this.associative = assoc && arity == 2;
    }

    public String toString() { 
        return toString(false); 
    }
    
    public String toString(boolean showArity) {
        if (showArity) return name + "(" + arity + ")";
        return name; 
    }

    /**
     * This puts high arity operations first.
     */
    public int compareTo(OperationSymbol sym) {
        if (arity < sym.arity()) return 1;
        if (arity > sym.arity()) return -1;
        return name.compareTo(sym.name());
    }

    public boolean equals(Object obj) {
        if (!(obj instanceof OperationSymbol)) return false;
        OperationSymbol sym = (OperationSymbol)obj;
        return name.equals(sym.name()) && arity == sym.arity();
    }

    public int hashCode() {
        return name.hashCode() + arity;
    }
}