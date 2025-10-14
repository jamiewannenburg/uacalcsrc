//! Partially defined lattices implementation.
//!
//! This module implements partially defined lattices as defined in the 
//! chapter "Free and finitely presented lattices" in Grätzer's STA book.

use crate::lat::Order;
use crate::term::Variable;

/// A partially defined lattice that wraps an order relation on variables
/// and tracks which join and meet operations are defined.
/// 
/// This corresponds to the Java `PartiallyDefinedLattice` class and implements
/// the `Order<Variable>` interface by delegating to a wrapped order.
/// 
/// # Examples
/// ```
/// use uacalc_core::fplat::PartiallyDefinedLattice;
/// use uacalc_core::term::Variable;
/// 
/// // Create variables
/// let x = Variable::named(0, "x".to_string());
/// let y = Variable::named(1, "y".to_string());
/// 
/// // Define a simple order: x <= y
/// let order = |a: &Variable, b: &Variable| {
///     a.index() <= b.index()
/// };
/// 
/// // Create partially defined lattice
/// let joins = vec![vec![x.clone(), y.clone()]]; // x ∨ y is defined
/// let meets = vec![vec![x.clone(), y.clone()]]; // x ∧ y is defined
/// 
/// let pdl = PartiallyDefinedLattice::new(
///     "example".to_string(),
///     order,
///     joins,
///     meets
/// );
/// 
/// // Test the order relation
/// assert!(pdl.leq(&x, &y));
/// assert!(pdl.leq(&x, &x));
/// ```
#[derive(Debug, Clone)]
pub struct PartiallyDefinedLattice<F>
where
    F: Fn(&Variable, &Variable) -> bool,
{
    /// Name of this partially defined lattice
    name: String,
    /// The underlying order relation on variables
    order: F,
    /// List of variable pairs/tuples for which join is defined
    defined_joins: Vec<Vec<Variable>>,
    /// List of variable pairs/tuples for which meet is defined
    defined_meets: Vec<Vec<Variable>>,
}

impl<F> PartiallyDefinedLattice<F>
where
    F: Fn(&Variable, &Variable) -> bool,
{
    /// Create a new partially defined lattice.
    /// 
    /// # Arguments
    /// * `name` - Name for this lattice
    /// * `order` - Order relation on variables (closure implementing leq)
    /// * `joins` - List of variable tuples for which join operations are defined
    /// * `meets` - List of variable tuples for which meet operations are defined
    /// 
    /// # Returns
    /// A new `PartiallyDefinedLattice` instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc_core::fplat::PartiallyDefinedLattice;
    /// use uacalc_core::term::Variable;
    /// 
    /// let x = Variable::named(0, "x".to_string());
    /// let y = Variable::named(1, "y".to_string());
    /// 
    /// let order = |a: &Variable, b: &Variable| a.index() <= b.index();
    /// let joins = vec![vec![x.clone(), y.clone()]];
    /// let meets = vec![vec![x.clone(), y.clone()]];
    /// 
    /// let pdl = PartiallyDefinedLattice::new(
    ///     "test".to_string(),
    ///     order,
    ///     joins, 
    ///     meets
    /// );
    /// ```
    pub fn new(
        name: String,
        order: F,
        joins: Vec<Vec<Variable>>,
        meets: Vec<Vec<Variable>>,
    ) -> Self {
        Self {
            name,
            order,
            defined_joins: joins,
            defined_meets: meets,
        }
    }
    
    /// Get the name of this partially defined lattice.
    pub fn name(&self) -> &str {
        &self.name
    }
    
    /// Get the defined join operations.
    /// 
    /// # Returns
    /// A reference to the list of variable tuples for which join is defined
    pub fn defined_joins(&self) -> &[Vec<Variable>] {
        &self.defined_joins
    }
    
    /// Get the defined meet operations.
    /// 
    /// # Returns
    /// A reference to the list of variable tuples for which meet is defined
    pub fn defined_meets(&self) -> &[Vec<Variable>] {
        &self.defined_meets
    }
    
    /// Check if a join operation is defined for the given variables.
    /// 
    /// # Arguments
    /// * `vars` - Variables to check for defined join
    /// 
    /// # Returns
    /// `true` if join is defined for these variables, `false` otherwise
    pub fn is_join_defined(&self, vars: &[Variable]) -> bool {
        self.defined_joins.iter().any(|defined_vars| {
            vars.len() == defined_vars.len() && 
            vars.iter().all(|v| defined_vars.contains(v))
        })
    }
    
    /// Check if a meet operation is defined for the given variables.
    /// 
    /// # Arguments
    /// * `vars` - Variables to check for defined meet
    /// 
    /// # Returns
    /// `true` if meet is defined for these variables, `false` otherwise
    pub fn is_meet_defined(&self, vars: &[Variable]) -> bool {
        self.defined_meets.iter().any(|defined_vars| {
            vars.len() == defined_vars.len() && 
            vars.iter().all(|v| defined_vars.contains(v))
        })
    }
    
    /// Add a defined join operation.
    /// 
    /// # Arguments
    /// * `vars` - Variables for which join should be defined
    pub fn add_defined_join(&mut self, vars: Vec<Variable>) {
        if !self.is_join_defined(&vars) {
            self.defined_joins.push(vars);
        }
    }
    
    /// Add a defined meet operation.
    /// 
    /// # Arguments  
    /// * `vars` - Variables for which meet should be defined
    pub fn add_defined_meet(&mut self, vars: Vec<Variable>) {
        if !self.is_meet_defined(&vars) {
            self.defined_meets.push(vars);
        }
    }
    
    /// Get all variables mentioned in this partially defined lattice.
    /// 
    /// # Returns
    /// A vector of all unique variables used in join/meet definitions
    pub fn variables(&self) -> Vec<Variable> {
        let mut vars = std::collections::HashSet::new();
        
        for join_vars in &self.defined_joins {
            for var in join_vars {
                vars.insert(var.clone());
            }
        }
        
        for meet_vars in &self.defined_meets {
            for var in meet_vars {
                vars.insert(var.clone());
            }
        }
        
        vars.into_iter().collect()
    }
}

impl<F> Order<Variable> for PartiallyDefinedLattice<F>
where
    F: Fn(&Variable, &Variable) -> bool,
{
    /// Check if variable `a` is less than or equal to variable `b` according to the underlying order.
    /// 
    /// This method delegates to the wrapped order relation.
    /// 
    /// # Arguments
    /// * `a` - First variable
    /// * `b` - Second variable
    /// 
    /// # Returns
    /// `true` if `a ≤ b` according to the underlying order, `false` otherwise
    /// 
    /// # Examples
    /// ```
    /// use uacalc_core::fplat::PartiallyDefinedLattice;
    /// use uacalc_core::term::Variable;
    /// use uacalc_core::lat::Order;
    /// 
    /// let x = Variable::named(0, "x".to_string());
    /// let y = Variable::named(1, "y".to_string());
    /// 
    /// let order = |a: &Variable, b: &Variable| a.index() <= b.index();
    /// let pdl = PartiallyDefinedLattice::new(
    ///     "test".to_string(),
    ///     order,
    ///     vec![],
    ///     vec![]
    /// );
    /// 
    /// assert!(pdl.leq(&x, &y));
    /// assert!(pdl.leq(&x, &x));
    /// assert!(!pdl.leq(&y, &x));
    /// ```
    fn leq(&self, a: &Variable, b: &Variable) -> bool {
        (self.order)(a, b)
    }
}

/// Demonstration function corresponding to the Java main method.
/// 
/// This function demonstrates basic usage of `PartiallyDefinedLattice`.
/// 
/// # Examples
/// ```
/// use uacalc_core::fplat::partially_defined_lattice_main;
/// 
/// // This will demonstrate the partially defined lattice functionality
/// partially_defined_lattice_main();
/// ```
pub fn main() {
    println!("PartiallyDefinedLattice demonstration");
    
    // Create some example variables
    let x = Variable::named(0, "x".to_string());
    let y = Variable::named(1, "y".to_string());
    let z = Variable::named(2, "z".to_string());
    
    // Define a simple order based on variable indices
    let index_order = |a: &Variable, b: &Variable| a.index() <= b.index();
    
    // Define some join and meet operations
    let joins = vec![
        vec![x.clone(), y.clone()],  // x ∨ y is defined
        vec![y.clone(), z.clone()],  // y ∨ z is defined
    ];
    
    let meets = vec![
        vec![x.clone(), y.clone()],  // x ∧ y is defined
        vec![x.clone(), z.clone()],  // x ∧ z is defined
    ];
    
    // Create the partially defined lattice
    let pdl = PartiallyDefinedLattice::new(
        "example".to_string(),
        index_order,
        joins,
        meets,
    );
    
    println!("Created partially defined lattice: {}", pdl.name());
    println!("Variables: {:?}", pdl.variables().iter().map(|v| v.name()).collect::<Vec<_>>());
    println!("Defined joins: {} operations", pdl.defined_joins().len());
    println!("Defined meets: {} operations", pdl.defined_meets().len());
    
    // Test the order relation
    println!("Order relations:");
    println!("  x ≤ y: {}", pdl.leq(&x, &y));
    println!("  y ≤ x: {}", pdl.leq(&y, &x));
    println!("  x ≤ z: {}", pdl.leq(&x, &z));
    
    // Test operation definitions
    println!("Operation definitions:");
    println!("  x ∨ y defined: {}", pdl.is_join_defined(&[x.clone(), y.clone()]));
    println!("  x ∧ z defined: {}", pdl.is_meet_defined(&[x.clone(), z.clone()]));
    println!("  y ∧ z defined: {}", pdl.is_meet_defined(&[y.clone(), z.clone()]));
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::lat::Order;

    #[test]
    fn test_new_partially_defined_lattice() {
        let x = Variable::named(0, "x".to_string());
        let y = Variable::named(1, "y".to_string());
        
        let order = |a: &Variable, b: &Variable| a.index() <= b.index();
        let joins = vec![vec![x.clone(), y.clone()]];
        let meets = vec![vec![x.clone(), y.clone()]];
        
        let pdl = PartiallyDefinedLattice::new(
            "test".to_string(),
            order,
            joins,
            meets,
        );
        
        assert_eq!(pdl.name(), "test");
        assert_eq!(pdl.defined_joins().len(), 1);
        assert_eq!(pdl.defined_meets().len(), 1);
    }
    
    #[test]
    fn test_order_delegation() {
        let x = Variable::named(0, "x".to_string());
        let y = Variable::named(1, "y".to_string());
        let z = Variable::named(2, "z".to_string());
        
        let index_order = |a: &Variable, b: &Variable| a.index() <= b.index();
        let pdl = PartiallyDefinedLattice::new(
            "test".to_string(),
            index_order,
            vec![],
            vec![],
        );
        
        // Test order delegation
        assert!(pdl.leq(&x, &y));
        assert!(pdl.leq(&y, &z));
        assert!(pdl.leq(&x, &z));
        assert!(pdl.leq(&x, &x));
        
        assert!(!pdl.leq(&y, &x));
        assert!(!pdl.leq(&z, &y));
        assert!(!pdl.leq(&z, &x));
    }
    
    #[test]
    fn test_operation_definitions() {
        let x = Variable::named(0, "x".to_string());
        let y = Variable::named(1, "y".to_string());
        let z = Variable::named(2, "z".to_string());
        
        let order = |a: &Variable, b: &Variable| a.index() <= b.index();
        let joins = vec![
            vec![x.clone(), y.clone()],
            vec![y.clone(), z.clone()],
        ];
        let meets = vec![
            vec![x.clone(), z.clone()],
        ];
        
        let pdl = PartiallyDefinedLattice::new(
            "test".to_string(),
            order,
            joins,
            meets,
        );
        
        // Test join definitions
        assert!(pdl.is_join_defined(&[x.clone(), y.clone()]));
        assert!(pdl.is_join_defined(&[y.clone(), z.clone()]));
        assert!(!pdl.is_join_defined(&[x.clone(), z.clone()]));
        
        // Test meet definitions
        assert!(pdl.is_meet_defined(&[x.clone(), z.clone()]));
        assert!(!pdl.is_meet_defined(&[x.clone(), y.clone()]));
        assert!(!pdl.is_meet_defined(&[y.clone(), z.clone()]));
    }
    
    #[test]
    fn test_add_operations() {
        let x = Variable::named(0, "x".to_string());
        let y = Variable::named(1, "y".to_string());
        
        let order = |a: &Variable, b: &Variable| a.index() <= b.index();
        let mut pdl = PartiallyDefinedLattice::new(
            "test".to_string(),
            order,
            vec![],
            vec![],
        );
        
        // Initially no operations defined
        assert!(!pdl.is_join_defined(&[x.clone(), y.clone()]));
        assert!(!pdl.is_meet_defined(&[x.clone(), y.clone()]));
        
        // Add operations
        pdl.add_defined_join(vec![x.clone(), y.clone()]);
        pdl.add_defined_meet(vec![x.clone(), y.clone()]);
        
        // Now operations should be defined
        assert!(pdl.is_join_defined(&[x.clone(), y.clone()]));
        assert!(pdl.is_meet_defined(&[x.clone(), y.clone()]));
        
        // Adding same operation again should not duplicate
        pdl.add_defined_join(vec![x.clone(), y.clone()]);
        assert_eq!(pdl.defined_joins().len(), 1);
    }
    
    #[test]
    fn test_variables() {
        let x = Variable::named(0, "x".to_string());
        let y = Variable::named(1, "y".to_string());
        let z = Variable::named(2, "z".to_string());
        
        let order = |a: &Variable, b: &Variable| a.index() <= b.index();
        let joins = vec![vec![x.clone(), y.clone()]];
        let meets = vec![vec![y.clone(), z.clone()]];
        
        let pdl = PartiallyDefinedLattice::new(
            "test".to_string(),
            order,
            joins,
            meets,
        );
        
        let vars = pdl.variables();
        assert_eq!(vars.len(), 3);
        assert!(vars.contains(&x));
        assert!(vars.contains(&y));
        assert!(vars.contains(&z));
    }
    
    #[test]
    fn test_empty_lattice() {
        let order = |a: &Variable, b: &Variable| a.index() <= b.index();
        let pdl = PartiallyDefinedLattice::new(
            "empty".to_string(),
            order,
            vec![],
            vec![],
        );
        
        assert_eq!(pdl.name(), "empty");
        assert_eq!(pdl.defined_joins().len(), 0);
        assert_eq!(pdl.defined_meets().len(), 0);
        assert_eq!(pdl.variables().len(), 0);
    }
    
}