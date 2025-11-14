use crate::lat::Lattice;
use crate::alg::algebra::Algebra;
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};
use std::collections::HashMap;
use std::fmt;

/// A small lattice is a finite lattice with indexed elements.
/// 
/// This trait extends the general `Lattice` trait with operations
/// specific to small finite lattices where elements can be indexed.
/// The main addition is the ability to get upper covers by index,
/// which is useful for efficient lattice computations.
/// 
/// # Index-Based Operations
/// 
/// Small lattices allow elements to be accessed by integer indices,
/// typically from 0 to size-1. This enables efficient algorithms
/// that work with array-based representations of the lattice.
/// 
/// # Examples
/// 
/// ## Diamond lattice (4-element lattice)
/// ```
/// use uacalc::lat::{SmallLattice, Lattice, Order};
/// use uacalc::alg::algebra::Algebra;
/// 
/// // Note: Full implementation would require implementing all parent traits
/// // This is a conceptual example showing the upper covers relationship
/// // In a diamond lattice with elements [⊥, a, b, ⊤]:
/// // - upper_covers_indices(0) -> [1, 2] (⊥ is covered by a and b)
/// // - upper_covers_indices(1) -> [3] (a is covered by ⊤)
/// // - upper_covers_indices(2) -> [3] (b is covered by ⊤)
/// // - upper_covers_indices(3) -> [] (⊤ has no upper covers)
/// ```
pub trait SmallLattice<E>: Lattice<E> {
    /// Returns the indices of the upper covers of the element at the given index.
    /// 
    /// An upper cover of an element x is an element y such that:
    /// 1. x < y (y is strictly greater than x)
    /// 2. There is no element z with x < z < y (y immediately covers x)
    /// 
    /// This method returns the indices (positions in the lattice ordering)
    /// of all such elements y for the element at position `index`.
    /// 
    /// # Arguments
    /// * `index` - The index of the element whose upper covers are requested
    /// 
    /// # Returns
    /// A vector of indices representing the upper covers of the element
    /// 
    /// # Panics
    /// May panic if `index` is out of bounds for the lattice
    fn upper_covers_indices(&self, index: usize) -> Vec<usize>;
}

/// A concrete implementation of SmallLattice for testing purposes.
/// 
/// This implements a diamond lattice (M3) with 4 elements:
/// - 0: bottom element (⊥)
/// - 1: left atom (a)
/// - 2: right atom (b) 
/// - 3: top element (⊤)
/// 
/// The covering relations are:
/// - 0 is covered by 1 and 2
/// - 1 and 2 are both covered by 3
/// - 3 has no upper covers
#[derive(Debug, Clone)]
pub struct DiamondLattice {
    elements: Vec<usize>,
    upper_covers: Vec<Vec<usize>>,
    name: String,
    description: Option<String>,
    similarity_type: SimilarityType,
}

impl fmt::Display for DiamondLattice {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "DiamondLattice")
    }
}

impl DiamondLattice {
    /// Create a new diamond lattice (M3).
    /// 
    /// # Returns
    /// A new diamond lattice with 4 elements
    pub fn new() -> Self {
        // Diamond lattice: 0 (bottom) < 1,2 (atoms) < 3 (top)
        // Upper covers: 0 -> [1,2], 1 -> [3], 2 -> [3], 3 -> []
        let elements = vec![0, 1, 2, 3];
        let upper_covers = vec![
            vec![1, 2],  // 0 is covered by 1 and 2
            vec![3],     // 1 is covered by 3
            vec![3],     // 2 is covered by 3
            vec![],      // 3 has no upper covers
        ];
        
        // Create similarity type with join and meet operations
        let operation_symbols = vec![
            OperationSymbol::new("join", 2, false),
            OperationSymbol::new("meet", 2, false),
        ];
        let similarity_type = SimilarityType::new(operation_symbols);
        
        DiamondLattice {
            elements,
            upper_covers,
            name: "DiamondLattice".to_string(),
            description: Some("Diamond lattice (M3) with 4 elements".to_string()),
            similarity_type,
        }
    }
    
    /// Get the element at the given index.
    pub fn get_element(&self, index: usize) -> Option<usize> {
        self.elements.get(index).copied()
    }
    
    /// Get the size of the lattice.
    pub fn size(&self) -> usize {
        self.elements.len()
    }
}

impl Algebra for DiamondLattice {
    type UniverseItem = usize;
    
    fn universe(&self) -> Box<dyn Iterator<Item = usize>> {
        Box::new(self.elements.clone().into_iter())
    }
    
    fn cardinality(&self) -> i32 {
        self.elements.len() as i32
    }
    
    fn input_size(&self) -> i32 {
        // For a 4-element algebra with 2 binary operations: 4^2 + 4^2 = 32
        32
    }
    
    fn is_unary(&self) -> bool {
        false // Has binary operations
    }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = usize>> {
        Box::new(self.elements.clone().into_iter())
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        // Return empty for now - would need to implement join/meet operations
        vec![]
    }
    
    fn get_operation(&self, _sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        None // Would need to implement join/meet operations
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        HashMap::new() // Would need to implement join/meet operations
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
        &self.similarity_type
    }
    
    fn update_similarity_type(&mut self) {
        // Already set in constructor
    }
    
    fn is_similar_to(&self, _other: &dyn Algebra<UniverseItem = usize>) -> bool {
        // Simplified implementation
        true
    }
    
    fn make_operation_tables(&mut self) {
        // No-op for now
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        vec![]
    }
    
    fn is_idempotent(&self) -> bool {
        true // Join and meet are idempotent
    }
    
    fn is_total(&self) -> bool {
        true // All operations are total
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

impl crate::lat::Order<usize> for DiamondLattice {
    fn leq(&self, a: &usize, b: &usize) -> bool {
        // In diamond lattice: 0 ≤ 1,2 ≤ 3
        match (*a, *b) {
            (0, _) => true,           // 0 ≤ everything
            (1, 1) | (2, 2) => true, // reflexivity
            (1, 3) | (2, 3) => true, // atoms ≤ top
            (3, 3) => true,          // reflexivity
            _ => false,              // all other cases
        }
    }
}

impl Lattice<usize> for DiamondLattice {
    fn join_irreducibles(&self) -> Option<Vec<usize>> {
        Some(vec![1, 2]) // The two atoms
    }
    
    fn meet_irreducibles(&self) -> Option<Vec<usize>> {
        Some(vec![1, 2]) // The two atoms (same as join irreducibles in this case)
    }
    
    fn atoms(&self) -> Option<Vec<usize>> {
        Some(vec![1, 2]) // The two atoms
    }
    
    fn coatoms(&self) -> Option<Vec<usize>> {
        Some(vec![1, 2]) // The two atoms (same as coatoms in this case)
    }
    
    fn join(&self, a: &usize, b: &usize) -> usize {
        // In diamond lattice: join is max in the order
        if *a == 0 { return *b; }
        if *b == 0 { return *a; }
        if *a == *b { return *a; }
        if (*a == 1 && *b == 2) || (*a == 2 && *b == 1) { return 3; }
        if *a == 3 || *b == 3 { return 3; }
        3 // fallback to top
    }
    
    fn join_list(&self, args: &[usize]) -> usize {
        if args.is_empty() {
            return 0; // bottom element
        }
        args.iter().fold(0, |acc, &x| self.join(&acc, &x))
    }
    
    fn meet(&self, a: &usize, b: &usize) -> usize {
        // In diamond lattice: meet is min in the order
        if *a == 3 { return *b; }
        if *b == 3 { return *a; }
        if *a == *b { return *a; }
        if (*a == 1 && *b == 2) || (*a == 2 && *b == 1) { return 0; }
        if *a == 0 || *b == 0 { return 0; }
        0 // fallback to bottom
    }
    
    fn meet_list(&self, args: &[usize]) -> usize {
        if args.is_empty() {
            return 3; // top element
        }
        args.iter().fold(3, |acc, &x| self.meet(&acc, &x))
    }
}

impl SmallLattice<usize> for DiamondLattice {
    fn upper_covers_indices(&self, index: usize) -> Vec<usize> {
        if index < self.upper_covers.len() {
            self.upper_covers[index].clone()
        } else {
            vec![] // out of bounds
        }
    }
}

/// A simple 2-element Boolean lattice for testing.
/// 
/// Elements:
/// - 0: false (bottom)
/// - 1: true (top)
#[derive(Debug, Clone)]
pub struct BooleanLattice {
    elements: Vec<usize>,
    upper_covers: Vec<Vec<usize>>,
    name: String,
    description: Option<String>,
    similarity_type: SimilarityType,
}

impl fmt::Display for BooleanLattice {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "BooleanLattice")
    }
}

impl BooleanLattice {
    /// Create a new Boolean lattice (2-element lattice).
    pub fn new() -> Self {
        let elements = vec![0, 1];
        let upper_covers = vec![
            vec![1],  // 0 is covered by 1
            vec![],   // 1 has no upper covers
        ];
        
        // Create similarity type with join and meet operations
        let operation_symbols = vec![
            OperationSymbol::new("join", 2, false),
            OperationSymbol::new("meet", 2, false),
        ];
        let similarity_type = SimilarityType::new(operation_symbols);
        
        BooleanLattice {
            elements,
            upper_covers,
            name: "BooleanLattice".to_string(),
            description: Some("Boolean lattice with 2 elements".to_string()),
            similarity_type,
        }
    }
    
    /// Get the element at the given index.
    pub fn get_element(&self, index: usize) -> Option<usize> {
        self.elements.get(index).copied()
    }
    
    /// Get the size of the lattice.
    pub fn size(&self) -> usize {
        self.elements.len()
    }
}

impl Algebra for BooleanLattice {
    type UniverseItem = usize;
    
    fn universe(&self) -> Box<dyn Iterator<Item = usize>> {
        Box::new(self.elements.clone().into_iter())
    }
    
    fn cardinality(&self) -> i32 {
        self.elements.len() as i32
    }
    
    fn input_size(&self) -> i32 {
        // For a 2-element algebra with 2 binary operations: 2^2 + 2^2 = 8
        8
    }
    
    fn is_unary(&self) -> bool {
        false // Has binary operations
    }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = usize>> {
        Box::new(self.elements.clone().into_iter())
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        // Return empty for now - would need to implement join/meet operations
        vec![]
    }
    
    fn get_operation(&self, _sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        None // Would need to implement join/meet operations
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        HashMap::new() // Would need to implement join/meet operations
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
        &self.similarity_type
    }
    
    fn update_similarity_type(&mut self) {
        // Already set in constructor
    }
    
    fn is_similar_to(&self, _other: &dyn Algebra<UniverseItem = usize>) -> bool {
        // Simplified implementation
        true
    }
    
    fn make_operation_tables(&mut self) {
        // No-op for now
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        vec![]
    }
    
    fn is_idempotent(&self) -> bool {
        true // Join and meet are idempotent
    }
    
    fn is_total(&self) -> bool {
        true // All operations are total
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

impl crate::lat::Order<usize> for BooleanLattice {
    fn leq(&self, a: &usize, b: &usize) -> bool {
        // In Boolean lattice: 0 ≤ 1
        *a <= *b
    }
}

impl Lattice<usize> for BooleanLattice {
    fn join_irreducibles(&self) -> Option<Vec<usize>> {
        Some(vec![1]) // Only the top element
    }
    
    fn meet_irreducibles(&self) -> Option<Vec<usize>> {
        Some(vec![1]) // Only the top element
    }
    
    fn atoms(&self) -> Option<Vec<usize>> {
        Some(vec![1]) // Only the top element
    }
    
    fn coatoms(&self) -> Option<Vec<usize>> {
        Some(vec![1]) // Only the top element
    }
    
    fn join(&self, a: &usize, b: &usize) -> usize {
        if *a == 1 || *b == 1 { 1 } else { 0 }
    }
    
    fn join_list(&self, args: &[usize]) -> usize {
        if args.is_empty() {
            return 0;
        }
        args.iter().fold(0, |acc, &x| self.join(&acc, &x))
    }
    
    fn meet(&self, a: &usize, b: &usize) -> usize {
        if *a == 0 || *b == 0 { 0 } else { 1 }
    }
    
    fn meet_list(&self, args: &[usize]) -> usize {
        if args.is_empty() {
            return 1;
        }
        args.iter().fold(1, |acc, &x| self.meet(&acc, &x))
    }
}

impl SmallLattice<usize> for BooleanLattice {
    fn upper_covers_indices(&self, index: usize) -> Vec<usize> {
        if index < self.upper_covers.len() {
            self.upper_covers[index].clone()
        } else {
            vec![] // out of bounds
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::lat::{SmallLattice, Lattice, Order};
    use crate::alg::algebra::Algebra;

    #[test]
    fn test_diamond_lattice_creation() {
        let lattice = DiamondLattice::new();
        assert_eq!(lattice.size(), 4);
        assert_eq!(lattice.cardinality(), 4);
        assert_eq!(lattice.universe().collect::<Vec<_>>(), vec![0, 1, 2, 3]);
    }

    #[test]
    fn test_diamond_lattice_get_element() {
        let lattice = DiamondLattice::new();
        assert_eq!(lattice.get_element(0), Some(0));
        assert_eq!(lattice.get_element(1), Some(1));
        assert_eq!(lattice.get_element(2), Some(2));
        assert_eq!(lattice.get_element(3), Some(3));
        assert_eq!(lattice.get_element(4), None); // out of bounds
    }

    #[test]
    fn test_diamond_lattice_upper_covers_indices() {
        let lattice = DiamondLattice::new();
        
        // Bottom element (0) is covered by both atoms (1, 2)
        let covers_0 = lattice.upper_covers_indices(0);
        assert_eq!(covers_0.len(), 2);
        assert!(covers_0.contains(&1));
        assert!(covers_0.contains(&2));
        
        // Left atom (1) is covered by top (3)
        let covers_1 = lattice.upper_covers_indices(1);
        assert_eq!(covers_1, vec![3]);
        
        // Right atom (2) is covered by top (3)
        let covers_2 = lattice.upper_covers_indices(2);
        assert_eq!(covers_2, vec![3]);
        
        // Top element (3) has no upper covers
        let covers_3 = lattice.upper_covers_indices(3);
        assert_eq!(covers_3, vec![] as Vec<usize>);
        
        // Out of bounds should return empty list
        let covers_out = lattice.upper_covers_indices(4);
        assert_eq!(covers_out, vec![] as Vec<usize>);
    }

    #[test]
    fn test_diamond_lattice_order_relation() {
        let lattice = DiamondLattice::new();
        
        // Bottom element is less than or equal to everything
        assert!(lattice.leq(&0, &0));
        assert!(lattice.leq(&0, &1));
        assert!(lattice.leq(&0, &2));
        assert!(lattice.leq(&0, &3));
        
        // Atoms are less than or equal to themselves and top
        assert!(lattice.leq(&1, &1));
        assert!(lattice.leq(&1, &3));
        assert!(lattice.leq(&2, &2));
        assert!(lattice.leq(&2, &3));
        
        // Top element is only less than or equal to itself
        assert!(lattice.leq(&3, &3));
        
        // Atoms are not comparable to each other
        assert!(!lattice.leq(&1, &2));
        assert!(!lattice.leq(&2, &1));
        
        // Nothing is less than bottom (except bottom itself)
        assert!(!lattice.leq(&1, &0));
        assert!(!lattice.leq(&2, &0));
        assert!(!lattice.leq(&3, &0));
    }

    #[test]
    fn test_diamond_lattice_join_operation() {
        let lattice = DiamondLattice::new();
        
        // Join with bottom element
        assert_eq!(lattice.join(&0, &1), 1);
        assert_eq!(lattice.join(&0, &2), 2);
        assert_eq!(lattice.join(&0, &3), 3);
        assert_eq!(lattice.join(&1, &0), 1);
        assert_eq!(lattice.join(&2, &0), 2);
        assert_eq!(lattice.join(&3, &0), 3);
        
        // Join of atoms is top
        assert_eq!(lattice.join(&1, &2), 3);
        assert_eq!(lattice.join(&2, &1), 3);
        
        // Join with top element
        assert_eq!(lattice.join(&1, &3), 3);
        assert_eq!(lattice.join(&2, &3), 3);
        assert_eq!(lattice.join(&3, &1), 3);
        assert_eq!(lattice.join(&3, &2), 3);
        
        // Idempotent
        assert_eq!(lattice.join(&0, &0), 0);
        assert_eq!(lattice.join(&1, &1), 1);
        assert_eq!(lattice.join(&2, &2), 2);
        assert_eq!(lattice.join(&3, &3), 3);
    }

    #[test]
    fn test_diamond_lattice_meet_operation() {
        let lattice = DiamondLattice::new();
        
        // Meet with top element
        assert_eq!(lattice.meet(&3, &1), 1);
        assert_eq!(lattice.meet(&3, &2), 2);
        assert_eq!(lattice.meet(&3, &0), 0);
        assert_eq!(lattice.meet(&1, &3), 1);
        assert_eq!(lattice.meet(&2, &3), 2);
        assert_eq!(lattice.meet(&0, &3), 0);
        
        // Meet of atoms is bottom
        assert_eq!(lattice.meet(&1, &2), 0);
        assert_eq!(lattice.meet(&2, &1), 0);
        
        // Meet with bottom element
        assert_eq!(lattice.meet(&1, &0), 0);
        assert_eq!(lattice.meet(&2, &0), 0);
        assert_eq!(lattice.meet(&0, &1), 0);
        assert_eq!(lattice.meet(&0, &2), 0);
        
        // Idempotent
        assert_eq!(lattice.meet(&0, &0), 0);
        assert_eq!(lattice.meet(&1, &1), 1);
        assert_eq!(lattice.meet(&2, &2), 2);
        assert_eq!(lattice.meet(&3, &3), 3);
    }

    #[test]
    fn test_diamond_lattice_join_list() {
        let lattice = DiamondLattice::new();
        
        // Join of all elements should be top
        assert_eq!(lattice.join_list(&[0, 1, 2, 3]), 3);
        
        // Join of atoms should be top
        assert_eq!(lattice.join_list(&[1, 2]), 3);
        
        // Join of single element should be that element
        assert_eq!(lattice.join_list(&[1]), 1);
        
        // Join of empty list should be bottom
        assert_eq!(lattice.join_list(&[]), 0);
    }

    #[test]
    fn test_diamond_lattice_meet_list() {
        let lattice = DiamondLattice::new();
        
        // Meet of all elements should be bottom
        assert_eq!(lattice.meet_list(&[0, 1, 2, 3]), 0);
        
        // Meet of atoms should be bottom
        assert_eq!(lattice.meet_list(&[1, 2]), 0);
        
        // Meet of single element should be that element
        assert_eq!(lattice.meet_list(&[1]), 1);
        
        // Meet of empty list should be top
        assert_eq!(lattice.meet_list(&[]), 3);
    }

    #[test]
    fn test_diamond_lattice_atoms_and_coatoms() {
        let lattice = DiamondLattice::new();
        
        let atoms = lattice.atoms().unwrap();
        assert_eq!(atoms.len(), 2);
        assert!(atoms.contains(&1));
        assert!(atoms.contains(&2));
        
        let coatoms = lattice.coatoms().unwrap();
        assert_eq!(coatoms.len(), 2);
        assert!(coatoms.contains(&1));
        assert!(coatoms.contains(&2));
    }

    #[test]
    fn test_diamond_lattice_join_irreducibles() {
        let lattice = DiamondLattice::new();
        
        let join_irr = lattice.join_irreducibles().unwrap();
        assert_eq!(join_irr.len(), 2);
        assert!(join_irr.contains(&1));
        assert!(join_irr.contains(&2));
    }

    #[test]
    fn test_diamond_lattice_meet_irreducibles() {
        let lattice = DiamondLattice::new();
        
        let meet_irr = lattice.meet_irreducibles().unwrap();
        assert_eq!(meet_irr.len(), 2);
        assert!(meet_irr.contains(&1));
        assert!(meet_irr.contains(&2));
    }

    #[test]
    fn test_diamond_lattice_laws() {
        let lattice = DiamondLattice::new();
        
        // Commutative laws
        for a in 0..4 {
            for b in 0..4 {
                assert_eq!(lattice.join(&a, &b), lattice.join(&b, &a));
                assert_eq!(lattice.meet(&a, &b), lattice.meet(&b, &a));
            }
        }
        
        // Associative laws
        for a in 0..4 {
            for b in 0..4 {
                for c in 0..4 {
                    // join(join(a,b), c) == join(a, join(b,c))
                    let left_join = lattice.join(&lattice.join(&a, &b), &c);
                    let right_join = lattice.join(&a, &lattice.join(&b, &c));
                    assert_eq!(left_join, right_join);
                    
                    // meet(meet(a,b), c) == meet(a, meet(b,c))
                    let left_meet = lattice.meet(&lattice.meet(&a, &b), &c);
                    let right_meet = lattice.meet(&a, &lattice.meet(&b, &c));
                    assert_eq!(left_meet, right_meet);
                }
            }
        }
        
        // Absorption laws
        for a in 0..4 {
            for b in 0..4 {
                // join(a, meet(a,b)) == a
                assert_eq!(lattice.join(&a, &lattice.meet(&a, &b)), a);
                // meet(a, join(a,b)) == a
                assert_eq!(lattice.meet(&a, &lattice.join(&a, &b)), a);
            }
        }
    }

    #[test]
    fn test_boolean_lattice_creation() {
        let lattice = BooleanLattice::new();
        assert_eq!(lattice.size(), 2);
        assert_eq!(lattice.cardinality(), 2);
        assert_eq!(lattice.universe().collect::<Vec<_>>(), vec![0, 1]);
    }

    #[test]
    fn test_boolean_lattice_get_element() {
        let lattice = BooleanLattice::new();
        assert_eq!(lattice.get_element(0), Some(0));
        assert_eq!(lattice.get_element(1), Some(1));
        assert_eq!(lattice.get_element(2), None); // out of bounds
    }

    #[test]
    fn test_boolean_lattice_upper_covers_indices() {
        let lattice = BooleanLattice::new();
        
        // Bottom element (0) is covered by top (1)
        let covers_0 = lattice.upper_covers_indices(0);
        assert_eq!(covers_0, vec![1]);
        
        // Top element (1) has no upper covers
        let covers_1 = lattice.upper_covers_indices(1);
        assert_eq!(covers_1, vec![] as Vec<usize>);
        
        // Out of bounds should return empty list
        let covers_out = lattice.upper_covers_indices(2);
        assert_eq!(covers_out, vec![] as Vec<usize>);
    }

    #[test]
    fn test_boolean_lattice_order_relation() {
        let lattice = BooleanLattice::new();
        
        // Bottom element is less than or equal to everything
        assert!(lattice.leq(&0, &0));
        assert!(lattice.leq(&0, &1));
        
        // Top element is only less than or equal to itself
        assert!(lattice.leq(&1, &1));
        
        // Top is not less than bottom
        assert!(!lattice.leq(&1, &0));
    }

    #[test]
    fn test_boolean_lattice_join_operation() {
        let lattice = BooleanLattice::new();
        
        // Join with bottom element
        assert_eq!(lattice.join(&0, &1), 1);
        assert_eq!(lattice.join(&1, &0), 1);
        
        // Idempotent
        assert_eq!(lattice.join(&0, &0), 0);
        assert_eq!(lattice.join(&1, &1), 1);
    }

    #[test]
    fn test_boolean_lattice_meet_operation() {
        let lattice = BooleanLattice::new();
        
        // Meet with top element
        assert_eq!(lattice.meet(&1, &0), 0);
        assert_eq!(lattice.meet(&0, &1), 0);
        
        // Idempotent
        assert_eq!(lattice.meet(&0, &0), 0);
        assert_eq!(lattice.meet(&1, &1), 1);
    }

    #[test]
    fn test_boolean_lattice_join_list() {
        let lattice = BooleanLattice::new();
        
        // Join of all elements should be top
        assert_eq!(lattice.join_list(&[0, 1]), 1);
        
        // Join of single element should be that element
        assert_eq!(lattice.join_list(&[0]), 0);
        assert_eq!(lattice.join_list(&[1]), 1);
        
        // Join of empty list should be bottom
        assert_eq!(lattice.join_list(&[]), 0);
    }

    #[test]
    fn test_boolean_lattice_meet_list() {
        let lattice = BooleanLattice::new();
        
        // Meet of all elements should be bottom
        assert_eq!(lattice.meet_list(&[0, 1]), 0);
        
        // Meet of single element should be that element
        assert_eq!(lattice.meet_list(&[0]), 0);
        assert_eq!(lattice.meet_list(&[1]), 1);
        
        // Meet of empty list should be top
        assert_eq!(lattice.meet_list(&[]), 1);
    }

    #[test]
    fn test_boolean_lattice_atoms_and_coatoms() {
        let lattice = BooleanLattice::new();
        
        let atoms = lattice.atoms().unwrap();
        assert_eq!(atoms, vec![1]);
        
        let coatoms = lattice.coatoms().unwrap();
        assert_eq!(coatoms, vec![1]);
    }

    #[test]
    fn test_boolean_lattice_join_irreducibles() {
        let lattice = BooleanLattice::new();
        
        let join_irr = lattice.join_irreducibles().unwrap();
        assert_eq!(join_irr, vec![1]);
    }

    #[test]
    fn test_boolean_lattice_meet_irreducibles() {
        let lattice = BooleanLattice::new();
        
        let meet_irr = lattice.meet_irreducibles().unwrap();
        assert_eq!(meet_irr, vec![1]);
    }

    #[test]
    fn test_boolean_lattice_laws() {
        let lattice = BooleanLattice::new();
        
        // Commutative laws
        for a in 0..2 {
            for b in 0..2 {
                assert_eq!(lattice.join(&a, &b), lattice.join(&b, &a));
                assert_eq!(lattice.meet(&a, &b), lattice.meet(&b, &a));
            }
        }
        
        // Associative laws
        for a in 0..2 {
            for b in 0..2 {
                for c in 0..2 {
                    // join(join(a,b), c) == join(a, join(b,c))
                    let left_join = lattice.join(&lattice.join(&a, &b), &c);
                    let right_join = lattice.join(&a, &lattice.join(&b, &c));
                    assert_eq!(left_join, right_join);
                    
                    // meet(meet(a,b), c) == meet(a, meet(b,c))
                    let left_meet = lattice.meet(&lattice.meet(&a, &b), &c);
                    let right_meet = lattice.meet(&a, &lattice.meet(&b, &c));
                    assert_eq!(left_meet, right_meet);
                }
            }
        }
        
        // Absorption laws
        for a in 0..2 {
            for b in 0..2 {
                // join(a, meet(a,b)) == a
                assert_eq!(lattice.join(&a, &lattice.meet(&a, &b)), a);
                // meet(a, join(a,b)) == a
                assert_eq!(lattice.meet(&a, &lattice.join(&a, &b)), a);
            }
        }
    }

    #[test]
    fn test_diamond_vs_boolean_comparison() {
        let diamond = DiamondLattice::new();
        let boolean = BooleanLattice::new();
        
        // Different sizes
        assert_ne!(diamond.size(), boolean.size());
        assert_eq!(diamond.size(), 4);
        assert_eq!(boolean.size(), 2);
        
        // Different upper covers for bottom element
        let diamond_covers = diamond.upper_covers_indices(0);
        let boolean_covers = boolean.upper_covers_indices(0);
        assert_ne!(diamond_covers.len(), boolean_covers.len());
        assert_eq!(diamond_covers.len(), 2); // diamond has 2 upper covers
        assert_eq!(boolean_covers.len(), 1); // boolean has 1 upper cover
        
        // Different atoms
        let diamond_atoms = diamond.atoms().unwrap();
        let boolean_atoms = boolean.atoms().unwrap();
        assert_ne!(diamond_atoms.len(), boolean_atoms.len());
        assert_eq!(diamond_atoms.len(), 2); // diamond has 2 atoms
        assert_eq!(boolean_atoms.len(), 1); // boolean has 1 atom
    }

    #[test]
    fn test_small_lattice_trait_usage() {
        // Test that we can use SmallLattice trait generically
        fn test_upper_covers<L: SmallLattice<usize>>(lattice: &L, index: usize) -> Vec<usize> {
            lattice.upper_covers_indices(index)
        }
        
        let diamond = DiamondLattice::new();
        let boolean = BooleanLattice::new();
        
        // Test with diamond lattice
        let diamond_covers = test_upper_covers(&diamond, 0);
        assert_eq!(diamond_covers.len(), 2);
        
        // Test with boolean lattice
        let boolean_covers = test_upper_covers(&boolean, 0);
        assert_eq!(boolean_covers.len(), 1);
    }
}