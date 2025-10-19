/*! Polymorphisms calculation for collections of partitions.

This module implements the calculation of polymorphisms for a collection of partitions
on a finite set. A polymorphism is a function that preserves the structure defined
by the partitions.

The implementation is based on the Java class `org.uacalc.alg.conlat.Polymorphisms`.
*/

use std::collections::HashMap;
use std::fmt;
use crate::alg::conlat::partition::Partition;
use crate::alg::op::Operation;
use crate::util::int_array::IntArray;

/// A structure for calculating polymorphisms of a collection of partitions.
/// 
/// Given a collection of partitions on a set, this calculates the polymorphisms
/// of the collection. A polymorphism is a function that preserves the structure
/// defined by the partitions.
/// 
/// This struct corresponds to the Java class `org.uacalc.alg.conlat.Polymorphisms`.
#[derive(Debug)]
pub struct Polymorphisms {
    /// The collection of partitions
    pub pars: Vec<Partition>,
    /// The size of the underlying algebra
    pub alg_size: usize,
    /// The arity of the polymorphisms to calculate
    pub arity: usize,
    /// Whether to only consider idempotent polymorphisms
    pub idempotent: bool,
    /// Fixed values for the polymorphisms (if any)
    pub fixed_values: Option<Vec<i32>>,
    /// Partial operation (if any)
    pub partial_op: Option<Box<dyn Operation>>,
    /// Partial operation table (if any)
    pub partial_op_table: Option<Vec<i32>>,
    /// The size of the operation table
    pub table_size: usize,
    /// Graph structure for polymorphism calculations
    pub graph: Option<HashMap<IntArray, HashMap<IntArray, Partition>>>,
}

impl Polymorphisms {
    /// Create a new Polymorphisms instance with proper error handling.
    /// 
    /// # Arguments
    /// * `arity` - The arity of the polymorphisms to calculate
    /// * `pars` - The collection of partitions
    /// * `idempotent` - Whether to only consider idempotent polymorphisms
    /// * `fixed_values` - Fixed values for the polymorphisms (optional)
    /// 
    /// # Returns
    /// * `Ok(Polymorphisms)` - Successfully created instance
    /// * `Err(String)` - Error message if validation fails
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::polymorphisms::Polymorphisms;
    /// use uacalc::alg::conlat::partition::Partition;
    /// 
    /// let pars = vec![Partition::zero(3), Partition::one(3)];
    /// let poly = Polymorphisms::new_safe(1, pars, false, None).unwrap();
    /// assert_eq!(poly.alg_size, 3);
    /// ```
    pub fn new_safe(
        arity: usize,
        pars: Vec<Partition>,
        idempotent: bool,
        fixed_values: Option<Vec<i32>>,
    ) -> Result<Self, String> {
        if pars.is_empty() {
            return Err("Partitions list cannot be empty".to_string());
        }
        
        let alg_size = pars[0].universe_size();
        
        // Validate that all partitions have the same universe size
        for (i, partition) in pars.iter().enumerate() {
            if partition.universe_size() != alg_size {
                return Err(format!(
                    "Partition {} has universe size {} but expected {}",
                    i,
                    partition.universe_size(),
                    alg_size
                ));
            }
        }
        
        // Calculate table size: alg_size^arity
        let table_size = alg_size.pow(arity as u32);
        
        Ok(Polymorphisms {
            pars,
            alg_size,
            arity,
            idempotent,
            fixed_values,
            partial_op: None,
            partial_op_table: None,
            table_size,
            graph: None,
        })
    }
    
    /// Create a new Polymorphisms instance (panicking version for compatibility).
    /// 
    /// # Arguments
    /// * `arity` - The arity of the polymorphisms to calculate
    /// * `pars` - The collection of partitions
    /// * `idempotent` - Whether to only consider idempotent polymorphisms
    /// * `fixed_values` - Fixed values for the polymorphisms (optional)
    /// 
    /// # Panics
    /// Panics if the partitions list is empty or if partitions have different universe sizes
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::conlat::polymorphisms::Polymorphisms;
    /// use uacalc::alg::conlat::partition::Partition;
    /// 
    /// let pars = vec![Partition::zero(3), Partition::one(3)];
    /// let poly = Polymorphisms::new(1, pars, false, None);
    /// assert_eq!(poly.alg_size, 3);
    /// ```
    pub fn new(
        arity: usize,
        pars: Vec<Partition>,
        idempotent: bool,
        fixed_values: Option<Vec<i32>>,
    ) -> Self {
        Self::new_safe(arity, pars, idempotent, fixed_values).unwrap()
    }
    
    /// Get the number of partitions in this collection.
    /// 
    /// # Returns
    /// The number of partitions
    pub fn num_partitions(&self) -> usize {
        self.pars.len()
    }
    
    /// Get a reference to the partitions.
    /// 
    /// # Returns
    /// A reference to the vector of partitions
    pub fn get_partitions(&self) -> &Vec<Partition> {
        &self.pars
    }
    
    /// Get the algebra size.
    /// 
    /// # Returns
    /// The size of the underlying algebra
    pub fn get_alg_size(&self) -> usize {
        self.alg_size
    }
    
    /// Get the arity.
    /// 
    /// # Returns
    /// The arity of the polymorphisms
    pub fn get_arity(&self) -> usize {
        self.arity
    }
    
    /// Check if idempotent polymorphisms are required.
    /// 
    /// # Returns
    /// `true` if only idempotent polymorphisms are considered
    pub fn is_idempotent(&self) -> bool {
        self.idempotent
    }
    
    /// Get the fixed values (if any).
    /// 
    /// # Returns
    /// A reference to the fixed values, or `None` if not set
    pub fn get_fixed_values(&self) -> Option<&Vec<i32>> {
        self.fixed_values.as_ref()
    }
    
    /// Get the table size.
    /// 
    /// # Returns
    /// The size of the operation table (alg_size^arity)
    pub fn get_table_size(&self) -> usize {
        self.table_size
    }
    
    /// Initialize the graph structure for polymorphism calculations.
    /// 
    /// This method creates the graph structure that will be used for
    /// calculating polymorphisms. The graph is initially empty.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully initialized the graph
    /// * `Err(String)` - Error message if initialization fails
    pub fn make_graph(&mut self) -> Result<(), String> {
        self.graph = Some(HashMap::new());
        Ok(())
    }
    
    /// Check if the graph has been initialized.
    /// 
    /// # Returns
    /// `true` if the graph has been initialized
    pub fn has_graph(&self) -> bool {
        self.graph.is_some()
    }
    
    /// Get a reference to the graph (if initialized).
    /// 
    /// # Returns
    /// A reference to the graph, or `None` if not initialized
    pub fn get_graph(&self) -> Option<&HashMap<IntArray, HashMap<IntArray, Partition>>> {
        self.graph.as_ref()
    }
    
    /// Set the partial operation.
    /// 
    /// # Arguments
    /// * `op` - The partial operation to set
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully set the operation
    /// * `Err(String)` - Error message if validation fails
    pub fn set_partial_op(&mut self, op: Box<dyn Operation>) -> Result<(), String> {
        // Validate that the operation has the correct arity
        if op.arity() as usize != self.arity {
            return Err(format!(
                "Operation arity {} does not match polymorphisms arity {}",
                op.arity(),
                self.arity
            ));
        }
        
        // Validate that the operation has the correct set size
        if op.get_set_size() as usize != self.alg_size {
            return Err(format!(
                "Operation set size {} does not match algebra size {}",
                op.get_set_size(),
                self.alg_size
            ));
        }
        
        self.partial_op = Some(op);
        Ok(())
    }
    
    /// Get a reference to the partial operation (if set).
    /// 
    /// # Returns
    /// A reference to the partial operation, or `None` if not set
    pub fn get_partial_op(&self) -> Option<&Box<dyn Operation>> {
        self.partial_op.as_ref()
    }
    
    /// Set the partial operation table.
    /// 
    /// # Arguments
    /// * `table` - The operation table to set
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully set the table
    /// * `Err(String)` - Error message if validation fails
    pub fn set_partial_op_table(&mut self, table: Vec<i32>) -> Result<(), String> {
        if table.len() != self.table_size {
            return Err(format!(
                "Table size {} does not match expected size {}",
                table.len(),
                self.table_size
            ));
        }
        
        self.partial_op_table = Some(table);
        Ok(())
    }
    
    /// Get a reference to the partial operation table (if set).
    /// 
    /// # Returns
    /// A reference to the operation table, or `None` if not set
    pub fn get_partial_op_table(&self) -> Option<&Vec<i32>> {
        self.partial_op_table.as_ref()
    }
}

impl fmt::Display for Polymorphisms {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Polymorphisms(arity={}, partitions={}, alg_size={}, idempotent={})",
            self.arity,
            self.pars.len(),
            self.alg_size,
            self.idempotent
        )
    }
}

impl PartialEq for Polymorphisms {
    fn eq(&self, other: &Self) -> bool {
        self.pars == other.pars
            && self.alg_size == other.alg_size
            && self.arity == other.arity
            && self.idempotent == other.idempotent
            && self.fixed_values == other.fixed_values
            && self.table_size == other.table_size
            // Note: We don't compare partial_op, partial_op_table, or graph
            // as they are not part of the core identity
    }
}

impl Eq for Polymorphisms {}

impl Clone for Polymorphisms {
    fn clone(&self) -> Self {
        Polymorphisms {
            pars: self.pars.clone(),
            alg_size: self.alg_size,
            arity: self.arity,
            idempotent: self.idempotent,
            fixed_values: self.fixed_values.clone(),
            partial_op: None, // Cannot clone Box<dyn Operation>
            partial_op_table: self.partial_op_table.clone(),
            table_size: self.table_size,
            graph: self.graph.clone(),
        }
    }
}

impl std::hash::Hash for Polymorphisms {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.pars.hash(state);
        self.alg_size.hash(state);
        self.arity.hash(state);
        self.idempotent.hash(state);
        self.fixed_values.hash(state);
        self.table_size.hash(state);
        // Note: We don't hash partial_op, partial_op_table, or graph
        // as they are not part of the core identity
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::hash::{Hash, Hasher};
    
    #[test]
    fn test_new_safe() {
        let pars = vec![Partition::zero(3), Partition::one(3)];
        let poly = Polymorphisms::new_safe(1, pars.clone(), false, None).unwrap();
        
        assert_eq!(poly.pars, pars);
        assert_eq!(poly.alg_size, 3);
        assert_eq!(poly.arity, 1);
        assert_eq!(poly.idempotent, false);
        assert_eq!(poly.fixed_values, None);
        assert_eq!(poly.table_size, 3);
        assert_eq!(poly.graph, None);
    }
    
    #[test]
    fn test_new_safe_empty_partitions() {
        let result = Polymorphisms::new_safe(1, vec![], false, None);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("cannot be empty"));
    }
    
    #[test]
    fn test_new_safe_different_sizes() {
        let pars = vec![Partition::zero(3), Partition::zero(4)];
        let result = Polymorphisms::new_safe(1, pars, false, None);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("universe size"));
    }
    
    #[test]
    fn test_new() {
        let pars = vec![Partition::zero(3), Partition::one(3)];
        let poly = Polymorphisms::new(1, pars, false, None);
        assert_eq!(poly.alg_size, 3);
        assert_eq!(poly.arity, 1);
    }
    
    #[test]
    fn test_table_size_calculation() {
        let pars = vec![Partition::zero(3)];
        
        // Arity 1: 3^1 = 3
        let poly1 = Polymorphisms::new_safe(1, pars.clone(), false, None).unwrap();
        assert_eq!(poly1.table_size, 3);
        
        // Arity 2: 3^2 = 9
        let poly2 = Polymorphisms::new_safe(2, pars.clone(), false, None).unwrap();
        assert_eq!(poly2.table_size, 9);
        
        // Arity 3: 3^3 = 27
        let poly3 = Polymorphisms::new_safe(3, pars, false, None).unwrap();
        assert_eq!(poly3.table_size, 27);
    }
    
    #[test]
    fn test_make_graph() {
        let pars = vec![Partition::zero(3)];
        let mut poly = Polymorphisms::new_safe(1, pars, false, None).unwrap();
        
        assert!(!poly.has_graph());
        poly.make_graph().unwrap();
        assert!(poly.has_graph());
        assert!(poly.get_graph().is_some());
    }
    
    #[test]
    fn test_fixed_values() {
        let pars = vec![Partition::zero(3)];
        let fixed_values = Some(vec![0, 1, 2]);
        let poly = Polymorphisms::new_safe(1, pars, false, fixed_values.clone()).unwrap();
        
        assert_eq!(poly.get_fixed_values(), fixed_values.as_ref());
    }
    
    #[test]
    fn test_display() {
        let pars = vec![Partition::zero(3), Partition::one(3)];
        let poly = Polymorphisms::new_safe(1, pars, true, None).unwrap();
        let s = poly.to_string();
        
        assert!(s.contains("arity=1"));
        assert!(s.contains("partitions=2"));
        assert!(s.contains("alg_size=3"));
        assert!(s.contains("idempotent=true"));
    }
    
    #[test]
    fn test_equality() {
        let pars1 = vec![Partition::zero(3), Partition::one(3)];
        let pars2 = vec![Partition::zero(3), Partition::one(3)];
        let pars3 = vec![Partition::zero(3)];
        
        let poly1 = Polymorphisms::new_safe(1, pars1, false, None).unwrap();
        let poly2 = Polymorphisms::new_safe(1, pars2, false, None).unwrap();
        let poly3 = Polymorphisms::new_safe(1, pars3, false, None).unwrap();
        
        assert_eq!(poly1, poly2);
        assert_ne!(poly1, poly3);
    }
    
    #[test]
    fn test_hash() {
        let pars1 = vec![Partition::zero(3), Partition::one(3)];
        let pars2 = vec![Partition::zero(3), Partition::one(3)];
        
        let poly1 = Polymorphisms::new_safe(1, pars1, false, None).unwrap();
        let poly2 = Polymorphisms::new_safe(1, pars2, false, None).unwrap();
        
        let mut hasher1 = std::collections::hash_map::DefaultHasher::new();
        let mut hasher2 = std::collections::hash_map::DefaultHasher::new();
        
        poly1.hash(&mut hasher1);
        poly2.hash(&mut hasher2);
        
        assert_eq!(hasher1.finish(), hasher2.finish());
    }
}
