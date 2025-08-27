//! Term evaluation engine for zero-allocation recursive evaluation
//!
//! This module provides efficient term evaluation using stack-based
//! iterative algorithms to avoid function call overhead.

use crate::algebra::SmallAlgebra;
use crate::operation::Operation;
use crate::term::variable::VariableAssignment;
use crate::term::{Term, TermArena, TermId, MAX_DEPTH};
use crate::utils::MAX_OPERATION_ARITY;
use crate::{UACalcError, UACalcResult};
use arrayvec::ArrayVec;
use std::collections::{HashMap, HashSet};

/// Compact stack frame for evaluation
#[derive(Debug, Clone, Copy)]
struct StackFrame {
    /// Term ID being evaluated
    term_id: TermId,
    /// Whether this term has been evaluated
    evaluated: bool,
}

impl StackFrame {
    fn new(term_id: TermId) -> Self {
        Self {
            term_id,
            evaluated: false,
        }
    }
}

/// Evaluation context for term evaluation with zero/minimal allocation
pub struct EvaluationContext<'a> {
    /// Reference to the algebra
    algebra: &'a dyn SmallAlgebra,
    /// Variable assignment
    variables: &'a VariableAssignment,
    /// Operation cache for fast lookup - tracks which operations have flat tables
    flat_table_ops: HashSet<usize>,
    /// Symbol name to operation index mapping
    name_to_op: HashMap<String, usize>,
    /// Evaluation stack for iterative evaluation using compact frames
    stack: ArrayVec<StackFrame, MAX_DEPTH>,
    /// Results cache for evaluated terms - indexed by TermId
    results: Vec<Option<usize>>,
    /// Strict evaluation mode - checks variable bounds
    strict: bool,
    /// Maximum arity seen in operations (for pre-validation)
    max_arity: usize,
}

impl<'a> EvaluationContext<'a> {
    /// Create a new evaluation context
    pub fn new(algebra: &'a dyn SmallAlgebra, variables: &'a VariableAssignment) -> Self {
        let operations = algebra.operations();
        
        // Build symbol name to operation index mapping
        let mut name_to_op = HashMap::new();
        for (idx, operation) in operations.iter().enumerate() {
            if let Ok(op_guard) = operation.lock() {
                name_to_op.insert(op_guard.symbol().name().to_string(), idx);
            }
        }

        Self {
            algebra,
            variables,
            flat_table_ops: HashSet::new(),
            name_to_op,
            stack: ArrayVec::new(),
            results: Vec::new(),
            strict: false,
            max_arity: 0,
        }
    }

    /// Create a new evaluation context with strict mode
    pub fn new_strict(algebra: &'a dyn SmallAlgebra, variables: &'a VariableAssignment) -> Self {
        let mut context = Self::new(algebra, variables);
        context.strict = true;
        context
    }

    /// Set strict evaluation mode
    pub fn set_strict(&mut self, strict: bool) {
        self.strict = strict;
    }

    /// Check if strict mode is enabled
    pub fn is_strict(&self) -> bool {
        self.strict
    }

    /// Pre-validate term arities to avoid bounds checks in hot loops
    fn validate_term_arities(&mut self, arena: &TermArena) -> UACalcResult<()> {
        for term_id in 0..arena.num_terms() {
            if let Ok(term) = arena.get_term(term_id) {
                if let Term::Operation { children, .. } = term {
                    if children.len() > MAX_OPERATION_ARITY {
                        return Err(UACalcError::InvalidOperation {
                            message: format!(
                                "Term {} has arity {} > MAX_OPERATION_ARITY ({})",
                                term_id,
                                children.len(),
                                MAX_OPERATION_ARITY
                            ),
                        });
                    }
                    self.max_arity = self.max_arity.max(children.len());
                }
            }
        }
        Ok(())
    }

    /// Ensure results cache has capacity for all terms in arena
    fn ensure_cache_capacity(&mut self, arena: &TermArena) {
        let needed_capacity = arena.num_terms();
        if self.results.len() < needed_capacity {
            self.results.resize_with(needed_capacity, || None);
        }
    }

    /// Evaluate a term using iterative stack-based algorithm with zero allocation
    pub fn eval_term(&mut self, term_id: TermId, arena: &TermArena) -> UACalcResult<usize> {
        // Pre-validate arities and ensure cache capacity
        self.validate_term_arities(arena)?;
        self.ensure_cache_capacity(arena);

        // Check if already evaluated
        if let Some(Some(result)) = self.results.get(term_id) {
            return Ok(*result);
        }

        // Clear stack and push initial term
        self.stack.clear();
        self.stack.push(StackFrame::new(term_id));

        // Main evaluation loop
        while !self.stack.is_empty() {
            let frame_idx = self.stack.len() - 1;
            let frame = &mut self.stack[frame_idx];

            if frame.evaluated {
                // Term is evaluated, pop it and store result
                let term_id_to_pop = frame.term_id;
                let result = self.results[term_id_to_pop].unwrap();
                self.stack.pop();

                // If this was the original term, we're done
                if term_id_to_pop == term_id {
                    return Ok(result);
                }
            } else {
                // Mark as evaluated and process children
                frame.evaluated = true;
                let current_term_id = frame.term_id;
                let term = arena.get_term(current_term_id)?;

                match term {
                    Term::Variable(index) => {
                        // Variable evaluation is immediate
                        let value = self.variables.get(*index);
                        self.results[current_term_id] = Some(value);
                    }
                    Term::Operation {
                        symbol_id,
                        children,
                    } => {
                        // Check if all children are evaluated
                        let mut all_children_evaluated = true;
                        for &child_id in children {
                            if self.results[child_id].is_none() {
                                all_children_evaluated = false;
                                break;
                            }
                        }

                        if all_children_evaluated {
                            // All children evaluated, compute operation result
                            let result = self.evaluate_operation(*symbol_id, children, arena)?;
                            self.results[current_term_id] = Some(result);
                        } else {
                            // Push children onto stack first (in reverse order for correct evaluation)
                            for &child_id in children.iter().rev() {
                                if self.results[child_id].is_none() {
                                    // Check for stack overflow
                                    if self.stack.len() >= MAX_DEPTH {
                                        return Err(UACalcError::InvalidOperation {
                                            message: format!("Evaluation stack overflow: term depth exceeds MAX_DEPTH ({})", MAX_DEPTH),
                                        });
                                    }
                                    self.stack.push(StackFrame::new(child_id));
                                }
                            }
                        }
                    }
                }
            }
        }

        Err(UACalcError::InvalidOperation {
            message: "Evaluation stack underflow".to_string(),
        })
    }

    /// Evaluate an operation with given arguments using stack-allocated args
    fn evaluate_operation(
        &mut self,
        symbol_id: u16,
        children: &[TermId],
        arena: &TermArena,
    ) -> UACalcResult<usize> {
        // Resolve symbol_id to operation index via symbol name
        let symbol = arena.get_symbol(symbol_id)?;
        let name = symbol.name();
        let op_idx = self.name_to_op.get(name).copied().ok_or_else(|| UACalcError::InvalidOperation {
            message: format!("Operation '{}' not found in algebra", name),
        })?;

        let operations = self.algebra.operations();
        let operation = &operations[op_idx];

        // Collect argument values using stack-allocated array
        let mut args: ArrayVec<usize, MAX_OPERATION_ARITY> = ArrayVec::new();
        for &child_id in children {
            let value = self.results[child_id].unwrap();
            args.push(value);
        }

        // Lock the operation and check if it has a flat table available
        let op_guard = operation
            .lock()
            .map_err(|_| UACalcError::InvalidOperation {
                message: "Failed to lock operation".to_string(),
            })?;
        let has_table = self.check_operation_table(&*op_guard, op_idx);

        // Evaluate the operation
        let result = if has_table {
            // Re-fetch the table inside the lock to avoid lifetime issues
            if let Some(table) = op_guard.get_table() {
                table.value_at(&args)?
            } else {
                op_guard.value(&args)?
            }
        } else {
            op_guard.value(&args)?
        };

        Ok(result)
    }

    /// Check if operation has a flat table available and cache the result
    fn check_operation_table(&mut self, operation: &dyn Operation, op_idx: usize) -> bool {
        // Check if we've already determined this operation has a flat table
        if !self.flat_table_ops.contains(&op_idx) {
            // Check if this operation has a flat table available
            if operation.get_table().is_some() {
                self.flat_table_ops.insert(op_idx);
                return true;
            }
            return false;
        }
        true
    }

    /// Clear the evaluation cache
    pub fn clear_cache(&mut self) {
        self.results.clear();
        self.flat_table_ops.clear();
        self.stack.clear();
    }

    /// Get the number of cached results
    pub fn cache_size(&self) -> usize {
        self.results.iter().filter(|r| r.is_some()).count()
    }

    /// Get memory usage statistics
    pub fn memory_stats(&self) -> EvaluationStats {
        EvaluationStats {
            stack_size: self.stack.len(),
            cache_size: self.cache_size(),
            cache_capacity: self.results.len(),
            flat_table_ops: self.flat_table_ops.len(),
            max_arity: self.max_arity,
        }
    }
}

/// Memory usage statistics for evaluation context
#[derive(Debug, Clone)]
pub struct EvaluationStats {
    pub stack_size: usize,
    pub cache_size: usize,
    pub cache_capacity: usize,
    pub flat_table_ops: usize,
    pub max_arity: usize,
}

/// Evaluate a term with given variable assignment
pub fn eval_term(
    term_id: TermId,
    arena: &TermArena,
    algebra: &dyn SmallAlgebra,
    variables: &VariableAssignment,
) -> UACalcResult<usize> {
    let mut context = EvaluationContext::new(algebra, variables);
    context.eval_term(term_id, arena)
}

/// Evaluate a term with integer variable values
pub fn eval_term_int(
    term_id: TermId,
    arena: &TermArena,
    algebra: &dyn SmallAlgebra,
    variable_values: &[usize],
) -> UACalcResult<usize> {
    let assignment = VariableAssignment::from_slice(variable_values);
    eval_term(term_id, arena, algebra, &assignment)
}

/// Evaluate multiple terms with the same variable assignment
pub fn eval_terms(
    term_ids: &[TermId],
    arena: &TermArena,
    algebra: &dyn SmallAlgebra,
    variables: &VariableAssignment,
) -> UACalcResult<Vec<usize>> {
    let mut context = EvaluationContext::new(algebra, variables);
    let mut results = Vec::with_capacity(term_ids.len());

    for &term_id in term_ids {
        let result = context.eval_term(term_id, arena)?;
        results.push(result);
    }

    Ok(results)
}

/// Evaluate a term and return the result as a term
pub fn eval_term_as_term(
    term_id: TermId,
    arena: &mut TermArena,
    algebra: &dyn SmallAlgebra,
    variables: &VariableAssignment,
) -> UACalcResult<TermId> {
    let value = eval_term(term_id, arena, algebra, variables)?;

    // Create a constant term representing the result in the provided arena
    let symbol = crate::operation::OperationSymbol::new(format!("const_{}", value), 0);
    let const_id = arena.make_term(&symbol, &[]);

    Ok(const_id)
}

/// Check if a term evaluates to a constant (no variables)
pub fn is_constant_term(term_id: TermId, arena: &TermArena) -> UACalcResult<bool> {
    let term = arena.get_term(term_id)?;
    match term {
        Term::Variable(_) => Ok(false),
        Term::Operation { children, .. } => {
            for &child_id in children {
                if !is_constant_term(child_id, arena)? {
                    return Ok(false);
                }
            }
            Ok(true)
        }
    }
}

/// Get the constant value of a term (if it's constant)
pub fn get_constant_value(
    term_id: TermId,
    arena: &TermArena,
    algebra: &dyn SmallAlgebra,
) -> UACalcResult<Option<usize>> {
    if is_constant_term(term_id, arena)? {
        let variables = VariableAssignment::new();
        let value = eval_term(term_id, arena, algebra, &variables)?;
        Ok(Some(value))
    } else {
        Ok(None)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::algebra::BasicAlgebra;
    use crate::operation::OperationSymbol;

    #[test]
    fn test_eval_variable() {
        let mut arena = TermArena::new();
        let var_id = arena.make_variable(0);

        let algebra = BasicAlgebra::with_cardinality("test".to_string(), 3).unwrap();
        let variables = VariableAssignment::from_values(vec![1, 2, 3]);

        let result = eval_term(var_id, &arena, &algebra, &variables);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 1);
    }

    #[test]
    fn test_eval_constant() {
        let mut arena = TermArena::new();
        let symbol = OperationSymbol::new("const".to_string(), 0);
        let const_id = arena.make_term(&symbol, &[]);

        let algebra = BasicAlgebra::with_cardinality("test".to_string(), 3).unwrap();
        let variables = VariableAssignment::new();

        let result = eval_term(const_id, &arena, &algebra, &variables);
        assert!(result.is_ok());
    }

    #[test]
    fn test_eval_operation() {
        let mut arena = TermArena::new();
        let x0 = arena.make_variable(0);
        let x1 = arena.make_variable(1);

        // Create a binary operation
        let symbol = OperationSymbol::new("f".to_string(), 2);
        let op_id = arena.make_term(&symbol, &[x0, x1]);

        let algebra = BasicAlgebra::with_cardinality("test".to_string(), 3).unwrap();
        let variables = VariableAssignment::from_values(vec![1, 2]);

        let result = eval_term(op_id, &arena, &algebra, &variables);
        assert!(result.is_ok());
    }

    #[test]
    fn test_eval_term_int() {
        let mut arena = TermArena::new();
        let var_id = arena.make_variable(0);

        let algebra = BasicAlgebra::with_cardinality("test".to_string(), 3).unwrap();
        let variable_values = vec![1, 2, 3];

        let result = eval_term_int(var_id, &arena, &algebra, &variable_values);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 1);
    }

    #[test]
    fn test_is_constant_term() {
        let mut arena = TermArena::new();
        let var_id = arena.make_variable(0);
        let symbol = OperationSymbol::new("const".to_string(), 0);
        let const_id = arena.make_term(&symbol, &[]);

        assert!(!is_constant_term(var_id, &arena).unwrap());
        assert!(is_constant_term(const_id, &arena).unwrap());
    }

    #[test]
    fn test_evaluation_context_memory_stats() {
        let mut arena = TermArena::new();
        let var_id = arena.make_variable(0);
        let symbol = OperationSymbol::new("f".to_string(), 1);
        let op_id = arena.make_term(&symbol, &[var_id]);

        let algebra = BasicAlgebra::with_cardinality("test".to_string(), 3).unwrap();
        let variables = VariableAssignment::from_values(vec![1]);

        let mut context = EvaluationContext::new(&algebra, &variables);
        let _result = context.eval_term(op_id, &arena).unwrap();

        let stats = context.memory_stats();
        assert!(stats.cache_size > 0);
        assert!(stats.max_arity > 0);
    }
}

/// Generate an operation table from a term
pub fn term_to_table(
    term_id: TermId,
    arena: &TermArena,
    algebra: &dyn SmallAlgebra,
) -> UACalcResult<crate::operation::FlatOperationTable> {
    let size = algebra.cardinality();
    let term = arena.get_term(term_id)?;
    
    // Determine arity from the term structure
    let arity = match term {
        Term::Variable(_) => 0, // Constants have arity 0
        Term::Operation { children, .. } => children.len(),
    };
    
    // For constants, create a 0-ary table
    if arity == 0 {
        let value = eval_term(term_id, arena, algebra, &VariableAssignment::new())?;
        let mut flat_table = crate::operation::FlatOperationTable::new(0, size)?;
        flat_table.set(0, value)?;
        return Ok(flat_table);
    }
    
    // For operations, evaluate all possible input tuples
    let total_tuples = size.pow(arity as u32);
    let mut table = vec![0; total_tuples];
    
    // Generate all possible input tuples using mixed-radix increment
    let mut args = vec![0; arity];
    
    for tuple_idx in 0..total_tuples {
        // Convert tuple index to argument values
        let mut temp_idx = tuple_idx;
        for i in 0..arity {
            args[i] = temp_idx % size;
            temp_idx /= size;
        }
        
        // Evaluate the term with these arguments
        let variables = VariableAssignment::from_values(args.clone());
        let result = eval_term(term_id, arena, algebra, &variables)?;
        table[tuple_idx] = result;
    }
    
    // Create the operation table
    let mut flat_table = crate::operation::FlatOperationTable::new(arity, size)?;
    
    // Copy the computed values into the table
    for (i, &value) in table.iter().enumerate() {
        flat_table.set(i, value)?;
    }
    
    Ok(flat_table)
}
