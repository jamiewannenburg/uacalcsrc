use std::cmp::Ordering;
use std::collections::HashSet;
use std::fmt::{self, Debug, Display};
use std::hash::{Hash, Hasher};
use crate::util::int_array::IntArrayTrait;
use crate::util::array_string;
use crate::alg::small_algebra::SmallAlgebra;

/// A basic set implementation for representing sets of integers {0, 1, ..., n-1}.
/// 
/// This struct provides basic set operations including union, intersection, difference,
/// and membership testing. It extends the functionality of IntArray with set-specific
/// operations and maintains elements in sorted order for efficient operations.
/// 
/// # Examples
/// ```
/// use uacalc::alg::sublat::BasicSet;
/// 
/// let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
/// let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
/// 
/// let intersection = set1.intersection(&set2);
/// assert_eq!(intersection.elements(), &vec![3]);
/// ```
#[derive(Debug, Clone)]
pub struct BasicSet {
    /// The elements of the set, stored in sorted order
    pub elements: Vec<i32>,
}

impl BasicSet {
    /// Empty set constant
    pub const EMPTY_SET: BasicSet = BasicSet { elements: vec![] };
    
    /// Create a new BasicSet from a vector of elements.
    /// 
    /// The elements will be automatically sorted and deduplicated.
    /// 
    /// # Arguments
    /// * `elements` - Vector of integers to include in the set
    /// 
    /// # Returns
    /// * `Ok(BasicSet)` - Successfully created set
    /// * `Err(String)` - If elements contain invalid values
    /// 
/// # Examples
/// ```
/// use uacalc::alg::sublat::BasicSet;
/// 
/// let set = BasicSet::new(vec![3, 1, 2]).unwrap();
/// assert_eq!(set.elements(), &vec![1, 2, 3]);
/// ```
    pub fn new(elements: Vec<i32>) -> Result<Self, String> {
        let mut set = BasicSet { elements };
        set.normalize();
        Ok(set)
    }
    
    /// Create a new BasicSet with proper error handling.
    /// 
    /// # Arguments
    /// * `elements` - Vector of integers to include in the set
    /// 
    /// # Returns
    /// * `Ok(BasicSet)` - Successfully created set
    /// * `Err(String)` - If elements contain invalid values
    pub fn new_safe(elements: Vec<i32>) -> Result<Self, String> {
        Self::new(elements)
    }
    
    /// Get the elements of the set.
    /// 
    /// # Returns
    /// A reference to the sorted elements vector
    pub fn elements(&self) -> &Vec<i32> {
        &self.elements
    }
    
    /// Get the size of the set (number of elements).
    /// 
    /// # Returns
    /// The number of elements in the set
    pub fn size(&self) -> usize {
        self.elements.len()
    }
    
    /// Get the universe size (same as size for BasicSet).
    /// 
    /// # Returns
    /// The number of elements in the set
    pub fn universe_size(&self) -> usize {
        self.elements.len()
    }
    
    /// Normalize the set by sorting elements and removing duplicates.
    /// 
    /// This method modifies the internal elements vector to ensure
    /// they are in ascending order with no duplicates.
    pub fn normalize(&mut self) {
        // Remove duplicates using HashSet
        let unique_elements: HashSet<i32> = self.elements.drain(..).collect();
        
        // Convert back to sorted vector
        self.elements = unique_elements.into_iter().collect();
        self.elements.sort();
    }
    
    /// Check if this set is a subset of another set.
    /// 
    /// # Arguments
    /// * `other` - The set to compare against
    /// 
    /// # Returns
    /// * `true` if this set is a subset of other
    /// * `false` otherwise
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::BasicSet;
    /// 
    /// let set1 = BasicSet::new(vec![1, 2]).unwrap();
    /// let set2 = BasicSet::new(vec![1, 2, 3, 4]).unwrap();
    /// assert!(set1.leq(&set2));
    /// ```
    pub fn leq(&self, other: &BasicSet) -> bool {
        Self::leq_static(&self.elements, &other.elements)
    }
    
    /// Static method to check if one array is a subset of another.
    /// 
    /// # Arguments
    /// * `u` - First array (sorted)
    /// * `v` - Second array (sorted)
    /// 
    /// # Returns
    /// * `true` if u is a subset of v
    /// * `false` otherwise
    pub fn leq_static(u: &[i32], v: &[i32]) -> bool {
        let n = u.len();
        let m = v.len();
        if m < n {
            return false;
        }
        
        let mut j = 0;
        for i in 0..n {
            let mut found = false;
            while j < m {
                if u[i] < v[j] {
                    return false;
                }
                if u[i] == v[j] {
                    found = true;
                    j += 1;
                    break;
                }
                j += 1;
            }
            if !found {
                return false;
            }
        }
        true
    }
    
    /// Check if the set contains a specific element.
    /// 
    /// # Arguments
    /// * `element` - The element to search for
    /// 
    /// # Returns
    /// * `true` if the element is in the set
    /// * `false` otherwise
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::BasicSet;
    /// 
    /// let set = BasicSet::new(vec![1, 3, 5]).unwrap();
    /// assert!(set.contains(3));
    /// assert!(!set.contains(2));
    /// ```
    pub fn contains(&self, element: i32) -> bool {
        self.elements.binary_search(&element).is_ok()
    }
    
    /// Compute the set difference (this - other).
    /// 
    /// # Arguments
    /// * `other` - The set to subtract
    /// 
    /// # Returns
    /// A new BasicSet containing elements in this set but not in other
    /// 
/// # Examples
/// ```
/// use uacalc::alg::sublat::BasicSet;
/// 
/// let set1 = BasicSet::new(vec![1, 2, 3, 4]).unwrap();
/// let set2 = BasicSet::new(vec![2, 4]).unwrap();
/// let diff = set1.set_difference(&set2);
/// assert_eq!(diff.elements(), &vec![1, 3]);
/// ```
    pub fn set_difference(&self, other: &BasicSet) -> BasicSet {
        let mut result = Vec::new();
        for &element in &self.elements {
            if !other.contains(element) {
                result.push(element);
            }
        }
        BasicSet { elements: result }
    }
    
    /// Compute the intersection of this set with another.
    /// 
    /// # Arguments
    /// * `other` - The set to intersect with
    /// 
    /// # Returns
    /// A new BasicSet containing elements in both sets
    /// 
/// # Examples
/// ```
/// use uacalc::alg::sublat::BasicSet;
/// 
/// let set1 = BasicSet::new(vec![1, 2, 3]).unwrap();
/// let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
/// let intersection = set1.intersection(&set2);
/// assert_eq!(intersection.elements(), &vec![2, 3]);
/// ```
    pub fn intersection(&self, other: &BasicSet) -> BasicSet {
        Self::intersection_static(self, other)
    }
    
    /// Static method to compute the intersection of two sets.
    /// 
    /// # Arguments
    /// * `set1` - First set
    /// * `set2` - Second set
    /// 
    /// # Returns
    /// A new BasicSet containing elements in both sets
    pub fn intersection_static(set1: &BasicSet, set2: &BasicSet) -> BasicSet {
        let mut result = Vec::new();
        for &element in &set1.elements {
            if set2.contains(element) {
                result.push(element);
            }
        }
        BasicSet { elements: result }
    }
    
    /// Compute the union of this set with another.
    /// 
    /// # Arguments
    /// * `other` - The set to union with
    /// 
    /// # Returns
    /// A new BasicSet containing elements from both sets
    /// 
/// # Examples
/// ```
/// use uacalc::alg::sublat::BasicSet;
/// 
/// let set1 = BasicSet::new(vec![1, 2]).unwrap();
/// let set2 = BasicSet::new(vec![2, 3]).unwrap();
/// let union = set1.union(&set2);
/// assert_eq!(union.elements(), &vec![1, 2, 3]);
/// ```
    pub fn union(&self, other: &BasicSet) -> BasicSet {
        Self::union_static(self, other)
    }
    
    /// Static method to compute the union of two sets.
    /// 
    /// # Arguments
    /// * `set1` - First set
    /// * `set2` - Second set
    /// 
    /// # Returns
    /// A new BasicSet containing elements from both sets
    pub fn union_static(set1: &BasicSet, set2: &BasicSet) -> BasicSet {
        let mut result = Vec::new();
        
        // Add all elements from set1
        for &element in &set1.elements {
            result.push(element);
        }
        
        // Add elements from set2 that are not already in result
        for &element in &set2.elements {
            if !result.contains(&element) {
                result.push(element);
            }
        }
        
        // Sort the result
        result.sort();
        BasicSet { elements: result }
    }
    
    /// Convert the set to a string representation using algebra elements.
    /// 
    /// # Arguments
    /// * `alg` - The algebra to use for element representation
    /// 
    /// # Returns
    /// A string representation of the set using algebra elements
    pub fn to_string_with_algebra<T>(&self, alg: &dyn SmallAlgebra<UniverseItem = T>) -> String 
    where 
        T: std::fmt::Display + Clone + PartialEq + Eq + Hash + std::fmt::Debug
    {
        let mut result = String::from("{");
        for (i, &element) in self.elements.iter().enumerate() {
            if i > 0 {
                result.push(',');
            }
            if let Some(elem) = alg.get_element(element as usize) {
                result.push_str(&array_string::to_string(&[elem]));
            } else {
                result.push_str(&element.to_string());
            }
        }
        result.push('}');
        result
    }
}

impl PartialEq for BasicSet {
    fn eq(&self, other: &Self) -> bool {
        self.elements == other.elements
    }
}

impl Eq for BasicSet {}

impl PartialOrd for BasicSet {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for BasicSet {
    fn cmp(&self, other: &Self) -> Ordering {
        // First compare by size
        match self.size().cmp(&other.size()) {
            Ordering::Equal => {
                // Then compare lexicographically
                self.elements.cmp(&other.elements)
            }
            other => other,
        }
    }
}

impl Hash for BasicSet {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.elements.hash(state);
    }
}

impl fmt::Display for BasicSet {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{{")?;
        for (i, &element) in self.elements.iter().enumerate() {
            if i > 0 {
                write!(f, ",")?;
            }
            write!(f, "{}", element)?;
        }
        write!(f, "}}")
    }
}

impl IntArrayTrait for BasicSet {
    fn universe_size(&self) -> usize {
        self.universe_size()
    }
    
    fn as_slice(&self) -> &[i32] {
        &self.elements
    }
    
    fn get(&self, index: usize) -> Option<i32> {
        self.elements.get(index).copied()
    }
    
    fn set(&mut self, index: usize, value: i32) -> Result<(), String> {
        if index >= self.elements.len() {
            return Err("Index out of bounds".to_string());
        }
        self.elements[index] = value;
        self.normalize();
        Ok(())
    }
    
    fn satisfies_blocks_constraint(&self, blocks: &[Vec<usize>]) -> bool {
        // For BasicSet, we check if all elements in each block are the same
        for block in blocks {
            if block.is_empty() {
                continue;
            }
            let first_element = self.elements[block[0]];
            for &index in block.iter().skip(1) {
                if index < self.elements.len() && self.elements[index] != first_element {
                    return false;
                }
            }
        }
        true
    }
    
    fn satisfies_values_constraint(&self, values: &[(usize, i32)]) -> bool {
        for &(index, expected_value) in values {
            if index >= self.elements.len() || self.elements[index] != expected_value {
                return false;
            }
        }
        true
    }
    
    fn satisfies_set_constraint(&self, index: usize, possible_values: &HashSet<i32>) -> bool {
        if index >= self.elements.len() {
            return false;
        }
        possible_values.contains(&self.elements[index])
    }
    
    fn satisfies_congruence_constraint(&self, index: usize, alpha: &crate::alg::conlat::partition::Partition, elem_index: usize) -> bool {
        if index >= self.elements.len() || elem_index >= self.elements.len() {
            return false;
        }
        // Check if elements are in the same block of the partition
        alpha.is_related(index, elem_index)
    }
    
    fn is_idempotent(&self) -> bool {
        // For BasicSet, check if all elements are their own indices
        for (i, &element) in self.elements.iter().enumerate() {
            if element != i as i32 {
                return false;
            }
        }
        true
    }
    
    fn is_constant(&self) -> bool {
        if self.elements.is_empty() {
            return true;
        }
        let first = self.elements[0];
        self.elements.iter().all(|&x| x == first)
    }
    
    fn clone_array(&self) -> Box<dyn IntArrayTrait> {
        Box::new(self.clone())
    }
}

use crate::alg::{Algebra, ProgressMonitor};
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};
use crate::alg::subalgebra::Subalgebra;
use crate::util::{ArrayIncrementor, SequenceGenerator, PermutationGenerator};
use crate::lat::{Order, Lattice};
use std::collections::HashMap;

/// Maximum size for drawable lattices
pub const MAX_DRAWABLE_SIZE: usize = 100;

/// A class to represent the subalgebra lattice of a basic algebra.
/// 
/// The subalgebra lattice represents all subalgebras of an algebra,
/// ordered by inclusion. It provides methods for computing subalgebras,
/// join and meet operations, and lattice-theoretic properties.
/// 
/// # Examples
/// ```
/// use uacalc::alg::sublat::SubalgebraLattice;
/// use uacalc::alg::{SmallAlgebra, BasicAlgebra};
/// use std::collections::HashSet;
/// 
/// // Create a small algebra
/// let alg = Box::new(BasicAlgebra::new(
///     "TestAlg".to_string(),
///     HashSet::from([0, 1, 2]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Create subalgebra lattice
/// let sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
/// assert_eq!(sub_lat.get_algebra().name(), "TestAlg");
/// ```
pub struct SubalgebraLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    /// The underlying algebra
    alg: Box<dyn SmallAlgebra<UniverseItem = T>>,
    /// Size of the algebra
    alg_size: i32,
    /// Number of operations
    num_ops: i32,
    /// The zero subalgebra (generated by constants)
    zero_subalg: BasicSet,
    /// The one subalgebra (entire algebra)
    one_subalg: BasicSet,
    /// Optional description
    description: Option<String>,
    /// Whether the lattice is too large to draw
    non_drawable: bool,
    
    // Cached computations (lazy initialization)
    /// Map from elements to their one-generated subalgebras
    one_generated_subalg_lookup: Option<HashMap<i32, BasicSet>>,
    /// Map from one-generated subalgebras to a generator
    one_generated_subalg_generator: Option<HashMap<BasicSet, i32>>,
    /// The universe of all subalgebras
    universe: Option<HashSet<BasicSet>>,
    /// Map from elements to their upper covers
    upper_covers_map: Option<HashMap<BasicSet, Vec<BasicSet>>>,
    /// Map from join irreducibles to their lower cover
    lower_cover_of_jis: Option<HashMap<BasicSet, BasicSet>>,
    /// List of one-generated subalgebras
    one_generated_subalgebras: Option<Vec<BasicSet>>,
    /// List of join irreducible elements
    join_irreducibles: Option<Vec<BasicSet>>,
    /// List of meet irreducible elements
    meet_irreducibles: Option<Vec<BasicSet>>,
    /// Hash set of join irreducibles for fast lookup
    jis_hash: Option<HashSet<BasicSet>>,
    
    // Progress tracking
    /// Size computed so far
    size_computed: i32,
    /// Whether join irreducibles have been made
    jis_made: bool,
    /// Flag to stop universe computation
    stop_make_universe: bool,
    /// Current k value in universe computation
    make_universe_k: i32,
}

impl<T> Clone for SubalgebraLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn clone(&self) -> Self {
        SubalgebraLattice {
            alg: self.alg.clone_box(),
            alg_size: self.alg_size,
            num_ops: self.num_ops,
            zero_subalg: self.zero_subalg.clone(),
            one_subalg: self.one_subalg.clone(),
            description: self.description.clone(),
            non_drawable: self.non_drawable,
            one_generated_subalg_lookup: None,
            one_generated_subalg_generator: None,
            universe: None,
            upper_covers_map: None,
            lower_cover_of_jis: None,
            one_generated_subalgebras: None,
            join_irreducibles: None,
            meet_irreducibles: None,
            jis_hash: None,
            size_computed: 0,
            jis_made: false,
            stop_make_universe: false,
            make_universe_k: 0,
        }
    }
}

impl<T> SubalgebraLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    /// Create a new SubalgebraLattice from an algebra.
    /// 
    /// # Arguments
    /// * `alg` - The underlying algebra
    /// 
    /// # Returns
    /// * `Ok(SubalgebraLattice)` - Successfully created subalgebra lattice
    /// * `Err(String)` - If the algebra is invalid
    ///
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::SubalgebraLattice;
    /// use uacalc::alg::{SmallAlgebra, BasicAlgebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "TestAlg".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
    /// assert_eq!(sub_lat.get_algebra().name(), "TestAlg");
    /// ```
    pub fn new_safe(alg: Box<dyn SmallAlgebra<UniverseItem = T>>) -> Result<Self, String> {
        let alg_size = alg.cardinality();
        if alg_size <= 0 {
            return Err("Algebra must have positive cardinality".to_string());
        }
        
        let operations = alg.get_operations_ref();
        let num_ops = operations.len() as i32;
        
        // Create one subalgebra (entire algebra)
        let mut one_vec = Vec::with_capacity(alg_size as usize);
        for i in 0..alg_size {
            one_vec.push(i);
        }
        let one_subalg = BasicSet::new(one_vec)?;
        
        // Create zero subalgebra (generated by constants)
        let mut constants = Vec::new();
        for op in &operations {
            if op.arity() == 0 {
                match op.int_value_at(&[]) {
                    Ok(val) => constants.push(val),
                    Err(e) => return Err(format!("Error evaluating constant operation: {}", e)),
                }
            }
        }
        
        // Generate zero subalgebra: empty if no constants, otherwise closure of constants
        let zero_subalg = if constants.is_empty() {
            BasicSet::new(vec![])?
        } else {
            // Sort and remove duplicates
            constants.sort();
            let constants = Self::no_duplicates(constants);
            // Generate the closure of constants (they may not be closed under operations)
            // get_operations_ref() already returns Vec<&dyn Operation>
            Self::make_sg_static(&operations, alg_size, constants, 0)?
        };
        
        Ok(SubalgebraLattice {
            alg,
            alg_size,
            num_ops,
            zero_subalg,
            one_subalg,
            description: None,
            non_drawable: false,
            one_generated_subalg_lookup: None,
            one_generated_subalg_generator: None,
            universe: None,
            upper_covers_map: None,
            lower_cover_of_jis: None,
            one_generated_subalgebras: None,
            join_irreducibles: None,
            meet_irreducibles: None,
            jis_hash: None,
            size_computed: 0,
            jis_made: false,
            stop_make_universe: false,
            make_universe_k: 0,
        })
    }
    
    /// Create a new SubalgebraLattice (panicking version for compatibility).
    /// 
    /// # Arguments
    /// * `alg` - The underlying algebra
    /// 
    /// # Panics
    /// Panics if the algebra is invalid
    pub fn new(alg: Box<dyn SmallAlgebra<UniverseItem = T>>) -> Self {
        Self::new_safe(alg).unwrap()
    }
    
    /// Remove duplicates from a sorted list.
    /// 
    /// # Arguments
    /// * `lst` - A sorted vector
    /// 
    /// # Returns
    /// A vector without duplicates
    pub fn no_duplicates<U: PartialEq + Clone>(lst: Vec<U>) -> Vec<U> {
        if lst.is_empty() {
            return lst;
        }
        
        let mut nodups = Vec::with_capacity(lst.len());
        let mut previous = &lst[0];
        nodups.push(lst[0].clone());
        
        for item in lst.iter().skip(1) {
            if item != previous {
                nodups.push(item.clone());
                previous = item;
            }
        }
        
        nodups
    }
    
    /// Static helper to generate subuniverse closure (used in constructor).
    /// 
    /// This extracts the closure logic from make_sg_with_max_size so it can be
    /// called from the constructor before self exists.
    /// 
    /// # Arguments
    /// * `operations` - Reference to operations (as slice of references)
    /// * `alg_size` - Size of the algebra
    /// * `gens` - List of generators (no duplicates, contains all constants)
    /// * `closed_mark` - Index up to which elements are already closed
    /// 
    /// # Returns
    /// The generated subuniverse
    fn make_sg_static(
        operations: &[&dyn Operation],
        alg_size: i32,
        gens: Vec<i32>,
        mut closed_mark: usize
    ) -> Result<BasicSet, String> {
        let max_size = (alg_size - 1) as usize;
        let mut current_mark = gens.len();
        let mut su: HashSet<i32> = gens.iter().cloned().collect();
        let mut lst = gens;
        
        // Create one subalgebra (entire algebra) for fallback
        let mut one_vec = Vec::with_capacity(alg_size as usize);
        for i in 0..alg_size {
            one_vec.push(i);
        }
        let one_subalg = BasicSet::new(one_vec)?;
        
        while closed_mark < current_mark {
            // Close the elements in current
            for op in operations {
                let arity = op.arity();
                if arity == 0 {
                    continue; // Constants are already there
                }
                let arity_usize = arity as usize;
                
                // Create argument indices
                let mut arg_indices = vec![0_i32; arity_usize];
                for i in 0..(arity - 1) {
                    arg_indices[i as usize] = 0;
                }
                arg_indices[(arity - 1) as usize] = closed_mark as i32;
                
                // Create incrementor for nondecreasing sequences
                let mut inc = SequenceGenerator::nondecreasing_sequence_incrementor(
                    &mut arg_indices,
                    (current_mark - 1) as i32
                );
                
                let mut arg = vec![0_i32; arity_usize];
                loop {
                    // Build argument from indices using get_current() to avoid borrow issues
                    let arg_indices_copy = inc.get_current();
                    for i in 0..arity {
                        arg[i as usize] = lst[arg_indices_copy[i as usize] as usize];
                    }
                    // Apply operation once for this argument (pilot: skip permutations)
                    match op.int_value_at(&arg) {
                        Ok(v) => {
                            if su.insert(v) {
                                lst.push(v);
                                if lst.len() > max_size {
                                    return Ok(one_subalg);
                                }
                            }
                        }
                        Err(_) => {
                            // Ignore errors for partial operations
                        }
                    }
                    // Increment sequence (clone to avoid borrow)
                    if !inc.increment() {
                        break;
                    }
                }
            }
            
            closed_mark = current_mark;
            current_mark = lst.len();
        }
        
        // Sort and create BasicSet
        lst.sort();
        BasicSet::new(lst).map_err(|e| format!("Failed to create BasicSet: {}", e))
    }
    
    /// Get the underlying algebra.
    /// 
    /// # Returns
    /// A reference to the algebra
    pub fn get_algebra(&self) -> &dyn SmallAlgebra<UniverseItem = T> {
        self.alg.as_ref()
    }
    
    /// Get the description of this subalgebra lattice.
    /// 
    /// # Returns
    /// The description, or a default description if none is set
    pub fn get_description(&self) -> String {
        self.description.clone().unwrap_or_else(|| {
            format!("Subalgebra Lattice of {}", self.alg.name())
        })
    }
    
    /// Set the description of this subalgebra lattice.
    /// 
    /// # Arguments
    /// * `desc` - The new description
    pub fn set_description(&mut self, desc: String) {
        self.description = Some(desc);
    }
    
    /// Check if the lattice is drawable (size <= MAX_DRAWABLE_SIZE).
    /// 
    /// # Returns
    /// `true` if the lattice is drawable
    pub fn is_drawable(&self) -> bool {
        if let Some(ref univ) = self.universe {
            return univ.len() <= MAX_DRAWABLE_SIZE;
        }
        if self.size_computed > 0 {
            return false;
        }
        self.is_smaller_than(MAX_DRAWABLE_SIZE + 1)
    }
    
    /// Check if the lattice has fewer than `size` elements.
    /// 
    /// # Arguments
    /// * `size` - The size to compare against
    /// 
    /// # Returns
    /// `true` if the lattice has fewer than `size` elements
    pub fn is_smaller_than(&self, size: usize) -> bool {
        if let Some(ref univ) = self.universe {
            return univ.len() < size;
        }
        if let Some(ref jis) = self.join_irreducibles {
            if jis.len() >= size {
                return false;
            }
        }
        // Would need to call makeUniverse(size), but that modifies self
        // For now, return false conservatively
        false
    }
    
    /// Get the zero subalgebra (generated by constants).
    /// 
    /// # Returns
    /// The zero subalgebra
    pub fn zero(&self) -> &BasicSet {
        &self.zero_subalg
    }
    
    /// Get the one subalgebra (entire algebra).
    /// 
    /// # Returns
    /// The one subalgebra
    pub fn one(&self) -> &BasicSet {
        &self.one_subalg
    }
    
    /// Get the size computed so far.
    /// 
    /// # Returns
    /// The number of subalgebras computed
    pub fn get_size_computed(&self) -> i32 {
        self.size_computed
    }
    
    /// Get the current k value in universe computation.
    /// 
    /// # Returns
    /// The current k value
    pub fn get_make_universe_k(&self) -> i32 {
        self.make_universe_k
    }
    
    /// Stop the universe computation.
    pub fn stop_make_universe(&mut self) {
        self.stop_make_universe = true;
    }
    
    /// Check if the universe has been found.
    /// 
    /// # Returns
    /// `true` if the universe has been computed
    pub fn universe_found(&self) -> bool {
        self.universe.is_some()
    }
    
    /// Generate the subalgebra generated by a set of generators.
    /// 
    /// # Arguments
    /// * `gens` - Array of generator indices
    /// 
    /// # Returns
    /// The subalgebra generated by the generators
    ///
    /// # Examples
    /// ```
    /// use uacalc::alg::sublat::SubalgebraLattice;
    /// use uacalc::alg::{SmallAlgebra, BasicAlgebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "TestAlg".to_string(),
    ///     HashSet::from([0, 1, 2]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let sub_lat = SubalgebraLattice::new_safe(alg).unwrap();
    /// let sub = sub_lat.sg(&[0, 1]);
    /// ```
    pub fn sg(&self, gens: &[i32]) -> BasicSet {
        if gens.is_empty() {
            return self.zero_subalg.clone();
        }
        
        // Handle case where generators are empty after removing constants
        if gens.is_empty() && self.zero_subalg.size() == 0 {
            return BasicSet::new(vec![]).unwrap_or_else(|_| self.zero_subalg.clone());
        }
        
        let mut gens_list = Vec::with_capacity(gens.len() + self.zero_subalg.size());
        
        // Add all constants from zero subalgebra
        for i in 0..self.zero_subalg.universe_size() {
            if let Some(elem) = self.zero_subalg.get(i) {
                gens_list.push(elem);
            }
        }
        
        // Add generators
        for &gen in gens {
            gens_list.push(gen);
        }
        
        // Sort and remove duplicates
        gens_list.sort();
        let gens_list = Self::no_duplicates(gens_list);
        
        self.make_sg(gens_list, 0)
    }
    
    /// Create a Subalgebra wrapper object.
    /// 
    /// # Arguments
    /// * `s` - The subalgebra as a BasicSet
    /// 
    /// # Returns
    /// A Subalgebra object
    pub fn sg_subalgebra(&self, s: &BasicSet) -> Subalgebra<T> {
        Subalgebra::new(
            format!("Subalgebra Of {}", self.alg.name()),
            self.alg.clone_box(),
            s.elements().clone()
        )
    }
    
    /// Create a Subalgebra from generators.
    /// 
    /// # Arguments
    /// * `gens` - Array of generator indices
    /// 
    /// # Returns
    /// A Subalgebra object
    pub fn sg_from_gens(&self, gens: &[i32]) -> Subalgebra<T> {
        let basic_set = self.sg(gens);
        self.sg_subalgebra(&basic_set)
    }
    
    /// Make the subuniverse generated by a list of integers without duplicates.
    /// 
    /// # Arguments
    /// * `gens` - List of generators (no duplicates, contains all constants)
    /// 
    /// # Returns
    /// The generated subuniverse
    pub fn make_sg(&self, gens: Vec<i32>, closed_mark: usize) -> BasicSet {
        self.make_sg_with_max_size(gens, closed_mark, (self.alg_size - 1) as usize)
    }
    
    /// Make the subuniverse generated by a list of integers without duplicates,
    /// up to a maximum size.
    /// 
    /// # Arguments
    /// * `gens` - List of generators (no duplicates, contains all constants)
    /// * `closed_mark` - Index up to which elements are already closed
    /// * `max_size` - Return the whole algebra if we exceed this
    /// 
    /// # Returns
    /// The generated subuniverse
    pub fn make_sg_with_max_size(
        &self,
        gens: Vec<i32>,
        mut closed_mark: usize,
        max_size: usize
    ) -> BasicSet {
        let mut current_mark = gens.len();
        let mut su: HashSet<i32> = gens.iter().cloned().collect();
        let mut lst = gens;
        
        let operations = self.alg.get_operations_ref();
        
        while closed_mark < current_mark {
            // Close the elements in current
            for op in &operations {
                let arity = op.arity();
                if arity == 0 {
                    continue; // Constants are already there
                }
                let arity_usize = arity as usize;
                
                // Create argument indices
                let mut arg_indices = vec![0_i32; arity_usize];
                for i in 0..(arity - 1) {
                    arg_indices[i as usize] = 0;
                }
                arg_indices[(arity - 1) as usize] = closed_mark as i32;
                
                // Create incrementor for nondecreasing sequences
                let mut inc = SequenceGenerator::nondecreasing_sequence_incrementor(
                    &mut arg_indices,
                    (current_mark - 1) as i32
                );
                
                let mut arg = vec![0_i32; arity_usize];
                loop {
                    // Build argument from indices using get_current() to avoid borrow issues
                    let arg_indices_copy = inc.get_current();
                    for i in 0..arity {
                        arg[i as usize] = lst[arg_indices_copy[i as usize] as usize];
                    }
                    // Apply operation once for this argument (pilot: skip permutations)
                    match op.int_value_at(&arg) {
                        Ok(v) => {
                            if su.insert(v) {
                                lst.push(v);
                                if lst.len() > max_size {
                                    return self.one().clone();
                                }
                            }
                        }
                        Err(_) => {
                            // Ignore errors for partial operations
                        }
                    }
                    // Increment sequence (clone to avoid borrow)
                    if !inc.increment() {
                        break;
                    }
                }
            }
            
            closed_mark = current_mark;
            current_mark = lst.len();
        }
        
        // Sort and create BasicSet
        lst.sort();
        BasicSet::new(lst).unwrap_or_else(|_| self.one().clone())
    }
    
    /// Get or compute one-generated subalgebras.
    /// 
    /// # Returns
    /// List of one-generated subalgebras
    pub fn one_generated_subalgebras(&mut self) -> &Vec<BasicSet> {
        if self.one_generated_subalgebras.is_none() {
            self.make_one_generated_subalgebras();
        }
        self.one_generated_subalgebras.as_ref().unwrap()
    }
    
    /// Compute all one-generated subalgebras.
    fn make_one_generated_subalgebras(&mut self) {
        let mut one_generated = Vec::new();
        let mut generator_map = HashMap::new();
        let mut lookup_map = HashMap::new();
        let mut one_gens: HashMap<BasicSet, BasicSet> = HashMap::new();
        
        for i in 0..self.alg_size {
            let sub = self.sg(&[i]);
            
            if !one_gens.contains_key(&sub) {
                one_gens.insert(sub.clone(), sub.clone());
                one_generated.push(sub.clone());
                generator_map.insert(sub.clone(), i);
            }
            
            let canonical_sub = one_gens.get(&sub).unwrap().clone();
            lookup_map.insert(i, canonical_sub);
        }
        
        one_generated.sort();
        
        self.one_generated_subalgebras = Some(one_generated);
        self.one_generated_subalg_generator = Some(generator_map);
        self.one_generated_subalg_lookup = Some(lookup_map);
    }
    
    /// Get or compute join irreducibles (mutable version).
    /// 
    /// # Returns
    /// Reference to list of join irreducible elements
    pub fn join_irreducibles_mut(&mut self) -> &Vec<BasicSet> {
        if self.join_irreducibles.is_none() {
            self.make_join_irreducibles();
        }
        self.join_irreducibles.as_ref().unwrap()
    }
    
    /// Check if a subalgebra is join irreducible.
    /// 
    /// # Arguments
    /// * `subalg` - The subalgebra to check
    /// 
    /// # Returns
    /// `true` if the subalgebra is join irreducible
    pub fn join_irreducible(&mut self, subalg: &BasicSet) -> bool {
        // Make sure join irreducibles have been computed
        self.join_irreducibles_mut();
        
        if let Some(ref jis) = self.jis_hash {
            jis.contains(subalg)
        } else {
            false
        }
    }
    
    /// Compute join irreducible elements.
    fn make_join_irreducibles(&mut self) {
        let mut jis_hash = HashSet::new();
        let mut lower_cover_map = HashMap::new();
        let mut jis = Vec::new();
        
        // Get one-generated subalgebras (sorted by size)
        let ones = self.one_generated_subalgebras().clone();
        
        for i in 0..ones.len() {
            let set = &ones[i];
            let mut lower = BasicSet::new(vec![]).unwrap();
            
            for j in (0..i).rev() {
                let set2 = &ones[j];
                if set.universe_size() == set2.universe_size() {
                    continue;
                }
                if set2.leq(set) && !set2.leq(&lower) {
                    if lower.size() == 0 {
                        lower = set2.clone();
                    } else {
                        // Join lower and set2
                        let mark = lower.universe_size();
                        let mut u = Vec::with_capacity(mark + set2.universe_size());
                        for k in 0..mark {
                            if let Some(elem) = lower.get(k) {
                                u.push(elem);
                            }
                        }
                        let diff = set2.set_difference(&lower);
                        for k in 0..diff.universe_size() {
                            if let Some(elem) = diff.get(k) {
                                u.push(elem);
                            }
                        }
                        lower = self.make_sg(u, mark);
                    }
                }
                if lower == *set {
                    break;
                }
            }
            
            if lower != *set {
                jis_hash.insert(set.clone());
                jis.push(set.clone());
                lower_cover_map.insert(set.clone(), lower);
            }
        }
        
        jis.sort();
        
        self.join_irreducibles = Some(jis);
        self.jis_hash = Some(jis_hash);
        self.lower_cover_of_jis = Some(lower_cover_map);
        self.jis_made = true;
    }
    
    /// Get or compute meet irreducibles (mutable version).
    /// 
    /// # Returns
    /// Reference to list of meet irreducible elements
    pub fn meet_irreducibles_mut(&mut self) -> &Vec<BasicSet> {
        if self.meet_irreducibles.is_none() {
            self.make_meet_irreducibles();
        }
        self.meet_irreducibles.as_ref().unwrap()
    }
    
    /// Compute meet irreducible elements.
    fn make_meet_irreducibles(&mut self) {
        // TODO: Implement meet irreducibles computation
        // For now, return empty list
        self.meet_irreducibles = Some(Vec::new());
    }
    
    /// Get the join irreducible subalgebras as an OrderedSet.
    ///
    /// # Returns
    /// An OrderedSet containing the join irreducible elements with their order relations
    pub fn join_irreducibles_po(&mut self) -> Result<crate::lat::ordered_set::OrderedSet<BasicSet>, String> {
        let jis = self.join_irreducibles_mut().clone();
        self.make_ordered_set_from_subset(&jis, "JoinIrreducibles".to_string())
    }
    
    /// Get the meet irreducible subalgebras as an OrderedSet.
    ///
    /// # Returns
    /// An OrderedSet containing the meet irreducible elements with their order relations
    pub fn meet_irreducibles_po(&mut self) -> Result<crate::lat::ordered_set::OrderedSet<BasicSet>, String> {
        let mis = self.meet_irreducibles_mut().clone();
        self.make_ordered_set_from_subset(&mis, "MeetIrreducibles".to_string())
    }
    
    /// Create an OrderedSet from a subset of BasicSets with their order relations.
    fn make_ordered_set_from_subset(
        &self,
        subset: &[BasicSet],
        name: String,
    ) -> Result<crate::lat::ordered_set::OrderedSet<BasicSet>, String> {
        use crate::lat::ordered_set::OrderedSet;
        use crate::lat::Order;
        
        let mut upper_covers_list: Vec<Vec<BasicSet>> = Vec::new();
        
        for elem1 in subset {
            let mut covers = Vec::new();
            
            // Find all elements that are greater than elem1
            let mut greater_than: Vec<&BasicSet> = subset.iter()
                .filter(|elem2| elem1 != *elem2 && Order::leq(self, elem1, elem2))
                .collect();
            
            // Find minimal elements among those greater than elem1
            // An element is a cover if it's minimal among the greater elements
            for candidate in &greater_than {
                let mut is_minimal = true;
                for other in &greater_than {
                    if candidate != other && Order::leq(self, other, candidate) {
                        is_minimal = false;
                        break;
                    }
                }
                if is_minimal {
                    covers.push((*candidate).clone());
                }
            }
            
            upper_covers_list.push(covers);
        }
        
        OrderedSet::new(Some(name), subset.to_vec(), upper_covers_list)
    }
    
    /// Compute the join of two subalgebras.
    /// 
    /// # Arguments
    /// * `a` - First subalgebra
    /// * `b` - Second subalgebra
    /// 
    /// # Returns
    /// The join (smallest subalgebra containing both)
    pub fn join_sets(&self, a: &BasicSet, b: &BasicSet) -> BasicSet {
        let (mut seta, mut setb) = if b.universe_size() > a.universe_size() {
            (b.clone(), a.clone())
        } else {
            (a.clone(), b.clone())
        };
        
        let foo = setb.set_difference(&seta);
        let closed_mark = seta.universe_size();
        
        let mut lst = Vec::with_capacity(closed_mark + foo.universe_size());
        for i in 0..closed_mark {
            if let Some(elem) = seta.get(i) {
                lst.push(elem);
            }
        }
        for i in 0..foo.universe_size() {
            if let Some(elem) = foo.get(i) {
                lst.push(elem);
            }
        }
        
        self.make_sg(lst, closed_mark)
    }
    
    /// Get the universe of all subalgebras.
    /// 
    /// # Returns
    /// The set of all subalgebras
    pub fn universe_mut(&mut self) -> &HashSet<BasicSet> {
        if self.universe.is_none() {
            self.make_universe_default();
        }
        self.universe.as_ref().unwrap()
    }
    
    /// Make the universe with default parameters.
    fn make_universe_default(&mut self) {
        self.make_universe(-1);
    }
    
    /// Construct the universe of all subalgebras.
    /// 
    /// # Arguments
    /// * `max_size` - Maximum size (-1 for no limit)
    pub fn make_universe(&mut self, max_size: i32) {
        let jis = self.join_irreducibles_mut().clone();
        self.size_computed = jis.len() as i32;
        
        let universe = if max_size > 0 {
            self.join_closure(&jis, max_size as usize)
        } else {
            self.join_closure_unlimited(&jis)
        };
        
        if let Some(mut univ) = universe {
            univ.insert(self.zero_subalg.clone());
            self.universe = Some(univ);
        }
    }
    
    /// Compute the join closure of a collection of elements.
    /// 
    /// # Arguments
    /// * `gens` - Generators
    /// 
    /// # Returns
    /// The join closure
    pub fn join_closure_unlimited(&self, gens: &[BasicSet]) -> Option<HashSet<BasicSet>> {
        self.join_closure(gens, usize::MAX)
    }
    
    /// Compute the join closure of a collection of elements.
    /// 
    /// # Arguments
    /// * `gens` - Generators
    /// * `max_size` - Maximum size
    /// 
    /// # Returns
    /// The join closure (None if exceeded max_size)
    pub fn join_closure(&self, gens: &[BasicSet], max_size: usize) -> Option<HashSet<BasicSet>> {
        let stop_if_big = max_size != usize::MAX;
        let mut ans: HashSet<BasicSet> = gens.iter().cloned().collect();
        let mut ans_list: Vec<BasicSet> = gens.to_vec();
        
        let g = gens.len();
        for (k, s) in gens.iter().enumerate() {
            let n = ans_list.len();
            for i in 0..n {
                let join = self.join_sets(s, &ans_list[i]);
                if !ans.contains(&join) {
                    ans.insert(join.clone());
                    ans_list.push(join);
                    if stop_if_big && ans_list.len() >= max_size {
                        return None;
                    }
                }
            }
        }
        
        Some(ans)
    }
    
    /// Filter elements containing a given subalgebra.
    /// 
    /// # Arguments
    /// * `elt` - The subalgebra to filter by
    /// 
    /// # Returns
    /// Set of all subalgebras containing `elt`
    pub fn filter(&mut self, elt: &BasicSet) -> HashSet<BasicSet> {
        let mut ans = HashSet::new();
        
        if self.universe_found() {
            if let Some(ref univ) = self.universe {
                for elt2 in univ {
                    if elt.leq(elt2) {
                        ans.insert(elt2.clone());
                    }
                }
                return ans;
            }
        }
        
        // If universe not found, use one-generated subalgebras
        let one_gens = self.one_generated_subalgebras().clone();
        for elt2 in &one_gens {
            ans.insert(self.join_sets(elt, elt2));
        }
        
        // Compute join closure
        if let Some(closure) = self.join_closure_unlimited(&ans.iter().cloned().collect::<Vec<_>>()) {
            ans = closure;
        }
        
        ans.insert(elt.clone());
        ans
    }
    
    /// Find a minimal sized generating set for the algebra.
    /// 
    /// # Returns
    /// A minimal generating set
    pub fn find_minimal_sized_generating_set(&mut self) -> BasicSet {
        if self.alg_size == 1 {
            return BasicSet::new(vec![]).unwrap();
        }
        
        let _ = self.one_generated_subalgebras();
        
        // Check if there's a single generator
        if let Some(ref gen_map) = self.one_generated_subalg_generator {
            if let Some(&g) = gen_map.get(self.one()) {
                return BasicSet::new(vec![g]).unwrap();
            }
        }
        
        // Try generating sets of increasing size
        for i in 2..=self.alg_size as usize {
            let mut arr = (0..i as i32).collect::<Vec<_>>();
            let mut inc = SequenceGenerator::increasing_sequence_incrementor(
                &mut arr,
                self.alg_size - 1
            );
            
            loop {
                // Use get_current() to check condition without borrowing issues
                {
                    let arr_copy = inc.get_current();
                    let sub = self.sg(&arr_copy);
                    if sub.universe_size() == self.alg_size as usize {
                        return BasicSet::new(arr_copy).unwrap();
                    }
                }
                if !inc.increment() {
                    break;
                }
            }
        }
        
        // Should not reach here
        self.one().clone()
    }
    
    /// Try to extend a map to a homomorphism between two algebras.
    /// 
    /// # Arguments
    /// * `gens` - Generators in source algebra
    /// * `gens_b` - Images in target algebra
    /// * `a` - Source algebra
    /// * `b` - Target algebra
    /// 
    /// # Returns
    /// * `Some(map)` - The homomorphism as a map
    /// * `None` - If no homomorphism exists
    pub fn extend_to_homomorphism(
        gens: &[i32],
        gens_b: &[i32],
        a: &dyn SmallAlgebra<UniverseItem = T>,
        b: &dyn SmallAlgebra<UniverseItem = T>
    ) -> Option<HashMap<i32, i32>> {
        if gens.len() != gens_b.len() {
            return None;
        }
        
        let mut homo = HashMap::new();
        for i in 0..gens.len() {
            if let Some(&existing) = homo.get(&gens[i]) {
                if existing != gens_b[i] {
                    return None;
                }
            }
            homo.insert(gens[i], gens_b[i]);
        }
        
        // Add constants
        if !Self::add_constants_to_map(&mut homo, a, b) {
            return None;
        }
        
        if homo.is_empty() {
            return Some(homo);
        }
        
        Self::extend_to_homomorphism_from_map(homo, a, b)
    }
    
    /// Add constants from algebra to the homomorphism map.
    fn add_constants_to_map(
        homo: &mut HashMap<i32, i32>,
        a: &dyn SmallAlgebra<UniverseItem = T>,
        b: &dyn SmallAlgebra<UniverseItem = T>
    ) -> bool {
        let empty_args: &[i32] = &[];
        
        for op_a in a.get_operations_ref() {
            if op_a.arity() == 0 {
                if let Ok(f_value) = op_a.int_value_at(empty_args) {
                    if let Some(op_b) = b.get_operation_ref(op_a.symbol()) {
                        if let Ok(g_value) = op_b.int_value_at(empty_args) {
                            if let Some(&existing) = homo.get(&f_value) {
                                if existing != g_value {
                                    return false;
                                }
                            } else {
                                homo.insert(f_value, g_value);
                            }
                        }
                    }
                }
            }
        }
        
        true
    }
    
    /// Extend a partial map to a homomorphism.
    fn extend_to_homomorphism_from_map(
        mut homo: HashMap<i32, i32>,
        a: &dyn SmallAlgebra<UniverseItem = T>,
        b: &dyn SmallAlgebra<UniverseItem = T>
    ) -> Option<HashMap<i32, i32>> {
        let mut lst: Vec<i32> = homo.keys().cloned().collect();
        lst.sort();
        
        let mut closed_mark = 0;
        let mut current_mark = lst.len();
        
        while closed_mark < current_mark {
            for op_a in a.get_operations_ref() {
                let arity = op_a.arity();
                if arity == 0 {
                    continue;
                }
                
                if let Some(op_b) = b.get_operation_ref(op_a.symbol()) {
                    let arity_usize = arity as usize;
                    let mut arg_indices = vec![0_i32; arity_usize];
                    for i in 0..(arity - 1) {
                        arg_indices[i as usize] = 0;
                    }
                    arg_indices[(arity - 1) as usize] = closed_mark as i32;
                    
                    let mut inc = SequenceGenerator::sequence_incrementor(
                        &mut arg_indices,
                        (current_mark - 1) as i32
                    );
                    
                    let mut arg = vec![0_i32; arity_usize];
                    let mut arg_b = vec![0_i32; arity_usize];
                    
                    loop {
                        // Use get_current() to avoid borrow issues
                        let arg_indices_copy = inc.get_current();
                        for i in 0..arity {
                            let idx = arg_indices_copy[i as usize] as usize;
                            arg[i as usize] = lst[idx];
                            arg_b[i as usize] = *homo.get(&lst[idx]).unwrap();
                        }
                        
                        if let (Ok(v), Ok(w)) = (op_a.int_value_at(&arg), op_b.int_value_at(&arg_b)) {
                            if let Some(&existing) = homo.get(&v) {
                                if existing != w {
                                    return None;
                                }
                            } else {
                                lst.push(v);
                                homo.insert(v, w);
                            }
                        }
                        
                        if !inc.increment() {
                            break;
                        }
                    }
                }
            }
            
            closed_mark = current_mark;
            current_mark = lst.len();
        }
        
        Some(homo)
    }
    
    /// Try to extend a map to a homomorphism between two algebras using generic element types.
    /// 
    /// This method converts elements to indices internally and then uses the existing
    /// index-based homomorphism algorithm.
    /// 
    /// # Arguments
    /// * `gens` - Generators in source algebra
    /// * `gens_b` - Images in target algebra
    /// * `a` - Source algebra
    /// * `b` - Target algebra
    /// 
    /// # Returns
    /// * `Some(map)` - The homomorphism as a map from source elements to target elements
    /// * `None` - If no homomorphism exists
    pub fn extend_to_homomorphism_generic(
        gens: &[T],
        gens_b: &[T],
        a: &dyn SmallAlgebra<UniverseItem = T>,
        b: &dyn SmallAlgebra<UniverseItem = T>
    ) -> Option<HashMap<T, T>> {
        if gens.len() != gens_b.len() {
            return None;
        }
        
        // Convert elements to indices
        let mut gens_indices = Vec::new();
        let mut gens_b_indices = Vec::new();
        
        for (gen, gen_b) in gens.iter().zip(gens_b.iter()) {
            let gen_idx = a.element_index(gen)?;
            let gen_b_idx = b.element_index(gen_b)?;
            gens_indices.push(gen_idx as i32);
            gens_b_indices.push(gen_b_idx as i32);
        }
        
        // Use the existing index-based method
        let homo_indices = Self::extend_to_homomorphism(&gens_indices, &gens_b_indices, a, b)?;
        
        // Convert back to element-based map
        let mut homo_elements = HashMap::new();
        for (idx, target_idx) in homo_indices {
            if let (Some(source_elem), Some(target_elem)) = (a.get_element(idx as usize), b.get_element(target_idx as usize)) {
                homo_elements.insert(source_elem, target_elem);
            } else {
                return None;
            }
        }
        
        Some(homo_elements)
    }
}

// Implement Order trait
impl<T> Order<BasicSet> for SubalgebraLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn leq(&self, a: &BasicSet, b: &BasicSet) -> bool {
        a.leq(b)
    }
}

// Implement Lattice trait
impl<T> Lattice<BasicSet> for SubalgebraLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn join_irreducibles(&self) -> Option<Vec<BasicSet>> {
        if let Some(ref jis) = self.join_irreducibles {
            Some(jis.clone())
        } else {
            None
        }
    }
    
    fn meet_irreducibles(&self) -> Option<Vec<BasicSet>> {
        if let Some(ref mis) = self.meet_irreducibles {
            Some(mis.clone())
        } else {
            None
        }
    }
    
    fn atoms(&self) -> Option<Vec<BasicSet>> {
        // TODO: Implement atoms computation
        None
    }
    
    fn coatoms(&self) -> Option<Vec<BasicSet>> {
        // TODO: Implement coatoms computation
        None
    }
    
    fn join(&self, a: &BasicSet, b: &BasicSet) -> BasicSet {
        self.join_sets(a, b)
    }
    
    fn join_list(&self, args: &[BasicSet]) -> BasicSet {
        if args.is_empty() {
            return self.zero_subalg.clone();
        }
        
        let mut result = args[0].clone();
        for i in 1..args.len() {
            result = self.join_sets(&result, &args[i]);
        }
        result
    }
    
    fn meet(&self, a: &BasicSet, b: &BasicSet) -> BasicSet {
        // Meet is intersection for subalgebras
        a.intersection(b)
    }
    
    fn meet_list(&self, args: &[BasicSet]) -> BasicSet {
        if args.is_empty() {
            return self.one_subalg.clone();
        }
        
        let mut result = args[0].clone();
        for i in 1..args.len() {
            result = result.intersection(&args[i]);
        }
        result
    }
}

// Implement Algebra trait
impl<T> Algebra for SubalgebraLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    type UniverseItem = BasicSet;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        if let Some(ref univ) = self.universe {
            Box::new(univ.clone().into_iter())
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
        // Return join and meet operations
        Vec::new()
    }
    
    fn get_operation(&self, sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        None
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        HashMap::new()
    }
    
    fn name(&self) -> &str {
        "SubalgebraLattice"
    }
    
    fn set_name(&mut self, _name: String) {
        // SubalgebraLattice doesn't support setting name
    }
    
    fn description(&self) -> Option<&str> {
        self.description.as_deref()
    }
    
    fn set_description(&mut self, desc: Option<String>) {
        self.description = desc;
    }
    
    fn similarity_type(&self) -> &SimilarityType {
        // Create a lattice similarity type with join and meet operations
        static LATTICE_TYPE: once_cell::sync::Lazy<SimilarityType> = once_cell::sync::Lazy::new(|| {
            SimilarityType::new(vec![
                OperationSymbol::new("join", 2, false),
                OperationSymbol::new("meet", 2, false),
            ])
        });
        &LATTICE_TYPE
    }
    
    fn update_similarity_type(&mut self) {
        // Lattice similarity type is fixed
    }
    
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        other.similarity_type() == self.similarity_type()
    }
    
    fn make_operation_tables(&mut self) {
        // Not applicable for lattices
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
    
    fn get_monitor(&self) -> Option<&dyn ProgressMonitor> {
        None
    }
    
    fn set_monitor(&mut self, _monitor: Option<Box<dyn ProgressMonitor>>) {
        // Not implemented
    }
}

impl<T> fmt::Display for SubalgebraLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "SubalgebraLattice({})", self.alg.name())
    }
}

impl<T> fmt::Debug for SubalgebraLattice<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("SubalgebraLattice")
            .field("alg", &self.alg.name())
            .field("alg_size", &self.alg_size)
            .field("num_ops", &self.num_ops)
            .finish()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;

    #[test]
    fn test_basic_set_creation() {
        let set = BasicSet::new(vec![1, 3, 5]).unwrap();
        assert_eq!(set.elements(), &[1, 3, 5]);
        assert_eq!(set.size(), 3);
    }

    #[test]
    fn test_basic_set_empty() {
        let set = BasicSet::new(vec![]).unwrap();
        assert_eq!(set.elements(), &[] as &[i32]);
        assert_eq!(set.size(), 0);
    }

    #[test]
    fn test_basic_set_duplicates() {
        let set = BasicSet::new(vec![1, 3, 1, 5, 3]).unwrap();
        // Should be normalized (sorted and deduplicated)
        assert_eq!(set.elements(), &[1, 3, 5]);
        assert_eq!(set.size(), 3);
    }

    #[test]
    fn test_basic_set_contains() {
        let set = BasicSet::new(vec![1, 3, 5]).unwrap();
        assert!(set.contains(3));
        assert!(!set.contains(2));
    }

    #[test]
    fn test_basic_set_leq() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![1, 2, 3, 4, 5]).unwrap();
        assert!(set1.leq(&set2));
        assert!(!set2.leq(&set1));
    }

    #[test]
    fn test_basic_set_leq_static() {
        assert!(BasicSet::leq_static(&[1, 3], &[1, 2, 3, 4]));
        assert!(!BasicSet::leq_static(&[1, 2, 3, 4], &[1, 3]));
    }

    #[test]
    fn test_basic_set_intersection() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
        let intersection = set1.intersection(&set2);
        assert_eq!(intersection.elements(), &[3]);
    }

    #[test]
    fn test_basic_set_intersection_static() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
        let intersection = BasicSet::intersection_static(&set1, &set2);
        assert_eq!(intersection.elements(), &[3]);
    }

    #[test]
    fn test_basic_set_union() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
        let union = set1.union(&set2);
        assert_eq!(sorted(union.elements().clone()), vec![1, 2, 3, 4, 5]);
    }

    #[test]
    fn test_basic_set_union_static() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
        let union = BasicSet::union_static(&set1, &set2);
        assert_eq!(sorted(union.elements().clone()), vec![1, 2, 3, 4, 5]);
    }

    #[test]
    fn test_basic_set_difference() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![2, 3, 4]).unwrap();
        let difference = set1.set_difference(&set2);
        assert_eq!(sorted(difference.elements().clone()), vec![1, 5]);
    }

    #[test]
    fn test_basic_set_normalize() {
        let mut set = BasicSet::new(vec![3, 1, 5, 1, 3]).unwrap();
        set.normalize();
        assert_eq!(set.elements(), &[1, 3, 5]);
    }

    #[test]
    fn test_basic_set_size() {
        let set = BasicSet::new(vec![1, 3, 5]).unwrap();
        assert_eq!(set.size(), 3);
    }

    #[test]
    fn test_basic_set_universe_size() {
        let set = BasicSet::new(vec![1, 3, 5]).unwrap();
        assert_eq!(set.universe_size(), 3);
    }

    #[test]
    fn test_basic_set_elements() {
        let set = BasicSet::new(vec![1, 3, 5]).unwrap();
        assert_eq!(set.elements(), &[1, 3, 5]);
    }

    #[test]
    fn test_basic_set_comparison() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set3 = BasicSet::new(vec![1, 3, 6]).unwrap();
        
        assert_eq!(set1, set2);
        assert_ne!(set1, set3);
        assert!(set1 <= set2);
        assert!(set1 >= set2);
        assert!(set1 < set3);
    }

    #[test]
    fn test_basic_set_hash() {
        let set1 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set2 = BasicSet::new(vec![1, 3, 5]).unwrap();
        let set3 = BasicSet::new(vec![1, 3, 6]).unwrap();
        
        let mut hash_set = HashSet::new();
        hash_set.insert(set1.clone());
        hash_set.insert(set2.clone());
        hash_set.insert(set3.clone());
        
        // set1 and set2 should be the same, so only 2 unique items
        assert_eq!(hash_set.len(), 2);
    }

    #[test]
    fn test_basic_set_display() {
        let set = BasicSet::new(vec![1, 3, 5]).unwrap();
        let display_str = format!("{}", set);
        assert_eq!(display_str, "{1,3,5}");
    }

    #[test]
    fn test_basic_set_int_array_trait() {
        let mut set = BasicSet::new(vec![1, 3, 5]).unwrap();
        
        // Test IntArrayTrait implementation
        assert_eq!(set.universe_size(), 3);
        assert_eq!(set.get(0), Some(1));
        assert_eq!(set.get(1), Some(3));
        assert_eq!(set.get(2), Some(5));
        assert_eq!(set.get(3), None);
        
        // Test set method
        set.set(0, 2).unwrap();
        assert_eq!(set.get(0), Some(2));
        
        // Test as_slice
        let slice = set.as_slice();
        assert_eq!(slice, &[2, 3, 5]);
    }

    #[test]
    fn test_basic_set_constraints() {
        let set = BasicSet::new(vec![1, 2, 3]).unwrap();
        
        // Test values constraint
        let values = vec![(0, 1), (1, 2)];
        assert!(set.satisfies_values_constraint(&values));
        
        // Test set constraint
        let possible_values: HashSet<i32> = [1, 2, 3].iter().cloned().collect();
        assert!(set.satisfies_set_constraint(0, &possible_values));
        
        // Test constant check
        let constant_set = BasicSet::new(vec![1, 1, 1]).unwrap();
        assert!(constant_set.is_constant());
        assert!(!set.is_constant());
        
        // Test idempotent check
        let idempotent_set = BasicSet::new(vec![0, 1, 2]).unwrap();
        assert!(idempotent_set.is_idempotent());
        assert!(!set.is_idempotent());
    }

    fn sorted(mut vec: Vec<i32>) -> Vec<i32> {
        vec.sort();
        vec
    }
}
