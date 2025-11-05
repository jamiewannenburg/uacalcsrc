/*!
 * BigProductAlgebra - Product of SmallAlgebras that may be too large for SmallAlgebra.
 * 
 * This is a partial implementation of org.uacalc.alg.BigProductAlgebra,
 * implementing just enough functionality for Closer to work.
 */

use std::collections::{HashMap, HashSet};
use std::fmt;
use std::hash::Hash;
use std::sync::Arc;
use crate::alg::{Algebra, SmallAlgebra, algebra::ProgressMonitor};
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};
use crate::alg::op::operation::boxed_arc_op;
use crate::util::int_array::IntArray;
use crate::terms::{Term, NonVariableTerm};

/// An operation on a BigProductAlgebra that applies componentwise.
/// 
/// Each operation on the product is defined by applying the corresponding
/// operation from each factor algebra to the corresponding component.
struct BigProductOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + std::fmt::Debug + Send + Sync + 'static
{
    symbol: OperationSymbol,
    arity: i32,
    number_of_factors: usize,
    /// The operations from each factor algebra
    op_list: Vec<Arc<dyn Operation>>,
    /// The factor algebras (needed to convert indices to elements for IntArray universes)
    factor_algebras: Vec<Box<dyn SmallAlgebra<UniverseItem = T>>>,
}

impl<T> BigProductOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + std::fmt::Debug + Send + Sync + 'static
{
    fn new(
        symbol: OperationSymbol,
        arity: i32,
        number_of_factors: usize,
        op_list: Vec<Arc<dyn Operation>>,
        factor_algebras: Vec<Box<dyn SmallAlgebra<UniverseItem = T>>>,
    ) -> Self {
        BigProductOperation {
            symbol,
            arity,
            number_of_factors,
            op_list,
            factor_algebras,
        }
    }
}

impl<T> fmt::Debug for BigProductOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + std::fmt::Debug + Send + Sync + 'static
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("BigProductOperation")
            .field("symbol", &self.symbol)
            .field("arity", &self.arity)
            .field("number_of_factors", &self.number_of_factors)
            .finish()
    }
}

impl<T> fmt::Display for BigProductOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + std::fmt::Debug + Send + Sync + 'static
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "BigProductOp({})", self.symbol)
    }
}

impl<T> Operation for BigProductOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + std::fmt::Debug + Send + Sync + 'static
{
    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn arity(&self) -> i32 {
        self.arity
    }
    
    fn get_set_size(&self) -> i32 {
        -1 // Product may be too large
    }
    
    fn int_value_at(&self, _args: &[i32]) -> Result<i32, String> {
        Err("BigProductOperation does not support int_value_at".to_string())
    }
    
    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
        // args is a slice of IntArrays (each is &[i32])
        // We need to apply the operation componentwise
        let mut ans = vec![0; self.number_of_factors];
        
        // Special case for nullary operations (arity 0)
        if self.arity == 0 {
            // For nullary operations, apply the operation once per factor
            for j in 0..self.number_of_factors {
                ans[j] = self.op_list[j].int_value_at(&[])?;
            }
            return Ok(ans);
        }
        
        // Check if factor algebras have IntArray elements
        // Use algebra type as a heuristic
        use crate::alg::AlgebraType;
        let has_int_array_elements = matches!(
            self.factor_algebras[0].algebra_type(), 
            AlgebraType::Free | AlgebraType::Subproduct
        );
        
        if has_int_array_elements {
            // For factor algebras with IntArray elements (e.g., FreeAlgebra),
            // SubProductOpWrapper.int_value_at handles index-to-element conversion internally.
            // We call int_value_at directly - SubProductOpWrapper should handle conversion correctly.
            for j in 0..self.number_of_factors {
                // Extract indices for this component
                let arg_indices: Vec<i32> = args.iter().map(|a| a[j]).collect();
                // SubProductOpWrapper.int_value_at converts indices to elements internally
                ans[j] = self.op_list[j].int_value_at(&arg_indices)?;
            }
        } else {
            // Factor algebras have i32 elements - can use int_value_at directly
            let mut arg_buf = vec![0; self.arity as usize];
            for j in 0..self.number_of_factors {
                // Extract j-th component from each argument
                for (index, &arg_array) in args.iter().enumerate() {
                    arg_buf[index] = arg_array[j];
                }
                // Apply the j-th operation
                ans[j] = self.op_list[j].int_value_at(&arg_buf)?;
            }
        }
        
        Ok(ans)
    }
    
    fn clone_box(&self) -> Box<dyn Operation> {
        // Cannot clone BigProductOperation easily because it contains Box<dyn SmallAlgebra>
        // Instead, return an error or create a new one
        // For now, we'll need to handle cloning differently
        todo!("BigProductOperation::clone_box not yet implemented - operations should be Arc-backed")
    }
    
    fn value_at(&self, _args: &[i32]) -> Result<i32, String> {
        Err("BigProductOperation does not support value_at".to_string())
    }
    
    fn int_value_at_horner(&self, _arg: i32) -> Result<i32, String> {
        Err("BigProductOperation does not support int_value_at_horner".to_string())
    }
    
    fn make_table(&mut self) -> Result<(), String> {
        Err("BigProductOperation does not support make_table".to_string())
    }
    
    fn get_table(&self) -> Option<&[i32]> {
        None
    }
    
    fn get_table_force(&mut self, _make_table: bool) -> Result<&[i32], String> {
        Err("BigProductOperation does not support get_table_force".to_string())
    }
    
    fn is_table_based(&self) -> bool {
        false
    }
    
    fn is_idempotent(&self) -> Result<bool, String> {
        Err("BigProductOperation does not support is_idempotent".to_string())
    }
    
    fn is_associative(&self) -> Result<bool, String> {
        Err("BigProductOperation does not support is_associative".to_string())
    }
    
    fn is_commutative(&self) -> Result<bool, String> {
        Err("BigProductOperation does not support is_commutative".to_string())
    }
    
    fn is_totally_symmetric(&self) -> Result<bool, String> {
        Err("BigProductOperation does not support is_totally_symmetric".to_string())
    }
    
    fn is_maltsev(&self) -> Result<bool, String> {
        Err("BigProductOperation does not support is_maltsev".to_string())
    }
    
    fn is_total(&self) -> Result<bool, String> {
        Err("BigProductOperation does not support is_total".to_string())
    }
}

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
    
    /// Operations on this algebra (Arc-backed, boxed view provided on demand)
    operations: Vec<Arc<dyn Operation>>,
    
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

    /// Borrowed access to Arc-backed operations to avoid cloning.
    pub fn operations_ref_arc(&self) -> &[Arc<dyn Operation>] {
        &self.operations
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
    /// For power algebras, uses operations from the root algebra with Arc references.
    fn make_operations(&mut self) {
        self.operations = Vec::new();
        
        // Get operations from first algebra as a template
        if self.algebras.is_empty() {
            return;
        }
        
        // For power algebras, get operations from root algebra using Arc references
        // For regular products, get from first factor
        if let Some(ref root_algs) = self.root_algebras {
            // Power algebra - use root algebra operations with Arc refs
            if let Some(root_alg) = root_algs.first() {
                // Get operations from root algebra
                // Note: Ideally we'd use operations_ref_arc() to avoid cloning,
                // but SmallAlgebra trait doesn't expose it. For FreeAlgebra/SubProductAlgebra
                // we could downcast, but for now we use operations() which creates boxes.
                let root_ops = root_alg.operations();
                let k = root_ops.len();
                
                // Verify root algebra has operations - this is critical
                if k == 0 {
                    eprintln!("ERROR: Root algebra has no operations for power algebra");
                    // Don't leave operations empty - this would cause issues
                    // Return early but operations will be empty, which will cause errors later
                    // This is better than silently continuing with no operations
                    return;
                }
                
                // For each operation in the root algebra
                for i in 0..k {
                    let root_op = &root_ops[i];
                    let arity = root_op.arity();
                    let symbol = root_op.symbol().clone();
                    
                    // Create a list of Arc references to the same operation (for power)
                    // Since all factors are the same, we use the same operation
                    let mut op_list = Vec::with_capacity(self.number_of_factors);
                    for _ in 0..self.number_of_factors {
                        // Clone the operation box and wrap in Arc
                        let op_box = root_ops[i].clone_box();
                        op_list.push(Arc::from(op_box));
                    }
                    
                    // Clone factor algebras for the operation
                    let factor_algebras: Vec<Box<dyn SmallAlgebra<UniverseItem = T>>> = 
                        self.algebras.iter().map(|a| a.clone_box()).collect();
                    
                    // Create the product operation
                    let prod_op = BigProductOperation::new(
                        symbol,
                        arity,
                        self.number_of_factors,
                        op_list,
                        factor_algebras,
                    );
                    
                    self.operations.push(Arc::new(prod_op));
                }
                
                // Verify we created operations
                if self.operations.is_empty() {
                    eprintln!("ERROR: Failed to create any operations for power algebra");
                }
                return; // Done with power algebra case
            }
        }
        
        // Regular product case - use original logic
        let first_ops = self.algebras[0].operations();
        let k = first_ops.len();
        
        // Verify first algebra has operations
        if k == 0 {
            eprintln!("ERROR: First factor algebra has no operations for product algebra");
            // Don't leave operations empty
            return;
        }
        
        // For each operation in the first algebra
        for i in 0..k {
            let arity = first_ops[i].arity();
            let symbol = first_ops[i].symbol().clone();
            let symbol_str = symbol.to_string();
            
            // Collect the i-th operation from each factor algebra
            let mut op_list = Vec::with_capacity(self.number_of_factors);
            let mut all_factors_have_op = true;
            for j in 0..self.number_of_factors {
                let ops = self.algebras[j].operations();
                if i < ops.len() {
                    // Wrap factor operation with Arc. Since Product/SmallAlgebra
                    // return ArcOp-backed boxes, clone_box is shallow.
                    op_list.push(Arc::from(ops[i].clone_box()));
                } else {
                    // Factor missing operation - skip this product operation
                    all_factors_have_op = false;
                    break;
                }
            }
            
            if !all_factors_have_op {
                // Skip this operation if any factor doesn't have it
                continue;
            }
            
            // Clone factor algebras for the operation
            let factor_algebras: Vec<Box<dyn SmallAlgebra<UniverseItem = T>>> = 
                self.algebras.iter().map(|a| a.clone_box()).collect();
            
            // Create the product operation
            let prod_op = BigProductOperation::new(
                symbol,
                arity,
                self.number_of_factors,
                op_list,
                factor_algebras,
            );
            
            self.operations.push(Arc::new(prod_op));
            
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
        
        // Build constants fresh each call (cache stored below)
        // Collect all 0-ary operation values as constants
        let mut constants_vec: Vec<IntArray> = Vec::new();
        let mut constants_set: HashSet<IntArray> = HashSet::new();
        let mut c2s: HashMap<IntArray, OperationSymbol> = HashMap::new();
        
        for op in &self.operations {
            if op.arity() == 0 {
                // Evaluate the nullary operation on the product
                // value_at_arrays expects a slice of argument arrays; for arity 0 this is empty.
                match op.value_at_arrays(&[]) {
                    Ok(vals) => {
                        if let Ok(ia) = IntArray::from_array(vals) {
                            if constants_set.insert(ia.clone()) {
                                c2s.insert(ia.clone(), op.symbol().clone());
                                constants_vec.push(ia);
                            }
                        }
                    }
                    Err(_) => { /* ignore malformed ops */ }
                }
            }
        }
        
        self.constants = Some(constants_vec.clone());
        self.constant_to_symbol = Some(c2s);
        
        constants_vec
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
        // BigProductOperation is intentionally non-table-based (lazy)
        // Do not attempt to build tables here.
        
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
        let mut cloned = BigProductAlgebra {
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
            operations: Vec::new(), // Will be populated by make_operations()
            similarity_type: None,
            monitor: None,
        };
        // Regenerate operations after cloning (since we cloned the algebras)
        cloned.make_operations();
        cloned
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
        // Return boxed Arc-backed delegators without deep cloning
        let ops: Vec<Box<dyn Operation>> = self.operations
            .iter()
            .map(|op| boxed_arc_op(Arc::clone(op)))
            .collect();
        
        ops
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
        // Delegate to inherent implementation (avoid recursion into this trait method)
        BigProductAlgebra::<T>::make_operation_tables(self);
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
    use crate::alg::op::{OperationSymbol, Operation, BasicOperation};
    use crate::util::int_array::IntArrayTrait;
    
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

    #[test]
    fn test_constants_from_nullary_ops() {
        // Build two small algebras each with a single nullary constant op
        let set1: HashSet<i32> = HashSet::from([0, 1, 2]);
        let set2: HashSet<i32> = HashSet::from([0, 1]);

        let c_sym = OperationSymbol::new_safe("c", 0, false).unwrap();
        let c1_val = 2; // constant in alg1
        let c2_val = 1; // constant in alg2

        let c1 = crate::alg::op::operations::make_int_operation(c_sym.clone(), 3, vec![c1_val]).unwrap();
        let c2 = crate::alg::op::operations::make_int_operation(c_sym.clone(), 2, vec![c2_val]).unwrap();

        let alg1 = Box::new(BasicSmallAlgebra::new("A1".to_string(), set1, vec![c1])) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        let alg2 = Box::new(BasicSmallAlgebra::new("A2".to_string(), set2, vec![c2])) as Box<dyn SmallAlgebra<UniverseItem = i32>>;

        let mut prod = BigProductAlgebra::<i32>::new_safe(vec![alg1, alg2]).unwrap();

        let consts = prod.get_constants();
        assert_eq!(consts.len(), 1);
        let ia = &consts[0];
        assert_eq!(ia.as_slice(), &[c1_val, c2_val]);

        // Symbol mapping
        let sym = prod.get_constant_symbol(ia).expect("symbol for constant");
        assert_eq!(sym, c_sym);
    }

    #[test]
    fn test_make_operation_tables_no_recursion() {
        // Build a small product and call make_operation_tables; it should not recurse infinitely
        let set1: HashSet<i32> = HashSet::from([0, 1]);
        let set2: HashSet<i32> = HashSet::from([0, 1]);

        // Include a simple unary op so factor tables can be made
        let f_sym = OperationSymbol::new_safe("f", 1, false).unwrap();
        let f1 = Box::new(BasicOperation::new_safe(f_sym.clone(), 2).unwrap()) as Box<dyn Operation>;
        let f2 = Box::new(BasicOperation::new_safe(f_sym.clone(), 2).unwrap()) as Box<dyn Operation>;

        let alg1 = Box::new(BasicSmallAlgebra::new("A1".to_string(), set1, vec![f1])) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        let alg2 = Box::new(BasicSmallAlgebra::new("A2".to_string(), set2, vec![f2])) as Box<dyn SmallAlgebra<UniverseItem = i32>>;

        let mut prod = BigProductAlgebra::<i32>::new_safe(vec![alg1, alg2]).unwrap();

        // Should not panic or recurse; BigProductOperation itself remains non-table-based
        prod.make_operation_tables();
    }
}

