//! Taylor term representation and search algorithms
//!
//! This module provides efficient Taylor term representation and
//! search algorithms for finding term interpretations.

use crate::operation::OperationSymbol;
use crate::taylor::canonical::{canonical_form, make_union_find, UnionFind};
use crate::taylor::int_array::IntArray;
use crate::term::{TermArena, TermId};
use std::collections::HashMap;

/// Taylor term specification
#[derive(Debug, Clone)]
pub struct TaylorSpec {
    /// Operation arity
    pub arity: usize,
    /// Defining equations
    pub equations: Vec<(IntArray, IntArray)>,
    /// Union-find structure for canonical form computation
    pub union_find: UnionFind,
    /// Operation symbol
    pub symbol: OperationSymbol,
}

impl TaylorSpec {
    /// Create a new Taylor specification
    pub fn new(
        arity: usize,
        equations: Vec<(IntArray, IntArray)>,
        symbol: OperationSymbol,
    ) -> Self {
        let union_find = make_union_find(&equations);
        Self {
            arity,
            equations,
            union_find,
            symbol,
        }
    }

    /// Check if the equations are satisfied (no assignment parameter needed)
    pub fn satisfies_equations(&self) -> bool {
        // Create a local mutable clone of union_find for canonical form computation
        let mut uf = self.union_find.clone();

        for (left, right) in &self.equations {
            // Compute canonical forms for both sides
            let left_canonical = canonical_form(left, &mut uf);
            let right_canonical = canonical_form(right, &mut uf);

            // Check if canonical forms are equal
            if left_canonical != right_canonical {
                return false;
            }
        }
        true
    }
}

/// Taylor term representation
#[derive(Debug, Clone)]
pub struct Taylor {
    /// The Taylor specification
    spec: TaylorSpec,
    /// Cached canonical forms
    canonical_cache: HashMap<IntArray, IntArray>,
}

impl Taylor {
    /// Create a new Taylor term
    pub fn new(spec: TaylorSpec) -> Self {
        Self {
            spec,
            canonical_cache: HashMap::new(),
        }
    }

    /// Get the specification
    pub fn spec(&self) -> &TaylorSpec {
        &self.spec
    }

    /// Get the arity
    pub fn arity(&self) -> usize {
        self.spec.arity
    }

    /// Get the equations
    pub fn equations(&self) -> &[(IntArray, IntArray)] {
        &self.spec.equations
    }

    /// Get the union-find structure
    pub fn union_find(&self) -> &UnionFind {
        &self.spec.union_find
    }

    /// Check if the equations are satisfied (no assignment parameter needed)
    pub fn satisfies_equations(&self) -> bool {
        // Create a local mutable clone of union_find for canonical form computation
        let mut uf = self.spec.union_find.clone();

        for (left, right) in &self.spec.equations {
            // Compute canonical forms for both sides
            let left_canonical = canonical_form(left, &mut uf);
            let right_canonical = canonical_form(right, &mut uf);

            // Check if canonical forms are equal
            if left_canonical != right_canonical {
                return false;
            }
        }
        true
    }

    /// Check if the equations are satisfied with a specific assignment
    pub fn satisfies_equations_with_assignment(&self, assignment: &IntArray) -> bool {
        // Create a fresh UnionFind seeded from self.spec.equations
        let mut uf = make_union_find(&self.spec.equations);

        // Additionally union entries implied by the assignment
        for i in 0..assignment.len() {
            let value = assignment.get(i).unwrap();
            // Create IntArray representations for union
            let pos_array = IntArray::from_vec(vec![i]);
            let val_array = IntArray::from_vec(vec![value]);
            uf.union(&pos_array, &val_array);
        }

        for (left, right) in &self.spec.equations {
            // Compute canonical forms for both sides
            let left_canonical = canonical_form(left, &mut uf);
            let right_canonical = canonical_form(right, &mut uf);

            // Check if canonical forms are equal
            if left_canonical != right_canonical {
                return false;
            }
        }
        true
    }

    /// Get mutable access to the union-find structure
    pub fn union_find_mut(&mut self) -> &mut UnionFind {
        &mut self.spec.union_find
    }

    /// Find an interpretation at the given level
    pub fn interprets(&self, level: usize, arena: &mut TermArena) -> Option<TermId> {
        // Generate all possible assignments at the given level
        let assignments = self.generate_assignments(level);

        for assignment in assignments {
            if self.satisfies_equations_with_assignment(&assignment) {
                // Convert the assignment to a term
                return Some(self.assignment_to_term(&assignment, arena));
            }
        }

        None
    }

    /// Generate all possible assignments at the given level
    fn generate_assignments(&self, level: usize) -> Vec<IntArray> {
        let mut assignments = Vec::new();
        let size = 2usize.pow(level as u32); // Binary assignments

        for i in 0..size {
            let mut assignment = IntArray::new(self.arity());
            for j in 0..self.arity() {
                let bit = (i >> j) & 1;
                assignment.set(j, bit).unwrap();
            }
            assignments.push(assignment);
        }

        assignments
    }

    /// Convert an array assignment to a term in the given arena
    fn assignment_to_term(&self, assignment: &IntArray, arena: &mut TermArena) -> TermId {
        // Create a balanced term tree from the assignment
        self.create_balanced_term(assignment, 0, assignment.len(), arena)
    }

    /// Create a balanced term tree recursively
    fn create_balanced_term(
        &self,
        assignment: &IntArray,
        start: usize,
        end: usize,
        arena: &mut TermArena,
    ) -> TermId {
        if end - start == 1 {
            // Leaf node
            let value = assignment.get(start).unwrap();
            arena.make_variable(value as u8)
        } else {
            // Internal node
            let mid = (start + end) / 2;
            let left = self.create_balanced_term(assignment, start, mid, arena);
            let right = self.create_balanced_term(assignment, mid, end, arena);

            // Create operation term using the spec's symbol
            arena.make_term(&self.spec.symbol, &[left, right])
        }
    }

    /// Convert to a term in the given arena
    pub fn to_term(&self, arena: &mut TermArena) -> TermId {
        // Create a simple term representation
        let symbol = self.spec.symbol.clone();
        let children = Vec::new(); // Will be populated based on arity

        arena.make_term(&symbol, &children)
    }
}

/// Create the Markovic-McKenzie term
pub fn markovic_mckenzie_term() -> Taylor {
    let arity = 4;
    let symbol = OperationSymbol::new("MM".to_string(), arity);

    // Define the canonical MM equations from Java Taylor.java
    let equations = vec![
        (
            IntArray::from_vec(vec![1, 0, 0, 0]),
            IntArray::from_vec(vec![0, 0, 1, 1]),
        ),
        (
            IntArray::from_vec(vec![0, 0, 1, 0]),
            IntArray::from_vec(vec![0, 1, 0, 0]),
        ),
    ];

    let spec = TaylorSpec::new(arity, equations, symbol);
    Taylor::new(spec)
}

/// Create the Siggers term
pub fn siggers_term() -> Taylor {
    let arity = 6;
    let symbol = OperationSymbol::new("Siggers".to_string(), arity);

    // Define the canonical Siggers equations from Java Taylor.java
    let equations = vec![
        (
            IntArray::from_vec(vec![1, 1, 0, 0, 0, 0]),
            IntArray::from_vec(vec![0, 0, 1, 0, 1, 0]),
        ),
        (
            IntArray::from_vec(vec![0, 0, 0, 0, 1, 1]),
            IntArray::from_vec(vec![0, 1, 0, 1, 0, 0]),
        ),
    ];

    let spec = TaylorSpec::new(arity, equations, symbol);
    Taylor::new(spec)
}

/// Convert an integer array to a balanced term tree
pub fn term_from_array(
    assignment: &IntArray,
    arena: &mut TermArena,
    symbol: &OperationSymbol,
) -> TermId {
    if assignment.len() == 1 {
        let value = assignment.get(0).unwrap();
        arena.make_variable(value as u8)
    } else {
        // Split the array and create a balanced tree
        let mid = assignment.len() / 2;
        let left_slice: Vec<usize> = assignment.as_slice().iter().map(|&x| x as usize).collect();
        let right_slice: Vec<usize> = assignment.as_slice()[mid..]
            .iter()
            .map(|&x| x as usize)
            .collect();
        let left_array = IntArray::from_slice(&left_slice[..mid]);
        let right_array = IntArray::from_slice(&right_slice);

        let left_id = term_from_array(&left_array, arena, symbol);
        let right_id = term_from_array(&right_array, arena, symbol);

        arena.make_term(symbol, &[left_id, right_id])
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_taylor_spec_creation() {
        let arity = 2;
        let equations = vec![
            (
                IntArray::from_vec(vec![0, 0]),
                IntArray::from_vec(vec![0, 0]),
            ),
            (
                IntArray::from_vec(vec![1, 1]),
                IntArray::from_vec(vec![1, 1]),
            ),
        ];
        let symbol = OperationSymbol::new("test".to_string(), arity);

        let spec = TaylorSpec::new(arity, equations, symbol);
        assert_eq!(spec.arity, 2);
        assert_eq!(spec.equations.len(), 2);
    }

    #[test]
    fn test_taylor_creation() {
        let arity = 2;
        let equations = vec![(
            IntArray::from_vec(vec![0, 0]),
            IntArray::from_vec(vec![0, 0]),
        )];
        let symbol = OperationSymbol::new("test".to_string(), arity);
        let spec = TaylorSpec::new(arity, equations, symbol);

        let taylor = Taylor::new(spec);
        assert_eq!(taylor.arity(), 2);
    }

    #[test]
    fn test_markovic_mckenzie_term() {
        let mm = markovic_mckenzie_term();
        assert_eq!(mm.arity(), 4);
    }

    #[test]
    fn test_siggers_term() {
        let siggers = siggers_term();
        assert_eq!(siggers.arity(), 4);
    }

    #[test]
    fn test_term_from_array() {
        let mut arena = TermArena::new();
        let array = IntArray::from_vec(vec![1, 0, 1, 0]);

        let term_id = term_from_array(
            &array,
            &mut arena,
            &OperationSymbol::new("f".to_string(), 2),
        );
        assert!(arena.is_valid_term(term_id));
    }
}
