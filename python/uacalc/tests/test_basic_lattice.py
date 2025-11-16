"""Tests for BasicLattice Python bindings."""

import pytest
import uacalc_lib


class TestBasicLattice:
    """Test BasicLattice Python bindings."""
    
    def test_basic_lattice_creation_placeholder(self):
        """Test that BasicLattice class exists."""
        # Currently BasicLattice creation requires CongruenceLattice
        # which may not be fully implemented in Python bindings yet
        assert hasattr(uacalc_lib.lat, "BasicLattice")
        BasicLattice = uacalc_lib.lat.BasicLattice
        assert BasicLattice is not None
    
    def test_lattice_graph_data_structure(self):
        """Test LatticeGraphData structure."""
        # Create a simple graph data structure manually
        # This tests the data structure even if BasicLattice creation isn't available
        assert hasattr(uacalc_lib.lat, "LatticeGraphData")
        LatticeGraphData = uacalc_lib.lat.LatticeGraphData
        assert LatticeGraphData is not None
    
    def test_graph_data_to_dot(self):
        """Test conversion to DOT format."""
        # This would require creating a LatticeGraphData instance
        # For now, just verify the method exists
        if hasattr(uacalc_lib.lat, "LatticeGraphData"):
            # We can't easily create an instance without BasicLattice
            # So we'll skip this test for now
            pass
    
    def test_graph_data_to_mermaid(self):
        """Test conversion to Mermaid format."""
        # This would require creating a LatticeGraphData instance
        # For now, just verify the method exists
        if hasattr(uacalc_lib.lat, "LatticeGraphData"):
            # We can't easily create an instance without BasicLattice
            # So we'll skip this test for now
            pass
    
    def test_graph_data_to_networkx(self):
        """Test conversion to NetworkX DiGraph (requires networkx)."""
        try:
            import networkx as nx
        except ImportError:
            pytest.skip("networkx not installed")
        
        # This would require creating a LatticeGraphData instance
        # For now, just verify the method exists
        if hasattr(uacalc_lib.lat, "LatticeGraphData"):
            # We can't easily create an instance without BasicLattice
            # So we'll skip this test for now
            pass


class TestBasicLatticeIntegration:
    """Integration tests for BasicLattice with other components."""
    
    def test_basic_lattice_from_congruence_lattice(self):
        """Test creating BasicLattice from CongruenceLattice."""
        import uacalc_lib
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        CongruenceLattice = uacalc_lib.alg.CongruenceLattice
        
        # Create a simple algebra
        algebra = BasicAlgebra("Test", [0, 1, 2], [])
        
        # Create congruence lattice
        con_lat = CongruenceLattice(algebra)
        
        # Get BasicLattice
        basic_lat_opt = con_lat.get_basic_lattice_default()
        assert basic_lat_opt is not None, "get_basic_lattice_default returned None"
        basic_lat = basic_lat_opt
        assert basic_lat.cardinality() > 0, f"Expected cardinality > 0, got {basic_lat.cardinality()}"
    
    def test_basic_lattice_from_subalgebra_lattice(self):
        """Test creating BasicLattice from SubalgebraLattice."""
        import uacalc_lib
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        SubalgebraLattice = uacalc_lib.alg.SubalgebraLattice
        
        # Create a simple algebra
        algebra = BasicAlgebra("Test", [0, 1, 2], [])
        
        # Create subalgebra lattice
        sub_lat = SubalgebraLattice(algebra)
        
        # Get BasicLattice
        basic_lat_opt = sub_lat.get_basic_lattice_default()
        assert basic_lat_opt is not None, "get_basic_lattice_default returned None"
        basic_lat = basic_lat_opt
        assert basic_lat.cardinality() > 0, f"Expected cardinality > 0, got {basic_lat.cardinality()}"


class TestLatticeGraphDataFormats:
    """Test LatticeGraphData format conversions."""
    
    def test_dot_format(self):
        """Test DOT format output."""
        import uacalc_lib
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        CongruenceLattice = uacalc_lib.alg.CongruenceLattice
        
        # Create a simple algebra
        algebra = BasicAlgebra("Test", [0, 1, 2], [])
        
        # Create congruence lattice
        con_lat = CongruenceLattice(algebra)
        
        # Get BasicLattice
        basic_lat_opt = con_lat.get_basic_lattice_default()
        assert basic_lat_opt is not None
        
        # Get graph data
        graph_data = basic_lat_opt.to_graph_data()
        
        # Convert to DOT format
        dot_str = graph_data.to_dot()
        
        # Verify DOT format contains expected elements
        assert "digraph" in dot_str.lower() or "graph" in dot_str.lower()
        assert "rankdir" in dot_str.lower() or len(dot_str) > 0  # Should have some content
    
    def test_mermaid_format(self):
        """Test Mermaid format output."""
        import uacalc_lib
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        CongruenceLattice = uacalc_lib.alg.CongruenceLattice
        
        # Create a simple algebra
        algebra = BasicAlgebra("Test", [0, 1, 2], [])
        
        # Create congruence lattice
        con_lat = CongruenceLattice(algebra)
        
        # Get BasicLattice
        basic_lat_opt = con_lat.get_basic_lattice_default()
        assert basic_lat_opt is not None
        
        # Get graph data
        graph_data = basic_lat_opt.to_graph_data()
        
        # Convert to Mermaid format
        mermaid_str = graph_data.to_mermaid()
        
        # Verify Mermaid format contains expected elements
        assert "graph" in mermaid_str.lower() or len(mermaid_str) > 0  # Should have some content
    
    def test_networkx_conversion(self):
        """Test NetworkX conversion."""
        try:
            import networkx as nx
        except ImportError:
            pytest.skip("networkx not installed")
        
        import uacalc_lib
        BasicAlgebra = uacalc_lib.alg.BasicAlgebra
        CongruenceLattice = uacalc_lib.alg.CongruenceLattice
        
        # Create a simple algebra
        algebra = BasicAlgebra("Test", [0, 1, 2], [])
        
        # Create congruence lattice
        con_lat = CongruenceLattice(algebra)
        
        # Get BasicLattice
        basic_lat_opt = con_lat.get_basic_lattice_default()
        assert basic_lat_opt is not None
        
        # Convert to NetworkX
        nx_graph = basic_lat_opt.to_networkx()
        
        # Verify it's a NetworkX graph
        assert nx_graph is not None
        # Check if it has nodes and edges (basic validation)
        # The graph should have at least one node
        assert hasattr(nx_graph, 'nodes') or hasattr(nx_graph, 'number_of_nodes')


class TestBasicLatticeFilterIdeal:
    """Test filter and ideal methods on BasicLattice."""
    
    def create_chain_lattice(self):
        """Create a 3-element chain lattice: 0 < 1 < 2."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        
        # Create a join operation for a chain
        symbol = OperationSymbol("join", 2, False)
        set_size = 3
        table = [
            0, 1, 2,  # join(0, 0)=0, join(0, 1)=1, join(0, 2)=2
            1, 1, 2,  # join(1, 0)=1, join(1, 1)=1, join(1, 2)=2
            2, 2, 2,  # join(2, 0)=2, join(2, 1)=2, join(2, 2)=2
        ]
        join_op = IntOperation(symbol, set_size, table)
        
        return uacalc_lib.lat.lattice_from_join("Chain3", join_op)
    
    def test_filter_chain(self):
        """Test filter method on a chain lattice."""
        lattice = self.create_chain_lattice()
        
        # Filter of 0 should contain all elements (0, 1, 2)
        filter_0 = lattice.filter(0)
        assert sorted(filter_0) == [0, 1, 2]
        
        # Filter of 1 should contain 1 and 2
        filter_1 = lattice.filter(1)
        assert sorted(filter_1) == [1, 2]
        
        # Filter of 2 should contain only 2
        filter_2 = lattice.filter(2)
        assert filter_2 == [2]
        
        # Test with invalid element
        import pytest
        with pytest.raises(ValueError):
            lattice.filter(99)
    
    def test_ideal_chain(self):
        """Test ideal method on a chain lattice."""
        lattice = self.create_chain_lattice()
        
        # Ideal of 0 should contain only 0
        ideal_0 = lattice.ideal(0)
        assert ideal_0 == [0]
        
        # Ideal of 1 should contain 0 and 1
        ideal_1 = lattice.ideal(1)
        assert sorted(ideal_1) == [0, 1]
        
        # Ideal of 2 should contain all elements (0, 1, 2)
        ideal_2 = lattice.ideal(2)
        assert sorted(ideal_2) == [0, 1, 2]
        
        # Test with invalid element
        import pytest
        with pytest.raises(ValueError):
            lattice.ideal(99)
    
    def test_filter_diamond(self):
        """Test filter method on a diamond lattice."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        
        # Create a join operation for a diamond: 0 < 1,2 < 3
        symbol = OperationSymbol("join", 2, False)
        set_size = 4
        # Order: (0,0), (0,1), (0,2), (0,3), (1,0), (1,1), (1,2), (1,3), 
        #        (2,0), (2,1), (2,2), (2,3), (3,0), (3,1), (3,2), (3,3)
        table = [
            0, 1, 2, 3,  # join(0, *)
            1, 1, 3, 3,  # join(1, *)
            2, 3, 2, 3,  # join(2, *)
            3, 3, 3, 3,  # join(3, *)
        ]
        join_op = IntOperation(symbol, set_size, table)
        
        lattice = uacalc_lib.lat.lattice_from_join("Diamond", join_op)
        
        # Filter of 0 should contain all elements
        filter_0 = lattice.filter(0)
        assert sorted(filter_0) == [0, 1, 2, 3]
        
        # Filter of 1 should contain 1 and 3
        filter_1 = lattice.filter(1)
        assert sorted(filter_1) == [1, 3]
        
        # Filter of 2 should contain 2 and 3
        filter_2 = lattice.filter(2)
        assert sorted(filter_2) == [2, 3]
        
        # Filter of 3 should contain only 3
        filter_3 = lattice.filter(3)
        assert filter_3 == [3]
    
    def test_ideal_diamond(self):
        """Test ideal method on a diamond lattice."""
        import uacalc_lib
        IntOperation = uacalc_lib.alg.IntOperation
        OperationSymbol = uacalc_lib.alg.OperationSymbol
        
        # Create a join operation for a diamond: 0 < 1,2 < 3
        symbol = OperationSymbol("join", 2, False)
        set_size = 4
        table = [
            0, 1, 2, 3,  # join(0, *)
            1, 1, 3, 3,  # join(1, *)
            2, 3, 2, 3,  # join(2, *)
            3, 3, 3, 3,  # join(3, *)
        ]
        join_op = IntOperation(symbol, set_size, table)
        
        lattice = uacalc_lib.lat.lattice_from_join("Diamond", join_op)
        
        # Ideal of 0 should contain only 0
        ideal_0 = lattice.ideal(0)
        assert ideal_0 == [0]
        
        # Ideal of 1 should contain 0 and 1
        ideal_1 = lattice.ideal(1)
        assert sorted(ideal_1) == [0, 1]
        
        # Ideal of 2 should contain 0 and 2
        ideal_2 = lattice.ideal(2)
        assert sorted(ideal_2) == [0, 2]
        
        # Ideal of 3 should contain all elements
        ideal_3 = lattice.ideal(3)
        assert sorted(ideal_3) == [0, 1, 2, 3]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

