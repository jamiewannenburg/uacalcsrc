use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyList;
use std::collections::HashMap;
use uacalc::alg::*;
use uacalc::terms::{VariableImp, Term};
use crate::util::PyIntArray;

use crate::alg::PyBasicSmallAlgebra;
use crate::alg::PySubalgebraLattice;
use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;

#[pyclass]
pub struct PyReductAlgebra {
    inner: uacalc::alg::ReductAlgebra,
}

impl PyReductAlgebra {
    /// Create PyReductAlgebra from inner Rust type (not exposed to Python)
    fn from_inner(inner: uacalc::alg::ReductAlgebra) -> Self {
        PyReductAlgebra { inner }
    }
}

#[pymethods]
impl PyReductAlgebra {
    /// Create a new ReductAlgebra from a super algebra and list of terms.
    /// 
    /// Args:
    ///     super_algebra (BasicSmallAlgebra): The super algebra that this reduct is based on
    ///     term_list (List[Term]): The list of terms that define the operations
    /// 
    /// Returns:
    ///     ReductAlgebra: A new ReductAlgebra instance
    /// 
    /// Raises:
    ///     ValueError: If the terms are invalid or algebra is incompatible
    #[new]
    fn new(super_algebra: &PyBasicSmallAlgebra, term_list: &PyList) -> PyResult<Self> {
        // Convert Python list of terms to Rust Vec<Box<dyn Term>>
        let mut rust_terms: Vec<Box<dyn uacalc::terms::Term>> = Vec::new();
        
        for item in term_list.iter() {
            // For now, we'll create a simple variable term
            // In a full implementation, we'd need to handle different term types
            if let Ok(var_name) = item.extract::<String>() {
                let var = Box::new(uacalc::terms::VariableImp::new(&var_name)) as Box<dyn uacalc::terms::Term>;
                rust_terms.push(var);
            } else {
                return Err(PyValueError::new_err("Term list must contain strings (variable names)"));
            }
        }
        
        // Create the super algebra as a trait object
        let super_alg = Box::new(super_algebra.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        
        match uacalc::alg::ReductAlgebra::new_safe(super_alg, rust_terms) {
            Ok(inner) => Ok(PyReductAlgebra { inner }),
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
    ///     name (str): The new name
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
    
    /// Get the algebra type.
    /// 
    /// Returns:
    ///     str: The algebra type
    fn algebra_type(&self) -> String {
        "Reduct".to_string()
    }
    
    /// Get the universe as a list.
    /// 
    /// Returns:
    ///     List[int]: The universe elements
    fn get_universe_list(&self) -> Option<Vec<i32>> {
        self.inner.get_universe_list()
    }
    
    /// Get the universe order as a dictionary.
    /// 
    /// Returns:
    ///     Dict[int, int]: The universe order mapping
    fn get_universe_order(&self) -> Option<HashMap<i32, usize>> {
        self.inner.get_universe_order()
    }
    
    /// Get an element by its index.
    /// 
    /// Args:
    ///     index (int): The index of the element
    /// 
    /// Returns:
    ///     int: The element at the given index
    fn get_element(&self, index: usize) -> Option<i32> {
        self.inner.get_element(index)
    }
    
    /// Get the index of an element.
    /// 
    /// Args:
    ///     element (int): The element to find the index for
    /// 
    /// Returns:
    ///     int: The index of the element
    fn element_index(&self, element: i32) -> Option<usize> {
        self.inner.element_index(&element)
    }
    
    /// Check if this algebra is unary.
    /// 
    /// Returns:
    ///     bool: True if the algebra is unary
    fn is_unary(&self) -> bool {
        self.inner.is_unary()
    }
    
    /// Check if this algebra is idempotent.
    /// 
    /// Returns:
    ///     bool: True if the algebra is idempotent
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }
    
    /// Check if this algebra is total.
    /// 
    /// Returns:
    ///     bool: True if the algebra is total
    fn is_total(&self) -> bool {
        self.inner.is_total()
    }
    
    /// Get the number of operations in this algebra.
    /// 
    /// Returns:
    ///     int: The number of operations
    fn operations_count(&self) -> usize {
        self.inner.get_operations_ref().len()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("ReductAlgebra({})", self.inner.to_string())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyReductAlgebra) -> bool {
        self.inner.name() == other.inner.name() && 
        self.inner.cardinality() == other.inner.cardinality()
    }
    
    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.name().hash(&mut hasher);
        self.inner.cardinality().hash(&mut hasher);
        hasher.finish()
    }
    
    /// Get the congruence lattice (lazy initialization).
    /// 
    /// Returns:
    ///     CongruenceLattice: The congruence lattice
    fn con(&mut self) -> PyCongruenceLattice {
        let con_lat = self.inner.con();
        PyCongruenceLattice { inner: con_lat.clone() }
    }
    
    /// Get the subalgebra lattice (lazy initialization).
    /// 
    /// Returns:
    ///     SubalgebraLattice: The subalgebra lattice
    fn sub(&mut self) -> PySubalgebraLattice {
        let sub_lat = self.inner.sub();
        PySubalgebraLattice::from_inner(sub_lat.clone())
    }
}


/// Python wrapper for UnaryTermsMonoid
#[pyclass]
pub struct PyUnaryTermsMonoid {
    inner: uacalc::alg::UnaryTermsMonoid,
}

#[pymethods]
impl PyUnaryTermsMonoid {
    /// Create a new UnaryTermsMonoid from a generating algebra.
    /// 
    /// Args:
    ///     algebra (BasicSmallAlgebra): The generating algebra
    /// 
    /// Raises:
    ///     ValueError: If construction fails
    #[new]
    fn new(algebra: &PyBasicSmallAlgebra) -> PyResult<Self> {
        let rust_alg = Box::new(algebra.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        
        match uacalc::alg::UnaryTermsMonoid::new_safe(rust_alg) {
            Ok(inner) => Ok(PyUnaryTermsMonoid { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new UnaryTermsMonoid with optional identity inclusion.
    /// 
    /// Args:
    ///     algebra (BasicSmallAlgebra): The generating algebra
    ///     include_id (bool): Whether to include the identity term
    /// 
    /// Raises:
    ///     ValueError: If construction fails
    #[staticmethod]
    fn new_with_id(algebra: &PyBasicSmallAlgebra, include_id: bool) -> PyResult<Self> {
        let rust_alg = Box::new(algebra.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        
        match uacalc::alg::UnaryTermsMonoid::new_with_id_safe(rust_alg, include_id) {
            Ok(inner) => Ok(PyUnaryTermsMonoid { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the algebra type.
    /// 
    /// Returns:
    ///     str: The algebra type
    fn algebra_type(&self) -> String {
        match self.inner.algebra_type() {
            uacalc::alg::AlgebraType::UnaryTermsMonoid => "UNARY_TERMS_MONOID".to_string(),
            _ => "UNKNOWN".to_string(),
        }
    }
    
    /// Get the cardinality of the algebra.
    /// 
    /// Returns:
    ///     int: The cardinality
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }
    
    /// Get the name of the algebra.
    /// 
    /// Returns:
    ///     str: The name
    fn name(&self) -> String {
        self.inner.name().to_string()
    }
    
    /// Set the name of the algebra.
    /// 
    /// Args:
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }
    
    /// Check if this algebra is unary.
    /// 
    /// Returns:
    ///     bool: True if the algebra is unary
    fn is_unary(&self) -> bool {
        self.inner.is_unary()
    }
    
    /// Check if this algebra is idempotent.
    /// 
    /// Returns:
    ///     bool: True if the algebra is idempotent
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }
    
    /// Check if this algebra is total.
    /// 
    /// Returns:
    ///     bool: True if the algebra is total
    fn is_total(&self) -> bool {
        self.inner.is_total()
    }
    
    /// Get the number of operations.
    /// 
    /// Returns:
    ///     int: The number of operations (1 for the product operation)
    fn operations_count(&self) -> usize {
        self.inner.get_operations_ref().len()
    }
    
    /// Get the universe as a list.
    /// 
    /// Returns:
    ///     List[IntArray]: The universe elements
    fn get_universe_list(&self) -> Vec<PyIntArray> {
        self.inner.universe()
            .map(|item| PyIntArray { inner: item })
            .collect()
    }
    
    /// Get an element by its index.
    /// 
    /// Args:
    ///     index (int): The index of the element
    /// 
    /// Returns:
    ///     IntArray: The element at the given index (optional)
    fn get_element(&self, index: usize) -> Option<PyIntArray> {
        self.inner.get_element(index).map(|item| PyIntArray { inner: item })
    }
    
    /// Get the index of an element.
    /// 
    /// Args:
    ///     element (IntArray): The element to find the index for
    /// 
    /// Returns:
    ///     int: The index of the element (optional)
    fn element_index(&self, element: &PyIntArray) -> Option<usize> {
        self.inner.element_index(&element.inner)
    }
    
    /// String representation of the algebra.
    /// 
    /// Returns:
    ///     str: String representation
    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }
    
    /// String representation for debugging.
    /// 
    /// Returns:
    ///     str: Debug string representation
    fn __repr__(&self) -> String {
        format!("UnaryTermsMonoid(name='{}', cardinality={})", self.name(), self.cardinality())
    }
    
    /// Length function for use with len().
    /// 
    /// Returns:
    ///     int: Cardinality of the algebra
    fn __len__(&self) -> usize {
        self.inner.cardinality() as usize
    }
}
