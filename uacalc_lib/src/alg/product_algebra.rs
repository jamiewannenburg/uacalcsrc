use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyAny;
use uacalc::alg::*;
use uacalc::util::horner;
use crate::alg::convert::{algebra_type_java_name, ops_to_basic_algebra, operation_to_py, operations_to_py};
use crate::alg::{PyBasicAlgebra, PySubalgebraLattice};
use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;
use crate::alg::op::similarity_type::PySimilarityType;

/// Python wrapper for ProductAlgebra
#[pyclass]
pub struct PyProductAlgebra {
    inner: uacalc::alg::ProductAlgebra,
    factors: Vec<uacalc::alg::BasicAlgebra<i32>>,
}

#[pymethods]
impl PyProductAlgebra {
    /// Create a new ProductAlgebra from a list of algebras.
    #[new]
    fn new(name: String, algebras: Vec<PyRef<PyBasicAlgebra>>) -> PyResult<Self> {
        if algebras.is_empty() {
            return Err(PyValueError::new_err("Cannot create product of empty algebra list"));
        }

        let factors: Vec<uacalc::alg::BasicAlgebra<i32>> =
            algebras.iter().map(|alg| alg.inner.clone()).collect();
        let rust_algebras: Vec<Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>> = factors
            .iter()
            .map(|alg| Box::new(alg.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>)
            .collect();

        match uacalc::alg::ProductAlgebra::new_safe(name, rust_algebras) {
            Ok(inner) => Ok(PyProductAlgebra { inner, factors }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn calc_card(sizes: Vec<i32>) -> PyResult<i32> {
        match uacalc::alg::ProductAlgebra::calc_card_safe(&sizes) {
            Ok(card) => Ok(card),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn number_of_factors(&self) -> usize {
        self.inner.number_of_factors()
    }

    fn get_sizes(&self) -> Vec<i32> {
        self.inner.get_sizes().to_vec()
    }

    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }

    fn input_size(&self) -> i32 {
        Algebra::input_size(&self.inner)
    }

    fn is_unary(&self) -> bool {
        Algebra::is_unary(&self.inner)
    }

    fn is_idempotent(&self) -> bool {
        Algebra::is_idempotent(&self.inner)
    }

    fn is_total(&self) -> bool {
        Algebra::is_total(&self.inner)
    }

    /// Horner index identity (library helper). Java `getElement` is the tuple.
    fn get_element(&self, k: usize) -> i32 {
        self.inner.get_element(k).unwrap_or(-1)
    }

    /// Java `getElement(int)` → `Horner.hornerInv(index, sizes)` (`int[]`).
    fn get_element_tuple(&self, k: i32) -> Vec<i32> {
        horner::horner_inv(k, self.inner.get_sizes())
    }

    fn element_index(&self, elem: i32) -> i32 {
        match self.inner.element_index(&elem) {
            Some(idx) => idx as i32,
            None => -1,
        }
    }

    /// Java `elementIndex(IntArray)` → `Horner.horner(array, sizes)`.
    fn element_index_tuple(&self, tuple: Vec<i32>) -> i32 {
        horner::horner(&tuple, self.inner.get_sizes())
    }

    /// Java universe iterator: last index increments fastest.
    fn get_universe_tuples(&self) -> Vec<Vec<i32>> {
        java_last_fastest_tuples(self.inner.get_sizes())
    }

    fn get_universe_list(&self) -> Vec<Vec<i32>> {
        self.get_universe_tuples()
    }

    fn get_universe_order(&self) -> Option<Vec<i32>> {
        None
    }

    fn algebra_type(&self) -> String {
        format!("{:?}", self.inner.algebra_type())
    }

    fn name(&self) -> &str {
        self.inner.name()
    }

    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }

    fn description(&self) -> Option<&str> {
        Algebra::description(&self.inner)
    }

    fn set_description(&mut self, description: Option<String>) {
        Algebra::set_description(&mut self.inner, description);
    }

    fn similarity_type(&self) -> PySimilarityType {
        PySimilarityType::from_inner(Algebra::similarity_type(&self.inner).clone())
    }

    fn operations(&self, py: Python<'_>) -> PyResult<Vec<PyObject>> {
        operations_to_py(py, Algebra::operations(&self.inner))
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

    fn make_operation_tables(&mut self) {
        self.inner.make_operation_tables();
    }

    fn factors(&self) -> Vec<PyBasicAlgebra> {
        self.factors
            .iter()
            .map(|alg| PyBasicAlgebra::from_inner(alg.clone()))
            .collect()
    }

    fn parents(&self) -> Vec<PyBasicAlgebra> {
        self.factors()
    }

    fn parent(&self) -> Option<PyBasicAlgebra> {
        None
    }

    fn projection(&self, k: usize) -> PyResult<PyBasicAlgebra> {
        self.factors.get(k).map(|alg| PyBasicAlgebra::from_inner(alg.clone())).ok_or_else(|| {
            PyValueError::new_err(format!("projection index {} out of range", k))
        })
    }

    /// Java stub: always null.
    fn projection_kernel(&self, _k: i32) -> Option<PyObject> {
        None
    }

    /// Java stub: always empty.
    fn sg_close(&self, _elems: Vec<Bound<'_, PyAny>>) -> Vec<PyObject> {
        Vec::new()
    }

    fn con(&mut self) -> PyCongruenceLattice {
        let con_lat = self.inner.con();
        PyCongruenceLattice { inner: con_lat.clone() }
    }

    fn sub(&mut self) -> PySubalgebraLattice {
        let sub_lat = self.inner.sub();
        PySubalgebraLattice::from_inner(sub_lat.clone())
    }

    fn reset_con_and_sub(&mut self) {
        SmallAlgebra::reset_con_and_sub(&mut self.inner);
    }

    fn to_basic_algebra(&self) -> PyResult<PyBasicAlgebra> {
        ops_to_basic_algebra(
            self.inner.name().to_string(),
            self.inner.cardinality(),
            Algebra::operations(&self.inner),
        )
    }

    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    fn __repr__(&self) -> String {
        format!("ProductAlgebra({})", self.inner.to_string())
    }
}

impl PyProductAlgebra {
    pub(crate) fn as_inner(&self) -> &uacalc::alg::ProductAlgebra {
        &self.inner
    }

    pub(crate) fn from_inner(inner: uacalc::alg::ProductAlgebra) -> Self {
        let factors = inner
            .factors()
            .iter()
            .map(|alg| {
                let card = alg.cardinality();
                let universe = (0..card).collect();
                uacalc::alg::BasicAlgebra::new(
                    alg.name().to_string(),
                    universe,
                    alg.operations(),
                )
            })
            .collect();
        PyProductAlgebra { inner, factors }
    }

    pub(crate) fn clone_inner(&self) -> uacalc::alg::ProductAlgebra {
        self.inner.clone()
    }
}

/// Java `ProductIterator`: last (right-most) index increments fastest.
fn java_last_fastest_tuples(sizes: &[i32]) -> Vec<Vec<i32>> {
    if sizes.is_empty() {
        return vec![Vec::new()];
    }
    if sizes.iter().any(|&s| s <= 0) {
        return Vec::new();
    }
    let n = sizes.len();
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
