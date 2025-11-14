use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::conlat::{BasicBinaryRelation, BinaryRelation};
use uacalc::alg::conlat::partition::Partition;
use uacalc::util::IntArrayTrait;

/// Python wrapper for CentralityData
///
/// Note: We store the concrete types (BasicBinaryRelation) instead of the trait objects
/// to avoid Send/Sync issues with PyO3.
#[pyclass]
pub struct PyCentralityData {
    left: BasicBinaryRelation,
    right: BasicBinaryRelation,
    delta: Partition,
}

#[pymethods]
impl PyCentralityData {
    /// Create a new CentralityData.
    ///
    /// Args:
    ///     left (BasicBinaryRelation): The left tolerance relation (S)
    ///     right (BasicBinaryRelation): The right tolerance relation (T)
    ///     delta (Partition): The congruence delta
    ///
    /// Returns:
    ///     CentralityData: A new CentralityData instance
    ///
    /// Raises:
    ///     ValueError: If the relations have incompatible universe sizes
    #[new]
    fn new(left: &crate::alg::conlat::basic_binary_relation::PyBasicBinaryRelation, right: &crate::alg::conlat::basic_binary_relation::PyBasicBinaryRelation, delta: &crate::alg::conlat::partition::PyPartition) -> PyResult<Self> {
        // Validate that all relations have the same universe size
        let s_size = left.get_inner().universe_size();
        let t_size = right.get_inner().universe_size();
        let delta_size = delta.get_inner().universe_size();

        if s_size != t_size || s_size != delta_size {
            return Err(PyValueError::new_err(format!(
                "Universe sizes must match: S={}, T={}, delta={}",
                s_size, t_size, delta_size
            )));
        }

        Ok(PyCentralityData {
            left: left.get_inner().clone(),
            right: right.get_inner().clone(),
            delta: delta.get_inner().clone(),
        })
    }

    /// Get the universe size.
    ///
    /// Returns:
    ///     int: The universe size
    fn universe_size(&self) -> usize {
        self.delta.universe_size()
    }

    /// Get the number of blocks in delta.
    ///
    /// Returns:
    ///     int: The number of blocks
    fn delta_blocks(&self) -> usize {
        self.delta.number_of_blocks()
    }

    /// Get the left tolerance relation (S).
    ///
    /// Returns:
    ///     BasicBinaryRelation: The left tolerance relation
    fn left(&self) -> crate::alg::conlat::basic_binary_relation::PyBasicBinaryRelation {
        crate::alg::conlat::basic_binary_relation::PyBasicBinaryRelation::from_inner(self.left.clone())
    }

    /// Get the right tolerance relation (T).
    ///
    /// Returns:
    ///     BasicBinaryRelation: The right tolerance relation
    fn right(&self) -> crate::alg::conlat::basic_binary_relation::PyBasicBinaryRelation {
        crate::alg::conlat::basic_binary_relation::PyBasicBinaryRelation::from_inner(self.right.clone())
    }

    /// Get the delta partition.
    ///
    /// Returns:
    ///     Partition: The delta partition
    fn delta(&self) -> crate::alg::conlat::partition::PyPartition {
        crate::alg::conlat::partition::PyPartition::from_inner(self.delta.clone())
    }

    /// Compare with another CentralityData.
    ///
    /// Args:
    ///     other (CentralityData): The other CentralityData to compare with
    ///
    /// Returns:
    ///     int: -1 if self < other, 0 if equal, 1 if self > other
    fn compare_to(&self, other: &PyCentralityData) -> i32 {
        use std::cmp::Ordering;
        match self.delta.cmp(&other.delta) {
            Ordering::Less => -1,
            Ordering::Equal => 0,
            Ordering::Greater => 1,
        }
    }

    /// Python string representation.
    fn __str__(&self) -> String {
        use uacalc::util::IntArrayTrait;
        let mut result = String::from("left: {");

        let left_pairs = self.left.get_pairs();
        for (i, pair) in left_pairs.iter().enumerate() {
            if i > 0 {
                result.push_str(", ");
            }
            result.push_str(&format!("({}, {})", pair.get(0).unwrap(), pair.get(1).unwrap()));
        }
        result.push_str("}, right: {");

        let right_pairs = self.right.get_pairs();
        for (i, pair) in right_pairs.iter().enumerate() {
            if i > 0 {
                result.push_str(", ");
            }
            result.push_str(&format!("({}, {})", pair.get(0).unwrap(), pair.get(1).unwrap()));
        }
        result.push_str(&format!("}}, delta: {}", self.delta));
        result
    }

    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("CentralityData(universe_size={}, delta_blocks={})",
                self.universe_size(), self.delta_blocks())
    }

    /// Python equality comparison.
    fn __eq__(&self, other: &PyCentralityData) -> bool {
        self.delta == other.delta
    }

    /// Python less than comparison.
    fn __lt__(&self, other: &PyCentralityData) -> bool {
        self.delta < other.delta
    }

    /// Python less than or equal comparison.
    fn __le__(&self, other: &PyCentralityData) -> bool {
        self.delta <= other.delta
    }

    /// Python greater than comparison.
    fn __gt__(&self, other: &PyCentralityData) -> bool {
        self.delta > other.delta
    }

    /// Python greater than or equal comparison.
    fn __ge__(&self, other: &PyCentralityData) -> bool {
        self.delta >= other.delta
    }
}