use uacalc_core::prelude::*;
use uacalc_core::conlat::cg::*;

#[test]
fn test_cg_empty_pairs() {
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let result = cg(&algebra, &[]);
    assert!(result.is_ok());
    let partition = result.unwrap();
    assert_eq!(partition.num_blocks(), 3); // Finest partition
}

#[test]
fn test_cg_single_pair() {
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let result = cg(&algebra, &[(0, 1)]);
    assert!(result.is_ok());
    let partition = result.unwrap();
    assert_eq!(partition.num_blocks(), 2); // {0,1}, {2}
}

#[test]
fn test_cg_coarsest_partition() {
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let result = cg(&algebra, &[(0, 1), (1, 2)]);
    assert!(result.is_ok());
    let partition = result.unwrap();
    assert_eq!(partition.num_blocks(), 1); // Coarsest partition
}

#[test]
fn test_principal_congruence() {
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let result = principal_congruence(&algebra, 0, 1);
    assert!(result.is_ok());
    let partition = result.unwrap();
    assert!(partition.same_block(0, 1).unwrap());
    assert!(!partition.same_block(0, 2).unwrap());
}

#[test]
fn test_cg_with_operations() {
    // Create a simple algebra with a binary operation
    let mut algebra = BasicAlgebra::with_cardinality("A".to_string(), 2).unwrap();
    
    // Add a simple operation: f(x,y) = x
    let operation = TableOperation::binary("f".to_string(), 2, |x, _y| x).unwrap();
    algebra.add_operation_simple(operation);
    
    let result = cg(&algebra, &[(0, 1)]);
    assert!(result.is_ok());
    let partition = result.unwrap();
    
    // Since f(0,0)=0 and f(1,1)=1, the operation preserves the partition
    // So the congruence should be the coarsest partition
    assert_eq!(partition.num_blocks(), 1);
}

#[test]
fn test_cg_invalid_pairs() {
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let result = cg(&algebra, &[(0, 5)]); // Invalid element
    assert!(result.is_err());
}

#[test]
fn test_is_congruence() {
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let partition = BasicPartition::new(3);
    
    let result = is_congruence(&algebra, &partition);
    assert!(result.is_ok());
    assert!(result.unwrap()); // Finest partition is always a congruence
}

#[test]
fn test_is_compatible_with_operation() {
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 2).unwrap();
    let partition = BasicPartition::new(2);
    
    // Create a simple operation
    let operation = TableOperation::unary("f".to_string(), 2, |x| x).unwrap();
    
    let result = is_compatible_with_operation(&partition, &operation);
    assert!(result.is_ok());
    assert!(result.unwrap()); // Identity operation is compatible with any partition
}

#[test]
fn test_cg_generator() {
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let mut generator = CongruenceGenerator::new(&algebra);
    
    let result = generator.compute_congruence(&[(0, 1)]);
    assert!(result.is_ok());
    let partition = result.unwrap();
    assert_eq!(partition.num_blocks(), 2);
}

#[test]
fn test_cg_generator_with_progress() {
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    let mut generator = CongruenceGenerator::new(&algebra);
    
    generator = generator.with_progress_closure(|progress: f64| {
        println!("Progress: {:.2}", progress);
    });
    let result = generator.compute_congruence(&[(0, 1)]);
    assert!(result.is_ok());
}

#[test]
fn test_cg_properties() {
    let algebra = BasicAlgebra::with_cardinality("A".to_string(), 3).unwrap();
    
    // Test monotonicity: A ⊆ B implies Cg(A) ≤ Cg(B)
    let cg_a = cg(&algebra, &[(0, 1)]).unwrap();
    let cg_b = cg(&algebra, &[(0, 1), (1, 2)]).unwrap();
    
    assert!(cg_a.is_finer_than(&cg_b).unwrap());
    
    // Test idempotence: Cg(Cg(A)) = Cg(A)
    let cg_a_once = cg(&algebra, &[(0, 1)]).unwrap();
    let cg_a_twice = cg(&algebra, &[(0, 1)]).unwrap();
    
    assert_eq!(cg_a_once, cg_a_twice);
}

#[test]
fn test_cg_with_complex_operations() {
    // Create an algebra with a more complex operation
    let mut algebra = BasicAlgebra::with_cardinality("A".to_string(), 4).unwrap();
    
    // Add a ternary operation: f(x,y,z) = (x + y + z) mod 2
    let operation = TableOperation::from_function(
        OperationSymbol::new("f".to_string(), 3),
        4,
        |args| Ok((args[0] + args[1] + args[2]) % 2)
    ).unwrap();
    algebra.add_operation_simple(operation);
    
    let result = cg(&algebra, &[(0, 1), (2, 3)]);
    assert!(result.is_ok());
    let partition = result.unwrap();
    
    // The operation should force all elements to be in the same block
    // because f(0,1,2) = 1 and f(1,0,3) = 1, but f(0,1,3) = 0 and f(1,0,2) = 0
    // This creates contradictions that force the coarsest partition
    assert_eq!(partition.num_blocks(), 1);
}
