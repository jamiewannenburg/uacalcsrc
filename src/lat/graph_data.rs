/*! Graph data structures for lattice visualization
 *
 * This module provides data structures for converting lattices to graph
 * representations that can be used with NetworkX, DOT, Mermaid, etc.
 */

use std::collections::HashMap;
use std::fmt::{self, Display};

/// Graph data structure for lattice visualization.
///
/// This structure contains all the information needed to convert a lattice
/// to a graph representation for visualization tools like NetworkX, Graphviz, or Mermaid.
#[derive(Debug, Clone)]
pub struct LatticeGraphData {
    /// List of nodes in the graph
    pub nodes: Vec<GraphNode>,
    /// List of edges in the graph
    pub edges: Vec<GraphEdge>,
    /// Map from node ID to label string
    pub node_labels: HashMap<usize, String>,
    /// Optional map from (source, target) edge to label (for TCT labeling)
    pub edge_labels: Option<HashMap<(usize, usize), String>>,
}

/// A node in the lattice graph.
#[derive(Debug, Clone)]
pub struct GraphNode {
    /// Unique identifier for the node
    pub id: usize,
    /// Display label for the node
    pub label: String,
    /// String representation of the underlying element
    pub element: String,
}

/// An edge in the lattice graph.
#[derive(Debug, Clone)]
pub struct GraphEdge {
    /// Source node ID
    pub source: usize,
    /// Target node ID
    pub target: usize,
    /// Optional label for the edge (e.g., TCT type)
    pub label: Option<String>,
}

impl LatticeGraphData {
    /// Create a new empty graph data structure.
    pub fn new() -> Self {
        LatticeGraphData {
            nodes: Vec::new(),
            edges: Vec::new(),
            node_labels: HashMap::new(),
            edge_labels: None,
        }
    }

    /// Add a node to the graph.
    pub fn add_node(&mut self, id: usize, label: String, element: String) {
        self.nodes.push(GraphNode {
            id,
            label: label.clone(),
            element: element.clone(),
        });
        self.node_labels.insert(id, label);
    }

    /// Add an edge to the graph.
    pub fn add_edge(&mut self, source: usize, target: usize, label: Option<String>) {
        self.edges.push(GraphEdge {
            source,
            target,
            label: label.clone(),
        });

        if let Some(ref lbl) = label {
            if self.edge_labels.is_none() {
                self.edge_labels = Some(HashMap::new());
            }
            if let Some(ref mut edge_labels) = self.edge_labels {
                edge_labels.insert((source, target), lbl.clone());
            }
        }
    }

    /// Convert to DOT format (Graphviz).
    pub fn to_dot(&self) -> String {
        let mut dot = String::from("digraph Lattice {\n");
        dot.push_str("  rankdir=BT;\n");
        dot.push_str("  node [shape=circle];\n\n");

        // Add nodes
        for node in &self.nodes {
            let label = self
                .node_labels
                .get(&node.id)
                .unwrap_or(&node.label)
                .replace('"', "\\\"");
            dot.push_str(&format!("  {} [label=\"{}\"];\n", node.id, label));
        }

        dot.push_str("\n");

        // Add edges
        for edge in &self.edges {
            if let Some(ref label) = edge.label {
                let lbl = label.replace('"', "\\\"");
                dot.push_str(&format!(
                    "  {} -> {} [label=\"{}\"];\n",
                    edge.source, edge.target, lbl
                ));
            } else {
                dot.push_str(&format!("  {} -> {};\n", edge.source, edge.target));
            }
        }

        dot.push_str("}\n");
        dot
    }

    /// Convert to Mermaid format.
    pub fn to_mermaid(&self) -> String {
        let mut mermaid = String::from("graph TD\n");

        // Add nodes
        for node in &self.nodes {
            let label = self
                .node_labels
                .get(&node.id)
                .unwrap_or(&node.label)
                .replace('"', "'");
            mermaid.push_str(&format!("  {}[\"{}\"]\n", node.id, label));
        }

        mermaid.push_str("\n");

        // Add edges
        for edge in &self.edges {
            if let Some(ref label) = edge.label {
                let lbl = label.replace('"', "'");
                mermaid.push_str(&format!(
                    "  {} -->|{}\"| {}\n",
                    edge.source, lbl, edge.target
                ));
            } else {
                mermaid.push_str(&format!("  {} --> {}\n", edge.source, edge.target));
            }
        }

        mermaid
    }
}

impl Default for LatticeGraphData {
    fn default() -> Self {
        Self::new()
    }
}

impl Display for LatticeGraphData {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "LatticeGraphData(nodes: {}, edges: {})",
            self.nodes.len(),
            self.edges.len()
        )
    }
}

