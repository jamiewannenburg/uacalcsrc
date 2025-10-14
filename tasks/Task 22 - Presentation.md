# Task 22: Translate `Presentation`

**Java File:** `org/uacalc/eq/Presentation.java`  
**Package:** `org.uacalc.eq`  
**Rust Module:** `eq::Presentation`  
**Dependencies:** 2 (2 non-UI/example)  
**Estimated Public Methods:** 3

## Description
Translate the Java class `org.uacalc.eq.Presentation` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Type**: Concrete class (data container)
- **Pattern**: Simple data structure with constructor and getters
- **Complexity**: Low - basic data container

### Public Methods
1. `Presentation(List<Variable> vars, List<Equation> rels)` - Constructor
2. `List<Variable> getVariables()` - Getter for variables
3. `List<Equation> getRelations()` - Getter for relations

### Dependencies Analysis
**CORRECTED DEPENDENCIES** (original task was incomplete):
- `org.uacalc.terms.Variable` (interface)
- `org.uacalc.eq.Equation` (concrete class)

**Dependency Status**:
- `Variable` (Task 40): ❌ Not implemented - all acceptance criteria unchecked
- `Equation` (Task 58): ❌ Not implemented - all acceptance criteria unchecked

## Rust Implementation Recommendations

### Design Pattern
- **Rust Construct**: `struct` (data container)
- **Fields**: Two public fields for direct access
- **Generics**: Not needed - simple data structure
- **Error Handling**: Constructor should validate inputs

### Struct Design
```rust
pub struct Presentation {
    pub variables: Vec<Variable>,
    pub relations: Vec<Equation>,
}
```

### Method Organization
- **Constructor**: `new(variables: Vec<Variable>, relations: Vec<Equation>) -> Self`
- **Getters**: Direct field access (Rust idiom) or keep getters for API consistency
- **Validation**: Constructor should validate non-null inputs

### Implementation Strategy
1. **Simple Data Structure**: No complex logic, just data storage
2. **Direct Field Access**: Use public fields following Rust conventions
3. **Input Validation**: Constructor should validate inputs are not null/empty if required
4. **Clone Support**: Implement `Clone` for easy copying

## Java Wrapper Suitability
- **Suitable**: ✅ Yes - concrete class with simple constructor and getters
- **Testing Strategy**: Create wrapper with constructor and getter commands
- **Commands Needed**:
  - `create` - Create new Presentation with variables and relations
  - `get_variables` - Get variables list
  - `get_relations` - Get relations list

## Implementation Recommendations

### 1. Dependency Resolution
**CRITICAL**: This task cannot be completed until dependencies are implemented:
- Must wait for Task 40 (Variable) to be completed
- Must wait for Task 58 (Equation) to be completed
- Both dependencies show no progress (all acceptance criteria unchecked)

### 2. Rust Implementation
- Simple struct with two public fields
- Implement `Debug`, `Clone`, `PartialEq`, `Eq` traits
- Constructor with input validation
- No complex error handling needed

### 3. Python Bindings
- Expose struct fields directly
- Implement `__str__` and `__repr__` methods
- Simple constructor and getter methods

### 4. Testing Strategy
- Test constructor with valid inputs
- Test getters return correct data
- Test with empty lists
- Test with single item lists
- Compare against Java wrapper output

## Updated Dependencies
This class depends on:
- `org.uacalc.terms.Variable` (Task 40 - NOT IMPLEMENTED)
- `org.uacalc.eq.Equation` (Task 58 - NOT IMPLEMENTED)

## Implementation Steps

1. **Wait for Dependencies** - Cannot proceed until Variable and Equation are implemented
2. **Implement Rust Struct** - Simple data container with validation
3. **Create Python Bindings** - Direct field access and basic methods
4. **Create Java Wrapper** - Constructor and getter commands
5. **Write Tests** - Basic functionality and edge cases
6. **Verification** - Ensure all tests pass and outputs match

## Acceptance Criteria
- [ ] All public methods translated to Rust
- [ ] Python bindings expose all public methods  
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] **Dependencies implemented** (Variable and Equation)
