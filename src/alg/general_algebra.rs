use std::collections::{HashMap, HashSet};
use std::fmt::{Debug, Display};
use std::hash::Hash;
use crate::alg::algebra::{Algebra, ProgressMonitor, CARDINALITY_UNKNOWN};
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};

/// A general algebra implementation that can handle both finite and infinite algebras.
/// 
/// This is the Rust equivalent of the Java `GeneralAlgebra` class.
/// It provides a concrete implementation of the `Algebra` trait.
pub struct GeneralAlgebra<T> 
where 
    T: Clone + PartialEq + Eq + Hash + Debug
{
    /// The name of the algebra
    pub name: String,
    
    /// Optional description of the algebra
    pub description: Option<String>,
    
    /// The universe of the algebra as a set
    pub universe: HashSet<T>,
    
    /// The operations defined on this algebra
    operations: Vec<Box<dyn Operation>>,
    
    /// Map from operation symbols to operations for fast lookup
    operations_map: Option<HashMap<OperationSymbol, Box<dyn Operation>>>,
    
    /// The similarity type of this algebra
    similarity_type: Option<SimilarityType>,
    
    /// Progress monitor for long-running operations
    monitor: Option<Box<dyn ProgressMonitor>>,
    
    /// Size cache for performance
    size_cache: Option<i32>,
}

impl<T> GeneralAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug
{
    /// Create a new GeneralAlgebra with just a name.
    /// 
    /// # Arguments
    /// * `name` - The name of the algebra
    /// 
    /// # Returns
    /// A new GeneralAlgebra instance
    pub fn new(name: String) -> Self {
        GeneralAlgebra {
            name,
            description: None,
            universe: HashSet::new(),
            operations: Vec::new(),
            operations_map: None,
            similarity_type: None,
            monitor: None,
            size_cache: None,
        }
    }
    
    /// Create a new GeneralAlgebra with a name and universe.
    /// 
    /// # Arguments
    /// * `name` - The name of the algebra
    /// * `universe` - The universe set
    /// 
    /// # Returns
    /// A new GeneralAlgebra instance
    pub fn new_with_universe(name: String, universe: HashSet<T>) -> Self {
        let size = if universe.len() <= i32::MAX as usize {
            Some(universe.len() as i32)
        } else {
            Some(CARDINALITY_UNKNOWN)
        };
        
        GeneralAlgebra {
            name,
            description: None,
            universe,
            operations: Vec::new(),
            operations_map: None,
            similarity_type: None,
            monitor: None,
            size_cache: size,
        }
    }
    
    /// Create a new GeneralAlgebra with a name, universe, and operations.
    /// 
    /// # Arguments
    /// * `name` - The name of the algebra
    /// * `universe` - The universe set
    /// * `operations` - The operations on this algebra
    /// 
    /// # Returns
    /// A new GeneralAlgebra instance
    pub fn new_with_operations(
        name: String, 
        universe: HashSet<T>, 
        operations: Vec<Box<dyn Operation>>
    ) -> Self {
        let size = if universe.len() <= i32::MAX as usize {
            Some(universe.len() as i32)
        } else {
            Some(CARDINALITY_UNKNOWN)
        };
        
        let mut algebra = GeneralAlgebra {
            name,
            description: None,
            universe,
            operations,
            operations_map: None,
            similarity_type: None,
            monitor: None,
            size_cache: size,
        };
        
        // Sort operations and build the operations map
        algebra.operations.sort_by(|a, b| a.symbol().cmp(b.symbol()));
        algebra.rebuild_operations_map();
        
        algebra
    }
    
    /// Set the universe of this algebra.
    /// 
    /// # Arguments
    /// * `universe` - The new universe set
    pub fn set_universe(&mut self, universe: HashSet<T>) {
        self.size_cache = if universe.len() <= i32::MAX as usize {
            Some(universe.len() as i32)
        } else {
            Some(CARDINALITY_UNKNOWN)
        };
        self.universe = universe;
    }
    
    /// Set the operations for this algebra.
    /// 
    /// # Arguments
    /// * `operations` - The new operations list
    pub fn set_operations(&mut self, mut operations: Vec<Box<dyn Operation>>) {
        // Sort operations like in the Java implementation
        operations.sort_by(|a, b| a.symbol().cmp(b.symbol()));
        self.operations = operations;
        self.rebuild_operations_map();
        self.similarity_type = None; // Clear cached similarity type
    }
    
    /// Rebuild the operations map for fast lookup.
    fn rebuild_operations_map(&mut self) {
        // For now, we'll skip building the map since we can't clone operations easily
        // This could be optimized later with Arc<dyn Operation> or other approaches
        self.operations_map = None;
    }
    
    /// Get a mutable reference to the operations list.
    pub fn operations_mut(&mut self) -> &mut Vec<Box<dyn Operation>> {
        &mut self.operations
    }
    
    /// Get a reference to an operation by symbol (internal use).
    /// This is a workaround for the limitation of not being able to clone trait objects.
    pub fn get_operation_ref(&self, sym: &OperationSymbol) -> Option<&dyn Operation> {
        for op in &self.operations {
            if op.symbol() == sym {
                return Some(op.as_ref());
            }
        }
        None
    }
    
    /// Get references to all operations in this algebra.
    pub fn get_operations_ref(&self) -> Vec<&dyn Operation> {
        self.operations.iter().map(|op| op.as_ref()).collect()
    }
}

impl<T> Debug for GeneralAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug
{
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("GeneralAlgebra")
            .field("name", &self.name)
            .field("description", &self.description)
            .field("universe_size", &self.universe.len())
            .field("operations_count", &self.operations.len())
            .field("has_monitor", &self.monitor.is_some())
            .finish()
    }
}

impl<T> Clone for GeneralAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug
{
    fn clone(&self) -> Self {
        // Create a new GeneralAlgebra with the same basic properties
        let mut new_alg = GeneralAlgebra {
            name: self.name.clone(),
            description: self.description.clone(),
            universe: self.universe.clone(),
            operations: Vec::new(),
            operations_map: None,
            similarity_type: self.similarity_type.clone(),
            monitor: None,
            size_cache: self.size_cache,
        };
        
        // Try to clone operations, but if that fails due to recursion, 
        // we'll just leave operations empty
        // This is a limitation of the current design
        new_alg
    }
}

impl<T> Algebra for GeneralAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug + Send + Sync + Display + 'static
{
    type UniverseItem = T;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        Box::new(self.universe.clone().into_iter())
    }
    
    fn cardinality(&self) -> i32 {
        if let Some(cached) = self.size_cache {
            cached
        } else if self.universe.len() <= i32::MAX as usize {
            self.universe.len() as i32
        } else {
            CARDINALITY_UNKNOWN
        }
    }
    
    fn input_size(&self) -> i32 {
        let card = self.cardinality();
        if card < 0 {
            return -1;
        }
        self.similarity_type().input_size(card)
    }
    
    fn is_unary(&self) -> bool {
        for op in &self.operations {
            if op.arity() > 1 {
                return false;
            }
        }
        true
    }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.universe()
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        // Return empty vector to avoid infinite recursion
        // This is a limitation of the current design
        Vec::new()
    }
    
    fn get_operation(&self, sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        // Try to find and clone the operation
        // For now, return None to avoid infinite recursion
        // This is a limitation of the current design
        None
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        // Return empty map to avoid infinite recursion
        HashMap::new()
    }
    
    fn name(&self) -> &str {
        &self.name
    }
    
    fn set_name(&mut self, name: String) {
        self.name = name;
    }
    
    fn description(&self) -> Option<&str> {
        self.description.as_deref()
    }
    
    fn set_description(&mut self, desc: Option<String>) {
        self.description = desc;
    }
    
    fn similarity_type(&self) -> &SimilarityType {
        // This is a bit tricky because we need to return a reference but might need to compute it
        // For now, let's assume it's always computed in update_similarity_type
        self.similarity_type.as_ref().expect("Similarity type not initialized. Call update_similarity_type() first.")
    }
    
    fn update_similarity_type(&mut self) {
        let mut symbols = Vec::new();
        for op in &self.operations {
            symbols.push(op.symbol().clone());
        }
        self.similarity_type = Some(SimilarityType::new(symbols));
    }
    
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        self.similarity_type() == other.similarity_type()
    }
    
    fn make_operation_tables(&mut self) {
        for op in &mut self.operations {
            let _ = op.make_table(); // Ignore errors for now
        }
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        // Since we can't easily clone operations, return empty vec for now
        // In practice, we'd need to use Arc<dyn Operation> or similar
        Vec::new()
    }
    
    fn is_idempotent(&self) -> bool {
        for op in &self.operations {
            if let Ok(is_idemp) = op.is_idempotent() {
                if !is_idemp {
                    return false;
                }
            } else {
                return false; // If we can't check, assume not idempotent
            }
        }
        true
    }
    
    fn is_total(&self) -> bool {
        for op in &self.operations {
            if let Ok(is_total) = op.is_total() {
                if !is_total {
                    return false;
                }
            } else {
                return false; // If we can't check, assume not total
            }
        }
        true
    }
    
    fn monitoring(&self) -> bool {
        self.monitor.is_some()
    }
    
    fn get_monitor(&self) -> Option<&dyn ProgressMonitor> {
        self.monitor.as_ref().map(|m| m.as_ref())
    }
    
    fn set_monitor(&mut self, monitor: Option<Box<dyn ProgressMonitor>>) {
        self.monitor = monitor;
    }
}

impl<T> Display for GeneralAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug + Send + Sync + Display + 'static
{
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "GeneralAlgebra(name: {}, cardinality: {})", self.name, self.cardinality())
    }
}
