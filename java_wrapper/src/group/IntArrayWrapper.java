package group;

import java.util.List;
import java.util.Arrays;

/**
 * Simple wrapper for IntArray-like functionality for PermutationGroup.
 */
public class IntArrayWrapper {
    
    private final int[] array;
    
    /**
     * Create an IntArrayWrapper from an array of integers.
     * 
     * @param array The array of integers
     */
    public IntArrayWrapper(int[] array) {
        this.array = array.clone();
    }
    
    /**
     * Create an IntArrayWrapper from a list of integers.
     * 
     * @param list The list of integers
     */
    public IntArrayWrapper(List<Integer> list) {
        this.array = list.stream().mapToInt(i -> i).toArray();
    }
    
    /**
     * Create an IntArrayWrapper from an array of integers.
     * 
     * @param array The array of integers
     * @return A new IntArrayWrapper
     */
    public static IntArrayWrapper fromArray(int[] array) {
        return new IntArrayWrapper(array);
    }
    
    /**
     * Create an IntArrayWrapper from a list of integers.
     * 
     * @param list The list of integers
     * @return A new IntArrayWrapper
     */
    public static IntArrayWrapper fromArray(List<Integer> list) {
        return new IntArrayWrapper(list);
    }
    
    /**
     * Get the underlying array.
     * 
     * @return The array
     */
    public int[] asArray() {
        return array.clone();
    }
    
    /**
     * Get the size of the array.
     * 
     * @return The size
     */
    public int size() {
        return array.length;
    }
    
    /**
     * Get the element at the given index.
     * 
     * @param index The index
     * @return The element
     */
    public int get(int index) {
        return array[index];
    }
    
    /**
     * Set the element at the given index.
     * 
     * @param index The index
     * @param value The value
     */
    public void set(int index, int value) {
        array[index] = value;
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        
        IntArrayWrapper that = (IntArrayWrapper) obj;
        return Arrays.equals(array, that.array);
    }
    
    @Override
    public int hashCode() {
        return Arrays.hashCode(array);
    }
    
    @Override
    public String toString() {
        return Arrays.toString(array);
    }
}
