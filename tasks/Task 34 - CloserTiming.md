# Task 34: Translate `CloserTiming`

**Java File:** `org/uacalc/alg/CloserTiming.java`  
**Package:** `org.uacalc.alg`  
**Rust Module:** `alg::CloserTiming`  
**Dependencies:** 2 (1 non-UI/example)  
**Estimated Public Methods:** 4

## Description
Translate the Java class `org.uacalc.alg.CloserTiming` to Rust with Python bindings.

## Java Class Analysis

### Class Type
- **Type**: Concrete class
- **Purpose**: Timing information holder for UI progress reporting during closure operations
- **Thread Safety**: Uses AtomicInteger and AtomicLong for thread safety (partial)

### Public Methods (4)
1. `CloserTiming(BigProductAlgebra algebra, ProgressReport report)` - Constructor
2. `updatePass(int size)` - Updates pass information and resets counters
3. `incrementApps()` - Increments application counters and updates timing estimates
4. `incrementNextPassSize()` - Increments next pass size counter

### Dependencies Analysis
**Direct Dependencies:**
- `org.uacalc.alg.BigProductAlgebra` - For algebra operations and factor count
- `org.uacalc.ui.tm.ProgressReport` - For UI progress reporting (UI component)
- `java.util.concurrent.atomic.AtomicInteger` - Thread-safe integer operations
- `java.util.concurrent.atomic.AtomicLong` - Thread-safe long operations
- `java.math.BigInteger` - For large number calculations

**Indirect Dependencies:**
- `org.uacalc.alg.op.*` - Through BigProductAlgebra operations
- Standard Java collections and math utilities

### Usage Patterns
- Used exclusively by `Closer` class for timing calculations during closure operations
- Instantiated when `ProgressReport` is not null
- Called during closure passes to track progress and estimate remaining time
- Thread-safe operations for concurrent closure algorithms

## Rust Implementation Recommendations

### Rust Construct Design
- **Primary**: `struct CloserTiming`
- **Traits**: No traits needed (concrete implementation)
- **Generics**: No generics needed
- **Error Handling**: Use `Result<(), String>` for fallible operations

### Struct Design
```rust
pub struct CloserTiming {
    report: Option<Box<dyn ProgressReport>>,  // Optional UI component
    projs: u64,                              // Number of factors
    pass: u32,                               // Current pass number
    next_pass_size: Arc<AtomicI32>,          // Thread-safe next pass size
    curr_pass_size: u32,                     // Current pass size
    last_pass_size: u32,                     // Previous pass size
    arities: Vec<u32>,                       // Operation arities
    apps_needed: u64,                        // Applications needed
    apps_this_pass: u64,                     // Applications this pass
    local_apps: Arc<AtomicI64>,              // Thread-safe local apps counter
    pass_start_time: Option<Instant>,        // Pass start time
    ms_per_app: f64,                         // Milliseconds per application
    update_time: bool,                       // Whether to update time estimates
    at_beginning: bool,                      // Whether at beginning of pass
    start_nano_time: Option<Instant>,        // Start time for calculations
    real_init_count: u64,                    // Real initialization count
}
```

### Method Organization
- **Constructor**: `new(algebra: &BigProductAlgebra, report: Option<Box<dyn ProgressReport>>) -> Self`
- **Public Methods**: All 4 public methods as struct methods
- **Private Methods**: Helper methods for calculations and time formatting

### Thread Safety Considerations
- Use `Arc<AtomicI32>` and `Arc<AtomicI64>` for thread-safe counters
- Use `std::sync::Mutex` for mutable state that needs synchronization
- Consider using `std::time::Instant` for precise timing

### Error Handling Strategy
- Constructor: `Result<Self, String>` for validation errors
- Methods: `Result<(), String>` for fallible operations
- Use `Option` for nullable fields instead of null pointers

## Java Wrapper Suitability
**Suitable for Java Wrapper**: Yes
- Concrete class with clear public interface
- Can be instantiated and tested independently
- Methods have simple parameters and return types
- No complex state dependencies

### Java Wrapper Design
- Create `CloserTimingWrapper` extending `WrapperBase`
- Expose all 4 public methods through CLI commands
- Handle `BigProductAlgebra` parameter through JSON serialization
- Mock `ProgressReport` for testing purposes

## Testing Strategy

### Rust Tests
- Unit tests for all public methods
- Test timing calculations with known inputs
- Test thread safety with concurrent access
- Test edge cases (zero operations, large numbers)
- Test error conditions and validation

### Python Tests
- Test all methods through Python bindings
- Compare timing calculations with Java implementation
- Test with various algebra configurations
- Verify thread safety in Python context

### Java Wrapper Tests
- Test constructor with various algebra configurations
- Test timing methods with different pass sizes
- Test concurrent access patterns
- Verify timing accuracy against expected values

## Implementation Priority
**Priority**: Medium
- Required for closure operations timing
- Used by `Closer` class (high dependency)
- Relatively simple implementation
- Good candidate for early implementation

## Dependencies Status
- `BigProductAlgebra`: Not yet implemented (Task 78)
- `ProgressReport`: UI component (excluded from core library)
- `org.uacalc.alg.op.*`: Various operation classes (multiple tasks)

## Recommendations
1. **Mock ProgressReport**: Create a mock implementation for testing since it's a UI component
2. **Thread Safety**: Implement proper thread safety using Rust's ownership system
3. **Timing Precision**: Use `std::time::Instant` for high-precision timing
4. **Error Handling**: Implement comprehensive error handling for edge cases
5. **Testing**: Focus on timing accuracy and thread safety in tests

## Acceptance Criteria
- [ ] All 4 public methods translated to Rust
- [ ] Python bindings expose all public methods
- [ ] Java CLI wrapper created with all public methods
- [ ] Rust tests pass with timeouts enabled
- [ ] Python tests pass and match Java output
- [ ] Thread safety verified in concurrent scenarios
- [ ] Timing calculations match Java implementation exactly
- [ ] Code compiles without warnings
- [ ] Documentation complete
