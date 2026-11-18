use pyo3::exceptions::{PyKeyboardInterrupt, PyMemoryError, PyTimeoutError, PyValueError};
use pyo3::prelude::*;
use std::sync::Once;
use std::time::Duration;
use uacalc::resource::{self, set_signal_hook, UaError};

static SIGNAL_HOOK_ONCE: Once = Once::new();

fn install_signal_hook() {
    SIGNAL_HOOK_ONCE.call_once(|| {
        set_signal_hook(Some(Box::new(|| {
            Python::with_gil(|py| py.check_signals().map_err(|_| UaError::Interrupted))
        })));
    });
}

/// Map [`UaError`] to the appropriate Python exception (PyO3 0.21).
pub fn ua_to_py(err: UaError, py: Python<'_>) -> PyErr {
    match err {
        UaError::Memory { used, limit } => {
            PyMemoryError::new_err(format!("memory limit exceeded: used {used}, limit {limit}"))
        }
        UaError::ElementLimit { count, limit } => PyMemoryError::new_err(format!(
            "element limit exceeded: kept {count}, limit {limit}"
        )),
        UaError::Interrupted => PyKeyboardInterrupt::new_err("computation interrupted"),
        UaError::TimeLimit => PyTimeoutError::new_err("time limit exceeded"),
        UaError::Message(s) => PyValueError::new_err(s),
    }
}

#[pyfunction]
#[pyo3(signature = (limit=None))]
fn set_memory_limit(limit: Option<u64>) -> PyResult<()> {
    install_signal_hook();
    resource::set_memory_limit(limit);
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (limit=None))]
fn set_element_limit(limit: Option<u64>) -> PyResult<()> {
    install_signal_hook();
    resource::set_element_limit(limit);
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (seconds=None))]
fn set_time_limit(seconds: Option<f64>) -> PyResult<()> {
    install_signal_hook();
    let dur = seconds.map(Duration::from_secs_f64);
    resource::set_time_limit(dur);
    Ok(())
}

#[pyfunction]
fn cancel() -> PyResult<()> {
    resource::request_cancel();
    Ok(())
}


#[pyfunction]
fn clear_cancel() -> PyResult<()> {
    resource::clear_cancel();
    Ok(())
}

pub fn register(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    install_signal_hook();
    m.add_function(wrap_pyfunction!(set_memory_limit, m)?)?;
    m.add_function(wrap_pyfunction!(set_element_limit, m)?)?;
    m.add_function(wrap_pyfunction!(set_time_limit, m)?)?;
    m.add_function(wrap_pyfunction!(cancel, m)?)?;
    m.add_function(wrap_pyfunction!(clear_cancel, m)?)?;
    Ok(())
}