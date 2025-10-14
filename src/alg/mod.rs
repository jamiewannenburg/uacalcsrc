pub mod algebra;
pub mod conlat;
pub mod general_algebra;
pub mod op;
pub mod parallel;
pub mod small_algebra;
pub mod sublat;

// Re-export partition types for convenience
pub use conlat::partition::{Partition, PrintType};

// Re-export algebra types
pub use algebra::{
    Algebra, CloneableAlgebra, BoxedAlgebra, boxed_algebra, ProgressMonitor,
    CARDINALITY_UNKNOWN, CARDINALITY_FINITE, CARDINALITY_INFINITE,
    CARDINALITY_COUNTABLE, CARDINALITY_COUNTABLY_INFINITE
};

// Re-export concrete algebra implementations
pub use general_algebra::GeneralAlgebra;
pub use small_algebra::{SmallAlgebra, BasicSmallAlgebra, AlgebraType};

// BasicAlgebra is now implemented as BasicSmallAlgebra
// GeneralAlgebra is now implemented in general_algebra.rs

pub struct FreeAlgebra {
    // TODO: Implement free algebra structure
}

pub struct ProductAlgebra {
    // TODO: Implement product algebra structure
}

pub struct Subalgebra {
    // TODO: Implement subalgebra structure
}

pub struct QuotientAlgebra {
    // TODO: Implement quotient algebra structure
}

pub struct Homomorphism {
    // TODO: Implement homomorphism structure
}

pub struct Closer {
    // TODO: Implement closer structure
}

pub struct Algebras {
    // TODO: Implement algebras collection
}

pub struct AlgebraFromMinimalSets {
    // TODO: Implement algebra from minimal sets
}

pub struct AlgebraWithGeneratingVector {
    // TODO: Implement algebra with generating vector
}

pub struct BigProductAlgebra {
    // TODO: Implement big product algebra
}

pub struct MatrixPowerAlgebra {
    // TODO: Implement matrix power algebra
}

pub struct ParameterizedAlgebra {
    // TODO: Implement parameterized algebra
}

pub struct PolinLikeAlgebra {
    // TODO: Implement Polin-like algebra
}

pub struct PowerAlgebra {
    // TODO: Implement power algebra
}

pub struct ReductAlgebra {
    // TODO: Implement reduct algebra
}

pub struct SubProductAlgebra {
    // TODO: Implement subproduct algebra
}

pub struct UnaryTermsMonoid {
    // TODO: Implement unary terms monoid
}

pub struct MaltsevDecompositionIterator {
    // TODO: Implement Maltsev decomposition iterator
}

pub struct MaltsevProductDecomposition {
    // TODO: Implement Maltsev product decomposition
}

pub struct Malcev {
    // TODO: Implement Malcev structure
}
