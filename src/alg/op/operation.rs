use std::fmt::{Debug, Display};
use crate::alg::op::OperationSymbol;

/// This trait specifies an operation, that is, a map from 
/// the direct product of some number (called the arity) of a set
/// to the set. Since the set will often be just 
/// `{0, 1, ..., n-1}` we have `int_value_at(args: &[i32])` 
/// form of the operation. We also have an `Object` form for
/// general sets. Since only one or the other may be required, both are
/// optional.
/// 
/// This trait is the Rust equivalent of the Java `Operation` interface
/// in `org.uacalc.alg.op.Operation`. It extends `Comparable<Operation>` in Java.
/// 
/// Note: We don't include `Ord`, `PartialOrd`, `Eq`, `PartialEq`, `Hash` in the trait
/// bounds to maintain object safety, but concrete implementations should implement these.
pub trait Operation: Display + Debug + Send + Sync {
    
    /// This gives the arity of this operation.
    /// 
    /// # Returns
    /// The number of arguments this operation takes
    fn arity(&self) -> i32;

    /// This gives the size of the set upon which the operation is defined.
    /// 
    /// # Returns  
    /// The size of the underlying set
    fn get_set_size(&self) -> i32;

    /// The operation symbol for this operation.
    /// 
    /// # Returns
    /// A reference to the operation symbol
    fn symbol(&self) -> &OperationSymbol;

    /// This operation is the element version that can work with any type.
    /// 
    /// # Arguments
    /// * `args` - A slice of arguments for the operation
    /// 
    /// # Returns
    /// * `Ok(i32)` - The result of the operation
    /// * `Err(String)` - Error message if the operation fails
    /// 
    /// # Note
    /// In Java this takes `List args` and returns `Object`. We use `&[i32]`
    /// for simplicity and return `i32` since most operations work on integers.
    fn value_at(&self, args: &[i32]) -> Result<i32, String>;

    /// This operation is for fast product operation.
    /// 
    /// # Arguments  
    /// * `args` - An array of arity int arrays from the product algebra
    /// 
    /// # Returns
    /// * `Ok(Vec<i32>)` - The result array of the operation
    /// * `Err(String)` - Error message if the operation fails
    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String>;

    /// This (optional) operation is the int version.
    /// 
    /// # Arguments
    /// * `args` - Array of integer arguments
    /// 
    /// # Returns
    /// * `Ok(i32)` - The result of the operation
    /// * `Err(String)` - Error message if the operation fails
    fn int_value_at(&self, args: &[i32]) -> Result<i32, String>;
    
    /// This (optional) operation is for fast access to the table, if it exists.
    /// 
    /// # Arguments
    /// * `arg` - The Horner encoding of the actual args
    /// 
    /// # Returns
    /// * `Ok(i32)` - The result of the operation
    /// * `Err(String)` - Error message if the operation fails or table doesn't exist
    fn int_value_at_horner(&self, arg: i32) -> Result<i32, String>;

    /// This will make a table and so make the operation faster but
    /// requires more space. So if A is in HSP(B) then for ints x and y,
    /// x * y would be evaluated by finding the representative
    /// of x and y of the congruence; then these representatives would be
    /// expanded into array representing the corresponding elements in the 
    /// direct product. These would be multiplied and then the whole process
    /// would be reversed. If A is reasonable small it may make sense to
    /// make a table for the multiplication.
    /// 
    /// # Returns
    /// * `Ok(())` - If table creation succeeds
    /// * `Err(String)` - Error message if table creation fails
    fn make_table(&mut self) -> Result<(), String>;

    /// Get the table for this operation or None if it does not exist.
    /// 
    /// # Returns
    /// * `Some(&[i32])` - Reference to the operation table
    /// * `None` - If no table exists
    fn get_table(&self) -> Option<&[i32]>;
    
    /// Get the table for this operation. If it does not exist
    /// make it if make_table is true.
    /// 
    /// # Arguments
    /// * `make_table` - Forces the table to be made if necessary
    /// 
    /// # Returns
    /// * `Ok(&[i32])` - Reference to the operation table
    /// * `Err(String)` - Error message if table creation fails
    fn get_table_force(&mut self, make_table: bool) -> Result<&[i32], String>;
    
    /// Check if this operation is table-based.
    /// 
    /// # Returns
    /// `true` if the operation uses a precomputed table, `false` otherwise
    fn is_table_based(&self) -> bool;

    /// Is this operation idempotent in the sense f(x,x,..,x) = x.
    /// 
    /// # Returns
    /// * `Ok(bool)` - `true` if the operation is idempotent
    /// * `Err(String)` - Error message if the check fails
    fn is_idempotent(&self) -> Result<bool, String>;

    /// Is this operation binary and associative.
    /// 
    /// # Returns
    /// * `Ok(bool)` - `true` if the operation is binary and associative
    /// * `Err(String)` - Error message if the check fails
    fn is_associative(&self) -> Result<bool, String>;

    /// Is this operation binary and commutative.
    /// 
    /// # Returns
    /// * `Ok(bool)` - `true` if the operation is binary and commutative
    /// * `Err(String)` - Error message if the check fails
    fn is_commutative(&self) -> Result<bool, String>;

    /// Is this operation totally symmetric; that is, invariant
    /// under all permutation of the variables.
    /// 
    /// # Returns
    /// * `Ok(bool)` - `true` if the operation is totally symmetric
    /// * `Err(String)` - Error message if the check fails
    fn is_totally_symmetric(&self) -> Result<bool, String>;
    
    /// Check if a ternary operation is a Maltsev operation.
    /// 
    /// # Returns
    /// * `Ok(bool)` - `true` if the operation is a Maltsev operation
    /// * `Err(String)` - Error message if the check fails
    fn is_maltsev(&self) -> Result<bool, String>;
    
    /// Only OperationWithDefaultValue's can fail this.
    /// 
    /// # Returns
    /// * `Ok(bool)` - `true` if the operation is total
    /// * `Err(String)` - Error message if the check fails
    fn is_total(&self) -> Result<bool, String>;
}

/// Helper trait for operations that need cloning.
/// 
/// Since we can't have `Clone` in the main trait due to object safety,
/// we provide this separate trait for cloning operations.
pub trait CloneableOperation: Operation {
    fn clone_box(&self) -> Box<dyn CloneableOperation>;
}

impl<T> CloneableOperation for T
where
    T: 'static + Operation + Clone,
{
    fn clone_box(&self) -> Box<dyn CloneableOperation> {
        Box::new(self.clone())
    }
}

/// Type alias for boxed operations for convenience.
pub type BoxedOperation = Box<dyn Operation>;

/// Create a boxed operation from any type implementing Operation.
pub fn boxed_operation<T: 'static + Operation>(op: T) -> BoxedOperation {
    Box::new(op)
}