use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyDict;
use uacalc::lat::*;
use uacalc::alg::algebra::Algebra;
use uacalc::alg::op::Operation;
use uacalc::lat::lattices;
use crate::alg::op::int_operation::PyIntOperation;
use crate::alg::op::operation::PyBasicOperation;
use std::ops::Deref;

/// Internal enum to hold either type of BasicLattice
/// Made public(crate) so it can be used in other modules
pub(crate) enum BasicLatticeInner {
    Partition(std::sync::Arc<std::sync::Mutex<uacalc::lat::BasicLattice<uacalc::alg::conlat::Partition>>>),
    BasicSet(std::sync::Arc<std::sync::Mutex<uacalc::lat::BasicLattice<uacalc::alg::sublat::BasicSet>>>),
    Int32(std::sync::Arc<std::sync::Mutex<uacalc::lat::BasicLattice<i32>>>),
}

/// Python wrapper for DivisibilityOrder
#[pyclass]
pub struct PyDivisibilityOrder {
    inner: uacalc::lat::DivisibilityOrder,
}

#[pymethods]
impl PyDivisibilityOrder {
    /// Create a new DivisibilityOrder
    #[new]
    fn new() -> Self {
        PyDivisibilityOrder {
            inner: uacalc::lat::DivisibilityOrder,
        }
    }
    
    /// Check if a divides b (a ≤ b in divisibility order)
    fn leq(&self, a: i32, b: i32) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        "DivisibilityOrder".to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        "DivisibilityOrder()".to_string()
    }
}

/// Python wrapper for PrefixOrder
#[pyclass]
pub struct PyPrefixOrder {
    inner: uacalc::lat::PrefixOrder,
}

#[pymethods]
impl PyPrefixOrder {
    /// Create a new PrefixOrder
    #[new]
    fn new() -> Self {
        PyPrefixOrder {
            inner: uacalc::lat::PrefixOrder,
        }
    }
    
    /// Check if a is a prefix of b (a ≤ b in prefix order)
    fn leq(&self, a: String, b: String) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        "PrefixOrder".to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        "PrefixOrder()".to_string()
    }
}

/// Python wrapper for NaturalOrder
#[pyclass]
pub struct PyNaturalOrder {
    inner: uacalc::lat::NaturalOrder,
}

#[pymethods]
impl PyNaturalOrder {
    /// Create a new NaturalOrder
    #[new]
    fn new() -> Self {
        PyNaturalOrder {
            inner: uacalc::lat::NaturalOrder,
        }
    }
    
    /// Check if a ≤ b in natural order for integers
    fn leq_i32(&self, a: i32, b: i32) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Check if a ≤ b in natural order for unsigned integers
    fn leq_u32(&self, a: u32, b: u32) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Check if a ≤ b in natural order for strings
    fn leq_string(&self, a: String, b: String) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        "NaturalOrder".to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        "NaturalOrder()".to_string()
    }
}

/// Find maximal elements in a collection using DivisibilityOrder
#[pyfunction]
fn maximals_divisibility(elems: Vec<i32>) -> PyResult<Vec<i32>> {
    let order = uacalc::lat::DivisibilityOrder;
    Ok(uacalc::lat::ordered_sets::maximals(&elems, &order))
}

/// Find maximal elements in a collection using PrefixOrder
#[pyfunction]
fn maximals_prefix(elems: Vec<String>) -> PyResult<Vec<String>> {
    let order = uacalc::lat::PrefixOrder;
    Ok(uacalc::lat::ordered_sets::maximals(&elems, &order))
}

/// Find maximal elements in a collection using NaturalOrder for integers
#[pyfunction]
fn maximals_natural_i32(elems: Vec<i32>) -> PyResult<Vec<i32>> {
    let order = uacalc::lat::NaturalOrder;
    Ok(uacalc::lat::ordered_sets::maximals(&elems, &order))
}

/// Find maximal elements in a collection using NaturalOrder for strings
#[pyfunction]
fn maximals_natural_string(elems: Vec<String>) -> PyResult<Vec<String>> {
    let order = uacalc::lat::NaturalOrder;
    Ok(uacalc::lat::ordered_sets::maximals(&elems, &order))
}

/// Run the main test function for ordered_sets
#[pyfunction]
fn ordered_sets_main() -> PyResult<String> {
    // Capture output from the main function
    let lst = vec![2, 3, 6, 35, 35 * 5];
    
    // Define divisibility order where a ≤ b if b % a == 0
    struct DivOrder;
    impl uacalc::lat::Order<i32> for DivOrder {
        fn leq(&self, a: &i32, b: &i32) -> bool {
            if *a == 0 { return true; }  // 0 divides everything by convention
            if *b == 0 { return *a == 0; }
            *a != 0 && *b % *a == 0
        }
    }
    
    let order = DivOrder;
    let maxs = uacalc::lat::ordered_sets::maximals(&lst, &order);
    
    Ok(format!("max's are {:?}", maxs))
}

/// Python wrapper for DiamondLattice
#[pyclass]
pub struct PyDiamondLattice {
    inner: uacalc::lat::DiamondLattice,
}

#[pymethods]
impl PyDiamondLattice {
    /// Create a new DiamondLattice
    #[new]
    fn new() -> Self {
        PyDiamondLattice {
            inner: uacalc::lat::DiamondLattice::new(),
        }
    }
    
    /// Get the element at the given index
    fn get_element(&self, index: usize) -> Option<usize> {
        self.inner.get_element(index)
    }
    
    /// Get the size of the lattice
    fn size(&self) -> usize {
        self.inner.size()
    }
    
    /// Get the universe (all elements)
    fn universe(&self) -> Vec<usize> {
        self.inner.universe().collect()
    }
    
    /// Get the cardinality of the lattice
    fn cardinality(&self) -> usize {
        self.inner.cardinality() as usize
    }
    
    /// Check if a ≤ b in the lattice order
    fn leq(&self, a: usize, b: usize) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Get join irreducibles
    fn join_irreducibles(&self) -> Option<Vec<usize>> {
        self.inner.join_irreducibles()
    }
    
    /// Get meet irreducibles
    fn meet_irreducibles(&self) -> Option<Vec<usize>> {
        self.inner.meet_irreducibles()
    }
    
    /// Get atoms
    fn atoms(&self) -> Option<Vec<usize>> {
        self.inner.atoms()
    }
    
    /// Get coatoms
    fn coatoms(&self) -> Option<Vec<usize>> {
        self.inner.coatoms()
    }
    
    /// Compute join of two elements
    fn join(&self, a: usize, b: usize) -> usize {
        self.inner.join(&a, &b)
    }
    
    /// Compute join of a list of elements
    fn join_list(&self, args: Vec<usize>) -> usize {
        self.inner.join_list(&args)
    }
    
    /// Compute meet of two elements
    fn meet(&self, a: usize, b: usize) -> usize {
        self.inner.meet(&a, &b)
    }
    
    /// Compute meet of a list of elements
    fn meet_list(&self, args: Vec<usize>) -> usize {
        self.inner.meet_list(&args)
    }
    
    /// Get upper covers indices for an element
    fn upper_covers_indices(&self, index: usize) -> Vec<usize> {
        self.inner.upper_covers_indices(index)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        "DiamondLattice".to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        "DiamondLattice()".to_string()
    }
}

/// Python wrapper for BooleanLattice
#[pyclass]
pub struct PyBooleanLattice {
    inner: uacalc::lat::BooleanLattice,
}

#[pymethods]
impl PyBooleanLattice {
    /// Create a new BooleanLattice
    #[new]
    fn new() -> Self {
        PyBooleanLattice {
            inner: uacalc::lat::BooleanLattice::new(),
        }
    }
    
    /// Get the element at the given index
    fn get_element(&self, index: usize) -> Option<usize> {
        self.inner.get_element(index)
    }
    
    /// Get the size of the lattice
    fn size(&self) -> usize {
        self.inner.size()
    }
    
    /// Get the universe (all elements)
    fn universe(&self) -> Vec<usize> {
        self.inner.universe().collect()
    }
    
    /// Get the cardinality of the lattice
    fn cardinality(&self) -> usize {
        self.inner.cardinality() as usize
    }
    
    /// Check if a ≤ b in the lattice order
    fn leq(&self, a: usize, b: usize) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Get join irreducibles
    fn join_irreducibles(&self) -> Option<Vec<usize>> {
        self.inner.join_irreducibles()
    }
    
    /// Get meet irreducibles
    fn meet_irreducibles(&self) -> Option<Vec<usize>> {
        self.inner.meet_irreducibles()
    }
    
    /// Get atoms
    fn atoms(&self) -> Option<Vec<usize>> {
        self.inner.atoms()
    }
    
    /// Get coatoms
    fn coatoms(&self) -> Option<Vec<usize>> {
        self.inner.coatoms()
    }
    
    /// Compute join of two elements
    fn join(&self, a: usize, b: usize) -> usize {
        self.inner.join(&a, &b)
    }
    
    /// Compute join of a list of elements
    fn join_list(&self, args: Vec<usize>) -> usize {
        self.inner.join_list(&args)
    }
    
    /// Compute meet of two elements
    fn meet(&self, a: usize, b: usize) -> usize {
        self.inner.meet(&a, &b)
    }
    
    /// Compute meet of a list of elements
    fn meet_list(&self, args: Vec<usize>) -> usize {
        self.inner.meet_list(&args)
    }
    
    /// Get upper covers indices for an element
    fn upper_covers_indices(&self, index: usize) -> Vec<usize> {
        self.inner.upper_covers_indices(index)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        "BooleanLattice".to_string()
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        "BooleanLattice()".to_string()
    }
}


/// Create a lattice from a meet operation using integers for labels
#[pyfunction]
fn py_lattice_from_meet(name: String, meet: &Bound<'_, PyAny>) -> PyResult<PyBasicLattice> {
    // Try to extract PyIntOperation
    if let Ok(py_int_op) = meet.extract::<PyRef<'_, PyIntOperation>>() {
        // Clone the inner operation to ensure we have ownership
        let op: Box<dyn Operation> = Box::new(py_int_op.inner.clone());
        match lattices::lattice_from_meet(name, op.as_ref()) {
            Ok(basic_lat) => Ok(PyBasicLattice {
                inner: BasicLatticeInner::Int32(std::sync::Arc::new(std::sync::Mutex::new(basic_lat))),
            }),
            Err(e) => Err(PyValueError::new_err(format!("Failed to create BasicLattice: {}", e))),
        }
    }
    // Try to extract PyBasicOperation
    else if let Ok(py_basic_op) = meet.extract::<PyRef<'_, PyBasicOperation>>() {
        // Clone the inner operation to ensure we have ownership
        let op: Box<dyn Operation> = Box::new(py_basic_op.inner.clone());
        match lattices::lattice_from_meet(name, op.as_ref()) {
            Ok(basic_lat) => Ok(PyBasicLattice {
                inner: BasicLatticeInner::Int32(std::sync::Arc::new(std::sync::Mutex::new(basic_lat))),
            }),
            Err(e) => Err(PyValueError::new_err(format!("Failed to create BasicLattice: {}", e))),
        }
    }
    else {
        Err(PyValueError::new_err(
            "lattice_from_meet requires an IntOperation or BasicOperation instance"
        ))
    }
}

/// Create a lattice from a join operation using integers for labels
#[pyfunction]
fn py_lattice_from_join(name: String, join: &Bound<'_, PyAny>) -> PyResult<PyBasicLattice> {
    // Try to extract PyIntOperation
    if let Ok(py_int_op) = join.extract::<PyRef<'_, PyIntOperation>>() {
        // Clone the inner operation to ensure we have ownership
        let op: Box<dyn Operation> = Box::new(py_int_op.inner.clone());
        match lattices::lattice_from_join(name, op.as_ref()) {
            Ok(basic_lat) => Ok(PyBasicLattice {
                inner: BasicLatticeInner::Int32(std::sync::Arc::new(std::sync::Mutex::new(basic_lat))),
            }),
            Err(e) => Err(PyValueError::new_err(format!("Failed to create BasicLattice: {}", e))),
        }
    }
    // Try to extract PyBasicOperation
    else if let Ok(py_basic_op) = join.extract::<PyRef<'_, PyBasicOperation>>() {
        // Clone the inner operation to ensure we have ownership
        let op: Box<dyn Operation> = Box::new(py_basic_op.inner.clone());
        match lattices::lattice_from_join(name, op.as_ref()) {
            Ok(basic_lat) => Ok(PyBasicLattice {
                inner: BasicLatticeInner::Int32(std::sync::Arc::new(std::sync::Mutex::new(basic_lat))),
            }),
            Err(e) => Err(PyValueError::new_err(format!("Failed to create BasicLattice: {}", e))),
        }
    }
    else {
        Err(PyValueError::new_err(
            "lattice_from_join requires an IntOperation or BasicOperation instance"
        ))
    }
}

/// Create a lattice from a meet operation with custom universe
#[pyfunction]
fn py_lattice_from_meet_with_universe(
    name: String,
    univ: Vec<i32>,
    meet: &Bound<'_, PyAny>
) -> PyResult<PyBasicLattice> {
    // Try to extract PyIntOperation
    if let Ok(py_int_op) = meet.extract::<PyRef<'_, PyIntOperation>>() {
        // Clone the inner operation to ensure we have ownership
        let op: Box<dyn Operation> = Box::new(py_int_op.inner.clone());
        match lattices::lattice_from_meet_with_universe(name, univ, op.as_ref()) {
            Ok(basic_lat) => Ok(PyBasicLattice {
                inner: BasicLatticeInner::Int32(std::sync::Arc::new(std::sync::Mutex::new(basic_lat))),
            }),
            Err(e) => Err(PyValueError::new_err(format!("Failed to create BasicLattice: {}", e))),
        }
    }
    // Try to extract PyBasicOperation
    else if let Ok(py_basic_op) = meet.extract::<PyRef<'_, PyBasicOperation>>() {
        // Clone the inner operation to ensure we have ownership
        let op: Box<dyn Operation> = Box::new(py_basic_op.inner.clone());
        match lattices::lattice_from_meet_with_universe(name, univ, op.as_ref()) {
            Ok(basic_lat) => Ok(PyBasicLattice {
                inner: BasicLatticeInner::Int32(std::sync::Arc::new(std::sync::Mutex::new(basic_lat))),
            }),
            Err(e) => Err(PyValueError::new_err(format!("Failed to create BasicLattice: {}", e))),
        }
    }
    else {
        Err(PyValueError::new_err(
            "lattice_from_meet_with_universe requires an IntOperation or BasicOperation instance"
        ))
    }
}

/// Create a lattice from a join operation with custom universe
#[pyfunction]
fn py_lattice_from_join_with_universe(
    name: String,
    univ: Vec<i32>,
    join: &Bound<'_, PyAny>
) -> PyResult<PyBasicLattice> {
    // Try to extract PyIntOperation
    if let Ok(py_int_op) = join.extract::<PyRef<'_, PyIntOperation>>() {
        // Clone the inner operation to ensure we have ownership
        let op: Box<dyn Operation> = Box::new(py_int_op.inner.clone());
        match lattices::lattice_from_join_with_universe(name, univ, op.as_ref()) {
            Ok(basic_lat) => Ok(PyBasicLattice {
                inner: BasicLatticeInner::Int32(std::sync::Arc::new(std::sync::Mutex::new(basic_lat))),
            }),
            Err(e) => Err(PyValueError::new_err(format!("Failed to create BasicLattice: {}", e))),
        }
    }
    // Try to extract PyBasicOperation
    else if let Ok(py_basic_op) = join.extract::<PyRef<'_, PyBasicOperation>>() {
        // Clone the inner operation to ensure we have ownership
        let op: Box<dyn Operation> = Box::new(py_basic_op.inner.clone());
        match lattices::lattice_from_join_with_universe(name, univ, op.as_ref()) {
            Ok(basic_lat) => Ok(PyBasicLattice {
                inner: BasicLatticeInner::Int32(std::sync::Arc::new(std::sync::Mutex::new(basic_lat))),
            }),
            Err(e) => Err(PyValueError::new_err(format!("Failed to create BasicLattice: {}", e))),
        }
    }
    else {
        Err(PyValueError::new_err(
            "lattice_from_join_with_universe requires an IntOperation or BasicOperation instance"
        ))
    }
}

/// Convert a congruence lattice to a small lattice
#[pyfunction]
fn py_con_to_small_lattice(con: &Bound<'_, PyAny>, _py: Python) -> PyResult<PyObject> {
    use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;
    
    // Try to extract PyCongruenceLattice
    if let Ok(py_con_lat) = con.extract::<PyRef<'_, PyCongruenceLattice>>() {
        // Clone the inner CongruenceLattice since we need mutable access
        let mut con_lat = py_con_lat.inner.clone();
        
        // Call the Rust function
        match uacalc::lat::lattices::con_to_small_lattice(&mut con_lat) {
            Ok(_small_lat) => {
                // SmallLattice is a trait, so we can't directly return it to Python
                // TODO: Create a PySmallLattice wrapper type or convert to OrderedSet/BasicLattice
                Err(PyValueError::new_err("con_to_small_lattice is implemented in Rust but needs a PySmallLattice wrapper type to be fully exposed to Python. Consider using the BasicLattice view of the CongruenceLattice instead."))
            }
            Err(e) => Err(PyValueError::new_err(format!("Failed to convert congruence lattice to small lattice: {}", e)))
        }
    } else {
        Err(PyValueError::new_err("con_to_small_lattice requires a CongruenceLattice instance"))
    }
}

/// Create the dual of a basic lattice
#[pyfunction]
fn py_dual(lat: &Bound<'_, PyAny>, _py: Python) -> PyResult<PyObject> {
    // Try to extract PyBasicLattice
    if let Ok(_py_basic_lat) = lat.extract::<PyRef<'_, PyBasicLattice>>() {
        // The dual function takes ownership of BasicLattice, which is problematic from Python
        // since BasicLattice is wrapped in Arc<Mutex<...>> and doesn't implement Clone easily.
        // TODO: Either implement Clone for BasicLattice or change dual to take a reference
        Err(PyValueError::new_err("dual is implemented in Rust but requires BasicLattice to implement Clone or dual to take a reference. This is a known limitation that needs to be addressed."))
    } else {
        Err(PyValueError::new_err("dual requires a BasicLattice instance"))
    }
}

/// Python wrapper for LatticeGraphData
#[pyclass]
pub struct PyLatticeGraphData {
    inner: uacalc::lat::LatticeGraphData,
}

#[pymethods]
impl PyLatticeGraphData {
    /// Get the nodes in the graph
    fn nodes(&self) -> Vec<(usize, String, String)> {
        self.inner.nodes.iter()
            .map(|n| (n.id, n.label.clone(), n.element.clone()))
            .collect()
    }
    
    /// Get the edges in the graph
    fn edges(&self) -> Vec<(usize, usize, Option<String>)> {
        self.inner.edges.iter()
            .map(|e| (e.source, e.target, e.label.clone()))
            .collect()
    }
    
    /// Get node labels as a dictionary
    fn node_labels(&self) -> std::collections::HashMap<usize, String> {
        self.inner.node_labels.clone()
    }
    
    /// Get edge labels as a dictionary
    fn edge_labels(&self) -> Option<std::collections::HashMap<(usize, usize), String>> {
        self.inner.edge_labels.clone()
    }
    
    /// Convert to NetworkX DiGraph if networkx is available
    fn to_networkx(&self, py: Python) -> PyResult<PyObject> {
        match py.import_bound("networkx") {
            Ok(nx) => {
                let graph = nx.getattr("DiGraph")?.call0()?;
                
                // Add nodes with attributes
                // NetworkX add_node(node, **attr) accepts keyword arguments for attributes
                for node in &self.inner.nodes {
                    // Add node first, then set attributes via nodes dict
                    graph.call_method1("add_node", (node.id,))?;
                    // Set node attributes via the nodes view
                    if let Ok(nodes_view) = graph.getattr("nodes") {
                        if let Ok(node_attrs) = nodes_view.call_method1("__getitem__", (node.id,)) {
                            if let Ok(node_dict) = node_attrs.downcast::<PyDict>() {
                                node_dict.set_item("label", node.label.clone())?;
                            }
                        }
                    }
                }
                
                // Add edges with attributes
                // NetworkX add_edge(u, v, **attr) accepts keyword arguments for attributes
                for edge in &self.inner.edges {
                    graph.call_method1("add_edge", (edge.source, edge.target))?;
                    // Set edge attributes if label exists
                    if let Some(ref label) = edge.label {
                        if let Ok(edges_view) = graph.getattr("edges") {
                            if let Ok(edge_attrs) = edges_view.call_method1("__getitem__", ((edge.source, edge.target),)) {
                                if let Ok(edge_dict) = edge_attrs.downcast::<PyDict>() {
                                    edge_dict.set_item("label", label.clone())?;
                                }
                            }
                        }
                    }
                }
                
                Ok(graph.into())
            }
            Err(_) => Err(PyValueError::new_err("networkx not installed. Install with: pip install uacalc[drawing]"))
        }
    }
    
    /// Convert to DOT format (Graphviz)
    fn to_dot(&self) -> String {
        self.inner.to_dot()
    }
    
    /// Convert to Mermaid format
    fn to_mermaid(&self) -> String {
        self.inner.to_mermaid()
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        format!("LatticeGraphData(nodes: {}, edges: {})", self.inner.nodes.len(), self.inner.edges.len())
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("LatticeGraphData(nodes: {}, edges: {})", self.inner.nodes.len(), self.inner.edges.len())
    }
}

/// Python wrapper for BasicLattice
/// This is a type-erased wrapper that can hold BasicLattice<Partition> or BasicLattice<BasicSet>
#[pyclass]
pub struct PyBasicLattice {
    pub(crate) inner: BasicLatticeInner,
}

#[pymethods]
impl PyBasicLattice {
    /// Create a BasicLattice from a CongruenceLattice
    #[new]
    #[pyo3(signature = (name, con_lat, label=true))]
    fn new(name: String, con_lat: &Bound<'_, PyAny>, label: bool) -> PyResult<Self> {
        // Try to extract PyCongruenceLattice
        use crate::alg::conlat::congruence_lattice::PyCongruenceLattice;
        use uacalc::lat::Lattice;
        if let Ok(py_con_lat) = con_lat.extract::<PyRef<'_, PyCongruenceLattice>>() {
            // Create BasicLattice from the Rust CongruenceLattice using new_from_lattice
            // since PyCongruenceLattice uses CongruenceLattice<i32> which implements Lattice<Partition>
            match uacalc::lat::BasicLattice::new_from_lattice(
                name,
                &py_con_lat.inner as &dyn Lattice<uacalc::alg::conlat::Partition>,
            ) {
                Ok(basic_lat) => {
                    Ok(PyBasicLattice {
                        inner: BasicLatticeInner::Partition(std::sync::Arc::new(std::sync::Mutex::new(basic_lat))),
                    })
                }
                Err(e) => Err(PyValueError::new_err(format!("Failed to create BasicLattice: {}", e))),
            }
        } else {
            Err(PyValueError::new_err("BasicLattice creation requires a CongruenceLattice instance"))
        }
    }
    
    /// Create a BasicLattice from an OrderedSet<i32>
    #[staticmethod]
    fn new_from_poset(name: String, poset: PyRef<'_, PyOrderedSet>) -> PyResult<Self> {
        // Extract the inner OrderedSet
        let inner_poset = poset.inner.lock().unwrap();
        // Clone the OrderedSet (we need to convert Arc<Mutex<OrderedSet>> to OrderedSet)
        // Since we can't easily clone, we'll need to reconstruct from the poset
        // For now, this is a limitation - we'd need to add a clone method or use a different approach
        // For BasicLattice<i32>, we can create from the poset's universe and upper covers
        let univ = inner_poset.univ();
        let universe: Vec<i32> = univ.iter().map(|e| *e.get_underlying_object()).collect();
        
        // Build upper covers list
        let mut upper_covers_list: Vec<Vec<i32>> = Vec::new();
        for po_elem in univ {
            let mut covers = Vec::new();
            let upper_covers = inner_poset.get_upper_covers(&po_elem);
            for cover_po in upper_covers {
                covers.push(*cover_po.get_underlying_object());
            }
            upper_covers_list.push(covers);
        }
        
        // Create a new OrderedSet and then BasicLattice from it
        drop(inner_poset); // Release the lock
        match uacalc::lat::ordered_set::OrderedSet::new(Some(name.clone()), universe, upper_covers_list) {
            Ok(new_poset) => {
                match uacalc::lat::BasicLattice::new_from_poset(name, new_poset) {
                    Ok(basic_lat) => Ok(PyBasicLattice {
                        inner: BasicLatticeInner::Int32(std::sync::Arc::new(std::sync::Mutex::new(basic_lat))),
                    }),
                    Err(e) => Err(PyValueError::new_err(format!("Failed to create BasicLattice: {}", e))),
                }
            }
            Err(e) => Err(PyValueError::new_err(format!("Failed to create OrderedSet: {}", e))),
        }
    }
    
    /// Get cardinality
    fn cardinality(&self) -> usize {
        match &self.inner {
            BasicLatticeInner::Partition(inner) => inner.lock().unwrap().cardinality(),
            BasicLatticeInner::BasicSet(inner) => inner.lock().unwrap().cardinality(),
            BasicLatticeInner::Int32(inner) => inner.lock().unwrap().cardinality(),
        }
    }
    
    /// Get the name
    fn name(&self) -> String {
        match &self.inner {
            BasicLatticeInner::Partition(inner) => inner.lock().unwrap().name().to_string(),
            BasicLatticeInner::BasicSet(inner) => inner.lock().unwrap().name().to_string(),
            BasicLatticeInner::Int32(inner) => inner.lock().unwrap().name().to_string(),
        }
    }
    
    /// Convert to graph data
    fn to_graph_data(&self) -> PyResult<PyLatticeGraphData> {
        let graph_data = match &self.inner {
            BasicLatticeInner::Partition(inner) => {
                let inner = inner.lock().unwrap();
                inner.to_graph_data()
            }
            BasicLatticeInner::BasicSet(inner) => {
                let inner = inner.lock().unwrap();
                inner.to_graph_data()
            }
            BasicLatticeInner::Int32(inner) => {
                let inner = inner.lock().unwrap();
                inner.to_graph_data()
            }
        };
        Ok(PyLatticeGraphData { inner: graph_data })
    }
    
    /// Convert to NetworkX DiGraph if networkx is available
    fn to_networkx(&self, py: Python) -> PyResult<PyObject> {
        let graph_data = self.to_graph_data()?;
        graph_data.to_networkx(py)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        format!("BasicLattice({})", self.name())
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("BasicLattice({})", self.name())
    }
    
    /// Get universe as a list of integers (for BasicLattice<i32> only)
    fn universe(&self) -> PyResult<Vec<i32>> {
        match &self.inner {
            BasicLatticeInner::Int32(inner) => {
                let inner = inner.lock().unwrap();
                let univ_list = inner.get_universe_list();
                Ok(univ_list.iter()
                    .map(|po_elem| *po_elem.get_underlying_object())
                    .collect())
            }
            _ => Err(PyValueError::new_err("universe() is only available for BasicLattice<i32> created from operations")),
        }
    }
    
    /// Check if a ≤ b (for BasicLattice<i32> only)
    fn leq(&self, a: i32, b: i32) -> PyResult<bool> {
        match &self.inner {
            BasicLatticeInner::Int32(inner) => {
                let inner = inner.lock().unwrap();
                let univ_list = inner.get_universe_list();
                
                // Find POElems for a and b
                let po_a = univ_list.iter().find(|e| *e.get_underlying_object() == a);
                let po_b = univ_list.iter().find(|e| *e.get_underlying_object() == b);
                
                match (po_a, po_b) {
                    (Some(pa), Some(pb)) => Ok(inner.leq(pa, pb)),
                    _ => Err(PyValueError::new_err(format!("Elements {} or {} not found in universe", a, b))),
                }
            }
            _ => Err(PyValueError::new_err("leq() is only available for BasicLattice<i32> created from operations")),
        }
    }
    
    /// Compute join of two elements (for BasicLattice<i32> only)
    fn join(&self, a: i32, b: i32) -> PyResult<i32> {
        match &self.inner {
            BasicLatticeInner::Int32(inner) => {
                let inner = inner.lock().unwrap();
                let univ_list = inner.get_universe_list();
                
                // Find POElems for a and b
                let po_a = univ_list.iter().find(|e| *e.get_underlying_object() == a);
                let po_b = univ_list.iter().find(|e| *e.get_underlying_object() == b);
                
                match (po_a, po_b) {
                    (Some(pa), Some(pb)) => {
                        let result = inner.join(pa, pb);
                        Ok(*result.get_underlying_object())
                    }
                    _ => Err(PyValueError::new_err(format!("Elements {} or {} not found in universe", a, b))),
                }
            }
            _ => Err(PyValueError::new_err("join() is only available for BasicLattice<i32> created from operations")),
        }
    }
    
    /// Compute meet of two elements (for BasicLattice<i32> only)
    fn meet(&self, a: i32, b: i32) -> PyResult<i32> {
        match &self.inner {
            BasicLatticeInner::Int32(inner) => {
                let inner = inner.lock().unwrap();
                let univ_list = inner.get_universe_list();
                
                // Find POElems for a and b
                let po_a = univ_list.iter().find(|e| *e.get_underlying_object() == a);
                let po_b = univ_list.iter().find(|e| *e.get_underlying_object() == b);
                
                match (po_a, po_b) {
                    (Some(pa), Some(pb)) => {
                        let result = inner.meet(pa, pb);
                        Ok(*result.get_underlying_object())
                    }
                    _ => Err(PyValueError::new_err(format!("Elements {} or {} not found in universe", a, b))),
                }
            }
            _ => Err(PyValueError::new_err("meet() is only available for BasicLattice<i32> created from operations")),
        }
    }
    
    /// Get the filter (all elements ≥ the given element) (for BasicLattice<i32> only).
    ///
    /// Args:
    ///     element: The element to get the filter for
    ///
    /// Returns:
    ///     List[int]: List of all elements greater than or equal to the given element
    fn filter(&self, element: i32) -> PyResult<Vec<i32>> {
        match &self.inner {
            BasicLatticeInner::Int32(inner) => {
                let inner = inner.lock().unwrap();
                let poset = inner.get_poset();
                let univ_list = inner.get_universe_list();
                
                let po_elem = univ_list.iter()
                    .find(|e| *e.get_underlying_object() == element)
                    .ok_or_else(|| PyValueError::new_err(format!("Element {} not found in universe", element)))?;
                
                let filter = po_elem.filter(poset);
                Ok(filter.iter()
                    .map(|e| *e.get_underlying_object())
                    .collect())
            }
            _ => Err(PyValueError::new_err("filter() is only available for BasicLattice<i32> created from operations")),
        }
    }
    
    /// Get the ideal (all elements ≤ the given element) (for BasicLattice<i32> only).
    ///
    /// Args:
    ///     element: The element to get the ideal for
    ///
    /// Returns:
    ///     List[int]: List of all elements less than or equal to the given element
    fn ideal(&self, element: i32) -> PyResult<Vec<i32>> {
        match &self.inner {
            BasicLatticeInner::Int32(inner) => {
                let inner = inner.lock().unwrap();
                let poset = inner.get_poset();
                let univ_list = inner.get_universe_list();
                
                let po_elem = univ_list.iter()
                    .find(|e| *e.get_underlying_object() == element)
                    .ok_or_else(|| PyValueError::new_err(format!("Element {} not found in universe", element)))?;
                
                let ideal = po_elem.ideal(poset);
                Ok(ideal.iter()
                    .map(|e| *e.get_underlying_object())
                    .collect())
            }
            _ => Err(PyValueError::new_err("ideal() is only available for BasicLattice<i32> created from operations")),
        }
    }
    
    /// Get join irreducibles (for BasicLattice<Partition> only, created from CongruenceLattice).
    ///
    /// Returns:
    ///     List[Partition]: List of join irreducible elements
    fn join_irreducibles(&self) -> PyResult<Vec<crate::alg::conlat::partition::PyPartition>> {
        match &self.inner {
            BasicLatticeInner::Partition(inner) => {
                let mut inner = inner.lock().unwrap();
                // Call the inherent method, not the trait method
                let jis: &[std::sync::Arc<uacalc::lat::ordered_set::POElem<uacalc::alg::conlat::Partition>>] = 
                    uacalc::lat::BasicLattice::join_irreducibles(&mut *inner);
                let mut result = Vec::new();
                for po_elem_arc in jis {
                    // po_elem_arc is &Arc<POElem<Partition>>, dereference to get &POElem<Partition>
                    let po_elem: &uacalc::lat::ordered_set::POElem<uacalc::alg::conlat::Partition> = po_elem_arc.deref();
                    let part = po_elem.get_underlying_object();
                    result.push(crate::alg::conlat::partition::PyPartition { inner: part.clone() });
                }
                Ok(result)
            }
            _ => Err(PyValueError::new_err("join_irreducibles() is only available for BasicLattice<Partition> created from CongruenceLattice")),
        }
    }
    
    /// Get zero (bottom) element (for BasicLattice<Partition> only).
    ///
    /// Returns:
    ///     Partition: The zero (bottom) element
    fn zero(&self) -> PyResult<crate::alg::conlat::partition::PyPartition> {
        match &self.inner {
            BasicLatticeInner::Partition(inner) => {
                let inner = inner.lock().unwrap();
                let zero = inner.zero();
                // zero is Arc<POElem<Partition>>, dereference to get &POElem<Partition>
                let po_elem: &uacalc::lat::ordered_set::POElem<uacalc::alg::conlat::Partition> = zero.deref();
                let part = po_elem.get_underlying_object();
                Ok(crate::alg::conlat::partition::PyPartition { inner: part.clone() })
            }
            _ => Err(PyValueError::new_err("zero() is only available for BasicLattice<Partition> created from CongruenceLattice")),
        }
    }
}

/// Python wrapper for OrderedSet<i32>
/// This provides Python bindings for creating and manipulating partially ordered sets
#[pyclass]
pub struct PyOrderedSet {
    inner: std::sync::Arc<std::sync::Mutex<uacalc::lat::ordered_set::OrderedSet<i32>>>,
}

#[pymethods]
impl PyOrderedSet {
    /// Create a new OrderedSet from a universe and upper covers.
    ///
    /// Args:
    ///     name: Optional name for the poset
    ///     universe: List of integers representing the universe
    ///     upper_covers: List of lists, where upper_covers[i] contains elements that directly cover universe[i]
    ///
    /// Returns:
    ///     OrderedSet: A new OrderedSet instance
    ///
    /// Raises:
    ///     ValueError: If the poset structure is invalid
    #[new]
    #[pyo3(signature = (universe, upper_covers, *, name=None))]
    fn new(universe: Vec<i32>, upper_covers: Vec<Vec<i32>>, name: Option<String>) -> PyResult<Self> {
        match uacalc::lat::ordered_set::OrderedSet::new(name, universe, upper_covers) {
            Ok(poset) => Ok(PyOrderedSet {
                inner: std::sync::Arc::new(std::sync::Mutex::new(poset)),
            }),
            Err(e) => Err(PyValueError::new_err(format!("Failed to create OrderedSet: {}", e))),
        }
    }
    
    /// Get the name of this poset.
    fn name(&self) -> Option<String> {
        self.inner.lock().unwrap().name().map(|s| s.to_string())
    }
    
    /// Get the cardinality (number of elements) of this poset.
    fn cardinality(&self) -> usize {
        self.inner.lock().unwrap().univ().len()
    }
    
    /// Get the universe as a list of integers.
    fn universe(&self) -> Vec<i32> {
        let poset = self.inner.lock().unwrap();
        poset.univ()
            .iter()
            .map(|elem| *elem.get_underlying_object())
            .collect()
    }
    
    /// Check if a ≤ b in this poset.
    ///
    /// Args:
    ///     a: First element (integer)
    ///     b: Second element (integer)
    ///
    /// Returns:
    ///     bool: True if a ≤ b, False otherwise
    fn leq(&self, a: i32, b: i32) -> PyResult<bool> {
        let poset = self.inner.lock().unwrap();
        let univ = poset.univ();
        
        let elem_a = univ.iter().find(|e| *e.get_underlying_object() == a);
        let elem_b = univ.iter().find(|e| *e.get_underlying_object() == b);
        
        match (elem_a, elem_b) {
            (Some(a_elem), Some(b_elem)) => Ok(poset.leq(a_elem, b_elem)),
            _ => Err(PyValueError::new_err(format!("Elements {} or {} not found in universe", a, b))),
        }
    }
    
    /// Get upper covers (elements that directly cover the given element).
    ///
    /// Args:
    ///     element: The element to get upper covers for
    ///
    /// Returns:
    ///     List[int]: List of elements that directly cover the given element
    fn get_upper_covers(&self, element: i32) -> PyResult<Vec<i32>> {
        let poset = self.inner.lock().unwrap();
        let univ = poset.univ();
        
        let elem = univ.iter()
            .find(|e| *e.get_underlying_object() == element)
            .ok_or_else(|| PyValueError::new_err(format!("Element {} not found in universe", element)))?;
        
        let covers = poset.get_upper_covers(elem);
        Ok(covers.iter()
            .map(|e| *e.get_underlying_object())
            .collect())
    }
    
    /// Get lower covers (elements directly covered by the given element).
    ///
    /// Args:
    ///     element: The element to get lower covers for
    ///
    /// Returns:
    ///     List[int]: List of elements directly covered by the given element
    fn get_lower_covers(&self, element: i32) -> PyResult<Vec<i32>> {
        let poset = self.inner.lock().unwrap();
        let univ = poset.univ();
        
        let elem = univ.iter()
            .find(|e| *e.get_underlying_object() == element)
            .ok_or_else(|| PyValueError::new_err(format!("Element {} not found in universe", element)))?;
        
        let covers = poset.get_lower_covers(elem);
        Ok(covers.iter()
            .map(|e| *e.get_underlying_object())
            .collect())
    }
    
    /// Get the filter (all elements ≥ the given element).
    ///
    /// Args:
    ///     element: The element to get the filter for
    ///
    /// Returns:
    ///     List[int]: List of all elements greater than or equal to the given element
    fn filter(&self, element: i32) -> PyResult<Vec<i32>> {
        let poset = self.inner.lock().unwrap();
        let univ = poset.univ();
        
        let elem = univ.iter()
            .find(|e| *e.get_underlying_object() == element)
            .ok_or_else(|| PyValueError::new_err(format!("Element {} not found in universe", element)))?;
        
        let filter = elem.filter(&poset);
        Ok(filter.iter()
            .map(|e| *e.get_underlying_object())
            .collect())
    }
    
    /// Get the ideal (all elements ≤ the given element).
    ///
    /// Args:
    ///     element: The element to get the ideal for
    ///
    /// Returns:
    ///     List[int]: List of all elements less than or equal to the given element
    fn ideal(&self, element: i32) -> PyResult<Vec<i32>> {
        let poset = self.inner.lock().unwrap();
        let univ = poset.univ();
        
        let elem = univ.iter()
            .find(|e| *e.get_underlying_object() == element)
            .ok_or_else(|| PyValueError::new_err(format!("Element {} not found in universe", element)))?;
        
        let ideal = elem.ideal(&poset);
        Ok(ideal.iter()
            .map(|e| *e.get_underlying_object())
            .collect())
    }
    
    /// Convert to graph data for visualization.
    ///
    /// Args:
    ///     edge_labels: Optional dictionary mapping (source, target) tuples to edge labels
    ///
    /// Returns:
    ///     LatticeGraphData: Graph data structure for visualization
    fn to_graph_data(&self, edge_labels: Option<&Bound<'_, PyDict>>) -> PyResult<PyLatticeGraphData> {
        use uacalc::lat::ordered_set::Edge;
        use std::collections::HashMap;
        
        let poset = self.inner.lock().unwrap();
        
        // Convert Python dict to Rust HashMap if provided
        let edge_labels_map: Option<HashMap<Edge, String>> = if let Some(labels) = edge_labels {
            let mut map = HashMap::new();
            for (key, value) in labels.iter() {
                if let Ok(tuple) = key.extract::<(String, String)>() {
                    if let Ok(label) = value.extract::<String>() {
                        map.insert(Edge::new(tuple.0, tuple.1), label);
                    }
                }
            }
            Some(map)
        } else {
            None
        };
        
        let graph_data = poset.to_graph_data(edge_labels_map.as_ref());
        Ok(PyLatticeGraphData { inner: graph_data })
    }
    
    /// Convert to NetworkX DiGraph if networkx is available
    fn to_networkx(&self, py: Python, edge_labels: Option<&Bound<'_, PyDict>>) -> PyResult<PyObject> {
        let graph_data = self.to_graph_data(edge_labels)?;
        graph_data.to_networkx(py)
    }
    
    /// Create an OrderedSet from filters.
    ///
    /// A filter for an element x is the set of all elements y such that x ≤ y.
    /// This method converts filters to upper covers and creates an OrderedSet.
    ///
    /// Args:
    ///     universe: List of integers representing the universe
    ///     filters: List of lists, where filters[i] contains all elements ≥ universe[i]
    ///     name: Optional name for the poset
    ///
    /// Returns:
    ///     OrderedSet: An OrderedSet created from the filters
    ///
    /// Raises:
    ///     ValueError: If universe and filters have different lengths or structure is invalid
    #[staticmethod]
    #[pyo3(signature = (universe, filters, *, name=None))]
    fn from_filters(universe: Vec<i32>, filters: Vec<Vec<i32>>, name: Option<String>) -> PyResult<PyOrderedSet> {
        match uacalc::lat::ordered_set::OrderedSet::ordered_set_from_filters(name, universe, filters) {
            Ok(poset) => Ok(PyOrderedSet {
                inner: std::sync::Arc::new(std::sync::Mutex::new(poset)),
            }),
            Err(e) => Err(PyValueError::new_err(format!("Failed to create OrderedSet from filters: {}", e))),
        }
    }
    
    /// Create an OrderedSet from a BasicLattice.
    ///
    /// This static method converts a lattice to an OrderedSet by computing
    /// upper covers using join irreducibles.
    ///
    /// Args:
    ///     lattice: The BasicLattice to convert
    ///     name: Optional name for the resulting OrderedSet
    ///
    /// Returns:
    ///     OrderedSet: An OrderedSet representing the lattice structure
    #[staticmethod]
    fn from_lattice(lattice: &Bound<'_, PyAny>, name: Option<String>) -> PyResult<PyOrderedSet> {
        // Try to extract as BasicLattice
        if let Ok(basic_lat) = lattice.extract::<PyRef<'_, PyBasicLattice>>() {
            // Get the poset from BasicLattice<i32>
            match &basic_lat.inner {
                BasicLatticeInner::Int32(inner) => {
                    let inner = inner.lock().unwrap();
                    let poset = inner.get_poset();
                    let univ_list = inner.get_universe_list();
                    
                    // Build upper covers for each element
                    let mut upper_covers_list: Vec<Vec<i32>> = Vec::new();
                    let universe: Vec<i32> = univ_list.iter()
                        .map(|e| *e.get_underlying_object())
                        .collect();
                    
                    for po_elem in univ_list {
                        let mut covers = Vec::new();
                        let upper_covers = poset.get_upper_covers(&po_elem);
                        for cover_po in upper_covers {
                            covers.push(*cover_po.get_underlying_object());
                        }
                        upper_covers_list.push(covers);
                    }
                    
                    // Create OrderedSet from universe and upper covers
                    match uacalc::lat::ordered_set::OrderedSet::new(name, universe, upper_covers_list) {
                        Ok(poset) => Ok(PyOrderedSet {
                            inner: std::sync::Arc::new(std::sync::Mutex::new(poset)),
                        }),
                        Err(e) => Err(PyValueError::new_err(format!("Failed to create OrderedSet: {}", e))),
                    }
                }
                _ => Err(PyValueError::new_err(
                    "from_lattice currently only supports BasicLattice<i32> created from operations"
                )),
            }
        } else {
            Err(PyValueError::new_err(
                "from_lattice requires a BasicLattice instance"
            ))
        }
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        let name = self.name().unwrap_or_else(|| "Unnamed".to_string());
        format!("OrderedSet({}, {} elements)", name, self.cardinality())
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        let name = self.name().map(|n| format!("name={:?}, ", n)).unwrap_or_default();
        format!("OrderedSet({}universe={:?})", name, self.universe())
    }
}

/// Python wrapper for OrderedSet<Partition>
#[pyclass]
pub struct PyOrderedSetPartition {
    pub(crate) inner: std::sync::Arc<std::sync::Mutex<uacalc::lat::ordered_set::OrderedSet<uacalc::alg::conlat::partition::Partition>>>,
}

#[pymethods]
impl PyOrderedSetPartition {
    /// Get the name of this poset.
    fn name(&self) -> Option<String> {
        self.inner.lock().unwrap().name().map(|s| s.to_string())
    }
    
    /// Get the cardinality (number of elements) of this poset.
    fn cardinality(&self) -> usize {
        self.inner.lock().unwrap().univ().len()
    }
    
    /// Get the universe as a list of Partitions.
    fn universe(&self) -> Vec<crate::alg::conlat::partition::PyPartition> {
        let poset = self.inner.lock().unwrap();
        poset.univ()
            .iter()
            .map(|elem| crate::alg::conlat::partition::PyPartition { inner: elem.get_underlying_object().clone() })
            .collect()
    }
    
    /// Check if a ≤ b in this poset.
    fn leq(&self, a: &crate::alg::conlat::partition::PyPartition, b: &crate::alg::conlat::partition::PyPartition) -> PyResult<bool> {
        let poset = self.inner.lock().unwrap();
        let univ = poset.univ();
        
        let elem_a = univ.iter().find(|e| e.get_underlying_object() == &a.inner);
        let elem_b = univ.iter().find(|e| e.get_underlying_object() == &b.inner);
        
        match (elem_a, elem_b) {
            (Some(a_elem), Some(b_elem)) => Ok(poset.leq(a_elem, b_elem)),
            _ => Err(PyValueError::new_err("Elements not found in universe")),
        }
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        let name = self.name().unwrap_or_else(|| "Unnamed".to_string());
        format!("OrderedSet({}, {} elements)", name, self.cardinality())
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("OrderedSetPartition({} elements)", self.cardinality())
    }
}

/// Python wrapper for OrderedSet<BasicSet>
#[pyclass]
pub struct PyOrderedSetBasicSet {
    pub(crate) inner: std::sync::Arc<std::sync::Mutex<uacalc::lat::ordered_set::OrderedSet<uacalc::alg::sublat::BasicSet>>>,
}

#[pymethods]
impl PyOrderedSetBasicSet {
    /// Get the name of this poset.
    fn name(&self) -> Option<String> {
        self.inner.lock().unwrap().name().map(|s| s.to_string())
    }
    
    /// Get the cardinality (number of elements) of this poset.
    fn cardinality(&self) -> usize {
        self.inner.lock().unwrap().univ().len()
    }
    
    /// Get the universe as a list of BasicSets.
    fn universe(&self) -> Vec<crate::alg::sublat::basic_set::PyBasicSet> {
        let poset = self.inner.lock().unwrap();
        poset.univ()
            .iter()
            .map(|elem| crate::alg::sublat::basic_set::PyBasicSet::from_inner(elem.get_underlying_object().clone()))
            .collect()
    }
    
    /// Check if a ≤ b in this poset.
    fn leq(&self, a: &crate::alg::sublat::basic_set::PyBasicSet, b: &crate::alg::sublat::basic_set::PyBasicSet) -> PyResult<bool> {
        let poset = self.inner.lock().unwrap();
        let univ = poset.univ();
        
        let elem_a = univ.iter().find(|e| e.get_underlying_object() == a.get_inner());
        let elem_b = univ.iter().find(|e| e.get_underlying_object() == b.get_inner());
        
        match (elem_a, elem_b) {
            (Some(a_elem), Some(b_elem)) => Ok(poset.leq(a_elem, b_elem)),
            _ => Err(PyValueError::new_err("Elements not found in universe")),
        }
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        let name = self.name().unwrap_or_else(|| "Unnamed".to_string());
        format!("OrderedSet({}, {} elements)", name, self.cardinality())
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("OrderedSetBasicSet({} elements)", self.cardinality())
    }
}

pub fn register_lat_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyDivisibilityOrder>()?;
    m.add_class::<PyPrefixOrder>()?;
    m.add_class::<PyNaturalOrder>()?;
    m.add_class::<PyDiamondLattice>()?;
    m.add_class::<PyBooleanLattice>()?;
    m.add_class::<PyBasicLattice>()?;
    m.add_class::<PyLatticeGraphData>()?;
    m.add_class::<PyOrderedSet>()?;
    m.add_class::<PyOrderedSetPartition>()?;
    m.add_class::<PyOrderedSetBasicSet>()?;
    
    // Export only clean names (without Py prefix)
    m.add("DivisibilityOrder", m.getattr("PyDivisibilityOrder")?)?;
    m.add("PrefixOrder", m.getattr("PyPrefixOrder")?)?;
    m.add("NaturalOrder", m.getattr("PyNaturalOrder")?)?;
    m.add("DiamondLattice", m.getattr("PyDiamondLattice")?)?;
    m.add("BooleanLattice", m.getattr("PyBooleanLattice")?)?;
    // Add OrderedSets functions
    m.add_function(wrap_pyfunction!(maximals_divisibility, m)?)?;
    m.add_function(wrap_pyfunction!(maximals_prefix, m)?)?;
    m.add_function(wrap_pyfunction!(maximals_natural_i32, m)?)?;
    m.add_function(wrap_pyfunction!(maximals_natural_string, m)?)?;
    m.add_function(wrap_pyfunction!(ordered_sets_main, m)?)?;
    
    // Add Lattices factory functions
    m.add_function(wrap_pyfunction!(py_lattice_from_meet, m)?)?;
    m.add_function(wrap_pyfunction!(py_lattice_from_join, m)?)?;
    m.add_function(wrap_pyfunction!(py_lattice_from_meet_with_universe, m)?)?;
    m.add_function(wrap_pyfunction!(py_lattice_from_join_with_universe, m)?)?;
    m.add_function(wrap_pyfunction!(py_con_to_small_lattice, m)?)?;
    m.add_function(wrap_pyfunction!(py_dual, m)?)?;
    
    // Add clean function names
    m.add("lattice_from_meet", m.getattr("py_lattice_from_meet")?)?;
    m.add("lattice_from_join", m.getattr("py_lattice_from_join")?)?;
    m.add("lattice_from_meet_with_universe", m.getattr("py_lattice_from_meet_with_universe")?)?;
    m.add("lattice_from_join_with_universe", m.getattr("py_lattice_from_join_with_universe")?)?;
    m.add("con_to_small_lattice", m.getattr("py_con_to_small_lattice")?)?;
    m.add("dual", m.getattr("py_dual")?)?;
    
    // Export clean names for new classes
    m.add("BasicLattice", m.getattr("PyBasicLattice")?)?;
    m.add("LatticeGraphData", m.getattr("PyLatticeGraphData")?)?;
    m.add("OrderedSet", m.getattr("PyOrderedSet")?)?;
    m.add("OrderedSetPartition", m.getattr("PyOrderedSetPartition")?)?;
    m.add("OrderedSetBasicSet", m.getattr("PyOrderedSetBasicSet")?)?;
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyDivisibilityOrder")?;
    module_dict.del_item("PyPrefixOrder")?;
    module_dict.del_item("PyNaturalOrder")?;
    module_dict.del_item("PyDiamondLattice")?;
    module_dict.del_item("PyBooleanLattice")?;
    module_dict.del_item("PyBasicLattice")?;
    module_dict.del_item("PyLatticeGraphData")?;
    module_dict.del_item("PyOrderedSet")?;
    module_dict.del_item("PyOrderedSetPartition")?;
    module_dict.del_item("PyOrderedSetBasicSet")?;
    
    // Remove the py_* function names from the module to avoid confusion
    module_dict.del_item("py_lattice_from_meet")?;
    module_dict.del_item("py_lattice_from_join")?;
    module_dict.del_item("py_lattice_from_meet_with_universe")?;
    module_dict.del_item("py_lattice_from_join_with_universe")?;
    module_dict.del_item("py_con_to_small_lattice")?;
    module_dict.del_item("py_dual")?;
    
    // Note: Lattice and SmallLattice are traits (interfaces) and cannot be instantiated directly.
    // Python bindings are provided for concrete implementations like DiamondLattice and BooleanLattice.
    
    Ok(())
}
