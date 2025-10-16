use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::eq::{Equation, equations};
use uacalc::terms::Term;  // Import Term trait for clone_box method
use std::collections::HashMap;
use std::sync::Arc;

/// Python wrapper for Equation
#[pyclass]
pub struct PyEquation {
    inner: Equation,
}

#[pymethods]
impl PyEquation {
    /// Create a new equation with left and right term sides.
    /// 
    /// # Arguments
    /// * `left` - The left side term (VariableImp or NonVariableTerm)
    /// * `right` - The right side term (VariableImp or NonVariableTerm)
    /// * `vars` - Optional list of variable names (default: computed from terms)
    /// 
    /// # Returns
    /// A new Equation instance
    #[new]
    #[pyo3(signature = (left, right, vars=None))]
    fn new(left: &Bound<'_, PyAny>, right: &Bound<'_, PyAny>, vars: Option<Vec<String>>) -> PyResult<Self> {
        // Convert left term
        let left_term = convert_to_term(left)?;
        
        // Convert right term
        let right_term = convert_to_term(right)?;
        
        // Create equation
        let inner = if let Some(var_list) = vars {
            Equation::new_with_vars(left_term, right_term, var_list)
        } else {
            Equation::new(left_term, right_term)
        };
        
        Ok(PyEquation { inner })
    }
    
    /// Get the left side term as a string representation.
    /// 
    /// # Returns
    /// String representation of the left side term
    fn left_side(&self) -> String {
        format!("{}", self.inner.left_side())
    }
    
    /// Get the right side term as a string representation.
    /// 
    /// # Returns
    /// String representation of the right side term
    fn right_side(&self) -> String {
        format!("{}", self.inner.right_side())
    }
    
    /// Get the variable list for this equation.
    /// 
    /// This is computed lazily by merging the variable lists of both sides.
    /// 
    /// # Returns
    /// List of all variables in the equation
    fn get_variable_list(&self) -> Vec<String> {
        self.inner.get_variable_list()
    }
    
    /// Get all operation symbols used in this equation.
    /// 
    /// # Returns
    /// List of operation symbol names with arities (e.g., "f/2" for binary operation f)
    fn get_operation_symbols(&self) -> Vec<String> {
        self.inner.get_operation_symbols()
            .into_iter()
            .map(|sym| format!("{}/{}", sym.name(), sym.arity()))
            .collect()
    }
    
    /// Find where this equation fails in the given algebra.
    /// 
    /// # Arguments
    /// * `algebra` - The algebra to check (BasicSmallAlgebra from Python)
    /// 
    /// # Returns
    /// * List of variable values where the equation fails
    /// * None if the equation holds in the algebra
    fn find_failure(&self, algebra: &crate::alg::PyBasicSmallAlgebra) -> PyResult<Option<Vec<i32>>> {
        let alg_arc: Arc<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>> = Arc::new(algebra.inner.clone());
        self.inner.find_failure(alg_arc)
            .map_err(|e| PyValueError::new_err(e))
    }
    
    /// Find where this equation fails in the given algebra as a variable map.
    /// 
    /// # Arguments
    /// * `algebra` - The algebra to check (BasicSmallAlgebra from Python)
    /// 
    /// # Returns
    /// * Dictionary from variable names to values where the equation fails
    /// * None if the equation holds in the algebra
    fn find_failure_map(&self, algebra: &crate::alg::PyBasicSmallAlgebra) -> PyResult<Option<HashMap<String, i32>>> {
        let alg_arc: Arc<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>> = Arc::new(algebra.inner.clone());
        self.inner.find_failure_map(alg_arc)
            .map_err(|e| PyValueError::new_err(e))
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("Equation({})", self.inner)
    }
}

/// Helper function to convert Python term objects to Rust Box<dyn Term>
fn convert_to_term(obj: &Bound<'_, PyAny>) -> PyResult<Box<dyn uacalc::terms::Term>> {
    // Try to extract as VariableImp
    if let Ok(var) = obj.extract::<pyo3::PyRef<crate::terms::PyVariableImp>>() {
        return Ok(Box::new(var.inner.clone()));
    }
    
    // Try to extract as NonVariableTerm
    if let Ok(nvt) = obj.extract::<pyo3::PyRef<crate::terms::PyNonVariableTerm>>() {
        return Ok(nvt.inner.clone_box());
    }
    
    Err(PyValueError::new_err(
        "Term must be a VariableImp or NonVariableTerm instance"
    ))
}

/// Create associative law equation: f(x,f(y,z)) = f(f(x,y),z)
/// 
/// The operation symbol must have arity 2.
/// 
/// # Arguments
/// * `op_symbol` - The operation symbol (must have arity 2)
/// 
/// # Returns
/// * `PyEquation` - The associative law equation
/// 
/// # Raises
/// * `ValueError` - If the arity is not 2
#[pyfunction]
fn associative_law(op_symbol: &crate::alg::PyOperationSymbol) -> PyResult<PyEquation> {
    let equation = equations::associative_law(&op_symbol.get_inner())
        .map_err(|e| PyValueError::new_err(e))?;
    Ok(PyEquation { inner: equation })
}

/// Create cyclic law equation: f(x0,x1,...,x{k-1}) = f(x{k-1},x0,...,x{k-2})
/// 
/// The operation symbol must have arity at least 1.
/// 
/// # Arguments
/// * `op_symbol` - The operation symbol (must have arity >= 1)
/// 
/// # Returns
/// * `PyEquation` - The cyclic law equation
/// 
/// # Raises
/// * `ValueError` - If the arity is less than 1
#[pyfunction]
fn cyclic_law(op_symbol: &crate::alg::PyOperationSymbol) -> PyResult<PyEquation> {
    let equation = equations::cyclic_law(&op_symbol.get_inner())
        .map_err(|e| PyValueError::new_err(e))?;
    Ok(PyEquation { inner: equation })
}

/// Create first-second symmetric law equation: f(x0,x1,x2,...,xk) = f(x1,x0,x2,...,xk)
/// 
/// The operation symbol must have arity at least 2.
/// 
/// # Arguments
/// * `op_symbol` - The operation symbol (must have arity >= 2)
/// 
/// # Returns
/// * `PyEquation` - The first-second symmetric law equation
/// 
/// # Raises
/// * `ValueError` - If the arity is less than 2
#[pyfunction]
fn first_second_symmetric_law(op_symbol: &crate::alg::PyOperationSymbol) -> PyResult<PyEquation> {
    let equation = equations::first_second_symmetric_law(&op_symbol.get_inner())
        .map_err(|e| PyValueError::new_err(e))?;
    Ok(PyEquation { inner: equation })
}

pub fn register_eq_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyEquation>()?;
    
    // Register equation generation functions
    m.add_function(wrap_pyfunction!(associative_law, m)?)?;
    m.add_function(wrap_pyfunction!(cyclic_law, m)?)?;
    m.add_function(wrap_pyfunction!(first_second_symmetric_law, m)?)?;
    
    // Export only clean names (without Py prefix)
    m.add("Equation", m.getattr("PyEquation")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyEquation")?;
    
    Ok(())
}
