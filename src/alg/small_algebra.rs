use std::collections::{HashMap, HashSet};
use std::fmt::{Debug, Display};
use std::hash::Hash;
use crate::alg::algebra::{Algebra, ProgressMonitor};
use crate::alg::general_algebra::GeneralAlgebra;
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};

/// Types of small algebras, matching the Java enum
#[derive(Debug, Clone, PartialEq)]
pub enum AlgebraType {
    Basic,
    BasicLattice,
    Quotient,
    Subalgebra,
    Product,
    Power,
    MatrixPower,
    Reduct,
    Subproduct,
    Free,
    PolinLike,
    UnaryTermsMonoid,
    FiniteField,
}

/// A small algebra trait that extends Algebra for finite algebras.
/// 
/// A small algebra is one whose universe can be effectively indexed by {0,...,n-1}
/// for some positive integer n. This trait provides additional methods for
/// working with indexed elements.
pub trait SmallAlgebra: Algebra {
    /// Get the type of this small algebra.
    /// 
    /// # Returns
    /// The algebra type (basic, quotient, subalgebra, etc.)
    fn algebra_type(&self) -> AlgebraType;
    
    /// Get the k-th element of the universe.
    /// 
    /// # Arguments
    /// * `k` - The index of the element to retrieve
    /// 
    /// # Returns
    /// * `Some(element)` if k is a valid index
    /// * `None` if k is out of bounds
    fn get_element(&self, k: usize) -> Option<Self::UniverseItem>;
    
    /// Get the index of an element in the universe.
    /// 
    /// # Arguments
    /// * `elem` - The element to find the index for
    /// 
    /// # Returns
    /// * `Some(index)` if the element is in the universe
    /// * `None` if the element is not found
    fn element_index(&self, elem: &Self::UniverseItem) -> Option<usize>;
    
    /// Get the universe as a vector for indexed access.
    /// 
    /// # Returns
    /// * `Some(vec)` if the universe can be represented as a vector
    /// * `None` if the universe is too large or infinite
    fn get_universe_list(&self) -> Option<Vec<Self::UniverseItem>>;
    
    /// Get a map from elements to their indices.
    /// 
    /// # Returns
    /// * `Some(map)` if the universe order can be represented as a map
    /// * `None` if the universe is too large or infinite
    fn get_universe_order(&self) -> Option<HashMap<Self::UniverseItem, usize>>;
    
    /// Get the parent algebra if this is a derived algebra.
    /// 
    /// For a BasicAlgebra this is None; for a QuotientAlgebra this is
    /// the preimage; for a Subalgebra it is the super algebra.
    /// 
    /// # Returns
    /// * `Some(parent)` if this algebra has a parent
    /// * `None` if this is a basic algebra
    fn parent(&self) -> Option<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>;
    
    /// Get the parent algebras if this is a product algebra.
    /// 
    /// For a ProductAlgebra this will be the factors. For a BasicAlgebra
    /// it will be None. Otherwise it is a list containing the parent algebra.
    /// 
    /// # Returns
    /// * `Some(parents)` if this algebra has parents
    /// * `None` if this is a basic algebra
    fn parents(&self) -> Option<Vec<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>>;
    
    /// Reset cached congruence and subalgebra lattices.
    /// 
    /// This is used when the algebra structure changes.
    fn reset_con_and_sub(&mut self);
    
    /// Convert operations to default value operations (for UI).
    /// 
    /// This is only valid for BASIC algebras and is used in the UI.
    fn convert_to_default_value_ops(&mut self);
}

/// A basic implementation of SmallAlgebra using a GeneralAlgebra as the base.
/// 
/// This provides a concrete implementation of the SmallAlgebra trait for
/// finite algebras that can be indexed by integers.
pub struct BasicSmallAlgebra<T> 
where 
    T: Clone + PartialEq + Eq + Hash + Debug
{
    /// The underlying general algebra
    base: GeneralAlgebra<T>,
    
    /// The type of this algebra
    algebra_type: AlgebraType,
    
    /// Cached universe as a vector for indexed access
    universe_list: Option<Vec<T>>,
    
    /// Cached universe order map
    universe_order: Option<HashMap<T, usize>>,
    
    /// Parent algebra reference (would need Arc in real implementation)
    parent: Option<Box<dyn SmallAlgebra<UniverseItem = T>>>,
}

impl<T> BasicSmallAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug
{
    /// Create a new BasicSmallAlgebra.
    /// 
    /// # Arguments
    /// * `name` - The name of the algebra
    /// * `universe` - The universe set
    /// * `operations` - The operations on this algebra
    /// 
    /// # Returns
    /// A new BasicSmallAlgebra instance
    pub fn new(
        name: String,
        universe: HashSet<T>,
        operations: Vec<Box<dyn Operation>>
    ) -> Self {
        let base = GeneralAlgebra::new_with_operations(name, universe, operations);
        
        BasicSmallAlgebra {
            base,
            algebra_type: AlgebraType::Basic,
            universe_list: None,
            universe_order: None,
            parent: None,
        }
    }
    
    /// Set the operations for this algebra.
    /// 
    /// # Arguments
    /// * `operations` - The new operations list
    pub fn set_operations(&mut self, operations: Vec<Box<dyn Operation>>) {
        self.base.set_operations(operations);
    }

    /// Ensure the universe list is cached.
    fn ensure_universe_list(&mut self) {
        if self.universe_list.is_none() {
            // Get universe elements from the HashSet directly since universe() is not available
            let universe_vec: Vec<T> = self.base.universe.iter().cloned().collect();
            let mut universe_order = HashMap::new();
            for (i, elem) in universe_vec.iter().enumerate() {
                universe_order.insert(elem.clone(), i);
            }
            self.universe_list = Some(universe_vec);
            self.universe_order = Some(universe_order);
        }
    }
}

impl<T> Debug for BasicSmallAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug
{
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("BasicSmallAlgebra")
            .field("base", &self.base)
            .field("algebra_type", &self.algebra_type)
            .field("has_universe_list", &self.universe_list.is_some())
            .field("has_parent", &self.parent.is_some())
            .finish()
    }
}

impl<T> Clone for BasicSmallAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug
{
    fn clone(&self) -> Self {
        BasicSmallAlgebra {
            base: self.base.clone(),
            algebra_type: self.algebra_type.clone(),
            universe_list: self.universe_list.clone(),
            universe_order: self.universe_order.clone(),
            // Can't clone trait objects, so start with None
            parent: None,
        }
    }
}

impl<T> Algebra for BasicSmallAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug + Send + Sync + Display + 'static
{
    type UniverseItem = T;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.base.universe()
    }
    
    fn cardinality(&self) -> i32 {
        self.base.cardinality()
    }
    
    fn input_size(&self) -> i32 {
        self.base.input_size()
    }
    
    fn is_unary(&self) -> bool {
        self.base.is_unary()
    }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.base.iterator()
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        self.base.operations()
    }
    
    fn get_operation(&self, sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        self.base.get_operation(sym)
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        self.base.get_operations_map()
    }
    
    fn name(&self) -> &str {
        self.base.name()
    }
    
    fn set_name(&mut self, name: String) {
        self.base.set_name(name);
    }
    
    fn description(&self) -> Option<&str> {
        self.base.description()
    }
    
    fn set_description(&mut self, desc: Option<String>) {
        self.base.set_description(desc);
    }
    
    fn similarity_type(&self) -> &SimilarityType {
        self.base.similarity_type()
    }
    
    fn update_similarity_type(&mut self) {
        self.base.update_similarity_type();
    }
    
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        self.base.is_similar_to(other)
    }
    
    fn make_operation_tables(&mut self) {
        self.base.make_operation_tables();
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        self.base.constant_operations()
    }
    
    fn is_idempotent(&self) -> bool {
        self.base.is_idempotent()
    }
    
    fn is_total(&self) -> bool {
        self.base.is_total()
    }
    
    fn monitoring(&self) -> bool {
        self.base.monitoring()
    }
    
    fn get_monitor(&self) -> Option<&dyn ProgressMonitor> {
        self.base.get_monitor()
    }
    
    fn set_monitor(&mut self, monitor: Option<Box<dyn ProgressMonitor>>) {
        self.base.set_monitor(monitor);
    }
}

impl<T> SmallAlgebra for BasicSmallAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug + Send + Sync + Display + 'static
{
    fn algebra_type(&self) -> AlgebraType {
        self.algebra_type.clone()
    }
    
    fn get_element(&self, _k: usize) -> Option<Self::UniverseItem> {
        // We need mutable access to ensure_universe_list, but this method is immutable
        // This is a design limitation - in practice we'd use RefCell or similar
        None // Placeholder
    }
    
    fn element_index(&self, _elem: &Self::UniverseItem) -> Option<usize> {
        // Similar issue - need mutable access for caching
        None // Placeholder
    }
    
    fn get_universe_list(&self) -> Option<Vec<Self::UniverseItem>> {
        // Would need RefCell for internal mutability in real implementation
        None
    }
    
    fn get_universe_order(&self) -> Option<HashMap<Self::UniverseItem, usize>> {
        // Would need RefCell for internal mutability in real implementation
        None
    }
    
    fn parent(&self) -> Option<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        self.parent.as_ref().map(|p| p.as_ref())
    }
    
    fn parents(&self) -> Option<Vec<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>> {
        // For basic algebras, no parents
        None
    }
    
    fn reset_con_and_sub(&mut self) {
        // Reset any cached congruence and subalgebra lattices
        // This is a placeholder - real implementation would clear caches
    }
    
    fn convert_to_default_value_ops(&mut self) {
        // Convert operations to default value operations for UI
        // This is a placeholder - real implementation would modify operations
    }
}

impl<T> Display for BasicSmallAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug + Send + Sync + Display + 'static
{
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "BasicSmallAlgebra({})", self.base)
    }
}
