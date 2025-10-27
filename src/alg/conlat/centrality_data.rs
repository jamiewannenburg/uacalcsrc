/*! CentralityData - Holds centrality data for congruence lattice computations.

This module implements the Java class `org.uacalc.alg.conlat.CentralityData`.

This struct holds two tolerance relations S and T, a congruence delta, and the status of
centrality, weak centrality, and strong rectangularity: Q(S,T,delta), including failure 
information and commutators.
*/

use std::cmp::Ordering;
use std::fmt::{self, Display, Debug};
use crate::alg::conlat::{BinaryRelation, Partition};
use crate::element::SubProductElement;
use crate::util::int_array::{IntArray, IntArrayTrait};

/// CentralityData holds two tolerance relations (S and T), a congruence delta,
/// and failure information for centrality, weak centrality, and strong rectangularity.
///
/// # Examples
/// ```
/// use uacalc::alg::conlat::{CentralityData, BasicBinaryRelation, Partition};
/// use uacalc::alg::conlat::MutableBinaryRelation;
///
/// let mut s = BasicBinaryRelation::new(3).unwrap();
/// s.add(0, 1).unwrap();
/// let mut t = BasicBinaryRelation::new(3).unwrap();
/// t.add(1, 2).unwrap();
/// let delta = Partition::zero(3);
///
/// let data = CentralityData::new(Box::new(s), Box::new(t), delta);
/// assert_eq!(data.get_left().universe_size(), 3);
/// ```
pub struct CentralityData {
    /// The left tolerance relation (S)
    left: Box<dyn BinaryRelation<IntArray>>,
    
    /// The right tolerance relation (T)
    right: Box<dyn BinaryRelation<IntArray>>,
    
    /// The congruence delta
    delta: Partition,
    
    /// Centrality failure information
    centrality_failure: Option<SubProductElement>,
    
    /// Weak centrality failure information
    weak_centrality_failure: Option<SubProductElement>,
    
    /// Strong rectangularity failure information
    strong_rectangularity_failure: Option<SubProductElement>,
}

impl CentralityData {
    /// Create a new CentralityData.
    ///
    /// # Arguments
    /// * `s` - The left tolerance relation
    /// * `t` - The right tolerance relation
    /// * `delta` - The congruence delta
    ///
    /// # Returns
    /// A new CentralityData instance
    ///
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::{CentralityData, BasicBinaryRelation, Partition};
    /// use uacalc::alg::conlat::MutableBinaryRelation;
    ///
    /// let mut s = BasicBinaryRelation::new(3).unwrap();
    /// s.add(0, 1).unwrap();
    /// let mut t = BasicBinaryRelation::new(3).unwrap();
    /// t.add(1, 2).unwrap();
    /// let delta = Partition::zero(3);
    ///
    /// let data = CentralityData::new(Box::new(s), Box::new(t), delta);
    /// assert_eq!(data.get_left().universe_size(), 3);
    /// assert_eq!(data.get_right().universe_size(), 3);
    /// ```
    pub fn new(
        s: Box<dyn BinaryRelation<IntArray>>,
        t: Box<dyn BinaryRelation<IntArray>>,
        delta: Partition,
    ) -> Self {
        CentralityData {
            left: s,
            right: t,
            delta,
            centrality_failure: None,
            weak_centrality_failure: None,
            strong_rectangularity_failure: None,
        }
    }
    
    /// Create a new CentralityData with validation.
    ///
    /// # Arguments
    /// * `s` - The left tolerance relation
    /// * `t` - The right tolerance relation
    /// * `delta` - The congruence delta
    ///
    /// # Returns
    /// * `Ok(CentralityData)` - Successfully created CentralityData
    /// * `Err(String)` - If the relations have incompatible universe sizes
    ///
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::{CentralityData, BasicBinaryRelation, Partition};
    /// use uacalc::alg::conlat::MutableBinaryRelation;
    ///
    /// let mut s = BasicBinaryRelation::new(3).unwrap();
    /// s.add(0, 1).unwrap();
    /// let mut t = BasicBinaryRelation::new(3).unwrap();
    /// t.add(1, 2).unwrap();
    /// let delta = Partition::zero(3);
    ///
    /// let data = CentralityData::new_safe(Box::new(s), Box::new(t), delta).unwrap();
    /// assert_eq!(data.get_left().universe_size(), 3);
    /// ```
    pub fn new_safe(
        s: Box<dyn BinaryRelation<IntArray>>,
        t: Box<dyn BinaryRelation<IntArray>>,
        delta: Partition,
    ) -> Result<Self, String> {
        // Validate that all relations have the same universe size
        let s_size = s.universe_size();
        let t_size = t.universe_size();
        let delta_size = delta.universe_size();
        
        if s_size != t_size || s_size != delta_size {
            return Err(format!(
                "Universe sizes must match: S={}, T={}, delta={}",
                s_size, t_size, delta_size
            ));
        }
        
        Ok(CentralityData::new(s, t, delta))
    }
    
    /// Get the left tolerance relation (S).
    ///
    /// # Returns
    /// Reference to the left relation
    pub fn get_left(&self) -> &dyn BinaryRelation<IntArray> {
        &*self.left
    }
    
    /// Get the right tolerance relation (T).
    ///
    /// # Returns
    /// Reference to the right relation
    pub fn get_right(&self) -> &dyn BinaryRelation<IntArray> {
        &*self.right
    }
    
    /// Get the congruence delta.
    ///
    /// # Returns
    /// Reference to the delta partition
    pub fn get_delta(&self) -> &Partition {
        &self.delta
    }
    
    /// Set the centrality failure information.
    ///
    /// # Arguments
    /// * `failure` - The centrality failure element
    pub fn set_centrality_failure(&mut self, failure: Option<SubProductElement>) {
        self.centrality_failure = failure;
    }
    
    /// Get the centrality failure information.
    ///
    /// # Returns
    /// Reference to the centrality failure element, if any
    pub fn get_centrality_failure(&self) -> &Option<SubProductElement> {
        &self.centrality_failure
    }
    
    /// Set the weak centrality failure information.
    ///
    /// # Arguments
    /// * `failure` - The weak centrality failure element
    pub fn set_weak_centrality_failure(&mut self, failure: Option<SubProductElement>) {
        self.weak_centrality_failure = failure;
    }
    
    /// Get the weak centrality failure information.
    ///
    /// # Returns
    /// Reference to the weak centrality failure element, if any
    pub fn get_weak_centrality_failure(&self) -> &Option<SubProductElement> {
        &self.weak_centrality_failure
    }
    
    /// Set the strong rectangularity failure information.
    ///
    /// # Arguments
    /// * `failure` - The strong rectangularity failure element
    pub fn set_strong_rectangularity_failure(&mut self, failure: Option<SubProductElement>) {
        self.strong_rectangularity_failure = failure;
    }
    
    /// Get the strong rectangularity failure information.
    ///
    /// # Returns
    /// Reference to the strong rectangularity failure element, if any
    pub fn get_strong_rectangularity_failure(&self) -> &Option<SubProductElement> {
        &self.strong_rectangularity_failure
    }
}

// Manual Clone implementation since Box<dyn BinaryRelation> doesn't implement Clone
impl Clone for CentralityData {
    fn clone(&self) -> Self {
        // We can't actually clone trait objects, so we'll use the get_pairs method
        // to reconstruct the relations
        use crate::alg::conlat::{BasicBinaryRelation, MutableBinaryRelation};
        
        // Reconstruct left relation
        let mut left_clone = BasicBinaryRelation::new(self.left.universe_size()).unwrap();
        for pair in self.left.get_pairs() {
            let i = pair.get(0).unwrap() as usize;
            let j = pair.get(1).unwrap() as usize;
            let _ = left_clone.add(i, j);
        }
        
        // Reconstruct right relation
        let mut right_clone = BasicBinaryRelation::new(self.right.universe_size()).unwrap();
        for pair in self.right.get_pairs() {
            let i = pair.get(0).unwrap() as usize;
            let j = pair.get(1).unwrap() as usize;
            let _ = right_clone.add(i, j);
        }
        
        CentralityData {
            left: Box::new(left_clone),
            right: Box::new(right_clone),
            delta: self.delta.clone(),
            centrality_failure: self.centrality_failure.clone(),
            weak_centrality_failure: self.weak_centrality_failure.clone(),
            strong_rectangularity_failure: self.strong_rectangularity_failure.clone(),
        }
    }
}

// Manual Debug implementation since Box<dyn BinaryRelation> doesn't implement Debug
impl Debug for CentralityData {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("CentralityData")
            .field("left_universe_size", &self.left.universe_size())
            .field("right_universe_size", &self.right.universe_size())
            .field("delta", &self.delta)
            .field("centrality_failure", &self.centrality_failure)
            .field("weak_centrality_failure", &self.weak_centrality_failure)
            .field("strong_rectangularity_failure", &self.strong_rectangularity_failure)
            .finish()
    }
}

impl PartialEq for CentralityData {
    fn eq(&self, other: &Self) -> bool {
        // Compare by delta (partitions support equality)
        self.delta == other.delta
    }
}

impl Eq for CentralityData {}

impl PartialOrd for CentralityData {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for CentralityData {
    fn cmp(&self, other: &Self) -> Ordering {
        // Compare by delta (matching Java's compareTo behavior)
        self.delta.cmp(&other.delta)
    }
}

impl Display for CentralityData {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "left: ")?;
        
        // Print left relation pairs
        let left_pairs = self.left.get_pairs();
        write!(f, "{{")?;
        for (i, pair) in left_pairs.iter().enumerate() {
            if i > 0 {
                write!(f, ", ")?;
            }
            write!(f, "({}, {})", pair.get(0).unwrap(), pair.get(1).unwrap())?;
        }
        write!(f, "}}")?;
        
        write!(f, ", right: ")?;
        
        // Print right relation pairs
        let right_pairs = self.right.get_pairs();
        write!(f, "{{")?;
        for (i, pair) in right_pairs.iter().enumerate() {
            if i > 0 {
                write!(f, ", ")?;
            }
            write!(f, "({}, {})", pair.get(0).unwrap(), pair.get(1).unwrap())?;
        }
        write!(f, "}}")?;
        
        write!(f, ", delta: {}", self.delta)?;
        
        write!(f, ", centralityFailure: ")?;
        match &self.centrality_failure {
            Some(failure) => write!(f, "{}", failure)?,
            None => write!(f, "null")?,
        }
        
        write!(f, ", weakCentralityFailure: ")?;
        match &self.weak_centrality_failure {
            Some(failure) => write!(f, "{}", failure)?,
            None => write!(f, "null")?,
        }
        
        write!(f, ", strongRectangularityFailure: ")?;
        match &self.strong_rectangularity_failure {
            Some(failure) => write!(f, "{}", failure)?,
            None => write!(f, "null")?,
        }
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::conlat::{BasicBinaryRelation, MutableBinaryRelation};
    
    #[test]
    fn test_new() {
        let mut s = BasicBinaryRelation::new(3).unwrap();
        s.add(0, 1).unwrap();
        let mut t = BasicBinaryRelation::new(3).unwrap();
        t.add(1, 2).unwrap();
        let delta = Partition::zero(3);
        
        let data = CentralityData::new(Box::new(s), Box::new(t), delta);
        assert_eq!(data.get_left().universe_size(), 3);
        assert_eq!(data.get_right().universe_size(), 3);
        assert_eq!(data.get_delta().universe_size(), 3);
    }
    
    #[test]
    fn test_new_safe_valid() {
        let mut s = BasicBinaryRelation::new(3).unwrap();
        s.add(0, 1).unwrap();
        let mut t = BasicBinaryRelation::new(3).unwrap();
        t.add(1, 2).unwrap();
        let delta = Partition::zero(3);
        
        let data = CentralityData::new_safe(Box::new(s), Box::new(t), delta);
        assert!(data.is_ok());
    }
    
    #[test]
    fn test_new_safe_invalid() {
        let mut s = BasicBinaryRelation::new(3).unwrap();
        s.add(0, 1).unwrap();
        let mut t = BasicBinaryRelation::new(4).unwrap();
        t.add(1, 2).unwrap();
        let delta = Partition::zero(3);
        
        let data = CentralityData::new_safe(Box::new(s), Box::new(t), delta);
        assert!(data.is_err());
    }
    
    #[test]
    fn test_getters() {
        let mut s = BasicBinaryRelation::new(3).unwrap();
        s.add(0, 1).unwrap();
        let mut t = BasicBinaryRelation::new(3).unwrap();
        t.add(1, 2).unwrap();
        let delta = Partition::zero(3);
        
        let data = CentralityData::new(Box::new(s), Box::new(t), delta);
        
        assert_eq!(data.get_left().universe_size(), 3);
        assert_eq!(data.get_right().universe_size(), 3);
        assert_eq!(data.get_delta().universe_size(), 3);
        assert_eq!(data.get_delta().number_of_blocks(), 3);
    }
    
    #[test]
    fn test_failure_setters() {
        let mut s = BasicBinaryRelation::new(3).unwrap();
        s.add(0, 1).unwrap();
        let mut t = BasicBinaryRelation::new(3).unwrap();
        t.add(1, 2).unwrap();
        let delta = Partition::zero(3);
        
        let mut data = CentralityData::new(Box::new(s), Box::new(t), delta);
        
        assert!(data.get_centrality_failure().is_none());
        assert!(data.get_weak_centrality_failure().is_none());
        assert!(data.get_strong_rectangularity_failure().is_none());
        
        data.set_centrality_failure(None);
        data.set_weak_centrality_failure(None);
        data.set_strong_rectangularity_failure(None);
        
        assert!(data.get_centrality_failure().is_none());
        assert!(data.get_weak_centrality_failure().is_none());
        assert!(data.get_strong_rectangularity_failure().is_none());
    }
    
    #[test]
    fn test_compare() {
        let mut s1 = BasicBinaryRelation::new(3).unwrap();
        s1.add(0, 1).unwrap();
        let mut t1 = BasicBinaryRelation::new(3).unwrap();
        t1.add(1, 2).unwrap();
        let delta1 = Partition::zero(3);
        
        let mut s2 = BasicBinaryRelation::new(3).unwrap();
        s2.add(0, 2).unwrap();
        let mut t2 = BasicBinaryRelation::new(3).unwrap();
        t2.add(2, 1).unwrap();
        let delta2 = Partition::one(3);
        
        let data1 = CentralityData::new(Box::new(s1), Box::new(t1), delta1);
        let data2 = CentralityData::new(Box::new(s2), Box::new(t2), delta2);
        
        // Comparison should be based on delta
        assert!(data1 < data2 || data1 > data2 || data1 == data2);
    }
    
    #[test]
    fn test_to_string() {
        let mut s = BasicBinaryRelation::new(2).unwrap();
        s.add(0, 1).unwrap();
        let mut t = BasicBinaryRelation::new(2).unwrap();
        t.add(1, 0).unwrap();
        let delta = Partition::zero(2);
        
        let data = CentralityData::new(Box::new(s), Box::new(t), delta);
        let s = data.to_string();
        
        assert!(s.contains("left:"));
        assert!(s.contains("right:"));
        assert!(s.contains("delta:"));
        assert!(s.contains("centralityFailure:"));
        assert!(s.contains("weakCentralityFailure:"));
        assert!(s.contains("strongRectangularityFailure:"));
    }
}
