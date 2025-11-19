use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::collections::HashMap;
use crate::alg::op::parameterized_operation::PyParameterizedOperation;

/// Python wrapper for ParameterizedAlgebra
#[pyclass]
pub struct PyParameterizedAlgebra {
    inner: uacalc::alg::ParameterizedAlgebra,
}

#[pymethods]
impl PyParameterizedAlgebra {
    /// Create a new ParameterizedAlgebra.
    /// 
    /// Args:
    ///     parameter_names (list[str]): Names of the parameters
    ///     name (str): Name of the algebra
    ///     set_size_exp (str): Expression for set size
    ///     description (str): Description of the algebra
    ///     ops (list[ParameterizedOperation]): List of parameterized operations
    #[new]
    fn new(
        parameter_names: Vec<String>,
        name: String,
        set_size_exp: String,
        description: String,
        ops: Vec<PyParameterizedOperation>,
    ) -> Self {
        let rust_ops = ops.into_iter().map(|op| op.get_inner()).collect();
        PyParameterizedAlgebra {
            inner: uacalc::alg::ParameterizedAlgebra::new(
                parameter_names,
                name,
                set_size_exp,
                description,
                rust_ops,
            )
        }
    }
    
    /// Create a parameter map from values.
    /// 
    /// Args:
    ///     values (list[int]): List of integer values for the parameters
    /// 
    /// Returns:
    ///     dict[str, str]: Map from parameter names to string values
    /// 
    /// Raises:
    ///     ValueError: If the number of values doesn't match the number of parameters
    fn get_parameter_map(&self, values: Vec<i32>) -> PyResult<HashMap<String, String>> {
        match self.inner.get_parameter_map(&values) {
            Ok(map) => Ok(map),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the parameter names.
    /// 
    /// Returns:
    ///     list[str]: List of parameter names
    fn get_parameter_names(&self) -> Vec<String> {
        self.inner.parameter_names.clone()
    }
    
    /// Get the algebra name.
    /// 
    /// Returns:
    ///     str: The name of the algebra
    fn get_name(&self) -> String {
        self.inner.name.clone()
    }
    
    /// Get the set size expression.
    /// 
    /// Returns:
    ///     str: The set size expression
    fn get_set_size_exp(&self) -> String {
        self.inner.set_size_exp.clone()
    }
    
    /// Get the description.
    /// 
    /// Returns:
    ///     str: The description
    fn get_description(&self) -> String {
        self.inner.description.clone()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("ParameterizedAlgebra({})", self.inner.to_string())
    }
}

// PyParameterizedOperation is now in alg/op/parameterized_operation.rs