use pyo3::prelude::*;
use pyo3::types::PyList;
use uacalc::terms::{VariableImp, Variable};
use uacalc::lat::Order;
use std::sync::Arc;

/// Python wrapper for PartiallyDefinedLattice
/// This mirrors the Java implementation with proper Order trait usage
#[pyclass]
pub struct PyPartiallyDefinedLattice {
    pub name: String,
    pub order: Arc<dyn Order<VariableImp> + Send + Sync>,
    pub defined_joins: Vec<Vec<VariableImp>>,
    pub defined_meets: Vec<Vec<VariableImp>>,
}

#[pymethods]
impl PyPartiallyDefinedLattice {
    /// Create a new partially defined lattice.
    /// 
    /// # Arguments
    /// * `name` - The name of the lattice
    /// * `joins` - List of defined join operations (list of lists of VariableImp)
    /// * `meets` - List of defined meet operations (list of lists of VariableImp)
    /// 
    /// # Returns
    /// A new PartiallyDefinedLattice instance
    #[new]
    fn new(name: String, joins: &Bound<'_, PyAny>, meets: &Bound<'_, PyAny>) -> PyResult<Self> {
        // Convert Python lists to Rust vectors
        let joins_list: &Bound<'_, PyList> = joins.downcast()?;
        let meets_list: &Bound<'_, PyList> = meets.downcast()?;
        
        let mut rust_joins = Vec::new();
        for join_py in joins_list {
            let join_list: &Bound<'_, PyList> = join_py.downcast()?;
            let mut join = Vec::new();
            for var_py in join_list {
                let var: PyVariableImp = var_py.extract()?;
                join.push(var.inner);
            }
            rust_joins.push(join);
        }
        
        let mut rust_meets = Vec::new();
        for meet_py in meets_list {
            let meet_list: &Bound<'_, PyList> = meet_py.downcast()?;
            let mut meet = Vec::new();
            for var_py in meet_list {
                let var: PyVariableImp = var_py.extract()?;
                meet.push(var.inner);
            }
            rust_meets.push(meet);
        }
        
        // Create a simple order that orders variables by name
        let order: Arc<dyn Order<VariableImp> + Send + Sync> = Arc::new(VariableNameOrder);
        
        Ok(PyPartiallyDefinedLattice {
            name,
            order,
            defined_joins: rust_joins,
            defined_meets: rust_meets,
        })
    }
    
    /// Get the name of this lattice
    fn name(&self) -> String {
        self.name.clone()
    }
    
    /// Get the defined joins
    fn get_defined_joins(&self) -> Vec<Vec<PyVariableImp>> {
        self.defined_joins
            .iter()
            .map(|join| join.iter().map(|v| PyVariableImp { inner: v.clone() }).collect())
            .collect()
    }
    
    /// Get the defined meets
    fn get_defined_meets(&self) -> Vec<Vec<PyVariableImp>> {
        self.defined_meets
            .iter()
            .map(|meet| meet.iter().map(|v| PyVariableImp { inner: v.clone() }).collect())
            .collect()
    }
    
    /// Check if one variable is less than or equal to another
    /// This uses the Order trait implementation
    fn leq(&self, a: &PyVariableImp, b: &PyVariableImp) -> bool {
        self.order.leq(&a.inner, &b.inner)
    }
    
    /// String representation
    fn __str__(&self) -> String {
        format!("PartiallyDefinedLattice({})", self.name)
    }
    
    /// Repr representation
    fn __repr__(&self) -> String {
        format!("PartiallyDefinedLattice('{}')", self.name)
    }
}

// Import PyVariableImp from terms module
use crate::terms::PyVariableImp;

/// Simple order implementation that orders variables by name
/// This implements the Order trait and is thread-safe
#[derive(Debug, Clone)]
struct VariableNameOrder;

impl Order<VariableImp> for VariableNameOrder {
    fn leq(&self, a: &VariableImp, b: &VariableImp) -> bool {
        a.get_name() <= b.get_name()
    }
}

pub fn register_fplat_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register the PartiallyDefinedLattice class
    m.add_class::<PyPartiallyDefinedLattice>()?;
    
    // Export clean name (without Py prefix)
    m.add("PartiallyDefinedLattice", m.getattr("PyPartiallyDefinedLattice")?)?;
    
    // Remove the Py* name from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyPartiallyDefinedLattice")?;
    
    Ok(())
}
