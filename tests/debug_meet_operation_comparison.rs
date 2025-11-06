/*!
 * Debug test comparing Rust and Java implementations of meet operation
 * on F(1)^3 power algebra.
 * 
 * This test prints detailed step-by-step information to identify where
 * the implementations diverge.
 */

use uacalc::alg::{FreeAlgebra, SmallAlgebra, BigProductAlgebra, Algebra};
use uacalc::util::int_array::{IntArray, IntArrayTrait};
use uacalc::io::algebra_io::read_algebra_file;
use std::path::Path;
use serde_json::json;
use uacalc::common::*;

fn create_ba2() -> Box<dyn SmallAlgebra<UniverseItem = i32>> {
    let alg_file = Path::new("resources/algebras/ba2.ua");
    if !alg_file.exists() {
        panic!("ba2.ua not found at {}", alg_file.display());
    }
    
    let base_alg = read_algebra_file(alg_file).expect("Failed to load ba2.ua");
    
    use uacalc::alg::op::ops::make_int_operations;
    use uacalc::alg::BasicAlgebra;
    
    let card = base_alg.cardinality();
    let ops = base_alg.operations();
    let int_ops = make_int_operations(ops).expect("Failed to create int operations");
    let universe: std::collections::HashSet<i32> = (0..card).collect();
    
    Box::new(BasicAlgebra::new(
        base_alg.name().to_string(),
        universe,
        int_ops,
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>
}

#[test]
fn test_meet_operation_debug_comparison() {
    let _config = TestConfig {
        verbose: true,
        ..Default::default()
    };
    
    // Create F(1) and F(1)^3 in Rust
    let f1 = FreeAlgebra::new_safe(create_ba2(), 1).expect("Failed to create F(1)");
    
    println!("\n=== RUST DEBUG INFO ===");
    let f1_cardinality = f1.cardinality();
    println!("F(1) cardinality: {}", f1_cardinality);
    
    // Get F(1) universe
    let f1_univ_list = f1.get_universe_list();
    if let Some(ref univ_list) = f1_univ_list {
        println!("F(1) universe ({} elements):", univ_list.len());
        for (i, elem) in univ_list.iter().enumerate() {
            println!("  Index {}: {:?}", i, elem.as_slice());
        }
    }
    
    // Get F(1) operations
    let f1_ops = f1.operations();
    println!("\nF(1) operations ({}):", f1_ops.len());
    for op in &f1_ops {
        println!("  {} (arity {})", op.symbol().name(), op.arity());
    }
    
    // Test meet on F(1) directly
    if let Some(meet_op_f1) = f1_ops.iter().find(|op| op.symbol().name() == "meet") {
        println!("\nTesting meet on F(1) directly:");
        for i in 0..3 {
            for j in 0..3 {
                if let Ok(result) = meet_op_f1.int_value_at(&[i, j]) {
                    if let Some(ref univ_list) = f1_univ_list {
                        let result_elem = &univ_list[result as usize];
                        println!("  meet({}, {}) = {} (element {:?})", i, j, result, result_elem.as_slice());
                    }
                }
            }
        }
    }
    
    // Create F(1)^3 - need to clone f1 since we'll use it later
    let f1_boxed: Box<dyn SmallAlgebra<UniverseItem = IntArray>> = 
        Box::new(f1.clone()) as Box<dyn SmallAlgebra<UniverseItem = IntArray>>;
    let f1_power3 = BigProductAlgebra::new_power_safe(f1_boxed, 3).expect("Failed to create F(1)^3");
    
    println!("\nF(1)^3 created successfully");
    println!("Number of factors: {}", f1_power3.get_number_of_factors());
    
    // Get meet operation for F(1)^3
    let ops_power3 = f1_power3.operations();
    let meet_op = ops_power3.iter().find(|op| op.symbol().name() == "meet")
        .expect("meet operation should exist");
    
    println!("\nTesting meet([0,0,1], [1,1,0]) on F(1)^3:");
    let arg0 = vec![0, 0, 1];
    let arg1 = vec![1, 1, 0];
    let args: Vec<&[i32]> = vec![&arg0, &arg1];
    
    println!("  Arguments: {:?}, {:?}", arg0, arg1);
    
    match meet_op.value_at_arrays(&args) {
        Ok(result) => {
            println!("  Result: {:?}", result);
            println!("  Expected: [0, 0, 0]");
            if result != vec![0, 0, 0] {
                println!("  *** MISMATCH ***");
            } else {
                println!("  ✓ Correct!");
            }
        }
        Err(e) => {
            println!("  Error: {}", e);
        }
    }
    
    // Create detailed debug output for Java comparison
    let rust_debug = json!({
        "f1_cardinality": f1_cardinality,
        "f1_universe": if let Some(ref univ_list) = f1_univ_list {
            univ_list.iter().map(|e| e.as_slice().to_vec()).collect::<Vec<_>>()
        } else {
            vec![]
        },
        "f1_meet_table": {
            // Create meet table for F(1)
            "rows": (0..3).map(|i| {
                (0..3).map(|j| {
                    if let Some(meet_op_f1) = f1_ops.iter().find(|op| op.symbol().name() == "meet") {
                        meet_op_f1.int_value_at(&[i, j]).unwrap_or(-1)
                    } else {
                        -1
                    }
                }).collect::<Vec<_>>()
            }).collect::<Vec<_>>()
        },
        "f1_power3_factors": f1_power3.get_number_of_factors(),
        "test_args": {
            "arg0": arg0,
            "arg1": arg1
        },
        "test_result": match meet_op.value_at_arrays(&args) {
            Ok(r) => r,
            Err(_e) => vec![],
        },
        "expected_result": vec![0, 0, 0]
    });
    
    // Print detailed debug output
    println!("\n=== DETAILED DEBUG OUTPUT ===");
    println!("{}", serde_json::to_string_pretty(&rust_debug).unwrap());
    
    // Compare with Java
    compare_with_java!(
        _config,
        "java_wrapper.src.alg.DebugMeetOperationWrapper",
        ["debug_meet"],
        || rust_debug
    );
}

