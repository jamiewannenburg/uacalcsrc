use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyAny;
use uacalc::alg::{Algebra, SmallAlgebra};
use uacalc::util::int_array::{IntArray, IntArrayTrait};

use crate::alg::basic_algebra::PyBasicAlgebra;
use crate::alg::big_product_algebra::PyBigProductAlgebra;
use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;
use crate::alg::convert::{
    algebra_type_java_name, operation_to_py, operations_to_py, ops_to_basic_algebra, term_to_py,
    vars_map_to_py,
};
use crate::alg::op::similarity_type::PySimilarityType;
use crate::alg::sublat::subalgebra_lattice::PySubalgebraLattice;
use crate::terms::PyVariableImp;
use crate::util::PyIntArray;

/// Python wrapper for SubProductAlgebra
#[pyclass]
pub struct PySubProductAlgebra {
    inner: uacalc::alg::SubProductAlgebra<i32>,
}

pub(crate) fn extract_int_array(obj: &Bound<'_, PyAny>) -> PyResult<IntArray> {
    if let Ok(ia) = obj.extract::<PyRef<PyIntArray>>() {
        return Ok(ia.inner.clone());
    }
    if let Ok(v) = obj.extract::<Vec<i32>>() {
        return IntArray::from_array(v).map_err(PyValueError::new_err);
    }
    for meth in ["to_array", "getArray", "get_array"] {
        if let Ok(arr) = obj.call_method0(meth) {
            if let Ok(v) = arr.extract::<Vec<i32>>() {
                return IntArray::from_array(v).map_err(PyValueError::new_err);
            }
        }
    }
    Err(PyValueError::new_err("expected IntArray or list[int]"))
}

fn extract_int_arrays(obj: &Bound<'_, PyAny>) -> PyResult<Vec<IntArray>> {
    let mut out = Vec::new();
    for item in obj.iter()? {
        out.push(extract_int_array(&item?)?);
    }
    Ok(out)
}

impl PySubProductAlgebra {
    pub(crate) fn as_inner(&self) -> &uacalc::alg::SubProductAlgebra<i32> {
        &self.inner
    }
}

#[pymethods]
impl PySubProductAlgebra {
    #[new]
    fn new(
        name: String,
        prod: &PyBigProductAlgebra,
        gens: &Bound<'_, PyAny>,
        find_terms: Option<bool>,
    ) -> PyResult<Self> {
        let gens = extract_int_arrays(gens)?;
        let inner = uacalc::alg::SubProductAlgebra::<i32>::new_safe(
            name,
            prod.clone_inner(),
            gens,
            find_terms.unwrap_or(false),
        )
        .map_err(PyValueError::new_err)?;
        Ok(PySubProductAlgebra { inner })
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

    fn name(&self) -> String {
        Algebra::name(&self.inner).to_string()
    }

    fn set_name(&mut self, name: String) {
        Algebra::set_name(&mut self.inner, name);
    }

    fn algebra_type(&self) -> String {
        algebra_type_java_name(SmallAlgebra::algebra_type(&self.inner))
    }

    fn generators(&self) -> Vec<Vec<i32>> {
        self.inner
            .generators()
            .iter()
            .map(|ia| ia.as_slice().to_vec())
            .collect()
    }

    fn get_universe_list(&self) -> Vec<Vec<i32>> {
        self.inner
            .get_universe_list()
            .iter()
            .map(|ia| ia.as_slice().to_vec())
            .collect()
    }

    fn get_universe_order(&self) -> Option<Vec<i32>> {
        None
    }

    fn get_product_algebra(&self) -> PyBigProductAlgebra {
        PyBigProductAlgebra::from_cloned(self.inner.get_product_algebra())
    }

    fn super_algebra(&self) -> PyBigProductAlgebra {
        self.get_product_algebra()
    }

    fn get_element(&self, k: usize) -> Vec<i32> {
        self.inner
            .get_universe_list()
            .get(k)
            .map(|ia| ia.as_slice().to_vec())
            .unwrap_or_default()
    }

    fn element_index(&self, tuple: Vec<i32>) -> i32 {
        match IntArray::from_array(tuple) {
            Ok(ia) => self
                .inner
                .get_universe_list()
                .iter()
                .position(|x| x == &ia)
                .map(|i| i as i32)
                .unwrap_or(-1),
            Err(_) => -1,
        }
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
        for op in Algebra::operations(&self.inner) {
            if op.symbol().name() == name {
                return Ok(Some(operation_to_py(py, op.as_ref())?));
            }
        }
        Ok(None)
    }

    fn make_operation_tables(&mut self) {
        Algebra::make_operation_tables(&mut self.inner);
    }

    fn similarity_type(&self) -> PySimilarityType {
        PySimilarityType::from_inner(Algebra::similarity_type(&self.inner).clone())
    }

    fn description(&self) -> Option<String> {
        Algebra::description(&self.inner).map(|s| s.to_string())
    }

    fn set_description(&mut self, description: Option<String>) {
        Algebra::set_description(&mut self.inner, description);
    }

    fn parent(&self) -> Option<PyObject> {
        None
    }

    fn parents(&self) -> Option<Vec<PyObject>> {
        None
    }

    fn get_terms(&self, py: Python<'_>) -> PyResult<Option<Vec<PyObject>>> {
        if self.inner.get_terms().is_none() {
            return Ok(None);
        }
        let mut out = Vec::new();
        for elt in self.inner.get_universe_list() {
            match self.inner.get_term(elt) {
                Some(term) => out.push(term_to_py(py, term)?),
                None => out.push(py.None()),
            }
        }
        Ok(Some(out))
    }

    /// Java `getTerm(IntArray)`.
    fn get_term(&self, py: Python<'_>, elt: &Bound<'_, PyAny>) -> PyResult<Option<PyObject>> {
        let ia = extract_int_array(elt)?;
        match self.inner.get_term(&ia) {
            Some(term) => Ok(Some(term_to_py(py, term)?)),
            None => Ok(None),
        }
    }

    /// Java `getVariableToGeneratorMap()`.
    fn get_variable_to_generator_map(&self, py: Python<'_>) -> PyResult<Option<PyObject>> {
        match self.inner.get_variable_to_generator_map() {
            Some(map) => Ok(Some(vars_map_to_py(py, map)?)),
            None => Ok(None),
        }
    }

    /// Java `getVariables()`.
    fn get_variables(&self) -> Option<Vec<PyVariableImp>> {
        self.inner.get_variables().map(|vars| {
            vars.into_iter()
                .map(|inner| PyVariableImp { inner })
                .collect()
        })
    }

    fn con(&mut self) -> PyResult<PyCongruenceLattice> {
        let basic = self.to_basic_algebra()?;
        Ok(PyCongruenceLattice::from_algebra(&basic))
    }

    fn sub(&mut self) -> PyResult<PySubalgebraLattice> {
        let basic = self.to_basic_algebra()?;
        PySubalgebraLattice::from_basic(&basic)
    }

    fn reset_con_and_sub(&mut self) {}

    fn to_basic_algebra(&self) -> PyResult<PyBasicAlgebra> {
        ops_to_basic_algebra(
            Algebra::name(&self.inner).to_string(),
            self.inner.cardinality(),
            Algebra::operations(&self.inner),
        )
    }

    fn __str__(&self) -> String {
        format!(
            "SubProductAlgebra(name: {}, cardinality: {})",
            Algebra::name(&self.inner),
            self.inner.cardinality()
        )
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }
}
