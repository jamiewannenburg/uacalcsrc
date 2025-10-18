use std::collections::HashMap;
use crate::util::int_array::IntArrayTrait;

pub mod algebra;
pub mod conlat;
pub mod general_algebra;
pub mod op;
pub mod parallel;
pub mod small_algebra;
pub mod sublat;

// Re-export partition types for convenience
pub use conlat::partition::{Partition, PrintType};

// Re-export algebra types
pub use algebra::{
    Algebra, CloneableAlgebra, BoxedAlgebra, boxed_algebra, ProgressMonitor,
    CARDINALITY_UNKNOWN, CARDINALITY_FINITE, CARDINALITY_INFINITE,
    CARDINALITY_COUNTABLE, CARDINALITY_COUNTABLY_INFINITE
};

// Re-export concrete algebra implementations
pub use general_algebra::GeneralAlgebra;
pub use small_algebra::{SmallAlgebra, BasicSmallAlgebra, AlgebraType};

// BasicAlgebra is now implemented as BasicSmallAlgebra
// GeneralAlgebra is now implemented in general_algebra.rs

pub struct FreeAlgebra {
    // TODO: Implement free algebra structure
}

pub struct ProductAlgebra {
    // TODO: Implement product algebra structure
}

pub struct Subalgebra {
    // TODO: Implement subalgebra structure
}

pub struct QuotientAlgebra {
    // TODO: Implement quotient algebra structure
}

/// A homomorphism from the domain algebra into the range algebra.
/// 
/// This struct represents a homomorphism between two small algebras, where
/// elements are mapped by their indices. The homomorphism preserves the
/// algebraic structure between the domain and range algebras.
/// 
/// # Examples
/// ```
/// use uacalc::alg::{Homomorphism, SmallAlgebra};
/// use std::collections::HashMap;
/// 
/// // Create a simple mapping
/// let mut map = HashMap::new();
/// map.insert(0, 0);
/// map.insert(1, 1);
/// 
/// // Create homomorphism (assuming domain and range algebras exist)
/// // let homo = Homomorphism::new(domain, range, map).unwrap();
/// ```
#[derive(Debug)]
pub struct Homomorphism {
    /// The domain algebra
    pub domain: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    /// The range algebra  
    pub range: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    /// The mapping from domain indices to range indices
    pub map: HashMap<usize, usize>,
}

impl Clone for Homomorphism {
    fn clone(&self) -> Self {
        Homomorphism {
            domain: self.domain.clone_box(),
            range: self.range.clone_box(),
            map: self.map.clone(),
        }
    }
}

impl Homomorphism {
    /// Create a new homomorphism from domain to range with the given mapping.
    /// 
    /// # Arguments
    /// * `domain` - The domain algebra
    /// * `range` - The range algebra
    /// * `map` - The mapping from domain indices to range indices
    /// 
    /// # Returns
    /// * `Ok(Homomorphism)` - Successfully created homomorphism
    /// * `Err(String)` - If the mapping is invalid or algebras are incompatible
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{Homomorphism, SmallAlgebra, BasicSmallAlgebra};
    /// use std::collections::{HashMap, HashSet};
    /// 
    /// // Create mock algebras
    /// let domain = Box::new(BasicSmallAlgebra::new(
    ///     "domain".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let range = Box::new(BasicSmallAlgebra::new(
    ///     "range".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// // Create a simple mapping
    /// let mut map = HashMap::new();
    /// map.insert(0, 0);
    /// map.insert(1, 1);
    /// 
    /// // Create homomorphism
    /// let homo = Homomorphism::new_safe(domain, range, map).unwrap();
    /// assert_eq!(homo.get_domain().name(), "domain");
    /// assert_eq!(homo.get_range().name(), "range");
    /// ```
    pub fn new_safe(
        domain: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        range: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        map: HashMap<usize, usize>,
    ) -> Result<Self, String> {
        // Validate that all domain elements are mapped
        let domain_size = domain.cardinality() as usize;
        for i in 0..domain_size {
            if !map.contains_key(&i) {
                return Err(format!("Domain element {} is not mapped", i));
            }
        }
        
        // Validate that all mapped values are valid range elements
        let range_size = range.cardinality() as usize;
        for (_, &range_val) in &map {
            if range_val >= range_size {
                return Err(format!("Mapped value {} is out of range [0, {})", range_val, range_size));
            }
        }
        
        Ok(Homomorphism { domain, range, map })
    }
    
    /// Create a new homomorphism with panic on error (for compatibility).
    /// 
    /// # Arguments
    /// * `domain` - The domain algebra
    /// * `range` - The range algebra
    /// * `map` - The mapping from domain indices to range indices
    /// 
    /// # Panics
    /// Panics if the mapping is invalid or algebras are incompatible
    pub fn new(
        domain: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        range: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        map: HashMap<usize, usize>,
    ) -> Self {
        Self::new_safe(domain, range, map).unwrap()
    }
    
    /// Compute the kernel partition of this homomorphism.
    /// 
    /// The kernel partition groups domain elements that map to the same
    /// range element. This is computed using the zero partition and
    /// joining blocks for elements with the same image.
    /// 
    /// # Returns
    /// * `Ok(Partition)` - The kernel partition
    /// * `Err(String)` - If there's an error computing the kernel
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{Homomorphism, SmallAlgebra, BasicSmallAlgebra};
    /// use std::collections::{HashMap, HashSet};
    /// 
    /// // Create mock algebras
    /// let domain = Box::new(BasicSmallAlgebra::new(
    ///     "domain".to_string(),
    ///     HashSet::from([0, 1, 2]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let range = Box::new(BasicSmallAlgebra::new(
    ///     "range".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// // Create mapping where 0 and 2 both map to 0, 1 maps to 1
    /// let mut map = HashMap::new();
    /// map.insert(0, 0);
    /// map.insert(1, 1);
    /// map.insert(2, 0);
    /// 
    /// // Create homomorphism and compute kernel
    /// let homo = Homomorphism::new_safe(domain, range, map).unwrap();
    /// let kernel = homo.kernel().unwrap();
    /// 
    /// // Kernel should have 2 blocks: {0, 2} and {1}
    /// assert_eq!(kernel.number_of_blocks(), 2);
    /// assert!(kernel.is_related(0, 2)); // 0 and 2 map to same value
    /// assert!(!kernel.is_related(0, 1)); // 0 and 1 map to different values
    /// ```
    pub fn kernel(&self) -> Result<Partition, String> {
        let size = self.domain.cardinality() as usize;
        let mut par = Partition::zero(size);
        
        for i in 0..size {
            let r = par.representative(i);
            for j in (i + 1)..size {
                if let (Some(&map_i), Some(&map_j)) = (self.map.get(&i), self.map.get(&j)) {
                    if map_i == map_j {
                        let s = par.representative(j);
                        if r != s {
                            par.join_blocks(r, s);
                        }
                    }
                }
            }
        }
        
        Ok(par)
    }
    
    /// Create a product homomorphism from a list of homomorphisms.
    /// 
    /// This static method creates a list of IntArray elements representing
    /// the product homomorphism. Each IntArray contains the mapped values
    /// for all homomorphisms at a given domain element.
    /// 
    /// # Arguments
    /// * `homomorphisms` - A slice of homomorphisms with the same domain
    /// 
    /// # Returns
    /// * `Ok(Vec<IntArray>)` - List of IntArray elements for the product
    /// * `Err(String)` - If the homomorphisms are incompatible or empty
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{Homomorphism, SmallAlgebra, BasicSmallAlgebra};
    /// use uacalc::util::int_array::IntArrayTrait;
    /// use std::collections::{HashMap, HashSet};
    /// 
    /// // Create mock algebras
    /// let domain = Box::new(BasicSmallAlgebra::new(
    ///     "domain".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let range1 = Box::new(BasicSmallAlgebra::new(
    ///     "range1".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let range2 = Box::new(BasicSmallAlgebra::new(
    ///     "range2".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// // Create two homomorphisms with same domain
    /// let mut map1 = HashMap::new();
    /// map1.insert(0, 0);
    /// map1.insert(1, 1);
    /// let homo1 = Homomorphism::new_safe(domain.clone_box(), range1, map1).unwrap();
    /// 
    /// let mut map2 = HashMap::new();
    /// map2.insert(0, 1);
    /// map2.insert(1, 0);
    /// let homo2 = Homomorphism::new_safe(domain, range2, map2).unwrap();
    /// 
    /// // Create product homomorphism
    /// let homos = vec![homo1, homo2];
    /// let product = Homomorphism::product_homo(&homos).unwrap();
    /// 
    /// // Product should have 2 elements (domain size)
    /// assert_eq!(product.len(), 2);
    /// // Each element should be an IntArray of size 2 (number of homomorphisms)
    /// assert_eq!(product[0].universe_size(), 2);
    /// assert_eq!(product[1].universe_size(), 2);
    /// ```
    pub fn product_homo(homomorphisms: &[Self]) -> Result<Vec<crate::util::int_array::IntArray>, String> {
        if homomorphisms.is_empty() {
            return Err("Cannot create product homomorphism from empty list".to_string());
        }
        
        let domain_size = homomorphisms[0].domain.cardinality() as usize;
        let mut ans = Vec::with_capacity(domain_size);
        
        for i in 0..domain_size {
            let mut ia = crate::util::int_array::IntArray::new(homomorphisms.len())?;
            for (k, homo) in homomorphisms.iter().enumerate() {
                if let Some(&mapped_val) = homo.map.get(&i) {
                    ia.set(k, mapped_val as i32)?;
                } else {
                    return Err(format!("Domain element {} not mapped in homomorphism {}", i, k));
                }
            }
            ans.push(ia);
        }
        
        Ok(ans)
    }
    
    /// Get the domain algebra.
    /// 
    /// # Returns
    /// A reference to the domain algebra
    pub fn get_domain(&self) -> &dyn SmallAlgebra<UniverseItem = i32> {
        self.domain.as_ref()
    }
    
    /// Set the domain algebra.
    /// 
    /// # Arguments
    /// * `domain` - The new domain algebra
    pub fn set_domain(&mut self, domain: Box<dyn SmallAlgebra<UniverseItem = i32>>) {
        self.domain = domain;
    }
    
    /// Get the range algebra.
    /// 
    /// # Returns
    /// A reference to the range algebra
    pub fn get_range(&self) -> &dyn SmallAlgebra<UniverseItem = i32> {
        self.range.as_ref()
    }
    
    /// Set the range algebra.
    /// 
    /// # Arguments
    /// * `range` - The new range algebra
    pub fn set_range(&mut self, range: Box<dyn SmallAlgebra<UniverseItem = i32>>) {
        self.range = range;
    }
    
    /// Get the mapping.
    /// 
    /// # Returns
    /// A reference to the mapping HashMap
    pub fn get_map(&self) -> &HashMap<usize, usize> {
        &self.map
    }
    
    /// Set the mapping.
    /// 
    /// # Arguments
    /// * `map` - The new mapping
    pub fn set_map(&mut self, map: HashMap<usize, usize>) {
        self.map = map;
    }
}

impl std::fmt::Display for Homomorphism {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "homomorphism: {} --> {} : {:?}",
            self.domain.name(),
            self.range.name(),
            self.map
        )
    }
}

pub struct Closer {
    // TODO: Implement closer structure
}

pub struct Algebras {
    // TODO: Implement algebras collection
}

pub struct AlgebraFromMinimalSets {
    // TODO: Implement algebra from minimal sets
}

pub struct AlgebraWithGeneratingVector {
    // TODO: Implement algebra with generating vector
}

pub struct BigProductAlgebra {
    // TODO: Implement big product algebra
}

pub struct MatrixPowerAlgebra {
    // TODO: Implement matrix power algebra
}

pub struct ParameterizedAlgebra {
    // TODO: Implement parameterized algebra
}

pub struct PolinLikeAlgebra {
    // TODO: Implement Polin-like algebra
}

pub struct PowerAlgebra {
    // TODO: Implement power algebra
}

pub struct ReductAlgebra {
    // TODO: Implement reduct algebra
}

pub struct SubProductAlgebra {
    // TODO: Implement subproduct algebra
}

pub struct UnaryTermsMonoid {
    // TODO: Implement unary terms monoid
}

pub struct MaltsevDecompositionIterator {
    // TODO: Implement Maltsev decomposition iterator
}

pub struct MaltsevProductDecomposition {
    // TODO: Implement Maltsev product decomposition
}

pub struct Malcev {
    // TODO: Implement Malcev structure
}
