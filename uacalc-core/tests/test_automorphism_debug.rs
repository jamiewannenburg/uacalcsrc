mod test_automorphism_debug {
    use std::sync::{Arc, Mutex};
    use std::thread;
    use std::time::Duration;
    use uacalc_core::{
        algebra::BasicAlgebra,
        error::{UACalcError, UACalcResult},
        homomorphism::enumerate_automorphisms,
        operation::{OperationSymbol, TableOperation},
    };

    // Helper function to create a cyclic group of given size
    fn create_cyclic_group(size: usize) -> Arc<Mutex<BasicAlgebra>> {
        println!("Creating cyclic group of size {}", size);
        let mut algebra = BasicAlgebra::with_cardinality("CyclicGroup".to_string(), size).unwrap();

        // Create multiplication table
        let mut table = Vec::new();
        for i in 0..size {
            for j in 0..size {
                table.push(vec![i, j, (i + j) % size]);
            }
        }

        let operation =
            TableOperation::new(OperationSymbol::new("multiply".to_string(), 2), table, size)
                .unwrap();

        algebra
            .add_operation("multiply".to_string(), Arc::new(Mutex::new(operation)))
            .unwrap();
        println!("Cyclic group created successfully");
        Arc::new(Mutex::new(algebra))
    }

    // Helper function to create a Boolean algebra of given size
    fn create_boolean_algebra(size: usize) -> UACalcResult<Arc<Mutex<BasicAlgebra>>> {
        println!("Creating Boolean algebra of size {}", size);

        // Boolean algebras must have size 2^n
        let mut n = 0;
        let mut s = 1;
        while s < size {
            s *= 2;
            n += 1;
        }
        if s != size {
            return Err(UACalcError::InvalidHomomorphism {
                message: "Boolean algebra size must be a power of 2".into(),
            });
        }

        let mut algebra =
            BasicAlgebra::with_cardinality("BooleanAlgebra".to_string(), size).unwrap();

        // Create meet operation (AND)
        let mut meet_table = Vec::new();
        for i in 0..size {
            for j in 0..size {
                meet_table.push(vec![i, j, i & j]);
            }
        }

        // Create join operation (OR)
        let mut join_table = Vec::new();
        for i in 0..size {
            for j in 0..size {
                join_table.push(vec![i, j, i | j]);
            }
        }

        // Create complement operation (NOT)
        let mut complement_table = Vec::new();
        for i in 0..size {
            complement_table.push(vec![i, (!i) & (size - 1)]);
        }

        let meet_op = TableOperation::new(
            OperationSymbol::new("meet".to_string(), 2),
            meet_table,
            size,
        )
        .unwrap();

        let join_op = TableOperation::new(
            OperationSymbol::new("join".to_string(), 2),
            join_table,
            size,
        )
        .unwrap();

        let complement_op = TableOperation::new(
            OperationSymbol::new("complement".to_string(), 1),
            complement_table,
            size,
        )
        .unwrap();

        algebra
            .add_operation("meet".to_string(), Arc::new(Mutex::new(meet_op)))
            .unwrap();
        algebra
            .add_operation("join".to_string(), Arc::new(Mutex::new(join_op)))
            .unwrap();
        algebra
            .add_operation(
                "complement".to_string(),
                Arc::new(Mutex::new(complement_op)),
            )
            .unwrap();

        println!("Boolean algebra created successfully");
        Ok(Arc::new(Mutex::new(algebra)))
    }

    fn run_with_timeout<F, T>(f: F, timeout_secs: u64) -> Option<UACalcResult<T>>
    where
        F: FnOnce() -> UACalcResult<T> + Send + 'static,
        T: Send + 'static,
    {
        let (tx, rx) = std::sync::mpsc::channel();

        let handle = thread::spawn(move || {
            println!("Thread started");
            let result = f();
            println!("Thread finished");
            let _ = tx.send(result);
        });

        println!("Waiting for thread to complete...");
        match rx.recv_timeout(Duration::from_secs(timeout_secs)) {
            Ok(result) => {
                println!("Thread completed successfully");
                // Ensure the thread is cleaned up
                let _ = handle.join();
                Some(result)
            }
            Err(_) => {
                println!("Thread timed out");
                // Timeout occurred
                None
            }
        }
    }

    #[test]
    fn test_automorphism_enumeration_with_timeout() {
        println!("Starting test with cyclic group Z4...");

        // Test Z4 first (simpler case)
        let z4 = create_cyclic_group(4);
        let z4_clone = Arc::clone(&z4);
        let result = run_with_timeout(
            move || {
                println!("Starting Z4 automorphism enumeration");
                let result = enumerate_automorphisms(z4_clone);
                println!("Z4 automorphism enumeration completed");
                result
            },
            30,
        ); // 30 second timeout

        match result {
            Some(Ok(autos)) => {
                println!(
                    "Z4 automorphisms completed successfully with {} automorphisms",
                    autos.len()
                );
                assert_eq!(autos.len(), 2);
            }
            Some(Err(e)) => {
                println!("Z4 test failed with error: {:?}", e);
                panic!("Z4 test failed");
            }
            None => {
                println!("Z4 test timed out after 30 seconds");
                panic!("Z4 test timed out");
            }
        }

        println!("\nStarting test with Boolean algebra...");

        // Test Boolean algebra (more complex case)
        let ba = create_boolean_algebra(4).unwrap();
        let ba_clone = Arc::clone(&ba);
        let result = run_with_timeout(
            move || {
                println!("Starting Boolean algebra automorphism enumeration");
                let result = enumerate_automorphisms(ba_clone);
                println!("Boolean algebra automorphism enumeration completed");
                result
            },
            60,
        ); // 60 second timeout

        match result {
            Some(Ok(autos)) => {
                println!(
                    "Boolean algebra automorphisms completed successfully with {} automorphisms",
                    autos.len()
                );
                assert_eq!(autos.len(), 24);
            }
            Some(Err(e)) => {
                println!("Boolean algebra test failed with error: {:?}", e);
                panic!("Boolean algebra test failed");
            }
            None => {
                println!("Boolean algebra test timed out after 60 seconds");
                panic!("Boolean algebra test timed out");
            }
        }
    }

    #[test]
    fn test_automorphism_enumeration_incremental() {
        println!("Testing automorphism enumeration with increasing sizes...");

        for size in 2..=4 {
            println!("\nTesting Boolean algebra of size {}...", size);
            match create_boolean_algebra(size) {
                Ok(ba) => {
                    let ba_clone = Arc::clone(&ba);
                    let result = run_with_timeout(
                        move || {
                            println!(
                                "Starting Boolean algebra automorphism enumeration for size {}",
                                size
                            );
                            let result = enumerate_automorphisms(ba_clone);
                            println!(
                                "Boolean algebra automorphism enumeration completed for size {}",
                                size
                            );
                            result
                        },
                        30,
                    );

                    match result {
                        Some(Ok(autos)) => {
                            println!("Size {} completed with {} automorphisms", size, autos.len());
                        }
                        Some(Err(e)) => {
                            println!("Size {} failed with error: {:?}", size, e);
                            panic!("Test failed at size {}", size);
                        }
                        None => {
                            println!("Size {} timed out after 30 seconds", size);
                            panic!("Test timed out at size {}", size);
                        }
                    }
                }
                Err(e) => {
                    if size == 3 {
                        // For size 3, we expect an error since Boolean algebras must have size 2^n
                        println!("Size {} failed with expected error: {:?}", size, e);
                    } else {
                        println!("Size {} failed with error: {:?}", size, e);
                        panic!("Test failed at size {}", size);
                    }
                }
            }
        }
    }
}
