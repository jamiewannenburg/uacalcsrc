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
use once_cell::sync::Lazy;

/// A simple linked list implementation with memory sharing
#[derive(Debug, Clone)]
pub enum SimpleList {
    /// Non-empty list with first element and rest
    Cons {
        first: Arc<dyn std::any::Any + Send + Sync>,
        rest: Arc<SimpleList>,
    },
    /// Empty list singleton
    Empty,
}

/// Static empty list instance
pub static EMPTY_LIST: Lazy<Arc<SimpleList>> = Lazy::new(|| Arc::new(SimpleList::Empty));

impl SimpleList {
    /// Create a new empty list
    pub fn new() -> Arc<Self> {
        EMPTY_LIST.clone()
    }

    /// Create a new list with a single element
    pub fn new_safe<T: 'static + Send + Sync>(obj: T) -> Result<Arc<Self>, String> {
        Ok(Arc::new(SimpleList::Cons {
            first: Arc::new(obj),
            rest: EMPTY_LIST.clone(),
        }))
    }

    /// Create a new list with a single element (panic version)
    pub fn new_panic<T: 'static + Send + Sync>(obj: T) -> Arc<Self> {
        Arc::new(SimpleList::Cons {
            first: Arc::new(obj),
            rest: EMPTY_LIST.clone(),
        })
    }

    /// Constructs a list with obj followed by list (cons operation)
    pub fn cons_safe<T: 'static + Send + Sync>(&self, obj: T) -> Result<Arc<Self>, String> {
        Ok(Arc::new(SimpleList::Cons {
            first: Arc::new(obj) as Arc<dyn std::any::Any + Send + Sync>,
            rest: Arc::new(self.clone()),
        }))
    }

    /// Constructs a list with obj followed by list (cons operation with Arc<dyn Any>)
    pub fn cons_any(&self, obj: Arc<dyn std::any::Any + Send + Sync>) -> Arc<Self> {
        Arc::new(SimpleList::Cons {
            first: obj,
            rest: Arc::new(self.clone()),
        })
    }

    /// Constructs a list with obj followed by list (cons operation, panic version)
    pub fn cons_panic<T: 'static + Send + Sync>(&self, obj: T) -> Arc<Self> {
        Arc::new(SimpleList::Cons {
            first: Arc::new(obj) as Arc<dyn std::any::Any + Send + Sync>,
            rest: Arc::new(self.clone()),
        })
    }

    /// Create a list from a collection
    pub fn from_collection_safe<T: 'static + Send + Sync + Clone>(
        collection: &[T]
    ) -> Result<Arc<Self>, String> {
        let mut result = EMPTY_LIST.clone();
        for item in collection.iter().rev() {
            result = result.cons_safe(item.clone())?;
        }
        Ok(result)
    }

    /// Create a list from a collection (panic version)
    pub fn from_collection_panic<T: 'static + Send + Sync + Clone>(
        collection: &[T]
    ) -> Arc<Self> {
        let mut result = EMPTY_LIST.clone();
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
        match self {
            SimpleList::Empty => 0,
            SimpleList::Cons { rest, .. } => 1 + rest.size(),
        }
    }

    /// Get the first element
    pub fn first(&self) -> Option<Arc<dyn std::any::Any + Send + Sync>> {
        match self {
            SimpleList::Empty => None,
            SimpleList::Cons { first, .. } => Some(first.clone()),
        }
    }

    /// Get the rest of the list
    pub fn rest(&self) -> Arc<Self> {
        match self {
            SimpleList::Empty => EMPTY_LIST.clone(),
            SimpleList::Cons { rest, .. } => rest.clone(),
        }
    }

    /// Get the first element as a specific type
    pub fn first_as<T: 'static + Send + Sync>(&self) -> Option<Arc<T>> {
        match self {
            SimpleList::Empty => None,
            SimpleList::Cons { first, .. } => {
                Arc::downcast(first.clone()).ok()
            }
        }
    }

    /// Copy the list (deep copy)
    pub fn copy_list(&self) -> Arc<Self> {
        match self {
            SimpleList::Empty => EMPTY_LIST.clone(),
            SimpleList::Cons { first, rest } => {
                Arc::new(SimpleList::Cons {
                    first: first.clone(),
                    rest: rest.copy_list(),
                })
            }
        }
    }

    /// Append another list to this list
    pub fn append(&self, other: &Arc<Self>) -> Arc<Self> {
        match self {
            SimpleList::Empty => other.clone(),
            SimpleList::Cons { first, rest } => {
                Arc::new(SimpleList::Cons {
                    first: first.clone(),
                    rest: rest.append(other),
                })
            }
        }
    }

    /// Reverse the list
    pub fn reverse(&self) -> Arc<Self> {
        self.reverse_with(EMPTY_LIST.clone())
    }

    /// Reverse the list and append another list (revappend)
    pub fn reverse_with(&self, other: Arc<Self>) -> Arc<Self> {
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
                    current = rest;
                }
            }
        }
        
        result
    }

    /// Check if the list contains an element
    pub fn contains<T: 'static + PartialEq>(&self, obj: &T) -> bool {
        match self {
            SimpleList::Empty => false,
            SimpleList::Cons { first, rest } => {
                if let Some(first_val) = first.downcast_ref::<T>() {
                    if first_val == obj {
                        return true;
                    }
                }
                rest.contains(obj)
            }
        }
    }

    /// Get element at index (inefficient - O(n))
    pub fn get_safe(&self, index: usize) -> Result<Option<Arc<dyn std::any::Any + Send + Sync>>, String> {
        if index >= self.size() {
            return Err(format!("Index {} out of bounds for list of size {}", index, self.size()));
        }
        
        let mut current = self;
        for _ in 0..index {
            current = match current {
                SimpleList::Empty => return Err("Unexpected empty list during traversal".to_string()),
                SimpleList::Cons { rest, .. } => rest,
            };
        }
        
        Ok(current.first())
    }

    /// Get element at index (panic version)
    pub fn get_panic(&self, index: usize) -> Option<Arc<dyn std::any::Any + Send + Sync>> {
        if index >= self.size() {
            panic!("Index {} out of bounds for list of size {}", index, self.size());
        }
        
        let mut current = self;
        for _ in 0..index {
            current = match current {
                SimpleList::Empty => panic!("Unexpected empty list during traversal"),
                SimpleList::Cons { rest, .. } => rest,
            };
        }
        
        current.first()
    }

    /// Find index of an element
    pub fn index_of<T: 'static + PartialEq>(&self, obj: &T) -> Option<usize> {
        let mut current = self;
        let mut index = 0;
        
        loop {
            match current {
                SimpleList::Empty => return None,
                SimpleList::Cons { first, rest } => {
                    if let Some(first_val) = first.downcast_ref::<T>() {
                        if first_val == obj {
                            return Some(index);
                        }
                    }
                    current = rest;
                    index += 1;
                }
            }
        }
    }

    /// Find last index of an element
    pub fn last_index_of<T: 'static + PartialEq>(&self, obj: &T) -> Option<usize> {
        let mut last_index = None;
        let mut current = self;
        let mut index = 0;
        
        loop {
            match current {
                SimpleList::Empty => return last_index,
                SimpleList::Cons { first, rest } => {
                    if let Some(first_val) = first.downcast_ref::<T>() {
                        if first_val == obj {
                            last_index = Some(index);
                        }
                    }
                    current = rest;
                    index += 1;
                }
            }
        }
    }

    /// Get a sublist
    pub fn sub_list_safe(&self, start: usize, end: usize) -> Result<Arc<Self>, String> {
        if start > end {
            return Err(format!("Start index {} > end index {}", start, end));
        }
        if end > self.size() {
            return Err(format!("End index {} > list size {}", end, self.size()));
        }
        
        let mut result = EMPTY_LIST.clone();
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
                    current = rest;
                    index += 1;
                }
            }
        }
        
        Ok(result.reverse())
    }

    /// Get a sublist (panic version)
    pub fn sub_list_panic(&self, start: usize, end: usize) -> Arc<Self> {
        if start > end {
            panic!("Start index {} > end index {}", start, end);
        }
        if end > self.size() {
            panic!("End index {} > list size {}", end, self.size());
        }
        
        let mut result = EMPTY_LIST.clone();
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
                    current = rest;
                    index += 1;
                }
            }
        }
        
        result.reverse()
    }

    /// Convert to vector
    pub fn to_vec(&self) -> Vec<Arc<dyn std::any::Any + Send + Sync>> {
        let mut result = Vec::new();
        let mut current = self;
        
        loop {
            match current {
                SimpleList::Empty => break,
                SimpleList::Cons { first, rest } => {
                    result.push(first.clone());
                    current = rest;
                }
            }
        }
        
        result
    }

    /// Convert to vector of specific type
    pub fn to_vec_of<T: 'static + Send + Sync>(&self) -> Vec<Arc<T>> {
        let mut result = Vec::new();
        let mut current = self;
        
        loop {
            match current {
                SimpleList::Empty => break,
                SimpleList::Cons { first, rest } => {
                    if let Ok(typed_first) = Arc::downcast(first.clone()) {
                        result.push(typed_first);
                    }
                    current = rest;
                }
            }
        }
        
        result
    }

    /// Check if this list contains all elements from another list
    pub fn contains_all<T: 'static + PartialEq>(&self, other: &Arc<Self>) -> bool {
        let mut current = other;
        
        loop {
            match current.as_ref() {
                SimpleList::Empty => return true,
                SimpleList::Cons { first, rest } => {
                    if let Some(first_val) = first.downcast_ref::<T>() {
                        if !self.contains(first_val) {
                            return false;
                        }
                    }
                    current = rest;
                }
            }
        }
    }
}

impl fmt::Display for SimpleList {
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
                    // Try to extract the actual value for display
                    if let Some(int_val) = elem.downcast_ref::<i32>() {
                        write!(f, "{}", int_val)?;
                    } else if let Some(string_val) = elem.downcast_ref::<String>() {
                        write!(f, "{}", string_val)?;
                    } else if let Some(bool_val) = elem.downcast_ref::<bool>() {
                        write!(f, "{}", bool_val)?;
                    } else if let Some(str_val) = elem.downcast_ref::<&str>() {
                        write!(f, "{}", str_val)?;
                    } else {
                        write!(f, "{:?}", elem)?;
                    }
                    first = false;
                    current = rest;
                }
            }
        }
        
        write!(f, ")")
    }
}

impl PartialEq for SimpleList {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (SimpleList::Empty, SimpleList::Empty) => true,
            (SimpleList::Cons { first: f1, rest: r1 }, SimpleList::Cons { first: f2, rest: r2 }) => {
                // Compare the actual values, not the Arc pointers
                if let (Some(v1), Some(v2)) = (f1.downcast_ref::<i32>(), f2.downcast_ref::<i32>()) {
                    v1 == v2 && r1 == r2
                } else if let (Some(v1), Some(v2)) = (f1.downcast_ref::<String>(), f2.downcast_ref::<String>()) {
                    v1 == v2 && r1 == r2
                } else if let (Some(v1), Some(v2)) = (f1.downcast_ref::<bool>(), f2.downcast_ref::<bool>()) {
                    v1 == v2 && r1 == r2
                } else if let (Some(v1), Some(v2)) = (f1.downcast_ref::<&str>(), f2.downcast_ref::<&str>()) {
                    v1 == v2 && r1 == r2
                } else {
                    // For other types, compare Arc pointers (reference equality)
                    Arc::ptr_eq(f1, f2) && r1 == r2
                }
            }
            _ => false,
        }
    }
}

impl Eq for SimpleList {}

impl Hash for SimpleList {
    fn hash<H: Hasher>(&self, state: &mut H) {
        match self {
            SimpleList::Empty => {
                // Hash empty list consistently
                "EMPTY_LIST".hash(state);
            }
            SimpleList::Cons { first, rest } => {
                // Hash the actual values, not the Arc pointers
                if let Some(val) = first.downcast_ref::<i32>() {
                    val.hash(state);
                } else if let Some(val) = first.downcast_ref::<String>() {
                    val.hash(state);
                } else if let Some(val) = first.downcast_ref::<bool>() {
                    val.hash(state);
                } else if let Some(val) = first.downcast_ref::<&str>() {
                    val.hash(state);
                } else {
                    // For other types, use pointer addresses
                    (Arc::as_ptr(first) as *const () as usize).hash(state);
                }
                rest.hash(state);
            }
        }
    }
}

impl Ord for SimpleList {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        // Simple ordering based on size first, then pointer addresses
        match (self, other) {
            (SimpleList::Empty, SimpleList::Empty) => std::cmp::Ordering::Equal,
            (SimpleList::Empty, _) => std::cmp::Ordering::Less,
            (_, SimpleList::Empty) => std::cmp::Ordering::Greater,
            (SimpleList::Cons { .. }, SimpleList::Cons { .. }) => {
                let size_cmp = self.size().cmp(&other.size());
                if size_cmp != std::cmp::Ordering::Equal {
                    return size_cmp;
                }
                
                // If sizes are equal, compare by pointer addresses
                let self_ptr = self as *const _ as usize;
                let other_ptr = other as *const _ as usize;
                self_ptr.cmp(&other_ptr)
            }
        }
    }
}

impl PartialOrd for SimpleList {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

/// Iterator for SimpleList
pub struct SimpleListIterator {
    current: Arc<SimpleList>,
}

impl SimpleListIterator {
    pub fn new(list: Arc<SimpleList>) -> Self {
        Self { current: list }
    }
}

impl Iterator for SimpleListIterator {
    type Item = Arc<dyn std::any::Any + Send + Sync>;

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

impl IntoIterator for SimpleList {
    type Item = Arc<dyn std::any::Any + Send + Sync>;
    type IntoIter = SimpleListIterator;

    fn into_iter(self) -> Self::IntoIter {
        SimpleListIterator::new(Arc::new(self))
    }
}

impl<'a> IntoIterator for &'a SimpleList {
    type Item = Arc<dyn std::any::Any + Send + Sync>;
    type IntoIter = SimpleListIterator;

    fn into_iter(self) -> Self::IntoIter {
        SimpleListIterator::new(Arc::new(self.clone()))
    }
}


/// Front iterator that stops at a specific tail
pub struct FrontIterator {
    current: Arc<SimpleList>,
    tail: Arc<SimpleList>,
}

impl FrontIterator {
    pub fn new(list: Arc<SimpleList>, tail: Arc<SimpleList>) -> Self {
        Self {
            current: list,
            tail,
        }
    }
}

impl Iterator for FrontIterator {
    type Item = Arc<dyn std::any::Any + Send + Sync>;

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
        let empty = SimpleList::new();
        assert!(empty.is_empty());
        assert_eq!(empty.size(), 0);
        assert!(empty.first().is_none());
    }

    #[test]
    fn test_cons_operation() {
        let empty = SimpleList::new();
        let list = empty.cons_safe(42).unwrap();
        
        assert!(!list.is_empty());
        assert_eq!(list.size(), 1);
        assert_eq!(*list.first_as::<i32>().unwrap(), 42);
    }

    #[test]
    fn test_multiple_cons() {
        let empty = SimpleList::new();
        let list = empty.cons_safe(3).unwrap()
                       .cons_safe(2).unwrap()
                       .cons_safe(1).unwrap();
        
        assert_eq!(list.size(), 3);
        assert_eq!(*list.first_as::<i32>().unwrap(), 1);
    }

    #[test]
    fn test_append() {
        let list1 = SimpleList::new().cons_safe(1).unwrap().cons_safe(2).unwrap();
        let list2 = SimpleList::new().cons_safe(3).unwrap().cons_safe(4).unwrap();
        let result = list1.append(&list2);
        
        assert_eq!(result.size(), 4);
    }

    #[test]
    fn test_reverse() {
        let list = SimpleList::new().cons_safe(1).unwrap()
                       .cons_safe(2).unwrap()
                       .cons_safe(3).unwrap();
        let reversed = list.reverse();
        
        assert_eq!(reversed.size(), 3);
        // After reversing (3 (2 (1 ()))) becomes (1 (2 (3 ())))
        assert_eq!(*reversed.first_as::<i32>().unwrap(), 1);
    }

    #[test]
    fn test_contains() {
        let list = SimpleList::new().cons_safe(1).unwrap()
                       .cons_safe(2).unwrap()
                       .cons_safe(3).unwrap();
        
        assert!(list.contains(&2));
        assert!(!list.contains(&4));
    }

    #[test]
    fn test_get() {
        let list = SimpleList::new().cons_safe(1).unwrap()
                       .cons_safe(2).unwrap()
                       .cons_safe(3).unwrap();
        
        // The list is (3 (2 (1 ()))), so indices are: 0=3, 1=2, 2=1
        assert_eq!(*list.get_safe(0).unwrap().unwrap().downcast_ref::<i32>().unwrap(), 3);
        assert_eq!(*list.get_safe(1).unwrap().unwrap().downcast_ref::<i32>().unwrap(), 2);
        assert_eq!(*list.get_safe(2).unwrap().unwrap().downcast_ref::<i32>().unwrap(), 1);
    }

    #[test]
    fn test_index_of() {
        let list = SimpleList::new().cons_safe(1).unwrap()
                       .cons_safe(2).unwrap()
                       .cons_safe(3).unwrap();
        
        assert_eq!(list.index_of(&2), Some(1));
        assert_eq!(list.index_of(&4), None);
    }

    #[test]
    fn test_sub_list() {
        let list = SimpleList::new().cons_safe(1).unwrap()
                       .cons_safe(2).unwrap()
                       .cons_safe(3).unwrap()
                       .cons_safe(4).unwrap();
        
        let sub = list.sub_list_safe(1, 3).unwrap();
        assert_eq!(sub.size(), 2);
    }

    #[test]
    fn test_iterator() {
        let list = SimpleList::new().cons_safe(1).unwrap()
                       .cons_safe(2).unwrap()
                       .cons_safe(3).unwrap();
        
        // The list is (3 (2 (1 ()))), so iteration gives: 3, 2, 1
        let mut iter = SimpleListIterator::new(list.clone());
        assert_eq!(*iter.next().unwrap().downcast_ref::<i32>().unwrap(), 3);
        assert_eq!(*iter.next().unwrap().downcast_ref::<i32>().unwrap(), 2);
        assert_eq!(*iter.next().unwrap().downcast_ref::<i32>().unwrap(), 1);
        assert!(iter.next().is_none());
    }

    #[test]
    fn test_from_collection() {
        let vec = vec![1, 2, 3, 4];
        let list = SimpleList::from_collection_safe(&vec).unwrap();
        
        assert_eq!(list.size(), 4);
        assert_eq!(*list.first_as::<i32>().unwrap(), 1);
    }
}
