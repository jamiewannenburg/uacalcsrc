use pyo3::prelude::*;
use uacalc::group::PermutationGroup;
use uacalc::util::int_array::{IntArray, IntArrayTrait};
use crate::alg::basic_algebra::PyBasicAlgebra;

#[pyclass]
pub struct PyPermutationGroup {
    inner: PermutationGroup,
}

#[pymethods]
impl PyPermutationGroup {
    #[new]
    fn new(name: String, generators: Vec<Vec<i32>>) -> PyResult<Self> {
        let int_arrays: Result<Vec<IntArray>, String> = generators
            .into_iter()
            .map(|gen| IntArray::from_array(gen))
            .collect();
        
        let int_arrays = int_arrays.map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        
        let perm_group = PermutationGroup::new(name, int_arrays);
        
        Ok(PyPermutationGroup { inner: perm_group })
    }

    #[staticmethod]
    fn new_with_universe(name: String, generators: Vec<Vec<i32>>, universe: Vec<Vec<i32>>) -> PyResult<Self> {
        let int_arrays: Result<Vec<IntArray>, String> = generators
            .into_iter()
            .map(|gen| IntArray::from_array(gen))
            .collect();
        
        let int_arrays = int_arrays.map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        
        let universe_arrays: Result<Vec<IntArray>, String> = universe
            .into_iter()
            .map(|univ| IntArray::from_array(univ))
            .collect();
        
        let universe_arrays = universe_arrays.map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        
        let perm_group = PermutationGroup::new_with_universe(name, int_arrays, universe_arrays);
        
        Ok(PyPermutationGroup { inner: perm_group })
    }

    #[staticmethod]
    fn new_safe(name: String, generators: Vec<Vec<i32>>) -> PyResult<Self> {
        let int_arrays: Result<Vec<IntArray>, String> = generators
            .into_iter()
            .map(|gen| IntArray::from_array(gen))
            .collect();
        
        let int_arrays = int_arrays.map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        
        let perm_group = PermutationGroup::new_safe(name, int_arrays)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        
        Ok(PyPermutationGroup { inner: perm_group })
    }

    #[staticmethod]
    fn new_with_universe_safe(name: String, generators: Vec<Vec<i32>>, universe: Vec<Vec<i32>>) -> PyResult<Self> {
        let int_arrays: Result<Vec<IntArray>, String> = generators
            .into_iter()
            .map(|gen| IntArray::from_array(gen))
            .collect();
        
        let int_arrays = int_arrays.map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        
        let universe_arrays: Result<Vec<IntArray>, String> = universe
            .into_iter()
            .map(|univ| IntArray::from_array(univ))
            .collect();
        
        let universe_arrays = universe_arrays.map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        
        let perm_group = PermutationGroup::new_with_universe_safe(name, int_arrays, universe_arrays)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        
        Ok(PyPermutationGroup { inner: perm_group })
    }

    #[staticmethod]
    fn prod(p1: Vec<i32>, p2: Vec<i32>) -> PyResult<Vec<i32>> {
        let arr1 = IntArray::from_array(p1).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        let arr2 = IntArray::from_array(p2).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        
        let result = PermutationGroup::prod(arr1, arr2)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        Ok(result.as_slice().to_vec())
    }

    #[staticmethod]
    fn inv(p: Vec<i32>) -> PyResult<Vec<i32>> {
        let arr = IntArray::from_array(p).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        
        let result = PermutationGroup::inv(arr)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        Ok(result.as_slice().to_vec())
    }

    #[staticmethod]
    fn id(set_size: i32) -> PyResult<Vec<i32>> {
        let result = PermutationGroup::id(set_size as usize);
        Ok(result.as_slice().to_vec())
    }

    /// Compute the automorphism group of a BasicAlgebra.
    ///
    /// This function finds all automorphisms (bijections that preserve all operations)
    /// of the given algebra and returns them as a PermutationGroup.
    ///
    /// Args:
    ///     alg (BasicAlgebra): The BasicAlgebra to compute the automorphism group for
    ///
    /// Returns:
    ///     PermutationGroup: The automorphism group
    ///
    /// Raises:
    ///     ValueError: If there's an error during computation
    #[staticmethod]
    fn automorphism_group(alg: &PyBasicAlgebra) -> PyResult<Self> {
        let aut_group = PermutationGroup::automorphism_group(&alg.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        Ok(PyPermutationGroup { inner: aut_group })
    }

    fn get_name(&self) -> String {
        self.inner.name.clone()
    }

    fn get_generators(&self) -> Vec<Vec<i32>> {
        self.inner.generators.iter().map(|gen| gen.as_slice().to_vec()).collect()
    }

    fn get_universe_list(&self) -> Option<Vec<Vec<i32>>> {
        self.inner.universe_list.as_ref().map(|univ| {
            univ.iter().map(|u| u.as_slice().to_vec()).collect()
        })
    }

    fn get_underlying_set_size(&self) -> usize {
        self.inner.underlying_set_size
    }

    fn get_identity(&self) -> Option<Vec<i32>> {
        self.inner.identity.as_ref().map(|id| id.as_slice().to_vec())
    }

    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }

    fn __repr__(&self) -> String {
        format!("PermutationGroup({})", self.inner.name)
    }

    /// Convert this PermutationGroup to a BasicAlgebra with integer elements.
    ///
    /// The resulting algebra has:
    /// - Universe: {0, 1, ..., n-1} where n is the underlying set size
    /// - Operations: The group operations (product, inverse, identity)
    ///
    /// Args:
    ///     name (str): The name for the resulting BasicAlgebra
    ///
    /// Returns:
    ///     BasicAlgebra: The BasicAlgebra representation
    ///
    /// Raises:
    ///     ValueError: If there's an error during conversion
    fn to_basic_algebra(&self, name: String) -> PyResult<PyBasicAlgebra> {
        let alg = self.inner.to_basic_algebra(name)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))?;
        Ok(PyBasicAlgebra::from_inner(alg))
    }
}

pub fn register_group_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyPermutationGroup>()?;
    
    // Export only clean names (without Py prefix)
    m.add("PermutationGroup", m.getattr("PyPermutationGroup")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyPermutationGroup")?;
    
    Ok(())
}