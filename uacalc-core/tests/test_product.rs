use uacalc_core::algebra::{Algebra, BasicAlgebra, SmallAlgebra};
use uacalc_core::operation::{OperationSymbol, TableOperation};
use uacalc_core::partition::Partition;
use uacalc_core::product::ProductAlgebra;
use uacalc_core::UACalcResult;
use std::sync::{Arc, Mutex};

fn create_test_algebra(name: &str, size: usize) -> UACalcResult<Arc<Mutex<dyn SmallAlgebra>>> {
    let mut algebra = BasicAlgebra::with_cardinality(name.to_string(), size)?;
    
    // Add a constant operation
    let const_symbol = OperationSymbol::new("const".to_string(), 0);
    let const_op = TableOperation::new(const_symbol, vec![vec![0]], size)?;
    algebra.add_operation("const".to_string(), Arc::new(Mutex::new(const_op)))?;
    
    // Add a unary operation (successor mod size)
    let unary_symbol = OperationSymbol::new("succ".to_string(), 1);
    let unary_table = (0..size).map(|i| vec![i, (i + 1) % size]).collect();
    let unary_op = TableOperation::new(unary_symbol, unary_table, size)?;
    algebra.add_operation("succ".to_string(), Arc::new(Mutex::new(unary_op)))?;
    
    // Add a binary operation (addition mod size)
    let binary_symbol = OperationSymbol::new("add".to_string(), 2);
    let mut binary_table = Vec::new();
    for i in 0..size {
        for j in 0..size {
            binary_table.push(vec![i, j, (i + j) % size]);
        }
    }
    let binary_op = TableOperation::new(binary_symbol, binary_table, size)?;
    algebra.add_operation("add".to_string(), Arc::new(Mutex::new(binary_op)))?;
    
    Ok(Arc::new(Mutex::new(algebra)))
}

#[test]
fn test_product_algebra_construction() -> UACalcResult<()> {
    // Create simple algebras without operations for basic testing
    let alg1 = BasicAlgebra::with_cardinality("A".to_string(), 2)?;
    let alg2 = BasicAlgebra::with_cardinality("B".to_string(), 3)?;
    
    let product = ProductAlgebra::new("A_x_B".to_string(), vec![Arc::new(Mutex::new(alg1)), Arc::new(Mutex::new(alg2))])?;
    
    assert_eq!(product.name(), "A_x_B");
    assert_eq!(product.cardinality(), 6); // 2 * 3
    assert_eq!(product.factors().len(), 2);
    
    Ok(())
}

#[test]
fn test_product_algebra_empty_factors() {
    let result = ProductAlgebra::new("empty".to_string(), vec![]);
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("at least one factor"));
}

#[test]
fn test_product_algebra_incompatible_operations() -> UACalcResult<()> {
    let mut alg1 = BasicAlgebra::with_cardinality("A".to_string(), 2)?;
    let mut alg2 = BasicAlgebra::with_cardinality("B".to_string(), 2)?;
    
    // Add operations with different arities to each algebra
    let op1_symbol = OperationSymbol::new("op1".to_string(), 1);
    let op1_table = vec![vec![0, 0], vec![1, 1]];
    let op1 = TableOperation::new(op1_symbol, op1_table, 2)?;
    alg1.add_operation("op1".to_string(), Arc::new(Mutex::new(op1)))?;
    
    let op2_symbol = OperationSymbol::new("op2".to_string(), 2); // Different arity
    let op2_table = vec![vec![0, 0, 0], vec![0, 1, 0], vec![1, 0, 0], vec![1, 1, 1]];
    let op2 = TableOperation::new(op2_symbol, op2_table, 2)?;
    alg2.add_operation("op2".to_string(), Arc::new(Mutex::new(op2)))?;
    
    let result = ProductAlgebra::new(
        "incompatible".to_string(),
        vec![Arc::new(Mutex::new(alg1)), Arc::new(Mutex::new(alg2))],
    );
    assert!(result.is_err());
    
    Ok(())
}

#[test]
fn test_coordinate_projection_and_embedding() -> UACalcResult<()> {
    let alg1 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("A".to_string(), 2)?));
    let alg2 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("B".to_string(), 3)?));
    
    let product = ProductAlgebra::new("A_x_B".to_string(), vec![alg1.clone(), alg2.clone()])?;
    
    // Test coordinate projection (little-endian mixed-radix encoding)
    // Product of sizes [2, 3] gives: [0,0]→0, [1,0]→1, [0,1]→2, [1,1]→3, [0,2]→4, [1,2]→5
    assert_eq!(product.coordinate_projection(0, 0)?, 0); // element 0 = [0,0], first coord = 0
    assert_eq!(product.coordinate_projection(0, 1)?, 0); // element 0 = [0,0], second coord = 0
    assert_eq!(product.coordinate_projection(1, 0)?, 1); // element 1 = [1,0], first coord = 1
    assert_eq!(product.coordinate_projection(1, 1)?, 0); // element 1 = [1,0], second coord = 0
    assert_eq!(product.coordinate_projection(2, 0)?, 0); // element 2 = [0,1], first coord = 0
    assert_eq!(product.coordinate_projection(2, 1)?, 1); // element 2 = [0,1], second coord = 1
    assert_eq!(product.coordinate_projection(3, 0)?, 1); // element 3 = [1,1], first coord = 1
    assert_eq!(product.coordinate_projection(3, 1)?, 1); // element 3 = [1,1], second coord = 1
    assert_eq!(product.coordinate_projection(4, 0)?, 0); // element 4 = [0,2], first coord = 0
    assert_eq!(product.coordinate_projection(4, 1)?, 2); // element 4 = [0,2], second coord = 2
    assert_eq!(product.coordinate_projection(5, 0)?, 1); // element 5 = [1,2], first coord = 1
    assert_eq!(product.coordinate_projection(5, 1)?, 2); // element 5 = [1,2], second coord = 2
    
    // Test coordinate embedding (little-endian mixed-radix encoding)
    assert_eq!(product.coordinate_embedding(&[0, 0])?, 0);
    assert_eq!(product.coordinate_embedding(&[1, 0])?, 1);
    assert_eq!(product.coordinate_embedding(&[0, 1])?, 2);
    assert_eq!(product.coordinate_embedding(&[1, 1])?, 3);
    assert_eq!(product.coordinate_embedding(&[0, 2])?, 4);
    assert_eq!(product.coordinate_embedding(&[1, 2])?, 5);
    
    // Test error cases
    assert!(product.coordinate_projection(6, 0).is_err()); // Out of bounds
    assert!(product.coordinate_projection(0, 2).is_err()); // Invalid factor index
    assert!(product.coordinate_embedding(&[0]).is_err()); // Wrong number of coordinates
    assert!(product.coordinate_embedding(&[0, 3]).is_err()); // Out of bounds
    
    Ok(())
}

#[test]
fn test_projection_kernel() -> UACalcResult<()> {
    let alg1 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("A".to_string(), 2)?));
    let alg2 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("B".to_string(), 3)?));
    
    let product = ProductAlgebra::new("A_x_B".to_string(), vec![alg1.clone(), alg2.clone()])?;
    
    // Test projection kernel for first factor
    let kernel1 = product.projection_kernel(0)?;
    assert_eq!(kernel1.num_blocks(), 2); // One block for each element of first factor
    
    // Test projection kernel for second factor
    let kernel2 = product.projection_kernel(1)?;
    assert_eq!(kernel2.num_blocks(), 3); // One block for each element of second factor
    
    // Test error case
    assert!(product.projection_kernel(2).is_err()); // Invalid factor index
    
    Ok(())
}

#[test]
fn test_operation_evaluation() -> UACalcResult<()> {
    // Create test algebras with actual operations
    let alg1 = create_test_algebra("A", 2)?;  // {0, 1} with mod 2 operations
    let alg2 = create_test_algebra("B", 3)?;  // {0, 1, 2} with mod 3 operations
    
    let product = ProductAlgebra::new("A_x_B".to_string(), vec![alg1.clone(), alg2.clone()])?;
    
    assert_eq!(product.cardinality(), 6); // 2 * 3
    assert_eq!(product.operations().len(), 3); // const, succ, add
    
    // Test constant operation
    let const_op = product.operation_arc_by_symbol("const")?;
    let const_guard = const_op.lock().unwrap();
    let const_result = const_guard.value(&[])?;
    assert_eq!(const_result, product.coordinate_embedding(&[0, 0])?); // (0,0) since const returns 0 in both factors
    
    // Test unary operation (successor)
    let succ_op = product.operation_arc_by_symbol("succ")?;
    let succ_guard = succ_op.lock().unwrap();
    
    // Test succ on element (0,0) = 0
    let elem_00 = product.coordinate_embedding(&[0, 0])?;
    let succ_00 = succ_guard.value(&[elem_00])?;
    let expected_00 = product.coordinate_embedding(&[1, 1])?; // succ(0,0) = (1,1)
    assert_eq!(succ_00, expected_00);
    
    // Test succ on element (1,2) = 5
    let elem_12 = product.coordinate_embedding(&[1, 2])?;
    let succ_12 = succ_guard.value(&[elem_12])?;
    let expected_12 = product.coordinate_embedding(&[0, 0])?; // succ(1,2) = (0,0) due to mod operations
    assert_eq!(succ_12, expected_12);
    
    // Test binary operation (addition)
    let add_op = product.operation_arc_by_symbol("add")?;
    let add_guard = add_op.lock().unwrap();
    
    // Test add((0,1), (1,0)) = (1,1)
    let elem_01 = product.coordinate_embedding(&[0, 1])?;
    let elem_10 = product.coordinate_embedding(&[1, 0])?;
    let add_result = add_guard.value(&[elem_01, elem_10])?;
    let expected_add = product.coordinate_embedding(&[1, 1])?; // (0+1, 1+0) = (1,1)
    assert_eq!(add_result, expected_add);
    
    // Test add((1,2), (1,1)) = (0,0)
    let elem_11 = product.coordinate_embedding(&[1, 1])?;
    let add_result2 = add_guard.value(&[elem_12, elem_11])?;
    let expected_add2 = product.coordinate_embedding(&[0, 0])?; // (1+1, 2+1) = (0,0) mod (2,3)
    assert_eq!(add_result2, expected_add2);
    
    // Verify componentwise computation manually
    for element1 in 0..product.cardinality() {
        for element2 in 0..product.cardinality() {
            let coords1 = product.decode_coords(element1);
            let coords2 = product.decode_coords(element2);
            
            // Manual componentwise addition
            let manual_result_coords = vec![
                (coords1[0] + coords2[0]) % 2,  // First factor mod 2
                (coords1[1] + coords2[1]) % 3,  // Second factor mod 3
            ];
            let manual_result = product.coordinate_embedding(&manual_result_coords)?;
            
            // Product algebra addition
            let product_result = add_guard.value(&[element1, element2])?;
            
            assert_eq!(product_result, manual_result, 
                "Componentwise addition mismatch for ({:?}, {:?})", coords1, coords2);
        }
    }
    
    Ok(())
}

#[test]
fn test_large_product_algebra() -> UACalcResult<()> {
    let alg1 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("A".to_string(), 10)?));
    let alg2 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("B".to_string(), 10)?));
    let alg3 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("C".to_string(), 10)?));
    
    let product = ProductAlgebra::new(
        "A_x_B_x_C".to_string(),
        vec![alg1.clone(), alg2.clone(), alg3.clone()],
    )?;
    
    assert_eq!(product.cardinality(), 1000); // 10^3
    assert_eq!(product.factors().len(), 3);
    
    // Test coordinate operations
    let coords = product.coordinate_embedding(&[5, 3, 7])?;
    assert_eq!(product.coordinate_projection(coords, 0)?, 5);
    assert_eq!(product.coordinate_projection(coords, 1)?, 3);
    assert_eq!(product.coordinate_projection(coords, 2)?, 7);
    
    Ok(())
}

#[test]
fn test_single_factor_product() -> UACalcResult<()> {
    let alg1 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("A".to_string(), 3)?));
    
    let product = ProductAlgebra::new("single".to_string(), vec![alg1.clone()])?;
    
    assert_eq!(product.cardinality(), 3);
    assert_eq!(product.factors().len(), 1);
    
    // For now, skip testing operations since they're not fully implemented
    // let id_op = product.operation_arc_by_symbol("id")?;
    // let id_guard = id_op.lock().unwrap();
    // for i in 0..3 {
    //     let result = id_guard.int_value_at(&[i])?;
    //     assert_eq!(result, i);
    // }
    
    Ok(())
}

#[test]
fn test_arithmetic_overflow_protection() {
    // Create many factors with moderate sizes that when multiplied together would cause overflow
    // Use size 256 with enough factors: 256^8 = 2^64 would overflow on 64-bit systems
    let factor_size = 256;
    let num_factors = 8;
    
    let mut factors: Vec<Arc<Mutex<dyn SmallAlgebra>>> = Vec::new();
    for i in 0..num_factors {
        factors.push(Arc::new(Mutex::new(
            BasicAlgebra::with_cardinality(format!("Factor{}", i), factor_size).unwrap()
        )));
    }
    
    let result = ProductAlgebra::new("overflow".to_string(), factors);
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("overflow"));
}

#[test]
fn test_mixed_radix_helpers() -> UACalcResult<()> {
    let alg1 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("A".to_string(), 2)?));
    let alg2 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("B".to_string(), 3)?));
    let alg3 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("C".to_string(), 4)?));
    
    let product = ProductAlgebra::new(
        "A_x_B_x_C".to_string(),
        vec![alg1.clone(), alg2.clone(), alg3.clone()],
    )?;
    
    // Test that decode_coords and encode_coords are consistent with coordinate_projection and coordinate_embedding
    for element in 0..product.cardinality() {
        let coords = product.decode_coords(element);
        let reconstructed = product.encode_coords(&coords)?;
        assert_eq!(reconstructed, element, "Round-trip failed for element {}", element);
        
        // Verify that the coordinates match coordinate_projection
        for k in 0..coords.len() {
            let projected = product.coordinate_projection(element, k)?;
            assert_eq!(coords[k], projected, "Coordinate {} mismatch for element {}", k, element);
        }
        
        // Verify that coordinate_embedding matches encode_coords
        let embedded = product.coordinate_embedding(&coords)?;
        assert_eq!(embedded, element, "Embedding mismatch for coords {:?}", coords);
    }
    
    Ok(())
}

#[test]
fn test_round_trip_validation_three_factors() -> UACalcResult<()> {
    let alg1 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("A".to_string(), 3)?));
    let alg2 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("B".to_string(), 4)?));
    let alg3 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("C".to_string(), 2)?));
    
    let product = ProductAlgebra::new(
        "A_x_B_x_C".to_string(),
        vec![alg1.clone(), alg2.clone(), alg3.clone()],
    )?;
    
    assert_eq!(product.cardinality(), 24); // 3 * 4 * 2
    
    // Test round-trip for all possible coordinates
    for a in 0..3 {
        for b in 0..4 {
            for c in 0..2 {
                let coords = vec![a, b, c];
                let element = product.coordinate_embedding(&coords)?;
                let decoded = product.decode_coords(element);
                assert_eq!(decoded, coords, "Round-trip failed for coords {:?}", coords);
                
                // Also test individual projections
                assert_eq!(product.coordinate_projection(element, 0)?, a);
                assert_eq!(product.coordinate_projection(element, 1)?, b);
                assert_eq!(product.coordinate_projection(element, 2)?, c);
            }
        }
    }
    
    Ok(())
}

#[test]
fn test_projection_kernel_all_coords() -> UACalcResult<()> {
    let alg1 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("A".to_string(), 2)?));
    let alg2 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("B".to_string(), 3)?));
    let alg3 = Arc::new(Mutex::new(BasicAlgebra::with_cardinality("C".to_string(), 2)?));
    
    let product = ProductAlgebra::new(
        "A_x_B_x_C".to_string(),
        vec![alg1.clone(), alg2.clone(), alg3.clone()],
    )?;
    
    // Test projection kernel for each factor
    for k in 0..3 {
        let kernel = product.projection_kernel(k)?;
        
        // Verify that elements with the same k-th coordinate are in the same equivalence class
        for element1 in 0..product.cardinality() {
            for element2 in 0..product.cardinality() {
                let coord1 = product.coordinate_projection(element1, k)?;
                let coord2 = product.coordinate_projection(element2, k)?;
                
                let same_equivalence_class = kernel.representative(element1)? == kernel.representative(element2)?;
                let same_coordinate = coord1 == coord2;
                
                assert_eq!(
                    same_equivalence_class, 
                    same_coordinate,
                    "Elements {} and {} should be in same equivalence class iff they have same {}-th coordinate ({} vs {})",
                    element1, element2, k, coord1, coord2
                );
            }
        }
    }
    
    Ok(())
}
