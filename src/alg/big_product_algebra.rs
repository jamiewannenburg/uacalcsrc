/*!
 * BigProductAlgebra - Product of SmallAlgebras that may be too large for SmallAlgebra.
 * 
 * This is a partial implementation of org.uacalc.alg.BigProductAlgebra,
 * implementing just enough functionality for Closer to work.
 */

use std::collections::{HashMap, HashSet};
use std::fmt;
use std::hash::Hash;
use crate::alg::{Algebra, SmallAlgebra, algebra::ProgressMonitor};
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};
use crate::util::int_array::IntArray;
use crate::terms::{Term, NonVariableTerm};

/// A product algebra that may be too large to be a SmallAlgebra.
/// 
/// This struct represents the direct product of SmallAlgebras, using IntArray
/// for elements. After we have a real element scheme, we'll use that.
/// 
/// # Examples
/// ```
/// use uacalc::alg::{BigProductAlgebra, SmallAlgebra, BasicSmallAlgebra};
/// use std::collections::HashSet;
/// 
/// // Create two small algebras
/// let alg1 = Box::new(BasicSmallAlgebra::new(
///     "A1".to_string(),
///     HashSet::from([0, 1]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// let alg2 = Box::new(BasicSmallAlgebra::new(
///     "A2".to_string(),
///     HashSet::from([0, 1, 2]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Create product algebra
/// let product = BigProductAlgebra::new_safe(vec![alg1, alg2]).unwrap();
/// assert_eq!(product.get_number_of_factors(), 2);
/// ```
#[derive(Debug)]
pub struct BigProductAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + std::fmt::Debug + Send + Sync + 'static
{
    /// Name of the algebra
    name: String,
    
    /// Description of the algebra
    description: Option<String>,
    
    /// The factor algebras
    algebras: Vec<Box<dyn SmallAlgebra<UniverseItem = T>>>,
    
    /// Sizes of each factor
    sizes: Vec<i32>,
    
    /// Number of factors
    number_of_factors: usize,
    
    /// Constants in this algebra
    constants: Option<Vec<IntArray>>,
    
    /// Map from constants to their symbols
    pub constant_to_symbol: Option<HashMap<IntArray, OperationSymbol>>,
    
    /// Cardinality (-2 = not calculated, -1 = too big)
    cardinality: i32,
    
    /// Root algebras (for powers)
    root_algebras: Option<Vec<Box<dyn SmallAlgebra<UniverseItem = T>>>>,
    
    /// Powers (for powers)
    powers: Option<Vec<i32>>,
    
    /// Operations on this algebra
    operations: Vec<Box<dyn Operation>>,
    
    /// Similarity type
    similarity_type: Option<SimilarityType>,
    
    /// Progress monitor
    monitor: Option<Box<dyn ProgressMonitor>>,
}

impl<T> BigProductAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + std::fmt::Debug + Send + Sync + 'static
{
    /// Construct the direct product of a list of SmallAlgebras.
    /// 
    /// # Arguments
    /// * `algebras` - Vector of SmallAlgebras to take the product of
    /// 
    /// # Returns
    /// * `Ok(BigProductAlgebra)` - Successfully created product
    /// * `Err(String)` - If algebras are incompatible
    pub fn new_safe(
        algebras: Vec<Box<dyn SmallAlgebra<UniverseItem = T>>>
    ) -> Result<Self, String> {
        Self::new_with_name_safe("".to_string(), algebras)
    }
    
    /// Construct the direct product with a custom name.
    /// 
    /// # Arguments
    /// * `name` - Name for the product algebra
    /// * `algebras` - Vector of SmallAlgebras to take the product of
    /// 
    /// # Returns
    /// * `Ok(BigProductAlgebra)` - Successfully created product
    /// * `Err(String)` - If algebras are incompatible
    pub fn new_with_name_safe(
        name: String,
        algebras: Vec<Box<dyn SmallAlgebra<UniverseItem = T>>>
    ) -> Result<Self, String> {
        if algebras.is_empty() {
            return Err("Cannot create product of empty list of algebras".to_string());
        }
        
        let number_of_factors = algebras.len();
        let mut sizes = Vec::with_capacity(number_of_factors);
        
        for alg in &algebras {
            sizes.push(alg.cardinality());
        }
        
        let mut product = BigProductAlgebra {
            name,
            description: None,
            algebras,
            sizes,
            number_of_factors,
            constants: None,
            constant_to_symbol: None,
            cardinality: -2,
            root_algebras: None,
            powers: None,
            operations: Vec::new(),
            similarity_type: None,
            monitor: None,
        };
        
        product.make_operations();
        
        Ok(product)
    }
    
    /// Construct the direct power of a SmallAlgebra.
    /// 
    /// # Arguments
    /// * `alg` - The algebra to raise to a power
    /// * `power` - The power
    /// 
    /// # Returns
    /// * `Ok(BigProductAlgebra)` - Successfully created power
    /// * `Err(String)` - If power is invalid
    pub fn new_power_safe(
        alg: Box<dyn SmallAlgebra<UniverseItem = T>>,
        power: usize
    ) -> Result<Self, String> {
        Self::new_power_with_name_safe("".to_string(), alg, power)
    }
    
    /// Construct the direct power with a custom name.
    /// 
    /// # Arguments
    /// * `name` - Name for the power algebra
    /// * `alg` - The algebra to raise to a power
    /// * `power` - The power
    /// 
    /// # Returns
    /// * `Ok(BigProductAlgebra)` - Successfully created power
    /// * `Err(String)` - If power is invalid
    pub fn new_power_with_name_safe(
        name: String,
        alg: Box<dyn SmallAlgebra<UniverseItem = T>>,
        power: usize
    ) -> Result<Self, String> {
        if power == 0 {
            return Err("Power must be positive".to_string());
        }
        
        let root_algebras = vec![alg];
        let powers = vec![power as i32];
        
        Self::setup(name, root_algebras, powers)
    }
    
    /// Setup a product with powers.
    fn setup(
        name: String,
        root_algs: Vec<Box<dyn SmallAlgebra<UniverseItem = T>>>,
        powers: Vec<i32>
    ) -> Result<Self, String> {
        if root_algs.len() != powers.len() {
            return Err("Number of algebras must match number of powers".to_string());
        }
        
        let mut algebras = Vec::new();
        let mut number_of_factors = 0;
        
        for (i, pow) in powers.iter().enumerate() {
            let alg = &root_algs[i];
            number_of_factors += *pow as usize;
            for _ in 0..*pow {
                algebras.push(alg.clone_box());
            }
        }
        
        let mut sizes = Vec::with_capacity(number_of_factors);
        for alg in &algebras {
            sizes.push(alg.cardinality());
        }
        
        let mut product = BigProductAlgebra {
            name,
            description: None,
            algebras,
            sizes,
            number_of_factors,
            constants: None,
            constant_to_symbol: None,
            cardinality: -2,
            root_algebras: Some(root_algs),
            powers: Some(powers),
            operations: Vec::new(),
            similarity_type: None,
            monitor: None,
        };
        
        product.make_operations();
        
        Ok(product)
    }
    
    /// Make operations on the product algebra.
    /// 
    /// This creates operations on the product that apply componentwise.
    fn make_operations(&mut self) {
        // For now, stub this out - in full implementation this would create
        // product operations that apply componentwise
        self.operations = Vec::new();
        
        // Get operations from first algebra as a template
        if !self.algebras.is_empty() {
            let _first_ops = self.algebras[0].operations();
            // For each operation in the first algebra, we would create a
            // corresponding product operation
            // TODO: Implement full operation creation
        }
    }
    
    /// Get constants in this algebra.
    /// 
    /// # Returns
    /// A vector of IntArray constants
    pub fn get_constants(&mut self) -> Vec<IntArray> {
        if let Some(ref constants) = self.constants {
            return constants.clone();
        }
        
        let constants = Vec::new();
        let constant_to_symbol = HashMap::new();
        let _hash: HashSet<IntArray> = HashSet::new();
        
        for op in &self.operations {
            if op.arity() == 0 {
                // This is a constant - evaluate it
                // TODO: Implement proper evaluation
            }
        }
        
        self.constants = Some(constants.clone());
        self.constant_to_symbol = Some(constant_to_symbol);
        
        constants
    }
    
    /// Get the symbol for a constant.
    /// 
    /// # Arguments
    /// * `constant` - The constant to look up
    /// 
    /// # Returns
    /// The operation symbol for this constant, if it exists
    pub fn get_constant_symbol(&mut self, constant: &IntArray) -> Option<OperationSymbol> {
        self.get_constants(); // Ensure constants are initialized
        self.constant_to_symbol.as_ref()?.get(constant).cloned()
    }
    
    /// Get the term for a constant.
    /// 
    /// # Arguments
    /// * `constant` - The constant to get a term for
    /// 
    /// # Returns
    /// * `Ok(Term)` - The term for this constant
    /// * `Err(String)` - If constant not found
    pub fn get_constant_term(&mut self, constant: &IntArray) -> Result<Box<dyn Term>, String> {
        let symbol = self.get_constant_symbol(constant)
            .ok_or_else(|| "Constant not found".to_string())?;
        
        Ok(Box::new(NonVariableTerm::new(symbol, Vec::new())))
    }
    
    /// Get the number of factors.
    /// 
    /// # Returns
    /// The number of factors in this product
    pub fn get_number_of_factors(&self) -> usize {
        self.number_of_factors
    }
    
    /// Get the factors list.
    /// 
    /// # Returns
    /// A reference to the list of factor algebras
    pub fn factors(&self) -> &[Box<dyn SmallAlgebra<UniverseItem = T>>] {
        &self.algebras
    }
    
    /// Get the root factors (for powers).
    /// 
    /// # Returns
    /// The list of root algebras, if this is a power
    pub fn root_factors(&self) -> Option<&[Box<dyn SmallAlgebra<UniverseItem = T>>]> {
        self.root_algebras.as_deref()
    }
    
    /// Get the powers (for powers).
    /// 
    /// # Returns
    /// The powers array, if this is a power
    pub fn get_powers(&self) -> Option<&[i32]> {
        self.powers.as_deref()
    }
    
    /// Check if this is a power algebra.
    /// 
    /// # Returns
    /// `true` if this is a power of a single algebra
    pub fn is_power(&self) -> bool {
        self.powers.is_some()
    }
    
    /// Make operation tables for all operations.
    pub fn make_operation_tables(&mut self) {
        for op in &mut self.operations {
            let _ = op.make_table();
        }
        
        // Also make tables for factor algebras
        for alg in &mut self.algebras {
            alg.make_operation_tables();
        }
    }
    
    /// Compute the subalgebra generated by the given elements.
    /// 
    /// # Arguments
    /// * `elems` - The generating elements
    /// 
    /// # Returns
    /// * `Ok(Vec<IntArray>)` - The closed subalgebra
    /// * `Err(String)` - If closure fails
    pub fn sg_close(&self, elems: Vec<IntArray>) -> Result<Vec<IntArray>, String> {
        self.sg_close_with_term_map(elems, None)
    }
    
    /// Compute the subalgebra with term map.
    /// 
    /// # Arguments
    /// * `elems` - The generating elements
    /// * `term_map` - Optional term map
    /// 
    /// # Returns
    /// * `Ok(Vec<IntArray>)` - The closed subalgebra
    /// * `Err(String)` - If closure fails
    pub fn sg_close_with_term_map(
        &self,
        elems: Vec<IntArray>,
        term_map: Option<HashMap<IntArray, Box<dyn Term>>>
    ) -> Result<Vec<IntArray>, String> {
        self.sg_close_full(elems, 0, term_map, None, None)
    }
    
    /// Full closure method with all parameters.
    /// 
    /// # Arguments
    /// * `elems` - The generating elements
    /// * `closed_mark` - Index up to which elements are already closed
    /// * `term_map` - Optional term map
    /// * `elt` - Optional element to find during closure
    /// * `report` - Optional progress reporter
    /// 
    /// # Returns
    /// * `Ok(Vec<IntArray>)` - The closed subalgebra
    /// * `Err(String)` - If closure fails
    pub fn sg_close_full(
        &self,
        elems: Vec<IntArray>,
        _closed_mark: usize,
        term_map: Option<HashMap<IntArray, Box<dyn Term>>>,
        elt: Option<IntArray>,
        report: Option<std::sync::Arc<dyn crate::progress::ProgressReport>>
    ) -> Result<Vec<IntArray>, String> {
        use std::sync::Arc;
        
        // Make a copy of elements (don't modify input)
        let elems_copy = elems.clone();
        
        // Create closer
        let algebra_arc = Arc::new(self.clone());
        let mut closer = crate::alg::Closer::new_safe(algebra_arc, elems_copy)?;
        
        // Set optional parameters
        if let Some(tm) = term_map {
            closer.set_term_map(Some(tm));
        }
        
        if let Some(e) = elt {
            closer.set_element_to_find(Some(e));
        }
        
        if let Some(r) = report {
            closer.set_progress_report(Some(r));
        }
        
        // Compute closure
        closer.sg_close()
    }
    
    /// Get the projection algebra for the k-th factor.
    /// 
    /// # Arguments
    /// * `k` - The index of the factor to project to
    /// 
    /// # Returns
    /// * `Ok(Box<dyn SmallAlgebra>)` - The k-th factor algebra
    /// * `Err(String)` - If k is out of bounds
    pub fn projection(&self, k: usize) -> Result<Box<dyn SmallAlgebra<UniverseItem = T>>, String> {
        if k >= self.number_of_factors {
            return Err(format!("Factor index {} out of bounds (max: {})", k, self.number_of_factors - 1));
        }
        
        Ok(self.algebras[k].clone_box())
    }
    
    /// Get size multiplicities for this product algebra.
    /// 
    /// # Returns
    /// A map from size to count of algebras with that size
    pub fn size_multiplicities(&self) -> std::collections::BTreeMap<i32, i32> {
        let mut multiplicities = std::collections::BTreeMap::new();
        
        for &size in &self.sizes {
            *multiplicities.entry(size).or_insert(0) += 1;
        }
        
        multiplicities
    }
    
    /// Get the projection kernel for the k-th factor.
    /// 
    /// # Arguments
    /// * `k` - The index of the factor
    /// 
    /// # Returns
    /// * `Ok(BasicPartition)` - The projection kernel
    /// * `Err(String)` - If k is out of bounds or not implemented
    pub fn projection_kernel(&self, k: usize) -> Result<crate::alg::conlat::partition::Partition, String> {
        if k >= self.number_of_factors {
            return Err(format!("Factor index {} out of bounds (max: {})", k, self.number_of_factors - 1));
        }
        
        // TODO: Implement projection kernel calculation
        // This would require understanding the equivalence relation
        // induced by the projection map
        Err("Projection kernel calculation not yet implemented".to_string())
    }
    
    /// Get the congruence lattice of this algebra.
    /// 
    /// **Note**: BigProductAlgebra does not implement SmallAlgebra because product
    /// algebras can be extremely large or conceptually infinite. Congruence lattices
    /// are only computable for SmallAlgebras.
    /// 
    /// To compute congruences of a product algebra:
    /// 1. Use SubProductAlgebra if you have a finite subalgebra
    /// 2. Use QuotientAlgebra if you want to quotient first
    /// 3. Compute congruences on the factor algebras separately
    /// 
    /// # Panics
    /// This method panics because BigProductAlgebra doesn't implement SmallAlgebra.
    /// 
    /// # Returns
    /// Does not return - panics with explanation
    pub fn con(&self) -> ! {
        panic!(
            "con() is not available for BigProductAlgebra. BigProductAlgebra does not \
            implement SmallAlgebra because product algebras can be extremely large. \
            To compute congruences, use SubProductAlgebra for finite subalgebras."
        )
    }
}

impl<T> Clone for BigProductAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + std::fmt::Debug + Send + Sync + 'static
{
    fn clone(&self) -> Self {
        BigProductAlgebra {
            name: self.name.clone(),
            description: self.description.clone(),
            algebras: self.algebras.iter().map(|a| a.clone_box()).collect(),
            sizes: self.sizes.clone(),
            number_of_factors: self.number_of_factors,
            constants: self.constants.clone(),
            constant_to_symbol: self.constant_to_symbol.clone(),
            cardinality: self.cardinality,
            root_algebras: self.root_algebras.as_ref().map(|v| v.iter().map(|a| a.clone_box()).collect()),
            powers: self.powers.clone(),
            operations: Vec::new(), // Can't clone operations easily
            similarity_type: None,
            monitor: None,
        }
    }
}

impl<T> fmt::Display for BigProductAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + std::fmt::Debug + Send + Sync + 'static
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "BigProductAlgebra({})", self.name)
    }
}

impl<T> Algebra for BigProductAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + std::fmt::Debug + Send + Sync + 'static
{
    type UniverseItem = IntArray;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        // Create an iterator over all possible combinations
        // For now, return empty iterator to avoid memory issues with large products
        // TODO: Implement proper universe iteration for small products
        Box::new(std::iter::empty())
    }
    
    fn cardinality(&self) -> i32 {
        if self.cardinality > -2 {
            return self.cardinality;
        }
        
        // Calculate cardinality using ProductAlgebra logic
        let mut total_size = 1i64;
        for &size in &self.sizes {
            total_size *= size as i64;
            // Check for overflow
            if total_size > i32::MAX as i64 {
                return -1; // Too big
            }
        }
        
        total_size as i32
    }
    
    fn input_size(&self) -> i32 {
        self.number_of_factors as i32
    }
    
    fn is_unary(&self) -> bool {
        if self.algebras.is_empty() {
            return true;
        }
        
        for alg in &self.algebras {
            if !alg.is_unary() {
                return false;
            }
        }
        
        true
    }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.universe()
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        // Return clones of operations
        // For now, return empty vec since operations are not fully implemented
        // TODO: Implement proper operation creation
        Vec::new()
    }
    
    fn get_operation(&self, _sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        None
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
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
        // Return cached similarity type or create a default one
        // For now, create a simple one
        static DEFAULT: once_cell::sync::Lazy<SimilarityType> = 
            once_cell::sync::Lazy::new(|| SimilarityType::new(Vec::new()));
        &DEFAULT
    }
    
    fn update_similarity_type(&mut self) {
        // Update similarity type from operations
        // TODO: Implement
    }
    
    fn is_similar_to(&self, _other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        // TODO: Implement proper similarity check
        false
    }
    
    fn make_operation_tables(&mut self) {
        self.make_operation_tables();
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        Vec::new()
    }
    
    fn is_idempotent(&self) -> bool {
        for alg in &self.algebras {
            if !alg.is_idempotent() {
                return false;
            }
        }
        true
    }
    
    fn is_total(&self) -> bool {
        for alg in &self.algebras {
            if !alg.is_total() {
                return false;
            }
        }
        true
    }
    
    fn monitoring(&self) -> bool {
        self.monitor.is_some()
    }
    
    fn get_monitor(&self) -> Option<&dyn ProgressMonitor> {
        self.monitor.as_deref()
    }
    
    fn set_monitor(&mut self, monitor: Option<Box<dyn ProgressMonitor>>) {
        self.monitor = monitor;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::BasicSmallAlgebra;
    use std::collections::HashSet;
    
    #[test]
    fn test_new_product() {
        let alg1 = Box::new(BasicSmallAlgebra::new(
            "A1".to_string(),
            HashSet::from([0, 1]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let alg2 = Box::new(BasicSmallAlgebra::new(
            "A2".to_string(),
            HashSet::from([0, 1, 2]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let product = BigProductAlgebra::<i32>::new_safe(vec![alg1, alg2]).unwrap();
        assert_eq!(product.get_number_of_factors(), 2);
    }
    
    #[test]
    fn test_new_power() {
        let alg = Box::new(BasicSmallAlgebra::new(
            "A".to_string(),
            HashSet::from([0, 1]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let power = BigProductAlgebra::<i32>::new_power_safe(alg, 3).unwrap();
        assert_eq!(power.get_number_of_factors(), 3);
        assert!(power.is_power());
    }
}

