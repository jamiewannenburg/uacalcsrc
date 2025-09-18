use uacalc_core::algebra::BasicAlgebra;
use uacalc_core::malcev::MalcevAnalyzer;
use uacalc_core::io::AlgebraReader;
use std::sync::{Arc, Mutex};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Testing Rust vs Java majority term implementation...");
    
    // Test with the 2-element Boolean algebra
    let algebra_file = "resources/algebras/ba2.ua";
    println!("Loading algebra from: {}", algebra_file);
    
    let algebra = AlgebraReader::read_algebra_file(algebra_file)?;
    println!("Loaded algebra: {} (size: {})", algebra.name(), algebra.cardinality());
    
    // Test majority term computation
    println!("\nTesting Rust implementation...");
    let start_time = std::time::Instant::now();
    let mut analyzer = MalcevAnalyzer::new();
    let analysis = analyzer.analyze_malcev_conditions(&algebra)?;
    let end_time = start_time.elapsed();
    
    println!("Rust results:");
    println!("  - has_majority_term: {}", analysis.has_majority_term);
    println!("  - has_malcev_term: {}", analysis.has_malcev_term);
    println!("  - has_join_term: {}", analysis.has_join_term);
    println!("  - congruence_modular: {}", analysis.congruence_modular);
    println!("  - congruence_distributive: {}", analysis.congruence_distributive);
    println!("  - analysis_completed: {}", analysis.analysis_completed);
    println!("  - computation time: {:?}", end_time);
    
    // Expected Java results for ba2.ua:
    // - has_majority_term: true (found term: join(meet(x,y),join(meet(x,z),meet(y,z))))
    // - has_malcev_term: false (Boolean algebras don't have Malcev terms)
    // - has_join_term: true (Boolean algebras have join terms)
    // - congruence_modular: true (Boolean algebras are modular)
    // - congruence_distributive: true (Boolean algebras are distributive)
    
    println!("\nExpected Java results for ba2.ua:");
    println!("  - has_majority_term: true");
    println!("  - has_malcev_term: false");
    println!("  - has_join_term: true");
    println!("  - congruence_modular: true");
    println!("  - congruence_distributive: true");
    
    // Check if results match
    let majority_matches = analysis.has_majority_term == true;
    let malcev_matches = analysis.has_malcev_term == false;
    let join_matches = analysis.has_join_term == true;
    let modular_matches = analysis.congruence_modular == true;
    let distributive_matches = analysis.congruence_distributive == true;
    
    println!("\nComparison:");
    println!("  - has_majority_term: {} (expected: true)", if majority_matches { "✓" } else { "✗" });
    println!("  - has_malcev_term: {} (expected: false)", if malcev_matches { "✓" } else { "✗" });
    println!("  - has_join_term: {} (expected: true)", if join_matches { "✓" } else { "✗" });
    println!("  - congruence_modular: {} (expected: true)", if modular_matches { "✓" } else { "✗" });
    println!("  - congruence_distributive: {} (expected: true)", if distributive_matches { "✓" } else { "✗" });
    
    let all_match = majority_matches && malcev_matches && join_matches && modular_matches && distributive_matches;
    println!("\nOverall result: {}", if all_match { "✓ All tests pass!" } else { "✗ Some tests failed" });
    
    Ok(())
}
