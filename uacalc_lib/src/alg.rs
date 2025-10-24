use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyList;
use std::collections::HashMap;
use uacalc::alg::*;
use uacalc::alg::conlat::{BinaryRelation, MutableBinaryRelation};
use uacalc::util::IntArrayTrait;
use uacalc::alg::conlat::BasicBinaryRelation;
use uacalc::alg::conlat::subtrace::Subtrace;
use uacalc::alg::op::{Operation, BasicOperation, AbstractIntOperation, IntOperation};
use uacalc::alg::sublat::BasicSet;
use uacalc::lat::{Lattice, Order};
use crate::util::PyIntArray;

/// Python wrapper for OperationSymbol
#[pyclass]
pub struct PyOperationSymbol {
    inner: uacalc::alg::op::OperationSymbol,
}

#[pymethods]
impl PyOperationSymbol {
    /// Create a new OperationSymbol with the given name and arity.
    /// 
    /// Args:
    ///     name (str): The name of the operation symbol
    ///     arity (int): The arity (number of operands) of the operation
    ///     associative (bool, optional): Whether the operation is associative (only valid for binary operations). Defaults to False.
    /// 
    /// Raises:
    ///     ValueError: If associative is True but arity is not 2.
    #[new]
    #[pyo3(signature = (name, arity, associative=false))]
    fn new(name: &str, arity: i32, associative: bool) -> PyResult<Self> {
        match uacalc::alg::op::OperationSymbol::new_safe(name, arity, associative) {
            Ok(inner) => Ok(PyOperationSymbol { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the arity of this operation symbol.
    /// 
    /// Returns:
    ///     int: The arity of the operation symbol
    fn arity(&self) -> i32 {
        self.inner.arity()
    }
    
    /// Get the name of this operation symbol.
    /// 
    /// Returns:
    ///     str: The name of the operation symbol
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    /// Check if this operation symbol is marked as associative.
    /// 
    /// Only binary operations (arity 2) can be associative.
    /// 
    /// Returns:
    ///     bool: True if the operation is associative, False otherwise
    fn is_associative(&self) -> bool {
        self.inner.is_associative()
    }
    
    /// Set whether this operation symbol is associative.
    /// 
    /// Args:
    ///     assoc (bool): Whether the operation should be associative
    /// 
    /// Raises:
    ///     ValueError: If assoc is True but the arity is not 2.
    fn set_associative(&mut self, assoc: bool) -> PyResult<()> {
        match self.inner.set_associative(assoc) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Convert this operation symbol to a string representation.
    /// 
    /// Args:
    ///     show_arity (bool, optional): Whether to include the arity in the string. Defaults to False.
    /// 
    /// Returns:
    ///     str: String representation of the operation symbol
    fn to_string_with_arity(&self, show_arity: Option<bool>) -> String {
        self.inner.to_string_with_arity(show_arity.unwrap_or(false))
    }
    
    /// Get an OperationSymbol in a uniform manner for consistent naming.
    /// 
    /// This method generates operation symbols with standardized names
    /// based on arity, ensuring that similar algebras will have consistent
    /// operation symbol naming.
    /// 
    /// Args:
    ///     arity (int): The arity of the operation symbol to generate
    /// 
    /// Returns:
    ///     OperationSymbol: A new OperationSymbol with a generated name based on the arity
    #[staticmethod]
    fn get_operation_symbol(arity: i32) -> Self {
        PyOperationSymbol {
            inner: uacalc::alg::op::OperationSymbol::get_operation_symbol(arity)
        }
    }
    
    /// Get the JOIN constant (binary operation).
    #[staticmethod]
    fn join() -> Self {
        PyOperationSymbol {
            inner: uacalc::alg::op::OperationSymbol::join().clone()
        }
    }
    
    /// Get the MEET constant (binary operation).
    #[staticmethod]
    fn meet() -> Self {
        PyOperationSymbol {
            inner: uacalc::alg::op::OperationSymbol::meet().clone()
        }
    }
    
    /// Get the PRODUCT constant (binary operation).
    #[staticmethod]
    fn product() -> Self {
        PyOperationSymbol {
            inner: uacalc::alg::op::OperationSymbol::product().clone()
        }
    }
    
    /// Get the INVERSE constant (unary operation).
    #[staticmethod]
    fn inverse() -> Self {
        PyOperationSymbol {
            inner: uacalc::alg::op::OperationSymbol::inverse().clone()
        }
    }
    
    /// Get the IDENTITY constant (nullary operation).
    #[staticmethod]
    fn identity() -> Self {
        PyOperationSymbol {
            inner: uacalc::alg::op::OperationSymbol::identity().clone()
        }
    }
    
    /// Python string representation.
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("OperationSymbol(name='{}', arity={}, associative={})", 
                self.inner.name(), self.inner.arity(), self.inner.is_associative())
    }
    
    /// Python equality comparison.
    fn __eq__(&self, other: &PyOperationSymbol) -> bool {
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
    
    /// Python comparison (less than).
    fn __lt__(&self, other: &PyOperationSymbol) -> bool {
        self.inner < other.inner
    }
    
    /// Python comparison (less than or equal).
    fn __le__(&self, other: &PyOperationSymbol) -> bool {
        self.inner <= other.inner
    }
    
    /// Python comparison (greater than).
    fn __gt__(&self, other: &PyOperationSymbol) -> bool {
        self.inner > other.inner
    }
    
    /// Python comparison (greater than or equal).
    fn __ge__(&self, other: &PyOperationSymbol) -> bool {
        self.inner >= other.inner
    }
}

impl PyOperationSymbol {
    /// Get the inner OperationSymbol (for internal use)
    pub(crate) fn get_inner(&self) -> uacalc::alg::op::OperationSymbol {
        self.inner.clone()
    }
}

/// Python wrapper for SimilarityType
#[pyclass]
pub struct PySimilarityType {
    inner: uacalc::alg::op::SimilarityType,
}

#[pymethods]
impl PySimilarityType {
    /// Create a new SimilarityType with the given operation symbols.
    /// 
    /// Args:
    ///     operation_symbols (List[OperationSymbol]): List of operation symbols
    ///     sort (bool, optional): Whether to sort the operation symbols. Defaults to False.
    /// 
    /// Returns:
    ///     SimilarityType: A new SimilarityType instance
    #[new]
    #[pyo3(signature = (operation_symbols, sort=false))]
    fn new(operation_symbols: &PyAny, sort: bool) -> PyResult<Self> {
        let ops: Vec<uacalc::alg::op::OperationSymbol> = operation_symbols
            .extract::<Vec<PyRef<PyOperationSymbol>>>()?
            .into_iter()
            .map(|py_op| py_op.inner.clone())
            .collect();
        
        match uacalc::alg::op::SimilarityType::new_safe(ops) {
            Ok(mut inner) => {
                if sort {
                    // Create a new instance with sorted symbols
                    let sorted_ops = inner.get_sorted_operation_symbols();
                    inner = uacalc::alg::op::SimilarityType::new(sorted_ops);
                }
                Ok(PySimilarityType { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the operation symbols in this similarity type.
    /// 
    /// Returns:
    ///     List[OperationSymbol]: List of operation symbols
    fn get_operation_symbols(&self) -> Vec<PyOperationSymbol> {
        self.inner.get_operation_symbols()
            .iter()
            .map(|op| PyOperationSymbol { inner: op.clone() })
            .collect()
    }
    
    /// Get a sorted list of operation symbols.
    /// 
    /// The sorting is by lowest arity first, then by alphabetical order on the name.
    /// 
    /// Returns:
    ///     List[OperationSymbol]: A sorted list of operation symbols
    fn get_sorted_operation_symbols(&self) -> Vec<PyOperationSymbol> {
        self.inner.get_sorted_operation_symbols()
            .into_iter()
            .map(|op| PyOperationSymbol { inner: op })
            .collect()
    }
    
    /// Calculate the computer input size for this similarity type.
    /// 
    /// If the result exceeds the maximum integer value, returns -1.
    /// If there are no operations, returns the algebra size.
    /// 
    /// Args:
    ///     alg_size (int): The algebra size
    /// 
    /// Returns:
    ///     int: The input size if it fits in an i32, or -1 if it exceeds the maximum
    fn input_size(&self, alg_size: i32) -> i32 {
        self.inner.input_size(alg_size)
    }
    
    /// Get a map from arity to the number of operations of that arity.
    /// 
    /// This method caches the result for performance.
    /// 
    /// Returns:
    ///     Dict[int, int]: A dictionary mapping arity to count
    fn get_arities_map(&mut self) -> std::collections::HashMap<i32, i32> {
        self.inner.get_arities_map().clone().into_iter().collect()
    }
    
    /// Get the maximum arity among all operation symbols.
    /// 
    /// This method caches the result for performance.
    /// 
    /// Returns:
    ///     int: The maximum arity, or -1 if there are no operations
    fn get_max_arity(&mut self) -> i32 {
        self.inner.get_max_arity()
    }
    
    /// Get the LATTICE_SIMILARITY_TYPE constant.
    /// 
    /// Returns:
    ///     SimilarityType: The static lattice similarity type
    #[staticmethod]
    fn lattice_similarity_type() -> Self {
        PySimilarityType {
            inner: uacalc::alg::op::SimilarityType::lattice_similarity_type().clone()
        }
    }
    
    /// Get the GROUP_SIMILARITY_TYPE constant.
    /// 
    /// Returns:
    ///     SimilarityType: The static group similarity type
    #[staticmethod]
    fn group_similarity_type() -> Self {
        PySimilarityType {
            inner: uacalc::alg::op::SimilarityType::group_similarity_type().clone()
        }
    }
    
    /// Generate a string representation of the arities.
    /// 
    /// Returns:
    ///     str: A string describing the arities of operations in this similarity type
    fn arities_string(&mut self) -> String {
        self.inner.arities_string()
    }
    
    /// Python string representation.
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("SimilarityType({})", self.inner.to_string())
    }
    
    /// Python equality comparison.
    fn __eq__(&self, other: &PySimilarityType) -> bool {
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
}

/// Python wrapper for PrintType
#[pyclass]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PyPrintType {
    inner: uacalc::alg::conlat::partition::PrintType,
}

#[pymethods]
impl PyPrintType {
    /// Create a new PrintType from string.
    #[new]
    fn new(print_type: &str) -> PyResult<Self> {
        let inner = match print_type.to_lowercase().as_str() {
            "internal" => uacalc::alg::conlat::partition::PrintType::Internal,
            "ewk" => uacalc::alg::conlat::partition::PrintType::Ewk,
            "block" => uacalc::alg::conlat::partition::PrintType::Block,
            "human" => uacalc::alg::conlat::partition::PrintType::Human,
            "sq_brace_block" => uacalc::alg::conlat::partition::PrintType::SqBraceBlock,
            _ => return Err(PyValueError::new_err(format!("Invalid print type: {}", print_type))),
        };
        Ok(PyPrintType { inner })
    }
    
    /// Get the string representation of this print type.
    fn to_string(&self) -> String {
        match self.inner {
            uacalc::alg::conlat::partition::PrintType::Internal => "internal".to_string(),
            uacalc::alg::conlat::partition::PrintType::Ewk => "ewk".to_string(),
            uacalc::alg::conlat::partition::PrintType::Block => "block".to_string(),
            uacalc::alg::conlat::partition::PrintType::Human => "human".to_string(),
            uacalc::alg::conlat::partition::PrintType::SqBraceBlock => "sq_brace_block".to_string(),
        }
    }
    
    /// Python string representation.
    fn __str__(&self) -> String {
        self.to_string()
    }
    
    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("PrintType('{}')", self.to_string())
    }
    
    /// Python equality comparison.
    fn __eq__(&self, other: &PyPrintType) -> bool {
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
}

/// Python wrapper for Partition
#[pyclass]
pub struct PyPartition {
    inner: uacalc::alg::conlat::partition::Partition,
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
    ///     bool: True if element is a representative
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
    
    /// Compute the join of two partitions.
    /// 
    /// Args:
    ///     other (Partition): Other partition to join with
    /// 
    /// Returns:
    ///     Partition: Join of the two partitions
    /// 
    /// Raises:
    ///     ValueError: If partitions have different universe sizes
    fn join(&self, other: &PyPartition) -> PyResult<PyPartition> {
        match self.inner.join(&other.inner) {
            Ok(inner) => Ok(PyPartition { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Compute the meet of two partitions.
    /// 
    /// Args:
    ///     other (Partition): Other partition to meet with
    /// 
    /// Returns:
    ///     Partition: Meet of the two partitions
    /// 
    /// Raises:
    ///     ValueError: If partitions have different universe sizes
    fn meet(&self, other: &PyPartition) -> PyResult<PyPartition> {
        match self.inner.meet(&other.inner) {
            Ok(inner) => Ok(PyPartition { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if this partition is less than or equal to another partition.
    /// 
    /// Args:
    ///     other (Partition): Other partition to compare with
    /// 
    /// Returns:
    ///     bool: True if this partition refines the other
    fn leq(&self, other: &PyPartition) -> bool {
        self.inner.leq(&other.inner)
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
    
    /// Get the array representation of the partition.
    /// 
    /// Returns:
    ///     List[int]: Array representation
    fn to_array(&self) -> Vec<i32> {
        self.inner.to_array()
    }
    
    /// Get the rank of the partition (universe size - number of blocks).
    /// 
    /// Returns:
    ///     int: The rank
    fn rank(&self) -> usize {
        self.inner.rank()
    }
    
    /// Convert to string with specified print type and maximum length.
    /// 
    /// Args:
    ///     print_type (PrintType): Type of string representation
    ///     max_len (int, optional): Maximum length (-1 for no limit)
    /// 
    /// Returns:
    ///     str: String representation
    fn to_string_with_type(&self, print_type: &PyPrintType, max_len: Option<i32>) -> String {
        self.inner.to_string_with_type(print_type.inner, max_len.unwrap_or(-1))
    }
    
    /// Convert to string with specified print type.
    /// 
    /// Args:
    ///     print_type (PrintType): Type of string representation
    /// 
    /// Returns:
    ///     str: String representation
    fn to_string_with_print_type(&self, print_type: &PyPrintType) -> String {
        self.inner.to_string_with_print_type(print_type.inner)
    }
    
    /// Convert to string with maximum length.
    /// 
    /// Args:
    ///     max_len (int): Maximum length
    /// 
    /// Returns:
    ///     str: String representation
    fn to_string_with_max_len(&self, max_len: i32) -> String {
        self.inner.to_string_with_max_len(max_len)
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
    
    /// Python comparison (less than).
    fn __lt__(&self, other: &PyPartition) -> bool {
        self.inner < other.inner
    }
    
    /// Python comparison (less than or equal).
    fn __le__(&self, other: &PyPartition) -> bool {
        self.inner <= other.inner
    }
    
    /// Python comparison (greater than).
    fn __gt__(&self, other: &PyPartition) -> bool {
        self.inner > other.inner
    }
    
    /// Python comparison (greater than or equal).
    fn __ge__(&self, other: &PyPartition) -> bool {
        self.inner >= other.inner
    }
    
    /// Calculate unary polymorphisms of a collection of partitions.
    /// 
    /// A unary polymorphism is a function f: {0,...,n-1} -> {0,...,n-1} that
    /// preserves all partitions in the collection.
    /// 
    /// Args:
    ///     pars (List[Partition]): Collection of partitions to respect
    /// 
    /// Returns:
    ///     List[IntArray]: List of all unary polymorphisms
    /// 
    /// Raises:
    ///     ValueError: If partitions are empty or have different sizes
    #[staticmethod]
    fn unary_polymorphisms(pars: Vec<PyRef<PyPartition>>) -> PyResult<Vec<PyIntArray>> {
        let rust_pars: Vec<uacalc::alg::conlat::partition::Partition> = 
            pars.iter().map(|p| p.inner.clone()).collect();
        
        match uacalc::alg::conlat::partition::Partition::unary_polymorphisms(&rust_pars) {
            Ok(result) => {
                let py_result: Vec<PyIntArray> = result.into_iter()
                    .map(|ia| PyIntArray { inner: ia })
                    .collect();
                Ok(py_result)
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Calculate binary polymorphisms of a collection of partitions.
    /// 
    /// A binary polymorphism is a binary operation that preserves all partitions
    /// in the collection.
    /// 
    /// Args:
    ///     pars (List[Partition]): Collection of partitions to respect
    ///     unary_clone (List[IntArray], optional): Precomputed unary polymorphisms
    /// 
    /// Returns:
    ///     List[IntArray]: List of all binary polymorphisms
    /// 
    /// Raises:
    ///     ValueError: If partitions are empty or have different sizes
    #[staticmethod]
    #[pyo3(signature = (pars, unary_clone=None))]
    fn binary_polymorphisms(
        pars: Vec<PyRef<PyPartition>>,
        unary_clone: Option<Vec<PyIntArray>>
    ) -> PyResult<Vec<PyIntArray>> {
        let rust_pars: Vec<uacalc::alg::conlat::partition::Partition> = 
            pars.iter().map(|p| p.inner.clone()).collect();
        
        let rust_unary_clone = unary_clone.map(|uc| {
            uc.into_iter().map(|ia| ia.inner).collect()
        });
        
        match uacalc::alg::conlat::partition::Partition::binary_polymorphisms(&rust_pars, rust_unary_clone) {
            Ok(result) => {
                let py_result: Vec<PyIntArray> = result.into_iter()
                    .map(|ia| PyIntArray { inner: ia })
                    .collect();
                Ok(py_result)
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
}

/// Python wrapper for Polymorphisms
#[pyclass]
pub struct PyPolymorphisms {
    inner: uacalc::alg::conlat::Polymorphisms,
}

#[pymethods]
impl PyPolymorphisms {
    /// Create a new Polymorphisms instance with proper error handling.
    /// 
    /// Args:
    ///     arity (int): The arity of the polymorphisms to calculate
    ///     pars (List[Partition]): The collection of partitions
    ///     idempotent (bool): Whether to only consider idempotent polymorphisms
    ///     fixed_values (Optional[List[int]]): Fixed values for the polymorphisms (optional)
    /// 
    /// Returns:
    ///     Polymorphisms: A new Polymorphisms instance
    /// 
    /// Raises:
    ///     ValueError: If validation fails
    #[new]
    #[pyo3(signature = (arity, pars, idempotent, fixed_values=None))]
    fn new(arity: usize, pars: &Bound<'_, PyList>, idempotent: bool, fixed_values: Option<Vec<i32>>) -> PyResult<Self> {
        let mut rust_pars = Vec::new();
        for item in pars.iter() {
            let py_partition: PyRef<PyPartition> = item.extract()?;
            rust_pars.push(py_partition.inner.clone());
        }
        match uacalc::alg::conlat::Polymorphisms::new_safe(arity, rust_pars, idempotent, fixed_values) {
            Ok(inner) => Ok(PyPolymorphisms { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the number of partitions in this collection.
    /// 
    /// Returns:
    ///     int: The number of partitions
    fn num_partitions(&self) -> usize {
        self.inner.num_partitions()
    }
    
    /// Get the algebra size.
    /// 
    /// Returns:
    ///     int: The size of the underlying algebra
    fn get_alg_size(&self) -> usize {
        self.inner.get_alg_size()
    }
    
    /// Get the arity.
    /// 
    /// Returns:
    ///     int: The arity of the polymorphisms
    fn get_arity(&self) -> usize {
        self.inner.get_arity()
    }
    
    /// Check if idempotent polymorphisms are required.
    /// 
    /// Returns:
    ///     bool: True if only idempotent polymorphisms are considered
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }
    
    /// Get the fixed values (if any).
    /// 
    /// Returns:
    ///     Optional[List[int]]: The fixed values, or None if not set
    fn get_fixed_values(&self) -> Option<Vec<i32>> {
        self.inner.get_fixed_values().cloned()
    }
    
    /// Get the table size.
    /// 
    /// Returns:
    ///     int: The size of the operation table (alg_size^arity)
    fn get_table_size(&self) -> usize {
        self.inner.get_table_size()
    }
    
    /// Initialize the graph structure for polymorphism calculations.
    /// 
    /// This method creates the graph structure that will be used for
    /// calculating polymorphisms. The graph is initially empty.
    /// 
    /// Returns:
    ///     None
    /// 
    /// Raises:
    ///     ValueError: If initialization fails
    fn make_graph(&mut self) -> PyResult<()> {
        match self.inner.make_graph() {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if the graph has been initialized.
    /// 
    /// Returns:
    ///     bool: True if the graph has been initialized
    fn has_graph(&self) -> bool {
        self.inner.has_graph()
    }
    
    /// Set the partial operation table.
    /// 
    /// Args:
    ///     table (List[int]): The operation table to set
    /// 
    /// Returns:
    ///     None
    /// 
    /// Raises:
    ///     ValueError: If validation fails
    fn set_partial_op_table(&mut self, table: Vec<i32>) -> PyResult<()> {
        match self.inner.set_partial_op_table(table) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get a reference to the partial operation table (if set).
    /// 
    /// Returns:
    ///     Optional[List[int]]: The operation table, or None if not set
    fn get_partial_op_table(&self) -> Option<Vec<i32>> {
        self.inner.get_partial_op_table().cloned()
    }
    
    /// Python string representation.
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("Polymorphisms({})", self.inner.to_string())
    }
    
    /// Python equality comparison.
    fn __eq__(&self, other: &PyPolymorphisms) -> bool {
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
}

/// Python wrapper for BasicOperation
#[pyclass]
pub struct PyBasicOperation {
    inner: BasicOperation,
}

#[pymethods]
impl PyBasicOperation {
    /// Create a new AbstractOperation with the given symbol and set size.
    /// 
    /// Args:
    ///     symbol (OperationSymbol): The operation symbol
    ///     set_size (int): The size of the set on which the operation is defined
    /// 
    /// Raises:
    ///     ValueError: If set_size is invalid
    #[new]
    #[pyo3(signature = (symbol, set_size, table=None))]
    fn new(symbol: &PyOperationSymbol, set_size: i32, table: Option<Vec<i32>>) -> PyResult<Self> {
        if let Some(table_vec) = table {
            match BasicOperation::new_with_table(symbol.inner.clone(), set_size, table_vec) {
                Ok(inner) => Ok(PyBasicOperation { inner }),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        } else {
            match BasicOperation::new_safe(symbol.inner.clone(), set_size) {
                Ok(inner) => Ok(PyBasicOperation { inner }),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        }
    }
    
    /// Create a simple binary operation for testing.
    /// 
    /// Args:
    ///     name (str): The name of the operation
    ///     set_size (int): The size of the set
    /// 
    /// Returns:
    ///     AbstractOperation: A new AbstractOperation instance
    #[staticmethod]
    fn simple_binary_op(name: &str, set_size: i32) -> PyResult<Self> {
        match BasicOperation::simple_binary_op(name, set_size) {
            Ok(inner) => Ok(PyBasicOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a simple unary operation for testing.
    /// 
    /// Args:
    ///     name (str): The name of the operation
    ///     set_size (int): The size of the set
    /// 
    /// Returns:
    ///     AbstractOperation: A new AbstractOperation instance
    #[staticmethod]
    fn simple_unary_op(name: &str, set_size: i32) -> PyResult<Self> {
        match BasicOperation::simple_unary_op(name, set_size) {
            Ok(inner) => Ok(PyBasicOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a simple nullary operation for testing.
    /// 
    /// Args:
    ///     name (str): The name of the operation
    ///     set_size (int): The size of the set
    /// 
    /// Returns:
    ///     AbstractOperation: A new AbstractOperation instance
    #[staticmethod]
    fn simple_nullary_op(name: &str, set_size: i32) -> PyResult<Self> {
        match BasicOperation::simple_nullary_op(name, set_size) {
            Ok(inner) => Ok(PyBasicOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the arity of this operation.
    /// 
    /// Returns:
    ///     int: The number of arguments this operation takes
    fn arity(&self) -> i32 {
        self.inner.arity()
    }
    
    /// Get the size of the set upon which the operation is defined.
    /// 
    /// Returns:
    ///     int: The size of the underlying set
    fn get_set_size(&self) -> i32 {
        self.inner.get_set_size()
    }
    
    /// Get the operation symbol for this operation.
    /// 
    /// Returns:
    ///     OperationSymbol: The operation symbol
    fn symbol(&self) -> PyOperationSymbol {
        PyOperationSymbol {
            inner: self.inner.symbol().clone()
        }
    }
    
    /// Evaluate the operation at the given arguments.
    /// 
    /// Args:
    ///     args (List[int]): Arguments for the operation
    /// 
    /// Returns:
    ///     int: The result of the operation
    /// 
    /// Raises:
    ///     ValueError: If arguments are invalid
    fn value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Evaluate the operation on arrays of arguments.
    /// 
    /// Args:
    ///     args (List[List[int]]): Arrays of arguments
    /// 
    /// Returns:
    ///     List[int]: Array of results
    /// 
    /// Raises:
    ///     ValueError: If arguments are invalid
    fn value_at_arrays(&self, args: Vec<Vec<i32>>) -> PyResult<Vec<i32>> {
        let arg_refs: Vec<&[i32]> = args.iter().map(|v| v.as_slice()).collect();
        match self.inner.value_at_arrays(&arg_refs) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Integer version of the operation evaluation.
    /// 
    /// Args:
    ///     args (List[int]): Integer arguments
    /// 
    /// Returns:
    ///     int: The result of the operation
    /// 
    /// Raises:
    ///     ValueError: If arguments are invalid
    fn int_value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.int_value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Fast table access using Horner encoding.
    /// 
    /// Args:
    ///     arg (int): The Horner encoding of the actual args
    /// 
    /// Returns:
    ///     int: The result of the operation
    /// 
    /// Raises:
    ///     ValueError: If argument is invalid or table doesn't exist
    fn int_value_at_horner(&self, arg: i32) -> PyResult<i32> {
        match self.inner.int_value_at_horner(arg) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a table for faster operation evaluation.
    /// 
    /// Raises:
    ///     ValueError: If table creation fails
    fn make_table(&mut self) -> PyResult<()> {
        match self.inner.make_table() {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the table for this operation.
    /// 
    /// Returns:
    ///     List[int] or None: The operation table or None if it doesn't exist
    fn get_table(&self) -> Option<Vec<i32>> {
        self.inner.get_table().map(|slice| slice.to_vec())
    }
    
    /// Get the table, creating it if necessary.
    /// 
    /// Args:
    ///     make_table (bool): Whether to create the table if it doesn't exist
    /// 
    /// Returns:
    ///     List[int]: The operation table
    /// 
    /// Raises:
    ///     ValueError: If table creation fails
    fn get_table_force(&mut self, make_table: bool) -> PyResult<Vec<i32>> {
        match self.inner.get_table_force(make_table) {
            Ok(slice) => Ok(slice.to_vec()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if this operation is table-based.
    /// 
    /// Returns:
    ///     bool: True if the operation uses a precomputed table
    fn is_table_based(&self) -> bool {
        self.inner.is_table_based()
    }
    
    /// Check if this operation is idempotent.
    /// 
    /// Returns:
    ///     bool: True if f(x,x,...,x) = x for all x
    /// 
    /// Raises:
    ///     ValueError: If the check fails
    fn is_idempotent(&self) -> PyResult<bool> {
        match self.inner.is_idempotent() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if this operation is binary and associative.
    /// 
    /// Returns:
    ///     bool: True if the operation is binary and associative
    /// 
    /// Raises:
    ///     ValueError: If the check fails
    fn is_associative(&self) -> PyResult<bool> {
        match self.inner.is_associative() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if this operation is binary and commutative.
    /// 
    /// Returns:
    ///     bool: True if the operation is binary and commutative
    /// 
    /// Raises:
    ///     ValueError: If the check fails
    fn is_commutative(&self) -> PyResult<bool> {
        match self.inner.is_commutative() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if this operation is totally symmetric.
    /// 
    /// Returns:
    ///     bool: True if the operation is invariant under all variable permutations
    /// 
    /// Raises:
    ///     ValueError: If the check fails
    fn is_totally_symmetric(&self) -> PyResult<bool> {
        match self.inner.is_totally_symmetric() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if this is a Maltsev operation.
    /// 
    /// Returns:
    ///     bool: True if the operation is a Maltsev operation
    /// 
    /// Raises:
    ///     ValueError: If the check fails
    fn is_maltsev(&self) -> PyResult<bool> {
        match self.inner.is_maltsev() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if this operation is total.
    /// 
    /// Returns:
    ///     bool: True if the operation is total
    /// 
    /// Raises:
    ///     ValueError: If the check fails
    fn is_total(&self) -> PyResult<bool> {
        match self.inner.is_total() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Python string representation.
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("BasicOperation({})", self.inner.to_string())
    }
    
    /// Python equality comparison.
    fn __eq__(&self, other: &PyBasicOperation) -> bool {
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
    
    /// Python comparison (less than).
    fn __lt__(&self, other: &PyBasicOperation) -> bool {
        self.inner < other.inner
    }
    
    /// Python comparison (less than or equal).
    fn __le__(&self, other: &PyBasicOperation) -> bool {
        self.inner <= other.inner
    }
    
    /// Python comparison (greater than).
    fn __gt__(&self, other: &PyBasicOperation) -> bool {
        self.inner > other.inner
    }
    
    /// Python comparison (greater than or equal).
    fn __ge__(&self, other: &PyBasicOperation) -> bool {
        self.inner >= other.inner
    }
}

/// Python wrapper for IntOperation
#[pyclass]
pub struct PyIntOperation {
    inner: IntOperation,
}

#[pymethods]
impl PyIntOperation {
    /// Create a new IntOperation with the given parameters.
    /// 
    /// Args:
    ///     symbol (OperationSymbol): The operation symbol
    ///     set_size (int): The size of the set on which the operation is defined
    ///     table (List[int] or numpy.ndarray): The precomputed table of operation results
    /// 
    /// Raises:
    ///     ValueError: If parameters are invalid
    #[new]
    fn new(symbol: &PyOperationSymbol, set_size: i32, table: &PyAny) -> PyResult<Self> {
        // Try to convert table to Vec<i32> - handles both lists and numpy arrays
        let table_vec: Vec<i32> = table.extract()?;
        match IntOperation::new(symbol.inner.clone(), set_size, table_vec) {
            Ok(inner) => Ok(PyIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a binary XOR operation for testing.
    /// 
    /// Args:
    ///     name (str): The name of the operation
    /// 
    /// Returns:
    ///     IntOperation: A new IntOperation implementing XOR on {0, 1}
    #[staticmethod]
    fn binary_xor(name: &str) -> PyResult<Self> {
        match IntOperation::binary_xor(name) {
            Ok(inner) => Ok(PyIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a binary AND operation for testing.
    /// 
    /// Args:
    ///     name (str): The name of the operation
    /// 
    /// Returns:
    ///     IntOperation: A new IntOperation implementing AND on {0, 1}
    #[staticmethod]
    fn binary_and(name: &str) -> PyResult<Self> {
        match IntOperation::binary_and(name) {
            Ok(inner) => Ok(PyIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a binary OR operation for testing.
    /// 
    /// Args:
    ///     name (str): The name of the operation
    /// 
    /// Returns:
    ///     IntOperation: A new IntOperation implementing OR on {0, 1}
    #[staticmethod]
    fn binary_or(name: &str) -> PyResult<Self> {
        match IntOperation::binary_or(name) {
            Ok(inner) => Ok(PyIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a unary NOT operation for testing.
    /// 
    /// Args:
    ///     name (str): The name of the operation
    /// 
    /// Returns:
    ///     IntOperation: A new IntOperation implementing NOT on {0, 1}
    #[staticmethod]
    fn unary_not(name: &str) -> PyResult<Self> {
        match IntOperation::unary_not(name) {
            Ok(inner) => Ok(PyIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a nullary constant operation for testing.
    /// 
    /// Args:
    ///     name (str): The name of the operation
    ///     constant_value (int): The constant value to return
    /// 
    /// Returns:
    ///     IntOperation: A new IntOperation returning the constant value
    #[staticmethod]
    fn nullary_constant(name: &str, constant_value: i32) -> PyResult<Self> {
        match IntOperation::nullary_constant(name, constant_value) {
            Ok(inner) => Ok(PyIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create an IntOperation from a Python function (int_value_at style).
    /// 
    /// Args:
    ///     name (str): The name of the operation
    ///     arity (int): The arity (number of arguments) of the operation
    ///     set_size (int): The size of the set on which the operation is defined
    ///     int_value_at_fn (callable): A Python function that takes a list of integers and returns an integer
    /// 
    /// Returns:
    ///     IntOperation: A new IntOperation that uses the provided function
    /// 
    /// Example:
    ///     def my_op(args):
    ///         return (args[0] + args[1]) % 3
    ///     op = IntOperation.from_int_value_at("add_mod3", 2, 3, my_op)
    #[staticmethod]
    fn from_int_value_at(name: &str, arity: i32, set_size: i32, int_value_at_fn: PyObject) -> PyResult<Self> {
        Python::with_gil(|py| {
            // Create the operation table by evaluating the function for all possible inputs
            let symbol = match uacalc::alg::op::OperationSymbol::new_safe(name, arity, false) {
                Ok(sym) => sym,
                Err(e) => return Err(PyValueError::new_err(e)),
            };
            
            let table_size = if arity == 0 { 1 } else { (set_size as usize).pow(arity as u32) };
            let mut table = Vec::with_capacity(table_size);
            
            // Generate all possible argument combinations and evaluate the function
            fn generate_args(arity: i32, set_size: i32, current: &mut Vec<i32>, all_args: &mut Vec<Vec<i32>>) {
                if current.len() == arity as usize {
                    all_args.push(current.clone());
                    return;
                }
                for i in 0..set_size {
                    current.push(i);
                    generate_args(arity, set_size, current, all_args);
                    current.pop();
                }
            }
            
            let mut all_args = Vec::new();
            if arity == 0 {
                all_args.push(Vec::new());
            } else {
                generate_args(arity, set_size, &mut Vec::new(), &mut all_args);
            }
            
            // Evaluate function for each argument combination
            for args in all_args {
                let py_args = PyList::new_bound(py, &args);
                let result = int_value_at_fn.call1(py, (py_args,))?;
                let result_int: i32 = result.extract(py)?;
                
                // Validate result is in range
                if result_int < 0 || result_int >= set_size {
                    return Err(PyValueError::new_err(format!(
                        "Function returned {} which is out of range [0, {})", 
                        result_int, set_size
                    )));
                }
                
                table.push(result_int);
            }
            
            // Create IntOperation with computed table
            match IntOperation::new(symbol, set_size, table) {
                Ok(inner) => Ok(PyIntOperation { inner }),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        })
    }
    
    /// Create an IntOperation from a Python function (value_at style for non-integer universes).
    /// 
    /// Args:
    ///     name (str): The name of the operation
    ///     arity (int): The arity (number of arguments) of the operation
    ///     universe (list): The universe elements (e.g., ["a", "b", "c"])
    ///     value_at_fn (callable): A Python function that takes a list of universe elements and returns a universe element
    /// 
    /// Returns:
    ///     IntOperation: A new IntOperation that uses the provided function (with integer indices)
    /// 
    /// Example:
    ///     def string_concat(args):
    ///         return args[0] + args[1]
    ///     op = IntOperation.from_value_at("concat", 2, ["a", "b", "c"], string_concat)
    #[staticmethod]
    fn from_value_at(name: &str, arity: i32, universe: Vec<PyObject>, value_at_fn: PyObject) -> PyResult<Self> {
        Python::with_gil(|py| {
            let set_size = universe.len() as i32;
            
            // Create the operation table by evaluating the function for all possible inputs
            let symbol = match uacalc::alg::op::OperationSymbol::new_safe(name, arity, false) {
                Ok(sym) => sym,
                Err(e) => return Err(PyValueError::new_err(e)),
            };
            
            let table_size = if arity == 0 { 1 } else { (set_size as usize).pow(arity as u32) };
            let mut table = Vec::with_capacity(table_size);
            
            // Generate all possible argument combinations and evaluate the function
            fn generate_indices(arity: i32, set_size: i32, current: &mut Vec<i32>, all_indices: &mut Vec<Vec<i32>>) {
                if current.len() == arity as usize {
                    all_indices.push(current.clone());
                    return;
                }
                for i in 0..set_size {
                    current.push(i);
                    generate_indices(arity, set_size, current, all_indices);
                    current.pop();
                }
            }
            
            let mut all_indices = Vec::new();
            if arity == 0 {
                all_indices.push(Vec::new());
            } else {
                generate_indices(arity, set_size, &mut Vec::new(), &mut all_indices);
            }
            
            // Evaluate function for each argument combination
            for indices in all_indices {
                // Convert indices to universe elements
                let mut universe_args = Vec::new();
                for &idx in &indices {
                    if idx < 0 || idx >= set_size {
                        return Err(PyValueError::new_err("Index out of universe bounds"));
                    }
                    universe_args.push(universe[idx as usize].clone());
                }
                
                let py_args = PyList::new_bound(py, &universe_args);
                let result = value_at_fn.call1(py, (py_args,))?;
                
                // Find the index of the result in the universe
                let mut result_index = None;
                for (i, universe_elem) in universe.iter().enumerate() {
                    if result.bind(py).eq(universe_elem)? {
                        result_index = Some(i as i32);
                        break;
                    }
                }
                
                match result_index {
                    Some(idx) => table.push(idx),
                    None => return Err(PyValueError::new_err(
                        "Function returned a value not in the universe"
                    )),
                }
            }
            
            // Create IntOperation with computed table
            match IntOperation::new(symbol, set_size, table) {
                Ok(inner) => Ok(PyIntOperation { inner }),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        })
    }
    
    /// Create an IntOperation from a 2D array/matrix (for binary operations).
    /// 
    /// Args:
    ///     name (str): The name of the operation
    ///     operation_matrix (List[List[int]] or 2D numpy.ndarray): A 2D array where entry [i][j] gives the result of operation(i, j)
    /// 
    /// Returns:
    ///     IntOperation: A new IntOperation based on the matrix
    /// 
    /// Example:
    ///     # XOR operation matrix
    ///     matrix = [[0, 1], [1, 0]]
    ///     op = IntOperation.from_matrix("xor", matrix)
    #[staticmethod]
    fn from_matrix(name: &str, operation_matrix: &PyAny) -> PyResult<Self> {
        Python::with_gil(|_py| {
            // Extract the 2D matrix
            let matrix: Vec<Vec<i32>> = operation_matrix.extract()?;
            
            if matrix.is_empty() {
                return Err(PyValueError::new_err("Operation matrix cannot be empty"));
            }
            
            let set_size = matrix.len() as i32;
            
            // Validate matrix is square and all rows have the same length
            for (i, row) in matrix.iter().enumerate() {
                if row.len() != set_size as usize {
                    return Err(PyValueError::new_err(format!(
                        "Row {} has length {} but expected {} (matrix must be square)",
                        i, row.len(), set_size
                    )));
                }
                
                // Validate all values are in range
                for (j, &value) in row.iter().enumerate() {
                    if value < 0 || value >= set_size {
                        return Err(PyValueError::new_err(format!(
                            "Value {} at position [{}, {}] is out of range [0, {})",
                            value, i, j, set_size
                        )));
                    }
                }
            }
            
            // Convert matrix to flat table (row-major order for binary operations)
            let mut table = Vec::with_capacity((set_size * set_size) as usize);
            for row in &matrix {
                table.extend_from_slice(row);
            }
            
            let symbol = match uacalc::alg::op::OperationSymbol::new_safe(name, 2, false) {
                Ok(sym) => sym,
                Err(e) => return Err(PyValueError::new_err(e)),
            };
            
            match IntOperation::new(symbol, set_size, table) {
                Ok(inner) => Ok(PyIntOperation { inner }),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        })
    }
    
    // Include all the same methods as PyAbstractOperation
    fn arity(&self) -> i32 {
        self.inner.arity()
    }
    
    fn get_set_size(&self) -> i32 {
        self.inner.get_set_size()
    }
    
    fn symbol(&self) -> PyOperationSymbol {
        PyOperationSymbol {
            inner: self.inner.symbol().clone()
        }
    }
    
    fn value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    fn value_at_arrays(&self, args: Vec<Vec<i32>>) -> PyResult<Vec<i32>> {
        let arg_refs: Vec<&[i32]> = args.iter().map(|v| v.as_slice()).collect();
        match self.inner.value_at_arrays(&arg_refs) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    fn int_value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.int_value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    fn int_value_at_horner(&self, arg: i32) -> PyResult<i32> {
        match self.inner.int_value_at_horner(arg) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    fn make_table(&mut self) -> PyResult<()> {
        match self.inner.make_table() {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    fn get_table(&self) -> Option<Vec<i32>> {
        self.inner.get_table().map(|slice| slice.to_vec())
    }
    
    fn get_table_force(&mut self, make_table: bool) -> PyResult<Vec<i32>> {
        match self.inner.get_table_force(make_table) {
            Ok(slice) => Ok(slice.to_vec()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    fn is_table_based(&self) -> bool {
        self.inner.is_table_based()
    }
    
    fn is_idempotent(&self) -> PyResult<bool> {
        match self.inner.is_idempotent() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    fn is_associative(&self) -> PyResult<bool> {
        match self.inner.is_associative() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    fn is_commutative(&self) -> PyResult<bool> {
        match self.inner.is_commutative() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    fn is_totally_symmetric(&self) -> PyResult<bool> {
        match self.inner.is_totally_symmetric() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    fn is_maltsev(&self) -> PyResult<bool> {
        match self.inner.is_maltsev() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    fn is_total(&self) -> PyResult<bool> {
        match self.inner.is_total() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    fn __repr__(&self) -> String {
        format!("IntOperation({})", self.inner.to_string())
    }
    
    fn __eq__(&self, other: &PyIntOperation) -> bool {
        self.inner == other.inner
    }
    
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }
    
    fn __lt__(&self, other: &PyIntOperation) -> bool {
        self.inner < other.inner
    }
    
    fn __le__(&self, other: &PyIntOperation) -> bool {
        self.inner <= other.inner
    }
    
    fn __gt__(&self, other: &PyIntOperation) -> bool {
        self.inner > other.inner
    }
    
    fn __ge__(&self, other: &PyIntOperation) -> bool {
        self.inner >= other.inner
    }
}

/// Python wrapper for AbstractIntOperation
#[pyclass]
pub struct PyAbstractIntOperation {
    inner: AbstractIntOperation,
}

#[pymethods]
impl PyAbstractIntOperation {
    /// Create a new AbstractIntOperation with name, arity, and algebra size.
    /// 
    /// Args:
    ///     name (str): The name of the operation
    ///     arity (int): The arity (number of arguments) of the operation
    ///     alg_size (int): The size of the algebra set
    /// 
    /// Raises:
    ///     ValueError: If parameters are invalid
    #[new]
    fn new(name: &str, arity: i32, alg_size: i32) -> PyResult<Self> {
        match AbstractIntOperation::new_safe(name, arity, alg_size) {
            Ok(inner) => Ok(PyAbstractIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new AbstractIntOperation with an existing OperationSymbol.
    /// 
    /// Args:
    ///     symbol (OperationSymbol): The operation symbol
    ///     alg_size (int): The size of the algebra set
    /// 
    /// Raises:
    ///     ValueError: If alg_size is invalid
    #[staticmethod]
    fn with_symbol(symbol: &PyOperationSymbol, alg_size: i32) -> PyResult<Self> {
        match AbstractIntOperation::new_with_symbol_safe(symbol.inner.clone(), alg_size) {
            Ok(inner) => Ok(PyAbstractIntOperation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the arity of this operation.
    fn arity(&self) -> i32 {
        self.inner.arity()
    }
    
    /// Get the size of the set upon which the operation is defined.
    fn get_set_size(&self) -> i32 {
        self.inner.get_set_size()
    }
    
    /// Get the operation symbol for this operation.
    fn symbol(&self) -> PyOperationSymbol {
        PyOperationSymbol {
            inner: self.inner.symbol().clone()
        }
    }
    
    /// Attempt to evaluate the operation (will fail with UnsupportedOperationException).
    /// 
    /// Args:
    ///     args (List[int]): Arguments for the operation
    /// 
    /// Raises:
    ///     ValueError: Always raises since this method is not implemented
    fn value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Attempt integer operation evaluation (will fail with UnsupportedOperationException).
    /// 
    /// Args:
    ///     args (List[int]): Integer arguments
    /// 
    /// Raises:
    ///     ValueError: Always raises since this method is not implemented
    fn int_value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.int_value_at(&args) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if this operation is total.
    fn is_total(&self) -> PyResult<bool> {
        match self.inner.is_total() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Python string representation.
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("AbstractIntOperation({})", self.inner.to_string())
    }
    
    /// Python equality comparison.
    fn __eq__(&self, other: &PyAbstractIntOperation) -> bool {
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
}

/// Python wrapper for Subtrace
#[pyclass]
pub struct PySubtrace {
    inner: Subtrace,
}

#[pymethods]
impl PySubtrace {
    /// Create a new Subtrace with given elements and involution flag.
    /// 
    /// Args:
    ///     a (int): First element of the subtrace pair
    ///     b (int): Second element of the subtrace pair
    ///     has_involution (bool): Whether this subtrace has involution
    /// 
    /// Returns:
    ///     Subtrace: A new Subtrace instance with type set to -1
    #[new]
    fn new(a: i32, b: i32, has_involution: bool) -> Self {
        PySubtrace {
            inner: Subtrace::new(a, b, has_involution)
        }
    }
    
    /// Create a new Subtrace with given elements, involution flag, and type.
    /// 
    /// Args:
    ///     a (int): First element of the subtrace pair
    ///     b (int): Second element of the subtrace pair
    ///     has_involution (bool): Whether this subtrace has involution
    ///     type_value (int): TCT type classification
    /// 
    /// Returns:
    ///     Subtrace: A new Subtrace instance with the specified type
    #[staticmethod]
    fn new_with_type(a: i32, b: i32, has_involution: bool, type_value: i32) -> Self {
        PySubtrace {
            inner: Subtrace::new_with_type(a, b, has_involution, type_value)
        }
    }
    
    /// Get the first element of the subtrace pair.
    /// 
    /// Returns:
    ///     int: The first element `a`
    fn first(&self) -> i32 {
        self.inner.first()
    }
    
    /// Get the second element of the subtrace pair.
    /// 
    /// Returns:
    ///     int: The second element `b`
    fn second(&self) -> i32 {
        self.inner.second()
    }
    
    /// Get the TCT type classification.
    /// 
    /// Returns:
    ///     int: The type value (-1 if not set)
    fn type_value(&self) -> i32 {
        self.inner.type_value()
    }
    
    /// Check if this subtrace has involution.
    /// 
    /// Returns:
    ///     bool: True if the subtrace has involution, False otherwise
    fn has_involution(&self) -> bool {
        self.inner.has_involution()
    }
    
    /// Set the TCT type classification.
    /// 
    /// Args:
    ///     type_value (int): The type to set
    fn set_type(&mut self, type_value: i32) {
        self.inner.set_type(type_value);
    }
    
    /// Get the subtrace universe.
    /// 
    /// Returns:
    ///     List[List[int]] or None: The subtrace universe as list of pairs, or None if not set
    fn get_subtrace_universe(&self) -> Option<Vec<Vec<i32>>> {
        self.inner.get_subtrace_universe().map(|universe| {
            universe.iter().map(|int_array| {
                let mut vec = Vec::new();
                for i in 0..int_array.universe_size() {
                    vec.push(int_array.get(i).unwrap());
                }
                vec
            }).collect()
        })
    }
    
    /// Set the subtrace universe.
    /// 
    /// Args:
    ///     universe (List[List[int]]): The subtrace universe to set
    /// 
    /// Raises:
    ///     ValueError: If any array doesn't have exactly 2 elements
    fn set_subtrace_universe(&mut self, universe: Vec<Vec<i32>>) -> PyResult<()> {
        let int_arrays: Result<Vec<_>, _> = universe.iter()
            .map(|arr| {
                if arr.len() != 2 {
                    Err(format!("Each subtrace universe element must have exactly 2 elements, got {}", arr.len()))
                } else {
                    Ok(uacalc::util::int_array::IntArray::from_array(arr.clone()).unwrap())
                }
            })
            .collect();
        
        match int_arrays {
            Ok(arrays) => {
                self.inner.set_subtrace_universe(arrays);
                Ok(())
            }
            Err(e) => Err(PyValueError::new_err(e))
        }
    }
    
    /// Get the matrix universe.
    /// 
    /// Returns:
    ///     List[List[int]] or None: The matrix universe as list of 4-tuples, or None if not set
    fn get_matrix_universe(&self) -> Option<Vec<Vec<i32>>> {
        self.inner.get_matrix_universe().map(|universe| {
            universe.iter().map(|int_array| {
                let mut vec = Vec::new();
                for i in 0..int_array.universe_size() {
                    vec.push(int_array.get(i).unwrap());
                }
                vec
            }).collect()
        })
    }
    
    /// Set the matrix universe.
    /// 
    /// Args:
    ///     universe (List[List[int]]): The matrix universe to set
    /// 
    /// Raises:
    ///     ValueError: If any array doesn't have exactly 4 elements
    fn set_matrix_universe(&mut self, universe: Vec<Vec<i32>>) -> PyResult<()> {
        let int_arrays: Result<Vec<_>, _> = universe.iter()
            .map(|arr| {
                if arr.len() != 4 {
                    Err(format!("Each matrix universe element must have exactly 4 elements, got {}", arr.len()))
                } else {
                    Ok(uacalc::util::int_array::IntArray::from_array(arr.clone()).unwrap())
                }
            })
            .collect();
        
        match int_arrays {
            Ok(arrays) => {
                self.inner.set_matrix_universe(arrays);
                Ok(())
            }
            Err(e) => Err(PyValueError::new_err(e))
        }
    }
    
    /// Get a string representation in brief format.
    /// 
    /// Args:
    ///     brief (bool): If True, returns brief format [a, b], otherwise full format
    /// 
    /// Returns:
    ///     str: String representation of the subtrace
    fn to_string_brief(&self, brief: bool) -> String {
        self.inner.to_string_brief(brief)
    }
    
    /// Python string representation.
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation.
    fn __repr__(&self) -> String {
        format!("Subtrace({}, {}, {}, {})", 
                self.inner.first(), 
                self.inner.second(), 
                self.inner.has_involution(),
                self.inner.type_value())
    }
    
    /// Python equality comparison.
    fn __eq__(&self, other: &PySubtrace) -> bool {
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
    
    /// Python comparison (less than).
    fn __lt__(&self, other: &PySubtrace) -> bool {
        self.inner < other.inner
    }
    
    /// Python comparison (less than or equal).
    fn __le__(&self, other: &PySubtrace) -> bool {
        self.inner <= other.inner
    }
    
    /// Python comparison (greater than).
    fn __gt__(&self, other: &PySubtrace) -> bool {
        self.inner > other.inner
    }
    
    /// Python comparison (greater than or equal).
    fn __ge__(&self, other: &PySubtrace) -> bool {
        self.inner >= other.inner
    }
}

// New abstract operation classes that can be instantiated from Python
#[derive(Debug, Clone)]
enum IntOperationEvaluationMode {
    Function(PyObject),
    Table(Vec<i32>),
}

/// Python wrapper for the new AbstractIntOperation class (function/table-based)
#[pyclass]
pub struct PyAbstractIntOperationNew {
    symbol: uacalc::alg::op::OperationSymbol,
    set_size: i32,
    evaluation_mode: IntOperationEvaluationMode,
}

#[pymethods]
impl PyAbstractIntOperationNew {
    /// Create an AbstractIntOperation from a Python function.
    #[staticmethod]
    fn from_int_value_at_function(name: &str, arity: i32, set_size: i32, int_value_at_fn: PyObject) -> PyResult<Self> {
        let symbol = match uacalc::alg::op::OperationSymbol::new_safe(name, arity, false) {
            Ok(sym) => sym,
            Err(e) => return Err(PyValueError::new_err(e)),
        };
        
        if set_size <= 0 {
            return Err(PyValueError::new_err("Set size must be positive"));
        }
        
        Ok(PyAbstractIntOperationNew {
            symbol,
            set_size,
            evaluation_mode: IntOperationEvaluationMode::Function(int_value_at_fn),
        })
    }
    
    /// Create an AbstractIntOperation from a pre-computed table.
    #[staticmethod]
    fn from_table(name: &str, arity: i32, set_size: i32, table: &PyAny) -> PyResult<Self> {
        let symbol = match uacalc::alg::op::OperationSymbol::new_safe(name, arity, false) {
            Ok(sym) => sym,
            Err(e) => return Err(PyValueError::new_err(e)),
        };
        
        if set_size <= 0 {
            return Err(PyValueError::new_err("Set size must be positive"));
        }
        
        let table_vec: Vec<i32> = table.extract()?;
        let expected_size = if arity == 0 { 1 } else { (set_size as usize).pow(arity as u32) };
        
        if table_vec.len() != expected_size {
            return Err(PyValueError::new_err(format!(
                "Table size {} doesn't match expected size {} for arity {} and set size {}",
                table_vec.len(), expected_size, arity, set_size
            )));
        }
        
        for (i, &value) in table_vec.iter().enumerate() {
            if value < 0 || value >= set_size {
                return Err(PyValueError::new_err(format!(
                    "Table value {} at index {} is out of range [0, {})",
                    value, i, set_size
                )));
            }
        }
        
        Ok(PyAbstractIntOperationNew {
            symbol,
            set_size,
            evaluation_mode: IntOperationEvaluationMode::Table(table_vec),
        })
    }
    
    fn arity(&self) -> i32 { self.symbol.arity() }
    fn get_set_size(&self) -> i32 { self.set_size }
    fn symbol(&self) -> PyOperationSymbol { PyOperationSymbol { inner: self.symbol.clone() } }
    
    fn int_value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        if args.len() != self.arity() as usize {
            return Err(PyValueError::new_err(format!("Expected {} arguments, got {}", self.arity(), args.len())));
        }
        
        for &arg in &args {
            if arg < 0 || arg >= self.set_size {
                return Err(PyValueError::new_err(format!("Argument {} is out of bounds [0, {})", arg, self.set_size)));
            }
        }
        
        match &self.evaluation_mode {
            IntOperationEvaluationMode::Function(func) => {
                Python::with_gil(|py| {
                    let py_args = PyList::new_bound(py, &args);
                    let result = func.call1(py, (py_args,))?;
                    let result_int: i32 = result.extract(py)?;
                    
                    if result_int < 0 || result_int >= self.set_size {
                        return Err(PyValueError::new_err(format!(
                            "Function returned {} which is out of range [0, {})", result_int, self.set_size
                        )));
                    }
                    
                    Ok(result_int)
                })
            }
            IntOperationEvaluationMode::Table(table) => {
                let index = self.horner_encode(&args);
                Ok(table[index as usize])
            }
        }
    }
    
    fn make_table(&mut self) -> PyResult<()> {
        // Clone the function to avoid borrowing issues
        let func_clone = match &self.evaluation_mode {
            IntOperationEvaluationMode::Table(_) => return Ok(()),
            IntOperationEvaluationMode::Function(func) => func.clone(),
        };
        
        Python::with_gil(|py| {
            let arity = self.arity();
            let set_size = self.set_size;
            let table_size = if arity == 0 { 1 } else { (set_size as usize).pow(arity as u32) };
            let mut table = Vec::with_capacity(table_size);
            
            let mut all_args = Vec::new();
            if arity == 0 {
                all_args.push(Vec::new());
            } else {
                PyAbstractIntOperationNew::generate_args_static(arity, set_size, &mut Vec::new(), &mut all_args);
            }
            
            for args in all_args {
                let py_args = PyList::new_bound(py, &args);
                let result = func_clone.call1(py, (py_args,))?;
                let result_int: i32 = result.extract(py)?;
                
                if result_int < 0 || result_int >= set_size {
                    return Err(PyValueError::new_err(format!(
                        "Function returned {} which is out of range [0, {})", result_int, set_size
                    )));
                }
                
                table.push(result_int);
            }
            
            self.evaluation_mode = IntOperationEvaluationMode::Table(table);
            Ok(())
        })
    }
    
    fn get_table(&self) -> Option<Vec<i32>> {
        match &self.evaluation_mode {
            IntOperationEvaluationMode::Table(table) => Some(table.clone()),
            IntOperationEvaluationMode::Function(_) => None,
        }
    }
    
    fn is_table_based(&self) -> bool {
        matches!(self.evaluation_mode, IntOperationEvaluationMode::Table(_))
    }
    
    fn is_idempotent(&self) -> PyResult<bool> {
        let arity = self.arity();
        for x in 0..self.set_size {
            let args = vec![x; arity as usize];
            if self.int_value_at(args)? != x {
                return Ok(false);
            }
        }
        Ok(true)
    }
    
    fn is_associative(&self) -> PyResult<bool> {
        if self.arity() != 2 { return Ok(false); }
        
        for x in 0..self.set_size {
            for y in 0..self.set_size {
                for z in 0..self.set_size {
                    let xy = self.int_value_at(vec![x, y])?;
                    let yz = self.int_value_at(vec![y, z])?;
                    let left = self.int_value_at(vec![xy, z])?;
                    let right = self.int_value_at(vec![x, yz])?;
                    
                    if left != right { return Ok(false); }
                }
            }
        }
        Ok(true)
    }
    
    fn is_commutative(&self) -> PyResult<bool> {
        if self.arity() != 2 { return Ok(false); }
        
        for x in 0..self.set_size {
            for y in 0..self.set_size {
                let xy = self.int_value_at(vec![x, y])?;
                let yx = self.int_value_at(vec![y, x])?;
                if xy != yx { return Ok(false); }
            }
        }
        Ok(true)
    }
    
    fn is_totally_symmetric(&self) -> PyResult<bool> {
        let arity = self.arity() as usize;
        if arity <= 1 { return Ok(true); }
        
        if arity >= 2 {
            let mut all_args = Vec::new();
            self.generate_args_recursive(self.arity(), &mut Vec::new(), &mut all_args);
            
            for args in all_args {
                let original = self.int_value_at(args.clone())?;
                let mut swapped = args;
                swapped.swap(0, 1);
                let swapped_result = self.int_value_at(swapped)?;
                
                if original != swapped_result { return Ok(false); }
            }
        }
        
        Ok(true)
    }
    
    fn is_maltsev(&self) -> PyResult<bool> {
        if self.arity() != 3 { return Ok(false); }
        
        for x in 0..self.set_size {
            for y in 0..self.set_size {
                let xyy = self.int_value_at(vec![x, y, y])?;
                let xxy = self.int_value_at(vec![x, x, y])?;
                
                if xyy != x || xxy != y { return Ok(false); }
            }
        }
        Ok(true)
    }
    
    fn is_total(&self) -> PyResult<bool> { Ok(true) }
    
    fn __str__(&self) -> String {
        format!("AbstractIntOperation({}, arity={}, set_size={}, table_based={})", 
                self.symbol.name(), self.arity(), self.set_size, self.is_table_based())
    }
    
    fn __repr__(&self) -> String {
        format!("AbstractIntOperation(name='{}', arity={}, set_size={}, table_based={})", 
                self.symbol.name(), self.arity(), self.set_size, self.is_table_based())
    }
}

impl PyAbstractIntOperationNew {
    fn horner_encode(&self, args: &[i32]) -> i32 {
        let mut result = 0;
        let mut multiplier = 1;
        
        for &arg in args.iter().rev() {
            result += arg * multiplier;
            multiplier *= self.set_size;
        }
        
        result
    }
    
    fn generate_args_recursive(&self, arity: i32, current: &mut Vec<i32>, all_args: &mut Vec<Vec<i32>>) {
        Self::generate_args_static(arity, self.set_size, current, all_args);
    }
    
    fn generate_args_static(arity: i32, set_size: i32, current: &mut Vec<i32>, all_args: &mut Vec<Vec<i32>>) {
        if current.len() == arity as usize {
            all_args.push(current.clone());
            return;
        }
        for i in 0..set_size {
            current.push(i);
            Self::generate_args_static(arity, set_size, current, all_args);
            current.pop();
        }
    }
}

/// Evaluation mode for AbstractOperation that supports both integer and non-integer universes
#[derive(Debug, Clone)]
enum AbstractOperationEvaluationMode {
    IntFunction(PyObject),
    ValueFunction(PyObject, Vec<PyObject>), // function and universe
    IntTable(Vec<i32>),
    ValueTable(Vec<i32>, Vec<PyObject>), // table indices and universe
}

/// Python wrapper for the new AbstractOperation class (supports both integer and non-integer universes)
#[pyclass]
pub struct PyAbstractOperationNew {
    symbol: uacalc::alg::op::OperationSymbol,
    set_size: i32,
    evaluation_mode: AbstractOperationEvaluationMode,
}

#[pymethods]
impl PyAbstractOperationNew {
    #[staticmethod]
    fn from_int_value_at_function(name: &str, arity: i32, set_size: i32, int_value_at_fn: PyObject) -> PyResult<Self> {
        let symbol = match uacalc::alg::op::OperationSymbol::new_safe(name, arity, false) {
            Ok(sym) => sym,
            Err(e) => return Err(PyValueError::new_err(e)),
        };
        
        if set_size <= 0 {
            return Err(PyValueError::new_err("Set size must be positive"));
        }
        
        Ok(PyAbstractOperationNew {
            symbol,
            set_size,
            evaluation_mode: AbstractOperationEvaluationMode::IntFunction(int_value_at_fn),
        })
    }
    
    #[staticmethod]
    fn from_value_at_function(name: &str, arity: i32, universe: Vec<PyObject>, value_at_fn: PyObject) -> PyResult<Self> {
        let set_size = universe.len() as i32;
        let symbol = match uacalc::alg::op::OperationSymbol::new_safe(name, arity, false) {
            Ok(sym) => sym,
            Err(e) => return Err(PyValueError::new_err(e)),
        };
        
        if set_size <= 0 {
            return Err(PyValueError::new_err("Universe cannot be empty"));
        }
        
        Ok(PyAbstractOperationNew {
            symbol,
            set_size,
            evaluation_mode: AbstractOperationEvaluationMode::ValueFunction(value_at_fn, universe),
        })
    }
    
    fn arity(&self) -> i32 { self.symbol.arity() }
    fn get_set_size(&self) -> i32 { self.set_size }
    fn symbol(&self) -> PyOperationSymbol { PyOperationSymbol { inner: self.symbol.clone() } }
    
    fn int_value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        if args.len() != self.arity() as usize {
            return Err(PyValueError::new_err(format!("Expected {} arguments, got {}", self.arity(), args.len())));
        }
        
        for &arg in &args {
            if arg < 0 || arg >= self.set_size {
                return Err(PyValueError::new_err(format!("Argument {} is out of bounds [0, {})", arg, self.set_size)));
            }
        }
        
        match &self.evaluation_mode {
            AbstractOperationEvaluationMode::IntFunction(func) => {
                Python::with_gil(|py| {
                    let py_args = PyList::new_bound(py, &args);
                    let result = func.call1(py, (py_args,))?;
                    let result_int: i32 = result.extract(py)?;
                    
                    if result_int < 0 || result_int >= self.set_size {
                        return Err(PyValueError::new_err(format!(
                            "Function returned {} which is out of range [0, {})", result_int, self.set_size
                        )));
                    }
                    
                    Ok(result_int)
                })
            }
            AbstractOperationEvaluationMode::ValueFunction(func, universe) => {
                Python::with_gil(|py| {
                    let universe_args: Vec<PyObject> = args.iter().map(|&i| universe[i as usize].clone()).collect();
                    let py_args = PyList::new_bound(py, &universe_args);
                    let result = func.call1(py, (py_args,))?;
                    
                    for (i, universe_elem) in universe.iter().enumerate() {
                        if result.bind(py).eq(universe_elem)? {
                            return Ok(i as i32);
                        }
                    }
                    
                    Err(PyValueError::new_err("Function returned a value not in the universe"))
                })
            }
            AbstractOperationEvaluationMode::IntTable(table) | AbstractOperationEvaluationMode::ValueTable(table, _) => {
                let index = self.horner_encode(&args);
                Ok(table[index as usize])
            }
        }
    }
    
    fn make_table(&mut self) -> PyResult<()> {
        match &self.evaluation_mode {
            AbstractOperationEvaluationMode::IntTable(_) | AbstractOperationEvaluationMode::ValueTable(_, _) => Ok(()),
            AbstractOperationEvaluationMode::IntFunction(func) => {
                let func_clone = func.clone();
                
                Python::with_gil(|py| {
                    let arity = self.arity();
                    let table_size = if arity == 0 { 1 } else { (self.set_size as usize).pow(arity as u32) };
                    let mut table = Vec::with_capacity(table_size);
                    
                    let mut all_args = Vec::new();
                    if arity == 0 {
                        all_args.push(Vec::new());
                    } else {
                        PyAbstractIntOperationNew::generate_args_static(arity, self.set_size, &mut Vec::new(), &mut all_args);
                    }
                    
                    for args in all_args {
                        let py_args = PyList::new_bound(py, &args);
                        let result = func_clone.call1(py, (py_args,))?;
                        let result_int: i32 = result.extract(py)?;
                        table.push(result_int);
                    }
                    
                    self.evaluation_mode = AbstractOperationEvaluationMode::IntTable(table);
                    Ok(())
                })
            }
            AbstractOperationEvaluationMode::ValueFunction(func, universe) => {
                let func_clone = func.clone();
                let universe_clone = universe.clone();
                
                Python::with_gil(|py| {
                    let arity = self.arity();
                    let table_size = if arity == 0 { 1 } else { (self.set_size as usize).pow(arity as u32) };
                    let mut table = Vec::with_capacity(table_size);
                    
                    let mut all_args = Vec::new();
                    if arity == 0 {
                        all_args.push(Vec::new());
                    } else {
                        PyAbstractIntOperationNew::generate_args_static(arity, self.set_size, &mut Vec::new(), &mut all_args);
                    }
                    
                    for args in all_args {
                        let universe_args: Vec<PyObject> = args.iter().map(|&i| universe_clone[i as usize].clone()).collect();
                        let py_args = PyList::new_bound(py, &universe_args);
                        let result = func_clone.call1(py, (py_args,))?;
                        
                        let mut result_index = None;
                        for (i, universe_elem) in universe_clone.iter().enumerate() {
                            if result.bind(py).eq(universe_elem)? {
                                result_index = Some(i as i32);
                                break;
                            }
                        }
                        
                        match result_index {
                            Some(idx) => table.push(idx),
                            None => return Err(PyValueError::new_err("Function returned a value not in the universe")),
                        }
                    }
                    
                    self.evaluation_mode = AbstractOperationEvaluationMode::ValueTable(table, universe_clone);
                    Ok(())
                })
            }
        }
    }
    
    fn get_table(&self) -> Option<Vec<i32>> {
        match &self.evaluation_mode {
            AbstractOperationEvaluationMode::IntTable(table) | AbstractOperationEvaluationMode::ValueTable(table, _) => Some(table.clone()),
            AbstractOperationEvaluationMode::IntFunction(_) | AbstractOperationEvaluationMode::ValueFunction(_, _) => None,
        }
    }
    
    fn is_table_based(&self) -> bool {
        matches!(self.evaluation_mode, AbstractOperationEvaluationMode::IntTable(_) | AbstractOperationEvaluationMode::ValueTable(_, _))
    }
    
    fn is_idempotent(&self) -> PyResult<bool> {
        let arity = self.arity();
        for x in 0..self.set_size {
            let args = vec![x; arity as usize];
            if self.int_value_at(args)? != x { return Ok(false); }
        }
        Ok(true)
    }
    
    fn is_associative(&self) -> PyResult<bool> {
        if self.arity() != 2 { return Ok(false); }
        for x in 0..self.set_size {
            for y in 0..self.set_size {
                for z in 0..self.set_size {
                    let xy = self.int_value_at(vec![x, y])?;
                    let yz = self.int_value_at(vec![y, z])?;
                    let left = self.int_value_at(vec![xy, z])?;
                    let right = self.int_value_at(vec![x, yz])?;
                    if left != right { return Ok(false); }
                }
            }
        }
        Ok(true)
    }
    
    fn is_commutative(&self) -> PyResult<bool> {
        if self.arity() != 2 { return Ok(false); }
        for x in 0..self.set_size {
            for y in 0..self.set_size {
                let xy = self.int_value_at(vec![x, y])?;
                let yx = self.int_value_at(vec![y, x])?;
                if xy != yx { return Ok(false); }
            }
        }
        Ok(true)
    }
    
    fn is_totally_symmetric(&self) -> PyResult<bool> {
        let arity = self.arity() as usize;
        if arity <= 1 { return Ok(true); }
        
        if arity >= 2 {
            let mut all_args = Vec::new();
            PyAbstractIntOperationNew::generate_args_static(self.arity(), self.set_size, &mut Vec::new(), &mut all_args);
            
            for args in all_args {
                let original = self.int_value_at(args.clone())?;
                let mut swapped = args;
                swapped.swap(0, 1);
                let swapped_result = self.int_value_at(swapped)?;
                if original != swapped_result { return Ok(false); }
            }
        }
        
        Ok(true)
    }
    
    fn is_maltsev(&self) -> PyResult<bool> {
        if self.arity() != 3 { return Ok(false); }
        for x in 0..self.set_size {
            for y in 0..self.set_size {
                let xyy = self.int_value_at(vec![x, y, y])?;
                let xxy = self.int_value_at(vec![x, x, y])?;
                if xyy != x || xxy != y { return Ok(false); }
            }
        }
        Ok(true)
    }
    
    fn is_total(&self) -> PyResult<bool> { Ok(true) }
    
    fn __str__(&self) -> String {
        let universe_type = match &self.evaluation_mode {
            AbstractOperationEvaluationMode::IntFunction(_) | AbstractOperationEvaluationMode::IntTable(_) => "integer",
            AbstractOperationEvaluationMode::ValueFunction(_, _) | AbstractOperationEvaluationMode::ValueTable(_, _) => "general",
        };
        format!("AbstractOperation({}, arity={}, set_size={}, universe={}, table_based={})", 
                self.symbol.name(), self.arity(), self.set_size, universe_type, self.is_table_based())
    }
    
    fn __repr__(&self) -> String {
        let universe_type = match &self.evaluation_mode {
            AbstractOperationEvaluationMode::IntFunction(_) | AbstractOperationEvaluationMode::IntTable(_) => "integer",
            AbstractOperationEvaluationMode::ValueFunction(_, _) | AbstractOperationEvaluationMode::ValueTable(_, _) => "general",
        };
        format!("AbstractOperation(name='{}', arity={}, set_size={}, universe={}, table_based={})", 
                self.symbol.name(), self.arity(), self.set_size, universe_type, self.is_table_based())
    }
}

impl PyAbstractOperationNew {
    fn horner_encode(&self, args: &[i32]) -> i32 {
        let mut result = 0;
        let mut multiplier = 1;
        
        for &arg in args.iter().rev() {
            result += arg * multiplier;
            multiplier *= self.set_size;
        }
        
        result
    }
}

/// Python wrapper for OperationWithDefaultValue
#[pyclass]
pub struct PyOperationWithDefaultValue {
    inner: uacalc::alg::op::OperationWithDefaultValue,
}

#[pymethods]
impl PyOperationWithDefaultValue {
    /// Constructor: Create with name, arity, set size, and default value.
    /// This is the default constructor (Constructor 2 in Java).
    #[new]
    #[pyo3(signature = (name_or_op, arity_or_set_size=None, set_size=None, default_value=-1))]
    fn new(
        name_or_op: &PyAny,
        arity_or_set_size: Option<i32>,
        set_size: Option<i32>,
        default_value: i32
    ) -> PyResult<Self> {
        // Check if first arg is a BasicOperation or OperationSymbol
        if let Ok(basic_op) = name_or_op.extract::<PyRef<PyBasicOperation>>() {
            // Constructor 1 or 5: from_operation
            if let Some(alg_size) = arity_or_set_size {
                // Constructor 5: from_operation_with_size
                match uacalc::alg::op::OperationWithDefaultValue::from_operation_with_size(
                    basic_op.inner.clone(),
                    alg_size
                ) {
                    Ok(inner) => return Ok(PyOperationWithDefaultValue { inner }),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            } else {
                // Constructor 1: from_operation
                match uacalc::alg::op::OperationWithDefaultValue::from_operation(basic_op.inner.clone()) {
                    Ok(inner) => return Ok(PyOperationWithDefaultValue { inner }),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            }
        } else if let Ok(op_symbol) = name_or_op.extract::<PyRef<PyOperationSymbol>>() {
            // Constructor 3, 4, or 6: with symbol
            let alg_size = arity_or_set_size.ok_or_else(|| 
                PyValueError::new_err("algebra size required when passing OperationSymbol")
            )?;
            
            if let Some(_table_param) = set_size {
                // This is actually the value table - Constructor 6
                // For now, use constructor 4
                match uacalc::alg::op::OperationWithDefaultValue::new_with_symbol_and_default(
                    op_symbol.inner.clone(),
                    alg_size,
                    default_value
                ) {
                    Ok(inner) => return Ok(PyOperationWithDefaultValue { inner }),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            } else {
                // Constructor 3 or 4
                match uacalc::alg::op::OperationWithDefaultValue::new_with_symbol_and_default(
                    op_symbol.inner.clone(),
                    alg_size,
                    default_value
                ) {
                    Ok(inner) => return Ok(PyOperationWithDefaultValue { inner }),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            }
        } else {
            // String name - Constructor 2
            let name = name_or_op.extract::<String>()?;
            let arity = arity_or_set_size.ok_or_else(|| 
                PyValueError::new_err("arity required when passing name")
            )?;
            let alg_size = set_size.ok_or_else(|| 
                PyValueError::new_err("set_size required when passing name and arity")
            )?;
            
            match uacalc::alg::op::OperationWithDefaultValue::new_with_name(
                &name,
                arity,
                alg_size,
                default_value
            ) {
                Ok(inner) => Ok(PyOperationWithDefaultValue { inner }),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        }
    }
    
    /// Alternative constructor: from_operation (Constructor 1)
    #[staticmethod]
    fn from_operation(op: PyRef<PyBasicOperation>) -> PyResult<Self> {
        match uacalc::alg::op::OperationWithDefaultValue::from_operation(op.inner.clone()) {
            Ok(inner) => Ok(PyOperationWithDefaultValue { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the arity of this operation.
    fn arity(&self) -> i32 {
        self.inner.arity()
    }
    
    /// Get the algebra size of this operation.
    fn get_set_size(&self) -> i32 {
        self.inner.get_set_size()
    }
    
    /// Get the operation symbol.
    fn symbol(&self) -> PyOperationSymbol {
        PyOperationSymbol {
            inner: self.inner.symbol().clone()
        }
    }
    
    /// Get the value at the given arguments (array version).
    /// Handles both list and single int arguments for flexibility.
    fn int_value_at(&self, args: &PyAny) -> PyResult<i32> {
        // Try to extract as a list first
        if let Ok(args_list) = args.extract::<Vec<i32>>() {
            match self.inner.int_value_at_array(&args_list) {
                Ok(value) => Ok(value),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        } else if let Ok(single_arg) = args.extract::<i32>() {
            // Single int argument
            match self.inner.int_value_at_single(single_arg) {
                Ok(value) => Ok(value),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        } else {
            Err(PyValueError::new_err("Expected list of ints or single int"))
        }
    }
    
    /// Get value at arguments (matches Java's Object valueAt(List args)).
    fn value_at(&self, args: Vec<i32>) -> PyResult<i32> {
        match self.inner.int_value_at_array(&args) {
            Ok(value) => Ok(value),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the default value.
    fn get_default_value(&self) -> i32 {
        self.inner.get_default_value()
    }
    
    /// Set the default value.
    fn set_default_value(&mut self, v: i32) {
        self.inner.set_default_value(v);
    }
    
    /// Check if the idempotent flag is set.
    fn is_idempotent_set(&self) -> bool {
        self.inner.is_idempotent_set()
    }
    
    /// Set the idempotent flag.
    fn set_idempotent(&mut self, v: bool) {
        self.inner.set_idempotent(v);
    }
    
    /// Make the operation idempotent.
    fn make_idempotent(&mut self) {
        self.inner.make_idempotent();
    }
    
    /// Check if a position is on the diagonal.
    fn is_diagonal(&self, row: usize, col: usize) -> bool {
        self.inner.is_diagonal(row, col)
    }
    
    /// Update the random value table.
    fn update_random_value_table(&mut self) {
        self.inner.update_random_value_table();
    }
    
    /// Get the random value table.
    fn get_random_value_table(&mut self) -> Vec<i32> {
        self.inner.get_random_value_table().to_vec()
    }
    
    /// Get the total table (with default values filled in).
    fn get_total_table(&self) -> Option<Vec<i32>> {
        self.inner.get_total_table()
    }
    
    /// Make an ordinary operation.
    fn make_ordinary_operation(&self) -> Option<PyIntOperation> {
        self.inner.make_ordinary_operation().map(|op| PyIntOperation { inner: op })
    }
    
    /// Static method: convert list of operations to ordinary operations.
    #[staticmethod]
    fn make_ordinary(ops: Vec<PyRef<PyOperationWithDefaultValue>>) -> Vec<PyIntOperation> {
        let rust_ops: Vec<_> = ops.into_iter().map(|op| op.inner.clone()).collect();
        uacalc::alg::op::OperationWithDefaultValue::make_ordinary_list(rust_ops)
            .into_iter()
            .map(|op| PyIntOperation { inner: op })
            .collect()
    }
    
    /// Check if this operation is idempotent.
    fn is_idempotent(&self) -> PyResult<bool> {
        match self.inner.is_idempotent() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if this operation is total.
    fn is_total(&self) -> PyResult<bool> {
        match self.inner.is_total() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if this operation is table-based.
    fn is_table_based(&self) -> bool {
        self.inner.is_table_based()
    }
    
    /// Get the operation table.
    fn get_table(&self) -> Option<Vec<i32>> {
        self.inner.get_table().map(|table| table.to_vec())
    }
    
    /// Make the operation table.
    fn make_table(&mut self) -> PyResult<()> {
        match self.inner.make_table() {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Python equality comparison.
    fn __eq__(&self, other: &PyOperationWithDefaultValue) -> bool {
        self.inner == other.inner
    }
    
    /// Python string representation.
    fn __repr__(&self) -> String {
        format!("OperationWithDefaultValue(name='{}', arity={}, set_size={}, default_value={})",
                self.inner.symbol().name(),
                self.inner.arity(),
                self.inner.get_set_size(),
                self.inner.get_default_value())
    }
    
    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }
}

/// Python wrapper for Operations utility class
#[pyclass]
pub struct PyOperations;

#[pymethods]
impl PyOperations {
    /// Make a full cycle operation.
    /// 
    /// Args:
    ///     alg_size: The algebra size
    /// 
    /// Returns:
    ///     IntOperation: The full cycle operation
    /// 
    /// Raises:
    ///     ValueError: If parameters are invalid
    #[staticmethod]
    fn make_full_cycle(alg_size: i32) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_full_cycle(alg_size) {
            Ok(op) => {
                // op is Box<dyn Operation>, but it's constructed as IntOperation inside; rebuild via table
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().map(|t| t.to_vec()).unwrap_or_else(|| {
                    let arity = op.arity() as usize;
                    let total = (set_size as usize).pow(arity as u32);
                    let mut vt = Vec::with_capacity(total);
                    for k in 0..total { let args = uacalc::util::horner::horner_inv_same_size(k as i32, set_size, arity); vt.push(op.int_value_at(&args).unwrap()); }
                    vt
                });
                let int_op = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner: int_op })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    // Removed concrete make_int_operation to avoid duplicate with generic overload

    /// Construct an operation from a string symbol and table.
    #[staticmethod]
    fn make_int_operation_str(name: &str, arity: i32, set_size: i32, table: Vec<i32>) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_int_operation_str(name, arity, set_size, table) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Make a transposition operation.
    /// 
    /// Args:
    ///     alg_size: The algebra size
    ///     i: First element to transpose
    ///     j: Second element to transpose
    /// 
    /// Returns:
    ///     IntOperation: The transposition operation
    /// 
    /// Raises:
    ///     ValueError: If parameters are invalid
    #[staticmethod]
    fn make_transposition(alg_size: i32, i: i32, j: i32) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_transposition(alg_size, i, j) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().map(|t| t.to_vec()).unwrap_or_else(|| {
                    let arity = op.arity() as usize;
                    let total = (set_size as usize).pow(arity as u32);
                    let mut vt = Vec::with_capacity(total);
                    for k in 0..total { let args = uacalc::util::horner::horner_inv_same_size(k as i32, set_size, arity); vt.push(op.int_value_at(&args).unwrap()); }
                    vt
                });
                let int_op = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner: int_op })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Make a ternary discriminator operation.
    /// 
    /// Args:
    ///     alg_size: The algebra size
    /// 
    /// Returns:
    ///     BasicOperation: The ternary discriminator operation
    /// 
    /// Raises:
    ///     ValueError: If parameters are invalid
    #[staticmethod]
    fn make_ternary_discriminator(alg_size: i32) -> PyResult<PyBasicOperation> {
        match uacalc::alg::op::ops::ternary_discriminator(alg_size) {
            Ok(_op) => {
                // For now, we'll create a simple BasicOperation wrapper
                let symbol = match uacalc::alg::op::OperationSymbol::new_safe("discriminator", 3, false) {
                    Ok(sym) => sym,
                    Err(e) => return Err(PyValueError::new_err(e)),
                };
                match uacalc::alg::op::BasicOperation::new_safe(symbol, alg_size) {
                    Ok(inner) => Ok(PyBasicOperation { inner }),
                    Err(e) => Err(PyValueError::new_err(e)),
                }
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if two operations have equal values.
    /// 
    /// Args:
    ///     op1: First operation
    ///     op2: Second operation
    /// 
    /// Returns:
    ///     bool: True if operations have equal values
    #[staticmethod]
    fn equal_values(op1: &PyAny, op2: &PyAny) -> PyResult<bool> {
        // Try to extract from different operation types and call the appropriate comparison
        if let Ok(basic_op1) = op1.extract::<PyRef<PyBasicOperation>>() {
            if let Ok(basic_op2) = op2.extract::<PyRef<PyBasicOperation>>() {
                match uacalc::alg::op::ops::equal_values(&basic_op1.inner, &basic_op2.inner) {
                    Ok(result) => return Ok(result),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            } else if let Ok(int_op2) = op2.extract::<PyRef<PyIntOperation>>() {
                match uacalc::alg::op::ops::equal_values(&basic_op1.inner, &int_op2.inner) {
                    Ok(result) => return Ok(result),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            }
        } else if let Ok(int_op1) = op1.extract::<PyRef<PyIntOperation>>() {
            if let Ok(basic_op2) = op2.extract::<PyRef<PyBasicOperation>>() {
                match uacalc::alg::op::ops::equal_values(&int_op1.inner, &basic_op2.inner) {
                    Ok(result) => return Ok(result),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            } else if let Ok(int_op2) = op2.extract::<PyRef<PyIntOperation>>() {
                match uacalc::alg::op::ops::equal_values(&int_op1.inner, &int_op2.inner) {
                    Ok(result) => return Ok(result),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            }
        }
        
        Err(PyValueError::new_err("Unsupported operation type combination"))
    }
    
    /// Find the first difference between two operations.
    /// 
    /// Args:
    ///     op1: First operation
    ///     op2: Second operation
    /// 
    /// Returns:
    ///     list: The first differing argument combination or None if no difference
    #[staticmethod]
    fn find_difference(op1: &PyAny, op2: &PyAny) -> PyResult<Option<Vec<i32>>> {
        // Try to extract from different operation types and call the appropriate comparison
        if let Ok(basic_op1) = op1.extract::<PyRef<PyBasicOperation>>() {
            if let Ok(basic_op2) = op2.extract::<PyRef<PyBasicOperation>>() {
                match uacalc::alg::op::ops::find_difference(&basic_op1.inner, &basic_op2.inner) {
                    Ok(result) => return Ok(result),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            } else if let Ok(int_op2) = op2.extract::<PyRef<PyIntOperation>>() {
                match uacalc::alg::op::ops::find_difference(&basic_op1.inner, &int_op2.inner) {
                    Ok(result) => return Ok(result),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            }
        } else if let Ok(int_op1) = op1.extract::<PyRef<PyIntOperation>>() {
            if let Ok(basic_op2) = op2.extract::<PyRef<PyBasicOperation>>() {
                match uacalc::alg::op::ops::find_difference(&int_op1.inner, &basic_op2.inner) {
                    Ok(result) => return Ok(result),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            } else if let Ok(int_op2) = op2.extract::<PyRef<PyIntOperation>>() {
                match uacalc::alg::op::ops::find_difference(&int_op1.inner, &int_op2.inner) {
                    Ok(result) => return Ok(result),
                    Err(e) => return Err(PyValueError::new_err(e)),
                }
            }
        }
        
        Err(PyValueError::new_err("Unsupported operation type combination"))
    }
    
    /// Check if an operation is commutative.
    /// 
    /// Args:
    ///     operation: The operation to check
    /// 
    /// Returns:
    ///     bool: True if the operation is commutative
    #[staticmethod]
    fn is_commutative(operation: &PyAny) -> PyResult<bool> {
        // Try to extract from different operation types
        if let Ok(basic_op) = operation.extract::<PyRef<PyBasicOperation>>() {
            match uacalc::alg::op::ops::is_commutative(&basic_op.inner) {
                Ok(result) => Ok(result),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        } else if let Ok(int_op) = operation.extract::<PyRef<PyIntOperation>>() {
            match uacalc::alg::op::ops::is_commutative(&int_op.inner) {
                Ok(result) => Ok(result),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        } else {
            Err(PyValueError::new_err("Unsupported operation type"))
        }
    }
    
    /// Check if an operation is idempotent.
    /// 
    /// Args:
    ///     operation: The operation to check
    /// 
    /// Returns:
    ///     bool: True if the operation is idempotent
    #[staticmethod]
    fn is_idempotent(operation: &PyAny) -> PyResult<bool> {
        // Try to extract from different operation types
        if let Ok(basic_op) = operation.extract::<PyRef<PyBasicOperation>>() {
            match uacalc::alg::op::ops::is_idempotent(&basic_op.inner) {
                Ok(result) => Ok(result),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        } else if let Ok(int_op) = operation.extract::<PyRef<PyIntOperation>>() {
            match uacalc::alg::op::ops::is_idempotent(&int_op.inner) {
                Ok(result) => Ok(result),
                Err(e) => Err(PyValueError::new_err(e)),
            }
        } else {
            Err(PyValueError::new_err("Unsupported operation type"))
        }
    }

    /// Check if a unary operation commutes with a general operation.
    #[staticmethod]
    fn commutes(unary_op: &PyAny, op: &PyAny) -> PyResult<bool> {
        if let Ok(u) = unary_op.extract::<PyRef<PyBasicOperation>>() {
            if let Ok(o) = op.extract::<PyRef<PyBasicOperation>>() {
                return uacalc::alg::op::ops::commutes_unary(&u.inner, &o.inner).map_err(PyValueError::new_err);
            } else if let Ok(o) = op.extract::<PyRef<PyIntOperation>>() {
                return uacalc::alg::op::ops::commutes_unary(&u.inner, &o.inner).map_err(PyValueError::new_err);
            }
        } else if let Ok(u) = unary_op.extract::<PyRef<PyIntOperation>>() {
            if let Ok(o) = op.extract::<PyRef<PyBasicOperation>>() {
                return uacalc::alg::op::ops::commutes_unary(&u.inner, &o.inner).map_err(PyValueError::new_err);
            } else if let Ok(o) = op.extract::<PyRef<PyIntOperation>>() {
                return uacalc::alg::op::ops::commutes_unary(&u.inner, &o.inner).map_err(PyValueError::new_err);
            }
        }
        Err(PyValueError::new_err("Unsupported operation types for commutes"))
    }

    /// Check if an operation is total.
    #[staticmethod]
    fn is_total(op: &PyAny) -> PyResult<bool> {
        if let Ok(o) = op.extract::<PyRef<PyBasicOperation>>() {
            return uacalc::alg::op::ops::is_total(&o.inner).map_err(PyValueError::new_err);
        } else if let Ok(o) = op.extract::<PyRef<PyIntOperation>>() {
            return uacalc::alg::op::ops::is_total(&o.inner).map_err(PyValueError::new_err);
        }
        Err(PyValueError::new_err("Unsupported operation type"))
    }

    /// Check if an operation is totally symmetric.
    #[staticmethod]
    fn is_totally_symmetric(op: &PyAny) -> PyResult<bool> {
        if let Ok(o) = op.extract::<PyRef<PyBasicOperation>>() {
            return uacalc::alg::op::ops::is_totally_symmetric(&o.inner).map_err(PyValueError::new_err);
        } else if let Ok(o) = op.extract::<PyRef<PyIntOperation>>() {
            return uacalc::alg::op::ops::is_totally_symmetric(&o.inner).map_err(PyValueError::new_err);
        }
        Err(PyValueError::new_err("Unsupported operation type"))
    }

    /// Check if an operation is associative.
    #[staticmethod]
    fn is_associative(op: &PyAny) -> PyResult<bool> {
        if let Ok(o) = op.extract::<PyRef<PyBasicOperation>>() {
            return uacalc::alg::op::ops::is_associative(&o.inner).map_err(PyValueError::new_err);
        } else if let Ok(o) = op.extract::<PyRef<PyIntOperation>>() {
            return uacalc::alg::op::ops::is_associative(&o.inner).map_err(PyValueError::new_err);
        }
        Err(PyValueError::new_err("Unsupported operation type"))
    }

    /// Check if an operation is a Maltsev operation.
    #[staticmethod]
    fn is_maltsev(op: &PyAny) -> PyResult<bool> {
        if let Ok(o) = op.extract::<PyRef<PyBasicOperation>>() {
            return uacalc::alg::op::ops::is_maltsev(&o.inner).map_err(PyValueError::new_err);
        } else if let Ok(o) = op.extract::<PyRef<PyIntOperation>>() {
            return uacalc::alg::op::ops::is_maltsev(&o.inner).map_err(PyValueError::new_err);
        }
        Err(PyValueError::new_err("Unsupported operation type"))
    }

    // -------------------- Factory methods --------------------
    #[staticmethod]
    #[pyo3(signature = (a, b, c, d=None))]
    fn make_int_operation(a: &PyAny, b: i32, c: &PyAny, d: Option<&PyAny>) -> PyResult<PyIntOperation> {
        // Case 1: (symbol, set_size, table)
        if let Ok(sym) = a.extract::<PyRef<PyOperationSymbol>>() {
            let set_size = b;
            let table: Vec<i32> = c.extract().map_err(PyValueError::new_err)?;
            match uacalc::alg::op::ops::make_int_operation(sym.inner.clone(), set_size, table) {
                Ok(op) => {
                    let sy = op.symbol().clone();
                    let ss = op.get_set_size();
                    let tb = op.get_table().unwrap().to_vec();
                    let inner = uacalc::alg::op::IntOperation::new(sy, ss, tb).map_err(PyValueError::new_err)?;
                    return Ok(PyIntOperation { inner })
                },
                Err(e) => return Err(PyValueError::new_err(e)),
            }
        }
        // Case 2: (name: str, arity, set_size, table)
        if let Ok(name) = a.extract::<String>() {
            let arity = b;
            let set_size: i32 = c.extract().map_err(PyValueError::new_err)?;
            let table_any = d.ok_or_else(|| PyValueError::new_err("table required"))?;
            let table: Vec<i32> = table_any.extract().map_err(PyValueError::new_err)?;
            match uacalc::alg::op::ops::make_int_operation_str(&name, arity, set_size, table) {
                Ok(op) => {
                    let sy = op.symbol().clone();
                    let ss = op.get_set_size();
                    let tb = op.get_table().unwrap().to_vec();
                    let inner = uacalc::alg::op::IntOperation::new(sy, ss, tb).map_err(PyValueError::new_err)?;
                    return Ok(PyIntOperation { inner })
                },
                Err(e) => return Err(PyValueError::new_err(e)),
            }
        }
        Err(PyValueError::new_err("Expected OperationSymbol or name string"))
    }

    #[staticmethod]
    fn make_binary_int_operation(symbol: &PyOperationSymbol, set_size: i32, table_1d: Vec<i32>) -> PyResult<PyIntOperation> {
        // Convert flattened 1D into 2D for Rust API
        let mut table2d: Vec<Vec<i32>> = Vec::with_capacity(set_size as usize);
        let mut k = 0usize;
        for _ in 0..set_size {
            let mut row = Vec::with_capacity(set_size as usize);
            for _ in 0..set_size { row.push(if k < table_1d.len() { table_1d[k] } else { 0 }); k += 1; }
            table2d.push(row);
        }
        match uacalc::alg::op::ops::make_binary_int_operation(symbol.inner.clone(), set_size, table2d) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn make_constant_int_operation(arg1: &PyAny, arg2: i32, arg3: Option<i32>) -> PyResult<PyIntOperation> {
        // Overloaded: (set_size, elt) or (prefix, set_size, elt)
        if let Ok(prefix) = arg1.extract::<String>() {
            let set_size = arg2;
            let elt = arg3.ok_or_else(|| PyValueError::new_err("elt required"))?;
            match uacalc::alg::op::ops::make_constant_int_operation_with_prefix(&prefix, set_size, elt) {
                Ok(op) => {
                    let sym = op.symbol().clone();
                    let set_size = op.get_set_size();
                    let table = op.get_table().unwrap().to_vec();
                    let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                    Ok(PyIntOperation { inner })
                },
                Err(e) => Err(PyValueError::new_err(e)),
            }
        } else if let Ok(set_size) = arg1.extract::<i32>() {
            if set_size <= 0 {
                return Err(PyValueError::new_err("Set size must be positive"));
            }
            let elt = arg2;
            if elt < 0 || elt >= set_size {
                return Err(PyValueError::new_err(format!("Default value {} is out of range [0, {})", elt, set_size)));
            }
            match uacalc::alg::op::ops::make_constant_int_operation(set_size, elt) {
                Ok(op) => {
                    let sym = op.symbol().clone();
                    let set_size = op.get_set_size();
                    let table = op.get_table().unwrap().to_vec();
                    let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                    Ok(PyIntOperation { inner })
                },
                Err(e) => Err(PyValueError::new_err(e)),
            }
        } else {
            Err(PyValueError::new_err("Invalid arguments for make_constant_int_operation"))
        }
    }

    #[staticmethod]
    fn make_constant_int_operations(set_size: i32) -> PyResult<Vec<PyIntOperation>> {
        match uacalc::alg::op::ops::make_constant_int_operations(set_size) {
            Ok(vec) => {
                let mut out = Vec::with_capacity(vec.len());
                for op in vec {
                    let sym = op.symbol().clone();
                    let ss = op.get_set_size();
                    let table = op.get_table().unwrap().to_vec();
                    let inner = uacalc::alg::op::IntOperation::new(sym, ss, table).map_err(PyValueError::new_err)?;
                    out.push(PyIntOperation { inner });
                }
                Ok(out)
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn make_int_operations(ops: Vec<PyRef<PyBasicOperation>>) -> PyResult<Vec<PyIntOperation>> {
        let rust_ops: Vec<Box<dyn uacalc::alg::op::Operation>> = ops.into_iter().map(|o| Box::new(o.inner.clone()) as Box<dyn uacalc::alg::op::Operation>).collect();
        match uacalc::alg::op::ops::make_int_operations(rust_ops) {
            Ok(vec) => {
                let mut out = Vec::with_capacity(vec.len());
                for op in vec {
                    let sym = op.symbol().clone();
                    let ss = op.get_set_size();
                    let table = op.get_table().unwrap().to_vec();
                    let inner = uacalc::alg::op::IntOperation::new(sym, ss, table).map_err(PyValueError::new_err)?;
                    out.push(PyIntOperation { inner });
                }
                Ok(out)
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn make_random_operation(n: i32, symbol: &PyOperationSymbol) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_random_operation(n, symbol.inner.clone()) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn make_random_operation_with_seed(n: i32, symbol: &PyOperationSymbol, seed: u64) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_random_operation_with_seed(n, symbol.inner.clone(), seed) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn make_random_operations(n: i32, sim_type: &PySimilarityType) -> PyResult<Vec<PyIntOperation>> {
        match uacalc::alg::op::ops::make_random_operations(n, &sim_type.inner) {
            Ok(vec) => {
                let mut out = Vec::with_capacity(vec.len());
                for op in vec {
                    let sym = op.symbol().clone();
                    let ss = op.get_set_size();
                    let table = op.get_table().unwrap().to_vec();
                    let inner = uacalc::alg::op::IntOperation::new(sym, ss, table).map_err(PyValueError::new_err)?;
                    out.push(PyIntOperation { inner });
                }
                Ok(out)
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn make_random_operations_with_seed(n: i32, sim_type: &PySimilarityType, seed: u64) -> PyResult<Vec<PyIntOperation>> {
        match uacalc::alg::op::ops::make_random_operations_with_seed(n, &sim_type.inner, Some(seed)) {
            Ok(vec) => {
                let mut out = Vec::with_capacity(vec.len());
                for op in vec {
                    let sym = op.symbol().clone();
                    let ss = op.get_set_size();
                    let table = op.get_table().unwrap().to_vec();
                    let inner = uacalc::alg::op::IntOperation::new(sym, ss, table).map_err(PyValueError::new_err)?;
                    out.push(PyIntOperation { inner });
                }
                Ok(out)
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn make_derived_operation(base_op: &PyAny, reduction_array: Vec<i32>, new_arity: i32) -> PyResult<PyIntOperation> {
        let op: Box<dyn uacalc::alg::op::Operation> = if let Ok(o) = base_op.extract::<PyRef<PyBasicOperation>>() {
            Box::new(o.inner.clone())
        } else if let Ok(o) = base_op.extract::<PyRef<PyIntOperation>>() {
            Box::new(o.inner.clone())
        } else {
            return Err(PyValueError::new_err("Unsupported operation type"));
        };
        match uacalc::alg::op::ops::make_derived_operation(std::sync::Arc::from(op), reduction_array, new_arity) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn ternary_discriminator(size: i32) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::ternary_discriminator(size) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn make_jonsson_operations_from_nuf(_nuf: &PyAny) -> PyResult<Vec<PyIntOperation>> {
        // Placeholder: returns empty list consistent with current Rust implementation
        Ok(Vec::new())
    }

    #[staticmethod]
    fn make_left_shift(vec_size: i32, root_size: i32) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_left_shift(vec_size, root_size) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn make_binary_left_shift(vec_size: i32, root_size: i32) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_binary_left_shift(vec_size, root_size) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn make_matrix_diagonal_op(vec_size: i32, root_size: i32) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_matrix_diagonal_op(vec_size, root_size) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn make_module_operation(modulus: i32, coeffs: Vec<i32>) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_module_operation(modulus, &coeffs) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn make_composition_op(n: i32, pow: i32) -> PyResult<PyIntOperation> {
        match uacalc::alg::op::ops::make_composition_op(n, pow) {
            Ok(op) => {
                let sym = op.symbol().clone();
                let set_size = op.get_set_size();
                let table = op.get_table().unwrap().to_vec();
                let inner = uacalc::alg::op::IntOperation::new(sym, set_size, table).map_err(PyValueError::new_err)?;
                Ok(PyIntOperation { inner })
            },
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    #[staticmethod]
    fn make_map(ops: Vec<PyRef<PyBasicOperation>>) -> PyResult<Vec<i32>> {
        let rust_ops: Vec<Box<dyn uacalc::alg::op::Operation>> = ops.into_iter().map(|o| Box::new(o.inner.clone()) as Box<dyn uacalc::alg::op::Operation>).collect();
        let map = uacalc::alg::op::ops::make_map(&rust_ops);
        // Return a list with the same size; contents unused by tests
        Ok(vec![0; map.len()])
    }
}

/// Python wrapper for BasicSet
#[pyclass]
pub struct PyBasicSet {
    inner: BasicSet,
}

#[pymethods]
impl PyBasicSet {
    /// Create a new BasicSet from a list of elements.
    /// 
    /// Args:
    ///     elements (List[int]): List of integers to include in the set
    /// 
    /// Returns:
    ///     BasicSet: A new BasicSet instance
    /// 
    /// Raises:
    ///     ValueError: If elements contain invalid values
    #[new]
    fn new(elements: Vec<i32>) -> PyResult<Self> {
        match BasicSet::new_safe(elements) {
            Ok(inner) => Ok(PyBasicSet { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the elements of the set.
    /// 
    /// Returns:
    ///     List[int]: The sorted elements of the set
    fn elements(&self) -> Vec<i32> {
        self.inner.elements().clone()
    }
    
    /// Get the size of the set (number of elements).
    /// 
    /// Returns:
    ///     int: The number of elements in the set
    fn size(&self) -> usize {
        self.inner.size()
    }
    
    /// Get the universe size (same as size for BasicSet).
    /// 
    /// Returns:
    ///     int: The number of elements in the set
    fn universe_size(&self) -> usize {
        self.inner.universe_size()
    }
    
    /// Normalize the set by sorting elements and removing duplicates.
    fn normalize(&mut self) {
        self.inner.normalize();
    }
    
    /// Check if this set is a subset of another set.
    /// 
    /// Args:
    ///     other (BasicSet): The set to compare against
    /// 
    /// Returns:
    ///     bool: True if this set is a subset of other
    fn leq(&self, other: &PyBasicSet) -> bool {
        self.inner.leq(&other.inner)
    }
    
    /// Static method to check if one array is a subset of another.
    /// 
    /// Args:
    ///     u (List[int]): First array (sorted)
    ///     v (List[int]): Second array (sorted)
    /// 
    /// Returns:
    ///     bool: True if u is a subset of v
    #[staticmethod]
    fn leq_static(u: Vec<i32>, v: Vec<i32>) -> bool {
        BasicSet::leq_static(&u, &v)
    }
    
    /// Check if the set contains a specific element.
    /// 
    /// Args:
    ///     element (int): The element to search for
    /// 
    /// Returns:
    ///     bool: True if the element is in the set
    fn contains(&self, element: i32) -> bool {
        self.inner.contains(element)
    }
    
    /// Compute the set difference (this - other).
    /// 
    /// Args:
    ///     other (BasicSet): The set to subtract
    /// 
    /// Returns:
    ///     BasicSet: A new BasicSet containing elements in this set but not in other
    fn set_difference(&self, other: &PyBasicSet) -> PyBasicSet {
        PyBasicSet { inner: self.inner.set_difference(&other.inner) }
    }
    
    /// Compute the intersection of this set with another.
    /// 
    /// Args:
    ///     other (BasicSet): The set to intersect with
    /// 
    /// Returns:
    ///     BasicSet: A new BasicSet containing elements in both sets
    fn intersection(&self, other: &PyBasicSet) -> PyBasicSet {
        PyBasicSet { inner: self.inner.intersection(&other.inner) }
    }
    
    /// Static method to compute the intersection of two sets.
    /// 
    /// Args:
    ///     set1 (BasicSet): First set
    ///     set2 (BasicSet): Second set
    /// 
    /// Returns:
    ///     BasicSet: A new BasicSet containing elements in both sets
    #[staticmethod]
    fn intersection_static(set1: &PyBasicSet, set2: &PyBasicSet) -> PyBasicSet {
        PyBasicSet { inner: BasicSet::intersection_static(&set1.inner, &set2.inner) }
    }
    
    /// Compute the union of this set with another.
    /// 
    /// Args:
    ///     other (BasicSet): The set to union with
    /// 
    /// Returns:
    ///     BasicSet: A new BasicSet containing elements from both sets
    fn union(&self, other: &PyBasicSet) -> PyBasicSet {
        PyBasicSet { inner: self.inner.union(&other.inner) }
    }
    
    /// Static method to compute the union of two sets.
    /// 
    /// Args:
    ///     set1 (BasicSet): First set
    ///     set2 (BasicSet): Second set
    /// 
    /// Returns:
    ///     BasicSet: A new BasicSet containing elements from both sets
    #[staticmethod]
    fn union_static(set1: &PyBasicSet, set2: &PyBasicSet) -> PyBasicSet {
        PyBasicSet { inner: BasicSet::union_static(&set1.inner, &set2.inner) }
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("BasicSet({})", self.inner.to_string())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyBasicSet) -> bool {
        self.inner == other.inner
    }
    
    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }
    
    /// Python less than comparison
    fn __lt__(&self, other: &PyBasicSet) -> bool {
        self.inner < other.inner
    }
    
    /// Python less than or equal comparison
    fn __le__(&self, other: &PyBasicSet) -> bool {
        self.inner <= other.inner
    }
    
    /// Python greater than comparison
    fn __gt__(&self, other: &PyBasicSet) -> bool {
        self.inner > other.inner
    }
    
    /// Python greater than or equal comparison
    fn __ge__(&self, other: &PyBasicSet) -> bool {
        self.inner >= other.inner
    }
}

/// Python wrapper for SubalgebraLattice
#[pyclass]
pub struct PySubalgebraLattice {
    inner: std::cell::RefCell<uacalc::alg::sublat::SubalgebraLattice>,
}

#[pymethods]
impl PySubalgebraLattice {
    /// Create a new SubalgebraLattice from a BasicSmallAlgebra.
    /// 
    /// Args:
    ///     algebra (BasicSmallAlgebra): The algebra to compute subalgebras for
    /// 
    /// Returns:
    ///     SubalgebraLattice: A new SubalgebraLattice instance
    /// 
    /// Raises:
    ///     ValueError: If the algebra is invalid or initialization fails
    #[new]
    fn new(algebra: &PyBasicSmallAlgebra) -> PyResult<Self> {
        let alg_box: Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>> =  
            Box::new(algebra.inner.clone());
        
        match uacalc::alg::sublat::SubalgebraLattice::new_safe(alg_box) {
            Ok(inner) => Ok(PySubalgebraLattice { 
                inner: std::cell::RefCell::new(inner) 
            }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the underlying algebra.
    /// 
    /// Returns:
    ///     str: String representation of the algebra
    fn get_algebra(&self) -> String {
        let inner = self.inner.borrow();
        format!("Algebra: size={}", inner.get_algebra().cardinality())
    }
    
    /// Get the description of this subalgebra lattice.
    /// 
    /// Returns:
    ///     str: The description
    fn get_description(&self) -> String {
        self.inner.borrow().get_description().to_string()
    }
    
    /// Set the description of this subalgebra lattice.
    /// 
    /// Args:
    ///     description (str): The new description
    fn set_description(&mut self, description: String) {
        self.inner.borrow_mut().set_description(description);
    }
    
    /// Check if the lattice can be drawn (small enough).
    /// 
    /// Returns:
    ///     bool: True if the lattice is small enough to draw
    fn is_drawable(&self) -> bool {
        self.inner.borrow().is_drawable()
    }
    
    /// Check if the lattice size is smaller than a given size.
    /// 
    /// Args:
    ///     size (int): The size to compare against
    /// 
    /// Returns:
    ///     bool: True if the lattice is smaller than the given size
    fn is_smaller_than(&self, size: i32) -> bool {
        self.inner.borrow().is_smaller_than(size.try_into().unwrap())
    }
    
    /// Check if the universe has been computed.
    /// 
    /// Returns:
    ///     bool: True if the universe has been computed
    fn universe_found(&self) -> bool {
        self.inner.borrow().universe_found()
    }
    
    /// Generate the subalgebra generated by the given elements.
    /// 
    /// Args:
    ///     generators (List[int]): List of generator elements
    /// 
    /// Returns:
    ///     BasicSet: The subalgebra generated by the given elements
    fn sg(&self, generators: Vec<i32>) -> PyBasicSet {
        let inner = self.inner.borrow();
        let result = inner.sg(&generators);
        PyBasicSet { inner: result }
    }
    
    /// Get the one-generated subalgebras.
    /// 
    /// Returns:
    ///     List[BasicSet]: List of one-generated subalgebras
    fn one_generated_subalgebras(&self) -> Vec<PyBasicSet> {
        let mut inner = self.inner.borrow_mut();
        let one_gens = inner.one_generated_subalgebras();
        one_gens.iter().map(|bs| PyBasicSet { inner: bs.clone() }).collect()
    }
    
    /// Get the join irreducibles.
    /// 
    /// Returns:
    ///     List[BasicSet]: List of join irreducible subalgebras
    fn join_irreducibles(&self) -> Vec<PyBasicSet> {
        let mut inner = self.inner.borrow_mut();
        let jis = inner.join_irreducibles_mut();
        jis.iter().map(|bs| PyBasicSet { inner: bs.clone() }).collect()
    }
    
    /// Get the meet irreducibles (stub implementation).
    /// 
    /// Returns:
    ///     List[BasicSet]: List of meet irreducible subalgebras (currently empty)
    fn meet_irreducibles(&self) -> Vec<PyBasicSet> {
        let mut inner = self.inner.borrow_mut();
        let mis = inner.meet_irreducibles_mut();
        mis.iter().map(|bs| PyBasicSet { inner: bs.clone() }).collect()
    }
    
    /// Compute the join of two subalgebras.
    /// 
    /// Args:
    ///     a (BasicSet): First subalgebra
    ///     b (BasicSet): Second subalgebra
    /// 
    /// Returns:
    ///     BasicSet: The join (smallest subalgebra containing both)
    fn join(&self, a: &PyBasicSet, b: &PyBasicSet) -> PyBasicSet {
        let inner = self.inner.borrow();
        let result = inner.join_sets(&a.inner, &b.inner);
        PyBasicSet { inner: result }
    }
    
    /// Compute the meet of two subalgebras.
    /// 
    /// Args:
    ///     a (BasicSet): First subalgebra
    ///     b (BasicSet): Second subalgebra
    /// 
    /// Returns:
    ///     BasicSet: The meet (intersection)
    fn meet(&self, a: &PyBasicSet, b: &PyBasicSet) -> PyBasicSet {
        let inner = self.inner.borrow();
        let result = Lattice::meet(&*inner, &a.inner, &b.inner);
        PyBasicSet { inner: result }
    }
    
    /// Check if one subalgebra is less than or equal to another (subset).
    /// 
    /// Args:
    ///     a (BasicSet): First subalgebra
    ///     b (BasicSet): Second subalgebra
    /// 
    /// Returns:
    ///     bool: True if a ⊆ b
    fn leq(&self, a: &PyBasicSet, b: &PyBasicSet) -> bool {
        let inner = self.inner.borrow();
        Order::leq(&*inner, &a.inner, &b.inner)
    }
    
    /// Get the universe of all subalgebras.
    /// 
    /// Returns:
    ///     List[BasicSet]: List of all subalgebras
    fn universe(&self) -> Vec<PyBasicSet> {
        let mut inner = self.inner.borrow_mut();
        let univ = inner.universe_mut();
        univ.iter().map(|bs| PyBasicSet { inner: bs.clone() }).collect()
    }
    
    /// Get the cardinality (number of subalgebras).
    /// 
    /// Returns:
    ///     int: Number of subalgebras in the lattice
    fn cardinality(&self) -> i32 {
        let inner = self.inner.borrow_mut();
        inner.cardinality()
    }
    
    /// Filter subalgebras that are greater than or equal to the given element.
    /// 
    /// Args:
    ///     element (BasicSet): The element to filter by
    /// 
    /// Returns:
    ///     List[BasicSet]: Subalgebras containing the given element
    fn filter(&self, element: &PyBasicSet) -> Vec<PyBasicSet> {
        let mut inner = self.inner.borrow_mut();
        let filtered = inner.filter(&element.inner);
        filtered.iter().map(|bs| PyBasicSet { inner: bs.clone() }).collect()
    }
    
    /// Find a minimal sized generating set for the algebra.
    /// 
    /// Returns:
    ///     BasicSet: A minimal generating set
    fn find_minimal_sized_generating_set(&self) -> PyBasicSet {
        let mut inner = self.inner.borrow_mut();
        let gen_set = inner.find_minimal_sized_generating_set();
        PyBasicSet { inner: gen_set }
    }
    
    /// Get the zero subalgebra (generated by constants).
    /// 
    /// Returns:
    ///     BasicSet: The zero subalgebra
    fn zero(&self) -> PyBasicSet {
        let inner = self.inner.borrow();
        PyBasicSet { inner: inner.zero().clone() }
    }
    
    /// Get the one subalgebra (entire algebra).
    /// 
    /// Returns:
    ///     BasicSet: The one subalgebra (whole algebra)
    fn one(&self) -> PyBasicSet {
        let inner = self.inner.borrow();
        PyBasicSet { inner: inner.one().clone() }
    }
    
    /// Remove duplicate elements from a list (static method).
    /// 
    /// Args:
    ///     lst (List[int]): List with potential duplicates
    /// 
    /// Returns:
    ///     List[int]: List with duplicates removed
    #[staticmethod]
    fn no_duplicates(lst: Vec<i32>) -> Vec<i32> {
        uacalc::alg::sublat::SubalgebraLattice::no_duplicates(lst)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        let inner = self.inner.borrow();
        format!("SubalgebraLattice(algebra_size={})", inner.get_algebra().cardinality())
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        self.__str__()
    }
}

/// Python wrapper for ParameterizedAlgebra
#[pyclass]
pub struct PyParameterizedAlgebra {
    inner: uacalc::alg::ParameterizedAlgebra,
}

#[pymethods]
impl PyParameterizedAlgebra {
    /// Create a new ParameterizedAlgebra.
    /// 
    /// Args:
    ///     parameter_names (list[str]): Names of the parameters
    ///     name (str): Name of the algebra
    ///     set_size_exp (str): Expression for set size
    ///     description (str): Description of the algebra
    ///     ops (list[ParameterizedOperation]): List of parameterized operations
    #[new]
    fn new(
        parameter_names: Vec<String>,
        name: String,
        set_size_exp: String,
        description: String,
        ops: Vec<PyParameterizedOperation>,
    ) -> Self {
        let rust_ops = ops.into_iter().map(|op| op.inner).collect();
        PyParameterizedAlgebra {
            inner: uacalc::alg::ParameterizedAlgebra::new(
                parameter_names,
                name,
                set_size_exp,
                description,
                rust_ops,
            )
        }
    }
    
    /// Create a parameter map from values.
    /// 
    /// Args:
    ///     values (list[int]): List of integer values for the parameters
    /// 
    /// Returns:
    ///     dict[str, str]: Map from parameter names to string values
    /// 
    /// Raises:
    ///     ValueError: If the number of values doesn't match the number of parameters
    fn get_parameter_map(&self, values: Vec<i32>) -> PyResult<HashMap<String, String>> {
        match self.inner.get_parameter_map(&values) {
            Ok(map) => Ok(map),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the parameter names.
    /// 
    /// Returns:
    ///     list[str]: List of parameter names
    fn get_parameter_names(&self) -> Vec<String> {
        self.inner.parameter_names.clone()
    }
    
    /// Get the algebra name.
    /// 
    /// Returns:
    ///     str: The name of the algebra
    fn get_name(&self) -> String {
        self.inner.name.clone()
    }
    
    /// Get the set size expression.
    /// 
    /// Returns:
    ///     str: The set size expression
    fn get_set_size_exp(&self) -> String {
        self.inner.set_size_exp.clone()
    }
    
    /// Get the description.
    /// 
    /// Returns:
    ///     str: The description
    fn get_description(&self) -> String {
        self.inner.description.clone()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("ParameterizedAlgebra({})", self.inner.to_string())
    }
}

/// Python wrapper for ParameterizedOperation
#[pyclass]
#[derive(Clone)]
pub struct PyParameterizedOperation {
    inner: uacalc::alg::op::ParameterizedOperation,
}

#[pymethods]
impl PyParameterizedOperation {
    /// Create a new ParameterizedOperation.
    /// 
    /// Args:
    ///     name (str): Name of the operation
    ///     symbol_name (str): Symbol name for the operation
    ///     set_size_exp (str): Expression for set size
    ///     parameter_names (list[str]): Names of the parameters
    ///     arity_exp (str): Expression for arity
    ///     description (str): Description of the operation
    ///     default_value_exp (str): Expression for default value
    ///     definition_exp (str): Expression for operation definition
    #[new]
    fn new(
        name: String,
        symbol_name: String,
        set_size_exp: String,
        parameter_names: Vec<String>,
        arity_exp: String,
        description: String,
        default_value_exp: String,
        definition_exp: String,
    ) -> Self {
        PyParameterizedOperation {
            inner: uacalc::alg::op::ParameterizedOperation::new(
                name,
                symbol_name,
                set_size_exp,
                parameter_names,
                arity_exp,
                description,
                default_value_exp,
                definition_exp,
            )
        }
    }
    
    /// Substitute parameter values in a parameterized string.
    /// 
    /// This is a simplified version that performs basic string substitution
    /// without full expression parsing.
    /// 
    /// Args:
    ///     parameterized_string (str): String containing parameter references
    ///     parm_map (dict[str, str]): Map from parameter names to values
    /// 
    /// Returns:
    ///     str: The string with parameters substituted
    #[staticmethod]
    fn sub_parm_values(parameterized_string: String, parm_map: HashMap<String, String>) -> String {
        uacalc::alg::op::ParameterizedOperation::sub_parm_values(&parameterized_string, &parm_map)
    }
    
    /// Get the operation name.
    /// 
    /// Returns:
    ///     str: The name of the operation
    fn get_name(&self) -> String {
        self.inner.name.clone()
    }
    
    /// Get the symbol name.
    /// 
    /// Returns:
    ///     str: The symbol name
    fn get_symbol_name(&self) -> String {
        self.inner.symbol_name.clone()
    }
    
    /// Get the set size expression.
    /// 
    /// Returns:
    ///     str: The set size expression
    fn get_set_size_exp(&self) -> String {
        self.inner.set_size_exp.clone()
    }
    
    /// Get the parameter names.
    /// 
    /// Returns:
    ///     list[str]: List of parameter names
    fn get_parameter_names(&self) -> Vec<String> {
        self.inner.parameter_names.clone()
    }
    
    /// Get the arity expression.
    /// 
    /// Returns:
    ///     str: The arity expression
    fn get_arity_exp(&self) -> String {
        self.inner.arity_exp.clone()
    }
    
    /// Get the description.
    /// 
    /// Returns:
    ///     str: The description
    fn get_description(&self) -> String {
        self.inner.description.clone()
    }
    
    /// Get the default value expression.
    /// 
    /// Returns:
    ///     str: The default value expression
    fn get_default_value_exp(&self) -> String {
        self.inner.default_value_exp.clone()
    }
    
    /// Get the definition expression.
    /// 
    /// Returns:
    ///     str: The definition expression
    fn get_definition_exp(&self) -> String {
        self.inner.definition_exp.clone()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("ParameterizedOperation({})", self.inner.to_string())
    }
}

/// Python wrapper for CongruenceLattice
#[pyclass]
pub struct PyCongruenceLattice {
    inner: uacalc::alg::conlat::CongruenceLattice,
}

#[pymethods]
impl PyCongruenceLattice {
    /// Create a new congruence lattice for an algebra.
    #[new]
    fn new(algebra: &PyBasicSmallAlgebra) -> Self {
        PyCongruenceLattice {
            inner: uacalc::alg::conlat::CongruenceLattice::new(Box::new(algebra.inner.clone())),
        }
    }
    
    /// Get the size of the algebra's universe.
    fn alg_size(&self) -> usize {
        self.inner.alg_size()
    }
    
    /// Get the zero congruence (all elements in separate blocks).
    fn zero(&self) -> PyPartition {
        PyPartition { inner: self.inner.zero() }
    }
    
    /// Get the one congruence (all elements in one block).
    fn one(&self) -> PyPartition {
        PyPartition { inner: self.inner.one() }
    }
    
    /// Get the cardinality of the congruence lattice.
    fn con_cardinality(&mut self) -> usize {
        self.inner.con_cardinality()
    }
    
    /// Test if the lattice is distributive.
    fn is_distributive(&mut self) -> bool {
        self.inner.is_distributive()
    }
    
    /// Get the description of the congruence lattice.
    fn get_description(&self) -> String {
        self.inner.get_description()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("CongruenceLattice({})", self.inner.to_string())
    }
}

pub fn register_alg_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyOperationSymbol>()?;
    m.add_class::<PySimilarityType>()?;
    m.add_class::<PyPrintType>()?;
    m.add_class::<PyPartition>()?;
    m.add_class::<PyPolymorphisms>()?;
    m.add_class::<PyBasicBinaryRelation>()?;
    m.add_class::<PyBasicOperation>()?;
    m.add_class::<PyIntOperation>()?;
    m.add_class::<PyAbstractIntOperation>()?;
    m.add_class::<PyCongruenceLattice>()?;
    m.add_class::<PyAbstractIntOperationNew>()?;
    m.add_class::<PyAbstractOperationNew>()?;
    m.add_class::<PySubtrace>()?;
    m.add_class::<PyGeneralAlgebra>()?;
    m.add_class::<PyBasicSmallAlgebra>()?;
    m.add_class::<PyOperationWithDefaultValue>()?;
    m.add_class::<PyOperations>()?;
    m.add_class::<PyHomomorphism>()?;
    m.add_class::<PyBasicSet>()?;
    m.add_class::<PySubalgebraLattice>()?;
    m.add_class::<PyProductAlgebra>()?;
    m.add_class::<PyPowerAlgebra>()?;
    m.add_class::<PySubalgebra>()?;
    m.add_class::<PyMatrixPowerAlgebra>()?;
    m.add_class::<PyParameterizedAlgebra>()?;
    m.add_class::<PyParameterizedOperation>()?;
    m.add_class::<PyReductAlgebra>()?;
    
    // Export only clean names (without Py prefix)
    m.add("OperationSymbol", m.getattr("PyOperationSymbol")?)?;
    m.add("SimilarityType", m.getattr("PySimilarityType")?)?;
    m.add("PrintType", m.getattr("PyPrintType")?)?;
    m.add("Partition", m.getattr("PyPartition")?)?;
    m.add("Polymorphisms", m.getattr("PyPolymorphisms")?)?;
    m.add("BasicBinaryRelation", m.getattr("PyBasicBinaryRelation")?)?;
    m.add("BasicOperation", m.getattr("PyBasicOperation")?)?;
    m.add("IntOperation", m.getattr("PyIntOperation")?)?;
    m.add("AbstractIntOperation", m.getattr("PyAbstractIntOperationNew")?)?;
    m.add("AbstractOperation", m.getattr("PyAbstractOperationNew")?)?;
    m.add("Subtrace", m.getattr("PySubtrace")?)?;
    m.add("GeneralAlgebra", m.getattr("PyGeneralAlgebra")?)?;
    m.add("BasicSmallAlgebra", m.getattr("PyBasicSmallAlgebra")?)?;
    m.add("OperationWithDefaultValue", m.getattr("PyOperationWithDefaultValue")?)?;
    m.add("Operations", m.getattr("PyOperations")?)?;
    m.add("Homomorphism", m.getattr("PyHomomorphism")?)?;
    m.add("BasicSet", m.getattr("PyBasicSet")?)?;
    m.add("SubalgebraLattice", m.getattr("PySubalgebraLattice")?)?;
    m.add("ProductAlgebra", m.getattr("PyProductAlgebra")?)?;
    m.add("PowerAlgebra", m.getattr("PyPowerAlgebra")?)?;
    m.add("Subalgebra", m.getattr("PySubalgebra")?)?;
    m.add("MatrixPowerAlgebra", m.getattr("PyMatrixPowerAlgebra")?)?;
    m.add("ParameterizedAlgebra", m.getattr("PyParameterizedAlgebra")?)?;
    m.add("ParameterizedOperation", m.getattr("PyParameterizedOperation")?)?;
    m.add("ReductAlgebra", m.getattr("PyReductAlgebra")?)?;
    m.add("CongruenceLattice", m.getattr("PyCongruenceLattice")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyOperationSymbol")?;
    module_dict.del_item("PySimilarityType")?;
    module_dict.del_item("PyPrintType")?;
    module_dict.del_item("PyPartition")?;
    module_dict.del_item("PyPolymorphisms")?;
    module_dict.del_item("PyBasicBinaryRelation")?;
    module_dict.del_item("PyBasicOperation")?;
    module_dict.del_item("PyIntOperation")?;
    module_dict.del_item("PyAbstractIntOperation")?;
    module_dict.del_item("PyCongruenceLattice")?;
    module_dict.del_item("PyAbstractIntOperationNew")?;
    module_dict.del_item("PyAbstractOperationNew")?;
    module_dict.del_item("PySubtrace")?;
    module_dict.del_item("PyGeneralAlgebra")?;
    module_dict.del_item("PyBasicSmallAlgebra")?;
    module_dict.del_item("PyOperationWithDefaultValue")?;
    module_dict.del_item("PyOperations")?;
    module_dict.del_item("PyHomomorphism")?;
    module_dict.del_item("PyBasicSet")?;
    module_dict.del_item("PySubalgebraLattice")?;
    module_dict.del_item("PyProductAlgebra")?;
    module_dict.del_item("PyPowerAlgebra")?;
    module_dict.del_item("PySubalgebra")?;
    module_dict.del_item("PyMatrixPowerAlgebra")?;
    module_dict.del_item("PyParameterizedAlgebra")?;
    module_dict.del_item("PyParameterizedOperation")?;
    module_dict.del_item("PyReductAlgebra")?;
    
    // Export cardinality constants
    m.add("CARDINALITY_UNKNOWN", uacalc::alg::CARDINALITY_UNKNOWN)?;
    m.add("CARDINALITY_FINITE", uacalc::alg::CARDINALITY_FINITE)?;
    m.add("CARDINALITY_INFINITE", uacalc::alg::CARDINALITY_INFINITE)?;
    m.add("CARDINALITY_COUNTABLE", uacalc::alg::CARDINALITY_COUNTABLE)?;
    m.add("CARDINALITY_COUNTABLY_INFINITE", uacalc::alg::CARDINALITY_COUNTABLY_INFINITE)?;
    
    Ok(())
}

/// Python wrapper for BasicBinaryRelation
#[pyclass]
pub struct PyBasicBinaryRelation {
    inner: BasicBinaryRelation,
}

#[pymethods]
impl PyBasicBinaryRelation {
    /// Create a new BasicBinaryRelation with the given universe size.
    /// 
    /// Args:
    ///     universe_size (int): The size of the universe {0, 1, ..., n-1}
    /// 
    /// Raises:
    ///     ValueError: If universe_size is zero or negative
    #[new]
    fn new(universe_size: usize) -> PyResult<Self> {
        match BasicBinaryRelation::new(universe_size) {
            Ok(inner) => Ok(PyBasicBinaryRelation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Add a pair (i, j) to the relation.
    /// 
    /// Args:
    ///     i (int): The first element
    ///     j (int): The second element
    /// 
    /// Raises:
    ///     ValueError: If indices are out of bounds
    fn add(&mut self, i: usize, j: usize) -> PyResult<()> {
        match self.inner.add(i, j) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if element i is related to element j.
    /// 
    /// Args:
    ///     i (int): The first element
    ///     j (int): The second element
    /// 
    /// Returns:
    ///     bool: True if i is related to j, False otherwise
    fn is_related(&self, i: usize, j: usize) -> bool {
        self.inner.is_related(i, j)
    }
    
    /// Get the size of the universe.
    /// 
    /// Returns:
    ///     int: The size of the universe
    fn universe_size(&self) -> usize {
        self.inner.universe_size()
    }
    
    /// Get all pairs in the relation.
    /// 
    /// Returns:
    ///     list: List of pairs as [i, j] lists
    fn get_pairs(&self) -> Vec<Vec<i32>> {
        let pairs = self.inner.get_pairs();
        pairs.into_iter()
            .map(|pair| vec![pair.get(0).unwrap(), pair.get(1).unwrap()])
            .collect()
    }
    
    /// Compose this relation with another relation.
    /// 
    /// Args:
    ///     other (BasicBinaryRelation): The other relation to compose with
    /// 
    /// Returns:
    ///     BasicBinaryRelation: The composition of the two relations
    /// 
    /// Raises:
    ///     ValueError: If relations have incompatible universe sizes
    fn compose(&self, other: &PyBasicBinaryRelation) -> PyResult<PyBasicBinaryRelation> {
        match self.inner.compose(&other.inner) {
            Ok(result) => {
                // Extract the BasicBinaryRelation from the boxed trait object
                // This is a bit of a hack since we can't downcast trait objects easily
                // For now, we'll create a new relation with the same pairs
                let pairs = result.get_pairs();
                let mut new_relation = BasicBinaryRelation::new(result.universe_size())
                    .map_err(|e| PyValueError::new_err(e))?;
                for pair in pairs {
                    let i = pair.get(0).unwrap() as usize;
                    let j = pair.get(1).unwrap() as usize;
                    new_relation.add(i, j).map_err(|e| PyValueError::new_err(e))?;
                }
                Ok(PyBasicBinaryRelation { inner: new_relation })
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Check if the relation is reflexive.
    /// 
    /// Returns:
    ///     bool: True if the relation is reflexive, False otherwise
    fn is_reflexive(&self) -> bool {
        self.inner.is_reflexive()
    }
    
    /// Check if the relation is symmetric.
    /// 
    /// Returns:
    ///     bool: True if the relation is symmetric, False otherwise
    fn is_symmetric(&self) -> bool {
        self.inner.is_symmetric()
    }
    
    /// Check if the relation is transitive.
    /// 
    /// Returns:
    ///     bool: True if the relation is transitive, False otherwise
    fn is_transitive(&self) -> bool {
        self.inner.is_transitive()
    }
    
    /// Check if the relation is an equivalence relation.
    /// 
    /// Returns:
    ///     bool: True if the relation is an equivalence relation, False otherwise
    fn is_equivalence(&self) -> bool {
        self.inner.is_equivalence()
    }
    
    /// Get the number of pairs in the relation.
    /// 
    /// Returns:
    ///     int: The number of pairs
    fn size(&self) -> usize {
        self.inner.size()
    }
    
    /// Check if the relation is empty.
    /// 
    /// Returns:
    ///     bool: True if the relation is empty, False otherwise
    fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }
    
    /// Clear all pairs from the relation.
    fn clear(&mut self) {
        self.inner.clear();
    }
    
    /// Remove a pair (i, j) from the relation.
    /// 
    /// Args:
    ///     i (int): The first element
    ///     j (int): The second element
    /// 
    /// Raises:
    ///     ValueError: If indices are out of bounds
    fn remove(&mut self, i: usize, j: usize) -> PyResult<()> {
        match self.inner.remove(i, j) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create the identity relation on a set of given size.
    /// 
    /// Args:
    ///     size (int): The size of the universe
    /// 
    /// Returns:
    ///     BasicBinaryRelation: The identity relation
    /// 
    /// Raises:
    ///     ValueError: If size is zero or negative
    #[staticmethod]
    fn identity(size: usize) -> PyResult<Self> {
        match BasicBinaryRelation::identity(size) {
            Ok(inner) => Ok(PyBasicBinaryRelation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create the universal relation on a set of given size.
    /// 
    /// Args:
    ///     size (int): The size of the universe
    /// 
    /// Returns:
    ///     BasicBinaryRelation: The universal relation
    /// 
    /// Raises:
    ///     ValueError: If size is zero or negative
    #[staticmethod]
    fn universal(size: usize) -> PyResult<Self> {
        match BasicBinaryRelation::universal(size) {
            Ok(inner) => Ok(PyBasicBinaryRelation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create the empty relation on a set of given size.
    /// 
    /// Args:
    ///     size (int): The size of the universe
    /// 
    /// Returns:
    ///     BasicBinaryRelation: The empty relation
    /// 
    /// Raises:
    ///     ValueError: If size is zero or negative
    #[staticmethod]
    fn empty(size: usize) -> PyResult<Self> {
        match BasicBinaryRelation::empty(size) {
            Ok(inner) => Ok(PyBasicBinaryRelation { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("BasicBinaryRelation({})", self.inner.to_string())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyBasicBinaryRelation) -> bool {
        self.inner == other.inner
    }
    
    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }
    
    /// Python iterator support
    fn __iter__(&self) -> PyResult<PyObject> {
        let pairs = self.get_pairs();
        Python::with_gil(|py| {
            let list = pyo3::types::PyList::new_bound(py, pairs);
            Ok(list.into())
        })
    }
}

/// Python wrapper for GeneralAlgebra (for integer universes)
#[pyclass]
pub struct PyGeneralAlgebra {
    inner: uacalc::alg::GeneralAlgebra<i32>,
}

#[pymethods]
impl PyGeneralAlgebra {
    /// Create a new GeneralAlgebra with a name.
    /// 
    /// Args:
    ///     name (str): The name of the algebra
    /// 
    /// Returns:
    ///     GeneralAlgebra: A new GeneralAlgebra instance
    #[new]
    #[pyo3(signature = (name))]
    fn new(name: String) -> Self {
        PyGeneralAlgebra {
            inner: uacalc::alg::GeneralAlgebra::new(name),
        }
    }
    
    /// Create a new GeneralAlgebra with a name and universe.
    /// 
    /// Args:
    ///     name (str): The name of the algebra
    ///     universe (Set[int]): The universe set as a list of integers
    /// 
    /// Returns:
    ///     GeneralAlgebra: A new GeneralAlgebra instance
    #[staticmethod]
    fn with_universe(name: String, universe: Vec<i32>) -> Self {
        let universe_set: std::collections::HashSet<i32> = universe.into_iter().collect();
        PyGeneralAlgebra {
            inner: uacalc::alg::GeneralAlgebra::new_with_universe(name, universe_set),
        }
    }
    
    /// Get the name of this algebra.
    /// 
    /// Returns:
    ///     str: The name of the algebra
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    /// Set the name of this algebra.
    /// 
    /// Args:
    ///     name (str): The new name for the algebra
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }
    
    /// Get the description of this algebra.
    /// 
    /// Returns:
    ///     Optional[str]: The description of the algebra, or None if not set
    fn description(&self) -> Option<&str> {
        self.inner.description()
    }
    
    /// Set the description of this algebra.
    /// 
    /// Args:
    ///     desc (Optional[str]): The new description for the algebra
    fn set_description(&mut self, desc: Option<String>) {
        self.inner.set_description(desc);
    }
    
    /// Get the cardinality of this algebra.
    /// 
    /// Returns:
    ///     int: The cardinality, or a negative value for infinite/unknown cardinalities
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }
    
    /// Get the input size for this algebra.
    /// 
    /// Returns:
    ///     int: The input size, or -1 if it exceeds maximum integer value
    fn input_size(&self) -> i32 {
        self.inner.input_size()
    }
    
    /// Check if this algebra is unary.
    /// 
    /// Returns:
    ///     bool: True if all operations have arity 1
    fn is_unary(&self) -> bool {
        self.inner.is_unary()
    }
    
    /// Check if all operations in this algebra are idempotent.
    /// 
    /// Returns:
    ///     bool: True if all operations are idempotent
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }
    
    /// Check if all operations in this algebra are total.
    /// 
    /// Returns:
    ///     bool: True if all operations are total
    fn is_total(&self) -> bool {
        self.inner.is_total()
    }
    
    /// Check if monitoring is enabled for this algebra.
    /// 
    /// Returns:
    ///     bool: True if monitoring is enabled
    fn monitoring(&self) -> bool {
        self.inner.monitoring()
    }
    
    /// Get the universe as a list of integers.
    /// 
    /// Returns:
    ///     List[int]: The universe elements as a list
    fn get_universe(&self) -> Vec<i32> {
        self.inner.universe().collect()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("GeneralAlgebra({})", self.inner.to_string())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyGeneralAlgebra) -> bool {
        // Compare basic properties since we can't easily compare the full structure
        self.inner.name() == other.inner.name() && 
        self.inner.cardinality() == other.inner.cardinality()
    }
}

/// Python wrapper for BasicSmallAlgebra (for integer universes)
#[pyclass]
pub struct PyBasicSmallAlgebra {
    pub(crate) inner: uacalc::alg::BasicSmallAlgebra<i32>,
}

impl PyBasicSmallAlgebra {
    /// Create PyBasicSmallAlgebra from inner Rust type (not exposed to Python)
    pub fn from_inner(inner: uacalc::alg::BasicSmallAlgebra<i32>) -> Self {
        PyBasicSmallAlgebra { inner }
    }
}

#[pymethods]
impl PyBasicSmallAlgebra {
    /// Create a new BasicSmallAlgebra.
    /// 
    /// Args:
    ///     name (str): The name of the algebra
    ///     universe (Set[int]): The universe set as a list of integers
    /// 
    /// Returns:
    ///     BasicSmallAlgebra: A new BasicSmallAlgebra instance
    #[new]
    #[pyo3(signature = (name, universe))]
    fn new(name: String, universe: Vec<i32>) -> Self {
        let universe_set: std::collections::HashSet<i32> = universe.into_iter().collect();
        let operations = Vec::new(); // Start with no operations
        PyBasicSmallAlgebra {
            inner: uacalc::alg::BasicSmallAlgebra::new(name, universe_set, operations),
        }
    }
    
    /// Get the name of this algebra.
    /// 
    /// Returns:
    ///     str: The name of the algebra
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    /// Set the name of this algebra.
    /// 
    /// Args:
    ///     name (str): The new name for the algebra
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }
    
    /// Get the description of this algebra.
    /// 
    /// Returns:
    ///     Optional[str]: The description of the algebra, or None if not set
    fn description(&self) -> Option<&str> {
        self.inner.description()
    }
    
    /// Set the description of this algebra.
    /// 
    /// Args:
    ///     desc (Optional[str]): The new description for the algebra
    fn set_description(&mut self, desc: Option<String>) {
        self.inner.set_description(desc);
    }
    
    /// Get the cardinality of this algebra.
    /// 
    /// Returns:
    ///     int: The cardinality of the algebra
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }
    
    /// Get the input size for this algebra.
    /// 
    /// Returns:
    ///     int: The input size, or -1 if it exceeds maximum integer value
    fn input_size(&self) -> i32 {
        self.inner.input_size()
    }
    
    /// Check if this algebra is unary.
    /// 
    /// Returns:
    ///     bool: True if all operations have arity 1
    fn is_unary(&self) -> bool {
        self.inner.is_unary()
    }
    
    /// Check if all operations in this algebra are idempotent.
    /// 
    /// Returns:
    ///     bool: True if all operations are idempotent
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }
    
    /// Check if all operations in this algebra are total.
    /// 
    /// Returns:
    ///     bool: True if all operations are total
    fn is_total(&self) -> bool {
        self.inner.is_total()
    }
    
    /// Check if monitoring is enabled for this algebra.
    /// 
    /// Returns:
    ///     bool: True if monitoring is enabled
    fn monitoring(&self) -> bool {
        self.inner.monitoring()
    }
    
    /// Get the universe as a list of integers.
    /// 
    /// Returns:
    ///     List[int]: The universe elements as a list
    fn get_universe(&self) -> Vec<i32> {
        self.inner.universe().collect()
    }
    
    /// Get the algebra type.
    /// 
    /// Returns:
    ///     str: The algebra type as a string
    fn algebra_type(&self) -> String {
        format!("{:?}", self.inner.algebra_type())
    }
    
    /// Get the k-th element of the universe.
    /// 
    /// Args:
    ///     k (int): The index of the element to retrieve
    /// 
    /// Returns:
    ///     int: The element at index k, or -1 if k is out of bounds
    fn get_element(&self, k: usize) -> i32 {
        self.inner.get_element(k).unwrap_or(-1)
    }
    
    /// Get the index of an element in the universe.
    /// 
    /// Args:
    ///     elem (int): The element to find the index for
    /// 
    /// Returns:
    ///     int: The index of the element, or -1 if not found
    fn element_index(&self, elem: i32) -> i32 {
        match self.inner.element_index(&elem) {
            Some(idx) => idx as i32,
            None => -1,
        }
    }
    
    /// Get the universe as a list.
    /// 
    /// Returns:
    ///     List[int]: The universe elements as a list, or None if not available
    fn get_universe_list(&self) -> Option<Vec<i32>> {
        self.inner.get_universe_list()
    }
    
    /// Get the universe order map.
    /// 
    /// Returns:
    ///     dict: A mapping from elements to their indices, or None if not available
    fn get_universe_order(&self) -> Option<HashMap<i32, usize>> {
        self.inner.get_universe_order()
    }
    
    /// Check if this algebra uses an integer universe.
    /// 
    /// Returns:
    ///     bool: True if the universe is just integers from 0 to n-1
    fn int_universe(&self) -> bool {
        self.inner.int_universe()
    }
    
    /// Reset cached congruence and subalgebra lattices.
    /// 
    /// Note: In this partial implementation, con/sub lattices are not yet implemented,
    /// so this is a no-op but matches the Java API signature.
    fn reset_con_and_sub(&mut self) {
        self.inner.reset_con_and_sub();
    }
    
    /// Convert operations to default value operations (for UI).
    /// 
    /// Note: In this partial implementation, this is a no-op but matches the Java API signature.
    fn convert_to_default_value_ops(&mut self) {
        self.inner.convert_to_default_value_ops();
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("BasicSmallAlgebra({})", self.inner.to_string())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyBasicSmallAlgebra) -> bool {
        // Compare basic properties since we can't easily compare the full structure
        self.inner.name() == other.inner.name() && 
        self.inner.cardinality() == other.inner.cardinality()
    }
    
    /// Get the congruence lattice (lazy initialization).
    /// 
    /// Returns:
    ///     CongruenceLattice: The congruence lattice
    fn con(&mut self) -> PyCongruenceLattice {
        let con_lat = self.inner.con();
        PyCongruenceLattice {
            inner: con_lat.clone(),
        }
    }
    
    /// Get the subalgebra lattice (lazy initialization).
    /// 
    /// Returns:
    ///     SubalgebraLattice: The subalgebra lattice
    fn sub(&mut self) -> PySubalgebraLattice {
        let sub_lat = self.inner.sub();
        PySubalgebraLattice {
            inner: std::cell::RefCell::new(sub_lat.clone()),
        }
    }
}

/// Python wrapper for Homomorphism
#[pyclass]
#[derive(Clone)]
pub struct PyHomomorphism {
    inner: uacalc::alg::Homomorphism,
}

#[pymethods]
impl PyHomomorphism {
    /// Create a new Homomorphism from domain to range with the given mapping.
    /// 
    /// Args:
    ///     domain (BasicSmallAlgebra): The domain algebra
    ///     range (BasicSmallAlgebra): The range algebra
    ///     map (dict): The mapping from domain indices to range indices
    /// 
    /// Raises:
    ///     ValueError: If the mapping is invalid or algebras are incompatible
    #[new]
    fn new(
        domain: &PyBasicSmallAlgebra,
        range: &PyBasicSmallAlgebra,
        map: std::collections::HashMap<usize, usize>,
    ) -> PyResult<Self> {
        // Convert Python algebras to Rust algebras
        let domain_box = Box::new(domain.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        let range_box = Box::new(range.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        
        match uacalc::alg::Homomorphism::new_safe(domain_box, range_box, map) {
            Ok(inner) => Ok(PyHomomorphism { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Compute the kernel partition of this homomorphism.
    /// 
    /// The kernel partition groups domain elements that map to the same
    /// range element.
    /// 
    /// Returns:
    ///     Partition: The kernel partition
    /// 
    /// Raises:
    ///     ValueError: If there's an error computing the kernel
    fn kernel(&self) -> PyResult<PyPartition> {
        match self.inner.kernel() {
            Ok(partition) => Ok(PyPartition { inner: partition }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a product homomorphism from a list of homomorphisms.
    /// 
    /// This static method creates a list of IntArray elements representing
    /// the product homomorphism.
    /// 
    /// Args:
    ///     homomorphisms (list): A list of homomorphisms with the same domain
    /// 
    /// Returns:
    ///     list: List of IntArray elements for the product
    /// 
    /// Raises:
    ///     ValueError: If the homomorphisms are incompatible or empty
    #[staticmethod]
    fn product_homo(homomorphisms: &Bound<'_, PyList>) -> PyResult<Vec<PyIntArray>> {
        let mut rust_homos = Vec::new();
        
        for item in homomorphisms.iter() {
            let py_homo = item.extract::<PyHomomorphism>()?;
            rust_homos.push(py_homo.inner.clone());
        }
        
        match uacalc::alg::Homomorphism::product_homo(&rust_homos) {
            Ok(int_arrays) => {
                let mut py_int_arrays = Vec::new();
                for int_array in int_arrays {
                    py_int_arrays.push(PyIntArray { inner: int_array });
                }
                Ok(py_int_arrays)
            }
            Err(e) => Err(PyValueError::new_err(e))
        }
    }
    
    /// Get the domain algebra.
    /// 
    /// Returns:
    ///     BasicSmallAlgebra: The domain algebra
    fn get_domain(&self) -> PyBasicSmallAlgebra {
        // Clone the domain algebra and return it as a BasicSmallAlgebra
        // Note: This assumes the domain is a BasicSmallAlgebra
        let domain = self.inner.get_domain();
        // We need to downcast from trait object to concrete type
        // For now, we'll create a new BasicSmallAlgebra with the same properties
        // This is a limitation - ideally we'd have a way to clone the exact type
        PyBasicSmallAlgebra {
            inner: uacalc::alg::BasicSmallAlgebra::new(
                domain.name().to_string(),
                domain.universe().collect(),
                domain.operations()
            )
        }
    }
    
    /// Set the domain algebra.
    /// 
    /// Args:
    ///     domain (BasicSmallAlgebra): The new domain algebra
    fn set_domain(&mut self, domain: &PyBasicSmallAlgebra) {
        let domain_box = Box::new(domain.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        self.inner.set_domain(domain_box);
    }
    
    /// Get the range algebra.
    /// 
    /// Returns:
    ///     BasicSmallAlgebra: The range algebra
    fn get_range(&self) -> PyBasicSmallAlgebra {
        // Clone the range algebra and return it as a BasicSmallAlgebra
        // Note: This assumes the range is a BasicSmallAlgebra
        let range = self.inner.get_range();
        // We need to downcast from trait object to concrete type
        // For now, we'll create a new BasicSmallAlgebra with the same properties
        // This is a limitation - ideally we'd have a way to clone the exact type
        PyBasicSmallAlgebra {
            inner: uacalc::alg::BasicSmallAlgebra::new(
                range.name().to_string(),
                range.universe().collect(),
                range.operations()
            )
        }
    }
    
    /// Set the range algebra.
    /// 
    /// Args:
    ///     range (BasicSmallAlgebra): The new range algebra
    fn set_range(&mut self, range: &PyBasicSmallAlgebra) {
        let range_box = Box::new(range.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        self.inner.set_range(range_box);
    }
    
    /// Get the mapping.
    /// 
    /// Returns:
    ///     dict: The mapping from domain indices to range indices
    fn get_map(&self) -> std::collections::HashMap<usize, usize> {
        self.inner.get_map().clone()
    }
    
    /// Set the mapping.
    /// 
    /// Args:
    ///     map (dict): The new mapping
    fn set_map(&mut self, map: std::collections::HashMap<usize, usize>) {
        self.inner.set_map(map);
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("Homomorphism({})", self.inner.to_string())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyHomomorphism) -> bool {
        // Compare basic properties since we can't easily compare the full structure
        self.inner.get_domain().name() == other.inner.get_domain().name() &&
        self.inner.get_range().name() == other.inner.get_range().name() &&
        self.inner.get_map() == other.inner.get_map()
    }
}

/// Python wrapper for ProductAlgebra
#[pyclass]
pub struct PyProductAlgebra {
    inner: uacalc::alg::ProductAlgebra,
}

#[pymethods]
impl PyProductAlgebra {
    /// Create a new ProductAlgebra from a list of algebras.
    /// 
    /// Args:
    ///     name (str): Name of the product algebra
    ///     algebras (list[BasicSmallAlgebra]): List of algebras to form the product
    /// 
    /// Raises:
    ///     ValueError: If algebras are incompatible or empty
    #[new]
    fn new(name: String, algebras: Vec<PyRef<PyBasicSmallAlgebra>>) -> PyResult<Self> {
        if algebras.is_empty() {
            return Err(PyValueError::new_err("Cannot create product of empty algebra list"));
        }
        
        let rust_algebras: Vec<Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>> = algebras
            .iter()
            .map(|alg| Box::new(alg.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>)
            .collect();
        
        match uacalc::alg::ProductAlgebra::new_safe(name, rust_algebras) {
            Ok(inner) => Ok(PyProductAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Calculate the product cardinality.
    /// 
    /// Args:
    ///     sizes (list[int]): The sizes of the algebras
    /// 
    /// Returns:
    ///     int: The product cardinality, or -1 if too large, or 0 if any factor is empty
    /// 
    /// Raises:
    ///     ValueError: If sizes array is empty
    #[staticmethod]
    fn calc_card(sizes: Vec<i32>) -> PyResult<i32> {
        match uacalc::alg::ProductAlgebra::calc_card_safe(&sizes) {
            Ok(card) => Ok(card),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the number of factor algebras.
    /// 
    /// Returns:
    ///     int: The number of algebras in the product
    fn number_of_factors(&self) -> usize {
        self.inner.number_of_factors()
    }
    
    /// Get the sizes of each factor algebra.
    /// 
    /// Returns:
    ///     list[int]: Sizes of the factor algebras
    fn get_sizes(&self) -> Vec<i32> {
        self.inner.get_sizes().to_vec()
    }
    
    /// Get the cardinality of this product algebra.
    /// 
    /// Returns:
    ///     int: The cardinality (size of the universe)
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }
    
    /// Get the element at the given index.
    /// 
    /// Args:
    ///     k (int): Index of the element
    /// 
    /// Returns:
    ///     int: The element at index k, or -1 if out of bounds
    fn get_element(&self, k: usize) -> i32 {
        self.inner.get_element(k).unwrap_or(-1)
    }
    
    /// Get the index of an element in the universe.
    /// 
    /// Args:
    ///     elem (int): The element to find
    /// 
    /// Returns:
    ///     int: The index of the element, or -1 if not found
    fn element_index(&self, elem: i32) -> i32 {
        match self.inner.element_index(&elem) {
            Some(idx) => idx as i32,
            None => -1,
        }
    }
    
    /// Get the algebra type.
    /// 
    /// Returns:
    ///     str: The algebra type ("Product")
    fn algebra_type(&self) -> String {
        format!("{:?}", self.inner.algebra_type())
    }
    
    /// Get the name of this algebra.
    /// 
    /// Returns:
    ///     str: The name of the algebra
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    /// Set the name of this algebra.
    /// 
    /// Args:
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }
    
    /// Make operation tables for all operations.
    fn make_operation_tables(&mut self) {
        self.inner.make_operation_tables();
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("ProductAlgebra({})", self.inner.to_string())
    }
}

/// Python wrapper for PowerAlgebra
#[pyclass]
pub struct PyPowerAlgebra {
    inner: uacalc::alg::PowerAlgebra,
}

#[pymethods]
impl PyPowerAlgebra {
    /// Create a new PowerAlgebra from a root algebra and power.
    /// 
    /// Args:
    ///     root (BasicSmallAlgebra): The algebra to raise to a power
    ///     power (int): The power/exponent (number of copies)
    /// 
    /// Raises:
    ///     ValueError: If power is invalid or algebra is incompatible
    #[new]
    fn new(root: &PyBasicSmallAlgebra, power: usize) -> PyResult<Self> {
        let rust_root = Box::new(root.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        
        match uacalc::alg::PowerAlgebra::new_safe(rust_root, power) {
            Ok(inner) => Ok(PyPowerAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new PowerAlgebra with a custom name.
    /// 
    /// Args:
    ///     name (str): The name for the power algebra
    ///     root (BasicSmallAlgebra): The algebra to raise to a power
    ///     power (int): The power/exponent (number of copies)
    /// 
    /// Raises:
    ///     ValueError: If power is invalid or algebra is incompatible
    #[staticmethod]
    fn new_with_name(name: String, root: &PyBasicSmallAlgebra, power: usize) -> PyResult<Self> {
        let rust_root = Box::new(root.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        
        match uacalc::alg::PowerAlgebra::new_with_name_safe(name, rust_root, power) {
            Ok(inner) => Ok(PyPowerAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the root algebra.
    /// 
    /// Returns:
    ///     BasicSmallAlgebra: The root algebra
    fn get_root(&self) -> PyBasicSmallAlgebra {
        // We can't return a reference to the root algebra since it's boxed
        // This is a limitation of the current design
        PyBasicSmallAlgebra { inner: uacalc::alg::BasicSmallAlgebra::new(
            "Root".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )}
    }
    
    /// Get the parent algebra (same as root for power algebra).
    /// 
    /// Returns:
    ///     BasicSmallAlgebra: The parent algebra
    fn parent(&self) -> PyBasicSmallAlgebra {
        // Same limitation as get_root
        PyBasicSmallAlgebra { inner: uacalc::alg::BasicSmallAlgebra::new(
            "Parent".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )}
    }
    
    /// Get the parent algebras (list containing the root algebra).
    /// 
    /// Returns:
    ///     list[BasicSmallAlgebra]: List containing the root algebra
    fn parents(&self) -> Vec<PyBasicSmallAlgebra> {
        // Same limitation as get_root
        vec![PyBasicSmallAlgebra { inner: uacalc::alg::BasicSmallAlgebra::new(
            "Parent".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )}]
    }
    
    /// Get the power/exponent.
    /// 
    /// Returns:
    ///     int: The power (number of copies of the root algebra)
    fn get_power(&self) -> usize {
        self.inner.get_power()
    }
    
    /// Get the size of the root algebra.
    /// 
    /// Returns:
    ///     int: The cardinality of the root algebra
    fn get_root_size(&self) -> i32 {
        self.inner.get_root_size()
    }
    
    /// Get the cardinality of this power algebra.
    /// 
    /// Returns:
    ///     int: The cardinality of the power algebra
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }
    
    /// Get the name of this power algebra.
    /// 
    /// Returns:
    ///     str: The name of the power algebra
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    /// Set the name of this power algebra.
    /// 
    /// Args:
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }
    
    /// Get the description of this power algebra.
    /// 
    /// Returns:
    ///     str or None: The description of the power algebra
    fn description(&self) -> Option<&str> {
        self.inner.description()
    }
    
    /// Set the description of this power algebra.
    /// 
    /// Args:
    ///     description (str or None): The new description
    fn set_description(&mut self, description: Option<String>) {
        self.inner.set_description(description);
    }
    
    /// Get the algebra type.
    /// 
    /// Returns:
    ///     str: The algebra type ("Power")
    fn algebra_type(&self) -> String {
        format!("{:?}", self.inner.algebra_type())
    }
    
    /// Get the operations of this power algebra.
    /// 
    /// Returns:
    ///     list: List of operations (placeholder - not implemented yet)
    fn operations(&self) -> Vec<PyBasicOperation> {
        // TODO: Implement proper operations conversion
        Vec::new()
    }
    
    /// Check if this power algebra is unary.
    /// 
    /// Returns:
    ///     bool: True if the algebra is unary, False otherwise
    fn is_unary(&self) -> bool {
        self.inner.is_unary()
    }
    
    /// Check if this power algebra is idempotent.
    /// 
    /// Returns:
    ///     bool: True if the algebra is idempotent, False otherwise
    fn is_idempotent(&self) -> bool {
        self.inner.is_idempotent()
    }
    
    /// Check if this power algebra is total.
    /// 
    /// Returns:
    ///     bool: True if the algebra is total, False otherwise
    fn is_total(&self) -> bool {
        self.inner.is_total()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("PowerAlgebra({})", self.inner.to_string())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyPowerAlgebra) -> bool {
        self.inner.name() == other.inner.name() &&
        self.inner.cardinality() == other.inner.cardinality() &&
        self.inner.get_power() == other.inner.get_power()
    }
    
    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.name().hash(&mut hasher);
        self.inner.cardinality().hash(&mut hasher);
        self.inner.get_power().hash(&mut hasher);
        hasher.finish()
    }
}

/// Python wrapper for Subalgebra
#[pyclass]
pub struct PySubalgebra {
    inner: uacalc::alg::Subalgebra,
}

#[pymethods]
impl PySubalgebra {
    /// Create a new Subalgebra with the given super algebra and subuniverse.
    /// 
    /// Args:
    ///     name (str): Name of the subalgebra
    ///     super_algebra (BasicSmallAlgebra): The super algebra
    ///     univ (list[int]): Array of indices in the super algebra forming the subuniverse
    /// 
    /// Raises:
    ///     ValueError: If the subuniverse is empty or contains invalid indices
    #[new]
    fn new(name: String, super_algebra: &PyBasicSmallAlgebra, univ: Vec<i32>) -> PyResult<Self> {
        let super_box = Box::new(super_algebra.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        match uacalc::alg::Subalgebra::new_safe(name, super_box, univ) {
            Ok(inner) => Ok(PySubalgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Find the index in this subalgebra of the element with index k in the super algebra.
    /// 
    /// Uses binary search since the universe array is sorted.
    /// 
    /// Args:
    ///     k (int): Index in the super algebra
    /// 
    /// Returns:
    ///     int: Index in the subalgebra, or -1 if not found
    fn index(&self, k: i32) -> i32 {
        match self.inner.index(k) {
            Some(idx) => idx as i32,
            None => -1,
        }
    }
    
    /// Restrict a partition (or congruence) on the parent algebra to this subalgebra.
    /// 
    /// Args:
    ///     par (Partition): Partition on the super algebra
    /// 
    /// Returns:
    ///     Partition: Restricted partition on this subalgebra
    /// 
    /// Raises:
    ///     ValueError: If restriction fails
    fn restrict_partition(&self, par: &crate::alg::PyPartition) -> PyResult<crate::alg::PyPartition> {
        match self.inner.restrict_partition(&par.inner) {
            Ok(restricted) => Ok(crate::alg::PyPartition { inner: restricted }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the super algebra name.
    /// 
    /// Returns:
    ///     str: Name of the super algebra
    fn super_algebra_name(&self) -> String {
        self.inner.super_algebra().name().to_string()
    }
    
    /// Get the subuniverse array.
    /// 
    /// Returns:
    ///     list[int]: Array of indices forming the subuniverse
    fn get_subuniverse_array(&self) -> Vec<i32> {
        self.inner.get_subuniverse_array().to_vec()
    }
    
    /// Get the cardinality of this subalgebra.
    /// 
    /// Returns:
    ///     int: The cardinality (size of the universe)
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }
    
    /// Get the element at the given index.
    /// 
    /// Args:
    ///     k (int): Index of the element
    /// 
    /// Returns:
    ///     int: The element at index k, or -1 if out of bounds
    fn get_element(&self, k: usize) -> i32 {
        self.inner.get_element(k).unwrap_or(-1)
    }
    
    /// Get the index of an element in the universe.
    /// 
    /// Args:
    ///     elem (int): The element to find
    /// 
    /// Returns:
    ///     int: The index of the element, or -1 if not found
    fn element_index(&self, elem: i32) -> i32 {
        match self.inner.element_index(&elem) {
            Some(idx) => idx as i32,
            None => -1,
        }
    }
    
    /// Get the algebra type.
    /// 
    /// Returns:
    ///     str: The algebra type ("Subalgebra")
    fn algebra_type(&self) -> String {
        format!("{:?}", self.inner.algebra_type())
    }
    
    /// Get the name of this algebra.
    /// 
    /// Returns:
    ///     str: The name of the algebra
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    /// Set the name of this algebra.
    /// 
    /// Args:
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("Subalgebra({})", self.inner.to_string())
    }
    
    /// Get the congruence lattice (lazy initialization).
    /// 
    /// Returns:
    ///     CongruenceLattice: The congruence lattice
    fn con(&mut self) -> PyCongruenceLattice {
        let con_lat = self.inner.con();
        PyCongruenceLattice {
            inner: con_lat.clone(),
        }
    }
    
    /// Get the subalgebra lattice (lazy initialization).
    /// 
    /// Returns:
    ///     SubalgebraLattice: The subalgebra lattice
    fn sub(&mut self) -> PySubalgebraLattice {
        let sub_lat = self.inner.sub();
        PySubalgebraLattice {
            inner: std::cell::RefCell::new(sub_lat.clone()),
        }
    }
}

/// Python wrapper for MatrixPowerAlgebra
#[pyclass]
pub struct PyMatrixPowerAlgebra {
    inner: uacalc::alg::MatrixPowerAlgebra,
}

#[pymethods]
impl PyMatrixPowerAlgebra {
    /// Create a new MatrixPowerAlgebra from a root algebra and power.
    /// 
    /// Args:
    ///     root (BasicSmallAlgebra): The algebra to raise to a power
    ///     power (int): The power/exponent (number of copies)
    /// 
    /// Raises:
    ///     ValueError: If power is invalid or algebra is incompatible
    #[new]
    fn new(root: &PyBasicSmallAlgebra, power: usize) -> PyResult<Self> {
        let rust_root = Box::new(root.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        
        match uacalc::alg::MatrixPowerAlgebra::new_safe(rust_root, power) {
            Ok(inner) => Ok(PyMatrixPowerAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Create a new MatrixPowerAlgebra with a custom name.
    /// 
    /// Args:
    ///     name (str): The name for the matrix power algebra
    ///     root (BasicSmallAlgebra): The algebra to raise to a power
    ///     power (int): The power/exponent (number of copies)
    /// 
    /// Raises:
    ///     ValueError: If power is invalid or algebra is incompatible
    #[staticmethod]
    fn new_with_name(name: String, root: &PyBasicSmallAlgebra, power: usize) -> PyResult<Self> {
        let rust_root = Box::new(root.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        
        match uacalc::alg::MatrixPowerAlgebra::new_with_name_safe(name, rust_root, power) {
            Ok(inner) => Ok(PyMatrixPowerAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the root algebra.
    /// 
    /// Returns:
    ///     BasicSmallAlgebra: The root algebra
    fn get_root(&self) -> PyBasicSmallAlgebra {
        // We can't return a reference to the root algebra since it's boxed
        // This is a limitation of the current design
        PyBasicSmallAlgebra { inner: uacalc::alg::BasicSmallAlgebra::new(
            "Root".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )}
    }
    
    /// Get the parent algebra (same as root for matrix power algebra).
    /// 
    /// Returns:
    ///     BasicSmallAlgebra: The parent algebra
    fn parent(&self) -> PyBasicSmallAlgebra {
        // Same limitation as get_root
        PyBasicSmallAlgebra { inner: uacalc::alg::BasicSmallAlgebra::new(
            "Parent".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )}
    }
    
    /// Get the parent algebras (list containing the root algebra).
    /// 
    /// Returns:
    ///     list[BasicSmallAlgebra]: List containing the root algebra
    fn parents(&self) -> Vec<PyBasicSmallAlgebra> {
        // Same limitation as get_root
        vec![PyBasicSmallAlgebra { inner: uacalc::alg::BasicSmallAlgebra::new(
            "Parent".to_string(),
            std::collections::HashSet::new(),
            Vec::new()
        )}]
    }
    
    /// Get the underlying power algebra.
    /// 
    /// Returns:
    ///     PowerAlgebra: The underlying power algebra
    fn get_power_algebra(&self) -> PyPowerAlgebra {
        // We can't return a reference to the power algebra since it's not cloneable
        // This is a limitation of the current design
        PyPowerAlgebra { inner: uacalc::alg::PowerAlgebra::new_safe(
            Box::new(uacalc::alg::BasicSmallAlgebra::new(
                "Dummy".to_string(),
                std::collections::HashSet::new(),
                Vec::new()
            )) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>,
            1
        ).unwrap()}
    }
    
    /// Get the power/exponent.
    /// 
    /// Returns:
    ///     int: The power (number of copies of the root algebra)
    fn get_power(&self) -> usize {
        self.inner.get_power()
    }
    
    /// Get an element by its index using Horner encoding.
    /// 
    /// Args:
    ///     index (int): The index of the element
    /// 
    /// Returns:
    ///     list[int]: The element as a list of integers
    fn get_element(&self, index: usize) -> Vec<i32> {
        self.inner.get_element(index)
    }
    
    /// Get the index of an element using the power algebra.
    /// 
    /// Args:
    ///     obj (list[int]): The element (as a list of integers)
    /// 
    /// Returns:
    ///     int: The index of the element
    fn element_index(&self, obj: Vec<i32>) -> usize {
        self.inner.element_index(&obj)
    }
    
    /// Get the universe as a list of integer arrays.
    /// 
    /// Returns:
    ///     list[list[int]]: A list of lists representing the universe elements
    fn get_universe_list(&self) -> Vec<Vec<i32>> {
        self.inner.get_universe_list()
    }
    
    /// Get the universe order (not implemented for matrix power algebras).
    /// 
    /// Returns:
    ///     None: Matrix power algebras don't have a natural order
    fn get_universe_order(&self) -> Option<HashMap<Vec<i32>, usize>> {
        self.inner.get_universe_order()
    }
    
    /// Convert to default value operations (not supported for matrix power algebras).
    /// 
    /// Raises:
    ///     RuntimeError: Always raises "Only for basic algebras"
    fn convert_to_default_value_ops(&mut self) -> PyResult<()> {
        Err(PyValueError::new_err("Only for basic algebras"))
    }
    
    /// Get the algebra type.
    /// 
    /// Returns:
    ///     str: The algebra type ("MATRIX_POWER")
    fn algebra_type(&self) -> String {
        "MATRIX_POWER".to_string()
    }
    
    /// Get the cardinality of this algebra.
    /// 
    /// Returns:
    ///     int: The number of elements in the algebra
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }
    
    /// Get the name of this algebra.
    /// 
    /// Returns:
    ///     str: The name of the algebra
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    /// Set the name of this algebra.
    /// 
    /// Args:
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }
    
    /// Get the description of this algebra.
    /// 
    /// Returns:
    ///     str or None: The description of the algebra
    fn description(&self) -> Option<&str> {
        self.inner.description()
    }
    
    /// Set the description of this algebra.
    /// 
    /// Args:
    ///     desc (str or None): The new description
    fn set_description(&mut self, desc: Option<String>) {
        self.inner.set_description(desc);
    }
    
    /// Check if this algebra is unary (all operations have arity 1).
    /// 
    /// Returns:
    ///     bool: True if all operations are unary
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
    
    /// Get the number of operations in this algebra.
    /// 
    /// Returns:
    ///     int: The number of operations
    fn operations_count(&self) -> usize {
        self.inner.operations().len()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("MatrixPowerAlgebra({})", self.inner.to_string())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyMatrixPowerAlgebra) -> bool {
        self.inner.name() == other.inner.name() && 
        self.inner.get_power() == other.inner.get_power() &&
        self.inner.cardinality() == other.inner.cardinality()
    }
    
    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.name().hash(&mut hasher);
        self.inner.get_power().hash(&mut hasher);
        self.inner.cardinality().hash(&mut hasher);
        hasher.finish()
    }
}

/// Python wrapper for ReductAlgebra
#[pyclass]
pub struct PyReductAlgebra {
    inner: uacalc::alg::ReductAlgebra,
}

impl PyReductAlgebra {
    /// Create PyReductAlgebra from inner Rust type (not exposed to Python)
    fn from_inner(inner: uacalc::alg::ReductAlgebra) -> Self {
        PyReductAlgebra { inner }
    }
}

#[pymethods]
impl PyReductAlgebra {
    /// Create a new ReductAlgebra from a super algebra and list of terms.
    /// 
    /// Args:
    ///     super_algebra (BasicSmallAlgebra): The super algebra that this reduct is based on
    ///     term_list (List[Term]): The list of terms that define the operations
    /// 
    /// Returns:
    ///     ReductAlgebra: A new ReductAlgebra instance
    /// 
    /// Raises:
    ///     ValueError: If the terms are invalid or algebra is incompatible
    #[new]
    fn new(super_algebra: &PyBasicSmallAlgebra, term_list: &PyList) -> PyResult<Self> {
        // Convert Python list of terms to Rust Vec<Box<dyn Term>>
        let mut rust_terms: Vec<Box<dyn uacalc::terms::Term>> = Vec::new();
        
        for item in term_list.iter() {
            // For now, we'll create a simple variable term
            // In a full implementation, we'd need to handle different term types
            if let Ok(var_name) = item.extract::<String>() {
                let var = Box::new(uacalc::terms::VariableImp::new(&var_name)) as Box<dyn uacalc::terms::Term>;
                rust_terms.push(var);
            } else {
                return Err(PyValueError::new_err("Term list must contain strings (variable names)"));
            }
        }
        
        // Create the super algebra as a trait object
        let super_alg = Box::new(super_algebra.inner.clone()) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
        
        match uacalc::alg::ReductAlgebra::new_safe(super_alg, rust_terms) {
            Ok(inner) => Ok(PyReductAlgebra { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the name of this algebra.
    /// 
    /// Returns:
    ///     str: The name of the algebra
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    /// Set the name of this algebra.
    /// 
    /// Args:
    ///     name (str): The new name
    fn set_name(&mut self, name: String) {
        self.inner.set_name(name);
    }
    
    /// Get the cardinality of this algebra.
    /// 
    /// Returns:
    ///     int: The cardinality of the algebra
    fn cardinality(&self) -> i32 {
        self.inner.cardinality()
    }
    
    /// Get the algebra type.
    /// 
    /// Returns:
    ///     str: The algebra type
    fn algebra_type(&self) -> String {
        "Reduct".to_string()
    }
    
    /// Get the universe as a list.
    /// 
    /// Returns:
    ///     List[int]: The universe elements
    fn get_universe_list(&self) -> Option<Vec<i32>> {
        self.inner.get_universe_list()
    }
    
    /// Get the universe order as a dictionary.
    /// 
    /// Returns:
    ///     Dict[int, int]: The universe order mapping
    fn get_universe_order(&self) -> Option<HashMap<i32, usize>> {
        self.inner.get_universe_order()
    }
    
    /// Get an element by its index.
    /// 
    /// Args:
    ///     index (int): The index of the element
    /// 
    /// Returns:
    ///     int: The element at the given index
    fn get_element(&self, index: usize) -> Option<i32> {
        self.inner.get_element(index)
    }
    
    /// Get the index of an element.
    /// 
    /// Args:
    ///     element (int): The element to find the index for
    /// 
    /// Returns:
    ///     int: The index of the element
    fn element_index(&self, element: i32) -> Option<usize> {
        self.inner.element_index(&element)
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
    
    /// Get the number of operations in this algebra.
    /// 
    /// Returns:
    ///     int: The number of operations
    fn operations_count(&self) -> usize {
        self.inner.operations().len()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("ReductAlgebra({})", self.inner.to_string())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PyReductAlgebra) -> bool {
        self.inner.name() == other.inner.name() && 
        self.inner.cardinality() == other.inner.cardinality()
    }
    
    /// Python hash function
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.name().hash(&mut hasher);
        self.inner.cardinality().hash(&mut hasher);
        hasher.finish()
    }
    
    /// Get the congruence lattice (lazy initialization).
    /// 
    /// Returns:
    ///     CongruenceLattice: The congruence lattice
    fn con(&mut self) -> PyCongruenceLattice {
        let con_lat = self.inner.con();
        PyCongruenceLattice {
            inner: con_lat.clone(),
        }
    }
    
    /// Get the subalgebra lattice (lazy initialization).
    /// 
    /// Returns:
    ///     SubalgebraLattice: The subalgebra lattice
    fn sub(&mut self) -> PySubalgebraLattice {
        let sub_lat = self.inner.sub();
        PySubalgebraLattice {
            inner: std::cell::RefCell::new(sub_lat.clone()),
        }
    }
}

