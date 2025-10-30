pub mod basic_algebra;
pub mod basic_operation;
pub mod algebra_with_generating_vector;
pub mod big_product_algebra;
pub mod closer;
pub mod free_algebra;
pub mod general_algebra;
pub mod homomorphism;
pub mod malcev;
pub mod maltsev_product_decomposition;
pub mod parameterized_algebra;
pub mod matrix_power_algebra;
pub mod power_algebra;
pub mod product_algebra;
pub mod reduct_algebra;
pub mod subalgebra;
pub mod unary_terms_monoid;
pub mod operation_symbol;
pub mod conlat;
pub mod op;
pub mod parallel;
pub mod sublat;
pub mod small_algebra;

// Re-export the main types that are used throughout the codebase
pub use basic_algebra::PyBasicSmallAlgebra;
pub use basic_operation::PyBasicOperation;
pub use operation_symbol::PyOperationSymbol;
pub use small_algebra::PySubalgebraLattice;
pub use conlat::basic_binary_relation::PyBasicBinaryRelation;
pub use conlat::centrality_data::PyCentralityData;
pub use conlat::partition::PyPartition;
pub use op::similarity_type::PySimilarityType;
pub use op::parameterized_operation::PyParameterizedOperation;
pub use sublat::basic_set::PyBasicSet;
pub use sublat::subalgebra_lattice::PySubalgebraLattice;

// Re-export the main types that are used throughout the codebase
pub use basic_algebra::PyBasicSmallAlgebra;
pub use basic_operation::PyBasicOperation;
pub use operation_symbol::PyOperationSymbol;
pub use small_algebra::PySubalgebraLattice;
pub use conlat::basic_binary_relation::PyBasicBinaryRelation;
pub use conlat::centrality_data::PyCentralityData;
pub use conlat::partition::PyPartition;
pub use op::similarity_type::PySimilarityType;
pub use op::parameterized_operation::PyParameterizedOperation;

// Module registration function
use pyo3::prelude::*;

pub fn register_alg_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyOperationSymbol>()?;
    m.add_class::<PyBasicOperation>()?;
    m.add_class::<PyBasicSmallAlgebra>()?;
    m.add_class::<PySubalgebraLattice>()?;
    m.add_class::<PyBasicBinaryRelation>()?;
    m.add_class::<PyCentralityData>()?;
    m.add_class::<PySimilarityType>()?;
    m.add_class::<PyPartition>()?;
    m.add_class::<PyParameterizedOperation>()?;
    m.add_class::<PyBasicSet>()?;

    // Export only clean names (without Py prefix)
    m.add("OperationSymbol", m.getattr("PyOperationSymbol")?)?;
    m.add("BasicOperation", m.getattr("PyBasicOperation")?)?;
    m.add("BasicSmallAlgebra", m.getattr("PyBasicSmallAlgebra")?)?;
    m.add("SubalgebraLattice", m.getattr("PySubalgebraLattice")?)?;
    m.add("BasicBinaryRelation", m.getattr("PyBasicBinaryRelation")?)?;
    m.add("SimilarityType", m.getattr("PySimilarityType")?)?;
    m.add("CentralityData", m.getattr("PyCentralityData")?)?;
    m.add("Partition", m.getattr("PyPartition")?)?;
    m.add("ParameterizedOperation", m.getattr("PyParameterizedOperation")?)?;
    m.add("BasicSet", m.getattr("PyBasicSet")?)?;

    Ok(())
}