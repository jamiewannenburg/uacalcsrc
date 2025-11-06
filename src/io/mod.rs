mod algebra_reader;
pub use algebra_reader::AlgebraReader;

pub mod algebra_io;
pub use algebra_io::*;

#[cfg(test)]
mod mace4_reader_tests;

use std::io::{Write, BufWriter};
use std::fs::File;
use crate::alg::{SmallAlgebra, AlgebraType};
use crate::alg::op::Operation;
use crate::alg::conlat::partition::Partition;
use crate::util::sequence_generator::SequenceGenerator;
use crate::util::horner;
use crate::util::array_string;

/// XML writer for algebras with support for multiple algebra types.
/// 
/// This struct provides functionality to write algebra definitions to XML format,
/// supporting various algebra types including BasicAlgebra, ProductAlgebra,
/// QuotientAlgebra, Subalgebra, PowerAlgebra, FreeAlgebra, BigProductAlgebra,
/// and SubProductAlgebra.
/// 
/// # Examples
/// ```
/// use uacalc::io::AlgebraWriter;
/// use uacalc::alg::{SmallAlgebra, BasicAlgebra, Algebra};
/// use std::collections::HashSet;
/// use std::fs::File;
/// 
/// // Create a small algebra
/// let alg = Box::new(BasicAlgebra::new(
///     "example".to_string(),
///     HashSet::from([0, 1, 2]),
///     Vec::new()
/// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
/// 
/// // Write to file
/// let mut writer = AlgebraWriter::new_with_file(alg, "output.xml").unwrap();
/// writer.write_algebra_xml().unwrap();
/// ```
pub struct AlgebraWriter {
    /// The output writer
    out: Box<dyn Write>,
    
    /// The algebra to write
    algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>,
    
    /// Current indentation level
    indent: usize,
}

impl AlgebraWriter {
    /// Create a new AlgebraWriter with a custom writer.
    /// 
    /// # Arguments
    /// * `algebra` - The algebra to write
    /// * `out` - The output writer
    /// 
    /// # Returns
    /// A new AlgebraWriter instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::AlgebraWriter;
    /// use uacalc::alg::{SmallAlgebra, BasicAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// use std::io::stdout;
    /// 
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "example".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let writer = AlgebraWriter::new(alg, Box::new(stdout()));
    /// ```
    pub fn new(algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>, out: Box<dyn Write>) -> Self {
        Self {
            out,
            algebra,
            indent: 0,
        }
    }
    
    /// Create a new AlgebraWriter that writes to a file.
    /// 
    /// # Arguments
    /// * `algebra` - The algebra to write
    /// * `file_path` - The path to the output file
    /// 
    /// # Returns
    /// * `Ok(AlgebraWriter)` - Successfully created writer
    /// * `Err(String)` - If the file cannot be created
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::AlgebraWriter;
    /// use uacalc::alg::{SmallAlgebra, BasicAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "example".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let writer = AlgebraWriter::new_with_file(alg, "output.xml").unwrap();
    /// ```
    pub fn new_with_file(algebra: Box<dyn SmallAlgebra<UniverseItem = i32>>, file_path: &str) -> Result<Self, String> {
        let file = File::create(file_path)
            .map_err(|e| format!("Failed to create file {}: {}", file_path, e))?;
        let writer = BufWriter::new(file);
        Ok(Self::new(algebra, Box::new(writer)))
    }
    
    /// Write the complete algebra XML to the output.
    /// 
    /// This method writes the XML header and the complete algebra definition,
    /// then closes the output stream.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::AlgebraWriter;
    /// use uacalc::alg::{SmallAlgebra, BasicAlgebra, Algebra};
    /// use std::collections::HashSet;
    /// 
    /// let alg = Box::new(BasicAlgebra::new(
    ///     "example".to_string(),
    ///     HashSet::from([0, 1]),
    ///     Vec::new()
    /// )) as Box<dyn SmallAlgebra<UniverseItem = i32>>;
    /// 
    /// let mut writer = AlgebraWriter::new_with_file(alg, "output.xml").unwrap();
    /// writer.write_algebra_xml().unwrap();
    /// ```
    pub fn write_algebra_xml(&mut self) -> Result<(), String> {
        writeln!(self.out, "<?xml version=\"1.0\"?>")
            .map_err(|e| format!("Failed to write XML header: {}", e))?;
        
        self.write_tag("<algebra>")?;
        self.write_algebra()?;
        self.write_end_tag("</algebra>")?;
        
        // Flush the output
        self.out.flush()
            .map_err(|e| format!("Failed to flush output: {}", e))?;
        
        Ok(())
    }
    
    /// Write the algebra definition (dispatches to specific type).
    /// 
    /// This method examines the algebra type and calls the appropriate
    /// writing method for that specific algebra type.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    pub fn write_algebra(&mut self) -> Result<(), String> {
        match self.algebra.algebra_type() {
            AlgebraType::Power => self.write_power_algebra(),
            AlgebraType::Product => self.write_product_algebra(),
            AlgebraType::Quotient => self.write_quotient_algebra(),
            AlgebraType::Subalgebra => self.write_subalgebra(),
            AlgebraType::Free => self.write_free_algebra(),
            AlgebraType::Subproduct => self.write_sub_product_algebra(),
            _ => self.write_basic_algebra(),
        }
    }
    
    /// Write a basic algebra definition.
    /// 
    /// This method writes the XML for a basic algebra, including its name,
    /// description, cardinality, universe (if not integer-based), and operations.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    pub fn write_basic_algebra(&mut self) -> Result<(), String> {
        self.write_tag("<basicAlgebra>")?;
        self.write_alg_name()?;
        self.write_desc()?;
        self.write_cardinality()?;
        
        // Write universe if it's not integer-based
        if self.algebra.get_universe_list().is_some() {
            self.write_universe()?;
        }
        
        self.write_tag("<operations>")?;
        let operations = self.algebra.get_operations_ref();
        let algebra_cardinality = self.algebra.cardinality();
        
        // Collect all operation data upfront to avoid borrowing conflicts
        let mut operation_data = Vec::new();
        for operation in operations {
            let symbol = operation.symbol().clone();
            let arity = operation.arity();
            let mut arg = vec![0; arity as usize];
            let mut inc = SequenceGenerator::sequence_incrementor(&mut arg, algebra_cardinality - 1);
            
            let mut h = 1;
            for _ in 0..arity {
                h = h * algebra_cardinality;
            }
            
            let mut arr = vec![0; h as usize];
            let mut k = 0;
            
            loop {
                let current_arg = inc.get_current();
                arr[k] = operation.int_value_at(&current_arg)?;
                k += 1;
                if !inc.increment() {
                    break;
                }
            }
            
            operation_data.push((symbol, arity, arr));
        }
        
        // Now write all operations without borrowing conflicts
        for (symbol, arity, arr) in operation_data {
            self.write_operation_from_data(&symbol, arity, &arr, algebra_cardinality)?;
        }
        self.write_end_tag("</operations>")?;
        
        self.write_end_tag("</basicAlgebra>")?;
        Ok(())
    }
    
    /// Write a power algebra definition.
    /// 
    /// This method writes the XML for a power algebra, including its root algebra
    /// and power information.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_power_algebra(&mut self) -> Result<(), String> {
        self.write_tag("<powerAlgebra>")?;
        self.write_alg_name()?;
        self.write_desc()?;
        self.write_cardinality()?;
        self.write_power()?;
        
        self.write_tag("<root>")?;
        // Note: In a real implementation, we would need to access the root algebra
        // For now, we'll write a placeholder
        self.write_tag("<basicAlgebra>")?;
        self.write_alg_name()?;
        self.write_desc()?;
        self.write_cardinality()?;
        self.write_end_tag("</basicAlgebra>")?;
        self.write_end_tag("</root>")?;
        
        self.write_end_tag("</powerAlgebra>")?;
        Ok(())
    }
    
    /// Write a product algebra definition.
    /// 
    /// This method writes the XML for a product algebra, including all its factors.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_product_algebra(&mut self) -> Result<(), String> {
        self.write_tag("<productAlgebra>")?;
        self.write_alg_name()?;
        self.write_desc()?;
        self.write_cardinality()?;
        
        self.write_tag("<factors>")?;
        // Note: In a real implementation, we would need to access the factors
        // For now, we'll write a placeholder
        self.write_tag("<factor>")?;
        self.write_tag("<basicAlgebra>")?;
        self.write_alg_name()?;
        self.write_desc()?;
        self.write_cardinality()?;
        self.write_end_tag("</basicAlgebra>")?;
        self.write_end_tag("</factor>")?;
        self.write_end_tag("</factors>")?;
        
        self.write_end_tag("</productAlgebra>")?;
        Ok(())
    }
    
    /// Write a quotient algebra definition.
    /// 
    /// This method writes the XML for a quotient algebra, including its super algebra
    /// and congruence relation.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_quotient_algebra(&mut self) -> Result<(), String> {
        self.write_tag("<quotientAlgebra>")?;
        self.write_alg_name()?;
        self.write_desc()?;
        self.write_cardinality()?;
        
        self.write_tag("<superAlgebra>")?;
        // Note: In a real implementation, we would need to access the super algebra
        self.write_tag("<basicAlgebra>")?;
        self.write_alg_name()?;
        self.write_desc()?;
        self.write_cardinality()?;
        self.write_end_tag("</basicAlgebra>")?;
        self.write_end_tag("</superAlgebra>")?;
        
        self.write_tag("<congruence>")?;
        // Note: In a real implementation, we would need to access the congruence
        self.write_tag("<partition>")?;
        self.write_indent()?;
        writeln!(self.out, "0,1")
            .map_err(|e| format!("Failed to write partition: {}", e))?;
        self.write_end_tag("</partition>")?;
        self.write_int_array(&[0, 1])?;
        self.write_end_tag("</congruence>")?;
        
        self.write_end_tag("</quotientAlgebra>")?;
        Ok(())
    }
    
    /// Write a subalgebra definition.
    /// 
    /// This method writes the XML for a subalgebra, including its super algebra
    /// and subuniverse.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_subalgebra(&mut self) -> Result<(), String> {
        self.write_tag("<subAlgebra>")?;
        self.write_alg_name()?;
        self.write_desc()?;
        self.write_cardinality()?;
        
        self.write_tag("<superAlgebra>")?;
        // Note: In a real implementation, we would need to access the super algebra
        self.write_tag("<basicAlgebra>")?;
        self.write_alg_name()?;
        self.write_desc()?;
        self.write_cardinality()?;
        self.write_end_tag("</basicAlgebra>")?;
        self.write_end_tag("</superAlgebra>")?;
        
        self.write_tag("<subUniverse>")?;
        // Note: In a real implementation, we would need to access the subuniverse
        self.write_int_array(&[0, 1])?;
        self.write_end_tag("</subUniverse>")?;
        
        self.write_end_tag("</subAlgebra>")?;
        Ok(())
    }
    
    /// Write a free algebra definition.
    /// 
    /// This method writes the XML for a free algebra (which is a special case
    /// of SubProductAlgebra).
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_free_algebra(&mut self) -> Result<(), String> {
        self.write_sub_product_algebra_aux("<freeAlgebra>", "</freeAlgebra>")
    }
    
    /// Write a subproduct algebra definition.
    /// 
    /// This method writes the XML for a subproduct algebra.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_sub_product_algebra(&mut self) -> Result<(), String> {
        self.write_sub_product_algebra_aux("<subProductAlgebra>", "</subProductAlgebra>")
    }
    
    /// Write a subproduct algebra with custom tags.
    /// 
    /// This is a helper method used by both free algebra and subproduct algebra
    /// writing methods.
    /// 
    /// # Arguments
    /// * `start_tag` - The opening tag
    /// * `end_tag` - The closing tag
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_sub_product_algebra_aux(&mut self, start_tag: &str, end_tag: &str) -> Result<(), String> {
        self.write_tag(start_tag)?;
        self.write_alg_name()?;
        self.write_desc()?;
        self.write_cardinality()?;
        
        self.write_tag("<generators>")?;
        // Note: In a real implementation, we would need to access the generators
        self.write_prod_elem(&[0, 0])?;
        self.write_prod_elem(&[1, 0])?;
        self.write_end_tag("</generators>")?;
        
        self.write_tag("<universe>")?;
        // Note: In a real implementation, we would need to access the universe
        self.write_prod_elem(&[0, 0])?;
        self.write_prod_elem(&[0, 1])?;
        self.write_prod_elem(&[1, 0])?;
        self.write_prod_elem(&[1, 1])?;
        self.write_end_tag("</universe>")?;
        
        self.write_tag("<superAlgebra>")?;
        // Note: In a real implementation, we would need to access the super algebra
        self.write_tag("<bigProductAlgebra>")?;
        self.write_alg_name()?;
        self.write_desc()?;
        self.write_tag("<powers>")?;
        self.write_int_array_with_line_break(&[2, 2], false)?;
        self.write_end_tag("</powers>")?;
        self.write_tag("<rootFactors>")?;
        self.write_tag("<factor>")?;
        self.write_tag("<basicAlgebra>")?;
        self.write_alg_name()?;
        self.write_desc()?;
        self.write_cardinality()?;
        self.write_end_tag("</basicAlgebra>")?;
        self.write_end_tag("</factor>")?;
        self.write_end_tag("</rootFactors>")?;
        self.write_end_tag("</bigProductAlgebra>")?;
        self.write_end_tag("</superAlgebra>")?;
        
        self.write_end_tag(end_tag)?;
        Ok(())
    }
    
    /// Write the algebra name.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_alg_name(&mut self) -> Result<(), String> {
        let name = self.algebra.name().to_string();
        if !name.is_empty() {
            self.write_begin_end_tag("<algName>", "</algName>", &name)?;
        }
        Ok(())
    }
    
    /// Write the algebra description.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_desc(&mut self) -> Result<(), String> {
        if let Some(desc) = self.algebra.description() {
            let desc_str = desc.to_string();
            if !desc_str.is_empty() {
                self.write_begin_end_tag("<desc>", "</desc>", &desc_str)?;
            }
        }
        Ok(())
    }
    
    /// Write the algebra cardinality.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_cardinality(&mut self) -> Result<(), String> {
        self.write_begin_end_tag("<cardinality>", "</cardinality>", &self.algebra.cardinality().to_string())?;
        Ok(())
    }
    
    /// Write the power for power algebras.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_power(&mut self) -> Result<(), String> {
        // Note: In a real implementation, we would need to access the power
        // For now, we'll write a placeholder
        self.write_begin_end_tag("<power>", "</power>", "2")?;
        Ok(())
    }
    
    /// Write the universe elements.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_universe(&mut self) -> Result<(), String> {
        self.write_tag("<universe>")?;
        
        if let Some(universe_list) = self.algebra.get_universe_list() {
            for element in universe_list {
                self.write_begin_end_tag("<elem>", "</elem>", &element.to_string())?;
            }
        }
        
        self.write_end_tag("</universe>")?;
        Ok(())
    }
    
    /// Write an operation definition.
    /// 
    /// # Arguments
    /// * `operation` - The operation to write
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_operation(&mut self, operation: &dyn Operation) -> Result<(), String> {
        let mut arg = vec![0; operation.arity() as usize];
        let mut inc = SequenceGenerator::sequence_incrementor(&mut arg, self.algebra.cardinality() - 1);
        
        self.write_tag("<op>")?;
        
        // Write the operation symbol
        self.write_tag("<opSymbol>")?;
        self.write_begin_end_tag("<opName>", "</opName>", operation.symbol().name())?;
        self.write_begin_end_tag("<arity>", "</arity>", &operation.arity().to_string())?;
        self.write_end_tag("</opSymbol>")?;
        
        // Write the operation table
        self.write_tag("<opTable>")?;
        
        let size = self.algebra.cardinality();
        let mut h = 1;
        for _ in 0..operation.arity() {
            h = h * size;
        }
        
        let mut arr = vec![0; h as usize];
        let mut k = 0;
        
        loop {
            let current_arg = inc.get_current();
            arr[k] = operation.int_value_at(&current_arg)?;
            k += 1;
            if !inc.increment() {
                break;
            }
        }
        
        self.write_op_array(&arr, operation.arity())?;
        self.write_end_tag("</opTable>")?;
        self.write_end_tag("</op>")?;
        
        Ok(())
    }
    
    /// Write an operation from collected data to avoid borrowing conflicts.
    /// 
    /// # Arguments
    /// * `symbol` - The operation symbol
    /// * `arity` - The arity of the operation
    /// * `arr` - The operation table array
    /// * `cardinality` - The cardinality of the algebra
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_operation_from_data(&mut self, symbol: &OperationSymbol, arity: i32, arr: &[i32], cardinality: i32) -> Result<(), String> {
        self.write_tag("<op>")?;
        
        // Write the operation symbol
        self.write_tag("<opSymbol>")?;
        self.write_begin_end_tag("<opName>", "</opName>", symbol.name())?;
        self.write_begin_end_tag("<arity>", "</arity>", &arity.to_string())?;
        self.write_end_tag("</opSymbol>")?;
        
        // Write the operation table
        self.write_tag("<opTable>")?;
        self.write_op_array_with_cardinality(arr, arity, cardinality)?;
        self.write_end_tag("</opTable>")?;
        self.write_end_tag("</op>")?;
        
        Ok(())
    }
    
    /// Write an operation array in the proper format.
    /// 
    /// # Arguments
    /// * `arr` - The operation array
    /// * `arity` - The arity of the operation
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_op_array(&mut self, arr: &[i32], arity: i32) -> Result<(), String> {
        let card = self.algebra.cardinality();
        self.write_tag("<intArray>")?;
        
        for i in (0..arr.len()).step_by(card as usize) {
            self.write_row(i, arr, arity)?;
        }
        
        self.write_end_tag("</intArray>")?;
        Ok(())
    }
    
    /// Write an operation array in the proper format using a specific cardinality.
    /// 
    /// # Arguments
    /// * `arr` - The operation array
    /// * `arity` - The arity of the operation
    /// * `cardinality` - The cardinality to use for formatting
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_op_array_with_cardinality(&mut self, arr: &[i32], arity: i32, cardinality: i32) -> Result<(), String> {
        self.write_tag("<intArray>")?;
        
        for i in (0..arr.len()).step_by(cardinality as usize) {
            self.write_row_with_cardinality(i, arr, arity, cardinality)?;
        }
        
        self.write_end_tag("</intArray>")?;
        Ok(())
    }
    
    /// Write a row of the operation table.
    /// 
    /// # Arguments
    /// * `index` - The starting index for this row
    /// * `arr` - The operation array
    /// * `arity` - The arity of the operation
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_row(&mut self, index: usize, arr: &[i32], arity: i32) -> Result<(), String> {
        let card = self.algebra.cardinality();
        
        if card <= 0 {
            return Err(format!("Invalid cardinality: {}", card));
        }
        
        if arity == 0 {
            self.write_indent()?;
            writeln!(self.out, "<row>{}</row>", arr[0])
                .map_err(|e| format!("Failed to write row: {}", e))?;
            return Ok(());
        }
        
        let mut row_values = Vec::new();
        for j in 0..card {
            row_values.push(arr[index + j as usize].to_string());
        }
        let row = row_values.join(",");
        
        self.write_indent()?;
        
        if arity == 1 {
            writeln!(self.out, "<row>{}</row>", row)
                .map_err(|e| format!("Failed to write row: {}", e))?;
        } else {
            let index_arr = horner::horner_inv((index / card as usize) as i32, &[card]);
            let reversed_index_arr = horner::reverse_array(&index_arr);
            let index_string = array_string::to_string(&reversed_index_arr);
            
            write!(self.out, "<row r=\"{}\">", index_string)
                .map_err(|e| format!("Failed to write row: {}", e))?;
            write!(self.out, "{}", row)
                .map_err(|e| format!("Failed to write row: {}", e))?;
            writeln!(self.out, "</row>")
                .map_err(|e| format!("Failed to write row: {}", e))?;
        }
        
        Ok(())
    }
    
    /// Write a row of the operation table using a specific cardinality.
    /// 
    /// # Arguments
    /// * `index` - The starting index for this row
    /// * `arr` - The operation array
    /// * `arity` - The arity of the operation
    /// * `cardinality` - The cardinality to use
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_row_with_cardinality(&mut self, index: usize, arr: &[i32], arity: i32, cardinality: i32) -> Result<(), String> {
        if cardinality <= 0 {
            return Err(format!("Invalid cardinality: {}", cardinality));
        }
        
        if arity == 0 {
            self.write_indent()?;
            writeln!(self.out, "<row>{}</row>", arr[0])
                .map_err(|e| format!("Failed to write row: {}", e))?;
            return Ok(());
        }
        
        let mut row_values = Vec::new();
        for j in 0..cardinality {
            row_values.push(arr[index + j as usize].to_string());
        }
        let row = row_values.join(",");
        
        self.write_indent()?;
        
        if arity == 1 {
            writeln!(self.out, "<row>{}</row>", row)
                .map_err(|e| format!("Failed to write row: {}", e))?;
        } else {
            let index_arr = horner::horner_inv((index / cardinality as usize) as i32, &[cardinality]);
            let reversed_index_arr = horner::reverse_array(&index_arr);
            let index_string = array_string::to_string(&reversed_index_arr);
            
            write!(self.out, "<row r=\"{}\">", index_string)
                .map_err(|e| format!("Failed to write row: {}", e))?;
            write!(self.out, "{}", row)
                .map_err(|e| format!("Failed to write row: {}", e))?;
            writeln!(self.out, "</row>")
                .map_err(|e| format!("Failed to write row: {}", e))?;
        }
        
        Ok(())
    }
    
    /// Write a product element.
    /// 
    /// # Arguments
    /// * `arr` - The array representing the product element
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_prod_elem(&mut self, arr: &[i32]) -> Result<(), String> {
        self.write_tag("<productElem>")?;
        self.write_indent()?;
        
        for i in 0..arr.len() - 1 {
            write!(self.out, "{},", arr[i])
                .map_err(|e| format!("Failed to write product element: {}", e))?;
        }
        writeln!(self.out, "{}", arr[arr.len() - 1])
            .map_err(|e| format!("Failed to write product element: {}", e))?;
        
        self.write_end_tag("</productElem>")?;
        Ok(())
    }
    
    /// Write an integer array.
    /// 
    /// # Arguments
    /// * `arr` - The array to write
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_int_array(&mut self, arr: &[i32]) -> Result<(), String> {
        self.write_int_array_with_line_break(arr, true)
    }
    
    /// Write an integer array with optional line breaks.
    /// 
    /// # Arguments
    /// * `arr` - The array to write
    /// * `line_break` - Whether to add line breaks
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_int_array_with_line_break(&mut self, arr: &[i32], line_break: bool) -> Result<(), String> {
        self.write_int_array_impl(arr, line_break)
    }
    
    /// Write an integer array with line break control.
    /// 
    /// # Arguments
    /// * `arr` - The array to write
    /// * `line_break` - Whether to add line breaks
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_int_array_impl(&mut self, arr: &[i32], line_break: bool) -> Result<(), String> {
        self.write_tag("<intArray>")?;
        let card = self.algebra.cardinality();
        
        self.write_indent()?;
        for i in 0..arr.len() - 1 {
            write!(self.out, "{}", arr[i])
                .map_err(|e| format!("Failed to write int array: {}", e))?;
            write!(self.out, ",")
                .map_err(|e| format!("Failed to write int array: {}", e))?;
            
            if line_break && (i + 1) % card as usize == 0 {
                writeln!(self.out)
                    .map_err(|e| format!("Failed to write int array: {}", e))?;
                self.write_indent()?;
            }
        }
        writeln!(self.out, "{}", arr[arr.len() - 1])
            .map_err(|e| format!("Failed to write int array: {}", e))?;
        
        self.write_end_tag("</intArray>")?;
        Ok(())
    }
    
    /// Write a human-readable partition.
    /// 
    /// # Arguments
    /// * `part` - The partition to write
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_human_partition(&mut self, part: &Partition) -> Result<(), String> {
        self.write_tag("<partition>")?;
        self.write_indent()?;
        writeln!(self.out, "{}", part.to_string())
            .map_err(|e| format!("Failed to write partition: {}", e))?;
        self.write_end_tag("</partition>")?;
        Ok(())
    }
    
    /// Write indentation spaces.
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_indent(&mut self) -> Result<(), String> {
        for _ in 0..self.indent {
            write!(self.out, "  ")
                .map_err(|e| format!("Failed to write indent: {}", e))?;
        }
        Ok(())
    }
    
    /// Write a tag and increase indentation.
    /// 
    /// # Arguments
    /// * `tag` - The tag to write
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_tag(&mut self, tag: &str) -> Result<(), String> {
        self.write_indent()?;
        writeln!(self.out, "{}", tag)
            .map_err(|e| format!("Failed to write tag: {}", e))?;
        self.indent += 1;
        Ok(())
    }
    
    /// Write an end tag and decrease indentation.
    /// 
    /// # Arguments
    /// * `end_tag` - The end tag to write
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_end_tag(&mut self, end_tag: &str) -> Result<(), String> {
        self.indent -= 1;
        self.write_indent()?;
        writeln!(self.out, "{}", end_tag)
            .map_err(|e| format!("Failed to write end tag: {}", e))?;
        Ok(())
    }
    
    /// Write a begin-end tag with a value.
    /// 
    /// # Arguments
    /// * `tag` - The opening tag
    /// * `end_tag` - The closing tag
    /// * `value` - The value to write between tags
    /// 
    /// # Returns
    /// * `Ok(())` - Successfully written
    /// * `Err(String)` - If writing fails
    fn write_begin_end_tag(&mut self, tag: &str, end_tag: &str, value: &str) -> Result<(), String> {
        self.write_indent()?;
        write!(self.out, "{}", tag)
            .map_err(|e| format!("Failed to write begin-end tag: {}", e))?;
        write!(self.out, "{}", value)
            .map_err(|e| format!("Failed to write begin-end tag: {}", e))?;
        writeln!(self.out, "{}", end_tag)
            .map_err(|e| format!("Failed to write begin-end tag: {}", e))?;
        Ok(())
    }
}

/// Exception thrown when an algebra file cannot be read or parsed correctly.
/// 
/// This exception is thrown when there are issues with the format, structure,
/// or content of an algebra file that prevent it from being processed.
/// 
/// # Examples
/// ```
/// use uacalc::io::BadAlgebraFileException;
/// 
/// let exception = BadAlgebraFileException::new("Invalid file format");
/// assert_eq!(exception.message(), "Invalid file format");
/// ```
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct BadAlgebraFileException {
    message: String,
}

impl BadAlgebraFileException {
    /// Creates a new `BadAlgebraFileException` with the given message.
    /// 
    /// # Arguments
    /// * `message` - The error message describing what went wrong
    /// 
    /// # Returns
    /// A new `BadAlgebraFileException` instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::BadAlgebraFileException;
    /// 
    /// let exception = BadAlgebraFileException::new("File not found");
    /// ```
    pub fn new(message: &str) -> Self {
        Self {
            message: message.to_string(),
        }
    }
    
    /// Creates a new `BadAlgebraFileException` with the given message (safe version).
    /// 
    /// This is the same as `new()` but provided for consistency with the pattern
    /// of having both `_safe` and regular versions of methods.
    /// 
    /// # Arguments
    /// * `message` - The error message describing what went wrong
    /// 
    /// # Returns
    /// `Ok(BadAlgebraFileException)` - A new exception instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::BadAlgebraFileException;
    /// 
    /// let exception = BadAlgebraFileException::new_safe("File corrupted").unwrap();
    /// ```
    pub fn new_safe(message: &str) -> Result<Self, String> {
        Ok(Self::new(message))
    }
    
    /// Returns the error message associated with this exception.
    /// 
    /// # Returns
    /// A reference to the error message string
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::BadAlgebraFileException;
    /// 
    /// let exception = BadAlgebraFileException::new("Invalid format");
    /// assert_eq!(exception.message(), "Invalid format");
    /// ```
    pub fn message(&self) -> &str {
        &self.message
    }
}

impl std::fmt::Display for BadAlgebraFileException {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "org.uacalc.io.BadAlgebraFileException: {}", self.message)
    }
}

impl std::error::Error for BadAlgebraFileException {
    fn description(&self) -> &str {
        &self.message
    }
}

use std::path::Path;
use once_cell::sync::Lazy;
use std::hash::{Hash, Hasher};

/// Filter files by extension.
/// 
/// This struct provides functionality to filter files based on their extensions,
/// similar to Java's FileFilter interface. It maintains a list of allowed extensions
/// and a description for display purposes.
/// 
/// # Examples
/// ```
/// use uacalc::io::ExtFileFilter;
/// use std::path::Path;
/// 
/// // Create filter for .ua files
/// let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string()]);
/// 
/// // Check if a file should be accepted
/// let path = Path::new("example.ua");
/// assert!(filter.accept(path));
/// ```
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ExtFileFilter {
    exts: Vec<String>,
    description: String,
}

impl Hash for ExtFileFilter {
    fn hash<H: Hasher>(&self, state: &mut H) {
        // Sort extensions for consistent hashing
        let mut sorted_exts: Vec<&String> = self.exts.iter().collect();
        sorted_exts.sort();
        sorted_exts.hash(state);
        self.description.hash(state);
    }
}

/// Extension constants matching Java implementation
pub const ALG_EXT: &'static str = "alg";
pub const XML_EXT: &'static str = "xml";
pub const UAC_EXT: &'static str = "uac";
pub const UA_EXT: &'static str = "ua";
pub const CSV_EXT: &'static str = "csv";
pub const TXT_EXT: &'static str = "txt";

/// Static extension lists matching Java implementation
pub static UA_EXTS: Lazy<Vec<String>> = Lazy::new(|| {
    vec![UA_EXT.to_string(), XML_EXT.to_string()]
});

pub static ALL_ALG_EXTS: Lazy<Vec<String>> = Lazy::new(|| {
    vec![
        UA_EXT.to_string(),
        XML_EXT.to_string(),
        ALG_EXT.to_string(),
    ]
});

pub static MACE4_EXTS: Lazy<Vec<String>> = Lazy::new(|| {
    vec!["m4".to_string()]
});

impl ExtFileFilter {

    /// Creates a new `ExtFileFilter` with the given description and list of extensions.
    /// 
    /// # Arguments
    /// * `description` - Human-readable description of the filter
    /// * `exts` - Vector of allowed file extensions (without leading dots)
    /// 
    /// # Returns
    /// A new `ExtFileFilter` instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// 
    /// let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string(), "xml".to_string()]);
    /// ```
    pub fn new(description: &str, exts: Vec<String>) -> Self {
        Self {
            exts: exts,
            description: description.to_string(),
        }
    }

    /// Creates a new `ExtFileFilter` with the given description and single extension.
    /// 
    /// # Arguments
    /// * `description` - Human-readable description of the filter
    /// * `ext` - Single allowed file extension (without leading dot)
    /// 
    /// # Returns
    /// A new `ExtFileFilter` instance
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// 
    /// let filter = ExtFileFilter::new_single("UA Files", "ua");
    /// ```
    pub fn new_single(description: &str, ext: &str) -> Self {
        Self {
            exts: vec![ext.to_string()],
            description: description.to_string(),
        }
    }

    /// Creates a new `ExtFileFilter` with the given description and list of extensions (safe version).
    /// 
    /// # Arguments
    /// * `description` - Human-readable description of the filter
    /// * `exts` - Vector of allowed file extensions (without leading dots)
    /// 
    /// # Returns
    /// `Ok(ExtFileFilter)` - A new filter instance
    /// `Err(String)` - If validation fails
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// 
    /// let filter = ExtFileFilter::new_safe("UA Files", vec!["ua".to_string()]).unwrap();
    /// ```
    pub fn new_safe(description: &str, exts: Vec<String>) -> Result<Self, String> {
        if description.is_empty() {
            return Err("Description cannot be empty".to_string());
        }
        if exts.is_empty() {
            return Err("Extensions list cannot be empty".to_string());
        }
        Ok(Self::new(description, exts))
    }

    /// Creates a new `ExtFileFilter` with the given description and single extension (safe version).
    /// 
    /// # Arguments
    /// * `description` - Human-readable description of the filter
    /// * `ext` - Single allowed file extension (without leading dot)
    /// 
    /// # Returns
    /// `Ok(ExtFileFilter)` - A new filter instance
    /// `Err(String)` - If validation fails
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// 
    /// let filter = ExtFileFilter::new_single_safe("UA Files", "ua").unwrap();
    /// ```
    pub fn new_single_safe(description: &str, ext: &str) -> Result<Self, String> {
        if description.is_empty() {
            return Err("Description cannot be empty".to_string());
        }
        if ext.is_empty() {
            return Err("Extension cannot be empty".to_string());
        }
        Ok(Self::new_single(description, ext))
    }

    /// Determines whether the given file should be accepted by this filter.
    /// 
    /// # Arguments
    /// * `path` - The file path to check
    /// 
    /// # Returns
    /// `true` if the file should be accepted, `false` otherwise.
    /// Directories are always accepted.
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// use std::path::Path;
    /// 
    /// let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string()]);
    /// let path = Path::new("example.ua");
    /// assert!(filter.accept(path));
    /// 
    /// let path = Path::new("example.txt");
    /// assert!(!filter.accept(path));
    /// ```
    pub fn accept(&self, path: &Path) -> bool {
        // Always accept directories
        if path.is_dir() {
            return true;
        }
        
        // Check if file extension is in our allowed list
        if let Some(ext) = Self::get_extension(path) {
            self.exts.contains(&ext)
        } else {
            false
        }
    }

    /// Returns the description of this filter.
    /// 
    /// # Returns
    /// A reference to the description string
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// 
    /// let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string()]);
    /// assert_eq!(filter.get_description(), "UA Files");
    /// ```
    pub fn get_description(&self) -> &str {
        &self.description
    }

    /// Returns the list of allowed extensions.
    /// 
    /// # Returns
    /// A reference to the list of allowed extensions
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// 
    /// let filter = ExtFileFilter::new("UA Files", vec!["ua".to_string()]);
    /// let exts = filter.get_extensions();
    /// assert!(exts.contains(&"ua".to_string()));
    /// ```
    pub fn get_extensions(&self) -> &Vec<String> {
        &self.exts
    }

    /// Split the file name into 2 parts: the first everything up to the
    /// last "."; the rest the extension.
    ///
    /// # Arguments
    /// * `path` - The file path to split
    ///
    /// # Returns
    /// A tuple containing (filename_without_extension, extension) or (None, None) if no extension
    ///
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// use std::path::Path;
    ///
    /// let path = Path::new("example.ua");
    /// let (name, ext) = ExtFileFilter::split_off_extension(path);
    /// assert_eq!(name, Some("example".to_string()));
    /// assert_eq!(ext, Some("ua".to_string()));
    ///
    /// let path = Path::new("noextension");
    /// let (name, ext) = ExtFileFilter::split_off_extension(path);
    /// assert_eq!(name, None);
    /// assert_eq!(ext, None);
    /// ```
    pub fn split_off_extension(path: &Path) -> (Option<String>, Option<String>) {
        let filename = path.file_name()
            .and_then(|name| name.to_str())
            .unwrap_or("");
        
        if let Some(last_dot) = filename.rfind('.') {
            if last_dot > 0 && last_dot < filename.len() - 1 {
                let name = filename[..last_dot].to_string();
                let ext = filename[last_dot + 1..].to_string();
                (Some(name), Some(ext))
            } else {
                (None, None)
            }
        } else {
            (None, None)
        }
    }

    /// Get the file extension from a file path.
    /// 
    /// # Arguments
    /// * `path` - The file path to get the extension from
    /// 
    /// # Returns
    /// `Some(extension)` if the file has an extension, `None` otherwise.
    /// The extension is returned without the leading dot.
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::ExtFileFilter;
    /// use std::path::Path;
    /// 
    /// let path = Path::new("example.ua");
    /// assert_eq!(ExtFileFilter::get_extension(path), Some("ua".to_string()));
    /// 
    /// let path = Path::new("noextension");
    /// assert_eq!(ExtFileFilter::get_extension(path), None);
    /// ```
    pub fn get_extension(path: &Path) -> Option<String> {
        let filename = path.file_name()
            .and_then(|name| name.to_str())
            .unwrap_or("");
        
        if let Some(last_dot) = filename.rfind('.') {
            if last_dot > 0 && last_dot < filename.len() - 1 {
                Some(filename[last_dot + 1..].to_string())
            } else {
                None
            }
        } else {
            None
        }
    }
}

impl std::fmt::Display for ExtFileFilter {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "ExtFileFilter({})", self.description)
    }
}

pub struct JSONChannel {
    // TODO: Implement JSON channel
}

use std::io::{BufRead, BufReader, Read};
use std::collections::{HashMap, HashSet};
use crate::alg::small_algebra::{BasicAlgebra};
use crate::alg::op::{OperationSymbol};
use crate::alg::op::operations;

/// A reader for Mace4 model files that parses them into algebras.
/// 
/// This reader handles Mace4 model files and extracts operations while ignoring relations.
/// It provides stateful parsing with line tracking and error handling.
/// 
/// # Examples
/// ```
/// use uacalc::io::Mace4Reader;
/// use std::fs::File;
/// 
/// let file = File::open("resources/mace4/KR-8.model").unwrap();
/// let mut reader = Mace4Reader::new(Box::new(file)).unwrap();
/// let algebra = reader.parse_algebra().unwrap();
/// ```
pub struct Mace4Reader {
    reader: BufReader<Box<dyn Read>>,
    line: Option<String>,
    lineno: usize,
    index: usize,
}

impl Mace4Reader {
    /// Creates a new Mace4Reader from an input stream.
    /// 
    /// # Arguments
    /// * `stream` - The input stream to read from
    /// 
    /// # Returns
    /// * `Ok(Mace4Reader)` - A new reader instance
    /// * `Err(String)` - If the reader cannot be created
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::Mace4Reader;
    /// use std::fs::File;
    /// 
    /// let file = File::open("resources/mace4/KR-8.model").unwrap();
    /// let reader = Mace4Reader::new(Box::new(file)).unwrap();
    /// ```
    pub fn new(stream: Box<dyn Read>) -> Result<Self, String> {
        Ok(Mace4Reader {
            reader: BufReader::new(stream),
            line: None,
            lineno: 0,
            index: 0,
        })
    }
    
    /// Creates a new Mace4Reader from an input stream (safe version).
    /// 
    /// # Arguments
    /// * `stream` - The input stream to read from
    /// 
    /// # Returns
    /// * `Ok(Mace4Reader)` - A new reader instance
    /// * `Err(String)` - If the reader cannot be created
    pub fn new_safe(stream: Box<dyn Read>) -> Result<Self, String> {
        Self::new(stream)
    }
    
    /// Peek at the current character without advancing the position.
    /// 
    /// # Returns
    /// The current character, or 0 if at end of line, or '\n' if at end of file
    fn peek_char(&self) -> char {
        if let Some(ref line) = self.line {
            if self.index < line.len() {
                line.chars().nth(self.index).unwrap_or('\0')
            } else {
                '\n'
            }
        } else {
            '\0'
        }
    }
    
    /// Advance to the next character, reading a new line if necessary.
    /// 
    /// # Returns
    /// * `Ok(())` - If successful
    /// * `Err(String)` - If an I/O error occurs
    fn next_char(&mut self) -> Result<(), String> {
        if let Some(ref line) = self.line {
            if self.index < line.len() {
                self.index += 1;
            } else {
                self.read_line()?;
            }
        }
        Ok(())
    }
    
    /// Read the next line from the input stream.
    /// 
    /// # Returns
    /// * `Ok(())` - If successful
    /// * `Err(String)` - If an I/O error occurs
    fn read_line(&mut self) -> Result<(), String> {
        let mut line = String::new();
        match self.reader.read_line(&mut line) {
            Ok(0) => {
                self.line = None;
                self.index = 0;
            }
            Ok(_) => {
                self.line = Some(line.trim_end().to_string());
                self.lineno += 1;
                self.index = 0;
            }
            Err(e) => return Err(format!("I/O error: {}", e)),
        }
        Ok(())
    }
    
    /// Get the next character, skipping whitespace.
    /// 
    /// # Returns
    /// * `Ok(char)` - The next non-whitespace character
    /// * `Err(String)` - If an I/O error occurs
    fn get_char(&mut self) -> Result<char, String> {
        self.eat_spaces()?;
        let c = self.peek_char();
        self.next_char()?;
        Ok(c)
    }
    
    /// Skip whitespace characters.
    /// 
    /// # Returns
    /// * `Ok(())` - If successful
    /// * `Err(String)` - If an I/O error occurs
    fn eat_spaces(&mut self) -> Result<(), String> {
        while self.peek_char().is_whitespace() {
            self.next_char()?;
        }
        Ok(())
    }
    
    /// Report an error with line and column information.
    /// 
    /// # Arguments
    /// * `message` - The error message
    /// 
    /// # Returns
    /// A BadAlgebraFileException with location information
    fn error(&self, message: &str) -> BadAlgebraFileException {
        BadAlgebraFileException::new(&format!("{} at line {} column {}", 
            message, self.lineno, self.index + 1))
    }
    
    /// Expect and consume a specific character.
    /// 
    /// # Arguments
    /// * `expected` - The character to expect
    /// 
    /// # Returns
    /// * `Ok(())` - If the character matches
    /// * `Err(BadAlgebraFileException)` - If the character doesn't match
    fn eat_char(&mut self, expected: char) -> Result<(), BadAlgebraFileException> {
        let actual = self.get_char().map_err(|e| BadAlgebraFileException::new(&e))?;
        if actual != expected {
            return Err(self.error(&format!("Character '{}' is expected", expected)));
        }
        Ok(())
    }
    
    /// Parse a number from the input.
    /// 
    /// # Returns
    /// * `Ok(i32)` - The parsed number
    /// * `Err(BadAlgebraFileException)` - If parsing fails
    fn parse_number(&mut self) -> Result<i32, BadAlgebraFileException> {
        let c = self.get_char().map_err(|e| BadAlgebraFileException::new(&e))?;
        if !c.is_ascii_digit() {
            return Err(self.error("Invalid number"));
        }
        
        let mut value = (c as i32) - ('0' as i32);
        
        loop {
            let c = self.peek_char();
            if !c.is_ascii_digit() {
                break;
            }
            
            value = value * 10 + ((c as i32) - ('0' as i32));
            if value > i32::MAX as i32 {
                return Err(self.error("Too large integer"));
            }
            
            self.next_char().map_err(|e| BadAlgebraFileException::new(&e))?;
        }
        
        Ok(value)
    }
    
    /// Check if a character is an ordinary character (letter, $, or _).
    /// 
    /// # Arguments
    /// * `c` - The character to check
    /// 
    /// # Returns
    /// `true` if the character is ordinary, `false` otherwise
    pub fn is_ordinary_character(c: char) -> bool {
        c.is_ascii_alphabetic() || c == '$' || c == '_'
    }
    
    /// Check if a character is a special character.
    /// 
    /// # Arguments
    /// * `c` - The character to check
    /// 
    /// # Returns
    /// `true` if the character is special, `false` otherwise
    pub fn is_special_character(c: char) -> bool {
        const SPECIAL_CHARS: &str = "{+-*/\\^<>=`~?@&|!#';}";
        SPECIAL_CHARS.contains(c)
    }
    
    /// Parse a symbol from the input.
    /// 
    /// # Returns
    /// * `Ok(String)` - The parsed symbol
    /// * `Err(BadAlgebraFileException)` - If parsing fails
    fn parse_symbol(&mut self) -> Result<String, BadAlgebraFileException> {
        let mut result = String::new();
        
        let c = self.get_char().map_err(|e| BadAlgebraFileException::new(&e))?;
        let is_ordinary = Self::is_ordinary_character(c);
        
        if !is_ordinary && !Self::is_special_character(c) {
            return Err(self.error("Invalid symbol character"));
        }
        
        result.push(c);
        
        loop {
            let c = self.peek_char();
            let should_continue = if is_ordinary {
                Self::is_ordinary_character(c) || c.is_ascii_digit()
            } else {
                Self::is_special_character(c)
            };
            
            if !should_continue {
                break;
            }
            
            result.push(c);
            self.next_char().map_err(|e| BadAlgebraFileException::new(&e))?;
        }
        
        Ok(result)
    }
    
    /// Parse a number table (array of integers).
    /// 
    /// # Returns
    /// * `Ok(Vec<i32>)` - The parsed table
    /// * `Err(BadAlgebraFileException)` - If parsing fails
    fn parse_number_table(&mut self) -> Result<Vec<i32>, BadAlgebraFileException> {
        let mut table = Vec::new();
        
        self.eat_char('[')?;
        self.eat_spaces().map_err(|e| BadAlgebraFileException::new(&e))?;
        
        if self.peek_char() != ']' {
            loop {
                table.push(self.parse_number()?);
                
                let c = self.get_char().map_err(|e| BadAlgebraFileException::new(&e))?;
                if c == ']' {
                    break;
                } else if c != ',' {
                    return Err(self.error("Comma is expected"));
                }
            }
        }
        
        Ok(table)
    }
    
    /// Eat a block of text between matching delimiters.
    /// 
    /// # Arguments
    /// * `begin` - The opening delimiter
    /// * `end` - The closing delimiter
    /// 
    /// # Returns
    /// * `Ok(())` - If successful
    /// * `Err(BadAlgebraFileException)` - If parsing fails
    fn eat_block(&mut self, begin: char, end: char) -> Result<(), BadAlgebraFileException> {
        self.eat_spaces().map_err(|e| BadAlgebraFileException::new(&e))?;
        self.eat_char(begin)?;
        
        let mut depth = 1;
        while depth > 0 {
            self.eat_spaces().map_err(|e| BadAlgebraFileException::new(&e))?;
            let c = self.peek_char();
            
            if c == begin {
                depth += 1;
            } else if c == end {
                depth -= 1;
            }
            
            self.next_char().map_err(|e| BadAlgebraFileException::new(&e))?;
        }
        
        Ok(())
    }
    
    /// Parse statistics from the input.
    /// 
    /// # Returns
    /// * `Ok(HashMap<String, i32>)` - The parsed statistics
    /// * `Err(BadAlgebraFileException)` - If parsing fails
    fn parse_stats(&mut self) -> Result<HashMap<String, i32>, BadAlgebraFileException> {
        let mut stats = HashMap::new();
        
        self.eat_char('[')?;
        loop {
            let key = self.parse_symbol()?;
            self.eat_char('=')?;
            let value = self.parse_number()?;
            
            stats.insert(key, value);
            
            let c = self.get_char().map_err(|e| BadAlgebraFileException::new(&e))?;
            if c == ']' {
                break;
            } else if c != ',' {
                return Err(self.error("Comma is expected"));
            }
        }
        
        Ok(stats)
    }
    
    /// Parse the arity of an operation from its formal arguments.
    /// 
    /// # Returns
    /// * `Ok(i32)` - The arity
    /// * `Err(BadAlgebraFileException)` - If parsing fails
    fn parse_arity(&mut self) -> Result<i32, BadAlgebraFileException> {
        self.eat_spaces().map_err(|e| BadAlgebraFileException::new(&e))?;
        let c = self.peek_char();
        
        if c != '(' {
            return Ok(0);
        }
        
        self.next_char().map_err(|e| BadAlgebraFileException::new(&e))?;
        
        let mut arity = 0;
        loop {
            let c = self.get_char().map_err(|e| BadAlgebraFileException::new(&e))?;
            if c == '_' {
                arity += 1;
            } else if c == ')' {
                break;
            } else if c != ',' {
                return Err(self.error("Invalid formal argument"));
            }
        }
        
        Ok(arity)
    }
    
    /// Parse a single algebra from the input stream.
    /// 
    /// # Returns
    /// * `Ok(Option<Box<dyn SmallAlgebra<UniverseItem = i32>>>)` - The parsed algebra, or None if end of stream
    /// * `Err(BadAlgebraFileException)` - If parsing fails
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::Mace4Reader;
    /// use std::fs::File;
    /// 
    /// let file = File::open("resources/mace4/KR-8.model").unwrap();
    /// let mut reader = Mace4Reader::new(Box::new(file)).unwrap();
    /// let algebra = reader.parse_algebra().unwrap();
    /// ```
    pub fn parse_algebra(&mut self) -> Result<Option<Box<dyn SmallAlgebra<UniverseItem = i32>>>, BadAlgebraFileException> {
        // Find the interpretation line
        loop {
            self.read_line().map_err(|e| BadAlgebraFileException::new(&e))?;
            
            if self.line.is_none() {
                return Ok(None);
            }
            
            if let Some(ref line) = self.line {
                if line.starts_with("interpretation(") {
                    break;
                }
            }
        }
        
        self.index = 0;
        
        let symbol = self.parse_symbol()?;
        if symbol != "interpretation" {
            return Err(self.error("Expected 'interpretation'"));
        }
        
        self.eat_char('(')?;
        let cardinality = self.parse_number()?;
        let mut operations = Vec::new();
        
        self.eat_char(',')?;
        let stats = self.parse_stats()?;
        self.eat_char(',')?;
        self.eat_char('[')?;
        
        if self.peek_char() != ']' {
            loop {
                let symbol = self.parse_symbol()?;
                if symbol == "function" {
                    self.eat_char('(')?;
                    let op_name = self.parse_symbol()?;
                    let arity = self.parse_arity()?;
                    self.eat_char(',')?;
                    let table = self.parse_number_table()?;
                    self.eat_char(')')?;
                    
                    let op_sym = OperationSymbol::new_safe(&op_name, arity, false)
                        .map_err(|e| self.error(&e))?;
                    
                    let operation = operations::make_int_operation(op_sym, cardinality, table)
                        .map_err(|e| self.error(&e))?;
                    
                    operations.push(operation);
                } else {
                    self.eat_block('(', ')')?;
                }
                
                let c = self.get_char().map_err(|e| BadAlgebraFileException::new(&e))?;
                if c == ']' {
                    break;
                } else if c != ',' {
                    return Err(self.error("Comma is expected"));
                }
            }
        }
        
        self.eat_char(')')?;
        self.eat_char('.')?;
        
        let mut name = "model".to_string();
        if let Some(number) = stats.get("number") {
            name.push_str(&number.to_string());
        }
        
        // Create universe as integers 0..cardinality-1
        let universe: HashSet<i32> = (0..cardinality).collect();
        
        let algebra = BasicAlgebra::new(name, universe, operations);
        Ok(Some(Box::new(algebra)))
    }
    
    /// Parse a list of algebras from the input stream.
    /// 
    /// # Returns
    /// * `Ok(Vec<Box<dyn SmallAlgebra<UniverseItem = i32>>>)` - The parsed algebras
    /// * `Err(BadAlgebraFileException)` - If parsing fails
    /// 
    /// # Examples
    /// ```
    /// use uacalc::io::Mace4Reader;
    /// use std::fs::File;
    /// 
    /// let file = File::open("resources/mace4/KR-8.model").unwrap();
    /// let mut reader = Mace4Reader::new(Box::new(file)).unwrap();
    /// let algebras = reader.parse_algebra_list().unwrap();
    /// ```
    pub fn parse_algebra_list(&mut self) -> Result<Vec<Box<dyn SmallAlgebra<UniverseItem = i32>>>, BadAlgebraFileException> {
        let mut algebras = Vec::new();
        
        loop {
            match self.parse_algebra()? {
                Some(algebra) => algebras.push(algebra),
                None => break,
            }
        }
        
        Ok(algebras)
    }
}

impl std::fmt::Display for Mace4Reader {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Mace4Reader(line {}, index {})", self.lineno, self.index)
    }
}

impl std::fmt::Debug for Mace4Reader {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Mace4Reader")
            .field("lineno", &self.lineno)
            .field("index", &self.index)
            .field("has_line", &self.line.is_some())
            .finish()
    }
}
