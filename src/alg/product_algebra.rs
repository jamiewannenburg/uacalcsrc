use std::collections::{HashMap, HashSet};
use std::fmt::{Debug, Display};
use crate::alg::algebra::{Algebra, ProgressMonitor};
use crate::alg::general_algebra::GeneralAlgebra;
use crate::alg::small_algebra::{SmallAlgebra, AlgebraType};
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};
use crate::util::horner;

/// A product algebra representing the direct product of SmallAlgebras.
/// 
/// This struct represents the direct product of a list of SmallAlgebra instances.
/// Each element in the product is represented as a vector of indices into the
/// component algebras, encoded using Horner's method for efficient storage.
/// 
/// # Examples
/// ```
/// use uacalc::alg::{ProductAlgebra, SmallAlgebra, BasicSmallAlgebra, Algebra};
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
///     HashSet::from([0, 1]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Create product
/// let product = ProductAlgebra::new_safe(
///     "A1 x A2".to_string(),
///     vec![alg1, alg2]
/// ).unwrap();
/// 
/// assert_eq!(product.cardinality(), 4); // 2 * 2 = 4
/// ```
pub struct ProductAlgebra {
    /// The underlying general algebra
    base: GeneralAlgebra<i32>,
    
    /// The list of algebras in the product
    algebras: Vec<Box<dyn SmallAlgebra<UniverseItem = i32>>>,
    
    /// The sizes of each algebra
    sizes: Vec<i32>,
    
    /// The number of algebras in the product
    number_of_products: usize,
    
    /// The total cardinality of the product
    size: i32,
}

impl ProductAlgebra {
    /// Create a new ProductAlgebra from a list of algebras.
    /// 
    /// # Arguments
    /// * `name` - Name of the product algebra
    /// * `algs` - List of algebras to form the product
    /// 
    /// # Returns
    /// * `Ok(ProductAlgebra)` - Successfully created product algebra
    /// * `Err(String)` - If algebras are incompatible or empty
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{ProductAlgebra, SmallAlgebra, BasicSmallAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg1 = Box::new(BasicSmallAlgebra::new(
    ///     "A1".to_string(),
    ///     HashSet::from([0, 1, 2]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let alg2 = Box::new(BasicSmallAlgebra::new(
    ///     "A2".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let product = ProductAlgebra::new_safe(
    ///     "A1 x A2".to_string(),
    ///     vec![alg1, alg2]
    /// ).unwrap();
    /// 
    /// assert_eq!(product.cardinality(), 6); // 3 * 2 = 6
    /// assert_eq!(product.number_of_factors(), 2);
    /// ```
    pub fn new_safe(
        name: String,
        algs: Vec<Box<dyn SmallAlgebra<UniverseItem = i32>>>
    ) -> Result<Self, String> {
        if algs.is_empty() {
            return Err("Cannot create product of empty algebra list".to_string());
        }
        
        // Check that all algebras have the same number of operations
        let num_ops = algs[0].operations().len();
        for (i, alg) in algs.iter().enumerate() {
            if alg.operations().len() != num_ops {
                return Err(format!(
                    "Algebra {} has {} operations, expected {}",
                    i, alg.operations().len(), num_ops
                ));
            }
        }
        
        let number_of_products = algs.len();
        let mut sizes = Vec::with_capacity(number_of_products);
        
        for alg in &algs {
            let card = alg.cardinality();
            if card < 0 {
                return Err("Cannot create product with algebra of unknown cardinality".to_string());
            }
            sizes.push(card);
        }
        
        let size = Self::calc_card_safe(&sizes)?;
        
        // Create universe as set of all Horner-encoded tuples
        let universe = Self::make_cartesian_product_universe(size);
        
        let base = GeneralAlgebra::new_with_universe(name, universe);
        
        let mut product = ProductAlgebra {
            base,
            algebras: algs,
            sizes,
            number_of_products,
            size,
        };
        
        // Create the operations
        product.make_operations()?;
        
        Ok(product)
    }
    
    /// Create a new ProductAlgebra (panicking version for compatibility).
    /// 
    /// # Arguments
    /// * `name` - Name of the product algebra
    /// * `algs` - List of algebras to form the product
    /// 
    /// # Panics
    /// Panics if algebras are incompatible or empty
    pub fn new(
        name: String,
        algs: Vec<Box<dyn SmallAlgebra<UniverseItem = i32>>>
    ) -> Self {
        Self::new_safe(name, algs).unwrap()
    }
    
    /// Calculate the product cardinality.
    /// 
    /// Returns the product of all sizes if it fits in an i32; otherwise returns -1.
    /// Returns 0 if any factor has size 0.
    /// 
    /// # Arguments
    /// * `sizes` - The sizes of the algebras
    /// 
    /// # Returns
    /// * `Ok(i32)` - The product cardinality, or -1 if too large
    /// * `Err(String)` - If sizes array is empty
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::ProductAlgebra;
    /// 
    /// let sizes = vec![2, 3, 4];
    /// let card = ProductAlgebra::calc_card_safe(&sizes).unwrap();
    /// assert_eq!(card, 24);
    /// 
    /// let sizes_with_zero = vec![2, 0, 4];
    /// let card = ProductAlgebra::calc_card_safe(&sizes_with_zero).unwrap();
    /// assert_eq!(card, 0);
    /// ```
    pub fn calc_card_safe(sizes: &[i32]) -> Result<i32, String> {
        if sizes.is_empty() {
            return Err("Cannot calculate cardinality of empty product".to_string());
        }
        
        let max_i32 = i32::MAX as i64;
        let mut v: i64 = 1;
        let mut infinity_has_occurred = false;
        
        for &size in sizes {
            if size == 0 {
                return Ok(0); // Empty factor means empty product
            }
            
            v = v.saturating_mul(size as i64);
            if v > max_i32 || size < 0 {
                infinity_has_occurred = true;
                v = 0; // Reset to minimize computation
            }
        }
        
        if infinity_has_occurred {
            Ok(-1)
        } else {
            Ok(v as i32)
        }
    }
    
    /// Calculate the product cardinality (panicking version).
    /// 
    /// # Arguments
    /// * `sizes` - The sizes of the algebras
    /// 
    /// # Returns
    /// The product cardinality, or -1 if too large, or 0 if any factor is empty
    /// 
    /// # Panics
    /// Panics if sizes array is empty
    pub fn calc_card(sizes: &[i32]) -> i32 {
        Self::calc_card_safe(sizes).unwrap()
    }
    
    /// Get the list of factor algebras.
    /// 
    /// # Returns
    /// A reference to the vector of factor algebras
    pub fn factors(&self) -> &[Box<dyn SmallAlgebra<UniverseItem = i32>>] {
        &self.algebras
    }
    
    /// Get the list of parent algebras (same as factors for product algebra).
    /// 
    /// # Returns
    /// A reference to the vector of parent algebras
    pub fn parents(&self) -> &[Box<dyn SmallAlgebra<UniverseItem = i32>>] {
        &self.algebras
    }
    
    /// Get the k-th projection algebra.
    /// 
    /// # Arguments
    /// * `k` - The index of the projection (0-based)
    /// 
    /// # Returns
    /// * `Some(&dyn SmallAlgebra)` - The k-th algebra
    /// * `None` - If k is out of range
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{ProductAlgebra, SmallAlgebra, BasicSmallAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
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
    /// let product = ProductAlgebra::new_safe(
    ///     "A1 x A2".to_string(),
    ///     vec![alg1, alg2]
    /// ).unwrap();
    /// 
    /// let proj0 = product.projection(0).unwrap();
    /// assert_eq!(proj0.cardinality(), 2);
    /// 
    /// let proj1 = product.projection(1).unwrap();
    /// assert_eq!(proj1.cardinality(), 3);
    /// ```
    pub fn projection(&self, k: usize) -> Option<&dyn SmallAlgebra<UniverseItem = i32>> {
        self.algebras.get(k).map(|alg| alg.as_ref())
    }
    
    /// Get the number of factor algebras.
    /// 
    /// # Returns
    /// The number of algebras in the product
    pub fn number_of_factors(&self) -> usize {
        self.number_of_products
    }
    
    /// Get the sizes array.
    /// 
    /// # Returns
    /// A slice of the sizes of each factor algebra
    pub fn get_sizes(&self) -> &[i32] {
        &self.sizes
    }
    
    /// Create the product universe as a set of Horner-encoded indices.
    fn make_cartesian_product_universe(size: i32) -> HashSet<i32> {
        if size < 0 || size > 1_000_000 {
            // For very large or unknown sizes, create empty set
            // The actual universe iteration will be handled differently
            HashSet::new()
        } else {
            (0..size).collect()
        }
    }
    
    /// Create the operations for the product algebra.
    fn make_operations(&mut self) -> Result<(), String> {
        let k = self.algebras[0].operations().len();
        let mut ops = Vec::with_capacity(k);
        
        for i in 0..k {
            let arity = self.algebras[0].operations()[i].arity();
            let symbol = self.algebras[0].operations()[i].symbol().clone();
            
            // Clone the algebras to store in the operation
            let alg_clones: Vec<Box<dyn SmallAlgebra<UniverseItem = i32>>> = self.algebras
                .iter()
                .map(|a| a.clone_box())
                .collect();
            
            let product_op = ProductOperation::new(
                symbol,
                self.size,
                arity,
                i, // Store the operation index instead of the operations themselves
                alg_clones,
                self.sizes.clone(),
                self.number_of_products,
            );
            
            ops.push(Box::new(product_op) as Box<dyn Operation>);
        }
        
        self.base.set_operations(ops);
        Ok(())
    }
    
    /// Make operation tables for all operations.
    pub fn make_operation_tables(&mut self) {
        self.base.make_operation_tables();
    }
    
    /// Add operations to the product algebra.
    /// 
    /// # Arguments
    /// * `operations` - Vector of operations to add
    pub fn add_operations(&mut self, operations: Vec<Box<dyn Operation>>) {
        let mut current_operations = self.base.operations();
        current_operations.extend(operations);
        self.base.set_operations(current_operations);
    }
}

impl Debug for ProductAlgebra {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("ProductAlgebra")
            .field("name", &self.base.name)
            .field("size", &self.size)
            .field("number_of_products", &self.number_of_products)
            .finish()
    }
}

impl Clone for ProductAlgebra {
    fn clone(&self) -> Self {
        ProductAlgebra {
            base: self.base.clone(),
            algebras: self.algebras.iter().map(|a| a.clone_box()).collect(),
            sizes: self.sizes.clone(),
            number_of_products: self.number_of_products,
            size: self.size,
        }
    }
}

impl Algebra for ProductAlgebra {
    type UniverseItem = i32;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        if self.size < 0 || self.size > 1_000_000 {
            // Return empty iterator for very large products
            Box::new(std::iter::empty())
        } else {
            Box::new(0..self.size)
        }
    }
    
    fn cardinality(&self) -> i32 {
        self.size
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

impl SmallAlgebra for ProductAlgebra {
    fn get_operation_ref(&self, sym: &OperationSymbol) -> Option<&dyn Operation> {
        self.base.get_operation_ref(sym)
    }
    
    fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        Box::new(self.clone())
    }
    
    fn algebra_type(&self) -> AlgebraType {
        AlgebraType::Product
    }
    
    fn get_element(&self, k: usize) -> Option<Self::UniverseItem> {
        if self.size < 0 {
            None
        } else if k < self.size as usize {
            Some(k as i32)
        } else {
            None
        }
    }
    
    fn element_index(&self, elem: &Self::UniverseItem) -> Option<usize> {
        if *elem >= 0 && *elem < self.size {
            Some(*elem as usize)
        } else {
            None
        }
    }
    
    fn get_universe_list(&self) -> Option<Vec<Self::UniverseItem>> {
        if self.size < 0 || self.size > 1_000_000 {
            None
        } else {
            Some((0..self.size).collect())
        }
    }
    
    fn get_universe_order(&self) -> Option<HashMap<Self::UniverseItem, usize>> {
        None
    }
    
    fn parent(&self) -> Option<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        None
    }
    
    fn parents(&self) -> Option<Vec<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>> {
        Some(self.algebras.iter().map(|a| a.as_ref()).collect())
    }
    
    fn reset_con_and_sub(&mut self) {
        // No cached lattices in partial implementation
    }
    
    fn convert_to_default_value_ops(&mut self) {
        panic!("Only for basic algebras");
    }
}

impl Display for ProductAlgebra {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "ProductAlgebra({}, cardinality: {})", self.base.name, self.size)
    }
}

/// An operation in a product algebra.
/// 
/// This operation computes values by:
/// 1. Decoding the Horner-encoded arguments into component indices
/// 2. Applying the corresponding operation in each component algebra
/// 3. Encoding the results back using Horner's method
struct ProductOperation {
    symbol: OperationSymbol,
    size: i32,
    arity: i32,
    op_index: usize, // Index of the operation in each algebra's operation list
    algebras: Vec<Box<dyn SmallAlgebra<UniverseItem = i32>>>,
    sizes: Vec<i32>,
    number_of_products: usize,
    value_table: Option<Vec<i32>>,
}

impl ProductOperation {
    fn new(
        symbol: OperationSymbol,
        size: i32,
        arity: i32,
        op_index: usize,
        algebras: Vec<Box<dyn SmallAlgebra<UniverseItem = i32>>>,
        sizes: Vec<i32>,
        number_of_products: usize,
    ) -> Self {
        ProductOperation {
            symbol,
            size,
            arity,
            op_index,
            algebras,
            sizes,
            number_of_products,
            value_table: None,
        }
    }
}

impl Operation for ProductOperation {
    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn arity(&self) -> i32 {
        self.arity
    }
    
    fn get_set_size(&self) -> i32 {
        self.size
    }
    
    fn int_value_at(&self, args: &[i32]) -> Result<i32, String> {
        // If we have a table, use it
        if let Some(ref table) = self.value_table {
            let index = horner::horner_same_size(args, self.size) as usize;
            if index < table.len() {
                return Ok(table[index]);
            }
        }
        
        // Inline Horner calculation
        let mut ans: i32 = 0;
        let mut args_expanded = vec![vec![0i32; self.number_of_products]; args.len()];
        
        // Decode each argument using horner_inv
        for (i, &arg) in args.iter().enumerate() {
            args_expanded[i] = horner::horner_inv(arg, &self.sizes);
        }
        
        // Apply operations in each component algebra (reverse order for Horner)
        for i in (0..self.number_of_products).rev() {
            // Get the operation from the algebra
            let ops = self.algebras[i].operations();
            if self.op_index >= ops.len() {
                return Err(format!("Operation index {} out of range", self.op_index));
            }
            let op = &ops[self.op_index];
            
            // Extract arguments for this component
            let mut component_args = Vec::with_capacity(args.len());
            for j in 0..args.len() {
                component_args.push(args_expanded[j][i]);
            }
            
            // Apply the operation
            let result = op.int_value_at(&component_args)?;
            
            // Accumulate using Horner's method
            let s = self.sizes[i];
            ans = s.wrapping_mul(ans).wrapping_add(result);
        }
        
        Ok(ans)
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
        let args = horner::horner_inv_same_size(arg, self.size, self.arity as usize);
        self.int_value_at(&args)
    }
    
    fn make_table(&mut self) -> Result<(), String> {
        let mut h = 1usize;
        for _ in 0..self.arity {
            h = h.saturating_mul(self.size as usize);
        }
        
        if h > 10_000_000 {
            return Err("Operation table too large".to_string());
        }
        
        let mut table = Vec::with_capacity(h);
        for i in 0..h {
            let args = horner::horner_inv_same_size(i as i32, self.size, self.arity as usize);
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
        // A product is idempotent iff all components are idempotent
        for alg in &self.algebras {
            let ops = alg.operations();
            if self.op_index >= ops.len() {
                return Err(format!("Operation index {} out of range", self.op_index));
            }
            if !ops[self.op_index].is_idempotent()? {
                return Ok(false);
            }
        }
        Ok(true)
    }
    
    fn is_commutative(&self) -> Result<bool, String> {
        // A product is commutative iff all components are commutative
        for alg in &self.algebras {
            let ops = alg.operations();
            if self.op_index >= ops.len() {
                return Err(format!("Operation index {} out of range", self.op_index));
            }
            if !ops[self.op_index].is_commutative()? {
                return Ok(false);
            }
        }
        Ok(true)
    }
    
    fn is_associative(&self) -> Result<bool, String> {
        // A product is associative iff all components are associative
        for alg in &self.algebras {
            let ops = alg.operations();
            if self.op_index >= ops.len() {
                return Err(format!("Operation index {} out of range", self.op_index));
            }
            if !ops[self.op_index].is_associative()? {
                return Ok(false);
            }
        }
        Ok(true)
    }
    
    fn is_totally_symmetric(&self) -> Result<bool, String> {
        // A product is totally symmetric iff all components are totally symmetric
        for alg in &self.algebras {
            let ops = alg.operations();
            if self.op_index >= ops.len() {
                return Err(format!("Operation index {} out of range", self.op_index));
            }
            if !ops[self.op_index].is_totally_symmetric()? {
                return Ok(false);
            }
        }
        Ok(true)
    }
    
    fn is_maltsev(&self) -> Result<bool, String> {
        // A product is Maltsev iff all components are Maltsev
        for alg in &self.algebras {
            let ops = alg.operations();
            if self.op_index >= ops.len() {
                return Err(format!("Operation index {} out of range", self.op_index));
            }
            if !ops[self.op_index].is_maltsev()? {
                return Ok(false);
            }
        }
        Ok(true)
    }
    
    fn is_total(&self) -> Result<bool, String> {
        // A product is total iff all components are total
        for alg in &self.algebras {
            let ops = alg.operations();
            if self.op_index >= ops.len() {
                return Err(format!("Operation index {} out of range", self.op_index));
            }
            if !ops[self.op_index].is_total()? {
                return Ok(false);
            }
        }
        Ok(true)
    }
    
    fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.int_value_at(args)
    }
    
    fn clone_box(&self) -> Box<dyn Operation> {
        // ProductOperation doesn't implement Clone, so we need a different approach
        // For now, we'll create a new instance with the same data
        let cloned_algebras = self.algebras.iter()
            .map(|alg| alg.clone_box())
            .collect();
        Box::new(ProductOperation {
            symbol: self.symbol.clone(),
            size: self.size,
            arity: self.arity,
            op_index: self.op_index,
            algebras: cloned_algebras,
            sizes: self.sizes.clone(),
            number_of_products: self.number_of_products,
            value_table: None, // Don't clone the table
        })
    }
}

impl Debug for ProductOperation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("ProductOperation")
            .field("symbol", &self.symbol)
            .field("arity", &self.arity)
            .field("size", &self.size)
            .field("number_of_products", &self.number_of_products)
            .field("has_table", &self.value_table.is_some())
            .finish()
    }
}

impl Display for ProductOperation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}(arity: {}, product of {})", self.symbol, self.arity, self.number_of_products)
    }
}

