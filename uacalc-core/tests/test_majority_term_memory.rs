use uacalc_core::algebra::BasicAlgebra;
use uacalc_core::malcev::MalcevAnalyzer;
use uacalc_core::Algebra;
use std::sync::{Arc, Mutex};


#[test]
fn test_baker2_majority_term() -> Result<(), Box<dyn std::error::Error>> {
    println!("Testing Baker2 algebra majority term...");
    
    // Create the Baker2 algebra manually
    // Baker2 is a 2-element algebra with a ternary operation 'bak'
    // The operation table from the .ua file:
    // bak(0,0,0) = 0, bak(0,0,1) = 0
    // bak(0,1,0) = 0, bak(0,1,1) = 0  
    // bak(1,0,0) = 0, bak(1,0,1) = 1
    // bak(1,1,0) = 1, bak(1,1,1) = 1
    
    use uacalc_core::algebra::BasicAlgebra;
    use uacalc_core::operation::{OperationSymbol, TableOperation};
    
    let mut algebra = BasicAlgebra::new("Baker2".to_string(), vec![0, 1])?;
    
    // Create the ternary operation 'bak'
    let bak_symbol = OperationSymbol::new("bak".to_string(), 3);
    let bak_table = vec![
        vec![0, 0, 0, 0], // bak(0,0,0) = 0
        vec![0, 0, 1, 0], // bak(0,0,1) = 0
        vec![0, 1, 0, 0], // bak(0,1,0) = 0
        vec![0, 1, 1, 0], // bak(0,1,1) = 0
        vec![1, 0, 0, 0], // bak(1,0,0) = 0
        vec![1, 0, 1, 1], // bak(1,0,1) = 1
        vec![1, 1, 0, 1], // bak(1,1,0) = 1
        vec![1, 1, 1, 1], // bak(1,1,1) = 1
    ];
    
    let bak_op = TableOperation::new(bak_symbol, bak_table, 2)?;
    algebra.add_operation("bak".to_string(), Arc::new(Mutex::new(bak_op)))?;
    
    println!("Created algebra: {} (size: {})", algebra.name(), algebra.cardinality());
    
    // Print operation details
    let operations = algebra.operations();
    for (i, op_arc) in operations.iter().enumerate() {
        let op_guard = op_arc.lock().unwrap();
        println!("Operation {}: {} (arity: {})", i, op_guard.symbol().name, op_guard.arity());
        
        // For the Baker2 algebra, let's check the ternary operation values
        if op_guard.arity() == 3 {
            println!("Ternary operation values:");
            for x in 0..2 {
                for y in 0..2 {
                    for z in 0..2 {
                        let result = op_guard.value(&[x, y, z]).unwrap();
                        println!("  bak({},{},{}) = {}", x, y, z, result);
                    }
                }
            }
        }
    }
    
    // Test majority term computation
    println!("\nTesting majority term...");
    let mut analyzer = MalcevAnalyzer::new();
    let analysis = analyzer.analyze_malcev_conditions(&algebra)?;
    
    println!("Rust results:");
    println!("  - has_majority_term: {}", analysis.has_majority_term);
    println!("  - has_malcev_term: {}", analysis.has_malcev_term);
    println!("  - has_join_term: {}", analysis.has_join_term);
    println!("  - congruence_modular: {}", analysis.congruence_modular);
    println!("  - congruence_distributive: {}", analysis.congruence_distributive);
    println!("  - analysis_completed: {}", analysis.analysis_completed);
    
    // Expected result: has_majority_term should be false (matches Java)
    assert_eq!(analysis.has_majority_term, false, "Baker2 should not have a majority term");
    
    println!("\n✓ Correct result: No majority term found (matches Java)");
    
    Ok(())
}
