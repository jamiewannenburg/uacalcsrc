use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use uacalc::alg::*;
use uacalc::alg::conlat::{BinaryRelation, MutableBinaryRelation};
use uacalc::util::IntArrayTrait;
use uacalc::alg::conlat::{BasicBinaryRelation, Subtrace};

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

pub fn register_alg_module(py: Python, m: &PyModule) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyOperationSymbol>()?;
    m.add_class::<PySimilarityType>()?;
    m.add_class::<PyPrintType>()?;
    m.add_class::<PyPartition>()?;
    m.add_class::<PyBasicBinaryRelation>()?;
    m.add_class::<PySubtrace>()?;
    
    // Export only clean names (without Py prefix)
    m.add("OperationSymbol", m.getattr("PyOperationSymbol")?)?;
    m.add("SimilarityType", m.getattr("PySimilarityType")?)?;
    m.add("PrintType", m.getattr("PyPrintType")?)?;
    m.add("Partition", m.getattr("PyPartition")?)?;
    m.add("BasicBinaryRelation", m.getattr("PyBasicBinaryRelation")?)?;
    m.add("Subtrace", m.getattr("PySubtrace")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyOperationSymbol")?;
    module_dict.del_item("PySimilarityType")?;
    module_dict.del_item("PyPrintType")?;
    module_dict.del_item("PyPartition")?;
    module_dict.del_item("PyBasicBinaryRelation")?;
    module_dict.del_item("PySubtrace")?;
    
    Ok(())
}

/// Python wrapper for BasicBinaryRelation
#[pyclass]
pub struct PyBasicBinaryRelation {
    inner: BasicBinaryRelation,
}

/// Python wrapper for Subtrace
#[pyclass]
pub struct PySubtrace {
    inner: Subtrace,
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
            let list = pyo3::types::PyList::new(py, pairs);
            Ok(list.into())
        })
    }
}

#[pymethods]
impl PySubtrace {
    /// Create a new Subtrace with given elements and involution flag.
    /// 
    /// Args:
    ///     a (int): First element of the subtrace pair
    ///     b (int): Second element of the subtrace pair
    ///     has_involution (bool): Whether this subtrace has involution
    #[new]
    fn new(a: i32, b: i32, has_involution: bool) -> Self {
        PySubtrace {
            inner: Subtrace::new(a, b, has_involution),
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
            inner: Subtrace::new_with_type(a, b, has_involution, type_value),
        }
    }
    
    /// Get the first element of the subtrace pair.
    /// 
    /// Returns:
    ///     int: The first element
    fn first(&self) -> i32 {
        self.inner.first()
    }
    
    /// Get the second element of the subtrace pair.
    /// 
    /// Returns:
    ///     int: The second element
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
    
    /// Get the subtrace universe.
    /// 
    /// Returns:
    ///     list or None: List of IntArray pairs if set, None otherwise
    fn get_subtrace_universe(&self) -> Option<Vec<Vec<i32>>> {
        self.inner.get_subtrace_universe().map(|universe| {
            universe.iter()
                .map(|int_array| vec![int_array.get(0).unwrap(), int_array.get(1).unwrap()])
                .collect()
        })
    }
    
    /// Set the subtrace universe.
    /// 
    /// Args:
    ///     universe (list): List of pairs as lists of two integers
    fn set_subtrace_universe(&mut self, universe: Vec<Vec<i32>>) -> PyResult<()> {
        let int_arrays: Result<Vec<_>, _> = universe.into_iter()
            .map(|pair| {
                if pair.len() != 2 {
                    Err("Each pair must have exactly 2 elements")
                } else {
                    Ok(uacalc::util::int_array::IntArray::from_array(pair)
                        .map_err(|e| format!("Failed to create IntArray: {}", e))?)
                }
            })
            .collect();
        
        match int_arrays {
            Ok(arrays) => {
                self.inner.set_subtrace_universe(arrays);
                Ok(())
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Get the matrix universe.
    /// 
    /// Returns:
    ///     list or None: List of 4-tuples if set, None otherwise
    fn get_matrix_universe(&self) -> Option<Vec<Vec<i32>>> {
        self.inner.get_matrix_universe().map(|universe| {
            universe.iter()
                .map(|int_array| {
                    (0..int_array.universe_size())
                        .map(|i| int_array.get(i).unwrap())
                        .collect()
                })
                .collect()
        })
    }
    
    /// Set the matrix universe.
    /// 
    /// Args:
    ///     universe (list): List of 4-tuples as lists of four integers
    fn set_matrix_universe(&mut self, universe: Vec<Vec<i32>>) -> PyResult<()> {
        let int_arrays: Result<Vec<_>, _> = universe.into_iter()
            .map(|tuple| {
                if tuple.len() != 4 {
                    Err("Each tuple must have exactly 4 elements")
                } else {
                    Ok(uacalc::util::int_array::IntArray::from_array(tuple)
                        .map_err(|e| format!("Failed to create IntArray: {}", e))?)
                }
            })
            .collect();
        
        match int_arrays {
            Ok(arrays) => {
                self.inner.set_matrix_universe(arrays);
                Ok(())
            }
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
    
    /// Set the TCT type classification.
    /// 
    /// Args:
    ///     type_value (int): The type to set
    fn set_type(&mut self, type_value: i32) {
        self.inner.set_type(type_value);
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
    
    /// Python string representation
    fn __str__(&self) -> String {
        self.inner.to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("Subtrace({}, {}, {}, {})", 
                self.inner.first(), 
                self.inner.second(), 
                self.inner.has_involution(),
                self.inner.type_value())
    }
    
    /// Python equality comparison
    fn __eq__(&self, other: &PySubtrace) -> bool {
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
    
    /// Python comparison (less than)
    fn __lt__(&self, other: &PySubtrace) -> bool {
        self.inner < other.inner
    }
    
    /// Python comparison (less than or equal)
    fn __le__(&self, other: &PySubtrace) -> bool {
        self.inner <= other.inner
    }
    
    /// Python comparison (greater than)
    fn __gt__(&self, other: &PySubtrace) -> bool {
        self.inner > other.inner
    }
    
    /// Python comparison (greater than or equal)
    fn __ge__(&self, other: &PySubtrace) -> bool {
        self.inner >= other.inner
    }
}
