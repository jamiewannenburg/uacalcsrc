use crate::operation::{Operation, TableOperation};
use crate::utils::validate_universe_contiguous;
use crate::{UACalcError, UACalcResult};

use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// Trait for universal algebra structures
pub trait Algebra {
    /// Get the universe (set of elements) of the algebra
    fn universe(&self) -> &[usize];

    /// Get the cardinality of the algebra
    fn cardinality(&self) -> usize;

    /// Get all operations of the algebra
    fn operations(&self) -> &[Arc<Mutex<dyn Operation>>];

    /// Get an operation by index
    ///
    /// Note: This method may be unsupported for some algebra implementations
    /// (e.g., ProductAlgebra) due to trait object reference limitations.
    /// Use operation_arc() when possible for better compatibility.
    fn operation(&self, index: usize) -> UACalcResult<&dyn Operation>;

    /// Get an operation by symbol name
    ///
    /// Note: This method may be unsupported for some algebra implementations
    /// (e.g., ProductAlgebra) due to trait object reference limitations.
    /// Use operation_arc_by_symbol() when possible for better compatibility.
    fn operation_by_symbol(&self, symbol: &str) -> UACalcResult<&dyn Operation>;

    /// Get an operation as an Arc<Mutex<dyn Operation>> by index
    fn operation_arc(&self, index: usize) -> UACalcResult<Arc<Mutex<dyn Operation>>>;

    /// Get an operation as an Arc<Mutex<dyn Operation>> by symbol name
    fn operation_arc_by_symbol(&self, symbol: &str) -> UACalcResult<Arc<Mutex<dyn Operation>>>;

    /// Convert element to index (mirrors Java's elementIndex)
    fn element_to_index(&self, element: usize) -> UACalcResult<usize> {
        if element >= self.cardinality() {
            return Err(UACalcError::IndexOutOfBounds {
                index: element,
                size: self.cardinality(),
            });
        }
        Ok(element)
    }

    /// Convert index to element (mirrors Java's getElement)
    fn index_to_element(&self, index: usize) -> UACalcResult<usize> {
        if index >= self.cardinality() {
            return Err(UACalcError::IndexOutOfBounds {
                index,
                size: self.cardinality(),
            });
        }
        Ok(index)
    }

    /// Calculate input size (sum of cardinality^arity for all operations)
    fn input_size(&self) -> UACalcResult<usize> {
        use crate::utils::power_checked;

        let mut total_size: usize = 0;
        for op in self.operations() {
            let op_guard = op.lock().unwrap();
            let arity = op_guard.arity();
            let cardinality = self.cardinality();

            let operation_size = if arity == 0 {
                1
            } else {
                power_checked(cardinality, arity).ok_or_else(|| {
                    UACalcError::ArithmeticOverflow {
                        operation: format!(
                            "cardinality^{} for operation with arity {}",
                            cardinality, arity
                        ),
                    }
                })?
            };

            total_size = total_size.checked_add(operation_size).ok_or_else(|| {
                UACalcError::ArithmeticOverflow {
                    operation: "summing operation input sizes".to_string(),
                }
            })?;
        }

        Ok(total_size)
    }

    /// Generate operation tables for all operations
    fn make_operation_tables(&mut self) -> UACalcResult<()>;

    /// Check if the algebra is finite
    fn is_finite(&self) -> bool {
        self.cardinality() < usize::MAX
    }

    /// Get the name of the algebra
    fn name(&self) -> &str;
}

/// Trait for finite algebras with efficient operations
pub trait SmallAlgebra: Algebra + Send + Sync {
    /// Get the maximum arity of operations
    fn max_arity(&self) -> usize;

    /// Get the universe as a range for contiguous integer universe
    fn universe_as_range(&self) -> std::ops::Range<usize> {
        0..self.cardinality()
    }

    /// Integer-optimized operation evaluation (mirrors Java's operationIntValue)
    fn operation_int_value(&self, op_index: usize, args: &[usize]) -> UACalcResult<usize> {
        let operation = self.operation(op_index)?;
        operation.int_value_at(args)
    }

    /// Check if all operations are total (defined for all inputs)
    fn is_total(&self) -> bool {
        // For SmallAlgebra with contiguous universe, operations should always be total
        // This is a simplified check - in practice, you might want to verify each operation
        true
    }

    /// Check if an operation is idempotent
    fn is_idempotent(&self, op_index: usize) -> UACalcResult<bool> {
        let operation = self.operation(op_index)?;
        operation.is_idempotent_on_set(self.cardinality())
    }

    /// Check if an operation is associative
    fn is_associative(&self, op_index: usize) -> UACalcResult<bool> {
        let operation = self.operation(op_index)?;
        operation.is_associative_on_set(self.cardinality())
    }

    /// Check if an operation is commutative
    fn is_commutative(&self, op_index: usize) -> UACalcResult<bool> {
        let operation = self.operation(op_index)?;
        operation.is_commutative_on_set(self.cardinality())
    }

    /// Get the subalgebra generated by a subset of elements
    fn subalgebra(&self, generators: &[usize]) -> UACalcResult<BasicAlgebra>;
}

/// Basic implementation of a finite algebra
#[derive(Debug, Clone)]
pub struct BasicAlgebra {
    name: String,
    universe: Vec<usize>,
    operations: Vec<Arc<Mutex<dyn Operation>>>,
    operation_symbols: HashMap<String, usize>,
    operation_tables_built: bool,
}

impl BasicAlgebra {
    /// Create a new basic algebra
    pub fn new(name: String, universe: Vec<usize>) -> UACalcResult<Self> {
        // Validate that universe is contiguous starting from 0
        validate_universe_contiguous(&universe)?;

        Ok(Self {
            name,
            universe,
            operations: Vec::new(),
            operation_symbols: HashMap::new(),
            operation_tables_built: false,
        })
    }

    /// Create a new basic algebra with a contiguous universe of given cardinality
    pub fn with_cardinality(name: String, cardinality: usize) -> UACalcResult<Self> {
        let universe: Vec<usize> = (0..cardinality).collect();
        Self::new(name, universe)
    }

    /// Add an operation to the algebra
    pub fn add_operation(
        &mut self,
        symbol: String,
        operation: Arc<Mutex<dyn Operation>>,
    ) -> UACalcResult<()> {
        // Validate that operation's set size matches algebra's cardinality
        let op_guard = operation
            .lock()
            .map_err(|_| UACalcError::InvalidOperation {
                message: "Failed to lock operation for validation".to_string(),
            })?;
        if op_guard.set_size() != self.cardinality() {
            // Okay for constants
            if op_guard.arity() != 0 {
                return Err(UACalcError::InvalidOperation {
                    message: format!(
                        "Operation set size {} does not match algebra cardinality {}",
                        op_guard.set_size(),
                        self.cardinality()
                    ),
                });
            }
        }

        // Use the operation's symbol name instead of the provided symbol
        let name = op_guard.symbol().name.clone();
        drop(op_guard); // Release the lock

        // Validate that the provided symbol matches the operation's symbol (optional warning)
        if symbol != name {
            eprintln!(
                "Warning: Provided symbol '{}' does not match operation symbol '{}'",
                symbol, name
            );
        }

        let index = self.operations.len();
        self.operation_symbols.insert(name, index);
        self.operations.push(operation);

        // Reset table building status since we added a new operation
        self.operation_tables_built = false;

        Ok(())
    }

    /// Add an operation to the algebra with automatic wrapping
    pub fn add_operation_simple(&mut self, op: impl Operation + 'static) -> UACalcResult<()> {
        let name = op.symbol().name.clone();
        let set_size = op.set_size();
        if set_size != self.cardinality() {
            return Err(UACalcError::InvalidOperation {
                message: format!(
                    "Operation set size {} does not match algebra cardinality {}",
                    set_size,
                    self.cardinality()
                ),
            });
        }
        let op_arc = Arc::new(Mutex::new(op));
        self.add_operation(name, op_arc)
    }

    /// Create an algebra from a universe and operations
    pub fn from_operations(
        name: String,
        universe: Vec<usize>,
        operations: Vec<(String, Arc<Mutex<dyn Operation>>)>,
    ) -> UACalcResult<Self> {
        let mut algebra = Self::new(name, universe)?;
        for (symbol, operation) in operations {
            algebra.add_operation(symbol, operation)?;
        }
        Ok(algebra)
    }

    /// Check if operation tables have been built
    pub fn tables_built(&self) -> bool {
        self.operation_tables_built
    }

    /// Get operation by index without Arc cloning overhead
    pub fn operation_direct(&self, index: usize) -> UACalcResult<&Arc<Mutex<dyn Operation>>> {
        self.operations
            .get(index)
            .ok_or_else(|| UACalcError::IndexOutOfBounds {
                index,
                size: self.operations.len(),
            })
    }

    /// Check if the algebra is idempotent (all operations are idempotent)
    pub fn is_idempotent(&self) -> UACalcResult<bool> {
        for i in 0..self.operations.len() {
            let operation = self.operation_direct(i)?;
            let op_guard = operation
                .lock()
                .map_err(|_| UACalcError::InvalidOperation {
                    message: "Failed to lock operation for idempotency check".to_string(),
                })?;
            if !op_guard.is_idempotent_on_set(self.cardinality())? {
                return Ok(false);
            }
        }
        Ok(true)
    }

    /// Check if the algebra is associative (all binary operations are associative)
    pub fn is_associative(&self) -> UACalcResult<bool> {
        for i in 0..self.operations.len() {
            let operation = self.operation_direct(i)?;
            let op_guard = operation
                .lock()
                .map_err(|_| UACalcError::InvalidOperation {
                    message: "Failed to lock operation for associativity check".to_string(),
                })?;
            if op_guard.arity() == 2 && !op_guard.is_associative_on_set(self.cardinality())? {
                return Ok(false);
            }
        }
        Ok(true)
    }

    /// Check if the algebra is commutative (all binary operations are commutative)
    pub fn is_commutative(&self) -> UACalcResult<bool> {
        for i in 0..self.operations.len() {
            let operation = self.operation_direct(i)?;
            let op_guard = operation
                .lock()
                .map_err(|_| UACalcError::InvalidOperation {
                    message: "Failed to lock operation for commutativity check".to_string(),
                })?;
            if op_guard.arity() == 2 && !op_guard.is_commutative_on_set(self.cardinality())? {
                return Ok(false);
            }
        }
        Ok(true)
    }
}

impl Algebra for BasicAlgebra {
    fn universe(&self) -> &[usize] {
        &self.universe
    }

    fn cardinality(&self) -> usize {
        self.universe.len()
    }

    fn operations(&self) -> &[Arc<Mutex<dyn Operation>>] {
        &self.operations
    }

    fn operation(&self, _index: usize) -> UACalcResult<&dyn Operation> {
        // This method is deprecated in favor of with_operation
        // For backward compatibility, we'll use the new approach internally
        Err(UACalcError::UnsupportedOperation {
            operation: "Use with_operation instead of operation".to_string(),
        })
    }

    fn operation_by_symbol(&self, _symbol: &str) -> UACalcResult<&dyn Operation> {
        // This method is deprecated in favor of with_operation_by_symbol
        // For backward compatibility, we'll use the new approach internally
        Err(UACalcError::UnsupportedOperation {
            operation: "Use with_operation_by_symbol instead of operation_by_symbol".to_string(),
        })
    }

    fn operation_arc(&self, index: usize) -> UACalcResult<Arc<Mutex<dyn Operation>>> {
        self.operations
            .get(index)
            .cloned()
            .ok_or_else(|| UACalcError::IndexOutOfBounds {
                index,
                size: self.operations.len(),
            })
    }

    fn operation_arc_by_symbol(&self, symbol: &str) -> UACalcResult<Arc<Mutex<dyn Operation>>> {
        let index =
            self.operation_symbols
                .get(symbol)
                .ok_or_else(|| UACalcError::OperationNotFound {
                    symbol: symbol.to_string(),
                })?;
        self.operation_arc(*index)
    }

    fn make_operation_tables(&mut self) -> UACalcResult<()> {
        if self.operation_tables_built {
            return Ok(());
        }

        for operation in &self.operations {
            let mut op_guard = operation
                .lock()
                .map_err(|_| UACalcError::InvalidOperation {
                    message: "Failed to lock operation for table building".to_string(),
                })?;
            op_guard.make_table(self.cardinality())?;
        }

        self.operation_tables_built = true;
        Ok(())
    }

    fn name(&self) -> &str {
        &self.name
    }
}

impl SmallAlgebra for BasicAlgebra {
    fn max_arity(&self) -> usize {
        self.operations
            .iter()
            .map(|op| {
                let op_guard = op.lock().unwrap();
                op_guard.arity()
            })
            .max()
            .unwrap_or(0)
    }

    fn subalgebra(&self, generators: &[usize]) -> UACalcResult<BasicAlgebra> {
        // Validate generators
        for &generator in generators {
            if generator >= self.cardinality() {
                return Err(UACalcError::IndexOutOfBounds {
                    index: generator,
                    size: self.cardinality(),
                });
            }
        }

        // Compute closure under all operations
        let mut universe = generators.to_vec();
        universe.sort();
        universe.dedup();

        let mut changed = true;
        while changed {
            changed = false;
            let current_universe = universe.clone();

            // Apply all operations to all combinations of elements
            for operation in &self.operations {
                let op_guard = operation.lock().unwrap();
                let arity = op_guard.arity();
                if arity == 0 {
                    // Constant operation - add result to universe
                    let result = op_guard.value(&[])?;
                    if !universe.contains(&result) {
                        universe.push(result);
                        changed = true;
                    }
                } else {
                    // Generate all combinations of arity elements from current universe
                    let mut args = vec![0; arity];
                    let mut indices = vec![0; arity];

                    loop {
                        // Set arguments for current combination
                        let mut valid_combination = true;
                        for (i, &idx) in indices.iter().enumerate() {
                            if idx >= current_universe.len() {
                                valid_combination = false;
                                break;
                            }
                            args[i] = current_universe[idx];
                        }

                        if !valid_combination {
                            // Try to increment indices
                            let mut i = arity - 1;
                            while i > 0 && indices[i] >= current_universe.len() {
                                indices[i] = 0;
                                i -= 1;
                                indices[i] += 1;
                            }

                            if i == 0 && indices[0] >= current_universe.len() {
                                break; // We're done
                            }
                            continue;
                        }

                        // Apply operation
                        let result = op_guard.value(&args)?;
                        if !universe.contains(&result) {
                            universe.push(result);
                            changed = true;
                        }

                        // Move to next combination
                        indices[arity - 1] += 1;
                    }
                }
            }
        }

        // Sort and deduplicate final universe
        universe.sort();
        universe.dedup();

        // Create subalgebra with contiguous universe [0..m)
        let new_universe: Vec<usize> = (0..universe.len()).collect();
        let mut subalgebra = BasicAlgebra::new(format!("{}_sub", self.name), new_universe.clone())?;

        // Build mapping from original universe to new universe [0..m)
        let mut map = HashMap::new();
        for (new_index, &original_element) in universe.iter().enumerate() {
            map.insert(original_element, new_index);
        }

        // For each operation, create a new TableOperation
        for operation in &self.operations {
            let op_guard = operation.lock().unwrap();
            let arity = op_guard.arity();
            let symbol_name = op_guard.symbol().name.clone();
            let universe_clone = new_universe.clone();

            // Build the table by mapping all possible argument combinations
            if arity == 0 {
                // Constant operation
                let original_result = op_guard.value(&[])?;
                let new_result =
                    map.get(&original_result)
                        .ok_or_else(|| UACalcError::InvalidOperation {
                            message: format!(
                                "Constant operation result {} not in subalgebra universe",
                                original_result
                            ),
                        })?;
                let new_operation = TableOperation::constant(
                    symbol_name.clone(),
                    *new_result,
                    universe_clone.len(),
                )?;
                subalgebra.add_operation(symbol_name, Arc::new(Mutex::new(new_operation)))?;
            } else {
                // Collect all table rows for non-constant operations
                let mut table_rows = Vec::new();

                // Generate all combinations of arity elements from new universe
                let mut args = vec![0; arity];
                let mut indices = vec![0; arity];

                loop {
                    // Set arguments for current combination
                    let mut valid_combination = true;
                    for (i, &idx) in indices.iter().enumerate() {
                        if idx >= universe_clone.len() {
                            valid_combination = false;
                            break;
                        }
                        args[i] = idx;
                    }

                    if !valid_combination {
                        // Try to increment indices
                        let mut i = arity - 1;
                        while i > 0 && indices[i] >= universe_clone.len() {
                            indices[i] = 0;
                            i -= 1;
                            indices[i] += 1;
                        }

                        if i == 0 && indices[0] >= universe_clone.len() {
                            break; // We're done
                        }
                        continue;
                    }

                    // Map arguments back to original universe
                    let mut original_args = vec![0; arity];
                    for (i, &new_arg) in args.iter().enumerate() {
                        original_args[i] = universe_clone[new_arg];
                    }

                    // Get result from original operation
                    let original_result = op_guard.value(&original_args)?;
                    let new_result =
                        map.get(&original_result)
                            .ok_or_else(|| UACalcError::InvalidOperation {
                                message: format!(
                                    "Operation result {} not in subalgebra universe",
                                    original_result
                                ),
                            })?;

                    // Create table row: [args..., result]
                    let mut row = args.clone();
                    row.push(*new_result);
                    table_rows.push(row);

                    // Move to next combination
                    indices[arity - 1] += 1;
                }

                // Create new TableOperation with collected rows
                let new_operation = TableOperation::new(
                    op_guard.symbol().clone(),
                    table_rows,
                    universe_clone.len(),
                )?;
                subalgebra.add_operation(symbol_name, Arc::new(Mutex::new(new_operation)))?;
            }
        }

        Ok(subalgebra)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::{Arc, Mutex};

    #[test]
    fn test_basic_algebra_subalgebra() -> Result<(), Box<dyn std::error::Error>> {
        // Create a basic algebra with universe {0, 1, 2, 3}
        let mut algebra = BasicAlgebra::new("test_algebra".to_string(), vec![0, 1, 2, 3])?;

        // Create a binary operation: addition modulo 4
        let add_op = Arc::new(Mutex::new(TableOperation::binary(
            "add".to_string(),
            4,
            |a, b| (a + b) % 4,
        )?));

        // Create a unary operation: negation modulo 4
        let neg_op = Arc::new(Mutex::new(TableOperation::unary(
            "neg".to_string(),
            4,
            |x| (4 - x) % 4,
        )?));

        // Add operations to algebra
        algebra.add_operation("add".to_string(), add_op)?;
        algebra.add_operation("neg".to_string(), neg_op)?;

        // Create subalgebra generated by {1}
        let subalgebra = algebra.subalgebra(&[1])?;

        // Verify subalgebra properties
        assert_eq!(subalgebra.name(), "test_algebra_sub");
        assert_eq!(subalgebra.cardinality(), 4); // Should generate the full algebra
        assert_eq!(subalgebra.universe(), &[0, 1, 2, 3]);

        // Verify operations are preserved
        assert_eq!(subalgebra.operations().len(), 2);

        // Test that operations work correctly in the subalgebra
        let add_op_sub = subalgebra.operation_arc_by_symbol("add")?;
        let neg_op_sub = subalgebra.operation_arc_by_symbol("neg")?;

        let add_guard = add_op_sub.lock().unwrap();
        let neg_guard = neg_op_sub.lock().unwrap();

        // Test addition in subalgebra
        assert_eq!(add_guard.value(&[1, 2])?, 3);
        assert_eq!(add_guard.value(&[2, 3])?, 1);
        assert_eq!(add_guard.value(&[3, 1])?, 0);

        // Test negation in subalgebra
        assert_eq!(neg_guard.value(&[1])?, 3);
        assert_eq!(neg_guard.value(&[2])?, 2);
        assert_eq!(neg_guard.value(&[3])?, 1);

        // Test subalgebra with single generator that doesn't generate everything
        let subalgebra3 = algebra.subalgebra(&[0])?;
        // This should only contain {0} since 0 + 0 = 0 and neg(0) = 0
        assert_eq!(subalgebra3.cardinality(), 1);
        assert_eq!(subalgebra3.universe(), &[0]);

        Ok(())
    }
}

/// A homomorphism from one algebra to another
/// 
/// This represents a structure-preserving map between algebras.
/// A homomorphism f: A -> B satisfies f(op_A(a1, ..., an)) = op_B(f(a1), ..., f(an))
/// for all operations op and all elements a1, ..., an in the domain.
#[derive(Clone)]
pub struct Homomorphism {
    domain: Arc<dyn SmallAlgebra>,
    range: Arc<dyn SmallAlgebra>,
    map: Vec<usize>, // map[i] is the image of element i in the domain
}

impl std::fmt::Debug for Homomorphism {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Homomorphism")
            .field("domain_name", &self.domain.name())
            .field("range_name", &self.range.name())
            .field("map", &self.map)
            .finish()
    }
}

impl Homomorphism {
    /// Create a new homomorphism
    /// 
    /// # Arguments
    /// * `domain` - The source algebra
    /// * `range` - The target algebra  
    /// * `map` - The mapping from domain elements to range elements
    /// 
    /// # Errors
    /// Returns an error if the map is invalid (wrong size, out of bounds, etc.)
    pub fn new(
        domain: Arc<dyn SmallAlgebra>,
        range: Arc<dyn SmallAlgebra>,
        map: Vec<usize>,
    ) -> UACalcResult<Self> {
        // Validate map size
        if map.len() != domain.cardinality() {
            return Err(UACalcError::InvalidOperation {
                message: format!(
                    "Map size {} does not match domain cardinality {}",
                    map.len(),
                    domain.cardinality()
                ),
            });
        }

        // Validate that all mapped values are in the range
        for &mapped_value in map.iter() {
            if mapped_value >= range.cardinality() {
                return Err(UACalcError::IndexOutOfBounds {
                    index: mapped_value,
                    size: range.cardinality(),
                });
            }
        }

        // Validate that the map preserves operations
        Self::validate_homomorphism(&domain, &range, &map)?;

        Ok(Self {
            domain,
            range,
            map,
        })
    }

    /// Get the domain algebra
    pub fn domain(&self) -> &Arc<dyn SmallAlgebra> {
        &self.domain
    }

    /// Get the range algebra
    pub fn range(&self) -> &Arc<dyn SmallAlgebra> {
        &self.range
    }

    /// Get the mapping as a slice
    pub fn map(&self) -> &[usize] {
        &self.map
    }

    /// Get the image of an element under this homomorphism
    pub fn image(&self, element: usize) -> UACalcResult<usize> {
        if element >= self.domain.cardinality() {
            return Err(UACalcError::IndexOutOfBounds {
                index: element,
                size: self.domain.cardinality(),
            });
        }
        Ok(self.map[element])
    }

    /// Check if this homomorphism is injective (one-to-one)
    pub fn is_injective(&self) -> bool {
        let mut seen = std::collections::HashSet::new();
        for &value in &self.map {
            if !seen.insert(value) {
                return false; // Found a duplicate, not injective
            }
        }
        true
    }

    /// Check if this homomorphism is surjective (onto)
    pub fn is_surjective(&self) -> bool {
        let mut range_elements = std::collections::HashSet::new();
        for &value in &self.map {
            range_elements.insert(value);
        }
        range_elements.len() == self.range.cardinality()
    }

    /// Check if this homomorphism is bijective (both injective and surjective)
    pub fn is_bijective(&self) -> bool {
        self.is_injective() && self.is_surjective()
    }

    /// Get the kernel of this homomorphism as a partition
    /// The kernel partitions the domain into equivalence classes of elements
    /// that map to the same element in the range
    pub fn kernel(&self) -> UACalcResult<crate::BasicPartition> {
        use crate::{BasicPartition, Partition};
        
        let size = self.domain.cardinality();
        let mut partition = BasicPartition::new(size);
        
        // Group elements by their image
        for i in 0..size {
            let r = partition.representative(i)?;
            for j in (i + 1)..size {
                if self.map[i] == self.map[j] {
                    let s = partition.representative(j)?;
                    if r != s {
                        partition.join_blocks(r, s)?;
                    }
                }
            }
        }
        
        Ok(partition)
    }

    /// Compose this homomorphism with another
    /// Returns a homomorphism from the domain of the first to the range of the second
    pub fn compose(&self, other: &Homomorphism) -> UACalcResult<Homomorphism> {
        // Check that the range of self matches the domain of other
        if self.range.cardinality() != other.domain.cardinality() {
            return Err(UACalcError::InvalidOperation {
                message: "Cannot compose homomorphisms: range of first does not match domain of second".to_string(),
            });
        }

        // Create the composed map
        let composed_map: Vec<usize> = self.map
            .iter()
            .map(|&x| other.map[x])
            .collect();

        Homomorphism::new(
            self.domain.clone(),
            other.range.clone(),
            composed_map,
        )
    }

    /// Validate that a map is actually a homomorphism
    fn validate_homomorphism(
        domain: &Arc<dyn SmallAlgebra>,
        range: &Arc<dyn SmallAlgebra>,
        map: &[usize],
    ) -> UACalcResult<()> {
        // Check that both algebras have the same number of operations
        if domain.operations().len() != range.operations().len() {
            return Err(UACalcError::InvalidOperation {
                message: "Domain and range must have the same number of operations".to_string(),
            });
        }

        // Check that operations have matching arities
        for i in 0..domain.operations().len() {
            let domain_op_arc = domain.operation_arc(i)?;
            let range_op_arc = range.operation_arc(i)?;
            
            let domain_op = domain_op_arc.try_lock().map_err(|_| UACalcError::InvalidOperation {
                message: "Failed to acquire domain operation lock (possible deadlock)".to_string(),
            })?;
            let range_op = range_op_arc.try_lock().map_err(|_| UACalcError::InvalidOperation {
                message: "Failed to acquire range operation lock (possible deadlock)".to_string(),
            })?;
            
            if domain_op.arity() != range_op.arity() {
                return Err(UACalcError::InvalidOperation {
                    message: format!(
                        "Operation {} has different arities: domain={}, range={}",
                        i, domain_op.arity(), range_op.arity()
                    ),
                });
            }
        }

        // Check homomorphism property for all operations
        for op_index in 0..domain.operations().len() {
            let domain_op_arc = domain.operation_arc(op_index)?;
            let range_op_arc = range.operation_arc(op_index)?;
            
            // Get arity first without holding locks
            let arity = {
                let domain_op = domain_op_arc.try_lock().map_err(|_| UACalcError::InvalidOperation {
                    message: "Failed to acquire domain operation lock for arity check".to_string(),
                })?;
                domain_op.arity()
            };

            // For each possible input tuple
            for args in Self::generate_argument_tuples(domain.cardinality(), arity) {
                // Compute operation in domain
                let domain_result = {
                    let domain_op = domain_op_arc.try_lock().map_err(|_| UACalcError::InvalidOperation {
                        message: "Failed to acquire domain operation lock for computation".to_string(),
                    })?;
                    domain_op.int_value_at(&args)?
                };
                
                // Apply homomorphism to arguments
                let mapped_args: Vec<usize> = args.iter().map(|&x| map[x]).collect();
                
                // Compute operation in range on mapped arguments
                let range_result = {
                    let range_op = range_op_arc.try_lock().map_err(|_| UACalcError::InvalidOperation {
                        message: "Failed to acquire range operation lock for computation".to_string(),
                    })?;
                    range_op.int_value_at(&mapped_args)?
                };
                
                // Apply homomorphism to domain result
                let mapped_domain_result = map[domain_result];
                
                // Check homomorphism property
                if mapped_domain_result != range_result {
                    return Err(UACalcError::InvalidOperation {
                        message: format!(
                            "Homomorphism property violated for operation {}: f(op({:?})) = {} != op(f({:?})) = {}",
                            op_index, args, mapped_domain_result, mapped_args, range_result
                        ),
                    });
                }
            }
        }

        Ok(())
    }

    /// Generate all possible argument tuples of given arity for a given set size
    fn generate_argument_tuples(set_size: usize, arity: usize) -> Vec<Vec<usize>> {
        if arity == 0 {
            return vec![vec![]];
        }

        let mut tuples = Vec::new();
        let mut current = vec![0; arity];
        
        loop {
            tuples.push(current.clone());
            
            // Increment the tuple
            let mut i = arity;
            while i > 0 {
                i -= 1;
                current[i] += 1;
                if current[i] < set_size {
                    break;
                }
                current[i] = 0;
            }
            
            // If we've wrapped around, we're done
            if i == 0 && current[0] == 0 {
                break;
            }
        }
        
        tuples
    }
}

/// Find a homomorphism from one algebra to another
/// 
/// This is a brute-force search that tries all possible mappings.
/// For large algebras, this will be very slow.
pub fn find_homomorphism(
    domain: Arc<dyn SmallAlgebra>,
    range: Arc<dyn SmallAlgebra>,
) -> UACalcResult<Option<Homomorphism>> {
    // Check basic compatibility
    if domain.operations().len() != range.operations().len() {
        return Ok(None);
    }

    // Check operation arities match
    for i in 0..domain.operations().len() {
        let domain_op_arc = domain.operation_arc(i)?;
        let range_op_arc = range.operation_arc(i)?;
        
        // Get arities without holding both locks simultaneously
        let domain_arity = {
            let domain_op = domain_op_arc.try_lock().map_err(|_| UACalcError::InvalidOperation {
                message: "Failed to acquire domain operation lock (possible deadlock)".to_string(),
            })?;
            domain_op.arity()
        };
        
        let range_arity = {
            let range_op = range_op_arc.try_lock().map_err(|_| UACalcError::InvalidOperation {
                message: "Failed to acquire range operation lock (possible deadlock)".to_string(),
            })?;
            range_op.arity()
        };
        
        if domain_arity != range_arity {
            return Ok(None);
        }
    }

    // Try all possible mappings
    let domain_size = domain.cardinality();
    let range_size = range.cardinality();
    
    // Generate all possible mappings
    for mapping in generate_all_mappings(domain_size, range_size) {
        if let Ok(homomorphism) = Homomorphism::new(domain.clone(), range.clone(), mapping) {
            return Ok(Some(homomorphism));
        }
    }

    Ok(None)
}

/// Generate all possible mappings from a set of size n to a set of size m
fn generate_all_mappings(n: usize, m: usize) -> Vec<Vec<usize>> {
    if n == 0 {
        return vec![vec![]];
    }

    let mut mappings = Vec::new();
    let mut current = vec![0; n];
    
    loop {
        mappings.push(current.clone());
        
        // Increment the mapping
        let mut i = n;
        while i > 0 {
            i -= 1;
            current[i] += 1;
            if current[i] < m {
                break;
            }
            current[i] = 0;
        }
        
        // If we've wrapped around, we're done
        if i == 0 && current[0] == 0 {
            break;
        }
    }
    
    mappings
}

/// Check if two algebras are isomorphic
pub fn are_isomorphic(
    algebra1: Arc<dyn SmallAlgebra>,
    algebra2: Arc<dyn SmallAlgebra>,
) -> UACalcResult<bool> {
    // Basic checks
    if algebra1.cardinality() != algebra2.cardinality() {
        return Ok(false);
    }

    if algebra1.operations().len() != algebra2.operations().len() {
        return Ok(false);
    }

    // Check operation arities
    for i in 0..algebra1.operations().len() {
        let op1_arc = algebra1.operation_arc(i)?;
        let op2_arc = algebra2.operation_arc(i)?;
        
        // Get arities without holding both locks simultaneously
        let op1_arity = {
            let op1 = op1_arc.try_lock().map_err(|_| UACalcError::InvalidOperation {
                message: "Failed to acquire operation 1 lock (possible deadlock)".to_string(),
            })?;
            op1.arity()
        };
        
        let op2_arity = {
            let op2 = op2_arc.try_lock().map_err(|_| UACalcError::InvalidOperation {
                message: "Failed to acquire operation 2 lock (possible deadlock)".to_string(),
            })?;
            op2.arity()
        };
        
        if op1_arity != op2_arity {
            return Ok(false);
        }
    }

    // Try to find an isomorphism
    if let Some(homomorphism) = find_homomorphism(algebra1.clone(), algebra2.clone())? {
        Ok(homomorphism.is_bijective())
    } else {
        Ok(false)
    }
}
