/*! TypeFinder implementation.
 *
 * A utility class to find a subtrace {a, b} and its TCT type of a
 * covering beta/beta_* for some join irreducible congruence beta.
 * It is designed so that it can be reused for efficiency.
 */

use std::collections::HashSet;
use std::hash::Hash;
use std::fmt::{Debug, Display};

use crate::alg::{SmallAlgebra, BigProductAlgebra, Algebra};
use crate::alg::conlat::{CongruenceLattice, Partition, Subtrace};
use crate::alg::op::Operation;
use crate::util::int_array::{IntArray, IntArrayTrait};
use crate::util::sequence_generator::SequenceGenerator;
use crate::util::array_incrementor::ArrayIncrementor;

/// A utility class to find subtraces and TCT types in algebras.
/// 
/// TypeFinder is used to analyze Tame Congruence Theory (TCT) properties of algebras,
/// specifically for finding subtraces and determining their types for join irreducible
/// congruences.
/// 
/// The main part of the calculation is to take elements a and b of the algebra such that
/// Cg(a, b) is join irreducible, and a congruence alpha above the lower cover of Cg(a, b)
/// but not above Cg(a, b) and find c and d such that Cg(c, d) = Cg(a, b) and {c, d} is
/// a subtrace. Then it finds the type of this pair.
/// 
/// # Examples
/// ```
/// use uacalc::alg::{SmallAlgebra, BasicAlgebra};
/// use uacalc::alg::conlat::TypeFinder;
/// use std::collections::HashSet;
/// 
/// // Create a simple algebra
/// let alg = Box::new(BasicAlgebra::new(
///     "A".to_string(),
///     HashSet::from([0, 1, 2]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Create TypeFinder
/// let type_finder = TypeFinder::new(alg).unwrap();
/// assert_eq!(type_finder.alg_size(), 3);
/// ```
pub struct TypeFinder<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    /// The algebra being analyzed
    a: Box<dyn SmallAlgebra<UniverseItem = T>>,
    
    /// Product A^2
    a_squared: BigProductAlgebra<T>,
    
    /// Product A^4
    a_fourth: BigProductAlgebra<T>,
    
    /// Size of the algebra
    alg_size: i32,
    
    /// Congruence lattice of the algebra
    con: CongruenceLattice<T>,
    
    /// Visited pairs
    visited: HashSet<IntArray>,
    
    /// Current alpha partition
    alpha: Partition,
    
    /// Representatives of alpha blocks
    roots: Vec<i32>,
    
    /// Number of roots
    roots_size: usize,
    
    /// Diagonal set (pairs [r, r] for representatives r)
    diagonal_hs: HashSet<IntArray>,
    
    /// Diagonal list
    diagonal: Vec<IntArray>,
    
    /// Diagonal set in A^4
    diagonal4_hs: HashSet<IntArray>,
    
    /// Diagonal list in A^4
    diagonal4: Vec<IntArray>,
    
    /// Cached type set
    type_set: Option<HashSet<i32>>,
}

impl<T> TypeFinder<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static
{
    /// Create a new TypeFinder for the given algebra.
    /// 
    /// # Arguments
    /// * `alg` - The SmallAlgebra to analyze
    /// 
    /// # Returns
    /// * `Ok(TypeFinder)` - Successfully created TypeFinder
    /// * `Err(String)` - If initialization fails
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{SmallAlgebra, BasicAlgebra};
    /// use uacalc::alg::conlat::TypeFinder;
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let type_finder = TypeFinder::new(alg).unwrap();
    /// ```
    pub fn new(alg: Box<dyn SmallAlgebra<UniverseItem = T>>) -> Result<Self, String> {
        Self::new_with_alpha(alg, None)
    }
    
    /// Create a new TypeFinder with the given algebra and alpha partition.
    /// 
    /// # Arguments
    /// * `alg` - The SmallAlgebra to analyze
    /// * `alpha` - Optional initial alpha partition
    /// 
    /// # Returns
    /// * `Ok(TypeFinder)` - Successfully created TypeFinder
    /// * `Err(String)` - If initialization fails
    pub fn new_with_alpha(
        alg: Box<dyn SmallAlgebra<UniverseItem = T>>,
        alpha: Option<Partition>
    ) -> Result<Self, String> {
        let alg_size = alg.cardinality();
        let con = CongruenceLattice::new(alg.clone_box());
        
        let a_squared = BigProductAlgebra::new_power_safe(alg.clone_box(), 2)?;
        let a_fourth = BigProductAlgebra::new_power_safe(alg.clone_box(), 4)?;
        
        let visited = HashSet::new();
        let diagonal_hs = HashSet::new();
        let diagonal = Vec::new();
        let diagonal4_hs = HashSet::new();
        let diagonal4 = Vec::new();
        
        let init_alpha = alpha.unwrap_or_else(|| con.zero().clone());
        
        let mut type_finder = TypeFinder {
            a: alg,
            a_squared,
            a_fourth,
            alg_size,
            con,
            visited,
            alpha: init_alpha.clone(),
            roots: Vec::new(),
            roots_size: 0,
            diagonal_hs,
            diagonal,
            diagonal4_hs,
            diagonal4,
            type_set: None,
        };
        
        type_finder.set_alpha(init_alpha)?;
        
        Ok(type_finder)
    }
    
    /// Get the size of the algebra.
    pub fn alg_size(&self) -> i32 {
        self.alg_size
    }
    
    /// Initialize with the zero congruence.
    pub fn init(&mut self) -> Result<(), String> {
        let zero = self.con.zero().clone();
        self.init_with_alpha(zero)
    }
    
    /// Initialize with the given alpha partition.
    /// 
    /// # Arguments
    /// * `alpha` - The partition to use as alpha
    pub fn init_with_alpha(&mut self, alpha: Partition) -> Result<(), String> {
        self.set_alpha(alpha)
    }
    
    /// Set the alpha partition and update related structures.
    fn set_alpha(&mut self, alpha: Partition) -> Result<(), String> {
        if alpha == self.alpha {
            return Ok(());
        }
        
        self.visited.clear();
        self.alpha = alpha.clone();
        let reps = alpha.representatives();
        self.roots = reps.iter().map(|&x| x as i32).collect();
        self.roots_size = self.roots.len();
        
        self.diagonal.clear();
        self.diagonal4.clear();
        self.diagonal_hs.clear();
        self.diagonal4_hs.clear();
        
        for i in 0..self.roots_size {
            let r = self.roots[i];
            let tmp = IntArray::from_array(vec![r, r])?;
            let tmp2 = IntArray::from_array(vec![r, r, r, r])?;
            
            self.diagonal.push(tmp.clone());
            self.diagonal_hs.insert(tmp);
            self.diagonal4.push(tmp2.clone());
            self.diagonal4_hs.insert(tmp2);
        }
        
        Ok(())
    }
    
    /// Find the TCT type set of the algebra.
    /// 
    /// Returns the set of all types appearing in the join irreducibles of the
    /// congruence lattice.
    /// 
    /// # Returns
    /// Set of TCT types (integers 1-5)
    pub fn find_type_set(&mut self) -> Result<HashSet<i32>, String> {
        if let Some(ref ts) = self.type_set {
            return Ok(ts.clone());
        }
        
        let mut type_set = HashSet::new();
        let join_irr = self.con.join_irreducibles().to_vec();
        
        for par in &join_irr {
            let typ = self.find_type(par)?;
            type_set.insert(typ);
        }
        
        self.type_set = Some(type_set.clone());
        Ok(type_set)
    }
    
    /// Test if the given pair is a beta subtrace.
    /// 
    /// # Arguments
    /// * `ia` - The pair to test
    /// * `beta` - The beta partition (must be join irreducible)
    /// 
    /// # Returns
    /// * `Ok(true)` - If the pair is a subtrace
    /// * `Ok(false)` - If the pair is not a subtrace
    /// * `Err(String)` - If beta is not join irreducible or other error
    pub fn is_subtrace(&mut self, ia: &IntArray, beta: &Partition) -> Result<bool, String> {
        let beta_star = self.con.lower_star(beta)
            .ok_or_else(|| format!("beta = {} is not join irreducible", beta))?;
        
        let joined_alpha = self.alpha.join(&beta_star)?;
        if beta.leq(&joined_alpha) {
            return Err("beta is below its lower cover join alpha".to_string());
        }
        
        self.set_alpha(joined_alpha)?;
        let subtrace = self.find_subtrace_from_pair(ia)?;
        
        Ok(subtrace.get_subtrace_universe()
            .map(|univ| univ.iter().any(|elem| elem == ia))
            .unwrap_or(false))
    }
    
    /// Find a subtrace for beta over its lower cover.
    /// 
    /// # Arguments
    /// * `beta` - The join irreducible congruence
    /// 
    /// # Returns
    /// The Subtrace for this beta
    pub fn find_subtrace(&mut self, beta: &Partition) -> Result<Subtrace, String> {
        let beta_star = self.con.lower_star(beta)
            .ok_or_else(|| format!("beta = {} is not join irreducible", beta))?;
        self.find_subtrace_with_alpha(beta, &beta_star)
    }
    
    /// Find a subtrace for beta with the given alpha.
    /// 
    /// # Arguments
    /// * `beta` - The join irreducible congruence
    /// * `alpha` - A congruence whose join with the lower cover of beta is not above beta
    /// 
    /// # Returns
    /// The Subtrace for this beta/alpha pair
    pub fn find_subtrace_with_alpha(
        &mut self,
        beta: &Partition,
        alpha: &Partition
    ) -> Result<Subtrace, String> {
        let beta_star = self.con.lower_star(beta)
            .ok_or_else(|| format!("beta = {} is not join irreducible", beta))?;
        
        let joined_alpha = alpha.join(&beta_star)?;
        if beta.leq(&joined_alpha) {
            return Err("beta is below its lower cover join alpha".to_string());
        }
        
        self.set_alpha(joined_alpha)?;
        let gen_pair = self.con.generating_pair(beta)
            .ok_or_else(|| format!("No generating pair found for beta"))?;
        self.find_subtrace_from_pair(&gen_pair)
    }
    
    /// Find a subtrace starting from the given pair.
    /// 
    /// This looks at the image of the ordered pair under Pol_1(A). If this image
    /// has not been visited in a previous call, this call is abandoned and a
    /// recursive call is made on the image pair. Otherwise it builds up Pol_1(A)
    /// restricted to the pair.
    /// 
    /// # Arguments
    /// * `pair_ia` - The initial pair to start from
    /// 
    /// # Returns
    /// The Subtrace found
    pub fn find_subtrace_from_pair(&mut self, pair_ia: &IntArray) -> Result<Subtrace, String> {
        let mut univ_hs = HashSet::new();
        let mut unordered_univ_hs = HashSet::new();
        let mut old_pair = pair_ia.clone();
        let mut univ = Vec::new();
        let mut current_pair = pair_ia.clone();
        
        loop {
            old_pair = current_pair.clone();
            univ.clear();
            
            match self.next_pair_for_subtrace(&current_pair, &mut univ_hs, &mut unordered_univ_hs, &mut univ)? {
                Some(next_pair) => {
                    current_pair = next_pair;
                }
                None => break,
            }
        }
        
        let a = old_pair.get(0).ok_or_else(|| "Invalid pair: missing first element".to_string())?;
        let b = old_pair.get(1).ok_or_else(|| "Invalid pair: missing second element".to_string())?;
        let reverse_pair = IntArray::from_array(vec![b, a])?;
        let has_involution = univ_hs.contains(&reverse_pair);
        
        let mut subtrace = Subtrace::new(a, b, has_involution);
        subtrace.set_subtrace_universe(univ);
        
        Ok(subtrace)
    }
    
    /// Look for another pair in the subalgebra of A^2 generated by the given pair
    /// and the constants.
    /// 
    /// Returns the next unvisited pair, or None if there is none (which implies
    /// the original pair is a subtrace).
    /// 
    /// # Arguments
    /// * `pair` - The current pair
    /// * `univ_hs` - HashSet of visited pairs
    /// * `unordered_univ_hs` - HashSet of unordered pairs
    /// * `univ` - List of pairs in the universe
    /// 
    /// # Returns
    /// * `Some(IntArray)` - The next pair to process
    /// * `None` - If no unvisited pair found (pair is a subtrace)
    pub fn next_pair_for_subtrace(
        &self,
        pair: &IntArray,
        univ_hs: &mut HashSet<IntArray>,
        unordered_univ_hs: &mut HashSet<IntArray>,
        univ: &mut Vec<IntArray>
    ) -> Result<Option<IntArray>, String> {
        univ_hs.clear();
        univ.push(pair.clone());
        
        for i in 0..self.alg_size {
            univ.push(IntArray::from_array(vec![i, i])?);
        }
        
        for elem in univ.iter() {
            univ_hs.insert(elem.clone());
        }
        
        let mut closed_mark = 0;
        let mut current_mark = univ.len();
        
        while closed_mark < current_mark {
            let ops = self.a_squared.operations();
            
            for f in &ops {
                let arity = f.arity();
                if arity == 0 {
                    continue;
                }
                
                let mut arg_indices = vec![0_i32; arity as usize];
                arg_indices[(arity - 1) as usize] = closed_mark as i32;
                
                let mut inc = SequenceGenerator::sequence_incrementor(
                    &mut arg_indices,
                    (current_mark - 1) as i32
                );
                
                loop {
                    let current_indices = inc.get_current();
                    let mut arg = vec![Vec::new(); arity as usize];
                    
                    for j in 0..arity as usize {
                        let idx = current_indices[j] as usize;
                        let elem = &univ[idx];
                        // Convert IntArray to Vec<i32>
                        let mut vec = Vec::new();
                        for k in 0..elem.universe_size() {
                            vec.push(elem.get(k).unwrap_or(0));
                        }
                        arg[j] = vec;
                    }
                    
                    let arg_ref: Vec<&[i32]> = arg.iter().map(|v| v.as_slice()).collect();
                    let v_raw = f.value_at_arrays(&arg_ref)?;
                    let v = IntArray::from_array(v_raw)?;
                    
                    let v0 = v.get(0).ok_or_else(|| "Invalid result: missing first element".to_string())?;
                    let v1 = v.get(1).ok_or_else(|| "Invalid result: missing second element".to_string())?;
                    
                    if !self.alpha.is_related(v0 as usize, v1 as usize) {
                        let v_unordered = if v0 < v1 {
                            IntArray::from_array(vec![v0, v1])?
                        } else {
                            IntArray::from_array(vec![v1, v0])?
                        };
                        
                        if unordered_univ_hs.insert(v_unordered) {
                            // v is new; start over with it
                            return Ok(Some(v));
                        }
                    }
                    
                    if univ_hs.insert(v.clone()) {
                        univ.push(v);
                    }
                    
                    if !inc.increment() {
                        break;
                    }
                }
            }
            
            closed_mark = current_mark;
            current_mark = univ.len();
        }
        
        Ok(None)
    }
    
    /// Find the type for beta over its lower cover.
    /// 
    /// # Arguments
    /// * `beta` - The join irreducible congruence
    /// 
    /// # Returns
    /// The TCT type (1-5)
    pub fn find_type(&mut self, beta: &Partition) -> Result<i32, String> {
        let beta_star = self.con.lower_star(beta)
            .ok_or_else(|| format!("beta = {} is not join irreducible", beta))?;
        self.find_type_with_alpha(beta, &beta_star)
    }
    
    /// Find the type for beta with the given alpha.
    /// 
    /// # Arguments
    /// * `beta` - The join irreducible congruence
    /// * `alpha` - A congruence whose join with the lower cover of beta is not above beta
    /// 
    /// # Returns
    /// The TCT type (1-5)
    pub fn find_type_with_alpha(
        &mut self,
        beta: &Partition,
        alpha: &Partition
    ) -> Result<i32, String> {
        let beta_star = self.con.lower_star(beta)
            .ok_or_else(|| format!("beta = {} is not join irreducible", beta))?;
        
        let joined_alpha = alpha.join(&beta_star)?;
        if beta.leq(&joined_alpha) {
            return Err("beta is below its lower cover join alpha".to_string());
        }
        
        self.set_alpha(joined_alpha)?;
        let gen_pair = self.con.generating_pair(beta)
            .ok_or_else(|| format!("No generating pair found for beta"))?;
        let subtrace = self.find_subtrace_from_pair(&gen_pair)?;
        self.find_type_from_subtrace(subtrace)
    }
    
    /// Find the type of a subtrace.
    /// 
    /// Let [c,d] be the subtrace. We think of quadruples as maps from {c,d}^2
    /// into A in row order: (c,c), (c,d), (d,c), (d,d). So the projections are
    /// [c,c,d,d] and [c,d,c,d].
    /// 
    /// # Arguments
    /// * `mut subtrace` - The subtrace to analyze (will be modified with type and universe)
    /// 
    /// # Returns
    /// The TCT type (1-5)
    pub fn find_type_from_subtrace(&self, mut subtrace: Subtrace) -> Result<i32, String> {
        let c = subtrace.first();
        let d = subtrace.second();
        
        let mut meet = false;
        let mut join = false;
        let mut one_snag = false;
        
        let mut universe = Vec::new();
        universe.extend_from_slice(&self.diagonal4);
        let mut univ_hash_set = HashSet::new();
        for elem in &universe {
            univ_hash_set.insert(elem.clone());
        }
        
        let rows = IntArray::from_array(vec![c, c, d, d])?;
        let cols = IntArray::from_array(vec![c, d, c, d])?;
        universe.push(rows.clone());
        universe.push(cols.clone());
        univ_hash_set.insert(rows);
        univ_hash_set.insert(cols);
        
        let mut closed_mark = 0;
        let mut current_mark = universe.len();
        
        while closed_mark < current_mark {
            let ops = self.a_fourth.operations();
            
            for f in &ops {
                let arity = f.arity();
                if arity == 0 {
                    continue;
                }
                
                let mut arg_indices = vec![0_i32; arity as usize];
                arg_indices[(arity - 1) as usize] = closed_mark as i32;
                
                let mut inc = SequenceGenerator::sequence_incrementor(
                    &mut arg_indices,
                    (current_mark - 1) as i32
                );
                
                loop {
                    let current_indices = inc.get_current();
                    let mut arg = vec![Vec::new(); arity as usize];
                    
                    for j in 0..arity as usize {
                        let idx = current_indices[j] as usize;
                        let elem = &universe[idx];
                        // Convert IntArray to Vec<i32>
                        let mut vec = Vec::new();
                        for k in 0..elem.universe_size() {
                            vec.push(elem.get(k).unwrap_or(0));
                        }
                        arg[j] = vec;
                    }
                    
                    let arg_ref: Vec<&[i32]> = arg.iter().map(|v| v.as_slice()).collect();
                    let v_raw = f.value_at_arrays(&arg_ref)?;
                    let vec = IntArray::from_array(v_raw.clone())?;
                    
                    if !univ_hash_set.insert(vec.clone()) {
                        if !inc.increment() {
                            break;
                        }
                        continue;
                    }
                    
                    universe.push(vec);
                    
                    // Check type based on v_raw mod alpha
                    let mut v_raw_mod_alpha = vec![0; 4];
                    for i in 0..4 {
                        v_raw_mod_alpha[i] = self.alpha.representative(v_raw[i] as usize) as i32;
                    }
                    
                    let x = v_raw_mod_alpha[0];
                    let y = v_raw_mod_alpha[1];
                    let u = v_raw_mod_alpha[2];
                    let v = v_raw_mod_alpha[3];
                    
                    // Check for join
                    if !join && (((x != y) && (u == v)) || ((x != u) && (y == v))) {
                        if subtrace.has_involution() {
                            subtrace.set_matrix_universe(universe);
                            subtrace.set_type(3);
                            return Ok(3);
                        }
                        if meet {
                            subtrace.set_matrix_universe(universe);
                            subtrace.set_type(4);
                            return Ok(4);
                        }
                        join = true;
                        one_snag = true;
                    } else if !meet && (((x == y) && (u != v)) || ((x == u) && (y != v))) {
                        // Check for meet
                        if subtrace.has_involution() {
                            subtrace.set_type(3);
                            return Ok(3);
                        }
                        if join {
                            subtrace.set_matrix_universe(universe);
                            subtrace.set_type(4);
                            return Ok(4);
                        }
                        meet = true;
                        one_snag = true;
                    }
                    
                    // Check for other one-snag
                    if !one_snag {
                        if ((x == v) && ((x != y) || (u != v))) || ((y == u) && ((x != y) || (u != v))) {
                            one_snag = true;
                        }
                    }
                    
                    if !inc.increment() {
                        break;
                    }
                }
            }
            
            closed_mark = current_mark;
            current_mark = universe.len();
        }
        
        subtrace.set_matrix_universe(universe.clone());
        
        if join || meet {
            subtrace.set_type(5);
            Ok(5)
        } else if one_snag {
            subtrace.set_type(2);
            Ok(2)
        } else {
            subtrace.set_type(1);
            Ok(1)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::{BasicAlgebra};
    use std::collections::HashSet;
    
    #[test]
    fn test_new() {
        let alg = Box::new(BasicAlgebra::new(
            "A".to_string(),
            HashSet::from([0, 1, 2]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let type_finder = TypeFinder::new(alg).unwrap();
        assert_eq!(type_finder.alg_size(), 3);
    }
    
    #[test]
    fn test_init() {
        let alg = Box::new(BasicAlgebra::new(
            "A".to_string(),
            HashSet::from([0, 1]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let mut type_finder = TypeFinder::new(alg).unwrap();
        assert!(type_finder.init().is_ok());
    }
}
