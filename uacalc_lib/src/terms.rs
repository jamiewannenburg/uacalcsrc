use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::terms::*;
use std::collections::HashMap;

/// Python wrapper for VariableImp
#[pyclass]
pub struct PyVariableImp {
    inner: VariableImp,
}

#[pymethods]
impl PyVariableImp {
    /// Create a new variable with the given name.
    /// 
    /// # Arguments
    /// * `name` - The name of the variable
    /// 
    /// # Returns
    /// A new variable
    #[new]
    fn new(name: String) -> Self {
        PyVariableImp {
            inner: VariableImp::new(&name),
        }
    }
    
    /// Create the predefined variable x
    #[staticmethod]
    fn x() -> Self {
        PyVariableImp {
            inner: VariableImp::x(),
        }
    }
    
    /// Create the predefined variable y
    #[staticmethod]
    fn y() -> Self {
        PyVariableImp {
            inner: VariableImp::y(),
        }
    }
    
    /// Create the predefined variable z
    #[staticmethod]
    fn z() -> Self {
        PyVariableImp {
            inner: VariableImp::z(),
        }
    }
    
    /// Get the name of this variable
    fn get_name(&self) -> String {
        self.inner.get_name().to_string()
    }
    
    /// Check if this term is a variable (always true for VariableImp)
    fn isa_variable(&self) -> bool {
        self.inner.isa_variable()
    }
    
    /// Get the depth of this term (always 0 for variables)
    fn depth(&self) -> i32 {
        self.inner.depth()
    }
    
    /// Get the length of this term (always 1 for variables)
    fn length(&self) -> i32 {
        self.inner.length()
    }
    
    /// Get the list of variables (returns a list with just this variable)
    fn get_variable_list(&self) -> Vec<String> {
        self.inner.get_variable_list()
    }
    
    /// Evaluate this variable using the given variable assignment
    /// 
    /// # Arguments
    /// * `map` - A dictionary mapping variable names to integer values
    /// 
    /// # Returns
    /// The value assigned to this variable
    fn eval(&self, map: HashMap<String, i32>) -> PyResult<i32> {
        self.inner.eval(&map).map_err(|e| PyValueError::new_err(e))
    }
    
    /// Evaluate this variable as an integer
    /// 
    /// # Arguments
    /// * `map` - A dictionary mapping variable names to integer values
    /// 
    /// # Returns
    /// The integer value assigned to this variable
    fn int_eval(&self, map: HashMap<String, i32>) -> PyResult<i32> {
        self.inner.int_eval(&map).map_err(|e| PyValueError::new_err(e))
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("VariableImp(\"{}\")", self.inner.get_name())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyVariableImp) -> bool {
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

pub fn register_terms_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyVariableImp>()?;
    
    // Export only clean names (without Py prefix)
    m.add("VariableImp", m.getattr("PyVariableImp")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyVariableImp")?;
    
    Ok(())
}
