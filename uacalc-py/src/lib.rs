use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use uacalc_core::prelude::*;
use uacalc_core::operation::{TableOperation, FunctionOperation};
use uacalc_core::partition::finest_partition;
use uacalc_core::binary_relation::{identity_relation, universal_relation};

/// Python module for UACalc
#[pymodule]
fn uacalc(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyAlgebra>()?;
    m.add_class::<PyOperation>()?;
    m.add_class::<PyPartition>()?;
    m.add_class::<PyBinaryRelation>()?;
    m.add_class::<PyCongruenceLattice>()?;
    m.add_function(wrap_pyfunction!(create_algebra, m)?)?;
    m.add_function(wrap_pyfunction!(create_operation, m)?)?;
    m.add_function(wrap_pyfunction!(create_partition, m)?)?;
    m.add_function(wrap_pyfunction!(create_binary_relation, m)?)?;
    Ok(())
}

/// Python wrapper for BasicAlgebra
#[pyclass]
pub struct PyAlgebra {
    inner: BasicAlgebra,
}

#[pymethods]
impl PyAlgebra {
    #[new]
    fn new(name: String, universe: Vec<usize>) -> PyResult<Self> {
        Ok(Self {
            inner: BasicAlgebra::new(name, universe),
        })
    }
    
    #[pyo3(name = "add_operation")]
    fn py_add_operation(&mut self, symbol: String, operation: PyOperation) -> PyResult<()> {
        let op_box = Box::new(operation.inner);
        self.inner.add_operation(symbol, op_box)
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
    
    #[getter]
    fn operations(&self) -> Vec<PyOperation> {
        self.inner.operations()
            .iter()
            .map(|op| PyOperation { inner: op.as_ref().clone() })
            .collect()
    }
    
    fn operation(&self, index: usize) -> PyResult<PyOperation> {
        let op = self.inner.operation(index)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyOperation { inner: op.clone() })
    }
    
    fn operation_by_symbol(&self, symbol: &str) -> PyResult<PyOperation> {
        let op = self.inner.operation_by_symbol(symbol)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyOperation { inner: op.clone() })
    }
    
    fn is_finite(&self) -> bool {
        self.inner.is_finite()
    }
    
    fn max_arity(&self) -> usize {
        self.inner.max_arity()
    }
    
    fn is_idempotent(&self, op_index: usize) -> PyResult<bool> {
        self.inner.is_idempotent(op_index)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn is_associative(&self, op_index: usize) -> PyResult<bool> {
        self.inner.is_associative(op_index)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn is_commutative(&self, op_index: usize) -> PyResult<bool> {
        self.inner.is_commutative(op_index)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn subalgebra(&self, generators: Vec<usize>) -> PyResult<PyAlgebra> {
        let sub = self.inner.subalgebra(&generators)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyAlgebra { inner: sub })
    }
}

/// Python wrapper for Operation
#[pyclass]
pub struct PyOperation {
    inner: Box<dyn Operation>,
}

#[pymethods]
impl PyOperation {
    #[getter]
    fn arity(&self) -> usize {
        self.inner.arity()
    }
    
    #[getter]
    fn symbol(&self) -> PyResult<String> {
        Ok(self.inner.symbol().name.clone())
    }
    
    fn value(&self, args: Vec<usize>) -> PyResult<usize> {
        self.inner.value(&args)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn operation_type(&self) -> String {
        match self.inner.operation_type() {
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
        self.inner.block(element)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn representative(&self, element: usize) -> PyResult<usize> {
        self.inner.representative(element)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn same_block(&self, a: usize, b: usize) -> PyResult<bool> {
        self.inner.same_block(a, b)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn blocks(&self) -> Vec<Vec<usize>> {
        self.inner.blocks()
    }
    
    fn union(&mut self, x: usize, y: usize) -> PyResult<()> {
        self.inner.union(x, y)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn join(&self, other: &PyPartition) -> PyResult<PyPartition> {
        let result = self.inner.join(&other.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyPartition { inner: result.downcast::<BasicPartition>().unwrap() })
    }
    
    fn meet(&self, other: &PyPartition) -> PyResult<PyPartition> {
        let result = self.inner.meet(&other.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyPartition { inner: result.downcast::<BasicPartition>().unwrap() })
    }
    
    fn is_finer_than(&self, other: &PyPartition) -> PyResult<bool> {
        self.inner.is_finer_than(&other.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn is_coarser_than(&self, other: &PyPartition) -> PyResult<bool> {
        self.inner.is_coarser_than(&other.inner)
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
        self.inner.contains(a, b)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn add(&mut self, a: usize, b: usize) -> PyResult<()> {
        self.inner.add(a, b)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn remove(&mut self, a: usize, b: usize) -> PyResult<()> {
        self.inner.remove(a, b)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn pairs(&self) -> Vec<(usize, usize)> {
        self.inner.pairs()
    }
    
    fn reflexive_closure(&self) -> PyResult<PyBinaryRelation> {
        let closure = self.inner.reflexive_closure()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyBinaryRelation { inner: closure.downcast::<BasicBinaryRelation>().unwrap() })
    }
    
    fn symmetric_closure(&self) -> PyResult<PyBinaryRelation> {
        let closure = self.inner.symmetric_closure()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyBinaryRelation { inner: closure.downcast::<BasicBinaryRelation>().unwrap() })
    }
    
    fn transitive_closure(&self) -> PyResult<PyBinaryRelation> {
        let closure = self.inner.transitive_closure()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyBinaryRelation { inner: closure.downcast::<BasicBinaryRelation>().unwrap() })
    }
    
    fn equivalence_closure(&self) -> PyResult<PyBinaryRelation> {
        let closure = self.inner.equivalence_closure()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyBinaryRelation { inner: closure.downcast::<BasicBinaryRelation>().unwrap() })
    }
    
    fn is_reflexive(&self) -> PyResult<bool> {
        self.inner.is_reflexive()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn is_symmetric(&self) -> PyResult<bool> {
        self.inner.is_symmetric()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn is_transitive(&self) -> PyResult<bool> {
        self.inner.is_transitive()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn is_equivalence(&self) -> PyResult<bool> {
        self.inner.is_equivalence()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
}

/// Python wrapper for BasicCongruenceLattice
#[pyclass]
pub struct PyCongruenceLattice {
    inner: BasicCongruenceLattice,
}

#[pymethods]
impl PyCongruenceLattice {
    #[new]
    fn new(algebra: PyAlgebra) -> PyResult<Self> {
        let algebra_box = Box::new(algebra.inner);
        let lattice = BasicCongruenceLattice::new(algebra_box)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(Self { inner: lattice })
    }
    
    #[getter]
    fn num_congruences(&self) -> usize {
        self.inner.num_congruences()
    }
    
    fn congruences(&self) -> Vec<PyPartition> {
        self.inner.congruences()
            .iter()
            .map(|cong| PyPartition { inner: cong.downcast::<BasicPartition>().unwrap() })
            .collect()
    }
    
    fn bottom(&self) -> PyPartition {
        PyPartition { inner: self.inner.bottom().downcast::<BasicPartition>().unwrap() }
    }
    
    fn top(&self) -> PyPartition {
        PyPartition { inner: self.inner.top().downcast::<BasicPartition>().unwrap() }
    }
    
    fn is_congruence(&self, partition: &PyPartition) -> PyResult<bool> {
        self.inner.is_congruence(&partition.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
    
    fn join(&self, a: &PyPartition, b: &PyPartition) -> PyResult<PyPartition> {
        let result = self.inner.join(&a.inner, &b.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyPartition { inner: result.downcast::<BasicPartition>().unwrap() })
    }
    
    fn meet(&self, a: &PyPartition, b: &PyPartition) -> PyResult<PyPartition> {
        let result = self.inner.meet(&a.inner, &b.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(PyPartition { inner: result.downcast::<BasicPartition>().unwrap() })
    }
    
    fn atoms(&self) -> Vec<PyPartition> {
        self.inner.atoms()
            .iter()
            .map(|atom| PyPartition { inner: atom.downcast::<BasicPartition>().unwrap() })
            .collect()
    }
    
    fn coatoms(&self) -> Vec<PyPartition> {
        self.inner.coatoms()
            .iter()
            .map(|coatom| PyPartition { inner: coatom.downcast::<BasicPartition>().unwrap() })
            .collect()
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
    let operation = TableOperation::new(symbol, table)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
    Ok(PyOperation { inner: Box::new(operation) })
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

