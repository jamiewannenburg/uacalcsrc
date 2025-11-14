use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::{SmallAlgebra, Algebra};
use uacalc::alg::op::Operation;
use crate::alg::PyBasicAlgebra;
use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;
use crate::alg::PySubalgebraLattice;
use crate::alg::op::operation::PyBasicOperation;

/// Python wrapper for PolinLikeAlgebra
#[pyclass]
pub struct PyPolinLikeAlgebra {
    inner: std::cell::RefCell<uacalc::alg::PolinLikeAlgebra<i32>>,
}

#[pymethods]
impl PyPolinLikeAlgebra {
    /// Create a new PolinLikeAlgebra from two algebras and an optional homomorphism map.
    ///
    /// Args:
    ///     name (str): Name of the algebra
    ///     top_alg (BasicAlgebra): The top algebra (A in f: A → B)
    ///     bot_alg (BasicAlgebra): The bottom algebra (B in f: A → B)
    ///     map (Operation, optional): Optional homomorphism map from topAlg to botAlg (None = identity)
    ///     top_const_index (int): Index of the top constant
    ///     bot_const_index (int): Index of the bottom constant
    ///
    /// Raises:
    ///     ValueError: If construction fails
    #[new]
    #[pyo3(signature = (name, top_alg, bot_alg, map=None, top_const_index=0, bot_const_index=0))]
    fn new(
        name: String,
        top_alg: &PyBasicAlgebra,
        bot_alg: &PyBasicAlgebra,
        map: Option<&PyBasicOperation>,
        top_const_index: usize,
        bot_const_index: usize,
    ) -> PyResult<Self> {
        let top_box = Box::new(top_alg.inner.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        let bot_box = Box::new(bot_alg.inner.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let map_box = map.map(|m| {
            // Convert PyBasicOperation to Box<dyn Operation>
            // Access inner field directly (pub(crate) allows this within crate)
            let inner_op = m.inner.clone();
            Box::new(inner_op) as Box<dyn Operation>
        });
        
        match uacalc::alg::PolinLikeAlgebra::new_safe(name, top_box, bot_box, map_box, top_const_index, bot_const_index) {
            Ok(inner) => Ok(PyPolinLikeAlgebra {
                inner: std::cell::RefCell::new(inner),
            }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the cardinality of this algebra.
    ///
    /// Returns:
    ///     int: The cardinality (size of the universe)
    fn cardinality(&self) -> i32 {
        self.inner.borrow().cardinality()
    }

    /// Get the element at the given index.
    ///
    /// Args:
    ///     k (int): Index of the element
    ///
    /// Returns:
    ///     int: The element at index k, or -1 if out of bounds
    fn get_element(&self, k: usize) -> i32 {
        self.inner.borrow().get_element(k).unwrap_or(-1)
    }

    /// Get the index of an element in the universe.
    ///
    /// Args:
    ///     elem (int): The element to find
    ///
    /// Returns:
    ///     int: The index of the element, or -1 if not found
    fn element_index(&self, elem: i32) -> i32 {
        match self.inner.borrow().element_index(&elem) {
            Some(idx) => idx as i32,
            None => -1,
        }
    }

    /// Get the algebra type.
    ///
    /// Returns:
    ///     str: The algebra type ("PolinLike")
    fn algebra_type(&self) -> String {
        format!("{:?}", self.inner.borrow().algebra_type())
    }

    /// Get the name of this algebra.
    ///
    /// Returns:
    ///     str: The name of the algebra
    fn name(&self) -> String {
        self.inner.borrow().name().to_string()
    }

    /// Set the name of this algebra.
    ///
    /// Args:
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.borrow_mut().set_name(name);
    }

    /// Get the top algebra name.
    ///
    /// Returns:
    ///     str: Name of the top algebra
    fn top_algebra_name(&self) -> String {
        self.inner.borrow().top_algebra().name().to_string()
    }

    /// Get the bottom algebra name.
    ///
    /// Returns:
    ///     str: Name of the bottom algebra
    fn bottom_algebra_name(&self) -> String {
        self.inner.borrow().bottom_algebra().name().to_string()
    }

    /// Get the congruence lattice (lazy initialization).
    ///
    /// Returns:
    ///     CongruenceLattice: The congruence lattice
    fn con(&mut self) -> PyCongruenceLattice {
        let con_lat = self.inner.borrow_mut().con().clone();
        PyCongruenceLattice { inner: con_lat }
    }

    /// Get the subalgebra lattice (lazy initialization).
    ///
    /// Returns:
    ///     SubalgebraLattice: The subalgebra lattice
    fn sub(&mut self) -> PySubalgebraLattice {
        let sub_lat = self.inner.borrow_mut().sub().clone();
        PySubalgebraLattice::from_inner(sub_lat)
    }

    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.borrow().to_string()
    }

    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("PolinLikeAlgebra({})", self.inner.borrow().name())
    }
}

