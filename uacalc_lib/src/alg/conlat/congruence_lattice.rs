use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;

use crate::alg::basic_algebra::PyBasicSmallAlgebra;
use crate::alg::conlat::partition::PyPartition;
use crate::alg::conlat::basic_binary_relation::PyBasicBinaryRelation;
use crate::util::PyIntArray;

/// Python wrapper for CongruenceLattice
#[pyclass]
pub struct PyCongruenceLattice {
    pub(crate) inner: uacalc::alg::conlat::CongruenceLattice<i32>,
}

#[pymethods]
impl PyCongruenceLattice {
    /// Create a new congruence lattice for an algebra.
    #[new]
    fn new(algebra: &PyBasicSmallAlgebra) -> Self {
        use uacalc::alg::SmallAlgebraWrapper;
        PyCongruenceLattice {
            inner: uacalc::alg::conlat::CongruenceLattice::new(
                Box::new(SmallAlgebraWrapper::new(Box::new(algebra.inner.clone())))
            ),
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
}


