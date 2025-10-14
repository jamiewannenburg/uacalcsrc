# UACalc Rust/Python Translation Plan

## Task 39: Translate `QuotientElement`

**Java File:** `org/uacalc/alg/QuotientElement.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::QuotientElement`  
**Dependencies:** 3 (3 non-UI/example)  
**Estimated Public Methods:** 6

### Description
Translate the Java class `org.uacalc.alg.QuotientElement` to Rust with Python bindings.

### Java Class Analysis

#### Class Type
- **Type**: Concrete class (not interface or abstract)
- **Purpose**: Represents an element in a quotient algebra
- **Key Fields**: 
  - `protected final QuotientAlgebra alg` - The quotient algebra this element belongs to
  - `protected final int index` - The index in the quotient algebra (not super algebra)

#### Public Methods (6 total)
1. `QuotientElement(QuotientAlgebra alg, int index)` - Constructor
2. `QuotientAlgebra getAlgebra()` - Returns the quotient algebra
3. `SmallAlgebra superAlgebra()` - Returns the super algebra via `alg.superAlgebra()`
4. `Partition getCongruence()` - Returns the congruence via `alg.getCongruence()`
5. `int getIndex()` - Returns the index in quotient algebra
6. `int getIndexInSuperAlgebra()` - Returns index in super algebra via `getCongruence().representatives()[index]`
7. `String toString()` - String representation as `superAlgebra().getElement(getIndexInSuperAlgebra()).toString() + "/" + getCongruence().toString()`

#### Dependencies Analysis
**Corrected Dependencies:**
- `org.uacalc.alg.QuotientAlgebra` - Direct dependency (field type)
- `org.uacalc.alg.SmallAlgebra` - Indirect dependency (via `superAlgebra()` method)
- `org.uacalc.alg.conlat.Partition` - Indirect dependency (via `getCongruence()` method)

**Dependencies Status:**
- ❌ `QuotientAlgebra` - Not yet implemented (Task 77)
- ❌ `SmallAlgebra` - Not yet implemented (Task 41) 
- ✅ `Partition` - Implemented (Task 5 - completed)

### Rust Implementation Recommendations

#### Rust Construct Design
- **Rust Type**: `struct QuotientElement` in `src/alg/quotient_element.rs`
- **Design Pattern**: Simple data holder struct with methods
- **Fields**: 
  - `pub alg: QuotientAlgebra` - Reference to quotient algebra
  - `pub index: usize` - Index in quotient algebra

#### Method Organization
- **Constructor**: `new(alg: QuotientAlgebra, index: usize) -> Self`
- **Getter Methods**: All public methods become struct methods
- **Display Trait**: Implement `Display` trait for `toString()` equivalent
- **Error Handling**: Use `Result<T, String>` for methods that can fail

#### Generic vs Dynamic Dispatch
- **Recommendation**: Use concrete types (not generics)
- **Reasoning**: QuotientElement is tightly coupled to QuotientAlgebra and doesn't need generics
- **Lifetime Management**: Use owned `QuotientAlgebra` or `Rc<QuotientAlgebra>` for shared ownership

#### Implementation Dependencies
**Blocking Dependencies:**
- `QuotientAlgebra` must be implemented first (Task 77)
- `SmallAlgebra` must be implemented first (Task 41)

**Non-blocking Dependencies:**
- `Partition` is already available

### Java Wrapper Suitability
- **Suitable**: ✅ Yes - Concrete class with simple methods
- **Reasoning**: 
  - Concrete class can be instantiated for testing
  - All methods are simple getters/constructors
  - No complex state management required
- **Wrapper Location**: `java_wrapper/src/alg/QuotientElementWrapper.java`
- **Test Commands**: Constructor, all getter methods, toString method

### Testing Strategy
- **Rust Tests**: Test all 6 public methods with `compare_with_java!` macro
- **Python Tests**: Test through Python bindings comparing against Java wrapper
- **Java Wrapper**: Create CLI commands for all methods
- **Test Data**: Use QuotientAlgebra instances with known congruences

### Implementation Recommendations

#### 1. Rust Struct Design
```rust
pub struct QuotientElement {
    pub alg: QuotientAlgebra,
    pub index: usize,
}

impl QuotientElement {
    pub fn new(alg: QuotientAlgebra, index: usize) -> Self {
        Self { alg, index }
    }
    
    pub fn get_algebra(&self) -> &QuotientAlgebra {
        &self.alg
    }
    
    pub fn super_algebra(&self) -> &SmallAlgebra {
        self.alg.super_algebra()
    }
    
    pub fn get_congruence(&self) -> &Partition {
        self.alg.get_congruence()
    }
    
    pub fn get_index(&self) -> usize {
        self.index
    }
    
    pub fn get_index_in_super_algebra(&self) -> usize {
        self.get_congruence().representatives()[self.index]
    }
}

impl Display for QuotientElement {
    fn fmt(&self, f: &mut Formatter<'_>) -> Result {
        let elem = self.super_algebra().get_element(self.get_index_in_super_algebra());
        write!(f, "{}/{}", elem, self.get_congruence())
    }
}
```

#### 2. Python Bindings
- Use `PyQuotientElement` as internal struct name
- Export clean `QuotientElement` name to Python
- Implement `__str__`, `__repr__`, `__eq__` magic methods
- Use `PyResult<T>` for error handling

#### 3. Java Wrapper Commands
- `new` - Constructor with alg and index parameters
- `getAlgebra` - Get quotient algebra
- `superAlgebra` - Get super algebra
- `getCongruence` - Get congruence
- `getIndex` - Get index
- `getIndexInSuperAlgebra` - Get index in super algebra
- `toString` - String representation

### Blocking Issues
1. **Cannot implement until dependencies are ready**: QuotientAlgebra and SmallAlgebra must be implemented first
2. **Task ordering**: This task should be moved after Tasks 41 and 77 are completed
3. **Dependency count incorrect**: Should be 3 dependencies, not 2

### Acceptance Criteria
- [ ] All 6 public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] Dependencies (QuotientAlgebra, SmallAlgebra) implemented first
