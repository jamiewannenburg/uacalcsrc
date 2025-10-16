# Term Cloning Requirements and Implementation Guide

## Overview

Currently, the term implementation has several features that require term cloning but cannot be fully implemented due to the trait object nature of `Box<dyn Term>`. This document outlines what needs to be implemented to satisfy cloning dependencies.

## Current State

### What Works ✅
- **VariableImp**: Implements `Clone` trait and can be cloned
- **TermClone trait**: Basic infrastructure exists for cloning trait objects
- **Variable cloning**: Works perfectly for all variable operations

### What Doesn't Work ❌
1. **NonVariableTerm cloning**: Cannot implement `Clone` because it contains `Vec<Box<dyn Term>>`
2. **get_children()**: Returns `None` for NonVariableTerm (needs cloning to return actual children)
3. **substitute()**: Cannot replace terms in NonVariableTerm (needs cloning)
4. **interpretation_simple()**: Cannot create TermOperationImp for NonVariableTerm (needs term cloning)
5. **Python bindings**: Cannot support NonVariableTerm children in constructor (needs cloning)

## Cloning Issues in Detail

### Issue 1: NonVariableTerm Cannot Implement Clone

**Location**: `src/terms/mod.rs` line 302

**Current Code**:
```rust
#[derive(Debug)]  // ❌ No Clone derive
pub struct NonVariableTerm {
    pub leading_operation_symbol: OperationSymbol,
    pub children: Vec<Box<dyn Term>>,  // ❌ Cannot derive Clone
}
```

**Problem**: 
- `Box<dyn Term>` doesn't automatically implement `Clone`
- Rust cannot derive `Clone` for structs containing trait objects

**Impact**:
- Cannot create copies of NonVariableTerm
- Cannot pass NonVariableTerm by value
- Limits operations that need to duplicate terms

### Issue 2: get_children() Returns None

**Location**: `src/terms/mod.rs` line 425-429

**Current Code**:
```rust
fn get_children(&self) -> Option<Vec<Box<dyn Term>>> {
    // We need to clone the children, which requires Term to be cloneable
    // For now, return None as a placeholder
    None
}
```

**Problem**:
- To return children, we need to clone each `Box<dyn Term>`
- No way to clone trait objects without explicit support

**Impact**:
- Cannot inspect term structure from outside
- Cannot traverse term trees programmatically
- Limits term analysis capabilities

### Issue 3: substitute() Is Incomplete

**Location**: `src/terms/mod.rs` lines 315-323, 543

**Current Code (VariableImp)**:
```rust
fn substitute(&self, map: &HashMap<String, Box<dyn Term>>) -> Result<Box<dyn Term>, String> {
    if let Some(_replacement) = map.get(&self.name) {
        // Clone the term by converting to string and back (placeholder)
        // In a real implementation, we'd need proper cloning
        Ok(Box::new(self.clone()))  // ❌ Should return replacement
    } else {
        Ok(Box::new(self.clone()))
    }
}
```

**Current Code (NonVariableTerm)**:
```rust
fn substitute(&self, _map: &HashMap<String, Box<dyn Term>>) -> Result<Box<dyn Term>, String> {
    Err("NonVariableTerm substitute not yet fully implemented".to_string())
}
```

**Problem**:
- Cannot clone the replacement term from the map
- Cannot recursively substitute in children

**Impact**:
- Term substitution doesn't work
- Cannot perform variable replacement operations
- Limits term manipulation capabilities

### Issue 4: interpretation_simple() for NonVariableTerm

**Location**: `src/terms/mod.rs` lines 512-519

**Current Code**:
```rust
fn interpretation_simple(
    &self,
    _alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
) -> Result<Box<dyn TermOperation>, String> {
    let _varlist = self.get_variable_list();
    // We can't easily create a Box<dyn Term> from &self since NonVariableTerm doesn't implement Clone
    // For now, return an error
    Err("NonVariableTerm interpretation_simple requires term cloning".to_string())
}
```

**Problem**:
- TermOperationImp needs `Box<dyn Term>` ownership
- Cannot create owned copy without cloning

**Impact**:
- interpretation_simple() doesn't work for compound terms
- Incomplete TermOperation support

### Issue 5: Python Bindings Limited

**Location**: `uacalc_lib/src/terms.rs`

**Current Code**:
```rust
#[new]
fn new(op_sym: &crate::alg::PyOperationSymbol, children: &Bound<'_, PyList>) -> PyResult<Self> {
    // ...
    } else if let Ok(nvt) = item.extract::<PyRef<PyNonVariableTerm>>() {
        // For NonVariableTerm, we need to create a new one since it doesn't implement Clone
        // For now, return an error
        return Err(PyValueError::new_err(
            "NonVariableTerm children are not yet supported (requires cloning)"
        ));
    }
    // ...
}
```

**Problem**:
- Cannot clone NonVariableTerm to add as child
- Python users cannot create nested compound terms

**Impact**:
- Python API is incomplete
- Cannot build complex terms from Python

## Solution: Implement Proper Term Cloning

### Step 1: Add clone_box() to Term Trait

The `TermClone` trait already exists but needs to be integrated into `Term`:

**Current Code**:
```rust
pub trait TermClone {
    fn clone_box(&self) -> Box<dyn Term>;
}

impl<T: 'static + Term + Clone> TermClone for T {
    fn clone_box(&self) -> Box<dyn Term> {
        Box::new(self.clone())
    }
}
```

**Required Change**:
```rust
pub trait Term: Display + Debug + Send + Sync {
    // ... existing methods ...
    
    /// Clone this term into a new boxed trait object.
    /// 
    /// This allows cloning of trait objects by delegating to the concrete type.
    fn clone_box(&self) -> Box<dyn Term>;
}
```

### Step 2: Implement Clone for VariableImp

**Already Done** ✅ - VariableImp derives Clone:
```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct VariableImp {
    pub name: String,
}

impl Term for VariableImp {
    // ...
    fn clone_box(&self) -> Box<dyn Term> {
        Box::new(self.clone())
    }
}
```

### Step 3: Implement Clone for NonVariableTerm

**Manual Implementation Required**:

```rust
impl Clone for NonVariableTerm {
    fn clone(&self) -> Self {
        NonVariableTerm {
            leading_operation_symbol: self.leading_operation_symbol.clone(),
            children: self.children.iter()
                .map(|child| child.clone_box())  // Use clone_box() for each child
                .collect(),
        }
    }
}

impl Term for NonVariableTerm {
    // ...
    fn clone_box(&self) -> Box<dyn Term> {
        Box::new(self.clone())
    }
}
```

### Step 4: Implement get_children()

```rust
impl Term for NonVariableTerm {
    // ...
    fn get_children(&self) -> Option<Vec<Box<dyn Term>>> {
        // Clone each child using clone_box()
        Some(self.children.iter()
            .map(|child| child.clone_box())
            .collect())
    }
}
```

### Step 5: Implement substitute()

**For VariableImp**:
```rust
impl Term for VariableImp {
    // ...
    fn substitute(&self, map: &HashMap<String, Box<dyn Term>>) -> Result<Box<dyn Term>, String> {
        if let Some(replacement) = map.get(&self.name) {
            // Clone the replacement term
            Ok(replacement.clone_box())
        } else {
            // No replacement, return clone of self
            Ok(Box::new(self.clone()))
        }
    }
}
```

**For NonVariableTerm**:
```rust
impl Term for NonVariableTerm {
    // ...
    fn substitute(&self, map: &HashMap<String, Box<dyn Term>>) -> Result<Box<dyn Term>, String> {
        // Recursively substitute in all children
        let new_children: Vec<Box<dyn Term>> = self.children
            .iter()
            .map(|child| child.substitute(map))
            .collect::<Result<Vec<_>, _>>()?;
        
        // Create new term with substituted children
        Ok(Box::new(NonVariableTerm {
            leading_operation_symbol: self.leading_operation_symbol.clone(),
            children: new_children,
        }))
    }
}
```

### Step 6: Implement interpretation_simple()

```rust
impl Term for NonVariableTerm {
    // ...
    fn interpretation_simple(
        &self,
        alg: Arc<dyn SmallAlgebra<UniverseItem = i32>>,
    ) -> Result<Box<dyn TermOperation>, String> {
        let varlist = self.get_variable_list();
        // Clone this term into a Box
        let term: Box<dyn Term> = self.clone_box();
        let interpretation = self.interpretation(alg.clone(), &varlist, true)?;
        Ok(Box::new(TermOperationImp::new(term, varlist, alg, interpretation)))
    }
}
```

### Step 7: Fix Python Bindings

```rust
impl PyNonVariableTerm {
    #[new]
    fn new(op_sym: &crate::alg::PyOperationSymbol, children: &Bound<'_, PyList>) -> PyResult<Self> {
        let mut rust_children: Vec<Box<dyn Term>> = Vec::new();
        
        for item in children.iter() {
            if let Ok(var) = item.extract::<PyRef<PyVariableImp>>() {
                rust_children.push(Box::new(var.inner.clone()));
            } else if let Ok(nvt) = item.extract::<PyRef<PyNonVariableTerm>>() {
                // Now we can clone NonVariableTerm!
                rust_children.push(nvt.inner.clone_box());
            } else {
                return Err(PyValueError::new_err(
                    "Children must be VariableImp or NonVariableTerm instances"
                ));
            }
        }
        
        Ok(PyNonVariableTerm {
            inner: NonVariableTerm::new(op_sym.inner.clone(), rust_children),
        })
    }
}
```

## Implementation Checklist

### Required Changes

- [ ] **Step 1**: Add `clone_box()` method to `Term` trait
- [ ] **Step 2**: Implement `clone_box()` for VariableImp (use existing Clone impl)
- [ ] **Step 3**: Implement `Clone` manually for NonVariableTerm
- [ ] **Step 4**: Implement `clone_box()` for NonVariableTerm
- [ ] **Step 5**: Fix `get_children()` to return cloned children
- [ ] **Step 6**: Fix `substitute()` for both VariableImp and NonVariableTerm
- [ ] **Step 7**: Fix `interpretation_simple()` for NonVariableTerm
- [ ] **Step 8**: Fix Python bindings to support NonVariableTerm children

### Testing Requirements

- [ ] Test cloning of VariableImp
- [ ] Test cloning of NonVariableTerm (simple)
- [ ] Test cloning of NonVariableTerm (nested)
- [ ] Test get_children() returns correct children
- [ ] Test substitute() with simple variable replacement
- [ ] Test substitute() with nested terms
- [ ] Test interpretation_simple() for NonVariableTerm
- [ ] Test Python NonVariableTerm with NonVariableTerm children
- [ ] Test deep cloning preserves term structure

### Files to Modify

1. `src/terms/mod.rs` - Main implementation
2. `uacalc_lib/src/terms.rs` - Python bindings
3. `src/terms/tests.rs` - Test suite additions

## Benefits of Implementation

Once cloning is properly implemented:

1. ✅ **Complete API**: All Term trait methods will work correctly
2. ✅ **Term Manipulation**: substitute() will enable variable replacement
3. ✅ **Term Analysis**: get_children() will enable tree traversal
4. ✅ **Python Support**: Full nested term construction from Python
5. ✅ **TermOperation**: interpretation_simple() will work for all terms
6. ✅ **Type Safety**: Proper Rust ownership semantics maintained

## Estimated Complexity

- **Implementation Time**: 2-4 hours
- **Testing Time**: 1-2 hours
- **Complexity**: Medium (trait objects + recursive structures)
- **Risk**: Low (well-defined pattern, existing infrastructure)

## Alternative Approaches Considered

### 1. Reference Counting (Arc<dyn Term>)
**Pros**: No cloning needed, shared ownership
**Cons**: Cannot mutate terms, changes API significantly

### 2. Term Serialization
**Pros**: Works with any term type
**Cons**: Performance overhead, complex implementation

### 3. Visitor Pattern
**Pros**: No cloning for tree traversal
**Cons**: Doesn't solve substitute() or Python bindings

## Recommendation

**Implement the clone_box() approach** as outlined above. It:
- Follows Rust best practices for trait object cloning
- Minimal API changes (just add one method to Term trait)
- Solves all outstanding cloning issues
- Maintains type safety and performance
- Already has partial infrastructure in place

## Next Steps

1. Add `clone_box()` to Term trait
2. Implement Clone for NonVariableTerm
3. Fix all dependent methods (get_children, substitute, interpretation_simple)
4. Update Python bindings
5. Add comprehensive tests
6. Update documentation

This implementation will complete the term module and enable full functionality for all term operations.
