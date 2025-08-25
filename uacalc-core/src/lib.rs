//! Universal Algebra Calculator Core Library
//! 
//! This library provides efficient implementations of universal algebra structures
//! and algorithms, ported from the Java UACalc implementation.

pub mod algebra;
pub mod operation;
pub mod partition;
pub mod binary_relation;
pub mod conlat;
pub mod error;

pub use algebra::{Algebra, SmallAlgebra, BasicAlgebra};
pub use operation::{Operation, OperationSymbol, OperationType};
pub use partition::{Partition, BasicPartition};
pub use binary_relation::{BinaryRelation, BasicBinaryRelation};
pub use conlat::{CongruenceLattice, CongruenceLatticeBuilder};
pub use error::{UACalcError, UACalcResult};

/// Re-export commonly used types
pub mod prelude {
    pub use crate::{
        Algebra, SmallAlgebra, BasicAlgebra,
        Operation, OperationSymbol, OperationType,
        Partition, BasicPartition,
        BinaryRelation, BasicBinaryRelation,
        CongruenceLattice, CongruenceLatticeBuilder,
        UACalcError, UACalcResult,
    };
}

