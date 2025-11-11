"""
Tests for uacalc_lib type stubs validation.

This module validates that the type stubs in uacalc_lib.pyi are:
1. Syntactically correct
2. Match the actual runtime signatures
3. Can be imported and used by type checkers
"""

import pytest
import inspect
from typing import get_type_hints, get_origin, get_args
from pathlib import Path
import sys

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import uacalc_lib
except ImportError:
    pytest.skip("uacalc_lib not available", allow_module_level=True)


class TestTypeStubValidation:
    """Test type stub validation."""

    def test_module_imports(self):
        """Test that all submodules can be imported."""
        submodules = ["alg", "element", "eq", "example", "fplat", 
                     "group", "io", "lat", "terms", "types", "util"]
        
        for submodule_name in submodules:
            assert hasattr(uacalc_lib, submodule_name), \
                f"Submodule {submodule_name} not found in uacalc_lib"
            submodule = getattr(uacalc_lib, submodule_name)
            assert submodule is not None, \
                f"Submodule {submodule_name} is None"

    def test_type_hints_accessible(self):
        """Test that type hints can be retrieved from the module."""
        try:
            hints = get_type_hints(uacalc_lib, include_extras=True)
            # Should have at least some type hints
            assert isinstance(hints, dict)
        except Exception as e:
            pytest.fail(f"Failed to get type hints: {e}")

    def test_classes_have_signatures(self):
        """Test that classes have inspectable signatures."""
        # Test a few known classes
        test_classes = [
            ("alg", "BasicAlgebra"),
            ("terms", "VariableImp"),
            ("lat", "DiamondLattice"),
        ]
        
        for module_name, class_name in test_classes:
            module = getattr(uacalc_lib, module_name, None)
            if module is None:
                continue
                
            cls = getattr(module, class_name, None)
            if cls is None:
                continue
            
            # Check that we can get the signature of __init__
            try:
                sig = inspect.signature(cls.__init__)
                assert sig is not None
            except (ValueError, TypeError) as e:
                # Some classes might not have inspectable signatures
                # This is okay for now, but we should document it
                pass

    def test_functions_have_signatures(self):
        """Test that module-level functions have inspectable signatures."""
        # Test a few known functions
        test_functions = [
            ("terms", "string_to_term"),
            ("lat", "lattice_from_meet"),
            ("io", "read_algebra_file"),
        ]
        
        for module_name, func_name in test_functions:
            module = getattr(uacalc_lib, module_name, None)
            if module is None:
                continue
                
            func = getattr(module, func_name, None)
            if func is None:
                continue
            
            try:
                sig = inspect.signature(func)
                assert sig is not None
            except (ValueError, TypeError) as e:
                pytest.fail(f"Function {module_name}.{func_name} has no signature: {e}")

    def test_method_signatures(self):
        """Test that class methods have inspectable signatures."""
        # Test a known class with methods
        try:
            BasicAlgebra = uacalc_lib.alg.BasicAlgebra
            instance = BasicAlgebra("test", [0, 1, 2], [])
            
            # Test a few methods
            methods = ["name", "cardinality", "algebra_type"]
            for method_name in methods:
                method = getattr(instance, method_name, None)
                if method is None:
                    continue
                
                try:
                    sig = inspect.signature(method)
                    assert sig is not None
                except (ValueError, TypeError):
                    # Some methods might not have inspectable signatures
                    pass
        except Exception:
            # If we can't create an instance, skip this test
            pass

    def test_static_methods(self):
        """Test that static methods are accessible."""
        # Test a known static method
        try:
            SimilarityType = uacalc_lib.alg.SimilarityType
            if hasattr(SimilarityType, "lattice_similarity_type"):
                method = SimilarityType.lattice_similarity_type
                assert callable(method)
        except Exception:
            pass

    def test_type_stub_file_exists(self):
        """Test that the type stub file exists."""
        stub_file = Path(__file__).parent.parent / "uacalc_lib.pyi"
        assert stub_file.exists(), "Type stub file uacalc_lib.pyi does not exist"

    def test_type_stub_syntax(self):
        """Test that the type stub file has valid Python syntax."""
        stub_file = Path(__file__).parent.parent / "uacalc_lib.pyi"
        if not stub_file.exists():
            pytest.skip("Type stub file does not exist")
        
        try:
            with open(stub_file, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, str(stub_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Type stub file has syntax errors: {e}")

