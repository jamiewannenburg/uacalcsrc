use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict, PyList};
use pyo3::wrap_pyfunction;
use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, Ordering};

use std::sync::Arc;
use std::sync::Mutex;

use uacalc_core::algebra::{Algebra, BasicAlgebra, SmallAlgebra};
use uacalc_core::binary_relation::{BasicBinaryRelation, BinaryRelation};
use uacalc_core::conlat::{BasicCongruenceLattice, CongruenceLattice as CongruenceLatticeTrait};
use uacalc_core::error::UACalcError;
use uacalc_core::operation::{Operation, OperationSymbol, TableOperation};
use uacalc_core::partition::{BasicPartition, Partition};
use uacalc_core::product::ProductAlgebra;
use uacalc_core::quotient::QuotientAlgebra;
use uacalc_core::term::evaluation::EvaluationContext;
use uacalc_core::term::variable::VariableAssignment;
use uacalc_core::term::{TermArena, TermId};

/// Python module for UACalc
#[pymodule]
fn uacalc_rust(_py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<PyAlgebra>()?;
    m.add_class::<PyProductAlgebra>()?;
    m.add_class::<PyQuotientAlgebra>()?;
    m.add_class::<PyOperation>()?;
    m.add_class::<PyPartition>()?;
    m.add_class::<PyBinaryRelation>()?;
    m.add_class::<PyCongruenceLattice>()?;
    m.add_class::<PyTerm>()?;
    m.add_class::<PyTermArena>()?;
    m.add_class::<PyProgressReporter>()?;

    m.add_function(wrap_pyfunction!(create_algebra, m)?)?;
    m.add_function(wrap_pyfunction!(create_operation, m)?)?;
    m.add_function(wrap_pyfunction!(create_operation_with_size, m)?)?;
    m.add_function(wrap_pyfunction!(create_partition, m)?)?;
    m.add_function(wrap_pyfunction!(create_partition_from_blocks, m)?)?;
    m.add_function(wrap_pyfunction!(create_binary_relation, m)?)?;
    m.add_function(wrap_pyfunction!(create_congruence_lattice, m)?)?;
    m.add_function(wrap_pyfunction!(create_term_arena, m)?)?;
    m.add_function(wrap_pyfunction!(create_progress_reporter, m)?)?;
    m.add_function(wrap_pyfunction!(parse_term, m)?)?;
    m.add_function(wrap_pyfunction!(eval_term, m)?)?;
    m.add_function(wrap_pyfunction!(rust_create_product_algebra, m)?)?;
    m.add_function(wrap_pyfunction!(rust_create_quotient_algebra, m)?)?;

    // Add custom exception classes
    m.add("UACalcError", _py.get_type_bound::<PyUACalcError>())?;
    m.add(
        "CancellationError",
        _py.get_type_bound::<PyCancellationError>(),
    )?;
    m.add(
        "OperationNotFoundError",
        _py.get_type_bound::<PyOperationNotFoundError>(),
    )?;

    Ok(())
}

// Create custom exceptions using pyo3::create_exception!
pyo3::create_exception!(uacalc_rust, PyUACalcError, pyo3::exceptions::PyException);
pyo3::create_exception!(
    uacalc_rust,
    PyCancellationError,
    pyo3::exceptions::PyException
);
pyo3::create_exception!(
    uacalc_rust,
    PyOperationNotFoundError,
    pyo3::exceptions::PyException
);

/// Map UACalcError to appropriate Python exception
fn map_uacalc_error(error: UACalcError) -> PyErr {
    match error {
        UACalcError::IndexOutOfBounds { index, size } => {
            PyErr::new::<pyo3::exceptions::PyIndexError, _>(format!(
                "Index {} out of bounds for size {}",
                index, size
            ))
        }
        UACalcError::InvalidArity { expected, actual } => {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Invalid arity: expected {}, got {}",
                expected, actual
            ))
        }
        UACalcError::OperationNotFound { symbol } => {
            PyErr::new::<PyOperationNotFoundError, _>(format!("Operation '{}' not found", symbol))
        }
        UACalcError::Cancelled { message } => PyErr::new::<PyCancellationError, _>(message),
        UACalcError::ParseError { message } => {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Parse error: {}", message))
        }
        _ => PyErr::new::<PyUACalcError, _>(error.to_string()),
    }
}

/// Python wrapper for BasicCongruenceLattice
#[pyclass]
pub struct PyCongruenceLattice {
    inner: Arc<Mutex<Option<BasicCongruenceLattice>>>,
    algebra: PyAlgebra,
    progress_callback: Arc<Mutex<Option<PyObject>>>,
    cancelled: Arc<AtomicBool>,
}

#[pymethods]
impl PyCongruenceLattice {
    #[new]
    fn new(algebra: PyAlgebra) -> Self {
        Self {
            inner: Arc::new(Mutex::new(None)),
            algebra,
            progress_callback: Arc::new(Mutex::new(None)),
            cancelled: Arc::new(AtomicBool::new(false)),
        }
    }

    fn ensure_universe_built(
        &self,
        _py: Python,
        progress_callback: Option<PyObject>,
    ) -> PyResult<()> {
        let mut inner_guard = self.inner.lock().unwrap();
        if inner_guard.is_none() {
            let mut lattice = BasicCongruenceLattice::new(Box::new(self.algebra.inner.clone()))
                .map_err(map_uacalc_error)?;

            if let Some(callback) = progress_callback {
                let cancelled = Arc::clone(&self.cancelled);
                let progress_reporter =
                    PyProgressReporter::new_with_cancellation(callback, Arc::clone(&cancelled));
                // Use catch_unwind to handle panics from the progress callback
                let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                    lattice.with_progress_callback(move |progress| {
                        // Check for cancellation first
                        if cancelled.load(Ordering::Relaxed) {
                            // We can't return an error from this closure, so we'll panic
                            // This will be caught and converted to a UACalcError::Cancelled
                            panic!("Operation cancelled by user");
                        }

                        Python::with_gil(|py| {
                            let _ = progress_reporter.report_progress(py, progress, None);
                        });
                    })
                }));

                match result {
                    Ok(lattice_result) => {
                        lattice = lattice_result.map_err(map_uacalc_error)?;
                    }
                    Err(panic_info) => {
                        // Convert panic to UACalcError::Cancelled
                        let panic_message = if let Some(s) = panic_info.downcast_ref::<&str>() {
                            s.to_string()
                        } else if let Some(s) = panic_info.downcast_ref::<String>() {
                            s.clone()
                        } else {
                            "Unknown panic".to_string()
                        };

                        if panic_message.contains("cancelled") {
                            return Err(map_uacalc_error(UACalcError::Cancelled {
                                message: "Operation cancelled by user".to_string(),
                            }));
                        } else {
                            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                                format!("Panic during lattice construction: {}", panic_message),
                            ));
                        }
                    }
                }
            }

            *inner_guard = Some(lattice);
        } else {
            // If lattice is already built and we have a progress callback, try to set it
            if let Some(callback) = progress_callback {
                if let Some(ref mut lattice) = *inner_guard {
                    let progress_reporter = PyProgressReporter::new(callback);
                    lattice
                        .set_progress_callback(move |progress| {
                            Python::with_gil(|py| {
                                let _ = progress_reporter.report_progress(py, progress, None);
                            });
                        })
                        .map_err(map_uacalc_error)?;
                }
            }
        }
        Ok(())
    }

    fn size(&self, py: Python) -> PyResult<usize> {
        self.ensure_universe_built(py, None)?;
        let inner_guard = self.inner.lock().unwrap();
        if let Some(ref lattice) = *inner_guard {
            Ok(lattice.num_congruences())
        } else {
            Ok(0) // Not built yet
        }
    }

    fn congruences(&self, py: Python) -> PyResult<Vec<PyPartition>> {
        self.ensure_universe_built(py, None)?;
        let inner_guard = self.inner.lock().unwrap();
        if let Some(ref lattice) = *inner_guard {
            let congruences = lattice.congruences_basic();
            let result = congruences
                .into_iter()
                .map(|p| PyPartition { inner: p })
                .collect();
            Ok(result)
        } else {
            Ok(Vec::new())
        }
    }

    fn principal_congruence(&self, py: Python, a: usize, b: usize) -> PyResult<PyPartition> {
        self.ensure_universe_built(py, None)?;
        let mut inner_guard = self.inner.lock().unwrap();
        if let Some(ref mut lattice) = *inner_guard {
            let congruence = lattice
                .get_principal_congruence(a, b)
                .map_err(map_uacalc_error)?;
            Ok(PyPartition {
                inner: congruence.clone(),
            })
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Lattice not built".to_string(),
            ))
        }
    }

    fn join(&self, py: Python, i: usize, j: usize) -> PyResult<PyPartition> {
        self.ensure_universe_built(py, None)?;
        let inner_guard = self.inner.lock().unwrap();
        if let Some(ref lattice) = *inner_guard {
            let result = lattice.join_by_index(i, j).map_err(map_uacalc_error)?;
            Ok(PyPartition { inner: result })
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Lattice not built".to_string(),
            ))
        }
    }

    fn meet(&self, py: Python, i: usize, j: usize) -> PyResult<PyPartition> {
        self.ensure_universe_built(py, None)?;
        let inner_guard = self.inner.lock().unwrap();
        if let Some(ref lattice) = *inner_guard {
            let result = lattice.meet_by_index(i, j).map_err(map_uacalc_error)?;
            Ok(PyPartition { inner: result })
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Lattice not built".to_string(),
            ))
        }
    }

    fn atoms(&self, py: Python) -> PyResult<Vec<PyPartition>> {
        self.ensure_universe_built(py, None)?;
        let inner_guard = self.inner.lock().unwrap();
        if let Some(ref lattice) = *inner_guard {
            let atoms = lattice.atoms_basic().map_err(map_uacalc_error)?;
            let result = atoms
                .into_iter()
                .map(|p| PyPartition { inner: p })
                .collect();
            Ok(result)
        } else {
            Ok(Vec::new())
        }
    }

    fn coatoms(&self, py: Python) -> PyResult<Vec<PyPartition>> {
        self.ensure_universe_built(py, None)?;
        let inner_guard = self.inner.lock().unwrap();
        if let Some(ref lattice) = *inner_guard {
            let coatoms = lattice.coatoms_basic().map_err(map_uacalc_error)?;
            let result = coatoms
                .into_iter()
                .map(|p| PyPartition { inner: p })
                .collect();
            Ok(result)
        } else {
            Ok(Vec::new())
        }
    }

    fn covering_relation(&self, py: Python) -> PyResult<Vec<(usize, usize)>> {
        self.ensure_universe_built(py, None)?;
        let inner_guard = self.inner.lock().unwrap();
        if let Some(ref lattice) = *inner_guard {
            lattice.covering_relation().map_err(map_uacalc_error)
        } else {
            Ok(Vec::new())
        }
    }

    fn with_progress_callback(&self, py: Python, callback: PyObject) -> PyResult<()> {
        // Store the callback for future use
        {
            let mut callback_guard = self.progress_callback.lock().unwrap();
            *callback_guard = Some(callback.clone_ref(py));
        }

        // Try to attach the callback to the existing lattice if it's already built
        self.ensure_universe_built(py, Some(callback))
    }

    fn set_cancelled(&self) {
        self.cancelled.store(true, Ordering::Relaxed);
    }

    fn is_cancelled(&self) -> bool {
        self.cancelled.load(Ordering::Relaxed)
    }
}

/// Python wrapper for Term
#[pyclass]
#[derive(Clone)]
pub struct PyTerm {
    id: TermId,
    arena: PyTermArena,
}

#[pymethods]
impl PyTerm {
    fn is_variable(&self, _py: Python) -> PyResult<bool> {
        let arena_guard = self.arena.inner.lock().unwrap();
        let term = arena_guard.get_term(self.id).map_err(map_uacalc_error)?;
        Ok(term.is_variable())
    }

    fn is_operation(&self, _py: Python) -> PyResult<bool> {
        let arena_guard = self.arena.inner.lock().unwrap();
        let term = arena_guard.get_term(self.id).map_err(map_uacalc_error)?;
        Ok(term.is_operation())
    }

    fn arity(&self, _py: Python) -> PyResult<usize> {
        let arena_guard = self.arena.inner.lock().unwrap();
        let term = arena_guard.get_term(self.id).map_err(map_uacalc_error)?;
        Ok(term.arity())
    }

    fn depth(&self, _py: Python) -> PyResult<usize> {
        let arena_guard = self.arena.inner.lock().unwrap();
        let term = arena_guard.get_term(self.id).map_err(map_uacalc_error)?;
        term.depth(&arena_guard).map_err(map_uacalc_error)
    }

    fn variables(&self, _py: Python) -> PyResult<Vec<u8>> {
        let arena_guard = self.arena.inner.lock().unwrap();
        let term = arena_guard.get_term(self.id).map_err(map_uacalc_error)?;
        term.variables(&arena_guard).map_err(map_uacalc_error)
    }

    fn to_string(&self, _py: Python) -> PyResult<String> {
        let arena_guard = self.arena.inner.lock().unwrap();
        let term = arena_guard.get_term(self.id).map_err(map_uacalc_error)?;
        term.to_string(&arena_guard).map_err(map_uacalc_error)
    }
}

/// Python wrapper for TermArena
#[pyclass]
#[derive(Clone)]
pub struct PyTermArena {
    inner: Arc<Mutex<TermArena>>,
}

#[pymethods]
impl PyTermArena {
    #[new]
    fn new() -> Self {
        Self {
            inner: Arc::new(Mutex::new(TermArena::new())),
        }
    }

    fn make_variable(&self, index: u8) -> PyResult<PyTerm> {
        let mut arena_guard = self.inner.lock().unwrap();
        let id = arena_guard.make_variable(index);
        Ok(PyTerm {
            id,
            arena: PyTermArena {
                inner: Arc::clone(&self.inner),
            },
        })
    }

    fn make_term(&self, symbol: String, children: Vec<PyTerm>) -> PyResult<PyTerm> {
        let mut arena_guard = self.inner.lock().unwrap();
        let child_ids: Vec<TermId> = children.iter().map(|t| t.id).collect();
        // Create a simple operation symbol
        let symbol_obj = OperationSymbol::new(symbol, child_ids.len());
        let id = arena_guard.make_term(&symbol_obj, &child_ids);
        Ok(PyTerm {
            id,
            arena: PyTermArena {
                inner: Arc::clone(&self.inner),
            },
        })
    }

    fn num_terms(&self) -> usize {
        let arena_guard = self.inner.lock().unwrap();
        arena_guard.num_terms()
    }

    fn num_symbols(&self) -> usize {
        let arena_guard = self.inner.lock().unwrap();
        arena_guard.num_symbols()
    }

    fn parse_term(&self, expr: String) -> PyResult<PyTerm> {
        let expr = expr.trim();

        if expr.is_empty() {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Empty expression".to_string(),
            ));
        }

        // Adjust parentheses (add missing closing parentheses)
        let adjusted_expr = self.adjust_parentheses(&expr);

        // Split on first '(' to separate symbol from arguments
        if let Some(open_paren_pos) = adjusted_expr.find('(') {
            let symbol = adjusted_expr[..open_paren_pos].trim();

            // Validate symbol name
            if !self.is_valid_symbol(&symbol) {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "Invalid operation symbol: {}",
                    symbol
                )));
            }

            // Extract arguments string
            let args_start = open_paren_pos + 1;
            let args_end = adjusted_expr.len() - 1; // Remove closing parenthesis
            let args_string = adjusted_expr[args_start..args_end].trim();

            // Parse arguments
            let arg_strings = self.parse_argument_list(&args_string)?;
            let mut child_terms = Vec::new();

            for arg_str in arg_strings {
                let child_term = self.parse_term(arg_str.to_string())?;
                child_terms.push(child_term);
            }

            // Create operation term
            return self.make_term(symbol.to_string(), child_terms);
        } else {
            // No parentheses - could be variable or constant
            // Handle variable terms like "x0", "x1", etc.
            if expr.starts_with('x') {
                if let Ok(index) = expr[1..].parse::<u8>() {
                    return self.make_variable(index);
                }
            }

            // If it's a valid symbol but not a variable, treat as constant
            if self.is_valid_symbol(&expr) {
                // Create a constant term
                let mut arena_guard = self.inner.lock().unwrap();
                let symbol = OperationSymbol::new(expr.to_string(), 0);
                let id = arena_guard.make_term(&symbol, &[]);
                return Ok(PyTerm {
                    id,
                    arena: PyTermArena {
                        inner: Arc::clone(&self.inner),
                    },
                });
            } else {
                // Invalid symbol - treat as variable 0
                return self.make_variable(0);
            }
        }
    }

    fn adjust_parentheses(&self, expr: &str) -> String {
        let mut depth = 0;
        for ch in expr.chars() {
            match ch {
                '(' => depth += 1,
                ')' => depth -= 1,
                _ => {}
            }
        }

        let mut result = expr.to_string();
        if depth > 0 {
            // Add missing closing parentheses
            for _ in 0..depth {
                result.push(')');
            }
        } else if depth > 0 {
            // Remove excess closing parentheses (depth is usize, so we handle this differently)
            // This case shouldn't occur with proper parenthesis counting
        }
        result
    }

    fn parse_argument_list(&self, args_string: &str) -> PyResult<Vec<String>> {
        if args_string.is_empty() {
            return Ok(Vec::new());
        }

        let mut arguments = Vec::new();
        let mut start = 0;
        let mut depth = 0;
        let mut i = 0;

        while i < args_string.len() {
            let ch = args_string.chars().nth(i).unwrap();
            match ch {
                '(' => depth += 1,
                ')' => depth -= 1,
                ',' => {
                    if depth == 0 {
                        let arg = args_string[start..i].trim();
                        if !arg.is_empty() {
                            arguments.push(arg.to_string());
                        }
                        start = i + 1;
                    }
                }
                _ => {}
            }
            i += 1;
        }

        // Add the last argument
        let last_arg = args_string[start..].trim();
        if !last_arg.is_empty() {
            arguments.push(last_arg.to_string());
        }

        Ok(arguments)
    }

    fn is_valid_symbol(&self, symbol: &str) -> bool {
        if symbol.is_empty() {
            return false;
        }

        // First character must be a letter
        if !symbol.chars().next().unwrap().is_alphabetic() {
            return false;
        }

        // Check for invalid characters
        for ch in symbol.chars() {
            if ch.is_whitespace() || ch == ',' || ch == '(' || ch == ')' {
                return false;
            }
        }

        true
    }

    fn is_valid_variable(&self, var: &str) -> bool {
        if var.is_empty() {
            return false;
        }

        // First character must be a letter
        if !var.chars().next().unwrap().is_alphabetic() {
            return false;
        }

        // Check for invalid characters
        for ch in var.chars() {
            if ch.is_whitespace() || ch == ',' || ch == '(' || ch == ')' {
                return false;
            }
        }

        true
    }
}

/// Python wrapper for ProgressReporter
#[pyclass]
pub struct PyProgressReporter {
    callback: Option<PyObject>,
    cancelled: Arc<AtomicBool>,
    current_progress: Arc<Mutex<f64>>,
}

#[pymethods]
impl PyProgressReporter {
    #[new]
    fn new(callback: PyObject) -> Self {
        Self {
            callback: Some(callback),
            cancelled: Arc::new(AtomicBool::new(false)),
            current_progress: Arc::new(Mutex::new(0.0)),
        }
    }

    #[staticmethod]
    fn new_silent() -> Self {
        Self {
            callback: None,
            cancelled: Arc::new(AtomicBool::new(false)),
            current_progress: Arc::new(Mutex::new(0.0)),
        }
    }

    fn report_progress(&self, py: Python, progress: f64, message: Option<String>) -> PyResult<()> {
        *self.current_progress.lock().unwrap() = progress;

        if let Some(ref callback) = self.callback {
            let args = if let Some(msg) = message {
                (progress, msg)
            } else {
                (progress, "".to_string())
            };
            callback.call1(py, args)?;
        }
        Ok(())
    }

    fn should_cancel(&self) -> bool {
        self.cancelled.load(Ordering::Relaxed)
    }

    fn set_cancelled(&self) {
        self.cancelled.store(true, Ordering::Relaxed);
    }

    fn current_progress(&self) -> f64 {
        *self.current_progress.lock().unwrap()
    }
}

impl PyProgressReporter {
    fn new_with_cancellation(callback: PyObject, cancelled: Arc<AtomicBool>) -> Self {
        Self {
            callback: Some(callback),
            cancelled,
            current_progress: Arc::new(Mutex::new(0.0)),
        }
    }
}

/// Python wrapper for BasicAlgebra
#[pyclass]
#[derive(Clone)]
pub struct PyAlgebra {
    inner: BasicAlgebra,
}

/// Python wrapper for ProductAlgebra
#[pyclass]
pub struct PyProductAlgebra {
    inner: ProductAlgebra,
}

/// Python wrapper for QuotientAlgebra
#[pyclass]
#[derive(Clone)]
pub struct PyQuotientAlgebra {
    inner: QuotientAlgebra,
}

#[pymethods]
impl PyProductAlgebra {
    #[getter]
    fn name(&self) -> String {
        self.inner.name().to_string()
    }

    #[getter]
    fn cardinality(&self) -> usize {
        self.inner.cardinality()
    }

    fn operations(&self) -> Vec<PyOperation> {
        self.inner
            .operations()
            .iter()
            .map(|op| PyOperation {
                inner: Arc::clone(op),
            })
            .collect()
    }

    fn operation_by_symbol(&self, symbol: &str) -> PyResult<PyOperation> {
        let op = self
            .inner
            .operation_arc_by_symbol(symbol)
            .map_err(map_uacalc_error)?;
        Ok(PyOperation { inner: op })
    }

    /// Get the k-th factor algebra (returns PyAlgebra for compatibility)
    fn projection(&self, k: usize) -> PyResult<PyAlgebra> {
        let factor = self.inner.projection(k).map_err(map_uacalc_error)?;
        let factor_guard = factor.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Failed to lock factor algebra".to_string(),
            )
        })?;

        // Convert the SmallAlgebra to BasicAlgebra for Python compatibility
        // This is a simplified conversion that preserves basic functionality
        let basic = BasicAlgebra::with_cardinality(
            factor_guard.name().to_string(),
            factor_guard.cardinality(),
        )
        .map_err(map_uacalc_error)?;

        Ok(PyAlgebra { inner: basic })
    }

    /// Extract the k-th coordinate from a product element
    fn coordinate_projection(&self, element: usize, k: usize) -> PyResult<usize> {
        self.inner
            .coordinate_projection(element, k)
            .map_err(map_uacalc_error)
    }

    /// Create a product element from coordinates
    fn coordinate_embedding(&self, coords: Vec<usize>) -> PyResult<usize> {
        self.inner
            .coordinate_embedding(&coords)
            .map_err(map_uacalc_error)
    }

    /// Get the projection kernel for the k-th factor
    fn projection_kernel(&self, k: usize) -> PyResult<PyPartition> {
        let kernel = self.inner.projection_kernel(k).map_err(map_uacalc_error)?;
        Ok(PyPartition { inner: kernel })
    }

    /// Decode a product element into its coordinates
    fn decode_coords(&self, element: usize) -> Vec<usize> {
        self.inner.decode_coords(element)
    }

    /// Encode coordinates back to a product element
    fn encode_coords(&self, coords: Vec<usize>) -> PyResult<usize> {
        self.inner.encode_coords(&coords).map_err(map_uacalc_error)
    }

    /// Get the factor sizes
    #[getter]
    fn factor_sizes(&self) -> Vec<usize> {
        self.inner
            .factors()
            .iter()
            .map(|factor| factor.lock().unwrap().cardinality())
            .collect()
    }

    /// Get the number of factors
    #[getter]
    fn num_factors(&self) -> usize {
        self.inner.factors().len()
    }
}

#[pymethods]
impl PyQuotientAlgebra {
    #[getter]
    fn name(&self) -> String {
        self.inner.name().to_string()
    }

    #[getter]
    fn cardinality(&self) -> usize {
        self.inner.cardinality()
    }

    fn operations(&self) -> Vec<PyOperation> {
        self.inner
            .operations()
            .iter()
            .map(|op| PyOperation {
                inner: Arc::clone(op),
            })
            .collect()
    }

    fn operation_by_symbol(&self, symbol: &str) -> PyResult<PyOperation> {
        let op = self
            .inner
            .operation_arc_by_symbol(symbol)
            .map_err(map_uacalc_error)?;
        Ok(PyOperation { inner: op })
    }

    /// Get the super algebra (returns PyAlgebra for compatibility)
    fn super_algebra(&self) -> PyResult<PyAlgebra> {
        let super_alg = self.inner.super_algebra();
        let super_guard = super_alg.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Failed to lock super algebra".to_string(),
            )
        })?;

        // Convert to BasicAlgebra for Python compatibility
        let basic = BasicAlgebra::with_cardinality(
            super_guard.name().to_string(),
            super_guard.cardinality(),
        )
        .map_err(map_uacalc_error)?;

        Ok(PyAlgebra { inner: basic })
    }

    /// Get the congruence relation
    fn congruence(&self) -> PyPartition {
        PyPartition {
            inner: self.inner.congruence().clone(),
        }
    }

    /// Canonical homomorphism: map parent algebra element to quotient index
    fn canonical_homomorphism(&self, element: usize) -> PyResult<usize> {
        self.inner
            .canonical_homomorphism(element)
            .map_err(map_uacalc_error)
    }

    /// Get the representatives of the congruence blocks
    fn representatives(&self) -> Vec<usize> {
        self.inner.congruence().representatives()
    }

    /// Get the block containing the element at the given index
    fn block_of_index(&self, index: usize) -> PyResult<Vec<usize>> {
        let representatives = self.inner.congruence().representatives();

        if index >= representatives.len() {
            return Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(format!(
                "Index {} out of bounds for {} representatives",
                index,
                representatives.len()
            )));
        }

        let representative = representatives[index];
        self.inner
            .congruence()
            .block(representative)
            .map_err(map_uacalc_error)
    }

    // Backward compatibility methods to match PyAlgebra interface

    #[getter]
    fn universe(&self) -> Vec<usize> {
        self.inner.universe().to_vec()
    }

    fn is_finite(&self) -> bool {
        true // Quotient algebras are always finite
    }

    fn max_arity(&self) -> usize {
        self.inner.max_arity()
    }

    fn operation(&self, index: usize) -> PyResult<PyOperation> {
        let op = self.inner.operation_arc(index).map_err(map_uacalc_error)?;
        Ok(PyOperation { inner: op })
    }

    fn is_idempotent(&self, op_index: usize) -> PyResult<bool> {
        let op = self
            .inner
            .operation_arc(op_index)
            .map_err(map_uacalc_error)?;
        let op_guard = op.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to lock operation".to_string())
        })?;
        op_guard
            .is_idempotent_on_set(self.inner.cardinality())
            .map_err(map_uacalc_error)
    }

    fn is_associative(&self, op_index: usize) -> PyResult<bool> {
        let op = self
            .inner
            .operation_arc(op_index)
            .map_err(map_uacalc_error)?;
        let op_guard = op.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to lock operation".to_string())
        })?;
        if op_guard.arity() == 2 {
            op_guard
                .is_associative_on_set(self.inner.cardinality())
                .map_err(map_uacalc_error)
        } else {
            Ok(false)
        }
    }

    fn is_commutative(&self, op_index: usize) -> PyResult<bool> {
        let op = self
            .inner
            .operation_arc(op_index)
            .map_err(map_uacalc_error)?;
        let op_guard = op.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to lock operation".to_string())
        })?;
        if op_guard.arity() == 2 {
            op_guard
                .is_commutative_on_set(self.inner.cardinality())
                .map_err(map_uacalc_error)
        } else {
            Ok(false)
        }
    }

    fn subalgebra(&self, generators: Vec<usize>) -> PyResult<PyAlgebra> {
        let sub = self
            .inner
            .subalgebra(&generators)
            .map_err(map_uacalc_error)?;
        Ok(PyAlgebra { inner: sub })
    }
}

#[pymethods]
impl PyAlgebra {
    #[new]
    fn new(name: String, universe: Vec<usize>) -> PyResult<Self> {
        Ok(Self {
            inner: BasicAlgebra::new(name, universe).map_err(map_uacalc_error)?,
        })
    }

    #[pyo3(name = "add_operation")]
    fn py_add_operation(&mut self, symbol: String, operation: &PyOperation) -> PyResult<()> {
        self.inner
            .add_operation(symbol, Arc::clone(&operation.inner))
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    #[getter]
    fn name(&self) -> String {
        self.inner.name().to_string()
    }

    #[getter]
    fn universe(&self) -> Vec<usize> {
        self.inner.universe().to_vec()
    }

    #[getter]
    fn cardinality(&self) -> usize {
        self.inner.cardinality()
    }

    fn operations(&self) -> Vec<PyOperation> {
        self.inner
            .operations()
            .iter()
            .map(|op| PyOperation {
                inner: Arc::clone(op),
            })
            .collect()
    }

    fn operation(&self, index: usize) -> PyResult<PyOperation> {
        let op = self.inner.operation_arc(index).map_err(map_uacalc_error)?;
        Ok(PyOperation { inner: op })
    }

    fn operation_by_symbol(&self, symbol: &str) -> PyResult<PyOperation> {
        let op = self
            .inner
            .operation_arc_by_symbol(symbol)
            .map_err(map_uacalc_error)?;
        Ok(PyOperation { inner: op })
    }

    fn is_finite(&self) -> bool {
        self.inner.is_finite()
    }

    fn max_arity(&self) -> usize {
        self.inner.max_arity()
    }

    fn is_idempotent(&self, op_index: usize) -> PyResult<bool> {
        let op = self
            .inner
            .operation_arc(op_index)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        let op_guard = op.lock().unwrap();
        op_guard
            .is_idempotent_on_set(self.inner.cardinality())
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn is_associative(&self, op_index: usize) -> PyResult<bool> {
        let op = self
            .inner
            .operation_arc(op_index)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        let op_guard = op.lock().unwrap();
        if op_guard.arity() == 2 {
            op_guard
                .is_associative_on_set(self.inner.cardinality())
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
        } else {
            Ok(false)
        }
    }

    fn is_commutative(&self, op_index: usize) -> PyResult<bool> {
        let op = self
            .inner
            .operation_arc(op_index)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        let op_guard = op.lock().unwrap();
        if op_guard.arity() == 2 {
            op_guard
                .is_commutative_on_set(self.inner.cardinality())
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
        } else {
            Ok(false)
        }
    }

    fn subalgebra(&self, generators: Vec<usize>) -> PyResult<PyAlgebra> {
        let sub = self
            .inner
            .subalgebra(&generators)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyAlgebra { inner: sub })
    }
}

/// Python wrapper for Operation
#[pyclass]
#[derive(Clone)]
pub struct PyOperation {
    inner: Arc<Mutex<dyn Operation>>,
}

#[pymethods]
impl PyOperation {
    fn arity(&self) -> usize {
        let op_guard = self.inner.lock().unwrap();
        op_guard.arity()
    }

    #[getter]
    fn symbol(&self) -> PyResult<String> {
        let op_guard = self.inner.lock().unwrap();
        Ok(op_guard.symbol().name.clone())
    }

    fn value(&self, args: Vec<usize>) -> PyResult<usize> {
        let op_guard = self.inner.lock().unwrap();
        op_guard
            .value(&args)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn operation_type(&self) -> String {
        let op_guard = self.inner.lock().unwrap();
        match op_guard.operation_type() {
            uacalc_core::operation::OperationType::Constant => "constant".to_string(),
            uacalc_core::operation::OperationType::Unary => "unary".to_string(),
            uacalc_core::operation::OperationType::Binary => "binary".to_string(),
            uacalc_core::operation::OperationType::Ternary => "ternary".to_string(),
            uacalc_core::operation::OperationType::Nary(n) => format!("nary({})", n),
        }
    }
}

/// Python wrapper for BasicPartition
#[pyclass]
pub struct PyPartition {
    inner: BasicPartition,
}

#[pymethods]
impl PyPartition {
    #[new]
    fn new(size: usize) -> Self {
        Self {
            inner: BasicPartition::new(size),
        }
    }

    #[getter]
    fn size(&self) -> usize {
        self.inner.size()
    }

    #[getter]
    fn num_blocks(&self) -> usize {
        self.inner.num_blocks()
    }

    fn block(&self, element: usize) -> PyResult<Vec<usize>> {
        self.inner
            .block(element)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn representative(&self, element: usize) -> PyResult<usize> {
        self.inner
            .representative(element)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn same_block(&self, a: usize, b: usize) -> PyResult<bool> {
        self.inner
            .same_block(a, b)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn blocks(&self) -> PyResult<Vec<Vec<usize>>> {
        self.inner
            .blocks()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn union(&mut self, x: usize, y: usize) -> PyResult<()> {
        self.inner
            .union(x, y)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn join(&self, other: &PyPartition) -> PyResult<PyPartition> {
        let result = self
            .inner
            .join(&other.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyPartition { inner: result })
    }

    fn meet(&self, other: &PyPartition) -> PyResult<PyPartition> {
        let result = self
            .inner
            .meet(&other.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyPartition { inner: result })
    }

    fn is_finer_than(&self, other: &PyPartition) -> PyResult<bool> {
        self.inner
            .is_finer_than(&other.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn is_coarser_than(&self, other: &PyPartition) -> PyResult<bool> {
        self.inner
            .is_coarser_than(&other.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    /// Create a discrete partition (identity relation) where each element is in its own block
    #[staticmethod]
    fn discrete(size: usize) -> PyResult<PyPartition> {
        Ok(PyPartition {
            inner: BasicPartition::new(size),
        })
    }
}

/// Python wrapper for BasicBinaryRelation
#[pyclass]
pub struct PyBinaryRelation {
    inner: BasicBinaryRelation,
}

#[pymethods]
impl PyBinaryRelation {
    #[new]
    fn new(size: usize) -> Self {
        Self {
            inner: BasicBinaryRelation::new(size),
        }
    }

    #[getter]
    fn size(&self) -> usize {
        self.inner.size()
    }

    fn contains(&self, a: usize, b: usize) -> PyResult<bool> {
        self.inner
            .contains(a, b)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn add(&mut self, a: usize, b: usize) -> PyResult<()> {
        self.inner
            .add(a, b)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn remove(&mut self, a: usize, b: usize) -> PyResult<()> {
        self.inner
            .remove(a, b)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn pairs(&self) -> Vec<(usize, usize)> {
        self.inner.pairs()
    }

    fn reflexive_closure(&self) -> PyResult<PyBinaryRelation> {
        let closure = self
            .inner
            .reflexive_closure_owned()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyBinaryRelation { inner: closure })
    }

    fn symmetric_closure(&self) -> PyResult<PyBinaryRelation> {
        let closure = self
            .inner
            .symmetric_closure_owned()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyBinaryRelation { inner: closure })
    }

    fn transitive_closure(&self) -> PyResult<PyBinaryRelation> {
        let closure = self
            .inner
            .transitive_closure_owned()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyBinaryRelation { inner: closure })
    }

    fn equivalence_closure(&self) -> PyResult<PyBinaryRelation> {
        let closure = self
            .inner
            .equivalence_closure_owned()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyBinaryRelation { inner: closure })
    }

    fn is_reflexive(&self) -> PyResult<bool> {
        self.inner
            .is_reflexive()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn is_symmetric(&self) -> PyResult<bool> {
        self.inner
            .is_symmetric()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn is_transitive(&self) -> PyResult<bool> {
        self.inner
            .is_transitive()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn is_equivalence(&self) -> PyResult<bool> {
        self.inner
            .is_equivalence()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
}

/// Helper function to create an algebra
#[pyfunction]
fn create_algebra(name: String, universe: Vec<usize>) -> PyResult<PyAlgebra> {
    Ok(PyAlgebra::new(name, universe)?)
}

/// Helper function to create an operation
#[pyfunction]
fn create_operation(name: String, arity: usize, table: PyObject) -> PyResult<PyOperation> {
    let symbol = uacalc_core::operation::OperationSymbol::new(name, arity);

    // Convert PyObject to Vec<Vec<usize>> based on the input type
    let table_vec: Vec<Vec<usize>> = Python::with_gil(|py| {
        if let Ok(list) = table.extract::<Vec<usize>>(py) {
            if arity == 0 {
                // Constant operation: expect [[value]]
                Ok(vec![vec![list[0]]])
            } else if arity == 1 {
                // Unary operation: expect [value1, value2, ...]
                Ok(list.into_iter().map(|val| vec![val]).collect())
            } else if arity == 2 {
                // Binary operation: handle NxN matrix format
                let _n = list.len();
                Ok(list.into_iter().map(|val| vec![val]).collect())
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "Single list format only supported for unary operations".to_string(),
                ))
            }
        } else if let Ok(nested_list) = table.extract::<Vec<Vec<usize>>>(py) {
            // Nested list format
            Ok(nested_list)
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Table must be a list of integers or list of lists of integers".to_string(),
            ))
        }
    })?;

    // Normalize table format to [args..., result]
    let normalized_table = if arity == 0 {
        // Constant operation: expect [[value]]
        if table_vec.len() == 1 && table_vec[0].len() == 1 {
            table_vec
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Constant operation should have table [[value]]".to_string(),
            ));
        }
    } else if arity == 1 {
        // Unary operation: handle both [value] and [input, value] formats
        if table_vec.len() > 0 && table_vec[0].len() == 1 {
            // Transform [value] format to [input, value]
            let mut normalized = Vec::with_capacity(table_vec.len());
            for (i, row) in table_vec.iter().enumerate() {
                normalized.push(vec![i, row[0]]);
            }
            normalized
        } else {
            // Already in [input, value] format
            table_vec
        }
    } else if arity == 2 {
        // Binary operation: handle NxN matrix format
        let n = table_vec.len();
        if n > 0 && table_vec[0].len() == n {
            // Transform NxN matrix to [i, j, result] format
            let mut normalized = Vec::with_capacity(n * n);
            for i in 0..n {
                for j in 0..n {
                    normalized.push(vec![i, j, table_vec[i][j]]);
                }
            }
            normalized
        } else {
            // Already in [i, j, result] format
            table_vec
        }
    } else {
        // Higher arity: expect [args..., result] format
        table_vec
    };

    // Determine the universe size from the table
    let universe_size = if arity == 0 {
        // For constants, infer universe size from the constant value
        let constant_value = normalized_table[0][0];
        constant_value + 1
    } else if arity == 1 {
        normalized_table.len()
    } else if arity == 2 {
        // For binary operations, determine size from the table
        let max_element = normalized_table
            .iter()
            .flat_map(|row| row.iter())
            .max()
            .copied()
            .unwrap_or(0);
        max_element + 1
    } else {
        // For higher arity, determine size from the table
        let max_element = normalized_table
            .iter()
            .flat_map(|row| row.iter())
            .max()
            .copied()
            .unwrap_or(0);
        max_element + 1
    };

    let operation = TableOperation::new(symbol, normalized_table, universe_size)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
    Ok(PyOperation {
        inner: Arc::new(Mutex::new(operation)),
    })
}

/// Helper function to create an operation with explicit universe size
#[pyfunction]
fn create_operation_with_size(
    name: String,
    arity: usize,
    table: PyObject,
    universe_size: usize,
) -> PyResult<PyOperation> {
    let symbol = uacalc_core::operation::OperationSymbol::new(name, arity);

    // Convert PyObject to Vec<Vec<usize>> based on the input type
    let table_vec: Vec<Vec<usize>> = Python::with_gil(|py| {
        if let Ok(list) = table.extract::<Vec<usize>>(py) {
            if arity == 0 {
                // Constant operation: expect [[value]]
                Ok(vec![vec![list[0]]])
            } else if arity == 1 {
                // Unary operation: expect [value1, value2, ...]
                Ok(list.into_iter().map(|val| vec![val]).collect())
            } else if arity == 2 {
                // Binary operation: handle NxN matrix format
                let _n = list.len();
                Ok(list.into_iter().map(|val| vec![val]).collect())
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "Single list format only supported for unary operations".to_string(),
                ))
            }
        } else if let Ok(nested_list) = table.extract::<Vec<Vec<usize>>>(py) {
            // Nested list format
            Ok(nested_list)
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Table must be a list of integers or list of lists of integers".to_string(),
            ))
        }
    })?;

    // Normalize table format to [args..., result]
    let normalized_table = if arity == 0 {
        // Constant operation: expect [[value]]
        if table_vec.len() == 1 && table_vec[0].len() == 1 {
            table_vec
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Constant operation should have table [[value]]".to_string(),
            ));
        }
    } else if arity == 1 {
        // Unary operation: handle both [value] and [input, value] formats
        if table_vec.len() > 0 && table_vec[0].len() == 1 {
            // Transform [value] format to [input, value]
            let mut normalized = Vec::with_capacity(table_vec.len());
            for (i, row) in table_vec.iter().enumerate() {
                normalized.push(vec![i, row[0]]);
            }
            normalized
        } else {
            // Already in [input, value] format
            table_vec
        }
    } else if arity == 2 {
        // Binary operation: handle NxN matrix format
        let n = table_vec.len();
        if n > 0 && table_vec[0].len() == n {
            // Transform NxN matrix to [i, j, result] format
            let mut normalized = Vec::with_capacity(n * n);
            for i in 0..n {
                for j in 0..n {
                    normalized.push(vec![i, j, table_vec[i][j]]);
                }
            }
            normalized
        } else {
            // Already in [i, j, result] format
            table_vec
        }
    } else {
        // Higher arity: expect [args..., result] format
        table_vec
    };

    // Use the provided universe size instead of inferring it
    let operation = TableOperation::new(symbol, normalized_table, universe_size)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
    Ok(PyOperation {
        inner: Arc::new(Mutex::new(operation)),
    })
}

/// Helper function to create a partition
#[pyfunction]
fn create_partition(size: usize) -> PyResult<PyPartition> {
    Ok(PyPartition::new(size))
}

/// Helper function to create a partition from blocks
#[pyfunction]
fn create_partition_from_blocks(size: usize, blocks: Vec<Vec<usize>>) -> PyResult<PyPartition> {
    let partition = BasicPartition::from_blocks(size, blocks)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
    Ok(PyPartition { inner: partition })
}

/// Helper function to create a binary relation
#[pyfunction]
fn create_binary_relation(size: usize) -> PyResult<PyBinaryRelation> {
    Ok(PyBinaryRelation::new(size))
}

/// Helper function to create a congruence lattice
#[pyfunction]
fn create_congruence_lattice(algebra: &Bound<PyAny>) -> PyResult<PyCongruenceLattice> {
    // Try to extract as PyAlgebra first, then PyQuotientAlgebra
    if let Ok(py_algebra) = algebra.extract::<PyAlgebra>() {
        Ok(PyCongruenceLattice::new(py_algebra))
    } else if let Ok(py_quotient) = algebra.extract::<PyQuotientAlgebra>() {
        // Convert PyQuotientAlgebra to PyAlgebra for congruence lattice computation
        let basic = BasicAlgebra::with_cardinality(
            py_quotient.inner.name().to_string(),
            py_quotient.inner.cardinality(),
        )
        .map_err(map_uacalc_error)?;

        let py_algebra = PyAlgebra { inner: basic };
        Ok(PyCongruenceLattice::new(py_algebra))
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "Expected PyAlgebra or PyQuotientAlgebra".to_string(),
        ))
    }
}

/// Helper function to create a term arena
#[pyfunction]
fn create_term_arena() -> PyResult<PyTermArena> {
    Ok(PyTermArena::new())
}

/// Helper function to create a progress reporter
#[pyfunction]
fn create_progress_reporter(callback: PyObject) -> PyResult<PyProgressReporter> {
    Ok(PyProgressReporter::new(callback))
}

/// Helper function to parse a term
#[pyfunction]
fn parse_term(arena: &PyTermArena, expr: String) -> PyResult<PyTerm> {
    arena.parse_term(expr)
}

/// Helper function to evaluate a term
#[pyfunction]
fn eval_term(term: &PyTerm, algebra: &PyAlgebra, assignment: &Bound<PyDict>) -> PyResult<usize> {
    let mut assignment_map = HashMap::new();
    for (key, value) in assignment.iter() {
        if let Ok(key_u8) = key.extract::<u8>() {
            assignment_map.insert(key_u8, value.extract::<usize>()?);
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Assignment keys must be u8 integers".to_string(),
            ));
        }
    }

    let mut var_assignment = VariableAssignment::new();
    for (var, val) in assignment_map {
        var_assignment.assign(var, val);
    }

    let mut context = EvaluationContext::new(&algebra.inner, &var_assignment);
    let result = context
        .eval_term(term.id, &term.arena.inner.lock().unwrap())
        .map_err(map_uacalc_error)?;
    Ok(result)
}

/// Helper function to create a product algebra
#[pyfunction]
fn rust_create_product_algebra(name: &str, factors: &Bound<PyList>) -> PyResult<PyProductAlgebra> {
    // Extract Rust algebra instances from PyAlgebra wrappers
    let mut rust_factors = Vec::new();
    for (_i, factor) in factors.iter().enumerate() {
        let py_algebra: PyRef<PyAlgebra> = factor.extract()?;

        // Convert BasicAlgebra to Arc<Mutex<dyn SmallAlgebra>>
        let small_algebra: Arc<Mutex<dyn SmallAlgebra>> =
            Arc::new(Mutex::new(py_algebra.inner.clone()));
        rust_factors.push(small_algebra);
    }

    // Validate the factors list is non-empty
    if rust_factors.is_empty() {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Product algebra must have at least one factor".to_string(),
        ));
    }

    // Calculate total cardinality to estimate computation time
    let mut total_cardinality: usize = 1;
    for factor in &rust_factors {
        let factor_guard = factor.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Failed to lock factor algebra".to_string(),
            )
        })?;
        let size = factor_guard.cardinality();
        total_cardinality = total_cardinality.checked_mul(size).ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>("Cardinality overflow".to_string())
        })?;
    }

    // Create product algebra
    let product_algebra =
        ProductAlgebra::new(name.to_string(), rust_factors).map_err(map_uacalc_error)?;

    // Return PyProductAlgebra directly, preserving ProductAlgebra-specific methods
    Ok(PyProductAlgebra {
        inner: product_algebra,
    })
}

/// Helper function to create a quotient algebra
#[pyfunction]
#[pyo3(signature = (name, super_algebra, congruence, validate = false))]
fn rust_create_quotient_algebra(
    name: &str,
    super_algebra: &PyAlgebra,
    congruence: &PyPartition,
    validate: bool,
) -> PyResult<PyQuotientAlgebra> {
    // Validate inputs are non-null and valid
    if name.is_empty() {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Quotient algebra name cannot be empty".to_string(),
        ));
    }

    // Extract Rust algebra instance from PyAlgebra wrapper
    let rust_super_algebra: Arc<Mutex<dyn SmallAlgebra>> =
        Arc::new(Mutex::new(super_algebra.inner.clone()));

    // Extract BasicPartition from PyPartition
    let rust_congruence = congruence.inner.clone();

    // Create quotient algebra with optional validation
    let quotient_algebra = if validate {
        QuotientAlgebra::new_with_validation(
            name.to_string(),
            rust_super_algebra,
            rust_congruence,
            true,
        )
    } else {
        QuotientAlgebra::new(name.to_string(), rust_super_algebra, rust_congruence)
    }
    .map_err(map_uacalc_error)?;

    // Return PyQuotientAlgebra directly, preserving QuotientAlgebra-specific methods
    Ok(PyQuotientAlgebra {
        inner: quotient_algebra,
    })
}
