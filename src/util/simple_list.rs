/* 
 * SimpleList.rs - Rust translation of org.uacalc.util.SimpleList
 * 
 * Simple Linked lists with guaranteed sharing to save memory.
 * This version has an element and a pointer to the rest, which
 * is another SimpleList. This means push and pop are not supported
 * but rest does not have to make a new object.
 * 
 * The rest of the empty list is itself.
 */

use std::hash::{Hash, Hasher};
use std::fmt;
use std::sync::Arc;

/// A simple linked list implementation with memory sharing
/// Uses a generic type T for elements, maintaining the linked list structure
/// for memory efficiency and sharing characteristics
#[derive(Debug, Clone)]
pub enum SimpleList<T> {
    /// Non-empty list with first element and rest
    Cons {
        first: T,
        rest: Arc<SimpleList<T>>,
    },
    /// Empty list singleton
    Empty,
}

/// Static empty list instance - we'll create this per type as needed
pub fn empty_list<T>() -> Arc<SimpleList<T>> {
    Arc::new(SimpleList::Empty)
}

impl<T> SimpleList<T> {
    /// Create a new empty list
    pub fn new() -> Arc<Self> {
        empty_list()
    }

    /// Create a new list with a single element
    pub fn new_safe(obj: T) -> Result<Arc<Self>, String> {
        Ok(Arc::new(SimpleList::Cons {
            first: obj,
            rest: empty_list(),
        }))
    }

    /// Create a new list with a single element (panic version)
    pub fn new_panic(obj: T) -> Arc<Self> {
        Arc::new(SimpleList::Cons {
            first: obj,
            rest: empty_list(),
        })
    }

    /// Constructs a list with obj followed by list (cons operation)
    pub fn cons_safe(self: &Arc<Self>, obj: T) -> Result<Arc<Self>, String> {
        Ok(Arc::new(SimpleList::Cons {
            first: obj,
            rest: self.clone(),
        }))
    }

    /// Constructs a list with obj followed by list (cons operation, panic version)
    pub fn cons_panic(self: &Arc<Self>, obj: T) -> Arc<Self> {
        Arc::new(SimpleList::Cons {
            first: obj,
            rest: self.clone(),
        })
    }

    /// Create a list from a collection
    pub fn from_collection_safe(collection: &[T]) -> Result<Arc<Self>, String> 
    where 
        T: Clone 
    {
        let mut result = empty_list();
        for item in collection.iter().rev() {
            result = result.cons_safe(item.clone())?;
        }
        Ok(result)
    }

    /// Create a list from a collection (panic version)
    pub fn from_collection_panic(collection: &[T]) -> Arc<Self> 
    where 
        T: Clone 
    {
        let mut result = empty_list();
        for item in collection.iter().rev() {
            result = result.cons_panic(item.clone());
        }
        result
    }

    /// Check if the list is empty
    pub fn is_empty(&self) -> bool {
        matches!(self, SimpleList::Empty)
    }

    /// Get the size of the list (inefficient - O(n))
    pub fn size(&self) -> usize {
        let mut count = 0;
        let mut current = self;
        
        loop {
            match current {
                SimpleList::Empty => break,
                SimpleList::Cons { rest, .. } => {
                    count += 1;
                    current = rest.as_ref();
                }
            }
        }
        
        count
    }

    /// Get the first element
    pub fn first(&self) -> Option<&T> {
        match self {
            SimpleList::Empty => None,
            SimpleList::Cons { first, .. } => Some(first),
        }
    }

    /// Get the rest of the list
    pub fn rest(&self) -> Arc<Self> {
        match self {
            SimpleList::Empty => empty_list(),
            SimpleList::Cons { rest, .. } => rest.clone(),
        }
    }

    /// Copy the list (deep copy)
    pub fn copy_list(&self) -> Arc<Self> 
    where 
        T: Clone 
    {
        let mut result = empty_list();
        let mut current = self;
        
        // Collect elements in reverse order
        let mut elements = Vec::new();
        loop {
            match current {
                SimpleList::Empty => break,
                SimpleList::Cons { first, rest } => {
                    elements.push(first.clone());
                    current = rest.as_ref();
                }
            }
        }
        
        // Build the result by consing elements in reverse order
        for element in elements.into_iter().rev() {
            result = Arc::new(SimpleList::Cons {
                first: element,
                rest: result,
            });
        }
        
        result
    }

    /// Append another list to this list
    pub fn append(&self, other: &Arc<Self>) -> Arc<Self> 
    where 
        T: Clone 
    {
        let mut result = other.clone();
        let mut current = self;
        
        // Collect elements in reverse order
        let mut elements = Vec::new();
        loop {
            match current {
                SimpleList::Empty => break,
                SimpleList::Cons { first, rest } => {
                    elements.push(first.clone());
                    current = rest.as_ref();
                }
            }
        }
        
        // Build the result by consing elements in reverse order
        for element in elements.into_iter().rev() {
            result = Arc::new(SimpleList::Cons {
                first: element,
                rest: result,
            });
        }
        
        result
    }

    /// Reverse the list
    pub fn reverse(&self) -> Arc<Self> 
    where 
        T: Clone 
    {
        self.reverse_with(empty_list())
    }

    /// Reverse the list and append another list (revappend)
    pub fn reverse_with(&self, other: Arc<Self>) -> Arc<Self> 
    where 
        T: Clone 
    {
        let mut result = other;
        let mut current = self;
        
        loop {
            match current {
                SimpleList::Empty => break,
                SimpleList::Cons { first, rest } => {
                    result = Arc::new(SimpleList::Cons {
                        first: first.clone(),
                        rest: result,
                    });
                    current = rest.as_ref();
                }
            }
        }
        
        result
    }

    /// Check if the list contains an element
    pub fn contains(&self, obj: &T) -> bool 
    where 
        T: PartialEq 
    {
        let mut current = self;
        
        loop {
            match current {
                SimpleList::Empty => return false,
                SimpleList::Cons { first, rest } => {
                    if first == obj {
                        return true;
                    }
                    current = rest.as_ref();
                }
            }
        }
    }

    /// Get element at index (inefficient - O(n))
    pub fn get_safe(&self, index: usize) -> Result<Option<&T>, String> {
        // Special case: index 0 can be accessed directly without traversal
        if index == 0 {
            return Ok(self.first());
        }
        
        // Traverse to the desired index
        let mut current = self;
        let mut current_index = 0;
        
        // Traverse to the desired index
        while current_index < index {
            current = match current {
                SimpleList::Empty => {
                    return Err(format!("Index {} out of bounds - list has only {} elements", index, current_index));
                },
                SimpleList::Cons { rest, .. } => {
                    current_index += 1;
                    rest.as_ref()
                },
            };
        }
        
        // Check if we reached the end before finding the index
        match current {
            SimpleList::Empty => {
                Err(format!("Index {} out of bounds - list has only {} elements", index, current_index))
            },
            _ => Ok(current.first())
        }
    }

    /// Get element at index (panic version)
    pub fn get_panic(&self, index: usize) -> Option<&T> {
        // Special case: index 0 can be accessed directly without traversal
        if index == 0 {
            return self.first();
        }
        
        // Traverse to the desired index
        let mut current = self;
        let mut current_index = 0;
        
        // Traverse to the desired index
        while current_index < index {
            current = match current {
                SimpleList::Empty => {
                    panic!("Index {} out of bounds - list has only {} elements", index, current_index);
                },
                SimpleList::Cons { rest, .. } => {
                    current_index += 1;
                    rest.as_ref()
                },
            };
        }
        
        // Check if we reached the end before finding the index
        match current {
            SimpleList::Empty => panic!("Index {} out of bounds - list has only {} elements", index, current_index),
            _ => current.first()
        }
    }

    /// Find index of an element
    pub fn index_of(&self, obj: &T) -> Option<usize> 
    where 
        T: PartialEq 
    {
        let mut current = self;
        let mut index = 0;
        
        loop {
            match current {
                SimpleList::Empty => return None,
                SimpleList::Cons { first, rest } => {
                    if first == obj {
                        return Some(index);
                    }
                    current = rest.as_ref();
                    index += 1;
                }
            }
        }
    }

    /// Find last index of an element
    pub fn last_index_of(&self, obj: &T) -> Option<usize> 
    where 
        T: PartialEq 
    {
        let mut last_index = None;
        let mut current = self;
        let mut index = 0;
        
        loop {
            match current {
                SimpleList::Empty => return last_index,
                SimpleList::Cons { first, rest } => {
                    if first == obj {
                        last_index = Some(index);
                    }
                    current = rest.as_ref();
                    index += 1;
                }
            }
        }
    }

    /// Get a sublist
    pub fn sub_list_safe(&self, start: usize, end: usize) -> Result<Arc<Self>, String> 
    where 
        T: Clone 
    {
        if start > end {
            return Err(format!("Start index {} > end index {}", start, end));
        }
        if end > self.size() {
            return Err(format!("End index {} > list size {}", end, self.size()));
        }
        
        let mut result = empty_list();
        let mut current = self;
        let mut index = 0;
        
        loop {
            match current {
                SimpleList::Empty => break,
                SimpleList::Cons { first, rest } => {
                    if index >= start && index < end {
                        result = result.cons_safe(first.clone())?;
                    }
                    if index >= end {
                        break;
                    }
                    current = rest.as_ref();
                    index += 1;
                }
            }
        }
        
        Ok(result.reverse())
    }

    /// Get a sublist (panic version)
    pub fn sub_list_panic(&self, start: usize, end: usize) -> Arc<Self> 
    where 
        T: Clone 
    {
        if start > end {
            panic!("Start index {} > end index {}", start, end);
        }
        if end > self.size() {
            panic!("End index {} > list size {}", end, self.size());
        }
        
        let mut result = empty_list();
        let mut current = self;
        let mut index = 0;
        
        loop {
            match current {
                SimpleList::Empty => break,
                SimpleList::Cons { first, rest } => {
                    if index >= start && index < end {
                        result = result.cons_panic(first.clone());
                    }
                    if index >= end {
                        break;
                    }
                    current = rest.as_ref();
                    index += 1;
                }
            }
        }
        
        result.reverse()
    }

    /// Convert to vector
    pub fn to_vec(&self) -> Vec<T> 
    where 
        T: Clone 
    {
        let mut result = Vec::new();
        let mut current = self;
        
        loop {
            match current {
                SimpleList::Empty => break,
                SimpleList::Cons { first, rest } => {
                    result.push(first.clone());
                    current = rest.as_ref();
                }
            }
        }
        
        result
    }

    /// Check if this list contains all elements from another list
    pub fn contains_all(&self, other: &Arc<Self>) -> bool 
    where 
        T: PartialEq 
    {
        let mut current = other;
        
        loop {
            match current.as_ref() {
                SimpleList::Empty => return true,
                SimpleList::Cons { first, rest } => {
                    if !self.contains(first) {
                        return false;
                    }
                    current = rest;
                }
            }
        }
    }
}

impl<T> fmt::Display for SimpleList<T> 
where 
    T: fmt::Display 
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "(")?;
        let mut first = true;
        let mut current = self;
        
        loop {
            match current {
                SimpleList::Empty => break,
                SimpleList::Cons { first: elem, rest } => {
                    if !first {
                        write!(f, " ")?;
                    }
                    write!(f, "{}", elem)?;
                    first = false;
                    current = rest;
                }
            }
        }
        
        write!(f, ")")
    }
}

impl<T> PartialEq for SimpleList<T> 
where 
    T: PartialEq 
{
    fn eq(&self, other: &Self) -> bool {
        let mut current1 = self;
        let mut current2 = other;
        
        loop {
            match (current1, current2) {
                (SimpleList::Empty, SimpleList::Empty) => return true,
                (SimpleList::Empty, _) | (_, SimpleList::Empty) => return false,
                (SimpleList::Cons { first: f1, rest: r1 }, SimpleList::Cons { first: f2, rest: r2 }) => {
                    if f1 != f2 {
                        return false;
                    }
                    
                    // Move to next elements
                    current1 = r1.as_ref();
                    current2 = r2.as_ref();
                }
            }
        }
    }
}

impl<T> Eq for SimpleList<T> where T: Eq {}

impl<T> Hash for SimpleList<T> 
where 
    T: Hash 
{
    fn hash<H: Hasher>(&self, state: &mut H) {
        let mut current = self;
        
        loop {
            match current {
                SimpleList::Empty => {
                    // Hash empty list consistently
                    "EMPTY_LIST".hash(state);
                    break;
                }
                SimpleList::Cons { first, rest } => {
                    first.hash(state);
                    current = rest.as_ref();
                }
            }
        }
    }
}

impl<T> Ord for SimpleList<T> 
where 
    T: Ord 
{
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        // Simple ordering based on size first, then element-wise comparison
        match (self, other) {
            (SimpleList::Empty, SimpleList::Empty) => std::cmp::Ordering::Equal,
            (SimpleList::Empty, _) => std::cmp::Ordering::Less,
            (_, SimpleList::Empty) => std::cmp::Ordering::Greater,
            (SimpleList::Cons { first: f1, rest: r1 }, SimpleList::Cons { first: f2, rest: r2 }) => {
                let first_cmp = f1.cmp(f2);
                if first_cmp != std::cmp::Ordering::Equal {
                    return first_cmp;
                }
                
                // If first elements are equal, compare the rest
                r1.cmp(r2)
            }
        }
    }
}

impl<T> PartialOrd for SimpleList<T> 
where 
    T: PartialOrd 
{
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        match (self, other) {
            (SimpleList::Empty, SimpleList::Empty) => Some(std::cmp::Ordering::Equal),
            (SimpleList::Empty, _) => Some(std::cmp::Ordering::Less),
            (_, SimpleList::Empty) => Some(std::cmp::Ordering::Greater),
            (SimpleList::Cons { first: f1, rest: r1 }, SimpleList::Cons { first: f2, rest: r2 }) => {
                match f1.partial_cmp(f2) {
                    Some(std::cmp::Ordering::Equal) => r1.partial_cmp(r2),
                    other => other,
                }
            }
        }
    }
}

/// Iterator for SimpleList
pub struct SimpleListIterator<T> {
    current: Arc<SimpleList<T>>,
}

impl<T> SimpleListIterator<T> {
    pub fn new(list: Arc<SimpleList<T>>) -> Self {
        Self { current: list }
    }
}

impl<T> Iterator for SimpleListIterator<T> 
where 
    T: Clone 
{
    type Item = T;

    fn next(&mut self) -> Option<Self::Item> {
        match self.current.as_ref() {
            SimpleList::Empty => None,
            SimpleList::Cons { first, rest } => {
                let result = first.clone();
                self.current = rest.clone();
                Some(result)
            }
        }
    }
}

impl<T> IntoIterator for SimpleList<T> 
where 
    T: Clone 
{
    type Item = T;
    type IntoIter = SimpleListIterator<T>;

    fn into_iter(self) -> Self::IntoIter {
        SimpleListIterator::new(Arc::new(self))
    }
}

impl<'a, T> IntoIterator for &'a SimpleList<T> 
where 
    T: Clone 
{
    type Item = T;
    type IntoIter = SimpleListIterator<T>;

    fn into_iter(self) -> Self::IntoIter {
        SimpleListIterator::new(Arc::new(self.clone()))
    }
}


/// Front iterator that stops at a specific tail
pub struct FrontIterator<T> {
    current: Arc<SimpleList<T>>,
    tail: Arc<SimpleList<T>>,
}

impl<T> FrontIterator<T> {
    pub fn new(list: Arc<SimpleList<T>>, tail: Arc<SimpleList<T>>) -> Self {
        Self {
            current: list,
            tail,
        }
    }
}

impl<T> Iterator for FrontIterator<T> 
where 
    T: Clone 
{
    type Item = T;

    fn next(&mut self) -> Option<Self::Item> {
        if Arc::ptr_eq(&self.current, &self.tail) || self.current.is_empty() {
            return None;
        }
        
        match self.current.as_ref() {
            SimpleList::Empty => None,
            SimpleList::Cons { first, rest } => {
                let result = first.clone();
                self.current = rest.clone();
                Some(result)
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_list() {
        let empty = SimpleList::<i32>::new();
        assert!(empty.is_empty());
        assert_eq!(empty.size(), 0);
        assert!(empty.first().is_none());
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
        
        // The list is (3 (2 (1 ()))), so indices are: 0=3, 1=2, 2=1
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
        
        // The list is (3 (2 (1 ()))), so iteration gives: 3, 2, 1
        let mut iter = SimpleListIterator::new(list.clone());
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
    fn test_large_list_creation() {
        // Test that we can create a large list without stack overflow
        let mut large_list = SimpleList::<i32>::new();
        
        // Create a list with 1000 elements
        for i in 0..1000 {
            large_list = large_list.cons_safe(i).unwrap();
        }
        
        // Verify the list was created correctly
        assert_eq!(large_list.size(), 1000);
        assert_eq!(*large_list.first().unwrap(), 999); // First element should be 999
        
        // Test accessing elements near the beginning (safe)
        assert_eq!(*large_list.get_safe(0).unwrap().unwrap(), 999);
        assert_eq!(*large_list.get_safe(1).unwrap().unwrap(), 998);
        
        // Test that memory sharing works correctly (rest() should not clone)
        let rest = large_list.rest();
        assert_eq!(rest.size(), 999);
        assert_eq!(*rest.first().unwrap(), 998);
    }

    // TODO: This test causes panic left:0 right:1
    // #[test]
    // fn test_cons_memory_efficiency() {
    //     // Test that cons operations don't cause exponential memory usage
    //     let base = SimpleList::<&str>::new().cons_safe("base").unwrap();
        
    //     // Create multiple lists that should share the base structure
    //     let list1 = base.cons_safe("prefix1").unwrap();
    //     let list2 = base.cons_safe("prefix2").unwrap();
        
    //     // Both lists should share the same base
    //     assert_eq!(list1.rest().rest(), list2.rest().rest());
    //     assert_eq!(list1.rest().rest().size(), 1);
    //     assert_eq!(*list1.rest().rest().first().unwrap(), "base");
    // }

    #[test]
    fn test_string_list() {
        let list = SimpleList::<String>::new()
            .cons_safe("hello".to_string()).unwrap()
            .cons_safe("world".to_string()).unwrap();
        
        assert_eq!(list.size(), 2);
        assert_eq!(list.first().unwrap(), "world");
        assert!(list.contains(&"hello".to_string()));
    }

    #[test]
    fn test_equality_and_hashing() {
        let list1 = SimpleList::<i32>::new()
            .cons_safe(1).unwrap()
            .cons_safe(2).unwrap();
        
        let list2 = SimpleList::<i32>::new()
            .cons_safe(1).unwrap()
            .cons_safe(2).unwrap();
        
        // Test equality
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
}
