use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::wrap_pyfunction;
use std::any::Any;
use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::sync::Mutex;
use uacalc_core::algebra::{Algebra, BasicAlgebra, SmallAlgebra};
use uacalc_core::binary_relation::{BasicBinaryRelation, BinaryRelation};
use uacalc_core::conlat::{BasicCongruenceLattice, CongruenceLattice as CongruenceLatticeTrait};
use uacalc_core::error::UACalcError;
use uacalc_core::operation::{FunctionOperation, Operation, OperationSymbol, TableOperation};
use uacalc_core::partition::{BasicPartition, Partition};
use uacalc_core::term::evaluation::EvaluationContext;
use uacalc_core::term::variable::VariableAssignment;
use uacalc_core::term::{Term, TermArena, TermId};

/// Python module for UACalc
#[pymodule]
fn uacalc_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyAlgebra>()?;
    m.add_class::<PyOperation>()?;
    m.add_class::<PyPartition>()?;
    m.add_class::<PyBinaryRelation>()?;
    m.add_class::<PyCongruenceLattice>()?;
    m.add_class::<PyTerm>()?;
    m.add_class::<PyTermArena>()?;
    m.add_class::<PyProgressReporter>()?;

    m.add_function(wrap_pyfunction!(create_algebra, m)?)?;
    m.add_function(wrap_pyfunction!(create_operation, m)?)?;
    m.add_function(wrap_pyfunction!(create_partition, m)?)?;
    m.add_function(wrap_pyfunction!(create_binary_relation, m)?)?;
    m.add_function(wrap_pyfunction!(create_congruence_lattice, m)?)?;
    m.add_function(wrap_pyfunction!(create_term_arena, m)?)?;
    m.add_function(wrap_pyfunction!(create_progress_reporter, m)?)?;
    m.add_function(wrap_pyfunction!(parse_term, m)?)?;
    m.add_function(wrap_pyfunction!(eval_term, m)?)?;

    // Add custom exception classes
    m.add("UACalcError", _py.get_type::<PyUACalcError>())?;
    m.add("CancellationError", _py.get_type::<PyCancellationError>())?;

    Ok(())
}

// Create custom exceptions using pyo3::create_exception!
pyo3::create_exception!(uacalc_rust, PyUACalcError, pyo3::exceptions::PyException);
pyo3::create_exception!(
    uacalc_rust,
    PyCancellationError,
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
            PyErr::new::<pyo3::exceptions::PyKeyError, _>(symbol)
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
}

#[pymethods]
impl PyCongruenceLattice {
    #[new]
    fn new(algebra: PyAlgebra) -> Self {
        Self {
            inner: Arc::new(Mutex::new(None)),
            algebra,
        }
    }

    fn ensure_universe_built(
        &self,
        py: Python,
        progress_callback: Option<PyObject>,
    ) -> PyResult<()> {
        let mut inner_guard = self.inner.lock().unwrap();
        if inner_guard.is_none() {
            let mut lattice = BasicCongruenceLattice::new(Box::new(self.algebra.inner.clone()))
                .map_err(map_uacalc_error)?;

            if let Some(callback) = progress_callback {
                let progress_reporter = PyProgressReporter::new(callback);
                lattice = lattice
                    .with_progress_callback(move |progress| {
                        Python::with_gil(|py| {
                            let _ = progress_reporter.report_progress(py, progress, None);
                        });
                    })
                    .map_err(map_uacalc_error)?;
            }

            *inner_guard = Some(lattice);
        }
        Ok(())
    }

    fn size(&self) -> PyResult<usize> {
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
            let congruences = lattice.congruences();
            let mut result = Vec::new();
            for p in congruences {
                if let Some(basic_partition) =
                    (p.as_ref() as &dyn std::any::Any).downcast_ref::<BasicPartition>()
                {
                    result.push(PyPartition {
                        inner: basic_partition.clone(),
                    });
                }
            }
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

    // TODO: Implement join and meet methods that work with indices

    fn atoms(&self, py: Python) -> PyResult<Vec<PyPartition>> {
        self.ensure_universe_built(py, None)?;
        let inner_guard = self.inner.lock().unwrap();
        if let Some(ref lattice) = *inner_guard {
            let atoms = lattice.atoms().map_err(map_uacalc_error)?;
            let mut result = Vec::new();
            for p in atoms {
                if let Some(basic_partition) =
                    (p.as_ref() as &dyn std::any::Any).downcast_ref::<BasicPartition>()
                {
                    result.push(PyPartition {
                        inner: basic_partition.clone(),
                    });
                }
            }
            Ok(result)
        } else {
            Ok(Vec::new())
        }
    }

    fn coatoms(&self, py: Python) -> PyResult<Vec<PyPartition>> {
        self.ensure_universe_built(py, None)?;
        let inner_guard = self.inner.lock().unwrap();
        if let Some(ref lattice) = *inner_guard {
            let coatoms = lattice.coatoms().map_err(map_uacalc_error)?;
            let mut result = Vec::new();
            for p in coatoms {
                if let Some(basic_partition) =
                    (p.as_ref() as &dyn std::any::Any).downcast_ref::<BasicPartition>()
                {
                    result.push(PyPartition {
                        inner: basic_partition.clone(),
                    });
                }
            }
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
        self.ensure_universe_built(py, Some(callback))
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
    fn is_variable(&self, py: Python) -> PyResult<bool> {
        let arena_guard = self.arena.inner.lock().unwrap();
        let term = arena_guard.get_term(self.id).map_err(map_uacalc_error)?;
        Ok(term.is_variable())
    }

    fn is_operation(&self, py: Python) -> PyResult<bool> {
        let arena_guard = self.arena.inner.lock().unwrap();
        let term = arena_guard.get_term(self.id).map_err(map_uacalc_error)?;
        Ok(term.is_operation())
    }

    fn arity(&self, py: Python) -> PyResult<usize> {
        let arena_guard = self.arena.inner.lock().unwrap();
        let term = arena_guard.get_term(self.id).map_err(map_uacalc_error)?;
        Ok(term.arity())
    }

    fn depth(&self, py: Python) -> PyResult<usize> {
        let arena_guard = self.arena.inner.lock().unwrap();
        let term = arena_guard.get_term(self.id).map_err(map_uacalc_error)?;
        term.depth(&arena_guard).map_err(map_uacalc_error)
    }

    fn variables(&self, py: Python) -> PyResult<Vec<u8>> {
        let arena_guard = self.arena.inner.lock().unwrap();
        let term = arena_guard.get_term(self.id).map_err(map_uacalc_error)?;
        term.variables(&arena_guard).map_err(map_uacalc_error)
    }

    fn to_string(&self, py: Python) -> PyResult<String> {
        let arena_guard = self.arena.inner.lock().unwrap();
        let term = arena_guard.get_term(self.id).map_err(map_uacalc_error)?;
        Ok(format!("{:?}", term))
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
        // For now, just create a simple variable term
        // TODO: Implement proper parsing
        let mut arena_guard = self.inner.lock().unwrap();
        let id = arena_guard.make_variable(0);
        Ok(PyTerm {
            id,
            arena: PyTermArena {
                inner: Arc::clone(&self.inner),
            },
        })
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

/// Python wrapper for BasicAlgebra
#[pyclass]
#[derive(Clone)]
pub struct PyAlgebra {
    inner: BasicAlgebra,
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
        let op = self
            .inner
            .operation_arc(index)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyOperation { inner: op })
    }

    fn operation_by_symbol(&self, symbol: &str) -> PyResult<PyOperation> {
        let op = self
            .inner
            .operation_arc_by_symbol(symbol)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyOperation { inner: op })
    }

    fn is_finite(&self) -> bool {
        self.inner.is_finite()
    }

    fn max_arity(&self) -> usize {
        self.inner.max_arity()
    }

    fn is_idempotent(&self, op_index: usize) -> PyResult<bool> {
        self.inner
            .is_idempotent()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn is_associative(&self, op_index: usize) -> PyResult<bool> {
        self.inner
            .is_associative()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }

    fn is_commutative(&self, op_index: usize) -> PyResult<bool> {
        self.inner
            .is_commutative()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
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
fn create_operation(name: String, arity: usize, table: Vec<Vec<usize>>) -> PyResult<PyOperation> {
    let symbol = uacalc_core::operation::OperationSymbol::new(name, arity);

    // Normalize table format to [args..., result]
    let normalized_table = if arity == 0 {
        // Constant operation: expect [[value]]
        if table.len() == 1 && table[0].len() == 1 {
            table
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Constant operation should have table [[value]]".to_string(),
            ));
        }
    } else if arity == 1 {
        // Unary operation: handle both [value] and [input, value] formats
        if table.len() > 0 && table[0].len() == 1 {
            // Transform [value] format to [input, value]
            let mut normalized = Vec::with_capacity(table.len());
            for (i, row) in table.iter().enumerate() {
                normalized.push(vec![i, row[0]]);
            }
            normalized
        } else {
            // Already in [input, value] format
            table
        }
    } else if arity == 2 {
        // Binary operation: handle NxN matrix format
        let n = table.len();
        if n > 0 && table[0].len() == n {
            // Transform NxN matrix to [i, j, result] format
            let mut normalized = Vec::with_capacity(n * n);
            for i in 0..n {
                for j in 0..n {
                    normalized.push(vec![i, j, table[i][j]]);
                }
            }
            normalized
        } else {
            // Already in [i, j, result] format
            table
        }
    } else {
        // Higher arity: expect [args..., result] format
        table
    };

    let operation = TableOperation::new(symbol, normalized_table, 0)
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

/// Helper function to create a binary relation
#[pyfunction]
fn create_binary_relation(size: usize) -> PyResult<PyBinaryRelation> {
    Ok(PyBinaryRelation::new(size))
}

/// Helper function to create a congruence lattice
#[pyfunction]
fn create_congruence_lattice(algebra: &PyAlgebra) -> PyResult<PyCongruenceLattice> {
    Ok(PyCongruenceLattice::new(algebra.clone()))
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
fn eval_term(term: &PyTerm, algebra: &PyAlgebra, assignment: &PyDict) -> PyResult<usize> {
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
