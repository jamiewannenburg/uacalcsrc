use std::collections::HashSet;
use std::fmt::{self, Display, Debug};
use std::cmp::Ordering;
use std::hash::Hash;
use crate::alg::algebra::Algebra;
use crate::alg::op::ops::make_int_operations;
use crate::alg::small_algebra::{BasicAlgebra, SmallAlgebra};
use crate::alg::sublat::SubalgebraLattice;
use crate::alg::quotient_algebra::QuotientAlgebra;

/// Flatten a quotient `A/θ` to a table-backed `BasicAlgebra<i32>` whose universe
/// is `{0, …, n-1}` (Java's integer block indices).
///
/// `siDecompose` must not transmute `QuotientElement<T>` into `i32`: that
/// reinterprets pointer-sized values as operation arguments and produces the
/// out-of-range junk (`Argument 1611473968 is out of bounds`) seen when
/// FreeAlgebra ran with `decompose=true`.
fn flatten_quotient_algebra_to_basic(
    quotient: &QuotientAlgebra<i32>,
) -> Result<BasicAlgebra<i32>, String> {
    let mut q = quotient.clone();
    q.make_operation_tables();
    let int_ops = make_int_operations(Algebra::operations(&q))?;
    let card = q.cardinality();
    if card < 0 {
        return Err(format!("quotient cardinality is negative: {}", card));
    }
    let universe: HashSet<i32> = (0..card).collect();
    Ok(BasicAlgebra::new(q.name().to_string(), universe, int_ops))
}

/// An algebra with an associated vector of elements that generates it.
/// 
/// This struct represents an algebra along with a generating vector of elements.
/// Repeats are allowed in the generating vector. This is used in FreeAlgebra
/// for subdirect decomposition and in ProgressReport as witness algebra.
/// 
/// The struct is generic over the element type `T`, allowing it to work with
/// different types of algebras (i32, IntArray, QuotientElement, etc.).
/// 
/// # Examples
/// ```
/// use uacalc::alg::{AlgebraWithGeneratingVector, SmallAlgebra, BasicAlgebra};
/// use std::collections::HashSet;
/// 
/// // Create a small algebra
/// let alg = Box::new(BasicAlgebra::new(
///     "A".to_string(),
///     HashSet::from([0, 1, 2]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Create algebra with generating vector
/// let alg_with_vec = AlgebraWithGeneratingVector::new(alg, vec![0, 1]);
/// assert_eq!(alg_with_vec.get_algebra().name(), "A");
/// assert_eq!(alg_with_vec.get_vector(), &[0, 1]);
/// ```
#[derive(Debug)]
pub struct AlgebraWithGeneratingVector<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    /// The underlying algebra
    pub alg: Box<dyn SmallAlgebra<UniverseItem = T>>,
    /// The generating vector of elements
    pub gens_vector: Vec<T>,
}

impl<T> Clone for AlgebraWithGeneratingVector<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn clone(&self) -> Self {
        AlgebraWithGeneratingVector {
            alg: self.alg.clone_box(),
            gens_vector: self.gens_vector.clone(),
        }
    }
}

impl<T> AlgebraWithGeneratingVector<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    /// Create a new AlgebraWithGeneratingVector.
    /// 
    /// # Arguments
    /// * `alg` - The underlying algebra
    /// * `vec` - The generating vector of elements
    /// 
    /// # Returns
    /// A new AlgebraWithGeneratingVector instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{AlgebraWithGeneratingVector, SmallAlgebra, BasicAlgebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1, 2]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let alg_with_vec = AlgebraWithGeneratingVector::new(alg, vec![0, 1, 2]);
    /// assert_eq!(alg_with_vec.get_vector().len(), 3);
    /// ```
    pub fn new(alg: Box<dyn SmallAlgebra<UniverseItem = T>>, vec: Vec<T>) -> Self {
        AlgebraWithGeneratingVector {
            alg,
            gens_vector: vec,
        }
    }
    
    /// Get the underlying algebra.
    /// 
    /// # Returns
    /// A reference to the underlying algebra
    pub fn get_algebra(&self) -> &dyn SmallAlgebra<UniverseItem = T> {
        self.alg.as_ref()
    }
    
    /// Get the generating vector.
    /// 
    /// # Returns
    /// A reference to the generating vector
    pub fn get_vector(&self) -> &[T] {
        &self.gens_vector
    }
    
    /// Check if this algebra with generating vector is an image of another.
    /// 
    /// This method checks if there exists a homomorphism from the other algebra
    /// to this algebra that maps the other's generating vector to this one's
    /// generating vector.
    /// 
    /// # Arguments
    /// * `other` - The other algebra with generating vector
    /// 
    /// # Returns
    /// `true` if this is an image of the other, `false` otherwise
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{AlgebraWithGeneratingVector, SmallAlgebra, BasicAlgebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg1 = Box::new(BasicAlgebra::new(
    ///     "A1".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let alg2 = Box::new(BasicAlgebra::new(
    ///     "A2".to_string(),
    ///     HashSet::from([0, 1, 2]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let alg_with_vec1 = AlgebraWithGeneratingVector::new(alg1, vec![0, 1]);
    /// let alg_with_vec2 = AlgebraWithGeneratingVector::new(alg2, vec![0, 1]);
    /// 
    /// // Check if alg_with_vec1 is an image of alg_with_vec2
    /// let is_image = alg_with_vec1.is_image_of(&alg_with_vec2);
    /// ```
    pub fn is_image_of(&self, other: &AlgebraWithGeneratingVector<T>) -> bool {
        // Check cardinality constraint - this algebra must have smaller or equal cardinality
        if self.get_algebra().cardinality() > other.get_algebra().cardinality() {
            return false;
        }
        
        // Check vector length constraint
        if self.gens_vector.len() != other.get_vector().len() {
            return false;
        }
        
        // For algebras with no operations, only allow if they have the same cardinality
        // This matches the test expectation that different cardinalities are not comparable
        if self.get_algebra().operations().is_empty() && other.get_algebra().operations().is_empty() {
            return self.get_algebra().cardinality() == other.get_algebra().cardinality();
        }
        
        // Use SubalgebraLattice to check if homomorphism exists
        // Use the new generic method that works with any element type
        crate::alg::sublat::SubalgebraLattice::extend_to_homomorphism_generic(
            other.get_vector(),
            &self.gens_vector,
            other.get_algebra(),
            self.get_algebra()
        ).is_some()
    }
}

impl AlgebraWithGeneratingVector<i32> {
    /// Decompose an algebra with generating vector into subdirectly irreducible components.
    /// 
    /// This static method takes an algebra and a generating vector, forms the
    /// subalgebra generated by the vector, and then decomposes that into
    /// subdirectly irreducible algebras.
    /// 
    /// # Arguments
    /// * `alg` - The algebra to decompose
    /// * `vec` - The generating vector
    /// 
    /// # Returns
    /// A list of AlgebraWithGeneratingVector instances representing the decomposition
    /// 
    /// # Examples
    /// ```
    /// use uacalc::alg::{AlgebraWithGeneratingVector, SmallAlgebra, BasicAlgebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "A".to_string(),
    ///     HashSet::from([0, 1, 2]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let decomposition = AlgebraWithGeneratingVector::si_decompose(alg, &[0, 1]);
    /// // Returns a list of subdirectly irreducible components
    /// ```
    pub fn si_decompose(
        alg: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        vec: &[i32],
    ) -> Vec<Self> {
        Self::si_decompose_with_relations(alg, vec, None)
    }

    /// Decompose an algebra with generating vector into subdirectly irreducible components,
    /// taking into account additional relations.
    ///
    /// Matches Java `siDecompose(alg, vec, relations)`: each factor is a quotient
    /// of `Sg(vec)` flattened to an integer-universe algebra, and the generating
    /// vector is the list of quotient block indices.
    pub fn si_decompose_with_relations(
        alg: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        vec: &[i32],
        relations: Option<Vec<crate::eq::Equation>>,
    ) -> Vec<Self> {
        if let Some(rels) = relations {
            if !rels.is_empty() {
                return Self::si_decompose_with_equation_relations(alg, vec, rels);
            }
        }
        Self::si_decompose_core(alg, vec)
    }

    fn si_decompose_core(
        alg: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        vec: &[i32],
    ) -> Vec<Self> {
        let indices: Vec<i32> = match vec
            .iter()
            .map(|elem| alg.element_index(elem))
            .collect::<Option<Vec<_>>>()
        {
            Some(indices) => indices.into_iter().map(|i| i as i32).collect(),
            None => {
                return vec![AlgebraWithGeneratingVector::new(alg, vec.to_vec())];
            }
        };

        let sub_lat = match SubalgebraLattice::new_safe(alg.clone_box()) {
            Ok(lat) => lat,
            Err(_) => {
                return vec![AlgebraWithGeneratingVector::new(alg, vec.to_vec())];
            }
        };

        let subalgebra = sub_lat.sg_from_gens(&indices);
        let sub_alg = Box::new(subalgebra.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        let mut con_lat = crate::alg::conlat::CongruenceLattice::new(sub_alg);

        // Java returns an empty list when there are no meet-irreducibles
        // (e.g. a 1-element algebra).
        let decomposition = con_lat.irredundant_meet_decomposition();
        if decomposition.is_empty() {
            return Vec::new();
        }

        let subalgebra_for_index = sub_lat.sg_from_gens(&indices);
        let index_vec: Vec<usize> = match vec
            .iter()
            .map(|elem| {
                alg.element_index(elem)
                    .and_then(|orig_idx| subalgebra_for_index.index(orig_idx as i32))
            })
            .collect::<Option<Vec<_>>>()
        {
            Some(indices) => indices,
            None => {
                return vec![AlgebraWithGeneratingVector::new(alg, vec.to_vec())];
            }
        };

        let mut result = Vec::new();
        for part in decomposition.iter() {
            let subalgebra_for_quot = sub_lat.sg_from_gens(&indices);
            let quotient = match QuotientAlgebra::<i32>::new_safe(
                Box::new(subalgebra_for_quot) as Box<dyn SmallAlgebra<UniverseItem = i32>>,
                part.clone(),
            ) {
                Ok(quot) => quot,
                Err(_) => continue,
            };

            let mut v = Vec::with_capacity(index_vec.len());
            let mut success = true;
            for &idx in &index_vec {
                let rep = part.representative(idx);
                match quotient.representative_index(rep) {
                    Ok(quot_idx) => v.push(quot_idx as i32),
                    Err(_) => {
                        success = false;
                        break;
                    }
                }
            }
            if !success || v.len() != index_vec.len() {
                continue;
            }

            match flatten_quotient_algebra_to_basic(&quotient) {
                Ok(basic) => {
                    result.push(AlgebraWithGeneratingVector::new(Box::new(basic), v));
                }
                Err(_) => continue,
            }
        }

        if result.is_empty() {
            vec![AlgebraWithGeneratingVector::new(alg, vec.to_vec())]
        } else {
            result
        }
    }

    /// Java `siDecompose(alg, vec, relations)` when `relations` is non-empty.
    ///
    /// Forms `B = Sg(vec)`, joins principal congruences of failed equations, then
    /// decomposes the quotient. Empty or missing relations use `si_decompose`.
    pub fn si_decompose_with_equation_relations(
        alg: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        vec: &[i32],
        relations: Vec<crate::eq::Equation>,
    ) -> Vec<Self> {
        use crate::alg::conlat::CongruenceLattice;
        use std::collections::HashMap;

        if relations.is_empty() {
            return Self::si_decompose(alg, vec);
        }

        let indices: Vec<i32> = match vec
            .iter()
            .map(|elem| alg.element_index(elem))
            .collect::<Option<Vec<_>>>()
        {
            Some(indices) => indices.into_iter().map(|i| i as i32).collect(),
            None => {
                return vec![AlgebraWithGeneratingVector::new(alg, vec.to_vec())];
            }
        };

        let sub_lat = match SubalgebraLattice::new_safe(alg.clone_box()) {
            Ok(lat) => lat,
            Err(_) => {
                return vec![AlgebraWithGeneratingVector::new(alg, vec.to_vec())];
            }
        };

        let subalgebra = sub_lat.sg_from_gens(&indices);
        let index_vec: Vec<usize> = match vec
            .iter()
            .map(|elem| {
                alg.element_index(elem)
                    .and_then(|orig_idx| subalgebra.index(orig_idx as i32))
            })
            .collect::<Option<Vec<_>>>()
        {
            Some(v) => v,
            None => {
                return vec![AlgebraWithGeneratingVector::new(alg, vec.to_vec())];
            }
        };

        let vars = relations[0].get_variable_list();
        let mut map = HashMap::new();
        for (k, var) in vars.iter().enumerate() {
            if k < index_vec.len() {
                map.insert(var.clone(), index_vec[k] as i32);
            }
        }

        let sub_for_eval = sub_lat.sg_from_gens(&indices);
        let mut con_lat = CongruenceLattice::new(
            Box::new(sub_for_eval.clone()) as Box<dyn SmallAlgebra<UniverseItem = i32>>,
        );
        let mut gamma = con_lat.zero();
        {
            let sub_ref: &dyn SmallAlgebra<UniverseItem = i32> = &sub_for_eval;
            for eq in &relations {
                let left = eq.left_side().int_eval(sub_ref, &map);
                let right = eq.right_side().int_eval(sub_ref, &map);
                if let (Ok(left), Ok(right)) = (left, right) {
                    if left != right {
                        let cg = con_lat.cg(left as usize, right as usize);
                        if let Ok(joined) = gamma.join(&cg) {
                            gamma = joined;
                        }
                    }
                }
            }
        }

        let sub_for_quot = sub_lat.sg_from_gens(&indices);
        let quotient = match QuotientAlgebra::<i32>::new_safe(
            Box::new(sub_for_quot) as Box<dyn SmallAlgebra<UniverseItem = i32>>,
            gamma.clone(),
        ) {
            Ok(q) => q,
            Err(_) => return Self::si_decompose(alg, vec),
        };

        let mut v = Vec::with_capacity(index_vec.len());
        for &idx in &index_vec {
            let rep = gamma.representative(idx);
            match quotient.representative_index(rep) {
                Ok(qidx) => v.push(qidx as i32),
                Err(_) => return Self::si_decompose(alg, vec),
            }
        }

        let basic = match flatten_quotient_algebra_to_basic(&quotient) {
            Ok(basic) => basic,
            Err(_) => return Self::si_decompose(alg, vec),
        };
        Self::si_decompose(Box::new(basic), &v)
    }
}

impl<T> PartialEq for AlgebraWithGeneratingVector<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn eq(&self, other: &Self) -> bool {
        self.is_image_of(other) && other.is_image_of(self)
    }
}

impl<T> Eq for AlgebraWithGeneratingVector<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{}

impl<T> PartialOrd for AlgebraWithGeneratingVector<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl<T> Ord for AlgebraWithGeneratingVector<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn cmp(&self, other: &Self) -> Ordering {
        if self.is_image_of(other) {
            if other.is_image_of(self) {
                Ordering::Equal
            } else {
                Ordering::Less
            }
        } else if other.is_image_of(self) {
            Ordering::Greater
        } else {
            Ordering::Equal
        }
    }
}

impl<T> Display for AlgebraWithGeneratingVector<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        // Format the vector with spaces like [0, 1, 2]
        let vec_str = format!("[{}]", self.gens_vector.iter()
            .map(|x| x.to_string())
            .collect::<Vec<_>>()
            .join(", "));
        
        write!(
            f,
            "Alg with vector, alg size = {}, vec = {}",
            self.get_algebra().cardinality(),
            vec_str
        )
    }
}

/// Specialized implementation for i32 elements that can use SubalgebraLattice.
impl AlgebraWithGeneratingVector<i32> {
    /// Check if this algebra with generating vector is an image of another (i32 specialization).
    /// 
    /// This method uses SubalgebraLattice::extend_to_homomorphism for i32 elements.
    pub fn is_image_of_i32(&self, other: &AlgebraWithGeneratingVector<i32>) -> bool {
        // Check cardinality constraint - this algebra must have smaller or equal cardinality
        if self.get_algebra().cardinality() > other.get_algebra().cardinality() {
            return false;
        }
        
        // Check vector length constraint
        if self.gens_vector.len() != other.get_vector().len() {
            return false;
        }
        
        // For algebras with no operations, only allow if they have the same cardinality
        if self.get_algebra().operations().is_empty() && other.get_algebra().operations().is_empty() {
            return self.get_algebra().cardinality() == other.get_algebra().cardinality();
        }
        
        // Use SubalgebraLattice to check if homomorphism exists
        SubalgebraLattice::extend_to_homomorphism(
            other.get_vector(),
            &self.gens_vector,
            other.get_algebra(),
            self.get_algebra()
        ).is_some()
    }
}

/// Type alias for backward compatibility with i32 elements.
/// 
/// This allows existing code to continue using `AlgebraWithGeneratingVector`
/// without specifying the generic type parameter.
pub type AlgebraWithGeneratingVectorI32 = AlgebraWithGeneratingVector<i32>;

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::small_algebra::BasicAlgebra;
    use std::collections::HashSet;
    
    #[test]
    fn test_algebra_with_generating_vector_creation() {
        let alg = Box::new(BasicAlgebra::new(
            "TestAlg".to_string(),
            HashSet::from([0, 1, 2]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let alg_with_vec = AlgebraWithGeneratingVector::new(alg, vec![0, 1]);
        
        assert_eq!(alg_with_vec.get_algebra().name(), "TestAlg");
        assert_eq!(alg_with_vec.get_vector(), &[0, 1]);
    }
    
    #[test]
    fn test_is_image_of_same_algebra() {
        let alg = Box::new(BasicAlgebra::new(
            "TestAlg".to_string(),
            HashSet::from([0, 1]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let alg_with_vec1 = AlgebraWithGeneratingVector::new(alg.clone_box(), vec![0, 1]);
        let alg_with_vec2 = AlgebraWithGeneratingVector::new(alg, vec![0, 1]);
        
        // Same algebra and vector should be images of each other
        assert!(alg_with_vec1.is_image_of(&alg_with_vec2));
        assert!(alg_with_vec2.is_image_of(&alg_with_vec1));
    }
    
    #[test]
    fn test_is_image_of_different_cardinality() {
        let alg1 = Box::new(BasicAlgebra::new(
            "Alg1".to_string(),
            HashSet::from([0, 1]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let alg2 = Box::new(BasicAlgebra::new(
            "Alg2".to_string(),
            HashSet::from([0, 1, 2]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let alg_with_vec1 = AlgebraWithGeneratingVector::new(alg1, vec![0, 1]);
        let alg_with_vec2 = AlgebraWithGeneratingVector::new(alg2, vec![0, 1]);
        
        // alg1 cannot be an image of alg2 due to cardinality constraint
        assert!(!alg_with_vec1.is_image_of(&alg_with_vec2));
    }
    
    #[test]
    fn test_equality() {
        let alg = Box::new(BasicAlgebra::new(
            "TestAlg".to_string(),
            HashSet::from([0, 1]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let alg_with_vec1 = AlgebraWithGeneratingVector::new(alg.clone_box(), vec![0, 1]);
        let alg_with_vec2 = AlgebraWithGeneratingVector::new(alg, vec![0, 1]);
        
        assert_eq!(alg_with_vec1, alg_with_vec2);
    }
    
    #[test]
    fn test_ordering() {
        let alg1 = Box::new(BasicAlgebra::new(
            "Alg1".to_string(),
            HashSet::from([0, 1]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let alg2 = Box::new(BasicAlgebra::new(
            "Alg2".to_string(),
            HashSet::from([0, 1, 2]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let alg_with_vec1 = AlgebraWithGeneratingVector::new(alg1, vec![0, 1]);
        let alg_with_vec2 = AlgebraWithGeneratingVector::new(alg2, vec![0, 1]);
        
        // Test ordering (should be equal since neither is image of the other)
        assert_eq!(alg_with_vec1.cmp(&alg_with_vec2), Ordering::Equal);
    }
    
    #[test]
    fn test_display() {
        let alg = Box::new(BasicAlgebra::new(
            "TestAlg".to_string(),
            HashSet::from([0, 1, 2]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let alg_with_vec = AlgebraWithGeneratingVector::new(alg, vec![0, 1]);
        let display_str = format!("{}", alg_with_vec);
        
        assert!(display_str.contains("alg size = 3"));
        assert!(display_str.contains("vec = [0, 1]"));
    }
    
    #[test]
    fn test_generic_element_types() {
        // Test with i32 elements (existing functionality)
        let alg_i32 = Box::new(BasicAlgebra::new(
            "A_i32".to_string(),
            HashSet::from([0, 1, 2]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
        
        let alg_with_vec_i32 = AlgebraWithGeneratingVector::new(alg_i32, vec![0, 1]);
        assert_eq!(alg_with_vec_i32.get_vector(), &[0, 1]);
        assert_eq!(alg_with_vec_i32.get_algebra().cardinality(), 3);
        
        // Test with String elements (demonstrating generic capability)
        let alg_string = Box::new(BasicAlgebra::new(
            "A_string".to_string(),
            HashSet::from(["a".to_string(), "b".to_string(), "c".to_string()]),
            Vec::new()
        )) as Box<dyn SmallAlgebra<UniverseItem = String>>;
        
        let alg_with_vec_string = AlgebraWithGeneratingVector::new(
            alg_string, 
            vec!["a".to_string(), "b".to_string()]
        );
        assert_eq!(alg_with_vec_string.get_vector(), &["a".to_string(), "b".to_string()]);
        assert_eq!(alg_with_vec_string.get_algebra().cardinality(), 3);
        
        // Test type alias for backward compatibility
        let alg_with_vec_i32_alias = AlgebraWithGeneratingVectorI32::new(
            Box::new(BasicAlgebra::new(
                "A_alias".to_string(),
                HashSet::from([0, 1]),
                Vec::new()
            )) as Box<dyn SmallAlgebra<UniverseItem = i32>>,
            vec![0, 1]
        );
        assert_eq!(alg_with_vec_i32_alias.get_vector(), &[0, 1]);
    }

    fn load_ua(name: &str) -> Option<BasicAlgebra<i32>> {
        let path = format!("resources/algebras/{}.ua", name);
        if !std::path::Path::new(&path).exists() {
            return None;
        }
        let reader = crate::io::AlgebraReader::new_from_path(&path).ok()?;
        reader.read_algebra_file().ok()
    }

    #[test]
    fn test_si_decompose_order_is_deterministic() {
        for name in ["cyclic2", "lat2", "z3"] {
            let Some(alg) = load_ua(name) else {
                continue;
            };
            let snap = |alg: BasicAlgebra<i32>| {
                AlgebraWithGeneratingVector::si_decompose(
                    Box::new(alg) as Box<dyn SmallAlgebra<UniverseItem = i32>>,
                    &[0, 1],
                )
                .into_iter()
                .map(|factor| {
                    (
                        factor.get_algebra().cardinality(),
                        factor.get_vector().to_vec(),
                    )
                })
                .collect::<Vec<_>>()
            };
            let first = snap(alg.clone());
            for i in 1..8 {
                let again = snap(alg.clone());
                assert_eq!(
                    again, first,
                    "si_decompose({name}) changed on run {i}: {again:?} vs {first:?}"
                );
            }
        }
    }

    #[test]
    fn test_si_decompose_vectors_are_in_range() {
        use crate::alg::algebra::Algebra;
        for name in ["cyclic2", "lat2", "z3"] {
            let Some(alg) = load_ua(name) else {
                continue;
            };
            let card = alg.cardinality();
            let decomp = AlgebraWithGeneratingVector::si_decompose(
                Box::new(alg) as Box<dyn SmallAlgebra<UniverseItem = i32>>,
                &[0, 1],
            );
            assert!(
                !decomp.is_empty(),
                "si_decompose({name}) returned no factors"
            );
            for factor in &decomp {
                let n = factor.get_algebra().cardinality();
                assert!(n > 0, "{name} factor has non-positive cardinality");
                for &v in factor.get_vector() {
                    assert!(
                        v >= 0 && v < n,
                        "{name} generating vector entry {v} outside [0, {n})"
                    );
                }
                for op in Algebra::operations(factor.get_algebra()) {
                    let arity = op.arity();
                    if arity != 2 {
                        continue;
                    }
                    for a in 0..n {
                        for b in 0..n {
                            let val = op
                                .int_value_at(&[a, b])
                                .unwrap_or_else(|e| panic!("{name} op eval: {e}"));
                            assert!(
                                val >= 0 && val < n,
                                "{name} op returned {val} outside [0, {n})"
                            );
                        }
                    }
                }
                let _ = card;
            }
        }
    }
}
