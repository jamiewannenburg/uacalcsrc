/// Python wrapper for SmallAlgebra (simplified for bindings)
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::BasicSmallAlgebra;
use uacalc::alg::SmallAlgebra;
use uacalc::util::IntArray;
use crate::alg::PyBasicSmallAlgebra;

pub fn register_small_algebra(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PySmallAlgebra>()?;
    m.add_class::<PySubalgebraLattice>()?;
    Ok(())
}

/// Python wrapper for SmallAlgebra
#[pyclass(name = "SmallAlgebra")]
pub struct PySmallAlgebra {
    inner: BasicSmallAlgebra<i32>,
}

#[pymethods]
impl PySmallAlgebra {
    /// Create a basic small algebra.
    ///
    /// # Arguments
    /// * `name` - The name of the algebra
    /// * `size` - The size of the algebra
    ///
    /// # Returns
    /// A new SmallAlgebra instance
    #[staticmethod]
    fn new_basic(name: String, size: usize) -> PyResult<Self> {
        use std::collections::HashSet;
        let universe: HashSet<i32> = (0..size as i32).collect();

        let alg = BasicSmallAlgebra::new(
            name,
            universe,
            Vec::new()
        );

        Ok(PySmallAlgebra { inner: alg })
    }

    /// Get the name.
    fn name(&self) -> String {
        self.inner.name().to_string()
    }

    /// Get the cardinality.
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }

    fn __str__(&self) -> String {
        format!("SmallAlgebra(name: {}, cardinality: {})",
            self.inner.name(),
            self.inner.cardinality())
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }
}

impl Clone for PySmallAlgebra {
    fn clone(&self) -> Self {
        PySmallAlgebra { inner: self.inner.clone() }
    }
}

impl PySmallAlgebra {
    /// Clone the inner algebra as a boxed trait object.
    /// This is needed for the BigProductAlgebra constructor.
    pub(crate) fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = i32>> {
        Box::new(self.inner.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>
    }
}

/// Python wrapper for SubalgebraLattice
#[pyclass]
pub struct PySubalgebraLattice {
    inner: std::cell::RefCell<uacalc::alg::sublat::SubalgebraLattice<i32>>,
}

#[pymethods]
impl PySubalgebraLattice {
    /// Create a new SubalgebraLattice from a BasicSmallAlgebra.
    /// 
    /// Args:
    ///     algebra (BasicSmallAlgebra): The algebra to compute subalgebras for
    /// 
    /// Returns:
    ///     SubalgebraLattice: A new SubalgebraLattice instance
    /// 
    /// Raises:
    ///     ValueError: If the algebra is invalid
    #[new]
    fn new(algebra: &PyBasicSmallAlgebra) -> PyResult<Self> {
        let alg_box: Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>> =  
            Box::new(algebra.inner.clone());
        
        match uacalc::alg::sublat::SubalgebraLattice::new_safe(alg_box) {
            Ok(inner) => Ok(PySubalgebraLattice { 
                inner: std::cell::RefCell::new(inner) 
            }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the number of subalgebras.
    /// 
    /// Returns:
    ///     int: The number of subalgebras
    fn size(&self) -> usize {
        self.inner.borrow().size()
    }
    
    /// Get the subalgebra at the given index.
    /// 
    /// Args:
    ///     index (int): The index of the subalgebra
    /// 
    /// Returns:
    ///     BasicSmallAlgebra: The subalgebra at the given index
    /// 
    /// Raises:
    ///     ValueError: If the index is out of bounds
    fn get_subalgebra(&self, index: usize) -> PyResult<PyBasicSmallAlgebra> {
        let sub_lat = self.inner.borrow();
        if index >= sub_lat.size() {
            return Err(PyValueError::new_err(format!("Index {} out of bounds for subalgebra lattice of size {}", index, sub_lat.size())));
        }
        
        let subalg = sub_lat.get_subalgebra(index);
        Ok(PyBasicSmallAlgebra::from_inner(subalg.clone()))
    }
    
    /// Get all subalgebras as a list.
    /// 
    /// Returns:
    ///     List[BasicSmallAlgebra]: List of all subalgebras
    fn get_all_subalgebras(&self) -> Vec<PyBasicSmallAlgebra> {
        let sub_lat = self.inner.borrow();
        (0..sub_lat.size())
            .map(|i| PyBasicSmallAlgebra::from_inner(sub_lat.get_subalgebra(i).clone()))
            .collect()
    }
    
    /// Check if a given set is a subalgebra.
    /// 
    /// Args:
    ///     elements (List[int]): The set of elements to check
    /// 
    /// Returns:
    ///     bool: True if the set is a subalgebra
    fn is_subalgebra(&self, elements: Vec<i32>) -> bool {
        let sub_lat = self.inner.borrow();
        let element_set: std::collections::HashSet<i32> = elements.into_iter().collect();
        sub_lat.is_subalgebra(&element_set)
    }
    
    /// Get the meet of two subalgebras.
    /// 
    /// Args:
    ///     index1 (int): Index of the first subalgebra
    ///     index2 (int): Index of the second subalgebra
    /// 
    /// Returns:
    ///     int: Index of the meet subalgebra
    /// 
    /// Raises:
    ///     ValueError: If either index is out of bounds
    fn meet(&self, index1: usize, index2: usize) -> PyResult<usize> {
        let sub_lat = self.inner.borrow();
        if index1 >= sub_lat.size() || index2 >= sub_lat.size() {
            return Err(PyValueError::new_err("Index out of bounds"));
        }
        Ok(sub_lat.meet(index1, index2))
    }
    
    /// Get the join of two subalgebras.
    /// 
    /// Args:
    ///     index1 (int): Index of the first subalgebra
    ///     index2 (int): Index of the second subalgebra
    /// 
    /// Returns:
    ///     int: Index of the join subalgebra
    /// 
    /// Raises:
    ///     ValueError: If either index is out of bounds
    fn join(&self, index1: usize, index2: usize) -> PyResult<usize> {
        let sub_lat = self.inner.borrow();
        if index1 >= sub_lat.size() || index2 >= sub_lat.size() {
            return Err(PyValueError::new_err("Index out of bounds"));
        }
        Ok(sub_lat.join(index1, index2))
    }
    
    /// Get the top element (the algebra itself).
    /// 
    /// Returns:
    ///     int: Index of the top element
    fn top(&self) -> usize {
        self.inner.borrow().top()
    }
    
    /// Get the bottom element (the empty subalgebra).
    /// 
    /// Returns:
    ///     int: Index of the bottom element
    fn bottom(&self) -> usize {
        self.inner.borrow().bottom()
    }
    
    /// Check if one subalgebra is less than or equal to another.
    /// 
    /// Args:
    ///     index1 (int): Index of the first subalgebra
    ///     index2 (int): Index of the second subalgebra
    /// 
    /// Returns:
    ///     bool: True if the first subalgebra is less than or equal to the second
    /// 
    /// Raises:
    ///     ValueError: If either index is out of bounds
    fn le(&self, index1: usize, index2: usize) -> PyResult<bool> {
        let sub_lat = self.inner.borrow();
        if index1 >= sub_lat.size() || index2 >= sub_lat.size() {
            return Err(PyValueError::new_err("Index out of bounds"));
        }
        Ok(sub_lat.le(index1, index2))
    }
    
    /// Python string representation.
    fn __str__(&self) -> String {
        let sub_lat = self.inner.borrow();
        format!("SubalgebraLattice(size: {})", sub_lat.size())
    }
    
    /// Python repr representation.
    fn __repr__(&self) -> String {
        self.__str__()
    }
}