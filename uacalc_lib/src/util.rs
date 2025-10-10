use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::util::horner;
use uacalc::util::simple_list;
use std::sync::Arc;

/// Helper function to convert PyObject to Arc<dyn Any + Send + Sync>
fn pyobject_to_any(obj: PyObject) -> PyResult<Arc<dyn std::any::Any + Send + Sync>> {
    Python::with_gil(|py| {
        // Try to extract common Python types
        if let Ok(int_val) = obj.extract::<i32>(py) {
            Ok(Arc::new(int_val) as Arc<dyn std::any::Any + Send + Sync>)
        } else if let Ok(string_val) = obj.extract::<String>(py) {
            Ok(Arc::new(string_val) as Arc<dyn std::any::Any + Send + Sync>)
        } else if let Ok(bool_val) = obj.extract::<bool>(py) {
            Ok(Arc::new(bool_val) as Arc<dyn std::any::Any + Send + Sync>)
        } else if let Ok(str_val) = obj.extract::<&str>(py) {
            Ok(Arc::new(str_val.to_string()) as Arc<dyn std::any::Any + Send + Sync>)
        } else {
            // For other types, convert to string representation
            let str_repr = obj.to_string();
            Ok(Arc::new(str_repr) as Arc<dyn std::any::Any + Send + Sync>)
        }
    })
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
    inner: std::sync::Arc<simple_list::SimpleList>,
}

#[pymethods]
impl PySimpleList {
    /// Create a new empty SimpleList
    #[new]
    fn new() -> Self {
        PySimpleList {
            inner: simple_list::SimpleList::new(),
        }
    }
    
    /// Create a new SimpleList with a single element
    #[staticmethod]
    fn make_list(obj: PyObject) -> PyResult<Self> {
        // Convert Python object to a generic Any type
        let any_obj = pyobject_to_any(obj)?;
        let inner = simple_list::SimpleList::new().cons_any(any_obj);
        Ok(PySimpleList { inner })
    }
    
    /// Create a new SimpleList from a Python list
    #[staticmethod]
    fn from_list(py: Python, items: Vec<PyObject>) -> PyResult<Self> {
        let mut result = simple_list::SimpleList::new();
        for item in items.into_iter().rev() {
            let any_obj = pyobject_to_any(item)?;
            result = result.cons_any(any_obj);
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
        self.inner.first().map(|f| {
            Python::with_gil(|py| {
                // Try to downcast to common Python types
                if let Ok(int_val) = f.clone().downcast::<i32>() {
                    (*int_val).to_object(py)
                } else if let Ok(string_val) = f.clone().downcast::<String>() {
                    (*string_val).to_object(py)
                } else if let Ok(bool_val) = f.clone().downcast::<bool>() {
                    (*bool_val).to_object(py)
                } else {
                    // For other types, convert to string representation
                    format!("{:?}", f).to_object(py)
                }
            })
        })
    }
    
    /// Get the rest of the list
    fn rest(&self) -> PySimpleList {
        PySimpleList {
            inner: self.inner.rest(),
        }
    }
    
    /// Add an element to the front of the list (cons operation)
    fn cons(&self, obj: PyObject) -> PyResult<Self> {
        let any_obj = pyobject_to_any(obj)?;
        let inner = self.inner.cons_any(any_obj);
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
        // For now, we'll do a simple comparison by converting to string
        // This is a limitation of the current implementation
        let obj_str = obj.to_string();
        let mut current = &*self.inner;
        loop {
            match current {
                simple_list::SimpleList::Empty => return false,
                simple_list::SimpleList::Cons { first, rest } => {
                    let first_str = if let Ok(int_val) = first.clone().downcast::<i32>() {
                        (*int_val).to_string()
                    } else if let Ok(string_val) = first.clone().downcast::<String>() {
                        (*string_val).clone()
                    } else if let Ok(bool_val) = first.clone().downcast::<bool>() {
                        (*bool_val).to_string()
                    } else {
                        format!("{:?}", first)
                    };
                    
                    if first_str == obj_str {
                        return true;
                    }
                    current = rest;
                }
            }
        }
    }
    
    /// Get element at index
    fn get(&self, index: usize) -> PyResult<Option<PyObject>> {
        match self.inner.get_safe(index) {
            Ok(Some(item)) => {
                Ok(Some(Python::with_gil(|py| {
                    // Try to downcast to common Python types
                    if let Ok(int_val) = item.clone().downcast::<i32>() {
                        (*int_val).to_object(py)
                    } else if let Ok(string_val) = item.clone().downcast::<String>() {
                        (*string_val).to_object(py)
                    } else if let Ok(bool_val) = item.clone().downcast::<bool>() {
                        (*bool_val).to_object(py)
                    } else {
                        format!("{:?}", item).to_object(py)
                    }
                })))
            }
            Ok(None) => Ok(None),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Find index of an element
    fn index_of(&self, obj: PyObject) -> Option<usize> {
        let obj_str = obj.to_string();
        let mut current = &*self.inner;
        let mut index = 0;
        
        loop {
            match current {
                simple_list::SimpleList::Empty => return None,
                simple_list::SimpleList::Cons { first, rest } => {
                    let first_str = if let Ok(int_val) = first.clone().downcast::<i32>() {
                        (*int_val).to_string()
                    } else if let Ok(string_val) = first.clone().downcast::<String>() {
                        (*string_val).clone()
                    } else if let Ok(bool_val) = first.clone().downcast::<bool>() {
                        (*bool_val).to_string()
                    } else {
                        format!("{:?}", first)
                    };
                    
                    if first_str == obj_str {
                        return Some(index);
                    }
                    current = rest;
                    index += 1;
                }
            }
        }
    }
    
    /// Find last index of an element
    fn last_index_of(&self, obj: PyObject) -> Option<usize> {
        let obj_str = obj.to_string();
        let mut last_index = None;
        let mut current = &*self.inner;
        let mut index = 0;
        
        loop {
            match current {
                simple_list::SimpleList::Empty => return last_index,
                simple_list::SimpleList::Cons { first, rest } => {
                    let first_str = if let Ok(int_val) = first.clone().downcast::<i32>() {
                        (*int_val).to_string()
                    } else if let Ok(string_val) = first.clone().downcast::<String>() {
                        (*string_val).clone()
                    } else if let Ok(bool_val) = first.clone().downcast::<bool>() {
                        (*bool_val).to_string()
                    } else {
                        format!("{:?}", first)
                    };
                    
                    if first_str == obj_str {
                        last_index = Some(index);
                    }
                    current = rest;
                    index += 1;
                }
            }
        }
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
        let mut result = Vec::new();
        let mut current = &*self.inner;
        
        loop {
            match current {
                simple_list::SimpleList::Empty => break,
                simple_list::SimpleList::Cons { first, rest } => {
                    // Try to downcast to common Python types
                    let py_obj = if let Ok(int_val) = first.clone().downcast::<i32>() {
                        (*int_val).to_object(py)
                    } else if let Ok(string_val) = first.clone().downcast::<String>() {
                        (*string_val).to_object(py)
                    } else if let Ok(bool_val) = first.clone().downcast::<bool>() {
                        (*bool_val).to_object(py)
                    } else {
                        format!("{:?}", first).to_object(py)
                    };
                    result.push(py_obj);
                    current = rest;
                }
            }
        }
        
        Ok(result)
    }
    
    /// Check if this list contains all elements from another list
    fn contains_all(&self, other: &PySimpleList) -> bool {
        // Simple implementation - check each element
        let other_list = Python::with_gil(|py| other.to_list(py));
        if let Ok(other_list) = other_list {
            for item in other_list {
                if !self.contains(item) {
                    return false;
                }
            }
        }
        true
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
    current: std::sync::Arc<simple_list::SimpleList>,
}

#[pymethods]
impl PySimpleListIterator {
    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }
    
    fn __next__(&mut self, py: Python) -> PyResult<Option<PyObject>> {
        match self.current.as_ref() {
            simple_list::SimpleList::Empty => Ok(None),
            simple_list::SimpleList::Cons { first, rest } => {
                let result = if let Ok(int_val) = first.clone().downcast::<i32>() {
                    (*int_val).to_object(py)
                } else if let Ok(string_val) = first.clone().downcast::<String>() {
                    (*string_val).to_object(py)
                } else if let Ok(bool_val) = first.clone().downcast::<bool>() {
                    (*bool_val).to_object(py)
                } else {
                    format!("{:?}", first).to_object(py)
                };
                self.current = rest.clone();
                Ok(Some(result))
            }
        }
    }
}

impl PySimpleListIterator {
    fn new(list: std::sync::Arc<simple_list::SimpleList>) -> Self {
        Self { current: list }
    }
}

pub fn register_util_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyHorner>()?;
    m.add_class::<PySimpleList>()?;
    m.add_class::<PySimpleListIterator>()?;
    Ok(())
}
