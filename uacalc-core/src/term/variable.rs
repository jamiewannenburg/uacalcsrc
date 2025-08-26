//! Variable handling for terms
//! 
//! This module provides efficient variable representation and management
//! for term evaluation.

use crate::{UACalcError, UACalcResult};
use std::collections::HashMap;

/// Variable representation
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Variable {
    /// Variable index (0-255)
    index: u8,
    /// Optional variable name for debugging
    name: Option<String>,
}

impl Variable {
    /// Create a new variable with given index
    pub fn new(index: u8) -> Self {
        Self {
            index,
            name: None,
        }
    }
    
    /// Create a new variable with name
    pub fn named(index: u8, name: String) -> Self {
        Self {
            index,
            name: Some(name),
        }
    }
    
    /// Get the variable index
    pub fn index(&self) -> u8 {
        self.index
    }
    
    /// Get the variable name if available
    pub fn name(&self) -> Option<&str> {
        self.name.as_deref()
    }
    
    /// Set the variable name
    pub fn set_name(&mut self, name: String) {
        self.name = Some(name);
    }
}

impl From<u8> for Variable {
    fn from(index: u8) -> Self {
        Self::new(index)
    }
}

impl std::fmt::Display for Variable {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        if let Some(name) = &self.name {
            write!(f, "{}", name)
        } else {
            write!(f, "x{}", self.index)
        }
    }
}

/// Variable assignment for term evaluation
#[derive(Debug, Clone)]
pub struct VariableAssignment {
    /// Map from variable indices to values
    values: HashMap<u8, usize>,
    /// Default value for unassigned variables
    default_value: usize,
}

impl VariableAssignment {
    /// Create a new variable assignment
    pub fn new() -> Self {
        Self {
            values: HashMap::new(),
            default_value: 0,
        }
    }
    
    /// Create a variable assignment with default value
    pub fn with_default(default_value: usize) -> Self {
        Self {
            values: HashMap::new(),
            default_value,
        }
    }
    
    /// Assign a value to a variable
    pub fn assign(&mut self, variable: u8, value: usize) {
        self.values.insert(variable, value);
    }
    
    /// Get the value of a variable
    pub fn get(&self, variable: u8) -> usize {
        self.values.get(&variable).copied().unwrap_or(self.default_value)
    }
    
    /// Check if a variable is assigned
    pub fn is_assigned(&self, variable: u8) -> bool {
        self.values.contains_key(&variable)
    }
    
    /// Get all assigned variables
    pub fn assigned_variables(&self) -> Vec<u8> {
        self.values.keys().cloned().collect()
    }
    
    /// Clear all assignments
    pub fn clear(&mut self) {
        self.values.clear();
    }
    
    /// Set the default value
    pub fn set_default(&mut self, default_value: usize) {
        self.default_value = default_value;
    }
    
    /// Get the default value
    pub fn default_value(&self) -> usize {
        self.default_value
    }
    
    /// Create from a vector of values (indexed by variable index)
    pub fn from_values(values: Vec<usize>) -> Self {
        let mut assignment = Self::new();
        for (index, value) in values.into_iter().enumerate() {
            if index <= u8::MAX as usize {
                assignment.assign(index as u8, value);
            }
        }
        assignment
    }
    
    /// Create from a slice of values
    pub fn from_slice(values: &[usize]) -> Self {
        Self::from_values(values.to_vec())
    }
}

impl Default for VariableAssignment {
    fn default() -> Self {
        Self::new()
    }
}

impl From<Vec<usize>> for VariableAssignment {
    fn from(values: Vec<usize>) -> Self {
        Self::from_values(values)
    }
}

impl From<&[usize]> for VariableAssignment {
    fn from(values: &[usize]) -> Self {
        Self::from_slice(values)
    }
}

/// Variable scope for managing variable bindings
#[derive(Debug, Clone)]
pub struct VariableScope {
    /// Stack of variable assignments
    scopes: Vec<VariableAssignment>,
}

impl VariableScope {
    /// Create a new variable scope
    pub fn new() -> Self {
        Self {
            scopes: vec![VariableAssignment::new()],
        }
    }
    
    /// Enter a new scope
    pub fn enter_scope(&mut self) {
        self.scopes.push(VariableAssignment::new());
    }
    
    /// Exit the current scope
    pub fn exit_scope(&mut self) -> UACalcResult<()> {
        if self.scopes.len() <= 1 {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot exit root scope".to_string(),
            });
        }
        self.scopes.pop();
        Ok(())
    }
    
    /// Assign a value to a variable in the current scope
    pub fn assign(&mut self, variable: u8, value: usize) {
        if let Some(scope) = self.scopes.last_mut() {
            scope.assign(variable, value);
        }
    }
    
    /// Get the value of a variable (searches from innermost to outermost scope)
    pub fn get(&self, variable: u8) -> usize {
        for scope in self.scopes.iter().rev() {
            if scope.is_assigned(variable) {
                return scope.get(variable);
            }
        }
        // Return default from root scope
        self.scopes.first().map(|s| s.default_value()).unwrap_or(0)
    }
    
    /// Check if a variable is assigned in any scope
    pub fn is_assigned(&self, variable: u8) -> bool {
        self.scopes.iter().any(|scope| scope.is_assigned(variable))
    }
    
    /// Get the current scope depth
    pub fn depth(&self) -> usize {
        self.scopes.len()
    }
}

impl Default for VariableScope {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_variable() {
        let var = Variable::new(5);
        assert_eq!(var.index(), 5);
        assert_eq!(var.name(), None);
        
        let named_var = Variable::named(3, "x".to_string());
        assert_eq!(named_var.index(), 3);
        assert_eq!(named_var.name(), Some("x"));
    }
    
    #[test]
    fn test_variable_assignment() {
        let mut assignment = VariableAssignment::new();
        assignment.assign(0, 5);
        assignment.assign(1, 10);
        
        assert_eq!(assignment.get(0), 5);
        assert_eq!(assignment.get(1), 10);
        assert_eq!(assignment.get(2), 0); // Default value
        
        assert!(assignment.is_assigned(0));
        assert!(assignment.is_assigned(1));
        assert!(!assignment.is_assigned(2));
    }
    
    #[test]
    fn test_variable_assignment_from_values() {
        let assignment = VariableAssignment::from_values(vec![1, 2, 3]);
        assert_eq!(assignment.get(0), 1);
        assert_eq!(assignment.get(1), 2);
        assert_eq!(assignment.get(2), 3);
    }
    
    #[test]
    fn test_variable_scope() {
        let mut scope = VariableScope::new();
        scope.assign(0, 5);
        
        scope.enter_scope();
        scope.assign(0, 10);
        scope.assign(1, 15);
        
        assert_eq!(scope.get(0), 10); // From inner scope
        assert_eq!(scope.get(1), 15); // From inner scope
        
        scope.exit_scope().unwrap();
        
        assert_eq!(scope.get(0), 5); // From outer scope
        assert_eq!(scope.get(1), 0); // Default value
    }
}
