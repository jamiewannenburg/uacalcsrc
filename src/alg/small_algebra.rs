use std::collections::{HashMap, HashSet};
use std::fmt::{Debug, Display};
use std::hash::Hash;
use std::sync::{Arc, RwLock};
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
    /// Get a reference to an operation by symbol (internal use).
    /// This is a workaround for the limitation of not being able to clone trait objects.
    fn get_operation_ref(&self, sym: &OperationSymbol) -> Option<&dyn Operation>;
    
    /// Get references to all operations (internal use).
    /// This is a workaround for the limitation of not being able to clone trait objects.
    fn get_operations_ref(&self) -> Vec<&dyn Operation>;

    /// Borrow Arc-backed operations when the concrete algebra supports it.
    ///
    /// Returning a borrowed slice lets product and closure algorithms share
    /// immutable operation tables without allocating wrappers or deep-cloning.
    fn operations_ref_arc(&self) -> Option<&[Arc<dyn Operation>]> {
        None
    }
    
    /// Clone this algebra into a new boxed trait object.
    /// 
    /// This allows cloning of trait objects by delegating to the concrete type's
    /// Clone implementation. This is necessary because `Box<dyn SmallAlgebra>` cannot
    /// automatically implement Clone.
    /// 
    /// # Returns
    /// A new boxed copy of this algebra
    fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>;
    

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
pub struct BasicAlgebra<T> 
where 
    T: Clone + PartialEq + Eq + Hash + Debug + Send + Sync + Display + 'static
{
    /// The underlying general algebra
    base: GeneralAlgebra<T>,
    
    /// The type of this algebra
    algebra_type: AlgebraType,
    
    /// Cached universe as a vector for indexed access (using RwLock for thread-safe interior mutability)
    universe_list: RwLock<Option<Vec<T>>>,
    
    /// Cached universe order map (using RwLock for thread-safe interior mutability)
    universe_order: RwLock<Option<HashMap<T, usize>>>,
    
    /// Parent algebra reference (would need Arc in real implementation)
    parent: Option<Box<dyn SmallAlgebra<UniverseItem = T>>>,
    
    /// Lazy-initialized congruence lattice
    con: Option<Box<crate::alg::conlat::CongruenceLattice<T>>>,
    
    /// Lazy-initialized subalgebra lattice
    sub: Option<Box<crate::alg::sublat::SubalgebraLattice<i32>>>,
}

impl<T> BasicAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug + Send + Sync + Display + 'static
{
    /// Create a new BasicAlgebra.
    /// 
    /// # Arguments
    /// * `name` - The name of the algebra
    /// * `universe` - The universe set
    /// * `operations` - The operations on this algebra
    /// 
    /// # Returns
    /// A new BasicAlgebra instance
    pub fn new(
        name: String,
        universe: HashSet<T>,
        operations: Vec<Box<dyn Operation>>
    ) -> Self {
        let mut base = GeneralAlgebra::new_with_operations(name, universe, operations);
        
        // Initialize the similarity type so that input_size() and other methods work
        base.update_similarity_type();
        
        BasicAlgebra {
            base,
            algebra_type: AlgebraType::Basic,
            universe_list: RwLock::new(None),
            universe_order: RwLock::new(None),
            parent: None,
            con: None,
            sub: None,
        }
    }
    
    /// Ensure the universe list and order are cached.
    /// This uses interior mutability via RwLock to allow caching in immutable methods.
    fn ensure_universe_list(&self) {
        // Check if we need to initialize (read lock)
        if self.universe_list.read().unwrap().is_none() {
            // Initialize with write lock
            let mut universe_vec: Vec<T> = self.base.universe.iter().cloned().collect();
            // Java integer universes are 0..n-1 in index order, not HashSet order.
            if std::any::TypeId::of::<T>() == std::any::TypeId::of::<i32>() {
                use std::any::Any;
                universe_vec.sort_unstable_by_key(|value| {
                    *(value as &dyn Any)
                        .downcast_ref::<i32>()
                        .expect("TypeId checked above")
                });
            }
            
            let mut universe_order = HashMap::new();
            for (i, elem) in universe_vec.iter().enumerate() {
                universe_order.insert(elem.clone(), i);
            }
            
            *self.universe_list.write().unwrap() = Some(universe_vec);
            *self.universe_order.write().unwrap() = Some(universe_order);
        }
    }
    
    /// Check if this algebra uses an integer universe (elements are just 0, 1, ..., n-1).
    /// 
    /// # Returns
    /// `true` if the universe is just integers from 0 to n-1, `false` otherwise
    pub fn int_universe(&self) -> bool {
        use std::any::{Any, TypeId};

        if TypeId::of::<T>() != TypeId::of::<i32>() {
            return false;
        }

        self.ensure_universe_list();
        self.universe_list
            .read()
            .unwrap()
            .as_ref()
            .is_some_and(|universe| {
                universe.iter().enumerate().all(|(index, value)| {
                    (value as &dyn Any).downcast_ref::<i32>() == Some(&(index as i32))
                })
            })
    }
    
    /// Reset the cached universe list and order.
    /// This should be called if the universe is modified.
    pub fn reset_universe_cache(&self) {
        *self.universe_list.write().unwrap() = None;
        *self.universe_order.write().unwrap() = None;
    }
    
    /// Get the congruence lattice (lazy initialization).
    /// 
    /// # Returns
    /// A reference to the congruence lattice
    pub fn con(&mut self) -> &crate::alg::conlat::CongruenceLattice<T>
    where
        T: 'static,
    {
        if self.con.is_none() {
            // Create congruence lattice using the new wrapper
            use crate::alg::SmallAlgebraWrapper;
            let alg_box = Box::new(self.clone()) as Box<dyn SmallAlgebra<UniverseItem = T>>;
            let wrapper = Box::new(SmallAlgebraWrapper::<T>::new(alg_box));
            self.con = Some(Box::new(crate::alg::conlat::CongruenceLattice::new(wrapper)));
        }
        self.con.as_ref().unwrap()
    }
    
    /// Get the subalgebra lattice (lazy initialization).
    /// 
    /// # Returns
    /// A reference to the subalgebra lattice
    /// 
    /// # Note
    /// This method is only available for BasicAlgebra<i32>.
    /// For other types, this will panic.
    pub fn sub(&mut self) -> &crate::alg::sublat::SubalgebraLattice<i32> {
        if self.sub.is_none() {
            // Only works for i32 universe type - check at runtime
            use std::any::TypeId;
            if TypeId::of::<T>() != TypeId::of::<i32>() {
                panic!("sub() method only available for BasicAlgebra<i32>");
            }
            
            // Create SubalgebraLattice for i32 universe type
            use crate::alg::SmallAlgebraWrapper;
            // SAFETY: We've verified that T = i32 above, so BasicAlgebra<T> = BasicAlgebra<i32>.
            // We transmute the concrete type (not the trait object) which is safe when T = i32.
            let cloned = self.clone();
            let i32_alg: BasicAlgebra<i32> = unsafe {
                std::mem::transmute(cloned)
            };
            let alg_box = Box::new(i32_alg) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
            let wrapper = Box::new(SmallAlgebraWrapper::<i32>::new(alg_box));
            match crate::alg::sublat::SubalgebraLattice::new_safe(wrapper) {
                Ok(sub_lat) => {
                    self.sub = Some(Box::new(sub_lat));
                }
                Err(e) => {
                    panic!("Failed to create SubalgebraLattice: {}", e);
                }
            }
        }
        self.sub.as_ref().unwrap()
    }
    
    /// Borrowed access to Arc-backed operations to avoid cloning.
    /// This provides shallow access to operations without deep cloning.
    pub fn operations_ref_arc(&self) -> &[std::sync::Arc<dyn Operation>] {
        self.base.operations_ref_arc()
    }
}

impl<T> Debug for BasicAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug + Send + Sync + Display + 'static
{
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("BasicAlgebra")
            .field("base", &self.base)
            .field("algebra_type", &self.algebra_type)
            .field("has_universe_list", &self.universe_list.read().unwrap().is_some())
            .field("has_parent", &self.parent.is_some())
            .finish()
    }
}

impl<T> Clone for BasicAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug + Send + Sync + Display + 'static
{
    fn clone(&self) -> Self {
        BasicAlgebra {
            base: self.base.clone(),
            algebra_type: self.algebra_type.clone(),
            universe_list: RwLock::new(self.universe_list.read().unwrap().clone()),
            universe_order: RwLock::new(self.universe_order.read().unwrap().clone()),
            // Can't clone trait objects, so start with None
            parent: None,
            con: None,
            sub: None,
        }
    }
}

impl<T> Algebra for BasicAlgebra<T>
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

impl<T> SmallAlgebra for BasicAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug + Send + Sync + Display + 'static
{
    fn get_operation_ref(&self, sym: &OperationSymbol) -> Option<&dyn Operation> {
        self.base.get_operation_ref(sym)
    }
    
    fn get_operations_ref(&self) -> Vec<&dyn Operation> {
        self.base.get_operations_ref()
    }

    fn operations_ref_arc(&self) -> Option<&[Arc<dyn Operation>]> {
        Some(BasicAlgebra::operations_ref_arc(self))
    }
    
    fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        Box::new(self.clone())
    }

    fn algebra_type(&self) -> AlgebraType {
        self.algebra_type.clone()
    }
    
    fn get_element(&self, k: usize) -> Option<Self::UniverseItem> {
        // Ensure universe list is cached
        self.ensure_universe_list();
        
        // Get element from cached list
        self.universe_list.read().unwrap()
            .as_ref()
            .and_then(|list| list.get(k).cloned())
    }
    
    fn element_index(&self, elem: &Self::UniverseItem) -> Option<usize> {
        // Ensure universe order is cached
        self.ensure_universe_list();
        
        // Get index from cached map
        self.universe_order.read().unwrap()
            .as_ref()
            .and_then(|order| order.get(elem).copied())
    }
    
    fn get_universe_list(&self) -> Option<Vec<Self::UniverseItem>> {
        // Ensure universe list is cached
        self.ensure_universe_list();
        
        // Return cloned list
        self.universe_list.read().unwrap().clone()
    }
    
    fn get_universe_order(&self) -> Option<HashMap<Self::UniverseItem, usize>> {
        // Ensure universe order is cached
        self.ensure_universe_list();
        
        // Return cloned map
        self.universe_order.read().unwrap().clone()
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
        // In this partial implementation, we don't have con/sub lattices yet
        // This is a no-op for now but matches the Java signature
    }
    
    fn convert_to_default_value_ops(&mut self) {
        // Convert operations to default value operations for UI
        // This would wrap operations in OperationWithDefaultValue
        // For now, this is a partial implementation - full implementation
        // would require OperationWithDefaultValue to be available
        // This is a no-op for now but matches the Java signature
    }
}

impl<T> Display for BasicAlgebra<T>
where 
    T: Clone + PartialEq + Eq + Hash + Debug + Send + Sync + Display + 'static
{
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "BasicAlgebra({})", self.base)
    }
}
