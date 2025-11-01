/*!
 * Closer - Class for finding closures of generating sets in algebras.
 * 
 * This is a partial implementation of org.uacalc.alg.Closer,
 * implementing core closure functionality.
 */

use std::collections::{HashMap, HashSet};
use std::sync::Arc;
use std::hash::Hash;
use std::fmt::Debug;
use crate::alg::big_product_algebra::BigProductAlgebra;
use crate::alg::Algebra;
use crate::util::int_array::{IntArray, IntArrayTrait};
use crate::terms::{Term, NonVariableTerm};
use crate::progress::ProgressReport;

/// A class for finding the closure of generating sets in algebras.
/// 
/// The `Closer` class provides methods for computing the subuniverses generated
/// by a set of elements in a `BigProductAlgebra`. It supports various configuration
/// options and can track progress during long-running closure operations.
/// 
/// # Examples
/// ```ignore
/// use uacalc::alg::{Closer, BigProductAlgebra};
/// use uacalc::util::int_array::IntArray;
/// 
/// // Create a BigProductAlgebra (details omitted)
/// // let algebra = ...;
/// 
/// // Create generators
/// // let generators = vec![IntArray::new(2).unwrap()];
/// 
/// // Create closer and compute closure
/// // let mut closer = Closer::new_safe(algebra, generators).unwrap();
/// // let result = closer.sg_close();
/// ```
pub struct Closer<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Send + Sync + 'static
{
    /// The algebra we're working with
    algebra: Arc<BigProductAlgebra<T>>,
    
    /// The generators
    generators: Vec<IntArray>,
    
    /// The answer (closure result)
    ans: Vec<IntArray>,
    
    /// Whether the closure completed successfully
    completed: bool,
    
    /// Term map from elements to terms that generate them
    term_map: Option<HashMap<IntArray, Box<dyn Term>>>,
    
    /// Element to find during closure
    elt_to_find: Option<IntArray>,
    
    /// Progress reporter
    report: Option<Arc<dyn ProgressReport>>,
    
    /// Whether to suppress output
    suppress_output: bool,
    
    /// Maximum size (stop when reached)
    max_size: Option<usize>,
}

impl<T> Closer<T>
where
    T: Clone + PartialEq + Eq + std::hash::Hash + std::fmt::Debug + Send + Sync + 'static
{
    /// Create a new Closer with an algebra and generators.
    /// 
    /// # Arguments
    /// * `algebra` - The BigProductAlgebra to work with
    /// * `generators` - The generating set
    /// 
    /// # Returns
    /// * `Ok(Closer)` - Successfully created closer
    /// * `Err(String)` - If inputs are invalid
    /// 
    /// # Examples
    /// ```ignore
    /// use uacalc::alg::{Closer, BigProductAlgebra};
    /// use uacalc::util::int_array::IntArray;
    /// 
    /// // let algebra = ...;
    /// // let generators = vec![IntArray::new(2).unwrap()];
    /// // let closer = Closer::new_safe(algebra, generators).unwrap();
    /// ```
    pub fn new_safe(
        algebra: Arc<BigProductAlgebra<T>>,
        generators: Vec<IntArray>
    ) -> Result<Self, String> {
        let mut closer = Closer {
            algebra,
            generators: Vec::new(),
            ans: Vec::new(),
            completed: false,
            term_map: None,
            elt_to_find: None,
            report: None,
            suppress_output: false,
            max_size: None,
        };
        
        closer.set_generators(generators);
        
        Ok(closer)
    }
    
    /// Create a new Closer with an algebra, generators, and term map.
    /// 
    /// # Arguments
    /// * `algebra` - The BigProductAlgebra to work with
    /// * `generators` - The generating set
    /// * `term_map` - Initial term map
    /// 
    /// # Returns
    /// * `Ok(Closer)` - Successfully created closer
    /// * `Err(String)` - If inputs are invalid
    pub fn new_with_term_map_safe(
        algebra: Arc<BigProductAlgebra<T>>,
        generators: Vec<IntArray>,
        term_map: HashMap<IntArray, Box<dyn Term>>
    ) -> Result<Self, String> {
        let mut closer = Self::new_safe(algebra, generators)?;
        closer.term_map = Some(term_map);
        Ok(closer)
    }
    
    /// Create a new Closer (panicking version).
    /// 
    /// # Arguments
    /// * `algebra` - The BigProductAlgebra to work with
    /// * `generators` - The generating set
    /// 
    /// # Panics
    /// Panics if inputs are invalid
    pub fn new(
        algebra: Arc<BigProductAlgebra<T>>,
        generators: Vec<IntArray>
    ) -> Self {
        Self::new_safe(algebra, generators).unwrap()
    }
    
    /// Set the generators, removing duplicates.
    /// 
    /// # Arguments
    /// * `gens` - The new generators
    pub fn set_generators(&mut self, gens: Vec<IntArray>) {
        self.generators = Vec::new();
        let mut seen = HashSet::new();
        
        for ia in gens {
            if seen.insert(ia.clone()) {
                self.generators.push(ia);
            }
        }
    }
    
    /// Get the generators.
    /// 
    /// # Returns
    /// A reference to the generators
    pub fn get_generators(&self) -> &[IntArray] {
        &self.generators
    }
    
    /// Get the answer (closure result).
    /// 
    /// # Returns
    /// A reference to the closure result
    pub fn get_answer(&self) -> &[IntArray] {
        &self.ans
    }
    
    /// Get the term map.
    /// 
    /// # Returns
    /// A reference to the term map, if it exists
    pub fn get_term_map(&self) -> Option<&HashMap<IntArray, Box<dyn Term>>> {
        self.term_map.as_ref()
    }
    
    /// Set the term map.
    /// 
    /// # Arguments
    /// * `term_map` - The new term map
    pub fn set_term_map(&mut self, term_map: Option<HashMap<IntArray, Box<dyn Term>>>) {
        self.term_map = term_map;
    }
    
    /// Set the element to find.
    /// 
    /// # Arguments
    /// * `elt` - The element to search for during closure
    pub fn set_element_to_find(&mut self, elt: Option<IntArray>) {
        self.elt_to_find = elt;
    }
    
    /// Get the element to find.
    /// 
    /// # Returns
    /// The element to find, if set
    pub fn get_element_to_find(&self) -> Option<&IntArray> {
        self.elt_to_find.as_ref()
    }
    
    /// Set the progress reporter.
    /// 
    /// # Arguments
    /// * `report` - The progress reporter to use
    pub fn set_progress_report(&mut self, report: Option<Arc<dyn ProgressReport>>) {
        self.report = report;
    }
    
    /// Set whether to suppress output.
    /// 
    /// # Arguments
    /// * `suppress` - Whether to suppress output
    pub fn set_suppress_output(&mut self, suppress: bool) {
        self.suppress_output = suppress;
    }
    
    /// Get whether output is suppressed.
    /// 
    /// # Returns
    /// `true` if output is suppressed
    pub fn is_suppress_output(&self) -> bool {
        self.suppress_output
    }
    
    /// Set the maximum size.
    /// 
    /// # Arguments
    /// * `max_size` - Maximum size (None for no limit)
    pub fn set_max_size(&mut self, max_size: Option<usize>) {
        self.max_size = max_size;
    }
    
    /// Get the maximum size.
    /// 
    /// # Returns
    /// The maximum size, if set
    pub fn get_max_size(&self) -> Option<usize> {
        self.max_size
    }
    
    /// Compute the closure of the generators.
    /// 
    /// This is the main method that computes the subuniverse generated by
    /// the generators under the operations of the algebra.
    /// 
    /// # Returns
    /// * `Ok(Vec<IntArray>)` - The closure (list of elements)
    /// * `Err(String)` - If closure computation fails
    /// 
    /// # Examples
    /// ```ignore
    /// use uacalc::alg::Closer;
    /// 
    /// // let mut closer = ...;
    /// // let closure = closer.sg_close()?;
    /// ```
    pub fn sg_close(&mut self) -> Result<Vec<IntArray>, String> {
        self.sg_close_impl(0)
    }
    
    /// Implementation of closure computation.
    /// 
    /// # Arguments
    /// * `closed_mark` - The index up to which elements are already closed
    /// 
    /// # Returns
    /// * `Ok(Vec<IntArray>)` - The closure
    /// * `Err(String)` - If computation fails
    fn sg_close_impl(&mut self, closed_mark: usize) -> Result<Vec<IntArray>, String> {
        if let Some(ref report) = self.report {
            report.add_start_line("subpower closing ...");
        }
        
        // Initialize answer with generators
        self.ans = self.generators.clone();
        let mut su = HashSet::new();
        for ia in &self.ans {
            su.insert(ia.clone());
        }
        
        // Add constants if any
        // Get constants from algebra and add them
        let operations = self.algebra.as_ref().operations();
        for op in &operations {
            if op.arity() == 0i32 {
                // Evaluate the nullary operation to get the constant value
                match op.value_at_arrays(&[]) {
                    Ok(vals) => {
                        if let Ok(constant_arr) = IntArray::from_array(vals) {
                            if su.insert(constant_arr.clone()) {
                                self.ans.push(constant_arr.clone());
                                // Add to term map if it exists
                                if let Some(ref mut term_map) = self.term_map {
                                    let symbol = op.symbol().clone();
                                    let constant_term = Box::new(NonVariableTerm::make_constant_term(symbol)) as Box<dyn Term>;
                                    term_map.insert(constant_arr, constant_term);
                                }
                            }
                        }
                    }
                    Err(_) => {
                        // Ignore malformed operations
                    }
                }
            }
        }
        
        let mut current_mark = self.ans.len();
        let mut pass = 0;
        let mut closed_mark = closed_mark;
        
        // Main closure loop
        while closed_mark < current_mark {
            let status_str = format!("pass: {}, size: {}", pass, self.ans.len());
            
            if let Some(ref report) = self.report {
                report.set_pass(pass);
                report.set_pass_size(self.ans.len());
                if !self.suppress_output {
                    report.add_line(&status_str);
                }
            } else if !self.suppress_output {
                println!("{}", status_str);
            }
            
            pass += 1;
            
            // Check max size
            if let Some(max_size) = self.max_size {
                if self.ans.len() >= max_size {
                    break;
                }
            }
            
            // Apply operations to expand the closure
            use crate::alg::Algebra;
            let operations = self.algebra.as_ref().operations();
            let num_ops = operations.len();
            
            for i in 0..num_ops {
                if i >= operations.len() {
                    break;
                }
                
                let op = &operations[i];
                let arity = op.arity();
                
                if arity == 0 {
                    continue; // Skip nullary operations (constants handled separately)
                }
                
                // Generate all argument combinations where at least one is from the new elements
                // Use SequenceGenerator for proper incrementor behavior matching Java
                let arity_usize = arity as usize;
                let mut arg_indices = vec![0i32; arity_usize];
                if arity_usize > 0 {
                    arg_indices[arity_usize - 1] = closed_mark as i32;
                }
                
                // Use SequenceGenerator incrementor (matching Java pattern)
                use crate::util::SequenceGenerator;
                let current_mark_i32 = current_mark as i32;
                let closed_mark_i32 = closed_mark as i32;
                // Java uses sequenceIncrementor(array, currentMark-1, closedMark)
                // But Rust's sequence_incrementor only takes 2 params, so we'll use sequence_incrementor_with_min
                let mut inc = SequenceGenerator::sequence_incrementor_with_min(
                    &mut arg_indices,
                    current_mark_i32 - 1,
                    closed_mark_i32
                );
                
                // Iterate through all combinations
                loop {
                    // Get current indices (use get_current to avoid borrow issues)
                    let indices = inc.get_current();
                    
                    // Check if at least one index is in the new range [closed_mark, current_mark)
                    let has_new_elem = indices.iter().any(|&idx| {
                        let idx_usize = idx as usize;
                        idx_usize >= closed_mark && idx_usize < current_mark
                    });
                    
                    if has_new_elem {
                        // Collect arguments
                        let mut args: Vec<&IntArray> = Vec::new();
                        for &idx in &indices {
                            let idx_usize = idx as usize;
                            if idx_usize < self.ans.len() {
                                args.push(&self.ans[idx_usize]);
                            }
                        }
                        
                        if args.len() == arity_usize {
                            // Apply operation and compute result
                            // Convert IntArray args to int arrays for operation
                            // args is Vec<&IntArray>, iter() gives &(&IntArray) = &&IntArray
                            // Use clone() or direct access
                            let arg_vecs: Vec<Vec<i32>> = args.iter()
                                .map(|&ia| ia.as_slice().to_vec())
                                .collect();
                            let arg_refs: Vec<&[i32]> = arg_vecs.iter()
                                .map(|v| v.as_slice())
                                .collect();
                            
                            // For product algebras, use value_at_arrays which returns an array
                            match op.value_at_arrays(&arg_refs) {
                                Ok(result_arr) => {
                                    if let Ok(result_ia) = IntArray::from_array(result_arr) {
                                        // Check if it's new
                                        if su.insert(result_ia.clone()) {
                                            // New element found - add to closure
                                            self.ans.push(result_ia.clone());
                                            
                                            // Add to term map if it exists
                                            if let Some(ref mut term_map) = self.term_map {
                                                let mut children = Vec::new();
                                                for &idx in &indices {
                                                    let idx_usize = idx as usize;
                                                    if idx_usize < self.ans.len() - 1 { // -1 because we just added result
                                                        if let Some(term) = term_map.get(&self.ans[idx_usize]) {
                                                            children.push(term.clone_box());
                                                        }
                                                    }
                                                }
                                                let symbol = op.symbol().clone();
                                                let new_term = Box::new(NonVariableTerm::new(symbol, children)) as Box<dyn Term>;
                                                term_map.insert(result_ia.clone(), new_term);
                                            }
                                            
                                            // Check if we found the element we're looking for
                                            if let Some(ref elt_to_find) = self.elt_to_find {
                                                if result_ia == *elt_to_find {
                                                    // Found target element
                                                    return Ok(self.ans.clone());
                                                }
                                            }
                                            
                                            // Check max size
                                            if let Some(max_size) = self.max_size {
                                                if self.ans.len() >= max_size {
                                                    break;
                                                }
                                            }
                                            
                                            // Update current_mark since we added a new element
                                            current_mark = self.ans.len();
                                        }
                                    }
                                }
                                Err(e) => {
                                    // Operation failed - continue to next combination
                                    // This might happen for malformed operations
                                    eprintln!("WARNING: Operation value_at_arrays failed: {}", e);
                                }
                            }
                        }
                    }
                    
                    // Increment for next iteration
                    if !inc.increment() {
                        break; // All combinations exhausted
                    }
                    
                    // Update current_mark in case new elements were added
                    let new_current_mark = self.ans.len();
                    if new_current_mark > current_mark {
                        current_mark = new_current_mark;
                        // Need to recreate incrementor with new bounds
                        // But for now, continue with existing bounds
                        // (Java doesn't recreate incrementor mid-loop)
                    }
                }
            }
            
            closed_mark = current_mark;
            current_mark = self.ans.len();
        }
        
        if let Some(ref report) = self.report {
            report.add_end_line(&format!("closing done, size = {}", self.ans.len()));
        }
        
        self.completed = true;
        Ok(self.ans.clone())
    }
    
    /// Check if closure completed successfully.
    /// 
    /// # Returns
    /// `true` if closure completed
    pub fn is_completed(&self) -> bool {
        self.completed
    }
}

impl<T> Clone for Closer<T>
where
    T: Clone + PartialEq + Eq + std::hash::Hash + std::fmt::Debug + Send + Sync + 'static
{
    fn clone(&self) -> Self {
        Closer {
            algebra: Arc::clone(&self.algebra),
            generators: self.generators.clone(),
            ans: self.ans.clone(),
            completed: self.completed,
            term_map: None, // Can't clone term map easily
            elt_to_find: self.elt_to_find.clone(),
            report: self.report.as_ref().map(Arc::clone),
            suppress_output: self.suppress_output,
            max_size: self.max_size,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::BasicSmallAlgebra;
    use std::collections::HashSet;
    
    #[test]
    fn test_new_closer() {
        let alg1 = Box::new(BasicSmallAlgebra::new(
            "A".to_string(),
            HashSet::from([0, 1]),
            Vec::new()
        )) as Box<dyn crate::alg::SmallAlgebra<UniverseItem = i32>>;
        
        let algebra = Arc::new(
            BigProductAlgebra::<i32>::new_power_safe(alg1, 2).unwrap()
        );
        
        let gen = IntArray::new(2).unwrap();
        let generators = vec![gen];
        
        let closer = Closer::<i32>::new_safe(algebra, generators).unwrap();
        assert_eq!(closer.get_generators().len(), 1);
    }
    
    #[test]
    fn test_set_generators_removes_duplicates() {
        let alg1 = Box::new(BasicSmallAlgebra::new(
            "A".to_string(),
            HashSet::from([0, 1]),
            Vec::new()
        )) as Box<dyn crate::alg::SmallAlgebra<UniverseItem = i32>>;
        
        let algebra = Arc::new(
            BigProductAlgebra::<i32>::new_power_safe(alg1, 2).unwrap()
        );
        
        let gen1 = IntArray::new(2).unwrap();
        let gen2 = IntArray::new(2).unwrap(); // Duplicate
        let gen3 = IntArray::from_array(vec![1, 0]).unwrap();
        
        let generators = vec![gen1, gen2, gen3];
        let closer = Closer::<i32>::new_safe(algebra, generators).unwrap();
        
        // Should have 2 generators after removing duplicates
        assert_eq!(closer.get_generators().len(), 2);
    }
    
    #[test]
    fn test_constants_added_to_closure() {
        use crate::alg::op::{OperationSymbol, operations};
        
        // Create a small algebra with a constant operation
        let set: HashSet<i32> = HashSet::from([0, 1]);
        let c_sym = OperationSymbol::new_safe("c", 0, false).unwrap();
        let c_val = 1; // constant value
        let c_op = operations::make_int_operation(c_sym.clone(), 2, vec![c_val]).unwrap();
        
        let alg1 = Box::new(BasicSmallAlgebra::new(
            "A".to_string(),
            set,
            vec![c_op]
        )) as Box<dyn crate::alg::SmallAlgebra<UniverseItem = i32>>;
        
        let algebra = Arc::new(
            BigProductAlgebra::<i32>::new_power_safe(alg1, 2).unwrap()
        );
        
        // Create generators
        let gen = IntArray::from_array(vec![0, 0]).unwrap();
        let generators = vec![gen];
        
        // Create closer and compute closure
        let mut closer = Closer::<i32>::new_safe(algebra, generators).unwrap();
        let result = closer.sg_close().unwrap();
        
        // The constant [1, 1] should be in the closure
        let expected_constant = IntArray::from_array(vec![c_val, c_val]).unwrap();
        assert!(result.contains(&expected_constant), 
                "Constant {:?} should be in closure, got: {:?}", 
                expected_constant, result);
        
        // The closure should include at least the generator and the constant
        assert!(result.len() >= 2, "Closure should have at least generator and constant");
    }
}

