use uacalc_core::malcev::MalcevAnalyzer;
use uacalc_core::algebra::{BasicAlgebra, Algebra};
use uacalc_core::operation::{OperationSymbol, TableOperation};
use std::sync::{Arc, Mutex};

#[test]
fn test_baker2_deadlock() {
    println!("=== BAKER2 DEADLOCK TEST ===");
    
    // Create the Baker2 algebra exactly as it appears in the .ua file
    let mut algebra = BasicAlgebra::new("Baker2".to_string(), vec![0, 1]).unwrap();
    
    // Add the ternary operation "bak" with the exact table from the .ua file
    // The table shows [x,y] -> [z0, z1] where bak(x,y,z) = z0 if z=0, z1 if z=1
    let op_symbol = OperationSymbol::new("bak".to_string(), 3);
    let op_table = vec![
        vec![0, 0, 0, 0], // [0,0,0] -> 0 (from [0,0] -> 0,0)
        vec![0, 0, 1, 0], // [0,0,1] -> 0 (from [0,0] -> 0,0)
        vec![0, 1, 0, 0], // [0,1,0] -> 0 (from [0,1] -> 0,0)
        vec![0, 1, 1, 0], // [0,1,1] -> 0 (from [0,1] -> 0,0)
        vec![1, 0, 0, 0], // [1,0,0] -> 0 (from [1,0] -> 0,1)
        vec![1, 0, 1, 1], // [1,0,1] -> 1 (from [1,0] -> 0,1)
        vec![1, 1, 0, 1], // [1,1,0] -> 1 (from [1,1] -> 1,1)
        vec![1, 1, 1, 1], // [1,1,1] -> 1 (from [1,1] -> 1,1)
    ];
    
    let op = TableOperation::new(op_symbol, op_table, 2).unwrap();
    algebra.add_operation("bak".to_string(), Arc::new(Mutex::new(op))).unwrap();
    
    println!("Created Baker2 algebra with cardinality: {}", algebra.cardinality());
    println!("Operations: {}", algebra.operations().len());
    
    // Test the Malcev analysis that's causing the deadlock
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
    
    println!("=== BAKER2 DEADLOCK TEST COMPLETED ===");
}
