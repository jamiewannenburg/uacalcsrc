<!-- 8b1379a7-a259-4df8-bf40-26ab9d201db5 e548c04c-d878-45ed-a914-68873f6ba6ef -->
# BasicLattice Implementation Plan

## Overview

Implement `BasicLattice` in Rust to replace the Java version that depends on the external `latdraw` library. The Rust implementation will provide graph data structures that can be converted to NetworkX graphs in Python for visualization.

## 1. Core Rust Implementation

### 1.1 Create BasicLattice Structure (`src/lat/basic_lattice.rs`)

**Struct Design:**

```rust
pub struct BasicLattice<T> {
    name: String,
    poset: OrderedSet<T>,  // Internal poset structure
    univ_list: Vec<POElem<T>>,
    univ_hs: Option<HashSet<POElem<T>>>,
    join_operation: Box<dyn Operation>,
    meet_operation: Box<dyn Operation>,
    join_irreducibles: Option<Vec<POElem<T>>>,
    meet_irreducibles: Option<Vec<POElem<T>>>,
    tct_type_map: Option<HashMap<Edge, String>>,  // For TCT labeling
}
```

**Key Methods to Implement:**

- `new_from_poset()` - Constructor from OrderedSet
- `new_from_lattice()` - Constructor from Lattice trait
- `new_from_congruence_lattice()` - Constructor from CongruenceLattice with optional TCT labeling
- `join()`, `meet()`, `leq()` - Lattice operations
- `atoms()`, `coatoms()` - Minimal/maximal elements
- `join_irreducibles()`, `meet_irreducibles()` - Irreducible elements
- `to_graph_data()` - Returns graph structure for visualization

### 1.2 Implement OrderedSet Structure (`src/lat/ordered_set.rs`)

**Replace latdraw dependency with internal implementation:**

```rust
pub struct OrderedSet<T> {
    name: Option<String>,
    universe: Vec<POElem<T>>,
    upper_covers: HashMap<POElem<T>, Vec<POElem<T>>>,
    elem_order: HashMap<POElem<T>, usize>,
}

pub struct POElem<T> {
    underlying_object: T,
    index: usize,
    // Cached covers
    upper_covers_cache: Option<Vec<POElem<T>>>,
    lower_covers_cache: Option<Vec<POElem<T>>>,
}
```

**Key Methods:**

- `new()` - Constructor from universe and upper covers
- `ordered_set_from_filters()` - Factory from filters (like latdraw)
- `univ()` - Get universe
- `leq()` - Order relation
- `elem_order()` - Get element index
- `get_element()` - Get element by index

### 1.3 Graph Data Structure (`src/lat/graph_data.rs`)

**Structure for NetworkX conversion:**

```rust
pub struct LatticeGraphData {
    pub nodes: Vec<GraphNode>,
    pub edges: Vec<GraphEdge>,
    pub node_labels: HashMap<usize, String>,
    pub edge_labels: Option<HashMap<(usize, usize), String>>,  // For TCT
}

pub struct GraphNode {
    pub id: usize,
    pub label: String,
    pub element: String,  // String representation of underlying element
}

pub struct GraphEdge {
    pub source: usize,
    pub target: usize,
    pub label: Option<String>,  // For TCT type labels
}
```

### 1.4 Implement Lattice Trait for BasicLattice

Implement `Lattice`, `SmallAlgebra`, and `GeneralAlgebra` traits following existing patterns in `src/lat/lattice.rs` and `src/alg/small_algebra.rs`.

### 1.5 Factory Methods in `src/lat/lattices.rs`

- `lattice_from_meet()` - Already partially implemented, complete it
- `lattice_from_join()` - Implement following Java pattern
- `dual()` - Create dual lattice

## 2. Add getBasicLattice Methods

### 2.1 CongruenceLattice (`src/alg/conlat/congruence_lattice.rs`)

Add methods:

```rust
impl<T> CongruenceLattice<T> {
    pub fn get_basic_lattice(&mut self, make_if_null: bool) -> Option<BasicLattice<Partition>> {
        // Create BasicLattice from this CongruenceLattice
        // Include TCT labeling if requested
    }
    
    pub fn get_basic_lattice_default(&mut self) -> Option<BasicLattice<Partition>> {
        self.get_basic_lattice(true)
    }
}
```

### 2.2 SubalgebraLattice (`src/alg/sublat/mod.rs`)

Add methods:

```rust
impl<T> SubalgebraLattice<T> {
    pub fn get_basic_lattice(&mut self, make_if_null: bool) -> Option<BasicLattice<BasicSet>> {
        // Create BasicLattice from this SubalgebraLattice
    }
    
    pub fn get_basic_lattice_default(&mut self) -> Option<BasicLattice<BasicSet>> {
        self.get_basic_lattice(true)
    }
}
```

### 2.3 SmallAlgebra Extension (`src/alg/small_algebra.rs`)

Add method to detect semilattice operations and create BasicLattice:

```rust
pub trait SmallAlgebra: Algebra {
    // ... existing methods ...
    
    /// Get BasicLattice for algebras that are lattices/semilattices
    fn get_basic_lattice_from_semilattice_ops(&self) -> Option<Vec<BasicLattice<i32>>> {
        // Find operations that are commutative, idempotent, and associative
        // Create BasicLattice for each using lattice_from_meet or lattice_from_join
    }
}
```

**Helper function to detect semilattice operations:**

```rust
pub fn find_semilattice_operations(alg: &dyn SmallAlgebra) -> Vec<&dyn Operation> {
    // Check each operation for is_commutative(), is_idempotent(), is_associative()
    // Return matching operations
}
```

## 3. Python Bindings (`uacalc_lib/src/lat.rs`)

### 3.1 PyBasicLattice Class

```rust
#[pyclass]
pub struct PyBasicLattice {
    inner: Arc<BasicLattice<i32>>,  // Use Arc following clone fix patterns
}

#[pymethods]
impl PyBasicLattice {
    #[new]
    fn new(name: String, lattice: PyObject) -> PyResult<Self> { ... }
    
    fn to_graph_data(&self) -> PyResult<PyLatticeGraphData> { ... }
    
    fn to_networkx(&self, py: Python) -> PyResult<PyObject> {
        // Optional: if networkx available, return DiGraph
        // Otherwise return graph data structure
    }
    
    // Expose key methods: join, meet, leq, atoms, coatoms, etc.
}
```

### 3.2 PyLatticeGraphData Class

```rust
#[pyclass]
pub struct PyLatticeGraphData {
    nodes: Vec<PyGraphNode>,
    edges: Vec<PyGraphEdge>,
    node_labels: HashMap<usize, String>,
    edge_labels: Option<HashMap<(usize, usize), String>>,
}

#[pymethods]
impl PyLatticeGraphData {
    fn to_networkx(&self, py: Python) -> PyResult<PyObject> {
        // Convert to NetworkX DiGraph if available
    }
    
    fn to_dot(&self) -> String { ... }
    fn to_mermaid(&self) -> String { ... }
}
```

### 3.3 Optional NetworkX Dependency

**In `pyproject.toml`:**

```toml
[project.optional-dependencies]
drawing = [
    "networkx>=3.0",
]
```

**In Python bindings, check for networkx:**

```rust
fn to_networkx(&self, py: Python) -> PyResult<PyObject> {
    match py.import("networkx") {
        Ok(nx) => {
            // Create DiGraph
            let graph = nx.getattr("DiGraph")?.call0()?;
            // Add nodes and edges
            Ok(graph)
        }
        Err(_) => Err(PyValueError::new_err("networkx not installed. Install with: pip install uacalc[drawing]"))
    }
}
```

### 3.4 Add getBasicLattice to Python Bindings

**For CongruenceLattice:**

```rust
#[pymethods]
impl PyCongruenceLattice {
    fn get_basic_lattice(&mut self, make_if_null: Option<bool>) -> PyResult<Option<PyBasicLattice>> {
        // ...
    }
}
```

**For SubalgebraLattice:**

```rust
#[pymethods]
impl PySubalgebraLattice {
    fn get_basic_lattice(&mut self, make_if_null: Option<bool>) -> PyResult<Option<PyBasicLattice>> {
        // ...
    }
}
```

**For SmallAlgebra:**

```rust
#[pymethods]
impl PySmallAlgebra {
    fn get_basic_lattice_from_semilattice_ops(&self) -> PyResult<Vec<PyBasicLattice>> {
        // ...
    }
}
```

## 4. Java Wrapper (`java_wrapper/src/lat/BasicLatticeWrapper.java`)

Create wrapper following `IMPLEMENTATION_PATTERNS.md`:

**Commands:**

- `help` - Show usage
- `new_from_poset` - Create from poset
- `new_from_lattice` - Create from lattice
- `new_from_congruence` - Create from congruence lattice
- `join` - Compute join
- `meet` - Compute meet
- `leq` - Check order relation
- `atoms` - Get atoms
- `coatoms` - Get coatoms
- `join_irreducibles` - Get join irreducibles
- `meet_irreducibles` - Get meet irreducibles
- `to_graph_data` - Get graph data (JSON format)
- `test` - Run basic tests

## 5. Testing Strategy

### 5.1 Rust Tests (`tests/lat_basic_lattice_tests.rs`)

- Test construction from poset
- Test construction from Lattice trait
- Test construction from CongruenceLattice
- Test construction from SubalgebraLattice
- Test all lattice operations (join, meet, leq)
- Test irreducible elements computation
- Test graph data generation
- Compare with Java wrapper output

### 5.2 Python Tests (`python/uacalc/tests/test_basic_lattice.py`)

- Test BasicLattice creation
- Test graph data conversion
- Test NetworkX integration (if available)
- Test getBasicLattice from CongruenceLattice
- Test getBasicLattice from SubalgebraLattice
- Test getBasicLattice from semilattice operations
- Test visualization formats (DOT, Mermaid)

## 6. Implementation Order

1. **Phase 1: Core Structures**

   - Implement `OrderedSet` and `POElem` in `src/lat/ordered_set.rs`
   - Implement `BasicLattice` struct and basic constructors
   - Implement `LatticeGraphData` structure

2. **Phase 2: Lattice Operations**

   - Implement join/meet operations
   - Implement order relation (leq)
   - Implement irreducible elements computation
   - Implement atoms/coatoms

3. **Phase 3: Graph Generation**

   - Implement `to_graph_data()` method
   - Add TCT labeling support

4. **Phase 4: Integration**

   - Add `get_basic_lattice()` to CongruenceLattice
   - Add `get_basic_lattice()` to SubalgebraLattice
   - Add semilattice detection to SmallAlgebra

5. **Phase 5: Python Bindings**

   - Implement PyBasicLattice
   - Implement PyLatticeGraphData
   - Add NetworkX optional integration
   - Add getBasicLattice methods to Python classes

6. **Phase 6: Java Wrapper**

   - Create BasicLatticeWrapper.java
   - Implement all command handlers

7. **Phase 7: Testing**

   - Write Rust tests
   - Write Python tests
   - Verify against Java implementation

## 7. Key Implementation Notes

### 7.1 Following Clone Fix Patterns

- Use `Arc<dyn Operation>` for operations storage (see `IMPLEMENT_CLONE_FIX.md`)
- Use `Weak` references where needed to break cycles
- Avoid deep cloning in `operations()` method

### 7.2 Following Implementation Patterns

- Use `Result<T, String>` for error handling
- Provide both `_safe` and panic versions where appropriate
- Follow naming conventions (Py* for internal, clean names for export)
- Use `status` field in test JSON, not `result`

### 7.3 TCT Labeling

- Store TCT type map as `HashMap<Edge, String>`
- Include in graph data structure
- Support edge labels in visualization

### 7.4 NetworkX Integration

- Make networkx optional dependency
- Provide fallback to graph data structure
- Support DOT and Mermaid export formats

## 8. Files to Create/Modify

**New Files:**

- `src/lat/basic_lattice.rs`
- `src/lat/ordered_set.rs`
- `src/lat/graph_data.rs`
- `java_wrapper/src/lat/BasicLatticeWrapper.java`
- `tests/lat_basic_lattice_tests.rs`
- `python/uacalc/tests/test_basic_lattice.py`

**Modified Files:**

- `src/lat/mod.rs` - Export BasicLattice
- `src/alg/conlat/congruence_lattice.rs` - Add get_basic_lattice()
- `src/alg/sublat/mod.rs` - Add get_basic_lattice()
- `src/alg/small_algebra.rs` - Add semilattice detection
- `src/lat/lattices.rs` - Complete factory methods
- `uacalc_lib/src/lat.rs` - Add Python bindings
- `uacalc_lib/src/alg.rs` - Add getBasicLattice to Python classes
- `pyproject.toml` - Add optional networkx dependency
- `uacalc_lib/Cargo.toml` - No changes needed (networkx is Python-only)

## 9. Compilation Notes

- Use `ant compile-wrappers` for Java wrapper
- Use `maturin develop` in venv for Python bindings
- Can disable warnings with `RUSTFLAGS="-A warnings"` if needed
- Follow existing patterns for module registration in `uacalc_lib/src/lib.rs`

### To-dos

- [ ] Implement OrderedSet and POElem structures in src/lat/ordered_set.rs to replace latdraw dependency
- [ ] Implement BasicLattice struct and core constructors in src/lat/basic_lattice.rs
- [ ] Implement LatticeGraphData structure in src/lat/graph_data.rs for NetworkX conversion
- [ ] Implement lattice operations (join, meet, leq) and irreducible elements in BasicLattice
- [ ] Implement to_graph_data() method in BasicLattice to generate graph structure
- [ ] Add get_basic_lattice() methods to CongruenceLattice in src/alg/conlat/congruence_lattice.rs
- [ ] Add get_basic_lattice() methods to SubalgebraLattice in src/alg/sublat/mod.rs
- [ ] Add semilattice operation detection and get_basic_lattice_from_semilattice_ops() to SmallAlgebra
- [ ] Complete lattice_from_meet() and implement lattice_from_join() in src/lat/lattices.rs
- [ ] Implement PyBasicLattice and PyLatticeGraphData Python bindings in uacalc_lib/src/lat.rs
- [ ] Add optional NetworkX integration in Python bindings with fallback to graph data
- [ ] Add getBasicLattice methods to Python CongruenceLattice and SubalgebraLattice bindings
- [ ] Add networkx as optional dependency in pyproject.toml
- [ ] Create BasicLatticeWrapper.java following IMPLEMENTATION_PATTERNS.md
- [ ] Write Rust tests in tests/lat_basic_lattice_tests.rs comparing with Java wrapper
- [ ] Write Python tests in python/uacalc/tests/test_basic_lattice.py including NetworkX tests