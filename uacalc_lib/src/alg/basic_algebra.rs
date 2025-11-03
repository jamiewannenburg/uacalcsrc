use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::collections::HashMap;
use uacalc::alg::*;
use crate::alg::PySubalgebraLattice;
use crate::alg::PyCongruenceLattice;

/// Python wrapper for BasicSmallAlgebra (for integer universes)
#[pyclass]
pub struct PyBasicSmallAlgebra {
    pub(crate) inner: uacalc::alg::BasicSmallAlgebra<i32>,
}

impl PyBasicSmallAlgebra {
    /// Create PyBasicSmallAlgebra from inner Rust type (not exposed to Python)
    pub fn from_inner(inner: uacalc::alg::BasicSmallAlgebra<i32>) -> Self {
        PyBasicSmallAlgebra { inner }
    }

    /// Get the inner algebra (for internal use)
    pub(crate) fn get_inner(&self) -> &uacalc::alg::BasicSmallAlgebra<i32> {
        &self.inner
    }

    /// Clone the inner algebra as a boxed trait object.
    /// This is needed for the MaltsevProductDecomposition constructor.
    pub(crate) fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = i32>> {
        Box::new(self.inner.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>
    }
}

#[pymethods]
impl PyBasicSmallAlgebra {
    /// Create a new BasicSmallAlgebra.
    ///
    /// Args:
    ///     name (str): The name of the algebra
    ///     universe (Set[int]): The universe set as a list of integers
    ///
    /// Returns:
    ///     BasicSmallAlgebra: A new BasicSmallAlgebra instance
    #[new]
    #[pyo3(signature = (name, universe))]
    fn new(name: String, universe: Vec<i32>) -> Self {
        let universe_set: std::collections::HashSet<i32> = universe.into_iter().collect();
        let operations = Vec::new(); // Start with no operations
        PyBasicSmallAlgebra {
            inner: uacalc::alg::BasicSmallAlgebra::new(name, universe_set, operations),
        }
    }

    /// Create a new BasicSmallAlgebra with a constant operation.
    ///
    /// Args:
    ///     name (str): The name of the algebra
    ///     universe (Set[int]): The universe set as a list of integers
    ///
    /// Returns:
    ///     BasicSmallAlgebra: A new BasicSmallAlgebra instance with a constant operation
    #[staticmethod]
    fn new_with_constant_op(name: String, universe: Vec<i32>) -> PyResult<Self> {
        let universe_set: std::collections::HashSet<i32> = universe.into_iter().collect();
        let set_size = universe_set.len() as i32;
        let mut operations = Vec::new();
        
        if set_size > 0 {
            // Create a constant operation that returns 0
            match uacalc::alg::op::ops::make_constant_int_operation(set_size, 0) {
                Ok(op) => operations.push(op),
                Err(e) => return Err(PyValueError::new_err(format!("Failed to create constant operation: {}", e))),
            }
        }
        
        Ok(PyBasicSmallAlgebra {
            inner: uacalc::alg::BasicSmallAlgebra::new(name, universe_set, operations),
        })
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
    ///     int: The cardinality of the algebra
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

    /// Get the algebra type.
    ///
    /// Returns:
    ///     str: The algebra type as a string
    fn algebra_type(&self) -> String {
        format!("{:?}", self.inner.algebra_type())
    }

    /// Get the k-th element of the universe.
    ///
    /// Args:
    ///     k (int): The index of the element to retrieve
    ///
    /// Returns:
    ///     int: The element at index k, or -1 if k is out of bounds
    fn get_element(&self, k: usize) -> i32 {
        self.inner.get_element(k).unwrap_or(-1)
    }

    /// Get the index of an element in the universe.
    ///
    /// Args:
    ///     elem (int): The element to find the index for
    ///
    /// Returns:
    ///     int: The index of the element, or -1 if not found
    fn element_index(&self, elem: i32) -> i32 {
        match self.inner.element_index(&elem) {
            Some(idx) => idx as i32,
            None => -1,
        }
    }

    /// Get the universe as a list.
    ///
    /// Returns:
    ///     List[int]: The universe elements as a list, or None if not available
    fn get_universe_list(&self) -> Option<Vec<i32>> {
        self.inner.get_universe_list()
    }

    /// Get the universe order map.
    ///
    /// Returns:
    ///     dict: A mapping from elements to their indices, or None if not available
    fn get_universe_order(&self) -> Option<HashMap<i32, usize>> {
        self.inner.get_universe_order()
    }

    /// Check if this algebra uses an integer universe.
    ///
    /// Returns:
    ///     bool: True if the universe is just integers from 0 to n-1
    fn int_universe(&self) -> bool {
        self.inner.int_universe()
    }

    /// Reset cached congruence and subalgebra lattices.
    ///
    /// Note: In this partial implementation, con/sub lattices are not yet implemented,
    /// so this is a no-op but matches the Java API signature.
    fn reset_con_and_sub(&mut self) {
        self.inner.reset_con_and_sub();
    }

    /// Convert operations to default value operations (for UI).
    ///
    /// Note: In this partial implementation, this is a no-op but matches the Java API signature.
    fn convert_to_default_value_ops(&mut self) {
        self.inner.convert_to_default_value_ops();
    }

    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("BasicSmallAlgebra({})", self.inner.to_string())
    }

    /// Python equality comparison
    fn __eq__(&self, other: &PyBasicSmallAlgebra) -> bool {
        // Compare basic properties since we can't easily compare the full structure
        self.inner.name() == other.inner.name() &&
        self.inner.cardinality() == other.inner.cardinality()
    }

    /// Get the operations of this algebra.
    ///
    /// Returns:
    ///     list: List of operation names and arities as tuples
    fn operations(&self) -> Vec<(String, i32)> {
        // Use get_operations_ref() to avoid infinite recursion limitation in operations()
        self.inner.get_operations_ref().iter().map(|op| {
            (op.symbol().name().to_string(), op.arity())
        }).collect()
    }

    /// Get the number of operations in this algebra.
    ///
    /// Returns:
    ///     int: The number of operations
    fn operations_count(&self) -> usize {
        // Use get_operations_ref() to avoid infinite recursion limitation in operations()
        self.inner.get_operations_ref().len()
    }

    /// Get the congruence lattice (lazy initialization).
    ///
    /// Returns:
    ///     CongruenceLattice: The congruence lattice
    fn con(&mut self) -> PyCongruenceLattice {
        // Construct a new congruence lattice for this algebra.
        // We create a fresh lattice instance rather than exposing an internal reference.
        PyCongruenceLattice::from_algebra(self)
    }

    /// Get the subalgebra lattice (lazy initialization).
    ///
    /// Returns:
    ///     SubalgebraLattice: The subalgebra lattice
    fn sub(&mut self) -> PySubalgebraLattice {
        let sub_lat = self.inner.sub();
        PySubalgebraLattice::from_inner(sub_lat.clone())
    }
}