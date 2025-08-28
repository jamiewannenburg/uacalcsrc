//! Term representation for universal algebra
//! 
//! This module provides efficient term representation with compact
//! memory layout and zero-allocation evaluation.

use crate::{UACalcError, UACalcResult};
use crate::term::arena::TermArena;
use smallvec::SmallVec;
use std::fmt;

/// Term identifier for arena-based allocation
pub type TermId = usize;

/// Term representation with compact memory layout
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Term {
    /// Variable term with index (supports up to 256 variables)
    Variable(u8),
    
    /// Operation term with symbol and children
    Operation {
        /// Index into symbol table
        symbol_id: u16,
        /// Child terms (most terms have ≤4 children)
        children: SmallVec<[TermId; 4]>,
    },
}

impl Term {
    /// Create a variable term
    pub fn variable(index: u8) -> Self {
        Term::Variable(index)
    }
    
    /// Create an operation term
    pub fn operation(symbol_id: u16, children: &[TermId]) -> Self {
        Term::Operation {
            symbol_id,
            children: children.iter().cloned().collect(),
        }
    }
    
    /// Check if this is a variable term
    pub fn is_variable(&self) -> bool {
        matches!(self, Term::Variable(_))
    }
    
    /// Check if this is an operation term
    pub fn is_operation(&self) -> bool {
        matches!(self, Term::Operation { .. })
    }
    
    /// Get the arity of this term (0 for variables, number of children for operations)
    pub fn arity(&self) -> usize {
        match self {
            Term::Variable(_) => 0,
            Term::Operation { children, .. } => children.len(),
        }
    }
    
    /// Get the depth of this term
    pub fn depth(&self, arena: &TermArena) -> UACalcResult<usize> {
        match self {
            Term::Variable(_) => Ok(0),
            Term::Operation { children, .. } => {
                let mut max_child_depth = 0;
                for &child_id in children {
                    let child = arena.get_term(child_id)?;
                    let child_depth = child.depth(arena)?;
                    max_child_depth = max_child_depth.max(child_depth);
                }
                Ok(max_child_depth + 1)
            }
        }
    }
    
    /// Get all variables used in this term
    pub fn variables(&self, arena: &TermArena) -> UACalcResult<Vec<u8>> {
        let mut vars = Vec::new();
        self.collect_variables(arena, &mut vars)?;
        vars.sort();
        vars.dedup();
        Ok(vars)
    }
    
    /// Collect variables recursively
    fn collect_variables(&self, arena: &TermArena, vars: &mut Vec<u8>) -> UACalcResult<()> {
        match self {
            Term::Variable(index) => {
                vars.push(*index);
            }
            Term::Operation { children, .. } => {
                for &child_id in children {
                    let child = arena.get_term(child_id)?;
                    child.collect_variables(arena, vars)?;
                }
            }
        }
        Ok(())
    }
    
    /// Convert to string representation
    pub fn to_string(&self, arena: &TermArena) -> UACalcResult<String> {
        match self {
            Term::Variable(index) => Ok(format!("x{}", index)),
            Term::Operation { symbol_id, children } => {
                let symbol = arena.get_symbol(*symbol_id)?;
                let mut args = Vec::new();
                for &child_id in children {
                    let child = arena.get_term(child_id)?;
                    args.push(child.to_string(arena)?);
                }
                if args.is_empty() {
                    Ok(symbol.name().to_string())
                } else {
                    Ok(format!("{}({})", symbol.name(), args.join(", ")))
                }
            }
        }
    }
}

impl fmt::Display for Term {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        // This requires a TermArena, so we'll use a simple representation
        match self {
            Term::Variable(index) => write!(f, "x{}", index),
            Term::Operation { symbol_id, children } => {
                write!(f, "f{}({} children)", symbol_id, children.len())
            }
        }
    }
}



/// Term construction utilities
pub mod utils {
    use super::*;
    use crate::operation::OperationSymbol;
    use crate::term::arena::TermArena;
    
    /// Create a simple variable term
    pub fn variable(arena: &mut TermArena, index: u8) -> TermId {
        arena.make_variable(index)
    }
    
    /// Create a constant term (0-ary operation)
    pub fn constant(arena: &mut TermArena, symbol: &OperationSymbol) -> TermId {
        arena.make_term(symbol, &[])
    }
    
    /// Create a unary operation term
    pub fn unary(arena: &mut TermArena, symbol: &OperationSymbol, child: TermId) -> TermId {
        arena.make_term(symbol, &[child])
    }
    
    /// Create a binary operation term
    pub fn binary(arena: &mut TermArena, symbol: &OperationSymbol, left: TermId, right: TermId) -> TermId {
        arena.make_term(symbol, &[left, right])
    }
    
    /// Create a term from a simple expression string
    pub fn from_string(arena: &mut TermArena, expr: &str) -> UACalcResult<TermId> {
        // Simple parser for basic expressions like "f(x0, x1)"
        // This is a basic implementation - more sophisticated parsing would be needed for complex terms
        
        let expr = expr.trim();
        
        // Check if it's a variable
        if expr.starts_with('x') {
            if let Ok(index) = expr[1..].parse::<u8>() {
                return Ok(variable(arena, index));
            }
        }
        
        // Check if it's a constant
        if !expr.contains('(') && !expr.contains(')') {
            let symbol = OperationSymbol::new(expr.to_string(), 0);
            return Ok(constant(arena, &symbol));
        }
        
        // Parse operation term
        if let Some(open_paren) = expr.find('(') {
            let name = expr[..open_paren].trim();
            let args_str = expr[open_paren + 1..expr.len() - 1].trim();
            
            let symbol = OperationSymbol::new(name.to_string(), 0); // Arity will be set below
            
            if args_str.is_empty() {
                return Ok(constant(arena, &symbol));
            }
            
            let args: Vec<TermId> = args_str
                .split(',')
                .map(|s| from_string(arena, s.trim()))
                .collect::<UACalcResult<_>>()?;
            
            let mut symbol = symbol;
            symbol.set_arity(args.len());
            
            Ok(arena.make_term(&symbol, &args))
        } else {
            Err(UACalcError::InvalidOperation {
                message: format!("Invalid term expression: {}", expr),
            })
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::operation::OperationSymbol;
    use crate::term::arena::TermArena;
    
    #[test]
    fn test_variable_term() {
        let term = Term::variable(5);
        assert!(term.is_variable());
        assert_eq!(term.arity(), 0);
    }
    
    #[test]
    fn test_operation_term() {
        let term = Term::operation(1, &[0, 2]);
        assert!(term.is_operation());
        assert_eq!(term.arity(), 2);
    }
    
    #[test]
    fn test_term_arena() {
        let mut arena = TermArena::new();
        
        let var_id = arena.make_variable(0);
        let symbol = OperationSymbol::new("f".to_string(), 2);
        let op_id = arena.make_term(&symbol, &[var_id]);
        
        assert_eq!(arena.num_terms(), 2);
        assert_eq!(arena.num_symbols(), 1);
        
        let var = arena.get_term(var_id).unwrap();
        assert!(var.is_variable());
        
        let op = arena.get_term(op_id).unwrap();
        assert!(op.is_operation());
    }
    
    #[test]
    fn test_term_depth() {
        let mut arena = TermArena::new();
        
        let x0 = arena.make_variable(0);
        let x1 = arena.make_variable(1);
        let symbol = OperationSymbol::new("f".to_string(), 2);
        let op = arena.make_term(&symbol, &[x0, x1]);
        
        let x0_term = arena.get_term(x0).unwrap();
        assert_eq!(x0_term.depth(&arena).unwrap(), 0);
        
        let op_term = arena.get_term(op).unwrap();
        assert_eq!(op_term.depth(&arena).unwrap(), 1);
    }
    
    #[test]
    fn test_term_variables() {
        let mut arena = TermArena::new();
        
        let x0 = arena.make_variable(0);
        let x1 = arena.make_variable(1);
        let symbol = OperationSymbol::new("f".to_string(), 2);
        let op = arena.make_term(&symbol, &[x0, x1]);
        
        let op_term = arena.get_term(op).unwrap();
        let vars = op_term.variables(&arena).unwrap();
        assert_eq!(vars, vec![0, 1]);
    }
}
