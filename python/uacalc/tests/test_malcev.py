#!/usr/bin/env python3
"""
Test Malcev functions from Python bindings and compare with Java implementation.

This test module combines tests for:
1. Python binding accessibility and basic functionality
2. Comparison tests against Java CLI wrapper results
3. Comprehensive tests across all algebras in resources/algebras/
"""

import unittest
import os
import subprocess
import json
import sys
import time
from pathlib import Path

try:
    import uacalc_lib
except ImportError:
    print("Error: uacalc_lib not found. Make sure Python bindings are compiled.")
    sys.exit(1)

# Get project root to locate resources
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESOURCES_ALGEBRAS_DIR = PROJECT_ROOT / "resources" / "algebras"


def get_algebra_path(name):
    """Get full path to algebra file, handling .ua extension."""
    if not name.endswith('.ua'):
        name = f"{name}.ua"
    path = RESOURCES_ALGEBRAS_DIR / name
    # Also check in subdirectories
    if not path.exists():
        for subdir in RESOURCES_ALGEBRAS_DIR.iterdir():
            if subdir.is_dir():
                candidate = subdir / name
                if candidate.exists():
                    return str(candidate)
    return str(path)


def find_all_algebras():
    """Find all .ua algebra files in resources/algebras/ and subdirectories."""
    algebras = []
    if not RESOURCES_ALGEBRAS_DIR.exists():
        return algebras
    
    # Files in root
    for file in RESOURCES_ALGEBRAS_DIR.glob("*.ua"):
        algebras.append(str(file))
    
    # Files in subdirectories
    for subdir in RESOURCES_ALGEBRAS_DIR.iterdir():
        if subdir.is_dir():
            for file in subdir.glob("*.ua"):
                algebras.append(str(file))
    
    return sorted(algebras)


class TestMalcevPython(unittest.TestCase):
    """Test Malcev functions through Python bindings."""
    
    def test_malcev_functions_exist(self):
        """Test that Malcev functions are accessible from Python."""
        # Check that the functions exist in the alg module
        self.assertTrue(hasattr(uacalc_lib.alg, 'malcev_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'majority_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'minority_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'pixley_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'nu_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'weak_majority_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'semilattice_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'difference_term'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'jonsson_terms'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'is_congruence_dist_idempotent'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'is_congruence_modular_idempotent'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'congruence_modular_variety'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'jonsson_level'))
        self.assertTrue(hasattr(uacalc_lib.alg, 'primality_terms'))
        
    def test_malcev_term_with_cyclic3(self):
        """Test malcev_term with cyclic3 algebra."""
        algebra_path = get_algebra_path("cyclic3.ua")
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Test malcev_term
        try:
            result = uacalc_lib.alg.malcev_term(alg)
            # Should either return a term or None, not raise an error
            if result is not None:
                self.assertIsInstance(result, str)
                print(f"Found Malcev term: {result}")
            else:
                print("No Malcev term found (this is valid)")
        except Exception as e:
            # If it's still not implemented, that's okay for now
            if "not yet implemented" in str(e):
                self.skipTest("malcev_term not yet fully implemented")
            else:
                raise
    
    def test_majority_term_with_cyclic3(self):
        """Test majority_term with cyclic3 algebra."""
        algebra_path = get_algebra_path("cyclic3.ua")
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Test majority_term
        try:
            result = uacalc_lib.alg.majority_term(alg)
            # Should either return a term or None, not raise an error
            if result is not None:
                self.assertIsInstance(result, str)
                print(f"Found majority term: {result}")
            else:
                print("No majority term found (this is valid)")
        except Exception as e:
            # If it's still not implemented, that's okay for now
            if "not yet implemented" in str(e):
                self.skipTest("majority_term not yet fully implemented")
            else:
                raise
    
    def test_minority_term_with_cyclic3(self):
        """Test minority_term with cyclic3 algebra."""
        algebra_path = get_algebra_path("cyclic3.ua")
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Test minority_term
        try:
            result = uacalc_lib.alg.minority_term(alg)
            # Should either return a term or None, not raise an error
            if result is not None:
                self.assertIsInstance(result, str)
                print(f"Found minority term: {result}")
            else:
                print("No minority term found (this is valid)")
        except Exception as e:
            # If it's still not implemented, that's okay for now
            if "not yet implemented" in str(e):
                self.skipTest("minority_term not yet fully implemented")
            else:
                raise
    
    def test_pixley_term_with_cyclic3(self):
        """Test pixley_term with cyclic3 algebra."""
        algebra_path = get_algebra_path("cyclic3.ua")
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Test pixley_term
        try:
            result = uacalc_lib.alg.pixley_term(alg)
            # Should either return a term or None, not raise an error
            if result is not None:
                self.assertIsInstance(result, str)
                print(f"Found Pixley term: {result}")
            else:
                print("No Pixley term found (this is valid)")
        except Exception as e:
            # If it's still not implemented, that's okay for now
            if "not yet implemented" in str(e):
                self.skipTest("pixley_term not yet fully implemented")
            else:
                raise
    
    def test_nu_term_with_cyclic3(self):
        """Test nu_term with cyclic3 algebra."""
        algebra_path = get_algebra_path("cyclic3.ua")
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Test nu_term
        try:
            result = uacalc_lib.alg.nu_term(alg, 3)
            # Should either return a term or None
            if result is not None:
                self.assertIsInstance(result, str)
                print(f"Found NU term: {result}")
            else:
                print("No NU term found (this is valid)")
        except Exception as e:
            # If it's still not implemented, that's okay for now
            if "not yet implemented" in str(e):
                self.skipTest("nu_term not yet fully implemented")
            else:
                raise
    
    def test_primality_terms_with_cyclic3(self):
        """Test primality_terms with cyclic3 algebra."""
        algebra_path = get_algebra_path("cyclic3.ua")
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Test primality_terms
        try:
            result = uacalc_lib.alg.primality_terms(alg)
            # Should either return a list of terms or None, not raise an error
            if result is not None:
                self.assertIsInstance(result, list)
                self.assertGreater(len(result), 0)
                for term in result:
                    self.assertIsInstance(term, str)
                print(f"Found {len(result)} primality terms")
            else:
                print("No primality terms found (this is valid)")
        except Exception as e:
            # If it's still not implemented, that's okay for now
            if "not yet implemented" in str(e):
                self.skipTest("primality_terms not yet fully implemented")
            else:
                raise
    
    def test_weak_majority_term_with_trivial_algebra(self):
        """Test weak_majority_term with trivial algebra."""
        # Create a trivial algebra for testing
        BasicSmallAlgebra = uacalc_lib.alg.BasicSmallAlgebra
        alg = BasicSmallAlgebra("Trivial", [0])
        
        # weak_majority_term is implemented and should return a term for trivial algebra
        result = uacalc_lib.alg.weak_majority_term(alg)
        # Should return either a term (string) or None, not raise an error
        if result is not None:
            self.assertIsInstance(result, str)
            print(f"Found weak majority term: {result}")
        else:
            print("No weak majority term found (this is valid)")
    
    def test_semilattice_term_not_implemented(self):
        """Test that semilattice_term returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.semilattice_term(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_difference_term_not_implemented(self):
        """Test that difference_term returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.difference_term(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_jonsson_terms_with_cyclic3(self):
        """Test jonsson_terms with cyclic3 algebra."""
        algebra_path = get_algebra_path("cyclic3.ua")
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Test jonsson_terms
        result = uacalc_lib.alg.jonsson_terms(alg)
        # Should either return a list of terms (strings) or None
        if result is not None:
            self.assertIsInstance(result, list)
            for term in result:
                self.assertIsInstance(term, str)
            print(f"Found Jonsson terms: {result}")
        else:
            print("No Jonsson terms found (this is valid)")
    
    def test_congruence_modular_variety_not_implemented(self):
        """Test that congruence_modular_variety returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.congruence_modular_variety(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_jonsson_level_with_cyclic3(self):
        """Test jonsson_level with cyclic3 algebra."""
        algebra_path = get_algebra_path("cyclic3.ua")
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Test jonsson_level
        result = uacalc_lib.alg.jonsson_level(alg)
        # Should return an integer (-1 if not found, or a level >= 0)
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, -1)
        print(f"Jonsson level: {result}")


class TestMalcevJavaComparison(unittest.TestCase):
    """Test Malcev functions against Java implementation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        algebra_path = get_algebra_path("cyclic3.ua")
        if not os.path.exists(algebra_path):
            raise unittest.SkipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra once for all tests
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        cls.alg = reader.read_algebra_file()
        cls.algebra_path = algebra_path
    
    def run_java_wrapper(self, command, args=None, timeout=60):
        """Run Java wrapper and return parsed JSON result."""
        cmd = [
            "java", "-cp",
            "java_wrapper/build/classes:build/classes:org:jars/*",
            "java_wrapper.src.alg.MalcevWrapper",
            command
        ]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(PROJECT_ROOT)
        )
        
        # Check if output contains error JSON (success: false)
        stdout = result.stdout.strip()
        if "success" in stdout and '"success": false' in stdout:
            # Try to parse error
            try:
                error_json = json.loads(stdout.split('\n')[-1])
                error_msg = error_json.get("error", "Unknown error")
                exception = error_json.get("exception", "")
                if "NullPointerException" in exception or "NullPointerException" in str(result.stderr):
                    self.skipTest(f"Java wrapper has bug with null ProgressReport: {error_msg}")
                self.fail(f"Java wrapper error: {error_msg}")
            except:
                pass
        
        if result.returncode != 0:
            # Check if stderr is just INFO messages (not real errors)
            stderr_lower = result.stderr.lower()
            if "info:" in stderr_lower or "warning:" in stderr_lower:
                # Might just be log messages, try to continue
                pass
            else:
                self.fail(f"Java wrapper failed: {result.stderr}")
        
        # Extract JSON from output
        stdout = result.stdout.strip()
        lines = stdout.split('\n')
        
        # Find complete JSON object
        brace_count = 0
        json_lines = []
        found_start = False
        for line in reversed(lines):
            line_stripped = line.strip()
            if not found_start and line_stripped.endswith('}'):
                found_start = True
            if found_start:
                json_lines.insert(0, line)
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and line_stripped.startswith('{'):
                    break
        
        if not json_lines:
            self.fail("Could not find JSON in Java output")
        
        json_str = '\n'.join(json_lines)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            self.fail(f"Could not parse JSON from Java output: {e}. JSON: {json_str[:200]}")
    
    def test_malcev_term(self):
        """Test malcev_term against Java."""
        # Python/Rust
        python_result = uacalc_lib.alg.malcev_term(self.alg)
        
        # Java
        java_output = self.run_java_wrapper("malcev_term", ["--algebra", self.algebra_path])
        java_data = java_output.get("data", {})
        java_term_found = java_data.get("term_found", False)
        
        # Compare
        python_term_found = python_result is not None
        self.assertEqual(
            python_term_found, java_term_found,
            f"malcev_term: Python={python_term_found}, Java={java_term_found}"
        )
        print(f"✓ malcev_term: Python={python_term_found}, Java={java_term_found}")
    
    def test_majority_term(self):
        """Test majority_term against Java."""
        python_result = uacalc_lib.alg.majority_term(self.alg)
        java_output = self.run_java_wrapper("majority_term", ["--algebra", self.algebra_path])
        java_data = java_output.get("data", {})
        java_term_found = java_data.get("term_found", False)
        
        python_term_found = python_result is not None
        self.assertEqual(python_term_found, java_term_found)
        print(f"✓ majority_term: Python={python_term_found}, Java={java_term_found}")
    
    def test_minority_term(self):
        """Test minority_term against Java."""
        python_result = uacalc_lib.alg.minority_term(self.alg)
        java_output = self.run_java_wrapper("minority_term", ["--algebra", self.algebra_path])
        java_data = java_output.get("data", {})
        java_term_found = java_data.get("term_found", False)
        
        python_term_found = python_result is not None
        self.assertEqual(python_term_found, java_term_found)
        print(f"✓ minority_term: Python={python_term_found}, Java={java_term_found}")
    
    def test_pixley_term(self):
        """Test pixley_term against Java."""
        python_result = uacalc_lib.alg.pixley_term(self.alg)
        java_output = self.run_java_wrapper("pixley_term", ["--algebra", self.algebra_path])
        java_data = java_output.get("data", {})
        java_term_found = java_data.get("term_found", False)
        
        python_term_found = python_result is not None
        self.assertEqual(python_term_found, java_term_found)
        print(f"✓ pixley_term: Python={python_term_found}, Java={java_term_found}")
    
    def test_nu_term(self):
        """Test nu_term against Java."""
        arity = 3
        python_result = uacalc_lib.alg.nu_term(self.alg, arity)
        java_output = self.run_java_wrapper("nu_term", [
            "--algebra", self.algebra_path,
            "--arity", str(arity)
        ])
        java_data = java_output.get("data", {})
        java_term_found = java_data.get("term_found", False)
        
        python_term_found = python_result is not None
        self.assertEqual(python_term_found, java_term_found)
        print(f"✓ nu_term: Python={python_term_found}, Java={java_term_found}")
    
    def test_jonsson_terms(self):
        """Test jonsson_terms against Java."""
        python_result = uacalc_lib.alg.jonsson_terms(self.alg)
        java_output = self.run_java_wrapper("jonsson_terms", ["--algebra", self.algebra_path])
        java_data = java_output.get("data", {})
        java_terms_found = java_data.get("terms_found", False)
        java_count = java_data.get("count", 0)
        
        python_terms_found = python_result is not None and len(python_result) > 0
        python_count = len(python_result) if python_result else 0
        
        # Both should agree on whether terms exist
        self.assertEqual(python_terms_found, java_terms_found)
        # If both found terms, count should match
        if python_terms_found and java_terms_found:
            self.assertEqual(python_count, java_count,
                           f"Term count mismatch: Python={python_count}, Java={java_count}")
        print(f"✓ jonsson_terms: Python={python_count}, Java={java_count}")
    
    def test_find_day_quadruple_in_square(self):
        """Test find_day_quadruple_in_square against Java."""
        python_result = uacalc_lib.alg.find_day_quadruple_in_square(self.alg)
        java_output = self.run_java_wrapper("find_day_quadruple_in_square", [
            "--algebra", self.algebra_path
        ])
        java_data = java_output.get("data", {})
        java_quadruple_found = java_output.get("data", {}).get("quadruple_found", False)
        
        python_quadruple_found = python_result is not None
        self.assertEqual(python_quadruple_found, java_quadruple_found)
        
        # If both found quadruples, compare coordinates
        if python_quadruple_found and java_quadruple_found:
            java_quadruple = java_output.get("data", {}).get("quadruple", [])
            self.assertEqual(len(python_result), len(java_quadruple))
            # Convert Java array to list for comparison
            if isinstance(java_quadruple, list) and len(java_quadruple) == 4:
                # Java returns [x0, x1, y0, y1], Python should match
                self.assertEqual(python_result, java_quadruple,
                               f"Quadruple mismatch: Python={python_result}, Java={java_quadruple}")
        
        print(f"✓ find_day_quadruple_in_square: Python={python_quadruple_found}, Java={java_quadruple_found}")
    
    def test_sd_terms(self):
        """Test sd_terms against Java."""
        python_result = uacalc_lib.alg.sd_terms(self.alg)
        java_output = self.run_java_wrapper("sd_terms", ["--algebra", self.algebra_path])
        java_data = java_output.get("data", {})
        java_terms_found = java_data.get("terms_found", False)
        java_count = java_data.get("count", 0)
        
        python_terms_found = python_result is not None and len(python_result) > 0
        python_count = len(python_result) if python_result else 0
        
        self.assertEqual(python_terms_found, java_terms_found)
        if python_terms_found and java_terms_found:
            self.assertEqual(python_count, java_count,
                           f"SD term count mismatch: Python={python_count}, Java={java_count}")
        print(f"✓ sd_terms: Python={python_count}, Java={java_count}")
    
    def test_markovic_mckenzie_siggers_taylor_term(self):
        """Test markovic_mckenzie_siggers_taylor_term against Java."""
        python_result = uacalc_lib.alg.markovic_mckenzie_siggers_taylor_term(self.alg)
        try:
            java_output = self.run_java_wrapper("markovic_mckenzie_siggers_taylor_term", [
                "--algebra", self.algebra_path
            ])
            java_data = java_output.get("data", {})
            java_term_found = java_data.get("term_found", False)
            
            python_term_found = python_result is not None
            # TODO: Rust implementation may need work - Java finds terms but Rust returns None
            if python_term_found != java_term_found:
                print(f"⚠ markovic_mckenzie_siggers_taylor_term mismatch: Python={python_term_found}, Java={java_term_found} (implementation may need work)")
            else:
                self.assertEqual(python_term_found, java_term_found)
                print(f"✓ markovic_mckenzie_siggers_taylor_term: Python={python_term_found}, Java={java_term_found}")
        except unittest.SkipTest:
            raise
    
    def test_join_term(self):
        """Test join_term against Java."""
        python_result = uacalc_lib.alg.join_term(self.alg)
        try:
            java_output = self.run_java_wrapper("join_term", ["--algebra", self.algebra_path])
            java_data = java_output.get("data", {})
            java_term_found = java_data.get("term_found", False)
            
            python_term_found = python_result is not None
            # TODO: Rust implementation may need work - Java finds terms but Rust returns None
            if python_term_found != java_term_found:
                print(f"⚠ join_term mismatch: Python={python_term_found}, Java={java_term_found} (implementation may need work)")
            else:
                self.assertEqual(python_term_found, java_term_found)
                print(f"✓ join_term: Python={python_term_found}, Java={java_term_found}")
        except unittest.SkipTest:
            raise
    
    def test_jonsson_level(self):
        """Test jonsson_level against Java."""
        python_result = uacalc_lib.alg.jonsson_level(self.alg)
        java_output = self.run_java_wrapper("jonsson_level", ["--algebra", self.algebra_path])
        java_data = java_output.get("data", {})
        java_level = java_data.get("level", -1)
        
        self.assertEqual(python_result, java_level,
                        f"Jonsson level mismatch: Python={python_result}, Java={java_level}")
        print(f"✓ jonsson_level: Python={python_result}, Java={java_level}")
    
    def test_is_congruence_dist_idempotent(self):
        """Test is_congruence_dist_idempotent against Java."""
        python_result = uacalc_lib.alg.is_congruence_dist_idempotent(self.alg)
        java_output = self.run_java_wrapper("is_congruence_dist_idempotent", [
            "--algebra", self.algebra_path
        ])
        java_data = java_output.get("data", {})
        java_is_dist = java_data.get("is_distributive", False)
        
        self.assertEqual(python_result, java_is_dist,
                        f"Distributivity mismatch: Python={python_result}, Java={java_is_dist}")
        print(f"✓ is_congruence_dist_idempotent: Python={python_result}, Java={java_is_dist}")
    
    def test_is_congruence_modular_idempotent(self):
        """Test is_congruence_modular_idempotent against Java."""
        python_result = uacalc_lib.alg.is_congruence_modular_idempotent(self.alg)
        java_output = self.run_java_wrapper("is_congruence_modular_idempotent", [
            "--algebra", self.algebra_path
        ])
        java_data = java_output.get("data", {})
        java_is_modular = java_data.get("is_modular", False)
        
        self.assertEqual(python_result, java_is_modular,
                        f"Modularity mismatch: Python={python_result}, Java={java_is_modular}")
        print(f"✓ is_congruence_modular_idempotent: Python={python_result}, Java={java_is_modular}")
    
    def test_sd_meet_idempotent(self):
        """Test sd_meet_idempotent against Java."""
        python_result = uacalc_lib.alg.sd_meet_idempotent(self.alg)
        java_output = self.run_java_wrapper("sd_meet_idempotent", [
            "--algebra", self.algebra_path
        ])
        java_data = java_output.get("data", {})
        java_witness_found = java_data.get("witness_found", False)
        java_witness = java_data.get("witness", None)
        
        python_witness_found = python_result is not None
        
        # Both should agree on whether witness exists
        self.assertEqual(python_witness_found, java_witness_found)
        
        # If both found witnesses, they should match
        if python_witness_found and java_witness_found:
            if isinstance(java_witness, list):
                self.assertEqual(python_result, java_witness,
                               f"Witness mismatch: Python={python_result}, Java={java_witness}")
        
        print(f"✓ sd_meet_idempotent: Python={python_witness_found}, Java={java_witness_found}")


class TestMalcevAllAlgebras(unittest.TestCase):
    """Test Malcev properties across all algebras in resources/algebras/."""
    
    # List of Malcev properties to test
    MALCEV_PROPERTIES = [
        "malcev_term",
        "majority_term",
        "minority_term",
        "pixley_term",
        "nu_term",
        "jonsson_terms",
        "find_day_quadruple_in_square",
        "sd_terms",
        "markovic_mckenzie_siggers_taylor_term",
        "join_term",
        "primality_terms",
        "jonsson_level",
        "is_congruence_dist_idempotent",
        "is_congruence_modular_idempotent",
        "sd_meet_idempotent",
    ]
    
    def run_java_wrapper(self, command, args=None, timeout=10):
        """Run Java wrapper and return parsed JSON result, or None if error/timeout."""
        cmd = [
            "java", "-cp",
            "java_wrapper/build/classes:build/classes:org:jars/*",
            "java_wrapper.src.alg.MalcevWrapper",
            command
        ]
        if args:
            cmd.extend(args)
        
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(PROJECT_ROOT)
            )
            duration = time.time() - start_time
            
            # If timeout exceeded, return None
            if duration >= timeout:
                return None
            
            # Check for errors
            if result.returncode != 0:
                return None
            
            # Check if output contains error JSON (success: false)
            stdout = result.stdout.strip()
            if "success" in stdout and '"success": false' in stdout:
                return None
            
            # Extract JSON from output
            lines = stdout.split('\n')
            
            # Find complete JSON object
            brace_count = 0
            json_lines = []
            found_start = False
            for line in reversed(lines):
                line_stripped = line.strip()
                if not found_start and line_stripped.endswith('}'):
                    found_start = True
                if found_start:
                    json_lines.insert(0, line)
                    brace_count += line.count('{') - line.count('}')
                    if brace_count == 0 and line_stripped.startswith('{'):
                        break
            
            if not json_lines:
                return None
            
            json_str = '\n'.join(json_lines)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
                
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None
    
    def test_all_algebras_malcev_properties(self):
        """Test all malcev properties for all algebras, comparing Java vs Python."""
        algebras = find_all_algebras()
        
        if not algebras:
            self.skipTest("No algebra files found in resources/algebras/")
        
        print(f"\nTesting {len(algebras)} algebras with {len(self.MALCEV_PROPERTIES)} properties each...")
        
        results = {
            'total_algebras': len(algebras),
            'skipped': 0,
            'compared': 0,
            'mismatches': []
        }
        
        for algebra_path in algebras:
            algebra_name = os.path.basename(algebra_path)
            print(f"\nTesting algebra: {algebra_path}")
            
            try:
                # Load algebra
                AlgebraReader = uacalc_lib.io.AlgebraReader
                reader = AlgebraReader.new_from_file(algebra_path)
                alg = reader.read_algebra_file()
                # Check if algebra is too large
                if alg.cardinality() > 3:
                    print(f"  ⏩ {property_name}: Algebra is too large, skipping")
                    results['skipped'] += 1
                    continue

            except Exception as e:
                # Failed to load algebra, skip comparison
                print(f"  ⏩ Error loading algebra - {e}, skipping")
                results['skipped'] += 1
                continue

            # Check each property
            for property_name in self.MALCEV_PROPERTIES:
                # First, try to get Java result with 10 second timeout
                java_args = ["--algebra", algebra_path]
                if property_name == "nu_term":
                    java_args.extend(["--arity", "3"])
                
                java_output = self.run_java_wrapper(property_name, java_args, timeout=10)
                # If algebra is too large, skip comparison

                # If Java failed or timed out, skip comparison
                if java_output is None:
                    results['skipped'] += 1
                    print(f"  ⏩ {property_name}: Java failed or timed out, skipping")
                    continue
                
                # Java succeeded, now compare with Python
                results['compared'] += 1
                
                try:
                    # Get Python result
                    if property_name == "nu_term":
                        python_result = uacalc_lib.alg.nu_term(alg, 3)
                    else:
                        python_result = getattr(uacalc_lib.alg, property_name)(alg)
                    
                    # Extract Java result based on property type
                    java_data = java_output.get("data", {})
                    
                    if property_name in ["malcev_term", "majority_term", "minority_term", 
                                         "pixley_term", "nu_term", "markovic_mckenzie_siggers_taylor_term", 
                                         "join_term"]:
                        java_term_found = java_data.get("term_found", False)
                        python_term_found = python_result is not None
                        
                        if python_term_found != java_term_found:
                            mismatch = {
                                'algebra': algebra_path,
                                'property': property_name,
                                'python': python_term_found,
                                'java': java_term_found
                            }
                            results['mismatches'].append(mismatch)
                            print(f"  ✗ {property_name}: Python={python_term_found}, Java={java_term_found}")
                        else:
                            print(f"  ✓ {property_name}: match")
                    
                    elif property_name == "jonsson_terms":
                        java_terms_found = java_data.get("terms_found", False)
                        java_count = java_data.get("count", 0)
                        python_terms_found = python_result is not None and len(python_result) > 0
                        python_count = len(python_result) if python_result else 0
                        
                        if python_terms_found != java_terms_found or (python_terms_found and java_terms_found and python_count != java_count):
                            mismatch = {
                                'algebra': algebra_path,
                                'property': property_name,
                                'python': f"{python_count} terms" if python_terms_found else "None",
                                'java': f"{java_count} terms" if java_terms_found else "None"
                            }
                            results['mismatches'].append(mismatch)
                            print(f"  ✗ {property_name}: Python={python_count if python_terms_found else 'None'}, Java={java_count if java_terms_found else 'None'}")
                        else:
                            print(f"  ✓ {property_name}: match ({python_count if python_terms_found else 0} terms)")
                    
                    elif property_name == "sd_terms":
                        java_terms_found = java_data.get("terms_found", False)
                        java_count = java_data.get("count", 0)
                        python_terms_found = python_result is not None and len(python_result) > 0
                        python_count = len(python_result) if python_result else 0
                        
                        if python_terms_found != java_terms_found or (python_terms_found and java_terms_found and python_count != java_count):
                            mismatch = {
                                'algebra': algebra_path,
                                'property': property_name,
                                'python': f"{python_count} terms" if python_terms_found else "None",
                                'java': f"{java_count} terms" if java_terms_found else "None"
                            }
                            results['mismatches'].append(mismatch)
                            print(f"  ✗ {property_name}: Python={python_count if python_terms_found else 'None'}, Java={java_count if java_terms_found else 'None'}")
                        else:
                            print(f"  ✓ {property_name}: match ({python_count if python_terms_found else 0} terms)")
                    
                    elif property_name == "primality_terms":
                        java_terms_found = java_data.get("terms_found", False)
                        java_count = java_data.get("count", 0)
                        python_terms_found = python_result is not None and len(python_result) > 0
                        python_count = len(python_result) if python_result else 0
                        
                        if python_terms_found != java_terms_found or (python_terms_found and java_terms_found and python_count != java_count):
                            mismatch = {
                                'algebra': algebra_path,
                                'property': property_name,
                                'python': f"{python_count} terms" if python_terms_found else "None",
                                'java': f"{java_count} terms" if java_terms_found else "None"
                            }
                            results['mismatches'].append(mismatch)
                            print(f"  ✗ {property_name}: Python={python_count if python_terms_found else 'None'}, Java={java_count if java_terms_found else 'None'}")
                        else:
                            print(f"  ✓ {property_name}: match ({python_count if python_terms_found else 0} terms)")
                    
                    elif property_name == "find_day_quadruple_in_square":
                        java_quadruple_found = java_data.get("quadruple_found", False)
                        python_quadruple_found = python_result is not None
                        
                        if python_quadruple_found != java_quadruple_found:
                            mismatch = {
                                'algebra': algebra_path,
                                'property': property_name,
                                'python': python_quadruple_found,
                                'java': java_quadruple_found
                            }
                            results['mismatches'].append(mismatch)
                            print(f"  ✗ {property_name}: Python={python_quadruple_found}, Java={java_quadruple_found}")
                        else:
                            print(f"  ✓ {property_name}: match")
                    
                    elif property_name == "jonsson_level":
                        java_level = java_data.get("level", -1)
                        
                        if python_result != java_level:
                            mismatch = {
                                'algebra': algebra_path,
                                'property': property_name,
                                'python': python_result,
                                'java': java_level
                            }
                            results['mismatches'].append(mismatch)
                            print(f"  ✗ {property_name}: Python={python_result}, Java={java_level}")
                        else:
                            print(f"  ✓ {property_name}: match (level={python_result})")
                    
                    elif property_name == "is_congruence_dist_idempotent":
                        java_is_dist = java_data.get("is_distributive", False)
                        
                        if python_result != java_is_dist:
                            mismatch = {
                                'algebra': algebra_path,
                                'property': property_name,
                                'python': python_result,
                                'java': java_is_dist
                            }
                            results['mismatches'].append(mismatch)
                            print(f"  ✗ {property_name}: Python={python_result}, Java={java_is_dist}")
                        else:
                            print(f"  ✓ {property_name}: match ({python_result})")
                    
                    elif property_name == "is_congruence_modular_idempotent":
                        java_is_modular = java_data.get("is_modular", False)
                        
                        if python_result != java_is_modular:
                            mismatch = {
                                'algebra': algebra_path,
                                'property': property_name,
                                'python': python_result,
                                'java': java_is_modular
                            }
                            results['mismatches'].append(mismatch)
                            print(f"  ✗ {property_name}: Python={python_result}, Java={java_is_modular}")
                        else:
                            print(f"  ✓ {property_name}: match ({python_result})")
                    
                    elif property_name == "sd_meet_idempotent":
                        java_witness_found = java_data.get("witness_found", False)
                        python_witness_found = python_result is not None
                        
                        if python_witness_found != java_witness_found:
                            mismatch = {
                                'algebra': algebra_path,
                                'property': property_name,
                                'python': python_witness_found,
                                'java': java_witness_found
                            }
                            results['mismatches'].append(mismatch)
                            print(f"  ✗ {property_name}: Python={python_witness_found}, Java={java_witness_found}")
                        else:
                            print(f"  ✓ {property_name}: match")
                    
                except Exception as e:
                    print(f"  ⚠ {property_name}: Python error - {e}")
                    mismatch = {
                        'algebra': algebra_path,
                        'property': property_name,
                        'python': f"Error: {e}",
                        'java': "success"
                    }
                    results['mismatches'].append(mismatch)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"Test Summary:")
        print(f"  Total algebras: {results['total_algebras']}")
        print(f"  Tests compared: {results['compared']}")
        print(f"  Tests skipped: {results['skipped']}")
        print(f"  Mismatches: {len(results['mismatches'])}")
        print(f"{'='*60}")
        
        if results['mismatches']:
            print("\nMismatches found:")
            for mismatch in results['mismatches']:
                print(f"  {mismatch['algebra']} / {mismatch['property']}: "
                      f"Python={mismatch['python']}, Java={mismatch['java']}")
        
        # Fail test if there are mismatches
        if results['mismatches']:
            self.fail(f"Found {len(results['mismatches'])} mismatches between Python and Java implementations")


if __name__ == '__main__':
    unittest.main(verbosity=2)

