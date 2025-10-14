"""
Tests for Subtrace Python bindings.

This module contains comprehensive tests for the Subtrace class,
including comparison with Java output.
"""

import pytest
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Import the test utilities
from test_utils import TestConfig


class TestSubtrace:
    """Test cases for Subtrace Python bindings."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = TestConfig()
    
    def test_create(self):
        """Test Subtrace creation."""
        import uacalc_lib
        Subtrace = uacalc_lib.alg.Subtrace
        
        # Test Python implementation
        subtrace = Subtrace(1, 2, True)
        assert subtrace.first() == 1
        assert subtrace.second() == 2
        assert subtrace.type_value() == -1
        assert subtrace.has_involution() == True
        
        # Compare with Java
        java_result = run_java_wrapper("create", ["--a", "1", "--b", "2", "--has_involution", "true"])
        assert java_result["status"] == "created"
        assert java_result["a"] == 1
        assert java_result["b"] == 2
        assert java_result["has_involution"] == True
    
    def test_create_with_type(self):
        """Test Subtrace creation with type."""
        import uacalc_lib
        Subtrace = uacalc_lib.alg.Subtrace
        
        # Test Python implementation
        subtrace = Subtrace.new_with_type(0, 3, False, 5)
        assert subtrace.first() == 0
        assert subtrace.second() == 3
        assert subtrace.type_value() == 5
        assert subtrace.has_involution() == False
        
        # Compare with Java
        java_result = run_java_wrapper("create_with_type", [
            "--a", "0", "--b", "3", "--has_involution", "false", "--type", "5"
        ])
        assert java_result["status"] == "created"
        assert java_result["a"] == 0
        assert java_result["b"] == 3
        assert java_result["type"] == 5
        assert java_result["has_involution"] == False
    
    def test_getters(self):
        """Test getter methods."""
        import uacalc_lib
        Subtrace = uacalc_lib.alg.Subtrace
        
        # Test Python implementation
        subtrace = Subtrace.new_with_type(1, 2, True, 3)
        
        assert subtrace.first() == 1
        assert subtrace.second() == 2
        assert subtrace.type_value() == 3
        assert subtrace.has_involution() == True
        
        # Test default type
        subtrace2 = Subtrace(5, 7, False)
        assert subtrace2.type_value() == -1
    
    def test_set_type(self):
        """Test setting type value."""
        import uacalc_lib
        Subtrace = uacalc_lib.alg.Subtrace
        
        # Test Python implementation
        subtrace = Subtrace(1, 2, True)
        assert subtrace.type_value() == -1
        
        subtrace.set_type(4)
        assert subtrace.type_value() == 4
    
    def test_subtrace_universe(self):
        """Test subtrace universe operations."""
        import uacalc_lib
        Subtrace = uacalc_lib.alg.Subtrace
        
        # Test Python implementation
        subtrace = Subtrace(1, 2, True)
        assert subtrace.get_subtrace_universe() is None
        
        # Set universe
        universe = [[1, 1], [1, 2], [2, 2]]
        subtrace.set_subtrace_universe(universe)
        
        retrieved = subtrace.get_subtrace_universe()
        assert retrieved is not None
        assert len(retrieved) == 3
        assert [1, 1] in retrieved
        assert [1, 2] in retrieved
        assert [2, 2] in retrieved
    
    def test_matrix_universe(self):
        """Test matrix universe operations."""
        import uacalc_lib
        Subtrace = uacalc_lib.alg.Subtrace
        
        # Test Python implementation
        subtrace = Subtrace(1, 2, True)
        assert subtrace.get_matrix_universe() is None
        
        # Set matrix universe
        universe = [[1, 1, 2, 2], [1, 2, 1, 2]]
        subtrace.set_matrix_universe(universe)
        
        retrieved = subtrace.get_matrix_universe()
        assert retrieved is not None
        assert len(retrieved) == 2
        assert [1, 1, 2, 2] in retrieved
        assert [1, 2, 1, 2] in retrieved
    
    def test_to_string_brief(self):
        """Test string representation methods."""
        import uacalc_lib
        Subtrace = uacalc_lib.alg.Subtrace
        
        # Test Python implementation
        subtrace = Subtrace.new_with_type(1, 2, True, 3)
        
        brief = subtrace.to_string_brief(True)
        full = subtrace.to_string_brief(False)
        
        assert brief == "[1, 2]"
        assert "subtrace [1, 2] typ = 3 inv: true" == full
        
        # Compare with Java using test command
        java_result = run_java_wrapper("test", [])
        assert java_result["brief_string"] == "[1, 2]"
        assert java_result["to_string"] == "subtrace [1, 2] typ = 3 inv: true"
    
    def test_string_representation(self):
        """Test string representation methods."""
        import uacalc_lib
        Subtrace = uacalc_lib.alg.Subtrace
        
        subtrace = Subtrace.new_with_type(3, 4, False, 2)
        
        str_repr = str(subtrace)
        repr_repr = repr(subtrace)
        
        assert "subtrace [3, 4] typ = 2 inv: false" == str_repr
        assert "Subtrace(3, 4, False, 2)" == repr_repr
    
    def test_equality_and_hash(self):
        """Test equality and hash methods."""
        import uacalc_lib
        Subtrace = uacalc_lib.alg.Subtrace
        
        subtrace1 = Subtrace.new_with_type(1, 2, True, 3)
        subtrace2 = Subtrace.new_with_type(1, 2, True, 3)
        subtrace3 = Subtrace.new_with_type(1, 2, False, 3)
        subtrace4 = Subtrace.new_with_type(1, 3, True, 3)
        
        assert subtrace1 == subtrace2
        assert subtrace1 != subtrace3
        assert subtrace1 != subtrace4
        
        # Test hash
        assert hash(subtrace1) == hash(subtrace2)
        assert hash(subtrace1) != hash(subtrace3)
    
    def test_ordering(self):
        """Test ordering comparison."""
        import uacalc_lib
        Subtrace = uacalc_lib.alg.Subtrace
        
        subtrace1 = Subtrace.new_with_type(1, 2, True, 3)
        subtrace2 = Subtrace.new_with_type(1, 3, True, 3)
        subtrace3 = Subtrace.new_with_type(2, 2, True, 3)
        
        assert subtrace1 < subtrace2
        assert subtrace1 < subtrace3
        assert subtrace2 < subtrace3
        
        assert subtrace2 > subtrace1
        assert subtrace3 > subtrace1
        assert subtrace3 > subtrace2
    
    def test_comprehensive_functionality(self):
        """Test comprehensive functionality matching Java test."""
        import uacalc_lib
        Subtrace = uacalc_lib.alg.Subtrace
        
        # Test Python implementation
        subtrace = Subtrace.new_with_type(1, 2, True, 3)
        
        assert subtrace.first() == 1
        assert subtrace.second() == 2
        assert subtrace.type_value() == 3
        assert subtrace.has_involution() == True
        
        # Test universe operations
        universe = [[1, 1], [1, 2], [2, 2]]
        subtrace.set_subtrace_universe(universe)
        retrieved = subtrace.get_subtrace_universe()
        assert len(retrieved) == 3
        
        # Test string operations
        brief = subtrace.to_string_brief(True)
        full = subtrace.to_string_brief(False)
        assert brief == "[1, 2]"
        assert full == "subtrace [1, 2] typ = 3 inv: true"
        
        # Compare with Java
        java_result = run_java_wrapper("test", [])
        assert java_result["first"] == 1
        assert java_result["second"] == 2
        assert java_result["type"] == 3
        assert java_result["has_involution"] == True
        assert java_result["brief_string"] == "[1, 2]"
        assert java_result["to_string"] == "subtrace [1, 2] typ = 3 inv: true"
        assert java_result["universe_size"] == 3
        assert java_result["status"] == "test_completed"
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        import uacalc_lib
        Subtrace = uacalc_lib.alg.Subtrace
        
        # Test negative values
        subtrace = Subtrace(-1, -2, True)
        assert subtrace.first() == -1
        assert subtrace.second() == -2
        
        # Test same values
        subtrace2 = Subtrace(5, 5, False)
        assert subtrace2.first() == 5
        assert subtrace2.second() == 5
        
        # Test large values
        subtrace3 = Subtrace.new_with_type(1000, 2000, True, 999)
        assert subtrace3.first() == 1000
        assert subtrace3.second() == 2000
        assert subtrace3.type_value() == 999
        
        # Test invalid universe inputs
        with pytest.raises(ValueError):
            subtrace.set_subtrace_universe([[1]])  # Too few elements
        
        with pytest.raises(ValueError):
            subtrace.set_matrix_universe([[1, 2, 3]])  # Too few elements for matrix universe


def run_java_wrapper(command: str, args: List[str]) -> Dict[str, Any]:
    """Run Java wrapper and return JSON output."""
    from test_utils import build_java_command
    
    wrapper_class = "java_wrapper.src.alg.conlat.SubtraceWrapper"
    cmd = build_java_command(wrapper_class, [command] + args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30.0
        )
        
        if result.returncode != 0:
            pytest.fail(f"Java wrapper failed: {result.stderr}")
        
        return json.loads(result.stdout)
    
    except subprocess.TimeoutExpired:
        pytest.fail("Java wrapper timed out")
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse Java wrapper output: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error running Java wrapper: {e}")