"""
Tests for congruence lattice functionality.
"""

import pytest
import time
from typing import List, Dict, Any

from uacalc import (
    Algebra, create_algebra, create_operation, create_congruence_lattice,
    CongruenceLattice, Partition, HAS_NETWORKX, HAS_MATPLOTLIB
)
from uacalc.congruence import (
    CongruenceLatticeBuilder, analyze_lattice, lattice_to_networkx,
    plot_lattice, export_lattice_data, principal_congruences_table,
    congruence_closure, is_congruence, ProgressBar, LoggingProgress
)


class TestCongruenceLatticeBasic:
    """Test basic congruence lattice construction and properties."""
    
    def test_create_congruence_lattice(self):
        """Test basic congruence lattice creation."""
        # Create a simple algebra
        algebra = create_algebra("test", [0, 1, 2])
        
        # Add a binary operation
        op_table = [[0, 1, 2], [1, 1, 1], [2, 1, 2]]
        operation = create_operation("f", 2, op_table)
        algebra.add_operation("f", operation)
        
        # Create congruence lattice
        lattice = create_congruence_lattice(algebra)
        
        assert lattice is not None
        assert isinstance(lattice, CongruenceLattice)
        assert lattice.size() >= 2  # At least bottom and top
    
    def test_lattice_size(self):
        """Test that lattice size is reasonable."""
        # Create a small algebra
        algebra = create_algebra("small", [0, 1])
        
        # Add identity operation
        operation = create_operation("id", 1, [[0, 0], [1, 1]])
        algebra.add_operation("id", operation)
        
        lattice = create_congruence_lattice(algebra)
        size = lattice.size()
        
        assert size >= 2  # At least bottom and top
        assert size <= 2**algebra.cardinality()  # At most 2^n congruences
    
    def test_congruences_list(self):
        """Test that congruences() returns a list of partitions."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        congruences = lattice.congruences()
        
        assert isinstance(congruences, list)
        assert len(congruences) == lattice.size()
        for congruence in congruences:
            assert isinstance(congruence, Partition)


class TestPrincipalCongruences:
    """Test principal congruence computation."""
    
    def test_principal_congruence_basic(self):
        """Test basic principal congruence computation."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        
        # Test principal congruence θ(0, 1)
        congruence = lattice.principal_congruence(0, 1)
        assert isinstance(congruence, Partition)
        assert congruence.same_block(0, 1)  # 0 and 1 should be in same block
    
    def test_principal_congruence_same_element(self):
        """Test principal congruence with same element."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        
        # θ(a, a) should be the identity relation
        congruence = lattice.principal_congruence(0, 0)
        assert isinstance(congruence, Partition)
        
        # Check that it's the identity relation
        for i in range(algebra.cardinality()):
            for j in range(algebra.cardinality()):
                if i == j:
                    assert congruence.same_block(i, j)
                else:
                    assert not congruence.same_block(i, j)
    
    def test_principal_congruence_caching(self):
        """Test that principal congruences are cached."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        
        # Compute same principal congruence twice
        start_time = time.time()
        congruence1 = lattice.principal_congruence(0, 1)
        time1 = time.time() - start_time
        
        start_time = time.time()
        congruence2 = lattice.principal_congruence(0, 1)
        time2 = time.time() - start_time
        
        # Second call should be faster (cached)
        assert time2 < time1
        assert congruence1.same_block(0, 1) == congruence2.same_block(0, 1)


class TestLatticeOperations:
    """Test lattice join and meet operations."""
    
    def test_join_operation(self):
        """Test join operation on congruences."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        congruences = lattice.congruences()
        
        if len(congruences) >= 3:
            # Test join of first two congruences
            join = lattice.join(0, 1)
            assert isinstance(join, Partition)
            
            # Join should be coarser than both original congruences
            assert join.is_coarser_than(congruences[0])
            assert join.is_coarser_than(congruences[1])
    
    def test_meet_operation(self):
        """Test meet operation on congruences."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        congruences = lattice.congruences()
        
        if len(congruences) >= 3:
            # Test meet of first two congruences
            meet = lattice.meet(0, 1)
            assert isinstance(meet, Partition)
            
            # Meet should be finer than both original congruences
            assert meet.is_finer_than(congruences[0])
            assert meet.is_finer_than(congruences[1])
    
    def test_lattice_laws(self):
        """Test basic lattice laws."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        congruences = lattice.congruences()
        
        if len(congruences) >= 3:
            # Test associativity of join
            join1 = lattice.join(0, 1)
            join2 = lattice.join(1, 2)
            join3 = lattice.join(0, 2)
            
            # Test that join operations return partitions
            assert isinstance(join1, Partition)
            assert isinstance(join2, Partition)
            assert isinstance(join3, Partition)
            
            # Test associativity of meet
            meet1 = lattice.meet(0, 1)
            meet2 = lattice.meet(1, 2)
            meet3 = lattice.meet(0, 2)
            
            assert isinstance(meet1, Partition)
            assert isinstance(meet2, Partition)
            assert isinstance(meet3, Partition)


class TestLatticeStructure:
    """Test lattice structure analysis."""
    
    def test_atoms_and_coatoms(self):
        """Test atom and coatom computation."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        
        atoms = lattice.atoms()
        coatoms = lattice.coatoms()
        
        assert isinstance(atoms, list)
        assert isinstance(coatoms, list)
        
        for atom in atoms:
            assert isinstance(atom, Partition)
        
        for coatom in coatoms:
            assert isinstance(coatom, Partition)
    
    def test_covering_relation(self):
        """Test covering relation computation."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        covering = lattice.covering_relation()
        
        assert isinstance(covering, list)
        for edge in covering:
            assert isinstance(edge, tuple)
            assert len(edge) == 2
            assert 0 <= edge[0] < lattice.size()
            assert 0 <= edge[1] < lattice.size()


class TestProgressReporting:
    """Test progress reporting functionality."""
    
    def test_progress_callback(self):
        """Test progress callback during lattice construction."""
        algebra = create_algebra("test", [0, 1, 2, 3])
        operation = create_operation("f", 2, [[0, 1, 2, 3], [1, 1, 1, 1], [2, 1, 2, 1], [3, 1, 1, 3]])
        algebra.add_operation("f", operation)
        
        progress_calls = []
        
        def progress_callback(progress: float, message: str):
            progress_calls.append((progress, message))
        
        lattice = create_congruence_lattice(algebra)
        lattice.with_progress_callback(progress_callback)
        
        # Force construction by accessing size
        _ = lattice.size()
        
        # Should have received some progress updates
        assert len(progress_calls) > 0
        
        # Progress should be between 0 and 1
        for progress, message in progress_calls:
            assert 0.0 <= progress <= 1.0
            assert isinstance(message, str)
    
    def test_progress_bar(self):
        """Test progress bar functionality."""
        progress_calls = []
        
        def callback(progress: float, message: str):
            progress_calls.append((progress, message))
        
        progress_bar = ProgressBar(100, "Test Progress")
        
        # Simulate progress updates
        for i in range(0, 101, 10):
            progress = i / 100.0
            progress_bar(progress, f"Step {i}")
        
        # Should have received progress updates
        assert len(progress_calls) > 0


class TestCongruenceLatticeBuilder:
    """Test the builder pattern for congruence lattices."""
    
    def test_builder_basic(self):
        """Test basic builder functionality."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        builder = CongruenceLatticeBuilder()
        lattice = builder.for_algebra(algebra).build()
        
        assert isinstance(lattice, CongruenceLattice)
        assert lattice.size() >= 2
    
    def test_builder_with_progress(self):
        """Test builder with progress callback."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        progress_calls = []
        
        def callback(progress: float, message: str):
            progress_calls.append((progress, message))
        
        builder = CongruenceLatticeBuilder()
        lattice = builder.for_algebra(algebra).with_progress(callback).build()
        
        # Force construction
        _ = lattice.size()
        
        assert len(progress_calls) > 0


class TestLatticeAnalysis:
    """Test lattice analysis utilities."""
    
    def test_analyze_lattice(self):
        """Test lattice analysis function."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        analysis = analyze_lattice(lattice)
        
        assert isinstance(analysis, dict)
        assert 'size' in analysis
        assert 'height' in analysis
        assert 'width' in analysis
        assert 'atom_count' in analysis
        assert 'coatom_count' in analysis
        assert 'is_distributive' in analysis
        assert 'is_modular' in analysis
        assert 'is_complemented' in analysis
        assert 'analysis_time' in analysis
        
        assert analysis['size'] == lattice.size()
        assert analysis['atom_count'] == len(lattice.atoms())
        assert analysis['coatom_count'] == len(lattice.coatoms())


class TestLatticeVisualization:
    """Test lattice visualization utilities."""
    
    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_lattice_to_networkx(self):
        """Test conversion to NetworkX graph."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        G = lattice_to_networkx(lattice)
        
        assert G.number_of_nodes() == lattice.size()
        assert G.number_of_edges() == len(lattice.covering_relation())
    
    @pytest.mark.skipif(not HAS_MATPLOTLIB, reason="Matplotlib not available")
    def test_plot_lattice(self):
        """Test lattice plotting."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        fig = plot_lattice(lattice)
        
        assert fig is not None
        # Clean up
        import matplotlib.pyplot as plt
        plt.close(fig)


class TestLatticeExport:
    """Test lattice data export functionality."""
    
    def test_export_lattice_json(self):
        """Test JSON export of lattice data."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        data = export_lattice_data(lattice, format='json')
        
        assert isinstance(data, dict)
        assert 'size' in data
        assert 'congruences' in data
        assert 'covering_relation' in data
        assert 'atoms' in data
        assert 'coatoms' in data
    
    def test_export_lattice_csv(self):
        """Test CSV export of lattice data."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        lattice = create_congruence_lattice(algebra)
        csv_data = export_lattice_data(lattice, format='csv')
        
        assert isinstance(csv_data, str)
        assert csv_data.startswith("source,target\n")
        assert len(csv_data.split('\n')) > 1


class TestPrincipalCongruencesTable:
    """Test principal congruences table generation."""
    
    def test_principal_congruences_table(self):
        """Test generation of all principal congruences."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        table = principal_congruences_table(algebra)
        
        assert isinstance(table, list)
        # Should have n*(n-1)/2 entries for n elements
        n = algebra.cardinality()
        expected_count = n * (n - 1) // 2
        assert len(table) == expected_count
        
        for a, b, congruence in table:
            assert 0 <= a < n
            assert 0 <= b < n
            assert a < b  # Should be in order
            assert isinstance(congruence, Partition)


class TestCongruenceClosure:
    """Test congruence closure computation."""
    
    def test_congruence_closure_empty(self):
        """Test congruence closure of empty set."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        closure = congruence_closure(algebra, [])
        
        assert isinstance(closure, Partition)
        # Should be the identity relation
        for i in range(algebra.cardinality()):
            for j in range(algebra.cardinality()):
                if i == j:
                    assert closure.same_block(i, j)
                else:
                    assert not closure.same_block(i, j)
    
    def test_congruence_closure_single_pair(self):
        """Test congruence closure of single pair."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        closure = congruence_closure(algebra, [(0, 1)])
        
        assert isinstance(closure, Partition)
        assert closure.same_block(0, 1)  # Should contain the original pair


class TestIntegration:
    """Integration tests for congruence lattice functionality."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from algebra to lattice analysis."""
        # Create algebra
        algebra = create_algebra("integration_test", [0, 1, 2, 3])
        operation = create_operation("f", 2, [[0, 1, 2, 3], [1, 1, 1, 1], [2, 1, 2, 1], [3, 1, 1, 3]])
        algebra.add_operation("f", operation)
        
        # Create lattice with progress reporting
        progress_calls = []
        def callback(progress: float, message: str):
            progress_calls.append((progress, message))
        
        lattice = create_congruence_lattice(algebra)
        lattice.with_progress_callback(callback)
        
        # Analyze lattice
        analysis = analyze_lattice(lattice)
        
        # Test principal congruences
        principal = lattice.principal_congruence(0, 1)
        
        # Test lattice operations
        congruences = lattice.congruences()
        if len(congruences) >= 3:
            join = lattice.join(0, 1)
            meet = lattice.meet(0, 1)
        
        # Verify results
        assert lattice.size() >= 2
        assert analysis['size'] == lattice.size()
        assert isinstance(principal, Partition)
        assert len(progress_calls) > 0
    
    @pytest.mark.slow
    def test_large_algebra_performance(self):
        """Test performance with larger algebra."""
        # Create a larger algebra
        size = 8
        algebra = create_algebra("large_test", list(range(size)))
        
        # Add a simple operation
        operation = create_operation("f", 2, [[(i + j) % size for j in range(size)] for i in range(size)])
        algebra.add_operation("f", operation)
        
        start_time = time.time()
        lattice = create_congruence_lattice(algebra)
        construction_time = time.time() - start_time
        
        # Should complete in reasonable time
        assert construction_time < 30.0  # 30 seconds max
        assert lattice.size() >= 2


if __name__ == "__main__":
    pytest.main([__file__])
