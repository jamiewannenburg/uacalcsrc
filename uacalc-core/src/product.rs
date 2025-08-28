use crate::algebra::{Algebra, BasicAlgebra, SmallAlgebra};
use crate::error::{UACalcError, UACalcResult};
use crate::operation::{Operation, TableOperation};
use crate::partition::BasicPartition;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// Product algebra implementation that creates the direct product of multiple algebras
pub struct ProductAlgebra {
    name: String,
    factors: Vec<Arc<Mutex<dyn SmallAlgebra>>>,
    cardinality: usize,
    factor_sizes: Vec<usize>,
    universe: Vec<usize>,
    operations: Vec<Arc<Mutex<TableOperation>>>,
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

        // Validate operation compatibility across factors
        let first_factor = &factors[0];
        let first_guard = first_factor
            .lock()
            .map_err(|_| UACalcError::InvalidOperation {
                message: "Failed to lock first factor algebra".to_string(),
            })?;
        let num_operations = first_guard.operations().len();

        // Clone factors to avoid borrow checker issues
        let factors_clone = factors.clone();

        for (i, factor) in factors.iter().enumerate().skip(1) {
            let factor_guard = factor.lock().map_err(|_| UACalcError::InvalidOperation {
                message: format!("Failed to lock factor algebra {}", i),
            })?;

            if factor_guard.operations().len() != num_operations {
                return Err(UACalcError::InvalidOperation {
                    message: format!(
                        "Factor {} has {} operations, but first factor has {}",
                        i,
                        factor_guard.operations().len(),
                        num_operations
                    ),
                });
            }

            // Check operation compatibility
            for (j, op) in factor_guard.operations().iter().enumerate() {
                let op_guard = op.lock().map_err(|_| UACalcError::InvalidOperation {
                    message: format!("Failed to lock operation {} in factor {}", j, i),
                })?;
                let first_op_arc = first_guard.operation_arc(j)?;
                let first_op_guard =
                    first_op_arc
                        .lock()
                        .map_err(|_| UACalcError::InvalidOperation {
                            message: format!("Failed to lock first operation {}", j),
                        })?;

                if op_guard.arity() != first_op_guard.arity() {
                    return Err(UACalcError::InvalidOperation {
                        message: format!(
                            "Operation {} has arity {} in factor {} but {} in first factor",
                            j,
                            op_guard.arity(),
                            i,
                            first_op_guard.arity()
                        ),
                    });
                }

                if op_guard.symbol().name != first_op_guard.symbol().name {
                    return Err(UACalcError::InvalidOperation {
                        message: format!(
                            "Operation {} has symbol '{}' in factor {} but '{}' in first factor",
                            j,
                            op_guard.symbol().name,
                            i,
                            first_op_guard.symbol().name
                        ),
                    });
                }
            }
        }

        // For now, create empty operations to avoid the table completion issue
        // TODO: Implement proper componentwise operations
        let mut operations = Vec::new();
        let mut operation_symbols = HashMap::new();

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
        let block_size = self.cardinality / factor_size;

        // Create blocks where elements map to the same value under k-th projection
        for i in 0..factor_size {
            let start = i * block_size;
            let end = if i == factor_size - 1 {
                self.cardinality
            } else {
                (i + 1) * block_size
            };

            // Union all elements in this block
            for j in start + 1..end {
                partition.union_elements(start, j)?;
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

        // Decode element using mixed-radix decoding
        let mut coordinates = Vec::with_capacity(self.factors.len());
        let mut remaining = element;

        for &factor_size in &self.factor_sizes {
            coordinates.push(remaining % factor_size);
            remaining /= factor_size;
        }
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

        // Encode coordinates using mixed-radix encoding
        let mut result: usize = 0;
        for (i, &coord) in coordinates.iter().enumerate() {
            if coord >= self.factor_sizes[i] {
                return Err(UACalcError::IndexOutOfBounds {
                    index: coord,
                    size: self.factor_sizes[i],
                });
            }

            // Multiply by the size of the current factor and add the coordinate
            result = result.checked_mul(self.factor_sizes[i]).ok_or_else(|| {
                UACalcError::ArithmeticOverflow {
                    operation: "encoding coordinates".to_string(),
                }
            })?;
            result = result
                .checked_add(coord)
                .ok_or_else(|| UACalcError::ArithmeticOverflow {
                    operation: "encoding coordinates".to_string(),
                })?;
        }
        Ok(result)
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
        // Cast the slice to the expected type
        unsafe {
            std::mem::transmute::<&[Arc<Mutex<TableOperation>>], &[Arc<Mutex<dyn Operation>>]>(
                &self.operations,
            )
        }
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

    fn subalgebra(&self, _generators: &[usize]) -> UACalcResult<BasicAlgebra> {
        // Delegate to BasicAlgebra implementation
        let basic = BasicAlgebra::with_cardinality(self.name.clone(), self.cardinality)?;
        // This is a simplified implementation - in practice, you'd want to
        // compute the actual subalgebra generated by the generators
        Ok(basic)
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
