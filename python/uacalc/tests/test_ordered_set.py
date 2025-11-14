"""Test cases for OrderedSet Python bindings."""

import unittest
import uacalc_lib


class TestOrderedSet(unittest.TestCase):
    """Test OrderedSet functionality."""

    def test_create_simple_chain(self):
        """Test creating a simple 3-element chain: 0 < 1 < 2."""
        OrderedSet = uacalc_lib.lat.OrderedSet
        
        universe = [0, 1, 2]
        upper_covers = [
            [1],      # 0 is covered by 1
            [2],      # 1 is covered by 2
            [],       # 2 has no upper covers
        ]
        
        poset = OrderedSet(universe=universe, upper_covers=upper_covers, name="Chain3")
        
        self.assertEqual(poset.cardinality(), 3)
        self.assertEqual(poset.name(), "Chain3")
        self.assertEqual(poset.universe(), [0, 1, 2])

    def test_create_without_name(self):
        """Test creating OrderedSet without a name."""
        OrderedSet = uacalc_lib.lat.OrderedSet
        
        universe = [0, 1]
        upper_covers = [[1], []]
        
        poset = OrderedSet(universe=universe, upper_covers=upper_covers)
        
        self.assertIsNone(poset.name())
        self.assertEqual(poset.cardinality(), 2)

    def test_leq_chain(self):
        """Test order relation queries on a chain."""
        OrderedSet = uacalc_lib.lat.OrderedSet
        
        universe = [0, 1, 2]
        upper_covers = [[1], [2], []]
        
        poset = OrderedSet(universe=universe, upper_covers=upper_covers)
        
        # Test direct relations
        self.assertTrue(poset.leq(0, 1))   # 0 <= 1
        self.assertTrue(poset.leq(1, 2))   # 1 <= 2
        self.assertTrue(poset.leq(0, 2))   # 0 <= 2 (transitivity)
        
        # Test reverse relations
        self.assertFalse(poset.leq(1, 0))  # 1 !<= 0
        self.assertFalse(poset.leq(2, 0))  # 2 !<= 0
        self.assertFalse(poset.leq(2, 1))  # 2 !<= 1
        
        # Test reflexivity
        self.assertTrue(poset.leq(0, 0))   # 0 <= 0
        self.assertTrue(poset.leq(1, 1))   # 1 <= 1
        self.assertTrue(poset.leq(2, 2))   # 2 <= 2

    def test_get_upper_covers(self):
        """Test getting upper covers."""
        OrderedSet = uacalc_lib.lat.OrderedSet
        
        universe = [0, 1, 2]
        upper_covers = [[1], [2], []]
        
        poset = OrderedSet(universe=universe, upper_covers=upper_covers)
        
        self.assertEqual(poset.get_upper_covers(0), [1])
        self.assertEqual(poset.get_upper_covers(1), [2])
        self.assertEqual(poset.get_upper_covers(2), [])

    def test_get_lower_covers(self):
        """Test getting lower covers."""
        OrderedSet = uacalc_lib.lat.OrderedSet
        
        universe = [0, 1, 2]
        upper_covers = [[1], [2], []]
        
        poset = OrderedSet(universe=universe, upper_covers=upper_covers)
        
        self.assertEqual(poset.get_lower_covers(0), [])
        self.assertEqual(poset.get_lower_covers(1), [0])
        self.assertEqual(poset.get_lower_covers(2), [1])

    def test_diamond_poset(self):
        """Test a diamond poset: 0 < 1,2 < 3."""
        OrderedSet = uacalc_lib.lat.OrderedSet
        
        universe = [0, 1, 2, 3]
        upper_covers = [
            [1, 2],   # 0 is covered by both 1 and 2
            [3],      # 1 is covered by 3
            [3],      # 2 is covered by 3
            [],       # 3 has no upper covers
        ]
        
        poset = OrderedSet(universe=universe, upper_covers=upper_covers)
        
        self.assertEqual(poset.cardinality(), 4)
        self.assertEqual(sorted(poset.get_upper_covers(0)), [1, 2])
        self.assertEqual(poset.get_upper_covers(1), [3])
        self.assertEqual(poset.get_upper_covers(2), [3])
        self.assertEqual(poset.get_upper_covers(3), [])
        
        # Test order relations
        self.assertTrue(poset.leq(0, 1))
        self.assertTrue(poset.leq(0, 2))
        self.assertTrue(poset.leq(1, 3))
        self.assertTrue(poset.leq(2, 3))
        self.assertTrue(poset.leq(0, 3))  # Transitivity
        
        # Test incomparable elements
        self.assertFalse(poset.leq(1, 2))
        self.assertFalse(poset.leq(2, 1))

    def test_invalid_element(self):
        """Test error handling for invalid elements."""
        OrderedSet = uacalc_lib.lat.OrderedSet
        
        universe = [0, 1, 2]
        upper_covers = [[1], [2], []]
        
        poset = OrderedSet(universe=universe, upper_covers=upper_covers)
        
        # Test leq with invalid element
        with self.assertRaises(ValueError):
            poset.leq(0, 99)
        
        with self.assertRaises(ValueError):
            poset.leq(99, 0)
        
        # Test get_upper_covers with invalid element
        with self.assertRaises(ValueError):
            poset.get_upper_covers(99)
        
        # Test get_lower_covers with invalid element
        with self.assertRaises(ValueError):
            poset.get_lower_covers(99)

    def test_to_graph_data(self):
        """Test converting to graph data."""
        OrderedSet = uacalc_lib.lat.OrderedSet
        
        universe = [0, 1, 2]
        upper_covers = [[1], [2], []]
        
        poset = OrderedSet(universe=universe, upper_covers=upper_covers)
        graph_data = poset.to_graph_data()
        
        self.assertIsNotNone(graph_data)
        self.assertEqual(len(graph_data.nodes()), 3)
        self.assertEqual(len(graph_data.edges()), 2)
        
        # Check nodes
        nodes = graph_data.nodes()
        node_ids = [n[0] for n in nodes]
        self.assertEqual(sorted(node_ids), [0, 1, 2])
        
        # Check edges
        edges = graph_data.edges()
        edge_pairs = [(e[0], e[1]) for e in edges]
        self.assertIn((0, 1), edge_pairs)
        self.assertIn((1, 2), edge_pairs)

    def test_to_graph_data_with_labels(self):
        """Test converting to graph data with edge labels."""
        OrderedSet = uacalc_lib.lat.OrderedSet
        
        universe = [0, 1, 2]
        upper_covers = [[1], [2], []]
        
        poset = OrderedSet(universe=universe, upper_covers=upper_covers)
        
        # Add edge labels
        edge_labels = {
            ("0", "1"): "label1",
            ("1", "2"): "label2",
        }
        
        graph_data = poset.to_graph_data(edge_labels=edge_labels)
        
        edges = graph_data.edges()
        edge_dict = {(e[0], e[1]): e[2] for e in edges}
        
        self.assertEqual(edge_dict.get((0, 1)), "label1")
        self.assertEqual(edge_dict.get((1, 2)), "label2")

    def test_to_dot(self):
        """Test converting to DOT format."""
        OrderedSet = uacalc_lib.lat.OrderedSet
        
        universe = [0, 1, 2]
        upper_covers = [[1], [2], []]
        
        poset = OrderedSet(universe=universe, upper_covers=upper_covers)
        graph_data = poset.to_graph_data()
        dot_string = graph_data.to_dot()
        
        self.assertIn("digraph", dot_string)
        self.assertIn("Lattice", dot_string)
        self.assertIn("0", dot_string)
        self.assertIn("1", dot_string)
        self.assertIn("2", dot_string)

    def test_to_mermaid(self):
        """Test converting to Mermaid format."""
        OrderedSet = uacalc_lib.lat.OrderedSet
        
        universe = [0, 1, 2]
        upper_covers = [[1], [2], []]
        
        poset = OrderedSet(universe=universe, upper_covers=upper_covers)
        graph_data = poset.to_graph_data()
        mermaid_string = graph_data.to_mermaid()
        
        self.assertIn("graph TD", mermaid_string)
        self.assertIn("0", mermaid_string)
        self.assertIn("1", mermaid_string)
        self.assertIn("2", mermaid_string)

    def test_str_repr(self):
        """Test string representations."""
        OrderedSet = uacalc_lib.lat.OrderedSet
        
        universe = [0, 1, 2]
        upper_covers = [[1], [2], []]
        
        poset = OrderedSet(universe=universe, upper_covers=upper_covers, name="TestPoset")
        
        str_repr = str(poset)
        self.assertIn("OrderedSet", str_repr)
        self.assertIn("TestPoset", str_repr)
        self.assertIn("3", str_repr)  # cardinality
        
        repr_str = repr(poset)
        self.assertIn("OrderedSet", repr_str)
        self.assertIn("TestPoset", repr_str)
        self.assertIn("[0, 1, 2]", repr_str)

    def test_invalid_creation(self):
        """Test error handling for invalid OrderedSet creation."""
        OrderedSet = uacalc_lib.lat.OrderedSet
        
        # Mismatched sizes
        universe = [0, 1, 2]
        upper_covers = [[1], [2]]  # Missing one
        
        with self.assertRaises(ValueError):
            OrderedSet(universe=universe, upper_covers=upper_covers)
        
        # Invalid upper cover element
        universe = [0, 1]
        upper_covers = [[1], [99]]  # 99 not in universe
        
        with self.assertRaises(ValueError):
            OrderedSet(universe=universe, upper_covers=upper_covers)


if __name__ == '__main__':
    unittest.main()

