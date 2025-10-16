# Task 37: Translate `Mace4Reader`

**Java File:** `org/uacalc/io/Mace4Reader.java`  
**Package:** `org.uacalc.io`  
**Rust Module:** `io::Mace4Reader`  
**Dependencies:** 4 (4 non-UI/example)  
**Estimated Public Methods:** 3

## Description
Translate the Java class `org.uacalc.io.Mace4Reader` to Rust with Python bindings. This class reads Mace4 model files and parses them into algebras, specifically handling the operations while ignoring relations.

## Java Class Analysis

### Class Type
- **Type**: Concrete class (`public final class Mace4Reader`)
- **Pattern**: Reader/parser with stateful parsing
- **Key Features**: 
  - Stateful parser with line tracking
  - Character-by-character parsing
  - Error handling with line/column information
  - Returns `SmallAlgebra` objects

### Public Methods
1. `Mace4Reader(InputStream stream)` - Constructor
2. `parseAlgebra()` - Parse single algebra from stream
3. `parseAlgebraList()` - Parse multiple algebras from stream
4. `isOrdinaryCharacter(char c)` - Static utility method
5. `isSpecialCharacter(char c)` - Static utility method

### Dependencies Analysis
**Direct Dependencies:**
- `org.uacalc.alg.SmallAlgebra` (interface)
- `org.uacalc.alg.BasicAlgebra` (concrete class)
- `org.uacalc.alg.op.Operation` (interface)
- `org.uacalc.alg.op.Operations` (utility class with static methods)
- `org.uacalc.io.BadAlgebraFileException` (exception class)

**Indirect Dependencies:**
- `org.uacalc.alg.op.OperationSymbol` (used by Operations.makeIntOperation)
- `org.uacalc.alg.op.AbstractOperation` (base class for operations)
- `org.uacalc.alg.op.IntOperationImp` (concrete operation implementation)
- `org.uacalc.alg.GeneralAlgebra` (base class for BasicAlgebra)

**Missing Dependencies in Task:**
- `org.uacalc.alg.BasicAlgebra` (not listed but used)
- `org.uacalc.alg.op.Operation` (not listed but used)
- `org.uacalc.alg.op.Operations` (not listed but used)

## Rust Implementation Recommendations

### Design Decisions
1. **Main Struct**: `Mace4Reader` - stateful parser with internal state
2. **Error Handling**: Use `Result<SmallAlgebra, BadAlgebraFileException>` for parsing methods
3. **State Management**: Store `BufferedReader`, line number, and parsing state
4. **Static Methods**: Convert to associated functions

### Struct Design
```rust
pub struct Mace4Reader {
    reader: BufReader<Box<dyn Read>>,
    line: Option<String>,
    lineno: usize,
    index: usize,
}
```

### Method Organization
- **Constructor**: `new(stream: Box<dyn Read>) -> Result<Self, String>`
- **Instance Methods**: `parse_algebra()`, `parse_algebra_list()`
- **Static Methods**: `is_ordinary_character()`, `is_special_character()`
- **Private Methods**: All parsing helper methods

### Dependencies Status
- ❌ `SmallAlgebra` - Not implemented (placeholder exists)
- ❌ `BasicAlgebra` - Not implemented (placeholder exists)  
- ❌ `Operation` - Not implemented (placeholder exists)
- ❌ `Operations` - Not implemented (placeholder exists)
- ❌ `BadAlgebraFileException` - Implemented in `src/io/mod.rs`

### Implementation Strategy
1. **Phase 1**: Implement core parsing logic with placeholder return types
2. **Phase 2**: Implement proper return types once dependencies are available
3. **Phase 3**: Add comprehensive error handling and validation
4. **Phase 4**: Add Python bindings and testing

## Java Wrapper Suitability
**Status**: ✅ Suitable for testing
**Reason**: Concrete class with clear public API that can be easily wrapped

### Wrapper Design
- **Constructor**: Accept file path or input stream
- **Methods**: Expose `parseAlgebra()` and `parseAlgebraList()`
- **Testing**: Use sample Mace4 files for validation

## Testing Strategy
1. **Unit Tests**: Test parsing logic with known Mace4 files
2. **Integration Tests**: Compare against Java implementation
3. **Error Tests**: Test malformed input handling
4. **Edge Cases**: Empty files, invalid syntax, large files

## Implementation Priority
**BLOCKED** - Cannot proceed until dependencies are implemented:
1. `SmallAlgebra` interface ✅ **IMPLEMENTED** (src/alg/small_algebra.rs)
2. `BasicAlgebra` concrete class ❌ **NOT IMPLEMENTED** (BasicSmallAlgebra exists but not BasicAlgebra)
3. `Operation` interface ✅ **IMPLEMENTED** (src/alg/op/operation.rs)
4. `Operations` utility class ✅ **IMPLEMENTED** (src/alg/op/operations.rs)

## Current Implementation Status

### Rust Implementation
- **Status**: ❌ **NOT STARTED**
- **Location**: src/io/mod.rs (placeholder struct only)
- **Quality**: N/A (not implemented)
- **Notes**: Only contains a placeholder struct with TODO comment

### Python Bindings
- **Status**: ❌ **NOT STARTED**
- **Location**: Not found
- **Quality**: N/A (not implemented)
- **Notes**: No Python bindings exist for Mace4Reader

### Java Wrapper
- **Status**: ❌ **NOT STARTED**
- **Location**: Not found
- **Quality**: N/A (not implemented)
- **Notes**: No Java wrapper exists for Mace4Reader

### Tests
- **Status**: ❌ **NOT STARTED**
- **Location**: Not found
- **Quality**: N/A (not implemented)
- **Notes**: No tests exist for Mace4Reader

### Dependencies Status
- ✅ `SmallAlgebra` - **IMPLEMENTED** (trait in src/alg/small_algebra.rs)
- ❌ `BasicAlgebra` - **NOT IMPLEMENTED** (BasicSmallAlgebra exists but not BasicAlgebra)
- ✅ `Operation` - **IMPLEMENTED** (trait in src/alg/op/operation.rs)
- ✅ `Operations` - **IMPLEMENTED** (module in src/alg/op/operations.rs)
- ✅ `BadAlgebraFileException` - **IMPLEMENTED** (struct in src/io/mod.rs)

### Blocking Dependencies
- `BasicAlgebra` concrete class (needed for return type of parseAlgebra())

### Ready Dependencies
- `SmallAlgebra` trait
- `Operation` trait
- `Operations` utility module
- `BadAlgebraFileException` struct

## Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] **Dependencies implemented first** (75% complete - only BasicAlgebra missing)
