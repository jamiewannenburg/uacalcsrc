# Task 42: Translate `Polymorphisms`

**Java File:** `org/uacalc/alg/conlat/Polymorphisms.java`  
**Package:** `org.uacalc.alg.conlat`  
**Rust Module:** `alg::conlat::Polymorphisms`  
**Dependencies:** 3 (3 non-UI/example)  
**Estimated Public Methods:** 1

## Description
Translate the Java class `org.uacalc.alg.conlat.Polymorphisms` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Type**: Concrete class (incomplete implementation)
- **Purpose**: Calculate polymorphisms of a collection of partitions
- **Status**: **INCOMPLETE** - Only has constructor and empty main method
- **Key Issue**: The actual polymorphism calculation methods are implemented in `BasicPartition.java`, not in this class

### Method Analysis
**Current Methods (1):**
- `Polymorphisms(int arity, List<Partition> pars, boolean idempotent, int[] fixedValues)` - Constructor

**Missing Methods:**
- The class appears to be a placeholder or incomplete implementation
- Actual polymorphism methods are in `BasicPartition.java`:
  - `unaryPolymorphisms(List<Partition> pars, ProgressReport report) -> NavigableSet<IntArray>`
  - `binaryPolymorphisms(List<Partition> pars, NavigableSet<IntArray> unaryClone, ProgressReport report) -> NavigableSet<IntArray>`
  - `unaryPolymorphismsAlgebra(List<Partition> pars, ProgressReport report) -> SmallAlgebra`
  - `binaryPolymorphismsAlgebra(List<Partition> pars, ProgressReport report) -> SmallAlgebra`

### Dependencies Analysis

**Correctly Identified:**
- `org.uacalc.alg.conlat.Partition` - Used in constructor parameter and field
- `org.uacalc.alg.op.Operation` - Used in partialOp field
- `org.uacalc.util.IntArray` - Used in graph field

**Dependencies are accurate** - All three dependencies are correctly identified.

## Rust Implementation Analysis

### Current Implementation Status: ❌ NOT STARTED
- **Rust Construct**: Should be a struct
- **Design Pattern**: Concrete struct with constructor
- **Error Handling**: Needs proper Result/Option usage
- **Memory Management**: Uses `Vec<Partition>` for partitions, `Option<Operation>` for partialOp

### Implementation Recommendations

**Struct Design:**
```rust
pub struct Polymorphisms {
    pub pars: Vec<Partition>,
    pub alg_size: usize,
    pub arity: usize,
    pub idempotent: bool,
    pub fixed_values: Option<Vec<i32>>,
    pub partial_op: Option<Operation>,
    pub partial_op_table: Option<Vec<i32>>,
    pub table_size: usize,
    pub graph: Option<HashMap<IntArray, HashMap<IntArray, Partition>>>,
}
```

**Constructor Design:**
```rust
impl Polymorphisms {
    pub fn new_safe(arity: usize, pars: Vec<Partition>, idempotent: bool, fixed_values: Option<Vec<i32>>) -> Result<Self, String> {
        if pars.is_empty() {
            return Err("Partitions list cannot be empty".to_string());
        }
        let alg_size = pars[0].universe_size();
        let table_size = alg_size.pow(arity as u32);
        Ok(Self {
            pars,
            alg_size,
            arity,
            idempotent,
            fixed_values,
            partial_op: None,
            partial_op_table: None,
            table_size,
            graph: None,
        })
    }
    
    pub fn new(arity: usize, pars: Vec<Partition>, idempotent: bool, fixed_values: Option<Vec<i32>>) -> Self {
        Self::new_safe(arity, pars, idempotent, fixed_values).unwrap()
    }
}
```

**Key Implementation Points:**
- Use `Vec<Partition>` instead of `List<Partition>`
- Use `Option<T>` for nullable fields
- Use `HashMap` instead of `TreeMap` for graph
- Implement proper error handling with `Result<T, String>`
- Add validation for empty partitions list

## Python Bindings Analysis

### Current Implementation Status: ❌ NOT STARTED
- **Python Class**: `Polymorphisms` (clean export name)
- **PyO3 Integration**: Needs proper error handling
- **Constructor**: Should accept Python lists and convert to Rust types

### Implementation Recommendations

**Python Binding Design:**
```rust
#[pyclass]
pub struct PyPolymorphisms {
    inner: uacalc::alg::conlat::Polymorphisms,
}

#[pymethods]
impl PyPolymorphisms {
    #[new]
    #[pyo3(signature = (arity, pars, idempotent, fixed_values=None))]
    fn new(arity: usize, pars: Vec<PyPartition>, idempotent: bool, fixed_values: Option<Vec<i32>>) -> PyResult<Self> {
        let rust_pars: Vec<Partition> = pars.into_iter().map(|p| p.inner).collect();
        match uacalc::alg::conlat::Polymorphisms::new_safe(arity, rust_pars, idempotent, fixed_values) {
            Ok(inner) => Ok(PyPolymorphisms { inner }),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
}
```

## Java Wrapper Analysis

### Current Implementation Status: ❌ NOT STARTED
- **Wrapper Class**: `PolymorphismsWrapper`
- **Suitability**: **SUITABLE** - Concrete class with constructor
- **Testing Strategy**: Test constructor with various parameter combinations

### Implementation Recommendations

**Java Wrapper Design:**
```java
public class PolymorphismsWrapper extends WrapperBase {
    public static void main(String[] args) {
        PolymorphismsWrapper wrapper = new PolymorphismsWrapper();
        try {
            wrapper.run(args);
        } catch (Exception e) {
            wrapper.handleError("Polymorphisms wrapper failed", e);
        }
    }
    
    @Override
    public void run(String[] args) throws Exception {
        // Implementation for constructor testing
    }
    
    private void testConstructor(String[] args) throws Exception {
        int arity = getIntArg(args, "arity", 1);
        List<Partition> pars = getPartitionListArg(args, "pars");
        boolean idempotent = getBoolArg(args, "idempotent", false);
        int[] fixedValues = getIntArrayArg(args, "fixedValues", null);
        
        Polymorphisms poly = new Polymorphisms(arity, pars, idempotent, fixedValues);
        
        handleSuccess(json!({
            "command": "constructor",
            "arity": arity,
            "pars_count": pars.size(),
            "idempotent": idempotent,
            "fixed_values": fixedValues,
            "alg_size": poly.algSize,
            "table_size": poly.tableSize,
            "status": "success"
        }));
    }
}
```

## Testing Strategy

### Rust Tests
- Test constructor with valid parameters
- Test constructor with invalid parameters (empty partitions)
- Test constructor with different arity values
- Test constructor with different idempotent values

### Python Tests
- Test constructor through Python bindings
- Test error handling for invalid parameters
- Compare results with Java wrapper

## Critical Issues and Recommendations

### Issue 1: Incomplete Implementation
**Problem**: The Java class is incomplete - it only has a constructor and empty main method.
**Recommendation**: 
1. **Option A**: Implement the missing polymorphism methods in the Rust version
2. **Option B**: Mark this task as incomplete and focus on the actual implementation in `BasicPartition.java`
3. **Option C**: Create a complete implementation based on the methods in `BasicPartition.java`

### Issue 2: Missing Core Functionality
**Problem**: The class doesn't have the actual polymorphism calculation methods.
**Recommendation**: Implement the core methods:
- `calculate_unary_polymorphisms() -> Result<Vec<IntArray>, String>`
- `calculate_binary_polymorphisms() -> Result<Vec<IntArray>, String>`
- `make_graph() -> Result<(), String>`

### Issue 3: Dependencies on Unimplemented Classes
**Problem**: Depends on `Partition`, `Operation`, and `IntArray` which may not be fully implemented.
**Recommendation**: Verify all dependencies are available before implementing.

## Implementation Priority

**HIGH PRIORITY**: This class appears to be incomplete and may need significant work to be functional. Consider:
1. Implementing the missing methods based on `BasicPartition.java`
2. Creating a complete implementation from scratch
3. Or marking as incomplete until the Java implementation is finished

## Current Implementation Status: ❌ NOT STARTED

### Implementation Status Summary
- **Rust Implementation**: ❌ NOT STARTED - No implementation found
- **Python Bindings**: ❌ NOT STARTED - No bindings found  
- **Java Wrapper**: ❌ NOT STARTED - No wrapper found
- **Tests**: ❌ NOT STARTED - No tests found
- **Dependencies**: ✅ READY - All dependencies (Partition, Operation, IntArray) are implemented

### Dependency Analysis
**Ready Dependencies:**
- ✅ `Partition` - Fully implemented in `src/alg/conlat/partition.rs`
- ✅ `Operation` - Implemented in `src/alg/op/` (OperationSymbol, etc.)
- ✅ `IntArray` - Implemented in `src/util/int_array.rs`

**Blocking Dependencies:** None - All required dependencies are available

### Critical Implementation Notes
1. **Java Class is Incomplete**: The `Polymorphisms.java` class only contains a constructor and empty main method
2. **Core Methods Missing**: The actual polymorphism calculation methods are implemented in `BasicPartition.java`:
   - `unaryPolymorphisms(List<Partition> pars, ProgressReport report) -> NavigableSet<IntArray>`
   - `binaryPolymorphisms(List<Partition> pars, NavigableSet<IntArray> unaryClone, ProgressReport report) -> NavigableSet<IntArray>`
   - `unaryPolymorphismsAlgebra(List<Partition> pars, ProgressReport report) -> SmallAlgebra`
   - `binaryPolymorphismsAlgebra(List<Partition> pars, ProgressReport report) -> SmallAlgebra`

### Implementation Strategy
**Option A: Complete Implementation**
- Implement the missing polymorphism methods in the Rust version
- Create a complete, functional implementation based on `BasicPartition.java`

**Option B: Minimal Implementation**  
- Only implement the constructor as specified in the Java class
- Mark as incomplete until Java implementation is finished

**Option C: Hybrid Approach**
- Implement constructor + basic structure
- Add placeholder methods for future implementation

## Acceptance Criteria
- [ ] Constructor translated to Rust with proper error handling
- [ ] Python bindings expose constructor
- [ ] Java CLI wrapper created for constructor testing
- [ ] Rust tests pass for constructor
- [ ] Python tests pass and match Java output
- [ ] Code compiles without warnings
- [ ] Documentation complete
- [ ] **CRITICAL**: Decide on approach for missing methods
- [ ] **NEW**: Implement core polymorphism calculation methods (if Option A chosen)
- [ ] **NEW**: Add comprehensive tests for polymorphism calculations
