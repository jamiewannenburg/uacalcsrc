# Task 52: Translate `ParameterizedAlgebra`

**Java File:** `org/uacalc/alg/ParameterizedAlgebra.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::ParameterizedAlgebra`  
**Dependencies:** 1 (1 non-UI/example)  
**Estimated Public Methods:** 1

### Description
Translate the Java class `org.uacalc.alg.ParameterizedAlgebra` to Rust with Python bindings.

### Java Class Analysis
- **Type**: Concrete class (not interface or abstract)
- **Purpose**: Represents parameterized algebras with configurable parameters
- **Key Fields**:
  - `List<String> parameterNames` - Names of parameters
  - `String name` - Algebra name
  - `String setSizeExp` - Expression for set size
  - `String description` - Algebra description
  - `List<ParameterizedOperation> ops` - List of parameterized operations
- **Public Methods**: 1
  - `getParameterMap(List<Integer> values)` - Creates parameter mapping from values

### Dependencies Analysis
**CORRECTED DEPENDENCIES** (based on actual codebase analysis):
- `org.uacalc.alg.BasicAlgebra` - Only actual dependency found in usage
- ~~`org.uacalc.alg.conlat`~~ - Imported but not used in implementation
- ~~`org.uacalc.alg.sublat`~~ - Imported but not used in implementation  
- ~~`org.uacalc.alg.op.ParameterizedOperation`~~ - Not directly used, only imported

**Dependency Level**: 1 (only depends on BasicAlgebra)

### Rust Implementation Recommendations

#### 1. Struct Design
```rust
pub struct ParameterizedAlgebra {
    pub parameter_names: Vec<String>,
    pub name: String,
    pub set_size_exp: String,
    pub description: String,
    pub ops: Vec<ParameterizedOperation>,
}
```

#### 2. Method Implementation
- **`get_parameter_map(values: Vec<i32>) -> HashMap<String, String>`**
  - Convert `List<Integer>` to `Vec<i32>`
  - Return `HashMap<String, String>` instead of `Map<String, String>`
  - Handle iterator logic with Rust idioms

#### 3. Constructor Pattern
- Implement `new()` constructor with all fields
- Consider `new_safe()` for validation if needed
- No special builder pattern required (simple struct)

#### 4. Dependencies
- **BasicAlgebra**: Must be implemented first (dependency level 1)
- **ParameterizedOperation**: Referenced in field but not used in methods
- **conlat/sublat**: Imported but unused - can be removed

#### 5. Error Handling
- Use `Result<HashMap<String, String>, String>` for `get_parameter_map_safe()`
- Provide both safe and panic versions following patterns
- Validate input lengths match parameter count

### Java Wrapper Suitability
**SUITABLE** - This is a concrete class with:
- Simple data structure (no complex logic)
- One public method that can be easily tested
- No abstract methods or interfaces
- Can be instantiated and tested directly

### Testing Strategy
1. **Rust Tests**: Test `get_parameter_map` with various input sizes
2. **Python Tests**: Verify parameter mapping functionality
3. **Java Wrapper**: Test parameter mapping with different value lists
4. **Edge Cases**: Empty lists, mismatched sizes, special characters

### Implementation Priority
**HIGH** - This is a foundational class (dependency level 1) that other classes depend on. Should be implemented early in the translation process.

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods  
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] Dependencies corrected (only BasicAlgebra)
