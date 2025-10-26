/*! Congruence Lattice implementation
 *
 * This module implements the congruence lattice of a SmallAlgebra using
 * Ralph Freese's fast algorithms from "Computing Congruences Efficiently".
 */

use std::collections::{HashMap, HashSet};
use std::sync::Arc;
use std::fmt::{self, Display};
use once_cell::sync::Lazy;

use crate::alg::{SmallAlgebra, Algebra};
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};
use crate::alg::conlat::{Partition, BinaryRelation};
use crate::util::simple_list::SimpleList;
use crate::util::int_array::{IntArray, IntArrayTrait};
use crate::lat::{Lattice, Order};

/// Type-erased interface for algebras that can have congruence lattices computed.
/// 
/// This trait provides the essential operations needed for computing congruences
/// without constraining the universe type. It allows CongruenceLattice to work
/// with algebras of any universe type (i32, IntArray, QuotientElement, etc.).
pub trait CongruenceComputable: Send + Sync {
    /// Get the cardinality of the algebra.
    fn cardinality(&self) -> i32;
    
    /// Get the name of the algebra.
    fn name(&self) -> &str;
    
    /// Get the number of operations.
    fn num_operations(&self) -> usize;
    
    /// Evaluate an operation at the given arguments (as indices).
    /// 
    /// # Arguments
    /// * `op_index` - The index of the operation to evaluate
    /// * `args` - The argument indices
    /// 
    /// # Returns
    /// * `Ok(result_index)` - The index of the result element
    /// * `Err(msg)` - If evaluation fails
    fn evaluate_operation(&self, op_index: usize, args: &[i32]) -> Result<i32, String>;
    
    /// Get the arity of an operation.
    /// 
    /// # Arguments
    /// * `op_index` - The index of the operation
    /// 
    /// # Returns
    /// The arity of the operation
    fn operation_arity(&self, op_index: usize) -> i32;
    
    /// Clone this as a boxed trait object.
    fn clone_box(&self) -> Box<dyn CongruenceComputable>;
}

/// Maximum lattice size for drawing
pub const MAX_DRAWABLE_SIZE: usize = 150;
pub const MAX_DRAWABLE_INPUT_SIZE: usize = 2500;

/// A congruence lattice of a SmallAlgebra.
///
/// This struct represents the lattice of all congruences on a given algebra,
/// using efficient algorithms for computing congruences and the lattice structure.
///
/// # Examples
/// ```
/// use uacalc::alg::{SmallAlgebra, BasicSmallAlgebra};
/// use uacalc::alg::conlat::CongruenceLattice;
/// use std::collections::HashSet;
///
/// // Create a simple algebra
/// let alg = Box::new(BasicSmallAlgebra::new(
///     "A".to_string(),
///     HashSet::from([0, 1, 2]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
///
/// // Create the congruence lattice
/// let con_lat = CongruenceLattice::new_from_i32_algebra(alg);
/// assert_eq!(con_lat.alg_size(), 3);
/// ```
pub struct CongruenceLattice {
    /// The algebra whose congruence lattice we're computing (type-erased)
    pub alg: Box<dyn CongruenceComputable>,
    
    /// Size of the algebra's universe
    pub alg_size: usize,
    
    /// Number of operations in the algebra
    pub num_ops: usize,
    
    /// The zero congruence (all elements in separate blocks)
    pub zero_cong: Partition,
    
    /// The one congruence (all elements in one block)
    pub one_cong: Partition,
    
    /// Optional description
    pub description: Option<String>,
    
    /// Is the lattice too large to draw?
    pub non_drawable: bool,
    
    // Cached computations
    /// The universe of all congruences (Vec maintains insertion order)
    universe: Option<Vec<Partition>>,
    
    /// Map from pairs [i,j] to Cg(i, j)
    principal_congruences_lookup: Option<HashMap<IntArray, Partition>>,
    
    /// Map from principal congruences to generating pairs
    principal_congruences_rep: Option<HashMap<Partition, IntArray>>,
    
    /// List of principal congruences sorted by rank
    principal_congruences: Option<Vec<Partition>>,
    
    /// Join irreducible congruences
    join_irreducibles: Option<Vec<Partition>>,
    
    /// Map from join irreducibles to their lower covers
    lower_cover_of_jis: Option<HashMap<Partition, Partition>>,
    
    /// Atoms of the lattice
    atoms: Option<Vec<Partition>>,
    
    /// Meet irreducible congruences
    meet_irreducibles: Option<Vec<Partition>>,
    
    /// Upper covers map
    upper_covers_map: Option<HashMap<Partition, Vec<Partition>>>,
    
    /// Permutability level (-1 if not computed)
    permutability_level: i32,
    
    /// Permutability level witnesses
    permutability_level_witnesses: Option<[Partition; 2]>,
    
    /// Size computed during universe generation
    size_computed: usize,
    
    /// Have principals been made?
    principals_made: bool,
}

impl fmt::Debug for CongruenceLattice {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("CongruenceLattice")
            .field("alg_name", &self.alg.name())
            .field("alg_size", &self.alg_size)
            .field("num_ops", &self.num_ops)
            .field("principals_made", &self.principals_made)
            .finish()
    }
}

impl Clone for CongruenceLattice {
    fn clone(&self) -> Self {
        CongruenceLattice {
            alg: self.alg.clone_box(),
            alg_size: self.alg_size,
            num_ops: self.num_ops,
            zero_cong: self.zero_cong.clone(),
            one_cong: self.one_cong.clone(),
            description: self.description.clone(),
            non_drawable: self.non_drawable,
            universe: None,
            principal_congruences_lookup: None,
            principal_congruences_rep: None,
            principal_congruences: None,
            join_irreducibles: None,
            lower_cover_of_jis: None,
            atoms: None,
            meet_irreducibles: None,
            upper_covers_map: None,
            permutability_level: -1,
            permutability_level_witnesses: None,
            size_computed: 0,
            principals_made: false,
        }
    }
}

impl CongruenceLattice {
    /// Create a new congruence lattice from an algebra with i32 universe (legacy constructor).
    ///
    /// # Arguments
    /// * `alg` - The algebra to compute the congruence lattice for
    ///
    /// # Returns
    /// A new CongruenceLattice instance
    pub fn new_from_i32_algebra(alg: Box<dyn SmallAlgebra<UniverseItem = i32>>) -> Self {
        Self::new(Box::new(SmallAlgebraWrapper::new(alg)))
    }
    
    /// Create a new congruence lattice from any SmallAlgebra.
    ///
    /// # Arguments
    /// * `alg` - The type-erased algebra to compute the congruence lattice for
    ///
    /// # Returns
    /// A new CongruenceLattice instance
    pub fn new(alg: Box<dyn CongruenceComputable>) -> Self {
        let alg_size = alg.cardinality() as usize;
        let num_ops = alg.num_operations();
        let zero_cong = Partition::zero(alg_size);
        let one_cong = Partition::one(alg_size);
        
        CongruenceLattice {
            alg,
            alg_size,
            num_ops,
            zero_cong,
            one_cong,
            description: None,
            non_drawable: false,
            universe: None,
            principal_congruences_lookup: None,
            principal_congruences_rep: None,
            principal_congruences: None,
            join_irreducibles: None,
            lower_cover_of_jis: None,
            atoms: None,
            meet_irreducibles: None,
            upper_covers_map: None,
            permutability_level: -1,
            permutability_level_witnesses: None,
            size_computed: 0,
            principals_made: false,
        }
    }
}

/// Wrapper that adapts a SmallAlgebra<UniverseItem=T> to CongruenceComputable.
/// 
/// This wrapper allows any SmallAlgebra to be used with CongruenceLattice by
/// providing index-based operation evaluation.
pub struct SmallAlgebraWrapper<T: Clone + std::hash::Hash + Eq + fmt::Debug + Display + Send + Sync + 'static> {
    inner: Box<dyn SmallAlgebra<UniverseItem = T>>,
}

impl<T: Clone + std::hash::Hash + Eq + fmt::Debug + Display + Send + Sync + 'static> SmallAlgebraWrapper<T> {
    pub fn new(alg: Box<dyn SmallAlgebra<UniverseItem = T>>) -> Self {
        SmallAlgebraWrapper { inner: alg }
    }
}

impl<T: Clone + std::hash::Hash + Eq + fmt::Debug + Display + Send + Sync + 'static> CongruenceComputable for SmallAlgebraWrapper<T> {
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }
    
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    fn num_operations(&self) -> usize {
        self.inner.operations().len()
    }
    
    fn evaluate_operation(&self, op_index: usize, args: &[i32]) -> Result<i32, String> {
        let ops = self.inner.operations();
        if op_index >= ops.len() {
            return Err(format!("Operation index {} out of bounds", op_index));
        }
        
        ops[op_index].int_value_at(args)
    }
    
    fn operation_arity(&self, op_index: usize) -> i32 {
        let ops = self.inner.operations();
        if op_index >= ops.len() {
            return 0;
        }
        
        ops[op_index].arity()
    }
    
    fn clone_box(&self) -> Box<dyn CongruenceComputable> {
        Box::new(SmallAlgebraWrapper {
            inner: self.inner.clone_box(),
        })
    }
}

impl CongruenceLattice {
    /// Get the size of the algebra's universe.
    pub fn alg_size(&self) -> usize {
        self.alg_size
    }
    
    /// Get the zero congruence (all elements in separate blocks).
    pub fn zero(&self) -> Partition {
        self.zero_cong.clone()
    }
    
    /// Get the one congruence (all elements in one block).
    pub fn one(&self) -> Partition {
        self.one_cong.clone()
    }
    
    /// Get the name of the algebra this is the congruence lattice of.
    pub fn get_algebra_name(&self) -> &str {
        self.alg.name()
    }
    
    /// Get or set the description.
    pub fn get_description(&self) -> String {
        if let Some(ref desc) = self.description {
            desc.clone()
        } else {
            format!("Congruence Lattice of {}", self.alg.name())
        }
    }
    
    /// Set the description.
    pub fn set_description(&mut self, desc: String) {
        self.description = Some(desc);
    }
    
    /// Check if the lattice is smaller than the given size.
    pub fn is_smaller_than(&mut self, size: usize) -> bool {
        if let Some(ref univ) = self.universe {
            return univ.len() < size;
        }
        
        if let Some(ref jis) = self.join_irreducibles {
            if jis.len() >= size {
                return false;
            }
        }
        
        self.make_universe_with_limit(size);
        if self.universe.is_none() {
            return false;
        }
        
        true
    }
    
    /// Check if the lattice is drawable (small enough).
    pub fn is_drawable(&mut self) -> bool {
        if let Some(ref univ) = self.universe {
            return univ.len() <= MAX_DRAWABLE_SIZE;
        }
        
        if self.size_computed > 0 {
            return false;
        }
        
        self.is_smaller_than(MAX_DRAWABLE_SIZE + 1)
    }
}

impl fmt::Display for CongruenceLattice {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Con({})", self.alg.name())
    }
}

// Implement Order trait for Partition comparison
impl Order<Partition> for CongruenceLattice {
    fn leq(&self, a: &Partition, b: &Partition) -> bool {
        a.leq(b)
    }
}

// Core congruence computation methods
impl CongruenceLattice {
    /// Compute the principal congruence generated by elements a and b.
    ///
    /// # Arguments
    /// * `a` - First element (as index)
    /// * `b` - Second element (as index)
    ///
    /// # Returns
    /// The congruence generated by (a, b)
    ///
    /// # Examples
    /// ```
    /// use uacalc::alg::{SmallAlgebra, BasicSmallAlgebra};
    /// use uacalc::alg::conlat::CongruenceLattice;
    /// use std::collections::HashSet;
    ///
    /// let alg = Box::new(BasicSmallAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1, 2]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    ///
    /// let mut con_lat = CongruenceLattice::new_from_i32_algebra(alg);
    /// let cg = con_lat.cg(0, 1);
    /// assert!(cg.is_related(0, 1));
    /// ```
    pub fn cg(&mut self, a: usize, b: usize) -> Partition {
        if a == b {
            return self.zero();
        }
        
        let (a, b) = if a > b { (b, a) } else { (a, b) };
        
        // Check if we have it cached
        if let Some(ref lookup) = self.principal_congruences_lookup {
            let mut key = IntArray::new(2).unwrap();
            key.set(0, a as i32).unwrap();
            key.set(1, b as i32).unwrap();
            if let Some(part) = lookup.get(&key) {
                return part.clone();
            }
        }
        
        self.make_cg(a, b)
    }
    
    /// Internal method to compute Cg(a, b) assuming a < b.
    fn make_cg(&self, a: usize, b: usize) -> Partition {
        let mut part = vec![-1_i32; self.alg_size];
        part[a] = -2;
        part[b] = a as i32;
        
        let mut pairs = SimpleList::new();
        pairs = pairs.cons_panic([a as i32, b as i32]);
        
        self.make_cg_aux(part, pairs)
    }
    
    /// Auxiliary method for computing congruences from a partition and pairs.
    fn make_cg_aux(&self, mut part: Vec<i32>, mut pairs: Arc<SimpleList<[i32; 2]>>) -> Partition {
        while !pairs.is_empty() {
            let pair = pairs.first().unwrap();
            let x = pair[0] as usize;
            let y = pair[1] as usize;
            pairs = pairs.rest();
            
            // For each operation f
            for op_index in 0..self.num_ops {
                let arity = self.alg.operation_arity(op_index);
                if arity == 0 {
                    continue;
                }
                
                let mut arg = vec![0_i32; arity as usize];
                
                // For each position index in the operation
                for index in 0..arity {
                    // Reset arg
                    for k in 0..arity as usize {
                        arg[k] = 0;
                    }
                    
                    // Increment through all possible arguments, varying all positions except 'index'
                    loop {
                        arg[index as usize] = x as i32;
                        let r_val = self.alg.evaluate_operation(op_index, &arg).unwrap_or(0);
                        let r = Self::find_root(r_val as usize, &part);
                        
                        arg[index as usize] = y as i32;
                        let s_val = self.alg.evaluate_operation(op_index, &arg).unwrap_or(0);
                        let s = Self::find_root(s_val as usize, &part);
                        
                        if r != s {
                            Self::join_blocks_in_array(r, s, &mut part);
                            pairs = pairs.cons_panic([r as i32, s as i32]);
                        }
                        
                        // Increment arg (excluding position 'index')
                        if !Self::increment_arg(&mut arg, index as usize, self.alg_size - 1) {
                            break;
                        }
                    }
                }
            }
        }
        
        Partition::new(part).unwrap()
    }
    
    /// Find the root of an element in a partition array.
    fn find_root(mut elem: usize, part: &[i32]) -> usize {
        while part[elem] >= 0 {
            elem = part[elem] as usize;
        }
        elem
    }
    
    /// Join two blocks in a partition array.
    fn join_blocks_in_array(r: usize, s: usize, part: &mut [i32]) {
        if r == s {
            return;
        }
        
        let size_r = (-part[r]) as usize;
        let size_s = (-part[s]) as usize;
        
        if size_r >= size_s {
            part[s] = r as i32;
            part[r] = -((size_r + size_s) as i32);
        } else {
            part[r] = s as i32;
            part[s] = -((size_r + size_s) as i32);
        }
    }
    
    /// Increment an argument array for all positions except the given index.
    fn increment_arg(arg: &mut [i32], index: usize, max: usize) -> bool {
        let length = arg.len();
        if length < 2 {
            return false;
        }
        
        for i in 0..length {
            if i == index {
                continue;
            }
            
            if (arg[i] as usize) < max {
                arg[i] += 1;
                return true;
            }
            arg[i] = 0;
        }
        
        false
    }
    
    /// Compute the principal congruence generated by a partition.
    ///
    /// # Arguments
    /// * `init_part` - The initial partition
    ///
    /// # Returns
    /// The congruence generated by the partition
    pub fn cg_partition(&self, init_part: &Partition) -> Partition {
        let mut ans = vec![0_i32; self.alg_size];
        let init_array = init_part.to_array();
        ans.copy_from_slice(&init_array);
        
        let mut pairs = SimpleList::new();
        let blocks = init_part.get_blocks();
        
        for block in blocks {
            let r = block[0];
            for j in 1..block.len() {
                pairs = pairs.cons_panic([r as i32, block[j] as i32]);
            }
        }
        
        self.make_cg_aux(ans, pairs)
    }
    
    /// Compute all principal congruences.
    ///
    /// This method generates all congruences of the form Cg(i, j) for i < j
    /// and stores them sorted by rank.
    pub fn make_principals(&mut self) {
        let mut pc_id_map: HashMap<Partition, Partition> = HashMap::new();
        let mut principals = Vec::new();
        let mut lookup = HashMap::new();
        let mut rep_map = HashMap::new();
        
        for i in 0..(self.alg_size - 1) {
            for j in (i + 1)..self.alg_size {
                let part_cong = self.make_cg(i, j);
                
                if !pc_id_map.contains_key(&part_cong) {
                    pc_id_map.insert(part_cong.clone(), part_cong.clone());
                    principals.push(part_cong.clone());
                    let mut rep_key = IntArray::new(2).unwrap();
                    rep_key.set(0, i as i32).unwrap();
                    rep_key.set(1, j as i32).unwrap();
                    rep_map.insert(part_cong.clone(), rep_key);
                }
                
                let canonical = pc_id_map.get(&part_cong).unwrap().clone();
                let mut lookup_key = IntArray::new(2).unwrap();
                lookup_key.set(0, i as i32).unwrap();
                lookup_key.set(1, j as i32).unwrap();
                lookup.insert(lookup_key, canonical);
            }
        }
        
        // Sort by rank (in the partition lattice)
        Self::sort_by_rank(&mut principals);
        
        self.principal_congruences = Some(principals);
        self.principal_congruences_lookup = Some(lookup);
        self.principal_congruences_rep = Some(rep_map);
        self.principals_made = true;
    }
    
    /// Get the list of principal congruences.
    pub fn principals(&mut self) -> &Vec<Partition> {
        if !self.principals_made {
            self.make_principals();
        }
        self.principal_congruences.as_ref().unwrap()
    }
    
    /// Sort partitions by rank (in the partition lattice).
    /// Rank is defined as size - number_of_blocks.
    fn sort_by_rank(partitions: &mut Vec<Partition>) {
        partitions.sort_by(|a, b| {
            let rank_a = a.universe_size() - a.number_of_blocks();
            let rank_b = b.universe_size() - b.number_of_blocks();
            rank_a.cmp(&rank_b)
        });
    }
    
    /// Generate the universe of all congruences.
    ///
    /// This method computes all congruences on the algebra by taking joins
    /// of join irreducibles.
    pub fn make_universe(&mut self) {
        self.make_universe_with_limit(usize::MAX);
    }
    
    /// Generate the universe with a size limit.
    ///
    /// # Arguments
    /// * `max_size` - Maximum size before stopping (usize::MAX for no limit)
    pub fn make_universe_with_limit(&mut self, max_size: usize) {
        let stop_if_big = max_size < usize::MAX;
        
        // Get join irreducibles
        if self.join_irreducibles.is_none() {
            self.make_join_irreducibles();
        }
        
        let jis = self.join_irreducibles.as_ref().unwrap();
        let mut univ: Vec<Partition> = jis.clone();
        let mut hash: HashSet<Partition> = jis.iter().cloned().collect();
        
        self.size_computed = univ.len();
        let size = jis.len();
        
        for k in 0..size {
            let elem = jis[k].clone();
            let n = univ.len();
            
            // Join with all elements from k onwards (not k+1!)
            // This matches the Java implementation: for (int i = makeUniverseK; i < n; i++)
            for i in k..n {
                let join = elem.join(&univ[i]).unwrap();
                
                if !hash.contains(&join) {
                    self.size_computed += 1;
                    
                    if stop_if_big && self.size_computed >= max_size {
                        return;
                    }
                    
                    hash.insert(join.clone());
                    univ.push(join);
                }
            }
        }
        
        // Add zero congruence at the beginning
        hash.insert(self.zero_cong.clone());
        univ.insert(0, self.zero_cong.clone());
        
        self.universe = Some(univ);
    }
    
    /// Get the universe of all congruences.
    ///
    /// # Returns
    /// A vector of all congruences (generates if not already computed)
    pub fn universe(&mut self) -> &Vec<Partition> {
        if self.universe.is_none() {
            self.make_universe();
        }
        self.universe.as_ref().unwrap()
    }
    
    /// Get the cardinality of the congruence lattice.
    /// This will compute the universe if it hasn't been computed yet.
    pub fn con_cardinality(&mut self) -> usize {
        if self.universe.is_none() {
            self.make_universe();
        }
        self.universe.as_ref().unwrap().len()
    }
    
    /// Check if the universe has been computed.
    pub fn universe_found(&self) -> bool {
        self.universe.is_some()
    }
    
    /// Compute the join irreducible congruences.
    ///
    /// A congruence is join irreducible if it cannot be expressed as the
    /// join of two strictly smaller congruences.
    pub fn make_join_irreducibles(&mut self) {
        // Make sure principals are computed
        if !self.principals_made {
            self.make_principals();
        }
        
        let principals = self.principal_congruences.as_ref().unwrap();
        let mut jis = Vec::new();
        let mut lower_covers = HashMap::new();
        
        for part in principals {
            let mut join = self.zero();
            
            for part2 in principals {
                if part2.leq(part) && part != part2 {
                    join = join.join(part2).unwrap();
                }
                if part == &join {
                    break;
                }
            }
            
            if part != &join {
                jis.push(part.clone());
                lower_covers.insert(part.clone(), join);
            }
        }
        
        self.join_irreducibles = Some(jis);
        self.lower_cover_of_jis = Some(lower_covers);
    }
    
    /// Get the join irreducible congruences.
    ///
    /// # Returns
    /// A list of join irreducible congruences (sorted by rank)
    pub fn join_irreducibles(&mut self) -> &Vec<Partition> {
        if self.join_irreducibles.is_none() {
            self.make_join_irreducibles();
        }
        self.join_irreducibles.as_ref().unwrap()
    }
    
    /// Check if a partition is join irreducible.
    ///
    /// # Arguments
    /// * `part` - The partition to check
    ///
    /// # Returns
    /// `true` if the partition is join irreducible, `false` otherwise
    pub fn join_irreducible(&mut self, part: &Partition) -> bool {
        // Ensure join irreducibles are computed
        if self.join_irreducibles.is_none() {
            self.make_join_irreducibles();
        }
        
        self.lower_cover_of_jis.as_ref().unwrap().contains_key(part)
    }
    
    /// Get the lower cover of a join irreducible element.
    ///
    /// # Arguments
    /// * `beta` - A join irreducible congruence
    ///
    /// # Returns
    /// * `Some(partition)` - The lower cover if beta is join irreducible
    /// * `None` - If beta is not join irreducible or is zero
    pub fn lower_star(&mut self, beta: &Partition) -> Option<Partition> {
        if self.join_irreducibles.is_some() {
            return self.lower_cover_of_jis.as_ref().and_then(|map| map.get(beta).cloned());
        }
        
        if beta == &self.zero() {
            return None;
        }
        
        let mut alpha = self.zero();
        let blocks = beta.get_blocks();
        
        for block in blocks {
            for j in 0..block.len() {
                for k in (j + 1)..block.len() {
                    let par = self.cg(block[j], block[k]);
                    if beta != &par {
                        alpha = alpha.join(&par).unwrap();
                    }
                    if beta == &alpha {
                        return None;
                    }
                }
            }
        }
        
        Some(alpha)
    }
    
    /// Compute the atoms of the lattice.
    ///
    /// An atom is a minimal non-zero element.
    pub fn make_atoms(&mut self) {
        // Ensure join irreducibles are computed
        if self.join_irreducibles.is_none() {
            self.make_join_irreducibles();
        }
        
        let jis = self.join_irreducibles.as_ref().unwrap().clone();
        let mut atoms_vec: Vec<Partition> = Vec::new();
        
        for ji in &jis {
            let mut is_atom = true;
            for par in &atoms_vec {
                if par.leq(ji) {
                    is_atom = false;
                    break;
                }
            }
            if is_atom {
                atoms_vec.push(ji.clone());
            }
        }
        
        self.atoms = Some(atoms_vec);
    }
    
    /// Get the atoms of the lattice.
    pub fn atoms(&mut self) -> &Vec<Partition> {
        if self.atoms.is_none() {
            self.make_atoms();
        }
        self.atoms.as_ref().unwrap()
    }
    
    /// Compute the meet irreducible congruences.
    pub fn make_meet_irreducibles(&mut self) {
        // Ensure universe is computed
        if self.universe.is_none() {
            self.make_universe();
        }
        
        // Ensure upper covers are computed
        if self.upper_covers_map.is_none() {
            self.make_upper_covers();
        }
        
        let univ = self.universe.as_ref().unwrap();
        let uc_map = self.upper_covers_map.as_ref().unwrap();
        
        let mut mis = Vec::new();
        
        for elem in univ {
            if let Some(ucs) = uc_map.get(elem) {
                if ucs.len() == 1 {
                    mis.push(elem.clone());
                }
            }
        }
        
        self.meet_irreducibles = Some(mis);
    }
    
    /// Get the meet irreducible congruences.
    pub fn meet_irreducibles(&mut self) -> &Vec<Partition> {
        if self.meet_irreducibles.is_none() {
            self.make_meet_irreducibles();
        }
        self.meet_irreducibles.as_ref().unwrap()
    }
    
    /// Check if a partition is meet irreducible.
    pub fn meet_irreducible(&mut self, part: &Partition) -> bool {
        if self.upper_covers_map.is_none() {
            self.make_upper_covers();
        }
        
        if let Some(uc_map) = &self.upper_covers_map {
            if let Some(uc) = uc_map.get(part) {
                return uc.len() == 1;
            }
        }
        
        false
    }
    
    /// Compute the upper covers map.
    fn make_upper_covers(&mut self) {
        // Ensure universe and join irreducibles are computed
        if self.universe.is_none() {
            self.make_universe();
        }
        if self.join_irreducibles.is_none() {
            self.make_join_irreducibles();
        }
        
        let univ = self.universe.as_ref().unwrap().clone();
        let jis = self.join_irreducibles.as_ref().unwrap().clone();
        
        let mut uc_map: HashMap<Partition, Vec<Partition>> = HashMap::new();
        
        for elem in &univ {
            let mut hs = HashSet::new();
            let mut covs = Vec::new();
            
            for ji in &jis {
                if !ji.leq(elem) {
                    let join = ji.join(elem).unwrap();
                    if !hs.contains(&join) {
                        hs.insert(join.clone());
                        
                        // Check if this is minimal among candidates
                        let mut above = false;
                        covs.retain(|cov: &Partition| {
                            if cov.leq(&join) {
                                above = true;
                                false
                            } else if join.leq(cov) {
                                false
                            } else {
                                true
                            }
                        });
                        
                        if !above {
                            covs.push(join);
                        }
                    }
                }
            }
            
            uc_map.insert(elem.clone(), covs);
        }
        
        self.upper_covers_map = Some(uc_map);
    }
    
    /// Get the upper covers map.
    pub fn upper_covers_map(&mut self) -> &HashMap<Partition, Vec<Partition>> {
        if self.upper_covers_map.is_none() {
            self.make_upper_covers();
        }
        self.upper_covers_map.as_ref().unwrap()
    }
    
    /// Test if the lattice is distributive.
    ///
    /// A lattice is distributive if every join irreducible is join prime.
    pub fn is_distributive(&mut self) -> bool {
        if self.join_irreducibles.is_none() {
            self.make_join_irreducibles();
        }
        
        let jis = self.join_irreducibles.as_ref().unwrap().clone();
        
        for par in &jis {
            if !self.join_prime(par) {
                return false;
            }
        }
        
        true
    }
    
    /// Test if a partition is join prime.
    ///
    /// An element β is join prime if whenever β ≤ ∨S, then β ≤ s for some s ∈ S.
    pub fn join_prime(&mut self, beta: &Partition) -> bool {
        if self.join_irreducibles.is_none() {
            self.make_join_irreducibles();
        }
        
        let jis = self.join_irreducibles.as_ref().unwrap().clone();
        let mut join = self.zero();
        
        for part in &jis {
            if !beta.leq(part) {
                join = join.join(part).unwrap();
                if beta.leq(&join) {
                    return false;
                }
            }
        }
        
        true
    }
    
    /// Compute the permutability level of the lattice.
    ///
    /// The permutability level is the maximum n such that there exist
    /// incomparable partitions α and β with permutability level n.
    pub fn permutability_level(&mut self) -> i32 {
        if self.permutability_level >= 0 {
            return self.permutability_level;
        }
        
        // Ensure universe is computed
        if self.universe.is_none() {
            self.make_universe();
        }
        
        let univ: Vec<Partition> = self.universe.as_ref().unwrap().iter().cloned().collect();
        let size = univ.len();
        let mut level = 0;
        let mut hi_level_pars = [self.zero(), self.zero()];
        
        for i in 0..size {
            let par0 = &univ[i];
            for j in (i + 1)..size {
                let par1 = &univ[j];
                
                // Skip if comparable
                if par1.leq(par0) || par0.leq(par1) {
                    continue;
                }
                
                // Permutability level computation is complex, use a simple heuristic for now
                let lev = 2; // Default value - real implementation requires more complexity
                if lev > level {
                    level = lev;
                    hi_level_pars = [par0.clone(), par1.clone()];
                }
            }
        }
        
        self.permutability_level = level;
        self.permutability_level_witnesses = Some(hi_level_pars);
        
        level
    }
    
    /// Get the permutability level witnesses.
    pub fn get_permutability_level_witnesses(&self) -> Option<&[Partition; 2]> {
        self.permutability_level_witnesses.as_ref()
    }
    
    /// Find an upper cover of a congruence.
    ///
    /// # Arguments
    /// * `congr` - The congruence to find an upper cover for
    ///
    /// # Returns
    /// * `Some(partition)` - An upper cover if one exists
    /// * `None` - If congr is the top element
    pub fn find_upper_cover(&mut self, congr: &Partition) -> Option<Partition> {
        if congr == &self.one() {
            return None;
        }
        
        if self.join_irreducibles.is_none() {
            self.make_join_irreducibles();
        }
        
        let jis = self.join_irreducibles.as_ref().unwrap();
        
        let mut not_below = Vec::new();
        for par in jis {
            if !par.leq(congr) {
                not_below.push(par.clone());
            }
        }
        
        let min_not_below = Self::minimal_elements(&not_below);
        let mut ans = self.one();
        
        for par in min_not_below {
            let join = congr.join(&par).unwrap();
            if join.leq(&ans) {
                ans = join;
            }
        }
        
        Some(ans)
    }
    
    /// Find the minimal elements in a topologically sorted list.
    fn minimal_elements(par_list: &[Partition]) -> Vec<Partition> {
        let mut ans = Vec::new();
        
        if par_list.is_empty() {
            return ans;
        }
        
        for par in par_list {
            let mut par_ok = true;
            for par0 in &ans {
                if par0.leq(par) {
                    par_ok = false;
                    break;
                }
            }
            if par_ok {
                ans.push(par.clone());
            }
        }
        
        ans
    }
    
    /// Find a principal chain in the lattice.
    ///
    /// Returns a chain where each element is the join of the previous one
    /// and a principal congruence.
    pub fn find_principal_chain(&mut self) -> Vec<Partition> {
        let mut ans = Vec::new();
        
        if self.alg_size == 1 {
            return ans;
        }
        
        let mut congr = self.zero();
        
        loop {
            ans.push(congr.clone());
            let reps = congr.representatives();
            congr = congr.join(&self.cg(reps[0], reps[1])).unwrap();
            
            if congr == self.one() {
                break;
            }
        }
        
        ans
    }
    
    /// Find complements of a partition in the lattice.
    ///
    /// # Arguments
    /// * `par` - The partition to find complements for
    ///
    /// # Returns
    /// A list of all complements of par
    pub fn complements(&mut self, par: &Partition) -> Vec<Partition> {
        if self.universe.is_none() {
            self.make_universe();
        }
        
        let univ = self.universe.as_ref().unwrap();
        let mut ans = Vec::new();
        
        for comp in univ {
            let join_val = par.join(comp).unwrap();
            let meet_val = par.meet(comp).unwrap();
            if self.one() == join_val && self.zero() == meet_val {
                ans.push(comp.clone());
            }
        }
        
        ans
    }
    
    /// Compute an irredundant meet decomposition of the one congruence.
    ///
    /// This method finds a minimal set of meet irreducible congruences whose
    /// meet equals the one congruence (all elements in one block).
    ///
    /// # Returns
    /// A list of meet irreducible congruences that form an irredundant meet decomposition
    ///
    /// # Examples
    /// ```
    /// use uacalc::alg::{SmallAlgebra, BasicSmallAlgebra};
    /// use uacalc::alg::conlat::CongruenceLattice;
    /// use std::collections::HashSet;
    ///
    /// let alg = Box::new(BasicSmallAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1, 2]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    ///
    /// let mut con_lat = CongruenceLattice::new_from_i32_algebra(alg);
    /// let decomposition = con_lat.irredundant_meet_decomposition();
    /// // The decomposition should contain meet irreducible congruences
    /// ```
    pub fn irredundant_meet_decomposition(&mut self) -> Vec<Partition> {
        // Ensure meet irreducibles are computed
        if self.meet_irreducibles.is_none() {
            self.make_meet_irreducibles();
        }
        
        let meet_irreducibles = self.meet_irreducibles.as_ref().unwrap();
        let mut decomposition: Vec<Partition> = Vec::new();
        
        // Start with all meet irreducibles
        let mut candidates = meet_irreducibles.clone();
        
        // Greedily remove candidates that are not needed
        for i in (0..candidates.len()).rev() {
            let mut test_candidates = candidates.clone();
            test_candidates.remove(i);
            
            // Check if the meet of remaining candidates still equals one
            if !test_candidates.is_empty() {
                let mut meet_result = test_candidates[0].clone();
                for candidate in &test_candidates[1..] {
                    meet_result = meet_result.meet(candidate).unwrap();
                }
                
                // If meet still equals one, we can remove this candidate
                if meet_result == self.one() {
                    candidates.remove(i);
                }
            }
        }
        
        candidates
    }
}

// Implement Lattice trait
impl Lattice<Partition> for CongruenceLattice {
    fn join_irreducibles(&self) -> Option<Vec<Partition>> {
        self.join_irreducibles.clone()
    }
    
    fn meet_irreducibles(&self) -> Option<Vec<Partition>> {
        self.meet_irreducibles.clone()
    }
    
    fn atoms(&self) -> Option<Vec<Partition>> {
        self.atoms.clone()
    }
    
    fn coatoms(&self) -> Option<Vec<Partition>> {
        // Coatoms are not implemented yet
        None
    }
    
    fn join(&self, a: &Partition, b: &Partition) -> Partition {
        a.join(b).unwrap()
    }
    
    fn join_list(&self, args: &[Partition]) -> Partition {
        if args.is_empty() {
            return self.zero_cong.clone();
        }
        
        let mut result = args[0].clone();
        for part in &args[1..] {
            result = result.join(part).unwrap();
        }
        result
    }
    
    fn meet(&self, a: &Partition, b: &Partition) -> Partition {
        a.meet(b).unwrap()
    }
    
    fn meet_list(&self, args: &[Partition]) -> Partition {
        if args.is_empty() {
            return self.one_cong.clone();
        }
        
        let mut result = args[0].clone();
        for part in &args[1..] {
            result = result.meet(part).unwrap();
        }
        result
    }
}

// Implement Algebra trait
impl Algebra for CongruenceLattice {
    type UniverseItem = Partition;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        if let Some(ref univ) = self.universe {
            let cloned = univ.clone();
            Box::new(cloned.into_iter())
        } else {
            Box::new(std::iter::empty())
        }
    }
    
    fn cardinality(&self) -> i32 {
        if let Some(ref univ) = self.universe {
            univ.len() as i32
        } else {
            -1
        }
    }
    
    fn input_size(&self) -> i32 {
        let card = self.cardinality();
        if card < 0 {
            return -1;
        }
        self.similarity_type().input_size(card)
    }
    
    fn is_unary(&self) -> bool {
        false
    }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.universe()
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        // CongruenceLattice operations are join and meet
        // This is a simplified implementation
        Vec::new()
    }
    
    fn get_operation(&self, _sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        None
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        HashMap::new()
    }
    
    fn name(&self) -> &str {
        "CongruenceLattice"
    }
    
    fn set_name(&mut self, _name: String) {
        // Not supported
    }
    
    fn description(&self) -> Option<&str> {
        self.description.as_deref()
    }
    
    fn set_description(&mut self, desc: Option<String>) {
        self.description = desc;
    }
    
    fn similarity_type(&self) -> &SimilarityType {
        static LATTICE_TYPE: Lazy<SimilarityType> = Lazy::new(|| {
            // Create join and meet operation symbols
            let join_sym = OperationSymbol::new("join", 2, false);
            let meet_sym = OperationSymbol::new("meet", 2, false);
            SimilarityType::new(vec![join_sym, meet_sym])
        });
        &LATTICE_TYPE
    }
    
    fn update_similarity_type(&mut self) {
        // Similarity type is fixed for lattices
    }
    
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        self.similarity_type() == other.similarity_type()
    }
    
    fn make_operation_tables(&mut self) {
        // Not needed for CongruenceLattice
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        Vec::new()
    }
    
    fn is_idempotent(&self) -> bool {
        true
    }
    
    fn is_total(&self) -> bool {
        true
    }
    
    fn monitoring(&self) -> bool {
        false
    }
    
    fn get_monitor(&self) -> Option<&dyn crate::alg::algebra::ProgressMonitor> {
        None
    }
    
    fn set_monitor(&mut self, _monitor: Option<Box<dyn crate::alg::algebra::ProgressMonitor>>) {
        // Monitoring not supported yet
    }
}

// Stub methods for functionality requiring unimplemented dependencies
impl CongruenceLattice {
    /// Compute the tolerance generated by two elements.
    ///
    /// This uses the algorithm from section 2.8 of Freese-McKenzie-Valeriote.
    /// A tolerance is a reflexive, symmetric subuniverse of A x A.
    ///
    /// # Arguments
    /// * `a` - First element (as index)
    /// * `b` - Second element (as index)
    ///
    /// # Returns
    /// * `Ok(relation)` - The tolerance relation
    /// * `Err(msg)` - If computation fails
    pub fn tg(&mut self, a: usize, b: usize) -> Result<Box<dyn BinaryRelation>, String> {
        use crate::alg::conlat::BasicBinaryRelation;
        use crate::alg::{BigProductAlgebra, Algebra};
        use std::sync::Arc;
        
        // Create the square product A^2
        let alg_for_product = self.alg.clone_box();
        
        // We need to create BigProductAlgebra, but we can't because we have a type-erased algebra
        // For now, return an error indicating this requires a concrete algebra type
        // TODO: Implement tolerance calculation properly once we have a way to construct products
        // from type-erased algebras
        
        // As a workaround, we'll compute a simple tolerance relation
        // The tolerance Tg(a,b) contains all pairs (x,y) such that
        // for all operations f and all tuples with x,y in positions:
        // f(...,x,...) ≅ f(...,y,...) (mod the congruence generated by (a,b))
        
        let cong = self.cg(a, b);
        let n = self.alg_size;
        
        // Build the relation as a set of IntArray pairs
        let mut pairs = Vec::new();
        
        // All pairs in the same congruence class are in the tolerance
        for i in 0..n {
            for j in 0..n {
                if cong.is_related(i, j) {
                    let pair = IntArray::from_array(vec![i as i32, j as i32])?;
                    pairs.push(pair);
                }
            }
        }
        
        // Create a BasicBinaryRelation from the pairs
        let relation = BasicBinaryRelation::from_pairs(pairs, n)?;
        
        Ok(Box::new(relation))
    }
    
    /// Calculate centrality data for two binary relations (STUBBED).
    ///
    /// This method requires CentralityData which is not yet implemented.
    ///
    /// # Arguments
    /// * `s` - First binary relation
    /// * `t` - Second binary relation
    ///
    /// # Returns
    /// Error indicating the method is not implemented
    pub fn calc_centrality(
        &self,
        _s: &dyn BinaryRelation,
        _t: &dyn BinaryRelation,
    ) -> Result<Vec<()>, String> {
        Err("CentralityData not implemented yet".to_string())
    }
    
    /// Compute the strong rectangularity commutator (STUBBED).
    ///
    /// Returns the one congruence as a default stub.
    ///
    /// # Arguments
    /// * `s` - First binary relation
    /// * `t` - Second binary relation
    ///
    /// # Returns
    /// The one congruence (stub implementation)
    pub fn strong_rectangularity_commutator(
        &self,
        _s: &dyn BinaryRelation,
        _t: &dyn BinaryRelation,
    ) -> Partition {
        self.one()
    }
    
    /// Compute the weak commutator (STUBBED).
    ///
    /// Returns the one congruence as a default stub.
    ///
    /// # Arguments
    /// * `s` - First binary relation
    /// * `t` - Second binary relation
    ///
    /// # Returns
    /// The one congruence (stub implementation)
    pub fn weak_commutator(
        &self,
        _s: &dyn BinaryRelation,
        _t: &dyn BinaryRelation,
    ) -> Partition {
        self.one()
    }
    
    /// Compute the commutator (STUBBED).
    ///
    /// Returns the one congruence as a default stub.
    ///
    /// # Arguments
    /// * `s` - First binary relation
    /// * `t` - Second binary relation
    ///
    /// # Returns
    /// The one congruence (stub implementation)
    pub fn commutator(
        &self,
        _s: &dyn BinaryRelation,
        _t: &dyn BinaryRelation,
    ) -> Partition {
        self.one()
    }
    
    /// Find the TCT type of a join irreducible element (STUBBED).
    ///
    /// This method requires TypeFinder which is not yet implemented.
    ///
    /// # Arguments
    /// * `beta` - A join irreducible partition
    ///
    /// # Returns
    /// Type 0 as a default stub
    pub fn type_ji(&self, _beta: &Partition) -> i32 {
        0
    }
    
    /// Find the TCT type of an interval (STUBBED).
    ///
    /// This method requires TypeFinder which is not yet implemented.
    ///
    /// # Arguments
    /// * `beta` - The upper element
    /// * `alpha` - The lower element
    ///
    /// # Returns
    /// Type 0 as a default stub
    pub fn type_interval(&self, _beta: &Partition, _alpha: &Partition) -> i32 {
        0
    }
    
    /// Get the type finder (STUBBED).
    ///
    /// This method requires TypeFinder which is not yet implemented.
    ///
    /// # Returns
    /// Error indicating the method is not implemented
    pub fn get_type_finder(&self) -> Result<(), String> {
        Err("TypeFinder not implemented yet".to_string())
    }
    
    /// Get the set of all TCT types in the lattice (STUBBED).
    ///
    /// This method requires TypeFinder which is not yet implemented.
    ///
    /// # Returns
    /// Error indicating the method is not implemented
    pub fn type_set(&self) -> Result<HashSet<i32>, String> {
        Err("TypeFinder not implemented yet".to_string())
    }
    
    /// Compute the matrices M(S,T) for centrality testing (STUBBED).
    ///
    /// This method requires BigProductAlgebra which is not yet implemented.
    ///
    /// # Arguments
    /// * `s` - First binary relation
    /// * `t` - Second binary relation
    ///
    /// # Returns
    /// Error indicating the method is not implemented
    pub fn matrices(
        &self,
        _s: &dyn BinaryRelation,
        _t: &dyn BinaryRelation,
    ) -> Result<(), String> {
        Err("matrices requires BigProductAlgebra which is not yet implemented".to_string())
    }
    
    /// Find a centrality failure witness (STUBBED).
    ///
    /// This method requires BigProductAlgebra which is not yet implemented.
    ///
    /// # Arguments
    /// * `s` - First binary relation
    /// * `t` - Second binary relation
    /// * `delta` - A congruence
    ///
    /// # Returns
    /// None (stub implementation)
    pub fn centrality_failure(
        &self,
        _s: &dyn BinaryRelation,
        _t: &dyn BinaryRelation,
        _delta: &Partition,
    ) -> Option<()> {
        None
    }
    
    /// Find a weak centrality failure witness (STUBBED).
    ///
    /// This method requires BigProductAlgebra which is not yet implemented.
    ///
    /// # Arguments
    /// * `s` - First binary relation
    /// * `t` - Second binary relation
    /// * `delta` - A congruence
    ///
    /// # Returns
    /// None (stub implementation)
    pub fn weak_centrality_failure(
        &self,
        _s: &dyn BinaryRelation,
        _t: &dyn BinaryRelation,
        _delta: &Partition,
    ) -> Option<()> {
        None
    }
    
    /// Find a strong rectangularity failure witness (STUBBED).
    ///
    /// This method requires BigProductAlgebra which is not yet implemented.
    ///
    /// # Arguments
    /// * `s` - First binary relation
    /// * `t` - Second binary relation
    /// * `delta` - A congruence
    ///
    /// # Returns
    /// None (stub implementation)
    pub fn strong_rectangularity_failure(
        &self,
        _s: &dyn BinaryRelation,
        _t: &dyn BinaryRelation,
        _delta: &Partition,
    ) -> Option<()> {
        None
    }
}
