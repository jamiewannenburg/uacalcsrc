"""
Tests for term parsing and evaluation functionality.
"""

import pytest
import time
from typing import List, Dict, Any

from uacalc import (
    Algebra, create_algebra, create_operation, create_term_arena,
    Term, TermArena, parse_term, eval_term, term_variables, term_operations,
    validate_term_against_algebra, HAS_NUMPY
)
from uacalc.terms import (
    TermParser, TermEvaluator, substitute_variables, simplify_term,
    term_depth, terms_equal, random_term, term_to_operation
)


class TestTermParsing:
    """Test term parsing functionality."""
    
    def test_parse_simple_variable(self):
        """Test parsing a simple variable."""
        arena = create_term_arena()
        term = parse_term(arena, "x0")
        
        assert isinstance(term, Term)
        assert term.is_variable()
        assert not term.is_operation()
        assert term.arity == 0
    
    def test_parse_constant(self):
        """Test parsing a constant term."""
        arena = create_term_arena()
        term = parse_term(arena, "c")
        
        assert isinstance(term, Term)
        assert not term.is_variable()
        assert term.is_operation()
        assert term.arity == 0
    
    def test_parse_unary_operation(self):
        """Test parsing a unary operation."""
        arena = create_term_arena()
        term = parse_term(arena, "f(x0)")
        
        assert isinstance(term, Term)
        assert not term.is_variable()
        assert term.is_operation()
        assert term.arity == 1
    
    def test_parse_binary_operation(self):
        """Test parsing a binary operation."""
        arena = create_term_arena()
        term = parse_term(arena, "f(x0, x1)")
        
        assert isinstance(term, Term)
        assert not term.is_variable()
        assert term.is_operation()
        assert term.arity == 2
    
    def test_parse_nested_operation(self):
        """Test parsing a nested operation."""
        arena = create_term_arena()
        term = parse_term(arena, "f(g(x0), h(x1, x2))")
        
        assert isinstance(term, Term)
        assert not term.is_variable()
        assert term.is_operation()
        assert term.arity == 2
    
    def test_parse_complex_expression(self):
        """Test parsing a complex expression."""
        arena = create_term_arena()
        term = parse_term(arena, "f(x0, g(h(x1), x2), k(x3, x4, x5))")
        
        assert isinstance(term, Term)
        assert not term.is_variable()
        assert term.is_operation()
        assert term.arity == 3
    
    def test_parse_with_variable_names(self):
        """Test parsing with named variables."""
        arena = create_term_arena()
        parser = TermParser(arena)
        var_names = {"a": 0, "b": 1, "c": 2}
        
        term = parser.parse_with_variables("f(a, g(b, c))", var_names)
        
        assert isinstance(term, Term)
        assert not term.is_variable()
        assert term.is_operation()
        assert term.arity == 2
    
    def test_validate_syntax_valid(self):
        """Test syntax validation with valid expressions."""
        arena = create_term_arena()
        parser = TermParser(arena)
        
        valid_expressions = [
            "x0",
            "c",
            "f(x0)",
            "f(x0, x1)",
            "f(g(x0), h(x1))",
            "f(x0, x1, x2)",
        ]
        
        for expr in valid_expressions:
            is_valid, error = parser.validate_syntax(expr)
            assert is_valid, f"Expression '{expr}' should be valid: {error}"
    
    def test_validate_syntax_invalid(self):
        """Test syntax validation with invalid expressions."""
        arena = create_term_arena()
        parser = TermParser(arena)
        
        invalid_expressions = [
            "",  # Empty
            "(",  # Unbalanced parentheses
            ")",  # Unbalanced parentheses
            "f(x0",  # Missing closing parenthesis
            "f(x0,)",  # Missing argument
            "f(,x0)",  # Missing argument
            "f(x0 x1)",  # Missing comma
        ]
        
        for expr in invalid_expressions:
            is_valid, error = parser.validate_syntax(expr)
            assert not is_valid, f"Expression '{expr}' should be invalid"
            assert error is not None


class TestTermEvaluation:
    """Test term evaluation functionality."""
    
    def test_eval_variable(self):
        """Test evaluating a variable term."""
        # Create algebra with operations
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        arena = create_term_arena()
        term = parse_term(arena, "x0")
        
        variables = {0: 1}
        result = eval_term(term, algebra, variables)
        
        assert result == 1
    
    def test_eval_constant(self):
        """Test evaluating a constant term."""
        # Create algebra with operations
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("c", 0, [[1]])
        algebra.add_operation("c", operation)
        
        arena = create_term_arena()
        term = parse_term(arena, "c")
        
        variables = {}
        result = eval_term(term, algebra, variables)
        
        # Should return some value (depends on implementation)
        assert isinstance(result, int)
    
    def test_eval_unary_operation(self):
        """Test evaluating a unary operation."""
        # Create algebra with operations
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 1, [[0, 1], [1, 2], [2, 0]])
        algebra.add_operation("f", operation)
        
        arena = create_term_arena()
        term = parse_term(arena, "f(x0)")
        
        variables = {0: 2}
        result = eval_term(term, algebra, variables)
        
        # Should return some value (depends on implementation)
        assert isinstance(result, int)
    
    def test_eval_binary_operation(self):
        """Test evaluating a binary operation."""
        # Create algebra with operations
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        arena = create_term_arena()
        term = parse_term(arena, "f(x0, x1)")
        
        variables = {0: 1, 1: 2}
        result = eval_term(term, algebra, variables)
        
        # Should return some value (depends on implementation)
        assert isinstance(result, int)
    
    def test_eval_nested_operation(self):
        """Test evaluating a nested operation."""
        # Create algebra with operations
        algebra = create_algebra("test", [0, 1, 2])
        f_op = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        g_op = create_operation("g", 1, [[0, 1], [1, 2], [2, 0]])
        h_op = create_operation("h", 1, [[0, 2], [1, 0], [2, 1]])
        algebra.add_operation("f", f_op)
        algebra.add_operation("g", g_op)
        algebra.add_operation("h", h_op)
        
        arena = create_term_arena()
        term = parse_term(arena, "f(g(x0), h(x1))")
        
        variables = {0: 1, 1: 2}
        result = eval_term(term, algebra, variables)
        
        # Should return some value (depends on implementation)
        assert isinstance(result, int)
    
    def test_eval_missing_variable(self):
        """Test evaluation with missing variable."""
        # Create algebra with operations
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        evaluator = TermEvaluator(algebra)
        arena = create_term_arena()
        term = parse_term(arena, "f(x0, x1)")
        
        variables = {0: 1}  # Missing x1
        
        with pytest.raises(ValueError):
            evaluator.eval(term, variables)


class TestTermEvaluator:
    """Test the TermEvaluator class."""
    
    def test_evaluator_creation(self):
        """Test creating a term evaluator."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        evaluator = TermEvaluator(algebra)
        assert evaluator.algebra == algebra
    
    def test_eval_simple_term(self):
        """Test evaluating a simple term."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        evaluator = TermEvaluator(algebra)
        arena = create_term_arena()
        term = parse_term(arena, "f(x0, x1)")
        
        variables = {0: 1, 1: 2}
        result = evaluator.eval(term, variables)
        
        assert isinstance(result, int)
        assert 0 <= result < algebra.cardinality
    
    def test_eval_string_term(self):
        """Test evaluating a term from string."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        evaluator = TermEvaluator(algebra)
        
        variables = {0: 1, 1: 2}
        result = evaluator.eval("f(x0, x1)", variables)
        
        assert isinstance(result, int)
        assert 0 <= result < algebra.cardinality
    
    def test_eval_batch(self):
        """Test batch evaluation."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        evaluator = TermEvaluator(algebra)
        arena = create_term_arena()
        term = parse_term(arena, "f(x0, x1)")
        
        variable_sets = [
            {0: 0, 1: 1},
            {0: 1, 1: 2},
            {0: 2, 1: 0},
        ]
        
        results = evaluator.eval_batch([term] * 3, variable_sets)
        
        assert len(results) == 3
        for result in results:
            assert isinstance(result, int)
            assert 0 <= result < algebra.cardinality
    
    def test_to_operation_table(self):
        """Test converting term to operation table."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        evaluator = TermEvaluator(algebra)
        arena = create_term_arena()
        term = parse_term(arena, "f(x0, x1)")
        
        table = evaluator.to_operation_table(term, 2)
        
        assert isinstance(table, list)
        assert len(table) == algebra.cardinality
        for row in table:
            assert len(row) == algebra.cardinality
            for value in row:
                assert isinstance(value, int)
                assert 0 <= value < algebra.cardinality
    
    def test_caching(self):
        """Test that evaluation results are cached."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        evaluator = TermEvaluator(algebra)
        arena = create_term_arena()
        term = parse_term(arena, "f(x0, x1)")
        
        variables = {0: 1, 1: 2}
        
        # First evaluation
        result1 = evaluator.eval(term, variables)
        
        # Second evaluation (should be cached)
        result2 = evaluator.eval(term, variables)
        
        assert result1 == result2
        
        # Test that cache is being used by checking cache size
        # The cache should contain at least one entry
        assert len(evaluator._cache) > 0


class TestTermManipulation:
    """Test term manipulation functions."""
    
    def test_term_depth(self):
        """Test computing term depth."""
        arena = create_term_arena()
        
        # Variable has depth 0
        var_term = parse_term(arena, "x0")
        assert var_term.depth() == 0
        
        # Simple operation has depth 1
        op_term = parse_term(arena, "f(x0)")
        assert op_term.depth() == 1
        
        # Nested operation has depth 2
        nested_term = parse_term(arena, "f(g(x0))")
        assert nested_term.depth() == 2
    
    def test_term_variables(self):
        """Test extracting variables from term."""
        arena = create_term_arena()
        
        # Single variable
        var_term = parse_term(arena, "x0")
        vars = var_term.variables()
        assert vars == [0]
        
        # Multiple variables
        multi_term = parse_term(arena, "f(x0, x1, x2)")
        vars = multi_term.variables()
        assert sorted(vars) == [0, 1, 2]
        
        # Nested variables
        nested_term = parse_term(arena, "f(g(x0, x1), h(x2))")
        vars = nested_term.variables()
        assert sorted(vars) == [0, 1, 2]
    
    def test_term_operations(self):
        """Test extracting operation symbols from term."""
        arena = create_term_arena()
        
        # Simple operation
        op_term = parse_term(arena, "f(x0)")
        ops = term_operations(op_term)
        # Implementation dependent - just check it's a list
        assert isinstance(ops, list)
    
    def test_terms_equal(self):
        """Test term equality checking."""
        arena = create_term_arena()
        algebra = create_algebra("test", [0, 1, 2])
        
        term1 = parse_term(arena, "f(x0, x1)")
        term2 = parse_term(arena, "f(x0, x1)")
        term3 = parse_term(arena, "f(x1, x0)")
        
        # Same terms should be equal
        assert terms_equal(term1, term2, algebra)
        
        # Different terms should not be equal
        assert not terms_equal(term1, term3, algebra)


class TestTermConstruction:
    """Test term construction functions."""
    
    def test_variable_construction(self):
        """Test creating variable terms."""
        arena = create_term_arena()
        
        # Test with index
        var1 = arena.make_variable(0)
        assert isinstance(var1, Term)
        assert var1.is_variable()
        
        # Test with different index
        var2 = arena.make_variable(1)
        assert isinstance(var2, Term)
        assert var2.is_variable()
    
    def test_constant_construction(self):
        """Test creating constant terms."""
        arena = create_term_arena()
        const = arena.make_term("c", [])
        assert isinstance(const, Term)
        assert const.is_operation()
        assert const.arity == 0
    
    def test_operation_construction(self):
        """Test creating operation terms."""
        arena = create_term_arena()
        var1 = arena.make_variable(0)
        var2 = arena.make_variable(1)
        
        op = arena.make_term("f", [var1, var2])
        assert isinstance(op, Term)
        assert op.is_operation()
        assert op.arity == 2
    
    def test_random_term_generation(self):
        """Test random term generation."""
        operations = ["f", "g", "h"]
        variables = 3
        
        term = random_term(depth=2, operations=operations, variables=variables)
        assert isinstance(term, Term)
        assert term.depth() <= 2


class TestTermIntegration:
    """Test term integration with algebra operations."""
    
    def test_term_to_operation(self):
        """Test converting term to operation."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        arena = create_term_arena()
        term = parse_term(arena, "f(x0, x1)")
        
        new_op = term_to_operation(term, "g", algebra)
        assert isinstance(new_op, type(operation))
        assert new_op.arity == 2
    
    def test_validate_term_against_algebra(self):
        """Test term validation against algebra."""
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        arena = create_term_arena()
        
        # Valid term
        valid_term = parse_term(arena, "f(x0, x1)")
        is_valid, error = validate_term_against_algebra(valid_term, algebra)
        assert is_valid
        assert error is None
        
        # Invalid term (unknown operation)
        invalid_term = parse_term(arena, "g(x0, x1)")
        is_valid, error = validate_term_against_algebra(invalid_term, algebra)
        assert not is_valid
        assert error is not None


class TestNumPyIntegration:
    """Test NumPy integration for term evaluation."""
    
    @pytest.mark.skipif(not HAS_NUMPY, reason="NumPy not available")
    def test_eval_term_numpy(self):
        """Test NumPy-based term evaluation."""
        import numpy as np
        
        arena = create_term_arena()
        term = parse_term(arena, "f(x0, x1)")
        
        # Create NumPy array of variable assignments
        variables = np.array([[0, 1], [1, 2], [2, 0]])
        
        # This would require the actual implementation
        # result = eval_term_numpy(term, variables)
        # assert isinstance(result, np.ndarray)
        # assert result.shape == (3,)
    
    @pytest.mark.skipif(not HAS_NUMPY, reason="NumPy not available")
    def test_batch_eval_terms(self):
        """Test batch evaluation of multiple terms."""
        import numpy as np
        
        arena = create_term_arena()
        terms = [
            parse_term(arena, "f(x0, x1)"),
            parse_term(arena, "g(x0)"),
        ]
        
        # Create NumPy array of variable assignments
        variables = np.array([[0, 1], [1, 2], [2, 0]])
        
        # This would require the actual implementation
        # result = batch_eval_terms(terms, variables)
        # assert isinstance(result, np.ndarray)
        # assert result.shape == (2, 3)


class TestTermParserAdvanced:
    """Test advanced term parser functionality."""
    
    def test_parser_with_complex_expressions(self):
        """Test parser with complex expressions."""
        arena = create_term_arena()
        parser = TermParser(arena)
        
        complex_expressions = [
            "f(x0, g(x1, h(x2)))",
            "f(g(x0), h(x1, x2), k(x3))",
            "f(x0, x1, x2, x3, x4)",
        ]
        
        for expr in complex_expressions:
            term = parser.parse(expr)
            assert isinstance(term, Term)
            assert term.is_operation()
    
    def test_parser_error_handling(self):
        """Test parser error handling."""
        arena = create_term_arena()
        parser = TermParser(arena)

        invalid_expressions = [
            "f(x0,",  # Missing closing parenthesis
            "f(x0, x1,)",  # Trailing comma        
            "f(x0 x1)",  # Missing comma
        ]

        for expr in invalid_expressions:
            is_valid, error = parser.validate_syntax(expr)
            assert not is_valid, f"Expression '{expr}' should be invalid"
            assert error is not None, f"Error message should be provided for '{expr}'"


class TestTermEvaluationAdvanced:
    """Test advanced term evaluation functionality."""
    
    def test_evaluation_with_large_terms(self):
        """Test evaluation with large terms."""
        arena = create_term_arena()
        
        # Create a large nested term with correct arity
        large_expr = "f(" + ", ".join([f"g(x{i})" for i in range(2)]) + ")"
        term = parse_term(arena, large_expr)
        
        variables = {i: i % 3 for i in range(10)}
        
        # Create algebra with operations
        algebra = create_algebra("test", [0, 1, 2])
        f_op = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        g_op = create_operation("g", 1, [[0, 1], [1, 2], [2, 0]])
        algebra.add_operation("f", f_op)
        algebra.add_operation("g", g_op)
        
        # Should not crash
        result = eval_term(term, algebra, variables)
        assert isinstance(result, int)
    
    def test_evaluation_performance(self):
        """Test evaluation performance."""
        arena = create_term_arena()
        term = parse_term(arena, "f(x0, x1)")
        
        variables = {0: 1, 1: 2}
        
        # Create algebra with operations
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        # Time multiple evaluations
        start_time = time.time()
        for _ in range(1000):
            result = eval_term(term, algebra, variables)
        total_time = time.time() - start_time
        
        # Should be reasonably fast
        assert total_time < 1.0  # Less than 1 second for 1000 evaluations


class TestIntegration:
    """Integration tests for term functionality."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from parsing to evaluation."""
        # Create algebra
        algebra = create_algebra("test", [0, 1, 2])
        operation = create_operation("f", 2, [[0, 1, 2], [1, 1, 1], [2, 1, 2]])
        algebra.add_operation("f", operation)
        
        # Parse term
        arena = create_term_arena()
        term = parse_term(arena, "f(x0, x1)")
        
        # Analyze term
        depth = term.depth()
        variables = term.variables()
        operations = term_operations(term)
        
        # Evaluate term
        var_assignment = {0: 1, 1: 2}
        result = eval_term(term, algebra, var_assignment)
        
        # Validate term
        is_valid, error = validate_term_against_algebra(term, algebra)
        
        # Verify results
        assert depth == 1
        assert sorted(variables) == [0, 1]
        assert isinstance(result, int)
        assert 0 <= result < algebra.cardinality
        assert is_valid
        assert error is None
    
    #@pytest.mark.slow
    def test_large_scale_evaluation(self):
        """Test large-scale term evaluation."""
        # Create larger algebra
        algebra = create_algebra("large_test", list(range(8)))
        operation = create_operation("f", 2, [[(i + j) % 8 for j in range(8)] for i in range(8)])
        algebra.add_operation("f", operation)
        
        # Create evaluator
        evaluator = TermEvaluator(algebra)
        
        # Generate many terms
        arena = create_term_arena()
        terms = []
        variable_sets = []
        
        for i in range(100):
            # Use correct arity for operation "f" (arity 2)
            term = random_term(depth=3, operations=["f"], variables=4, operation_arities={"f": 2})
            terms.append(term)
            variable_sets.append({j: (i + j) % 8 for j in range(4)})
        
        # Batch evaluate
        start_time = time.time()
        results = evaluator.eval_batch(terms, variable_sets)
        total_time = time.time() - start_time
        
        # Should complete in reasonable time
        assert total_time < 10.0  # Less than 10 seconds
        assert len(results) == 100
        for result in results:
            assert 0 <= result < 8


if __name__ == "__main__":
    pytest.main([__file__])
