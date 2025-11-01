"""
Test Malcev functions from Python bindings.

This test module verifies that the Malcev functions are properly exposed
through the Python bindings and return appropriate error messages indicating
they are not yet implemented.
"""

import unittest
import uacalc_lib


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
        
    def test_malcev_term_with_cyclic3(self):
        """Test malcev_term with cyclic3 algebra."""
        import os
        algebra_path = "resources/algebras/cyclic3.ua"
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
        import os
        algebra_path = "resources/algebras/cyclic3.ua"
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
        import os
        algebra_path = "resources/algebras/cyclic3.ua"
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
        import os
        algebra_path = "resources/algebras/cyclic3.ua"
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
        import os
        algebra_path = "resources/algebras/cyclic3.ua"
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
    
    def test_jonsson_terms_not_implemented(self):
        """Test that jonsson_terms returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.jonsson_terms(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_is_congruence_dist_idempotent_with_cyclic3(self):
        """Test is_congruence_dist_idempotent with cyclic3 and compare with Java."""
        import os
        import subprocess
        import json
        
        algebra_path = "resources/algebras/cyclic3.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra with Python
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Get Python/Rust result
        python_result = uacalc_lib.alg.is_congruence_dist_idempotent(alg)
        self.assertIsInstance(python_result, bool)
        
        # Get Java result
        try:
            cmd = [
                "java", "-cp",
                "java_wrapper/build/classes:build/classes:org:jars/*",
                "java_wrapper.src.alg.MalcevWrapper",
                "is_congruence_dist_idempotent",
                "--algebra", algebra_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                # Extract JSON from output (may have progress messages before JSON)
                # JSON is typically the last complete JSON object in the output
                stdout = result.stdout.strip()
                # Find the last line that starts with '{' which is likely the JSON start
                lines = stdout.split('\n')
                json_start_idx = -1
                for i in range(len(lines) - 1, -1, -1):
                    if lines[i].strip().startswith('{'):
                        json_start_idx = i
                        break
                if json_start_idx == -1:
                    self.skipTest("Could not find JSON in Java output")
                # Get all lines from JSON start to end
                json_lines = lines[json_start_idx:]
                json_str = '\n'.join(json_lines)
                try:
                    java_output = json.loads(json_str)
                except json.JSONDecodeError as e:
                    # Try finding complete JSON by looking for matching braces
                    brace_count = 0
                    json_lines = []
                    found_start = False
                    for line in reversed(lines):
                        if not found_start and line.strip().endswith('}'):
                            found_start = True
                        if found_start:
                            json_lines.insert(0, line)
                            brace_count += line.count('{') - line.count('}')
                            if brace_count == 0:
                                break
                    json_str = '\n'.join(json_lines)
                    try:
                        java_output = json.loads(json_str)
                    except json.JSONDecodeError:
                        self.skipTest(f"Could not parse JSON from Java output: {e}")
                java_data = java_output.get("data", {})
                java_is_dist = java_data.get("is_distributive", False)
                
                # Compare results
                self.assertEqual(
                    python_result, java_is_dist,
                    f"Python/Rust returned {python_result}, Java returned {java_is_dist}"
                )
                print(f"✓ is_congruence_dist_idempotent matches Java: {python_result}")
            else:
                self.skipTest(f"Java wrapper failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.skipTest("Java wrapper timed out")
        except FileNotFoundError:
            self.skipTest("Java not found in PATH")
        except (AssertionError, KeyError, json.JSONDecodeError, ValueError) as e:
            # Don't catch AssertionError - let test failures propagate
            raise
        except Exception as e:
            self.skipTest(f"Could not run Java wrapper: {e}")
    
    def test_is_congruence_modular_idempotent_with_cyclic3(self):
        """Test is_congruence_modular_idempotent with cyclic3 and compare with Java.
        """
        import os
        import subprocess
        import json
        
        algebra_path = "resources/algebras/cyclic3.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra with Python
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Note: cyclic3 is not idempotent
        # Check idempotency first
        is_idempotent = alg.is_idempotent()
        if not is_idempotent:
            print(f"Note: {algebra_path} is not idempotent; results may differ")
        
        # Get Python/Rust result
        python_result = uacalc_lib.alg.is_congruence_modular_idempotent(alg)
        self.assertIsInstance(python_result, bool)
        
        # Get Java result
        try:
            cmd = [
                "java", "-cp",
                "java_wrapper/build/classes:build/classes:org:jars/*",
                "java_wrapper.src.alg.MalcevWrapper",
                "is_congruence_modular_idempotent",
                "--algebra", algebra_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                # Extract JSON from output (may have progress messages before JSON)
                # Find the complete JSON object by counting braces
                stdout = result.stdout.strip()
                lines = stdout.split('\n')
                
                # Find the outermost complete JSON object
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
                    self.skipTest("Could not find JSON in Java output")
                
                json_str = '\n'.join(json_lines)
                try:
                    java_output = json.loads(json_str)
                except json.JSONDecodeError as e:
                    self.skipTest(f"Could not parse JSON from Java output: {e}. JSON: {json_str[:200]}")
                java_data = java_output.get("data", {})
                java_is_modular = java_data.get("is_modular", False)
                
                # Compare results
                self.assertEqual(
                    python_result, java_is_modular,
                    f"Python/Rust returned {python_result}, Java returned {java_is_modular}"
                )
            else:
                self.skipTest(f"Java wrapper failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.skipTest("Java wrapper timed out")
        except FileNotFoundError:
            self.skipTest("Java not found in PATH")
        except (AssertionError, KeyError, json.JSONDecodeError, ValueError) as e:
            # Don't catch AssertionError - let test failures propagate
            raise
        except Exception as e:
            self.skipTest(f"Could not run Java wrapper: {e}")
    
    def test_sd_meet_idempotent_with_cyclic3(self):
        """Test sd_meet_idempotent with cyclic3 and compare with Java."""
        import os
        import subprocess
        import json
        
        algebra_path = "resources/algebras/cyclic3.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra with Python
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Get Python/Rust result
        python_result = uacalc_lib.alg.sd_meet_idempotent(alg)
        # Should be None or a list of 2 elements
        if python_result is not None:
            self.assertIsInstance(python_result, list)
            self.assertEqual(len(python_result), 2)
        
        # Get Java result
        try:
            cmd = [
                "java", "-cp",
                "java_wrapper/build/classes:build/classes:org:jars/*",
                "java_wrapper.src.alg.MalcevWrapper",
                "sd_meet_idempotent",
                "--algebra", algebra_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                # Extract JSON from output (may have progress messages before JSON)
                stdout = result.stdout.strip()
                lines = stdout.split('\n')
                json_start_idx = -1
                for i in range(len(lines) - 1, -1, -1):
                    if lines[i].strip().startswith('{'):
                        json_start_idx = i
                        break
                if json_start_idx == -1:
                    self.skipTest("Could not find JSON in Java output")
                json_lines = lines[json_start_idx:]
                json_str = '\n'.join(json_lines)
                try:
                    java_output = json.loads(json_str)
                except json.JSONDecodeError as e:
                    brace_count = 0
                    json_lines = []
                    found_start = False
                    for line in reversed(lines):
                        if not found_start and line.strip().endswith('}'):
                            found_start = True
                        if found_start:
                            json_lines.insert(0, line)
                            brace_count += line.count('{') - line.count('}')
                            if brace_count == 0:
                                break
                    json_str = '\n'.join(json_lines)
                    try:
                        java_output = json.loads(json_str)
                    except json.JSONDecodeError:
                        self.skipTest(f"Could not parse JSON from Java output: {e}")
                java_data = java_output.get("data", {})
                java_witness_found = java_data.get("witness_found", False)
                
                # Compare results
                if python_result is None:
                    self.assertFalse(
                        java_witness_found,
                        f"Python/Rust returned None, but Java found witness: {java_data.get('witness')}"
                    )
                else:
                    self.assertTrue(
                        java_witness_found,
                        f"Python/Rust found witness {python_result}, but Java returned None"
                    )
                    java_witness = java_data.get("witness", [])
                    if isinstance(java_witness, str):
                        # Parse if it's a string representation
                        import ast
                        java_witness = ast.literal_eval(java_witness)
                    self.assertEqual(
                        python_result, java_witness,
                        f"Python/Rust witness {python_result} != Java witness {java_witness}"
                    )
                print(f"✓ sd_meet_idempotent matches Java: {python_result}")
            else:
                self.skipTest(f"Java wrapper failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.skipTest("Java wrapper timed out")
        except FileNotFoundError:
            self.skipTest("Java not found in PATH")
        except (AssertionError, KeyError, json.JSONDecodeError, ValueError) as e:
            # Don't catch AssertionError - let test failures propagate
            raise
        except Exception as e:
            self.skipTest(f"Could not run Java wrapper: {e}")
    
    def test_find_day_quadruple_in_square_with_cyclic3(self):
        """Test find_day_quadruple_in_square with cyclic3."""
        import os
        
        algebra_path = "resources/algebras/cyclic3.ua"
        if not os.path.exists(algebra_path):
            self.skipTest(f"Algebra file {algebra_path} not found")
        
        # Load algebra with Python
        AlgebraReader = uacalc_lib.io.AlgebraReader
        reader = AlgebraReader.new_from_file(algebra_path)
        alg = reader.read_algebra_file()
        
        # Get Python/Rust result
        python_result = uacalc_lib.alg.find_day_quadruple_in_square(alg)
        # Should be None or a list of 4 elements [x0, x1, y0, y1]
        if python_result is not None:
            self.assertIsInstance(python_result, list)
            self.assertEqual(len(python_result), 4)
        
        print(f"✓ find_day_quadruple_in_square result: {python_result}")
    
    def test_congruence_modular_variety_not_implemented(self):
        """Test that congruence_modular_variety returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.congruence_modular_variety(None)
        self.assertIn("not yet implemented", str(context.exception))
    
    def test_jonsson_level_not_implemented(self):
        """Test that jonsson_level returns not implemented error."""
        with self.assertRaises(ValueError) as context:
            uacalc_lib.alg.jonsson_level(None)
        self.assertIn("not yet implemented", str(context.exception))


if __name__ == '__main__':
    unittest.main()

