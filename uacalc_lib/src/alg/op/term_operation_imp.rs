use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::{PyAny, PyList};
use std::sync::Arc;
use uacalc::alg::op::{TermOperationImp, TermOperation, Operation};
use uacalc::alg::SmallAlgebra;
use uacalc::terms::{Term, Variable};
use crate::alg::PyBasicAlgebra;
use crate::terms::{PyVariableImp, PyNonVariableTerm};

/// Python wrapper for TermOperationImp
#[pyclass]
pub struct PyTermOperationImp {
    pub(crate) inner: TermOperationImp,
}

#[pymethods]
impl PyTermOperationImp {
    /// Create a new TermOperationImp from a term, variables, and algebra.
    ///
    /// This matches the Java API: `TermOperationImp(String name, Term term, List<Variable> variables, SmallAlgebra alg)`
    ///
    /// # Arguments
    /// * `name` - Optional name for the operation (if None, uses term's string representation)
    /// * `term` - The term to interpret (VariableImp or NonVariableTerm)
    /// * `variables` - List of variables (VariableImp instances or variable names as strings)
    /// * `algebra` - The algebra for interpretation
    ///
    /// # Returns
    /// A new TermOperationImp instance
    ///
    /// # Raises
    /// ValueError: If parameters are invalid
    #[new]
    #[pyo3(signature = (term, variables, algebra, name=None))]
    fn new(
        term: &Bound<'_, PyAny>,
        variables: &Bound<'_, PyList>,
        algebra: &PyBasicAlgebra,
        name: Option<String>,
    ) -> PyResult<Self> {
        // Convert term to Box<dyn Term>
        let term_box: Box<dyn Term> = if let Ok(var) = term.extract::<PyRef<PyVariableImp>>() {
            Box::new(var.inner.clone())
        } else if let Ok(nvt) = term.extract::<PyRef<PyNonVariableTerm>>() {
            nvt.inner.clone_box()
        } else {
            return Err(PyValueError::new_err(
                "term must be VariableImp or NonVariableTerm"
            ));
        };

        // Convert variables to Vec<String>
        let mut var_list: Vec<String> = Vec::new();
        for item in variables.iter() {
            if let Ok(var_imp) = item.extract::<PyRef<PyVariableImp>>() {
                var_list.push(var_imp.inner.get_name().to_string());
            } else if let Ok(var_name) = item.extract::<String>() {
                var_list.push(var_name);
            } else {
                return Err(PyValueError::new_err(
                    "variables must be VariableImp instances or strings"
                ));
            }
        }

        // Get algebra as Arc
        let alg_arc: Arc<dyn SmallAlgebra<UniverseItem = i32>> = 
            Arc::new(algebra.inner.clone());

        // Get interpretation
        let interpretation = term_box.interpretation(alg_arc.clone(), &var_list, true)
            .map_err(|e| PyValueError::new_err(e))?;

        // Create TermOperationImp
        let term_clone = term_box.clone_box();
        let term_op = if let Some(op_name) = name {
            TermOperationImp::new_with_name_safe(
                op_name,
                term_clone,
                var_list,
                alg_arc,
                interpretation,
            )
        } else {
            TermOperationImp::new_safe(
                term_clone,
                var_list,
                alg_arc,
                interpretation,
            )
        };

        match term_op {
            Ok(inner) => Ok(PyTermOperationImp { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the term that this operation interprets.
    ///
    /// # Returns
    /// The term as a string representation
    fn get_term(&self) -> String {
        format!("{}", self.inner.get_term())
    }

    /// Get the ordered list of variables.
    ///
    /// # Returns
    /// List of variable names
    fn get_ordered_variables(&self) -> Vec<String> {
        self.inner.get_ordered_variables()
    }

    /// Get the arity of this operation.
    ///
    /// # Returns
    /// The number of arguments this operation takes
    fn arity(&self) -> i32 {
        self.inner.arity()
    }

    /// Get the size of the set upon which the operation is defined.
    ///
    /// # Returns
    /// The size of the underlying set
    fn get_set_size(&self) -> i32 {
        self.inner.get_set_size()
    }

    /// Evaluate the operation at the given arguments.
    ///
    /// # Arguments
    /// * `args` - List of integer arguments
    ///
    /// # Returns
    /// The result of the operation
    ///
    /// # Raises
    /// ValueError: If arguments are invalid
    fn int_value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.int_value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the operation table.
    ///
    /// # Returns
    /// List of integers representing the operation table, or None if not available
    fn get_table(&self) -> Option<Vec<i32>> {
        self.inner.get_table().map(|slice| slice.to_vec())
    }

    /// Python string representation.
    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }

    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("TermOperationImp({})", self.inner)
    }
}

