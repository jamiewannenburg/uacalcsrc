/// Python wrapper for AlgebraWithGeneratingVector
#[pyclass]
pub struct PyAlgebraWithGeneratingVector {
    inner: uacalc::alg::AlgebraWithGeneratingVector,
}

#[pymethods]
impl PyAlgebraWithGeneratingVector {
    /// Create a new AlgebraWithGeneratingVector.
    ///
    /// Args:
    ///     algebra (BasicSmallAlgebra): The algebra
    ///     vector (List[int]): The generating vector
    ///
    /// Returns:
    ///     AlgebraWithGeneratingVector: A new AlgebraWithGeneratingVector instance
    #[new]
    fn new(algebra: &PyBasicSmallAlgebra, vector: Vec<i32>) -> Self {
        PyAlgebraWithGeneratingVector {
            inner: uacalc::alg::AlgebraWithGeneratingVector::new(
                algebra.inner.clone(),
                vector,
            ),
        }
    }

    /// Get the algebra.
    ///
    /// Returns:
    ///     BasicSmallAlgebra: The algebra
    fn get_algebra(&self) -> PyBasicSmallAlgebra {
        PyBasicSmallAlgebra {
            inner: self.inner.get_algebra().clone(),
        }
    }

    /// Get the generating vector.
    ///
    /// Returns:
    ///     List[int]: The generating vector
    fn get_vector(&self) -> Vec<i32> {
        self.inner.get_vector().clone()
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
        self.inner.hash(&mut hasher);
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
}