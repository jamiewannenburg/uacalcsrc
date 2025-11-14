//! Python wrapper for Homomorphism

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyList;
use pyo3::Bound;
use crate::alg::PyBasicAlgebra;
use crate::alg::conlat::partition::PyPartition;
use crate::util::PyIntArray;

/// Python wrapper for Homomorphism
#[pyclass]
#[derive(Clone)]
pub struct PyHomomorphism {
    inner: uacalc::alg::Homomorphism,
}

#[pymethods]
impl PyHomomorphism {
    /// Create a new Homomorphism from domain to range with the given mapping.
    ///
    /// Args:
    ///     domain (BasicAlgebra): The domain algebra
    ///     range (BasicAlgebra): The range algebra
    ///     map (dict): The mapping from domain indices to range indices
    ///
    /// Raises:
    ///     ValueError: If the mapping is invalid or algebras are incompatible
    #[new]
    fn new(
        domain: &PyBasicAlgebra,
        range: &PyBasicAlgebra,
        map: std::collections::HashMap<usize, usize>,
    ) -> PyResult<Self> {
        // Convert Python algebras to Rust algebras
        let domain_box = Box::new(domain.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        let range_box = Box::new(range.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::Homomorphism::new_safe(domain_box, range_box, map) {
            Ok(inner) => Ok(PyHomomorphism { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Compute the kernel partition of this homomorphism.
    ///
    /// The kernel partition groups domain elements that map to the same
    /// range element.
    ///
    /// Returns:
    ///     Partition: The kernel partition
    ///
    /// Raises:
    ///     ValueError: If there's an error computing the kernel
    fn kernel(&self) -> PyResult<PyPartition> {
        match self.inner.kernel() {
            Ok(partition) => Ok(PyPartition::from_inner(partition)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a product homomorphism from a list of homomorphisms.
    ///
    /// This static method creates a list of IntArray elements representing
    /// the product homomorphism.
    ///
    /// Args:
    ///     homomorphisms (list): A list of homomorphisms with the same domain
    ///
    /// Returns:
    ///     list: List of IntArray elements for the product
    ///
    /// Raises:
    ///     ValueError: If the homomorphisms are incompatible or empty
    #[staticmethod]
    fn product_homo(homomorphisms: &Bound<'_, PyList>) -> PyResult<Vec<PyIntArray>> {
        let mut rust_homos = Vec::new();

        for item in homomorphisms.iter() {
            let py_homo = item.extract::<PyHomomorphism>()?;
            rust_homos.push(py_homo.inner.clone());
        }

        match uacalc::alg::Homomorphism::product_homo(&rust_homos) {
            Ok(int_arrays) => {
                let mut py_int_arrays = Vec::new();
                for int_array in int_arrays {
                    py_int_arrays.push(PyIntArray { inner: int_array });
                }
                Ok(py_int_arrays)
            }
            Err(e) => Err(PyValueError::new_err(e))
        }
    }

    /// Get the domain algebra.
    ///
    /// Returns:
    ///     BasicAlgebra: The domain algebra
    fn get_domain(&self) -> PyBasicAlgebra {
        // Clone the domain algebra and return it as a BasicAlgebra
        // Note: This assumes the domain is a BasicAlgebra
        let domain = self.inner.get_domain();
        // We need to downcast from trait object to concrete type
        // For now, we'll create a new BasicAlgebra with the same properties
        // This is a limitation - ideally we'd have a way to clone the exact type
        PyBasicAlgebra {
            inner: uacalc::alg::BasicAlgebra::new(
                domain.name().to_string(),
                domain.universe().collect(),
                domain.operations()
            )
        }
    }

    /// Set the domain algebra.
    ///
    /// Args:
    ///     domain (BasicAlgebra): The new domain algebra
    fn set_domain(&mut self, domain: &PyBasicAlgebra) {
        let domain_box = Box::new(domain.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        self.inner.set_domain(domain_box);
    }

    /// Get the range algebra.
    ///
    /// Returns:
    ///     BasicAlgebra: The range algebra
    fn get_range(&self) -> PyBasicAlgebra {
        // Clone the range algebra and return it as a BasicAlgebra
        // Note: This assumes the range is a BasicAlgebra
        let range = self.inner.get_range();
        // We need to downcast from trait object to concrete type
        // For now, we'll create a new BasicAlgebra with the same properties
        // This is a limitation - ideally we'd have a way to clone the exact type
        PyBasicAlgebra {
            inner: uacalc::alg::BasicAlgebra::new(
                range.name().to_string(),
                range.universe().collect(),
                range.operations()
            )
        }
    }

    /// Set the range algebra.
    ///
    /// Args:
    ///     range (BasicAlgebra): The new range algebra
    fn set_range(&mut self, range: &PyBasicAlgebra) {
        let range_box = Box::new(range.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        self.inner.set_range(range_box);
    }

    /// Get the mapping.
    ///
    /// Returns:
    ///     dict: The mapping from domain indices to range indices
    fn get_map(&self) -> std::collections::HashMap<usize, usize> {
        self.inner.get_map().clone()
    }

    /// Set the mapping.
    ///
    /// Args:
    ///     map (dict): The new mapping
    fn set_map(&mut self, map: std::collections::HashMap<usize, usize>) {
        self.inner.set_map(map);
    }

    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("Homomorphism({})", self.inner.to_string())
    }

    /// Python equality comparison
    fn __eq__(&self, other: &PyHomomorphism) -> bool {
        // Compare basic properties since we can't easily compare the full structure
        self.inner.get_domain().name() == other.inner.get_domain().name() &&
        self.inner.get_range().name() == other.inner.get_range().name() &&
        self.inner.get_map() == other.inner.get_map()
    }
}

impl PyHomomorphism {
    /// Create a PyHomomorphism from an existing Homomorphism.
    /// 
    /// This is used internally when converting Rust Homomorphism objects
    /// to Python objects.
    pub fn from_inner(inner: uacalc::alg::Homomorphism) -> Self {
        PyHomomorphism { inner }
    }
}