use std::collections::{HashMap, HashSet};
use std::sync::{Arc, Mutex};
use std::fmt;
use crate::terms::Term;
use crate::alg::SmallAlgebra;
use crate::alg::op::{OperationSymbol, operations};

/// A class to represent equations, that is, pairs of terms.
/// 
/// In Java: `org.uacalc.eq.Equation`
#[derive(Debug)]
pub struct Equation {
    left_side: Box<dyn Term>,
    right_side: Box<dyn Term>,
    var_list: Arc<Mutex<Option<Vec<String>>>>,
}

impl Equation {
    /// Create a new equation with left and right term sides.
    /// 
    /// # Arguments
    /// * `left` - The left side term
    /// * `right` - The right side term
    /// 
    /// # Returns
    /// A new Equation instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::eq::Equation;
    /// use uacalc::terms::VariableImp;
    /// 
    /// let x = Box::new(VariableImp::new("x"));
    /// let y = Box::new(VariableImp::new("y"));
    /// let eq = Equation::new(x, y);
    /// assert_eq!(eq.to_string(), "x = y");
    /// ```
    pub fn new(left: Box<dyn Term>, right: Box<dyn Term>) -> Self {
        Equation {
            left_side: left,
            right_side: right,
            var_list: Arc::new(Mutex::new(None)),
        }
    }
    
    /// Create a new equation with explicit variable list.
    /// 
    /// # Arguments
    /// * `left` - The left side term
    /// * `right` - The right side term
    /// * `vars` - The list of variables to use
    /// 
    /// # Returns
    /// A new Equation instance with the specified variable list
    pub fn new_with_vars(left: Box<dyn Term>, right: Box<dyn Term>, vars: Vec<String>) -> Self {
        Equation {
            left_side: left,
            right_side: right,
            var_list: Arc::new(Mutex::new(Some(vars))),
        }
    }
    
    /// Get the left side term.
    /// 
    /// # Returns
    /// A reference to the left side term
    pub fn left_side(&self) -> &dyn Term {
        self.left_side.as_ref()
    }
    
    /// Get the right side term.
    /// 
    /// # Returns
    /// A reference to the right side term
    pub fn right_side(&self) -> &dyn Term {
        self.right_side.as_ref()
    }
    
    /// Get the variable list for this equation.
    /// 
    /// This is computed lazily by merging the variable lists of both sides.
    /// The variable list is cached after the first computation.
    /// 
    /// # Returns
    /// The list of all variables in the equation
    pub fn get_variable_list(&self) -> Vec<String> {
        let mut var_list_guard = self.var_list.lock().unwrap();
        
        if var_list_guard.is_none() {
            // Compute variable list by merging both sides
            let mut vars = self.left_side.get_variable_list();
            let right_vars = self.right_side.get_variable_list();
            
            // Add variables from right side that aren't already in the list
            for v in right_vars {
                if !vars.contains(&v) {
                    vars.push(v);
                }
            }
            
            *var_list_guard = Some(vars);
        }
        
        var_list_guard.as_ref().unwrap().clone()
    }
    
    /// Get all operation symbols used in this equation.
    /// 
    /// # Returns
    /// A set containing all operation symbols from both sides
    pub fn get_operation_symbols(&self) -> HashSet<OperationSymbol> {
        let mut set = self.left_side.get_operation_symbols();
        for sym in self.right_side.get_operation_symbols() {
            set.insert(sym);
        }
        set
    }
    
    /// Find where this equation fails in the given algebra.
    /// 
    /// # Arguments
    /// * `alg` - The algebra to check
    /// 
    /// # Returns
    /// * `Ok(Some(args))` - The variable assignment where the equation fails
    /// * `Ok(None)` - If the equation holds in the algebra
    /// * `Err(String)` - If an error occurs during checking
    pub fn find_failure(&self, alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>) -> Result<Option<Vec<i32>>, String> {
        let var_list = self.get_variable_list();
        let left_op = self.left_side.interpretation(alg.clone(), &var_list, true)?;
        let right_op = self.right_side.interpretation(alg, &var_list, true)?;
        operations::find_difference(left_op.as_ref(), right_op.as_ref())
    }
    
    /// Find where this equation fails in the given algebra as a variable map.
    /// 
    /// # Arguments
    /// * `alg` - The algebra to check
    /// 
    /// # Returns
    /// * `Ok(Some(map))` - A map from variable names to values where the equation fails
    /// * `Ok(None)` - If the equation holds in the algebra
    /// * `Err(String)` - If an error occurs during checking
    pub fn find_failure_map(&self, alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>) -> Result<Option<HashMap<String, i32>>, String> {
        let diff = self.find_failure(alg)?;
        if diff.is_none() {
            return Ok(None);
        }
        
        let diff = diff.unwrap();
        let var_list = self.get_variable_list();
        let mut map = HashMap::new();
        
        for (k, var) in var_list.iter().enumerate() {
            map.insert(var.clone(), diff[k]);
        }
        
        Ok(Some(map))
    }
}

impl fmt::Display for Equation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} = {}", self.left_side, self.right_side)
    }
}

// Equations module for generating common algebraic equations
pub mod equations;

pub struct Presentation {
    // TODO: Implement presentation structure
}
