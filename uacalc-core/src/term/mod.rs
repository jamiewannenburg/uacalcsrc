//! Term evaluation engine for universal algebra
//! 
//! This module provides efficient term representation and evaluation
//! with zero-allocation recursive evaluation using stack arrays.

pub mod term;
pub mod variable;
pub mod evaluation;
pub mod arena;

pub use term::{Term, TermId};
pub use variable::{Variable, VariableAssignment, VariableScope};
pub use arena::TermArena;
pub use evaluation::{EvaluationContext, eval_term, eval_term_int};

/// Maximum depth for term evaluation to prevent stack overflow
pub const MAX_DEPTH: usize = 1000;

/// Re-export commonly used term types
pub mod prelude {
    pub use super::{Term, TermId, Variable, TermArena, EvaluationContext};
    pub use super::{eval_term, eval_term_int};
}

/// Common type aliases for term operations
pub type TermResult<T> = Result<T, crate::UACalcError>;
