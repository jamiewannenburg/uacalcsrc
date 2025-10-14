use std::cmp::Ordering;
use std::collections::HashMap;
use std::fmt;
use std::hash::{Hash, Hasher};
use std::sync::Mutex;

use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

lazy_static::lazy_static! {
    static ref CURRENT_SYM_INDEX_MAP: Mutex<HashMap<i32, i32>> = Mutex::new(HashMap::new());
}

/// An operation symbol with a name and arity
#[pyclass(name = "OperationSymbol")]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OperationSymbol {
    name: String,
    arity: i32,
    associative: bool,
}

// Static constants
impl OperationSymbol {
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
    pub fn new(name: String, arity: i32, associative: Option<bool>) -> Self {
        let mut symbol = Self {
            name,
            arity,
            associative: false,
        };
        symbol.set_associative(associative.unwrap_or(false));
        symbol
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
    
    /// Check if this symbol is associative
    #[getter]
    pub fn is_associative(&self) -> bool {
        self.associative
    }
    
    /// Set whether this symbol is associative
    pub fn set_associative(&mut self, assoc: bool) {
        if assoc && self.arity != 2 {
            panic!("Only binary terms can be associative.");
        }
        self.associative = assoc && self.arity == 2;
    }
    
    /// String representation
    #[pyo3(signature = (show_arity = false))]
    pub fn to_string(&self, show_arity: Option<bool>) -> String {
        if show_arity.unwrap_or(false) {
            format!("{}({})", self.name, self.arity)
        } else {
            self.name.clone()
        }
    }
    
    /// Get an operation symbol in a uniform manner
    #[staticmethod]
    pub fn get_operation_symbol(arity: i32) -> Self {
        let mut map = CURRENT_SYM_INDEX_MAP.lock().unwrap();
        let index = map.get(&arity).unwrap_or(&-1) + 1;
        map.insert(arity, index);
        
        let name = match arity {
            0 => format!("c_{}", index),
            1 => format!("u_{}", index),
            2 => format!("b_{}", index),
            3 => format!("t_{}", index),
            _ => format!("op{}_{}", arity, index),
        };
        
        Self::new(name, arity, Some(false))
    }
    
    fn __str__(&self) -> String {
        self.to_string(None)
    }
    
    fn __repr__(&self) -> String {
        format!("OperationSymbol('{}', {})", self.name, self.arity)
    }
    
    fn __eq__(&self, other: &Self) -> bool {
        self.name == other.name && self.arity == other.arity
    }
    
    fn __hash__(&self) -> u64 {
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        self.hash(&mut hasher);
        hasher.finish()
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
    // This puts high arity operations first (reversed from Java)
    fn cmp(&self, other: &Self) -> Ordering {
        match other.arity.cmp(&self.arity) {
            Ordering::Equal => self.name.cmp(&other.name),
            ord => ord,
        }
    }
}