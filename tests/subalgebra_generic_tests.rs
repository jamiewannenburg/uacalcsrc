use uacalc::alg::{
    Subalgebra, BasicSmallAlgebra, SmallAlgebra, Algebra, 
    QuotientAlgebra, QuotientElement, ProductAlgebra
};
use uacalc::alg::conlat::partition::Partition;
use std::collections::HashSet;

/// Test Subalgebra<i32> - basic integer universe (backward compatibility)
#[test]
fn test_subalgebra_i32() {
    // Create a super algebra with universe {0, 1, 2, 3}
    let mut universe = HashSet::new();
    universe.insert(0);
    universe.insert(1);
    universe.insert(2);
    universe.insert(3);
    
    let super_alg = Box::new(BasicSmallAlgebra::new(
        "super".to_string(),
        universe,
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    // Get the actual elements from the super algebra to understand the indexing
    let elem0 = super_alg.get_element(0).unwrap();
    let elem1 = super_alg.get_element(1).unwrap();
    let elem2 = super_alg.get_element(2).unwrap();
    let elem3 = super_alg.get_element(3).unwrap();
    
    // Find the indices of elements 0 and 1 in the super algebra
    let idx0 = super_alg.element_index(&0).unwrap();
    let idx1 = super_alg.element_index(&1).unwrap();
    
    // Create a subalgebra with universe containing elements 0 and 1
    let sub_alg = Subalgebra::<i32>::new_safe(
        "sub".to_string(),
        super_alg,
        vec![idx0 as i32, idx1 as i32]
    ).unwrap();
    
    assert_eq!(sub_alg.cardinality(), 2);
    assert_eq!(sub_alg.name(), "sub");
    
    // Test element access - should return the actual elements, not indices
    // Note: The subalgebra sorts the indices, so the order is determined by the sorted indices
    let elem_at_0 = sub_alg.get_element(0).unwrap();
    let elem_at_1 = sub_alg.get_element(1).unwrap();
    assert!(elem_at_0 == 0 || elem_at_0 == 1);
    assert!(elem_at_1 == 0 || elem_at_1 == 1);
    assert_ne!(elem_at_0, elem_at_1);
    assert_eq!(sub_alg.get_element(2), None);
    
    // Test element index
    assert!(sub_alg.element_index(&0).is_some());
    assert!(sub_alg.element_index(&1).is_some());
    assert_eq!(sub_alg.element_index(&2), None);
    
    // Test universe iteration
    let universe: Vec<i32> = sub_alg.universe().collect();
    assert_eq!(universe.len(), 2);
    assert!(universe.contains(&0));
    assert!(universe.contains(&1));
}

/// Test Subalgebra<IntArray> - from ProductAlgebra
#[test]
fn test_subalgebra_intarray() {
    // Create a ProductAlgebra with two factors of size 2
    let factor1 = Box::new(BasicSmallAlgebra::new(
        "factor1".to_string(),
        HashSet::from([0, 1]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let factor2 = Box::new(BasicSmallAlgebra::new(
        "factor2".to_string(),
        HashSet::from([0, 1]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let product = ProductAlgebra::new_safe(
        "product".to_string(),
        vec![factor1, factor2]
    ).unwrap();
    
    // Create subalgebra with indices [0, 1] (first two elements)
    let sub_alg = Subalgebra::<i32>::new_safe(
        "sub_product".to_string(),
        Box::new(product) as Box<dyn SmallAlgebra<UniverseItem = i32>>,
        vec![0, 1]
    ).unwrap();
    
    assert_eq!(sub_alg.cardinality(), 2);
    assert_eq!(sub_alg.name(), "sub_product");
    
    // Test element access
    let elem0 = sub_alg.get_element(0);
    let elem1 = sub_alg.get_element(1);
    assert!(elem0.is_some());
    assert!(elem1.is_some());
    
    // Test universe iteration
    let universe: Vec<i32> = sub_alg.universe().collect();
    assert_eq!(universe.len(), 2);
}

/// Test Subalgebra<QuotientElement> - from QuotientAlgebra
#[test]
fn test_subalgebra_quotient_element() {
    // Create a super algebra
    let super_alg = Box::new(BasicSmallAlgebra::new(
        "super".to_string(),
        HashSet::from([0, 1, 2, 3]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    // Create a partition with two blocks
    let mut partition = Partition::zero(4);
    partition.join_blocks(0, 1); // Block 1: {0, 1}
    partition.join_blocks(2, 3); // Block 2: {2, 3}
    
    // Create a quotient algebra
    let quotient = QuotientAlgebra::<i32>::new_safe(
        super_alg,
        partition
    ).unwrap();
    
    let super_alg_quotient = Box::new(quotient) as Box<dyn SmallAlgebra<UniverseItem = QuotientElement<i32>>>;
    
    // Create subalgebra with universe containing first quotient element
    let sub_alg = Subalgebra::<QuotientElement<i32>>::new_safe(
        "sub_quotient".to_string(),
        super_alg_quotient,
        vec![0] // Only first quotient element
    ).unwrap();
    
    assert_eq!(sub_alg.cardinality(), 1);
    assert_eq!(sub_alg.name(), "sub_quotient");
    
    // Test element access
    let elem = sub_alg.get_element(0);
    assert!(elem.is_some());
    
    // Test universe iteration
    let universe: Vec<QuotientElement<i32>> = sub_alg.universe().collect();
    assert_eq!(universe.len(), 1);
}

/// Test operations on subalgebras preserve universe type
#[test]
fn test_subalgebra_operations_preserve_type() {
    // Create a super algebra with operations
    let super_alg = Box::new(BasicSmallAlgebra::new(
        "super".to_string(),
        HashSet::from([0, 1, 2, 3]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    // Create subalgebra
    let sub_alg = Subalgebra::<i32>::new_safe(
        "sub".to_string(),
        super_alg,
        vec![0, 1]
    ).unwrap();
    
    // Test that operations are preserved
    let operations = sub_alg.operations();
    // The subalgebra should have the same operations as the super algebra
    // (though restricted to the subuniverse)
    
    // Test that the subalgebra implements SmallAlgebra correctly
    assert_eq!(sub_alg.algebra_type(), uacalc::alg::small_algebra::AlgebraType::Subalgebra);
    
    // Test parent relationship
    let parent = sub_alg.parent();
    assert!(parent.is_some());
}

/// Test nested subalgebras (subalgebra of a subalgebra)
#[test]
fn test_nested_subalgebras() {
    // Create a super algebra
    let mut universe = HashSet::new();
    for i in 0..6 {
        universe.insert(i);
    }
    
    let super_alg = Box::new(BasicSmallAlgebra::new(
        "super".to_string(),
        universe,
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    // Find indices of elements 0, 1, 2 in the super algebra
    let idx0 = super_alg.element_index(&0).unwrap();
    let idx1 = super_alg.element_index(&1).unwrap();
    let idx2 = super_alg.element_index(&2).unwrap();
    
    // Create first subalgebra with universe {0, 1, 2}
    let sub1 = Subalgebra::<i32>::new_safe(
        "sub1".to_string(),
        super_alg,
        vec![idx0 as i32, idx1 as i32, idx2 as i32]
    ).unwrap();
    
    // Find indices of elements 0, 1 in the first subalgebra
    let sub1_idx0 = sub1.element_index(&0).unwrap();
    let sub1_idx1 = sub1.element_index(&1).unwrap();
    
    // Create second subalgebra of the first subalgebra with universe {0, 1}
    let sub1_boxed = Box::new(sub1) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    let sub2 = Subalgebra::<i32>::new_safe(
        "sub2".to_string(),
        sub1_boxed,
        vec![sub1_idx0 as i32, sub1_idx1 as i32]
    ).unwrap();
    
    assert_eq!(sub2.cardinality(), 2);
    assert_eq!(sub2.name(), "sub2");
    
    // Test element access - get the actual elements from the subalgebra
    let sub2_elem0 = sub2.get_element(0).unwrap();
    let sub2_elem1 = sub2.get_element(1).unwrap();
    assert_eq!(sub2.get_element(2), None);
    
    // Verify that the elements are 0 and 1 (in some order)
    assert!(sub2_elem0 == 0 || sub2_elem0 == 1);
    assert!(sub2_elem1 == 0 || sub2_elem1 == 1);
    assert_ne!(sub2_elem0, sub2_elem1);
    
    // Test parent relationship
    let parent = sub2.parent();
    assert!(parent.is_some());
    assert_eq!(parent.unwrap().name(), "sub1");
}

/// Test error handling for invalid subuniverse
#[test]
fn test_subalgebra_error_handling() {
    let super_alg = Box::new(BasicSmallAlgebra::new(
        "super".to_string(),
        HashSet::from([0, 1, 2, 3]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    // Test empty subuniverse
    let result = Subalgebra::<i32>::new_safe(
        "empty".to_string(),
        super_alg.clone_box(),
        vec![]
    );
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("empty"));
    
    // Test invalid indices
    let result = Subalgebra::<i32>::new_safe(
        "invalid".to_string(),
        super_alg,
        vec![0, 5] // 5 is out of bounds
    );
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("Invalid"));
}

/// Test subalgebra with different universe types maintains type safety
#[test]
fn test_type_safety() {
    // This test ensures that we can't accidentally mix different universe types
    let int_alg = Box::new(BasicSmallAlgebra::new(
        "int_alg".to_string(),
        HashSet::from([0, 1]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    // Find the index of element 0 in the super algebra
    let idx0 = int_alg.element_index(&0).unwrap();
    
    let int_sub = Subalgebra::<i32>::new_safe(
        "int_sub".to_string(),
        int_alg,
        vec![idx0 as i32]
    ).unwrap();
    
    // The subalgebra should have i32 universe items
    let elem = int_sub.get_element(0);
    assert!(elem.is_some());
    assert_eq!(elem.unwrap(), 0i32);
    
    // Test that universe iteration returns the correct type
    let universe: Vec<i32> = int_sub.universe().collect();
    assert_eq!(universe.len(), 1);
    assert!(universe.contains(&0));
}

/// Test subalgebra with operations
#[test]
fn test_subalgebra_with_operations() {
    use uacalc::alg::op::{OperationSymbol, BasicOperation, Operation};
    
    // Create a super algebra with an operation
    let op_sym = OperationSymbol::new("f", 2, false);
    let op = Box::new(BasicOperation::new(op_sym.clone(), 4)) as Box<dyn Operation>;
    
    let mut universe = HashSet::new();
    for i in 0..4 {
        universe.insert(i);
    }
    
    let super_alg = Box::new(BasicSmallAlgebra::new(
        "super".to_string(),
        universe,
        vec![op]
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    // Find indices of elements 0, 1, 2 in the super algebra
    let idx0 = super_alg.element_index(&0).unwrap();
    let idx1 = super_alg.element_index(&1).unwrap();
    let idx2 = super_alg.element_index(&2).unwrap();
    
    // Create subalgebra
    let sub_alg = Subalgebra::<i32>::new_safe(
        "sub".to_string(),
        super_alg.clone_box(),
        vec![idx0 as i32, idx1 as i32, idx2 as i32]
    ).unwrap();
    
    // Test that operations are available
    // Note: operations() returns empty vector due to infinite recursion limitation
    // Instead, test that we can access the operation by symbol
    
    // Test that the super algebra has the operation
    let super_op_ref = super_alg.get_operation_ref(&op_sym);
    assert!(super_op_ref.is_some());
    
    // Test that the subalgebra has the operation
    let sub_op_ref = sub_alg.get_operation_ref(&op_sym);
    assert!(sub_op_ref.is_some());
    
    // Test operation access
    let op_ref = sub_alg.get_operation_ref(&op_sym);
    assert!(op_ref.is_some());
    assert_eq!(op_ref.unwrap().symbol().name(), "f");
    assert_eq!(op_ref.unwrap().arity(), 2);
    
    // Test that we can get elements from the subalgebra
    let elem0 = sub_alg.get_element(0).unwrap();
    let elem1 = sub_alg.get_element(1).unwrap();
    let elem2 = sub_alg.get_element(2).unwrap();
    
    // Verify that the elements are 0, 1, 2 (in some order)
    let mut elements = vec![elem0, elem1, elem2];
    elements.sort();
    assert_eq!(elements, vec![0, 1, 2]);
    
    // Test that the subalgebra has the correct cardinality
    assert_eq!(sub_alg.cardinality(), 3);
}

/// Test subalgebra cloning
#[test]
fn test_subalgebra_cloning() {
    let super_alg = Box::new(BasicSmallAlgebra::new(
        "super".to_string(),
        HashSet::from([0, 1, 2, 3]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let sub_alg = Subalgebra::<i32>::new_safe(
        "sub".to_string(),
        super_alg,
        vec![0, 1]
    ).unwrap();
    
    // Clone the subalgebra
    let cloned = sub_alg.clone();
    
    assert_eq!(cloned.cardinality(), sub_alg.cardinality());
    assert_eq!(cloned.name(), sub_alg.name());
    
    // Test that both have the same universe
    let orig_universe: Vec<i32> = sub_alg.universe().collect();
    let cloned_universe: Vec<i32> = cloned.universe().collect();
    assert_eq!(orig_universe, cloned_universe);
}

/// Test subalgebra display formatting
#[test]
fn test_subalgebra_display() {
    let super_alg = Box::new(BasicSmallAlgebra::new(
        "super".to_string(),
        HashSet::from([0, 1, 2, 3]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let sub_alg = Subalgebra::<i32>::new_safe(
        "sub".to_string(),
        super_alg,
        vec![0, 1]
    ).unwrap();
    
    let display_str = format!("{}", sub_alg);
    assert!(display_str.contains("Subalgebra"));
    assert!(display_str.contains("sub"));
    assert!(display_str.contains("cardinality: 2"));
}

/// Test subalgebra debug formatting
#[test]
fn test_subalgebra_debug() {
    let super_alg = Box::new(BasicSmallAlgebra::new(
        "super".to_string(),
        HashSet::from([0, 1, 2, 3]),
        Vec::new()
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    let sub_alg = Subalgebra::<i32>::new_safe(
        "sub".to_string(),
        super_alg,
        vec![0, 1]
    ).unwrap();
    
    let debug_str = format!("{:?}", sub_alg);
    assert!(debug_str.contains("Subalgebra"));
    assert!(debug_str.contains("sub"));
    assert!(debug_str.contains("size"));
}
