"""
High-level algebra utilities for UACalc.

This module provides convenient Python interfaces for creating and manipulating
algebras, with integration to Python's scientific computing ecosystem.
"""

from typing import List, Tuple, Optional, Dict, Any, Union
import numpy as np

from . import Algebra, Operation, create_algebra, create_operation

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
    
    def build(self) -> Algebra:
        """Build the algebra."""
        algebra = create_algebra(self.name, self.universe)
        
        for name, operation in self.operations.items():
            algebra.add_operation(name, operation)
        
        return algebra

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

def create_product_algebra(algebra1: Algebra, algebra2: Algebra) -> Algebra:
    """
    Create the direct product of two algebras.
    
    Args:
        algebra1: First algebra
        algebra2: Second algebra
        
    Returns:
        Direct product algebra
    """
    size1 = algebra1.cardinality()
    size2 = algebra2.cardinality()
    product_size = size1 * size2
    
    # Create mapping from product elements to pairs
    def to_pair(element: int) -> Tuple[int, int]:
        return (element // size2, element % size2)
    
    def from_pair(pair: Tuple[int, int]) -> int:
        return pair[0] * size2 + pair[1]
    
    # Build the product algebra
    builder = AlgebraBuilder(f"{algebra1.name}_x_{algebra2.name}", product_size)
    
    # For each operation in algebra1, create corresponding operation in product
    for i, op1 in enumerate(algebra1.operations()):
        if op1.arity() == 0:  # Constant
            # Map constant to product
            value1 = op1.value([])
            for j, op2 in enumerate(algebra2.operations()):
                if op2.arity() == 0:
                    value2 = op2.value([])
                    product_value = from_pair((value1, value2))
                    builder.add_constant(f"{op1.symbol}_{op2.symbol}", product_value)
        
        elif op1.arity() == 1:  # Unary
            # Create unary operation that applies to first component
            values = []
            for element in range(product_size):
                a, b = to_pair(element)
                result_a = op1.value([a])
                values.append(from_pair((result_a, b)))
            builder.add_unary_operation(f"{op1.symbol}_1", values)
        
        elif op1.arity() == 2:  # Binary
            # Create binary operation that applies to first component
            table = [[0] * product_size for _ in range(product_size)]
            for element1 in range(product_size):
                for element2 in range(product_size):
                    a1, b1 = to_pair(element1)
                    a2, b2 = to_pair(element2)
                    result_a = op1.value([a1, a2])
                    table[element1][element2] = from_pair((result_a, b1))
            builder.add_binary_operation(f"{op1.symbol}_1", table)
    
    # Similarly for operations in algebra2
    for i, op2 in enumerate(algebra2.operations()):
        if op2.arity() == 0:  # Constant
            value2 = op2.value([])
            for j, op1 in enumerate(algebra1.operations()):
                if op1.arity() == 0:
                    value1 = op1.value([])
                    product_value = from_pair((value1, value2))
                    builder.add_constant(f"{op1.symbol}_{op2.symbol}", product_value)
        
        elif op2.arity() == 1:  # Unary
            values = []
            for element in range(product_size):
                a, b = to_pair(element)
                result_b = op2.value([b])
                values.append(from_pair((a, result_b)))
            builder.add_unary_operation(f"{op2.symbol}_2", values)
        
        elif op2.arity() == 2:  # Binary
            table = [[0] * product_size for _ in range(product_size)]
            for element1 in range(product_size):
                for element2 in range(product_size):
                    a1, b1 = to_pair(element1)
                    a2, b2 = to_pair(element2)
                    result_b = op2.value([b1, b2])
                    table[element1][element2] = from_pair((a1, result_b))
            builder.add_binary_operation(f"{op2.symbol}_2", table)
    
    return builder.build()

def algebra_to_numpy(algebra: Algebra) -> Dict[str, np.ndarray]:
    """
    Convert algebra operations to NumPy arrays for efficient computation.
    
    Args:
        algebra: Algebra to convert
        
    Returns:
        Dictionary mapping operation names to NumPy arrays
    """
    result = {}
    
    for operation in algebra.operations():
        if operation.arity() == 0:  # Constant
            value = operation.value([])
            result[operation.symbol] = np.array(value)
        
        elif operation.arity() == 1:  # Unary
            values = []
            for i in range(algebra.cardinality()):
                values.append(operation.value([i]))
            result[operation.symbol] = np.array(values)
        
        elif operation.arity() == 2:  # Binary
            table = np.zeros((algebra.cardinality(), algebra.cardinality()), dtype=int)
            for i in range(algebra.cardinality()):
                for j in range(algebra.cardinality()):
                    table[i, j] = operation.value([i, j])
            result[operation.symbol] = table
        
        else:  # Higher arity - store as list of tuples
            # This is less efficient but handles arbitrary arity
            entries = []
            for args in _generate_combinations(list(range(algebra.cardinality())), operation.arity()):
                result_val = operation.value(args)
                entries.append((*args, result_val))
            result[operation.symbol] = np.array(entries)
    
    return result

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

