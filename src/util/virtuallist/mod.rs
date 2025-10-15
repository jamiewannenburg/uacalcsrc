use std::hash::{Hash, Hasher};

/// A trait for lists indexed by `i64` rather than `usize`.
/// These have no backing structure; so they are virtual lists.
/// They are immutable so they only need a `get` and `size` method.
/// 
/// An example would be all triples of elements of a list with
/// elements of type E. A triple could be an array `Vec<E>` or a list of length 3.
/// If the list had `n` elements then the LongList would have size `n^3`.
/// The main subtlety is defining `get` which defines a function from i64's
/// less than `n^3` to triples and should be stateless, or at least thread safe,
/// so that it behaves well with parallel processing.
pub trait LongList<E>: Send + Sync {
    /// Get the kth element.
    /// 
    /// # Arguments
    /// * `k` - the index
    /// 
    /// # Returns
    /// The element at index k
    fn get(&self, k: i64) -> E;
    
    /// Get the size of the list.
    /// 
    /// # Returns
    /// The number of elements in the list
    fn size(&self) -> i64;
}

/// A LongList of int arrays of length `tuple_length` with entries between 0
/// and `base` - 1, inclusive. The kth entry is k written in base `base`.
pub struct IntTuples {
    pub tuple_length: usize,
    pub base: usize,
    pub size: i64,
}

impl IntTuples {
    /// Create a new IntTuples LongList.
    /// 
    /// # Arguments
    /// * `tuple_length` - The length of each tuple
    /// * `base` - The base for the numbering system
    /// 
    /// # Returns
    /// * `Ok(IntTuples)` - Successfully created
    /// * `Err(String)` - If arguments are invalid or result is too large
    pub fn new_safe(tuple_length: usize, base: usize) -> Result<Self, String> {
        if tuple_length == 0 && base == 0 {
            return Err("Both tuple_length and base cannot be 0".to_string());
        }
        
        // Calculate size = base^tuple_length
        let mut size = 1i64;
        for _ in 0..tuple_length {
            if let Some(new_size) = size.checked_mul(base as i64) {
                size = new_size;
            } else {
                return Err(format!("{}^{} is too big to be a long", base, tuple_length));
            }
        }
        
        Ok(IntTuples {
            tuple_length,
            base,
            size,
        })
    }
    
    /// Create a new IntTuples LongList (panic version for compatibility).
    pub fn new(tuple_length: usize, base: usize) -> Self {
        Self::new_safe(tuple_length, base).unwrap()
    }
}

impl LongList<Vec<i32>> for IntTuples {
    fn get(&self, k: i64) -> Vec<i32> {
        let mut ans = vec![0; self.tuple_length];
        let mut k = k;
        for i in 0..self.tuple_length {
            ans[i] = (k % self.base as i64) as i32;
            k = k / self.base as i64;
        }
        ans
    }
    
    fn size(&self) -> i64 {
        self.size
    }
}

/// A LongList of int arrays of length `tuple_length` with entries between 0
/// and `base` - 1, inclusive, and having at least one entry in the range `min` to
/// `base` - 1.
pub struct IntTuplesWithMin {
    pub tuple_length: usize,
    pub base: usize,
    pub min: usize,
    pub size: i64,
    partial_sums: Vec<i64>,
}

impl IntTuplesWithMin {
    /// Create a new IntTuplesWithMin LongList.
    /// 
    /// # Arguments
    /// * `tuple_length` - The length of each tuple
    /// * `base` - The base for the numbering system
    /// * `min` - The minimum value for at least one entry
    /// 
    /// # Returns
    /// * `Ok(IntTuplesWithMin)` - Successfully created
    /// * `Err(String)` - If arguments are invalid or result is too large
    pub fn new_safe(tuple_length: usize, base: usize, min: usize) -> Result<Self, String> {
        if base <= min {
            return Err("base must be greater than min".to_string());
        }
        
        // Calculate size = base^tuple_length - min^tuple_length
        let base_pow = base.pow(tuple_length as u32);
        let min_pow = min.pow(tuple_length as u32);
        
        if base_pow > i64::MAX as usize || min_pow > i64::MAX as usize {
            return Err(format!("{}^{} or {}^{} is too big to be a long", base, tuple_length, min, tuple_length));
        }
        
        let size = (base_pow - min_pow) as i64;
        let diff = base - min;
        
        // Calculate partial sums
        let mut partial_sums = vec![0i64; tuple_length];
        let mut summand = diff as i64;
        for i in 1..tuple_length {
            summand = summand.saturating_mul(min as i64);
        }
        partial_sums[0] = summand;
        
        for i in 1..tuple_length {
            summand = (summand.saturating_mul(base as i64)) / (min as i64);
            partial_sums[i] = partial_sums[i-1].saturating_add(summand);
        }
        
        Ok(IntTuplesWithMin {
            tuple_length,
            base,
            min,
            size,
            partial_sums,
        })
    }
    
    /// Create a new IntTuplesWithMin LongList (panic version for compatibility).
    pub fn new(tuple_length: usize, base: usize, min: usize) -> Self {
        Self::new_safe(tuple_length, base, min).unwrap()
    }
}

impl LongList<Vec<i32>> for IntTuplesWithMin {
    fn get(&self, k: i64) -> Vec<i32> {
        let mut k = k;
        let mut stage = 0;
        
        // Find the stage
        while stage < self.partial_sums.len() && k >= self.partial_sums[stage] {
            stage += 1;
        }
        
        if stage > 0 {
            k = k - self.partial_sums[stage - 1];
        }
        
        let mut ans = vec![0; self.tuple_length];
        let diff = self.base - self.min;
        
        // Fill the first stage positions
        for i in 0..stage {
            ans[i] = (k % self.base as i64) as i32;
            k = k / self.base as i64;
        }
        
        // Fill the stage position with min constraint
        if stage < self.tuple_length {
            ans[stage] = (self.min as i64 + (k % diff as i64)) as i32;
            k = k / diff as i64;
        }
        
        // Fill the remaining positions
        for i in (stage + 1)..self.tuple_length {
            ans[i] = (k % self.min as i64) as i32;
            k = k / self.min as i64;
        }
        
        ans
    }
    
    fn size(&self) -> i64 {
        self.size
    }
}

/// A LongList of int[]'s representing all subsets of size `subset_size` from
/// the set of nonnegative integers less than `set_size`.
pub struct FixedSizedSubsets {
    pub subset_size: usize,
    pub set_size: usize,
    pub size: i64,
}

impl FixedSizedSubsets {
    /// Create a new FixedSizedSubsets LongList.
    /// 
    /// # Arguments
    /// * `subset_size` - The size of each subset
    /// * `set_size` - The size of the set to choose from
    /// 
    /// # Returns
    /// * `Ok(FixedSizedSubsets)` - Successfully created
    /// * `Err(String)` - If arguments are invalid or result is too large
    pub fn new_safe(subset_size: usize, set_size: usize) -> Result<Self, String> {
        if subset_size > set_size {
            return Err("subset_size must be <= set_size".to_string());
        }
        
        // Calculate binomial coefficient: C(set_size, subset_size)
        let size = Self::binomial(set_size, subset_size);
        if size > i64::MAX {
            return Err("There are too many subsets to be a long".to_string());
        }
        
        Ok(FixedSizedSubsets {
            subset_size,
            set_size,
            size,
        })
    }
    
    /// Create a new FixedSizedSubsets LongList (panic version for compatibility).
    pub fn new(subset_size: usize, set_size: usize) -> Self {
        Self::new_safe(subset_size, set_size).unwrap()
    }
    
    /// Calculate binomial coefficient C(n, r)
    fn binomial(n: usize, r: usize) -> i64 {
        if r > n {
            return 0;
        }
        let r = r.min(n - r); // Use symmetry
        let mut result = 1i64;
        for i in 0..r {
            result = result.saturating_mul((n - i) as i64) / ((i + 1) as i64);
        }
        result
    }
    
    /// Find the largest t such that C(t, r) <= k < C(t+1, r)
    fn set_last_entry(&self, k: i64, r: usize, arr: &mut Vec<i32>) -> i64 {
        let one_over_r = 1.0 / (r as f64);
        let mut guess = (Self::factorial(r) as f64 * k as f64).powf(one_over_r) as i32 + (r / 2) as i32;
        
        if k == 0 {
            guess = (r - 1) as i32;
        }
        
        // Binary search for the correct t
        let mut low = 0i32;
        let mut high = guess.max(r as i32);
        
        while low <= high {
            let mid = (low + high) / 2;
            let binom = Self::binomial(mid as usize, r);
            if binom <= k {
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
        
        let t = high;
        arr[r - 1] = t;
        k - Self::binomial(t as usize, r)
    }
    
    /// Calculate factorial of n
    fn factorial(n: usize) -> i64 {
        if n < 2 {
            return 1;
        }
        let mut result = 1i64;
        for i in 2..=n {
            result = result.saturating_mul(i as i64);
        }
        result
    }
}

impl LongList<Vec<i32>> for FixedSizedSubsets {
    fn get(&self, k: i64) -> Vec<i32> {
        let mut ans = vec![0; self.subset_size];
        let mut left_over = k;
        
        for r in (1..=self.subset_size).rev() {
            left_over = self.set_last_entry(left_over, r, &mut ans);
        }
        
        ans
    }
    
    fn size(&self) -> i64 {
        self.size
    }
}

/// A LongList of all subsets of the set of int 0 to set_size - 1,
/// represented as increasing int arrays.
pub struct Subsets {
    pub set_size: usize,
    pub size: i64,
}

impl Subsets {
    /// Create a new Subsets LongList.
    /// 
    /// # Arguments
    /// * `set_size` - The size of the set
    /// 
    /// # Returns
    /// * `Ok(Subsets)` - Successfully created
    /// * `Err(String)` - If arguments are invalid or result is too large
    pub fn new_safe(set_size: usize) -> Result<Self, String> {
        if set_size >= 63 {
            return Err("There are too many subsets to be a long. set_size should be at most 63".to_string());
        }
        
        let size = 1i64 << set_size; // 2^set_size
        
        Ok(Subsets {
            set_size,
            size,
        })
    }
    
    /// Create a new Subsets LongList (panic version for compatibility).
    pub fn new(set_size: usize) -> Self {
        Self::new_safe(set_size).unwrap()
    }
    
    /// Calculate 2^r
    fn pow2(r: usize) -> i64 {
        1i64 << r
    }
    
    /// Calculate log2 of k
    fn log2(k: i64) -> usize {
        if k <= 0 {
            panic!("k must be positive");
        }
        63 - k.leading_zeros() as usize
    }
}

impl LongList<Vec<i32>> for Subsets {
    fn get(&self, k: i64) -> Vec<i32> {
        if k == 0 {
            return vec![];
        }
        
        let mut result = Vec::new();
        let mut k = k;
        
        while k > 0 {
            let t = Self::log2(k);
            result.push(t as i32);
            k = k - Self::pow2(t);
        }
        
        result.reverse();
        result
    }
    
    fn size(&self) -> i64 {
        self.size
    }
}

/// A LongList of all permutations of n elements.
pub struct Permutations {
    pub n: usize,
    pub size: i64,
    factorials: Vec<i64>,
}

impl Permutations {
    /// Create a new Permutations LongList.
    /// 
    /// # Arguments
    /// * `n` - The number of elements to permute
    /// 
    /// # Returns
    /// * `Ok(Permutations)` - Successfully created
    /// * `Err(String)` - If arguments are invalid or result is too large
    pub fn new_safe(n: usize) -> Result<Self, String> {
        if n > 20 {
            return Err("There are too many permutations to be a long. n should be at most 20".to_string());
        }
        
        let size = Self::factorial(n);
        let mut factorials = vec![0i64; 21];
        for i in 0..21 {
            factorials[i] = Self::factorial(i);
        }
        
        Ok(Permutations {
            n,
            size,
            factorials,
        })
    }
    
    /// Create a new Permutations LongList (panic version for compatibility).
    pub fn new(n: usize) -> Self {
        Self::new_safe(n).unwrap()
    }
    
    /// Calculate factorial of n
    fn factorial(n: usize) -> i64 {
        if n < 2 {
            return 1;
        }
        let mut result = 1i64;
        for i in 2..=n {
            result = result.saturating_mul(i as i64);
        }
        result
    }
    
    /// Set the entry at the given index
    fn set_entry(&self, index: usize, k: i64, arr: &mut Vec<i32>, lst: &mut Vec<i32>) -> i64 {
        let m = lst.len();
        let m_fac = self.factorials[m - 1];
        let mut r = 0;
        
        while k >= (r + 1) * m_fac {
            r += 1;
        }
        
        arr[index] = lst[r as usize];
        lst.remove(r as usize);
        k - r * m_fac
    }
}

impl LongList<Vec<i32>> for Permutations {
    fn get(&self, k: i64) -> Vec<i32> {
        let mut lst: Vec<i32> = (0..self.n as i32).collect();
        let mut ans = vec![0; self.n];
        let mut k = k;
        
        for i in 0..self.n {
            k = self.set_entry(i, k, &mut ans, &mut lst);
        }
        
        ans
    }
    
    fn size(&self) -> i64 {
        self.size
    }
}

/// A concrete implementation of LongList for tuples with minimum values.
/// This is a direct translation of the Java TupleWithMin class.
pub struct TupleWithMin {
    pub array_len: i32,
    pub size: i32,
    pub min: i32,
    pub diff: i32,
    pub partial_sums: Vec<i64>,
}

impl TupleWithMin {
    /// Create a new TupleWithMin.
    /// 
    /// # Arguments
    /// * `array_len` - The length of each tuple array
    /// * `base` - The base for the numbering system
    /// * `min` - The minimum value for at least one entry
    /// 
    /// # Returns
    /// * `Ok(TupleWithMin)` - Successfully created
    /// * `Err(String)` - If arguments are invalid
    /// 
    /// # Examples
    /// ```
    /// use uacalc::util::virtuallist::{TupleWithMin, LongList};
    /// let tuples = TupleWithMin::new_safe(3, 4, 2).unwrap();
    /// assert_eq!(tuples.size(), 56);
    /// ```
    pub fn new_safe(array_len: i32, base: i32, min: i32) -> Result<Self, String> {
        if array_len < 0 {
            return Err("array_len must be non-negative".to_string());
        }
        if base < 0 {
            return Err("base must be non-negative".to_string());
        }
        if min < 0 {
            return Err("min must be non-negative".to_string());
        }
        if base <= min {
            return Err("base must be greater than min".to_string());
        }
        
        let diff = base - min;
        let mut partial_sums = vec![0i64; array_len as usize];
        
        // Calculate initial summand = diff * (min^(array_len-1))
        let mut summand = diff as i64;
        for _ in 1..array_len {
            summand = summand.saturating_mul(min as i64);
        }
        
        partial_sums[0] = summand;
        
        // Calculate remaining partial sums
        for i in 1..array_len as usize {
            summand = (summand.saturating_mul(base as i64)) / (min as i64);
            partial_sums[i] = partial_sums[i-1].saturating_add(summand);
        }
        
        Ok(TupleWithMin {
            array_len,
            size: base,
            min,
            diff,
            partial_sums,
        })
    }
    
    /// Create a new TupleWithMin (panic version for compatibility).
    /// 
    /// # Panics
    /// Panics if arguments are invalid.
    pub fn new(array_len: i32, base: i32, min: i32) -> Self {
        Self::new_safe(array_len, base, min).unwrap()
    }
}

impl LongList<Vec<i32>> for TupleWithMin {
    fn get(&self, k: i64) -> Vec<i32> {
        let mut k = k;
        let mut stage = 0;
        
        // Find the stage
        while stage < self.partial_sums.len() && k >= self.partial_sums[stage] {
            stage += 1;
        }
        
        if stage > 0 {
            k = k - self.partial_sums[stage - 1];
        }
        
        let mut ans = vec![0; self.array_len as usize];
        
        // Fill the first stage positions
        for i in 0..stage {
            ans[i] = (k % self.size as i64) as i32;
            k = k / self.size as i64;
        }
        
        // Fill the stage position with min constraint
        ans[stage] = self.min + (k % self.diff as i64) as i32;
        k = k / self.diff as i64;
        
        // Fill the remaining positions
        for i in (stage + 1)..self.array_len as usize {
            ans[i] = (k % self.min as i64) as i32;
            k = k / self.min as i64;
        }
        
        ans
    }
    
    fn size(&self) -> i64 {
        self.partial_sums[self.array_len as usize - 1]
    }
}

/// Utility functions for LongList operations
pub struct LongListUtils;

impl LongListUtils {
    /// Calculate factorial of n
    pub fn factorial(n: usize) -> i64 {
        if n < 2 {
            return 1;
        }
        let mut result = 1i64;
        for i in 2..=n {
            result = result.saturating_mul(i as i64);
        }
        result
    }
    
    /// Calculate binomial coefficient C(n, r)
    pub fn binomial(n: usize, r: usize) -> i64 {
        if r > n {
            return 0;
        }
        let r = r.min(n - r); // Use symmetry
        let mut result = 1i64;
        for i in 0..r {
            result = result.saturating_mul((n - i) as i64) / ((i + 1) as i64);
        }
        result
    }
    
    /// Calculate log2 of k
    pub fn log2(k: i64) -> usize {
        if k <= 0 {
            panic!("k must be positive");
        }
        63 - k.leading_zeros() as usize
    }
    
    /// Calculate 2^r
    pub fn pow2(r: usize) -> i64 {
        1i64 << r
    }
}

// Implement common traits for all LongList implementations
impl<E> PartialEq for dyn LongList<E> where E: PartialEq {
    fn eq(&self, other: &Self) -> bool {
        if self.size() != other.size() {
            return false;
        }
        for i in 0..self.size() {
            if self.get(i) != other.get(i) {
                return false;
            }
        }
        true
    }
}

impl<E> Eq for dyn LongList<E> where E: Eq {}

impl<E> Hash for dyn LongList<E> where E: Hash {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.size().hash(state);
        // Hash first few elements for efficiency
        for i in 0..self.size().min(10) {
            self.get(i).hash(state);
        }
    }
}

impl<E> std::fmt::Display for dyn LongList<E> where E: std::fmt::Display {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "LongList(size={})", self.size())
    }
}

impl<E> std::fmt::Debug for dyn LongList<E> where E: std::fmt::Debug {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "LongList(size={})", self.size())
    }
}
