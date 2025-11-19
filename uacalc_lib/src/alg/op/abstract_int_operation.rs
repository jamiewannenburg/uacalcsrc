use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyList;
use uacalc::alg::op::{Operation, AbstractIntOperation};

/// Python wrapper for AbstractIntOperation
#[derive(Debug, Clone)]
enum IntOperationEvaluationMode {
    Function(PyObject),
    Table(Vec<i32>),
}

#[pyclass]
pub struct PyAbstractIntOperation {
    inner: AbstractIntOperation,
    evaluation_mode: Option<IntOperationEvaluationMode>,
}

#[pymethods]
impl PyAbstractIntOperation {
    /// Create a new AbstractIntOperation with name, arity, and algebra size.
    ///
    /// Args:
    ///     name (str): The name of the operation
    ///     arity (int): The arity (number of arguments) of the operation
    ///     alg_size (int): The size of the algebra set
    ///
    /// Raises:
    ///     ValueError: If parameters are invalid
    #[new]
    fn new(name: &str, arity: i32, alg_size: i32) -> PyResult<Self> {
        match AbstractIntOperation::new_safe(name, arity, alg_size) {
            Ok(inner) => Ok(PyAbstractIntOperation { inner, evaluation_mode: None }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new AbstractIntOperation with an existing OperationSymbol.
    ///
    /// Args:
    ///     symbol (OperationSymbol): The operation symbol
    ///     alg_size (int): The size of the algebra set
    ///
    /// Raises:
    ///     ValueError: If alg_size is invalid
    #[staticmethod]
    fn with_symbol(symbol: &super::operation_symbol::PyOperationSymbol, alg_size: i32) -> PyResult<Self> {
        match AbstractIntOperation::new_with_symbol_safe(symbol.get_inner().clone(), alg_size) {
            Ok(inner) => Ok(PyAbstractIntOperation { inner, evaluation_mode: None }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new AbstractIntOperation from a Python function evaluating on int args (as used in tests).
    #[staticmethod]
    fn from_int_value_at_function(name: &str, arity: i32, set_size: i32, int_value_at_fn: PyObject) -> PyResult<Self> {
        match AbstractIntOperation::new_safe(name, arity, set_size) {
            Ok(inner) => Ok(PyAbstractIntOperation { inner, evaluation_mode: Some(IntOperationEvaluationMode::Function(int_value_at_fn)) }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new AbstractIntOperation from a precomputed table (as used in tests).
    #[staticmethod]
    fn from_table(name: &str, arity: i32, set_size: i32, table: &Bound<'_, pyo3::types::PyAny>) -> PyResult<Self> {
        // Validate symbol and sizes
        let inner = match AbstractIntOperation::new_safe(name, arity, set_size) {
            Ok(inner) => inner,
            Err(e) => return Err(PyValueError::new_err(e)),
        };

        let table_vec: Vec<i32> = table.extract()?;
        let expected_size = if arity == 0 { 1 } else { (set_size as usize).pow(arity as u32) };

        if table_vec.len() != expected_size {
            return Err(PyValueError::new_err(format!(
                "Table size {} doesn't match expected size {} for arity {} and set size {}",
                table_vec.len(), expected_size, arity, set_size
            )));
        }

        for (i, &value) in table_vec.iter().enumerate() {
            if value < 0 || value >= set_size {
                return Err(PyValueError::new_err(format!(
                    "Table value {} at index {} is out of range [0, {})",
                    value, i, set_size
                )));
            }
        }

        Ok(PyAbstractIntOperation { inner, evaluation_mode: Some(IntOperationEvaluationMode::Table(table_vec)) })
    }

    

    /// Get the arity of this operation.
    fn arity(&self) -> i32 {
        self.inner.arity()
    }

    /// Get the size of the set upon which the operation is defined.
    fn get_set_size(&self) -> i32 {
        self.inner.get_set_size()
    }

    /// Get the operation symbol for this operation.
    fn symbol(&self) -> super::operation_symbol::PyOperationSymbol { super::operation_symbol::PyOperationSymbol::from_inner(self.inner.symbol().clone()) }

    /// Attempt to evaluate the operation (will fail with UnsupportedOperationException).
    ///
    /// Args:
    ///     args (List[int]): Arguments for the operation
    ///
    /// Raises:
    ///     ValueError: Always raises since this method is not implemented
    fn value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        // Delegate to integer evaluation for int-based universes
        self.int_value_at(args)
    }

    /// Attempt integer operation evaluation (will fail with UnsupportedOperationException).
    ///
    /// Args:
    ///     args (List[int]): Integer arguments
    ///
    /// Raises:
    ///     ValueError: Always raises since this method is not implemented
    fn int_value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        if args.len() != self.arity() as usize {
            return Err(PyValueError::new_err(format!("Expected {} arguments, got {}", self.arity(), args.len())));
        }
        for &arg in &args {
            if arg < 0 || arg >= self.get_set_size() {
                return Err(PyValueError::new_err(format!("Argument {} is out of bounds [0, {})", arg, self.get_set_size())));
            }
        }

        match &self.evaluation_mode {
            Some(IntOperationEvaluationMode::Function(func)) => {
                Python::with_gil(|py| {
                    let py_args = PyList::new_bound(py, &args);
                    let result = func.call1(py, (py_args,))?;
                    let result_int: i32 = result.extract(py)?;
                    if result_int < 0 || result_int >= self.get_set_size() {
                        return Err(PyValueError::new_err(format!(
                            "Function returned {} which is out of range [0, {})", result_int, self.get_set_size()
                        )));
                    }
                    Ok(result_int)
                })
            }
            Some(IntOperationEvaluationMode::Table(table)) => {
                let index = self.horner_encode(&args);
                Ok(table[index as usize])
            }
            None => match self.inner.int_value_at(&args) {
                Ok(result) => Ok(result),
                Err(e) => Err(PyValueError::new_err(e)),
            },
        }
    }

    /// Check if this operation is total.
    fn is_total(&self) -> PyResult<bool> { Ok(true) }

    fn make_table(&mut self) -> PyResult<()> {
        let func = match &self.evaluation_mode {
            Some(IntOperationEvaluationMode::Table(_)) => return Ok(()),
            Some(IntOperationEvaluationMode::Function(f)) => f.clone(),
            None => return Err(PyValueError::new_err("No evaluation function to make table from")),
        };

        Python::with_gil(|py| {
            let arity = self.arity();
            let set_size = self.get_set_size();
            let table_size = if arity == 0 { 1 } else { (set_size as usize).pow(arity as u32) };
            let mut table = Vec::with_capacity(table_size);

            let mut all_args = Vec::new();
            if arity == 0 {
                all_args.push(Vec::new());
            } else {
                Self::generate_args_static(arity, set_size, &mut Vec::new(), &mut all_args);
            }

            for args in all_args {
                let py_args = PyList::new_bound(py, &args);
                let result = func.call1(py, (py_args,))?;
                let result_int: i32 = result.extract(py)?;
                if result_int < 0 || result_int >= set_size {
                    return Err(PyValueError::new_err(format!(
                        "Function returned {} which is out of range [0, {})", result_int, set_size
                    )));
                }
                table.push(result_int);
            }

            self.evaluation_mode = Some(IntOperationEvaluationMode::Table(table));
            Ok(())
        })
    }

    fn get_table(&self) -> Option<Vec<i32>> {
        match &self.evaluation_mode {
            Some(IntOperationEvaluationMode::Table(t)) => Some(t.clone()),
            _ => None,
        }
    }

    fn is_table_based(&self) -> bool {
        matches!(self.evaluation_mode, Some(IntOperationEvaluationMode::Table(_)))
    }

    fn is_idempotent(&self) -> PyResult<bool> {
        let arity = self.arity();
        for x in 0..self.get_set_size() {
            let args = vec![x; arity as usize];
            if self.int_value_at(args)? != x {
                return Ok(false);
            }
        }
        Ok(true)
    }

    fn is_associative(&self) -> PyResult<bool> {
        if self.arity() != 2 { return Ok(false); }
        for x in 0..self.get_set_size() {
            for y in 0..self.get_set_size() {
                for z in 0..self.get_set_size() {
                    let xy = self.int_value_at(vec![x, y])?;
                    let yz = self.int_value_at(vec![y, z])?;
                    let left = self.int_value_at(vec![xy, z])?;
                    let right = self.int_value_at(vec![x, yz])?;
                    if left != right { return Ok(false); }
                }
            }
        }
        Ok(true)
    }

    fn is_commutative(&self) -> PyResult<bool> {
        if self.arity() != 2 { return Ok(false); }
        for x in 0..self.get_set_size() {
            for y in 0..self.get_set_size() {
                let xy = self.int_value_at(vec![x, y])?;
                let yx = self.int_value_at(vec![y, x])?;
                if xy != yx { return Ok(false); }
            }
        }
        Ok(true)
    }

    fn is_totally_symmetric(&self) -> PyResult<bool> {
        let arity = self.arity() as usize;
        if arity <= 1 { return Ok(true); }
        // Check symmetry by swapping first two args across all tuples
        let mut all_args = Vec::new();
        self.generate_args_recursive(self.arity(), &mut Vec::new(), &mut all_args);
        for args in all_args {
            let original = self.int_value_at(args.clone())?;
            let mut swapped = args;
            swapped.swap(0, 1);
            let swapped_result = self.int_value_at(swapped)?;
            if original != swapped_result { return Ok(false); }
        }
        Ok(true)
    }

    fn is_maltsev(&self) -> PyResult<bool> {
        if self.arity() != 3 { return Ok(false); }
        for x in 0..self.get_set_size() {
            for y in 0..self.get_set_size() {
                let xyy = self.int_value_at(vec![x, y, y])?;
                let xxy = self.int_value_at(vec![x, x, y])?;
                if xyy != x || xxy != y { return Ok(false); }
            }
        }
        Ok(true)
    }

    /// Python string representation.
    fn __str__(&self) -> String {
        format!(
            "AbstractIntOperation({}, arity={}, set_size={}, table_based={})",
            self.inner.symbol(), self.arity(), self.get_set_size(), self.is_table_based()
        )
    }

    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!(
            "AbstractIntOperation(name='{}', arity={}, set_size={}, table_based={})",
            self.inner.symbol().name(), self.arity(), self.get_set_size(), self.is_table_based()
        )
    }

    /// Python equality comparison.
    fn __eq__(&self, other: &PyAbstractIntOperation) -> bool {
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

impl PyAbstractIntOperation {
    fn horner_encode(&self, args: &[i32]) -> i32 {
        let mut result = 0;
        let mut multiplier = 1;
        for &arg in args.iter().rev() {
            result += arg * multiplier;
            multiplier *= self.get_set_size();
        }
        result
    }

    fn generate_args_recursive(&self, arity: i32, current: &mut Vec<i32>, all_args: &mut Vec<Vec<i32>>) {
        Self::generate_args_static(arity, self.get_set_size(), current, all_args);
    }

    fn generate_args_static(arity: i32, set_size: i32, current: &mut Vec<i32>, all_args: &mut Vec<Vec<i32>>) {
        if current.len() == arity as usize {
            all_args.push(current.clone());
            return;
        }
        for i in 0..set_size {
            current.push(i);
            Self::generate_args_static(arity, set_size, current, all_args);
            current.pop();
        }
    }
}