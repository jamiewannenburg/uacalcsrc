//! Term arena for memory-efficient term storage
//!
//! This module provides arena-based memory management for terms,
//! enabling efficient allocation and deallocation.

use crate::operation::OperationSymbol;
use crate::term::{Term, TermId};
use crate::{UACalcError, UACalcResult};
use std::collections::HashMap;

/// Arena for efficient term allocation and management
#[derive(Debug, Clone)]
pub struct TermArena {
    /// All terms in the arena
    terms: Vec<Term>,
    /// Symbol table mapping symbols to indices
    symbols: Vec<OperationSymbol>,
    /// Symbol name to index mapping for fast lookup
    symbol_map: HashMap<String, u16>,
    /// Free list for reuse of deallocated terms
    free_list: Vec<TermId>,
}

impl TermArena {
    /// Create a new term arena
    pub fn new() -> Self {
        Self {
            terms: Vec::new(),
            symbols: Vec::new(),
            symbol_map: HashMap::new(),
            free_list: Vec::new(),
        }
    }

    /// Create a term arena with initial capacity
    pub fn with_capacity(term_capacity: usize, symbol_capacity: usize) -> Self {
        Self {
            terms: Vec::with_capacity(term_capacity),
            symbols: Vec::with_capacity(symbol_capacity),
            symbol_map: HashMap::with_capacity(symbol_capacity),
            free_list: Vec::new(),
        }
    }

    /// Allocate a new term in the arena
    pub fn alloc_term(&mut self, term: Term) -> TermId {
        // Check if we can reuse a free slot
        if let Some(id) = self.free_list.pop() {
            self.terms[id] = term;
            id
        } else {
            // Allocate new slot
            let id = self.terms.len();
            self.terms.push(term);
            id
        }
    }

    /// Deallocate a term (add to free list for reuse)
    pub fn dealloc_term(&mut self, id: TermId) -> UACalcResult<()> {
        if id >= self.terms.len() {
            return Err(UACalcError::InvalidOperation {
                message: format!("Invalid term ID: {}", id),
            });
        }

        // Clear the term and add to free list
        self.terms[id] = Term::Variable(0); // Placeholder
        self.free_list.push(id);

        Ok(())
    }

    /// Get a term by ID
    pub fn get_term(&self, id: TermId) -> UACalcResult<&Term> {
        self.terms
            .get(id)
            .ok_or_else(|| UACalcError::InvalidOperation {
                message: format!("Invalid term ID: {}", id),
            })
    }

    /// Get a mutable reference to a term by ID
    pub fn get_term_mut(&mut self, id: TermId) -> UACalcResult<&mut Term> {
        self.terms
            .get_mut(id)
            .ok_or_else(|| UACalcError::InvalidOperation {
                message: format!("Invalid term ID: {}", id),
            })
    }

    /// Add a symbol to the symbol table
    pub fn add_symbol(&mut self, symbol: OperationSymbol) -> u16 {
        let name = symbol.name().to_string();
        if let Some(&id) = self.symbol_map.get(&name) {
            id
        } else {
            let id = self.symbols.len() as u16;
            self.symbols.push(symbol);
            self.symbol_map.insert(name, id);
            id
        }
    }

    /// Get a symbol by ID
    pub fn get_symbol(&self, id: u16) -> UACalcResult<&OperationSymbol> {
        self.symbols
            .get(id as usize)
            .ok_or_else(|| UACalcError::InvalidOperation {
                message: format!("Invalid symbol ID: {}", id),
            })
    }

    /// Find a symbol by name
    pub fn find_symbol(&self, name: &str) -> Option<u16> {
        self.symbol_map.get(name).cloned()
    }

    /// Get the number of terms in the arena
    pub fn num_terms(&self) -> usize {
        self.terms.len()
    }

    /// Get the number of active terms (excluding free slots)
    pub fn num_active_terms(&self) -> usize {
        self.terms.len() - self.free_list.len()
    }

    /// Get the number of symbols in the arena
    pub fn num_symbols(&self) -> usize {
        self.symbols.len()
    }

    /// Get the number of free slots
    pub fn num_free_slots(&self) -> usize {
        self.free_list.len()
    }

    /// Clear all terms (keep symbols)
    pub fn clear_terms(&mut self) {
        self.terms.clear();
        self.free_list.clear();
    }

    /// Clear everything
    pub fn clear(&mut self) {
        self.terms.clear();
        self.symbols.clear();
        self.symbol_map.clear();
        self.free_list.clear();
    }

    /// Compact the arena by removing free slots
    pub fn compact(&mut self) {
        if self.free_list.is_empty() {
            return;
        }

        // Create a new terms vector with only active terms
        let mut new_terms = Vec::new();
        let mut old_to_new = Vec::new();

        for (old_id, term) in self.terms.iter().enumerate() {
            if !self.free_list.contains(&old_id) {
                old_to_new.push(Some(new_terms.len()));
                new_terms.push(term.clone());
            } else {
                old_to_new.push(None);
            }
        }

        // Update child references in operation terms
        for term in &mut new_terms {
            if let Term::Operation { children, .. } = term {
                for child in children {
                    if let Some(new_id) = old_to_new[*child] {
                        *child = new_id;
                    }
                }
            }
        }

        // Replace terms and clear free list
        self.terms = new_terms;
        self.free_list.clear();
    }

    /// Get memory usage statistics
    pub fn memory_stats(&self) -> ArenaStats {
        let term_size = std::mem::size_of::<Term>();
        let symbol_size = std::mem::size_of::<OperationSymbol>();

        ArenaStats {
            total_terms: self.terms.len(),
            active_terms: self.num_active_terms(),
            free_slots: self.free_list.len(),
            total_symbols: self.symbols.len(),
            term_memory: self.terms.len() * term_size,
            symbol_memory: self.symbols.len() * symbol_size,
            map_memory: self.symbol_map.len()
                * (std::mem::size_of::<String>() + std::mem::size_of::<u16>()),
            free_list_memory: self.free_list.len() * std::mem::size_of::<TermId>(),
        }
    }

    /// Get all active terms
    pub fn active_terms(&self) -> Vec<(TermId, &Term)> {
        let mut active = Vec::new();
        for (id, term) in self.terms.iter().enumerate() {
            if !self.free_list.contains(&id) {
                active.push((id, term));
            }
        }
        active
    }

    /// Get free slots
    pub fn free_slots(&self) -> Vec<TermId> {
        self.free_list.clone()
    }

    /// Check if a term ID is valid and active
    pub fn is_valid_term(&self, id: TermId) -> bool {
        id < self.terms.len() && !self.free_list.contains(&id)
    }

    /// Create a variable term
    pub fn make_variable(&mut self, index: u8) -> TermId {
        self.alloc_term(Term::Variable(index))
    }

    /// Create an operation term
    pub fn make_operation(&mut self, symbol_id: u16, children: &[TermId]) -> TermId {
        self.alloc_term(Term::Operation {
            symbol_id,
            children: children.iter().cloned().collect(),
        })
    }

    /// Create a term from a symbol and child terms
    pub fn make_term(&mut self, symbol: &OperationSymbol, children: &[TermId]) -> TermId {
        let symbol_id = self.add_symbol(symbol.clone());
        self.make_operation(symbol_id, children)
    }
}

impl Default for TermArena {
    fn default() -> Self {
        Self::new()
    }
}

/// Memory usage statistics for the arena
#[derive(Debug, Clone)]
pub struct ArenaStats {
    /// Total number of term slots (including free)
    pub total_terms: usize,
    /// Number of active terms
    pub active_terms: usize,
    /// Number of free slots
    pub free_slots: usize,
    /// Number of symbols
    pub total_symbols: usize,
    /// Memory used by terms (bytes)
    pub term_memory: usize,
    /// Memory used by symbols (bytes)
    pub symbol_memory: usize,
    /// Memory used by symbol map (bytes)
    pub map_memory: usize,
    /// Memory used by free list (bytes)
    pub free_list_memory: usize,
}

impl ArenaStats {
    /// Get total memory usage
    pub fn total_memory(&self) -> usize {
        self.term_memory + self.symbol_memory + self.map_memory + self.free_list_memory
    }

    /// Get memory efficiency (active terms / total terms)
    pub fn efficiency(&self) -> f64 {
        if self.total_terms == 0 {
            1.0
        } else {
            self.active_terms as f64 / self.total_terms as f64
        }
    }
}

/// Iterator over active terms in the arena
pub struct ActiveTermsIter<'a> {
    arena: &'a TermArena,
    current: usize,
}

impl<'a> ActiveTermsIter<'a> {
    fn new(arena: &'a TermArena) -> Self {
        Self { arena, current: 0 }
    }
}

impl<'a> Iterator for ActiveTermsIter<'a> {
    type Item = (TermId, &'a Term);

    fn next(&mut self) -> Option<Self::Item> {
        while self.current < self.arena.terms.len() {
            let id = self.current;
            self.current += 1;

            if !self.arena.free_list.contains(&id) {
                return Some((id, &self.arena.terms[id]));
            }
        }
        None
    }
}

impl<'a> TermArena {
    /// Get an iterator over active terms
    pub fn iter_active(&'a self) -> ActiveTermsIter<'a> {
        ActiveTermsIter::new(self)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::operation::OperationSymbol;

    #[test]
    fn test_arena_creation() {
        let arena = TermArena::new();
        assert_eq!(arena.num_terms(), 0);
        assert_eq!(arena.num_symbols(), 0);
        assert_eq!(arena.num_free_slots(), 0);
    }

    #[test]
    fn test_arena_with_capacity() {
        let arena = TermArena::with_capacity(100, 10);
        assert_eq!(arena.num_terms(), 0);
        assert_eq!(arena.num_symbols(), 0);
    }

    #[test]
    fn test_term_allocation() {
        let mut arena = TermArena::new();
        let var_id = arena.make_variable(5);
        let op_id = arena.make_operation(1, &[var_id]);

        assert_eq!(arena.num_terms(), 2);
        assert_eq!(arena.num_active_terms(), 2);

        let var = arena.get_term(var_id).unwrap();
        assert!(var.is_variable());

        let op = arena.get_term(op_id).unwrap();
        assert!(op.is_operation());
    }

    #[test]
    fn test_term_deallocation() {
        let mut arena = TermArena::new();
        let var_id = arena.make_variable(5);

        assert_eq!(arena.num_active_terms(), 1);

        arena.dealloc_term(var_id).unwrap();

        assert_eq!(arena.num_active_terms(), 0);
        assert_eq!(arena.num_free_slots(), 1);
    }

    #[test]
    fn test_symbol_management() {
        let mut arena = TermArena::new();
        let symbol = OperationSymbol::new("f".to_string(), 2);
        let symbol_id = arena.add_symbol(symbol);

        assert_eq!(arena.num_symbols(), 1);

        let retrieved = arena.get_symbol(symbol_id).unwrap();
        assert_eq!(retrieved.name(), "f");
        assert_eq!(retrieved.arity(), 2);
    }

    #[test]
    fn test_arena_compaction() {
        let mut arena = TermArena::new();
        let var1 = arena.make_variable(1);
        let var2 = arena.make_variable(2);
        let var3 = arena.make_variable(3);

        arena.dealloc_term(var2).unwrap();

        assert_eq!(arena.num_terms(), 3);
        assert_eq!(arena.num_active_terms(), 2);
        assert_eq!(arena.num_free_slots(), 1);

        arena.compact();

        assert_eq!(arena.num_terms(), 2);
        assert_eq!(arena.num_active_terms(), 2);
        assert_eq!(arena.num_free_slots(), 0);
    }

    #[test]
    fn test_memory_stats() {
        let mut arena = TermArena::new();
        arena.make_variable(1);
        arena.make_variable(2);

        let stats = arena.memory_stats();
        assert_eq!(stats.total_terms, 2);
        assert_eq!(stats.active_terms, 2);
        assert_eq!(stats.free_slots, 0);
        assert!(stats.efficiency() > 0.0);
    }

    #[test]
    fn test_active_terms_iter() {
        let mut arena = TermArena::new();
        let var1 = arena.make_variable(1);
        let var2 = arena.make_variable(2);
        arena.dealloc_term(var1).unwrap();

        let active: Vec<_> = arena.iter_active().collect();
        assert_eq!(active.len(), 1);
        assert_eq!(active[0].0, var2);
    }
}
