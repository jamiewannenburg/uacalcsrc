use std::fmt::{Display, Debug};
use std::sync::Arc;
use crate::alg::op::{Operation, OperationSymbol, TermOperation, AbstractOperation};
use crate::alg::SmallAlgebra;
use crate::terms::Term;

/// Implementation of a term operation.
/// 
/// This class represents the interpretation of a term in an algebra.
/// It wraps an operation that is the interpretation of the term with respect
/// to an ordered list of variables.
/// 
/// This corresponds to `org.uacalc.alg.op.TermOperationImp` in the Java codebase.
/// 
/// # Examples
/// 
/// ```ignore
/// use uacalc::alg::op::TermOperationImp;
/// use uacalc::terms::VariableImp;
/// 
/// // Create a term operation from a term and algebra
/// let term = VariableImp::new("x");
/// let variables = vec!["x".to_string()];
/// let alg = /* some algebra */;
/// let term_op = TermOperationImp::new(Box::new(term), variables, alg);
/// ```
pub struct TermOperationImp {
    /// The underlying term
    term: Box<dyn Term>,
    
    /// The ordered list of variables (without repeats)
    variables: Vec<String>,
    
    /// The algebra in which this term is interpreted
    alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
    
    /// The interpretation of the term as an operation
    interpretation: Box<dyn Operation>,
    
    /// The operation symbol (name and arity)
    symbol: OperationSymbol,
    
    /// The size of the algebra
    alg_size: i32,
}

impl TermOperationImp {
    /// Create a new TermOperationImp with a default name.
    /// 
    /// The name is derived from the term's string representation.
    /// 
    /// # Arguments
    /// * `term` - The term to interpret
    /// * `variables` - The ordered list of variable names
    /// * `alg` - The algebra for interpretation
    /// * `interpretation` - The operation that is the interpretation of the term
    /// 
    /// # Returns
    /// A new TermOperationImp instance
    /// 
    /// # Examples
    /// 
    /// ```ignore
    /// let term = VariableImp::new("x");
    /// let variables = vec!["x".to_string()];
    /// let term_op = TermOperationImp::new(Box::new(term), variables, Arc::new(alg), interpretation);
    /// ```
    pub fn new(
        term: Box<dyn Term>,
        variables: Vec<String>,
        alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
        interpretation: Box<dyn Operation>,
    ) -> Self {
        let name = format!("\"{}\"", term);
        Self::new_with_name(name, term, variables, alg, interpretation)
    }
    
    /// Create a new TermOperationImp with a custom name.
    /// 
    /// # Arguments
    /// * `name` - The name for this operation
    /// * `term` - The term to interpret
    /// * `variables` - The ordered list of variable names
    /// * `alg` - The algebra for interpretation
    /// * `interpretation` - The operation that is the interpretation of the term
    /// 
    /// # Returns
    /// A new TermOperationImp instance
    /// 
    /// # Examples
    /// 
    /// ```ignore
    /// let term = VariableImp::new("x");
    /// let variables = vec!["x".to_string()];
    /// let term_op = TermOperationImp::new_with_name(
    ///     "my_op".to_string(),
    ///     Box::new(term),
    ///     variables,
    ///     Arc::new(alg),
    ///     interpretation
    /// );
    /// ```
    pub fn new_with_name(
        name: String,
        term: Box<dyn Term>,
        variables: Vec<String>,
        alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
        interpretation: Box<dyn Operation>,
    ) -> Self {
        let arity = variables.len() as i32;
        let alg_size = alg.cardinality();
        let symbol = OperationSymbol::new(&name, arity, false);
        
        TermOperationImp {
            term,
            variables,
            alg,
            interpretation,
            symbol,
            alg_size,
        }
    }
    
    /// Create a new TermOperationImp with proper error handling.
    /// 
    /// # Arguments
    /// * `term` - The term to interpret
    /// * `variables` - The ordered list of variable names
    /// * `alg` - The algebra for interpretation
    /// * `interpretation` - The operation that is the interpretation of the term
    /// 
    /// # Returns
    /// * `Ok(TermOperationImp)` if successful
    /// * `Err(String)` if validation fails
    pub fn new_safe(
        term: Box<dyn Term>,
        variables: Vec<String>,
        alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
        interpretation: Box<dyn Operation>,
    ) -> Result<Self, String> {
        let name = format!("\"{}\"", term);
        Self::new_with_name_safe(name, term, variables, alg, interpretation)
    }
    
    /// Create a new TermOperationImp with a custom name and proper error handling.
    /// 
    /// # Arguments
    /// * `name` - The name for this operation
    /// * `term` - The term to interpret
    /// * `variables` - The ordered list of variable names
    /// * `alg` - The algebra for interpretation
    /// * `interpretation` - The operation that is the interpretation of the term
    /// 
    /// # Returns
    /// * `Ok(TermOperationImp)` if successful
    /// * `Err(String)` if validation fails
    pub fn new_with_name_safe(
        name: String,
        term: Box<dyn Term>,
        variables: Vec<String>,
        alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
        interpretation: Box<dyn Operation>,
    ) -> Result<Self, String> {
        // Validate that the interpretation has the correct arity
        let arity = variables.len() as i32;
        if interpretation.arity() != arity {
            return Err(format!(
                "Interpretation arity {} does not match variables length {}",
                interpretation.arity(),
                arity
            ));
        }
        
        Ok(Self::new_with_name(name, term, variables, alg, interpretation))
    }
}

// Implement TermOperation trait
impl TermOperation for TermOperationImp {
    fn get_term(&self) -> &dyn Term {
        &*self.term
    }
    
    fn get_ordered_variables(&self) -> Vec<String> {
        self.variables.clone()
    }
}

// Implement AbstractOperation trait
impl AbstractOperation for TermOperationImp {
    fn get_symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn get_algebra_size(&self) -> i32 {
        self.alg_size
    }
    
    fn has_value_table(&self) -> bool {
        self.interpretation.get_table().is_some()
    }
    
    fn get_value_table(&self) -> Option<&[i32]> {
        self.interpretation.get_table()
    }
    
    fn create_value_table(&mut self) -> Result<(), String> {
        // Delegate to interpretation
        // Note: This requires mutable access which we don't have
        // For now, return an error
        Err("Cannot create value table on immutable interpretation".to_string())
    }
    
    fn compute_value(&self, args: &[i32]) -> Result<i32, String> {
        self.interpretation.int_value_at(args)
    }
}

// Implement Operation trait by delegating to AbstractOperation defaults
impl Operation for TermOperationImp {
    fn arity(&self) -> i32 {
        self.default_arity()
    }
    
    fn get_set_size(&self) -> i32 {
        self.default_get_set_size()
    }
    
    fn symbol(&self) -> &OperationSymbol {
        self.default_symbol()
    }
    
    fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.interpretation.value_at(args)
    }
    
    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
        self.interpretation.value_at_arrays(args)
    }
    
    fn int_value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.interpretation.int_value_at(args)
    }
    
    fn int_value_at_horner(&self, arg: i32) -> Result<i32, String> {
        self.interpretation.int_value_at_horner(arg)
    }
    
    fn make_table(&mut self) -> Result<(), String> {
        // We can't make a table on an immutable interpretation
        Err("Cannot make table on immutable interpretation".to_string())
    }
    
    fn get_table(&self) -> Option<&[i32]> {
        self.interpretation.get_table()
    }
    
    fn get_table_force(&mut self, _make_table: bool) -> Result<&[i32], String> {
        // We can't force table creation on an immutable interpretation
        self.interpretation.get_table()
            .ok_or_else(|| "No table available".to_string())
    }
    
    fn is_table_based(&self) -> bool {
        self.interpretation.is_table_based()
    }
    
    fn is_idempotent(&self) -> Result<bool, String> {
        self.interpretation.is_idempotent()
    }
    
    fn is_associative(&self) -> Result<bool, String> {
        self.interpretation.is_associative()
    }
    
    fn is_commutative(&self) -> Result<bool, String> {
        self.interpretation.is_commutative()
    }
    
    fn is_totally_symmetric(&self) -> Result<bool, String> {
        self.interpretation.is_totally_symmetric()
    }
    
    fn is_maltsev(&self) -> Result<bool, String> {
        self.interpretation.is_maltsev()
    }
    
    fn is_total(&self) -> Result<bool, String> {
        self.interpretation.is_total()
    }
    
    fn clone_box(&self) -> Box<dyn Operation> {
        // TermOperationImp cannot derive Clone because of trait objects
        // So we manually create a new instance
        Box::new(TermOperationImp {
            term: self.term.clone_box(),
            variables: self.variables.clone(),
            alg: self.alg.clone(),
            interpretation: self.interpretation.clone_box(),
            symbol: self.symbol.clone(),
            alg_size: self.alg_size,
        })
    }
}

impl Display for TermOperationImp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.term)
    }
}

impl Debug for TermOperationImp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("TermOperationImp")
            .field("term", &format!("{}", self.term))
            .field("variables", &self.variables)
            .field("arity", &self.symbol.arity())
            .field("alg_size", &self.alg_size)
            .finish()
    }
}

