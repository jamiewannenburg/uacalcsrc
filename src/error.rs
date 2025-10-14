//! Error types for UACalc operations

use thiserror::Error;
use pyo3::{exceptions::PyException, PyErr};

/// UACalc error types
#[derive(Error, Debug, Clone)]
pub enum UaCalcError {
    #[error("Invalid arity: {0}")]
    InvalidArity(i32),
    
    #[error("Invalid argument count: expected {expected}, got {actual}")]
    InvalidArgumentCount { expected: usize, actual: usize },
    
    #[error("Invalid argument value: {0}")]
    InvalidArgument(String),
    
    #[error("Operation not supported: {0}")]
    UnsupportedOperation(String),
    
    #[error("Table not available")]
    TableNotAvailable,
    
    #[error("Invalid set size: {0}")]
    InvalidSetSize(i32),
    
    #[error("Operation error: {0}")]
    OperationError(String),
}

impl From<UaCalcError> for PyErr {
    fn from(err: UaCalcError) -> PyErr {
        PyException::new_err(err.to_string())
    }
}

pub type Result<T> = std::result::Result<T, UaCalcError>;