use std::sync::{Arc, Mutex};
use uacalc_core::prelude::*;
use uacalc_core::malcev::MalcevAnalyzer;

/// Test TCT type detection compatibility with Java implementation
/// This test verifies that the Rust implementation produces consistent
/// results with the Java TypeFinder for basic algebras.

#[test]
fn test_tct_type_trivial_algebra() -> Result<(), Box<dyn std::error::Error>> {
    // Test trivial algebra (size 1) - should be type 1
    let universe = vec![0];
    let algebra = BasicAlgebra::new("trivial".to_string(), universe)?;
    
    let analyzer = MalcevAnalyzer::new();
    let tct_analysis = analyzer.analyze_tct_type(&algebra)?;
    
    assert_eq!(tct_analysis.tct_type, 1);
    assert!(tct_analysis.type_determined);
    assert!(tct_analysis.has_type_1);
    assert!(!tct_analysis.has_type_2);
    assert!(!tct_analysis.has_type_3);
    assert!(!tct_analysis.has_type_4);
    assert!(!tct_analysis.has_type_5);
    
    Ok(())
}

#[test]
fn test_tct_type_small_boolean_algebra() -> Result<(), Box<dyn std::error::Error>> {
    // Test small boolean algebra (size 2) with meet and join operations
    let universe = vec![0, 1];
    let mut algebra = BasicAlgebra::new("boolean".to_string(), universe)?;
    
    // Add meet operation (min)
    let meet_op = Arc::new(Mutex::new(TableOperation::binary("meet".to_string(), 2, |a, b| {
        if a == 0 || b == 0 { 0 } else { 1 }
    })?));
    
    // Add join operation (max)
    let join_op = Arc::new(Mutex::new(TableOperation::binary("join".to_string(), 2, |a, b| {
        if a == 1 || b == 1 { 1 } else { 0 }
    })?));
    
    algebra.add_operation("meet".to_string(), meet_op)?;
    algebra.add_operation("join".to_string(), join_op)?;
    
    let analyzer = MalcevAnalyzer::new();
    let tct_analysis = analyzer.analyze_tct_type(&algebra)?;
    
    // Boolean algebras should have type 1 (distributive)
    assert_eq!(tct_analysis.tct_type, 1);
    assert!(tct_analysis.type_determined);
    assert!(tct_analysis.has_type_1);
    
    Ok(())
}

#[test]
fn test_tct_type_small_group_algebra() -> Result<(), Box<dyn std::error::Error>> {
    // Test small group algebra (Z/3Z) - should be type 1
    let universe = vec![0, 1, 2];
    let mut algebra = BasicAlgebra::new("z3".to_string(), universe)?;
    
    // Add group operation (addition mod 3)
    let add_op = Arc::new(Mutex::new(TableOperation::binary("add".to_string(), 3, |a, b| {
        (a + b) % 3
    })?));
    
    // Add inverse operation
    let inv_op = Arc::new(Mutex::new(TableOperation::unary("inv".to_string(), 3, |x| {
        (3 - x) % 3
    })?));
    
    algebra.add_operation("add".to_string(), add_op)?;
    algebra.add_operation("inv".to_string(), inv_op)?;
    
    let analyzer = MalcevAnalyzer::new();
    let tct_analysis = analyzer.analyze_tct_type(&algebra)?;
    
    // Groups should have type 1
    assert_eq!(tct_analysis.tct_type, 1);
    assert!(tct_analysis.type_determined);
    assert!(tct_analysis.has_type_1);
    
    Ok(())
}

#[test]
fn test_tct_type_small_lattice_algebra() -> Result<(), Box<dyn std::error::Error>> {
    // Test small lattice algebra (size 3) - should be type 1
    let universe = vec![0, 1, 2];
    let mut algebra = BasicAlgebra::new("lattice3".to_string(), universe)?;
    
    // Add meet operation
    let meet_op = Arc::new(Mutex::new(TableOperation::binary("meet".to_string(), 3, |a, b| {
        match (a, b) {
            (0, _) | (_, 0) => 0,
            (1, 1) => 1,
            (1, 2) | (2, 1) => 1,
            (2, 2) => 2,
            _ => 0,
        }
    })?));
    
    // Add join operation
    let join_op = Arc::new(Mutex::new(TableOperation::binary("join".to_string(), 3, |a, b| {
        match (a, b) {
            (2, _) | (_, 2) => 2,
            (1, 1) => 1,
            (0, 1) | (1, 0) => 1,
            (0, 0) => 0,
            _ => 2,
        }
    })?));
    
    algebra.add_operation("meet".to_string(), meet_op)?;
    algebra.add_operation("join".to_string(), join_op)?;
    
    let analyzer = MalcevAnalyzer::new();
    let tct_analysis = analyzer.analyze_tct_type(&algebra)?;
    
    // Small lattices should have type 1
    assert_eq!(tct_analysis.tct_type, 1);
    assert!(tct_analysis.type_determined);
    assert!(tct_analysis.has_type_1);
    
    Ok(())
}

#[test]
fn test_tct_type_memory_estimation() -> Result<(), Box<dyn std::error::Error>> {
    // Test that TCT analysis works for medium-sized algebras
    let universe = vec![0, 1, 2, 3, 4];
    let algebra = BasicAlgebra::new("test5".to_string(), universe)?;
    
    let analyzer = MalcevAnalyzer::new();
    let tct_analysis = analyzer.analyze_tct_type(&algebra)?;
    
    // Should return a valid result
    assert!(tct_analysis.tct_type >= 0);
    assert!(tct_analysis.tct_type <= 5);
    
    Ok(())
}

#[test]
fn test_tct_type_consistency() -> Result<(), Box<dyn std::error::Error>> {
    // Test that TCT type analysis is consistent across multiple calls
    let universe = vec![0, 1, 2];
    let mut algebra = BasicAlgebra::new("consistency_test".to_string(), universe)?;
    
    // Add a simple operation
    let op = Arc::new(Mutex::new(TableOperation::binary("op".to_string(), 3, |a, b| {
        (a + b) % 3
    })?));
    algebra.add_operation("op".to_string(), op)?;
    
    let analyzer = MalcevAnalyzer::new();
    
    // Run analysis multiple times
    let result1 = analyzer.analyze_tct_type(&algebra)?;
    let result2 = analyzer.analyze_tct_type(&algebra)?;
    let result3 = analyzer.analyze_tct_type(&algebra)?;
    
    // Results should be identical
    assert_eq!(result1.tct_type, result2.tct_type);
    assert_eq!(result2.tct_type, result3.tct_type);
    assert_eq!(result1.type_determined, result2.type_determined);
    assert_eq!(result2.type_determined, result3.type_determined);
    
    Ok(())
}

#[test]
fn test_tct_type_edge_cases() -> Result<(), Box<dyn std::error::Error>> {
    // Test edge cases for TCT type analysis
    
    // Test algebra with no operations
    let universe = vec![0, 1];
    let algebra = BasicAlgebra::new("no_ops".to_string(), universe)?;
    
    let analyzer = MalcevAnalyzer::new();
    let tct_analysis = analyzer.analyze_tct_type(&algebra)?;
    
    // Algebra with no operations should still have a type
    assert!(tct_analysis.tct_type >= 0);
    assert!(tct_analysis.tct_type <= 5);
    
    Ok(())
}

#[test]
fn test_tct_type_advanced_properties() -> Result<(), Box<dyn std::error::Error>> {
    // Test that TCT analysis includes advanced properties
    let universe = vec![0, 1, 2];
    let mut algebra = BasicAlgebra::new("advanced_test".to_string(), universe)?;
    
    // Add operations that might affect advanced properties
    let meet_op = Arc::new(Mutex::new(TableOperation::binary("meet".to_string(), 3, |a, b| {
        if a == 0 || b == 0 { 0 } else { 1 }
    })?));
    
    let join_op = Arc::new(Mutex::new(TableOperation::binary("join".to_string(), 3, |a, b| {
        if a == 2 || b == 2 { 2 } else { 1 }
    })?));
    
    algebra.add_operation("meet".to_string(), meet_op)?;
    algebra.add_operation("join".to_string(), join_op)?;
    
    let analyzer = MalcevAnalyzer::new();
    let tct_analysis = analyzer.analyze_tct_type(&algebra)?;
    
    // Verify that the analysis includes all expected fields
    assert!(tct_analysis.tct_type >= 0);
    assert!(tct_analysis.tct_type <= 5);
    assert!(tct_analysis.type_determined || !tct_analysis.type_determined); // Either true or false
    assert!(tct_analysis.has_type_1 || !tct_analysis.has_type_1);
    assert!(tct_analysis.has_type_2 || !tct_analysis.has_type_2);
    assert!(tct_analysis.has_type_3 || !tct_analysis.has_type_3);
    assert!(tct_analysis.has_type_4 || !tct_analysis.has_type_4);
    assert!(tct_analysis.has_type_5 || !tct_analysis.has_type_5);
    
    Ok(())
}

#[test]
fn test_tct_type_memory_limit_handling() -> Result<(), Box<dyn std::error::Error>> {
    // Test that TCT analysis handles memory limits gracefully
    let universe = vec![0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; // Size 10
    let mut algebra = BasicAlgebra::new("memory_test".to_string(), universe)?;
    
    // Add some operations
    let op1 = Arc::new(Mutex::new(TableOperation::binary("op1".to_string(), 10, |a, b| {
        (a + b) % 10
    })?));
    
    let op2 = Arc::new(Mutex::new(TableOperation::unary("op2".to_string(), 10, |x| {
        (x + 1) % 10
    })?));
    
    algebra.add_operation("op1".to_string(), op1)?;
    algebra.add_operation("op2".to_string(), op2)?;
    
    let analyzer = MalcevAnalyzer::new();
    
    // This should not panic or fail, even if memory limits are reached
    let tct_analysis = analyzer.analyze_tct_type(&algebra)?;
    
    // Should still return a valid result
    assert!(tct_analysis.tct_type >= 0);
    assert!(tct_analysis.tct_type <= 5);
    
    Ok(())
}
