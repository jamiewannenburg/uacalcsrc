//! OperationSymbol implementation

use crate::error::{Result, UaCalcError};
use std::collections::HashMap;
use std::fmt::{self, Display};
use std::hash::{Hash, Hasher};
use std::sync::LazyLock;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

/// Static map for generating uniform operation symbols
static CURRENT_SYM_INDEX_MAP: LazyLock<std::sync::Mutex<HashMap<i32, i32>>> = LazyLock::new(|| std::sync::Mutex::new(HashMap::new()));

/// An operation symbol with a name and arity
#[pyclass(name = "OperationSymbol")]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OperationSymbol {
    name: String,
    arity: i32,
    associative: bool,
}

impl OperationSymbol {
    /// Standard operation symbols
    pub const JOIN: OperationSymbol = OperationSymbol {
        name: String::new(), // Will be set in lazy_static or const fn when stable
        arity: 2,
        associative: false,
    };

    /// Create a new operation symbol
    pub fn new(name: String, arity: i32) -> Result<Self> {
        Self::new_with_associative(name, arity, false)
    }

    /// Create a new operation symbol with associative flag
    pub fn new_with_associative(name: String, arity: i32, associative: bool) -> Result<Self> {
        if arity < 0 {
            return Err(UaCalcError::InvalidArity(arity));
        }
        
        let mut symbol = OperationSymbol {
            name,
            arity,
            associative: false,
        };
        
        symbol.set_associative(associative)?;
        Ok(symbol)
    }

    /// Get the arity of this operation symbol
    pub fn arity(&self) -> i32 {
        self.arity
    }

    /// Get the name of this operation symbol
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Check if this operation symbol is marked as associative
    pub fn is_associative(&self) -> bool {
        self.associative
    }

    /// Set the associative flag
    pub fn set_associative(&mut self, associative: bool) -> Result<()> {
        if associative && self.arity != 2 {
            return Err(UaCalcError::InvalidArity(self.arity));
        }
        self.associative = associative && self.arity == 2;
        Ok(())
    }

    /// Get an operation symbol in a uniform manner
    pub fn get_operation_symbol(arity: i32) -> Result<Self> {
        if arity < 0 {
            return Err(UaCalcError::InvalidArity(arity));
        }

        let mut map = CURRENT_SYM_INDEX_MAP.lock().unwrap();
        let index = map.entry(arity).or_insert(0);
        let current_index = *index;
        *index += 1;

        let name = match arity {
            0 => format!("c_{}", current_index),
            1 => format!("u_{}", current_index),
            2 => format!("b_{}", current_index),
            3 => format!("t_{}", current_index),
            _ => format!("op{}_{}", arity, current_index),
        };

        Ok(OperationSymbol {
            name,
            arity,
            associative: false,
        })
    }

    /// Convert to string with optional arity display
    pub fn to_string_with_arity(&self, show_arity: bool) -> String {
        if show_arity {
            format!("{}({})", self.name, self.arity)
        } else {
            self.name.clone()
        }
    }
}

impl Display for OperationSymbol {
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
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for OperationSymbol {
    /// This puts high arity operations first
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        match other.arity.cmp(&self.arity) {
            std::cmp::Ordering::Equal => self.name.cmp(&other.name),
            other_ord => other_ord,
        }
    }
}

/// Python wrapper for OperationSymbol
#[pymethods]
impl OperationSymbol {
    #[new]
    #[pyo3(signature = (name, arity, associative = false))]
    fn py_new(name: String, arity: i32, associative: Option<bool>) -> PyResult<Self> {
        Self::new_with_associative(name, arity, associative.unwrap_or(false))
            .map_err(|e| e.into())
    }

    #[getter]
    fn get_name(&self) -> &str {
        self.name()
    }

    #[getter]
    fn get_arity(&self) -> i32 {
        self.arity()
    }

    #[getter]
    fn get_associative(&self) -> bool {
        self.is_associative()
    }

    #[setter]
    fn set_associative_py(&mut self, associative: bool) -> PyResult<()> {
        self.set_associative(associative).map_err(|e| e.into())
    }

    fn __str__(&self) -> String {
        self.to_string()
    }

    fn __repr__(&self) -> String {
        format!("OperationSymbol('{}', {})", self.name, self.arity)
    }

    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        let mut hasher = DefaultHasher::new();
        self.hash(&mut hasher);
        hasher.finish()
    }

    fn __eq__(&self, other: &Self) -> bool {
        self == other
    }

    fn __lt__(&self, other: &Self) -> bool {
        self < other
    }

    fn __le__(&self, other: &Self) -> bool {
        self <= other
    }

    fn __gt__(&self, other: &Self) -> bool {
        self > other
    }

    fn __ge__(&self, other: &Self) -> bool {
        self >= other
    }

    #[staticmethod]
    fn get_operation_symbol_py(arity: i32) -> PyResult<Self> {
        Self::get_operation_symbol(arity).map_err(|e| e.into())
    }

    fn to_string_with_arity_py(&self, show_arity: bool) -> String {
        self.to_string_with_arity(show_arity)
    }
}

// Create a type alias for the Python class
pub type PyOperationSymbol = OperationSymbol;