//! Combinatorial search algorithms for Taylor terms
//! 
//! This module provides efficient search algorithms for finding
//! term interpretations using array-based canonicalization.

use crate::{UACalcError, UACalcResult};
use crate::taylor::{Taylor, IntArray};
use crate::term::{Term, TermId, TermArena};

/// Search configuration
pub struct SearchConfig {
    /// Maximum search level
    pub max_level: usize,
    /// Maximum iterations
    pub max_iterations: usize,
    /// Progress callback
    pub progress_callback: Option<Box<dyn Fn(f64) + Send + Sync>>,
}

impl std::fmt::Debug for SearchConfig {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("SearchConfig")
            .field("max_level", &self.max_level)
            .field("max_iterations", &self.max_iterations)
            .field("progress_callback", &self.progress_callback.is_some())
            .finish()
    }
}

impl Default for SearchConfig {
    fn default() -> Self {
        Self {
            max_level: 10,
            max_iterations: 1000000,
            progress_callback: None,
        }
    }
}

/// Search result
#[derive(Debug, Clone)]
pub enum SearchResult {
    /// Interpretation found
    Found(TermId, TermArena),
    /// No interpretation found
    NotFound,
    /// Search timed out
    Timeout,
    /// Search error
    Error(String),
}

/// Array incrementor for systematic enumeration
pub struct ArrayIncrementor {
    /// Current array
    current: IntArray,
    /// Base for each position
    bases: Vec<usize>,
    /// Whether we've reached the end
    done: bool,
}

impl ArrayIncrementor {
    /// Create a new array incrementor
    pub fn new(length: usize, bases: Vec<usize>) -> UACalcResult<Self> {
        if bases.len() != length {
            return Err(UACalcError::InvalidOperation {
                message: "Bases length must match array length".to_string(),
            });
        }
        
        let current = IntArray::new(length);
        
        Ok(Self {
            current,
            bases,
            done: false,
        })
    }
    
    /// Get the current array
    pub fn current(&self) -> &IntArray {
        &self.current
    }
    
    /// Check if we're done
    pub fn is_done(&self) -> bool {
        self.done
    }
    
    /// Increment to the next array
    pub fn increment(&mut self) -> UACalcResult<()> {
        if self.done {
            return Ok(());
        }
        
        let mut i = 0;
        while i < self.current.len() {
            let current_value = self.current.get(i)?;
            let base = self.bases[i];
            
            if current_value + 1 < base {
                self.current.set(i, current_value + 1)?;
                return Ok(());
            } else {
                self.current.set(i, 0)?;
                i += 1;
            }
        }
        
        // If we get here, we've wrapped around
        self.done = true;
        Ok(())
    }
    
    /// Reset to the beginning
    pub fn reset(&mut self) -> UACalcResult<()> {
        for i in 0..self.current.len() {
            self.current.set(i, 0)?;
        }
        self.done = false;
        Ok(())
    }
}

/// Sequence incrementor with overflow detection
pub struct SequenceIncrementor {
    /// The underlying array incrementor
    incrementor: ArrayIncrementor,
    /// Variable count
    variable_count: usize,
}

impl SequenceIncrementor {
    /// Create a new sequence incrementor
    pub fn new(variable_count: usize, max_value: usize) -> UACalcResult<Self> {
        let bases = vec![max_value; variable_count];
        let incrementor = ArrayIncrementor::new(variable_count, bases)?;
        
        Ok(Self {
            incrementor,
            variable_count,
        })
    }
    
    /// Get the current sequence
    pub fn current(&self) -> &IntArray {
        self.incrementor.current()
    }
    
    /// Check if we're done
    pub fn is_done(&self) -> bool {
        self.incrementor.is_done()
    }
    
    /// Increment to the next sequence
    pub fn increment(&mut self) -> UACalcResult<()> {
        self.incrementor.increment()
    }
    
    /// Reset to the beginning
    pub fn reset(&mut self) -> UACalcResult<()> {
        self.incrementor.reset()
    }
}

/// Search for Markovic-McKenzie interpretations
pub fn find_markovic_mckenzie(config: SearchConfig) -> SearchResult {
    let taylor = crate::taylor::taylor::markovic_mckenzie_term();
    find_interpretation(&taylor, config)
}

/// Search for Siggers interpretations
pub fn find_siggers(config: SearchConfig) -> SearchResult {
    let taylor = crate::taylor::taylor::siggers_term();
    find_interpretation(&taylor, config)
}

/// Generic interpretation search
pub fn find_interpretation(taylor: &Taylor, config: SearchConfig) -> SearchResult {
    let mut iterations = 0;
    
    for level in 1..=config.max_level {
        // Report progress
        if let Some(ref callback) = config.progress_callback {
            let progress = level as f64 / config.max_level as f64;
            callback(progress);
        }
        
        // Create sequence incrementor for this level
        let mut incrementor = match SequenceIncrementor::new(taylor.arity(), 2) {
            Ok(inc) => inc,
            Err(_) => return SearchResult::Error("Failed to create incrementor".to_string()),
        };
        
        // Search at this level
        while !incrementor.is_done() && iterations < config.max_iterations {
            iterations += 1;
            
            let assignment = incrementor.current();
            
            // Check if this assignment satisfies the equations
            if taylor.satisfies_equations_with_assignment(assignment) {
                // Convert to term
                let mut arena = TermArena::new();
                let term_id = crate::taylor::taylor::term_from_array(assignment, &mut arena, &taylor.spec().symbol);
                
                return SearchResult::Found(term_id, arena);
            }
            
            // Increment to next assignment
            if let Err(_) = incrementor.increment() {
                break;
            }
        }
        
        if iterations >= config.max_iterations {
            return SearchResult::Timeout;
        }
    }
    
    SearchResult::NotFound
}

/// Search for interpretations with early termination
pub fn find_interpretation_early_termination(
    taylor: &Taylor,
    config: SearchConfig,
    early_termination: impl Fn(&IntArray) -> bool,
) -> SearchResult {
    let mut iterations = 0;
    
    for level in 1..=config.max_level {
        // Report progress
        if let Some(ref callback) = config.progress_callback {
            let progress = level as f64 / config.max_level as f64;
            callback(progress);
        }
        
        // Create sequence incrementor for this level
        let mut incrementor = match SequenceIncrementor::new(taylor.arity(), 2) {
            Ok(inc) => inc,
            Err(_) => return SearchResult::Error("Failed to create incrementor".to_string()),
        };
        
        // Search at this level
        while !incrementor.is_done() && iterations < config.max_iterations {
            iterations += 1;
            
            let assignment = incrementor.current();
            
            // Check early termination condition
            if early_termination(assignment) {
                return SearchResult::NotFound;
            }
            
            // Check if this assignment satisfies the equations
            if taylor.satisfies_equations_with_assignment(assignment) {
                // Convert to term
                let mut arena = TermArena::new();
                let term_id = crate::taylor::taylor::term_from_array(assignment, &mut arena, &taylor.spec().symbol);
                
                return SearchResult::Found(term_id, arena);
            }
            
            // Increment to next assignment
            if let Err(_) = incrementor.increment() {
                break;
            }
        }
        
        if iterations >= config.max_iterations {
            return SearchResult::Timeout;
        }
    }
    
    SearchResult::NotFound
}

/// Batch search for multiple interpretations
pub fn find_multiple_interpretations(
    taylor: &Taylor,
    config: SearchConfig,
    max_interpretations: usize,
) -> Vec<Term> {
    let mut interpretations = Vec::new();
    let mut iterations = 0;
    
    for level in 1..=config.max_level {
        // Report progress
        if let Some(ref callback) = config.progress_callback {
            let progress = level as f64 / config.max_level as f64;
            callback(progress);
        }
        
        // Create sequence incrementor for this level
        let mut incrementor = match SequenceIncrementor::new(taylor.arity(), 2) {
            Ok(inc) => inc,
            Err(_) => break,
        };
        
        // Search at this level
        while !incrementor.is_done() && iterations < config.max_iterations {
            iterations += 1;
            
            let assignment = incrementor.current();
            
            // Check if this assignment satisfies the equations
            if taylor.satisfies_equations_with_assignment(assignment) {
                // Convert to term
                let mut arena = TermArena::new();
                let term_id = crate::taylor::taylor::term_from_array(assignment, &mut arena, &taylor.spec().symbol);
                let term = arena.get_term(term_id).unwrap().clone();
                
                interpretations.push(term);
                
                if interpretations.len() >= max_interpretations {
                    return interpretations;
                }
            }
            
            // Increment to next assignment
            if let Err(_) = incrementor.increment() {
                break;
            }
        }
        
        if iterations >= config.max_iterations {
            break;
        }
    }
    
    interpretations
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_array_incrementor() {
        let mut incrementor = ArrayIncrementor::new(3, vec![2, 2, 2]).unwrap();
        
        // First array should be [0, 0, 0]
        assert_eq!(incrementor.current().to_vec(), vec![0, 0, 0]);
        assert!(!incrementor.is_done());
        
        // Increment
        incrementor.increment().unwrap();
        assert_eq!(incrementor.current().to_vec(), vec![1, 0, 0]);
        
        // Reset
        incrementor.reset().unwrap();
        assert_eq!(incrementor.current().to_vec(), vec![0, 0, 0]);
    }
    
    #[test]
    fn test_sequence_incrementor() {
        let mut incrementor = SequenceIncrementor::new(2, 2).unwrap();
        
        // First sequence should be [0, 0]
        assert_eq!(incrementor.current().to_vec(), vec![0, 0]);
        assert!(!incrementor.is_done());
        
        // Increment
        incrementor.increment().unwrap();
        assert_eq!(incrementor.current().to_vec(), vec![1, 0]);
    }
    
    #[test]
    fn test_search_config_default() {
        let config = SearchConfig::default();
        assert_eq!(config.max_level, 10);
        assert_eq!(config.max_iterations, 1000000);
    }
    
    #[test]
    fn test_find_markovic_mckenzie() {
        let config = SearchConfig {
            max_level: 2,
            max_iterations: 1000,
            progress_callback: None,
        };
        
        let result = find_markovic_mckenzie(config);
        match result {
            SearchResult::NotFound | SearchResult::Timeout => {
                // Expected for small search space
            }
            SearchResult::Found(_, _) => {
                // Also acceptable - a valid interpretation was found
            }
            SearchResult::Error(msg) => {
                panic!("Search error: {}", msg);
            }
        }
    }
}
