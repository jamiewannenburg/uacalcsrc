/* MockBasicSet.java - Mock implementation of BasicSet for testing
 * 
 * This is a simplified mock implementation of BasicSet for testing purposes.
 * It provides the basic functionality needed for the wrapper tests.
 */

package sublat;

import java.util.*;

/**
 * Mock implementation of BasicSet for testing purposes.
 */
public class MockBasicSet {
    private int[] array;
    private int size;
    
    public MockBasicSet(int[] set) {
        this.array = set.clone();
        this.size = set.length;
        normalize();
    }
    
    public void normalize() {
        Arrays.sort(array);
        // Remove duplicates
        Set<Integer> unique = new HashSet<>();
        for (int i : array) {
            unique.add(i);
        }
        array = unique.stream().mapToInt(i -> i).toArray();
        size = array.length;
    }
    
    public int compareTo(Object o) {
        MockBasicSet set = (MockBasicSet) o;
        if (size < set.size) return -1;
        if (size > set.size) return 1;
        for (int i = 0; i < size; i++) {
            if (array[i] < set.array[i]) return -1;
            if (array[i] > set.array[i]) return 1;
        }
        return 0;
    }
    
    public boolean leq(MockBasicSet set2) {
        return leq(this.array, set2.array);
    }
    
    public static boolean leq(int[] u, int[] v) {
        int n = u.length;
        int m = v.length;
        if (m < n) return false;
        int j = 0;
        for (int i = 0; i < n; i++) {
            boolean ok = false;
            for (; j < m; j++) {
                if (u[i] < v[j]) return false;
                if (u[i] == v[j]) {
                    ok = true;
                    break;
                }
            }
            if (!ok) return false;
        }
        return true;
    }
    
    public boolean contains(int i) {
        return Arrays.binarySearch(array, i) >= 0;
    }
    
    public MockBasicSet setDifference(MockBasicSet set2) {
        List<Integer> lst = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            if (!set2.contains(array[i])) {
                lst.add(array[i]);
            }
        }
        int[] arr = new int[lst.size()];
        for (int i = 0; i < arr.length; i++) {
            arr[i] = lst.get(i);
        }
        return new MockBasicSet(arr);
    }
    
    public MockBasicSet intersection(MockBasicSet set2) {
        return intersection(this, set2);
    }
    
    public static MockBasicSet intersection(MockBasicSet set1, MockBasicSet set2) {
        List<Integer> lst = new ArrayList<>();
        for (int i = 0; i < set1.size; i++) {
            if (set2.contains(set1.array[i])) {
                lst.add(set1.array[i]);
            }
        }
        int[] arr = new int[lst.size()];
        for (int i = 0; i < arr.length; i++) {
            arr[i] = lst.get(i);
        }
        return new MockBasicSet(arr);
    }
    
    public MockBasicSet union(MockBasicSet set2) {
        return union(this, set2);
    }
    
    public static MockBasicSet union(MockBasicSet set1, MockBasicSet set2) {
        List<Integer> lst = new ArrayList<>();
        for (int i = 0; i < set1.size; i++) {
            lst.add(set1.array[i]);
        }
        for (int i = 0; i < set2.size; i++) {
            if (!lst.contains(set2.array[i])) {
                lst.add(set2.array[i]);
            }
        }
        int[] arr = new int[lst.size()];
        for (int i = 0; i < arr.length; i++) {
            arr[i] = lst.get(i);
        }
        return new MockBasicSet(arr);
    }
    
    public int size() {
        return size;
    }
    
    public int universeSize() {
        return size;
    }
    
    public int get(int index) {
        if (index >= 0 && index < size) {
            return array[index];
        }
        throw new IndexOutOfBoundsException("Index out of bounds: " + index);
    }
    
    public int[] toArray() {
        return array.clone();
    }
    
    @Override
    public String toString() {
        return Arrays.toString(array);
    }
}
