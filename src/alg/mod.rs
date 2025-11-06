use std::collections::{HashMap, HashSet};
use std::fmt::{Debug, Display};
use std::hash::Hash;
use std::sync::Arc;
use crate::util::int_array::IntArrayTrait;
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};
use crate::terms::Term;

/// A wrapper for SmallAlgebra that can be put into an Arc
#[derive(Debug)]
pub struct SmallAlgebraWrapper<T> {
    inner: Box<dyn SmallAlgebra<UniverseItem = T>>,
}

impl<T> SmallAlgebraWrapper<T> {
    pub fn new(inner: Box<dyn SmallAlgebra<UniverseItem = T>>) -> Self {
        SmallAlgebraWrapper { inner }
    }
}

impl<T> SmallAlgebra for SmallAlgebraWrapper<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn get_operation_ref(&self, sym: &OperationSymbol) -> Option<&dyn Operation> {
        self.inner.get_operation_ref(sym)
    }
    
    fn get_operations_ref(&self) -> Vec<&dyn Operation> {
        self.inner.get_operations_ref()
    }
    
    fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        Box::new(SmallAlgebraWrapper::new(self.inner.clone_box()))
    }
    
    fn algebra_type(&self) -> AlgebraType {
        self.inner.algebra_type()
    }
    
    fn get_element(&self, k: usize) -> Option<Self::UniverseItem> {
        self.inner.get_element(k)
    }
    
    fn element_index(&self, elem: &Self::UniverseItem) -> Option<usize> {
        self.inner.element_index(elem)
    }
    
    fn get_universe_list(&self) -> Option<Vec<Self::UniverseItem>> {
        self.inner.get_universe_list()
    }
    
    fn get_universe_order(&self) -> Option<HashMap<Self::UniverseItem, usize>> {
        self.inner.get_universe_order()
    }
    
    fn parent(&self) -> Option<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        self.inner.parent()
    }
    
    fn parents(&self) -> Option<Vec<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>> {
        self.inner.parents()
    }
    
    fn reset_con_and_sub(&mut self) {
        self.inner.reset_con_and_sub();
    }
    
    fn convert_to_default_value_ops(&mut self) {
        self.inner.convert_to_default_value_ops();
    }
}

impl<T> Algebra for SmallAlgebraWrapper<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    type UniverseItem = T;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.inner.universe()
    }
    
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }
    
    fn input_size(&self) -> i32 {
        self.inner.input_size()
    }
    
    fn is_unary(&self) -> bool {
        self.inner.is_unary()
    }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.inner.iterator()
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        self.inner.operations()
    }
    
    fn get_operation(&self, sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        self.inner.get_operation(sym)
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        self.inner.get_operations_map()
    }
    
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }
    
    fn description(&self) -> Option<&str> {
        self.inner.description()
    }
    
    fn set_description(&mut self, desc: Option<String>) {
        self.inner.set_description(desc);
    }
    
    fn similarity_type(&self) -> &SimilarityType {
        self.inner.similarity_type()
    }
    
    fn update_similarity_type(&mut self) {
        self.inner.update_similarity_type();
    }
    
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        self.inner.is_similar_to(other)
    }
    
    fn make_operation_tables(&mut self) {
        self.inner.make_operation_tables();
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        self.inner.constant_operations()
    }
    
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }
    
    fn is_total(&self) -> bool {
        self.inner.is_total()
    }
    
    fn monitoring(&self) -> bool {
        self.inner.monitoring()
    }
    
    fn get_monitor(&self) -> Option<&dyn ProgressMonitor> {
        self.inner.get_monitor()
    }
    
    fn set_monitor(&mut self, monitor: Option<Box<dyn ProgressMonitor>>) {
        self.inner.set_monitor(monitor);
    }
}

impl<T> std::fmt::Display for SmallAlgebraWrapper<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "SmallAlgebraWrapper({})", self.inner.name())
    }
}

pub mod algebra;
pub mod algebra_with_generating_vector;
pub mod big_product_algebra;
pub mod closer;
pub mod closer_timing;
pub mod conlat;
pub mod general_algebra;
pub mod op;
pub mod parallel;
pub mod product_algebra;
pub mod quotient_algebra;
pub mod quotient_element;
pub mod small_algebra;
pub mod subalgebra;
pub mod sub_product_algebra;
pub mod sublat;

#[cfg(test)]
mod matrix_power_algebra_tests;

// Re-export partition types for convenience
pub use conlat::partition::{Partition, PrintType};

// Re-export CloserTiming and Closer
pub use closer_timing::CloserTiming;
pub use closer::Closer;
pub use big_product_algebra::BigProductAlgebra;

// Re-export algebra types
pub use algebra::{
    Algebra, CloneableAlgebra, BoxedAlgebra, boxed_algebra, ProgressMonitor,
    CARDINALITY_UNKNOWN, CARDINALITY_FINITE, CARDINALITY_INFINITE,
    CARDINALITY_COUNTABLE, CARDINALITY_COUNTABLY_INFINITE
};

// Re-export concrete algebra implementations
pub use general_algebra::GeneralAlgebra;
pub use small_algebra::{SmallAlgebra, BasicAlgebra, AlgebraType};
pub use subalgebra::Subalgebra;
pub use product_algebra::ProductAlgebra;
pub use quotient_algebra::QuotientAlgebra;
pub use quotient_element::QuotientElement;
pub use algebra_with_generating_vector::{AlgebraWithGeneratingVector, AlgebraWithGeneratingVectorI32};

// Import ParameterizedOperation from op module (defined later in this file)
pub use op::ParameterizedOperation;

// PowerAlgebra is implemented in this file (mod.rs)

// BasicAlgebra is now implemented as BasicAlgebra
// GeneralAlgebra is now implemented in general_algebra.rs
// ProductAlgebra is now implemented in product_algebra.rs
// Subalgebra is now implemented in subalgebra.rs

pub mod free_algebra;

pub use free_algebra::FreeAlgebra;

// QuotientAlgebra is now implemented in quotient_algebra.rs

/// A homomorphism from the domain algebra into the range algebra.
/// 
/// This struct represents a homomorphism between two small algebras, where
/// elements are mapped by their indices. The homomorphism preserves the
/// algebraic structure between the domain and range algebras.
/// 
/// # Examples
/// ```
/// use uacalc::alg::{Homomorphism, SmallAlgebra};
/// use std::collections::HashMap;
/// 
/// // Create a simple mapping
/// let mut map = HashMap::new();
/// map.insert(0, 0);
/// map.insert(1, 1);
/// 
/// // Create homomorphism (assuming domain and range algebras exist)
/// // let homo = Homomorphism::new(domain, range, map).unwrap();
/// ```
#[derive(Debug)]
pub struct Homomorphism {
    /// The domain algebra
    pub domain: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    /// The range algebra  
    pub range: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    /// The mapping from domain indices to range indices
    pub map: HashMap<usize, usize>,
}

impl Clone for Homomorphism {
    fn clone(&self) -> Self {
        Homomorphism {
            domain: self.domain.clone_box(),
            range: self.range.clone_box(),
            map: self.map.clone(),
        }
    }
}

impl Homomorphism {
    /// Create a new homomorphism from domain to range with the given mapping.
    /// 
    /// # Arguments
    /// * `domain` - The domain algebra
    /// * `range` - The range algebra
    /// * `map` - The mapping from domain indices to range indices
    /// 
    /// # Returns
    /// * `Ok(Homomorphism)` - Successfully created homomorphism
    /// * `Err(String)` - If the mapping is invalid or algebras are incompatible
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{Homomorphism, SmallAlgebra, BasicAlgebra};
    /// use std::collections::{HashMap, HashSet};
    /// 
    /// // Create mock algebras
    /// let domain = Box::new(BasicAlgebra::new(
    ///     "domain".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let range = Box::new(BasicAlgebra::new(
    ///     "range".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// // Create a simple mapping
    /// let mut map = HashMap::new();
    /// map.insert(0, 0);
    /// map.insert(1, 1);
    /// 
    /// // Create homomorphism
    /// let homo = Homomorphism::new_safe(domain, range, map).unwrap();
    /// assert_eq!(homo.get_domain().name(), "domain");
    /// assert_eq!(homo.get_range().name(), "range");
    /// ```
    pub fn new_safe(
        domain: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        range: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        map: HashMap<usize, usize>,
    ) -> Result<Self, String> {
        // Validate that all domain elements are mapped
        let domain_size = domain.cardinality() as usize;
        for i in 0..domain_size {
            if !map.contains_key(&i) {
                return Err(format!("Domain element {} is not mapped", i));
            }
        }
        
        // Validate that all mapped values are valid range elements
        let range_size = range.cardinality() as usize;
        for (_, &range_val) in &map {
            if range_val >= range_size {
                return Err(format!("Mapped value {} is out of range [0, {})", range_val, range_size));
            }
        }
        
        Ok(Homomorphism { domain, range, map })
    }
    
    /// Create a new homomorphism with panic on error (for compatibility).
    /// 
    /// # Arguments
    /// * `domain` - The domain algebra
    /// * `range` - The range algebra
    /// * `map` - The mapping from domain indices to range indices
    /// 
    /// # Panics
    /// Panics if the mapping is invalid or algebras are incompatible
    pub fn new(
        domain: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        range: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        map: HashMap<usize, usize>,
    ) -> Self {
        Self::new_safe(domain, range, map).unwrap()
    }
    
    /// Compute the kernel partition of this homomorphism.
    /// 
    /// The kernel partition groups domain elements that map to the same
    /// range element. This is computed using the zero partition and
    /// joining blocks for elements with the same image.
    /// 
    /// # Returns
    /// * `Ok(Partition)` - The kernel partition
    /// * `Err(String)` - If there's an error computing the kernel
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{Homomorphism, SmallAlgebra, BasicAlgebra};
    /// use std::collections::{HashMap, HashSet};
    /// 
    /// // Create mock algebras
    /// let domain = Box::new(BasicAlgebra::new(
    ///     "domain".to_string(),
    ///     HashSet::from([0, 1, 2]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let range = Box::new(BasicAlgebra::new(
    ///     "range".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// // Create mapping where 0 and 2 both map to 0, 1 maps to 1
    /// let mut map = HashMap::new();
    /// map.insert(0, 0);
    /// map.insert(1, 1);
    /// map.insert(2, 0);
    /// 
    /// // Create homomorphism and compute kernel
    /// let homo = Homomorphism::new_safe(domain, range, map).unwrap();
    /// let kernel = homo.kernel().unwrap();
    /// 
    /// // Kernel should have 2 blocks: {0, 2} and {1}
    /// assert_eq!(kernel.number_of_blocks(), 2);
    /// assert!(kernel.is_related(0, 2)); // 0 and 2 map to same value
    /// assert!(!kernel.is_related(0, 1)); // 0 and 1 map to different values
    /// ```
    pub fn kernel(&self) -> Result<Partition, String> {
        let size = self.domain.cardinality() as usize;
        let mut par = Partition::zero(size);
        
        for i in 0..size {
            let r = par.representative(i);
            for j in (i + 1)..size {
                if let (Some(&map_i), Some(&map_j)) = (self.map.get(&i), self.map.get(&j)) {
                    if map_i == map_j {
                        let s = par.representative(j);
                        if r != s {
                            par.join_blocks(r, s);
                        }
                    }
                }
            }
        }
        
        Ok(par)
    }
    
    /// Create a product homomorphism from a list of homomorphisms.
    /// 
    /// This static method creates a list of IntArray elements representing
    /// the product homomorphism. Each IntArray contains the mapped values
    /// for all homomorphisms at a given domain element.
    /// 
    /// # Arguments
    /// * `homomorphisms` - A slice of homomorphisms with the same domain
    /// 
    /// # Returns
    /// * `Ok(Vec<IntArray>)` - List of IntArray elements for the product
    /// * `Err(String)` - If the homomorphisms are incompatible or empty
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{Homomorphism, SmallAlgebra, BasicAlgebra};
    /// use uacalc::util::int_array::IntArrayTrait;
    /// use std::collections::{HashMap, HashSet};
    /// 
    /// // Create mock algebras
    /// let domain = Box::new(BasicAlgebra::new(
    ///     "domain".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let range1 = Box::new(BasicAlgebra::new(
    ///     "range1".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let range2 = Box::new(BasicAlgebra::new(
    ///     "range2".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// // Create two homomorphisms with same domain
    /// let mut map1 = HashMap::new();
    /// map1.insert(0, 0);
    /// map1.insert(1, 1);
    /// let homo1 = Homomorphism::new_safe(domain.clone_box(), range1, map1).unwrap();
    /// 
    /// let mut map2 = HashMap::new();
    /// map2.insert(0, 1);
    /// map2.insert(1, 0);
    /// let homo2 = Homomorphism::new_safe(domain, range2, map2).unwrap();
    /// 
    /// // Create product homomorphism
    /// let homos = vec![homo1, homo2];
    /// let product = Homomorphism::product_homo(&homos).unwrap();
    /// 
    /// // Product should have 2 elements (domain size)
    /// assert_eq!(product.len(), 2);
    /// // Each element should be an IntArray of size 2 (number of homomorphisms)
    /// assert_eq!(product[0].universe_size(), 2);
    /// assert_eq!(product[1].universe_size(), 2);
    /// ```
    pub fn product_homo(homomorphisms: &[Self]) -> Result<Vec<crate::util::int_array::IntArray>, String> {
        if homomorphisms.is_empty() {
            return Err("Cannot create product homomorphism from empty list".to_string());
        }
        
        let domain_size = homomorphisms[0].domain.cardinality() as usize;
        let mut ans = Vec::with_capacity(domain_size);
        
        for i in 0..domain_size {
            let mut ia = crate::util::int_array::IntArray::new(homomorphisms.len())?;
            for (k, homo) in homomorphisms.iter().enumerate() {
                if let Some(&mapped_val) = homo.map.get(&i) {
                    ia.set(k, mapped_val as i32)?;
                } else {
                    return Err(format!("Domain element {} not mapped in homomorphism {}", i, k));
                }
            }
            ans.push(ia);
        }
        
        Ok(ans)
    }
    
    /// Get the domain algebra.
    /// 
    /// # Returns
    /// A reference to the domain algebra
    pub fn get_domain(&self) -> &dyn SmallAlgebra<UniverseItem = i32> {
        self.domain.as_ref()
    }
    
    /// Set the domain algebra.
    /// 
    /// # Arguments
    /// * `domain` - The new domain algebra
    pub fn set_domain(&mut self, domain: Box<dyn SmallAlgebra<UniverseItem = i32>>) {
        self.domain = domain;
    }
    
    /// Get the range algebra.
    /// 
    /// # Returns
    /// A reference to the range algebra
    pub fn get_range(&self) -> &dyn SmallAlgebra<UniverseItem = i32> {
        self.range.as_ref()
    }
    
    /// Set the range algebra.
    /// 
    /// # Arguments
    /// * `range` - The new range algebra
    pub fn set_range(&mut self, range: Box<dyn SmallAlgebra<UniverseItem = i32>>) {
        self.range = range;
    }
    
    /// Get the mapping.
    /// 
    /// # Returns
    /// A reference to the mapping HashMap
    pub fn get_map(&self) -> &HashMap<usize, usize> {
        &self.map
    }
    
    /// Set the mapping.
    /// 
    /// # Arguments
    /// * `map` - The new mapping
    pub fn set_map(&mut self, map: HashMap<usize, usize>) {
        self.map = map;
    }
}

impl std::fmt::Display for Homomorphism {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "homomorphism: {} --> {} : {:?}",
            self.domain.name(),
            self.range.name(),
            self.map
        )
    }
}

pub struct Algebras {
    // TODO: Implement algebras collection
}

pub struct AlgebraFromMinimalSets {
    // TODO: Implement algebra from minimal sets
}

// AlgebraWithGeneratingVector is now implemented in algebra_with_generating_vector.rs

/// A matrix power algebra that extends PowerAlgebra with matrix-specific operations.
/// 
/// This struct represents the direct power A^n of a single algebra A, where
/// each element is a tuple of n elements from A, with additional matrix operations
/// like left shift and diagonal operations.
/// 
/// # Examples
/// ```
/// use uacalc::alg::{MatrixPowerAlgebra, SmallAlgebra, BasicAlgebra, Algebra};
/// use std::collections::HashSet;
/// 
/// // Create a small algebra
/// let alg = Box::new(BasicAlgebra::new(
///     "A".to_string(),
///     HashSet::from([0, 1]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Create matrix power algebra A^3
/// let matrix_power = MatrixPowerAlgebra::new_safe(alg, 3).unwrap();
/// 
/// assert_eq!(matrix_power.cardinality(), 8); // 2^3 = 8
/// assert_eq!(matrix_power.get_power(), 3);
/// ```
pub struct MatrixPowerAlgebra {
    /// The underlying power algebra
    power_algebra: PowerAlgebra,
    
    /// The root algebra that is being raised to a power
    root: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    
    /// The size of the root algebra
    root_size: i32,
    
    /// The power/exponent (number of copies)
    power: usize,
    
    /// Matrix-specific operations (left shift and diagonal)
    matrix_operations: Vec<Box<dyn Operation>>,
}

impl MatrixPowerAlgebra {
    /// Create a new MatrixPowerAlgebra from a root algebra and power.
    /// 
    /// # Arguments
    /// * `root` - The algebra to raise to a power
    /// * `power` - The power/exponent (number of copies)
    /// 
    /// # Returns
    /// * `Ok(MatrixPowerAlgebra)` - Successfully created matrix power algebra
    /// * `Err(String)` - If power is invalid or algebra is incompatible
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{MatrixPowerAlgebra, SmallAlgebra, BasicAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1, 2]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let matrix_power = MatrixPowerAlgebra::new_safe(alg, 2).unwrap();
    /// assert_eq!(matrix_power.cardinality(), 9); // 3^2 = 9
    /// ```
    pub fn new_safe(
        root: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        power: usize,
    ) -> Result<Self, String> {
        Self::new_with_name_safe("".to_string(), root, power)
    }
    
    /// Create a new MatrixPowerAlgebra with a custom name.
    /// 
    /// # Arguments
    /// * `name` - The name for the matrix power algebra
    /// * `root` - The algebra to raise to a power
    /// * `power` - The power/exponent (number of copies)
    /// 
    /// # Returns
    /// * `Ok(MatrixPowerAlgebra)` - Successfully created matrix power algebra
    /// * `Err(String)` - If power is invalid or algebra is incompatible
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{MatrixPowerAlgebra, SmallAlgebra, BasicAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let matrix_power = MatrixPowerAlgebra::new_with_name_safe("MyMatrix".to_string(), alg, 3).unwrap();
    /// assert_eq!(matrix_power.name(), "MyMatrix");
    /// ```
    pub fn new_with_name_safe(
        name: String,
        root: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        power: usize,
    ) -> Result<Self, String> {
        if power == 0 {
            return Err("Power cannot be zero".to_string());
        }
        
        let root_size = root.cardinality();
        if root_size <= 0 {
            return Err("Root algebra must have positive cardinality".to_string());
        }
        
        // Determine the name first before moving root
        let final_name = if name.is_empty() {
            let root_name = root.name();
            if root_name.is_empty() {
                format!("{}-matrix power", power)
            } else {
                format!("{}^[{}]", root_name, power)
            }
        } else {
            name
        };
        
        // Create the underlying power algebra
        // Note: We can't clone the root algebra, so we'll create a new one
        let power_algebra = PowerAlgebra::new_safe(root, power)?;
        
        // Create matrix power algebra
        // We need to create a new root algebra since we can't clone the original
        let new_root = Box::new(BasicAlgebra::new(
            "MatrixPowerRoot".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let mut matrix_power = MatrixPowerAlgebra {
            power_algebra,
            root: new_root,
            root_size,
            power,
            matrix_operations: Vec::new(),
        };
        
        // Set the name
        matrix_power.set_name(final_name);
        
        // Add matrix-specific operations
        matrix_power.add_matrix_operations()?;
        
        Ok(matrix_power)
    }
    
    /// Add matrix-specific operations (left shift and diagonal operations).
    fn add_matrix_operations(&mut self) -> Result<(), String> {
        use crate::alg::op::operations::{make_left_shift, make_matrix_diagonal_op};
        
        // Add left shift operation
        let left_shift = make_left_shift(self.cardinality(), self.root_size)?;
        
        // Add matrix diagonal operation
        let matrix_diagonal = make_matrix_diagonal_op(self.cardinality(), self.root_size)?;
        
        // Store operations in matrix_operations field
        self.matrix_operations.push(left_shift);
        self.matrix_operations.push(matrix_diagonal);
        
        Ok(())
    }
    
    /// Get the root algebra.
    /// 
    /// # Returns
    /// A reference to the root algebra
    pub fn get_root(&self) -> &dyn SmallAlgebra<UniverseItem = i32> {
        self.root.as_ref()
    }
    
    /// Get the root algebra (alias for get_root).
    /// 
    /// # Returns
    /// A reference to the root algebra
    pub fn parent(&self) -> &dyn SmallAlgebra<UniverseItem = i32> {
        self.get_root()
    }
    
    /// Get the list of parent algebras (contains only the root algebra).
    /// 
    /// # Returns
    /// A vector containing the root algebra
    pub fn parents(&self) -> Vec<&dyn SmallAlgebra<UniverseItem = i32>> {
        vec![self.root.as_ref()]
    }
    
    /// Get the underlying power algebra.
    /// 
    /// # Returns
    /// A reference to the power algebra
    pub fn get_power_algebra(&self) -> &PowerAlgebra {
        &self.power_algebra
    }
    
    /// Get the power/exponent.
    /// 
    /// # Returns
    /// The power/exponent (number of copies)
    pub fn get_power(&self) -> usize {
        self.power
    }
    
    /// Get an element by its index using Horner encoding.
    /// 
    /// # Arguments
    /// * `index` - The index of the element
    /// 
    /// # Returns
    /// The element as a vector of integers
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{MatrixPowerAlgebra, SmallAlgebra, BasicAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let matrix_power = MatrixPowerAlgebra::new_safe(alg, 2).unwrap();
    /// let element = matrix_power.get_element(0);
    /// assert_eq!(element, vec![0, 0]);
    /// ```
    pub fn get_element(&self, index: usize) -> Vec<i32> {
        use crate::util::horner::horner_inv_same_size;
        horner_inv_same_size(index as i32, self.root_size, self.power)
    }
    
    /// Get the index of an element using the power algebra.
    /// 
    /// # Arguments
    /// * `obj` - The element (as a vector of integers)
    /// 
    /// # Returns
    /// The index of the element
    pub fn element_index(&self, obj: &[i32]) -> usize {
        // Convert the vector to a single integer using Horner encoding
        use crate::util::horner::horner_same_size;
        let encoded = horner_same_size(obj, self.root_size);
        self.power_algebra.element_index(&encoded).unwrap_or(0)
    }
    
    /// Get the universe as a list of integer arrays.
    /// 
    /// # Returns
    /// A vector of vectors representing the universe elements
    pub fn get_universe_list(&self) -> Vec<Vec<i32>> {
        let mut universe = Vec::new();
        for i in 0..self.cardinality() {
            universe.push(self.get_element(i as usize));
        }
        universe
    }
    
    /// Get the universe order (not implemented for matrix power algebras).
    /// 
    /// # Returns
    /// None (matrix power algebras don't have a natural order)
    pub fn get_universe_order(&self) -> Option<HashMap<Vec<i32>, usize>> {
        None
    }
    
    /// Convert to default value operations (not supported for matrix power algebras).
    /// 
    /// # Panics
    /// Always panics with "Only for basic algebras"
    pub fn convert_to_default_value_ops(&mut self) {
        panic!("Only for basic algebras");
    }
    
    /// Get the algebra type.
    /// 
    /// # Returns
    /// `AlgebraType::MatrixPower`
    pub fn algebra_type(&self) -> AlgebraType {
        AlgebraType::MatrixPower
    }
}

impl Algebra for MatrixPowerAlgebra {
    type UniverseItem = i32;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.power_algebra.universe()
    }
    
    fn cardinality(&self) -> i32 {
        self.power_algebra.cardinality()
    }
    
    fn input_size(&self) -> i32 {
        self.power_algebra.input_size()
    }
    
    fn is_unary(&self) -> bool {
        // Check if the underlying power algebra is unary
        if !self.power_algebra.is_unary() {
            return false;
        }
        
        // Check if all matrix operations are unary (arity <= 1)
        for op in &self.matrix_operations {
            if op.arity() > 1 {
                return false;
            }
        }
        
        true
    }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.power_algebra.iterator()
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        // Recreate the matrix operations since we can't clone Box<dyn Operation>
        use crate::alg::op::operations::{make_left_shift, make_matrix_diagonal_op};
        
        let mut operations = Vec::new();
        
        // Recreate left shift operation
        if let Ok(left_shift) = make_left_shift(self.cardinality(), self.root_size) {
            operations.push(left_shift);
        }
        
        // Recreate matrix diagonal operation
        if let Ok(matrix_diagonal) = make_matrix_diagonal_op(self.cardinality(), self.root_size) {
            operations.push(matrix_diagonal);
        }
        
        operations
    }
    
    fn get_operation(&self, sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        self.power_algebra.get_operation(sym)
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        self.power_algebra.get_operations_map()
    }
    
    fn name(&self) -> &str {
        self.power_algebra.name()
    }
    
    fn set_name(&mut self, name: String) {
        self.power_algebra.set_name(name);
    }
    
    fn description(&self) -> Option<&str> {
        self.power_algebra.description()
    }
    
    fn set_description(&mut self, desc: Option<String>) {
        self.power_algebra.set_description(desc);
    }
    
    fn similarity_type(&self) -> &SimilarityType {
        self.power_algebra.similarity_type()
    }
    
    fn update_similarity_type(&mut self) {
        self.power_algebra.update_similarity_type();
    }
    
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        self.power_algebra.is_similar_to(other)
    }
    
    fn make_operation_tables(&mut self) {
        self.power_algebra.make_operation_tables();
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        self.power_algebra.constant_operations()
    }
    
    fn is_idempotent(&self) -> bool {
        // Check if the underlying power algebra is idempotent
        if !self.power_algebra.is_idempotent() {
            return false;
        }
        
        // Check if all matrix operations are idempotent
        for op in &self.matrix_operations {
            match op.is_idempotent() {
                Ok(false) => return false,
                Err(_) => return false, // If we can't determine, assume not idempotent
                Ok(true) => continue,
            }
        }
        
        true
    }
    
    fn is_total(&self) -> bool {
        self.power_algebra.is_total()
    }
    
    fn monitoring(&self) -> bool {
        self.power_algebra.monitoring()
    }
    
    fn get_monitor(&self) -> Option<&dyn crate::alg::algebra::ProgressMonitor> {
        self.power_algebra.get_monitor()
    }
    
    fn set_monitor(&mut self, monitor: Option<Box<dyn crate::alg::algebra::ProgressMonitor>>) {
        self.power_algebra.set_monitor(monitor);
    }
}

impl SmallAlgebra for MatrixPowerAlgebra {
    fn get_operation_ref(&self, sym: &OperationSymbol) -> Option<&dyn Operation> {
        // Check matrix operations first
        for op in &self.matrix_operations {
            if op.symbol() == sym {
                return Some(op.as_ref());
            }
        }
        // Fall back to power algebra operations
        self.power_algebra.get_operation_ref(sym)
    }
    
    fn get_operations_ref(&self) -> Vec<&dyn Operation> {
        // Return matrix operations (they are the operations of this algebra)
        self.matrix_operations.iter().map(|op| op.as_ref()).collect()
    }
    
    fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        // We can't clone trait objects, so we'll create a new one
        // This is a limitation of the current design
        let alg = Box::new(BasicAlgebra::new(
            "ClonedRoot".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        Box::new(MatrixPowerAlgebra::new_safe(alg, self.power).unwrap())
    }
    
    fn get_element(&self, k: usize) -> Option<Self::UniverseItem> {
        // For SmallAlgebra, we need to return a single integer
        // We'll use the Horner encoding of the element
        use crate::util::horner::horner_same_size;
        let element = self.get_element(k);
        Some(horner_same_size(&element, self.root_size))
    }
    
    fn parent(&self) -> Option<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        Some(self.root.as_ref())
    }
    
    fn parents(&self) -> Option<Vec<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>> {
        Some(vec![self.root.as_ref()])
    }
    
    fn reset_con_and_sub(&mut self) {
        // Matrix power algebras don't have con and sub lattices in this implementation
        // This is a no-op for now
    }
    
    fn element_index(&self, obj: &Self::UniverseItem) -> Option<usize> {
        // For SmallAlgebra, the universe item is a single integer
        // We need to convert it back to the element vector and then get the index
        use crate::util::horner::horner_inv_same_size;
        let element = horner_inv_same_size(*obj, self.root_size, self.power);
        // Convert the element vector to a single integer using Horner encoding
        use crate::util::horner::horner_same_size;
        let encoded = horner_same_size(&element, self.root_size);
        self.power_algebra.element_index(&encoded)
    }
    
    fn get_universe_list(&self) -> Option<Vec<Self::UniverseItem>> {
        let mut universe = Vec::new();
        for i in 0..self.cardinality() {
            // For SmallAlgebra, we need to return a single integer (Horner encoded)
            use crate::util::horner::horner_same_size;
            let element = self.get_element(i as usize);
            let encoded = horner_same_size(&element, self.root_size);
            universe.push(encoded);
        }
        Some(universe)
    }
    
    fn get_universe_order(&self) -> Option<HashMap<Self::UniverseItem, usize>> {
        None // Matrix power algebras don't have a natural order
    }
    
    fn convert_to_default_value_ops(&mut self) {
        panic!("Only for basic algebras");
    }
    
    fn algebra_type(&self) -> AlgebraType {
        AlgebraType::MatrixPower
    }
}

impl std::fmt::Display for MatrixPowerAlgebra {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "MatrixPowerAlgebra({}, power={})", self.name(), self.power)
    }
}

impl std::fmt::Debug for MatrixPowerAlgebra {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("MatrixPowerAlgebra")
            .field("name", &self.name())
            .field("power", &self.power)
            .field("root_size", &self.root_size)
            .field("cardinality", &self.cardinality())
            .finish()
    }
}

/// A parameterized algebra with configurable parameters.
/// 
/// This struct represents an algebra that can be instantiated with specific
/// parameter values. Parameters can be used in expressions for set size and
/// operation definitions.
/// 
/// # Examples
/// ```
/// use uacalc::alg::ParameterizedAlgebra;
/// use std::collections::HashMap;
/// 
/// // Create a parameterized algebra
/// let param_alg = ParameterizedAlgebra::new(
///     vec!["n".to_string(), "m".to_string()],
///     "ParamAlg".to_string(),
///     "n*m".to_string(),
///     "A parameterized algebra".to_string(),
///     Vec::new()
/// );
/// 
/// // Get parameter map
/// let values = vec![3, 4];
/// let map = param_alg.get_parameter_map(&values).unwrap();
/// assert_eq!(map.get("n"), Some(&"3".to_string()));
/// assert_eq!(map.get("m"), Some(&"4".to_string()));
/// ```
#[derive(Debug, Clone)]
pub struct ParameterizedAlgebra {
    /// Names of the parameters
    pub parameter_names: Vec<String>,
    /// Name of the algebra
    pub name: String,
    /// Expression for set size (may contain parameter references)
    pub set_size_exp: String,
    /// Description of the algebra
    pub description: String,
    /// List of parameterized operations
    pub ops: Vec<ParameterizedOperation>,
}

impl ParameterizedAlgebra {
    /// Create a new ParameterizedAlgebra.
    /// 
    /// # Arguments
    /// * `parameter_names` - Names of the parameters
    /// * `name` - Name of the algebra
    /// * `set_size_exp` - Expression for set size
    /// * `description` - Description of the algebra
    /// * `ops` - List of parameterized operations
    /// 
    /// # Returns
    /// A new ParameterizedAlgebra instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::ParameterizedAlgebra;
    /// 
    /// let param_alg = ParameterizedAlgebra::new(
    ///     vec!["n".to_string()],
    ///     "Zn".to_string(),
    ///     "n".to_string(),
    ///     "Cyclic group of order n".to_string(),
    ///     Vec::new()
    /// );
    /// assert_eq!(param_alg.name, "Zn");
    /// ```
    pub fn new(
        parameter_names: Vec<String>,
        name: String,
        set_size_exp: String,
        description: String,
        ops: Vec<ParameterizedOperation>,
    ) -> Self {
        ParameterizedAlgebra {
            parameter_names,
            name,
            set_size_exp,
            description,
            ops,
        }
    }
    
    /// Create a parameter map from values.
    /// 
    /// Maps each parameter name to its corresponding value from the values list.
    /// 
    /// # Arguments
    /// * `values` - List of integer values for the parameters
    /// 
    /// # Returns
    /// * `Ok(HashMap<String, String>)` - Map from parameter names to string values
    /// * `Err(String)` - If the number of values doesn't match the number of parameters
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::ParameterizedAlgebra;
    /// 
    /// let param_alg = ParameterizedAlgebra::new(
    ///     vec!["n".to_string(), "m".to_string()],
    ///     "Example".to_string(),
    ///     "n*m".to_string(),
    ///     "".to_string(),
    ///     Vec::new()
    /// );
    /// 
    /// let map = param_alg.get_parameter_map(&vec![5, 7]).unwrap();
    /// assert_eq!(map.get("n"), Some(&"5".to_string()));
    /// assert_eq!(map.get("m"), Some(&"7".to_string()));
    /// ```
    pub fn get_parameter_map(&self, values: &[i32]) -> Result<HashMap<String, String>, String> {
        if values.len() != self.parameter_names.len() {
            return Err(format!(
                "Expected {} values but got {}",
                self.parameter_names.len(),
                values.len()
            ));
        }
        
        let mut map = HashMap::new();
        for (name, &value) in self.parameter_names.iter().zip(values.iter()) {
            map.insert(name.clone(), value.to_string());
        }
        
        Ok(map)
    }
}

impl std::fmt::Display for ParameterizedAlgebra {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "ParameterizedAlgebra(name={}, params={:?})",
            self.name, self.parameter_names
        )
    }
}

pub struct PolinLikeAlgebra {
    // TODO: Implement Polin-like algebra
}

/// A power algebra representing the direct power of a SmallAlgebra.
/// 
/// This struct represents the direct power A^n of a single algebra A, where
/// each element is a tuple of n elements from A. This is a special case of
/// ProductAlgebra where all factors are the same algebra.
/// 
/// # Examples
/// ```
/// use uacalc::alg::{PowerAlgebra, SmallAlgebra, BasicAlgebra, Algebra};
/// use std::collections::HashSet;
/// 
/// // Create a small algebra
/// let alg = Box::new(BasicAlgebra::new(
///     "A".to_string(),
///     HashSet::from([0, 1]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Create power algebra A^3
/// let power = PowerAlgebra::new_safe(alg, 3).unwrap();
/// 
/// assert_eq!(power.cardinality(), 8); // 2^3 = 8
/// assert_eq!(power.get_power(), 3);
/// ```
pub struct PowerAlgebra {
    /// The underlying product algebra
    product: ProductAlgebra,
    
    /// The root algebra that is being raised to a power
    root: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    
    /// The size of the root algebra
    root_size: i32,
    
    /// The power/exponent (number of copies)
    power: usize,
    
    /// Lazy-initialized congruence lattice
    con: Option<Box<crate::alg::conlat::CongruenceLattice<i32>>>,
    
    /// Lazy-initialized subalgebra lattice
    sub: Option<Box<crate::alg::sublat::SubalgebraLattice<i32>>>,
}

impl PowerAlgebra {
    /// Create a new PowerAlgebra from a root algebra and power.
    /// 
    /// # Arguments
    /// * `root` - The algebra to raise to a power
    /// * `power` - The power/exponent (number of copies)
    /// 
    /// # Returns
    /// * `Ok(PowerAlgebra)` - Successfully created power algebra
    /// * `Err(String)` - If power is invalid or algebra is incompatible
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{PowerAlgebra, SmallAlgebra, BasicAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1, 2]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let power = PowerAlgebra::new_safe(alg, 2).unwrap();
    /// assert_eq!(power.cardinality(), 9); // 3^2 = 9
    /// ```
    pub fn new_safe(
        root: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        power: usize
    ) -> Result<Self, String> {
        if power == 0 {
            return Err("Power cannot be zero".to_string());
        }
        
        let root_size = root.cardinality();
        if root_size < 0 {
            return Err("Cannot create power of algebra with unknown cardinality".to_string());
        }
        
        // Create a list of the same algebra repeated 'power' times
        let mut algebras = Vec::with_capacity(power);
        for _ in 0..power {
            algebras.push(root.clone_box());
        }
        
        // Create the product algebra
        let name = format!("{}^{}", root.name(), power);
        let product = ProductAlgebra::new_safe(name, algebras)?;
        
        Ok(PowerAlgebra {
            product,
            root,
            root_size,
            power,
            con: None,
            sub: None,
        })
    }
    
    /// Create a new PowerAlgebra with a custom name.
    /// 
    /// # Arguments
    /// * `name` - The name for the power algebra
    /// * `root` - The algebra to raise to a power
    /// * `power` - The power/exponent (number of copies)
    /// 
    /// # Returns
    /// * `Ok(PowerAlgebra)` - Successfully created power algebra
    /// * `Err(String)` - If power is invalid or algebra is incompatible
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{PowerAlgebra, SmallAlgebra, BasicAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let power = PowerAlgebra::new_with_name_safe(
    ///     "CustomPower".to_string(),
    ///     alg,
    ///     3
    /// ).unwrap();
    /// assert_eq!(power.name(), "CustomPower");
    /// ```
    pub fn new_with_name_safe(
        name: String,
        root: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        power: usize
    ) -> Result<Self, String> {
        if power == 0 {
            return Err("Power cannot be zero".to_string());
        }
        
        let root_size = root.cardinality();
        if root_size < 0 {
            return Err("Cannot create power of algebra with unknown cardinality".to_string());
        }
        
        // Create a list of the same algebra repeated 'power' times
        let mut algebras = Vec::with_capacity(power);
        for _ in 0..power {
            algebras.push(root.clone_box());
        }
        
        // Create the product algebra
        let product = ProductAlgebra::new_safe(name, algebras)?;
        
        Ok(PowerAlgebra {
            product,
            root,
            root_size,
            power,
            con: None,
            sub: None,
        })
    }
    
    /// Create a new PowerAlgebra (panicking version for compatibility).
    /// 
    /// # Arguments
    /// * `root` - The algebra to raise to a power
    /// * `power` - The power/exponent (number of copies)
    /// 
    /// # Panics
    /// Panics if power is invalid or algebra is incompatible
    pub fn new(
        root: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        power: usize
    ) -> Self {
        Self::new_safe(root, power).unwrap()
    }
    
    /// Create a new PowerAlgebra with a custom name (panicking version).
    /// 
    /// # Arguments
    /// * `name` - The name for the power algebra
    /// * `root` - The algebra to raise to a power
    /// * `power` - The power/exponent (number of copies)
    /// 
    /// # Panics
    /// Panics if power is invalid or algebra is incompatible
    pub fn new_with_name(
        name: String,
        root: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        power: usize
    ) -> Self {
        Self::new_with_name_safe(name, root, power).unwrap()
    }
    
    /// Get the root algebra.
    /// 
    /// # Returns
    /// A reference to the root algebra
    pub fn get_root(&self) -> &dyn SmallAlgebra<UniverseItem = i32> {
        self.root.as_ref()
    }
    
    /// Get the parent algebra (same as root for power algebra).
    /// 
    /// # Returns
    /// A reference to the root algebra
    pub fn parent(&self) -> &dyn SmallAlgebra<UniverseItem = i32> {
        self.root.as_ref()
    }
    
    /// Get the parent algebras (list containing the root algebra).
    /// 
    /// # Returns
    /// A vector containing the root algebra
    pub fn parents(&self) -> Vec<&dyn SmallAlgebra<UniverseItem = i32>> {
        vec![self.root.as_ref()]
    }
    
    /// Get the power/exponent.
    /// 
    /// # Returns
    /// The power (number of copies of the root algebra)
    pub fn get_power(&self) -> usize {
        self.power
    }
    
    /// Get the size of the root algebra.
    /// 
    /// # Returns
    /// The cardinality of the root algebra
    pub fn get_root_size(&self) -> i32 {
        self.root_size
    }
    
    /// Add operations to the power algebra.
    /// 
    /// # Arguments
    /// * `operations` - Vector of operations to add
    pub fn add_operations(&mut self, operations: Vec<Box<dyn Operation>>) {
        self.product.add_operations(operations);
    }
    
    /// Get the congruence lattice (lazy initialization).
    /// 
    /// # Returns
    /// A reference to the congruence lattice
    pub fn con(&mut self) -> &crate::alg::conlat::CongruenceLattice<i32> {
        if self.con.is_none() {
            // Create congruence lattice using the type-erased wrapper
            use crate::alg::SmallAlgebraWrapper;
            
            // Clone this algebra as a trait object
            let alg_box = Box::new(self.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
            let wrapper = Box::new(SmallAlgebraWrapper::<i32>::new(alg_box));
            self.con = Some(Box::new(crate::alg::conlat::CongruenceLattice::<i32>::new(wrapper)));
        }
        self.con.as_ref().unwrap()
    }
    
    /// Get the subalgebra lattice (lazy initialization).
    /// 
    /// # Returns
    /// A reference to the subalgebra lattice
    pub fn sub(&mut self) -> &crate::alg::sublat::SubalgebraLattice<i32> {
        if self.sub.is_none() {
            // Create SubalgebraLattice with i32 universe type
            use crate::alg::SmallAlgebraWrapper;
            
            // Clone this algebra as a trait object for the SubalgebraLattice
            let alg_box = Box::new(self.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
            let wrapper = Box::new(SmallAlgebraWrapper::<i32>::new(alg_box));
            
            match crate::alg::sublat::SubalgebraLattice::new_safe(wrapper) {
                Ok(sub_lat) => {
                    self.sub = Some(Box::new(sub_lat));
                }
                Err(e) => {
                    panic!("Failed to create SubalgebraLattice for PowerAlgebra: {}", e);
                }
            }
        }
        self.sub.as_ref().unwrap()
    }
}

impl Debug for PowerAlgebra {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("PowerAlgebra")
            .field("name", &self.product.name())
            .field("root_name", &self.root.name())
            .field("power", &self.power)
            .field("root_size", &self.root_size)
            .field("cardinality", &self.product.cardinality())
            .finish()
    }
}

impl Clone for PowerAlgebra {
    fn clone(&self) -> Self {
        PowerAlgebra {
            product: self.product.clone(),
            root: self.root.clone_box(),
            root_size: self.root_size,
            power: self.power,
            con: None, // Don't clone cached lattices
            sub: None,
        }
    }
}

impl Display for PowerAlgebra {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "PowerAlgebra({}, cardinality: {})", self.product.name(), self.product.cardinality())
    }
}

impl Algebra for PowerAlgebra {
    type UniverseItem = i32;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.product.universe()
    }
    
    fn cardinality(&self) -> i32 {
        self.product.cardinality()
    }
    
    fn input_size(&self) -> i32 {
        self.product.input_size()
    }
    
    fn is_unary(&self) -> bool {
        self.product.is_unary()
    }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.product.iterator()
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        self.product.operations()
    }
    
    fn get_operation(&self, sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        self.product.get_operation(sym)
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        self.product.get_operations_map()
    }
    
    fn name(&self) -> &str {
        self.product.name()
    }
    
    fn set_name(&mut self, name: String) {
        self.product.set_name(name);
    }
    
    fn description(&self) -> Option<&str> {
        self.product.description()
    }
    
    fn set_description(&mut self, desc: Option<String>) {
        self.product.set_description(desc);
    }
    
    fn similarity_type(&self) -> &SimilarityType {
        self.product.similarity_type()
    }
    
    fn update_similarity_type(&mut self) {
        self.product.update_similarity_type();
    }
    
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        self.product.is_similar_to(other)
    }
    
    fn make_operation_tables(&mut self) {
        self.product.make_operation_tables();
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        self.product.constant_operations()
    }
    
    fn is_idempotent(&self) -> bool {
        self.product.is_idempotent()
    }
    
    fn is_total(&self) -> bool {
        self.product.is_total()
    }
    
    fn monitoring(&self) -> bool {
        self.product.monitoring()
    }
    
    fn get_monitor(&self) -> Option<&dyn ProgressMonitor> {
        self.product.get_monitor()
    }
    
    fn set_monitor(&mut self, monitor: Option<Box<dyn ProgressMonitor>>) {
        self.product.set_monitor(monitor);
    }
}

impl SmallAlgebra for PowerAlgebra {
    fn get_operation_ref(&self, sym: &OperationSymbol) -> Option<&dyn Operation> {
        self.product.get_operation_ref(sym)
    }
    
    fn get_operations_ref(&self) -> Vec<&dyn Operation> {
        self.product.get_operations_ref()
    }
    
    fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        Box::new(self.clone())
    }
    
    fn algebra_type(&self) -> AlgebraType {
        AlgebraType::Power
    }
    
    fn get_element(&self, k: usize) -> Option<Self::UniverseItem> {
        self.product.get_element(k)
    }
    
    fn element_index(&self, elem: &Self::UniverseItem) -> Option<usize> {
        self.product.element_index(elem)
    }
    
    fn get_universe_list(&self) -> Option<Vec<Self::UniverseItem>> {
        self.product.get_universe_list()
    }
    
    fn get_universe_order(&self) -> Option<HashMap<Self::UniverseItem, usize>> {
        self.product.get_universe_order()
    }
    
    fn parent(&self) -> Option<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        Some(self.root.as_ref())
    }
    
    fn parents(&self) -> Option<Vec<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>> {
        Some(vec![self.root.as_ref()])
    }
    
    fn reset_con_and_sub(&mut self) {
        // No cached lattices in partial implementation
    }
    
    fn convert_to_default_value_ops(&mut self) {
        panic!("Only for basic algebras");
    }
}

/// A reduct algebra that represents a reduct of a SmallAlgebra to a list of Terms.
/// 
/// This struct represents a reduct of a `SmallAlgebra` to a list of `Term`s.
/// It creates operations from terms by interpreting them in the super algebra
/// and delegates universe and element access to the super algebra.
/// 
/// # Examples
/// ```
/// use uacalc::alg::{ReductAlgebra, SmallAlgebra, BasicAlgebra, Algebra};
/// use uacalc::terms::{VariableImp, NonVariableTerm, Term};
/// use uacalc::alg::op::{OperationSymbol, BasicOperation, Operation};
/// use std::collections::HashSet;
/// 
/// // Create a small algebra with operation f
/// let f_sym = OperationSymbol::new("f", 2, false);
/// let f_op = Box::new(BasicOperation::new(f_sym.clone(), 2)) as Box<dyn Operation>;
/// let alg = Box::new(BasicAlgebra::new(
///     "A".to_string(),
///     HashSet::from([0, 1]),
///     vec![f_op]
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Debug: Check if operation exists in algebra
/// let found_op = alg.get_operation_ref(&f_sym);
/// assert!(found_op.is_some(), "Operation f should exist in algebra");
/// 
/// // Debug: Check the symbol of the found operation
/// let op_symbol = found_op.unwrap().symbol();
/// assert_eq!(op_symbol.name(), "f");
/// assert_eq!(op_symbol.arity(), 2);
/// 
/// // Create terms
/// let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
/// let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
/// let f_term = Box::new(NonVariableTerm::new(f_sym, vec![x, y]));
/// 
/// // Create reduct algebra
/// let reduct = ReductAlgebra::new_safe(alg, vec![f_term]).unwrap();
/// assert_eq!(reduct.cardinality(), 2);
/// ```
#[derive(Debug)]
pub struct ReductAlgebra {
    /// The super algebra that this reduct is based on
    pub super_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    
    /// The list of terms that define the operations of this reduct
    pub term_list: Vec<Box<dyn Term>>,
    
    /// The name of this reduct algebra
    pub name: String,
    
    /// The size of the universe (cached from super algebra)
    pub size: i32,
    
    /// The universe of this algebra (same as super algebra)
    pub universe: HashSet<i32>,
    
    /// The operations created from the terms (Arc-backed)
    pub operations: Vec<Arc<dyn Operation>>,
    
    /// Lazy-initialized congruence lattice
    pub con: Option<Box<crate::alg::conlat::CongruenceLattice<i32>>>,
    
    /// Lazy-initialized subalgebra lattice
    pub sub: Option<Box<crate::alg::sublat::SubalgebraLattice<i32>>>,
    
    /// The similarity type of this algebra
    pub similarity_type: Option<SimilarityType>,
}

impl ReductAlgebra {
    /// Create a new ReductAlgebra from a super algebra and list of terms.
    /// 
    /// # Arguments
    /// * `super_algebra` - The super algebra that this reduct is based on
    /// * `term_list` - The list of terms that define the operations
    /// 
    /// # Returns
    /// * `Ok(ReductAlgebra)` - Successfully created reduct algebra
    /// * `Err(String)` - If the terms are invalid or algebra is incompatible
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{ReductAlgebra, SmallAlgebra, BasicAlgebra, Algebra};
    /// use uacalc::terms::{VariableImp, NonVariableTerm, Term};
    /// use uacalc::alg::op::{OperationSymbol, BasicOperation, Operation};
    /// use std::collections::HashSet;
    /// 
    /// let f_sym = OperationSymbol::new("f", 2, false);
    /// let f_op = Box::new(BasicOperation::new(f_sym.clone(), 2)) as Box<dyn Operation>;
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1]),
    ///     vec![f_op]
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    /// let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    /// let f_term = Box::new(NonVariableTerm::new(f_sym, vec![x, y]));
    /// 
    /// let reduct = ReductAlgebra::new_safe(alg, vec![f_term]).unwrap();
    /// assert_eq!(reduct.cardinality(), 2);
    /// ```
    pub fn new_safe(
        super_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        term_list: Vec<Box<dyn Term>>,
    ) -> Result<Self, String> {
        Self::new_with_name_safe("".to_string(), super_algebra, term_list)
    }
    
    /// Create a new ReductAlgebra with a custom name.
    /// 
    /// # Arguments
    /// * `name` - The name for the reduct algebra
    /// * `super_algebra` - The super algebra that this reduct is based on
    /// * `term_list` - The list of terms that define the operations
    /// 
    /// # Returns
    /// * `Ok(ReductAlgebra)` - Successfully created reduct algebra
    /// * `Err(String)` - If the terms are invalid or algebra is incompatible
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{ReductAlgebra, SmallAlgebra, BasicAlgebra, Algebra};
    /// use uacalc::terms::{VariableImp, NonVariableTerm, Term};
    /// use uacalc::alg::op::{OperationSymbol, BasicOperation, Operation};
    /// use std::collections::HashSet;
    /// 
    /// let f_sym = OperationSymbol::new("f", 2, false);
    /// let f_op = Box::new(BasicOperation::new(f_sym.clone(), 2)) as Box<dyn Operation>;
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1]),
    ///     vec![f_op]
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let x = Box::new(VariableImp::new("x")) as Box<dyn Term>;
    /// let y = Box::new(VariableImp::new("y")) as Box<dyn Term>;
    /// let f_term = Box::new(NonVariableTerm::new(f_sym, vec![x, y]));
    /// 
    /// let reduct = ReductAlgebra::new_with_name_safe(
    ///     "MyReduct".to_string(),
    ///     alg,
    ///     vec![f_term]
    /// ).unwrap();
    /// assert_eq!(reduct.name(), "MyReduct");
    /// ```
    pub fn new_with_name_safe(
        name: String,
        super_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        term_list: Vec<Box<dyn Term>>,
    ) -> Result<Self, String> {
        // Validate that the super algebra has a finite universe
        let size = super_algebra.cardinality();
        if size < 0 {
            return Err("Cannot create reduct of algebra with unknown cardinality".to_string());
        }
        
        // Get the universe from the super algebra
        let universe = if let Some(universe_list) = super_algebra.get_universe_list() {
            universe_list.into_iter().collect()
        } else {
            return Err("Cannot create reduct of algebra without universe list".to_string());
        };
        
        // Determine the name
        let final_name = if name.is_empty() {
            format!("Reduct({})", super_algebra.name())
        } else {
            name
        };
        
        let mut reduct = ReductAlgebra {
            super_algebra,
            term_list,
            name: final_name,
            size,
            universe,
            operations: Vec::new(),
            con: None,
            sub: None,
            similarity_type: None,
        };
        
        // Create operations from terms
        reduct.make_operation_tables()?;
        
        Ok(reduct)
    }
    
    /// Create a new ReductAlgebra (panicking version for compatibility).
    /// 
    /// # Arguments
    /// * `super_algebra` - The super algebra that this reduct is based on
    /// * `term_list` - The list of terms that define the operations
    /// 
    /// # Panics
    /// Panics if the terms are invalid or algebra is incompatible
    pub fn new(
        super_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        term_list: Vec<Box<dyn Term>>,
    ) -> Self {
        Self::new_safe(super_algebra, term_list).unwrap()
    }
    
    /// Create a new ReductAlgebra with a custom name (panicking version).
    /// 
    /// # Arguments
    /// * `name` - The name for the reduct algebra
    /// * `super_algebra` - The super algebra that this reduct is based on
    /// * `term_list` - The list of terms that define the operations
    /// 
    /// # Panics
    /// Panics if the terms are invalid or algebra is incompatible
    pub fn new_with_name(
        name: String,
        super_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        term_list: Vec<Box<dyn Term>>,
    ) -> Self {
        Self::new_with_name_safe(name, super_algebra, term_list).unwrap()
    }
    
    /// Get the super algebra.
    /// 
    /// # Returns
    /// A reference to the super algebra
    pub fn super_algebra(&self) -> &dyn SmallAlgebra<UniverseItem = i32> {
        self.super_algebra.as_ref()
    }
    
    /// Get the congruence lattice (lazy initialization).
    /// 
    /// # Returns
    /// A reference to the congruence lattice
    pub fn con(&mut self) -> &crate::alg::conlat::CongruenceLattice<i32> {
        if self.con.is_none() {
            // Create a wrapper that implements SmallAlgebra for this ReductAlgebra
            use crate::alg::SmallAlgebraWrapper;
            let wrapper = Box::new(SmallAlgebraWrapper::<i32>::new(self.super_algebra.clone_box()));
            self.con = Some(Box::new(crate::alg::conlat::CongruenceLattice::new(wrapper)));
        }
        self.con.as_ref().unwrap()
    }
    
    /// Get the subalgebra lattice (lazy initialization).
    /// 
    /// # Returns
    /// A reference to the subalgebra lattice
    pub fn sub(&mut self) -> &crate::alg::sublat::SubalgebraLattice<i32> {
        if self.sub.is_none() {
            // Create a wrapper that implements SmallAlgebra for this ReductAlgebra
            let wrapper = Box::new(SmallAlgebraWrapper::<i32>::new(self.super_algebra.clone_box()));
            self.sub = Some(Box::new(crate::alg::sublat::SubalgebraLattice::new_safe(wrapper).unwrap()));
        }
        self.sub.as_ref().unwrap()
    }
    
    /// Create operation tables from the terms.
    /// 
    /// This method interprets each term in the super algebra to create
    /// operations for this reduct algebra.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully created operations
    /// * `Err(String)` - If term interpretation fails
    pub fn make_operation_tables(&mut self) -> Result<(), String> {
        self.operations.clear();
        
        for term in &self.term_list {
            // Get the variable list for this term
            let varlist = term.get_variable_list();
            
            // Now that clone_box preserves operations, we can use it safely
            let cloned_alg = self.super_algebra.clone_box();
            let wrapper = SmallAlgebraWrapper::new(cloned_alg);
            let alg_arc = Arc::new(wrapper);
            let interpretation = term.interpretation(alg_arc, &varlist, true)?;
            
            self.operations.push(Arc::from(interpretation));
        }
        
        Ok(())
    }
    
    /// Borrowed access to Arc-backed operations to avoid cloning.
    pub fn operations_ref_arc(&self) -> &[Arc<dyn Operation>] {
        &self.operations
    }
}

impl Algebra for ReductAlgebra {
    type UniverseItem = i32;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        Box::new(self.universe.clone().into_iter())
    }
    
    fn cardinality(&self) -> i32 {
        self.size
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
        // Return boxed Arc-backed delegators without deep cloning
        self.operations
            .iter()
            .map(|op| crate::alg::op::operation::boxed_arc_op(Arc::clone(op)))
            .collect()
    }
    
    fn get_operation(&self, sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        for op in &self.operations {
            if op.symbol() == sym {
                return Some(crate::alg::op::operation::boxed_arc_op(Arc::clone(op)));
            }
        }
        None
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        let mut map = HashMap::new();
        for op in &self.operations {
            map.insert(op.symbol().clone(), crate::alg::op::operation::boxed_arc_op(Arc::clone(op)));
        }
        map
    }
    
    fn name(&self) -> &str {
        &self.name
    }
    
    fn set_name(&mut self, name: String) {
        self.name = name;
    }
    
    fn description(&self) -> Option<&str> {
        None
    }
    
    fn set_description(&mut self, desc: Option<String>) {
        // ReductAlgebra doesn't have a description field
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
        let _ = self.make_operation_tables(); // Ignore errors for now
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
        false
    }
    
    fn get_monitor(&self) -> Option<&dyn ProgressMonitor> {
        None
    }
    
    fn set_monitor(&mut self, monitor: Option<Box<dyn ProgressMonitor>>) {
        // ReductAlgebra doesn't support monitoring
    }
}

impl SmallAlgebra for ReductAlgebra {
    fn get_operation_ref(&self, sym: &OperationSymbol) -> Option<&dyn Operation> {
        for op in &self.operations {
            if op.symbol() == sym {
                return Some(op.as_ref());
            }
        }
        None
    }
    
    fn get_operations_ref(&self) -> Vec<&dyn Operation> {
        self.operations.iter().map(|op| op.as_ref()).collect()
    }
    
    fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        // We can't clone trait objects, so we'll create a new one
        // This is a limitation of the current design
        let alg = Box::new(BasicAlgebra::new(
            "ClonedSuper".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Clone the term list using clone_box()
        let cloned_terms: Vec<Box<dyn Term>> = self.term_list.iter()
            .map(|term| term.clone_box())
            .collect();
        
        Box::new(ReductAlgebra::new_safe(alg, cloned_terms).unwrap())
    }
    
    fn algebra_type(&self) -> AlgebraType {
        AlgebraType::Reduct
    }
    
    fn get_element(&self, k: usize) -> Option<Self::UniverseItem> {
        self.super_algebra.get_element(k)
    }
    
    fn element_index(&self, elem: &Self::UniverseItem) -> Option<usize> {
        self.super_algebra.element_index(elem)
    }
    
    fn get_universe_list(&self) -> Option<Vec<Self::UniverseItem>> {
        self.super_algebra.get_universe_list()
    }
    
    fn get_universe_order(&self) -> Option<HashMap<Self::UniverseItem, usize>> {
        self.super_algebra.get_universe_order()
    }
    
    fn parent(&self) -> Option<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        Some(self.super_algebra.as_ref())
    }
    
    fn parents(&self) -> Option<Vec<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>> {
        Some(vec![self.super_algebra.as_ref()])
    }
    
    fn reset_con_and_sub(&mut self) {
        // Reset any cached congruence and subalgebra lattices
        self.con = None;
        self.sub = None;
    }
    
    fn convert_to_default_value_ops(&mut self) {
        panic!("Only for basic algebras");
    }
}

impl Clone for ReductAlgebra {
    fn clone(&self) -> Self {
        // We can't clone the super_algebra trait object, so we'll create a new one
        // This is a limitation of the current design
        let alg = Box::new(BasicAlgebra::new(
            "ClonedSuper".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Clone the term list using clone_box()
        let cloned_terms: Vec<Box<dyn Term>> = self.term_list.iter()
            .map(|term| term.clone_box())
            .collect();
        
        ReductAlgebra {
            super_algebra: alg,
            term_list: cloned_terms,
            name: self.name.clone(),
            size: self.size,
            universe: self.universe.clone(),
            operations: Vec::new(), // Can't clone operations easily
            con: None, // Can't clone CongruenceLattice
            sub: None, // Can't clone SubalgebraLattice
            similarity_type: self.similarity_type.clone(),
        }
    }
}

impl std::fmt::Display for ReductAlgebra {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "ReductAlgebra({}, cardinality: {})", self.name, self.cardinality())
    }
}

// SubProductAlgebra is now implemented in sub_product_algebra.rs
pub use sub_product_algebra::SubProductAlgebra;

/// The monoid or semigroup of unary terms from a generating algebra.
/// 
/// This struct creates a monoid where each element is a unary term over
/// the generating algebra, and the binary operation is term composition.
/// 
/// # Examples
/// ```ignore
/// use uacalc::alg::{UnaryTermsMonoid, SmallAlgebra, BasicAlgebra};
/// use std::collections::HashSet;
/// 
/// // Create a generating algebra
/// let alg = Box::new(BasicAlgebra::new(
///     "A".to_string(),
///     HashSet::from([0, 1, 2]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Create unary terms monoid
/// let monoid = UnaryTermsMonoid::new_safe(alg).unwrap();
/// ```
#[derive(Debug)]
pub struct UnaryTermsMonoid {
    /// The generating algebra
    pub generating_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    
    /// The free algebra with 1 generator
    pub free_algebra: FreeAlgebra,
    
    /// List of unary terms (parallel to free_algebra's elements)
    pub unary_term_list: Vec<Box<dyn Term>>,
    
    /// The product operation
    pub operation: Option<Box<dyn Operation>>,
    
    /// Name of this algebra
    pub name: String,
    
    /// Cached congruence lattice
    pub con: Option<Box<crate::alg::conlat::CongruenceLattice<i32>>>,
    
    /// Cached subalgebra lattice
    pub sub: Option<Box<crate::alg::sublat::SubalgebraLattice<i32>>>,
}

impl UnaryTermsMonoid {
    /// Create a new UnaryTermsMonoid from a generating algebra.
    /// 
    /// # Arguments
    /// * `alg` - The generating algebra
    /// 
    /// # Returns
    /// * `Ok(UnaryTermsMonoid)` - Successfully created monoid
    /// * `Err(String)` - If construction fails
    /// 
    /// # Examples
    /// ```ignore
    /// let monoid = UnaryTermsMonoid::new_safe(alg).unwrap();
    /// ```
    pub fn new_safe(
        alg: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    ) -> Result<Self, String> {
        Self::new_with_id_safe(alg, false)
    }
    
    /// Create a new UnaryTermsMonoid with optional identity inclusion.
    /// 
    /// # Arguments
    /// * `alg` - The generating algebra
    /// * `include_id` - Whether to include the identity term
    /// 
    /// # Returns
    /// * `Ok(UnaryTermsMonoid)` - Successfully created monoid
    /// * `Err(String)` - If construction fails
    /// 
    /// # Examples
    /// ```ignore
    /// let monoid = UnaryTermsMonoid::new_with_id_safe(alg, true).unwrap();
    /// ```
    pub fn new_with_id_safe(
        alg: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        _include_id: bool,
    ) -> Result<Self, String> {
        let name = format!("UnaryTerms({})", alg.name());
        
        // Create free algebra with 1 generator
        let free_algebra = FreeAlgebra::new_safe(alg.clone_box(), 1)?;
        
        // Get all terms from the free algebra
        // We can't directly clone Box<dyn Term>, so we need to clone each one using clone_box()
        let terms = if let Some(term_list) = &free_algebra.get_inner().terms {
            term_list.iter().map(|t| t.clone_box()).collect()
        } else {
            return Err("Free algebra does not have terms".to_string());
        };
        
        let mut monoid = UnaryTermsMonoid {
            generating_algebra: alg,
            free_algebra,
            unary_term_list: terms,
            operation: None,
            name,
            con: None,
            sub: None,
        };
        
        // Create the product operation
        monoid.make_product_operation()?;
        
        Ok(monoid)
    }
    
    /// Create a new UnaryTermsMonoid (panicking version for compatibility).
    /// 
    /// # Arguments
    /// * `alg` - The generating algebra
    /// 
    /// # Panics
    /// Panics if construction fails
    pub fn new(alg: Box<dyn SmallAlgebra<UniverseItem = i32>>) -> Self {
        Self::new_safe(alg).unwrap()
    }
    
    /// Create the product operation for term composition.
    /// 
    /// This creates a binary operation where op(i, j) computes the composition
    /// of term i followed by term j, i.e., term_j(term_i(x)).
    fn make_product_operation(&mut self) -> Result<(), String> {
        let table = self.make_table()?;
        
        // Create a binary operation from the table
        let cardinality = self.unary_term_list.len();
        let product_sym = OperationSymbol::new("*", 2, true); // Product is associative
        let op = crate::alg::op::operations::make_binary_int_operation(
            product_sym,
            cardinality as i32,
            table,
        )?;
        
        self.operation = Some(op);
        Ok(())
    }
    
    /// Create the operation table for term composition.
    /// 
    /// For each pair of terms (i, j), compute the composition term_j(term_i(x))
    /// and find its index in the term list. Note the "backwards" indexing:
    /// table[j][i] instead of table[i][j].
    /// 
    /// # Returns
    /// * `Ok(Vec<Vec<i32>>)` - The 2D operation table
    /// * `Err(String)` - If table construction fails
    fn make_table(&self) -> Result<Vec<Vec<i32>>, String> {
        let n = self.generating_algebra.cardinality();
        let m = self.unary_term_list.len();
        
        // Get the variable list from the free algebra
        let varlist = if let Some(vars) = &self.free_algebra.get_inner().variables {
            // Convert VariableImp to String names
            vars.iter().map(|v| v.to_string()).collect::<Vec<String>>()
        } else {
            return Err("Free algebra does not have variables".to_string());
        };
        
        // Get the universe order map for lookups
        let univ_order = self.free_algebra.get_inner().get_universe_order();
        
        // Build a mapping from free algebra universe index to monoid term index
        // Since unary_term_list is built from free_algebra.get_inner().terms in order,
        // and free algebra's terms and universe are in the same order, we can build
        // the mapping by evaluating each term to get its element
        let mut free_to_monoid_map: HashMap<usize, usize> = HashMap::new();
        
        // Wrap the generating algebra in an Arc for term operations (reused later)
        use crate::alg::SmallAlgebraWrapper;
        let wrapper = SmallAlgebraWrapper::new(self.generating_algebra.clone_box());
        let alg_arc = Arc::new(wrapper);
        
        // For each term in unary_term_list, compute its element and find its index
        for (monoid_idx, term) in self.unary_term_list.iter().enumerate() {
            // Create a term operation to compute the element
            if let Ok(term_op) = term.interpretation(alg_arc.clone(), &varlist, true) {
                // Compute the element as IntArray by evaluating on all inputs
                let mut elem_vec = Vec::with_capacity(n as usize);
                let mut all_ok = true;
                for r in 0..n {
                    match term_op.int_value_at(&[r]) {
                        Ok(val) => elem_vec.push(val),
                        Err(_) => {
                            all_ok = false;
                            break;
                        }
                    }
                }
                if all_ok && elem_vec.len() == n as usize {
                    if let Ok(elem_array) = crate::util::int_array::IntArray::from_array(elem_vec) {
                        if let Some(free_idx) = univ_order.get(&elem_array) {
                            free_to_monoid_map.insert(*free_idx, monoid_idx);
                        }
                    }
                }
            }
        }
        
        let mut table = vec![vec![0; m]; m];
        let mut tmp = vec![0; n as usize];
        
        // alg_arc already created above for mapping
        
        for (i, term0) in self.unary_term_list.iter().enumerate() {
            // Create term operation for term0
            let term_op0 = term0.interpretation(alg_arc.clone(), &varlist, true)?;
            
            for (j, term1) in self.unary_term_list.iter().enumerate() {
                // Create term operation for term1
                let term_op1 = term1.interpretation(alg_arc.clone(), &varlist, true)?;
                
                // Compute composition: term_op0(term_op1(r)) for each r
                for r in 0..n {
                    let val1 = term_op1.int_value_at(&[r])?;
                    let val0 = term_op0.int_value_at(&[val1])?;
                    tmp[r as usize] = val0;
                }
                
                // Find the index of the resulting term in free algebra
                let tmp_array = crate::util::int_array::IntArray::from_array(tmp.clone())?;
                let free_idx = univ_order.get(&tmp_array)
                    .ok_or_else(|| "Composition result not in universe".to_string())?;
                
                // Map from free algebra index to monoid term index
                let monoid_idx = free_to_monoid_map.get(free_idx)
                    .ok_or_else(|| format!("No mapping found for free algebra index {}", free_idx))?;
                
                // Note: table[j][i] not table[i][j] - this is intentional!
                table[j][i] = *monoid_idx as i32;
            }
        }
        
        Ok(table)
    }
    
    /// Get the congruence lattice (lazy initialization).
    /// 
    /// # Returns
    /// A reference to the congruence lattice
    pub fn con(&mut self) -> &crate::alg::conlat::CongruenceLattice<i32> {
        if self.con.is_none() {
            use crate::alg::SmallAlgebraWrapper;
            
            // We can't easily get a proper SmallAlgebra<UniverseItem = i32> from this
            // For now, create a basic wrapper
            let wrapper = Box::new(SmallAlgebraWrapper::<i32>::new(self.generating_algebra.clone_box()));
            self.con = Some(Box::new(crate::alg::conlat::CongruenceLattice::<i32>::new(wrapper)));
        }
        self.con.as_ref().unwrap()
    }
    
    /// Get the subalgebra lattice (lazy initialization).
    /// 
    /// # Returns
    /// A reference to the subalgebra lattice
    pub fn sub(&mut self) -> &crate::alg::sublat::SubalgebraLattice<i32> {
        if self.sub.is_none() {
            use crate::alg::SmallAlgebraWrapper;
            
            let wrapper = Box::new(SmallAlgebraWrapper::<i32>::new(self.generating_algebra.clone_box()));
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
}

impl Algebra for UnaryTermsMonoid {
    type UniverseItem = crate::util::int_array::IntArray;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.free_algebra.universe()
    }
    
    fn cardinality(&self) -> i32 {
        self.unary_term_list.len() as i32
    }
    
    fn input_size(&self) -> i32 {
        self.free_algebra.input_size()
    }
    
    fn is_unary(&self) -> bool {
        false // Unary terms monoid has a binary product operation
    }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.free_algebra.iterator()
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        if let Some(ref op) = self.operation {
            vec![op.clone_box()]
        } else {
            Vec::new()
        }
    }
    
    fn get_operation(&self, sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        if let Some(ref op) = self.operation {
            if op.symbol() == sym {
                return Some(op.clone_box());
            }
        }
        None
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        let mut map = HashMap::new();
        if let Some(ref op) = self.operation {
            map.insert(op.symbol().clone(), op.clone_box());
        }
        map
    }
    
    fn name(&self) -> &str {
        &self.name
    }
    
    fn set_name(&mut self, name: String) {
        self.name = name;
    }
    
    fn description(&self) -> Option<&str> {
        None
    }
    
    fn set_description(&mut self, _desc: Option<String>) {
        // UnaryTermsMonoid doesn't have a description field
    }
    
    fn similarity_type(&self) -> &SimilarityType {
        // Return a similarity type with just the product operation
        static SIMILARITY_TYPE: once_cell::sync::Lazy<SimilarityType> = once_cell::sync::Lazy::new(|| {
            let product_sym = OperationSymbol::new("*", 2, true);
            SimilarityType::new(vec![product_sym])
        });
        &SIMILARITY_TYPE
    }
    
    fn update_similarity_type(&mut self) {
        // Similarity type is static for UnaryTermsMonoid
    }
    
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        self.similarity_type() == other.similarity_type()
    }
    
    fn make_operation_tables(&mut self) {
        // Operation table is already created in constructor
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        Vec::new() // Product operation is not a constant
    }
    
    fn is_idempotent(&self) -> bool {
        if let Some(ref op) = self.operation {
            op.is_idempotent().unwrap_or(false)
        } else {
            false
        }
    }
    
    fn is_total(&self) -> bool {
        if let Some(ref op) = self.operation {
            op.is_total().unwrap_or(false)
        } else {
            false
        }
    }
    
    fn monitoring(&self) -> bool {
        false
    }
    
    fn get_monitor(&self) -> Option<&dyn ProgressMonitor> {
        None
    }
    
    fn set_monitor(&mut self, _monitor: Option<Box<dyn ProgressMonitor>>) {
        // UnaryTermsMonoid doesn't support monitoring
    }
}

impl SmallAlgebra for UnaryTermsMonoid {
    fn get_operation_ref(&self, sym: &OperationSymbol) -> Option<&dyn Operation> {
        if let Some(ref op) = self.operation {
            if op.symbol() == sym {
                return Some(op.as_ref());
            }
        }
        None
    }
    
    fn get_operations_ref(&self) -> Vec<&dyn Operation> {
        if let Some(ref op) = self.operation {
            vec![op.as_ref()]
        } else {
            Vec::new()
        }
    }
    
    fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        // Create a new UnaryTermsMonoid
        match Self::new_safe(self.generating_algebra.clone_box()) {
            Ok(monoid) => Box::new(monoid),
            Err(_) => panic!("Failed to clone UnaryTermsMonoid"),
        }
    }
    
    fn algebra_type(&self) -> AlgebraType {
        AlgebraType::UnaryTermsMonoid
    }
    
    fn get_element(&self, k: usize) -> Option<Self::UniverseItem> {
        if k >= self.unary_term_list.len() {
            return None;
        }
        
        // Get the term at index k and compute its element
        let term = &self.unary_term_list[k];
        let n = self.generating_algebra.cardinality();
        
        // Get variable list
        let varlist = if let Some(vars) = &self.free_algebra.get_inner().variables {
            vars.iter().map(|v| v.to_string()).collect::<Vec<String>>()
        } else {
            return None;
        };
        
        // Create term operation
        use crate::alg::SmallAlgebraWrapper;
        let wrapper = SmallAlgebraWrapper::new(self.generating_algebra.clone_box());
        let alg_arc = Arc::new(wrapper);
        
        let term_op = match term.interpretation(alg_arc, &varlist, true) {
            Ok(op) => op,
            Err(_) => return None,
        };
        
        // Compute element by evaluating on all inputs
        let mut elem_vec = Vec::with_capacity(n as usize);
        for r in 0..n {
            match term_op.int_value_at(&[r]) {
                Ok(val) => elem_vec.push(val),
                Err(_) => return None,
            }
        }
        
        crate::util::int_array::IntArray::from_array(elem_vec).ok()
    }
    
    fn element_index(&self, elem: &Self::UniverseItem) -> Option<usize> {
        // Search through unary_term_list to find the term that produces this element
        let n = self.generating_algebra.cardinality();
        
        // Get variable list
        let varlist = if let Some(vars) = &self.free_algebra.get_inner().variables {
            vars.iter().map(|v| v.to_string()).collect::<Vec<String>>()
        } else {
            return None;
        };
        
        // Create term operation wrapper
        use crate::alg::SmallAlgebraWrapper;
        let wrapper = SmallAlgebraWrapper::new(self.generating_algebra.clone_box());
        let alg_arc = Arc::new(wrapper);
        
        for (idx, term) in self.unary_term_list.iter().enumerate() {
            if let Ok(term_op) = term.interpretation(alg_arc.clone(), &varlist, true) {
                // Compute element for this term
                let mut elem_vec = Vec::with_capacity(n as usize);
                let mut all_ok = true;
                for r in 0..n {
                    match term_op.int_value_at(&[r]) {
                        Ok(val) => elem_vec.push(val),
                        Err(_) => {
                            all_ok = false;
                            break;
                        }
                    }
                }
                if all_ok && elem_vec.len() == n as usize {
                    if let Ok(term_elem) = crate::util::int_array::IntArray::from_array(elem_vec) {
                        if &term_elem == elem {
                            return Some(idx);
                        }
                    }
                }
            }
        }
        None
    }
    
    fn get_universe_list(&self) -> Option<Vec<Self::UniverseItem>> {
        // Compute elements for all terms in unary_term_list
        let n = self.generating_algebra.cardinality();
        
        // Get variable list
        let varlist = if let Some(vars) = &self.free_algebra.get_inner().variables {
            vars.iter().map(|v| v.to_string()).collect::<Vec<String>>()
        } else {
            return None;
        };
        
        // Create term operation wrapper
        use crate::alg::SmallAlgebraWrapper;
        let wrapper = SmallAlgebraWrapper::new(self.generating_algebra.clone_box());
        let alg_arc = Arc::new(wrapper);
        
        let mut universe = Vec::with_capacity(self.unary_term_list.len());
        for term in &self.unary_term_list {
            if let Ok(term_op) = term.interpretation(alg_arc.clone(), &varlist, true) {
                // Compute element by evaluating on all inputs
                let mut elem_vec = Vec::with_capacity(n as usize);
                let mut all_ok = true;
                for r in 0..n {
                    match term_op.int_value_at(&[r]) {
                        Ok(val) => elem_vec.push(val),
                        Err(_) => {
                            all_ok = false;
                            break;
                        }
                    }
                }
                if all_ok && elem_vec.len() == n as usize {
                    if let Ok(elem_array) = crate::util::int_array::IntArray::from_array(elem_vec) {
                        universe.push(elem_array);
                    } else {
                        return None;
                    }
                } else {
                    return None;
                }
            } else {
                return None;
            }
        }
        Some(universe)
    }
    
    fn get_universe_order(&self) -> Option<HashMap<Self::UniverseItem, usize>> {
        // Build order map from unary_term_list
        if let Some(universe) = self.get_universe_list() {
            let mut order = HashMap::new();
            for (idx, elem) in universe.iter().enumerate() {
                order.insert(elem.clone(), idx);
            }
            Some(order)
        } else {
            None
        }
    }
    
    fn parent(&self) -> Option<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        None // Type mismatch - generating_algebra has different UniverseItem type
    }
    
    fn parents(&self) -> Option<Vec<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>> {
        None // Type mismatch
    }
    
    fn reset_con_and_sub(&mut self) {
        self.con = None;
        self.sub = None;
    }
    
    fn convert_to_default_value_ops(&mut self) {
        panic!("Only for basic algebras");
    }
}

impl Display for UnaryTermsMonoid {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "UnaryTermsMonoid({}, cardinality: {})", self.name, self.cardinality())
    }
}

pub mod maltsev_product_decomposition;

pub use maltsev_product_decomposition::MaltsevProductDecomposition;

pub struct MaltsevDecompositionIterator {
    // TODO: Implement Maltsev decomposition iterator
}

pub mod malcev;

// Re-export malcev functions for convenience
pub use malcev::{
    malcev_term, majority_term, minority_term, pixley_term,
    nu_term, nu_term_idempotent, weak_nu_term, weak_majority_term,
    semilattice_term, difference_term, jonsson_terms,
    hagemann_mitschke_terms, gumm_terms, join_term,
    sd_meet_terms, sd_terms, markovic_mckenzie_siggers_taylor_term,
    weak_3_edge_term, is_congruence_dist_idempotent,
    is_congruence_modular_idempotent, congruence_modular_variety,
    jonsson_level, local_distributivity_level, day_quadruple,
    cyclic_term_idempotent,
};
