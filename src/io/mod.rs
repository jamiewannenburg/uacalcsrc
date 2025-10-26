mod algebra_reader;
pub use algebra_reader::AlgebraReader;

#[cfg(test)]
mod mace4_reader_tests;

pub struct AlgebraIO {
    // TODO: Implement algebra IO
}

pub struct AlgebraWriter {
    // TODO: Implement algebra writer
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
use crate::alg::small_algebra::{SmallAlgebra, BasicSmallAlgebra};
use crate::alg::algebra::Algebra;
use crate::alg::op::{Operation, OperationSymbol};
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
        
        let algebra = BasicSmallAlgebra::new(name, universe, operations);
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
