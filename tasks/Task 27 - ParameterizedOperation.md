# Task 27: Translate `ParameterizedOperation`

**Java File:** `org/uacalc/alg/op/ParameterizedOperation.java`  
**Package:** `org.uacalc.alg.op`  
**Rust Module:** `alg::op::ParameterizedOperation`  
**Dependencies:** 4 (4 non-UI/example)  
**Estimated Public Methods:** 2

## Java Class Analysis

### Class Type
- **Type**: Concrete class (not interface or abstract)
- **Purpose**: Represents parameterized operations that can be instantiated with specific parameter values
- **Key Features**: Uses Groovy scripting engine for dynamic operation definition

### Public Methods
1. `makeOp(Map<String,String> parmMap) -> Operation` - Creates an Operation from parameter map
2. `subParmValues(String parmeterizedString, Map<String,String> parmMap) -> String` - Static method for parameter substitution

### Dependencies Analysis
**UACalc Dependencies:**
- `org.uacalc.alg.ParameterizedAlgebra` - Contains parameter names and values
- `org.uacalc.alg.op.Operation` - Interface for operations
- `org.uacalc.alg.op.AbstractOperation` - Abstract base class for operations
- `org.uacalc.alg.op.OperationSymbol` - Symbol representation

**External Dependencies:**
- `javax.script.*` - Java Scripting API (ScriptEngine, ScriptEngineManager, Invocable, ScriptException)
- `java.util.*` - Standard Java collections (List, Map, HashMap)

### Current Implementation Status
- **Rust Implementation**: Placeholder struct only (line 245-247 in `src/alg/op/mod.rs`)
- **Java Wrapper**: Not implemented
- **Python Bindings**: Not implemented
- **Tests**: Not implemented

## Implementation Recommendations

### Rust Design
**Struct Design:**
```rust
pub struct ParameterizedOperation {
    pub algebra: ParameterizedAlgebra,
    pub name: String,
    pub symbol_name: String,
    pub set_size_exp: String,
    pub parameter_names: Vec<String>,
    pub arity_exp: String,
    pub description: String,
    pub default_value_exp: String,
    pub definition_exp: String,
}
```

**Key Design Decisions:**
1. **No Scripting Engine**: The Java implementation uses Groovy scripting which is complex to replicate in Rust. Recommend implementing a simplified parameter substitution system instead.
2. **Static Method**: `subParmValues` should be a free function, not a struct method.
3. **Error Handling**: Use `Result<Operation, String>` for `makeOp` method to handle parameter parsing errors.
4. **Generic Dispatch**: Not needed - this is a concrete data structure.

### Method Organization
- **Struct Methods**: `makeOp` (with proper error handling)
- **Free Functions**: `sub_parm_values` (static method equivalent)
- **Trait Methods**: None needed

### Java Wrapper Suitability
**Suitable for Testing**: Yes
- Concrete class with clear public interface
- Can be instantiated and tested
- Methods return concrete types that can be serialized

**Wrapper Implementation Strategy:**
- Store input parameters during construction for testing
- Expose `makeOp` method with parameter map input
- Expose `subParmValues` as static method
- Handle Groovy scripting limitations in wrapper

### Testing Strategy
**Rust Tests:**
- Test parameter substitution logic
- Test operation creation with valid parameters
- Test error handling for invalid parameters
- Mock the scripting engine functionality

**Python Tests:**
- Test parameter substitution through Python bindings
- Test operation creation with various parameter maps
- Compare with Java wrapper output

**Java Wrapper Tests:**
- Test with simple parameter maps
- Test error conditions
- Note: Full Groovy functionality may not be testable

### Critical Implementation Challenges

1. **Scripting Engine Replacement**: The Java code uses Groovy scripting engine which is not easily replicable in Rust. Recommend implementing a simple parameter substitution system.

2. **AbstractOperation Dependency**: The `makeOp` method creates an `AbstractOperation` instance, which requires the Operation and AbstractOperation classes to be implemented first.

3. **Parameter Substitution**: The `subParmValues` method is currently a stub - needs proper implementation for parameter replacement in expressions.

4. **Dynamic Operation Creation**: The current implementation creates operations with hardcoded logic (`Math.max(args[0], args[1])`). This needs to be made configurable.

### Recommended Implementation Order
1. Implement basic struct with fields
2. Implement `sub_parm_values` function for parameter substitution
3. Implement simplified `make_op` method (without full scripting support)
4. Create Java wrapper with limited functionality
5. Add comprehensive tests
6. Create Python bindings

### Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods  
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] Parameter substitution system implemented
- [ ] Operation creation works with simplified logic
