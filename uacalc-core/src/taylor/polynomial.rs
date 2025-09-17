//! Polynomial expansion algorithms for Taylor terms
//! 
//! This module provides efficient polynomial expansion algorithms for
//! Taylor terms, including Taylor series computation and polynomial
//! manipulation operations.

use crate::{UACalcError, UACalcResult};
use crate::taylor::{Taylor, IntArray};

/// Polynomial coefficient representation
#[derive(Debug, Clone, PartialEq)]
pub struct PolynomialCoefficient {
    /// The coefficient value
    pub value: f64,
    /// The variable indices for this monomial
    pub variable_indices: Vec<usize>,
    /// The powers for each variable
    pub powers: Vec<usize>,
}

impl PolynomialCoefficient {
    /// Create a new polynomial coefficient
    pub fn new(value: f64, variable_indices: Vec<usize>, powers: Vec<usize>) -> UACalcResult<Self> {
        if variable_indices.len() != powers.len() {
            return Err(UACalcError::InvalidOperation {
                message: "Variable indices and powers must have the same length".to_string(),
            });
        }
        
        Ok(Self {
            value,
            variable_indices,
            powers,
        })
    }
    
    /// Get the degree of this monomial
    pub fn degree(&self) -> usize {
        self.powers.iter().sum()
    }
    
    /// Check if this is a constant term
    pub fn is_constant(&self) -> bool {
        self.powers.iter().all(|&p| p == 0)
    }
    
    /// Get the total number of variables
    pub fn variable_count(&self) -> usize {
        self.variable_indices.len()
    }
}

/// Polynomial representation
#[derive(Debug, Clone)]
pub struct Polynomial {
    /// The coefficients of the polynomial
    pub coefficients: Vec<PolynomialCoefficient>,
    /// The maximum degree
    pub max_degree: usize,
    /// The number of variables
    pub variable_count: usize,
}

impl Polynomial {
    /// Create a new polynomial
    pub fn new(variable_count: usize) -> Self {
        Self {
            coefficients: Vec::new(),
            max_degree: 0,
            variable_count,
        }
    }
    
    /// Add a coefficient to the polynomial
    pub fn add_coefficient(&mut self, coeff: PolynomialCoefficient) -> UACalcResult<()> {
        if coeff.variable_count() > self.variable_count {
            return Err(UACalcError::InvalidOperation {
                message: "Coefficient has more variables than polynomial".to_string(),
            });
        }
        
        self.max_degree = self.max_degree.max(coeff.degree());
        self.coefficients.push(coeff);
        Ok(())
    }
    
    /// Get the coefficient for a specific monomial
    pub fn get_coefficient(&self, variable_indices: &[usize], powers: &[usize]) -> f64 {
        for coeff in &self.coefficients {
            if coeff.variable_indices == variable_indices && coeff.powers == powers {
                return coeff.value;
            }
        }
        0.0
    }
    
    /// Evaluate the polynomial at given values
    pub fn evaluate(&self, values: &[f64]) -> UACalcResult<f64> {
        if values.len() < self.variable_count {
            return Err(UACalcError::InvalidOperation {
                message: "Not enough values provided for polynomial evaluation".to_string(),
            });
        }
        
        let mut result = 0.0;
        
        for coeff in &self.coefficients {
            let mut term_value = coeff.value;
            
            for (i, &power) in coeff.powers.iter().enumerate() {
                let var_index = coeff.variable_indices[i];
                let var_value = values[var_index];
                term_value *= var_value.powi(power as i32);
            }
            
            result += term_value;
        }
        
        Ok(result)
    }
    
    /// Get the derivative with respect to a variable
    pub fn derivative(&self, variable_index: usize) -> UACalcResult<Self> {
        let mut result = Self::new(self.variable_count);
        
        for coeff in &self.coefficients {
            // Find the power of the variable in this coefficient
            let mut var_pos = None;
            
            for (i, &var_idx) in coeff.variable_indices.iter().enumerate() {
                if var_idx == variable_index {
                    var_pos = Some(i);
                    break;
                }
            }
            
            if let Some(pos) = var_pos {
                let power = coeff.powers[pos];
                if power > 0 {
                    // Create new coefficient with reduced power
                    let new_indices = coeff.variable_indices.clone();
                    let mut new_powers = coeff.powers.clone();
                    
                    new_powers[pos] -= 1;
                    let new_value = coeff.value * power as f64;
                    
                    // Only add if the new power is >= 0
                    if new_powers[pos] >= 0 {
                        let new_coeff = PolynomialCoefficient::new(
                            new_value,
                            new_indices,
                            new_powers,
                        )?;
                        result.add_coefficient(new_coeff)?;
                    }
                }
            }
        }
        
        Ok(result)
    }
    
    /// Get the integral with respect to a variable
    pub fn integral(&self, variable_index: usize) -> UACalcResult<Self> {
        let mut result = Self::new(self.variable_count);
        
        for coeff in &self.coefficients {
            // Find the power of the variable in this coefficient
            let mut var_pos = None;
            
            for (i, &var_idx) in coeff.variable_indices.iter().enumerate() {
                if var_idx == variable_index {
                    var_pos = Some(i);
                    break;
                }
            }
            
            // Create new coefficient with increased power
            let mut new_indices = coeff.variable_indices.clone();
            let mut new_powers = coeff.powers.clone();
            
            if let Some(pos) = var_pos {
                new_powers[pos] += 1;
                let new_value = coeff.value / (new_powers[pos] as f64);
                
                let new_coeff = PolynomialCoefficient::new(
                    new_value,
                    new_indices,
                    new_powers,
                )?;
                result.add_coefficient(new_coeff)?;
            } else {
                // Variable not present, add it with power 1
                new_indices.push(variable_index);
                new_powers.push(1);
                
                let new_coeff = PolynomialCoefficient::new(
                    coeff.value,
                    new_indices,
                    new_powers,
                )?;
                result.add_coefficient(new_coeff)?;
            }
        }
        
        Ok(result)
    }
}

/// Taylor series expansion for a Taylor term
#[derive(Debug, Clone)]
pub struct TaylorSeries {
    /// The original Taylor term
    pub taylor_term: Taylor,
    /// The polynomial expansion
    pub polynomial: Polynomial,
    /// The expansion point
    pub expansion_point: Vec<f64>,
    /// The maximum degree of the expansion
    pub max_degree: usize,
}

impl TaylorSeries {
    /// Create a new Taylor series expansion
    pub fn new(
        taylor_term: Taylor,
        expansion_point: Vec<f64>,
        max_degree: usize,
    ) -> UACalcResult<Self> {
        let variable_count = taylor_term.arity();
        
        if expansion_point.len() != variable_count {
            return Err(UACalcError::InvalidOperation {
                message: "Expansion point must have same dimension as Taylor term arity".to_string(),
            });
        }
        
        let polynomial = Self::compute_taylor_expansion(&taylor_term, &expansion_point, max_degree)?;
        
        Ok(Self {
            taylor_term,
            polynomial,
            expansion_point,
            max_degree,
        })
    }
    
    /// Compute the Taylor expansion of a Taylor term
    fn compute_taylor_expansion(
        taylor_term: &Taylor,
        expansion_point: &[f64],
        max_degree: usize,
    ) -> UACalcResult<Polynomial> {
        let mut polynomial = Polynomial::new(taylor_term.arity());
        
        // For Taylor terms, we need to compute the expansion based on the defining equations
        // This is a simplified implementation that generates polynomial terms
        
        // Add constant term (evaluation at expansion point)
        let constant_value = Self::evaluate_taylor_at_point(taylor_term, expansion_point)?;
        let constant_coeff = PolynomialCoefficient::new(
            constant_value,
            vec![],
            vec![],
        )?;
        polynomial.add_coefficient(constant_coeff)?;
        
        // Add linear terms (first derivatives)
        for i in 0..taylor_term.arity() {
            let derivative_value = Self::compute_derivative_at_point(taylor_term, expansion_point, i)?;
            if derivative_value.abs() > 1e-10 {
                let linear_coeff = PolynomialCoefficient::new(
                    derivative_value,
                    vec![i],
                    vec![1],
                )?;
                polynomial.add_coefficient(linear_coeff)?;
            }
        }
        
        // Add higher-order terms if max_degree > 1
        if max_degree > 1 {
            for degree in 2..=max_degree {
                Self::add_degree_terms(&mut polynomial, taylor_term, expansion_point, degree)?;
            }
        }
        
        Ok(polynomial)
    }
    
    /// Evaluate a Taylor term at a specific point
    fn evaluate_taylor_at_point(taylor_term: &Taylor, point: &[f64]) -> UACalcResult<f64> {
        // Convert the point to an IntArray for evaluation
        let mut assignment = IntArray::new(taylor_term.arity());
        for (i, &value) in point.iter().enumerate() {
            // Convert float to integer (simplified)
            let int_value = if value > 0.5 { 1 } else { 0 };
            assignment.set(i, int_value)?;
        }
        
        // Check if the assignment satisfies the equations
        if taylor_term.satisfies_equations_with_assignment(&assignment) {
            Ok(1.0) // Satisfies equations
        } else {
            Ok(0.0) // Doesn't satisfy equations
        }
    }
    
    /// Compute the derivative of a Taylor term at a specific point
    fn compute_derivative_at_point(
        taylor_term: &Taylor,
        point: &[f64],
        variable_index: usize,
    ) -> UACalcResult<f64> {
        // Create a small perturbation
        let epsilon = 1e-6;
        let mut perturbed_point = point.to_vec();
        perturbed_point[variable_index] += epsilon;
        
        let original_value = Self::evaluate_taylor_at_point(taylor_term, point)?;
        let perturbed_value = Self::evaluate_taylor_at_point(taylor_term, &perturbed_point)?;
        
        Ok((perturbed_value - original_value) / epsilon)
    }
    
    /// Add terms of a specific degree to the polynomial
    fn add_degree_terms(
        polynomial: &mut Polynomial,
        taylor_term: &Taylor,
        expansion_point: &[f64],
        degree: usize,
    ) -> UACalcResult<()> {
        // Generate all possible combinations of variables with the given degree
        let variable_count = taylor_term.arity();
        
        // For simplicity, we'll add some basic higher-order terms
        // In a full implementation, this would generate all possible combinations
        
        for i in 0..variable_count {
            for j in 0..variable_count {
                if degree == 2 && i <= j {
                    // Add quadratic terms
                    let coeff_value = Self::compute_second_derivative_at_point(
                        taylor_term,
                        expansion_point,
                        i,
                        j,
                    )? / 2.0;
                    
                    if coeff_value.abs() > 1e-10 {
                        let (indices, powers) = if i == j {
                            (vec![i], vec![2])
                        } else {
                            (vec![i, j], vec![1, 1])
                        };
                        
                        let coeff = PolynomialCoefficient::new(coeff_value, indices, powers)?;
                        polynomial.add_coefficient(coeff)?;
                    }
                }
            }
        }
        
        Ok(())
    }
    
    /// Compute the second derivative of a Taylor term at a specific point
    fn compute_second_derivative_at_point(
        taylor_term: &Taylor,
        point: &[f64],
        var1: usize,
        var2: usize,
    ) -> UACalcResult<f64> {
        let epsilon = 1e-6;
        
        // Create perturbed points
        let mut point_pp = point.to_vec();
        point_pp[var1] += epsilon;
        point_pp[var2] += epsilon;
        
        let mut point_pm = point.to_vec();
        point_pm[var1] += epsilon;
        point_pm[var2] -= epsilon;
        
        let mut point_mp = point.to_vec();
        point_mp[var1] -= epsilon;
        point_mp[var2] += epsilon;
        
        let mut point_mm = point.to_vec();
        point_mm[var1] -= epsilon;
        point_mm[var2] -= epsilon;
        
        let f_pp = Self::evaluate_taylor_at_point(taylor_term, &point_pp)?;
        let f_pm = Self::evaluate_taylor_at_point(taylor_term, &point_pm)?;
        let f_mp = Self::evaluate_taylor_at_point(taylor_term, &point_mp)?;
        let f_mm = Self::evaluate_taylor_at_point(taylor_term, &point_mm)?;
        
        Ok((f_pp - f_pm - f_mp + f_mm) / (4.0 * epsilon * epsilon))
    }
    
    /// Evaluate the Taylor series at a given point
    pub fn evaluate(&self, point: &[f64]) -> UACalcResult<f64> {
        self.polynomial.evaluate(point)
    }
    
    /// Get the polynomial representation
    pub fn polynomial(&self) -> &Polynomial {
        &self.polynomial
    }
    
    /// Get the expansion point
    pub fn expansion_point(&self) -> &[f64] {
        &self.expansion_point
    }
    
    /// Get the maximum degree
    pub fn max_degree(&self) -> usize {
        self.max_degree
    }
}

/// Polynomial expansion utilities
pub struct PolynomialExpansion;

impl PolynomialExpansion {
    /// Expand a Taylor term as a polynomial
    pub fn expand_taylor_term(
        taylor_term: &Taylor,
        max_degree: usize,
    ) -> UACalcResult<Polynomial> {
        // Use expansion point at origin
        let expansion_point = vec![0.0; taylor_term.arity()];
        let taylor_series = TaylorSeries::new(taylor_term.clone(), expansion_point, max_degree)?;
        Ok(taylor_series.polynomial)
    }
    
    /// Expand a Taylor term around a specific point
    pub fn expand_taylor_term_around_point(
        taylor_term: &Taylor,
        expansion_point: Vec<f64>,
        max_degree: usize,
    ) -> UACalcResult<Polynomial> {
        let taylor_series = TaylorSeries::new(taylor_term.clone(), expansion_point, max_degree)?;
        Ok(taylor_series.polynomial)
    }
    
    /// Compute the Taylor series for a Taylor term
    pub fn compute_taylor_series(
        taylor_term: &Taylor,
        expansion_point: Vec<f64>,
        max_degree: usize,
    ) -> UACalcResult<TaylorSeries> {
        TaylorSeries::new(taylor_term.clone(), expansion_point, max_degree)
    }
    
    /// Check if a polynomial is a valid Taylor expansion
    pub fn is_valid_taylor_expansion(polynomial: &Polynomial) -> bool {
        // Check basic properties of a valid Taylor expansion
        // 1. Should have a constant term
        let has_constant = polynomial.coefficients.iter().any(|c| c.is_constant());
        
        // 2. All coefficients should have reasonable values
        let has_reasonable_coeffs = polynomial.coefficients.iter().all(|c| c.value.is_finite());
        
        // 3. Variable indices should be within bounds
        let valid_indices = polynomial.coefficients.iter().all(|c| {
            c.variable_indices.iter().all(|&i| i < polynomial.variable_count)
        });
        
        has_constant && has_reasonable_coeffs && valid_indices
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::taylor::taylor::markovic_mckenzie_term;
    
    #[test]
    fn test_polynomial_coefficient_creation() {
        let coeff = PolynomialCoefficient::new(2.5, vec![0, 1], vec![1, 2]).unwrap();
        assert_eq!(coeff.value, 2.5);
        assert_eq!(coeff.variable_indices, vec![0, 1]);
        assert_eq!(coeff.powers, vec![1, 2]);
        assert_eq!(coeff.degree(), 3);
        assert!(!coeff.is_constant());
    }
    
    #[test]
    fn test_polynomial_creation() {
        let mut poly = Polynomial::new(2);
        let coeff1 = PolynomialCoefficient::new(1.0, vec![0], vec![1]).unwrap();
        let coeff2 = PolynomialCoefficient::new(2.0, vec![1], vec![2]).unwrap();
        
        poly.add_coefficient(coeff1).unwrap();
        poly.add_coefficient(coeff2).unwrap();
        
        assert_eq!(poly.variable_count, 2);
        assert_eq!(poly.max_degree, 2);
        assert_eq!(poly.coefficients.len(), 2);
    }
    
    #[test]
    fn test_polynomial_evaluation() {
        let mut poly = Polynomial::new(2);
        let coeff1 = PolynomialCoefficient::new(1.0, vec![0], vec![1]).unwrap(); // x
        let coeff2 = PolynomialCoefficient::new(2.0, vec![1], vec![2]).unwrap(); // 2y^2
        
        poly.add_coefficient(coeff1).unwrap();
        poly.add_coefficient(coeff2).unwrap();
        
        let result = poly.evaluate(&[3.0, 2.0]).unwrap();
        assert!((result - (3.0 + 2.0 * 4.0)).abs() < 1e-10);
    }
    
    #[test]
    fn test_polynomial_derivative() {
        let mut poly = Polynomial::new(2);
        let coeff1 = PolynomialCoefficient::new(3.0, vec![0], vec![2]).unwrap(); // 3x^2
        let coeff2 = PolynomialCoefficient::new(2.0, vec![1], vec![1]).unwrap(); // 2y
        
        poly.add_coefficient(coeff1).unwrap();
        poly.add_coefficient(coeff2).unwrap();
        
        let derivative = poly.derivative(0).unwrap(); // d/dx
        assert_eq!(derivative.coefficients.len(), 1);
        assert_eq!(derivative.coefficients[0].value, 6.0); // 6x
    }
    
    #[test]
    fn test_taylor_series_creation() {
        let taylor_term = markovic_mckenzie_term();
        let expansion_point = vec![0.0, 0.0, 0.0, 0.0];
        
        let taylor_series = TaylorSeries::new(taylor_term, expansion_point, 2).unwrap();
        assert_eq!(taylor_series.max_degree, 2);
        assert_eq!(taylor_series.expansion_point.len(), 4);
    }
    
    #[test]
    fn test_polynomial_expansion() {
        let taylor_term = markovic_mckenzie_term();
        let polynomial = PolynomialExpansion::expand_taylor_term(&taylor_term, 2).unwrap();
        
        assert!(PolynomialExpansion::is_valid_taylor_expansion(&polynomial));
        assert_eq!(polynomial.variable_count, 4);
    }
}
