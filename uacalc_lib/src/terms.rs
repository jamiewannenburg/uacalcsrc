use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyList;
use uacalc::terms::{VariableImp, NonVariableTerm, Term, Variable};
use std::collections::HashMap;

/// Python wrapper for VariableImp
#[pyclass]
pub struct PyVariableImp {
    pub(crate) inner: VariableImp,
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
    pub(crate) inner: NonVariableTerm,
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
                // Now we can clone NonVariableTerm!
                rust_children.push(nvt.inner.clone_box());
            } else {
                return Err(PyValueError::new_err(
                    "Children must be VariableImp or NonVariableTerm instances"
                ));
            }
        }
        
        Ok(PyNonVariableTerm {
            inner: NonVariableTerm::new(op_sym.get_inner(), rust_children),
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
            inner: NonVariableTerm::make_constant_term(sym.get_inner()),
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

// ============================================================================
// Terms Utility Functions - Python Bindings
// ============================================================================

/// Parse a string representation into a Term.
/// 
/// # Arguments
/// * `s` - The string representation of the term
/// 
/// # Returns
/// * `VariableImp` if the term is a variable
/// * `NonVariableTerm` if the term is a compound term
/// 
/// # Examples
/// ```python
/// import uacalc_lib
/// 
/// # Parse a variable
/// x = uacalc_lib.terms.string_to_term("x")
/// assert x.get_name() == "x"
/// 
/// # Parse a compound term
/// term = uacalc_lib.terms.string_to_term("f(x,y)")
/// assert term.to_string() == "f(x,y)"
/// ```
#[pyfunction]
fn string_to_term(s: String) -> PyResult<PyObject> {
    Python::with_gil(|py| {
        match uacalc::terms::string_to_term(&s) {
            Ok(term) => {
                // Check if it's a variable or non-variable term
                if term.isa_variable() {
                    // Extract the variable name from the term
                    let var_name = format!("{}", term);
                    let py_var = PyVariableImp {
                        inner: VariableImp::new(&var_name),
                    };
                    Ok(py_var.into_py(py))
                } else {
                    // It's a non-variable term, but we need to reconstruct it
                    // from the boxed term - for now, create from the original implementation
                    // This is a bit hacky but works
                    let py_term = reconstruct_non_variable_term(term.as_ref())?;
                    Ok(py_term.into_py(py))
                }
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    })
}

// Helper function to reconstruct a PyNonVariableTerm from a Term trait object
fn reconstruct_non_variable_term(term: &dyn Term) -> PyResult<PyNonVariableTerm> {
    if term.isa_variable() {
        return Err(PyValueError::new_err("Cannot reconstruct a variable as NonVariableTerm"));
    }
    
    let op_sym = term.leading_operation_symbol()
        .ok_or_else(|| PyValueError::new_err("Term has no leading operation symbol"))?;
    
    let children = term.get_children()
        .ok_or_else(|| PyValueError::new_err("Term has no children"))?;
    
    Ok(PyNonVariableTerm {
        inner: NonVariableTerm::new(op_sym.clone(), children),
    })
}

/// Validate if a string can be a variable name.
/// 
/// # Arguments
/// * `s` - The string to validate
/// 
/// # Returns
/// `True` if the string is a valid variable name, `False` otherwise
/// 
/// # Examples
/// ```python
/// import uacalc_lib
/// 
/// assert uacalc_lib.terms.is_valid_var_string("x")
/// assert uacalc_lib.terms.is_valid_var_string("var1")
/// assert not uacalc_lib.terms.is_valid_var_string("")
/// assert not uacalc_lib.terms.is_valid_var_string("1x")
/// ```
#[pyfunction]
fn is_valid_var_string(s: String) -> bool {
    uacalc::terms::is_valid_var_string(&s)
}

/// Validate if a string can be an operation name.
/// 
/// # Arguments
/// * `s` - The string to validate
/// 
/// # Returns
/// `True` if the string is a valid operation name, `False` otherwise
/// 
/// # Examples
/// ```python
/// import uacalc_lib
/// 
/// assert uacalc_lib.terms.is_valid_op_name_string("f")
/// assert uacalc_lib.terms.is_valid_op_name_string("add")
/// assert not uacalc_lib.terms.is_valid_op_name_string("")
/// ```
#[pyfunction]
fn is_valid_op_name_string(s: String) -> bool {
    uacalc::terms::is_valid_op_name_string(&s)
}

/// Flatten associative operations in a term.
/// 
/// # Arguments
/// * `term` - The term to flatten (VariableImp or NonVariableTerm)
/// 
/// # Returns
/// A new term with associative operations flattened
/// 
/// # Examples
/// ```python
/// import uacalc_lib
/// 
/// # Parse a term with nested associative operations
/// # Note: This assumes the operation is marked as associative
/// term = uacalc_lib.terms.string_to_term("f(f(x,y),z)")
/// flattened = uacalc_lib.terms.flatten(term)
/// ```
#[pyfunction]
fn flatten(term: &Bound<'_, PyAny>) -> PyResult<PyObject> {
    Python::with_gil(|py| {
        // Try to extract as PyVariableImp first
        if let Ok(var) = term.extract::<PyRef<PyVariableImp>>() {
            let term_ref: &dyn Term = &var.inner;
            let flattened = uacalc::terms::flatten(term_ref);
            
            if flattened.isa_variable() {
                let var_name = format!("{}", flattened);
                let py_var = PyVariableImp {
                    inner: VariableImp::new(&var_name),
                };
                Ok(py_var.into_py(py))
            } else {
                let py_term = reconstruct_non_variable_term(flattened.as_ref())?;
                Ok(py_term.into_py(py))
            }
        } else if let Ok(nvt) = term.extract::<PyRef<PyNonVariableTerm>>() {
            let term_ref: &dyn Term = &nvt.inner;
            let flattened = uacalc::terms::flatten(term_ref);
            
            if flattened.isa_variable() {
                let var_name = format!("{}", flattened);
                let py_var = PyVariableImp {
                    inner: VariableImp::new(&var_name),
                };
                Ok(py_var.into_py(py))
            } else {
                let py_term = reconstruct_non_variable_term(flattened.as_ref())?;
                Ok(py_term.into_py(py))
            }
        } else {
            Err(PyValueError::new_err(
                "Term must be a VariableImp or NonVariableTerm instance"
            ))
        }
    })
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
    
    // Register utility functions
    m.add_function(wrap_pyfunction!(string_to_term, m)?)?;
    m.add_function(wrap_pyfunction!(is_valid_var_string, m)?)?;
    m.add_function(wrap_pyfunction!(is_valid_op_name_string, m)?)?;
    m.add_function(wrap_pyfunction!(flatten, m)?)?;
    
    Ok(())
}
