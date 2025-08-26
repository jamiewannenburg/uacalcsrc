use criterion::{black_box, criterion_group, criterion_main, Criterion};
use uacalc_core::prelude::*;

#[cfg(feature = "conlat")]
fn benchmark_congruence_generation(c: &mut Criterion) {
    let mut group = c.benchmark_group("congruence_generation");

    // Test with different algebra sizes
    for size in [3, 4, 5] {
        let algebra = BasicAlgebra::with_cardinality(format!("size_{}", size), size).unwrap();

        group.bench_function(&format!("size_{}", size), |b| {
            b.iter(|| {
                let pairs = vec![(0, 1)];
                black_box(cg(&algebra, &pairs).unwrap());
            });
        });
    }

    group.finish();
}

#[cfg(feature = "conlat")]
fn benchmark_lattice_construction(c: &mut Criterion) {
    let mut group = c.benchmark_group("lattice_construction");

    // Test with different algebra sizes
    for size in [3, 4] {
        let algebra = BasicAlgebra::with_cardinality(format!("size_{}", size), size).unwrap();

        group.bench_function(&format!("size_{}", size), |b| {
            b.iter(|| {
                let mut lattice = BasicCongruenceLattice::new(Box::new(algebra.clone())).unwrap();
                black_box(lattice.ensure_universe_built().unwrap());
            });
        });
    }

    group.finish();
}

#[cfg(feature = "term-eval")]
fn benchmark_term_evaluation(c: &mut Criterion) {
    let mut group = c.benchmark_group("term_evaluation");

    // Create a simple algebra and term
    let algebra = BasicAlgebra::with_cardinality("test".to_string(), 3).unwrap();
    let mut arena = TermArena::new();
    let var_id = arena.make_variable(0);
    let variables = VariableAssignment::from_values(vec![1, 2, 3]);

    group.bench_function("simple_variable", |b| {
        b.iter(|| {
            black_box(eval_term(var_id, &arena, &algebra, &variables).unwrap());
        });
    });

    group.finish();
}

#[cfg(feature = "taylor")]
fn benchmark_taylor_search(c: &mut Criterion) {
    let mut group = c.benchmark_group("taylor_search");

    // Create a simple Taylor specification
    let arity = 4;
    let symbol = OperationSymbol::new("Bench".to_string(), arity);
    let equations = vec![(
        IntArray::from_vec(vec![0, 0, 0, 0]),
        IntArray::from_vec(vec![0, 0, 0, 0]),
    )];
    let spec = TaylorSpec::new(arity, equations, symbol);
    let taylor = Taylor::new(spec);

    group.bench_function("level_1_search", |b| {
        b.iter(|| {
            let mut arena = TermArena::new();
            black_box(taylor.interprets(1, &mut arena));
        });
    });

    group.finish();
}

#[cfg(feature = "conlat")]
fn benchmark_principal_congruence(c: &mut Criterion) {
    let mut group = c.benchmark_group("principal_congruence");

    // Test with different algebra sizes
    for size in [3, 4, 5] {
        let algebra = BasicAlgebra::with_cardinality(format!("size_{}", size), size).unwrap();

        group.bench_function(&format!("size_{}_pair_0_1", size), |b| {
            b.iter(|| {
                black_box(principal_congruence(&algebra, 0, 1).unwrap());
            });
        });
    }

    group.finish();
}

#[cfg(feature = "conlat")]
fn benchmark_join_irreducible_detection(c: &mut Criterion) {
    let mut group = c.benchmark_group("join_irreducible_detection");

    // Test with different algebra sizes
    for size in [3, 4] {
        let algebra = BasicAlgebra::with_cardinality(format!("size_{}", size), size).unwrap();

        group.bench_function(&format!("size_{}", size), |b| {
            b.iter(|| {
                black_box(find_join_irreducibles(&algebra).unwrap());
            });
        });
    }

    group.finish();
}

// Configure criterion groups
#[cfg(feature = "conlat")]
criterion_group!(
    conlat_benches,
    benchmark_congruence_generation,
    benchmark_lattice_construction,
    benchmark_principal_congruence,
    benchmark_join_irreducible_detection
);

#[cfg(feature = "term-eval")]
criterion_group!(term_benches, benchmark_term_evaluation);

#[cfg(feature = "taylor")]
criterion_group!(taylor_benches, benchmark_taylor_search);

// Main function for running benchmarks
#[cfg(any(feature = "conlat", feature = "term-eval", feature = "taylor"))]
criterion_main!(
    #[cfg(feature = "conlat")]
    conlat_benches,
    #[cfg(feature = "term-eval")]
    term_benches,
    #[cfg(feature = "taylor")]
    taylor_benches
);

// Fallback main for when no features are enabled
#[cfg(not(any(feature = "conlat", feature = "term-eval", feature = "taylor")))]
fn main() {
    println!("No benchmark features enabled. Enable 'conlat', 'term-eval', or 'taylor' features to run benchmarks.");
}
