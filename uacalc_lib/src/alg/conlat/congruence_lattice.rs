use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use pyo3::types::PyAny;

use crate::alg::basic_algebra::PyBasicAlgebra;
use crate::alg::conlat::partition::PyPartition;
use crate::alg::conlat::basic_binary_relation::PyBasicBinaryRelation;
use crate::util::PyIntArray;

/// Python wrapper for CongruenceLattice
#[pyclass]
pub struct PyCongruenceLattice {
    pub(crate) inner: uacalc::alg::conlat::CongruenceLattice<i32>,
}

// Rust-visible constructor for internal use (separate from the #[new] Python ctor)
impl PyCongruenceLattice {
    pub fn from_algebra(algebra: &PyBasicAlgebra) -> Self {
        use uacalc::alg::SmallAlgebraWrapper;
        let con_lat = uacalc::alg::conlat::CongruenceLattice::new(
            Box::new(SmallAlgebraWrapper::new(Box::new(algebra.inner.clone())))
        );
        // Java CongruenceLattice(SmallAlgebra) is lazy; do not precompute.
        PyCongruenceLattice {
            inner: con_lat,
        }
    }
}

#[pymethods]
impl PyCongruenceLattice {
    /// Create a new congruence lattice for an algebra.
    #[new]
    fn new(algebra: &Bound<'_, PyAny>) -> PyResult<Self> {
        if let Ok(alg) = algebra.extract::<PyRef<PyBasicAlgebra>>() {
            return Ok(Self::from_algebra(&alg));
        }
        if let Ok(inner) = algebra.getattr("_inner") {
            if let Ok(alg) = inner.extract::<PyRef<PyBasicAlgebra>>() {
                return Ok(Self::from_algebra(&alg));
            }
        }
        Err(PyRuntimeError::new_err(
            "CongruenceLattice() requires a BasicAlgebra / SmallAlgebra instance",
        ))
    }

    fn alg_size(&self) -> usize { self.inner.alg_size() }

    fn zero(&self) -> PyPartition { PyPartition { inner: self.inner.zero() } }

    fn one(&self) -> PyPartition { PyPartition { inner: self.inner.one() } }

    fn con_cardinality(&mut self) -> usize { self.inner.con_cardinality() }

    fn is_distributive(&mut self) -> bool { self.inner.is_distributive() }

    fn get_description(&self) -> String { self.inner.get_description() }

    fn __str__(&self) -> String { self.inner.to_string() }

    fn __repr__(&self) -> String { format!("CongruenceLattice({})", self.inner.to_string()) }

    fn tg(&mut self, a: usize, b: usize) -> PyResult<PyBasicBinaryRelation> {
        match self.inner.tg(a, b) {
            Ok(relation) => Ok(PyBasicBinaryRelation { inner: relation }),
            Err(e) => Err(PyRuntimeError::new_err(e)),
        }
    }

    fn generating_pair(&mut self, partition: &PyPartition) -> Option<PyIntArray> {
        self.inner.generating_pair(&partition.inner).map(|ia| PyIntArray { inner: ia })
    }

    fn find_coatom_above(&mut self, partition: &PyPartition) -> PyPartition {
        PyPartition { inner: self.inner.find_coatom_above(&partition.inner) }
    }

    fn find_join_irred(&mut self, a: &PyPartition, b: &PyPartition) -> Option<PyPartition> {
        self.inner.find_join_irred(&a.inner, &b.inner).map(|p| PyPartition { inner: p })
    }

    fn find_meet_irred(&mut self, a: &PyPartition, b: &PyPartition) -> Option<PyPartition> {
        self.inner.find_meet_irred(&a.inner, &b.inner).map(|p| PyPartition { inner: p })
    }

    fn join_irreducibles(&mut self) -> Vec<PyPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        let jis: &Vec<uacalc::alg::conlat::partition::Partition> = CongruenceLattice::join_irreducibles(&mut self.inner);
        jis.iter().map(|p| PyPartition { inner: p.clone() }).collect()
    }

    fn principals(&mut self) -> Vec<PyPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        let principals: &Vec<uacalc::alg::conlat::partition::Partition> = CongruenceLattice::principals(&mut self.inner);
        principals.iter().map(|p| PyPartition { inner: p.clone() }).collect()
    }

    fn atoms(&mut self) -> Vec<PyPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        let atoms: &Vec<uacalc::alg::conlat::partition::Partition> = CongruenceLattice::atoms(&mut self.inner);
        atoms.iter().map(|p| PyPartition { inner: p.clone() }).collect()
    }

    fn meet_irreducibles(&mut self) -> Vec<PyPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        let mis: &Vec<uacalc::alg::conlat::partition::Partition> = CongruenceLattice::meet_irreducibles(&mut self.inner);
        mis.iter().map(|p| PyPartition { inner: p.clone() }).collect()
    }

    fn join_irreducibles_po(&mut self) -> PyResult<crate::lat::PyOrderedSetPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        match CongruenceLattice::join_irreducibles_po(&mut self.inner) {
            Ok(ordered_set) => Ok(crate::lat::PyOrderedSetPartition {
                inner: std::sync::Arc::new(std::sync::Mutex::new(ordered_set)),
            }),
            Err(e) => Err(PyRuntimeError::new_err(format!("Failed to create OrderedSet: {}", e))),
        }
    }

    fn meet_irreducibles_po(&mut self) -> PyResult<crate::lat::PyOrderedSetPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        match CongruenceLattice::meet_irreducibles_po(&mut self.inner) {
            Ok(ordered_set) => Ok(crate::lat::PyOrderedSetPartition {
                inner: std::sync::Arc::new(std::sync::Mutex::new(ordered_set)),
            }),
            Err(e) => Err(PyRuntimeError::new_err(format!("Failed to create OrderedSet: {}", e))),
        }
    }

    fn universe(&mut self) -> Vec<PyPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        let univ: &Vec<uacalc::alg::conlat::partition::Partition> = CongruenceLattice::universe(&mut self.inner);
        univ.iter().map(|p| PyPartition { inner: p.clone() }).collect()
    }

    fn permutability_level(&mut self) -> i32 { self.inner.permutability_level() }

    fn cg(&mut self, a: usize, b: usize) -> PyPartition { PyPartition { inner: self.inner.cg(a, b) } }

    fn complements(&mut self, partition: &PyPartition) -> Vec<PyPartition> {
        self.inner
            .complements(&partition.inner)
            .into_iter()
            .map(|p| PyPartition { inner: p })
            .collect()
    }

    fn find_principal_chain(&mut self) -> Vec<PyPartition> {
        self.inner
            .find_principal_chain()
            .into_iter()
            .map(|p| PyPartition { inner: p })
            .collect()
    }

    fn find_upper_cover(&mut self, congr: &PyPartition) -> Option<PyPartition> {
        self.inner
            .find_upper_cover(&congr.inner)
            .map(|p| PyPartition { inner: p })
    }

    fn irredundant_meet_decomposition(&mut self) -> Vec<PyPartition> {
        self.inner
            .irredundant_meet_decomposition()
            .into_iter()
            .map(|p| PyPartition { inner: p })
            .collect()
    }

    fn find_maximal_chain(&mut self) -> Vec<PyPartition> {
        self.inner
            .find_maximal_chain()
            .into_iter()
            .map(|p| PyPartition { inner: p })
            .collect()
    }

    fn idempotent_polynomials(&mut self) -> PyResult<Vec<PyIntArray>> {
        match self.inner.idempotent_polynomials() {
            Ok(polynomials) => Ok(polynomials
                .into_iter()
                .map(|ia| PyIntArray { inner: ia })
                .collect()),
            Err(e) => Err(PyRuntimeError::new_err(e)),
        }
    }

    fn delta(&mut self, alpha: &PyPartition, beta: &PyPartition) -> PyPartition {
        PyPartition { inner: self.inner.delta(&alpha.inner, &beta.inner) }
    }

    fn commutator2(&mut self, alpha: &PyPartition, beta: &PyPartition) -> PyPartition {
        PyPartition { inner: self.inner.commutator2(&alpha.inner, &beta.inner) }
    }

    fn centralizes(&self, s: &PyBasicBinaryRelation, t: &PyBasicBinaryRelation, delta: &PyPartition) -> bool {
        self.inner.centralizes(&s.inner, &t.inner, &delta.inner)
    }

    /// Get the cardinality of the congruence lattice.
    ///
    /// Returns:
    ///     int: The cardinality
    fn cardinality(&mut self) -> usize {
        self.con_cardinality()
    }

    /// Get the BasicLattice view of this congruence lattice.
    ///
    /// Args:
    ///     make_if_null (bool, optional): Create the BasicLattice if it doesn't exist. Defaults to True.
    ///
    /// Returns:
    ///     BasicLattice: The BasicLattice view, or None if creation fails
    fn get_basic_lattice(&mut self, make_if_null: Option<bool>) -> PyResult<Option<crate::lat::PyBasicLattice>> {
        use uacalc::lat::Lattice;
        use crate::lat::PyBasicLattice;
        let make = make_if_null.unwrap_or(true);
        
        // Ensure universe is computed
        let _ = self.inner.con_cardinality();
        
        // Convert CongruenceLattice<i32> to BasicLattice using new_from_lattice
        // CongruenceLattice<i32> implements Lattice<Partition>
        match uacalc::lat::BasicLattice::new_from_lattice(
            "CongruenceLattice".to_string(),
            &self.inner as &dyn Lattice<uacalc::alg::conlat::Partition>,
        ) {
            Ok(basic_lat) => {
                // Wrap in Arc<Mutex> for thread safety
                use crate::lat::BasicLatticeInner;
                Ok(Some(PyBasicLattice {
                    inner: BasicLatticeInner::Partition(std::sync::Arc::new(std::sync::Mutex::new(basic_lat))),
                }))
            }
            Err(e) => {
                if make {
                    Err(pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create BasicLattice: {}", e)))
                } else {
                    Ok(None)
                }
            }
        }
    }

    /// Get the BasicLattice view (default: create if null).
    ///
    /// Returns:
    ///     BasicLattice: The BasicLattice view, or None if creation fails
    fn get_basic_lattice_default(&mut self) -> PyResult<Option<crate::lat::PyBasicLattice>> {
        self.get_basic_lattice(Some(true))
    }

    fn get_name(&self) -> String {
        format!("Con({})", self.inner.get_algebra_name())
    }

    fn get_algebra_name(&self) -> String {
        self.inner.get_algebra_name().to_string()
    }

    fn cg_partition(&self, part: &PyPartition) -> PyResult<PyPartition> {
        if part.inner.universe_size() != self.inner.alg_size() {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "partition universe size {} does not match algebra size {}",
                part.inner.universe_size(),
                self.inner.alg_size()
            )));
        }
        Ok(PyPartition {
            inner: self.inner.cg_partition(&part.inner),
        })
    }

    fn is_total(&self) -> bool {
        true
    }

    fn is_unary(&self) -> bool {
        false
    }

    fn is_idempotent(&self) -> bool {
        true
    }

    fn universe_found(&self) -> bool {
        self.inner.universe_found()
    }

    fn join_irreducible(&mut self, part: &PyPartition) -> bool {
        self.inner.join_irreducible(&part.inner)
    }

    fn meet_irreducible(&mut self, part: &PyPartition) -> bool {
        self.inner.meet_irreducible(&part.inner)
    }

    fn join_prime(&mut self, beta: &PyPartition) -> bool {
        self.inner.join_prime(&beta.inner)
    }

    fn lower_star(&mut self, beta: &PyPartition) -> Option<PyPartition> {
        self.inner
            .lower_star(&beta.inner)
            .map(|p| PyPartition { inner: p })
    }

    fn is_smaller_than(&mut self, size: usize) -> bool {
        self.inner.is_smaller_than(size)
    }

    fn is_drawable(&mut self) -> bool {
        self.inner.is_drawable()
    }

    fn set_description(&mut self, desc: Option<String>) {
        self.inner.set_description(desc.unwrap_or_default());
    }

    fn make_universe(&mut self) {
        self.inner.make_universe();
    }

    fn make_principals(&mut self) {
        self.inner.make_principals();
    }

    fn make_atoms(&mut self) {
        self.inner.make_atoms();
    }

    fn make_join_irreducibles(&mut self) {
        self.inner.make_join_irreducibles();
    }

    fn get_universe_list(&mut self) -> Vec<PyPartition> {
        self.universe()
    }

    fn lattice_join(&self, a: &PyPartition, b: &PyPartition) -> PyResult<PyPartition> {
        match a.inner.join(&b.inner) {
            Ok(inner) => Ok(PyPartition { inner }),
            Err(e) => Err(PyRuntimeError::new_err(e)),
        }
    }

    fn lattice_meet(&self, a: &PyPartition, b: &PyPartition) -> PyResult<PyPartition> {
        match a.inner.meet(&b.inner) {
            Ok(inner) => Ok(PyPartition { inner }),
            Err(e) => Err(PyRuntimeError::new_err(e)),
        }
    }

    fn lattice_leq(&self, a: &PyPartition, b: &PyPartition) -> bool {
        a.inner.leq(&b.inner)
    }

    fn input_size(&mut self) -> i32 {
        use uacalc::alg::Algebra;
        let _ = self.inner.con_cardinality();
        Algebra::input_size(&self.inner)
    }

    fn upper_covers_map(&mut self) -> Vec<(PyPartition, Vec<PyPartition>)> {
        self.inner
            .upper_covers_map()
            .iter()
            .map(|(k, vs)| {
                (
                    PyPartition { inner: k.clone() },
                    vs.iter()
                        .map(|p| PyPartition { inner: p.clone() })
                        .collect(),
                )
            })
            .collect()
    }

    fn join_irreducibles_found(&self) -> bool {
        self.inner.join_irreducibles_found()
    }

    fn get_permutability_level_witnesses(&self) -> Option<Vec<PyPartition>> {
        self.inner.get_permutability_level_witnesses().map(|pair| {
            vec![
                PyPartition {
                    inner: pair[0].clone(),
                },
                PyPartition {
                    inner: pair[1].clone(),
                },
            ]
        })
    }

    #[staticmethod]
    fn minimal_elements(pars: Vec<PyRef<PyPartition>>) -> Vec<PyPartition> {
        // Java assumes a topologically sorted list and only compares
        // against elements already accepted.
        let mut out: Vec<PyPartition> = Vec::new();
        for p in &pars {
            let mut par_ok = true;
            for q in &out {
                if q.inner.leq(&p.inner) {
                    par_ok = false;
                    break;
                }
            }
            if par_ok {
                out.push(PyPartition {
                    inner: p.inner.clone(),
                });
            }
        }
        out
    }
}

/// Python wrapper for CongruenceLattice<IntArray>
#[pyclass]
pub struct PyCongruenceLatticeIntArray {
    pub(crate) inner: uacalc::alg::conlat::CongruenceLattice<uacalc::util::int_array::IntArray>,
}

#[pymethods]
impl PyCongruenceLatticeIntArray {
    fn alg_size(&self) -> usize { self.inner.alg_size() }

    fn zero(&self) -> PyPartition { PyPartition { inner: self.inner.zero() } }

    fn one(&self) -> PyPartition { PyPartition { inner: self.inner.one() } }

    fn con_cardinality(&mut self) -> usize { self.inner.con_cardinality() }

    fn cardinality(&mut self) -> usize { self.con_cardinality() }

    fn is_distributive(&mut self) -> bool { self.inner.is_distributive() }

    fn get_description(&self) -> String { self.inner.get_description() }

    fn __str__(&self) -> String { self.inner.to_string() }

    fn __repr__(&self) -> String { format!("CongruenceLattice({})", self.inner.to_string()) }

    fn tg(&mut self, a: usize, b: usize) -> PyResult<PyBasicBinaryRelation> {
        match self.inner.tg(a, b) {
            Ok(relation) => Ok(PyBasicBinaryRelation { inner: relation }),
            Err(e) => Err(PyRuntimeError::new_err(e)),
        }
    }

    fn generating_pair(&mut self, partition: &PyPartition) -> Option<PyIntArray> {
        self.inner.generating_pair(&partition.inner).map(|ia| PyIntArray { inner: ia })
    }

    fn find_coatom_above(&mut self, partition: &PyPartition) -> PyPartition {
        PyPartition { inner: self.inner.find_coatom_above(&partition.inner) }
    }

    fn find_join_irred(&mut self, a: &PyPartition, b: &PyPartition) -> Option<PyPartition> {
        self.inner.find_join_irred(&a.inner, &b.inner).map(|p| PyPartition { inner: p })
    }

    fn find_meet_irred(&mut self, a: &PyPartition, b: &PyPartition) -> Option<PyPartition> {
        self.inner.find_meet_irred(&a.inner, &b.inner).map(|p| PyPartition { inner: p })
    }

    fn join_irreducibles(&mut self) -> Vec<PyPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        let jis: &Vec<uacalc::alg::conlat::partition::Partition> = CongruenceLattice::join_irreducibles(&mut self.inner);
        jis.iter().map(|p| PyPartition { inner: p.clone() }).collect()
    }

    fn principals(&mut self) -> Vec<PyPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        let principals: &Vec<uacalc::alg::conlat::partition::Partition> = CongruenceLattice::principals(&mut self.inner);
        principals.iter().map(|p| PyPartition { inner: p.clone() }).collect()
    }

    fn atoms(&mut self) -> Vec<PyPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        let atoms: &Vec<uacalc::alg::conlat::partition::Partition> = CongruenceLattice::atoms(&mut self.inner);
        atoms.iter().map(|p| PyPartition { inner: p.clone() }).collect()
    }

    fn meet_irreducibles(&mut self) -> Vec<PyPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        let mis: &Vec<uacalc::alg::conlat::partition::Partition> = CongruenceLattice::meet_irreducibles(&mut self.inner);
        mis.iter().map(|p| PyPartition { inner: p.clone() }).collect()
    }

    fn join_irreducibles_po(&mut self) -> PyResult<crate::lat::PyOrderedSetPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        match CongruenceLattice::join_irreducibles_po(&mut self.inner) {
            Ok(ordered_set) => Ok(crate::lat::PyOrderedSetPartition {
                inner: std::sync::Arc::new(std::sync::Mutex::new(ordered_set)),
            }),
            Err(e) => Err(PyRuntimeError::new_err(format!("Failed to create OrderedSet: {}", e))),
        }
    }

    fn meet_irreducibles_po(&mut self) -> PyResult<crate::lat::PyOrderedSetPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        match CongruenceLattice::meet_irreducibles_po(&mut self.inner) {
            Ok(ordered_set) => Ok(crate::lat::PyOrderedSetPartition {
                inner: std::sync::Arc::new(std::sync::Mutex::new(ordered_set)),
            }),
            Err(e) => Err(PyRuntimeError::new_err(format!("Failed to create OrderedSet: {}", e))),
        }
    }

    fn universe(&mut self) -> Vec<PyPartition> {
        use uacalc::alg::conlat::CongruenceLattice;
        let univ: &Vec<uacalc::alg::conlat::partition::Partition> = CongruenceLattice::universe(&mut self.inner);
        univ.iter().map(|p| PyPartition { inner: p.clone() }).collect()
    }

    fn permutability_level(&mut self) -> i32 { self.inner.permutability_level() }

    fn cg(&mut self, a: usize, b: usize) -> PyPartition { PyPartition { inner: self.inner.cg(a, b) } }

    fn complements(&mut self, partition: &PyPartition) -> Vec<PyPartition> {
        self.inner
            .complements(&partition.inner)
            .into_iter()
            .map(|p| PyPartition { inner: p })
            .collect()
    }

    fn find_principal_chain(&mut self) -> Vec<PyPartition> {
        self.inner
            .find_principal_chain()
            .into_iter()
            .map(|p| PyPartition { inner: p })
            .collect()
    }

    fn find_upper_cover(&mut self, congr: &PyPartition) -> Option<PyPartition> {
        self.inner
            .find_upper_cover(&congr.inner)
            .map(|p| PyPartition { inner: p })
    }

    fn irredundant_meet_decomposition(&mut self) -> Vec<PyPartition> {
        self.inner
            .irredundant_meet_decomposition()
            .into_iter()
            .map(|p| PyPartition { inner: p })
            .collect()
    }

    fn find_maximal_chain(&mut self) -> Vec<PyPartition> {
        self.inner
            .find_maximal_chain()
            .into_iter()
            .map(|p| PyPartition { inner: p })
            .collect()
    }

    fn idempotent_polynomials(&mut self) -> PyResult<Vec<PyIntArray>> {
        match self.inner.idempotent_polynomials() {
            Ok(polynomials) => Ok(polynomials
                .into_iter()
                .map(|ia| PyIntArray { inner: ia })
                .collect()),
            Err(e) => Err(PyRuntimeError::new_err(e)),
        }
    }

    fn delta(&mut self, alpha: &PyPartition, beta: &PyPartition) -> PyPartition {
        PyPartition { inner: self.inner.delta(&alpha.inner, &beta.inner) }
    }

    fn commutator2(&mut self, alpha: &PyPartition, beta: &PyPartition) -> PyPartition {
        PyPartition { inner: self.inner.commutator2(&alpha.inner, &beta.inner) }
    }

    fn centralizes(&self, s: &PyBasicBinaryRelation, t: &PyBasicBinaryRelation, delta: &PyPartition) -> bool {
        self.inner.centralizes(&s.inner, &t.inner, &delta.inner)
    }
}


