use crate::alg::algebra_extract::extract_boxed_small_algebra;
use crate::alg::convert::{ops_to_basic_algebra, term_to_py};
use crate::alg::op::operation_symbol::PyOperationSymbol;
use crate::alg::PyBasicAlgebra;
use crate::util::PyIntArray;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyAny;
use std::sync::Arc;
use uacalc::alg::{Algebra, BigProductAlgebra, SmallAlgebra};
use uacalc::util::int_array::IntArray;

/// Python wrapper for BigProductAlgebra
#[pyclass(name = "BigProductAlgebra")]
pub struct PyBigProductAlgebra {
    inner: Arc<BigProductAlgebra<i32>>,
}

#[pymethods]
impl PyBigProductAlgebra {
    /// Create a new BigProductAlgebra from a list of SmallAlgebras.
    ///
    /// # Arguments
    /// * `algebras` - List of SmallAlgebra instances
    ///
    /// # Returns
    /// A new BigProductAlgebra instance
    #[staticmethod]
    fn new_from_algebras(algebras: &Bound<'_, PyAny>) -> PyResult<Self> {
        Self::new_from_algebras_named("".to_string(), algebras)
    }

    #[staticmethod]
    fn new_from_algebras_named(name: String, algebras: &Bound<'_, PyAny>) -> PyResult<Self> {
        let mut rust_algs: Vec<Box<dyn SmallAlgebra<UniverseItem = i32>>> = Vec::new();
        for item in algebras.iter()? {
            rust_algs.push(extract_boxed_small_algebra(&item?)?);
        }
        match BigProductAlgebra::<i32>::new_with_name_safe(name, rust_algs) {
            Ok(algebra) => Ok(PyBigProductAlgebra {
                inner: Arc::new(algebra),
            }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new BigProductAlgebra as a power.
    ///
    /// # Arguments
    /// * `algebra` - The base algebra
    /// * `power` - The power
    ///
    /// # Returns
    /// A new BigProductAlgebra instance
    #[staticmethod]
    fn new_power(algebra: &Bound<'_, PyAny>, power: usize) -> PyResult<Self> {
        Self::new_power_named("".to_string(), algebra, power)
    }

    #[staticmethod]
    fn new_power_named(name: String, algebra: &Bound<'_, PyAny>, power: usize) -> PyResult<Self> {
        let rust_alg = extract_boxed_small_algebra(algebra)?;
        match BigProductAlgebra::<i32>::new_power_with_name_safe(name, rust_alg, power) {
            Ok(algebra) => Ok(PyBigProductAlgebra {
                inner: Arc::new(algebra),
            }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the number of factors.
    ///
    /// # Returns
    /// The number of factors
    fn get_number_of_factors(&self) -> usize {
        self.inner.get_number_of_factors()
    }

    /// Java ``isPower()``: powers is non-null and has length 1.

    /// Get the name of the algebra.
    ///
    /// # Returns
    /// The name
    fn name(&self) -> String {
        self.inner.name().to_string()
    }

    /// Java `numberOfFactors()` / `getNumberOfFactors()`.
    fn number_of_factors(&self) -> usize {
        self.inner.get_number_of_factors()
    }

    #[allow(non_snake_case)]
    fn getNumberOfFactors(&self) -> usize {
        self.inner.get_number_of_factors()
    }

    #[allow(non_snake_case)]
    fn numberOfFactors(&self) -> usize {
        self.inner.get_number_of_factors()
    }

    /// Java ``getPowers()``. Empty when this is not stored as a power.
    fn get_powers(&self) -> Vec<i32> {
        self.inner
            .get_powers()
            .map(|p| p.to_vec())
            .unwrap_or_default()
    }

    /// Java ``rootFactors()`` materialized as table-backed BasicAlgebras.
    fn root_factors(&self) -> PyResult<Vec<PyBasicAlgebra>> {
        let factors = self
            .inner
            .root_factors()
            .unwrap_or_else(|| self.inner.factors());
        Self::factors_to_basic(factors)
    }

    /// Java ``rootFactors()`` is null when this was not built as a power.
    fn root_factors_or_none(&self) -> PyResult<Option<Vec<PyBasicAlgebra>>> {
        match self.inner.root_factors() {
            Some(factors) => Ok(Some(Self::factors_to_basic(factors)?)),
            None => Ok(None),
        }
    }

    /// Java ``factors()``.
    fn factors(&self) -> PyResult<Vec<PyBasicAlgebra>> {
        Self::factors_to_basic(self.inner.factors())
    }

    fn is_power(&self) -> bool {
        self.inner
            .get_powers()
            .map(|p| p.len() == 1)
            .unwrap_or(false)
    }

    #[allow(non_snake_case)]
    fn isPower(&self) -> bool {
        self.is_power()
    }

    fn size_multiplicities(&self) -> std::collections::BTreeMap<i32, i32> {
        self.inner.size_multiplicities()
    }

    #[allow(non_snake_case)]
    fn sizeMultiplicities(&self) -> std::collections::BTreeMap<i32, i32> {
        self.size_multiplicities()
    }

    fn projection(&self, k: usize) -> PyResult<PyBasicAlgebra> {
        let factor = self
            .inner
            .projection(k)
            .map_err(PyValueError::new_err)?;
        ops_to_basic_algebra(
            factor.name().to_string(),
            factor.cardinality(),
            factor.operations(),
        )
    }

    /// Java stub: always null.
    fn projection_kernel(&self, _k: i32) -> Option<PyObject> {
        None
    }

    #[allow(non_snake_case)]
    fn projectionKernel(&self, k: i32) -> Option<PyObject> {
        self.projection_kernel(k)
    }

    fn get_constants(&self) -> Vec<PyIntArray> {
        let mut alg = (*self.inner).clone();
        alg.get_constants()
            .into_iter()
            .map(|ia| PyIntArray { inner: ia })
            .collect()
    }

    #[allow(non_snake_case)]
    fn getConstants(&self) -> Vec<PyIntArray> {
        self.get_constants()
    }

    fn get_constant_symbol(&self, constant: &PyIntArray) -> Option<PyOperationSymbol> {
        let mut alg = (*self.inner).clone();
        alg.get_constant_symbol(&constant.inner)
            .map(PyOperationSymbol::from_inner)
    }

    #[allow(non_snake_case)]
    fn getConstantSymbol(&self, constant: &PyIntArray) -> Option<PyOperationSymbol> {
        self.get_constant_symbol(constant)
    }

    fn get_constant_term(&self, py: Python<'_>, constant: &PyIntArray) -> PyResult<PyObject> {
        let mut alg = (*self.inner).clone();
        match alg.get_constant_term(&constant.inner) {
            Ok(term) => term_to_py(py, term.as_ref()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[allow(non_snake_case)]
    fn getConstantTerm(&self, py: Python<'_>, constant: &PyIntArray) -> PyResult<PyObject> {
        self.get_constant_term(py, constant)
    }

    fn make_operation_tables(&self) {
        let mut alg = (*self.inner).clone();
        alg.make_operation_tables();
    }

    #[allow(non_snake_case)]
    fn makeOperationTables(&self) {
        self.make_operation_tables()
    }

    fn cardinality(&self) -> i32 {
        Algebra::cardinality(&*self.inner)
    }

    /// Apply product operation ``op_index`` to coordinate arrays (Java ``valueAt(int[][])``).
    fn value_at_arrays(&self, op_index: usize, args: Vec<Vec<i32>>) -> PyResult<Vec<i32>> {
        let ops = self.inner.operations_ref_arc();
        let op = ops.get(op_index).ok_or_else(|| {
            PyValueError::new_err(format!("operation index {} out of range", op_index))
        })?;
        let refs: Vec<&[i32]> = args.iter().map(|a| a.as_slice()).collect();
        op.value_at_arrays(&refs).map_err(PyValueError::new_err)
    }

    fn operations_meta(&self) -> Vec<(String, i32)> {
        self.inner
            .operations_ref_arc()
            .iter()
            .map(|op| (op.symbol().name().to_string(), op.arity()))
            .collect()
    }

    fn sg_close(&self, elems: Vec<PyRef<PyIntArray>>) -> PyResult<Vec<PyIntArray>> {
        let gens: Vec<IntArray> = elems.iter().map(|e| e.inner.clone()).collect();
        match self.inner.sg_close(gens) {
            Ok(closed) => Ok(closed.into_iter().map(|ia| PyIntArray { inner: ia }).collect()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn sg_close_with_elt(
        &self,
        elems: Vec<PyRef<PyIntArray>>,
        elt: Option<&PyIntArray>,
    ) -> PyResult<Vec<PyIntArray>> {
        let gens: Vec<IntArray> = elems.iter().map(|e| e.inner.clone()).collect();
        match self.inner.sg_close_full(
            gens,
            0,
            None,
            elt.map(|e| e.inner.clone()),
            None,
        ) {
            Ok(closed) => Ok(closed.into_iter().map(|ia| PyIntArray { inner: ia }).collect()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn __str__(&self) -> String {
        format!(
            "BigProductAlgebra(name: {}, factors: {})",
            self.inner.name(),
            self.inner.get_number_of_factors()
        )
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }
}

impl PyBigProductAlgebra {
    fn factors_to_basic(
        factors: &[Arc<dyn SmallAlgebra<UniverseItem = i32>>],
    ) -> PyResult<Vec<PyBasicAlgebra>> {
        let mut out = Vec::new();
        for factor in factors {
            out.push(ops_to_basic_algebra(
                factor.name().to_string(),
                factor.cardinality(),
                factor.operations(),
            )?);
        }
        Ok(out)
    }

    /// Get the inner BigProductAlgebra (for internal use)
    pub(crate) fn get_inner(&self) -> Arc<BigProductAlgebra<i32>> {
        Arc::clone(&self.inner)
    }

    pub(crate) fn from_cloned(inner: &BigProductAlgebra<i32>) -> Self {
        PyBigProductAlgebra {
            inner: Arc::new(inner.clone()),
        }
    }

    pub(crate) fn clone_inner(&self) -> BigProductAlgebra<i32> {
        (*self.inner).clone()
    }
}
