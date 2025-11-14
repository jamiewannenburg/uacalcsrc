use pyo3::prelude::*;
use std::collections::HashMap;
use uacalc::alg::op::ParameterizedOperation;

/// Python wrapper for ParameterizedOperation
#[pyclass]
#[derive(Clone)]
pub struct PyParameterizedOperation {
    inner: uacalc::alg::op::ParameterizedOperation,
}

#[pymethods]
impl PyParameterizedOperation {
    /// Create a new ParameterizedOperation.
    ///
    /// Args:
    ///     name (str): Name of the operation
    ///     symbol_name (str): Symbol name for the operation
    ///     set_size_exp (str): Expression for set size
    ///     parameter_names (list[str]): Names of the parameters
    ///     arity_exp (str): Expression for arity
    ///     description (str): Description of the operation
    ///     default_value_exp (str): Expression for default value
    ///     definition_exp (str): Expression for operation definition
    #[new]
    fn new(
        name: String,
        symbol_name: String,
        set_size_exp: String,
        parameter_names: Vec<String>,
        arity_exp: String,
        description: String,
        default_value_exp: String,
        definition_exp: String,
    ) -> Self {
        PyParameterizedOperation {
            inner: uacalc::alg::op::ParameterizedOperation::new(
                name,
                symbol_name,
                set_size_exp,
                parameter_names,
                arity_exp,
                description,
                default_value_exp,
                definition_exp,
            )
        }
    }

    /// Substitute parameter values in a parameterized string.
    ///
    /// This is a simplified version that performs basic string substitution
    /// without full expression parsing.
    ///
    /// Args:
    ///     parameterized_string (str): String containing parameter references
    ///     parm_map (dict[str, str]): Map from parameter names to values
    ///
    /// Returns:
    ///     str: The string with parameters substituted
    #[staticmethod]
    fn sub_parm_values(parameterized_string: String, parm_map: HashMap<String, String>) -> String {
        uacalc::alg::op::ParameterizedOperation::sub_parm_values(&parameterized_string, &parm_map)
    }

    /// Get the operation name.
    ///
    /// Returns:
    ///     str: The name of the operation
    fn get_name(&self) -> String {
        self.inner.name.clone()
    }

    /// Get the symbol name.
    ///
    /// Returns:
    ///     str: The symbol name
    fn get_symbol_name(&self) -> String {
        self.inner.symbol_name.clone()
    }

    /// Get the set size expression.
    ///
    /// Returns:
    ///     str: The set size expression
    fn get_set_size_exp(&self) -> String {
        self.inner.set_size_exp.clone()
    }

    /// Get the parameter names.
    ///
    /// Returns:
    ///     list[str]: List of parameter names
    fn get_parameter_names(&self) -> Vec<String> {
        self.inner.parameter_names.clone()
    }

    /// Get the arity expression.
    ///
    /// Returns:
    ///     str: The arity expression
    fn get_arity_exp(&self) -> String {
        self.inner.arity_exp.clone()
    }

    /// Get the description.
    ///
    /// Returns:
    ///     str: The description
    fn get_description(&self) -> String {
        self.inner.description.clone()
    }

    /// Get the default value expression.
    ///
    /// Returns:
    ///     str: The default value expression
    fn get_default_value_exp(&self) -> String {
        self.inner.default_value_exp.clone()
    }

    /// Get the definition expression.
    ///
    /// Returns:
    ///     str: The definition expression
    fn get_definition_exp(&self) -> String {
        self.inner.definition_exp.clone()
    }

    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("ParameterizedOperation({})", self.inner.to_string())
    }
}

impl PyParameterizedOperation {
    pub(crate) fn get_inner(self) -> uacalc::alg::op::ParameterizedOperation {
        self.inner
    }
}