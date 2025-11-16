/*! BasicLattice implementation
 *
 * This module implements BasicLattice, which wraps a poset structure and
 * provides lattice operations for visualization and computation.
 */

use std::collections::{HashMap, HashSet};
use std::fmt::{self, Display, Debug};
use std::hash::Hash;
use std::sync::Arc;

use crate::alg::{SmallAlgebra, Algebra, AlgebraType, ProgressMonitor};
use crate::alg::general_algebra::GeneralAlgebra;
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};
use crate::lat::{Lattice, Order};
use crate::lat::ordered_set::{OrderedSet, POElem, Edge};
use crate::lat::graph_data::LatticeGraphData;

/// A basic lattice structure for visualization and computation.
///
/// This struct wraps a poset (OrderedSet) and provides lattice operations
/// (join, meet) along with methods for visualization via graph data structures.
pub struct BasicLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    /// Base algebra structure
    base: GeneralAlgebra<Arc<POElem<T>>>,
    
    /// The underlying poset
    poset: Arc<OrderedSet<T>>,
    
    /// Universe as a list (for indexed access)
    univ_list: Vec<Arc<POElem<T>>>,
    
    /// Universe as a set (cached)
    univ_hs: Option<HashSet<Arc<POElem<T>>>>,
    
    /// Join operation
    join_operation: Arc<dyn Operation>,
    
    /// Meet operation
    meet_operation: Arc<dyn Operation>,
    
    /// Cached join irreducibles
    join_irreducibles: Option<Vec<Arc<POElem<T>>>>,
    
    /// Cached meet irreducibles
    meet_irreducibles: Option<Vec<Arc<POElem<T>>>>,
    
    /// TCT type map for edge labeling (from edges to type strings "1".."5")
    tct_type_map: Option<HashMap<Edge, String>>,
}

impl<T> BasicLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    /// Create a BasicLattice from an OrderedSet.
    ///
    /// # Arguments
    /// * `name` - Name for the lattice
    /// * `poset` - The ordered set to wrap
    ///
    /// # Returns
    /// * `Ok(BasicLattice)` - Successfully created lattice
    /// * `Err(String)` - If creation fails
    pub fn new_from_poset(name: String, poset: OrderedSet<T>) -> Result<Self, String> {
        let poset_arc = Arc::new(poset);
        let univ_list = poset_arc.univ();
        
        // Create universe set
        let mut universe = HashSet::new();
        for elem in &univ_list {
            universe.insert(elem.clone());
        }
        
        // Create base algebra
        let mut base = GeneralAlgebra::new_with_universe(name.clone(), universe);
        
        // Create join and meet operations
        let join_op = Self::make_join_operation(&poset_arc, &univ_list)?;
        let meet_op = Self::make_meet_operation(&poset_arc, &univ_list)?;
        
        // Set operations - we need to convert Arc to Box
        // Since we can't directly convert Arc<dyn Operation> to Box<dyn Operation>,
        // we'll use ArcOp as a wrapper
        use crate::alg::op::operation::ArcOp;
        base.set_operations(vec![
            Box::new(ArcOp::new(join_op.clone())),
            Box::new(ArcOp::new(meet_op.clone())),
        ]);
        
        Ok(BasicLattice {
            base,
            poset: poset_arc,
            univ_list,
            univ_hs: None,
            join_operation: join_op,
            meet_operation: meet_op,
            join_irreducibles: None,
            meet_irreducibles: None,
            tct_type_map: None,
        })
    }

    /// Create a BasicLattice from a Lattice trait implementation.
    ///
    /// # Arguments
    /// * `name` - Name for the lattice
    /// * `lat` - The lattice to convert (must have same element type T)
    ///
    /// # Returns
    /// * `Ok(BasicLattice)` - Successfully created lattice
    /// * `Err(String)` - If creation fails
    pub fn new_from_lattice(name: String, lat: &dyn Lattice<T>) -> Result<Self, String> {
        // Get universe and join irreducibles
        let univ: Vec<T> = lat.universe().into_iter().collect();
        let jis = lat.join_irreducibles().unwrap_or_default();
        
        // Build upper covers for each element
        let mut ucs: Vec<Vec<T>> = Vec::new();
        for elem1 in &univ {
            let mut covs = Vec::new();
            for ji in &jis {
                let join = lat.join(elem1, ji);
                if join != *elem1 {
                    let mut bad = false;
                    let mut to_remove = Vec::new();
                    for (idx, elem2) in covs.iter().enumerate() {
                        if lat.leq(elem2, &join) {
                            bad = true;
                            break;
                        }
                        if lat.leq(&join, elem2) {
                            to_remove.push(idx);
                        }
                    }
                    // Remove elements that are greater than join
                    for &idx in to_remove.iter().rev() {
                        covs.remove(idx);
                    }
                    if !bad {
                        covs.push(join);
                    }
                }
            }
            ucs.push(covs);
        }
        
        let poset = OrderedSet::new(Some(name.clone()), univ, ucs)?;
        Self::new_from_poset(name, poset)
    }

}

// Specialized implementation for Partition type
impl BasicLattice<crate::alg::conlat::Partition> {
    /// Create a BasicLattice from a CongruenceLattice with optional TCT labeling.
    ///
    /// # Arguments
    /// * `name` - Name for the lattice
    /// * `con_lat` - The congruence lattice
    /// * `label` - Whether to include TCT labeling
    ///
    /// # Returns
    /// * `Ok(BasicLattice)` - Successfully created lattice
    /// * `Err(String)` - If creation fails
    pub fn new_from_congruence_lattice(
        name: String,
        con_lat: &crate::alg::conlat::CongruenceLattice<crate::alg::conlat::Partition>,
        label: bool,
    ) -> Result<Self, String> {
        // Create poset from congruence lattice
        let poset = Self::make_ordered_set_from_congruence_lattice(con_lat)?;
        
        // Create basic lattice
        let mut basic_lat = Self::new_from_poset(name, poset)?;
        
        // Add TCT labeling if requested
        if label {
            basic_lat.make_tct_type_map(con_lat)?;
        }
        
        Ok(basic_lat)
    }

    /// Make an OrderedSet from a CongruenceLattice.
    fn make_ordered_set_from_congruence_lattice(
        con_lat: &crate::alg::conlat::CongruenceLattice<crate::alg::conlat::Partition>,
    ) -> Result<OrderedSet<crate::alg::conlat::Partition>, String> {
        use crate::alg::conlat::Partition;
        let univ: Vec<Partition> = con_lat.universe().into_iter().collect();
        let jis = con_lat.join_irreducibles().unwrap_or_default();
        
        let mut ucs: Vec<Vec<Partition>> = Vec::new();
        for elem1 in &univ {
            let mut covs = Vec::new();
            for ji in &jis {
                let join = con_lat.join(elem1, ji);
                if join != *elem1 {
                    let mut bad = false;
                    let mut to_remove = Vec::new();
                    for (idx, elem2) in covs.iter().enumerate() {
                        if con_lat.leq(elem2, &join) {
                            bad = true;
                            break;
                        }
                        if con_lat.leq(&join, elem2) {
                            to_remove.push(idx);
                        }
                    }
                    for &idx in to_remove.iter().rev() {
                        covs.remove(idx);
                    }
                    if !bad {
                        covs.push(join);
                    }
                }
            }
            ucs.push(covs);
        }
        
        OrderedSet::new(None, univ, ucs)
    }

    /// Make TCT type map for congruence lattice edges.
    fn make_tct_type_map(
        &mut self,
        con_lat: &crate::alg::conlat::CongruenceLattice<crate::alg::conlat::Partition>,
    ) -> Result<(), String> {
        use crate::alg::conlat::Partition;
        let types = vec!["1", "2", "3", "4", "5"];
        let mut tct_map = HashMap::new();
        
        let univ: Vec<Partition> = con_lat.universe().into_iter().collect();
        for elt in &univ {
            if let Some(pelt) = self.poset.get_element(elt) {
                for upper_cover in self.poset.get_upper_covers(&pelt) {
                    let elt2 = upper_cover.get_underlying_object();
                    // Use type_interval method (beta, alpha) where beta covers alpha
                    let typ = con_lat.type_interval(elt2, elt);
                    if typ >= 1 && typ <= 5 {
                        let edge = Edge::new(elt.to_string(), elt2.to_string());
                        tct_map.insert(edge, types[typ as usize - 1].to_string());
                    }
                }
            }
        }
        
        self.tct_type_map = Some(tct_map);
        Ok(())
    }
}

impl<T> BasicLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    /// Make join operation for this lattice.
    fn make_join_operation(
        poset: &Arc<OrderedSet<T>>,
        univ_list: &[Arc<POElem<T>>],
    ) -> Result<Arc<dyn Operation>, String> {
        // Create a LatticeJoinOperation
        let op = LatticeJoinOperation::new(poset.clone(), univ_list.to_vec())?;
        Ok(Arc::new(op))
    }

    /// Make meet operation for this lattice.
    fn make_meet_operation(
        poset: &Arc<OrderedSet<T>>,
        univ_list: &[Arc<POElem<T>>],
    ) -> Result<Arc<dyn Operation>, String> {
        // Create a LatticeMeetOperation
        let op = LatticeMeetOperation::new(poset.clone(), univ_list.to_vec())?;
        Ok(Arc::new(op))
    }

    /// Get the poset.
    pub fn get_poset(&self) -> &Arc<OrderedSet<T>> {
        &self.poset
    }

    /// Get cardinality.
    pub fn cardinality(&self) -> usize {
        self.univ_list.len()
    }

    /// Get zero (bottom) element.
    pub fn zero(&self) -> Arc<POElem<T>> {
        self.univ_list[0].clone()
    }

    /// Get one (top) element.
    pub fn one(&self) -> Arc<POElem<T>> {
        self.univ_list[self.univ_list.len() - 1].clone()
    }

    /// Get universe as a set.
    pub fn universe(&self) -> HashSet<Arc<POElem<T>>> {
        if let Some(ref hs) = self.univ_hs {
            hs.clone()
        } else {
            let hs: HashSet<Arc<POElem<T>>> = self.univ_list.iter().cloned().collect();
            // Note: We can't mutate self here, so we'll compute on demand
            hs
        }
    }

    /// Get universe as a list.
    pub fn get_universe_list(&self) -> &[Arc<POElem<T>>] {
        &self.univ_list
    }

    /// Compute join of two elements.
    pub fn join(&self, a: &Arc<POElem<T>>, b: &Arc<POElem<T>>) -> Arc<POElem<T>> {
        // Find least upper bound
        let a_idx = self.poset.elem_order(a).unwrap_or(0);
        let b_idx = self.poset.elem_order(b).unwrap_or(0);
        let max_idx = a_idx.max(b_idx);
        
        // Search from max_idx upward
        for i in max_idx..self.univ_list.len() {
            let elem = &self.univ_list[i];
            if self.poset.leq(a, elem) && self.poset.leq(b, elem) {
                // Check if this is the least upper bound
                let mut is_lub = true;
                for j in max_idx..i {
                    let other = &self.univ_list[j];
                    if self.poset.leq(a, other) && self.poset.leq(b, other) && self.poset.leq(elem, other) {
                        is_lub = false;
                        break;
                    }
                }
                if is_lub {
                    return elem.clone();
                }
            }
        }
        
        // Should not happen in a lattice, but return top element as fallback
        self.one()
    }

    /// Compute meet of two elements.
    pub fn meet(&self, a: &Arc<POElem<T>>, b: &Arc<POElem<T>>) -> Arc<POElem<T>> {
        // Find greatest lower bound
        let a_idx = self.poset.elem_order(a).unwrap_or(0);
        let b_idx = self.poset.elem_order(b).unwrap_or(0);
        let min_idx = a_idx.min(b_idx);
        
        // Search from min_idx downward
        for i in (0..=min_idx).rev() {
            let elem = &self.univ_list[i];
            if self.poset.leq(elem, a) && self.poset.leq(elem, b) {
                // Check if this is the greatest lower bound
                let mut is_glb = true;
                for j in (i + 1)..=min_idx {
                    let other = &self.univ_list[j];
                    if self.poset.leq(other, a) && self.poset.leq(other, b) && self.poset.leq(other, elem) {
                        is_glb = false;
                        break;
                    }
                }
                if is_glb {
                    return elem.clone();
                }
            }
        }
        
        // Should not happen in a lattice, but return bottom element as fallback
        self.zero()
    }

    /// Check if a ≤ b.
    pub fn leq(&self, a: &Arc<POElem<T>>, b: &Arc<POElem<T>>) -> bool {
        self.poset.leq(a, b)
    }

    /// Get atoms (elements covering zero).
    pub fn atoms(&self) -> Vec<Arc<POElem<T>>> {
        self.poset.get_upper_covers(&self.zero())
    }

    /// Get coatoms (elements covered by one).
    pub fn coatoms(&self) -> Vec<Arc<POElem<T>>> {
        self.poset.get_lower_covers(&self.one())
    }

    /// Get join irreducibles.
    /// 
    /// Uses the same logic as Java: an element is join irreducible if it cannot
    /// be expressed as the join of two strictly smaller elements. The bottom
    /// element (zero) is excluded as it has no strictly smaller elements.
    pub fn join_irreducibles(&mut self) -> &[Arc<POElem<T>>] {
        if self.join_irreducibles.is_none() {
            let mut jis = Vec::new();
            let zero = self.zero();
            
            for elem in &self.univ_list {
                // Skip bottom element - it's not join irreducible
                if elem == &zero {
                    continue;
                }
                
                // Compute the join of all elements strictly smaller than elem
                let mut join_of_smaller = None;
                
                for other in &self.univ_list {
                    // Check if other is strictly smaller than elem
                    if self.leq(other, elem) && other != elem {
                        if let Some(current_join) = join_of_smaller {
                            join_of_smaller = Some(self.join(&current_join, other));
                        } else {
                            join_of_smaller = Some(other.clone());
                        }
                        
                        // Early exit: if we've already reached elem, it's not join irreducible
                        if let Some(ref join_val) = join_of_smaller {
                            if join_val == elem {
                                break;
                            }
                        }
                    }
                }
                
                // If join_of_smaller is None, elem has no strictly smaller elements (shouldn't happen for non-zero)
                // If join_of_smaller != elem, then elem is join irreducible
                match join_of_smaller {
                    None => {
                        // This shouldn't happen for non-zero elements, but if it does, skip it
                    }
                    Some(join_val) => {
                        if join_val != *elem {
                            jis.push(elem.clone());
                        }
                    }
                }
            }
            
            self.join_irreducibles = Some(jis);
        }
        self.join_irreducibles.as_ref().unwrap()
    }

    /// Get meet irreducibles.
    pub fn meet_irreducibles(&mut self) -> &[Arc<POElem<T>>] {
        if self.meet_irreducibles.is_none() {
            let mut mis = Vec::new();
            for elem in &self.univ_list {
                if elem.is_meet_irreducible(&self.poset) {
                    mis.push(elem.clone());
                }
            }
            self.meet_irreducibles = Some(mis);
        }
        self.meet_irreducibles.as_ref().unwrap()
    }

    /// Convert to graph data for visualization.
    pub fn to_graph_data(&self) -> LatticeGraphData {
        self.poset.to_graph_data(self.tct_type_map.as_ref())
    }

    /// Get element index.
    pub fn element_index(&self, obj: &Arc<POElem<T>>) -> Option<usize> {
        self.poset.elem_order(obj)
    }

    /// Get element by index.
    pub fn get_element(&self, k: usize) -> Option<Arc<POElem<T>>> {
        self.univ_list.get(k).cloned()
    }

    /// Get the name of this lattice.
    pub fn name(&self) -> &str {
        &self.base.name
    }
}

// Implement Algebra trait for BasicLattice
impl<T> Algebra for BasicLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    type UniverseItem = Arc<POElem<T>>;

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

    fn similarity_type(&self) -> &SimilarityType {
        self.base.similarity_type()
    }

    fn update_similarity_type(&mut self) {
        self.base.update_similarity_type()
    }

    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        self.base.is_similar_to(other)
    }

    fn make_operation_tables(&mut self) {
        self.base.make_operation_tables()
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
        self.base.set_monitor(monitor)
    }

    fn name(&self) -> &str {
        &self.base.name
    }

    fn set_name(&mut self, name: String) {
        self.base.set_name(name)
    }

    fn description(&self) -> Option<&str> {
        self.base.description()
    }

    fn set_description(&mut self, desc: Option<String>) {
        self.base.set_description(desc)
    }
}

// Implement Order trait for BasicLattice
impl<T> Order<Arc<POElem<T>>> for BasicLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn leq(&self, a: &Arc<POElem<T>>, b: &Arc<POElem<T>>) -> bool {
        self.poset.leq(a, b)
    }
}

// Implement Lattice trait for BasicLattice
impl<T> Lattice<Arc<POElem<T>>> for BasicLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn join_irreducibles(&self) -> Option<Vec<Arc<POElem<T>>>> {
        // This requires mutable access, so we return None for now
        // Callers should use the method directly
        None
    }

    fn meet_irreducibles(&self) -> Option<Vec<Arc<POElem<T>>>> {
        // This requires mutable access, so we return None for now
        // Callers should use the method directly
        None
    }

    fn atoms(&self) -> Option<Vec<Arc<POElem<T>>>> {
        Some(self.atoms())
    }

    fn coatoms(&self) -> Option<Vec<Arc<POElem<T>>>> {
        Some(self.coatoms())
    }

    fn join(&self, a: &Arc<POElem<T>>, b: &Arc<POElem<T>>) -> Arc<POElem<T>> {
        self.join(a, b)
    }

    fn join_list(&self, args: &[Arc<POElem<T>>]) -> Arc<POElem<T>> {
        if args.is_empty() {
            return self.zero();
        }
        args.iter().fold(args[0].clone(), |acc, x| self.join(&acc, x))
    }

    fn meet(&self, a: &Arc<POElem<T>>, b: &Arc<POElem<T>>) -> Arc<POElem<T>> {
        self.meet(a, b)
    }

    fn meet_list(&self, args: &[Arc<POElem<T>>]) -> Arc<POElem<T>> {
        if args.is_empty() {
            return self.one();
        }
        args.iter().fold(args[0].clone(), |acc, x| self.meet(&acc, x))
    }
}

// Implement SmallAlgebra trait for BasicLattice
impl<T> SmallAlgebra for BasicLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn get_operation_ref(&self, sym: &OperationSymbol) -> Option<&dyn Operation> {
        self.base.get_operation_ref(sym)
    }

    fn get_operations_ref(&self) -> Vec<&dyn Operation> {
        self.base.get_operations_ref()
    }

    fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        Box::new(self.clone())
    }

    fn algebra_type(&self) -> AlgebraType {
        AlgebraType::BasicLattice
    }

    fn get_element(&self, k: usize) -> Option<Self::UniverseItem> {
        BasicLattice::get_element(self, k)
    }

    fn element_index(&self, elem: &Self::UniverseItem) -> Option<usize> {
        BasicLattice::element_index(self, elem)
    }

    fn get_universe_list(&self) -> Option<Vec<Self::UniverseItem>> {
        Some(self.univ_list.clone())
    }

    fn get_universe_order(&self) -> Option<HashMap<Self::UniverseItem, usize>> {
        let mut map = HashMap::new();
        for (idx, elem) in self.univ_list.iter().enumerate() {
            map.insert(elem.clone(), idx);
        }
        Some(map)
    }

    fn parent(&self) -> Option<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>> {
        None
    }

    fn parents(&self) -> Option<Vec<&dyn SmallAlgebra<UniverseItem = Self::UniverseItem>>> {
        None
    }

    fn reset_con_and_sub(&mut self) {
        // Not applicable for BasicLattice
    }

    fn convert_to_default_value_ops(&mut self) {
        // Not applicable for BasicLattice
    }
}

impl<T> Clone for BasicLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn clone(&self) -> Self {
        BasicLattice {
            base: self.base.clone(),
            poset: self.poset.clone(),
            univ_list: self.univ_list.clone(),
            univ_hs: self.univ_hs.clone(),
            join_operation: self.join_operation.clone(),
            meet_operation: self.meet_operation.clone(),
            join_irreducibles: self.join_irreducibles.clone(),
            meet_irreducibles: self.meet_irreducibles.clone(),
            tct_type_map: self.tct_type_map.clone(),
        }
    }
}

impl<T> Debug for BasicLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("BasicLattice")
            .field("name", &self.name())
            .field("cardinality", &self.cardinality())
            .finish()
    }
}

impl<T> Display for BasicLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "BasicLattice({})", self.name())
    }
}

/// Join operation for a lattice.
struct LatticeJoinOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    symbol: OperationSymbol,
    poset: Arc<OrderedSet<T>>,
    univ_list: Vec<Arc<POElem<T>>>,
    set_size: i32,
}

impl<T> LatticeJoinOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn new(poset: Arc<OrderedSet<T>>, univ_list: Vec<Arc<POElem<T>>>) -> Result<Self, String> {
        let symbol = OperationSymbol::join().clone();
        let set_size = univ_list.len() as i32;
        Ok(LatticeJoinOperation {
            symbol,
            poset,
            univ_list,
            set_size,
        })
    }
}

impl<T> Operation for LatticeJoinOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn arity(&self) -> i32 {
        2
    }

    fn get_set_size(&self) -> i32 {
        self.set_size
    }

    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }

    fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        if args.len() != 2 {
            return Err("Join operation requires exactly 2 arguments".to_string());
        }
        self.int_value_at(args)
    }

    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
        if args.len() != 2 {
            return Err("Join operation requires exactly 2 argument arrays".to_string());
        }
        let len = args[0].len();
        if args[1].len() != len {
            return Err("Argument arrays must have the same length".to_string());
        }
        let mut result = Vec::with_capacity(len);
        for i in 0..len {
            result.push(self.int_value_at(&[args[0][i], args[1][i]])?);
        }
        Ok(result)
    }

    fn int_value_at(&self, args: &[i32]) -> Result<i32, String> {
        if args.len() != 2 {
            return Err("Join operation requires exactly 2 arguments".to_string());
        }
        let i0 = args[0] as usize;
        let i1 = args[1] as usize;
        
        if i0 >= self.univ_list.len() || i1 >= self.univ_list.len() {
            return Err(format!("Index out of bounds: {} or {}", i0, i1));
        }
        
        let a = &self.univ_list[i0];
        let b = &self.univ_list[i1];
        
        // Find least upper bound
        let max_idx = i0.max(i1);
        
        for i in max_idx..self.univ_list.len() {
            let elem = &self.univ_list[i];
            if self.poset.leq(a, elem) && self.poset.leq(b, elem) {
                // Check if this is the least upper bound
                let mut is_lub = true;
                for j in max_idx..i {
                    let other = &self.univ_list[j];
                    if self.poset.leq(a, other) && self.poset.leq(b, other) && self.poset.leq(elem, other) {
                        is_lub = false;
                        break;
                    }
                }
                if is_lub {
                    return Ok(i as i32);
                }
            }
        }
        
        // Should not happen in a lattice, but return top element as fallback
        Ok((self.univ_list.len() - 1) as i32)
    }

    fn int_value_at_horner(&self, arg: i32) -> Result<i32, String> {
        // Decode horner encoding
        let base = self.set_size;
        let mut args = Vec::new();
        let mut val = arg;
        for _ in 0..2 {
            args.push(val % base);
            val /= base;
        }
        args.reverse();
        self.int_value_at(&args)
    }

    fn make_table(&mut self) -> Result<(), String> {
        // Tables are not used for lattice operations
        Ok(())
    }

    fn get_table(&self) -> Option<&[i32]> {
        None
    }

    fn get_table_force(&mut self, _make_table: bool) -> Result<&[i32], String> {
        Err("Lattice operations do not use tables".to_string())
    }

    fn is_table_based(&self) -> bool {
        false
    }

    fn is_idempotent(&self) -> Result<bool, String> {
        Ok(false) // Join is not idempotent in the sense f(x,x) = x
    }

    fn is_associative(&self) -> Result<bool, String> {
        Ok(true) // Join is associative
    }

    fn is_commutative(&self) -> Result<bool, String> {
        Ok(true) // Join is commutative
    }

    fn is_totally_symmetric(&self) -> Result<bool, String> {
        Ok(true) // Join is totally symmetric
    }

    fn is_maltsev(&self) -> Result<bool, String> {
        Ok(false) // Join is not a Maltsev operation
    }

    fn is_total(&self) -> Result<bool, String> {
        Ok(true) // Join is total
    }

    fn clone_box(&self) -> Box<dyn Operation> {
        Box::new(LatticeJoinOperation {
            symbol: self.symbol.clone(),
            poset: self.poset.clone(),
            univ_list: self.univ_list.clone(),
            set_size: self.set_size,
        })
    }
}

impl<T> Display for LatticeJoinOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Join({})", self.set_size)
    }
}

impl<T> Debug for LatticeJoinOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("LatticeJoinOperation")
            .field("set_size", &self.set_size)
            .finish()
    }
}

/// Meet operation for a lattice.
struct LatticeMeetOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    symbol: OperationSymbol,
    poset: Arc<OrderedSet<T>>,
    univ_list: Vec<Arc<POElem<T>>>,
    set_size: i32,
}

impl<T> LatticeMeetOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn new(poset: Arc<OrderedSet<T>>, univ_list: Vec<Arc<POElem<T>>>) -> Result<Self, String> {
        let symbol = OperationSymbol::meet().clone();
        let set_size = univ_list.len() as i32;
        Ok(LatticeMeetOperation {
            symbol,
            poset,
            univ_list,
            set_size,
        })
    }
}

impl<T> Operation for LatticeMeetOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn arity(&self) -> i32 {
        2
    }

    fn get_set_size(&self) -> i32 {
        self.set_size
    }

    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }

    fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        if args.len() != 2 {
            return Err("Meet operation requires exactly 2 arguments".to_string());
        }
        self.int_value_at(args)
    }

    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
        if args.len() != 2 {
            return Err("Meet operation requires exactly 2 argument arrays".to_string());
        }
        let len = args[0].len();
        if args[1].len() != len {
            return Err("Argument arrays must have the same length".to_string());
        }
        let mut result = Vec::with_capacity(len);
        for i in 0..len {
            result.push(self.int_value_at(&[args[0][i], args[1][i]])?);
        }
        Ok(result)
    }

    fn int_value_at(&self, args: &[i32]) -> Result<i32, String> {
        if args.len() != 2 {
            return Err("Meet operation requires exactly 2 arguments".to_string());
        }
        let i0 = args[0] as usize;
        let i1 = args[1] as usize;
        
        if i0 >= self.univ_list.len() || i1 >= self.univ_list.len() {
            return Err(format!("Index out of bounds: {} or {}", i0, i1));
        }
        
        let a = &self.univ_list[i0];
        let b = &self.univ_list[i1];
        
        // Find greatest lower bound
        let min_idx = i0.min(i1);
        
        for i in (0..=min_idx).rev() {
            let elem = &self.univ_list[i];
            if self.poset.leq(elem, a) && self.poset.leq(elem, b) {
                // Check if this is the greatest lower bound
                let mut is_glb = true;
                for j in (i + 1)..=min_idx {
                    let other = &self.univ_list[j];
                    if self.poset.leq(other, a) && self.poset.leq(other, b) && self.poset.leq(other, elem) {
                        is_glb = false;
                        break;
                    }
                }
                if is_glb {
                    return Ok(i as i32);
                }
            }
        }
        
        // Should not happen in a lattice, but return bottom element as fallback
        Ok(0)
    }

    fn int_value_at_horner(&self, arg: i32) -> Result<i32, String> {
        // Decode horner encoding
        let base = self.set_size;
        let mut args = Vec::new();
        let mut val = arg;
        for _ in 0..2 {
            args.push(val % base);
            val /= base;
        }
        args.reverse();
        self.int_value_at(&args)
    }

    fn make_table(&mut self) -> Result<(), String> {
        // Tables are not used for lattice operations
        Ok(())
    }

    fn get_table(&self) -> Option<&[i32]> {
        None
    }

    fn get_table_force(&mut self, _make_table: bool) -> Result<&[i32], String> {
        Err("Lattice operations do not use tables".to_string())
    }

    fn is_table_based(&self) -> bool {
        false
    }

    fn is_idempotent(&self) -> Result<bool, String> {
        Ok(false) // Meet is not idempotent in the sense f(x,x) = x
    }

    fn is_associative(&self) -> Result<bool, String> {
        Ok(true) // Meet is associative
    }

    fn is_commutative(&self) -> Result<bool, String> {
        Ok(true) // Meet is commutative
    }

    fn is_totally_symmetric(&self) -> Result<bool, String> {
        Ok(true) // Meet is totally symmetric
    }

    fn is_maltsev(&self) -> Result<bool, String> {
        Ok(false) // Meet is not a Maltsev operation
    }

    fn is_total(&self) -> Result<bool, String> {
        Ok(true) // Meet is total
    }

    fn clone_box(&self) -> Box<dyn Operation> {
        Box::new(LatticeMeetOperation {
            symbol: self.symbol.clone(),
            poset: self.poset.clone(),
            univ_list: self.univ_list.clone(),
            set_size: self.set_size,
        })
    }
}

impl<T> Display for LatticeMeetOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Meet({})", self.set_size)
    }
}

impl<T> Debug for LatticeMeetOperation<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("LatticeMeetOperation")
            .field("set_size", &self.set_size)
            .finish()
    }
}

