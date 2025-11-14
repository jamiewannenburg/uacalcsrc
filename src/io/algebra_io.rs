use std::fs::File;
use std::io::{BufRead, BufReader, Read, Write};
use std::path::Path;
use crate::alg::{SmallAlgebra, Algebra};
use crate::alg::small_algebra::BasicAlgebra;
use crate::alg::op::{Operation, OperationSymbol, operations};
use crate::io::{AlgebraReader, AlgebraWriter, Mace4Reader, ExtFileFilter, BadAlgebraFileException};
use crate::util::horner;
use std::collections::HashSet;

/// Parse a line as a single int, returning -1 for comments.
/// 
/// Lines starting with "%" are treated as comments and return -1.
/// 
/// # Arguments
/// * `line` - The line to parse
/// 
/// # Returns
/// * `Ok(i32)` - The parsed integer, or -1 for comments
/// * `Err(String)` - If the line cannot be parsed as an integer
/// 
/// # Examples
/// ```
/// use uacalc::io::algebra_io::parse_line;
/// 
/// assert_eq!(parse_line("42").unwrap(), 42);
/// assert_eq!(parse_line("% comment").unwrap(), -1);
/// assert_eq!(parse_line("  10  ").unwrap(), 10);
/// ```
pub fn parse_line(line: &str) -> Result<i32, String> {
    let trimmed = line.trim();
    if trimmed.starts_with('%') {
        return Ok(-1);
    }
    trimmed.parse::<i32>()
        .map_err(|e| format!("Failed to parse line as integer: {}", e))
}

/// Read an algebra from a file path.
/// 
/// Supports multiple file formats:
/// - .ua, .xml - XML format (via AlgebraReader)
/// - .m4 - Mace4 format (via Mace4Reader)
/// - .alg - Legacy text format
/// 
/// # Arguments
/// * `path` - The file path to read from
/// 
/// # Returns
/// * `Ok(Box<dyn SmallAlgebra>)` - The parsed algebra
/// * `Err(BadAlgebraFileException)` - If the file cannot be read or parsed
/// 
/// # Examples
/// ```
/// use uacalc::io::algebra_io::read_algebra_file;
/// use std::path::Path;
/// 
/// let path = Path::new("resources/algebras/cyclic3.ua");
/// if path.exists() {
///     let alg = read_algebra_file(path).unwrap();
///     assert_eq!(alg.cardinality(), 3);
/// }
/// ```
pub fn read_algebra_file(path: &Path) -> Result<Box<dyn SmallAlgebra<UniverseItem = i32>>, BadAlgebraFileException> {
    let ext = ExtFileFilter::get_extension(path);
    
    if let Some(ext_str) = ext {
        let ext_lower = ext_str.to_lowercase();
        
        // Check for UA/XML format
        if ext_lower == "ua" || ext_lower == "xml" {
            let reader = AlgebraReader::new_from_file(path)
                .map_err(|e| BadAlgebraFileException::new(&e))?;
            let alg = reader.read_algebra_file()
                .map_err(|e| BadAlgebraFileException::new(&e))?;
            return Ok(Box::new(alg));
        }
        
        // Check for Mace4 format
        if ext_lower == "m4" {
            let file = File::open(path)
                .map_err(|e| BadAlgebraFileException::new(&format!("Failed to open file: {}", e)))?;
            let mut reader = Mace4Reader::new(Box::new(file))
                .map_err(|e| BadAlgebraFileException::new(&e))?;
            return reader.parse_algebra()
                .and_then(|opt| opt.ok_or_else(|| BadAlgebraFileException::new("No algebra found in file")));
        }
        
        // Check for legacy .alg format
        if ext_lower == "alg" {
            return read_alg_format(path);
        }
    }
    
    // Default: try legacy .alg format
    read_alg_format(path)
}

/// Read an algebra from a legacy .alg format file.
/// 
/// The .alg format is:
/// - First line: cardinality (size)
/// - Following lines: for each operation, arity followed by operation table
/// 
/// # Arguments
/// * `path` - The file path to read from
/// 
/// # Returns
/// * `Ok(Box<dyn SmallAlgebra>)` - The parsed algebra
/// * `Err(BadAlgebraFileException)` - If the file cannot be read or parsed
fn read_alg_format(path: &Path) -> Result<Box<dyn SmallAlgebra<UniverseItem = i32>>, BadAlgebraFileException> {
    let file = File::open(path)
        .map_err(|e| BadAlgebraFileException::new(&format!("Failed to open file: {}", e)))?;
    let mut reader = BufReader::new(file);
    
    let mut line = String::new();
    reader.read_line(&mut line)
        .map_err(|e| BadAlgebraFileException::new(&format!("Failed to read first line: {}", e)))?;
    
    if line.trim().is_empty() {
        return Err(BadAlgebraFileException::new("Nothing in the file"));
    }
    
    let size = line.trim().parse::<i32>()
        .map_err(|e| BadAlgebraFileException::new(&format!("Failed to parse size: {}", e)))?;
    
    let mut operations = Vec::new();
    
    loop {
        line.clear();
        let bytes_read = reader.read_line(&mut line)
            .map_err(|e| BadAlgebraFileException::new(&format!("Failed to read line: {}", e)))?;
        
        if bytes_read == 0 {
            break; // EOF
        }
        
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        
        let arity = trimmed.parse::<i32>()
            .map_err(|e| BadAlgebraFileException::new(&format!("Failed to parse arity: {}", e)))?;
        
        let op = read_op(arity, size, &mut reader)?;
        operations.push(op);
    }
    
    let name = path.file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("algebra")
        .to_string();
    
    let universe: HashSet<i32> = (0..size).collect();
    let alg = BasicAlgebra::new(name, universe, operations);
    Ok(Box::new(alg))
}

/// Read an algebra from an input stream.
/// 
/// Assumes XML format and uses AlgebraReader.
/// 
/// # Arguments
/// * `stream` - The input stream to read from
/// 
/// # Returns
/// * `Ok(Box<dyn SmallAlgebra>)` - The parsed algebra
/// * `Err(BadAlgebraFileException)` - If the stream cannot be read or parsed
/// 
/// # Examples
/// ```
/// use uacalc::io::algebra_io::read_algebra_from_stream;
/// use std::fs::File;
/// 
/// let path = "resources/algebras/cyclic3.ua";
/// if std::path::Path::new(path).exists() {
///     let file = File::open(path).unwrap();
///     let alg = read_algebra_from_stream(Box::new(file)).unwrap();
///     assert_eq!(alg.cardinality(), 3);
/// }
/// ```
pub fn read_algebra_from_stream(stream: Box<dyn Read>) -> Result<Box<dyn SmallAlgebra<UniverseItem = i32>>, BadAlgebraFileException> {
    // Convert Box<dyn Read> to Vec<u8>
    let mut data = Vec::new();
    let mut reader = std::io::BufReader::new(stream);
    reader.read_to_end(&mut data)
        .map_err(|e| BadAlgebraFileException::new(&format!("Failed to read stream: {}", e)))?;
    
    let alg_reader = AlgebraReader::new_from_stream(data)
        .map_err(|e| BadAlgebraFileException::new(&e))?;
    let alg = alg_reader.read_algebra_from_stream()
        .map_err(|e| BadAlgebraFileException::new(&e))?;
    Ok(Box::new(alg))
}

/// Read a list of algebras from a file.
/// 
/// Supports multiple file formats:
/// - .ua, .xml - XML format (via AlgebraReader)
/// - .m4 - Mace4 format (via Mace4Reader)
/// - .alg - Legacy text format (returns single algebra in list)
/// 
/// # Arguments
/// * `path` - The file path to read from
/// 
/// # Returns
/// * `Ok(Vec<Box<dyn SmallAlgebra>>)` - The list of parsed algebras
/// * `Err(BadAlgebraFileException)` - If the file cannot be read or parsed
/// 
/// # Examples
/// ```
/// use uacalc::io::algebra_io::read_algebra_list_file;
/// use std::path::Path;
/// 
/// let path = Path::new("resources/algebras/cyclic3.ua");
/// if path.exists() {
///     let algebras = read_algebra_list_file(path).unwrap();
///     assert!(algebras.len() >= 1);
/// }
/// ```
pub fn read_algebra_list_file(path: &Path) -> Result<Vec<Box<dyn SmallAlgebra<UniverseItem = i32>>>, BadAlgebraFileException> {
    let ext = ExtFileFilter::get_extension(path);
    
    if let Some(ext_str) = ext {
        let ext_lower = ext_str.to_lowercase();
        
        // For .alg files, return single algebra in a list
        if ext_lower == "alg" {
            let alg = read_algebra_file(path)?;
            return Ok(vec![alg]);
        }
        
        // Check for UA/XML format
        if ext_lower == "ua" || ext_lower == "xml" {
            let reader = AlgebraReader::new_from_file(path)
                .map_err(|e| BadAlgebraFileException::new(&e))?;
            let algs = reader.read_algebra_list_file()
                .map_err(|e| BadAlgebraFileException::new(&e))?;
            return Ok(algs.into_iter().map(|alg| Box::new(alg) as Box<dyn SmallAlgebra<UniverseItem = i32>>).collect());
        }
        
        // Check for Mace4 format
        if ext_lower == "m4" {
            let file = File::open(path)
                .map_err(|e| BadAlgebraFileException::new(&format!("Failed to open file: {}", e)))?;
            let mut reader = Mace4Reader::new(Box::new(file))
                .map_err(|e| BadAlgebraFileException::new(&e))?;
            return reader.parse_algebra_list();
        }
    }
    
    Err(BadAlgebraFileException::new("Unsupported file format"))
}

/// Read a single algebra from an input stream.
/// 
/// Assumes XML format and uses AlgebraReader.
/// 
/// # Arguments
/// * `stream` - The input stream to read from
/// 
/// # Returns
/// * `Ok(Box<dyn SmallAlgebra>)` - The parsed algebra
/// * `Err(BadAlgebraFileException)` - If the stream cannot be read or parsed
/// 
/// # Examples
/// ```
/// use uacalc::io::algebra_io::read_algebra_list_from_stream;
/// use std::fs::File;
/// 
/// let path = "resources/algebras/cyclic3.ua";
/// if std::path::Path::new(path).exists() {
///     let file = File::open(path).unwrap();
///     let alg = read_algebra_list_from_stream(Box::new(file)).unwrap();
///     assert_eq!(alg.cardinality(), 3);
/// }
/// ```
pub fn read_algebra_list_from_stream(stream: Box<dyn Read>) -> Result<Box<dyn SmallAlgebra<UniverseItem = i32>>, BadAlgebraFileException> {
    read_algebra_from_stream(stream)
}

/// Read an operation from a buffered reader.
/// 
/// Reads an operation table from the legacy .alg format.
/// The operation table has `size^arity` entries, one per line.
/// 
/// # Arguments
/// * `arity` - The arity of the operation
/// * `size` - The cardinality of the algebra
/// * `reader` - The buffered reader to read from
/// 
/// # Returns
/// * `Ok(Box<dyn Operation>)` - The parsed operation
/// * `Err(BadAlgebraFileException)` - If the operation cannot be read or parsed
/// 
/// # Examples
/// ```
/// use uacalc::io::algebra_io::read_op;
/// use std::io::BufReader;
/// 
/// let data = "0\n1\n1\n0\n";
/// let mut reader = BufReader::new(data.as_bytes());
/// let op = read_op(2, 2, &mut reader).unwrap();
/// assert_eq!(op.arity(), 2);
/// ```
pub fn read_op<R: BufRead>(arity: i32, size: i32, reader: &mut R) -> Result<Box<dyn Operation>, BadAlgebraFileException> {
    let mut h = 1;
    for _ in 0..arity {
        h *= size;
    }
    
    let mut values = vec![0; h as usize];
    for i in 0..h {
        let mut line = String::new();
        reader.read_line(&mut line)
            .map_err(|e| BadAlgebraFileException::new(&format!("Failed to read line: {}", e)))?;
        
        if line.trim().is_empty() {
            return Err(BadAlgebraFileException::new("Bad file: unexpected end of operation table"));
        }
        
        values[i as usize] = line.trim().parse::<i32>()
            .map_err(|e| BadAlgebraFileException::new(&format!("Failed to parse value: {}", e)))?;
    }
    
    let op_sym = OperationSymbol::get_operation_symbol(arity);
    operations::make_int_operation(op_sym, size, values)
        .map_err(|e| BadAlgebraFileException::new(&e))
}

/// Read a depth-2 list (unimplemented).
/// 
/// This function is not implemented in the Java version and returns None.
/// 
/// # Arguments
/// * `_reader` - The buffered reader (unused)
/// * `_start` - The start delimiter (unused)
/// * `_end` - The end delimiter (unused)
/// 
/// # Returns
/// * `None` - Always returns None
pub fn read_depth2_list<R: BufRead>(_reader: &mut R, _start: &str, _end: &str) -> Option<Vec<Vec<i32>>> {
    None
}

/// Convert a legacy .alg file to XML format.
/// 
/// Reads the input file and writes an XML file with the same name but .xml extension.
/// 
/// # Arguments
/// * `path` - The file path to convert
/// 
/// # Returns
/// * `Ok(())` - If conversion succeeds
/// * `Err(BadAlgebraFileException)` - If conversion fails
/// 
/// # Examples
/// ```
/// use uacalc::io::algebra_io::convert_to_xml;
/// use std::path::Path;
/// 
/// // This example requires a valid .alg file
/// // convert_to_xml(Path::new("example.alg")).unwrap();
/// ```
pub fn convert_to_xml(path: &Path) -> Result<(), BadAlgebraFileException> {
    let (name, ext) = ExtFileFilter::split_off_extension(path);
    
    if let (Some(basename), Some(ext_str)) = (name, ext) {
        if ext_str.to_lowercase() == "alg" {
            let alg = read_algebra_file(path)?;
            // Preserve the directory path by using parent() and join()
            let output_path = if let Some(parent) = path.parent() {
                parent.join(format!("{}.xml", basename))
            } else {
                std::path::PathBuf::from(format!("{}.xml", basename))
            };
            let mut writer = AlgebraWriter::new_with_file(alg, output_path.to_str().unwrap())
                .map_err(|e| BadAlgebraFileException::new(&e))?;
            writer.write_algebra_xml()
                .map_err(|e| BadAlgebraFileException::new(&e))?;
            return Ok(());
        }
    }
    
    Err(BadAlgebraFileException::new("File must have .alg extension"))
}

/// Write an algebra to a file.
/// 
/// Uses XML format by default. The file extension will be .xml unless specified.
/// 
/// # Arguments
/// * `alg` - The algebra to write
/// * `path` - The file path to write to
/// 
/// # Returns
/// * `Ok(())` - If writing succeeds
/// * `Err(String)` - If writing fails
/// 
/// # Examples
/// ```
/// use uacalc::io::algebra_io::write_algebra_file;
/// use uacalc::alg::{SmallAlgebra, BasicAlgebra, Algebra};
/// use std::collections::HashSet;
/// use std::path::Path;
/// 
/// let alg = Box::new(BasicAlgebra::new(
///     "test".to_string(),
///     HashSet::from([0, 1, 2]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // write_algebra_file(alg, Path::new("/tmp/test.xml")).unwrap();
/// ```
pub fn write_algebra_file(alg: Box<dyn SmallAlgebra<UniverseItem = i32>>, path: &Path) -> Result<(), String> {
    write_algebra_file_with_style(alg, path, false)
}

/// Write an algebra to a file with optional old-style format.
/// 
/// If `old_style` is false, uses XML format. If true, uses legacy .alg format.
/// 
/// # Arguments
/// * `alg` - The algebra to write
/// * `path` - The file path to write to
/// * `old_style` - Whether to use legacy .alg format instead of XML
/// 
/// # Returns
/// * `Ok(())` - If writing succeeds
/// * `Err(String)` - If writing fails
/// 
/// # Examples
/// ```
/// use uacalc::io::algebra_io::write_algebra_file_with_style;
/// use uacalc::alg::{SmallAlgebra, BasicAlgebra, Algebra};
/// use std::collections::HashSet;
/// use std::path::Path;
/// 
/// let alg = Box::new(BasicAlgebra::new(
///     "test".to_string(),
///     HashSet::from([0, 1, 2]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // write_algebra_file_with_style(alg, Path::new("/tmp/test.alg"), true).unwrap();
/// ```
pub fn write_algebra_file_with_style(alg: Box<dyn SmallAlgebra<UniverseItem = i32>>, path: &Path, old_style: bool) -> Result<(), String> {
    if !old_style {
        // XML format
        let (name, ext) = ExtFileFilter::split_off_extension(path);
        let output_path = if let (Some(_), Some(ext_str)) = (&name, &ext) {
            if ext_str == "xml" {
                path.to_str().unwrap().to_string()
            } else {
                format!("{}.xml", path.to_str().unwrap())
            }
        } else {
            format!("{}.xml", path.to_str().unwrap())
        };
        
        let mut writer = AlgebraWriter::new_with_file(alg, &output_path)?;
        writer.write_algebra_xml()?;
        Ok(())
    } else {
        // Old style .alg format
        write_algebra_old_style(alg, path)
    }
}

/// Write an algebra in the old .alg format.
/// 
/// The .alg format is:
/// - First line: cardinality (size)
/// - For each operation: arity followed by operation table (one value per line)
/// 
/// # Arguments
/// * `alg` - The algebra to write
/// * `path` - The file path to write to
/// 
/// # Returns
/// * `Ok(())` - If writing succeeds
/// * `Err(String)` - If writing fails
fn write_algebra_old_style(alg: Box<dyn SmallAlgebra<UniverseItem = i32>>, path: &Path) -> Result<(), String> {
    let file = File::create(path)
        .map_err(|e| format!("Failed to create file: {}", e))?;
    let mut writer = std::io::BufWriter::new(file);
    
    let card = alg.cardinality();
    writeln!(writer, "{}", card)
        .map_err(|e| format!("Failed to write cardinality: {}", e))?;
    
    let operations = alg.get_operations_ref();
    for op in operations {
        let arity = op.arity();
        writeln!(writer, "{}", arity)
            .map_err(|e| format!("Failed to write arity: {}", e))?;
        
        let mut op_size = 1;
        for _ in 0..arity {
            op_size *= card;
        }
        
        for i in 0..op_size {
            let arg = horner::horner_inv_same_size(i, card, arity as usize);
            let value = op.int_value_at(&arg)
                .map_err(|e| format!("Failed to get operation value: {}", e))?;
            writeln!(writer, "{}", value)
                .map_err(|e| format!("Failed to write operation value: {}", e))?;
        }
    }
    
    writer.flush()
        .map_err(|e| format!("Failed to flush output: {}", e))?;
    
    Ok(())
}

/// Read a projective plane from an input stream.
/// 
/// The file format has one line per line of the plane, with the points it contains
/// (integers 0 to N-1). The first line must be 0, 1, ..., n.
/// 
/// # Arguments
/// * `stream` - The input stream to read from
/// 
/// # Returns
/// * `Ok(Box<dyn SmallAlgebra>)` - The parsed ternary ring algebra
/// * `Err(BadAlgebraFileException)` - If the file cannot be read or parsed
/// 
/// # Note
/// This function is partially implemented and currently returns an error.
pub fn read_projective_plane_from_stream(stream: Box<dyn Read>) -> Result<Box<dyn SmallAlgebra<UniverseItem = i32>>, BadAlgebraFileException> {
    let reader = BufReader::new(stream);
    read_projective_plane_from_reader(reader)
}

/// Read a projective plane from a file path.
/// 
/// # Arguments
/// * `path` - The file path to read from
/// 
/// # Returns
/// * `Ok(Box<dyn SmallAlgebra>)` - The parsed ternary ring algebra
/// * `Err(BadAlgebraFileException)` - If the file cannot be read or parsed
pub fn read_projective_plane(path: &Path) -> Result<Box<dyn SmallAlgebra<UniverseItem = i32>>, BadAlgebraFileException> {
    let file = File::open(path)
        .map_err(|e| BadAlgebraFileException::new(&format!("Failed to open file: {}", e)))?;
    let reader = BufReader::new(file);
    read_projective_plane_from_reader(reader)
}

/// Read a projective plane from a buffered reader.
/// 
/// # Arguments
/// * `reader` - The buffered reader to read from
/// 
/// # Returns
/// * `Ok(Box<dyn SmallAlgebra>)` - The parsed ternary ring algebra
/// * `Err(BadAlgebraFileException)` - If the reader cannot be parsed
fn read_projective_plane_from_reader<R: BufRead>(mut reader: R) -> Result<Box<dyn SmallAlgebra<UniverseItem = i32>>, BadAlgebraFileException> {
    let mut lines = Vec::new();
    
    let mut line = String::new();
    loop {
        line.clear();
        let bytes_read = reader.read_line(&mut line)
            .map_err(|e| BadAlgebraFileException::new(&format!("Failed to read line: {}", e)))?;
        
        if bytes_read == 0 {
            break; // EOF
        }
        
        let tokens: Vec<&str> = line.split_whitespace().collect();
        if tokens.is_empty() {
            continue;
        }
        
        let mut line_points = Vec::new();
        for token in tokens {
            let point = token.parse::<i32>()
                .map_err(|e| BadAlgebraFileException::new(&format!("Failed to parse point: {}", e)))?;
            line_points.push(point);
        }
        
        lines.push(line_points);
    }
    
    if lines.is_empty() {
        return Err(BadAlgebraFileException::new("nothing in file"));
    }
    
    // Check the first row is the first n+1 integers
    let order = lines[0].len() - 1;
    for i in 0..=order {
        if lines[0][i] != i as i32 {
            return Err(BadAlgebraFileException::new("the first line must be 0, ..., n"));
        }
    }
    
    // TODO: Implement ternary ring construction
    // For now, return error indicating this is not fully implemented
    Err(BadAlgebraFileException::new("Projective plane to ternary ring conversion not yet implemented"))
}

#[cfg(test)]
mod tests {
    use super::*;
    
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
        let data = "0\n1\n1\n0\n";
        let mut reader = BufReader::new(data.as_bytes());
        let op = read_op(2, 2, &mut reader).unwrap();
        assert_eq!(op.arity(), 2);
        
        // Test the operation values
        assert_eq!(op.int_value_at(&[0, 0]).unwrap(), 0);
        assert_eq!(op.int_value_at(&[0, 1]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[1, 0]).unwrap(), 1);
        assert_eq!(op.int_value_at(&[1, 1]).unwrap(), 0);
    }
    
    #[test]
    fn test_read_depth2_list() {
        let data = "test";
        let mut reader = BufReader::new(data.as_bytes());
        let result = read_depth2_list(&mut reader, "[", "]");
        assert!(result.is_none());
    }
}

