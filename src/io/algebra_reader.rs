/*!
 * AlgebraReader - Rust translation of org.uacalc.io.AlgebraReader
 * 
 * XML reading for algebra files. Supports reading single algebras or lists of algebras
 * from .ua and .xml files.
 */

use std::path::Path;
use std::collections::{HashMap, HashSet, VecDeque};
use quick_xml::Reader;
use quick_xml::events::Event;

use crate::alg::Algebra;
use crate::alg::BasicSmallAlgebra;
use crate::alg::op::Operation;
use crate::alg::op::operations as Operations;
use crate::util::horner as Horner;

/// Algebra type constants
pub const BASIC: i32 = 0;
pub const PRODUCT: i32 = 1;
pub const QUOTIENT: i32 = 2;
pub const SUBALGEBRA: i32 = 3;
pub const POWER: i32 = 4;

const EMPTY_STRING: &str = "";

/// AlgebraReader reads algebra definitions from XML files.
/// 
/// This reader parses .ua and .xml files containing algebra definitions,
/// supporting various algebra types including BasicAlgebra, ProductAlgebra,
/// QuotientAlgebra, Subalgebra, and PowerAlgebra.
/// 
/// # Examples
/// ```no_run
/// use uacalc::io::AlgebraReader;
/// use std::path::Path;
/// 
/// let reader = AlgebraReader::new_from_file(Path::new("example.ua")).unwrap();
/// let algebra = reader.read_algebra_file().unwrap();
/// ```
pub struct AlgebraReader {
    file_path: Option<String>,
    input_data: Option<Vec<u8>>,
}

impl AlgebraReader {
    /// Create a new AlgebraReader from a file path.
    /// 
    /// # Arguments
    /// * `file` - Path to the algebra file
    /// 
    /// # Returns
    /// `Ok(AlgebraReader)` on success, `Err(String)` on failure
    pub fn new_from_file(file: &Path) -> Result<Self, String> {
        if !file.exists() {
            return Err(format!("File does not exist: {:?}", file));
        }
        
        Ok(Self {
            file_path: Some(file.to_string_lossy().to_string()),
            input_data: None,
        })
    }
    
    /// Create a new AlgebraReader from a file path string.
    /// 
    /// # Arguments
    /// * `file` - Path string to the algebra file
    /// 
    /// # Returns
    /// `Ok(AlgebraReader)` on success, `Err(String)` on failure
    pub fn new_from_path(file: &str) -> Result<Self, String> {
        Self::new_from_file(Path::new(file))
    }
    
    /// Create a new AlgebraReader from input data.
    /// 
    /// # Arguments
    /// * `data` - XML data as bytes
    /// 
    /// # Returns
    /// `Ok(AlgebraReader)` on success, `Err(String)` on failure
    pub fn new_from_stream(data: Vec<u8>) -> Result<Self, String> {
        Ok(Self {
            file_path: None,
            input_data: Some(data),
        })
    }
    
    /// Read a single algebra from the file.
    /// 
    /// # Returns
    /// The algebra on success, error message on failure
    pub fn read_algebra_file(&self) -> Result<BasicSmallAlgebra<i32>, String> {
        let data = if let Some(ref path) = self.file_path {
            std::fs::read(path).map_err(|e| format!("Failed to read file: {}", e))?
        } else if let Some(ref data) = self.input_data {
            data.clone()
        } else {
            return Err("No file path or input data provided".to_string());
        };
        
        self.parse_single_algebra(&data)
    }
    
    /// Read a single algebra from the stream.
    /// 
    /// # Returns
    /// The algebra on success, error message on failure
    pub fn read_algebra_from_stream(&self) -> Result<BasicSmallAlgebra<i32>, String> {
        self.read_algebra_file()
    }
    
    /// Read a list of algebras from the file.
    /// 
    /// # Returns
    /// List of algebras on success, error message on failure
    pub fn read_algebra_list_file(&self) -> Result<Vec<BasicSmallAlgebra<i32>>, String> {
        let data = if let Some(ref path) = self.file_path {
            std::fs::read(path).map_err(|e| format!("Failed to read file: {}", e))?
        } else if let Some(ref data) = self.input_data {
            data.clone()
        } else {
            return Err("No file path or input data provided".to_string());
        };
        
        self.parse_algebra_list(&data)
    }
    
    /// Read a list of algebras from the stream.
    /// 
    /// # Returns
    /// List of algebras on success, error message on failure
    pub fn read_algebra_list_from_stream(&self) -> Result<Vec<BasicSmallAlgebra<i32>>, String> {
        self.read_algebra_list_file()
    }
    
    /// Parse a single algebra from XML data.
    fn parse_single_algebra(&self, data: &[u8]) -> Result<BasicSmallAlgebra<i32>, String> {
        let algebras = self.parse_algebra_list(data)?;
        if algebras.is_empty() {
            Err("No algebras found in file".to_string())
        } else {
            Ok(algebras.into_iter().next().unwrap())
        }
    }
    
    /// Parse a list of algebras from XML data.
    fn parse_algebra_list(&self, data: &[u8]) -> Result<Vec<BasicSmallAlgebra<i32>>, String> {
        let mut reader = Reader::from_reader(data);
        reader.trim_text(true);
        
        let mut parser = AlgebraParser::new();
        let mut buf = Vec::new();
        
        loop {
            match reader.read_event_into(&mut buf) {
                Ok(Event::Start(ref e)) => {
                    let name = String::from_utf8_lossy(e.name().as_ref()).to_string();
                    parser.start_element(&name)?;
                }
                Ok(Event::End(ref e)) => {
                    let name = String::from_utf8_lossy(e.name().as_ref()).to_string();
                    parser.end_element(&name)?;
                }
                Ok(Event::Text(ref e)) => {
                    let text = e.unescape().map_err(|e| format!("Text unescape error: {}", e))?;
                    parser.characters(&text)?;
                }
                Ok(Event::Eof) => break,
                Err(e) => return Err(format!("XML parse error: {}", e)),
                _ => (),
            }
            buf.clear();
        }
        
        Ok(parser.algebra_list)
    }
}

/// Internal parser state for processing XML events.
struct AlgebraParser {
    // String accumulation
    alg_name_string: String,
    op_name_string: String,
    desc_string: String,
    cardinality_string: String,
    arity_string: String,
    power_string: String,
    powers_string: String,
    row_string: String,
    int_array_string: String,
    product_elem_string: String,
    
    // Parsed values
    alg_name: Option<String>,
    op_name: Option<String>,
    desc: Option<String>,
    cardinality: i32,
    arity: i32,
    power: i32,
    powers: Vec<i32>,
    
    // Working data
    int_array: Vec<i32>,
    int_array_index: usize,
    ops: Vec<Box<dyn Operation>>,
    
    // Algebra tracking
    algebra: Option<BasicSmallAlgebra<i32>>,
    algebra_list: Vec<BasicSmallAlgebra<i32>>,
    alg_type: i32,
    
    // Tag stack for context
    tag_stack: Vec<String>,
    alg_name_stack: VecDeque<String>,
    name_desc_map: HashMap<String, Option<String>>,
}

impl AlgebraParser {
    fn new() -> Self {
        Self {
            alg_name_string: String::new(),
            op_name_string: String::new(),
            desc_string: String::new(),
            cardinality_string: String::new(),
            arity_string: String::new(),
            power_string: String::new(),
            powers_string: String::new(),
            row_string: String::new(),
            int_array_string: String::new(),
            product_elem_string: String::new(),
            
            alg_name: None,
            op_name: None,
            desc: None,
            cardinality: 0,
            arity: 0,
            power: 0,
            powers: Vec::new(),
            
            int_array: Vec::new(),
            int_array_index: 0,
            ops: Vec::new(),
            
            algebra: None,
            algebra_list: Vec::new(),
            alg_type: BASIC,
            
            tag_stack: Vec::new(),
            alg_name_stack: VecDeque::new(),
            name_desc_map: HashMap::new(),
        }
    }
    
    fn clear_strings(&mut self) {
        self.alg_name_string.clear();
        self.op_name_string.clear();
        self.desc_string.clear();
        self.cardinality_string.clear();
        self.arity_string.clear();
        self.power_string.clear();
        self.powers_string.clear();
        self.row_string.clear();
        self.int_array_string.clear();
        self.product_elem_string.clear();
    }
    
    fn current_tag(&self) -> Option<&str> {
        self.tag_stack.last().map(|s| s.as_str())
    }
    
    fn parent_tag(&self) -> Option<&str> {
        if self.tag_stack.len() < 2 {
            None
        } else {
            self.tag_stack.get(self.tag_stack.len() - 2).map(|s| s.as_str())
        }
    }
    
    fn int_row(&mut self, s: &str) -> Result<(), String> {
        let parts: Vec<&str> = s.split(',').map(|p| p.trim()).collect();
        for (i, part) in parts.iter().enumerate() {
            let val = part.parse::<i32>()
                .map_err(|e| format!("Failed to parse int in row: {}", e))?;
            if self.int_array_index + i < self.int_array.len() {
                self.int_array[self.int_array_index + i] = val;
            }
        }
        self.int_array_index += parts.len();
        Ok(())
    }
    
    fn raw_int_array(&self, s: &str) -> Result<Vec<i32>, String> {
        s.split(',')
            .map(|p| p.trim())
            .filter(|p| !p.is_empty())
            .map(|p| p.parse::<i32>().map_err(|e| format!("Failed to parse int: {}", e)))
            .collect()
    }
    
    fn start_element(&mut self, elem_name: &str) -> Result<(), String> {
        self.tag_stack.push(elem_name.to_string());
        
        match elem_name {
            "algName" => self.alg_name_string.clear(),
            "opName" => self.op_name_string.clear(),
            "desc" => self.desc_string.clear(),
            "cardinality" => self.cardinality_string.clear(),
            "arity" => self.arity_string.clear(),
            "power" => self.power_string.clear(),
            "powers" => self.powers_string.clear(),
            "row" => self.row_string.clear(),
            "productElem" => self.product_elem_string.clear(),
            "intArray" => self.int_array_string.clear(),
            
            "basicAlgebra" => self.alg_type = BASIC,
            "powerAlgebra" => self.alg_type = POWER,
            "productAlgebra" => self.alg_type = PRODUCT,
            "quotientAlgebra" => self.alg_type = QUOTIENT,
            "subAlgebra" => self.alg_type = SUBALGEBRA,
            
            "opTable" => {
                let size = (self.cardinality as usize).pow(self.arity as u32);
                self.int_array = vec![0; size];
                self.int_array_index = 0;
            }
            "congruence" => {
                self.int_array = vec![0; self.cardinality as usize];
                self.int_array_index = 0;
            }
            "subUniverse" => {
                self.int_array = vec![0; self.cardinality as usize];
                self.int_array_index = 0;
            }
            _ => {}
        }
        
        Ok(())
    }
    
    fn characters(&mut self, s: &str) -> Result<(), String> {
        let current = self.current_tag();
        let parent = self.parent_tag();
        
        match current {
            Some("algName") => self.alg_name_string.push_str(s),
            Some("opName") => self.op_name_string.push_str(s),
            Some("desc") => self.desc_string.push_str(s),
            Some("cardinality") => self.cardinality_string.push_str(s),
            Some("arity") => self.arity_string.push_str(s),
            Some("power") => self.power_string.push_str(s),
            Some("row") => self.row_string.push_str(s),
            Some("intArray") => {
                if parent == Some("congruence") && !s.is_empty() {
                    self.int_array_string.push_str(s);
                } else if parent == Some("subUniverse") && !s.is_empty() {
                    self.int_array_string.push_str(s);
                } else if parent == Some("powers") && !s.is_empty() {
                    self.powers_string.push_str(s);
                }
            }
            Some("productElem") => self.product_elem_string.push_str(s),
            _ => {}
        }
        
        Ok(())
    }
    
    fn end_element(&mut self, elem_name: &str) -> Result<(), String> {
        // Get parent before popping stack to avoid borrow issues
        let parent = if self.tag_stack.len() >= 2 {
            Some(self.tag_stack[self.tag_stack.len() - 2].clone())
        } else {
            None
        };
        self.tag_stack.pop();
        
        match elem_name {
            "algebra" => {
                if let Some(alg) = self.algebra.take() {
                    self.algebra_list.push(alg);
                }
                self.clear_strings();
            }
            "algName" => {
                let name = self.alg_name_string.trim().to_string();
                self.alg_name = Some(name.clone());
                self.alg_name_stack.push_front(name.clone());
                self.name_desc_map.insert(name, None);
            }
            "opName" => {
                self.op_name = Some(self.op_name_string.trim().to_string());
            }
            "desc" => {
                let desc = self.desc_string.trim().to_string();
                self.desc = Some(desc.clone());
                if let Some(ref name) = self.alg_name {
                    self.name_desc_map.insert(name.clone(), Some(desc));
                }
                self.desc_string.clear();
            }
            "cardinality" => {
                self.cardinality = self.cardinality_string.trim().parse()
                    .map_err(|e| format!("Failed to parse cardinality: {}", e))?;
            }
            "arity" => {
                self.arity = self.arity_string.trim().parse()
                    .map_err(|e| format!("Failed to parse arity: {}", e))?;
            }
            "power" => {
                self.power = self.power_string.trim().parse()
                    .map_err(|e| format!("Failed to parse power: {}", e))?;
            }
            "powers" => {
                self.powers = self.raw_int_array(self.powers_string.trim())?;
            }
            "row" => {
                let row_str = self.row_string.trim().to_string();
                self.int_row(&row_str)?;
            }
            "intArray" if parent == Some("congruence".to_string()) => {
                let trimmed = self.int_array_string.trim().to_string();
                if !trimmed.is_empty() {
                    self.int_array = self.raw_int_array(&trimmed)?;
                }
            }
            "intArray" if parent == Some("subUniverse".to_string()) => {
                let trimmed = self.int_array_string.trim().to_string();
                if !trimmed.is_empty() {
                    self.int_array = self.raw_int_array(&trimmed)?;
                }
            }
            "op" => {
                // Create operation using Operations factory
                let op_name = self.op_name.clone().unwrap_or_else(|| "op".to_string());
                let arity = self.arity;
                let cardinality = self.cardinality;
                
                // Apply left-right reverse transformation as in Java
                let transformed_table = Horner::left_right_reverse(
                    &self.int_array, 
                    cardinality, 
                    arity as usize
                );
                
                let operation = Operations::make_int_operation_str(
                    &op_name,
                    arity,
                    cardinality,
                    transformed_table
                )?;
                
                self.ops.push(operation);
            }
            "basicAlgebra" => {
                let name = self.alg_name_stack.front()
                    .map(|s| s.clone())
                    .unwrap_or_else(|| "unnamed".to_string());
                
                // Create BasicSmallAlgebra with integer universe {0, 1, ..., cardinality-1}
                let universe: HashSet<i32> = (0..self.cardinality).collect();
                let ops = std::mem::take(&mut self.ops);
                let algebra = BasicSmallAlgebra::new(
                    name.clone(),
                    universe,
                    ops
                );
                
                self.algebra = Some(algebra);
                self.add_description();
                self.ops = Vec::new();
            }
            _ => {}
        }
        
        Ok(())
    }
    
    fn add_description(&mut self) {
        if let Some(ref mut algebra) = self.algebra {
            if let Some(desc_opt) = self.name_desc_map.get(algebra.name()) {
                if let Some(ref desc) = desc_opt {
                    algebra.set_description(Some(desc.clone()));
                }
            }
            if !self.alg_name_stack.is_empty() {
                self.alg_name_stack.pop_front();
            }
            self.alg_name = None;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_algebra_reader_from_file() {
        // Test reading a simple algebra file
        let xml = r#"<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>test</algName>
    <cardinality>2</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>f</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,1</row>
            <row r="[1]">1,0</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>"#;
        
        let reader = AlgebraReader::new_from_stream(xml.as_bytes().to_vec()).unwrap();
        let algebra = reader.read_algebra_from_stream().unwrap();
        
        assert_eq!(algebra.name(), "test");
        assert_eq!(algebra.cardinality(), 2);
    }
}

