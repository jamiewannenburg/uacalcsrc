use pyo3::prelude::*;
use uacalc::alg::Algebra;

/// Python wrapper for GeneralAlgebra (for integer universes)
#[pyclass]
pub struct PyGeneralAlgebra {
    inner: uacalc::alg::GeneralAlgebra<i32>,
}

#[pymethods]
impl PyGeneralAlgebra {
    /// Create a new GeneralAlgebra with a name.
    ///
    /// Args:
    ///     name (str): The name of the algebra
    ///
    /// Returns:
    ///     GeneralAlgebra: A new GeneralAlgebra instance
    #[new]
    #[pyo3(signature = (name))]
    fn new(name: String) -> Self {
        PyGeneralAlgebra {
            inner: uacalc::alg::GeneralAlgebra::new(name),
        }
    }

    /// Create a new GeneralAlgebra with a name and universe.
    ///
    /// Args:
    ///     name (str): The name of the algebra
    ///     universe (Set[int]): The universe set as a list of integers
    ///
    /// Returns:
    ///     GeneralAlgebra: A new GeneralAlgebra instance
    #[staticmethod]
    fn with_universe(name: String, universe: Vec<i32>) -> Self {
        let universe_set: std::collections::HashSet<i32> = universe.into_iter().collect();
        PyGeneralAlgebra {
            inner: uacalc::alg::GeneralAlgebra::new_with_universe(name, universe_set),
        }
    }

    /// Get the name of this algebra.
    ///
    /// Returns:
    ///     str: The name of the algebra
    fn name(&self) -> &str {
        self.inner.name()
    }

    /// Set the name of this algebra.
    ///
    /// Args:
    ///     name (str): The new name for the algebra
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }

    /// Get the description of this algebra.
    ///
    /// Returns:
    ///     Optional[str]: The description of the algebra, or None if not set
    fn description(&self) -> Option<&str> {
        self.inner.description()
    }

    /// Set the description of this algebra.
    ///
    /// Args:
    ///     desc (Optional[str]): The new description for the algebra
    fn set_description(&mut self, desc: Option<String>) {
        self.inner.set_description(desc);
    }

    /// Get the cardinality of this algebra.
    ///
    /// Returns:
    ///     int: The cardinality, or a negative value for infinite/unknown cardinalities
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }

    /// Get the input size for this algebra.
    ///
    /// Returns:
    ///     int: The input size, or -1 if it exceeds maximum integer value
    fn input_size(&self) -> i32 {
        self.inner.input_size()
    }

    /// Check if this algebra is unary.
    ///
    /// Returns:
    ///     bool: True if all operations have arity 1
    fn is_unary(&self) -> bool {
        self.inner.is_unary()
    }

    /// Check if all operations in this algebra are idempotent.
    ///
    /// Returns:
    ///     bool: True if all operations are idempotent
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }

    /// Check if all operations in this algebra are total.
    ///
    /// Returns:
    ///     bool: True if all operations are total
    fn is_total(&self) -> bool {
        self.inner.is_total()
    }

    /// Check if monitoring is enabled for this algebra.
    ///
    /// Returns:
    ///     bool: True if monitoring is enabled
    fn monitoring(&self) -> bool {
        self.inner.monitoring()
    }

    /// Get the universe as a list of integers.
    ///
    /// Returns:
    ///     List[int]: The universe elements as a list
    fn get_universe(&self) -> Vec<i32> {
        self.inner.universe().collect()
    }

    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("GeneralAlgebra({})", self.inner.to_string())
    }

    /// Python equality comparison
    fn __eq__(&self, other: &PyGeneralAlgebra) -> bool {
        // Compare basic properties since we can't easily compare the full structure
        self.inner.name() == other.inner.name() &&
        self.inner.cardinality() == other.inner.cardinality()
    }
}

pub fn register_general_algebra_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyGeneralAlgebra>()?;
    m.add("GeneralAlgebra", m.getattr("PyGeneralAlgebra")?)?;
    Ok(())
}