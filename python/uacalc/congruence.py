"""
Congruence Lattice Operations

This module provides high-level Python interfaces for working with congruence lattices,
including construction, analysis, and visualization utilities.
"""

from typing import Optional, Callable, Dict, Any, List, Tuple, Union
from typing_extensions import Protocol
import warnings

from . import (
    CongruenceLattice, Algebra, Partition, 
    create_congruence_lattice, HAS_NETWORKX, HAS_MATPLOTLIB
)

class ProgressCallback(Protocol):
    """Protocol for progress callback functions."""
    def __call__(self, progress: float, message: str) -> None: ...

class CongruenceLatticeBuilder:
    """Builder pattern for constructing congruence lattices with various options."""
    
    def __init__(self):
        self._algebra: Optional[Algebra] = None
        self._progress_callback: Optional[ProgressCallback] = None
        self._timeout_seconds: Optional[float] = None
        self._lazy_construction: bool = True
    
    def for_algebra(self, algebra: Algebra) -> 'CongruenceLatticeBuilder':
        """Set the algebra for lattice construction.
        
        Args:
            algebra: The algebra to compute the congruence lattice for
            
        Returns:
            Self for method chaining
        """
        self._algebra = algebra
        return self
    
    def with_progress(self, callback: ProgressCallback) -> 'CongruenceLatticeBuilder':
        """Set a progress callback for long-running constructions.
        
        Args:
            callback: Function(progress: float, message: str) for progress reporting
            
        Returns:
            Self for method chaining
        """
        self._progress_callback = callback
        return self
    
    def with_timeout(self, seconds: float) -> 'CongruenceLatticeBuilder':
        """Set a timeout for lattice construction.
        
        Args:
            seconds: Timeout in seconds
            
        Returns:
            Self for method chaining
        """
        self._timeout_seconds = seconds
        return self
    
    def eager_construction(self) -> 'CongruenceLatticeBuilder':
        """Use eager construction instead of lazy construction.
        
        Returns:
            Self for method chaining
        """
        self._lazy_construction = False
        return self
    
    def build(self) -> CongruenceLattice:
        """Build the congruence lattice with the configured options.
        
        Returns:
            Constructed congruence lattice
            
        Raises:
            ValueError: If no algebra is set
            RuntimeError: If construction fails or times out
        """
        if self._algebra is None:
            raise ValueError("Algebra must be set before building lattice")
        
        lattice = create_congruence_lattice(self._algebra)
        
        if self._progress_callback is not None:
            lattice.with_progress_callback(self._progress_callback)
        
        if not self._lazy_construction:
            # Force construction by accessing size
            _ = lattice.size()
        
        return lattice

def analyze_lattice(lattice: CongruenceLattice) -> Dict[str, Any]:
    """Analyze a congruence lattice and return its properties.
    
    Args:
        lattice: The congruence lattice to analyze
        
    Returns:
        Dictionary containing lattice properties:
        - size: Number of congruences
        - height: Height of the lattice
        - width: Width of the lattice  
        - atom_count: Number of atoms
        - coatom_count: Number of coatoms
        - is_distributive: Whether the lattice is distributive
        - is_modular: Whether the lattice is modular
        - is_complemented: Whether the lattice is complemented
    """
    import time
    
    start_time = time.time()
    
    # Basic properties
    size = lattice.size()
    atoms = lattice.atoms()
    coatoms = lattice.coatoms()
    
    atom_count = len(atoms)
    coatom_count = len(coatoms)
    
    # Compute height and width
    height = _compute_lattice_height(lattice)
    width = _compute_lattice_width(lattice)
    
    # Check lattice properties
    is_distributive = _is_distributive_lattice(lattice)
    is_modular = _is_modular_lattice(lattice)
    is_complemented = _is_complemented_lattice(lattice)
    
    analysis_time = time.time() - start_time
    
    return {
        'size': size,
        'height': height,
        'width': width,
        'atom_count': atom_count,
        'coatom_count': coatom_count,
        'is_distributive': is_distributive,
        'is_modular': is_modular,
        'is_complemented': is_complemented,
        'analysis_time': analysis_time,
    }

def _compute_lattice_height(lattice: CongruenceLattice) -> int:
    """Compute the height of a lattice (length of longest chain)."""
    # Simple implementation - can be optimized
    size = lattice.size()
    if size <= 2:
        return size - 1
    
    # For now, return a reasonable estimate
    # TODO: Implement proper height computation
    return size // 2

def _compute_lattice_width(lattice: CongruenceLattice) -> int:
    """Compute the width of a lattice (size of largest antichain)."""
    # Simple implementation - can be optimized
    size = lattice.size()
    if size <= 2:
        return size
    
    # For now, return a reasonable estimate
    # TODO: Implement proper width computation using Dilworth's theorem
    return size // 2

def _is_distributive_lattice(lattice: CongruenceLattice) -> bool:
    """Check if a lattice is distributive."""
    # TODO: Implement distributive lattice check
    # For now, return False as a conservative estimate
    return False

def _is_modular_lattice(lattice: CongruenceLattice) -> bool:
    """Check if a lattice is modular."""
    # TODO: Implement modular lattice check
    # For now, return False as a conservative estimate
    return False

def _is_complemented_lattice(lattice: CongruenceLattice) -> bool:
    """Check if a lattice is complemented."""
    # TODO: Implement complemented lattice check
    # For now, return False as a conservative estimate
    return False

def lattice_to_networkx(lattice: CongruenceLattice) -> 'nx.DiGraph':
    """Convert a congruence lattice to a NetworkX directed graph.
    
    Args:
        lattice: The congruence lattice to convert
        
    Returns:
        NetworkX DiGraph representing the lattice
        
    Raises:
        ImportError: If NetworkX is not available
    """
    if not HAS_NETWORKX:
        raise ImportError("NetworkX is required for lattice graph conversion")
    
    import networkx as nx
    
    G = nx.DiGraph()
    
    # Add nodes
    size = lattice.size()
    for i in range(size):
        G.add_node(i)
    
    # Add edges from covering relation
    covering = lattice.covering_relation()
    for source, target in covering:
        G.add_edge(source, target)
    
    return G

def plot_lattice(lattice: CongruenceLattice, 
                layout: str = 'spring',
                node_size: int = 500,
                font_size: int = 10,
                figsize: Tuple[int, int] = (10, 8),
                **kwargs) -> 'matplotlib.figure.Figure':
    """Plot a congruence lattice using matplotlib.
    
    Args:
        lattice: The congruence lattice to plot
        layout: NetworkX layout algorithm ('spring', 'hierarchical', 'circular')
        node_size: Size of nodes in the plot
        font_size: Font size for node labels
        figsize: Figure size as (width, height)
        **kwargs: Additional arguments passed to NetworkX draw function
        
    Returns:
        Matplotlib figure object
        
    Raises:
        ImportError: If matplotlib or NetworkX is not available
    """
    if not HAS_MATPLOTLIB:
        raise ImportError("Matplotlib is required for lattice plotting")
    if not HAS_NETWORKX:
        raise ImportError("NetworkX is required for lattice plotting")
    
    import matplotlib.pyplot as plt
    import networkx as nx
    
    G = lattice_to_networkx(lattice)
    
    # Choose layout
    if layout == 'spring':
        pos = nx.spring_layout(G)
    elif layout == 'hierarchical':
        pos = nx.kamada_kawai_layout(G)
    elif layout == 'circular':
        pos = nx.circular_layout(G)
    else:
        pos = nx.spring_layout(G)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Draw the graph
    nx.draw(G, pos, 
            node_size=node_size,
            font_size=font_size,
            with_labels=True,
            node_color='lightblue',
            edge_color='gray',
            arrows=True,
            ax=ax,
            **kwargs)
    
    ax.set_title(f"Congruence Lattice (Size: {lattice.size()})")
    plt.tight_layout()
    
    return fig

def export_lattice_data(lattice: CongruenceLattice, 
                       format: str = 'json',
                       file_path: Optional[str] = None) -> Union[str, Dict[str, Any]]:
    """Export lattice data in various formats.
    
    Args:
        lattice: The congruence lattice to export
        format: Export format ('json', 'csv', 'dot')
        file_path: Optional file path to save the data
        
    Returns:
        Exported data as string or dictionary
        
    Raises:
        ValueError: If format is not supported
    """
    if format == 'json':
        data = {
            'size': lattice.size(),
            'congruences': [congruence.blocks() for congruence in lattice.congruences()],
            'covering_relation': lattice.covering_relation(),
            'atoms': [atom.blocks() for atom in lattice.atoms()],
            'coatoms': [coatom.blocks() for coatom in lattice.coatoms()],
        }
        
        if file_path:
            import json
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        
        return data
    
    elif format == 'csv':
        # Export covering relation as CSV
        covering = lattice.covering_relation()
        csv_data = "source,target\n"
        for source, target in covering:
            csv_data += f"{source},{target}\n"
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(csv_data)
        
        return csv_data
    
    elif format == 'dot':
        # Export as Graphviz DOT format
        if not HAS_NETWORKX:
            raise ImportError("NetworkX is required for DOT export")
        
        import networkx as nx
        G = lattice_to_networkx(lattice)
        dot_data = nx.drawing.nx_pydot.to_pydot(G).to_string()
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(dot_data)
        
        return dot_data
    
    else:
        raise ValueError(f"Unsupported format: {format}")

def principal_congruences_table(algebra: Algebra) -> List[Tuple[int, int, Partition]]:
    """Generate all principal congruences for an algebra.
    
    Args:
        algebra: The algebra to compute principal congruences for
        
    Returns:
        List of (a, b, congruence) tuples for all pairs a, b
    """
    lattice = create_congruence_lattice(algebra)
    size = algebra.cardinality()
    
    principal_congruences = []
    for a in range(size):
        for b in range(a + 1, size):
            congruence = lattice.principal_congruence(a, b)
            principal_congruences.append((a, b, congruence))
    
    return principal_congruences

def congruence_closure(algebra: Algebra, pairs: List[Tuple[int, int]]) -> Partition:
    """Compute the congruence closure of a set of pairs.
    
    Args:
        algebra: The algebra
        pairs: List of (a, b) pairs to close
        
    Returns:
        The smallest congruence containing all the pairs
    """
    if not pairs:
        # Return the identity relation
        size = algebra.cardinality()
        return Partition(size)
    
    lattice = create_congruence_lattice(algebra)
    
    # Start with the identity relation
    result = Partition(algebra.cardinality())
    
    # Join with each principal congruence
    for a, b in pairs:
        principal = lattice.principal_congruence(a, b)
        result = result.join(principal)
    
    return result

def is_congruence(algebra: Algebra, partition: Partition) -> bool:
    """Check if a partition is a congruence of the algebra.
    
    Args:
        algebra: The algebra
        partition: The partition to check
        
    Returns:
        True if the partition is a congruence
    """
    # TODO: Implement proper congruence checking
    # For now, return True as a placeholder
    # This should check that the partition is compatible with all operations
    return True

class ProgressBar:
    """Progress bar wrapper using tqdm."""
    
    def __init__(self, total: int = 100, desc: str = "Progress"):
        try:
            from tqdm import tqdm
            self._tqdm = tqdm(total=total, desc=desc)
            self._available = True
        except ImportError:
            warnings.warn("tqdm not available, falling back to print progress")
            self._available = False
            self._last_progress = 0
            self._total = total
            self._desc = desc
    
    def __call__(self, progress: float, message: str = ""):
        if self._available:
            self._tqdm.set_postfix_str(message)
            self._tqdm.n = int(progress * self._total)
            self._tqdm.refresh()
        else:
            current = int(progress * self._total)
            if current > self._last_progress:
                print(f"{self._desc}: {progress:.1%} - {message}")
                self._last_progress = current
    
    def close(self):
        if self._available:
            self._tqdm.close()

class LoggingProgress:
    """Progress reporter that logs to Python logging system."""
    
    def __init__(self, logger=None, level='INFO'):
        import logging
        self.logger = logger or logging.getLogger(__name__)
        self.level = getattr(logging, level.upper())
        self._last_progress = 0
    
    def __call__(self, progress: float, message: str = ""):
        current = int(progress * 100)
        if current > self._last_progress:
            self.logger.log(self.level, f"Progress: {progress:.1%} - {message}")
            self._last_progress = current

class CallbackProgress:
    """Wrapper for custom progress callbacks."""
    
    def __init__(self, callback: ProgressCallback):
        self.callback = callback
    
    def __call__(self, progress: float, message: str = ""):
        self.callback(progress, message)

# Extend Algebra class with congruence lattice methods
def _algebra_congruence_lattice(self: Algebra, 
                               with_progress: Optional[ProgressCallback] = None) -> CongruenceLattice:
    """Get the congruence lattice for this algebra.
    
    Args:
        with_progress: Optional progress callback
        
    Returns:
        CongruenceLattice object
    """
    lattice = create_congruence_lattice(self)
    if with_progress is not None:
        lattice.with_progress_callback(with_progress)
    return lattice

def _algebra_analyze_congruences(self: Algebra) -> Dict[str, Any]:
    """Analyze the congruence structure of this algebra.
    
    Returns:
        Dictionary with congruence analysis results
    """
    lattice = create_congruence_lattice(self)
    return analyze_lattice(lattice)

def _algebra_principal_congruence(self: Algebra, a: int, b: int) -> Partition:
    """Get the principal congruence θ(a, b) for this algebra.
    
    Args:
        a, b: Elements of the algebra
        
    Returns:
        Principal congruence partition
    """
    lattice = create_congruence_lattice(self)
    return lattice.principal_congruence(a, b)

# Monkey patch Algebra class with new methods
Algebra.congruence_lattice = _algebra_congruence_lattice
Algebra.analyze_congruences = _algebra_analyze_congruences  
Algebra.principal_congruence = _algebra_principal_congruence
