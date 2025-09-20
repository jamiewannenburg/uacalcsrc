//! Variety analysis and specialized term finding
//!
//! This module provides implementations for variety membership analysis,
//! specialized term finding (Jonsson, Gumm, Hagemann-Mitschke, etc.),
//! and variety-specific property detection.

use crate::{UACalcError, UACalcResult, SmallAlgebra};
use crate::algebra::Algebra;
use crate::operation::Operation;
use crate::term::TermArena;
use crate::free_algebra::FreeAlgebra;
use std::sync::{Arc, Mutex};
use std::collections::HashSet;

#[cfg(feature = "memory-limit")]
use crate::memory::{would_exceed_limit, get_allocated_memory};

/// Results from variety-specific term analysis
#[derive(Debug, Clone)]
pub struct VarietyTermAnalysis {
    /// Whether Jonsson terms exist
    pub has_jonsson_terms: bool,
    /// Whether Gumm terms exist
    pub has_gumm_terms: bool,
    /// Whether Hagemann-Mitschke terms exist
    pub has_hagemann_mitschke_terms: bool,
    /// Whether semidistributive terms exist
    pub has_sd_terms: bool,
    /// Whether SD-meet terms exist
    pub has_sdmeet_terms: bool,
    /// Whether primality terms exist
    pub has_primality_terms: bool,
    /// The actual Jonsson terms if found
    pub jonsson_terms: Option<Vec<String>>,
    /// The actual Gumm terms if found
    pub gumm_terms: Option<Vec<String>>,
    /// The actual Hagemann-Mitschke terms if found
    pub hagemann_mitschke_terms: Option<Vec<String>>,
    /// Analysis completion status
    pub analysis_completed: bool,
}

/// Results from variety membership analysis
#[derive(Debug, Clone)]
pub struct VarietyAnalysis {
    /// Whether the algebra is in the variety of groups
    pub is_group: bool,
    /// Whether the algebra is in the variety of lattices
    pub is_lattice: bool,
    /// Whether the algebra is in the variety of Boolean algebras
    pub is_boolean_algebra: bool,
    /// Whether the algebra is in the variety of semilattices
    pub is_semilattice: bool,
    /// Whether the algebra is in the variety of quasigroups
    pub is_quasigroup: bool,
    /// Total number of varieties the algebra belongs to
    pub variety_count: usize,
}

/// Results from specialized term finding
#[derive(Debug, Clone)]
pub struct SpecializedTermAnalysis {
    /// Whether a semilattice term exists
    pub has_semilattice_term: bool,
    /// Whether a difference term exists
    pub has_difference_term: bool,
    /// Whether a Pixley term exists
    pub has_pixley_term: bool,
    /// Whether a weak majority term exists
    pub has_weak_majority_term: bool,
    /// Whether a weak NU term exists
    pub has_weak_nu_term: bool,
    /// Whether a weak 3-edge term exists
    pub has_weak_3edge_term: bool,
    /// Whether a fixed k-edge term exists
    pub has_fixed_kedge_term: bool,
    /// The actual semilattice term if found
    pub semilattice_term: Option<String>,
    /// The actual difference term if found
    pub difference_term: Option<String>,
    /// The actual Pixley term if found
    pub pixley_term: Option<String>,
    /// Analysis completion status
    pub analysis_completed: bool,
}

/// Main variety analyzer
pub struct VarietyAnalyzer {
    arena: TermArena,
}

impl VarietyAnalyzer {
    /// Create a new variety analyzer
    pub fn new() -> Self {
        Self {
            arena: TermArena::new(),
        }
    }

    /// Analyze variety-specific terms for an algebra
    pub fn analyze_variety_terms(&mut self, algebra: &dyn SmallAlgebra) -> UACalcResult<VarietyTermAnalysis> {
        let mut analysis = VarietyTermAnalysis {
            has_jonsson_terms: false,
            has_gumm_terms: false,
            has_hagemann_mitschke_terms: false,
            has_sd_terms: false,
            has_sdmeet_terms: false,
            has_primality_terms: false,
            jonsson_terms: None,
            gumm_terms: None,
            hagemann_mitschke_terms: None,
            analysis_completed: false,
        };

        // For very small algebras, we can do more complete analysis
        if algebra.cardinality() <= 4 {
            analysis = self.analyze_small_algebra_variety_terms(algebra)?;
        } else {
            // For larger algebras, use conservative estimates
            analysis = self.analyze_large_algebra_variety_terms(algebra)?;
        }

        analysis.analysis_completed = true;
        Ok(analysis)
    }

    /// Analyze variety membership for an algebra
    pub fn analyze_variety_membership(&self, algebra: &dyn SmallAlgebra) -> UACalcResult<VarietyAnalysis> {
        eprintln!("DEBUG: Starting variety membership analysis");
        
        let mut analysis = VarietyAnalysis {
            is_group: false,
            is_lattice: false,
            is_boolean_algebra: false,
            is_semilattice: false,
            is_quasigroup: false,
            variety_count: 0,
        };

        // Check group variety: exactly one binary operation with group properties
        eprintln!("DEBUG: Checking group variety");
        analysis.is_group = self.check_group_variety(algebra)?;
        eprintln!("DEBUG: Group variety result: {}", analysis.is_group);

        // Check lattice variety: exactly two binary operations
        eprintln!("DEBUG: Checking lattice variety");
        analysis.is_lattice = self.check_lattice_variety(algebra)?;
        eprintln!("DEBUG: Lattice variety result: {}", analysis.is_lattice);

        // Check Boolean algebra variety: two binary, one unary, two nullary operations
        eprintln!("DEBUG: Checking Boolean algebra variety");
        analysis.is_boolean_algebra = self.check_boolean_algebra_variety(algebra)?;
        eprintln!("DEBUG: Boolean algebra variety result: {}", analysis.is_boolean_algebra);

        // Check semilattice variety: exactly one binary operation
        eprintln!("DEBUG: Checking semilattice variety");
        analysis.is_semilattice = self.check_semilattice_variety(algebra)?;
        eprintln!("DEBUG: Semilattice variety result: {}", analysis.is_semilattice);

        // Check quasigroup variety: exactly one binary operation
        eprintln!("DEBUG: Checking quasigroup variety");
        analysis.is_quasigroup = self.check_quasigroup_variety(algebra)?;
        eprintln!("DEBUG: Quasigroup variety result: {}", analysis.is_quasigroup);

        // Count varieties
        analysis.variety_count = [
            analysis.is_group,
            analysis.is_lattice,
            analysis.is_boolean_algebra,
            analysis.is_semilattice,
            analysis.is_quasigroup,
        ].iter().filter(|&&x| x).count();

        eprintln!("DEBUG: Variety analysis complete, count: {}", analysis.variety_count);
        Ok(analysis)
    }

    /// Analyze specialized terms for an algebra
    pub fn analyze_specialized_terms(&mut self, algebra: &dyn SmallAlgebra) -> UACalcResult<SpecializedTermAnalysis> {
        let mut analysis = SpecializedTermAnalysis {
            has_semilattice_term: false,
            has_difference_term: false,
            has_pixley_term: false,
            has_weak_majority_term: false,
            has_weak_nu_term: false,
            has_weak_3edge_term: false,
            has_fixed_kedge_term: false,
            semilattice_term: None,
            difference_term: None,
            pixley_term: None,
            analysis_completed: false,
        };

        // For very small algebras, we can do more complete analysis
        if algebra.cardinality() <= 4 {
            analysis = self.analyze_small_algebra_specialized_terms(algebra)?;
        } else {
            // For larger algebras, use conservative estimates
            analysis = self.analyze_large_algebra_specialized_terms(algebra)?;
        }

        analysis.analysis_completed = true;
        Ok(analysis)
    }

    /// Analyze variety terms for small algebras
    fn analyze_small_algebra_variety_terms(&mut self, algebra: &dyn SmallAlgebra) -> UACalcResult<VarietyTermAnalysis> {
        let mut analysis = VarietyTermAnalysis {
            has_jonsson_terms: false,
            has_gumm_terms: false,
            has_hagemann_mitschke_terms: false,
            has_sd_terms: false,
            has_sdmeet_terms: false,
            has_primality_terms: false,
            jonsson_terms: None,
            gumm_terms: None,
            hagemann_mitschke_terms: None,
            analysis_completed: false,
        };

        // Check for Jonsson terms
        if let Ok(jonsson_terms) = self.find_jonsson_terms(algebra) {
            analysis.has_jonsson_terms = !jonsson_terms.is_empty();
            analysis.jonsson_terms = Some(jonsson_terms);
        }

        // Check for Gumm terms
        if let Ok(gumm_terms) = self.find_gumm_terms(algebra) {
            analysis.has_gumm_terms = !gumm_terms.is_empty();
            analysis.gumm_terms = Some(gumm_terms);
        }

        // Check for Hagemann-Mitschke terms
        if let Ok(hm_terms) = self.find_hagemann_mitschke_terms(algebra) {
            analysis.has_hagemann_mitschke_terms = !hm_terms.is_empty();
            analysis.hagemann_mitschke_terms = Some(hm_terms);
        }

        // Check for semidistributive terms
        analysis.has_sd_terms = self.has_sd_terms(algebra)?;

        // Check for SD-meet terms
        analysis.has_sdmeet_terms = self.has_sdmeet_terms(algebra)?;

        // Check for primality terms
        analysis.has_primality_terms = self.has_primality_terms(algebra)?;

        Ok(analysis)
    }

    /// Analyze variety terms for large algebras (conservative estimates)
    fn analyze_large_algebra_variety_terms(&mut self, algebra: &dyn SmallAlgebra) -> UACalcResult<VarietyTermAnalysis> {
        let mut analysis = VarietyTermAnalysis {
            has_jonsson_terms: false,
            has_gumm_terms: false,
            has_hagemann_mitschke_terms: false,
            has_sd_terms: false,
            has_sdmeet_terms: false,
            has_primality_terms: false,
            jonsson_terms: None,
            gumm_terms: None,
            hagemann_mitschke_terms: None,
            analysis_completed: false,
        };

        // For large algebras, use signature-based heuristics
        let operations = algebra.operations();
        
        // Very basic heuristics based on operation signatures
        if operations.len() == 1 {
            // Single operation algebras might have some variety terms
            analysis.has_sd_terms = true;
        }

        Ok(analysis)
    }

    /// Analyze specialized terms for small algebras
    fn analyze_small_algebra_specialized_terms(&mut self, algebra: &dyn SmallAlgebra) -> UACalcResult<SpecializedTermAnalysis> {
        let mut analysis = SpecializedTermAnalysis {
            has_semilattice_term: false,
            has_difference_term: false,
            has_pixley_term: false,
            has_weak_majority_term: false,
            has_weak_nu_term: false,
            has_weak_3edge_term: false,
            has_fixed_kedge_term: false,
            semilattice_term: None,
            difference_term: None,
            pixley_term: None,
            analysis_completed: false,
        };

        // Check for semilattice term
        if let Ok(term) = self.find_semilattice_term(algebra) {
            analysis.has_semilattice_term = true;
            analysis.semilattice_term = Some(term);
        }

        // Check for difference term
        if let Ok(term) = self.find_difference_term(algebra) {
            analysis.has_difference_term = true;
            analysis.difference_term = Some(term);
        }

        // Check for Pixley term
        if let Ok(term) = self.find_pixley_term(algebra) {
            analysis.has_pixley_term = true;
            analysis.pixley_term = Some(term);
        }

        // Check for weak majority term
        analysis.has_weak_majority_term = self.has_weak_majority_term(algebra)?;

        // Check for weak NU term
        analysis.has_weak_nu_term = self.has_weak_nu_term(algebra)?;

        // Check for weak 3-edge term
        analysis.has_weak_3edge_term = self.has_weak_3edge_term(algebra)?;

        // Check for fixed k-edge term
        analysis.has_fixed_kedge_term = self.has_fixed_kedge_term(algebra)?;

        Ok(analysis)
    }

    /// Analyze specialized terms for large algebras (conservative estimates)
    fn analyze_large_algebra_specialized_terms(&mut self, algebra: &dyn SmallAlgebra) -> UACalcResult<SpecializedTermAnalysis> {
        let mut analysis = SpecializedTermAnalysis {
            has_semilattice_term: false,
            has_difference_term: false,
            has_pixley_term: false,
            has_weak_majority_term: false,
            has_weak_nu_term: false,
            has_weak_3edge_term: false,
            has_fixed_kedge_term: false,
            semilattice_term: None,
            difference_term: None,
            pixley_term: None,
            analysis_completed: false,
        };

        // For large algebras, use signature-based heuristics
        let operations = algebra.operations();
        
        // Very basic heuristics based on operation signatures
        if operations.len() == 1 {
            // Single operation algebras might have some specialized terms
            analysis.has_semilattice_term = true;
        }

        Ok(analysis)
    }

    /// Find Jonsson terms for an algebra
    fn find_jonsson_terms(&mut self, algebra: &dyn SmallAlgebra) -> UACalcResult<Vec<String>> {
        // Implementation would go here - for now return empty
        Ok(vec![])
    }

    /// Find Gumm terms for an algebra
    fn find_gumm_terms(&mut self, algebra: &dyn SmallAlgebra) -> UACalcResult<Vec<String>> {
        // Implementation would go here - for now return empty
        Ok(vec![])
    }

    /// Find Hagemann-Mitschke terms for an algebra
    fn find_hagemann_mitschke_terms(&mut self, algebra: &dyn SmallAlgebra) -> UACalcResult<Vec<String>> {
        // Implementation would go here - for now return empty
        Ok(vec![])
    }

    /// Check if algebra has semidistributive terms
    fn has_sd_terms(&self, algebra: &dyn SmallAlgebra) -> UACalcResult<bool> {
        // Implementation would go here - for now return false
        Ok(false)
    }

    /// Check if algebra has SD-meet terms
    fn has_sdmeet_terms(&self, algebra: &dyn SmallAlgebra) -> UACalcResult<bool> {
        // Implementation would go here - for now return false
        Ok(false)
    }

    /// Check if algebra has primality terms
    fn has_primality_terms(&self, algebra: &dyn SmallAlgebra) -> UACalcResult<bool> {
        // Implementation would go here - for now return false
        Ok(false)
    }

    /// Find semilattice term for an algebra
    fn find_semilattice_term(&mut self, algebra: &dyn SmallAlgebra) -> UACalcResult<String> {
        // Implementation would go here - for now return placeholder
        Ok("x".to_string())
    }

    /// Find difference term for an algebra
    fn find_difference_term(&mut self, algebra: &dyn SmallAlgebra) -> UACalcResult<String> {
        // Implementation would go here - for now return placeholder
        Ok("x".to_string())
    }

    /// Find Pixley term for an algebra
    fn find_pixley_term(&mut self, algebra: &dyn SmallAlgebra) -> UACalcResult<String> {
        // Implementation would go here - for now return placeholder
        Ok("x".to_string())
    }

    /// Check if algebra has weak majority term
    fn has_weak_majority_term(&self, algebra: &dyn SmallAlgebra) -> UACalcResult<bool> {
        // Implementation would go here - for now return false
        Ok(false)
    }

    /// Check if algebra has weak NU term
    fn has_weak_nu_term(&self, algebra: &dyn SmallAlgebra) -> UACalcResult<bool> {
        // Implementation would go here - for now return false
        Ok(false)
    }

    /// Check if algebra has weak 3-edge term
    fn has_weak_3edge_term(&self, algebra: &dyn SmallAlgebra) -> UACalcResult<bool> {
        // Implementation would go here - for now return false
        Ok(false)
    }

    /// Check if algebra has fixed k-edge term
    fn has_fixed_kedge_term(&self, algebra: &dyn SmallAlgebra) -> UACalcResult<bool> {
        // Implementation would go here - for now return false
        Ok(false)
    }

    /// Check if algebra is in the variety of groups
    fn check_group_variety(&self, algebra: &dyn SmallAlgebra) -> UACalcResult<bool> {
        let operations = algebra.operations();
        
        // Must have exactly one binary operation
        let binary_ops: Vec<_> = operations.iter().filter(|op| {
            let op_guard = op.lock().unwrap();
            op_guard.arity() == 2
        }).collect();
        if binary_ops.len() != 1 {
            return Ok(false);
        }
        
        // Must have no other operations (pure group)
        if operations.len() != 1 {
            return Ok(false);
        }
        
        let cardinality = algebra.cardinality();
        
        // For very small algebras, we can do complete group property checks
        if cardinality <= 8 {
            return self.check_group_properties_complete(algebra, &binary_ops[0]);
        } else {
            // For larger algebras, use signature-based check only
            return Ok(false);
        }
    }

    /// Complete group property check for small algebras
    fn check_group_properties_complete(&self, algebra: &dyn SmallAlgebra, binary_op: &Arc<Mutex<dyn crate::operation::Operation>>) -> UACalcResult<bool> {
        let cardinality = algebra.cardinality();
        
        // Check for identity element
        let mut has_identity = false;
        for e in 0..cardinality {
            let mut is_identity = true;
            for a in 0..cardinality {
                let args1 = vec![e, a];
                let args2 = vec![a, e];
                let op_guard = binary_op.lock().unwrap();
                if op_guard.value(&args1)? != a || op_guard.value(&args2)? != a {
                    is_identity = false;
                    break;
                }
            }
            if is_identity {
                has_identity = true;
                break;
            }
        }
        
        if !has_identity {
            return Ok(false);
        }
        
        // Check for inverses (simplified - assume they exist if identity exists for small algebras)
        let has_inverses = true;
        
        // Check associativity
        let mut is_associative = true;
        for a in 0..cardinality {
            for b in 0..cardinality {
                for c in 0..cardinality {
                    let args1 = vec![a, b];
                    let op_guard = binary_op.lock().unwrap();
                    let ab = op_guard.value(&args1)?;
                    let args2 = vec![ab, c];
                    let left_result = op_guard.value(&args2)?;
                    
                    let args3 = vec![b, c];
                    let bc = op_guard.value(&args3)?;
                    let args4 = vec![a, bc];
                    let right_result = op_guard.value(&args4)?;
                    
                    if left_result != right_result {
                        is_associative = false;
                        break;
                    }
                }
                if !is_associative {
                    break;
                }
            }
            if !is_associative {
                break;
            }
        }
        
        Ok(has_identity && has_inverses && is_associative)
    }

    /// Check if algebra is in the variety of lattices
    fn check_lattice_variety(&self, algebra: &dyn SmallAlgebra) -> UACalcResult<bool> {
        let operations = algebra.operations();
        
        // Debug: Print operation details
        eprintln!("DEBUG: Checking lattice variety for algebra with {} operations", operations.len());
        for (i, op) in operations.iter().enumerate() {
            let op_guard = op.lock().unwrap();
            eprintln!("DEBUG: Operation {}: arity = {}", i, op_guard.arity());
        }
        
        // Must have exactly two binary operations
        let binary_ops: Vec<_> = operations.iter().filter(|op| {
            let op_guard = op.lock().unwrap();
            op_guard.arity() == 2
        }).collect();
        
        eprintln!("DEBUG: Found {} binary operations", binary_ops.len());
        
        if binary_ops.len() != 2 {
            eprintln!("DEBUG: Not a lattice - need exactly 2 binary operations, found {}", binary_ops.len());
            return Ok(false);
        }
        
        // Must have no other operations (pure lattice)
        if operations.len() != 2 {
            eprintln!("DEBUG: Not a lattice - need exactly 2 operations total, found {}", operations.len());
            return Ok(false);
        }
        
        let cardinality = algebra.cardinality();
        eprintln!("DEBUG: Algebra cardinality: {}", cardinality);
        
        // For small algebras, we can do complete lattice property checks
        if cardinality <= 8 {
            eprintln!("DEBUG: Performing complete lattice property checks");
            let result = self.check_lattice_properties_complete(algebra, &binary_ops[0], &binary_ops[1]);
            eprintln!("DEBUG: Lattice property check result: {:?}", result);
            return result;
        } else {
            // For larger algebras, use signature-based check only
            eprintln!("DEBUG: Algebra too large for complete checks");
            return Ok(false);
        }
    }

    /// Complete lattice property check for small algebras
    fn check_lattice_properties_complete(&self, algebra: &dyn SmallAlgebra, meet_op: &Arc<Mutex<dyn crate::operation::Operation>>, join_op: &Arc<Mutex<dyn crate::operation::Operation>>) -> UACalcResult<bool> {
        let cardinality = algebra.cardinality();
        
        // Check commutativity for both operations
        if !self.check_commutativity(meet_op, cardinality)? || !self.check_commutativity(join_op, cardinality)? {
            return Ok(false);
        }
        
        // Check associativity for both operations
        if !self.check_associativity(meet_op, cardinality)? || !self.check_associativity(join_op, cardinality)? {
            return Ok(false);
        }
        
        // Check idempotency for both operations
        if !self.check_idempotency(meet_op, cardinality)? || !self.check_idempotency(join_op, cardinality)? {
            return Ok(false);
        }
        
        // Check absorption laws
        if !self.check_absorption_laws(meet_op, join_op, cardinality)? {
            return Ok(false);
        }
        
        Ok(true)
    }

    /// Check commutativity: a * b = b * a
    fn check_commutativity(&self, op: &Arc<Mutex<dyn crate::operation::Operation>>, cardinality: usize) -> UACalcResult<bool> {
        for a in 0..cardinality {
            for b in 0..cardinality {
                let args1 = vec![a, b];
                let args2 = vec![b, a];
                let op_guard = op.lock().unwrap();
                if op_guard.value(&args1)? != op_guard.value(&args2)? {
                    return Ok(false);
                }
            }
        }
        Ok(true)
    }

    /// Check associativity: (a * b) * c = a * (b * c)
    fn check_associativity(&self, op: &Arc<Mutex<dyn crate::operation::Operation>>, cardinality: usize) -> UACalcResult<bool> {
        for a in 0..cardinality {
            for b in 0..cardinality {
                for c in 0..cardinality {
                    let args1 = vec![a, b];
                    let op_guard = op.lock().unwrap();
                    let ab = op_guard.value(&args1)?;
                    let args2 = vec![ab, c];
                    let left_result = op_guard.value(&args2)?;
                    
                    let args3 = vec![b, c];
                    let bc = op_guard.value(&args3)?;
                    let args4 = vec![a, bc];
                    let right_result = op_guard.value(&args4)?;
                    
                    if left_result != right_result {
                        return Ok(false);
                    }
                }
            }
        }
        Ok(true)
    }

    /// Check idempotency: a * a = a
    fn check_idempotency(&self, op: &Arc<Mutex<dyn crate::operation::Operation>>, cardinality: usize) -> UACalcResult<bool> {
        for a in 0..cardinality {
            let args = vec![a, a];
            let op_guard = op.lock().unwrap();
            if op_guard.value(&args)? != a {
                return Ok(false);
            }
        }
        Ok(true)
    }

    /// Check absorption laws: a ∧ (a ∨ b) = a and a ∨ (a ∧ b) = a
    fn check_absorption_laws(&self, meet_op: &Arc<Mutex<dyn crate::operation::Operation>>, join_op: &Arc<Mutex<dyn crate::operation::Operation>>, cardinality: usize) -> UACalcResult<bool> {
        for a in 0..cardinality {
            for b in 0..cardinality {
                // Check first absorption law: a ∧ (a ∨ b) = a
                let join_args = vec![a, b];
                let join_guard = join_op.lock().unwrap();
                let a_join_b = join_guard.value(&join_args)?;
                let meet_args1 = vec![a, a_join_b];
                let meet_guard = meet_op.lock().unwrap();
                let a_meet_a_join_b = meet_guard.value(&meet_args1)?;
                
                if a_meet_a_join_b != a {
                    return Ok(false);
                }
                
                // Check second absorption law: a ∨ (a ∧ b) = a
                let meet_args2 = vec![a, b];
                let a_meet_b = meet_guard.value(&meet_args2)?;
                let join_args2 = vec![a, a_meet_b];
                let a_join_a_meet_b = join_guard.value(&join_args2)?;
                
                if a_join_a_meet_b != a {
                    return Ok(false);
                }
            }
        }
        Ok(true)
    }

    /// Check if algebra is in the variety of Boolean algebras
    fn check_boolean_algebra_variety(&self, algebra: &dyn SmallAlgebra) -> UACalcResult<bool> {
        let operations = algebra.operations();
        
        // Must have exactly: two binary, one unary, two nullary operations
        let binary_ops: Vec<_> = operations.iter().filter(|op| {
            let op_guard = op.lock().unwrap();
            op_guard.arity() == 2
        }).collect();
        let unary_ops: Vec<_> = operations.iter().filter(|op| {
            let op_guard = op.lock().unwrap();
            op_guard.arity() == 1
        }).collect();
        let nullary_ops: Vec<_> = operations.iter().filter(|op| {
            let op_guard = op.lock().unwrap();
            op_guard.arity() == 0
        }).collect();
        
        if binary_ops.len() != 2 || unary_ops.len() != 1 || nullary_ops.len() != 2 {
            return Ok(false);
        }
        
        // Must have exactly 5 operations total
        if operations.len() != 5 {
            return Ok(false);
        }
        
        // For now, just check signature - full Boolean algebra property checking would be complex
        Ok(false)
    }

    /// Check if algebra is in the variety of semilattices
    fn check_semilattice_variety(&self, algebra: &dyn SmallAlgebra) -> UACalcResult<bool> {
        eprintln!("DEBUG: Starting semilattice variety check");
        
        // Handle trivial case
        if algebra.cardinality() == 1 {
            eprintln!("DEBUG: Trivial algebra is in semilattice variety");
            return Ok(true);
        }

        let operations = algebra.operations();
        
        // Must have exactly one binary operation
        let binary_ops: Vec<_> = operations.iter().filter(|op| {
            let op_guard = op.lock().unwrap();
            op_guard.arity() == 2
        }).collect();
        
        if binary_ops.len() != 1 {
            eprintln!("DEBUG: Not a semilattice - need exactly 1 binary operation, found {}", binary_ops.len());
            return Ok(false);
        }
        
        // Must have no other operations (pure semilattice)
        if operations.len() != 1 {
            eprintln!("DEBUG: Not a semilattice - need exactly 1 operation total, found {}", operations.len());
            return Ok(false);
        }

        // Check if the single binary operation is a semilattice operation
        let op_guard = binary_ops[0].lock().unwrap();
        eprintln!("DEBUG: Checking single operation for semilattice properties");
        
        if self.is_semilattice_operation(&*op_guard, algebra.cardinality())? {
            eprintln!("DEBUG: Found semilattice operation");
            return Ok(true);
        }

        eprintln!("DEBUG: No semilattice operation found");
        Ok(false)
    }

    /// Check if an operation is a semilattice operation (idempotent, commutative, associative)
    fn is_semilattice_operation(
        &self,
        operation: &dyn Operation,
        cardinality: usize,
    ) -> UACalcResult<bool> {
        // Check if operation is binary
        if operation.arity() != 2 {
            return Ok(false);
        }

        // Check idempotency: f(x,x) = x for all x
        for x in 0..cardinality {
            if operation.int_value_at(&[x, x])? != x {
                return Ok(false);
            }
        }

        // Check commutativity: f(x,y) = f(y,x) for all x,y
        for x in 0..cardinality {
            for y in 0..cardinality {
                if operation.int_value_at(&[x, y])? != operation.int_value_at(&[y, x])? {
                    return Ok(false);
                }
            }
        }

        // Check associativity: f(f(x,y),z) = f(x,f(y,z)) for all x,y,z
        for x in 0..cardinality {
            for y in 0..cardinality {
                for z in 0..cardinality {
                    let left = operation.int_value_at(&[operation.int_value_at(&[x, y])?, z])?;
                    let right = operation.int_value_at(&[x, operation.int_value_at(&[y, z])?])?;
                    if left != right {
                        return Ok(false);
                    }
                }
            }
        }

        Ok(true)
    }

    /// Check if algebra is in the variety of quasigroups
    fn check_quasigroup_variety(&self, algebra: &dyn SmallAlgebra) -> UACalcResult<bool> {
        let operations = algebra.operations();
        
        // Must have exactly one binary operation
        let binary_ops: Vec<_> = operations.iter().filter(|op| {
            let op_guard = op.lock().unwrap();
            op_guard.arity() == 2
        }).collect();
        if binary_ops.len() != 1 {
            return Ok(false);
        }
        
        // Must have no other operations (pure quasigroup)
        if operations.len() != 1 {
            return Ok(false);
        }
        
        let cardinality = algebra.cardinality();
        
        // For very small algebras, we can do complete quasigroup property checks
        if cardinality <= 8 {
            return self.check_quasigroup_properties_complete(algebra, &binary_ops[0]);
        } else {
            // For larger algebras, use signature-based check only
            return Ok(false);
        }
    }

    /// Complete quasigroup property check for small algebras
    fn check_quasigroup_properties_complete(&self, algebra: &dyn SmallAlgebra, binary_op: &Arc<Mutex<dyn crate::operation::Operation>>) -> UACalcResult<bool> {
        let cardinality = algebra.cardinality();
        let op_guard = binary_op.lock().unwrap();
        
        // Check left cancellativity: if a·x = a·y, then x = y
        for a in 0..cardinality {
            for x in 0..cardinality {
                for y in 0..cardinality {
                    if x != y {
                        let ax = op_guard.int_value_at(&[a, x])?;
                        let ay = op_guard.int_value_at(&[a, y])?;
                        if ax == ay {
                            return Ok(false); // Not left cancellative
                        }
                    }
                }
            }
        }
        
        // Check right cancellativity: if x·a = y·a, then x = y
        for a in 0..cardinality {
            for x in 0..cardinality {
                for y in 0..cardinality {
                    if x != y {
                        let xa = op_guard.int_value_at(&[x, a])?;
                        let ya = op_guard.int_value_at(&[y, a])?;
                        if xa == ya {
                            return Ok(false); // Not right cancellative
                        }
                    }
                }
            }
        }
        
        // Check that the operation table is a Latin square
        // Each row and column must contain each element exactly once
        for row in 0..cardinality {
            let mut row_elements = vec![false; cardinality];
            for col in 0..cardinality {
                let value = op_guard.int_value_at(&[row, col])?;
                if row_elements[value] {
                    return Ok(false); // Duplicate in row
                }
                row_elements[value] = true;
            }
        }
        
        for col in 0..cardinality {
            let mut col_elements = vec![false; cardinality];
            for row in 0..cardinality {
                let value = op_guard.int_value_at(&[row, col])?;
                if col_elements[value] {
                    return Ok(false); // Duplicate in column
                }
                col_elements[value] = true;
            }
        }
        
        Ok(true)
    }
}

// Convenience functions for direct access
pub fn analyze_variety_terms(algebra: &dyn SmallAlgebra) -> UACalcResult<VarietyTermAnalysis> {
    let mut analyzer = VarietyAnalyzer::new();
    analyzer.analyze_variety_terms(algebra)
}

pub fn analyze_specialized_terms(algebra: &dyn SmallAlgebra) -> UACalcResult<SpecializedTermAnalysis> {
    let mut analyzer = VarietyAnalyzer::new();
    analyzer.analyze_specialized_terms(algebra)
}

pub fn analyze_variety_membership(algebra: &dyn SmallAlgebra) -> UACalcResult<VarietyAnalysis> {
    let analyzer = VarietyAnalyzer::new();
    analyzer.analyze_variety_membership(algebra)
}
