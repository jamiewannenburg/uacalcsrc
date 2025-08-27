use criterion::{black_box, criterion_group, criterion_main, Criterion};
use std::path::Path;
use std::time::Instant;
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

/// Java comparison benchmarks
#[cfg(feature = "conlat")]
fn benchmark_cg_vs_java(c: &mut Criterion) {
    let mut group = c.benchmark_group("java_comparison");

    // Test with real algebra files from resources
    let algebra_files = [
        "resources/algebras/ba2.ua",
        "resources/algebras/cyclic3.ua",
        "resources/algebras/m3.ua",
        "resources/algebras/n5.ua",
    ];

    for file in &algebra_files {
        if Path::new(file).exists() {
            if let Ok(algebra) = load_algebra_from_file(file) {
                let file_name = Path::new(file).file_name().unwrap().to_str().unwrap();

                group.bench_function(&format!("cg_{}", file_name), |b| {
                    b.iter(|| {
                        let size = algebra.cardinality();
                        for a in 0..size {
                            for b in (a + 1)..size {
                                black_box(cg(&algebra, &[(a, b)]).unwrap());
                            }
                        }
                    });
                });
            }
        }
    }

    group.finish();
}

/// Memory usage benchmarks
#[cfg(feature = "conlat")]
fn benchmark_memory_usage(c: &mut Criterion) {
    let mut group = c.benchmark_group("memory_usage");

    for size in [3, 5, 7, 10] {
        let algebra = BasicAlgebra::with_cardinality(format!("size_{}", size), size).unwrap();

        group.bench_function(&format!("cg_memory_size_{}", size), |b| {
            b.iter(|| {
                let start_memory = get_memory_usage();
                let pairs = vec![(0, 1)];
                let _result = cg(&algebra, &pairs).unwrap();
                let end_memory = get_memory_usage();

                if let (Some(start), Some(end)) = (start_memory, end_memory) {
                    let memory_used = end - start;
                    black_box(memory_used);
                }
            });
        });
    }

    group.finish();
}

/// Scalability testing
#[cfg(feature = "conlat")]
fn benchmark_scalability(c: &mut Criterion) {
    let mut group = c.benchmark_group("scalability");

    // Test performance scaling with algebra size
    for size in [3, 5, 7, 10, 15] {
        let algebra = BasicAlgebra::with_cardinality(format!("size_{}", size), size).unwrap();

        group.bench_function(&format!("cg_scaling_size_{}", size), |b| {
            b.iter(|| {
                let size = algebra.cardinality();
                for a in 0..size {
                    for b in (a + 1)..size {
                        black_box(cg(&algebra, &[(a, b)]).unwrap());
                    }
                }
            });
        });
    }

    group.finish();
}

/// I/O performance benchmarks
fn benchmark_io_performance(c: &mut Criterion) {
    let mut group = c.benchmark_group("io_performance");

    let algebra_files = [
        "resources/algebras/ba2.ua",
        "resources/algebras/cyclic3.ua",
        "resources/algebras/m3.ua",
    ];

    for file in &algebra_files {
        if Path::new(file).exists() {
            let file_name = Path::new(file).file_name().unwrap().to_str().unwrap();

            group.bench_function(&format!("load_{}", file_name), |b| {
                b.iter(|| {
                    black_box(load_algebra_from_file(file).unwrap());
                });
            });
        }
    }

    group.finish();
}

/// Helper function to get memory usage
fn get_memory_usage() -> Option<f64> {
    #[cfg(target_os = "linux")]
    {
        if let Ok(contents) = std::fs::read_to_string("/proc/self/status") {
            for line in contents.lines() {
                if line.starts_with("VmRSS:") {
                    if let Some(kb_str) = line.split_whitespace().nth(1) {
                        if let Ok(kb) = kb_str.parse::<f64>() {
                            return Some(kb / 1024.0); // Convert KB to MB
                        }
                    }
                }
            }
        }
    }
    None
}

// Configure criterion groups
#[cfg(feature = "conlat")]
criterion_group!(
    conlat_benches,
    benchmark_congruence_generation,
    benchmark_lattice_construction,
    benchmark_principal_congruence,
    benchmark_join_irreducible_detection,
    benchmark_cg_vs_java,
    benchmark_memory_usage,
    benchmark_scalability
);

#[cfg(feature = "term-eval")]
criterion_group!(term_benches, benchmark_term_evaluation);

#[cfg(feature = "taylor")]
criterion_group!(taylor_benches, benchmark_taylor_search);

// Configure criterion main
criterion_main!(conlat_benches, term_benches, taylor_benches);
