use thiserror::Error;

/// Custom error type for UACalc operations
#[derive(Error, Debug)]
pub enum UACalcError {
    #[error("Invalid operation: {message}")]
    InvalidOperation { message: String },

    #[error("Index out of bounds: index {index}, size {size}")]
    IndexOutOfBounds { index: usize, size: usize },

    #[error("Invalid arity: expected {expected}, got {actual}")]
    InvalidArity { expected: usize, actual: usize },

    #[error("Algebra not found: {name}")]
    AlgebraNotFound { name: String },

    #[error("Operation not found: {symbol}")]
    OperationNotFound { symbol: String },

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    #[error("Parse error: {message}")]
    ParseError { message: String },

    #[error("Unsupported operation: {operation}")]
    UnsupportedOperation { operation: String },

    #[error("Arithmetic overflow: {operation}")]
    ArithmeticOverflow { operation: String },

    #[error("Operation cancelled: {message}")]
    Cancelled { message: String },

    #[error("Memory limit exceeded: {message}")]
    MemoryLimitExceeded { message: String },
}

/// Result type for UACalc operations
pub type UACalcResult<T> = Result<T, UACalcError>;
