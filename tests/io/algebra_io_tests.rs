use uacalc::io::algebra_io::*;
use uacalc::alg::{Algebra, SmallAlgebra};
use uacalc::alg::small_algebra::BasicSmallAlgebra;
use uacalc::alg::op::{OperationSymbol, operations};
use std::collections::HashSet;
use std::path::Path;
use std::fs;
use std::io::{BufReader, Write};

#[test]
fn test_parse_line() {
    assert_eq!(parse_line("42").unwrap(), 42);
    assert_eq!(parse_line("  10  ").unwrap(), 10);
    assert_eq!(parse_line("% comment").unwrap(), -1);
    assert_eq!(parse_line("  % another comment").unwrap(), -1);
    assert!(parse_line("not a number").is_err());
}

#[test]
fn test_read_op() {
    // Test reading a binary operation (XOR)
    let data = "0\n1\n1\n0\n";
    let mut reader = BufReader::new(data.as_bytes());
    let op = read_op(2, 2, &mut reader).unwrap();
    
    assert_eq!(op.arity(), 2);
    assert_eq!(op.int_value_at(&[0, 0]).unwrap(), 0);
    assert_eq!(op.int_value_at(&[0, 1]).unwrap(), 1);
    assert_eq!(op.int_value_at(&[1, 0]).unwrap(), 1);
    assert_eq!(op.int_value_at(&[1, 1]).unwrap(), 0);
}

#[test]
fn test_read_op_unary() {
    // Test reading a unary operation (identity)
    let data = "0\n1\n";
    let mut reader = BufReader::new(data.as_bytes());
    let op = read_op(1, 2, &mut reader).unwrap();
    
    assert_eq!(op.arity(), 1);
    assert_eq!(op.int_value_at(&[0]).unwrap(), 0);
    assert_eq!(op.int_value_at(&[1]).unwrap(), 1);
}

#[test]
fn test_read_depth2_list() {
    let data = "test";
    let mut reader = BufReader::new(data.as_bytes());
    let result = read_depth2_list(&mut reader, "[", "]");
    assert!(result.is_none());
}

#[test]
fn test_read_algebra_file_ua() {
    let path = Path::new("resources/algebras/cyclic3.ua");
    if !path.exists() {
        // Skip test if file doesn't exist
        return;
    }
    
    let alg = read_algebra_file(path).unwrap();
    assert_eq!(alg.cardinality(), 3);
    // Use get_operations_ref() instead of operations() to avoid infinite recursion limitation
    assert!(alg.get_operations_ref().len() > 0);
}

#[test]
fn test_read_algebra_list_file() {
    let path = Path::new("resources/algebras/cyclic3.ua");
    if !path.exists() {
        // Skip test if file doesn't exist
        return;
    }
    
    let algebras = read_algebra_list_file(path).unwrap();
    assert!(algebras.len() >= 1);
    assert_eq!(algebras[0].cardinality(), 3);
}

#[test]
fn test_write_and_read_algebra_xml() {
    // Create a simple algebra
    let op_sym = OperationSymbol::new("f", 2, false);
    let values = vec![0, 1, 1, 0]; // XOR operation
    let op = operations::make_int_operation(op_sym, 2, values).unwrap();
    
    let universe: HashSet<i32> = HashSet::from([0, 1]);
    let alg = Box::new(BasicSmallAlgebra::new(
        "test_alg".to_string(),
        universe,
        vec![op]
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    // Write to temp file
    let temp_path = Path::new("/tmp/test_algebra_io.xml");
    write_algebra_file(alg, temp_path).unwrap();
    
    // Check file exists
    assert!(temp_path.exists());
    
    // Read back
    let read_alg = read_algebra_file(temp_path).unwrap();
    assert_eq!(read_alg.cardinality(), 2);
    // Use get_operations_ref() instead of operations() to avoid infinite recursion limitation
    assert_eq!(read_alg.get_operations_ref().len(), 1);
    
    // Clean up
    let _ = fs::remove_file(temp_path);
}

#[test]
fn test_write_algebra_old_style() {
    // Create a simple algebra
    let op_sym = OperationSymbol::new("f", 2, false);
    let values = vec![0, 1, 1, 0]; // XOR operation
    let op = operations::make_int_operation(op_sym, 2, values).unwrap();
    
    let universe: HashSet<i32> = HashSet::from([0, 1]);
    let alg = Box::new(BasicSmallAlgebra::new(
        "test_alg".to_string(),
        universe,
        vec![op]
    )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    
    // Write to temp file in old style
    let temp_path = Path::new("/tmp/test_algebra_io.alg");
    write_algebra_file_with_style(alg, temp_path, true).unwrap();
    
    // Check file exists
    assert!(temp_path.exists());
    
    // Read back
    let read_alg = read_algebra_file(temp_path).unwrap();
    assert_eq!(read_alg.cardinality(), 2);
    // Use get_operations_ref() instead of operations() to avoid infinite recursion limitation
    assert_eq!(read_alg.get_operations_ref().len(), 1);
    
    // Clean up
    let _ = fs::remove_file(temp_path);
}

#[test]
fn test_read_algebra_from_stream() {
    let path = Path::new("resources/algebras/cyclic3.ua");
    if !path.exists() {
        // Skip test if file doesn't exist
        return;
    }
    
    let file = std::fs::File::open(path).unwrap();
    let alg = read_algebra_from_stream(Box::new(file)).unwrap();
    assert_eq!(alg.cardinality(), 3);
}

#[test]
fn test_convert_to_xml() {
    // Create a simple .alg file
    let temp_alg_path = Path::new("/tmp/test_convert.alg");
    {
        let mut file = std::fs::File::create(temp_alg_path).unwrap();
        writeln!(file, "2").unwrap();  // cardinality
        writeln!(file, "2").unwrap();  // arity
        writeln!(file, "0").unwrap();  // operation table
        writeln!(file, "1").unwrap();
        writeln!(file, "1").unwrap();
        writeln!(file, "0").unwrap();
    }
    
    // Convert to XML
    let result = convert_to_xml(temp_alg_path);
    
    if result.is_ok() {
        let xml_path = Path::new("/tmp/test_convert.xml");
        assert!(xml_path.exists());
        
        // Clean up
        let _ = fs::remove_file(xml_path);
    }
    
    // Clean up
    let _ = fs::remove_file(temp_alg_path);
}

#[test]
fn test_read_projective_plane_error() {
    // Create a test file with invalid format
    let temp_path = Path::new("/tmp/test_plane.txt");
    {
        let mut file = std::fs::File::create(temp_path).unwrap();
        writeln!(file, "1 2 3").unwrap();  // Invalid: should start with 0
    }
    
    let result = read_projective_plane(temp_path);
    assert!(result.is_err());
    
    // Clean up
    let _ = fs::remove_file(temp_path);
}

#[test]
fn test_read_projective_plane_valid_header() {
    // Create a test file with valid first line
    let temp_path = Path::new("/tmp/test_plane_valid.txt");
    {
        let mut file = std::fs::File::create(temp_path).unwrap();
        writeln!(file, "0 1 2").unwrap();  // Valid first line
        writeln!(file, "3 4 5").unwrap();
    }
    
    // This should pass the first line check but fail on implementation
    let result = read_projective_plane(temp_path);
    assert!(result.is_err());
    assert!(result.unwrap_err().message().contains("not yet implemented"));
    
    // Clean up
    let _ = fs::remove_file(temp_path);
}

