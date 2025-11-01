use std::fmt::{self, Debug, Display};
use std::sync::Arc;
use std::hash::{Hash, Hasher};
use crate::alg::conlat::partition::Partition;
use crate::alg::small_algebra::SmallAlgebra;

/// Represents an element in a quotient algebra.
/// 
/// A QuotientElement holds a reference to its containing QuotientAlgebra
/// and an index within that algebra. The index refers to a position in the
/// quotient algebra (not the super algebra).
/// 
/// # Type Parameters
/// * `T` - The universe item type of the super algebra
/// 
/// # Examples
/// ```
/// // QuotientElement is typically created by QuotientAlgebra.get_element()
/// // See QuotientAlgebra documentation for examples
/// ```
#[derive(Debug, Clone)]
pub struct QuotientElement<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    /// The quotient algebra this element belongs to (shared reference)
    pub(crate) alg: Arc<QuotientAlgebraRef<T>>,
    /// The index in the quotient algebra (not super algebra)
    pub index: usize,
}

/// Internal reference type for QuotientAlgebra to avoid circular dependencies.
/// This holds the minimal information needed by QuotientElement.
#[derive(Debug)]
pub struct QuotientAlgebraRef<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    /// The super algebra
    pub super_algebra: Box<dyn SmallAlgebra<UniverseItem = T>>,
    /// The congruence partition
    pub congruence: Partition,
    /// Representatives of congruence classes
    pub representatives: Vec<usize>,
}

impl<T> QuotientElement<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    /// Create a new QuotientElement.
    /// 
    /// # Arguments
    /// * `alg` - Reference to the quotient algebra
    /// * `index` - The index in the quotient algebra
    /// 
    /// # Returns
    /// A new QuotientElement instance
    /// 
    /// # Examples
    /// ```
    /// // QuotientElement is typically created by QuotientAlgebra.get_element()
    /// ```
    pub fn new(alg: Arc<QuotientAlgebraRef<T>>, index: usize) -> Self {
        QuotientElement { alg, index }
    }
    
    /// Get the quotient algebra reference.
    /// 
    /// # Returns
    /// A shared reference to the quotient algebra data
    pub fn get_algebra(&self) -> &Arc<QuotientAlgebraRef<T>> {
        &self.alg
    }
    
    /// Get the super algebra.
    /// 
    /// # Returns
    /// A reference to the super algebra
    pub fn super_algebra(&self) -> &dyn SmallAlgebra<UniverseItem = T> {
        self.alg.super_algebra.as_ref()
    }
    
    /// Get the congruence partition.
    /// 
    /// # Returns
    /// A reference to the congruence partition
    pub fn get_congruence(&self) -> &Partition {
        &self.alg.congruence
    }
    
    /// Get the index in the quotient algebra.
    /// 
    /// # Returns
    /// The index in the quotient algebra (not super algebra)
    pub fn get_index(&self) -> usize {
        self.index
    }
    
    /// Get the index in the super algebra.
    /// 
    /// This returns the representative element in the super algebra
    /// for this quotient element's equivalence class.
    /// 
    /// # Returns
    /// The index in the super algebra
    pub fn get_index_in_super_algebra(&self) -> usize {
        self.alg.representatives[self.index]
    }
}

impl<T> Display for QuotientElement<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let index_in_super = self.get_index_in_super_algebra();
        if let Some(elem) = self.super_algebra().get_element(index_in_super) {
            write!(f, "{}/{}", elem, self.get_congruence())
        } else {
            write!(f, "?/{}", self.get_congruence())
        }
    }
}

impl<T> PartialEq for QuotientElement<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn eq(&self, other: &Self) -> bool {
        // Two quotient elements are equal if they have the same index
        // and belong to the same algebra (by checking representatives)
        self.index == other.index &&
        self.alg.representatives == other.alg.representatives
    }
}

impl<T> Eq for QuotientElement<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{}

impl<T> Hash for QuotientElement<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    fn hash<H: Hasher>(&self, state: &mut H) {
        // Hash based on index and representatives (which identifies the algebra)
        self.index.hash(state);
        self.alg.representatives.hash(state);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::small_algebra::BasicSmallAlgebra;
    use std::collections::HashSet;
    
    #[test]
    fn test_quotient_element_creation() {
        // Create a simple super algebra
        let super_algebra = Box::new(BasicSmallAlgebra::new(
            "A".to_string(),
            HashSet::from([0, 1, 2, 3]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        // Create a congruence: {0,1}, {2,3}
        let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
        let representatives = congruence.representatives();
        
        // Create quotient algebra reference
        let alg_ref = Arc::new(QuotientAlgebraRef::<i32> {
            super_algebra,
            congruence,
            representatives,
        });
        
        // Create quotient element
        let elem = QuotientElement::new(alg_ref.clone(), 0);
        
        assert_eq!(elem.get_index(), 0);
        assert_eq!(elem.get_index_in_super_algebra(), 0);
    }
}
