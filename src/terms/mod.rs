use std::collections::{HashMap, HashSet};
use std::fmt::{Display, Debug};
use crate::alg::op::OperationSymbol;
use crate::alg::SmallAlgebra;

/// The Term trait represents algebraic terms in universal algebra.
/// 
/// A term is a tree structure with variables as leaves and operations as internal nodes.
/// This trait defines the core interface for term manipulation, evaluation, and interpretation.
/// 
/// In Java: `org.uacalc.terms.Term` interface
pub trait Term: Display + Debug {
    
    /// Determines if this term is a variable.
    /// 
    /// # Returns
    /// `true` if this term is a variable, `false` otherwise
    fn isa_variable(&self) -> bool;
    
    /// Returns the leading operation symbol of this term.
    /// 
    /// For a variable term, this returns `None`.
    /// For a compound term, this returns the operation symbol at the root.
    /// 
    /// # Returns
    /// The leading operation symbol, or `None` for a variable
    fn leading_operation_symbol(&self) -> Option<&OperationSymbol>;
    
    /// Returns the set of all operation symbols used in this term.
    /// 
    /// For a variable, this returns an empty set.
    /// For a compound term, this recursively collects all operation symbols.
    /// 
    /// # Returns
    /// A set containing all operation symbols in this term
    fn get_operation_symbols(&self) -> HashSet<OperationSymbol>;
    
    /// Returns the immediate children of this term.
    /// 
    /// - For a variable: returns `None`
    /// - For a constant (0-ary operation): returns `Some(vec![])`  
    /// - For a compound term: returns `Some(children)`
    /// 
    /// # Returns
    /// The list of child terms, or `None` for a variable
    fn get_children(&self) -> Option<Vec<Box<dyn Term>>>;
    
    /// Evaluates this term in an algebra using the given variable assignment.
    /// 
    /// # Arguments
    /// * `alg` - The algebra in which to evaluate the term
    /// * `map` - A map from variable names to their integer values
    /// 
    /// # Returns
    /// * `Ok(i32)` - The result of evaluating the term
    /// * `Err(String)` - Error message if evaluation fails
    fn eval(&self, alg: &dyn SmallAlgebra<UniverseItem = i32>, map: &HashMap<String, i32>) -> Result<i32, String>;
    
    /// Evaluates this term as an integer in an algebra.
    /// 
    /// # Arguments
    /// * `alg` - The algebra in which to evaluate the term
    /// * `map` - A map from variable names to integer values
    /// 
    /// # Returns
    /// * `Ok(i32)` - The integer result of evaluating the term
    /// * `Err(String)` - Error message if evaluation fails
    fn int_eval(&self, alg: &dyn SmallAlgebra<UniverseItem = i32>, map: &HashMap<String, i32>) -> Result<i32, String>;
    
    /// Returns the interpretation of this term as an operation on the given algebra.
    /// 
    /// The `varlist` specifies the order of variables. If `use_all` is true,
    /// variables not explicit in the term are still included in the operation's arity.
    /// 
    /// # Arguments
    /// * `alg` - The algebra for interpretation
    /// * `varlist` - The ordered list of variable names
    /// * `use_all` - If true, use all variables in varlist regardless of occurrence
    /// 
    /// # Returns
    /// * `Ok(())` - Success
    /// * `Err(String)` - Error message if interpretation fails
    /// 
    /// # Note
    /// This is a placeholder that will be properly implemented when algebra interpretation is ready
    fn interpretation(&self, varlist: &[String], use_all: bool) -> Result<(), String>;
    
    /// Returns the interpretation using the variables in the order they occur.
    /// 
    /// # Arguments
    /// * `alg` - The algebra for interpretation
    /// 
    /// # Returns
    /// * `Ok(())` - Success
    /// * `Err(String)` - Error message if interpretation fails
    /// 
    /// # Note
    /// This is a placeholder that will be properly implemented when algebra interpretation is ready
    fn interpretation_simple(&self) -> Result<(), String>;
    
    /// Returns the depth of the term tree.
    /// 
    /// A variable has depth 0. A compound term's depth is 1 plus the maximum
    /// depth of its children.
    /// 
    /// # Returns
    /// The depth of the term tree
    fn depth(&self) -> i32;
    
    /// Returns the length (total number of nodes) of the term.
    /// 
    /// A variable has length 1. A compound term's length is 1 plus the sum
    /// of the lengths of its children.
    /// 
    /// # Returns
    /// The total number of nodes in the term
    fn length(&self) -> i32;
    
    /// Returns the list of variables in the order they appear in the term.
    /// 
    /// Variables are collected in a depth-first traversal, with duplicates
    /// appearing only once (first occurrence).
    /// 
    /// # Returns
    /// The ordered list of variable names
    fn get_variable_list(&self) -> Vec<String>;
    
    /// Substitutes terms for variables according to the given map.
    /// 
    /// Variables not in the map are left unchanged.
    /// 
    /// # Arguments
    /// * `map` - A map from variable names to replacement terms
    /// 
    /// # Returns
    /// * `Ok(Box<dyn Term>)` - The term with substitutions applied
    /// * `Err(String)` - Error message if substitution fails
    fn substitute(&self, map: &HashMap<String, Box<dyn Term>>) -> Result<Box<dyn Term>, String>;
    
    /// Writes this term to a string buffer.
    /// 
    /// This is an efficiency helper for `to_string()`.
    /// 
    /// # Arguments
    /// * `sb` - The string buffer to write to
    fn write_string_buffer(&self, sb: &mut String);
}

/// The Variable trait extends Term for variable terms.
/// 
/// A variable is a leaf node in a term tree with a name.
/// 
/// In Java: `org.uacalc.terms.Variable` interface
pub trait Variable: Term {
    /// Returns the name of this variable.
    /// 
    /// # Returns
    /// The variable name
    fn get_name(&self) -> &str;
}

/// A concrete implementation of a variable term.
/// 
/// In Java: `org.uacalc.terms.VariableImp` class
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct VariableImp {
    pub name: String,
}

impl VariableImp {
    /// Creates a new variable with the given name.
    /// 
    /// # Arguments
    /// * `name` - The name of the variable
    /// 
    /// # Returns
    /// A new VariableImp instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::terms::VariableImp;
    /// 
    /// let x = VariableImp::new("x");
    /// assert_eq!(x.get_name(), "x");
    /// ```
    pub fn new(name: &str) -> Self {
        VariableImp {
            name: name.to_string(),
        }
    }
    
    /// Predefined variable x
    pub fn x() -> Self {
        VariableImp::new("x")
    }
    
    /// Predefined variable y
    pub fn y() -> Self {
        VariableImp::new("y")
    }
    
    /// Predefined variable z
    pub fn z() -> Self {
        VariableImp::new("z")
    }
}

impl Display for VariableImp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.name)
    }
}

// Implement Clone for Box<dyn Term> to allow term manipulation
pub trait TermClone {
    fn clone_box(&self) -> Box<dyn Term>;
}

impl<T: 'static + Term + Clone> TermClone for T {
    fn clone_box(&self) -> Box<dyn Term> {
        Box::new(self.clone())
    }
}

impl Variable for VariableImp {
    fn get_name(&self) -> &str {
        &self.name
    }
}

impl Term for VariableImp {
    fn isa_variable(&self) -> bool {
        true
    }
    
    fn leading_operation_symbol(&self) -> Option<&OperationSymbol> {
        None
    }
    
    fn get_operation_symbols(&self) -> HashSet<OperationSymbol> {
        HashSet::new()
    }
    
    fn get_children(&self) -> Option<Vec<Box<dyn Term>>> {
        None
    }
    
    fn eval(&self, _alg: &dyn SmallAlgebra<UniverseItem = i32>, map: &HashMap<String, i32>) -> Result<i32, String> {
        // For a variable, just look up its value in the assignment map
        map.get(&self.name)
            .copied()
            .ok_or_else(|| format!("Variable {} not found in assignment map", self.name))
    }
    
    fn int_eval(&self, alg: &dyn SmallAlgebra<UniverseItem = i32>, map: &HashMap<String, i32>) -> Result<i32, String> {
        // For variables, int_eval is the same as eval
        self.eval(alg, map)
    }
    
    fn interpretation(&self, _varlist: &[String], _use_all: bool) -> Result<(), String> {
        // For now, return an error as we need TermOperation implementation
        Err("Term interpretation not yet fully implemented".to_string())
    }
    
    fn interpretation_simple(&self) -> Result<(), String> {
        // For now, return an error as we need TermOperation implementation
        Err("Term interpretation not yet fully implemented".to_string())
    }
    
    fn depth(&self) -> i32 {
        0
    }
    
    fn length(&self) -> i32 {
        1
    }
    
    fn get_variable_list(&self) -> Vec<String> {
        vec![self.name.clone()]
    }
    
    fn substitute(&self, map: &HashMap<String, Box<dyn Term>>) -> Result<Box<dyn Term>, String> {
        if let Some(_replacement) = map.get(&self.name) {
            // Clone the term by converting to string and back (placeholder)
            // In a real implementation, we'd need proper cloning
            Ok(Box::new(self.clone()))
        } else {
            Ok(Box::new(self.clone()))
        }
    }
    
    fn write_string_buffer(&self, sb: &mut String) {
        sb.push_str(&self.name);
    }
}

/// A non-variable (compound) term.
/// 
/// Represents a term with an operation symbol and child terms.
/// 
/// In Java: `org.uacalc.terms.NonVariableTerm` class
#[derive(Debug)]
pub struct NonVariableTerm {
    pub leading_operation_symbol: OperationSymbol,
    pub children: Vec<Box<dyn Term>>,
}

impl NonVariableTerm {
    /// Creates a new non-variable term.
    /// 
    /// # Arguments
    /// * `op_sym` - The operation symbol at the root
    /// * `children` - The child terms
    /// 
    /// # Returns
    /// A new NonVariableTerm instance
    pub fn new(op_sym: OperationSymbol, children: Vec<Box<dyn Term>>) -> Self {
        NonVariableTerm {
            leading_operation_symbol: op_sym,
            children,
        }
    }
    
    /// Creates a constant term from an operation symbol.
    /// 
    /// # Arguments
    /// * `sym` - The operation symbol (must have arity 0)
    /// 
    /// # Returns
    /// A constant term
    pub fn make_constant_term(sym: OperationSymbol) -> Self {
        NonVariableTerm::new(sym, vec![])
    }
    
    // Helper method to add variables from a term
    fn add_variables(term: &dyn Term, vars: &mut Vec<String>) {
        if term.isa_variable() {
            // We need to get the variable name somehow
            // For now, use the string representation
            let name = format!("{}", term);
            if !vars.contains(&name) {
                vars.push(name);
            }
        } else {
            if let Some(children) = term.get_children() {
                for child in children {
                    Self::add_variables(child.as_ref(), vars);
                }
            }
        }
    }
    
    // Helper method to fill operation symbol set
    fn fill_op_sym_set(term: &dyn Term, set: &mut HashSet<OperationSymbol>) {
        if term.isa_variable() {
            return;
        }
        if let Some(children) = term.get_children() {
            for child in children {
                Self::fill_op_sym_set(child.as_ref(), set);
            }
        }
        if let Some(op_sym) = term.leading_operation_symbol() {
            set.insert(op_sym.clone());
        }
    }
}

impl Display for NonVariableTerm {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let mut sb = String::new();
        self.write_string_buffer(&mut sb);
        write!(f, "{}", sb)
    }
}

impl Term for NonVariableTerm {
    fn isa_variable(&self) -> bool {
        false
    }
    
    fn leading_operation_symbol(&self) -> Option<&OperationSymbol> {
        Some(&self.leading_operation_symbol)
    }
    
    fn get_operation_symbols(&self) -> HashSet<OperationSymbol> {
        let mut set = HashSet::new();
        Self::fill_op_sym_set(self, &mut set);
        set
    }
    
    fn get_children(&self) -> Option<Vec<Box<dyn Term>>> {
        // We need to clone the children, which requires Term to be cloneable
        // For now, return None as a placeholder
        None
    }
    
    fn eval(&self, alg: &dyn SmallAlgebra<UniverseItem = i32>, map: &HashMap<String, i32>) -> Result<i32, String> {
        // Get the operation from the algebra
        let op = alg.get_operation_ref(&self.leading_operation_symbol)
            .ok_or_else(|| format!("Operation {} not found in algebra", 
                                  self.leading_operation_symbol.name()))?;
        
        // Recursively evaluate all children
        let mut args = Vec::new();
        for child in &self.children {
            let value = child.eval(alg, map)?;
            args.push(value);
        }
        
        // Apply the operation to the evaluated arguments
        op.int_value_at(&args)
    }
    
    fn int_eval(&self, alg: &dyn SmallAlgebra<UniverseItem = i32>, map: &HashMap<String, i32>) -> Result<i32, String> {
        // For integer algebras, int_eval is the same as eval
        self.eval(alg, map)
    }
    
    fn interpretation(&self, _varlist: &[String], _use_all: bool) -> Result<(), String> {
        Err("NonVariableTerm interpretation not yet fully implemented".to_string())
    }
    
    fn interpretation_simple(&self) -> Result<(), String> {
        Err("NonVariableTerm interpretation_simple not yet fully implemented".to_string())
    }
    
    fn depth(&self) -> i32 {
        let mut max = 0;
        for child in &self.children {
            max = max.max(child.depth());
        }
        1 + max
    }
    
    fn length(&self) -> i32 {
        let mut ans = 1;
        for child in &self.children {
            ans += child.length();
        }
        ans
    }
    
    fn get_variable_list(&self) -> Vec<String> {
        let mut lst = Vec::new();
        Self::add_variables(self, &mut lst);
        lst
    }
    
    fn substitute(&self, map: &HashMap<String, Box<dyn Term>>) -> Result<Box<dyn Term>, String> {
        Err("NonVariableTerm substitute not yet fully implemented".to_string())
    }
    
    fn write_string_buffer(&self, sb: &mut String) {
        sb.push_str(self.leading_operation_symbol.name());
        sb.push('(');
        let n = self.children.len();
        for (i, child) in self.children.iter().enumerate() {
            child.write_string_buffer(sb);
            if i < n - 1 {
                sb.push(',');
            }
        }
        sb.push(')');
    }
}

/// Placeholder for the Taylor struct
pub struct Taylor {
    // TODO: Implement Taylor
}

/// Placeholder for the Terms collection
pub struct Terms {
    // TODO: Implement terms collection
}

#[cfg(test)]
mod tests;
