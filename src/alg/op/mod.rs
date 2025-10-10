use std::sync::Mutex;
use std::collections::HashMap;
use std::cmp::Ordering;
use std::hash::{Hash, Hasher};
use once_cell::sync::Lazy;

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
        match other.arity.cmp(&self.arity) {
            Ordering::Equal => self.name.cmp(&other.name),
            other => other,
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

// Placeholder structs for future implementation
pub struct Operation {
    // TODO: Implement operation structure
}

pub struct Operations {
    // TODO: Implement operations collection
}

pub struct AbstractOperation {
    // TODO: Implement abstract operation
}

pub struct AbstractIntOperation {
    // TODO: Implement abstract int operation
}

pub struct OperationWithDefaultValue {
    // TODO: Implement operation with default value
}

pub struct ParameterizedOperation {
    // TODO: Implement parameterized operation
}

pub struct SimilarityType {
    // TODO: Implement similarity type
}

pub struct TermOperation {
    // TODO: Implement term operation
}

pub struct TermOperationImp {
    // TODO: Implement term operation implementation
}
