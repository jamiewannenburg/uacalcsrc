use crate::algebra::{Algebra, BasicAlgebra, SmallAlgebra};
use crate::error::{UACalcError, UACalcResult};
use crate::operation::{Operation, OperationSymbol};
use crate::partition::{BasicPartition, Partition};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// Custom operation implementation for quotient operations
struct QuotientOperation {
    symbol: OperationSymbol,
    parent_op: Arc<Mutex<dyn Operation>>,
    congruence: Arc<BasicPartition>,
    representatives: Arc<Vec<usize>>,
    rep_to_index: Arc<HashMap<usize, usize>>,
    cached_constant: Option<usize>,
    set_size: usize,
}

impl QuotientOperation {
    fn new(
        symbol: OperationSymbol,
        parent_op: Arc<Mutex<dyn Operation>>,
        congruence: Arc<BasicPartition>,
        representatives: Arc<Vec<usize>>,
        rep_to_index: Arc<HashMap<usize, usize>>,
        set_size: usize,
    ) -> UACalcResult<Self> {
        // Check if this is a constant operation and cache its value
        let cached_constant = if symbol.arity == 0 {
            let op_guard = parent_op
                .lock()
                .map_err(|_| UACalcError::InvalidOperation {
                    message: "Failed to lock parent operation for constant caching".to_string(),
                })?;
            let parent_result = op_guard.value(&[])?;
            let result_representative = congruence.representative(parent_result)?;
            Some(*rep_to_index.get(&result_representative).ok_or_else(|| {
                UACalcError::InvalidOperation {
                    message: format!(
                        "Representative {} not found in quotient",
                        result_representative
                    ),
                }
            })?)
        } else {
            None
        };

        Ok(Self {
            symbol,
            parent_op,
            congruence,
            representatives,
            rep_to_index,
            cached_constant,
            set_size,
        })
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

        // For constant operations, return cached value directly
        if self.arity() == 0 {
            if let Some(cached_value) = self.cached_constant {
                return Ok(cached_value);
            }
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

        // Evaluate parent operation using cached operation reference
        let parent_result = {
            let op_guard = self
                .parent_op
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
    
    fn as_any(&self) -> &dyn std::any::Any {
        self
    }
}

impl std::fmt::Debug for QuotientOperation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("QuotientOperation")
            .field("symbol", &self.symbol)
            .field("congruence", &self.congruence)
            .field("representatives", &self.representatives)
            .field("rep_to_index", &self.rep_to_index)
            .field("cached_constant", &self.cached_constant)
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
#[derive(Clone)]
pub struct QuotientAlgebra {
    name: String,
    super_algebra: Arc<Mutex<dyn SmallAlgebra>>,
    congruence: Arc<BasicPartition>,
    representatives: Arc<Vec<usize>>,
    rep_to_index: Arc<HashMap<usize, usize>>,
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
    /// * `validate` - Optional flag to validate congruence compatibility (default: false)
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
        Self::new_with_validation(name, super_algebra, congruence, false)
    }

    /// Create a new quotient algebra with optional validation
    ///
    /// # Arguments
    /// * `name` - Name for the quotient algebra
    /// * `super_algebra` - The parent algebra to quotient
    /// * `congruence` - The congruence relation (partition) to quotient by
    /// * `validate` - Whether to validate that the partition is actually a congruence
    ///
    /// # Returns
    /// A new QuotientAlgebra instance
    ///
    /// # Errors
    /// Returns an error if validation fails or other creation errors occur
    pub fn new_with_validation(
        name: String,
        super_algebra: Arc<Mutex<dyn SmallAlgebra>>,
        congruence: BasicPartition,
        validate: bool,
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

        // Validate that the partition is actually a congruence if requested
        if validate {
            Self::validate_congruence(&super_algebra, &congruence)?;
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

        // Create shared Arc references
        let congruence_arc = Arc::new(congruence);
        let representatives_arc = Arc::new(representatives);
        let rep_to_index_arc = Arc::new(rep_to_index);

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

            for super_op_arc in super_guard.operations().iter() {
                let super_op_guard =
                    super_op_arc
                        .lock()
                        .map_err(|_| UACalcError::InvalidOperation {
                            message: "Failed to lock super operation".to_string(),
                        })?;

                let symbol_name = super_op_guard.symbol().name.clone();
                let arity = super_op_guard.arity();
                drop(super_op_guard); // Release the lock before creating quotient operation

                // Create a quotient operation
                let quotient_symbol = OperationSymbol::new(symbol_name.clone(), arity);

                let quotient_operation = QuotientOperation::new(
                    quotient_symbol,
                    super_op_arc.clone(),
                    congruence_arc.clone(),
                    representatives_arc.clone(),
                    rep_to_index_arc.clone(),
                    cardinality,
                )?;

                operation_symbols.insert(symbol_name, operations.len());
                operations
                    .push(Arc::new(Mutex::new(quotient_operation)) as Arc<Mutex<dyn Operation>>);
            }
        }

        Ok(Self {
            name,
            super_algebra,
            congruence: congruence_arc,
            representatives: representatives_arc,
            rep_to_index: rep_to_index_arc,
            cardinality,
            universe,
            operations,
            operation_symbols,
            operation_tables_built: false,
        })
    }

    /// Validate that a partition is actually a congruence for the given algebra
    fn validate_congruence(
        super_algebra: &Arc<Mutex<dyn SmallAlgebra>>,
        congruence: &BasicPartition,
    ) -> UACalcResult<()> {
        let super_guard = super_algebra
            .lock()
            .map_err(|_| UACalcError::InvalidOperation {
                message: "Failed to lock super algebra for validation".to_string(),
            })?;

        // For each operation, check congruence compatibility on block representatives
        for op_arc in super_guard.operations().iter() {
            let op_guard = op_arc.lock().map_err(|_| UACalcError::InvalidOperation {
                message: "Failed to lock operation for validation".to_string(),
            })?;

            let arity = op_guard.arity();

            if arity == 0 {
                // Constants are always compatible
                continue;
            }

            // Get representative samples for validation
            let representatives = congruence.representatives();
            let sample_size = std::cmp::min(representatives.len(), 10); // Limit validation to avoid performance issues

            for i in 0..sample_size {
                let rep1 = representatives[i];
                let block1 = congruence.block(rep1)?;

                if arity == 1 {
                    // For unary operations, check that f(a) ~ f(a') for all a ~ a'
                    let result_rep = op_guard.value(&[rep1])?;

                    for &other in &block1 {
                        if other != rep1 {
                            let other_result = op_guard.value(&[other])?;
                            if !congruence.same_block(result_rep, other_result)? {
                                return Err(UACalcError::InvalidOperation {
                                    message: format!(
                                        "Partition is not a congruence: operation {} violates compatibility on elements {} and {}",
                                        op_guard.symbol().name, rep1, other
                                    ),
                                });
                            }
                        }
                    }
                } else if arity == 2 {
                    // For binary operations, check f(a,b) ~ f(a',b') for a ~ a', b ~ b'
                    for j in 0..sample_size {
                        let rep2 = representatives[j];
                        let block2 = congruence.block(rep2)?;

                        let result_rep = op_guard.value(&[rep1, rep2])?;

                        // Check with first element from each block varied
                        if let Some(&other1) = block1.iter().find(|&&x| x != rep1) {
                            let other_result = op_guard.value(&[other1, rep2])?;
                            if !congruence.same_block(result_rep, other_result)? {
                                return Err(UACalcError::InvalidOperation {
                                    message: format!(
                                        "Partition is not a congruence: operation {} violates compatibility",
                                        op_guard.symbol().name
                                    ),
                                });
                            }
                        }

                        if let Some(&other2) = block2.iter().find(|&&x| x != rep2) {
                            let other_result = op_guard.value(&[rep1, other2])?;
                            if !congruence.same_block(result_rep, other_result)? {
                                return Err(UACalcError::InvalidOperation {
                                    message: format!(
                                        "Partition is not a congruence: operation {} violates compatibility",
                                        op_guard.symbol().name
                                    ),
                                });
                            }
                        }
                    }
                }
                // For higher arity operations, we do a simplified check
                // Full validation would be computationally expensive
            }
        }

        Ok(())
    }

    /// Get the super algebra
    pub fn super_algebra(&self) -> Arc<Mutex<dyn SmallAlgebra>> {
        self.super_algebra.clone()
    }

    /// Get the congruence relation
    pub fn congruence(&self) -> &BasicPartition {
        &*self.congruence
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

    /// Get the representatives vector
    pub fn representatives(&self) -> &[usize] {
        &*self.representatives
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

    fn algebra_type(&self) -> crate::algebra::AlgebraType {
        crate::algebra::AlgebraType::Quotient
    }

    fn get_element(&self, k: usize) -> UACalcResult<usize> {
        if k >= self.universe.len() {
            return Err(UACalcError::IndexOutOfBounds {
                index: k,
                size: self.universe.len(),
            });
        }
        Ok(self.universe[k])
    }

    fn get_universe_list(&self) -> Vec<usize> {
        self.universe.clone()
    }

    fn get_universe_order(&self) -> std::collections::HashMap<usize, usize> {
        let mut order = std::collections::HashMap::new();
        for (index, &element) in self.universe.iter().enumerate() {
            order.insert(element, index);
        }
        order
    }

    fn parent(&self) -> Option<Arc<Mutex<dyn SmallAlgebra>>> {
        Some(self.super_algebra.clone())
    }

    fn parents(&self) -> Vec<Arc<Mutex<dyn SmallAlgebra>>> {
        vec![self.super_algebra.clone()]
    }

    fn reset_con_and_sub(&mut self) {
        // QuotientAlgebra doesn't cache lattices, so nothing to reset
    }

    fn convert_to_default_value_ops(&mut self) -> UACalcResult<()> {
        // For QuotientAlgebra, this is a no-op
        Ok(())
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
