/*! Tests for the Partition module.

These tests verify that the Rust implementation matches the Java implementation
by comparing outputs with the Java CLI wrapper.
*/

use uacalc::alg::conlat::partition::{Partition, PrintType};
use crate::common::*;
use serde_json::json;

#[test]
fn test_zero_partition() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["zero", "--size", "3"],
        || {
            let partition = Partition::zero(3);
            json!({
                "result": partition.to_string(),
                "universe_size": partition.universe_size(),
                "number_of_blocks": partition.number_of_blocks(),
                "is_zero": partition.is_zero()
            })
        }
    );
}

#[test]
fn test_one_partition() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["one", "--size", "3"],
        || {
            let partition = Partition::one(3);
            json!({
                "result": partition.to_string(),
                "universe_size": partition.universe_size(),
                "number_of_blocks": partition.number_of_blocks(),
                "is_zero": partition.is_zero()
            })
        }
    );
}

#[test]
fn test_from_array() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["from_array", "--array", "[-2,0,-1,-1]"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.to_string(),
                "universe_size": partition.universe_size(),
                "number_of_blocks": partition.number_of_blocks()
            })
        }
    );
}

#[test]
fn test_from_string() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["from_string", "--str", "|0 1|2 3|"],
        || {
            let partition = Partition::from_string("|0 1|2 3|").unwrap();
            json!({
                "result": partition.to_string(),
                "universe_size": partition.universe_size(),
                "number_of_blocks": partition.number_of_blocks()
            })
        }
    );
}

#[test]
fn test_universe_size() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["universe_size", "--partition_array", "[-2,0,-1,-1]"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.universe_size()
            })
        }
    );
}

#[test]
fn test_number_of_blocks() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["number_of_blocks", "--partition_array", "[-2,0,-1,-1]"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.number_of_blocks()
            })
        }
    );
}

#[test]
fn test_is_related() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["is_related", "--partition_array", "[-2,0,-1,-1]", "--i", "0", "--j", "1"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.is_related(0, 1)
            })
        }
    );
}

#[test]
fn test_representative() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["representative", "--partition_array", "[-2,0,-1,-1]", "--i", "1"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.representative(1)
            })
        }
    );
}

#[test]
fn test_is_representative() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["is_representative", "--partition_array", "[-2,0,-1,-1]", "--i", "0"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.is_representative(0)
            })
        }
    );
}

#[test]
fn test_representatives() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["representatives", "--partition_array", "[-2,0,-1,-1]"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.representatives()
            })
        }
    );
}

#[test]
fn test_block_index() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["block_index", "--partition_array", "[-2,0,-1,-1]", "--i", "1"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.block_index(1).unwrap()
            })
        }
    );
}

#[test]
fn test_get_blocks() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["get_blocks", "--partition_array", "[-2,0,-1,-1]"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.get_blocks()
            })
        }
    );
}

#[test]
fn test_join_blocks() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["join_blocks", "--partition_array", "[-1,-1,-1,-1]", "--r", "0", "--s", "1"],
        || {
            let mut partition = Partition::new(vec![-1, -1, -1, -1]).unwrap();
            partition.join_blocks(0, 1);
            json!({
                "result": partition.to_string()
            })
        }
    );
}

#[test]
fn test_join() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["join", "--partition1_array", "[-2,0,-1,-1]", "--partition2_array", "[-1,-1,-2,2]"],
        || {
            let partition1 = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            let partition2 = Partition::new(vec![-1, -1, -2, 2]).unwrap();
            let join = partition1.join(&partition2).unwrap();
            json!({
                "result": join.to_string()
            })
        }
    );
}

#[test]
fn test_meet() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["meet", "--partition1_array", "[-2,0,-1,-1]", "--partition2_array", "[-1,-1,-2,2]"],
        || {
            let partition1 = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            let partition2 = Partition::new(vec![-1, -1, -2, 2]).unwrap();
            let meet = partition1.meet(&partition2).unwrap();
            json!({
                "result": meet.to_string()
            })
        }
    );
}

#[test]
fn test_leq() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["leq", "--partition1_array", "[-2,0,-1,-1]", "--partition2_array", "[-4,0,0,0]"],
        || {
            let partition1 = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            let partition2 = Partition::new(vec![-4, 0, 0, 0]).unwrap();
            json!({
                "result": partition1.leq(&partition2)
            })
        }
    );
}

#[test]
fn test_normalize() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["normalize", "--partition_array", "[-2,0,-1,-1]"],
        || {
            let mut partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            partition.normalize();
            json!({
                "result": partition.to_string()
            })
        }
    );
}

#[test]
fn test_is_zero() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["is_zero", "--partition_array", "[-1,-1,-1,-1]"],
        || {
            let partition = Partition::new(vec![-1, -1, -1, -1]).unwrap();
            json!({
                "result": partition.is_zero()
            })
        }
    );
}

#[test]
fn test_is_uniform() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["is_uniform", "--partition_array", "[-2,0,-2,2]"],
        || {
            let partition = Partition::new(vec![-2, 0, -2, 2]).unwrap();
            json!({
                "result": partition.is_uniform()
            })
        }
    );
}

#[test]
fn test_is_initial_lex_representative() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["is_initial_lex_representative", "--partition_array", "[-2,0,-1,-1]"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.is_initial_lex_representative()
            })
        }
    );
}

#[test]
fn test_to_array() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["to_array", "--partition_array", "[-2,0,-1,-1]"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.to_array()
            })
        }
    );
}

#[test]
fn test_rank() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["rank", "--partition_array", "[-2,0,-1,-1]"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.rank()
            })
        }
    );
}

#[test]
fn test_to_string() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["to_string", "--partition_array", "[-2,0,-1,-1]"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.to_string()
            })
        }
    );
}

#[test]
fn test_to_string_with_type() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["to_string_with_type", "--partition_array", "[-2,0,-1,-1]", "--type", "block"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.to_string_with_print_type(PrintType::Block)
            })
        }
    );
}

#[test]
fn test_to_string_with_max_len() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["to_string_with_max_len", "--partition_array", "[-2,0,-1,-1]", "--max_len", "50"],
        || {
            let partition = Partition::new(vec![-2, 0, -1, -1]).unwrap();
            json!({
                "result": partition.to_string_with_max_len(50)
            })
        }
    );
}

#[test]
fn test_basic_functionality() {
    let config = TestConfig::default();
    
    // Test a simple join operation that can be compared with Java
    compare_with_java!(
        config,
        "java_wrapper.src.alg.conlat.PartitionWrapper",
        ["join", "--partition1_array", "[-1,-1,-1,-1]", "--partition2_array", "[-4,0,0,0]"],
        || {
            let p1 = Partition::new(vec![-1, -1, -1, -1]).unwrap();
            let p2 = Partition::new(vec![-4, 0, 0, 0]).unwrap();
            let join = p1.join(&p2).unwrap();
            json!({
                "result": join.to_string()
            })
        }
    );
}
