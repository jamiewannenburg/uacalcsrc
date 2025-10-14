# Task 11: Translate `AbstractOperation`

**Java File:** `org/uacalc/alg/op/AbstractOperation.java`  
**Package:** `org.uacalc.alg.op`  
**Rust Module:** `alg::op::AbstractOperation`  
**Dependencies:** 3 (3 non-UI/example)  
**Estimated Public Methods:** ~20

## Description
Translate the Java class `org.uacalc.alg.op.AbstractOperation` to Rust with Python bindings.

## Dependencies
- **Operation** (interface) - AbstractOperation implements this interface
- **OperationSymbol** - Used for operation symbol representation and comparison  
- **Operations** (utility class) - Used for static methods like isTotal, isAssociative, etc.

**Note**: The original task incorrectly listed 0 dependencies. This is a foundational class with 3 key dependencies that must be implemented first.

## Java Class Analysis

### Class Type
- **Type**: Abstract class implementing Operation interface
- **Inheritance**: `public abstract class AbstractOperation implements Operation`
- **Key Fields**: 
  - `OperationSymbol symbol` - Operation symbol with name and arity
  - `int algSize` - Size of the algebra set
  - `int[] valueTable` - Optional value table for fast lookup
- **Abstract Method**: `valueAt(List args)` - Must be implemented by subclasses
- **Key Methods**: 20+ public methods including arity(), getSetSize(), isIdempotent(), etc.

### Public Methods Analysis
1. **Constructors**: 2 constructors (String+int+int, OperationSymbol+int)
2. **Accessors**: arity(), getSetSize(), symbol()
3. **Abstract Methods**: valueAt(List args) - must be implemented
4. **Optional Methods**: valueAt(int[][]), intValueAt(int[]), intValueAt(int)
5. **Property Methods**: isTableBased(), isIdempotent(), isTotal(), isTotallySymmetric(), isAssociative(), isCommutative(), isMaltsev()
6. **Table Methods**: makeTable(), getTable(), getTable(boolean)
7. **Comparison**: compareTo(Operation)

### Dependencies Found
- **OperationSymbol** (Task 1) - ✅ Already implemented
- **Operation interface** (Task 12) - ❌ Not yet implemented  
- **Operations utility class** (Task 50) - ❌ Not yet implemented
- **Logger** - Java logging framework (needs Rust equivalent)
- **ArrayString** - Utility for array string representation

## Rust Implementation Strategy

### Trait Design
- **Operation Trait**: Convert Java interface to Rust trait with all required methods
- **AbstractOperation Trait**: Create trait with default implementations for most methods
- **Trait Objects**: Use `Box<dyn Operation>` for dynamic dispatch where needed

### Struct Design
- **AbstractOperation**: Cannot be instantiated directly (abstract class)
- **Concrete Implementations**: Focus on AbstractIntOperation, OperationWithDefaultValue
- **Error Handling**: Use `Result<T, String>` for operations that can fail
- **Memory Management**: Use `Box<dyn Operation>` for trait objects

### Method Organization
- **Trait Methods**: All interface methods from Operation
- **Default Implementations**: Most AbstractOperation methods as default trait implementations
- **Abstract Methods**: valueAt() must be implemented by concrete types
- **Static Methods**: Operations utility methods as associated functions

### Generic vs Dynamic Dispatch
- **Trait Objects**: Use for Operation interface compliance
- **Generics**: Use for compile-time optimization where possible
- **Mixed Approach**: Trait objects for external API, generics for internal operations

## Java Wrapper Suitability

### Assessment
- **NOT SUITABLE** - AbstractOperation cannot be instantiated directly
- **Alternative**: Create wrappers for concrete subclasses:
  - AbstractIntOperation (concrete but minimal)
  - OperationWithDefaultValue (concrete and functional)
- **Testing Strategy**: Test through concrete implementations

### Recommended Approach
1. Create wrapper for AbstractIntOperation (simple concrete subclass)
2. Create wrapper for OperationWithDefaultValue (full-featured concrete subclass)
3. Test AbstractOperation functionality through these concrete implementations

## Implementation Recommendations

### Phase 1: Core Infrastructure
1. **Implement Operation Trait** (Task 12) - Must be done first
2. **Implement Operations Utility** (Task 50) - Required for many AbstractOperation methods
3. **Set up logging framework** - Replace Java Logger with Rust logging

### Phase 2: AbstractOperation Trait
1. **Create Operation trait** with all interface methods
2. **Create AbstractOperation trait** with default implementations
3. **Implement comparison traits** (Ord, PartialOrd, Eq, PartialEq)
4. **Add logging support** for debug/info messages

### Phase 3: Concrete Implementations
1. **AbstractIntOperation** - Simple concrete implementation
2. **OperationWithDefaultValue** - Full-featured concrete implementation
3. **IntOperationImp** - Table-based implementation from Operations class

### Phase 4: Testing & Validation
1. **Rust unit tests** for all trait methods
2. **Java wrapper tests** for concrete implementations
3. **Python binding tests** for concrete implementations
4. **Cross-language compatibility tests**

## Critical Implementation Notes

### Key Challenges
- **Abstract Class Pattern**: Rust doesn't have abstract classes - use traits with default implementations
- **Logger Integration**: Replace Java Logger with Rust logging framework
- **Value Table Management**: Careful memory handling for optional value tables
- **Method Delegation**: Many methods delegate to Operations utility class
- **Comparison Logic**: Implement proper trait implementations for ordering

### Error Handling Strategy
- **Validation Errors**: Use `Result<T, String>` for recoverable errors
- **Unsupported Operations**: Use `panic!` for truly unsupported operations (matching Java behavior)
- **Input Validation**: Validate arity, set size, and argument bounds

### Memory Management
- **Trait Objects**: Use `Box<dyn Operation>` for dynamic dispatch
- **Value Tables**: Use `Option<Vec<i32>>` for optional value tables
- **String Handling**: Use `String` for owned strings, `&str` for borrowed strings

## Testing Strategy

### Rust Tests
- **Unit Tests**: Test all trait methods with various inputs
- **Edge Cases**: Test boundary conditions and error cases
- **Performance Tests**: Test with timeouts matching Java performance
- **Integration Tests**: Test with concrete implementations

### Java Wrapper Tests
- **AbstractIntOperation Wrapper**: Test basic functionality
- **OperationWithDefaultValue Wrapper**: Test full feature set
- **Comparison Tests**: Compare results with Rust implementation

### Python Tests
- **Binding Tests**: Test all exposed methods through Python
- **Compatibility Tests**: Ensure Python API matches Rust API
- **Error Handling Tests**: Test error conditions and exceptions

## Acceptance Criteria
- [ ] Operation trait implemented with all required methods
- [ ] AbstractOperation trait with default implementations  
- [ ] Operations utility class with static methods
- [ ] Concrete implementations (AbstractIntOperation, OperationWithDefaultValue)
- [ ] Python bindings for concrete implementations
- [ ] Java CLI wrappers for concrete implementations
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
