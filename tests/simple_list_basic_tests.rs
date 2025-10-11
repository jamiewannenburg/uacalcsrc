/*!
 * Basic tests for SimpleList implementation.
 * 
 * This module provides basic unit tests for the SimpleList class.
 */

use uacalc::util::simple_list::SimpleList;
use std::time::Duration;

#[test]
fn test_empty_list_creation() {
    let list = SimpleList::<i32>::new();
    assert!(list.is_empty());
    assert_eq!(list.size(), 0);
    assert!(list.first().is_none());
}

#[test]
fn test_cons_operation() {
    let empty = SimpleList::<i32>::new();
    let list = empty.cons_safe(42).unwrap();
    
    assert!(!list.is_empty());
    assert_eq!(list.size(), 1);
    assert_eq!(*list.first().unwrap(), 42);
}

#[test]
fn test_multiple_cons() {
    let empty = SimpleList::<i32>::new();
    let list = empty.cons_safe(3).unwrap()
                   .cons_safe(2).unwrap()
                   .cons_safe(1).unwrap();
    
    assert_eq!(list.size(), 3);
    assert_eq!(*list.first().unwrap(), 1);
}

#[test]
fn test_append() {
    let list1 = SimpleList::<i32>::new().cons_safe(1).unwrap().cons_safe(2).unwrap();
    let list2 = SimpleList::<i32>::new().cons_safe(3).unwrap().cons_safe(4).unwrap();
    let result = list1.append(&list2);
    
    assert_eq!(result.size(), 4);
}

#[test]
fn test_reverse() {
    let list = SimpleList::<i32>::new().cons_safe(1).unwrap()
                   .cons_safe(2).unwrap()
                   .cons_safe(3).unwrap();
    let reversed = list.reverse();
    
    assert_eq!(reversed.size(), 3);
    // After reversing (3 (2 (1 ()))) becomes (1 (2 (3 ())))
    // The first element should be 1
    assert_eq!(*reversed.first().unwrap(), 1);
}

#[test]
fn test_contains() {
    let list = SimpleList::<i32>::new().cons_safe(1).unwrap()
                   .cons_safe(2).unwrap()
                   .cons_safe(3).unwrap();
    
    assert!(list.contains(&2));
    assert!(!list.contains(&4));
}

#[test]
fn test_get() {
    let list = SimpleList::<i32>::new().cons_safe(1).unwrap()
                   .cons_safe(2).unwrap()
                   .cons_safe(3).unwrap();
    
    // The list is (3 (2 (1 ()))), so indices are 0=3, 1=2, 2=1
    assert_eq!(*list.get_safe(0).unwrap().unwrap(), 3);
    assert_eq!(*list.get_safe(1).unwrap().unwrap(), 2);
    assert_eq!(*list.get_safe(2).unwrap().unwrap(), 1);
}

#[test]
fn test_index_of() {
    let list = SimpleList::<i32>::new().cons_safe(1).unwrap()
                   .cons_safe(2).unwrap()
                   .cons_safe(3).unwrap();
    
    assert_eq!(list.index_of(&2), Some(1));
    assert_eq!(list.index_of(&4), None);
}

#[test]
fn test_sub_list() {
    let list = SimpleList::<i32>::new().cons_safe(1).unwrap()
                   .cons_safe(2).unwrap()
                   .cons_safe(3).unwrap()
                   .cons_safe(4).unwrap();
    
    let sub = list.sub_list_safe(1, 3).unwrap();
    assert_eq!(sub.size(), 2);
}

#[test]
fn test_iterator() {
    let list = SimpleList::<i32>::new().cons_safe(1).unwrap()
                   .cons_safe(2).unwrap()
                   .cons_safe(3).unwrap();
    
    let mut iter = uacalc::util::simple_list::SimpleListIterator::new(list.clone());
    // The list is (3 (2 (1 ()))), so first element is 3
    assert_eq!(iter.next().unwrap(), 3);
    assert_eq!(iter.next().unwrap(), 2);
    assert_eq!(iter.next().unwrap(), 1);
    assert!(iter.next().is_none());
}

#[test]
fn test_from_collection() {
    let vec = vec![1, 2, 3, 4];
    let list = SimpleList::from_collection_safe(&vec).unwrap();
    
    assert_eq!(list.size(), 4);
    assert_eq!(*list.first().unwrap(), 1);
}

#[test]
fn test_equality_and_hashing() {
    let list1 = SimpleList::<&str>::new()
        .cons_safe("a").unwrap()
        .cons_safe("b").unwrap();
    
    let list2 = SimpleList::<&str>::new()
        .cons_safe("a").unwrap()
        .cons_safe("b").unwrap();
    
    // Test equality (should be true for identical structure)
    assert_eq!(list1, list2);
    
    // Test hashing
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    
    let mut hasher1 = DefaultHasher::new();
    let mut hasher2 = DefaultHasher::new();
    
    list1.hash(&mut hasher1);
    list2.hash(&mut hasher2);
    
    assert_eq!(hasher1.finish(), hasher2.finish());
}

#[test]
fn test_ordering() {
    let empty = SimpleList::<&str>::new();
    let list1 = empty.cons_safe("a").unwrap();
    let list2 = empty.cons_safe("a").unwrap().cons_safe("b").unwrap();
    
    // Empty list should be less than non-empty
    assert!(empty < list1);
    assert!(empty < list2);
    
    // Shorter list should be less than longer list
    assert!(list1 < list2);
}

#[test]
fn test_memory_sharing() {
    // Test that lists share memory efficiently
    let base = SimpleList::<&str>::new()
        .cons_safe("x").unwrap()
        .cons_safe("y").unwrap();
    
    let list1 = base.cons_safe("a").unwrap();
    let list2 = base.cons_safe("b").unwrap();
    
    // Both lists should share the same base structure
    assert_eq!(list1.rest().rest(), list2.rest().rest());
    
    // Test that rest() doesn't create new objects unnecessarily
    let rest1 = list1.rest();
    let rest2 = list1.rest();
    assert_eq!(rest1, rest2);
}

#[test]
fn test_edge_cases() {
    // Test operations on empty list
    let empty = SimpleList::<&str>::new();
    
    assert!(empty.is_empty());
    assert_eq!(empty.size(), 0);
    assert!(empty.first().is_none());
    assert_eq!(empty.rest(), empty);
    assert_eq!(empty.reverse(), empty);
    assert_eq!(empty.append(&empty), empty);
    
    // Test single element list
    let single = empty.cons_safe("a").unwrap();
    assert!(!single.is_empty());
    assert_eq!(single.size(), 1);
    assert_eq!(*single.first().unwrap(), "a");
    assert_eq!(single.rest(), empty);
    assert_eq!(single.reverse(), single);
}

#[test]
fn test_performance_characteristics() {
    // Test that size() is O(n) as documented
    let start = std::time::Instant::now();
    
    // Create a moderately large list
    let mut list = SimpleList::<i32>::new();
    for i in (0..1000).rev() {
        list = list.cons_safe(i).unwrap();
    }
    
    let creation_time = start.elapsed();
    
    // Test size() performance
    let start = std::time::Instant::now();
    let size = list.size();
    let size_time = start.elapsed();
    
    assert_eq!(size, 1000);
    
    // Size should complete in reasonable time (less than 1 second for 1000 elements)
    assert!(size_time < Duration::from_secs(1));
    
    // Test get() performance (should be O(n))
    let start = std::time::Instant::now();
    let element = list.get_safe(999).unwrap();
    let get_time = start.elapsed();
    
    assert!(element.is_some());
    assert!(get_time < Duration::from_secs(1));
    
    println!("Creation time: {:?}, Size time: {:?}, Get time: {:?}", 
             creation_time, size_time, get_time);
}
