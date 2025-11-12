use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyDict;
use uacalc::lat::*;
use uacalc::alg::algebra::Algebra;

/// Internal enum to hold either type of BasicLattice
/// Made public(crate) so it can be used in other modules
pub(crate) enum BasicLatticeInner {
    Partition(std::sync::Arc<std::sync::Mutex<uacalc::lat::BasicLattice<uacalc::alg::conlat::Partition>>>),
    BasicSet(std::sync::Arc<std::sync::Mutex<uacalc::lat::BasicLattice<uacalc::alg::sublat::BasicSet>>>),
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

/// Python wrapper for MeetLattice
#[pyclass]
pub struct PyMeetLattice {
    inner: uacalc::lat::lattices::MeetLattice,
}

#[pymethods]
impl PyMeetLattice {
    /// Get the name of this lattice
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    /// Get the universe of this lattice
    fn universe(&self) -> Vec<i32> {
        self.inner.universe().to_vec()
    }
    
    /// Get join irreducibles of this lattice
    fn join_irreducibles(&self) -> Vec<i32> {
        self.inner.join_irreducibles()
    }
    
    /// Get meet irreducibles of this lattice
    fn meet_irreducibles(&self) -> Vec<i32> {
        self.inner.meet_irreducibles()
    }
    
    /// Get atoms of this lattice
    fn atoms(&self) -> Vec<i32> {
        self.inner.atoms()
    }
    
    /// Get coatoms of this lattice
    fn coatoms(&self) -> Vec<i32> {
        self.inner.coatoms()
    }
    
    /// Compute join of two elements
    fn join(&self, a: i32, b: i32) -> i32 {
        self.inner.join(&a, &b)
    }
    
    /// Compute join of a list of elements
    fn join_list(&self, args: Vec<i32>) -> i32 {
        self.inner.join_list(&args)
    }
    
    /// Compute meet of two elements
    fn meet(&self, a: i32, b: i32) -> i32 {
        self.inner.meet(&a, &b)
    }
    
    /// Compute meet of a list of elements
    fn meet_list(&self, args: Vec<i32>) -> i32 {
        self.inner.meet_list(&args)
    }
    
    /// Check if a ≤ b in the lattice order
    fn leq(&self, a: i32, b: i32) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        format!("MeetLattice({})", self.inner.name())
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("MeetLattice({})", self.inner.name())
    }
}

/// Python wrapper for JoinLattice
#[pyclass]
pub struct PyJoinLattice {
    inner: uacalc::lat::lattices::JoinLattice,
}

#[pymethods]
impl PyJoinLattice {
    /// Get the name of this lattice
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    /// Get the universe of this lattice
    fn universe(&self) -> Vec<i32> {
        self.inner.universe().to_vec()
    }
    
    /// Get join irreducibles of this lattice
    fn join_irreducibles(&self) -> Vec<i32> {
        self.inner.join_irreducibles()
    }
    
    /// Get meet irreducibles of this lattice
    fn meet_irreducibles(&self) -> Vec<i32> {
        self.inner.meet_irreducibles()
    }
    
    /// Get atoms of this lattice
    fn atoms(&self) -> Vec<i32> {
        self.inner.atoms()
    }
    
    /// Get coatoms of this lattice
    fn coatoms(&self) -> Vec<i32> {
        self.inner.coatoms()
    }
    
    /// Compute join of two elements
    fn join(&self, a: i32, b: i32) -> i32 {
        self.inner.join(&a, &b)
    }
    
    /// Compute join of a list of elements
    fn join_list(&self, args: Vec<i32>) -> i32 {
        self.inner.join_list(&args)
    }
    
    /// Compute meet of two elements
    fn meet(&self, a: i32, b: i32) -> i32 {
        self.inner.meet(&a, &b)
    }
    
    /// Compute meet of a list of elements
    fn meet_list(&self, args: Vec<i32>) -> i32 {
        self.inner.meet_list(&args)
    }
    
    /// Check if a ≤ b in the lattice order
    fn leq(&self, a: i32, b: i32) -> bool {
        self.inner.leq(&a, &b)
    }
    
    /// Python string representation
    fn __str__(&self) -> String {
        format!("JoinLattice({})", self.inner.name())
    }
    
    /// Python repr representation
    fn __repr__(&self) -> String {
        format!("JoinLattice({})", self.inner.name())
    }
}

/// Create a lattice from a meet operation using integers for labels
#[pyfunction]
fn py_lattice_from_meet(_name: String, _meet: &PyAny) -> PyResult<PyMeetLattice> {
    // For now, return an error since we need a concrete Operation implementation
    Err(PyValueError::new_err("lattice_from_meet requires a concrete Operation implementation which is not yet available"))
}

/// Create a lattice from a join operation using integers for labels
#[pyfunction]
fn py_lattice_from_join(_name: String, _join: &PyAny) -> PyResult<PyJoinLattice> {
    // For now, return an error since we need a concrete Operation implementation
    Err(PyValueError::new_err("lattice_from_join requires a concrete Operation implementation which is not yet available"))
}

/// Create a lattice from a meet operation with custom universe
#[pyfunction]
fn py_lattice_from_meet_with_universe(_name: String, _univ: Vec<i32>, _meet: &PyAny) -> PyResult<PyMeetLattice> {
    // For now, return an error since we need a concrete Operation implementation
    Err(PyValueError::new_err("lattice_from_meet_with_universe requires a concrete Operation implementation which is not yet available"))
}

/// Create a lattice from a join operation with custom universe
#[pyfunction]
fn py_lattice_from_join_with_universe(_name: String, _univ: Vec<i32>, _join: &PyAny) -> PyResult<PyJoinLattice> {
    // For now, return an error since we need a concrete Operation implementation
    Err(PyValueError::new_err("lattice_from_join_with_universe requires a concrete Operation implementation which is not yet available"))
}

/// Convert a congruence lattice to a small lattice (not implemented)
#[pyfunction]
fn py_con_to_small_lattice(_con: &PyAny) -> PyResult<PyObject> {
    Err(PyValueError::new_err("con_to_small_lattice requires CongruenceLattice which is not yet implemented"))
}

/// Create the dual of a basic lattice (not implemented)
#[pyfunction]
fn py_dual(_lat: &PyAny) -> PyResult<PyObject> {
    Err(PyValueError::new_err("dual requires BasicLattice which is not yet implemented"))
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
        match py.import("networkx") {
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
    
    /// Get cardinality
    fn cardinality(&self) -> usize {
        match &self.inner {
            BasicLatticeInner::Partition(inner) => inner.lock().unwrap().cardinality(),
            BasicLatticeInner::BasicSet(inner) => inner.lock().unwrap().cardinality(),
        }
    }
    
    /// Get the name
    fn name(&self) -> String {
        match &self.inner {
            BasicLatticeInner::Partition(inner) => inner.lock().unwrap().name().to_string(),
            BasicLatticeInner::BasicSet(inner) => inner.lock().unwrap().name().to_string(),
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
}

pub fn register_lat_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes internally but only export clean names
    m.add_class::<PyDivisibilityOrder>()?;
    m.add_class::<PyPrefixOrder>()?;
    m.add_class::<PyNaturalOrder>()?;
    m.add_class::<PyDiamondLattice>()?;
    m.add_class::<PyBooleanLattice>()?;
    m.add_class::<PyMeetLattice>()?;
    m.add_class::<PyJoinLattice>()?;
    m.add_class::<PyBasicLattice>()?;
    m.add_class::<PyLatticeGraphData>()?;
    
    // Export only clean names (without Py prefix)
    m.add("DivisibilityOrder", m.getattr("PyDivisibilityOrder")?)?;
    m.add("PrefixOrder", m.getattr("PyPrefixOrder")?)?;
    m.add("NaturalOrder", m.getattr("PyNaturalOrder")?)?;
    m.add("DiamondLattice", m.getattr("PyDiamondLattice")?)?;
    m.add("BooleanLattice", m.getattr("PyBooleanLattice")?)?;
    m.add("MeetLattice", m.getattr("PyMeetLattice")?)?;
    m.add("JoinLattice", m.getattr("PyJoinLattice")?)?;
    
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
    
    // Remove the Py* names from the module to avoid confusion
    let module_dict = m.dict();
    module_dict.del_item("PyDivisibilityOrder")?;
    module_dict.del_item("PyPrefixOrder")?;
    module_dict.del_item("PyNaturalOrder")?;
    module_dict.del_item("PyDiamondLattice")?;
    module_dict.del_item("PyBooleanLattice")?;
    module_dict.del_item("PyMeetLattice")?;
    module_dict.del_item("PyJoinLattice")?;
    module_dict.del_item("PyBasicLattice")?;
    module_dict.del_item("PyLatticeGraphData")?;
    
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
