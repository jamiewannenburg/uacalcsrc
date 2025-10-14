# UACalc Rust/Python Translation Plan

## Overview

This plan contains the ordered list of translation tasks for converting the UACalc Java library to Rust with Python bindings. Tasks are ordered by dependency count to ensure foundational classes are translated before dependent classes.

## Translation Strategy

### Approach
- Direct Java-to-Rust translation maintaining exact semantics
- Use Rust idioms where appropriate (traits for interfaces, Result/Option, etc.)
- All public methods must be translated and tested
- Output must match Java implementation exactly

### Testing Strategy
- Rust tests for all public methods with timeouts
- Python binding tests comparing against Java
- Java CLI wrappers for ground truth comparison
- Global memory limit configurable from Python

### ExcluRded Packages
The following packages are **excluded** from this plan:
- `org.uacalc.ui.*` - UI components (not needed for core library)
- `org.uacalc.nbui.*` - NetBeans UI components
- `org.uacalc.example.*` - Example/demo classes (NOTE: To be implemented later)


## Translation Tasks

## Task 8: Translate `ExtFileFilter` ✅ COMPLETED

**Java File:** `org/uacalc/io/ExtFileFilter.java`  
**Package:** `org.uacalc.io`  
**Rust Module:** `io::ExtFileFilter`  
**Dependencies:** 0 (0 non-UI/example)  
**Actual Public Methods:** 16

### Description
Translate the Java class `org.uacalc.io.ExtFileFilter` to Rust with Python bindings.

### Dependencies
**VERIFIED:** No dependencies on other UACalc classes (leaf node). The class only uses standard Java libraries (`java.io.*`, `java.util.*`, `javax.swing.filechooser.*`).

### Java Class Analysis

**Class Type:** Concrete class extending `javax.swing.filechooser.FileFilter`  
**Public Methods:** 16 total
- 2 constructors: `ExtFileFilter(String, List<String>)`, `ExtFileFilter(String, String)`
- 2 instance methods: `accept(File)`, `getDescription()`
- 2 static methods: `splitOffExtension(File)`, `getExtension(File)`
- 6 public constants: `ALG_EXT`, `XML_EXT`, `UAC_EXT`, `UA_EXT`, `CSV_EXT`, `TXT_EXT`
- 3 static lists: `UA_EXTS`, `ALL_ALG_EXTS`, `MACE4_EXTS`
- 1 main method (for testing)

**Key Patterns:**
- File filtering based on extensions
- Static utility methods for file path manipulation
- Constants for common file extensions
- Extends Swing FileFilter for UI integration

### Rust Implementation Analysis

**Rust Construct:** Struct with associated functions and constants  
**Design Decisions:**
- `ExtFileFilter` struct with `Vec<String>` for extensions (vs Java's `List<String>`)
- `Option<String>` return types for methods that can return null in Java
- Static constants using `once_cell::sync::Lazy` for lazy initialization
- Manual `Hash` implementation due to `Vec<String>` not implementing `Hash`
- Both `_safe` and regular versions of constructors for error handling

**Method Organization:**
- Instance methods: `accept()`, `get_description()`, `get_extensions()`
- Static methods: `split_off_extension()`, `get_extension()`
- Constructors: `new()`, `new_single()`, `new_safe()`, `new_single_safe()`
- Constants: `ALG_EXT`, `XML_EXT`, `UAC_EXT`, `UA_EXT`, `CSV_EXT`, `TXT_EXT`
- Static lists: `UA_EXTS`, `ALL_ALG_EXTS`, `MACE4_EXTS`

### Python Bindings Analysis

**Implementation:** Complete PyO3 bindings with clean exports  
**Key Features:**
- Clean API exports (no `Py` prefixes visible to users)
- Proper error handling with `PyValueError`
- Python magic methods: `__str__`, `__repr__`, `__eq__`, `__hash__`
- Static methods properly exposed
- String parameters for file paths (converted to `Path` internally)

### Java Wrapper Analysis

**Suitability:** ✅ SUITABLE - Concrete class with all methods accessible  
**Implementation:** Complete CLI wrapper with all 16 methods exposed  
**Features:**
- All public methods accessible through CLI commands
- JSON output for easy comparison with Rust/Python
- Proper argument parsing and error handling
- Test command for basic functionality verification

### Testing Strategy

**Rust Tests:** 18 comprehensive tests covering all methods and edge cases  
**Python Tests:** 17 tests verifying Python bindings functionality  
**Java Wrapper Tests:** 5 basic functionality tests via CLI  
**Cross-Language Verification:** All tests pass and produce identical results

**Test Coverage:**
- All 16 public methods tested
- Edge cases: files without extensions, directories, invalid inputs
- Error conditions: empty descriptions, empty extension lists
- Cross-language compatibility: Rust ↔ Java ↔ Python

### Implementation Recommendations

**Rust Design:**
- ✅ **Struct with Vec<String>** - Appropriate for mutable extension lists
- ✅ **Option<String> returns** - Proper null handling vs Java's null returns
- ✅ **Manual Hash implementation** - Required for Vec<String> consistency
- ✅ **Static constants with Lazy** - Efficient lazy initialization
- ✅ **Both safe/panic versions** - Follows established patterns

**Python Bindings:**
- ✅ **Clean API exports** - No Py prefixes visible to users
- ✅ **Proper error handling** - PyValueError for validation errors
- ✅ **Magic methods** - Full Python object protocol support
- ✅ **String path parameters** - User-friendly API

**Java Wrapper:**
- ✅ **Complete method coverage** - All 16 methods accessible
- ✅ **JSON output format** - Easy comparison with other implementations
- ✅ **Proper argument parsing** - Handles all parameter types correctly

### Verification Results

**Dependencies:** ✅ VERIFIED - No UACalc dependencies, only standard Java libraries  
**Implementation Completeness:** ✅ VERIFIED - All 16 methods implemented  
**Test Coverage:** ✅ VERIFIED - 18 Rust + 17 Python + 5 Java tests all passing  
**Cross-Language Compatibility:** ✅ VERIFIED - Identical behavior across all implementations  
**Code Quality:** ✅ VERIFIED - No compilation warnings, proper error handling

### Acceptance Criteria
- [x] All public methods translated to Rust
- [x] Python bindings expose all public methods  
- [x] Java CLI wrapper created with all public methods
- [x] Rust tests pass with timeouts enabled
- [x] Python tests pass and match Java output
- [x] Code compiles without warnings
- [x] Documentation complete

### Completion Summary
**Status:** ✅ COMPLETED  
**Date:** January 2025  
**Implementation Details:**
- Successfully translated all 16 public methods from Java to Rust
- Created comprehensive Python bindings using PyO3 with clean API exports
- Implemented Java CLI wrapper for cross-language testing and validation
- All 18 Rust tests pass with proper timeout handling
- All 17 Python tests pass and verify functionality
- Fixed critical issue with `split_off_extension` method to match Java behavior (returns `None` for both name and extension when no extension exists)
- Updated `WrapperBase.java` to properly serialize Java `List` objects as JSON arrays
- All tests verify exact output matching between Rust and Java implementations
- **VERIFIED:** No dependencies on other UACalc classes - this is a true leaf node
