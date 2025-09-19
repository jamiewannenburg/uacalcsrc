//! Universal Algebra Calculator Core Library
//!
//! This library provides efficient implementations of universal algebra structures
//! and algorithms, ported from the Java UACalc implementation.

pub mod algebra;
pub mod binary_relation;
#[cfg(feature = "conlat")]
pub mod conlat;
pub mod error;
pub mod malcev;
#[cfg(feature = "memory-limit")]
pub mod memory;
#[cfg(feature = "term-eval")]
pub mod equation;
#[cfg(feature = "term-eval")]
pub mod presentation;
pub mod free_algebra;
pub mod operation;
pub mod partition;
pub mod permutation_group;
pub mod polymorphisms;
pub mod product;
pub mod quotient;
pub mod subalgebra;
#[cfg(feature = "taylor")]
pub mod taylor;
#[cfg(feature = "term-eval")]
pub mod term;
pub mod utils;

pub use algebra::{Algebra, BasicAlgebra, SmallAlgebra, Homomorphism, find_homomorphism, are_isomorphic};
pub use binary_relation::{
    empty_relation, equivalence_from_partition, identity_relation, universal_relation,
    BasicBinaryRelation, BinaryRelation,
};
pub use error::{UACalcError, UACalcResult};
pub use malcev::{
    MalcevAnalyzer, MalcevAnalysis, VarietyAnalysis, TctAnalysis, AdvancedProperties, LatticeProperties,
    analyze_malcev_conditions, analyze_variety_membership, analyze_tct_type, analyze_advanced_properties, analyze_lattice_properties
};
pub use free_algebra::{FreeAlgebra, VarietyConstraint, create_free_algebra, create_free_algebra_with_common_operations};
pub use operation::{
    FlatOperationTable, FunctionOperation, Operation, Operations, OperationSymbol, OperationType,
    TableOperation,
};
pub use partition::{coarsest_partition, finest_partition, BasicPartition, Partition};
pub use polymorphisms::{
    Polymorphism, PolymorphismType, PolymorphismAnalysis, PolymorphismDetector,
    find_unary_polymorphisms, find_binary_polymorphisms, analyze_polymorphisms,
    create_polymorphism_algebra, has_majority_polymorphism, has_minority_polymorphism,
    has_semilattice_polymorphism, has_maltsev_polymorphism
};
pub use permutation_group::{
    Permutation, PermutationGroupAnalysis, GroupElementOperations, SubgroupAnalysis,
    GroupHomomorphismAnalysis, PermutationGroupOperations,
    analyze_permutation_group, analyze_group_element_operations, analyze_subgroups,
    analyze_group_homomorphisms, analyze_permutation_group_operations,
    analyze_permutation_group_from_algebra, analyze_group_element_operations_from_algebra,
    analyze_subgroups_from_algebra, analyze_group_homomorphisms_from_algebras,
    analyze_permutation_group_operations_from_algebra,
};
pub use product::ProductAlgebra;
pub use quotient::QuotientAlgebra;
pub use subalgebra::Subalgebra;
pub use utils::{
    binomial_coefficient, estimate_table_memory, factorial, horner_decode, horner_encode,
    horner_table_size, power_checked, validate_operation_args, validate_partition_elements,
    validate_universe_contiguous, DEFAULT_CACHE_SIZE, ERR_INVALID_ARITY, ERR_INVALID_UNIVERSE,
    ERR_OVERFLOW, ERR_TABLE_TOO_LARGE, MAX_OPERATION_ARITY, MAX_TABLE_SIZE, MAX_UNIVERSE_SIZE,
    PERFORMANCE_THRESHOLD,
};

#[cfg(feature = "memory-limit")]
pub use memory::{
    set_memory_limit, get_memory_limit, get_allocated_memory, get_peak_allocated_memory,
    would_exceed_limit, estimate_free_algebra_memory, check_free_algebra_memory_limit,
};

#[cfg(feature = "conlat")]
pub use conlat::{
    cg, find_join_irreducibles, principal_congruence, BasicCongruenceLattice, CongruenceLattice,
    CongruenceLatticeBuilder,
};

#[cfg(feature = "taylor")]
pub use taylor::{IntArray, Polynomial, PolynomialCoefficient, PolynomialExpansion, Taylor, TaylorSeries, TaylorSpec};
#[cfg(feature = "term-eval")]
pub use term::{eval_term, eval_term_int, term_to_table, EvaluationContext, Term, TermArena};
#[cfg(feature = "term-eval")]
pub use equation::{Equation, EquationComplexity, EquationProperties, ComplexityLevel};
#[cfg(feature = "term-eval")]
pub use presentation::{Presentation, PresentationProperties};

/// Re-export commonly used types
pub mod prelude {
    pub use crate::{
        coarsest_partition, empty_relation, equivalence_from_partition, finest_partition,
        identity_relation, universal_relation, Algebra, BasicAlgebra, BasicBinaryRelation,
        BasicPartition, BinaryRelation, FlatOperationTable, FreeAlgebra, FunctionOperation, 
        Homomorphism, Operation, OperationSymbol, OperationType, Partition, Polymorphism, 
        PolymorphismType, PolymorphismAnalysis, PolymorphismDetector, QuotientAlgebra, 
        SmallAlgebra, Subalgebra, TableOperation, UACalcError, UACalcResult, VarietyConstraint,
        are_isomorphic, create_free_algebra, create_free_algebra_with_common_operations, 
        find_homomorphism, MalcevAnalyzer, MalcevAnalysis, VarietyAnalysis, TctAnalysis, AdvancedProperties,
        analyze_malcev_conditions, analyze_variety_membership, analyze_tct_type, analyze_advanced_properties, analyze_lattice_properties,
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
    pub use crate::{eval_term, eval_term_int, term_to_table, EvaluationContext, Term, TermArena, Equation, EquationComplexity, EquationProperties, ComplexityLevel, Presentation, PresentationProperties};

    #[cfg(feature = "taylor")]
    pub use crate::taylor::{markovic_mckenzie_term, siggers_term, IntArray, Polynomial, PolynomialCoefficient, PolynomialExpansion, Taylor, TaylorSeries, TaylorSpec};
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
