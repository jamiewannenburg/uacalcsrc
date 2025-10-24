package group;

import java.util.List;

/**
 * Simple wrapper for GeneralAlgebra-like functionality for PermutationGroup.
 */
public class GeneralAlgebraWrapper {
    
    private final List<IntArrayWrapper> generators;
    
    /**
     * Create a GeneralAlgebraWrapper with the given generators.
     * 
     * @param generators The generators
     */
    public GeneralAlgebraWrapper(List<IntArrayWrapper> generators) {
        this.generators = generators;
    }
    
    /**
     * Get the generators.
     * 
     * @return The generators
     */
    public List<IntArrayWrapper> getGenerators() {
        return generators;
    }
    
    @Override
    public String toString() {
        return "GeneralAlgebraWrapper{" +
                "generators=" + generators +
                '}';
    }
}
