//! Operation module providing traits and implementations for universal algebra operations

mod operation_symbol;
mod operation;
mod abstract_operation;
mod int_operation;

pub use operation_symbol::*;
pub use operation::*;
pub use abstract_operation::*;
pub use int_operation::*;