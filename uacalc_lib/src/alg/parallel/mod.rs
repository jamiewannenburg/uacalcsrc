use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::parallel::Pool;

/// Python wrapper for Pool
#[pyclass]
pub struct PyPool;

#[pymethods]
impl PyPool {
    /// Get the ForkJoinPool-equivalent runtime.
    /// 
    /// Returns a reference to the lazily initialized, thread-safe runtime.
    /// This is equivalent to accessing Java's Pool.fjPool static field.
    /// 
    /// # Returns
    /// A runtime object that can be used for parallel processing.
    #[staticmethod]
    fn fj_pool() -> PyResult<String> {
        // For Python bindings, we just verify the pool can be accessed
        // The actual runtime is internal to Rust
        let _runtime = Pool::fj_pool();
        // Return a simple status indicating the pool is initialized
        Ok("initialized".to_string())
    }
    
    /// Check if the pool is initialized.
    /// 
    /// # Returns
    /// True if the pool has been initialized (always true after first access).
    #[staticmethod]
    fn is_initialized() -> bool {
        // Accessing fj_pool will initialize it if not already initialized
        let _runtime = Pool::fj_pool();
        true
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        "Pool()".to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        "Pool()".to_string()
    }
}

pub fn register_parallel_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyPool>()?;
    
    // Export only clean names (without Py prefix)
    m.add("Pool", m.getattr("PyPool")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyPool")?;
    
    Ok(())
}

