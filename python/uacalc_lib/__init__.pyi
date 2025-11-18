"""
Type stubs for uacalc_lib module.
This file provides type information for Python IDEs and type checkers.
"""

from typing import Any, List, Dict, Optional, Union, Tuple, Set
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
    
    def value_at(self, args: List[int]) -> int: ...
    """Evaluates the operation at the given integer arguments (alias for int_value_at)."""

    def value_at_arrays(self, args: List[List[int]]) -> List[int]: ...
    """Evaluates the operation on arrays of arguments."""

    def int_value_at_horner(self, arg: int) -> int: ...
    """Evaluates the operation using Horner encoding."""

    def make_table(self) -> None: ...
    """Creates the operation table for faster evaluation."""

    def get_table(self) -> Optional[List[int]]: ...
    """Returns the operation table if available, None otherwise.

    Returns:
        The operation table as a list of integers, or None if not available
    """

    def get_table_force(self, make_table: bool) -> Optional[List[int]]: ...
    """Returns the operation table, creating it if requested and not present."""

    def is_table_based(self) -> bool: ...
    """Checks if the operation is table-based."""

    def is_idempotent(self) -> bool: ...
    """Checks if the operation is idempotent (f(x,x,...,x) = x)."""

    def is_associative(self) -> bool: ...
    """Checks if the operation is associative (for binary operations)."""

    def is_commutative(self) -> bool: ...
    """Checks if the operation is commutative (for binary operations)."""

    def is_totally_symmetric(self) -> bool: ...
    """Checks if the operation is totally symmetric."""

    def is_maltsev(self) -> bool: ...
    """Checks if the operation is Maltsev (for ternary operations)."""

    def is_total(self) -> bool: ...
    """Checks if the operation is total."""

class Algebra(Protocol):
    """Protocol for algebra types in universal algebra.

    An algebra consists of a universe (set) and a collection of operations
    defined on that set. This protocol defines the interface that all algebras
    must implement.
    """
    def universe(self) -> Any: ...
    """Returns the universe of this algebra.

    Returns:
        The universe (set of elements)
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

    def operations(self) -> List[Operation]: ...
    """Returns a list of all operations in this algebra.

    Returns:
        List of Operation instances
    """

    def get_operation(self, sym: "alg.OperationSymbol") -> Optional[Operation]: ...
    """Gets operation by symbol.

    Args:
        sym: The operation symbol

    Returns:
        The operation if found, None otherwise
    """

    def operations_map(self) -> Dict["alg.OperationSymbol", Operation]: ...
    """Returns a map of operation symbols to operations.

    Returns:
        Dictionary mapping operation symbols to operations
    """

    def name(self) -> str: ...
    """Returns the name of this algebra."""

    def set_name(self, name: str) -> None: ...
    """Sets the name of this algebra.

    Args:
        name: The new name
    """

    def description(self) -> Optional[str]: ...
    """Returns the description of this algebra.

    Returns:
        The description if set, None otherwise
    """

    def set_description(self, desc: Optional[str]) -> None: ...
    """Sets the description of this algebra.

    Args:
        desc: The new description
    """

    def similarity_type(self) -> "alg.SimilarityType": ...
    """Returns the similarity type of this algebra.

    Returns:
        The similarity type
    """

    def update_similarity_type(self) -> None: ...
    """Updates the similarity type of this algebra."""

    def is_similar_to(self, other: "Algebra") -> bool: ...
    """Checks if this algebra is similar to another.

    Args:
        other: The other algebra

    Returns:
        True if similar, False otherwise
    """

    def make_operation_tables(self) -> None: ...
    """Creates operation tables for faster evaluation."""

    def constant_operations(self) -> List[Operation]: ...
    """Returns the constant operations in this algebra.

    Returns:
        List of constant operations
    """

    def is_idempotent(self) -> bool: ...
    """Checks if this algebra is idempotent.

    Returns:
        True if idempotent, False otherwise
    """

    def is_total(self) -> bool: ...
    """Checks if this algebra is total.

    Returns:
        True if total, False otherwise
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

class SmallLattice(Lattice):
   """Protocol for small lattice types.

   A small lattice is a finite lattice with indexed elements.
   This protocol extends the general Lattice protocol with operations
   specific to small finite lattices where elements can be indexed.
   The main addition is the ability to get upper covers by index.
   """
   def upper_covers_indices(self, index: int) -> List[int]: ...
   """Returns the indices of the upper covers of the element at the given index.

   Args:
       index: The index of the element whose upper covers are requested

   Returns:
       A list of indices representing the upper covers of the element
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
        def interpretation(self, algebra: "alg.BasicAlgebra") -> "alg.IntOperation": ...
        def substitute(self, var_map: Dict["terms.VariableImp", Union["terms.VariableImp", "terms.NonVariableTerm"]]) -> Union["terms.VariableImp", "terms.NonVariableTerm"]: ...
        def clone_box(self) -> Union["terms.VariableImp", "terms.NonVariableTerm"]: ...
        def to_string(self) -> str: ...
        def write_string_buffer(self, sb: str) -> None: ...
        def check(self) -> bool: ...
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
        def get_children(self) -> List[Union["terms.VariableImp", "terms.NonVariableTerm"]]: ...
        def eval(self, algebra: "alg.BasicAlgebra", var_map: Dict[str, int]) -> int: ...
        def int_eval(self, algebra: "alg.BasicAlgebra", var_map: Dict[str, int]) -> int: ...
        def interpretation(
            self,
            algebra: "alg.BasicAlgebra",
            varlist: List[str],
            use_all: bool,
        ) -> "alg.IntOperation": ...
        def substitute(self, var_map: Dict[str, Union["terms.VariableImp", "terms.NonVariableTerm"]]) -> Union["terms.VariableImp", "terms.NonVariableTerm"]: ...
        def to_string(self) -> str: ...
        def write_string_buffer(self, sb: str) -> str: ...
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
        def new_with_inteqs(
            inteqs: List[List["util.IntArray"]],
        ) -> "terms.Taylor": ...
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
        def interprets(self, term: Union["terms.VariableImp", "terms.NonVariableTerm"]) -> bool: ...
        def term_from_array(self, arr: List[int]) -> Union["terms.VariableImp", "terms.NonVariableTerm"]: ...
        @staticmethod
        def lexicographically_compare_terms(
            a: Union["terms.VariableImp", "terms.NonVariableTerm"],
            b: Union["terms.VariableImp", "terms.NonVariableTerm"],
        ) -> int: ...
        @staticmethod
        def lexicographically_compare_int_arrays(
            a: "util.IntArray",
            b: "util.IntArray",
        ) -> int: ...
        @staticmethod
        def lexicographically_compare_arrays(a: List[int], b: List[int]) -> int: ...
        @staticmethod
        def make_balanced_taylor_term(
            arity: int,
            equations: List[List["util.IntArray"]],
        ) -> Union["terms.VariableImp", "terms.NonVariableTerm"]: ...
        def arity(self) -> int: ...
        def inteqs(self) -> List[List["util.IntArray"]]: ...
        def equations(self) -> List[List["util.IntArray"]]: ...
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
    
    class Order(Protocol):
        """Protocol for order relations that can be implemented in Python.

        This protocol represents a partial order relation (≤) that can be implemented
        by Python classes. Implementations must satisfy the mathematical properties
        of a partial order: reflexivity, antisymmetry, and transitivity.
        
        Note: This is a Protocol (type hint only), not a concrete Rust export.
        Concrete implementations like DivisibilityOrder, PrefixOrder, and NaturalOrder
        are available as Rust classes.
        """
        def leq(self, a: Any, b: Any) -> bool: ...
        """Returns true if a ≤ b in this order relation.

        Args:
            a: First element
            b: Second element

        Returns:
            True if a ≤ b, False otherwise
        """

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
        def universe(self) -> List[int]: ...
        """Get universe as a list of integers (for BasicLattice<i32> only).

        Returns:
            List of integers representing the universe

        Raises:
            ValueError: If not available for this BasicLattice type
        """
        def leq(self, a: int, b: int) -> bool: ...
        """Check if a ≤ b in the lattice order (for BasicLattice<i32> only).

        Args:
            a: First element
            b: Second element

        Returns:
            True if a ≤ b, False otherwise

        Raises:
            ValueError: If not available for this BasicLattice type
        """
        def join(self, a: int, b: int) -> int: ...
        """Compute join of two elements (for BasicLattice<i32> only).

        Args:
            a: First element
            b: Second element

        Returns:
            The join (least upper bound) of a and b

        Raises:
            ValueError: If not available for this BasicLattice type
        """
        def meet(self, a: int, b: int) -> int: ...
        """Compute meet of two elements (for BasicLattice<i32> only).

        Args:
            a: First element
            b: Second element

        Returns:
            The meet (greatest lower bound) of a and b

        Raises:
            ValueError: If not available for this BasicLattice type
        """
        def filter(self, element: int) -> List[int]: ...
        """Get the filter (all elements ≥ the given element) (for BasicLattice<i32> only).

        Args:
            element: The element to get the filter for

        Returns:
            List of all elements greater than or equal to the given element

        Raises:
            ValueError: If not available for this BasicLattice type
        """
        def ideal(self, element: int) -> List[int]: ...
        """Get the ideal (all elements ≤ the given element) (for BasicLattice<i32> only).

        Args:
            element: The element to get the ideal for

        Returns:
            List of all elements less than or equal to the given element

        Raises:
            ValueError: If not available for this BasicLattice type
        """
        def join_irreducibles(self) -> List["alg.Partition"]: ...
        """Get join irreducibles (for BasicLattice<Partition> only, created from CongruenceLattice).

        Returns:
            List of join irreducible elements

        Raises:
            ValueError: If not available for this BasicLattice type
        """
        def zero(self) -> "alg.Partition": ...
        """Get zero (bottom) element (for BasicLattice<Partition> only).

        Returns:
            The zero (bottom) element

        Raises:
            ValueError: If not available for this BasicLattice type
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
        """Create an OrderedSet from a BasicLattice.
        
        This static method converts a BasicLattice<i32> to an OrderedSet.
        
        Args:
            lattice: The BasicLattice to convert (must be BasicLattice<i32>)
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
        ALG_EXT: str
        XML_EXT: str
        UAC_EXT: str
        UA_EXT: str
        CSV_EXT: str
        TXT_EXT: str
        UA_EXTS: List[str]
        ALL_ALG_EXTS: List[str]
        MACE4_EXTS: List[str]
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...
    
    @staticmethod
    def parse_line(line: str) -> int: ...
    @staticmethod
    def read_algebra_file(path: str) -> "alg.BasicAlgebra": ...
    @staticmethod
    def read_algebra_from_stream(data: bytes) -> "alg.BasicAlgebra": ...
    @staticmethod
    def read_algebra_list_file(path: str) -> List["alg.BasicAlgebra"]: ...
    @staticmethod
    def read_algebra_list_from_stream(data: bytes) -> "alg.BasicAlgebra": ...
    @staticmethod
    def convert_to_xml(path: str) -> None: ...
    @staticmethod
    def write_algebra_file(algebra: "alg.BasicAlgebra", path: str) -> None: ...
    @staticmethod
    def write_algebra_file_with_style(algebra: "alg.BasicAlgebra", path: str, old_style: bool) -> None: ...
    @staticmethod
    def read_projective_plane(path: str) -> "alg.BasicAlgebra": ...
    @staticmethod
    def read_projective_plane_from_stream(data: bytes) -> "alg.BasicAlgebra": ...

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
        def get_relations(self) -> List["eq.Equation"]: ...
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
    
    class PermutationGroup:
        """Represents a permutation group."""

        def __init__(self, name: str, generators: List[List[int]]) -> None: ...

        @staticmethod
        def new_with_universe(name: str, generators: List[List[int]], universe: List[List[int]]) -> "group.PermutationGroup": ...

        @staticmethod
        def new_safe(name: str, generators: List[List[int]]) -> "group.PermutationGroup": ...

        @staticmethod
        def new_with_universe_safe(name: str, generators: List[List[int]], universe: List[List[int]]) -> "group.PermutationGroup": ...

        @staticmethod
        def prod(p1: List[int], p2: List[int]) -> List[int]: ...

        @staticmethod
        def inv(p: List[int]) -> List[int]: ...

        @staticmethod
        def id(set_size: int) -> List[int]: ...

        def get_name(self) -> str: ...

        def get_generators(self) -> List[List[int]]: ...

        def get_universe_list(self) -> Optional[List[List[int]]]: ...

        def get_underlying_set_size(self) -> int: ...

        def get_identity(self) -> Optional[List[int]]: ...

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
            order: "lat.Order",
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
    
    # TODO: Register and expose AlgebraWithGeneratingVector in Rust bindings
    class AlgebraWithGeneratingVector:
        """Python wrapper for AlgebraWithGeneratingVector.

        Represents an algebra with an associated vector of elements that generates it.
        Allows repeats in generating vector, supports subdirect decomposition.
        """
        def __init__(self, alg: "alg.BasicAlgebra", vec: List[int]) -> None: ...
        def get_algebra(self) -> "alg.BasicAlgebra": ...
        def get_vector(self) -> List[int]: ...
        def is_image_of(self, other: "alg.AlgebraWithGeneratingVector") -> bool: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...
        def __lt__(self, other: "alg.AlgebraWithGeneratingVector") -> bool: ...
        def __le__(self, other: "alg.AlgebraWithGeneratingVector") -> bool: ...
        def __gt__(self, other: "alg.AlgebraWithGeneratingVector") -> bool: ...
        def __ge__(self, other: "alg.AlgebraWithGeneratingVector") -> bool: ...
        @staticmethod
        def si_decompose(alg: "alg.BasicAlgebra", vec: List[int]) -> List["alg.AlgebraWithGeneratingVector"]: ...
        @staticmethod
        def si_decompose_with_relations(alg: "alg.BasicAlgebra", vec: List[int], relations: List["alg.Partition"]) -> List["alg.AlgebraWithGeneratingVector"]: ...

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
        def int_value_at(self, args: List[int]) -> int: ...
    
        def value_at_arrays(self, args: List[List[int]]) -> List[int]: ...
    
        def int_value_at_horner(self, arg: int) -> int: ...
    
        def make_table(self) -> None: ...
    
        def value_at(self, args: List[int]) -> int: ...
    
        def value_at_arrays(self, args: List[List[int]]) -> List[int]: ...
    
        def int_value_at_horner(self, arg: int) -> int: ...
    
        def make_table(self) -> None: ...
    
        def get_table(self) -> Optional[List[int]]: ...
    
        def get_table_force(self, make_table: bool) -> Optional[List[int]]: ...
    
        def is_table_based(self) -> bool: ...
    
        def is_idempotent(self) -> bool: ...
    
        def is_associative(self) -> bool: ...
    
        def is_commutative(self) -> bool: ...
    
        def is_totally_symmetric(self) -> bool: ...
    
        def is_maltsev(self) -> bool: ...
    
        def is_total(self) -> bool: ...
    
        def get_table_force(self, make_table: bool) -> Optional[List[int]]: ...
    
        def is_table_based(self) -> bool: ...
    
        def is_idempotent(self) -> bool: ...
    
        def is_associative(self) -> bool: ...
    
        def is_commutative(self) -> bool: ...
    
        def is_totally_symmetric(self) -> bool: ...
    
        def is_maltsev(self) -> bool: ...
    
        def is_total(self) -> bool: ...
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
    
        def compare_to(self, other: "alg.OperationSymbol") -> int: ...
    
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
        @staticmethod
        def from_int_value_at_function(name: str, arity: int, set_size: int, int_value_at_fn: Any) -> "alg.AbstractIntOperation": ...
        @staticmethod
        def from_table(name: str, arity: int, set_size: int, table: Any) -> "alg.AbstractIntOperation": ...
        def arity(self) -> int: ...
        def get_set_size(self) -> int: ...
        def symbol(self) -> "alg.OperationSymbol": ...
        def value_at(self, args: List[int]) -> int: ...
        def int_value_at(self, args: List[int]) -> int: ...
        def is_total(self) -> bool: ...
        def make_table(self) -> None: ...
        def get_table(self) -> Optional[List[int]]: ...
        def is_table_based(self) -> bool: ...
        def is_idempotent(self) -> bool: ...
        def is_associative(self) -> bool: ...
        def is_commutative(self) -> bool: ...
        def is_totally_symmetric(self) -> bool: ...
        def is_maltsev(self) -> bool: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...
    
    class AbstractOperation:
        """Python wrapper for AbstractOperation that supports both integer and non-integer universes.

        This class provides operations that can work with both integer universes and arbitrary
        Python objects as universe elements. Operations can be defined using functions or tables.
        """

        @staticmethod
        def from_int_value_at_function(name: str, arity: int, set_size: int, int_value_at_fn: Any) -> "alg.AbstractOperation": ...
        """Create an AbstractOperation from an integer-valued function.

        Args:
            name: Name of the operation
            arity: Number of arguments the operation takes
            set_size: Size of the universe (for integer universes)
            int_value_at_fn: Function that takes a list of integers and returns an integer

        Returns:
            A new AbstractOperation instance
        """

        @staticmethod
        def from_value_at_function(name: str, arity: int, universe: List[Any], value_at_fn: Any) -> "alg.AbstractOperation": ...
        """Create an AbstractOperation from a value-valued function.

        Args:
            name: Name of the operation
            arity: Number of arguments the operation takes
            universe: List of universe elements (can be any Python objects)
            value_at_fn: Function that takes a list of universe elements and returns a universe element

        Returns:
            A new AbstractOperation instance
        """

        def arity(self) -> int: ...
        """Returns the arity (number of arguments) of this operation."""

        def get_set_size(self) -> int: ...
        """Returns the size of the universe."""

        def symbol(self) -> "alg.OperationSymbol": ...
        """Returns the operation symbol."""

        def int_value_at(self, args: List[int]) -> int: ...
        """Evaluate the operation with integer arguments.

        Args:
            args: List of integer arguments

        Returns:
            The result as an integer
        """

        def value_at(self, args: List[Any]) -> Any: ...
        """Evaluate the operation with universe element arguments.

        Args:
            args: List of universe elements

        Returns:
            The result as a universe element
        """

        def make_table(self) -> None: ...
        """Convert a function-based operation to a table-based operation.

        This method evaluates the operation for all possible argument combinations
        and stores the results in a lookup table for faster future evaluations.
        """

        def get_table(self) -> Optional[List[int]]: ...
        """Get the operation table if available.

        Returns:
            The operation table as a list of integers, or None if not table-based
        """

        def value_at_arrays(self, args: List[List[int]]) -> List[int]: ...
    
        def int_value_at_horner(self, arg: int) -> int: ...
    
        def get_table_force(self, make_table: bool) -> Optional[List[int]]: ...
    
        def is_table_based(self) -> bool: ...
        """Check if this operation is table-based.

        Returns:
            True if the operation uses a lookup table, False if function-based
        """

        def is_idempotent(self) -> bool: ...
        """Check if this operation is idempotent.

        An operation is idempotent if f(x, x, ..., x) = x for all x.

        Returns:
            True if idempotent, False otherwise
        """

        def is_associative(self) -> bool: ...
        """Check if this binary operation is associative.

        Returns:
            True if associative, False otherwise (or if not binary)
        """

        def is_commutative(self) -> bool: ...
        """Check if this binary operation is commutative.

        Returns:
            True if commutative, False otherwise (or if not binary)
        """

        def is_totally_symmetric(self) -> bool: ...
        """Check if this operation is totally symmetric.

        An operation is totally symmetric if swapping any two arguments
        doesn't change the result.

        Returns:
            True if totally symmetric, False otherwise
        """

        def is_maltsev(self) -> bool: ...
        """Check if this ternary operation satisfies the Maltsev condition.

        Returns:
            True if Maltsev, False otherwise (or if not ternary)
        """

        def is_total(self) -> bool: ...
        """Check if this operation is total.

        Returns:
            True (AbstractOperations are always total)
        """

        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...
    
    class Operations:
        """Operations module for operation creation and testing functions."""
    
        @staticmethod
        def make_int_operation(symbol: "alg.OperationSymbol") -> "alg.IntOperation": ...
    
        @staticmethod
        def make_random_operation(set_size: int, arity: int) -> "alg.IntOperation": ...
    
        @staticmethod
        def make_random_operation_with_seed(set_size: int, arity: int, seed: int) -> "alg.IntOperation": ...
    
        @staticmethod
        def make_derived_operation(op: "alg.Operation", derivation: str) -> "alg.Operation": ...
    
        @staticmethod
        def is_commutative(op: "alg.Operation") -> bool: ...
    
        @staticmethod
        def is_associative(op: "alg.Operation") -> bool: ...
    
        @staticmethod
        def is_idempotent(op: "alg.Operation") -> bool: ...
    
        @staticmethod
        def is_totally_symmetric(op: "alg.Operation") -> bool: ...
    
        @staticmethod
        def is_maltsev(op: "alg.Operation") -> bool: ...
    
        @staticmethod
        def is_total(op: "alg.Operation") -> bool: ...
    
        @staticmethod
        def commutes(op1: "alg.Operation", op2: "alg.Operation") -> bool: ...
    
        @staticmethod
        def find_difference(op1: "alg.Operation", op2: "alg.Operation") -> Optional[List[int]]: ...
    
        @staticmethod
        def make_map(domain: List[int], codomain: List[int]) -> Dict[int, int]: ...
    
        @staticmethod
        def power(op: "alg.Operation", n: int) -> "alg.Operation": ...
    
        @staticmethod
        def equal_values(op1: "alg.Operation", op2: "alg.Operation") -> bool: ...
    
        @staticmethod
        def make_left_shift(set_size: int) -> "alg.IntOperation": ...
    
        @staticmethod
        def make_module_operation(set_size: int, modulus: int) -> "alg.IntOperation": ...
    
        @staticmethod
        def ternary_discriminator(set_size: int) -> "alg.IntOperation": ...
    
    class OperationWithDefaultValue(AbstractOperation):
        """Python wrapper for OperationWithDefaultValue.

        A convenience class for UI that wraps operations with default value handling.
        Supports random value generation for undefined entries and provides idempotent
        operation support. Can convert to ordinary operations by filling in default values.
        """

        def __init__(self, op: "alg.AbstractOperation", default_value: int = -1) -> None:
            """Create OperationWithDefaultValue wrapping an operation with default value.

            Args:
                op: The operation to wrap
                default_value: Default value (-1 = undefined, -2 = random, >=0 = specific value)
            """

        @staticmethod
        def new_with_random(op: "alg.AbstractOperation") -> "alg.OperationWithDefaultValue":
            """Create OperationWithDefaultValue with random default values.

            Args:
                op: The operation to wrap

            Returns:
                New OperationWithDefaultValue instance
            """

        @staticmethod
        def new_with_idempotent(op: "alg.AbstractOperation", default_value: int = -1) -> "alg.OperationWithDefaultValue":
            """Create OperationWithDefaultValue with idempotent support.

            Args:
                op: The operation to wrap
                default_value: Default value

            Returns:
                New OperationWithDefaultValue instance
            """

        def int_value_at(self, args: Union[List[int], int]) -> int:
            """Evaluate the operation at the given arguments.

            Supports both list of integers and single integer (for unary operations).

            Args:
                args: Arguments as list or single int

            Returns:
                The result of the operation
            """

        def value_at(self, args: List[int]) -> int:
            """Evaluate the operation at the given integer arguments (alias for int_value_at).

            Args:
                args: List of integer arguments

            Returns:
                The result of the operation
            """

        def get_default_value(self) -> int:
            """Get the default value.

            Returns:
                The default value (-1 = undefined, -2 = random, >=0 = specific value)
            """

        def set_default_value(self, default_value: int) -> None:
            """Set the default value.

            Args:
                default_value: The default value to set
            """

        def is_total(self) -> bool:
            """Check if the operation is total.

            Returns:
                True if total, False otherwise
            """

        def update_random_value_table(self) -> None:
            """Update the random value table for undefined entries."""

        def get_random_value_table(self) -> Optional[List[int]]:
            """Get the random value table.

            Returns:
                The random value table if available, None otherwise
            """

        def is_idempotent_set(self) -> bool:
            """Check if idempotent operations are set.

            Returns:
                True if idempotent operations are set, False otherwise
            """

        def set_idempotent(self, idempotent: bool) -> None:
            """Set idempotent operation support.

            Args:
                idempotent: Whether to enable idempotent operations
            """

        def make_idempotent(self) -> None:
            """Make the operation idempotent."""

        def is_diagonal(self, i: int, j: int) -> bool:
            """Check if the given indices form a diagonal.

            Args:
                i: First index
                j: Second index

            Returns:
                True if diagonal, False otherwise
            """

        def make_table(self) -> None:
            """Create the operation table for faster evaluation."""

        def get_total_table(self) -> Optional[List[int]]:
            """Get the total operation table.

            Returns:
                The total table if available, None otherwise
            """

        def make_ordinary_operation(self) -> "alg.AbstractOperation":
            """Convert to an ordinary operation by filling in default values.

            Returns:
                An ordinary operation with default values filled in
            """

        @staticmethod
        def make_ordinary(operations: List["alg.AbstractOperation"]) -> List["alg.AbstractOperation"]:
            """Convert a list of operations to ordinary operations.

            Args:
                operations: List of operations to convert

            Returns:
                List of ordinary operations
            """

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
        def __lt__(self, other: "alg.SimilarityType") -> bool: ...
        def __le__(self, other: "alg.SimilarityType") -> bool: ...
        def __gt__(self, other: "alg.SimilarityType") -> bool: ...
        def __ge__(self, other: "alg.SimilarityType") -> bool: ...
    class ParameterizedOperation:
        def __init__(self, name: str, symbol_name: str, set_size_exp: str, parameter_names: List[str], arity_exp: str, description: str, default_value_exp: str, definition_exp: str) -> None: ...
        @staticmethod
        def sub_parm_values(parameterized_string: str, parm_map: Dict[str, str]) -> str: ...
        def get_name(self) -> str: ...
        def get_symbol_name(self) -> str: ...
        def get_set_size_exp(self) -> str: ...
        def get_parameter_names(self) -> List[str]: ...
        def get_arity_exp(self) -> str: ...
        def get_description(self) -> str: ...
        def get_default_value_exp(self) -> str: ...
        def get_definition_exp(self) -> str: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...

    
    # Advanced algebra types
    class Homomorphism:
        """Python wrapper for Homomorphism - represents a homomorphism between two algebras.

        A homomorphism is a structure-preserving map between two algebras of the same similarity type.
        It preserves all operations of the algebras.
        """
        def __init__(self, domain: "alg.BasicAlgebra", range: "alg.BasicAlgebra", map: Dict[int, int]) -> None:
            """Create a new Homomorphism.

            Args:
                domain: The domain algebra (source)
                range: The range algebra (target)
                map: Dictionary mapping domain elements to range elements

            Raises:
                ValueError: If the map is not a valid homomorphism
            """
        def kernel(self) -> "alg.Partition":
            """Compute the kernel of this homomorphism.

            The kernel is the congruence relation on the domain algebra
            consisting of pairs that map to the same element in the range.

            Returns:
                The kernel partition
            """
        @staticmethod
        def product_homo(homomorphisms: List["alg.Homomorphism"]) -> List["util.IntArray"]:
            """Create the product homomorphism from a list of homomorphisms.

            Args:
                homomorphisms: List of homomorphisms to combine

            Returns:
                List of IntArray objects representing the product homomorphism
            """
        def get_domain(self) -> "alg.BasicAlgebra":
            """Get the domain algebra.

            Returns:
                The domain algebra
            """
        def set_domain(self, domain: "alg.BasicAlgebra") -> None:
            """Set the domain algebra.

            Args:
                domain: The new domain algebra
            """
        def get_range(self) -> "alg.BasicAlgebra":
            """Get the range algebra.

            Returns:
                The range algebra
            """
        def set_range(self, range: "alg.BasicAlgebra") -> None:
            """Set the range algebra.

            Args:
                range: The new range algebra
            """
        def get_map(self) -> Dict[int, int]:
            """Get the mapping dictionary.

            Returns:
                Dictionary mapping domain elements to range elements
            """
        def set_map(self, map: Dict[int, int]) -> None:
            """Set the mapping dictionary.

            Args:
                map: The new mapping dictionary
            """
        def __str__(self) -> str:
            """String representation of the homomorphism."""
        def __repr__(self) -> str:
            """Detailed string representation of the homomorphism."""
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
    class BasicBinaryRelation:
        """Python wrapper for BasicBinaryRelation.

        A basic implementation of a binary relation on a finite universe.
        Relations are stored as ordered pairs (i,j) where i,j are integers
        from 0 to universe_size-1.
        """
        def __init__(self, size: int) -> None:
            """Create a new empty binary relation with the given universe size.

            Args:
                size: The size of the universe (must be positive)

            Raises:
                ValueError: If size is not positive
            """
        def universe_size(self) -> int:
            """Get the size of the universe.

            Returns:
                The universe size
            """
        def size(self) -> int:
            """Get the number of pairs in the relation.

            Returns:
                The number of related pairs
            """
        def is_empty(self) -> bool:
            """Check if the relation is empty.

            Returns:
                True if the relation contains no pairs, False otherwise
            """
        def is_related(self, i: int, j: int) -> bool:
            """Check if the pair (i,j) is in the relation.

            Args:
                i: First element
                j: Second element

            Returns:
                True if (i,j) is related, False otherwise

            Raises:
                ValueError: If i or j is out of bounds
            """
        def add(self, i: int, j: int) -> None:
            """Add the pair (i,j) to the relation.

            Args:
                i: First element
                j: Second element

            Raises:
                ValueError: If i or j is out of bounds
            """
        def remove(self, i: int, j: int) -> None:
            """Remove the pair (i,j) from the relation.

            Args:
                i: First element
                j: Second element

            Raises:
                ValueError: If i or j is out of bounds
            """
        def clear(self) -> None:
            """Remove all pairs from the relation."""
        def get_pairs(self) -> List[List[int]]:
            """Get all pairs in the relation as a list of [i,j] lists.

            Returns:
                List of pairs, where each pair is [i, j]
            """
        def is_reflexive(self) -> bool:
            """Check if the relation is reflexive.

            A relation is reflexive if for all i, (i,i) is in the relation.

            Returns:
                True if reflexive, False otherwise
            """
        def is_symmetric(self) -> bool:
            """Check if the relation is symmetric.

            A relation is symmetric if for all i,j, if (i,j) is in the relation
            then (j,i) is also in the relation.

            Returns:
                True if symmetric, False otherwise
            """
        def is_transitive(self) -> bool:
            """Check if the relation is transitive.

            A relation is transitive if for all i,j,k, if (i,j) and (j,k) are
            in the relation then (i,k) is also in the relation.

            Returns:
                True if transitive, False otherwise
            """
        def is_equivalence(self) -> bool:
            """Check if the relation is an equivalence relation.

            A relation is an equivalence relation if it is reflexive,
            symmetric, and transitive.

            Returns:
                True if equivalence relation, False otherwise
            """
        def compose(self, other: "alg.BasicBinaryRelation") -> "alg.BasicBinaryRelation":
            """Compute the composition of this relation with another.

            The composition R∘S is defined as: (i,k) ∈ R∘S iff there exists j
            such that (i,j) ∈ S and (j,k) ∈ R.

            Args:
                other: The relation to compose with (S in the definition above)

            Returns:
                The composition relation

            Raises:
                ValueError: If universe sizes don't match
            """
        @staticmethod
        def identity(size: int) -> "alg.BasicBinaryRelation":
            """Create the identity relation on a universe of the given size.

            The identity relation contains all pairs (i,i) for i in 0..size-1.

            Args:
                size: The universe size

            Returns:
                The identity relation
            """
        @staticmethod
        def universal(size: int) -> "alg.BasicBinaryRelation":
            """Create the universal relation on a universe of the given size.

            The universal relation contains all possible pairs (i,j).

            Args:
                size: The universe size

            Returns:
                The universal relation
            """
        @staticmethod
        def empty(size: int) -> "alg.BasicBinaryRelation":
            """Create the empty relation on a universe of the given size.

            The empty relation contains no pairs.

            Args:
                size: The universe size

            Returns:
                The empty relation
            """
        def __str__(self) -> str:
            """Get a string representation of the relation."""
        def __repr__(self) -> str:
            """Get a detailed string representation of the relation."""
        def __eq__(self, other: object) -> bool:
            """Check equality with another relation."""
        def __hash__(self) -> int:
            """Get the hash value of the relation."""
        def __iter__(self) -> Any:
            """Get an iterator over the pairs in the relation."""
    class CentralityData:
        """Python wrapper for CentralityData.

        A data structure holding centrality information including two tolerance relations
        (S and T), a congruence delta, and failure information for centrality, weak centrality,
        and strong rectangularity.
        """
        def __init__(
            self,
            left: "alg.BasicBinaryRelation",
            right: "alg.BasicBinaryRelation",
            delta: "alg.Partition",
        ) -> None:
            """Create a new CentralityData instance.

            Args:
                left: The left tolerance relation (S)
                right: The right tolerance relation (T)
                delta: The congruence delta

            Raises:
                ValueError: If the relations have incompatible universe sizes
            """
        def universe_size(self) -> int:
            """Get the universe size.

            Returns:
                The universe size
            """
        def delta_blocks(self) -> int:
            """Get the number of blocks in delta.

            Returns:
                The number of blocks
            """
        def left(self) -> "alg.BasicBinaryRelation":
            """Get the left tolerance relation (S).

            Returns:
                The left tolerance relation
            """
        def right(self) -> "alg.BasicBinaryRelation":
            """Get the right tolerance relation (T).

            Returns:
                The right tolerance relation
            """
        def delta(self) -> "alg.Partition":
            """Get the delta partition.

            Returns:
                The delta partition
            """
        def compare_to(self, other: "alg.CentralityData") -> int:
            """Compare with another CentralityData.

            Args:
                other: The other CentralityData to compare with

            Returns:
                -1 if self < other, 0 if equal, 1 if self > other
            """
        def __str__(self) -> str:
            """Get a string representation of the CentralityData."""
        def __repr__(self) -> str:
            """Get a detailed string representation of the CentralityData."""
        def __eq__(self, other: object) -> bool:
            """Check equality with another object."""
        def __lt__(self, other: "alg.CentralityData") -> bool:
            """Check if self < other."""
        def __le__(self, other: "alg.CentralityData") -> bool:
            """Check if self <= other."""
        def __gt__(self, other: "alg.CentralityData") -> bool:
            """Check if self > other."""
        def __ge__(self, other: "alg.CentralityData") -> bool:
            """Check if self >= other."""
    class Partition:
        """Python wrapper for Partition - represents a partition of a set.

        A partition divides a set into non-empty, pairwise disjoint subsets called blocks.
        Partitions are fundamental in congruence theory and polymorphism calculations.
        """
        def __init__(self, array: List[int]) -> None:
            """Create a new Partition from an array representation.

            Args:
                array: The array representation of the partition

            Raises:
                ValueError: If the array is invalid
            """
            ...

        @staticmethod
        def from_string(str: str) -> "alg.Partition":
            """Create a new Partition from a string representation.

            Args:
                str: String representation of the partition

            Returns:
                A new Partition instance

            Raises:
                ValueError: If the string format is invalid
            """
            ...

        @staticmethod
        def from_string_with_length(str: str, length: int) -> "alg.Partition":
            """Create a new Partition from a string representation with specified length.

            Args:
                str: String representation of the partition
                length: Maximum universe size (-1 for auto-detect)

            Returns:
                A new Partition instance

            Raises:
                ValueError: If the string format is invalid
            """
            ...

        @staticmethod
        def zero(size: int) -> "alg.Partition":
            """Create the zero partition (all elements in separate blocks).

            Args:
                size: Size of the universe

            Returns:
                Zero partition
            """
            ...

        @staticmethod
        def one(size: int) -> "alg.Partition":
            """Create the one partition (all elements in one block).

            Args:
                size: Size of the universe

            Returns:
                One partition
            """
            ...

        def universe_size(self) -> int:
            """Get the universe size (number of elements).

            Returns:
                The universe size
            """
            ...

        def number_of_blocks(self) -> int:
            """Get the number of blocks in the partition.

            Returns:
                The number of blocks
            """
            ...

        def is_related(self, i: int, j: int) -> bool:
            """Check if two elements are related (in the same block).

            Args:
                i: First element
                j: Second element

            Returns:
                True if elements are in the same block
            """
            ...

        def representative(self, i: int) -> int:
            """Get the representative (root) of the block containing element i.

            Args:
                i: Element index

            Returns:
                Representative element index
            """
            ...

        def is_representative(self, i: int) -> bool:
            """Check if an element is a representative (root) of its block.

            Args:
                i: Element index

            Returns:
                True if element is representative
            """
            ...

        def representatives(self) -> List[int]:
            """Get all representatives of the partition.

            Returns:
                List of representative indices
            """
            ...

        def block_index(self, i: int) -> int:
            """Get the index of the block containing element i.

            Args:
                i: Element index

            Returns:
                Block index

            Raises:
                ValueError: If element not found in representatives
            """
            ...

        def get_blocks(self) -> List[List[int]]:
            """Get the blocks of the partition as an array of arrays.

            Returns:
                List of blocks, where each block is a list of element indices
            """
            ...

        def join_blocks(self, r: int, s: int) -> None:
            """Join two blocks by their representatives.

            Args:
                r: Representative of first block
                s: Representative of second block

            Raises:
                ValueError: If r or s are not representatives or if r == s
            """
            ...

        def normalize(self) -> None:
            """Normalize the partition representation."""
            ...

        def is_zero(self) -> bool:
            """Check if this is the zero partition (all elements in separate blocks).

            Returns:
                True if this is the zero partition
            """
            ...

        def is_uniform(self) -> bool:
            """Check if this partition is uniform (all blocks have the same size).

            Returns:
                True if all blocks have the same size
            """
            ...

        def is_initial_lex_representative(self) -> bool:
            """Check if this partition is in initial lexicographic representative form.

            Returns:
                True if in initial lexicographic representative form
            """
            ...

        def rank(self) -> int:
            """Get the rank of the partition (universe size - number of blocks).

            Returns:
                The rank
            """
            ...

        def to_array(self) -> List[int]:
            """Get the array representation of the partition.

            Returns:
                Array representation
            """
            ...

        def to_string(self) -> str:
            """Get the string representation of the partition.

            Returns:
                String representation
            """
            ...

        def le(self, other: "alg.Partition") -> bool:
            """Check if this partition is less than or equal to another.

            Args:
                other: The other partition

            Returns:
                True if this partition is less than or equal to the other
            """
            ...

        def meet(self, other: "alg.Partition") -> "alg.Partition":
            """Get the meet of this partition with another.

            Args:
                other: The other partition

            Returns:
                The meet partition

            Raises:
                ValueError: If operation fails
            """
            ...

        def join(self, other: "alg.Partition") -> "alg.Partition":
            """Get the join of this partition with another.

            Args:
                other: The other partition

            Returns:
                The join partition

            Raises:
                ValueError: If operation fails
            """
            ...

        def __str__(self) -> str:
            """Python string representation."""
            ...

        def __repr__(self) -> str:
            """Python repr representation."""
            ...

        def __eq__(self, other: object) -> bool:
            """Python equality comparison."""
            ...

        def __hash__(self) -> int:
            """Python hash function."""
            ...

        def to_binary_relation(self) -> "alg.BasicBinaryRelation":
            """Convert this partition to a BasicBinaryRelation.

            Returns:
                The equivalent BasicBinaryRelation
            """
            ...

        def leq(self, other: "alg.Partition") -> bool:
            """leq alias for 'le' method.

            Args:
                other: The other partition

            Returns:
                True if this partition is less than or equal to the other
            """
            ...

        def to_string_with_type(self, print_type: "alg.PrintType", max_len: Optional[int] = None) -> str:
            """Convert to string with specified print type and maximum length.

            Args:
                print_type: The print type struct
                max_len: The max length, or None

            Returns:
                String representation
            """
            ...

        def to_string_with_max_len(self, max_len: int) -> str:
            """Convert to string with maximum length.

            Args:
                max_len: The max length

            Returns:
                String representation
            """
            ...

        def __lt__(self, other: "alg.Partition") -> bool:
            """Python comparison (less than)."""
            ...

        def __le__(self, other: "alg.Partition") -> bool:
            """Python comparison (less than or equal)."""
            ...

        def __gt__(self, other: "alg.Partition") -> bool:
            """Python comparison (greater than)."""
            ...

        def __ge__(self, other: "alg.Partition") -> bool:
            """Python comparison (greater than or equal)."""
            ...

        @staticmethod
        def unary_polymorphisms(pars: List["alg.Partition"]) -> List["util.IntArray"]:
            """Compute unary polymorphisms from a list of partitions.

            Args:
                pars: List of partitions to compute polymorphisms from

            Returns:
                List of IntArray objects representing unary polymorphisms
            """
            ...

        @staticmethod
        def binary_polymorphisms(pars: List["alg.Partition"], unary_clone: List["util.IntArray"]) -> List["util.IntArray"]:
            """Compute binary polymorphisms from a list of partitions and unary clone.

            Args:
                pars: List of partitions to compute polymorphisms from
                unary_clone: List of unary operations from the clone

            Returns:
                List of IntArray objects representing binary polymorphisms
            """
            ...

        @staticmethod
        def unary_polymorphisms_algebra(pars: List["alg.Partition"]) -> "alg.BasicAlgebra":
            """Create an algebra from unary polymorphisms of partitions.

            Args:
                pars: List of partitions to compute polymorphisms from

            Returns:
                BasicAlgebra representing the unary polymorphisms algebra
            """
            ...

        @staticmethod
        def binary_polymorphisms_algebra(pars: List["alg.Partition"]) -> "alg.BasicAlgebra":
            """Create an algebra from binary polymorphisms of partitions.

            Args:
                pars: List of partitions to compute polymorphisms from

            Returns:
                BasicAlgebra representing the binary polymorphisms algebra
            """
            ...
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
    class BasicSet:
        """Python wrapper for BasicSet - represents a set of integers {0, 1, ..., n-1}.

        BasicSet represents a set of integers with basic set operations like union,
        intersection, and subset checking. Elements are always kept in sorted order.
        """

        EMPTY_SET: "alg.BasicSet"
        """The empty set constant."""

        def __init__(self, elements: List[int]) -> None:
            """Create a new BasicSet from a list of integers.

            Args:
                elements: List of integers representing the set elements

            Raises:
                ValueError: If elements contains duplicates or negative values
            """

        def normalize(self) -> None:
            """Sort the array in ascending order.

            This method ensures the elements are in sorted order and removes duplicates.
            """

        def leq(self, other: "alg.BasicSet") -> bool:
            """Check if this set is a subset of another set.

            Args:
                other: The other BasicSet to compare against

            Returns:
                True if this set is a subset of other, False otherwise
            """

        def contains(self, element: int) -> bool:
            """Check if the set contains a specific element.

            Args:
                element: The element to check for membership

            Returns:
                True if the element is in the set, False otherwise
            """

        def set_difference(self, other: "alg.BasicSet") -> "alg.BasicSet":
            """Compute the set difference (this - other).

            Args:
                other: The set to subtract

            Returns:
                A new BasicSet containing elements in this set but not in other
            """

        def intersection(self, other: "alg.BasicSet") -> "alg.BasicSet":
            """Compute the intersection of this set with another set.

            Args:
                other: The other set to intersect with

            Returns:
                A new BasicSet containing elements common to both sets
            """

        def union(self, other: "alg.BasicSet") -> "alg.BasicSet":
            """Compute the union of this set with another set.

            Args:
                other: The other set to union with

            Returns:
                A new BasicSet containing all elements from both sets
            """

        def to_string(self, algebra: "alg.BasicAlgebra") -> str:
            """Convert to string representation using algebra element names.

            Args:
                algebra: The algebra providing element names

            Returns:
                String representation of the set using algebra element names
            """

        @staticmethod
        def leq_static(u: List[int], v: List[int]) -> bool:
            """Check if array u is a subset of array v.

            Args:
                u: First array of integers
                v: Second array of integers

            Returns:
                True if u is a subset of v, False otherwise
            """

        @staticmethod
        def intersection_static(set1: "alg.BasicSet", set2: "alg.BasicSet") -> "alg.BasicSet":
            """Compute the intersection of two BasicSets (static method).

            Args:
                set1: First BasicSet
                set2: Second BasicSet

            Returns:
                A new BasicSet containing the intersection
            """

        @staticmethod
        def union_static(set1: "alg.BasicSet", set2: "alg.BasicSet") -> "alg.BasicSet":
            """Compute the union of two BasicSets (static method).

            Args:
                set1: First BasicSet
                set2: Second BasicSet

            Returns:
                A new BasicSet containing the union
            """

        def __str__(self) -> str:
            """String representation of the set."""

        def __repr__(self) -> str:
            """Detailed string representation of the set."""

        def __eq__(self, other: object) -> bool:
            """Check equality with another object."""

        def __hash__(self) -> int:
            """Get the hash value of the set."""

        def __lt__(self, other: "alg.BasicSet") -> bool:
            """Less than comparison (lexicographic ordering)."""

        def __le__(self, other: "alg.BasicSet") -> bool:
            """Less than or equal comparison."""

        def __gt__(self, other: "alg.BasicSet") -> bool:
            """Greater than comparison."""

        def __ge__(self, other: "alg.BasicSet") -> bool:
            """Greater than or equal comparison."""
    class FreeAlgebra: ...
    class ProductAlgebra:
        """Python wrapper for ProductAlgebra - represents the direct product of algebras.

        A ProductAlgebra is the direct product of a list of SmallAlgebras.
        The universe consists of all tuples from the Cartesian product of the
        factor algebras' universes. Operations are defined componentwise.
        """

        def __init__(self, name: str, algebras: List["alg.BasicAlgebra"]) -> None:
            """Create a new ProductAlgebra from a list of algebras.

            Args:
                name: Name of the product algebra
                algebras: List of algebras to form the product

            Raises:
                ValueError: If algebras are incompatible or empty
            """

        @staticmethod
        def calc_card(sizes: List[int]) -> int:
            """Calculate the product cardinality.

            Args:
                sizes: The sizes of the algebras

            Returns:
                The product cardinality, or -1 if too large, or 0 if any factor is empty

            Raises:
                ValueError: If sizes array is empty
            """

        def number_of_factors(self) -> int:
            """Get the number of factor algebras.

            Returns:
                The number of algebras in the product
            """

        def get_sizes(self) -> List[int]:
            """Get the sizes of each factor algebra.

            Returns:
                Sizes of the factor algebras
            """

        def cardinality(self) -> int:
            """Get the cardinality of this product algebra.

            Returns:
                The cardinality (size of the universe)
            """

        def get_element(self, k: int) -> int:
            """Get the element at the given index.

            Args:
                k: Index of the element

            Returns:
                The element at index k, or -1 if out of bounds
            """

        def element_index(self, elem: int) -> int:
            """Get the index of an element in the universe.

            Args:
                elem: The element to find

            Returns:
                The index of the element, or -1 if not found
            """

        def algebra_type(self) -> str:
            """Get the algebra type.

            Returns:
                The algebra type ("Product")
            """

        def name(self) -> str:
            """Get the name of this algebra.

            Returns:
                The name of the algebra
            """

        def set_name(self, name: str) -> None:
            """Set the name of this algebra.

            Args:
                name: The new name
            """

        def make_operation_tables(self) -> None:
            """Make operation tables for all operations."""

        def __str__(self) -> str:
            """Python string representation."""

        def __repr__(self) -> str:
            """Python repr representation."""

        def con(self) -> "alg.CongruenceLattice":
            """Get the congruence lattice (lazy initialization).

            Returns:
                The congruence lattice
            """

        def sub(self) -> "alg.SubalgebraLattice":
            """Get the subalgebra lattice (lazy initialization).

            Returns:
                The subalgebra lattice
            """
    class PowerAlgebra:
        """Python wrapper for PowerAlgebra - represents the power of an algebra.

        A PowerAlgebra is the direct power A^k of a SmallAlgebra A, where k is the power.
        The universe consists of all k-tuples of elements from A, and operations are
        defined componentwise.
        """

        def __init__(self, root: "alg.BasicAlgebra", power: int) -> None:
            """Create a new PowerAlgebra from a root algebra and power.

            Args:
                root: The algebra to raise to a power
                power: The power/exponent (number of copies)

            Raises:
                ValueError: If power is invalid or algebra is incompatible
            """

        @staticmethod
        def new_with_name(name: str, root: "alg.BasicAlgebra", power: int) -> "alg.PowerAlgebra":
            """Create a new PowerAlgebra with a custom name.

            Args:
                name: The name for the power algebra
                root: The algebra to raise to a power
                power: The power/exponent (number of copies)

            Returns:
                A new PowerAlgebra instance

            Raises:
                ValueError: If power is invalid or algebra is incompatible
            """

        def get_root(self) -> "alg.BasicAlgebra":
            """Get the root algebra.

            Returns:
                The root algebra
            """

        def parent(self) -> "alg.BasicAlgebra":
            """Get the parent algebra (same as root for power algebra).

            Returns:
                The parent algebra
            """

        def parents(self) -> List["alg.BasicAlgebra"]:
            """Get the parent algebras (list containing the root algebra).

            Returns:
                List containing the root algebra
            """

        def get_power(self) -> int:
            """Get the power/exponent.

            Returns:
                The power (number of copies of the root algebra)
            """

        def get_root_size(self) -> int:
            """Get the size of the root algebra.

            Returns:
                The cardinality of the root algebra
            """

        def cardinality(self) -> int:
            """Get the cardinality of this power algebra.

            Returns:
                The cardinality of the power algebra
            """

        def name(self) -> str:
            """Get the name of this power algebra.

            Returns:
                The name of the power algebra
            """

        def set_name(self, name: str) -> None:
            """Set the name of this power algebra.

            Args:
                name: The new name
            """

        def description(self) -> Optional[str]:
            """Get the description of this power algebra.

            Returns:
                The description of the power algebra
            """

        def set_description(self, description: Optional[str]) -> None:
            """Set the description of this power algebra.

            Args:
                description: The new description
            """

        def algebra_type(self) -> str:
            """Get the algebra type.

            Returns:
                The algebra type ("Power")
            """

        def operations(self) -> List[Tuple[str, int]]:
            """Get the operations of this power algebra.

            Returns:
                List of operation names and arities as tuples
            """

        def is_unary(self) -> bool:
            """Check if this power algebra is unary.

            Returns:
                True if the algebra is unary, False otherwise
            """

        def is_idempotent(self) -> bool:
            """Check if this power algebra is idempotent.

            Returns:
                True if the algebra is idempotent, False otherwise
            """

        def is_total(self) -> bool:
            """Check if this power algebra is total.

            Returns:
                True if the algebra is total, False otherwise
            """

        def __str__(self) -> str:
            """String representation of the power algebra."""

        def __repr__(self) -> str:
            """Detailed string representation of the power algebra."""

        def __eq__(self, other: object) -> bool:
            """Check equality with another object."""

        def __hash__(self) -> int:
            """Get the hash value of the power algebra."""

        def con(self) -> "alg.CongruenceLattice":
            """Get the congruence lattice (lazy initialization).

            Returns:
                The congruence lattice
            """

        def sub(self) -> "alg.SubalgebraLattice":
            """Get the subalgebra lattice (lazy initialization).

            Returns:
                The subalgebra lattice
            """
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
        def get_element(self, k: int) -> Optional[int]: ...
        """Get the k-th element of the universe.

        Args:
            k: The index of the element to retrieve

        Returns:
            Optional[int]: The element at index k, or None if k is out of bounds
        """
        def element_index(self, elem: int) -> Optional[int]: ...
        """Get the index of an element in the universe.

        Args:
            elem: The element to find the index for

        Returns:
            Optional[int]: The index of the element, or None if not found
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
        def get_universe_list(self) -> Optional[List[int]]: ...
        """Get the universe as a list.
    
        Returns:
            None (matching Java behavior)
        """
        def get_universe_order(self) -> Optional[Dict[int, int]]: ...
        """Get the universe order.
    
        Returns:
            None (matching Java behavior)
        """
        def make_operation_tables(self) -> None: ...
        """Build operation tables.
    
        Creates operation tables for faster evaluation.
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
    
    class ParameterizedAlgebra:
        """Python wrapper for ParameterizedAlgebra - represents parameterized algebras with configurable parameters.

        A parameterized algebra consists of parameter names, a name, set size expression,
        description, and a list of parameterized operations.
        """
        def get_parameter_map(self, values: List[int]) -> Dict[str, str]: ...
        """Create a parameter mapping from a list of integer values.

        Maps parameter names to their corresponding string values based on the provided
        integer values list. The mapping is used to substitute parameters in expressions.

        Args:
            values: List of integer values to map to parameter names

        Returns:
            Dictionary mapping parameter names to their string values
        """
    class MaltsevProductDecomposition:
        """Python wrapper for MaltsevProductDecomposition.

        A decomposition of idempotent algebras into quotient and block subalgebras
        for Maltsev product analysis.
        """
        def __init__(self, algebra: "alg.BasicAlgebra", congruence: "alg.Partition") -> None: ...
        def get_congruence(self) -> "alg.Partition": ...
        def set_congruence(self, congruence: "alg.Partition") -> None: ...
        def get_algebra(self) -> "alg.BasicAlgebra": ...
        def set_algebra(self, algebra: "alg.BasicAlgebra") -> None: ...
        def get_block_algebras(self) -> List["alg.BasicAlgebra"]: ...
        def set_block_algebras(self, block_algebras: List["alg.BasicAlgebra"]) -> None: ...
        def get_quotient_algebra(self) -> "alg.BasicAlgebra": ...
        def set_quotient_algebra(self, quotient_algebra: "alg.BasicAlgebra") -> None: ...
    
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
    
    class GeneralAlgebra:
        """Python wrapper for GeneralAlgebra."""
        def __init__(
            self,
            name: str,
            universe: List[Any],
            operations: Optional[List[Any]] = None,
        ) -> None: ...
        @staticmethod
        def with_name(name: str) -> "alg.GeneralAlgebra": ...
        @staticmethod
        def with_universe(name: str, universe: List[Any]) -> "alg.GeneralAlgebra": ...
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
        def universe(self) -> List[Any]: ...
        def get_operations(self) -> List[Any]: ...
        def add_operation(self, operation: Any) -> None: ...
        def get_operation(self, index: int) -> Any: ...
        def operations_count(self) -> int: ...
        def set_monitor(self, m: Any) -> None: ...
        def get_monitor(self) -> Any: ...
        def get_operations_map(self) -> Dict["alg.OperationSymbol", Any]: ...
        def get_operation_by_symbol(self, sym: "alg.OperationSymbol") -> Optional[Any]: ...
        def constant_operations(self) -> List[Any]: ...
        def similarity_type(self) -> "alg.SimilarityType": ...
        def update_similarity_type(self) -> None: ...
        def is_similar_to(self, other: "Algebra") -> bool: ...
        def iterator(self) -> Any: ...
        def universe(self) -> List[Any]: ...
        def con(self) -> "alg.CongruenceLattice": ...
        def sub(self) -> "alg.SubalgebraLattice": ...
        def reset_con_and_sub(self) -> None: ...
        def make_operation_tables(self) -> None: ...
        def parent(self) -> Optional["alg.BasicAlgebra"]: ...
        def parents(self) -> List["alg.BasicAlgebra"]: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...
    class Polymorphisms: ...
    class Subtrace:
        """Python wrapper for Subtrace.

        A subtrace represents a pair of elements in Tame Congruence Theory (TCT) analysis.
        A subtrace holds a subtrace {a, b} and its TCT type classification.
        """
        def __init__(self, a: int, b: int, has_involution: bool) -> None: ...
        """Create a new Subtrace with given elements and involution flag.

        Args:
            a: First element of the subtrace pair
            b: Second element of the subtrace pair
            has_involution: Whether this subtrace has involution

        Returns:
            A new Subtrace instance with type set to -1
        """
        @staticmethod
        def new_with_type(a: int, b: int, has_involution: bool, type_value: int) -> "alg.Subtrace": ...
        """Create a new Subtrace with given elements, involution flag, and type.

        Args:
            a: First element of the subtrace pair
            b: Second element of the subtrace pair
            has_involution: Whether this subtrace has involution
            type_value: TCT type classification

        Returns:
            A new Subtrace instance with the specified type
        """
        def first(self) -> int: ...
        """Get the first element of the subtrace pair.

        Returns:
            The first element `a`
        """
        def second(self) -> int: ...
        """Get the second element of the subtrace pair.

        Returns:
            The second element `b`
        """
        def type_value(self) -> int: ...
        """Get the TCT type classification.

        Returns:
            The type value (-1 if not set)
        """
        def has_involution(self) -> bool: ...
        """Check if this subtrace has involution.

        Returns:
            True if the subtrace has involution, False otherwise
        """
        def set_type(self, type_value: int) -> None: ...
        """Set the TCT type classification.

        Args:
            type_value: The type to set
        """
        def get_subtrace_universe(self) -> Optional[List[List[int]]]: ...
        """Get the subtrace universe.

        Returns:
            The subtrace universe as list of pairs, or None if not set
        """
        def set_subtrace_universe(self, universe: List[List[int]]) -> None: ...
        """Set the subtrace universe.

        Args:
            universe: The subtrace universe to set

        Raises:
            ValueError: If any array doesn't have exactly 2 elements
        """
        def get_matrix_universe(self) -> Optional[List[List[int]]]: ...
        """Get the matrix universe.

        Returns:
            The matrix universe as list of 4-tuples, or None if not set
        """
        def set_matrix_universe(self, universe: List[List[int]]) -> None: ...
        """Set the matrix universe.

        Args:
            universe: The matrix universe to set

        Raises:
            ValueError: If any array doesn't have exactly 4 elements
        """
        def to_string_brief(self, brief: bool) -> str: ...
        """Get a string representation in brief format.

        Args:
            brief: If True, returns brief format [a, b], otherwise full format

        Returns:
            String representation of the subtrace
        """
        def __str__(self) -> str: ...
        """Python string representation."""
        def __repr__(self) -> str: ...
        """Python repr representation."""
        def __eq__(self, other: object) -> bool: ...
        """Python equality comparison."""
        def __hash__(self) -> int: ...
        """Python hash function."""
        def __lt__(self, other: "alg.Subtrace") -> bool: ...
        """Python comparison (less than)."""
        def __le__(self, other: "alg.Subtrace") -> bool: ...
        """Python comparison (less than or equal)."""
        def __gt__(self, other: "alg.Subtrace") -> bool: ...
        """Python comparison (greater than)."""
        def __ge__(self, other: "alg.Subtrace") -> bool: ...
        """Python comparison (greater than or equal)."""
    class TypeFinder:
        """Python wrapper for TypeFinder - utility class for finding subtraces and TCT types in algebras.

        TypeFinder is a reusable class that maintains state for efficient computation
        of subtraces and TCT (Tame Congruence Theory) types in algebras. It works with
        join irreducible congruences and implements complex algorithms for finding subtraces.
        """

        def __init__(self, small_algebra: "alg.BasicAlgebra") -> None:
            """Create a new TypeFinder with the given algebra.

            Args:
                small_algebra: The algebra to analyze
            """

        @staticmethod
        def new_with_alpha(small_algebra: "alg.BasicAlgebra", alpha: "alg.Partition") -> "alg.TypeFinder":
            """Create a new TypeFinder with the given algebra and initial alpha partition.

            Args:
                small_algebra: The algebra to analyze
                alpha: The initial alpha partition

            Returns:
                A new TypeFinder instance
            """

        def init(self) -> None:
            """Initialize the TypeFinder.

            This method sets up the internal state for subtrace finding.
            """

        def init_with_alpha(self, alpha: "alg.Partition") -> None:
            """Initialize the TypeFinder with a specific alpha partition.

            Args:
                alpha: The alpha partition to use for initialization
            """

        def find_type_set(self) -> Set[int]:
            """Find the set of all TCT types in the algebra.

            Returns:
                A set of integers representing the TCT types
            """

        def is_subtrace(self, ia: "util.IntArray", beta: "alg.Partition") -> bool:
            """Check if the given pair forms a subtrace.

            Args:
                ia: The pair to check (as IntArray)
                beta: The beta partition

            Returns:
                True if the pair is a subtrace, False otherwise
            """

        def find_subtrace(self, beta: "alg.Partition") -> "alg.Subtrace":
            """Find a subtrace for the given beta partition.

            Args:
                beta: The beta partition

            Returns:
                The found subtrace
            """

        def find_subtrace_with_alpha(self, beta: "alg.Partition", alpha: "alg.Partition") -> "alg.Subtrace":
            """Find a subtrace for the given beta and alpha partitions.

            Args:
                beta: The beta partition
                alpha: The alpha partition

            Returns:
                The found subtrace
            """

        def find_subtrace_from_pair(self, ia: "util.IntArray") -> "alg.Subtrace":
            """Find a subtrace from the given pair.

            Args:
                ia: The pair to use for finding the subtrace

            Returns:
                The found subtrace
            """

        def next_pair_for_subtrace(self) -> Optional["util.IntArray"]:
            """Get the next pair for subtrace finding.

            Returns:
                The next pair as IntArray, or None if no more pairs
            """

        def find_type(self, beta: "alg.Partition") -> int:
            """Find the TCT type for the given beta partition.

            Args:
                beta: The beta partition

            Returns:
                The TCT type as an integer
            """

        def find_type_with_alpha(self, beta: "alg.Partition", alpha: "alg.Partition") -> int:
            """Find the TCT type for the given beta and alpha partitions.

            Args:
                beta: The beta partition
                alpha: The alpha partition

            Returns:
                The TCT type as an integer
            """

        def find_type_from_subtrace(self, subtrace: "alg.Subtrace") -> int:
            """Find the TCT type for the given subtrace.

            Args:
                subtrace: The subtrace to analyze

            Returns:
                The TCT type as an integer
            """
    
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
    
    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def malcev_term(algebra: "alg.BasicAlgebra") -> Optional[str]: ...
    """Find a Malcev term for the algebra.

    Args:
        algebra: The algebra to check (BasicAlgebra)

    Returns:
        The Malcev term as a string if one exists, None otherwise
    """

    @staticmethod
    def majority_term(algebra: "alg.BasicAlgebra") -> Optional[str]: ...
    """Find a majority term for the algebra.

    Args:
        algebra: The algebra to check (BasicAlgebra)

    Returns:
        The majority term as a string if one exists, None otherwise
    """

    @staticmethod
    def minority_term(algebra: "alg.BasicAlgebra") -> Optional[str]: ...
    """Find a minority term for the algebra.

    Args:
        algebra: The algebra to check (BasicAlgebra)

    Returns:
        The minority term as a string if one exists, None otherwise
    """

    @staticmethod
    def pixley_term(algebra: "alg.BasicAlgebra") -> Optional[str]: ...
    """Find a Pixley term for the algebra.

    Args:
        algebra: The algebra to check (BasicAlgebra)

    Returns:
        The Pixley term as a string if one exists, None otherwise
    """

    @staticmethod
    def nu_term(algebra: "alg.BasicAlgebra", arity: int) -> Optional[str]: ...
    """Find a near unanimity term of the given arity.

    Args:
        algebra: The algebra to check (BasicAlgebra)
        arity: The arity of the NU term

    Returns:
        The NU term as a string if one exists, None otherwise
    """

    @staticmethod
    def nu_term_idempotent(algebra: "alg.BasicAlgebra", arity: int) -> bool: ...
    """Test if an idempotent algebra has an NU term of the given arity.

    Args:
        algebra: The idempotent algebra to check
        arity: The arity of the NU term

    Returns:
        True if the algebra has an NU term, False otherwise
    """

    @staticmethod
    def weak_nu_term(algebra: "alg.BasicAlgebra", arity: int) -> Optional[str]: ...
    """Find a weak near unanimity term of the given arity.

    Args:
        algebra: The algebra to check
        arity: The arity of the weak NU term

    Returns:
        The weak NU term if one exists, None otherwise
    """

    @staticmethod
    def weak_majority_term(algebra: "alg.BasicAlgebra") -> Optional[str]: ...
    """Find a weak majority term for the algebra.

    Args:
        algebra: The algebra to check (BasicAlgebra)

    Returns:
        The weak majority term as a string if one exists, None otherwise
    """

    @staticmethod
    def semilattice_term(algebra: "alg.BasicAlgebra") -> Optional[str]: ...
    """Find a semilattice term for the algebra.

    Args:
        algebra: The algebra to check (BasicAlgebra)

    Returns:
        The semilattice term as a string if one exists, None otherwise
    """

    @staticmethod
    def difference_term(algebra: "alg.BasicAlgebra") -> Optional[str]: ...
    """Find a difference term for the algebra.

    Args:
        algebra: The algebra to check

    Returns:
        The difference term if one exists, None otherwise
    """

    @staticmethod
    def jonsson_terms(algebra: "alg.BasicAlgebra") -> Optional[List[str]]: ...
    """Find Jonsson terms for the algebra.

    Args:
        algebra: The algebra to check (BasicAlgebra)

    Returns:
        List of Jonsson terms as strings if they exist, None otherwise
    """

    @staticmethod
    def hagemann_mitschke_terms(algebra: "alg.BasicAlgebra") -> Optional[List[str]]: ...
    """Find Hagemann-Mitschke terms for the algebra.

    Args:
        algebra: The algebra to check (BasicAlgebra)

    Returns:
        List of Hagemann-Mitschke terms as strings if they exist, None otherwise
    """

    @staticmethod
    def gumm_terms(algebra: "alg.BasicAlgebra") -> Optional[List[str]]: ...
    """Find Gumm terms for the algebra.

    Args:
        algebra: The algebra to check

    Returns:
        List of Gumm terms if they exist, None otherwise
    """

    @staticmethod
    def join_term(algebra: "alg.BasicAlgebra") -> Optional[str]: ...
    """Get a join term (Kearnes-Kiss) for the algebra.

    Args:
        algebra: The algebra to check (BasicAlgebra)

    Returns:
        The join term as a string if one exists, None otherwise
    """

    @staticmethod
    def sd_meet_terms(algebra: "alg.BasicAlgebra") -> Optional[List[str]]: ...
    """Find SD-meet terms for the algebra.

    Args:
        algebra: The algebra to check

    Returns:
        List of SD-meet terms if they exist, None otherwise
    """

    @staticmethod
    def sd_terms(algebra: "alg.BasicAlgebra") -> Optional[List[str]]: ...
    """Find SD terms for the algebra.

    Args:
        algebra: The algebra to check (BasicAlgebra)

    Returns:
        List of SD terms as strings if they exist, None otherwise
    """

    @staticmethod
    def markovic_mckenzie_siggers_taylor_term(algebra: "alg.BasicAlgebra") -> Optional[str]: ...
    """Find the Markovic-McKenzie-Siggers-Taylor term for the algebra.

    Args:
        algebra: The algebra to check (BasicAlgebra)

    Returns:
        The MMST term as a string if one exists, None otherwise
    """

    @staticmethod
    def weak_3_edge_term(algebra: "alg.BasicAlgebra") -> Optional[str]: ...
    """Find a weak 3-edge term for the algebra.

    Args:
        algebra: The algebra to check

    Returns:
        The weak 3-edge term if one exists, None otherwise
    """

    @staticmethod
    def is_congruence_dist_idempotent(algebra: "alg.BasicAlgebra") -> bool: ...
    """Test if an idempotent algebra is congruence distributive.

    Args:
        algebra: The idempotent algebra to check

    Returns:
        True if the algebra is congruence distributive, False otherwise
    """

    @staticmethod
    def is_congruence_modular_idempotent(algebra: "alg.BasicAlgebra") -> bool: ...
    """Test if an idempotent algebra is congruence modular.

    Args:
        algebra: The idempotent algebra to check

    Returns:
        True if the algebra is congruence modular, False otherwise
    """

    @staticmethod
    def congruence_modular_variety(algebra: "alg.BasicAlgebra") -> bool: ...
    """Test if the variety generated by the algebra is congruence modular.

    Args:
        algebra: The algebra to check

    Returns:
        True if the variety is congruence modular, False otherwise
    """

    @staticmethod
    def jonsson_level(algebra: "alg.BasicAlgebra") -> int: ...
    """Compute the Jonsson level of an algebra.

    Args:
        algebra: The algebra (BasicAlgebra)

    Returns:
        The Jonsson level
    """

    @staticmethod
    def local_distributivity_level(a: int, b: int, c: int, algebra: "alg.BasicAlgebra") -> int: ...
    """Compute the local distributivity level for three elements.

    Args:
        a: First element index
        b: Second element index
        c: Third element index
        algebra: The algebra

    Returns:
        The local distributivity level, or -1 if (a,c) is not in the join
    """

    @staticmethod
    def day_quadruple(a: int, b: int, c: int, d: int, algebra: "alg.BasicAlgebra") -> bool: ...
    """Check if a, b, c, d form a Day quadruple in the algebra.

    Note: This is a lower-level function that requires working with congruence lattices.
    Most users should use `find_day_quadruple_in_square` or `is_congruence_modular_idempotent` instead.

    Args:
        a, b, c, d: Four element indices
        algebra: The algebra

    Returns:
        True if a Day quadruple exists, False otherwise
    """

    @staticmethod
    def find_day_quadruple_in_square(algebra: "alg.BasicAlgebra") -> Optional[List[int]]: ...
    """Find a Day quadruple in the square of the algebra.

    Args:
        algebra: The algebra to check

    Returns:
        A tuple (x0, x1, y0, y1) if a Day quadruple is found, None otherwise
    """

    @staticmethod
    def sd_meet_idempotent(algebra: "alg.BasicAlgebra") -> Optional[List[int]]: ...
    """Find a witness for SD-meet failure in an idempotent algebra.

    Args:
        algebra: The idempotent algebra to check

    Returns:
        A tuple [x, y] if a witness is found, None otherwise
    """

    @staticmethod
    def cyclic_term_idempotent(algebra: "alg.BasicAlgebra", arity: int) -> bool: ...
    """Test if the algebra admits a cyclic term of the given arity.

    This implements an algorithm of Valeriote and Willard for testing if
    the idempotent algebra has a cyclic term of a given arity.

    Args:
        algebra: The algebra (must be idempotent)
        arity: The arity of the cyclic term (must be at least 2)

    Returns:
        True if a cyclic term exists, False otherwise
    """

    @staticmethod
    def primality_terms(algebra: "alg.BasicAlgebra") -> Optional[List[str]]: ...
    """Find primality terms for the algebra.

    This gives unary terms evaluating to the characteristic functions of the one element
    subsets of alg; a term which applied to these unit vectors gives the identity function;
    and a binary term giving a semilattice operation on {0, 1}.

    Args:
        algebra: The algebra to check (BasicAlgebra)

    Returns:
        List of primality terms as strings if they exist, None otherwise
    """

    @staticmethod
    def fixed_k_edge_term(algebra: "alg.BasicAlgebra", k: int) -> Optional[str]: ...
    """Find a k-edge term for the algebra.

    Args:
        algebra: The algebra to check (BasicAlgebra)
        k: The parameter k (edge term will have arity k+1)

    Returns:
        The k-edge term as a string if one exists, None otherwise
    """

    @staticmethod
    def fixed_k_qwnu(algebra: "alg.BasicAlgebra", arity: int) -> bool: ...
    """Test if an algebra has a quasi weak near unanimity (QWNU) term of the given arity.

    Args:
        algebra: The algebra to test (BasicAlgebra)
        arity: The arity of the QWNU term (must be at least 2)

    Returns:
        True if the algebra has a QWNU term of the given arity, False otherwise
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
        @staticmethod
        def from_string(str: str) -> "util.IntArray": ...
        def universe_size(self) -> int: ...
        def size(self) -> int: ...
        def to_array(self) -> List[int]: ...
        def as_slice(self) -> List[int]: ...
        def get(self, index: int) -> int: ...
        def set(self, index: int, value: int) -> None: ...
        def satisfies_blocks_constraint(self, blocks: List[List[int]]) -> bool: ...
        def satisfies_values_constraint(self, values: List[Tuple[int, int]]) -> bool: ...
        def satisfies_set_constraint(self, index: int, possible_values: Any) -> bool: ...
        def satisfies_congruence_constraint(self, index: int, alpha: Any, elem_index: int) -> bool: ...
        def is_idempotent(self) -> bool: ...
        def is_constant(self) -> bool: ...
        def clone_array(self) -> "util.IntArray": ...
        def to_string(self) -> str: ...
        @staticmethod
        def string_to_array(str: str) -> List[int]: ...
        @staticmethod
        def array_to_string(array: List[int]) -> str: ...
        @staticmethod
        def arrays_equal(a: List[int], b: List[int]) -> bool: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...
    class Horner:
        """Python wrapper for Horner encoding/decoding operations.

        Provides static methods for Horner encoding and decoding operations
        used in direct products of algebras.
        """

        def __init__(self) -> None: ...
        """Create a new Horner instance (static methods only)."""

        @staticmethod
        def horner(args: List[int], sizes: List[int]) -> int:
            """Returns the Horner encoding of an int array representing an element
            from a direct product of algebras with various sizes.

            Args:
                args: Array of integers representing the element coordinates
                sizes: Array of integers representing the sizes of each algebra

            Returns:
                The Horner encoding as an integer

            Raises:
                ValueError: If encoding fails due to invalid arguments
            """

        @staticmethod
        def horner_inv(k: int, sizes: List[int]) -> List[int]:
            """Returns the int array corresponding to this Horner encoding
            for a direct product of algebras with various sizes.

            Args:
                k: The Horner encoding to decode
                sizes: Array of integers representing the sizes of each algebra

            Returns:
                The decoded array of coordinates

            Raises:
                ValueError: If decoding fails due to invalid arguments
            """

        @staticmethod
        def horner_same_size(args: List[int], size: int) -> int:
            """Returns the Horner encoding of an int array representing an element
            from a direct product of algebras all with the same size.

            Args:
                args: Array of integers representing the element coordinates
                size: The common size of all algebras

            Returns:
                The Horner encoding as an integer

            Raises:
                ValueError: If encoding fails due to invalid arguments
            """

        @staticmethod
        def horner_inv_same_size(k: int, size: int, length: int) -> List[int]:
            """Returns the int array corresponding to this Horner encoding
            for a direct product of algebras with the same size.

            Args:
                k: The Horner encoding to decode
                size: The common size of all algebras
                length: The number of coordinates to decode

            Returns:
                The decoded array of coordinates

            Raises:
                ValueError: If decoding fails due to invalid arguments
            """

        @staticmethod
        def horner_integer(args: List[int], size: int) -> int:
            """Returns the Horner encoding of an int array representing an element
            from a direct product of algebras with the same size (Integer version).

            Args:
                args: Array of integers representing the element coordinates
                size: The common size of all algebras

            Returns:
                The Horner encoding as an integer

            Raises:
                ValueError: If encoding fails due to invalid arguments
            """

        @staticmethod
        def reverse_array(arr: List[int]) -> List[int]:
            """A convenience method for generating a new array with the reverse
            order of the given array.

            Args:
                arr: The array to reverse

            Returns:
                A new array with elements in reverse order
            """

        @staticmethod
        def left_right_reverse(values: List[int], alg_size: int, arity: int) -> List[int]:
            """If values are the values of a function at [0,0, ...,0], [1,0,...,0],
            this gives the values in the order [0,0, ...,0], [0,0,...,1], ... .

            Args:
                values: Array of function values
                alg_size: Size of the algebra
                arity: Arity of the function

            Returns:
                Reordered array of values

            Raises:
                ValueError: If reordering fails due to invalid arguments
            """

        def __str__(self) -> str: ...
        """String representation of the Horner instance."""

        def __repr__(self) -> str: ...
        """String representation of the Horner instance."""
    class SimpleList:
        """Python wrapper for SimpleList - an immutable linked list implementation.

        SimpleList is an immutable linked list that provides functional list operations.
        It uses a cons cell structure where each element points to the rest of the list.
        All operations return new lists rather than modifying existing ones.
        """

        def __init__(self) -> None: ...
        """Create a new empty SimpleList."""

        @staticmethod
        def make_list(obj: Any) -> "util.SimpleList": ...
        """Create a new SimpleList with a single element.

        Args:
            obj: The element to put in the list

        Returns:
            A new SimpleList containing the single element
        """

        @staticmethod
        def from_list(items: List[Any]) -> "util.SimpleList": ...
        """Create a new SimpleList from a Python list.

        Args:
            items: List of items to convert to SimpleList

        Returns:
            A new SimpleList containing all the items
        """

        def is_empty(self) -> bool: ...
        """Check if the list is empty.

        Returns:
            True if the list is empty, False otherwise
        """

        def size(self) -> int: ...
        """Get the size of the list.

        Returns:
            The number of elements in the list
        """

        def first(self) -> Any: ...
        """Get the first element of the list.

        Returns:
            The first element, or None if the list is empty

        Raises:
            ValueError: If the list is empty
        """

        def rest(self) -> "util.SimpleList": ...
        """Get the rest of the list (all elements except the first).

        Returns:
            A new SimpleList containing all elements except the first
        """

        def cons(self, obj: Any) -> "util.SimpleList": ...
        """Add an element to the front of the list.

        Args:
            obj: The element to add

        Returns:
            A new SimpleList with the element added to the front
        """

        def copy_list(self) -> "util.SimpleList": ...
        """Create a copy of this list.

        Returns:
            A new SimpleList that is a copy of this list
        """

        def append(self, other: "util.SimpleList") -> "util.SimpleList": ...
        """Append another list to the end of this list.

        Args:
            other: The list to append

        Returns:
            A new SimpleList containing elements from this list followed by elements from other
        """

        def reverse(self) -> "util.SimpleList": ...
        """Reverse the order of elements in the list.

        Returns:
            A new SimpleList with elements in reverse order
        """

        def reverse_with(self, other: "util.SimpleList") -> "util.SimpleList": ...
        """Reverse this list and append another list.

        Args:
            other: The list to append after reversing

        Returns:
            A new SimpleList with this list reversed and other appended
        """

        def get(self, index: int) -> Any: ...
        """Get the element at the specified index.

        Args:
            index: The index of the element to get

        Returns:
            The element at the specified index

        Raises:
            ValueError: If index is out of bounds
        """

        def contains(self, obj: Any) -> bool: ...
        """Check if the list contains the specified element.

        Args:
            obj: The element to search for

        Returns:
            True if the element is found, False otherwise
        """

        def index_of(self, obj: Any) -> int: ...
        """Get the index of the first occurrence of the specified element.

        Args:
            obj: The element to search for

        Returns:
            The index of the first occurrence, or -1 if not found
        """

        def last_index_of(self, obj: Any) -> int: ...
        """Get the index of the last occurrence of the specified element.

        Args:
            obj: The element to search for

        Returns:
            The index of the last occurrence, or -1 if not found
        """

        def sub_list(self, start: int, end: int) -> "util.SimpleList": ...
        """Get a sublist from start index (inclusive) to end index (exclusive).

        Args:
            start: The start index (inclusive)
            end: The end index (exclusive)

        Returns:
            A new SimpleList containing elements from start to end-1

        Raises:
            ValueError: If indices are out of bounds
        """

        def contains_all(self, other: "util.SimpleList") -> bool: ...
        """Check if this list contains all elements from another list.

        Args:
            other: The list to check against

        Returns:
            True if this list contains all elements from other, False otherwise
        """

        def to_array(self) -> List[Any]: ...
        """Convert the list to a Python list.

        Returns:
            A Python list containing all elements in order
        """

        def __str__(self) -> str: ...
        """Get a string representation of the list."""

        def __repr__(self) -> str: ...
        """Get a detailed string representation of the list."""

        def __eq__(self, other: object) -> bool: ...
        """Check equality with another object."""

        def __hash__(self) -> int: ...
        """Get the hash value of the list."""

        def __len__(self) -> int: ...
        """Get the length of the list (same as size())."""

        def __iter__(self) -> Any: ...
        """Get an iterator over the list elements."""
    class ArrayString:
        @staticmethod
        def to_string_int(array: List[int]) -> str: ...
        @staticmethod
        def to_string_str(array: List[str]) -> str: ...
        @staticmethod
        def to_string_2d_int(array: List[List[int]]) -> str: ...
        @staticmethod
        def to_string_2d_str(array: List[List[str]]) -> str: ...
        @staticmethod
        def value_of(value: Any) -> str: ...
    class PermutationGenerator:
        def __init__(self, n: int) -> None: ...
        def has_next(self) -> bool: ...
        def __iter__(self) -> "util.PermutationGenerator": ...
        def __next__(self) -> List[int]: ...
        def reset(self) -> None: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
    class ArrayIncrementorImpl:
        """Python wrapper for ArrayIncrementorImpl."""
        def __init__(self, arr: List[int]) -> None: ...
        def increment(self) -> bool: ...
        def get_array(self) -> List[int]: ...
        def reset(self) -> None: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...

    class SimpleArrayIncrementor:
        """Python wrapper for SimpleArrayIncrementor."""
        def __init__(self, arr: List[int]) -> None: ...
        @staticmethod
        def new_with_max_values(arr: List[int], max_values: List[int]) -> "util.SimpleArrayIncrementor": ...
        def increment(self) -> bool: ...
        def get_array(self) -> List[int]: ...
        def get_max_values(self) -> List[int]: ...
        def reset(self) -> None: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def __eq__(self, other: object) -> bool: ...
        def __hash__(self) -> int: ...
    class IntTuples:
        """Python wrapper for IntTuples - generates all tuples of integers."""
        @staticmethod
        def int_tuples(arity: int, size: int) -> "util.IntTuples": ...
        def get(self, k: int) -> List[int]: ...
        def size(self) -> int: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...

    class IntTuplesWithMin:
        """Python wrapper for IntTuplesWithMin - generates tuples with minimum constraints."""
        @staticmethod
        def int_tuples_with_min(arity: int, size: int, min_val: int) -> "util.IntTuplesWithMin": ...
        def get(self, k: int) -> List[int]: ...
        def size(self) -> int: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...

    class TupleWithMin:
        """Python wrapper for TupleWithMin - implements LongList<Vec<i32>> for tuple generation with minimum constraints."""
        @staticmethod
        def new(array_len: int, base: int, min_val: int) -> "util.TupleWithMin": ...
        def get(self, k: int) -> List[int]: ...
        def size(self) -> int: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...

    class FixedSizedSubsets:
        """Python wrapper for FixedSizedSubsets - generates subsets of fixed size."""
        @staticmethod
        def fixed_sized_subsets(n: int, k: int) -> "util.FixedSizedSubsets": ...
        def get(self, k: int) -> List[int]: ...
        def size(self) -> int: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...

    class Subsets:
        """Python wrapper for Subsets - generates all subsets."""
        @staticmethod
        def subsets(n: int) -> "util.Subsets": ...
        def get(self, k: int) -> List[int]: ...
        def size(self) -> int: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...

    class Permutations:
        """Python wrapper for Permutations - generates all permutations."""
        @staticmethod
        def permutations(n: int) -> "util.Permutations": ...
        def get(self, k: int) -> List[int]: ...
        def size(self) -> int: ...
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...

    class LongListUtils:
        """Utility functions for LongList operations."""
        @staticmethod
        def factorial(n: int) -> int: ...
        @staticmethod
        def binomial(n: int, k: int) -> int: ...
        @staticmethod
        def log2(n: int) -> int: ...
        @staticmethod
        def pow2(n: int) -> int: ...
    class SequenceGenerator:
        """Python wrapper for SequenceGenerator - utility class for generating sequences."""

        @staticmethod
        def nondecreasing_sequence_incrementor(arr: List[int], max: int) -> "util.NondecreasingSequenceIncrementor": ...
        @staticmethod
        def nondecreasing_sequence_incrementor_with_last_min(arr: List[int], max: int, last_min: int) -> "util.NondecreasingSequenceIncrementor": ...
        @staticmethod
        def increasing_sequence_incrementor(arr: List[int], max: int) -> "util.IncreasingSequenceIncrementor": ...
        @staticmethod
        def sequence_incrementor(arr: List[int], max: int) -> "util.SequenceIncrementor": ...
        @staticmethod
        def sequence_incrementor_with_maxs(arr: List[int], maxs: List[int]) -> "util.SequenceIncrementor": ...
        @staticmethod
        def sequence_incrementor_with_min(arr: List[int], max: int, min: int) -> "util.SequenceIncrementor": ...
        @staticmethod
        def sequence_incrementor_with_min_and_jump(arr: List[int], max: int, min: int, jump: int) -> "util.SequenceIncrementor": ...
        @staticmethod
        def left_sequence_incrementor(arr: List[int], max: int) -> "util.LeftSequenceIncrementor": ...
        @staticmethod
        def initial_partition(size: int, num_blocks: int) -> List[int]: ...
        @staticmethod
        def partition_array_incrementor(arr: List[int], num_blocks: int) -> "util.PartitionArrayIncrementor": ...

    class NondecreasingSequenceIncrementor:
        """Python wrapper for NondecreasingSequenceIncrementor."""

        def get_array(self) -> List[int]: ...
        def increment(self) -> bool: ...

    class IncreasingSequenceIncrementor:
        """Python wrapper for IncreasingSequenceIncrementor."""

        def get_array(self) -> List[int]: ...
        def increment(self) -> bool: ...

    class SequenceIncrementor:
        """Python wrapper for SequenceIncrementor."""

        def get_array(self) -> List[int]: ...
        def increment(self) -> bool: ...

    class LeftSequenceIncrementor:
        """Python wrapper for LeftSequenceIncrementor."""

        def get_array(self) -> List[int]: ...
        def increment(self) -> bool: ...

    class PartitionArrayIncrementor:
        """Python wrapper for PartitionArrayIncrementor."""

        def get_array(self) -> List[int]: ...
        def increment(self) -> bool: ...
    class VirtualLists:
        """Python wrapper for VirtualLists - utility class for creating virtual lists and array indexing.

        VirtualLists provides static utility methods for creating virtual lists of tuples
        and performing array indexing operations with minimum constraints.
        """
        @staticmethod
        def int_tuples(tuple_len: int, base: int) -> "util.IntTuples":
            """Returns a virtual list of all tuples of given length with elements from 0 to base-1.

            Args:
                tuple_len: The length of each tuple
                base: The base (maximum value + 1) for each coordinate

            Returns:
                IntTuples: A virtual list containing all possible tuples
            """
        @staticmethod
        def int_tuples_with_min(tuple_len: int, base: int, min_val: int) -> "util.IntTuplesWithMin":
            """Returns a virtual list of tuples with minimum value constraints.

            Args:
                tuple_len: The length of each tuple
                base: The base (maximum value + 1) for each coordinate
                min_val: The minimum value allowed for each coordinate

            Returns:
                IntTuplesWithMin: A virtual list containing tuples with minimum constraints
            """
        @staticmethod
        def array_indexer_with_min(k: int, arity: int, base: int, min_val: int) -> List[int]:
            """Array indexer with minimum constraint.

            Args:
                k: The index to decode
                arity: The arity (number of coordinates)
                base: The base for each coordinate
                min_val: The minimum value for each coordinate

            Returns:
                List of integers representing the decoded coordinates
            """
        @staticmethod
        def test_pow(k: int) -> str:
            """Test method for power calculations.

            Args:
                k: The value to test

            Returns:
                String representation of power calculation results
            """
        @staticmethod
        def foo(k: int, r: int) -> int:
            """Helper method for binomial calculations.

            Args:
                k: First parameter
                r: Second parameter

            Returns:
                Result of binomial calculation
            """
        @staticmethod
        def bar(k: int, r: int) -> int:
            """Helper method for binomial calculations.

            Args:
                k: First parameter
                r: Second parameter

            Returns:
                Result of binomial calculation
            """
        @staticmethod
        def baz(k: int, r: int) -> int:
            """Helper method for binomial calculations.

            Args:
                k: First parameter
                r: Second parameter

            Returns:
                Result of binomial calculation
            """
        @staticmethod
        def main(args: List[str]) -> str:
            """Test/demo method.

            Args:
                args: Command line arguments

            Returns:
                String output from the demo
            """
