"""
Term Parsing and Evaluation

This module provides comprehensive term parsing, evaluation, and manipulation
utilities for universal algebra computations.
"""

from typing import Optional, Dict, List, Tuple, Union, Any, Callable
from typing_extensions import Protocol
import re
import warnings

from . import (
    Term, TermArena, Algebra, Operation, 
    create_term_arena, parse_term, eval_term, HAS_NUMPY
)

class TermParser:
    """Enhanced term parser with support for complex expressions and variable names."""
    
    def __init__(self, arena: Optional[TermArena] = None):
        self.arena = arena or create_term_arena()
        self._var_names: Dict[str, int] = {}
        self._next_var_index = 0
    
    def parse(self, expr: str) -> Term:
        """Parse a term expression.
        
        Args:
            expr: String representation of the term
            
        Returns:
            Parsed term object
            
        Raises:
            ValueError: If the expression is malformed
        """
        # Use the improved Rust parser
        return parse_term(self.arena, expr)
    
    def parse_with_variables(self, expr: str, var_names: Dict[str, int]) -> Term:
        """Parse a term with named variables.
        
        Args:
            expr: String representation of the term
            var_names: Dictionary mapping variable names to indices
            
        Returns:
            Parsed term object
        """
        # Store variable mapping
        self._var_names = var_names.copy()
        self._next_var_index = max(var_names.values()) + 1 if var_names else 0
        
        # Replace variable names with indices
        processed_expr = self._replace_variable_names(expr)
        
        return self.parse(processed_expr)
    
    def _replace_variable_names(self, expr: str) -> str:
        """Replace variable names with x0, x1, etc. format."""
        # Sort by length (longest first) to avoid partial matches
        sorted_names = sorted(self._var_names.keys(), key=len, reverse=True)
        
        result = expr
        for name in sorted_names:
            index = self._var_names[name]
            result = re.sub(r'\b' + re.escape(name) + r'\b', f'x{index}', result)
        
        return result
    
    def validate_syntax(self, expr: str) -> Tuple[bool, Optional[str]]:
        """Validate term syntax without parsing.
        
        Args:
            expr: String to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Basic syntax checks
            if not expr.strip():
                return False, "Empty expression"
            
            # Check balanced parentheses
            if not self._check_balanced_parentheses(expr):
                return False, "Unbalanced parentheses"
            
            # Check for invalid characters
            if not self._check_valid_characters(expr):
                return False, "Invalid characters in expression"
            
            # Check for specific syntax errors
            error = self._check_specific_syntax_errors(expr)
            if error:
                return False, error
            
            # Try to parse (this will catch most syntax errors)
            # Only try to parse if basic checks pass to avoid Rust panics
            try:
                _ = self.parse(expr)
                return True, None
            except Exception as parse_error:
                return False, f"Parse error: {parse_error}"
            
        except Exception as e:
            return False, str(e)
    
    def _check_balanced_parentheses(self, expr: str) -> bool:
        """Check if parentheses are balanced."""
        stack = []
        for char in expr:
            if char == '(':
                stack.append(char)
            elif char == ')':
                if not stack:
                    return False
                stack.pop()
        return len(stack) == 0
    
    def _check_valid_characters(self, expr: str) -> bool:
        """Check for valid characters in expression."""
        # Allow letters, numbers, parentheses, commas, spaces, and common symbols
        valid_pattern = r'^[a-zA-Z0-9\(\)\[\],\s\+\-\*\/\^_]+$'
        return bool(re.match(valid_pattern, expr))
    
    def _check_specific_syntax_errors(self, expr: str) -> Optional[str]:
        """Check for specific syntax errors like trailing commas, missing arguments."""
        # Check for trailing comma in function calls
        if re.search(r'\([^)]*,\s*\)', expr):
            return "Missing argument after comma"
        
        # Check for leading comma in function calls
        if re.search(r'\(\s*,', expr):
            return "Missing argument before comma"
        
        # Check for consecutive commas
        if re.search(r',\s*,', expr):
            return "Consecutive commas"
        
        # Check for missing comma between arguments
        if re.search(r'[a-zA-Z0-9_]\s+[a-zA-Z0-9_]', expr):
            return "Missing comma between arguments"
        
        return None

class TermEvaluator:
    """Term evaluator with caching and optimization."""
    
    def __init__(self, algebra: Algebra):
        self.algebra = algebra
        self._cache: Dict[Tuple[str, Tuple[int, ...]], int] = {}
        self._arena = create_term_arena()
    
    def eval(self, term: Union[Term, str], variables: Dict[int, int]) -> int:
        """Evaluate a term with given variable assignment.
        
        Args:
            term: Term object or string expression
            variables: Dictionary mapping variable indices to values
            
        Returns:
            Result of evaluation
            
        Raises:
            ValueError: If any required variables are missing
        """
        if isinstance(term, str):
            term = parse_term(self._arena, term)
        
        # Check for missing variables
        required_vars = term_variables(term)
        missing_vars = [var for var in required_vars if var not in variables]
        if missing_vars:
            raise ValueError(f"Missing variables: {missing_vars}")
        
        # Create cache key
        cache_key = (term.to_string(), tuple(sorted(variables.items())))
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Evaluate
        result = eval_term(term, self.algebra, variables)
        
        # Cache result
        self._cache[cache_key] = result
        
        return result
    
    def eval_batch(self, terms: List[Union[Term, str]], 
                  variable_sets: List[Dict[int, int]]) -> List[int]:
        """Evaluate multiple terms with different variable assignments.
        
        Args:
            terms: List of terms to evaluate
            variable_sets: List of variable assignments
            
        Returns:
            List of evaluation results
        """
        if len(terms) != len(variable_sets):
            raise ValueError("Number of terms must match number of variable sets")
        
        results = []
        for term, variables in zip(terms, variable_sets):
            results.append(self.eval(term, variables))
        
        return results
    
    def to_operation_table(self, term: Union[Term, str], arity: int) -> List[List[int]]:
        """Convert a term to an operation table.
        
        Args:
            term: Term to convert
            arity: Arity of the resulting operation
            
        Returns:
            Operation table as nested list
        """
        if isinstance(term, str):
            term = parse_term(self._arena, term)
        
        # Determine universe size
        universe_size = self.algebra.cardinality
        
        # Generate all possible input combinations
        if arity == 0:
            # Constant operation
            result = self.eval(term, {})
            return [[result]]
        elif arity == 1:
            # Unary operation
            table = []
            for i in range(universe_size):
                result = self.eval(term, {0: i})
                table.append([result])
            return table
        elif arity == 2:
            # Binary operation
            table = []
            for i in range(universe_size):
                row = []
                for j in range(universe_size):
                    result = self.eval(term, {0: i, 1: j})
                    row.append(result)
                table.append(row)
            return table
        else:
            # Higher arity - return flat table
            table = []
            for args in self._generate_combinations(universe_size, arity):
                variables = {i: val for i, val in enumerate(args)}
                result = self.eval(term, variables)
                table.append(list(args) + [result])
            return table
    
    def _generate_combinations(self, universe_size: int, arity: int) -> List[Tuple[int, ...]]:
        """Generate all combinations of universe elements for given arity."""
        if arity == 0:
            return [()]
        elif arity == 1:
            return [(i,) for i in range(universe_size)]
        else:
            # Recursive generation
            sub_combinations = self._generate_combinations(universe_size, arity - 1)
            combinations = []
            for sub_combo in sub_combinations:
                for i in range(universe_size):
                    combinations.append(sub_combo + (i,))
            return combinations
    
    def clear_cache(self):
        """Clear the evaluation cache."""
        self._cache.clear()

def substitute_variables(term: Term, substitutions: Dict[int, Union[int, Term]]) -> Term:
    """Substitute variables in a term.
    
    Args:
        term: Term to substitute in
        substitutions: Dictionary mapping variable indices to values or terms
        
    Returns:
        Term with substitutions applied
    """
    # Convert substitutions to the format expected by Rust
    rust_substitutions = {}
    for var_index, substitute in substitutions.items():
        if isinstance(substitute, int):
            # If substitute is an int, treat it as a variable index
            substitute_term = term.arena.make_variable(substitute)
        elif isinstance(substitute, Term):
            # If substitute is a Term, use its term_id
            substitute_term = substitute.term_id
        else:
            raise ValueError(f"Invalid substitution type: {type(substitute)}")
        
        rust_substitutions[var_index] = substitute_term
    
    # Call the Rust substitution method
    substituted_term_id = term.arena.substitute_term(term.term_id, rust_substitutions)
    
    # Return a new Term object with the substituted term_id
    return Term(substituted_term_id, term.arena)

def simplify_term(term: Term, algebra: Algebra) -> Term:
    """Simplify a term using algebra properties.
    
    Args:
        term: Term to simplify
        algebra: Algebra for simplification rules
        
    Returns:
        Simplified term
    """
    # TODO: Implement term simplification
    # For now, return the original term
    return term

def term_depth(term: Term) -> int:
    """Get the depth of a term.
    
    Args:
        term: Term to analyze
        
    Returns:
        Depth of the term
    """
    return term.depth()

def term_variables(term: Term) -> List[int]:
    """Get all variables used in a term.
    
    Args:
        term: Term to analyze
        
    Returns:
        List of variable indices
    """
    return term.variables()

def term_operations(term: Term) -> List[str]:
    """Get all operation symbols used in a term.
    
    Args:
        term: Term to analyze
        
    Returns:
        List of operation symbols
    """
    operations = []
    
    def collect_operations(t: Term):
        if t.is_operation():
            # Get the operation symbol from the term
            # This requires accessing the symbol from the Rust implementation
            try:
                # Try to get symbol from term string representation
                term_str = t.to_string()
                if '(' in term_str:
                    symbol = term_str[:term_str.find('(')]
                    if symbol not in operations:
                        operations.append(symbol)
            except:
                pass
            
            # Recursively check children
            for i in range(t.arity()):
                try:
                    child = t.child(i)
                    collect_operations(child)
                except:
                    pass
    
    collect_operations(term)
    return operations

def terms_equal(term1: Term, term2: Term, algebra: Algebra) -> bool:
    """Check if two terms are semantically equal in an algebra.
    
    Args:
        term1: First term
        term2: Second term
        algebra: Algebra for equality checking
        
    Returns:
        True if terms are semantically equal
    """
    # TODO: Implement semantic equality checking
    # For now, compare string representations
    return term1.to_string() == term2.to_string()

# Factory functions for term construction
def variable(index: Union[int, str], arena: Optional[TermArena] = None) -> Term:
    """Create a variable term.
    
    Args:
        index: Variable index (int) or variable name (str like "x0", "x", "y", etc.)
        arena: Term arena to create the term in (creates new one if not provided)
        
    Returns:
        Variable term
    """
    if arena is None:
        arena = create_term_arena()
    
    if isinstance(index, str):
        # Handle x0, x1, x2 format
        if index.startswith('x'):
            try:
                index = int(index[1:])
            except ValueError:
                # Handle general variable names like "x", "y", "z"
                # Map them to indices based on their hash or position
                if len(index) == 1 and index.isalpha():
                    # Single letter variables: x->0, y->1, z->2, etc.
                    # Map a-z to 0-25, A-Z to 26-51
                    if index.islower():
                        index = ord(index) - ord('a')
                    else:
                        index = ord(index) - ord('A') + 26
                else:
                    # For other variable names, use hash-based mapping
                    index = hash(index) % 255  # Use modulo to fit in u8
        else:
            # For non-x variables, use hash-based mapping
            index = hash(index) % 255  # Use modulo to fit in u8
    
    return arena.make_variable(index)

def constant(symbol: str, arena: Optional[TermArena] = None) -> Term:
    """Create a constant term.
    
    Args:
        symbol: Operation symbol for the constant
        arena: Term arena to create the term in (creates new one if not provided)
        
    Returns:
        Constant term
    """
    if arena is None:
        arena = create_term_arena()
    return arena.make_term(symbol, [])

def operation(symbol: str, *args: Term, arena: Optional[TermArena] = None) -> Term:
    """Create an operation term.
    
    Args:
        symbol: Operation symbol
        *args: Child terms
        arena: Term arena to create the term in (creates new one if not provided)
        
    Returns:
        Operation term
    """
    if arena is None:
        arena = create_term_arena()
    return arena.make_term(symbol, list(args))

def from_operation_table(table: List[List[int]], var_names: Optional[List[str]] = None) -> Term:
    """Create a term from an operation table (reverse engineering).
    
    Args:
        table: Operation table
        var_names: Optional variable names
        
    Returns:
        Term representing the operation table
        
    Raises:
        ValueError: If table format is not supported
    """
    # TODO: Implement reverse engineering from operation table
    # This is a complex problem that requires solving systems of equations
    raise NotImplementedError("Reverse engineering from operation tables not yet implemented")

def random_term(depth: int, operations: List[str], variables: int, operation_arities: Optional[Dict[str, int]] = None) -> Term:
    """Generate a random term.
    
    Args:
        depth: Maximum depth of the term
        operations: List of available operation symbols
        variables: Number of available variables
        operation_arities: Dictionary mapping operation symbols to their arities
        
    Returns:
        Randomly generated term
    """
    import random
    
    arena = create_term_arena()
    
    def generate_random_term(current_depth: int) -> Term:
        if current_depth == 0 or random.random() < 0.3:
            # Create variable
            var_index = random.randint(0, variables - 1)
            return arena.make_variable(var_index)
        else:
            # Create operation
            symbol = random.choice(operations)
            
            # Determine arity based on operation_arities if provided
            if operation_arities and symbol in operation_arities:
                required_arity = operation_arities[symbol]
                # Only create operation if we have enough depth for the required arity
                if current_depth >= required_arity:
                    arity = required_arity
                else:
                    # Not enough depth, create variable instead
                    var_index = random.randint(0, variables - 1)
                    return arena.make_variable(var_index)
            else:
                # Default to binary operations if arity not specified
                arity = 2
                if current_depth < arity:
                    # Not enough depth, create variable instead
                    var_index = random.randint(0, variables - 1)
                    return arena.make_variable(var_index)
            
            children = [generate_random_term(current_depth - 1) for _ in range(arity)]
            return arena.make_term(symbol, children)
    
    return generate_random_term(depth)

# Integration with algebra operations
def term_to_operation(term: Term, symbol: str, algebra: Algebra) -> Operation:
    """Convert a term to an operation.
    
    Args:
        term: Term to convert
        symbol: Symbol for the new operation
        algebra: Algebra to add the operation to
        
    Returns:
        New operation
    """
    # Determine arity from term variables
    variables = term.variables()
    arity = max(variables) + 1 if variables else 0
    
    # Create operation table
    evaluator = TermEvaluator(algebra)
    table = evaluator.to_operation_table(term, arity)
    
    # Create operation
    from . import create_operation
    return create_operation(symbol, arity, table)

def validate_term_against_algebra(term: Term, algebra: Algebra) -> Tuple[bool, Optional[str]]:
    """Validate that a term is compatible with an algebra.
    
    Args:
        term: Term to validate
        algebra: Algebra to validate against
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check that all operation symbols exist in the algebra
        operations = term_operations(term)
        algebra_operations = [op.symbol for op in algebra.operations()]
        
        for op_symbol in operations:
            if op_symbol not in algebra_operations:
                return False, f"Operation '{op_symbol}' not found in algebra"
        
        # Check variable bounds
        variables = term_variables(term)
        if variables:
            max_var = max(variables)
            if max_var >= algebra.cardinality:
                return False, f"Variable index {max_var} exceeds algebra cardinality {algebra.cardinality}"
        
        return True, None
        
    except Exception as e:
        return False, str(e)

# NumPy integration for efficient batch evaluation
if HAS_NUMPY:
    import numpy as np
    
    def eval_term_numpy(term: Term, algebra: Algebra, variables: np.ndarray) -> np.ndarray:
        """Evaluate a term with NumPy array of variable assignments.
        
        Args:
            term: Term to evaluate
            algebra: Algebra to evaluate the term in
            variables: NumPy array of shape (n_assignments, n_variables)
            
        Returns:
            NumPy array of results
        """
        evaluator = TermEvaluator(algebra)
        results = []
        
        for i in range(variables.shape[0]):
            var_dict = {j: int(variables[i, j]) for j in range(variables.shape[1])}
            results.append(evaluator.eval(term, var_dict))
        
        return np.array(results)
    
    def batch_eval_terms(terms: List[Term], algebra: Algebra, variables: np.ndarray) -> np.ndarray:
        """Evaluate multiple terms with NumPy array of variable assignments.
        
        Args:
            terms: List of terms to evaluate
            algebra: Algebra to evaluate the terms in
            variables: NumPy array of shape (n_assignments, n_variables)
            
        Returns:
            NumPy array of shape (n_terms, n_assignments)
        """
        results = np.zeros((len(terms), variables.shape[0]), dtype=int)
        
        for i, term in enumerate(terms):
            results[i] = eval_term_numpy(term, algebra, variables)
        
        return results
else:
    # Fallback implementations without NumPy
    def eval_term_numpy(term: Term, algebra: Algebra, variables: List[List[int]]) -> List[int]:
        """Fallback implementation without NumPy."""
        warnings.warn("NumPy not available, using fallback implementation")
        return [eval_term(term, algebra, {i: val for i, val in enumerate(var_set)}) 
                for var_set in variables]
    
    def batch_eval_terms(terms: List[Term], algebra: Algebra, variables: List[List[int]]) -> List[List[int]]:
        """Fallback implementation without NumPy."""
        warnings.warn("NumPy not available, using fallback implementation")
        return [eval_term_numpy(term, algebra, variables) for term in terms]
