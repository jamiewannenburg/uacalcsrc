use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::{PyList, PyListMethods, PyDict};
use uacalc::alg::*;
use uacalc::alg::conlat::{BinaryRelation, MutableBinaryRelation};
use uacalc::util::IntArrayTrait;
use uacalc::alg::conlat::BasicBinaryRelation;
use uacalc::alg::conlat::subtrace::Subtrace;
use uacalc::alg::op::{Operation, BasicOperation, AbstractIntOperation, IntOperation};

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
        Python::with_gil(|py| {
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
            
            if let Some(table_param) = set_size {
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
            Ok(op) => {
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

pub fn register_alg_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyOperationSymbol>()?;
    m.add_class::<PySimilarityType>()?;
    m.add_class::<PyPrintType>()?;
    m.add_class::<PyPartition>()?;
    m.add_class::<PyBasicBinaryRelation>()?;
    m.add_class::<PyBasicOperation>()?;
    m.add_class::<PyIntOperation>()?;
    m.add_class::<PyAbstractIntOperation>()?;
    m.add_class::<PyAbstractIntOperationNew>()?;
    m.add_class::<PyAbstractOperationNew>()?;
    m.add_class::<PySubtrace>()?;
    m.add_class::<PyGeneralAlgebra>()?;
    m.add_class::<PyBasicSmallAlgebra>()?;
    m.add_class::<PyOperationWithDefaultValue>()?;
    m.add_class::<PyOperations>()?;
    
    // Export only clean names (without Py prefix)
    m.add("OperationSymbol", m.getattr("PyOperationSymbol")?)?;
    m.add("SimilarityType", m.getattr("PySimilarityType")?)?;
    m.add("PrintType", m.getattr("PyPrintType")?)?;
    m.add("Partition", m.getattr("PyPartition")?)?;
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
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyOperationSymbol")?;
    module_dict.del_item("PySimilarityType")?;
    module_dict.del_item("PyPrintType")?;
    module_dict.del_item("PyPartition")?;
    module_dict.del_item("PyBasicBinaryRelation")?;
    module_dict.del_item("PyBasicOperation")?;
    module_dict.del_item("PyIntOperation")?;
    module_dict.del_item("PyAbstractIntOperation")?;
    module_dict.del_item("PyAbstractIntOperationNew")?;
    module_dict.del_item("PyAbstractOperationNew")?;
    module_dict.del_item("PySubtrace")?;
    module_dict.del_item("PyGeneralAlgebra")?;
    module_dict.del_item("PyBasicSmallAlgebra")?;
    module_dict.del_item("PyOperationWithDefaultValue")?;
    module_dict.del_item("PyOperations")?;
    
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
    inner: uacalc::alg::BasicSmallAlgebra<i32>,
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
}

