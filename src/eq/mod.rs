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

impl fmt::Display for Presentation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let rels: Vec<String> = self.relations.iter().map(|r| format!("{}", r)).collect();
        write!(f, "Presentation(variables=[{}], relations=[{}])", 
               self.variables.join(", "), rels.join(", "))
    }
}

// Equations module for generating common algebraic equations
pub mod equations;

#[cfg(test)]
mod tests {
    use super::*;
    use crate::terms::VariableImp;
    
    #[test]
    fn test_presentation_creation() {
        let variables = vec!["x".to_string(), "y".to_string()];
        let relations = vec![];
        
        let pres = Presentation::new(variables, relations);
        
        assert_eq!(pres.get_variables().len(), 2);
        assert_eq!(pres.get_relations().len(), 0);
    }
    
    #[test]
    fn test_presentation_with_relations() {
        let variables = vec!["x".to_string(), "y".to_string()];
        
        let left = Box::new(VariableImp::new("x")) as Box<dyn Term>;
        let right = Box::new(VariableImp::new("y")) as Box<dyn Term>;
        let equation = Equation::new(left, right);
        let relations = vec![equation];
        
        let pres = Presentation::new(variables, relations);
        
        assert_eq!(pres.get_variables().len(), 2);
        assert_eq!(pres.get_relations().len(), 1);
    }
    
    #[test]
    fn test_presentation_getters() {
        let variables = vec!["x".to_string(), "y".to_string()];
        let relations = vec![];
        
        let pres = Presentation::new(variables, relations);
        
        let vars = pres.get_variables();
        assert_eq!(vars.len(), 2);
        assert_eq!(vars[0], "x");
        assert_eq!(vars[1], "y");
        
        let rels = pres.get_relations();
        assert_eq!(rels.len(), 0);
    }
    
    #[test]
    fn test_presentation_display() {
        let variables = vec!["x".to_string(), "y".to_string()];
        let relations = vec![];
        
        let pres = Presentation::new(variables, relations);
        let display_str = format!("{}", pres);
        
        assert!(display_str.contains("variables=[x, y]"));
        assert!(display_str.contains("relations=[]"));
    }
    
    #[test]
    fn test_presentation_clone() {
        let variables = vec!["x".to_string()];
        let relations = vec![];
        
        let pres1 = Presentation::new(variables, relations);
        let pres2 = pres1.clone();
        
        assert_eq!(pres1.get_variables().len(), pres2.get_variables().len());
        assert_eq!(pres1.get_relations().len(), pres2.get_relations().len());
    }
    
    #[test]
    fn test_presentation_equality() {
        let variables1 = vec!["x".to_string(), "y".to_string()];
        let relations1 = vec![];
        
        let variables2 = vec!["x".to_string(), "y".to_string()];
        let relations2 = vec![];
        
        let pres1 = Presentation::new(variables1, relations1);
        let pres2 = Presentation::new(variables2, relations2);
        
        // Test that they have the same content (since we can't derive PartialEq)
        assert_eq!(pres1.get_variables(), pres2.get_variables());
        assert_eq!(pres1.get_relations().len(), pres2.get_relations().len());
    }
}

/// A presentation for finitely presented algebras.
/// 
/// A presentation consists of a list of variables and equations 
/// thought of as relations.
/// 
/// In Java: `org.uacalc.eq.Presentation`
#[derive(Debug)]
pub struct Presentation {
    /// The variables in this presentation (stored as names for simplicity)
    pub variables: Vec<String>,
    /// The equations (relations) in this presentation
    pub relations: Vec<Equation>,
}

impl Presentation {
    /// Create a new presentation with the given variables and relations.
    /// 
    /// # Arguments
    /// * `variables` - The list of variable names
    /// * `relations` - The list of equations (relations)
    /// 
    /// # Returns
    /// A new Presentation instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::eq::Presentation;
    /// 
    /// let vars = vec!["x".to_string(), "y".to_string()];
    /// let rels = vec![];
    /// let pres = Presentation::new(vars, rels);
    /// ```
    pub fn new(variables: Vec<String>, relations: Vec<Equation>) -> Self {
        Presentation {
            variables,
            relations,
        }
    }
    
    /// Get the variables in this presentation.
    /// 
    /// # Returns
    /// A reference to the variables list
    pub fn get_variables(&self) -> &Vec<String> {
        &self.variables
    }
    
    /// Get the relations (equations) in this presentation.
    /// 
    /// # Returns
    /// A reference to the relations list
    pub fn get_relations(&self) -> &Vec<Equation> {
        &self.relations
    }
}

impl Clone for Equation {
    fn clone(&self) -> Self {
        // Note: This is a simplified clone that doesn't preserve the var_list cache
        // In a real implementation, you might want to handle this differently
        Equation {
            left_side: self.left_side.clone_box(),
            right_side: self.right_side.clone_box(),
            var_list: Arc::new(Mutex::new(None)), // Reset cache
        }
    }
}

impl Clone for Presentation {
    fn clone(&self) -> Self {
        Presentation {
            variables: self.variables.clone(),
            relations: self.relations.clone(),
        }
    }
}
