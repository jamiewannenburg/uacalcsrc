use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::util::IntArrayTrait;
use uacalc::alg::conlat::Subtrace;

/// Python wrapper for Subtrace
#[pyclass]
pub struct PySubtrace {
    inner: Subtrace,
}

#[pymethods]
impl PySubtrace {
    /// Create a new Subtrace with given elements and involution flag.
    ///
    /// Args:
    ///     a (int): First element of the subtrace pair
    ///     b (int): Second element of the subtrace pair
    ///     has_involution (bool): Whether this subtrace has involution
    ///
    /// Returns:
    ///     Subtrace: A new Subtrace instance with type set to -1
    #[new]
    fn new(a: i32, b: i32, has_involution: bool) -> Self {
        PySubtrace {
            inner: Subtrace::new(a, b, has_involution)
        }
    }

    /// Create a new Subtrace with given elements, involution flag, and type.
    ///
    /// Args:
    ///     a (int): First element of the subtrace pair
    ///     b (int): Second element of the subtrace pair
    ///     has_involution (bool): Whether this subtrace has involution
    ///     type_value (int): TCT type classification
    ///
    /// Returns:
    ///     Subtrace: A new Subtrace instance with the specified type
    #[staticmethod]
    fn new_with_type(a: i32, b: i32, has_involution: bool, type_value: i32) -> Self {
        PySubtrace {
            inner: Subtrace::new_with_type(a, b, has_involution, type_value)
        }
    }

    /// Get the first element of the subtrace pair.
    ///
    /// Returns:
    ///     int: The first element `a`
    fn first(&self) -> i32 {
        self.inner.first()
    }

    /// Get the second element of the subtrace pair.
    ///
    /// Returns:
    ///     int: The second element `b`
    fn second(&self) -> i32 {
        self.inner.second()
    }

    /// Get the TCT type classification.
    ///
    /// Returns:
    ///     int: The type value (-1 if not set)
    fn type_value(&self) -> i32 {
        self.inner.type_value()
    }

    /// Get the TCT type classification (alias for type_value).
    ///
    /// Returns:
    ///     int: The type value (-1 if not set)
    fn r#type(&self) -> i32 {
        self.inner.type_value()
    }

    /// Check if this subtrace has involution.
    ///
    /// Returns:
    ///     bool: True if the subtrace has involution, False otherwise
    fn has_involution(&self) -> bool {
        self.inner.has_involution()
    }

    /// Set the TCT type classification.
    ///
    /// Args:
    ///     type_value (int): The type to set
    fn set_type(&mut self, type_value: i32) {
        self.inner.set_type(type_value);
    }

    /// Get the subtrace universe.
    ///
    /// Returns:
    ///     List[List[int]] or None: The subtrace universe as list of pairs, or None if not set
    fn get_subtrace_universe(&self) -> Option<Vec<Vec<i32>>> {
        self.inner.get_subtrace_universe().map(|universe| {
            universe.iter().map(|int_array| {
                let mut vec = Vec::new();
                for i in 0..int_array.universe_size() {
                    vec.push(int_array.get(i).unwrap());
                }
                vec
            }).collect()
        })
    }

    /// Set the subtrace universe.
    ///
    /// Args:
    ///     universe (List[List[int]]): The subtrace universe to set
    ///
    /// Raises:
    ///     ValueError: If any array doesn't have exactly 2 elements
    fn set_subtrace_universe(&mut self, universe: Vec<Vec<i32>>) -> PyResult<()> {
        let int_arrays: Result<Vec<_>, _> = universe.iter()
            .map(|arr| {
                if arr.len() != 2 {
                    Err(format!("Each subtrace universe element must have exactly 2 elements, got {}", arr.len()))
                } else {
                    Ok(uacalc::util::int_array::IntArray::from_array(arr.clone()).unwrap())
                }
            })
            .collect();

        match int_arrays {
            Ok(arrays) => {
                self.inner.set_subtrace_universe(arrays);
                Ok(())
            }
            Err(e) => Err(PyValueError::new_err(e))
        }
    }

    /// Get the matrix universe.
    ///
    /// Returns:
    ///     List[List[int]] or None: The matrix universe as list of 4-tuples, or None if not set
    fn get_matrix_universe(&self) -> Option<Vec<Vec<i32>>> {
        self.inner.get_matrix_universe().map(|universe| {
            universe.iter().map(|int_array| {
                let mut vec = Vec::new();
                for i in 0..int_array.universe_size() {
                    vec.push(int_array.get(i).unwrap());
                }
                vec
            }).collect()
        })
    }

    /// Set the matrix universe.
    ///
    /// Args:
    ///     universe (List[List[int]]): The matrix universe to set
    ///
    /// Raises:
    ///     ValueError: If any array doesn't have exactly 4 elements
    fn set_matrix_universe(&mut self, universe: Vec<Vec<i32>>) -> PyResult<()> {
        let int_arrays: Result<Vec<_>, _> = universe.iter()
            .map(|arr| {
                if arr.len() != 4 {
                    Err(format!("Each matrix universe element must have exactly 4 elements, got {}", arr.len()))
                } else {
                    Ok(uacalc::util::int_array::IntArray::from_array(arr.clone()).unwrap())
                }
            })
            .collect();

        match int_arrays {
            Ok(arrays) => {
                self.inner.set_matrix_universe(arrays);
                Ok(())
            }
            Err(e) => Err(PyValueError::new_err(e))
        }
    }

    /// Get a string representation in brief format.
    ///
    /// Args:
    ///     brief (bool): If True, returns brief format [a, b], otherwise full format
    ///
    /// Returns:
    ///     str: String representation of the subtrace
    fn to_string_brief(&self, brief: bool) -> String {
        self.inner.to_string_brief(brief)
    }

    /// Python string representation.
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("Subtrace({}, {}, {}, {})",
                self.inner.first(),
                self.inner.second(),
                self.inner.has_involution(),
                self.inner.type_value())
    }

    /// Python equality comparison.
    fn __eq__(&self, other: &PySubtrace) -> bool {
        self.inner == other.inner
    }

    /// Python hash function.
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }

    /// Python comparison (less than).
    fn __lt__(&self, other: &PySubtrace) -> bool {
        self.inner < other.inner
    }

    /// Python comparison (less than or equal).
    fn __le__(&self, other: &PySubtrace) -> bool {
        self.inner <= other.inner
    }

    /// Python comparison (greater than).
    fn __gt__(&self, other: &PySubtrace) -> bool {
        self.inner > other.inner
    }

    /// Python comparison (greater than or equal).
    fn __ge__(&self, other: &PySubtrace) -> bool {
        self.inner >= other.inner
    }
}

impl PySubtrace {
    pub(crate) fn from_inner(inner: Subtrace) -> Self { PySubtrace { inner } }
    pub(crate) fn get_inner(&self) -> &Subtrace { &self.inner }
}