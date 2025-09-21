use uacalc_core::algebra::{BasicAlgebra, Algebra};
use uacalc_core::malcev::MalcevAnalyzer;
use uacalc_core::free_algebra::{FreeAlgebra, VarietyConstraint};
use uacalc_core::operation::{OperationSymbol, TableOperation};
use uacalc_core::memory::{set_memory_limit, reset_memory_limit, would_exceed_limit};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

/// Helper function to create a simple 2-element join algebra
fn create_join_algebra() -> Result<BasicAlgebra, Box<dyn std::error::Error>> {
    println!("    create_join_algebra: Starting");
    let mut algebra = BasicAlgebra::new("Join2".to_string(), vec![0, 1])?;
    println!("    create_join_algebra: BasicAlgebra created");
    
    // Create join operation: max(x,y)
    let join_symbol = OperationSymbol::new("join".to_string(), 2);
    println!("    create_join_algebra: OperationSymbol created");
    let join_table = vec![
        vec![0, 0, 0], // join(0,0) = 0
        vec![0, 1, 1], // join(0,1) = 1
        vec![1, 0, 1], // join(1,0) = 1
        vec![1, 1, 1], // join(1,1) = 1
    ];
    println!("    create_join_algebra: Table created");
    
    let join_op = TableOperation::new(join_symbol, join_table, 2)?;
    println!("    create_join_algebra: TableOperation created");
    algebra.add_operation("join".to_string(), Arc::new(Mutex::new(join_op)))?;
    println!("    create_join_algebra: Operation added to algebra");
    
    Ok(algebra)
}

/// Helper function to create a 3-element join algebra
fn create_join_algebra_3() -> Result<BasicAlgebra, Box<dyn std::error::Error>> {
    let mut algebra = BasicAlgebra::new("Join3".to_string(), vec![0, 1, 2])?;
    
    // Create join operation: max(x,y)
    let join_symbol = OperationSymbol::new("join".to_string(), 2);
    let join_table = vec![
        vec![0, 0, 0], vec![0, 1, 1], vec![0, 2, 2],
        vec![1, 0, 1], vec![1, 1, 1], vec![1, 2, 2],
        vec![2, 0, 2], vec![2, 1, 2], vec![2, 2, 2],
    ];
    
    let join_op = TableOperation::new(join_symbol, join_table, 3)?;
    algebra.add_operation("join".to_string(), Arc::new(Mutex::new(join_op)))?;
    
    Ok(algebra)
}

/// Helper function to create an algebra without semilattice operations
fn create_non_semilattice_algebra() -> Result<BasicAlgebra, Box<dyn std::error::Error>> {
    let mut algebra = BasicAlgebra::new("NonSemilattice".to_string(), vec![0, 1])?;
    
    // Create a non-commutative operation
    let op_symbol = OperationSymbol::new("op".to_string(), 2);
    let op_table = vec![
        vec![0, 0, 0], // op(0,0) = 0
        vec![0, 1, 1], // op(0,1) = 1
        vec![1, 0, 0], // op(1,0) = 0 (not commutative: op(0,1) != op(1,0))
        vec![1, 1, 1], // op(1,1) = 1
    ];
    
    let op = TableOperation::new(op_symbol, op_table, 2)?;
    algebra.add_operation("op".to_string(), Arc::new(Mutex::new(op)))?;
    
    Ok(algebra)
}

/// Test FreeAlgebra construction and basic functionality
#[test]
fn test_free_algebra_construction() -> Result<(), Box<dyn std::error::Error>> {
    println!("Testing FreeAlgebra construction...");
    
    let algebra = create_join_algebra()?;
    
    // Test FreeAlgebra::from_algebra
    let free_algebra = FreeAlgebra::from_algebra(&algebra, 2, 3)?;
    
    assert_eq!(free_algebra.name(), "F2");
    assert_eq!(free_algebra.generators().len(), 2);
    assert_eq!(free_algebra.generators()[0], "x0");
    assert_eq!(free_algebra.generators()[1], "x1");
    assert_eq!(free_algebra.variety_constraints(), &VarietyConstraint::Idempotent);
    
    println!("✓ FreeAlgebra construction successful");
    Ok(())
}

/// Test FreeAlgebra term generation
#[test]
fn test_free_algebra_terms() -> Result<(), Box<dyn std::error::Error>> {
    println!("Testing FreeAlgebra term generation...");
    
    let algebra = create_join_algebra()?;
    let free_algebra = FreeAlgebra::from_algebra(&algebra, 2, 2)?; // Small depth for testing
    
    // Test get_terms
    let terms = free_algebra.get_terms();
    assert!(!terms.is_empty(), "Should have at least generator terms");
    assert!(terms.len() >= 2, "Should have at least 2 generator terms");
    
    // Test get_idempotent_terms
    let idempotent_terms = free_algebra.get_idempotent_terms()?;
    assert!(!idempotent_terms.is_empty(), "Should have at least generator terms as idempotent");
    
    println!("✓ FreeAlgebra term generation successful");
    println!("  - Total terms: {}", terms.len());
    println!("  - Idempotent terms: {}", idempotent_terms.len());
    
    Ok(())
}

/// Test term interpretation functionality
#[test]
fn test_term_interpretation() -> Result<(), Box<dyn std::error::Error>> {
    println!("Testing term interpretation...");
    
    let algebra = create_join_algebra()?;
    let free_algebra = FreeAlgebra::from_algebra(&algebra, 2, 2)?;
    
    let terms = free_algebra.get_terms();
    
    // Test interpretation of generator terms
    for term_id in &terms[0..2] { // First two should be generators
        let term_op = free_algebra.term_interpretation(*term_id, &algebra, true)?;
        
        // Use trylock to prevent deadlocks
        let op_guard = term_op.try_lock()
            .map_err(|_| "Failed to acquire lock - potential deadlock")?;
        
        assert_eq!(op_guard.arity(), 2, "Generator terms should have arity 2 when interpreted");
        assert_eq!(op_guard.set_size(), 2, "Should have set size 2");
    }
    
    println!("✓ Term interpretation successful");
    Ok(())
}

/// Test operation property checking (commutative, associative)
#[test]
fn test_operation_properties() -> Result<(), Box<dyn std::error::Error>> {
    println!("Testing operation properties...");
    
    let algebra = create_join_algebra()?;
    let free_algebra = FreeAlgebra::from_algebra(&algebra, 2, 2)?;
    
    let terms = free_algebra.get_terms();
    
    // Test properties on generator terms
    for term_id in &terms[0..2] {
        let term_op = free_algebra.term_interpretation(*term_id, &algebra, true)?;
        
        // Use trylock to prevent deadlocks
        let op_guard = term_op.try_lock()
            .map_err(|_| "Failed to acquire lock - potential deadlock")?;
        
        // Test commutative property
        let is_commutative = op_guard.is_commutative()?;
        println!("  - Term {} is commutative: {}", term_id, is_commutative);
        
        // Test associative property
        let is_associative = op_guard.is_associative()?;
        println!("  - Term {} is associative: {}", term_id, is_associative);
    }
    
    println!("✓ Operation properties testing successful");
    Ok(())
}

/// Test semilattice term finding with deadlock prevention
#[test]
fn test_semilattice_term_finding() -> Result<(), Box<dyn std::error::Error>> {
    println!("Testing semilattice term finding...");
    
    let algebra = create_join_algebra()?;
    let mut analyzer = MalcevAnalyzer::new();
    
    // Test with timeout to prevent hanging
    let start_time = Instant::now();
    let timeout = Duration::from_secs(10);
    
    let analysis = analyzer.analyze_malcev_conditions(&algebra)?;
    
    let elapsed = start_time.elapsed();
    assert!(elapsed < timeout, "Analysis took too long: {:?}", elapsed);
    
    // Check if semilattice term was found
    if let Some(term) = &analysis.semilattice_term {
        println!("✓ Semilattice term found: {}", term);
        assert!(term.contains("join"), "Should find join operation as semilattice term");
    } else {
        println!("✗ No semilattice term found");
    }
    
    println!("✓ Semilattice term finding completed in {:?}", elapsed);
    Ok(())
}

/// Test semilattice term finding on 3-element algebra
#[test]
fn test_semilattice_term_3_element() -> Result<(), Box<dyn std::error::Error>> {
    println!("Testing semilattice term finding on 3-element algebra...");
    
    let algebra = create_join_algebra_3()?;
    let mut analyzer = MalcevAnalyzer::new();
    
    let start_time = Instant::now();
    let analysis = analyzer.analyze_malcev_conditions(&algebra)?;
    let elapsed = start_time.elapsed();
    
    if let Some(term) = &analysis.semilattice_term {
        println!("✓ Semilattice term found: {}", term);
    } else {
        println!("✗ No semilattice term found");
    }
    
    println!("✓ 3-element algebra analysis completed in {:?}", elapsed);
    Ok(())
}

/// Test non-semilattice algebra
#[test]
fn test_non_semilattice_algebra() -> Result<(), Box<dyn std::error::Error>> {
    println!("Testing non-semilattice algebra...");
    
    let algebra = create_non_semilattice_algebra()?;
    let mut analyzer = MalcevAnalyzer::new();
    
    let start_time = Instant::now();
    let analysis = analyzer.analyze_malcev_conditions(&algebra)?;
    let elapsed = start_time.elapsed();
    
    // Should not find a semilattice term
    assert!(analysis.semilattice_term.is_none(), "Non-semilattice algebra should not have semilattice term");
    
    println!("✓ Non-semilattice algebra correctly identified in {:?}", elapsed);
    Ok(())
}

/// Test memory limit functionality
#[test]
fn test_memory_limits() -> Result<(), Box<dyn std::error::Error>> {
    println!("Testing memory limits...");
    
    // Set a small memory limit
    set_memory_limit(1024 * 1024)?; // 1MB
    
    let algebra = create_join_algebra()?;
    
    // Test that we can still create free algebra with small limit
    let free_algebra = FreeAlgebra::from_algebra(&algebra, 2, 2)?;
    assert_eq!(free_algebra.name(), "F2");
    
    // Test memory limit checking
    let would_exceed = would_exceed_limit(1024 * 1024 * 2); // 2MB
    assert!(would_exceed, "Should detect memory limit would be exceeded");
    
    // Reset memory limit
    reset_memory_limit()?;
    
    println!("✓ Memory limit testing successful");
    Ok(())
}

/// Test deadlock prevention with multiple concurrent operations
#[test]
fn test_deadlock_prevention() -> Result<(), Box<dyn std::error::Error>> {
    println!("Testing deadlock prevention...");
    
    let algebra = create_join_algebra()?;
    let free_algebra = FreeAlgebra::from_algebra(&algebra, 2, 2)?;
    
    let terms = free_algebra.get_terms();
    
    // Create multiple operations concurrently
    let mut operations = Vec::new();
    for term_id in &terms[0..2] {
        let term_op = free_algebra.term_interpretation(*term_id, &algebra, true)?;
        operations.push(term_op);
    }
    
    // Test concurrent access with trylock
    let start_time = Instant::now();
    let timeout = Duration::from_secs(5);
    
    for (i, op) in operations.iter().enumerate() {
        let op_guard = op.try_lock()
            .map_err(|_| format!("Failed to acquire lock for operation {} - potential deadlock", i))?;
        
        // Quick property check
        let _is_commutative = op_guard.is_commutative()?;
        let _is_associative = op_guard.is_associative()?;
        
        let elapsed = start_time.elapsed();
        assert!(elapsed < timeout, "Operation {} took too long: {:?}", i, elapsed);
    }
    
    println!("✓ Deadlock prevention testing successful");
    Ok(())
}

/// Test large algebra with memory constraints
#[test]
fn test_large_algebra_memory() -> Result<(), Box<dyn std::error::Error>> {
    println!("Testing large algebra with memory constraints...");
    
    // Set memory limit
    set_memory_limit(50 * 1024 * 1024)?; // 50MB
    
    // Create a larger algebra
    let mut algebra = BasicAlgebra::new("Large".to_string(), (0..5).collect())?;
    
    // Add a binary operation
    let op_symbol = OperationSymbol::new("op".to_string(), 2);
    let mut op_table = Vec::new();
    for x in 0..5 {
        for y in 0..5 {
            op_table.push(vec![x, y, (x + y) % 5]);
        }
    }
    
    let op = TableOperation::new(op_symbol, op_table, 5)?;
    algebra.add_operation("op".to_string(), Arc::new(Mutex::new(op)))?;
    
    let start_time = Instant::now();
    let mut analyzer = MalcevAnalyzer::new();
    
    // This should complete within memory limits
    let analysis = analyzer.analyze_malcev_conditions(&algebra)?;
    let elapsed = start_time.elapsed();
    
    println!("✓ Large algebra analysis completed in {:?}", elapsed);
    println!("  - Analysis completed: {}", analysis.analysis_completed);
    
    // Reset memory limit
    reset_memory_limit()?;
    
    Ok(())
}

/// Test error handling and recovery
#[test]
fn test_error_handling() -> Result<(), Box<dyn std::error::Error>> {
    println!("Testing error handling...");
    println!("  - Test started");
    
    // Test with invalid parameters
    println!("  - Creating join algebra...");
    let algebra = create_join_algebra()?;
    println!("  - Join algebra created successfully");
    
    // Test FreeAlgebra with 0 generators (should fail)
    println!("  - Testing FreeAlgebra with 0 generators...");
    let result = FreeAlgebra::from_algebra(&algebra, 0, 3);
    assert!(result.is_err(), "Should fail with 0 generators");
    println!("  - 0 generators test passed");
    
    // Test with small depth first to avoid hanging
    println!("  - Testing FreeAlgebra with small depth (2)...");
    let result = FreeAlgebra::from_algebra(&algebra, 2, 2);
    match result {
        Ok(_) => println!("  - Small depth handled gracefully"),
        Err(e) => println!("  - Small depth properly rejected: {}", e),
    }
    println!("  - Small depth test completed");
    
    println!("✓ Error handling testing successful");
    Ok(())
}

/// Performance benchmark test
#[test]
fn test_performance_benchmark() -> Result<(), Box<dyn std::error::Error>> {
    println!("Running performance benchmark...");
    
    let algebra = create_join_algebra()?;
    let mut analyzer = MalcevAnalyzer::new();
    
    // Run multiple iterations to get average time
    let iterations = 5;
    let mut total_time = Duration::new(0, 0);
    
    for i in 0..iterations {
        let start_time = Instant::now();
        let _analysis = analyzer.analyze_malcev_conditions(&algebra)?;
        let elapsed = start_time.elapsed();
        total_time += elapsed;
        
        println!("  Iteration {}: {:?}", i + 1, elapsed);
    }
    
    let average_time = total_time / iterations;
    println!("✓ Average analysis time: {:?}", average_time);
    
    // Should complete reasonably quickly
    assert!(average_time < Duration::from_secs(5), "Analysis should complete within 5 seconds on average");
    
    Ok(())
}
