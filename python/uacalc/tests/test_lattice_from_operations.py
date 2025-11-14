"""Test cases for lattice_from_join and lattice_from_meet factory methods."""

import unittest
import uacalc_lib

# Type aliases for convenience
IntOperation = uacalc_lib.alg.IntOperation
BasicOperation = uacalc_lib.alg.BasicOperation
OperationSymbol = uacalc_lib.alg.OperationSymbol
JoinLattice = uacalc_lib.lat.JoinLattice
MeetLattice = uacalc_lib.lat.MeetLattice


class TestLatticeFromOperations(unittest.TestCase):
    """Test lattice_from_join and lattice_from_meet factory methods."""

    def create_simple_join_operation(self, op_type="IntOperation"):
        """Create a simple join operation for testing.
        
        Creates a join operation on {0, 1, 2} where:
        - join(0, 0) = 0, join(0, 1) = 1, join(0, 2) = 2
        - join(1, 0) = 1, join(1, 1) = 1, join(1, 2) = 2
        - join(2, 0) = 2, join(2, 1) = 2, join(2, 2) = 2
        This creates a 3-element chain lattice: 0 < 1 < 2
        """
        symbol = OperationSymbol("join", 2, False)
        set_size = 3
        
        # Create the operation table
        # For a binary operation on set_size=3, we need set_size^arity = 3^2 = 9 entries
        # Order: (0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2)
        table = [
            0,  # join(0, 0) = 0
            1,  # join(0, 1) = 1
            2,  # join(0, 2) = 2
            1,  # join(1, 0) = 1
            1,  # join(1, 1) = 1
            2,  # join(1, 2) = 2
            2,  # join(2, 0) = 2
            2,  # join(2, 1) = 2
            2,  # join(2, 2) = 2
        ]
        
        if op_type == "IntOperation":
            return IntOperation(symbol, set_size, table)
        else:
            return BasicOperation(symbol, set_size, table)

    def create_simple_meet_operation(self, op_type="IntOperation"):
        """Create a simple meet operation for testing.
        
        Creates a meet operation on {0, 1, 2} where:
        - meet(0, 0) = 0, meet(0, 1) = 0, meet(0, 2) = 0
        - meet(1, 0) = 0, meet(1, 1) = 1, meet(1, 2) = 1
        - meet(2, 0) = 0, meet(2, 1) = 1, meet(2, 2) = 2
        This creates a 3-element chain lattice: 0 < 1 < 2
        """
        symbol = OperationSymbol("meet", 2, False)
        set_size = 3
        
        # Create the operation table
        table = [
            0,  # meet(0, 0) = 0
            0,  # meet(0, 1) = 0
            0,  # meet(0, 2) = 0
            0,  # meet(1, 0) = 0
            1,  # meet(1, 1) = 1
            1,  # meet(1, 2) = 1
            0,  # meet(2, 0) = 0
            1,  # meet(2, 1) = 1
            2,  # meet(2, 2) = 2
        ]
        
        if op_type == "IntOperation":
            return IntOperation(symbol, set_size, table)
        else:
            return BasicOperation(symbol, set_size, table)

    def test_lattice_from_join_int_operation(self):
        """Test lattice_from_join with IntOperation."""
        join_op = self.create_simple_join_operation("IntOperation")
        lattice = uacalc_lib.lat.lattice_from_join("TestJoinLattice", join_op)
        
        self.assertIsNotNone(lattice)
        self.assertIsInstance(lattice, JoinLattice)
        self.assertEqual(lattice.name(), "TestJoinLattice")
        
        # Check universe
        universe = lattice.universe()
        self.assertIsInstance(universe, list)
        self.assertGreaterEqual(len(universe), 3)  # At least 3 elements
        
        # Verify the order relation first
        # The filter of element i contains j if join(i, j) == j
        # For our operation: join(0,0)=0, join(0,1)=1, join(0,2)=2
        # So filter of 0 should contain [0, 1, 2], meaning 0 ≤ 0, 0 ≤ 1, 0 ≤ 2
        # join(1,0)=1, join(1,1)=1, join(1,2)=2
        # So filter of 1 should contain [1, 2], meaning 1 ≤ 1, 1 ≤ 2
        # join(2,0)=2, join(2,1)=2, join(2,2)=2
        # So filter of 2 should contain [2], meaning 2 ≤ 2
        # This gives us: 0 ≤ 1 ≤ 2
        
        # Check order relations
        self.assertTrue(lattice.leq(0, 0))  # Reflexive
        self.assertTrue(lattice.leq(0, 1))  # 0 ≤ 1
        self.assertTrue(lattice.leq(0, 2))  # 0 ≤ 2
        self.assertTrue(lattice.leq(1, 1))  # Reflexive
        self.assertTrue(lattice.leq(1, 2))  # 1 ≤ 2
        self.assertTrue(lattice.leq(2, 2))  # Reflexive
        self.assertFalse(lattice.leq(1, 0))  # Not 1 ≤ 0
        self.assertFalse(lattice.leq(2, 0))  # Not 2 ≤ 0
        self.assertFalse(lattice.leq(2, 1))  # Not 2 ≤ 1
        
        # Check lattice operations
        # In a chain 0 < 1 < 2, join is the least upper bound:
        # join(0, 1) = least upper bound of {0, 1} = 1
        # join(0, 2) = least upper bound of {0, 2} = 2
        # join(1, 2) = least upper bound of {1, 2} = 2
        self.assertEqual(lattice.join(0, 1), 1)
        self.assertEqual(lattice.join(0, 2), 2)
        self.assertEqual(lattice.join(1, 2), 2)

    def test_lattice_from_join_basic_operation(self):
        """Test lattice_from_join with BasicOperation."""
        join_op = self.create_simple_join_operation("BasicOperation")
        lattice = uacalc_lib.lat.lattice_from_join("TestJoinLattice", join_op)
        
        self.assertIsNotNone(lattice)
        self.assertIsInstance(lattice, JoinLattice)
        self.assertEqual(lattice.name(), "TestJoinLattice")

    def test_lattice_from_meet_int_operation(self):
        """Test lattice_from_meet with IntOperation."""
        meet_op = self.create_simple_meet_operation("IntOperation")
        lattice = uacalc_lib.lat.lattice_from_meet("TestMeetLattice", meet_op)
        
        self.assertIsNotNone(lattice)
        self.assertIsInstance(lattice, MeetLattice)
        self.assertEqual(lattice.name(), "TestMeetLattice")
        
        # Check universe
        universe = lattice.universe()
        self.assertIsInstance(universe, list)
        self.assertGreaterEqual(len(universe), 3)  # At least 3 elements
        
        # Verify the order relation first
        # The filter of element i contains j if meet(i, j) == i
        # For our operation: meet(0,0)=0, meet(0,1)=0, meet(0,2)=0
        # So filter of 0 should contain [0, 1, 2], meaning 0 ≤ 0, 0 ≤ 1, 0 ≤ 2
        # meet(1,0)=0, meet(1,1)=1, meet(1,2)=1
        # So filter of 1 should contain [1, 2], meaning 1 ≤ 1, 1 ≤ 2
        # meet(2,0)=0, meet(2,1)=1, meet(2,2)=2
        # So filter of 2 should contain [2], meaning 2 ≤ 2
        # This gives us: 0 ≤ 1 ≤ 2
        
        # Check order relations
        self.assertTrue(lattice.leq(0, 0))  # Reflexive
        self.assertTrue(lattice.leq(0, 1))  # 0 ≤ 1
        self.assertTrue(lattice.leq(0, 2))  # 0 ≤ 2
        self.assertTrue(lattice.leq(1, 1))  # Reflexive
        self.assertTrue(lattice.leq(1, 2))  # 1 ≤ 2
        self.assertTrue(lattice.leq(2, 2))  # Reflexive
        self.assertFalse(lattice.leq(1, 0))  # Not 1 ≤ 0
        self.assertFalse(lattice.leq(2, 0))  # Not 2 ≤ 0
        self.assertFalse(lattice.leq(2, 1))  # Not 2 ≤ 1
        
        # Check lattice operations
        # In a chain 0 < 1 < 2, meet is the greatest lower bound:
        # meet(0, 1) = greatest lower bound of {0, 1} = 0
        # meet(0, 2) = greatest lower bound of {0, 2} = 0
        # meet(1, 2) = greatest lower bound of {1, 2} = 1
        self.assertEqual(lattice.meet(0, 1), 0)
        self.assertEqual(lattice.meet(0, 2), 0)
        self.assertEqual(lattice.meet(1, 2), 1)

    def test_lattice_from_meet_basic_operation(self):
        """Test lattice_from_meet with BasicOperation."""
        meet_op = self.create_simple_meet_operation("BasicOperation")
        lattice = uacalc_lib.lat.lattice_from_meet("TestMeetLattice", meet_op)
        
        self.assertIsNotNone(lattice)
        self.assertIsInstance(lattice, MeetLattice)
        self.assertEqual(lattice.name(), "TestMeetLattice")

    def test_lattice_from_join_with_universe_int_operation(self):
        """Test lattice_from_join_with_universe with IntOperation."""
        join_op = self.create_simple_join_operation("IntOperation")
        univ = [0, 1, 2]
        lattice = uacalc_lib.lat.lattice_from_join_with_universe(
            "TestJoinLattice", univ, join_op
        )
        
        self.assertIsNotNone(lattice)
        self.assertIsInstance(lattice, JoinLattice)
        self.assertEqual(lattice.name(), "TestJoinLattice")
        
        # Universe should match or be extended
        universe = lattice.universe()
        self.assertIsInstance(universe, list)
        self.assertGreaterEqual(len(universe), len(univ))

    def test_lattice_from_join_with_universe_basic_operation(self):
        """Test lattice_from_join_with_universe with BasicOperation."""
        join_op = self.create_simple_join_operation("BasicOperation")
        univ = [0, 1, 2]
        lattice = uacalc_lib.lat.lattice_from_join_with_universe(
            "TestJoinLattice", univ, join_op
        )
        
        self.assertIsNotNone(lattice)
        self.assertIsInstance(lattice, JoinLattice)

    def test_lattice_from_meet_with_universe_int_operation(self):
        """Test lattice_from_meet_with_universe with IntOperation."""
        meet_op = self.create_simple_meet_operation("IntOperation")
        univ = [0, 1, 2]
        lattice = uacalc_lib.lat.lattice_from_meet_with_universe(
            "TestMeetLattice", univ, meet_op
        )
        
        self.assertIsNotNone(lattice)
        self.assertIsInstance(lattice, MeetLattice)
        self.assertEqual(lattice.name(), "TestMeetLattice")

    def test_lattice_from_meet_with_universe_basic_operation(self):
        """Test lattice_from_meet_with_universe with BasicOperation."""
        meet_op = self.create_simple_meet_operation("BasicOperation")
        univ = [0, 1, 2]
        lattice = uacalc_lib.lat.lattice_from_meet_with_universe(
            "TestMeetLattice", univ, meet_op
        )
        
        self.assertIsNotNone(lattice)
        self.assertIsInstance(lattice, MeetLattice)

    def test_lattice_from_join_invalid_operation(self):
        """Test that lattice_from_join raises error for invalid operation type."""
        with self.assertRaises(Exception) as context:
            uacalc_lib.lat.lattice_from_join("Test", "not an operation")
        
        error_msg = str(context.exception)
        self.assertIn("IntOperation", error_msg)
        self.assertIn("BasicOperation", error_msg)

    def test_lattice_from_meet_invalid_operation(self):
        """Test that lattice_from_meet raises error for invalid operation type."""
        with self.assertRaises(Exception) as context:
            uacalc_lib.lat.lattice_from_meet("Test", "not an operation")
        
        error_msg = str(context.exception)
        self.assertIn("IntOperation", error_msg)
        self.assertIn("BasicOperation", error_msg)

    def test_lattice_properties(self):
        """Test that created lattices have expected properties."""
        join_op = self.create_simple_join_operation("IntOperation")
        join_lat = uacalc_lib.lat.lattice_from_join("JoinTest", join_op)
        
        meet_op = self.create_simple_meet_operation("IntOperation")
        meet_lat = uacalc_lib.lat.lattice_from_meet("MeetTest", meet_op)
        
        # Both should have universe, join_irreducibles, etc.
        self.assertIsNotNone(join_lat.universe())
        self.assertIsNotNone(meet_lat.universe())
        
        # Both should support join and meet operations
        univ_join = join_lat.universe()
        univ_meet = meet_lat.universe()
        
        if len(univ_join) > 0:
            first = univ_join[0]
            self.assertIsInstance(join_lat.join(first, first), int)
            self.assertIsInstance(join_lat.meet(first, first), int)
        
        if len(univ_meet) > 0:
            first = univ_meet[0]
            self.assertIsInstance(meet_lat.join(first, first), int)
            self.assertIsInstance(meet_lat.meet(first, first), int)

    def test_diagnostic_lattice_structure(self):
        """Diagnostic test to understand the actual lattice structure."""
        join_op = self.create_simple_join_operation("IntOperation")
        join_lat = uacalc_lib.lat.lattice_from_join("DiagnosticJoin", join_op)
        
        print(f"\n=== Join Lattice Diagnostic ===")
        print(f"Universe: {join_lat.universe()}")
        
        # Check all order relations
        univ = join_lat.universe()
        print(f"\nOrder relations:")
        for a in univ:
            for b in univ:
                if join_lat.leq(a, b):
                    print(f"  {a} ≤ {b}")
        
        print(f"\nJoin operations:")
        for a in univ:
            for b in univ:
                result = join_lat.join(a, b)
                print(f"  join({a}, {b}) = {result}")
        
        print(f"\nMeet operations:")
        for a in univ:
            for b in univ:
                result = join_lat.meet(a, b)
                print(f"  meet({a}, {b}) = {result}")
        
        # Verify original operation values
        print(f"\nOriginal operation values:")
        for i in range(3):
            for j in range(3):
                result = join_op.int_value_at([i, j])
                print(f"  join_op({i}, {j}) = {result}")


if __name__ == '__main__':
    unittest.main()

