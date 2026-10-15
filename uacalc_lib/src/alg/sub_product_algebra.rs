use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyAny;
use uacalc::alg::{Algebra, SmallAlgebra};
use uacalc::util::int_array::{IntArray, IntArrayTrait};

use crate::alg::big_product_algebra::PyBigProductAlgebra;
use crate::alg::convert::{algebra_type_java_name, ops_to_basic_algebra, operation_to_py, operations_to_py};
use crate::alg::basic_algebra::PyBasicAlgebra;
use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;
use crate::alg::op::similarity_type::PySimilarityType;
use crate::alg::sublat::subalgebra_lattice::PySubalgebraLattice;
use crate::util::PyIntArray;

/// Python wrapper for SubProductAlgebra
#[pyclass]
pub struct PySubProductAlgebra {
    inner: uacalc::alg::SubProductAlgebra<i32>,
}

fn extract_int_arrays(obj: &Bound<'_, PyAny>) -> PyResult<Vec<IntArray>> {
    let mut out = Vec::new();
    for item in obj.iter()? {
        let item = item?;
        if let Ok(ia) = item.extract::<PyRef<PyIntArray>>() {
            out.push(ia.inner.clone());
            continue;
        }
        if let Ok(v) = item.extract::<Vec<i32>>() {
            out.push(IntArray::from_array(v).map_err(PyValueError::new_err)?);
            continue;
        }
        return Err(PyValueError::new_err(
            "generators must be IntArray or list[int]",
        ));
    }
    Ok(out)
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

    fn get_terms(&self) -> Option<Vec<PyObject>> {
        None
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
