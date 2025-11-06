use uacalc::alg::{Algebra, SmallAlgebra, BasicAlgebra, MaltsevProductDecomposition, Partition};
use std::collections::HashSet;

#[cfg(test)]
mod maltsev_product_decomposition_tests {
    use super::*;

    #[test]
    fn test_basic_creation() {
        // Create a simple algebra with 4 elements
        let universe: HashSet<i32> = (0..4).collect();
        let operations = Vec::new();
        let algebra = Box::new(BasicAlgebra::new(
            "TestAlgebra".to_string(),
            universe,
            operations,
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Create a congruence with blocks {0,1}, {2,3}
        let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
        
        // Create decomposition
        let decomp = MaltsevProductDecomposition::new_safe(algebra, congruence).unwrap();
        
        // Verify properties
        assert_eq!(decomp.cardinality(), 4);
        assert_eq!(decomp.get_congruence().number_of_blocks(), 2);
        assert_eq!(decomp.get_block_algebras().len(), 2); // Two blocks with >1 element
        assert_eq!(decomp.get_quotient_algebra().cardinality(), 2); // Two equivalence classes
    }

    #[test]
    fn test_single_block_congruence() {
        // Create algebra with 3 elements
        let universe: HashSet<i32> = (0..3).collect();
        let operations = Vec::new();
        let algebra = Box::new(BasicAlgebra::new(
            "TestAlgebra".to_string(),
            universe,
            operations,
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Create a congruence with one block {0,1,2}
        let congruence = Partition::new(vec![-3, 0, 0]).unwrap();
        
        // Create decomposition
        let decomp = MaltsevProductDecomposition::new_safe(algebra, congruence).unwrap();
        
        // Verify properties
        assert_eq!(decomp.cardinality(), 3);
        assert_eq!(decomp.get_congruence().number_of_blocks(), 1);
        assert_eq!(decomp.get_block_algebras().len(), 1); // One block with >1 element
        assert_eq!(decomp.get_quotient_algebra().cardinality(), 1); // One equivalence class
    }

    #[test]
    fn test_zero_congruence() {
        // Create algebra with 3 elements
        let universe: HashSet<i32> = (0..3).collect();
        let operations = Vec::new();
        let algebra = Box::new(BasicAlgebra::new(
            "TestAlgebra".to_string(),
            universe,
            operations,
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Create zero congruence (all singleton blocks)
        let congruence = Partition::new(vec![-1, -1, -1]).unwrap();
        
        // Create decomposition
        let decomp = MaltsevProductDecomposition::new_safe(algebra, congruence).unwrap();
        
        // Verify properties
        assert_eq!(decomp.cardinality(), 3);
        assert_eq!(decomp.get_congruence().number_of_blocks(), 3);
        assert_eq!(decomp.get_block_algebras().len(), 0); // No blocks with >1 element
        assert_eq!(decomp.get_quotient_algebra().cardinality(), 3); // Three equivalence classes
    }

    #[test]
    fn test_get_congruence() {
        // Create algebra and congruence
        let universe: HashSet<i32> = (0..4).collect();
        let operations = Vec::new();
        let algebra = Box::new(BasicAlgebra::new(
            "TestAlgebra".to_string(),
            universe,
            operations,
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
        let orig_blocks = congruence.number_of_blocks();
        
        // Create decomposition
        let decomp = MaltsevProductDecomposition::new_safe(algebra, congruence).unwrap();
        
        // Get congruence and verify
        let returned_cong = decomp.get_congruence();
        assert_eq!(returned_cong.number_of_blocks(), orig_blocks);
        assert_eq!(returned_cong.universe_size(), 4);
    }

    #[test]
    fn test_get_algebra() {
        // Create algebra
        let universe: HashSet<i32> = (0..5).collect();
        let operations = Vec::new();
        let algebra = Box::new(BasicAlgebra::new(
            "TestAlgebra".to_string(),
            universe,
            operations,
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let congruence = Partition::new(vec![-2, 0, -3, 2, 2]).unwrap();
        
        // Create decomposition
        let decomp = MaltsevProductDecomposition::new_safe(algebra, congruence).unwrap();
        
        // Get algebra and verify
        let returned_alg = decomp.get_algebra();
        assert_eq!(returned_alg.cardinality(), 5);
        assert_eq!(returned_alg.name(), "TestAlgebra");
    }

    #[test]
    fn test_invalid_congruence_size() {
        // Create algebra with 4 elements
        let universe: HashSet<i32> = (0..4).collect();
        let operations = Vec::new();
        let algebra = Box::new(BasicAlgebra::new(
            "TestAlgebra".to_string(),
            universe,
            operations,
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Create congruence with wrong size (5 elements)
        let congruence = Partition::new(vec![-2, 0, -2, 2, -1]).unwrap();
        
        // Should fail with size mismatch error
        let result = MaltsevProductDecomposition::new_safe(algebra, congruence);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("does not match"));
    }

    #[test]
    fn test_display() {
        // Create algebra and decomposition
        let universe: HashSet<i32> = (0..4).collect();
        let operations = Vec::new();
        let algebra = Box::new(BasicAlgebra::new(
            "TestAlgebra".to_string(),
            universe,
            operations,
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
        let decomp = MaltsevProductDecomposition::new_safe(algebra, congruence).unwrap();
        
        // Test display
        let display_str = format!("{}", decomp);
        assert!(display_str.contains("MaltsevProductDecomposition"));
        assert!(display_str.contains("TestAlgebra"));
    }

    #[test]
    fn test_block_algebras_cardinalities() {
        // Create algebra with 6 elements
        let universe: HashSet<i32> = (0..6).collect();
        let operations = Vec::new();
        let algebra = Box::new(BasicAlgebra::new(
            "TestAlgebra".to_string(),
            universe,
            operations,
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Create congruence with blocks {0,1,2}, {3,4}, {5}
        let congruence = Partition::new(vec![-3, 0, 0, -2, 3, -1]).unwrap();
        
        // Create decomposition
        let decomp = MaltsevProductDecomposition::new_safe(algebra, congruence).unwrap();
        
        // Verify block algebras
        let block_algs = decomp.get_block_algebras();
        assert_eq!(block_algs.len(), 2); // Two blocks with >1 element
        
        // Get cardinalities of block algebras
        let mut cardinalities: Vec<i32> = block_algs.iter()
            .map(|alg| alg.cardinality())
            .collect();
        cardinalities.sort();
        
        assert_eq!(cardinalities, vec![2, 3]); // Blocks of size 2 and 3
    }

    #[test]
    fn test_set_methods() {
        // Create initial algebra and congruence
        let universe: HashSet<i32> = (0..4).collect();
        let operations = Vec::new();
        let algebra = Box::new(BasicAlgebra::new(
            "TestAlgebra".to_string(),
            universe.clone(),
            operations,
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
        
        // Create decomposition
        let mut decomp = MaltsevProductDecomposition::new_safe(algebra, congruence).unwrap();
        
        // Test set_congruence
        let new_congruence = Partition::new(vec![-4, 0, 0, 0]).unwrap();
        decomp.set_congruence(new_congruence);
        assert_eq!(decomp.get_congruence().number_of_blocks(), 1);
        
        // Test set_algebra
        let new_algebra = Box::new(BasicAlgebra::new(
            "NewAlgebra".to_string(),
            universe,
            Vec::new(),
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        decomp.set_algebra(new_algebra);
        assert_eq!(decomp.get_algebra().name(), "NewAlgebra");
    }
}
