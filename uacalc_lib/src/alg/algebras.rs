/* algebras.rs - Python bindings for Algebras functions
 *
 * This module provides Python bindings for all the Algebras static functions.
 */

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use crate::alg::PyBasicAlgebra;
use crate::alg::homomorphism::PyHomomorphism;
use crate::alg::op::int_operation::PyIntOperation;
use crate::alg::op::similarity_type::PySimilarityType;
use crate::alg::conlat::partition::PyPartition;
use crate::util::PyIntArray;
use uacalc::alg::op::Operation;
use uacalc::alg::algebras;

/// Python module for Algebras functions.
///
/// Since all Algebras methods are static functions in Java, we expose them
/// as module-level functions in Python.
pub fn register_algebras_functions(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_endomorphism, m)?)?;
    m.add_function(wrap_pyfunction!(is_homomorphism, m)?)?;
    m.add_function(wrap_pyfunction!(jonsson_terms, m)?)?;
    m.add_function(wrap_pyfunction!(jonsson_level, m)?)?;
    m.add_function(wrap_pyfunction!(find_nuf, m)?)?;
    m.add_function(wrap_pyfunction!(matrix_power, m)?)?;
    m.add_function(wrap_pyfunction!(ternary_discriminator_algebra, m)?)?;
    m.add_function(wrap_pyfunction!(member_of_quasivariety, m)?)?;
    m.add_function(wrap_pyfunction!(member_of_quasivariety_list, m)?)?;
    m.add_function(wrap_pyfunction!(member_of_quasivariety_gen_by_proper_subs, m)?)?;
    m.add_function(wrap_pyfunction!(make_random_algebra, m)?)?;
    m.add_function(wrap_pyfunction!(make_random_algebra_with_seed, m)?)?;
    m.add_function(wrap_pyfunction!(make_random_algebra_with_arities, m)?)?;
    m.add_function(wrap_pyfunction!(make_random_algebra_with_arities_and_seed, m)?)?;
    m.add_function(wrap_pyfunction!(full_transformation_semigroup, m)?)?;
    m.add_function(wrap_pyfunction!(quasi_critical_congruences, m)?)?;
    m.add_function(wrap_pyfunction!(quasi_critical, m)?)?;
    m.add_function(wrap_pyfunction!(unary_clone, m)?)?;

    Ok(())
}

/// Test if an operation is an endomorphism of an algebra.
///
/// An endomorphism is a unary operation that commutes with all operations
/// of the algebra.
///
/// # Arguments
/// * `endo` - The operation to test (must be unary, IntOperation)
/// * `alg` - The algebra to test against (BasicAlgebra)
///
/// # Returns
/// `True` if the operation is an endomorphism, `False` otherwise
///
/// # Raises
/// `ValueError` if the operation is not unary or there's an error
#[pyfunction]
fn is_endomorphism(endo: &PyIntOperation, alg: &PyBasicAlgebra) -> PyResult<bool> {
    match algebras::is_endomorphism(&endo.inner as &dyn Operation, &alg.inner) {
        Ok(result) => Ok(result),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Test if a map is a homomorphism from one algebra to another.
///
/// A homomorphism is a map h: A -> B such that for any operation f in alg0
/// and corresponding operation g in alg1 (with the same symbol), we have:
/// h(f(x1, x2, ..., xn)) = g(h(x1), h(x2), ..., h(xn))
///
/// # Arguments
/// * `map` - A list of integers defining the map from elements of alg0 to elements of alg1
/// * `alg0` - The source algebra (BasicAlgebra)
/// * `alg1` - The target algebra (BasicAlgebra)
///
/// # Returns
/// `True` if the map is a homomorphism, `False` otherwise
///
/// # Raises
/// `ValueError` if there's an error (e.g., map size mismatch, missing operation)
#[pyfunction]
fn is_homomorphism(map: Vec<i32>, alg0: &PyBasicAlgebra, alg1: &PyBasicAlgebra) -> PyResult<bool> {
    match algebras::is_homomorphism(&map, &alg0.inner, &alg1.inner) {
        Ok(result) => Ok(result),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find Jonsson terms for the algebra.
///
/// This returns a list of Jonsson terms witnessing congruence distributivity,
/// or None if the algebra does not generate a congruence distributive variety.
/// The returned terms are guaranteed to be the least number of terms possible.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// List of Jonsson terms as strings if they exist, None otherwise
///
/// # Raises
/// `ValueError` if there's an error during computation
#[pyfunction]
fn jonsson_terms(algebra: &PyBasicAlgebra) -> PyResult<Option<Vec<String>>> {
    match algebras::jonsson_terms(&algebra.inner) {
        Ok(Some(terms)) => {
            let term_strings: Vec<String> = terms.iter().map(|t| format!("{}", t)).collect();
            Ok(Some(term_strings))
        },
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Get the Jonsson level for the algebra.
///
/// If the algebra generates a distributive variety, this returns the minimal
/// number of Jonsson terms minus 1; otherwise it returns -1.
/// For congruence distributivity testing, it's probably better to use
/// `jonsson_terms` to get the actual terms.
///
/// If the algebra has only one element, it returns 1.
/// For a lattice it returns 2.
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
///
/// # Returns
/// The Jonsson level (minimal number of Jonsson terms minus 1), or -1 if not distributive
///
/// # Raises
/// `ValueError` if there's an error during computation
#[pyfunction]
fn jonsson_level(algebra: &PyBasicAlgebra) -> PyResult<i32> {
    match algebras::jonsson_level(&algebra.inner) {
        Ok(level) => Ok(level),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find a near unanimity term (NUF) of the given arity.
///
/// This will find a near unanimity term of the given arity if one exists;
/// otherwise it returns None.
///
/// A near unanimity term of arity n is a term t(x₀, x₁, ..., xₙ₋₁) such that:
/// - t(y,x,x,...,x) = x
/// - t(x,y,x,...,x) = x
/// - ...
/// - t(x,x,x,...,y) = x
///
/// # Arguments
/// * `algebra` - The algebra to check (BasicAlgebra)
/// * `arity` - The arity of the NU term (must be at least 3)
///
/// # Returns
/// The NU term as a string if one exists, None otherwise
///
/// # Raises
/// `ValueError` if arity is less than 3 or there's an error during computation
#[pyfunction]
fn find_nuf(algebra: &PyBasicAlgebra, arity: usize) -> PyResult<Option<String>> {
    match algebras::find_nuf(&algebra.inner, arity) {
        Ok(Some(term)) => Ok(Some(format!("{}", term))),
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// The matrix power algebra as defined in Hobby-McKenzie.
///
/// Creates a matrix power algebra A^[k] from a given algebra A and power k.
/// This is a BasicAlgebra that contains:
/// - All operations from the power algebra A^k
/// - A binary left shift operation
///
/// # Arguments
/// * `alg` - The root algebra to raise to a power (BasicAlgebra)
/// * `k` - The power/exponent (number of copies)
///
/// # Returns
/// A BasicAlgebra representing the matrix power algebra
///
/// # Raises
/// `ValueError` if k is not positive or there's an error during creation
#[pyfunction]
fn matrix_power(alg: &PyBasicAlgebra, k: i32) -> PyResult<PyBasicAlgebra> {
    let rust_alg = Box::new(alg.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
    
    match algebras::matrix_power(rust_alg, k) {
        Ok(result) => Ok(PyBasicAlgebra { inner: result }),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Create a ternary discriminator algebra.
///
/// A ternary discriminator algebra is an algebra with a single ternary operation
/// called the discriminator. The discriminator operation d(x,y,z) satisfies:
/// - d(x,y,z) = z if x = y
/// - d(x,y,z) = x if x ≠ y
///
/// # Arguments
/// * `card` - The cardinality of the algebra (size of the universe)
///
/// # Returns
/// A BasicAlgebra representing the ternary discriminator algebra
///
/// # Raises
/// `ValueError` if cardinality is not positive or there's an error during creation
#[pyfunction]
fn ternary_discriminator_algebra(card: i32) -> PyResult<PyBasicAlgebra> {
    match algebras::ternary_discriminator_algebra(card) {
        Ok(result) => Ok(PyBasicAlgebra { inner: result }),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Test if algebra A is in the quasivariety generated by algebra B.
///
/// Returns a list of homomorphisms from A into B if A is in the quasivariety;
/// otherwise returns None.
///
/// # Arguments
/// * `a` - The algebra to test for membership (BasicAlgebra)
/// * `b` - The generating algebra (BasicAlgebra)
///
/// # Returns
/// List of Homomorphism objects if A is in the quasivariety, None otherwise
///
/// # Raises
/// `ValueError` if there's an error during computation
#[pyfunction]
fn member_of_quasivariety(a: &PyBasicAlgebra, b: &PyBasicAlgebra) -> PyResult<Option<Vec<PyHomomorphism>>> {
    let a_box = Box::new(a.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
    let b_box = Box::new(b.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
    
    match algebras::member_of_quasivariety(a_box, b_box, None) {
        Ok(Some(homos)) => {
            let py_homos: Vec<PyHomomorphism> = homos.into_iter()
                .map(|h| PyHomomorphism::from_inner(h))
                .collect();
            Ok(Some(py_homos))
        },
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Test if algebra A is in the quasivariety generated by a list of algebras.
///
/// Returns a list of homomorphisms from A into the generating algebras if A is
/// in the quasivariety; otherwise returns None.
///
/// # Arguments
/// * `a` - The algebra to test for membership (BasicAlgebra)
/// * `gen_algs` - The list of generating algebras (list of BasicAlgebra)
///
/// # Returns
/// List of Homomorphism objects if A is in the quasivariety, None otherwise
///
/// # Raises
/// `ValueError` if there's an error during computation
#[pyfunction]
fn member_of_quasivariety_list(
    a: &PyBasicAlgebra,
    gen_algs: Vec<PyRef<'_, PyBasicAlgebra>>,
) -> PyResult<Option<Vec<PyHomomorphism>>> {
    let a_box = Box::new(a.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
    let gen_algs_box: Vec<Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>> = gen_algs.iter()
        .map(|alg| Box::new(alg.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>)
        .collect();
    
    match algebras::member_of_quasivariety_list(a_box, gen_algs_box, None) {
        Ok(Some(homos)) => {
            let py_homos: Vec<PyHomomorphism> = homos.into_iter()
                .map(|h| PyHomomorphism::from_inner(h))
                .collect();
            Ok(Some(py_homos))
        },
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Test if algebra A can be embedded into a product of proper subalgebras of A.
///
/// This checks if A is in the quasivariety generated by its proper subalgebras.
/// Returns a list of homomorphisms from A into A (with non-zero kernels) if A
/// can be embedded; otherwise returns None.
///
/// # Arguments
/// * `a` - The algebra to test (BasicAlgebra)
///
/// # Returns
/// List of Homomorphism objects if A can be embedded, None otherwise
///
/// # Raises
/// `ValueError` if there's an error during computation
#[pyfunction]
fn member_of_quasivariety_gen_by_proper_subs(a: &PyBasicAlgebra) -> PyResult<Option<Vec<PyHomomorphism>>> {
    let a_box = Box::new(a.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
    
    match algebras::member_of_quasivariety_gen_by_proper_subs(a_box, None) {
        Ok(Some(homos)) => {
            let py_homos: Vec<PyHomomorphism> = homos.into_iter()
                .map(|h| PyHomomorphism::from_inner(h))
                .collect();
            Ok(Some(py_homos))
        },
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Make a random algebra of a given similarity type.
///
/// Creates a random algebra with the specified size and similarity type.
/// The operations are generated randomly.
///
/// # Arguments
/// * `n` - The size of the algebra (cardinality of the universe)
/// * `sim_type` - The similarity type (defines the operations)
///
/// # Returns
/// BasicAlgebra: A new random algebra
///
/// # Raises
/// `ValueError` if there's an error during creation
#[pyfunction]
fn make_random_algebra(n: i32, sim_type: &PySimilarityType) -> PyResult<PyBasicAlgebra> {
    match algebras::make_random_algebra(n, &sim_type.get_inner()) {
        Ok(result) => Ok(PyBasicAlgebra { inner: result }),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Make a random algebra of a given similarity type with a seed.
///
/// Creates a random algebra with the specified size and similarity type.
/// The operations are generated randomly using the provided seed for reproducibility.
///
/// # Arguments
/// * `n` - The size of the algebra (cardinality of the universe)
/// * `sim_type` - The similarity type (defines the operations)
/// * `seed` - Optional seed for the random number generator (None means use random seed)
///
/// # Returns
/// BasicAlgebra: A new random algebra
///
/// # Raises
/// `ValueError` if there's an error during creation
#[pyfunction]
#[pyo3(signature = (n, sim_type, seed=None))]
fn make_random_algebra_with_seed(n: i32, sim_type: &PySimilarityType, seed: Option<i64>) -> PyResult<PyBasicAlgebra> {
    match algebras::make_random_algebra_with_seed(n, &sim_type.get_inner(), seed) {
        Ok(result) => Ok(PyBasicAlgebra { inner: result }),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Make a random algebra with given arities of the operations.
///
/// Creates a random algebra with the specified size and operation arities.
/// Operation symbols are automatically created as "r0", "r1", etc.
///
/// # Arguments
/// * `n` - The size of the algebra (cardinality of the universe)
/// * `arities` - List of arities for the operations
///
/// # Returns
/// BasicAlgebra: A new random algebra
///
/// # Raises
/// `ValueError` if there's an error during creation
#[pyfunction]
fn make_random_algebra_with_arities(n: i32, arities: Vec<i32>) -> PyResult<PyBasicAlgebra> {
    match algebras::make_random_algebra_with_arities(n, &arities) {
        Ok(result) => Ok(PyBasicAlgebra { inner: result }),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Make a random algebra with given arities of the operations and a seed.
///
/// Creates a random algebra with the specified size and operation arities.
/// Operation symbols are automatically created as "r0", "r1", etc.
/// The operations are generated randomly using the provided seed for reproducibility.
///
/// # Arguments
/// * `n` - The size of the algebra (cardinality of the universe)
/// * `arities` - List of arities for the operations
/// * `seed` - Optional seed for the random number generator (None means use random seed)
///
/// # Returns
/// BasicAlgebra: A new random algebra
///
/// # Raises
/// `ValueError` if there's an error during creation
#[pyfunction]
#[pyo3(signature = (n, arities, seed=None))]
fn make_random_algebra_with_arities_and_seed(n: i32, arities: Vec<i32>, seed: Option<i64>) -> PyResult<PyBasicAlgebra> {
    match algebras::make_random_algebra_with_arities_and_seed(n, &arities, seed) {
        Ok(result) => Ok(PyBasicAlgebra { inner: result }),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Create the full transformation semigroup on n elements.
///
/// The transformation semigroup consists of all functions from {0..n-1} to {0..n-1}.
/// Each transformation is encoded as a Horner integer.
///
/// # Arguments
/// * `n` - The size of the underlying set (must be at most 9)
/// * `include_constants` - Whether to include constant transformations (one for each element)
/// * `include_id` - Whether to include the identity transformation
///
/// # Returns
/// A BasicAlgebra representing the transformation semigroup algebra
///
/// # Raises
/// `ValueError` if n > 9 or there's an error during creation
#[pyfunction]
fn full_transformation_semigroup(n: i32, include_constants: bool, include_id: bool) -> PyResult<PyBasicAlgebra> {
    match algebras::full_transformation_semigroup(n, include_constants, include_id) {
        Ok(result) => Ok(PyBasicAlgebra { inner: result }),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Find all quasi-critical congruences of an algebra.
///
/// A congruence theta is quasi-critical if A/theta is quasi-critical,
/// i.e., A/theta is not a subdirect product of proper subalgebras.
///
/// # Arguments
/// * `a` - The algebra to analyze (BasicAlgebra)
///
/// # Returns
/// List of Partition objects representing quasi-critical congruences
///
/// # Raises
/// `ValueError` if there's an error during computation
#[pyfunction]
fn quasi_critical_congruences(a: &PyBasicAlgebra) -> PyResult<Vec<PyPartition>> {
    let a_box = Box::new(a.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
    
    match algebras::quasi_critical_congruences(a_box, None) {
        Ok(partitions) => {
            let py_partitions: Vec<PyPartition> = partitions.into_iter()
                .map(|p| PyPartition::from_inner(p))
                .collect();
            Ok(py_partitions)
        },
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Determine if an algebra is quasi-critical.
///
/// An algebra is quasi-critical if it is not a subdirect product of proper subalgebras.
/// This method returns a dictionary mapping congruences to subalgebra generators if
/// the algebra is quasi-critical, or None if it is not.
///
/// Note: This has been replaced by `member_of_quasivariety_gen_by_proper_subs` in newer code,
/// but is kept for compatibility.
///
/// # Arguments
/// * `a` - The algebra to test (BasicAlgebra)
///
/// # Returns
/// Dictionary mapping Partition objects to lists of generator indices if quasi-critical, None otherwise
///
/// # Raises
/// `ValueError` if there's an error during computation
#[pyfunction]
fn quasi_critical(py: Python, a: &PyBasicAlgebra) -> PyResult<Option<PyObject>> {
    use pyo3::types::PyDict;
    
    let a_box = Box::new(a.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
    
    match algebras::quasi_critical(a_box, None) {
        Ok(Some(map)) => {
            let py_dict = PyDict::new(py);
            for (partition, gens) in map {
                let py_partition = PyPartition::from_inner(partition);
                // Convert PyPartition to PyObject for use as dict key
                let py_partition_obj = Py::new(py, py_partition)?.into_py(py);
                py_dict.set_item(py_partition_obj, gens)?;
            }
            Ok(Some(py_dict.into()))
        },
        Ok(None) => Ok(None),
        Err(e) => Err(PyValueError::new_err(e)),
    }
}

/// Compute the unary clone set from partitions.
///
/// This function computes the set of all unary operations (represented as IntArray)
/// that respect every partition in `pars` and also respect the partitions `eta0` and `eta1`,
/// which meet and join to 0 and 1 and permute.
///
/// # Arguments
/// * `pars` - List of partitions that the operations must respect
/// * `eta0` - First eta partition
/// * `eta1` - Second eta partition
///
/// # Returns
/// Set of IntArray objects representing unary operations
///
/// # Raises
/// `ValueError` if there's an error (e.g., empty partitions list or mismatched sizes)
#[pyfunction]
fn unary_clone(
    pars: Vec<PyRef<'_, PyPartition>>,
    eta0: &PyPartition,
    eta1: &PyPartition,
) -> PyResult<Vec<PyIntArray>> {
    let pars_rust: Vec<uacalc::alg::conlat::partition::Partition> = pars.iter()
        .map(|p| p.inner.clone())
        .collect();
    
    match algebras::unary_clone(&pars_rust, &eta0.inner, &eta1.inner) {
        Ok(clone_set) => {
            let py_arrays: Vec<PyIntArray> = clone_set.into_iter()
                .map(|ia| PyIntArray { inner: ia })
                .collect();
            Ok(py_arrays)
        },
        Err(e) => Err(PyValueError::new_err(e)),
    }
}
