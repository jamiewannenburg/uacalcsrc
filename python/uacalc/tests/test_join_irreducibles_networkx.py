"""
Test to verify that join_irreducibles from Rust/Python agrees with NetworkX calculation.

This test loads the idempotent_distributive_crl.model file, parses all algebras,
creates lattices from their join operations, and compares the join_irreducibles
calculated by the Rust implementation with those calculated using NetworkX's in_edges method.
"""

import unittest
import os
import sys
from pathlib import Path

# Try to import networkx
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

import uacalc_lib

# Get project root to locate resources
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESOURCES_MACE4_DIR = PROJECT_ROOT / "resources" / "mace4"
MODEL_FILE = RESOURCES_MACE4_DIR / "idempotent_distributive_crl.model"


def find_join_operation(algebra):
    """
    Find the join operation in an algebra.
    
    Looks for operations with symbol name "*" (which is typically the join operation
    in these model files).
    
    Args:
        algebra: The algebra to search
        
    Returns:
        The join operation, or None if not found
    """
    operations = algebra.operations()
    for op in operations:
        symbol = op.symbol()
        if symbol.name() == "v":
            return op
    return None


class TestJoinIrreduciblesNetworkX(unittest.TestCase):
    """Test that join_irreducibles from Rust/Python agrees with NetworkX calculation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class by loading the model file."""
        if not MODEL_FILE.exists():
            raise unittest.SkipTest(f"Model file {MODEL_FILE} not found")
        
        if not HAS_NETWORKX:
            raise unittest.SkipTest("networkx not installed")
        
        # Load all algebras from the model file
        Mace4Reader = uacalc_lib.io.Mace4Reader
        cls.algebras = list(Mace4Reader.parse_algebra_list_from_file(str(MODEL_FILE)))
        
        if not cls.algebras:
            raise unittest.SkipTest(f"Failed to parse any algebras from {MODEL_FILE}")
    

    def test_lattice_join_agreement_with_join_operation(self):
        """Test that lattice join agrees with join operation for all algebras."""
        for alg_idx, algebra in enumerate(self.algebras):
            with self.subTest(algebra_name=algebra.name(), algebra_index=alg_idx):
                join_op = find_join_operation(algebra)
                if join_op is None:
                    self.skipTest(f"No join operation found in algebra {algebra.name()}")
                
                # Create lattice from join operation
                lattice_name = f"{algebra.name()}_lattice"
                try:
                    lattice = uacalc_lib.lat.lattice_from_join_with_universe(lattice_name, algebra.get_universe(), join_op)
                except Exception as e:
                    self.fail(f"Failed to create lattice from join operation for {algebra.name()}: {e}")
                
                # Check that lattice join agrees with join operation
                # Note: lattice.join(a, b) takes element VALUES and returns a VALUE
                # join_op.int_value_at([i, j]) takes INDICES and returns an INDEX
                # We need to convert between values and indices for comparison
                univ = list(algebra.get_universe())
                for a in lattice.universe():
                    for b in lattice.universe():
                        join_ab = lattice.join(a, b)
                        # Convert values to indices
                        idx_a = univ.index(a)
                        idx_b = univ.index(b)
                        result_idx = join_op.int_value_at([idx_a, idx_b])
                        # Convert result index back to value
                        join_ab_op = univ[result_idx]
                        self.assertEqual(join_ab, join_ab_op, 
                                        f"Join of {a} and {b} does not agree with join operation: {join_ab} != {join_ab_op}\n"
                                        f"algebra = {algebra.name()}\n"
                                        f"lattice.join(a, b) = {join_ab}\n"
                                        f"join_op.int_value_at([idx_a, idx_b]) = {join_ab_op}\n"
                                        f"idx_a = {idx_a}\n"
                                        f"idx_b = {idx_b}\n"
                                        f"univ = {univ}\n")
                        
                        
    def test_join_irreducibles_agreement_all_algebras(self):
        """Test that Rust/Python join_irreducibles agrees with NetworkX calculation for all algebras."""
        for alg_idx, algebra in enumerate(self.algebras):
            with self.subTest(algebra_name=algebra.name(), algebra_index=alg_idx):
                # Find the join operation
                join_op = find_join_operation(algebra)
                if join_op is None:
                    self.skipTest(f"No join operation found in algebra {algebra.name()}")
                
                # Create lattice from join operation
                lattice_name = f"{algebra.name()}_lattice"
                try:
                    lattice = uacalc_lib.lat.lattice_from_join_with_universe(lattice_name, algebra.get_universe(), join_op)
                except Exception as e:
                    self.fail(f"Failed to create lattice from join operation for {algebra.name()}: {e}")
                
                        
                # Get join irreducibles from Rust/Python implementation
                rust_python_jis = lattice.join_irreducibles()
                
                # Convert to NetworkX graph
                nx_graph = lattice.to_networkx()
                
                # Calculate join irreducibles using NetworkX
                # An element is join irreducible iff it has exactly one lower cover
                # In the graph, in_edges(n) gives the lower covers of n
                networkx_jis_indices = [n for n in nx_graph.nodes() if len(nx_graph.in_edges(n)) == 1]
                
                # Convert NetworkX indices to values using the lattice's universe
                # The universe may be reordered, so indices don't directly correspond to values
                lattice_univ = lattice.universe()
                networkx_jis = [lattice_univ[i] for i in networkx_jis_indices]
                
                # Convert Rust/Python join irreducibles to sorted list for comparison
                rust_python_jis_sorted = sorted(rust_python_jis)
                
                # Compare the results
                self.assertEqual(
                    set(rust_python_jis_sorted),
                    set(networkx_jis),
                    f"Join irreducibles mismatch for algebra {algebra.name()}:\n"
                    f"  Rust/Python: {rust_python_jis_sorted}\n"
                    f"  NetworkX:    {sorted(networkx_jis)}\n"
                    f"  NetworkX (indices): {networkx_jis_indices}"
                )
                
                # Also check that the counts match
                self.assertEqual(
                    len(rust_python_jis_sorted),
                    len(networkx_jis),
                    f"Join irreducibles count mismatch for algebra {algebra.name()}: "
                    f"Rust/Python has {len(rust_python_jis_sorted)}, "
                    f"NetworkX has {len(networkx_jis)}"
                )

                # Check that the join of in_edges is it
                nx_graph = lattice.to_networkx()
                for node in nx_graph.nodes():
                    in_edges = list(nx_graph.in_edges(node))
                    if len(in_edges) > 1:
                        self.assertEqual(join_op.int_value_at([in_edges[0][0], in_edges[1][0]]), node,
                        f"Join of {in_edges[0][0]} and {in_edges[1][0]} should be {node} for algebra {algebra.name()}\n"
                        f"nx_graph = {nx_graph}\n")
    
    def test_join_irreducibles_non_empty(self):
        """Test that join irreducibles list is not empty for all algebras."""
        for alg_idx, algebra in enumerate(self.algebras):
            with self.subTest(algebra_name=algebra.name(), algebra_index=alg_idx):
                join_op = find_join_operation(algebra)
                if join_op is None:
                    self.skipTest(f"No join operation found in algebra {algebra.name()}")
                
                lattice_name = f"{algebra.name()}_lattice"
                try:
                    lattice = uacalc_lib.lat.lattice_from_join(lattice_name, join_op)
                except Exception as e:
                    self.skipTest(f"Failed to create lattice from join operation for {algebra.name()}: {e}")
                
                jis = lattice.join_irreducibles()
                self.assertGreater(len(jis), 0, 
                                 f"Join irreducibles list should not be empty for algebra {algebra.name()}")
    
    def test_zero_properties(self):
        """Test that zero (bottom element) is not in join irreducibles for all algebras."""
        for alg_idx, algebra in enumerate(self.algebras):
            with self.subTest(algebra_name=algebra.name(), algebra_index=alg_idx):
                join_op = find_join_operation(algebra)
                if join_op is None:
                    self.skipTest(f"No join operation found in algebra {algebra.name()}")
                
                lattice_name = f"{algebra.name()}_lattice"
                try:
                    lattice = uacalc_lib.lat.lattice_from_join(lattice_name, join_op)
                except Exception as e:
                    self.skipTest(f"Failed to create lattice from join operation for {algebra.name()}: {e}")
                
                lattice_univ = list(lattice.universe())
                univ = list(algebra.get_universe())
                zero = lattice.zero()
                # TODO this is inconsistent with the lattice join operation
                # the zero is the bottom element of the algebra not the lattice
                join_op = find_join_operation(algebra)
                for x in univ:
                    self.assertEqual(join_op.int_value_at([x, zero]), x, 
                    f"Join of {x} and {zero} should be {x}\n"
                    f"algebra = {algebra.name()}\n"
                    f"lattice_univ = {lattice_univ}\n"
                    f"univ = {univ}\n"
                    f"zero = {zero}")

                # Check that zero is not in the join irreducibles
                jis = lattice.join_irreducibles()
                self.assertNotIn(zero, jis, 
                               f"Zero (bottom element) should not be join irreducible for algebra {algebra.name()}")
                # Bottom should not have any edge going into it
                nx_graph = lattice.to_networkx()
                self.assertListEqual(list(nx_graph.in_edges(zero)), [])
                

if __name__ == '__main__':
    unittest.main()

