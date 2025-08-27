use uacalc_core::prelude::*;

#[cfg(feature = "conlat")]
#[test]
fn test_principal_cache_after_sorting() {
    // Test that principal cache indices remain correct after sorting join-irreducibles
    let algebra = create_test_algebra();
    let mut builder = LatticeBuilder::new(&algebra);
    
    // Build the universe to trigger join-irreducible finding and sorting
    let _universe = builder.build_universe().unwrap();
    
    // Verify that principal cache entries point to correct join-irreducibles
    for ((a, b), ji_index) in &builder.principal_cache {
        let principal = builder.principal_congruence_cache()
            .get_principal_congruence(*a, *b)
            .unwrap();
        
        // The cached index should point to the correct join-irreducible
        assert_eq!(&builder.join_irreducibles[*ji_index], principal);
    }
}

fn create_test_algebra() -> impl SmallAlgebra {
    // Create a simple test algebra for testing
    use uacalc_core::algebra::BasicAlgebra;
    use uacalc_core::operation::Operation;
    
    let size = 4;
    let mut algebra = BasicAlgebra::new(size);
    
    // Add a simple binary operation
    let mut table = vec![0; size * size];
    for i in 0..size {
        for j in 0..size {
            table[i * size + j] = (i + j) % size;
        }
    }
    
    let op = Operation::from_table("test_op".to_string(), 2, table).unwrap();
    algebra.add_operation(op);
    
    algebra
}
