//! Term analysis utilities for universal algebra
//! 
//! This module provides utilities for analyzing terms, including
//! checking variable usage, term properties, and string conversion.

use crate::{UACalcError, UACalcResult};
use crate::term::{Term, TermArena, TermId};
use std::collections::HashSet;

/// Check if a term is a variable term
pub fn is_variable_term(term_id: TermId, arena: &TermArena) -> UACalcResult<bool> {
    let term = arena.get_term(term_id)?;
    Ok(matches!(term, Term::Variable(_)))
}

/// Check if a term uses exactly two variables (for binary operations)
pub fn term_uses_exactly_two_variables(term_id: TermId, arena: &TermArena) -> UACalcResult<bool> {
    let variables = get_variables_in_term(term_id, arena)?;
    Ok(variables.len() == 2)
}

/// Get all variables used in a term
pub fn get_variables_in_term(term_id: TermId, arena: &TermArena) -> UACalcResult<HashSet<u8>> {
    let mut variables = HashSet::new();
    collect_variables_recursive(term_id, arena, &mut variables)?;
    Ok(variables)
}

/// Recursively collect all variables in a term
fn collect_variables_recursive(term_id: TermId, arena: &TermArena, variables: &mut HashSet<u8>) -> UACalcResult<()> {
    let term = arena.get_term(term_id)?;
    match term {
        Term::Variable(index) => {
            variables.insert(*index);
        }
        Term::Operation { children, .. } => {
            for &child_id in children {
                collect_variables_recursive(child_id, arena, variables)?;
            }
        }
    }
    Ok(())
}

/// Convert a term to string representation
pub fn term_to_string(term_id: TermId, arena: &TermArena) -> UACalcResult<String> {
    let term = arena.get_term(term_id)?;
    match term {
        Term::Variable(idx) => {
            match idx {
                0 => Ok("x".to_string()),
                1 => Ok("y".to_string()),
                _ => Ok(format!("x{}", idx)),
            }
        },
        Term::Operation { symbol_id, children } => {
            // Get the symbol from the arena
            let symbol = arena.get_symbol(*symbol_id)?;
            
            if children.len() == 2 {
                let left = term_to_string(children[0], arena)?;
                let right = term_to_string(children[1], arena)?;
                Ok(format!("{}({},{})", symbol.name(), left, right))
            } else {
                let child_strings: Vec<String> = children.iter()
                    .map(|&child_id| term_to_string(child_id, arena))
                    .collect::<UACalcResult<Vec<String>>>()?;
                Ok(format!("{}({})", symbol.name(), child_strings.join(",")))
            }
        }
    }
}

/// Check if a term is a binary operation (has exactly 2 children)
pub fn is_binary_operation(term_id: TermId, arena: &TermArena) -> UACalcResult<bool> {
    let term = arena.get_term(term_id)?;
    match term {
        Term::Variable(_) => Ok(false), // Variables are not operations
        Term::Operation { children, .. } => Ok(children.len() == 2),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::term::arena::TermArena;
    use crate::operation::OperationSymbol;

    #[test]
    fn test_is_variable_term() {
        let mut arena = TermArena::new();
        let var_id = arena.make_variable(0);
        let symbol = OperationSymbol::new("f".to_string(), 2);
        let op_id = arena.make_term(&symbol, &[var_id, var_id]);
        
        assert!(is_variable_term(var_id, &arena).unwrap());
        assert!(!is_variable_term(op_id, &arena).unwrap());
    }

    #[test]
    fn test_term_uses_exactly_two_variables() {
        let mut arena = TermArena::new();
        let x = arena.make_variable(0);
        let y = arena.make_variable(1);
        let z = arena.make_variable(2);
        
        let symbol = OperationSymbol::new("f".to_string(), 2);
        let f_xy = arena.make_term(&symbol, &[x, y]);
        let f_xyz = arena.make_term(&symbol, &[f_xy, z]);
        
        assert!(term_uses_exactly_two_variables(f_xy, &arena).unwrap());
        assert!(!term_uses_exactly_two_variables(f_xyz, &arena).unwrap());
        assert!(!term_uses_exactly_two_variables(x, &arena).unwrap());
    }

    #[test]
    fn test_get_variables_in_term() {
        let mut arena = TermArena::new();
        let x = arena.make_variable(0);
        let y = arena.make_variable(1);
        let z = arena.make_variable(2);
        
        let symbol = OperationSymbol::new("f".to_string(), 2);
        let f_xy = arena.make_term(&symbol, &[x, y]);
        let f_xyz = arena.make_term(&symbol, &[f_xy, z]);
        
        let vars_xy = get_variables_in_term(f_xy, &arena).unwrap();
        assert_eq!(vars_xy.len(), 2);
        assert!(vars_xy.contains(&0));
        assert!(vars_xy.contains(&1));
        
        let vars_xyz = get_variables_in_term(f_xyz, &arena).unwrap();
        assert_eq!(vars_xyz.len(), 3);
        assert!(vars_xyz.contains(&0));
        assert!(vars_xyz.contains(&1));
        assert!(vars_xyz.contains(&2));
    }

    #[test]
    fn test_term_to_string() {
        let mut arena = TermArena::new();
        let x = arena.make_variable(0);
        let y = arena.make_variable(1);
        
        let symbol = OperationSymbol::new("f".to_string(), 2);
        let f_xy = arena.make_term(&symbol, &[x, y]);
        
        assert_eq!(term_to_string(x, &arena).unwrap(), "x");
        assert_eq!(term_to_string(y, &arena).unwrap(), "y");
        assert_eq!(term_to_string(f_xy, &arena).unwrap(), "f(x,y)");
    }

    #[test]
    fn test_is_binary_operation() {
        let mut arena = TermArena::new();
        let x = arena.make_variable(0);
        let y = arena.make_variable(1);
        
        let symbol = OperationSymbol::new("f".to_string(), 2);
        let f_xy = arena.make_term(&symbol, &[x, y]);
        
        assert!(!is_binary_operation(x, &arena).unwrap());
        assert!(is_binary_operation(f_xy, &arena).unwrap());
    }
}
