use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::{PyAny, PyList};
use uacalc::alg::op::{IntOperation, Operation};
use crate::alg::op::operation_symbol::PyOperationSymbol;

/// Python wrapper for IntOperation
#[pyclass]
pub struct PyIntOperation {
    pub(crate) inner: IntOperation,
}

#[pymethods]
impl PyIntOperation {
    /// Create a new IntOperation with the given parameters.
    ///
    /// Args:
    ///     symbol (OperationSymbol): The operation symbol
    ///     set_size (int): The size of the set on which the operation is defined
    ///     table (List[int] or numpy.ndarray): The precomputed table of operation results
    ///
    /// Raises:
    ///     ValueError: If parameters are invalid
    #[new]
    fn new(symbol: &PyOperationSymbol, set_size: i32, table: &PyAny) -> PyResult<Self> {
        // Try to convert table to Vec<i32> - handles both lists and numpy arrays
        let table_vec: Vec<i32> = table.extract()?;
        match IntOperation::new(symbol.get_inner().clone(), set_size, table_vec) {
            Ok(inner) => Ok(PyIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a binary XOR operation for testing.
    ///
    /// Args:
    ///     name (str): The name of the operation
    ///
    /// Returns:
    ///     IntOperation: A new IntOperation implementing XOR on {0, 1}
    #[staticmethod]
    fn binary_xor(name: &str) -> PyResult<Self> {
        match IntOperation::binary_xor(name) {
            Ok(inner) => Ok(PyIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a binary AND operation for testing.
    ///
    /// Args:
    ///     name (str): The name of the operation
    ///
    /// Returns:
    ///     IntOperation: A new IntOperation implementing AND on {0, 1}
    #[staticmethod]
    fn binary_and(name: &str) -> PyResult<Self> {
        match IntOperation::binary_and(name) {
            Ok(inner) => Ok(PyIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a binary OR operation for testing.
    ///
    /// Args:
    ///     name (str): The name of the operation
    ///
    /// Returns:
    ///     IntOperation: A new IntOperation implementing OR on {0, 1}
    #[staticmethod]
    fn binary_or(name: &str) -> PyResult<Self> {
        match IntOperation::binary_or(name) {
            Ok(inner) => Ok(PyIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a unary NOT operation for testing.
    ///
    /// Args:
    ///     name (str): The name of the operation
    ///
    /// Returns:
    ///     IntOperation: A new IntOperation implementing NOT on {0, 1}
    #[staticmethod]
    fn unary_not(name: &str) -> PyResult<Self> {
        match IntOperation::unary_not(name) {
            Ok(inner) => Ok(PyIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a nullary constant operation for testing.
    ///
    /// Args:
    ///     name (str): The name of the operation
    ///     constant_value (int): The constant value to return
    ///
    /// Returns:
    ///     IntOperation: A new IntOperation returning the constant value
    #[staticmethod]
    fn nullary_constant(name: &str, constant_value: i32) -> PyResult<Self> {
        match IntOperation::nullary_constant(name, constant_value) {
            Ok(inner) => Ok(PyIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create an IntOperation from a Python function (int_value_at style).
    ///
    /// Args:
    ///     name (str): The name of the operation
    ///     arity (int): The arity (number of arguments) of the operation
    ///     set_size (int): The size of the set on which the operation is defined
    ///     int_value_at_fn (callable): A Python function that takes a list of integers and returns an integer
    ///
    /// Returns:
    ///     IntOperation: A new IntOperation that uses the provided function
    ///
    /// Example:
    ///     def my_op(args):
    ///         return (args[0] + args[1]) % 3
    ///     op = IntOperation.from_int_value_at("add_mod3", 2, 3, my_op)
    #[staticmethod]
    fn from_int_value_at(name: &str, arity: i32, set_size: i32, int_value_at_fn: PyObject) -> PyResult<Self> {
        Python::with_gil(|py| {
            // Create the operation table by evaluating the function for all possible inputs
            let symbol = match uacalc::alg::op::OperationSymbol::new_safe(name, arity, false) {
                Ok(sym) => sym,
                Err(e) => return Err(PyValueError::new_err(e)),
            };

            let table_size = if arity == 0 { 1 } else { (set_size as usize).pow(arity as u32) };
            let mut table = Vec::with_capacity(table_size);

            // Generate all possible argument combinations and evaluate the function
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

            // Evaluate function for each argument combination
            for args in all_args {
                let py_args = PyList::new_bound(py, &args);
                let result = int_value_at_fn.call1(py, (py_args,))?;
                let result_int: i32 = result.extract(py)?;

                // Validate result is in range
                if result_int < 0 || result_int >= set_size {
                    return Err(PyValueError::new_err(format!(
                        "Function returned {} which is out of range [0, {})",
                        result_int, set_size
                    )));
                }

                table.push(result_int);
            }

            // Create IntOperation with computed table
            match IntOperation::new(symbol, set_size, table) {
                Ok(inner) => Ok(PyIntOperation { inner }),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        })
    }

    /// Create an IntOperation from a Python function (value_at style for non-integer universes).
    ///
    /// Args:
    ///     name (str): The name of the operation
    ///     arity (int): The arity (number of arguments) of the operation
    ///     universe (list): The universe elements (e.g., ["a", "b", "c"])
    ///     value_at_fn (callable): A Python function that takes a list of universe elements and returns a universe element
    ///
    /// Returns:
    ///     IntOperation: A new IntOperation that uses the provided function (with integer indices)
    ///
    /// Example:
    ///     def string_concat(args):
    ///         return args[0] + args[1]
    ///     op = IntOperation.from_value_at("concat", 2, ["a", "b", "c"], string_concat)
    #[staticmethod]
    fn from_value_at(name: &str, arity: i32, universe: Vec<PyObject>, value_at_fn: PyObject) -> PyResult<Self> {
        Python::with_gil(|py| {
            let set_size = universe.len() as i32;

            // Create the operation table by evaluating the function for all possible inputs
            let symbol = match uacalc::alg::op::OperationSymbol::new_safe(name, arity, false) {
                Ok(sym) => sym,
                Err(e) => return Err(PyValueError::new_err(e)),
            };

            let table_size = if arity == 0 { 1 } else { (set_size as usize).pow(arity as u32) };
            let mut table = Vec::with_capacity(table_size);

            // Generate all possible argument combinations and evaluate the function
            fn generate_indices(arity: i32, set_size: i32, current: &mut Vec<i32>, all_indices: &mut Vec<Vec<i32>>) {
                if current.len() == arity as usize {
                    all_indices.push(current.clone());
                    return;
                }
                for i in 0..set_size {
                    current.push(i);
                    generate_indices(arity, set_size, current, all_indices);
                    current.pop();
                }
            }

            let mut all_indices = Vec::new();
            if arity == 0 {
                all_indices.push(Vec::new());
            } else {
                generate_indices(arity, set_size, &mut Vec::new(), &mut all_indices);
            }

            // Evaluate function for each argument combination
            for indices in all_indices {
                // Convert indices to universe elements
                let mut universe_args = Vec::new();
                for &idx in &indices {
                    if idx < 0 || idx >= set_size {
                        return Err(PyValueError::new_err("Index out of universe bounds"));
                    }
                    universe_args.push(universe[idx as usize].clone());
                }

                let py_args = PyList::new_bound(py, &universe_args);
                let result = value_at_fn.call1(py, (py_args,))?;

                // Find the index of the result in the universe
                let mut result_index = None;
                for (i, universe_elem) in universe.iter().enumerate() {
                    if result.bind(py).eq(universe_elem)? {
                        result_index = Some(i as i32);
                        break;
                    }
                }

                match result_index {
                    Some(idx) => table.push(idx),
                    None => return Err(PyValueError::new_err(
                        "Function returned a value not in the universe"
                    )),
                }
            }

            // Create IntOperation with computed table
            match IntOperation::new(symbol, set_size, table) {
                Ok(inner) => Ok(PyIntOperation { inner }),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        })
    }

    /// Create an IntOperation from a 2D array/matrix (for binary operations).
    ///
    /// Args:
    ///     name (str): The name of the operation
    ///     operation_matrix (List[List[int]] or 2D numpy.ndarray): A 2D array where entry [i][j] gives the result of operation(i, j)
    ///
    /// Returns:
    ///     IntOperation: A new IntOperation based on the matrix
    ///
    /// Example:
    ///     # XOR operation matrix
    ///     matrix = [[0, 1], [1, 0]]
    ///     op = IntOperation.from_matrix("xor", matrix)
    #[staticmethod]
    fn from_matrix(name: &str, operation_matrix: &PyAny) -> PyResult<Self> {
        Python::with_gil(|_py| {
            // Extract the 2D matrix
            let matrix: Vec<Vec<i32>> = operation_matrix.extract()?;

            if matrix.is_empty() {
                return Err(PyValueError::new_err("Operation matrix cannot be empty"));
            }

            let set_size = matrix.len() as i32;

            // Validate matrix is square and all rows have the same length
            for (i, row) in matrix.iter().enumerate() {
                if row.len() != set_size as usize {
                    return Err(PyValueError::new_err(format!(
                        "Row {} has length {} but expected {} (matrix must be square)",
                        i, row.len(), set_size
                    )));
                }

                // Validate all values are in range
                for (j, &value) in row.iter().enumerate() {
                    if value < 0 || value >= set_size {
                        return Err(PyValueError::new_err(format!(
                            "Value {} at position [{}, {}] is out of range [0, {})",
                            value, i, j, set_size
                        )));
                    }
                }
            }

            // Convert matrix to flat table (row-major order for binary operations)
            let mut table = Vec::with_capacity((set_size * set_size) as usize);
            for row in &matrix {
                table.extend_from_slice(row);
            }

            let symbol = match uacalc::alg::op::OperationSymbol::new_safe(name, 2, false) {
                Ok(sym) => sym,
                Err(e) => return Err(PyValueError::new_err(e)),
            };

            match IntOperation::new(symbol, set_size, table) {
                Ok(inner) => Ok(PyIntOperation { inner }),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        })
    }

    // Include all the same methods as PyAbstractOperation
    fn arity(&self) -> i32 {
        self.inner.arity()
    }

    fn get_set_size(&self) -> i32 {
        self.inner.get_set_size()
    }

    fn symbol(&self) -> PyOperationSymbol { PyOperationSymbol::from_inner(self.inner.symbol().clone()) }

    fn value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn value_at_arrays(&self, args: Vec<Vec<i32>>) -> PyResult<Vec<i32>> {
        let arg_refs: Vec<&[i32]> = args.iter().map(|v| v.as_slice()).collect();
        match self.inner.value_at_arrays(&arg_refs) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn int_value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.int_value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn int_value_at_horner(&self, arg: i32) -> PyResult<i32> {
        match self.inner.int_value_at_horner(arg) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn make_table(&mut self) -> PyResult<()> {
        match self.inner.make_table() {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn get_table(&self) -> Option<Vec<i32>> {
        self.inner.get_table().map(|slice| slice.to_vec())
    }

    fn get_table_force(&mut self, make_table: bool) -> PyResult<Vec<i32>> {
        match self.inner.get_table_force(make_table) {
            Ok(slice) => Ok(slice.to_vec()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn is_table_based(&self) -> bool {
        self.inner.is_table_based()
    }

    fn is_idempotent(&self) -> PyResult<bool> {
        match self.inner.is_idempotent() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn is_associative(&self) -> PyResult<bool> {
        match self.inner.is_associative() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn is_commutative(&self) -> PyResult<bool> {
        match self.inner.is_commutative() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn is_totally_symmetric(&self) -> PyResult<bool> {
        match self.inner.is_totally_symmetric() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn is_maltsev(&self) -> PyResult<bool> {
        match self.inner.is_maltsev() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn is_total(&self) -> PyResult<bool> {
        match self.inner.is_total() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    fn __repr__(&self) -> String {
        format!("IntOperation({})", self.inner.to_string())
    }

    fn __eq__(&self, other: &PyIntOperation) -> bool {
        self.inner == other.inner
    }

    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }

    fn __lt__(&self, other: &PyIntOperation) -> bool {
        self.inner < other.inner
    }

    fn __le__(&self, other: &PyIntOperation) -> bool {
        self.inner <= other.inner
    }

    fn __gt__(&self, other: &PyIntOperation) -> bool {
        self.inner > other.inner
    }

    fn __ge__(&self, other: &PyIntOperation) -> bool {
        self.inner >= other.inner
    }
}