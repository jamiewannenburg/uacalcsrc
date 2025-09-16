//! Equation representation and operations for universal algebra
//!
//! This module provides equation representation, satisfaction checking,
//! and manipulation operations for universal algebra.

use crate::{UACalcError, UACalcResult};
use crate::algebra::{Algebra, BasicAlgebra};
use crate::operation::OperationSymbol;
use crate::term::{Term, TermId, TermArena, eval_term};
use crate::term::variable::VariableAssignment;
use std::collections::HashMap;
use std::fmt;

/// An equation is a pair of terms (left side, right side)
#[derive(Debug, Clone)]
pub struct Equation {
    /// Left side of the equation
    pub left: TermId,
    /// Right side of the equation
    pub right: TermId,
    /// Arena containing the terms
    arena: TermArena,
}

impl Equation {
    /// Create a new equation from two terms
    pub fn new(left: TermId, right: TermId, arena: TermArena) -> Self {
        Self { left, right, arena }
    }

    /// Create an equation from term strings
    pub fn from_strings(arena: &mut TermArena, left_str: &str, right_str: &str) -> UACalcResult<Self> {
        let left = crate::term::term::utils::from_string(arena, left_str)?;
        let right = crate::term::term::utils::from_string(arena, right_str)?;
        Ok(Self::new(left, right, arena.clone()))
    }

    /// Get the left side term
    pub fn left(&self) -> &Term {
        self.arena.get_term(self.left).unwrap()
    }

    /// Get the right side term
    pub fn right(&self) -> &Term {
        self.arena.get_term(self.right).unwrap()
    }

    /// Get the arena
    pub fn arena(&self) -> &TermArena {
        &self.arena
    }

    /// Get all variables used in this equation
    pub fn variables(&self) -> UACalcResult<Vec<u8>> {
        let left_vars = self.left().variables(&self.arena)?;
        let right_vars = self.right().variables(&self.arena)?;
        
        let mut all_vars = left_vars;
        all_vars.extend(right_vars);
        all_vars.sort();
        all_vars.dedup();
        
        Ok(all_vars)
    }

    /// Get all operation symbols used in this equation
    pub fn operation_symbols(&self) -> UACalcResult<Vec<OperationSymbol>> {
        let left_ops = self.left().operation_symbols(&self.arena)?;
        let right_ops = self.right().operation_symbols(&self.arena)?;
        
        let mut all_ops = left_ops;
        all_ops.extend(right_ops);
        all_ops.sort_by(|a, b| a.name().cmp(b.name()));
        all_ops.dedup();
        
        Ok(all_ops)
    }

    /// Check if this equation is satisfied in the given algebra
    pub fn is_satisfied_in(&self, algebra: &BasicAlgebra) -> UACalcResult<bool> {
        let variables = self.variables()?;
        
        // For small algebras, check exhaustively
        if algebra.cardinality() <= 8 {
            self.check_exhaustively(algebra, &variables)
        } else {
            // For larger algebras, use sampling
            self.check_sampling(algebra, &variables)
        }
    }

    /// Check equation satisfaction exhaustively for small algebras
    fn check_exhaustively(&self, algebra: &BasicAlgebra, variables: &[u8]) -> UACalcResult<bool> {
        use itertools::Itertools;
        
        for assignment in (0..algebra.cardinality()).combinations_with_replacement(variables.len()) {
            if assignment.len() != variables.len() {
                continue;
            }
            
            let mut var_map = VariableAssignment::new();
            for (i, &var) in variables.iter().enumerate() {
                var_map.assign(var, assignment[i]);
            }
            
            let left_value = eval_term(self.left, &self.arena, algebra, &var_map)?;
            let right_value = eval_term(self.right, &self.arena, algebra, &var_map)?;
            
            if left_value != right_value {
                return Ok(false);
            }
        }
        
        Ok(true)
    }

    /// Check equation satisfaction using sampling for large algebras
    fn check_sampling(&self, algebra: &BasicAlgebra, variables: &[u8]) -> UACalcResult<bool> {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        let sample_size = (algebra.cardinality().pow(variables.len() as u32)).min(1000);
        
        for _ in 0..sample_size {
            let mut var_map = VariableAssignment::new();
            for &var in variables {
                var_map.assign(var, rng.gen_range(0..algebra.cardinality()));
            }
            
            let left_value = eval_term(self.left, &self.arena, algebra, &var_map)?;
            let right_value = eval_term(self.right, &self.arena, algebra, &var_map)?;
            
            if left_value != right_value {
                return Ok(false);
            }
        }
        
        Ok(true)
    }

    /// Find a counterexample where the equation fails
    pub fn find_counterexample(&self, algebra: &BasicAlgebra) -> UACalcResult<Option<HashMap<u8, usize>>> {
        let variables = self.variables()?;
        
        // For small algebras, check exhaustively
        if algebra.cardinality() <= 8 {
            self.find_counterexample_exhaustive(algebra, &variables)
        } else {
            // For larger algebras, use sampling
            self.find_counterexample_sampling(algebra, &variables)
        }
    }

    /// Find counterexample exhaustively
    fn find_counterexample_exhaustive(&self, algebra: &BasicAlgebra, variables: &[u8]) -> UACalcResult<Option<HashMap<u8, usize>>> {
        use itertools::Itertools;
        
        for assignment in (0..algebra.cardinality()).combinations_with_replacement(variables.len()) {
            if assignment.len() != variables.len() {
                continue;
            }
            
            let mut var_map = VariableAssignment::new();
            for (i, &var) in variables.iter().enumerate() {
                var_map.assign(var, assignment[i]);
            }
            
            let left_value = eval_term(self.left, &self.arena, algebra, &var_map)?;
            let right_value = eval_term(self.right, &self.arena, algebra, &var_map)?;
            
            if left_value != right_value {
                let mut result = HashMap::new();
                for &var in variables {
                    result.insert(var, var_map.get(var));
                }
                return Ok(Some(result));
            }
        }
        
        Ok(None)
    }

    /// Find counterexample using sampling
    fn find_counterexample_sampling(&self, algebra: &BasicAlgebra, variables: &[u8]) -> UACalcResult<Option<HashMap<u8, usize>>> {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        let sample_size = (algebra.cardinality().pow(variables.len() as u32)).min(1000);
        
        for _ in 0..sample_size {
            let mut var_map = VariableAssignment::new();
            for &var in variables {
                var_map.assign(var, rng.gen_range(0..algebra.cardinality()));
            }
            
            let left_value = eval_term(self.left, &self.arena, algebra, &var_map)?;
            let right_value = eval_term(self.right, &self.arena, algebra, &var_map)?;
            
            if left_value != right_value {
                let mut result = HashMap::new();
                for &var in variables {
                    result.insert(var, var_map.get(var));
                }
                return Ok(Some(result));
            }
        }
        
        Ok(None)
    }

    /// Substitute variables in this equation
    pub fn substitute(&mut self, substitutions: &HashMap<u8, TermId>) -> UACalcResult<()> {
        let left_term = self.arena.get_term(self.left)?.clone();
        let right_term = self.arena.get_term(self.right)?.clone();
        
        let new_left = left_term.substitute(&mut self.arena, substitutions)?;
        let new_right = right_term.substitute(&mut self.arena, substitutions)?;
        
        self.left = new_left;
        self.right = new_right;
        
        Ok(())
    }

    /// Check if this is an identity equation (left == right)
    pub fn is_identity(&self) -> UACalcResult<bool> {
        Ok(self.left == self.right)
    }

    /// Get the complexity of this equation
    pub fn complexity(&self) -> UACalcResult<EquationComplexity> {
        let left_depth = self.left().depth(&self.arena)?;
        let right_depth = self.right().depth(&self.arena)?;
        let max_depth = left_depth.max(right_depth);
        
        let variables = self.variables()?;
        let operations = self.operation_symbols()?;
        
        let complexity_level = if variables.len() <= 2 && operations.len() <= 2 && max_depth <= 2 {
            ComplexityLevel::Low
        } else if variables.len() <= 4 && operations.len() <= 4 && max_depth <= 4 {
            ComplexityLevel::Medium
        } else {
            ComplexityLevel::High
        };
        
        Ok(EquationComplexity {
            variable_count: variables.len(),
            operation_count: operations.len(),
            max_depth,
            complexity_level,
        })
    }

    /// Analyze properties of this equation
    pub fn analyze_properties(&self) -> UACalcResult<EquationProperties> {
        let mut properties = Vec::new();
        
        // Check if it's an identity
        if self.is_identity()? {
            properties.push("identity".to_string());
            properties.push("tautology".to_string());
        }
        
        // Check for commutative pattern
        let left_str = self.left().to_string(&self.arena)?;
        let right_str = self.right().to_string(&self.arena)?;
        
        if left_str.contains("f(x0, x1)") && right_str.contains("f(x1, x0)") {
            properties.push("commutative".to_string());
        }
        
        // Check for associative pattern
        if left_str.contains("f(f(x0, x1), x2)") && right_str.contains("f(x0, f(x1, x2))") {
            properties.push("associative".to_string());
        }
        
        let is_identity = properties.contains(&"identity".to_string());
        let is_tautology = properties.contains(&"tautology".to_string());
        
        Ok(EquationProperties {
            properties,
            is_identity,
            is_tautology,
        })
    }
}

impl fmt::Display for Equation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let left_str = self.left().to_string(&self.arena).unwrap_or_else(|_| "?".to_string());
        let right_str = self.right().to_string(&self.arena).unwrap_or_else(|_| "?".to_string());
        write!(f, "{} = {}", left_str, right_str)
    }
}

/// Equation complexity information
#[derive(Debug, Clone)]
pub struct EquationComplexity {
    pub variable_count: usize,
    pub operation_count: usize,
    pub max_depth: usize,
    pub complexity_level: ComplexityLevel,
}

/// Complexity level classification
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ComplexityLevel {
    Low,
    Medium,
    High,
}

/// Equation properties analysis
#[derive(Debug, Clone)]
pub struct EquationProperties {
    pub properties: Vec<String>,
    pub is_identity: bool,
    pub is_tautology: bool,
}

/// Standard equation generation utilities
pub mod standard {
    use super::*;
    use crate::operation::OperationSymbol;
    
    /// Generate associative law: f(f(x,y),z) = f(x,f(y,z))
    pub fn associative_law(arena: &mut TermArena, symbol: &OperationSymbol) -> UACalcResult<Equation> {
        if symbol.arity() != 2 {
            return Err(UACalcError::InvalidOperation {
                message: "Associative law requires binary operation".to_string(),
            });
        }
        
        let x = arena.make_variable(0);
        let y = arena.make_variable(1);
        let z = arena.make_variable(2);
        
        let fxy = arena.make_term(symbol, &[x, y]);
        let fyz = arena.make_term(symbol, &[y, z]);
        
        let left = arena.make_term(symbol, &[fxy, z]);
        let right = arena.make_term(symbol, &[x, fyz]);
        
        Ok(Equation::new(left, right, arena.clone()))
    }
    
    /// Generate cyclic law: f(x0,x1,...,x{k-1}) = f(x{k-1},x0,...,x{k-2})
    pub fn cyclic_law(arena: &mut TermArena, symbol: &OperationSymbol) -> UACalcResult<Equation> {
        let arity = symbol.arity();
        if arity < 1 {
            return Err(UACalcError::InvalidOperation {
                message: "Cyclic law requires operation with arity >= 1".to_string(),
            });
        }
        
        let mut args = Vec::new();
        let mut args2 = Vec::new();
        
        for i in 0..arity {
            args.push(arena.make_variable(i as u8));
        }
        
        // Cyclic permutation: x0 -> x{k-1}, x1 -> x0, ..., x{k-1} -> x{k-2}
        args2.push(arena.make_variable((arity - 1) as u8));
        for i in 0..(arity - 1) {
            args2.push(arena.make_variable(i as u8));
        }
        
        let left = arena.make_term(symbol, &args);
        let right = arena.make_term(symbol, &args2);
        
        Ok(Equation::new(left, right, arena.clone()))
    }
    
    /// Generate first-second symmetric law: f(x,y) = f(y,x)
    pub fn first_second_symmetric_law(arena: &mut TermArena, symbol: &OperationSymbol) -> UACalcResult<Equation> {
        if symbol.arity() < 2 {
            return Err(UACalcError::InvalidOperation {
                message: "First-second symmetric law requires operation with arity >= 2".to_string(),
            });
        }
        
        let x = arena.make_variable(0);
        let y = arena.make_variable(1);
        
        let left = arena.make_term(symbol, &[x, y]);
        let right = arena.make_term(symbol, &[y, x]);
        
        Ok(Equation::new(left, right, arena.clone()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::operation::OperationSymbol;
    use crate::algebra::SmallAlgebra;
    
    #[test]
    fn test_equation_creation() {
        let mut arena = TermArena::new();
        let x = arena.make_variable(0);
        let y = arena.make_variable(1);
        
        let equation = Equation::new(x, y, arena.clone());
        assert_eq!(equation.left(), &Term::variable(0));
        assert_eq!(equation.right(), &Term::variable(1));
    }
    
    #[test]
    fn test_equation_from_strings() {
        let mut arena = TermArena::new();
        let equation = Equation::from_strings(&mut arena, "x0", "x1").unwrap();
        assert_eq!(equation.left(), &Term::variable(0));
        assert_eq!(equation.right(), &Term::variable(1));
    }
    
    #[test]
    fn test_equation_variables() {
        let mut arena = TermArena::new();
        let equation = Equation::from_strings(&mut arena, "x0", "x1").unwrap();
        let vars = equation.variables().unwrap();
        assert_eq!(vars, vec![0, 1]);
    }
    
    #[test]
    fn test_equation_identity() {
        let mut arena = TermArena::new();
        let x = arena.make_variable(0);
        let equation = Equation::new(x, x, arena.clone());
        assert!(equation.is_identity().unwrap());
    }
    
    #[test]
    fn test_associative_law_generation() {
        let mut arena = TermArena::new();
        let symbol = OperationSymbol::new("f".to_string(), 2);
        let equation = standard::associative_law(&mut arena, &symbol).unwrap();
        
        let left_str = equation.left().to_string(&arena).unwrap();
        let right_str = equation.right().to_string(&arena).unwrap();
        
        assert!(left_str.contains("f(f(x0, x1), x2)"));
        assert!(right_str.contains("f(x0, f(x1, x2))"));
    }
    
    #[test]
    fn test_cyclic_law_generation() {
        let mut arena = TermArena::new();
        let symbol = OperationSymbol::new("g".to_string(), 3);
        let equation = standard::cyclic_law(&mut arena, &symbol).unwrap();
        
        let left_str = equation.left().to_string(&arena).unwrap();
        let right_str = equation.right().to_string(&arena).unwrap();
        
        assert!(left_str.contains("g(x0, x1, x2)"));
        assert!(right_str.contains("g(x2, x0, x1)"));
    }
}
