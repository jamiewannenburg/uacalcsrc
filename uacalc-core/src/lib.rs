//! Universal Algebra Calculator Core Library
//! 
//! This library provides efficient implementations of universal algebra structures
//! and algorithms, ported from the Java UACalc implementation.

pub mod algebra;
pub mod operation;
pub mod partition;
pub mod binary_relation;
pub mod utils;
#[cfg(feature = "conlat")]
pub mod conlat;
pub mod error;

pub use algebra::{Algebra, SmallAlgebra, BasicAlgebra};
pub use operation::{Operation, OperationSymbol, OperationType, FlatOperationTable, TableOperation, FunctionOperation};
pub use partition::{Partition, BasicPartition, finest_partition, coarsest_partition};
pub use binary_relation::{BinaryRelation, BasicBinaryRelation, identity_relation, universal_relation, empty_relation, equivalence_from_partition};
pub use error::{UACalcError, UACalcResult};
pub use utils::{
    horner_encode, horner_decode, horner_table_size,
    validate_universe_contiguous, validate_operation_args, validate_partition_elements,
    power_checked, factorial, binomial_coefficient,
    estimate_table_memory, time_operation,
    MAX_UNIVERSE_SIZE, MAX_OPERATION_ARITY, MAX_TABLE_SIZE,
    DEFAULT_CACHE_SIZE, PERFORMANCE_THRESHOLD,
    ERR_OVERFLOW, ERR_INVALID_UNIVERSE, ERR_TABLE_TOO_LARGE, ERR_INVALID_ARITY,
};

/// Re-export commonly used types
pub mod prelude {
    pub use crate::{
        Algebra, SmallAlgebra, BasicAlgebra,
        Operation, OperationSymbol, OperationType, FlatOperationTable, TableOperation, FunctionOperation,
        Partition, BasicPartition, finest_partition, coarsest_partition,
        BinaryRelation, BasicBinaryRelation, identity_relation, universal_relation, empty_relation, equivalence_from_partition,
        UACalcError, UACalcResult,
    };
    
    // Utility functions
    pub use crate::{
        horner_encode, horner_decode, horner_table_size,
        validate_universe_contiguous, validate_operation_args, validate_partition_elements,
        power_checked, factorial, binomial_coefficient,
        estimate_table_memory, time_operation,
        MAX_UNIVERSE_SIZE, MAX_OPERATION_ARITY, MAX_TABLE_SIZE,
        DEFAULT_CACHE_SIZE, PERFORMANCE_THRESHOLD,
        ERR_OVERFLOW, ERR_INVALID_UNIVERSE, ERR_TABLE_TOO_LARGE, ERR_INVALID_ARITY,
    };
    
    #[cfg(feature = "conlat")]
    pub use crate::{CongruenceLattice, CongruenceLatticeBuilder};
}

/// Common type aliases for better ergonomics
pub type AlgebraResult<T> = Result<T, UACalcError>;
pub type OperationTable = FlatOperationTable;
pub type PartitionResult<T> = Result<T, UACalcError>;
pub type RelationResult<T> = Result<T, UACalcError>;

