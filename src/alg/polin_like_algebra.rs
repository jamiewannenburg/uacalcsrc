use std::collections::{HashMap, HashSet};
use std::fmt::{self, Debug, Display};
use std::hash::Hash;
use std::sync::{Arc, RwLock};
use crate::alg::algebra::{Algebra, ProgressMonitor};
use crate::alg::general_algebra::GeneralAlgebra;
use crate::alg::small_algebra::{SmallAlgebra, AlgebraType};
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};

/// A simple complement operation for Polin-like algebras.
/// 
/// This implements the unary "^+" operation that maps:
/// - Elements in botAlg (0..botSize-1) → botSize + topConstIndex
/// - Elements in topAlg (botSize..botSize+topSize-1) → botConstIndex
#[derive(Debug, Clone)]
struct ComplementOperation {
    symbol: OperationSymbol,
    bot_size: usize,
    top_size: usize,
    top_const_index: usize,
    bot_const_index: usize,
}

impl Operation for ComplementOperation {
    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn arity(&self) -> i32 {
        1
    }
    
    fn get_set_size(&self) -> i32 {
        (self.bot_size + self.top_size) as i32
    }
    
    fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.int_value_at(args)
    }
    
    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
        if args.is_empty() {
            return Err("No argument arrays provided".to_string());
        }
        
        let length = args[0].len();
        let mut result = Vec::with_capacity(length);
        
        for i in 0..length {
            let mut single_args = Vec::with_capacity(args.len());
            for arg_array in args {
                if arg_array.len() != length {
                    return Err("All argument arrays must have the same length".to_string());
                }
                single_args.push(arg_array[i]);
            }
            result.push(self.int_value_at(&single_args)?);
        }
        
        Ok(result)
    }
    
    fn int_value_at_horner(&self, _arg: i32) -> Result<i32, String> {
        Err("Horner indexing not supported for ComplementOperation".to_string())
    }
    
    fn get_table(&self) -> Option<&[i32]> {
        None
    }
    
    fn get_table_force(&mut self, _make_table: bool) -> Result<&[i32], String> {
        Err("Table access not supported for ComplementOperation".to_string())
    }
    
    fn is_table_based(&self) -> bool {
        false
    }
    
    fn is_associative(&self) -> Result<bool, String> {
        Ok(false)
    }
    
    fn is_commutative(&self) -> Result<bool, String> {
        Ok(false)
    }
    
    fn is_totally_symmetric(&self) -> Result<bool, String> {
        Ok(false)
    }
    
    fn is_maltsev(&self) -> Result<bool, String> {
        Ok(false)
    }
    
    fn clone_box(&self) -> Box<dyn Operation> {
        Box::new(self.clone())
    }
    
    fn int_value_at(&self, args: &[i32]) -> Result<i32, String> {
        if args.is_empty() {
            return Err("Complement operation requires one argument".to_string());
        }
        let arg = args[0];
        if arg < self.bot_size as i32 {
            // In botAlg - return botSize + topConstIndex
            Ok((self.bot_size + self.top_const_index) as i32)
        } else {
            // In topAlg - return botConstIndex
            Ok(self.bot_const_index as i32)
        }
    }
    
    fn make_table(&mut self) -> Result<(), String> {
        Ok(())
    }
    
    fn is_idempotent(&self) -> Result<bool, String> {
        Ok(false)
    }
    
    fn is_total(&self) -> Result<bool, String> {
        Ok(true)
    }
}

impl Display for ComplementOperation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "ComplementOperation({})", self.symbol)
    }
}

/// A Polin-like algebra constructed from a homomorphism between two algebras.
/// 
/// Given a homomorphism f: A → B, this constructs a Polin-type algebra
/// on the disjoint union of A and B. The elements are ordered by the elements
/// of B first followed by those of A.
/// 
/// # Type Parameters
/// * `T` - The universe item type (typically i32 for small algebras)
/// 
/// # Examples
/// ```
/// use uacalc::alg::{PolinLikeAlgebra, SmallAlgebra, BasicAlgebra, Algebra};
/// use std::collections::HashSet;
/// 
/// // Create two algebras
/// let top_alg = Box::new(BasicAlgebra::new(
///     "top".to_string(),
///     HashSet::from([0, 1]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// let bot_alg = Box::new(BasicAlgebra::new(
///     "bot".to_string(),
///     HashSet::from([0, 1]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Create Polin-like algebra (with identity map)
/// let polin = PolinLikeAlgebra::new_safe(
///     "polin".to_string(),
///     top_alg,
///     bot_alg,
///     None,
///     0,
///     0
/// ).unwrap();
/// 
/// assert_eq!(polin.cardinality(), 4); // 2 + 2 = 4
/// ```
#[derive(Debug)]
pub struct PolinLikeAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    /// The base general algebra structure
    base: GeneralAlgebra<i32>,
    
    /// The top algebra (A in the homomorphism f: A → B)
    pub top_alg: Box<dyn SmallAlgebra<UniverseItem = T>>,
    
    /// The bottom algebra (B in the homomorphism f: A → B)
    pub bot_alg: Box<dyn SmallAlgebra<UniverseItem = T>>,
    
    /// The homomorphism map from topAlg to botAlg (None means identity)
    pub map: Option<Arc<dyn Operation>>,
    
    /// Index of the top constant
    pub top_const_index: usize,
    
    /// Index of the bottom constant
    pub bot_const_index: usize,
    
    /// Size of the bottom algebra
    bot_size: usize,
    
    /// Size of the top algebra
    top_size: usize,
    
    /// The polinized operations
    operations: Vec<PolinizedOperation>,
    
    /// Cached universe as a vector
    universe_list: RwLock<Option<Vec<i32>>>,
    
    /// Cached universe order map
    universe_order: RwLock<Option<HashMap<i32, usize>>>,
    
    /// Lazy-initialized congruence lattice
    con: Option<Box<crate::alg::conlat::CongruenceLattice<i32>>>,
    
    /// Lazy-initialized subalgebra lattice
    sub: Option<Box<crate::alg::sublat::SubalgebraLattice<i32>>>,
}

/// A polinized operation that handles mixed arguments from both algebras.
#[derive(Debug, Clone)]
struct PolinizedOperation {
    /// The operation symbol
    symbol: OperationSymbol,
    
    /// The operation from the bottom algebra (Arc-backed)
    bot_operation: Arc<dyn Operation>,
    
    /// The operation from the top algebra (Arc-backed)
    top_operation: Arc<dyn Operation>,
    
    /// The homomorphism map (Arc-backed, None means identity)
    map: Option<Arc<dyn Operation>>,
    
    /// Size of the bottom algebra
    bot_size: usize,
    
    /// Total size of the polinized algebra
    total_size: usize,
}

impl Operation for PolinizedOperation {
    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn arity(&self) -> i32 {
        self.bot_operation.arity()
    }
    
    fn get_set_size(&self) -> i32 {
        self.total_size as i32
    }
    
    fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.int_value_at(args)
    }
    
    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
        if args.is_empty() {
            return Err("No argument arrays provided".to_string());
        }
        
        let length = args[0].len();
        let mut result = Vec::with_capacity(length);
        
        for i in 0..length {
            let mut single_args = Vec::with_capacity(args.len());
            for arg_array in args {
                if arg_array.len() != length {
                    return Err("All argument arrays must have the same length".to_string());
                }
                single_args.push(arg_array[i]);
            }
            result.push(self.int_value_at(&single_args)?);
        }
        
        Ok(result)
    }
    
    fn int_value_at_horner(&self, _arg: i32) -> Result<i32, String> {
        Err("Horner indexing not supported for PolinizedOperation".to_string())
    }
    
    fn get_table(&self) -> Option<&[i32]> {
        None
    }
    
    fn get_table_force(&mut self, _make_table: bool) -> Result<&[i32], String> {
        Err("Table access not supported for PolinizedOperation".to_string())
    }
    
    fn is_table_based(&self) -> bool {
        false
    }
    
    fn is_associative(&self) -> Result<bool, String> {
        Ok(false) // Conservative answer
    }
    
    fn is_commutative(&self) -> Result<bool, String> {
        Ok(false) // Conservative answer
    }
    
    fn is_totally_symmetric(&self) -> Result<bool, String> {
        Ok(false) // Conservative answer
    }
    
    fn is_maltsev(&self) -> Result<bool, String> {
        Ok(false) // Conservative answer
    }
    
    fn clone_box(&self) -> Box<dyn Operation> {
        Box::new(self.clone())
    }
    
    fn int_value_at(&self, args: &[i32]) -> Result<i32, String> {
        if args.is_empty() {
            return Err("No arguments provided".to_string());
        }
        
        let arg_type = Self::arg_type(args, self.bot_size);
        
        match arg_type {
            0 => {
                // All arguments are in botAlg - use botAlg operation directly
                self.bot_operation.int_value_at(args)
            }
            1 => {
                // All arguments are in topAlg - use topAlg operation with offset
                let mut top_args = Vec::with_capacity(args.len());
                for &arg in args {
                    if arg < self.bot_size as i32 {
                        return Err(format!("Invalid argument {} for type 1", arg));
                    }
                    top_args.push(arg - self.bot_size as i32);
                }
                let result = self.top_operation.int_value_at(&top_args)?;
                Ok(result + self.bot_size as i32)
            }
            2 => {
                // Mixed arguments - map topAlg args to botAlg via map, then use botAlg operation
                let mut bot_args = Vec::with_capacity(args.len());
                for &arg in args {
                    if arg < self.bot_size as i32 {
                        bot_args.push(arg);
                    } else {
                        // Map from topAlg to botAlg
                        let top_arg = arg - self.bot_size as i32;
                        if let Some(ref map_op) = self.map {
                            let mapped = map_op.int_value_at(&[top_arg])?;
                            bot_args.push(mapped);
                        } else {
                            // Identity map
                            bot_args.push(top_arg);
                        }
                    }
                }
                self.bot_operation.int_value_at(&bot_args)
            }
            _ => Err("Invalid argument type".to_string()),
        }
    }
    
    fn make_table(&mut self) -> Result<(), String> {
        // Tables are not used for PolinizedOperation
        Ok(())
    }
    
    fn is_idempotent(&self) -> Result<bool, String> {
        // Check if f(x,x,...,x) = x for all x
        for i in 0..self.total_size {
            let args = vec![i as i32; self.arity() as usize];
            let result = self.int_value_at(&args)?;
            if result != i as i32 {
                return Ok(false);
            }
        }
        Ok(true)
    }
    
    fn is_total(&self) -> Result<bool, String> {
        Ok(true)
    }
}

impl Display for PolinizedOperation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "PolinizedOperation({})", self.symbol)
    }
}

impl PolinizedOperation {
    /// Determine the argument type: 0 = all bot, 1 = all top, 2 = mixed
    fn arg_type(args: &[i32], bot_size: usize) -> i32 {
        if args.is_empty() {
            return 0;
        }
        
        if args[0] < bot_size as i32 {
            // First arg is in botAlg - check if all are
            for i in 1..args.len() {
                if args[i] >= bot_size as i32 {
                    return 2; // Mixed
                }
            }
            return 0; // All bot
        } else {
            // First arg is in topAlg - check if all are
            for i in 1..args.len() {
                if args[i] < bot_size as i32 {
                    return 2; // Mixed
                }
            }
            return 1; // All top
        }
    }
}

impl<T> PolinLikeAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    /// Create a new PolinLikeAlgebra with error handling.
    /// 
    /// # Arguments
    /// * `name` - The name of the algebra
    /// * `top_alg` - The top algebra (A in f: A → B)
    /// * `bot_alg` - The bottom algebra (B in f: A → B)
    /// * `map` - Optional homomorphism map from topAlg to botAlg (None = identity)
    /// * `top_const_index` - Index of the top constant
    /// * `bot_const_index` - Index of the bottom constant
    /// 
    /// # Returns
    /// * `Ok(PolinLikeAlgebra)` - Successfully created algebra
    /// * `Err(String)` - If there's an error in construction
    pub fn new_safe(
        name: String,
        top_alg: Box<dyn SmallAlgebra<UniverseItem = T>>,
        bot_alg: Box<dyn SmallAlgebra<UniverseItem = T>>,
        map: Option<Box<dyn Operation>>,
        top_const_index: usize,
        bot_const_index: usize,
    ) -> Result<Self, String> {
        let bot_size = bot_alg.cardinality() as usize;
        let top_size = top_alg.cardinality() as usize;
        let total_size = bot_size + top_size;
        
        // Validate constant indices
        if top_const_index >= top_size {
            return Err(format!("top_const_index {} >= top_size {}", top_const_index, top_size));
        }
        if bot_const_index >= bot_size {
            return Err(format!("bot_const_index {} >= bot_size {}", bot_const_index, bot_size));
        }
        
        // Create universe as HashSet<i32> for GeneralAlgebra
        let mut universe = HashSet::new();
        for i in 0..total_size {
            universe.insert(i as i32);
        }
        
        // Create base GeneralAlgebra
        let mut base = GeneralAlgebra::new_with_universe(name.clone(), universe);
        
        // Convert map to Arc if provided
        let map_arc = map.map(|m| Arc::<dyn Operation>::from(m));
        
        // Setup operations
        let operations = Self::setup_operations(
            top_alg.as_ref(),
            bot_alg.as_ref(),
            map_arc.as_ref().map(|m| m.as_ref()),
            bot_size,
            top_size,
            top_const_index,
            bot_const_index,
        )?;
        
        // Convert operations to Box for base
        let ops_box: Vec<Box<dyn Operation>> = operations
            .iter()
            .map(|op| op.clone_box())
            .collect();
        
        base.set_operations(ops_box);
        
        Ok(PolinLikeAlgebra {
            base,
            top_alg,
            bot_alg,
            map: map_arc,
            top_const_index,
            bot_const_index,
            bot_size,
            top_size,
            operations,
            universe_list: RwLock::new(None),
            universe_order: RwLock::new(None),
            con: None,
            sub: None,
        })
    }
    
    /// Create a new PolinLikeAlgebra (panics on error).
    pub fn new(
        name: String,
        top_alg: Box<dyn SmallAlgebra<UniverseItem = T>>,
        bot_alg: Box<dyn SmallAlgebra<UniverseItem = T>>,
        map: Option<Box<dyn Operation>>,
        top_const_index: usize,
        bot_const_index: usize,
    ) -> Self {
        Self::new_safe(name, top_alg, bot_alg, map, top_const_index, bot_const_index)
            .expect("Failed to create PolinLikeAlgebra")
    }
    
    /// Setup operations for the polinized algebra.
    fn setup_operations(
        top_alg: &dyn SmallAlgebra<UniverseItem = T>,
        bot_alg: &dyn SmallAlgebra<UniverseItem = T>,
        map: Option<&dyn Operation>,
        bot_size: usize,
        top_size: usize,
        top_const_index: usize,
        bot_const_index: usize,
    ) -> Result<Vec<PolinizedOperation>, String> {
        let mut ops = Vec::new();
        
        // Get similarity type from top algebra
        let sim_type = top_alg.similarity_type();
        
        // Create polinized operations for each operation symbol
        for sym in sim_type.get_operation_symbols() {
            let bot_op = bot_alg.get_operation_ref(sym)
                .ok_or_else(|| format!("Operation {} not found in bot algebra", sym))?;
            let top_op = top_alg.get_operation_ref(sym)
                .ok_or_else(|| format!("Operation {} not found in top algebra", sym))?;
            
            // Convert to Arc
            let bot_op_arc = Arc::<dyn Operation>::from(bot_op.clone_box());
            let top_op_arc = Arc::<dyn Operation>::from(top_op.clone_box());
            let map_arc = map.map(|m| Arc::<dyn Operation>::from(m.clone_box()));
            
            ops.push(PolinizedOperation {
                symbol: sym.clone(),
                bot_operation: bot_op_arc,
                top_operation: top_op_arc,
                map: map_arc,
                bot_size,
                total_size: bot_size + top_size,
            });
        }
        
        // Add the unary "^+" operation (external complement)
        let complement_sym = OperationSymbol::new("^+", 1, false);
        let complement_op = Self::create_complement_operation(
            complement_sym,
            bot_size,
            top_size,
            top_const_index,
            bot_const_index,
        );
        ops.push(complement_op);
        
        Ok(ops)
    }
    
    /// Create the unary "^+" complement operation.
    fn create_complement_operation(
        symbol: OperationSymbol,
        bot_size: usize,
        top_size: usize,
        top_const_index: usize,
        bot_const_index: usize,
    ) -> PolinizedOperation {
        // Create a simple complement operation
        let complement_op = ComplementOperation {
            symbol: symbol.clone(),
            bot_size,
            top_size,
            top_const_index,
            bot_const_index,
        };
        
        // Wrap in Arc
        let op_arc = Arc::<dyn Operation>::from(Box::new(complement_op) as Box<dyn Operation>);
        
        PolinizedOperation {
            symbol,
            bot_operation: op_arc.clone(),
            top_operation: op_arc.clone(),
            map: None,
            bot_size,
            total_size: bot_size + top_size,
        }
    }
    
    /// Get the top algebra.
    pub fn top_algebra(&self) -> &dyn SmallAlgebra<UniverseItem = T> {
        self.top_alg.as_ref()
    }
    
    /// Get the bottom algebra.
    pub fn bottom_algebra(&self) -> &dyn SmallAlgebra<UniverseItem = T> {
        self.bot_alg.as_ref()
    }
    
    /// Get the homomorphism map.
    pub fn map(&self) -> Option<&Arc<dyn Operation>> {
        self.map.as_ref()
    }
}

impl<T> Clone for PolinLikeAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn clone(&self) -> Self {
        PolinLikeAlgebra {
            base: GeneralAlgebra::new(self.base.name.clone()),
            top_alg: self.top_alg.clone_box(),
            bot_alg: self.bot_alg.clone_box(),
            map: self.map.clone(),
            top_const_index: self.top_const_index,
            bot_const_index: self.bot_const_index,
            bot_size: self.bot_size,
            top_size: self.top_size,
            operations: self.operations.clone(),
            universe_list: RwLock::new(self.universe_list.read().unwrap().clone()),
            universe_order: RwLock::new(self.universe_order.read().unwrap().clone()),
            con: None, // Don't clone cached lattices
            sub: None,
        }
    }
}

impl<T> Display for PolinLikeAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "PolinLikeAlgebra(name={})", self.base.name)
    }
}

impl<T> Algebra for PolinLikeAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    type UniverseItem = i32;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.base.universe()
    }
    
    fn cardinality(&self) -> i32 {
        (self.bot_size + self.top_size) as i32
    }
    
    fn input_size(&self) -> i32 {
        self.cardinality()
    }
    
    fn is_unary(&self) -> bool {
        false
    }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.base.iterator()
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        // Return boxed operations from the operations vector
        self.operations.iter().map(|op| op.clone_box()).collect()
    }
    
    fn similarity_type(&self) -> &SimilarityType {
        self.base.similarity_type()
    }
    
    fn name(&self) -> &str {
        &self.base.name
    }
    
    fn set_name(&mut self, name: String) {
        self.base.set_name(name);
    }
    
    fn description(&self) -> Option<&str> {
        self.base.description()
    }
    
    fn set_description(&mut self, description: Option<String>) {
        self.base.set_description(description);
    }
    
    fn update_similarity_type(&mut self) {
        self.base.update_similarity_type();
    }
    
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        self.similarity_type() == other.similarity_type()
    }
    
    fn make_operation_tables(&mut self) {
        self.base.make_operation_tables();
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        self.operations.iter()
            .filter(|op| op.arity() == 0)
            .map(|op| op.clone_box())
            .collect()
    }
    
    fn is_idempotent(&self) -> bool {
        for op in &self.operations {
            if let Ok(is_idemp) = op.is_idempotent() {
                if !is_idemp {
                    return false;
                }
            } else {
                return false;
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
                return false;
            }
        }
        true
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
    
    fn get_operation(&self, sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        for op in &self.operations {
            if op.symbol() == sym {
                return Some(op.clone_box());
            }
        }
        None
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        let mut map = HashMap::new();
        for op in &self.operations {
            map.insert(op.symbol().clone(), op.clone_box());
        }
        map
    }
}

impl<T> SmallAlgebra for PolinLikeAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn get_operation_ref(&self, sym: &OperationSymbol) -> Option<&dyn Operation> {
        for op in &self.operations {
            if op.symbol() == sym {
                return Some(op as &dyn Operation);
            }
        }
        None
    }
    
    fn get_operations_ref(&self) -> Vec<&dyn Operation> {
        self.operations.iter().map(|op| op as &dyn Operation).collect()
    }
    
    fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        Box::new(self.clone())
    }
    
    fn algebra_type(&self) -> AlgebraType {
        AlgebraType::PolinLike
    }
    
    fn get_element(&self, k: usize) -> Option<Self::UniverseItem> {
        if k < self.bot_size + self.top_size {
            Some(k as i32)
        } else {
            None
        }
    }
    
    fn element_index(&self, elem: &Self::UniverseItem) -> Option<usize> {
        let idx = *elem as usize;
        if idx < self.bot_size + self.top_size {
            Some(idx)
        } else {
            None
        }
    }
    
    fn get_universe_list(&self) -> Option<Vec<Self::UniverseItem>> {
        self.ensure_universe_list();
        self.universe_list.read().unwrap().clone()
    }
    
    fn get_universe_order(&self) -> Option<HashMap<Self::UniverseItem, usize>> {
        self.ensure_universe_list();
        let universe = self.universe_list.read().unwrap();
        if let Some(ref univ) = *universe {
            let mut map = HashMap::new();
            for (idx, &elem) in univ.iter().enumerate() {
                map.insert(elem, idx);
            }
            Some(map)
        } else {
            None
        }
    }
    
    fn parent(&self) -> Option<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        None
    }
    
    fn parents(&self) -> Option<Vec<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>> {
        None
    }
    
    fn reset_con_and_sub(&mut self) {
        self.con = None;
        self.sub = None;
    }
    
    fn convert_to_default_value_ops(&mut self) {
        // Not applicable for PolinLikeAlgebra
    }
}

impl<T> PolinLikeAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    /// Ensure the universe list is computed.
    fn ensure_universe_list(&self) {
        let mut list = self.universe_list.write().unwrap();
        if list.is_none() {
            let mut univ = Vec::with_capacity(self.bot_size + self.top_size);
            // Bot elements first (0..botSize-1)
            for i in 0..self.bot_size {
                univ.push(i as i32);
            }
            // Top elements next (botSize..botSize+topSize-1)
            for i in 0..self.top_size {
                univ.push((self.bot_size + i) as i32);
            }
            *list = Some(univ);
        }
    }
    
    /// Get the congruence lattice (lazy initialization).
    pub fn con(&mut self) -> &mut crate::alg::conlat::CongruenceLattice<i32> {
        if self.con.is_none() {
            use crate::alg::SmallAlgebraWrapper;
            
            // Clone this algebra as a trait object
            let alg_box = Box::new(self.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
            let wrapper = Box::new(SmallAlgebraWrapper::<i32>::new(alg_box));
            self.con = Some(Box::new(crate::alg::conlat::CongruenceLattice::<i32>::new(wrapper)));
        }
        self.con.as_mut().unwrap()
    }
    
    /// Get the subalgebra lattice (lazy initialization).
    pub fn sub(&mut self) -> &mut crate::alg::sublat::SubalgebraLattice<i32> {
        if self.sub.is_none() {
            use crate::alg::SmallAlgebraWrapper;
            
            // Clone this algebra as a trait object
            let alg_box = Box::new(self.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
            let wrapper = Box::new(SmallAlgebraWrapper::<i32>::new(alg_box));
            
            match crate::alg::sublat::SubalgebraLattice::new_safe(wrapper) {
                Ok(sub_lat) => {
                    self.sub = Some(Box::new(sub_lat));
                }
                Err(e) => {
                    panic!("Failed to create SubalgebraLattice for PolinLikeAlgebra: {}", e);
                }
            }
        }
        self.sub.as_mut().unwrap()
    }
}

