# Task 74: NonVariableTerm Analysis and Implementation Recommendations

## Java Class Analysis

**Java File:** `org/uacalc/terms/NonVariableTerm.java`  
**Package:** `org.uacalc.terms`  
**Class Type:** Concrete class implementing `Term` interface  
**Dependencies:** 8 (8 non-UI/example)  
**Estimated Public Methods:** ~29

### Java Class Structure
- **Main Class**: `NonVariableTerm` - concrete class implementing `Term` interface
- **Key Fields**: 
  - `leadingOperationSymbol: OperationSymbol` - the operation symbol at the root
  - `children: List<Term>` - list of child terms
- **Static Constants**: `LEFT_PAR`, `RIGHT_PAR`, `COMMA` - string constants for formatting
- **Key Methods**: Term evaluation, interpretation, substitution, string formatting

### Key Java Methods (29 total)
1. **Constructor**: `NonVariableTerm(OperationSymbol opSym, List<Term> children)`
2. **Static Factory**: `makeConstantTerm(OperationSymbol sym)` - creates constant terms
3. **Core Methods**: `isaVariable()`, `leadingOperationSymbol()`, `getChildren()`
4. **Evaluation**: `eval(Algebra alg, Map map)`, `intEval(Algebra alg, Map<Variable,Integer> map)`
5. **Interpretation**: `interpretation(SmallAlgebra alg, List<Variable> varlist, boolean useAll)`
6. **Term Operations**: `getVariableList()`, `getOperationSymbols()`, `substitute(Map<Variable,Term> map)`
7. **Properties**: `length()`, `depth()`
8. **String Operations**: `toString()`, `writeStringBuffer(StringBuffer sb)`
9. **Object Methods**: `equals(Object obj)`, `hashCode()`

## Dependency Analysis

### Dependencies Found
- **org.uacalc.alg.*** - Used for Algebra, SmallAlgebra types in method signatures
- **org.uacalc.alg.op.AbstractOperation** - Used in interpretation() method
- **org.uacalc.alg.op.Operation** - Used in eval() and intEval() methods
- **org.uacalc.alg.op.OperationSymbol** - Core field type and method parameter
- **org.uacalc.alg.op.Operations** - Used in interpretation() method
- **org.uacalc.alg.op.TermOperation** - Used in interpretation() method
- **org.uacalc.alg.op.TermOperationImp** - Used in interpretation() method
- **org.uacalc.util.*** - Used for utility classes (Horner, etc.)

### Dependencies Correct
❌ **NO** - Current task lists 8 dependencies, but analysis shows they are correct:
- ✅ `org.uacalc.alg` - Used for Algebra, SmallAlgebra types
- ✅ `org.uacalc.alg.op.AbstractOperation` - Used in interpretation() method
- ✅ `org.uacalc.alg.op.Operation` - Used in eval() and intEval() methods
- ✅ `org.uacalc.alg.op.OperationSymbol` - Core field type
- ✅ `org.uacalc.alg.op.Operations` - Used in interpretation() method
- ✅ `org.uacalc.alg.op.TermOperation` - Used in interpretation() method
- ✅ `org.uacalc.alg.op.TermOperationImp` - Used in interpretation() method
- ✅ `org.uacalc.util` - Used for utility classes

### Usage Patterns in Codebase
- **Term Construction**: Used extensively throughout codebase for building complex terms
- **Algebra Operations**: Used in algebra evaluation, interpretation, and term operations
- **Equation Generation**: Used in equation creation and manipulation
- **Term Manipulation**: Used in substitution, flattening, and canonicalization
- **Algebra Closures**: Used in closure computations and term mapping

## Rust Implementation Analysis

### Current Implementation Status
❌ **NOT IMPLEMENTED** - Only placeholder struct exists in `src/terms/mod.rs`

### Dependencies Status
- **OperationSymbol**: ✅ **IMPLEMENTED** (Task 1 - Complete)
- **Operation**: ❌ **NOT IMPLEMENTED** (Task 50 - Incomplete)
- **AbstractOperation**: ❌ **NOT IMPLEMENTED** (Task 12 - Incomplete)
- **Operations**: ❌ **NOT IMPLEMENTED** (Task 50 - Incomplete)
- **TermOperation**: ❌ **NOT IMPLEMENTED** (Task 33 - Incomplete)
- **TermOperationImp**: ❌ **NOT IMPLEMENTED** (Task 33 - Incomplete)
- **Algebra**: ❌ **NOT IMPLEMENTED** (Task 55 - Incomplete)
- **SmallAlgebra**: ❌ **NOT IMPLEMENTED** (Task 41 - Incomplete)
- **Variable**: ❌ **NOT IMPLEMENTED** (Task 40 - Incomplete)
- **Term**: ❌ **NOT IMPLEMENTED** (Task 56 - Incomplete)
- **util**: ❌ **NOT IMPLEMENTED** (Various utility tasks)

### Rust Implementation Recommendations

#### 1. Rust Construct Design
- **Java Class Type**: Concrete class implementing interface
- **Rust Construct**: `struct NonVariableTerm` (appropriate for concrete class)
- **Key Design Decisions**:
  - Use `Vec<Term>` for children (Rust equivalent of `List<Term>`)
  - Use `Box<dyn Term>` for trait objects if needed
  - Implement `Term` trait for the struct
  - Use `Result<T, String>` for error handling

#### 2. Method Organization
- **Trait Methods**: Implement `Term` trait with all required methods
- **Struct Methods**: Implement constructor, factory methods, and utility methods
- **Static Methods**: Convert to associated functions or module-level functions
- **Error Handling**: Use `Result<T, String>` for methods that can fail

#### 3. Generic vs Dynamic Dispatch
- **Use Dynamic Dispatch**: For `Term` trait objects in children list
- **Use Generics**: For type-safe method signatures where possible
- **Trait Objects**: Use `Box<dyn Term>` for children list to allow different term types

#### 4. Key Implementation Challenges
- **Circular Dependencies**: `Term` interface depends on `NonVariableTerm`, but `NonVariableTerm` implements `Term`
- **Complex Evaluation**: Methods like `eval()` and `intEval()` require complex algebra operations
- **Interpretation Logic**: The `interpretation()` method creates complex operation objects
- **String Formatting**: The `writeStringBuffer()` method requires careful string building

#### 5. Java Wrapper Suitability
✅ **SUITABLE** - This is a concrete class with many public methods that can be easily tested through CLI:
- **Constructor Testing**: Can test constructor with various parameters
- **Method Testing**: Can test all 29 public methods with different inputs
- **Evaluation Testing**: Can test evaluation methods with mock algebras
- **String Testing**: Can test string formatting and output methods

### Testing Strategy Recommendations

#### 1. Rust Tests
- **Unit Tests**: Test each method individually with various inputs
- **Integration Tests**: Test complex scenarios like term evaluation and interpretation
- **Error Tests**: Test error conditions and edge cases
- **Performance Tests**: Test with large terms and deep nesting

#### 2. Python Tests
- **API Tests**: Test all methods through Python bindings
- **Compatibility Tests**: Compare results with Java implementation
- **Error Handling Tests**: Test error conditions in Python context

#### 3. Java Wrapper Tests
- **Method Coverage**: Test all 29 public methods through CLI
- **Parameter Testing**: Test with various parameter combinations
- **Output Validation**: Verify output format and correctness

### Implementation Priority
**BLOCKED** - Cannot proceed until dependencies are implemented:
1. **Term** interface (Task 56) - Required for trait implementation
2. **Variable** (Task 40) - Required for term operations
3. **Operation** (Task 50) - Required for evaluation methods
4. **Algebra** (Task 55) - Required for evaluation methods
5. **SmallAlgebra** (Task 41) - Required for interpretation methods
6. **AbstractOperation** (Task 12) - Required for interpretation methods
7. **Operations** (Task 50) - Required for interpretation methods
8. **TermOperation** (Task 33) - Required for interpretation methods
9. **TermOperationImp** (Task 33) - Required for interpretation methods
10. **util** utilities - Required for various utility methods

### Acceptance Criteria
- [ ] All dependencies implemented and available
- [ ] All 29 public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] Term evaluation works correctly with all algebra types
- [ ] Term interpretation works correctly with all algebra types
- [ ] String formatting matches Java output exactly
- [ ] Error handling works correctly for all edge cases
