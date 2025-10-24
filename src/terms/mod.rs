use std::collections::{HashMap, HashSet};
use std::fmt::{Display, Debug};
use std::sync::Arc;
use crate::alg::op::{OperationSymbol, Operation, TermOperation, TermOperationImp, operations};
use crate::alg::SmallAlgebra;

/// The Term trait represents algebraic terms in universal algebra.
/// 
/// A term is a tree structure with variables as leaves and operations as internal nodes.
/// This trait defines the core interface for term manipulation, evaluation, and interpretation.
/// 
/// In Java: `org.uacalc.terms.Term` interface
pub trait Term: Display + Debug + Send + Sync {
    
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
    /// * `Ok(Box<dyn Operation>)` - The operation that interprets this term
    /// * `Err(String)` - Error message if interpretation fails
    fn interpretation(
        &self,
        alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
        varlist: &[String],
        use_all: bool,
    ) -> Result<Box<dyn Operation>, String>;
    
    /// Returns the interpretation using the variables in the order they occur.
    /// 
    /// # Arguments
    /// * `alg` - The algebra for interpretation
    /// 
    /// # Returns
    /// * `Ok(Box<dyn TermOperation>)` - The term operation that interprets this term
    /// * `Err(String)` - Error message if interpretation fails
    fn interpretation_simple(
        &self,
        alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
    ) -> Result<Box<dyn TermOperation>, String>;
    
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
    
    /// Clone this term into a new boxed trait object.
    /// 
    /// This allows cloning of trait objects by delegating to the concrete type's
    /// Clone implementation. This is necessary because `Box<dyn Term>` cannot
    /// automatically implement Clone.
    /// 
    /// # Returns
    /// A new boxed copy of this term
    fn clone_box(&self) -> Box<dyn Term>;
    
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
    /// use uacalc::terms::{VariableImp, Variable};
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
    
    fn interpretation(
        &self,
        alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
        varlist: &[String],
        _use_all: bool,
    ) -> Result<Box<dyn Operation>, String> {
        // Find this variable's index in the varlist
        let index = varlist.iter().position(|v| v == &self.name)
            .ok_or_else(|| format!("Variable {} not found in varlist", self.name))?;
        
        // Create a projection operation that returns the i-th argument
        let arity = varlist.len() as i32;
        let alg_size = alg.cardinality();
        let name = format!("Op_{}", self.name);
        let symbol = OperationSymbol::new(&name, arity, false);
        
        // Build value table for projection operation
        // For projection, the value at args is just args[index]
        let table_size = (alg_size as usize).pow(arity as u32);
        let mut table = Vec::with_capacity(table_size);
        
        use crate::util::horner;
        for k in 0..table_size {
            let args = horner::horner_inv_same_size(k as i32, alg_size, arity as usize);
            table.push(args[index]);
        }
        
        operations::make_int_operation(symbol, alg_size, table)
    }
    
    fn interpretation_simple(
        &self,
        alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
    ) -> Result<Box<dyn TermOperation>, String> {
        let varlist = self.get_variable_list();
        let term: Box<dyn Term> = Box::new(self.clone());
        let interpretation = self.interpretation(alg.clone(), &varlist, true)?;
        Ok(Box::new(TermOperationImp::new(term, varlist, alg, interpretation)))
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
        if let Some(replacement) = map.get(&self.name) {
            // Clone the replacement term
            Ok(replacement.clone_box())
        } else {
            // No replacement, return clone of self
            Ok(Box::new(self.clone()))
        }
    }
    
    fn clone_box(&self) -> Box<dyn Term> {
        Box::new(self.clone())
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

impl Clone for NonVariableTerm {
    fn clone(&self) -> Self {
        NonVariableTerm {
            leading_operation_symbol: self.leading_operation_symbol.clone(),
            children: self.children.iter()
                .map(|child| child.clone_box())
                .collect(),
        }
    }
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
        // Clone each child using clone_box()
        Some(self.children.iter()
            .map(|child| child.clone_box())
            .collect())
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
    
    fn interpretation(
        &self,
        alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
        varlist: &[String],
        use_all: bool,
    ) -> Result<Box<dyn Operation>, String> {
        // Get the term's variable list
        let term_var_list = self.get_variable_list();
        
        // Validate that varlist contains all variables in the term
        for var in &term_var_list {
            if !varlist.contains(var) {
                return Err(format!("varlist must have all the variables of the term; missing: {}", var));
            }
        }
        
        // Determine the arity based on use_all flag
        let arity = if use_all {
            varlist.len()
        } else {
            term_var_list.len()
        } as i32;
        
        // Build the actual variable list to use
        let ans_var_list: Vec<String> = if use_all {
            varlist.to_vec()
        } else {
            varlist.iter()
                .filter(|v| term_var_list.contains(v))
                .cloned()
                .collect()
        };
        
        let alg_size = alg.cardinality();
        let symbol = OperationSymbol::new(&format!("{}", self), arity, false);
        
        // Build value table by evaluating the term for all possible argument combinations
        let table_size = (alg_size as usize).pow(arity as u32);
        let mut table = Vec::with_capacity(table_size);
        
        use crate::util::horner;
        for k in 0..table_size {
            let args = horner::horner_inv_same_size(k as i32, alg_size, arity as usize);
            
            // Build variable assignment map
            let mut var_map = HashMap::new();
            for (i, var) in ans_var_list.iter().enumerate() {
                var_map.insert(var.clone(), args[i]);
            }
            
            // Evaluate the term with this assignment
            let value = self.eval(&*alg, &var_map)?;
            table.push(value);
        }
        
        operations::make_int_operation(symbol, alg_size, table)
    }
    
    fn interpretation_simple(
        &self,
        alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
    ) -> Result<Box<dyn TermOperation>, String> {
        let varlist = self.get_variable_list();
        // Clone this term into a Box
        let term: Box<dyn Term> = self.clone_box();
        let interpretation = self.interpretation(alg.clone(), &varlist, true)?;
        Ok(Box::new(TermOperationImp::new(term, varlist, alg, interpretation)))
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
        // Recursively substitute in all children
        let new_children: Vec<Box<dyn Term>> = self.children
            .iter()
            .map(|child| child.substitute(map))
            .collect::<Result<Vec<_>, _>>()?;
        
        // Create new term with substituted children
        Ok(Box::new(NonVariableTerm {
            leading_operation_symbol: self.leading_operation_symbol.clone(),
            children: new_children,
        }))
    }
    
    fn clone_box(&self) -> Box<dyn Term> {
        Box::new(self.clone())
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

/// Taylor term analyzer for checking Markovic-McKenzie-Siggers term properties.
/// 
/// This struct helps determine if a term in a language can be a Markovic-McKenzie-Siggers term,
/// which is an idempotent term satisfying specific equations.
/// 
/// In Java: `org.uacalc.terms.Taylor`
#[derive(Debug)]
pub struct Taylor {
    pub taylor_term: Box<dyn Term>,
    pub arity: i32,
    pub eqs: Option<Vec<crate::eq::Equation>>,
    pub inteqs: Vec<Vec<crate::util::int_array::IntArray>>,
    root_map: std::collections::HashMap<crate::util::int_array::IntArray, crate::util::int_array::IntArray>,
}

impl Clone for Taylor {
    fn clone(&self) -> Self {
        Taylor {
            taylor_term: self.taylor_term.clone_box(),
            arity: self.arity,
            eqs: self.eqs.clone(),
            inteqs: self.inteqs.clone(),
            root_map: self.root_map.clone(),
        }
    }
}

impl Taylor {
    /// Create a new Taylor analyzer from a term and equations.
    /// 
    /// # Arguments
    /// * `taylor_term` - The Taylor term
    /// * `eqs` - The list of equations
    /// 
    /// # Returns
    /// A new Taylor instance
    pub fn new(taylor_term: Box<dyn Term>, eqs: Vec<crate::eq::Equation>) -> Self {
        let arity = taylor_term.leading_operation_symbol()
            .expect("Taylor term must have an operation symbol")
            .arity();
        
        let mut taylor = Taylor {
            taylor_term,
            arity,
            eqs: Some(eqs.clone()),
            inteqs: Vec::new(),
            root_map: std::collections::HashMap::new(),
        };
        
        taylor.make_root_map_from_eqs(&eqs);
        taylor
    }
    
    /// Create a new Taylor analyzer from an operation symbol and integer equations.
    /// 
    /// # Arguments
    /// * `sym` - The operation symbol
    /// * `inteqs` - The list of equation pairs (each equation is a pair of IntArrays)
    /// 
    /// # Returns
    /// A new Taylor instance
    pub fn new_with_inteqs(sym: OperationSymbol, inteqs: Vec<Vec<crate::util::int_array::IntArray>>) -> Self {
        let arity = sym.arity();
        let mut vars: Vec<Box<dyn Term>> = Vec::new();
        for i in 0..arity {
            vars.push(Box::new(VariableImp::new(&format!("x_{}", i))));
        }
        let taylor_term = Box::new(NonVariableTerm::new(sym, vars));
        
        let mut taylor = Taylor {
            taylor_term,
            arity,
            eqs: None,
            inteqs: inteqs.clone(),
            root_map: std::collections::HashMap::new(),
        };
        
        taylor.make_root_map(&inteqs);
        taylor
    }
    
    /// Create a new Taylor analyzer from arity and integer equations.
    /// 
    /// # Arguments
    /// * `arity` - The arity of the operation
    /// * `inteqs` - The list of equation pairs
    /// 
    /// # Returns
    /// A new Taylor instance
    pub fn new_with_arity(arity: i32, inteqs: Vec<Vec<crate::util::int_array::IntArray>>) -> Self {
        Self::new_with_inteqs(OperationSymbol::new("f", arity, false), inteqs)
    }
    
    /// Get the Markovic-McKenzie term (singleton).
    /// 
    /// This is a static factory method that returns the standard Markovic-McKenzie term.
    /// 
    /// # Returns
    /// A Taylor instance representing the Markovic-McKenzie term
    pub fn markovic_mckenzie_term() -> Self {
        use crate::util::int_array::IntArray;
        
        let mut eqs = Vec::new();
        
        let mut eq = Vec::new();
        eq.push(IntArray::from_array(vec![1, 0, 0, 0]).unwrap());
        eq.push(IntArray::from_array(vec![0, 0, 1, 1]).unwrap());
        eqs.push(eq);
        
        let mut eq = Vec::new();
        eq.push(IntArray::from_array(vec![0, 0, 1, 0]).unwrap());
        eq.push(IntArray::from_array(vec![0, 1, 0, 0]).unwrap());
        eqs.push(eq);
        
        Self::new_with_inteqs(OperationSymbol::new("mm", 4, false), eqs)
    }
    
    /// Get the Siggers term (singleton).
    /// 
    /// This is a static factory method that returns the standard Siggers term.
    /// 
    /// # Returns
    /// A Taylor instance representing the Siggers term
    pub fn siggers_term() -> Self {
        use crate::util::int_array::IntArray;
        
        let mut eqs = Vec::new();
        
        let mut eq = Vec::new();
        eq.push(IntArray::from_array(vec![1, 1, 0, 0, 0, 0]).unwrap());
        eq.push(IntArray::from_array(vec![0, 0, 1, 0, 1, 0]).unwrap());
        eqs.push(eq);
        
        let mut eq = Vec::new();
        eq.push(IntArray::from_array(vec![0, 0, 0, 0, 1, 1]).unwrap());
        eq.push(IntArray::from_array(vec![0, 1, 0, 1, 0, 0]).unwrap());
        eqs.push(eq);
        
        Self::new_with_inteqs(OperationSymbol::new("s", 6, false), eqs)
    }
    
    /// Find the canonical form of a term.
    /// 
    /// This reduces via idempotence and chooses the lexicographic order.
    /// 
    /// # Arguments
    /// * `t` - The term to canonicalize
    /// 
    /// # Returns
    /// The canonical form of the term
    pub fn canonical_form(&self, t: &dyn Term) -> Box<dyn Term> {
        if t.isa_variable() {
            return t.clone_box();
        }
        
        let children = t.get_children().unwrap_or_default();
        let mut canonical_children: Vec<Box<dyn Term>> = Vec::new();
        for child in children {
            canonical_children.push(self.canonical_form(child.as_ref()));
        }
        
        let mut reps: Vec<Box<dyn Term>> = Vec::new();
        let mut map: std::collections::HashMap<String, usize> = std::collections::HashMap::new();
        let mut current = 0;
        
        for child in &canonical_children {
            let child_str = format!("{}", child);
            if !map.contains_key(&child_str) {
                map.insert(child_str, current);
                reps.push(child.clone_box());
                current += 1;
                if current > 2 {
                    return Box::new(NonVariableTerm::new(
                        self.taylor_term.leading_operation_symbol().unwrap().clone(),
                        canonical_children,
                    ));
                }
            }
        }
        
        if current == 1 {
            return canonical_children[0].clone_box();
        }
        
        let (small_term, big_term) = if Taylor::lexicographically_compare_terms(reps[0].as_ref(), reps[1].as_ref()) < 0 {
            (reps[0].clone_box(), reps[1].clone_box())
        } else {
            (reps[1].clone_box(), reps[0].clone_box())
        };
        
        let mut foo = vec![0; self.arity as usize];
        for (i, child) in canonical_children.iter().enumerate() {
            let child_str = format!("{}", child);
            let small_str = format!("{}", small_term);
            if child_str == small_str {
                foo[i] = 0;
            } else {
                foo[i] = 1;
            }
        }
        
        use crate::util::int_array::IntArray;
        let root = self.find_root(&IntArray::from_array(foo).unwrap());
        
        if self.all_equal(&root, 0) {
            return small_term;
        }
        if self.all_equal(&root, 1) {
            return big_term;
        }
        
        let mut mod_children: Vec<Box<dyn Term>> = Vec::new();
        for i in 0..self.arity as usize {
            use crate::util::int_array::IntArrayTrait;
            if root.get(i).unwrap_or(0) == 0 {
                mod_children.push(small_term.clone_box());
            } else {
                mod_children.push(big_term.clone_box());
            }
        }
        
        Box::new(NonVariableTerm::new(
            self.taylor_term.leading_operation_symbol().unwrap().clone(),
            mod_children,
        ))
    }
    
    /// Find a term which interprets the given Taylor term.
    /// 
    /// # Arguments
    /// * `g` - The target Taylor term to interpret
    /// * `level` - The depth level to search
    /// 
    /// # Returns
    /// The interpreting term if found, None otherwise
    pub fn interprets(&self, g: &Taylor, level: i32) -> Option<Box<dyn Term>> {
        let g_arity = g.arity;
        let inteqs = &g.inteqs;
        
        let mut pow = 1;
        for _ in 0..level {
            pow *= self.arity;
        }
        
        let mut seq = vec![0; pow as usize];
        use crate::util::sequence_generator::SequenceGenerator;
        use crate::util::array_incrementor::ArrayIncrementor;
        
        let mut c: i64 = 0;
        loop {
            // Create incrementor, increment, then drop it so we can read seq
            let has_next = {
                let mut inc = SequenceGenerator::sequence_incrementor(&mut seq, g_arity - 1);
                inc.increment()
            };
            
            if !has_next {
                break;
            }
            
            if c % 1000000 == 0 {
                println!("c = {}", c);
            }
            c += 1;
            
            let mut ok = true;
            for eq in inteqs {
                use crate::util::int_array::IntArrayTrait;
                let side = eq[0].as_slice();
                let mut arr = vec![0; pow as usize];
                for i in 0..pow as usize {
                    arr[i] = side[seq[i] as usize];
                }
                let left = self.canonical_form(self.term_from_array(&arr).as_ref());
                
                let side = eq[1].as_slice();
                for i in 0..pow as usize {
                    arr[i] = side[seq[i] as usize];
                }
                let rt = self.canonical_form(self.term_from_array(&arr).as_ref());
                
                if format!("{}", rt) != format!("{}", left) {
                    ok = false;
                    break;
                }
            }
            
            if ok {
                use crate::util::array_string::to_string;
                println!("this works: {}", to_string(&seq));
                return None;
            }
        }
        
        None
    }
    
    /// Create a term from an array of variable indices.
    /// 
    /// # Arguments
    /// * `arr` - The array of variable indices (0 for x, 1 for y)
    /// 
    /// # Returns
    /// The term represented by the array
    pub fn term_from_array(&self, arr: &[i32]) -> Box<dyn Term> {
        self.term_from_array_range(arr, 0, arr.len())
    }
    
    /// Create a term from a range in an array.
    /// 
    /// # Arguments
    /// * `arr` - The array of variable indices
    /// * `start` - The starting index
    /// * `len` - The length of the range
    /// 
    /// # Returns
    /// The term represented by the array range
    pub fn term_from_array_range(&self, arr: &[i32], start: usize, len: usize) -> Box<dyn Term> {
        if len == 1 {
            if arr[start] == 0 {
                return Box::new(VariableImp::x());
            }
            return Box::new(VariableImp::y());
        }
        
        let len2 = len / self.arity as usize;
        let mut lst: Vec<Box<dyn Term>> = Vec::new();
        for i in 0..self.arity as usize {
            lst.push(self.term_from_array_range(arr, start + i * len2, len2));
        }
        
        Box::new(NonVariableTerm::new(
            self.taylor_term.leading_operation_symbol().unwrap().clone(),
            lst,
        ))
    }
    
    /// Make a balanced Taylor term.
    /// 
    /// # Arguments
    /// * `f` - The operation symbol
    /// * `depth` - The depth of the term (at least 1)
    /// * `var_list` - The list of variables (length should be k^depth)
    /// 
    /// # Returns
    /// The balanced Taylor term
    pub fn make_balanced_taylor_term(&self, f: &OperationSymbol, depth: i32, var_list: &[VariableImp]) -> Box<dyn Term> {
        self.balanced_tt(f, depth, var_list, 0)
    }
    
    /// Lexicographically compare two terms.
    /// 
    /// # Arguments
    /// * `s` - The first term
    /// * `t` - The second term
    /// 
    /// # Returns
    /// * `-1` if s < t
    /// * `0` if s == t
    /// * `1` if s > t
    pub fn lexicographically_compare_terms(s: &dyn Term, t: &dyn Term) -> i32 {
        let s_str = format!("{}", s);
        let t_str = format!("{}", t);
        if s_str == t_str {
            return 0;
        }
        
        if s.depth() < t.depth() {
            return -1;
        }
        if t.depth() < s.depth() {
            return 1;
        }
        
        if s.isa_variable() {
            // Both are variables
            if s_str == "x" {
                return -1;
            }
            return 1;
        }
        
        let s_children = s.get_children().unwrap_or_default();
        let t_children = t.get_children().unwrap_or_default();
        
        for i in 0..s_children.len().min(t_children.len()) {
            let c = Taylor::lexicographically_compare_terms(s_children[i].as_ref(), t_children[i].as_ref());
            if c < 0 {
                return -1;
            }
            if c > 0 {
                return 1;
            }
        }
        
        0
    }
    
    /// Lexicographically compare two IntArrays (static version).
    /// 
    /// # Arguments
    /// * `a` - The first IntArray
    /// * `b` - The second IntArray
    /// 
    /// # Returns
    /// * `-1` if a < b
    /// * `0` if a == b
    /// * `1` if a > b
    pub fn lexicographically_compare_int_arrays(a: &crate::util::int_array::IntArray, b: &crate::util::int_array::IntArray) -> i32 {
        use crate::util::int_array::IntArrayTrait;
        Self::lexicographically_compare_arrays(a.as_slice(), b.as_slice())
    }
    
    /// Lexicographically compare two arrays (static version).
    /// 
    /// # Arguments
    /// * `a` - The first array
    /// * `b` - The second array
    /// 
    /// # Returns
    /// * `-1` if a < b
    /// * `0` if a == b
    /// * `1` if a > b
    pub fn lexicographically_compare_arrays(a: &[i32], b: &[i32]) -> i32 {
        if a.len() != b.len() {
            panic!("Arrays not of the same size");
        }
        
        for i in 0..a.len() {
            if a[i] < b[i] {
                return -1;
            }
            if a[i] > b[i] {
                return 1;
            }
        }
        
        0
    }
    
    /// Get the arity of this Taylor term.
    /// 
    /// # Returns
    /// The arity
    pub fn arity(&self) -> i32 {
        self.arity
    }
    
    /// Get the integer equations.
    /// 
    /// # Returns
    /// The list of integer equation pairs
    pub fn inteqs(&self) -> &Vec<Vec<crate::util::int_array::IntArray>> {
        &self.inteqs
    }
    
    /// Get the equations.
    /// 
    /// # Returns
    /// The list of equations if available
    pub fn equations(&self) -> Option<&Vec<crate::eq::Equation>> {
        self.eqs.as_ref()
    }
    
    // Private helper methods
    
    fn make_root_map_from_eqs(&mut self, _eqs: &[crate::eq::Equation]) {
        // TODO: Implement this method if needed
        // The Java version has this as TODO as well
    }
    
    fn make_root_map(&mut self, inteqs: &[Vec<crate::util::int_array::IntArray>]) {
        for eq in inteqs {
            let r0 = self.find_root(&eq[0]);
            let r1 = self.find_root(&eq[1]);
            
            if Self::lexicographically_compare_int_arrays(&r0, &r1) < 0 {
                if self.all_equal(&r1, 1) {
                    self.root_map.insert(r0.clone(), r1.clone());
                } else {
                    self.root_map.insert(r1.clone(), r0.clone());
                }
            } else if Self::lexicographically_compare_int_arrays(&r0, &r1) > 0 {
                if self.all_equal(&r0, 1) {
                    self.root_map.insert(r1.clone(), r0.clone());
                } else {
                    self.root_map.insert(r0.clone(), r1.clone());
                }
            }
            
            let r0 = self.find_root(&self.complement(&eq[0]));
            let r1 = self.find_root(&self.complement(&eq[1]));
            
            if Self::lexicographically_compare_int_arrays(&r0, &r1) < 0 {
                if self.all_equal(&r1, 1) {
                    self.root_map.insert(r0.clone(), r1.clone());
                } else {
                    self.root_map.insert(r1.clone(), r0.clone());
                }
            } else if Self::lexicographically_compare_int_arrays(&r0, &r1) > 0 {
                if self.all_equal(&r0, 1) {
                    self.root_map.insert(r1.clone(), r0.clone());
                } else {
                    self.root_map.insert(r0.clone(), r1.clone());
                }
            }
        }
    }
    
    fn all_equal(&self, ia: &crate::util::int_array::IntArray, value: i32) -> bool {
        use crate::util::int_array::IntArrayTrait;
        for i in 0..self.arity as usize {
            if let Some(v) = ia.get(i) {
                if v != value {
                    return false;
                }
            } else {
                return false;
            }
        }
        true
    }
    
    fn complement(&self, ia: &crate::util::int_array::IntArray) -> crate::util::int_array::IntArray {
        use crate::util::int_array::{IntArray, IntArrayTrait};
        let n = ia.universe_size();
        let mut arr = vec![0; n];
        for i in 0..n {
            if ia.get(i).unwrap_or(0) == 0 {
                arr[i] = 1;
            } else {
                arr[i] = 0;
            }
        }
        IntArray::from_array(arr).unwrap()
    }
    
    fn find_root(&self, ia: &crate::util::int_array::IntArray) -> crate::util::int_array::IntArray {
        if let Some(next) = self.root_map.get(ia) {
            let r = self.find_root(next);
            // Note: We can't insert into root_map here due to immutable borrow
            r
        } else {
            ia.clone()
        }
    }
    
    fn balanced_tt(&self, f: &OperationSymbol, depth: i32, var_list: &[VariableImp], start: usize) -> Box<dyn Term> {
        let k = f.arity() as usize;
        let factor = var_list.len() / k;
        
        if depth == 1 {
            let mut lst: Vec<Box<dyn Term>> = Vec::new();
            for i in 0..k {
                lst.push(Box::new(var_list[start + i].clone()));
            }
            return Box::new(NonVariableTerm::new(f.clone(), lst));
        }
        
        let mut lst: Vec<Box<dyn Term>> = Vec::new();
        let mut current = start;
        for _ in 0..k {
            lst.push(self.balanced_tt(f, depth - 1, var_list, current));
            current += factor;
        }
        
        Box::new(NonVariableTerm::new(f.clone(), lst))
    }
}

// =============================================================================
// Terms Module - Utility functions for term manipulation
// =============================================================================

/// Parse a string representation into a Term.
/// 
/// This function converts a string like "f(x,y)" or "x" into a Term object.
/// The string should follow these rules:
/// - Variable names must start with a letter and contain no spaces, commas, or parentheses
/// - Operation names follow the same rules as variable names
/// - Operations are written as `name(arg1,arg2,...,argn)`
/// - Nested operations are supported: `f(g(x),y)`
/// 
/// # Arguments
/// * `str` - The string representation of the term
/// 
/// # Returns
/// * `Ok(Box<dyn Term>)` - The parsed term
/// * `Err(String)` - Error message if parsing fails
/// 
/// # Examples
/// ```
/// use uacalc::terms;
/// 
/// // Parse a variable
/// let x = terms::string_to_term("x").unwrap();
/// assert_eq!(x.to_string(), "x");
/// 
/// // Parse a compound term
/// let term = terms::string_to_term("f(x,y)").unwrap();
/// assert_eq!(term.to_string(), "f(x,y)");
/// 
/// // Parse a nested term
/// let nested = terms::string_to_term("f(g(x),y)").unwrap();
/// assert_eq!(nested.to_string(), "f(g(x),y)");
/// ```
pub fn string_to_term(str: &str) -> Result<Box<dyn Term>, String> {
    if str.is_empty() {
        return Err("empty string".to_string());
    }
    
    let str = str.trim();
    if str.is_empty() {
        return Err("empty string".to_string());
    }
    
    let str = adjust_parens(str);
    
    // Split on first '('
    if let Some(paren_pos) = str.find('(') {
        let op_name = &str[..paren_pos];
        let rest = &str[paren_pos + 1..];
        
        // Validate operation name
        if !is_valid_op_name_string(op_name) {
            return Err(format!("The string {} cannot be made into a function symbol.", op_name));
        }
        
        // Remove trailing ')' if present
        let args_string = if rest.ends_with(')') {
            &rest[..rest.len() - 1]
        } else {
            rest
        };
        
        // Parse arguments
        let arg_strings = get_argument_strings(args_string);
        let arity = arg_strings.len();
        let sym = OperationSymbol::new(op_name, arity as i32, false);
        
        // Recursively parse each argument
        let mut children: Vec<Box<dyn Term>> = Vec::new();
        for arg_string in arg_strings {
            children.push(string_to_term(&arg_string)?);
        }
        
        Ok(Box::new(NonVariableTerm::new(sym, children)))
    } else {
        // No '(' means it's a variable
        if is_valid_var_string(&str) {
            Ok(Box::new(VariableImp::new(&str)))
        } else {
            Err(format!("The string {} cannot be made into a variable.", str))
        }
    }
}

/// Validate if a string can be a variable name.
/// 
/// A valid variable name must:
/// - Not be empty
/// - Start with a letter (A-Z or a-z)
/// - Not contain whitespace, commas, or parentheses
/// 
/// # Arguments
/// * `str` - The string to validate
/// 
/// # Returns
/// `true` if the string is a valid variable name, `false` otherwise
/// 
/// # Examples
/// ```
/// use uacalc::terms;
/// 
/// assert!(terms::is_valid_var_string("x"));
/// assert!(terms::is_valid_var_string("var1"));
/// assert!(terms::is_valid_var_string("myVar"));
/// assert!(!terms::is_valid_var_string(""));
/// assert!(!terms::is_valid_var_string("1x"));
/// assert!(!terms::is_valid_var_string("x,y"));
/// assert!(!terms::is_valid_var_string("x("));
/// ```
pub fn is_valid_var_string(str: &str) -> bool {
    if str.is_empty() {
        return false;
    }
    
    // Check first character is a letter
    let first_char = str.chars().next().unwrap();
    if !first_char.is_ascii_alphabetic() {
        return false;
    }
    
    // Check for invalid characters
    if str.contains(char::is_whitespace) {
        return false;
    }
    if str.contains(',') {
        return false;
    }
    if str.contains('(') {
        return false;
    }
    if str.contains(')') {
        return false;
    }
    
    true
}

/// Validate if a string can be an operation name.
/// 
/// Uses the same validation rules as variable names.
/// 
/// # Arguments
/// * `str` - The string to validate
/// 
/// # Returns
/// `true` if the string is a valid operation name, `false` otherwise
/// 
/// # Examples
/// ```
/// use uacalc::terms;
/// 
/// assert!(terms::is_valid_op_name_string("f"));
/// assert!(terms::is_valid_op_name_string("add"));
/// assert!(!terms::is_valid_op_name_string(""));
/// assert!(!terms::is_valid_op_name_string("1f"));
/// ```
pub fn is_valid_op_name_string(str: &str) -> bool {
    is_valid_var_string(str)
}

/// Flatten associative operations in a term.
/// 
/// This function takes a term and flattens any associative operations,
/// reducing nesting where possible. For example, `f(f(x,y),z)` becomes
/// `f(x,y,z)` if `f` is associative.
/// 
/// # Arguments
/// * `term` - The term to flatten
/// 
/// # Returns
/// A new term with associative operations flattened
/// 
/// # Examples
/// ```
/// use uacalc::terms::{VariableImp, NonVariableTerm, Term};
/// use uacalc::alg::op::OperationSymbol;
/// use uacalc::terms;
/// 
/// // Create an associative operation f
/// let f = OperationSymbol::new("f", 2, true);
/// 
/// // Create term f(f(x,y),z)
/// let x: Box<dyn Term> = Box::new(VariableImp::new("x"));
/// let y: Box<dyn Term> = Box::new(VariableImp::new("y"));
/// let z: Box<dyn Term> = Box::new(VariableImp::new("z"));
/// let inner = Box::new(NonVariableTerm::new(f.clone(), vec![x, y]));
/// let outer = Box::new(NonVariableTerm::new(f.clone(), vec![inner, z]));
/// 
/// // Flatten should produce f(x,y,z)
/// let flattened = terms::flatten(outer.as_ref());
/// assert_eq!(flattened.to_string(), "f(x,y,z)");
/// ```
pub fn flatten(term: &dyn Term) -> Box<dyn Term> {
    if term.isa_variable() {
        return term.clone_box();
    }
    
    let children = term.get_children().unwrap_or_default();
    let mut flat_children: Vec<Box<dyn Term>> = Vec::new();
    
    // Recursively flatten all children
    for child in children {
        flat_children.push(flatten(child.as_ref()));
    }
    
    let leading_op_sym = term.leading_operation_symbol().unwrap();
    
    // If the operation is not associative, just return with flattened children
    if !leading_op_sym.is_associative() {
        return Box::new(NonVariableTerm::new(leading_op_sym.clone(), flat_children));
    }
    
    // For associative operations, flatten children with the same operation
    let mut args: Vec<Box<dyn Term>> = Vec::new();
    for arg in flat_children {
        if arg.isa_variable() {
            args.push(arg);
        } else {
            let arg_op_sym = arg.leading_operation_symbol().unwrap();
            if arg_op_sym == leading_op_sym {
                // Same operation, flatten it in
                if let Some(grandchildren) = arg.get_children() {
                    args.extend(grandchildren);
                }
            } else {
                // Different operation, keep it as is
                args.push(arg);
            }
        }
    }
    
    Box::new(NonVariableTerm::new(leading_op_sym.clone(), args))
}

// =============================================================================
// Private helper functions
// =============================================================================

/// Parse comma-separated arguments respecting parentheses.
/// 
/// Takes a string like "x,y,f(x,z),u" and returns ["x", "y", "f(x,z)", "u"].
/// Commas inside parentheses are not treated as separators.
fn get_argument_strings(str: &str) -> Vec<String> {
    let mut ans = Vec::new();
    let mut start = 0;
    let mut depth = 0;
    
    for (i, ch) in str.char_indices() {
        match ch {
            '(' => depth += 1,
            ')' => depth -= 1,
            ',' if depth == 0 => {
                ans.push(str[start..i].to_string());
                start = i + 1;
            }
            _ => {}
        }
    }
    
    // Add the last argument
    if start < str.len() {
        ans.push(str[start..].to_string());
    } else if str.is_empty() {
        // Empty string means no arguments
    } else {
        ans.push(String::new());
    }
    
    ans
}

/// Adjust parentheses in a string to balance them.
/// 
/// If there are more '(' than ')', add ')' at the end.
/// If there are more ')' than '(', remove trailing ')'.
fn adjust_parens(str: &str) -> String {
    let mut depth = 0;
    
    for ch in str.chars() {
        match ch {
            '(' => depth += 1,
            ')' => depth -= 1,
            _ => {}
        }
    }
    
    if depth == 0 {
        str.to_string()
    } else if depth > 0 {
        // Add closing parentheses
        let mut result = str.to_string();
        for _ in 0..depth {
            result.push(')');
        }
        result
    } else {
        // Remove extra closing parentheses from the end
        let chars: Vec<char> = str.chars().collect();
        let new_len = (chars.len() as i32 + depth) as usize;
        chars[..new_len].iter().collect()
    }
}

#[cfg(test)]
mod tests;
