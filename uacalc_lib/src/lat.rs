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

/// Find maximal elements in a collection using DivisibilityOrder
#[pyfunction]
fn maximals_divisibility(elems: Vec<i32>) -> PyResult<Vec<i32>> {
    let order = uacalc::lat::DivisibilityOrder;
    Ok(uacalc::lat::ordered_sets::maximals(&elems, &order))
}

/// Find maximal elements in a collection using PrefixOrder
#[pyfunction]
fn maximals_prefix(elems: Vec<String>) -> PyResult<Vec<String>> {
    let order = uacalc::lat::PrefixOrder;
    Ok(uacalc::lat::ordered_sets::maximals(&elems, &order))
}

/// Find maximal elements in a collection using NaturalOrder for integers
#[pyfunction]
fn maximals_natural_i32(elems: Vec<i32>) -> PyResult<Vec<i32>> {
    let order = uacalc::lat::NaturalOrder;
    Ok(uacalc::lat::ordered_sets::maximals(&elems, &order))
}

/// Find maximal elements in a collection using NaturalOrder for strings
#[pyfunction]
fn maximals_natural_string(elems: Vec<String>) -> PyResult<Vec<String>> {
    let order = uacalc::lat::NaturalOrder;
    Ok(uacalc::lat::ordered_sets::maximals(&elems, &order))
}

/// Run the main test function for ordered_sets
#[pyfunction]
fn ordered_sets_main() -> PyResult<String> {
    // Capture output from the main function
    let lst = vec![2, 3, 6, 35, 35 * 5];
    
    // Define divisibility order where a ≤ b if b % a == 0
    struct DivOrder;
    impl uacalc::lat::Order<i32> for DivOrder {
        fn leq(&self, a: &i32, b: &i32) -> bool {
            if *a == 0 { return true; }  // 0 divides everything by convention
            if *b == 0 { return *a == 0; }
            *a != 0 && *b % *a == 0
        }
    }
    
    let order = DivOrder;
    let maxs = uacalc::lat::ordered_sets::maximals(&lst, &order);
    
    Ok(format!("max's are {:?}", maxs))
}

pub fn register_lat_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyDivisibilityOrder>()?;
    m.add_class::<PyPrefixOrder>()?;
    m.add_class::<PyNaturalOrder>()?;
    
    // Export only clean names (without Py prefix)
    m.add("DivisibilityOrder", m.getattr("PyDivisibilityOrder")?)?;
    m.add("PrefixOrder", m.getattr("PyPrefixOrder")?)?;
    m.add("NaturalOrder", m.getattr("PyNaturalOrder")?)?;
    
    // Add OrderedSets functions
    m.add_function(wrap_pyfunction!(maximals_divisibility, m)?)?;
    m.add_function(wrap_pyfunction!(maximals_prefix, m)?)?;
    m.add_function(wrap_pyfunction!(maximals_natural_i32, m)?)?;
    m.add_function(wrap_pyfunction!(maximals_natural_string, m)?)?;
    m.add_function(wrap_pyfunction!(ordered_sets_main, m)?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyDivisibilityOrder")?;
    module_dict.del_item("PyPrefixOrder")?;
    module_dict.del_item("PyNaturalOrder")?;
    
    Ok(())
}
