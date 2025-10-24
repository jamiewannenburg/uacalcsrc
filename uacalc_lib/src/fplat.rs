use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyList;
use uacalc::fplat::PartiallyDefinedLattice;
use uacalc::lat::Order;
use uacalc::terms::VariableImp;
use std::sync::Arc;

/// A simple order implementation for testing that orders variables by name.
#[derive(Debug, Clone)]
struct VariableNameOrder;

impl Order<VariableImp> for VariableNameOrder {
    fn leq(&self, a: &VariableImp, b: &VariableImp) -> bool {
        a.name <= b.name
    }
}

/// Python wrapper for PartiallyDefinedLattice
#[pyclass]
pub struct PyPartiallyDefinedLattice {
    pub(crate) inner: PartiallyDefinedLattice,
}

#[pymethods]
impl PyPartiallyDefinedLattice {
    /// Create a new partially defined lattice.
    /// 
    /// For now, this uses a simple name-based ordering on variables.
    /// 
    /// # Arguments
    /// * `name` - The name of the lattice
    /// * `joins` - List of lists of variables representing defined joins
    /// * `meets` - List of lists of variables representing defined meets
    /// 
    /// # Returns
    /// A new partially defined lattice
    #[new]
    fn new(
        name: String,
        joins: &Bound<'_, PyList>,
        meets: &Bound<'_, PyList>,
    ) -> PyResult<Self> {
        // Convert Python joins to Rust
        let mut rust_joins: Vec<Vec<VariableImp>> = Vec::new();
        for join_item in joins.iter() {
            let join_list: &Bound<'_, PyList> = join_item.downcast()?;
            let mut rust_join: Vec<VariableImp> = Vec::new();
            for var_item in join_list.iter() {
                let py_var: PyRef<crate::terms::PyVariableImp> = var_item.extract()?;
                rust_join.push(py_var.inner.clone());
            }
            rust_joins.push(rust_join);
        }
        
        // Convert Python meets to Rust
        let mut rust_meets: Vec<Vec<VariableImp>> = Vec::new();
        for meet_item in meets.iter() {
            let meet_list: &Bound<'_, PyList> = meet_item.downcast()?;
            let mut rust_meet: Vec<VariableImp> = Vec::new();
            for var_item in meet_list.iter() {
                let py_var: PyRef<crate::terms::PyVariableImp> = var_item.extract()?;
                rust_meet.push(py_var.inner.clone());
            }
            rust_meets.push(rust_meet);
        }
        
        // Create order (using simple name-based ordering)
        let order: Arc<dyn Order<VariableImp>> = Arc::new(VariableNameOrder);
        
        // Create the partially defined lattice
        match PartiallyDefinedLattice::new_safe(name, order, rust_joins, rust_meets) {
            Ok(inner) => Ok(PyPartiallyDefinedLattice { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the name of this lattice
    fn name(&self) -> String {
        self.inner.name().to_string()
    }
    
    /// Check if variable a is less than or equal to variable b
    /// 
    /// # Arguments
    /// * `a` - First variable
    /// * `b` - Second variable
    /// 
    /// # Returns
    /// True if a ≤ b, false otherwise
    fn leq(&self, a: &crate::terms::PyVariableImp, b: &crate::terms::PyVariableImp) -> bool {
        self.inner.leq(&a.inner, &b.inner)
    }
    
    /// Get the defined joins
    /// 
    /// # Returns
    /// List of lists of variables representing defined joins
    fn get_defined_joins(&self, py: Python) -> PyResult<PyObject> {
        let joins = self.inner.get_defined_joins();
        let py_joins = PyList::empty_bound(py);
        
        for join in joins {
            let py_join = PyList::empty_bound(py);
            for var in join {
                let py_var = crate::terms::PyVariableImp { inner: var.clone() };
                py_join.append(Py::new(py, py_var)?)?;
            }
            py_joins.append(py_join)?;
        }
        
        Ok(py_joins.into())
    }
    
    /// Get the defined meets
    /// 
    /// # Returns
    /// List of lists of variables representing defined meets
    fn get_defined_meets(&self, py: Python) -> PyResult<PyObject> {
        let meets = self.inner.get_defined_meets();
        let py_meets = PyList::empty_bound(py);
        
        for meet in meets {
            let py_meet = PyList::empty_bound(py);
            for var in meet {
                let py_var = crate::terms::PyVariableImp { inner: var.clone() };
                py_meet.append(Py::new(py, py_var)?)?;
            }
            py_meets.append(py_meet)?;
        }
        
        Ok(py_meets.into())
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        format!("PartiallyDefinedLattice({})", self.inner.name())
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("PartiallyDefinedLattice(name=\"{}\")", self.inner.name())
    }
}

pub fn register_fplat_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPartiallyDefinedLattice>()?;
    
    // Export clean name without Py prefix
    m.add("PartiallyDefinedLattice", m.getattr("PyPartiallyDefinedLattice")?)?;
    
    // Remove Py* name to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyPartiallyDefinedLattice")?;
    
    Ok(())
}
