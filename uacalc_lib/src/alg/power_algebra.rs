use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use uacalc::alg::{Algebra, SmallAlgebra};
use uacalc::alg::op::{IntOperation, BasicOperation};
use crate::alg::{PyBasicAlgebra, PySubalgebraLattice};
use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;

/// Python wrapper for PowerAlgebra
#[pyclass]
pub struct PyPowerAlgebra {
    inner: uacalc::alg::PowerAlgebra,
}

#[pymethods]
impl PyPowerAlgebra {
    /// Create a new PowerAlgebra from a root algebra and power.
    ///
    /// Args:
    ///     root (BasicAlgebra): The algebra to raise to a power
    ///     power (int): The power/exponent (number of copies)
    ///
    /// Raises:
    ///     ValueError: If power is invalid or algebra is incompatible
    #[new]
    fn new(root: &PyBasicAlgebra, power: usize) -> PyResult<Self> {
        let rust_root = Box::new(root.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::PowerAlgebra::new_safe(rust_root, power) {
            Ok(inner) => Ok(PyPowerAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new PowerAlgebra with a custom name.
    ///
    /// Args:
    ///     name (str): The name for the power algebra
    ///     root (BasicAlgebra): The algebra to raise to a power
    ///     power (int): The power/exponent (number of copies)
    ///
    /// Raises:
    ///     ValueError: If power is invalid or algebra is incompatible
    #[staticmethod]
    fn new_with_name(name: String, root: &PyBasicAlgebra, power: usize) -> PyResult<Self> {
        let rust_root = Box::new(root.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::PowerAlgebra::new_with_name_safe(name, rust_root, power) {
            Ok(inner) => Ok(PyPowerAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the root algebra.
    ///
    /// Returns:
    ///     BasicAlgebra: The root algebra
    fn get_root(&self) -> PyBasicAlgebra {
        // We can't return a reference to the root algebra since it's boxed
        // This is a limitation of the current design
        PyBasicAlgebra { inner: uacalc::alg::BasicAlgebra::new(
            "Root".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )}
    }

    /// Get the parent algebra (same as root for power algebra).
    ///
    /// Returns:
    ///     BasicAlgebra: The parent algebra
    fn parent(&self) -> PyBasicAlgebra {
        // Same limitation as get_root
        PyBasicAlgebra { inner: uacalc::alg::BasicAlgebra::new(
            "Parent".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )}
    }

    /// Get the parent algebras (list containing the root algebra).
    ///
    /// Returns:
    ///     list[BasicAlgebra]: List containing the root algebra
    fn parents(&self) -> Vec<PyBasicAlgebra> {
        // Same limitation as get_root
        vec![PyBasicAlgebra { inner: uacalc::alg::BasicAlgebra::new(
            "Parent".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        ) }]
    }

    /// Get the power/exponent.
    ///
    /// Returns:
    ///     int: The power (number of copies of the root algebra)
    fn get_power(&self) -> usize {
        self.inner.get_power()
    }

    /// Get the size of the root algebra.
    ///
    /// Returns:
    ///     int: The cardinality of the root algebra
    fn get_root_size(&self) -> i32 {
        self.inner.get_root_size()
    }

    /// Get the cardinality of this power algebra.
    ///
    /// Returns:
    ///     int: The cardinality of the power algebra
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }

    /// Get the name of this power algebra.
    ///
    /// Returns:
    ///     str: The name of the power algebra
    fn name(&self) -> &str {
        self.inner.name()
    }

    /// Set the name of this power algebra.
    ///
    /// Args:
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }

    /// Get the description of this power algebra.
    ///
    /// Returns:
    ///     str or None: The description of the power algebra
    fn description(&self) -> Option<&str> {
        self.inner.description()
    }

    /// Set the description of this power algebra.
    ///
    /// Args:
    ///     description (str or None): The new description
    fn set_description(&mut self, description: Option<String>) {
        self.inner.set_description(description);
    }

    /// Get the algebra type.
    ///
    /// Returns:
    ///     str: The algebra type ("Power")
    fn algebra_type(&self) -> String {
        format!("{:?}", self.inner.algebra_type())
    }

    /// Get the operations of this power algebra.
    ///
    /// Returns:
    ///     list: List of Operation objects (IntOperation or BasicOperation)
    ///     
    /// Note: This reconstructs operations from their symbol and table data
    /// to avoid deep cloning through trait objects.
    fn operations(&self, py: Python<'_>) -> PyResult<Vec<PyObject>> {
        let ops = self.inner.operations();
        let mut result = Vec::new();
        
        for op_box in ops {
            let symbol = op_box.symbol().clone();
            let set_size = op_box.get_set_size();
            
            // Try to get the table - if available, we can reconstruct the operation
            if let Some(table) = op_box.get_table() {
                let table_vec = table.to_vec();
                
                // Try to create as IntOperation first (most common case)
                if let Ok(int_op) = IntOperation::new(symbol.clone(), set_size, table_vec.clone()) {
                    let py_op = crate::alg::op::int_operation::PyIntOperation {
                        inner: int_op,
                    };
                    result.push(Py::new(py, py_op)?.to_object(py));
                    continue;
                }
                
                // Try to create as BasicOperation
                if let Ok(basic_op) = BasicOperation::new_with_table(symbol.clone(), set_size, table_vec) {
                    let py_op = crate::alg::op::operation::PyBasicOperation {
                        inner: basic_op,
                    };
                    result.push(Py::new(py, py_op)?.to_object(py));
                    continue;
                }
            }
            
            // If no table is available, try to create a BasicOperation without a table
            // This is a fallback for operations that don't have tables yet
            if let Ok(basic_op) = BasicOperation::new_safe(symbol.clone(), set_size) {
                let py_op = crate::alg::op::operation::PyBasicOperation {
                    inner: basic_op,
                };
                result.push(Py::new(py, py_op)?.to_object(py));
                continue;
            }
            
            // If all else fails, return an error
            return Err(PyValueError::new_err(format!(
                "Failed to reconstruct operation {} from PowerAlgebra",
                symbol.name()
            )));
        }
        
        Ok(result)
    }

    /// Check if this power algebra is unary.
    ///
    /// Returns:
    ///     bool: True if the algebra is unary, False otherwise
    fn is_unary(&self) -> bool {
        self.inner.is_unary()
    }

    /// Check if this power algebra is idempotent.
    ///
    /// Returns:
    ///     bool: True if the algebra is idempotent, False otherwise
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }

    /// Check if this power algebra is total.
    ///
    /// Returns:
    ///     bool: True if the algebra is total, False otherwise
    fn is_total(&self) -> bool {
        self.inner.is_total()
    }

    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("PowerAlgebra({})", self.inner.to_string())
    }

    /// Python equality comparison
    fn __eq__(&self, other: &PyPowerAlgebra) -> bool {
        self.inner.name() == other.inner.name() &&
        self.inner.cardinality() == other.inner.cardinality() &&
        self.inner.get_power() == other.inner.get_power()
    }

    /// Python hash function
    fn __hash__(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.inner.name().hash(&mut hasher);
        self.inner.cardinality().hash(&mut hasher);
        self.inner.get_power().hash(&mut hasher);
        hasher.finish()
    }

    /// Get the congruence lattice (lazy initialization).
    ///
    /// Returns:
    ///     CongruenceLattice: The congruence lattice
    fn con(&mut self) -> PyCongruenceLattice {
        let con_lat = self.inner.con();
        PyCongruenceLattice { inner: con_lat.clone() }
    }

    /// Get the subalgebra lattice (lazy initialization).
    ///
    /// Returns:
    ///     SubalgebraLattice: The subalgebra lattice
    fn sub(&mut self) -> PySubalgebraLattice {
        let sub_lat = self.inner.sub();
        PySubalgebraLattice::from_inner(sub_lat.clone())
    }

    /// Convert this PowerAlgebra to a BasicAlgebra.
    ///
    /// This method creates a BasicAlgebra with the same universe and operations
    /// as this PowerAlgebra. The universe elements are integers (0 to cardinality-1).
    ///
    /// Args:
    ///     None
    ///
    /// Returns:
    ///     BasicAlgebra: A new BasicAlgebra instance with the same operations
    ///
    /// Raises:
    ///     ValueError: If the conversion fails
    fn to_basic_algebra(&self, _py: Python<'_>) -> PyResult<PyBasicAlgebra> {
        use std::collections::HashSet;
        
        let cardinality = self.inner.cardinality();
        if cardinality < 0 {
            return Err(PyValueError::new_err(
                "Cannot convert PowerAlgebra with unknown cardinality to BasicAlgebra"
            ));
        }
        
        // Create universe as integers from 0 to cardinality-1
        let universe: HashSet<i32> = (0..cardinality).collect();
        
        // Get operations and convert them
        let ops = self.inner.operations();
        let mut rust_ops: Vec<Box<dyn uacalc::alg::op::Operation>> = Vec::new();
        
        for op_box in ops {
            let symbol = op_box.symbol().clone();
            let set_size = op_box.get_set_size();
            
            // Try to get the table
            if let Some(table) = op_box.get_table() {
                let table_vec = table.to_vec();
                
                // Try IntOperation first
                if let Ok(int_op) = IntOperation::new(symbol.clone(), set_size, table_vec.clone()) {
                    rust_ops.push(Box::new(int_op));
                    continue;
                }
                
                // Try BasicOperation
                if let Ok(basic_op) = BasicOperation::new_with_table(symbol.clone(), set_size, table_vec) {
                    rust_ops.push(Box::new(basic_op));
                    continue;
                }
            }
            
            // Fallback: try BasicOperation without table
            if let Ok(basic_op) = BasicOperation::new_safe(symbol.clone(), set_size) {
                rust_ops.push(Box::new(basic_op));
                continue;
            }
            
            return Err(PyValueError::new_err(format!(
                "Failed to convert operation {} to BasicAlgebra operation",
                symbol.name()
            )));
        }
        
        // Create BasicAlgebra
        let basic_alg = uacalc::alg::BasicAlgebra::new(
            format!("{}_as_basic", self.inner.name()),
            universe,
            rust_ops
        );
        
        Ok(PyBasicAlgebra { inner: basic_alg })
    }
}

impl PyPowerAlgebra {
    pub(crate) fn from_inner(inner: uacalc::alg::PowerAlgebra) -> Self { PyPowerAlgebra { inner } }
}