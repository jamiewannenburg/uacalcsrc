/// Python wrapper for SmallAlgebra (simplified for bindings)
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::BasicSmallAlgebra;
use uacalc::alg::SmallAlgebra;
use uacalc::alg::Algebra;
use uacalc::util::IntArray;
use crate::alg::PyBasicSmallAlgebra;

pub fn register_small_algebra(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PySmallAlgebra>()?;
    Ok(())
}

/// Python wrapper for SmallAlgebra
#[pyclass(name = "SmallAlgebra")]
pub struct PySmallAlgebra {
    inner: BasicSmallAlgebra<i32>,
}

#[pymethods]
impl PySmallAlgebra {
    /// Create a basic small algebra.
    ///
    /// # Arguments
    /// * `name` - The name of the algebra
    /// * `size` - The size of the algebra
    ///
    /// # Returns
    /// A new SmallAlgebra instance
    #[staticmethod]
    fn new_basic(name: String, size: usize) -> PyResult<Self> {
        use std::collections::HashSet;
        let universe: HashSet<i32> = (0..size as i32).collect();

        let alg = BasicSmallAlgebra::new(
            name,
            universe,
            Vec::new()
        );

        Ok(PySmallAlgebra { inner: alg })
    }

    /// Get the name.
    fn name(&self) -> String {
        self.inner.name().to_string()
    }

    /// Get the cardinality.
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }

    fn __str__(&self) -> String {
        format!("SmallAlgebra(name: {}, cardinality: {})",
            self.inner.name(),
            self.inner.cardinality())
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }
}

impl Clone for PySmallAlgebra {
    fn clone(&self) -> Self {
        PySmallAlgebra { inner: self.inner.clone() }
    }
}

impl PySmallAlgebra {
    /// Clone the inner algebra as a boxed trait object.
    /// This is needed for the BigProductAlgebra constructor.
    pub(crate) fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = i32>> {
        Box::new(self.inner.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>
    }
}

// Removed duplicate PySubalgebraLattice; use alg::sublat::subalgebra_lattice::PySubalgebraLattice instead