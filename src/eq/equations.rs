//! Equations module for generating common algebraic equations.
//!
//! This module provides static functions for creating standard algebraic equations
//! like associative law, cyclic law, and symmetric law equations.
//!
//! In Java: `org.uacalc.eq.Equations` class

use crate::alg::op::OperationSymbol;
use crate::terms::{VariableImp, NonVariableTerm, Term};
use crate::eq::Equation;

/// Create associative law equation: f(x,f(y,z)) = f(f(x,y),z)
/// 
/// The operation symbol must have arity 2.
/// 
/// # Arguments
/// * `f` - The operation symbol (must have arity 2)
/// 
/// # Returns
/// * `Ok(Equation)` - The associative law equation
/// * `Err(String)` - If the arity is not 2
/// 
/// # Examples
/// ```
/// use uacalc::alg::op::OperationSymbol;
/// use uacalc::eq::equations::associative_law;
/// 
/// let f = OperationSymbol::new("multiply", 2);
/// let equation = associative_law(&f).unwrap();
/// ```
pub fn associative_law(f: &OperationSymbol) -> Result<Equation, String> {
    if f.arity() != 2 {
        return Err(format!("The arity must be 2, got {}", f.arity()));
    }
    
    // Create variables x, y, z
    let x = VariableImp::x();
    let y = VariableImp::y();
    let z = VariableImp::z();
    
    // Create f(x,y) and f(y,z)
    let xy_children = vec![Box::new(x.clone()) as Box<dyn Term>, Box::new(y.clone()) as Box<dyn Term>];
    let yz_children = vec![Box::new(y.clone()) as Box<dyn Term>, Box::new(z.clone()) as Box<dyn Term>];
    
    let fxy = NonVariableTerm::new(f.clone(), xy_children);
    let fyz = NonVariableTerm::new(f.clone(), yz_children);
    
    // Create f(x,f(y,z)) and f(f(x,y),z)
    let left_children = vec![Box::new(x) as Box<dyn Term>, Box::new(fyz) as Box<dyn Term>];
    let right_children = vec![Box::new(fxy) as Box<dyn Term>, Box::new(z) as Box<dyn Term>];
    
    let left = NonVariableTerm::new(f.clone(), left_children);
    let right = NonVariableTerm::new(f.clone(), right_children);
    
    Ok(Equation::new(Box::new(left), Box::new(right)))
}

/// Create cyclic law equation: f(x0,x1,...,x{k-1}) = f(x{k-1},x0,...,x{k-2})
/// 
/// The operation symbol must have arity at least 1.
/// 
/// # Arguments
/// * `f` - The operation symbol (must have arity >= 1)
/// 
/// # Returns
/// * `Ok(Equation)` - The cyclic law equation
/// * `Err(String)` - If the arity is less than 1
/// 
/// # Examples
/// ```
/// use uacalc::alg::op::OperationSymbol;
/// use uacalc::eq::equations::cyclic_law;
/// 
/// let f = OperationSymbol::new("ternary_op", 3);
/// let equation = cyclic_law(&f).unwrap();
/// ```
pub fn cyclic_law(f: &OperationSymbol) -> Result<Equation, String> {
    let k = f.arity();
    if k < 1 {
        return Err(format!("The arity must be at least 1, got {}", k));
    }
    
    // Create variable lists for both sides
    let mut args = Vec::new();
    let mut args2 = Vec::new();
    
    // First variable: x0 for left side, x{k-1} for right side
    args.push(Box::new(VariableImp::new("x0")) as Box<dyn Term>);
    args2.push(Box::new(VariableImp::new(&format!("x{}", k-1))) as Box<dyn Term>);
    
    // Remaining variables: x1,x2,...,x{k-1} for left side, x0,x1,...,x{k-2} for right side
    for i in 1..k {
        args.push(Box::new(VariableImp::new(&format!("x{}", i))) as Box<dyn Term>);
        args2.push(Box::new(VariableImp::new(&format!("x{}", i-1))) as Box<dyn Term>);
    }
    
    let left = NonVariableTerm::new(f.clone(), args);
    let right = NonVariableTerm::new(f.clone(), args2);
    
    Ok(Equation::new(Box::new(left), Box::new(right)))
}

/// Create first-second symmetric law equation: f(x0,x1,x2,...,xk) = f(x1,x0,x2,...,xk)
/// 
/// The operation symbol must have arity at least 2.
/// 
/// # Arguments
/// * `f` - The operation symbol (must have arity >= 2)
/// 
/// # Returns
/// * `Ok(Equation)` - The first-second symmetric law equation
/// * `Err(String)` - If the arity is less than 2
/// 
/// # Examples
/// ```
/// use uacalc::alg::op::OperationSymbol;
/// use uacalc::eq::equations::first_second_symmetric_law;
/// 
/// let f = OperationSymbol::new("binary_op", 2);
/// let equation = first_second_symmetric_law(&f).unwrap();
/// ```
pub fn first_second_symmetric_law(f: &OperationSymbol) -> Result<Equation, String> {
    let k = f.arity();
    if k < 2 {
        return Err(format!("The arity must be at least 2, got {}", k));
    }
    
    // Create variable lists for both sides
    let mut args = Vec::new();
    let mut args2 = Vec::new();
    
    // First two variables: x0,x1 for left side, x1,x0 for right side
    let x0 = VariableImp::new("x0");
    let x1 = VariableImp::new("x1");
    
    args.push(Box::new(x0.clone()) as Box<dyn Term>);
    args.push(Box::new(x1.clone()) as Box<dyn Term>);
    
    args2.push(Box::new(x1) as Box<dyn Term>);
    args2.push(Box::new(x0) as Box<dyn Term>);
    
    // Remaining variables: x2,x3,...,x{k-1} (same for both sides)
    for i in 2..k {
        let xi = VariableImp::new(&format!("x{}", i));
        args.push(Box::new(xi.clone()) as Box<dyn Term>);
        args2.push(Box::new(xi) as Box<dyn Term>);
    }
    
    let left = NonVariableTerm::new(f.clone(), args);
    let right = NonVariableTerm::new(f.clone(), args2);
    
    Ok(Equation::new(Box::new(left), Box::new(right)))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alg::op::OperationSymbol;
    
    #[test]
    fn test_associative_law_binary() {
        let f = OperationSymbol::new("multiply", 2, false);
        let equation = associative_law(&f).unwrap();
        
        // Check that we got an equation
        assert!(equation.left_side().isa_variable() == false);
        assert!(equation.right_side().isa_variable() == false);
        
        // The equation should be f(x,f(y,z)) = f(f(x,y),z)
        // We can verify by checking the string representation
        let left_str = format!("{}", equation.left_side());
        let right_str = format!("{}", equation.right_side());
        
        // Both sides should contain the operation symbol name
        assert!(left_str.contains("multiply"));
        assert!(right_str.contains("multiply"));
    }
    
    #[test]
    fn test_associative_law_wrong_arity() {
        let f = OperationSymbol::new("unary_op", 1, false);
        let result = associative_law(&f);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("arity must be 2"));
    }
    
    #[test]
    fn test_cyclic_law_ternary() {
        let f = OperationSymbol::new("ternary_op", 3, false);
        let equation = cyclic_law(&f).unwrap();
        
        // Check that we got an equation
        assert!(equation.left_side().isa_variable() == false);
        assert!(equation.right_side().isa_variable() == false);
        
        // The equation should be f(x0,x1,x2) = f(x2,x0,x1)
        let left_str = format!("{}", equation.left_side());
        let right_str = format!("{}", equation.right_side());
        
        assert!(left_str.contains("ternary_op"));
        assert!(right_str.contains("ternary_op"));
    }
    
    #[test]
    fn test_cyclic_law_unary() {
        let f = OperationSymbol::new("unary_op", 1, false);
        let equation = cyclic_law(&f).unwrap();
        
        // For unary operation: f(x0) = f(x0) (trivial)
        let left_str = format!("{}", equation.left_side());
        let right_str = format!("{}", equation.right_side());
        
        assert!(left_str.contains("unary_op"));
        assert!(right_str.contains("unary_op"));
    }
    
    #[test]
    fn test_cyclic_law_zero_arity() {
        let f = OperationSymbol::new("constant", 0, false);
        let result = cyclic_law(&f);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("arity must be at least 1"));
    }
    
    #[test]
    fn test_first_second_symmetric_law_binary() {
        let f = OperationSymbol::new("binary_op", 2, false);
        let equation = first_second_symmetric_law(&f).unwrap();
        
        // Check that we got an equation
        assert!(equation.left_side().isa_variable() == false);
        assert!(equation.right_side().isa_variable() == false);
        
        // The equation should be f(x0,x1) = f(x1,x0)
        let left_str = format!("{}", equation.left_side());
        let right_str = format!("{}", equation.right_side());
        
        assert!(left_str.contains("binary_op"));
        assert!(right_str.contains("binary_op"));
    }
    
    #[test]
    fn test_first_second_symmetric_law_ternary() {
        let f = OperationSymbol::new("ternary_op", 3, false);
        let equation = first_second_symmetric_law(&f).unwrap();
        
        // The equation should be f(x0,x1,x2) = f(x1,x0,x2)
        let left_str = format!("{}", equation.left_side());
        let right_str = format!("{}", equation.right_side());
        
        assert!(left_str.contains("ternary_op"));
        assert!(right_str.contains("ternary_op"));
    }
    
    #[test]
    fn test_first_second_symmetric_law_unary() {
        let f = OperationSymbol::new("unary_op", 1, false);
        let result = first_second_symmetric_law(&f);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("arity must be at least 2"));
    }
    
    #[test]
    fn test_first_second_symmetric_law_zero_arity() {
        let f = OperationSymbol::new("constant", 0, false);
        let result = first_second_symmetric_law(&f);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("arity must be at least 2"));
    }
}
