pub mod basic_algebra;
pub mod basic_operation;
pub mod algebra_with_generating_vector;
pub mod big_product_algebra;
pub mod closer;
pub mod closer_timing;
pub mod free_algebra;
pub mod general_algebra;
pub mod homomorphism;
pub mod malcev;
pub mod maltsev_product_decomposition;
pub mod parameterized_algebra;
pub mod polin_like_algebra;
pub mod matrix_power_algebra;
pub mod power_algebra;
pub mod product_algebra;
pub mod reduct_algebra;
pub mod subalgebra;
pub mod unary_terms_monoid;
pub mod conlat;
pub mod op;
pub mod parallel;
pub mod sublat;
pub mod small_algebra;

// Re-export the main types that are used throughout the codebase
pub use basic_algebra::PyBasicAlgebra;
pub use op::operation::PyBasicOperation;
pub use conlat::basic_binary_relation::PyBasicBinaryRelation;
pub use conlat::centrality_data::PyCentralityData;
pub use conlat::partition::PyPartition;
pub use conlat::print_type::PyPrintType;
pub use conlat::congruence_lattice::{PyCongruenceLattice, PyCongruenceLatticeIntArray};
pub use op::similarity_type::PySimilarityType;
pub use op::parameterized_operation::PyParameterizedOperation;
pub use op::operations::PyOperations;
pub use op::operation_with_default_value::PyOperationWithDefaultValue;
pub use sublat::basic_set::PyBasicSet;
pub use sublat::subalgebra_lattice::PySubalgebraLattice;
pub use crate::alg::op::operation_symbol::PyOperationSymbol;

// Module registration function
use pyo3::prelude::*;
use crate::alg::homomorphism::PyHomomorphism;
use crate::alg::free_algebra::PyFreeAlgebra;
use crate::alg::product_algebra::PyProductAlgebra;
use crate::alg::power_algebra::PyPowerAlgebra;
use crate::alg::matrix_power_algebra::PyMatrixPowerAlgebra;
use crate::alg::subalgebra::PySubalgebra;
use crate::alg::reduct_algebra::PyReductAlgebra;
use crate::alg::unary_terms_monoid::PyUnaryTermsMonoid;
use crate::alg::polin_like_algebra::PyPolinLikeAlgebra;
use crate::alg::parameterized_algebra::PyParameterizedAlgebra;
use crate::alg::maltsev_product_decomposition::PyMaltsevProductDecomposition;
use crate::alg::general_algebra::PyGeneralAlgebra;
use crate::alg::conlat::polymorphisms::PyPolymorphisms;
use crate::alg::conlat::subtrace::PySubtrace;
use crate::alg::conlat::type_finder::PyTypeFinder;
use crate::alg::op::int_operation::PyIntOperation;
use crate::alg::op::abstract_int_operation::PyAbstractIntOperation;
use crate::alg::op::abstract_operation::PyAbstractOperationNew;
use crate::alg::parallel::PyPool;
use crate::alg::closer::register_closer;
use crate::alg::closer_timing::register_closer_timing;

pub fn register_alg_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyOperationSymbol>()?;
    m.add_class::<PyBasicOperation>()?;
    m.add_class::<PyBasicAlgebra>()?;
    m.add_class::<PyIntOperation>()?;
    m.add_class::<PyAbstractIntOperation>()?;
    m.add_class::<PyAbstractOperationNew>()?;
    m.add_class::<PyOperations>()?;
    m.add_class::<PyOperationWithDefaultValue>()?;
    m.add_class::<PyHomomorphism>()?;
    m.add_class::<PySubalgebraLattice>()?;
    m.add_class::<PyBasicBinaryRelation>()?;
    m.add_class::<PyCentralityData>()?;
    m.add_class::<PySimilarityType>()?;
    m.add_class::<PyPartition>()?;
    m.add_class::<PyPrintType>()?;
    m.add_class::<PyCongruenceLattice>()?;
    m.add_class::<PyCongruenceLatticeIntArray>()?;
    m.add_class::<PyParameterizedOperation>()?;
    m.add_class::<PyBasicSet>()?;
    m.add_class::<PyFreeAlgebra>()?;
    m.add_class::<PyProductAlgebra>()?;
    m.add_class::<PyPowerAlgebra>()?;
    m.add_class::<PyMatrixPowerAlgebra>()?;
    m.add_class::<PySubalgebra>()?;
    m.add_class::<PyReductAlgebra>()?;
    m.add_class::<PyUnaryTermsMonoid>()?;
    m.add_class::<PyPolinLikeAlgebra>()?;
    m.add_class::<PyParameterizedAlgebra>()?;
    m.add_class::<PyMaltsevProductDecomposition>()?;
    m.add_class::<PyGeneralAlgebra>()?;
    m.add_class::<PyPolymorphisms>()?;
    m.add_class::<PySubtrace>()?;
    m.add_class::<PyTypeFinder>()?;
    m.add_class::<PyPool>()?;

    // Register closer module components
    closer::register_closer(_py, m)?;
    closer_timing::register_closer_timing(_py, m)?;

    // Export only clean names (without Py prefix)
    m.add("Closer", m.getattr("PyCloser")?)?;
    m.add("CloserTiming", m.getattr("PyCloserTiming")?)?;
    m.add("OperationSymbol", m.getattr("PyOperationSymbol")?)?;
    m.add("BasicOperation", m.getattr("PyBasicOperation")?)?;
    m.add("BasicAlgebra", m.getattr("PyBasicAlgebra")?)?;
    m.add("IntOperation", m.getattr("PyIntOperation")?)?;
    m.add("AbstractIntOperation", m.getattr("PyAbstractIntOperation")?)?;
    m.add("AbstractOperation", m.getattr("PyAbstractOperationNew")?)?;
    m.add("Operations", m.getattr("PyOperations")?)?;
    m.add("OperationWithDefaultValue", m.getattr("PyOperationWithDefaultValue")?)?;
    m.add("Homomorphism", m.getattr("PyHomomorphism")?)?;
    m.add("SubalgebraLattice", m.getattr("PySubalgebraLattice")?)?;
    m.add("BasicBinaryRelation", m.getattr("PyBasicBinaryRelation")?)?;
    m.add("SimilarityType", m.getattr("PySimilarityType")?)?;
    m.add("CentralityData", m.getattr("PyCentralityData")?)?;
    m.add("Partition", m.getattr("PyPartition")?)?;
    m.add("PrintType", m.getattr("PyPrintType")?)?;
    m.add("CongruenceLattice", m.getattr("PyCongruenceLattice")?)?;
    m.add("ParameterizedOperation", m.getattr("PyParameterizedOperation")?)?;
    m.add("BasicSet", m.getattr("PyBasicSet")?)?;
    m.add("FreeAlgebra", m.getattr("PyFreeAlgebra")?)?;
    m.add("ProductAlgebra", m.getattr("PyProductAlgebra")?)?;
    m.add("PowerAlgebra", m.getattr("PyPowerAlgebra")?)?;
    m.add("MatrixPowerAlgebra", m.getattr("PyMatrixPowerAlgebra")?)?;
    m.add("Subalgebra", m.getattr("PySubalgebra")?)?;
    m.add("ReductAlgebra", m.getattr("PyReductAlgebra")?)?;
    m.add("UnaryTermsMonoid", m.getattr("PyUnaryTermsMonoid")?)?;
    m.add("PolinLikeAlgebra", m.getattr("PyPolinLikeAlgebra")?)?;
    m.add("ParameterizedAlgebra", m.getattr("PyParameterizedAlgebra")?)?;
    m.add("MaltsevProductDecomposition", m.getattr("PyMaltsevProductDecomposition")?)?;
    m.add("GeneralAlgebra", m.getattr("PyGeneralAlgebra")?)?;
    m.add("Polymorphisms", m.getattr("PyPolymorphisms")?)?;
    m.add("Subtrace", m.getattr("PySubtrace")?)?;
    m.add("TypeFinder", m.getattr("PyTypeFinder")?)?;
    m.add("Pool", m.getattr("PyPool")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyPool")?;
    module_dict.del_item("PyCloser")?;
    module_dict.del_item("PyCloserTiming")?;
    module_dict.del_item("PyPolinLikeAlgebra")?;

    // Register malcev module-level functions
    malcev::register_malcev_functions(_py, m)?;

    Ok(())
}