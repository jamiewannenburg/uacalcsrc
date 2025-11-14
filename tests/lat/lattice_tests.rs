use uacalc::lat::{Lattice, SmallLattice, Order};
use uacalc::alg::algebra::{Algebra, ProgressMonitor};
use uacalc::alg::op::{Operation, OperationSymbol, SimilarityType};
use std::collections::HashMap;
use std::fmt::{Debug, Display};
use std::hash::Hash;

/// A mock implementation of ProgressMonitor for testing
#[derive(Debug)]
struct TestProgressMonitor;

impl ProgressMonitor for TestProgressMonitor {
    fn report_progress(&self, _message: &str) {}
    fn is_cancelled(&self) -> bool { false }
    fn set_progress(&self, _progress: f64) {}
}

/// Example implementation of a simple Boolean lattice (2-element lattice)
/// Elements: false (bottom) and true (top)
#[derive(Debug)]
pub struct BooleanLattice {
    name: String,
    description: Option<String>,
    similarity_type: SimilarityType,
}

impl Display for BooleanLattice {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "BooleanLattice({})", self.name)
    }
}

impl BooleanLattice {
    pub fn new() -> Self {
        BooleanLattice {
            name: "Boolean2".to_string(),
            description: Some("Two-element Boolean lattice".to_string()),
            similarity_type: SimilarityType::new(Vec::new()),
        }
    }
}

impl Algebra for BooleanLattice {
    type UniverseItem = bool;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        Box::new([false, true].into_iter())
    }
    
    fn cardinality(&self) -> i32 { 2 }
    
    fn input_size(&self) -> i32 { 2 }
    
    fn is_unary(&self) -> bool { false }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.universe()
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        Vec::new() // No operations for this simple example
    }
    
    fn get_operation(&self, _sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        None
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        HashMap::new()
    }
    
    fn name(&self) -> &str { &self.name }
    
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
        // Update based on operations (none in this case)
    }
    
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        self.similarity_type() == other.similarity_type()
    }
    
    fn make_operation_tables(&mut self) {
        // No operations to make tables for
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        Vec::new()
    }
    
    fn is_idempotent(&self) -> bool { true }
    
    fn is_total(&self) -> bool { true }
    
    fn monitoring(&self) -> bool {
        false // No monitor for this simple example
    }
    
    fn get_monitor(&self) -> Option<&dyn ProgressMonitor> {
        None
    }
    
    fn set_monitor(&mut self, _monitor: Option<Box<dyn ProgressMonitor>>) {
        // No-op for this simple example
    }
}

impl Order<bool> for BooleanLattice {
    fn leq(&self, a: &bool, b: &bool) -> bool {
        // In Boolean lattice: false ≤ false, false ≤ true, true ≤ true
        // Only false ≤ false is false when a=true, b=false
        !a || *b
    }
}

impl Lattice<bool> for BooleanLattice {
    fn join_irreducibles(&self) -> Option<Vec<bool>> {
        // In Boolean lattice, true is join irreducible
        Some(vec![true])
    }
    
    fn meet_irreducibles(&self) -> Option<Vec<bool>> {
        // In Boolean lattice, false is meet irreducible
        Some(vec![false])
    }
    
    fn atoms(&self) -> Option<Vec<bool>> {
        // true is the only atom (covers bottom element false)
        Some(vec![true])
    }
    
    fn coatoms(&self) -> Option<Vec<bool>> {
        // false is the only coatom (covered by top element true)
        Some(vec![false])
    }
    
    fn join(&self, a: &bool, b: &bool) -> bool {
        *a || *b
    }
    
    fn join_list(&self, args: &[bool]) -> bool {
        args.iter().any(|&x| x)
    }
    
    fn meet(&self, a: &bool, b: &bool) -> bool {
        *a && *b
    }
    
    fn meet_list(&self, args: &[bool]) -> bool {
        args.iter().all(|&x| x)
    }
}

/// Example small lattice implementation with indexed elements
/// Elements: [false, true] with indices [0, 1]
impl SmallLattice<bool> for BooleanLattice {
    fn upper_covers_indices(&self, index: usize) -> Vec<usize> {
        match index {
            0 => vec![1], // false (index 0) is covered by true (index 1)
            1 => vec![],  // true (index 1) has no upper covers
            _ => panic!("Index {} out of bounds for Boolean lattice", index),
        }
    }
}

/// Example implementation of a 4-element diamond lattice
/// Elements: [bottom, left, right, top] with indices [0, 1, 2, 3]
#[derive(Debug)]
pub struct DiamondLattice {
    name: String,
    description: Option<String>,
    similarity_type: SimilarityType,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum DiamondElement {
    Bottom = 0,
    Left = 1,
    Right = 2,
    Top = 3,
}

impl Display for DiamondLattice {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "DiamondLattice({})", self.name)
    }
}

impl DiamondLattice {
    pub fn new() -> Self {
        DiamondLattice {
            name: "Diamond4".to_string(),
            description: Some("Four-element diamond lattice".to_string()),
            similarity_type: SimilarityType::new(Vec::new()),
        }
    }
}

impl Algebra for DiamondLattice {
    type UniverseItem = DiamondElement;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        use DiamondElement::*;
        Box::new([Bottom, Left, Right, Top].into_iter())
    }
    
    fn cardinality(&self) -> i32 { 4 }
    
    fn input_size(&self) -> i32 { 4 }
    
    fn is_unary(&self) -> bool { false }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.universe()
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        Vec::new()
    }
    
    fn get_operation(&self, _sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        None
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        HashMap::new()
    }
    
    fn name(&self) -> &str { &self.name }
    
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
    
    fn update_similarity_type(&mut self) {}
    
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        self.similarity_type() == other.similarity_type()
    }
    
    fn make_operation_tables(&mut self) {}
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        Vec::new()
    }
    
    fn is_idempotent(&self) -> bool { true }
    
    fn is_total(&self) -> bool { true }
    
    fn monitoring(&self) -> bool {
        false
    }
    
    fn get_monitor(&self) -> Option<&dyn ProgressMonitor> {
        None
    }
    
    fn set_monitor(&mut self, _monitor: Option<Box<dyn ProgressMonitor>>) {
        // No-op for this simple example
    }
}

impl Order<DiamondElement> for DiamondLattice {
    fn leq(&self, a: &DiamondElement, b: &DiamondElement) -> bool {
        use DiamondElement::*;
        match (a, b) {
            (Bottom, _) => true,       // Bottom ≤ everything
            (_, Top) => true,          // Everything ≤ Top
            (Left, Left) => true,      // Reflexive
            (Right, Right) => true,    // Reflexive
            (Left, Right) => false,    // Left and Right are incomparable
            (Right, Left) => false,    // Left and Right are incomparable
            (Top, _) => *b == Top,     // Top ≤ only Top
            (_, Bottom) => *a == Bottom, // Only Bottom ≤ Bottom
        }
    }
}

impl Lattice<DiamondElement> for DiamondLattice {
    fn join_irreducibles(&self) -> Option<Vec<DiamondElement>> {
        use DiamondElement::*;
        // Left, Right, and Top are join irreducible
        Some(vec![Left, Right, Top])
    }
    
    fn meet_irreducibles(&self) -> Option<Vec<DiamondElement>> {
        use DiamondElement::*;
        // Bottom, Left, and Right are meet irreducible
        Some(vec![Bottom, Left, Right])
    }
    
    fn atoms(&self) -> Option<Vec<DiamondElement>> {
        use DiamondElement::*;
        // Left and Right are atoms (cover Bottom)
        Some(vec![Left, Right])
    }
    
    fn coatoms(&self) -> Option<Vec<DiamondElement>> {
        use DiamondElement::*;
        // Left and Right are coatoms (covered by Top)
        Some(vec![Left, Right])
    }
    
    fn join(&self, a: &DiamondElement, b: &DiamondElement) -> DiamondElement {
        use DiamondElement::*;
        match (a, b) {
            (Bottom, x) | (x, Bottom) => *x,
            (Top, _) | (_, Top) => Top,
            (Left, Left) => Left,
            (Right, Right) => Right,
            (Left, Right) | (Right, Left) => Top,
        }
    }
    
    fn join_list(&self, args: &[DiamondElement]) -> DiamondElement {
        args.iter().fold(DiamondElement::Bottom, |acc, &x| self.join(&acc, &x))
    }
    
    fn meet(&self, a: &DiamondElement, b: &DiamondElement) -> DiamondElement {
        use DiamondElement::*;
        match (a, b) {
            (Top, x) | (x, Top) => *x,
            (Bottom, _) | (_, Bottom) => Bottom,
            (Left, Left) => Left,
            (Right, Right) => Right,
            (Left, Right) | (Right, Left) => Bottom,
        }
    }
    
    fn meet_list(&self, args: &[DiamondElement]) -> DiamondElement {
        args.iter().fold(DiamondElement::Top, |acc, &x| self.meet(&acc, &x))
    }
}

impl SmallLattice<DiamondElement> for DiamondLattice {
    fn upper_covers_indices(&self, index: usize) -> Vec<usize> {
        match index {
            0 => vec![1, 2], // Bottom (0) is covered by Left (1) and Right (2)
            1 => vec![3],    // Left (1) is covered by Top (3)
            2 => vec![3],    // Right (2) is covered by Top (3)
            3 => vec![],     // Top (3) has no upper covers
            _ => panic!("Index {} out of bounds for diamond lattice", index),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_boolean_lattice_basic() {
        let lattice = BooleanLattice::new();
        
        // Test basic algebra properties
        assert_eq!(lattice.name(), "Boolean2");
        assert_eq!(lattice.cardinality(), 2);
        
        // Test universe
        let universe: Vec<bool> = lattice.universe().collect();
        assert_eq!(universe.len(), 2);
        assert!(universe.contains(&false));
        assert!(universe.contains(&true));
    }

    #[test]
    fn test_boolean_lattice_order() {
        let lattice = BooleanLattice::new();
        
        // Test order relation (false ≤ everything, true ≤ only true)
        assert!(lattice.leq(&false, &false));
        assert!(lattice.leq(&false, &true));
        assert!(!lattice.leq(&true, &false));
        assert!(lattice.leq(&true, &true));
    }

    #[test]
    fn test_boolean_lattice_operations() {
        let lattice = BooleanLattice::new();
        
        // Test join operations (OR)
        assert_eq!(lattice.join(&false, &false), false);
        assert_eq!(lattice.join(&false, &true), true);
        assert_eq!(lattice.join(&true, &false), true);
        assert_eq!(lattice.join(&true, &true), true);
        
        // Test meet operations (AND)
        assert_eq!(lattice.meet(&false, &false), false);
        assert_eq!(lattice.meet(&false, &true), false);
        assert_eq!(lattice.meet(&true, &false), false);
        assert_eq!(lattice.meet(&true, &true), true);
        
        // Test list operations
        assert_eq!(lattice.join_list(&[false, false]), false);
        assert_eq!(lattice.join_list(&[false, true]), true);
        assert_eq!(lattice.join_list(&[true, true]), true);
        
        assert_eq!(lattice.meet_list(&[false, false]), false);
        assert_eq!(lattice.meet_list(&[true, false]), false);
        assert_eq!(lattice.meet_list(&[true, true]), true);
    }

    #[test]
    fn test_boolean_lattice_special_elements() {
        let lattice = BooleanLattice::new();
        
        // Test join irreducibles
        let join_irreds = lattice.join_irreducibles().unwrap();
        assert_eq!(join_irreds, vec![true]);
        
        // Test meet irreducibles
        let meet_irreds = lattice.meet_irreducibles().unwrap();
        assert_eq!(meet_irreds, vec![false]);
        
        // Test atoms
        let atoms = lattice.atoms().unwrap();
        assert_eq!(atoms, vec![true]);
        
        // Test coatoms
        let coatoms = lattice.coatoms().unwrap();
        assert_eq!(coatoms, vec![false]);
    }

    #[test]
    fn test_boolean_small_lattice() {
        let lattice = BooleanLattice::new();
        
        // Test upper covers
        assert_eq!(lattice.upper_covers_indices(0), vec![1]); // false -> true
        assert_eq!(lattice.upper_covers_indices(1), Vec::<usize>::new()); // true -> none
    }

    #[test]
    #[should_panic(expected = "Index 2 out of bounds")]
    fn test_boolean_lattice_index_bounds() {
        let lattice = BooleanLattice::new();
        lattice.upper_covers_indices(2); // Should panic
    }

    #[test]
    fn test_diamond_lattice_basic() {
        let lattice = DiamondLattice::new();
        
        assert_eq!(lattice.name(), "Diamond4");
        assert_eq!(lattice.cardinality(), 4);
        
        let universe: Vec<DiamondElement> = lattice.universe().collect();
        assert_eq!(universe.len(), 4);
    }

    #[test]
    fn test_diamond_lattice_order() {
        let lattice = DiamondLattice::new();
        use DiamondElement::*;
        
        // Bottom ≤ everything
        assert!(lattice.leq(&Bottom, &Bottom));
        assert!(lattice.leq(&Bottom, &Left));
        assert!(lattice.leq(&Bottom, &Right));
        assert!(lattice.leq(&Bottom, &Top));
        
        // Everything ≤ Top
        assert!(lattice.leq(&Bottom, &Top));
        assert!(lattice.leq(&Left, &Top));
        assert!(lattice.leq(&Right, &Top));
        assert!(lattice.leq(&Top, &Top));
        
        // Left and Right are incomparable
        assert!(!lattice.leq(&Left, &Right));
        assert!(!lattice.leq(&Right, &Left));
        
        // Reflexivity
        assert!(lattice.leq(&Left, &Left));
        assert!(lattice.leq(&Right, &Right));
    }

    #[test]
    fn test_diamond_lattice_operations() {
        let lattice = DiamondLattice::new();
        use DiamondElement::*;
        
        // Test join operations
        assert_eq!(lattice.join(&Bottom, &Left), Left);
        assert_eq!(lattice.join(&Left, &Right), Top);
        assert_eq!(lattice.join(&Left, &Top), Top);
        
        // Test meet operations
        assert_eq!(lattice.meet(&Top, &Left), Left);
        assert_eq!(lattice.meet(&Left, &Right), Bottom);
        assert_eq!(lattice.meet(&Left, &Bottom), Bottom);
        
        // Test list operations
        assert_eq!(lattice.join_list(&[Bottom, Left, Right]), Top);
        assert_eq!(lattice.meet_list(&[Top, Left, Right]), Bottom);
    }

    #[test]
    fn test_diamond_lattice_special_elements() {
        let lattice = DiamondLattice::new();
        use DiamondElement::*;
        
        let join_irreds = lattice.join_irreducibles().unwrap();
        assert!(join_irreds.contains(&Left));
        assert!(join_irreds.contains(&Right));
        assert!(join_irreds.contains(&Top));
        
        let atoms = lattice.atoms().unwrap();
        assert_eq!(atoms.len(), 2);
        assert!(atoms.contains(&Left));
        assert!(atoms.contains(&Right));
        
        let coatoms = lattice.coatoms().unwrap();
        assert_eq!(coatoms.len(), 2);
        assert!(coatoms.contains(&Left));
        assert!(coatoms.contains(&Right));
    }

    #[test]
    fn test_diamond_small_lattice() {
        let lattice = DiamondLattice::new();
        
        // Test upper covers for diamond structure
        assert_eq!(lattice.upper_covers_indices(0), vec![1, 2]); // Bottom -> Left, Right
        assert_eq!(lattice.upper_covers_indices(1), vec![3]);    // Left -> Top
        assert_eq!(lattice.upper_covers_indices(2), vec![3]);    // Right -> Top  
        assert_eq!(lattice.upper_covers_indices(3), Vec::<usize>::new());     // Top -> none
    }

    #[test]
    fn test_lattice_laws_boolean() {
        let lattice = BooleanLattice::new();
        
        for &a in &[false, true] {
            for &b in &[false, true] {
                // Test commutativity
                assert_eq!(lattice.join(&a, &b), lattice.join(&b, &a));
                assert_eq!(lattice.meet(&a, &b), lattice.meet(&b, &a));
                
                // Test absorption laws
                assert_eq!(lattice.join(&a, &lattice.meet(&a, &b)), a);
                assert_eq!(lattice.meet(&a, &lattice.join(&a, &b)), a);
                
                for &c in &[false, true] {
                    // Test associativity
                    assert_eq!(
                        lattice.join(&lattice.join(&a, &b), &c),
                        lattice.join(&a, &lattice.join(&b, &c))
                    );
                    assert_eq!(
                        lattice.meet(&lattice.meet(&a, &b), &c),
                        lattice.meet(&a, &lattice.meet(&b, &c))
                    );
                }
            }
        }
    }

    #[test]
    fn test_lattice_laws_diamond() {
        let lattice = DiamondLattice::new();
        use DiamondElement::*;
        let elements = [Bottom, Left, Right, Top];
        
        for &a in &elements {
            for &b in &elements {
                // Test commutativity
                assert_eq!(lattice.join(&a, &b), lattice.join(&b, &a));
                assert_eq!(lattice.meet(&a, &b), lattice.meet(&b, &a));
                
                // Test absorption laws
                assert_eq!(lattice.join(&a, &lattice.meet(&a, &b)), a);
                assert_eq!(lattice.meet(&a, &lattice.join(&a, &b)), a);
                
                for &c in &elements {
                    // Test associativity
                    assert_eq!(
                        lattice.join(&lattice.join(&a, &b), &c),
                        lattice.join(&a, &lattice.join(&b, &c))
                    );
                    assert_eq!(
                        lattice.meet(&lattice.meet(&a, &b), &c),
                        lattice.meet(&a, &lattice.meet(&b, &c))
                    );
                }
            }
        }
    }

    #[test]
    fn test_trait_object_compatibility() {
        let boolean_lattice = BooleanLattice::new();
        let diamond_lattice = DiamondLattice::new();
        
        // Test that we can use trait objects
        let _order1: &dyn Order<bool> = &boolean_lattice;
        let _lattice1: &dyn Lattice<bool> = &boolean_lattice;
        let _small_lattice1: &dyn SmallLattice<bool> = &boolean_lattice;
        
        let _order2: &dyn Order<DiamondElement> = &diamond_lattice;
        let _lattice2: &dyn Lattice<DiamondElement> = &diamond_lattice;
        let _small_lattice2: &dyn SmallLattice<DiamondElement> = &diamond_lattice;
        
        // Test algebra trait objects
        let _algebra1: &dyn Algebra<UniverseItem = bool> = &boolean_lattice;
        let _algebra2: &dyn Algebra<UniverseItem = DiamondElement> = &diamond_lattice;
    }

    #[test]
    fn test_empty_list_operations() {
        let lattice = BooleanLattice::new();
        
        // Empty join should return false (bottom element)
        assert_eq!(lattice.join_list(&[]), false);
        
        // Empty meet should return true (top element)
        assert_eq!(lattice.meet_list(&[]), true);
    }

    #[test]
    fn test_single_element_operations() {
        let lattice = BooleanLattice::new();
        
        // Single element operations
        assert_eq!(lattice.join_list(&[false]), false);
        assert_eq!(lattice.join_list(&[true]), true);
        assert_eq!(lattice.meet_list(&[false]), false);
        assert_eq!(lattice.meet_list(&[true]), true);
    }
}