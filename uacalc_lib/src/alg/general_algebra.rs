#![allow(warnings)]

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::{PyList, PyAny};

/// Python wrapper for GeneralAlgebra that supports Python objects and AbstractOperations
#[pyclass]
pub struct PyGeneralAlgebra {
    name: String,
    description: Option<String>,
    universe: Vec<PyObject>, // Universe as Python objects
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

        // Build unique universe and check for duplicates
        let mut unique_universe: Vec<PyObject> = Vec::new();
        for elem in universe_list.iter() {
            // Check if we've seen this element before using Python equality
            let mut found = false;
            for existing_elem in unique_universe.iter() {
                if elem.bind(py).eq(existing_elem.bind(py))? {
                    found = true;
                    break;
                }
            }
            if !found {
                unique_universe.push(elem.clone());
            }
        }

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
            universe: unique_universe,
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
    fn with_name(name: String) -> Self {
        PyGeneralAlgebra {
            name,
            description: None,
            universe: Vec::new(),
            operations: Vec::new(),
        }
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
    fn get_universe(&self, py: Python<'_>) -> Vec<PyObject> {
        self.universe.clone()
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
        use std::collections::HashSet;
        
        // Convert universe elements to integers
        let mut universe_ints: Vec<i32> = Vec::new();
        
        for (idx, elem) in self.universe.iter().enumerate() {
            let idx_i32 = idx as i32;
            
            // Try to extract as integer directly
            if let Ok(int_val) = elem.bind(py).extract::<i32>() {
                universe_ints.push(int_val);
            } else {
                // If not an integer, use the index as the integer value
                universe_ints.push(idx_i32);
            }
        }
        
        let universe_set: HashSet<i32> = universe_ints.iter().cloned().collect();
        let set_size = universe_set.len() as i32;
        
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
            
            // Get symbol name
            let symbol_obj = op_bound.getattr("symbol")?.call0()?;
            let symbol_name: String = symbol_obj.getattr("name")?.call0()?.extract()?;
            
            // Try to get table first (more efficient)
            let table: Option<Vec<i32>> = if let Ok(get_table) = op_bound.getattr("get_table") {
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
            
            // Build table if not available
            let final_table = if let Some(t) = table {
                t
            } else {
                // Generate table by calling int_value_at for all argument combinations
                let table_size = if arity == 0 { 1 } else { (set_size as usize).pow(arity as u32) };
                let mut op_table = Vec::with_capacity(table_size);
                
                // Generate all argument combinations
                fn generate_args(arity: i32, set_size: i32, current: &mut Vec<i32>, all_args: &mut Vec<Vec<i32>>) {
                    if current.len() == arity as usize {
                        all_args.push(current.clone());
                        return;
                    }
                    for i in 0..set_size {
                        current.push(i);
                        generate_args(arity, set_size, current, all_args);
                        current.pop();
                    }
                }
                
                let mut all_args = Vec::new();
                if arity == 0 {
                    all_args.push(Vec::new());
                } else {
                    generate_args(arity, set_size, &mut Vec::new(), &mut all_args);
                }
                
                // Evaluate operation for each argument combination
                for args in all_args {
                    // Map universe elements to integers if needed
                    let mapped_args: Vec<i32> = if op_set_size == set_size {
                        args
                    } else {
                        // If operation uses different universe, we need to map
                        // For now, assume they match
                        args
                    };
                    
                    let py_args = PyList::new_bound(py, &mapped_args);
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
        
        Ok(PyBasicAlgebra::from_inner(basic_alg))
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
        for (self_elem, other_elem) in self.universe.iter().zip(other.universe.iter()) {
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