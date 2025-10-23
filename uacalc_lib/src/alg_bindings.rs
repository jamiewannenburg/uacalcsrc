use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::sync::Arc;
use std::collections::HashMap;
use uacalc::alg::{Closer, BigProductAlgebra, SmallAlgebra, BasicSmallAlgebra, Algebra};
use uacalc::util::int_array::{IntArray, IntArrayTrait};

/// Python wrapper for Closer
#[pyclass(name = "Closer")]
pub struct PyCloser {
    inner: Closer,
}

#[pymethods]
impl PyCloser {
    /// Create a new Closer with an algebra and generators.
    /// 
    /// # Arguments
    /// * `algebra` - The BigProductAlgebra to work with
    /// * `generators` - List of IntArray generators
    /// 
    /// # Returns
    /// A new Closer instance
    #[new]
    fn new(algebra: &PyBigProductAlgebra, generators: Vec<PyIntArray>) -> PyResult<Self> {
        let rust_gens: Vec<IntArray> = generators.iter()
            .map(|g| g.inner.clone())
            .collect();
        
        match Closer::new_safe(Arc::clone(&algebra.inner), rust_gens) {
            Ok(closer) => Ok(PyCloser { inner: closer }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the generators.
    /// 
    /// # Returns
    /// List of IntArray generators
    fn get_generators(&self) -> Vec<PyIntArray> {
        self.inner.get_generators()
            .iter()
            .map(|ia| PyIntArray { inner: ia.clone() })
            .collect()
    }
    
    /// Get the answer (closure result).
    /// 
    /// # Returns
    /// List of IntArray elements in the closure
    fn get_answer(&self) -> Vec<PyIntArray> {
        self.inner.get_answer()
            .iter()
            .map(|ia| PyIntArray { inner: ia.clone() })
            .collect()
    }
    
    /// Compute the closure of the generators.
    /// 
    /// # Returns
    /// List of IntArray elements in the closure
    fn sg_close(&mut self) -> PyResult<Vec<PyIntArray>> {
        match self.inner.sg_close() {
            Ok(result) => Ok(result.iter()
                .map(|ia| PyIntArray { inner: ia.clone() })
                .collect()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Set whether to suppress output.
    /// 
    /// # Arguments
    /// * `suppress` - Whether to suppress output
    fn set_suppress_output(&mut self, suppress: bool) {
        self.inner.set_suppress_output(suppress);
    }
    
    /// Get whether output is suppressed.
    /// 
    /// # Returns
    /// True if output is suppressed
    fn is_suppress_output(&self) -> bool {
        self.inner.is_suppress_output()
    }
    
    /// Set the maximum size.
    /// 
    /// # Arguments
    /// * `max_size` - Maximum size (None for no limit)
    fn set_max_size(&mut self, max_size: Option<usize>) {
        self.inner.set_max_size(max_size);
    }
    
    /// Get the maximum size.
    /// 
    /// # Returns
    /// The maximum size, if set
    fn get_max_size(&self) -> Option<usize> {
        self.inner.get_max_size()
    }
    
    /// Check if closure completed successfully.
    /// 
    /// # Returns
    /// True if closure completed
    fn is_completed(&self) -> bool {
        self.inner.is_completed()
    }
    
    fn __str__(&self) -> String {
        format!("Closer(generators: {}, answer_size: {})",
            self.inner.get_generators().len(),
            self.inner.get_answer().len())
    }
    
    fn __repr__(&self) -> String {
        self.__str__()
    }
}

/// Python wrapper for BigProductAlgebra
#[pyclass(name = "BigProductAlgebra")]
pub struct PyBigProductAlgebra {
    inner: Arc<BigProductAlgebra>,
}

#[pymethods]
impl PyBigProductAlgebra {
    /// Create a new BigProductAlgebra from a list of SmallAlgebras.
    /// 
    /// # Arguments
    /// * `algebras` - List of SmallAlgebra instances
    /// 
    /// # Returns
    /// A new BigProductAlgebra instance
    #[staticmethod]
    fn new_from_algebras(algebras: Vec<PySmallAlgebra>) -> PyResult<Self> {
        let rust_algs: Vec<Box<dyn SmallAlgebra<UniverseItem = i32>>> = algebras.iter()
            .map(|a| a.inner.clone_box())
            .collect();
        
        match BigProductAlgebra::new_safe(rust_algs) {
            Ok(algebra) => Ok(PyBigProductAlgebra { inner: Arc::new(algebra) }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new BigProductAlgebra as a power.
    /// 
    /// # Arguments
    /// * `algebra` - The base algebra
    /// * `power` - The power
    /// 
    /// # Returns
    /// A new BigProductAlgebra instance
    #[staticmethod]
    fn new_power(algebra: &PySmallAlgebra, power: usize) -> PyResult<Self> {
        let rust_alg = algebra.inner.clone_box();
        
        match BigProductAlgebra::new_power_safe(rust_alg, power) {
            Ok(algebra) => Ok(PyBigProductAlgebra { inner: Arc::new(algebra) }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the number of factors.
    /// 
    /// # Returns
    /// The number of factors
    fn get_number_of_factors(&self) -> usize {
        self.inner.get_number_of_factors()
    }
    
    /// Check if this is a power algebra.
    /// 
    /// # Returns
    /// True if this is a power
    fn is_power(&self) -> bool {
        self.inner.is_power()
    }
    
    /// Get the name of the algebra.
    /// 
    /// # Returns
    /// The name
    fn name(&self) -> String {
        self.inner.name().to_string()
    }
    
    /// Get the cardinality.
    /// 
    /// # Returns
    /// The cardinality
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }
    
    fn __str__(&self) -> String {
        format!("BigProductAlgebra(name: {}, factors: {})",
            self.inner.name(),
            self.inner.get_number_of_factors())
    }
    
    fn __repr__(&self) -> String {
        self.__str__()
    }
}

/// Python wrapper for SmallAlgebra (simplified for bindings)
#[pyclass(name = "SmallAlgebra")]
struct PySmallAlgebra {
    inner: Box<dyn SmallAlgebra<UniverseItem = i32>>,
}

#[pymethods]
impl PySmallAlgebra {
    /// Create a basic small algebra.
    /// 
    /// # Arguments
    /// * `name` - The name of the algebra
    /// * `size` - The size of the algebra
    /// 
    /// # Returns
    /// A new SmallAlgebra instance
    #[staticmethod]
    fn new_basic(name: String, size: usize) -> PyResult<Self> {
        use std::collections::HashSet;
        let universe: HashSet<i32> = (0..size as i32).collect();
        
        let alg = Box::new(BasicSmallAlgebra::new(
            name,
            universe,
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        Ok(PySmallAlgebra { inner: alg })
    }
    
    /// Get the name.
    fn name(&self) -> String {
        self.inner.name().to_string()
    }
    
    /// Get the cardinality.
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }
    
    fn __str__(&self) -> String {
        format!("SmallAlgebra(name: {}, cardinality: {})",
            self.inner.name(),
            self.inner.cardinality())
    }
    
    fn __repr__(&self) -> String {
        self.__str__()
    }
}

/// Python wrapper for IntArray
#[pyclass(name = "IntArray")]
#[derive(Clone)]
pub struct PyIntArray {
    inner: IntArray,
}

#[pymethods]
impl PyIntArray {
    /// Create a new IntArray.
    /// 
    /// # Arguments
    /// * `size` - The size of the array
    /// 
    /// # Returns
    /// A new IntArray instance
    #[new]
    fn new(size: usize) -> PyResult<Self> {
        match IntArray::new(size) {
            Ok(ia) => Ok(PyIntArray { inner: ia }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create an IntArray from a list.
    /// 
    /// # Arguments
    /// * `values` - The values
    /// 
    /// # Returns
    /// A new IntArray instance
    #[staticmethod]
    fn from_list(values: Vec<i32>) -> PyResult<Self> {
        match IntArray::from_array(values) {
            Ok(ia) => Ok(PyIntArray { inner: ia }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the size.
    fn size(&self) -> usize {
        self.inner.universe_size()
    }
    
    /// Get a value at an index.
    fn get(&self, index: usize) -> PyResult<i32> {
        match self.inner.get(index) {
            Some(val) => Ok(val),
            None => Err(PyValueError::new_err(format!("Index {} out of bounds", index))),
        }
    }
    
    /// Set a value at an index.
    fn set(&mut self, index: usize, value: i32) -> PyResult<()> {
        match self.inner.set(index, value) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Convert to a list.
    fn to_list(&self) -> Vec<i32> {
        let mut result = Vec::new();
        for i in 0..self.inner.universe_size() {
            if let Some(val) = self.inner.get(i) {
                result.push(val);
            }
        }
        result
    }
    
    fn __str__(&self) -> String {
        format!("{:?}", self.to_list())
    }
    
    fn __repr__(&self) -> String {
        format!("IntArray({:?})", self.to_list())
    }
    
    fn __eq__(&self, other: &PyIntArray) -> bool {
        self.inner == other.inner
    }
    
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }
}

pub fn register_alg_bindings(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyCloser>()?;
    m.add_class::<PyBigProductAlgebra>()?;
    m.add_class::<PySmallAlgebra>()?;
    m.add_class::<PyIntArray>()?;
    
    // Export clean names
    m.add("Closer", m.getattr("PyCloser")?)?;
    m.add("BigProductAlgebra", m.getattr("PyBigProductAlgebra")?)?;
    m.add("SmallAlgebra", m.getattr("PySmallAlgebra")?)?;
    m.add("IntArray", m.getattr("PyIntArray")?)?;
    
    // Remove Py* names
    let module_dict = m.dict();
    module_dict.del_item("PyCloser")?;
    module_dict.del_item("PyBigProductAlgebra")?;
    module_dict.del_item("PySmallAlgebra")?;
    module_dict.del_item("PyIntArray")?;
    
    Ok(())
}
