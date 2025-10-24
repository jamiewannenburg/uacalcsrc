use std::collections::{HashMap, HashSet};
use std::fmt::{Debug, Display};
use crate::alg::algebra::{Algebra, ProgressMonitor};
use crate::alg::general_algebra::GeneralAlgebra;
use crate::alg::small_algebra::{SmallAlgebra, AlgebraType};
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};
use crate::alg::conlat::partition::Partition;
use crate::alg::SmallAlgebraWrapper;
use crate::util::horner;

/// A subalgebra of a SmallAlgebra with a restricted universe.
/// 
/// This struct represents a subalgebra by maintaining a reference to the
/// super algebra and a sorted array of universe indices that form the
/// subuniverse. All operations are restricted to this subuniverse.
/// 
/// # Examples
/// ```
/// use uacalc::alg::{BasicSmallAlgebra, SmallAlgebra, Subalgebra, Algebra};
/// use std::collections::HashSet;
/// 
/// // Create a super algebra with universe {0, 1, 2, 3}
/// let super_alg = Box::new(BasicSmallAlgebra::new(
///     "super".to_string(),
///     HashSet::from([0, 1, 2, 3]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Create a subalgebra with universe {0, 1}
/// let sub_alg = Subalgebra::new_safe(
///     "sub".to_string(),
///     super_alg,
///     vec![0, 1]
/// ).unwrap();
/// 
/// assert_eq!(sub_alg.cardinality(), 2);
/// ```
pub struct Subalgebra {
    /// The underlying general algebra
    base: GeneralAlgebra<i32>,
    
    /// Reference to the super algebra
    super_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    
    /// Sorted array of universe indices forming the subuniverse
    univ_array: Vec<i32>,
    
    /// Lazy-initialized congruence lattice
    con: Option<Box<crate::alg::conlat::CongruenceLattice>>,
    
    /// Lazy-initialized subalgebra lattice
    sub: Option<Box<crate::alg::sublat::SubalgebraLattice>>,
}

impl Subalgebra {
    /// Create a new subalgebra with the given super algebra and subuniverse.
    /// 
    /// # Arguments
    /// * `name` - Name of the subalgebra
    /// * `super_algebra` - The super algebra
    /// * `univ` - Array of indices in the super algebra forming the subuniverse
    /// 
    /// # Returns
    /// * `Ok(Subalgebra)` - Successfully created subalgebra
    /// * `Err(String)` - If the subuniverse is empty or invalid
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{BasicSmallAlgebra, SmallAlgebra, Subalgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let super_alg = Box::new(BasicSmallAlgebra::new(
    ///     "super".to_string(),
    ///     HashSet::from([0, 1, 2]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let sub_alg = Subalgebra::new_safe(
    ///     "sub".to_string(),
    ///     super_alg,
    ///     vec![0, 1]
    /// ).unwrap();
    /// 
    /// assert_eq!(sub_alg.cardinality(), 2);
    /// ```
    pub fn new_safe(
        name: String,
        super_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        univ: Vec<i32>
    ) -> Result<Self, String> {
        // Validate inputs
        if univ.is_empty() {
            return Err("Subuniverse cannot be empty".to_string());
        }
        
        // Sort and deduplicate universe indices
        let mut univ_array = univ;
        univ_array.sort();
        univ_array.dedup();
        
        // Validate indices are within super algebra bounds
        let super_size = super_algebra.cardinality();
        if super_size < 0 {
            return Err("Super algebra has unknown cardinality".to_string());
        }
        
        for &idx in &univ_array {
            if idx < 0 || idx >= super_size {
                return Err(format!("Invalid universe index: {}", idx));
            }
        }
        
        // Create the base general algebra
        let universe = Self::make_universe_internal(&super_algebra, &univ_array);
        let base = GeneralAlgebra::new_with_universe(name, universe);
        
        let mut subalgebra = Subalgebra {
            base,
            super_algebra,
            univ_array,
            con: None,
            sub: None,
        };
        
        // Create restricted operations
        subalgebra.make_operations()?;
        
        Ok(subalgebra)
    }
    
    /// Create a new subalgebra (panicking version for compatibility).
    /// 
    /// # Arguments
    /// * `name` - Name of the subalgebra
    /// * `super_algebra` - The super algebra
    /// * `univ` - Array of indices in the super algebra forming the subuniverse
    /// 
    /// # Panics
    /// Panics if the subuniverse is empty or invalid
    pub fn new(
        name: String,
        super_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        univ: Vec<i32>
    ) -> Self {
        Self::new_safe(name, super_algebra, univ).unwrap()
    }
    
    /// Find the index in this subalgebra of the element with index k in the super algebra.
    /// 
    /// Uses binary search since univ_array is sorted.
    /// 
    /// # Arguments
    /// * `k` - Index in the super algebra
    /// 
    /// # Returns
    /// * `Some(index)` if k is in the subalgebra
    /// * `None` if k is not in the subalgebra
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{BasicSmallAlgebra, SmallAlgebra, Subalgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let super_alg = Box::new(BasicSmallAlgebra::new(
    ///     "super".to_string(),
    ///     HashSet::from([0, 1, 2, 3]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let sub_alg = Subalgebra::new_safe(
    ///     "sub".to_string(),
    ///     super_alg,
    ///     vec![0, 2]
    /// ).unwrap();
    /// 
    /// assert_eq!(sub_alg.index(0), Some(0));
    /// assert_eq!(sub_alg.index(2), Some(1));
    /// assert_eq!(sub_alg.index(1), None);
    /// ```
    pub fn index(&self, k: i32) -> Option<usize> {
        match self.univ_array.binary_search(&k) {
            Ok(idx) => Some(idx),
            Err(_) => None,
        }
    }
    
    /// Restrict a partition (or congruence) on the parent algebra to this subalgebra.
    /// 
    /// # Arguments
    /// * `par` - Partition on the super algebra
    /// 
    /// # Returns
    /// * `Ok(Partition)` - Restricted partition on this subalgebra
    /// * `Err(String)` - If restriction fails
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{BasicSmallAlgebra, SmallAlgebra, Subalgebra, Algebra};
    /// use uacalc::alg::conlat::partition::Partition;
    /// use std::collections::HashSet;
    /// 
    /// let super_alg = Box::new(BasicSmallAlgebra::new(
    ///     "super".to_string(),
    ///     HashSet::from([0, 1, 2, 3]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let sub_alg = Subalgebra::new_safe(
    ///     "sub".to_string(),
    ///     super_alg,
    ///     vec![0, 1, 2]
    /// ).unwrap();
    /// 
    /// // Create a partition on the super algebra
    /// let par = Partition::new(vec![-2, 0, -2, 2]).unwrap();
    /// 
    /// // Restrict to subalgebra
    /// let restricted = sub_alg.restrict_partition(&par).unwrap();
    /// assert_eq!(restricted.universe_size(), 3);
    /// ```
    pub fn restrict_partition(&self, par: &Partition) -> Result<Partition, String> {
        let mut blocks: HashMap<usize, Vec<usize>> = HashMap::new();
        
        // Build blocks for subalgebra elements
        for (i, &univ_idx) in self.univ_array.iter().enumerate() {
            let r = par.representative(univ_idx as usize);
            blocks.entry(r).or_insert_with(Vec::new).push(i);
        }
        
        // Build the array representation
        let mut arr = vec![0i32; self.univ_array.len()];
        for block in blocks.values() {
            if !block.is_empty() {
                let root = block[0];
                arr[root] = -(block.len() as i32);
                for &elem in &block[1..] {
                    arr[elem] = root as i32;
                }
            }
        }
        
        Partition::new(arr)
    }
    
    /// Get the super algebra reference.
    /// 
    /// # Returns
    /// A reference to the super algebra
    pub fn super_algebra(&self) -> &dyn SmallAlgebra<UniverseItem = i32> {
        self.super_algebra.as_ref()
    }
    
    /// Get the subuniverse array.
    /// 
    /// # Returns
    /// A slice of the subuniverse indices
    pub fn get_subuniverse_array(&self) -> &[i32] {
        &self.univ_array
    }
    
    /// Get the congruence lattice (lazy initialization).
    /// 
    /// # Returns
    /// A reference to the congruence lattice
    pub fn con(&mut self) -> &crate::alg::conlat::CongruenceLattice {
        if self.con.is_none() {
            // Create a wrapper that implements SmallAlgebra for this Subalgebra
            let wrapper = Box::new(SmallAlgebraWrapper::new(self.super_algebra.clone_box()));
            self.con = Some(Box::new(crate::alg::conlat::CongruenceLattice::new(wrapper)));
        }
        self.con.as_ref().unwrap()
    }
    
    /// Get the subalgebra lattice (lazy initialization).
    /// 
    /// # Returns
    /// A reference to the subalgebra lattice
    pub fn sub(&mut self) -> &crate::alg::sublat::SubalgebraLattice {
        if self.sub.is_none() {
            // Create a wrapper that implements SmallAlgebra for this Subalgebra
            let wrapper = Box::new(SmallAlgebraWrapper::new(self.super_algebra.clone_box()));
            self.sub = Some(Box::new(crate::alg::sublat::SubalgebraLattice::new(wrapper)));
        }
        self.sub.as_ref().unwrap()
    }
    
    /// Make the operation tables for all operations.
    pub fn make_operation_tables(&mut self) {
        self.base.make_operation_tables();
    }
    
    /// Create restricted operations that delegate to the super algebra.
    fn make_operations(&mut self) -> Result<(), String> {
        let super_ops = self.super_algebra.operations();
        let mut ops = Vec::with_capacity(super_ops.len());
        
        for super_op in super_ops {
            let restricted_op = RestrictedOperation::new(
                super_op.symbol().clone(),
                self.univ_array.len(),
                super_op.arity(),
                self.univ_array.clone(),
                super_op,
                self.super_algebra.clone_box(),
            );
            ops.push(Box::new(restricted_op) as Box<dyn Operation>);
        }
        
        self.base.set_operations(ops);
        Ok(())
    }
    
    /// Create the universe set for this subalgebra.
    fn make_universe_internal(
        _super_algebra: &Box<dyn SmallAlgebra<UniverseItem = i32>>,
        univ_array: &[i32]
    ) -> HashSet<i32> {
        univ_array.iter().copied().collect()
    }
}

impl Debug for Subalgebra {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Subalgebra")
            .field("name", &self.base.name)
            .field("size", &self.univ_array.len())
            .field("super_algebra_name", &self.super_algebra.name())
            .finish()
    }
}

impl Clone for Subalgebra {
    fn clone(&self) -> Self {
        // Create a new instance with the same parameters
        Subalgebra {
            base: self.base.clone(),
            super_algebra: self.super_algebra.clone_box(),
            univ_array: self.univ_array.clone(),
            con: None,
            sub: None,
        }
    }
}

impl Algebra for Subalgebra {
    type UniverseItem = i32;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        Box::new(self.univ_array.clone().into_iter())
    }
    
    fn cardinality(&self) -> i32 {
        self.univ_array.len() as i32
    }
    
    fn input_size(&self) -> i32 {
        self.base.input_size()
    }
    
    fn is_unary(&self) -> bool {
        self.base.is_unary()
    }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.universe()
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

impl SmallAlgebra for Subalgebra {
    fn get_operation_ref(&self, sym: &OperationSymbol) -> Option<&dyn Operation> {
        self.base.get_operation_ref(sym)
    }
    
    fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        Box::new(self.clone())
    }
    
    fn algebra_type(&self) -> AlgebraType {
        AlgebraType::Subalgebra
    }
    
    fn get_element(&self, k: usize) -> Option<Self::UniverseItem> {
        if k < self.univ_array.len() {
            Some(self.univ_array[k])
        } else {
            None
        }
    }
    
    fn element_index(&self, elem: &Self::UniverseItem) -> Option<usize> {
        self.index(*elem)
    }
    
    fn get_universe_list(&self) -> Option<Vec<Self::UniverseItem>> {
        Some(self.univ_array.clone())
    }
    
    fn get_universe_order(&self) -> Option<HashMap<Self::UniverseItem, usize>> {
        let mut order = HashMap::new();
        for (i, &elem) in self.univ_array.iter().enumerate() {
            order.insert(elem, i);
        }
        Some(order)
    }
    
    fn parent(&self) -> Option<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        Some(self.super_algebra.as_ref())
    }
    
    fn parents(&self) -> Option<Vec<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>> {
        Some(vec![self.super_algebra.as_ref()])
    }
    
    fn reset_con_and_sub(&mut self) {
        // No cached lattices in partial implementation
    }
    
    fn convert_to_default_value_ops(&mut self) {
        panic!("Only for basic algebras");
    }
}

impl Display for Subalgebra {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Subalgebra({}, cardinality: {})", self.base.name, self.cardinality())
    }
}

/// A restricted operation that delegates to a super algebra operation.
/// 
/// This operation maps subalgebra indices to super algebra indices,
/// applies the super algebra operation, then maps the result back.
struct RestrictedOperation {
    symbol: OperationSymbol,
    size: usize,
    arity: i32,
    univ_array: Vec<i32>,
    super_op: Box<dyn Operation>,
    super_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    value_table: Option<Vec<i32>>,
}

impl RestrictedOperation {
    fn new(
        symbol: OperationSymbol,
        size: usize,
        arity: i32,
        univ_array: Vec<i32>,
        super_op: Box<dyn Operation>,
        super_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    ) -> Self {
        RestrictedOperation {
            symbol,
            size,
            arity,
            univ_array,
            super_op,
            super_algebra,
            value_table: None,
        }
    }
}

impl Operation for RestrictedOperation {
    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn arity(&self) -> i32 {
        self.arity
    }
    
    fn get_set_size(&self) -> i32 {
        self.size as i32
    }
    
    fn int_value_at(&self, args: &[i32]) -> Result<i32, String> {
        // If we have a table, use it
        if let Some(ref table) = self.value_table {
            let index = horner::horner_same_size(args, self.size as i32) as usize;
            if index < table.len() {
                return Ok(table[index]);
            }
        }
        
        // Map subalgebra indices to super algebra indices
        let mut super_args = Vec::with_capacity(args.len());
        for &arg in args {
            if arg < 0 || arg >= self.univ_array.len() as i32 {
                return Err(format!("Argument {} out of range", arg));
            }
            super_args.push(self.univ_array[arg as usize]);
        }
        
        // Apply super algebra operation
        let super_result = self.super_op.int_value_at(&super_args)?;
        
        // Map result back to subalgebra index
        match self.univ_array.binary_search(&super_result) {
            Ok(idx) => Ok(idx as i32),
            Err(_) => Err(format!("Result {} not in subalgebra", super_result)),
        }
    }
    
    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
        if args.is_empty() {
            return Ok(Vec::new());
        }
        let len = args[0].len();
        let mut result = Vec::with_capacity(len);
        for i in 0..len {
            let mut single_args = Vec::with_capacity(args.len());
            for arg_array in args {
                single_args.push(arg_array[i]);
            }
            result.push(self.int_value_at(&single_args)?);
        }
        Ok(result)
    }
    
    fn int_value_at_horner(&self, arg: i32) -> Result<i32, String> {
        let args = horner::horner_inv_same_size(arg, self.size as i32, self.arity as usize);
        self.int_value_at(&args)
    }
    
    fn make_table(&mut self) -> Result<(), String> {
        let mut h = 1;
        for _ in 0..self.arity {
            h *= self.size;
        }
        
        let mut table = Vec::with_capacity(h);
        for i in 0..h {
            let args = horner::horner_inv_same_size(i as i32, self.size as i32, self.arity as usize);
            table.push(self.int_value_at(&args)?);
        }
        
        self.value_table = Some(table);
        Ok(())
    }
    
    fn get_table(&self) -> Option<&[i32]> {
        self.value_table.as_deref()
    }
    
    fn get_table_force(&mut self, make_table: bool) -> Result<&[i32], String> {
        if make_table && self.value_table.is_none() {
            self.make_table()?;
        }
        self.value_table.as_deref()
            .ok_or_else(|| "Table not available".to_string())
    }
    
    fn is_table_based(&self) -> bool {
        self.value_table.is_some()
    }
    
    fn is_idempotent(&self) -> Result<bool, String> {
        self.super_op.is_idempotent()
    }
    
    fn is_commutative(&self) -> Result<bool, String> {
        self.super_op.is_commutative()
    }
    
    fn is_associative(&self) -> Result<bool, String> {
        self.super_op.is_associative()
    }
    
    fn is_totally_symmetric(&self) -> Result<bool, String> {
        self.super_op.is_totally_symmetric()
    }
    
    fn is_maltsev(&self) -> Result<bool, String> {
        self.super_op.is_maltsev()
    }
    
    fn is_total(&self) -> Result<bool, String> {
        self.super_op.is_total()
    }
    
    fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.int_value_at(args)
    }
    
    fn clone_box(&self) -> Box<dyn Operation> {
        Box::new(RestrictedOperation {
            symbol: self.symbol.clone(),
            size: self.size,
            arity: self.arity,
            univ_array: self.univ_array.clone(),
            super_op: self.super_op.clone_box(),
            super_algebra: self.super_algebra.clone_box(),
            value_table: None, // Don't clone the table
        })
    }
}

impl Debug for RestrictedOperation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("RestrictedOperation")
            .field("symbol", &self.symbol)
            .field("arity", &self.arity)
            .field("size", &self.size)
            .field("has_table", &self.value_table.is_some())
            .finish()
    }
}

impl Display for RestrictedOperation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}(arity: {})", self.symbol, self.arity)
    }
}

