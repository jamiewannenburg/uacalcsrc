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
    use std::fmt::{Debug, Display};
    use std::hash::Hash;
    use std::sync::Arc;
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
    /// * `Ok(BasicLattice<i32>)` - Successfully created lattice
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
    pub fn lattice_from_meet(name: String, meet: &dyn Operation) -> Result<crate::lat::BasicLattice<i32>, String> {
        use crate::lat::ordered_set::OrderedSet;
        use crate::lat::BasicLattice;
        
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
        
        // Create OrderedSet from filters
        let poset = OrderedSet::ordered_set_from_filters(Some(name.clone()), univ, filters)?;
        
        // Create BasicLattice from OrderedSet
        BasicLattice::new_from_poset(name, poset)
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
    /// * `Ok(BasicLattice<i32>)` - Successfully created lattice
    /// * `Err(String)` - Error message if creation fails
    pub fn lattice_from_join(name: String, join: &dyn Operation) -> Result<crate::lat::BasicLattice<i32>, String> {
        use crate::lat::ordered_set::OrderedSet;
        use crate::lat::BasicLattice;
        
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
        
        // Create OrderedSet from filters
        let poset = OrderedSet::ordered_set_from_filters(Some(name.clone()), univ, filters)?;
        
        // Create BasicLattice from OrderedSet
        BasicLattice::new_from_poset(name, poset)
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
    /// * `Ok(BasicLattice<i32>)` - Successfully created lattice
    /// * `Err(String)` - Error message if creation fails
    pub fn lattice_from_meet_with_universe(
        name: String, 
        univ: Vec<i32>, 
        meet: &dyn Operation
    ) -> Result<crate::lat::BasicLattice<i32>, String> {
        use crate::lat::ordered_set::OrderedSet;
        use crate::lat::BasicLattice;
        
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
        
        // Create OrderedSet from filters
        let poset = OrderedSet::ordered_set_from_filters(Some(name.clone()), universe, filters)?;
        
        // Create BasicLattice from OrderedSet
        BasicLattice::new_from_poset(name, poset)
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
    /// * `Ok(BasicLattice<i32>)` - Successfully created lattice
    /// * `Err(String)` - Error message if creation fails
    pub fn lattice_from_join_with_universe(
        name: String, 
        univ: Vec<i32>, 
        join: &dyn Operation
    ) -> Result<crate::lat::BasicLattice<i32>, String> {
        use crate::lat::ordered_set::OrderedSet;
        use crate::lat::BasicLattice;
        
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
        
        // Create OrderedSet from filters
        let poset = OrderedSet::ordered_set_from_filters(Some(name.clone()), universe, filters)?;
        
        // Create BasicLattice from OrderedSet
        BasicLattice::new_from_poset(name, poset)
    }
    
    /// Convert a congruence lattice to a small lattice.
    /// 
    /// This method converts a CongruenceLattice to a SmallLattice by computing
    /// the upper covers for each element using join irreducibles.
    /// 
    /// # Arguments
    /// * `con` - The congruence lattice to convert
    /// 
    /// # Returns
    /// * `Ok(Box<dyn SmallLattice<Partition>>)` - Successfully created small lattice
    /// * `Err(String)` - Error message if conversion fails
    pub fn con_to_small_lattice<T>(
        con: &mut crate::alg::conlat::CongruenceLattice<T>
    ) -> Result<Box<dyn crate::lat::SmallLattice<crate::alg::conlat::Partition>>, String>
    where
        T: Clone + PartialEq + Eq + std::hash::Hash + Debug + Display + Send + Sync + 'static,
    {
        use crate::alg::conlat::Partition;
        use crate::lat::Lattice;
        
        // Get universe and join irreducibles
        let univ: Vec<Partition> = con.universe().iter().cloned().collect();
        // Use the mutable method to compute join irreducibles if needed
        let jis: Vec<Partition> = con.join_irreducibles().iter().cloned().collect();
        
        // Build upper covers for each element
        let mut ucs: Vec<Vec<usize>> = Vec::new();
        for (idx, elem1) in univ.iter().enumerate() {
            let mut covs = Vec::new();
            for ji in &jis {
                let join = Lattice::join(con, elem1, ji);
                if join != *elem1 {
                    let mut bad = false;
                    let mut to_remove = Vec::new();
                    
                    // Check if join is greater than any existing cover
                    for (cov_idx, elem2) in covs.iter().enumerate() {
                        let cover_part: &Partition = &univ[*elem2];
                        if cover_part.leq(&join) {
                            bad = true;
                            break;
                        }
                        if join.leq(cover_part) {
                            to_remove.push(cov_idx);
                        }
                    }
                    
                    // Remove elements that are greater than join
                    for &idx in to_remove.iter().rev() {
                        covs.remove(idx);
                    }
                    
                    if !bad {
                        // Find index of join in universe
                        if let Some(join_idx) = univ.iter().position(|p| p == &join) {
                            covs.push(join_idx);
                        }
                    }
                }
            }
            ucs.push(covs);
        }
        
        // Create SmallLattice implementation
        Ok(Box::new(PartitionSmallLattice {
            universe: univ,
            upper_covers: ucs,
        }))
    }
    
    /// Create the dual of a basic lattice.
    /// 
    /// The dual lattice reverses the order (leq becomes reversed) and swaps
    /// join and meet operations.
    /// 
    /// # Arguments
    /// * `lat` - The basic lattice to dualize
    /// 
    /// # Returns
    /// * `Ok(Box<dyn Lattice<T>>)` - Successfully created dual lattice
    /// * `Err(String)` - Error message if creation fails
    pub fn dual<T>(lat: crate::lat::BasicLattice<T>) -> Result<Box<dyn crate::lat::Lattice<Arc<crate::lat::ordered_set::POElem<T>>>>, String>
    where
        T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
    {
        use std::sync::Arc;
        use crate::alg::algebra::Algebra;
        
        // Get name and description from the lattice
        let name = lat.name().to_string();
        let description = lat.description().map(|s| s.to_string());
        
        // Create a wrapper that reverses the order and swaps join/meet
        Ok(Box::new(DualLattice {
            base: Arc::new(std::sync::RwLock::new(lat)),
            name,
            description,
        }))
    }
    
    /// A SmallLattice implementation for Partition elements.
    #[derive(Debug)]
    struct PartitionSmallLattice {
        universe: Vec<crate::alg::conlat::Partition>,
        upper_covers: Vec<Vec<usize>>,
    }
    
    impl Display for PartitionSmallLattice {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            write!(f, "PartitionSmallLattice(size={})", self.universe.len())
        }
    }
    
    impl crate::lat::Order<crate::alg::conlat::Partition> for PartitionSmallLattice {
        fn leq(&self, a: &crate::alg::conlat::Partition, b: &crate::alg::conlat::Partition) -> bool {
            a.leq(b)
        }
    }
    
    impl crate::lat::Lattice<crate::alg::conlat::Partition> for PartitionSmallLattice {
        fn join_irreducibles(&self) -> Option<Vec<crate::alg::conlat::Partition>> {
            // Find join irreducibles (elements with exactly one upper cover)
            let jis: Vec<_> = self.upper_covers.iter()
                .enumerate()
                .filter(|(_, covers)| covers.len() == 1)
                .map(|(idx, _)| self.universe[idx].clone())
                .collect();
            Some(jis)
        }
        
        fn meet_irreducibles(&self) -> Option<Vec<crate::alg::conlat::Partition>> {
            // For now, return empty - can be computed if needed
            None
        }
        
        fn atoms(&self) -> Option<Vec<crate::alg::conlat::Partition>> {
            // Atoms are elements with no lower covers (minimal elements)
            // Elements with empty upper covers in the dual are atoms
            // For simplicity, return elements that are covered by all others
            None
        }
        
        fn coatoms(&self) -> Option<Vec<crate::alg::conlat::Partition>> {
            // Coatoms are elements with no upper covers (maximal elements)
            let mut coatoms = Vec::new();
            for (idx, covers) in self.upper_covers.iter().enumerate() {
                if covers.is_empty() {
                    coatoms.push(self.universe[idx].clone());
                }
            }
            Some(coatoms)
        }
        
        fn join(&self, a: &crate::alg::conlat::Partition, b: &crate::alg::conlat::Partition) -> crate::alg::conlat::Partition {
            a.join(b).unwrap_or_else(|_| a.clone())
        }
        
        fn join_list(&self, args: &[crate::alg::conlat::Partition]) -> crate::alg::conlat::Partition {
            if args.is_empty() {
                return self.universe[0].clone(); // Return first element as zero
            }
            args.iter().fold(args[0].clone(), |acc, x| self.join(&acc, x))
        }
        
        fn meet(&self, a: &crate::alg::conlat::Partition, b: &crate::alg::conlat::Partition) -> crate::alg::conlat::Partition {
            a.meet(b).unwrap_or_else(|_| a.clone())
        }
        
        fn meet_list(&self, args: &[crate::alg::conlat::Partition]) -> crate::alg::conlat::Partition {
            if args.is_empty() {
                return self.universe.last().unwrap().clone(); // Return last element as one
            }
            args.iter().fold(args[0].clone(), |acc, x| self.meet(&acc, x))
        }
    }
    
    impl crate::lat::SmallLattice<crate::alg::conlat::Partition> for PartitionSmallLattice {
        fn upper_covers_indices(&self, index: usize) -> Vec<usize> {
            if index < self.upper_covers.len() {
                self.upper_covers[index].clone()
            } else {
                vec![]
            }
        }
    }
    
    impl crate::alg::algebra::Algebra for PartitionSmallLattice {
        type UniverseItem = crate::alg::conlat::Partition;
        
        fn name(&self) -> &str {
            "PartitionSmallLattice"
        }
        
        fn cardinality(&self) -> i32 {
            self.universe.len() as i32
        }
        
        fn input_size(&self) -> i32 {
            // For a lattice, input size is cardinality^2 for join and meet
            let card = self.universe.len() as i64;
            let size = card * card * 2; // join and meet operations
            if size > i32::MAX as i64 {
                -1
            } else {
                size as i32
            }
        }
        
        fn is_unary(&self) -> bool {
            false // Lattices have binary operations
        }
        
        fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem> + 'static> {
            Box::new(self.universe.clone().into_iter())
        }
        
        fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem> + 'static> {
            Box::new(self.universe.clone().into_iter())
        }
        
        fn operations(&self) -> Vec<Box<dyn crate::alg::op::Operation>> {
            vec![]
        }
        
        fn get_operation(&self, _sym: &crate::alg::op::OperationSymbol) -> Option<Box<dyn crate::alg::op::Operation>> {
            None
        }
        
        fn get_operations_map(&self) -> std::collections::HashMap<crate::alg::op::OperationSymbol, Box<dyn crate::alg::op::Operation>> {
            std::collections::HashMap::new()
        }
        
        fn set_name(&mut self, _name: String) {
            // No-op - name is fixed
        }
        
        fn description(&self) -> Option<&str> {
            None
        }
        
        fn set_description(&mut self, _desc: Option<String>) {
            // No-op
        }
        
        fn similarity_type(&self) -> &crate::alg::op::SimilarityType {
            // Return the lattice similarity type
            use crate::alg::op::SimilarityType;
            use once_cell::sync::Lazy;
            static LATTICE_TYPE: Lazy<SimilarityType> = Lazy::new(|| {
                use crate::alg::op::OperationSymbol;
                SimilarityType::new(vec![
                    OperationSymbol::join().clone(),
                    OperationSymbol::meet().clone(),
                ])
            });
            &LATTICE_TYPE
        }
        
        fn update_similarity_type(&mut self) {
            // No-op - similarity type is fixed
        }
        
        fn is_similar_to(&self, other: &dyn crate::alg::algebra::Algebra<UniverseItem = Self::UniverseItem>) -> bool {
            self.similarity_type() == other.similarity_type()
        }
        
        fn make_operation_tables(&mut self) {
            // No-op - no operations to table
        }
        
        fn constant_operations(&self) -> Vec<Box<dyn crate::alg::op::Operation>> {
            vec![]
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
            // No-op
        }
    }
    
    /// A dual lattice wrapper that reverses order and swaps join/meet.
    /// 
    /// This uses Arc and RwLock for interior mutability to handle methods
    /// that require mutable access in a thread-safe way.
    struct DualLattice<T>
    where
        T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
    {
        base: std::sync::Arc<std::sync::RwLock<crate::lat::BasicLattice<T>>>,
        name: String,
        description: Option<String>,
    }
    
    impl<T> std::fmt::Debug for DualLattice<T>
    where
        T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
    {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            write!(f, "DualLattice")
        }
    }
    
    impl<T> std::fmt::Display for DualLattice<T>
    where
        T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
    {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            let base = self.base.read().unwrap();
            write!(f, "Dual({})", base.name())
        }
    }
    
    impl<T> crate::lat::Order<Arc<crate::lat::ordered_set::POElem<T>>> for DualLattice<T>
    where
        T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
    {
        fn leq(&self, a: &Arc<crate::lat::ordered_set::POElem<T>>, b: &Arc<crate::lat::ordered_set::POElem<T>>) -> bool {
            // Reverse the order: a ≤ b in dual iff b ≤ a in original
            let base = self.base.read().unwrap();
            base.leq(b, a)
        }
    }
    
    impl<T> crate::alg::algebra::Algebra for DualLattice<T>
    where
        T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
    {
        type UniverseItem = Arc<crate::lat::ordered_set::POElem<T>>;
        
        fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem> + 'static> {
            let base = self.base.read().unwrap();
            // Use fully qualified syntax to call the trait method, not the public method
            crate::alg::algebra::Algebra::universe(&*base)
        }
        
        fn cardinality(&self) -> i32 {
            let base = self.base.read().unwrap();
            base.cardinality() as i32
        }
        
        fn input_size(&self) -> i32 {
            let base = self.base.read().unwrap();
            base.input_size()
        }
        
        fn is_unary(&self) -> bool {
            let base = self.base.read().unwrap();
            base.is_unary()
        }
        
        fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem> + 'static> {
            let base = self.base.read().unwrap();
            base.iterator()
        }
        
        fn operations(&self) -> Vec<Box<dyn crate::alg::op::Operation>> {
            let base = self.base.read().unwrap();
            base.operations()
        }
        
        fn get_operation(&self, sym: &crate::alg::op::OperationSymbol) -> Option<Box<dyn crate::alg::op::Operation>> {
            let base = self.base.read().unwrap();
            base.get_operation(sym)
        }
        
        fn get_operations_map(&self) -> std::collections::HashMap<crate::alg::op::OperationSymbol, Box<dyn crate::alg::op::Operation>> {
            let base = self.base.read().unwrap();
            base.get_operations_map()
        }
        
        fn similarity_type(&self) -> &crate::alg::op::SimilarityType {
            // We can't return a reference to data inside the RwLock guard
            // So we need to use the base's similarity type directly
            // This is a limitation - we'll need to store a reference or clone
            // For now, we'll use a static or clone the similarity type
            // Actually, BasicLattice stores the similarity type in the base GeneralAlgebra,
            // which should be accessible. Let me check if we can access it differently.
            // Since we can't return a reference, we need to either:
            // 1. Store the similarity type in DualLattice
            // 2. Clone it (but SimilarityType might not be Clone)
            // For now, let's use a workaround - return a static lattice similarity type
            use crate::alg::op::SimilarityType;
            use once_cell::sync::Lazy;
            static LATTICE_TYPE: Lazy<SimilarityType> = Lazy::new(|| {
                use crate::alg::op::OperationSymbol;
                SimilarityType::new(vec![
                    OperationSymbol::join().clone(),
                    OperationSymbol::meet().clone(),
                ])
            });
            &LATTICE_TYPE
        }
        
        fn update_similarity_type(&mut self) {
            let mut base = self.base.write().unwrap();
            base.update_similarity_type()
        }
        
        fn is_similar_to(&self, other: &dyn crate::alg::algebra::Algebra<UniverseItem = Self::UniverseItem>) -> bool {
            let base = self.base.read().unwrap();
            base.is_similar_to(other)
        }
        
        fn make_operation_tables(&mut self) {
            let mut base = self.base.write().unwrap();
            base.make_operation_tables()
        }
        
        fn constant_operations(&self) -> Vec<Box<dyn crate::alg::op::Operation>> {
            let base = self.base.read().unwrap();
            base.constant_operations()
        }
        
        fn is_idempotent(&self) -> bool {
            let base = self.base.read().unwrap();
            base.is_idempotent()
        }
        
        fn is_total(&self) -> bool {
            let base = self.base.read().unwrap();
            base.is_total()
        }
        
        fn monitoring(&self) -> bool {
            let base = self.base.read().unwrap();
            base.monitoring()
        }
        
        fn get_monitor(&self) -> Option<&dyn crate::alg::algebra::ProgressMonitor> {
            // Can't return a reference to data inside RwLock guard
            // BasicLattice doesn't store monitor, so return None
            None
        }
        
        fn set_monitor(&mut self, monitor: Option<Box<dyn crate::alg::algebra::ProgressMonitor>>) {
            let mut base = self.base.write().unwrap();
            base.set_monitor(monitor)
        }
        
        fn name(&self) -> &str {
            &self.name
        }
        
        fn set_name(&mut self, name: String) {
            self.name = name.clone();
            let mut base = self.base.write().unwrap();
            base.set_name(name)
        }
        
        fn description(&self) -> Option<&str> {
            self.description.as_deref()
        }
        
        fn set_description(&mut self, desc: Option<String>) {
            self.description = desc.clone();
            let mut base = self.base.write().unwrap();
            base.set_description(desc)
        }
    }
    
    impl<T> crate::lat::Lattice<Arc<crate::lat::ordered_set::POElem<T>>> for DualLattice<T>
    where
        T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
    {
        fn join_irreducibles(&self) -> Option<Vec<Arc<crate::lat::ordered_set::POElem<T>>>> {
            // Join irreducibles in dual are meet irreducibles in original
            let base = self.base.write().unwrap();
            base.meet_irreducibles().map(|mis| mis.iter().cloned().collect())
        }
        
        fn meet_irreducibles(&self) -> Option<Vec<Arc<crate::lat::ordered_set::POElem<T>>>> {
            // Meet irreducibles in dual are join irreducibles in original
            let base = self.base.write().unwrap();
            base.join_irreducibles().map(|jis| jis.iter().cloned().collect())
        }
        
        fn atoms(&self) -> Option<Vec<Arc<crate::lat::ordered_set::POElem<T>>>> {
            // Atoms in dual are coatoms in original
            let base = self.base.read().unwrap();
            Some(base.coatoms().iter().cloned().collect())
        }
        
        fn coatoms(&self) -> Option<Vec<Arc<crate::lat::ordered_set::POElem<T>>>> {
            // Coatoms in dual are atoms in original
            let base = self.base.read().unwrap();
            Some(base.atoms().iter().cloned().collect())
        }
        
        fn join(&self, a: &Arc<crate::lat::ordered_set::POElem<T>>, b: &Arc<crate::lat::ordered_set::POElem<T>>) -> Arc<crate::lat::ordered_set::POElem<T>> {
            // Join in dual is meet in original
            let base = self.base.read().unwrap();
            base.meet(a, b)
        }
        
        fn join_list(&self, args: &[Arc<crate::lat::ordered_set::POElem<T>>]) -> Arc<crate::lat::ordered_set::POElem<T>> {
            // Join list in dual is meet list in original
            let base = self.base.read().unwrap();
            base.meet_list(args)
        }
        
        fn meet(&self, a: &Arc<crate::lat::ordered_set::POElem<T>>, b: &Arc<crate::lat::ordered_set::POElem<T>>) -> Arc<crate::lat::ordered_set::POElem<T>> {
            // Meet in dual is join in original
            let base = self.base.read().unwrap();
            base.join(a, b)
        }
        
        fn meet_list(&self, args: &[Arc<crate::lat::ordered_set::POElem<T>>]) -> Arc<crate::lat::ordered_set::POElem<T>> {
            // Meet list in dual is join list in original
            let base = self.base.read().unwrap();
            base.join_list(args)
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
