use crate::alg::op::Operation;
use crate::terms::Term;

/// This trait specifies a term operation, that is, the interpretation
/// of a term in an algebra.
/// 
/// A term operation is a special kind of operation that is derived from
/// evaluating a term in an algebra. It provides access to both the 
/// underlying term and the ordered list of variables used in the term.
/// 
/// This trait is the Rust equivalent of the Java `TermOperation` interface
/// in `org.uacalc.alg.op.TermOperation`. It extends the `Operation` trait
/// and adds methods to access the term and its variables.
/// 
/// # Examples
/// 
/// Concrete implementations like `TermOperationImp` will implement this trait:
/// 
/// ```ignore
/// use uacalc::alg::op::TermOperation;
/// use uacalc::terms::Term;
/// 
/// // This will be implemented by TermOperationImp (Task 33)
/// struct MyTermOperation {
///     // ... fields
/// }
/// 
/// impl TermOperation for MyTermOperation {
///     fn get_term(&self) -> &dyn Term {
///         // Return the underlying term
///         &self.term
///     }
///     
///     fn get_ordered_variables(&self) -> Vec<String> {
///         // Return ordered list of variables
///         self.variables.clone()
///     }
/// }
/// ```
pub trait TermOperation: Operation {
    
    /// Returns the underlying term.
    /// 
    /// This gives access to the term that defines this operation.
    /// 
    /// # Returns
    /// A reference to the term that defines this operation
    fn get_term(&self) -> &dyn Term;
    
    /// Returns a list of the variables in order without repeats.
    /// 
    /// This provides the ordered list of variable names used in the term,
    /// with each variable appearing only once (at its first occurrence).
    /// The order matches the order in which variables appear in the term.
    /// 
    /// # Returns
    /// A vector of variable names in the order they appear in the term
    fn get_ordered_variables(&self) -> Vec<String>;
}
