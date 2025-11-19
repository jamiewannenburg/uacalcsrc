use pyo3::prelude::*;
use uacalc::alg::CloserTiming;
use crate::alg::big_product_algebra::PyBigProductAlgebra;

/// Python wrapper for CloserTiming
#[pyclass]
pub struct PyCloserTiming {
    inner: CloserTiming,
}

#[pymethods]
impl PyCloserTiming {
    /// Create a new CloserTiming from a BigProductAlgebra.
    ///
    /// # Arguments
    /// * `algebra` - The BigProductAlgebra to get timing information for
    ///
    /// # Returns
    /// A new CloserTiming instance
    #[new]
    fn new(algebra: &PyBigProductAlgebra) -> PyResult<Self> {
        let algebra_arc = algebra.get_inner();
        let timing = CloserTiming::new_from_algebra(&*algebra_arc, None);
        Ok(PyCloserTiming { inner: timing })
    }
    
    /// Create a new CloserTiming with explicit arities and number of factors.
    ///
    /// # Arguments
    /// * `arities` - List of operation arities
    /// * `num_factors` - Number of factors in the product algebra
    ///
    /// # Returns
    /// A new CloserTiming instance
    #[staticmethod]
    fn new_with_params(arities: Vec<i32>, num_factors: u64) -> PyResult<Self> {
        let timing = CloserTiming::new(arities, num_factors, None);
        Ok(PyCloserTiming { inner: timing })
    }

    /// Update the pass information and reset counters.
    ///
    /// # Arguments
    /// * `size` - The size of the current pass
    fn update_pass(&mut self, size: u32) {
        self.inner.update_pass(size);
    }

    /// Increment application counters and update timing estimates.
    fn increment_apps(&mut self) {
        self.inner.increment_apps();
    }

    /// Increment the next pass size counter.
    fn increment_next_pass_size(&self) {
        self.inner.increment_next_pass_size();
    }

    /// Get the current pass number.
    ///
    /// # Returns
    /// The current pass number
    fn get_pass(&self) -> u32 {
        self.inner.get_pass()
    }

    /// Get the number of factors.
    ///
    /// # Returns
    /// The number of factors in the product algebra
    fn get_num_factors(&self) -> u64 {
        self.inner.get_num_factors()
    }

    /// Get the operation arities.
    ///
    /// # Returns
    /// List of operation arities
    fn get_arities(&self) -> Vec<i32> {
        self.inner.get_arities().to_vec()
    }

    /// Convert milliseconds to a formatted time string.
    ///
    /// # Arguments
    /// * `ms` - Time in milliseconds
    ///
    /// # Returns
    /// Formatted time string (e.g., "1:05" or "1:01:05")
    #[staticmethod]
    fn ms_to_string(ms: u64) -> String {
        CloserTiming::ms_to_string(ms)
    }

    fn __str__(&self) -> String {
        format!("CloserTiming(pass: {}, num_factors: {}, arities: {:?})",
            self.inner.get_pass(),
            self.inner.get_num_factors(),
            self.inner.get_arities())
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }
}

pub fn register_closer_timing(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyCloserTiming>()?;
    Ok(())
}

