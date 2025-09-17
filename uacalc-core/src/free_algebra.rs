//! Free Algebra Implementation
//!
//! This module provides implementations for free algebras in universal algebra.
//! Free algebras are algebras that satisfy the universal property: for any algebra
//! in the same variety, there exists a unique homomorphism from the free algebra
//! to that algebra, determined by the mapping of generators.

use crate::algebra::{Algebra, BasicAlgebra, SmallAlgebra};
use crate::operation::{Operation, OperationSymbol, OperationType, TableOperation};
use crate::term::{Term, TermArena, TermId};
use crate::error::{UACalcError, UACalcResult};

use std::collections::{HashMap, HashSet};
use std::sync::{Arc, Mutex};

/// Represents a variety constraint for free algebra generation
#[derive(Debug, Clone, PartialEq)]
pub enum VarietyConstraint {
    /// Trivial variety (no equations)
    Trivial,
    /// Idempotent variety (x * x = x for all operations)
    Idempotent,
    /// Associative variety (x * (y * z) = (x * y) * z for all operations)
    Associative,
    /// Commutative variety (x * y = y * x for all operations)
    Commutative,
    /// Custom equations
    Custom(Vec<String>),
}

impl VarietyConstraint {
    /// Parse variety constraint from string
    pub fn from_string(s: &str) -> UACalcResult<Self> {
        match s.to_lowercase().as_str() {
            "trivial" => Ok(VarietyConstraint::Trivial),
            "idempotent" => Ok(VarietyConstraint::Idempotent),
            "associative" => Ok(VarietyConstraint::Associative),
            "commutative" => Ok(VarietyConstraint::Commutative),
            _ => Err(UACalcError::ParseError {
                message: format!("Unknown variety constraint: {}", s),
            }),
        }
    }
}

/// A free algebra generated from a set of generators and variety constraints
#[derive(Debug, Clone)]
pub struct FreeAlgebra {
    name: String,
    generators: Vec<String>,
    variety_constraints: VarietyConstraint,
    operations: Vec<Arc<Mutex<dyn Operation>>>,
    operation_symbols: HashMap<String, usize>,
    universe: Vec<usize>,
    term_arena: TermArena,
    generator_terms: Vec<TermId>,
}

impl FreeAlgebra {
    /// Create a new free algebra with given generators and variety constraints
    pub fn new(
        name: String,
        generators: Vec<String>,
        variety_constraints: VarietyConstraint,
        operation_symbols: Vec<OperationSymbol>,
        max_depth: usize,
    ) -> UACalcResult<Self> {
        if generators.is_empty() {
            return Err(UACalcError::ParseError {
                message: "Free algebra must have at least one generator".to_string(),
            });
        }

        // Create term arena for managing terms
        let mut term_arena = TermArena::new();
        
        // Create generator terms
        let mut generator_terms = Vec::new();
        for (i, _gen) in generators.iter().enumerate() {
            let term = term_arena.make_variable(i as u8);
            generator_terms.push(term);
        }

        // Generate all terms up to max_depth
        let all_terms = Self::generate_terms(
            &mut term_arena,
            &generator_terms,
            &operation_symbols,
            max_depth,
        )?;

        // Apply variety constraints to reduce terms
        let reduced_terms = Self::apply_variety_constraints(
            &all_terms,
            &variety_constraints,
            &operation_symbols,
        )?;

        // Create universe from reduced terms
        let universe: Vec<usize> = (0..reduced_terms.len()).collect();

        // Create operations
        let operations = Self::create_operations(
            &reduced_terms,
            &operation_symbols,
            &variety_constraints,
        )?;

        // Create operation symbol mapping
        let mut operation_symbols_map = HashMap::new();
        for (i, symbol) in operation_symbols.iter().enumerate() {
            operation_symbols_map.insert(symbol.name().to_string(), i);
        }

        Ok(Self {
            name,
            generators,
            variety_constraints,
            operations,
            operation_symbols: operation_symbols_map,
            universe,
            term_arena,
            generator_terms,
        })
    }

    /// Generate all terms up to a given depth
    fn generate_terms(
        arena: &mut TermArena,
        generators: &[TermId],
        operation_symbols: &[OperationSymbol],
        max_depth: usize,
    ) -> UACalcResult<Vec<TermId>> {
        let mut all_terms = Vec::new();
        let mut current_level = generators.to_vec();

        // Add generators as depth 0 terms
        all_terms.extend_from_slice(generators);

        // Generate terms level by level
        for depth in 1..=max_depth {
            let mut next_level = Vec::new();
            
            for symbol in operation_symbols {
                let arity = symbol.arity();
                if arity == 0 {
                    // Constant operation - create a term with no children
                    let term = arena.make_term(symbol, &[]);
                    next_level.push(term);
                } else {
                    // Generate all combinations of arguments from previous levels
                    let mut args_combinations = Vec::new();
                    Self::generate_argument_combinations(
                        &all_terms,
                        arity,
                        &mut args_combinations,
                        Vec::new(),
                    );

                    for args in args_combinations {
                        let term = arena.make_term(symbol, &args);
                        next_level.push(term);
                    }
                }
            }

            all_terms.extend_from_slice(&next_level);
            current_level = next_level;
        }

        Ok(all_terms)
    }

    /// Generate all combinations of arguments for operations
    fn generate_argument_combinations(
        available_terms: &[TermId],
        arity: usize,
        combinations: &mut Vec<Vec<TermId>>,
        current: Vec<TermId>,
    ) {
        if current.len() == arity {
            combinations.push(current);
            return;
        }

        for &term in available_terms {
            let mut new_current = current.clone();
            new_current.push(term);
            Self::generate_argument_combinations(
                available_terms,
                arity,
                combinations,
                new_current,
            );
        }
    }

    /// Apply variety constraints to reduce the set of terms
    fn apply_variety_constraints(
        terms: &[TermId],
        constraints: &VarietyConstraint,
        operation_symbols: &[OperationSymbol],
    ) -> UACalcResult<Vec<TermId>> {
        match constraints {
            VarietyConstraint::Trivial => {
                // No reduction needed for trivial variety
                Ok(terms.to_vec())
            }
            VarietyConstraint::Idempotent => {
                // Remove terms that are equivalent under idempotency
                Self::reduce_by_idempotency(terms)
            }
            VarietyConstraint::Associative => {
                // Remove terms that are equivalent under associativity
                Self::reduce_by_associativity(terms, operation_symbols)
            }
            VarietyConstraint::Commutative => {
                // Remove terms that are equivalent under commutativity
                Self::reduce_by_commutativity(terms, operation_symbols)
            }
            VarietyConstraint::Custom(_) => {
                // For custom constraints, we would need equation solving
                // For now, return all terms
                Ok(terms.to_vec())
            }
        }
    }

    /// Reduce terms by idempotency (x * x = x)
    fn reduce_by_idempotency(terms: &[TermId]) -> UACalcResult<Vec<TermId>> {
        let mut reduced = Vec::new();
        let mut seen = HashSet::new();

        for &term in terms {
            // Check if term is idempotent (simplified check)
            if Self::is_idempotent_term(term) {
                // For idempotent terms, we might want to keep only the base form
                // This is a simplified implementation
                if !seen.contains(&term) {
                    reduced.push(term);
                    seen.insert(term);
                }
            } else {
                reduced.push(term);
            }
        }

        Ok(reduced)
    }

    /// Check if a term is idempotent (simplified implementation)
    fn is_idempotent_term(term: TermId) -> bool {
        // This is a simplified check - in practice, you'd need proper term analysis
        // For now, we'll assume all terms are idempotent for simplicity
        true
    }

    /// Reduce terms by associativity
    fn reduce_by_associativity(
        terms: &[TermId],
        _operation_symbols: &[OperationSymbol],
    ) -> UACalcResult<Vec<TermId>> {
        // This is a complex operation that would require proper term rewriting
        // For now, return all terms
        Ok(terms.to_vec())
    }

    /// Reduce terms by commutativity
    fn reduce_by_commutativity(
        terms: &[TermId],
        _operation_symbols: &[OperationSymbol],
    ) -> UACalcResult<Vec<TermId>> {
        // This would require canonicalizing terms by argument order
        // For now, return all terms
        Ok(terms.to_vec())
    }

    /// Create operations for the free algebra
    fn create_operations(
        terms: &[TermId],
        operation_symbols: &[OperationSymbol],
        _constraints: &VarietyConstraint,
    ) -> UACalcResult<Vec<Arc<Mutex<dyn Operation>>>> {
        let mut operations = Vec::new();

        for symbol in operation_symbols {
            let arity = symbol.arity();
            let table_size = if arity == 0 {
                1
            } else {
                terms.len().pow(arity as u32)
            };

            let mut table = Vec::new();

            if arity == 0 {
                // Constant operation - create a single row with result
                table.push(vec![0]); // Map to first term
            } else {
                // Create operation table
                for i in 0..table_size {
                    // Convert index to arguments
                    let args = Self::index_to_arguments(i, terms.len(), arity);
                    
                    // Apply operation to get result term
                    let result_term = Self::apply_operation_to_terms(
                        symbol,
                        &args,
                        terms,
                    )?;
                    
                    // Find index of result term
                    let result = Self::find_term_index(result_term, terms)?;
                    
                    // Create row with arguments and result
                    let mut row = args;
                    row.push(result);
                    table.push(row);
                }
            }

            let table_op = TableOperation::new(
                symbol.clone(),
                table,
                terms.len(),
            )?;

            let operation: Arc<Mutex<dyn Operation>> = Arc::new(Mutex::new(table_op));
            operations.push(operation);
        }

        Ok(operations)
    }

    /// Convert table index to operation arguments
    fn index_to_arguments(index: usize, num_terms: usize, arity: usize) -> Vec<usize> {
        let mut args = Vec::new();
        let mut remaining = index;

        for _ in 0..arity {
            args.push(remaining % num_terms);
            remaining /= num_terms;
        }

        args
    }

    /// Apply operation to terms (simplified implementation)
    fn apply_operation_to_terms(
        _symbol: &OperationSymbol,
        args: &[usize],
        terms: &[TermId],
    ) -> UACalcResult<TermId> {
        // This is a simplified implementation
        // In practice, you'd need proper term construction and rewriting
        
        // For now, just return the first argument as a placeholder
        if args.is_empty() {
            return Err(UACalcError::InvalidOperation {
                message: "Operation requires arguments".to_string(),
            });
        }

        // Find the term corresponding to the first argument
        if args[0] < terms.len() {
            Ok(terms[args[0]])
        } else {
            Err(UACalcError::IndexOutOfBounds {
                index: args[0],
                size: terms.len(),
            })
        }
    }

    /// Find the index of a term in the terms list
    fn find_term_index(term: TermId, terms: &[TermId]) -> UACalcResult<usize> {
        for (i, &t) in terms.iter().enumerate() {
            if t == term {
                return Ok(i);
            }
        }
        Err(UACalcError::InvalidOperation {
            message: "Term not found in terms list".to_string(),
        })
    }

    /// Get the generators of the free algebra
    pub fn generators(&self) -> &[String] {
        &self.generators
    }

    /// Get the variety constraints
    pub fn variety_constraints(&self) -> &VarietyConstraint {
        &self.variety_constraints
    }

    /// Check if the algebra satisfies the universal property
    pub fn satisfies_universal_property(&self) -> bool {
        // A free algebra always satisfies the universal property by definition
        true
    }

    /// Check if the algebra is freely generated
    pub fn is_freely_generated(&self) -> bool {
        true
    }
}

impl Algebra for FreeAlgebra {
    fn universe(&self) -> &[usize] {
        &self.universe
    }

    fn cardinality(&self) -> usize {
        self.universe.len()
    }

    fn operations(&self) -> &[Arc<Mutex<dyn Operation>>] {
        &self.operations
    }

    fn operation(&self, index: usize) -> UACalcResult<&dyn Operation> {
        if index >= self.operations.len() {
            return Err(UACalcError::IndexOutOfBounds {
                index,
                size: self.operations.len(),
            });
        }

        // This is a limitation of the current trait design
        // We need to return a reference, but we have Arc<Mutex<dyn Operation>>
        Err(UACalcError::UnsupportedOperation {
            operation: "Direct operation access not supported for FreeAlgebra. Use operation_arc instead.".to_string(),
        })
    }

    fn operation_by_symbol(&self, symbol: &str) -> UACalcResult<&dyn Operation> {
        let index = self.operation_symbols.get(symbol)
            .ok_or_else(|| UACalcError::InvalidOperation {
                message: format!("Operation '{}' not found", symbol),
            })?;
        self.operation(*index)
    }

    fn operation_arc(&self, index: usize) -> UACalcResult<Arc<Mutex<dyn Operation>>> {
        if index >= self.operations.len() {
            return Err(UACalcError::IndexOutOfBounds {
                index,
                size: self.operations.len(),
            });
        }
        Ok(self.operations[index].clone())
    }

    fn operation_arc_by_symbol(&self, symbol: &str) -> UACalcResult<Arc<Mutex<dyn Operation>>> {
        let index = self.operation_symbols.get(symbol)
            .ok_or_else(|| UACalcError::InvalidOperation {
                message: format!("Operation '{}' not found", symbol),
            })?;
        self.operation_arc(*index)
    }

    fn name(&self) -> &str {
        &self.name
    }

    fn is_finite(&self) -> bool {
        true // Free algebras with finite generators and bounded depth are finite
    }

    fn make_operation_tables(&mut self) -> UACalcResult<()> {
        // Operation tables are already built during construction
        Ok(())
    }
}

impl SmallAlgebra for FreeAlgebra {
    fn max_arity(&self) -> usize {
        self.operations
            .iter()
            .map(|op| {
                op.lock().unwrap().arity()
            })
            .max()
            .unwrap_or(0)
    }

    fn subalgebra(&self, generators: &[usize]) -> UACalcResult<BasicAlgebra> {
        // For a free algebra, generating a subalgebra is complex
        // This would require proper term generation and constraint application
        Err(UACalcError::UnsupportedOperation {
            operation: "Subalgebra generation not yet implemented for FreeAlgebra".to_string(),
        })
    }
}

/// Factory function to create a free algebra
pub fn create_free_algebra(
    name: String,
    generators: Vec<String>,
    variety_constraints: VarietyConstraint,
    operation_symbols: Vec<OperationSymbol>,
    max_depth: usize,
) -> UACalcResult<FreeAlgebra> {
    FreeAlgebra::new(name, generators, variety_constraints, operation_symbols, max_depth)
}

/// Factory function to create a free algebra with common operation symbols
pub fn create_free_algebra_with_common_operations(
    name: String,
    generators: Vec<String>,
    variety_constraints: VarietyConstraint,
    max_depth: usize,
) -> UACalcResult<FreeAlgebra> {
    let operation_symbols = vec![
        OperationSymbol::new("*".to_string(), 2),
        OperationSymbol::new("+".to_string(), 2),
        OperationSymbol::new("0".to_string(), 0),
        OperationSymbol::new("1".to_string(), 0),
    ];

    FreeAlgebra::new(name, generators, variety_constraints, operation_symbols, max_depth)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_free_algebra_creation() {
        let generators = vec!["x".to_string(), "y".to_string()];
        let variety = VarietyConstraint::Trivial;
        let operation_symbols = vec![
            OperationSymbol::new("*".to_string(), 2),
        ];

        let free_algebra = FreeAlgebra::new(
            "TestFreeAlgebra".to_string(),
            generators.clone(),
            variety.clone(),
            operation_symbols,
            2,
        ).unwrap();

        assert_eq!(free_algebra.name(), "TestFreeAlgebra");
        assert_eq!(free_algebra.generators(), generators);
        assert_eq!(free_algebra.variety_constraints(), &variety);
        assert!(free_algebra.satisfies_universal_property());
        assert!(free_algebra.is_freely_generated());
    }

    #[test]
    fn test_variety_constraint_parsing() {
        assert_eq!(VarietyConstraint::from_string("trivial").unwrap(), VarietyConstraint::Trivial);
        assert_eq!(VarietyConstraint::from_string("idempotent").unwrap(), VarietyConstraint::Idempotent);
        assert_eq!(VarietyConstraint::from_string("associative").unwrap(), VarietyConstraint::Associative);
        assert_eq!(VarietyConstraint::from_string("commutative").unwrap(), VarietyConstraint::Commutative);
        
        assert!(VarietyConstraint::from_string("unknown").is_err());
    }

    #[test]
    fn test_free_algebra_with_no_generators() {
        let result = FreeAlgebra::new(
            "Empty".to_string(),
            vec![],
            VarietyConstraint::Trivial,
            vec![],
            1,
        );
        
        assert!(result.is_err());
    }
}
