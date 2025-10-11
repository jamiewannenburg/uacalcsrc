use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::util::horner;
use uacalc::util::simple_list;
use std::sync::Arc;
use std::collections::HashMap;

/// A type-erased SimpleList that can hold any Python object
/// This maintains the linked list structure while allowing dynamic typing
#[derive(Debug, Clone)]
pub enum PySimpleListInner {
    Cons {
        first: PyObject,
        rest: Arc<PySimpleListInner>,
    },
    Empty,
}

impl PySimpleListInner {
    /// Create a new empty list
    pub fn new() -> Arc<Self> {
        Arc::new(PySimpleListInner::Empty)
    }

    /// Create a new list with a single element
    pub fn new_safe(obj: PyObject) -> Result<Arc<Self>, String> {
        Ok(Arc::new(PySimpleListInner::Cons {
            first: obj,
            rest: Self::new(),
        }))
    }

    /// Constructs a list with obj followed by list (cons operation)
    pub fn cons_safe(self: &Arc<Self>, obj: PyObject) -> Result<Arc<Self>, String> {
        Ok(Arc::new(PySimpleListInner::Cons {
            first: obj,
            rest: self.clone(),
        }))
    }

    /// Check if the list is empty
    pub fn is_empty(&self) -> bool {
        matches!(self, PySimpleListInner::Empty)
    }

    /// Get the size of the list (inefficient - O(n))
    pub fn size(&self) -> usize {
        let mut count = 0;
        let mut current = self;
        
        loop {
            match current {
                PySimpleListInner::Empty => break,
                PySimpleListInner::Cons { rest, .. } => {
                    count += 1;
                    current = rest.as_ref();
                }
            }
        }
        
        count
    }

    /// Get the first element
    pub fn first(&self) -> Option<PyObject> {
        match self {
            PySimpleListInner::Empty => None,
            PySimpleListInner::Cons { first, .. } => Some(first.clone()),
        }
    }

    /// Get the rest of the list
    pub fn rest(&self) -> Arc<Self> {
        match self {
            PySimpleListInner::Empty => Self::new(),
            PySimpleListInner::Cons { rest, .. } => rest.clone(),
        }
    }

    /// Copy the list (deep copy)
    pub fn copy_list(&self) -> Arc<Self> {
        let mut result = Self::new();
        let mut current = self;
        
        // Collect elements in reverse order
        let mut elements = Vec::new();
        loop {
            match current {
                PySimpleListInner::Empty => break,
                PySimpleListInner::Cons { first, rest } => {
                    elements.push(first.clone());
                    current = rest.as_ref();
                }
            }
        }
        
        // Build the result by consing elements in reverse order
        for element in elements.into_iter().rev() {
            result = result.cons_safe(element).unwrap();
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
                PySimpleListInner::Empty => break,
                PySimpleListInner::Cons { first, rest } => {
                    elements.push(first.clone());
                    current = rest.as_ref();
                }
            }
        }
        
        // Build the result by consing elements in reverse order
        for element in elements.into_iter().rev() {
            result = result.cons_safe(element).unwrap();
        }
        
        result
    }

    /// Reverse the list
    pub fn reverse(&self) -> Arc<Self> {
        self.reverse_with(Self::new())
    }

    /// Reverse the list and append another list (revappend)
    pub fn reverse_with(&self, other: Arc<Self>) -> Arc<Self> {
        let mut result = other;
        let mut current = self;
        
        loop {
            match current {
                PySimpleListInner::Empty => break,
                PySimpleListInner::Cons { first, rest } => {
                    result = result.cons_safe(first.clone()).unwrap();
                    current = rest.as_ref();
                }
            }
        }
        
        result
    }

    /// Check if the list contains an element
    pub fn contains(&self, obj: &PyObject) -> bool {
        let mut current = self;
        
        loop {
            match current {
                PySimpleListInner::Empty => return false,
                PySimpleListInner::Cons { first, rest } => {
                    // Use Python's equality comparison
                    let found = Python::with_gil(|py| {
                        if let Ok(equal) = first.call_method1(py, "__eq__", (obj,)) {
                            if let Ok(is_equal) = equal.extract::<bool>(py) {
                                return is_equal;
                            }
                        }
                        false
                    });
                    if found {
                        return true;
                    }
                    current = rest.as_ref();
                }
            }
        }
    }

    /// Get element at index (inefficient - O(n))
    pub fn get_safe(&self, index: usize) -> Result<Option<PyObject>, String> {
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
                PySimpleListInner::Empty => {
                    return Err(format!("Index {} out of bounds - list has only {} elements", index, current_index));
                },
                PySimpleListInner::Cons { rest, .. } => {
                    current_index += 1;
                    rest.as_ref()
                },
            };
        }
        
        // Check if we reached the end before finding the index
        match current {
            PySimpleListInner::Empty => {
                Err(format!("Index {} out of bounds - list has only {} elements", index, current_index))
            },
            _ => Ok(current.first())
        }
    }

    /// Find index of an element
    pub fn index_of(&self, obj: &PyObject) -> Option<usize> {
        let mut current = self;
        let mut index = 0;
        
        loop {
            match current {
                PySimpleListInner::Empty => return None,
                PySimpleListInner::Cons { first, rest } => {
                    // Use Python's equality comparison
                    let found = Python::with_gil(|py| {
                        if let Ok(equal) = first.call_method1(py, "__eq__", (obj,)) {
                            if let Ok(is_equal) = equal.extract::<bool>(py) {
                                return is_equal;
                            }
                        }
                        false
                    });
                    if found {
                        return Some(index);
                    }
                    current = rest.as_ref();
                    index += 1;
                }
            }
        }
    }

    /// Find last index of an element
    pub fn last_index_of(&self, obj: &PyObject) -> Option<usize> {
        let mut last_index = None;
        let mut current = self;
        let mut index = 0;
        
        loop {
            match current {
                PySimpleListInner::Empty => return last_index,
                PySimpleListInner::Cons { first, rest } => {
                    // Use Python's equality comparison
                    let found = Python::with_gil(|py| {
                        if let Ok(equal) = first.call_method1(py, "__eq__", (obj,)) {
                            if let Ok(is_equal) = equal.extract::<bool>(py) {
                                return is_equal;
                            }
                        }
                        false
                    });
                    if found {
                        last_index = Some(index);
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
        
        let mut result = Self::new();
        let mut current = self;
        let mut index = 0;
        
        loop {
            match current {
                PySimpleListInner::Empty => break,
                PySimpleListInner::Cons { first, rest } => {
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

    /// Convert to Python list
    pub fn to_list(&self, py: Python) -> PyResult<Vec<PyObject>> {
        let mut result = Vec::new();
        let mut current = self;
        
        loop {
            match current {
                PySimpleListInner::Empty => break,
                PySimpleListInner::Cons { first, rest } => {
                    result.push(first.clone());
                    current = rest.as_ref();
                }
            }
        }
        
        Ok(result)
    }

    /// Check if this list contains all elements from another list
    pub fn contains_all(&self, other: &Arc<Self>) -> bool {
        let mut current = other;
        
        loop {
            match current.as_ref() {
                PySimpleListInner::Empty => return true,
                PySimpleListInner::Cons { first, rest } => {
                    if !self.contains(first) {
                        return false;
                    }
                    current = rest;
                }
            }
        }
    }

    /// Convert to string representation
    pub fn to_string(&self) -> String {
        let mut result = String::from("(");
        let mut first = true;
        let mut current = self;
        
        loop {
            match current {
                PySimpleListInner::Empty => break,
                PySimpleListInner::Cons { first: elem, rest } => {
                    if !first {
                        result.push(' ');
                    }
                    result.push_str(&elem.to_string());
                    first = false;
                    current = rest;
                }
            }
        }
        
        result.push(')');
        result
    }
}

/// Python wrapper for Horner encoding/decoding operations
#[pyclass]
pub struct PyHorner;

#[pymethods]
impl PyHorner {
    /// Create a new Horner instance (static methods, so this is just a placeholder)
    #[new]
    fn new() -> Self {
        PyHorner
    }
    
    /// Returns the Horner encoding of an int array representing an element
    /// from a direct product of algebras with various sizes.
    #[staticmethod]
    fn horner(args: Vec<i32>, sizes: Vec<i32>) -> PyResult<i32> {
        match horner::horner_safe(&args, &sizes) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Returns the int array corresponding to this Horner encoding
    /// for a direct product of algebras with various sizes.
    #[staticmethod]
    fn horner_inv(k: i32, sizes: Vec<i32>) -> PyResult<Vec<i32>> {
        match horner::horner_inv_safe(k, &sizes) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Returns the Horner encoding of an int array representing an element
    /// from a direct product of algebras all with the same size.
    #[staticmethod]
    fn horner_same_size(args: Vec<i32>, size: i32) -> PyResult<i32> {
        match horner::horner_same_size_safe(&args, size) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Returns the int array corresponding to this Horner encoding
    /// for a direct product of algebras with the same size.
    #[staticmethod]
    fn horner_inv_same_size(k: i32, size: i32, length: usize) -> PyResult<Vec<i32>> {
        match horner::horner_inv_same_size_safe(k, size, length) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Returns the Horner encoding of an int array representing an element
    /// from a direct product of algebras with the same size (Integer version).
    #[staticmethod]
    fn horner_integer(args: Vec<i32>, size: i32) -> PyResult<i32> {
        match horner::horner_integer_safe(&args, size) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// A convenience method for generating a new array with the reverse
    /// order of the given array.
    #[staticmethod]
    fn reverse_array(arr: Vec<i32>) -> Vec<i32> {
        horner::reverse_array(&arr)
    }
    
    /// If values are the values of a function at [0,0, ...,0], [1,0,...,0],
    /// this gives the values in the order [0,0, ...,0], [0,0,...,1], ...  .
    #[staticmethod]
    fn left_right_reverse(values: Vec<i32>, alg_size: i32, arity: usize) -> PyResult<Vec<i32>> {
        match horner::left_right_reverse_safe(&values, alg_size, arity) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        "Horner".to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        "Horner()".to_string()
    }
}

/// Python wrapper for SimpleList
#[pyclass]
pub struct PySimpleList {
    inner: Arc<PySimpleListInner>,
}

#[pymethods]
impl PySimpleList {
    /// Create a new empty SimpleList
    #[new]
    fn new() -> Self {
        PySimpleList {
            inner: PySimpleListInner::new(),
        }
    }
    
    /// Create a new SimpleList with a single element
    #[staticmethod]
    fn make_list(obj: PyObject) -> PyResult<Self> {
        let inner = PySimpleListInner::new_safe(obj).map_err(|e| PyValueError::new_err(e))?;
        Ok(PySimpleList { inner })
    }
    
    /// Create a new SimpleList from a Python list
    #[staticmethod]
    fn from_list(py: Python, items: Vec<PyObject>) -> PyResult<Self> {
        let mut result = PySimpleListInner::new();
        for item in items.into_iter().rev() {
            result = result.cons_safe(item).map_err(|e| PyValueError::new_err(e))?;
        }
        Ok(PySimpleList { inner: result })
    }
    
    /// Check if the list is empty
    fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }
    
    /// Get the size of the list
    fn size(&self) -> usize {
        self.inner.size()
    }
    
    /// Get the first element
    fn first(&self) -> Option<PyObject> {
        self.inner.first()
    }
    
    /// Get the rest of the list
    fn rest(&self) -> PySimpleList {
        PySimpleList {
            inner: self.inner.rest(),
        }
    }
    
    /// Add an element to the front of the list (cons operation)
    fn cons(&self, obj: PyObject) -> PyResult<Self> {
        let inner = self.inner.cons_safe(obj).map_err(|e| PyValueError::new_err(e))?;
        Ok(PySimpleList { inner })
    }
    
    /// Copy the list
    fn copy_list(&self) -> Self {
        PySimpleList {
            inner: self.inner.copy_list(),
        }
    }
    
    /// Append another list to this list
    fn append(&self, other: &PySimpleList) -> Self {
        PySimpleList {
            inner: self.inner.append(&other.inner),
        }
    }
    
    /// Reverse the list
    fn reverse(&self) -> Self {
        PySimpleList {
            inner: self.inner.reverse(),
        }
    }
    
    /// Reverse the list and append another list
    fn reverse_with(&self, other: &PySimpleList) -> Self {
        PySimpleList {
            inner: self.inner.reverse_with(other.inner.clone()),
        }
    }
    
    /// Check if the list contains an element
    fn contains(&self, obj: PyObject) -> bool {
        self.inner.contains(&obj)
    }
    
    /// Get element at index
    fn get(&self, index: usize) -> PyResult<Option<PyObject>> {
        match self.inner.get_safe(index) {
            Ok(item) => Ok(item),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Find index of an element
    fn index_of(&self, obj: PyObject) -> Option<usize> {
        self.inner.index_of(&obj)
    }
    
    /// Find last index of an element
    fn last_index_of(&self, obj: PyObject) -> Option<usize> {
        self.inner.last_index_of(&obj)
    }
    
    /// Get a sublist
    fn sub_list(&self, start: usize, end: usize) -> PyResult<Self> {
        match self.inner.sub_list_safe(start, end) {
            Ok(inner) => Ok(PySimpleList { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Convert to Python list
    fn to_list(&self, py: Python) -> PyResult<Vec<PyObject>> {
        self.inner.to_list(py)
    }
    
    /// Check if this list contains all elements from another list
    fn contains_all(&self, other: &PySimpleList) -> bool {
        self.inner.contains_all(&other.inner)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("SimpleList({})", self.inner.to_string())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PySimpleList) -> bool {
        // For now, use string comparison for equality
        // This could be improved to do proper element-wise comparison
        self.inner.to_string() == other.inner.to_string()
    }
    
    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.to_string().hash(&mut hasher);
        hasher.finish()
    }
    
    /// Python length function
    fn __len__(&self) -> usize {
        self.inner.size()
    }
    
    /// Python iteration support
    fn __iter__(slf: PyRef<Self>) -> PyResult<PyObject> {
        let iter = PySimpleListIterator::new(slf.inner.clone());
        Ok(iter.into_py(slf.py()))
    }
}

/// Iterator for Python SimpleList
#[pyclass]
pub struct PySimpleListIterator {
    current: Arc<PySimpleListInner>,
}

#[pymethods]
impl PySimpleListIterator {
    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }
    
    fn __next__(&mut self, py: Python) -> PyResult<Option<PyObject>> {
        match self.current.as_ref() {
            PySimpleListInner::Empty => Ok(None),
            PySimpleListInner::Cons { first, rest } => {
                let result = first.clone();
                self.current = rest.clone();
                Ok(Some(result))
            }
        }
    }
}

impl PySimpleListIterator {
    fn new(list: Arc<PySimpleListInner>) -> Self {
        Self { current: list }
    }
}

pub fn register_util_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyHorner>()?;
    m.add_class::<PySimpleList>()?;
    m.add_class::<PySimpleListIterator>()?;
    Ok(())
}
