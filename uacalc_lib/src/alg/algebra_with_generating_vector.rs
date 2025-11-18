use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use crate::alg::PyBasicAlgebra;
use uacalc::alg::BasicAlgebra;

/// Python wrapper for AlgebraWithGeneratingVector
#[pyclass]
pub struct PyAlgebraWithGeneratingVector {
    inner: uacalc::alg::AlgebraWithGeneratingVector<i32>,
}

#[pymethods]
impl PyAlgebraWithGeneratingVector {
    /// Create a new AlgebraWithGeneratingVector.
    ///
    /// Args:
    ///     algebra (BasicAlgebra): The algebra
    ///     vector (List[int]): The generating vector
    ///
    /// Returns:
    ///     AlgebraWithGeneratingVector: A new AlgebraWithGeneratingVector instance
    #[new]
    fn new(algebra: &PyBasicAlgebra, vector: Vec<i32>) -> Self {
        PyAlgebraWithGeneratingVector {
            inner: uacalc::alg::AlgebraWithGeneratingVector::new(
                Box::new(algebra.inner.clone()),
                vector,
            ),
        }
    }

    /// Get the algebra name.
    ///
    /// Returns:
    ///     str: The algebra name
    fn get_algebra_name(&self) -> String { 
        self.inner.get_algebra().name().to_string() 
    }

    /// Get the algebra.
    ///
    /// Returns:
    ///     BasicAlgebra: The algebra (reconstructed from SmallAlgebra properties)
    ///
    /// Note: Operations are not preserved due to trait object limitations.
    ///       Only the name and universe are preserved.
    ///
    /// Raises:
    ///     ValueError: If the algebra cannot be converted to BasicAlgebra
    fn get_algebra(&self) -> PyResult<PyBasicAlgebra> {
        let alg = self.inner.get_algebra();
        
        // Try to reconstruct BasicAlgebra from SmallAlgebra properties
        // This works for BasicAlgebra and some derived types
        let name = alg.name().to_string();
        let universe_list = alg.get_universe_list()
            .ok_or_else(|| PyValueError::new_err("Cannot get universe list from algebra"))?;
        let universe_set: std::collections::HashSet<i32> = universe_list.into_iter().collect();
        
        // Note: Operations are not cloned due to trait object limitations.
        // This is a known limitation when converting from SmallAlgebra to BasicAlgebra.
        let ops: Vec<Box<dyn uacalc::alg::op::Operation>> = Vec::new();
        
        // Create BasicAlgebra (operations will be empty due to trait object limitations)
        let basic_alg = BasicAlgebra::new(name, universe_set, ops);
        Ok(PyBasicAlgebra::from_inner(basic_alg))
    }

    /// Get the generating vector.
    ///
    /// Returns:
    ///     List[int]: The generating vector
    fn get_vector(&self) -> Vec<i32> { 
        self.inner.get_vector().to_vec() 
    }

    /// Check if this algebra with generating vector is an image of another.
    ///
    /// Args:
    ///     other (AlgebraWithGeneratingVector): The other algebra with generating vector
    ///
    /// Returns:
    ///     bool: True if this is an image of the other
    fn is_image_of(&self, other: &PyAlgebraWithGeneratingVector) -> bool {
        self.inner.is_image_of(&other.inner)
    }

    /// Python string representation.
    fn __str__(&self) -> String {
        format!("AlgebraWithGeneratingVector(algebra={}, vector={:?})",
                self.inner.get_algebra().name(),
                self.inner.get_vector())
    }

    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("AlgebraWithGeneratingVector(algebra='{}', vector={:?})",
                self.inner.get_algebra().name(),
                self.inner.get_vector())
    }

    /// Python equality comparison.
    fn __eq__(&self, other: &PyAlgebraWithGeneratingVector) -> bool {
        self.inner == other.inner
    }

    /// Python hash function.
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        self.inner.gens_vector.hash(&mut hasher);
        hasher.finish()
    }

    /// Python comparison (less than).
    fn __lt__(&self, other: &PyAlgebraWithGeneratingVector) -> bool {
        self.inner < other.inner
    }

    /// Python comparison (less than or equal).
    fn __le__(&self, other: &PyAlgebraWithGeneratingVector) -> bool {
        self.inner <= other.inner
    }

    /// Python comparison (greater than).
    fn __gt__(&self, other: &PyAlgebraWithGeneratingVector) -> bool {
        self.inner > other.inner
    }

    /// Python comparison (greater than or equal).
    fn __ge__(&self, other: &PyAlgebraWithGeneratingVector) -> bool {
        self.inner >= other.inner
    }

    /// Decompose an algebra with generating vector into subdirectly irreducible components.
    ///
    /// Args:
    ///     alg (BasicAlgebra): The algebra to decompose
    ///     vec (List[int]): The generating vector
    ///
    /// Returns:
    ///     List[AlgebraWithGeneratingVector]: List of subdirectly irreducible components
    #[staticmethod]
    fn si_decompose(alg: &PyBasicAlgebra, vec: Vec<i32>) -> Vec<PyAlgebraWithGeneratingVector> {
        let alg_box = Box::new(alg.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        let decomposition = uacalc::alg::AlgebraWithGeneratingVector::si_decompose(alg_box, &vec);
        decomposition.into_iter()
            .map(|item| PyAlgebraWithGeneratingVector { inner: item })
            .collect()
    }

    /// Decompose an algebra with generating vector into subdirectly irreducible components,
    /// taking into account additional relations.
    ///
    /// Args:
    ///     alg (BasicAlgebra): The algebra to decompose
    ///     vec (List[int]): The generating vector
    ///     relations (Optional[List[Equation]]): Optional list of equations representing relations
    ///
    /// Returns:
    ///     List[AlgebraWithGeneratingVector]: List of subdirectly irreducible components
    #[staticmethod]
    #[pyo3(signature = (alg, vec, relations=None))]
    fn si_decompose_with_relations(
        alg: &PyBasicAlgebra,
        vec: Vec<i32>,
        relations: Option<Vec<crate::eq::PyEquation>>,
    ) -> Vec<PyAlgebraWithGeneratingVector> {
        let alg_box = Box::new(alg.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        let relations_opt = relations.map(|eqs| eqs.into_iter().map(|eq| eq.inner).collect());
        let decomposition = uacalc::alg::AlgebraWithGeneratingVector::si_decompose_with_relations(
            alg_box,
            &vec,
            relations_opt,
        );
        decomposition.into_iter()
            .map(|item| PyAlgebraWithGeneratingVector { inner: item })
            .collect()
    }
}