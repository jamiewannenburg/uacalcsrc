package group;

import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;

/**
 * Demo class for PermutationGroupWrapper to test basic functionality.
 */
public class PermutationGroupWrapperDemo {
    
    public static void main(String[] args) {
        System.out.println("PermutationGroupWrapper Demo");
        System.out.println("============================");
        
        try {
            // Test basic creation
            List<List<Integer>> generators = Arrays.asList(
                Arrays.asList(1, 2, 0),
                Arrays.asList(2, 0, 1)
            );
            
            PermutationGroupWrapper pg = new PermutationGroupWrapper("TestGroup", generators);
            System.out.println("Created group: " + pg.getName());
            System.out.println("Generators: " + pg.getGenerators());
            System.out.println("Set size: " + pg.getUnderlyingSetSize());
            System.out.println("Identity: " + pg.getIdentity());
            
            // Test static methods
            List<Integer> p1 = Arrays.asList(1, 2, 0);
            List<Integer> p2 = Arrays.asList(2, 0, 1);
            List<Integer> result = PermutationGroupWrapper.prod(p1, p2);
            System.out.println("Product [1,2,0] * [2,0,1] = " + result);
            
            List<Integer> inv = PermutationGroupWrapper.inv(p1);
            System.out.println("Inverse of [1,2,0] = " + inv);
            
            List<Integer> id = PermutationGroupWrapper.id(3);
            System.out.println("Identity of size 3 = " + id);
            
            // Test safe creation
            PermutationGroupWrapper pgSafe = PermutationGroupWrapper.newSafe("SafeGroup", generators);
            System.out.println("Safe creation successful: " + pgSafe.getName());
            
            System.out.println("\nAll tests passed!");
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
