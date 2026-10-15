//! Extract `SmallAlgebra<i32>` trait objects from Python algebra wrappers.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyAny;
use uacalc::alg::SmallAlgebra;

use crate::alg::basic_algebra::PyBasicAlgebra;
use crate::alg::power_algebra::PyPowerAlgebra;
use crate::alg::product_algebra::PyProductAlgebra;

pub fn extract_boxed_small_algebra(
    obj: &Bound<'_, PyAny>,
) -> PyResult<Box<dyn SmallAlgebra<UniverseItem = i32>>> {
    if let Ok(alg) = obj.extract::<PyRef<PyBasicAlgebra>>() {
        return Ok(Box::new(alg.inner.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>);
    }
    if let Ok(inner) = obj.getattr("_inner") {
        if let Ok(alg) = inner.extract::<PyRef<PyBasicAlgebra>>() {
            return Ok(Box::new(alg.inner.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>);
        }
        if let Ok(prod) = inner.extract::<PyRef<PyProductAlgebra>>() {
            return Ok(Box::new(prod.clone_inner()) as Box<dyn SmallAlgebra<UniverseItem = i32>>);
        }
        if let Ok(pow) = inner.extract::<PyRef<PyPowerAlgebra>>() {
            return Ok(Box::new(pow.clone_inner()) as Box<dyn SmallAlgebra<UniverseItem = i32>>);
        }
    }
    if let Ok(prod) = obj.extract::<PyRef<PyProductAlgebra>>() {
        return Ok(Box::new(prod.clone_inner()) as Box<dyn SmallAlgebra<UniverseItem = i32>>);
    }
    if let Ok(pow) = obj.extract::<PyRef<PyPowerAlgebra>>() {
        return Ok(Box::new(pow.clone_inner()) as Box<dyn SmallAlgebra<UniverseItem = i32>>);
    }
    Err(PyValueError::new_err(format!(
        "expected SmallAlgebra, got {}",
        obj.get_type().name()?
    )))
}

pub fn extract_basic_algebra(obj: &Bound<'_, PyAny>) -> PyResult<uacalc::alg::BasicAlgebra<i32>> {
    if let Ok(alg) = obj.extract::<PyRef<PyBasicAlgebra>>() {
        return Ok(alg.inner.clone());
    }
    if let Ok(inner) = obj.getattr("_inner") {
        if let Ok(alg) = inner.extract::<PyRef<PyBasicAlgebra>>() {
            return Ok(alg.inner.clone());
        }
    }
    Err(PyValueError::new_err("expected BasicAlgebra"))
}
