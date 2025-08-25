use uacalc_core::prelude::*;

#[test]
fn test_bitset_operations() {
    let size = 4;
    let mut rel1 = BasicBinaryRelation::new(size);
    let mut rel2 = BasicBinaryRelation::new(size);
    
    // Set up relations
    rel1.add(0, 1).unwrap();
    rel1.add(1, 2).unwrap();
    rel1.add(2, 3).unwrap();
    
    rel2.add(1, 2).unwrap();
    rel2.add(2, 3).unwrap();
    rel2.add(3, 0).unwrap();
    
    // Test efficient union
    let union = rel1.union_efficient(&rel2).unwrap();
    assert!(union.contains(0, 1).unwrap());
    assert!(union.contains(1, 2).unwrap());
    assert!(union.contains(2, 3).unwrap());
    assert!(union.contains(3, 0).unwrap());
    
    // Test efficient intersection
    let intersection = rel1.intersection_efficient(&rel2).unwrap();
    assert!(!intersection.contains(0, 1).unwrap());
    assert!(intersection.contains(1, 2).unwrap());
    assert!(intersection.contains(2, 3).unwrap());
    assert!(!intersection.contains(3, 0).unwrap());
    
    // Test matrix multiplication for composition
    let composition = rel1.matrix_multiply(&rel2).unwrap();
    assert!(composition.contains(0, 2).unwrap()); // 0->1->2
    assert!(composition.contains(1, 3).unwrap()); // 1->2->3
    assert!(!composition.contains(0, 0).unwrap());
}

#[test]
fn test_closure_algorithms() {
    let size = 4;
    let mut relation = BasicBinaryRelation::new(size);
    
    // Create a relation: 0->1->2->3
    relation.add(0, 1).unwrap();
    relation.add(1, 2).unwrap();
    relation.add(2, 3).unwrap();
    
    // Test reflexive closure
    let reflexive = relation.reflexive_closure_owned().unwrap();
    assert!(reflexive.contains(0, 0).unwrap());
    assert!(reflexive.contains(1, 1).unwrap());
    assert!(reflexive.contains(2, 2).unwrap());
    assert!(reflexive.contains(3, 3).unwrap());
    assert!(reflexive.contains(0, 1).unwrap());
    
    // Test symmetric closure
    let symmetric = relation.symmetric_closure_owned().unwrap();
    assert!(symmetric.contains(0, 1).unwrap());
    assert!(symmetric.contains(1, 0).unwrap());
    assert!(symmetric.contains(1, 2).unwrap());
    assert!(symmetric.contains(2, 1).unwrap());
    assert!(!symmetric.contains(0, 2).unwrap()); // Not directly connected
    
    // Test transitive closure using Warshall's algorithm
    let transitive = relation.transitive_closure_owned().unwrap();
    assert!(transitive.contains(0, 1).unwrap());
    assert!(transitive.contains(0, 2).unwrap()); // 0->1->2
    assert!(transitive.contains(0, 3).unwrap()); // 0->1->2->3
    assert!(transitive.contains(1, 3).unwrap()); // 1->2->3
    assert!(!transitive.contains(1, 0).unwrap()); // No reverse path
    
    // Test equivalence closure
    let equivalence = relation.equivalence_closure_owned().unwrap();
    assert!(equivalence.contains(0, 0).unwrap()); // Reflexive
    assert!(equivalence.contains(0, 1).unwrap());
    assert!(equivalence.contains(1, 0).unwrap()); // Symmetric
    assert!(equivalence.contains(0, 3).unwrap()); // Transitive
    assert!(equivalence.contains(3, 0).unwrap()); // Symmetric
}

#[test]
fn test_relation_properties() {
    let size = 3;
    
    // Test reflexive relation
    let reflexive = BasicBinaryRelation::identity(size);
    assert!(reflexive.is_reflexive().unwrap());
    assert!(!reflexive.is_symmetric().unwrap());
    assert!(reflexive.is_transitive().unwrap());
    assert!(!reflexive.is_equivalence().unwrap());
    
    // Test symmetric relation
    let mut symmetric = BasicBinaryRelation::new(size);
    symmetric.add(0, 1).unwrap();
    symmetric.add(1, 0).unwrap();
    symmetric.add(1, 2).unwrap();
    symmetric.add(2, 1).unwrap();
    assert!(!symmetric.is_reflexive().unwrap());
    assert!(symmetric.is_symmetric().unwrap());
    assert!(!symmetric.is_transitive().unwrap());
    assert!(!symmetric.is_equivalence().unwrap());
    
    // Test transitive relation
    let mut transitive = BasicBinaryRelation::new(size);
    transitive.add(0, 1).unwrap();
    transitive.add(1, 2).unwrap();
    transitive.add(0, 2).unwrap(); // Explicitly add transitive closure
    assert!(!transitive.is_reflexive().unwrap());
    assert!(!transitive.is_symmetric().unwrap());
    assert!(transitive.is_transitive().unwrap());
    assert!(!transitive.is_equivalence().unwrap());
    
    // Test equivalence relation
    let mut equivalence = BasicBinaryRelation::new(size);
    equivalence.add(0, 0).unwrap();
    equivalence.add(1, 1).unwrap();
    equivalence.add(2, 2).unwrap();
    equivalence.add(0, 1).unwrap();
    equivalence.add(1, 0).unwrap();
    equivalence.add(1, 2).unwrap();
    equivalence.add(2, 1).unwrap();
    equivalence.add(0, 2).unwrap();
    equivalence.add(2, 0).unwrap();
    assert!(equivalence.is_reflexive().unwrap());
    assert!(equivalence.is_symmetric().unwrap());
    assert!(equivalence.is_transitive().unwrap());
    assert!(equivalence.is_equivalence().unwrap());
}

#[test]
fn test_conversion_operations() {
    let size = 4;
    
    // Create a partition
    let mut partition = BasicPartition::new(size).unwrap();
    partition.union_elements(0, 1).unwrap();
    partition.union_elements(2, 3).unwrap();
    
    // Convert partition to binary relation
    let relation = BasicBinaryRelation::from_partition(&partition).unwrap();
    assert!(relation.is_equivalence().unwrap());
    assert!(relation.contains(0, 1).unwrap());
    assert!(relation.contains(1, 0).unwrap());
    assert!(relation.contains(2, 3).unwrap());
    assert!(relation.contains(3, 2).unwrap());
    assert!(!relation.contains(0, 2).unwrap());
    
    // Convert back to partition
    let partition2 = relation.to_partition().unwrap();
    assert_eq!(partition2.num_blocks(), 2);
    assert!(partition2.same_block(0, 1).unwrap());
    assert!(partition2.same_block(2, 3).unwrap());
    assert!(!partition2.same_block(0, 2).unwrap());
}

#[test]
fn test_relation_creation() {
    let size = 3;
    
    // Test identity relation
    let identity = BasicBinaryRelation::identity(size);
    assert_eq!(identity.size(), size);
    assert!(identity.contains(0, 0).unwrap());
    assert!(identity.contains(1, 1).unwrap());
    assert!(identity.contains(2, 2).unwrap());
    assert!(!identity.contains(0, 1).unwrap());
    
    // Test universal relation
    let universal = BasicBinaryRelation::universal(size);
    assert_eq!(universal.size(), size);
    for i in 0..size {
        for j in 0..size {
            assert!(universal.contains(i, j).unwrap());
        }
    }
    
    // Test empty relation
    let empty = BasicBinaryRelation::empty(size);
    assert_eq!(empty.size(), size);
    for i in 0..size {
        for j in 0..size {
            assert!(!empty.contains(i, j).unwrap());
        }
    }
    
    // Test from pairs
    let pairs = vec![(0, 1), (1, 2), (2, 0)];
    let relation = BasicBinaryRelation::from_pairs(size, pairs).unwrap();
    assert!(relation.contains(0, 1).unwrap());
    assert!(relation.contains(1, 2).unwrap());
    assert!(relation.contains(2, 0).unwrap());
    assert!(!relation.contains(0, 0).unwrap());
}

#[test]
fn test_relation_iteration() {
    let size = 3;
    let mut relation = BasicBinaryRelation::new(size);
    relation.add(0, 1).unwrap();
    relation.add(1, 2).unwrap();
    relation.add(2, 0).unwrap();
    
    // Test pairs iteration
    let pairs: Vec<_> = relation.iter_pairs().collect();
    assert_eq!(pairs.len(), 3);
    assert!(pairs.contains(&(0, 1)));
    assert!(pairs.contains(&(1, 2)));
    assert!(pairs.contains(&(2, 0)));
    
    // Test rows iteration
    let rows: Vec<Vec<bool>> = relation.rows().map(|row| row.collect()).collect();
    assert_eq!(rows.len(), 3);
    assert_eq!(rows[0], vec![false, true, false]);
    assert_eq!(rows[1], vec![false, false, true]);
    assert_eq!(rows[2], vec![true, false, false]);
    
    // Test columns iteration
    let columns: Vec<Vec<bool>> = relation.columns().map(|col| col.collect()).collect();
    assert_eq!(columns.len(), 3);
    assert_eq!(columns[0], vec![false, false, true]);
    assert_eq!(columns[1], vec![true, false, false]);
    assert_eq!(columns[2], vec![false, true, false]);
}

#[test]
fn test_bulk_operations() {
    let size = 4;
    let mut relation = BasicBinaryRelation::new(size);
    
    let pairs = vec![(0, 1), (1, 2), (2, 3), (3, 0)];
    
    // Test add_all
    relation.add_all(&pairs).unwrap();
    assert!(relation.contains_all(&pairs).unwrap());
    
    // Test contains_all
    assert!(relation.contains_all(&[(0, 1), (1, 2)]).unwrap());
    assert!(!relation.contains_all(&[(0, 1), (0, 2)]).unwrap()); // (0, 2) not in relation
}

#[test]
fn test_relation_composition() {
    let size = 3;
    let mut rel1 = BasicBinaryRelation::new(size);
    let mut rel2 = BasicBinaryRelation::new(size);
    
    // R1: 0->1, 1->2
    rel1.add(0, 1).unwrap();
    rel1.add(1, 2).unwrap();
    
    // R2: 1->0, 2->1
    rel2.add(1, 0).unwrap();
    rel2.add(2, 1).unwrap();
    
    // Test composition
    let composition = rel1.composition(&rel2).unwrap();
    assert!(composition.contains(0, 0).unwrap()); // 0->1->0
    assert!(composition.contains(1, 1).unwrap()); // 1->2->1
    assert!(!composition.contains(0, 1).unwrap());
    assert!(!composition.contains(1, 0).unwrap());
    
    // Test efficient composition
    let efficient_composition = rel1.composition_efficient(&rel2).unwrap();
    assert_eq!(composition.pairs(), efficient_composition.pairs());
}

#[test]
fn test_relation_union_intersection() {
    let size = 3;
    let mut rel1 = BasicBinaryRelation::new(size);
    let mut rel2 = BasicBinaryRelation::new(size);
    
    rel1.add(0, 1).unwrap();
    rel1.add(1, 2).unwrap();
    
    rel2.add(1, 2).unwrap();
    rel2.add(2, 0).unwrap();
    
    // Test union
    let union = rel1.union(&rel2).unwrap();
    assert!(union.contains(0, 1).unwrap());
    assert!(union.contains(1, 2).unwrap());
    assert!(union.contains(2, 0).unwrap());
    
    // Test intersection
    let intersection = rel1.intersection(&rel2).unwrap();
    assert!(!intersection.contains(0, 1).unwrap());
    assert!(intersection.contains(1, 2).unwrap());
    assert!(!intersection.contains(2, 0).unwrap());
    
    // Test efficient operations
    let efficient_union = rel1.union_efficient(&rel2).unwrap();
    let efficient_intersection = rel1.intersection_efficient(&rel2).unwrap();
    
    assert_eq!(union.pairs(), efficient_union.pairs());
    assert_eq!(intersection.pairs(), efficient_intersection.pairs());
}

#[test]
fn test_relation_performance() {
    let size = 100;
    let mut relation = BasicBinaryRelation::new(size);
    
    // Add many pairs
    let start = std::time::Instant::now();
    for i in 0..size {
        for j in 0..size {
            if (i + j) % 2 == 0 {
                relation.add(i, j).unwrap();
            }
        }
    }
    let add_time = start.elapsed();
    
    // Test transitive closure performance
    let start = std::time::Instant::now();
    let closure = relation.transitive_closure_owned().unwrap();
    let closure_time = start.elapsed();
    
    println!("Adding pairs: {:?}", add_time);
    println!("Transitive closure: {:?}", closure_time);
    
    // Verify closure is transitive
    assert!(closure.is_transitive().unwrap());
}

#[test]
fn test_relation_serialization() {
    let size = 3;
    let mut relation = BasicBinaryRelation::new(size);
    relation.add(0, 1).unwrap();
    relation.add(1, 2).unwrap();
    relation.add(2, 0).unwrap();
    
    // Test serialization
    let serialized = serde_json::to_string(&relation).unwrap();
    let deserialized: BasicBinaryRelation = serde_json::from_str(&serialized).unwrap();
    
    // Verify deserialized relation works correctly
    assert_eq!(deserialized.size(), size);
    assert!(deserialized.contains(0, 1).unwrap());
    assert!(deserialized.contains(1, 2).unwrap());
    assert!(deserialized.contains(2, 0).unwrap());
    assert!(!deserialized.contains(0, 0).unwrap());
}

#[test]
fn test_relation_error_handling() {
    let size = 3;
    let relation = BasicBinaryRelation::new(size);
    
    // Test out of bounds access
    assert!(relation.contains(3, 0).is_err());
    assert!(relation.contains(0, 3).is_err());
    assert!(relation.contains(3, 3).is_err());
    
    let mut relation = relation;
    assert!(relation.add(3, 0).is_err());
    assert!(relation.remove(3, 0).is_err());
    
    // Test operations with different sizes
    let other = BasicBinaryRelation::new(4);
    assert!(relation.union(&other).is_err());
    assert!(relation.intersection(&other).is_err());
    assert!(relation.composition(&other).is_err());
}

#[test]
fn test_relation_edge_cases() {
    // Test empty relation
    let empty = BasicBinaryRelation::new(0);
    assert_eq!(empty.size(), 0);
    assert!(empty.pairs().is_empty());
    
    // Test single element relation
    let single = BasicBinaryRelation::new(1);
    assert_eq!(single.size(), 1);
    assert!(!single.contains(0, 0).unwrap());
    
    let mut single = single;
    single.add(0, 0).unwrap();
    assert!(single.contains(0, 0).unwrap());
    assert!(single.is_reflexive().unwrap());
    assert!(single.is_symmetric().unwrap());
    assert!(single.is_transitive().unwrap());
    assert!(single.is_equivalence().unwrap());
}

#[test]
fn test_relation_complex_scenarios() {
    let size = 5;
    let mut relation = BasicBinaryRelation::new(size);
    
    // Create a complex relation with cycles
    relation.add(0, 1).unwrap();
    relation.add(1, 2).unwrap();
    relation.add(2, 3).unwrap();
    relation.add(3, 4).unwrap();
    relation.add(4, 0).unwrap(); // Creates a cycle
    
    // Test transitive closure with cycle
    let closure = relation.transitive_closure_owned().unwrap();
    assert!(closure.contains(0, 0).unwrap()); // 0->1->2->3->4->0
    assert!(closure.contains(1, 1).unwrap()); // 1->2->3->4->0->1
    assert!(closure.contains(2, 2).unwrap()); // 2->3->4->0->1->2
    
    // Test equivalence closure
    let equivalence = relation.equivalence_closure_owned().unwrap();
    assert!(equivalence.is_equivalence().unwrap());
    
    // All elements should be in the same equivalence class due to the cycle
    for i in 0..size {
        for j in 0..size {
            assert!(equivalence.contains(i, j).unwrap());
        }
    }
}

#[test]
fn test_relation_java_compatibility() {
    let size = 4;
    let mut relation = BasicBinaryRelation::new(size);
    relation.add(0, 1).unwrap();
    relation.add(1, 2).unwrap();
    relation.add(2, 3).unwrap();
    
    // Test Java-compatible method names
    assert!(relation.is_related(0, 1).unwrap());
    assert!(!relation.is_related(0, 2).unwrap());
    
    let pairs = relation.get_pairs();
    assert_eq!(pairs.len(), 3);
    assert!(pairs.contains(&(0, 1)));
    assert!(pairs.contains(&(1, 2)));
    assert!(pairs.contains(&(2, 3)));
    
    // Test composition with Java-compatible method name
    let mut rel2 = BasicBinaryRelation::new(size);
    rel2.add(1, 0).unwrap();
    rel2.add(2, 1).unwrap();
    rel2.add(3, 2).unwrap();
    
    let composition = relation.compose(&rel2).unwrap();
    assert!(composition.contains(0, 0).unwrap()); // 0->1->0
    assert!(composition.contains(1, 1).unwrap()); // 1->2->1
    assert!(composition.contains(2, 2).unwrap()); // 2->3->2
}
