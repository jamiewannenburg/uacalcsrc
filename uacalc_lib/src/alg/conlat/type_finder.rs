use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::conlat::partition::Partition;

/// Python wrapper for TypeFinder
#[pyclass]
pub struct PyTypeFinder {
    inner: uacalc::alg::conlat::TypeFinder<i32>,
}

#[pymethods]
impl PyTypeFinder {
    /// Create a new TypeFinder for the given algebra.
    ///
    /// Args:
    ///     alg (BasicSmallAlgebra): The algebra to analyze
    ///
    /// Raises:
    ///     ValueError: If initialization fails
    #[new]
    fn new(alg: &crate::alg::PyBasicSmallAlgebra) -> PyResult<Self> {
        let rust_alg = Box::new(alg.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::conlat::TypeFinder::new(rust_alg) {
            Ok(inner) => Ok(PyTypeFinder { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the size of the algebra.
    ///
    /// Returns:
    ///     int: The cardinality of the algebra
    fn alg_size(&self) -> i32 {
        self.inner.alg_size()
    }

    /// Initialize with the zero congruence.
    ///
    /// Raises:
    ///     ValueError: If initialization fails
    fn init(&mut self) -> PyResult<()> {
        match self.inner.init() {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Initialize with the given alpha partition.
    ///
    /// Args:
    ///     alpha (Partition): The partition to use as alpha
    ///
    /// Raises:
    ///     ValueError: If initialization fails
    fn init_with_alpha(&mut self, alpha: &crate::alg::PyPartition) -> PyResult<()> {
        match self.inner.init_with_alpha(alpha.get_inner().clone()) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Find the TCT type set of the algebra.
    ///
    /// Returns the set of all types appearing in the join irreducibles of the
    /// congruence lattice.
    ///
    /// Returns:
    ///     set: Set of TCT types (integers 1-5)
    ///
    /// Raises:
    ///     ValueError: If computation fails
    fn find_type_set(&mut self) -> PyResult<std::collections::HashSet<i32>> {
        match self.inner.find_type_set() {
            Ok(type_set) => Ok(type_set),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Test if the given pair is a beta subtrace.
    ///
    /// Args:
    ///     ia (IntArray): The pair to test
    ///     beta (Partition): The beta partition (must be join irreducible)
    ///
    /// Returns:
    ///     bool: True if the pair is a subtrace
    ///
    /// Raises:
    ///     ValueError: If beta is not join irreducible or other error
    fn is_subtrace(&mut self, ia: &crate::util::PyIntArray, beta: &crate::alg::PyPartition) -> PyResult<bool> {
        match self.inner.is_subtrace(&ia.inner, &beta.get_inner()) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Find a subtrace for beta over its lower cover.
    ///
    /// Args:
    ///     beta (Partition): The join irreducible congruence
    ///
    /// Returns:
    ///     Subtrace: The subtrace for this beta
    ///
    /// Raises:
    ///     ValueError: If beta is not join irreducible or computation fails
    fn find_subtrace(&mut self, beta: &crate::alg::PyPartition) -> PyResult<crate::alg::conlat::subtrace::PySubtrace> {
        match self.inner.find_subtrace(&beta.get_inner()) {
            Ok(subtrace) => Ok(crate::alg::conlat::subtrace::PySubtrace::from_inner(subtrace)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Find a subtrace for beta with the given alpha.
    ///
    /// Args:
    ///     beta (Partition): The join irreducible congruence
    ///     alpha (Partition): A congruence whose join with the lower cover of beta is not above beta
    ///
    /// Returns:
    ///     Subtrace: The subtrace for this beta/alpha pair
    ///
    /// Raises:
    ///     ValueError: If beta is not join irreducible or computation fails
    fn find_subtrace_with_alpha(&mut self, beta: &crate::alg::PyPartition, alpha: &crate::alg::PyPartition) -> PyResult<crate::alg::conlat::subtrace::PySubtrace> {
        match self.inner.find_subtrace_with_alpha(&beta.get_inner(), &alpha.get_inner()) {
            Ok(subtrace) => Ok(crate::alg::conlat::subtrace::PySubtrace::from_inner(subtrace)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Find a subtrace starting from the given pair.
    ///
    /// Args:
    ///     pair (IntArray): The initial pair to start from
    ///
    /// Returns:
    ///     Subtrace: The subtrace found
    ///
    /// Raises:
    ///     ValueError: If computation fails
    fn find_subtrace_from_pair(&mut self, pair: &crate::util::PyIntArray) -> PyResult<crate::alg::conlat::subtrace::PySubtrace> {
        match self.inner.find_subtrace_from_pair(&pair.inner) {
            Ok(subtrace) => Ok(crate::alg::conlat::subtrace::PySubtrace::from_inner(subtrace)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Find the type for beta over its lower cover.
    ///
    /// Args:
    ///     beta (Partition): The join irreducible congruence
    ///
    /// Returns:
    ///     int: The TCT type (1-5)
    ///
    /// Raises:
    ///     ValueError: If beta is not join irreducible or computation fails
    fn find_type(&mut self, beta: &crate::alg::PyPartition) -> PyResult<i32> {
        match self.inner.find_type(&beta.get_inner()) {
            Ok(typ) => Ok(typ),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Find the type for beta with the given alpha.
    ///
    /// Args:
    ///     beta (Partition): The join irreducible congruence
    ///     alpha (Partition): A congruence whose join with the lower cover of beta is not above beta
    ///
    /// Returns:
    ///     int: The TCT type (1-5)
    ///
    /// Raises:
    ///     ValueError: If beta is not join irreducible or computation fails
    fn find_type_with_alpha(&mut self, beta: &crate::alg::PyPartition, alpha: &crate::alg::PyPartition) -> PyResult<i32> {
        match self.inner.find_type_with_alpha(&beta.get_inner(), &alpha.get_inner()) {
            Ok(typ) => Ok(typ),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Find the type of a subtrace.
    ///
    /// Args:
    ///     subtrace (Subtrace): The subtrace to analyze
    ///
    /// Returns:
    ///     int: The TCT type (1-5)
    ///
    /// Raises:
    ///     ValueError: If computation fails
    fn find_type_from_subtrace(&self, subtrace: &crate::alg::conlat::subtrace::PySubtrace) -> PyResult<i32> {
        match self.inner.find_type_from_subtrace(subtrace.get_inner().clone()) {
            Ok(typ) => Ok(typ),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// String representation.
    fn __str__(&self) -> String {
        format!("TypeFinder(alg_size={})", self.inner.alg_size())
    }

    /// Debug representation.
    fn __repr__(&self) -> String {
        format!("TypeFinder(alg_size={})", self.inner.alg_size())
    }
}