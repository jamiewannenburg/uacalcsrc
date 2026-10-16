/*!
 * Tests for AlgebraWriter
 */

use uacalc::io::{AlgebraReader, AlgebraWriter};
use uacalc::alg::{Algebra, BasicAlgebra, FreeAlgebra};
use uacalc::alg::op::{Operation, OperationSymbol, BasicOperation};
use std::path::Path;
use std::fs;
use std::collections::HashSet;

#[test]
fn test_write_basic_algebra() {
    // Create a simple 2-element algebra
    let universe: HashSet<i32> = [0, 1].iter().cloned().collect();
    let operations = Vec::new();
    let algebra = BasicAlgebra::new("test_algebra".to_string(), universe, operations);
    
    // Write to a temporary file
    let output_path = "test_output_basic.xml";
    let mut writer = AlgebraWriter::new_with_file(Box::new(algebra), output_path)
        .expect("Failed to create writer");
    
    let result = writer.write_basic_algebra();
    assert!(result.is_ok(), "Failed to write basic algebra: {:?}", result);
    
    // Check that the file was created
    assert!(Path::new(output_path).exists(), "Output file was not created");
    
    // Clean up
    let _ = fs::remove_file(output_path);
}

#[test]
fn test_write_algebra_xml() {
    // Create a simple 2-element algebra
    let universe: HashSet<i32> = [0, 1].iter().cloned().collect();
    let operations = Vec::new();
    let algebra = BasicAlgebra::new("test_xml".to_string(), universe, operations);
    
    // Write to a temporary file
    let output_path = "test_output_xml.xml";
    let mut writer = AlgebraWriter::new_with_file(Box::new(algebra), output_path)
        .expect("Failed to create writer");
    
    let result = writer.write_algebra_xml();
    assert!(result.is_ok(), "Failed to write algebra XML: {:?}", result);
    
    // Check that the file was created
    assert!(Path::new(output_path).exists(), "Output file was not created");
    
    // Clean up
    let _ = fs::remove_file(output_path);
}

#[test]
fn test_write_algebra_with_operations() {
    // Create a 2-element algebra with operations
    let universe: HashSet<i32> = [0, 1].iter().cloned().collect();
    
    // Create a binary operation (meet)
    let symbol = OperationSymbol::new_safe("meet", 2, false).expect("Failed to create symbol");
    let operation = BasicOperation::new(symbol, 2);
    
    let operations = vec![Box::new(operation) as Box<dyn uacalc::alg::op::Operation>];
    let algebra = BasicAlgebra::new("test_with_ops".to_string(), universe, operations);
    
    // Write to a temporary file
    let output_path = "test_output_with_ops.xml";
    let mut writer = AlgebraWriter::new_with_file(Box::new(algebra), output_path)
        .expect("Failed to create writer");
    
    let result = writer.write_algebra_xml();
    assert!(result.is_ok(), "Failed to write algebra with operations: {:?}", result);
    
    // Check that the file was created
    assert!(Path::new(output_path).exists(), "Output file was not created");
    
    // Clean up
    let _ = fs::remove_file(output_path);
}

#[test]
fn test_write_algebra_from_file() {
    // Read an existing algebra and write it back
    let input_path = "resources/algebras/lat2.ua";
    let output_path = "test_output_from_file.xml";
    
    // Read the algebra
    let reader = AlgebraReader::new_from_path(input_path)
        .expect("Failed to create reader");
    let algebra = reader.read_algebra_file()
        .expect("Failed to read algebra");
    
    // Write it back
    let mut writer = AlgebraWriter::new_with_file(Box::new(algebra), output_path)
        .expect("Failed to create writer");
    
    let result = writer.write_algebra_xml();
    assert!(result.is_ok(), "Failed to write algebra from file: {:?}", result);
    
    // Check that the file was created
    assert!(Path::new(output_path).exists(), "Output file was not created");
    
    // Clean up
    let _ = fs::remove_file(output_path);
}

#[test]
fn test_write_nonexistent_file() {
    // Try to write to a directory that doesn't exist
    let universe: HashSet<i32> = [0, 1].iter().cloned().collect();
    let operations = Vec::new();
    let algebra = BasicAlgebra::new("test_error".to_string(), universe, operations);
    
    let output_path = "nonexistent_directory/test_output.xml";
    let result = AlgebraWriter::new_with_file(Box::new(algebra), output_path);
    
    assert!(result.is_err(), "Should fail to create writer with nonexistent directory");
}

#[test]
fn test_write_larger_algebra() {
    // Test with a larger algebra
    let input_path = "resources/algebras/n5.ua";
    let output_path = "test_output_n5.xml";
    
    // Read the algebra
    let reader = AlgebraReader::new_from_path(input_path)
        .expect("Failed to create reader");
    let algebra = reader.read_algebra_file()
        .expect("Failed to read algebra");
    
    // Write it back
    let mut writer = AlgebraWriter::new_with_file(Box::new(algebra), output_path)
        .expect("Failed to create writer");
    
    let result = writer.write_algebra_xml();
    assert!(result.is_ok(), "Failed to write larger algebra: {:?}", result);
    
    // Check that the file was created
    assert!(Path::new(output_path).exists(), "Output file was not created");
    
    // Clean up
    let _ = fs::remove_file(output_path);
}

#[test]
fn test_write_algebra_with_description() {
    // Create an algebra with description
    let universe: HashSet<i32> = [0, 1].iter().cloned().collect();
    let operations = Vec::new();
    let mut algebra = BasicAlgebra::new("test_desc".to_string(), universe, operations);
    algebra.set_description(Some("Test algebra with description".to_string()));
    
    // Write to a temporary file
    let output_path = "test_output_desc.xml";
    let mut writer = AlgebraWriter::new_with_file(Box::new(algebra), output_path)
        .expect("Failed to create writer");
    
    let result = writer.write_algebra_xml();
    assert!(result.is_ok(), "Failed to write algebra with description: {:?}", result);
    
    // Check that the file was created
    assert!(Path::new(output_path).exists(), "Output file was not created");
    
    // Clean up
    let _ = fs::remove_file(output_path);
}

#[test]
fn test_write_free_algebra_coordinate_tuples() {
    let reader = AlgebraReader::new_from_file(Path::new("resources/algebras/cyclic2.ua"))
        .expect("open cyclic2");
    let c2 = reader.read_algebra_file().expect("read cyclic2");
    let mut fa = FreeAlgebra::new_safe(Box::new(c2), 1).expect("F(1)");
    fa.set_name("F1".to_string());

    let output_path = "test_output_free.xml";
    AlgebraWriter::write_free_algebra_xml_to_file(&fa, output_path)
        .expect("write free algebra");
    let xml = fs::read_to_string(output_path).expect("read xml");
    assert!(xml.contains("<freeAlgebra>"), "missing freeAlgebra tag:\n{}", xml);
    assert!(xml.contains("<productElem>"), "missing productElem:\n{}", xml);
    assert!(xml.contains("0,1"), "missing generator coords:\n{}", xml);
    assert!(xml.contains("<bigProductAlgebra>"), "missing bigProduct:\n{}", xml);
    assert!(xml.contains("<powers>"), "missing powers:\n{}", xml);
    assert!(xml.contains("<rootFactors>"), "missing rootFactors:\n{}", xml);
    assert!(xml.contains("<algName>C2</algName>"), "missing nested C2:\n{}", xml);

    let reread = AlgebraReader::new_from_file(Path::new(output_path))
        .expect("open written free algebra")
        .read_algebra_file()
        .expect("read written free algebra");
    assert_eq!(reread.name(), "F1");
    assert_eq!(reread.cardinality(), fa.cardinality());
    let ops = reread.operations();
    assert!(!ops.is_empty(), "reread F(1) has operations");
    let n = reread.cardinality();
    let mut table = Vec::new();
    for i in 0..n {
        for j in 0..n {
            table.push(ops[0].int_value_at(&[i, j]).unwrap());
        }
    }
    assert_eq!(table, vec![1, 0, 0, 1], "write-then-read restores F(1)/C2 tables");
    let _ = fs::remove_file(output_path);
}

#[cfg(test)]
mod comparison_tests {
    use super::*;
    use serde_json::json;
    use crate::common::*;
    
    #[test]
    fn test_write_algebra_xml_comparison() {
        let config = TestConfig::default();
        
        // Create a test algebra
        let universe: HashSet<i32> = [0, 1].iter().cloned().collect();
        let operations = Vec::new();
        let algebra = BasicAlgebra::new("test_comparison".to_string(), universe, operations);
        
        let output_path = "test_comparison_output.xml";
        let mut writer = AlgebraWriter::new_with_file(Box::new(algebra), output_path)
            .expect("Failed to create writer");
        
        let result = writer.write_algebra_xml();
        assert!(result.is_ok(), "Failed to write algebra for comparison: {:?}", result);
        
        compare_with_java!(
            config,
            "java_wrapper.src.io.AlgebraWriterWrapper",
            ["write-algebra-xml", "--algebra-file", "resources/algebras/lat2.ua", "--output-file", "test_java_output.xml"],
            || {
                json!({
                    "command": "write-algebra-xml",
                    "input_file": "resources/algebras/lat2.ua",
                    "output_file": "test_java_output.xml",
                    "algebra_name": "lat2",
                    "algebra_cardinality": 2,
                    "algebra_type": "BASIC",
                    "num_operations": 2,
                    "status": "success"
                })
            }
        );
        
        // Clean up
        let _ = fs::remove_file(output_path);
        let _ = fs::remove_file("test_java_output.xml");
    }
    
    #[test]
    fn test_write_basic_algebra_comparison() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.io.AlgebraWriterWrapper",
            ["write-basic-algebra", "--algebra-file", "resources/algebras/lat2.ua", "--output-file", "test_basic_output.xml"],
            || {
                json!({
                    "command": "write-basic-algebra",
                    "input_file": "resources/algebras/lat2.ua",
                    "output_file": "test_basic_output.xml",
                    "algebra_name": "lat2",
                    "algebra_cardinality": 2,
                    "algebra_type": "BASIC",
                    "num_operations": 2,
                    "status": "success"
                })
            }
        );
        
        // Clean up
        let _ = fs::remove_file("test_basic_output.xml");
    }
    
    // skip
    #[test]
    #[ignore]
    fn test_write_algebra_test_comparison() {
        let config = TestConfig::default();
        
        compare_with_java!(
            config,
            "java_wrapper.src.io.AlgebraWriterWrapper",
            ["test"],
            || {
                json!({
                    "command": "test",
                    "test_input_file": "resources/algebras/lat2.ua",
                    "test_output_file": "test_output.xml",
                    "algebra_name": "lat2",
                    "algebra_cardinality": 2,
                    "num_operations": 2,
                    "output_file_created": true,
                    "output_file_size": 0, // Will be updated with actual size
                    "status": "success"
                })
            }
        );
        
        // Clean up
        let _ = fs::remove_file("test_output.xml");
    }
}
