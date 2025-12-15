// Test to debug ProductOperation component ordering issue
#![allow(warnings)]

use uacalc::alg::{BasicAlgebra, SmallAlgebra, PowerAlgebra, Algebra};
use uacalc::alg::op::{IntOperation, OperationSymbol, Operation};
use uacalc::util::horner;
use std::collections::HashSet;

#[test]
fn test_power_algebra_join_idempotency() {
    // Create 2-element boolean algebra
    let mut universe = HashSet::new();
    universe.insert(0);
    universe.insert(1);
    
    // Join table: join(0,0)=0, join(0,1)=1, join(1,0)=1, join(1,1)=1
    // Table is Horner-encoded: for args [i, j], index = i * 2 + j
    let join_table = vec![
        0, 1,  // join(0,0)=0, join(0,1)=1
        1, 1,  // join(1,0)=1, join(1,1)=1
    ];
    
    let join_sym = OperationSymbol::new_safe("join", 2, false).unwrap();
    let join_op = IntOperation::new(join_sym, 2, join_table).unwrap();
    
    let ba2 = BasicAlgebra::new(
        "DistributiveLattice2".to_string(),
        universe,
        vec![Box::new(join_op)]
    );
    
    // Create power algebra with n=2
    let root = Box::new(ba2) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    let power_alg = PowerAlgebra::new_safe(root, 2).unwrap();
    
    // Get operations directly from PowerAlgebra
    let operations = power_alg.operations();
    let join_op_power = operations.iter()
        .find(|op| op.symbol().name() == "join")
        .expect("Join operation not found");
    
    // Test idempotency: join(x, x) should equal x
    let cardinality = power_alg.cardinality();
    for i in 0..cardinality {
        let result = join_op_power.int_value_at(&[i, i]).unwrap();
        assert_eq!(result, i, "join({}, {}) should equal {}, but got {}", i, i, i, result);
    }
}

#[test]
fn test_horner_encoding_decoding() {
    // Test that horner and horner_inv are inverses
    let sizes = vec![2, 2];
    
    for k in 0..4 {
        let decoded = horner::horner_inv(k, &sizes);
        let encoded = horner::horner(&decoded, &sizes);
        assert_eq!(encoded, k, "Encoding/decoding mismatch: {} -> {:?} -> {}", k, decoded, encoded);
    }
}

#[test]
fn test_component_extraction() {
    // Test what components we get when decoding element 1
    let sizes = vec![2, 2];
    let element_1 = 1;
    let decoded = horner::horner_inv(element_1, &sizes);
    
    // Element 1 should decode to [1, 0] where:
    // - decoded[0] = 1 (component 0, least significant, first algebra)
    // - decoded[1] = 0 (component 1, most significant, second algebra)
    assert_eq!(decoded, vec![1, 0], "Element 1 should decode to [1, 0]");
    
    // When we compute join(1, 1), we should get:
    // - Component 0: join(1, 1) = 1
    // - Component 1: join(0, 0) = 0
    // Result should be [1, 0] which encodes to 1
    let result_components = vec![1, 0];
    let encoded_result = horner::horner(&result_components, &sizes);
    assert_eq!(encoded_result, 1, "Result [1, 0] should encode to 1");
}

#[test]
fn test_manual_computation() {
    // Manually trace through what should happen for join(1, 1)
    let sizes = vec![2, 2];
    
    // Decode element 1
    let args_expanded_0 = horner::horner_inv(1, &sizes); // [1, 0]
    let args_expanded_1 = horner::horner_inv(1, &sizes); // [1, 0]
    
    println!("args_expanded[0] = {:?}", args_expanded_0);
    println!("args_expanded[1] = {:?}", args_expanded_1);
    
    // Join table: join(0,0)=0, join(0,1)=1, join(1,0)=1, join(1,1)=1
    let join_table = |i: i32, j: i32| -> i32 {
        if i == 0 && j == 0 { 0 }
        else if i == 0 && j == 1 { 1 }
        else if i == 1 && j == 0 { 1 }
        else { 1 } // i == 1 && j == 1
    };
    
    // When iterating in reverse (i = 1, then i = 0):
    // i = 1 (most significant, second algebra):
    //   component_args = [args_expanded[0][1], args_expanded[1][1]] = [0, 0]
    //   result = join(0, 0) = 0
    //   ans = sizes[1] * 0 + 0 = 2 * 0 + 0 = 0
    let i = 1;
    let comp_args_i1 = vec![args_expanded_0[i as usize], args_expanded_1[i as usize]];
    let result_i1 = join_table(comp_args_i1[0], comp_args_i1[1]);
    let mut ans = sizes[i as usize] * 0 + result_i1;
    println!("i={}: component_args={:?}, result={}, ans={}", i, comp_args_i1, result_i1, ans);
    
    // i = 0 (least significant, first algebra):
    //   component_args = [args_expanded[0][0], args_expanded[1][0]] = [1, 1]
    //   result = join(1, 1) = 1
    //   ans = sizes[0] * 0 + 1 = 2 * 0 + 1 = 1
    let i = 0;
    let comp_args_i0 = vec![args_expanded_0[i as usize], args_expanded_1[i as usize]];
    let result_i0 = join_table(comp_args_i0[0], comp_args_i0[1]);
    ans = sizes[i as usize] * ans + result_i0;
    println!("i={}: component_args={:?}, result={}, ans={}", i, comp_args_i0, result_i0, ans);
    
    assert_eq!(ans, 1, "join(1, 1) should equal 1, but got {}", ans);
}

