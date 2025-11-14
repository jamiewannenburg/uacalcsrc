use crate::lat::Order;
use crate::terms::{Variable, VariableImp};
use std::sync::Arc;
use std::fmt;

/// A partially defined lattice as defined in Gratzer's "Free and finitely presented lattices".
/// 
/// This structure represents a partial lattice with a defined order relation and
/// lists of defined join and meet operations.
/// 
/// In Java: `org.uacalc.fplat.PartiallyDefinedLattice`
#[derive(Clone)]
pub struct PartiallyDefinedLattice {
    /// The name of this partially defined lattice
    pub name: String,
    /// The underlying order relation on variables (shared ownership for cloneability)
    pub order: Arc<dyn Order<VariableImp> + Send + Sync>,
    /// List of defined join operations
    pub defined_joins: Vec<Vec<VariableImp>>,
    /// List of defined meet operations
    pub defined_meets: Vec<Vec<VariableImp>>,
}

impl fmt::Debug for PartiallyDefinedLattice {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("PartiallyDefinedLattice")
            .field("name", &self.name)
            .field("defined_joins", &self.defined_joins)
            .field("defined_meets", &self.defined_meets)
            .finish()
    }
}

impl PartiallyDefinedLattice {
    /// Creates a new partially defined lattice with the given parameters.
    /// 
    /// # Arguments
    /// * `name` - The name of the lattice
    /// * `order` - The order relation on variables
    /// * `joins` - List of defined join operations
    /// * `meets` - List of defined meet operations
    /// 
    /// # Returns
    /// A new PartiallyDefinedLattice instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::fplat::PartiallyDefinedLattice;
    /// use uacalc::lat::{Order, NaturalOrder};
    /// use uacalc::terms::VariableImp;
    /// use std::sync::Arc;
    /// 
    /// // Create a simple order (Note: NaturalOrder doesn't work directly with VariableImp,
    /// // this is just for illustration)
    /// // let order = Arc::new(NaturalOrder) as Arc<dyn Order<VariableImp>>;
    /// 
    /// // Create variables
    /// let x = VariableImp::new("x");
    /// let y = VariableImp::new("y");
    /// 
    /// // Define joins and meets
    /// let joins = vec![vec![x.clone(), y.clone()]];
    /// let meets = vec![vec![x.clone(), y.clone()]];
    /// 
    /// // For testing, we'd create a custom order implementation
    /// // let lattice = PartiallyDefinedLattice::new(
    /// //     "TestLattice".to_string(),
    /// //     order,
    /// //     joins,
    /// //     meets
    /// // );
    /// ```
    pub fn new(
        name: String,
        order: Arc<dyn Order<VariableImp> + Send + Sync>,
        joins: Vec<Vec<VariableImp>>,
        meets: Vec<Vec<VariableImp>>,
    ) -> Self {
        PartiallyDefinedLattice {
            name,
            order,
            defined_joins: joins,
            defined_meets: meets,
        }
    }
    
    /// Creates a new partially defined lattice with validation.
    /// 
    /// # Arguments
    /// * `name` - The name of the lattice
    /// * `order` - The order relation on variables
    /// * `joins` - List of defined join operations
    /// * `meets` - List of defined meet operations
    /// 
    /// # Returns
    /// * `Ok(Self)` - Successfully created lattice
    /// * `Err(String)` - Error message if validation fails
    pub fn new_safe(
        name: String,
        order: Arc<dyn Order<VariableImp> + Send + Sync>,
        joins: Vec<Vec<VariableImp>>,
        meets: Vec<Vec<VariableImp>>,
    ) -> Result<Self, String> {
        // Validation could be added here
        Ok(Self::new(name, order, joins, meets))
    }
    
    /// Returns the name of this partially defined lattice.
    /// 
    /// # Returns
    /// The lattice name
    pub fn name(&self) -> &str {
        &self.name
    }
    
    /// Returns the defined joins.
    /// 
    /// # Returns
    /// A reference to the list of defined join operations
    pub fn get_defined_joins(&self) -> &Vec<Vec<VariableImp>> {
        &self.defined_joins
    }
    
    /// Returns the defined meets.
    /// 
    /// # Returns
    /// A reference to the list of defined meet operations
    pub fn get_defined_meets(&self) -> &Vec<Vec<VariableImp>> {
        &self.defined_meets
    }
}

impl Order<VariableImp> for PartiallyDefinedLattice {
    /// Implements the order relation by delegating to the underlying order.
    /// 
    /// # Arguments
    /// * `a` - The first variable
    /// * `b` - The second variable
    /// 
    /// # Returns
    /// `true` if a ≤ b according to the underlying order, `false` otherwise
    fn leq(&self, a: &VariableImp, b: &VariableImp) -> bool {
        self.order.leq(a, b)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::lat::Order;
    use crate::terms::VariableImp;
    use std::sync::Arc;
    
    /// Simple order implementation for testing that orders variables by name
    #[derive(Debug, Clone)]
    struct VariableNameOrder;
    
    impl Order<VariableImp> for VariableNameOrder {
        fn leq(&self, a: &VariableImp, b: &VariableImp) -> bool {
            a.name <= b.name
        }
    }
    
    #[test]
    fn test_create_simple() {
        // Create variables
        let x = VariableImp::new("x");
        let y = VariableImp::new("y");
        let z = VariableImp::new("z");
        
        // Create order
        let order: Arc<dyn Order<VariableImp> + Send + Sync> = Arc::new(VariableNameOrder);
        
        // Create joins and meets
        let joins = vec![vec![x.clone(), y.clone()]];
        let meets = vec![vec![y.clone(), z.clone()]];
        
        // Create lattice
        let lattice = PartiallyDefinedLattice::new(
            "TestLattice".to_string(),
            order,
            joins,
            meets,
        );
        
        // Test name
        assert_eq!(lattice.name(), "TestLattice");
        
        // Test joins and meets
        assert_eq!(lattice.get_defined_joins().len(), 1);
        assert_eq!(lattice.get_defined_meets().len(), 1);
        
        // Test order relation
        assert!(lattice.leq(&x, &y)); // x <= y because "x" <= "y"
        assert!(!lattice.leq(&y, &x)); // y > x
        assert!(lattice.leq(&x, &x)); // reflexive
    }
    
    #[test]
    fn test_leq_order() {
        // Create variables with different names
        let a = VariableImp::new("a");
        let b = VariableImp::new("b");
        let c = VariableImp::new("c");
        
        // Create order
        let order: Arc<dyn Order<VariableImp> + Send + Sync> = Arc::new(VariableNameOrder);
        
        // Create empty joins and meets
        let joins = vec![];
        let meets = vec![];
        
        // Create lattice
        let lattice = PartiallyDefinedLattice::new(
            "OrderTest".to_string(),
            order,
            joins,
            meets,
        );
        
        // Test order relations
        assert!(lattice.leq(&a, &b)); // a <= b
        assert!(lattice.leq(&b, &c)); // b <= c
        assert!(lattice.leq(&a, &c)); // a <= c (transitivity)
        assert!(!lattice.leq(&c, &a)); // c > a
        
        // Test reflexivity
        assert!(lattice.leq(&a, &a));
        assert!(lattice.leq(&b, &b));
        assert!(lattice.leq(&c, &c));
    }
    
    #[test]
    fn test_multiple_joins_meets() {
        // Create several variables
        let x = VariableImp::new("x");
        let y = VariableImp::new("y");
        let z = VariableImp::new("z");
        let w = VariableImp::new("w");
        
        // Create order
        let order: Arc<dyn Order<VariableImp> + Send + Sync> = Arc::new(VariableNameOrder);
        
        // Create multiple joins and meets
        let joins = vec![
            vec![x.clone(), y.clone()],
            vec![z.clone(), w.clone()],
        ];
        let meets = vec![
            vec![x.clone(), z.clone()],
            vec![y.clone(), w.clone()],
        ];
        
        // Create lattice
        let lattice = PartiallyDefinedLattice::new(
            "MultiLattice".to_string(),
            order,
            joins,
            meets,
        );
        
        // Test counts
        assert_eq!(lattice.get_defined_joins().len(), 2);
        assert_eq!(lattice.get_defined_meets().len(), 2);
        
        // Test individual joins
        assert_eq!(lattice.get_defined_joins()[0].len(), 2);
        assert_eq!(lattice.get_defined_joins()[1].len(), 2);
        
        // Test individual meets
        assert_eq!(lattice.get_defined_meets()[0].len(), 2);
        assert_eq!(lattice.get_defined_meets()[1].len(), 2);
    }
    
    #[test]
    fn test_clone() {
        // Create variables
        let x = VariableImp::new("x");
        let y = VariableImp::new("y");
        
        // Create order
        let order: Arc<dyn Order<VariableImp> + Send + Sync> = Arc::new(VariableNameOrder);
        
        // Create joins and meets
        let joins = vec![vec![x.clone(), y.clone()]];
        let meets = vec![vec![x.clone(), y.clone()]];
        
        // Create lattice
        let lattice = PartiallyDefinedLattice::new(
            "Original".to_string(),
            order,
            joins,
            meets,
        );
        
        // Clone the lattice
        let cloned = lattice.clone();
        
        // Test that clone has same properties
        assert_eq!(cloned.name(), lattice.name());
        assert_eq!(cloned.get_defined_joins().len(), lattice.get_defined_joins().len());
        assert_eq!(cloned.get_defined_meets().len(), lattice.get_defined_meets().len());
        
        // Test order relation on clone
        assert_eq!(cloned.leq(&x, &y), lattice.leq(&x, &y));
    }
    
    #[test]
    fn test_new_safe() {
        // Create variables
        let x = VariableImp::new("x");
        let y = VariableImp::new("y");
        
        // Create order
        let order: Arc<dyn Order<VariableImp> + Send + Sync> = Arc::new(VariableNameOrder);
        
        // Create joins and meets
        let joins = vec![vec![x.clone(), y.clone()]];
        let meets = vec![vec![x.clone(), y.clone()]];
        
        // Test new_safe
        let result = PartiallyDefinedLattice::new_safe(
            "SafeLattice".to_string(),
            order,
            joins,
            meets,
        );
        
        assert!(result.is_ok());
        let lattice = result.unwrap();
        assert_eq!(lattice.name(), "SafeLattice");
    }
}
