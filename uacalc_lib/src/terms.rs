use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyList;
use uacalc::terms::*;
use uacalc::alg::op::OperationSymbol;
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
    /// * `algebra` - The algebra in which to evaluate (a BasicSmallAlgebra from Python)
    /// * `var_map` - A dictionary mapping variable names to integer values
    /// 
    /// # Returns
    /// The value assigned to this variable
    fn eval(&self, algebra: &crate::alg::PyBasicSmallAlgebra, var_map: HashMap<String, i32>) -> PyResult<i32> {
        self.inner.eval(&algebra.inner, &var_map)
            .map_err(|e| PyValueError::new_err(e))
    }
    
    /// Evaluate this variable as an integer
    /// 
    /// # Arguments
    /// * `algebra` - The algebra in which to evaluate
    /// * `var_map` - A dictionary mapping variable names to integer values
    /// 
    /// # Returns
    /// The integer value assigned to this variable
    fn int_eval(&self, algebra: &crate::alg::PyBasicSmallAlgebra, var_map: HashMap<String, i32>) -> PyResult<i32> {
        self.inner.int_eval(&algebra.inner, &var_map)
            .map_err(|e| PyValueError::new_err(e))
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

/// Python wrapper for NonVariableTerm
#[pyclass]
pub struct PyNonVariableTerm {
    inner: NonVariableTerm,
}

#[pymethods]
impl PyNonVariableTerm {
    /// Create a new non-variable term.
    /// 
    /// # Arguments
    /// * `op_sym` - The operation symbol (a PyOperationSymbol)
    /// * `children` - List of child terms (PyVariableImp or PyNonVariableTerm)
    /// 
    /// # Returns
    /// A new non-variable term
    #[new]
    fn new(op_sym: &crate::alg::PyOperationSymbol, children: &Bound<'_, PyList>) -> PyResult<Self> {
        // Convert Python children to Rust Box<dyn Term>
        let mut rust_children: Vec<Box<dyn Term>> = Vec::new();
        
        for item in children.iter() {
            // Try to extract as PyVariableImp first
            if let Ok(var) = item.extract::<PyRef<PyVariableImp>>() {
                rust_children.push(Box::new(var.inner.clone()));
            } else if let Ok(nvt) = item.extract::<PyRef<PyNonVariableTerm>>() {
                // For NonVariableTerm, we need to create a new one since it doesn't implement Clone
                // For now, return an error
                return Err(PyValueError::new_err(
                    "NonVariableTerm children are not yet supported (requires cloning)"
                ));
            } else {
                return Err(PyValueError::new_err(
                    "Children must be VariableImp or NonVariableTerm instances"
                ));
            }
        }
        
        Ok(PyNonVariableTerm {
            inner: NonVariableTerm::new(op_sym.inner.clone(), rust_children),
        })
    }
    
    /// Create a constant term from an operation symbol.
    /// 
    /// # Arguments
    /// * `sym` - The operation symbol (must have arity 0)
    /// 
    /// # Returns
    /// A constant term
    #[staticmethod]
    fn make_constant_term(sym: &crate::alg::PyOperationSymbol) -> Self {
        PyNonVariableTerm {
            inner: NonVariableTerm::make_constant_term(sym.inner.clone()),
        }
    }
    
    /// Check if this term is a variable (always false for NonVariableTerm)
    fn isa_variable(&self) -> bool {
        self.inner.isa_variable()
    }
    
    /// Get the depth of this term
    fn depth(&self) -> i32 {
        self.inner.depth()
    }
    
    /// Get the length of this term
    fn length(&self) -> i32 {
        self.inner.length()
    }
    
    /// Get the list of variables in this term
    fn get_variable_list(&self) -> Vec<String> {
        self.inner.get_variable_list()
    }
    
    /// Evaluate this term using the given algebra and variable assignment
    /// 
    /// # Arguments
    /// * `algebra` - The algebra in which to evaluate (a BasicSmallAlgebra from Python)
    /// * `var_map` - A dictionary mapping variable names to integer values
    /// 
    /// # Returns
    /// The result of evaluating the term
    fn eval(&self, algebra: &crate::alg::PyBasicSmallAlgebra, var_map: HashMap<String, i32>) -> PyResult<i32> {
        self.inner.eval(&algebra.inner, &var_map)
            .map_err(|e| PyValueError::new_err(e))
    }
    
    /// Evaluate this term as an integer
    /// 
    /// # Arguments
    /// * `algebra` - The algebra in which to evaluate
    /// * `var_map` - A dictionary mapping variable names to integer values
    /// 
    /// # Returns
    /// The integer result of evaluating the term
    fn int_eval(&self, algebra: &crate::alg::PyBasicSmallAlgebra, var_map: HashMap<String, i32>) -> PyResult<i32> {
        self.inner.int_eval(&algebra.inner, &var_map)
            .map_err(|e| PyValueError::new_err(e))
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("NonVariableTerm({})", self.inner)
    }
}

pub fn register_terms_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyVariableImp>()?;
    m.add_class::<PyNonVariableTerm>()?;
    
    // Export only clean names (without Py prefix)
    m.add("VariableImp", m.getattr("PyVariableImp")?)?;
    m.add("NonVariableTerm", m.getattr("PyNonVariableTerm")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyVariableImp")?;
    module_dict.del_item("PyNonVariableTerm")?;
    
    Ok(())
}
