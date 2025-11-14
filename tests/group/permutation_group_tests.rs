use uacalc::group::PermutationGroup;
use uacalc::util::int_array::{IntArray, IntArrayTrait};
use uacalc::alg::op::Operation;

#[test]
fn test_permutation_group_new() {
    let generators = vec![
        IntArray::from_array(vec![1, 0, 2]).unwrap(),
        IntArray::from_array(vec![2, 1, 0]).unwrap(),
    ];
    let group = PermutationGroup::new("S3".to_string(), generators.clone());
    
    assert_eq!(group.name, "S3");
    assert_eq!(group.generators.len(), 2);
    assert_eq!(group.underlying_set_size, 3);
    assert!(group.identity.is_some());
    assert!(group.universe_list.is_none());
}

#[test]
fn test_permutation_group_new_with_universe() {
    let generators = vec![
        IntArray::from_array(vec![1, 0, 2]).unwrap(),
    ];
    let universe_list = vec![
        IntArray::from_array(vec![0, 1, 2]).unwrap(),
        IntArray::from_array(vec![2, 0, 1]).unwrap(),
    ];
    let group = PermutationGroup::new_with_universe("S3".to_string(), generators, universe_list.clone());
    
    assert_eq!(group.name, "S3");
    assert_eq!(group.generators.len(), 1);
    assert_eq!(group.underlying_set_size, 3);
    assert!(group.identity.is_some());
    assert!(group.universe_list.is_some());
    assert_eq!(group.universe_list.unwrap().len(), 2);
}

#[test]
fn test_permutation_group_new_safe() {
    let generators = vec![
        IntArray::from_array(vec![1, 0, 2]).unwrap(),
    ];
    let result = PermutationGroup::new_safe("S3".to_string(), generators);
    assert!(result.is_ok());
    
    let group = result.unwrap();
    assert_eq!(group.name, "S3");
    assert_eq!(group.underlying_set_size, 3);
}

#[test]
fn test_permutation_group_new_safe_empty_generators() {
    let result = PermutationGroup::new_safe("S3".to_string(), vec![]);
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("Generators cannot be empty"));
}

#[test]
fn test_permutation_group_new_safe_mismatched_sizes() {
    let generators = vec![
        IntArray::from_array(vec![1, 0, 2]).unwrap(),
        IntArray::from_array(vec![1, 0]).unwrap(), // Wrong size
    ];
    let result = PermutationGroup::new_safe("S3".to_string(), generators);
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("Generator 1 has size 2, expected 3"));
}

#[test]
fn test_permutation_group_prod() {
    let p0 = IntArray::from_array(vec![1, 0, 2]).unwrap();
    let p1 = IntArray::from_array(vec![2, 1, 0]).unwrap();
    let result = PermutationGroup::prod(p0, p1).unwrap();
    
    // p0 * p1: 0 -> p0[p1[0]] = p0[2] = 2, 1 -> p0[p1[1]] = p0[1] = 0, 2 -> p0[p1[2]] = p0[0] = 1
    assert_eq!(result.as_slice(), &[2, 0, 1]);
}

#[test]
fn test_permutation_group_inv() {
    let p = IntArray::from_array(vec![1, 0, 2]).unwrap();
    let inv = PermutationGroup::inv(p).unwrap();
    
    // Inverse of [1, 0, 2] is [1, 0, 2] (it's its own inverse)
    assert_eq!(inv.as_slice(), &[1, 0, 2]);
}

#[test]
fn test_permutation_group_inv_complex() {
    let p = IntArray::from_array(vec![2, 0, 1]).unwrap();
    let inv = PermutationGroup::inv(p).unwrap();
    
    // Inverse of [2, 0, 1] is [1, 2, 0]
    assert_eq!(inv.as_slice(), &[1, 2, 0]);
}

#[test]
fn test_permutation_group_id() {
    let id = PermutationGroup::id(3);
    assert_eq!(id.as_slice(), &[0, 1, 2]);
    
    let id5 = PermutationGroup::id(5);
    assert_eq!(id5.as_slice(), &[0, 1, 2, 3, 4]);
}

#[test]
fn test_permutation_group_make_prod_op() {
    let op = PermutationGroup::make_prod_op(3);
    assert_eq!(op.arity(), 2);
    assert_eq!(op.get_set_size(), 3);
    assert_eq!(op.symbol().name(), "prod");
}

#[test]
fn test_permutation_group_make_inv_op() {
    let op = PermutationGroup::make_inv_op(3);
    assert_eq!(op.arity(), 1);
    assert_eq!(op.get_set_size(), 3);
    assert_eq!(op.symbol().name(), "inv");
}

#[test]
fn test_permutation_group_make_id_op() {
    let op = PermutationGroup::make_id_op(3, 3);
    assert_eq!(op.arity(), 0);
    assert_eq!(op.get_set_size(), 3);
    assert_eq!(op.symbol().name(), "id");
}

#[test]
fn test_permutation_group_operations() {
    let generators = vec![
        IntArray::from_array(vec![1, 0, 2]).unwrap(),
    ];
    let group = PermutationGroup::new("S3".to_string(), generators);
    
    // Test getters
    assert_eq!(group.get_generators().len(), 1);
    assert_eq!(group.get_underlying_set_size(), 3);
    assert!(group.get_identity().is_some());
    assert!(group.get_universe_list().is_none());
    
    let identity = group.get_identity().unwrap();
    assert_eq!(identity.as_slice(), &[0, 1, 2]);
}

#[test]
fn test_permutation_group_equality() {
    let generators1 = vec![
        IntArray::from_array(vec![1, 0, 2]).unwrap(),
    ];
    let generators2 = vec![
        IntArray::from_array(vec![1, 0, 2]).unwrap(),
    ];
    
    let group1 = PermutationGroup::new("S3".to_string(), generators1);
    let group2 = PermutationGroup::new("S3".to_string(), generators2);
    
    assert_eq!(group1, group2);
}

#[test]
fn test_permutation_group_display() {
    let generators = vec![
        IntArray::from_array(vec![1, 0, 2]).unwrap(),
    ];
    let group = PermutationGroup::new("S3".to_string(), generators);
    
    let display_str = format!("{}", group);
    assert!(display_str.contains("PermutationGroup"));
    assert!(display_str.contains("S3"));
    assert!(display_str.contains("generators: 1"));
    assert!(display_str.contains("set_size: 3"));
}

#[test]
fn test_permutation_group_hash() {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    
    let generators = vec![
        IntArray::from_array(vec![1, 0, 2]).unwrap(),
    ];
    let group1 = PermutationGroup::new("S3".to_string(), generators.clone());
    let group2 = PermutationGroup::new("S3".to_string(), generators);
    
    let mut hasher1 = DefaultHasher::new();
    let mut hasher2 = DefaultHasher::new();
    
    group1.hash(&mut hasher1);
    group2.hash(&mut hasher2);
    
    assert_eq!(hasher1.finish(), hasher2.finish());
}

#[test]
fn test_permutation_group_clone() {
    let generators = vec![
        IntArray::from_array(vec![1, 0, 2]).unwrap(),
    ];
    let group1 = PermutationGroup::new("S3".to_string(), generators);
    let group2 = group1.clone();
    
    assert_eq!(group1, group2);
    assert_eq!(group1.name, group2.name);
    assert_eq!(group1.underlying_set_size, group2.underlying_set_size);
}

#[test]
fn test_permutation_group_operation_properties() {
    let prod_op = PermutationGroup::make_prod_op(3);
    let inv_op = PermutationGroup::make_inv_op(3);
    let id_op = PermutationGroup::make_id_op(3, 3);
    
    // Test operation properties
    assert!(prod_op.is_associative().unwrap());
    assert!(!prod_op.is_commutative().unwrap());
    assert!(!prod_op.is_idempotent().unwrap());
    assert!(prod_op.is_total().unwrap());
    
    assert!(!inv_op.is_associative().unwrap());
    assert!(!inv_op.is_commutative().unwrap());
    assert!(!inv_op.is_idempotent().unwrap());
    assert!(inv_op.is_total().unwrap());
    
    assert!(id_op.is_associative().unwrap());
    assert!(id_op.is_commutative().unwrap());
    assert!(id_op.is_idempotent().unwrap());
    assert!(id_op.is_total().unwrap());
}

#[test]
fn test_permutation_group_operation_evaluation() {
    let prod_op = PermutationGroup::make_prod_op(3);
    let inv_op = PermutationGroup::make_inv_op(3);
    let id_op = PermutationGroup::make_id_op(3, 3);
    
    // Test product operation - this is a simplified test since the operations
    // work with IntArray indices, not direct permutation values
    let result = prod_op.value_at(&[0, 0]).unwrap();
    assert_eq!(result, 0); // Basic test
    
    // Test inverse operation
    let result = inv_op.value_at(&[0]).unwrap();
    assert_eq!(result, 0); // Basic test
    
    // Test identity operation
    let result = id_op.value_at(&[]).unwrap();
    assert_eq!(result, 0); // First element of identity
}

#[test]
fn test_permutation_group_complex_permutations() {
    // Test with larger permutations
    let p1 = IntArray::from_array(vec![2, 0, 1, 3]).unwrap();
    let p2 = IntArray::from_array(vec![1, 3, 0, 2]).unwrap();
    
    let product = PermutationGroup::prod(p1.clone(), p2).unwrap();
    // p1 * p2: 0 -> p1[p2[0]] = p1[1] = 0, 1 -> p1[p2[1]] = p1[3] = 3, 2 -> p1[p2[2]] = p1[0] = 2, 3 -> p1[p2[3]] = p1[2] = 1
    assert_eq!(product.as_slice(), &[0, 3, 2, 1]);
    
    let inverse = PermutationGroup::inv(p1).unwrap();
    // Inverse of [2, 0, 1, 3] is [1, 2, 0, 3]
    assert_eq!(inverse.as_slice(), &[1, 2, 0, 3]);
}

#[test]
fn test_permutation_group_edge_cases() {
    // Test with single element
    let p = IntArray::from_array(vec![0]).unwrap();
    let inv = PermutationGroup::inv(p.clone()).unwrap();
    assert_eq!(inv.as_slice(), &[0]);
    
    let id = PermutationGroup::id(1);
    assert_eq!(id.as_slice(), &[0]);
    
    // Test product with single elements
    let product = PermutationGroup::prod(p.clone(), p).unwrap();
    assert_eq!(product.as_slice(), &[0]);
}
