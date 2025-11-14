/// A partial order relation on elements of type E.
/// 
/// This trait defines the "less than or equal to" relation (≤) for elements.
/// Implementations must satisfy the mathematical properties of a partial order:
/// 
/// - **Reflexivity**: `leq(a, a) == true` for all a
/// - **Antisymmetry**: if `leq(a, b) && leq(b, a)` then `a == b`
/// - **Transitivity**: if `leq(a, b) && leq(b, c)` then `leq(a, c)`
/// 
/// # Examples
/// 
/// ## Integer divisibility order
/// ```
/// use uacalc::lat::Order;
/// 
/// struct DivisibilityOrder;
/// 
/// impl Order<i32> for DivisibilityOrder {
///     fn leq(&self, a: &i32, b: &i32) -> bool {
///         if *a == 0 { return true; }  // 0 divides everything by convention
///         if *b == 0 { return *a == 0; }
///         b % a == 0
///     }
/// }
/// 
/// let order = DivisibilityOrder;
/// assert!(order.leq(&2, &6));   // 2 divides 6
/// assert!(!order.leq(&6, &2));  // 6 does not divide 2
/// assert!(order.leq(&3, &3));   // 3 divides itself (reflexivity)
/// ```
/// 
/// ## String prefix order
/// ```
/// use uacalc::lat::Order;
/// 
/// struct PrefixOrder;
/// 
/// impl Order<String> for PrefixOrder {
///     fn leq(&self, a: &String, b: &String) -> bool {
///         b.starts_with(a)
///     }
/// }
/// 
/// let order = PrefixOrder;
/// assert!(order.leq(&"ab".to_string(), &"abcd".to_string()));
/// assert!(!order.leq(&"abcd".to_string(), &"ab".to_string()));
/// ```
pub trait Order<E>: Send + Sync {
    /// Returns true if a ≤ b in this order relation.
    /// 
    /// # Arguments
    /// * `a` - The first element
    /// * `b` - The second element
    /// 
    /// # Returns
    /// `true` if a ≤ b according to this order relation, `false` otherwise
    fn leq(&self, a: &E, b: &E) -> bool;
}

// Import trait implementations from separate modules
pub mod lattice;
pub mod small_lattice;

pub use lattice::Lattice;
pub use small_lattice::{SmallLattice, DiamondLattice, BooleanLattice};

pub mod ordered_set;
pub mod graph_data;
pub mod basic_lattice;

pub use ordered_set::{OrderedSet, POElem, Edge};
pub use graph_data::{LatticeGraphData, GraphNode, GraphEdge};
pub use basic_lattice::BasicLattice;

/// Utility functions for creating and manipulating lattices.
/// 
/// This module provides factory methods for creating lattices from operations
/// and other lattice operations. It's a partial implementation that excludes
/// methods requiring CongruenceLattice and BasicLattice dependencies.
pub mod lattices {
    use crate::alg::op::Operation;
    use crate::lat::Order;
    
    /// Create a lattice from a meet operation using integers for labels.
    /// 
    /// This method constructs a lattice from a semilattice operation viewed as a meet.
    /// It creates filters for each element and uses them to construct the lattice structure.
    /// 
    /// # Arguments
    /// * `name` - Name for the lattice
    /// * `meet` - The meet operation
    /// 
    /// # Returns
    /// * `Ok(MeetLattice)` - Successfully created lattice
    /// * `Err(String)` - Error message if creation fails
    /// 
    /// # Examples
    /// ```
    /// use uacalc::lat::lattices::lattice_from_meet;
    /// use uacalc::alg::op::Operation;
    /// 
    /// // This would require a concrete Operation implementation
    /// // let lattice = lattice_from_meet("TestLattice", meet_op).unwrap();
    /// ```
    pub fn lattice_from_meet(name: String, meet: &dyn Operation) -> Result<MeetLattice, String> {
        let s = meet.get_set_size() as usize;
        let mut univ: Vec<i32> = (0..s as i32).collect();
        
        // Create filters for each element
        let mut filters: Vec<Vec<i32>> = Vec::new();
        for i in 0..s {
            let mut filter = Vec::new();
            for j in 0..s {
                match meet.int_value_at(&[i as i32, j as i32]) {
                    Ok(result) if result == i as i32 => filter.push(j as i32),
                    Ok(_) => {},
                    Err(e) => return Err(format!("Error evaluating meet operation: {}", e)),
                }
            }
            filters.push(filter);
        }
        
        // Check if we need to add a top element
        let mut max_count = 0;
        for filter in &filters {
            if filter.len() == 1 {
                max_count += 1;
                if max_count > 1 {
                    break;
                }
            }
        }
        
        if max_count > 1 {
            univ.push(-1);
            let top_filter = vec![-1];
            filters.push(top_filter);
            for filter in &mut filters {
                filter.push(-1);
            }
        }
        
        // Create a simple lattice implementation
        MeetLattice::new(name, univ, filters)
    }
    
    /// Create a lattice from a join operation using integers for labels.
    /// 
    /// This method constructs a lattice from a semilattice operation viewed as a join.
    /// It creates filters for each element and uses them to construct the lattice structure.
    /// 
    /// # Arguments
    /// * `name` - Name for the lattice
    /// * `join` - The join operation
    /// 
    /// # Returns
    /// * `Ok(JoinLattice)` - Successfully created lattice
    /// * `Err(String)` - Error message if creation fails
    pub fn lattice_from_join(name: String, join: &dyn Operation) -> Result<JoinLattice, String> {
        let s = join.get_set_size() as usize;
        let mut univ: Vec<i32> = (0..s as i32).collect();
        
        // Create filters for each element
        let mut filters: Vec<Vec<i32>> = Vec::new();
        for i in 0..s {
            let mut filter = Vec::new();
            for j in 0..s {
                match join.int_value_at(&[i as i32, j as i32]) {
                    Ok(result) if result == j as i32 => filter.push(j as i32),
                    Ok(_) => {},
                    Err(e) => return Err(format!("Error evaluating join operation: {}", e)),
                }
            }
            filters.push(filter);
        }
        
        // Check if we need to add a bottom element
        let mut has_zero = false;
        for filter in &filters {
            if filter.len() == s {
                has_zero = true;
                break;
            }
        }
        
        if !has_zero {
            univ.push(-1);
            let bot_filter = univ.clone();
            filters.push(bot_filter);
        }
        
        // Create a simple lattice implementation
        JoinLattice::new(name, univ, filters)
    }
    
    /// Create a lattice from a meet operation with custom universe.
    /// 
    /// This method constructs a lattice from a meet operation using a custom universe.
    /// 
    /// # Arguments
    /// * `name` - Name for the lattice
    /// * `univ` - Custom universe elements
    /// * `meet` - The meet operation
    /// 
    /// # Returns
    /// * `Ok(MeetLattice)` - Successfully created lattice
    /// * `Err(String)` - Error message if creation fails
    pub fn lattice_from_meet_with_universe(
        name: String, 
        univ: Vec<i32>, 
        meet: &dyn Operation
    ) -> Result<MeetLattice, String> {
        let s = univ.len();
        let mut universe = univ.clone();
        
        // Create filters for each element
        let mut filters: Vec<Vec<i32>> = Vec::new();
        for i in 0..s {
            let mut filter = Vec::new();
            for j in 0..s {
                let args = vec![universe[i], universe[j]];
                match meet.value_at(&args) {
                    Ok(result) if result == universe[i] => filter.push(universe[j]),
                    Ok(_) => {},
                    Err(e) => return Err(format!("Error evaluating meet operation: {}", e)),
                }
            }
            filters.push(filter);
        }
        
        // Check if we need to add a top element
        let mut max_count = 0;
        for filter in &filters {
            if filter.len() == 1 {
                max_count += 1;
                if max_count > 1 {
                    break;
                }
            }
        }
        
        if max_count > 1 {
            universe.push(-1); // Use -1 as top element
            let top_filter = vec![-1];
            filters.push(top_filter);
            for filter in &mut filters {
                filter.push(-1);
            }
        }
        
        // Create a simple lattice implementation
        MeetLattice::new(name, universe, filters)
    }
    
    /// Create a lattice from a join operation with custom universe.
    /// 
    /// This method constructs a lattice from a join operation using a custom universe.
    /// 
    /// # Arguments
    /// * `name` - Name for the lattice
    /// * `univ` - Custom universe elements
    /// * `join` - The join operation
    /// 
    /// # Returns
    /// * `Ok(JoinLattice)` - Successfully created lattice
    /// * `Err(String)` - Error message if creation fails
    pub fn lattice_from_join_with_universe(
        name: String, 
        univ: Vec<i32>, 
        join: &dyn Operation
    ) -> Result<JoinLattice, String> {
        let s = univ.len();
        let mut universe = univ.clone();
        
        // Create filters for each element
        let mut filters: Vec<Vec<i32>> = Vec::new();
        for i in 0..s {
            let mut filter = Vec::new();
            for j in 0..s {
                let args = vec![universe[i], universe[j]];
                match join.value_at(&args) {
                    Ok(result) if result == universe[j] => filter.push(universe[j]),
                    Ok(_) => {},
                    Err(e) => return Err(format!("Error evaluating join operation: {}", e)),
                }
            }
            filters.push(filter);
        }
        
        // Check if we need to add a bottom element
        let mut has_zero = false;
        for filter in &filters {
            if filter.len() == s {
                has_zero = true;
                break;
            }
        }
        
        if !has_zero {
            universe.push(-1); // Use -1 as bottom element
            let bot_filter = universe.clone();
            filters.push(bot_filter);
        }
        
        // Create a simple lattice implementation
        JoinLattice::new(name, universe, filters)
    }
    
    /// Convert a congruence lattice to a small lattice.
    /// 
    /// This method is not implemented in the partial version as it requires
    /// CongruenceLattice which is not yet available.
    /// 
    /// # Arguments
    /// * `con` - The congruence lattice to convert
    /// 
    /// # Returns
    /// * `Err(String)` - Always returns an error indicating this method is not implemented
    pub fn con_to_small_lattice(_con: &dyn crate::lat::Lattice<i32>) -> Result<Box<dyn crate::lat::SmallLattice<i32>>, String> {
        Err("con_to_small_lattice requires CongruenceLattice which is not yet implemented".to_string())
    }
    
    /// Create the dual of a basic lattice.
    /// 
    /// This method is not implemented in the partial version as it requires
    /// BasicLattice which is not yet available.
    /// 
    /// # Arguments
    /// * `lat` - The basic lattice to dualize
    /// 
    /// # Returns
    /// * `Err(String)` - Always returns an error indicating this method is not implemented
    pub fn dual(_lat: &dyn crate::lat::Lattice<i32>) -> Result<Box<dyn crate::lat::Lattice<i32>>, String> {
        Err("dual requires BasicLattice which is not yet implemented".to_string())
    }
    
    /// A simple lattice implementation for meet operations.
    #[derive(Debug, Clone)]
    pub struct MeetLattice {
        name: String,
        universe: Vec<i32>,
        filters: Vec<Vec<i32>>,
    }
    
    impl MeetLattice {
        pub fn new(name: String, universe: Vec<i32>, filters: Vec<Vec<i32>>) -> Result<Self, String> {
            if universe.len() != filters.len() {
                return Err("Universe and filters must have the same length".to_string());
            }
            Ok(MeetLattice { name, universe, filters })
        }
    }
    
    impl crate::lat::Order<i32> for MeetLattice {
        fn leq(&self, a: &i32, b: &i32) -> bool {
            // Find the index of a in the universe
            if let Some(a_idx) = self.universe.iter().position(|&x| x == *a) {
                // Check if b is in the filter of a
                self.filters[a_idx].contains(b)
            } else {
                false
            }
        }
    }
    
    impl MeetLattice {
        /// Get the name of this lattice.
        pub fn name(&self) -> &str {
            &self.name
        }
        
        /// Get the universe of this lattice.
        pub fn universe(&self) -> &[i32] {
            &self.universe
        }
        
        /// Get join irreducibles of this lattice.
        pub fn join_irreducibles(&self) -> Vec<i32> {
            // For now, return all elements as join irreducibles
            self.universe.clone()
        }
        
        /// Get meet irreducibles of this lattice.
        pub fn meet_irreducibles(&self) -> Vec<i32> {
            // For now, return all elements as meet irreducibles
            self.universe.clone()
        }
        
        /// Get join irreducibles as an OrderedSet.
        pub fn join_irreducibles_po(&self) -> Result<crate::lat::ordered_set::OrderedSet<i32>, String> {
            let jis = self.join_irreducibles();
            self.make_ordered_set_from_subset(&jis, "JoinIrreducibles".to_string())
        }
        
        /// Get meet irreducibles as an OrderedSet.
        pub fn meet_irreducibles_po(&self) -> Result<crate::lat::ordered_set::OrderedSet<i32>, String> {
            let mis = self.meet_irreducibles();
            self.make_ordered_set_from_subset(&mis, "MeetIrreducibles".to_string())
        }
        
        /// Create an OrderedSet from a subset of elements with their order relations.
        fn make_ordered_set_from_subset(
            &self,
            subset: &[i32],
            name: String,
        ) -> Result<crate::lat::ordered_set::OrderedSet<i32>, String> {
            use crate::lat::ordered_set::OrderedSet;
            
            let mut upper_covers_list: Vec<Vec<i32>> = Vec::new();
            
            for &elem1 in subset {
                let mut covers = Vec::new();
                
                // Find all elements that are greater than elem1
                let mut greater_than: Vec<i32> = subset.iter()
                    .filter(|&&elem2| elem1 != elem2 && self.leq(&elem1, &elem2))
                    .copied()
                    .collect();
                
                // Find minimal elements among those greater than elem1
                // An element is a cover if it's minimal among the greater elements
                for &candidate in &greater_than {
                    let mut is_minimal = true;
                    for &other in &greater_than {
                        if candidate != other && self.leq(&other, &candidate) {
                            is_minimal = false;
                            break;
                        }
                    }
                    if is_minimal {
                        covers.push(candidate);
                    }
                }
                
                upper_covers_list.push(covers);
            }
            
            OrderedSet::new(Some(name), subset.to_vec(), upper_covers_list)
        }
        
        /// Get atoms of this lattice.
        pub fn atoms(&self) -> Vec<i32> {
            // Find elements that are minimal in the order
            let mut atoms = Vec::new();
            for &elem in &self.universe {
                let mut is_atom = true;
                for &other in &self.universe {
                    if other != elem && self.leq(&other, &elem) {
                        is_atom = false;
                        break;
                    }
                }
                if is_atom {
                    atoms.push(elem);
                }
            }
            atoms
        }
        
        /// Get coatoms of this lattice.
        pub fn coatoms(&self) -> Vec<i32> {
            // Find elements that are maximal in the order
            let mut coatoms = Vec::new();
            for &elem in &self.universe {
                let mut is_coatom = true;
                for &other in &self.universe {
                    if other != elem && self.leq(&elem, &other) {
                        is_coatom = false;
                        break;
                    }
                }
                if is_coatom {
                    coatoms.push(elem);
                }
            }
            coatoms
        }
        
        /// Compute the join of two elements.
        pub fn join(&self, a: &i32, b: &i32) -> i32 {
            // Find the least upper bound
            for &elem in &self.universe {
                if self.leq(a, &elem) && self.leq(b, &elem) {
                    let mut is_lub = true;
                    for &other in &self.universe {
                        // Check if there's another upper bound that is strictly less than elem
                        if self.leq(a, &other) && self.leq(b, &other) && self.leq(&other, &elem) && elem != other {
                            is_lub = false;
                            break;
                        }
                    }
                    if is_lub {
                        return elem;
                    }
                }
            }
            // If no lub found, return the maximum element
            *self.universe.iter().max().unwrap_or(a)
        }
        
        /// Compute the join of a list of elements.
        pub fn join_list(&self, args: &[i32]) -> i32 {
            if args.is_empty() {
                return *self.universe.iter().min().unwrap_or(&0);
            }
            args.iter().fold(args[0], |acc, &x| self.join(&acc, &x))
        }
        
        /// Compute the meet of two elements.
        pub fn meet(&self, a: &i32, b: &i32) -> i32 {
            // Find the greatest lower bound
            for &elem in &self.universe {
                if self.leq(&elem, a) && self.leq(&elem, b) {
                    let mut is_glb = true;
                    for &other in &self.universe {
                        // Check if there's another lower bound that is strictly greater than elem
                        if self.leq(&other, a) && self.leq(&other, b) && self.leq(&elem, &other) && elem != other {
                            is_glb = false;
                            break;
                        }
                    }
                    if is_glb {
                        return elem;
                    }
                }
            }
            // If no glb found, return the minimum element
            *self.universe.iter().min().unwrap_or(a)
        }
        
        /// Compute the meet of a list of elements.
        pub fn meet_list(&self, args: &[i32]) -> i32 {
            if args.is_empty() {
                return *self.universe.iter().max().unwrap_or(&0);
            }
            args.iter().fold(args[0], |acc, &x| self.meet(&acc, &x))
        }
    }
    
    /// A simple lattice implementation for join operations.
    #[derive(Debug, Clone)]
    pub struct JoinLattice {
        name: String,
        universe: Vec<i32>,
        filters: Vec<Vec<i32>>,
    }
    
    impl JoinLattice {
        pub fn new(name: String, universe: Vec<i32>, filters: Vec<Vec<i32>>) -> Result<Self, String> {
            if universe.len() != filters.len() {
                return Err("Universe and filters must have the same length".to_string());
            }
            Ok(JoinLattice { name, universe, filters })
        }
    }
    
    impl crate::lat::Order<i32> for JoinLattice {
        fn leq(&self, a: &i32, b: &i32) -> bool {
            // Find the index of a in the universe
            if let Some(a_idx) = self.universe.iter().position(|&x| x == *a) {
                // Check if b is in the filter of a
                self.filters[a_idx].contains(b)
            } else {
                false
            }
        }
    }
    
    impl JoinLattice {
        /// Get the name of this lattice.
        pub fn name(&self) -> &str {
            &self.name
        }
        
        /// Get the universe of this lattice.
        pub fn universe(&self) -> &[i32] {
            &self.universe
        }
        
        /// Get join irreducibles of this lattice.
        /// An element is join irreducible if it cannot be expressed as the join
        /// of two strictly smaller elements.
        pub fn join_irreducibles(&self) -> Vec<i32> {
            let mut jis = Vec::new();
            
            for &elem in &self.universe {
                // Compute the join of all elements strictly smaller than elem
                let mut join_of_smaller = None;
                
                for &other in &self.universe {
                    // Check if other is strictly smaller than elem
                    if self.leq(&other, &elem) && other != elem {
                        if let Some(current_join) = join_of_smaller {
                            join_of_smaller = Some(self.join(&current_join, &other));
                        } else {
                            join_of_smaller = Some(other);
                        }
                        
                        // Early exit: if we've already reached elem, it's not join irreducible
                        if let Some(ref join_val) = join_of_smaller {
                            if *join_val == elem {
                                break;
                            }
                        }
                    }
                }
                
                // If join_of_smaller is None, elem is the bottom element (not join irreducible)
                // If join_of_smaller != elem, then elem is join irreducible
                match join_of_smaller {
                    None => {
                        // Bottom element - not considered join irreducible
                        // Do not add it to the list
                    }
                    Some(join_val) => {
                        if join_val != elem {
                            jis.push(elem);
                        }
                    }
                }
            }
            
            jis
        }
        
        /// Get meet irreducibles of this lattice.
        pub fn meet_irreducibles(&self) -> Vec<i32> {
            // For now, return all elements as meet irreducibles
            self.universe.clone()
        }
        
        /// Get join irreducibles as an OrderedSet.
        pub fn join_irreducibles_po(&self) -> Result<crate::lat::ordered_set::OrderedSet<i32>, String> {
            let jis = self.join_irreducibles();
            self.make_ordered_set_from_subset(&jis, "JoinIrreducibles".to_string())
        }
        
        /// Get meet irreducibles as an OrderedSet.
        pub fn meet_irreducibles_po(&self) -> Result<crate::lat::ordered_set::OrderedSet<i32>, String> {
            let mis = self.meet_irreducibles();
            self.make_ordered_set_from_subset(&mis, "MeetIrreducibles".to_string())
        }
        
        /// Create an OrderedSet from a subset of elements with their order relations.
        fn make_ordered_set_from_subset(
            &self,
            subset: &[i32],
            name: String,
        ) -> Result<crate::lat::ordered_set::OrderedSet<i32>, String> {
            use crate::lat::ordered_set::OrderedSet;
            
            let mut upper_covers_list: Vec<Vec<i32>> = Vec::new();
            
            for &elem1 in subset {
                let mut covers = Vec::new();
                
                // Find all elements that are greater than elem1
                let mut greater_than: Vec<i32> = subset.iter()
                    .filter(|&&elem2| elem1 != elem2 && self.leq(&elem1, &elem2))
                    .copied()
                    .collect();
                
                // Find minimal elements among those greater than elem1
                // An element is a cover if it's minimal among the greater elements
                for &candidate in &greater_than {
                    let mut is_minimal = true;
                    for &other in &greater_than {
                        if candidate != other && self.leq(&other, &candidate) {
                            is_minimal = false;
                            break;
                        }
                    }
                    if is_minimal {
                        covers.push(candidate);
                    }
                }
                
                upper_covers_list.push(covers);
            }
            
            OrderedSet::new(Some(name), subset.to_vec(), upper_covers_list)
        }
        
        /// Get atoms of this lattice.
        pub fn atoms(&self) -> Vec<i32> {
            // Find elements that are minimal in the order
            let mut atoms = Vec::new();
            for &elem in &self.universe {
                let mut is_atom = true;
                for &other in &self.universe {
                    if other != elem && self.leq(&other, &elem) {
                        is_atom = false;
                        break;
                    }
                }
                if is_atom {
                    atoms.push(elem);
                }
            }
            atoms
        }
        
        /// Get coatoms of this lattice.
        pub fn coatoms(&self) -> Vec<i32> {
            // Find elements that are maximal in the order
            let mut coatoms = Vec::new();
            for &elem in &self.universe {
                let mut is_coatom = true;
                for &other in &self.universe {
                    if other != elem && self.leq(&elem, &other) {
                        is_coatom = false;
                        break;
                    }
                }
                if is_coatom {
                    coatoms.push(elem);
                }
            }
            coatoms
        }
        
        /// Compute the join of two elements.
        pub fn join(&self, a: &i32, b: &i32) -> i32 {
            // Find the least upper bound
            for &elem in &self.universe {
                if self.leq(a, &elem) && self.leq(b, &elem) {
                    let mut is_lub = true;
                    for &other in &self.universe {
                        // Check if there's another upper bound that is strictly less than elem
                        if self.leq(a, &other) && self.leq(b, &other) && self.leq(&other, &elem) && elem != other {
                            is_lub = false;
                            break;
                        }
                    }
                    if is_lub {
                        return elem;
                    }
                }
            }
            // If no lub found, return the maximum element
            *self.universe.iter().max().unwrap_or(a)
        }
        
        /// Compute the join of a list of elements.
        pub fn join_list(&self, args: &[i32]) -> i32 {
            if args.is_empty() {
                return *self.universe.iter().min().unwrap_or(&0);
            }
            args.iter().fold(args[0], |acc, &x| self.join(&acc, &x))
        }
        
        /// Compute the meet of two elements.
        pub fn meet(&self, a: &i32, b: &i32) -> i32 {
            // Find the greatest lower bound
            for &elem in &self.universe {
                if self.leq(&elem, a) && self.leq(&elem, b) {
                    let mut is_glb = true;
                    for &other in &self.universe {
                        // Check if there's another lower bound that is strictly greater than elem
                        if self.leq(&other, a) && self.leq(&other, b) && self.leq(&elem, &other) && elem != other {
                            is_glb = false;
                            break;
                        }
                    }
                    if is_glb {
                        return elem;
                    }
                }
            }
            // If no glb found, return the minimum element
            *self.universe.iter().min().unwrap_or(a)
        }
        
        /// Compute the meet of a list of elements.
        pub fn meet_list(&self, args: &[i32]) -> i32 {
            if args.is_empty() {
                return *self.universe.iter().max().unwrap_or(&0);
            }
            args.iter().fold(args[0], |acc, &x| self.meet(&acc, &x))
        }
    }
}

pub use lattices::*;

pub mod ordered_sets;

// Example implementations for testing
#[derive(Debug, Clone)]
pub struct DivisibilityOrder;

impl Order<i32> for DivisibilityOrder {
    fn leq(&self, a: &i32, b: &i32) -> bool {
        if *a == 0 { return true; }  // 0 divides everything by convention
        if *b == 0 { return *a == 0; }
        *a != 0 && *b % *a == 0
    }
}

#[derive(Debug, Clone)]
pub struct PrefixOrder;

impl Order<String> for PrefixOrder {
    fn leq(&self, a: &String, b: &String) -> bool {
        b.starts_with(a)
    }
}

#[derive(Debug, Clone)]
pub struct NaturalOrder;

impl Order<i32> for NaturalOrder {
    fn leq(&self, a: &i32, b: &i32) -> bool {
        a <= b
    }
}

impl Order<u32> for NaturalOrder {
    fn leq(&self, a: &u32, b: &u32) -> bool {
        a <= b
    }
}

impl Order<String> for NaturalOrder {
    fn leq(&self, a: &String, b: &String) -> bool {
        a <= b
    }
}
