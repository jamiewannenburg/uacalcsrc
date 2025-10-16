use std::sync::Mutex;
use std::collections::HashMap;
use std::cmp::Ordering;
use std::hash::{Hash, Hasher};
use once_cell::sync::Lazy;
use num_traits::cast::ToPrimitive;

/// An operation symbol with a name and arity.
/// 
/// This struct represents an operation symbol in universal algebra,
/// containing both a string name for display and an integer arity
/// indicating the number of operands the operation takes.
#[derive(Debug, Clone)]
pub struct OperationSymbol {
    name: String,
    arity: i32,
    associative: bool,
}

// Static constants matching Java implementation
static JOIN: Lazy<OperationSymbol> = Lazy::new(|| OperationSymbol::new("join", 2, false));
static MEET: Lazy<OperationSymbol> = Lazy::new(|| OperationSymbol::new("meet", 2, false));
static PRODUCT: Lazy<OperationSymbol> = Lazy::new(|| OperationSymbol::new("prod", 2, false));
static INVERSE: Lazy<OperationSymbol> = Lazy::new(|| OperationSymbol::new("inv", 1, false));
static IDENTITY: Lazy<OperationSymbol> = Lazy::new(|| OperationSymbol::new("id", 0, false));

// Static mutable map for getOperationSymbol - thread-safe
static CURRENT_SYM_INDEX_MAP: Lazy<Mutex<HashMap<i32, i32>>> = Lazy::new(|| Mutex::new(HashMap::new()));

impl OperationSymbol {
    /// Create a new OperationSymbol with the given name and arity.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation symbol
    /// * `arity` - The arity (number of operands) of the operation
    /// * `associative` - Whether the operation is associative (only valid for binary operations)
    /// 
    /// # Panics
    /// Panics if `associative` is true but `arity` is not 2.
    pub fn new(name: &str, arity: i32, associative: bool) -> Self {
        let mut sym = OperationSymbol {
            name: name.to_string(),
            arity,
            associative: false,
        };
        sym.set_associative_panic(associative);
        sym
    }
    
    /// Create a new OperationSymbol with proper error handling.
    /// 
    /// # Arguments
    /// * `name` - The name of the operation symbol
    /// * `arity` - The arity (number of operands) of the operation
    /// * `associative` - Whether the operation is associative (only valid for binary operations)
    /// 
    /// # Returns
    /// * `Ok(OperationSymbol)` if successful
    /// * `Err(String)` if `associative` is true but `arity` is not 2
    pub fn new_safe(name: &str, arity: i32, associative: bool) -> Result<Self, String> {
        if arity < 0 {
            return Err("Arity must be non-negative".to_string());
        }
        let mut sym = OperationSymbol {
            name: name.to_string(),
            arity,
            associative: false,
        };
        sym.set_associative(associative)?;
        Ok(sym)
    }
    
    /// Get the arity of this operation symbol.
    pub fn arity(&self) -> i32 {
        self.arity
    }
    
    /// Get the name of this operation symbol.
    pub fn name(&self) -> &str {
        &self.name
    }
    
    /// Check if this operation symbol is marked as associative.
    /// 
    /// Only binary operations (arity 2) can be associative.
    pub fn is_associative(&self) -> bool {
        self.associative
    }
    
    /// Set whether this operation symbol is associative.
    /// 
    /// # Arguments
    /// * `assoc` - Whether the operation should be associative
    /// 
    /// # Returns
    /// * `Ok(())` if successful
    /// * `Err(String)` if `assoc` is true but the arity is not 2
    pub fn set_associative(&mut self, assoc: bool) -> Result<(), String> {
        if assoc && self.arity != 2 {
            return Err("Only binary terms can be associative.".to_string());
        }
        self.associative = assoc && self.arity == 2;
        Ok(())
    }
    
    /// Set whether this operation symbol is associative (panicking version for compatibility).
    /// 
    /// # Arguments
    /// * `assoc` - Whether the operation should be associative
    /// 
    /// # Panics
    /// Panics if `assoc` is true but the arity is not 2.
    pub fn set_associative_panic(&mut self, assoc: bool) {
        if assoc && self.arity != 2 {
            panic!("Only binary terms can be associative.");
        }
        self.associative = assoc && self.arity == 2;
    }
    
    /// Convert this operation symbol to a string representation.
    /// 
    /// # Arguments
    /// * `show_arity` - Whether to include the arity in the string
    /// 
    /// # Returns
    /// String representation of the operation symbol
    pub fn to_string_with_arity(&self, show_arity: bool) -> String {
        if show_arity {
            format!("{}({})", self.name, self.arity)
        } else {
            self.name.clone()
        }
    }
    
    /// Get an OperationSymbol in a uniform manner for consistent naming.
    /// 
    /// This method generates operation symbols with standardized names
    /// based on arity, ensuring that similar algebras will have consistent
    /// operation symbol naming.
    /// 
    /// # Arguments
    /// * `arity` - The arity of the operation symbol to generate
    /// 
    /// # Returns
    /// A new OperationSymbol with a generated name based on the arity
    pub fn get_operation_symbol(arity: i32) -> OperationSymbol {
        let mut map = CURRENT_SYM_INDEX_MAP.lock().unwrap();
        let index = map.entry(arity).or_insert(-1);
        *index += 1;
        let ind = *index;
        
        match arity {
            0 => OperationSymbol::new(&format!("c_{}", ind), arity, false),
            1 => OperationSymbol::new(&format!("u_{}", ind), arity, false),
            2 => OperationSymbol::new(&format!("b_{}", ind), arity, false),
            3 => OperationSymbol::new(&format!("t_{}", ind), arity, false),
            _ => OperationSymbol::new(&format!("op{}_{}", arity, ind), arity, false),
        }
    }
    
    /// Get the JOIN constant (binary operation).
    pub fn join() -> &'static OperationSymbol {
        &JOIN
    }
    
    /// Get the MEET constant (binary operation).
    pub fn meet() -> &'static OperationSymbol {
        &MEET
    }
    
    /// Get the PRODUCT constant (binary operation).
    pub fn product() -> &'static OperationSymbol {
        &PRODUCT
    }
    
    /// Get the INVERSE constant (unary operation).
    pub fn inverse() -> &'static OperationSymbol {
        &INVERSE
    }
    
    /// Get the IDENTITY constant (nullary operation).
    pub fn identity() -> &'static OperationSymbol {
        &IDENTITY
    }
}

impl std::fmt::Display for OperationSymbol {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.name)
    }
}

// Implement comparison traits to match Java's Comparable interface
impl Ord for OperationSymbol {
    fn cmp(&self, other: &Self) -> Ordering {
        // High arity operations first, then by name (ascending)
        // This matches Java's compareTo: if (arity < sym.arity()) return 1; if (arity > sym.arity()) return -1;
        match self.arity.cmp(&other.arity) {
            Ordering::Equal => self.name.cmp(&other.name),
            Ordering::Less => Ordering::Greater,    // self.arity < other.arity -> self > other
            Ordering::Greater => Ordering::Less,    // self.arity > other.arity -> self < other
        }
    }
}

impl PartialOrd for OperationSymbol {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Eq for OperationSymbol {}

impl PartialEq for OperationSymbol {
    fn eq(&self, other: &Self) -> bool {
        self.name == other.name && self.arity == other.arity
    }
}

impl Hash for OperationSymbol {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.name.hash(state);
        self.arity.hash(state);
    }
}

// Operation trait and related functionality
pub mod operation;
pub use operation::{Operation, CloneableOperation, BoxedOperation, boxed_operation};

// Abstract operation trait (Task 11)
pub mod abstract_operation;

// Concrete operation implementations  
pub mod basic_operation;
pub mod abstract_int_operation;
pub mod int_operation; 
pub mod operation_with_default_value;
pub mod operations;

// Re-exports
pub use abstract_operation::AbstractOperation; // This will be the trait
pub use basic_operation::BasicOperation; // The concrete implementation I made
pub use abstract_int_operation::AbstractIntOperation; // Task 13
pub use int_operation::IntOperation;
pub use operation_with_default_value::OperationWithDefaultValue;
pub use operations as ops; // Re-export operations module

// Tests module
#[cfg(test)]
mod operation_tests;

// Simple tests module (no Java integration)
#[cfg(test)]
mod simple_operation_tests;

// Term operation tests (Task 25)
#[cfg(test)]
mod term_operation_tests;


pub struct ParameterizedOperation {
    // TODO: Implement parameterized operation
}

// Term operation trait (Task 25)
pub mod term_operation;
pub use term_operation::TermOperation;

/// A set of OperationSymbol's representing a similarity type.
/// 
/// This struct represents a collection of operation symbols that define
/// the similarity type of an algebra. It provides methods for calculating
/// input sizes, managing arities, and various utility functions.
#[derive(Debug, Clone)]
pub struct SimilarityType {
    operation_symbols: Vec<OperationSymbol>,
    arities_map: Option<std::collections::BTreeMap<i32, i32>>,
    max_arity: Option<i32>,
}

// Static constants matching Java implementation
static LATTICE_SIMILARITY_TYPE: Lazy<SimilarityType> = Lazy::new(|| {
    let opsyms = vec![
        OperationSymbol::join().clone(),
        OperationSymbol::meet().clone(),
    ];
    SimilarityType::new(opsyms)
});

static GROUP_SIMILARITY_TYPE: Lazy<SimilarityType> = Lazy::new(|| {
    let opsyms = vec![
        OperationSymbol::product().clone(),
        OperationSymbol::inverse().clone(),
        OperationSymbol::identity().clone(),
    ];
    SimilarityType::new(opsyms)
});

impl SimilarityType {
    /// Create a new SimilarityType with the given operation symbols.
    /// 
    /// # Arguments
    /// * `op_syms` - Vector of operation symbols
    /// 
    /// # Returns
    /// A new SimilarityType instance
    pub fn new(op_syms: Vec<OperationSymbol>) -> Self {
        Self::new_with_sort(op_syms, false)
    }
    
    /// Create a new SimilarityType with the given operation symbols and optional sorting.
    /// 
    /// # Arguments
    /// * `op_syms` - Vector of operation symbols
    /// * `sort` - Whether to sort the operation symbols
    /// 
    /// # Returns
    /// A new SimilarityType instance
    pub fn new_with_sort(mut op_syms: Vec<OperationSymbol>, sort: bool) -> Self {
        if sort {
            op_syms.sort();
        }
        SimilarityType {
            operation_symbols: op_syms,
            arities_map: None,
            max_arity: None,
        }
    }
    
    /// Create a new SimilarityType with proper error handling.
    /// 
    /// # Arguments
    /// * `op_syms` - Vector of operation symbols
    /// 
    /// # Returns
    /// * `Ok(SimilarityType)` if successful
    /// * `Err(String)` if validation fails
    pub fn new_safe(op_syms: Vec<OperationSymbol>) -> Result<Self, String> {
        Ok(Self::new(op_syms))
    }
    
    /// Get the operation symbols in this similarity type.
    /// 
    /// # Returns
    /// A reference to the vector of operation symbols
    pub fn get_operation_symbols(&self) -> &Vec<OperationSymbol> {
        &self.operation_symbols
    }
    
    /// Get a sorted list of operation symbols.
    /// 
    /// The sorting is by lowest arity first, then by alphabetical order on the name.
    /// 
    /// # Returns
    /// A sorted vector of operation symbols
    pub fn get_sorted_operation_symbols(&self) -> Vec<OperationSymbol> {
        let mut sorted = self.operation_symbols.clone();
        sorted.sort();
        sorted
    }
    
    /// Calculate the computer input size for this similarity type.
    /// 
    /// If the result exceeds the maximum integer value, returns -1.
    /// If there are no operations, returns the algebra size.
    /// 
    /// # Arguments
    /// * `alg_size` - The algebra size
    /// 
    /// # Returns
    /// The input size if it fits in an i32, or -1 if it exceeds the maximum
    pub fn input_size(&self, alg_size: i32) -> i32 {
        if self.operation_symbols.is_empty() {
            return alg_size;
        }
        
        let mut input_size = num_bigint::BigInt::from(0);
        let algebra_size = num_bigint::BigInt::from(alg_size as i64);
        let max_int = num_bigint::BigInt::from(i32::MAX as i64);
        
        for sym in &self.operation_symbols {
            input_size += algebra_size.pow(sym.arity() as u32);
            if input_size >= max_int {
                return -1;
            }
        }
        
        input_size.to_i32().unwrap_or(-1)
    }
    
    /// Get a map from arity to the number of operations of that arity.
    /// 
    /// This method caches the result for performance.
    /// 
    /// # Returns
    /// A BTreeMap mapping arity to count
    pub fn get_arities_map(&mut self) -> &std::collections::BTreeMap<i32, i32> {
        if self.arities_map.is_none() {
            let mut map = std::collections::BTreeMap::new();
            let mut max = -1;
            
            for sym in &self.operation_symbols {
                let k = sym.arity();
                max = max.max(k);
                *map.entry(k).or_insert(0) += 1;
            }
            
            self.arities_map = Some(map);
            self.max_arity = Some(max);
        }
        
        self.arities_map.as_ref().unwrap()
    }
    
    /// Get the maximum arity among all operation symbols.
    /// 
    /// This method caches the result for performance.
    /// 
    /// # Returns
    /// The maximum arity, or -1 if there are no operations
    pub fn get_max_arity(&mut self) -> i32 {
        if self.max_arity.is_none() {
            self.get_arities_map(); // This will set max_arity
        }
        self.max_arity.unwrap_or(-1)
    }
    
    /// Get the LATTICE_SIMILARITY_TYPE constant.
    /// 
    /// # Returns
    /// A reference to the static lattice similarity type
    pub fn lattice_similarity_type() -> &'static SimilarityType {
        &LATTICE_SIMILARITY_TYPE
    }
    
    /// Get the GROUP_SIMILARITY_TYPE constant.
    /// 
    /// # Returns
    /// A reference to the static group similarity type
    pub fn group_similarity_type() -> &'static SimilarityType {
        &GROUP_SIMILARITY_TYPE
    }
    
    /// Generate a string representation of the arities.
    /// 
    /// # Returns
    /// A string describing the arities of operations in this similarity type
    pub fn arities_string(&mut self) -> String {
        let k = self.get_max_arity();
        let arities_map = self.get_arities_map();
        let mut parts = Vec::new();
        
        for i in (0..=k).rev() {
            if let Some(&num) = arities_map.get(&i) {
                let ary_string = match i {
                    1 => format!("unary ({})", num),
                    2 => format!("binary: ({})", num),
                    _ => format!("{}-ary ({})", i, num),
                };
                parts.push(ary_string);
            }
        }
        
        parts.join(", ")
    }
}

impl std::fmt::Display for SimilarityType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "(")?;
        for (i, sym) in self.operation_symbols.iter().enumerate() {
            if i > 0 {
                write!(f, ", ")?;
            }
            write!(f, "{}", sym)?;
        }
        write!(f, ")")
    }
}

impl PartialEq for SimilarityType {
    fn eq(&self, other: &Self) -> bool {
        if self.operation_symbols.len() != other.operation_symbols.len() {
            return false;
        }
        
        for op in &self.operation_symbols {
            if !other.operation_symbols.contains(op) {
                return false;
            }
        }
        true
    }
}

impl Eq for SimilarityType {}

impl Hash for SimilarityType {
    fn hash<H: Hasher>(&self, state: &mut H) {
        // Sort the operation symbols for consistent hashing
        let mut sorted = self.operation_symbols.clone();
        sorted.sort();
        sorted.hash(state);
    }
}

pub struct TermOperationImp {
    // TODO: Implement term operation implementation (Task 33)
}
