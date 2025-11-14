/*!
 * Parallel single-operation closure implementation.
 * 
 * This module provides parallel closure operations for a single Operation,
 * replacing the Java `org.uacalc.alg.parallel.SingleClose` class.
 */

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::sync::atomic::{AtomicUsize, Ordering};
use crate::util::{IntArray, ArrayIncrementor, SequenceGenerator};
use crate::util::int_array::IntArrayTrait;
use crate::alg::op::Operation;
use crate::terms::{Term, NonVariableTerm};
use crate::alg::CloserTiming;
use crate::progress::ProgressReport;

/// Minimum computation size to trigger parallel processing
const MIN_COMPUTATION_SIZE: u64 = 1_000_000;

/// Result of a closure operation: list of new elements found
pub type CloseResult = Vec<IntArray>;

/// Performs one pass of partial closure with a single Operation using a parallel algorithm.
/// 
/// This struct implements parallel closure computation using Rust's threading capabilities
/// instead of Java's Fork-Join framework. It manages concurrent access to shared data
/// structures and handles progress reporting and timing.
/// 
/// # Examples
/// ```no_run
/// use std::collections::HashMap;
/// use std::sync::{Arc, Mutex};
/// use std::sync::atomic::AtomicUsize;
/// use uacalc::alg::parallel::SingleClose;
/// use uacalc::util::IntArray;
/// use uacalc::terms::Term;
/// 
/// // Create shared map and universe list
/// let map: Arc<Mutex<HashMap<IntArray, Box<dyn Term>>>> = Arc::new(Mutex::new(HashMap::new()));
/// let univ_list: Vec<IntArray> = vec![]; // Start with some initial elements
/// 
/// // Note: Full example requires an Operation implementation
/// ```
#[derive(Debug)]
pub struct SingleClose {
    /// The universe list (shared across threads)
    univ_list: Vec<IntArray>,
    
    /// Map from elements to terms (thread-safe)
    map: Arc<Mutex<HashMap<IntArray, Box<dyn Term>>>>,
    
    /// The operation to apply
    op: Arc<dyn Operation>,
    
    /// Minimum index in universe list
    min: usize,
    
    /// Maximum index in universe list
    max: usize,
    
    /// Counter for elements found (thread-safe)
    elts_found: Arc<AtomicUsize>,
    
    /// Number of parallel threads to use
    increment: usize,
    
    /// Total computation size
    computation_size: u64,
    
    /// Whether computation is too small for parallelization
    too_small: bool,
    
    /// Initial arrays for parallel workers (stored as i32 for compatibility with SequenceGenerator)
    arrays: Vec<Vec<i32>>,
    
    /// Results from parallel workers
    results: Vec<CloseResult>,
}

impl SingleClose {
    /// Create a new SingleClose instance.
    /// 
    /// # Arguments
    /// * `univ_list` - The universe list of elements
    /// * `map` - Map from elements to terms (thread-safe)
    /// * `op` - The operation to apply
    /// * `min` - Minimum index in universe list
    /// * `max` - Maximum index in universe list
    /// * `elts_found` - Counter for elements found
    /// 
    /// # Returns
    /// A new SingleClose instance
    /// 
    /// # Examples
    /// ```no_run
    /// use std::collections::HashMap;
    /// use std::sync::{Arc, Mutex};
    /// use std::sync::atomic::AtomicUsize;
    /// use uacalc::alg::parallel::SingleClose;
    /// use uacalc::util::IntArray;
    /// use uacalc::terms::Term;
    /// 
    /// let map: Arc<Mutex<HashMap<IntArray, Box<dyn Term>>>> = Arc::new(Mutex::new(HashMap::new()));
    /// let univ_list: Vec<IntArray> = vec![];
    /// let elts_found = Arc::new(AtomicUsize::new(0));
    /// 
    /// // Note: Requires Operation implementation
    /// // let sc = SingleClose::new(univ_list, map, op, 0, 10, elts_found);
    /// ```
    pub fn new(
        univ_list: Vec<IntArray>,
        map: Arc<Mutex<HashMap<IntArray, Box<dyn Term>>>>,
        op: Arc<dyn Operation>,
        min: usize,
        max: usize,
        elts_found: Arc<AtomicUsize>,
    ) -> Result<Self, String> {
        let computation_size = Self::compute_size(&univ_list, &*op, min, max)?;
        let increment = Self::calculate_increment(computation_size, max - min);
        let too_small = computation_size < MIN_COMPUTATION_SIZE;
        
        let mut single_close = SingleClose {
            univ_list,
            map,
            op,
            min,
            max,
            elts_found,
            increment,
            computation_size,
            too_small,
            arrays: Vec::new(),
            results: Vec::new(),
        };
        
        single_close.set_initial_arrays()?;
        Ok(single_close)
    }
    
    /// Compute the total computation size.
    /// 
    /// This calculates the number of operation applications times the vector length.
    fn compute_size(
        univ_list: &[IntArray],
        op: &dyn Operation,
        min: usize,
        max: usize,
    ) -> Result<u64, String> {
        if univ_list.is_empty() {
            return Ok(0);
        }
        
        let size = (max + 1) as u128;
        let mark = min as u128;
        let r = op.arity() as u32;
        
        // Calculate size^r - mark^r
        let ans = size.pow(r) - mark.pow(r);
        
        if ans > u64::MAX as u128 {
            return Ok(u64::MAX);
        }
        
        let array_len = univ_list[0].universe_size() as u64;
        Ok((ans as u64) * array_len)
    }
    
    /// Calculate the number of parallel increments to use.
    fn calculate_increment(computation_size: u64, range: usize) -> usize {
        if computation_size < MIN_COMPUTATION_SIZE {
            return 1;
        }
        if range < 6 {
            return 1;
        }
        2 // Can be adjusted based on available cores
    }
    
    /// Set up initial arrays for parallel workers.
    fn set_initial_arrays(&mut self) -> Result<(), String> {
        let k = self.op.arity() as usize;
        let mut a = vec![0i32; k];
        if k > 0 {
            a[k - 1] = self.min as i32;
        }
        
        let max_i32 = self.max as i32;
        let min_i32 = self.min as i32;
        
        for i in 0..self.increment {
            // Store the current array
            self.arrays.push(a.clone());
            
            // If not the last iteration, increment for next worker
            if i < self.increment - 1 {
                let mut tmp_inc = SequenceGenerator::sequence_incrementor_with_min(&mut a, max_i32, min_i32);
                tmp_inc.increment();
            }
        }
        
        Ok(())
    }
    
    /// Perform one closure step with optional progress reporting.
    /// 
    /// This method executes the parallel closure computation, updating the universe
    /// list and term map with newly found elements.
    /// 
    /// # Arguments
    /// * `report` - Optional progress reporter
    /// * `timing` - Optional timing tracker
    /// 
    /// # Returns
    /// A vector of vectors containing the new elements found by each worker
    /// 
    /// # Examples
    /// ```no_run
    /// use std::collections::HashMap;
    /// use std::sync::{Arc, Mutex};
    /// use std::sync::atomic::AtomicUsize;
    /// use uacalc::alg::parallel::SingleClose;
    /// use uacalc::util::IntArray;
    /// use uacalc::terms::Term;
    /// 
    /// let map: Arc<Mutex<HashMap<IntArray, Box<dyn Term>>>> = Arc::new(Mutex::new(HashMap::new()));
    /// let univ_list: Vec<IntArray> = vec![];
    /// let elts_found = Arc::new(AtomicUsize::new(0));
    /// 
    /// // Note: Requires Operation implementation
    /// // let mut sc = SingleClose::new(univ_list, map, op, 0, 10, elts_found).unwrap();
    /// // let results = sc.do_one_step(None, None);
    /// ```
    pub fn do_one_step(
        &mut self,
        report: Option<Arc<dyn ProgressReport>>,
        timing: Option<Arc<Mutex<CloserTiming>>>,
    ) -> Result<Vec<CloseResult>, String> {
        self.results.clear();
        
        // For small computations or single increment, use serial execution
        if self.increment == 1 || self.too_small {
            let result = self.do_one_step_serial(0, report.clone(), timing.clone())?;
            self.results.push(result);
        } else {
            // Parallel execution using std::thread
            // Clone necessary data for thread safety
            let univ_list = Arc::new(self.univ_list.clone());
            let map = Arc::clone(&self.map);
            let op = Arc::clone(&self.op);
            let min = self.min;
            let max = self.max;
            let elts_found = Arc::clone(&self.elts_found);
            let too_small = self.too_small;
            let increment = self.increment;
            
            // Create thread handles
            let mut handles = Vec::new();
            
            // Spawn worker threads (all but the last one)
            for i in 0..(increment - 1) {
                let univ_list_clone = Arc::clone(&univ_list);
                let map_clone = Arc::clone(&map);
                let op_clone = Arc::clone(&op);
                let report_clone = report.clone();
                let timing_clone = timing.clone();
                let elts_found_clone = Arc::clone(&elts_found);
                let worker_array = self.arrays[i].clone();
                
                let handle = std::thread::spawn(move || {
                    Self::do_one_step_serial_worker(
                        univ_list_clone,
                        map_clone,
                        op_clone,
                        worker_array,
                        min,
                        max,
                        too_small,
                        increment,
                        report_clone,
                        timing_clone,
                        elts_found_clone,
                    )
                });
                handles.push(handle);
            }
            
            // Execute last worker on current thread
            let last_array = self.arrays[increment - 1].clone();
            let last_result = Self::do_one_step_serial_worker(
                Arc::clone(&univ_list),
                Arc::clone(&map),
                Arc::clone(&op),
                last_array,
                min,
                max,
                too_small,
                increment,
                report.clone(),
                timing.clone(),
                Arc::clone(&elts_found),
            )?;
            self.results.push(last_result);
            
            // Wait for all threads to complete
            for handle in handles {
                match handle.join() {
                    Ok(Ok(result)) => self.results.push(result),
                    Ok(Err(e)) => return Err(e),
                    Err(_) => return Err("Thread panicked".to_string()),
                }
            }
        }
        
        // Update size in progress report
        if let Some(ref rep) = report {
            rep.set_size(self.univ_list.len());
        }
        
        Ok(self.results.clone())
    }
    
    /// Static helper method for worker threads.
    /// This is separated from the instance method to avoid borrowing issues.
    fn do_one_step_serial_worker(
        univ_list: Arc<Vec<IntArray>>,
        map: Arc<Mutex<HashMap<IntArray, Box<dyn Term>>>>,
        op: Arc<dyn Operation>,
        mut arg_indices: Vec<i32>,
        min: usize,
        max: usize,
        too_small: bool,
        increment: usize,
        report: Option<Arc<dyn ProgressReport>>,
        timing: Option<Arc<Mutex<CloserTiming>>>,
        elts_found: Arc<AtomicUsize>,
    ) -> Result<CloseResult, String> {
        let mut new_elts = Vec::new();
        let arity = op.arity() as usize;
        let max_i32 = max as i32;
        let min_i32 = min as i32;
        
        // Track whether we've processed the first combination
        let mut first = true;
        
        loop {
            // Build arguments for operation (before incrementing)
            let mut args = Vec::with_capacity(arity);
            for &idx in &arg_indices {
                let idx_usize = idx as usize;
                if idx_usize >= univ_list.len() {
                    return Err(format!("Index {} out of bounds for universe list of size {}", idx, univ_list.len()));
                }
                args.push(univ_list[idx_usize].as_slice());
            }
            
            // Apply operation
            let result_array = op.value_at_arrays(&args)?;
            let v = IntArray::from_array(result_array)?;
            
            // Update timing if present
            if let Some(ref t) = timing {
                if let Ok(mut timing_guard) = t.lock() {
                    timing_guard.increment_apps();
                }
            }
            
            // Check if element is new
            let is_new = {
                let map_guard = map.lock().unwrap();
                !map_guard.contains_key(&v)
            };
            
            if is_new {
                // Build term for this element
                let mut children: Vec<Box<dyn Term>> = Vec::new();
                for &idx in &arg_indices {
                    let idx_usize = idx as usize;
                    let map_guard = map.lock().unwrap();
                    if let Some(term) = map_guard.get(&univ_list[idx_usize]) {
                        children.push(term.clone_box());
                    } else {
                        return Err(format!("No term found for element at index {}", idx));
                    }
                }
                
                let term = Box::new(NonVariableTerm::new(
                    op.symbol().clone(),
                    children,
                )) as Box<dyn Term>;
                
                // Try to insert into map
                let mut map_guard = map.lock().unwrap();
                if !map_guard.contains_key(&v) {
                    map_guard.insert(v.clone(), term);
                    drop(map_guard); // Release lock before updating counters
                    
                    new_elts.push(v);
                    elts_found.fetch_add(1, Ordering::SeqCst);
                    
                    if let Some(ref rep) = report {
                        rep.set_size(elts_found.load(Ordering::SeqCst));
                    }
                    
                    if let Some(ref t) = timing {
                        if let Ok(timing_guard) = t.lock() {
                            timing_guard.increment_next_pass_size();
                        }
                    }
                }
            }
            
            // Increment to next combination
            // Create a temporary incrementor to update arg_indices
            let has_next = {
                let mut worker_inc = if too_small {
                    SequenceGenerator::sequence_incrementor_with_min(&mut arg_indices, max_i32, min_i32)
                } else {
                    SequenceGenerator::sequence_incrementor_with_jump(&mut arg_indices, max_i32, min_i32, increment)
                };
                
                // On first iteration, we already have the initial value, don't increment yet
                if first {
                    first = false;
                    true
                } else {
                    worker_inc.increment()
                }
            };
            
            if !has_next {
                break;
            }
        }
        
        Ok(new_elts)
    }
    
    /// Perform one serial closure step.
    /// 
    /// This is called for serial execution or as a wrapper for the worker method.
    fn do_one_step_serial(
        &self,
        worker_id: usize,
        report: Option<Arc<dyn ProgressReport>>,
        timing: Option<Arc<Mutex<CloserTiming>>>,
    ) -> Result<CloseResult, String> {
        Self::do_one_step_serial_worker(
            Arc::new(self.univ_list.clone()),
            Arc::clone(&self.map),
            Arc::clone(&self.op),
            self.arrays[worker_id].clone(),
            self.min,
            self.max,
            self.too_small,
            self.increment,
            report,
            timing,
            Arc::clone(&self.elts_found),
        )
    }
    
    /// Get the computation size.
    pub fn get_computation_size(&self) -> u64 {
        self.computation_size
    }
    
    /// Get the number of parallel workers.
    pub fn get_increment(&self) -> usize {
        self.increment
    }
    
    /// Get whether the computation is too small for parallelization.
    pub fn is_too_small(&self) -> bool {
        self.too_small
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::op::{OperationSymbol, operations};
    use std::collections::HashSet;
    
    #[test]
    fn test_calculate_increment() {
        assert_eq!(SingleClose::calculate_increment(100, 10), 1);
        assert_eq!(SingleClose::calculate_increment(2_000_000, 10), 2);
        assert_eq!(SingleClose::calculate_increment(2_000_000, 3), 1);
    }
    
    #[test]
    fn test_compute_size() {
        // Create a simple operation for testing
        let op_sym = OperationSymbol::new("f", 2, false);
        let table = vec![0, 1, 1, 0]; // XOR operation on {0, 1}
        let op = operations::make_int_operation(op_sym, 2, table).unwrap();
        
        // Create universe list with 2-element IntArrays
        let univ_list = vec![
            IntArray::from_array(vec![0]).unwrap(),
            IntArray::from_array(vec![1]).unwrap(),
        ];
        
        let size = SingleClose::compute_size(&univ_list, &*op, 0, 1).unwrap();
        
        // Size should be (2^2 - 0^2) * 1 = 4
        assert_eq!(size, 4);
    }
    
    #[test]
    fn test_new() {
        let op_sym = OperationSymbol::new("f", 2, false);
        let table = vec![0, 1, 1, 0];
        let op = operations::make_int_operation(op_sym, 2, table).unwrap();
        let arc_op = Arc::from(op);
        
        let univ_list = vec![
            IntArray::from_array(vec![0]).unwrap(),
            IntArray::from_array(vec![1]).unwrap(),
        ];
        
        let map = Arc::new(Mutex::new(HashMap::new()));
        let elts_found = Arc::new(AtomicUsize::new(0));
        
        let sc = SingleClose::new(univ_list, map, arc_op, 0, 1, elts_found);
        assert!(sc.is_ok());
        
        let sc = sc.unwrap();
        assert_eq!(sc.get_increment(), 1); // Too small for parallelization
        assert!(sc.is_too_small());
    }
}


