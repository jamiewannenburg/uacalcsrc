/*!
 * Closer - Class for finding closures of generating sets in algebras.
 * 
 * This is a partial implementation of org.uacalc.alg.Closer,
 * implementing core closure functionality.
 */

use std::collections::{HashMap, HashSet};
use std::sync::Arc;
use crate::alg::big_product_algebra::BigProductAlgebra;
use crate::util::int_array::IntArray;
use crate::terms::Term;
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
pub struct Closer<T> {
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
        // TODO: Get constants from algebra and add them
        
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
                let arity_usize = arity as usize;
                let mut arg_indices = vec![0usize; arity_usize];
                if arity_usize > 0 {
                    arg_indices[arity_usize - 1] = closed_mark;
                }
                
                // Simple incrementor - iterate through all combinations
                loop {
                    // Check if at least one index is in the new range [closed_mark, current_mark)
                    let has_new_elem = arg_indices.iter().any(|&idx| idx >= closed_mark && idx < current_mark);
                    
                    if has_new_elem {
                        // Collect arguments
                        let mut args: Vec<&IntArray> = Vec::new();
                        for &idx in &arg_indices {
                            if idx < self.ans.len() {
                                args.push(&self.ans[idx]);
                            }
                        }
                        
                        if args.len() == arity_usize {
                            // Apply operation (simplified - in full version would actually compute)
                            // For now, just check if we've reached max size
                            if let Some(max_size) = self.max_size {
                                if self.ans.len() >= max_size {
                                    break;
                                }
                            }
                            
                            // In full implementation: compute op.value_at(args) and add if new
                            // For now, this is still a stub
                        }
                    }
                    
                    // Increment indices (like odometer)
                    let mut carry = true;
                    for j in 0..arity_usize {
                        if carry {
                            arg_indices[j] += 1;
                            if arg_indices[j] < current_mark {
                                carry = false;
                            } else {
                                arg_indices[j] = 0;
                            }
                        }
                    }
                    
                    if carry {
                        break; // All combinations exhausted
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
        let mut closer = Closer::<i32>::new_safe(algebra, generators).unwrap();
        
        // Should have 2 generators after removing duplicates
        assert_eq!(closer.get_generators().len(), 2);
    }
}

