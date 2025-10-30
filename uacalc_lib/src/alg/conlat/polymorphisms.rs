use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyList;
use std::collections::{HashMap, HashSet};
use uacalc::alg::*;
use uacalc::alg::conlat::{BinaryRelation, MutableBinaryRelation};
use uacalc::util::IntArrayTrait;
use uacalc::alg::conlat::BasicBinaryRelation;
use uacalc::alg::conlat::subtrace::Subtrace;
use uacalc::alg::op::{Operation, BasicOperation, AbstractIntOperation, IntOperation};
use uacalc::alg::sublat::BasicSet;
use uacalc::lat::{Lattice, Order};
use crate::util::PyIntArray;
use crate::eq::PyEquation;

/// Python wrapper for Polymorphisms
#[pyclass]
pub struct PyPolymorphisms {
    inner: uacalc::alg::conlat::Polymorphisms,
}

#[pymethods]
impl PyPolymorphisms {
    /// Create a new Polymorphisms instance with proper error handling.
    ///
    /// Args:
    ///     arity (int): The arity of the polymorphisms to calculate
    ///     pars (List[Partition]): The collection of partitions
    ///     idempotent (bool): Whether to only consider idempotent polymorphisms
    ///     fixed_values (Optional[List[int]]): Fixed values for the polymorphisms (optional)
    ///
    /// Returns:
    ///     Polymorphisms: A new Polymorphisms instance
    ///
    /// Raises:
    ///     ValueError: If validation fails
    #[new]
    #[pyo3(signature = (arity, pars, idempotent, fixed_values=None))]
    fn new(arity: usize, pars: &Bound<'_, PyList>, idempotent: bool, fixed_values: Option<Vec<i32>>) -> PyResult<Self> {
        let mut rust_pars = Vec::new();
        for item in pars.iter() {
            let py_partition: PyRef<crate::alg::conlat::partition::PyPartition> = item.extract()?;
            rust_pars.push(py_partition.inner.clone());
        }
        match uacalc::alg::conlat::Polymorphisms::new_safe(arity, rust_pars, idempotent, fixed_values) {
            Ok(inner) => Ok(PyPolymorphisms { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the number of partitions in this collection.
    ///
    /// Returns:
    ///     int: The number of partitions
    fn num_partitions(&self) -> usize {
        self.inner.num_partitions()
    }

    /// Get the algebra size.
    ///
    /// Returns:
    ///     int: The size of the underlying algebra
    fn get_alg_size(&self) -> usize {
        self.inner.get_alg_size()
    }

    /// Get the arity.
    ///
    /// Returns:
    ///     int: The arity of the polymorphisms
    fn get_arity(&self) -> usize {
        self.inner.get_arity()
    }

    /// Check if idempotent polymorphisms are required.
    ///
    /// Returns:
    ///     bool: True if only idempotent polymorphisms are considered
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }

    /// Get the fixed values (if any).
    ///
    /// Returns:
    ///     Optional[List[int]]: The fixed values, or None if not set
    fn get_fixed_values(&self) -> Option<Vec<i32>> {
        self.inner.get_fixed_values().cloned()
    }

    /// Get the table size.
    ///
    /// Returns:
    ///     int: The size of the operation table (alg_size^arity)
    fn get_table_size(&self) -> usize {
        self.inner.get_table_size()
    }

    /// Initialize the graph structure for polymorphism calculations.
    ///
    /// This method creates the graph structure that will be used for
    /// calculating polymorphisms. The graph is initially empty.
    ///
    /// Returns:
    ///     None
    ///
    /// Raises:
    ///     ValueError: If initialization fails
    fn make_graph(&mut self) -> PyResult<()> {
        match self.inner.make_graph() {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Check if the graph has been initialized.
    ///
    /// Returns:
    ///     bool: True if the graph has been initialized
    fn has_graph(&self) -> bool {
        self.inner.has_graph()
    }

    /// Set the partial operation table.
    ///
    /// Args:
    ///     table (List[int]): The operation table to set
    ///
    /// Returns:
    ///     None
    ///
    /// Raises:
    ///     ValueError: If validation fails
    fn set_partial_op_table(&mut self, table: Vec<i32>) -> PyResult<()> {
        match self.inner.set_partial_op_table(table) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get a reference to the partial operation table (if set).
    ///
    /// Returns:
    ///     Optional[List[int]]: The operation table, or None if not set
    fn get_partial_op_table(&self) -> Option<Vec<i32>> {
        self.inner.get_partial_op_table().cloned()
    }

    /// Python string representation.
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("Polymorphisms({})", self.inner.to_string())
    }

    /// Python equality comparison.
    fn __eq__(&self, other: &PyPolymorphisms) -> bool {
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
}