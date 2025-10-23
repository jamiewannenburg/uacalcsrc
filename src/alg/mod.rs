use std::collections::HashMap;
use std::fmt::{Debug, Display};
use crate::util::int_array::IntArrayTrait;
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};

pub mod algebra;
pub mod conlat;
pub mod general_algebra;
pub mod op;
pub mod parallel;
pub mod product_algebra;
pub mod small_algebra;
pub mod subalgebra;
pub mod sublat;

#[cfg(test)]
mod matrix_power_algebra_tests;

// Re-export partition types for convenience
pub use conlat::partition::{Partition, PrintType};

// Re-export algebra types
pub use algebra::{
    Algebra, CloneableAlgebra, BoxedAlgebra, boxed_algebra, ProgressMonitor,
    CARDINALITY_UNKNOWN, CARDINALITY_FINITE, CARDINALITY_INFINITE,
    CARDINALITY_COUNTABLE, CARDINALITY_COUNTABLY_INFINITE
};

// Re-export concrete algebra implementations
pub use general_algebra::GeneralAlgebra;
pub use small_algebra::{SmallAlgebra, BasicSmallAlgebra, AlgebraType};
pub use subalgebra::Subalgebra;
pub use product_algebra::ProductAlgebra;

// PowerAlgebra is implemented in this file (mod.rs)

// BasicAlgebra is now implemented as BasicSmallAlgebra
// GeneralAlgebra is now implemented in general_algebra.rs
// ProductAlgebra is now implemented in product_algebra.rs
// Subalgebra is now implemented in subalgebra.rs

pub struct FreeAlgebra {
    // TODO: Implement free algebra structure
}

pub struct QuotientAlgebra {
    // TODO: Implement quotient algebra structure
}

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
    /// use uacalc::alg::{Homomorphism, SmallAlgebra, BasicSmallAlgebra};
    /// use std::collections::{HashMap, HashSet};
    /// 
    /// // Create mock algebras
    /// let domain = Box::new(BasicSmallAlgebra::new(
    ///     "domain".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let range = Box::new(BasicSmallAlgebra::new(
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
    /// use uacalc::alg::{Homomorphism, SmallAlgebra, BasicSmallAlgebra};
    /// use std::collections::{HashMap, HashSet};
    /// 
    /// // Create mock algebras
    /// let domain = Box::new(BasicSmallAlgebra::new(
    ///     "domain".to_string(),
    ///     HashSet::from([0, 1, 2]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let range = Box::new(BasicSmallAlgebra::new(
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
    /// use uacalc::alg::{Homomorphism, SmallAlgebra, BasicSmallAlgebra};
    /// use uacalc::util::int_array::IntArrayTrait;
    /// use std::collections::{HashMap, HashSet};
    /// 
    /// // Create mock algebras
    /// let domain = Box::new(BasicSmallAlgebra::new(
    ///     "domain".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let range1 = Box::new(BasicSmallAlgebra::new(
    ///     "range1".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let range2 = Box::new(BasicSmallAlgebra::new(
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

pub struct Closer {
    // TODO: Implement closer structure
}

pub struct Algebras {
    // TODO: Implement algebras collection
}

pub struct AlgebraFromMinimalSets {
    // TODO: Implement algebra from minimal sets
}

pub struct AlgebraWithGeneratingVector {
    // TODO: Implement algebra with generating vector
}

pub struct BigProductAlgebra {
    // TODO: Implement big product algebra
}

/// A matrix power algebra that extends PowerAlgebra with matrix-specific operations.
/// 
/// This struct represents the direct power A^n of a single algebra A, where
/// each element is a tuple of n elements from A, with additional matrix operations
/// like left shift and diagonal operations.
/// 
/// # Examples
/// ```
/// use uacalc::alg::{MatrixPowerAlgebra, SmallAlgebra, BasicSmallAlgebra, Algebra};
/// use std::collections::HashSet;
/// 
/// // Create a small algebra
/// let alg = Box::new(BasicSmallAlgebra::new(
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
    /// use uacalc::alg::{MatrixPowerAlgebra, SmallAlgebra, BasicSmallAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicSmallAlgebra::new(
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
    /// use uacalc::alg::{MatrixPowerAlgebra, SmallAlgebra, BasicSmallAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicSmallAlgebra::new(
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
        let new_root = Box::new(BasicSmallAlgebra::new(
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
    /// use uacalc::alg::{MatrixPowerAlgebra, SmallAlgebra, BasicSmallAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicSmallAlgebra::new(
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
        self.power_algebra.get_operation_ref(sym)
    }
    
    fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        // We can't clone trait objects, so we'll create a new one
        // This is a limitation of the current design
        let alg = Box::new(BasicSmallAlgebra::new(
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

pub struct ParameterizedAlgebra {
    // TODO: Implement parameterized algebra
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
/// use uacalc::alg::{PowerAlgebra, SmallAlgebra, BasicSmallAlgebra, Algebra};
/// use std::collections::HashSet;
/// 
/// // Create a small algebra
/// let alg = Box::new(BasicSmallAlgebra::new(
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
    /// use uacalc::alg::{PowerAlgebra, SmallAlgebra, BasicSmallAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicSmallAlgebra::new(
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
    /// use uacalc::alg::{PowerAlgebra, SmallAlgebra, BasicSmallAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicSmallAlgebra::new(
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

pub struct ReductAlgebra {
    // TODO: Implement reduct algebra
}

pub struct SubProductAlgebra {
    // TODO: Implement subproduct algebra
}

pub struct UnaryTermsMonoid {
    // TODO: Implement unary terms monoid
}

pub struct MaltsevDecompositionIterator {
    // TODO: Implement Maltsev decomposition iterator
}

pub struct MaltsevProductDecomposition {
    // TODO: Implement Maltsev product decomposition
}

pub struct Malcev {
    // TODO: Implement Malcev structure
}
