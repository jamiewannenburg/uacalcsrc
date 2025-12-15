use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::*;
use uacalc::alg::op::{IntOperation, BasicOperation};
use crate::alg::PyBasicAlgebra;
use crate::alg::PyPartition;
use crate::alg::PySubalgebraLattice;
use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;

/// Python wrapper for Subalgebra
#[pyclass]
pub struct PySubalgebra {
    inner: uacalc::alg::Subalgebra<i32>,
}

#[pymethods]
impl PySubalgebra {
    /// Create a new Subalgebra with the given super algebra and subuniverse.
    ///
    /// Args:
    ///     name (str): Name of the subalgebra
    ///     super_algebra (BasicAlgebra): The super algebra
    ///     univ (list[int]): Array of indices in the super algebra forming the subuniverse
    ///
    /// Raises:
    ///     ValueError: If the subuniverse is empty or contains invalid indices
    #[new]
    fn new(name: String, super_algebra: &PyBasicAlgebra, univ: Vec<i32>) -> PyResult<Self> {
        let super_box = Box::new(super_algebra.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        match uacalc::alg::Subalgebra::new_safe(name, super_box, univ) {
            Ok(inner) => Ok(PySubalgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Find the index in this subalgebra of the element with index k in the super algebra.
    ///
    /// Uses binary search since the universe array is sorted.
    ///
    /// Args:
    ///     k (int): Index in the super algebra
    ///
    /// Returns:
    ///     int: Index in the subalgebra, or -1 if not found
    fn index(&self, k: i32) -> i32 {
        match self.inner.index(k) {
            Some(idx) => idx as i32,
            None => -1,
        }
    }

    /// Restrict a partition (or congruence) on the parent algebra to this subalgebra.
    ///
    /// Args:
    ///     par (Partition): Partition on the super algebra
    ///
    /// Returns:
    ///     Partition: Restricted partition on this subalgebra
    ///
    /// Raises:
    ///     ValueError: If restriction fails
    fn restrict_partition(&self, par: &PyPartition) -> PyResult<PyPartition> {
        match self.inner.restrict_partition(par.get_inner()) {
            Ok(restricted) => Ok(PyPartition::from_inner(restricted)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the super algebra name.
    ///
    /// Returns:
    ///     str: Name of the super algebra
    fn super_algebra_name(&self) -> String {
        self.inner.super_algebra().name().to_string()
    }

    /// Get the subuniverse array.
    ///
    /// Returns:
    ///     list[int]: Array of indices forming the subuniverse
    fn get_subuniverse_array(&self) -> Vec<i32> {
        self.inner.get_subuniverse_array().to_vec()
    }

    /// Get the universe as a list of integers.
    ///
    /// Returns:
    ///     List[int]: The universe elements as a list
    fn get_universe(&self) -> Vec<i32> {
        self.inner.universe().collect()
    }

    /// Get the cardinality of this subalgebra.
    ///
    /// Returns:
    ///     int: The cardinality (size of the universe)
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }

    /// Get the element at the given index.
    ///
    /// Args:
    ///     k (int): Index of the element
    ///
    /// Returns:
    ///     int: The element at index k, or -1 if out of bounds
    fn get_element(&self, k: usize) -> i32 {
        self.inner.get_element(k).unwrap_or(-1)
    }

    /// Get the index of an element in the universe.
    ///
    /// Args:
    ///     elem (int): The element to find
    ///
    /// Returns:
    ///     int: The index of the element, or -1 if not found
    fn element_index(&self, elem: i32) -> i32 {
        match self.inner.element_index(&elem) {
            Some(idx) => idx as i32,
            None => -1,
        }
    }

    /// Get the algebra type.
    ///
    /// Returns:
    ///     str: The algebra type ("Subalgebra")
    fn algebra_type(&self) -> String {
        format!("{:?}", self.inner.algebra_type())
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
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }

    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("Subalgebra({})", self.inner.to_string())
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

    /// Get the operations of this subalgebra.
    ///
    /// Returns:
    ///     List[Operation]: List of Operation instances (IntOperation or BasicOperation)
    ///
    /// Note: This method reconstructs Python operation objects from the internal
    /// Rust operations. Operations are restricted to the subalgebra's universe.
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
                "Failed to reconstruct operation {} from Subalgebra (arity: {}, set_size: {})",
                symbol.name(),
                symbol.arity(),
                set_size
            )));
        }
        
        Ok(result)
    }
    
    /// Create a congruence as an algebra (static method).
    /// 
    /// This gives the congruence as a subalgebra of A².
    /// 
    /// Args:
    ///     alg (BasicAlgebra): The algebra
    ///     cong (Partition): The congruence partition
    /// 
    /// Returns:
    ///     Subalgebra: The congruence as an algebra
    /// 
    /// Raises:
    ///     ValueError: If creation fails
    #[staticmethod]
    fn congruence_as_algebra(alg: &PyBasicAlgebra, cong: &PyPartition) -> PyResult<PySubalgebra> {
        let alg_box = Box::new(alg.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        match uacalc::alg::Subalgebra::<i32>::congruence_as_algebra_subalgebra("".to_string(), alg_box, cong.get_inner()) {
            Ok(subalgebra) => Ok(PySubalgebra { inner: subalgebra }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a congruence as an algebra with a name (static method).
    /// 
    /// This gives the congruence as a subalgebra of A².
    /// 
    /// Args:
    ///     name (str): The name for the algebra
    ///     alg (BasicAlgebra): The algebra
    ///     cong (Partition): The congruence partition
    /// 
    /// Returns:
    ///     Subalgebra: The congruence as an algebra
    /// 
    /// Raises:
    ///     ValueError: If creation fails
    #[staticmethod]
    fn congruence_as_algebra_with_name(
        name: String,
        alg: &PyBasicAlgebra,
        cong: &PyPartition
    ) -> PyResult<PySubalgebra> {
        let alg_box = Box::new(alg.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        match uacalc::alg::Subalgebra::<i32>::congruence_as_algebra_subalgebra(name, alg_box, cong.get_inner()) {
            Ok(subalgebra) => Ok(PySubalgebra { inner: subalgebra }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Convert this Subalgebra to a BasicAlgebra.
    ///
    /// This method creates a BasicAlgebra with the same universe and operations
    /// as this Subalgebra. The universe elements are integers (0 to cardinality-1).
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
        use uacalc::util::horner;
        
        let cardinality = self.inner.cardinality();
        if cardinality < 0 {
            return Err(PyValueError::new_err(
                "Cannot convert Subalgebra with unknown cardinality to BasicAlgebra"
            ));
        }
        
        // Create universe as integers from 0 to cardinality-1
        let universe: HashSet<i32> = (0..cardinality).collect();
        
        // Get operations from the subalgebra
        let ops = self.inner.operations();
        let mut rust_ops: Vec<Box<dyn uacalc::alg::op::Operation>> = Vec::new();
        
        for op_box in ops {
            let symbol = op_box.symbol().clone();
            let arity = op_box.arity();
            
            // Build the operation table by calling int_value_at for all argument combinations
            let table_size = if arity == 0 { 1 } else { (cardinality as usize).pow(arity as u32) };
            let mut table_vec = Vec::with_capacity(table_size);
            
            // Generate all argument combinations and evaluate the operation
            for i in 0..table_size {
                let args = if arity == 0 {
                    Vec::new()
                } else {
                    horner::horner_inv_same_size(i as i32, cardinality, arity as usize)
                };
                
                // Call int_value_at on the operation
                let result = op_box.int_value_at(&args)
                    .map_err(|e| PyValueError::new_err(format!(
                        "Failed to compute operation {} value at {:?}: {}",
                        symbol.name(), args, e
                    )))?;
                
                table_vec.push(result);
            }
            
            // Create IntOperation with the computed table
            if let Ok(int_op) = IntOperation::new(symbol.clone(), cardinality, table_vec.clone()) {
                rust_ops.push(Box::new(int_op));
                continue;
            }
            
            // Try BasicOperation as fallback
            if let Ok(basic_op) = BasicOperation::new_with_table(symbol.clone(), cardinality, table_vec) {
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