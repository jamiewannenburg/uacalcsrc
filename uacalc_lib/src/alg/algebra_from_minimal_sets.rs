use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyList;
use uacalc::alg::*;
use crate::alg::PyBasicAlgebra;

/// Python wrapper for AlgebraFromMinimalSets
#[pyclass]
pub struct PyAlgebraFromMinimalSets {
    inner: uacalc::alg::AlgebraFromMinimalSets,
}

impl PyAlgebraFromMinimalSets {
    /// Create PyAlgebraFromMinimalSets from inner Rust type (not exposed to Python)
    pub fn from_inner(inner: uacalc::alg::AlgebraFromMinimalSets) -> Self {
        PyAlgebraFromMinimalSets { inner }
    }
}

#[pymethods]
impl PyAlgebraFromMinimalSets {
    /// Create a new AlgebraFromMinimalSets with default size (3 * minAlgSize - 2).
    ///
    /// Args:
    ///     min_algebra (BasicAlgebra): The minimal algebra B
    ///
    /// Returns:
    ///     AlgebraFromMinimalSets: A new AlgebraFromMinimalSets instance
    ///
    /// Raises:
    ///     ValueError: If there's an error creating the algebra
    #[new]
    fn new(min_algebra: &PyBasicAlgebra) -> PyResult<Self> {
        let min_alg_box = min_algebra.clone_box();
        match AlgebraFromMinimalSets::new(min_alg_box) {
            Ok(inner) => Ok(PyAlgebraFromMinimalSets { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new AlgebraFromMinimalSets with explicit size and maps.
    ///
    /// Args:
    ///     min_algebra (BasicAlgebra): The minimal algebra B
    ///     alg_size (int): The size of the constructed algebra
    ///     maps (Optional[List[List[int]]]): Optional list of maps (if None, default maps are created)
    ///
    /// Returns:
    ///     AlgebraFromMinimalSets: A new AlgebraFromMinimalSets instance
    ///
    /// Raises:
    ///     ValueError: If there's an error creating the algebra
    #[staticmethod]
    #[pyo3(signature = (min_algebra, alg_size, maps=None))]
    fn new_with_size(
        min_algebra: &PyBasicAlgebra,
        alg_size: usize,
        maps: Option<&Bound<'_, PyList>>
    ) -> PyResult<Self> {
        let min_alg_box = min_algebra.clone_box();
        let maps_opt = if let Some(maps_list) = maps {
            let mut maps_vec = Vec::new();
            for item in maps_list.iter() {
                let map_list: &Bound<'_, PyList> = item.downcast()?;
                let mut map_vec = Vec::new();
                for val in map_list.iter() {
                    map_vec.push(val.extract::<i32>()?);
                }
                maps_vec.push(map_vec);
            }
            Some(maps_vec)
        } else {
            None
        };
        
        match AlgebraFromMinimalSets::new_with_size(min_alg_box, alg_size, maps_opt) {
            Ok(inner) => Ok(PyAlgebraFromMinimalSets { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new AlgebraFromMinimalSets with a name.
    ///
    /// Args:
    ///     min_algebra (BasicAlgebra): The minimal algebra B
    ///     name (Optional[str]): Optional name for the algebra
    ///
    /// Returns:
    ///     AlgebraFromMinimalSets: A new AlgebraFromMinimalSets instance
    ///
    /// Raises:
    ///     ValueError: If there's an error creating the algebra
    #[staticmethod]
    #[pyo3(signature = (min_algebra, name=None))]
    fn new_with_name(
        min_algebra: &PyBasicAlgebra,
        name: Option<String>
    ) -> PyResult<Self> {
        let min_alg_box = min_algebra.clone_box();
        match AlgebraFromMinimalSets::new_with_name(name, min_alg_box) {
            Ok(inner) => Ok(PyAlgebraFromMinimalSets { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new AlgebraFromMinimalSets with connecting points.
    ///
    /// Args:
    ///     min_algebra (BasicAlgebra): The minimal algebra B
    ///     name (Optional[str]): Optional name for the algebra
    ///     connect_pts (Optional[List[int]]): Optional connecting points [a, b]
    ///
    /// Returns:
    ///     AlgebraFromMinimalSets: A new AlgebraFromMinimalSets instance
    ///
    /// Raises:
    ///     ValueError: If there's an error creating the algebra
    #[staticmethod]
    #[pyo3(signature = (min_algebra, name=None, connect_pts=None))]
    fn new_with_connecting_pts(
        min_algebra: &PyBasicAlgebra,
        name: Option<String>,
        connect_pts: Option<Vec<i32>>
    ) -> PyResult<Self> {
        let min_alg_box = min_algebra.clone_box();
        match AlgebraFromMinimalSets::new_with_connecting_pts(name, min_alg_box, connect_pts) {
            Ok(inner) => Ok(PyAlgebraFromMinimalSets { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new AlgebraFromMinimalSets with all parameters.
    ///
    /// Args:
    ///     min_algebra (BasicAlgebra): A permutational algebra (the minimal algebra B)
    ///     alg_size (int): The size of the constructed algebra
    ///     name (Optional[str]): Optional name for the algebra
    ///     maps (Optional[List[List[int]]]): Optional list of maps (if None, default maps are created)
    ///     connect_pts (Optional[List[int]]): Optional connecting points [a, b]
    ///
    /// Returns:
    ///     AlgebraFromMinimalSets: A new AlgebraFromMinimalSets instance
    ///
    /// Raises:
    ///     ValueError: If there's an error creating the algebra
    #[staticmethod]
    #[pyo3(signature = (min_algebra, alg_size, name=None, maps=None, connect_pts=None))]
    fn new_full(
        min_algebra: &PyBasicAlgebra,
        alg_size: usize,
        name: Option<String>,
        maps: Option<&Bound<'_, PyList>>,
        connect_pts: Option<Vec<i32>>
    ) -> PyResult<Self> {
        let min_alg_box = min_algebra.clone_box();
        let maps_opt = if let Some(maps_list) = maps {
            let mut maps_vec = Vec::new();
            for item in maps_list.iter() {
                let map_list: &Bound<'_, PyList> = item.downcast()?;
                let mut map_vec = Vec::new();
                for val in map_list.iter() {
                    map_vec.push(val.extract::<i32>()?);
                }
                maps_vec.push(map_vec);
            }
            Some(maps_vec)
        } else {
            None
        };
        
        match AlgebraFromMinimalSets::new_full(name, min_alg_box, alg_size, maps_opt, connect_pts) {
            Ok(inner) => Ok(PyAlgebraFromMinimalSets { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the name of this algebra.
    ///
    /// Returns:
    ///     str: The name of the algebra
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    /// Set the name of this algebra.
    ///
    /// Args:
    ///     name (str): The new name for the algebra
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }
    
    /// Get the cardinality of this algebra.
    ///
    /// Returns:
    ///     int: The cardinality of the algebra
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }
    
    /// Get the k-th element of the universe.
    ///
    /// Args:
    ///     k (int): The index of the element to retrieve
    ///
    /// Returns:
    ///     int: The element at index k, or None if k is out of bounds
    fn get_element(&self, k: usize) -> Option<i32> {
        self.inner.get_element(k)
    }
    
    /// Get the index of an element in the universe.
    ///
    /// Args:
    ///     elem (int): The element to find the index for
    ///
    /// Returns:
    ///     int: The index of the element, or None if not found
    fn element_index(&self, elem: i32) -> Option<usize> {
        self.inner.element_index(&elem)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("AlgebraFromMinimalSets({})", self.inner.name())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyAlgebraFromMinimalSets) -> bool {
        // Compare by name and cardinality for now
        self.inner.name() == other.inner.name() && 
        self.inner.cardinality() == other.inner.cardinality()
    }
}

impl Clone for PyAlgebraFromMinimalSets {
    fn clone(&self) -> Self {
        PyAlgebraFromMinimalSets {
            inner: self.inner.clone(),
        }
    }
}

