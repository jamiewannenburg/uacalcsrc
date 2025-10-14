//! Operation Symbol implementation for UACalc
//! 
//! Provides the OperationSymbol struct that represents operation names and arities.

use pyo3::prelude::*;
use std::cmp::Ordering;
use std::collections::HashMap;
use std::fmt;
use std::hash::{Hash, Hasher};
use std::sync::Mutex;

lazy_static::lazy_static! {
    static ref CURRENT_SYM_INDEX_MAP: Mutex<HashMap<i32, i32>> = Mutex::new(HashMap::new());
}

/// Represents an operation symbol with a name and arity
#[derive(Debug, Clone)]
#[pyclass(name = "OperationSymbol")]
pub struct OperationSymbol {
    pub name: String,
    pub arity: i32,
    pub associative: bool,
}

impl OperationSymbol {
    /// Create a new OperationSymbol
    pub fn new(name: String, arity: i32) -> Self {
        Self::new_with_associative(name, arity, false)
    }
    
    /// Create a new OperationSymbol with associativity flag
    pub fn new_with_associative(name: String, arity: i32, associative: bool) -> Self {
        if associative && arity != 2 {
            panic!("Only binary operations can be associative");
        }
        
        Self {
            name,
            arity,
            associative: associative && arity == 2,
        }
    }
    
    /// Get a standard operation symbol for the given arity
    pub fn get_operation_symbol(arity: i32) -> Self {
        let mut map = CURRENT_SYM_INDEX_MAP.lock().unwrap();
        let index = map.entry(arity).or_insert(-1);
        *index += 1;
        let ind = *index;
        drop(map);
        
        let name = match arity {
            0 => format!("c_{}", ind),
            1 => format!("u_{}", ind),
            2 => format!("b_{}", ind),
            3 => format!("t_{}", ind),
            _ => format!("op{}_{}", arity, ind),
        };
        
        Self::new(name, arity)
    }
    
    /// Predefined operation symbols
    pub fn join() -> Self {
        Self::new("join".to_string(), 2)
    }
    
    pub fn meet() -> Self {
        Self::new("meet".to_string(), 2)
    }
    
    pub fn product() -> Self {
        Self::new("prod".to_string(), 2)
    }
    
    pub fn inverse() -> Self {
        Self::new("inv".to_string(), 1)
    }
    
    pub fn identity() -> Self {
        Self::new("id".to_string(), 0)
    }
}

#[pymethods]
impl OperationSymbol {
    #[new]
    #[pyo3(signature = (name, arity, associative = false))]
    pub fn py_new(name: String, arity: i32, associative: bool) -> Self {
        Self::new_with_associative(name, arity, associative)
    }
    
    /// Get the arity of this operation symbol
    #[getter]
    pub fn arity(&self) -> i32 {
        self.arity
    }
    
    /// Get the name of this operation symbol
    #[getter]
    pub fn name(&self) -> &str {
        &self.name
    }
    
    /// Get associative flag
    #[getter]
    pub fn associative(&self) -> bool {
        self.associative
    }
    
    /// Check if this operation symbol is associative
    pub fn is_associative(&self) -> bool {
        self.associative
    }
    
    /// Set associativity (only valid for binary operations)
    pub fn set_associative(&mut self, assoc: bool) -> PyResult<()> {
        if assoc && self.arity != 2 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Only binary operations can be associative"
            ));
        }
        self.associative = assoc && self.arity == 2;
        Ok(())
    }
    
    /// String representation with optional arity display
    #[pyo3(signature = (show_arity = false))]
    pub fn to_string(&self, show_arity: bool) -> String {
        if show_arity {
            format!("{}({})", self.name, self.arity)
        } else {
            self.name.clone()
        }
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.to_string(false)
    }
    
    /// Python representation
    fn __repr__(&self) -> String {
        format!("OperationSymbol('{}', {})", self.name, self.arity)
    }
    
    /// Python equality
    fn __eq__(&self, other: &Self) -> bool {
        self == other
    }
    
    /// Python hash
    fn __hash__(&self) -> u64 {
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        self.hash(&mut hasher);
        hasher.finish()
    }
    
    /// Get a standard operation symbol (static method)
    #[staticmethod]
    pub fn get_standard_symbol(arity: i32) -> Self {
        Self::get_operation_symbol(arity)
    }
}

impl fmt::Display for OperationSymbol {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.name)
    }
}

impl PartialEq for OperationSymbol {
    fn eq(&self, other: &Self) -> bool {
        self.name == other.name && self.arity == other.arity
    }
}

impl Eq for OperationSymbol {}

impl Hash for OperationSymbol {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.name.hash(state);
        self.arity.hash(state);
    }
}

impl PartialOrd for OperationSymbol {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for OperationSymbol {
    /// This puts high arity operations first (as in Java implementation)
    fn cmp(&self, other: &Self) -> Ordering {
        match other.arity.cmp(&self.arity) {
            Ordering::Equal => self.name.cmp(&other.name),
            other => other,
        }
    }
}