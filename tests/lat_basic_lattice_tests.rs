/*! Tests for BasicLattice implementation
 *
 * These tests verify the BasicLattice implementation and compare
 * with the Java wrapper output where applicable.
 */

use uacalc::lat::*;
use uacalc::lat::ordered_set::OrderedSet;

#[test]
fn test_ordered_set_creation() {
    // Create a simple 3-element chain: 0 < 1 < 2
    let univ = vec![0, 1, 2];
    let ucs = vec![
        vec![1],      // 0 is covered by 1
        vec![2],      // 1 is covered by 2
        vec![],       // 2 has no upper covers
    ];
    
    let poset = OrderedSet::new(Some("Chain3".to_string()), univ, ucs);
    assert!(poset.is_ok());
    
    let poset = poset.unwrap();
    assert_eq!(poset.univ().len(), 3);
}

#[test]
fn test_ordered_set_leq() {
    // Create a simple 3-element chain: 0 < 1 < 2
    let univ = vec![0, 1, 2];
    let ucs = vec![
        vec![1],
        vec![2],
        vec![],
    ];
    
    let poset = OrderedSet::new(Some("Chain3".to_string()), univ, ucs).unwrap();
    let univ_list = poset.univ();
    
    // Check order relations
    assert!(poset.leq(&univ_list[0], &univ_list[1])); // 0 <= 1
    assert!(poset.leq(&univ_list[1], &univ_list[2])); // 1 <= 2
    assert!(poset.leq(&univ_list[0], &univ_list[2])); // 0 <= 2 (transitivity)
    assert!(!poset.leq(&univ_list[1], &univ_list[0])); // 1 !<= 0
    assert!(!poset.leq(&univ_list[2], &univ_list[0])); // 2 !<= 0
}

#[test]
fn test_basic_lattice_from_poset() {
    // Create a simple 3-element chain: 0 < 1 < 2
    let univ = vec![0, 1, 2];
    let ucs = vec![
        vec![1],
        vec![2],
        vec![],
    ];
    
    let poset = OrderedSet::new(Some("Chain3".to_string()), univ, ucs).unwrap();
    
    let basic_lat = BasicLattice::new_from_poset("TestLattice".to_string(), poset, None);
    assert!(basic_lat.is_ok());
    
    let basic_lat = basic_lat.unwrap();
    assert_eq!(basic_lat.cardinality(), 3);
}

#[test]
fn test_basic_lattice_join_meet() {
    // Create a simple 3-element chain: 0 < 1 < 2
    let univ = vec![0, 1, 2];
    let ucs = vec![
        vec![1],
        vec![2],
        vec![],
    ];
    
    let poset = OrderedSet::new(Some("Chain3".to_string()), univ, ucs).unwrap();
    let basic_lat = BasicLattice::new_from_poset("TestLattice".to_string(), poset, None).unwrap();
    
    let univ_list = basic_lat.get_universe_list();
    assert_eq!(univ_list.len(), 3);
    
    // Test join: join(0, 1) = 1 (least upper bound)
    let join_result = basic_lat.join(&univ_list[0], &univ_list[1]);
    assert_eq!(basic_lat.element_index(&join_result), Some(1));
    
    // Test meet: meet(1, 2) = 1 (greatest lower bound)
    let meet_result = basic_lat.meet(&univ_list[1], &univ_list[2]);
    assert_eq!(basic_lat.element_index(&meet_result), Some(1));
    
    // Test join(0, 2) = 2
    let join_result = basic_lat.join(&univ_list[0], &univ_list[2]);
    assert_eq!(basic_lat.element_index(&join_result), Some(2));
    
    // Test meet(0, 2) = 0
    let meet_result = basic_lat.meet(&univ_list[0], &univ_list[2]);
    assert_eq!(basic_lat.element_index(&meet_result), Some(0));
}

#[test]
fn test_basic_lattice_atoms_coatoms() {
    // Create a simple 3-element chain: 0 < 1 < 2
    let univ = vec![0, 1, 2];
    let ucs = vec![
        vec![1],
        vec![2],
        vec![],
    ];
    
    let poset = OrderedSet::new(Some("Chain3".to_string()), univ, ucs).unwrap();
    let basic_lat = BasicLattice::new_from_poset("TestLattice".to_string(), poset, None).unwrap();
    
    // Atoms are elements covering zero
    let atoms = basic_lat.atoms();
    assert_eq!(atoms.len(), 1);
    assert_eq!(basic_lat.element_index(&atoms[0]), Some(1));
    
    // Coatoms are elements covered by one
    let coatoms = basic_lat.coatoms();
    assert_eq!(coatoms.len(), 1);
    assert_eq!(basic_lat.element_index(&coatoms[0]), Some(1));
}

#[test]
fn test_basic_lattice_join_irreducibles() {
    // Create a simple 3-element chain: 0 < 1 < 2
    let univ = vec![0, 1, 2];
    let ucs = vec![
        vec![1],
        vec![2],
        vec![],
    ];
    
    let poset = OrderedSet::new(Some("Chain3".to_string()), univ, ucs).unwrap();
    let mut basic_lat = BasicLattice::new_from_poset("TestLattice".to_string(), poset, None).unwrap();
    
    // Join irreducibles are elements with exactly one upper cover
    // Use BasicLattice::join_irreducibles() method directly (not trait method)
    use std::sync::Arc;
    use uacalc::lat::ordered_set::POElem;
    let jis = BasicLattice::join_irreducibles(&mut basic_lat);
    // In a chain, all elements except the top are join irreducible
    // Verify we got some join irreducibles
    assert!(!jis.is_empty());
}

#[test]
fn test_basic_lattice_to_graph_data() {
    // Create a simple 3-element chain: 0 < 1 < 2
    let univ = vec![0, 1, 2];
    let ucs = vec![
        vec![1],
        vec![2],
        vec![],
    ];
    
    let poset = OrderedSet::new(Some("Chain3".to_string()), univ, ucs).unwrap();
    let basic_lat = BasicLattice::new_from_poset("TestLattice".to_string(), poset, None).unwrap();
    
    let graph_data = basic_lat.to_graph_data();
    
    // Should have 3 nodes
    assert_eq!(graph_data.nodes.len(), 3);
    
    // Should have 2 edges (0->1 and 1->2)
    assert_eq!(graph_data.edges.len(), 2);
    
    // Check that edges are correct
    let edge_sources: Vec<usize> = graph_data.edges.iter().map(|e| e.source).collect();
    let edge_targets: Vec<usize> = graph_data.edges.iter().map(|e| e.target).collect();
    
    assert!(edge_sources.contains(&0));
    assert!(edge_targets.contains(&1));
    assert!(edge_sources.contains(&1));
    assert!(edge_targets.contains(&2));
}

#[test]
fn test_graph_data_to_dot() {
    // Create a simple 3-element chain: 0 < 1 < 2
    let univ = vec![0, 1, 2];
    let ucs = vec![
        vec![1],
        vec![2],
        vec![],
    ];
    
    let poset = OrderedSet::new(Some("Chain3".to_string()), univ, ucs).unwrap();
    let basic_lat = BasicLattice::new_from_poset("TestLattice".to_string(), poset, None).unwrap();
    
    let graph_data = basic_lat.to_graph_data();
    let dot = graph_data.to_dot();
    
    // DOT format should contain digraph
    assert!(dot.contains("digraph"));
    assert!(dot.contains("Lattice"));
    assert!(dot.contains("rankdir=BT"));
}

#[test]
fn test_graph_data_to_mermaid() {
    // Create a simple 3-element chain: 0 < 1 < 2
    let univ = vec![0, 1, 2];
    let ucs = vec![
        vec![1],
        vec![2],
        vec![],
    ];
    
    let poset = OrderedSet::new(Some("Chain3".to_string()), univ, ucs).unwrap();
    let basic_lat = BasicLattice::new_from_poset("TestLattice".to_string(), poset, None).unwrap();
    
    let graph_data = basic_lat.to_graph_data();
    let mermaid = graph_data.to_mermaid();
    
    // Mermaid format should contain graph TD
    assert!(mermaid.contains("graph TD"));
}

#[test]
fn test_ordered_set_from_filters() {
    // Create filters for a 3-element chain: 0 < 1 < 2
    // Filter of 0: {0, 1, 2} (all elements >= 0)
    // Filter of 1: {1, 2} (all elements >= 1)
    // Filter of 2: {2} (all elements >= 2)
    let univ = vec![0, 1, 2];
    let filters = vec![
        vec![0, 1, 2],
        vec![1, 2],
        vec![2],
    ];
    
    let poset = OrderedSet::ordered_set_from_filters(Some("Chain3".to_string()), univ, filters);
    assert!(poset.is_ok());
    
    let poset = poset.unwrap();
    let univ_list = poset.univ();
    
    // Check that order is correct
    assert!(poset.leq(&univ_list[0], &univ_list[1]));
    assert!(poset.leq(&univ_list[1], &univ_list[2]));
}

