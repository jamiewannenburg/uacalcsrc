use std::sync::{Arc, Mutex};
use uacalc_core::algebra::{Algebra, BasicAlgebra, SmallAlgebra};
use uacalc_core::operation::TableOperation;
use uacalc_core::partition::{BasicPartition, Partition};
use uacalc_core::quotient::QuotientAlgebra;
use uacalc_core::UACalcResult;

/// Create a simple Z4 algebra for testing
fn create_z4() -> UACalcResult<BasicAlgebra> {
    let mut z4 = BasicAlgebra::with_cardinality("Z4".to_string(), 4)?;

    // Add addition modulo 4
    let add_op = Arc::new(Mutex::new(TableOperation::binary(
        "add".to_string(),
        4,
        |a, b| (a + b) % 4,
    )?));
    z4.add_operation("add".to_string(), add_op)?;

    // Add multiplication modulo 4
    let mul_op = Arc::new(Mutex::new(TableOperation::binary(
        "mul".to_string(),
        4,
        |a, b| (a * b) % 4,
    )?));
    z4.add_operation("mul".to_string(), mul_op)?;

    Ok(z4)
}

/// Create a Z3 algebra for testing
fn create_z3() -> UACalcResult<BasicAlgebra> {
    let mut z3 = BasicAlgebra::with_cardinality("Z3".to_string(), 3)?;

    // Add addition modulo 3
    let add_op = Arc::new(Mutex::new(TableOperation::binary(
        "add".to_string(),
        3,
        |a, b| (a + b) % 3,
    )?));
    z3.add_operation("add".to_string(), add_op)?;

    Ok(z3)
}

#[test]
fn test_quotient_algebra_basic_creation() -> Result<(), Box<dyn std::error::Error>> {
    // Create Z4 algebra
    let z4 = create_z4()?;
    let z4_arc = Arc::new(Mutex::new(z4));

    // Create a congruence: {0, 2} and {1, 3} (even/odd)
    let congruence = BasicPartition::from_blocks(4, vec![vec![0, 2], vec![1, 3]])?;

    // Create quotient algebra
    let quotient = QuotientAlgebra::new("Z2".to_string(), z4_arc, congruence)?;

    // Test basic properties
    assert_eq!(quotient.cardinality(), 2);
    assert_eq!(quotient.universe(), &[0, 1]);
    assert_eq!(quotient.operations().len(), 2); // add and mul
    assert_eq!(quotient.name(), "Z2");

    Ok(())
}

#[test]
fn test_quotient_operation_evaluation() -> Result<(), Box<dyn std::error::Error>> {
    // Create Z4 algebra
    let z4 = create_z4()?;
    let z4_arc = Arc::new(Mutex::new(z4));

    // Create congruence: {0, 2} and {1, 3}
    let congruence = BasicPartition::from_blocks(4, vec![vec![0, 2], vec![1, 3]])?;

    // Create quotient algebra
    let quotient = QuotientAlgebra::new("Z2".to_string(), z4_arc, congruence)?;

    // Test addition operation
    let add_quotient = quotient.operation_arc_by_symbol("add")?;
    let add_guard = add_quotient.lock().unwrap();

    // In the quotient: 0 represents {0,2}, 1 represents {1,3}
    // 0 + 0 = 0 (even + even = even)
    assert_eq!(add_guard.value(&[0, 0])?, 0);
    // 0 + 1 = 1 (even + odd = odd)
    assert_eq!(add_guard.value(&[0, 1])?, 1);
    // 1 + 0 = 1 (odd + even = odd)
    assert_eq!(add_guard.value(&[1, 0])?, 1);
    // 1 + 1 = 0 (odd + odd = even)
    assert_eq!(add_guard.value(&[1, 1])?, 0);

    drop(add_guard);

    // Test multiplication operation
    let mul_quotient = quotient.operation_arc_by_symbol("mul")?;
    let mul_guard = mul_quotient.lock().unwrap();

    // 0 * 0 = 0 (even * even = even)
    assert_eq!(mul_guard.value(&[0, 0])?, 0);
    // 0 * 1 = 0 (even * odd = even)
    assert_eq!(mul_guard.value(&[0, 1])?, 0);
    // 1 * 0 = 0 (odd * even = even)
    assert_eq!(mul_guard.value(&[1, 0])?, 0);
    // 1 * 1 = 1 (odd * odd = odd)
    assert_eq!(mul_guard.value(&[1, 1])?, 1);

    Ok(())
}

#[test]
fn test_quotient_canonical_homomorphism() -> Result<(), Box<dyn std::error::Error>> {
    // Create Z4 algebra
    let z4 = create_z4()?;
    let z4_arc = Arc::new(Mutex::new(z4));

    // Create congruence: {0, 2} and {1, 3}
    let congruence = BasicPartition::from_blocks(4, vec![vec![0, 2], vec![1, 3]])?;

    // Create quotient algebra
    let quotient = QuotientAlgebra::new("Z2".to_string(), z4_arc, congruence)?;

    // Test canonical homomorphism
    assert_eq!(quotient.canonical_homomorphism(0)?, 0); // 0 maps to equivalence class 0
    assert_eq!(quotient.canonical_homomorphism(1)?, 1); // 1 maps to equivalence class 1
    assert_eq!(quotient.canonical_homomorphism(2)?, 0); // 2 maps to equivalence class 0
    assert_eq!(quotient.canonical_homomorphism(3)?, 1); // 3 maps to equivalence class 1

    Ok(())
}

#[test]
fn test_quotient_trivial_cases() -> Result<(), Box<dyn std::error::Error>> {
    // Test identity congruence (finest partition)
    let z3 = create_z3()?;
    let z3_arc = Arc::new(Mutex::new(z3));

    // Identity congruence: each element in its own class
    let identity_congruence = BasicPartition::new(3);
    let identity_quotient = QuotientAlgebra::new(
        "Z3_identity".to_string(),
        z3_arc.clone(),
        identity_congruence,
    )?;

    // Should be isomorphic to original
    assert_eq!(identity_quotient.cardinality(), 3);

    // Test universal congruence (coarsest partition)
    let universal_congruence = BasicPartition::from_blocks(3, vec![vec![0, 1, 2]])?;
    let universal_quotient =
        QuotientAlgebra::new("Z3_universal".to_string(), z3_arc, universal_congruence)?;

    // Should be trivial algebra
    assert_eq!(universal_quotient.cardinality(), 1);

    Ok(())
}

#[test]
fn test_quotient_error_cases() -> Result<(), Box<dyn std::error::Error>> {
    // Create algebra
    let mut algebra = BasicAlgebra::with_cardinality("test".to_string(), 3)?;
    let op = Arc::new(Mutex::new(TableOperation::unary(
        "id".to_string(),
        3,
        |x| x,
    )?));
    algebra.add_operation("id".to_string(), op)?;

    // Test mismatched congruence size
    let bad_congruence = BasicPartition::new(5); // Wrong size
    let algebra_arc = Arc::new(Mutex::new(algebra));

    let result = QuotientAlgebra::new("test_quotient".to_string(), algebra_arc, bad_congruence);

    assert!(result.is_err());

    Ok(())
}

#[test]
fn test_quotient_with_constants() -> Result<(), Box<dyn std::error::Error>> {
    // Create algebra with constants
    let mut algebra = BasicAlgebra::with_cardinality("test".to_string(), 4)?;

    // Add constant operation
    let const_op = Arc::new(Mutex::new(TableOperation::constant(
        "const".to_string(),
        2,
        4,
    )?));
    algebra.add_operation("const".to_string(), const_op)?;

    // Add unary operation
    let neg_op = Arc::new(Mutex::new(TableOperation::unary(
        "neg".to_string(),
        4,
        |x| (4 - x) % 4,
    )?));
    algebra.add_operation("neg".to_string(), neg_op)?;

    let algebra_arc = Arc::new(Mutex::new(algebra));

    // Create congruence
    let congruence = BasicPartition::from_blocks(4, vec![vec![0, 2], vec![1, 3]])?;

    // Create quotient
    let quotient = QuotientAlgebra::new("test_quotient".to_string(), algebra_arc, congruence)?;

    // Test constant operation
    let const_quotient = quotient.operation_arc_by_symbol("const")?;
    let const_guard = const_quotient.lock().unwrap();
    let const_result = const_guard.value(&[])?;
    // Constant 2 should map to class 0 (since 2 is in {0,2})
    assert_eq!(const_result, 0);

    drop(const_guard);

    // Test unary operation
    let neg_quotient = quotient.operation_arc_by_symbol("neg")?;
    let neg_guard = neg_quotient.lock().unwrap();

    // neg(0) in original = 0, maps to class 0
    assert_eq!(neg_guard.value(&[0])?, 0);
    // neg(1) in original = 3, maps to class 1 (since 3 is in {1,3})
    assert_eq!(neg_guard.value(&[1])?, 1);

    Ok(())
}

#[test]
fn test_quotient_representatives() -> Result<(), Box<dyn std::error::Error>> {
    // Create Z4 algebra
    let z4 = create_z4()?;
    let z4_arc = Arc::new(Mutex::new(z4));

    // Create congruence with specific representatives order
    let congruence = BasicPartition::from_blocks(4, vec![vec![2, 0], vec![3, 1]])?;

    // Create quotient algebra
    let quotient = QuotientAlgebra::new("Z2".to_string(), z4_arc, congruence)?;

    // Test that operations work correctly regardless of representative order
    let add_quotient = quotient.operation_arc_by_symbol("add")?;
    let add_guard = add_quotient.lock().unwrap();

    // The quotient should still work correctly
    assert_eq!(add_guard.value(&[0, 0])?, 0); // even + even = even
    assert_eq!(add_guard.value(&[0, 1])?, 1); // even + odd = odd
    assert_eq!(add_guard.value(&[1, 0])?, 1); // odd + even = odd
    assert_eq!(add_guard.value(&[1, 1])?, 0); // odd + odd = even

    Ok(())
}

#[test]
fn test_quotient_algebra_traits() -> Result<(), Box<dyn std::error::Error>> {
    // Create Z4 algebra
    let z4 = create_z4()?;
    let z4_arc = Arc::new(Mutex::new(z4));

    // Create congruence
    let congruence = BasicPartition::from_blocks(4, vec![vec![0, 2], vec![1, 3]])?;

    // Create quotient algebra
    let quotient = QuotientAlgebra::new("Z2".to_string(), z4_arc, congruence)?;

    // Test Algebra trait methods
    assert_eq!(quotient.universe(), &[0, 1]);
    assert_eq!(quotient.cardinality(), 2);
    assert_eq!(quotient.operations().len(), 2);
    assert_eq!(quotient.name(), "Z2");

    // Test SmallAlgebra trait methods
    assert_eq!(quotient.max_arity(), 2);
    assert_eq!(quotient.universe_as_range(), 0..2);

    // Test operation access methods
    let op = quotient.operation_arc(0)?;
    assert!(op.lock().is_ok());

    let op_by_symbol = quotient.operation_arc_by_symbol("add")?;
    assert!(op_by_symbol.lock().is_ok());

    // Test subalgebra generation
    let subalgebra = quotient.subalgebra(&[0])?;
    assert!(subalgebra.cardinality() <= 2);

    Ok(())
}

#[test]
fn test_quotient_with_complex_congruence() -> Result<(), Box<dyn std::error::Error>> {
    // Create a larger algebra Z6
    let mut z6 = BasicAlgebra::with_cardinality("Z6".to_string(), 6)?;
    let add_op = Arc::new(Mutex::new(TableOperation::binary(
        "add".to_string(),
        6,
        |a, b| (a + b) % 6,
    )?));
    z6.add_operation("add".to_string(), add_op)?;

    let z6_arc = Arc::new(Mutex::new(z6));

    // Create congruence: {0, 3}, {1, 4}, {2, 5}
    let congruence = BasicPartition::from_blocks(6, vec![vec![0, 3], vec![1, 4], vec![2, 5]])?;

    // Create quotient algebra (should be isomorphic to Z3)
    let quotient = QuotientAlgebra::new("Z6_mod_3".to_string(), z6_arc, congruence)?;

    // Test properties
    assert_eq!(quotient.cardinality(), 3);

    // Test that addition works like Z3
    let add_quotient = quotient.operation_arc_by_symbol("add")?;
    let add_guard = add_quotient.lock().unwrap();

    // Test a few cases
    assert_eq!(add_guard.value(&[0, 1])?, 1); // 0 + 1 = 1
    assert_eq!(add_guard.value(&[1, 2])?, 0); // 1 + 2 = 0 (mod 3)
    assert_eq!(add_guard.value(&[2, 2])?, 1); // 2 + 2 = 1 (mod 3)

    Ok(())
}

#[test]
fn test_quotient_super_algebra_access() -> Result<(), Box<dyn std::error::Error>> {
    // Create Z4 algebra
    let z4 = create_z4()?;
    let z4_arc = Arc::new(Mutex::new(z4));
    let z4_clone = z4_arc.clone();

    // Create congruence
    let congruence = BasicPartition::from_blocks(4, vec![vec![0, 2], vec![1, 3]])?;

    // Create quotient algebra
    let quotient = QuotientAlgebra::new("Z2".to_string(), z4_arc, congruence)?;

    // Test super algebra access
    let super_algebra = quotient.super_algebra();
    let super_guard = super_algebra.lock().unwrap();
    assert_eq!(super_guard.cardinality(), 4);
    assert_eq!(super_guard.name(), "Z4");
    drop(super_guard);

    // Test congruence access
    let quotient_congruence = quotient.congruence();
    assert_eq!(quotient_congruence.size(), 4);
    assert_eq!(quotient_congruence.num_blocks(), 2);

    // Test representative index lookup
    assert_eq!(quotient.representative_index(0)?, 0);
    assert_eq!(quotient.representative_index(1)?, 1);

    Ok(())
}

#[test]
fn test_quotient_operation_tables() -> Result<(), Box<dyn std::error::Error>> {
    // Create Z4 algebra
    let z4 = create_z4()?;
    let z4_arc = Arc::new(Mutex::new(z4));

    // Create congruence
    let congruence = BasicPartition::from_blocks(4, vec![vec![0, 2], vec![1, 3]])?;

    // Create quotient algebra
    let mut quotient = QuotientAlgebra::new("Z2".to_string(), z4_arc, congruence)?;

    // Build operation tables
    quotient.make_operation_tables()?;

    // Test that operations still work after table building
    let add_quotient = quotient.operation_arc_by_symbol("add")?;
    let add_guard = add_quotient.lock().unwrap();
    assert_eq!(add_guard.value(&[0, 0])?, 0);
    assert_eq!(add_guard.value(&[1, 1])?, 0);

    Ok(())
}
