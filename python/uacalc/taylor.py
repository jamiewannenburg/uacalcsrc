"""
Taylor module for UACalc

This module provides Python bindings for Taylor term construction, 
polynomial expansion, and Taylor series computation.
"""

from typing import List, Tuple, Optional, Union
import uacalc_rust

# Import Taylor types from the Rust extension
try:
    from uacalc_rust import (
        IntArray, PolynomialCoefficient, Polynomial, TaylorSpec, 
        Taylor, TaylorSeries, markovic_mckenzie_term, siggers_term,
        create_int_array, create_polynomial, create_taylor_spec, 
        create_taylor, create_taylor_series, expand_taylor_term,
        expand_taylor_term_around_point
    )
    TAYLOR_AVAILABLE = True
except ImportError:
    TAYLOR_AVAILABLE = False
    # Create dummy classes for when Taylor functionality is not available
    class IntArray:
        def __init__(self, *args, **kwargs):
            raise ImportError("Taylor functionality not available")
    
    class PolynomialCoefficient:
        def __init__(self, *args, **kwargs):
            raise ImportError("Taylor functionality not available")
    
    class Polynomial:
        def __init__(self, *args, **kwargs):
            raise ImportError("Taylor functionality not available")
    
    class TaylorSpec:
        def __init__(self, *args, **kwargs):
            raise ImportError("Taylor functionality not available")
    
    class Taylor:
        def __init__(self, *args, **kwargs):
            raise ImportError("Taylor functionality not available")
    
    class TaylorSeries:
        def __init__(self, *args, **kwargs):
            raise ImportError("Taylor functionality not available")
    
    def markovic_mckenzie_term():
        raise ImportError("Taylor functionality not available")
    
    def siggers_term():
        raise ImportError("Taylor functionality not available")
    
    def create_int_array(*args, **kwargs):
        raise ImportError("Taylor functionality not available")
    
    def create_polynomial(*args, **kwargs):
        raise ImportError("Taylor functionality not available")
    
    def create_taylor_spec(*args, **kwargs):
        raise ImportError("Taylor functionality not available")
    
    def create_taylor(*args, **kwargs):
        raise ImportError("Taylor functionality not available")
    
    def create_taylor_series(*args, **kwargs):
        raise ImportError("Taylor functionality not available")
    
    def expand_taylor_term(*args, **kwargs):
        raise ImportError("Taylor functionality not available")
    
    def expand_taylor_term_around_point(*args, **kwargs):
        raise ImportError("Taylor functionality not available")


class TaylorExpansion:
    """
    High-level interface for Taylor expansion operations.
    
    This class provides convenient methods for working with Taylor terms
    and their polynomial expansions.
    """
    
    def __init__(self):
        if not TAYLOR_AVAILABLE:
            raise ImportError("Taylor functionality not available")
    
    @staticmethod
    def create_markovic_mckenzie_term() -> Taylor:
        """Create a Markovic-McKenzie term."""
        return markovic_mckenzie_term()
    
    @staticmethod
    def create_siggers_term() -> Taylor:
        """Create a Siggers term."""
        return siggers_term()
    
    @staticmethod
    def create_custom_taylor_term(
        arity: int, 
        equations: List[Tuple[List[int], List[int]]], 
        symbol_name: str
    ) -> Taylor:
        """
        Create a custom Taylor term.
        
        Args:
            arity: The arity of the operation
            equations: List of equation pairs (left, right) as integer arrays
            symbol_name: Name of the operation symbol
            
        Returns:
            A Taylor term with the specified properties
        """
        # Create operation symbol
        from uacalc.operation import OperationSymbol
        symbol = OperationSymbol(symbol_name, arity)
        
        # Convert equations to IntArray pairs
        int_array_equations = []
        for left, right in equations:
            left_array = IntArray.from_vec(left)
            right_array = IntArray.from_vec(right)
            int_array_equations.append((left_array, right_array))
        
        # Create Taylor specification
        spec = create_taylor_spec(arity, int_array_equations, symbol)
        
        # Create Taylor term
        return create_taylor(spec)
    
    @staticmethod
    def expand_as_polynomial(
        taylor_term: Taylor, 
        max_degree: int = 2
    ) -> Polynomial:
        """
        Expand a Taylor term as a polynomial.
        
        Args:
            taylor_term: The Taylor term to expand
            max_degree: Maximum degree of the polynomial expansion
            
        Returns:
            A polynomial representation of the Taylor term
        """
        return expand_taylor_term(taylor_term, max_degree)
    
    @staticmethod
    def expand_around_point(
        taylor_term: Taylor, 
        expansion_point: List[float], 
        max_degree: int = 2
    ) -> Polynomial:
        """
        Expand a Taylor term around a specific point.
        
        Args:
            taylor_term: The Taylor term to expand
            expansion_point: The point around which to expand
            max_degree: Maximum degree of the polynomial expansion
            
        Returns:
            A polynomial representation of the Taylor term
        """
        return expand_taylor_term_around_point(taylor_term, expansion_point, max_degree)
    
    @staticmethod
    def create_taylor_series(
        taylor_term: Taylor, 
        expansion_point: List[float], 
        max_degree: int = 2
    ) -> TaylorSeries:
        """
        Create a Taylor series for a Taylor term.
        
        Args:
            taylor_term: The Taylor term
            expansion_point: The point around which to expand
            max_degree: Maximum degree of the series
            
        Returns:
            A Taylor series representation
        """
        return create_taylor_series(taylor_term, expansion_point, max_degree)


class PolynomialUtils:
    """
    Utility functions for working with polynomials.
    """
    
    @staticmethod
    def evaluate_polynomial(polynomial: Polynomial, values: List[float]) -> float:
        """
        Evaluate a polynomial at given values.
        
        Args:
            polynomial: The polynomial to evaluate
            values: Values for the variables
            
        Returns:
            The result of the evaluation
        """
        return polynomial.evaluate(values)
    
    @staticmethod
    def get_derivative(polynomial: Polynomial, variable_index: int) -> Polynomial:
        """
        Get the derivative of a polynomial with respect to a variable.
        
        Args:
            polynomial: The polynomial to differentiate
            variable_index: Index of the variable to differentiate with respect to
            
        Returns:
            The derivative polynomial
        """
        return polynomial.derivative(variable_index)
    
    @staticmethod
    def get_integral(polynomial: Polynomial, variable_index: int) -> Polynomial:
        """
        Get the integral of a polynomial with respect to a variable.
        
        Args:
            polynomial: The polynomial to integrate
            variable_index: Index of the variable to integrate with respect to
            
        Returns:
            The integral polynomial
        """
        return polynomial.integral(variable_index)
    
    @staticmethod
    def print_polynomial(polynomial: Polynomial) -> str:
        """
        Print a polynomial in a readable format.
        
        Args:
            polynomial: The polynomial to print
            
        Returns:
            A string representation of the polynomial
        """
        if not polynomial.coefficients():
            return "0"
        
        terms = []
        for coeff in polynomial.coefficients():
            if coeff.is_constant():
                terms.append(f"{coeff.value()}")
            else:
                term_parts = []
                for i, (var_idx, power) in enumerate(zip(coeff.variable_indices(), coeff.powers())):
                    if power == 1:
                        term_parts.append(f"x{var_idx}")
                    elif power > 1:
                        term_parts.append(f"x{var_idx}^{power}")
                
                if coeff.value() == 1.0:
                    term_str = " * ".join(term_parts)
                else:
                    term_str = f"{coeff.value()} * " + " * ".join(term_parts)
                
                terms.append(term_str)
        
        return " + ".join(terms)


# Convenience functions for common operations
def create_majority_term() -> Taylor:
    """Create a majority term (3-ary operation)."""
    equations = [
        ([1, 0, 0], [0, 0, 1]),  # maj(x,x,y) = x
        ([0, 1, 0], [0, 0, 1]),  # maj(x,y,x) = x
        ([0, 0, 1], [1, 0, 0]),  # maj(y,x,x) = x
    ]
    return TaylorExpansion.create_custom_taylor_term(3, equations, "maj")


def create_minority_term() -> Taylor:
    """Create a minority term (3-ary operation)."""
    equations = [
        ([1, 0, 0], [0, 0, 1]),  # min(x,x,y) = y
        ([0, 1, 0], [0, 0, 1]),  # min(x,y,x) = y
        ([0, 0, 1], [1, 0, 0]),  # min(y,x,x) = y
    ]
    return TaylorExpansion.create_custom_taylor_term(3, equations, "min")


def create_maltsev_term() -> Taylor:
    """Create a Maltsev term (3-ary operation)."""
    equations = [
        ([1, 0, 0], [0, 0, 1]),  # p(x,x,y) = y
        ([0, 1, 0], [1, 0, 0]),  # p(x,y,x) = x
    ]
    return TaylorExpansion.create_custom_taylor_term(3, equations, "p")


def create_pixley_term() -> Taylor:
    """Create a Pixley term (3-ary operation)."""
    equations = [
        ([1, 0, 0], [0, 0, 1]),  # pix(x,x,y) = y
        ([0, 1, 0], [0, 0, 1]),  # pix(x,y,x) = y
        ([0, 0, 1], [1, 0, 0]),  # pix(y,x,x) = x
    ]
    return TaylorExpansion.create_custom_taylor_term(3, equations, "pix")


# Export the main classes and functions
__all__ = [
    'IntArray', 'PolynomialCoefficient', 'Polynomial', 'TaylorSpec', 
    'Taylor', 'TaylorSeries', 'TaylorExpansion', 'PolynomialUtils',
    'markovic_mckenzie_term', 'siggers_term', 'create_majority_term',
    'create_minority_term', 'create_maltsev_term', 'create_pixley_term',
    'TAYLOR_AVAILABLE'
]
