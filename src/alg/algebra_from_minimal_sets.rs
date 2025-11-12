use std::collections::{HashMap, HashSet};
use std::fmt::{Debug, Display};
use std::sync::Arc;
use crate::alg::algebra::{Algebra, ProgressMonitor};
use crate::alg::general_algebra::GeneralAlgebra;
use crate::alg::small_algebra::{SmallAlgebra, AlgebraType};
use crate::alg::op::{Operation, OperationSymbol, SimilarityType};
use crate::alg::op::operations::make_int_operation;
use crate::util::horner;

/// An algebra constructed from minimal sets with a specific geometry.
/// 
/// Starting with an algebra B which is permutational (nonconstant
/// unary polynomials are permutations) and a geometry for the 
/// minimal sets, this constructs an algebra A with tame minimal sets, 
/// having B as a minimal set. Initially we will assume the geometry
/// has 3 minimal sets, B, C, D, with C and D disjoint and the intersection
/// of B and C just 0 and B and D the last element of B.
/// 
/// If n is the size of A and k is the size of each minimal set, we can
/// specify the geometry of a list of maps 0 to k-1 into A.
/// 
/// This implementation is specialized for i32 universe type, matching the Java implementation.
/// 
/// # Examples
/// ```
/// use uacalc::alg::{BasicAlgebra, SmallAlgebra, AlgebraFromMinimalSets, Algebra};
/// use std::collections::HashSet;
/// 
/// // Create a minimal algebra
/// let min_alg = Box::new(BasicAlgebra::new(
///     "minimal".to_string(),
///     HashSet::from([0, 1, 2]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Create algebra from minimal sets
/// let alg = AlgebraFromMinimalSets::new(min_alg).unwrap();
/// assert_eq!(alg.cardinality(), 7); // 3 * 3 - 2 = 7
/// ```
pub struct AlgebraFromMinimalSets {
    /// The underlying general algebra (composition instead of inheritance)
    base: GeneralAlgebra<i32>,
    
    /// The minimal algebra B
    minimal_algebra: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
    
    /// Size of the minimal algebra
    min_alg_size: usize,
    
    /// Optional connecting points
    connecting_pts: Option<Vec<i32>>,
    
    /// Connection index a (default 0)
    a: usize,
    
    /// Connection index b (default minAlgSize - 1)
    b: usize,
    
    /// List of maps from {0,...,k-1} to {0,...,n-1}
    maps: Vec<Vec<i32>>,
    
    /// Map from A to B, identity on B, and an isomorphism when restricted to any minimal set
    map_to_b: Vec<i32>,
}

impl AlgebraFromMinimalSets {
    /// Create a new AlgebraFromMinimalSets with default size (3 * minAlgSize - 2).
    /// 
    /// # Arguments
    /// * `min_algebra` - The minimal algebra B
    /// 
    /// # Returns
    /// * `Ok(AlgebraFromMinimalSets)` - Successfully created algebra
    /// * `Err(String)` - If there's an error creating the algebra
    pub fn new(
        min_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>
    ) -> Result<Self, String> {
        Self::new_with_name(None, min_algebra)
    }
    
    /// Create a new AlgebraFromMinimalSets with explicit size and maps.
    /// 
    /// # Arguments
    /// * `min_algebra` - The minimal algebra B
    /// * `alg_size` - The size of the constructed algebra
    /// * `maps` - Optional list of maps (if None, default maps are created)
    /// 
    /// # Returns
    /// * `Ok(AlgebraFromMinimalSets)` - Successfully created algebra
    /// * `Err(String)` - If there's an error creating the algebra
    pub fn new_with_size(
        min_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        alg_size: usize,
        maps: Option<Vec<Vec<i32>>>
    ) -> Result<Self, String> {
        Self::new_full(None, min_algebra, alg_size, maps, None)
    }
    
    /// Create a new AlgebraFromMinimalSets with a name.
    /// 
    /// # Arguments
    /// * `name` - Optional name for the algebra
    /// * `min_algebra` - The minimal algebra B
    /// 
    /// # Returns
    /// * `Ok(AlgebraFromMinimalSets)` - Successfully created algebra
    /// * `Err(String)` - If there's an error creating the algebra
    pub fn new_with_name(
        name: Option<String>,
        min_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>
    ) -> Result<Self, String> {
        let min_alg_size = min_algebra.cardinality() as usize;
        let alg_size = 3 * min_alg_size - 2;
        Self::new_full(name, min_algebra, alg_size, None, None)
    }
    
    /// Create a new AlgebraFromMinimalSets with connecting points.
    /// 
    /// # Arguments
    /// * `name` - Optional name for the algebra
    /// * `min_algebra` - The minimal algebra B
    /// * `connect_pts` - Optional connecting points [a, b]
    /// 
    /// # Returns
    /// * `Ok(AlgebraFromMinimalSets)` - Successfully created algebra
    /// * `Err(String)` - If there's an error creating the algebra
    pub fn new_with_connecting_pts(
        name: Option<String>,
        min_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        connect_pts: Option<Vec<i32>>
    ) -> Result<Self, String> {
        let min_alg_size = min_algebra.cardinality() as usize;
        let alg_size = 3 * min_alg_size - 2;
        Self::new_full(name, min_algebra, alg_size, None, connect_pts)
    }
    
    /// Create a new AlgebraFromMinimalSets with all parameters.
    /// 
    /// If k is the cardinality of `min_algebra`, each map maps
    /// k = {0,..., k-1} one-to-one into n = {0,...,n-1}. The first map
    /// must be the identity. Each element of n must be in the range of 
    /// at least one map. Given any two elements of n, there are overlapping
    /// ranges of the maps going from one to the other.
    /// 
    /// # Arguments
    /// * `name` - Optional name for the algebra
    /// * `min_algebra` - A permutational algebra (the minimal algebra B)
    /// * `alg_size` - The size of the constructed algebra
    /// * `maps` - Optional list of maps (if None, default maps are created)
    /// * `connect_pts` - Optional connecting points [a, b]
    /// 
    /// # Returns
    /// * `Ok(AlgebraFromMinimalSets)` - Successfully created algebra
    /// * `Err(String)` - If there's an error creating the algebra
    pub fn new_full(
        name: Option<String>,
        min_algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
        alg_size: usize,
        maps: Option<Vec<Vec<i32>>>,
        connect_pts: Option<Vec<i32>>
    ) -> Result<Self, String> {
        let min_alg_size = min_algebra.cardinality() as usize;
        
        // Create universe as integers 0..alg_size-1
        let universe: HashSet<i32> = (0..alg_size as i32).collect();
        
        let base = GeneralAlgebra::new_with_universe(
            name.unwrap_or_else(|| "AlgebraFromMinimalSets".to_string()),
            universe
        );
        
        // Initialize connection points
        let mut a = 0;
        let mut b = min_alg_size - 1;
        if let Some(ref pts) = connect_pts {
            if pts.len() > 1 {
                a = pts[0] as usize;
                b = pts[1] as usize;
            }
        }
        
        // Create maps (default if None)
        let maps_null = maps.is_none();
        let maps = if let Some(m) = maps {
            m
        } else {
            Self::make_default_maps(min_alg_size, a, b)?
        };
        
        // Create map_to_b
        let map_to_b = Self::make_map_to_b(alg_size, min_alg_size, &maps)?;
        
        let mut alg = AlgebraFromMinimalSets {
            base,
            minimal_algebra: Arc::from(min_algebra),
            min_alg_size,
            connecting_pts: connect_pts,
            a,
            b,
            maps,
            map_to_b,
        };
        
        // Create operations
        let ops = alg.make_ops(maps_null)?;
        alg.base.set_operations(ops);
        
        Ok(alg)
    }
    
    /// Create default maps (B, C, D) when maps is None.
    /// 
    /// # Arguments
    /// * `k` - Size of minimal algebra
    /// * `a` - Connection index a
    /// * `b` - Connection index b
    /// 
    /// # Returns
    /// * `Ok(Vec<Vec<i32>>)` - List of three maps [B, C, D]
    /// * `Err(String)` - If there's an error creating maps
    fn make_default_maps(k: usize, a: usize, b: usize) -> Result<Vec<Vec<i32>>, String> {
        let mut maps = Vec::with_capacity(3);
        let mut b_map = vec![0i32; k];
        let mut c_map = vec![0i32; k];
        let mut d_map = vec![0i32; k];
        
        for i in 0..k {
            b_map[i] = i as i32;
            if i < a {
                c_map[i] = (i + k) as i32;
            } else {
                c_map[i] = (i + k - 1) as i32;
            }
            if i < b {
                d_map[i] = (i + 2 * k - 1) as i32;
            } else {
                d_map[i] = (i + 2 * k - 2) as i32;
            }
        }
        c_map[a] = a as i32;
        d_map[b] = b as i32;
        
        maps.push(b_map);
        maps.push(c_map);
        maps.push(d_map);
        
        Ok(maps)
    }
    
    /// Create the map from A to B.
    /// 
    /// This map is the identity on B, and an isomorphism when restricted
    /// to any minimal set.
    /// 
    /// # Arguments
    /// * `size` - Size of algebra A
    /// * `min_alg_size` - Size of minimal algebra B
    /// * `maps` - List of maps
    /// 
    /// # Returns
    /// * `Ok(Vec<i32>)` - The map_to_b array
    /// * `Err(String)` - If maps are inconsistent
    fn make_map_to_b(
        size: usize,
        min_alg_size: usize,
        maps: &[Vec<i32>]
    ) -> Result<Vec<i32>, String> {
        let mut map_to_b = vec![-1i32; size];
        
        for map in maps {
            for i in 0..min_alg_size {
                let iprime = map[i] as usize;
                if iprime >= size {
                    return Err(format!("Map index {} out of bounds for size {}", iprime, size));
                }
                let existing = map_to_b[iprime];
                if existing != -1 && existing != i as i32 {
                    return Err("Inconsistent maps".to_string());
                }
                map_to_b[iprime] = i as i32;
            }
        }
        
        Ok(map_to_b)
    }
    
    /// Create operations from maps and minimal algebra operations.
    /// 
    /// # Arguments
    /// * `maps_null` - Whether maps was None (determines if we add the 's' operation)
    /// 
    /// # Returns
    /// * `Ok(Vec<Box<dyn Operation>>)` - List of operations
    /// * `Err(String)` - If there's an error creating operations
    fn make_ops(&self, maps_null: bool) -> Result<Vec<Box<dyn Operation>>, String> {
        let mut ops = Vec::new();
        
        // Add 's' operation if maps was None
        if maps_null {
            let size = self.base.cardinality() as usize;
            let min_alg_size = self.min_alg_size;
            let a = self.a as i32;
            let b = self.b as i32;
            
            // Create table for 's' operation: s(x) = x if x < minAlgSize, else a or b
            let mut table = Vec::with_capacity(size);
            for i in 0..size {
                let val = if i < min_alg_size {
                    i as i32
                } else if i < 2 * min_alg_size - 1 {
                    a
                } else {
                    b
                };
                table.push(val);
            }
            
            let sym = OperationSymbol::new_safe("s", 1, false)?;
            let op = make_int_operation(sym, size as i32, table)?;
            ops.push(op);
        }
        
        // Add operations from maps
        let mut r = 0;
        for map in &self.maps {
            let size = self.base.cardinality() as usize;
            let min_alg_size = self.min_alg_size;
            
            // Create table for 'p' operation: p(x) = map[map_to_b[x]]
            let mut table = Vec::with_capacity(size);
            for i in 0..size {
                let map_to_b_val = self.map_to_b[i] as usize;
                if map_to_b_val >= min_alg_size {
                    return Err(format!("map_to_b[{}] = {} out of bounds", i, map_to_b_val));
                }
                table.push(map[map_to_b_val]);
            }
            
            let sym = OperationSymbol::new_safe(&format!("p{}", r), 1, false)?;
            let op = make_int_operation(sym, size as i32, table)?;
            ops.push(op);
            r += 1;
        }
        
        // Add operations from minimal algebra
        let min_ops = self.minimal_algebra.get_operations_ref();
        for min_op in min_ops {
            let arity = min_op.arity();
            let size = self.base.cardinality() as usize;
            let min_alg_size = self.min_alg_size;
            
            // Create table for operation: op(x1,...,xk) = minOp(map_to_b[x1],...,map_to_b[xk])
            let table_size = (size as usize).pow(arity as u32);
            let mut table = Vec::with_capacity(table_size);
            
            for k in 0..table_size {
                let args = horner::horner_inv_same_size(k as i32, size as i32, arity as usize);
                let mut args_to_b = Vec::with_capacity(arity as usize);
                for &arg in &args {
                    let map_to_b_val = self.map_to_b[arg as usize];
                    if map_to_b_val < 0 || map_to_b_val as usize >= min_alg_size {
                        return Err(format!("Invalid map_to_b value: {}", map_to_b_val));
                    }
                    args_to_b.push(map_to_b_val);
                }
                
                let result = min_op.int_value_at(&args_to_b)?;
                table.push(result);
            }
            
            let sym_name = format!("op-{}", min_op.symbol().name());
            let sym = OperationSymbol::new_safe(&sym_name, arity, false)?;
            let op = make_int_operation(sym, size as i32, table)?;
            ops.push(op);
        }
        
        Ok(ops)
    }
}

impl Clone for AlgebraFromMinimalSets {
    fn clone(&self) -> Self {
        AlgebraFromMinimalSets {
            base: self.base.clone(),
            minimal_algebra: Arc::clone(&self.minimal_algebra),
            min_alg_size: self.min_alg_size,
            connecting_pts: self.connecting_pts.clone(),
            a: self.a,
            b: self.b,
            maps: self.maps.clone(),
            map_to_b: self.map_to_b.clone(),
        }
    }
}

impl Debug for AlgebraFromMinimalSets {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("AlgebraFromMinimalSets")
            .field("base", &self.base)
            .field("min_alg_size", &self.min_alg_size)
            .field("a", &self.a)
            .field("b", &self.b)
            .field("maps_count", &self.maps.len())
            .finish()
    }
}

impl Display for AlgebraFromMinimalSets {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "AlgebraFromMinimalSets({})", self.base.name())
    }
}

impl Algebra for AlgebraFromMinimalSets {
    type UniverseItem = i32;
    
    fn universe(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.base.universe()
    }
    
    fn cardinality(&self) -> i32 {
        self.base.cardinality()
    }
    
    fn input_size(&self) -> i32 {
        self.base.input_size()
    }
    
    fn is_unary(&self) -> bool {
        self.base.is_unary()
    }
    
    fn iterator(&self) -> Box<dyn Iterator<Item = Self::UniverseItem>> {
        self.base.iterator()
    }
    
    fn operations(&self) -> Vec<Box<dyn Operation>> {
        self.base.operations()
    }
    
    fn get_operation(&self, sym: &OperationSymbol) -> Option<Box<dyn Operation>> {
        self.base.get_operation(sym)
    }
    
    fn get_operations_map(&self) -> HashMap<OperationSymbol, Box<dyn Operation>> {
        self.base.get_operations_map()
    }
    
    fn name(&self) -> &str {
        self.base.name()
    }
    
    fn set_name(&mut self, name: String) {
        self.base.set_name(name);
    }
    
    fn description(&self) -> Option<&str> {
        self.base.description()
    }
    
    fn set_description(&mut self, desc: Option<String>) {
        self.base.set_description(desc);
    }
    
    fn similarity_type(&self) -> &SimilarityType {
        self.base.similarity_type()
    }
    
    fn update_similarity_type(&mut self) {
        self.base.update_similarity_type();
    }
    
    fn is_similar_to(&self, other: &dyn Algebra<UniverseItem = Self::UniverseItem>) -> bool {
        self.base.is_similar_to(other)
    }
    
    fn make_operation_tables(&mut self) {
        self.base.make_operation_tables();
    }
    
    fn constant_operations(&self) -> Vec<Box<dyn Operation>> {
        self.base.constant_operations()
    }
    
    fn is_idempotent(&self) -> bool {
        self.base.is_idempotent()
    }
    
    fn is_total(&self) -> bool {
        self.base.is_total()
    }
    
    fn monitoring(&self) -> bool {
        self.base.monitoring()
    }
    
    fn get_monitor(&self) -> Option<&dyn ProgressMonitor> {
        self.base.get_monitor()
    }
    
    fn set_monitor(&mut self, monitor: Option<Box<dyn ProgressMonitor>>) {
        self.base.set_monitor(monitor);
    }
}

impl SmallAlgebra for AlgebraFromMinimalSets {
    fn get_operation_ref(&self, sym: &OperationSymbol) -> Option<&dyn Operation> {
        self.base.get_operation_ref(sym)
    }
    
    fn get_operations_ref(&self) -> Vec<&dyn Operation> {
        self.base.get_operations_ref()
    }
    
    fn clone_box(&self) -> Box<dyn SmallAlgebra<UniverseItem = i32>> {
        Box::new(self.clone())
    }
    
    fn algebra_type(&self) -> AlgebraType {
        AlgebraType::Basic // This is a basic algebra type
    }
    
    fn get_element(&self, k: usize) -> Option<i32> {
        let size = self.base.cardinality() as usize;
        if k < size {
            Some(k as i32)
        } else {
            None
        }
    }
    
    fn element_index(&self, elem: &i32) -> Option<usize> {
        let size = self.base.cardinality() as usize;
        if *elem >= 0 && (*elem as usize) < size {
            Some(*elem as usize)
        } else {
            None
        }
    }
    
    fn get_universe_list(&self) -> Option<Vec<i32>> {
        let size = self.base.cardinality() as usize;
        Some((0..size as i32).collect())
    }
    
    fn get_universe_order(&self) -> Option<HashMap<i32, usize>> {
        let size = self.base.cardinality() as usize;
        let mut order = HashMap::new();
        for i in 0..size {
            order.insert(i as i32, i);
        }
        Some(order)
    }
    
    fn parent(&self) -> Option<&dyn SmallAlgebra<UniverseItem = i32>> {
        Some(self.minimal_algebra.as_ref())
    }
    
    fn parents(&self) -> Option<Vec<&dyn SmallAlgebra<UniverseItem = i32>>> {
        Some(vec![self.minimal_algebra.as_ref()])
    }
    
    fn reset_con_and_sub(&mut self) {
        // No-op for now
    }
    
    fn convert_to_default_value_ops(&mut self) {
        // No-op for now
    }
}

