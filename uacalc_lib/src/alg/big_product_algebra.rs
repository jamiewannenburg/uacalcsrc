use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::sync::Arc;
use uacalc::alg::{BigProductAlgebra, SmallAlgebra, Algebra};
use crate::alg::small_algebra::PySmallAlgebra;

/// Python wrapper for BigProductAlgebra
#[pyclass(name = "BigProductAlgebra")]
pub struct PyBigProductAlgebra {
    inner: Arc<BigProductAlgebra<i32>>,
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
    fn new_from_algebras(algebras: &Bound<'_, PyAny>) -> PyResult<Self> {
        let py_algebras: Vec<PyRef<PySmallAlgebra>> = algebras.extract()?;
        let rust_algs: Vec<Box<dyn SmallAlgebra<UniverseItem = i32>>> = py_algebras.iter()
            .map(|a| a.clone_box())
            .collect();
        
        match BigProductAlgebra::<i32>::new_safe(rust_algs) {
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
        let rust_alg = algebra.clone_box();

        match BigProductAlgebra::<i32>::new_power_safe(rust_alg, power) {
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

impl PyBigProductAlgebra {
    /// Get the inner BigProductAlgebra (for internal use)
    pub(crate) fn get_inner(&self) -> Arc<BigProductAlgebra<i32>> {
        Arc::clone(&self.inner)
    }
}