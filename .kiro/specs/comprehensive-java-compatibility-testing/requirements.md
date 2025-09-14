# Requirements Document

## Introduction

This feature expands the existing Java compatibility test suite to comprehensively verify that the Rust/Python UACalc implementation produces identical results to the original Java UACalc library across all major features. The goal is to create a robust verification system that ensures 100% compatibility and allows systematic implementation of features one by one with confidence in correctness.

## Requirements

### Requirement 1: Core Algebra Operations Testing

**User Story:** As a UACalc developer, I want comprehensive testing of core algebra operations so that I can verify the Rust implementation matches Java behavior exactly.

#### Acceptance Criteria

1. WHEN testing algebra creation THEN the system SHALL verify identical universe, cardinality, and operation count between Java and Rust
2. WHEN testing operation evaluation THEN the system SHALL verify identical results for all operation tables across all test algebras
3. WHEN testing algebra properties THEN the system SHALL verify identical results for idempotent, associative, and commutative checks
4. WHEN testing subalgebra generation THEN the system SHALL verify identical subalgebras are generated from the same generators
5. WHEN testing algebra serialization THEN the system SHALL verify round-trip compatibility preserves all algebra properties

### Requirement 2: Congruence and Lattice Operations Testing

**User Story:** As a UACalc researcher, I want comprehensive congruence lattice testing so that I can trust the Rust implementation for advanced algebraic computations.

#### Acceptance Criteria

1. WHEN computing principal congruences Cg(a,b) THEN the system SHALL verify identical partitions between Java and Rust for all element pairs
2. WHEN computing congruence lattice properties THEN the system SHALL verify identical lattice size, join irreducibles, and height/width measurements
3. WHEN testing lattice operations THEN the system SHALL verify identical results for join, meet, and ordering operations on congruences
4. WHEN testing congruence generation THEN the system SHALL verify identical results for generating congruences from relation sets
5. WHEN testing lattice traversal THEN the system SHALL verify identical ordering and covering relations in the congruence lattice

### Requirement 3: Binary Relations and Closures Testing

**User Story:** As a UACalc user, I want comprehensive binary relation testing so that I can verify relation operations work identically to Java UACalc.

#### Acceptance Criteria

1. WHEN creating binary relations THEN the system SHALL verify identical relation membership and properties
2. WHEN computing reflexive closure THEN the system SHALL verify identical results between Java and Rust implementations
3. WHEN computing symmetric closure THEN the system SHALL verify identical results between Java and Rust implementations
4. WHEN computing transitive closure THEN the system SHALL verify identical results between Java and Rust implementations
5. WHEN computing equivalence closure THEN the system SHALL verify identical partitions are generated
6. WHEN testing relation properties THEN the system SHALL verify identical results for reflexivity, symmetry, and transitivity checks

### Requirement 4: Term Operations and Evaluation Testing

**User Story:** As a UACalc developer, I want comprehensive term testing so that I can verify term parsing and evaluation matches Java behavior exactly.

#### Acceptance Criteria

1. WHEN parsing valid terms THEN the system SHALL verify identical parsing results and term structure between Java and Rust
2. WHEN parsing invalid terms THEN the system SHALL verify identical error handling and rejection behavior
3. WHEN evaluating terms THEN the system SHALL verify identical evaluation results for all variable assignments
4. WHEN validating terms against algebras THEN the system SHALL verify identical validation results for operation symbol checking
5. WHEN handling variable substitution THEN the system SHALL verify identical results for complex term evaluations

### Requirement 5: Advanced Algebraic Properties Testing

**User Story:** As a UACalc researcher, I want testing of advanced algebraic properties so that I can verify sophisticated algebraic computations are correct.

#### Acceptance Criteria

1. WHEN testing Maltsev conditions THEN the system SHALL verify identical results for checking if algebras satisfy Maltsev conditions (congruence modularity, congruence distributivity, etc.)
2. WHEN computing free algebras THEN the system SHALL verify identical free algebra generation and properties for given generators and variety constraints
3. WHEN testing isomorphisms THEN the system SHALL verify identical isomorphism detection and mapping between algebras
4. WHEN computing direct products THEN the system SHALL verify identical product algebra construction and properties
5. WHEN testing quotient algebras THEN the system SHALL verify identical quotient construction from congruences
6. WHEN checking variety membership THEN the system SHALL verify identical results for determining if algebras belong to specific varieties (groups, lattices, Boolean algebras, etc.)
7. WHEN testing automorphism groups THEN the system SHALL verify identical automorphism detection and group structure computation

### Requirement 6: File Format and I/O Compatibility Testing

**User Story:** As a UACalc user, I want comprehensive file format testing so that I can seamlessly interchange files between Java and Rust implementations.

#### Acceptance Criteria

1. WHEN loading Java-created .ua files THEN the system SHALL verify identical algebra reconstruction in Rust
2. WHEN saving Rust-created .ua files THEN the system SHALL verify Java can load them identically
3. WHEN testing round-trip file operations THEN the system SHALL verify no data loss or corruption occurs
4. WHEN handling Unicode and special characters THEN the system SHALL verify identical encoding/decoding behavior
5. WHEN processing malformed files THEN the system SHALL verify identical error handling and recovery behavior

### Requirement 7: Correctness Verification Testing

**User Story:** As a UACalc developer, I want correctness verification testing so that I can ensure the Rust implementation produces mathematically correct results.

#### Acceptance Criteria

1. WHEN testing large algebras THEN the system SHALL verify both implementations produce identical results within reasonable time limits
2. WHEN running comprehensive test suites THEN the system SHALL verify system stability and consistent results across all test algebras
3. WHEN testing edge cases THEN the system SHALL verify proper handling of boundary conditions and special cases
4. WHEN validating mathematical properties THEN the system SHALL verify algebraic laws and identities are preserved
5. WHEN testing with diverse algebra types THEN the system SHALL verify correctness across groups, lattices, rings, and other algebraic structures