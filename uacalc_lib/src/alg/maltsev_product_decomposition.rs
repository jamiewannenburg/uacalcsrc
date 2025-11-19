use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::*;
use uacalc::alg::op::Operation;
use crate::alg::PyBasicAlgebra;
use crate::alg::conlat::partition::PyPartition;

/// Python wrapper for MaltsevProductDecomposition
#[pyclass]
pub struct PyMaltsevProductDecomposition {
    inner: uacalc::alg::MaltsevProductDecomposition,
}

#[pymethods]
impl PyMaltsevProductDecomposition {
    /// Create a new Maltsev product decomposition.
    ///
    /// Args:
    ///     algebra (BasicAlgebra): The idempotent algebra to decompose
    ///     congruence (Partition): A congruence relation on the algebra
    ///
    /// Returns:
    ///     MaltsevProductDecomposition: The decomposition
    ///
    /// Raises:
    ///     ValueError: If the algebra or congruence is invalid
    #[new]
    fn new(algebra: &PyBasicAlgebra, congruence: &PyPartition) -> PyResult<Self> {
        // Clone the algebra and congruence
        let alg_box = algebra.clone_box();
        let cong = congruence.get_inner().clone();

        match uacalc::alg::MaltsevProductDecomposition::new_safe(alg_box, cong) {
            Ok(inner) => Ok(PyMaltsevProductDecomposition { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the congruence relation.
    ///
    /// Returns:
    ///     Partition: The congruence partition
    fn get_congruence(&self) -> PyPartition { PyPartition::from_inner(self.inner.get_congruence().clone()) }

    /// Get the cardinality of the original algebra.
    ///
    /// Returns:
    ///     int: The cardinality
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }

    /// Get the number of block algebras.
    ///
    /// Returns:
    ///     int: The number of block algebras
    fn get_block_count(&self) -> usize {
        self.inner.get_block_algebras().len()
    }

    /// Get the cardinality of the quotient algebra.
    ///
    /// Returns:
    ///     int: The quotient algebra cardinality
    fn get_quotient_cardinality(&self) -> i32 {
        self.inner.get_quotient_algebra().cardinality()
    }

    /// String representation of the decomposition.
    ///
    /// Returns:
    ///     str: String representation
    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }

    /// String representation for debugging.
    ///
    /// Returns:
    ///     str: Debug string representation
    fn __repr__(&self) -> String {
        format!(
            "MaltsevProductDecomposition(blocks={}, quotient_card={})",
            self.inner.get_block_algebras().len(),
            self.inner.get_quotient_algebra().cardinality()
        )
    }
}