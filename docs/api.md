# UACalc API Documentation

This document describes the Rust and Python APIs for the UACalc implementation, including migration guidance from the original Java version.

## Overview

The UACalc Rust/Python implementation provides a modern, high-performance alternative to the original Java UACalc while maintaining API compatibility and file format support.

## Core Concepts

### Algebra
An algebra consists of:
- A **universe** (set of elements)
- A collection of **operations** defined on the universe
- Optional **properties** and **metadata**

### Operation
An operation is a function that takes a fixed number of arguments (its **arity**) and returns a single value from the universe.

### Partition
A partition of a set divides it into disjoint subsets called **blocks**. Partitions are fundamental for congruence relations.

### Binary Relation
A binary relation on a set is a subset of the Cartesian product of the set with itself.

## Rust API

### Core Traits

#### `Algebra`
```rust
pub trait Algebra {
    fn universe(&self) -> &[usize];
    fn cardinality(&self) -> usize;
    fn operations(&self) -> &[Box<dyn Operation>];
    fn operation(&self, index: usize) -> UACalcResult<&dyn Operation>;
    fn operation_by_symbol(&self, symbol: &str) -> UACalcResult<&dyn Operation>;
    fn is_finite(&self) -> bool;
    fn name(&self) -> &str;
}
```

#### `SmallAlgebra`
```rust
pub trait SmallAlgebra: Algebra {
    fn max_arity(&self) -> usize;
    fn is_idempotent(&self, op_index: usize) -> UACalcResult<bool>;
    fn is_associative(&self, op_index: usize) -> UACalcResult<bool>;
    fn is_commutative(&self, op_index: usize) -> UACalcResult<bool>;
    fn subalgebra(&self, generators: &[usize]) -> UACalcResult<BasicAlgebra>;
}
```

#### `Operation`
```rust
pub trait Operation: fmt::Debug + Send + Sync {
    fn arity(&self) -> usize;
    fn symbol(&self) -> &OperationSymbol;
    fn value(&self, args: &[usize]) -> UACalcResult<usize>;
    fn operation_type(&self) -> OperationType;
}
```

#### `Partition`
```rust
pub trait Partition: Clone + Send + Sync {
    fn size(&self) -> usize;
    fn num_blocks(&self) -> usize;
    fn block(&self, element: usize) -> UACalcResult<Vec<usize>>;
    fn representative(&self, element: usize) -> UACalcResult<usize>;
    fn same_block(&self, a: usize, b: usize) -> UACalcResult<bool>;
    fn blocks(&self) -> Vec<Vec<usize>>;
    fn join(&self, other: &dyn Partition) -> UACalcResult<Box<dyn Partition>>;
    fn meet(&self, other: &dyn Partition) -> UACalcResult<Box<dyn Partition>>;
}
```

### Concrete Implementations

#### `BasicAlgebra`
```rust
pub struct BasicAlgebra {
    name: String,
    universe: Vec<usize>,
    operations: Vec<Box<dyn Operation>>,
    operation_symbols: HashMap<String, usize>,
}

impl BasicAlgebra {
    pub fn new(name: String, universe: Vec<usize>) -> Self;
    pub fn add_operation(&mut self, symbol: String, operation: Box<dyn Operation>) -> UACalcResult<()>;
    pub fn from_operations(name: String, universe: Vec<usize>, operations: Vec<(String, Box<dyn Operation>)>) -> UACalcResult<Self>;
}
```

#### `TableOperation`
```rust
pub struct TableOperation {
    symbol: OperationSymbol,
    table: Vec<Vec<usize>>,
}

impl TableOperation {
    pub fn new(symbol: OperationSymbol, table: Vec<Vec<usize>>) -> UACalcResult<Self>;
    pub fn constant(name: String, value: usize) -> Self;
    pub fn unary<F>(name: String, size: usize, f: F) -> Self where F: Fn(usize) -> usize;
    pub fn binary<F>(name: String, size: usize, f: F) -> Self where F: Fn(usize, usize) -> usize;
}
```

#### `BasicPartition`
```rust
pub struct BasicPartition {
    size: usize,
    parent: Vec<usize>,
    rank: Vec<usize>,
    block_cache: Option<Vec<Vec<usize>>>,
}

impl BasicPartition {
    pub fn new(size: usize) -> Self;
    pub fn from_blocks(size: usize, blocks: Vec<Vec<usize>>) -> UACalcResult<Self>;
    pub fn union(&mut self, x: usize, y: usize) -> UACalcResult<()>;
}
```

## Python API

### Core Classes

#### `Algebra`
```python
class Algebra:
    def __init__(self, name: str, universe: List[int])
    def add_operation(self, symbol: str, operation: Operation) -> None
    def operation(self, index: int) -> Operation
    def operation_by_symbol(self, symbol: str) -> Operation
    def cardinality(self) -> int
    def is_finite(self) -> bool
    def max_arity(self) -> int
    def is_idempotent(self, op_index: int) -> bool
    def is_associative(self, op_index: int) -> bool
    def is_commutative(self, op_index: int) -> bool
    def subalgebra(self, generators: List[int]) -> Algebra
    
    # Properties
    name: str
    universe: List[int]
    operations: List[Operation]
```

#### `Operation`
```python
class Operation:
    def value(self, args: List[int]) -> int
    def arity(self) -> int
    def symbol(self) -> str
    def operation_type(self) -> str
```

#### `Partition`
```python
class Partition:
    def __init__(self, size: int)
    def union(self, x: int, y: int) -> None
    def same_block(self, a: int, b: int) -> bool
    def blocks(self) -> List[List[int]]
    def join(self, other: Partition) -> Partition
    def meet(self, other: Partition) -> Partition
    def is_finer_than(self, other: Partition) -> bool
    def is_coarser_than(self, other: Partition) -> bool
    
    # Properties
    size: int
    num_blocks: int
```

#### `BinaryRelation`
```python
class BinaryRelation:
    def __init__(self, size: int)
    def contains(self, a: int, b: int) -> bool
    def add(self, a: int, b: int) -> None
    def remove(self, a: int, b: int) -> None
    def reflexive_closure(self) -> BinaryRelation
    def symmetric_closure(self) -> BinaryRelation
    def transitive_closure(self) -> BinaryRelation
    def equivalence_closure(self) -> BinaryRelation
    def is_reflexive(self) -> bool
    def is_symmetric(self) -> bool
    def is_transitive(self) -> bool
    def is_equivalence(self) -> bool
```

### Factory Functions

```python
def create_algebra(name: str, universe: List[int]) -> Algebra
def create_operation(name: str, arity: int, table: List[List[int]]) -> Operation
def create_partition(size: int) -> Partition
def create_binary_relation(size: int) -> BinaryRelation
```

### Utility Functions

```python
def load_algebra(file_path: Union[str, Path]) -> Algebra
def save_algebra(algebra: Algebra, file_path: Union[str, Path]) -> None
def create_boolean_algebra(size: int = 2) -> Algebra
def create_cyclic_group(size: int) -> Algebra
def create_symmetric_group(size: int) -> Algebra
def create_product_algebra(algebra1: Algebra, algebra2: Algebra) -> Algebra
def algebra_to_numpy(algebra: Algebra) -> Dict[str, np.ndarray]
```

## Migration from Java UACalc

### API Mapping

| Java | Rust | Python |
|------|------|--------|
| `Algebra.getUniverse()` | `algebra.universe()` | `algebra.universe` |
| `Algebra.getCardinality()` | `algebra.cardinality()` | `algebra.cardinality` |
| `Algebra.getOperation(int)` | `algebra.operation(index)` | `algebra.operation(index)` |
| `Operation.getValue(int[])` | `operation.value(&args)` | `operation.value(args)` |
| `Operation.getArity()` | `operation.arity()` | `operation.arity()` |
| `Partition.getBlocks()` | `partition.blocks()` | `partition.blocks()` |

### Key Differences

1. **Error Handling**: Rust uses `Result<T, E>` instead of exceptions
2. **Memory Management**: Rust provides zero-cost abstractions
3. **Type Safety**: Rust enforces compile-time type checking
4. **Performance**: Rust provides near-native performance

### Migration Steps

1. **Load Existing Data**:
   ```python
   # Java: AlgebraIO.readAlgebra(file)
   # Python: uacalc.load_algebra(file)
   algebra = uacalc.load_algebra("existing.ua")
   ```

2. **Update API Calls**:
   ```python
   # Java: algebra.getOperation(0).getValue(new int[]{1, 2})
   # Python: algebra.operation(0).value([1, 2])
   result = algebra.operation(0).value([1, 2])
   ```

3. **Handle Errors**:
   ```python
   # Java: try-catch blocks
   # Python: try-except blocks
   try:
       result = operation.value(args)
   except ValueError as e:
       print(f"Error: {e}")
   ```

4. **Export for Compatibility**:
   ```python
   # Save in Java-compatible format
   uacalc.save_algebra(algebra, "compatible.ua")
   ```

## Performance Considerations

### Rust Optimizations

1. **Zero-Cost Abstractions**: Traits provide compile-time polymorphism
2. **Memory Safety**: No garbage collection overhead
3. **SIMD Support**: Automatic vectorization where possible
4. **Cache Locality**: Optimized data structures

### Python Performance

1. **Extension Module**: Core operations in Rust
2. **NumPy Integration**: Efficient array operations
3. **Type Hints**: Better optimization opportunities
4. **Memory Views**: Zero-copy data sharing

### Benchmarking

```python
import time
import uacalc

# Benchmark operation evaluation
algebra = uacalc.create_algebra("Benchmark", list(range(10)))
operation = uacalc.create_operation("test", 2, [[(i + j) % 10 for j in range(10)] for i in range(10)])

start_time = time.time()
for _ in range(100000):
    operation.value([5, 3])
end_time = time.time()

print(f"Operations per second: {100000 / (end_time - start_time):.0f}")
```

## Best Practices

### Rust Development

1. **Use Traits**: Prefer trait objects over concrete types
2. **Error Handling**: Use `Result` types consistently
3. **Memory Management**: Leverage Rust's ownership system
4. **Testing**: Write comprehensive unit and integration tests

### Python Development

1. **Type Hints**: Use type annotations for better IDE support
2. **Error Handling**: Use specific exception types
3. **Documentation**: Include docstrings for all public APIs
4. **Testing**: Use pytest for comprehensive testing

### Performance Optimization

1. **Profile First**: Use profiling tools to identify bottlenecks
2. **Batch Operations**: Group operations when possible
3. **Memory Layout**: Consider cache-friendly data structures
4. **Algorithm Choice**: Select appropriate algorithms for your use case

## Examples

### Creating a Group

```python
import uacalc

# Create cyclic group Z_5
algebra = uacalc.create_cyclic_group(5)

# Verify group properties
operation = algebra.operation_by_symbol("multiply")
assert operation.value([1, 2]) == 3  # 1 + 2 = 3 (mod 5)
assert operation.value([2, 3]) == 0  # 2 + 3 = 0 (mod 5)
```

### Working with Partitions

```python
import uacalc

# Create partition
partition = uacalc.create_partition(4)
partition.union(0, 1)
partition.union(2, 3)

# Check properties
assert partition.num_blocks == 2
assert partition.same_block(0, 1)
assert not partition.same_block(0, 2)
```

### Loading and Saving

```python
import uacalc

# Load existing algebra
algebra = uacalc.load_algebra("resources/algebras/cyclic3.ua")

# Modify algebra
# ... make changes ...

# Save modified algebra
uacalc.save_algebra(algebra, "modified_cyclic3.ua")
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the Rust extension is built
2. **Type Errors**: Check that arguments match expected types
3. **Performance Issues**: Use release builds for production
4. **Memory Issues**: Monitor memory usage with large algebras

### Debugging

1. **Rust**: Use `cargo test` and `cargo bench`
2. **Python**: Use `pytest` with verbose output
3. **Integration**: Test with existing `.ua` files
4. **Performance**: Profile with appropriate tools

## Future Extensions

The API is designed to be extensible. Planned additions include:

1. **Parallel Processing**: Multi-threaded algorithms
2. **GPU Acceleration**: CUDA/OpenCL support
3. **Web Assembly**: Browser-based computation
4. **Distributed Computing**: Cluster support
5. **Advanced Algorithms**: More sophisticated algebra algorithms

