use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyAny;
use std::collections::HashMap;
use std::sync::atomic::AtomicUsize;
use std::sync::{Arc, Mutex};
use uacalc::alg::op::Operation;
use uacalc::alg::parallel::{Pool, SingleClose};
use uacalc::terms::{Term, VariableImp};
use uacalc::util::IntArray;

use crate::alg::op::int_operation::PyIntOperation;
use crate::alg::op::operation::PyBasicOperation;
use crate::util::PyIntArray;

/// Python wrapper for Pool
#[pyclass]
pub struct PyPool;

#[pymethods]
impl PyPool {
    #[new]
    fn new() -> Self {
        PyPool
    }

    /// Get the ForkJoinPool-equivalent runtime.
    ///
    /// Returns a reference to the lazily initialized, thread-safe runtime.
    /// This is equivalent to accessing Java's Pool.fjPool static field.
    #[staticmethod]
    fn fj_pool() -> PyResult<String> {
        let _runtime = Pool::fj_pool();
        Ok("initialized".to_string())
    }

    /// Check if the pool is initialized.
    #[staticmethod]
    fn is_initialized() -> bool {
        let _runtime = Pool::fj_pool();
        true
    }

    fn __str__(&self) -> String {
        "Pool()".to_string()
    }

    fn __repr__(&self) -> String {
        "Pool()".to_string()
    }
}

fn extract_int_array(elem: &Bound<'_, PyAny>) -> PyResult<IntArray> {
    if let Ok(ia) = elem.extract::<PyRef<PyIntArray>>() {
        return Ok(ia.inner.clone());
    }
    let vals: Vec<i32> = elem.extract()?;
    IntArray::from_array(vals).map_err(PyValueError::new_err)
}

fn extract_int_arrays(gens: &Bound<'_, PyAny>) -> PyResult<Vec<IntArray>> {
    let mut out = Vec::new();
    for item in gens.iter()? {
        out.push(extract_int_array(&item?)?);
    }
    Ok(out)
}

fn extract_dyn_op(op: &Bound<'_, PyAny>) -> PyResult<Arc<dyn Operation>> {
    if let Ok(o) = op.extract::<PyRef<PyBasicOperation>>() {
        return Ok(Arc::new(o.inner.clone()) as Arc<dyn Operation>);
    }
    if let Ok(o) = op.extract::<PyRef<PyIntOperation>>() {
        return Ok(Arc::new(o.inner.clone()) as Arc<dyn Operation>);
    }
    // Algebra operations() may return a wrapped facade; try inner attributes.
    for attr in ["_inner", "inner", "_op"] {
        if let Ok(inner) = op.getattr(attr) {
            if inner.is(op) {
                continue;
            }
            if let Ok(arc) = extract_dyn_op(&inner) {
                return Ok(arc);
            }
        }
    }
    Err(PyValueError::new_err(
        "SingleClose expects a BasicOperation or IntOperation",
    ))
}

fn dummy_term_map(univ: &[IntArray]) -> Arc<Mutex<HashMap<IntArray, Box<dyn Term>>>> {
    let mut map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
    for (i, ia) in univ.iter().enumerate() {
        map.insert(
            ia.clone(),
            Box::new(VariableImp::new(&format!("x{i}"))) as Box<dyn Term>,
        );
    }
    Arc::new(Mutex::new(map))
}

fn extract_elts_found(elts_found: &Bound<'_, PyAny>, fallback: usize) -> usize {
    if let Ok(i) = elts_found.extract::<i64>() {
        return i.max(0) as usize;
    }
    if let Ok(got) = elts_found.call_method0("get") {
        if let Ok(i) = got.extract::<i64>() {
            return i.max(0) as usize;
        }
    }
    fallback
}

/// Python wrapper for SingleClose (one parallel closure pass).
#[pyclass]
pub struct PySingleClose {
    inner: Option<SingleClose>,
}

#[pymethods]
impl PySingleClose {
    /// Java ``SingleClose(univList, map, op, min, max, eltsFound)``.
    ///
    /// ``map`` may be a dict (keys used; terms rebuilt) or None (dummy terms
    /// for the universe). ``eltsFound`` may be an int or an object with ``get()``.
    #[new]
    #[pyo3(signature = (univ_list, map, op, min, max, elts_found, _inc=None))]
    fn new(
        univ_list: &Bound<'_, PyAny>,
        map: Option<&Bound<'_, PyAny>>,
        op: &Bound<'_, PyAny>,
        min: usize,
        max: usize,
        elts_found: &Bound<'_, PyAny>,
        _inc: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Self> {
        let univ = extract_int_arrays(univ_list)?;
        if univ.is_empty() {
            return Err(PyValueError::new_err("univList must be non-empty"));
        }
        let rust_op = extract_dyn_op(op)?;
        let n = extract_elts_found(elts_found, univ.len());
        let term_map = if let Some(m) = map {
            if m.is_none() {
                dummy_term_map(&univ)
            } else if let Ok(items) = m.call_method0("items") {
                let mut rust_map: HashMap<IntArray, Box<dyn Term>> = HashMap::new();
                for item in items.iter()? {
                    let pair = item?;
                    let key = extract_int_array(&pair.get_item(0)?)?;
                    rust_map.insert(
                        key.clone(),
                        Box::new(VariableImp::new("t")) as Box<dyn Term>,
                    );
                }
                if rust_map.is_empty() {
                    dummy_term_map(&univ)
                } else {
                    for ia in &univ {
                        rust_map
                            .entry(ia.clone())
                            .or_insert_with(|| Box::new(VariableImp::new("t")) as Box<dyn Term>);
                    }
                    Arc::new(Mutex::new(rust_map))
                }
            } else {
                dummy_term_map(&univ)
            }
        } else {
            dummy_term_map(&univ)
        };
        let inner = SingleClose::new(
            univ,
            term_map,
            rust_op,
            min,
            max,
            Arc::new(AtomicUsize::new(n)),
        )
        .map_err(PyValueError::new_err)?;
        Ok(PySingleClose { inner: Some(inner) })
    }

    /// Java ``doOneStep(pool, callingThread, report, timing)``.
    ///
    /// Pool / thread / ProgressReport / CloserTiming are accepted and ignored;
    /// timing and thread counts are not part of the deterministic API.
    #[pyo3(signature = (pool=None, calling_thread=None, report=None, timing=None))]
    fn do_one_step(
        &mut self,
        pool: Option<&Bound<'_, PyAny>>,
        calling_thread: Option<&Bound<'_, PyAny>>,
        report: Option<&Bound<'_, PyAny>>,
        timing: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Vec<Vec<PyIntArray>>> {
        let _ = (pool, calling_thread, report, timing);
        let inner = self
            .inner
            .as_mut()
            .ok_or_else(|| PyValueError::new_err("SingleClose is not initialized"))?;
        let results = inner
            .do_one_step(None, None)
            .map_err(PyValueError::new_err)?;
        Ok(results
            .into_iter()
            .map(|chunk| {
                chunk
                    .into_iter()
                    .map(|ia| PyIntArray { inner: ia })
                    .collect()
            })
            .collect())
    }

    fn __str__(&self) -> String {
        "SingleClose()".to_string()
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }
}

pub fn register_parallel_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPool>()?;
    m.add_class::<PySingleClose>()?;

    m.add("Pool", m.getattr("PyPool")?)?;
    m.add("SingleClose", m.getattr("PySingleClose")?)?;

    let module_dict = m.dict();
    module_dict.del_item("PyPool")?;
    module_dict.del_item("PySingleClose")?;

    Ok(())
}
