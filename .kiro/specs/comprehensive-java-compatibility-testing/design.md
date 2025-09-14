# Design Document

## Overview

This design expands the existing `test_java_compatibility.py` file to create a comprehensive test suite that verifies 100% compatibility between the Rust/Python UACalc implementation and the original Java UACalc across all major features. The design follows a modular approach where each major feature area has dedicated test classes, and a robust Java wrapper system enables systematic comparison of results.

## Architecture

### High-Level Architecture

The test suite architecture mirrors the Java UACalc package structure to ensure comprehensive coverage of all features:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Comprehensive Test Suite                     │
│                  (Mirrors org.uacalc structure)                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   org.uacalc    │  │   org.uacalc    │  │   org.uacalc    │  │
│  │   .alg Tests    │  │ .alg.conlat     │  │  .alg.op Tests  │  │
│  │                 │  │    Tests        │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   org.uacalc    │  │   org.uacalc    │  │   org.uacalc    │  │
│  │  .terms Tests   │  │   .lat Tests    │  │   .eq Tests     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   org.uacalc    │  │   org.uacalc    │  │   org.uacalc    │  │
│  │  .group Tests   │  │   .io Tests     │  │  .util Tests    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    Enhanced Java Wrapper                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Java UACalc   │  │   Rust UACalc   │  │   Test Data     │  │
│  │   (Reference)   │  │ (Implementation)│  │   (.ua files)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Test Class Structure

The test suite is organized to mirror the Java UACalc package structure, with each test class corresponding to a specific Java package:

#### Core Algebra Package Tests (org.uacalc.alg)
1. **AlgebraCompatibilityTest** - Basic Algebra interface and implementations
2. **BasicAlgebraCompatibilityTest** - BasicAlgebra class functionality  
3. **SmallAlgebraCompatibilityTest** - SmallAlgebra interface methods
4. **AlgebrasCompatibilityTest** - Algebras utility class methods
5. **FreeAlgebraCompatibilityTest** - Free algebra generation and properties
6. **HomomorphismCompatibilityTest** - Homomorphism detection and validation
7. **MalcevCompatibilityTest** - Maltsev conditions and variety theory
8. **ProductAlgebraCompatibilityTest** - Direct product construction
9. **QuotientAlgebraCompatibilityTest** - Quotient algebra construction
10. **SubalgebraCompatibilityTest** - Subalgebra generation and properties
11. **PowerAlgebraCompatibilityTest** - Power algebra construction

#### Congruence and Lattice Tests (org.uacalc.alg.conlat)
12. **CongruenceLatticeCompatibilityTest** - Congruence lattice computation
13. **PartitionCompatibilityTest** - Partition operations and properties
14. **BinaryRelationCompatibilityTest** - Binary relation operations
15. **PolymorphismsCompatibilityTest** - Polymorphism detection
16. **TypeFinderCompatibilityTest** - Tame congruence theory type finding

#### Operation Tests (org.uacalc.alg.op)
17. **OperationCompatibilityTest** - Operation interface and implementations
18. **OperationsCompatibilityTest** - Operations utility class
19. **OperationSymbolCompatibilityTest** - Operation symbol handling
20. **TermOperationCompatibilityTest** - Term-based operations

#### Term Tests (org.uacalc.terms)
21. **TermCompatibilityTest** - Term parsing, validation, and evaluation
22. **TermsCompatibilityTest** - Terms utility class methods
23. **VariableCompatibilityTest** - Variable handling and substitution
24. **TaylorCompatibilityTest** - Taylor term operations

#### Lattice Tests (org.uacalc.lat)
25. **LatticeCompatibilityTest** - Lattice interface and operations
26. **BasicLatticeCompatibilityTest** - BasicLattice implementation
27. **OrderCompatibilityTest** - Partial order operations
28. **LatticesCompatibilityTest** - Lattices utility methods

#### Equation Tests (org.uacalc.eq)
29. **EquationCompatibilityTest** - Equation representation and operations
30. **EquationsCompatibilityTest** - Equations utility methods
31. **PresentationCompatibilityTest** - Algebraic presentations

#### Group Tests (org.uacalc.group)
32. **PermutationGroupCompatibilityTest** - Permutation group operations

#### I/O Tests (org.uacalc.io)
33. **AlgebraIOCompatibilityTest** - File format reading and writing
34. **AlgebraReaderCompatibilityTest** - Algebra file parsing
35. **AlgebraWriterCompatibilityTest** - Algebra file generation

#### Utility Tests (org.uacalc.util)
36. **IntArrayCompatibilityTest** - Integer array utilities
37. **HornerCompatibilityTest** - Horner encoding/decoding
38. **SequenceGeneratorCompatibilityTest** - Sequence generation utilities

## Components and Interfaces

### Enhanced Java Wrapper

The existing `JavaWrapper.java` will be significantly expanded to support all the advanced features needed for comprehensive testing.

#### New Java Wrapper Methods

```java
// Advanced algebraic properties
public static void outputMaltsevConditions(String uaFile)
public static void outputIsomorphismCheck(String uaFile1, String uaFile2)  
public static void outputAutomorphismGroup(String uaFile)
public static void outputFreeAlgebra(String generators, String variety)
public static void outputDirectProduct(String uaFile1, String uaFile2)
public static void outputQuotientAlgebra(String uaFile, String congruenceData)

// Binary relation operations
public static void outputReflexiveClosure(String relationData)
public static void outputSymmetricClosure(String relationData)
public static void outputTransitiveClosure(String relationData)
public static void outputEquivalenceClosure(String relationData)
public static void outputRelationProperties(String relationData)

// Advanced congruence operations
public static void outputCongruenceJoin(String uaFile, String cong1Data, String cong2Data)
public static void outputCongruenceMeet(String uaFile, String cong1Data, String cong2Data)
public static void outputCongruenceOrdering(String uaFile, String cong1Data, String cong2Data)
public static void outputJoinIrreducibles(String uaFile)
public static void outputLatticeProperties(String uaFile)

// Term operations
public static void outputTermComplexity(String termString)
public static void outputTermSubstitution(String termString, String substitutionData)
public static void outputTermEquivalence(String term1, String term2, String uaFile)

// Variety and property checking
public static void outputVarietyMembership(String uaFile, String varietyType)
public static void outputAlgebraProperties(String uaFile) // Extended version
public static void outputSubalgebraGeneration(String uaFile, String generators)
```

#### Java Wrapper Data Formats

All Java wrapper methods output JSON for consistent parsing:

```json
{
  "success": true,
  "operation": "maltsev_conditions",
  "algebra_name": "C3",
  "results": {
    "congruence_modular": true,
    "congruence_distributive": false,
    "has_majority_term": false,
    "has_minority_term": true,
    "maltsev_type": "2"
  },
  "java_memory_mb": 12.5,
  "computation_time_ms": 45
}
```

### Python Test Infrastructure

#### Base Test Class

```python
class BaseCompatibilityTest(unittest.TestCase):
    """Base class providing common functionality for all compatibility tests"""
    
    @classmethod
    def setUpClass(cls):
        """Initialize Java environment and test data"""
        cls.java_jar_path = "jars/uacalc.jar"
        cls.java_wrapper_path = "scripts/JavaWrapper.java"
        cls.algebra_files = cls._discover_test_algebras()
        cls.java_available = cls._check_java_availability()
        
    def _run_java_operation(self, operation: str, *args) -> Optional[Dict[str, Any]]:
        """Generic method to run Java operations and parse JSON results"""
        
    def _compare_results(self, rust_result: Any, java_result: Dict[str, Any], 
                        operation: str, context: str = "") -> None:
        """Generic result comparison with detailed error reporting"""
        
    def _load_test_algebra(self, file_path: str) -> Any:
        """Load algebra with error handling and caching"""
```

#### Specialized Test Classes

Each test class inherits from `BaseCompatibilityTest` and implements specific test methods corresponding to Java classes:

```python
class AlgebraCompatibilityTest(BaseCompatibilityTest):
    """Test org.uacalc.alg.Algebra interface compatibility"""
    
    def test_algebra_cardinality_compatibility(self):
        """Test Algebra.cardinality() matches between Java and Rust"""
        
    def test_algebra_operations_compatibility(self):
        """Test Algebra.operations() returns identical operation lists"""
        
    def test_algebra_universe_compatibility(self):
        """Test Algebra.universe() returns identical universes"""

class BasicAlgebraCompatibilityTest(BaseCompatibilityTest):
    """Test org.uacalc.alg.BasicAlgebra class compatibility"""
    
    def test_basic_algebra_construction_compatibility(self):
        """Test BasicAlgebra constructor produces identical algebras"""
        
    def test_basic_algebra_operation_addition_compatibility(self):
        """Test adding operations to BasicAlgebra works identically"""

class MalcevCompatibilityTest(BaseCompatibilityTest):
    """Test org.uacalc.alg.Malcev class compatibility"""
    
    def test_maltsev_conditions_compatibility(self):
        """Test Maltsev condition checking matches between implementations"""
        
    def test_variety_membership_compatibility(self):
        """Test variety membership detection matches exactly"""
        
    def test_congruence_modularity_compatibility(self):
        """Test congruence modularity detection matches"""

class CongruenceLatticeCompatibilityTest(BaseCompatibilityTest):
    """Test org.uacalc.alg.conlat.CongruenceLattice class compatibility"""
    
    def test_congruence_lattice_construction_compatibility(self):
        """Test CongruenceLattice construction produces identical lattices"""
        
    def test_principal_congruence_compatibility(self):
        """Test Cg(a,b) computation produces identical partitions"""
        
    def test_join_irreducibles_compatibility(self):
        """Test join irreducible detection matches exactly"""
```

### Test Data Management

#### Algebra Test Set

The test suite uses a comprehensive set of test algebras covering different algebraic structures:

- **Small algebras**: cyclic2.ua, cyclic3.ua, ba2.ua (for exhaustive testing)
- **Medium algebras**: sym3.ua, d16.ua, m3.ua, m4.ua (for performance testing)  
- **Complex algebras**: hajilarov.ua, polin.ua (for advanced feature testing)
- **Special cases**: lat2.ua, n5.ua (for lattice-specific testing)

#### Test Case Generation

```python
class TestCaseGenerator:
    """Generates systematic test cases for comprehensive coverage"""
    
    def generate_element_pairs(self, algebra_size: int) -> List[Tuple[int, int]]:
        """Generate all element pairs for congruence testing"""
        
    def generate_operation_test_cases(self, operation: Operation) -> List[List[int]]:
        """Generate comprehensive operation evaluation test cases"""
        
    def generate_relation_test_cases(self, size: int) -> List[BinaryRelation]:
        """Generate diverse binary relations for closure testing"""
```

## Data Models

### Test Result Models

```python
@dataclass
class CompatibilityTestResult:
    """Represents the result of a single compatibility test"""
    test_name: str
    algebra_name: str
    operation: str
    rust_result: Any
    java_result: Any
    matches: bool
    error_message: Optional[str] = None
    execution_time_rust: float = 0.0
    execution_time_java: float = 0.0

@dataclass  
class TestSuiteReport:
    """Aggregated results from the entire test suite"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    compatibility_percentage: float
    failed_test_details: List[CompatibilityTestResult]
    feature_coverage: Dict[str, float]
```

### Algebra Property Models

```python
@dataclass
class AlgebraProperties:
    """Standardized representation of algebra properties"""
    name: str
    cardinality: int
    operation_count: int
    operation_symbols: List[str]
    operation_arities: List[int]
    is_idempotent: Dict[str, bool]
    is_associative: Dict[str, bool] 
    is_commutative: Dict[str, bool]
    
@dataclass
class MaltsevProperties:
    """Properties related to Maltsev conditions"""
    congruence_modular: bool
    congruence_distributive: bool
    has_majority_term: bool
    has_minority_term: bool
    maltsev_type: int
    variety_membership: List[str]
```

## Error Handling

### Java Wrapper Error Handling

The Java wrapper provides consistent error reporting:

```java
try {
    // Operation implementation
    outputSuccessResult(result);
} catch (Exception e) {
    outputErrorResult(e.getClass().getSimpleName(), e.getMessage());
}

private static void outputErrorResult(String errorType, String message) {
    System.out.println(String.format(
        "{\"success\":false,\"error_type\":\"%s\",\"error_message\":\"%s\"}", 
        errorType, message.replace("\"", "\\\"")));
}
```

### Python Error Handling

The Python test suite handles various error conditions:

```python
class CompatibilityTestError(Exception):
    """Base exception for compatibility testing errors"""
    pass

class JavaUnavailableError(CompatibilityTestError):
    """Raised when Java UACalc is not available"""
    pass

class ResultMismatchError(CompatibilityTestError):
    """Raised when Java and Rust results don't match"""
    def __init__(self, operation: str, rust_result: Any, java_result: Any):
        self.operation = operation
        self.rust_result = rust_result
        self.java_result = java_result
        super().__init__(f"Results mismatch in {operation}")
```

## Testing Strategy

### Test Coverage Strategy

1. **Exhaustive Small Algebra Testing**: Test all possible operations on small algebras (size ≤ 4)
2. **Sampling Medium Algebra Testing**: Test representative samples on medium algebras (size 5-10)
3. **Targeted Large Algebra Testing**: Test specific operations on larger algebras (size > 10)
4. **Edge Case Testing**: Test boundary conditions, empty sets, single elements
5. **Error Condition Testing**: Verify identical error handling between implementations

### Test Execution Strategy

```python
class TestExecutionStrategy:
    """Manages test execution with timeouts and resource limits"""
    
    def __init__(self):
        self.small_algebra_timeout = 30  # seconds
        self.medium_algebra_timeout = 120  # seconds  
        self.large_algebra_timeout = 300  # seconds
        
    def execute_with_timeout(self, test_func: Callable, timeout: int) -> Any:
        """Execute test function with timeout protection"""
        
    def should_skip_test(self, algebra_size: int, operation: str) -> bool:
        """Determine if test should be skipped based on complexity"""
```

### Regression Testing

The test suite includes mechanisms to detect regressions:

```python
class RegressionDetector:
    """Detects performance and correctness regressions"""
    
    def __init__(self, baseline_file: str = "test_baselines.json"):
        self.baselines = self._load_baselines(baseline_file)
        
    def check_performance_regression(self, test_name: str, 
                                   execution_time: float) -> bool:
        """Check if execution time represents a regression"""
        
    def update_baselines(self, test_results: List[CompatibilityTestResult]) -> None:
        """Update baseline measurements with new results"""
```

## Implementation Plan Integration

The design supports incremental implementation by providing:

1. **Feature Flags**: Enable/disable specific test categories during development
2. **Partial Compatibility Reporting**: Track compatibility percentage by feature area
3. **Implementation Guidance**: Test failures provide specific guidance on what needs to be implemented
4. **Verification Checkpoints**: Each implemented feature can be immediately verified against Java

### Feature Implementation Workflow

```python
class FeatureImplementationTracker:
    """Tracks implementation progress and provides guidance"""
    
    def __init__(self):
        self.feature_status = {
            'core_algebra': 'implemented',
            'congruence_lattice': 'partial', 
            'binary_relations': 'not_implemented',
            'term_operations': 'partial',
            'advanced_properties': 'not_implemented',
            'file_format': 'implemented'
        }
        
    def get_next_feature_to_implement(self) -> str:
        """Suggest next feature to implement based on dependencies"""
        
    def verify_feature_implementation(self, feature: str) -> CompatibilityReport:
        """Run targeted tests for a specific feature"""
```

This design provides a comprehensive framework for ensuring 100% compatibility between the Rust and Java implementations while supporting systematic feature-by-feature development and verification.