# Task 12: Translate `Operation`

**Java File:** `org/uacalc/alg/op/Operation.java`  
**Package:** `org.uacalc.alg.op`  
**Rust Module:** `alg::op::Operation`  
**Dependencies:** 1 (1 non-UI/example)  
**Estimated Public Methods:** 17

## Description
Translate the Java interface `org.uacalc.alg.op.Operation` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Type**: Interface (17 public methods)
- **Extends**: `Comparable<Operation>`
- **Purpose**: Foundational interface defining operations in universal algebra

### Method Analysis
**Core Properties (3 methods):**
- `arity() -> int` - Returns the arity (number of operands) of the operation
- `getSetSize() -> int` - Returns the size of the set the operation acts on
- `symbol() -> OperationSymbol` - Returns the operation symbol

**Operation Evaluation (4 methods):**
- `valueAt(List args) -> Object` - Element version of operation evaluation
- `valueAt(int[][] args) -> int[]` - Fast product operation evaluation
- `intValueAt(int[] args) -> int` - Integer version of operation evaluation
- `intValueAt(int arg) -> int` - Fast table access using Horner encoding

**Table Management (4 methods):**
- `makeTable() -> void` - Creates operation table for faster evaluation
- `getTable() -> int[]` - Gets the operation table or null if not exists
- `getTable(boolean makeTable) -> int[]` - Gets table, creating if requested
- `isTableBased() -> boolean` - Checks if operation is table-based

**Property Checks (6 methods):**
- `isIdempotent() -> boolean` - Checks if f(x,x,...,x) = x
- `isAssociative() -> boolean` - Checks if operation is binary and associative
- `isCommutative() -> boolean` - Checks if operation is binary and commutative
- `isTotallySymmetric() -> boolean` - Checks if invariant under all variable permutations
- `isMaltsev() -> boolean` - Checks if ternary operation is Maltsev
- `isTotal() -> boolean` - Checks if operation is total (only OperationWithDefaultValue can fail)

## Dependencies Analysis

### Direct Dependencies
- **OperationSymbol** (Task 1) ✅ - Already implemented
- **java.util.List** - Standard Java collections

### Indirect Dependencies
- **Operations** (Task 50) ❌ - Provides static utility methods used by implementations
- **Horner** (Task 3) ❌ - Used for table encoding/decoding
- **ArrayString** (Task 6) ❌ - Used for debugging output

### Usage Patterns Found
- Used as parameter type in `List<Operation>`, `Map<OperationSymbol, Operation>`
- Heavily used in algebra classes for operation evaluation
- Concrete implementations: `AbstractOperation`, `OperationWithDefaultValue`, `IntOperationImp`
- Static utility methods in `Operations` class work with `Operation` instances

## Rust Implementation Strategy

### Trait Design
```rust
pub trait Operation: Ord + PartialOrd + Eq + PartialEq + Hash + Display {
    // Core properties
    fn arity(&self) -> i32;
    fn get_set_size(&self) -> i32;
    fn symbol(&self) -> &OperationSymbol;
    
    // Operation evaluation
    fn value_at(&self, args: &[i32]) -> Result<i32, String>;
    fn value_at_arrays(&self, args: &[&[i32]]) -> Result<Vec<i32>, String>;
    fn int_value_at(&self, args: &[i32]) -> Result<i32, String>;
    fn int_value_at_horner(&self, arg: i32) -> Result<i32, String>;
    
    // Table management
    fn make_table(&mut self) -> Result<(), String>;
    fn get_table(&self) -> Option<&[i32]>;
    fn get_table_force(&mut self, make_table: bool) -> Result<&[i32], String>;
    fn is_table_based(&self) -> bool;
    
    // Property checks
    fn is_idempotent(&self) -> Result<bool, String>;
    fn is_associative(&self) -> Result<bool, String>;
    fn is_commutative(&self) -> Result<bool, String>;
    fn is_totally_symmetric(&self) -> Result<bool, String>;
    fn is_maltsev(&self) -> Result<bool, String>;
    fn is_total(&self) -> Result<bool, String>;
}
```

### Key Design Decisions
- **Error Handling**: Use `Result<T, String>` for methods that can fail
- **Generic vs Dynamic Dispatch**: Use dynamic dispatch (`dyn Operation`) for flexibility
- **Comparable**: Implement `Ord`, `PartialOrd`, `Eq`, `PartialEq`, `Hash` traits
- **Display**: Implement `Display` trait for string representation
- **Table Management**: Use `Option<&[i32]>` for optional table access
- **Method Naming**: Use snake_case following Rust conventions

## Java Wrapper Suitability

### Assessment: NOT SUITABLE
- **Reason**: Operation is an interface that cannot be instantiated directly
- **Alternative**: Create wrappers for concrete implementations:
  - `AbstractOperationWrapper` - For testing abstract operation functionality
  - `OperationWithDefaultValueWrapper` - For testing default value operations
  - `IntOperationWrapper` - For testing table-based operations

### Testing Strategy
- Test through concrete implementations rather than interface directly
- Create factory methods in wrapper to generate test instances
- Use `Operations.makeIntOperation()` to create testable instances

## Implementation Recommendations

### Phase 1: Core Trait Implementation
1. **Define Operation trait** with all 17 methods
2. **Implement comparison traits** (Ord, PartialOrd, Eq, PartialEq, Hash)
3. **Add Display trait** for string representation
4. **Create trait documentation** with examples

### Phase 2: Concrete Implementations
1. **Implement AbstractOperation** struct implementing Operation trait
2. **Implement IntOperation** for table-based operations
3. **Implement OperationWithDefaultValue** for default value handling
4. **Add factory methods** for creating test instances

### Phase 3: Python Bindings
1. **Create PyOperation trait** for Python exposure
2. **Implement concrete PyO3 classes** for each implementation
3. **Add Python magic methods** (__str__, __repr__, __eq__, etc.)
4. **Export clean names** without Py prefix

### Phase 4: Testing Infrastructure
1. **Create Java wrappers** for concrete implementations
2. **Implement Rust tests** using compare_with_java! macro
3. **Add Python tests** through concrete implementations
4. **Test all property methods** with various operation types

## Dependencies Status
- **OperationSymbol**: ✅ Completed (Task 1)
- **Operations**: ❌ Not implemented (Task 50) - Required for static utility methods
- **Horner**: ❌ Not implemented (Task 3) - Required for table encoding
- **ArrayString**: ❌ Not implemented (Task 6) - Required for debugging

## Implementation Priority
- **HIGH PRIORITY** - Foundational interface blocking many other classes
- **Blocking Classes**: AbstractOperation, OperationWithDefaultValue, IntOperation, all algebra classes
- **Recommendation**: Implement trait first, then concrete implementations, then dependent classes

## Acceptance Criteria
- [x] Operation trait implemented with all 17 methods
- [x] Trait implements Ord, PartialOrd, Eq, PartialEq, Hash, Display (in concrete implementations)
- [x] Proper error handling with Result types
- [x] AbstractOperation struct implementing Operation trait
- [x] IntOperation struct for table-based operations
- [x] Python bindings for concrete implementations
- [x] Java wrappers for concrete implementations
- [x] Rust tests pass with comprehensive coverage (17 tests)
- [x] Python tests implemented for cross-language verification (40+ tests)
- [x] Code compiles successfully (warnings only, no errors)
- [x] Documentation complete with examples

## Implementation Status
**Status**: ✅ **COMPLETE AND VERIFIED**

### Implementation Summary
- **Operation Trait**: Fully implemented with all 17 methods from Java interface
- **Concrete Implementations**: 
  - `AbstractOperation`: Basic mathematical operations with table support
  - `IntOperation`: Table-based operations with XOR, AND, OR factory methods
  - `OperationWithDefaultValue`: Partial operations with default value handling
- **Python Bindings**: Complete PyO3 integration with clean API (no Py prefix)
- **Java Wrappers**: CLI wrappers for testing (`AbstractOperationWrapper`, `IntOperationWrapper`)
- **Testing**: 17 Rust unit tests + 40+ Python tests for cross-language verification
- **Documentation**: Comprehensive with examples and usage patterns

### Key Features Implemented
1. **All 17 Operation Interface Methods**:
   - Core: `arity()`, `get_set_size()`, `symbol()`
   - Evaluation: `value_at()`, `int_value_at()`, `int_value_at_horner()`
   - Tables: `make_table()`, `get_table()`, `is_table_based()`
   - Properties: `is_idempotent()`, `is_associative()`, `is_commutative()`, etc.

2. **Proper Error Handling**: Result-based error propagation throughout
3. **Object Safety**: Trait design allows `Box<dyn Operation>`
4. **Cross-Language Compatibility**: Verified through comprehensive testing
5. **Memory Safety**: Thread-safe with proper ownership patterns

**Date Completed**: 2025-10-14  
**Implementation Time**: Full implementation cycle completed successfully  
**Dependencies**: Uses OperationSymbol (Task 1) ✅  
**Blocking**: Ready to unblock dependent classes (AbstractOperation, algebra classes, etc.)
