use std::sync::Arc;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

/// Stable Python-facing labels for a dense Rust universe `0..n`.
///
/// The Rust core never owns Python objects. Bindings share this sidecar across
/// algebra and operation wrappers so algorithms use integers while values
/// crossing the Python boundary retain their original representation.
#[derive(Clone, Debug)]
pub(crate) struct PyUniverseMap {
    labels: Arc<Vec<PyObject>>,
}

impl PyUniverseMap {
    pub(crate) fn from_objects(
        py: Python<'_>,
        labels: Vec<PyObject>,
        deduplicate: bool,
    ) -> PyResult<Self> {
        if !deduplicate {
            return Ok(Self {
                labels: Arc::new(labels),
            });
        }

        let mut unique = Vec::with_capacity(labels.len());
        for label in labels {
            let duplicate = unique
                .iter()
                .try_fold(false, |found, existing: &PyObject| {
                    if found {
                        Ok(true)
                    } else {
                        label.bind(py).eq(existing.bind(py))
                    }
                })?;
            if !duplicate {
                unique.push(label);
            }
        }
        Ok(Self {
            labels: Arc::new(unique),
        })
    }

    pub(crate) fn len(&self) -> usize {
        self.labels.len()
    }

    pub(crate) fn is_empty(&self) -> bool {
        self.labels.is_empty()
    }

    pub(crate) fn labels(&self) -> &[PyObject] {
        self.labels.as_slice()
    }

    pub(crate) fn labels_owned(&self) -> Vec<PyObject> {
        self.labels.as_ref().clone()
    }

    pub(crate) fn is_dense_integer_identity(&self, py: Python<'_>) -> bool {
        self.labels.iter().enumerate().all(|(index, label)| {
            matches!(
                label.bind(py).extract::<i32>(),
                Ok(value) if value == index as i32
            )
        })
    }

    pub(crate) fn element(&self, index: usize) -> Option<PyObject> {
        self.labels.get(index).cloned()
    }

    pub(crate) fn element_or_error(
        &self,
        index: i32,
        context: &str,
    ) -> PyResult<PyObject> {
        if index < 0 {
            return Err(PyValueError::new_err(format!(
                "{} index {} is negative",
                context, index
            )));
        }
        self.element(index as usize).ok_or_else(|| {
            PyValueError::new_err(format!(
                "{} index {} is out of range [0, {})",
                context,
                index,
                self.len()
            ))
        })
    }

    pub(crate) fn index_of(
        &self,
        py: Python<'_>,
        value: &Bound<'_, PyAny>,
    ) -> PyResult<Option<usize>> {
        for (index, label) in self.labels.iter().enumerate() {
            if value.eq(label.bind(py))? {
                return Ok(Some(index));
            }
        }
        Ok(None)
    }
}
