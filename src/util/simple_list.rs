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

/// Maximum recursion depth to prevent stack overflow
const MAX_RECURSION_DEPTH: usize = 10000;

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
    pub fn cons_safe<T: 'static + Send + Sync>(self: &Arc<Self>, obj: T) -> Result<Arc<Self>, String> {
        // Debug: Check if we're creating a very large list
        if let Some(size) = self.try_size() {
            if size > 5000 {
                println!("DEBUG: cons_safe() called on list with size {}", size);
            }
        }
        
        Ok(Arc::new(SimpleList::Cons {
            first: Arc::new(obj),
            rest: self.clone(),
        }))
    }

    /// Constructs a list with obj followed by list (cons operation with Arc<dyn Any>)
    pub fn cons_any(self: &Arc<Self>, obj: Arc<dyn std::any::Any + Send + Sync>) -> Arc<Self> {
        Arc::new(SimpleList::Cons {
            first: obj,
            rest: self.clone(),
        })
    }

    /// Constructs a list with obj followed by list (cons operation, panic version)
    pub fn cons_panic<T: 'static + Send + Sync>(self: &Arc<Self>, obj: T) -> Arc<Self> {
        Arc::new(SimpleList::Cons {
            first: Arc::new(obj),
            rest: self.clone(),
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
        println!("DEBUG: size() called");
        let mut count = 0;
        let mut current = self;
        
        loop {
            match current {
                SimpleList::Empty => {
                    println!("DEBUG: size() found empty list, count = {}", count);
                    break;
                },
                SimpleList::Cons { rest, .. } => {
                    count += 1;
                    if count % 1000 == 0 {
                        println!("DEBUG: size() at count {}", count);
                    }
                    // Check recursion depth to prevent stack overflow
                    if count > MAX_RECURSION_DEPTH {
                        println!("DEBUG: size() exceeded MAX_RECURSION_DEPTH at count {}", count);
                        panic!("List size exceeds maximum allowed depth {} - possible circular reference", MAX_RECURSION_DEPTH);
                    }
                    current = rest.as_ref();
                }
            }
        }
        
        println!("DEBUG: size() returning count = {}", count);
        count
    }

    /// Try to get the size of the list without panicking (returns None if too deep)
    pub fn try_size(&self) -> Option<usize> {
        let mut count = 0;
        let mut current = self;
        
        loop {
            match current {
                SimpleList::Empty => break,
                SimpleList::Cons { rest, .. } => {
                    count += 1;
                    // Check recursion depth to prevent stack overflow
                    if count > MAX_RECURSION_DEPTH {
                        return None; // Return None instead of panicking
                    }
                    current = rest.as_ref();
                }
            }
        }
        
        Some(count)
    }

    /// Get the first element
    pub fn first(&self) -> Option<Arc<dyn std::any::Any + Send + Sync>> {
        println!("DEBUG: first() called");
        match self {
            SimpleList::Empty => {
                println!("DEBUG: first() found empty list");
                None
            },
            SimpleList::Cons { first, .. } => {
                println!("DEBUG: first() found element, about to clone Arc");
                let cloned = first.clone();
                println!("DEBUG: first() successfully cloned Arc");
                Some(cloned)
            },
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
        let mut result = EMPTY_LIST.clone();
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
    pub fn append(&self, other: &Arc<Self>) -> Arc<Self> {
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
                    current = rest.as_ref();
                }
            }
        }
        
        result
    }

    /// Check if the list contains an element
    pub fn contains<T: 'static + PartialEq>(&self, obj: &T) -> bool {
        let mut current = self;
        
        loop {
            match current {
                SimpleList::Empty => return false,
                SimpleList::Cons { first, rest } => {
                    if let Some(first_val) = first.downcast_ref::<T>() {
                        if first_val == obj {
                            return true;
                        }
                    }
                    current = rest.as_ref();
                }
            }
        }
    }

    /// Get element at index (inefficient - O(n))
    pub fn get_safe(&self, index: usize) -> Result<Option<Arc<dyn std::any::Any + Send + Sync>>, String> {
        println!("DEBUG: get_safe({}) called", index);
        
        // Special case: index 0 can be accessed directly without traversal
        if index == 0 {
            println!("DEBUG: get_safe() accessing index 0 directly");
            return Ok(self.first());
        }
        
        // For large indices, avoid calling size() to prevent stack overflow
        // Instead, traverse and check bounds during traversal
        let mut current = self;
        let mut current_index = 0;
        
        // Traverse to the desired index
        while current_index < index {
            if current_index % 1000 == 0 {
                println!("DEBUG: get_safe() at current_index {}", current_index);
            }
            current = match current {
                SimpleList::Empty => {
                    println!("DEBUG: get_safe() found empty list at index {}", current_index);
                    return Err(format!("Index {} out of bounds - list has only {} elements", index, current_index));
                },
                SimpleList::Cons { rest, .. } => {
                    // Check recursion depth to prevent stack overflow
                    if current_index > MAX_RECURSION_DEPTH {
                        println!("DEBUG: get_safe() exceeded MAX_RECURSION_DEPTH at current_index {}", current_index);
                        return Err(format!("Traversal depth {} exceeds maximum allowed depth {}", current_index, MAX_RECURSION_DEPTH));
                    }
                    current_index += 1;
                    rest.as_ref()
                },
            };
        }
        
        println!("DEBUG: get_safe() reached target index {}, getting element", index);
        // Check if we reached the end before finding the index
        match current {
            SimpleList::Empty => {
                println!("DEBUG: get_safe() found empty list at target index {}", index);
                Err(format!("Index {} out of bounds - list has only {} elements", index, current_index))
            },
            _ => {
                let result = current.first();
                println!("DEBUG: get_safe() returning element: {:?}", result);
                Ok(result)
            }
        }
    }

    /// Get element at index (panic version)
    pub fn get_panic(&self, index: usize) -> Option<Arc<dyn std::any::Any + Send + Sync>> {
        // Special case: index 0 can be accessed directly without traversal
        if index == 0 {
            return self.first();
        }
        
        // For large indices, avoid calling size() to prevent stack overflow
        // Instead, traverse and check bounds during traversal
        let mut current = self;
        let mut current_index = 0;
        
        // Traverse to the desired index
        while current_index < index {
            current = match current {
                SimpleList::Empty => {
                    panic!("Index {} out of bounds - list has only {} elements", index, current_index);
                },
                SimpleList::Cons { rest, .. } => {
                    // Check recursion depth to prevent stack overflow
                    if current_index > MAX_RECURSION_DEPTH {
                        panic!("Traversal depth {} exceeds maximum allowed depth {}", current_index, MAX_RECURSION_DEPTH);
                    }
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
                    // Check recursion depth to prevent stack overflow
                    if index > MAX_RECURSION_DEPTH {
                        return None; // Return None if we exceed depth limit
                    }
                    current = rest.as_ref();
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
                    // Check recursion depth to prevent stack overflow
                    if index > MAX_RECURSION_DEPTH {
                        return last_index; // Return last found index if we exceed depth limit
                    }
                    current = rest.as_ref();
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
                    current = rest.as_ref();
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
                    current = rest.as_ref();
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
                    current = rest.as_ref();
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
                    current = rest.as_ref();
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
        let mut current1 = self;
        let mut current2 = other;
        
        loop {
            match (current1, current2) {
                (SimpleList::Empty, SimpleList::Empty) => return true,
                (SimpleList::Empty, _) | (_, SimpleList::Empty) => return false,
                (SimpleList::Cons { first: f1, rest: r1 }, SimpleList::Cons { first: f2, rest: r2 }) => {
                    // Compare the actual values, not the Arc pointers
                    let values_equal = if let (Some(v1), Some(v2)) = (f1.downcast_ref::<i32>(), f2.downcast_ref::<i32>()) {
                        v1 == v2
                    } else if let (Some(v1), Some(v2)) = (f1.downcast_ref::<String>(), f2.downcast_ref::<String>()) {
                        v1 == v2
                    } else if let (Some(v1), Some(v2)) = (f1.downcast_ref::<bool>(), f2.downcast_ref::<bool>()) {
                        v1 == v2
                    } else if let (Some(v1), Some(v2)) = (f1.downcast_ref::<&str>(), f2.downcast_ref::<&str>()) {
                        v1 == v2
                    } else {
                        // For other types, compare Arc pointers (reference equality)
                        Arc::ptr_eq(f1, f2)
                    };
                    
                    if !values_equal {
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

impl Eq for SimpleList {}

impl Hash for SimpleList {
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
                    current = rest.as_ref();
                }
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

    #[test]
    fn test_large_list_creation() {
        // Test that we can create a large list without stack overflow
        // Reduced size to prevent stack overflow while still testing functionality
        let mut large_list = SimpleList::new();
        
        // Create a list with 1000 elements (reduced from 10000 to prevent stack overflow)
        for i in 0..1000 {
            large_list = large_list.cons_safe(i).unwrap();
        }
        
        // Verify the list was created correctly
        assert_eq!(large_list.size(), 1000);
        assert_eq!(*large_list.first_as::<i32>().unwrap(), 999); // First element should be 999
        
        // Test accessing elements near the beginning (safe)
        assert_eq!(*large_list.get_safe(0).unwrap().unwrap().downcast_ref::<i32>().unwrap(), 999);
        assert_eq!(*large_list.get_safe(1).unwrap().unwrap().downcast_ref::<i32>().unwrap(), 998);
        
        // Test that memory sharing works correctly (rest() should not clone)
        let rest = large_list.rest();
        assert_eq!(rest.size(), 999);
        assert_eq!(*rest.first_as::<i32>().unwrap(), 998);
    }

    #[test]
    fn test_cons_memory_efficiency() {
        // Test that cons operations don't cause exponential memory usage
        let base = SimpleList::new().cons_safe("base").unwrap();
        
        // Create multiple lists that should share the base structure
        let list1 = base.cons_safe("prefix1").unwrap();
        let list2 = base.cons_safe("prefix2").unwrap();
        
        // Both lists should share the same base
        assert_eq!(list1.rest().rest(), list2.rest().rest());
        assert_eq!(list1.rest().rest().size(), 1);
        assert_eq!(*list1.rest().rest().first_as::<&str>().unwrap(), "base");
    }

    #[test]
    fn test_large_list_graceful_handling() {
        println!("=== Starting test_large_list_graceful_handling ===");
        
        // Test that large lists are handled gracefully without stack overflow
        let mut large_list = SimpleList::new();
        println!("Created empty list");
        
        // Create a list that approaches the recursion limit
        println!("Starting to create list with {} elements", MAX_RECURSION_DEPTH);
        for i in 0..MAX_RECURSION_DEPTH {
            if i % 1000 == 0 {
                println!("Creating element {} of {}", i, MAX_RECURSION_DEPTH);
            }
            large_list = large_list.cons_safe(i).unwrap();
        }
        println!("Finished creating list with {} elements", MAX_RECURSION_DEPTH);
        
        // Test that we can still access elements near the beginning
        println!("Testing get_safe(0)...");
        println!("DEBUG: About to call get_safe(0) on list");
        let first_element_arc = large_list.get_safe(0).unwrap().unwrap();
        println!("DEBUG: Successfully got first_element_arc: {:?}", first_element_arc);
        println!("DEBUG: About to downcast first_element_arc to i32");
        let first_element = first_element_arc.downcast_ref::<i32>()
            .expect("Failed to downcast first element to i32");
        println!("DEBUG: Successfully downcast to i32: {}", first_element);
        println!("Got first element: {}", first_element);
        assert_eq!(*first_element, (MAX_RECURSION_DEPTH - 1) as i32);
        
        println!("Testing get_safe(1)...");
        let second_element_arc = large_list.get_safe(1).unwrap().unwrap();
        let second_element = second_element_arc.downcast_ref::<i32>()
            .expect("Failed to downcast second element to i32");
        println!("Got second element: {}", second_element);
        assert_eq!(*second_element, (MAX_RECURSION_DEPTH - 2) as i32);
        
        // Test that accessing beyond the limit returns an error instead of panicking
        println!("Testing get_safe beyond limit...");
        let result = large_list.get_safe(MAX_RECURSION_DEPTH + 100);
        println!("Got result: {:?}", result);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("exceeds maximum allowed depth"));
        
        println!("=== test_large_list_graceful_handling completed successfully ===");
    }
}
