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
pub use utils::{
    binomial_coefficient, estimate_table_memory, factorial, horner_decode, horner_encode,
    horner_table_size, power_checked, validate_operation_args, validate_partition_elements,
    validate_universe_contiguous, DEFAULT_CACHE_SIZE, ERR_INVALID_ARITY, ERR_INVALID_UNIVERSE,
    ERR_OVERFLOW, ERR_TABLE_TOO_LARGE, MAX_OPERATION_ARITY, MAX_TABLE_SIZE, MAX_UNIVERSE_SIZE,
    PERFORMANCE_THRESHOLD,
};

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
    pub use crate::{CongruenceLattice, CongruenceLatticeBuilder};
}

/// Common type aliases for better ergonomics
pub type AlgebraResult<T> = Result<T, UACalcError>;
pub type OperationTable = FlatOperationTable;
pub type PartitionResult<T> = Result<T, UACalcError>;
pub type RelationResult<T> = Result<T, UACalcError>;
