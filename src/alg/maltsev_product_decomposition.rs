use std::fmt::{Debug, Display};
use crate::alg::algebra::Algebra;
use crate::alg::small_algebra::SmallAlgebra;
use crate::alg::conlat::partition::Partition;
use crate::alg::quotient_algebra::QuotientAlgebra;
use crate::alg::subalgebra::Subalgebra;

/// A decomposition of an idempotent algebra into a quotient and block subalgebras.
/// 
/// This represents a Maltsev product decomposition where an idempotent algebra A
/// is decomposed relative to a congruence θ into:
/// - A quotient algebra A/θ
/// - Block subalgebras (one for each congruence block with more than one element)
/// 
/// This is useful for testing properties that are robust under Maltsev product
/// decomposition, where a property holds in A iff it holds in the quotient and
/// all block subalgebras.
/// 
/// # Examples
/// ```
/// use uacalc::alg::{MaltsevProductDecomposition, SmallAlgebra, BasicSmallAlgebra, Partition, Algebra};
/// use std::collections::HashSet;
/// 
/// // Create a simple algebra with 4 elements
/// let algebra = Box::new(BasicSmallAlgebra::new(
///     "A".to_string(),
///     HashSet::from([0, 1, 2, 3]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Create a congruence with blocks {0,1}, {2,3}
/// let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
/// 
/// // Create decomposition
/// let decomp = MaltsevProductDecomposition::new_safe(algebra, congruence).unwrap();
/// 
/// assert_eq!(decomp.get_quotient_algebra().cardinality(), 2);
/// assert_eq!(decomp.get_block_algebras().len(), 2); // Two blocks with >1 element
/// ```
#[derive(Debug)]
pub struct MaltsevProductDecomposition {
    /// The original algebra being decomposed
    pub algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    
    /// The congruence relation defining the decomposition
    pub congruence: Partition,
    
    /// The quotient algebra A/θ (stores QuotientAlgebra directly)
    pub quotient_algebra: QuotientAlgebra,
    
    /// Block subalgebras (one for each block with more than one element)
    pub block_algebras: Vec<Subalgebra<i32>>,
}

impl MaltsevProductDecomposition {
    /// Create a new Maltsev product decomposition.
    /// 
    /// # Arguments
    /// * `algebra` - The idempotent algebra to decompose
    /// * `congruence` - A congruence relation on the algebra
    /// 
    /// # Returns
    /// * `Ok(MaltsevProductDecomposition)` - Successfully created decomposition
    /// * `Err(String)` - If the algebra or congruence is invalid
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{MaltsevProductDecomposition, SmallAlgebra, BasicSmallAlgebra, Partition, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let algebra = Box::new(BasicSmallAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1, 2, 3]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
    /// let decomp = MaltsevProductDecomposition::new_safe(algebra, congruence).unwrap();
    /// 
    /// assert_eq!(decomp.cardinality(), 4);
    /// ```
    pub fn new_safe(
        algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        congruence: Partition,
    ) -> Result<Self, String> {
        // Validate that congruence size matches algebra cardinality
        let card = algebra.cardinality();
        if card < 0 {
            return Err("Cannot create decomposition for algebra with unknown cardinality".to_string());
        }
        
        if congruence.universe_size() != card as usize {
            return Err(format!(
                "Congruence size {} does not match algebra cardinality {}",
                congruence.universe_size(),
                card
            ));
        }
        
        // Create quotient algebra
        let quotient_algebra = QuotientAlgebra::new_safe(
            algebra.clone_box(),
            congruence.clone(),
        )?;
        
        // Create block subalgebras for blocks with more than one element
        let blocks = congruence.get_blocks();
        let mut block_algebras = Vec::new();
        
        for block in blocks {
            if block.len() > 1 {
                // Convert block indices from usize to i32
                let block_i32: Vec<i32> = block.iter().map(|&x| x as i32).collect();
                // Create subalgebra for this block
                let sub = Subalgebra::<i32>::new_safe(
                    format!("block_{}", block[0]),
                    algebra.clone_box(),
                    block_i32,
                )?;
                block_algebras.push(sub);
            }
        }
        
        Ok(MaltsevProductDecomposition {
            algebra,
            congruence,
            quotient_algebra,
            block_algebras,
        })
    }
    
    /// Create a new Maltsev product decomposition (panicking version).
    /// 
    /// # Arguments
    /// * `algebra` - The idempotent algebra to decompose
    /// * `congruence` - A congruence relation on the algebra
    /// 
    /// # Panics
    /// Panics if the algebra or congruence is invalid
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{MaltsevProductDecomposition, SmallAlgebra, BasicSmallAlgebra, Partition};
    /// use std::collections::HashSet;
    /// 
    /// let algebra = Box::new(BasicSmallAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1, 2, 3]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let congruence = Partition::new(vec![-2, 0, -2, 2]).unwrap();
    /// let decomp = MaltsevProductDecomposition::new(algebra, congruence);
    /// ```
    pub fn new(
        algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        congruence: Partition,
    ) -> Self {
        Self::new_safe(algebra, congruence).unwrap()
    }
    
    /// Get the congruence relation.
    /// 
    /// # Returns
    /// A reference to the congruence partition
    pub fn get_congruence(&self) -> &Partition {
        &self.congruence
    }
    
    /// Set the congruence relation.
    /// 
    /// # Arguments
    /// * `congruence` - The new congruence partition
    pub fn set_congruence(&mut self, congruence: Partition) {
        self.congruence = congruence;
    }
    
    /// Get the original algebra.
    /// 
    /// # Returns
    /// A reference to the algebra
    pub fn get_algebra(&self) -> &dyn SmallAlgebra<UniverseItem = i32> {
        self.algebra.as_ref()
    }
    
    /// Set the original algebra.
    /// 
    /// # Arguments
    /// * `algebra` - The new algebra
    pub fn set_algebra(&mut self, algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>) {
        self.algebra = algebra;
    }
    
    /// Get the block algebras.
    /// 
    /// # Returns
    /// A reference to the vector of block algebras
    pub fn get_block_algebras(&self) -> &Vec<Subalgebra<i32>> {
        &self.block_algebras
    }
    
    /// Set the block algebras.
    /// 
    /// # Arguments
    /// * `block_algebras` - The new block algebras
    pub fn set_block_algebras(&mut self, block_algebras: Vec<Subalgebra<i32>>) {
        self.block_algebras = block_algebras;
    }
    
    /// Get the quotient algebra.
    /// 
    /// # Returns
    /// A reference to the quotient algebra
    pub fn get_quotient_algebra(&self) -> &QuotientAlgebra {
        &self.quotient_algebra
    }
    
    /// Set the quotient algebra.
    /// 
    /// # Arguments
    /// * `quotient_algebra` - The new quotient algebra
    pub fn set_quotient_algebra(&mut self, quotient_algebra: QuotientAlgebra) {
        self.quotient_algebra = quotient_algebra;
    }
    
    /// Get the cardinality of the original algebra.
    /// 
    /// # Returns
    /// The cardinality
    pub fn cardinality(&self) -> i32 {
        self.algebra.cardinality()
    }
}

impl Display for MaltsevProductDecomposition {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "MaltsevProductDecomposition(algebra: {}, blocks: {}, quotient_card: {})",
            self.algebra.name(),
            self.block_algebras.len(),
            self.quotient_algebra.cardinality()
        )
    }
}
