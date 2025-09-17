//! Taylor combinatorial search algorithms
//!
//! This module provides efficient Taylor term representation and
//! combinatorial search algorithms for finding term interpretations.

pub mod canonical;
pub mod int_array;
pub mod polynomial;
pub mod search;
pub mod taylor;

pub use canonical::{canonical_form, make_union_find, UnionFind};
pub use int_array::IntArray;
pub use polynomial::{Polynomial, PolynomialCoefficient, PolynomialExpansion, TaylorSeries};
pub use search::{find_markovic_mckenzie, find_siggers, SearchConfig, SearchResult};
pub use taylor::{markovic_mckenzie_term, siggers_term, Taylor, TaylorSpec};

/// Re-export commonly used Taylor types
pub mod prelude {
    pub use super::{canonical_form, make_union_find};
    pub use super::{find_markovic_mckenzie, find_siggers, SearchConfig, SearchResult};
    pub use super::{IntArray, Polynomial, PolynomialCoefficient, PolynomialExpansion, Taylor, TaylorSeries, TaylorSpec, UnionFind};
    pub use super::canonical::CanonicalForm;
}

/// Common type aliases for Taylor operations
pub type TaylorResult<T> = Result<T, crate::UACalcError>;
