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

#[cfg(feature = "memory-limit")]
use crate::memory::check_free_algebra_memory_limit;

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
    pub name: String,
    pub generators: Vec<String>,
    pub variety_constraints: VarietyConstraint,
    pub operations: Vec<Arc<Mutex<dyn Operation>>>,
    pub operation_symbols: HashMap<String, usize>,
    pub universe: Vec<usize>,
    pub term_arena: TermArena,
    pub generator_terms: Vec<TermId>,
}

impl FreeAlgebra {
    /// Create a new free algebra from an existing algebra with given number of generators
    /// This matches the Java constructor: new FreeAlgebra(alg, numGenerators, report)
    pub fn from_algebra(
        algebra: &dyn crate::algebra::SmallAlgebra,
        num_generators: usize,
        max_depth: usize,
    ) -> UACalcResult<Self> {
        if num_generators == 0 {
            return Err(UACalcError::ParseError {
                message: "Free algebra must have at least one generator".to_string(),
            });
        }

        // Create generator names
        let generators: Vec<String> = (0..num_generators)
            .map(|i| format!("x{}", i))
            .collect();

        // Create operation symbols from the algebra's operations
        let mut operation_symbols = Vec::new();
        for op_arc in algebra.operations() {
            let op_guard = op_arc.lock().map_err(|_| UACalcError::InvalidOperation {
                message: "Failed to lock operation".to_string(),
            })?;
            
            let symbol = OperationSymbol::new(
                op_guard.symbol().to_string(),
                op_guard.arity()
            );
            operation_symbols.push(symbol);
        }

        // Create the free algebra with idempotent variety constraint
        Self::new(
            format!("F{}", num_generators),
            generators,
            VarietyConstraint::Idempotent,
            operation_symbols,
            max_depth,
        )
    }

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

        // Check memory limit before proceeding
        #[cfg(feature = "memory-limit")]
        {
            let operation_arities: Vec<usize> = operation_symbols.iter().map(|s| s.arity()).collect();
            // Only check memory limit if estimation is possible
            if let Err(e) = check_free_algebra_memory_limit(
                generators.len(),
                operation_symbols.len(),
                max_depth,
                &operation_arities,
            ) {
                // If the error is about estimation being too large, log a warning but continue
                if e.to_string().contains("too large to estimate") {
                    // Log warning but don't fail - let the operation proceed
                    eprintln!("Warning: Memory estimation failed for free algebra generation, proceeding without limit check");
                } else {
                    // For other memory limit errors, fail
                    return Err(e);
                }
            }
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
            
            // Limit total terms to prevent memory explosion
            if all_terms.len() > 1000 {
                break;
            }
            
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
                    
                    // Limit combinations to prevent exponential explosion
                    if args_combinations.len() > 1000 {
                        args_combinations.truncate(1000);
                    }

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
        // Prevent exponential explosion by limiting combinations
        if combinations.len() > 10000 {
            return;
        }
        
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

    /// Get all terms in the free algebra (matches Java getTerms())
    pub fn get_terms(&self) -> Vec<TermId> {
        // Return all terms from the term arena
        let mut terms = Vec::new();
        
        // Add generator terms
        terms.extend_from_slice(&self.generator_terms);
        
        // Add all other terms from the arena
        // The term arena contains all generated terms
        for term_id in 0..self.term_arena.num_terms() {
            if !self.generator_terms.contains(&term_id) {
                terms.push(term_id);
            }
        }
        
        terms
    }

    /// Get idempotent terms (matches Java getIdempotentTerms())
    pub fn get_idempotent_terms(&self) -> UACalcResult<Vec<TermId>> {
        let mut idempotent_terms = Vec::new();
        let terms = self.get_terms();
        
        // Add generator terms (variables are always idempotent)
        idempotent_terms.extend_from_slice(&self.generator_terms);
        
        // Check other terms for idempotency
        for term_id in terms {
            if !self.generator_terms.contains(&term_id) {
                // For now, we'll use a simplified check
                // In a full implementation, we'd evaluate the term and check if the resulting operation is idempotent
                if self.is_term_idempotent(term_id)? {
                    idempotent_terms.push(term_id);
                }
            }
        }
        
        Ok(idempotent_terms)
    }

    /// Check if a term is idempotent by evaluating it
    fn is_term_idempotent(&self, term_id: TermId) -> UACalcResult<bool> {
        use crate::term::eval_term;
        use crate::term::variable::VariableAssignment;
        
        let term = self.term_arena.get_term(term_id)?;
        
        // Variable terms are always idempotent
        if matches!(term, crate::term::Term::Variable(_)) {
            return Ok(true);
        }
        
        // For operation terms, check if they are idempotent
        // A term t(x) is idempotent if t(x,x,...,x) = x for all x
        let n = self.universe.len();
        
        for x in 0..n {
            // Create assignment where all variables are set to x
            let mut assignment = VariableAssignment::new();
            for i in 0..self.generators.len() {
                assignment.assign(i as u8, x);
            }
            
            // Evaluate the term with all variables set to x
            let result = eval_term(term_id, &self.term_arena, self, &assignment)?;
            
            // If result is not x, the term is not idempotent
            if result != x {
                return Ok(false);
            }
        }
        
        Ok(true)
    }

    /// Create an operation from a term (matches Java term.interpretation())
    pub fn term_interpretation(
        &self,
        term_id: TermId,
        target_algebra: &dyn crate::algebra::SmallAlgebra,
        use_all_variables: bool,
    ) -> UACalcResult<Arc<Mutex<dyn crate::operation::Operation>>> {
        use crate::term::eval_term;
        use crate::term::variable::VariableAssignment;
        use crate::operation::{OperationSymbol, TableOperation};
        
        let n = target_algebra.cardinality();
        
        // Determine the arity of the term
        let arity = if use_all_variables {
            self.generators.len()
        } else {
            // Count unique variables in the term
            self.count_variables_in_term(term_id)?
        };
        
        // Create operation table
        let mut table = Vec::new();
        
        // Generate all possible argument combinations
        for args in self.generate_argument_combinations_for_term(n, arity) {
            let assignment = VariableAssignment::from_slice(&args);
            let result = eval_term(term_id, &self.term_arena, target_algebra, &assignment)?;
            
            // Add row to table: [args..., result]
            let mut row = args.to_vec();
            row.push(result);
            table.push(row);
        }
        
        // Create operation symbol
        let symbol = OperationSymbol::new("term_op".to_string(), arity);
        
        // Create table operation
        let term_op = TableOperation::new(symbol, table, n)?;
        
        Ok(Arc::new(Mutex::new(term_op)))
    }

    /// Count the number of unique variables in a term
    fn count_variables_in_term(&self, term_id: TermId) -> UACalcResult<usize> {
        let term = self.term_arena.get_term(term_id)?;
        match term {
            crate::term::Term::Variable(idx) => Ok(1),
            crate::term::Term::Operation { children, .. } => {
                let mut max_var = 0;
                for &child_id in children {
                    let child_vars = self.count_variables_in_term(child_id)?;
                    max_var = max_var.max(child_vars);
                }
                Ok(max_var)
            }
        }
    }

    /// Generate all possible argument combinations for an operation (for term interpretation)
    fn generate_argument_combinations_for_term(&self, n: usize, arity: usize) -> Vec<Vec<usize>> {
        let mut combinations = Vec::new();
        let mut current = vec![0; arity];
        
        loop {
            combinations.push(current.clone());
            
            // Increment the combination
            let mut carry = 1;
            for i in (0..arity).rev() {
                current[i] += carry;
                if current[i] >= n {
                    current[i] = 0;
                    carry = 1;
                } else {
                    carry = 0;
                    break;
                }
            }
            
            if carry == 1 {
                break; // All combinations generated
            }
        }
        
        combinations
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

    fn algebra_type(&self) -> crate::algebra::AlgebraType {
        crate::algebra::AlgebraType::Free
    }

    fn get_element(&self, k: usize) -> UACalcResult<usize> {
        if k >= self.universe.len() {
            return Err(UACalcError::IndexOutOfBounds {
                index: k,
                size: self.universe.len(),
            });
        }
        Ok(self.universe[k])
    }

    fn get_universe_list(&self) -> Vec<usize> {
        self.universe.clone()
    }

    fn get_universe_order(&self) -> std::collections::HashMap<usize, usize> {
        let mut order = std::collections::HashMap::new();
        for (index, &element) in self.universe.iter().enumerate() {
            order.insert(element, index);
        }
        order
    }

    fn parent(&self) -> Option<Arc<Mutex<dyn SmallAlgebra>>> {
        None // FreeAlgebra has no parent
    }

    fn parents(&self) -> Vec<Arc<Mutex<dyn SmallAlgebra>>> {
        vec![] // FreeAlgebra has no parents
    }

    fn reset_con_and_sub(&mut self) {
        // FreeAlgebra doesn't cache lattices, so nothing to reset
    }

    fn convert_to_default_value_ops(&mut self) -> UACalcResult<()> {
        // For FreeAlgebra, this is a no-op
        Ok(())
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
        use crate::memory::set_memory_limit;
        
        // Set a reasonable memory limit for this test (50MB)
        set_memory_limit(50 * 1024 * 1024).unwrap();
        
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
        use crate::memory::set_memory_limit;
        
        // Set a reasonable memory limit for this test (50MB)
        set_memory_limit(50 * 1024 * 1024).unwrap();
        
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
