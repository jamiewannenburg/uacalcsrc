# Task 65: Translate `AlgebraIO`

**Java File:** `org/uacalc/io/AlgebraIO.java`  
**Package:** `org.uacalc.io`  
**Rust Module:** `io::AlgebraIO`  
**Dependencies:** 11 (11 non-UI/example)  
**Estimated Public Methods:** 18

## Description
Translate the Java class `org.uacalc.io.AlgebraIO` to Rust with Python bindings.

## Java File Analysis

### Class Type
- **Type**: Concrete class with static methods only
- **Pattern**: Utility class (all methods are static)
- **Constructor**: Private (utility class pattern)
- **Public Methods**: 18 static methods

### Method Analysis
The class contains the following public static methods:
1. `parseLine(String line)` - Parse line as int, return -1 for comments
2. `readAlgebraFile(String f)` - Read algebra from file path
3. `readAlgebraFile(File f)` - Read algebra from File object
4. `readAlgebraFromStream(InputStream is)` - Read algebra from stream
5. `readAlgebraListFile(String f)` - Read list of algebras from file path
6. `readAlgebraListFile(File f)` - Read list of algebras from File object
7. `readAlgebraListFromStream(InputStream is)` - Read single algebra from stream
8. `readOp(int arity, int size, BufferedReader in)` - Read operation from stream
9. `readDepth2List(BufferedReader in, String start, String end)` - Unimplemented
10. `convertToXML(String f)` - Convert algebra file to XML
11. `convertToXML(File f)` - Convert algebra file to XML
12. `writeAlgebraFile(SmallAlgebra alg, String f)` - Write algebra to file
13. `writeAlgebraFile(SmallAlgebra alg, File f)` - Write algebra to file
14. `writeAlgebraFile(SmallAlgebra alg, String f, boolean oldStyle)` - Write with style option
15. `writeAlgebraFile(SmallAlgebra alg, File f, boolean oldStyle)` - Write with style option
16. `readProjectivePlane(InputStream f)` - Read projective plane from stream
17. `readProjectivePlane(String f)` - Read projective plane from file path
18. `readProjectivePlane(File f)` - Read projective plane from File object
19. `readProjectivePlane(BufferedReader in)` - Read projective plane from reader

## Dependencies Analysis

### Current Dependencies (Incorrect)
The task file lists only 6 dependencies, but analysis reveals 11 dependencies:

### Corrected Dependencies
1. `org.uacalc.alg` - For SmallAlgebra, BasicAlgebra
2. `org.uacalc.alg.conlat` - For conlat package (imported but not directly used)
3. `org.uacalc.alg.op.Operation` - For Operation interface
4. `org.uacalc.alg.op.OperationSymbol` - For OperationSymbol class
5. `org.uacalc.alg.op.Operations` - For Operations.makeIntOperation
6. `org.uacalc.util` - For util package (imported but not directly used)
7. `org.uacalc.io.ExtFileFilter` - For file extension handling
8. `org.uacalc.io.AlgebraReader` - For reading XML algebra files
9. `org.uacalc.io.AlgebraWriter` - For writing XML algebra files
10. `org.uacalc.io.Mace4Reader` - For reading Mace4 format files
11. `org.uacalc.io.BadAlgebraFileException` - For exception handling
12. `org.uacalc.util.Horner` - For hornerInv method

### Missing Dependencies
The following dependencies are missing from the current task file:
- `org.uacalc.io.ExtFileFilter` (Task 8)
- `org.uacalc.io.AlgebraReader` (Task 62)
- `org.uacalc.io.AlgebraWriter` (Task 54)
- `org.uacalc.io.Mace4Reader` (Task 37)
- `org.uacalc.io.BadAlgebraFileException` (Task 7)
- `org.uacalc.util.Horner` (Task 3)

## Rust Implementation Recommendations

### Design Pattern
- **Rust Construct**: Module with free functions (not a struct)
- **Reasoning**: Java class has only static methods, so Rust should use free functions in a module
- **Module Structure**: `io::algebra_io` module with public functions

### Function Organization
- **Static Methods → Free Functions**: All static methods become free functions
- **Error Handling**: Use `Result<T, BadAlgebraFileException>` for functions that can fail
- **File I/O**: Use `std::fs::File` and `std::io::BufReader` for file operations
- **Stream I/O**: Use `std::io::Read` trait for stream operations

### Key Implementation Decisions
1. **Generic vs Dynamic Dispatch**: Use dynamic dispatch for file format detection
2. **Error Handling**: Use custom `BadAlgebraFileException` type
3. **File Format Support**: Support .alg, .ua, .xml, and .m4 formats
4. **Stream Handling**: Use `Box<dyn Read>` for stream parameters

### Method Translation Strategy
- `parseLine` → `parse_line(line: &str) -> Result<i32, String>`
- `readAlgebraFile` → `read_algebra_file(path: &Path) -> Result<SmallAlgebra, BadAlgebraFileException>`
- `writeAlgebraFile` → `write_algebra_file(alg: &SmallAlgebra, path: &Path, old_style: bool) -> Result<(), std::io::Error>`
- All other methods follow similar patterns

## Java Wrapper Suitability

### Assessment: **SUITABLE**
- **Reason**: Concrete utility class with static methods
- **Testing Strategy**: Create wrapper with CLI commands for each method
- **Wrapper Location**: `java_wrapper/src/io/AlgebraIOWrapper.java`

### Wrapper Design
- **Base Class**: Extend `WrapperBase`
- **Command Structure**: One command per public method
- **Input Handling**: File paths, streams, and parameters
- **Output Format**: JSON with method results

## Testing Strategy

### Rust Tests
- **Unit Tests**: Test each function individually
- **Integration Tests**: Test file I/O operations
- **Error Tests**: Test error conditions and edge cases
- **Format Tests**: Test different file formats (.alg, .ua, .xml, .m4)

### Python Tests
- **Binding Tests**: Test Python bindings for all functions
- **File I/O Tests**: Test reading/writing various file formats
- **Error Handling Tests**: Test exception handling in Python

### Java Wrapper Tests
- **CLI Tests**: Test all command-line interfaces
- **Cross-Validation**: Compare results with Rust implementation
- **File Format Tests**: Test all supported file formats

## Implementation Status

### Current Status: **NOT STARTED**
- **Rust Implementation**: Only placeholder struct exists in `src/io/mod.rs`
- **Python Bindings**: Not implemented
- **Java Wrapper**: Not implemented
- **Tests**: Not implemented

### Required Dependencies Status
- `ExtFileFilter` (Task 8): ✅ **COMPLETED** - Full implementation with Rust, Python bindings, and Java wrapper
- `BadAlgebraFileException` (Task 7): ✅ **COMPLETED** - Full implementation with Rust, Python bindings, and Java wrapper
- `Horner` (Task 3): ✅ **COMPLETED** - Full implementation with Rust, Python bindings, and Java wrapper
- `AlgebraReader` (Task 62): ✅ **COMPLETED** - Full implementation with Rust, Python bindings, and Java wrapper (2025-01-15)
- `AlgebraWriter` (Task 54): ❌ **NOT COMPLETED** - Only placeholder struct exists in `src/io/mod.rs`
- `Mace4Reader` (Task 37): ✅ **COMPLETED** - Full implementation with Rust, Python bindings, and Java wrapper

## Implementation Priority

### Priority: **PARTIALLY READY**
- **Reason**: Core I/O functionality, but depends on 2 incomplete tasks
- **Blocking Dependencies**: AlgebraWriter, Mace4Reader
- **Available Dependencies**: ExtFileFilter, BadAlgebraFileException, Horner, AlgebraReader
- **Available Algebra Types**: BasicSmallAlgebra, ProductAlgebra, Subalgebra, QuotientAlgebra, SubProductAlgebra, BigProductAlgebra
- **Recommendation**: Can implement basic functionality now, but will need AlgebraWriter and Mace4Reader for complete implementation

## Next Steps

1. **Implement Partial Functionality**: Can implement methods that don't require AlgebraWriter or Mace4Reader
2. **Complete Blocking Dependencies**: Finish AlgebraWriter and Mace4Reader tasks for full functionality
3. **Implement Rust Module**: Create `src/io/algebra_io.rs` with all functions
4. **Add Python Bindings**: Expose functions through PyO3
5. **Create Java Wrapper**: Implement CLI wrapper for testing
6. **Write Tests**: Comprehensive test suite for all functions
7. **Update Dependencies**: Correct the dependency list in this task file

## Acceptance Criteria
- [ ] All 18 public methods translated to Rust free functions
- [ ] Python bindings expose all functions
- [ ] Java CLI wrapper created with all methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] All dependencies completed and available

## Current Implementation Analysis

### Rust Implementation
- **Status**: ❌ **NOT STARTED**
- **Location**: `src/io/mod.rs` (only placeholder struct exists)
- **Quality**: **Poor** - Only empty struct definition with TODO comment
- **Notes**: No actual implementation, just placeholder struct

### Python Bindings
- **Status**: ❌ **NOT STARTED**
- **Location**: Not found
- **Quality**: **N/A**
- **Notes**: No Python bindings exist

### Java Wrapper
- **Status**: ❌ **NOT STARTED**
- **Location**: Not found
- **Quality**: **N/A**
- **Notes**: No Java wrapper exists

### Tests
- **Status**: ❌ **NOT STARTED**
- **Location**: Not found
- **Quality**: **N/A**
- **Notes**: No tests exist

### Blocking Dependencies
- `AlgebraWriter` (Task 54): ❌ **NOT COMPLETED** - Only placeholder struct exists in `src/io/mod.rs`
- `Mace4Reader` (Task 37): ✅ **COMPLETED** - Full implementation with Rust, Python bindings, and Java wrapper

### Ready Dependencies
- `ExtFileFilter` (Task 8): ✅ **COMPLETED** - Full implementation with Rust, Python bindings, and Java wrapper
- `BadAlgebraFileException` (Task 7): ✅ **COMPLETED** - Full implementation with Rust, Python bindings, and Java wrapper
- `Horner` (Task 3): ✅ **COMPLETED** - Full implementation with Rust, Python bindings, and Java wrapper
- `AlgebraReader` (Task 62): ✅ **COMPLETED** - Full implementation with Rust, Python bindings, and Java wrapper (2025-01-15)

### Available Algebra Types
- `BasicSmallAlgebra`: ✅ **IMPLEMENTED** - Full implementation
- `ProductAlgebra`: ✅ **IMPLEMENTED** - Full implementation  
- `Subalgebra`: ✅ **IMPLEMENTED** - Full implementation
- `QuotientAlgebra`: ✅ **IMPLEMENTED** - Full implementation
- `SubProductAlgebra`: ✅ **IMPLEMENTED** - Full implementation
- `BigProductAlgebra`: ✅ **IMPLEMENTED** - Full implementation

### Implementation Status Analysis

**Can Implement Now (Partial Implementation):**
- `parseLine` - ✅ **READY** - No dependencies
- `readAlgebraFile` (String/File) - ✅ **READY** - Uses ExtFileFilter, AlgebraReader, Mace4Reader (but Mace4Reader not available)
- `readAlgebraFromStream` - ✅ **READY** - Uses AlgebraReader only
- `readAlgebraListFile` (String/File) - ✅ **READY** - Uses ExtFileFilter, AlgebraReader
- `readAlgebraListFromStream` - ✅ **READY** - Uses AlgebraReader only
- `readOp` - ✅ **READY** - No dependencies
- `readDepth2List` - ✅ **READY** - Unimplemented in Java, can implement as stub
- `readProjectivePlane` (all variants) - ✅ **READY** - No dependencies

**Cannot Implement Yet (Blocked):**
- `convertToXML` (String/File) - ❌ **BLOCKED** - Requires AlgebraWriter
- `writeAlgebraFile` (all variants) - ❌ **BLOCKED** - Requires AlgebraWriter
- `readAlgebraFile` with Mace4 support - ✅ **READY** - Mace4Reader now available

**Summary:**
- **Implementable Now**: 9 out of 18 methods (50%)
- **Blocked**: 9 out of 18 methods (50%)
- **Recommendation**: Start with partial implementation, complete when AlgebraWriter dependency is ready

## Updated Task Status Summary

**Updated Status**: Task 65 - AlgebraIO can now be **PARTIALLY IMPLEMENTED**

**Key Findings:**
1. **5 out of 6 dependencies are COMPLETED** (83% complete)
2. **All required algebra types are IMPLEMENTED** (BasicSmallAlgebra, ProductAlgebra, Subalgebra, QuotientAlgebra, etc.)
3. **9 out of 18 methods can be implemented now** (50% of functionality)
4. **Only 1 dependency remains**: AlgebraWriter (only has placeholder struct)

**Recommendation**: 
- **Start implementation now** with the 9 methods that can be completed
- **Complete remaining dependency** (AlgebraWriter) for full functionality
- **This represents significant progress** from the previous "BLOCKED" status

**Implementation Priority**: **MEDIUM-HIGH** - Can provide substantial value with partial implementation
