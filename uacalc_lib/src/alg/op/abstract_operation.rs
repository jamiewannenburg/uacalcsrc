use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyList;
use std::sync::Arc;
use crate::alg::op::operation_symbol::PyOperationSymbol;
use crate::alg::universe_map::PyUniverseMap;

/// Evaluation mode for AbstractOperation that supports both integer and non-integer universes
#[derive(Debug, Clone)]
enum AbstractOperationEvaluationMode {
    IntFunction(PyObject),
    ValueFunction(PyObject, PyUniverseMap),
    IntTable(Arc<[i32]>),
    ValueTable(Arc<[i32]>, PyUniverseMap),
}

/// Python wrapper for the new AbstractOperation class (supports both integer and non-integer universes)
#[pyclass]
pub struct PyAbstractOperationNew {
    symbol: uacalc::alg::op::OperationSymbol,
    set_size: i32,
    evaluation_mode: AbstractOperationEvaluationMode,
}

#[pymethods]
impl PyAbstractOperationNew {
    #[staticmethod]
    fn from_int_value_at_function(name: &str, arity: i32, set_size: i32, int_value_at_fn: PyObject) -> PyResult<Self> {
        let symbol = match uacalc::alg::op::OperationSymbol::new_safe(name, arity, false) {
            Ok(sym) => sym,
            Err(e) => return Err(PyValueError::new_err(e)),
        };

        if set_size <= 0 {
            return Err(PyValueError::new_err("Set size must be positive"));
        }

        Ok(PyAbstractOperationNew {
            symbol,
            set_size,
            evaluation_mode: AbstractOperationEvaluationMode::IntFunction(int_value_at_fn),
        })
    }

    #[staticmethod]
    fn from_value_at_function(
        py: Python<'_>,
        name: &str,
        arity: i32,
        universe: Vec<PyObject>,
        value_at_fn: PyObject,
    ) -> PyResult<Self> {
        let universe = PyUniverseMap::from_objects(py, universe, true)?;
        let set_size = universe.len() as i32;
        let symbol = match uacalc::alg::op::OperationSymbol::new_safe(name, arity, false) {
            Ok(sym) => sym,
            Err(e) => return Err(PyValueError::new_err(e)),
        };

        if set_size <= 0 {
            return Err(PyValueError::new_err("Universe cannot be empty"));
        }

        Ok(PyAbstractOperationNew {
            symbol,
            set_size,
            evaluation_mode: AbstractOperationEvaluationMode::ValueFunction(value_at_fn, universe),
        })
    }

    fn arity(&self) -> i32 { self.symbol.arity() }
    fn get_set_size(&self) -> i32 { self.set_size }
    fn symbol(&self) -> PyOperationSymbol { PyOperationSymbol::from_inner(self.symbol.clone()) }

    fn int_value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        if args.len() != self.arity() as usize {
            return Err(PyValueError::new_err(format!("Expected {} arguments, got {}", self.arity(), args.len())));
        }

        for &arg in &args {
            if arg < 0 || arg >= self.set_size {
                return Err(PyValueError::new_err(format!("Argument {} is out of bounds [0, {})", arg, self.set_size)));
            }
        }

        match &self.evaluation_mode {
            AbstractOperationEvaluationMode::IntFunction(func) => {
                Python::with_gil(|py| {
                    let py_args = PyList::new_bound(py, &args);
                    let result = func.call1(py, (py_args,))?;
                    let result_int: i32 = result.extract(py)?;

                    if result_int < 0 || result_int >= self.set_size {
                        return Err(PyValueError::new_err(format!(
                            "Function returned {} which is out of range [0, {})", result_int, self.set_size
                        )));
                    }

                    Ok(result_int)
                })
            }
            AbstractOperationEvaluationMode::ValueFunction(func, universe) => {
                Python::with_gil(|py| {
                    let universe_args: Vec<PyObject> = args
                        .iter()
                        .map(|&index| {
                            universe.element_or_error(index, "Operation argument")
                        })
                        .collect::<PyResult<_>>()?;
                    let py_args = PyList::new_bound(py, &universe_args);
                    let result = func.call1(py, (py_args,))?;

                    if let Some(index) = universe.index_of(py, result.bind(py))? {
                        return Ok(index as i32);
                    }

                    Err(PyValueError::new_err("Function returned a value not in the universe"))
                })
            }
            AbstractOperationEvaluationMode::IntTable(table) | AbstractOperationEvaluationMode::ValueTable(table, _) => {
                let index = self.horner_encode(&args);
                Ok(table[index as usize])
            }
        }
    }

    /// Evaluate the operation with actual universe elements (not indices).
    ///
    /// Args:
    ///     args (List[Any]): List of universe elements (not indices)
    ///
    /// Returns:
    ///     Any: The result as a universe element (not an index)
    ///
    /// Raises:
    ///     ValueError: If arguments are invalid or result is not in universe
    fn value_at(&self, args: Vec<PyObject>) -> PyResult<PyObject> {
        if args.len() != self.arity() as usize {
            return Err(PyValueError::new_err(format!("Expected {} arguments, got {}", self.arity(), args.len())));
        }

        Python::with_gil(|py| {
            match &self.evaluation_mode {
                AbstractOperationEvaluationMode::IntFunction(_) => {
                    // For integer functions, convert universe elements to indices
                    // First, we need to find the indices - but we don't have the universe stored
                    // So we'll need to extract as integers
                    let mut int_args = Vec::new();
                    for arg in &args {
                        let int_val: i32 = arg.bind(py).extract()?;
                        if int_val < 0 || int_val >= self.set_size {
                            return Err(PyValueError::new_err(format!("Argument {} is out of bounds [0, {})", int_val, self.set_size)));
                        }
                        int_args.push(int_val);
                    }
                    let result_idx = self.int_value_at(int_args)?;
                    // Return as integer
                    Ok(result_idx.into_py(py))
                }
                AbstractOperationEvaluationMode::ValueFunction(func, universe) => {
                    // Verify all arguments are in the universe
                    for arg in &args {
                        if universe.index_of(py, arg.bind(py))?.is_none() {
                            return Err(PyValueError::new_err("Argument not in universe"));
                        }
                    }
                    
                    // Call the function with the actual universe elements
                    let py_args = PyList::new_bound(py, &args);
                    let result = func.call1(py, (py_args,))?;
                    
                    // Verify result is in universe
                    if universe.index_of(py, result.bind(py))?.is_some() {
                        return Ok(result);
                    }
                    
                    Err(PyValueError::new_err("Function returned a value not in the universe"))
                }
                AbstractOperationEvaluationMode::IntTable(_) => {
                    // For integer tables, convert to indices and look up
                    let mut int_args = Vec::new();
                    for arg in &args {
                        let int_val: i32 = arg.bind(py).extract()?;
                        if int_val < 0 || int_val >= self.set_size {
                            return Err(PyValueError::new_err(format!("Argument {} is out of bounds [0, {})", int_val, self.set_size)));
                        }
                        int_args.push(int_val);
                    }
                    let result_idx = self.int_value_at(int_args)?;
                    Ok(result_idx.into_py(py))
                }
                AbstractOperationEvaluationMode::ValueTable(table, universe) => {
                    // Convert universe elements to indices
                    let mut int_args = Vec::new();
                    for arg in &args {
                        match universe.index_of(py, arg.bind(py))? {
                            Some(idx) => int_args.push(idx as i32),
                            None => return Err(PyValueError::new_err("Argument not in universe")),
                        }
                    }
                    let result_idx = self.int_value_at(int_args)?;
                    // Return the universe element at that index
                    universe.element_or_error(result_idx, "Operation result")
                }
            }
        })
    }

    fn make_table(&mut self) -> PyResult<()> {
        match &self.evaluation_mode {
            AbstractOperationEvaluationMode::IntTable(_) | AbstractOperationEvaluationMode::ValueTable(_, _) => Ok(()),
            AbstractOperationEvaluationMode::IntFunction(func) => {
                let func_clone = func.clone();

                Python::with_gil(|py| {
                    let arity = self.arity();
                    let table_size = if arity == 0 { 1 } else { (self.set_size as usize).pow(arity as u32) };
                    let mut table = Vec::with_capacity(table_size);

                    for encoded in 0..table_size {
                        let args = uacalc::util::horner::horner_inv_same_size(
                            encoded as i32,
                            self.set_size,
                            arity as usize,
                        );
                        let py_args = PyList::new_bound(py, &args);
                        let result = func_clone.call1(py, (py_args,))?;
                        let result_int: i32 = result.extract(py)?;
                        table.push(result_int);
                    }

                    self.evaluation_mode = AbstractOperationEvaluationMode::IntTable(table.into());
                    Ok(())
                })
            }
            AbstractOperationEvaluationMode::ValueFunction(func, universe) => {
                let func_clone = func.clone();
                let universe_clone = universe.clone();

                Python::with_gil(|py| {
                    let arity = self.arity();
                    let table_size = if arity == 0 { 1 } else { (self.set_size as usize).pow(arity as u32) };
                    let mut table = Vec::with_capacity(table_size);

                    for encoded in 0..table_size {
                        let args = uacalc::util::horner::horner_inv_same_size(
                            encoded as i32,
                            self.set_size,
                            arity as usize,
                        );
                        let universe_args: Vec<PyObject> = args
                            .iter()
                            .map(|&index| {
                                universe_clone.element_or_error(index, "Operation argument")
                            })
                            .collect::<PyResult<_>>()?;
                        let py_args = PyList::new_bound(py, &universe_args);
                        let result = func_clone.call1(py, (py_args,))?;

                        let result_index = universe_clone
                            .index_of(py, result.bind(py))?
                            .map(|index| index as i32);

                        match result_index {
                            Some(idx) => table.push(idx),
                            None => return Err(PyValueError::new_err("Function returned a value not in the universe")),
                        }
                    }

                    self.evaluation_mode =
                        AbstractOperationEvaluationMode::ValueTable(table.into(), universe_clone);
                    Ok(())
                })
            }
        }
    }

    fn get_table(&self) -> Option<Vec<i32>> {
        match &self.evaluation_mode {
            AbstractOperationEvaluationMode::IntTable(table)
            | AbstractOperationEvaluationMode::ValueTable(table, _) => {
                Some(table.as_ref().to_vec())
            }
            AbstractOperationEvaluationMode::IntFunction(_) | AbstractOperationEvaluationMode::ValueFunction(_, _) => None,
        }
    }

    fn is_table_based(&self) -> bool {
        matches!(self.evaluation_mode, AbstractOperationEvaluationMode::IntTable(_) | AbstractOperationEvaluationMode::ValueTable(_, _))
    }

    fn is_idempotent(&self) -> PyResult<bool> {
        let arity = self.arity();
        for x in 0..self.set_size {
            let args = vec![x; arity as usize];
            if self.int_value_at(args)? != x { return Ok(false); }
        }
        Ok(true)
    }

    fn is_associative(&self) -> PyResult<bool> {
        if self.arity() != 2 { return Ok(false); }
        for x in 0..self.set_size {
            for y in 0..self.set_size {
                for z in 0..self.set_size {
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
        for x in 0..self.set_size {
            for y in 0..self.set_size {
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

        if arity >= 2 {
            let mut all_args = Vec::new();
            Self::generate_args_static(self.arity(), self.set_size, &mut Vec::new(), &mut all_args);

            for args in all_args {
                let original = self.int_value_at(args.clone())?;
                let mut swapped = args;
                swapped.swap(0, 1);
                let swapped_result = self.int_value_at(swapped)?;
                if original != swapped_result { return Ok(false); }
            }
        }

        Ok(true)
    }

    fn is_maltsev(&self) -> PyResult<bool> {
        if self.arity() != 3 { return Ok(false); }
        for x in 0..self.set_size {
            for y in 0..self.set_size {
                let xyy = self.int_value_at(vec![x, y, y])?;
                let xxy = self.int_value_at(vec![x, x, y])?;
                if xyy != x || xxy != y { return Ok(false); }
            }
        }
        Ok(true)
    }

    fn is_total(&self) -> PyResult<bool> { Ok(true) }

    fn __str__(&self) -> String {
        let universe_type = match &self.evaluation_mode {
            AbstractOperationEvaluationMode::IntFunction(_) | AbstractOperationEvaluationMode::IntTable(_) => "integer",
            AbstractOperationEvaluationMode::ValueFunction(_, _) | AbstractOperationEvaluationMode::ValueTable(_, _) => "general",
        };
        format!("AbstractOperation({}, arity={}, set_size={}, universe={}, table_based={})",
                self.symbol.name(), self.arity(), self.set_size, universe_type, self.is_table_based())
    }

    fn __repr__(&self) -> String {
        let universe_type = match &self.evaluation_mode {
            AbstractOperationEvaluationMode::IntFunction(_) | AbstractOperationEvaluationMode::IntTable(_) => "integer",
            AbstractOperationEvaluationMode::ValueFunction(_, _) | AbstractOperationEvaluationMode::ValueTable(_, _) => "general",
        };
        format!("AbstractOperation(name='{}', arity={}, set_size={}, universe={}, table_based={})",
                self.symbol.name(), self.arity(), self.set_size, universe_type, self.is_table_based())
    }

    fn __eq__(&self, other: &PyAbstractOperationNew) -> bool {
        self.symbol == other.symbol && self.set_size == other.set_size
    }

    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        self.symbol.hash(&mut hasher);
        self.set_size.hash(&mut hasher);
        hasher.finish()
    }
}

impl PyAbstractOperationNew {
    pub(crate) fn from_value_table(
        symbol: uacalc::alg::op::OperationSymbol,
        table: Vec<i32>,
        universe: PyUniverseMap,
    ) -> PyResult<Self> {
        let set_size = i32::try_from(universe.len())
            .map_err(|_| PyValueError::new_err("Universe is too large"))?;
        let expected_size = if symbol.arity() == 0 {
            1
        } else {
            (set_size as usize)
                .checked_pow(symbol.arity() as u32)
                .ok_or_else(|| PyValueError::new_err("Operation table size overflow"))?
        };
        if table.len() != expected_size {
            return Err(PyValueError::new_err(format!(
                "Table has {} values, expected {}",
                table.len(),
                expected_size
            )));
        }
        if table.iter().any(|&value| value < 0 || value >= set_size) {
            return Err(PyValueError::new_err(
                "Operation table contains an index outside the universe",
            ));
        }
        Ok(Self {
            symbol,
            set_size,
            evaluation_mode: AbstractOperationEvaluationMode::ValueTable(
                table.into(),
                universe,
            ),
        })
    }

    fn horner_encode(&self, args: &[i32]) -> i32 {
        let mut result = 0;
        let mut multiplier = 1;

        for &arg in args.iter().rev() {
            result += arg * multiplier;
            multiplier *= self.set_size;
        }

        result
    }

    fn generate_args_static(
        arity: i32,
        set_size: i32,
        current: &mut Vec<i32>,
        all_args: &mut Vec<Vec<i32>>,
    ) {
        if current.len() == arity as usize {
            all_args.push(current.clone());
            return;
        }
        for value in 0..set_size {
            current.push(value);
            Self::generate_args_static(arity, set_size, current, all_args);
            current.pop();
        }
    }

}