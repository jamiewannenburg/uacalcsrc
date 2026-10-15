use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyAny;
use uacalc::alg::{Algebra, SmallAlgebra};

use crate::alg::algebra_extract::extract_boxed_small_algebra;
use crate::alg::basic_algebra::PyBasicAlgebra;
use crate::alg::convert::{
    algebra_type_java_name, binary_search_usize, ops_to_basic_algebra, operation_to_py,
    operations_to_py,
};
use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;
use crate::alg::conlat::partition::PyPartition;
use crate::alg::op::similarity_type::PySimilarityType;
use crate::alg::sublat::subalgebra_lattice::PySubalgebraLattice;

/// Python wrapper for QuotientAlgebra
#[pyclass]
pub struct PyQuotientAlgebra {
    inner: uacalc::alg::QuotientAlgebra<i32>,
    super_obj: PyObject,
}

#[pyclass]
pub struct PyQuotientElement {
    index: usize,
    index_in_super: i32,
    super_elem: PyObject,
    congruence_str: String,
    algebra: Py<PyQuotientAlgebra>,
}

#[pymethods]
impl PyQuotientAlgebra {
    #[new]
    fn new(
        py: Python<'_>,
        name: String,
        alg: &Bound<'_, PyAny>,
        cong: &PyPartition,
    ) -> PyResult<Self> {
        let super_box = extract_boxed_small_algebra(alg)?;
        let inner = uacalc::alg::QuotientAlgebra::<i32>::new_with_name_safe(
            name,
            super_box,
            cong.get_inner().clone(),
        )
        .map_err(PyValueError::new_err)?;
        Ok(PyQuotientAlgebra {
            inner,
            super_obj: alg.clone().into_py(py),
        })
    }

    fn cardinality(&self) -> i32 {
        Algebra::cardinality(&self.inner)
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

    fn name(&self) -> &str {
        Algebra::name(&self.inner)
    }

    fn set_name(&mut self, name: String) {
        Algebra::set_name(&mut self.inner, name);
    }

    fn description(&self) -> Option<&str> {
        Algebra::description(&self.inner)
    }

    fn set_description(&mut self, description: Option<String>) {
        Algebra::set_description(&mut self.inner, description);
    }

    fn algebra_type(&self) -> String {
        algebra_type_java_name(SmallAlgebra::algebra_type(&self.inner))
    }

    fn super_algebra(&self, py: Python<'_>) -> PyObject {
        self.super_obj.clone_ref(py)
    }

    fn get_congruence(&self) -> PyPartition {
        PyPartition::from_inner(self.inner.get_congruence().clone())
    }

    fn representatives(&self) -> Vec<i32> {
        self.inner.representatives.iter().map(|&r| r as i32).collect()
    }

    /// Java `Arrays.binarySearch(representatives, rep)`.
    fn representative_index(&self, rep: i32) -> i32 {
        if rep < 0 {
            return -1;
        }
        binary_search_usize(&self.inner.representatives, rep as usize)
    }

    fn canonical_homomorphism(&self, e: i32) -> i32 {
        if e < 0 {
            return self.representative_index(e);
        }
        let rep = self.inner.get_congruence().representative(e as usize);
        binary_search_usize(&self.inner.representatives, rep)
    }

    fn get_universe_list(&self) -> Option<Vec<i32>> {
        None
    }

    fn get_universe_order(&self) -> Option<Vec<i32>> {
        None
    }

    fn get_element(slf: Py<Self>, py: Python<'_>, index: i32) -> PyResult<PyQuotientElement> {
        if index < 0 {
            return Err(PyValueError::new_err(format!(
                "Index: {}, Size: {}",
                index,
                slf.borrow(py).inner.representatives.len()
            )));
        }
        let k = index as usize;
        let borrow = slf.borrow(py);
        if k >= borrow.inner.representatives.len() {
            return Err(PyValueError::new_err(format!(
                "Index: {}, Size: {}",
                index,
                borrow.inner.representatives.len()
            )));
        }
        let index_in_super = borrow.inner.representatives[k] as i32;
        let congruence_str = borrow.inner.get_congruence().to_string();
        let super_obj = borrow.super_obj.clone_ref(py);
        drop(borrow);
        let super_elem = if let Ok(get) = super_obj.getattr(py, "getElement") {
            get.call1(py, (index_in_super,))?
        } else if let Ok(get) = super_obj.getattr(py, "get_element") {
            get.call1(py, (index_in_super,))?
        } else {
            index_in_super.into_py(py)
        };
        Ok(PyQuotientElement {
            index: k,
            index_in_super,
            super_elem,
            congruence_str,
            algebra: slf,
        })
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

    fn similarity_type(&self) -> PySimilarityType {
        PySimilarityType::from_inner(Algebra::similarity_type(&self.inner).clone())
    }

    fn make_operation_tables(&mut self) {
        self.inner.make_operation_tables();
    }

    fn parent(&self) -> Option<PyObject> {
        None
    }

    fn parents(&self) -> Option<Vec<PyObject>> {
        None
    }

    fn reset_con_and_sub(&mut self) {}

    fn con(&mut self) -> PyResult<PyCongruenceLattice> {
        let basic = self.to_basic_algebra()?;
        Ok(PyCongruenceLattice::from_algebra(&basic))
    }

    fn sub(&mut self) -> PyResult<PySubalgebraLattice> {
        let basic = self.to_basic_algebra()?;
        PySubalgebraLattice::from_basic(&basic)
    }

    fn to_basic_algebra(&self) -> PyResult<PyBasicAlgebra> {
        ops_to_basic_algebra(
            Algebra::name(&self.inner).to_string(),
            Algebra::cardinality(&self.inner),
            Algebra::operations(&self.inner),
        )
    }

    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    fn __repr__(&self) -> String {
        format!("QuotientAlgebra({})", self.inner)
    }
}

#[pymethods]
impl PyQuotientElement {
    fn get_algebra(&self, py: Python<'_>) -> Py<PyQuotientAlgebra> {
        self.algebra.clone_ref(py)
    }

    fn super_algebra(&self, py: Python<'_>) -> PyObject {
        self.algebra.borrow(py).super_algebra(py)
    }

    fn get_congruence(&self, py: Python<'_>) -> PyPartition {
        self.algebra.borrow(py).get_congruence()
    }

    fn get_index(&self) -> usize {
        self.index
    }

    fn get_index_in_super_algebra(&self) -> i32 {
        self.index_in_super
    }

    fn __str__(&self, py: Python<'_>) -> PyResult<String> {
        let elem = self.super_elem.bind(py).str()?.to_str()?.to_owned();
        Ok(format!("{}/{}", elem, self.congruence_str))
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        self.__str__(py)
    }
}
