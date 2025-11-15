"""
Type stubs for uacalc_lib module.
This file provides type information for Python IDEs and type checkers.
"""

from typing import Any, List, Dict, Optional, Union, Tuple
from typing_extensions import Protocol

# Type aliases for common UACalc types
Element = Union[int, str, Tuple[Any, ...]]

# ============================================================================
# PROTOCOL DEFINITIONS
# ============================================================================

class Operation(Protocol):
    """Protocol for operation types in universal algebra.
    
    This protocol defines the interface that all operations must implement.
    Operations are maps from the direct product of some number (arity) of a set
    to the set itself.
    """
    def arity(self) -> int: ...
    """Returns the arity (number of arguments) of this operation."""
    
    def get_set_size(self) -> int: ...
    """Returns the size of the set upon which the operation is defined."""
    
    def symbol(self) -> "alg.OperationSymbol": ...
    """Returns the operation symbol for this operation."""
    
    def int_value_at(self, args: List[int]) -> int: ...
    """Evaluates the operation at the given integer arguments.
    
    Args:
        args: List of integer arguments
        
    Returns:
        The result of the operation as an integer
    """
    
    def get_table(self) -> Optional[List[int]]: ...
    """Returns the operation table if available, None otherwise.
    
    Returns:
        The operation table as a list of integers, or None if not available
    """

class Algebra(Protocol):
    """Protocol for algebra types in universal algebra.
    
    An algebra consists of a universe (set) and a collection of operations
    defined on that set. This protocol defines the interface that all algebras
    must implement.
    """
    def cardinality(self) -> int: ...
    """Returns the cardinality of the algebra.
    
    For finite algebras, returns the actual size. For infinite or unknown
    cardinalities, returns a negative constant.
    
    Returns:
        Positive integer for finite algebras, negative constant otherwise
    """
    
    def input_size(self) -> int: ...
    """Returns the input size of the algebra.
    
    This is the sum of the cardinality raised to the power of each
    operation's arity. Returns -1 if the size exceeds maximum integer value.
    
    Returns:
        The input size or -1 if it exceeds maximum integer value
    """
    
    def is_unary(self) -> bool: ...
    """Checks if this algebra is unary (has only unary operations).
    
    Returns:
        True if all operations have arity 1, False otherwise
    """
    
    def name(self) -> str: ...
    """Returns the name of this algebra."""
    
    def operations(self) -> List[Operation]: ...
    """Returns a list of all operations in this algebra.
    
    Returns:
        List of Operation instances
    """

class Lattice(Protocol):
    """Protocol for lattice types.
    
    A lattice is a partially ordered set with join and meet operations.
    This protocol extends Algebra and defines the fundamental operations
    of lattice theory.
    """
    def join_irreducibles(self) -> Optional[List[Any]]: ...
    """Returns the list of join irreducible elements, if available.
    
    A join irreducible element is one that cannot be expressed as the join
    of two strictly smaller elements.
    
    Returns:
        List of join irreducible elements, or None if not available
    """
    
    def meet_irreducibles(self) -> Optional[List[Any]]: ...
    """Returns the list of meet irreducible elements, if available.
    
    A meet irreducible element is one that cannot be expressed as the meet
    of two strictly larger elements.
    
    Returns:
        List of meet irreducible elements, or None if not available
    """
    
    def atoms(self) -> Optional[List[Any]]: ...
    """Returns the list of atoms (minimal non-zero elements), if available.
    
    An atom is an element that covers only the bottom element (if it exists).
    
    Returns:
        List of atoms, or None if not available
    """
    
    def coatoms(self) -> Optional[List[Any]]: ...
    """Returns the list of coatoms (maximal non-one elements), if available.
    
    A coatom is an element that is covered only by the top element (if it exists).
    
    Returns:
        List of coatoms, or None if not available
    """
    
    def join(self, a: Any, b: Any) -> Any: ...
    """Returns the join (least upper bound) of two elements.
    
    The join operation finds the smallest element that is greater than
    or equal to both a and b.
    
    Args:
        a: First element
        b: Second element
        
    Returns:
        The join of a and b
    """
    
    def meet(self, a: Any, b: Any) -> Any: ...
    """Returns the meet (greatest lower bound) of two elements.
    
    The meet operation finds the largest element that is less than
    or equal to both a and b.
    
    Args:
        a: First element
        b: Second element
        
    Returns:
        The meet of a and b
    """

# Module-level exports
__version__: str
__author__: str
__license__: str

# ============================================================================
# ELEMENT MODULE
# ============================================================================

class element:
    """Element module - currently empty, trait-based implementations."""
    pass

# ============================================================================
# TYPES MODULE
# ============================================================================

class types:
    """Types module - currently empty."""
    pass

# ============================================================================
# EXAMPLE MODULE
# ============================================================================

class example:
    """Example module - currently empty."""
    pass

# ============================================================================
# TERMS MODULE
# ============================================================================

class terms:
    """Terms module for term structures and operations."""
    
    class VariableImp:
        """Python wrapper for VariableImp."""
        def __init__(self, name: str) -> None: ...
        @staticmethod
        def x() -> "terms.VariableImp": ...
        @staticmethod
        def y() -> "terms.VariableImp": ...
        @staticmethod
        def z() -> "terms.VariableImp": ...
        def get_name(self) -> str: ...
        def isa_variable(self) -> bool: ...
        def depth(self) -> int: ...
        def length(self) -> int: ...
        def get_variable_list(self) -> List[str]: ...
        def eval(self, algebra: "alg.BasicAlgebra", var_map: Dict[str, int]) -> int: ...
        def int_eval(self, algebra: "alg.BasicAlgebra", var_map: Dict[str, int]) -> int: ...
        def interpretation(
            self,
            algebra: "alg.BasicAlgebra",
            varlist: List[str],
            use_all: bool,
        ) -> "alg.IntOperation": ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...
    
    class NonVariableTerm:
        """Python wrapper for NonVariableTerm."""
        def __init__(
            self,
            op_sym: "alg.OperationSymbol",
            children: List[Union["terms.VariableImp", "terms.NonVariableTerm"]],
        ) -> None: ...
        @staticmethod
        def make_constant_term(sym: "alg.OperationSymbol") -> "terms.NonVariableTerm": ...
        def isa_variable(self) -> bool: ...
        def depth(self) -> int: ...
        def length(self) -> int: ...
        def get_variable_list(self) -> List[str]: ...
        def eval(self, algebra: "alg.BasicAlgebra", var_map: Dict[str, int]) -> int: ...
        def int_eval(self, algebra: "alg.BasicAlgebra", var_map: Dict[str, int]) -> int: ...
        def interpretation(
            self,
            algebra: "alg.BasicAlgebra",
            varlist: List[str],
            use_all: bool,
        ) -> "alg.IntOperation": ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class Taylor:
        """Python wrapper for Taylor term analyzer."""
        def __init__(
            self,
            op_sym: "alg.OperationSymbol",
            inteqs: List[List["util.IntArray"]],
        ) -> None: ...
        @staticmethod
        def new_with_arity(
            arity: int,
            inteqs: List[List["util.IntArray"]],
        ) -> "terms.Taylor": ...
        @staticmethod
        def markovic_mckenzie_term() -> "terms.Taylor": ...
        @staticmethod
        def siggers_term() -> "terms.Taylor": ...
        def canonical_form(self, term: Union["terms.VariableImp", "terms.NonVariableTerm"]) -> Union["terms.VariableImp", "terms.NonVariableTerm"]: ...
        def term_from_array(self, arr: List[int]) -> Union["terms.VariableImp", "terms.NonVariableTerm"]: ...
        @staticmethod
        def lexicographically_compare_int_arrays(
            a: "util.IntArray",
            b: "util.IntArray",
        ) -> int: ...
        @staticmethod
        def lexicographically_compare_arrays(a: List[int], b: List[int]) -> int: ...
        def arity(self) -> int: ...
        def inteqs(self) -> List[List["util.IntArray"]]: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class TermOperationImp:
        """Python wrapper for TermOperationImp."""
        def __init__(
            self,
            term: Union["terms.VariableImp", "terms.NonVariableTerm"],
            variables: List[Union["terms.VariableImp", str]],
            algebra: "alg.BasicAlgebra",
            name: Optional[str] = None,
        ) -> None: ...
        def get_term(self) -> str: ...
        def get_ordered_variables(self) -> List[str]: ...
        def arity(self) -> int: ...
        def get_set_size(self) -> int: ...
        def int_value_at(self, args: List[int]) -> int: ...
        def get_table(self) -> Optional[List[int]]: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    @staticmethod
    def string_to_term(s: str) -> Union["terms.VariableImp", "terms.NonVariableTerm"]: ...
    @staticmethod
    def is_valid_var_string(s: str) -> bool: ...
    @staticmethod
    def is_valid_op_name_string(s: str) -> bool: ...
    @staticmethod
    def flatten(term: Union["terms.VariableImp", "terms.NonVariableTerm"]) -> Union["terms.VariableImp", "terms.NonVariableTerm"]: ...

# ============================================================================
# LATTICE MODULE
# ============================================================================

class lat:
    """Lattice module for lattice structures and operations."""
    
    class DivisibilityOrder:
        """Divisibility order for integers."""
        def __init__(self) -> None: ...
        def leq(self, a: int, b: int) -> bool: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class PrefixOrder:
        """Prefix order for strings."""
        def __init__(self) -> None: ...
        def leq(self, a: str, b: str) -> bool: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class NaturalOrder:
        """Natural order for various types."""
        def __init__(self) -> None: ...
        def leq_i32(self, a: int, b: int) -> bool: ...
        def leq_u32(self, a: int, b: int) -> bool: ...
        def leq_string(self, a: str, b: str) -> bool: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class DiamondLattice:
        """Diamond lattice implementation."""
        def __init__(self) -> None: ...
        def get_element(self, index: int) -> Optional[int]: ...
        def size(self) -> int: ...
        def universe(self) -> List[int]: ...
        def cardinality(self) -> int: ...
        def leq(self, a: int, b: int) -> bool: ...
        def join_irreducibles(self) -> Optional[List[int]]: ...
        def meet_irreducibles(self) -> Optional[List[int]]: ...
        def atoms(self) -> Optional[List[int]]: ...
        def coatoms(self) -> Optional[List[int]]: ...
        def join(self, a: int, b: int) -> int: ...
        def join_list(self, args: List[int]) -> int: ...
        def meet(self, a: int, b: int) -> int: ...
        def meet_list(self, args: List[int]) -> int: ...
        def upper_covers_indices(self, index: int) -> List[int]: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class BooleanLattice:
        """Boolean lattice implementation."""
        def __init__(self) -> None: ...
        def get_element(self, index: int) -> Optional[int]: ...
        def size(self) -> int: ...
        def universe(self) -> List[int]: ...
        def cardinality(self) -> int: ...
        def leq(self, a: int, b: int) -> bool: ...
        def join_irreducibles(self) -> Optional[List[int]]: ...
        def meet_irreducibles(self) -> Optional[List[int]]: ...
        def atoms(self) -> Optional[List[int]]: ...
        def coatoms(self) -> Optional[List[int]]: ...
        def join(self, a: int, b: int) -> int: ...
        def join_list(self, args: List[int]) -> int: ...
        def meet(self, a: int, b: int) -> int: ...
        def meet_list(self, args: List[int]) -> int: ...
        def upper_covers_indices(self, index: int) -> List[int]: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class MeetLattice:
        """Meet lattice implementation."""
        def name(self) -> str: ...
        def universe(self) -> List[int]: ...
        def join_irreducibles(self) -> List[int]: ...
        def meet_irreducibles(self) -> List[int]: ...
        def atoms(self) -> List[int]: ...
        def coatoms(self) -> List[int]: ...
        def join(self, a: int, b: int) -> int: ...
        def join_list(self, args: List[int]) -> int: ...
        def meet(self, a: int, b: int) -> int: ...
        def meet_list(self, args: List[int]) -> int: ...
        def leq(self, a: int, b: int) -> bool: ...
        def join_irreducibles_po(self) -> "lat.OrderedSet": ...
        """Get join irreducibles as an OrderedSet.
        
        Returns:
            OrderedSet: An OrderedSet containing the join irreducible elements
                       with their order relations
        """
        def meet_irreducibles_po(self) -> "lat.OrderedSet": ...
        """Get meet irreducibles as an OrderedSet.
        
        Returns:
            OrderedSet: An OrderedSet containing the meet irreducible elements
                       with their order relations
        """
        def to_ordered_set(self, name: Optional[str] = None) -> "lat.OrderedSet": ...
        """Convert this MeetLattice to an OrderedSet.
        
        This method computes the upper covers for each element using join irreducibles
        and creates an OrderedSet representing the full lattice structure.
        
        Args:
            name: Optional name for the resulting OrderedSet
            
        Returns:
            OrderedSet: An OrderedSet representing the lattice structure
        """
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class JoinLattice:
        """Join lattice implementation."""
        def name(self) -> str: ...
        def universe(self) -> List[int]: ...
        def join_irreducibles(self) -> List[int]: ...
        def meet_irreducibles(self) -> List[int]: ...
        def atoms(self) -> List[int]: ...
        def coatoms(self) -> List[int]: ...
        def join(self, a: int, b: int) -> int: ...
        def join_list(self, args: List[int]) -> int: ...
        def meet(self, a: int, b: int) -> int: ...
        def meet_list(self, args: List[int]) -> int: ...
        def leq(self, a: int, b: int) -> bool: ...
        def join_irreducibles_po(self) -> "lat.OrderedSet": ...
        """Get join irreducibles as an OrderedSet.
        
        Returns:
            OrderedSet: An OrderedSet containing the join irreducible elements
                       with their order relations
        """
        def meet_irreducibles_po(self) -> "lat.OrderedSet": ...
        """Get meet irreducibles as an OrderedSet.
        
        Returns:
            OrderedSet: An OrderedSet containing the meet irreducible elements
                       with their order relations
        """
        def to_ordered_set(self, name: Optional[str] = None) -> "lat.OrderedSet": ...
        """Convert this JoinLattice to an OrderedSet.
        
        This method computes the upper covers for each element using join irreducibles
        and creates an OrderedSet representing the full lattice structure.
        
        Args:
            name: Optional name for the resulting OrderedSet
            
        Returns:
            OrderedSet: An OrderedSet representing the lattice structure
        """
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class BasicLattice:
        """Basic lattice implementation for visualization and computation.
        
        A BasicLattice wraps a poset (OrderedSet) and provides lattice operations
        (join, meet) along with methods for visualization via graph data structures.
        Primarily used for drawing and visualization of lattices.
        """
        def __init__(
            self,
            name: str,
            con_lat: "alg.CongruenceLattice",
            label: bool = True,
        ) -> None: ...
        """Create a BasicLattice from a CongruenceLattice.
        
        Args:
            name: Name for the lattice
            con_lat: The congruence lattice to convert
            label: Whether to include TCT (Type Classification Theory) labeling
        """
        def cardinality(self) -> int: ...
        """Get the cardinality of this lattice.
        
        Returns:
            The number of elements in the lattice
        """
        def name(self) -> str: ...
        """Get the name of this lattice.
        
        Returns:
            The name of the lattice
        """
        def universe(self) -> List[int]: ...
        """Get the universe as a list of integers (for BasicLattice<i32> only).
        
        Returns:
            List of integers representing the universe elements
            
        Raises:
            ValueError: If this is not a BasicLattice<i32> created from operations
        """
        def leq(self, a: int, b: int) -> bool: ...
        """Check if a ≤ b in the lattice order (for BasicLattice<i32> only).
        
        Args:
            a: First element
            b: Second element
            
        Returns:
            True if a ≤ b, False otherwise
            
        Raises:
            ValueError: If this is not a BasicLattice<i32> or elements not found
        """
        def join(self, a: int, b: int) -> int: ...
        """Compute the join (least upper bound) of two elements (for BasicLattice<i32> only).
        
        Args:
            a: First element
            b: Second element
            
        Returns:
            The join of a and b
            
        Raises:
            ValueError: If this is not a BasicLattice<i32> or elements not found
        """
        def meet(self, a: int, b: int) -> int: ...
        """Compute the meet (greatest lower bound) of two elements (for BasicLattice<i32> only).
        
        Args:
            a: First element
            b: Second element
            
        Returns:
            The meet of a and b
            
        Raises:
            ValueError: If this is not a BasicLattice<i32> or elements not found
        """
        def to_graph_data(self) -> "lat.LatticeGraphData": ...
        """Convert this lattice to graph data for visualization.
        
        Returns:
            LatticeGraphData containing nodes and edges for the lattice diagram
        """
        def to_networkx(self) -> Any: ...
        """Convert this lattice to a NetworkX DiGraph (requires networkx).
        
        Returns:
            A NetworkX DiGraph representing the lattice structure
            
        Raises:
            ImportError: If networkx is not installed
        """
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class LatticeGraphData:
        """Graph data structure for lattice visualization.
        
        This class represents a lattice as a graph with nodes and edges,
        suitable for conversion to various visualization formats (DOT, Mermaid, NetworkX).
        """
        def to_dot(self) -> str: ...
        """Convert to Graphviz DOT format.
        
        Returns:
            A string in DOT format representing the lattice graph
        """
        def to_mermaid(self) -> str: ...
        """Convert to Mermaid diagram format.
        
        Returns:
            A string in Mermaid format representing the lattice graph
        """
        def to_networkx(self) -> Any: ...
        """Convert to NetworkX DiGraph (requires networkx).
        
        Returns:
            A NetworkX DiGraph representing the lattice structure
            
        Raises:
            ImportError: If networkx is not installed
        """
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class OrderedSet:
        """Partially ordered set (poset) structure.
        
        This class provides Python bindings for creating and manipulating
        partially ordered sets with integer elements.
        """
        def __init__(
            self,
            universe: List[int],
            upper_covers: List[List[int]],
            *,
            name: Optional[str] = None,
        ) -> None: ...
        """Create a new OrderedSet from a universe and upper covers.
        
        Args:
            universe: List of integers representing the universe
            upper_covers: List of lists, where upper_covers[i] contains elements
                         that directly cover universe[i]
            name: Optional name for the poset
            
        Raises:
            ValueError: If the poset structure is invalid
        """
        def name(self) -> Optional[str]: ...
        """Get the name of this poset.
        
        Returns:
            The name of the poset, or None if not set
        """
        def cardinality(self) -> int: ...
        """Get the cardinality (number of elements) of this poset.
        
        Returns:
            The number of elements in the poset
        """
        def universe(self) -> List[int]: ...
        """Get the universe as a list of integers.
        
        Returns:
            List of integers representing the universe
        """
        def leq(self, a: int, b: int) -> bool: ...
        """Check if a ≤ b in this poset.
        
        Args:
            a: First element (integer)
            b: Second element (integer)
            
        Returns:
            True if a ≤ b, False otherwise
            
        Raises:
            ValueError: If elements are not found in universe
        """
        def get_upper_covers(self, element: int) -> List[int]: ...
        """Get upper covers (elements that directly cover the given element).
        
        Args:
            element: The element to get upper covers for
            
        Returns:
            List of elements that directly cover the given element
            
        Raises:
            ValueError: If element is not found in universe
        """
        def get_lower_covers(self, element: int) -> List[int]: ...
        """Get lower covers (elements directly covered by the given element).
        
        Args:
            element: The element to get lower covers for
            
        Returns:
            List of elements directly covered by the given element
            
        Raises:
            ValueError: If element is not found in universe
        """
        def to_graph_data(self, edge_labels: Optional[Dict[Tuple[str, str], str]] = None) -> "lat.LatticeGraphData": ...
        """Convert to graph data for visualization.
        
        Args:
            edge_labels: Optional dictionary mapping (source, target) tuples to edge labels
            
        Returns:
            LatticeGraphData: Graph data structure for visualization
        """
        def to_networkx(self, edge_labels: Optional[Dict[Tuple[str, str], str]] = None) -> Any: ...
        """Convert to NetworkX DiGraph if networkx is available.
        
        Args:
            edge_labels: Optional dictionary mapping (source, target) tuples to edge labels
            
        Returns:
            A NetworkX DiGraph representing the poset structure
            
        Raises:
            ImportError: If networkx is not installed
        """
        @staticmethod
        def from_lattice(lattice: Any, name: Optional[str] = None) -> "lat.OrderedSet": ...
        """Create an OrderedSet from a JoinLattice or MeetLattice.
        
        This static method converts a lattice to an OrderedSet by computing
        upper covers using join irreducibles.
        
        Args:
            lattice: The JoinLattice or MeetLattice to convert
            name: Optional name for the resulting OrderedSet
            
        Returns:
            OrderedSet: An OrderedSet representing the lattice structure
        """
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class OrderedSetPartition:
        """Partially ordered set (poset) structure for Partition elements.
        
        This class provides Python bindings for creating and manipulating
        partially ordered sets where elements are Partition objects.
        """
        def name(self) -> Optional[str]: ...
        """Get the name of this poset.
        
        Returns:
            The name of the poset, or None if not set
        """
        def cardinality(self) -> int: ...
        """Get the cardinality (number of elements) of this poset.
        
        Returns:
            The number of elements in the poset
        """
        def universe(self) -> List["alg.Partition"]: ...
        """Get the universe as a list of Partitions.
        
        Returns:
            List of Partition objects representing the universe
        """
        def leq(self, a: "alg.Partition", b: "alg.Partition") -> bool: ...
        """Check if a ≤ b in this poset.
        
        Args:
            a: First element (Partition)
            b: Second element (Partition)
            
        Returns:
            True if a ≤ b, False otherwise
            
        Raises:
            ValueError: If elements are not found in universe
        """
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class OrderedSetBasicSet:
        """Partially ordered set (poset) structure for BasicSet elements.
        
        This class provides Python bindings for creating and manipulating
        partially ordered sets where elements are BasicSet objects.
        """
        def name(self) -> Optional[str]: ...
        """Get the name of this poset.
        
        Returns:
            The name of the poset, or None if not set
        """
        def cardinality(self) -> int: ...
        """Get the cardinality (number of elements) of this poset.
        
        Returns:
            The number of elements in the poset
        """
        def universe(self) -> List["alg.BasicSet"]: ...
        """Get the universe as a list of BasicSets.
        
        Returns:
            List of BasicSet objects representing the universe
        """
        def leq(self, a: "alg.BasicSet", b: "alg.BasicSet") -> bool: ...
        """Check if a ≤ b in this poset.
        
        Args:
            a: First element (BasicSet)
            b: Second element (BasicSet)
            
        Returns:
            True if a ≤ b, False otherwise
            
        Raises:
            ValueError: If elements are not found in universe
        """
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    # Module-level functions
    @staticmethod
    def maximals_divisibility(elems: List[int]) -> List[int]: ...
    @staticmethod
    def maximals_prefix(elems: List[str]) -> List[str]: ...
    @staticmethod
    def maximals_natural_i32(elems: List[int]) -> List[int]: ...
    @staticmethod
    def maximals_natural_string(elems: List[str]) -> List[str]: ...
    @staticmethod
    def ordered_sets_main() -> str: ...
    @staticmethod
    def lattice_from_meet(name: str, meet: Any) -> "lat.BasicLattice": ...
    @staticmethod
    def lattice_from_join(name: str, join: Any) -> "lat.BasicLattice": ...
    @staticmethod
    def lattice_from_meet_with_universe(name: str, univ: List[int], meet: Any) -> "lat.BasicLattice": ...
    @staticmethod
    def lattice_from_join_with_universe(name: str, univ: List[int], join: Any) -> "lat.BasicLattice": ...
    @staticmethod
    def con_to_small_lattice(con: Any) -> Any: ...
    @staticmethod
    def dual(lat: Any) -> Any: ...
    # Internal function names (also exported for compatibility)
    @staticmethod
    def py_lattice_from_meet(name: str, meet: Any) -> "lat.BasicLattice": ...
    @staticmethod
    def py_lattice_from_join(name: str, join: Any) -> "lat.BasicLattice": ...
    @staticmethod
    def py_lattice_from_meet_with_universe(name: str, univ: List[int], meet: Any) -> "lat.BasicLattice": ...
    @staticmethod
    def py_lattice_from_join_with_universe(name: str, univ: List[int], join: Any) -> "lat.BasicLattice": ...
    @staticmethod
    def py_con_to_small_lattice(con: Any) -> Any: ...
    @staticmethod
    def py_dual(lat: Any) -> Any: ...

# ============================================================================
# IO MODULE
# ============================================================================

class io:
    """IO module for algebra file I/O operations."""
    
    class Mace4Reader:
        """Reader for Mace4 format algebra files."""
        @staticmethod
        def new_from_file(file_path: str) -> "io.Mace4Reader": ...
        @staticmethod
        def new_from_stream(data: List[int]) -> "io.Mace4Reader": ...
        @staticmethod
        def parse_algebra_from_file(file_path: str) -> Optional["alg.BasicAlgebra"]: ...
        def parse_algebra_from_stream(self, data: List[int]) -> Optional["alg.BasicAlgebra"]: ...
        @staticmethod
        def parse_algebra_list_from_file(file_path: str) -> Any: ...  # Returns iterator
        def parse_algebra_list_from_stream(self, data: List[int]) -> List["alg.BasicAlgebra"]: ...
        @staticmethod
        def is_ordinary_character(c: str) -> bool: ...
        @staticmethod
        def is_special_character(c: str) -> bool: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class AlgebraReader:
        """Reader for algebra files."""
        @staticmethod
        def new_from_file(file_path: str) -> "io.AlgebraReader": ...
        @staticmethod
        def new_from_stream(data: List[int]) -> "io.AlgebraReader": ...
        def read_algebra_file(self) -> Optional["alg.BasicAlgebra"]: ...
        @staticmethod
        def read_algebra_from_file(file_path: str) -> Optional["alg.BasicAlgebra"]: ...
        def read_algebra_from_stream(self, data: List[int]) -> Optional["alg.BasicAlgebra"]: ...
        def read_algebra_list_from_file(self, file_path: str) -> List["alg.BasicAlgebra"]: ...
        def read_algebra_list_from_stream(self, data: List[int]) -> List["alg.BasicAlgebra"]: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class AlgebraWriter:
        """Writer for algebra files."""
        @staticmethod
        def new_with_file(algebra: "alg.BasicAlgebra", file_path: str) -> "io.AlgebraWriter": ...
        @staticmethod
        def new_with_writer(algebra: "alg.BasicAlgebra") -> "io.AlgebraWriter": ...
        @staticmethod
        def write_algebra_xml_to_file(algebra: "alg.BasicAlgebra", file_path: str) -> None: ...
        @staticmethod
        def write_algebra_to_file(algebra: "alg.BasicAlgebra", file_path: str) -> None: ...
        @staticmethod
        def write_basic_algebra_to_file(algebra: "alg.BasicAlgebra", file_path: str) -> None: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class BadAlgebraFileException:
        """Exception for bad algebra file format."""
        def __init__(self, message: str) -> None: ...
        @staticmethod
        def new_safe(message: str) -> "io.BadAlgebraFileException": ...
        def message(self) -> str: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...
    
    class ExtFileFilter:
        """File filter based on extensions."""
        def __init__(self, description: str, exts: List[str]) -> None: ...
        @staticmethod
        def new_single(description: str, ext: str) -> "io.ExtFileFilter": ...
        @staticmethod
        def new_safe(description: str, exts: List[str]) -> "io.ExtFileFilter": ...
        @staticmethod
        def new_single_safe(description: str, ext: str) -> "io.ExtFileFilter": ...
        def accept(self, path: str) -> bool: ...
        def get_description(self) -> str: ...
        def get_extensions(self) -> List[str]: ...
        @staticmethod
        def split_off_extension(path: str) -> Tuple[Optional[str], Optional[str]]: ...
        @staticmethod
        def get_extension(path: str) -> Optional[str]: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...
    
    @staticmethod
    def parse_line(line: str) -> int: ...
    @staticmethod
    def read_algebra_file(path: str) -> "alg.BasicAlgebra": ...
    @staticmethod
    def read_algebra_from_stream(data: List[int]) -> "alg.BasicAlgebra": ...
    @staticmethod
    def read_algebra_list_file(path: str) -> List["alg.BasicAlgebra"]: ...
    @staticmethod
    def read_algebra_list_from_stream(data: List[int]) -> "alg.BasicAlgebra": ...
    @staticmethod
    def convert_to_xml(path: str) -> None: ...
    @staticmethod
    def write_algebra_file(algebra: "alg.BasicAlgebra", path: str) -> None: ...
    @staticmethod
    def write_algebra_file_with_style(algebra: "alg.BasicAlgebra", path: str, old_style: bool) -> None: ...
    @staticmethod
    def read_projective_plane(path: str) -> "alg.BasicAlgebra": ...
    @staticmethod
    def read_projective_plane_from_stream(data: List[int]) -> "alg.BasicAlgebra": ...

# ============================================================================
# EQUATION MODULE
# ============================================================================

class eq:
    """Equation module for equation handling."""
    
    class Equation:
        """Python wrapper for Equation."""
        def __init__(
            self,
            left: Union["terms.VariableImp", "terms.NonVariableTerm"],
            right: Union["terms.VariableImp", "terms.NonVariableTerm"],
            vars: Optional[List[str]] = None,
        ) -> None: ...
        def left_side(self) -> str: ...
        def right_side(self) -> str: ...
        def get_variable_list(self) -> List[str]: ...
        def get_operation_symbols(self) -> List[str]: ...
        def find_failure(self, algebra: "alg.BasicAlgebra") -> Optional[List[int]]: ...
        def find_failure_map(self, algebra: "alg.BasicAlgebra") -> Optional[Dict[str, int]]: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class Presentation:
        """Python wrapper for Presentation."""
        def __init__(self, variables: List[str], relations: List["eq.Equation"]) -> None: ...
        def get_variables(self) -> List[str]: ...
        def get_relations(self) -> List[str]: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    @staticmethod
    def associative_law(op_symbol: "alg.OperationSymbol") -> "eq.Equation": ...
    @staticmethod
    def cyclic_law(op_symbol: "alg.OperationSymbol") -> "eq.Equation": ...
    @staticmethod
    def first_second_symmetric_law(op_symbol: "alg.OperationSymbol") -> "eq.Equation": ...

# ============================================================================
# GROUP MODULE
# ============================================================================

class group:
    """Group module for group theory operations."""
    pass

# ============================================================================
# PARALLEL MODULE
# ============================================================================

class parallel:
    """Parallel module for parallel processing utilities."""
    
    class Pool:
        """Python wrapper for Pool."""
        @staticmethod
        def fj_pool() -> str: ...
        @staticmethod
        def is_initialized() -> bool: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...

# ============================================================================
# FPLAT MODULE
# ============================================================================

class fplat:
    """Fplat module for partially defined lattices."""
    
    class PartiallyDefinedLattice:
        """Python wrapper for PartiallyDefinedLattice."""
        def __init__(
            self,
            name: str,
            joins: List[List["terms.VariableImp"]],
            meets: List[List["terms.VariableImp"]],
        ) -> None: ...
        def name(self) -> str: ...
        def get_defined_joins(self) -> List[List["terms.VariableImp"]]: ...
        def get_defined_meets(self) -> List[List["terms.VariableImp"]]: ...
        def leq(self, a: "terms.VariableImp", b: "terms.VariableImp") -> bool: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...

# ============================================================================
# GENERAL_ALGEBRA MODULE
# ============================================================================

class general_algebra:
    """General algebra module for algebras with arbitrary universe elements."""
    
    class GeneralAlgebra:
        """Python wrapper for GeneralAlgebra."""
        def __init__(
            self,
            name: str,
            universe: List[Any],
            operations: Optional[List[Any]] = None,
        ) -> None: ...
        @staticmethod
        def with_name(name: str) -> "general_algebra.GeneralAlgebra": ...
        def name(self) -> str: ...
        def set_name(self, name: str) -> None: ...
        def description(self) -> Optional[str]: ...
        def set_description(self, desc: Optional[str]) -> None: ...
        def cardinality(self) -> int: ...
        def input_size(self) -> int: ...
        def is_unary(self) -> bool: ...
        def is_idempotent(self) -> bool: ...
        def is_total(self) -> bool: ...
        def monitoring(self) -> bool: ...
        def get_universe(self) -> List[Any]: ...
        def get_operations(self) -> List[Any]: ...
        def add_operation(self, operation: Any) -> None: ...
        def get_operation(self, index: int) -> Any: ...
        def operations_count(self) -> int: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...

# ============================================================================
# ALG MODULE
# ============================================================================

class alg:
    """Algebra module - main algebra structures and operations."""
    
    class BasicAlgebra:
        """Python wrapper for BasicAlgebra."""
        def __init__(
            self,
            name: str,
            universe: List[int],
            operations: Optional[List[Any]] = None,
        ) -> None: ...
        @staticmethod
        def new_with_constant_op(name: str, universe: List[int]) -> "alg.BasicAlgebra": ...
        @staticmethod
        def from_general_algebra(general_algebra: "alg.GeneralAlgebra") -> "alg.BasicAlgebra": ...
        def name(self) -> str: ...
        def set_name(self, name: str) -> None: ...
        def description(self) -> Optional[str]: ...
        def set_description(self, desc: Optional[str]) -> None: ...
        def cardinality(self) -> int: ...
        def input_size(self) -> int: ...
        def is_unary(self) -> bool: ...
        def is_idempotent(self) -> bool: ...
        def is_total(self) -> bool: ...
        def monitoring(self) -> bool: ...
        def get_universe(self) -> List[int]: ...
        def algebra_type(self) -> str: ...
        def get_element(self, k: int) -> int: ...
        def element_index(self, elem: int) -> int: ...
        def get_universe_list(self) -> Optional[List[int]]: ...
        def get_universe_order(self) -> Optional[Dict[int, int]]: ...
        def int_universe(self) -> bool: ...
        def reset_con_and_sub(self) -> None: ...
        def convert_to_default_value_ops(self) -> None: ...
        def operations(self) -> List[Any]: ...
        def operations_count(self) -> int: ...
        def con(self) -> "alg.CongruenceLattice": ...
        def sub(self) -> "alg.SubalgebraLattice": ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
    
    class BasicOperation:
        """Python wrapper for BasicOperation."""
        def __init__(
            self,
            symbol: "alg.OperationSymbol",
            set_size: int,
            table: Optional[List[int]] = None,
        ) -> None: ...
        @staticmethod
        def simple_binary_op(name: str, set_size: int) -> "alg.BasicOperation": ...
        @staticmethod
        def simple_unary_op(name: str, set_size: int) -> "alg.BasicOperation": ...
        @staticmethod
        def simple_nullary_op(name: str, set_size: int) -> "alg.BasicOperation": ...
        def arity(self) -> int: ...
        def get_set_size(self) -> int: ...
        def symbol(self) -> "alg.OperationSymbol": ...
        def value_at(self, args: List[int]) -> int: ...
        def get_table(self) -> Optional[List[int]]: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class OperationSymbol:
        """Python wrapper for OperationSymbol."""
        def __init__(self, name: str, arity: int, associative: bool = False) -> None: ...
        def arity(self) -> int: ...
        def name(self) -> str: ...
        def is_associative(self) -> bool: ...
        def set_associative(self, assoc: bool) -> None: ...
        def to_string_with_arity(self, show_arity: Optional[bool] = None) -> str: ...
        @staticmethod
        def get_operation_symbol(arity: int) -> "alg.OperationSymbol": ...
        @staticmethod
        def join() -> "alg.OperationSymbol": ...
        @staticmethod
        def meet() -> "alg.OperationSymbol": ...
        @staticmethod
        def product() -> "alg.OperationSymbol": ...
        @staticmethod
        def inverse() -> "alg.OperationSymbol": ...
        @staticmethod
        def identity() -> "alg.OperationSymbol": ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...
    
    class IntOperation:
        """Python wrapper for IntOperation."""
        def __init__(
            self,
            symbol: "alg.OperationSymbol",
            set_size: int,
            table: List[int],
        ) -> None: ...
        def arity(self) -> int: ...
        def get_set_size(self) -> int: ...
        def symbol(self) -> "alg.OperationSymbol": ...
        def int_value_at(self, args: List[int]) -> int: ...
        def get_table(self) -> Optional[List[int]]: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class AbstractIntOperation:
        """Python wrapper for AbstractIntOperation."""
        def __init__(self, name: str, arity: int, alg_size: int) -> None: ...
        @staticmethod
        def with_symbol(symbol: "alg.OperationSymbol", alg_size: int) -> "alg.AbstractIntOperation": ...
        def arity(self) -> int: ...
        def get_set_size(self) -> int: ...
        def symbol(self) -> "alg.OperationSymbol": ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class AbstractOperation: ...
    
    class Operations: ...
    
    class OperationWithDefaultValue: ...
    
    class SimilarityType:
        """Python wrapper for SimilarityType."""
        def __init__(
            self,
            operation_symbols: List["alg.OperationSymbol"],
            sort: bool = False,
        ) -> None: ...
        def get_operation_symbols(self) -> List["alg.OperationSymbol"]: ...
        def get_sorted_operation_symbols(self) -> List["alg.OperationSymbol"]: ...
        def input_size(self, alg_size: int) -> int: ...
        def get_arities_map(self) -> Dict[int, int]: ...
        def get_max_arity(self) -> int: ...
        @staticmethod
        def lattice_similarity_type() -> "alg.SimilarityType": ...
        @staticmethod
        def group_similarity_type() -> "alg.SimilarityType": ...
        def arities_string(self) -> str: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...
    
    class ParameterizedOperation: ...
    
    # Advanced algebra types
    class Homomorphism: ...
    class SubalgebraLattice:
        """Subalgebra lattice implementation."""
        def join_irreducibles_po(self) -> "lat.OrderedSetBasicSet": ...
        """Get the join irreducibles as an OrderedSet.
        
        Returns:
            OrderedSetBasicSet: An OrderedSet containing the join irreducible elements
                              with their order relations
        """
        def meet_irreducibles_po(self) -> "lat.OrderedSetBasicSet": ...
        """Get the meet irreducibles as an OrderedSet.
        
        Returns:
            OrderedSetBasicSet: An OrderedSet containing the meet irreducible elements
                              with their order relations
        """
    class BasicBinaryRelation: ...
    class CentralityData: ...
    class Partition: ...
    class PrintType: ...
    class CongruenceLattice:
        """Congruence lattice implementation."""
        def join_irreducibles_po(self) -> "lat.OrderedSetPartition": ...
        """Get the join irreducibles as an OrderedSet.
        
        Returns:
            OrderedSetPartition: An OrderedSet containing the join irreducible elements
                               with their order relations
        """
        def meet_irreducibles_po(self) -> "lat.OrderedSetPartition": ...
        """Get the meet irreducibles as an OrderedSet.
        
        Returns:
            OrderedSetPartition: An OrderedSet containing the meet irreducible elements
                               with their order relations
        """
    class BasicSet: ...
    class FreeAlgebra: ...
    class ProductAlgebra: ...
    class PowerAlgebra: ...
    class MatrixPowerAlgebra: ...
    
    class PolinLikeAlgebra:
        """Python wrapper for PolinLikeAlgebra.
        
        A Polin-like algebra constructed from a homomorphism between two algebras.
        The universe is the disjoint union of the bottom algebra and top algebra,
        with elements ordered as botAlg elements first, then topAlg elements.
        """
        def __init__(
            self,
            name: str,
            top_alg: "alg.BasicAlgebra",
            bot_alg: "alg.BasicAlgebra",
            map: Optional["alg.BasicOperation"] = None,
            top_const_index: int = 0,
            bot_const_index: int = 0,
        ) -> None: ...
        """Create a new PolinLikeAlgebra from two algebras and an optional homomorphism map.
        
        Args:
            name: Name of the algebra
            top_alg: The top algebra (A in f: A → B)
            bot_alg: The bottom algebra (B in f: A → B)
            map: Optional homomorphism map from topAlg to botAlg (None = identity)
            top_const_index: Index of the top constant
            bot_const_index: Index of the bottom constant
            
        Raises:
            ValueError: If construction fails
        """
        def cardinality(self) -> int: ...
        """Get the cardinality of this algebra.
        
        Returns:
            The cardinality (size of the universe)
        """
        def get_element(self, k: int) -> int: ...
        """Get the element at the given index.
        
        Args:
            k: Index of the element
            
        Returns:
            The element at index k, or -1 if out of bounds
        """
        def element_index(self, elem: int) -> int: ...
        """Get the index of an element in the universe.
        
        Args:
            elem: The element to find
            
        Returns:
            The index of the element, or -1 if not found
        """
        def algebra_type(self) -> str: ...
        """Get the algebra type.
        
        Returns:
            The algebra type ("PolinLike")
        """
        def name(self) -> str: ...
        """Get the name of this algebra.
        
        Returns:
            The name of the algebra
        """
        def set_name(self, name: str) -> None: ...
        """Set the name of this algebra.
        
        Args:
            name: The new name
        """
        def top_algebra_name(self) -> str: ...
        """Get the top algebra name.
        
        Returns:
            Name of the top algebra
        """
        def bottom_algebra_name(self) -> str: ...
        """Get the bottom algebra name.
        
        Returns:
            Name of the bottom algebra
        """
        def con(self) -> "alg.CongruenceLattice": ...
        """Get the congruence lattice (lazy initialization).
        
        Returns:
            The congruence lattice
        """
        def sub(self) -> "alg.SubalgebraLattice": ...
        """Get the subalgebra lattice (lazy initialization).
        
        Returns:
            The subalgebra lattice
        """
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class AlgebraFromMinimalSets:
        """Python wrapper for AlgebraFromMinimalSets.
        
        An algebra constructed from a minimal algebra (permutational algebra B).
        The algebra is built by extending the minimal algebra with additional
        elements and operations based on maps and connecting points.
        """
        def __init__(self, min_algebra: "alg.BasicAlgebra") -> None: ...
        """Create a new AlgebraFromMinimalSets with default size (3 * minAlgSize - 2).
        
        Args:
            min_algebra: The minimal algebra B
            
        Raises:
            ValueError: If there's an error creating the algebra
        """
        @staticmethod
        def new_with_size(
            min_algebra: "alg.BasicAlgebra",
            alg_size: int,
            maps: Optional[List[List[int]]] = None,
        ) -> "alg.AlgebraFromMinimalSets": ...
        """Create a new AlgebraFromMinimalSets with explicit size and maps.
        
        Args:
            min_algebra: The minimal algebra B
            alg_size: The size of the constructed algebra
            maps: Optional list of maps (if None, default maps are created)
            
        Returns:
            AlgebraFromMinimalSets: A new AlgebraFromMinimalSets instance
            
        Raises:
            ValueError: If there's an error creating the algebra
        """
        @staticmethod
        def new_with_name(
            min_algebra: "alg.BasicAlgebra",
            name: Optional[str] = None,
        ) -> "alg.AlgebraFromMinimalSets": ...
        """Create a new AlgebraFromMinimalSets with a name.
        
        Args:
            min_algebra: The minimal algebra B
            name: Optional name for the algebra
            
        Returns:
            AlgebraFromMinimalSets: A new AlgebraFromMinimalSets instance
            
        Raises:
            ValueError: If there's an error creating the algebra
        """
        @staticmethod
        def new_with_connecting_pts(
            min_algebra: "alg.BasicAlgebra",
            name: Optional[str] = None,
            connect_pts: Optional[List[int]] = None,
        ) -> "alg.AlgebraFromMinimalSets": ...
        """Create a new AlgebraFromMinimalSets with connecting points.
        
        Args:
            min_algebra: The minimal algebra B
            name: Optional name for the algebra
            connect_pts: Optional connecting points [a, b]
            
        Returns:
            AlgebraFromMinimalSets: A new AlgebraFromMinimalSets instance
            
        Raises:
            ValueError: If there's an error creating the algebra
        """
        @staticmethod
        def new_full(
            min_algebra: "alg.BasicAlgebra",
            alg_size: int,
            name: Optional[str] = None,
            maps: Optional[List[List[int]]] = None,
            connect_pts: Optional[List[int]] = None,
        ) -> "alg.AlgebraFromMinimalSets": ...
        """Create a new AlgebraFromMinimalSets with all parameters.
        
        Args:
            min_algebra: A permutational algebra (the minimal algebra B)
            alg_size: The size of the constructed algebra
            name: Optional name for the algebra
            maps: Optional list of maps (if None, default maps are created)
            connect_pts: Optional connecting points [a, b]
            
        Returns:
            AlgebraFromMinimalSets: A new AlgebraFromMinimalSets instance
            
        Raises:
            ValueError: If there's an error creating the algebra
        """
        def name(self) -> str: ...
        """Get the name of this algebra.
        
        Returns:
            The name of the algebra
        """
        def set_name(self, name: str) -> None: ...
        """Set the name of this algebra.
        
        Args:
            name: The new name for the algebra
        """
        def cardinality(self) -> int: ...
        """Get the cardinality of this algebra.
        
        Returns:
            The cardinality of the algebra
        """
        def get_element(self, k: int) -> int: ...
        """Get the k-th element of the universe.
        
        Args:
            k: The index of the element to retrieve
            
        Returns:
            The element at index k, or -1 if k is out of bounds
        """
        def element_index(self, elem: int) -> int: ...
        """Get the index of an element in the universe.
        
        Args:
            elem: The element to find the index for
            
        Returns:
            The index of the element, or -1 if not found
        """
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
    
    class Subalgebra:
        """Python wrapper for Subalgebra.
        
        A subalgebra of a SmallAlgebra with a restricted universe.
        This struct represents a subalgebra by maintaining a reference to the
        super algebra and a sorted array of universe indices that form the
        subuniverse. All operations are restricted to this subuniverse.
        """
        def __init__(
            self,
            name: str,
            super_algebra: "alg.BasicAlgebra",
            univ: List[int],
        ) -> None: ...
        """Create a new Subalgebra with the given super algebra and subuniverse.
        
        Args:
            name: Name of the subalgebra
            super_algebra: The super algebra
            univ: Array of indices in the super algebra forming the subuniverse
            
        Raises:
            ValueError: If the subuniverse is empty or contains invalid indices
        """
        def index(self, k: int) -> int: ...
        """Find the index in this subalgebra of the element with index k in the super algebra.
        
        Uses binary search since the universe array is sorted.
        
        Args:
            k: Index in the super algebra
            
        Returns:
            Index in the subalgebra, or -1 if not found
        """
        def restrict_partition(self, par: "alg.Partition") -> "alg.Partition": ...
        """Restrict a partition (or congruence) on the parent algebra to this subalgebra.
        
        Args:
            par: Partition on the super algebra
            
        Returns:
            Restricted partition on this subalgebra
            
        Raises:
            ValueError: If restriction fails
        """
        def super_algebra_name(self) -> str: ...
        """Get the super algebra name.
        
        Returns:
            Name of the super algebra
        """
        def get_subuniverse_array(self) -> List[int]: ...
        """Get the subuniverse array.
        
        Returns:
            Array of indices forming the subuniverse
        """
        def cardinality(self) -> int: ...
        """Get the cardinality of this subalgebra.
        
        Returns:
            The cardinality (size of the universe)
        """
        def get_element(self, k: int) -> int: ...
        """Get the element at the given index.
        
        Args:
            k: Index of the element
            
        Returns:
            The element at index k, or -1 if out of bounds
        """
        def element_index(self, elem: int) -> int: ...
        """Get the index of an element in the universe.
        
        Args:
            elem: The element to find
            
        Returns:
            The index of the element, or -1 if not found
        """
        def algebra_type(self) -> str: ...
        """Get the algebra type.
        
        Returns:
            The algebra type ("Subalgebra")
        """
        def name(self) -> str: ...
        """Get the name of this algebra.
        
        Returns:
            The name of the algebra
        """
        def set_name(self, name: str) -> None: ...
        """Set the name of this algebra.
        
        Args:
            name: The new name
        """
        def con(self) -> "alg.CongruenceLattice": ...
        """Get the congruence lattice (lazy initialization).
        
        Returns:
            The congruence lattice
        """
        def sub(self) -> "alg.SubalgebraLattice": ...
        """Get the subalgebra lattice (lazy initialization).
        
        Returns:
            The subalgebra lattice
        """
        @staticmethod
        def congruence_as_algebra(
            alg: "alg.BasicAlgebra",
            cong: "alg.Partition",
        ) -> "alg.Subalgebra": ...
        """Create a congruence as an algebra (static method).
        
        This gives the congruence as a subalgebra of A².
        
        Args:
            alg: The algebra
            cong: The congruence partition
            
        Returns:
            The congruence as an algebra
            
        Raises:
            ValueError: If creation fails
        """
        @staticmethod
        def congruence_as_algebra_with_name(
            name: str,
            alg: "alg.BasicAlgebra",
            cong: "alg.Partition",
        ) -> "alg.Subalgebra": ...
        """Create a congruence as an algebra with a name (static method).
        
        This gives the congruence as a subalgebra of A².
        
        Args:
            name: The name for the algebra
            alg: The algebra
            cong: The congruence partition
            
        Returns:
            The congruence as an algebra
            
        Raises:
            ValueError: If creation fails
        """
        def __str__(self) -> str: ...
        """Python string representation."""
        def __repr__(self) -> str: ...
        """Python repr representation."""
    
    class ReductAlgebra:
        """Python wrapper for ReductAlgebra.
        
        A reduct of a SmallAlgebra to a list of Terms. This creates a new algebra
        by interpreting terms from the super algebra, effectively restricting the
        operations to those defined by the terms.
        """
        def __init__(
            self,
            super_algebra: "alg.BasicAlgebra",
            term_list: List[Union[str, "terms.VariableImp", "terms.NonVariableTerm"]],
        ) -> None: ...
        """Create a new ReductAlgebra from a super algebra and list of terms.
        
        Args:
            super_algebra: The super algebra that this reduct is based on
            term_list: The list of terms that define the operations (can be strings for variables)
            
        Raises:
            ValueError: If the terms are invalid or algebra is incompatible
        """
        def name(self) -> str: ...
        """Get the name of this algebra.
        
        Returns:
            The name of the algebra
        """
        def set_name(self, name: str) -> None: ...
        """Set the name of this algebra.
        
        Args:
            name: The new name
        """
        def cardinality(self) -> int: ...
        """Get the cardinality of this algebra.
        
        Returns:
            The cardinality (same as super algebra)
        """
        def algebra_type(self) -> str: ...
        """Get the algebra type.
        
        Returns:
            The algebra type ("Reduct")
        """
        def get_universe_list(self) -> Optional[List[int]]: ...
        """Get the universe as a list.
        
        Returns:
            List of universe elements (same as super algebra)
        """
        def get_universe_order(self) -> Optional[Dict[int, int]]: ...
        """Get the universe order as a dictionary.
        
        Returns:
            Dictionary mapping elements to their indices
        """
        def get_element(self, index: int) -> Optional[int]: ...
        """Get an element by its index.
        
        Args:
            index: The index of the element
            
        Returns:
            The element at the given index, or None if out of bounds
        """
        def element_index(self, element: int) -> Optional[int]: ...
        """Get the index of an element.
        
        Args:
            element: The element to find the index for
            
        Returns:
            The index of the element, or None if not found
        """
        def is_unary(self) -> bool: ...
        """Check if this algebra is unary.
        
        Returns:
            True if all operations have arity 1, False otherwise
        """
        def is_idempotent(self) -> bool: ...
        """Check if this algebra is idempotent.
        
        Returns:
            True if all operations are idempotent, False otherwise
        """
        def is_total(self) -> bool: ...
        """Check if this algebra is total.
        
        Returns:
            True if all operations are total, False otherwise
        """
        def operations_count(self) -> int: ...
        """Get the number of operations in this algebra.
        
        Returns:
            The number of operations (non-variable terms)
        """
        def make_operation_tables(self) -> None: ...
        """Make operation tables from the terms.
        
        This method interprets each term in the super algebra to create
        operations for this reduct algebra.
        
        Raises:
            ValueError: If term interpretation fails
        """
        def con(self) -> "alg.CongruenceLattice": ...
        """Get the congruence lattice (lazy initialization).
        
        Returns:
            The congruence lattice of this reduct algebra
        """
        def sub(self) -> "alg.SubalgebraLattice": ...
        """Get the subalgebra lattice (lazy initialization).
        
        Returns:
            The subalgebra lattice of this reduct algebra
        """
        def super_algebra(self) -> "alg.BasicAlgebra": ...
        """Get the super algebra.
        
        Note: Currently returns an error as this requires storing the original
        algebra reference. This is a limitation that may be addressed in the future.
        
        Returns:
            The super algebra
            
        Raises:
            ValueError: Currently always raises (not yet fully implemented)
        """
        @staticmethod
        def congruence_as_algebra(
            alg: "alg.BasicAlgebra",
            cong: "alg.Partition",
        ) -> "alg.BasicAlgebra": ...
        """Create a congruence as an algebra (static method).
        
        This gives the congruence as a subalgebra of A^2.
        
        Args:
            alg: The algebra
            cong: The congruence partition
            
        Returns:
            The congruence as an algebra
            
        Raises:
            ValueError: Currently always raises (not yet implemented in Rust)
        """
        @staticmethod
        def congruence_as_algebra_with_name(
            name: str,
            alg: "alg.BasicAlgebra",
            cong: "alg.Partition",
        ) -> "alg.BasicAlgebra": ...
        """Create a congruence as an algebra with a name (static method).
        
        This gives the congruence as a subalgebra of A^2.
        
        Args:
            name: The name for the algebra
            alg: The algebra
            cong: The congruence partition
            
        Returns:
            The congruence as an algebra
            
        Raises:
            ValueError: Currently always raises (not yet implemented in Rust)
        """
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...
    
    class UnaryTermsMonoid:
        """Python wrapper for UnaryTermsMonoid.
        
        The monoid or semigroup of unary terms constructed from a generating algebra.
        This creates a monoid where the elements are unary terms and the operation
        is composition of term operations.
        """
        def __init__(self, algebra: "alg.BasicAlgebra") -> None: ...
        """Create a new UnaryTermsMonoid from a generating algebra.
        
        Args:
            algebra: The generating algebra
            
        Raises:
            ValueError: If construction fails
        """
        @staticmethod
        def new_with_id(algebra: "alg.BasicAlgebra", include_id: bool) -> "alg.UnaryTermsMonoid": ...
        """Create a new UnaryTermsMonoid with optional identity inclusion.
        
        Args:
            algebra: The generating algebra
            include_id: Whether to include the identity term
            
        Returns:
            UnaryTermsMonoid: A new UnaryTermsMonoid instance
            
        Raises:
            ValueError: If construction fails
        """
        def algebra_type(self) -> str: ...
        """Get the algebra type.
        
        Returns:
            The algebra type ("UNARY_TERMS_MONOID")
        """
        def cardinality(self) -> int: ...
        """Get the cardinality of this monoid.
        
        Returns:
            The cardinality (number of unary terms)
        """
        def name(self) -> str: ...
        """Get the name of this monoid.
        
        Returns:
            The name of the monoid
        """
        def set_name(self, name: str) -> None: ...
        """Set the name of this monoid.
        
        Args:
            name: The new name
        """
        def is_unary(self) -> bool: ...
        """Check if this algebra is unary.
        
        Returns:
            True if the algebra is unary, False otherwise
        """
        def is_idempotent(self) -> bool: ...
        """Check if this algebra is idempotent.
        
        Returns:
            True if the algebra is idempotent, False otherwise
        """
        def is_total(self) -> bool: ...
        """Check if this algebra is total.
        
        Returns:
            True if the algebra is total, False otherwise
        """
        def operations_count(self) -> int: ...
        """Get the number of operations.
        
        Returns:
            The number of operations (1 for the product operation)
        """
        def get_universe_list(self) -> List["util.IntArray"]: ...
        """Get the universe as a list of elements.
        
        Returns:
            List of IntArray elements representing the unary terms
        """
        def get_element(self, index: int) -> Optional["util.IntArray"]: ...
        """Get an element by its index.
        
        Args:
            index: The index of the element
            
        Returns:
            The element at the given index, or None if out of bounds
        """
        def element_index(self, element: "util.IntArray") -> Optional[int]: ...
        """Get the index of an element in the universe.
        
        Args:
            element: The element to find the index for
            
        Returns:
            The index of the element, or None if not found
        """
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __len__(self) -> int: ...
        """Get the cardinality of the monoid (for use with len()).
        
        Returns:
            The cardinality of the monoid
        """
    
    class ParameterizedAlgebra: ...
    class MaltsevProductDecomposition: ...
    
    class MaltsevDecompositionIterator:
        """Python wrapper for MaltsevDecompositionIterator.
        
        An iterator over sections (quotients of subalgebras) of an idempotent algebra.
        This iterator is used in variety analysis to decompose algebras into their
        Maltsev decomposition components.
        """
        def __init__(self, algebra: "alg.BasicAlgebra") -> None: ...
        """Create a new MaltsevDecompositionIterator for an idempotent algebra.
        
        Args:
            algebra: An idempotent algebra to decompose
            
        Raises:
            ValueError: If the algebra is not idempotent
        """
        def has_next(self) -> bool: ...
        """Check if there are more elements in the iterator.
        
        Returns:
            True if there are more elements, False otherwise
        """
        def __iter__(self) -> "alg.MaltsevDecompositionIterator": ...
        """Python iterator protocol - returns self."""
        def __next__(self) -> Optional[Dict[str, int]]: ...
        """Python iterator protocol - get next element.
        
        Returns a dictionary with the algebra's cardinality (matching Java behavior).
        The dictionary has the form: {"cardinality": <int>}
        
        Returns:
            A dictionary with "cardinality" key containing the algebra's cardinality,
            or None if the iterator is exhausted
        """
        def remove(self) -> None: ...
        """Remove the last element (not supported).
        
        Raises:
            ValueError: Always raises this exception (UnsupportedOperationException)
        """
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class GeneralAlgebra: ...
    class Polymorphisms: ...
    class Subtrace: ...
    class TypeFinder: ...
    
    class Pool:
        """Python wrapper for Pool."""
        @staticmethod
        def fj_pool() -> str: ...
        @staticmethod
        def is_initialized() -> bool: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    
    class Closer: ...
    class CloserTiming: ...
    
    # Module-level functions for algebra operations
    @staticmethod
    def is_endomorphism(endo: "alg.IntOperation", alg: "alg.BasicAlgebra") -> bool: ...
    """Test if an operation is an endomorphism of an algebra.
    
    An endomorphism is a unary operation that commutes with all operations
    of the algebra. This means that for any operation f and endomorphism e,
    we have: e(f(x1, x2, ..., xn)) = f(e(x1), e(x2), ..., e(xn))
    
    Args:
        endo: The operation to test (must be unary, IntOperation)
        alg: The algebra to test against (BasicAlgebra)
        
    Returns:
        True if the operation is an endomorphism, False otherwise
        
    Raises:
        ValueError: If the operation is not unary or there's an error
    """
    
    @staticmethod
    def is_homomorphism(map: List[int], alg0: "alg.BasicAlgebra", alg1: "alg.BasicAlgebra") -> bool: ...
    """Test if a map is a homomorphism from one algebra to another.
    
    A homomorphism is a map h: A -> B such that for any operation f in alg0
    and corresponding operation g in alg1 (with the same symbol), we have:
    h(f(x1, x2, ..., xn)) = g(h(x1), h(x2), ..., h(xn))
    
    Args:
        map: A list of integers defining the map from elements of alg0 to elements of alg1
        alg0: The source algebra (BasicAlgebra)
        alg1: The target algebra (BasicAlgebra)
        
    Returns:
        True if the map is a homomorphism, False otherwise
        
    Raises:
        ValueError: If there's an error (e.g., map size mismatch, missing operation)
    """
    
    @staticmethod
    def jonsson_terms(algebra: "alg.BasicAlgebra") -> Optional[List[str]]: ...
    """Find Jonsson terms for the algebra.
    
    This returns a list of Jonsson terms witnessing congruence distributivity,
    or None if the algebra does not generate a congruence distributive variety.
    The returned terms are guaranteed to be the least number of terms possible.
    
    Args:
        algebra: The algebra to check (BasicAlgebra)
        
    Returns:
        List of Jonsson terms as strings if they exist, None otherwise
    """
    
    @staticmethod
    def jonsson_level(algebra: "alg.BasicAlgebra") -> int: ...
    """Get the Jonsson level for the algebra.
    
    If the algebra generates a distributive variety, this returns the minimal
    number of Jonsson terms minus 1; otherwise it returns -1.
    For congruence distributivity testing, it's probably better to use
    jonsson_terms to get the actual terms.
    
    If the algebra has only one element, it returns 1.
    For a lattice it returns 2.
    
    Args:
        algebra: The algebra to check (BasicAlgebra)
        
    Returns:
        The Jonsson level (minimal number of Jonsson terms minus 1), or -1 if not distributive
    """
    
    @staticmethod
    def find_nuf(algebra: "alg.BasicAlgebra", arity: int) -> Optional[str]: ...
    """Find a near unanimity term (NUF) of the given arity.
    
    This will find a near unanimity term of the given arity if one exists;
    otherwise it returns None.
    
    A near unanimity term of arity n is a term t(x₀, x₁, ..., xₙ₋₁) such that:
    - t(y,x,x,...,x) = x
    - t(x,y,x,...,x) = x
    - ...
    - t(x,x,x,...,y) = x
    
    Args:
        algebra: The algebra to check (BasicAlgebra)
        arity: The arity of the NU term (must be at least 3)
        
    Returns:
        The NU term as a string if one exists, None otherwise
        
    Raises:
        ValueError: If arity is less than 3 or there's an error during computation
    """
    
    @staticmethod
    def matrix_power(alg: "alg.BasicAlgebra", k: int) -> "alg.BasicAlgebra": ...
    """The matrix power algebra as defined in Hobby-McKenzie.
    
    Creates a matrix power algebra A^[k] from a given algebra A and power k.
    This is a BasicAlgebra that contains:
    - All operations from the power algebra A^k
    - A binary left shift operation
    
    Args:
        alg: The root algebra to raise to a power (BasicAlgebra)
        k: The power/exponent (number of copies)
        
    Returns:
        A BasicAlgebra representing the matrix power algebra
        
    Raises:
        ValueError: If k is not positive or there's an error during creation
    """
    
    @staticmethod
    def make_random_algebra(n: int, sim_type: "alg.SimilarityType") -> "alg.BasicAlgebra": ...
    """Make a random algebra of a given similarity type.
    
    Creates a random algebra with the specified size and similarity type.
    The operations are generated randomly.
    
    Args:
        n: The size of the algebra (cardinality of the universe)
        sim_type: The similarity type (defines the operations)
        
    Returns:
        BasicAlgebra: A new random algebra
        
    Raises:
        ValueError: If there's an error during creation
    """
    
    @staticmethod
    def make_random_algebra_with_seed(n: int, sim_type: "alg.SimilarityType", seed: Optional[int] = None) -> "alg.BasicAlgebra": ...
    """Make a random algebra of a given similarity type with a seed.
    
    Creates a random algebra with the specified size and similarity type.
    The operations are generated randomly using the provided seed for reproducibility.
    
    Args:
        n: The size of the algebra (cardinality of the universe)
        sim_type: The similarity type (defines the operations)
        seed: Optional seed for the random number generator (None means use random seed)
        
    Returns:
        BasicAlgebra: A new random algebra
        
    Raises:
        ValueError: If there's an error during creation
    """
    
    @staticmethod
    def make_random_algebra_with_arities(n: int, arities: List[int]) -> "alg.BasicAlgebra": ...
    """Make a random algebra with given arities of the operations.
    
    Creates a random algebra with the specified size and operation arities.
    Operation symbols are automatically created as "r0", "r1", etc.
    
    Args:
        n: The size of the algebra (cardinality of the universe)
        arities: List of arities for the operations
        
    Returns:
        BasicAlgebra: A new random algebra
        
    Raises:
        ValueError: If there's an error during creation
    """
    
    @staticmethod
    def make_random_algebra_with_arities_and_seed(n: int, arities: List[int], seed: Optional[int] = None) -> "alg.BasicAlgebra": ...
    """Make a random algebra with given arities of the operations and a seed.
    
    Creates a random algebra with the specified size and operation arities.
    Operation symbols are automatically created as "r0", "r1", etc.
    The operations are generated randomly using the provided seed for reproducibility.
    
    Args:
        n: The size of the algebra (cardinality of the universe)
        arities: List of arities for the operations
        seed: Optional seed for the random number generator (None means use random seed)
        
    Returns:
        BasicAlgebra: A new random algebra
        
    Raises:
        ValueError: If there's an error during creation
    """
    
    @staticmethod
    def ternary_discriminator_algebra(card: int) -> "alg.BasicAlgebra": ...
    """Create a ternary discriminator algebra.
    
    A ternary discriminator algebra is an algebra with a single ternary operation
    called the discriminator. The discriminator operation d(x,y,z) satisfies:
    - d(x,y,z) = z if x = y
    - d(x,y,z) = x if x ≠ y
    
    Args:
        card: The cardinality of the algebra (size of the universe)
    
    Returns:
        A BasicAlgebra representing the ternary discriminator algebra
    
    Raises:
        ValueError: If cardinality is not positive or there's an error during creation
    """
    
    def full_transformation_semigroup(n: int, include_constants: bool, include_id: bool) -> "alg.BasicAlgebra": ...
    """Create the full transformation semigroup on n elements.
    
    The transformation semigroup consists of all functions from {0..n-1} to {0..n-1}.
    Each transformation is encoded as a Horner integer.
    
    Args:
        n: The size of the underlying set (must be at most 9)
        include_constants: Whether to include constant transformations (one for each element)
        include_id: Whether to include the identity transformation
    
    Returns:
        A BasicAlgebra representing the transformation semigroup algebra
    
    Raises:
        ValueError: If n > 9 or there's an error during creation
    """
    
    @staticmethod
    def member_of_quasivariety(a: "alg.BasicAlgebra", b: "alg.BasicAlgebra") -> Optional[List["alg.Homomorphism"]]: ...
    """Test if algebra A is in the quasivariety generated by algebra B.
    
    Returns a list of homomorphisms from A into B if A is in the quasivariety;
    otherwise returns None.
    
    Args:
        a: The algebra to test for membership (BasicAlgebra)
        b: The generating algebra (BasicAlgebra)
        
    Returns:
        List of Homomorphism objects if A is in the quasivariety, None otherwise
        
    Raises:
        ValueError: If there's an error during computation
    """
    
    @staticmethod
    def member_of_quasivariety_list(a: "alg.BasicAlgebra", gen_algs: List["alg.BasicAlgebra"]) -> Optional[List["alg.Homomorphism"]]: ...
    """Test if algebra A is in the quasivariety generated by a list of algebras.
    
    Returns a list of homomorphisms from A into the generating algebras if A is
    in the quasivariety; otherwise returns None.
    
    Args:
        a: The algebra to test for membership (BasicAlgebra)
        gen_algs: The list of generating algebras (list of BasicAlgebra)
        
    Returns:
        List of Homomorphism objects if A is in the quasivariety, None otherwise
        
        Raises:
        ValueError: If there's an error during computation
    """
    
    @staticmethod
    def member_of_quasivariety_gen_by_proper_subs(a: "alg.BasicAlgebra") -> Optional[List["alg.Homomorphism"]]: ...
    """Test if algebra A can be embedded into a product of proper subalgebras of A.
    
    This checks if A is in the quasivariety generated by its proper subalgebras.
    Returns a list of homomorphisms from A into A (with non-zero kernels) if A
    can be embedded; otherwise returns None.
    
    Args:
        a: The algebra to test (BasicAlgebra)
        
    Returns:
        List of Homomorphism objects if A can be embedded, None otherwise
        
    Raises:
        ValueError: If there's an error during computation
    """
    
    @staticmethod
    def quasi_critical_congruences(a: "alg.BasicAlgebra") -> List["alg.Partition"]: ...
    """Find all quasi-critical congruences of an algebra.
    
    A congruence theta is quasi-critical if A/theta is quasi-critical,
    i.e., A/theta is not a subdirect product of proper subalgebras.
    
    Args:
        a: The algebra to analyze (BasicAlgebra)
        
    Returns:
        List of Partition objects representing quasi-critical congruences
        
    Raises:
        ValueError: If there's an error during computation
    """
    
    @staticmethod
    def quasi_critical(a: "alg.BasicAlgebra") -> Optional[Dict["alg.Partition", List[int]]]: ...
    """Determine if an algebra is quasi-critical.
    
    An algebra is quasi-critical if it is not a subdirect product of proper subalgebras.
    This method returns a dictionary mapping congruences to subalgebra generators if
    the algebra is quasi-critical, or None if it is not.
    
    Note: This has been replaced by `member_of_quasivariety_gen_by_proper_subs` in newer code,
    but is kept for compatibility.
    
    Args:
        a: The algebra to test (BasicAlgebra)
        
    Returns:
        Dictionary mapping Partition objects to lists of generator indices if quasi-critical, None otherwise
        
    Raises:
        ValueError: If there's an error during computation
    """
    
    @staticmethod
    def unary_clone(pars: List["alg.Partition"], eta0: "alg.Partition", eta1: "alg.Partition") -> List["util.IntArray"]: ...
    """Compute the unary clone set from partitions.
    
    This function computes the set of all unary operations (represented as IntArray)
    that respect every partition in `pars` and also respect the partitions `eta0` and `eta1`,
    which meet and join to 0 and 1 and permute.
    
    Args:
        pars: List of partitions that the operations must respect
        eta0: First eta partition
        eta1: Second eta partition
        
    Returns:
        List of IntArray objects representing unary operations
        
    Raises:
        ValueError: If there's an error (e.g., empty partitions list or mismatched sizes)
    """

    def find_in_clone(ops: List["alg.op.IntOperation"], alg: "alg.BasicAlgebra") -> Dict["alg.op.OperationSymbol", str]: ...
    """Find operations in the clone of an algebra.
    
    This function tests if the given operations are in the clone of the algebra A
    and returns a mapping from OperationSymbols to terms (as strings), which will
    have entries for those operations which are in the clone.
    
    Args:
        ops: A list of operations on the set of A (IntOperation objects)
        alg: The algebra A (BasicAlgebra)
        
    Returns:
        Dictionary mapping OperationSymbol objects to term strings for operations found in the clone
        
    Raises:
        ValueError: If there's an error (e.g., empty operations list)
    """
    
    def unary_clone_alg_from_partitions(pars: List["alg.Partition"], eta0: "alg.Partition", eta1: "alg.Partition") -> "alg.BasicAlgebra": ...
    """Make the unary algebra whose operations are the clone of unary operations.
    
    This function computes the unary clone set and then creates a BasicAlgebra
    with one unary operation for each element in the clone set.
    
    Args:
        pars: List of partitions that the operations must respect
        eta0: First eta partition
        eta1: Second eta partition
        
    Returns:
        BasicAlgebra with unary operations from the clone
        
    Raises:
        ValueError: If there's an error (e.g., empty partitions list or mismatched sizes)
    """

# ============================================================================
# UTIL MODULE (Partial - will be expanded)
# ============================================================================

class util:
    """Utility module for utility functions and classes."""
    
    class IntArray:
        """Python wrapper for IntArray."""
        def __init__(self, size: int) -> None: ...
        @staticmethod
        def from_array(array: List[int]) -> "util.IntArray": ...
        def size(self) -> int: ...
        def get(self, index: int) -> int: ...
        def set(self, index: int, value: int) -> None: ...
        def as_slice(self) -> List[int]: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    class Horner: ...
    class SimpleList: ...
    class ArrayString: ...
    class PermutationGenerator: ...
    class ArrayIncrementorImpl: ...
    class SimpleArrayIncrementor: ...
    class IntTuples: ...
    class IntTuplesWithMin: ...
    class TupleWithMin: ...
    class FixedSizedSubsets: ...
    class Subsets: ...
    class Permutations: ...
    class LongListUtils: ...
    class SequenceGenerator: ...
    class NondecreasingSequenceIncrementor: ...
    class IncreasingSequenceIncrementor: ...
    class SequenceIncrementor: ...
    class LeftSequenceIncrementor: ...
    class PartitionArrayIncrementor: ...
    class VirtualLists: ...
