use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;

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
        let mut con_lat = uacalc::alg::conlat::CongruenceLattice::new(
            Box::new(SmallAlgebraWrapper::new(Box::new(algebra.inner.clone())))
        );
        // Ensure principals are computed when the lattice is created
        // This ensures the lattice is "built" and ready to use
        con_lat.make_principals();
        PyCongruenceLattice {
            inner: con_lat,
        }
    }
}

#[pymethods]
impl PyCongruenceLattice {
    /// Create a new congruence lattice for an algebra.
    #[new]
    fn new(algebra: &PyBasicAlgebra) -> Self {
        use uacalc::alg::SmallAlgebraWrapper;
        let mut con_lat = uacalc::alg::conlat::CongruenceLattice::new(
            Box::new(SmallAlgebraWrapper::new(Box::new(algebra.inner.clone())))
        );
        // Ensure principals are computed when the lattice is created
        // This ensures the lattice is "built" and ready to use
        con_lat.make_principals();
        PyCongruenceLattice {
            inner: con_lat,
        }
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


