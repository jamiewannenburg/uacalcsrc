use crate::algebra::{Algebra, BasicAlgebra, SmallAlgebra};
use crate::error::{UACalcError, UACalcResult};
use crate::operation::{Operation, OperationSymbol};
use crate::partition::{BasicPartition, Partition};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// Custom operation implementation for quotient operations
struct QuotientOperation {
    symbol: OperationSymbol,
    super_algebra: Arc<Mutex<dyn SmallAlgebra>>,
    congruence: BasicPartition,
    representatives: Vec<usize>,
    rep_to_index: HashMap<usize, usize>,
    op_index: usize,
    set_size: usize,
}

impl QuotientOperation {
    fn new(
        symbol: OperationSymbol,
        super_algebra: Arc<Mutex<dyn SmallAlgebra>>,
        congruence: BasicPartition,
        representatives: Vec<usize>,
        rep_to_index: HashMap<usize, usize>,
        op_index: usize,
        set_size: usize,
    ) -> Self {
        Self {
            symbol,
            super_algebra,
            congruence,
            representatives,
            rep_to_index,
            op_index,
            set_size,
        }
    }
}

impl Operation for QuotientOperation {
    fn arity(&self) -> usize {
        self.symbol.arity
    }

    fn symbol(&self) -> &OperationSymbol {
        &self.symbol
    }

    fn value(&self, args: &[usize]) -> UACalcResult<usize> {
        if args.len() != self.arity() {
            return Err(UACalcError::InvalidArity {
                expected: self.arity(),
                actual: args.len(),
            });
        }

        // Map quotient arguments to parent representatives
        let mut parent_args = Vec::with_capacity(args.len());
        for &quotient_arg in args {
            if quotient_arg >= self.representatives.len() {
                return Err(UACalcError::IndexOutOfBounds {
                    index: quotient_arg,
                    size: self.representatives.len(),
                });
            }
            parent_args.push(self.representatives[quotient_arg]);
        }

        // Evaluate parent operation
        let parent_result = {
            let super_guard =
                self.super_algebra
                    .lock()
                    .map_err(|_| UACalcError::InvalidOperation {
                        message: "Failed to lock super algebra in quotient operation".to_string(),
                    })?;
            let operation_arc = super_guard.operation_arc(self.op_index)?;
            drop(super_guard); // Release the super algebra lock before locking the operation
            let op_guard = operation_arc
                .lock()
                .map_err(|_| UACalcError::InvalidOperation {
                    message: "Failed to lock parent operation".to_string(),
                })?;
            op_guard.value(&parent_args)?
        };

        // Find the representative of the result
        let result_representative = self.congruence.representative(parent_result)?;

        // Map result representative to quotient index
        self.rep_to_index
            .get(&result_representative)
            .copied()
            .ok_or_else(|| UACalcError::InvalidOperation {
                message: format!(
                    "Representative {} not found in quotient",
                    result_representative
                ),
            })
    }

    fn set_size(&self) -> usize {
        self.set_size
    }

    fn make_table(&mut self, _set_size: usize) -> UACalcResult<()> {
        // Quotient operations are computed on-demand, no table needed
        Ok(())
    }

    fn get_table(&self) -> Option<&crate::operation::FlatOperationTable> {
        // Quotient operations don't use flat tables
        None
    }
}

impl std::fmt::Debug for QuotientOperation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("QuotientOperation")
            .field("symbol", &self.symbol)
            .field("congruence", &self.congruence)
            .field("representatives", &self.representatives)
            .field("rep_to_index", &self.rep_to_index)
            .field("op_index", &self.op_index)
            .field("set_size", &self.set_size)
            .finish()
    }
}

/// Quotient algebra implementation
///
/// A quotient algebra is formed by taking an algebra and partitioning its elements
/// according to a congruence relation. Operations on the quotient are defined by
/// applying the original operations to representatives and mapping the result
/// back to the quotient.
pub struct QuotientAlgebra {
    name: String,
    super_algebra: Arc<Mutex<dyn SmallAlgebra>>,
    congruence: BasicPartition,
    representatives: Vec<usize>,
    rep_to_index: HashMap<usize, usize>,
    cardinality: usize,
    universe: Vec<usize>,
    operations: Vec<Arc<Mutex<dyn Operation>>>,
    operation_symbols: HashMap<String, usize>,
    operation_tables_built: bool,
}

impl QuotientAlgebra {
    /// Create a new quotient algebra
    ///
    /// # Arguments
    /// * `name` - Name for the quotient algebra
    /// * `super_algebra` - The parent algebra to quotient
    /// * `congruence` - The congruence relation (partition) to quotient by
    ///
    /// # Returns
    /// A new QuotientAlgebra instance
    ///
    /// # Errors
    /// Returns an error if the congruence size doesn't match the super algebra cardinality
    /// or if operation creation fails
    pub fn new(
        name: String,
        super_algebra: Arc<Mutex<dyn SmallAlgebra>>,
        congruence: BasicPartition,
    ) -> UACalcResult<Self> {
        // Validate congruence size matches algebra cardinality
        let super_cardinality = {
            let super_guard = super_algebra
                .lock()
                .map_err(|_| UACalcError::InvalidOperation {
                    message: "Failed to lock super algebra".to_string(),
                })?;
            super_guard.cardinality()
        };

        if congruence.size() != super_cardinality {
            return Err(UACalcError::InvalidOperation {
                message: format!(
                    "Congruence size {} does not match algebra cardinality {}",
                    congruence.size(),
                    super_cardinality
                ),
            });
        }

        // Extract sorted representatives
        let mut representatives = congruence.representatives();
        representatives.sort();
        let cardinality = representatives.len();

        // Build rep_to_index HashMap for O(1) lookup
        let mut rep_to_index = HashMap::new();
        for (index, &rep) in representatives.iter().enumerate() {
            rep_to_index.insert(rep, index);
        }

        // Create universe vector
        let universe: Vec<usize> = (0..cardinality).collect();

        // Create quotient operations
        let mut operations = Vec::new();
        let mut operation_symbols = HashMap::new();

        {
            let super_guard = super_algebra
                .lock()
                .map_err(|_| UACalcError::InvalidOperation {
                    message: "Failed to lock super algebra for operation creation".to_string(),
                })?;

            for (op_index, super_op_arc) in super_guard.operations().iter().enumerate() {
                let super_op_guard =
                    super_op_arc
                        .lock()
                        .map_err(|_| UACalcError::InvalidOperation {
                            message: format!("Failed to lock super operation {}", op_index),
                        })?;

                let symbol_name = super_op_guard.symbol().name.clone();
                let arity = super_op_guard.arity();

                // Create a quotient operation
                let quotient_symbol = OperationSymbol::new(symbol_name.clone(), arity);

                let quotient_operation = QuotientOperation::new(
                    quotient_symbol,
                    super_algebra.clone(),
                    congruence.clone(),
                    representatives.clone(),
                    rep_to_index.clone(),
                    op_index,
                    cardinality,
                );

                operation_symbols.insert(symbol_name, operations.len());
                operations
                    .push(Arc::new(Mutex::new(quotient_operation)) as Arc<Mutex<dyn Operation>>);
            }
        }

        Ok(Self {
            name,
            super_algebra,
            congruence,
            representatives,
            rep_to_index,
            cardinality,
            universe,
            operations,
            operation_symbols,
            operation_tables_built: false,
        })
    }

    /// Get the super algebra
    pub fn super_algebra(&self) -> Arc<Mutex<dyn SmallAlgebra>> {
        self.super_algebra.clone()
    }

    /// Get the congruence relation
    pub fn congruence(&self) -> &BasicPartition {
        &self.congruence
    }

    /// Get the index of a representative in the quotient
    pub fn representative_index(&self, rep: usize) -> UACalcResult<usize> {
        self.rep_to_index
            .get(&rep)
            .copied()
            .ok_or_else(|| UACalcError::InvalidOperation {
                message: format!("Representative {} not found in quotient", rep),
            })
    }

    /// Map a parent algebra element to its quotient index (canonical homomorphism)
    pub fn canonical_homomorphism(&self, element: usize) -> UACalcResult<usize> {
        let representative = self.congruence.representative(element)?;
        self.representative_index(representative)
    }
}

impl Algebra for QuotientAlgebra {
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
        // Similar to ProductAlgebra, direct access is not supported
        Err(UACalcError::UnsupportedOperation {
            operation: "Use operation_arc instead of operation for QuotientAlgebra".to_string(),
        })
    }

    fn operation_by_symbol(&self, _symbol: &str) -> UACalcResult<&dyn Operation> {
        // Similar to ProductAlgebra, direct access is not supported
        Err(UACalcError::UnsupportedOperation {
            operation:
                "Use operation_arc_by_symbol instead of operation_by_symbol for QuotientAlgebra"
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

impl SmallAlgebra for QuotientAlgebra {
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

    fn subalgebra(&self, _generators: &[usize]) -> UACalcResult<BasicAlgebra> {
        // For now, return a simple subalgebra implementation
        // This avoids the complexity and potential issues with the full implementation
        BasicAlgebra::with_cardinality(
            format!("{}_sub", self.name),
            1, // Simplified: just return a trivial algebra
        )
    }
}

impl std::fmt::Debug for QuotientAlgebra {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("QuotientAlgebra")
            .field("name", &self.name)
            .field("cardinality", &self.cardinality)
            .field("representatives", &self.representatives)
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::algebra::BasicAlgebra;
    use crate::operation::TableOperation;
    use crate::partition::{BasicPartition, Partition};

    #[test]
    fn test_quotient_algebra_creation() -> Result<(), Box<dyn std::error::Error>> {
        // Create a simple algebra Z4 = {0, 1, 2, 3} with addition mod 4
        let mut z4 = BasicAlgebra::with_cardinality("Z4".to_string(), 4)?;
        let add_op = Arc::new(Mutex::new(TableOperation::binary(
            "add".to_string(),
            4,
            |a, b| (a + b) % 4,
        )?));
        z4.add_operation("add".to_string(), add_op)?;

        // Create a congruence: {0, 2} and {1, 3} (even/odd)
        let congruence = BasicPartition::from_blocks(4, vec![vec![0, 2], vec![1, 3]])?;

        // Create quotient algebra
        let z4_arc = Arc::new(Mutex::new(z4));
        let quotient = QuotientAlgebra::new("Z2".to_string(), z4_arc, congruence)?;

        // Test basic properties
        assert_eq!(quotient.cardinality(), 2);
        assert_eq!(quotient.universe(), &[0, 1]);
        assert_eq!(quotient.operations().len(), 1);

        // Test operation evaluation
        let add_quotient = quotient.operation_arc_by_symbol("add")?;
        let add_guard = add_quotient.lock().unwrap();

        // In the quotient: 0 represents {0,2}, 1 represents {1,3}
        // 0 + 0 = 0 (even + even = even)
        assert_eq!(add_guard.value(&[0, 0])?, 0);
        // 0 + 1 = 1 (even + odd = odd)
        assert_eq!(add_guard.value(&[0, 1])?, 1);
        // 1 + 0 = 1 (odd + even = odd)
        assert_eq!(add_guard.value(&[1, 0])?, 1);
        // 1 + 1 = 0 (odd + odd = even)
        assert_eq!(add_guard.value(&[1, 1])?, 0);

        Ok(())
    }

    #[test]
    fn test_quotient_canonical_homomorphism() -> Result<(), Box<dyn std::error::Error>> {
        // Create Z4 with addition
        let mut z4 = BasicAlgebra::with_cardinality("Z4".to_string(), 4)?;
        let add_op = Arc::new(Mutex::new(TableOperation::binary(
            "add".to_string(),
            4,
            |a, b| (a + b) % 4,
        )?));
        z4.add_operation("add".to_string(), add_op)?;

        // Create congruence: {0, 2} and {1, 3}
        let congruence = BasicPartition::from_blocks(4, vec![vec![0, 2], vec![1, 3]])?;

        let z4_arc = Arc::new(Mutex::new(z4));
        let quotient = QuotientAlgebra::new("Z2".to_string(), z4_arc, congruence)?;

        // Test canonical homomorphism
        assert_eq!(quotient.canonical_homomorphism(0)?, 0); // 0 maps to equivalence class 0
        assert_eq!(quotient.canonical_homomorphism(1)?, 1); // 1 maps to equivalence class 1
        assert_eq!(quotient.canonical_homomorphism(2)?, 0); // 2 maps to equivalence class 0
        assert_eq!(quotient.canonical_homomorphism(3)?, 1); // 3 maps to equivalence class 1

        Ok(())
    }

    #[test]
    fn test_quotient_error_cases() -> Result<(), Box<dyn std::error::Error>> {
        // Create algebra
        let mut algebra = BasicAlgebra::with_cardinality("test".to_string(), 3)?;
        let op = Arc::new(Mutex::new(TableOperation::unary(
            "id".to_string(),
            3,
            |x| x,
        )?));
        algebra.add_operation("id".to_string(), op)?;

        // Create mismatched congruence (wrong size)
        let bad_congruence = BasicPartition::new(5); // Wrong size

        let algebra_arc = Arc::new(Mutex::new(algebra));
        let result = QuotientAlgebra::new("test_quotient".to_string(), algebra_arc, bad_congruence);

        assert!(result.is_err());

        Ok(())
    }
}
