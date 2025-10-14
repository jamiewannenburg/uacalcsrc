use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::lat::*;

/// Python wrapper for DivisibilityOrder
#[pyclass]
pub struct PyDivisibilityOrder {
    inner: uacalc::lat::DivisibilityOrder,
}

#[pymethods]
impl PyDivisibilityOrder {
    /// Create a new DivisibilityOrder
    #[new]
    fn new() -> Self {
        PyDivisibilityOrder {
            inner: uacalc::lat::DivisibilityOrder,
        }
    }
    
    /// Check if a divides b (a ≤ b in divisibility order)
    fn leq(&self, a: i32, b: i32) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        "DivisibilityOrder".to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        "DivisibilityOrder()".to_string()
    }
}

/// Python wrapper for PrefixOrder
#[pyclass]
pub struct PyPrefixOrder {
    inner: uacalc::lat::PrefixOrder,
}

#[pymethods]
impl PyPrefixOrder {
    /// Create a new PrefixOrder
    #[new]
    fn new() -> Self {
        PyPrefixOrder {
            inner: uacalc::lat::PrefixOrder,
        }
    }
    
    /// Check if a is a prefix of b (a ≤ b in prefix order)
    fn leq(&self, a: String, b: String) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        "PrefixOrder".to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        "PrefixOrder()".to_string()
    }
}

/// Python wrapper for NaturalOrder
#[pyclass]
pub struct PyNaturalOrder {
    inner: uacalc::lat::NaturalOrder,
}

#[pymethods]
impl PyNaturalOrder {
    /// Create a new NaturalOrder
    #[new]
    fn new() -> Self {
        PyNaturalOrder {
            inner: uacalc::lat::NaturalOrder,
        }
    }
    
    /// Check if a ≤ b in natural order for integers
    fn leq_i32(&self, a: i32, b: i32) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Check if a ≤ b in natural order for unsigned integers
    fn leq_u32(&self, a: u32, b: u32) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Check if a ≤ b in natural order for strings
    fn leq_string(&self, a: String, b: String) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        "NaturalOrder".to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        "NaturalOrder()".to_string()
    }
}

pub fn register_lat_module(_py: Python, m: &PyModule) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyDivisibilityOrder>()?;
    m.add_class::<PyPrefixOrder>()?;
    m.add_class::<PyNaturalOrder>()?;
    
    // Export only clean names (without Py prefix)
    m.add("DivisibilityOrder", m.getattr("PyDivisibilityOrder")?)?;
    m.add("PrefixOrder", m.getattr("PyPrefixOrder")?)?;
    m.add("NaturalOrder", m.getattr("PyNaturalOrder")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyDivisibilityOrder")?;
    module_dict.del_item("PyPrefixOrder")?;
    module_dict.del_item("PyNaturalOrder")?;
    
    Ok(())
}
