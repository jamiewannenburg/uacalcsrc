# Task 54: Translate `AlgebraWriter`

**Java File:** `org/uacalc/io/AlgebraWriter.java`  
**Package:** `org.uacalc.io`  
**Rust Module:** `io::AlgebraWriter`  
**Dependencies:** 4 (4 non-UI/example)  
**Estimated Public Methods:** ~76

## Analysis Summary

### Java Class Analysis
- **Type**: Concrete class (not interface or abstract)
- **Purpose**: XML writing for algebras with support for multiple algebra types
- **Key Methods**: 3 public methods + 1 main method + 20+ private helper methods
- **Special Patterns**: Uses instanceof checks for different algebra types, recursive XML generation
- **File Size**: 510 lines, 17KB

### Dependency Analysis
**Current Dependencies Listed:**
- `org.uacalc.alg` ✅ (Multiple algebra types - partially implemented)
- `org.uacalc.alg.conlat` ✅ (Partition - Task 5 completed)
- `org.uacalc.alg.op.Operation` ❌ (Task 12 - not completed)
- `org.uacalc.util` ✅ (Multiple utility classes - mostly completed)

**Additional Dependencies Found:**
- `org.uacalc.alg.SmallAlgebra` (interface) - **MISSING from dependencies**
- `org.uacalc.alg.Algebra` (parent interface) - **MISSING from dependencies**
- `org.uacalc.alg.PowerAlgebra` (concrete class) - **MISSING from dependencies**
- `org.uacalc.alg.ProductAlgebra` (concrete class) - **MISSING from dependencies**
- `org.uacalc.alg.QuotientAlgebra` (concrete class) - **MISSING from dependencies**
- `org.uacalc.alg.Subalgebra` (concrete class) - **MISSING from dependencies**
- `org.uacalc.alg.FreeAlgebra` (concrete class) - **MISSING from dependencies**
- `org.uacalc.alg.BigProductAlgebra` (concrete class) - **MISSING from dependencies**
- `org.uacalc.alg.SubProductAlgebra` (concrete class) - **MISSING from dependencies**
- `org.uacalc.util.IntArray` (concrete class) - **MISSING from dependencies**
- `org.uacalc.util.ArrayIncrementor` (interface) - **MISSING from dependencies**
- `org.uacalc.util.SequenceGenerator` (utility class) - **MISSING from dependencies**
- `org.uacalc.util.Horner` (utility class) - **MISSING from dependencies**
- `org.uacalc.util.ArrayString` (utility class) - **MISSING from dependencies**
- `org.uacalc.io.AlgebraIO` (utility class) - **MISSING from dependencies**

**Dependency Status**: ❌ **BLOCKED** - Many critical dependencies are not completed yet

### Rust Implementation Recommendations

#### 1. Struct Design
```rust
/// XML writer for algebras with support for multiple algebra types
pub struct AlgebraWriter {
    out: Box<dyn Write>,
    algebra: Box<dyn SmallAlgebra>,
    indent: usize,
}

impl AlgebraWriter {
    /// Create new writer with PrintWriter
    pub fn new(algebra: Box<dyn SmallAlgebra>, out: Box<dyn Write>) -> Self
    
    /// Create new writer with file path
    pub fn new_with_file(algebra: Box<dyn SmallAlgebra>, file_path: &str) -> Result<Self, String>
    
    /// Write complete algebra XML
    pub fn write_algebra_xml(&mut self) -> Result<(), String>
    
    /// Write algebra (dispatches to specific type)
    pub fn write_algebra(&mut self) -> Result<(), String>
    
    /// Write basic algebra
    pub fn write_basic_algebra(&mut self) -> Result<(), String>
    
    // Private helper methods for different algebra types
    // write_power_algebra, write_product_algebra, etc.
}
```

#### 2. Implementation Strategy
- **Concrete Class → Struct**: Convert Java class to Rust struct
- **Generic vs Dynamic Dispatch**: Use `Box<dyn SmallAlgebra>` for dynamic dispatch
- **Error Handling**: Use `Result<T, String>` for operations that can fail
- **XML Generation**: Use string building with proper indentation
- **Algebra Type Dispatch**: Use pattern matching instead of instanceof checks

#### 3. Method Organization
- **Public Methods**: Constructor, main writing methods
- **Private Methods**: Helper methods for specific algebra types
- **Static Constants**: XML tag constants as associated constants
- **Error Handling**: Comprehensive error handling for file operations

### Java Wrapper Suitability
**Status**: ✅ **SUITABLE** - Concrete class with public methods

**Reasoning**: 
- AlgebraWriter is a concrete class that can be instantiated
- Has public methods that can be tested
- Can create instances with different algebra types
- Suitable for comprehensive testing

### Testing Strategy
1. **Unit Tests**: Test XML generation for different algebra types
2. **Integration Tests**: Test with actual algebra instances
3. **Cross-Language Tests**: Compare XML output against Java implementation
4. **File I/O Tests**: Test file writing and reading operations

### Implementation Priority
**BLOCKED** - Cannot proceed until dependencies are completed:
1. Complete Operation interface (Task 12)
2. Complete SmallAlgebra interface (Task 41)
3. Complete all algebra concrete classes (PowerAlgebra, ProductAlgebra, etc.)
4. Complete remaining utility classes (Horner, ArrayString, etc.)
5. Then implement AlgebraWriter

### Recommendations
1. **Update Dependencies**: Add all missing dependencies to dependency list
2. **Wait for Dependencies**: Do not start implementation until all dependencies are complete
3. **Design for Extensibility**: Ensure struct design accommodates all algebra types
4. **Plan for XML Generation**: Design efficient XML generation with proper indentation
5. **Consider Error Handling**: Plan comprehensive error handling for file operations

### Acceptance Criteria
- [ ] All dependencies completed (Operation, SmallAlgebra, algebra classes, utilities)
- [ ] AlgebraWriter struct implemented with all public methods
- [ ] XML generation works for all algebra types
- [ ] File I/O operations work correctly
- [ ] Rust tests pass for all methods
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Documentation complete
- [ ] Code compiles without warnings
