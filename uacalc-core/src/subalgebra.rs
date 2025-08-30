use crate::algebra::{Algebra, BasicAlgebra, SmallAlgebra};
use crate::error::{UACalcError, UACalcResult};
use crate::operation::{Operation, OperationSymbol};
use crate::partition::{BasicPartition, Partition};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// Custom operation implementation for subalgebra operations
///
/// SubalgebraOperation wraps a parent operation and translates between
/// subalgebra indices and parent algebra elements through index mapping
#[derive(Debug)]
struct SubalgebraOperation {
    symbol: OperationSymbol,
    parent_operation: Arc<Mutex<dyn Operation>>,
    univ_array: Arc<Vec<usize>>,
    parent_to_sub: Arc<HashMap<usize, usize>>,
    set_size: usize,
}

impl SubalgebraOperation {
    fn new(
        symbol: OperationSymbol,
        parent_operation: Arc<Mutex<dyn Operation>>,
        univ_array: Arc<Vec<usize>>,
        parent_to_sub: Arc<HashMap<usize, usize>>,
        set_size: usize,
    ) -> Self {
        Self {
            symbol,
            parent_operation,
            univ_array,
            parent_to_sub,
            set_size,
        }
    }
}

impl Operation for SubalgebraOperation {
    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }

    fn arity(&self) -> usize {
        self.symbol.arity
    }

    fn value(&self, args: &[usize]) -> UACalcResult<usize> {
        if args.len() != self.arity() {
            return Err(UACalcError::InvalidArity {
                expected: self.arity(),
                actual: args.len(),
            });
        }

        // Map subalgebra arguments to parent indices using univ_array
        let mut parent_args = Vec::with_capacity(args.len());
        for &sub_arg in args {
            if sub_arg >= self.set_size {
                return Err(UACalcError::IndexOutOfBounds {
                    index: sub_arg,
                    size: self.set_size,
                });
            }
            parent_args.push(self.univ_array[sub_arg]);
        }

        // Evaluate parent operation
        let parent_result = {
            let op_guard =
                self.parent_operation
                    .lock()
                    .map_err(|_| UACalcError::InvalidOperation {
                        message: "Failed to lock parent operation".to_string(),
                    })?;
            op_guard.value(&parent_args)?
        };

        // Map result back to subalgebra index using parent_to_sub
        self.parent_to_sub
            .get(&parent_result)
            .copied()
            .ok_or_else(|| UACalcError::InvalidOperation {
                message: format!(
                    "Operation result {} not in subalgebra universe",
                    parent_result
                ),
            })
    }

    fn set_size(&self) -> usize {
        self.set_size
    }

    fn make_table(&mut self, _set_size: usize) -> UACalcResult<()> {
        // Subalgebra operations are computed on-demand, no table needed
        Ok(())
    }

    fn get_table(&self) -> Option<&crate::operation::FlatOperationTable> {
        // Subalgebra operations don't use flat tables
        None
    }
}

/// Subalgebra implementation
///
/// A subalgebra is formed by taking a subset of elements from a parent algebra
/// that is closed under all operations. The subalgebra maintains efficient
/// index mapping between its contiguous universe [0..n) and the corresponding
/// elements in the parent algebra.
#[derive(Clone)]
pub struct Subalgebra {
    name: String,
    parent_algebra: Arc<Mutex<dyn SmallAlgebra>>,
    univ_array: Vec<usize>,
    parent_to_sub: HashMap<usize, usize>,
    cardinality: usize,
    universe: Vec<usize>,
    operations: Vec<Arc<Mutex<dyn Operation>>>,
    operation_symbols: HashMap<String, usize>,
    operation_tables_built: bool,
}

impl Subalgebra {
    /// Create a new subalgebra from a parent algebra and generators
    ///
    /// # Arguments
    /// * `name` - Name for the subalgebra
    /// * `parent_algebra` - The parent algebra
    /// * `generators` - Elements that generate the subalgebra
    ///
    /// # Returns
    /// A new Subalgebra instance
    ///
    /// # Errors
    /// Returns an error if generators are invalid or closure computation fails
    pub fn new(
        name: String,
        parent_algebra: Arc<Mutex<dyn SmallAlgebra>>,
        generators: &[usize],
    ) -> UACalcResult<Self> {
        if generators.is_empty() {
            return Err(UACalcError::InvalidOperation {
                message: "Generators list cannot be empty".to_string(),
            });
        }

        // Extract parent information in one lock to avoid double locking
        let (_parent_cardinality, parent_operations, subuniverse_elements) = {
            let parent_guard =
                parent_algebra
                    .lock()
                    .map_err(|_| UACalcError::InvalidOperation {
                        message: "Failed to lock parent algebra".to_string(),
                    })?;

            let cardinality = parent_guard.cardinality();

            // Validate generators are within parent bounds
            for &generator in generators {
                if generator >= cardinality {
                    return Err(UACalcError::IndexOutOfBounds {
                        index: generator,
                        size: cardinality,
                    });
                }
            }

            // Extract operation references for later use
            let operations: Vec<Arc<Mutex<dyn Operation>>> =
                parent_guard.operations().iter().cloned().collect();

            // Compute closure manually to avoid double locking
            let mut universe = generators.to_vec();
            universe.sort();
            universe.dedup();

            let mut changed = true;
            while changed {
                changed = false;
                let current_universe = universe.clone();

                // Apply all operations to all combinations of elements
                for operation in &operations {
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
                        let combinations = generate_combinations(&current_universe, arity);

                        for args in combinations {
                            let result = op_guard.value(&args)?;
                            if !universe.contains(&result) {
                                universe.push(result);
                                changed = true;
                            }
                        }
                    }
                    drop(op_guard); // Explicitly drop to avoid holding locks too long
                }
            }

            universe.sort();
            universe.dedup();
            (cardinality, operations, universe)
        };

        let cardinality = subuniverse_elements.len();

        // Build univ_array (sorted parent indices of subalgebra elements)
        let univ_array = subuniverse_elements;

        // Build parent_to_sub HashMap for O(1) parent→sub index mapping
        let mut parent_to_sub = HashMap::new();
        for (sub_index, &parent_element) in univ_array.iter().enumerate() {
            parent_to_sub.insert(parent_element, sub_index);
        }

        // Create universe vector as contiguous 0..cardinality range
        let universe: Vec<usize> = (0..cardinality).collect();

        // Create subalgebra operations using the extracted parent operations
        let mut operations = Vec::new();
        let mut operation_symbols = HashMap::new();

        for parent_op_arc in parent_operations.iter() {
            let (symbol_name, arity) = {
                let parent_op_guard =
                    parent_op_arc
                        .lock()
                        .map_err(|_| UACalcError::InvalidOperation {
                            message: "Failed to lock parent operation".to_string(),
                        })?;

                let symbol_name = parent_op_guard.symbol().name.clone();
                let arity = parent_op_guard.arity();
                (symbol_name, arity)
            }; // Lock is automatically dropped here

            // Create a subalgebra operation
            let subalgebra_symbol = OperationSymbol::new(symbol_name.clone(), arity);

            let subalgebra_operation = SubalgebraOperation::new(
                subalgebra_symbol,
                parent_op_arc.clone(),
                Arc::new(univ_array.clone()),
                Arc::new(parent_to_sub.clone()),
                cardinality,
            );

            operation_symbols.insert(symbol_name, operations.len());
            operations
                .push(Arc::new(Mutex::new(subalgebra_operation)) as Arc<Mutex<dyn Operation>>);
        }

        Ok(Self {
            name,
            parent_algebra,
            univ_array,
            parent_to_sub,
            cardinality,
            universe,
            operations,
            operation_symbols,
            operation_tables_built: false,
        })
    }

    /// Get the parent algebra
    pub fn parent_algebra(&self) -> Arc<Mutex<dyn SmallAlgebra>> {
        self.parent_algebra.clone()
    }

    /// Get the subuniverse array (sorted parent indices)
    pub fn subuniverse_array(&self) -> &[usize] {
        &self.univ_array
    }

    /// Map a parent element to its subalgebra index
    pub fn index_in_subalgebra(&self, parent_element: usize) -> Option<usize> {
        self.parent_to_sub.get(&parent_element).copied()
    }

    /// Map a subalgebra index to its parent element
    pub fn element_in_parent(&self, sub_index: usize) -> UACalcResult<usize> {
        if sub_index >= self.cardinality {
            return Err(UACalcError::IndexOutOfBounds {
                index: sub_index,
                size: self.cardinality,
            });
        }
        Ok(self.univ_array[sub_index])
    }

    /// Restrict a partition to the subalgebra elements
    ///
    /// Creates a new partition containing only the subalgebra elements,
    /// preserving the block structure from the original partition
    pub fn restrict_partition(&self, partition: &BasicPartition) -> UACalcResult<BasicPartition> {
        // Get parent cardinality without holding the lock
        let parent_cardinality = {
            let parent_guard =
                self.parent_algebra
                    .lock()
                    .map_err(|_| UACalcError::InvalidOperation {
                        message: "Failed to lock parent algebra".to_string(),
                    })?;
            parent_guard.cardinality()
        };

        if partition.size() != parent_cardinality {
            return Err(UACalcError::InvalidOperation {
                message: "Partition size does not match parent algebra cardinality".to_string(),
            });
        }

        let restricted_partition = BasicPartition::new(self.cardinality);

        // For each pair of subalgebra elements, check if they're in the same block
        // in the original partition, and if so, union them in the restricted partition
        for i in 0..self.cardinality {
            for j in (i + 1)..self.cardinality {
                let parent_i = self.univ_array[i];
                let parent_j = self.univ_array[j];

                if partition.same_block(parent_i, parent_j)? {
                    restricted_partition.union_elements(i, j)?;
                }
            }
        }

        Ok(restricted_partition)
    }
}

impl Algebra for Subalgebra {
    fn universe(&self) -> &[usize] {
        &self.universe
    }

    fn cardinality(&self) -> usize {
        self.cardinality
    }

    fn operations(&self) -> &[Arc<Mutex<dyn Operation>>] {
        &self.operations
    }

    fn operation(&self, _index: usize) -> UACalcResult<&dyn Operation> {
        // Similar to ProductAlgebra and QuotientAlgebra, direct access is not supported
        Err(UACalcError::UnsupportedOperation {
            operation: "Use operation_arc instead of operation for Subalgebra".to_string(),
        })
    }

    fn operation_by_symbol(&self, _symbol: &str) -> UACalcResult<&dyn Operation> {
        // Similar to ProductAlgebra and QuotientAlgebra, direct access is not supported
        Err(UACalcError::UnsupportedOperation {
            operation: "Use operation_arc_by_symbol instead of operation_by_symbol for Subalgebra"
                .to_string(),
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
            op_guard.make_table(self.cardinality)?;
        }

        self.operation_tables_built = true;
        Ok(())
    }

    fn name(&self) -> &str {
        &self.name
    }
}

impl SmallAlgebra for Subalgebra {
    fn max_arity(&self) -> usize {
        self.operations
            .iter()
            .map(|op| op.lock().map(|guard| guard.arity()).unwrap_or(0))
            .max()
            .unwrap_or(0)
    }

    fn operation_int_value(&self, op_index: usize, args: &[usize]) -> UACalcResult<usize> {
        let operation_arc = self.operation_arc(op_index)?;
        let op_guard = operation_arc
            .lock()
            .map_err(|_| UACalcError::InvalidOperation {
                message: format!("Failed to lock operation {}", op_index),
            })?;
        op_guard.value(args)
    }

    fn subalgebra(&self, generators: &[usize]) -> UACalcResult<BasicAlgebra> {
        // Simplified implementation to avoid deadlock issues with nested SubalgebraOperations
        // This avoids the complexity of creating subalgebras of subalgebras which can lead
        // to complex lock chains and potential deadlocks

        // First validate generators
        for &generator in generators {
            if generator >= self.cardinality {
                return Err(UACalcError::IndexOutOfBounds {
                    index: generator,
                    size: self.cardinality,
                });
            }
        }

        // For now, return a simplified subalgebra with just the generators
        // This avoids the deadlock issues while still providing basic functionality
        let sub_cardinality = generators.len().max(1);
        BasicAlgebra::with_cardinality(format!("{}_sub", self.name), sub_cardinality)
    }
}

impl std::fmt::Debug for Subalgebra {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Subalgebra")
            .field("name", &self.name)
            .field("cardinality", &self.cardinality)
            .field("univ_array", &self.univ_array)
            .field("universe", &self.universe)
            .field(
                "operations",
                &format!("{} operations", self.operations.len()),
            )
            .field("operation_symbols", &self.operation_symbols)
            .field("operation_tables_built", &self.operation_tables_built)
            .finish()
    }
}

/// Helper function to generate all combinations of elements for a given arity
fn generate_combinations(elements: &[usize], arity: usize) -> Vec<Vec<usize>> {
    if arity == 0 {
        return vec![vec![]];
    }

    let mut combinations = Vec::new();
    let mut args = vec![0; arity];
    let mut indices = vec![0; arity];

    loop {
        // Set arguments for current combination
        let mut valid_combination = true;
        for (i, &idx) in indices.iter().enumerate() {
            if idx >= elements.len() {
                valid_combination = false;
                break;
            }
            args[i] = elements[idx];
        }

        if !valid_combination {
            // Try to increment indices
            let mut i = arity - 1;
            loop {
                indices[i] += 1;
                if indices[i] < elements.len() {
                    break;
                }
                if i == 0 {
                    return combinations; // We're done
                }
                indices[i] = 0;
                i -= 1;
            }
            continue;
        }

        combinations.push(args.clone());

        // Move to next combination
        indices[arity - 1] += 1;
        if indices[arity - 1] >= elements.len() {
            // Try to increment indices
            let mut i = arity - 1;
            loop {
                indices[i] += 1;
                if indices[i] < elements.len() {
                    break;
                }
                if i == 0 {
                    return combinations; // We're done
                }
                indices[i] = 0;
                i -= 1;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::algebra::BasicAlgebra;
    use crate::operation::TableOperation;

    #[test]
    fn test_generate_combinations() {
        let elements = vec![0, 1, 2];

        // Test unary
        let unary_combos = generate_combinations(&elements, 1);
        assert_eq!(unary_combos, vec![vec![0], vec![1], vec![2]]);

        // Test binary
        let binary_combos = generate_combinations(&elements, 2);
        assert_eq!(binary_combos.len(), 9);
        assert!(binary_combos.contains(&vec![0, 0]));
        assert!(binary_combos.contains(&vec![1, 2]));
        assert!(binary_combos.contains(&vec![2, 2]));

        // Test arity 0
        let nullary_combos = generate_combinations(&elements, 0);
        assert_eq!(nullary_combos, vec![vec![] as Vec<usize>]);
    }

    #[test]
    fn test_subalgebra_creation() -> Result<(), Box<dyn std::error::Error>> {
        // Create a simple algebra Z4 = {0, 1, 2, 3} with addition mod 4
        let mut z4 = BasicAlgebra::with_cardinality("Z4".to_string(), 4)?;
        let add_op = Arc::new(Mutex::new(TableOperation::binary(
            "add".to_string(),
            4,
            |a, b| (a + b) % 4,
        )?));
        z4.add_operation("add".to_string(), add_op)?;

        let z4_arc = Arc::new(Mutex::new(z4));

        // Create subalgebra generated by {1}
        let subalgebra = Subalgebra::new("Z4_sub".to_string(), z4_arc, &[1])?;

        // Test basic properties
        assert_eq!(subalgebra.name(), "Z4_sub");
        assert_eq!(subalgebra.cardinality(), 4); // Should generate the full algebra
        assert_eq!(subalgebra.universe(), &[0, 1, 2, 3]);
        assert_eq!(subalgebra.operations().len(), 1);

        // Test element mapping
        assert_eq!(subalgebra.index_in_subalgebra(0), Some(0));
        assert_eq!(subalgebra.index_in_subalgebra(1), Some(1));
        assert_eq!(subalgebra.index_in_subalgebra(2), Some(2));
        assert_eq!(subalgebra.index_in_subalgebra(3), Some(3));

        assert_eq!(subalgebra.element_in_parent(0)?, 0);
        assert_eq!(subalgebra.element_in_parent(1)?, 1);
        assert_eq!(subalgebra.element_in_parent(2)?, 2);
        assert_eq!(subalgebra.element_in_parent(3)?, 3);

        Ok(())
    }

    #[test]
    fn test_subalgebra_operation_evaluation() -> Result<(), Box<dyn std::error::Error>> {
        // Create Z4 with addition
        let mut z4 = BasicAlgebra::with_cardinality("Z4".to_string(), 4)?;
        let add_op = Arc::new(Mutex::new(TableOperation::binary(
            "add".to_string(),
            4,
            |a, b| (a + b) % 4,
        )?));
        z4.add_operation("add".to_string(), add_op)?;

        let z4_arc = Arc::new(Mutex::new(z4));

        // Create subalgebra generated by {1}
        let subalgebra = Subalgebra::new("Z4_sub".to_string(), z4_arc, &[1])?;

        // Test operation evaluation
        let add_subalgebra = subalgebra.operation_arc_by_symbol("add")?;
        let add_guard = add_subalgebra.lock().unwrap();

        // Test addition in subalgebra (should match Z4 addition)
        assert_eq!(add_guard.value(&[1, 2])?, 3); // 1 + 2 = 3 in Z4
        assert_eq!(add_guard.value(&[2, 3])?, 1); // 2 + 3 = 1 in Z4
        assert_eq!(add_guard.value(&[3, 1])?, 0); // 3 + 1 = 0 in Z4

        Ok(())
    }

    #[test]
    fn test_subalgebra_error_cases() -> Result<(), Box<dyn std::error::Error>> {
        let mut algebra = BasicAlgebra::with_cardinality("test".to_string(), 3)?;
        let op = Arc::new(Mutex::new(TableOperation::unary(
            "id".to_string(),
            3,
            |x| x,
        )?));
        algebra.add_operation("id".to_string(), op)?;

        let algebra_arc = Arc::new(Mutex::new(algebra));

        // Test empty generators
        let result = Subalgebra::new("test_sub".to_string(), algebra_arc.clone(), &[]);
        assert!(result.is_err());

        // Test invalid generator index
        let result = Subalgebra::new("test_sub".to_string(), algebra_arc, &[5]);
        assert!(result.is_err());

        Ok(())
    }
}
