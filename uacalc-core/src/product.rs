use crate::algebra::{Algebra, BasicAlgebra, SmallAlgebra};
use crate::error::{UACalcError, UACalcResult};
use crate::operation::{FlatOperationTable, Operation, OperationSymbol};
use crate::partition::BasicPartition;
use crate::utils::{horner_decode, horner_table_size, mixed_radix_decode, mixed_radix_encode};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// Componentwise table operation that computes results on-demand
/// This avoids pre-computing the full table which can be enormous for large product algebras
#[derive(Debug)]
struct ComponentwiseTableOperation {
    symbol: OperationSymbol,
    factor_operations: Vec<Arc<Mutex<dyn Operation>>>,
    factor_sizes: Vec<usize>,
    cardinality: usize,
    table: Option<FlatOperationTable>,
}

impl ComponentwiseTableOperation {
    fn new(
        symbol: OperationSymbol,
        factor_operations: Vec<Arc<Mutex<dyn Operation>>>,
        factor_sizes: Vec<usize>,
        cardinality: usize,
    ) -> UACalcResult<Self> {
        Ok(Self {
            symbol,
            factor_operations,
            factor_sizes,
            cardinality,
            table: None,
        })
    }

    /// Decode a product element into its coordinates
    fn decode_element(&self, element: usize) -> Vec<usize> {
        mixed_radix_decode(element, &self.factor_sizes)
    }

    /// Encode coordinates back to a product element
    fn encode_coordinates(&self, coordinates: &[usize]) -> UACalcResult<usize> {
        mixed_radix_encode(coordinates, &self.factor_sizes).ok_or_else(|| {
            UACalcError::InvalidOperation {
                message: "Failed to encode coordinates".to_string(),
            }
        })
    }

    /// Helper method to compute componentwise result for given arguments
    /// Optimized to reduce allocations by reusing buffers
    fn compute_componentwise_result(&self, args: &[usize]) -> UACalcResult<usize> {
        if args.len() != self.arity() {
            return Err(UACalcError::InvalidArity {
                expected: self.arity(),
                actual: args.len(),
            });
        }

        let num_factors = self.factor_operations.len();
        let arity = self.arity();

        // Pre-allocate factor argument buffers for each factor
        let mut factor_args_buffers: Vec<Vec<usize>> = Vec::with_capacity(num_factors);
        for _ in 0..num_factors {
            factor_args_buffers.push(Vec::with_capacity(arity));
        }

        // Decode each argument once and distribute coordinates to factor buffers
        for &arg in args {
            let coordinates = self.decode_element(arg);
            for (factor_idx, &coord) in coordinates.iter().enumerate() {
                if factor_idx < num_factors {
                    factor_args_buffers[factor_idx].push(coord);
                } else {
                    return Err(UACalcError::InvalidOperation {
                        message: format!("Coordinate index {} out of range", factor_idx),
                    });
                }
            }
        }

        // Apply each factor operation and collect results
        let mut result_coordinates = Vec::with_capacity(num_factors);
        for (i, factor_op) in self.factor_operations.iter().enumerate() {
            let op_guard = factor_op
                .lock()
                .map_err(|_| UACalcError::InvalidOperation {
                    message: format!("Failed to lock factor operation {}", i),
                })?;

            // Apply the factor operation using the pre-filled buffer
            let factor_result = op_guard.value(&factor_args_buffers[i])?;
            result_coordinates.push(factor_result);

            // Clear the buffer for potential reuse (if this method gets called repeatedly)
            factor_args_buffers[i].clear();
        }

        // Encode the result coordinates back to a product element
        self.encode_coordinates(&result_coordinates)
    }
}

impl Operation for ComponentwiseTableOperation {
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

        // Use table if available, otherwise compute on-demand
        if let Some(ref table) = self.table {
            table.get_value(args)
        } else {
            self.compute_componentwise_result(args)
        }
    }

    fn get_table(&self) -> Option<&FlatOperationTable> {
        self.table.as_ref()
    }

    fn set_size(&self) -> usize {
        self.cardinality
    }

    fn make_table(&mut self, set_size: usize) -> UACalcResult<()> {
        if set_size != self.cardinality {
            return Err(UACalcError::InvalidOperation {
                message: format!("set_size mismatch: {} != {}", set_size, self.cardinality),
            });
        }

        let mut flat_table = FlatOperationTable::new(self.arity(), set_size)?;

        // Populate the table using Horner encoding
        let arity = self.arity();
        let table_len =
            horner_table_size(arity, set_size).ok_or(UACalcError::InvalidOperation {
                message: "Table size would overflow".to_string(),
            })?;

        for idx in 0..table_len {
            let args = horner_decode(idx, arity, set_size);
            let result = self.compute_componentwise_result(&args)?;
            if result >= set_size {
                return Err(UACalcError::IndexOutOfBounds {
                    index: result,
                    size: set_size,
                });
            }
            flat_table.set(idx, result)?;
        }

        self.table = Some(flat_table);
        Ok(())
    }
    
    fn as_any(&self) -> &dyn std::any::Any {
        self
    }
}

/// Product algebra implementation that creates the direct product of multiple algebras
pub struct ProductAlgebra {
    name: String,
    factors: Vec<Arc<Mutex<dyn SmallAlgebra>>>,
    cardinality: usize,
    factor_sizes: Vec<usize>,
    universe: Vec<usize>,
    operations: Vec<Arc<Mutex<dyn Operation>>>,
    operation_symbols: HashMap<String, usize>,
    operation_tables_built: bool,
}

impl ProductAlgebra {
    /// Create a new product algebra from a list of factor algebras
    pub fn new(name: String, factors: Vec<Arc<Mutex<dyn SmallAlgebra>>>) -> UACalcResult<Self> {
        if factors.is_empty() {
            return Err(UACalcError::InvalidOperation {
                message: "Product algebra must have at least one factor".to_string(),
            });
        }

        let num_factors = factors.len();
        let mut factor_sizes = Vec::with_capacity(num_factors);
        let mut cardinality: usize = 1;

        // Calculate factor sizes and total cardinality
        for factor in &factors {
            let factor_guard = factor.lock().map_err(|_| UACalcError::InvalidOperation {
                message: "Failed to lock factor algebra".to_string(),
            })?;
            let size = factor_guard.cardinality();
            factor_sizes.push(size);

            cardinality =
                cardinality
                    .checked_mul(size)
                    .ok_or_else(|| UACalcError::ArithmeticOverflow {
                        operation: "calculating product cardinality".to_string(),
                    })?;
        }

        // Validate operation compatibility by symbol name across factors
        // Build a HashMap<String,(arity, index)> for the first factor
        let first_factor_ops = {
            let first_factor = &factors[0];
            let first_guard = first_factor
                .lock()
                .map_err(|_| UACalcError::InvalidOperation {
                    message: "Failed to lock first factor algebra".to_string(),
                })?;

            let mut op_map = HashMap::new();
            for (index, op_arc) in first_guard.operations().iter().enumerate() {
                let op_guard = op_arc.lock().map_err(|_| UACalcError::InvalidOperation {
                    message: format!("Failed to lock operation {} in first factor", index),
                })?;
                let symbol_name = op_guard.symbol().name.clone();
                let arity = op_guard.arity();
                op_map.insert(symbol_name, (arity, index));
            }
            op_map
        };

        // Clone factors to avoid borrow checker issues
        let factors_clone = factors.clone();

        // For each other factor, ensure the same symbol set and arity
        for (i, factor) in factors.iter().enumerate().skip(1) {
            let factor_guard = factor.lock().map_err(|_| UACalcError::InvalidOperation {
                message: format!("Failed to lock factor algebra {}", i),
            })?;

            // Check that this factor has the same number of operations
            if factor_guard.operations().len() != first_factor_ops.len() {
                return Err(UACalcError::InvalidOperation {
                    message: format!(
                        "Factor {} has {} operations, but first factor has {}",
                        i,
                        factor_guard.operations().len(),
                        first_factor_ops.len()
                    ),
                });
            }

            // Build symbol map for this factor
            let mut factor_op_map = HashMap::new();
            for op_arc in factor_guard.operations().iter() {
                let op_guard = op_arc.lock().map_err(|_| UACalcError::InvalidOperation {
                    message: format!("Failed to lock operation in factor {}", i),
                })?;
                let symbol_name = op_guard.symbol().name.clone();
                let arity = op_guard.arity();
                factor_op_map.insert(symbol_name, arity);
            }

            // Verify that each operation in the first factor exists with same arity in this factor
            for (symbol_name, (first_arity, _)) in &first_factor_ops {
                match factor_op_map.get(symbol_name) {
                    Some(&factor_arity) => {
                        if factor_arity != *first_arity {
                            return Err(UACalcError::InvalidOperation {
                                message: format!(
                                    "Operation '{}' has arity {} in factor {} but {} in first factor",
                                    symbol_name, factor_arity, i, first_arity
                                ),
                            });
                        }
                    }
                    None => {
                        return Err(UACalcError::InvalidOperation {
                            message: format!(
                                "Operation '{}' exists in first factor but not in factor {}",
                                symbol_name, i
                            ),
                        });
                    }
                }
            }

            // Verify that this factor doesn't have extra operations
            for symbol_name in factor_op_map.keys() {
                if !first_factor_ops.contains_key(symbol_name) {
                    return Err(UACalcError::InvalidOperation {
                        message: format!(
                            "Operation '{}' exists in factor {} but not in first factor",
                            symbol_name, i
                        ),
                    });
                }
            }
        }

        // Create componentwise operations by iterating the first factor's symbol order
        // and fetching corresponding ops by symbol from all factors
        let mut operations = Vec::new();
        let mut operation_symbols = HashMap::new();

        // Sort operations by symbol name for consistent ordering
        let mut sorted_ops: Vec<_> = first_factor_ops.iter().collect();
        sorted_ops.sort_by(|a, b| a.0.cmp(b.0));

        for (symbol_name, (arity, _)) in sorted_ops {
            // Collect operations from all factors using operation_arc_by_symbol
            let mut factor_ops = Vec::new();
            for factor in &factors {
                let factor_guard = factor.lock().map_err(|_| UACalcError::InvalidOperation {
                    message: "Failed to lock factor algebra".to_string(),
                })?;
                let factor_op =
                    factor_guard
                        .operation_arc_by_symbol(symbol_name)
                        .map_err(|_| UACalcError::InvalidOperation {
                            message: format!(
                                "Failed to find operation '{}' in factor",
                                symbol_name
                            ),
                        })?;
                factor_ops.push(factor_op);
            }

            // Create a componentwise operation that computes results on-demand
            let componentwise_op = ComponentwiseTableOperation::new(
                OperationSymbol::new(symbol_name.clone(), *arity),
                factor_ops,
                factor_sizes.clone(),
                cardinality,
            )?;

            // Add to operations list
            let op_arc: Arc<Mutex<dyn Operation>> = Arc::new(Mutex::new(componentwise_op));
            operation_symbols.insert(symbol_name.clone(), operations.len());
            operations.push(op_arc);
        }

        // Create universe vector
        let universe: Vec<usize> = (0..cardinality).collect();
        Ok(Self {
            name,
            factors: factors_clone,
            cardinality,
            factor_sizes,
            universe,
            operations,
            operation_symbols,
            operation_tables_built: false,
        })
    }

    /// Get the factor algebras
    pub fn factors(&self) -> &[Arc<Mutex<dyn SmallAlgebra>>] {
        &self.factors
    }

    /// Get the k-th factor algebra
    pub fn projection(&self, k: usize) -> UACalcResult<Arc<Mutex<dyn SmallAlgebra>>> {
        if k >= self.factors.len() {
            return Err(UACalcError::IndexOutOfBounds {
                index: k,
                size: self.factors.len(),
            });
        }
        Ok(self.factors[k].clone())
    }

    /// Get the projection kernel for the k-th factor
    pub fn projection_kernel(&self, k: usize) -> UACalcResult<BasicPartition> {
        if k >= self.factors.len() {
            return Err(UACalcError::IndexOutOfBounds {
                index: k,
                size: self.factors.len(),
            });
        }

        let partition = BasicPartition::new(self.cardinality);
        let factor_size = self.factor_sizes[k];

        // Store representatives for each coordinate value
        let mut representatives: Vec<Option<usize>> = vec![None; factor_size];

        // Iterate through all elements and group by coordinate projection
        for x in 0..self.cardinality {
            let c = self.coordinate_projection(x, k)?;

            if let Some(rep) = representatives[c] {
                // Union x with existing representative
                partition.union_elements(rep, x)?;
            } else {
                // Set x as the representative for coordinate c
                representatives[c] = Some(x);
            }
        }

        Ok(partition)
    }

    /// Extract the k-th coordinate from a product element
    pub fn coordinate_projection(&self, element: usize, k: usize) -> UACalcResult<usize> {
        if element >= self.cardinality {
            return Err(UACalcError::IndexOutOfBounds {
                index: element,
                size: self.cardinality,
            });
        }
        if k >= self.factors.len() {
            return Err(UACalcError::IndexOutOfBounds {
                index: k,
                size: self.factors.len(),
            });
        }

        let coordinates = self.decode_coords(element);
        if coordinates.len() <= k {
            return Err(UACalcError::InvalidOperation {
                message: "Failed to decode element coordinates".to_string(),
            });
        }
        Ok(coordinates[k])
    }

    /// Create a product element from coordinates
    pub fn coordinate_embedding(&self, coordinates: &[usize]) -> UACalcResult<usize> {
        if coordinates.len() != self.factors.len() {
            return Err(UACalcError::InvalidArity {
                expected: self.factors.len(),
                actual: coordinates.len(),
            });
        }

        // Validate coordinates are within bounds
        for (i, &coord) in coordinates.iter().enumerate() {
            if coord >= self.factor_sizes[i] {
                return Err(UACalcError::IndexOutOfBounds {
                    index: coord,
                    size: self.factor_sizes[i],
                });
            }
        }

        self.encode_coords(coordinates)
    }

    /// Decode a product element into its coordinates using consistent mixed-radix scheme
    pub fn decode_coords(&self, element: usize) -> Vec<usize> {
        mixed_radix_decode(element, &self.factor_sizes)
    }

    /// Encode coordinates back to a product element using consistent mixed-radix scheme
    pub fn encode_coords(&self, coords: &[usize]) -> UACalcResult<usize> {
        mixed_radix_encode(coords, &self.factor_sizes).ok_or_else(|| {
            UACalcError::InvalidOperation {
                message: "Failed to encode coordinates".to_string(),
            }
        })
    }
}

impl Algebra for ProductAlgebra {
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
        // This is a limitation of the trait design - we can't return a reference
        // to a trait object inside an Arc<Mutex<>>. In practice, this method
        // is rarely used directly, and operation_arc() is preferred.
        Err(UACalcError::InvalidOperation {
            message: "Direct operation access not supported for ProductAlgebra".to_string(),
        })
    }

    fn operation_by_symbol(&self, _symbol: &str) -> UACalcResult<&dyn Operation> {
        // This is a limitation of the trait design - we can't return a reference
        // to a trait object inside an Arc<Mutex<>>. In practice, this method
        // is rarely used directly, and operation_arc_by_symbol() is preferred.
        Err(UACalcError::InvalidOperation {
            message: "Direct operation access not supported for ProductAlgebra".to_string(),
        })
    }

    fn operation_arc(&self, index: usize) -> UACalcResult<Arc<Mutex<dyn Operation>>> {
        let op = self
            .operations
            .get(index)
            .ok_or_else(|| UACalcError::IndexOutOfBounds {
                index,
                size: self.operations.len(),
            })?;
        Ok(op.clone())
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
        for operation in &mut self.operations {
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

impl SmallAlgebra for ProductAlgebra {
    fn max_arity(&self) -> usize {
        self.operations
            .iter()
            .map(|op| op.lock().map(|guard| guard.arity()).unwrap_or(0))
            .max()
            .unwrap_or(0)
    }

    /// Override operation_int_value to work with ProductAlgebra's Arc-based operations
    fn operation_int_value(&self, op_index: usize, args: &[usize]) -> UACalcResult<usize> {
        let operation_arc = self.operation_arc(op_index)?;
        let op_guard = operation_arc
            .lock()
            .map_err(|_| UACalcError::InvalidOperation {
                message: format!("Failed to lock operation {}", op_index),
            })?;
        op_guard.value(args)
    }

    fn subalgebra(&self, _generators: &[usize]) -> UACalcResult<BasicAlgebra> {
        // TODO: Implement proper subalgebra generation for ProductAlgebra
        // This should generate a subalgebra that respects the product structure,
        // potentially resulting in another ProductAlgebra when possible.
        Err(UACalcError::UnsupportedOperation {
            operation: "subalgebra for ProductAlgebra".into(),
        })
    }
}

impl std::fmt::Debug for ProductAlgebra {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("ProductAlgebra")
            .field("name", &self.name)
            .field("cardinality", &self.cardinality)
            .field("factor_sizes", &self.factor_sizes)
            .field(
                "operations",
                &format!("{} operations", self.operations.len()),
            )
            .field("factors", &format!("{} factors", self.factors.len()))
            .finish()
    }
}
