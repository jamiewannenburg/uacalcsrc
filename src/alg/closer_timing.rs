/*!
 * Timing information holder for closure operations.
 * 
 * This module provides timing and progress tracking for closure operations,
 * replacing the UI-dependent `org.uacalc.alg.CloserTiming` from the Java implementation.
 */

use std::sync::Arc;
use std::sync::atomic::{AtomicI32, AtomicI64, Ordering};
use std::time::Instant;
use crate::progress::ProgressReport;
use crate::alg::BigProductAlgebra;

/// Timing information holder for closure operations.
/// 
/// This struct holds timing data for UI progress reporting during closure operations.
/// It uses atomic types for thread safety in parallel closure algorithms.
/// 
/// # Thread Safety
/// This struct uses `AtomicI32` and `AtomicI64` for thread-safe counters,
/// but full thread safety may require additional synchronization.
pub struct CloserTiming {
    /// The progress reporter (optional)
    report: Option<Arc<dyn ProgressReport>>,
    
    /// Number of factors in the product algebra
    projs: u64,
    
    /// Current pass number
    pass: u32,
    
    /// Next pass size (thread-safe)
    next_pass_size: Arc<AtomicI32>,
    
    /// Current pass size
    curr_pass_size: u32,
    
    /// Previous pass size
    last_pass_size: u32,
    
    /// Operation arities
    arities: Vec<i32>,
    
    /// Applications needed for this pass
    apps_needed: u64,
    
    /// Applications completed this pass
    apps_this_pass: u64,
    
    /// Local applications counter (thread-safe)
    local_apps: Arc<AtomicI64>,
    
    /// Pass start time
    pass_start_time: Option<Instant>,
    
    /// Milliseconds per application
    ms_per_app: f64,
    
    /// Whether to update time estimates
    update_time: bool,
    
    /// Whether at beginning of pass
    at_beginning: bool,
    
    /// Start time for calculations
    start_nano_time: Option<Instant>,
    
    /// Real initialization count
    real_init_count: u64,
}

// Constants for timing thresholds
const INIT_COUNT: u64 = 20_000_000;   // Should be less than 2 seconds
const SECOND_COUNT: u64 = 60_000_000;
const THIRD_COUNT: u64 = 60_000_000;

impl CloserTiming {
    /// Create a new CloserTiming instance from a BigProductAlgebra.
    /// 
    /// This constructor extracts the number of factors and operation arities
    /// from the provided algebra, matching the Java implementation.
    /// 
    /// # Arguments
    /// * `algebra` - The BigProductAlgebra to get timing information for
    /// * `report` - Optional progress reporter
    /// 
    /// # Returns
    /// A new CloserTiming instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{CloserTiming, BigProductAlgebra, BasicSmallAlgebra};
    /// use uacalc::progress::factory;
    /// use std::collections::HashSet;
    /// 
    /// let alg1 = Box::new(BasicSmallAlgebra::new(
    ///     "A1".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn uacalc::alg::SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let product = BigProductAlgebra::<i32>::new_safe(vec![alg1]).unwrap();
    /// let timing = CloserTiming::new_from_algebra(&product, Some(factory::console()));
    /// ```
    pub fn new_from_algebra<T>(
        algebra: &BigProductAlgebra<T>,
        report: Option<Arc<dyn ProgressReport>>,
    ) -> Self
    where
        T: Clone + std::cmp::PartialEq + Eq + std::hash::Hash + std::fmt::Debug + Send + Sync + 'static,
    {
        let projs = algebra.get_number_of_factors() as u64;
        let ops = algebra.operations_ref_arc();
        let mut arities = Vec::with_capacity(ops.len());
        
        for op in ops {
            arities.push(op.arity());
        }
        
        CloserTiming {
            report,
            projs,
            pass: 0,
            next_pass_size: Arc::new(AtomicI32::new(0)),
            curr_pass_size: 0,
            last_pass_size: 0,
            arities,
            apps_needed: 0,
            apps_this_pass: 0,
            local_apps: Arc::new(AtomicI64::new(0)),
            pass_start_time: None,
            ms_per_app: 0.0,
            update_time: true,
            at_beginning: true,
            start_nano_time: None,
            real_init_count: 0,
        }
    }
    
    /// Create a new CloserTiming instance.
    /// 
    /// This is a simplified constructor that takes arities and number of factors
    /// directly, instead of deriving them from a BigProductAlgebra.
    /// This is kept for backward compatibility and testing purposes.
    /// 
    /// # Arguments
    /// * `arities` - The arities of operations in the algebra
    /// * `num_factors` - The number of factors in the product algebra
    /// * `report` - Optional progress reporter
    /// 
    /// # Returns
    /// A new CloserTiming instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::CloserTiming;
    /// use uacalc::progress::factory;
    /// 
    /// let arities = vec![2, 2, 1]; // binary ops and one unary
    /// let timing = CloserTiming::new(arities, 3, Some(factory::console()));
    /// ```
    pub fn new(
        arities: Vec<i32>,
        num_factors: u64,
        report: Option<Arc<dyn ProgressReport>>,
    ) -> Self {
        CloserTiming {
            report,
            projs: num_factors,
            pass: 0,
            next_pass_size: Arc::new(AtomicI32::new(0)),
            curr_pass_size: 0,
            last_pass_size: 0,
            arities,
            apps_needed: 0,
            apps_this_pass: 0,
            local_apps: Arc::new(AtomicI64::new(0)),
            pass_start_time: None,
            ms_per_app: 0.0,
            update_time: true,
            at_beginning: true,
            start_nano_time: None,
            real_init_count: 0,
        }
    }
    
    /// Update the pass information and reset counters.
    /// 
    /// # Arguments
    /// * `size` - The size of the current pass
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::CloserTiming;
    /// 
    /// let arities = vec![2, 2];
    /// let mut timing = CloserTiming::new(arities, 2, None);
    /// timing.update_pass(10);
    /// ```
    pub fn update_pass(&mut self, size: u32) {
        self.next_pass_size.store(0, Ordering::SeqCst);
        self.apps_this_pass = 0;
        self.update_time = true;
        self.at_beginning = true;
        
        self.last_pass_size = self.curr_pass_size;
        self.curr_pass_size = size;
        self.pass += 1;
        
        self.apps_needed = self.count_func_applications(self.last_pass_size, self.curr_pass_size);
        
        if let Some(ref report) = self.report {
            report.set_time_next("");
        }
    }
    
    /// Increment application counters and update timing estimates.
    /// 
    /// This method is called after each operation application to update
    /// progress and time estimates.
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::CloserTiming;
    /// 
    /// let arities = vec![2];
    /// let mut timing = CloserTiming::new(arities, 2, None);
    /// timing.update_pass(10);
    /// 
    /// // Simulate operation applications
    /// for _ in 0..100 {
    ///     timing.increment_apps();
    /// }
    /// ```
    pub fn increment_apps(&mut self) {
        self.apps_this_pass += self.projs;
        self.local_apps.fetch_add(self.projs as i64, Ordering::SeqCst);
        
        if self.at_beginning && self.apps_this_pass > INIT_COUNT {
            self.at_beginning = false;
            self.real_init_count = self.apps_this_pass;
            self.start_nano_time = Some(Instant::now());
        } else if self.update_time && self.apps_this_pass > SECOND_COUNT {
            self.local_apps.store(0, Ordering::SeqCst);
            self.update_time = false;
            
            if let Some(start_time) = self.start_nano_time {
                let elapsed_ms = start_time.elapsed().as_millis() as f64;
                self.ms_per_app = elapsed_ms / (self.apps_this_pass - self.real_init_count) as f64;
                
                let time_left = ((self.apps_needed - self.apps_this_pass) as f64 * self.ms_per_app) as u64;
                let time_str = Self::ms_to_string(time_left);
                
                if let Some(ref report) = self.report {
                    report.set_time_left(&time_str);
                }
                
                println!("{}", time_str);
                println!("msPerApp = {}", self.ms_per_app);
                println!("funcAppsNeeded: {}", self.apps_needed);
                println!("appsSoFar: {}", self.apps_this_pass);
            }
        } else if self.local_apps.load(Ordering::SeqCst) as u64 > THIRD_COUNT {
            self.local_apps.store(0, Ordering::SeqCst);
            
            if let Some(start_time) = self.start_nano_time {
                let elapsed_ms = start_time.elapsed().as_millis() as f64;
                self.ms_per_app = elapsed_ms / (self.apps_this_pass - self.real_init_count) as f64;
                
                let time_left = ((self.apps_needed - self.apps_this_pass) as f64 * self.ms_per_app) as u64;
                let time_str = Self::ms_to_string(time_left);
                
                if let Some(ref report) = self.report {
                    report.set_time_left(&time_str);
                }
                
                let next_size = self.next_pass_size.load(Ordering::SeqCst) as u32;
                let next_apps = self.count_func_applications(
                    self.curr_pass_size,
                    next_size + self.curr_pass_size
                );
                let time_next = (next_apps as f64 * self.ms_per_app) as u64;
                let time_next_str = Self::ms_to_string(time_next);
                
                if let Some(ref report) = self.report {
                    report.set_time_next(&time_next_str);
                }
            }
        }
    }
    
    /// Increment the next pass size counter.
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::CloserTiming;
    /// 
    /// let arities = vec![2];
    /// let mut timing = CloserTiming::new(arities, 2, None);
    /// timing.increment_next_pass_size();
    /// ```
    pub fn increment_next_pass_size(&self) {
        self.next_pass_size.fetch_add(1, Ordering::SeqCst);
    }
    
    /// Count the number of function applications needed.
    /// 
    /// This calculates the number of function applications required
    /// for a pass from size0 to size1.
    /// 
    /// # Arguments
    /// * `size0` - Starting size
    /// * `size1` - Ending size
    /// 
    /// # Returns
    /// The number of function applications needed (or u64::MAX if too large)
    fn count_func_applications(&self, size0: u32, size1: u32) -> u64 {
        let mut ans: u128 = 0;
        let s0 = size0 as u128;
        let s1 = size1 as u128;
        
        for &arity in &self.arities {
            let r = arity as u32;
            // Calculate s1^r - s0^r
            let s1_pow = s1.pow(r);
            let s0_pow = s0.pow(r);
            ans += s1_pow - s0_pow;
        }
        
        // Check if result fits in u64
        if ans > u64::MAX as u128 {
            return u64::MAX;
        }
        
        (ans as u64) * self.projs
    }
    
    /// Convert milliseconds to a formatted time string.
    /// 
    /// Formats time as "H:MM:SS" or "M:SS" or just "S" depending on magnitude.
    /// 
    /// # Arguments
    /// * `ms` - Time in milliseconds
    /// 
    /// # Returns
    /// Formatted time string
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::CloserTiming;
    /// 
    /// assert_eq!(CloserTiming::ms_to_string(5000), "5");
    /// assert_eq!(CloserTiming::ms_to_string(65000), "1:05");
    /// assert_eq!(CloserTiming::ms_to_string(3665000), "1:01:05");
    /// ```
    pub fn ms_to_string(ms: u64) -> String {
        let tot_secs = ms / 1000;
        let secs = tot_secs % 60;
        let tot_mins = tot_secs / 60;
        let mins = tot_mins % 60;
        let hrs = tot_mins / 60;
        
        let secs_string = if secs < 10 {
            format!("0{}", secs)
        } else {
            secs.to_string()
        };
        
        if hrs == 0 {
            if mins == 0 {
                return secs.to_string();
            }
            return format!("{}:{}", mins, secs_string);
        }
        
        let mins_string = if mins < 10 {
            format!("0{}", mins)
        } else {
            mins.to_string()
        };
        
        format!("{}:{}:{}", hrs, mins_string, secs_string)
    }
    
    /// Get the current pass number.
    /// 
    /// # Returns
    /// The current pass number
    pub fn get_pass(&self) -> u32 {
        self.pass
    }
    
    /// Get the number of factors.
    /// 
    /// # Returns
    /// The number of factors in the product algebra
    pub fn get_num_factors(&self) -> u64 {
        self.projs
    }
    
    /// Get the operation arities.
    /// 
    /// # Returns
    /// A reference to the operation arities
    pub fn get_arities(&self) -> &[i32] {
        &self.arities
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::progress::factory;
    
    #[test]
    fn test_ms_to_string() {
        assert_eq!(CloserTiming::ms_to_string(5000), "5");
        assert_eq!(CloserTiming::ms_to_string(65000), "1:05");
        assert_eq!(CloserTiming::ms_to_string(3665000), "1:01:05");
        assert_eq!(CloserTiming::ms_to_string(125000), "2:05");
    }
    
    #[test]
    fn test_new() {
        let arities = vec![2, 2, 1];
        let timing = CloserTiming::new(arities.clone(), 3, None);
        
        assert_eq!(timing.get_pass(), 0);
        assert_eq!(timing.get_num_factors(), 3);
        assert_eq!(timing.get_arities(), &arities);
    }
    
    #[test]
    fn test_update_pass() {
        let arities = vec![2, 2];
        let mut timing = CloserTiming::new(arities, 2, None);
        
        timing.update_pass(10);
        assert_eq!(timing.get_pass(), 1);
        assert_eq!(timing.curr_pass_size, 10);
        assert_eq!(timing.last_pass_size, 0);
        
        timing.update_pass(20);
        assert_eq!(timing.get_pass(), 2);
        assert_eq!(timing.curr_pass_size, 20);
        assert_eq!(timing.last_pass_size, 10);
    }
    
    #[test]
    fn test_increment_apps() {
        let arities = vec![2];
        let mut timing = CloserTiming::new(arities, 2, None);
        timing.update_pass(10);
        
        let initial_apps = timing.apps_this_pass;
        timing.increment_apps();
        assert_eq!(timing.apps_this_pass, initial_apps + 2); // projs = 2
    }
    
    #[test]
    fn test_increment_next_pass_size() {
        let arities = vec![2];
        let timing = CloserTiming::new(arities, 2, None);
        
        assert_eq!(timing.next_pass_size.load(Ordering::SeqCst), 0);
        timing.increment_next_pass_size();
        assert_eq!(timing.next_pass_size.load(Ordering::SeqCst), 1);
        timing.increment_next_pass_size();
        assert_eq!(timing.next_pass_size.load(Ordering::SeqCst), 2);
    }
    
    #[test]
    fn test_with_progress_report() {
        let arities = vec![2, 2];
        let report = factory::no_op();
        let mut timing = CloserTiming::new(arities, 3, Some(report));
        
        timing.update_pass(5);
        timing.increment_apps();
        // Should not panic with progress report
    }
    
    #[test]
    fn test_new_from_algebra() {
        use crate::alg::{BigProductAlgebra, BasicSmallAlgebra};
        use std::collections::HashSet;
        
        let alg1 = Box::new(BasicSmallAlgebra::new(
            "A1".to_string(),
            HashSet::from([0, 1]),
            Vec::new()
        )) as Box<dyn crate::alg::SmallAlgebra<UniverseItem = i32>>;
        
        let alg2 = Box::new(BasicSmallAlgebra::new(
            "A2".to_string(),
            HashSet::from([0, 1]),
            Vec::new()
        )) as Box<dyn crate::alg::SmallAlgebra<UniverseItem = i32>>;
        
        let product = BigProductAlgebra::<i32>::new_safe(vec![alg1, alg2]).unwrap();
        let timing = CloserTiming::new_from_algebra(&product, None);
        
        assert_eq!(timing.get_pass(), 0);
        assert_eq!(timing.get_num_factors(), 2);
        // Operations may be empty for BasicSmallAlgebra, so we just check it doesn't panic
    }
}

