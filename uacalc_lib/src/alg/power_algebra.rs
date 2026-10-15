use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyAny;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use uacalc::alg::{Algebra, SmallAlgebra};
use uacalc::alg::op::{IntOperation, BasicOperation};
use uacalc::util::horner;
use crate::alg::convert::{algebra_type_java_name, ops_to_basic_algebra, operation_to_py, operations_to_py};
use crate::alg::{PyBasicAlgebra, PySubalgebraLattice};
use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;
use crate::alg::op::similarity_type::PySimilarityType;

/// Python wrapper for PowerAlgebra
#[pyclass]
pub struct PyPowerAlgebra {
    inner: uacalc::alg::PowerAlgebra,
    root: uacalc::alg::BasicAlgebra<i32>,
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
            Ok(inner) => Ok(PyPowerAlgebra { inner, root: root.inner.clone() }),
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
            Ok(inner) => Ok(PyPowerAlgebra { inner, root: root.inner.clone() }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn get_root(&self) -> PyBasicAlgebra {
        PyBasicAlgebra::from_inner(self.root.clone())
    }

    fn parent(&self) -> PyBasicAlgebra {
        self.get_root()
    }

    fn parents(&self) -> Vec<PyBasicAlgebra> {
        vec![self.get_root()]
    }

    fn factors(&self) -> Vec<PyBasicAlgebra> {
        (0..self.inner.get_power()).map(|_| self.get_root()).collect()
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

    fn get_element_tuple(&self, k: i32) -> Vec<i32> {
        let sizes = vec![self.inner.get_root_size(); self.inner.get_power()];
        horner::horner_inv(k, &sizes)
    }

    fn element_index_tuple(&self, tuple: Vec<i32>) -> i32 {
        let sizes = vec![self.inner.get_root_size(); self.inner.get_power()];
        horner::horner(&tuple, &sizes)
    }

    fn get_universe_tuples(&self) -> Vec<Vec<i32>> {
        let sizes = vec![self.inner.get_root_size(); self.inner.get_power()];
        let n = sizes.len();
        if n == 0 {
            return vec![Vec::new()];
        }
        if sizes.iter().any(|&s| s <= 0) {
            return Vec::new();
        }
        let mut indices = vec![0i32; n];
        let mut out = Vec::new();
        loop {
            out.push(indices.clone());
            let mut k = n;
            loop {
                if k == 0 {
                    return out;
                }
                k -= 1;
                indices[k] += 1;
                if indices[k] < sizes[k] {
                    break;
                }
                indices[k] = 0;
            }
        }
    }

    fn get_universe_list(&self) -> Vec<Vec<i32>> {
        self.get_universe_tuples()
    }

    fn get_universe_order(&self) -> Option<Vec<i32>> {
        None
    }

    fn similarity_type(&self) -> PySimilarityType {
        PySimilarityType::from_inner(Algebra::similarity_type(&self.inner).clone())
    }

    fn make_operation_tables(&mut self) {
        Algebra::make_operation_tables(&mut self.inner);
    }

    fn input_size(&self) -> i32 {
        Algebra::input_size(&self.inner)
    }

    fn get_operation(&self, py: Python<'_>, sym: &Bound<'_, PyAny>) -> PyResult<Option<PyObject>> {
        let name = if let Ok(s) = sym.extract::<String>() {
            s
        } else if let Ok(n) = sym.call_method0("name") {
            n.extract::<String>()?
        } else {
            return Ok(None);
        };
        let arity = if let Ok(a) = sym.call_method0("arity") {
            a.extract::<i32>().ok()
        } else {
            None
        };
        for op in Algebra::operations(&self.inner) {
            if op.symbol().name() == name && arity.map(|a| op.arity() == a).unwrap_or(true) {
                return Ok(Some(operation_to_py(py, op.as_ref())?));
            }
        }
        Ok(None)
    }

    fn projection(&self, k: usize) -> PyResult<PyBasicAlgebra> {
        if k < self.inner.get_power() {
            Ok(self.get_root())
        } else {
            Err(PyValueError::new_err(format!("projection index {} out of range", k)))
        }
    }

    fn projection_kernel(&self, _k: i32) -> Option<PyObject> {
        None
    }

    fn number_of_factors(&self) -> usize {
        self.inner.get_power()
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
        // BUG FIX: Manually compute tables by calling operations on the root algebra
        // This bypasses any buggy cached tables in ProductOperation
        let root = self.inner.get_root();
        let power = self.inner.get_power();
        let root_size = self.inner.get_root_size();
        
        // Get operations from root algebra
        let root_ops: Vec<_> = root.get_operations_ref();
        
        let mut rust_ops: Vec<Box<dyn uacalc::alg::op::Operation>> = Vec::new();
        
        for root_op in root_ops {
            let symbol = root_op.symbol().clone();
            let arity = root_op.arity();
            
            // Manually compute the table for the power algebra operation
            // by applying the root operation component-wise
            use uacalc::util::horner;
            let table_size = if arity == 0 { 1 } else { (cardinality as usize).pow(arity as u32) };
            let mut table_vec = Vec::with_capacity(table_size);
            
            for i in 0..table_size {
                // Decode the Horner-encoded index into component arguments
                let args_encoded = horner::horner_inv_same_size(i as i32, cardinality, arity as usize);
                
                // Decode each encoded argument into its components
                let mut args_expanded = Vec::with_capacity(arity as usize);
                for &arg_encoded in &args_encoded {
                    args_expanded.push(horner::horner_inv(arg_encoded, &vec![root_size; power]));
                }
                
                // Apply the operation component-wise
                let mut result_components = vec![0i32; power];
                for comp_idx in 0..power {
                    // Extract arguments for this component
                    let mut component_args = Vec::with_capacity(arity as usize);
                    for arg_components in &args_expanded {
                        component_args.push(arg_components[comp_idx]);
                    }
                    
                    // Apply the root operation
                    result_components[comp_idx] = root_op.int_value_at(&component_args)
                        .map_err(|e| PyValueError::new_err(format!("Failed to compute operation value: {}", e)))?;
                }
                
                // Encode the result using Horner's method
                let result = horner::horner(&result_components, &vec![root_size; power]);
                table_vec.push(result);
            }
            
            // Create IntOperation with the manually computed table
            if let Ok(int_op) = IntOperation::new(symbol.clone(), cardinality, table_vec.clone()) {
                rust_ops.push(Box::new(int_op));
                continue;
            }
            
            // Try BasicOperation
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
        
        Ok(PyBasicAlgebra::from_inner(basic_alg))
    }
}

impl PyPowerAlgebra {
    pub(crate) fn from_inner(inner: uacalc::alg::PowerAlgebra) -> Self {
        let root = inner.get_root();
        let card = root.cardinality();
        let reconstructed = uacalc::alg::BasicAlgebra::new(
            root.name().to_string(),
            (0..card).collect(),
            root.operations(),
        );
        PyPowerAlgebra { inner, root: reconstructed }
    }

    pub(crate) fn clone_inner(&self) -> uacalc::alg::PowerAlgebra {
        self.inner.clone()
    }
}