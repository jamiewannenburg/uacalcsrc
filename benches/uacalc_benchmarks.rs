use criterion::{black_box, criterion_group, criterion_main, BatchSize, Criterion};
use std::collections::HashSet;
use std::sync::Arc;
use uacalc::alg::op::operations::make_int_operation_str;
use uacalc::alg::{BasicAlgebra, BigProductAlgebra, Closer, SmallAlgebra};
use uacalc::resource::{clear_cancel, set_element_limit, set_memory_limit};
use uacalc::util::int_array::IntArray;

fn c2_power3() -> (Arc<BigProductAlgebra<i32>>, Vec<IntArray>) {
    let op = make_int_operation_str("m", 2, 2, vec![0, 1, 1, 0]).unwrap();
    let c2 = BasicAlgebra::new("C2".into(), HashSet::from([0, 1]), vec![op]);
    let boxed: Box<dyn SmallAlgebra<UniverseItem = i32>> = Box::new(c2);
    let alg = Arc::new(BigProductAlgebra::new_power_safe(boxed, 3).unwrap());
    let gens = vec![
        IntArray::from_array(vec![0, 0, 0]).unwrap(),
        IntArray::from_array(vec![0, 0, 1]).unwrap(),
    ];
    (alg, gens)
}

fn bench_sg_close_power(c: &mut Criterion) {
    let (alg, gens) = c2_power3();

    c.bench_function("sg_close_power_no_limits", |b| {
        b.iter(|| {
            clear_cancel();
            set_memory_limit(None);
            set_element_limit(None);
            let mut closer = Closer::new_safe(alg.clone(), gens.clone()).unwrap();
            black_box(closer.sg_close_power().unwrap());
        });
    });

    c.bench_function("sg_close_power_with_limits", |b| {
        b.iter(|| {
            clear_cancel();
            set_memory_limit(Some(u64::MAX / 4));
            set_element_limit(Some(10_000));
            let mut closer = Closer::new_safe(alg.clone(), gens.clone()).unwrap();
            black_box(closer.sg_close_power().unwrap());
        });
    });
}

criterion_group!(benches, bench_sg_close_power);
criterion_main!(benches);