use std::collections::HashSet;
use std::fmt::{Debug, Display};
use std::hash::{Hash, Hasher};
use crate::alg::general_algebra::GeneralAlgebra;
use crate::alg::op::{Operation, OperationSymbol};
use crate::util::int_array::{IntArray, IntArrayTrait};

/// A permutation group on the set {0, ..., n-1}.
/// 
/// This struct represents a group of permutations with operations for
/// product, inverse, and identity. It extends the functionality of
/// GeneralAlgebra to provide group-specific operations.
#[derive(Debug, Clone)]
pub struct PermutationGroup {
    /// The name of the permutation group
    pub name: String,
    /// The generators of the group
    pub generators: Vec<IntArray>,
    /// Optional universe list for the group
    pub universe_list: Option<Vec<IntArray>>,
    /// The size of the underlying set
    pub underlying_set_size: usize,
    /// The identity permutation (cached)
    pub identity: Option<IntArray>,
    /// The underlying general algebra
    pub general_algebra: GeneralAlgebra<IntArray>,
}

impl PermutationGroup {
    /// Create a new PermutationGroup with the given name and generators.
    /// 
    /// # Arguments
    /// * `name` - The name of the permutation group
    /// * `generators` - The generators of the group
    /// 
    /// # Returns
    /// A new PermutationGroup instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::group::PermutationGroup;
    /// use uacalc::util::int_array::{IntArray, IntArrayTrait};
    /// 
    /// let generators = vec![IntArray::from_array(vec![1, 0, 2]).unwrap()];
    /// let group = PermutationGroup::new("S3".to_string(), generators);
    /// assert_eq!(group.name, "S3");
    /// ```
    pub fn new(name: String, generators: Vec<IntArray>) -> Self {
        let underlying_set_size = if let Some(first_gen) = generators.first() {
            first_gen.universe_size()
        } else {
            0
        };
        
        let identity = if underlying_set_size > 0 {
            Some(Self::id(underlying_set_size))
        } else {
            None
        };
        
        // Create universe from generators and identity
        let mut universe = HashSet::new();
        universe.extend(generators.iter().cloned());
        if let Some(ref id) = identity {
            universe.insert(id.clone());
        }
        
        let general_algebra = GeneralAlgebra::new_with_universe(name.clone(), universe);
        
        PermutationGroup {
            name,
            generators,
            universe_list: None,
            underlying_set_size,
            identity,
            general_algebra,
        }
    }
    
    /// Create a new PermutationGroup with the given name, generators, and universe list.
    /// 
    /// # Arguments
    /// * `name` - The name of the permutation group
    /// * `generators` - The generators of the group
    /// * `universe_list` - The universe list for the group
    /// 
    /// # Returns
    /// A new PermutationGroup instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::group::PermutationGroup;
    /// use uacalc::util::int_array::{IntArray, IntArrayTrait};
    /// 
    /// let generators = vec![IntArray::from_array(vec![1, 0, 2]).unwrap()];
    /// let universe_list = vec![IntArray::from_array(vec![0, 1, 2]).unwrap()];
    /// let group = PermutationGroup::new_with_universe("S3".to_string(), generators, universe_list);
    /// assert_eq!(group.name, "S3");
    /// ```
    pub fn new_with_universe(name: String, generators: Vec<IntArray>, universe_list: Vec<IntArray>) -> Self {
        let underlying_set_size = if let Some(first_gen) = generators.first() {
            first_gen.universe_size()
        } else {
            0
        };
        
        let identity = if underlying_set_size > 0 {
            Some(Self::id(underlying_set_size))
        } else {
            None
        };
        
        // Create universe from generators, universe_list, and identity
        let mut universe = HashSet::new();
        universe.extend(generators.iter().cloned());
        universe.extend(universe_list.iter().cloned());
        if let Some(ref id) = identity {
            universe.insert(id.clone());
        }
        
        let general_algebra = GeneralAlgebra::new_with_universe(name.clone(), universe);
        
        PermutationGroup {
            name,
            generators,
            universe_list: Some(universe_list),
            underlying_set_size,
            identity,
            general_algebra,
        }
    }
    
    /// Create a new PermutationGroup with proper error handling.
    /// 
    /// # Arguments
    /// * `name` - The name of the permutation group
    /// * `generators` - The generators of the group
    /// 
    /// # Returns
    /// * `Ok(PermutationGroup)` if successful
    /// * `Err(String)` if validation fails
    pub fn new_safe(name: String, generators: Vec<IntArray>) -> Result<Self, String> {
        if generators.is_empty() {
            return Err("Generators cannot be empty".to_string());
        }
        
        let first_size = generators[0].universe_size();
        for (i, gen) in generators.iter().enumerate() {
            if gen.universe_size() != first_size {
                return Err(format!("Generator {} has size {}, expected {}", 
                    i, gen.universe_size(), first_size));
            }
        }
        
        Ok(Self::new(name, generators))
    }
    
    /// Create a new PermutationGroup with universe list and proper error handling.
    /// 
    /// # Arguments
    /// * `name` - The name of the permutation group
    /// * `generators` - The generators of the group
    /// * `universe_list` - The universe list for the group
    /// 
    /// # Returns
    /// * `Ok(PermutationGroup)` if successful
    /// * `Err(String)` if validation fails
    pub fn new_with_universe_safe(name: String, generators: Vec<IntArray>, universe_list: Vec<IntArray>) -> Result<Self, String> {
        if generators.is_empty() {
            return Err("Generators cannot be empty".to_string());
        }
        
        let first_size = generators[0].universe_size();
        for (i, gen) in generators.iter().enumerate() {
            if gen.universe_size() != first_size {
                return Err(format!("Generator {} has size {}, expected {}", 
                    i, gen.universe_size(), first_size));
            }
        }
        
        for (i, elem) in universe_list.iter().enumerate() {
            if elem.universe_size() != first_size {
                return Err(format!("Universe element {} has size {}, expected {}", 
                    i, elem.universe_size(), first_size));
            }
        }
        
        Ok(Self::new_with_universe(name, generators, universe_list))
    }
    
    /// Create a product operation for the given algebra size.
    /// 
    /// # Arguments
    /// * `alg_size` - The size of the algebra
    /// 
    /// # Returns
    /// A new Operation that computes the product of two permutations
    /// 
    /// # Examples
    /// ```
    /// use uacalc::group::PermutationGroup;
    /// use uacalc::util::int_array::IntArray;
    /// 
    /// let op = PermutationGroup::make_prod_op(3);
    /// assert_eq!(op.arity(), 2);
    /// ```
    pub fn make_prod_op(alg_size: i32) -> Box<dyn Operation> {
        let symbol = OperationSymbol::product().clone();
        Box::new(ProductOperation { symbol, alg_size })
    }
    
    /// Compute the product of two permutations.
    /// 
    /// # Arguments
    /// * `p0` - First permutation
    /// * `p1` - Second permutation
    /// 
    /// # Returns
    /// The product permutation p0 * p1, or an error if the permutations are invalid
    /// 
    /// # Examples
    /// ```
    /// use uacalc::group::PermutationGroup;
    /// use uacalc::util::int_array::{IntArray, IntArrayTrait};
    /// 
    /// let p0 = IntArray::from_array(vec![1, 0, 2]).unwrap();
    /// let p1 = IntArray::from_array(vec![2, 1, 0]).unwrap();
    /// let result = PermutationGroup::prod(p0, p1).unwrap();
    /// assert_eq!(result.as_slice(), &[2, 0, 1]);
    /// ```
    pub fn prod(p0: IntArray, p1: IntArray) -> Result<IntArray, String> {
        let arr0 = p0.as_slice();
        let arr1 = p1.as_slice();
        
        if arr0.len() != arr1.len() {
            return Err(format!("Permutations must have the same size: {} != {}", arr0.len(), arr1.len()));
        }
        
        let n = arr0.len();
        let mut arr = vec![0; n];
        
        for i in 0..n {
            if arr1[i] < 0 || arr1[i] as usize >= n {
                return Err(format!("Invalid permutation: index {} out of bounds for size {}", arr1[i], n));
            }
            arr[i] = arr0[arr1[i] as usize];
        }
        
        IntArray::from_array(arr).map_err(|e| format!("Failed to create IntArray: {}", e))
    }
    
    /// Create an inverse operation for the given algebra size.
    /// 
    /// # Arguments
    /// * `alg_size` - The size of the algebra
    /// 
    /// # Returns
    /// A new Operation that computes the inverse of a permutation
    /// 
    /// # Examples
    /// ```
    /// use uacalc::group::PermutationGroup;
    /// 
    /// let op = PermutationGroup::make_inv_op(3);
    /// assert_eq!(op.arity(), 1);
    /// ```
    pub fn make_inv_op(alg_size: i32) -> Box<dyn Operation> {
        let symbol = OperationSymbol::inverse().clone();
        Box::new(InverseOperation { symbol, alg_size })
    }
    
    /// Compute the inverse of a permutation.
    /// 
    /// # Arguments
    /// * `a` - The permutation to invert
    /// 
    /// # Returns
    /// The inverse permutation, or an error if the permutation is invalid
    /// 
    /// # Examples
    /// ```
    /// use uacalc::group::PermutationGroup;
    /// use uacalc::util::int_array::{IntArray, IntArrayTrait};
    /// 
    /// let p = IntArray::from_array(vec![1, 0, 2]).unwrap();
    /// let inv = PermutationGroup::inv(p).unwrap();
    /// assert_eq!(inv.as_slice(), &[1, 0, 2]);
    /// ```
    pub fn inv(a: IntArray) -> Result<IntArray, String> {
        let arr0 = a.as_slice();
        let n = arr0.len();
        let mut arr = vec![0; n];
        
        for i in 0..n {
            if arr0[i] < 0 || arr0[i] as usize >= n {
                return Err(format!("Invalid permutation: index {} out of bounds for size {}", arr0[i], n));
            }
            arr[arr0[i] as usize] = i as i32;
        }
        
        IntArray::from_array(arr).map_err(|e| format!("Failed to create IntArray: {}", e))
    }
    
    /// Create an identity operation for the given algebra size and set size.
    /// 
    /// # Arguments
    /// * `alg_size` - The size of the algebra
    /// * `set_size` - The size of the underlying set
    /// 
    /// # Returns
    /// A new Operation that returns the identity permutation
    /// 
    /// # Examples
    /// ```
    /// use uacalc::group::PermutationGroup;
    /// 
    /// let op = PermutationGroup::make_id_op(3, 3);
    /// assert_eq!(op.arity(), 0);
    /// ```
    pub fn make_id_op(alg_size: i32, set_size: i32) -> Box<dyn Operation> {
        let symbol = OperationSymbol::identity().clone();
        Box::new(IdentityOperation { symbol, alg_size, set_size: set_size as usize })
    }
    
    /// Create the identity permutation of the given size.
    /// 
    /// # Arguments
    /// * `set_size` - The size of the underlying set
    /// 
    /// # Returns
    /// The identity permutation [0, 1, 2, ..., set_size-1]
    /// 
    /// # Examples
    /// ```
    /// use uacalc::group::PermutationGroup;
    /// use uacalc::util::int_array::IntArrayTrait;
    /// 
    /// let id = PermutationGroup::id(3);
    /// assert_eq!(id.as_slice(), &[0, 1, 2]);
    /// ```
    pub fn id(set_size: usize) -> IntArray {
        let arr: Vec<i32> = (0..set_size as i32).collect();
        IntArray::from_array(arr).unwrap()
    }
    
    /// Get the generators of this permutation group.
    /// 
    /// # Returns
    /// A reference to the generators vector
    pub fn get_generators(&self) -> &Vec<IntArray> {
        &self.generators
    }
    
    /// Get the universe list of this permutation group.
    /// 
    /// # Returns
    /// A reference to the universe list, if it exists
    pub fn get_universe_list(&self) -> Option<&Vec<IntArray>> {
        self.universe_list.as_ref()
    }
    
    /// Get the underlying set size.
    /// 
    /// # Returns
    /// The size of the underlying set
    pub fn get_underlying_set_size(&self) -> usize {
        self.underlying_set_size
    }
    
    /// Get the identity permutation.
    /// 
    /// # Returns
    /// A reference to the identity permutation, if it exists
    pub fn get_identity(&self) -> Option<&IntArray> {
        self.identity.as_ref()
    }
    
    /// Get a reference to the underlying general algebra.
    /// 
    /// # Returns
    /// A reference to the general algebra
    pub fn get_general_algebra(&self) -> &GeneralAlgebra<IntArray> {
        &self.general_algebra
    }
    
    /// Get a mutable reference to the underlying general algebra.
    /// 
    /// # Returns
    /// A mutable reference to the general algebra
    pub fn get_general_algebra_mut(&mut self) -> &mut GeneralAlgebra<IntArray> {
        &mut self.general_algebra
    }
}

impl PartialEq for PermutationGroup {
    fn eq(&self, other: &Self) -> bool {
        self.name == other.name &&
        self.generators == other.generators &&
        self.universe_list == other.universe_list &&
        self.underlying_set_size == other.underlying_set_size
    }
}

impl Eq for PermutationGroup {}

impl Hash for PermutationGroup {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.name.hash(state);
        self.generators.hash(state);
        self.universe_list.hash(state);
        self.underlying_set_size.hash(state);
    }
}

impl Display for PermutationGroup {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "PermutationGroup(name: {}, generators: {}, set_size: {})", 
            self.name, self.generators.len(), self.underlying_set_size)
    }
}

/// Product operation for permutation groups.
#[derive(Debug, Clone)]
struct ProductOperation {
    symbol: OperationSymbol,
    alg_size: i32,
}

impl Display for ProductOperation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "ProductOperation({})", self.symbol)
    }
}

impl Operation for ProductOperation {
    fn arity(&self) -> i32 {
        self.symbol.arity()
    }
    
    fn get_set_size(&self) -> i32 {
        self.alg_size
    }
    
    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        if args.len() != 2 {
            return Err("Product operation requires exactly 2 arguments".to_string());
        }
        
        // Convert indices to IntArray and compute product
        let p0 = IntArray::from_array(vec![args[0]])
            .map_err(|e| format!("Failed to create IntArray: {}", e))?;
        let p1 = IntArray::from_array(vec![args[1]])
            .map_err(|e| format!("Failed to create IntArray: {}", e))?;
        let result = PermutationGroup::prod(p0, p1)?;
        result.get(0).ok_or_else(|| "Empty result array".to_string())
    }
    
    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
        if args.len() != 2 {
            return Err("Product operation requires exactly 2 arguments".to_string());
        }
        
        let mut result = Vec::with_capacity(args[0].len());
        for i in 0..args[0].len() {
            let p0 = IntArray::from_array(vec![args[0][i]])
                .map_err(|e| format!("Failed to create IntArray: {}", e))?;
            let p1 = IntArray::from_array(vec![args[1][i]])
                .map_err(|e| format!("Failed to create IntArray: {}", e))?;
            let prod = PermutationGroup::prod(p0, p1)?;
            result.push(prod.get(0).ok_or_else(|| "Empty result array".to_string())?);
        }
        Ok(result)
    }
    
    fn int_value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.value_at(args)
    }
    
    fn int_value_at_horner(&self, _arg: i32) -> Result<i32, String> {
        Err("Horner access not supported for product operation".to_string())
    }
    
    fn make_table(&mut self) -> Result<(), String> {
        // Product operations don't use tables
        Ok(())
    }
    
    fn get_table(&self) -> Option<&[i32]> {
        None
    }
    
    fn get_table_force(&mut self, _make_table: bool) -> Result<&[i32], String> {
        Err("No table available for product operation".to_string())
    }
    
    fn is_table_based(&self) -> bool {
        false
    }
    
    fn is_idempotent(&self) -> Result<bool, String> {
        Ok(false) // Product is not idempotent
    }
    
    fn is_associative(&self) -> Result<bool, String> {
        Ok(true) // Product is associative
    }
    
    fn is_commutative(&self) -> Result<bool, String> {
        Ok(false) // Product is not commutative
    }
    
    fn is_totally_symmetric(&self) -> Result<bool, String> {
        Ok(false) // Product is not symmetric
    }
    
    fn is_maltsev(&self) -> Result<bool, String> {
        Ok(false) // Product is not Maltsev
    }
    
    fn is_total(&self) -> Result<bool, String> {
        Ok(true) // Product is total
    }
    
    fn clone_box(&self) -> Box<dyn Operation> {
        Box::new(self.clone())
    }
    
}

/// Inverse operation for permutation groups.
#[derive(Debug, Clone)]
struct InverseOperation {
    symbol: OperationSymbol,
    alg_size: i32,
}

impl Display for InverseOperation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "InverseOperation({})", self.symbol)
    }
}

impl Operation for InverseOperation {
    fn arity(&self) -> i32 {
        self.symbol.arity()
    }
    
    fn get_set_size(&self) -> i32 {
        self.alg_size
    }
    
    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn value_at(&self, args: &[i32]) -> Result<i32, String> {
        if args.len() != 1 {
            return Err("Inverse operation requires exactly 1 argument".to_string());
        }
        
        // Convert index to IntArray and compute inverse
        let a = IntArray::from_array(vec![args[0]])
            .map_err(|e| format!("Failed to create IntArray: {}", e))?;
        let result = PermutationGroup::inv(a)?;
        result.get(0).ok_or_else(|| "Empty result array".to_string())
    }
    
    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
        if args.len() != 1 {
            return Err("Inverse operation requires exactly 1 argument".to_string());
        }
        
        let mut result = Vec::with_capacity(args[0].len());
        for i in 0..args[0].len() {
            let a = IntArray::from_array(vec![args[0][i]])
                .map_err(|e| format!("Failed to create IntArray: {}", e))?;
            let inv = PermutationGroup::inv(a)?;
            result.push(inv.get(0).ok_or_else(|| "Empty result array".to_string())?);
        }
        Ok(result)
    }
    
    fn int_value_at(&self, args: &[i32]) -> Result<i32, String> {
        self.value_at(args)
    }
    
    fn int_value_at_horner(&self, _arg: i32) -> Result<i32, String> {
        Err("Horner access not supported for inverse operation".to_string())
    }
    
    fn make_table(&mut self) -> Result<(), String> {
        // Inverse operations don't use tables
        Ok(())
    }
    
    fn get_table(&self) -> Option<&[i32]> {
        None
    }
    
    fn get_table_force(&mut self, _make_table: bool) -> Result<&[i32], String> {
        Err("No table available for inverse operation".to_string())
    }
    
    fn is_table_based(&self) -> bool {
        false
    }
    
    fn is_idempotent(&self) -> Result<bool, String> {
        Ok(false) // Inverse is not idempotent
    }
    
    fn is_associative(&self) -> Result<bool, String> {
        Ok(false) // Unary operations are not associative
    }
    
    fn is_commutative(&self) -> Result<bool, String> {
        Ok(false) // Unary operations are not commutative
    }
    
    fn is_totally_symmetric(&self) -> Result<bool, String> {
        Ok(true) // Unary operations are symmetric
    }
    
    fn is_maltsev(&self) -> Result<bool, String> {
        Ok(false) // Unary operations are not Maltsev
    }
    
    fn is_total(&self) -> Result<bool, String> {
        Ok(true) // Inverse is total
    }
    
    fn clone_box(&self) -> Box<dyn Operation> {
        Box::new(self.clone())
    }
    
}

/// Identity operation for permutation groups.
#[derive(Debug, Clone)]
struct IdentityOperation {
    symbol: OperationSymbol,
    alg_size: i32,
    set_size: usize,
}

impl Display for IdentityOperation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "IdentityOperation({})", self.symbol)
    }
}

impl Operation for IdentityOperation {
    fn arity(&self) -> i32 {
        self.symbol.arity()
    }
    
    fn get_set_size(&self) -> i32 {
        self.alg_size
    }
    
    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }
    
    fn value_at(&self, _args: &[i32]) -> Result<i32, String> {
        // Identity operation returns the identity permutation
        let id = PermutationGroup::id(self.set_size);
        Ok(id.get(0).unwrap())
    }
    
    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String> {
        if !args.is_empty() && !args[0].is_empty() {
            let mut result = Vec::with_capacity(args[0].len());
            for _i in 0..args[0].len() {
                let id = PermutationGroup::id(self.set_size);
                result.push(id.get(0).unwrap());
            }
            Ok(result)
        } else {
            Ok(vec![0]) // Default identity
        }
    }
    
    fn int_value_at(&self, _args: &[i32]) -> Result<i32, String> {
        self.value_at(&[])
    }
    
    fn int_value_at_horner(&self, _arg: i32) -> Result<i32, String> {
        Ok(0) // Identity element
    }
    
    fn make_table(&mut self) -> Result<(), String> {
        // Identity operations don't use tables
        Ok(())
    }
    
    fn get_table(&self) -> Option<&[i32]> {
        None
    }
    
    fn get_table_force(&mut self, _make_table: bool) -> Result<&[i32], String> {
        Err("No table available for identity operation".to_string())
    }
    
    fn is_table_based(&self) -> bool {
        false
    }
    
    fn is_idempotent(&self) -> Result<bool, String> {
        Ok(true) // Identity is idempotent
    }
    
    fn is_associative(&self) -> Result<bool, String> {
        Ok(true) // Identity is associative
    }
    
    fn is_commutative(&self) -> Result<bool, String> {
        Ok(true) // Identity is commutative
    }
    
    fn is_totally_symmetric(&self) -> Result<bool, String> {
        Ok(true) // Identity is symmetric
    }
    
    fn is_maltsev(&self) -> Result<bool, String> {
        Ok(false) // Identity is not Maltsev
    }
    
    fn is_total(&self) -> Result<bool, String> {
        Ok(true) // Identity is total
    }
    
    fn clone_box(&self) -> Box<dyn Operation> {
        Box::new(self.clone())
    }
    
}
