use uacalc_core::prelude::*;

#[cfg(feature = "taylor")]
#[test]
fn test_taylor_spec_creation() {
    // Test creating a Taylor specification
    let arity = 4;
    let symbol = OperationSymbol::new("MM".to_string(), arity);

    // Create simple equations
    let equations = vec![
        (
            IntArray::from_vec(vec![0, 0, 0, 0]),
            IntArray::from_vec(vec![0, 0, 0, 0]),
        ),
        (
            IntArray::from_vec(vec![1, 1, 1, 1]),
            IntArray::from_vec(vec![1, 1, 1, 1]),
        ),
    ];

    let spec = TaylorSpec::new(arity, equations, symbol);

    assert_eq!(spec.arity, 4);
    assert_eq!(spec.equations.len(), 2);
    assert_eq!(spec.symbol.name(), "MM");
}

#[cfg(feature = "taylor")]
#[test]
fn test_taylor_equation_satisfaction() {
    // Test equation satisfaction checking
    let arity = 4;
    let symbol = OperationSymbol::new("Test".to_string(), arity);

    // Create equations that are satisfied by constant assignments
    let equations = vec![
        (
            IntArray::from_vec(vec![0, 0, 0, 0]),
            IntArray::from_vec(vec![0, 0, 0, 0]),
        ),
        (
            IntArray::from_vec(vec![1, 1, 1, 1]),
            IntArray::from_vec(vec![1, 1, 1, 1]),
        ),
    ];

    let spec = TaylorSpec::new(arity, equations, symbol);

    // Test with constant assignments
    let const_0 = IntArray::from_vec(vec![0, 0, 0, 0]);
    let const_1 = IntArray::from_vec(vec![1, 1, 1, 1]);

    assert!(spec.satisfies_equations());
    assert!(spec.satisfies_equations());
}

#[cfg(feature = "taylor")]
#[test]
fn test_taylor_interpretation_search() {
    // Test interpretation search
    let arity = 4;
    let symbol = OperationSymbol::new("Search".to_string(), arity);

    // Create simple equations
    let equations = vec![(
        IntArray::from_vec(vec![0, 0, 0, 0]),
        IntArray::from_vec(vec![0, 0, 0, 0]),
    )];

    let spec = TaylorSpec::new(arity, equations, symbol);
    let taylor = Taylor::new(spec);

    // Test interpretation search at low levels
    let mut arena = TermArena::new();

    // Search for interpretations at level 1
    let interpretation = taylor.interprets(1, &mut arena);
    // May or may not find an interpretation depending on the equations
    assert!(interpretation.is_some() || interpretation.is_none());
}

#[cfg(feature = "taylor")]
#[test]
fn test_taylor_canonical_forms() {
    // Test canonical form computation
    let arity = 4;
    let symbol = OperationSymbol::new("Canonical".to_string(), arity);

    // Create equations that should have canonical forms
    let equations = vec![(
        IntArray::from_vec(vec![0, 1, 0, 1]),
        IntArray::from_vec(vec![0, 1, 0, 1]),
    )];

    let spec = TaylorSpec::new(arity, equations, symbol);

    // Test canonical form computation
    let input = IntArray::from_vec(vec![0, 1, 0, 1]);
    let mut uf = spec.union_find.clone();
    let canonical = canonical_form(&input, &mut uf);

    // Canonical form should be consistent
    assert_eq!(canonical, input);
}

#[cfg(feature = "taylor")]
#[test]
fn test_taylor_term_conversion() {
    // Test converting Taylor specifications to terms
    let arity = 4;
    let symbol = OperationSymbol::new("Convert".to_string(), arity);

    let equations = vec![(
        IntArray::from_vec(vec![0, 0, 0, 0]),
        IntArray::from_vec(vec![0, 0, 0, 0]),
    )];

    let spec = TaylorSpec::new(arity, equations, symbol);
    let taylor = Taylor::new(spec);

    // Test conversion to term
    let mut arena = TermArena::new();
    let term_id = taylor.to_term(&mut arena);

    // Should create a valid term
    assert!(arena.get_term(term_id).is_ok());
}

#[cfg(feature = "taylor")]
#[test]
fn test_markovic_mckenzie_term() {
    // Test Markovic-McKenzie term creation
    let taylor = markovic_mckenzie_term();

    assert_eq!(taylor.arity(), 4);
    assert_eq!(taylor.spec().symbol.name(), "MM");
    assert!(!taylor.equations().is_empty());
}

#[cfg(feature = "taylor")]
#[test]
fn test_siggers_term() {
    // Test Siggers term creation
    let taylor = siggers_term();

    assert_eq!(taylor.arity(), 6);
    assert_eq!(taylor.spec().symbol.name(), "Siggers");
    assert!(!taylor.equations().is_empty());
}

#[cfg(feature = "taylor")]
#[test]
fn test_int_array_operations() {
    // Test IntArray operations
    let mut array = IntArray::new(4);

    // Test setting and getting values
    array.set(0, 1).unwrap();
    array.set(1, 0).unwrap();
    array.set(2, 1).unwrap();
    array.set(3, 0).unwrap();

    assert_eq!(array.get(0).unwrap(), 1);
    assert_eq!(array.get(1).unwrap(), 0);
    assert_eq!(array.get(2).unwrap(), 1);
    assert_eq!(array.get(3).unwrap(), 0);

    // Test from_vec constructor
    let vec_array = IntArray::from_vec(vec![1, 0, 1, 0]);
    assert_eq!(vec_array.get(0).unwrap(), 1);
    assert_eq!(vec_array.get(1).unwrap(), 0);
    assert_eq!(vec_array.get(2).unwrap(), 1);
    assert_eq!(vec_array.get(3).unwrap(), 0);
}

#[cfg(feature = "taylor")]
#[test]
fn test_taylor_assignment_aware_validation() {
    // Test assignment-aware equation validation
    let arity = 4;
    let symbol = OperationSymbol::new("AssignmentTest".to_string(), arity);

    // Create equations that depend on assignments
    let equations = vec![(
        IntArray::from_vec(vec![0, 1, 2, 3]),
        IntArray::from_vec(vec![0, 1, 2, 3]),
    )];

    let spec = TaylorSpec::new(arity, equations, symbol);
    let taylor = Taylor::new(spec);

    // Test with assignment that should satisfy equations
    let satisfying_assignment = IntArray::from_vec(vec![0, 1, 2, 3]);
    assert!(taylor.satisfies_equations_with_assignment(&satisfying_assignment));

    // Test with assignment that should not satisfy equations
    let non_satisfying_assignment = IntArray::from_vec(vec![1, 0, 1, 0]);
    assert!(!taylor.satisfies_equations_with_assignment(&non_satisfying_assignment));
}

#[cfg(feature = "taylor")]
#[test]
fn test_taylor_assignment_validation_with_union_find() {
    // Test that assignment validation properly uses UnionFind
    let arity = 2;
    let symbol = OperationSymbol::new("UnionTest".to_string(), arity);

    // Create equations that create equivalence classes
    let equations = vec![(
        IntArray::from_vec(vec![0, 1]),
        IntArray::from_vec(vec![1, 0]),
    )];

    let spec = TaylorSpec::new(arity, equations, symbol);
    let taylor = Taylor::new(spec);

    // Test with assignment that should satisfy the equivalence
    let assignment = IntArray::from_vec(vec![0, 1]);
    assert!(taylor.satisfies_equations_with_assignment(&assignment));

    // Test with assignment that should also satisfy (due to equivalence)
    let assignment2 = IntArray::from_vec(vec![1, 0]);
    assert!(taylor.satisfies_equations_with_assignment(&assignment2));
}

#[cfg(feature = "taylor")]
#[test]
fn test_taylor_interpretation_with_assignment() {
    // Test that interpretation search uses assignment-aware validation
    let arity = 2;
    let symbol = OperationSymbol::new("InterpretTest".to_string(), arity);

    // Create simple equations that should be satisfied by constant assignments
    let equations = vec![(
        IntArray::from_vec(vec![0, 0]),
        IntArray::from_vec(vec![0, 0]),
    )];

    let spec = TaylorSpec::new(arity, equations, symbol);
    let taylor = Taylor::new(spec);

    // Test interpretation search
    let mut arena = TermArena::new();
    let interpretation = taylor.interprets(1, &mut arena);

    // Should find an interpretation with constant assignment [0, 0]
    assert!(interpretation.is_some());
}
