use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict};
use uacalc::alg::SubProductAlgebra;
use uacalc::terms::Term;
use uacalc::util::int_array::IntArray;

use crate::alg::convert::term_to_py;
use crate::alg::free_algebra::PyFreeAlgebra;
use crate::alg::sub_product_algebra::{extract_int_array, PySubProductAlgebra};
use crate::terms::PyVariableImp;
use crate::util::PyIntArray;

/// Java `org.uacalc.element.Element` interface (not constructible from scripts).
#[pyclass(name = "Element", subclass)]
pub struct PyElement {}

#[pymethods]
impl PyElement {
    #[new]
    fn new() -> PyResult<Self> {
        Err(PyValueError::new_err(
            "org.uacalc.element.Element is an interface and cannot be instantiated",
        ))
    }
}

/// Java `org.uacalc.element.SubProductElement`.
#[pyclass(name = "SubProductElement")]
pub struct PySubProductElement {
    element: IntArray,
    algebra: PyObject,
}

fn with_subproduct<F, R>(py: Python<'_>, alg: &PyObject, f: F) -> PyResult<R>
where
    F: FnOnce(&SubProductAlgebra<i32>) -> PyResult<R>,
{
    if alg.is_none(py) {
        return Err(PyValueError::new_err("null"));
    }
    let bound = alg.bind(py);
    if let Ok(sp) = bound.extract::<PyRef<PySubProductAlgebra>>() {
        return f(sp.as_inner());
    }
    if let Ok(fa) = bound.extract::<PyRef<PyFreeAlgebra>>() {
        return f(fa.as_inner().get_inner());
    }
    Err(PyValueError::new_err(
        "SubProductElement algebra must be a SubProductAlgebra or FreeAlgebra",
    ))
}

fn array_string(ia: &IntArray) -> String {
    ia.to_string()
}

#[pymethods]
impl PySubProductElement {
    #[new]
    fn new(elt: &Bound<'_, PyAny>, alg: PyObject) -> PyResult<Self> {
        Ok(PySubProductElement {
            element: extract_int_array(elt)?,
            algebra: alg,
        })
    }

    fn get_algebra(&self, py: Python<'_>) -> PyObject {
        self.algebra.clone_ref(py)
    }

    fn index(&self, py: Python<'_>) -> PyResult<i32> {
        with_subproduct(py, &self.algebra, |alg| {
            alg.element_index(&self.element)
                .map(|i| i as i32)
                .ok_or_else(|| PyValueError::new_err("null"))
        })
    }

    fn get_term(&self, py: Python<'_>) -> PyResult<Option<PyObject>> {
        with_subproduct(py, &self.algebra, |alg| match alg.get_term(&self.element) {
            Some(term) => Ok(Some(term_to_py(py, term)?)),
            None => Ok(None),
        })
    }

    fn get_variable_list(&self, py: Python<'_>) -> PyResult<Vec<PyVariableImp>> {
        with_subproduct(py, &self.algebra, |alg| {
            let term = alg
                .get_term(&self.element)
                .ok_or_else(|| PyValueError::new_err("null"))?;
            Ok(term
                .get_variable_list()
                .into_iter()
                .map(|name| PyVariableImp {
                    inner: uacalc::terms::VariableImp::new(&name),
                })
                .collect())
        })
    }

    fn get_variable_map(&self, py: Python<'_>) -> PyResult<PyObject> {
        with_subproduct(py, &self.algebra, |alg| {
            let term: &dyn Term = alg
                .get_term(&self.element)
                .ok_or_else(|| PyValueError::new_err("null"))?;
            let vars_map = alg
                .get_variable_to_generator_map()
                .ok_or_else(|| PyValueError::new_err("null"))?;
            let dict = PyDict::new_bound(py);
            for name in term.get_variable_list() {
                let var = uacalc::terms::VariableImp::new(&name);
                let key = Py::new(py, PyVariableImp { inner: var.clone() })?;
                match vars_map.get(&var) {
                    Some(ia) => {
                        let val = Py::new(py, PyIntArray { inner: ia.clone() })?;
                        dict.set_item(key, val)?;
                    }
                    None => {
                        dict.set_item(key, py.None())?;
                    }
                }
            }
            Ok(dict.to_object(py))
        })
    }

    fn get_parent(&self, py: Python<'_>) -> PyObject {
        py.None()
    }

    fn get_parent_array(&self, py: Python<'_>) -> PyObject {
        py.None()
    }

    fn parent_index_array(&self, py: Python<'_>) -> PyObject {
        py.None()
    }

    fn __str__(&self, py: Python<'_>) -> PyResult<String> {
        with_subproduct(py, &self.algebra, |alg| {
            let mut sb = array_string(&self.element);
            if let Some(term) = alg.get_term(&self.element) {
                let vars_map = alg
                    .get_variable_to_generator_map()
                    .ok_or_else(|| PyValueError::new_err("null"))?;
                sb.push_str(", term: ");
                sb.push_str(&term.to_string());
                sb.push_str(" under ");
                for name in term.get_variable_list() {
                    sb.push_str(&name);
                    sb.push_str(" -> ");
                    match vars_map.get(&uacalc::terms::VariableImp::new(&name)) {
                        Some(ia) => sb.push_str(&array_string(ia)),
                        None => sb.push_str("null"),
                    }
                    sb.push_str(", ");
                }
            }
            Ok(sb)
        })
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        self.__str__(py)
    }
}

pub fn register_element_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyElement>()?;
    m.add_class::<PySubProductElement>()?;
    Ok(())
}
