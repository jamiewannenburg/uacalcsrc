"""
High-level algebra utilities for UACalc.

This module provides convenient Python interfaces for creating and manipulating
algebras, with integration to Python's scientific computing ecosystem.
"""

from typing import List, Tuple, Optional, Dict, Any, Union, Callable
import warnings

from . import (
    Algebra, Operation, create_algebra, create_operation,
    CongruenceLattice, Term, TermArena, create_congruence_lattice,
    create_term_arena, parse_term, eval_term, HAS_NUMPY
)

# Conditionally import NumPy
if HAS_NUMPY:
    import numpy as np
else:
    np = None

class AlgebraBuilder:
    """Builder class for creating algebras with a fluent interface."""
    
    def __init__(self, name: str, size: int):
        """
        Initialize algebra builder.
        
        Args:
            name: Name of the algebra
            size: Size of the universe (number of elements)
        """
        self.name = name
        self.size = size
        self.universe = list(range(size))
        self.operations: Dict[str, Operation] = {}
        self._congruence_lattice: Optional[CongruenceLattice] = None
    
    def add_operation(self, name: str, operation: Operation) -> 'AlgebraBuilder':
        """Add an operation to the algebra."""
        self.operations[name] = operation
        return self
    
    def add_constant(self, name: str, value: int) -> 'AlgebraBuilder':
        """Add a constant operation."""
        if not 0 <= value < self.size:
            raise ValueError(f"Constant value {value} out of range [0, {self.size})")
        
        operation = create_operation(name, 0, [[value]])
        return self.add_operation(name, operation)
    
    def add_unary_operation(self, name: str, values: List[int]) -> 'AlgebraBuilder':
        """Add a unary operation defined by its values."""
        if len(values) != self.size:
            raise ValueError(f"Expected {self.size} values, got {len(values)}")
        
        table = [[i, values[i]] for i in range(self.size)]
        operation = create_operation(name, 1, table)
        return self.add_operation(name, operation)
    
    def add_binary_operation(self, name: str, table: List[List[int]]) -> 'AlgebraBuilder':
        """Add a binary operation defined by its table."""
        if len(table) != self.size:
            raise ValueError(f"Expected {self.size} rows, got {len(table)}")
        
        for i, row in enumerate(table):
            if len(row) != self.size:
                raise ValueError(f"Row {i} has {len(row)} columns, expected {self.size}")
        
        # Convert to the format expected by create_operation
        op_table = []
        for i in range(self.size):
            for j in range(self.size):
                op_table.append([i, j, table[i][j]])
        
        operation = create_operation(name, 2, op_table)
        return self.add_operation(name, operation)
    
    def add_term_operation(self, name: str, term_expr: str, variables: Optional[Dict[str, int]] = None) -> 'AlgebraBuilder':
        """Add an operation defined by a term expression.
        
        Args:
            name: Name of the operation
            term_expr: String representation of the term (e.g., "f(x0, g(x1))")
            variables: Optional mapping of variable names to indices
            
        Returns:
            Self for method chaining
        """
        # Create term arena and parse the term
        arena = create_term_arena()
        if variables:
            # Replace variable names with indices
            processed_expr = term_expr
            for var_name, var_index in variables.items():
                processed_expr = processed_expr.replace(var_name, f"x{var_index}")
            term = parse_term(arena, processed_expr)
        else:
            term = parse_term(arena, term_expr)
        
        # Determine arity from variables
        var_indices = term.variables()
        arity = max(var_indices) + 1 if var_indices else 0
        
        # Create operation table
        algebra = self.build()
        table = []
        for args in self._generate_combinations(list(range(self.size)), arity):
            var_assignment = {i: val for i, val in enumerate(args)}
            result = eval_term(term, algebra, var_assignment)
            table.append(list(args) + [result])
        
        operation = create_operation(name, arity, table)
        return self.add_operation(name, operation)
    
    def congruence_lattice(self, with_progress: Optional[Callable[[float, str], None]] = None) -> CongruenceLattice:
        """Get the congruence lattice for this algebra.
        
        Args:
            with_progress: Optional progress callback function
            
        Returns:
            CongruenceLattice object
        """
        if self._congruence_lattice is None:
            algebra = self.build()
            self._congruence_lattice = create_congruence_lattice(algebra)
            if with_progress is not None:
                self._congruence_lattice.with_progress_callback(with_progress)
        
        return self._congruence_lattice
    
    def analyze_congruences(self) -> Dict[str, Any]:
        """Analyze the congruence structure of this algebra.
        
        Returns:
            Dictionary with congruence analysis results
        """
        from .congruence import analyze_lattice
        lattice = self.congruence_lattice()
        return analyze_lattice(lattice)
    
    def principal_congruence(self, a: int, b: int) -> 'Partition':
        """Get the principal congruence θ(a, b) for this algebra.
        
        Args:
            a, b: Elements of the algebra
            
        Returns:
            Principal congruence partition
        """
        lattice = self.congruence_lattice()
        return lattice.principal_congruence(a, b)
    
    def evaluate_term(self, term_expr: str, variables: Dict[int, int]) -> int:
        """Evaluate a term expression in this algebra.
        
        Args:
            term_expr: String representation of the term
            variables: Dictionary mapping variable indices to values
            
        Returns:
            Result of term evaluation
        """
        arena = create_term_arena()
        term = parse_term(arena, term_expr)
        algebra = self.build()
        return eval_term(term, algebra, variables)
    
    def operation_from_term(self, term: Term, symbol: str) -> Operation:
        """Create an operation from a term.
        
        Args:
            term: Term object
            symbol: Symbol for the new operation
            
        Returns:
            New operation
        """
        from .terms import term_to_operation
        algebra = self.build()
        return term_to_operation(term, symbol, algebra)
    
    def operation_properties(self, op_name: str) -> Dict[str, Any]:
        """Get detailed properties of an operation.
        
        Args:
            op_name: Name of the operation
            
        Returns:
            Dictionary with operation properties
        """
        algebra = self.build()
        operation = algebra.operation_by_symbol(op_name)
        
        properties = {
            'name': op_name,
            'arity': operation.arity(),
            'type': operation.operation_type(),
        }
        
        # Check algebraic properties
        # Find operation index by symbol
        op_index = None
        for i, op in enumerate(algebra.operations()):
            if op.symbol == operation.symbol:
                op_index = i
                break
        
        if op_index is not None:
            properties['is_idempotent'] = algebra.is_idempotent(op_index)
            properties['is_associative'] = algebra.is_associative(op_index)
            properties['is_commutative'] = algebra.is_commutative(op_index)
        else:
            properties['is_idempotent'] = False
            properties['is_associative'] = False
            properties['is_commutative'] = False
        
        # Analyze operation table
        if operation.arity() == 1:
            values = [operation.value([i]) for i in range(self.size)]
            properties['values'] = values
            properties['is_bijective'] = len(set(values)) == self.size
            properties['fixed_points'] = [i for i, v in enumerate(values) if i == v]
        
        elif operation.arity() == 2:
            table = [[operation.value([i, j]) for j in range(self.size)] 
                    for i in range(self.size)]
            properties['table'] = table
            
            # Check for identity element
            identity = None
            for e in range(self.size):
                if all(operation.value([e, i]) == i and operation.value([i, e]) == i 
                       for i in range(self.size)):
                    identity = e
                    break
            properties['identity'] = identity
            
            # Check for inverses (if identity exists)
            if identity is not None:
                inverses = {}
                for a in range(self.size):
                    for b in range(self.size):
                        if (operation.value([a, b]) == identity and 
                            operation.value([b, a]) == identity):
                            inverses[a] = b
                            break
                properties['inverses'] = inverses
        
        return properties
    
    def is_idempotent_algebra(self) -> bool:
        """Check if all operations in the algebra are idempotent."""
        algebra = self.build()
        for i, _op in enumerate(algebra.operations()):
            if not algebra.is_idempotent(i):
                return False
        return True
    
    def is_associative_algebra(self) -> bool:
        """Check if all binary operations in the algebra are associative."""
        algebra = self.build()
        for i, _op in enumerate(algebra.operations()):
            if _op.arity() == 2 and not algebra.is_associative(i):
                return False
        return True
    
    def subalgebra_closure(self, generators: List[int], 
                          with_progress: Optional[Callable[[float, str], None]] = None) -> List[int]:
        """Compute the subalgebra generated by a set of elements.
        
        Args:
            generators: List of generator elements
            with_progress: Optional progress callback
            
        Returns:
            List of elements in the generated subalgebra
        """
        algebra = self.build()
        
        # Start with generators
        current = set(generators)
        previous = set()
        
        step = 0
        while current != previous:
            if with_progress:
                progress = min(step / 10, 0.9)  # Cap at 90% until done
                with_progress(progress, f"Computing closure step {step}")
            
            previous = current.copy()
            
            # Apply all operations to current elements
            for operation in algebra.operations():
                if operation.arity() == 0:  # Constant
                    current.add(operation.value([]))
                elif operation.arity() == 1:  # Unary
                    for element in list(current):
                        current.add(operation.value([element]))
                elif operation.arity() == 2:  # Binary
                    for a in list(current):
                        for b in list(current):
                            current.add(operation.value([a, b]))
                else:  # Higher arity
                    # Generate all combinations of current elements
                    for args in self._generate_combinations(list(current), operation.arity()):
                        current.add(operation.value(args))
            
            step += 1
            if step > 100:  # Safety limit
                warnings.warn("Subalgebra closure computation exceeded 100 steps")
                break
        
        if with_progress:
            with_progress(1.0, "Subalgebra closure complete")
        
        return sorted(list(current))
    
    def build(self) -> Algebra:
        """Build the algebra."""
        algebra = create_algebra(self.name, self.universe)
        
        for name, operation in self.operations.items():
            algebra.add_operation(name, operation)
        
        return algebra
    
    def _generate_combinations(self, elements: List[int], length: int) -> List[List[int]]:
        """Generate all combinations of elements with given length."""
        if length == 0:
            return [[]]
        
        if length == 1:
            return [[x] for x in elements]
        
        result = []
        for i, elem in enumerate(elements):
            for combo in self._generate_combinations(elements, length - 1):
                result.append([elem] + combo)
        
        return result

def create_group_operation(name: str, size: int, multiplication_table: List[List[int]]) -> Operation:
    """
    Create a group operation from a multiplication table.
    
    Args:
        name: Name of the operation
        size: Size of the group
        multiplication_table: 2D array representing the group multiplication
        
    Returns:
        Operation representing the group multiplication
    """
    if len(multiplication_table) != size:
        raise ValueError(f"Expected {size} rows, got {len(multiplication_table)}")
    
    for i, row in enumerate(multiplication_table):
        if len(row) != size:
            raise ValueError(f"Row {i} has {len(row)} columns, expected {size}")
        
        # Check that all values are in range
        for j, value in enumerate(row):
            if not 0 <= value < size:
                raise ValueError(f"Invalid value {value} at position ({i}, {j})")
    
    # Convert to the format expected by create_operation
    op_table = []
    for i in range(size):
        for j in range(size):
            op_table.append([i, j, multiplication_table[i][j]])
    
    return create_operation(name, 2, op_table)

def create_lattice_operations(name: str, size: int, meet_table: List[List[int]], join_table: List[List[int]]) -> Tuple[Operation, Operation]:
    """
    Create meet and join operations for a lattice.
    
    Args:
        name: Base name for the operations (will create name_meet and name_join)
        size: Size of the lattice
        meet_table: 2D array representing the meet operation
        join_table: 2D array representing the join operation
        
    Returns:
        Tuple of (meet_operation, join_operation)
    """
    meet_op = create_group_operation(f"{name}_meet", size, meet_table)
    join_op = create_group_operation(f"{name}_join", size, join_table)
    
    return meet_op, join_op

def create_boolean_algebra(size: int = 2) -> Algebra:
    """
    Create a Boolean algebra of given size (must be a power of 2).
    
    Args:
        size: Size of the Boolean algebra (default: 2)
        
    Returns:
        Boolean algebra with meet, join, and complement operations
    """
    if size < 2 or (size & (size - 1)) != 0:
        raise ValueError("Boolean algebra size must be a power of 2")
    
    # Create meet operation (AND)
    meet_table = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            meet_table[i][j] = i & j
    
    # Create join operation (OR)
    join_table = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            join_table[i][j] = i | j
    
    # Create complement operation (NOT)
    complement_values = []
    for i in range(size):
        complement_values.append((~i) & (size - 1))
    
    # Build the algebra
    builder = AlgebraBuilder("BooleanAlgebra", size)
    meet_op, join_op = create_lattice_operations("bool", size, meet_table, join_table)
    
    builder.add_operation("meet", meet_op)
    builder.add_operation("join", join_op)
    builder.add_unary_operation("complement", complement_values)
    
    return builder.build()

def create_cyclic_group(size: int) -> Algebra:
    """
    Create a cyclic group of given size.
    
    Args:
        size: Size of the cyclic group
        
    Returns:
        Cyclic group with multiplication operation
    """
    if size < 1:
        raise ValueError("Group size must be positive")
    
    # Create multiplication table for cyclic group
    multiplication_table = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            multiplication_table[i][j] = (i + j) % size
    
    # Build the algebra
    builder = AlgebraBuilder(f"CyclicGroup_{size}", size)
    mult_op = create_group_operation("multiply", size, multiplication_table)
    builder.add_operation("multiply", mult_op)
    
    return builder.build()

def create_symmetric_group(size: int) -> Algebra:
    """
    Create the symmetric group S_n.
    
    Args:
        size: Size of the symmetric group (n)
        
    Returns:
        Symmetric group with composition operation
    """
    if size < 1:
        raise ValueError("Group size must be positive")
    
    # For small sizes, we can create the full symmetric group
    if size > 6:
        raise ValueError("Symmetric groups larger than S_6 are not supported")
    
    # Generate all permutations
    from itertools import permutations
    perms = list(permutations(range(size)))
    perm_count = len(perms)
    
    # Create multiplication table
    multiplication_table = [[0] * perm_count for _ in range(perm_count)]
    for i, perm1 in enumerate(perms):
        for j, perm2 in enumerate(perms):
            # Compose permutations
            composed = tuple(perm1[perm2[k]] for k in range(size))
            multiplication_table[i][j] = perms.index(composed)
    
    # Build the algebra
    builder = AlgebraBuilder(f"SymmetricGroup_{size}", perm_count)
    comp_op = create_group_operation("compose", perm_count, multiplication_table)
    builder.add_operation("compose", comp_op)
    
    return builder.build()

def create_product_algebra(*factors, name: Optional[str] = None) -> 'ProductAlgebra':
    """
    Create the direct product of algebras using optimized Rust implementation.
    
    Args:
        *factors: Variable number of algebras to take the product of
        name: Optional name for the product algebra
        
    Alternative usage:
        create_product_algebra(factors=[alg1, alg2, alg3], name="ProductAlg")
        
    Returns:
        Direct product algebra with ProductAlgebra-specific methods
    """
    from . import rust_create_product_algebra
    
    # Handle different calling conventions
    if len(factors) == 1 and hasattr(factors[0], '__iter__') and not hasattr(factors[0], 'name'):
        # Called with create_product_algebra(factors=[...])
        factor_list = list(factors[0])
    else:
        # Called with create_product_algebra(alg1, alg2, ...)
        factor_list = list(factors)
    
    # Validate input
    if len(factor_list) < 1:
        raise ValueError("Product algebra must have at least one factor")
    
    # Generate default name if not provided
    if name is None:
        if len(factor_list) <= 3:
            name = "_x_".join(alg.name for alg in factor_list)
        else:
            name = f"Product_{len(factor_list)}_factors"
    
    # Call Rust implementation
    result = rust_create_product_algebra(name, factor_list)
    return result

def algebra_to_numpy(algebra: Algebra) -> Dict[str, 'np.ndarray']:
    """
    Convert algebra operations to NumPy arrays for efficient computation.
    
    Args:
        algebra: Algebra to convert
        
    Returns:
        Dictionary mapping operation names to NumPy arrays
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is required for algebra_to_numpy")
    
    result = {}
    
    for operation in algebra.operations():
        if operation.arity() == 0:  # Constant
            value = operation.value([])
            result[operation.symbol] = np.array(value)
        
        elif operation.arity() == 1:  # Unary
            values = []
            for i in range(algebra.cardinality):
                values.append(operation.value([i]))
            result[operation.symbol] = np.array(values)
        
        elif operation.arity() == 2:  # Binary
            table = np.zeros((algebra.cardinality, algebra.cardinality), dtype=int)
            for i in range(algebra.cardinality):
                for j in range(algebra.cardinality):
                    table[i, j] = operation.value([i, j])
            result[operation.symbol] = table
        
        else:  # Higher arity - store as sparse format for efficiency
            entries = []
            for args in _generate_combinations(list(range(algebra.cardinality)), operation.arity()):
                result_val = operation.value(args)
                entries.append((*args, result_val))
            result[operation.symbol] = np.array(entries)
    
    return result

def numpy_to_algebra(arrays: Dict[str, 'np.ndarray'], name: str) -> Algebra:
    """Convert NumPy arrays to an algebra.
    
    Args:
        arrays: Dictionary mapping operation names to NumPy arrays
        name: Name for the algebra
        
    Returns:
        Algebra object
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is required for numpy_to_algebra")
    
    # Determine universe size from first array
    first_array = next(iter(arrays.values()))
    if first_array.ndim == 0:  # Scalar
        universe_size = 1
    elif first_array.ndim == 1:  # 1D array
        universe_size = len(first_array)
    elif first_array.ndim == 2:  # 2D array
        universe_size = first_array.shape[0]
    else:
        raise ValueError("Cannot determine universe size from array shape")
    
    builder = AlgebraBuilder(name, universe_size)
    
    for op_name, array in arrays.items():
        if array.ndim == 0:  # Constant
            builder.add_constant(op_name, int(array))
        
        elif array.ndim == 1:  # Unary operation
            values = array.tolist()
            builder.add_unary_operation(op_name, values)
        
        elif array.ndim == 2:  # Binary operation
            table = array.tolist()
            builder.add_binary_operation(op_name, table)
        
        else:  # Higher arity - convert from sparse format
            entries = array.tolist()
            # Convert sparse format to operation table
            arity = len(entries[0]) - 1 if entries else 0
            table = []
            for entry in entries:
                args = entry[:-1]
                result = entry[-1]
                table.append([*args, result])
            
            operation = create_operation(op_name, arity, table)
            builder.add_operation(op_name, operation)
    
    return builder.build()

def batch_evaluate_operations(algebra: Algebra, operations: List[str], 
                             inputs: 'np.ndarray') -> 'np.ndarray':
    """Efficiently evaluate multiple operations on batch inputs.
    
    Args:
        algebra: Algebra to evaluate in
        operations: List of operation names to evaluate
        inputs: NumPy array of inputs with shape (batch_size, max_arity)
        
    Returns:
        NumPy array of results with shape (batch_size, len(operations))
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is required for batch_evaluate_operations")
    
    batch_size = inputs.shape[0]
    num_operations = len(operations)
    results = np.zeros((batch_size, num_operations), dtype=int)
    
    for i, op_name in enumerate(operations):
        operation = algebra.operation_by_symbol(op_name)
        arity = operation.arity()
        
        for j in range(batch_size):
            args = inputs[j, :arity].tolist()
            results[j, i] = operation.value(args)
    
    return results

def validate_algebra(algebra: Algebra) -> Tuple[bool, List[str]]:
    """Validate an algebra for consistency.
    
    Args:
        algebra: Algebra to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check universe size consistency
    universe_size = algebra.cardinality
    if universe_size == 0:
        errors.append("Algebra has empty universe")
    
    # Check operation consistency
    for operation in algebra.operations():
        # Check that operation values are in universe
        if operation.arity() == 0:  # Constant
            value = operation.value([])
            if not 0 <= value < universe_size:
                errors.append(f"Constant operation {operation.symbol} has value {value} outside universe")
        
        elif operation.arity() == 1:  # Unary
            for i in range(universe_size):
                try:
                    value = operation.value([i])
                    if not 0 <= value < universe_size:
                        errors.append(f"Unary operation {operation.symbol} maps {i} to {value} outside universe")
                except Exception as e:
                    errors.append(f"Unary operation {operation.symbol} fails on input {i}: {e}")
        
        elif operation.arity() == 2:  # Binary
            for i in range(universe_size):
                for j in range(universe_size):
                    try:
                        value = operation.value([i, j])
                        if not 0 <= value < universe_size:
                            errors.append(f"Binary operation {operation.symbol} maps ({i}, {j}) to {value} outside universe")
                    except Exception as e:
                        errors.append(f"Binary operation {operation.symbol} fails on inputs ({i}, {j}): {e}")
    
    return len(errors) == 0, errors

# Enhanced factory methods with progress reporting
def create_free_algebra(generators: List[str], operations: List[str], 
                       max_depth: int = 3) -> Algebra:
    """Create a free algebra with given generators and operations.
    
    Args:
        generators: List of generator symbols
        operations: List of operation symbols
        max_depth: Maximum depth of terms to generate
        
    Returns:
        Free algebra
    """
    # This is a simplified implementation
    # A full free algebra would be infinite, so we limit by depth
    
    # Generate all terms up to max_depth
    from .terms import random_term
    
    arena = create_term_arena()
    terms = []
    
    # Add generators as terms
    for i, gen in enumerate(generators):
        term = arena.make_variable(i)
        terms.append(term)
    
    # Generate compound terms
    for depth in range(1, max_depth + 1):
        for _ in range(len(operations) * 2):  # Generate some terms at each depth
            term = random_term(depth, operations, len(generators))
            terms.append(term)
    
    # Create algebra with these terms as elements
    size = len(terms)
    builder = AlgebraBuilder("FreeAlgebra", size)
    
    # Add operations that act on terms
    for op_name in operations:
        # Create operation that applies the operation symbol to terms
        # This is a simplified implementation
        values = list(range(size))  # Identity operation for now
        builder.add_unary_operation(op_name, values)
    
    return builder.build()

def create_quotient_algebra(algebra: Algebra, congruence: 'Partition', name: Optional[str] = None, validate: bool = False) -> Algebra:
    """Create a quotient algebra by a congruence using optimized Rust implementation.
    
    Args:
        algebra: Original algebra
        congruence: Congruence partition
        name: Optional name for the quotient algebra (defaults to "{algebra.name}_quotient")
        validate: Whether to validate that the partition is actually a congruence (default: False)
        
    Returns:
        Quotient algebra with efficient operations
    """
    from . import rust_create_quotient_algebra
    
    # Validate input parameters
    if algebra is None:
        raise ValueError("Algebra cannot be None")
    if congruence is None:
        raise ValueError("Congruence cannot be None")
    
    # Generate default name if not provided
    if name is None:
        name = f"{algebra.name}_quotient"
    
    # Call optimized Rust implementation with validation parameter
    result = rust_create_quotient_algebra(name, algebra, congruence, validate)
    return result

def _compute_subalgebra_closure(algebra: Algebra, generators: List[int], 
                               with_progress: Optional[Callable[[float, str], None]] = None) -> List[int]:
    """Compute the subalgebra generated by a set of elements.
    
    Args:
        algebra: The algebra to compute closure in
        generators: List of generator elements
        with_progress: Optional progress callback
        
    Returns:
        List of elements in the generated subalgebra
    """
    # Start with generators
    current = set(generators)
    previous = set()
    
    step = 0
    while current != previous:
        if with_progress:
            progress = min(step / 10, 0.9)  # Cap at 90% until done
            with_progress(progress, f"Computing closure step {step}")
        
        previous = current.copy()
        
        # Apply all operations to current elements
        for operation in algebra.operations():
            if operation.arity() == 0:  # Constant
                current.add(operation.value([]))
            elif operation.arity() == 1:  # Unary
                for element in list(current):
                    current.add(operation.value([element]))
            elif operation.arity() == 2:  # Binary
                for a in list(current):
                    for b in list(current):
                        current.add(operation.value([a, b]))
            else:  # Higher arity
                # Generate all combinations of current elements
                for args in _generate_combinations(list(current), operation.arity()):
                    current.add(operation.value(args))
        
        step += 1
        if step > 100:  # Safety limit
            warnings.warn("Subalgebra closure computation exceeded 100 steps")
            break
    
    if with_progress:
        with_progress(1.0, "Subalgebra closure complete")
    
    return sorted(list(current))

def create_subalgebra(algebra: Algebra, generators: List[int], 
                     with_progress: Optional[Callable[[float, str], None]] = None) -> Algebra:
    """Create a subalgebra generated by a set of elements.
    
    Args:
        algebra: Original algebra
        generators: List of generator elements
        with_progress: Optional progress callback
        
    Returns:
        Subalgebra
    """
    # Compute subalgebra closure using the helper function
    sub_elements = _compute_subalgebra_closure(algebra, generators, with_progress)
    
    # Create mapping from subalgebra elements to indices
    element_to_index = {elem: i for i, elem in enumerate(sub_elements)}
    sub_size = len(sub_elements)
    
    # Create new algebra with subalgebra elements
    sub_builder = AlgebraBuilder(f"{algebra.name}_sub", sub_size)
    
    # Define operations on subalgebra
    for operation in algebra.operations():
        if operation.arity() == 0:  # Constant
            value = operation.value([])
            if value in element_to_index:
                sub_builder.add_constant(operation.symbol, element_to_index[value])
        
        elif operation.arity() == 1:  # Unary
            values = []
            for i in range(sub_size):
                element = sub_elements[i]
                result = operation.value([element])
                if result in element_to_index:
                    values.append(element_to_index[result])
                else:
                    # Result not in subalgebra - use identity
                    values.append(i)
            sub_builder.add_unary_operation(operation.symbol, values)
        
        elif operation.arity() == 2:  # Binary
            table = [[0] * sub_size for _ in range(sub_size)]
            for i in range(sub_size):
                for j in range(sub_size):
                    elem1 = sub_elements[i]
                    elem2 = sub_elements[j]
                    result = operation.value([elem1, elem2])
                    if result in element_to_index:
                        table[i][j] = element_to_index[result]
                    else:
                        # Result not in subalgebra - use first element
                        table[i][j] = 0
            sub_builder.add_binary_operation(operation.symbol, table)
    
    return sub_builder.build()

def _generate_combinations(elements: List[int], length: int) -> List[List[int]]:
    """Generate all combinations of elements with given length."""
    if length == 0:
        return [[]]
    
    if length == 1:
        return [[x] for x in elements]
    
    result = []
    for i, elem in enumerate(elements):
        for combo in _generate_combinations(elements, length - 1):
            result.append([elem] + combo)
    
    return result

