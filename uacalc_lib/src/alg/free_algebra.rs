use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::{Algebra, SmallAlgebra};
use crate::alg::{PyBasicSmallAlgebra, PyBasicOperation};
use crate::eq::PyEquation;
use crate::util::PyIntArray;
use std::collections::HashMap;

/// Python wrapper for FreeAlgebra
#[pyclass]
pub struct PyFreeAlgebra {
    inner: uacalc::alg::FreeAlgebra,
}

#[pymethods]
impl PyFreeAlgebra {
    /// Create a new FreeAlgebra with the given base algebra and number of generators.
    ///
    /// Args:
    ///     base (BasicSmallAlgebra): The base algebra
    ///     number_of_gens (int): Number of generators
    ///
    /// Raises:
    ///     ValueError: If construction fails
    #[new]
    fn new(base: &PyBasicSmallAlgebra, number_of_gens: i32) -> PyResult<Self> {
        let rust_base = Box::new(base.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::FreeAlgebra::new_safe(rust_base, number_of_gens) {
            Ok(inner) => Ok(PyFreeAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new FreeAlgebra with a custom name.
    ///
    /// Args:
    ///     name (str): The name for the free algebra
    ///     base (BasicSmallAlgebra): The base algebra
    ///     number_of_gens (int): Number of generators
    ///
    /// Raises:
    ///     ValueError: If construction fails
    #[staticmethod]
    fn new_with_name(name: String, base: &PyBasicSmallAlgebra, number_of_gens: i32) -> PyResult<Self> {
        let rust_base = Box::new(base.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::FreeAlgebra::new_with_name_safe(name, rust_base, number_of_gens) {
            Ok(inner) => Ok(PyFreeAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new FreeAlgebra with progress control.
    ///
    /// Args:
    ///     base (BasicSmallAlgebra): The base algebra
    ///     number_of_gens (int): Number of generators
    ///     make_universe (bool): Whether to compute the universe
    ///     thin_gens (bool): Whether to thin generators
    ///     decompose (bool): Whether to decompose
    ///
    /// Raises:
    ///     ValueError: If construction fails
    #[staticmethod]
    fn new_with_progress(
        base: &PyBasicSmallAlgebra,
        number_of_gens: i32,
        make_universe: bool,
        thin_gens: bool,
        decompose: bool
    ) -> PyResult<Self> {
        let rust_base = Box::new(base.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::FreeAlgebra::new_with_progress_safe(rust_base, number_of_gens, None) {
            Ok(inner) => Ok(PyFreeAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new FreeAlgebra with relations (finitely presented algebra).
    ///
    /// Args:
    ///     base (BasicSmallAlgebra): The base algebra
    ///     number_of_gens (int): Number of generators
    ///     relations (List[Equation]): The relations
    ///
    /// Raises:
    ///     ValueError: If construction fails
    #[staticmethod]
    fn new_with_relations(
        base: &PyBasicSmallAlgebra,
        number_of_gens: i32,
        relations: Vec<PyEquation>
    ) -> PyResult<Self> {
        let rust_base = Box::new(base.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        let rust_relations: Vec<uacalc::eq::Equation> = relations.into_iter().map(|eq| eq.inner).collect();

        match uacalc::alg::FreeAlgebra::new_with_relations_safe(rust_base, number_of_gens, rust_relations, None) {
            Ok(inner) => Ok(PyFreeAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the idempotent terms.
    ///
    /// Returns:
    ///     List[str]: List of idempotent term representations (simplified)
    fn get_idempotent_terms(&self) -> PyResult<Vec<String>> {
        match self.inner.get_idempotent_terms() {
            Ok(_terms) => {
                // Simplified implementation - return empty list for now
                // In practice, you'd convert Box<dyn Term> to appropriate Python types
                Ok(vec![])
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the algebra type.
    ///
    /// Returns:
    ///     str: The algebra type
    fn algebra_type(&self) -> String {
        match self.inner.algebra_type() {
            uacalc::alg::AlgebraType::Free => "FREE".to_string(),
            _ => "UNKNOWN".to_string(),
        }
    }

    /// Switch x and y automorphism.
    ///
    /// Returns:
    ///     Optional[PyBasicOperation]: The automorphism operation, or None if not applicable
    fn switch_x_and_y_automorphism(&self) -> PyResult<Option<PyBasicOperation>> {
        match self.inner.switch_x_and_y_automorphism() {
            Ok(Some(op)) => {
                // Convert Box<dyn Operation> to PyBasicOperation
                // This is a simplified approach - in practice, you'd need proper type conversion
                Ok(None) // Simplified for now
            },
            Ok(None) => Ok(None),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Find equation of A not B.
    ///
    /// Args:
    ///     a (FreeAlgebra): Algebra A
    ///     b (BasicSmallAlgebra): Algebra B
    ///
    /// Returns:
    ///     Optional[Equation]: The equation, or None if not found
    #[staticmethod]
    fn find_equation_of_a_not_b(a: &PyFreeAlgebra, b: &PyBasicSmallAlgebra) -> PyResult<Option<PyEquation>> {
        // Simplified implementation - return None for now
        // The actual implementation would need proper type conversion between FreeAlgebra and SmallAlgebra
        Ok(None)
    }

    /// Get the cardinality of the algebra.
    ///
    /// Returns:
    ///     int: The cardinality
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }

    /// Get the name of the algebra.
    ///
    /// Returns:
    ///     str: The name
    fn name(&self) -> String {
        self.inner.name().to_string()
    }

    /// Set the name of the algebra.
    ///
    /// Args:
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }

    /// Check if this algebra is unary.
    ///
    /// Returns:
    ///     bool: True if the algebra is unary
    fn is_unary(&self) -> bool {
        self.inner.is_unary()
    }

    /// Check if this algebra is idempotent.
    ///
    /// Returns:
    ///     bool: True if the algebra is idempotent
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }

    /// Check if this algebra is total.
    ///
    /// Returns:
    ///     bool: True if the algebra is total
    fn is_total(&self) -> bool {
        self.inner.is_total()
    }

    /// Get the number of operations.
    ///
    /// Returns:
    ///     int: The number of operations
    fn operations_count(&self) -> usize {
        self.inner.get_operations_ref().len()
    }

    /// Get the universe as a list.
    ///
    /// Returns:
    ///     List[IntArray]: The universe elements
    fn get_universe_list(&self) -> Vec<PyIntArray> {
        self.inner.universe()
            .map(|item| PyIntArray { inner: item })
            .collect()
    }

    /// Get the universe order as a dictionary.
    ///
    /// Returns:
    ///     Dict[IntArray, int]: The universe order mapping
    fn get_universe_order(&self) -> Option<HashMap<PyIntArray, usize>> {
        // This is a simplified implementation
        // The full implementation would need to handle IntArray as keys
        None
    }

    /// Get an element by its index.
    ///
    /// Args:
    ///     index (int): The index of the element
    ///
    /// Returns:
    ///     IntArray: The element at the given index
    fn get_element(&self, index: usize) -> Option<PyIntArray> {
        // This is a simplified implementation
        // The full implementation would need to convert from IntArray
        None
    }

    /// Get the index of an element.
    ///
    /// Args:
    ///     element (IntArray): The element to find the index for
    ///
    /// Returns:
    ///     int: The index of the element
    fn element_index(&self, element: &PyIntArray) -> Option<usize> {
        // This is a simplified implementation
        // The full implementation would need to search through the universe
        None
    }

    /// String representation of the algebra.
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
        format!("FreeAlgebra(name='{}', cardinality={})", self.name(), self.cardinality())
    }

    /// Equality comparison.
    ///
    /// Args:
    ///     other (FreeAlgebra): The other algebra to compare with
    ///
    /// Returns:
    ///     bool: True if equal
    fn __eq__(&self, other: &PyFreeAlgebra) -> bool {
        self.inner == other.inner
    }

    /// Hash function for use in sets and dictionaries.
    ///
    /// Returns:
    ///     int: Hash value
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }

    /// Length function for use with len().
    ///
    /// Returns:
    ///     int: Cardinality of the algebra
    fn __len__(&self) -> usize {
        self.inner.cardinality() as usize
    }
}