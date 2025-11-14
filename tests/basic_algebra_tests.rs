use uacalc::alg::{Algebra, SmallAlgebra, BasicAlgebra, AlgebraType};
use std::collections::HashSet;
use serde_json::json;

#[cfg(test)]
mod basic_algebra_tests {
    use super::*;

    #[test]
    fn test_basic_algebra_creation() {
        // Create a simple algebra with integer universe
        let universe: HashSet<i32> = (0..5).collect();
        let operations = Vec::new();
        let alg = BasicAlgebra::new("test".to_string(), universe, operations);
        
        assert_eq!(alg.name(), "test");
        assert_eq!(alg.cardinality(), 5);
        assert_eq!(alg.algebra_type(), AlgebraType::Basic);
    }

    #[test]
    fn test_int_universe() {
        // Create algebra with integer universe
        let universe: HashSet<i32> = (0..5).collect();
        let operations = Vec::new();
        let alg = BasicAlgebra::new("test".to_string(), universe, operations);
        
        // Initially, universe list is not cached so int_universe returns true
        assert!(alg.int_universe());
    }

    #[test]
    fn test_get_element() {
        // Create algebra
        let universe: HashSet<i32> = (0..5).collect();
        let operations = Vec::new();
        let alg = BasicAlgebra::new("test".to_string(), universe, operations);
        
        // Get elements
        assert!(alg.get_element(0).is_some());
        assert!(alg.get_element(2).is_some());
        assert!(alg.get_element(4).is_some());
        
        // Out of bounds
        assert!(alg.get_element(10).is_none());
    }

    #[test]
    fn test_element_index() {
        // Create algebra
        let universe: HashSet<i32> = (0..5).collect();
        let operations = Vec::new();
        let alg = BasicAlgebra::new("test".to_string(), universe, operations);
        
        // Get indices
        let elem0 = alg.get_element(0).unwrap();
        let elem2 = alg.get_element(2).unwrap();
        
        assert_eq!(alg.element_index(&elem0), Some(0));
        assert_eq!(alg.element_index(&elem2), Some(2));
        
        // Non-existent element
        assert_eq!(alg.element_index(&100), None);
    }

    #[test]
    fn test_get_universe_list() {
        // Create algebra
        let universe: HashSet<i32> = (0..5).collect();
        let operations = Vec::new();
        let alg = BasicAlgebra::new("test".to_string(), universe, operations);
        
        // Get universe list
        let universe_list = alg.get_universe_list();
        assert!(universe_list.is_some());
        assert_eq!(universe_list.unwrap().len(), 5);
    }

    #[test]
    fn test_get_universe_order() {
        // Create algebra
        let universe: HashSet<i32> = (0..5).collect();
        let operations = Vec::new();
        let alg = BasicAlgebra::new("test".to_string(), universe, operations);
        
        // Get universe order
        let universe_order = alg.get_universe_order();
        assert!(universe_order.is_some());
        assert_eq!(universe_order.unwrap().len(), 5);
    }

    #[test]
    fn test_reset_universe_cache() {
        // Create algebra
        let universe: HashSet<i32> = (0..5).collect();
        let operations = Vec::new();
        let alg = BasicAlgebra::new("test".to_string(), universe, operations);
        
        // Access universe list to cache it
        let _ = alg.get_universe_list();
        assert!(!alg.int_universe());
        
        // Reset cache
        alg.reset_universe_cache();
        assert!(alg.int_universe());
    }

    #[test]
    fn test_algebra_type() {
        // Create algebra
        let universe: HashSet<i32> = (0..3).collect();
        let operations = Vec::new();
        let alg = BasicAlgebra::new("test".to_string(), universe, operations);
        
        assert_eq!(alg.algebra_type(), AlgebraType::Basic);
    }

    #[test]
    fn test_cardinality() {
        // Create algebras of different sizes
        let universe3: HashSet<i32> = (0..3).collect();
        let alg3 = BasicAlgebra::new("test3".to_string(), universe3, Vec::new());
        assert_eq!(alg3.cardinality(), 3);
        
        let universe10: HashSet<i32> = (0..10).collect();
        let alg10 = BasicAlgebra::new("test10".to_string(), universe10, Vec::new());
        assert_eq!(alg10.cardinality(), 10);
    }

    #[test]
    fn test_name_operations() {
        // Create algebra
        let universe: HashSet<i32> = (0..5).collect();
        let operations = Vec::new();
        let mut alg = BasicAlgebra::new("original".to_string(), universe, operations);
        
        assert_eq!(alg.name(), "original");
        
        // Set new name
        alg.set_name("renamed".to_string());
        assert_eq!(alg.name(), "renamed");
    }

    #[test]
    fn test_description_operations() {
        // Create algebra
        let universe: HashSet<i32> = (0..5).collect();
        let operations = Vec::new();
        let mut alg = BasicAlgebra::new("test".to_string(), universe, operations);
        
        // Initially no description
        assert!(alg.description().is_none());
        
        // Set description
        alg.set_description(Some("A test algebra".to_string()));
        assert_eq!(alg.description(), Some("A test algebra"));
        
        // Clear description
        alg.set_description(None);
        assert!(alg.description().is_none());
    }

    #[test]
    fn test_reset_con_and_sub() {
        // Create algebra
        let universe: HashSet<i32> = (0..5).collect();
        let operations = Vec::new();
        let mut alg = BasicAlgebra::new("test".to_string(), universe, operations);
        
        // This should not panic (even though con/sub are not implemented)
        alg.reset_con_and_sub();
    }

    #[test]
    fn test_convert_to_default_value_ops() {
        // Create algebra
        let universe: HashSet<i32> = (0..5).collect();
        let operations = Vec::new();
        let mut alg = BasicAlgebra::new("test".to_string(), universe, operations);
        
        // This should not panic (even though it's not fully implemented)
        alg.convert_to_default_value_ops();
    }

    #[test]
    fn test_clone() {
        // Create algebra
        let universe: HashSet<i32> = (0..5).collect();
        let operations = Vec::new();
        let alg = BasicAlgebra::new("test".to_string(), universe, operations);
        
        // Clone it
        let alg_clone = alg.clone();
        
        assert_eq!(alg.name(), alg_clone.name());
        assert_eq!(alg.cardinality(), alg_clone.cardinality());
        assert_eq!(alg.algebra_type(), alg_clone.algebra_type());
    }

    #[test]
    fn test_display() {
        // Create algebra
        let universe: HashSet<i32> = (0..3).collect();
        let operations = Vec::new();
        let alg = BasicAlgebra::new("test".to_string(), universe, operations);
        
        let display_string = format!("{}", alg);
        assert!(display_string.contains("BasicAlgebra"));
    }
}

