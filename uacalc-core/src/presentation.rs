//! Presentation representation and operations for universal algebra
//!
//! This module provides presentation representation, equivalence checking,
//! normalization, and algebra construction from presentations.

use crate::{UACalcError, UACalcResult};
use crate::algebra::{Algebra, BasicAlgebra};
use crate::equation::{Equation, EquationComplexity, EquationProperties};
use crate::operation::OperationSymbol;
use crate::term::{Term, TermId, TermArena, eval_term};
use crate::term::variable::VariableAssignment;
use std::collections::{HashMap, HashSet};
use std::fmt;
// Note: Serialize/Deserialize removed for now due to complex dependencies

/// A presentation consists of a list of variables and equations (relations)
#[derive(Debug, Clone)]
pub struct Presentation {
    /// List of variable names
    pub variables: Vec<String>,
    /// List of equations (relations)
    pub equations: Vec<Equation>,
    /// Arena containing all terms
    arena: TermArena,
}

impl Presentation {
    /// Create a new presentation from variables and equations
    pub fn new(variables: Vec<String>, equations: Vec<Equation>) -> UACalcResult<Self> {
        // Validate that all equations use the same arena
        if let Some(first_arena) = equations.first().map(|eq| eq.arena()) {
            for equation in &equations {
                if !std::ptr::eq(equation.arena(), first_arena) {
                    return Err(UACalcError::InvalidOperation {
                        message: "All equations must use the same term arena".to_string()
                    });
                }
            }
        }

        let arena = equations.first()
            .map(|eq| eq.arena().clone())
            .unwrap_or_else(|| TermArena::new());

        Ok(Self {
            variables,
            equations,
            arena,
        })
    }

    /// Create a presentation from variable names and equation strings
    pub fn from_strings(
        variables: Vec<String>,
        equation_strings: Vec<(String, String)>,
    ) -> UACalcResult<Self> {
        let mut arena = TermArena::new();
        let mut equations = Vec::new();

        for (left_str, right_str) in equation_strings {
            let equation = Equation::from_strings(&mut arena, &left_str, &right_str)?;
            equations.push(equation);
        }

        Self::new(variables, equations)
    }

    /// Get the variables
    pub fn variables(&self) -> &[String] {
        &self.variables
    }

    /// Get the equations
    pub fn equations(&self) -> &[Equation] {
        &self.equations
    }

    /// Get the term arena
    pub fn arena(&self) -> &TermArena {
        &self.arena
    }

    /// Get all variables used in the equations
    pub fn used_variables(&self) -> UACalcResult<HashSet<String>> {
        let mut used_vars = HashSet::new();
        
        for equation in &self.equations {
            let left_vars = equation.left().variables(&self.arena)?;
            let right_vars = equation.right().variables(&self.arena)?;
            
            // Convert variable indices to names (assuming x0, x1, x2, ...)
            for var_idx in left_vars {
                used_vars.insert(format!("x{}", var_idx));
            }
            for var_idx in right_vars {
                used_vars.insert(format!("x{}", var_idx));
            }
        }
        
        Ok(used_vars)
    }

    /// Get all operation symbols used in the equations
    pub fn operation_symbols(&self) -> UACalcResult<HashSet<OperationSymbol>> {
        let mut symbols = HashSet::new();
        
        for equation in &self.equations {
            let left_ops = equation.left().operation_symbols(&self.arena)?;
            let right_ops = equation.right().operation_symbols(&self.arena)?;
            
            symbols.extend(left_ops);
            symbols.extend(right_ops);
        }
        
        Ok(symbols)
    }

    /// Check if the presentation is consistent (all declared variables are used)
    pub fn is_consistent(&self) -> UACalcResult<bool> {
        let used_vars = self.used_variables()?;
        let declared_vars: HashSet<String> = self.variables.iter().cloned().collect();
        
        // Check if all declared variables are used
        Ok(declared_vars.is_subset(&used_vars))
    }

    /// Check if the presentation is valid (all equations are well-formed)
    pub fn is_valid(&self) -> bool {
        self.equations.iter().all(|eq| {
            // Basic validation - equations should be well-formed
            eq.left().is_well_formed(&self.arena) && 
            eq.right().is_well_formed(&self.arena)
        })
    }

    /// Analyze properties of the presentation
    pub fn analyze_properties(&self) -> UACalcResult<PresentationProperties> {
        let mut properties = Vec::new();
        
        // Check consistency
        if self.is_consistent()? {
            properties.push("consistent".to_string());
        }
        
        // Check validity
        if self.is_valid() {
            properties.push("valid".to_string());
        }
        
        // Check complexity
        let equation_count = self.equations.len();
        if equation_count == 1 {
            properties.push("minimal".to_string());
            properties.push("single_equation".to_string());
        } else if equation_count > 5 {
            properties.push("complex".to_string());
        }
        
        // Check operation diversity
        let operation_symbols = self.operation_symbols()?;
        if operation_symbols.len() > 2 {
            properties.push("multiple_operations".to_string());
        }
        
        // Check for specific algebraic properties
        for equation in &self.equations {
            let eq_props = equation.analyze_properties()?;
            for prop in eq_props.properties {
                if !properties.contains(&prop) {
                    properties.push(prop);
                }
            }
        }
        
        let is_consistent = properties.contains(&"consistent".to_string());
        let is_valid = properties.contains(&"valid".to_string());
        
        Ok(PresentationProperties {
            properties,
            variable_count: self.variables.len(),
            equation_count: self.equations.len(),
            operation_count: operation_symbols.len(),
            is_consistent,
            is_valid,
        })
    }

    /// Check if two presentations are equivalent (structurally similar)
    pub fn is_equivalent_to(&self, other: &Presentation) -> UACalcResult<bool> {
        // Check if they have the same number of equations
        if self.equations.len() != other.equations.len() {
            return Ok(false);
        }
        
        // Check if they use the same operations
        let self_ops = self.operation_symbols()?;
        let other_ops = other.operation_symbols()?;
        if self_ops != other_ops {
            return Ok(false);
        }
        
        // For now, we do a simple structural comparison
        // In a full implementation, you'd want more sophisticated equivalence checking
        Ok(true)
    }

    /// Normalize the presentation (rename variables, reorder equations)
    pub fn normalize(&self) -> UACalcResult<Presentation> {
        let mut arena = TermArena::new();
        let mut equations = Vec::new();
        
        // Create variable mapping for normalization
        let mut var_mapping = HashMap::new();
        let mut next_var_idx = 0;
        
        // Collect all used variables
        let used_vars = self.used_variables()?;
        let mut sorted_vars: Vec<String> = used_vars.into_iter().collect();
        sorted_vars.sort();
        
        // Create mapping from old variable names to normalized names
        for var in &sorted_vars {
            var_mapping.insert(var.clone(), format!("x{}", next_var_idx));
            next_var_idx += 1;
        }
        
        // Process equations in sorted order
        let mut equation_strings: Vec<(String, String)> = self.equations.iter()
            .map(|eq| {
                let left_str = eq.left().to_string(&self.arena).unwrap_or_else(|_| "?".to_string());
                let right_str = eq.right().to_string(&self.arena).unwrap_or_else(|_| "?".to_string());
                (left_str, right_str)
            })
            .collect();
        
        // Sort equations for consistent ordering
        equation_strings.sort();
        
        // Create normalized equations
        for (left_str, right_str) in equation_strings {
            // Apply variable renaming
            let normalized_left = self._apply_variable_mapping(&left_str, &var_mapping);
            let normalized_right = self._apply_variable_mapping(&right_str, &var_mapping);
            
            let equation = Equation::from_strings(&mut arena, &normalized_left, &normalized_right)?;
            equations.push(equation);
        }
        
        // Create normalized variable list
        let normalized_variables: Vec<String> = (0..next_var_idx)
            .map(|i| format!("x{}", i))
            .collect();
        
        Presentation::new(normalized_variables, equations)
    }

    /// Apply variable mapping to a term string
    fn _apply_variable_mapping(&self, term_str: &str, mapping: &HashMap<String, String>) -> String {
        let mut result = term_str.to_string();
        for (old_var, new_var) in mapping {
            result = result.replace(old_var, new_var);
        }
        result
    }

    /// Check if an algebra satisfies this presentation
    pub fn is_satisfied_by(&self, algebra: &BasicAlgebra) -> UACalcResult<bool> {
        // Sample a subset of variable assignments to check satisfaction
        let sample_size = std::cmp::min(100, algebra.cardinality().pow(3));
        
        for equation in &self.equations {
            if !self._check_equation_satisfaction(equation, algebra, sample_size)? {
                return Ok(false);
            }
        }
        
        Ok(true)
    }

    /// Check if a single equation is satisfied by an algebra
    fn _check_equation_satisfaction(
        &self,
        equation: &Equation,
        algebra: &BasicAlgebra,
        sample_size: usize,
    ) -> UACalcResult<bool> {
        let left_vars = equation.left().variables(&self.arena)?;
        let right_vars = equation.right().variables(&self.arena)?;
        let all_vars: HashSet<u8> = left_vars.into_iter().chain(right_vars).collect();
        
        // Generate sample assignments
        for _ in 0..sample_size {
            let mut assignment = VariableAssignment::new();
            for &var_idx in &all_vars {
                let value = fastrand::usize(0..algebra.cardinality()) as u8;
                assignment.assign(var_idx, value as usize);
            }
            
            let left_value = eval_term(equation.left, &self.arena, algebra, &assignment)?;
            let right_value = eval_term(equation.right, &self.arena, algebra, &assignment)?;
            
            if left_value != right_value {
                return Ok(false);
            }
        }
        
        Ok(true)
    }
}

impl fmt::Display for Presentation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        writeln!(f, "Presentation:")?;
        writeln!(f, "  Variables: {:?}", self.variables)?;
        writeln!(f, "  Equations:")?;
        for (i, equation) in self.equations.iter().enumerate() {
            writeln!(f, "    {}: {}", i + 1, equation)?;
        }
        Ok(())
    }
}

/// Properties of a presentation
#[derive(Debug, Clone)]
pub struct PresentationProperties {
    pub properties: Vec<String>,
    pub variable_count: usize,
    pub equation_count: usize,
    pub operation_count: usize,
    pub is_consistent: bool,
    pub is_valid: bool,
}

impl fmt::Display for PresentationProperties {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        writeln!(f, "Presentation Properties:")?;
        writeln!(f, "  Variables: {}", self.variable_count)?;
        writeln!(f, "  Equations: {}", self.equation_count)?;
        writeln!(f, "  Operations: {}", self.operation_count)?;
        writeln!(f, "  Consistent: {}", self.is_consistent)?;
        writeln!(f, "  Valid: {}", self.is_valid)?;
        writeln!(f, "  Properties: {:?}", self.properties)?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_presentation_creation() {
        let variables = vec!["x".to_string(), "y".to_string()];
        let equations = vec![
            ("f(x,y)".to_string(), "f(y,x)".to_string()),
            ("f(x,x)".to_string(), "x".to_string()),
        ];
        
        let presentation = Presentation::from_strings(variables, equations).unwrap();
        assert_eq!(presentation.variables().len(), 2);
        assert_eq!(presentation.equations().len(), 2);
    }

    #[test]
    fn test_presentation_properties() {
        let variables = vec!["x".to_string(), "y".to_string()];
        let equations = vec![
            ("f(x,y)".to_string(), "f(y,x)".to_string()),
        ];
        
        let presentation = Presentation::from_strings(variables, equations).unwrap();
        let properties = presentation.analyze_properties().unwrap();
        
        assert!(properties.is_valid);
        assert_eq!(properties.equation_count, 1);
        assert!(properties.properties.contains(&"minimal".to_string()));
    }

    #[test]
    fn test_presentation_normalization() {
        let variables = vec!["a".to_string(), "b".to_string()];
        let equations = vec![
            ("f(a,b)".to_string(), "f(b,a)".to_string()),
        ];
        
        let presentation = Presentation::from_strings(variables, equations).unwrap();
        let normalized = presentation.normalize().unwrap();
        
        assert_eq!(normalized.variables(), &["x0", "x1"]);
    }
}
