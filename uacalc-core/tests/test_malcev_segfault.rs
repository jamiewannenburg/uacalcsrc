use uacalc_core::algebra::{BasicAlgebra, Algebra};
use uacalc_core::malcev::MalcevAnalyzer;
use uacalc_core::operation::{OperationSymbol, TableOperation};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

/// Helper function to create a simple 4-element algebra that should trigger the segfault
fn create_problematic_algebra() -> Result<BasicAlgebra, Box<dyn std::error::Error>> {
    println!("    create_problematic_algebra: Starting");
    let mut algebra = BasicAlgebra::new("Problem4".to_string(), vec![0, 1, 2, 3])?;
    println!("    create_problematic_algebra: BasicAlgebra created");
    
    // Create a binary operation that will cause issues in subalgebra generation
    let op_symbol = OperationSymbol::new("f".to_string(), 2);
    println!("    create_problematic_algebra: OperationSymbol created");
    
    // Create a simple operation table
    let op_table = vec![
        vec![0, 0, 0], vec![0, 1, 1], vec![0, 2, 2], vec![0, 3, 3],
        vec![1, 0, 1], vec![1, 1, 0], vec![1, 2, 3], vec![1, 3, 2],
        vec![2, 0, 2], vec![2, 1, 3], vec![2, 2, 0], vec![2, 3, 1],
        vec![3, 0, 3], vec![3, 1, 2], vec![3, 2, 1], vec![3, 3, 0],
    ];
    println!("    create_problematic_algebra: Table created");
    
    let op = TableOperation::new(op_symbol, op_table, 4)?;
    println!("    create_problematic_algebra: TableOperation created");
    algebra.add_operation("f".to_string(), Arc::new(Mutex::new(op)))?;
    println!("    create_problematic_algebra: Operation added to algebra");
    
    Ok(algebra)
}

#[test]
fn test_malcev_analyzer_segfault_reproduction() {
    println!("test_malcev_analyzer_segfault_reproduction: Starting test");
    
    // Create the problematic algebra
    let algebra = match create_problematic_algebra() {
        Ok(alg) => {
            println!("test_malcev_analyzer_segfault_reproduction: Algebra created successfully");
            alg
        },
        Err(e) => {
            panic!("Failed to create algebra: {}", e);
        }
    };
    
    println!("test_malcev_analyzer_segfault_reproduction: Algebra cardinality: {}", algebra.cardinality());
    
    // Create MalcevAnalyzer
    let mut analyzer = MalcevAnalyzer::new();
    println!("test_malcev_analyzer_segfault_reproduction: MalcevAnalyzer created");
    
    // This should trigger the segfault/memory issue
    println!("test_malcev_analyzer_segfault_reproduction: About to call analyze_malcev_conditions");
    let start_time = Instant::now();
    
    match analyzer.analyze_malcev_conditions(&algebra) {
        Ok(analysis) => {
            let duration = start_time.elapsed();
            println!("test_malcev_analyzer_segfault_reproduction: Analysis completed in {:?}", duration);
            println!("test_malcev_analyzer_segfault_reproduction: Analysis result: {:?}", analysis);
            
            // The test should fail if it takes too long (indicating the issue)
            if duration > Duration::from_secs(5) {
                panic!("Analysis took too long ({:?}), indicating the segfault/memory issue", duration);
            }
        },
        Err(e) => {
            let duration = start_time.elapsed();
            println!("test_malcev_analyzer_segfault_reproduction: Analysis failed after {:?}: {}", duration, e);
            
            // Check if it's a memory limit error (expected)
            if e.to_string().contains("MemoryLimitExceeded") {
                println!("test_malcev_analyzer_segfault_reproduction: Got expected memory limit error");
                return; // This is expected
            }
            
            // If it's not a memory limit error, it might be the segfault
            panic!("Unexpected error: {}", e);
        }
    }
    
    println!("test_malcev_analyzer_segfault_reproduction: Test completed successfully");
}

#[test]
fn test_generate_argument_combinations_explosion() {
    println!("test_generate_argument_combinations_explosion: Starting test");
    
    use uacalc_core::utils::generate_argument_combinations;
    
    // Test with a small universe but high arity to trigger exponential explosion
    let universe = vec![0, 1, 2, 3]; // 4 elements
    let arity = 3; // This will generate 4^3 = 64 combinations
    
    println!("test_generate_argument_combinations_explosion: Generating combinations for universe {:?} with arity {}", universe, arity);
    let start_time = Instant::now();
    
    let combinations = generate_argument_combinations(&universe, arity);
    let duration = start_time.elapsed();
    
    println!("test_generate_argument_combinations_explosion: Generated {} combinations in {:?}", combinations.len(), duration);
    
    // This should be manageable
    assert_eq!(combinations.len(), 64);
    
    // Test with higher arity to see the explosion
    let arity_4 = 4; // This will generate 4^4 = 256 combinations
    println!("test_generate_argument_combinations_explosion: Testing arity 4 (should generate 256 combinations)");
    
    let combinations_4 = generate_argument_combinations(&universe, arity_4);
    println!("test_generate_argument_combinations_explosion: Generated {} combinations for arity 4", combinations_4.len());
    assert_eq!(combinations_4.len(), 256);
    
    println!("test_generate_argument_combinations_explosion: Test completed successfully");
}
