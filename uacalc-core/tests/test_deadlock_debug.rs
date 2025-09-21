use uacalc_core::malcev::MalcevAnalyzer;
use uacalc_core::algebra::{BasicAlgebra, Algebra};
use uacalc_core::operation::{OperationSymbol, TableOperation};
use std::sync::{Arc, Mutex};

#[test]
fn test_deadlock_debug_small_algebra() {
    println!("=== DEADLOCK DEBUG TEST: Small Algebra ===");
    
    // Create a small algebra similar to what the Python test might be doing
    let mut algebra = BasicAlgebra::new("TestAlgebra".to_string(), vec![0, 1, 2]).unwrap();
    
    // Add a simple binary operation
    let op_symbol = OperationSymbol::new("f".to_string(), 2);
    let mut op_table = Vec::new();
    for x in 0..3 {
        for y in 0..3 {
            op_table.push(vec![x, y, (x + y) % 3]);
        }
    }
    
    let op = TableOperation::new(op_symbol, op_table, 3).unwrap();
    algebra.add_operation("f".to_string(), Arc::new(Mutex::new(op))).unwrap();
    
    println!("Created algebra with cardinality: {}", algebra.cardinality());
    
    // Test the Malcev analysis that's causing the segfault
    let mut analyzer = MalcevAnalyzer::new();
    
    println!("Starting Malcev analysis...");
    match analyzer.analyze_malcev_conditions(&algebra) {
        Ok(analysis) => {
            println!("Analysis completed successfully!");
            println!("  - Has Malcev term: {}", analysis.has_malcev_term);
            println!("  - Has join term: {}", analysis.has_join_term);
            println!("  - Analysis completed: {}", analysis.analysis_completed);
            println!("  - Semilattice term: {:?}", analysis.semilattice_term);
        },
        Err(e) => {
            println!("Analysis failed with error: {}", e);
        }
    }
    
    println!("=== DEADLOCK DEBUG TEST COMPLETED ===");
}

#[test]
fn test_deadlock_debug_medium_algebra() {
    println!("=== DEADLOCK DEBUG TEST: Medium Algebra ===");
    
    // Create a medium algebra that might trigger the deadlock
    let mut algebra = BasicAlgebra::new("TestAlgebra".to_string(), vec![0, 1, 2, 3]).unwrap();
    
    // Add a simple binary operation
    let op_symbol = OperationSymbol::new("f".to_string(), 2);
    let mut op_table = Vec::new();
    for x in 0..4 {
        for y in 0..4 {
            op_table.push(vec![x, y, (x + y) % 4]);
        }
    }
    
    let op = TableOperation::new(op_symbol, op_table, 4).unwrap();
    algebra.add_operation("f".to_string(), Arc::new(Mutex::new(op))).unwrap();
    
    println!("Created algebra with cardinality: {}", algebra.cardinality());
    
    // Test the Malcev analysis that's causing the segfault
    let mut analyzer = MalcevAnalyzer::new();
    
    println!("Starting Malcev analysis...");
    match analyzer.analyze_malcev_conditions(&algebra) {
        Ok(analysis) => {
            println!("Analysis completed successfully!");
            println!("  - Has Malcev term: {}", analysis.has_malcev_term);
            println!("  - Has join term: {}", analysis.has_join_term);
            println!("  - Analysis completed: {}", analysis.analysis_completed);
            println!("  - Semilattice term: {:?}", analysis.semilattice_term);
        },
        Err(e) => {
            println!("Analysis failed with error: {}", e);
        }
    }
    
    println!("=== DEADLOCK DEBUG TEST COMPLETED ===");
}

#[test]
fn test_deadlock_debug_semilattice_term_only() {
    println!("=== DEADLOCK DEBUG TEST: Semilattice Term Only ===");
    
    // Create a semilattice algebra
    let mut algebra = BasicAlgebra::new("Semilattice".to_string(), vec![0, 1, 2]).unwrap();
    
    // Add a semilattice operation (join)
    let op_symbol = OperationSymbol::new("join".to_string(), 2);
    let op_table = vec![
        vec![0, 0, 0], vec![0, 1, 1], vec![0, 2, 2],
        vec![1, 0, 1], vec![1, 1, 1], vec![1, 2, 2],
        vec![2, 0, 2], vec![2, 1, 2], vec![2, 2, 2],
    ];
    
    let op = TableOperation::new(op_symbol, op_table, 3).unwrap();
    algebra.add_operation("join".to_string(), Arc::new(Mutex::new(op))).unwrap();
    
    println!("Created semilattice algebra with cardinality: {}", algebra.cardinality());
    
    // Test just the semilattice term finding
    let mut analyzer = MalcevAnalyzer::new();
    
    println!("Starting semilattice term finding...");
    match analyzer.find_semilattice_term(&algebra) {
        Ok(term) => {
            println!("Found semilattice term: {}", term);
        },
        Err(e) => {
            println!("Semilattice term finding failed with error: {}", e);
        }
    }
    
    println!("=== DEADLOCK DEBUG TEST COMPLETED ===");
}
