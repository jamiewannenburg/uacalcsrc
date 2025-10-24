package group;

import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Optional;
import java.util.stream.Collectors;

// Local imports

/**
 * Java wrapper for PermutationGroup Rust implementation.
 * 
 * This class provides a Java interface to the Rust PermutationGroup implementation,
 * allowing Java code to create and manipulate permutation groups.
 */
public class PermutationGroupWrapper {
    
    private final String name;
    private final List<IntArrayWrapper> generators;
    private final Optional<List<IntArrayWrapper>> universeList;
    private final int underlyingSetSize;
    private final Optional<IntArrayWrapper> identity;
    private final GeneralAlgebraWrapper generalAlgebra;
    
    /**
     * Create a new PermutationGroup with the given name and generators.
     * 
     * @param name The name of the permutation group
     * @param generators The generators of the group
     */
    public PermutationGroupWrapper(String name, List<List<Integer>> generators) {
        this.name = name;
        this.generators = generators.stream()
            .map(gen -> IntArrayWrapper.fromArray(gen))
            .collect(Collectors.toList());
        this.universeList = Optional.empty();
        this.underlyingSetSize = generators.isEmpty() ? 0 : generators.get(0).size();
        this.identity = underlyingSetSize > 0 ? 
            Optional.of(IntArrayWrapper.fromArray(createIdentity(underlyingSetSize))) : 
            Optional.empty();
        this.generalAlgebra = new GeneralAlgebraWrapper(this.generators);
    }
    
    /**
     * Create a new PermutationGroup with the given name, generators, and universe list.
     * 
     * @param name The name of the permutation group
     * @param generators The generators of the group
     * @param universeList The universe list for the group
     */
    public PermutationGroupWrapper(String name, List<List<Integer>> generators, List<List<Integer>> universeList) {
        this.name = name;
        this.generators = generators.stream()
            .map(gen -> IntArrayWrapper.fromArray(gen))
            .collect(Collectors.toList());
        this.universeList = Optional.of(universeList.stream()
            .map(univ -> IntArrayWrapper.fromArray(univ))
            .collect(Collectors.toList()));
        this.underlyingSetSize = generators.isEmpty() ? 0 : generators.get(0).size();
        this.identity = underlyingSetSize > 0 ? 
            Optional.of(IntArrayWrapper.fromArray(createIdentity(underlyingSetSize))) : 
            Optional.empty();
        this.generalAlgebra = new GeneralAlgebraWrapper(this.generators);
    }
    
    /**
     * Create a new PermutationGroup with validation.
     * 
     * @param name The name of the permutation group
     * @param generators The generators of the group
     * @return A new PermutationGroupWrapper
     * @throws IllegalArgumentException if validation fails
     */
    public static PermutationGroupWrapper newSafe(String name, List<List<Integer>> generators) {
        if (generators.isEmpty()) {
            throw new IllegalArgumentException("Generators cannot be empty");
        }
        
        int firstSize = generators.get(0).size();
        for (int i = 0; i < generators.size(); i++) {
            if (generators.get(i).size() != firstSize) {
                throw new IllegalArgumentException(
                    String.format("Generator %d has size %d, expected %d", 
                        i, generators.get(i).size(), firstSize));
            }
        }
        
        return new PermutationGroupWrapper(name, generators);
    }
    
    /**
     * Create a new PermutationGroup with universe list and validation.
     * 
     * @param name The name of the permutation group
     * @param generators The generators of the group
     * @param universeList The universe list for the group
     * @return A new PermutationGroupWrapper
     * @throws IllegalArgumentException if validation fails
     */
    public static PermutationGroupWrapper newWithUniverseSafe(String name, 
            List<List<Integer>> generators, List<List<Integer>> universeList) {
        if (generators.isEmpty()) {
            throw new IllegalArgumentException("Generators cannot be empty");
        }
        
        int firstSize = generators.get(0).size();
        for (int i = 0; i < generators.size(); i++) {
            if (generators.get(i).size() != firstSize) {
                throw new IllegalArgumentException(
                    String.format("Generator %d has size %d, expected %d", 
                        i, generators.get(i).size(), firstSize));
            }
        }
        
        return new PermutationGroupWrapper(name, generators, universeList);
    }
    
    /**
     * Compute the product of two permutations.
     * 
     * @param p1 The first permutation
     * @param p2 The second permutation
     * @return The product permutation
     */
    public static List<Integer> prod(List<Integer> p1, List<Integer> p2) {
        if (p1.size() != p2.size()) {
            throw new IllegalArgumentException("Permutations must have the same size");
        }
        
        int n = p1.size();
        List<Integer> result = new ArrayList<>(n);
        
        for (int i = 0; i < n; i++) {
            int index = p2.get(i);
            if (index < 0 || index >= n) {
                throw new IllegalArgumentException(
                    String.format("Invalid permutation: index %d out of bounds for size %d", index, n));
            }
            result.add(p1.get(index));
        }
        
        return result;
    }
    
    /**
     * Compute the inverse of a permutation.
     * 
     * @param p The permutation to invert
     * @return The inverse permutation
     */
    public static List<Integer> inv(List<Integer> p) {
        int n = p.size();
        List<Integer> result = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            result.add(0);
        }
        
        for (int i = 0; i < n; i++) {
            int index = p.get(i);
            if (index < 0 || index >= n) {
                throw new IllegalArgumentException(
                    String.format("Invalid permutation: index %d out of bounds for size %d", index, n));
            }
            result.set(index, i);
        }
        
        return result;
    }
    
    /**
     * Create an identity permutation of the given size.
     * 
     * @param setSize The size of the permutation
     * @return The identity permutation
     */
    public static List<Integer> id(int setSize) {
        List<Integer> result = new ArrayList<>(setSize);
        for (int i = 0; i < setSize; i++) {
            result.add(i);
        }
        return result;
    }
    
    /**
     * Get the name of the permutation group.
     * 
     * @return The name
     */
    public String getName() {
        return name;
    }
    
    /**
     * Get the generators of the permutation group.
     * 
     * @return The generators
     */
    public List<List<Integer>> getGenerators() {
        return generators.stream()
            .map(gen -> {
                int[] array = gen.asArray();
                List<Integer> list = new ArrayList<>();
                for (int i : array) {
                    list.add(i);
                }
                return list;
            })
            .collect(Collectors.toList());
    }
    
    /**
     * Get the universe list of the permutation group.
     * 
     * @return The universe list, if present
     */
    public Optional<List<List<Integer>>> getUniverseList() {
        return universeList.map(univ -> univ.stream()
            .map(u -> {
                int[] array = u.asArray();
                List<Integer> list = new ArrayList<>();
                for (int i : array) {
                    list.add(i);
                }
                return list;
            })
            .collect(Collectors.toList()));
    }
    
    /**
     * Get the underlying set size of the permutation group.
     * 
     * @return The underlying set size
     */
    public int getUnderlyingSetSize() {
        return underlyingSetSize;
    }
    
    /**
     * Get the identity permutation of the permutation group.
     * 
     * @return The identity permutation, if present
     */
    public Optional<List<Integer>> getIdentity() {
        return identity.map(id -> {
            int[] array = id.asArray();
            List<Integer> list = new ArrayList<>();
            for (int i : array) {
                list.add(i);
            }
            return list;
        });
    }
    
    /**
     * Get the general algebra of the permutation group.
     * 
     * @return The general algebra
     */
    public GeneralAlgebraWrapper getGeneralAlgebra() {
        return generalAlgebra;
    }
    
    /**
     * Create an identity permutation of the given size.
     * 
     * @param size The size of the permutation
     * @return The identity permutation as a list
     */
    private static List<Integer> createIdentity(int size) {
        List<Integer> identity = new ArrayList<>(size);
        for (int i = 0; i < size; i++) {
            identity.add(i);
        }
        return identity;
    }
    
    @Override
    public String toString() {
        return String.format("PermutationGroup(%s)", name);
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        
        PermutationGroupWrapper that = (PermutationGroupWrapper) obj;
        
        if (underlyingSetSize != that.underlyingSetSize) return false;
        if (!name.equals(that.name)) return false;
        if (!generators.equals(that.generators)) return false;
        if (!universeList.equals(that.universeList)) return false;
        if (!identity.equals(that.identity)) return false;
        
        return true;
    }
    
    @Override
    public int hashCode() {
        int result = name.hashCode();
        result = 31 * result + generators.hashCode();
        result = 31 * result + universeList.hashCode();
        result = 31 * result + underlyingSetSize;
        result = 31 * result + identity.hashCode();
        return result;
    }
}
