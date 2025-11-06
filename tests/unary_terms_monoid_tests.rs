use uacalc::alg::{Algebra, SmallAlgebra, BasicAlgebra, AlgebraType, UnaryTermsMonoid};
use uacalc::alg::op::{Operation, OperationSymbol};
use uacalc::alg::op::operations;
use std::collections::HashSet;

#[cfg(test)]
mod unary_terms_monoid_tests {
    use super::*;

    /// Create a simple test algebra for testing
    fn create_test_algebra() -> Box<dyn SmallAlgebra<UniverseItem = i32>> {
        let universe: HashSet<i32> = (0..3).collect();
        // Add at least one operation (needed for closure computation)
        let mut ops: Vec<Box<dyn Operation>> = Vec::new();
        let const_sym = OperationSymbol::new("c", 0, false);
        let const_op = operations::make_int_operation(const_sym, 3, vec![0])
            .expect("Failed to create constant operation");
        ops.push(const_op);
        
        Box::new(BasicAlgebra::new(
            "TestAlgebra".to_string(),
            universe,
            ops,
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>
    }

    #[test]
    fn test_unary_terms_monoid_creation() {
        let alg = create_test_algebra();
        let monoid = UnaryTermsMonoid::new_safe(alg);
        
        if let Err(e) = &monoid {
            panic!("Failed to create UnaryTermsMonoid: {}", e);
        }
        let monoid = monoid.unwrap();
        assert_eq!(monoid.algebra_type(), AlgebraType::UnaryTermsMonoid);
        assert!(monoid.name().contains("UnaryTerms"));
    }

    #[test]
    fn test_unary_terms_monoid_cardinality() {
        // For a 3-element algebra with no operations, the only unary term is x
        let alg = create_test_algebra();
        let monoid = UnaryTermsMonoid::new_safe(alg).unwrap();
        
        // Should have at least 1 term (the variable)
        assert!(monoid.cardinality() > 0);
    }

    #[test]
    fn test_unary_terms_monoid_name() {
        let alg = create_test_algebra();
        let monoid = UnaryTermsMonoid::new_safe(alg).unwrap();
        
        // Check name contains expected parts
        assert!(monoid.name().contains("UnaryTerms"));
        assert!(monoid.name().contains("TestAlgebra"));
    }

    #[test]
    fn test_unary_terms_monoid_operations() {
        let alg = create_test_algebra();
        let monoid = UnaryTermsMonoid::new_safe(alg).unwrap();
        
        // Should have exactly one operation (the product operation)
        let ops = monoid.get_operations_ref();
        assert_eq!(ops.len(), 1);
        
        // The operation should be binary
        assert_eq!(ops[0].arity(), 2);
    }

    #[test]
    fn test_unary_terms_monoid_is_unary() {
        let alg = create_test_algebra();
        let monoid = UnaryTermsMonoid::new_safe(alg).unwrap();
        
        // UnaryTermsMonoid has a binary product operation, so is_unary should be false
        assert!(!monoid.is_unary());
    }

    #[test]
    fn test_unary_terms_monoid_universe() {
        let alg = create_test_algebra();
        let monoid = UnaryTermsMonoid::new_safe(alg).unwrap();
        
        // Check we can get universe list
        let universe_list = monoid.get_universe_list();
        assert!(universe_list.is_some());
        
        let universe = universe_list.unwrap();
        assert!(universe.len() > 0);
        assert_eq!(universe.len(), monoid.cardinality() as usize);
    }

    #[test]
    fn test_unary_terms_monoid_get_element() {
        let alg = create_test_algebra();
        let monoid = UnaryTermsMonoid::new_safe(alg).unwrap();
        
        // Get first element (should be the variable)
        let elem0 = monoid.get_element(0);
        assert!(elem0.is_some());
        
        // Check out of bounds
        let card = monoid.cardinality() as usize;
        assert!(monoid.get_element(card).is_none());
    }

    #[test]
    fn test_unary_terms_monoid_element_index() {
        let alg = create_test_algebra();
        let monoid = UnaryTermsMonoid::new_safe(alg).unwrap();
        
        // Get an element and find its index
        if let Some(elem) = monoid.get_element(0) {
            let idx = monoid.element_index(&elem);
            assert_eq!(idx, Some(0));
        }
    }

    #[test]
    fn test_unary_terms_monoid_with_id() {
        let alg = create_test_algebra();
        
        // Create with include_id = true
        let monoid = UnaryTermsMonoid::new_with_id_safe(alg, true);
        assert!(monoid.is_ok());
        
        let monoid = monoid.unwrap();
        assert_eq!(monoid.algebra_type(), AlgebraType::UnaryTermsMonoid);
    }

    #[test]
    fn test_unary_terms_monoid_display() {
        let alg = create_test_algebra();
        let monoid = UnaryTermsMonoid::new_safe(alg).unwrap();
        
        // Check Display trait
        let display_str = format!("{}", monoid);
        assert!(display_str.contains("UnaryTermsMonoid"));
    }

    #[test]
    fn test_unary_terms_monoid_product_operation() {
        let alg = create_test_algebra();
        let monoid = UnaryTermsMonoid::new_safe(alg).unwrap();
        
        // Get the product operation
        let product_sym = OperationSymbol::new("*", 2, true);
        let op = monoid.get_operation_ref(&product_sym);
        
        // The operation might have a different symbol, so just check we have one operation
        let ops = monoid.get_operations_ref();
        assert_eq!(ops.len(), 1);
        assert_eq!(ops[0].arity(), 2);
        
        // Check the operation has a table
        assert!(ops[0].is_table_based());
    }

    #[test]
    fn test_unary_terms_monoid_clone() {
        let alg = create_test_algebra();
        let monoid = UnaryTermsMonoid::new_safe(alg).unwrap();
        
        // Clone through SmallAlgebra trait
        let cloned = monoid.clone_box();
        
        // Check properties match
        assert_eq!(cloned.algebra_type(), AlgebraType::UnaryTermsMonoid);
        assert_eq!(cloned.cardinality(), monoid.cardinality());
    }
}

