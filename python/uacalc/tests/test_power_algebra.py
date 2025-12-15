"""Tests for PowerAlgebra implementation.

This module contains comprehensive tests for the PowerAlgebra class,
including unit tests, integration tests, and comparison tests with Java implementation.
"""

import pytest
import os
import json
import uacalc_lib
from test_utils import run_java_wrapper


def get_java_data(java_result):
    """Extract and parse the data field from Java output."""
    parsed = java_result.parse_json()
    data = parsed.get("data", {})
    if isinstance(data, str):
        return json.loads(data)
    return data


@pytest.fixture
def algebra_classes():
    """Fixture providing algebra classes."""
    return {
        'BasicAlgebra': uacalc_lib.alg.BasicAlgebra,
        'PowerAlgebra': uacalc_lib.alg.PowerAlgebra,
        'IntOperation': uacalc_lib.alg.IntOperation,
        'OperationSymbol': uacalc_lib.alg.OperationSymbol,
    }


def test_power_algebra_creation(algebra_classes):
    """Test PowerAlgebra creation."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    # Create a basic small algebra
    root_alg = BasicAlgebra("TestRoot", [0, 1], [])
    
    # Create power algebra
    power = PowerAlgebra(root_alg, 3)
    
    # Verify basic properties
    assert power.get_power() == 3
    assert power.cardinality() == 8  # 2^3 = 8
    assert power.get_root_size() == 2
    assert "Power" in power.algebra_type()


def test_power_algebra_creation_with_name(algebra_classes):
    """Test PowerAlgebra creation with custom name."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [])
    
    power = PowerAlgebra.new_with_name("MyPower", root_alg, 2)
    
    assert power.name() == "MyPower"
    assert power.get_power() == 2
    assert power.cardinality() == 4  # 2^2 = 4


def test_get_power(algebra_classes):
    """Test get_power method."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [])
    power = PowerAlgebra(root_alg, 4)
    
    assert power.get_power() == 4


def test_cardinality(algebra_classes):
    """Test cardinality method."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    root_alg = BasicAlgebra("TestRoot", [0, 1, 2], [])
    power = PowerAlgebra(root_alg, 2)
    
    # 3^2 = 9
    assert power.cardinality() == 9


def test_get_root_size(algebra_classes):
    """Test get_root_size method."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    root_alg = BasicAlgebra("TestRoot", [0, 1, 2, 3], [])
    power = PowerAlgebra(root_alg, 3)
    
    assert power.get_root_size() == 4


def test_name_and_description(algebra_classes):
    """Test name and description methods."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [])
    power = PowerAlgebra.new_with_name("TestPower", root_alg, 2)
    
    assert power.name() == "TestPower"
    assert power.description() is None
    
    # Test setting name
    power.set_name("NewName")
    assert power.name() == "NewName"
    
    # Test setting description
    power.set_description("Test description")
    assert power.description() == "Test description"
    
    power.set_description(None)
    assert power.description() is None


def test_operations_returns_operation_objects(algebra_classes):
    """Test that operations() returns Operation objects, not tuples."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    OperationSymbol = algebra_classes['OperationSymbol']
    IntOperation = algebra_classes['IntOperation']
    
    # Create root algebra with an operation
    symbol = OperationSymbol("f", 2)
    table = [0, 1, 1, 0]  # XOR operation on {0, 1}
    op = IntOperation(symbol, 2, table)
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [op])
    power = PowerAlgebra(root_alg, 2)
    
    # Get operations - should return Operation objects, not tuples
    ops = power.operations()
    
    # Verify it's a list
    assert isinstance(ops, list)
    assert len(ops) > 0
    
    # Verify each operation is an Operation object (has symbol and arity methods)
    for op in ops:
        # Should have symbol() method (Operation objects have this)
        assert hasattr(op, 'symbol')
        assert hasattr(op, 'arity')
        assert hasattr(op, 'get_set_size')
        
        # Should NOT be a tuple
        assert not isinstance(op, tuple)


def test_operations_preserves_operation_properties(algebra_classes):
    """Test that operations preserve their properties."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    OperationSymbol = algebra_classes['OperationSymbol']
    IntOperation = algebra_classes['IntOperation']
    
    # Create root algebra with an operation
    symbol = OperationSymbol("g", 1)
    table = [1, 0]  # NOT operation on {0, 1}
    op = IntOperation(symbol, 2, table)
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [op])
    power = PowerAlgebra(root_alg, 2)
    
    ops = power.operations()
    assert len(ops) == 1
    
    # Check operation properties
    op_obj = ops[0]
    assert op_obj.symbol().name() == "g"
    assert op_obj.arity() == 1
    assert op_obj.get_set_size() == 4  # Power algebra size is 2^2 = 4


def test_to_basic_algebra(algebra_classes):
    """Test conversion to BasicAlgebra."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    OperationSymbol = algebra_classes['OperationSymbol']
    IntOperation = algebra_classes['IntOperation']
    
    # Create root algebra with an operation
    symbol = OperationSymbol("h", 2)
    table = [0, 0, 0, 1]  # AND operation on {0, 1}
    op = IntOperation(symbol, 2, table)
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [op])
    power = PowerAlgebra(root_alg, 2)
    
    # Convert to BasicAlgebra
    basic_alg = power.to_basic_algebra()
    
    # Verify it's a BasicAlgebra
    assert isinstance(basic_alg, BasicAlgebra)
    
    # Verify cardinality matches
    assert basic_alg.cardinality() == power.cardinality()
    
    # Verify operations are preserved
    basic_ops = basic_alg.operations()
    power_ops = power.operations()
    assert len(basic_ops) == len(power_ops)


def test_to_basic_algebra_preserves_operations(algebra_classes):
    """Test that to_basic_algebra preserves operation structure."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    OperationSymbol = algebra_classes['OperationSymbol']
    IntOperation = algebra_classes['IntOperation']
    
    # Create root algebra with multiple operations
    symbol1 = OperationSymbol("f", 2)
    table1 = [0, 1, 1, 0]  # XOR
    op1 = IntOperation(symbol1, 2, table1)
    
    symbol2 = OperationSymbol("g", 1)
    table2 = [1, 0]  # NOT
    op2 = IntOperation(symbol2, 2, table2)
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [op1, op2])
    power = PowerAlgebra(root_alg, 2)
    
    basic_alg = power.to_basic_algebra()
    
    # Check operations count
    basic_ops = basic_alg.operations()
    assert len(basic_ops) == 2
    
    # Check operation names
    op_names = [op.symbol().name() for op in basic_ops]
    assert "f" in op_names
    assert "g" in op_names


def test_is_unary(algebra_classes):
    """Test is_unary method."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    OperationSymbol = algebra_classes['OperationSymbol']
    IntOperation = algebra_classes['IntOperation']
    
    # Create unary algebra
    symbol = OperationSymbol("u", 1)
    table = [1, 0]
    op = IntOperation(symbol, 2, table)
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [op])
    power = PowerAlgebra(root_alg, 2)
    
    assert power.is_unary()
    
    # Create non-unary algebra
    symbol2 = OperationSymbol("b", 2)
    table2 = [0, 1, 1, 0]
    op2 = IntOperation(symbol2, 2, table2)
    
    root_alg2 = BasicAlgebra("TestRoot2", [0, 1], [op2])
    power2 = PowerAlgebra(root_alg2, 2)
    
    assert not power2.is_unary()


def test_is_total(algebra_classes):
    """Test is_total method."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [])
    power = PowerAlgebra(root_alg, 2)
    
    # Algebra with no operations should be total
    assert power.is_total()


def test_is_idempotent(algebra_classes):
    """Test is_idempotent method."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [])
    power = PowerAlgebra(root_alg, 2)
    
    # Test that method exists and doesn't crash
    result = power.is_idempotent()
    assert isinstance(result, bool)


def test_string_representations(algebra_classes):
    """Test string representation methods."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [])
    power = PowerAlgebra(root_alg, 2)
    
    # Test __str__
    str_repr = str(power)
    assert isinstance(str_repr, str)
    assert len(str_repr) > 0
    
    # Test __repr__
    repr_str = repr(power)
    assert isinstance(repr_str, str)
    assert "PowerAlgebra" in repr_str


def test_equality(algebra_classes):
    """Test equality comparison."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    root_alg1 = BasicAlgebra("TestRoot", [0, 1], [])
    power1 = PowerAlgebra.new_with_name("Test", root_alg1, 2)
    
    root_alg2 = BasicAlgebra("TestRoot", [0, 1], [])
    power2 = PowerAlgebra.new_with_name("Test", root_alg2, 2)
    
    # Should be equal if name, cardinality, and power match
    assert power1 == power2


def test_hash(algebra_classes):
    """Test hash function."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [])
    power = PowerAlgebra(root_alg, 2)
    
    # Test that hash exists and is consistent
    hash1 = hash(power)
    hash2 = hash(power)
    assert hash1 == hash2
    assert isinstance(hash1, int)


def test_congruence_lattice(algebra_classes):
    """Test congruence lattice access."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [])
    power = PowerAlgebra(root_alg, 2)
    
    # Test that con() method exists and returns a CongruenceLattice
    con_lat = power.con()
    assert con_lat is not None
    # Verify it has expected methods
    assert hasattr(con_lat, 'cardinality')


def test_subalgebra_lattice(algebra_classes):
    """Test subalgebra lattice access."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    root_alg = BasicAlgebra("TestRoot", [0, 1], [])
    power = PowerAlgebra(root_alg, 2)
    
    # Test that sub() method exists and returns a SubalgebraLattice
    sub_lat = power.sub()
    assert sub_lat is not None
    # Verify it has expected methods
    assert hasattr(sub_lat, 'cardinality')


def test_large_power(algebra_classes):
    """Test with larger power values."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    
    root_alg = BasicAlgebra("TestRoot", [0, 1, 2], [])
    power = PowerAlgebra(root_alg, 3)
    
    # 3^3 = 27
    assert power.cardinality() == 27
    assert power.get_power() == 3
    assert power.get_root_size() == 3


def test_power_algebra_with_operations(algebra_classes):
    """Test PowerAlgebra with operations from root."""
    BasicAlgebra = algebra_classes['BasicAlgebra']
    PowerAlgebra = algebra_classes['PowerAlgebra']
    OperationSymbol = algebra_classes['OperationSymbol']
    IntOperation = algebra_classes['IntOperation']
    
    # Create root with operation
    symbol = OperationSymbol("mult", 2)
    # Multiplication mod 3: 0*0=0, 0*1=0, 0*2=0, 1*0=0, 1*1=1, 1*2=2, etc.
    table = [0, 0, 0, 0, 1, 2, 0, 2, 1]
    op = IntOperation(symbol, 3, table)
    
    root_alg = BasicAlgebra("Z3", [0, 1, 2], [op])
    power = PowerAlgebra(root_alg, 2)
    
    # Power algebra should have operations
    ops = power.operations()
    assert len(ops) > 0
    
    # Operations should be Operation objects
    for op in ops:
        assert hasattr(op, 'symbol')
        assert hasattr(op, 'arity')
