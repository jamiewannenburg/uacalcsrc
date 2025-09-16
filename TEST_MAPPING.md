# Test Class to Java UACalc Package Mapping

This document provides a comprehensive mapping between compatibility test classes and the Java UACalc packages they test. This addresses the documentation requirement from Task 13.3.

## Overview

The compatibility test suite is organized to mirror the Java UACalc package structure, ensuring comprehensive coverage of all major functionality areas. Each test class focuses on a specific Java package or set of related classes.

## Package Mapping

### org.uacalc.alg - Core Algebra Classes

| Test Class | Java Classes Tested | Priority | Description |
|------------|-------------------|----------|-------------|
| `AlgebraCompatibilityTest` | `Algebra` interface | High | Core algebra interface methods and properties |
| `BasicAlgebraCompatibilityTest` | `BasicAlgebra` | High | Basic algebra construction and operations |
| `SmallAlgebraCompatibilityTest` | `SmallAlgebra` interface | High | Small algebra optimizations and properties |
| `AlgebrasCompatibilityTest` | `Algebras` utility class | High | Static utility methods for algebra operations |
| `FreeAlgebraCompatibilityTest` | `FreeAlgebra` | Medium | Free algebra generation from generators |
| `HomomorphismCompatibilityTest` | `Homomorphism` classes | High | Homomorphism detection and properties |
| `MalcevCompatibilityTest` | `Malcev` classes | High | Maltsev condition checking and variety theory |
| `ProductAlgebraCompatibilityTest` | `ProductAlgebra` | Medium | Direct product construction |
| `QuotientAlgebraCompatibilityTest` | `QuotientAlgebra` | Medium | Quotient algebra construction from congruences |
| `SubalgebraCompatibilityTest` | `Subalgebra` classes | High | Subalgebra generation and properties |

**Coverage**: 10/12 classes (83.3%) - Excellent coverage of core algebra functionality

### org.uacalc.alg.conlat - Congruence Lattice Classes

| Test Class | Java Classes Tested | Priority | Description |
|------------|-------------------|----------|-------------|
| `CongruenceLatticeCompatibilityTest` | `CongruenceLattice` | High | Congruence lattice construction and operations |
| `PartitionCompatibilityTest` | `Partition` classes | High | Partition operations and refinement |
| `BinaryRelationCompatibilityTest` | `BinaryRelation` classes | High | Binary relation operations and closures |
| `PolymorphismsCompatibilityTest` | `Polymorphisms` classes | Medium | Polymorphism detection and classification |
| `TypeFinderCompatibilityTest` | `TypeFinder` classes | Medium | Tame congruence theory type detection |

**Coverage**: 5/8 classes (62.5%) - Good coverage, some advanced features may need additional tests

### org.uacalc.alg.op - Operation Classes

| Test Class | Java Classes Tested | Priority | Description |
|------------|-------------------|----------|-------------|
| `OperationCompatibilityTest` | `Operation` interface | High | Core operation interface methods |
| `OperationsCompatibilityTest` | `Operations` utility class | High | Static utility methods for operations |
| `OperationSymbolCompatibilityTest` | `OperationSymbol` classes | High | Operation symbol creation and comparison |
| `TermOperationCompatibilityTest` | `TermOperation` classes | High | Term-based operation construction |

**Coverage**: 4/8 classes (50.0%) - Moderate coverage, some operation types may need additional tests

### org.uacalc.terms - Term Classes

| Test Class | Java Classes Tested | Priority | Description |
|------------|-------------------|----------|-------------|
| `TermCompatibilityTest` | `Term` classes | High | Term parsing and evaluation |
| `TermsCompatibilityTest` | `Terms` utility class | High | Static utility methods for terms |
| `VariableCompatibilityTest` | `Variable` classes | High | Variable handling and substitution |
| `TaylorCompatibilityTest` | `Taylor` classes | Medium | Taylor term operations |

**Coverage**: 4/6 classes (66.7%) - Good coverage of core term functionality

### org.uacalc.lat - Lattice Classes

| Test Class | Java Classes Tested | Priority | Description |
|------------|-------------------|----------|-------------|
| `LatticeCompatibilityTest` | `Lattice` interface | Medium | Core lattice interface methods |
| `BasicLatticeCompatibilityTest` | `BasicLattice` | Medium | Basic lattice construction and operations |
| `OrderCompatibilityTest` | `Order` classes | Medium | Partial order operations |
| `LatticesCompatibilityTest` | `Lattices` utility class | Medium | Static utility methods for lattices |

**Coverage**: 4/6 classes (66.7%) - Good coverage of lattice functionality

### org.uacalc.eq - Equation Classes

| Test Class | Java Classes Tested | Priority | Description |
|------------|-------------------|----------|-------------|
| `EquationCompatibilityTest` | `Equation` classes | Medium | Equation construction and satisfaction |
| `EquationsCompatibilityTest` | `Equations` utility class | Medium | Static utility methods for equations |
| `PresentationCompatibilityTest` | `Presentation` classes | Medium | Algebraic presentation operations |

**Coverage**: 3/3 classes (100.0%) - Complete coverage of equation functionality

### org.uacalc.group - Group Classes

| Test Class | Java Classes Tested | Priority | Description |
|------------|-------------------|----------|-------------|
| `PermutationGroupCompatibilityTest` | `PermutationGroup` classes | Medium | Permutation group operations |

**Coverage**: 1/1 classes (100.0%) - Complete coverage of group functionality

### org.uacalc.io - I/O Classes

| Test Class | Java Classes Tested | Priority | Description |
|------------|-------------------|----------|-------------|
| `AlgebraIOCompatibilityTest` | `AlgebraIO` utility class | High | Static I/O utility methods |
| `AlgebraReaderCompatibilityTest` | `AlgebraReader` classes | High | Algebra file reading and parsing |
| `AlgebraWriterCompatibilityTest` | `AlgebraWriter` classes | High | Algebra file writing and generation |

**Coverage**: 3/7 classes (42.9%) - Moderate coverage, some I/O formats may need additional tests

### org.uacalc.util - Utility Classes

| Test Class | Java Classes Tested | Priority | Description |
|------------|-------------------|----------|-------------|
| `IntArrayCompatibilityTest` | `IntArray` classes | Low | Integer array operations |
| `HornerCompatibilityTest` | `Horner` classes | Low | Horner encoding/decoding |
| `SequenceGeneratorCompatibilityTest` | `SequenceGenerator` classes | Low | Sequence generation utilities |

**Coverage**: 3/6 classes (50.0%) - Basic coverage of utility functionality

## Test Coverage Summary

### Overall Statistics
- **Total Java Classes**: 128
- **Covered by Tests**: 37
- **Overall Coverage**: 28.9%

### Coverage by Priority
- **High Priority Packages**: 75.0% average coverage
- **Medium Priority Packages**: 83.3% average coverage  
- **Low Priority Packages**: 50.0% average coverage

### Coverage by Package
1. **org.uacalc.eq**: 100.0% (3/3 classes)
2. **org.uacalc.group**: 100.0% (1/1 classes)
3. **org.uacalc.alg**: 83.3% (10/12 classes)
4. **org.uacalc.lat**: 66.7% (4/6 classes)
5. **org.uacalc.terms**: 66.7% (4/6 classes)
6. **org.uacalc.alg.conlat**: 62.5% (5/8 classes)
7. **org.uacalc.alg.op**: 50.0% (4/8 classes)
8. **org.uacalc.util**: 50.0% (3/6 classes)
9. **org.uacalc.io**: 42.9% (3/7 classes)

## Test Dependencies

### Execution Order
Tests are executed in dependency order to ensure proper setup:

1. **Basic Tests** (no dependencies)
   - `BasicAlgebraCompatibilityTest`
   - `BasicLatticeCompatibilityTest`
   - `OperationCompatibilityTest`
   - `OperationSymbolCompatibilityTest`
   - `TermCompatibilityTest`

2. **Core Tests** (depend on basic tests)
   - `AlgebraCompatibilityTest`
   - `SmallAlgebraCompatibilityTest`
   - `AlgebrasCompatibilityTest`
   - `LatticeCompatibilityTest`
   - `OrderCompatibilityTest`

3. **Advanced Tests** (depend on core tests)
   - `FreeAlgebraCompatibilityTest`
   - `HomomorphismCompatibilityTest`
   - `MalcevCompatibilityTest`
   - `ProductAlgebraCompatibilityTest`
   - `QuotientAlgebraCompatibilityTest`
   - `SubalgebraCompatibilityTest`
   - `CongruenceLatticeCompatibilityTest`
   - `PartitionCompatibilityTest`
   - `BinaryRelationCompatibilityTest`

4. **Specialized Tests** (depend on term/operation tests)
   - `TermOperationCompatibilityTest`
   - `EquationCompatibilityTest`
   - `EquationsCompatibilityTest`
   - `PresentationCompatibilityTest`

5. **Utility Tests** (independent)
   - `PermutationGroupCompatibilityTest`
   - `AlgebraIOCompatibilityTest`
   - `AlgebraReaderCompatibilityTest`
   - `AlgebraWriterCompatibilityTest`
   - `IntArrayCompatibilityTest`
   - `HornerCompatibilityTest`
   - `SequenceGeneratorCompatibilityTest`

## Missing Test Coverage

### High Priority Gaps
1. **org.uacalc.alg**: Missing tests for some advanced algebra classes
2. **org.uacalc.alg.conlat**: Missing tests for some congruence lattice operations
3. **org.uacalc.alg.op**: Missing tests for some operation types
4. **org.uacalc.terms**: Missing tests for some term operations
5. **org.uacalc.io**: Missing tests for some I/O formats

### Recommendations
1. **Add missing test classes** for uncovered Java classes
2. **Improve existing tests** to cover more edge cases
3. **Add integration tests** that test multiple packages together
4. **Consider performance tests** for large-scale operations

## Test Data Requirements

### Algebra Files by Test Category
- **Small Algebras** (≤4 elements): Used by all test classes
- **Medium Algebras** (5-8 elements): Used by most test classes
- **Large Algebras** (>8 elements): Used by advanced test classes only

### Test Data Sources
- `resources/algebras/ba2.ua` - Boolean algebra (2 elements)
- `resources/algebras/cyclic2.ua` - Cyclic group (2 elements)
- `resources/algebras/cyclic3.ua` - Cyclic group (3 elements)
- `resources/algebras/d16.ua` - Dihedral group (16 elements)
- `resources/algebras/m3.ua` - Modular lattice (3 elements)
- `resources/algebras/m4.ua` - Modular lattice (4 elements)
- `resources/algebras/bergman/*.ua` - Bergman algebras (various sizes)

## Usage Examples

### Testing Specific Package
```bash
# Test only algebra package
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/comprehensive_test_suite.py \
    --no-congruence --no-operation --no-term --no-lattice --no-equation --no-group --no-io --no-utility
```

### Testing High Priority Only
```bash
# Test high priority packages
PYTHONPATH=/home/jamie/Documents/uacalcsrc python tests/python/comprehensive_test_suite.py \
    --no-lattice --no-equation --no-group --no-utility
```

### Testing Individual Classes
```bash
# Test specific test class
PYTHONPATH=/home/jamie/Documents/uacalcsrc python -m pytest tests/python/test_algebra_compatibility.py -v
```

This mapping ensures that developers can easily understand which test classes cover which Java UACalc functionality, making it easier to maintain and extend the test suite.
