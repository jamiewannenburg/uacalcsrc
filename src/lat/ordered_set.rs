/*! OrderedSet and POElem implementation
 *
 * This module provides an implementation of ordered sets (posets) to replace
 * the external latdraw dependency. It provides the core functionality needed
 * for BasicLattice visualization.
 */

use std::collections::{HashMap, HashSet};
use std::fmt::{self, Display, Debug};
use std::hash::{Hash, Hasher};
use std::sync::Arc;
use crate::lat::graph_data::LatticeGraphData;

/// A partially ordered set (poset) structure.
///
/// This replaces the latdraw OrderedSet dependency and provides the core
/// functionality for representing and querying partial orders.
pub struct OrderedSet<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    name: Option<String>,
    universe: Vec<Arc<POElem<T>>>,
    upper_covers: HashMap<Arc<POElem<T>>, Vec<Arc<POElem<T>>>>,
    elem_order: HashMap<Arc<POElem<T>>, usize>,
}

/// A partially ordered element (POElem) in an OrderedSet.
///
/// Each element wraps an underlying object and maintains its position
/// in the poset structure.
#[derive(Clone)]
pub struct POElem<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    underlying_object: T,
    index: usize,
}

impl<T> POElem<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    /// Create a new POElem.
    pub fn new(underlying_object: T, index: usize) -> Self {
        POElem {
            underlying_object,
            index,
        }
    }

    /// Get the underlying object.
    pub fn get_underlying_object(&self) -> &T {
        &self.underlying_object
    }

    /// Get the index of this element.
    pub fn index(&self) -> usize {
        self.index
    }

    /// Get upper covers (elements that directly cover this element).
    /// Note: This requires the poset to be passed in, as POElem doesn't store a reference.
    pub fn upper_covers(&self, poset: &OrderedSet<T>) -> Vec<Arc<POElem<T>>> {
        let self_arc = Arc::new(self.clone());
        poset.upper_covers.get(&self_arc).cloned().unwrap_or_default()
    }

    /// Get lower covers (elements directly covered by this element).
    /// Note: This requires the poset to be passed in.
    pub fn lower_covers(&self, poset: &OrderedSet<T>) -> Vec<Arc<POElem<T>>> {
        let mut lower = Vec::new();
        for (elem, uppers) in &poset.upper_covers {
            if uppers.iter().any(|u| *u.get_underlying_object() == self.underlying_object) {
                lower.push(elem.clone());
            }
        }
        lower
    }

    /// Get the ideal (all elements ≤ this element).
    /// Note: This requires the poset to be passed in.
    pub fn ideal(&self, poset: &OrderedSet<T>) -> Vec<Arc<POElem<T>>> {
        let self_arc = Arc::new(self.clone());
        let mut ideal = Vec::new();
        for elem in &poset.universe {
            if poset.leq(elem, &self_arc) {
                ideal.push(elem.clone());
            }
        }
        ideal
    }

    /// Get the filter (all elements ≥ this element).
    /// Note: This requires the poset to be passed in.
    pub fn filter(&self, poset: &OrderedSet<T>) -> Vec<Arc<POElem<T>>> {
        let self_arc = Arc::new(self.clone());
        let mut filter = Vec::new();
        for elem in &poset.universe {
            if poset.leq(&self_arc, elem) {
                filter.push(elem.clone());
            }
        }
        filter
    }

    /// Check if this element is join irreducible.
    /// Note: This requires the poset to be passed in.
    pub fn is_join_irreducible(&self, poset: &OrderedSet<T>) -> bool {
        let uppers = self.upper_covers(poset);
        if uppers.is_empty() {
            return false; // Top element is not join irreducible
        }
        if uppers.len() == 1 {
            return true;
        }
        // An element is join irreducible if it has exactly one upper cover
        // or if it cannot be expressed as the join of two strictly smaller elements
        // For now, use the simple check: has exactly one upper cover
        uppers.len() == 1
    }

    /// Check if this element is meet irreducible.
    /// Note: This requires the poset to be passed in.
    pub fn is_meet_irreducible(&self, poset: &OrderedSet<T>) -> bool {
        let lowers = self.lower_covers(poset);
        if lowers.is_empty() {
            return false; // Bottom element is not meet irreducible
        }
        if lowers.len() == 1 {
            return true;
        }
        // An element is meet irreducible if it has exactly one lower cover
        lowers.len() == 1
    }
}

impl<T> PartialEq for POElem<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn eq(&self, other: &Self) -> bool {
        self.underlying_object == other.underlying_object && self.index == other.index
    }
}

impl<T> Eq for POElem<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
}

impl<T> Hash for POElem<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.underlying_object.hash(state);
        self.index.hash(state);
    }
}

impl<T> Debug for POElem<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("POElem")
            .field("underlying_object", &self.underlying_object)
            .field("index", &self.index)
            .finish()
    }
}

impl<T> Display for POElem<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.underlying_object)
    }
}

/// An edge in the poset (for TCT labeling).
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Edge {
    pub source: String,
    pub target: String,
}

impl Edge {
    pub fn new(source: String, target: String) -> Self {
        Edge { source, target }
    }
}

impl Display for Edge {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({}, {})", self.source, self.target)
    }
}

impl<T> OrderedSet<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    /// Create a new OrderedSet from a universe and upper covers.
    ///
    /// # Arguments
    /// * `name` - Optional name for the poset
    /// * `universe` - List of underlying objects
    /// * `upper_covers_list` - List of upper covers for each element (by index)
    ///
    /// # Returns
    /// * `Ok(OrderedSet)` - Successfully created poset
    /// * `Err(String)` - If the poset structure is invalid
    pub fn new(
        name: Option<String>,
        universe: Vec<T>,
        upper_covers_list: Vec<Vec<T>>,
    ) -> Result<Self, String> {
        if universe.len() != upper_covers_list.len() {
            return Err(format!(
                "Universe size {} does not match upper covers size {}",
                universe.len(),
                upper_covers_list.len()
            ));
        }

        // Create POElems for each element
        let mut po_elems: Vec<Arc<POElem<T>>> = Vec::new();
        let mut elem_order: HashMap<Arc<POElem<T>>, usize> = HashMap::new();

        for (index, obj) in universe.iter().enumerate() {
            let po_elem = Arc::new(POElem::new(obj.clone(), index));
            elem_order.insert(po_elem.clone(), index);
            po_elems.push(po_elem);
        }

        // Build upper covers map
        let mut upper_covers: HashMap<Arc<POElem<T>>, Vec<Arc<POElem<T>>>> = HashMap::new();

        for (index, covers) in upper_covers_list.iter().enumerate() {
            let elem = &po_elems[index];
            let mut cover_elems = Vec::new();

            for cover_obj in covers {
                // Find the POElem for this cover object
                if let Some(cover_elem) = po_elems.iter().find(|e| e.get_underlying_object() == cover_obj) {
                    cover_elems.push(cover_elem.clone());
                } else {
                    return Err(format!(
                        "Upper cover object {:?} not found in universe",
                        cover_obj
                    ));
                }
            }

            upper_covers.insert(elem.clone(), cover_elems);
        }

        // Create the OrderedSet
        let poset = OrderedSet {
            name,
            universe: po_elems.clone(),
            upper_covers,
            elem_order,
        };

        Ok(poset)
    }

    /// Create an OrderedSet from filters (like latdraw's orderedSetFromFilters).
    ///
    /// A filter for an element x is the set of all elements y such that x ≤ y.
    ///
    /// # Arguments
    /// * `name` - Optional name for the poset
    /// * `universe` - List of underlying objects
    /// * `filters` - List of filters for each element (by index)
    ///
    /// # Returns
    /// * `Ok(OrderedSet)` - Successfully created poset
    /// * `Err(String)` - If the poset structure is invalid
    pub fn ordered_set_from_filters(
        name: Option<String>,
        universe: Vec<T>,
        filters: Vec<Vec<T>>,
    ) -> Result<Self, String> {
        if universe.len() != filters.len() {
            return Err(format!(
                "Universe size {} does not match filters size {}",
                universe.len(),
                filters.len()
            ));
        }

        // Convert filters to upper covers
        // For each element, its upper covers are the minimal elements in its filter
        let mut upper_covers_list: Vec<Vec<T>> = Vec::new();

        for (index, filter) in filters.iter().enumerate() {
            let elem = &universe[index];
            let mut covers = Vec::new();

            // Find minimal elements in the filter (elements that are not greater than any other in the filter)
            for candidate in filter {
                if candidate == elem {
                    continue; // Skip the element itself
                }

                let mut is_minimal = true;
                for other in filter {
                    if other != candidate && other != elem {
                        // Check if other < candidate (i.e., candidate is in other's filter but other is not in candidate's filter)
                        let other_idx = universe.iter().position(|x| x == other);
                        let candidate_idx = universe.iter().position(|x| x == candidate);

                        if let (Some(oi), Some(ci)) = (other_idx, candidate_idx) {
                            // If candidate is in other's filter but other is not in candidate's filter, then other < candidate
                            let other_filter = &filters[oi];
                            let candidate_filter = &filters[ci];

                            if other_filter.contains(candidate) && !candidate_filter.contains(other) {
                                is_minimal = false;
                                break;
                            }
                        }
                    }
                }

                if is_minimal {
                    covers.push(candidate.clone());
                }
            }

            upper_covers_list.push(covers);
        }

        Self::new(name, universe, upper_covers_list)
    }

    /// Get the universe of this poset.
    pub fn univ(&self) -> Vec<Arc<POElem<T>>> {
        self.universe.clone()
    }

    /// Check if a ≤ b in this poset.
    pub fn leq(&self, a: &Arc<POElem<T>>, b: &Arc<POElem<T>>) -> bool {
        if a == b {
            return true; // Reflexivity
        }

        // Use transitive closure via DFS
        let mut visited = HashSet::new();
        self.leq_dfs(a, b, &mut visited)
    }

    fn leq_dfs(
        &self,
        a: &Arc<POElem<T>>,
        b: &Arc<POElem<T>>,
        visited: &mut HashSet<Arc<POElem<T>>>,
    ) -> bool {
        if a == b {
            return true;
        }

        if visited.contains(a) {
            return false;
        }
        visited.insert(a.clone());

        if let Some(covers) = self.upper_covers.get(a) {
            for cover in covers {
                if cover == b {
                    return true;
                }
                if self.leq_dfs(cover, b, visited) {
                    return true;
                }
            }
        }

        false
    }

    /// Get the order index of an element.
    pub fn elem_order(&self, elem: &Arc<POElem<T>>) -> Option<usize> {
        self.elem_order.get(elem).copied()
    }

    /// Get an element by its underlying object.
    pub fn get_element(&self, obj: &T) -> Option<Arc<POElem<T>>> {
        self.universe
            .iter()
            .find(|e| e.get_underlying_object() == obj)
            .cloned()
    }

    /// Get an element by index.
    pub fn get_element_by_index(&self, index: usize) -> Option<Arc<POElem<T>>> {
        self.universe.get(index).cloned()
    }

    /// Get the name of this poset.
    pub fn name(&self) -> Option<&str> {
        self.name.as_deref()
    }

    /// Get upper covers for an element (convenience method).
    pub fn get_upper_covers(&self, elem: &Arc<POElem<T>>) -> Vec<Arc<POElem<T>>> {
        self.upper_covers.get(elem).cloned().unwrap_or_default()
    }

    /// Get lower covers for an element (convenience method).
    pub fn get_lower_covers(&self, elem: &Arc<POElem<T>>) -> Vec<Arc<POElem<T>>> {
        let mut lower = Vec::new();
        for (other_elem, uppers) in &self.upper_covers {
            if uppers.iter().any(|u| u.get_underlying_object() == elem.get_underlying_object()) {
                lower.push(other_elem.clone());
            }
        }
        lower
    }

    /// Convert to graph data for visualization.
    ///
    /// # Arguments
    /// * `edge_labels` - Optional map from edges to labels (e.g., for TCT type labeling)
    ///
    /// # Returns
    /// A `LatticeGraphData` structure containing nodes and edges for visualization
    pub fn to_graph_data(&self, edge_labels: Option<&HashMap<Edge, String>>) -> LatticeGraphData {
        let mut graph = LatticeGraphData::new();
        
        // Add nodes
        for (idx, elem) in self.universe.iter().enumerate() {
            let label = elem.to_string();
            graph.add_node(idx, label.clone(), label);
        }
        
        // Add edges (from upper covers)
        for (idx, elem) in self.universe.iter().enumerate() {
            for upper_cover in self.get_upper_covers(elem) {
                if let Some(cover_idx) = self.elem_order(&upper_cover) {
                    // Check for edge label
                    let edge_label = if let Some(labels) = edge_labels {
                        let edge = Edge::new(elem.to_string(), upper_cover.to_string());
                        labels.get(&edge).cloned()
                    } else {
                        None
                    };
                    graph.add_edge(idx, cover_idx, edge_label);
                }
            }
        }
        
        graph
    }
}

impl<T> Debug for OrderedSet<T>
where
    T: Clone + PartialEq + Eq + Hash + Debug + Display + Send + Sync + 'static,
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("OrderedSet")
            .field("name", &self.name)
            .field("universe_size", &self.universe.len())
            .finish()
    }
}

