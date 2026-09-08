#![allow(warnings)]

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::{PyList, PyAny};
use crate::alg::universe_map::PyUniverseMap;

/// Python wrapper for GeneralAlgebra that supports Python objects and AbstractOperations
#[pyclass]
pub struct PyGeneralAlgebra {
    name: String,
    description: Option<String>,
    universe: PyUniverseMap,
    operations: Vec<PyObject>, // Operations stored as PyObject references to PyAbstractOperationNew
}

#[pymethods]
impl PyGeneralAlgebra {
    /// Create a new GeneralAlgebra with a name, universe (list/set of Python objects), and operations.
    ///
    /// Args:
    ///     name (str): The name of the algebra
    ///     universe (List[Any]): The universe set as a list of Python objects
    ///     operations (Optional[List[AbstractOperation]]): List of AbstractOperation instances (optional)
    ///
    /// Returns:
    ///     GeneralAlgebra: A new GeneralAlgebra instance
    ///
    /// Raises:
    ///     ValueError: If universe is empty or contains duplicates
    #[new]
    #[pyo3(signature = (name, universe, operations=None))]
    fn new(
        py: Python<'_>,
        name: String,
        universe: &Bound<'_, PyAny>,
        operations: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Self> {
        // Extract universe as a list of PyObjects
        let universe_list: Vec<PyObject> = if let Ok(list) = universe.extract::<Vec<PyObject>>() {
            list
        } else if let Ok(iter) = universe.iter() {
            let mut result = Vec::new();
            for item in iter {
                result.push(item?.to_object(py));
            }
            result
        } else {
            return Err(PyValueError::new_err("Universe must be a list, set, or iterable"));
        };

        if universe_list.is_empty() {
            return Err(PyValueError::new_err("Universe cannot be empty"));
        }

        let universe = PyUniverseMap::from_objects(py, universe_list, true)?;

        // Extract operations
        let operations_list: Vec<PyObject> = if let Some(ops) = operations {
            if let Ok(list) = ops.extract::<Vec<PyObject>>() {
                list
            } else if let Ok(iter) = ops.iter() {
                let mut result = Vec::new();
                for item in iter {
                    result.push(item?.to_object(py));
                }
                result
            } else {
                return Err(PyValueError::new_err("Operations must be a list or iterable"));
            }
        } else {
            Vec::new()
        };

        // Validate that all operations are AbstractOperation instances
        for op in &operations_list {
            if op.bind(py).getattr("int_value_at").is_err() {
                return Err(PyValueError::new_err("All operations must be AbstractOperation instances"));
            }
        }

        Ok(PyGeneralAlgebra {
            name,
            description: None,
            universe,
            operations: operations_list,
        })
    }

    /// Create a new GeneralAlgebra with just a name.
    ///
    /// Args:
    ///     name (str): The name of the algebra
    ///
    /// Returns:
    ///     GeneralAlgebra: A new GeneralAlgebra instance with empty universe
    #[staticmethod]
    fn with_name(py: Python<'_>, name: String) -> Self {
        PyGeneralAlgebra {
            name,
            description: None,
            universe: PyUniverseMap::from_objects(py, Vec::new(), false)
                .expect("an empty universe map is valid"),
            operations: Vec::new(),
        }
    }

    /// Create a new GeneralAlgebra with a name and universe.
    ///
    /// Args:
    ///     name (str): The name of the algebra
    ///     universe (List[Any]): The universe set as a list of Python objects
    ///
    /// Returns:
    ///     GeneralAlgebra: A new GeneralAlgebra instance
    ///
    /// Raises:
    ///     ValueError: If universe is empty or contains duplicates
    #[staticmethod]
    fn with_universe(py: Python<'_>, name: String, universe: &Bound<'_, PyAny>) -> PyResult<Self> {
        // Extract universe as a list of PyObjects
        let universe_list: Vec<PyObject> = if let Ok(list) = universe.extract::<Vec<PyObject>>() {
            list
        } else if let Ok(iter) = universe.iter() {
            let mut result = Vec::new();
            for item in iter {
                result.push(item?.to_object(py));
            }
            result
        } else {
            return Err(PyValueError::new_err("Universe must be a list, set, or iterable"));
        };

        if universe_list.is_empty() {
            return Err(PyValueError::new_err("Universe cannot be empty"));
        }

        let universe = PyUniverseMap::from_objects(py, universe_list, true)?;

        Ok(PyGeneralAlgebra {
            name,
            description: None,
            universe,
            operations: Vec::new(),
        })
    }

    /// Get the name of this algebra.
    ///
    /// Returns:
    ///     str: The name of the algebra
    fn name(&self) -> &str {
        &self.name
    }

    /// Set the name of this algebra.
    ///
    /// Args:
    ///     name (str): The new name for the algebra
    fn set_name(&mut self, name: String) {
        self.name = name;
    }

    /// Get the description of this algebra.
    ///
    /// Returns:
    ///     Optional[str]: The description of the algebra, or None if not set
    fn description(&self) -> Option<String> {
        self.description.clone()
    }

    /// Set the description of this algebra.
    ///
    /// Args:
    ///     desc (Optional[str]): The new description for the algebra
    fn set_description(&mut self, desc: Option<String>) {
        self.description = desc;
    }

    /// Get the cardinality of this algebra.
    ///
    /// Returns:
    ///     int: The cardinality of the universe
    fn cardinality(&self) -> i32 {
        self.universe.len() as i32
    }

    /// Get the input size for this algebra.
    ///
    /// Returns:
    ///     int: The input size (same as cardinality for finite algebras)
    fn input_size(&self) -> i32 {
        self.universe.len() as i32
    }

    /// Check if this algebra is unary.
    ///
    /// Returns:
    ///     bool: True if all operations have arity 1
    fn is_unary(&self, py: Python<'_>) -> PyResult<bool> {
        for op_obj in &self.operations {
            let arity = op_obj.bind(py).getattr("arity")?.call0()?;
            let arity_int: i32 = arity.extract()?;
            if arity_int != 1 {
                return Ok(false);
            }
        }
        Ok(true)
    }

    /// Check if all operations in this algebra are idempotent.
    ///
    /// Returns:
    ///     bool: True if all operations are idempotent
    fn is_idempotent(&self, py: Python<'_>) -> PyResult<bool> {
        for op_obj in &self.operations {
            if let Ok(is_idem) = op_obj.bind(py).getattr("is_idempotent") {
                if let Ok(result) = is_idem.call0() {
                    if let Ok(false) = result.extract::<bool>() {
                        return Ok(false);
                    }
                }
            } else {
                // If operation doesn't have is_idempotent, check manually
                let arity = op_obj.bind(py).getattr("arity")?.call0()?;
                let arity_int: i32 = arity.extract()?;
                let set_size = self.universe.len() as i32;
                
                for x in 0..set_size {
                    let args = vec![x; arity_int as usize];
                    let result = op_obj.bind(py).call_method1("int_value_at", (args,))?;
                    let result_int: i32 = result.extract()?;
                    if result_int != x {
                        return Ok(false);
                    }
                }
            }
        }
        Ok(true)
    }

    /// Check if all operations in this algebra are total.
    ///
    /// Returns:
    ///     bool: True if all operations are total
    fn is_total(&self, py: Python<'_>) -> PyResult<bool> {
        // AbstractOperations are always total
        Ok(true)
    }

    /// Check if monitoring is enabled for this algebra.
    ///
    /// Returns:
    ///     bool: Always False (monitoring not implemented)
    fn monitoring(&self) -> bool {
        false
    }

    /// Get the universe as a list of Python objects.
    ///
    /// Returns:
    ///     List[Any]: The universe elements as a list
    fn get_universe(&self) -> Vec<PyObject> {
        self.universe.labels_owned()
    }

    /// Get the universe as a list of Python objects (alias for get_universe).
    ///
    /// Returns:
    ///     List[Any]: The universe elements as a list
    fn universe(&self) -> Vec<PyObject> {
        self.get_universe()
    }

    /// Get the operations of this algebra.
    ///
    /// Returns:
    ///     List[AbstractOperation]: List of AbstractOperation instances
    fn get_operations(&self, py: Python<'_>) -> Vec<PyObject> {
        self.operations.clone()
    }

    /// Add an operation to this algebra.
    ///
    /// Args:
    ///     operation (AbstractOperation): The operation to add
    ///
    /// Raises:
    ///     ValueError: If operation is not an AbstractOperation
    fn add_operation(&mut self, py: Python<'_>, operation: &Bound<'_, PyAny>) -> PyResult<()> {
        if operation.getattr("int_value_at").is_err() {
            return Err(PyValueError::new_err("Operation must be an AbstractOperation instance"));
        }
        self.operations.push(operation.to_object(py));
        Ok(())
    }

    /// Get an operation by index.
    ///
    /// Args:
    ///     index (int): The index of the operation
    ///
    /// Returns:
    ///     AbstractOperation: The operation at the given index
    ///
    /// Raises:
    ///     IndexError: If index is out of bounds
    fn get_operation(&self, py: Python<'_>, index: usize) -> PyResult<PyObject> {
        if index >= self.operations.len() {
            return Err(PyValueError::new_err(format!("Operation index {} out of bounds", index)));
        }
        Ok(self.operations[index].clone())
    }

    /// Get the number of operations.
    ///
    /// Returns:
    ///     int: The number of operations
    fn operations_count(&self) -> usize {
        self.operations.len()
    }

    /// Convert this GeneralAlgebra to a BasicAlgebra.
    ///
    /// This method converts a GeneralAlgebra (which can have arbitrary Python objects
    /// as universe elements) to a BasicAlgebra (which requires integer universe elements).
    ///
    /// Args:
    ///     None
    ///
    /// Returns:
    ///     BasicAlgebra: A new BasicAlgebra instance with the same name, universe (as integers),
    ///                   and operations (converted to IntOperation)
    ///
    /// Raises:
    ///     ValueError: If universe elements cannot be converted to integers, or if operations
    ///                  cannot be converted to IntOperation
    pub(crate) fn to_basic_algebra(&self, py: Python<'_>) -> PyResult<crate::alg::PyBasicAlgebra> {
        use crate::alg::PyBasicAlgebra;
        let set_size = i32::try_from(self.universe.len())
            .map_err(|_| PyValueError::new_err("Universe is too large"))?;
        let universe_set = (0..set_size).collect();
        
        // Convert operations from PyAbstractOperationNew to IntOperation
        let mut rust_ops: Vec<Box<dyn uacalc::alg::op::Operation>> = Vec::new();
        
        for op_obj in &self.operations {
            let op_bound = op_obj.bind(py);
            
            // Check if it's a PyAbstractOperationNew
            if op_bound.getattr("int_value_at").is_err() {
                return Err(PyValueError::new_err(
                    "Operations must be AbstractOperation instances with int_value_at method"
                ));
            }
            
            // Get operation properties
            let arity: i32 = op_bound.getattr("arity")?.call0()?.extract()?;
            let op_set_size: i32 = op_bound.getattr("get_set_size")?.call0()?.extract()?;
            if op_set_size != set_size {
                return Err(PyValueError::new_err(format!(
                    "Operation has set size {}, expected {}",
                    op_set_size, set_size
                )));
            }
            
            // Get symbol name
            let symbol_obj = op_bound.getattr("symbol")?.call0()?;
            let symbol_name: String = symbol_obj.getattr("name")?.call0()?.extract()?;
            
            // Try to get table first (more efficient)
            let mut table: Option<Vec<i32>> = if let Ok(get_table) = op_bound.getattr("get_table") {
                if let Ok(table_result) = get_table.call0() {
                    if let Ok(Some(table_vec)) = table_result.extract::<Option<Vec<i32>>>() {
                        Some(table_vec)
                    } else {
                        None
                    }
                } else {
                    None
                }
            } else {
                None
            };

            // Native abstract operations cache their table after the first
            // conversion, so repeated conversions never re-enter Python.
            if table.is_none() && op_bound.call_method0("make_table").is_ok() {
                table = op_bound
                    .call_method0("get_table")?
                    .extract::<Option<Vec<i32>>>()?;
            }
            
            // Build table if not available
            let final_table = if let Some(t) = table {
                t
            } else {
                // Generate table by calling int_value_at for all argument combinations
                let table_size = if arity == 0 {
                    1
                } else {
                    (set_size as usize)
                        .checked_pow(arity as u32)
                        .ok_or_else(|| PyValueError::new_err("Operation table size overflow"))?
                };
                let mut op_table = Vec::with_capacity(table_size);

                for encoded in 0..table_size {
                    let args = uacalc::util::horner::horner_inv_same_size(
                        encoded as i32,
                        set_size,
                        arity as usize,
                    );
                    let py_args = PyList::new_bound(py, &args);
                    let result = op_bound.call_method1("int_value_at", (py_args,))?;
                    let result_int: i32 = result.extract()?;
                    
                    // Validate result is in range
                    if result_int < 0 || result_int >= set_size {
                        return Err(PyValueError::new_err(format!(
                            "Operation {} returned {} which is out of range [0, {})",
                            symbol_name, result_int, set_size
                        )));
                    }
                    
                    op_table.push(result_int);
                }
                
                op_table
            };
            
            // Create IntOperation from table
            let symbol = match uacalc::alg::op::OperationSymbol::new_safe(&symbol_name, arity, false) {
                Ok(sym) => sym,
                Err(e) => return Err(PyValueError::new_err(format!("Invalid operation symbol: {}", e))),
            };
            
            let int_op = match uacalc::alg::op::IntOperation::new(symbol, set_size, final_table) {
                Ok(op) => op,
                Err(e) => return Err(PyValueError::new_err(format!("Failed to create IntOperation: {}", e))),
            };
            
            rust_ops.push(Box::new(int_op) as Box<dyn uacalc::alg::op::Operation>);
        }
        
        // Create BasicAlgebra
        let basic_alg = uacalc::alg::BasicAlgebra::new(
            self.name.clone(),
            universe_set,
            rust_ops
        );
        
        if self.universe.is_dense_integer_identity(py) {
            Ok(PyBasicAlgebra::from_inner(basic_alg))
        } else {
            Ok(PyBasicAlgebra::from_inner_with_map(
                basic_alg,
                self.universe.clone(),
            ))
        }
    }

    /// Python string representation
    fn __str__(&self) -> String {
        format!("GeneralAlgebra(name='{}', cardinality={}, operations={})",
                self.name, self.universe.len(), self.operations.len())
    }

    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("GeneralAlgebra(name='{}', cardinality={}, operations={})",
                self.name, self.universe.len(), self.operations.len())
    }

    /// Python equality comparison
    fn __eq__(&self, other: &Bound<'_, PyGeneralAlgebra>, py: Python<'_>) -> PyResult<bool> {
        let other = other.borrow();
        if self.name != other.name {
            return Ok(false);
        }
        if self.universe.len() != other.universe.len() {
            return Ok(false);
        }
        if self.operations.len() != other.operations.len() {
            return Ok(false);
        }
        // Compare universes element by element
        for (self_elem, other_elem) in self
            .universe
            .labels()
            .iter()
            .zip(other.universe.labels())
        {
            if !self_elem.bind(py).eq(other_elem.bind(py))? {
                return Ok(false);
            }
        }
        Ok(true)
    }
    
    /// Python hash implementation
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        let mut hasher = DefaultHasher::new();
        self.name.hash(&mut hasher);
        self.universe.len().hash(&mut hasher);
        self.operations.len().hash(&mut hasher);
        hasher.finish()
    }
}

pub fn register_general_algebra_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyGeneralAlgebra>()?;
    m.add("GeneralAlgebra", m.getattr("PyGeneralAlgebra")?)?;
    Ok(())
}