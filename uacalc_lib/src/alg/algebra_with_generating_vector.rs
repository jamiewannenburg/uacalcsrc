use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use crate::alg::PyBasicAlgebra;
use uacalc::alg::BasicAlgebra;

/// Python wrapper for AlgebraWithGeneratingVector
#[pyclass]
pub struct PyAlgebraWithGeneratingVector {
    inner: uacalc::alg::AlgebraWithGeneratingVector<i32>,
    algebra: uacalc::alg::BasicAlgebra<i32>,
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
            algebra: algebra.inner.clone(),
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
        Ok(PyBasicAlgebra::from_inner(self.algebra.clone()))
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
        let vec = self.inner.get_vector();
        let mut body = String::from("[");
        for (i, v) in vec.iter().enumerate() {
            if i > 0 {
                body.push(',');
            }
            body.push_str(&v.to_string());
        }
        body.push(']');
        format!(
            "Alg with vector, alg size = {}, vec = {}",
            self.inner.get_algebra().cardinality(),
            body
        )
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
            .map(|item| {
                let card = item.get_algebra().cardinality();
                let reconstructed = BasicAlgebra::new(
                    item.get_algebra().name().to_string(),
                    (0..card).collect(),
                    Vec::new(),
                );
                PyAlgebraWithGeneratingVector {
                    inner: item,
                    algebra: reconstructed,
                }
            })
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
        let relations_opt: Option<Vec<_>> =
            relations.map(|eqs| eqs.into_iter().map(|eq| eq.inner).collect());
        let decomposition = match relations_opt {
            Some(rels) if !rels.is_empty() => {
                uacalc::alg::AlgebraWithGeneratingVector::si_decompose_with_equation_relations(
                    alg_box, &vec, rels,
                )
            }
            _ => uacalc::alg::AlgebraWithGeneratingVector::si_decompose(alg_box, &vec),
        };
        decomposition.into_iter()
            .map(|item| {
                let card = item.get_algebra().cardinality();
                let reconstructed = BasicAlgebra::new(
                    item.get_algebra().name().to_string(),
                    (0..card).collect(),
                    Vec::new(),
                );
                PyAlgebraWithGeneratingVector {
                    inner: item,
                    algebra: reconstructed,
                }
            })
            .collect()
    }
}