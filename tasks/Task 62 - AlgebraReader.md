# Task 62: Translate `AlgebraReader`

**Java File:** `org/uacalc/io/AlgebraReader.java`  
**Package:** `org.uacalc.io`  
**Rust Module:** `io::AlgebraReader`  
**Dependencies:** 6 (6 non-UI/example)  
**Estimated Public Methods:** ~17

## Description
Translate the Java class `org.uacalc.io.AlgebraReader` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Type**: Concrete class extending `DefaultHandler` (SAX XML parser)
- **Pattern**: SAX event handler for parsing XML algebra files
- **Complexity**: High - complex state management with many internal variables

### Public Methods (17 total)
1. `AlgebraReader(File file)` - Constructor from File
2. `AlgebraReader(String file)` - Constructor from String path  
3. `AlgebraReader(InputStream is)` - Constructor from InputStream
4. `readAlgebraFile()` - Read single algebra from file
5. `readAlgebraFromStream()` - Read single algebra from stream
6. `readAlgebraListFile()` - Read list of algebras from file
7. `readAlgebraListFromStream()` - Read list of algebras from stream
8. `startElement()` - SAX start element handler
9. `characters()` - SAX character data handler
10. `endElement()` - SAX end element handler
11. `main()` - Test/demo method

### Dependencies Analysis
**Correctly Listed Dependencies:**
- `org.uacalc.alg` - Used for SmallAlgebra, Algebra interfaces
- `org.uacalc.alg.conlat` - Used for BasicPartition (congruence handling)
- `org.uacalc.alg.op.Operation` - Used for operation objects
- `org.uacalc.alg.op.OperationSymbol` - Used for operation symbols
- `org.uacalc.alg.op.Operations` - Used for operation creation
- `org.uacalc.util` - Used for SimpleList, Horner, IntArray utilities

**Missing Dependencies:**
- `org.uacalc.io.BadAlgebraFileException` - Exception class used in method signatures

### Usage Patterns
- **Primary Usage**: Used by `AlgebraIO` class for reading XML algebra files
- **File Types**: Handles `.ua` and `.xml` algebra files
- **Algebra Types**: Supports BasicAlgebra, ProductAlgebra, QuotientAlgebra, Subalgebra, PowerAlgebra, BigProductAlgebra, SubProductAlgebra
- **XML Structure**: Complex nested XML with operations, congruences, subuniverses, etc.

## Rust Implementation Recommendations

### Design Decisions
- **Rust Construct**: `struct` (concrete class)
- **Error Handling**: Use `Result<AlgebraReader, String>` for constructors, `Result<SmallAlgebra, String>` for read methods
- **State Management**: Use `RefCell` or `Mutex` for mutable state during parsing
- **XML Parsing**: Use `quick-xml` or `roxmltree` for XML parsing instead of SAX
- **Memory Management**: Use `Rc<RefCell<>>` for shared references to algebras

### Key Implementation Challenges
1. **Complex State Management**: 20+ internal state variables need careful management
2. **XML Parsing**: SAX event-driven parsing needs to be converted to DOM or streaming parser
3. **Algebra Construction**: Multiple algebra types with different construction patterns
4. **Error Handling**: Convert Java exceptions to Rust Result types
5. **Memory Safety**: Ensure proper ownership of algebra objects during construction

### Method Organization
- **Constructor Methods**: `new_from_file()`, `new_from_path()`, `new_from_stream()`
- **Read Methods**: `read_algebra_file()`, `read_algebra_from_stream()`, `read_algebra_list_file()`, `read_algebra_list_from_stream()`
- **SAX Handlers**: `start_element()`, `characters()`, `end_element()` (private)
- **Utility Methods**: `clear_strings()`, `current_tag()`, `parent_tag()`, `int_row()`, `raw_int_array()`, `int_array()`, `add_description()` (private)

### Generic vs Dynamic Dispatch
- **Use Dynamic Dispatch**: For algebra types (SmallAlgebra, Algebra) since they have different implementations
- **Use Generics**: For utility methods that work with generic types

## Java Wrapper Suitability
- **Suitable**: Yes - concrete class with clear public API
- **Testing Strategy**: Test all read methods with sample algebra files
- **CLI Commands**: 
  - `read-algebra-file --file <path>` - Read single algebra
  - `read-algebra-list-file --file <path>` - Read algebra list
  - `read-algebra-from-stream --input <data>` - Read from stream
  - `read-algebra-list-from-stream --input <data>` - Read list from stream

## Testing Strategy
- **Rust Tests**: Test with sample `.ua` and `.xml` files, verify algebra construction
- **Python Tests**: Test all read methods, compare results with Java wrapper
- **Integration Tests**: Test with various algebra types and complex XML structures
- **Error Tests**: Test with malformed XML, invalid algebra data

## Implementation Priority
- **High Priority**: Core read methods for single algebras
- **Medium Priority**: List reading methods, error handling
- **Low Priority**: Advanced XML features, optimization

## Dependencies Status
- **All Dependencies Available**: Yes, all required classes are implemented
- **Dependency Order**: Correct - all dependencies are lower-numbered tasks
- **Missing Dependencies**: Add `org.uacalc.io.BadAlgebraFileException` to dependency list

## Recommendations
1. **Start with Basic Implementation**: Focus on BasicAlgebra reading first
2. **Use XML Library**: Don't try to reimplement SAX - use existing Rust XML library
3. **State Management**: Use builder pattern for complex algebra construction
4. **Error Handling**: Provide both `_safe` and panic versions of methods
5. **Testing**: Create comprehensive test suite with various algebra file types
6. **Documentation**: Document XML format requirements and algebra construction process

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] XML parsing works correctly for all algebra types
- [ ] Error handling matches Java behavior
- [ ] Memory management is safe and efficient
