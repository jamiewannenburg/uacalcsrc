//! Universal Algebra Calculator Core Library
//!
//! This library provides efficient implementations of universal algebra structures
//! and algorithms, ported from the Java UACalc implementation.

pub mod algebra;
pub mod binary_relation;
#[cfg(feature = "conlat")]
pub mod conlat;
pub mod error;
pub mod operation;
pub mod partition;
pub mod product;
#[cfg(feature = "taylor")]
pub mod taylor;
#[cfg(feature = "term-eval")]
pub mod term;
pub mod utils;

pub use algebra::{Algebra, BasicAlgebra, SmallAlgebra};
pub use binary_relation::{
    empty_relation, equivalence_from_partition, identity_relation, universal_relation,
    BasicBinaryRelation, BinaryRelation,
};
pub use error::{UACalcError, UACalcResult};
pub use operation::{
    FlatOperationTable, FunctionOperation, Operation, OperationSymbol, OperationType,
    TableOperation,
};
pub use partition::{coarsest_partition, finest_partition, BasicPartition, Partition};
pub use product::ProductAlgebra;
pub use utils::{
    binomial_coefficient, estimate_table_memory, factorial, horner_decode, horner_encode,
    horner_table_size, power_checked, validate_operation_args, validate_partition_elements,
    validate_universe_contiguous, DEFAULT_CACHE_SIZE, ERR_INVALID_ARITY, ERR_INVALID_UNIVERSE,
    ERR_OVERFLOW, ERR_TABLE_TOO_LARGE, MAX_OPERATION_ARITY, MAX_TABLE_SIZE, MAX_UNIVERSE_SIZE,
    PERFORMANCE_THRESHOLD,
};

#[cfg(feature = "conlat")]
pub use conlat::{
    cg, find_join_irreducibles, principal_congruence, BasicCongruenceLattice, CongruenceLattice,
    CongruenceLatticeBuilder,
};

#[cfg(feature = "taylor")]
pub use taylor::{IntArray, Taylor, TaylorSpec};
#[cfg(feature = "term-eval")]
pub use term::{eval_term, eval_term_int, term_to_table, EvaluationContext, Term, TermArena};

/// Re-export commonly used types
pub mod prelude {
    pub use crate::{
        coarsest_partition, empty_relation, equivalence_from_partition, finest_partition,
        identity_relation, universal_relation, Algebra, BasicAlgebra, BasicBinaryRelation,
        BasicPartition, BinaryRelation, FlatOperationTable, FunctionOperation, Operation,
        OperationSymbol, OperationType, Partition, SmallAlgebra, TableOperation, UACalcError,
        UACalcResult,
    };

    // Utility functions
    pub use crate::{
        binomial_coefficient, estimate_table_memory, factorial, horner_decode, horner_encode,
        horner_table_size, power_checked, validate_operation_args, validate_partition_elements,
        validate_universe_contiguous, DEFAULT_CACHE_SIZE, ERR_INVALID_ARITY, ERR_INVALID_UNIVERSE,
        ERR_OVERFLOW, ERR_TABLE_TOO_LARGE, MAX_OPERATION_ARITY, MAX_TABLE_SIZE, MAX_UNIVERSE_SIZE,
        PERFORMANCE_THRESHOLD,
    };

    #[cfg(feature = "conlat")]
    pub use crate::{
        cg, find_join_irreducibles, principal_congruence, BasicCongruenceLattice,
        CongruenceLattice, CongruenceLatticeBuilder,
    };

    #[cfg(feature = "term-eval")]
    pub use crate::{eval_term, eval_term_int, term_to_table, EvaluationContext, Term, TermArena};

    #[cfg(feature = "taylor")]
    pub use crate::taylor::{markovic_mckenzie_term, siggers_term, IntArray, Taylor, TaylorSpec};
}

/// Common type aliases for better ergonomics
pub type AlgebraResult<T> = Result<T, UACalcError>;
pub type OperationTable = FlatOperationTable;
pub type PartitionResult<T> = Result<T, UACalcError>;
pub type RelationResult<T> = Result<T, UACalcError>;
#[cfg(feature = "term-eval")]
pub type TermResult<T> = Result<T, UACalcError>;
#[cfg(feature = "taylor")]
pub type TaylorResult<T> = Result<T, UACalcError>;
