use std::collections::{HashMap, HashSet};
use std::fmt::{Debug, Display};
use std::hash::Hash;
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};

/// Constants for cardinality values, matching Java implementation
pub const CARDINALITY_UNKNOWN: i32 = -1;
pub const CARDINALITY_FINITE: i32 = -2;
pub const CARDINALITY_INFINITE: i32 = -3;
pub const CARDINALITY_COUNTABLE: i32 = -4;
pub const CARDINALITY_COUNTABLY_INFINITE: i32 = -5;

/// Progress monitor trait to avoid UI dependencies
pub trait ProgressMonitor: Send + Sync + Debug {
    fn report_progress(&self, message: &str);
    fn is_cancelled(&self) -> bool;
    fn set_progress(&self, progress: f64);
}

/// The core Algebra trait that defines the contract for all algebras in UACalc.
/// 
/// This trait represents an algebra in universal algebra, containing:
/// - A universe (the underlying set)
/// - A collection of operations defined on that set
/// - Metadata about the algebra (name, description, similarity type)
/// 
/// The trait is designed to handle both finite and infinite algebras,
/// with special support for unknown cardinalities.
pub trait Algebra: Display + Debug + Send + Sync {
    /// The type of elements in the universe
    type UniverseItem: Clone + PartialEq + Eq + Hash + Debug;
    
    /// Returns an iterator over the universe of the algebra.
    /// 
    /// Since the universe may be infinite, this returns a boxed iterator
    /// that can handle both finite and infinite cases. The iterator may
    /// throw an UnsupportedOperationException for infinite algebras.
    /// 
    /// # Returns
    /// An iterator over the universe elements
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>>;
    
    /// Returns the cardinality of the algebra.
    /// 
    /// For finite algebras, returns the actual size. For infinite or unknown
    /// cardinalities, returns one of the negative constants defined above.
    /// 
    /// # Returns
    /// * Positive integer for finite algebras
    /// * Negative constant for infinite/unknown cardinalities
    fn cardinality(&self) -> i32;
    
    /// Calculate the input size for this algebra.
    /// 
    /// This is the sum of the cardinality raised to the power of each
    /// operation's arity. Returns -1 if the size exceeds i32::MAX.
    /// 
    /// # Returns
    /// The input size or -1 if it exceeds maximum integer value
    fn input_size(&self) -> i32;
    
    /// Check if this algebra is unary (has only unary operations).
    /// 
    /// # Returns
    /// `true` if all operations have arity 1, `false` otherwise
    fn is_unary(&self) -> bool;
    
    /// Returns an iterator over the universe elements.
    /// 
    /// This is similar to `universe()` but matches the Java interface more closely.
    /// May throw an UnsupportedOperationException for infinite algebras.
    /// 
    /// # Returns
    /// An iterator over the universe elements
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>>;
    
    /// Returns a list of all operations in this algebra.
    /// 
    /// # Returns
    /// A vector containing all operations
    fn operations(&self) -> Vec<Box<dyn Operation>>;
    
    /// Get the operation corresponding to a symbol.
    /// 
    /// # Arguments
    /// * `sym` - The operation symbol to look up
    /// 
    /// # Returns
    /// * `Some(operation)` if the symbol exists in the algebra
    /// * `None` if the symbol is not part of the similarity type
    fn get_operation(&self, sym: &OperationSymbol) -> Option<Box<dyn Operation>>;
    
    /// Get a map from operation symbols to operations.
    /// 
    /// # Returns
    /// A HashMap mapping operation symbols to their corresponding operations
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>>;
    
    /// Get the name of this algebra.
    /// 
    /// # Returns
    /// The name of the algebra
    fn name(&self) -> &str;
    
    /// Set the name of this algebra.
    /// 
    /// # Arguments
    /// * `name` - The new name for the algebra
    fn set_name(&mut self, name: String);
    
    /// Get the description of this algebra.
    /// 
    /// # Returns
    /// * `Some(description)` if a description is set
    /// * `None` if no description is set
    fn description(&self) -> Option<&str>;
    
    /// Set the description of this algebra.
    /// 
    /// # Arguments
    /// * `desc` - The new description for the algebra
    fn set_description(&mut self, desc: Option<String>);
    
    /// Get the similarity type of this algebra.
    /// 
    /// The similarity type defines the operation symbols and their arities.
    /// 
    /// # Returns
    /// A reference to the similarity type
    fn similarity_type(&self) -> &SimilarityType;
    
    /// Update the similarity type based on the current operations.
    /// 
    /// This method recalculates the similarity type from the operations list.
    fn update_similarity_type(&mut self);
    
    /// Check if this algebra is similar to another algebra.
    /// 
    /// Two algebras are similar if they have the same similarity type.
    /// 
    /// # Arguments
    /// * `other` - The algebra to compare with
    /// 
    /// # Returns
    /// `true` if the algebras have the same similarity type
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool;
    
    /// Create operation tables to speed up operation evaluation.
    /// 
    /// This trades memory for speed by precomputing operation results.
    /// Should only be used for reasonably small algebras.
    fn make_operation_tables(&mut self);
    
    /// Get a list of constant operations (arity 0).
    /// 
    /// # Returns
    /// A vector of operations with arity 0
    fn constant_operations(&self) -> Vec<Box<dyn Operation>>;
    
    /// Check if all operations in this algebra are idempotent.
    /// 
    /// An operation is idempotent if f(x,x,...,x) = x for all x.
    /// 
    /// # Returns
    /// `true` if all operations are idempotent
    fn is_idempotent(&self) -> bool;
    
    /// Check if all operations in this algebra are total.
    /// 
    /// This will only return `false` if there are OperationWithDefaultValue
    /// operations that are not total.
    /// 
    /// # Returns
    /// `true` if all operations are total
    fn is_total(&self) -> bool;
    
    /// Check if monitoring is enabled for this algebra.
    /// 
    /// # Returns
    /// `true` if monitoring is enabled
    fn monitoring(&self) -> bool;
    
    /// Get the progress monitor for this algebra.
    /// 
    /// # Returns
    /// * `Some(monitor)` if monitoring is enabled
    /// * `None` if no monitor is set
    fn get_monitor(&self) -> Option<&dyn ProgressMonitor>;
    
    /// Set the progress monitor for this algebra.
    /// 
    /// # Arguments
    /// * `monitor` - The progress monitor to use
    fn set_monitor(&mut self, monitor: Option<Box<dyn ProgressMonitor>>);
}

/// Helper trait for algebras that need to be cloned.
/// 
/// Since we can't have `Clone` in the main trait due to object safety,
/// we provide this separate trait for cloning algebras.
pub trait CloneableAlgebra: Algebra {
    fn clone_box(&self) -> Box<dyn CloneableAlgebra<UniverseItem = Self::UniverseItem>>;
}

impl<T> CloneableAlgebra for T
where
    T: 'static + Algebra + Clone,
{
    fn clone_box(&self) -> Box<dyn CloneableAlgebra<UniverseItem = Self::UniverseItem>> {
        Box::new(self.clone())
    }
}

/// Type alias for boxed algebras for convenience.
pub type BoxedAlgebra<T> = Box<dyn Algebra<UniverseItem = T>>;

/// Create a boxed algebra from any type implementing Algebra.
pub fn boxed_algebra<T: 'static + Algebra>(alg: T) -> BoxedAlgebra<T::UniverseItem> {
    Box::new(alg)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::{GeneralAlgebra, BasicAlgebra, AlgebraType};
    use crate::alg::small_algebra::SmallAlgebra;
    use crate::alg::op::{OperationSymbol};
    use std::collections::HashSet;
    
    #[test]
    fn test_cardinality_constants() {
        assert_eq!(CARDINALITY_UNKNOWN, -1);
        assert_eq!(CARDINALITY_FINITE, -2);
        assert_eq!(CARDINALITY_INFINITE, -3);
        assert_eq!(CARDINALITY_COUNTABLE, -4);
        assert_eq!(CARDINALITY_COUNTABLY_INFINITE, -5);
    }

    /// Test GeneralAlgebra creation and basic properties
    #[test]
    fn test_general_algebra_creation() {
        let algebra: GeneralAlgebra<i32> = GeneralAlgebra::new("TestAlgebra".to_string());
        
        assert_eq!(algebra.name(), "TestAlgebra");
        assert_eq!(algebra.description(), None);
        assert_eq!(algebra.cardinality(), 0); // Empty universe
        assert!(!algebra.monitoring()); // No monitor by default
    }

    /// Test GeneralAlgebra with universe
    #[test]
    fn test_general_algebra_with_universe() {
        let mut universe = HashSet::new();
        universe.insert(0);
        universe.insert(1);
        universe.insert(2);
        
        let algebra = GeneralAlgebra::new_with_universe("TestAlgebra".to_string(), universe);
        
        assert_eq!(algebra.name(), "TestAlgebra");
        assert_eq!(algebra.cardinality(), 3);
        
        let universe_vec: Vec<i32> = algebra.universe().collect();
        assert_eq!(universe_vec.len(), 3);
        assert!(universe_vec.contains(&0));
        assert!(universe_vec.contains(&1));
        assert!(universe_vec.contains(&2));
    }

    /// Test algebra name and description operations
    #[test]
    fn test_algebra_metadata() {
        let mut algebra: GeneralAlgebra<i32> = GeneralAlgebra::new("Original".to_string());
        
        // Test initial state
        assert_eq!(algebra.name(), "Original");
        assert_eq!(algebra.description(), None);
        
        // Test setting name
        algebra.set_name("NewName".to_string());
        assert_eq!(algebra.name(), "NewName");
        
        // Test setting description
        algebra.set_description(Some("Test description".to_string()));
        assert_eq!(algebra.description(), Some("Test description"));
        
        // Test clearing description
        algebra.set_description(None);
        assert_eq!(algebra.description(), None);
    }

    /// Test input size calculation
    #[test]
    fn test_input_size() {
        let mut universe = HashSet::new();
        universe.insert(0);
        universe.insert(1);
        
        let mut algebra = GeneralAlgebra::new_with_universe("TestAlgebra".to_string(), universe);
        
        // With no operations, input size calculation depends on similarity type
        algebra.update_similarity_type();
        let input_size = algebra.input_size();
        
        // The exact value will depend on the implementation
        // For an empty similarity type, it should return the algebra size
        assert!(input_size >= 0);
    }

    /// Test is_unary method
    #[test]
    fn test_is_unary() {
        let algebra: GeneralAlgebra<i32> = GeneralAlgebra::new("TestAlgebra".to_string());
        
        // With no operations, should return true (empty set is vacuously unary)
        assert!(algebra.is_unary());
    }

    /// Test idempotent check
    #[test]
    fn test_is_idempotent() {
        let algebra: GeneralAlgebra<i32> = GeneralAlgebra::new("TestAlgebra".to_string());
        
        // With no operations, should return true (vacuously true)
        assert!(algebra.is_idempotent());
    }

    /// Test total check
    #[test]
    fn test_is_total() {
        let algebra: GeneralAlgebra<i32> = GeneralAlgebra::new("TestAlgebra".to_string());
        
        // With no operations, should return true (vacuously true)
        assert!(algebra.is_total());
    }

    /// Test BasicAlgebra creation
    #[test]
    fn test_basic_small_algebra_creation() {
        let mut universe = HashSet::new();
        universe.insert(0);
        universe.insert(1);
        universe.insert(2);
        
        let operations = Vec::new(); // No operations for now
        let algebra = BasicAlgebra::new("SmallTest".to_string(), universe, operations);
        
        assert_eq!(algebra.name(), "SmallTest");
        assert_eq!(algebra.cardinality(), 3);
        assert_eq!(algebra.algebra_type(), AlgebraType::Basic);
    }

    /// Test universe iteration
    #[test]
    fn test_universe_iteration() {
        let mut universe = HashSet::new();
        universe.insert(5);
        universe.insert(10);
        universe.insert(15);
        
        let algebra = GeneralAlgebra::new_with_universe("TestAlgebra".to_string(), universe);
        
        let collected: HashSet<i32> = algebra.universe().collect();
        assert_eq!(collected.len(), 3);
        assert!(collected.contains(&5));
        assert!(collected.contains(&10));
        assert!(collected.contains(&15));
        
        // Test that iterator() returns the same as universe()
        let collected2: HashSet<i32> = algebra.iterator().collect();
        assert_eq!(collected, collected2);
    }

    /// Test large universe cardinality
    #[test]
    fn test_large_universe() {
        let mut universe = HashSet::new();
        for i in 0..1000 {
            universe.insert(i);
        }
        
        let algebra = GeneralAlgebra::new_with_universe("LargeAlgebra".to_string(), universe);
        
        assert_eq!(algebra.cardinality(), 1000);
        assert_eq!(algebra.universe().count(), 1000);
    }

    /// Test empty universe
    #[test]
    fn test_empty_universe() {
        let universe: HashSet<i32> = HashSet::new();
        let algebra = GeneralAlgebra::new_with_universe("EmptyAlgebra".to_string(), universe);
        
        assert_eq!(algebra.cardinality(), 0);
        assert_eq!(algebra.universe().count(), 0);
    }

    /// Test Display implementation for GeneralAlgebra
    #[test]
    fn test_display_implementation() {
        let algebra: GeneralAlgebra<i32> = GeneralAlgebra::new("DisplayTest".to_string());
        let display_string = format!("{}", algebra);
        
        assert!(display_string.contains("DisplayTest"));
        assert!(display_string.contains("GeneralAlgebra"));
    }

    /// Test clone functionality
    #[test]
    fn test_clone_functionality() {
        let mut universe = HashSet::new();
        universe.insert(42);
        
        let algebra1 = GeneralAlgebra::new_with_universe("Original".to_string(), universe);
        let algebra2 = algebra1.clone();
        
        // Basic properties should be the same
        assert_eq!(algebra1.name(), algebra2.name());
        assert_eq!(algebra1.cardinality(), algebra2.cardinality());
        assert_eq!(algebra1.description(), algebra2.description());
        
        // But they should be independent objects
        let mut algebra2_mut = algebra2;
        algebra2_mut.set_name("Modified".to_string());
        assert_eq!(algebra1.name(), "Original");
        assert_eq!(algebra2_mut.name(), "Modified");
    }

    /// Test similarity type update
    #[test]
    fn test_similarity_type_update() {
        let mut algebra: GeneralAlgebra<i32> = GeneralAlgebra::new("TestAlgebra".to_string());
        
        // Update similarity type (this should work even with no operations)
        algebra.update_similarity_type();
        
        // We can't easily test the similarity type content without operations,
        // but we can test that the method doesn't panic
        let _similarity_type = algebra.similarity_type();
    }

    /// Test operations-related methods
    #[test]
    fn test_operations_methods() {
        let algebra: GeneralAlgebra<i32> = GeneralAlgebra::new("TestAlgebra".to_string());
        
        // With no operations
        let operations = algebra.operations();
        assert_eq!(operations.len(), 0);
        
        let operations_map = algebra.get_operations_map();
        assert_eq!(operations_map.len(), 0);
        
        let constant_ops = algebra.constant_operations();
        assert_eq!(constant_ops.len(), 0);
        
        // Test getting operation by symbol (should return None)
        let op_symbol = OperationSymbol::new("test", 1, false);
        let operation = algebra.get_operation(&op_symbol);
        assert!(operation.is_none());
    }

    /// Test make_operation_tables method
    #[test]
    fn test_make_operation_tables() {
        let mut algebra: GeneralAlgebra<i32> = GeneralAlgebra::new("TestAlgebra".to_string());
        
        // Should not panic even with no operations
        algebra.make_operation_tables();
    }
}
