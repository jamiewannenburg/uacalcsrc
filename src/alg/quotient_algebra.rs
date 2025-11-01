use std::collections::{HashMap, HashSet};
use std::fmt::{self, Debug, Display};
use std::hash::Hash;
use std::sync::{Arc, RwLock};
use crate::alg::algebra::{Algebra, ProgressMonitor};
use crate::alg::general_algebra::GeneralAlgebra;
use crate::alg::small_algebra::{SmallAlgebra, AlgebraType};
use crate::alg::conlat::partition::Partition;
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};
use crate::alg::quotient_element::{QuotientElement, QuotientAlgebraRef};
use crate::util::horner::horner_same_size;

/// A quotient algebra of a SmallAlgebra by a congruence relation.
/// 
/// This struct represents the quotient algebra A/θ where A is the super algebra
/// and θ is a congruence relation on A. The elements of the quotient algebra
/// are equivalence classes represented by their canonical representatives.
/// 
/// # Type Parameters
/// * `T` - The universe item type of the super algebra
/// 
/// # Examples
/// ```
/// use uacalc::alg::{QuotientAlgebra, SmallAlgebra, BasicSmallAlgebra, Partition, Algebra};
/// use std::collections::HashSet;
/// 
/// // Create a super algebra with 4 elements
/// let super_algebra = Box::new(BasicSmallAlgebra::new(
///     "A".to_string(),
///     HashSet::from([0, 1, 2, 3]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Create a congruence with 2 blocks: {0,1}, {2,3}
/// let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
/// 
/// // Create quotient algebra
/// let quot = QuotientAlgebra::<i32>::new_safe(super_algebra, congruence).unwrap();
/// 
/// assert_eq!(quot.cardinality(), 2); // Two equivalence classes
/// ```
#[derive(Debug)]
pub struct QuotientAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    /// The base general algebra structure
    base: GeneralAlgebra<QuotientElement<T>>,
    
    /// The super algebra
    pub super_algebra: Box<dyn SmallAlgebra<UniverseItem = T>>,
    
    /// Representatives of congruence classes
    pub representatives: Vec<usize>,
    
    /// The congruence partition
    pub congruence: Partition,
    
    /// Shared reference for QuotientElements
    alg_ref: Arc<QuotientAlgebraRef<T>>,
    
    /// Cached universe as a vector (using RwLock for thread-safe interior mutability)
    universe_list: RwLock<Option<Vec<QuotientElement<T>>>>,
    
    /// Cached universe order map (using RwLock for thread-safe interior mutability)
    universe_order: RwLock<Option<HashMap<usize, usize>>>,
    
    /// The operations on the quotient algebra
    operations: Vec<QuotientOperation>,
    
    /// Lazy-initialized congruence lattice
    con: Option<Box<crate::alg::conlat::CongruenceLattice<QuotientElement<T>>>>,
    
    /// Lazy-initialized subalgebra lattice
    sub: Option<Box<crate::alg::sublat::SubalgebraLattice<QuotientElement<T>>>>,
}

/// An operation on a quotient algebra.
/// 
/// This wraps an operation from the super algebra and lifts it to the quotient.
#[derive(Debug)]
struct QuotientOperation {
    /// The original operation from the super algebra (Arc-backed, shallow clones)
    super_operation: Arc<dyn Operation>,
    /// The representatives array
    representatives: Vec<usize>,
    /// The congruence partition
    congruence: Partition,
    /// The size of the quotient algebra
    size: usize,
    /// Cached operation table (if computed)
    table: RwLock<Option<Vec<i32>>>,
}

impl Display for QuotientOperation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "QuotientOp({})", self.super_operation)
    }
}

impl QuotientOperation {
    fn new(
        super_operation: Arc<dyn Operation>,
        representatives: Vec<usize>,
        congruence: Partition,
        size: usize,
    ) -> Self {
        QuotientOperation {
            super_operation,
            representatives,
            congruence,
            size,
            table: RwLock::new(None),
        }
    }
}

impl Operation for QuotientOperation {
    fn symbol(&self) -> &OperationSymbol {
        self.super_operation.symbol()
    }
    
    fn arity(&self) -> i32 {
        self.super_operation.arity()
    }
    
    fn get_set_size(&self) -> i32 {
        self.size as i32
    }
    
    fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.int_value_at(args)
    }
    
    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
        Err("value_at_arrays not implemented for QuotientOperation".to_string())
    }
    
    fn int_value_at_horner(&self, arg: i32) -> Result<i32, String> {
        // Use cached table if available
        if let Some(table) = self.table.read().unwrap().as_ref() {
            if (arg as usize) < table.len() {
                return Ok(table[arg as usize]);
            }
        }
        Err("Table not available for Horner indexing".to_string())
    }
    
    fn get_table(&self) -> Option<&[i32]> {
        // Can't return a reference to RwLock-protected data easily
        None
    }
    
    fn get_table_force(&mut self, make_table: bool) -> Result<&[i32], String> {
        if make_table && self.table.read().unwrap().is_none() {
            self.make_table()?;
        }
        Err("get_table_force not supported for RwLock-protected tables".to_string())
    }
    
    fn is_table_based(&self) -> bool {
        self.table.read().unwrap().is_some()
    }
    
    fn is_associative(&self) -> Result<bool, String> {
        // This would require checking the operation property
        Ok(false) // Conservative answer
    }
    
    fn is_commutative(&self) -> Result<bool, String> {
        // This would require checking the operation property
        Ok(false) // Conservative answer
    }
    
    fn is_totally_symmetric(&self) -> Result<bool, String> {
        // This would require checking the operation property
        Ok(false) // Conservative answer
    }
    
    fn is_maltsev(&self) -> Result<bool, String> {
        // This would require checking if arity is 3 and p(x,y,y) = x and p(x,x,y) = y
        if self.arity() != 3 {
            return Ok(false);
        }
        Ok(false) // Conservative answer for now
    }
    
    fn clone_box(&self) -> Box<dyn Operation> {
        Box::new(self.clone())
    }
    
    fn int_value_at(&self, args: &[i32]) -> Result<i32, String> {
        // Check if we have a cached table
        if let Some(table) = self.table.read().unwrap().as_ref() {
            // Use cached table
            let index = horner_same_size(args, self.size as i32) as usize;
            if index < table.len() {
                return Ok(table[index]);
            }
        }
        
        // Compute value without table
        // Map quotient indices to super algebra indices
        let mut super_args = Vec::with_capacity(args.len());
        for &arg in args {
            if (arg as usize) < self.representatives.len() {
                super_args.push(self.representatives[arg as usize] as i32);
            } else {
                return Err(format!("Argument {} out of range", arg));
            }
        }
        
        // Apply operation in super algebra
        let result = self.super_operation.int_value_at(&super_args)?;
        
        // Find representative of the result
        let rep = self.congruence.representative(result as usize);
        
        // Find index of representative in representatives array
        match self.representatives.binary_search(&rep) {
            Ok(index) => Ok(index as i32),
            Err(_) => Err(format!("Representative {} not found in representatives array", rep)),
        }
    }
    
    fn make_table(&mut self) -> Result<(), String> {
        let arity = self.arity() as usize;
        let mut table_size = 1;
        for _ in 0..arity {
            table_size *= self.size;
        }
        
        let mut table = vec![0; table_size];
        
        for i in 0..table_size {
            let args = crate::util::horner::horner_inv_same_size(i as i32, self.size as i32, arity);
            table[i] = self.int_value_at(&args)?;
        }
        
        *self.table.write().unwrap() = Some(table);
        Ok(())
    }
    
    fn is_idempotent(&self) -> Result<bool, String> {
        // An operation is idempotent if f(x,x,...,x) = x for all x
        for i in 0..self.size {
            let args = vec![i as i32; self.arity() as usize];
            let result = self.int_value_at(&args)?;
            if result != i as i32 {
                return Ok(false);
            }
        }
        Ok(true)
    }
    
    fn is_total(&self) -> Result<bool, String> {
        // For finite algebras, operations are always total
        Ok(true)
    }
}

impl Clone for QuotientOperation {
    fn clone(&self) -> Self {
        QuotientOperation {
            super_operation: Arc::clone(&self.super_operation),
            representatives: self.representatives.clone(),
            congruence: self.congruence.clone(),
            size: self.size,
            table: RwLock::new(self.table.read().unwrap().clone()),
        }
    }
}

impl<T> QuotientAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    /// Create a new QuotientAlgebra with default name.
    /// 
    /// # Arguments
    /// * `super_algebra` - The algebra to take a quotient of
    /// * `congruence` - The congruence relation
    /// 
    /// # Returns
    /// * `Ok(QuotientAlgebra)` - Successfully created quotient algebra
    /// * `Err(String)` - If the congruence is invalid or incompatible
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{QuotientAlgebra, SmallAlgebra, BasicSmallAlgebra, Partition, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let super_algebra = Box::new(BasicSmallAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1, 2, 3]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
    /// let quot = QuotientAlgebra::<i32>::new_safe(super_algebra, congruence).unwrap();
    /// 
    /// assert_eq!(quot.cardinality(), 2);
    /// ```
    pub fn new_safe(
        super_algebra: Box<dyn SmallAlgebra<UniverseItem = T>>,
        congruence: Partition,
    ) -> Result<Self, String> {
        Self::new_with_name_safe("".to_string(), super_algebra, congruence)
    }
    
    /// Create a new QuotientAlgebra with a custom name.
    /// 
    /// # Arguments
    /// * `name` - The name for the quotient algebra
    /// * `super_algebra` - The algebra to take a quotient of
    /// * `congruence` - The congruence relation
    /// 
    /// # Returns
    /// * `Ok(QuotientAlgebra)` - Successfully created quotient algebra
    /// * `Err(String)` - If the congruence is invalid or incompatible
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{QuotientAlgebra, SmallAlgebra, BasicSmallAlgebra, Partition, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let super_algebra = Box::new(BasicSmallAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1, 2, 3]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
    /// let quot = QuotientAlgebra::<i32>::new_with_name_safe(
    ///     "A/θ".to_string(),
    ///     super_algebra,
    ///     congruence
    /// ).unwrap();
    /// 
    /// assert_eq!(quot.name(), "A/θ");
    /// ```
    pub fn new_with_name_safe(
        name: String,
        super_algebra: Box<dyn SmallAlgebra<UniverseItem = T>>,
        congruence: Partition,
    ) -> Result<Self, String> {
        // Validate that congruence size matches super algebra size
        if congruence.universe_size() != super_algebra.cardinality() as usize {
            return Err(format!(
                "Congruence size ({}) does not match super algebra size ({})",
                congruence.universe_size(),
                super_algebra.cardinality()
            ));
        }
        
        let representatives = congruence.representatives();
        let size = representatives.len();
        
        // Create shared reference for QuotientElements
        let alg_ref = Arc::new(QuotientAlgebraRef::<T> {
            super_algebra: super_algebra.clone_box(),
            congruence: congruence.clone(),
            representatives: representatives.clone(),
        });
        
        // Create base algebra with empty universe (will be populated lazily)
        let mut base = GeneralAlgebra::new(name);
        base.set_universe(HashSet::new());
        
        // Create quotient operations
        let super_ops = super_algebra.operations();
        let mut operations = Vec::new();
        for super_op in super_ops {
            // Convert boxed operation to Arc-backed operation for shallow cloning
            let op_arc: Arc<dyn Operation> = Arc::from(super_op);
            operations.push(QuotientOperation::new(
                op_arc,
                representatives.clone(),
                congruence.clone(),
                size,
            ));
        }
        
        let quot = QuotientAlgebra {
            base,
            super_algebra,
            representatives,
            congruence,
            alg_ref,
            universe_list: RwLock::new(None),
            universe_order: RwLock::new(None),
            operations,
            con: None,
            sub: None,
        };
        
        Ok(quot)
    }
    
    /// Create a new QuotientAlgebra (panicking version for compatibility).
    /// 
    /// # Arguments
    /// * `super_algebra` - The algebra to take a quotient of
    /// * `congruence` - The congruence relation
    /// 
    /// # Panics
    /// Panics if the congruence is invalid or incompatible
    pub fn new(
        super_algebra: Box<dyn SmallAlgebra<UniverseItem = T>>,
        congruence: Partition,
    ) -> Self {
        Self::new_safe(super_algebra, congruence).unwrap()
    }
    
    /// Create a new QuotientAlgebra with a custom name (panicking version).
    /// 
    /// # Arguments
    /// * `name` - The name for the quotient algebra
    /// * `super_algebra` - The algebra to take a quotient of
    /// * `congruence` - The congruence relation
    /// 
    /// # Panics
    /// Panics if the congruence is invalid or incompatible
    pub fn new_with_name(
        name: String,
        super_algebra: Box<dyn SmallAlgebra<UniverseItem = T>>,
        congruence: Partition,
    ) -> Self {
        Self::new_with_name_safe(name, super_algebra, congruence).unwrap()
    }
    
    /// Make operation tables for all operations.
    /// 
    /// This computes and caches the operation tables for faster evaluation.
    pub fn make_operation_tables(&mut self) {
        for op in &mut self.operations {
            let _ = op.make_table(); // Ignore errors
        }
    }
    
    /// Get the super algebra.
    /// 
    /// # Returns
    /// A reference to the super algebra
    pub fn super_algebra(&self) -> &dyn SmallAlgebra<UniverseItem = T> {
        self.super_algebra.as_ref()
    }
    
    /// Get the congruence partition.
    /// 
    /// # Returns
    /// A reference to the congruence partition
    pub fn get_congruence(&self) -> &Partition {
        &self.congruence
    }
    
    /// Find the index of a representative in the representatives array.
    /// 
    /// # Arguments
    /// * `rep` - A member of the representatives array
    /// 
    /// # Returns
    /// * `Ok(index)` - The index of the representative
    /// * `Err(String)` - If the representative is not found
    pub fn representative_index(&self, rep: usize) -> Result<usize, String> {
        match self.representatives.binary_search(&rep) {
            Ok(index) => Ok(index),
            Err(_) => Err(format!("Representative {} not found in representatives array", rep)),
        }
    }
    
    /// Get the canonical homomorphism image of an element.
    /// 
    /// Maps an element index from the super algebra to the corresponding
    /// element index in the quotient algebra.
    /// 
    /// # Arguments
    /// * `e` - The index of an element in the super algebra
    /// 
    /// # Returns
    /// * `Ok(index)` - The index of the image in the quotient algebra
    /// * `Err(String)` - If the element index is invalid
    pub fn canonical_homomorphism(&self, e: usize) -> Result<usize, String> {
        let rep = self.congruence.representative(e);
        self.representative_index(rep)
    }
    
    /// Ensure the universe list is cached.
    fn ensure_universe_list(&self) {
        if self.universe_list.read().unwrap().is_none() {
            let mut universe_vec = Vec::new();
            let mut universe_order = HashMap::new();
            
            for i in 0..self.representatives.len() {
                let elem = QuotientElement::<T>::new(self.alg_ref.clone(), i);
                universe_order.insert(i, i);
                universe_vec.push(elem);
            }
            
            *self.universe_list.write().unwrap() = Some(universe_vec);
            *self.universe_order.write().unwrap() = Some(universe_order);
        }
    }
    
    /// Get the congruence lattice (lazy initialization).
    /// 
    /// # Returns
    /// A reference to the congruence lattice
    pub fn con(&mut self) -> &crate::alg::conlat::CongruenceLattice<QuotientElement<T>> {
        if self.con.is_none() {
            // Create congruence lattice using the type-erased wrapper
            use crate::alg::SmallAlgebraWrapper;
            use crate::alg::quotient_element::QuotientElement;
            
            let alg_box = Box::new(self.clone()) as Box<dyn SmallAlgebra<UniverseItem = QuotientElement<T>>>;
            let wrapper = Box::new(SmallAlgebraWrapper::<QuotientElement<T>>::new(alg_box));
            self.con = Some(Box::new(crate::alg::conlat::CongruenceLattice::new(wrapper)));
        }
        self.con.as_ref().unwrap()
    }
    
    /// Get the subalgebra lattice (lazy initialization).
    /// 
    /// # Returns
    /// A reference to the subalgebra lattice
    pub fn sub(&mut self) -> &crate::alg::sublat::SubalgebraLattice<QuotientElement<T>> {
        if self.sub.is_none() {
            // Create subalgebra lattice for quotient elements
            use crate::alg::SmallAlgebraWrapper;
            use crate::alg::quotient_element::QuotientElement;
            
            let alg_box = Box::new(self.clone()) as Box<dyn SmallAlgebra<UniverseItem = QuotientElement<T>>>;
            let wrapper = Box::new(SmallAlgebraWrapper::<QuotientElement<T>>::new(alg_box));
            self.sub = Some(Box::new(crate::alg::sublat::SubalgebraLattice::new_safe(wrapper).unwrap()));
        }
        self.sub.as_ref().unwrap()
    }
}

impl<T> Clone for QuotientAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn clone(&self) -> Self {
        QuotientAlgebra {
            base: self.base.clone(),
            super_algebra: self.super_algebra.clone_box(),
            representatives: self.representatives.clone(),
            congruence: self.congruence.clone(),
            alg_ref: self.alg_ref.clone(),
            universe_list: RwLock::new(self.universe_list.read().unwrap().clone()),
            universe_order: RwLock::new(self.universe_order.read().unwrap().clone()),
            operations: self.operations.clone(),
            con: None, // Don't clone cached lattices
            sub: None,
        }
    }
}

impl<T> Display for QuotientAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "QuotientAlgebra(name: {}, super: {}, blocks: {})",
            self.name(),
            self.super_algebra.name(),
            self.congruence.number_of_blocks()
        )
    }
}

impl<T> Algebra for QuotientAlgebra<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    type UniverseItem = QuotientElement<T>;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.ensure_universe_list();
        let universe = self.universe_list.read().unwrap().clone().unwrap();
        Box::new(universe.into_iter())
    }
    
    fn cardinality(&self) -> i32 {
        self.representatives.len() as i32
    }
    
    fn input_size(&self) -> i32 {
        self.base.input_size()
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
        // Convert QuotientOperations to trait objects
        self.operations.iter()
            .map(|op| Box::new(op.clone()) as Box<dyn Operation>)
            .collect()
    }
    
    fn get_operation(&self, sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        for op in &self.operations {
            if op.symbol() == sym {
                return Some(Box::new(op.clone()) as Box<dyn Operation>);
            }
        }
        None
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        let mut map = HashMap::new();
        for op in &self.operations {
            map.insert(op.symbol().clone(), Box::new(op.clone()) as Box<dyn Operation>);
        }
        map
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
        self.super_algebra.similarity_type()
    }
    
    fn update_similarity_type(&mut self) {
        // Quotient algebra has the same similarity type as super algebra
        // Nothing to update
    }
    
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        self.similarity_type() == other.similarity_type()
    }
    
    fn make_operation_tables(&mut self) {
        self.make_operation_tables();
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        self.operations.iter()
            .filter(|op| op.arity() == 0)
            .map(|op| Box::new(op.clone()) as Box<dyn Operation>)
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
}

impl<T> SmallAlgebra for QuotientAlgebra<T>
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
        AlgebraType::Quotient
    }
    
    fn get_element(&self, k: usize) -> Option<Self::UniverseItem> {
        if k < self.representatives.len() {
            Some(QuotientElement::<T>::new(self.alg_ref.clone(), k))
        } else {
            None
        }
    }
    
    fn element_index(&self, elem: &Self::UniverseItem) -> Option<usize> {
        // QuotientElements store their index directly
        Some(elem.index)
    }
    
    fn get_universe_list(&self) -> Option<Vec<Self::UniverseItem>> {
        self.ensure_universe_list();
        self.universe_list.read().unwrap().clone()
    }
    
    fn get_universe_order(&self) -> Option<HashMap<Self::UniverseItem, usize>> {
        // QuotientElement implements Hash, so we can build the map
        self.ensure_universe_list();
        let universe = self.universe_list.read().unwrap();
        if let Some(ref univ) = *universe {
            let mut map = HashMap::new();
            for (idx, elem) in univ.iter().enumerate() {
                map.insert(elem.clone(), idx);
            }
            Some(map)
        } else {
            None
        }
    }
    
    fn parent(&self) -> Option<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        // QuotientAlgebra's parent is a SmallAlgebra<UniverseItem = T>
        // but we need SmallAlgebra<UniverseItem = QuotientElement<T>>
        // This is a type mismatch, so we return None
        None
    }
    
    fn parents(&self) -> Option<Vec<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>> {
        // Same issue as parent() - type mismatch
        None
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::small_algebra::BasicSmallAlgebra;
    use std::collections::HashSet;
    
    #[test]
    fn test_quotient_algebra_creation() {
        // Create a super algebra with 4 elements
        let super_algebra = Box::new(BasicSmallAlgebra::new(
            "A".to_string(),
            HashSet::from([0, 1, 2, 3]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Create a congruence with 2 blocks: {0,1}, {2,3}
        let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
        
        // Create quotient algebra
        let quot = QuotientAlgebra::<i32>::new_safe(super_algebra, congruence).unwrap();
        
        assert_eq!(quot.cardinality(), 2);
        assert_eq!(quot.representatives.len(), 2);
    }
    
    #[test]
    fn test_quotient_algebra_get_element() {
        let super_algebra = Box::new(BasicSmallAlgebra::new(
            "A".to_string(),
            HashSet::from([0, 1, 2, 3]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
        let quot = QuotientAlgebra::<i32>::new_safe(super_algebra, congruence).unwrap();
        
        let elem0 = quot.get_element(0).unwrap();
        assert_eq!(elem0.get_index(), 0);
        
        let elem1 = quot.get_element(1).unwrap();
        assert_eq!(elem1.get_index(), 1);
        
        assert!(quot.get_element(2).is_none()); // Only 2 elements
    }
    
    #[test]
    fn test_canonical_homomorphism() {
        let super_algebra = Box::new(BasicSmallAlgebra::new(
            "A".to_string(),
            HashSet::from([0, 1, 2, 3]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Congruence: {0,1}, {2,3}
        let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
        let quot = QuotientAlgebra::<i32>::new_safe(super_algebra, congruence).unwrap();
        
        // Elements 0 and 1 should map to the same quotient element
        assert_eq!(quot.canonical_homomorphism(0).unwrap(), quot.canonical_homomorphism(1).unwrap());
        
        // Elements 2 and 3 should map to the same quotient element
        assert_eq!(quot.canonical_homomorphism(2).unwrap(), quot.canonical_homomorphism(3).unwrap());
        
        // But they should be different from each other
        assert_ne!(quot.canonical_homomorphism(0).unwrap(), quot.canonical_homomorphism(2).unwrap());
    }
}
