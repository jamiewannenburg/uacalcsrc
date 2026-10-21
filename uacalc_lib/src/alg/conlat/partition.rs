use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyAny;
use uacalc::util::IntArrayTrait;
use uacalc::alg::conlat::{BinaryRelation, MutableBinaryRelation};
use uacalc::alg::conlat::partition::Partition;
use crate::alg::conlat::basic_binary_relation::PyBasicBinaryRelation;
use crate::util::PyIntArray;

fn extract_partition(obj: &Bound<'_, PyAny>) -> PyResult<Partition> {
    if let Ok(p) = obj.extract::<PyRef<PyPartition>>() {
        return Ok(p.inner.clone());
    }
    Err(PyValueError::new_err("expected Partition"))
}

fn extract_partition_list(obj: &Bound<'_, PyAny>) -> PyResult<Vec<Partition>> {
    let mut out = Vec::new();
    for item in obj.iter()? {
        out.push(extract_partition(&item?)?);
    }
    Ok(out)
}

fn wrap(inner: Partition) -> PyPartition {
    PyPartition { inner }
}

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

    /// Java ``Partition.leq``: refinement order, not ``compareTo`` / PartialOrd.
    fn leq(&self, other: &PyPartition) -> bool {
        self.inner.leq(&other.inner)
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

    fn get_array(&self) -> Vec<i32> {
        self.inner.to_array()
    }

    fn get_pairs(&self) -> Vec<Vec<i32>> {
        self.inner
            .pairs_as_vec()
            .into_iter()
            .map(|p| vec![p[0], p[1]])
            .collect()
    }

    fn compose(&self, other: &Bound<'_, PyAny>) -> PyResult<PyBasicBinaryRelation> {
        let rel = if let Ok(p) = other.extract::<PyRef<PyPartition>>() {
            self.inner.compose_bbr(&p.inner)
        } else if let Ok(r) = other.extract::<PyRef<PyBasicBinaryRelation>>() {
            self.inner.compose_bbr(&r.inner)
        } else {
            return Err(PyValueError::new_err("compose expects a BinaryRelation"));
        };
        match rel {
            Ok(inner) => Ok(PyBasicBinaryRelation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    fn compare_to(&self, other: &PyPartition) -> i32 {
        // Java BasicPartition.compareTo: -1/1 on block-count, else raw array diff.
        let diff = other.inner.number_of_blocks() as i32 - self.inner.number_of_blocks() as i32;
        if diff < 0 {
            return -1;
        }
        if diff > 0 {
            return 1;
        }
        let a = self.inner.to_array();
        let b = other.inner.to_array();
        let n = a.len().min(b.len());
        for i in 0..n {
            let d = b[i] - a[i];
            if d != 0 {
                return d;
            }
        }
        0
    }

    fn get(&self, i: usize) -> PyResult<i32> {
        let arr = self.inner.to_array();
        arr.get(i).copied().ok_or_else(|| {
            pyo3::exceptions::PyIndexError::new_err(format!(
                "Index {} out of bounds for length {}",
                i,
                arr.len()
            ))
        })
    }

    fn hash_code(&self) -> i32 {
        Partition::java_hash_code(&self.inner.to_array())
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<PyPartitionPairsIter>> {
        let pairs = slf.get_pairs();
        Py::new(
            slf.py(),
            PyPartitionPairsIter { pairs, index: 0 },
        )
    }

    #[staticmethod]
    fn string_to_partition(str: &str, length: i32) -> PyResult<Option<Vec<i32>>> {
        match Partition::string_to_partition(str, length) {
            Ok(v) => Ok(v),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn jb_to_partition(a: Vec<i32>) -> PyResult<PyPartition> {
        match Partition::jb_to_partition(&a) {
            Ok(inner) => Ok(wrap(inner)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    #[pyo3(signature = (a_or_par0, b_or_par1, par0=None, par1=None))]
    fn permutability_level(
        a_or_par0: &Bound<'_, PyAny>,
        b_or_par1: &Bound<'_, PyAny>,
        par0: Option<&PyPartition>,
        par1: Option<&PyPartition>,
    ) -> PyResult<i32> {
        if let (Some(p0), Some(p1)) = (par0, par1) {
            let a = a_or_par0.extract::<usize>()?;
            let b = b_or_par1.extract::<usize>()?;
            return Ok(Partition::permutability_level(a, b, &p0.inner, &p1.inner));
        }
        let p0 = extract_partition(a_or_par0)?;
        let p1 = extract_partition(b_or_par1)?;
        match Partition::permutability_level_of_join(&p0, &p1) {
            Ok(v) => Ok(v),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn leq_arrays(u: Vec<i32>, v: Vec<i32>) -> bool {
        Partition::leq_arrays(&u, &v)
    }

    #[staticmethod]
    fn normalize_array(mut part: Vec<i32>) -> PyResult<Vec<i32>> {
        match Partition::normalize_array_java(&mut part) {
            Ok(()) => Ok(part),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn part_to_kiss_string(part: Vec<i32>) -> String {
        Partition::part_to_kiss_string_public(&part)
    }

    #[staticmethod]
    fn direct_product(alpha: &Bound<'_, PyAny>, beta: &Bound<'_, PyAny>) -> PyResult<PyPartition> {
        let a = extract_partition(alpha)?;
        let b = extract_partition(beta)?;
        match Partition::direct_product(&a, &b) {
            Ok(inner) => Ok(wrap(inner)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn unary_polymorphisms(pars: &Bound<'_, PyAny>) -> PyResult<Vec<PyIntArray>> {
        let rust = extract_partition_list(pars)?;
        match Partition::unary_polymorphisms(&rust) {
            Ok(set) => Ok(set.into_iter().map(|ia| PyIntArray { inner: ia }).collect()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn binary_polymorphisms(pars: &Bound<'_, PyAny>) -> PyResult<Vec<PyIntArray>> {
        let rust = extract_partition_list(pars)?;
        match Partition::binary_polymorphisms(&rust, None) {
            Ok(set) => Ok(set.into_iter().map(|ia| PyIntArray { inner: ia }).collect()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn join_closure(pars: &Bound<'_, PyAny>) -> PyResult<Vec<PyPartition>> {
        let rust = extract_partition_list(pars)?;
        match Partition::join_closure(&rust) {
            Ok(v) => Ok(v.into_iter().map(wrap).collect()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn meet_closure(pars: &Bound<'_, PyAny>) -> PyResult<Vec<PyPartition>> {
        let rust = extract_partition_list(pars)?;
        match Partition::meet_closure(&rust) {
            Ok(v) => Ok(v.into_iter().map(wrap).collect()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn sub_universe_generated(gens: &Bound<'_, PyAny>) -> PyResult<Vec<PyPartition>> {
        let rust = extract_partition_list(gens)?;
        match Partition::sub_universe_generated(&rust) {
            Ok(v) => Ok(v.into_iter().map(wrap).collect()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn partition_from_matrix(matrix: Vec<Vec<i32>>) -> PyResult<PyPartition> {
        match Partition::partition_from_matrix(&matrix) {
            Ok(inner) => Ok(wrap(inner)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn first_projection(n: usize) -> PyResult<PyPartition> {
        match Partition::first_projection(n) {
            Ok(inner) => Ok(wrap(inner)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn second_projection(n: usize) -> PyResult<PyPartition> {
        match Partition::second_projection(n) {
            Ok(inner) => Ok(wrap(inner)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
}

#[pyclass]
pub struct PyPartitionPairsIter {
    pairs: Vec<Vec<i32>>,
    index: usize,
}

#[pymethods]
impl PyPartitionPairsIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(&mut self) -> Option<PyIntArray> {
        if self.index >= self.pairs.len() {
            return None;
        }
        let pair = &self.pairs[self.index];
        self.index += 1;
        match uacalc::util::int_array::IntArray::from_array(pair.clone()) {
            Ok(inner) => Some(PyIntArray { inner }),
            Err(_) => None,
        }
    }
}

impl PyPartition {
    /// Get the inner Partition (for internal use)
    pub(crate) fn get_inner(&self) -> &uacalc::alg::conlat::partition::Partition {
        &self.inner
    }
    pub(crate) fn from_inner(inner: uacalc::alg::conlat::partition::Partition) -> Self { PyPartition { inner } }
}
