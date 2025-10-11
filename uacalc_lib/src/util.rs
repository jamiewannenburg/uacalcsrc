use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::util::horner;
use uacalc::util::simple_list;
use uacalc::util::array_string;
use uacalc::util::permutation_generator;
use uacalc::util::array_incrementor;
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

/// Python wrapper for ArrayString operations
#[pyclass]
pub struct PyArrayString;

#[pymethods]
impl PyArrayString {
    /// Create a new ArrayString instance (static methods, so this is just a placeholder)
    #[new]
    fn new() -> Self {
        PyArrayString
    }
    
    /// Convert an array or collection to a string representation.
    /// 
    /// This function mimics the behavior of Java's ArrayString.toString() method.
    /// It recursively converts nested arrays and collections to a bracketed format.
    #[staticmethod]
    fn to_string(arr: Vec<PyObject>) -> PyResult<String> {
        // Convert Python objects to their string representations
        let mut result = String::new();
        result.push('[');
        
        for (i, item) in arr.iter().enumerate() {
            if i > 0 {
                result.push(',');
            }
            result.push_str(&item.to_string());
        }
        
        result.push(']');
        Ok(result)
    }
    
    /// Convert a 2D array to a string representation.
    #[staticmethod]
    fn to_string_2d(arr: Vec<Vec<PyObject>>) -> PyResult<String> {
        let mut result = String::new();
        result.push('[');
        
        for (i, row) in arr.iter().enumerate() {
            if i > 0 {
                result.push(',');
            }
            result.push('[');
            for (j, item) in row.iter().enumerate() {
                if j > 0 {
                    result.push(',');
                }
                result.push_str(&item.to_string());
            }
            result.push(']');
        }
        
        result.push(']');
        Ok(result)
    }
    
    /// Convert any displayable type to string (handles non-arrays like Java's String.valueOf).
    #[staticmethod]
    fn value_of(value: PyObject) -> String {
        value.to_string()
    }
    
    /// Convert an integer array to string representation.
    #[staticmethod]
    fn to_string_int(arr: Vec<i32>) -> String {
        array_string::to_string(&arr)
    }
    
    /// Convert a 2D integer array to string representation.
    #[staticmethod]
    fn to_string_2d_int(arr: Vec<Vec<i32>>) -> String {
        array_string::to_string_2d(&arr)
    }
    
    /// Convert a string array to string representation.
    #[staticmethod]
    fn to_string_str(arr: Vec<String>) -> String {
        array_string::to_string(&arr)
    }
    
    /// Convert a 2D string array to string representation.
    #[staticmethod]
    fn to_string_2d_str(arr: Vec<Vec<String>>) -> String {
        array_string::to_string_2d(&arr)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        "ArrayString".to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        "ArrayString()".to_string()
    }
}

/// Python wrapper for PermutationGenerator
#[pyclass]
pub struct PyPermutationGenerator {
    inner: permutation_generator::PermutationGenerator,
}

#[pymethods]
impl PyPermutationGenerator {
    /// Create a new PermutationGenerator for permutations of n elements.
    #[new]
    #[pyo3(signature = (n))]
    fn new(n: usize) -> PyResult<Self> {
        match permutation_generator::PermutationGenerator::new_safe(n) {
            Ok(inner) => Ok(PyPermutationGenerator { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Reset the generator to the initial state (identity permutation).
    fn reset(&mut self) {
        self.inner.reset();
    }
    
    /// Get the current permutation array.
    fn get_permutation(&self) -> Vec<usize> {
        self.inner.get_permutation_vec()
    }
    
    /// Get the size of the permutation.
    fn size(&self) -> usize {
        self.inner.size()
    }
    
    /// Get the next index for permutation.
    /// 
    /// Returns the index i such that the next permutation should interchange 
    /// the i-th and following elements. Returns None if no more permutations.
    fn next_index(&mut self) -> Option<usize> {
        self.inner.next_index()
    }
    
    /// Get the next index for permutation with error handling.
    /// 
    /// Returns the index i such that the next permutation should interchange 
    /// the i-th and following elements. Returns an error if no more permutations.
    fn next_index_safe(&mut self) -> PyResult<usize> {
        match self.inner.next_index_safe() {
            Ok(index) => Ok(index),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create an iterator over all permutations.
    /// 
    /// This iterator iterates all permutations on the set 0, ..., n-1.
    /// The iteration is on a fixed array so one needs to be careful to
    /// copy any permutation that needs to be saved.
    #[staticmethod]
    fn iterator(n: usize) -> PyResult<PyPermutationIterator> {
        if n < 1 {
            return Err(PyValueError::new_err("Min 1"));
        }
        Ok(PyPermutationIterator::new(n))
    }
    
    /// Create an array incrementor for the given array.
    /// 
    /// This increments arr, applying the next transposition that results
    /// in a different array.
    /// The iteration is on a fixed array so one needs to be careful to
    /// copy any result that needs to be saved.
    #[staticmethod]
    fn array_incrementor(arr: Vec<usize>) -> PyResult<PyArrayIncrementor> {
        if arr.is_empty() {
            return Err(PyValueError::new_err("Array cannot be empty"));
        }
        Ok(PyArrayIncrementor::new(arr))
    }
    
    /// Create a list incrementor for the given list.
    /// 
    /// This increments lst, applying the next transposition that results
    /// in a different list.
    /// The iteration is on a fixed list so one needs to be careful to
    /// copy any result that needs to be saved.
    #[staticmethod]
    fn list_incrementor(lst: Vec<PyObject>) -> PyResult<PyListIncrementor> {
        if lst.is_empty() {
            return Err(PyValueError::new_err("List cannot be empty"));
        }
        Ok(PyListIncrementor::new(lst))
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("PermutationGenerator({})", self.inner.to_string())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyPermutationGenerator) -> bool {
        self.inner == other.inner
    }
    
    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }
}

/// Python wrapper for PermutationIterator
#[pyclass]
pub struct PyPermutationIterator {
    inner: permutation_generator::PermutationIterator,
}

#[pymethods]
impl PyPermutationIterator {
    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }
    
    fn __next__(&mut self) -> Option<Vec<usize>> {
        self.inner.next()
    }
}

impl PyPermutationIterator {
    fn new(n: usize) -> Self {
        Self {
            inner: permutation_generator::PermutationGenerator::iterator(n),
        }
    }
}

/// Python wrapper for ArrayIncrementor
#[pyclass]
pub struct PyArrayIncrementor {
    inner: Vec<usize>,
    generator: permutation_generator::PermutationGenerator,
}

#[pymethods]
impl PyArrayIncrementor {
    /// Get the current array
    fn get_array(&self) -> Vec<usize> {
        self.inner.clone()
    }
    
    /// Increment the array to the next permutation
    fn increment(&mut self) -> bool {
        loop {
            match self.generator.next_index() {
                Some(k) => {
                    if self.inner[k] != self.inner[k + 1] {
                        self.inner.swap(k, k + 1);
                        return true;
                    }
                    // If elements are equal, continue to next permutation
                }
                None => {
                    // Reset to original state if array has more than 1 element
                    if self.inner.len() > 1 {
                        self.inner.swap(0, 1);
                    }
                    return false;
                }
            }
        }
    }
}

impl PyArrayIncrementor {
    fn new(arr: Vec<usize>) -> Self {
        let mut generator = permutation_generator::PermutationGenerator::new(arr.len());
        Self {
            inner: arr,
            generator,
        }
    }
}

/// Python wrapper for ListIncrementor
#[pyclass]
pub struct PyListIncrementor {
    inner: Vec<PyObject>,
    generator: permutation_generator::PermutationGenerator,
}

#[pymethods]
impl PyListIncrementor {
    /// Get the current list
    fn get_list(&self) -> Vec<PyObject> {
        self.inner.clone()
    }
    
    /// Increment the list to the next permutation
    fn increment(&mut self) -> bool {
        loop {
            match self.generator.next_index() {
                Some(k) => {
                    // Use Python's equality comparison
                    let are_equal = Python::with_gil(|py| {
                        if let Ok(equal) = self.inner[k].call_method1(py, "__eq__", (&self.inner[k + 1],)) {
                            if let Ok(is_equal) = equal.extract::<bool>(py) {
                                return is_equal;
                            }
                        }
                        false
                    });
                    
                    if !are_equal {
                        self.inner.swap(k, k + 1);
                        return true;
                    }
                    // If elements are equal, continue to next permutation
                }
                None => {
                    // Reset to original state if list has more than 1 element
                    if self.inner.len() > 1 {
                        self.inner.swap(0, 1);
                    }
                    return false;
                }
            }
        }
    }
}

impl PyListIncrementor {
    fn new(lst: Vec<PyObject>) -> Self {
        let mut generator = permutation_generator::PermutationGenerator::new(lst.len());
        Self {
            inner: lst,
            generator,
        }
    }
}

/// Python wrapper for ArrayIncrementorImpl
#[pyclass]
pub struct PyArrayIncrementorImpl {
    data: Vec<usize>,
    generator: permutation_generator::PermutationGenerator,
}

/// Python wrapper for SimpleArrayIncrementor
#[pyclass]
pub struct PySimpleArrayIncrementor {
    data: Vec<usize>,
    max_values: Vec<usize>,
    first_call: bool,
}

#[pymethods]
impl PyArrayIncrementorImpl {
    /// Create a new ArrayIncrementorImpl for the given array.
    #[new]
    #[pyo3(signature = (arr))]
    fn new(arr: Vec<usize>) -> PyResult<Self> {
        let generator = permutation_generator::PermutationGenerator::new(arr.len());
        Ok(Self {
            data: arr,
            generator,
        })
    }
    
    /// Modify the array to be the next one; return false if there is no more.
    fn increment(&mut self) -> bool {
        loop {
            match self.generator.next_index() {
                Some(k) => {
                    if self.data[k] != self.data[k + 1] {
                        self.data.swap(k, k + 1);
                        return true;
                    }
                    // If elements are equal, continue to next permutation
                }
                None => {
                    // Reset to original state if array has more than 1 element
                    if self.data.len() > 1 {
                        self.data.swap(0, 1);
                    }
                    return false;
                }
            }
        }
    }
    
    /// Get a copy of the current array state.
    fn get_array(&self) -> Vec<usize> {
        self.data.clone()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        format!("ArrayIncrementorImpl(arr={:?})", self.data)
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("ArrayIncrementorImpl({:?})", self.data)
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyArrayIncrementorImpl) -> bool {
        self.data == other.data
    }
    
    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.data.hash(&mut hasher);
        hasher.finish()
    }
}

#[pymethods]
impl PySimpleArrayIncrementor {
    /// Create a new SimpleArrayIncrementor for the given array.
    #[new]
    #[pyo3(signature = (arr))]
    fn new(arr: Vec<usize>) -> PyResult<Self> {
        let max_values = vec![arr.len() - 1; arr.len()];
        Ok(Self {
            data: arr,
            max_values,
            first_call: true,
        })
    }
    
    /// Create a new SimpleArrayIncrementor with custom maximum values.
    #[staticmethod]
    fn new_with_max_values(arr: Vec<usize>, max_values: Vec<usize>) -> PyResult<Self> {
        if arr.len() != max_values.len() {
            return Err(PyValueError::new_err("Array and max_values must have the same length"));
        }
        
        // Validate that all array values are within their max bounds
        for (i, &val) in arr.iter().enumerate() {
            if val > max_values[i] {
                return Err(PyValueError::new_err(format!(
                    "Array value {} at position {} exceeds maximum {}", 
                    val, i, max_values[i]
                )));
            }
        }
        
        Ok(Self {
            data: arr,
            max_values,
            first_call: true,
        })
    }
    
    /// Modify the array to be the next one; return false if there is no more.
    fn increment(&mut self) -> bool {
        if self.first_call {
            self.first_call = false;
            return true; // Return the initial state
        }
        
        // Find the rightmost position that can be incremented
        for i in (0..self.data.len()).rev() {
            if self.data[i] < self.max_values[i] {
                self.data[i] += 1;
                // Reset all positions to the right to 0
                for j in (i + 1)..self.data.len() {
                    self.data[j] = 0;
                }
                return true;
            }
        }
        
        false // No more increments possible
    }
    
    /// Get a copy of the current array state.
    fn get_array(&self) -> Vec<usize> {
        self.data.clone()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        format!("SimpleArrayIncrementor(arr={:?})", self.data)
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("SimpleArrayIncrementor({:?})", self.data)
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PySimpleArrayIncrementor) -> bool {
        self.data == other.data
    }
    
    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.data.hash(&mut hasher);
        hasher.finish()
    }
}

pub fn register_util_module(py: Python, m: &PyModule) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyHorner>()?;
    m.add_class::<PySimpleList>()?;
    m.add_class::<PySimpleListIterator>()?;
    m.add_class::<PyArrayString>()?;
    m.add_class::<PyPermutationGenerator>()?;
    m.add_class::<PyPermutationIterator>()?;
    m.add_class::<PyArrayIncrementor>()?;
    m.add_class::<PyListIncrementor>()?;
    m.add_class::<PyArrayIncrementorImpl>()?;
    m.add_class::<PySimpleArrayIncrementor>()?;
    
    // Export only clean names (without Py prefix)
    m.add("Horner", m.getattr("PyHorner")?)?;
    m.add("SimpleList", m.getattr("PySimpleList")?)?;
    m.add("ArrayString", m.getattr("PyArrayString")?)?;
    m.add("PermutationGenerator", m.getattr("PyPermutationGenerator")?)?;
    m.add("ArrayIncrementorImpl", m.getattr("PyArrayIncrementorImpl")?)?;
    m.add("SimpleArrayIncrementor", m.getattr("PySimpleArrayIncrementor")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyHorner")?;
    module_dict.del_item("PySimpleList")?;
    module_dict.del_item("PySimpleListIterator")?;
    module_dict.del_item("PyArrayString")?;
    module_dict.del_item("PyPermutationGenerator")?;
    module_dict.del_item("PyPermutationIterator")?;
    module_dict.del_item("PyArrayIncrementor")?;
    module_dict.del_item("PyListIncrementor")?;
    module_dict.del_item("PyArrayIncrementorImpl")?;
    module_dict.del_item("PySimpleArrayIncrementor")?;
    
    Ok(())
}
