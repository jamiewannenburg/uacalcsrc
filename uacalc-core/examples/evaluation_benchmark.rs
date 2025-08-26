use uacalc_core::prelude::*;
use uacalc_core::algebra::BasicAlgebra;
use uacalc_core::operation::OperationSymbol;
use uacalc_core::term::evaluation::{EvaluationContext, EvaluationStats};
use std::time::Instant;

fn main() {
    println!("UACalc Term Evaluation Benchmark - Zero Allocation Refactoring");
    println!("=============================================================\n");

    // Create a test algebra
    let algebra = BasicAlgebra::with_cardinality("benchmark".to_string(), 5).unwrap();
    
    // Create a complex term structure to test evaluation performance
    let mut arena = TermArena::new();
    
    // Build a deep term tree with shared subterms
    let x0 = arena.make_variable(0);
    let x1 = arena.make_variable(1);
    let x2 = arena.make_variable(2);
    
    // Create some operation symbols
    let f_sym = OperationSymbol::new("f".to_string(), 2);
    let g_sym = OperationSymbol::new("g".to_string(), 1);
    let h_sym = OperationSymbol::new("h".to_string(), 3);
    
    // Build a complex term: h(f(x0,x1), g(f(x1,x2)), f(x2,x0))
    let f1 = arena.make_term(&f_sym, &[x0, x1]);
    let f2 = arena.make_term(&f_sym, &[x1, x2]);
    let f3 = arena.make_term(&f_sym, &[x2, x0]);
    let g1 = arena.make_term(&g_sym, &[f2]);
    let complex_term = arena.make_term(&h_sym, &[f1, g1, f3]);
    
    println!("Term structure:");
    println!("  Variables: x0, x1, x2");
    println!("  Operations: f(2-ary), g(1-ary), h(3-ary)");
    println!("  Complex term: h(f(x0,x1), g(f(x1,x2)), f(x2,x0))");
    println!("  Total terms in arena: {}", arena.num_terms());
    println!();

    // Test variable assignments
    let assignments = vec![
        vec![0, 1, 2],
        vec![1, 2, 3],
        vec![2, 3, 4],
        vec![3, 4, 0],
        vec![4, 0, 1],
    ];

    println!("Performance Benchmark:");
    println!("=====================");

    let mut total_time = 0;
    let num_iterations = 1000;

    for (i, assignment) in assignments.iter().enumerate() {
        let variables = VariableAssignment::from_values(assignment.clone());
        
        // Warm up
        let mut context = EvaluationContext::new(&algebra, &variables);
        let _warmup = context.eval_term(complex_term, &arena);
        
        // Benchmark
        let start = Instant::now();
        for _ in 0..num_iterations {
            let mut context = EvaluationContext::new(&algebra, &variables);
            let result = context.eval_term(complex_term, &arena);
            assert!(result.is_ok());
        }
        let duration = start.elapsed();
        total_time += duration.as_micros();
        
        println!("  Assignment {}: {:?} -> {} evaluations in {:?} ({:.2} μs/iter)", 
                i + 1, assignment, num_iterations, duration, duration.as_micros() as f64 / num_iterations as f64);
        
        // Show memory stats for the last iteration
        let mut context = EvaluationContext::new(&algebra, &variables);
        let _result = context.eval_term(complex_term, &arena);
        let stats = context.memory_stats();
        println!("    Memory stats: cache_size={}, stack_size={}, max_arity={}", 
                stats.cache_size, stats.stack_size, stats.max_arity);
    }

    println!("\nSummary:");
    println!("  Total time: {} μs", total_time);
    println!("  Average time per evaluation: {:.2} μs", total_time as f64 / (assignments.len() * num_iterations) as f64);
    println!("  Zero-allocation optimizations:");
    println!("    ✓ Stack-allocated ArrayVec for evaluation stack");
    println!("    ✓ Vec<Option<usize>> for results cache (indexed by TermId)");
    println!("    ✓ ArrayVec for operation arguments (up to MAX_OPERATION_ARITY)");
    println!("    ✓ Pre-validated term arities");
    println!("    ✓ Compact StackFrame struct");
}
