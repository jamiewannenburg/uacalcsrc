use crate::alg::algebra_extract::extract_boxed_small_algebra;
use crate::alg::big_product_algebra::PyBigProductAlgebra;
use crate::alg::conlat::partition::PyPartition;
use crate::alg::convert::{ops_to_basic_algebra, py_to_term, term_to_py};
use crate::eq::PyEquation;
use crate::util::PyIntArray;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict, PyList};
use std::collections::{HashMap, HashSet};
use std::sync::Arc;
use uacalc::alg::{Closer, SmallAlgebra};
use uacalc::terms::Term;
use uacalc::util::int_array::IntArray;

/// Python wrapper for Closer
#[pyclass]
pub struct PyCloser {
    inner: Closer<i32>,
}

fn extract_int_arrays(gens: &Bound<'_, PyAny>) -> PyResult<Vec<IntArray>> {
    let mut out = Vec::new();
    for item in gens.iter()? {
        let item = item?;
        if let Ok(ia) = item.extract::<PyRef<PyIntArray>>() {
            out.push(ia.inner.clone());
        } else {
            let vals: Vec<i32> = item.extract()?;
            out.push(IntArray::from_array(vals).map_err(PyValueError::new_err)?);
        }
    }
    Ok(out)
}

fn extract_int_array(elem: &Bound<'_, PyAny>) -> PyResult<IntArray> {
    if let Ok(ia) = elem.extract::<PyRef<PyIntArray>>() {
        return Ok(ia.inner.clone());
    }
    let vals: Vec<i32> = elem.extract()?;
    IntArray::from_array(vals).map_err(PyValueError::new_err)
}

fn to_py_int_arrays(arrays: &[IntArray]) -> Vec<PyIntArray> {
    arrays
        .iter()
        .map(|ia| PyIntArray { inner: ia.clone() })
        .collect()
}

#[pymethods]
impl PyCloser {
    /// Create a new Closer with an algebra and generators.
    #[new]
    fn new(algebra: &PyBigProductAlgebra, generators: &Bound<'_, PyAny>) -> PyResult<Self> {
        let rust_gens = extract_int_arrays(generators)?;
        match Closer::new_safe(algebra.get_inner(), rust_gens) {
            Ok(closer) => Ok(PyCloser { inner: closer }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Java `Closer(alg, gens, termMap)`.
    #[staticmethod]
    fn new_with_term_map(
        py: Python<'_>,
        algebra: &PyBigProductAlgebra,
        generators: &Bound<'_, PyAny>,
        term_map: &Bound<'_, PyAny>,
    ) -> PyResult<Self> {
        let rust_gens = extract_int_arrays(generators)?;
        let rust_map = py_term_map(py, term_map)?;
        match Closer::new_with_term_map_safe(algebra.get_inner(), rust_gens, rust_map) {
            Ok(closer) => Ok(PyCloser { inner: closer }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Java `Closer(alg, gens, makeTermMap)`.
    #[staticmethod]
    fn new_with_make_term_map(
        algebra: &PyBigProductAlgebra,
        generators: &Bound<'_, PyAny>,
        make_term_map: bool,
    ) -> PyResult<Self> {
        let rust_gens = extract_int_arrays(generators)?;
        let mut closer =
            Closer::new_safe(algebra.get_inner(), rust_gens).map_err(PyValueError::new_err)?;
        if make_term_map {
            closer.setup_term_map();
        }
        Ok(PyCloser { inner: closer })
    }

    fn get_generators(&self) -> Vec<PyIntArray> {
        to_py_int_arrays(self.inner.get_generators())
    }

    fn set_generators(&mut self, generators: &Bound<'_, PyAny>) -> PyResult<()> {
        let rust_gens = extract_int_arrays(generators)?;
        self.inner.set_generators(rust_gens);
        Ok(())
    }

    fn get_answer(&self) -> Vec<PyIntArray> {
        to_py_int_arrays(self.inner.get_answer())
    }

    fn close(&mut self) -> PyResult<Vec<PyIntArray>> {
        match self.inner.close() {
            Ok(result) => Ok(to_py_int_arrays(&result)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn sg_close(&mut self) -> PyResult<Vec<PyIntArray>> {
        match self.inner.sg_close() {
            Ok(result) => Ok(to_py_int_arrays(&result)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Java `sgClose(elems, closedMark, termMap)` element-set path.
    fn sg_close_from(
        &mut self,
        elems: &Bound<'_, PyAny>,
        closed_mark: usize,
    ) -> PyResult<Vec<PyIntArray>> {
        let rust_elems = extract_int_arrays(elems)?;
        match self.inner.sg_close_from(Some(rust_elems), closed_mark) {
            Ok(result) => Ok(to_py_int_arrays(&result)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn sg_close_power(&mut self) -> PyResult<Vec<PyIntArray>> {
        match self.inner.sg_close_power() {
            Ok(result) => Ok(to_py_int_arrays(&result)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn sg_close_parallel(&mut self) -> PyResult<Vec<PyIntArray>> {
        match self.inner.sg_close_parallel() {
            Ok(result) => Ok(to_py_int_arrays(&result)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn get_term_map(&self, py: Python<'_>) -> PyResult<Option<PyObject>> {
        let Some(map) = self.inner.get_term_map() else {
            return Ok(None);
        };
        let dict = PyDict::new_bound(py);
        for (ia, term) in map {
            let key = Py::new(py, PyIntArray { inner: ia.clone() })?;
            dict.set_item(key, term_to_py(py, term.as_ref())?)?;
        }
        Ok(Some(dict.into()))
    }

    fn set_term_map(
        &mut self,
        py: Python<'_>,
        term_map: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<()> {
        match term_map {
            None => self.inner.set_term_map(None),
            Some(m) => self.inner.set_term_map(Some(py_term_map(py, m)?)),
        }
        Ok(())
    }

    fn set_suppress_output(&mut self, suppress: bool) {
        self.inner.set_suppress_output(suppress);
    }

    fn is_suppress_output(&self) -> bool {
        self.inner.is_suppress_output()
    }

    fn set_max_size(&mut self, max_size: Option<i32>) {
        self.inner
            .set_max_size(max_size.and_then(|k| if k < 0 { None } else { Some(k as usize) }));
    }

    fn get_max_size(&self) -> Option<usize> {
        self.inner.get_max_size()
    }

    fn is_completed(&self) -> bool {
        self.inner.is_completed()
    }

    fn get_element_to_find(&self) -> Option<PyIntArray> {
        self.inner
            .get_element_to_find()
            .map(|ia| PyIntArray { inner: ia.clone() })
    }

    fn set_element_to_find(&mut self, element: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
        match element {
            None => self.inner.set_element_to_find(None),
            Some(e) => self.inner.set_element_to_find(Some(extract_int_array(e)?)),
        }
        Ok(())
    }

    fn get_elements_to_find(&self) -> Option<Vec<PyIntArray>> {
        self.inner
            .get_elements_to_find()
            .map(|elts| to_py_int_arrays(elts))
    }

    fn set_elements_to_find(
        &mut self,
        elements: &Bound<'_, PyAny>,
        generators: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<()> {
        let rust_elts = extract_int_arrays(elements)?;
        let gens = match generators {
            Some(g) => extract_int_arrays(g)?,
            None => self.inner.get_generators().to_vec(),
        };
        self.inner.set_elements_to_find(rust_elts, &gens);
        Ok(())
    }

    fn all_elements_found(&self) -> bool {
        self.inner.all_elements_found()
    }

    fn get_blocks(&self) -> Option<Vec<Vec<usize>>> {
        self.inner.get_blocks().cloned()
    }

    fn set_blocks(&mut self, blocks: Option<Vec<Vec<usize>>>) {
        self.inner.set_blocks(blocks);
    }

    fn get_values(&self) -> Option<Vec<(usize, i32)>> {
        self.inner.get_values().cloned()
    }

    fn set_values(&mut self, values: Option<Vec<(usize, i32)>>) {
        self.inner.set_values(values);
    }

    fn get_set_constraint(&self) -> Option<HashSet<i32>> {
        self.inner.get_set_constraint().cloned()
    }

    fn set_constraint_set(&mut self, set: Option<HashSet<i32>>) {
        self.inner.set_constraint_set(set);
    }

    fn get_index_for_constraint_set(&self) -> Option<usize> {
        self.inner.get_index_for_constraint_set()
    }

    fn set_index_for_constraint_set(&mut self, index: Option<i32>) {
        self.inner.set_index_for_constraint_set(index.and_then(|k| {
            if k < 0 {
                None
            } else {
                Some(k as usize)
            }
        }));
    }

    fn get_index_for_congruence_constraint(&self) -> Option<usize> {
        self.inner.get_index_for_congruence_constraint()
    }

    fn set_index_for_congruence_constraint(&mut self, index: Option<i32>) {
        self.inner
            .set_index_for_congruence_constraint(index.map(|k| k as usize));
    }

    fn get_congruence_constraint_elem_index(&self) -> Option<usize> {
        self.inner.get_congruence_constraint_elem_index()
    }

    fn set_congruence_constraint_elem_index(&mut self, elem_index: Option<i32>) {
        self.inner
            .set_congruence_constraint_elem_index(elem_index.map(|k| k as usize));
    }

    fn get_congruence_for_congruence_constraint(&self) -> Option<PyPartition> {
        self.inner
            .get_congruence_for_congruence_constraint()
            .cloned()
            .map(PyPartition::from_inner)
    }

    fn set_congruence_for_congruence_constraint(&mut self, alpha: Option<&PyPartition>) {
        self.inner
            .set_congruence_for_congruence_constraint(alpha.map(|p| p.inner.clone()));
    }

    fn setup_congruence_constraint(
        &mut self,
        alpha: &PyPartition,
        index: usize,
        elem_index: usize,
    ) {
        self.inner
            .setup_congruence_constraint(alpha.inner.clone(), index, elem_index);
    }

    fn get_homomorphism(&self, py: Python<'_>) -> PyResult<Option<PyObject>> {
        let Some(map) = self.inner.get_homomorphism() else {
            return Ok(None);
        };
        let dict = PyDict::new_bound(py);
        for (ia, img) in map {
            let key = Py::new(py, PyIntArray { inner: ia.clone() })?;
            dict.set_item(key, *img)?;
        }
        Ok(Some(dict.into()))
    }

    fn set_homomorphism(&mut self, homomorphism: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
        match homomorphism {
            None => {
                self.inner.set_homomorphism(None);
                Ok(())
            }
            Some(obj) => {
                if let Ok(list) = obj.downcast::<PyList>() {
                    let gens: Vec<i32> = list.extract()?;
                    self.inner
                        .set_homomorphism_from_gens(gens)
                        .map_err(PyValueError::new_err)
                } else {
                    let mut rust_map = HashMap::new();
                    for item in obj.call_method0("items")?.iter()? {
                        let pair = item?;
                        let key = extract_int_array(&pair.get_item(0)?)?;
                        let val: i32 = pair.get_item(1)?.extract()?;
                        rust_map.insert(key, val);
                    }
                    self.inner.set_homomorphism(Some(rust_map));
                    Ok(())
                }
            }
        }
    }

    fn get_image_algebra(&self) -> PyResult<Option<crate::alg::PyBasicAlgebra>> {
        let Some(alg) = self.inner.get_image_algebra() else {
            return Ok(None);
        };
        Ok(Some(ops_to_basic_algebra(
            alg.name().to_string(),
            alg.cardinality(),
            alg.operations(),
        )?))
    }

    fn set_image_algebra(&mut self, alg: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
        match alg {
            None => {
                self.inner
                    .set_image_algebra(None)
                    .map_err(PyValueError::new_err)?;
                Ok(())
            }
            Some(obj) => {
                let boxed = extract_boxed_small_algebra(obj)?;
                self.inner
                    .set_image_algebra(Some(Arc::from(boxed)))
                    .map_err(PyValueError::new_err)?;
                Ok(())
            }
        }
    }

    fn get_failing_equation(&self) -> Option<PyEquation> {
        self.inner
            .get_failing_equation()
            .cloned()
            .map(|inner| PyEquation { inner })
    }

    fn get_term_map_for_operations(&self, py: Python<'_>) -> PyResult<Option<PyObject>> {
        let Some(map) = self.inner.get_term_map_for_operations() else {
            return Ok(None);
        };
        let dict = PyDict::new_bound(py);
        for (sym, term) in map {
            dict.set_item(sym.name(), term_to_py(py, term.as_ref())?)?;
        }
        Ok(Some(dict.into()))
    }

    fn set_root_algebra(&mut self, alg: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
        match alg {
            None => self.inner.set_root_algebra(None),
            Some(obj) => {
                let boxed = extract_boxed_small_algebra(obj)?;
                self.inner.set_root_algebra(Some(Arc::from(boxed)));
            }
        }
        Ok(())
    }

    fn set_operations(&mut self, operations: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
        match operations {
            None => {
                self.inner.set_operations(None);
                Ok(())
            }
            Some(ops) => {
                let mut rust_ops = Vec::new();
                for item in ops.iter()? {
                    let item = item?;
                    if let Ok(op) =
                        item.extract::<PyRef<crate::alg::op::int_operation::PyIntOperation>>()
                    {
                        rust_ops.push(Arc::new(op.inner.clone())
                            as Arc<dyn uacalc::alg::op::Operation>);
                    } else {
                        return Err(PyValueError::new_err(
                            "setOperations expects IntOperation values",
                        ));
                    }
                }
                self.inner.set_operations(Some(rust_ops));
                Ok(())
            }
        }
    }

    fn __str__(&self) -> String {
        format!(
            "Closer(generators: {}, answer_size: {})",
            self.inner.get_generators().len(),
            self.inner.get_answer().len()
        )
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }
}

fn py_term_map(
    _py: Python<'_>,
    term_map: &Bound<'_, PyAny>,
) -> PyResult<HashMap<IntArray, Box<dyn Term>>> {
    let mut rust_map = HashMap::new();
    for item in term_map.call_method0("items")?.iter()? {
        let pair = item?;
        let key = extract_int_array(&pair.get_item(0)?)?;
        let term = py_to_term(&pair.get_item(1)?)?;
        rust_map.insert(key, term);
    }
    Ok(rust_map)
}

pub fn register_closer(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyCloser>()?;
    Ok(())
}
