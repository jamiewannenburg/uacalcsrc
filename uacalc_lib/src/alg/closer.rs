use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::sync::Arc;
use uacalc::alg::Closer;
use uacalc::util::int_array::IntArray;
use crate::alg::big_product_algebra::PyBigProductAlgebra;
use crate::util::PyIntArray;

/// Python wrapper for Closer
#[pyclass]
pub struct PyCloser {
    inner: Closer<i32>,
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

        match Closer::new_safe(algebra.get_inner(), rust_gens) {
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

    /// Compute the closure using the specialized power algebra algorithm.
    ///
    /// This method matches Java's `sgClosePower()` public method and uses
    /// the optimized power algebra closure algorithm.
    ///
    /// # Returns
    /// List of IntArray elements in the closure
    fn sg_close_power(&mut self) -> PyResult<Vec<PyIntArray>> {
        match self.inner.sg_close_power() {
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

    /// Get the elements to find.
    ///
    /// # Returns
    /// List of IntArray elements to find, if set
    fn get_elements_to_find(&self) -> Option<Vec<PyIntArray>> {
        self.inner.get_elements_to_find()
            .map(|elts| elts.iter()
                .map(|ia| PyIntArray { inner: ia.clone() })
                .collect())
    }

    /// Set the elements to find.
    ///
    /// # Arguments
    /// * `elements` - List of IntArray elements to search for during closure
    fn set_elements_to_find(&mut self, elements: Vec<PyIntArray>) -> PyResult<()> {
        let rust_elts: Vec<IntArray> = elements.iter()
            .map(|e| e.inner.clone())
            .collect();
        
        let generators = self.inner.get_generators();
        self.inner.set_elements_to_find(rust_elts, generators);
        Ok(())
    }

    /// Check if all elements have been found.
    ///
    /// # Returns
    /// True if all elements in elts_to_find have been found
    fn all_elements_found(&self) -> bool {
        self.inner.all_elements_found()
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

pub fn register_closer(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyCloser>()?;
    Ok(())
}






