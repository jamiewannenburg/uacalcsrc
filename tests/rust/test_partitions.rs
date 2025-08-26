use uacalc_core::prelude::*;

#[test]
fn test_union_find_operations() {
    let mut partition = BasicPartition::new(5);

    // Test initial state
    assert_eq!(partition.num_blocks(), 5);
    assert!(partition.is_zero());

    // Test union operations
    assert!(partition.union_elements(0, 1).unwrap());
    assert_eq!(partition.num_blocks(), 4);
    assert!(partition.same_block(0, 1).unwrap());
    assert!(!partition.same_block(0, 2).unwrap());

    // Test union by rank
    partition.union_elements(2, 3).unwrap();
    partition.union_elements(0, 2).unwrap();
    assert_eq!(partition.num_blocks(), 2);
    assert!(partition.same_block(0, 1).unwrap());
    assert!(partition.same_block(0, 2).unwrap());
    assert!(partition.same_block(0, 3).unwrap());
    assert!(!partition.same_block(0, 4).unwrap());

    // Test path compression
    let rep = partition.representative(3).unwrap();
    assert_eq!(rep, partition.representative(0).unwrap());
}

#[test]
fn test_partition_creation() {
    // Test creation from blocks
    let blocks = vec![vec![0, 1], vec![2, 3], vec![4]];
    let partition = BasicPartition::from_blocks(5, blocks).unwrap();

    assert_eq!(partition.num_blocks(), 3);
    assert!(partition.same_block(0, 1).unwrap());
    assert!(partition.same_block(2, 3).unwrap());
    assert!(!partition.same_block(0, 2).unwrap());
    assert!(!partition.same_block(0, 4).unwrap());

    // Test creation from array
    let array = vec![0, 0, 2, 2, 4];
    let partition2 = BasicPartition::from_array(&array).unwrap();

    assert_eq!(partition2.num_blocks(), 3);
    assert!(partition2.same_block(0, 1).unwrap());
    assert!(partition2.same_block(2, 3).unwrap());
    assert!(!partition2.same_block(0, 2).unwrap());
}

#[test]
fn test_partition_lattice_operations() {
    let size = 4;

    // Create two partitions
    let mut p1 = BasicPartition::new(size);
    p1.union_elements(0, 1).unwrap();
    p1.union_elements(2, 3).unwrap();

    let mut p2 = BasicPartition::new(size);
    p2.union_elements(0, 2).unwrap();
    p2.union_elements(1, 3).unwrap();

    // Test join
    let join = p1.join(&p2).unwrap();
    assert_eq!(join.num_blocks(), 1);
    assert!(join.is_one());

    // Test meet
    let meet = p1.meet(&p2).unwrap();
    assert_eq!(meet.num_blocks(), 4);
    assert!(meet.is_zero());

    // Test refinement
    assert!(p1.is_finer_than(&join).unwrap());
    assert!(meet.is_finer_than(&p1).unwrap());
    assert!(!p1.is_finer_than(&p2).unwrap());
}

#[test]
fn test_partition_properties() {
    let size = 5;
    let partition = BasicPartition::new(size);

    // Test zero partition
    assert!(partition.is_zero());
    assert!(!partition.is_one());
    assert!(partition.is_uniform());

    // Test one partition
    let mut one_partition = BasicPartition::new(size);
    for i in 1..size {
        one_partition.union_elements(0, i).unwrap();
    }
    assert!(!one_partition.is_zero());
    assert!(one_partition.is_one());
    assert!(one_partition.is_uniform());

    // Test uniform partition
    let mut uniform_partition = BasicPartition::new(6);
    uniform_partition.union_elements(0, 1).unwrap();
    uniform_partition.union_elements(2, 3).unwrap();
    uniform_partition.union_elements(4, 5).unwrap();
    assert!(uniform_partition.is_uniform());

    // Test non-uniform partition
    let mut non_uniform_partition = BasicPartition::new(5);
    non_uniform_partition.union_elements(0, 1).unwrap();
    non_uniform_partition.union_elements(2, 3).unwrap();
    non_uniform_partition.union_elements(3, 4).unwrap();
    assert!(!non_uniform_partition.is_uniform());
}

#[test]
fn test_partition_representatives() {
    let mut partition = BasicPartition::new(4);
    partition.union_elements(0, 1).unwrap();
    partition.union_elements(2, 3).unwrap();

    let reps = partition.representatives();
    assert_eq!(reps.len(), 2);
    assert!(reps.contains(&0) || reps.contains(&1));
    assert!(reps.contains(&2) || reps.contains(&3));

    // Test block index
    assert_eq!(partition.block_index(0).unwrap(), 0);
    assert_eq!(partition.block_index(1).unwrap(), 0);
    assert_eq!(partition.block_index(2).unwrap(), 1);
    assert_eq!(partition.block_index(3).unwrap(), 1);
}

#[test]
fn test_partition_blocks() {
    let mut partition = BasicPartition::new(4);
    partition.union_elements(0, 1).unwrap();
    partition.union_elements(2, 3).unwrap();

    let blocks = partition.blocks();
    assert_eq!(blocks.len(), 2);

    // Check that each block contains the right elements
    let mut found_0 = false;
    let mut found_2 = false;

    for block in blocks {
        if block.contains(&0) {
            assert!(block.contains(&1));
            assert!(!block.contains(&2));
            assert!(!block.contains(&3));
            found_0 = true;
        } else if block.contains(&2) {
            assert!(block.contains(&3));
            assert!(!block.contains(&0));
            assert!(!block.contains(&1));
            found_2 = true;
        }
    }

    assert!(found_0);
    assert!(found_2);
}

#[test]
fn test_partition_array_conversion() {
    let size = 4;
    let mut partition = BasicPartition::new(size);
    partition.union_elements(0, 1).unwrap();
    partition.union_elements(2, 3).unwrap();

    // Test to_array
    let array = partition.to_array();
    assert_eq!(array.len(), size);
    assert_eq!(array[0], array[1]); // Same block
    assert_eq!(array[2], array[3]); // Same block
    assert_ne!(array[0], array[2]); // Different blocks

    // Test from_array round trip
    let partition2 = BasicPartition::from_array(&array).unwrap();
    assert_eq!(partition2.num_blocks(), partition.num_blocks());
    assert!(partition2.same_block(0, 1).unwrap());
    assert!(partition2.same_block(2, 3).unwrap());
    assert!(!partition2.same_block(0, 2).unwrap());
}

#[test]
fn test_partition_factory_functions() {
    let size = 5;

    // Test finest partition
    let finest = finest_partition(size);
    assert_eq!(finest.num_blocks(), size);
    assert!(finest.is_zero());

    // Test coarsest partition
    let coarsest = coarsest_partition(size).unwrap();
    assert_eq!(coarsest.num_blocks(), 1);
    assert!(coarsest.is_one());
}

#[test]
fn test_partition_validation() {
    // Test invalid array
    let invalid_array = vec![0, 1, 5]; // 5 >= size
    assert!(BasicPartition::from_array(&invalid_array).is_err());

    // Test invalid blocks
    let invalid_blocks = vec![vec![0, 1], vec![2, 5]]; // 5 >= size
    assert!(BasicPartition::from_blocks(5, invalid_blocks).is_err());
}

#[test]
fn test_partition_performance() {
    let size = 1000;
    let mut partition = BasicPartition::new(size);

    // Test many union operations
    let start = std::time::Instant::now();
    for i in 0..size - 1 {
        partition.union_elements(i, i + 1).unwrap();
    }
    let union_time = start.elapsed();

    assert_eq!(partition.num_blocks(), 1);
    assert!(partition.is_one());

    // Test representative queries
    let start = std::time::Instant::now();
    for _ in 0..1000 {
        partition.representative(0).unwrap();
        partition.representative(size / 2).unwrap();
        partition.representative(size - 1).unwrap();
    }
    let query_time = start.elapsed();

    println!("Union operations: {:?}", union_time);
    println!("Representative queries: {:?}", query_time);

    // Verify path compression is working
    let rep = partition.representative(size - 1).unwrap();
    assert_eq!(rep, partition.representative(0).unwrap());
}

#[test]
fn test_partition_join_blocks() {
    let mut partition = BasicPartition::new(4);
    partition.union_elements(0, 1).unwrap();
    partition.union_elements(2, 3).unwrap();

    // Get representatives
    let rep1 = partition.representative(0).unwrap();
    let rep2 = partition.representative(2).unwrap();

    // Join blocks by representatives
    partition.join_blocks(rep1, rep2).unwrap();

    assert_eq!(partition.num_blocks(), 1);
    assert!(partition.is_one());
}

#[test]
fn test_partition_normalization() {
    let mut partition = BasicPartition::new(4);
    partition.union_elements(1, 0).unwrap(); // Union in reverse order
    partition.union_elements(3, 2).unwrap();

    // Verify representatives are canonical
    let reps = partition.representatives();
    assert_eq!(reps.len(), 2);
    assert!(reps.contains(&0));
    assert!(reps.contains(&2));

    // Verify all elements in a block have the same representative
    assert_eq!(
        partition.representative(0).unwrap(),
        partition.representative(1).unwrap()
    );
    assert_eq!(
        partition.representative(2).unwrap(),
        partition.representative(3).unwrap()
    );
}

#[test]
fn test_partition_serialization() {
    let mut partition = BasicPartition::new(4);
    partition.union_elements(0, 1).unwrap();
    partition.union_elements(2, 3).unwrap();

    // Test serialization
    let serialized = serde_json::to_string(&partition).unwrap();
    let deserialized: BasicPartition = serde_json::from_str(&serialized).unwrap();

    // Verify deserialized partition works correctly
    assert_eq!(deserialized.num_blocks(), 2);
    assert!(deserialized.same_block(0, 1).unwrap());
    assert!(deserialized.same_block(2, 3).unwrap());
    assert!(!deserialized.same_block(0, 2).unwrap());
}

#[test]
fn test_partition_edge_cases() {
    // Test empty partition (should not be allowed)
    assert!(BasicPartition::try_new(0).is_err());

    // Test single element partition
    let partition = BasicPartition::try_new(1).unwrap();
    assert_eq!(partition.num_blocks(), 1);
    assert!(partition.is_zero());
    assert!(partition.is_one());
    assert!(partition.is_uniform());

    // Test large partition
    let size = 10000;
    let mut partition = BasicPartition::try_new(size).unwrap();
    partition.union_elements(0, size - 1).unwrap();
    assert_eq!(partition.num_blocks(), size - 1);
}

#[test]
fn test_partition_error_handling() {
    let partition = BasicPartition::try_new(5).unwrap();

    // Test out of bounds access
    assert!(partition.representative(5).is_err());
    assert!(partition.block(5).is_err());
    assert!(partition.same_block(0, 5).is_err());
    assert!(partition.block_index(5).is_err());

    // Test union with out of bounds elements
    assert!(partition.union_elements(0, 5).is_err());
    assert!(partition.union_elements(5, 0).is_err());
    assert!(partition.union_elements(5, 6).is_err());
}

#[test]
fn test_partition_complex_scenarios() {
    let size = 10;
    let mut partition = BasicPartition::try_new(size).unwrap();

    // Create a complex partition with multiple blocks of different sizes
    partition.union_elements(0, 1).unwrap();
    partition.union_elements(1, 2).unwrap();
    partition.union_elements(3, 4).unwrap();
    partition.union_elements(5, 6).unwrap();
    partition.union_elements(6, 7).unwrap();
    partition.union_elements(7, 8).unwrap();

    // Verify structure
    assert_eq!(partition.num_blocks(), 4);
    assert!(partition.same_block(0, 1).unwrap());
    assert!(partition.same_block(0, 2).unwrap());
    assert!(partition.same_block(3, 4).unwrap());
    assert!(partition.same_block(5, 6).unwrap());
    assert!(partition.same_block(5, 7).unwrap());
    assert!(partition.same_block(5, 8).unwrap());
    assert!(!partition.same_block(0, 3).unwrap());
    assert!(!partition.same_block(0, 5).unwrap());
    assert!(!partition.same_block(0, 9).unwrap());

    // Test that 9 is in its own block
    assert_eq!(partition.block(9).unwrap(), vec![9]);

    // Test representatives
    let reps = partition.representatives();
    assert_eq!(reps.len(), 4);
    assert!(reps.contains(&0));
    assert!(reps.contains(&3));
    assert!(reps.contains(&5));
    assert!(reps.contains(&9));
}
