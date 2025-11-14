use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::util::IntArrayTrait;
use uacalc::alg::conlat::{BinaryRelation, MutableBinaryRelation};
use crate::alg::conlat::basic_binary_relation::PyBasicBinaryRelation;

/// Python wrapper for Partition
#[pyclass]
pub struct PyPartition {
    pub(crate) inner: uacalc::alg::conlat::partition::Partition,
}

#[pymethods]
impl PyPartition {
    /// Create a new Partition from an array representation.
    /// 
    /// Args:
    ///     array (List[int]): The array representation of the partition
    /// 
    /// Returns:
    ///     Partition: A new Partition instance
    /// 
    /// Raises:
    ///     ValueError: If the array is invalid
    #[new]
    fn new(array: Vec<i32>) -> PyResult<Self> {
        match uacalc::alg::conlat::partition::Partition::new(array) {
            Ok(inner) => Ok(PyPartition { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new Partition from a string representation.
    /// 
    /// Args:
    ///     str (str): String representation of the partition
    /// 
    /// Returns:
    ///     Partition: A new Partition instance
    /// 
    /// Raises:
    ///     ValueError: If the string format is invalid
    #[staticmethod]
    fn from_string(str: &str) -> PyResult<Self> {
        match uacalc::alg::conlat::partition::Partition::from_string(str) {
            Ok(inner) => Ok(PyPartition { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new Partition from a string representation with specified length.
    /// 
    /// Args:
    ///     str (str): String representation of the partition
    ///     length (int): Maximum universe size (-1 for auto-detect)
    /// 
    /// Returns:
    ///     Partition: A new Partition instance
    /// 
    /// Raises:
    ///     ValueError: If the string format is invalid
    #[staticmethod]
    fn from_string_with_length(str: &str, length: i32) -> PyResult<Self> {
        match uacalc::alg::conlat::partition::Partition::from_string_with_length(str, length) {
            Ok(inner) => Ok(PyPartition { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create the zero partition (all elements in separate blocks).
    /// 
    /// Args:
    ///     size (int): Size of the universe
    /// 
    /// Returns:
    ///     Partition: Zero partition
    #[staticmethod]
    fn zero(size: usize) -> Self {
        PyPartition {
            inner: uacalc::alg::conlat::partition::Partition::zero(size),
        }
    }
    
    /// Create the one partition (all elements in one block).
    /// 
    /// Args:
    ///     size (int): Size of the universe
    /// 
    /// Returns:
    ///     Partition: One partition
    #[staticmethod]
    fn one(size: usize) -> Self {
        PyPartition {
            inner: uacalc::alg::conlat::partition::Partition::one(size),
        }
    }
    
    /// Get the universe size (number of elements).
    /// 
    /// Returns:
    ///     int: The universe size
    fn universe_size(&self) -> usize {
        self.inner.universe_size()
    }
    
    /// Get the number of blocks in the partition.
    /// 
    /// Returns:
    ///     int: The number of blocks
    fn number_of_blocks(&self) -> usize {
        self.inner.number_of_blocks()
    }

    /// Check if two elements are related (in the same block).
    /// 
    /// Args:
    ///     i (int): First element
    ///     j (int): Second element
    /// 
    /// Returns:
    ///     bool: True if elements are in the same block
    fn is_related(&self, i: usize, j: usize) -> bool {
        self.inner.is_related(i, j)
    }

    /// Get the representative (root) of the block containing element i.
    /// 
    /// Args:
    ///     i (int): Element index
    /// 
    /// Returns:
    ///     int: Representative element index
    fn representative(&self, i: usize) -> usize {
        self.inner.representative(i)
    }

    /// Check if an element is a representative (root) of its block.
    /// 
    /// Args:
    ///     i (int): Element index
    /// 
    /// Returns:
    ///     bool: True if element is representative
    fn is_representative(&self, i: usize) -> bool {
        self.inner.is_representative(i)
    }

    /// Get all representatives of the partition.
    /// 
    /// Returns:
    ///     List[int]: List of representative indices
    fn representatives(&self) -> Vec<usize> {
        self.inner.representatives()
    }

    /// Get the index of the block containing element i.
    /// 
    /// Args:
    ///     i (int): Element index
    /// 
    /// Returns:
    ///     int: Block index
    /// 
    /// Raises:
    ///     ValueError: If element not found in representatives
    fn block_index(&self, i: usize) -> PyResult<usize> {
        match self.inner.block_index(i) {
            Ok(idx) => Ok(idx),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    /// Get the blocks of the partition as an array of arrays.
    /// 
    /// Returns:
    ///     List[List[int]]: List of blocks, where each block is a list of element indices
    fn get_blocks(&self) -> Vec<Vec<usize>> {
        self.inner.get_blocks()
    }

    /// Join two blocks by their representatives.
    /// 
    /// Args:
    ///     r (int): Representative of first block
    ///     s (int): Representative of second block
    /// 
    /// Raises:
    ///     ValueError: If r or s are not representatives or if r == s
    fn join_blocks(&mut self, r: usize, s: usize) -> PyResult<()> {
        if r == s {
            return Err(PyValueError::new_err("Cannot join a block with itself"));
        }
        if !self.inner.is_representative(r) || !self.inner.is_representative(s) {
            return Err(PyValueError::new_err("Both arguments must be representatives"));
        }
        self.inner.join_blocks(r, s);
        Ok(())
    }

    /// Normalize the partition representation.
    fn normalize(&mut self) {
        self.inner.normalize();
    }

    /// Check if this is the zero partition (all elements in separate blocks).
    /// 
    /// Returns:
    ///     bool: True if this is the zero partition
    fn is_zero(&self) -> bool {
        self.inner.is_zero()
    }

    /// Check if this partition is uniform (all blocks have the same size).
    /// 
    /// Returns:
    ///     bool: True if all blocks have the same size
    fn is_uniform(&self) -> bool {
        self.inner.is_uniform()
    }

    /// Check if this partition is in initial lexicographic representative form.
    /// 
    /// Returns:
    ///     bool: True if in initial lexicographic representative form
    fn is_initial_lex_representative(&self) -> bool {
        self.inner.is_initial_lex_representative()
    }

    /// Get the rank of the partition (universe size - number of blocks).
    /// 
    /// Returns:
    ///     int: The rank
    fn rank(&self) -> usize {
        self.inner.rank()
    }

    /// Get the array representation of the partition.
    /// 
    /// Returns:
    ///     List[int]: Array representation
    fn to_array(&self) -> Vec<i32> {
        self.inner.to_array()
    }
    
    /// Get the string representation of the partition.
    /// 
    /// Returns:
    ///     str: String representation
    fn to_string(&self) -> String {
        self.inner.to_string()
    }
    
    /// Check if this partition is less than or equal to another.
    /// 
    /// Args:
    ///     other (Partition): The other partition
    /// 
    /// Returns:
    ///     bool: True if this partition is less than or equal to the other
    fn le(&self, other: &PyPartition) -> bool {
        self.inner.le(&other.inner)
    }
    
    /// Get the meet of this partition with another.
    /// 
    /// Args:
    ///     other (Partition): The other partition
    /// 
    /// Returns:
    ///     Partition: The meet partition
    fn meet(&self, other: &PyPartition) -> PyResult<PyPartition> {
        match self.inner.meet(&other.inner) {
            Ok(inner) => Ok(PyPartition { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the join of this partition with another.
    /// 
    /// Args:
    ///     other (Partition): The other partition
    /// 
    /// Returns:
    ///     Partition: The join partition
    fn join(&self, other: &PyPartition) -> PyResult<PyPartition> {
        match self.inner.join(&other.inner) {
            Ok(inner) => Ok(PyPartition { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Python string representation.
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("Partition({})", self.inner.to_string())
    }
    
    /// Python equality comparison.
    fn __eq__(&self, other: &PyPartition) -> bool {
        self.inner == other.inner
    }
    
    /// Python hash function.
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }

    /// Convert this partition to a BasicBinaryRelation.
    fn to_binary_relation(&self) -> PyResult<PyBasicBinaryRelation> {
        // Build a relation containing all pairs from the equivalence relation
        let size = self.inner.universe_size();
        let mut rel = uacalc::alg::conlat::basic_binary_relation::BasicBinaryRelation::new(size)
            .map_err(|e| PyValueError::new_err(e))?;
        let pairs = self.inner.get_pairs();
        for pair in pairs {
            let i = pair.get(0).unwrap_or(0) as usize;
            let j = pair.get(1).unwrap_or(0) as usize;
            rel.add(i, j).map_err(|e| PyValueError::new_err(e))?;
        }
        Ok(PyBasicBinaryRelation { inner: rel })
    }

    /// leq alias for 'le' method.
    fn leq(&self, other: &PyPartition) -> bool {
        self.le(other)
    }

    /// Convert to string with specified print type and maximum length.
    /// Args:
    ///   print_type (PyPrintType): The print type struct
    ///   max_len (int, optional): The max length, or -1
    /// Returns:
    ///   str: String rep
    fn to_string_with_type(&self, print_type: &crate::alg::conlat::print_type::PyPrintType, max_len: Option<i32>) -> String {
        self.inner.to_string_with_type(print_type.inner, max_len.unwrap_or(-1))
    }

    /// Convert to string with maximum length.
    fn to_string_with_max_len(&self, max_len: i32) -> String {
        self.inner.to_string_with_max_len(max_len)
    }

    // Python comparison (less than).
    fn __lt__(&self, other: &PyPartition) -> bool {
        self.inner < other.inner
    }
    // Python comparison (less than or equal).
    fn __le__(&self, other: &PyPartition) -> bool {
        self.inner <= other.inner
    }
    // Python comparison (greater than).
    fn __gt__(&self, other: &PyPartition) -> bool {
        self.inner > other.inner
    }
    // Python comparison (greater than or equal).
    fn __ge__(&self, other: &PyPartition) -> bool {
        self.inner >= other.inner
    }
}

impl PyPartition {
    /// Get the inner Partition (for internal use)
    pub(crate) fn get_inner(&self) -> &uacalc::alg::conlat::partition::Partition {
        &self.inner
    }
    pub(crate) fn from_inner(inner: uacalc::alg::conlat::partition::Partition) -> Self { PyPartition { inner } }
}
