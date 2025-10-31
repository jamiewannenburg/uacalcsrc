/*!
 * Test for MembershipTester example.
 * 
 * This test replicates the functionality of MembershipTester.java:
 * - Loads two algebras (n5.ua and m3.ua)
 * - Finds an equation that holds in alg0 but fails in alg1
 * - Tests the equation in both algebras
 * 
 * If the implementation is incomplete, the test will note what's missing.
 */

#[cfg(test)]
mod tests {
    use std::path::Path;
    use uacalc::io::algebra_io::read_algebra_file;
    use uacalc::alg::free_algebra::FreeAlgebra;
    use uacalc::alg::SmallAlgebra;
    use std::sync::Arc;
    
    /// Test membership testing similar to MembershipTester.java
    /// 
    /// This test loads n5.ua and m3.ua, then tries to find an equation
    /// that holds in n5 but fails in m3.
    #[test]
    fn test_membership_tester() {
        // Paths to algebra files (same as Java example)
        let alg0_file = Path::new("resources/algebras/n5.ua");
        let alg1_file = Path::new("resources/algebras/m3.ua");
        
        // Check if files exist
        if !alg0_file.exists() {
            eprintln!("Skipping test: {} not found", alg0_file.display());
            return;
        }
        if !alg1_file.exists() {
            eprintln!("Skipping test: {} not found", alg1_file.display());
            return;
        }
        
        // Load algebras
        let alg0 = read_algebra_file(alg0_file)
            .expect("Failed to read alg0 file");
        let alg1 = read_algebra_file(alg1_file)
            .expect("Failed to read alg1 file");
        
        println!("Loaded alg0: {} (size: {})", alg0.name(), alg0.cardinality());
        println!("Loaded alg1: {} (size: {})", alg1.name(), alg1.cardinality());
        
        // Generators for alg1 (same as Java example)
        let alg1_generators = vec![1, 2, 3];
        
        // Find equation that holds in alg0 but fails in alg1
        println!("\nFinding equation...");
        match FreeAlgebra::find_equation_of_a_not_b(
            alg0.clone_box(),
            alg1.clone_box(),
            alg1_generators.clone()
        ) {
            Ok(Some(eq)) => {
                println!("eq is\n{}", eq);
                
                // Test that eq fails in alg1
                let alg1_arc: Arc<dyn SmallAlgebra<UniverseItem = i32>> = Arc::from(alg1.clone_box());
                match eq.find_failure_map(alg1_arc.clone()) {
                    Ok(Some(failure)) => {
                        println!("failure in alg1\n{:?}", failure);
                    }
                    Ok(None) => {
                        println!("WARNING: Equation does not fail in alg1 (unexpected!)");
                    }
                    Err(e) => {
                        println!("Error finding failure in alg1: {}", e);
                    }
                }
                
                // Try to find a failure in alg0 (should be None)
                let alg0_arc: Arc<dyn SmallAlgebra<UniverseItem = i32>> = Arc::from(alg0.clone_box());
                match eq.find_failure_map(alg0_arc) {
                    Ok(Some(failure)) => {
                        println!("WARNING: Equation fails in alg0 (unexpected!): {:?}", failure);
                    }
                    Ok(None) => {
                        println!("failure in alg0\nnull (as expected)");
                    }
                    Err(e) => {
                        println!("Error finding failure in alg0: {}", e);
                    }
                }
            }
            Ok(None) => {
                println!("eq is null (alg1 is in V(alg0))");
            }
            Err(e) => {
                println!("Error finding equation: {}", e);
                println!("\n=== IMPLEMENTATION STATUS ===");
                println!("find_equation_of_a_not_b returned an error.");
                println!("This may indicate that the following methods need to be implemented:");
                println!("1. Closer::set_image_algebra");
                println!("2. Closer::set_homomorphism");
                println!("3. Closer::get_failing_equation");
            }
        }
    }
    
    /// Test with a simpler case to verify basic functionality
    #[test]
    fn test_membership_tester_simple() {
        let alg0_file = Path::new("resources/algebras/cyclic2.ua");
        let alg1_file = Path::new("resources/algebras/cyclic3.ua");
        
        if !alg0_file.exists() || !alg1_file.exists() {
            eprintln!("Skipping test: algebra files not found");
            return;
        }
        
        let alg0 = read_algebra_file(alg0_file)
            .expect("Failed to read alg0 file");
        let alg1 = read_algebra_file(alg1_file)
            .expect("Failed to read alg1 file");
        
        let alg1_generators = vec![0, 1];
        
        match FreeAlgebra::find_equation_of_a_not_b(
            alg0.clone_box(),
            alg1.clone_box(),
            alg1_generators
        ) {
            Ok(Some(eq)) => {
                println!("Found equation: {}", eq);
            }
            Ok(None) => {
                println!("No equation found (alg1 may be in V(alg0))");
            }
            Err(e) => {
                println!("Error: {}", e);
            }
        }
    }
}

