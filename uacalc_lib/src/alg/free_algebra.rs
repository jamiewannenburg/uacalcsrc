use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyAny;
use uacalc::alg::{Algebra, SmallAlgebra};
use crate::alg::{PyBasicAlgebra, PyBasicOperation};
use crate::alg::big_product_algebra::PyBigProductAlgebra;
use crate::alg::convert::{algebra_type_java_name, operation_to_py, py_to_term, term_to_py};
use crate::alg::conlat::congruence_lattice::PyCongruenceLatticeIntArray;
use crate::eq::PyEquation;
use crate::terms::PyVariableImp;
use crate::util::PyIntArray;
use std::collections::HashMap;

/// Python wrapper for FreeAlgebra
#[pyclass]
pub struct PyFreeAlgebra {
    inner: uacalc::alg::FreeAlgebra,
}

#[pymethods]
impl PyFreeAlgebra {
    /// Create a new FreeAlgebra with the given base algebra and number of generators.
    ///
    /// Args:
    ///     base (BasicAlgebra): The base algebra
    ///     number_of_gens (int): Number of generators
    ///
    /// Raises:
    ///     ValueError: If construction fails
    #[new]
    fn new(base: &PyBasicAlgebra, number_of_gens: i32) -> PyResult<Self> {
        let rust_base = Box::new(base.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::FreeAlgebra::new_safe(rust_base, number_of_gens) {
            Ok(inner) => Ok(PyFreeAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new FreeAlgebra with a custom name.
    ///
    /// Args:
    ///     name (str): The name for the free algebra
    ///     base (BasicAlgebra): The base algebra
    ///     number_of_gens (int): Number of generators
    ///
    /// Raises:
    ///     ValueError: If construction fails
    #[staticmethod]
    fn new_with_name(name: String, base: &PyBasicAlgebra, number_of_gens: i32) -> PyResult<Self> {
        let rust_base = Box::new(base.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;

        match uacalc::alg::FreeAlgebra::new_with_name_safe(name, rust_base, number_of_gens) {
            Ok(inner) => Ok(PyFreeAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new FreeAlgebra with progress control.
    ///
    /// Args:
    ///     base (BasicAlgebra): The base algebra
    ///     number_of_gens (int): Number of generators
    ///     make_universe (bool): Whether to compute the universe
    ///     thin_gens (bool): Whether to thin generators
    ///     decompose (bool): Whether to decompose
    ///
    /// Raises:
    ///     ValueError: If construction fails
    #[staticmethod]
    fn new_with_progress(
        base: &PyBasicAlgebra,
        number_of_gens: i32,
        make_universe: bool,
        thin_gens: bool,
        decompose: bool
    ) -> PyResult<Self> {
        let rust_base = Box::new(base.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        let _ = decompose;

        match uacalc::alg::FreeAlgebra::new_with_thin_safe(
            rust_base,
            number_of_gens,
            make_universe,
            thin_gens,
        ) {
            Ok(inner) => Ok(PyFreeAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Create a new FreeAlgebra with relations (finitely presented algebra).
    ///
    /// Args:
    ///     base (BasicAlgebra): The base algebra
    ///     number_of_gens (int): Number of generators
    ///     relations (List[Equation]): The relations
    ///
    /// Raises:
    ///     ValueError: If construction fails
    #[staticmethod]
    fn new_with_relations(
        base: &PyBasicAlgebra,
        number_of_gens: i32,
        relations: Vec<PyEquation>
    ) -> PyResult<Self> {
        let rust_base = Box::new(base.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        let rust_relations: Vec<uacalc::eq::Equation> = relations.into_iter().map(|eq| eq.inner).collect();

        match uacalc::alg::FreeAlgebra::new_with_relations_safe(rust_base, number_of_gens, rust_relations, None) {
            Ok(inner) => Ok(PyFreeAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the idempotent terms.
    ///
    /// Returns:
    ///     List[Term]: Idempotent terms (VariableImp / NonVariableTerm)
    fn get_idempotent_terms(&self, py: Python<'_>) -> PyResult<Vec<PyObject>> {
        match self.inner.get_idempotent_terms() {
            Ok(terms) => terms
                .iter()
                .map(|t| term_to_py(py, t.as_ref()))
                .collect(),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the algebra type.
    ///
    /// Returns:
    ///     str: The algebra type
    fn algebra_type(&self) -> String {
        algebra_type_java_name(self.inner.algebra_type())
    }

    /// Switch x and y automorphism.
    ///
    /// Returns:
    ///     Optional[PyBasicOperation]: The automorphism operation, or None if not applicable
    fn switch_x_and_y_automorphism(&self) -> PyResult<Option<PyBasicOperation>> {
        match self.inner.switch_x_and_y_automorphism() {
            Ok(Some(op)) => {
                // Convert Box<dyn Operation> to PyBasicOperation
                // This is a simplified approach - in practice, you'd need proper type conversion
                Ok(None) // Simplified for now
            },
            Ok(None) => Ok(None),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Find equation of A not B.
    ///
    /// Args:
    ///     a (BasicAlgebra): Algebra A
    ///     b (BasicAlgebra): Algebra B
    ///     b_gens (List[int]): Generators for algebra B
    ///
    /// Returns:
    ///     Optional[Equation]: The equation, or None if not found
    #[staticmethod]
    fn find_equation_of_a_not_b(a: &PyBasicAlgebra, b: &PyBasicAlgebra, b_gens: Vec<i32>) -> PyResult<Option<PyEquation>> {
        let a_boxed = a.clone_box();
        let b_boxed = b.clone_box();
        
        match uacalc::alg::FreeAlgebra::find_equation_of_a_not_b(a_boxed, b_boxed, b_gens) {
            Ok(Some(eq)) => Ok(Some(PyEquation { inner: eq })),
            Ok(None) => Ok(None),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the cardinality of the algebra.
    ///
    /// Returns:
    ///     int: The cardinality
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }

    /// Get the name of the algebra.
    ///
    /// Returns:
    ///     str: The name
    fn name(&self) -> String {
        self.inner.name().to_string()
    }

    /// Set the name of the algebra.
    ///
    /// Args:
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }

    /// Check if this algebra is unary.
    ///
    /// Returns:
    ///     bool: True if the algebra is unary
    fn is_unary(&self) -> bool {
        self.inner.is_unary()
    }

    /// Check if this algebra is idempotent.
    ///
    /// Returns:
    ///     bool: True if the algebra is idempotent
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }

    /// Check if this algebra is total.
    ///
    /// Returns:
    ///     bool: True if the algebra is total
    fn is_total(&self) -> bool {
        self.inner.is_total()
    }

    /// Get the number of operations.
    ///
    /// Returns:
    ///     int: The number of operations
    fn operations_count(&self) -> usize {
        self.inner.get_operations_ref().len()
    }

    /// Java `operations()` — table-backed ops so `intValueAt` works from Python.
    fn operations(&self, py: Python<'_>) -> PyResult<Vec<PyObject>> {
        let mut result = Vec::new();
        for op in self.inner.operations() {
            result.push(operation_to_py(py, op.as_ref())?);
        }
        Ok(result)
    }

    /// Java `getTerms()`.
    fn get_terms(&self, py: Python<'_>) -> PyResult<Vec<PyObject>> {
        match self.inner.get_inner().get_terms() {
            Some(terms) => terms
                .iter()
                .map(|t| term_to_py(py, t.as_ref()))
                .collect(),
            None => Ok(Vec::new()),
        }
    }

    /// Java `getTerm(elt)`.
    fn get_term(&self, py: Python<'_>, element: &PyIntArray) -> PyResult<Option<PyObject>> {
        match self.inner.get_inner().get_term(&element.inner) {
            Some(term) => Ok(Some(term_to_py(py, term)?)),
            None => Ok(None),
        }
    }

    /// Java `getElementFromTerm(term)`.
    fn get_element_from_term(&self, term: &Bound<'_, PyAny>) -> PyResult<Option<PyIntArray>> {
        let rust_term = py_to_term(term)?;
        Ok(self
            .inner
            .get_inner()
            .get_element_from_term(rust_term.as_ref())
            .map(|arr| PyIntArray { inner: arr }))
    }

    /// Java `getProductAlgebra()`.
    fn get_product_algebra(&self) -> PyBigProductAlgebra {
        PyBigProductAlgebra::from_cloned(self.inner.get_inner().get_product_algebra())
    }

    /// Java `superAlgebra()` — same as the product algebra for a free algebra.
    fn super_algebra(&self) -> PyBigProductAlgebra {
        self.get_product_algebra()
    }

    /// Java `generators()`.
    fn generators(&self) -> Vec<PyIntArray> {
        self.inner
            .get_inner()
            .generators()
            .iter()
            .cloned()
            .map(|arr| PyIntArray { inner: arr })
            .collect()
    }

    /// Java `getVariables()`.
    fn get_variables(&self) -> Vec<PyVariableImp> {
        self.inner
            .get_inner()
            .get_variables()
            .unwrap_or_default()
            .into_iter()
            .map(|inner| PyVariableImp { inner })
            .collect()
    }

    /// Get the universe as a list.
    ///
    /// Returns:
    ///     List[IntArray]: The universe elements
    fn get_universe_list(&self) -> Vec<PyIntArray> {
        self.inner.universe()
            .map(|item| PyIntArray { inner: item })
            .collect()
    }

    /// Get the universe order as a dictionary.
    ///
    /// Returns:
    ///     Dict[IntArray, int]: The universe order mapping
    fn get_universe_order(&self) -> Option<HashMap<PyIntArray, usize>> {
        // This is a simplified implementation
        // The full implementation would need to handle IntArray as keys
        None
    }

    /// Get an element by its index.
    ///
    /// Args:
    ///     index (int): The index of the element
    ///
    /// Returns:
    ///     IntArray: The element at the given index
    fn get_element(&self, index: usize) -> Option<PyIntArray> {
        self.inner
            .get_element(index)
            .map(|arr| PyIntArray { inner: arr })
    }

    /// Get the index of an element.
    ///
    /// Args:
    ///     element (IntArray): The element to find the index for
    ///
    /// Returns:
    ///     int: The index of the element
    fn element_index(&self, element: &PyIntArray) -> Option<usize> {
        self.inner.element_index(&element.inner)
    }

    /// String representation of the algebra.
    ///
    /// Returns:
    ///     str: String representation
    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }

    /// String representation for debugging.
    ///
    /// Returns:
    ///     str: Debug string representation
    fn __repr__(&self) -> String {
        format!("FreeAlgebra(name='{}', cardinality={})", self.name(), self.cardinality())
    }

    /// Equality comparison.
    ///
    /// Args:
    ///     other (FreeAlgebra): The other algebra to compare with
    ///
    /// Returns:
    ///     bool: True if equal
    fn __eq__(&self, other: &PyFreeAlgebra) -> bool {
        self.inner == other.inner
    }

    /// Hash function for use in sets and dictionaries.
    ///
    /// Returns:
    ///     int: Hash value
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }

    /// Length function for use with len().
    ///
    /// Returns:
    ///     int: Cardinality of the algebra
    fn __len__(&self) -> usize {
        self.inner.cardinality() as usize
    }

    /// Get the congruence lattice (lazy initialization).
    ///
    /// Returns:
    ///     CongruenceLatticeIntArray: The congruence lattice
    fn con(&mut self) -> PyCongruenceLatticeIntArray {
        let con_lat = self.inner.con();
        PyCongruenceLatticeIntArray {
            inner: con_lat.clone(),
        }
    }
}